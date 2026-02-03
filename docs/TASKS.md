# Tasks (Sprint 1)

- **Repo / bootstrap**
  - [ ] Create `src/` layout and placeholders for Path A and Path B.
  - [ ] Add `requirements.txt`, `pyproject.toml`, `.gitignore`, and `LICENSE`.
  - [ ] Verify `cd src && python -m main` runs and prints the init message.

- **Path A – CPU reference (2D)**
  - [ ] Implement 2D `ParticleState` and a simple uniform-with-noise initializer.
  - [ ] Implement a clear O(N²) CPU gravity force function with softening.
  - [ ] Implement a basic integrator (Euler or leapfrog) and run a tiny test.

- **Visualization milestone (Path A)**
  - [ ] Implement a minimal live 2D scatter plot.
  - [ ] Implement a simple frame export function to `outputs/frames/`.

- **Validation & sanity checks**
  - [ ] Check time step stability (no immediate numerical blow-ups).
  - [ ] Run a few seeds and visually confirm clustering behavior is plausible.

- **GPU / performance stretch**
  - [ ] (Optional) Explore numba-based or similar acceleration after CPU is stable.

- **Path B – Week 1 research + minimal model**
  - [ ] Collect 1–2 references on collider radius vs energy scaling.
  - [ ] Define a simple `RingCollider` model and a toy radius→energy function.
  - [ ] Draft one basic visualization or text summary for Path B.

