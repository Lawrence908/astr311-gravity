"""Export a replay .npz file to JSON for the web viewer. Run from repo root:

    python tools/export_replay_to_json.py outputs/runs/run.npz web-viewer/replay.json

Or: cd src && python -c "
from gravity.replay import load_replay
import json, sys
d = load_replay(sys.argv[1])
# Convert ndarrays to lists for JSON
out = {
  'positions': d['positions'].tolist(),
  'steps': d['steps'].tolist(),
  'masses': d['masses'].tolist(),
  'dt': d['dt'],
  'n_particles': d['n_particles'],
  'n_snapshots': d['n_snapshots'],
}
with open(sys.argv[2], 'w') as f:
    json.dump(out, f)
" path.npz out.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from repo root or from tools/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gravity.replay import load_replay


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python export_replay_to_json.py <input.npz> <output.json>")
        sys.exit(1)
    npz_path = Path(sys.argv[1])
    json_path = Path(sys.argv[2])

    data = load_replay(npz_path)
    out = {
        "positions": data["positions"].tolist(),
        "steps": data["steps"].tolist(),
        "masses": data["masses"].tolist(),
        "dt": data["dt"],
        "n_particles": int(data["n_particles"]),
        "n_snapshots": int(data["n_snapshots"]),
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(out, f)
    print(f"Exported {data['n_snapshots']} snapshots to {json_path}")


if __name__ == "__main__":
    main()
