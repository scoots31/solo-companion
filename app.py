"""
Solo Companion — local read-only companion app for the Solo Builder Framework.

SL-001: Flask shell on port 8710.
SL-002: project discovery sync from projects.md.
SL-003: full content sync — phases, deliverables, slices with every field
        per records-spec.md, plus decisions, changes, questions, materials,
        flags.
SL-004: persistent sidebar — project list, color dots, recency labels,
        navigation. Layout wrapper used by all routes.
SL-005: dashboard top bar — project count, last-synced relative time,
        refresh button (/sync POST route).
SL-006: Needs Attention — Blocked card. Red-tinted card for is_blocked
        slices; absent from DOM when no blocked slices exist.
SL-007: Needs Attention — Flagged card. Amber-tinted card for flags
        table items + is_flagged slices; absent when nothing flagged.
SL-008: Dashboard Phases bucket — In Progress phases with progress bars.
"""

import os
import time
from datetime import datetime, timezone
from flask import Flask, redirect, request, url_for

from db import get_conn, init_db
from sync import discover_projects, get_last_synced

PORT = 8710
app = Flask(__name__)
init_db()

# ── Color palette (deterministic hash of project name) ──────────────────

_PALETTE = [
    "#2563EB", "#0D9488", "#7C3AED", "#D97706",
    "#DC2626", "#059669", "#DB2777", "#0891B2",
]


def _project_color(name):
    return _PALETTE[sum(ord(c) for c in name) % len(_PALETTE)]


# ── Recency label from filesystem mtime ─────────────────────────────────

def _project_recency(path):
    """Walk project directory and return recency label based on most recent mtime."""
    most_recent = 0.0
    try:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fname in files:
                if fname.startswith("."):
                    continue
                try:
                    mtime = os.path.getmtime(os.path.join(root, fname))
                    if mtime > most_recent:
                        most_recent = mtime
                except OSError:
                    pass
    except OSError:
        return "unknown"

    if most_recent == 0.0:
        return "never"

    age = time.time() - most_recent
    if age < 86400:
        return "today"
    days = int(age / 86400)
    if days < 7:
        return f"{days}d ago"
    weeks = int(days / 7)
    return f"{weeks}w ago"


# ── Last-synced formatter ────────────────────────────────────────────────

def _format_synced(iso_ts):
    if not iso_ts:
        return "never"
    try:
        return datetime.fromisoformat(iso_ts).astimezone().strftime("%-I:%M %p").lower()
    except ValueError:
        return iso_ts


def _relative_synced(iso_ts):
    """Return relative time string for a last_synced ISO timestamp."""
    if not iso_ts:
        return "never"
    try:
        ts = datetime.fromisoformat(iso_ts).timestamp()
    except ValueError:
        return iso_ts
    age = time.time() - ts
    if age < 60:
        return "just now"
    if age < 3600:
        return f"{int(age / 60)}m ago"
    if age < 86400:
        return f"{int(age / 3600)}h ago"
    days = int(age / 86400)
    if days < 7:
        return f"{days}d ago"
    return f"{int(days / 7)}w ago"


# ── Sidebar HTML ─────────────────────────────────────────────────────────

