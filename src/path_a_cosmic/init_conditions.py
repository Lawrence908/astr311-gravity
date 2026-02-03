"""Initial condition generators for the Path A gravity demo."""

from __future__ import annotations

import numpy as np

from .state import ParticleState


def make_uniform_2d(n: int, seed: int | None = None) -> ParticleState:
    """Return a nearly uniform 2D particle distribution with tiny noise.

    Implementation is intentionally simple and will be refined later.
    """
    rng = np.random.default_rng(seed)

    # Placeholders: zero arrays to keep the function importable.
    positions = np.zeros((n, 2), dtype=float)
    velocities = np.zeros_like(positions)
    masses = np.ones(n, dtype=float)

    return ParticleState(positions=positions, velocities=velocities, masses=masses)

