"""
Sync layer — reads framework files from disk and populates SQLite.

SL-002: Project discovery — reads projects.md, upserts into projects table.
SL-003: Full parse — for each active project, reads framework files and
        populates all remaining tables.

Entry point: run_sync() — called on every dashboard request.
"""

import os, re, sqlite3
from datetime import datetime, timezone
from db import get_conn

PROJECTS_MD = os.path.expanduser("~/Developer/engineering-playbook/projects.md")

# Fixed color palette — 8 colors, assigned by hashing project name
_PALETTE = [
    "#2563EB", "#0D9488", "#7C3AED", "#D97706",
    "#DC2626", "#059669", "#DB2777", "#0891B2",
]


def _project_color(name):
    return _PALETTE[sum(ord(c) for c in name) % len(_PALETTE)]


# ── SL-002: Project discovery ──────────────────────────────────────────────────

def _discover_projects(conn):
    """Read projects.md and upsert each row into the projects table."""
    if not os.path.exists(PROJECTS_MD):
        return

    with open(PROJECTS_MD, "r") as f:
        text = f.read()

    # Parse the markdown table — skip header and separator rows
    rows = []
    in_table = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("| Name") or line.startswith("|---"):
            in_table = True
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2:
                rows.append((parts[0], parts[1]))

    now = datetime.now(timezone.utc).isoformat()
    c = conn.cursor()

    # Track names seen in this sync — mark others inactive
    seen = set()
    for name, path in rows:
        if not name:
            continue
        color = _project_color(name)
        is_active = 1 if os.path.isdir(path) else 0
        seen.add(name)

        # Upsert — insert or update path/color/is_active/last_synced
        c.execute("""
            INSERT INTO projects (name, path, color, last_synced, is_active)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                path        = excluded.path,
                color       = excluded.color,
                last_synced = excluded.last_synced,
                is_active   = excluded.is_active
        """, (name, path, color, now, is_active))

    # Projects no longer in registry → mark inactive (preserve history)
    if seen:
        placeholders = ",".join("?" * len(seen))
        c.execute(
            f"UPDATE projects SET is_active = 0 WHERE name NOT IN ({placeholders})",
            list(seen)
        )

    conn.commit()


# ── SL-003: Full parse ─────────────────────────────────────────────────────────

def _clear_project_data(conn, project_id):
    """Remove all derived data for a project before re-syncing."""
    c = conn.cursor()
    for table in ("phases", "deliverables", "slices", "materials",
                  "decisions", "changes", "questions", "flags"):
        c.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))
    conn.commit()


def _section_text(text, header):
    """Extract text under a markdown ## header, up to the next ## header."""
    pattern = rf"^##\s+{re.escape(header)}\s*$"
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return ""
    start = match.end()
    next_section = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_section.start() if next_section else len(text)
    return text[start:end].strip()


def _parse_backlog(conn, project_id, backlog_path):
    """Parse docs/backlog.md — extract phases, deliverables, slices."""
    if not os.path.exists(backlog_path):
        return

    with open(backlog_path, "r") as f:
        text = f.read()

    c = conn.cursor()

    # ── Phases (### Phase N · Name) ────────────────────────────────────────────
    phase_blocks = re.split(r"(?=^### Phase \d+)", text, flags=re.MULTILINE)
    for block in phase_blocks:
        m = re.match(r"^### Phase (\d+)\s*[·•]\s*(.+)", block, re.MULTILINE)
        if not m:
            continue
        phase_name = f"Phase {m.group(1)} — {m.group(2).strip()}"
        status_m = re.search(r"^Status:\s*(.+)", block, re.MULTILINE)
        status = status_m.group(1).strip() if status_m else "Planning"
        c.execute("""
            INSERT INTO phases (project_id, name, status)
            VALUES (?, ?, ?)
        """, (project_id, phase_name, status))

    # ── Deliverables (### D-NN · Name) ─────────────────────────────────────────
    deliv_blocks = re.split(r"(?=^### D-\d+)", text, flags=re.MULTILINE)
    for block in deliv_blocks:
        m = re.match(r"^### (D-\d+)\s*[·•]\s*(.+)", block, re.MULTILINE)
        if not m:
            continue
        deliv_id = m.group(1)
        deliv_name = f"{deliv_id} — {m.group(2).strip()}"
        status_m = re.search(r"^Status:\s*(.+)", block, re.MULTILINE)
        status = status_m.group(1).strip() if status_m else "Defined"
        phase_m = re.search(r"^Phase:\s*(.+)", block, re.MULTILINE)
        phase_name = phase_m.group(1).strip() if phase_m else ""
        type_m = re.search(r"^Type:\s*(.+)", block, re.MULTILINE)
        dtype = type_m.group(1).strip() if type_m else ""
        slices_m = re.search(r"^Slices:\s*(.+)", block, re.MULTILINE)
        slice_count = len(slices_m.group(1).split("·")) if slices_m else 0
        c.execute("""
            INSERT INTO deliverables (project_id, phase_name, name, status, type, slice_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (project_id, phase_name, deliv_name, status, dtype, slice_count))

    # ── Slices (### SL-NNN · Name) ─────────────────────────────────────────────
    slice_blocks = re.split(r"(?=^### SL-\d+)", text, flags=re.MULTILINE)
    for block in slice_blocks:
        m = re.match(r"^### (SL-\d+)\s*[·•]\s*(.+)", block, re.MULTILINE)
        if not m:
            continue
        slice_id = m.group(1)
        slice_name = m.group(2).strip()

        status_m   = re.search(r"^Status:\s*(.+)", block, re.MULTILINE)
        phase_m    = re.search(r"^Phase:\s*(.+)", block, re.MULTILINE)
        deliv_m    = re.search(r"^Deliverable:\s*(.+)", block, re.MULTILINE)
        url_m      = re.search(r"^review_url:\s*(.+)", block, re.MULTILINE)

        status       = status_m.group(1).strip() if status_m else "Ready"
        phase_name   = phase_m.group(1).strip() if phase_m else ""
        deliv_name   = deliv_m.group(1).strip() if deliv_m else ""
        review_url   = url_m.group(1).strip() if url_m else None
        is_blocked   = 1 if status == "Blocked" else 0

        c.execute("""
            INSERT INTO slices
              (project_id, phase_name, deliverable_name, slice_id, name,
               status, review_url, is_blocked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, phase_name, deliv_name, slice_id, slice_name,
              status, review_url, is_blocked))

    conn.commit()


