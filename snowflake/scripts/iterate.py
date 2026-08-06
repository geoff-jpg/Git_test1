"""
Main iterative improvement loop.

Usage:
    python -m snowflake.scripts.iterate [--iter N] [--params key=val ...]
"""

import sys
import os
import json
import csv
import time
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from snowflake.src import reiter_model, renderer, metrics


OUTPUTS = Path(__file__).resolve().parents[1] / "outputs"
ITERATIONS_DIR = OUTPUTS / "iterations"
METRICS_LOG = OUTPUTS / "metrics_log.csv"
REF_DIR = Path(__file__).resolve().parents[1] / "research" / "reference_images"

PLATEAU_WINDOW = 5          # stop after this many iterations with Q delta < threshold
PLATEAU_THRESHOLD = 0.005
MAX_ITERATIONS = 25


def _csv_header():
    return ["iteration", "Q", "S", "FD", "fd_score", "BAD", "ATP", "RSS",
            "ACLR", "arm_count", "length_ratio", "params_json"]


def _append_csv(row_dict, params):
    METRICS_LOG.parent.mkdir(parents=True, exist_ok=True)
    write_header = not METRICS_LOG.exists()
    with open(METRICS_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_csv_header())
        if write_header:
            writer.writeheader()
        writer.writerow({
            **{k: row_dict.get(k, "") for k in _csv_header()[:-1]},
            "params_json": json.dumps(params),
        })


def _suggest_params(scores, current_params):
    """Return updated params dict targeting the lowest sub-metric."""
    low_metric = min(
        [("S", scores["S"]),
         ("FD_norm", scores["fd_score"]),
         ("BAD", scores["BAD"]),
         ("ATP", scores["ATP"]),
         ("ACLR", scores["ACLR"])],
        key=lambda x: x[1]
    )[0]

    p = dict(current_params)

    if low_metric == "S":
        p["symmetry_every"] = max(10, p.get("symmetry_every", 30) - 5)
        p["mu"] = min(0.06, p.get("mu", 0.02) + 0.005)

    elif low_metric == "FD_norm":
        fd = scores["FD"]
        if fd < 1.70:   # need more branching
            p["beta"] = min(1.8, p.get("beta", 1.3) + 0.08)
            p["rho"]  = max(0.45, p.get("rho", 0.65) - 0.05)
        else:           # too fractal, smooth out
            p["beta"] = max(0.9, p.get("beta", 1.3) - 0.08)
            p["rho"]  = min(0.95, p.get("rho", 0.65) + 0.05)

    elif low_metric == "BAD":
        p["symmetry_every"] = max(10, p.get("symmetry_every", 30) - 5)

    elif low_metric == "ATP":
        p["alpha"] = min(0.18, p.get("alpha", 0.08) + 0.01)

    elif low_metric == "ACLR":
        p["initial_vapour"] = min(0.55, p.get("initial_vapour", 0.4) + 0.02)

    return p, low_metric


def run_iteration(iteration_num, params):
    """Run one full CA + render + metric cycle. Return (image_path, scores)."""
    ITERATIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ITERATIONS_DIR / f"iter_{iteration_num:02d}.png"

    print(f"\n  Running Reiter CA (steps={params.get('steps', 3000)})...", flush=True)
    t0 = time.time()
    frozen, s, u = reiter_model.run(params)
    print(f"  CA done in {time.time()-t0:.1f}s  |  frozen cells: {frozen.sum()}", flush=True)

    print("  Rendering...", flush=True)
    img = renderer.render(frozen, output_path=str(out_path))
    print(f"  Saved → {out_path}", flush=True)

    print("  Computing metrics...", flush=True)
    ref_dir = str(REF_DIR) if REF_DIR.exists() else None
    scores = metrics.composite_score(frozen, ref_dir=ref_dir)
    scores["iteration"] = iteration_num

    _append_csv(scores, params)
    return str(out_path), scores


