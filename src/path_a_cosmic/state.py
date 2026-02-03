"""Data structures for the Path A gravity simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass
class ParticleState:
    """Minimal particle state for the toy gravity model.

    For now this is 2D-only (x, y). We can later extend to 3D.
    """

    positions: np.ndarray  # shape (N, 2)
    velocities: np.ndarray  # shape (N, 2)
    masses: np.ndarray  # shape (N,)


class AccelerationFn(Protocol):
    """Callable type for computing accelerations."""

    def __call__(self, state: ParticleState) -> np.ndarray:  # pragma: no cover
        ...

