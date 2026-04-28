"""
Solo Companion — local read-only companion app for the Solo Builder Framework.
Runs as a LaunchAgent on port 8710. Serves project state derived from framework files.
"""

from flask import Flask, render_template, render_template_string, jsonify, abort, Response
import os
from db import init_db
from sync import run_sync
from data import get_projects, get_last_synced, get_dashboard_data, get_project_by_name

PORT = 8710
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
init_db()  # idempotent — creates tables if they don't exist


@app.after_request
def no_cache(response):
    """Prevent browser from caching any page — this is a local dev tool."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route("/")
def dashboard():
    run_sync()
    return render_template(
        "dashboard.html",
        projects=get_projects(),
        last_synced=get_last_synced(),
        data=get_dashboard_data(),
    )


@app.route("/project/<name>")
def project_detail(name):
    from data import get_project_detail
    run_sync()
    project = get_project_by_name(name)
    if not project:
        abort(404)
    return render_template(
        "project_detail.html",
        project=project,
        projects=get_projects(),
        last_synced=get_last_synced(),
        detail=get_project_detail(project["id"]),
    )


@app.route("/feed")
def activity_feed():
    return render_template_string(PROJECT_SHELL, project_name="Activity Feed — coming in Phase 2.")


@app.route("/overlay-test")
def overlay_test():
    """Isolated overlay test page — debug use only."""
    return render_template("overlay_test.html")


@app.route("/favicon.ico")
def favicon():
    # Inline SVG favicon — no file needed
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#2563EB"/><text x="16" y="22" font-size="18" text-anchor="middle" fill="#fff" font-family="sans-serif">S</text></svg>'
    return Response(svg, mimetype='image/svg+xml')


@app.route("/health")
def health():
    return jsonify({"status": "ok", "port": PORT})


@app.route("/debug/sync")
def debug_sync():
    """Inspect current sync state — used during build verification only."""
    from db import get_conn
    conn = get_conn()
    c = conn.cursor()
    result = {}
    for table in ("projects", "phases", "deliverables", "slices", "materials", "flags", "questions"):
        c.execute(f"SELECT COUNT(*) as n FROM {table}")
        result[table] = c.fetchone()["n"]
    c.execute("SELECT name, path, color, last_synced, is_active FROM projects")
    result["project_list"] = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(result)


# Minimal shells — replaced by real templates in SL-004+
DASHBOARD_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Solo Companion</title>
<style>
  body { margin: 0; background: #0F1729; color: #EDE8E0; font-family: -apple-system, sans-serif;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; }
  .msg { text-align: center; }
  h1 { font-size: 18px; font-weight: 600; margin: 0 0 8px; }
  p  { font-size: 13px; color: rgba(255,255,255,0.4); margin: 0; }
</style>
</head>
<body>
<div class="msg">
  <h1>Solo Companion</h1>
  <p>Foundation phase — dashboard coming in Phase 2 build.</p>
</div>
</body>
</html>"""

PROJECT_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Solo Companion — {{ project_name }}</title>
<style>
  body { margin: 0; background: #0F1729; color: #EDE8E0; font-family: -apple-system, sans-serif;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; }
  .msg { text-align: center; }
  h1 { font-size: 18px; font-weight: 600; margin: 0 0 8px; }
  p  { font-size: 13px; color: rgba(255,255,255,0.4); margin: 0; }
</style>
</head>
<body>
<div class="msg">
  <h1>{{ project_name }}</h1>
  <p>Project detail coming in Phase 3 build.</p>
</div>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
