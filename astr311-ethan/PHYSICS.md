# Physics & Mathematics Documentation

## Overview
This document explains the mathematical formulations and physical principles underlying the N-body gravity simulator.

---

## 1. Newtonian Gravitation

### Gravitational Force
The gravitational force between two point masses follows Newton's law of universal gravitation:

$$
F = G \frac{m_1 m_2}{r^2}
$$

Where:
- $F$ = magnitude of gravitational force (N)
- $G$ = gravitational constant ($6.67430 \times 10^{-11}\ \text{m}^3\ \text{kg}^{-1}\ \text{s}^{-2}$)
- $m_1, m_2$ = masses of the two bodies (kg)
- $r$ = distance between their centers (m)

### Vector Form
In 2D, the gravitational acceleration of body `i` due to body `j` is:

$$
a_{ij} = G m_j \frac{\vec{r}_j - \vec{r}_i}{|\vec{r}_j - \vec{r}_i|^3}
$$

Where:
- $\vec{r}_i, \vec{r}_j$ = position vectors [x, y]
- $|\vec{r}|$ = Euclidean norm (distance)
- The direction is along $(\vec{r}_j - \vec{r}_i)$ (toward body j)

### Total Acceleration
For an N-body system, the total acceleration on body `i` is the superposition of all pairwise forces:

$$
a_i = \sum_{j \neq i} G m_j \frac{\vec{r}_j - \vec{r}_i}{|\vec{r}_j - \vec{r}_i|^3}
$$

**Implementation** (`gravitational_acceleration()` in `sim.py`):
```python
def gravitational_acceleration(body, bodies, G, softening=0.0):
    acceleration = np.zeros(2)
    for other in bodies:
        if other is not body:
            r_vector = other.position - body.position
            r2 = np.dot(r_vector, r_vector) + softening * softening
            r = np.sqrt(r2)
            if r > 1e-10:
                acceleration += G * other.mass / (r2 * r) * r_vector
    return acceleration
```

---

## 2. Gravitational Softening

### The Singularity Problem
In pure Newtonian gravity, acceleration diverges as $r \to 0$:

$$
a \sim \frac{1}{r^2} \to \infty \text{ as } r \to 0
$$

Numerical integrators cannot handle this singularity. Close encounters cause:
- Catastrophic loss of precision
- Unphysical velocities/ejections
- Energy non-conservation

### Plummer Softening
We use **Plummer softening**, which modifies the force law near r=0:

$$
a = G m \frac{r}{(r^2 + \varepsilon^2)^{3/2}}
$$

Where $\varepsilon$ is the **softening length**. Behavior:
- **r >> ε**: recovers Newtonian $a \approx Gm/r^2$
- **r << ε**: force is linear $a \approx Gm r/\varepsilon^3$ (harmonic oscillator-like)
- **r = 0**: acceleration is zero (no singularity)

**Physical Interpretation**: Bodies act as if they have finite radius ≈ ε, not point masses.

**Three-Body Parameters**:
- Softening length: $\varepsilon = 0.05$
- Typical separations: $r \sim 1$–$3$
- Softening is "felt" only during closest approaches ($r < 0.15$)

---

## 3. Velocity Verlet Integration

### Why Verlet?
The **Velocity Verlet** algorithm is:
- **Symplectic**: preserves phase-space volume → better long-term energy conservation
- **Time-reversible**: forward then backward integration returns to start
- **Second-order accurate**: global error $\sim \mathcal{O}(\Delta t^2)$
- **Explicit**: no matrix inversions needed

### Algorithm
For each timestep dt:

1. **Position update** (half-step using old velocity and acceleration):
$$
r(t + \Delta t) = r(t) + v(t)\,\Delta t + \tfrac{1}{2}\,a(t)\,\Delta t^2
$$

2. **Compute new accelerations** at updated positions:
$$
a(t + \Delta t) = \text{compute\_acceleration}\bigl(r(t + \Delta t)\bigr)
$$

3. **Velocity update** (half-step using average acceleration):
$$
v(t + \Delta t) = v(t) + \tfrac{1}{2}\bigl(a(t) + a(t + \Delta t)\bigr)\,\Delta t
$$

### Truncation Error
Local error per step: $\mathcal{O}(\Delta t^3)$
Global error after time T: $\mathcal{O}(\Delta t^2)$

For three-body: $\Delta t = 0.0005$, $T = 60$ → ~120,000 steps needed

**Implementation** (`simulate()` in `sim.py`):
```python
for step in range(steps):
    # Save state
    if step % record_every == 0:
        history.append(current_state)
    
    # Position update
    for i, body in enumerate(bodies):
        body.position += body.velocity * dt + 0.5 * accelerations[i] * dt**2
    
    # Recompute accelerations
    new_accelerations = [gravitational_acceleration(body, bodies, G, softening) 
                         for body in bodies]
    
    # Velocity update
    for i, body in enumerate(bodies):
        body.velocity += 0.5 * (accelerations[i] + new_accelerations[i]) * dt
    
    accelerations = new_accelerations
```

