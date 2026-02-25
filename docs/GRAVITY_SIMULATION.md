# Gravity Simulation — Implementation Overview

This document describes the current simulation architecture for the **Gravitational Simulation of Solar System Formation** project. It references actual modules under `src/gravity/`.

## Physical model

- **Newtonian gravity** between all pairs of point masses.
- **Central star:** implemented as particle index 0 with large mass `M_star`.
- **Softening:** distance in force law is `sqrt(r^2 + ε^2)` so forces stay finite at small separations.
- **Units:** mass, distance, and time are in code units (e.g. G = 1); we do not convert to physical units.
- **2D (Phase 1):** positions and velocities are (x, y). No periodic boundaries; particles move in open space.

## Key equations

- Acceleration on particle i:  
  **a_i = G Σ_j (j≠i) m_j (r_j − r_i) / (|r_j − r_i|² + ε²)^(3/2)**
- Circular orbit speed at radius r (around central mass M):  
  **v = sqrt(G M / r)**
- Integration: **Leapfrog (kick-drift-kick)** for stability and approximate energy conservation.

## Module roles

| Module | Role |
|--------|------|
| `state.py` | `ParticleState`: positions (N,2), velocities (N,2), masses (N,). Central star is index 0. |
| `forces_cpu.py` | `compute_accelerations()` (loop) and `compute_accelerations_vectorized()` (NumPy). Optional: energy helpers kept here or in diagnostics. |
| `init_conditions.py` | `make_disk_2d(n, seed, M_star, r_min, r_max)` — star + annular disk with circular velocities; `make_cloud_2d(n, seed, M_star, r_max)` — star + random cloud with partial angular momentum; `make_uniform_2d(n, seed)` — uniform box (legacy/reference). |
| `integrators.py` | `leapfrog_step(state, dt, accel_fn)` and `euler_step()` for testing. |
| `diagnostics.py` | `compute_kinetic_energy`, `compute_potential_energy`, `compute_angular_momentum`, and `SimulationLog` for time-series of E, L. |
| `viz_live.py` | Live 2D scatter: central star as distinct marker, particles colored by distance or speed; optional diagnostic text. |
| `demo_2d.py` | Main loop: build ICs, run Leapfrog, call diagnostics, update viz; CLI for n, steps, dt, IC type. |

## Initial conditions

- **Disk:** Particles placed in an annulus between `r_min` and `r_max`. Tangential velocity set to circular orbit value `v = sqrt(G*M_star/r)` (prograde), with small random perturbations.
- **Cloud:** Particles randomly distributed inside radius `r_max`. Velocities set with a configurable fraction of circular velocity to control angular momentum.

In both cases the first particle (index 0) is the central star at the origin with mass `M_star` and zero velocity.

## Diagnostics

- **Total kinetic energy** K = (1/2) Σ m_i v_i²  
- **Total potential energy** U = −G Σ_{i<j} m_i m_j / r_ij (softened)  
- **Total angular momentum** L = Σ m_i (r_i × v_i) (z-component in 2D)

These are logged over time via `SimulationLog` and can be plotted to check conservation.

## Running

- Tests: `cd src && python -m gravity.tests_2d`
- 2D demo: `cd src && python -m gravity.demo_2d`  
  Optional: `--n`, `--steps`, `--dt`, `--ic disk|cloud`, etc., as implemented in `demo_2d.py`.
