# Architecture Overview

Source layout (flat `src/`):

- `src/main.py` – tiny CLI entry stub.
- `src/config.py` – shared configuration dataclasses.
- `src/common/` – logging and other simple utilities.
- `src/path_a_cosmic/` – early-universe gravity demo (Path A).
- `src/path_b_collider/` – collider models (Path B).

```mermaid
flowchart TD
  src[src]
  mainFile[main.py]
  cfg[config.py]
  common[common/]
  pathA[path_a_cosmic/]
  pathB[path_b_collider/]

  src --> mainFile
  src --> cfg
  src --> common
  src --> pathA
  src --> pathB

  pathA --> stateA[state.py]
  pathA --> forcesA[forces_cpu.py]
  pathA --> integA[integrators.py]
  pathA --> vizA[viz_*]

  pathB --> modelsB[models.py]
  pathB --> numericsB[numerics.py]
  pathB --> vizB[viz.py]
```