def _sidebar_html(projects, active_name=None):
    """Render the persistent left sidebar."""

    def nav_link(label, href, icon=""):
        is_active = request.path == href
        bg = "rgba(255,255,255,0.07)" if is_active else "transparent"
        weight = "600" if is_active else "400"
        return (
            f"<a href='{href}' style='display:block;padding:6px 12px;border-radius:6px;"
            f"background:{bg};color:rgba(255,255,255,0.75);text-decoration:none;"
            f"font-size:12px;font-weight:{weight};white-space:nowrap;overflow:hidden;"
            f"text-overflow:ellipsis;'>{icon}{label}</a>"
        )

    views_block = (
        "<div style='margin-bottom:20px;'>"
        "<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.3);"
        "letter-spacing:0.08em;text-transform:uppercase;padding:0 12px;margin-bottom:6px;'>"
        "Views</div>"
        + nav_link("Dashboard", "/")
        + nav_link("Activity Feed", "/feed")
        + "</div>"
    )

    project_rows = []
    for p in projects:
        color = _project_color(p["name"])
        recency = _project_recency(p["path"])
        is_active = p["name"] == active_name
        border = f"border-left:3px solid {color}" if is_active else "border-left:3px solid transparent"
        bg = "rgba(255,255,255,0.06)" if is_active else "transparent"
        href = f"/project/{p['name']}"
        project_rows.append(
            f"<a href='{href}' style='display:flex;align-items:center;gap:8px;padding:6px 12px;"
            f"border-radius:6px;background:{bg};{border};text-decoration:none;"
            f"color:rgba(255,255,255,0.75);'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{color};"
            f"flex-shrink:0;'></span>"
            f"<span style='flex:1;font-size:12px;white-space:nowrap;overflow:hidden;"
            f"text-overflow:ellipsis;'>{p['name']}</span>"
            f"<span style='font-size:10px;color:rgba(255,255,255,0.3);flex-shrink:0;'>"
            f"{recency}</span>"
            f"</a>"
        )

    projects_block = (
        "<div>"
        "<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.3);"
        "letter-spacing:0.08em;text-transform:uppercase;padding:0 12px;margin-bottom:6px;'>"
        "Projects</div>"
        + "".join(project_rows)
        + "</div>"
    )

    return (
        "<div style='width:200px;min-width:200px;height:100vh;position:sticky;top:0;"
        "background:#0A0F1E;border-right:1px solid rgba(255,255,255,0.07);"
        "display:flex;flex-direction:column;padding:20px 0;box-sizing:border-box;overflow-y:auto;'>"
        "<div style='font-size:13px;font-weight:700;color:#EDE8E0;padding:0 14px;margin-bottom:24px;"
        "letter-spacing:-0.01em;'>Solo Companion</div>"
        + views_block
        + projects_block
        + "</div>"
    )


# ── Page layout wrapper ──────────────────────────────────────────────────

def _page(sidebar_html, main_html, title="Solo Companion"):
    return (
        "<!DOCTYPE html>"
        "<html lang='en'><head><meta charset='UTF-8'>"
        f"<title>{title}</title></head>"
        "<body style='font-family:-apple-system,sans-serif;background:#0F1729;color:#EDE8E0;"
        "margin:0;display:flex;min-height:100vh;'>"
        + sidebar_html
        + f"<div style='flex:1;padding:48px 40px;min-width:0;'>{main_html}</div>"
        "</body></html>"
    )


# ── Helpers ──────────────────────────────────────────────────────────────

def _get_active_projects(conn):

    return conn.execute(
        "SELECT id, name, path, is_active FROM projects WHERE is_active = 1 ORDER BY name"
    ).fetchall()


def _open_duration(iso_ts):
    """Return human duration string from an ISO timestamp to now."""
    if not iso_ts:
        return "?"
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(iso_ts)
        days = age.days
        if days == 0:
            return "today"
        if days < 7:
            return f"{days}d"
        return f"{int(days / 7)}w"
    except ValueError:
        return "?"


def _blocked_card(conn, projects_by_id):
    """Render the Blocked needs-attention card, or '' if no blocked slices."""
    rows = conn.execute(
        "SELECT slice_id, name, notes, last_modified, project_id "
        "FROM slices WHERE is_blocked = 1 ORDER BY last_modified ASC"
    ).fetchall()

    if not rows:
        return ""

    item_html = []
    for r in rows:
        proj = projects_by_id.get(r["project_id"], {})
        proj_name = proj.get("name", "unknown")
        color = _project_color(proj_name)
        duration = _open_duration(r["last_modified"])
        reason = (r["notes"] or "").strip()
        if len(reason) > 80:
            reason = reason[:77] + "…"
        item_html.append(
            f"<div style='padding:10px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.04);cursor:pointer;'>"
            f"<span style='font-family:SF Mono,monospace;font-size:11px;"
            f"color:rgba(255,255,255,0.4);min-width:56px;'>{r['slice_id']}</span>"
            f"<span style='flex:1;font-size:12px;color:rgba(255,255,255,0.7);'>"
            f"{reason or r['name']}</span>"
            f"<span style='display:flex;align-items:center;gap:5px;flex-shrink:0;'>"
            f"<span style='width:6px;height:6px;border-radius:50%;background:{color};'></span>"
            f"<span style='font-size:11px;color:rgba(255,255,255,0.35);white-space:nowrap;'>"
            f"{proj_name} · {duration}</span>"
            f"</span></div>"
        )

    count = len(rows)
    return (
        "<div style='background:rgba(220,38,38,0.07);border:1px solid rgba(220,38,38,0.2);"
        "border-radius:10px;margin-bottom:16px;overflow:hidden;'>"
        "<div style='padding:10px 16px;border-bottom:1px solid rgba(220,38,38,0.15);"
        "display:flex;align-items:center;gap:8px;'>"
        "<span style='color:#EF4444;font-size:13px;font-weight:600;'>Blocked</span>"
        f"<span style='background:rgba(220,38,38,0.2);color:#EF4444;font-size:11px;"
        f"padding:1px 7px;border-radius:10px;font-weight:600;'>{count}</span>"
        "</div>"
        + "".join(item_html)
        + "</div>"
    )


