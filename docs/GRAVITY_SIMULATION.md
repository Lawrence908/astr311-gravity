Below are **copy-paste starter Markdown docs** + a **simple Python project skeleton** aimed at a **GPU-accelerated gravity simulation** that visually demonstrates **early structure / proto-galaxy formation** (the “density perturbations → clumping” idea tied to CMB fluctuations and later galaxy formation in your course).

---

## `README.md`

````markdown
# Cosmic Origins
GPU-accelerated gravitational clustering demo (early structure → proto-galaxies).

## What we’re building
A visual simulation showing how tiny density perturbations can grow into clumps under gravity.
Goal: a clear, watchable demo + a short explanation that connects to course concepts:
- early density perturbations (CMB fluctuations) → future galaxies
- dark matter’s gravitational role in structure formation
- why “more mass than meets the eye” matters for galaxy evolution

## Why this fits the course
The course covers the Big Bang timeline and formation of galaxies, but does not go deep into
how structure actually forms dynamically. We fill that gap with a computable, visual model.
(See: formation of galaxies after dark ages; CMB fluctuations as precursors; dark matter halos.)

## Deliverables (end of term)
1. Live demo (GPU optional but targeted) that runs a simulation and shows clumping over time.
2. Short writeup: assumptions, equations, limitations, what it teaches.
3. Slides: visuals (snapshots / animation) + interpretation.

## Quick start
### 1) Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

### 2) Run

```bash
python -m src.run_sim --steps 2000 --n 20000 --backend auto
```

### 3) Visualize

* Either live window (matplotlib) or export frames to `outputs/frames/` and stitch into a video.

## Tech choices (simple first, then better)

Phase 1 (fastest): GPU brute-force O(N^2) with softening + small N

* Numba CUDA or CuPy backend for force computation

Phase 2 (scaling): Barnes–Hut tree (O(N log N)) or particle-mesh

* optional if time permits

## Team roles (3 people)

* Physics/Math Lead: equations, integrator, initial conditions
* GPU/Performance Lead: CUDA/Numba kernels, profiling
* Visualization/Story Lead: rendering, outputs, narration, slides

## Project name candidates

* Cosmic Origins (primary)
* Primeval Verse
* Genesis Cluster
* ProtoVerse
* Galactic Dawn
* CosmoForge

````

> Course tie-ins referenced above: “CMB fluctuations as precursors of galaxies” + “formation of galaxies ~1 billion years” + dark matter’s gravitational effect and halo idea. 

---

## `docs/PROJECT_SCOPE.md`

```markdown
# Project Scope: Cosmic Origins

## Objective
Create a visually compelling simulation that demonstrates gravitational clustering from
early-universe-like initial conditions (tiny density perturbations).

## Model (what we simulate)
- Collisionless particles interacting via Newtonian gravity
- Use "softening" to avoid infinite forces at tiny separations
- Periodic boundary conditions (box) OR reflective boundaries (simpler)

## What we are NOT simulating (explicitly)
- Hydrodynamics / gas pressure / star formation
- Relativistic effects
- Feedback processes (supernovae/AGN)

## Why it still teaches the right idea
Even a dark-matter-only N-body toy model captures the core intuition:
gravity amplifies small density fluctuations into structure (clumps/halos), which later host galaxies.

## Success criteria
Minimum Viable Demo (MVD):
- Runs reliably on one machine
- Shows visible clumping from near-uniform initial state
- Exports frames + produces at least one nice animation

Stretch goals
- Compare CPU vs GPU timing
- Add simple “expanding box” / scale factor (cosmology-flavored)
- Add a Barnes–Hut mode for larger N
````

---

## `docs/MILESTONES.md`

```markdown
# Milestones (2–3 month plan)

## Week 1: Foundations
- Repo + environment + CLI skeleton
- CPU reference implementation (small N) + basic visualization
- Validate physics: stable time step, energy roughly conserved (within reason)

## Week 2–3: GPU MVP
- Implement GPU force kernel (Numba CUDA or CuPy)
- Confirm results match CPU at small N (sanity check)
- Basic performance notes: N vs runtime

## Week 4–5: Better “early universe” initial conditions
- Add density perturbation generator:
  - uniform random + small gaussian noise
  - optional: clustered seeds
- Tune softening + timestep for good visuals

## Week 6: Presentation assets
- Export frames, generate animation
- Capture graphs: runtime scaling, clump count vs time

## Week 7–8: Polish + writeup
- Clear limitations + what this demonstrates
- Final demo script: one command to run + render
```

---

## `docs/PHYSICS_NOTES.md`

```markdown
# Physics Notes (toy N-body)

## State
For each particle i:
- position r_i (3D)
- velocity v_i (3D)
- mass m_i

## Gravitational acceleration (softened)
a_i = G * Σ_{j≠i} m_j * (r_j - r_i) / (|r_j - r_i|^2 + eps^2)^(3/2)

- eps is the softening length (prevents singularities)
- G can be set to 1 in code units (we’re demonstrating patterns, not calibrating units)

## Integration (recommend leapfrog / velocity Verlet)
- More stable than Euler for orbital/gravity systems

## Boundaries
Pick one:
- Periodic box (good for “infinite-ish” universe feel)
- Reflective box (simpler)

## What to report
- show snapshots of particle density over time
- explain “small perturbations → clumps”
```

---

## `docs/ARCHITECTURE.md`

```markdown
# Architecture

src/
  run_sim.py            # CLI entry: parse args, run loop, call renderer
  sim/
    state.py            # ParticleState dataclass: positions, velocities, masses
    init_conditions.py  # perturbations, seeded halos, etc.
    integrators.py      # leapfrog / verlet
    forces_cpu.py       # CPU reference
    forces_gpu.py       # GPU backends (numba/cupy)
  viz/
    render_live.py       # live scatter
    render_frames.py     # save frames
  utils/
    config.py           # defaults
    profiling.py        # timing helpers

