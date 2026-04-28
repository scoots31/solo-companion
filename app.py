"""
Solo Companion — local read-only companion app for the Solo Builder Framework.
Runs as a LaunchAgent on port 8710. Serves project state derived from framework files.
"""

from flask import Flask, render_template_string, jsonify, abort
import os

PORT = 8710
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_SHELL)


@app.route("/project/<name>")
def project_detail(name):
    return render_template_string(PROJECT_SHELL, project_name=name)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "port": PORT})


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
