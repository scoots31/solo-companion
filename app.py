"""
Solo Companion — local read-only companion app for the Solo Builder Framework.

SL-001: Flask shell on port 8710.
SL-002: project discovery sync on dashboard request; placeholder shows sync state.
"""

from datetime import datetime
from flask import Flask

from db import get_conn, init_db
from sync import discover_projects, get_last_synced

PORT = 8710
app = Flask(__name__)
init_db()


def _format_synced(iso_ts):
    """Render an ISO timestamp as 'h:mm am/pm' in local time, or 'never'."""
    if not iso_ts:
        return "never"
    try:
        dt = datetime.fromisoformat(iso_ts).astimezone()
        return dt.strftime("%-I:%M %p").lower()
    except ValueError:
        return iso_ts


@app.route("/")
def dashboard():
    discover_projects()
    conn = get_conn()
    rows = conn.execute(
        "SELECT name, is_active FROM projects ORDER BY name"
    ).fetchall()
    conn.close()

    active = sum(1 for r in rows if r["is_active"])
    inactive = len(rows) - active
    project_lines = "".join(
        f"<li style='font-family:SF Mono,monospace;font-size:11px;"
        f"color:rgba(255,255,255,{0.65 if r['is_active'] else 0.25});'>"
        f"{r['name']}{' (inactive)' if not r['is_active'] else ''}</li>"
        for r in rows
    )

    return (
        "<!DOCTYPE html>"
        "<html lang='en'><head><meta charset='UTF-8'>"
        "<title>Solo Companion</title></head>"
        "<body style='font-family:-apple-system,sans-serif;background:#0F1729;color:#EDE8E0;"
        "display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;'>"
        "<div style='text-align:center;max-width:480px;'>"
        "<h1 style='font-size:18px;font-weight:600;margin:0 0 8px;'>Solo Companion</h1>"
        "<p style='font-size:13px;color:rgba(255,255,255,0.4);margin:0 0 20px;'>"
        "Foundation slice (SL-001/SL-002) — dashboard arrives in SL-004 onwards."
        "</p>"
        f"<p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0 0 6px;'>"
        f"Synced {active} active project{'s' if active != 1 else ''}"
        f"{f' · {inactive} inactive' if inactive else ''}"
        f" · last synced {_format_synced(get_last_synced())}</p>"
        f"<ul style='list-style:none;padding:0;margin:8px 0 0;'>{project_lines}</ul>"
        "</div></body></html>"
    )


@app.route("/project/<name>")
def project_detail(name):
    return (
        "<!DOCTYPE html>"
        f"<html lang='en'><head><meta charset='UTF-8'>"
        f"<title>Solo Companion — {name}</title></head>"
        "<body style='font-family:-apple-system,sans-serif;background:#0F1729;color:#EDE8E0;"
        "display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;'>"
        "<div style='text-align:center;'>"
        f"<h1 style='font-size:18px;font-weight:600;margin:0 0 8px;'>{name}</h1>"
        "<p style='font-size:13px;color:rgba(255,255,255,0.4);margin:0;'>"
        "Foundation slice (SL-001) — project detail arrives in SL-014 onwards."
        "</p></div></body></html>"
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
