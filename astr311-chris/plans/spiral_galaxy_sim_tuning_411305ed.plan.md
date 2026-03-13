---
name: Spiral Galaxy Sim Tuning
overview: Tune the N-body simulation to produce stable spiral galaxy patterns by fixing mass ratios, adding a static dark matter halo potential, calibrating softening, and exposing a "dark matter" slider in the web UI.
todos:
  - id: halo-force
    content: Add compute_halo_acceleration() Hernquist function to forces_cpu.py and forces_gpu.py
    status: completed
  - id: fix-init-velocities
    content: "Update init_conditions.py: accept M_halo/a_halo, fix v_circ to use enclosed halo mass"
    status: completed
  - id: update-config
    content: Add M_halo and a_halo fields to GravityConfig in config.py
    status: completed
  - id: wire-demos
    content: Add halo CLI args to demo_2d.py and demo_3d.py, compose accel_fn with halo contribution
    status: in_progress
  - id: wire-server
    content: Add M_halo/a_halo to sim_server.py parse_run_params and build_run_cmd
    status: pending
  - id: web-ui-halo
    content: Add dark matter halo mass slider and scale radius input to web viewer form
    status: pending
  - id: mass-ratio-slider
    content: Replace separate M_star/m_particle inputs with a mass ratio slider in queue.html
    status: pending
  - id: visual-sizing
    content: Scale particle/star sphere sizes in viewer.html proportional to mass ratio
    status: pending
  - id: test-presets
    content: Document recommended parameter presets for spiral galaxy runs (1k-5k particles)
    status: pending
isProject: false
---

# Spiral Galaxy Simulation Tuning Plan

## Why particles spiral inward (the real problem)

The issue is **not** the softening value -- it's the **mass ratio**. Currently:

- `M_star = 1.0`, `m_particle = 1/(N+1)` -> total disk mass ~ 1.0 (same as the star)
- Initial velocities are set to `v_circ = sqrt(G * M_star / r)`, which only accounts for the star, ignoring the disk's own mass
- A disk with mass comparable to the central body is **violently unstable** -- it forms bars and clumps that transfer angular momentum inward, causing infall
- No dark matter halo means no stabilizing background potential

In real galaxies, the disk is ~5% of total mass; dark matter provides ~85%.

## Physics changes (3 items)

### 1. Add a static dark matter halo potential

Add a new force contribution from a static (non-particle) dark matter halo using a **Hernquist profile** (simple, analytically tractable):

```
a_halo(r) = -G * M_halo / (r + a)^2 * (r_hat)
```

Where `M_halo` is total halo mass and `a` is scale radius. This provides:

- A flat rotation curve at large radii (like real galaxies)
- Extra centripetal force to keep disk particles in orbit
- A single "dark matter mass" knob the user can slide

Implementation: add a `compute_halo_acceleration(positions, M_halo, a_halo)` function in a new file [init_conditions.py](astr311-chris/app/src/gravity/init_conditions.py) or alongside forces, then sum it with particle-particle forces in the `accel_fn` closure in [demo_2d.py](astr311-chris/app/src/gravity/demo_2d.py) and [demo_3d.py](astr311-chris/app/src/gravity/demo_3d.py).

### 2. Fix initial velocities to account for enclosed mass

Currently in [init_conditions.py](astr311-chris/app/src/gravity/init_conditions.py) line 74:

```python
v_circ = np.sqrt(G * M_star / r)
```

This only uses the star mass. Should be:

```python
v_circ = np.sqrt(G * (M_star + M_halo_enclosed(r)) / r)
```

Where `M_halo_enclosed(r)` is the enclosed halo mass at radius `r` (for Hernquist: `M_halo * r^2 / (r + a)^2`). This ensures particles start on correct circular orbits for the total potential, not just the star.

### 3. Calibrate softening to particle spacing

Rule of thumb: `epsilon ~ mean_interparticle_spacing / 5`. For `N` particles in annulus `[r_min, r_max]`:

