"""2D gravity demo: central star + disk or cloud, vectorized forces, diagnostics (Phase 1).

Run with:

    cd src
    python -m gravity.demo_2d [--n 1000] [--steps 2000] [--ic disk|cloud] [--dt 0.01]
    python -m gravity.demo_2d --steps 5000 --viz-every 20   # run longer, fewer redraws
    python -m gravity.demo_2d --pause 0.02                  # slow down display
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .diagnostics import SimulationLog, compute_angular_momentum, compute_total_energy
from .forces_cpu import compute_accelerations_vectorized
from .init_conditions import make_cloud_2d, make_disk_2d
from .integrators import leapfrog_step
from .progress import report_progress
from .state import ParticleState
from .replay import save_replay
from .viz_export import save_frame
from .viz_live import LiveScatter2D


def _make_accel_fn(softening: float = 0.05, G: float = 1.0):
    def accel_fn(state: ParticleState):
        return compute_accelerations_vectorized(
            state, softening=softening, G=G
        )

    return accel_fn


def run_demo(
    n_particles: int = 1000,
    n_steps: int = 2000,
    dt: float = 0.01,
    softening: float = 0.05,
    ic: str = "disk",
    seed: int | None = 42,
    M_star: float = 1.0,
    r_min: float = 0.5,
    r_max: float = 2.0,
    log_interval: int = 50,
    viz_every: int = 2,
    pause: float = 0.001,
    save_frames: bool = False,
    frames_dir: str | None = None,
    save_every: int | None = None,
    show_live: bool = True,
    diagnostics_path: str | None = None,
    replay_path: str | None = None,
    replay_every: int = 10,
) -> None:
    """Run 2D gravity demo with central star, disk or cloud ICs, and diagnostics.

    viz_every: update the plot every this many steps (larger = fewer redraws, more
        simulation time per frame = faster to watch long runs).
    pause: seconds to pause after each plot update (larger = slower, easier to watch).
    save_frames: if True, write PNG frames to frames_dir.
    frames_dir: directory for frame PNGs (default: outputs/frames).
    save_every: save a frame every this many steps (default: same as viz_every).
    show_live: if False, do not open the live window (useful when only saving frames).
    diagnostics_path: if set, save E and Lz vs step plot to this path after the run.
    replay_path: if set, save replay .npz to this path (positions at replay_every steps).
    replay_every: save a snapshot every this many steps when replay_path is set.
    """
    if frames_dir is None:
        frames_dir = "outputs/frames"
    if save_every is None:
        save_every = viz_every

    if ic == "disk":
        state = make_disk_2d(
            n_particles, seed=seed, M_star=M_star, r_min=r_min, r_max=r_max
        )
    elif ic == "cloud":
        state = make_cloud_2d(
            n_particles, seed=seed, M_star=M_star, r_max=r_max
        )
    else:
        raise ValueError(f"Unknown ic={ic!r}; use 'disk' or 'cloud'")

    accel_fn = _make_accel_fn(softening=softening)
    sim_log = SimulationLog()
    frames_path = Path(frames_dir) if save_frames else None
    if save_frames:
        frames_path.mkdir(parents=True, exist_ok=True)

    viz = LiveScatter2D(r_max=r_max) if show_live else None
    if show_live:
        plt.ion()
    last_E, last_L = None, None
    replay_positions: list[np.ndarray] = []
    replay_steps: list[int] = []

    for step in range(n_steps):
        state = leapfrog_step(state, dt=dt, accel_fn=accel_fn)

        if step % log_interval == 0:
            sim_log.append(step, state, softening=softening, G=1.0)
            last_E = compute_total_energy(state, softening=softening, G=1.0)
            last_L = compute_angular_momentum(state)
        extra = f"E={last_E:.6g}  Lz={last_L:.6g}" if last_E is not None else None
        report_progress(step, n_steps, "2D demo", extra=extra)

        if step % viz_every == 0 and show_live and viz is not None:
            viz.update(state, step=step, E=last_E, L=last_L)
            plt.pause(pause)

        if save_frames and frames_path is not None and step % save_every == 0:
            save_frame(
                state,
                frames_path / f"frame_{step:06d}.png",
                step=step,
                r_max=r_max,
                E=last_E,
                L=last_L,
            )

        if replay_path is not None and step % replay_every == 0:
            replay_positions.append(state.positions.copy())
            replay_steps.append(step)

    # Final log entry and 100% progress
    report_progress(n_steps, n_steps, "2D demo", extra=f"E={last_E:.6g}  Lz={last_L:.6g}" if last_E is not None else None)
    sim_log.append(n_steps, state, softening=softening, G=1.0)
    if save_frames and frames_path is not None:
        save_frame(
            state,
            frames_path / f"frame_{n_steps:06d}.png",
            step=n_steps,
            r_max=r_max,
            E=last_E,
            L=last_L,
        )
        print(f"Frames saved to {frames_path}")

    if replay_path is not None:
        replay_positions.append(state.positions.copy())
        replay_steps.append(n_steps)
        save_replay(
            replay_path,
            positions_list=replay_positions,
            step_indices=replay_steps,
            masses=state.masses,
            dt=dt,
            softening=softening,
            G=1.0,
        )
        print(f"Replay saved to {replay_path} ({len(replay_positions)} snapshots)")

    if diagnostics_path is not None:
        Path(diagnostics_path).parent.mkdir(parents=True, exist_ok=True)
        sim_log.summary_plot(path=diagnostics_path)
        print(f"Diagnostics plot saved to {diagnostics_path}")

    print("Demo finished; close the plot window to exit." if show_live else "Demo finished.")
    if show_live and viz is not None:
        time.sleep(0.5)
        plt.ioff()
        viz.show()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Run 2D gravity demo (central star + disk or cloud)."
    )
    p.add_argument("--n", type=int, default=1000, help="Number of disk/cloud particles")
    p.add_argument("--steps", type=int, default=2000, help="Number of timesteps (use 5000+ for long runs)")
    p.add_argument("--dt", type=float, default=0.01, help="Timestep")
    p.add_argument("--viz-every", type=int, default=2, metavar="N", help="Update plot every N steps (e.g. 20 = faster to watch long runs)")
    p.add_argument("--pause", type=float, default=0.001, metavar="SEC", help="Pause (seconds) per frame (e.g. 0.02 = slow down display)")
    p.add_argument(
        "--ic",
        choices=["disk", "cloud"],
        default="disk",
        help="Initial condition: disk or cloud",
    )
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--M_star", type=float, default=1.0, help="Central star mass")
    p.add_argument("--r_min", type=float, default=0.5, help="Disk inner radius (disk IC)")
    p.add_argument("--r_max", type=float, default=2.0, help="Disk/cloud outer radius")
    p.add_argument("--save-frames", action="store_true", help="Save PNG frames to outputs/frames (or --frames-dir)")
    p.add_argument("--frames-dir", type=str, default="outputs/frames", help="Directory for saved frames")
    p.add_argument("--save-every", type=int, default=None, metavar="N", help="Save a frame every N steps (default: same as --viz-every)")
    p.add_argument("--no-viz", action="store_true", help="Do not show live window (use with --save-frames for batch export)")
    p.add_argument("--save-diagnostics", type=str, default=None, metavar="PATH", help="Save E and Lz vs step plot to PATH (e.g. outputs/diagnostics.png)")
    p.add_argument("--save-replay", type=str, default=None, metavar="PATH", help="Save replay .npz to PATH (e.g. outputs/runs/run.npz)")
    p.add_argument("--replay-every", type=int, default=10, metavar="N", help="Save a snapshot every N steps when using --save-replay")
    args = p.parse_args()

    run_demo(
        n_particles=args.n,
        n_steps=args.steps,
        dt=args.dt,
        ic=args.ic,
        seed=args.seed,
        M_star=args.M_star,
        r_min=args.r_min,
        r_max=args.r_max,
        viz_every=args.viz_every,
        pause=args.pause,
        save_frames=args.save_frames,
        frames_dir=args.frames_dir,
        save_every=args.save_every,
        show_live=not args.no_viz,
        diagnostics_path=args.save_diagnostics,
        replay_path=args.save_replay,
        replay_every=args.replay_every,
    )


if __name__ == "__main__":
    main()
