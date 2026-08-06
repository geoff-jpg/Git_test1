"""Generate 10 canonical reference snowflakes with varied published parameters."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from snowflake.src.generator import generate, save, DEFAULT_PARAMS

REF_DIR = Path(__file__).resolve().parents[1] / "research" / "reference_images"
REF_DIR.mkdir(parents=True, exist_ok=True)

# 10 parameter sets drawn from Nakaya/Libbrecht morphology space
# Each represents a distinct morphological variant of stellar dendrite
VARIANTS = [
    # (arm_length, branch_levels, branch_ratio, branch_spacing, branch_offset, arm_width, branch_angle)
    # 1: classic stellar dendrite
    dict(arm_length=0.42, branch_levels=4, branch_ratio=0.42, branch_spacing=0.28, branch_offset=0.18, arm_width=3.5, branch_angle=60),
    # 2: long arms, fine secondary detail
    dict(arm_length=0.46, branch_levels=4, branch_ratio=0.38, branch_spacing=0.22, branch_offset=0.15, arm_width=3.0, branch_angle=60),
    # 3: short dense arms
    dict(arm_length=0.36, branch_levels=4, branch_ratio=0.48, branch_spacing=0.30, branch_offset=0.20, arm_width=4.0, branch_angle=60),
    # 4: sparse elegant
    dict(arm_length=0.44, branch_levels=3, branch_ratio=0.44, branch_spacing=0.35, branch_offset=0.22, arm_width=2.5, branch_angle=60),
    # 5: fernlike stellar dendrite (many levels)
    dict(arm_length=0.44, branch_levels=5, branch_ratio=0.36, branch_spacing=0.20, branch_offset=0.12, arm_width=3.0, branch_angle=60),
    # 6: broad 55° branching angle
    dict(arm_length=0.42, branch_levels=4, branch_ratio=0.40, branch_spacing=0.26, branch_offset=0.18, arm_width=3.0, branch_angle=55),
    # 7: tight 65° branching
    dict(arm_length=0.42, branch_levels=4, branch_ratio=0.44, branch_spacing=0.28, branch_offset=0.20, arm_width=3.0, branch_angle=65),
    # 8: wide-spaced branching
    dict(arm_length=0.44, branch_levels=4, branch_ratio=0.42, branch_spacing=0.38, branch_offset=0.25, arm_width=3.5, branch_angle=60),
    # 9: compact with thick arms
    dict(arm_length=0.38, branch_levels=4, branch_ratio=0.45, branch_spacing=0.25, branch_offset=0.15, arm_width=4.5, branch_angle=60),
    # 10: very fine delicate
    dict(arm_length=0.45, branch_levels=5, branch_ratio=0.38, branch_spacing=0.22, branch_offset=0.14, arm_width=2.0, branch_angle=60),
]

for i, variant in enumerate(VARIANTS, 1):
    p = {**DEFAULT_PARAMS, **variant, "size": 512, "noise_sigma": 0}
    img, _ = generate(p)
    # Save greyscale for metric comparison
    grey = img.convert("L")
    out = REF_DIR / f"ref_{i:02d}.png"
    grey.save(str(out))
    print(f"Saved {out}")

print("Done — 10 reference images created.")
