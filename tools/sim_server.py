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
        # Suppress noisy GET 200/304 for page, static assets, and replay list (browser polling).
        # Still log POST/DELETE and any errors so runs and failures are visible.
        if len(args) >= 2:
            requestline, code = args[0], str(args[1])
            if code in ("200", "304") and requestline.startswith("GET "):
                raw_path = requestline.split(None, 2)[1] if len(requestline.split(None, 2)) > 1 else ""
                path = raw_path.split("?")[0]
                if path in ("/", "/api/replays") or path.startswith("/replays/"):
                    return
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
            steps = max(1, min(1_000_000, int(params.get("steps", 1000))))
            dt = float(params.get("dt", 0.01))
            r_max = float(params.get("r_max", 2.0))
            replay_every = max(1, min(1000, int(params.get("replay_every", 20))))
            # Cap snapshots so the exported JSON stays loadable in the browser (~2000 snapshots)
            MAX_SNAPSHOTS = 2000
            n_snapshots_cap = 1 + (steps // replay_every)
            if n_snapshots_cap > MAX_SNAPSHOTS:
                replay_every = max(replay_every, (steps + MAX_SNAPSHOTS - 2) // (MAX_SNAPSHOTS - 1))
            softening = float(params.get("softening", 0.05))
            seed = int(params.get("seed", 42))
            use_gpu = bool(params.get("gpu", False))
            M_star = float(params.get("M_star", 1.0))
            m_particle = params.get("m_particle")  # None = use default 1/(N+1) in demos
            if m_particle is not None:
                m_particle = float(m_particle)
            collisions = bool(params.get("collisions", False))
            r_collide = params.get("r_collide")
            if r_collide is not None:
                r_collide = float(r_collide)

            REPLAYS_DIR.mkdir(parents=True, exist_ok=True)
            out_json = REPLAYS_DIR / f"{name}.json"
            # Keep .npz in replays/ so you can thin later with tools/thin_replay.py
            temp_npz = REPLAYS_DIR / f"{name}.npz"

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
                        "--M_star", str(M_star),
                    ]
                    if m_particle is not None:
                        cmd.extend(["--m-particle", str(m_particle)])
                    if collisions:
                        cmd.append("--collisions")
                        if r_collide is not None:
                            cmd.extend(["--r-collide", str(r_collide)])
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
                        "--M_star", str(M_star),
                    ]
                    if m_particle is not None:
                        cmd.extend(["--m-particle", str(m_particle)])
                    if collisions:
                        cmd.append("--collisions")
                        if r_collide is not None:
                            cmd.extend(["--r-collide", str(r_collide)])
                if use_gpu:
                    cmd.append("--gpu")
                # Don't capture output: demo progress (report_progress, print) streams to
                # server stdout so it appears in container logs (e.g. docker compose logs -f).
                # Timeout 24h for long runs (e.g. 1M steps, 5k particles can take many hours).
                result = subprocess.run(
                    cmd,
                    cwd=str(SRC_DIR),
                    timeout=86400,
                )
                if result.returncode != 0:
                    self.send_json({
                        "ok": False,
                        "error": f"Simulation exited with code {result.returncode}. Check server logs for details.",
                    }, status=500)
                    return

                export_result = subprocess.run(
                    [python, str(TOOLS_DIR / "export_replay_to_json.py"), str(temp_npz), str(out_json)],
                    cwd=str(REPO_ROOT),
                    timeout=600,
                )
                if export_result.returncode != 0:
                    self.send_json({
                        "ok": False,
                        "error": f"Export exited with code {export_result.returncode}. Check server logs.",
                    }, status=500)
                    return

                n_snapshots = 1 + (steps // replay_every)
                self.send_json({
                    "ok": True,
                    "name": name,
                    "n_snapshots": n_snapshots,
                    "replay_every": replay_every,
                })
            finally:
                # Optionally remove .npz to save space (keep it by default for thinning)
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
