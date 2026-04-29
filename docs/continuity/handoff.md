# Project Handoff — 2026-04-29

**Current phase:** Phase 3 — Project Detail
**Overall status:** Phase 1 (Foundation) and Phase 2 (Dashboard) complete. SL-001–SL-018 Done. Progress tab is fully built. Moving to SL-019 (Backlog Tab).

## Where we are

Phase 1 (Foundation) and Phase 2 (Dashboard) are complete. Phase 3 (Project Detail) is underway — Action tab and full Progress tab built.

**Phase 1 — Foundation (Done):** SL-001/002/003. Server, sync, SQLite fully populated.
**Phase 2 — Dashboard (Done):** SL-004–SL-013. Sidebar, top bar, Needs Attention cards, three dashboard buckets, all three overlay types (Slice, Deliverable, Phase).
**Phase 3 — Project Detail (In Progress):** SL-014–SL-018 Done. Routing, breadcrumb, phase pill, tab bar, Action tab, full Progress tab (phase summary card, deliverables, slice list).

## What was just completed

SL-018 — Progress Tab: Slice List:
- All 9 Phase 3 slices render with ID, name, deliverable name, and status badge
- Row click opens slice overlay (SL-011) with "Already on this project" footer
- Review button logic in place — renders on Done slices with review_url (none populated yet, Phase 4)
- Slice count badge in "All Slices" section header

SL-017 — Progress Tab: Deliverables Section:
- 5 deliverables render for Phase 3 (D-04 through D-08)
- Status derived from slice completion at render time (not from raw deliverables.status field)
- Slice count per deliverable via LEFT JOIN
- Each row clickable → opens deliverable overlay (SL-012)
- Phase statuses corrected in backlog.md: Phase 1/2 = Done, Phase 3 = In Progress so companion correctly identifies the current phase

SL-016 — Progress Tab: Phase Summary Card:
- Gate status derived live from slice completion
- Progress bar + 4-bucket status counts
- Card clickable → opens phase overlay

SL-015 — Action Tab:
- Blocked (red), Flagged (amber), Questions (blue) — absent when empty
- Clean "No action items" empty state

## Open right now

Nothing blocked. SL-019 is next.

## Outstanding questions needing outside input

None blocking. One open commitment: Phase 5 — Distribution (README, install script, plist templating, config.json setup) to be defined before Phase 4 wraps.

**Framework curator review — player-evaluation legacy format:**
player-evaluation is currently excluded from Solo Companion (`is_active=0`) because its backlog uses a legacy format that predates the records-spec. It doesn't have `plain_description`, `technical_description`, or other labeled fields the sync layer expects. Question for the curator: can the player-evaluation backlog be migrated to records-spec format so it can sync into the companion app? The overlay handles missing fields gracefully (sections are hidden, not crashed) — so a partial migration would still render. This needs a human to review the player-evaluation backlog and assess the migration cost.

## Next session picks up at

**SL-019 — Backlog Tab.** Spec:
- Three sections: Phases (all phases, ordered by sequence), Deliverables (all phases, ordered by phase then name), Slices (all slices, ordered by slice_id)
- Upcoming items (status Planning/Upcoming) rendered at 50% opacity
- All rows clickable — opens appropriate overlay type
- Design anchor: sprint-02-project-detail.html — Backlog tab, all three sections
- Done criteria: all phases/deliverables/slices render; upcoming items dimmed; each overlay type opens correctly

## Key context to carry

- **The framework's slice schema is the spec.** 17 slice fields, 15 deliverable fields, 15 phase fields. All in SQLite. Overlays (SL-011/SL-012/SL-013) render every field — no subsets.
- **Design files are the visual contract.** `sprint-01-dashboard.html` for dashboard/overlays. `sprint-02-project-detail.html` for all project detail content (tabs, overlays, everything). Read the file before writing any UI code.
- **Build cadence:** slice by slice. Solo-build → code-review-and-quality → solo-qa with browser sign-off. Slice status updated in backlog.md immediately on sign-off.
- **Player-evaluation is excluded.** Legacy backlog format, marked is_active=0 in SQLite. Not a bug — by design.
- **Distribution is real and near-term.** Partner queued to install after Phase 4. Phase 5 — Distribution committed. No hardcoded paths in any code — config-driven framework path, gitignored user state.
- **`_page(padded=False)` for project detail.** Dashboard uses `padded=True` (default). Project detail uses `padded=False` — the main wrapper is flex-column so the sticky top bar works.
- **Derived status, not raw status.** Deliverable status is computed from slice completion at render time. Phase gate is computed from slice completion. The raw `deliverables.status` and `phases.status` fields hold acceptance/tracking values from backlog.md, not build state.
- **Phase status matters for current phase detection.** The companion picks the current phase by querying `status IN ('Active','In Progress')` first, then falls back to non-Done/Cancelled. Phase statuses in backlog.md must be kept accurate — Phase 1/2 = Done, Phase 3 = In Progress.
- **Repo:** `scoots31/solo-companion` (private).

## Resume Prompt

> "Resuming Solo Companion. Phase 1 and Phase 2 complete. Phase 3 (Project Detail) in progress. SL-001–SL-017 Done. Progress tab has phase summary card and deliverables list. Begin SL-018 (Progress Tab — Slice List). Read sprint-02-project-detail.html before writing any code. Slice-by-slice with browser sign-off. Player-evaluation excluded (legacy format). Phase 5 — Distribution committed."
