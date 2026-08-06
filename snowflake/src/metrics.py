"""Six objective metrics + composite Q scorer for snowflake quality evaluation."""

import numpy as np
from scipy.ndimage import rotate, label
from skimage.morphology import skeletonize
from skimage.measure import regionprops


# ---------------------------------------------------------------------------
# Metric 1: Symmetry Score
# ---------------------------------------------------------------------------

def symmetry_score(mask):
    """D6 symmetry: diff mask against each 60° rotation, return 1 - mean_error."""
    errors = []
    for angle in range(60, 360, 60):
        rot = rotate(mask.astype(float), angle, reshape=False, order=1,
                     mode="constant", cval=0)
        errors.append(np.mean(np.abs(rot - mask.astype(float))))
    return float(1.0 - np.mean(errors))


# ---------------------------------------------------------------------------
# Metric 2: Fractal Dimension (box-counting)
# ---------------------------------------------------------------------------

def fractal_dimension(mask):
    """Box-counting fractal dimension of the snowflake mask."""
    binary = mask > 0.5
    sizes = [2, 4, 8, 16, 32, 64, 128]
    counts = []
    for s in sizes:
        # Downsample and count non-zero boxes
        trimmed_r = (binary.shape[0] // s) * s
        trimmed_c = (binary.shape[1] // s) * s
        cropped = binary[:trimmed_r, :trimmed_c]
        reshaped = cropped.reshape(trimmed_r // s, s, trimmed_c // s, s)
        box_occupied = reshaped.any(axis=(1, 3))
        counts.append(box_occupied.sum())

    counts = np.array(counts, dtype=float)
    sizes_arr = np.array(sizes, dtype=float)
    valid = counts > 0
    if valid.sum() < 2:
        return 0.0
    log_s = np.log(1.0 / sizes_arr[valid])
    log_c = np.log(counts[valid])
    coeffs = np.polyfit(log_s, log_c, 1)
    return float(coeffs[0])


# ---------------------------------------------------------------------------
# Metric 3: Branch Angle Distribution
# ---------------------------------------------------------------------------

def branch_angle_distribution(mask):
    """Fraction of skeleton branch segments aligned to multiples of 60°."""
    binary = (mask > 0.5).astype(np.uint8)
    skel = skeletonize(binary)

    # Find branch points via local neighbourhood count
    pts = np.argwhere(skel)
    if len(pts) < 10:
        return 0.0

    # Sample angles from gradient of skeleton
    from scipy.ndimage import sobel
    sx = sobel(skel.astype(float), axis=1)
    sy = sobel(skel.astype(float), axis=0)
    angles = np.degrees(np.arctan2(sy[skel], sx[skel])) % 180

    # Check alignment to 0, 60, 120 degrees (mod 60 within ±10°)
    aligned = (angles % 60) < 10
    aligned |= (angles % 60) > 50
    return float(aligned.mean())


# ---------------------------------------------------------------------------
# Metric 4: Arm Taper Profile
# ---------------------------------------------------------------------------

def arm_taper_profile(mask):
    """Power-law R² fit to arm width samples along one arm."""
    binary = (mask > 0.5)
    rows, cols = binary.shape
    cx = cy = rows // 2

    # Sample along the rightward arm (0° direction)
    n_samples = 12
    arm_half = cols // 2
    widths = []
    r_positions = []

    for k in range(1, n_samples + 1):
        r = int(arm_half * k / (n_samples + 1))
        # Count pixels in a vertical slice at this radius
        col = cx + r
        if col >= cols:
            break
        width = binary[:, col].sum()
        if width > 0:
            widths.append(float(width))
            r_positions.append(float(r))

    if len(widths) < 4:
        return 0.0

    r_arr = np.array(r_positions)
    w_arr = np.array(widths)
    # Fit w = a * (1 - r/L)^alpha in log space
    L = arm_half
    frac = 1.0 - r_arr / L
    valid = frac > 0.05
    if valid.sum() < 3:
        return 0.0

    log_frac = np.log(frac[valid])
    log_w = np.log(w_arr[valid])
    coeffs = np.polyfit(log_frac, log_w, 1)
    alpha = coeffs[0]

    predicted = np.polyval(coeffs, log_frac)
    ss_res = np.sum((log_w - predicted) ** 2)
    ss_tot = np.sum((log_w - log_w.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    # Penalise if exponent outside ideal range [0.4, 0.9]
    alpha_ok = 1.0 if 0.4 <= alpha <= 0.9 else 0.5
    return float(max(0.0, min(1.0, r2 * alpha_ok)))


# ---------------------------------------------------------------------------
# Metric 5: Reference Similarity Score
# ---------------------------------------------------------------------------

def reference_similarity(mask, ref_dir=None):
    """
    Mean SSIM of generated mask against up to 10 reference images.
    Returns (mean_ssim, per_ref_scores_list).
    If no references found, returns (0.0, []).
    """
    import os
    from skimage.metrics import structural_similarity as ssim
    from PIL import Image

    if ref_dir is None:
        return 0.0, []

    scores = []
    ref_files = sorted([
        f for f in os.listdir(ref_dir)
        if f.startswith("ref_") and f.endswith(".png")
    ])

    gen = (mask > 0.5).astype(np.uint8)
    # Resize to 256×256 for speed
    gen_img = Image.fromarray((gen * 255).astype(np.uint8)).resize((256, 256))
    gen_arr = np.array(gen_img).astype(float) / 255.0

    for rf in ref_files[:10]:
        try:
            ref_img = Image.open(os.path.join(ref_dir, rf)).convert("L").resize((256, 256))
            ref_arr = np.array(ref_img).astype(float) / 255.0
            # Binarise reference
            ref_bin = (ref_arr > 0.5).astype(float)
            s = ssim(gen_arr, ref_bin, data_range=1.0)
            scores.append(float(s))
        except Exception:
            continue

    if not scores:
        return 0.0, []
    return float(np.mean(scores)), scores


# ---------------------------------------------------------------------------
# Metric 6: Arm Count and Length Ratio
# ---------------------------------------------------------------------------

def arm_count_length_ratio(mask):
    """
    Returns (score, arm_count, length_ratio).
    score = 1.0 if exactly 6 arms and ratio in [0.40, 0.85], else partial.
    """
    binary = (mask > 0.5).astype(np.uint8)
    rows, cols = binary.shape
    cx = cy = rows // 2

    # Remove central blob with a larger exclusion radius so only primary arm
    # trunks remain as separate components (secondary branches stay attached).
    y_idx, x_idx = np.mgrid[0:rows, 0:cols]
    dist = np.sqrt((x_idx - cx)**2 + (y_idx - cy)**2)
    central_radius = rows * 0.18   # enlarged from 0.06 → isolates primary arms
    outer = binary.copy()
    outer[dist < central_radius] = 0

    labeled, n_comp = label(outer)
    # Keep only components large enough to be a primary arm (≥ 0.3% of pixels)
    min_arm_pixels = int(rows * cols * 0.003)
    arm_lengths = []
    for comp_id in range(1, n_comp + 1):
        pts = np.argwhere(labeled == comp_id)
        if len(pts) < min_arm_pixels:
            continue
        d = np.sqrt((pts[:, 1] - cx)**2 + (pts[:, 0] - cy)**2)
        arm_lengths.append(d.max())

    arm_count = len(arm_lengths)
    if arm_count == 0:
        return 0.0, 0, 0.0

    avg_len = np.mean(arm_lengths)
    length_ratio = avg_len / (cols / 2)

    count_score = 1.0 if arm_count == 6 else max(0.0, 1.0 - abs(arm_count - 6) * 0.2)
    ratio_score = 1.0 if 0.40 <= length_ratio <= 0.85 else 0.5
    score = count_score * ratio_score

    return float(score), arm_count, float(length_ratio)


# ---------------------------------------------------------------------------
# Composite score Q
# ---------------------------------------------------------------------------

def composite_score(mask, ref_dir=None):
    """Compute all metrics and return a dict with individual scores and Q."""
    S = symmetry_score(mask)
    FD = fractal_dimension(mask)
    BAD = branch_angle_distribution(mask)
    ATP = arm_taper_profile(mask)
    rss_mean, rss_per_ref = reference_similarity(mask, ref_dir)
    aclr, arm_count, length_ratio = arm_count_length_ratio(mask)

    # Normalise FD into [0,1]: ideal range [1.70, 1.90]
    if 1.70 <= FD <= 1.90:
        fd_score = 1.0
    elif FD < 1.70:
        fd_score = max(0.0, 1.0 - (1.70 - FD) * 2.0)
    else:
        fd_score = max(0.0, 1.0 - (FD - 1.90) * 2.0)

    Q = (0.25 * S + 0.20 * fd_score + 0.20 * BAD + 0.15 * ATP
         + 0.10 * rss_mean + 0.10 * aclr)

    return {
        "S":             round(S, 4),
        "FD":            round(FD, 4),
        "fd_score":      round(fd_score, 4),
        "BAD":           round(BAD, 4),
        "ATP":           round(ATP, 4),
        "RSS":           round(rss_mean, 4),
        "rss_per_ref":   [round(x, 4) for x in rss_per_ref],
        "ACLR":          round(aclr, 4),
        "arm_count":     arm_count,
        "length_ratio":  round(length_ratio, 4),
        "Q":             round(Q, 4),
    }
