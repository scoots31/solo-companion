# Deferred Decisions — Solo Companion
**Date:** 2026-04-28
**Source:** Design sprint walk-through conversation

---

## Phase 2

### Activity Feed
**What it is:** Chronological event stream across all projects. Shows slice status changes, review links becoming available, blocks opening and closing, flags raised, phase gates cleared, deliverable completions. Grouped by day. Filterable by project and event type. Every event clickable with the standard overlay pattern.

**Why deferred:** Dashboard and Project Detail cover the solo's core orientation and cross-project awareness needs in Phase 1. Activity Feed adds the historical/motion view — what changed and when — which compounds value once the solo has been using the app for a while and has a meaningful event history to scan.

**Design artifact:** `docs/design/sprint-03-activity-feed.html` — fully designed, ready for Phase 2 build.

---

## Phase 1 — Confirmed in walk-through

| Screen | Feature | Decision |
|--------|---------|----------|
| Dashboard | Needs Attention — Blocked + Flagged cards | Phase 1, full detail |
| Dashboard | Three buckets — Phases, Deliverables, Slices | Phase 1, full detail |
| Dashboard | Project filter on Deliverables + Slices buckets | Phase 1 |
| Dashboard | Overlays — slice, deliverable, phase with all attributes | Phase 1, full detail |
| Project Detail | Action tab — Blocked, Flagged, Outstanding Questions | Phase 1, full detail |
| Project Detail | Progress tab — phase summary, deliverables, slice list | Phase 1, full detail |
| Project Detail | Backlog tab — all phases, deliverables, slices | Phase 1, full detail |
| Project Detail | Materials tab — inline doc rendering + screen overlay | Phase 1, full detail |
| Project Detail | Decisions & Changes tab | Phase 1, full detail |

---

## Phase 6 — Board View

**Design artifact:** `docs/design/sprint-04-board.html`
**Walk-through date:** 2026-05-05

### Board View (local app + cloud viewer)

**Visible — in scope:**
- **Project dropdown** — single dropdown button ("All projects" default), opens popover with one option per project. Matches live activity feed pattern. Filters all columns simultaneously.
- **Deliverables / Slices toggle** — pill chips, same style as activity feed type chips. Switches card unit across all columns. Defaults to Deliverable view.
- **Four kanban columns** — Design Sprint (purple), Planning (blue), In Build (amber), In Test (teal). Column tint matches accent color. Active work only — Done excluded.
- **Deliverable cards** — name, project dot + name, slice count pill, status breakdown (colored pip dots per state). Alternating subtle shade within each column.
- **Slice cards** — slice ID, slice name, deliverable name, project dot + name, status badge. Same alternating shade.
- **Card click → overlay** — reuses existing deliverable overlay (SL-012) and slice overlay (SL-011). No new overlay design required.
- **Board in local app** — new `/board` route in app.py. Sidebar includes Search and Capture (same as all local routes).
- **Board in cloud viewer** — new Board tab in index.js `renderBoard()` function. Sidebar does NOT include Search or Capture — cloud viewer has never had those and Board does not add them.

**Implied infrastructure — in scope:**
- **Column assignment logic** — uses existing slice `status` field, same data already driving dashboard buckets and project detail tabs. No new derived field. Most-advanced status per deliverable determines column placement.
- **Active-only filter** — excludes deliverables and slices where all slices are Done or status is Cancelled. Same status field used elsewhere.
- **Project filter query** — same pattern as activity feed project dropdown. Filters SQLite query by `project_id`.
- **View toggle** — client-side JS switching card visibility, same pattern as existing type chips on activity feed.

**Visible — deferred:**
- None. All visible elements confirmed in scope for Phase 6.

**Explicitly out of scope:**
- Framework skill changes (parallel pipeline mode, `Pipeline mode` field in handoff.md, `start` soft prompt detection) — separate curator track, not this build.
- Done deliverables and slices on the board.
- Real-time board updates — sync-on-open covers this.
- Drag-to-reorder or status changes from the board — read-only view.
- Search and Capture in the cloud viewer sidebar — those features do not exist in the cloud viewer.

**Open questions:**
- None. All walk-through questions resolved.
