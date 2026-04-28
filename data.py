"""
Data access layer — query helpers for routes.
All queries go through here; routes stay thin.
"""

import os
from datetime import datetime, timezone
from db import get_conn


def _recency_label(project_path):
    """Return a human label for how recently a project directory was modified."""
    latest = 0
    try:
        for root, _, files in os.walk(project_path):
            # Skip hidden dirs (e.g. .git) for performance
            root_parts = root.replace(project_path, "").split(os.sep)
            if any(p.startswith(".") for p in root_parts):
                continue
            for f in files:
                try:
                    mtime = os.path.getmtime(os.path.join(root, f))
                    if mtime > latest:
                        latest = mtime
                except OSError:
                    pass
    except OSError:
        return "—"

    if latest == 0:
        return "—"

    age_seconds = datetime.now().timestamp() - latest
    age_days = age_seconds / 86400

    if age_days < 1:
        return "today"
    if age_days < 7:
        return f"{int(age_days)}d"
    weeks = int(age_days / 7)
    return f"{weeks}w"


def get_projects():
    """Return all active projects with recency labels, ordered by recency."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, path, color FROM projects WHERE is_active = 1 ORDER BY name")
    rows = c.fetchall()
    conn.close()

    projects = []
    for r in rows:
        projects.append({
            "id":      r["id"],
            "name":    r["name"],
            "path":    r["path"],
            "color":   r["color"],
            "recency": _recency_label(r["path"]),
        })

    # Sort by recency: today first, then days, then weeks
    def sort_key(p):
        rec = p["recency"]
        if rec == "today": return 0
        if rec.endswith("d"): return int(rec[:-1])
        if rec.endswith("w"): return int(rec[:-1]) * 7
        return 9999

    return sorted(projects, key=sort_key)


def get_last_synced():
    """Return the most recent sync timestamp across all projects, formatted."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT MAX(last_synced) as ts FROM projects")
    row = c.fetchone()
    conn.close()
    if not row or not row["ts"]:
        return "never"
    try:
        dt = datetime.fromisoformat(row["ts"])
        return dt.strftime("%-I:%M %p").lower()
    except Exception:
        return row["ts"]


def get_dashboard_data():
    """Return all data needed to render the dashboard."""
    conn = get_conn()
    c = conn.cursor()

    # Blocked slices across all active projects
    c.execute("""
        SELECT s.slice_id, s.name, s.phase_name, s.deliverable_name,
               p.name as project_name, p.color as project_color
        FROM slices s
        JOIN projects p ON p.id = s.project_id
        WHERE s.is_blocked = 1 AND p.is_active = 1
        ORDER BY p.name, s.slice_id
    """)
    blocked = [dict(r) for r in c.fetchall()]

    # Flagged items across all active projects
    c.execute("""
        SELECT f.text, f.flagged_reason, f.object_type, f.object_id,
               p.name as project_name, p.color as project_color
        FROM flags f
        JOIN projects p ON p.id = f.project_id
        WHERE p.is_active = 1
        ORDER BY p.name
    """)
    flagged = [dict(r) for r in c.fetchall()]

    # Phases across all active projects
    c.execute("""
        SELECT ph.name, ph.status, ph.progress_pct,
               p.id as project_id, p.name as project_name, p.color as project_color
        FROM phases ph
        JOIN projects p ON p.id = ph.project_id
        WHERE p.is_active = 1
        ORDER BY p.name, ph.name
    """)
    phases = [dict(r) for r in c.fetchall()]

    # Deliverables across all active projects
    c.execute("""
        SELECT d.name, d.status, d.type, d.slice_count, d.phase_name,
               p.id as project_id, p.name as project_name, p.color as project_color
        FROM deliverables d
        JOIN projects p ON p.id = d.project_id
        WHERE p.is_active = 1
        ORDER BY p.name, d.phase_name, d.name
    """)
    deliverables = [dict(r) for r in c.fetchall()]

    # Slices — In Build, In QA, Done excluded (show active work)
    c.execute("""
        SELECT s.slice_id, s.name, s.status, s.phase_name, s.deliverable_name,
               s.is_blocked, s.is_flagged,
               p.id as project_id, p.name as project_name, p.color as project_color
        FROM slices s
        JOIN projects p ON p.id = s.project_id
        WHERE p.is_active = 1
          AND s.status NOT IN ('Done')
        ORDER BY p.name, s.slice_id
    """)
    slices = [dict(r) for r in c.fetchall()]

    conn.close()

    return {
        "blocked":      blocked,
        "flagged":      flagged,
        "phases":       phases,
        "deliverables": deliverables,
        "slices":       slices,
    }


def get_project_by_name(name):
    """Return a single active project by name, or None."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, path, color FROM projects WHERE name = ? AND is_active = 1", (name,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None