def _bucket_section(header, rows_html):
    """Shared container for dashboard data buckets (Phases, Deliverables, Slices)."""
    return (
        "<div style='margin-bottom:24px;'>"
        f"<div style='font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);"
        f"letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;'>{header}</div>"
        "<div style='border:1px solid rgba(255,255,255,0.08);border-radius:10px;overflow:hidden;'>"
        + "".join(rows_html)
        + "</div></div>"
    )


def _status_pill(status):
    """Return a small inline status badge."""
    colors = {
        "In Progress": ("#3B82F6", "rgba(59,130,246,0.15)"),
        "In QA":       ("#8B5CF6", "rgba(139,92,246,0.15)"),
        "In Test":     ("#0D9488", "rgba(13,148,136,0.15)"),
        "Ready":       ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"),
        "Blocked":     ("#EF4444", "rgba(220,38,38,0.15)"),
        "Done":        ("#22C55E", "rgba(34,197,94,0.12)"),
        "Defined":     ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"),
        "Accepted":    ("#22C55E", "rgba(34,197,94,0.12)"),
        "Active":      ("#3B82F6", "rgba(59,130,246,0.15)"),
        "Planning":    ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"),
    }
    text_color, bg = colors.get(status or "", ("rgba(255,255,255,0.35)", "rgba(255,255,255,0.06)"))
    return (
        f"<span style='font-size:10px;padding:2px 7px;border-radius:8px;"
        f"background:{bg};color:{text_color};white-space:nowrap;flex-shrink:0;'>"
        f"{status or '—'}</span>"
    )


def _phases_bucket(conn, projects_by_id):
    """Render active phases (not Done/Cancelled) with slice progress bars."""
    phases = conn.execute(
        "SELECT id, name, status, project_id FROM phases "
        "WHERE status NOT IN ('Done', 'Cancelled') "
        "ORDER BY project_id, name"
    ).fetchall()

    if not phases:
        return ""

    rows = []
    for ph in phases:
        proj = projects_by_id.get(ph["project_id"], {})
        proj_name = proj.get("name", "unknown")
        color = _project_color(proj_name)

        # Extract phase number from "Phase N · Name" to match slices.phase = "N"
        parts = ph["name"].split(" ")
        phase_num = parts[1] if len(parts) > 1 else ph["name"]

        total = conn.execute(
            "SELECT COUNT(*) FROM slices WHERE project_id = ? AND phase = ?",
            (ph["project_id"], phase_num)
        ).fetchone()[0]
        done = conn.execute(
            "SELECT COUNT(*) FROM slices WHERE project_id = ? AND phase = ? AND status = 'Done'",
            (ph["project_id"], phase_num)
        ).fetchone()[0]

        pct = int(done / total * 100) if total > 0 else 0
        phase_display = ph["name"].split(" · ", 1)[1] if " · " in ph["name"] else ph["name"]

        rows.append(
            f"<div style='padding:12px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer;'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{color};"
            f"flex-shrink:0;'></span>"
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.35);margin-bottom:2px;'>"
            f"{proj_name}</div>"
            f"<div style='font-size:13px;color:rgba(255,255,255,0.8);'>{phase_display}</div>"
            f"</div>"
            f"{_status_pill(ph['status'])}"
            f"<div style='flex-shrink:0;text-align:right;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.35);margin-bottom:4px;'>"
            f"{done}/{total}</div>"
            f"<div style='width:80px;height:4px;background:rgba(255,255,255,0.08);"
            f"border-radius:2px;overflow:hidden;'>"
            f"<div style='width:{pct}%;height:100%;background:{color};border-radius:2px;'>"
            f"</div></div></div></div>"
        )

    return _bucket_section("Phases", rows)


