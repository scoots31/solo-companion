"""
Cloud push — sends a snapshot of all active projects to the Cloudflare Worker.

Reads universe, machine_label, worker_url, and push_api_key from config.json.
If those keys are absent (cloud not configured), push_snapshot() is a no-op.
Called after every sync and on a 15-minute background timer.
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

from db import get_conn

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(REPO_ROOT, "config.json")

WORKER_URL = "https://solo-companion-api.scotth-builds.workers.dev"


def _cloud_config():
    """Return cloud config dict or None if not configured."""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    universe = cfg.get("universe")
    api_key = cfg.get("push_api_key")
    if not universe or not api_key:
        return None
    return cfg


def _row(r):
    """Convert a sqlite3.Row to a plain dict."""
    return {k: r[k] for k in r.keys()}


def _read_material_content(file_path, max_bytes=50_000):
    """Read a material file and return its text content, or None on failure."""
    if not file_path:
        return None
    path = os.path.expanduser(file_path)
    if not os.path.exists(path):
        return None
    try:
        size = os.path.getsize(path)
        if size > max_bytes * 4:
            return f"[File too large to display — {size // 1024}KB]"
        with open(path, "r", encoding="utf-8", errors="strict") as f:
            content = f.read(max_bytes)
        if len(content) == max_bytes:
            content += "\n\n[... truncated at 50KB ...]"
        return content
    except (UnicodeDecodeError, IOError):
        return None


def build_snapshot(cfg):
    """Build the full JSON payload to push to Cloudflare."""
    import socket
    hostname = socket.gethostname().replace(".local", "").replace("-", " ").title()

    conn = get_conn()
    projects = []

    for p in conn.execute("SELECT * FROM projects WHERE is_active=1").fetchall():
        pid = p["id"]

        phases = [
            _row(r) for r in conn.execute(
                "SELECT * FROM phases WHERE project_id=? ORDER BY id", (pid,)
            ).fetchall()
        ]
        deliverables = [
            _row(r) for r in conn.execute(
                "SELECT * FROM deliverables WHERE project_id=? ORDER BY phase, deliverable_id", (pid,)
            ).fetchall()
        ]
        slices = [
            _row(r) for r in conn.execute(
                "SELECT * FROM slices WHERE project_id=? ORDER BY slice_id", (pid,)
            ).fetchall()
        ]
        decisions = [
            _row(r) for r in conn.execute(
                "SELECT * FROM decisions WHERE project_id=? ORDER BY date DESC", (pid,)
            ).fetchall()
        ]
        changes = [
            _row(r) for r in conn.execute(
                "SELECT * FROM changes WHERE project_id=? ORDER BY date DESC", (pid,)
            ).fetchall()
        ]
        questions = [
            _row(r) for r in conn.execute(
                "SELECT * FROM questions WHERE project_id=? ORDER BY id", (pid,)
            ).fetchall()
        ]
        flags = [
            _row(r) for r in conn.execute(
                "SELECT * FROM flags WHERE project_id=?", (pid,)
            ).fetchall()
        ]
        materials = []
        for r in conn.execute(
            "SELECT * FROM materials WHERE project_id=? ORDER BY phase_name, name", (pid,)
        ).fetchall():
            m = _row(r)
            m["content"] = _read_material_content(m.get("file_path"))
            materials.append(m)
        events = [
            _row(r) for r in conn.execute(
                "SELECT * FROM events WHERE project_id=? ORDER BY event_ts DESC LIMIT 200", (pid,)
            ).fetchall()
        ]

        projects.append({
            "id": pid,
            "name": p["name"],
            "last_synced": p["last_synced"],
            "phases": phases,
            "deliverables": deliverables,
            "slices": slices,
            "decisions": decisions,
            "changes": changes,
            "questions": questions,
            "flags": flags,
            "materials": materials,
            "events": events,
        })

    conn.close()

    return {
        "universe": cfg["universe"],
        "machine": cfg.get("machine_id") or hostname.lower().replace(" ", "-"),
        "machine_label": cfg.get("machine_label") or hostname,
        "pushed_at": datetime.now(timezone.utc).isoformat(),
        "projects": projects,
    }


def push_snapshot():
    """Push snapshot to Cloudflare. Silent on any failure."""
    cfg = _cloud_config()
    if not cfg:
        return False

    try:
        snapshot = build_snapshot(cfg)
        data = json.dumps(snapshot).encode("utf-8")
        req = urllib.request.Request(
            WORKER_URL + "/push",
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": cfg["push_api_key"],
                "User-Agent": "SoloCompanion/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def register_universe(universe, machine_label):
    """
    Register a universe with the Worker. Returns viewer_url on success, None on failure.
    Called from the settings page when a user saves their universe name.
    """
    cfg = _cloud_config()
    if not cfg:
        return None

    try:
        data = json.dumps({"universe": universe}).encode("utf-8")
        req = urllib.request.Request(
            WORKER_URL + "/register",
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": cfg["push_api_key"],
                "User-Agent": "SoloCompanion/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("viewer_url")
    except Exception:
        return None
