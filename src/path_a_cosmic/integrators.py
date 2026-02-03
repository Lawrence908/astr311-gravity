"""Time integration methods for the Path A gravity demo."""

from __future__ import annotations

from .state import AccelerationFn, ParticleState


def euler_step(state: ParticleState, dt: float, accel_fn: AccelerationFn) -> ParticleState:
    """Very simple Euler integrator (for early testing only)."""
    acc = accel_fn(state)
    new_vel = state.velocities + dt * acc
    new_pos = state.positions + dt * new_vel
    return ParticleState(positions=new_pos, velocities=new_vel, masses=state.masses)