def _deliverables_bucket(conn, projects_by_id):
    """Render active deliverables (not Done/Cancelled) across all projects."""
    deliverables = conn.execute(
        "SELECT deliverable_id, name, status, project_id FROM deliverables "
        "WHERE status NOT IN ('Done', 'Cancelled') "
        "ORDER BY project_id, deliverable_id"
    ).fetchall()

    if not deliverables:
        return ""

    rows = []
    for d in deliverables:
        proj = projects_by_id.get(d["project_id"], {})
        proj_name = proj.get("name", "unknown")
        color = _project_color(proj_name)
        rows.append(
            f"<div style='padding:12px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer;'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{color};"
            f"flex-shrink:0;'></span>"
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.35);margin-bottom:2px;'>"
            f"{proj_name} · {d['deliverable_id']}</div>"
            f"<div style='font-size:13px;color:rgba(255,255,255,0.8);'>{d['name']}</div>"
            f"</div>"
            f"{_status_pill(d['status'])}"
            f"</div>"
        )

    return _bucket_section("Deliverables", rows)


def _slices_bucket(conn, projects_by_id):
    """Render in-flight slices; if none, show next Ready slices as up-next."""
    in_flight = conn.execute(
        "SELECT slice_id, name, status, project_id FROM slices "
        "WHERE status IN ('In Progress', 'In QA', 'In Test') "
        "ORDER BY project_id, slice_id"
    ).fetchall()

    if in_flight:
        rows_data = list(in_flight)
        header_label = "Slices"
    else:
        # Nothing in flight — show next Ready slices as "up next"
        rows_data = conn.execute(
            "SELECT slice_id, name, status, project_id FROM slices "
            "WHERE status = 'Ready' ORDER BY project_id, slice_id LIMIT 10"
        ).fetchall()
        header_label = "Slices — Up Next"

    if not rows_data:
        return ""

    rows = []
    for s in rows_data:
        proj = projects_by_id.get(s["project_id"], {})
        proj_name = proj.get("name", "unknown")
        color = _project_color(proj_name)
        rows.append(
            f"<div style='padding:12px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer;'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{color};"
            f"flex-shrink:0;'></span>"
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.35);margin-bottom:2px;'>"
            f"{proj_name} · {s['slice_id']}</div>"
            f"<div style='font-size:13px;color:rgba(255,255,255,0.8);'>{s['name']}</div>"
            f"</div>"
            f"{_status_pill(s['status'])}"
            f"</div>"
        )

    return _bucket_section(header_label, rows)


