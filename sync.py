"""
Sync layer — reads framework files into SQLite.

SL-002: project discovery from projects.md.
SL-003: full content sync per active project — phases, deliverables, slices
        with every field per records-spec.md; decisions, changes, questions
        from continuity files; materials from docs/ filesystem walk; flags
        derived at parse time.

Re-sync pattern: each sync is authoritative. For each project, child rows
(phases, deliverables, slices, materials, decisions, changes, questions,
flags) are deleted and re-inserted in a single transaction. Projects whose
backlog format is incompatible with records-spec.md are marked inactive
and content sync is skipped for them.
"""

import json, os, re
from datetime import datetime, timezone
from pathlib import Path

from config import get_framework_path
from db import get_conn
from parsers import (
    DELIVERABLE_FIELDS,
    PHASE_FIELDS,
    SLICE_FIELDS,
    extract_section,
    is_records_spec_format,
    parse_decisions,
    parse_deliverable_header,
    parse_fields,
    parse_phase_header,
    parse_slice_header,
    split_records,
)

STALE_IN_PROGRESS_DAYS = 3


# ── Project discovery (SL-002) ──────────────────────────────────────────

def _parse_projects_md(projects_md_path):
    """Parse the projects.md markdown table. Returns list of (name, path) tuples."""
    discovered = []
    with open(projects_md_path) as f:
        for raw in f:
            line = raw.strip()
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
    """Sync projects table from projects.md, then content-sync each active project."""
    projects_md = Path(get_framework_path()) / "projects.md"
    if not projects_md.exists():
        print(f"[sync] projects.md not found at {projects_md}")
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

    for name in existing:
        if name not in discovered_names:
            c.execute("UPDATE projects SET is_active = 0 WHERE name = ?", (name,))

    conn.commit()

    # Phase 2 of sync: content per active project (SL-003)
    for r in c.execute("SELECT id, name, path FROM projects WHERE is_active = 1").fetchall():
        sync_project_content(conn, r["id"], r["name"], r["path"])

    conn.close()


def get_last_synced():
    """Return the most recent last_synced timestamp across projects, or None."""
    conn = get_conn()
    row = conn.execute("SELECT MAX(last_synced) AS ts FROM projects").fetchone()
    conn.close()
    return row["ts"] if row and row["ts"] else None


# ── Content sync per project (SL-003) ──────────────────────────────────

def sync_project_content(conn, project_id, project_name, project_path):
    """Parse all framework files for a single project and replace its DB rows.

    If the project's backlog is not in records-spec.md format, the project is
    marked inactive and no content rows are written.
    """
    project_dir = Path(project_path)
    backlog_path = project_dir / "docs" / "backlog.md"

    if not backlog_path.exists():
        print(f"[sync] {project_name}: docs/backlog.md missing, marking inactive")
        conn.execute("UPDATE projects SET is_active = 0 WHERE id = ?", (project_id,))
        conn.commit()
        return

    backlog_text = backlog_path.read_text()
    if not is_records_spec_format(backlog_text):
        print(f"[sync] {project_name}: backlog format pre-records-spec, marking inactive")
        conn.execute("UPDATE projects SET is_active = 0 WHERE id = ?", (project_id,))
        conn.commit()
        return

    backlog_mtime = datetime.fromtimestamp(backlog_path.stat().st_mtime, tz=timezone.utc).isoformat()

    c = conn.cursor()

    # Wipe child rows for this project; re-insert fresh below
    for table in ("phases", "deliverables", "slices", "materials",
                  "decisions", "changes", "questions", "flags"):
        c.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))

    _sync_phases(c, project_id, backlog_text)
    _sync_deliverables(c, project_id, backlog_text)
    handoff_open_right_now = _read_handoff_sections(project_dir)
    _sync_slices(c, project_id, backlog_text, backlog_mtime, handoff_open_right_now)
    _sync_decisions_and_changes(c, project_id, project_dir)
    _sync_questions(c, project_id, project_dir, handoff_open_right_now)
    _sync_flags(c, project_id, handoff_open_right_now)
    _sync_materials(c, project_id, project_dir)

    conn.commit()


# ── Per-table sync helpers ──────────────────────────────────────────────

def _list_or_none(value):
    """Return JSON-encoded value if list-shaped, else the raw string, else None."""
    if value is None:
        return None
    if isinstance(value, list):
        return json.dumps(value)
    return json.dumps(value) if isinstance(value, str) else None


def _scalar(value):
    """Return string scalar or None. Lists collapsed to comma-joined string."""
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(value) if value else None
    return str(value).strip() or None