outputs/
  frames/
  runs/
docs/
```

---

## Minimal Python skeleton (files to create)

### `requirements.txt`

```txt
numpy
matplotlib
numba
cupy-cuda12x; platform_system != "Darwin"
```

*(If CuPy install is annoying on your server, keep it optional and run Numba CUDA first.)*

---

### `src/run_sim.py`

```python
import argparse
from sim.init_conditions import init_particles
from sim.integrators import leapfrog_step
from sim.forces_cpu import accel_cpu
from sim.forces_gpu import accel_gpu_auto
from viz.render_live import LiveRenderer

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=20000)
    p.add_argument("--steps", type=int, default=2000)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--eps", type=float, default=0.05)
    p.add_argument("--backend", choices=["auto", "cpu", "gpu"], default="auto")
    return p.parse_args()

def main():
    args = parse_args()
    state = init_particles(n=args.n, seed=42)

    if args.backend == "cpu":
        accel_fn = lambda s: accel_cpu(s, eps=args.eps)
    elif args.backend == "gpu":
        accel_fn = lambda s: accel_gpu_auto(s, eps=args.eps)
    else:
        accel_fn = lambda s: accel_gpu_auto(s, eps=args.eps, fallback_cpu=True)

    renderer = LiveRenderer()
    for k in range(args.steps):
        state = leapfrog_step(state, dt=args.dt, accel_fn=accel_fn)
        if k % 5 == 0:
            renderer.update(state, step=k)

    renderer.close()

if __name__ == "__main__":
    main()
```

---

### `src/sim/state.py`

```python
from dataclasses import dataclass
import numpy as np

@dataclass
class ParticleState:
    pos: np.ndarray   # (N, 3)
    vel: np.ndarray   # (N, 3)
    mass: np.ndarray  # (N,)
```

---

### `src/sim/init_conditions.py`

```python
import numpy as np
from .state import ParticleState

def init_particles(n: int, seed: int = 0) -> ParticleState:
    rng = np.random.default_rng(seed)

    # "Early universe-ish": nearly uniform with small perturbations
    pos = rng.random((n, 3))  # unit cube
    pos += 0.01 * rng.normal(size=(n, 3))  # tiny density perturbations
    pos %= 1.0

    vel = np.zeros((n, 3), dtype=np.float64)
    mass = np.ones(n, dtype=np.float64) / n
    return ParticleState(pos=pos.astype(np.float64), vel=vel, mass=mass)
```

---

### `src/sim/integrators.py`

```python
import numpy as np
from .state import ParticleState

def leapfrog_step(state: ParticleState, dt: float, accel_fn):
    # Kick-drift-kick
    a0 = accel_fn(state)
    v_half = state.vel + 0.5 * dt * a0
    pos_new = (state.pos + dt * v_half) % 1.0  # periodic box

    tmp = ParticleState(pos=pos_new, vel=v_half, mass=state.mass)
    a1 = accel_fn(tmp)
    vel_new = v_half + 0.5 * dt * a1

    return ParticleState(pos=pos_new, vel=vel_new, mass=state.mass)
```

---

### `src/sim/forces_cpu.py` (simple, correct, slow)

```python
import numpy as np
from .state import ParticleState

def accel_cpu(state: ParticleState, eps: float = 0.05, G: float = 1.0) -> np.ndarray:
    pos = state.pos
    m = state.mass
    n = pos.shape[0]
    a = np.zeros_like(pos)

    for i in range(n):
        dx = pos - pos[i]
        # minimum-image convention for periodic box
        dx -= np.round(dx)
        r2 = (dx * dx).sum(axis=1) + eps * eps
        inv_r3 = 1.0 / (r2 * np.sqrt(r2))
        inv_r3[i] = 0.0
        a[i] = G * (m[:, None] * dx * inv_r3[:, None]).sum(axis=0)

    return a
```

---

### `src/sim/forces_gpu.py` (placeholder “auto” selector)

```python
def accel_gpu_auto(state, eps: float = 0.05, G: float = 1.0, fallback_cpu: bool = True):
    # Start simple: if CUDA isn't available, fallback to CPU.
    # Implement one backend first (Numba CUDA OR CuPy), then add the other if time.
    try:
        from .forces_gpu_numba import accel_gpu_numba
        return accel_gpu_numba(state, eps=eps, G=G)
    except Exception:
        if fallback_cpu:
            from .forces_cpu import accel_cpu
            return accel_cpu(state, eps=eps, G=G)
        raise
```

---

### `src/viz/render_live.py`

```python
import matplotlib.pyplot as plt

class LiveRenderer:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.scat = None
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_title("Cosmic Origins (2D view: x vs y)")
        plt.ion()
        plt.show()

    def update(self, state, step: int):
        x = state.pos[:, 0]
        y = state.pos[:, 1]
        if self.scat is None:
            self.scat = self.ax.scatter(x, y, s=1)
        else:
            self.scat.set_offsets(list(zip(x, y)))
        self.ax.set_xlabel(f"step={step}")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def close(self):
        plt.ioff()
        plt.show()
```

---

## Notes that keep this aligned to *your course* (and not overcomplicate it)

* Your lectures explicitly connect **CMB temperature fluctuations** to **future galaxies** and mention **formation of galaxies** after the dark ages. That’s exactly what your simulation visualizes—just as a toy model. 
* Your lectures also highlight that **dark matter is inferred from gravitational effects** and is a major mass component in galaxies—your “collisionless particles under gravity” model is basically a dark-matter-only demo.