# Project Handoff — 2026-04-28

**Current phase:** Phase 3 — Project Detail
**Overall status:** Phase 1 (Foundation) and Phase 2 (Dashboard) complete. SL-001–SL-016 Done. Project detail shell, Action tab, and Progress tab Phase Summary Card live. Moving to SL-017 (Progress Tab — Deliverables Section).

## Where we are

Phase 1 (Foundation) and Phase 2 (Dashboard) are complete. Phase 3 (Project Detail) is underway.

**Phase 1 — Foundation (Done):** SL-001/002/003. Server, sync, SQLite fully populated.
**Phase 2 — Dashboard (Done):** SL-004–SL-013. Sidebar, top bar, Needs Attention cards, three dashboard buckets, all three overlay types (Slice, Deliverable, Phase).
**Phase 3 — Project Detail (In Progress):** SL-014 Done. Routing, breadcrumb, phase pill, tab bar with counts, tab switching JS.

## What was just completed

SL-016 — Progress Tab: Phase Summary Card:
- Phase summary card at top of Progress tab
- Gate status derived live from slice completion (not from phases.status raw field)
- Progress bar + 4-bucket status counts (Done/In Progress/In Test/Ready)
- Card clickable → opens phase overlay (SL-013)
- Placeholder text for SL-017/018 below the card

SL-014/SL-015 — Project detail shell + Action tab:
- Full routing, breadcrumb, phase pill, tab bar with counts
- Action tab: Blocked (red), Flagged (amber), Questions (blue) — absent when empty
- "No action items" clean empty state

Prior: SL-014 — Project detail shell:
- `/project/<name>` route fully implemented (replaces stub)
- `padded=False` layout mode added to `_page()` — flex-column main wrapper so top bar sticks
- Top bar: breadcrumb (Dashboard / project_name) + phase pill (current phase from phases table, teal styling)
- Tab bar: 5 tabs with count badges, Action active by default, JS tab switching
- 404 handling for unknown project names
- Counts verified against live SQLite: Progress=3, Backlog=24, Materials=12, DC=7

## Open right now

Nothing blocked. SL-017 is next.

## Outstanding questions needing outside input

None blocking. One open commitment: Phase 5 — Distribution (README, install script, plist templating, config.json setup) to be defined before Phase 4 wraps.

**Framework curator review — player-evaluation legacy format:**
player-evaluation is currently excluded from Solo Companion (`is_active=0`) because its backlog uses a legacy format that predates the records-spec. It doesn't have `plain_description`, `technical_description`, or other labeled fields the sync layer expects. Question for the curator: can the player-evaluation backlog be migrated to records-spec format so it can sync into the companion app? The overlay handles missing fields gracefully (sections are hidden, not crashed) — so a partial migration would still render. This needs a human to review the player-evaluation backlog and assess the migration cost.

## Next session picks up at

**SL-017 — Progress Tab: Deliverables Section.** Spec:
- List of deliverables for current phase (from deliverables table WHERE phase_id)
- Each row: deliverable name + slice count + status chips — clickable → opens deliverable overlay (SL-012)
- Empty state if no deliverables for current phase
- Design anchor: sprint-02-project-detail.html — Progress tab, deliverables section
- Done criteria: deliverable rows render from live data; overlay opens on click

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
