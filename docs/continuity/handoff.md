# Project Handoff — 2026-04-28

**Current phase:** Phase 3 — Project Detail
**Overall status:** Phase 1 (Foundation) and Phase 2 (Dashboard) complete. SL-001–SL-014 Done. Project detail shell live — routing, breadcrumb, phase pill, tab bar. Moving to SL-015 (Action Tab content).

## Where we are

Phase 1 (Foundation) and Phase 2 (Dashboard) are complete. Phase 3 (Project Detail) is underway.

**Phase 1 — Foundation (Done):** SL-001/002/003. Server, sync, SQLite fully populated.
**Phase 2 — Dashboard (Done):** SL-004–SL-013. Sidebar, top bar, Needs Attention cards, three dashboard buckets, all three overlay types (Slice, Deliverable, Phase).
**Phase 3 — Project Detail (In Progress):** SL-014 Done. Routing, breadcrumb, phase pill, tab bar with counts, tab switching JS.

## What was just completed

SL-014 — Project detail shell:
- `/project/<name>` route fully implemented (replaces stub)
- `padded=False` layout mode added to `_page()` — flex-column main wrapper so top bar sticks
- Top bar: breadcrumb (Dashboard / project_name) + phase pill (current phase from phases table, teal styling)
- Tab bar: 5 tabs with count badges, Action active by default, JS tab switching
- 404 handling for unknown project names
- Counts verified against live SQLite: Progress=3, Backlog=24, Materials=12, DC=7

## Open right now

Nothing blocked. SL-015 is next.

## Outstanding questions needing outside input

None blocking. One open commitment: Phase 5 — Distribution (README, install script, plist templating, config.json setup) to be defined before Phase 4 wraps.

**Framework curator review — player-evaluation legacy format:**
player-evaluation is currently excluded from Solo Companion (`is_active=0`) because its backlog uses a legacy format that predates the records-spec. It doesn't have `plain_description`, `technical_description`, or other labeled fields the sync layer expects. Question for the curator: can the player-evaluation backlog be migrated to records-spec format so it can sync into the companion app? The overlay handles missing fields gracefully (sections are hidden, not crashed) — so a partial migration would still render. This needs a human to review the player-evaluation backlog and assess the migration cost.

## Next session picks up at

**SL-015 — Action Tab.** First tab content slice. Spec:
- Three sections: Blocked (red), Flagged (amber), Outstanding Questions (blue) — each absent when empty
- Blocked: slices WHERE is_blocked=1 for this project
- Flagged: flags table WHERE project_id
- Questions: questions table WHERE project_id AND status != 'Answered'
- Each blocked/flagged item is clickable → opens slice overlay (SL-011)
- All three sections empty → clean "No action items" state
- Design anchor: sprint-02-project-detail.html — Action tab
- Done criteria: all three sections render correctly from real data; empty state is clean

## Key context to carry

- **The framework's slice schema is the spec.** 17 slice fields, 15 deliverable fields, 15 phase fields. All in SQLite. Overlays (SL-011/SL-012/SL-013) render every field — no subsets.
- **Design files are the visual contract.** `sprint-01-dashboard.html` for dashboard/overlays. `sprint-02-project-detail.html` for all project detail content (tabs, overlays, everything). Read the file before writing any UI code.
- **Build cadence:** slice by slice. Solo-build → code-review-and-quality → solo-qa with browser sign-off. Slice status updated in backlog.md immediately on sign-off.
- **Player-evaluation is excluded.** Legacy backlog format, marked is_active=0 in SQLite. Not a bug — by design.
- **Distribution is real and near-term.** Partner queued to install after Phase 4. Phase 5 — Distribution committed. No hardcoded paths in any code — config-driven framework path, gitignored user state.
- **`_page(padded=False)` for project detail.** Dashboard uses `padded=True` (default). Project detail uses `padded=False` — the main wrapper is flex-column so the sticky top bar works.
- **Repo:** `scoots31/solo-companion` (private).

## Resume Prompt

> "Resuming Solo Companion. Phase 1 and Phase 2 complete. Phase 3 (Project Detail) in progress. SL-001–SL-014 Done. Project detail shell live — routing, breadcrumb, phase pill, tab bar with counts. Begin SL-015 (Action Tab content). Read sprint-02-project-detail.html before writing any code. Slice-by-slice with browser sign-off. Player-evaluation excluded (legacy format). Phase 5 — Distribution committed."
