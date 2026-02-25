# Physics Notes — Gravitational Simulation of Solar System Formation

## Model

- **Newtonian gravity** between point masses.
- **Central star:** one particle (index 0) with mass M_star at the origin; all other particles are “test” particles or additional masses.
- **Gravitational softening:** we use a softened distance so forces do not diverge at small separations.

## Force law

Acceleration on particle i due to all others:

**a_i = G Σ_{j≠i} m_j (r_j − r_i) / (|r_j − r_i|² + ε²)^(3/2)**

- G: gravitational constant (e.g. 1 in code units).
- ε: softening length (e.g. 0.05); prevents singularities when particles get very close.
- In 2D, r and v are (x, y); the formula is the same with 2-vectors.

## Circular orbits

For a particle of negligible mass at distance r from a central mass M, the circular orbital speed is:

**v_circ = sqrt(G M / r)**

Tangential velocity is set from this in disk initial conditions (with small random perturbations). In 2D, angular momentum per unit mass is L_z = x v_y − y v_x (out of the plane).

## Integration

- **Leapfrog (kick-drift-kick)** is used for stability and approximate energy conservation:
  - Half-kick: v → v + (dt/2) a
  - Drift: r → r + dt v
  - Half-kick: v → v + (dt/2) a_new
- **Euler** is available for quick tests but is not suitable for long runs.
- Timestep dt must be small enough that orbits remain stable (e.g. fraction of the shortest dynamical time).

## Conservation (ideal case)

- **Total energy** E = K + U should be approximately constant (Leapfrog preserves it well in practice).
  - Kinetic: K = (1/2) Σ m_i v_i²  
  - Potential: U = −G Σ_{i<j} m_i m_j / r_ij (with softened r_ij).
- **Total angular momentum** L = Σ m_i (r_i × v_i) is exactly conserved by Newtonian gravity (in 2D, only the z-component is non-zero). We track it to validate the integrator and initial conditions.

## Initial conditions

- **Disk:** Particles in an annulus [r_min, r_max] with tangential velocity ≈ v_circ(r); small random perturbations to positions and velocities.
- **Cloud:** Particles randomly distributed inside a radius r_max; velocities set with a configurable fraction of circular to give partial angular momentum.

Both include the central star as particle 0 (mass M_star, at origin, zero velocity).

## What we do not include

- Gas dynamics, magnetic fields, radiation.
- Relativistic effects.
- Collisions or fragmentation.

We explicitly discuss these simplifications and how they differ from real planetary formation.
