"""Reiter (1996) cellular automaton for snow crystal growth on a hexagonal lattice."""

import numpy as np
from .hex_lattice import hex_laplacian, apply_d6_symmetry


DEFAULT_PARAMS = {
    "rho": 0.65,      # diffusion constant
    "beta": 1.3,      # attachment coefficient
    "alpha": 0.08,    # boundary diffusion
    "theta": 0.025,   # melting at tips
    "kappa": 0.005,   # plate / dendrite balance
    "mu": 0.02,       # noise smoothing
    "upsilon": 0.00001,  # initial seed noise
    "sigma": 0.00001,    # crystal noise
    "initial_vapour": 0.4,
    "grid_size": 400,
    "symmetry_every": 30,
    "steps": 3000,
}


def run(params=None):
    """Run the Reiter CA and return the frozen mask (2D bool array)."""
    p = {**DEFAULT_PARAMS, **(params or {})}
    N = p["grid_size"]
    rho = p["rho"]
    beta = p["beta"]
    alpha = p["alpha"]
    theta = p["theta"]
    kappa = p["kappa"]
    mu = p["mu"]
    sym_every = p["symmetry_every"]
    steps = p["steps"]

    # State arrays
    u = np.full((N, N), p["initial_vapour"])   # water vapour
    s = np.zeros((N, N))                         # ice content
    frozen = np.zeros((N, N), dtype=bool)

    # Seed: freeze centre cell
    cx = cy = N // 2
    frozen[cy, cx] = True
    s[cy, cx] = 1.0
    u[cy, cx] = 0.0

    rng = np.random.default_rng(42)

    for step in range(steps):
        # --- diffusion (non-frozen cells only) ---
        lap = hex_laplacian(u)
        u_new = u + (rho / 12.0) * lap
        u_new[frozen] = u[frozen]  # frozen cells don't diffuse

        # --- attachment: boundary cells adjacent to frozen gain ice ---
        # Boundary = non-frozen cells that have at least one frozen neighbour
        # Approximate with a max-pooling dilation: dilate frozen mask
        from scipy.ndimage import binary_dilation
        struct = np.array([[0,1,1],[1,1,1],[1,1,0]], dtype=bool)  # hex-approx 6-conn
        dilated = binary_dilation(frozen, structure=struct)
        boundary = dilated & ~frozen

        # Each boundary cell: receive attachment from local vapour
        attachment = (beta * u_new)
        s_new = s.copy()
        s_new[boundary] += attachment[boundary]
        u_new[boundary] *= (1.0 - beta)
        u_new[u_new < 0] = 0

        # Quasi-liquid layer: boundary cells re-emit a fraction
        u_new[boundary] += theta * s_new[boundary]
        s_new[boundary] -= theta * s_new[boundary]

        # --- freezing ---
        newly_frozen = (s_new >= 1.0) & ~frozen
        excess = s_new - 1.0
        excess[~newly_frozen] = 0
        u_new += excess * kappa   # re-emit excess as vapour
        s_new[newly_frozen] = 1.0
        frozen |= newly_frozen

        # --- smoothing ---
        u_new = u_new * (1 - mu) + mu * 0.5 * (np.roll(u_new, 1, axis=1) + np.roll(u_new, -1, axis=1))

        # --- clamp ---
        u_new = np.clip(u_new, 0, 2.0)
        s_new = np.clip(s_new, 0, 1.0)

        u, s = u_new, s_new

        # --- enforce D6 symmetry periodically ---
        if step % sym_every == 0 and step > 0:
            # Symmetrise the frozen mask and ice content
            frozen_f = frozen.astype(float)
            frozen_sym = apply_d6_symmetry(frozen_f)
            frozen = frozen_sym > 0.5
            s_sym = apply_d6_symmetry(s)
            s[frozen] = np.maximum(s[frozen], s_sym[frozen])

        # Early stop if snowflake reaches 85% of half-grid
        r_max = np.sqrt(np.sum((np.argwhere(frozen) - [cy, cx])**2, axis=1)).max() if frozen.any() else 0
        if r_max > 0.85 * (N // 2):
            break

    return frozen, s, u
