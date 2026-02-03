"""Live visualization helpers for the 2D Path A demo."""

from __future__ import annotations

import matplotlib.pyplot as plt

from .state import ParticleState


class LiveScatter2D:
    """Minimal live 2D scatter plot for particles."""

    def __init__(self) -> None:
        self.fig, self.ax = plt.subplots()
        self.scat = None
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_title("Cosmic Origins — Path A (2D demo)")

    def update(self, state: ParticleState) -> None:
        x = state.positions[:, 0]
        y = state.positions[:, 1]
        if self.scat is None:
            self.scat = self.ax.scatter(x, y, s=2)
        else:
            self.scat.set_offsets(list(zip(x, y)))
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def show(self) -> None:
        plt.show()

