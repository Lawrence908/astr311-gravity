"""Frame/plot export utilities for Path A visualizations."""

from __future__ import annotations

from pathlib import Path

from .state import ParticleState


def save_frame(state: ParticleState, out_dir: Path, step: int) -> None:
    """Placeholder for a function that saves a frame image.

    Implementation will use matplotlib; for now we just write a dummy file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    dummy_path = out_dir / f"frame_{step:05d}.txt"
    dummy_path.write_text("Placeholder for rendered frame.\n")
    _ = state

