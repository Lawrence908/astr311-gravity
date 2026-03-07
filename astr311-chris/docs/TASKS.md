# Tasks — Phase 1 (2D prototype)

Aligned with `docs/work-breakdown.md` and the 2D CPU prototype milestone.

## 1. Simulation core

- [x] Gravitational force model: Newtonian with softening; configurable G and ε.
- [x] Force implementation: loop version (reference) and vectorized NumPy version for performance.
- [x] Numerical integration: Leapfrog (and Euler for testing); adjustable timestep.
- [x] Central mass: star as particle index 0 in state.
- [x] Initial conditions: `make_disk_2d` (annular disk, circular velocities) and `make_cloud_2d` (random cloud, configurable angular momentum).
- [x] Verify stability over extended simulation time (`test_long_run.py`: bounded motion, E/L drift).

## 2. Diagnostics and validation

- [x] Track total kinetic and potential energy.
- [x] Track total angular momentum (z-component in 2D).
- [x] Diagnostics module: `diagnostics.py` with energy, angular momentum, and `SimulationLog`.
- [x] Log simulation summaries (E, L at intervals in demo; `--save-diagnostics` for plot).
- [x] Produce plots demonstrating conservation trends (`SimulationLog.summary_plot`).

## 3. Visualization

- [x] Minimal live 2D scatter plot.
- [x] Central star rendered as distinct marker; particles colored (e.g. by distance or speed).
- [x] Show step count and basic diagnostics in title or annotation.
- [x] Frame export to `outputs/frames/` (`--save-frames`, `--frames-dir`, `--save-every`).

## 4. Demo and CLI

- [x] `demo_2d.py`: run loop with disk or cloud ICs, vectorized forces, periodic diagnostic output.
- [x] Command-line arguments: particle count, steps, dt, IC type (disk/cloud).

## 5. Testing

- [x] Two-body symmetry test.
- [x] Center-of-mass motion test.
- [x] Energy drift test.
- [x] Circular orbit stability test (single particle around central mass).
- [x] Vectorized vs loop force comparison test.
- [x] Angular momentum conservation test.

## 6. Repo and config

- [x] `src/` layout; `config.py` with simulation parameters (e.g. M_star, r_min, r_max, ic_type).
- [x] `requirements.txt`, `pyproject.toml`, `.gitignore`.
- [x] `cd src && python -m main` runs; `python -m gravity.tests_2d` and `python -m gravity.demo_2d` work.

## Phase 2 — 3D extension

- [x] State and forces support (N, 3) positions; `make_disk_3d`, `make_cloud_3d`.
- [x] Diagnostics: `compute_angular_momentum_vector` for 3D.
- [x] `viz_3d.py`: LiveScatter3D (mplot3d); `demo_3d.py`.
- [x] 3D tests: `tests_3d.py` (energy drift, circular orbit, angular momentum).

## Phase 3 — Scaling and performance

- [x] `benchmark.py`: time vectorized force computation at increasing N.
- [x] `docs/PERFORMANCE.md`: CPU particle limits and how to run benchmark.

## Phase 4 — Replay and WebGL viewer

- [x] Replay format: `.npz` with positions, steps, masses, dt, softening, G (`replay.py`; `docs/REPLAY_FORMAT.md`).
- [x] `--save-replay`, `--replay-every` in `demo_2d.py`.
- [x] `tools/export_replay_to_json.py`: convert .npz to JSON for browser.
- [x] `web-viewer/`: Three.js viewer (particles, star, orbit controls, timeline slider).