- Area = pi * (r_max^2 - r_min^2)
- Mean spacing ~ sqrt(Area / N)
- For N=3000, r_min=15, r_max=20: spacing ~ 0.43, so epsilon ~ 0.08 is fine

Current softening of 0.035 is reasonable for these parameters. No major change needed here, but we should document the relationship.

## Config and parameter changes

### 4. Extend [config.py](astr311-chris/app/src/config.py) with halo parameters

Add to `GravityConfig`:

```python
M_halo: float = 0.0        # dark matter halo mass (0 = no halo)
a_halo: float = 5.0         # halo scale radius (Hernquist)
```

### 5. Recommended "good defaults" presets

For spiral-galaxy-like runs with 1000-5000 particles:


| Parameter      | Value        | Rationale                                     |
| -------------- | ------------ | --------------------------------------------- |
| M_star         | 1.0          | Central bulge/SMBH                            |
| m_particle     | 1e-4 to 1e-5 | Disk mass << star mass (total disk ~ 0.1-0.5) |
| M_halo         | 5.0-20.0     | Dominant mass, provides flat rotation curve   |
| a_halo         | r_max * 0.5  | Scale radius ~ half the disk extent           |
| r_min          | 2.0          | Inner gap (avoids central singularity)        |
| r_max          | 15.0         | Outer disk edge                               |
| softening      | 0.05-0.1     | ~ spacing/5                                   |
| dt             | 0.01-0.02    | Small enough for orbit at r_min               |
| velocity_noise | 0.05         | Seeds spiral arm formation                    |


## Web UI changes

### 6. Add dark matter controls to the web viewer form

In the simulation form (visible in the screenshot), add:

- **M_halo** slider/input (0 to 50, default 10) labeled "Dark matter halo mass"
- **a_halo** input (default 5.0) labeled "Halo scale radius"
- A hint line showing the disk-to-halo mass ratio

### 7. Wire halo parameters through sim_server.py

In [sim_server.py](astr311-chris/app/tools/sim_server.py), add `M_halo` and `a_halo` to `_parse_run_params()` and `_build_run_cmd()`, then add corresponding CLI args to demo_2d.py and demo_3d.py.

### 8. Mass ratio slider

Replace the separate Star mass / Particle mass inputs in queue.html with a single **mass ratio slider** (range ~100 to 100000, log scale). The slider directly sets the star-to-particle mass ratio. As the user adjusts:

- `m_particle = M_star / ratio`
- Display the computed ratio and per-particle mass below the slider
- Keep M_star as an editable field (default 1.0); the slider controls the ratio

### 9. Visual mass-proportional sizing in viewer

In viewer.html, scale the Three.js sphere sizes so the star and particles visually reflect their mass ratio:

- Star sphere radius: fixed base (e.g. 0.15)
- Particle sphere radius: `starRadius * (m_particle / M_star)^(1/3)` (cube-root scaling = volume-proportional)
- When mass data is available in the replay JSON, read it; otherwise fall back to equal sizing
- This means at ratio 1000:1, star is ~10x the radius of particles; at 10000:1, ~21.5x

## Implementation files to modify

- **New function**: `compute_halo_acceleration()` -- add to [forces_cpu.py](astr311-chris/app/src/gravity/forces_cpu.py) and [forces_gpu.py](astr311-chris/app/src/gravity/forces_gpu.py)
- **Modify**: [init_conditions.py](astr311-chris/app/src/gravity/init_conditions.py) -- accept `M_halo`, `a_halo` and fix `v_circ`
- **Modify**: [demo_2d.py](astr311-chris/app/src/gravity/demo_2d.py), [demo_3d.py](astr311-chris/app/src/gravity/demo_3d.py) -- add CLI args and compose `accel_fn` with halo
- **Modify**: [config.py](astr311-chris/app/src/config.py) -- add halo fields
- **Modify**: [sim_server.py](astr311-chris/app/tools/sim_server.py) -- parse and forward halo params
- **Modify**: Web viewer HTML -- add halo inputs to the form

