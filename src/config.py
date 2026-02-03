"""Configuration and shared constants for Cosmic Origins."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PathAConfig:
    """Basic configuration for Path A (cosmic gravity demo)."""

    dim: int = 2  # start in 2D, extend to 3D
    n_particles: int = 500
    time_step: float = 0.01
    softening_length: float = 0.05


@dataclass
class PathBConfig:
    """Basic configuration for Path B (collider models)."""

    ring_radius_km: float = 27.0  # LHC-scale baseline (toy)
    beam_energy_TeV: float = 7.0  # toy value


@dataclass
class AppConfig:
    """Top-level configuration wrapper."""

    path_a: PathAConfig = PathAConfig()
    path_b: PathBConfig = PathBConfig()

