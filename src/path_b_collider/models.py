"""Conceptual physics models for Path B (colliders)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RingCollider:
    """Toy representation of a circular collider.

    Units and exact scaling will be defined in `PHYSICS_NOTES.md`.
    """

    radius_km: float
    beam_energy_TeV: float

