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
SL-011: Overlay — Slice panel. All 17 spec fields, quality gates derived
        from status, backdrop + ✕ dismiss, "Take me to this project" footer.
"""

import json
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

def _page(sidebar_html, main_html, title="Solo Companion", padded=True):
    overlay_js = (
        "<div id='overlay-backdrop' onclick='closeOverlay()' "
        "style='display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);"
        "backdrop-filter:blur(2px);z-index:200;justify-content:center;align-items:center;'>"
        "<div id='overlay-root' onclick='event.stopPropagation()'></div>"
        "</div>"
        "<script>"
        "function openSliceOverlay(pid,sid){"
        "  var from=encodeURIComponent(window.location.pathname);"
        "  fetch('/overlay/slice/'+pid+'/'+sid+'?from='+from)"
        "  .then(function(r){return r.text()})"
        "  .then(function(h){"
        "    document.getElementById('overlay-root').innerHTML=h;"
        "    document.getElementById('overlay-backdrop').style.display='flex';"
        "  });}"
        "function openDeliverableOverlay(pid,did){"
        "  var from=encodeURIComponent(window.location.pathname);"
        "  fetch('/overlay/deliverable/'+pid+'/'+did+'?from='+from)"
        "  .then(function(r){return r.text()})"
        "  .then(function(h){"
        "    document.getElementById('overlay-root').innerHTML=h;"
        "    document.getElementById('overlay-backdrop').style.display='flex';"
        "  });}"
        "function openPhaseOverlay(pid,phid){"
        "  var from=encodeURIComponent(window.location.pathname);"
        "  fetch('/overlay/phase/'+pid+'/'+phid+'?from='+from)"
        "  .then(function(r){return r.text()})"
        "  .then(function(h){"
        "    document.getElementById('overlay-root').innerHTML=h;"
        "    document.getElementById('overlay-backdrop').style.display='flex';"
        "  });}"
        "function closeOverlay(){"
        "  document.getElementById('overlay-backdrop').style.display='none';"
        "  document.getElementById('overlay-root').innerHTML='';}"
        "document.addEventListener('keydown',function(e){"
        "  if(e.key==='Escape')closeOverlay();});"
        "</script>"
    )
    return (
        "<!DOCTYPE html>"
        "<html lang='en'><head><meta charset='UTF-8'>"
        f"<title>{title}</title></head>"
        "<body style='font-family:-apple-system,sans-serif;background:#0F1729;color:#EDE8E0;"
        "margin:0;display:flex;min-height:100vh;'>"
        + sidebar_html
        + (
            f"<div style='flex:1;padding:48px 40px;min-width:0;'>{main_html}</div>"
            if padded else
            f"<div style='flex:1;min-width:0;display:flex;flex-direction:column;'>{main_html}</div>"
        )
        + overlay_js
        + "</body></html>"
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
        pid = r["project_id"]
        sid = r["slice_id"]
        item_html.append(
            f"<div onclick='openSliceOverlay({pid},\"{sid}\")' "
            f"style='padding:10px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.04);cursor:pointer;'>"
            f"<span style='font-family:SF Mono,monospace;font-size:11px;"
            f"color:rgba(255,255,255,0.4);min-width:56px;'>{sid}</span>"
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
        "Ready":       ("#7DD3FC", "rgba(14,165,233,0.12)"),
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
    """Render active phases (not Done/Cancelled, and not fully complete by slice count)."""
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

        # Skip phases where every slice is already Done — they're complete regardless of status field
        if total > 0 and done == total:
            continue

        pct = int(done / total * 100) if total > 0 else 0
        phid = ph["id"]
        ph_pid = ph["project_id"]
        rows.append(
            f"<div onclick='openPhaseOverlay({ph_pid},{phid})' "
            f"style='padding:12px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer;"
            f"transition:background 0.1s;' "
            f"onmouseover='this.style.background=\"rgba(255,255,255,0.03)\"' "
            f"onmouseout='this.style.background=\"transparent\"'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{color};"
            f"flex-shrink:0;'></span>"
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:2px;'>"
            f"{proj_name}</div>"
            f"<div style='font-size:13px;color:rgba(255,255,255,0.8);'>{ph['name']}</div>"
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
        pid = d["project_id"]
        did = d["deliverable_id"]
        rows.append(
            f"<div onclick='openDeliverableOverlay({pid},\"{did}\")' "
            f"style='padding:12px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer;"
            f"transition:background 0.1s;' "
            f"onmouseover='this.style.background=\"rgba(255,255,255,0.03)\"' "
            f"onmouseout='this.style.background=\"transparent\"'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{color};"
            f"flex-shrink:0;'></span>"
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:2px;'>"
            f"{proj_name} · {did}</div>"
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
        pid = s["project_id"]
        sid = s["slice_id"]
        rows.append(
            f"<div onclick='openSliceOverlay({pid},\"{sid}\")' "
            f"style='padding:12px 16px;display:flex;align-items:center;gap:12px;"
            f"border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer;"
            f"transition:background 0.1s;' "
            f"onmouseover='this.style.background=\"rgba(255,255,255,0.03)\"' "
            f"onmouseout='this.style.background=\"transparent\"'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{color};"
            f"flex-shrink:0;'></span>"
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:2px;'>"
            f"{proj_name} · {sid}</div>"
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


# ── Overlay helpers ─────────────────────────────────────────────────────

def _decode_list(val):
    """Decode a JSON-encoded list column, returning [] if null or invalid."""
    if not val:
        return []
    try:
        result = json.loads(val)
        return result if isinstance(result, list) else [str(result)]
    except (json.JSONDecodeError, TypeError):
        return [val]


def _ol_section(label, body_html):
    """Overlay section block with a muted label above."""
    if not body_html:
        return ""
    return (
        f"<div style='margin-bottom:24px;'>"
        f"<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.3);"
        f"letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;'>{label}</div>"
        f"{body_html}"
        f"</div>"
    )


def _ol_text(val):
    """Render a scalar text value for the overlay."""
    if not val:
        return ""
    escaped = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines = escaped.replace("\n", "<br>")
    return f"<p style='font-size:13px;color:rgba(255,255,255,0.75);margin:0;line-height:1.6;'>{lines}</p>"


def _ol_list(items):
    """Render a list of strings as bullet rows."""
    if not items:
        return ""
    bullets = "".join(
        f"<li style='font-size:12px;color:rgba(255,255,255,0.65);margin-bottom:4px;"
        f"line-height:1.5;'>{item.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</li>"
        for item in items
    )
    return f"<ul style='margin:0;padding-left:18px;'>{bullets}</ul>"


def _ol_anchor_grid(design, data, process, done_criteria):
    """Render the four-anchor 2×2 grid."""
    def cell(label, text):
        content = (text or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:12px;'>"
            f"<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.3);"
            f"letter-spacing:0.06em;text-transform:uppercase;margin-bottom:6px;'>{label}</div>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.7);line-height:1.5;'>{content}</div>"
            f"</div>"
        )

    # Done criteria: join list items as a summary, or use first item
    done_text = done_criteria[0] if done_criteria else None
    if len(done_criteria) > 1:
        done_text = f"{done_criteria[0]} (+{len(done_criteria)-1} more)"

    return (
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>"
        + cell("Design", design)
        + cell("Data", data)
        + cell("Process", process)
        + cell("Done", done_text)
        + "</div>"
    )


def _ol_gate(label, confirmed, detail=None):
    """Render one quality gate row."""
    icon = "✓" if confirmed else "○"
    icon_color = "#22C55E" if confirmed else "rgba(255,255,255,0.25)"
    label_color = "rgba(255,255,255,0.7)" if confirmed else "rgba(255,255,255,0.4)"
    detail_html = ""
    if detail:
        detail_html = (
            f"<span style='font-size:11px;color:rgba(255,255,255,0.35);margin-left:6px;'>"
            f"— {detail}</span>"
        )
    return (
        f"<div style='display:flex;align-items:center;gap:10px;padding:6px 0;"
        f"border-bottom:1px solid rgba(255,255,255,0.04);'>"
        f"<span style='color:{icon_color};font-size:14px;width:16px;'>{icon}</span>"
        f"<span style='font-size:12px;color:{label_color};'>{label}</span>"
        f"{detail_html}"
        f"</div>"
    )


def _render_phase_overlay(ph, counts, deliverables, proj_name, from_project=None):
    """Build phase overlay panel HTML per sprint-01-dashboard.html phase overlay."""
    color = _project_color(proj_name)
    status = ph["status"] or "—"

    acceptance = _decode_list(ph["acceptance_criteria"])

    btn_href = f"/project/{proj_name}#progress"
    is_same_project = from_project and from_project == proj_name
    if is_same_project:
        footer_btn = (
            "<button disabled style='background:rgba(255,255,255,0.05);border:1px solid "
            "rgba(255,255,255,0.1);color:rgba(255,255,255,0.3);font-size:13px;padding:9px 18px;"
            "border-radius:8px;cursor:not-allowed;font-family:-apple-system,sans-serif;font-weight:600;'>"
            "Already on this project</button>"
        )
    else:
        footer_btn = (
            f"<a href='{btn_href}' style='display:inline-flex;align-items:center;gap:8px;"
            f"background:#2563EB;color:#fff;font-size:13px;padding:9px 18px;border-radius:8px;"
            f"text-decoration:none;font-family:-apple-system,sans-serif;font-weight:600;'>"
            f"Take me to this project →</a>"
        )

    def field_box(label, value):
        escaped = (value or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 12px;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.3);text-transform:uppercase;"
            f"letter-spacing:0.08em;font-weight:600;margin-bottom:4px;'>{label}</div>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.8);font-weight:500;line-height:1.4;'>"
            f"{escaped}</div></div>"
        )

    def full_field(text):
        if not text:
            return ""
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 12px;'>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.8);line-height:1.6;'>"
            f"{escaped.replace(chr(10), '<br>')}</div></div>"
        )

    def bullet_field(items):
        if not items:
            return ""
        bullets = "".join(
            f"<li style='font-size:12px;color:rgba(255,255,255,0.8);margin-bottom:4px;"
            f"line-height:1.5;'>"
            f"{item.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</li>"
            for item in items
        )
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 16px;'>"
            f"<ul style='margin:0;padding-left:16px;'>{bullets}</ul></div>"
        )

    def section(label, body):
        if not body:
            return ""
        return (
            f"<div style='margin-bottom:18px;'>"
            f"<div style='font-size:10px;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.1em;color:rgba(255,255,255,0.25);margin-bottom:8px;'>{label}</div>"
            f"{body}</div>"
        )

    _pill = {
        "In Progress": ("#93C5FD", "rgba(37,99,235,0.2)"),
        "In QA":       ("#C4B5FD", "rgba(124,58,237,0.2)"),
        "In Test":     ("#5EEAD4", "rgba(13,148,136,0.2)"),
        "Ready":       ("#7DD3FC", "rgba(14,165,233,0.12)"),
        "Done":        ("#86EFAC", "rgba(21,128,61,0.2)"),
        "Accepted":    ("#86EFAC", "rgba(21,128,61,0.2)"),
        "Defined":     ("rgba(255,255,255,0.5)", "rgba(255,255,255,0.08)"),
        "Blocked":     ("#FDA4AF", "rgba(190,18,60,0.25)"),
        "Planning":    ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"),
        "Active":      ("#93C5FD", "rgba(37,99,235,0.2)"),
    }
    stc, sbg = _pill.get(status, ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"))
    status_pill_html = (
        f"<span style='margin-left:auto;font-size:11px;font-weight:600;padding:3px 10px;"
        f"border-radius:20px;background:{sbg};color:{stc};'>{status}</span>"
    )

    # Slice progress: counts dict has keys Done/In Progress/In Test/In QA/Ready/etc.
    n_done    = counts.get("Done", 0)
    n_prog    = counts.get("In Progress", 0)
    n_test    = counts.get("In Test", 0) + counts.get("In QA", 0)
    n_ready   = counts.get("Ready", 0)
    n_total   = sum(counts.values())
    pct = int(n_done / n_total * 100) if n_total > 0 else 0

    def stat_box(label, count, text_color, bg_color, border_color):
        return (
            f"<div style='text-align:center;padding:6px;background:{bg_color};"
            f"border:1px solid {border_color};border-radius:6px;'>"
            f"<div style='font-size:16px;font-weight:700;color:{text_color};'>{count}</div>"
            f"<div style='font-size:9px;color:rgba(255,255,255,0.3);text-transform:uppercase;"
            f"letter-spacing:0.8px;'>{label}</div>"
            f"</div>"
        )

    progress_html = (
        f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
        f"border-radius:8px;padding:12px;'>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:8px;'>"
        f"<span style='font-size:12px;color:rgba(255,255,255,0.6);'>{n_done} of {n_total} Done</span>"
        f"<span style='font-size:12px;color:rgba(255,255,255,0.3);'>{pct}%</span>"
        f"</div>"
        f"<div style='height:5px;background:rgba(255,255,255,0.08);border-radius:3px;"
        f"overflow:hidden;margin-bottom:12px;'>"
        f"<div style='width:{pct}%;height:100%;background:#2563EB;border-radius:3px;'></div>"
        f"</div>"
        f"<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:6px;'>"
        + stat_box("Done",        n_done, "#5EEAD4", "rgba(13,148,136,0.12)", "rgba(13,148,136,0.2)")
        + stat_box("In Progress", n_prog, "#93C5FD", "rgba(37,99,235,0.1)",   "rgba(37,99,235,0.2)")
        + stat_box("In Test",     n_test, "#C4B5FD", "rgba(124,58,237,0.1)",  "rgba(124,58,237,0.2)")
        + stat_box("Ready",       n_ready,"#7DD3FC", "rgba(255,255,255,0.04)","rgba(255,255,255,0.08)")
        + "</div></div>"
    )

    # Deliverables list
    def deliv_row(d):
        ds = d["status"] or "—"
        dc, db_ = _pill.get(ds, ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"))
        name_esc = d["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"padding:8px 12px;background:rgba(255,255,255,0.04);"
            f"border:1px solid rgba(255,255,255,0.07);border-radius:7px;'>"
            f"<span style='font-size:12px;color:rgba(255,255,255,0.7);'>{name_esc}</span>"
            f"<span style='font-size:10px;font-weight:600;padding:2px 7px;border-radius:4px;"
            f"background:{db_};color:{dc};white-space:nowrap;flex-shrink:0;margin-left:8px;'>"
            f"{ds}</span></div>"
        )

    deliverables_html = (
        f"<div style='display:flex;flex-direction:column;gap:6px;'>"
        + "".join(deliv_row(d) for d in deliverables)
        + "</div>"
    ) if deliverables else ""

    details_html = (
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;'>"
        + field_box("Status", status)
        + field_box("Question answered", ph["question_answered"])
        + "</div>"
    )

    return (
        "<div style='background:#152035;border:1px solid rgba(255,255,255,0.12);border-radius:14px;"
        "width:600px;max-width:90vw;max-height:88vh;display:flex;flex-direction:column;"
        "overflow:hidden;box-shadow:0 24px 64px rgba(0,0,0,0.6);'>"

        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "padding:20px 24px;border-bottom:1px solid rgba(255,255,255,0.08);flex-shrink:0;'>"
        "<div style='display:flex;align-items:center;gap:10px;min-width:0;'>"
        "<span style='font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;"
        "padding:3px 8px;border-radius:4px;background:rgba(124,58,237,0.2);color:#C4B5FD;"
        "flex-shrink:0;'>Phase</span>"
        f"<span style='font-size:15px;font-weight:700;color:#fff;white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis;'>{ph['name']}</span>"
        "</div>"
        "<button onclick='closeOverlay()' style='width:28px;height:28px;border-radius:6px;"
        "border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);"
        "color:rgba(255,255,255,0.5);font-size:14px;cursor:pointer;display:flex;"
        "align-items:center;justify-content:center;flex-shrink:0;margin-left:12px;"
        "font-family:-apple-system,sans-serif;line-height:1;'>✕</button>"
        "</div>"

        "<div style='padding:24px;overflow-y:auto;flex:1;'>"

        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:20px;'>"
        f"<div style='width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;'></div>"
        f"<span style='font-size:12px;font-weight:600;color:rgba(255,255,255,0.5);"
        f"font-family:\"SF Mono\",\"Fira Code\",monospace;'>{proj_name}</span>"
        f"{status_pill_html}"
        f"</div>"

        + section("Details", details_html)
        + section("Plain language description", full_field(ph["plain_description"]))
        + section("Technical description", full_field(ph["technical_description"]))
        + section("Acceptance criteria", bullet_field(acceptance))
        + section("Slice progress", progress_html)
        + section("Deliverables", deliverables_html)
        + (section("Notes", full_field(ph["notes"])) if ph["notes"] else "")

        + "</div>"

        + f"<div style='padding:16px 24px;border-top:1px solid rgba(255,255,255,0.08);"
        f"display:flex;align-items:center;justify-content:space-between;flex-shrink:0;'>"
        f"<span style='font-size:11px;color:rgba(255,255,255,0.25);'>Phase · {proj_name}</span>"
        f"{footer_btn}"
        f"</div>"

        + "</div>"
    )


def _render_deliverable_overlay(d, slices, proj_name, from_project=None):
    """Build deliverable overlay panel HTML per sprint-01-dashboard.html deliverable overlay."""
    color = _project_color(proj_name)
    status = d["status"] or "—"

    acceptance = _decode_list(d["acceptance_criteria"])
    builder_conf = _decode_list(d["builder_confirmation"])
    references = _decode_list(d["references_list"])
    builder_confirmed = bool(builder_conf) and builder_conf[0] != "Pending build"

    # Footer button
    btn_href = f"/project/{proj_name}#progress"
    is_same_project = from_project and from_project == proj_name
    if is_same_project:
        footer_btn = (
            "<button disabled style='background:rgba(255,255,255,0.05);border:1px solid "
            "rgba(255,255,255,0.1);color:rgba(255,255,255,0.3);font-size:13px;padding:9px 18px;"
            "border-radius:8px;cursor:not-allowed;font-family:-apple-system,sans-serif;font-weight:600;'>"
            "Already on this project</button>"
        )
    else:
        footer_btn = (
            f"<a href='{btn_href}' style='display:inline-flex;align-items:center;gap:8px;"
            f"background:#2563EB;color:#fff;font-size:13px;padding:9px 18px;border-radius:8px;"
            f"text-decoration:none;font-family:-apple-system,sans-serif;font-weight:600;'>"
            f"Take me to this project →</a>"
        )

    def field_box(label, value):
        escaped = (value or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 12px;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.3);text-transform:uppercase;"
            f"letter-spacing:0.08em;font-weight:600;margin-bottom:4px;'>{label}</div>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.8);font-weight:500;line-height:1.4;'>"
            f"{escaped}</div></div>"
        )

    def full_field(text):
        if not text:
            return ""
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 12px;'>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.8);line-height:1.6;'>"
            f"{escaped.replace(chr(10), '<br>')}</div></div>"
        )

    def bullet_field(items):
        if not items:
            return ""
        bullets = "".join(
            f"<li style='font-size:12px;color:rgba(255,255,255,0.8);margin-bottom:4px;"
            f"line-height:1.5;'>"
            f"{item.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</li>"
            for item in items
        )
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 16px;'>"
            f"<ul style='margin:0;padding-left:16px;'>{bullets}</ul></div>"
        )

    def section(label, body):
        if not body:
            return ""
        return (
            f"<div style='margin-bottom:18px;'>"
            f"<div style='font-size:10px;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.1em;color:rgba(255,255,255,0.25);margin-bottom:8px;'>{label}</div>"
            f"{body}</div>"
        )

    _pill = {
        "In Progress": ("#93C5FD", "rgba(37,99,235,0.2)"),
        "In QA":       ("#C4B5FD", "rgba(124,58,237,0.2)"),
        "In Test":     ("#5EEAD4", "rgba(13,148,136,0.2)"),
        "Ready":       ("#7DD3FC", "rgba(14,165,233,0.12)"),
        "Done":        ("#86EFAC", "rgba(21,128,61,0.2)"),
        "Accepted":    ("#86EFAC", "rgba(21,128,61,0.2)"),
        "Defined":     ("rgba(255,255,255,0.5)", "rgba(255,255,255,0.08)"),
        "Blocked":     ("#FDA4AF", "rgba(190,18,60,0.25)"),
    }
    stc, sbg = _pill.get(status, ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"))
    status_pill_html = (
        f"<span style='margin-left:auto;font-size:11px;font-weight:600;padding:3px 10px;"
        f"border-radius:20px;background:{sbg};color:{stc};'>{status}</span>"
    )

    # Slice list
    def slice_row(s):
        ss = s["status"] or "—"
        sc, sb = _pill.get(ss, ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"))
        name_esc = s["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"padding:8px 12px;background:rgba(255,255,255,0.04);"
            f"border:1px solid rgba(255,255,255,0.07);border-radius:7px;'>"
            f"<span style='font-size:12px;color:rgba(255,255,255,0.7);"
            f"font-family:\"SF Mono\",\"Fira Code\",monospace;'>{s['slice_id']} · {name_esc}</span>"
            f"<span style='font-size:10px;font-weight:600;padding:2px 7px;border-radius:4px;"
            f"background:{sb};color:{sc};white-space:nowrap;flex-shrink:0;margin-left:8px;'>"
            f"{ss}</span></div>"
        )

    slices_html = (
        f"<div style='display:flex;flex-direction:column;gap:6px;'>"
        + "".join(slice_row(s) for s in slices)
        + "</div>"
    ) if slices else ""

    # Builder confirmation
    if builder_confirmed:
        builder_html = full_field("Confirmed")
    else:
        builder_html = (
            "<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            "border-radius:8px;padding:10px 12px;'>"
            "<div style='font-size:12px;color:rgba(255,255,255,0.3);line-height:1.6;'>"
            "Pending — all slices must reach Done before confirmation</div></div>"
        )

    details_html = (
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;'>"
        + field_box("Type", d["type"])
        + field_box("Phase", f"Phase {d['phase']}" if d["phase"] else None)
        + "</div>"
    )

    return (
        "<div style='background:#152035;border:1px solid rgba(255,255,255,0.12);border-radius:14px;"
        "width:600px;max-width:90vw;max-height:88vh;display:flex;flex-direction:column;"
        "overflow:hidden;box-shadow:0 24px 64px rgba(0,0,0,0.6);'>"

        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "padding:20px 24px;border-bottom:1px solid rgba(255,255,255,0.08);flex-shrink:0;'>"
        "<div style='display:flex;align-items:center;gap:10px;min-width:0;'>"
        "<span style='font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;"
        "padding:3px 8px;border-radius:4px;background:rgba(13,148,136,0.2);color:#5EEAD4;"
        "flex-shrink:0;'>Deliverable</span>"
        f"<span style='font-size:15px;font-weight:700;color:#fff;white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis;'>{d['name']}</span>"
        "</div>"
        "<button onclick='closeOverlay()' style='width:28px;height:28px;border-radius:6px;"
        "border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);"
        "color:rgba(255,255,255,0.5);font-size:14px;cursor:pointer;display:flex;"
        "align-items:center;justify-content:center;flex-shrink:0;margin-left:12px;"
        "font-family:-apple-system,sans-serif;line-height:1;'>✕</button>"
        "</div>"

        "<div style='padding:24px;overflow-y:auto;flex:1;'>"

        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:20px;'>"
        f"<div style='width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;'></div>"
        f"<span style='font-size:12px;font-weight:600;color:rgba(255,255,255,0.5);"
        f"font-family:\"SF Mono\",\"Fira Code\",monospace;'>{proj_name}</span>"
        f"{status_pill_html}"
        f"</div>"

        + section("Details", details_html)
        + section("Plain language description", full_field(d["plain_description"]))
        + section("Technical description", full_field(d["technical_description"]))
        + section("Acceptance criteria", bullet_field(acceptance))
        + section("Slices", slices_html)
        + section("Builder confirmation", builder_html)
        + (section("References", bullet_field(references)) if references else "")
        + (section("Depends on", full_field(d["depends_on"]))
           if d["depends_on"] and d["depends_on"].lower() != "none" else "")
        + (section("Notes", full_field(d["notes"])) if d["notes"] else "")

        + "</div>"

        + f"<div style='padding:16px 24px;border-top:1px solid rgba(255,255,255,0.08);"
        f"display:flex;align-items:center;justify-content:space-between;flex-shrink:0;'>"
        f"<span style='font-size:11px;color:rgba(255,255,255,0.25);'>Deliverable · {proj_name}</span>"
        f"{footer_btn}"
        f"</div>"

        + "</div>"
    )


def _render_slice_overlay(s, proj_name, from_project=None):
    """Build the full slice overlay panel HTML — centered floating card per sprint-01-dashboard.html."""
    color = _project_color(proj_name)
    status = s["status"] or "—"
    is_done = status == "Done"
    is_qa = status in ("In QA", "In Test", "Done")

    done_criteria = _decode_list(s["done_criteria"])
    self_verif = _decode_list(s["self_verification"])
    builder_conf = _decode_list(s["builder_confirmation"])
    references = _decode_list(s["references_list"])

    builder_confirmed = bool(builder_conf) and builder_conf[0] != "Pending build"

    # Footer button
    btn_href = f"/project/{proj_name}#slices"
    is_same_project = from_project and from_project == proj_name
    if is_same_project:
        footer_btn = (
            "<button disabled style='background:rgba(255,255,255,0.05);border:1px solid "
            "rgba(255,255,255,0.1);color:rgba(255,255,255,0.3);font-size:13px;padding:9px 18px;"
            "border-radius:8px;cursor:not-allowed;font-family:-apple-system,sans-serif;font-weight:600;'>"
            "Already on this project</button>"
        )
    else:
        footer_btn = (
            f"<a href='{btn_href}' style='display:inline-flex;align-items:center;gap:8px;"
            f"background:#2563EB;color:#fff;font-size:13px;padding:9px 18px;border-radius:8px;"
            f"text-decoration:none;font-family:-apple-system,sans-serif;font-weight:600;'>"
            f"Take me to this project →</a>"
        )

    # Field box — used in 2-col grids
    def field_box(label, value, mono=False):
        val_style = 'font-family:"SF Mono","Fira Code",monospace;font-size:11px;' if mono else "font-size:12px;"
        escaped = (value or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 12px;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.3);text-transform:uppercase;"
            f"letter-spacing:0.08em;font-weight:600;margin-bottom:4px;'>{label}</div>"
            f"<div style='{val_style}color:rgba(255,255,255,0.8);font-weight:500;line-height:1.4;'>"
            f"{escaped}</div>"
            f"</div>"
        )

    # Full-width prose field
    def full_field(text):
        if not text:
            return ""
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 12px;'>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.8);line-height:1.6;'>"
            f"{escaped.replace(chr(10), '<br>')}</div>"
            f"</div>"
        )

    # Section: label above content
    def section(label, body):
        if not body:
            return ""
        return (
            f"<div style='margin-bottom:18px;'>"
            f"<div style='font-size:10px;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.1em;color:rgba(255,255,255,0.25);margin-bottom:8px;'>{label}</div>"
            f"{body}"
            f"</div>"
        )

    # Bullet list in a field box
    def bullet_field(items):
        if not items:
            return ""
        bullets = "".join(
            f"<li style='font-size:12px;color:rgba(255,255,255,0.8);margin-bottom:4px;"
            f"line-height:1.5;'>"
            f"{item.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</li>"
            for item in items
        )
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 16px;'>"
            f"<ul style='margin:0;padding-left:16px;'>{bullets}</ul></div>"
        )

    # Status pill colors matching design
    _pill_colors = {
        "In Progress": ("#93C5FD", "rgba(37,99,235,0.2)"),
        "In QA":       ("#C4B5FD", "rgba(124,58,237,0.2)"),
        "In Test":     ("#5EEAD4", "rgba(13,148,136,0.2)"),
        "Ready":       ("#7DD3FC", "rgba(14,165,233,0.12)"),
        "Blocked":     ("#FDA4AF", "rgba(190,18,60,0.25)"),
        "Done":        ("#86EFAC", "rgba(21,128,61,0.2)"),
    }
    stc, sbg = _pill_colors.get(status, ("rgba(255,255,255,0.4)", "rgba(255,255,255,0.06)"))
    status_pill_html = (
        f"<span style='margin-left:auto;font-size:11px;font-weight:600;padding:3px 10px;"
        f"border-radius:20px;background:{sbg};color:{stc};'>{status}</span>"
    )

    # Overlay header title — slice_id · name, truncated if needed
    overlay_title = f"{s['slice_id']} · {s['name']}"
    if len(overlay_title) > 52:
        overlay_title = overlay_title[:49] + "…"

    # Details grid (2-col)
    details_html = (
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;'>"
        + field_box("Deliverable", s["deliverable_ref"])
        + field_box("Phase", f"Phase {s['phase']}" if s["phase"] else None)
        + field_box("Slice ID", s["slice_id"], mono=True)
        + field_box("Last updated", s["last_modified"], mono=True)
        + "</div>"
    )

    # Four Anchors grid (2-col)
    done_text = done_criteria[0] if done_criteria else None
    if len(done_criteria) > 1:
        done_text = f"{done_criteria[0]} (+{len(done_criteria)-1} more)"
    anchors_html = (
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;'>"
        + field_box("Design anchor", s["design_anchor"])
        + field_box("Data anchor", s["data_anchor"])
        + field_box("Process anchor", s["process_anchor"])
        + field_box("Done anchor", done_text)
        + "</div>"
    )

    # Quality Gates grid (2-col)
    def gate_field(label, confirmed, pending_text="Pending"):
        val = "Confirmed" if confirmed else pending_text
        val_color = "#22C55E" if confirmed else "rgba(255,255,255,0.3)"
        return (
            f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:8px;padding:10px 12px;'>"
            f"<div style='font-size:10px;color:rgba(255,255,255,0.3);text-transform:uppercase;"
            f"letter-spacing:0.08em;font-weight:600;margin-bottom:4px;'>{label}</div>"
            f"<div style='font-size:12px;color:{val_color};font-weight:500;line-height:1.4;'>{val}</div>"
            f"</div>"
        )

    review_text = s["review_url"] if s["review_url"] else "Available when Done"
    gates_html = (
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;'>"
        + gate_field("Code review", is_done)
        + gate_field("QA sign-off", is_qa)
        + gate_field("Review link", bool(s["review_url"]), review_text)
        + gate_field("Builder confirmation", builder_confirmed)
        + "</div>"
    )

    return (
        # Floating card — centered by backdrop flex
        "<div style='background:#152035;border:1px solid rgba(255,255,255,0.12);border-radius:14px;"
        "width:600px;max-width:90vw;max-height:88vh;display:flex;flex-direction:column;"
        "overflow:hidden;box-shadow:0 24px 64px rgba(0,0,0,0.6);'>"

        # Header
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "padding:20px 24px;border-bottom:1px solid rgba(255,255,255,0.08);flex-shrink:0;'>"
        "<div style='display:flex;align-items:center;gap:10px;min-width:0;'>"
        "<span style='font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;"
        "padding:3px 8px;border-radius:4px;background:rgba(37,99,235,0.2);color:#93C5FD;"
        "flex-shrink:0;'>Slice</span>"
        f"<span style='font-size:15px;font-weight:700;color:#fff;white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis;'>{overlay_title}</span>"
        "</div>"
        "<button onclick='closeOverlay()' style='width:28px;height:28px;border-radius:6px;"
        "border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);"
        "color:rgba(255,255,255,0.5);font-size:14px;cursor:pointer;display:flex;"
        "align-items:center;justify-content:center;flex-shrink:0;margin-left:12px;"
        "font-family:-apple-system,sans-serif;line-height:1;'>✕</button>"
        "</div>"

        # Body (scrollable)
        "<div style='padding:24px;overflow-y:auto;flex:1;'>"

        # Project row: dot · name · status pill
        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:20px;'>"
        f"<div style='width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;'></div>"
        f"<span style='font-size:12px;font-weight:600;color:rgba(255,255,255,0.5);"
        f"font-family:\"SF Mono\",\"Fira Code\",monospace;'>{proj_name}</span>"
        f"{status_pill_html}"
        f"</div>"

        + section("Details", details_html)
        + section("Plain language description", full_field(s["plain_description"]))
        + section("Technical description", full_field(s["technical_description"]))
        + section("Done criteria", bullet_field(done_criteria))
        + section("Four Anchors", anchors_html)
        + section("Quality Gates", gates_html)
        + (section("Self-verification checklist", bullet_field(self_verif)) if self_verif else "")
        + (section("References", bullet_field(references)) if references else "")
        + (section("Depends on", full_field(s["depends_on"]))
           if s["depends_on"] and s["depends_on"].lower() != "none" else "")
        + (section("Notes", full_field(s["notes"])) if s["notes"] else "")
        + (section("Distribution note", full_field(s["distribution_note"])) if s["distribution_note"] else "")

        + "</div>"

        # Footer
        + f"<div style='padding:16px 24px;border-top:1px solid rgba(255,255,255,0.08);"
        f"display:flex;align-items:center;justify-content:space-between;flex-shrink:0;'>"
        f"<span style='font-size:11px;color:rgba(255,255,255,0.25);'>Slice · {proj_name}</span>"
        f"{footer_btn}"
        f"</div>"

        + "</div>"
    )


# ── Project detail tab renderers ─────────────────────────────────────────

def _action_tab_html(blocked_rows, flag_items, flagged_slices, question_rows, project_id):
    """Render the Action tab content for a project detail page."""

    def _esc(s):
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _truncate(s, n=120):
        s = (s or "").strip()
        return s[:n - 3] + "…" if len(s) > n else s

    def action_item(dot_color, text, tag=None, who=None, age=None,
                    clickable=False, pid=None, sid=None):
        click_attr = f"onclick='openSliceOverlay({pid},\"{sid}\")' " if clickable else ""
        hover_attrs = (
            "onmouseover='this.style.background=\"rgba(255,255,255,0.05)\"' "
            "onmouseout='this.style.background=\"transparent\"'"
        ) if clickable else ""
        cursor = "cursor:pointer;" if clickable else ""
        meta_parts = []
        if tag:
            meta_parts.append(
                f"<span style='font-size:10px;color:rgba(255,255,255,0.3);"
                f'font-family:"SF Mono","Fira Code",monospace;'
                f"'>{_esc(tag)}</span>"
            )
        if who:
            meta_parts.append(
                f"<span style='font-size:11px;color:rgba(255,255,255,0.25);'>"
                f"Who can answer: {_esc(who)}</span>"
            )
        if age:
            meta_parts.append(
                f"<span style='font-size:11px;color:rgba(255,255,255,0.2);'>Open {age}</span>"
            )
        meta_html = (
            f"<div style='display:flex;align-items:center;gap:12px;'>{''.join(meta_parts)}</div>"
            if meta_parts else ""
        )
        return (
            f"<div {click_attr}{hover_attrs} "
            f"style='display:flex;align-items:flex-start;gap:10px;padding:10px 8px;"
            f"border-radius:6px;{cursor}margin:0 -8px;'>"
            f"<div style='width:6px;height:6px;border-radius:50%;background:{dot_color};"
            f"margin-top:5px;flex-shrink:0;'></div>"
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:13px;color:rgba(255,255,255,0.8);line-height:1.5;"
            f"margin-bottom:4px;'>{_esc(_truncate(text))}</div>"
            f"{meta_html}"
            f"</div></div>"
        )

    def card(bg, border_color, badge_bg, badge_color, badge_label, tier_desc, items_html):
        # Add dividers between items (last item has no border)
        dividers = []
        for i, h in enumerate(items_html):
            sep = "" if i == len(items_html) - 1 else "border-bottom:1px solid rgba(255,255,255,0.05);"
            dividers.append(h.replace("border-radius:6px;", f"border-radius:6px;{sep}", 1))
        return (
            f"<div style='background:{bg};border:1px solid {border_color};"
            f"border-radius:10px;padding:16px 18px;margin-bottom:12px;'>"
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:12px;'>"
            f"<span style='font-size:10px;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:1px;padding:2px 8px;border-radius:4px;"
            f"background:{badge_bg};color:{badge_color};'>{badge_label}</span>"
            f"<span style='font-size:11px;color:rgba(255,255,255,0.3);'>{tier_desc}</span>"
            f"</div>"
            + "".join(dividers)
            + "</div>"
        )

    sections = []

    # ── Blocked ─────────────────────────────────────────────────────────
    if blocked_rows:
        items = [
            action_item(
                "#FDA4AF",
                r["notes"] or r["name"],
                tag=f"{r['slice_id']} · Slice",
                age=_open_duration(r["last_modified"]),
                clickable=True, pid=project_id, sid=r["slice_id"]
            )
            for r in blocked_rows
        ]
        sections.append(card(
            "rgba(190,18,60,0.08)", "rgba(190,18,60,0.25)",
            "rgba(190,18,60,0.25)", "#FDA4AF",
            "Blocked", "Hard stop — work cannot proceed", items
        ))

    # ── Flagged ─────────────────────────────────────────────────────────
    flagged_items_html = []
    for f in flag_items:
        is_slice = f["object_type"] == "slice" and f["object_id"]
        flagged_items_html.append(action_item(
            "#FCD34D",
            f["reason"],
            tag=f"{f['object_id']} · {f['object_type'].title()}" if f["object_id"] else None,
            clickable=bool(is_slice), pid=project_id, sid=f["object_id"] if is_slice else None
        ))
    for s in flagged_slices:
        flagged_items_html.append(action_item(
            "#FCD34D",
            s["reason"] or s["name"],
            tag=f"{s['slice_id']} · Slice",
            age=_open_duration(s["last_modified"]),
            clickable=True, pid=project_id, sid=s["slice_id"]
        ))
    if flagged_items_html:
        sections.append(card(
            "rgba(180,83,9,0.08)", "rgba(180,83,9,0.2)",
            "rgba(180,83,9,0.25)", "#FCD34D",
            "Flagged", "Soft signal — worth attention", flagged_items_html
        ))

    # ── Outstanding Questions ────────────────────────────────────────────
    if question_rows:
        items = [
            action_item(
                "#93C5FD",
                q["text"],
                tag=q["surfaced_during"] or None,
                who=q["who_can_answer"] or None
            )
            for q in question_rows
        ]
        sections.append(card(
            "rgba(37,99,235,0.06)", "rgba(37,99,235,0.18)",
            "rgba(37,99,235,0.2)", "#93C5FD",
            "Outstanding Questions", "External input needed", items
        ))

    if not sections:
        return (
            "<div style='display:flex;flex-direction:column;align-items:center;"
            "justify-content:center;padding:60px 0;text-align:center;'>"
            "<div style='font-size:24px;margin-bottom:12px;opacity:0.3;'>✓</div>"
            "<p style='font-size:14px;font-weight:600;color:rgba(255,255,255,0.4);"
            "margin:0 0 4px;'>No action items</p>"
            "<p style='font-size:12px;color:rgba(255,255,255,0.2);margin:0;'>"
            "Nothing blocked, flagged, or outstanding for this project.</p>"
            "</div>"
        )

    return "".join(sections)


def _progress_tab_html(current_phase, phase_slice_counts, deliverable_rows, phase_slices, project_id):
    """Render the Progress tab — phase summary card + deliverables list + slice list (SL-018)."""

    ph = "font-size:13px;color:rgba(255,255,255,0.25);margin:0;"

    if not current_phase:
        return f"<p style='{ph}'>No active phase found for this project.</p>"

    phase_id   = current_phase["id"]
    phase_name = current_phase["name"]
    name_esc   = phase_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    n_total = sum(phase_slice_counts.values())
    n_done  = phase_slice_counts.get("Done", 0)
    n_prog  = phase_slice_counts.get("In Progress", 0)
    n_test  = phase_slice_counts.get("In Test", 0) + phase_slice_counts.get("In QA", 0)
    n_ready = phase_slice_counts.get("Ready", 0)
    pct     = int(n_done / n_total * 100) if n_total > 0 else 0

    gate_cleared = n_total > 0 and n_done == n_total
    gate_label   = "Cleared" if gate_cleared else "Not yet cleared"
    gate_color   = "#5EEAD4" if gate_cleared else "rgba(255,255,255,0.5)"
    gate_sub     = "All slices are Done" if gate_cleared else "All slices must reach Done"

    def col_label(text):
        return (
            f"<div style='font-size:10px;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:1.5px;color:rgba(255,255,255,0.3);margin-bottom:4px;'>{text}</div>"
        )

    def col_value(text, size="18px", color="#fff"):
        esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<div style='font-size:{size};font-weight:700;color:{color};'>{esc}</div>"

    def col_sub(text):
        return (
            f"<div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:2px;'>"
            f"{text}</div>"
        )

    def count_chip(dot_color, num, label):
        return (
            f"<div style='display:flex;align-items:center;gap:5px;'>"
            f"<div style='width:6px;height:6px;border-radius:50%;background:{dot_color};'></div>"
            f"<span style='font-size:11px;font-weight:700;color:rgba(255,255,255,0.6);'>{num}</span>"
            f"<span style='font-size:11px;color:rgba(255,255,255,0.35);'>{label}</span>"
            f"</div>"
        )

    divider = (
        "<div style='width:1px;height:40px;background:rgba(255,255,255,0.08);"
        "flex-shrink:0;'></div>"
    )

    card = (
        f"<div onclick='openPhaseOverlay({project_id},{phase_id})' "
        f"style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);"
        f"border-radius:12px;padding:20px 24px;margin-bottom:24px;"
        f"display:flex;align-items:center;gap:32px;cursor:pointer;' "
        f"onmouseover='this.style.background=\"rgba(255,255,255,0.07)\";"
        f"this.style.borderColor=\"rgba(255,255,255,0.14)\"' "
        f"onmouseout='this.style.background=\"rgba(255,255,255,0.04)\";"
        f"this.style.borderColor=\"rgba(255,255,255,0.08)\"'>"

        # Column 1 — current phase name
        f"<div>"
        + col_label("Current phase")
        + col_value(name_esc)
        + "</div>"

        + divider

        # Column 2 — gate status
        + "<div>"
        + col_label("Gate status")
        + col_value(gate_label, size="14px", color=gate_color)
        + col_sub(gate_sub)
        + "</div>"

        + divider

        # Column 3 — progress bar + 4-bucket counts
        + "<div style='flex:1;'>"
        + col_label(f"Slice progress — {n_done} of {n_total} Done")
        + f"<div style='height:6px;background:rgba(255,255,255,0.08);border-radius:3px;"
        f"overflow:hidden;margin-bottom:6px;'>"
        f"<div style='width:{pct}%;height:100%;background:#2563EB;border-radius:3px;'>"
        f"</div></div>"
        + "<div style='display:flex;gap:16px;'>"
        + count_chip("#5EEAD4", n_done, "Done")
        + count_chip("#93C5FD", n_prog, "In Progress")
        + count_chip("#C4B5FD", n_test, "In Test")
        + count_chip("rgba(255,255,255,0.3)", n_ready, "Ready")
        + "</div>"
        + "</div>"

        + "</div>"
    )

    def _deliv_status(row):
        """Derive display status + colors from slice counts."""
        sc = row["slice_count"] or 0
        if sc == 0:
            return "Ready", "rgba(255,255,255,0.07)", "rgba(255,255,255,0.4)"
        if row["blocked_count"]:
            return "Blocked", "rgba(190,18,60,0.12)", "#FDA4AF"
        if (row["done_count"] or 0) >= sc:
            return "Done", "rgba(13,148,136,0.2)", "#5EEAD4"
        if row["active_count"]:
            return "In Progress", "rgba(37,99,235,0.2)", "#93C5FD"
        return "Ready", "rgba(255,255,255,0.07)", "rgba(255,255,255,0.4)"

    def deliv_row_html(row):
        did = row["deliverable_id"]
        dname = row["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        sc = row["slice_count"] or 0
        slice_label = f"{sc} slice{'s' if sc != 1 else ''}"
        status_label, st_bg, st_color = _deliv_status(row)
        return (
            f"<div onclick='openDeliverableOverlay({project_id},\"{did}\")' "
            f"style='display:flex;align-items:center;gap:14px;padding:12px 16px;"
            f"background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:9px;cursor:pointer;margin-bottom:6px;' "
            f"onmouseover='this.style.background=\"rgba(255,255,255,0.07)\"' "
            f"onmouseout='this.style.background=\"rgba(255,255,255,0.04)\"'>"
            f"<div style='width:28px;height:28px;border-radius:7px;"
            f"background:rgba(37,99,235,0.12);display:flex;align-items:center;"
            f"justify-content:center;font-size:12px;flex-shrink:0;'>⊞</div>"
            f"<span style='flex:1;font-size:13px;color:rgba(255,255,255,0.85);"
            f"font-weight:500;'>{dname}</span>"
            f"<span style='font-size:11px;color:rgba(255,255,255,0.3);flex-shrink:0;'>"
            f"{slice_label}</span>"
            f"<span style='font-size:10px;font-weight:600;padding:2px 8px;border-radius:4px;"
            f"background:{st_bg};color:{st_color};flex-shrink:0;'>{status_label}</span>"
            f"</div>"
        )

    n_delivs = len(deliverable_rows)
    section_header = (
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "margin-bottom:12px;margin-top:0;'>"
        "<span style='font-size:11px;font-weight:700;text-transform:uppercase;"
        "letter-spacing:1.5px;color:rgba(255,255,255,0.35);'>Deliverables</span>"
        f"<span style='font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;"
        f"background:rgba(124,58,237,0.15);color:#C4B5FD;'>{n_delivs} in phase</span>"
        "</div>"
    )

    deliverables_html = (
        section_header
        + "".join(deliv_row_html(r) for r in deliverable_rows)
        if deliverable_rows else ""
    )

    # ── Slice status badge colors ────────────────────────────────────────
    _STATUS_STYLES = {
        "Done":        ("rgba(13,148,136,0.2)",  "#5EEAD4"),
        "In Progress": ("rgba(37,99,235,0.2)",   "#93C5FD"),
        "In Test":     ("rgba(124,58,237,0.2)",  "#C4B5FD"),
        "In QA":       ("rgba(180,83,9,0.15)",   "#FCD34D"),
        "Ready":       ("rgba(255,255,255,0.07)","rgba(255,255,255,0.4)"),
    }

    def slice_row_html(row):
        sid    = row["slice_id"]
        sname  = row["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        status = row["status"] or "Ready"
        dname  = (row["deliverable_name"] or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        st_bg, st_color = _STATUS_STYLES.get(status, _STATUS_STYLES["Ready"])

        review_url = row["review_url"]
        review_btn = ""
        if status == "Done" and review_url:
            url_esc = review_url.replace("&", "&amp;").replace('"', "&quot;")
            review_btn = (
                f"<a href='{url_esc}' target='_blank' "
                f"onclick='event.stopPropagation()' "
                f"style='display:flex;align-items:center;gap:5px;font-size:11px;"
                f"font-weight:600;padding:4px 10px;border-radius:5px;"
                f"border:1px solid rgba(13,148,136,0.3);color:#5EEAD4;"
                f"background:rgba(13,148,136,0.1);text-decoration:none;flex-shrink:0;' "
                f"onmouseover='this.style.background=\"rgba(13,148,136,0.2)\"' "
                f"onmouseout='this.style.background=\"rgba(13,148,136,0.1)\"'>"
                f"▶ Review</a>"
            )

        return (
            f"<div onclick='openSliceOverlay({project_id},\"{sid}\")' "
            f"style='display:flex;align-items:center;gap:14px;padding:12px 16px;"
            f"background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:9px;cursor:pointer;' "
            f"onmouseover='this.style.background=\"rgba(255,255,255,0.07)\"' "
            f"onmouseout='this.style.background=\"rgba(255,255,255,0.04)\"'>"
            f"<span style='font-size:11px;font-weight:700;color:rgba(255,255,255,0.3);"
            f'font-family:"SF Mono","Fira Code",monospace;'
            f"width:50px;flex-shrink:0;'>{sid}</span>"
            f"<span style='flex:1;font-size:13px;color:rgba(255,255,255,0.85);"
            f"font-weight:500;'>{sname}</span>"
            f"<span style='font-size:11px;color:rgba(255,255,255,0.3);flex-shrink:0;"
            f"max-width:180px;text-align:right;'>{dname}</span>"
            f"<span style='font-size:10px;font-weight:600;padding:2px 8px;border-radius:4px;"
            f"background:{st_bg};color:{st_color};flex-shrink:0;width:86px;"
            f"text-align:center;box-sizing:border-box;'>{status}</span>"
            + review_btn
            + "</div>"
        )

    n_slices = len(phase_slices)
    slices_header = (
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "margin-bottom:12px;margin-top:28px;'>"
        "<span style='font-size:11px;font-weight:700;text-transform:uppercase;"
        "letter-spacing:1.5px;color:rgba(255,255,255,0.35);'>All Slices</span>"
        f"<span style='font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;"
        f"background:rgba(37,99,235,0.15);color:#93C5FD;'>{n_slices} in phase</span>"
        "</div>"
    )

    slices_html = (
        slices_header
        + "<div style='display:flex;flex-direction:column;gap:6px;'>"
        + "".join(slice_row_html(r) for r in phase_slices)
        + "</div>"
        if phase_slices else ""
    )

    return (
        card
        + "<div style='margin-bottom:28px;'>"
        + deliverables_html
        + "</div>"
        + slices_html
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

    proj = conn.execute(
        "SELECT id, name, path FROM projects WHERE name = ? AND is_active = 1",
        (name,)
    ).fetchone()

    if not proj:
        projects = _get_active_projects(conn)
        conn.close()
        name_esc = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        main_html = (
            "<div style='padding:48px 40px;'>"
            f"<h1 style='font-size:20px;font-weight:600;margin:0 0 8px;'>Project not found</h1>"
            f"<p style='font-size:13px;color:rgba(255,255,255,0.4);margin:0;'>"
            f"No active project named “{name_esc}”.</p>"
            "</div>"
        )
        return _page(_sidebar_html(projects), main_html, title="Solo Companion — Not Found"), 404

    project_id = proj["id"]
    proj_name = proj["name"]

    # Current phase: prefer Active/In Progress, else first non-Done/Cancelled
    current_phase = conn.execute(
        "SELECT id, name, status FROM phases WHERE project_id = ? "
        "AND status IN ('Active','In Progress') ORDER BY name LIMIT 1",
        (project_id,)
    ).fetchone()
    if not current_phase:
        current_phase = conn.execute(
            "SELECT id, name, status FROM phases WHERE project_id = ? "
            "AND status NOT IN ('Done','Cancelled') ORDER BY name LIMIT 1",
            (project_id,)
        ).fetchone()
    phase_label = current_phase["name"] if current_phase else "—"

    # Phase number ("Phase 2 · Dashboard" → "2") for scoped slice count
    if current_phase:
        parts = current_phase["name"].split(" ")
        phase_num = parts[1] if len(parts) > 1 else current_phase["name"]
    else:
        phase_num = None

    # Tab counts
    # Action tab — full row data + counts
    blocked_rows = conn.execute(
        "SELECT slice_id, name, notes, last_modified FROM slices "
        "WHERE project_id=? AND is_blocked=1 ORDER BY last_modified ASC",
        (project_id,)
    ).fetchall()
    flag_items = conn.execute(
        "SELECT text AS reason, object_type, object_id FROM flags WHERE project_id=?",
        (project_id,)
    ).fetchall()
    flagged_slices = conn.execute(
        "SELECT slice_id, name, flagged_reason AS reason, last_modified FROM slices "
        "WHERE project_id=? AND is_flagged=1",
        (project_id,)
    ).fetchall()
    question_rows = conn.execute(
        "SELECT text, surfaced_during, who_can_answer FROM questions "
        "WHERE project_id=? AND (status IS NULL OR status != 'Answered') ORDER BY id",
        (project_id,)
    ).fetchall()

    n_blocked = len(blocked_rows)
    n_flags = len(flag_items) + len(flagged_slices)
    n_questions = len(question_rows)
    action_count = n_blocked + n_flags + n_questions

    phase_slice_counts = {}
    if phase_num:
        for row in conn.execute(
            "SELECT status, COUNT(*) AS cnt FROM slices "
            "WHERE project_id=? AND phase=? GROUP BY status",
            (project_id, phase_num)
        ).fetchall():
            phase_slice_counts[row["status"] or "Unknown"] = row["cnt"]
    progress_count = sum(phase_slice_counts.values())

    deliverable_rows = []
    if phase_num:
        deliverable_rows = conn.execute(
            "SELECT d.deliverable_id, d.name, "
            "COUNT(s.id) AS slice_count, "
            "SUM(CASE WHEN s.status='Done' THEN 1 ELSE 0 END) AS done_count, "
            "SUM(CASE WHEN s.status IN ('In Progress','In QA','In Test') THEN 1 ELSE 0 END) AS active_count, "
            "SUM(CASE WHEN s.is_blocked=1 THEN 1 ELSE 0 END) AS blocked_count "
            "FROM deliverables d "
            "LEFT JOIN slices s ON s.project_id=d.project_id AND s.deliverable_ref=d.deliverable_id "
            "WHERE d.project_id=? AND d.phase=? "
            "GROUP BY d.deliverable_id ORDER BY d.deliverable_id",
            (project_id, phase_num)
        ).fetchall()

    phase_slices = []
    if phase_num:
        phase_slices = conn.execute(
            "SELECT s.slice_id, s.name, s.status, s.review_url, "
            "COALESCE(d.name, s.deliverable_ref) AS deliverable_name "
            "FROM slices s "
            "LEFT JOIN deliverables d ON d.project_id=s.project_id AND d.deliverable_id=s.deliverable_ref "
            "WHERE s.project_id=? AND s.phase=? ORDER BY s.slice_id",
            (project_id, phase_num)
        ).fetchall()

    backlog_count = conn.execute(
        "SELECT COUNT(*) FROM slices WHERE project_id=?",
        (project_id,)
    ).fetchone()[0]
    materials_count = conn.execute(
        "SELECT COUNT(*) FROM materials WHERE project_id=?",
        (project_id,)
    ).fetchone()[0]
    dc_count = (
        conn.execute("SELECT COUNT(*) FROM decisions WHERE project_id=?", (project_id,)).fetchone()[0]
        + conn.execute("SELECT COUNT(*) FROM changes WHERE project_id=?", (project_id,)).fetchone()[0]
    )

    last_synced = get_last_synced()
    synced_label = _relative_synced(last_synced)
    projects = _get_active_projects(conn)
    conn.close()

    name_esc = proj_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # ── Top bar ─────────────────────────────────────────────────────────
    top_bar = (
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "padding:18px 40px;border-bottom:1px solid rgba(255,255,255,0.07);"
        "background:rgba(0,0,0,0.2);position:sticky;top:0;z-index:5;flex-shrink:0;'>"
        "<div style='display:flex;align-items:center;gap:12px;'>"
        "<div style='display:flex;align-items:center;gap:8px;font-size:13px;'>"
        "<a href='/' style='color:rgba(255,255,255,0.35);text-decoration:none;'>Dashboard</a>"
        "<span style='color:rgba(255,255,255,0.2);'>/</span>"
        f"<span style='color:#fff;font-weight:600;'>{name_esc}</span>"
        "</div>"
        f"<span style='font-size:11px;font-weight:600;background:rgba(13,148,136,0.15);"
        f"color:#5EEAD4;border:1px solid rgba(13,148,136,0.25);padding:3px 10px;"
        f"border-radius:20px;'>{phase_label}</span>"
        "</div>"
        "<div style='display:flex;align-items:center;gap:12px;'>"
        f"<span style='font-size:11px;color:rgba(255,255,255,0.3);"
        f'font-family:"SF Mono","Fira Code",monospace;'
        f"'>synced {synced_label}</span>"
        "<form method='POST' action='/sync' style='margin:0;'>"
        "<button type='submit' style='display:flex;align-items:center;gap:6px;"
        "background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);"
        "color:rgba(255,255,255,0.6);padding:6px 14px;border-radius:6px;font-size:12px;"
        "font-weight:500;cursor:pointer;font-family:-apple-system,sans-serif;'>↻ Refresh</button>"
        "</form>"
        "</div>"
        "</div>"
    )

    # ── Tab bar ──────────────────────────────────────────────────────────
    def tab_btn(tab_id, label, count, active=False):
        t_color = "#fff" if active else "rgba(255,255,255,0.4)"
        t_border = "2px solid #2563EB" if active else "2px solid transparent"
        c_bg = "rgba(37,99,235,0.2)" if active else "rgba(255,255,255,0.08)"
        c_color = "#93C5FD" if active else "rgba(255,255,255,0.4)"
        return (
            f"<div id='tab-btn-{tab_id}' onclick='switchTab(\"{tab_id}\")' "
            f"style='padding:14px 18px;font-size:13px;font-weight:500;color:{t_color};"
            f"cursor:pointer;border-bottom:{t_border};display:flex;align-items:center;"
            f"gap:7px;font-family:-apple-system,sans-serif;'>"
            f"{label} "
            f"<span id='tab-count-{tab_id}' style='font-size:10px;font-weight:700;"
            f"padding:1px 6px;border-radius:10px;background:{c_bg};color:{c_color};'>"
            f"{count}</span>"
            f"</div>"
        )

    tab_bar = (
        "<div style='display:flex;align-items:center;gap:2px;padding:0 40px;"
        "border-bottom:1px solid rgba(255,255,255,0.07);background:rgba(0,0,0,0.15);"
        "flex-shrink:0;'>"
        + tab_btn("action", "Action", action_count, active=True)
        + tab_btn("progress", "Progress", progress_count)
        + tab_btn("backlog", "Backlog", backlog_count)
        + tab_btn("materials", "Materials", materials_count)
        + tab_btn("decisions", "Decisions &amp; Changes", dc_count)
        + "</div>"
    )

    # ── Tab panels (placeholders — SL-015+ replaces) ─────────────────────
    ph = "font-size:13px;color:rgba(255,255,255,0.25);margin:0;"

    def tab_panel(panel_id, content, active=False):
        disp = "block" if active else "none"
        return f"<div id='tab-panel-{panel_id}' style='display:{disp};'>{content}</div>"

    action_html   = _action_tab_html(
        blocked_rows, flag_items, flagged_slices, question_rows, project_id
    )
    progress_html = _progress_tab_html(current_phase, phase_slice_counts, deliverable_rows, phase_slices, project_id)

    content = (
        "<div style='padding:32px 40px;flex:1;'>"
        + tab_panel("action",    action_html,    active=True)
        + tab_panel("progress",  progress_html)
        + tab_panel("backlog",   f"<p style='{ph}'>Backlog view arrives in unit of work SL-017.</p>")
        + tab_panel("materials", f"<p style='{ph}'>Materials view arrives in unit of work SL-018.</p>")
        + tab_panel("decisions", f"<p style='{ph}'>Decisions &amp; Changes view arrives in unit of work SL-019.</p>")
        + "</div>"
    )

    # ── Tab switching JS ─────────────────────────────────────────────────
    tab_js = (
        "<script>"
        "var _tabIds=['action','progress','backlog','materials','decisions'];"
        "function switchTab(name){"
        "  _tabIds.forEach(function(t){"
        "    var btn=document.getElementById('tab-btn-'+t);"
        "    var panel=document.getElementById('tab-panel-'+t);"
        "    var cnt=document.getElementById('tab-count-'+t);"
        "    if(t===name){"
        "      btn.style.color='#fff';"
        "      btn.style.borderBottom='2px solid #2563EB';"
        "      cnt.style.background='rgba(37,99,235,0.2)';"
        "      cnt.style.color='#93C5FD';"
        "      panel.style.display='block';"
        "    }else{"
        "      btn.style.color='rgba(255,255,255,0.4)';"
        "      btn.style.borderBottom='2px solid transparent';"
        "      cnt.style.background='rgba(255,255,255,0.08)';"
        "      cnt.style.color='rgba(255,255,255,0.4)';"
        "      panel.style.display='none';"
        "    }"
        "  });"
        "}"
        "</script>"
    )

    main_html = top_bar + tab_bar + content + tab_js
    sidebar = _sidebar_html(projects, active_name=proj_name)
    return _page(sidebar, main_html, title=f"Solo Companion — {proj_name}", padded=False)


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


@app.route("/overlay/slice/<int:project_id>/<slice_id>")
def overlay_slice(project_id, slice_id):
    conn = get_conn()
    s = conn.execute(
        "SELECT * FROM slices WHERE project_id = ? AND slice_id = ?",
        (project_id, slice_id)
    ).fetchone()
    proj = conn.execute(
        "SELECT name FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    conn.close()

    if not s or not proj:
        return "<div style='padding:32px;color:rgba(255,255,255,0.5);'>Slice not found.</div>", 404

    from_path = request.args.get("from", "")
    from_project = None
    if from_path.startswith("/project/"):
        from_project = from_path[len("/project/"):]

    return _render_slice_overlay(s, proj["name"], from_project=from_project)


@app.route("/overlay/deliverable/<int:project_id>/<deliverable_id>")
def overlay_deliverable(project_id, deliverable_id):
    conn = get_conn()
    d = conn.execute(
        "SELECT * FROM deliverables WHERE project_id = ? AND deliverable_id = ?",
        (project_id, deliverable_id)
    ).fetchone()
    proj = conn.execute(
        "SELECT name FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    slices = conn.execute(
        "SELECT slice_id, name, status FROM slices "
        "WHERE project_id = ? AND deliverable_ref = ? ORDER BY slice_id",
        (project_id, deliverable_id)
    ).fetchall()
    conn.close()

    if not d or not proj:
        return "<div style='padding:32px;color:rgba(255,255,255,0.5);'>Deliverable not found.</div>", 404

    from_path = request.args.get("from", "")
    from_project = None
    if from_path.startswith("/project/"):
        from_project = from_path[len("/project/"):]

    return _render_deliverable_overlay(d, slices, proj["name"], from_project=from_project)


@app.route("/overlay/phase/<int:project_id>/<int:phase_db_id>")
def overlay_phase(project_id, phase_db_id):
    conn = get_conn()
    ph = conn.execute(
        "SELECT * FROM phases WHERE id = ? AND project_id = ?",
        (phase_db_id, project_id)
    ).fetchone()
    proj = conn.execute(
        "SELECT name FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    conn.close()

    if not ph or not proj:
        return "<div style='padding:32px;color:rgba(255,255,255,0.5);'>Phase not found.</div>", 404

    # Extract phase number ("Phase 2 · Dashboard" → "2") to match slices.phase + deliverables.phase
    parts = ph["name"].split(" ")
    phase_num = parts[1] if len(parts) > 1 else ph["name"]

    conn = get_conn()
    slice_rows = conn.execute(
        "SELECT status FROM slices WHERE project_id = ? AND phase = ?",
        (project_id, phase_num)
    ).fetchall()
    deliverables = conn.execute(
        "SELECT name, status FROM deliverables WHERE project_id = ? AND phase = ? ORDER BY deliverable_id",
        (project_id, phase_num)
    ).fetchall()
    conn.close()

    counts = {}
    for s in slice_rows:
        st = s["status"] or "Unknown"
        counts[st] = counts.get(st, 0) + 1

    from_path = request.args.get("from", "")
    from_project = None
    if from_path.startswith("/project/"):
        from_project = from_path[len("/project/"):]

    return _render_phase_overlay(ph, counts, deliverables, proj["name"], from_project=from_project)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
