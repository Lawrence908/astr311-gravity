"""Minimal 3D gravity demo (Phase 2). Run with: cd src && python -m gravity.demo_3d [--n 200] [--steps 500]

Export 3D replay for web viewer:
  python -m gravity.demo_3d --save-replay ../outputs/runs/run3d.npz --replay-every 20 --no-viz --steps 500 --n 200
Then from repo root: python tools/export_replay_to_json.py outputs/runs/run3d.npz web-viewer/replay.json
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import matplotlib.pyplot as plt

from .diagnostics import compute_angular_momentum, compute_total_energy
from .forces_cpu import compute_accelerations_vectorized
from .init_conditions import make_disk_3d
from .integrators import leapfrog_step
from .progress import report_progress
from .replay import save_replay
from .state import ParticleState
from .viz_3d import LiveScatter3D


def main() -> None:
    p = argparse.ArgumentParser(description="Run 3D gravity demo (thick disk).")
    p.add_argument("--n", type=int, default=200, help="Number of disk particles")
    p.add_argument("--steps", type=int, default=500, help="Number of timesteps")
    p.add_argument("--dt", type=float, default=0.01, help="Timestep")
    p.add_argument("--r-max", type=float, default=2.0, dest="r_max", help="Disk outer radius")
    p.add_argument("--viz-every", type=int, default=2, help="Update plot every N steps")
    p.add_argument("--save-replay", type=str, default=None, metavar="PATH", help="Save replay .npz (3D positions) for web viewer")
    p.add_argument("--replay-every", type=int, default=10, metavar="N", help="Save snapshot every N steps when using --save-replay")
    p.add_argument("--no-viz", action="store_true", help="No live matplotlib window (use with --save-replay for batch export)")
    args = p.parse_args()

    state = make_disk_3d(args.n, seed=42, M_star=1.0, r_min=0.5, r_max=args.r_max, thickness=0.05)

    def accel_fn(s: ParticleState):
        return compute_accelerations_vectorized(s, softening=0.05, G=1.0)

    replay_positions = []
    replay_steps_list = []
    show_live = not args.no_viz
    viz = LiveScatter3D(r_max=args.r_max) if show_live else None
    if show_live:
        plt.ion()
    last_E, last_L = None, None

    total_steps = args.steps
    for step in range(total_steps):
        state = leapfrog_step(state, dt=args.dt, accel_fn=accel_fn)
        if step % 10 == 0:
            last_E = compute_total_energy(state, softening=0.05, G=1.0)
            last_L = compute_angular_momentum(state)
        report_progress(step, total_steps, "3D demo")
        if show_live and step % args.viz_every == 0:
            viz.update(state, step=step, E=last_E, L=last_L)
            plt.pause(0.001)
        if args.save_replay is not None and step % args.replay_every == 0:
            replay_positions.append(state.positions.copy())
            replay_steps_list.append(step)

    report_progress(total_steps, total_steps, "3D demo")
    if args.save_replay is not None:
        replay_positions.append(state.positions.copy())
        replay_steps_list.append(args.steps)
        path = Path(args.save_replay)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_replay(
            path,
            positions_list=replay_positions,
            step_indices=replay_steps_list,
            masses=state.masses,
            dt=args.dt,
            softening=0.05,
            G=1.0,
        )
        print(f"Replay saved to {args.save_replay} ({len(replay_positions)} snapshots, 3D)")

    print("3D demo finished; close the plot window to exit." if show_live else "3D demo finished.")
    if show_live and viz is not None:
        time.sleep(0.5)
        plt.ioff()
        viz.show()


if __name__ == "__main__":
    main()