def _sync_phases(c, project_id, backlog_text):
    section = extract_section(backlog_text, "## Phase Records")
    for header, body in split_records(section):
        phase_key, _ = parse_phase_header(header)
        if not phase_key:
            continue
        fields = parse_fields(body, PHASE_FIELDS)
        # Use the full header (e.g. "Phase 1 · Foundation") as the canonical name
        full_name = header.split(" · ", 1)[0] + " · " + header.split(" · ", 1)[1] if " · " in header else header
        c.execute("""
            INSERT INTO phases
              (project_id, name, status, plain_description, technical_description,
               question_answered, deliverables_list, process_steps_completed,
               proves_de_risks, out_of_scope, blocked_by, definition_of_done,
               acceptance_criteria, self_verification, builder_confirmation, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            full_name,
            _scalar(fields.get("Status")),
            _scalar(fields.get("Plain language description")),
            _scalar(fields.get("Technical description")),
            _scalar(fields.get("Question this phase answers")),
            _scalar(fields.get("Deliverables")),
            _scalar(fields.get("Process steps completed")),
            _scalar(fields.get("Proves / de-risks")),
            _scalar(fields.get("Explicitly out of scope")),
            _scalar(fields.get("Blocked by")),
            _scalar(fields.get("Definition of done")),
            _list_or_none(fields.get("Acceptance criteria")),
            _list_or_none(fields.get("Self-verification checklist")),
            _list_or_none(fields.get("Builder confirmation")),
            _scalar(fields.get("Notes")),
        ))


def _sync_deliverables(c, project_id, backlog_text):
    section = extract_section(backlog_text, "## Deliverable Records")
    for header, body in split_records(section):
        del_id, del_name = parse_deliverable_header(header)
        if not del_id:
            continue
        fields = parse_fields(body, DELIVERABLE_FIELDS)
        c.execute("""
            INSERT INTO deliverables
              (project_id, deliverable_id, name, status, type, phase,
               plain_description, technical_description, screens,
               acceptance_criteria, self_verification, builder_confirmation,
               slices_list, references_list, depends_on, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            del_id,
            del_name,
            _scalar(fields.get("Status")),
            _scalar(fields.get("Type")),
            _scalar(fields.get("Phase")),
            _scalar(fields.get("Plain language description")),
            _scalar(fields.get("Technical description")),
            _list_or_none(fields.get("Screens")),
            _list_or_none(fields.get("Acceptance criteria")),
            _list_or_none(fields.get("Self-verification checklist")),
            _list_or_none(fields.get("Builder confirmation")),
            _scalar(fields.get("Slices")),
            _list_or_none(fields.get("References")),
            _scalar(fields.get("Depends on")),
            _scalar(fields.get("Notes")),
        ))


def _sync_slices(c, project_id, backlog_text, backlog_mtime, open_right_now):
    section = extract_section(backlog_text, "## Slice Detail")
    open_right_now_ids = {item.get("slice_id") for item in open_right_now if item.get("slice_id")}
    for header, body in split_records(section):
        slice_id, slice_name = parse_slice_header(header)
        if not slice_id:
            continue
        fields = parse_fields(body, SLICE_FIELDS)
        status = _scalar(fields.get("Status"))

        is_blocked = 1 if (status or "").lower() == "blocked" else 0

        # Flagged: stale In Progress (file mtime > 3 days) OR slice id appears in handoff "Open right now"
        is_flagged = 0
        flagged_reason = None
        if (status or "").lower() == "in progress":
            try:
                age = datetime.now(timezone.utc) - datetime.fromisoformat(backlog_mtime)
                if age.days > STALE_IN_PROGRESS_DAYS:
                    is_flagged = 1
                    flagged_reason = f"In Progress for {age.days}+ days"
            except ValueError:
                pass
        if slice_id in open_right_now_ids:
            is_flagged = 1
            flagged_reason = "Listed in handoff Open right now"

        c.execute("""
            INSERT INTO slices
              (project_id, slice_id, name, status, phase, deliverable_ref,
               plain_description, technical_description,
               design_anchor, data_anchor, process_anchor,
               references_list, done_criteria, self_verification, builder_confirmation,
               depends_on, notes, distribution_note,
               is_blocked, is_flagged, flagged_reason, review_url, last_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            slice_id,
            slice_name,
            status,
            _scalar(fields.get("Phase")),
            _scalar(fields.get("Deliverable")),
            _scalar(fields.get("Plain language description")),
            _scalar(fields.get("Technical description")),
            _scalar(fields.get("Design anchor")),
            _scalar(fields.get("Data anchor")),
            _scalar(fields.get("Process anchor")),
            _list_or_none(fields.get("References")),
            _list_or_none(fields.get("Done criteria")),
            _list_or_none(fields.get("Self-verification checklist")),
            _list_or_none(fields.get("Builder confirmation")),
            _scalar(fields.get("Depends on")),
            _scalar(fields.get("Notes")),
            _scalar(fields.get("Distribution note")),
            is_blocked,
            is_flagged,
            flagged_reason,
            _scalar(fields.get("Review URL")),
            backlog_mtime,
        ))


def _sync_decisions_and_changes(c, project_id, project_dir):
    decisions_md = project_dir / "docs" / "continuity" / "decisions.md"
    changes_md = project_dir / "docs" / "continuity" / "changes.md"

    if decisions_md.exists():
        for entry in parse_decisions(decisions_md.read_text()):
            c.execute("""
                INSERT INTO decisions
                  (project_id, title, phase, date, status, body, why, alternatives, tradeoffs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                entry.get("title"),
                entry.get("phase"),
                entry.get("date"),
                entry.get("status"),
                entry.get("body"),
                entry.get("why"),
                entry.get("alternatives"),
                entry.get("tradeoffs"),
            ))

    if changes_md.exists():
        # Same parser shape as decisions for now — append-only labelled blocks
        for entry in parse_decisions(changes_md.read_text()):
            c.execute("""
                INSERT INTO changes
                  (project_id, title, phase, date, was_value, became_value, why, affects)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                entry.get("title"),
                entry.get("phase"),
                entry.get("date"),
                entry.get("alternatives"),  # repurposed — refine if changes.md gets a stricter format
                entry.get("body"),
                entry.get("why"),
                entry.get("tradeoffs"),
            ))


def _sync_questions(c, project_id, project_dir, open_right_now):
    questions_md = project_dir / "docs" / "continuity" / "questions.md"
    if questions_md.exists():
        for entry in parse_decisions(questions_md.read_text()):  # same labelled-block shape
            c.execute("""
                INSERT INTO questions
                  (project_id, text, surfaced_during, blocking, who_can_answer, status, answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                entry.get("title"),
                entry.get("phase"),       # surfaced_during often lives in Phase: line
                None,
                None,
                entry.get("status"),
                entry.get("body"),
            ))


