"""Procedural geometric snowflake arm drawing (Algorithm B)."""

import numpy as np
from PIL import Image, ImageDraw


def draw_snowflake(size=2048, params=None):
    """Return a greyscale PIL Image with a procedurally drawn snowflake."""
    p = {
        "arm_length_ratio": 0.42,   # arm length as fraction of half-image
        "base_width_ratio": 0.018,  # arm base width as fraction of image size
        "taper_alpha": 0.60,        # width taper exponent
        "secondary_spacing": 0.12,  # secondary branch spacing (fraction of arm length)
        "secondary_scale": 0.38,    # secondary length as fraction of arm length
        "secondary_taper": 1.2,
        "tertiary_scale": 0.35,     # tertiary as fraction of secondary
        "tip_plate_ratio": 0.08,    # tip hexagon size as fraction of arm length
        **(params or {}),
    }

    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    cx = cy = size // 2
    arm_len = p["arm_length_ratio"] * size / 2
    base_w  = p["base_width_ratio"] * size

    for arm_idx in range(6):
        angle = np.radians(arm_idx * 60)
        _draw_arm(draw, cx, cy, angle, arm_len, base_w, p)

    return img


def _poly_arm(cx, cy, angle, length, base_w, taper_alpha):
    """Return polygon points for a tapered arm rectangle."""
    tip_w = max(1.0, base_w * 0.08)
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    cos_p, sin_p = np.cos(angle + np.pi/2), np.sin(angle + np.pi/2)

    # Four corners: base-left, base-right, tip-right, tip-left
    bx, by = cx, cy
    tx = cx + cos_a * length
    ty = cy - sin_a * length

    bl = (bx + cos_p * base_w/2, by - sin_p * base_w/2)
    br = (bx - cos_p * base_w/2, by + sin_p * base_w/2)
    tr = (tx - cos_p * tip_w/2,  ty + sin_p * tip_w/2)
    tl = (tx + cos_p * tip_w/2,  ty - sin_p * tip_w/2)
    return [bl, br, tr, tl]


def _draw_arm(draw, cx, cy, angle, arm_len, base_w, p):
    """Draw one arm with secondary and tertiary branches."""
    taper_alpha = p["taper_alpha"]

    # Main spine
    poly = _poly_arm(cx, cy, angle, arm_len, base_w, taper_alpha)
    draw.polygon(poly, fill=255)

    # Secondary branches
    spacing = p["secondary_spacing"] * arm_len
    sec_base_len = p["secondary_scale"] * arm_len
    sec_taper = p["secondary_taper"]

    n_secondary = max(1, int(arm_len / spacing))
    cos_a, sin_a = np.cos(angle), np.sin(angle)

    for k in range(1, n_secondary + 1):
        r = k * spacing
        if r >= arm_len * 0.92:
            break
        frac = r / arm_len
        # Width of main arm at this point
        w_at_r = base_w * max(0.05, (1 - frac) ** taper_alpha)
        # Secondary length scales down toward tip
        sec_len = sec_base_len * max(0.05, (1 - frac) ** sec_taper)
        if sec_len < 2:
            continue
        sec_w = w_at_r * 0.55

        bx = cx + cos_a * r
        by = cy - sin_a * r

        for sign in (+1, -1):
            sec_angle = angle + sign * np.radians(60)
            sec_poly = _poly_arm(bx, by, sec_angle, sec_len, sec_w, taper_alpha)
            draw.polygon(sec_poly, fill=255)

            # Tertiary branches from each secondary
            ter_len = sec_len * p["tertiary_scale"]
            ter_w   = sec_w * 0.45
            if ter_len < 2:
                continue
            ter_spacing = sec_len * 0.40
            n_ter = max(1, int(sec_len / ter_spacing))
            cos_s, sin_s = np.cos(sec_angle), np.sin(sec_angle)
            for m in range(1, n_ter + 1):
                tr_r = m * ter_spacing
                if tr_r >= sec_len * 0.85:
                    break
                tbx = bx + cos_s * tr_r
                tby = by - sin_s * tr_r
                for tsign in (+1, -1):
                    ter_angle = sec_angle + tsign * np.radians(60)
                    ter_poly = _poly_arm(tbx, tby, ter_angle, ter_len, ter_w, taper_alpha)
                    draw.polygon(ter_poly, fill=220)

    # Hexagonal tip plate
    _draw_hex(draw, cx + cos_a * arm_len, cy - sin_a * arm_len,
              p["tip_plate_ratio"] * arm_len, angle)


def _draw_hex(draw, cx, cy, radius, angle_offset=0):
    """Draw a small hexagon centred at (cx, cy)."""
    pts = []
    for i in range(6):
        a = angle_offset + np.radians(i * 60)
        pts.append((cx + radius * np.cos(a), cy - radius * np.sin(a)))
    draw.polygon(pts, fill=255)
