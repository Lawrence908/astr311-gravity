"""Numerical helper functions for Path B (collider scaling laws)."""

from __future__ import annotations

from .models import RingCollider


def estimate_energy_for_radius(radius_km: float) -> float:
    """Placeholder mapping from radius to energy.

    The actual formula will be a simple scaling law chosen for clarity,
    not realism. For now, this returns 0.0 so the code compiles.
    """
    _ = radius_km
    return 0.0


def describe_collider(collider: RingCollider) -> str:
    """Return a short human-readable description string."""
    return (
        f"Ring collider: radius={collider.radius_km:.1f} km, "
        f"beam energy={collider.beam_energy_TeV:.1f} TeV (toy model)"
    )

