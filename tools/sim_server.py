"""Simulation API server: serves web-viewer and runs gravity demos from the browser.

Run from repo root:

    .venv/bin/python tools/sim_server.py

Then open http://localhost:8000
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_VIEWER = REPO_ROOT / "web-viewer"
REPLAYS_DIR = WEB_VIEWER / "replays"
SRC_DIR = REPO_ROOT / "src"
TOOLS_DIR = REPO_ROOT / "tools"


def sanitize_replay_name(name: str) -> str:
    """Allow only alphanumeric, hyphens, underscores."""
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name or "replay").strip("_") or "replay"
    return safe[:200]


class SimServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_VIEWER), **kwargs)

    def log_message(self, format, *args):
        print(format % args)

    def send_json(self, obj: dict, status: int = 200) -> None:
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))

    def send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/replays":
            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            replays = []
            if REPLAYS_DIR.exists():
                for f in sorted(REPLAYS_DIR.glob("*.json")):
                    try:
                        size_kb = f.stat().st_size // 1024
                    except OSError:
                        size_kb = 0
                    name = f.stem
                    replays.append({"name": name, "file": f.name, "size_kb": size_kb})
            self.wfile.write(json.dumps(replays).encode("utf-8"))
            return

        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/run":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0:
                self.send_json({"ok": False, "error": "Missing body"}, status=400)
                return
            try:
                body = self.rfile.read(content_length).decode("utf-8")
                params = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self.send_json({"ok": False, "error": str(e)}, status=400)
                return

            name = sanitize_replay_name(params.get("name", "run"))
            dim = (params.get("dim") or "3d").lower()
            if dim not in ("2d", "3d"):
                dim = "3d"
            ic = (params.get("ic") or "disk").lower()
            if ic not in ("disk", "cloud"):
                ic = "disk"
            n = max(1, min(10000, int(params.get("n", 500))))
            steps = max(1, min(100000, int(params.get("steps", 1000))))
            dt = float(params.get("dt", 0.01))
            r_max = float(params.get("r_max", 2.0))
            replay_every = max(1, min(1000, int(params.get("replay_every", 20))))
            softening = float(params.get("softening", 0.05))
            seed = int(params.get("seed", 42))

            REPLAYS_DIR.mkdir(parents=True, exist_ok=True)
            out_json = REPLAYS_DIR / f"{name}.json"

            with tempfile.NamedTemporaryFile(suffix=".npz", delete=False, dir=REPO_ROOT) as f:
                temp_npz = f.name

            try:
                python = sys.executable
                if dim == "2d":
                    cmd = [
                        python, "-m", "gravity.demo_2d",
                        "--save-replay", temp_npz,
                        "--replay-every", str(replay_every),
                        "--no-viz",
                        "--n", str(n),
                        "--steps", str(steps),
                        "--dt", str(dt),
                        "--r-max", str(r_max),
                        "--ic", ic,
                        "--seed", str(seed),
                    ]
                else:
                    cmd = [
                        python, "-m", "gravity.demo_3d",
                        "--save-replay", temp_npz,
                        "--replay-every", str(replay_every),
                        "--no-viz",
                        "--n", str(n),
                        "--steps", str(steps),
                        "--dt", str(dt),
                        "--r-max", str(r_max),
                    ]
                # Don't capture output: demo progress (report_progress, print) streams to
                # server stdout so it appears in container logs (e.g. docker compose logs -f).
                result = subprocess.run(
                    cmd,
                    cwd=str(SRC_DIR),
                    timeout=600,
                )
                if result.returncode != 0:
                    self.send_json({
                        "ok": False,
                        "error": f"Simulation exited with code {result.returncode}. Check server logs for details.",
                    }, status=500)
                    return

                export_result = subprocess.run(
                    [python, str(TOOLS_DIR / "export_replay_to_json.py"), temp_npz, str(out_json)],
                    cwd=str(REPO_ROOT),
                    timeout=60,
                )
                if export_result.returncode != 0:
                    self.send_json({
                        "ok": False,
                        "error": f"Export exited with code {export_result.returncode}. Check server logs.",
                    }, status=500)
                    return

                n_snapshots = 1 + (steps // replay_every)
                self.send_json({"ok": True, "name": name, "n_snapshots": n_snapshots})
            finally:
                try:
                    os.unlink(temp_npz)
                except OSError:
                    pass
            return

        return SimpleHTTPRequestHandler.do_GET(self)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/replays/"):
            name = path.replace("/api/replays/", "").strip("/")
            name = sanitize_replay_name(name)
            if name == "replay" and not (REPLAYS_DIR / "replay.json").exists():
                pass
            target = REPLAYS_DIR / f"{name}.json"
            if not target.exists():
                self.send_json({"ok": False, "error": "Replay not found"}, status=404)
                return
            try:
                target.unlink()
            except OSError as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
                return
            self.send_cors_headers()
            self.send_json({"ok": True})
            return
        self.send_response(404)
        self.end_headers()


def main() -> None:
    REPLAYS_DIR.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("", port), SimServerHandler)
    print(f"Serving at http://localhost:{port}")
    print("Open in browser to run simulations and view replays.")
    server.serve_forever()


if __name__ == "__main__":
    main()
