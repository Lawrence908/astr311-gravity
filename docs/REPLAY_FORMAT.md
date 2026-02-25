# Replay File Format

Replay files store simulation snapshots (particle positions at fixed step intervals) plus metadata so that a viewer can replay the run without re-running the simulation.

## Format: NumPy .npz

The replay is a single `.npz` file (e.g. `outputs/runs/run.npz`) produced by `gravity.replay.save_replay` and loaded with `gravity.replay.load_replay`.

## Arrays and scalars

| Key           | Shape / type   | Description |
|---------------|----------------|-------------|
| `positions`   | (n_snapshots, N, 2) or (n_snapshots, N, 3) | Position of each particle at each saved step; index 0 is the central star in disk/cloud runs. |
| `steps`       | (n_snapshots,) int64 | Step index for each snapshot. |
| `masses`      | (N,) float64   | Particle masses (constant for the run). |
| `dt`          | scalar float64 | Timestep. |
| `softening`   | scalar float64 | Gravitational softening length. |
| `G`           | scalar float64 | Gravitational constant in code units. |
| `n_particles` | scalar int64   | N. |
| `n_snapshots` | scalar int64   | Number of saved frames. |

## Usage

- **Export:** `python -m gravity.demo_2d --save-replay outputs/runs/run.npz --replay-every 20 --no-viz --steps 1000`
- **Load in Python:** `from gravity.replay import load_replay; data = load_replay("outputs/runs/run.npz")` then `data["positions"]`, `data["steps"]`, etc.
- **Web viewer:** The WebGL viewer can load a converted form (e.g. JSON or a binary format) of this data; conversion scripts can use `load_replay` and then serialize as needed.

## Notes

- Velocities are not stored; the format is position-only for simplicity and smaller files.
- For 2D runs, `positions` has shape `(n_snapshots, N, 2)`; for 3D, `(n_snapshots, N, 3)`.
