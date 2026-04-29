# Tech Context — Solo Companion
**Profile:** General Solo
**Created:** 2026-04-28
**Last updated:** 2026-04-29

---

## What's Being Built

A read-only local companion app for the Solo Builder Framework. Runs as a persistent
Mac menu-bar process, serving a dark-themed web UI at localhost:8710. Syncs from
framework markdown files into SQLite on every dashboard open. No internet connectivity
required — all data is local.

---

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | Python 3 + Flask | ~/Apps/.venv carries Flask |
| Database | SQLite | companion.db, derived data — not committed |
| Frontend | Inline HTML/CSS/JS | No build step; raw strings in app.py |
| Deployment | LaunchAgent | com.scotth.solocompanion.plist |
| Testing | Manual browser sign-off | Slice-by-slice QA |

---

## Architecture Constraints

- **Python stdlib only for local apps** — no external packages beyond Flask (already in ~/Apps/.venv)
- **No build step** — all HTML/CSS/JS is inline raw strings; no bundler, no npm
- **Read-only** — the companion never writes to framework files; SQLite is a derived cache only
- **Config-driven paths** — framework path read from config.json; no hardcoded user paths
- **Dark theme** — `--bg:#090806` `--text:#EDE8E0` `--gold:#E8971C`; fonts: Cormorant Garamond (display), DM Sans (body)

---

## Engineering Principles

- Single-file Flask app (app.py) — all routes, HTML rendering, and helpers in one file
- Sync layer (sync.py) and DB layer (db.py) kept separate from app.py
- Markdown parsing in parsers.py — section-anchored, field-anchored extraction
- No hardcoded project paths — config.json at install time
- companion.db excluded from git — populated fresh from framework files on each run

---

## Branching and Delivery

- **Repo:** scoots31/solo-companion (private)
- **Branches:** main only — single-developer, no feature branches in practice
- **Commit convention:** `SL-[ID] [phase] — [slice name]`

---

## Infrastructure Slices Required

All infrastructure complete — Phase 1 (Foundation) is Done.

---

## Secrets and Config

- Google Maps API key — not used by this app
- Framework path — `~/Apps/data/chase_the_light/config.json` pattern; companion uses `~/Apps/data/companion/config.json` or falls back to `~/Developer/engineering-playbook`
- No secrets committed; companion.db gitignored

---

## Runtime

- **Start command:** `/Users/scottheinemeier/Apps/.venv/bin/python3 app.py`
- **App port:** `8710`

---

## Profile Reference

General solo — built from scratch. Local Mac app suite conventions from ~/Apps/CLAUDE.md.
