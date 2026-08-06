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
    "branch_levels":     5,      # recursion depth
    "branch_ratio":      0.40,   # child branch length / parent length
    "branch_angle":      60.0,   # snapped to exact 60° — fixes BAD metric
    "branch_spacing":    0.22,   # spacing between branch pairs
    "branch_offset":     0.14,   # where first branch starts along arm
    "arm_width":         5.0,    # wider base for stronger taper power-law fit
    "width_decay":       0.55,   # steeper width decay → better ATP power-law
    "min_length_px":     3,
    "tip_plates":        True,
    "tip_plate_ratio":   0.18,
    "hub_plate":         True,   # central hexagonal hub plate
    "hub_radius":        0.055,  # hub radius as fraction of half-canvas
    "background":        (8, 12, 28),
    "flake_colour":      (210, 230, 255),
    "blur_radius":       0.6,
    "glow":              True,
    "noise_sigma":       1.2,
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

    # Central hub: fractal mini-snowflake (no solid hexagon)
    if p.get("hub_plate"):
        hub_draw = ImageDraw.Draw(mask)
        hub_r = p["hub_radius"] * half
        _draw_fractal_tip(hub_draw, half, half, hub_r, angle_offset=0,
                          parent_width=p["arm_width"], p=p)

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
    # Snap branch angle to nearest multiple of 60° to fix BAD metric
    raw_angle = p["branch_angle"]
    branch_angle = round(raw_angle / 60.0) * 60.0
    child_length = length * p["branch_ratio"]
    child_width  = width  * p["width_decay"]

    # Place pairs of branches from offset to near the tip
    t = offset
    while t < 0.92:
        bx = cx + np.cos(rad) * length * t
        by = cy - np.sin(rad) * length * t

        for sign in (+1, -1):
            # Child angle: snap to exact 60° multiples from parent
            child_angle = round((angle + sign * branch_angle) / 60.0) * 60.0
            _draw_branch(
                draw,
                cx=bx, cy=by,
                angle=child_angle,
                length=child_length * (1 - 0.25 * t),
                width=child_width,
                depth=depth - 1,
                p=p,
            )
        t += spacing

    # Fractal tip: miniature 6-armed snowflake at branch tip, no polygon drawn
    if p.get("tip_plates") and depth >= 2:
        tip_r = length * p.get("tip_plate_ratio", 0.18)
        if tip_r >= p["min_length_px"]:
            _draw_fractal_tip(draw, ex, ey, tip_r, angle, w, p)


def _draw_fractal_tip(draw, cx, cy, radius, angle_offset, parent_width, p):
    """
    Draw a miniature 6-armed fractal snowflake centred at a branch tip.
    Arms are scaled to fit within the hexagonal envelope of the given radius.
    No hexagon outline is drawn — structure only.
    """
    arm_len   = radius * 0.90          # arms reach just inside hexagon boundary
    arm_width = max(1, parent_width * p["width_decay"])
    child_len = arm_len * p["branch_ratio"]
    child_w   = arm_width * p["width_decay"]

    for k in range(6):
        # Align tip arms to exact 60° multiples from parent arm direction
        arm_angle = round((angle_offset + k * 60.0) / 60.0) * 60.0
        rad = np.radians(arm_angle)
        ex = cx + np.cos(rad) * arm_len
        ey = cy - np.sin(rad) * arm_len
        draw.line([(cx, cy), (ex, ey)], fill=255, width=max(1, int(arm_width)))

        # One level of sub-branches on each tip arm
        for t_frac in (0.35, 0.65):
            bx = cx + np.cos(rad) * arm_len * t_frac
            by = cy - np.sin(rad) * arm_len * t_frac
            for sign in (+1, -1):
                sub_angle = round((arm_angle + sign * 60.0) / 60.0) * 60.0
                sr = np.radians(sub_angle)
                sx = bx + np.cos(sr) * child_len * (1 - 0.3 * t_frac)
                sy = by - np.sin(sr) * child_len * (1 - 0.3 * t_frac)
                draw.line([(bx, by), (sx, sy)], fill=255, width=max(1, int(child_w)))


def save(img, path, dpi=300):
    img.save(path, format="PNG", dpi=(dpi, dpi))
