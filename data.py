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

    # Phases across all active projects — subqueries avoid JOIN Cartesian product
    c.execute("""
        SELECT ph.name, ph.status, ph.progress_pct, ph.gate_status, ph.started_date,
               (SELECT COUNT(*) FROM slices s
                WHERE s.project_id = ph.project_id AND s.phase_name = ph.name)            as total_slices,
               (SELECT COUNT(*) FROM slices s
                WHERE s.project_id = ph.project_id AND s.phase_name = ph.name
                  AND s.status = 'Done')                                                   as done_slices,
               (SELECT COUNT(*) FROM deliverables d
                WHERE d.project_id = ph.project_id AND d.phase_name = ph.name)            as total_deliverables,
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

    # Slices — Done excluded (show active work)
    # Resolve deliverable short-ref (e.g. "D-09") to full name via LEFT JOIN
    c.execute("""
        SELECT s.slice_id, s.name, s.status, s.phase_name,
               COALESCE(dv.name, s.deliverable_name) as deliverable_name,
               s.is_blocked, s.is_flagged, s.flagged_reason, s.review_url,
               p.id as project_id, p.name as project_name, p.color as project_color
        FROM slices s
        JOIN projects p ON p.id = s.project_id
        LEFT JOIN deliverables dv
               ON dv.project_id = s.project_id
              AND dv.name LIKE s.deliverable_name || ' %'
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


def get_project_detail(project_id):
    """Return all tab data for a project detail page."""
    conn = get_conn()
    c = conn.cursor()

    # Action tab — blocked slices
    c.execute("""
        SELECT slice_id, name, phase_name, deliverable_name, status
        FROM slices WHERE project_id = ? AND is_blocked = 1
        ORDER BY slice_id
    """, (project_id,))
    blocked = [dict(r) for r in c.fetchall()]

    # Action tab — flagged items
    c.execute("""
        SELECT text, flagged_reason, object_type, object_id
        FROM flags WHERE project_id = ?
        ORDER BY id
    """, (project_id,))
    flagged = [dict(r) for r in c.fetchall()]

    # Action tab — outstanding questions
    c.execute("""
        SELECT text, source, who_can_answer, open_days
        FROM questions WHERE project_id = ?
        ORDER BY id
    """, (project_id,))
    questions = [dict(r) for r in c.fetchall()]

    # Progress tab — phases
    c.execute("""
        SELECT name, status, started_date, gate_status, progress_pct
        FROM phases WHERE project_id = ?
        ORDER BY name
    """, (project_id,))
    phases = [dict(r) for r in c.fetchall()]

    # Progress tab — deliverables
    c.execute("""
        SELECT name, status, type, slice_count, phase_name
        FROM deliverables WHERE project_id = ?
        ORDER BY phase_name, name
    """, (project_id,))
    deliverables = [dict(r) for r in c.fetchall()]

    # Progress + Backlog — all slices
    c.execute("""
        SELECT slice_id, name, status, phase_name, deliverable_name,
               is_blocked, is_flagged, flagged_reason, review_url
        FROM slices WHERE project_id = ?
        ORDER BY slice_id
    """, (project_id,))
    slices = [dict(r) for r in c.fetchall()]

    # Materials tab
    c.execute("""
        SELECT name, type, file_path
        FROM materials WHERE project_id = ?
        ORDER BY type, name
    """, (project_id,))
    materials = [dict(r) for r in c.fetchall()]

    # Decisions & Changes tab
    c.execute("""
        SELECT title, date, body, why, phase
        FROM decisions WHERE project_id = ?
        ORDER BY date DESC
    """, (project_id,))
    decisions = [dict(r) for r in c.fetchall()]

    c.execute("""
        SELECT title, date, was_value, became_value
        FROM changes WHERE project_id = ?
        ORDER BY date DESC
    """, (project_id,))
    changes = [dict(r) for r in c.fetchall()]

    conn.close()

    # Compute tab counts
    action_count  = len(blocked) + len(flagged) + len(questions)
    progress_count = len(phases) + len(deliverables)
    backlog_count  = len(slices)
    mat_count      = len(materials)
    dec_count      = len(decisions) + len(changes)

    return {
        "blocked":        blocked,
        "flagged":        flagged,
        "questions":      questions,
        "phases":         phases,
        "deliverables":   deliverables,
        "slices":         slices,
        "materials":      materials,
        "decisions":      decisions,
        "changes":        changes,
        "action_count":   action_count,
        "progress_count": progress_count,
        "backlog_count":  backlog_count,
        "mat_count":      mat_count,
        "dec_count":      dec_count,
    }
