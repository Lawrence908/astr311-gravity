# ASTR 311 – N-Body Gravity Simulation

Newtonian N-body gravity simulation for solar system formation, with 2D/3D demos, replay export, and a web-based 3D viewer.

## How to run

### Setup

```bash
cd astr311-ethan
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the web server (viewer + simulation queue)

```bash
python tools/sim_server.py
```

Open http://localhost:8000 in browser. From there:
- **Queue & logs** – submit simulation jobs (2D/3D, disk/cloud, configurable particles, timesteps, etc.)
- **Open viewer** – interactive Three.js 3D replay viewer with trails, camera presets, playback controls

### Run 2D demo (CLI)

```bash
cd src
python -m gravity.demo_2d --n 1000 --steps 2000
```

### Run 3D demo (CLI)

```bash
cd src
python -m gravity.demo_3d --n 200 --steps 500
```

### Export replay for web viewer

```bash
cd src
python -m gravity.demo_2d --n 1000 --steps 2000 --save-replay ../web-viewer/replays/demo.npz --no-viz
cd ..
python tools/export_replay_to_json.py web-viewer/replays/demo.npz web-viewer/replays/demo.json
```

Then load the replay in the viewer at http://localhost:8000/viewer.html

## Legacy backend/frontend

The original FastAPI backend and frontend are preserved in `backend/` and `frontend/` for reference.
