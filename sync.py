"""
Sync layer — reads framework files into SQLite.

SL-002: project discovery only. Reads projects.md from the framework
path, parses the markdown table, and reconciles the projects table:
- new projects inserted
- existing projects updated (path may have moved)
- projects whose path no longer exists on disk marked inactive
- projects no longer present in projects.md marked inactive

Sync timestamp is written on every run. Later slices add per-project
file parsing on top of this discovery layer.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from config import get_framework_path
from db import get_conn


def _parse_projects_md(projects_md_path):
    """Parse the projects.md markdown table. Returns list of (name, path) tuples."""
    discovered = []
    with open(projects_md_path) as f:
        for raw in f:
            line = raw.strip()
            # Skip non-table lines, header, and separator rows
            if not line.startswith("|") or "---" in line:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2 or cells[0].lower() == "name":
                continue
            name, path = cells[0], os.path.expanduser(cells[1])
            if name and path:
                discovered.append((name, path))
    return discovered


def discover_projects():
    """Sync projects table from the framework's projects.md registry."""
    projects_md = Path(get_framework_path()) / "projects.md"
    if not projects_md.exists():
        # First-run before config — surface to log, don't crash
        print(f"[sync] projects.md not found at {projects_md} — skipping discovery")
        return

    discovered = _parse_projects_md(projects_md)
    sync_time = datetime.now(timezone.utc).isoformat()

    conn = get_conn()
    c = conn.cursor()

    existing = {r["name"]: r["id"] for r in c.execute("SELECT id, name FROM projects")}
    discovered_names = {name for name, _ in discovered}

    for name, path in discovered:
        is_active = 1 if os.path.isdir(path) else 0
        if name in existing:
            c.execute(
                "UPDATE projects SET path = ?, last_synced = ?, is_active = ? WHERE name = ?",
                (path, sync_time, is_active, name),
            )
        else:
            c.execute(
                "INSERT INTO projects (name, path, last_synced, is_active) VALUES (?, ?, ?, ?)",
                (name, path, sync_time, is_active),
            )

    # Projects in DB but no longer in projects.md → mark inactive (preserve history)
    for name in existing:
        if name not in discovered_names:
            c.execute("UPDATE projects SET is_active = 0 WHERE name = ?", (name,))

    conn.commit()
    conn.close()


def get_last_synced():
    """Return the most recent last_synced timestamp across projects, or None."""
    conn = get_conn()
    row = conn.execute("SELECT MAX(last_synced) AS ts FROM projects").fetchone()
    conn.close()
    return row["ts"] if row and row["ts"] else None