def _flagged_card(conn, projects_by_id):
    """Render the Flagged needs-attention card, or '' if nothing flagged."""
    # Union: handoff open-right-now items (flags table) + stale in-progress slices
    rows = conn.execute("""
        SELECT f.text AS reason, f.object_type, f.object_id, f.project_id
        FROM flags f
        UNION ALL
        SELECT s.flagged_reason, 'slice', s.slice_id, s.project_id
        FROM slices s WHERE s.is_flagged = 1
        ORDER BY project_id
    """).fetchall()

    if not rows:
        return ""

    item_html = []
    for r in rows:
        proj = projects_by_id.get(r["project_id"], {})
        proj_name = proj.get("name", "unknown")
        color = _project_color(proj_name)
        reason = (r["reason"] or "").strip()
        if len(reason) > 80:
            reason = reason[:77] + "…"
        obj_label = ""
        if r["object_type"] == "slice" and r["object_id"]:
            obj_label = (
                f"<span style='font-family:SF Mono,monospace;font-size:10px;"
                f"color:rgba(255,255,255,0.35);margin-left:6px;'>{r['object_id']}</span>"
            )
        item_html.append(
            f"<div style='padding:10px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.04);cursor:pointer;'>"
            f"<span style='flex:1;font-size:12px;color:rgba(255,255,255,0.7);'>"
            f"{reason}</span>"
            f"{obj_label}"
            f"<span style='display:flex;align-items:center;gap:5px;flex-shrink:0;'>"
            f"<span style='width:6px;height:6px;border-radius:50%;background:{color};'></span>"
            f"<span style='font-size:11px;color:rgba(255,255,255,0.35);white-space:nowrap;'>"
            f"{proj_name}</span>"
            f"</span></div>"
        )

    count = len(rows)
    return (
        "<div style='background:rgba(217,119,6,0.07);border:1px solid rgba(217,119,6,0.2);"
        "border-radius:10px;margin-bottom:16px;overflow:hidden;'>"
        "<div style='padding:10px 16px;border-bottom:1px solid rgba(217,119,6,0.15);"
        "display:flex;align-items:center;gap:8px;'>"
        "<span style='color:#F59E0B;font-size:13px;font-weight:600;'>Flagged</span>"
        f"<span style='background:rgba(217,119,6,0.2);color:#F59E0B;font-size:11px;"
        f"padding:1px 7px;border-radius:10px;font-weight:600;'>{count}</span>"
        "</div>"
        + "".join(item_html)
        + "</div>"
    )


# ── Routes ───────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    discover_projects()
    conn = get_conn()

    projects = _get_active_projects(conn)
    last_synced = get_last_synced()
    projects_by_id = {p["id"]: dict(p) for p in projects}
    blocked = _blocked_card(conn, projects_by_id)
    flagged = _flagged_card(conn, projects_by_id)
    phases = _phases_bucket(conn, projects_by_id)
    deliverables = _deliverables_bucket(conn, projects_by_id)
    slices = _slices_bucket(conn, projects_by_id)
    conn.close()

    project_count = len(projects)
    synced_label = _relative_synced(last_synced)

    top_bar = (
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "margin-bottom:32px;'>"
        "<div>"
        "<h1 style='font-size:20px;font-weight:600;margin:0 0 4px;'>Dashboard</h1>"
        f"<p style='font-size:12px;color:rgba(255,255,255,0.4);margin:0;'>"
        f"{project_count} active project{'s' if project_count != 1 else ''} "
        f"· synced {synced_label}</p>"
        "</div>"
        "<form method='POST' action='/sync' style='margin:0;'>"
        "<button type='submit' style='background:rgba(255,255,255,0.07);border:1px solid "
        "rgba(255,255,255,0.12);color:rgba(255,255,255,0.75);font-size:12px;padding:6px 14px;"
        "border-radius:6px;cursor:pointer;font-family:-apple-system,sans-serif;'>"
        "↻ Refresh</button>"
        "</form>"
        "</div>"
    )

    main_html = (
        top_bar
        + blocked
        + flagged
        + phases
        + deliverables
        + slices
    )

    sidebar = _sidebar_html(projects)
    return _page(sidebar, main_html)


@app.route("/project/<name>")
def project_detail(name):
    conn = get_conn()
    projects = _get_active_projects(conn)
    conn.close()

    color = _project_color(name)
    main_html = (
        f"<h1 style='font-size:20px;font-weight:600;margin:0 0 6px;'>{name}</h1>"
        f"<p style='font-size:13px;color:rgba(255,255,255,0.4);margin:0;'>"
        f"Project detail arrives in SL-014 onwards.</p>"
    )

    sidebar = _sidebar_html(projects, active_name=name)
    return _page(sidebar, main_html, title=f"Solo Companion — {name}")


@app.route("/feed")
def activity_feed():
    conn = get_conn()
    projects = _get_active_projects(conn)
    conn.close()

    main_html = (
        "<h1 style='font-size:20px;font-weight:600;margin:0 0 6px;'>Activity Feed</h1>"
        "<p style='font-size:13px;color:rgba(255,255,255,0.4);margin:0;'>"
        "Activity feed arrives in Phase 3.</p>"
    )

    sidebar = _sidebar_html(projects)
    return _page(sidebar, main_html, title="Solo Companion — Activity Feed")


@app.route("/sync", methods=["POST"])
def sync():
    discover_projects()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
