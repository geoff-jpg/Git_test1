"""Hexagonal grid primitives using offset coordinates."""

import numpy as np


def hex_neighbours(i, j, rows, cols):
    """Return valid (row, col) neighbours of cell (i,j) on an offset-coordinate hex grid."""
    if i % 2 == 0:
        candidates = [
            (i,   j-1), (i,   j+1),
            (i-1, j-1), (i-1, j),
            (i+1, j-1), (i+1, j),
        ]
    else:
        candidates = [
            (i,   j-1), (i,   j+1),
            (i-1, j),   (i-1, j+1),
            (i+1, j),   (i+1, j+1),
        ]
    return [(r, c) for r, c in candidates if 0 <= r < rows and 0 <= c < cols]


def hex_laplacian(field):
    """Approximate hexagonal Laplacian via six shifted copies (periodic-like, zero-padded)."""
    rows, cols = field.shape
    result = np.zeros_like(field)

    # even rows: neighbours at (i-1,j-1),(i-1,j),(i+1,j-1),(i+1,j),(i,j-1),(i,j+1)
    # odd  rows: neighbours at (i-1,j),(i-1,j+1),(i+1,j),(i+1,j+1),(i,j-1),(i,j+1)

    # We compute a uniform approximation: average of six shifts minus 6*centre
    # Using roll with appropriate offsets; even/odd row correction is applied via a mask.

    even = np.zeros((rows, cols), dtype=bool)
    even[0::2, :] = True
    odd = ~even

    # Left / right (same for both parities)
    nb_left  = np.roll(field, 1, axis=1);  nb_left[:, 0]  = 0
    nb_right = np.roll(field, -1, axis=1); nb_right[:, -1] = 0

    # Upper neighbours
    up = np.roll(field, 1, axis=0); up[0, :] = 0
    # even rows: upper-left = up shifted right, upper-right = up
    up_left_even  = np.roll(up, 1, axis=1);  up_left_even[:, 0]  = 0
    up_right_even = up.copy()
    # odd rows: upper-left = up, upper-right = up shifted left
    up_left_odd   = up.copy()
    up_right_odd  = np.roll(up, -1, axis=1); up_right_odd[:, -1] = 0

    # Lower neighbours
    dn = np.roll(field, -1, axis=0); dn[-1, :] = 0
    dn_left_even  = np.roll(dn, 1, axis=1);  dn_left_even[:, 0]  = 0
    dn_right_even = dn.copy()
    dn_left_odd   = dn.copy()
    dn_right_odd  = np.roll(dn, -1, axis=1); dn_right_odd[:, -1] = 0

    nb_sum = np.where(even,
                      nb_left + nb_right + up_left_even + up_right_even + dn_left_even + dn_right_even,
                      nb_left + nb_right + up_left_odd  + up_right_odd  + dn_left_odd  + dn_right_odd)

    return nb_sum - 6 * field


def apply_d6_symmetry(grid):
    """Enforce D6 symmetry: copy sector 0 (top-right 60° wedge) to all 6 sectors."""
    rows, cols = grid.shape
    cx, cy = cols // 2, rows // 2

    # Work in Cartesian coordinates from centre, rotate each pixel back to sector 0
    result = grid.copy()
    y_idx, x_idx = np.mgrid[0:rows, 0:cols]
    dx = x_idx - cx
    dy = cy - y_idx  # flip y so up is positive

    r = np.sqrt(dx**2 + dy**2)
    theta = np.arctan2(dy, dx)  # -π to π

    # Normalise theta to sector 0: [0, π/3)
    theta_mod = theta % (2 * np.pi / 6)

    # Sample source pixel from sector 0
    src_x = (cx + r * np.cos(theta_mod)).astype(int)
    src_y = (cy - r * np.sin(theta_mod)).astype(int)

    valid = (src_x >= 0) & (src_x < cols) & (src_y >= 0) & (src_y < rows)
    result[valid] = grid[src_y[valid], src_x[valid]]
    return result
