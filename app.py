"""
Solo Companion — local read-only companion app for the Solo Builder Framework.

SL-001: foundation slice. Flask server on port 8710, dashboard and project routes.
No data layer, no sync, no real UI — those arrive in later slices.
"""

from flask import Flask

PORT = 8710
app = Flask(__name__)


@app.route("/")
def dashboard():
    return (
        "<!DOCTYPE html>"
        "<html lang='en'><head><meta charset='UTF-8'>"
        "<title>Solo Companion</title></head>"
        "<body style='font-family:-apple-system,sans-serif;background:#0F1729;color:#EDE8E0;"
        "display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;'>"
        "<div style='text-align:center;'>"
        "<h1 style='font-size:18px;font-weight:600;margin:0 0 8px;'>Solo Companion</h1>"
        "<p style='font-size:13px;color:rgba(255,255,255,0.4);margin:0;'>"
        "Foundation slice (SL-001) — dashboard arrives in SL-004 onwards."
        "</p></div></body></html>"
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
