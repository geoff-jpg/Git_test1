"""Compositing pipeline: CA mask + procedural detail → final PNG."""

import numpy as np
from PIL import Image, ImageFilter
from .procedural import draw_snowflake


BG_COLOR  = (8,  12,  28)
SF_COLOR  = (220, 235, 255)
OUTPUT_SIZE = 2048


def render(frozen_mask, params=None, output_path=None):
    """
    Compose final RGBA snowflake image.

    frozen_mask: 2D bool numpy array from Reiter CA
    Returns PIL Image (RGBA).
    """
    p = {
        "procedural_blend": 0.30,
        "noise_sigma": 2,
        "gradient_strength": 0.12,
        **(params or {}),
    }

    size = OUTPUT_SIZE
    ca_size = frozen_mask.shape[0]

    # --- CA mask → greyscale image, upscaled ---
    ca_img = Image.fromarray((frozen_mask.astype(np.uint8) * 255), mode="L")
    ca_img = ca_img.resize((size, size), Image.LANCZOS)
    # Smooth edges then re-threshold
    ca_blur = ca_img.filter(ImageFilter.GaussianBlur(radius=1.2))
    ca_arr = np.array(ca_blur)
    ca_mask = (ca_arr > 100).astype(np.float32)

    # Apply 6-fold symmetry pass on the full-res mask
    ca_mask = _enforce_d6(ca_mask)

    # --- procedural overlay ---
    proc_img = draw_snowflake(size=size)
    proc_arr = np.array(proc_img).astype(np.float32) / 255.0

    # Blend: weighted sum, clamp to [0,1]
    blend = np.clip(ca_mask + p["procedural_blend"] * proc_arr, 0, 1)

    # --- radial gradient (centre slightly brighter) ---
    cx = cy = size // 2
    y_idx, x_idx = np.mgrid[0:size, 0:size]
    dist = np.sqrt((x_idx - cx)**2 + (y_idx - cy)**2)
    max_dist = np.sqrt(cx**2 + cy**2)
    grad = 1.0 - p["gradient_strength"] * (dist / max_dist)
    blend = np.clip(blend * grad, 0, 1)

    # --- colour mapping ---
    bg = np.array(BG_COLOR, dtype=np.float32)
    sf = np.array(SF_COLOR, dtype=np.float32)
    blend_3d = blend[:, :, np.newaxis]
    colour = bg[np.newaxis, np.newaxis, :] * (1 - blend_3d) + sf[np.newaxis, np.newaxis, :] * blend_3d
    colour = colour.astype(np.uint8)

    # --- Gaussian noise ---
    if p["noise_sigma"] > 0:
        noise = np.random.normal(0, p["noise_sigma"], colour.shape).astype(np.int16)
        colour = np.clip(colour.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    out = Image.fromarray(colour, mode="RGB")

    if output_path:
        out.save(output_path, format="PNG", dpi=(300, 300))

    return out


def _enforce_d6(mask):
    """Symmetrise a float mask under 60° rotations."""
    from scipy.ndimage import rotate
    result = mask.copy()
    for angle in range(60, 360, 60):
        rotated = rotate(mask, angle, reshape=False, order=1, mode="constant", cval=0)
        result = np.maximum(result, rotated)
    # Average back to avoid over-inflation
    return np.clip(result, 0, 1)
