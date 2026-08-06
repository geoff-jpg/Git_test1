"""
Thin-line recursive snowflake generator.

Draws one 60-degree sector recursively, then rotates to all 6 sectors for
perfect D6 symmetry. Output matches the thin dendritic style of real
stellar dendrite snowflakes.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


DEFAULT_PARAMS = {
    "size":              2048,   # canvas pixels
    "arm_length":        0.44,   # arm length as fraction of half-canvas
    "branch_levels":     4,      # recursion depth (3=simple, 4=detailed, 5=very fine)
    "branch_ratio":      0.42,   # child branch length / parent length
    "branch_angle":      60.0,   # branch angle off parent (degrees)
    "branch_spacing":    0.30,   # spacing between branch pairs (fraction of parent length)
    "branch_offset":     0.20,   # where first branch starts along arm (fraction)
    "arm_width":         3.0,    # pixel width of primary arm
    "width_decay":       0.62,   # child width = parent_width * width_decay
    "min_length_px":     4,      # stop recursing below this pixel length
    "background":        (8, 12, 28),
    "flake_colour":      (210, 230, 255),
    "blur_radius":       0.6,    # slight anti-alias blur on final mask
    "glow":              True,   # add faint glow halo around crystal
    "noise_sigma":       1.2,    # photographic grain
}


def generate(params=None):
    """Generate and return a PIL RGBA Image of a single snowflake."""
    p = {**DEFAULT_PARAMS, **(params or {})}
    size = p["size"]
    half = size // 2

    # Work on a large greyscale canvas, then colourise
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)

    arm_px = p["arm_length"] * half

    # Draw one arm (pointing right, 0°), then rotate 5 times
    arm_mask = Image.new("L", (size, size), 0)
    arm_draw = ImageDraw.Draw(arm_mask)

    _draw_branch(
        arm_draw,
        cx=half, cy=half,
        angle=0.0,
        length=arm_px,
        width=p["arm_width"],
        depth=p["branch_levels"],
        p=p,
    )

    # Rotate and composite all 6 arms for perfect D6 symmetry
    for k in range(6):
        rotated = arm_mask.rotate(k * 60, resample=Image.BICUBIC, center=(half, half))
        mask = Image.fromarray(
            np.maximum(np.array(mask), np.array(rotated)).astype(np.uint8), "L"
        )

    # Slight gaussian blur for anti-aliasing
    if p["blur_radius"] > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=p["blur_radius"]))

    mask_arr = np.array(mask).astype(np.float32) / 255.0

    # Optional glow
    if p["glow"]:
        glow_blur = mask.filter(ImageFilter.GaussianBlur(radius=6))
        glow_arr = np.array(glow_blur).astype(np.float32) / 255.0 * 0.25
        mask_arr = np.clip(mask_arr + glow_arr, 0, 1)

    # Radial gradient: centre slightly brighter
    y_idx, x_idx = np.mgrid[0:size, 0:size]
    dist = np.sqrt((x_idx - half)**2 + (y_idx - half)**2)
    max_dist = np.sqrt(half**2 + half**2)
    grad = 1.0 - 0.10 * (dist / max_dist)
    mask_arr = np.clip(mask_arr * grad, 0, 1)

    # Colourise
    bg = np.array(p["background"],   dtype=np.float32)
    sf = np.array(p["flake_colour"], dtype=np.float32)
    m3 = mask_arr[:, :, np.newaxis]
    colour = bg * (1 - m3) + sf * m3
    colour = colour.astype(np.uint8)

    # Photographic grain
    if p["noise_sigma"] > 0:
        noise = np.random.default_rng(0).normal(0, p["noise_sigma"], colour.shape)
        colour = np.clip(colour.astype(np.int16) + noise.astype(np.int16), 0, 255).astype(np.uint8)

    return Image.fromarray(colour, "RGB"), mask_arr


def _draw_branch(draw, cx, cy, angle, length, width, depth, p):
    """Recursively draw one branch and its children."""
    if depth <= 0 or length < p["min_length_px"]:
        return

    rad = np.radians(angle)
    ex = cx + np.cos(rad) * length
    ey = cy - np.sin(rad) * length  # PIL y-axis is flipped

    w = max(1, int(round(width)))
    draw.line([(cx, cy), (ex, ey)], fill=255, width=w)

    # Child branches along this branch
    offset = p["branch_offset"]
    spacing = p["branch_spacing"]
    branch_angle = p["branch_angle"]
    child_length = length * p["branch_ratio"]
    child_width  = width  * p["width_decay"]

    # Place pairs of branches from offset to near the tip
    t = offset
    while t < 0.92:
        bx = cx + np.cos(rad) * length * t
        by = cy - np.sin(rad) * length * t

        for sign in (+1, -1):
            _draw_branch(
                draw,
                cx=bx, cy=by,
                angle=angle + sign * branch_angle,
                length=child_length * (1 - 0.3 * t),  # branches shorten toward tip
                width=child_width,
                depth=depth - 1,
                p=p,
            )
        t += spacing


def save(img, path, dpi=300):
    img.save(path, format="PNG", dpi=(dpi, dpi))