---

## 4. The Three-Body Problem

### Why Chaotic?
The gravitational three-body problem is **chaotic**:
- **No closed-form solution** (Poincaré, 1890s)
- **Sensitive dependence on initial conditions**: tiny changes → wildly different outcomes
- **Non-integrable**: no conserved quantities beyond E, L, P

### Pythagorean Configuration
Our default setup uses the famous **Pythagorean three-body problem** (Burrau, 1913):

**Initial Conditions**:
- Masses: [3, 4, 5]
- Positions: vertices of a 3-4-5 right triangle
  - Body 1 (m=3): [1, 3]
  - Body 2 (m=4): [-2, -1]
  - Body 3 (m=5): [1, -1]
- Velocities: all zero [0, 0]

**Why this configuration?**
- Simple integer masses and rational positions
- Bodies start at rest → pure gravitational dynamics
- Produces complex chaotic motion without fine-tuning
- System remains bound for ~60 time units before one body escapes

### Center of Mass Adjustment
All initial conditions are adjusted to satisfy:

**Center of Mass at Origin**:
$$
\vec{R}_{\text{cm}} = \frac{\sum m_i \vec{r}_i}{\sum m_i} = \mathbf{0}
$$

**Zero Total Momentum**:
$$
\vec{P}_{\text{tot}} = \sum m_i \vec{v}_i = \mathbf{0}
$$

This ensures:
- No "drift" of the entire system
- Camera can stay centered on COM
- Conservation laws are cleaner

**Implementation** (in `create_three_body_problem()`):
```python
total_mass = sum(masses)
com_pos = sum(masses[i] * positions[i]) / total_mass
com_vel = sum(masses[i] * velocities[i]) / total_mass

positions = [pos - com_pos for pos in positions]
velocities = [vel - com_vel for vel in velocities]
```

### Dimensionless Units
For three-body, we use **G = 1** (dimensionless units):
- Lengths measured in "natural units" (triangle edge ~ 1)
- Time measured in units of $\sqrt{L^3/(GM)}$
- Easier to compare configurations without worrying about physical scales

---

## 5. The Pluto System

