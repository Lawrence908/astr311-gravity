"""Replay file format and I/O for the gravity simulation.

See docs/REPLAY_FORMAT.md for the .npz layout.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .state import ParticleState


def save_replay(
    path: str | Path,
    positions_list: list[np.ndarray],
    step_indices: list[int],
    masses: np.ndarray,
    dt: float,
    softening: float = 0.05,
    G: float = 1.0,
) -> None:
    """Write a replay .npz file.

    Parameters
    ----------
    path : path to output .npz file
    positions_list : list of position arrays, each shape (N, 2) or (N, 3)
    step_indices : step number for each snapshot (length = len(positions_list))
    masses : array of shape (N,)
    dt, softening, G : simulation parameters
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    positions = np.stack(positions_list, axis=0)
    steps = np.array(step_indices, dtype=np.int64)

    np.savez(
        path,
        positions=positions,
        steps=steps,
        masses=masses,
        dt=np.float64(dt),
        softening=np.float64(softening),
        G=np.float64(G),
        n_particles=np.int64(masses.shape[0]),
        n_snapshots=np.int64(len(positions_list)),
    )


def load_replay(path: str | Path) -> dict:
    """Load a replay .npz file. Returns a dict with keys:

    - positions: (n_snapshots, N, 2) or (n_snapshots, N, 3)
    - steps: (n_snapshots,)
    - masses: (N,)
    - dt, softening, G: scalars
    - n_particles, n_snapshots: ints
    """
    data = np.load(path, allow_pickle=False)
    return {
        "positions": data["positions"],
        "steps": data["steps"],
        "masses": data["masses"],
        "dt": float(data["dt"]),
        "softening": float(data["softening"]),
        "G": float(data["G"]),
        "n_particles": int(data["n_particles"]),
        "n_snapshots": int(data["n_snapshots"]),
    }