def _sync_flags(c, project_id, open_right_now):
    """Persist 'Open right now' items from handoff as flags for the dashboard Needs Attention card."""
    for item in open_right_now:
        c.execute("""
            INSERT INTO flags (project_id, text, object_type, object_id, flagged_reason)
            VALUES (?, ?, ?, ?, ?)
        """, (
            project_id,
            item.get("text"),
            "slice" if item.get("slice_id") else "handoff",
            item.get("slice_id"),
            "Open right now (handoff)",
        ))


def _sync_materials(c, project_id, project_dir):
    """Walk docs/ and register meaningful files as materials."""
    docs = project_dir / "docs"
    if not docs.exists():
        return

    rules = (
        ("discovery-brief.md",                     "Discover", "Discovery brief"),
        ("brainstorm-*.md",                        "Discover", "Brainstorm"),
        ("process/as-is-*.md",                     "Discover", "As-is process map"),
        ("process/to-be-*.md",                     "Discover", "To-be process map"),
        ("design/sprint-*.html",                   "Design",   "Design screen"),
        ("design/deferred-decisions.md",           "Design",   "Deferred decisions"),
        ("backlog.md",                             "Build",    "Backlog"),
        ("tech-context.md",                        "Build",    "Tech context"),
        ("continuity/handoff.md",                  "Continuity", "Handoff"),
        ("continuity/decisions.md",                "Continuity", "Decision log"),
        ("continuity/changes.md",                  "Continuity", "Change log"),
        ("continuity/questions.md",                "Continuity", "Outstanding questions"),
        ("continuity/current-phase.md",            "Continuity", "Current phase"),
        ("continuity/onboarding.md",               "Continuity", "Onboarding"),
        ("continuity/target-state.md",             "Continuity", "Target state"),
    )

    for pattern, phase_name, mat_type in rules:
        for path in docs.glob(pattern):
            try:
                rel = path.relative_to(project_dir)
            except ValueError:
                rel = path
            try:
                c.execute("""
                    INSERT INTO materials (project_id, phase_name, name, type, file_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (project_id, phase_name, path.name, mat_type, str(rel)))
            except Exception:
                pass


# ── Handoff section reader ──────────────────────────────────────────────

_OPEN_RIGHT_NOW_RE = re.compile(
    r"^##\s+Open right now\s*\n(.*?)(?=^## |\Z)",
    re.DOTALL | re.MULTILINE | re.IGNORECASE,
)
_SLICE_REF_RE = re.compile(r"\b(SL-[A-Za-z0-9-]+)\b")


def _read_handoff_sections(project_dir):
    """Extract 'Open right now' items from handoff.md as a list of dicts."""
    handoff = project_dir / "docs" / "continuity" / "handoff.md"
    if not handoff.exists():
        return []

    text = handoff.read_text()
    m = _OPEN_RIGHT_NOW_RE.search(text)
    if not m:
        return []

    items = []
    for line in m.group(1).split("\n"):
        stripped = line.strip()
        if not stripped or not stripped.startswith(("- ", "* ")):
            continue
        text = stripped[2:].strip()
        slice_match = _SLICE_REF_RE.search(text)
        items.append({"text": text, "slice_id": slice_match.group(1) if slice_match else None})
    return items
