# Project Handoff — 2026-04-28

**Current phase:** Phase 4 — Review Flow
**Overall status:** Phases 1–3 shipped. Dashboard and Project Detail are live. Overlay debug incomplete.

## What was built and is working
- **Phase 1 — Foundation:** Sync layer (sync.py), SQLite DB (9 tables), LaunchAgent auto-start on port 8710
- **Phase 2 — Dashboard:** Sidebar nav, three bucket columns (Phases, Deliverables, Slices), project filter buttons, attention panel, last-synced timestamp
- **Phase 3 — Project Detail:** Project detail page with Action / Progress / Backlog / Materials / Decisions tabs
- Both projects sync correctly: solo-companion (section-header backlog) and player-evaluation (table-format backlog)
- Progress % computes correctly from Done slices per phase
- Slice counts per deliverable compute correctly

## What is broken / unresolved going into next session
**Dashboard overlays open but attribute content is not loading correctly.** The overlay panel appears when clicking a phase, deliverable, or slice row. The JS generates the right HTML (confirmed via Node.js test). The data attributes are correctly structured in the HTML. But the user reports attributes are not showing as expected.

### What was tried and did NOT fix it
- Fixed missing `>` on all 10 clickable div tags — overlay panel now opens
- Rewrote `openOverlay()` from template literals to plain string concatenation
- Added `window.onerror` + try/catch with alert() — no JS errors surfaced
- Added `gate_status`, `started_date` to phases query
- Added `review_url`, `flagged_reason` to slices query
- Fixed phase slice counts (Cartesian product bug fixed with subqueries)
- Fixed deliverable_name resolution (D-09 → D-09 — Review Flow via LEFT JOIN)
- Added Flagged and Review fields always visible in slice overlay (not conditional)
- Added Slices (done of total) and Deliverables count to phase overlay

### Current overlay field set
- **Slice:** Status, Phase, Deliverable (full name), Blocked, Flagged, Review URL
- **Deliverable:** Status, Phase, Type, Slices total
- **Phase:** Status, Progress, Gate, Slices (x of y done), Deliverables count, Started (if set)

### What to try next session
The next session should open browser DevTools (F12 → Console tab) on the dashboard and click a row. Check for any JS errors or warnings. Also check the Elements tab to confirm `#overlay-content` innerHTML is being set after a click. The JS and data are structurally correct — the issue is likely something subtle in the browser rendering environment that hasn't been surfaced yet.

## Active slices (Phase 4)
- **SL-023** — Review Link Surfacing | Status: Ready | Deliverable: D-09 — Review Flow
- **SL-024** — Start & Review Action | Status: Ready | Deliverable: D-09 — Review Flow

## Key files
- `app.py` — Flask routes, port 8710
- `sync.py` — reads framework markdown files into SQLite
- `data.py` — all DB queries for templates
- `db.py` — schema init
- `templates/dashboard.html` — main dashboard with overlay JS
- `templates/project_detail.html` — project detail tabs
- `companion.db` — SQLite database (do not commit)

## Key context to carry
- App is read-only. Start & Review (SL-024) is the one exception — executes app start command.
- player-evaluation slices don't have deliverable associations in their backlog (flat table format). Empty deliverable_name on those rows is correct.
- gate_status and started_date are NULL for all phases — not yet parsed from backlog. "Not yet cleared" is the fallback display.
- The `/overlay-test` route exists for isolated overlay testing (debug use).
- The `/debug/sync` route shows table row counts.
- LaunchAgent plist: `com.scotth.solocompanion.plist` — KeepAlive=true, respawns on kill.

## Resume prompt
> "Resuming Solo Companion. Phases 1–3 complete and live on port 8710. Phase 4 build blocked on overlay attribute display bug. Dashboard overlays open but attributes not rendering correctly. No JS errors surface via try/catch. Start by opening DevTools on the dashboard, clicking a row, and checking the Elements panel to see what innerHTML is set on #overlay-content after the click."