### Physical System
Pluto and its 5 moons:
1. **Pluto**: $1.303 \times 10^{22}$ kg (primary)
2. **Charon**: $1.586 \times 10^{21}$ kg (~12% of Pluto's mass — a "binary dwarf planet")
3. **Nix**: $4.5 \times 10^{16}$ kg
4. **Styx**: $7.5 \times 10^{15}$ kg
5. **Kerberos**: $1.65 \times 10^{16}$ kg
6. **Hydra**: $4.8 \times 10^{16}$ kg

All small moons orbit the **Pluto-Charon barycenter**, not Pluto itself.

### Circular Orbit Approximation
Each body is initialized on a circular orbit around the system barycenter:

**Orbital velocity for circular orbit**:
$$
v = \sqrt{\frac{G M_{\text{total}}}{r}}
$$

Where:
- `M_total` = Pluto mass + Charon mass (small moons negligible)
- `r` = semi-major axis (distance from barycenter)

**Pluto-Charon setup** ($d_{pc} = 19{,}571\text{ km}$, separation between Pluto and Charon):
$$
r_{\text{pluto}} = \frac{M_{\text{charon}}}{M_{\text{total}}}\,d_{pc}, \qquad
r_{\text{charon}} = \frac{M_{\text{pluto}}}{M_{\text{total}}}\,d_{pc}
$$
$$
v_{\text{pluto}} = \frac{M_{\text{charon}}}{M_{\text{total}}} \sqrt{\frac{G M_{\text{total}}}{d_{pc}}}, \qquad
v_{\text{charon}} = \frac{M_{\text{pluto}}}{M_{\text{total}}} \sqrt{\frac{G M_{\text{total}}}{d_{pc}}}
$$

Bodies are placed perpendicular to velocity for circular motion.

### Why SI Units?
Pluto system uses $G = 6.67430 \times 10^{-11}\ \text{m}^3\ \text{kg}^{-1}\ \text{s}^{-2}$ (SI units):
- Real physical masses in kg
- Real distances in meters
- Real time in seconds
- Output time converted to days for user display

---

## 6. Barycenter (Center of Mass)

### Definition
The barycenter is the mass-weighted center of the system:

$$
\vec{R}_{\text{cm}} = \frac{\sum m_i \vec{r}_i}{\sum m_i}
$$

In 2D:
$$
x_{\text{cm}} = \frac{\sum m_i x_i}{M_{\text{total}}}, \qquad y_{\text{cm}} = \frac{\sum m_i y_i}{M_{\text{total}}}
$$

### Properties
- In an isolated system (no external forces), the barycenter moves at constant velocity
- Since we initialize with P_total = 0, the barycenter is **stationary**
- Camera focuses on barycenter → system stays centered in view

### COM Marker in UI
The yellow crosshair shows the instantaneous COM position. In principle, it should never move (since P_total=0), but numerical errors cause slight drift over long integrations.

**Implementation** (`getBarycenter()` in `index.html`):
```javascript
function getBarycenter(state) {
    let tm = 0, cx = 0, cy = 0;
    for (const b of state.bodies) {
        tm += b.mass;
        cx += b.position[0] * b.mass;
        cy += b.position[1] * b.mass;
    }
    return [cx/tm, cy/tm];
}
```

---

## 7. Coordinate Transformations

### World to Screen
The frontend converts physical coordinates (world space) to pixel coordinates (screen space):

$$
\text{screen}_x = (\text{world}_x - \text{focus}_x) \cdot \text{scale} + \frac{\text{canvas\_width}}{2}
$$
$$
\text{screen}_y = (\text{world}_y - \text{focus}_y) \cdot \text{scale} + \frac{\text{canvas\_height}}{2}
$$

Where:
- `focus` = camera focus position (usually barycenter)
- `scale` = pixels per world unit

### Automatic Scaling
Scale is chosen to fit all visible bodies on screen:

$$
\text{max\_distance} = \max_i |\vec{r}_i - \text{focus}|
$$
$$
\text{scale} = \frac{0.4 \cdot \min(\text{canvas\_width},\, \text{canvas\_height})}{\text{max\_distance}}
$$

For three-body, scale is computed **once** across all history frames and cached to prevent zoom jitter during playback.

---

## 8. Conservation Laws (In Theory)

### Energy Conservation
Total energy should be conserved:
$$
E = T + U = \frac{1}{2}\sum_i m_i |\vec{v}_i|^2 - \sum_{i<j} \frac{G m_i m_j}{|\vec{r}_i - \vec{r}_j|}
$$

In practice:
- Verlet integrator has small energy drift
- Softening slightly violates energy conservation near $r \sim \varepsilon$
- Typical drift: $\Delta E/E \sim 10^{-4}$ to $10^{-6}$ over $t = 60$

### Momentum Conservation
Total momentum should be conserved:
$$
\vec{P} = \sum m_i \vec{v}_i = \text{constant} = \mathbf{0}
$$

Verlet preserves momentum better than energy (symplectic property).

### Angular Momentum Conservation
Total angular momentum about the origin:
$$
L = \sum_i m_i (\vec{r}_i \times \vec{v}_i)
$$

In 2D (scalar): $L = \sum_i m_i (x_i v_{y,i} - y_i v_{x,i})$

Only conserved if the system is rotationally symmetric (not true for typical three-body configs).

---

## 9. Numerical Stability

### Timestep Selection
The timestep must be small enough to resolve orbital motion:

**Three-body**:
- Typical orbital period: $T \sim 2\pi\sqrt{r^3/(GM)} \sim 5$–$10$
- Timestep: $\Delta t = 0.0005$ → 10,000–20,000 steps per orbit
- Rule of thumb: $\Delta t < T/100$

**Pluto system**:
- Charon orbital period: ~6.4 days = 550,000 seconds
- Timestep: $\Delta t = 1000\ \text{s}$ → 550 steps per orbit
- Adequate since orbits are nearly circular (no close encounters)

### Softening Tradeoff
- **Too small** ($\varepsilon \to 0$): recovers $r^{-2}$ singularity, integration fails
- **Too large** ($\varepsilon \gg r$): bodies don't feel gravity until far apart, unrealistic
- **Optimal**: $\varepsilon \sim 0.05$–$0.1$ for three-body with typical separations $r \sim 1$

---

## 10. Orbital Mechanics Concepts

### Kepler's Third Law
For circular orbits around a central mass M:
$$
T^2 = \frac{4\pi^2}{GM}\,r^3
$$

Applied in Pluto system to initialize circular orbits.

### Vis-Viva Equation
For elliptical orbits:
$$
v^2 = GM\left(\frac{2}{r} - \frac{1}{a}\right)
$$

Where:
- `a` = semi-major axis
- At periapsis/apoapsis, this determines orbital speed

Not directly used in code (full N-body, not Keplerian approximation), but governs the underlying dynamics.

### Escape Velocity
A body escapes if its kinetic energy exceeds potential energy:
$$
v_{\text{escape}} = \sqrt{\frac{2GM}{r}}
$$

In three-body, after t~55-60, one body sometimes reaches escape velocity and leaves.

---

## 11. Chaos Theory Concepts

### Lyapunov Exponent
In chaotic systems, nearby trajectories diverge exponentially:
$$
\delta r(t) \sim \delta r(0)\,e^{\lambda t}
$$

Where $\lambda$ is the Lyapunov exponent. For three-body, $\lambda > 0$ (positive → chaos).

### Poincaré Recurrence
Despite chaos, bounded systems *eventually* return arbitrarily close to initial state (recurrence theorem). Recurrence time is astronomically long for three-body.

### Sensitive Dependence
Changing initial position by $10^{-6}$ can lead to completely different outcomes after $t \sim 20$–$30$. This is why "randomize" button produces unique orbits each time.

---

## 12. Computational Complexity

### Per-Step Cost
- Computing accelerations: $\mathcal{O}(N^2)$ for $N$ bodies (all pairwise interactions)
- Verlet updates: $\mathcal{O}(N)$ (linear in number of bodies)
- **Total**: $\mathcal{O}(N^2)$ per timestep

For N=3 (three-body): 3 pairwise forces → minimal cost
For N=6 (Pluto system): 15 pairwise forces → still negligible

### Timestep Scaling
Total computational cost:
$$
\text{Cost} = \text{steps} \times N^2 = \frac{T}{\Delta t}\,N^2
$$

For three-body:
- T = 60, dt = 0.0005 → 120,000 physics steps
- With record_every=20 → 6,000 frames sent to browser
- Computation time: ~2-3 seconds on modern CPU

---

## 13. Mathematical Formulas Summary

| Quantity | Formula |
|----------|---------|
| Gravitational Force | $\vec{F} = -G m_1 m_2 \hat{r} / r^2$ |
| Acceleration | $a_i = \sum_j G m_j (\vec{r}_j - \vec{r}_i) / |\vec{r}_j - \vec{r}_i|^3$ |
| Softened Acceleration | $a_i = \sum_j G m_j (\vec{r}_j - \vec{r}_i) / (r^2 + \varepsilon^2)^{3/2}$ |
| Verlet Position | $\vec{r}(t+\Delta t) = \vec{r}(t) + \vec{v}(t)\Delta t + \tfrac{1}{2}\vec{a}(t)\Delta t^2$ |
| Verlet Velocity | $\vec{v}(t+\Delta t) = \vec{v}(t) + \tfrac{1}{2}(\vec{a}(t) + \vec{a}(t+\Delta t))\Delta t$ |
| Center of Mass | $\vec{R}_{\text{cm}} = \sum m_i \vec{r}_i / \sum m_i$ |
| Kinetic Energy | $T = \tfrac{1}{2} \sum m_i |\vec{v}_i|^2$ |
| Potential Energy | $U = -\sum_{i<j} G m_i m_j / |\vec{r}_i - \vec{r}_j|$ |
| Circular Orbit Speed | $v = \sqrt{GM/r}$ |
| Escape Velocity | $v_{\text{esc}} = \sqrt{2GM/r}$ |

---

## 14. References

### Classical Mechanics
- Goldstein, H. (2002). *Classical Mechanics* (3rd ed.)
- Newton, I. (1687). *Philosophiæ Naturalis Principia Mathematica*

### N-Body Problem
- Burrau, C. (1913). "Numerische Berechnung eines Spezialfalles des Dreikörperproblems" (Pythagorean problem)
- Poincaré, H. (1890s). "Sur le problème des trois corps" (proof of non-integrability)

### Numerical Methods
- Hairer, E., Lubich, C., & Wanner, G. (2006). *Geometric Numerical Integration*
- Leimkuhler, B., & Reich, S. (2004). *Simulating Hamiltonian Dynamics*

### Pluto System
- NASA New Horizons mission data (2015)
- Showalter, M. R., & Hamilton, D. P. (2015). "Resonant interactions and chaotic rotation of Pluto's small moons"

---

## Appendix: Units Table

### Three-Body Problem (Dimensionless)
| Quantity | Unit | Typical Value |
|----------|------|---------------|
| Mass | dimensionless | 1-10 |
| Length | dimensionless | 0.1-10 |
| Time | dimensionless | 0-100 |
| Velocity | length/time | 0.01-1 |
| G | 1 | 1.0 |

### Pluto System (SI)
| Quantity | Unit | Typical Value |
|----------|------|---------------|
| Mass | kg | $10^{15}$–$10^{22}$ |
| Length | m | $10^7$–$10^8$ |
| Time | s | $0$–$10^9$ |
| Velocity | m/s | $10^2$–$10^3$ |
| G | $\text{m}^3\ \text{kg}^{-1}\ \text{s}^{-2}$ | $6.67430 \times 10^{-11}$ |
