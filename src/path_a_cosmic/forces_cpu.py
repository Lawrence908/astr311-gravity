"""CPU reference implementations of gravitational forces for Path A.

We will start with a clear O(N^2) model later. For now, this is a stub.
"""

from __future__ import annotations

import numpy as np

from .state import ParticleState


def compute_accelerations(state: ParticleState, softening: float = 0.05) -> np.ndarray:
    """Compute accelerations for all particles (stub implementation).

    The real Newtonian gravity calculation will be implemented later.
    """
    _ = softening
    return np.zeros_like(state.positions)

