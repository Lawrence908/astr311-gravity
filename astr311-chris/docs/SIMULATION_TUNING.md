# Simulation Tuning — Clumps and Long-Term Orbits

Notes on getting desirable behavior: initial clumping, orbits that persist, and avoiding everything spiraling into a tight cluster around the star.

## Softening: more or less attraction?

**Increasing gravitational softening (ε) makes particles *less* attracted to each other at very close distances.**

- The force uses a softened distance: \( r_{\mathrm{eff}}^2 = r^2 + \varepsilon^2 \), so the acceleration is bounded and never infinite.
- **Larger ε** → force is weaker when \( r \lesssim \varepsilon \). Close encounters are “smoothed out”; particles are less violently deflected or pulled into mergers.
- **Smaller ε** → force approaches pure Newtonian at close range; stronger attraction when particles get very close, which can cause numerical issues and rapid inspirals.

So: **more softening = less attraction at close range**. That can help clumps survive close passes and reduce the tendency for everything to merge into one central blob. Try ε in the 0.05–0.1 range; going too large will make the potential too soft and orbits less Keplerian.

## Starting further out: r_max and r_min

- **Max initial radius (r_max):** Larger values place the disk (or cloud) further from the star. With particles starting at larger r, they have more room to form clumps before strong central pull dominates, and orbital times are longer. **Try r_max = 4–6** (or more) instead of 2 for “start further out” runs.
- **Min initial radius (r_min), disk only:** Raising r_min keeps the *inner* edge of the annulus away from the star. That avoids placing many particles on initially tight orbits that quickly “crash past” the star and spiral in. Example: **r_min = 1.0, r_max = 5.0** for a wider, more distant annulus.

Together, larger r_max and (for disk) a higher r_min give particles more distance and time to clump and to maintain orbits before being dragged inward.

## Other knobs

- **Star mass (M_star) vs particle mass:** If the central star dominates (e.g. M_star = 1, m_particle small so total particle mass ≪ 1), the potential is more central; clumps behave more like test particles and can retain orbits longer. If particle mass is large, particle–particle gravity competes and can cause more merging and inspiral.
- **Time step (Δt):** Smaller dt improves energy conservation and stability during close encounters; use it if you see wild energy drift or ejections when clumps pass near the star.
- **Steps:** For “long-term” orbits, run long enough (e.g. 5000–20000 steps) so that you can see whether clumps persist or eventually merge into the core.
- **Initial conditions:** “Disk” with circular-ish velocities gives more ordered motion; “cloud” with partial angular momentum is more chaotic. For clumping and orbits, disk with modest velocity_noise is usually a good starting point.
- **Collisions:** With collisions on, merging is explicit; r_collide small (e.g. ~1× softening) keeps mergers gradual. With collisions off, overlapping particles just pass through; you still get clumping in position/velocity from gravity alone.

## Suggested starting point for “clumps + long-term orbits”

- **n:** 2000–5000  
- **r_max:** 4 or 5 (particles start further out)  
- **r_min:** 1.0 (disk only; inner edge away from star)  
- **ε (softening):** 0.05–0.08  
- **M_star:** 1.0, m_particle: auto (so star dominates)  
- **steps:** 5000+  
- **dt:** 0.01 (reduce to 0.005 if you see energy blow-ups)

Then adjust r_max, r_min, and softening based on whether clumps stay coherent and orbit longer or still spiral in too quickly.
