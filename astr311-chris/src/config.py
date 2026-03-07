"""Configuration and shared constants for the gravity simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GravityConfig:
    """Configuration for the gravity simulation (Phase 1: 2D; Phase 2: 3D)."""

    dim: int = 2  # 2D for Phase 1, extend to 3D later
    n_particles: int = 1000
    time_step: float = 0.01
    softening_length: float = 0.05
    M_star: float = 1.0
    r_min: float = 0.5
    r_max: float = 2.0
    ic_type: str = "disk"  # "disk" or "cloud"


@dataclass
class AppConfig:
    """Top-level configuration wrapper."""

    gravity: GravityConfig = GravityConfig()