def print_report(iteration_num, scores, params, prev_Q, next_params, low_metric):
    """Print the interim report to stdout."""
    print("\n" + "="*70)
    print(f"  ITERATION {iteration_num:02d} — INTERIM REPORT")
    print("="*70)

    # Section A
    print("\n--- Section A: Geometric Property Comparison ---\n")
    rows_a = [
        ("Symmetry Score (S)",     "> 0.97",          scores["S"],            scores["S"] >= 0.97),
        ("Fractal Dimension (FD)", "1.70 – 1.90",     scores["FD"],           1.70 <= scores["FD"] <= 1.90),
        ("Branch Angle Dist (BAD)","≥ 0.85",           scores["BAD"],          scores["BAD"] >= 0.85),
        ("Arm Taper Profile (ATP)","≥ 0.90",           scores["ATP"],          scores["ATP"] >= 0.90),
        ("Arm Count",              "= 6",              scores["arm_count"],    scores["arm_count"] == 6),
        ("Arm Length Ratio",       "0.40–0.85",        scores["length_ratio"], 0.40 <= scores["length_ratio"] <= 0.85),
        ("ACLR Score",             "pass",             scores["ACLR"],         scores["ACLR"] >= 0.8),
    ]
    print(f"  {'Property':<28} {'Target':<14} {'Measured':<12} {'Pass?'}")
    print(f"  {'-'*28} {'-'*14} {'-'*12} {'-'*6}")
    for name, target, val, ok in rows_a:
        tick = "✓" if ok else "✗"
        print(f"  {name:<28} {target:<14} {str(val):<12} {tick}")
    print(f"\n  Composite Q = {scores['Q']:.4f}  (previous: {prev_Q:.4f}, delta: {scores['Q']-prev_Q:+.4f})")

    # Narrative
    print("\n  Narrative:")
    if scores["S"] < 0.90:
        print("  * Symmetry is low — some arms differ noticeably in shape.")
    if not (1.65 <= scores["FD"] <= 1.95):
        print(f"  * Fractal dimension {scores['FD']:.3f} is outside the acceptable band — "
              + ("needs more branching." if scores["FD"] < 1.70 else "too densely branched."))
    if scores["BAD"] < 0.75:
        print("  * Branch angles deviate significantly from 60° multiples — symmetry enforcement may need to be more frequent.")
    if scores["ATP"] < 0.80:
        print("  * Arm taper is not following the expected power-law profile.")
    if scores["arm_count"] != 6:
        print(f"  * Detected {scores['arm_count']} arms instead of 6.")

    # Section B
    print("\n--- Section B: Reference Image Comparison ---\n")
    if scores["rss_per_ref"]:
        for idx, s_val in enumerate(scores["rss_per_ref"], 1):
            bar = "█" * int(s_val * 20)
            print(f"  ref_{idx:02d}  SSIM {s_val:.4f}  {bar}")
        best_idx = int(np.argmax(scores["rss_per_ref"])) + 1
        print(f"\n  Closest reference: ref_{best_idx:02d}  (SSIM {max(scores['rss_per_ref']):.4f})")
        print(f"  Mean RSS = {scores['RSS']:.4f}")
    else:
        print("  No reference images found in research/reference_images/.")
        print("  RSS metric skipped (will not contribute to Q).")

    # Section C — image path (caller will display)
    img_path = ITERATIONS_DIR / f"iter_{iteration_num:02d}.png"
    print(f"\n--- Section C: Generated Image ---\n")
    print(f"  Saved to: {img_path}")

    # Section D
    print(f"\n--- Section D: Next-Step Proposal ---\n")
    print(f"  Lowest sub-metric: {low_metric}")
    print(f"  Parameters changing for next iteration:")
    for k, v in next_params.items():
        orig = params.get(k)
        if orig != v:
            print(f"    {k}: {orig} → {v}")
    print()


def main():
    import numpy as np

    params = dict(reiter_model.DEFAULT_PARAMS)
    history_Q = []
    best_Q = -1.0
    best_iter = 0

    print("\n" + "="*70)
    print("  SNOWFLAKE SIMULATION — ITERATIVE IMPROVEMENT LOOP")
    print("="*70)
    print(f"  Max iterations: {MAX_ITERATIONS}")
    print(f"  Plateau window: {PLATEAU_WINDOW} iterations with ΔQ < {PLATEAU_THRESHOLD}")
    print(f"  User approval required after each iteration.")

    for iteration in range(MAX_ITERATIONS):
        img_path, scores = run_iteration(iteration, params)

        prev_Q = history_Q[-1] if history_Q else 0.0
        next_params, low_metric = _suggest_params(scores, params)

        print_report(iteration, scores, params, prev_Q, next_params, low_metric)

        history_Q.append(scores["Q"])
        if scores["Q"] > best_Q:
            best_Q = scores["Q"]
            best_iter = iteration

        # Stopping checks
        stop_reason = None
        if scores["Q"] >= 0.88:
            stop_reason = f"Quality ceiling reached (Q={scores['Q']:.4f} ≥ 0.88)"
        elif len(history_Q) >= PLATEAU_WINDOW:
            recent_delta = max(history_Q[-PLATEAU_WINDOW:]) - min(history_Q[-PLATEAU_WINDOW:])
            if recent_delta < PLATEAU_THRESHOLD:
                stop_reason = (f"Plateau: Q range {recent_delta:.4f} < {PLATEAU_THRESHOLD} "
                               f"over last {PLATEAU_WINDOW} iterations")

        if stop_reason:
            print(f"\n  *** STOPPING: {stop_reason} ***")
            print(f"  Best iteration: {best_iter:02d}  (Q={best_Q:.4f})")
            best_src = ITERATIONS_DIR / f"iter_{best_iter:02d}.png"
            final_dst = OUTPUTS / "final_snowflake.png"
            import shutil
            shutil.copy(str(best_src), str(final_dst))
            print(f"  Final image → {final_dst}")
            break

        # User approval gate
        print("\n" + "-"*70)
        print(f"  Iteration {iteration:02d} complete.")
        print(f"  Image: {img_path}")
        answer = input("  Proceed to next iteration? [y/n]: ").strip().lower()
        if answer != "y":
            print("  User halted iteration loop.")
            break

        params = next_params
        print()

    # Copy best regardless
    best_src = ITERATIONS_DIR / f"iter_{best_iter:02d}.png"
    final_dst = OUTPUTS / "final_snowflake.png"
    if best_src.exists():
        import shutil
        shutil.copy(str(best_src), str(final_dst))
        print(f"\n  Best image (iter {best_iter:02d}, Q={best_Q:.4f}) saved to:\n  {final_dst}")


if __name__ == "__main__":
    import numpy as np
    main()