def _parse_handoff(conn, project_id, handoff_path):
    """Parse handoff.md — extract open items (flags) and outstanding questions."""
    if not os.path.exists(handoff_path):
        return

    with open(handoff_path, "r") as f:
        text = f.read()

    c = conn.cursor()

    # "Open right now" section → flags table
    open_section = _section_text(text, "Open right now")
    for line in open_section.splitlines():
        line = line.strip().lstrip("-").strip()
        if line:
            c.execute("""
                INSERT INTO flags (project_id, text, object_type, flagged_reason)
                VALUES (?, ?, 'handoff', 'open item')
            """, (project_id, line))

    # "Outstanding questions" section → questions table
    questions_section = _section_text(text, "Outstanding questions needing outside input")
    for line in questions_section.splitlines():
        line = line.strip().lstrip("-").strip()
        if line:
            c.execute("""
                INSERT INTO questions (project_id, text, source)
                VALUES (?, ?, 'handoff')
            """, (project_id, line))

    conn.commit()


def _scan_materials(conn, project_id, project_path):
    """Walk known material locations and record discovered files."""
    c = conn.cursor()

    checks = [
        # (glob_dir, pattern, type, label_fn)
        ("docs/design",   r"sprint-.*\.html$", "screen"),
        ("docs/process",  r"to-be-.*\.md$",    "process"),
        ("docs/process",  r"as-is-.*\.md$",    "process"),
        ("docs",          r"discovery-brief\.md$", "doc"),
    ]

    for subdir, pattern, mtype in checks:
        dirpath = os.path.join(project_path, subdir)
        if not os.path.isdir(dirpath):
            continue
        for fname in os.listdir(dirpath):
            if re.search(pattern, fname):
                fpath = os.path.join(dirpath, fname)
                label = fname.replace("-", " ").replace("_", " ").rsplit(".", 1)[0]
                c.execute("""
                    INSERT INTO materials (project_id, name, type, file_path)
                    VALUES (?, ?, ?, ?)
                """, (project_id, label, mtype, fpath))

    conn.commit()


def _flag_stale_slices(conn, project_id, project_path):
    """Flag any In Progress slice whose project was last modified > 3 days ago."""
    c = conn.cursor()
    c.execute("""
        SELECT id, slice_id FROM slices
        WHERE project_id = ? AND status = 'In Progress'
    """, (project_id,))
    rows = c.fetchall()
    if not rows:
        return

    # Most recently modified file in project directory
    latest_mtime = 0
    for root, _, files in os.walk(project_path):
        for f in files:
            try:
                mtime = os.path.getmtime(os.path.join(root, f))
                if mtime > latest_mtime:
                    latest_mtime = mtime
            except OSError:
                pass

    age_days = (datetime.now().timestamp() - latest_mtime) / 86400
    if age_days > 3:
        for row in rows:
            c.execute("""
                UPDATE slices SET is_flagged = 1, flagged_reason = 'stale progress'
                WHERE id = ?
            """, (row["id"],))
        conn.commit()


def _sync_project(conn, project_id, project_path):
    _clear_project_data(conn, project_id)
    _parse_backlog(conn, project_id, os.path.join(project_path, "docs/backlog.md"))
    _parse_handoff(conn, project_id, os.path.join(project_path, "docs/continuity/handoff.md"))
    _scan_materials(conn, project_id, project_path)
    _flag_stale_slices(conn, project_id, project_path)


# ── Public entry point ─────────────────────────────────────────────────────────

def run_sync():
    """Discover projects and sync all active ones. Called on every dashboard load."""
    conn = get_conn()
    _discover_projects(conn)

    c = conn.cursor()
    c.execute("SELECT id, path FROM projects WHERE is_active = 1")
    projects = c.fetchall()

    for p in projects:
        _sync_project(conn, p["id"], p["path"])

    conn.close()
