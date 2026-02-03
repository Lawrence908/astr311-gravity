## `README.md`

```markdown
# Cosmic Origins
Visual simulations of how fundamental physical laws give rise to structure in the universe.

## What this project is
Cosmic Origins is a computational visualization project focused on making abstract physics
concepts intuitive and visible. Using simplified simulations, we explore how matter evolves
from early-universe conditions into observable structure.

The project supports two aligned exploration paths:
1. **Cosmic scale** — how gravity forms the first galaxies
2. **Particle scale** — how colliders probe early-universe physics

Only one path is required; the second may be used as an extension or fallback.

## Why this fits the course
The course explains *what* we observe (galaxies, dark matter, particles) but does not deeply
cover *how* these processes can be modeled or explored computationally. This project fills
that gap using visualization and simulation to reinforce course concepts.

## Project paths

### Path A — Early Galaxy Formation (Primary)
A visual simulation showing how tiny density fluctuations grow into clumps under gravity,
demonstrating the origin of proto-galaxies.

### Path B — Particle Physics & Colliders (Alternate)
A visualization-driven model of particle accelerators (inspired by the LHC), exploring how
collider size relates to achievable energy and what that means for probing early-universe
conditions.

## Deliverables
- A live or recorded simulation demo
- Visual outputs (plots, animations, or Unity scenes)
- Short written explanation connecting the simulation to course material
- Final presentation

## Team structure (3 people)
- Physics & concepts
- Simulation & computation
- Visualization & presentation

## Project names
- Cosmic Origins (primary)
- ProtoVerse
- Galactic Dawn
- Genesis Cluster
- Big Bang Origins
- CosmoForge
```

---

## `docs/PROJECT_SCOPE.md`

```markdown
# Project Scope

## Core goal
Create an educational simulation that visually demonstrates how fundamental physics
processes operate at scales that cannot be directly observed.

## Supported project paths

### Path A — Cosmic Structure Formation
We simulate collisionless particles interacting through gravity to demonstrate how
early-universe density perturbations evolve into clustered structures.

Included:
- Gravitational interaction
- Simple initial perturbations
- Visual clustering over time

Excluded:
- Hydrodynamics
- Star formation
- Relativistic effects

### Path B — Particle Colliders
We simulate conceptual particle acceleration and collisions to illustrate how collider
size affects energy and discovery potential.

Included:
- Particle acceleration paths
- Energy scaling with radius
- Collision probability visualization

Excluded:
- Full quantum field theory
- Exact Standard Model predictions

## Constraints
- Educational accuracy over experimental precision
- Visual clarity over physical completeness
- Stable, demonstrable output over maximum realism

## Definition of success
- Simulation runs reliably
- Concepts are visually understandable
- Clear connection to course topics is demonstrated
```

---

## `docs/MILESTONES.md`

```markdown
# Project Milestones

## Week 1 — Foundations
- Finalize which path to pursue (A or B)
- Set up repository and environment
- Basic visualization prototype

## Week 2 — Physics Model
Path A:
- Implement gravitational interaction
- Test small particle counts

Path B:
- Implement particle motion and acceleration
- Visualize energy scaling

## Week 3–4 — Simulation & Visualization
- Improve stability and visuals
- Add parameter controls (particle count, scale, energy)
- Begin capturing output for presentation

## Week 5 — Analysis & Interpretation
- Connect simulation behavior to course concepts
- Prepare explanatory diagrams

## Week 6–7 — Finalization
- Polish visuals
- Write final explanation
- Prepare presentation demo
```

---

## `docs/PHYSICS_NOTES.md`

```markdown
# Physics Notes (Simplified Models)

## Path A — Gravity & Structure Formation

We model matter as particles interacting through Newtonian gravity.

Acceleration:
a_i = G * Σ m_j (r_j - r_i) / (|r_j - r_i|^2 + ε^2)^(3/2)

- ε (softening) prevents singularities
- Units are normalized for visualization
- Focus is on pattern formation, not exact prediction

## Path B — Particle Colliders

We model particles as classical objects accelerated along a circular path.

Key ideas:
- Larger collider radius → higher achievable energy
- Energy determines what particle interactions become possible
- Colliders probe conditions similar to the early universe

We emphasize **scaling behavior**, not exact quantum outcomes.
```

---

## `docs/ARCHITECTURE.md`

```markdown
# Project Architecture

src/
  main.py              # Entry point
  config.py            # Global parameters

  cosmic/
    init_conditions.py
    gravity.py
    integrator.py
    visualize.py

  collider/
    accelerator.py
    collision_model.py
    visualize.py

viz/
  plots/
  animations/

docs/
outputs/

## Notes
- Only one of cosmic/ or collider/ must be implemented
- Shared visualization tools are encouraged
- Code is a means to explanation, not the final goal
```

---

## `docs/PROPOSAL_ONE_PAGER.md` (Instructor-facing)

```markdown
# Cosmic Origins — Project Proposal

We propose creating a visual simulation to explore how fundamental physical laws shape the
universe at scales that cannot be directly observed.

Our project will focus on either:
1. The formation of early galaxies from small density fluctuations, or
2. The role of particle colliders in probing early-universe physics.

Using simplified computational models, we aim to make these abstract processes visually
intuitive and easier to understand. The project emphasizes conceptual clarity, not
experimental precision, and directly supports topics covered in the course.

The final result will be a demonstrable simulation and presentation illustrating how matter
organizes itself from the smallest to the largest scales.