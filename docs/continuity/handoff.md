# Project Handoff — 2026-04-28

**Current phase:** Phase 1 — Foundation (rebuild)
**Overall status:** SL-001, SL-002, SL-003 Done. Data foundation complete — SQLite fully populated from real framework files. Moving into Phase 2 dashboard UI with SL-004.

## Where we are

Phase 1 Foundation slices are complete:

- **SL-001** — Flask server on port 8710, LaunchAgent registered, routes confirmed
- **SL-002** — Project discovery sync reading projects.md, projects table populated
- **SL-003** — Full content sync: parsers.py + extended sync.py reading all 9 table types from framework files. All 17 slice fields, 15 deliverable fields, 15 phase fields captured per records-spec.md. Verified against live data: solo-companion → 4 phases / 9 deliverables / 24 slices / 12 materials / 7 decisions. player-evaluation correctly excluded (legacy format, is_active=0).

The data foundation is correct. Phase 2 dashboard work begins with SL-004.

## What was just completed

SL-003 — Sync layer:
- `parsers.py` written from scratch: section-anchored + field-anchored extraction, every labeled field captured, list-typed fields preserved as JSON
- `db.py` schema: all 9 tables, all spec fields, JSON-encoded TEXT for list columns
- `sync.py` extended with `sync_project_content()` — destructive per-project wipe + re-insert on every sync
- `is_records_spec_format()` gates legacy projects out automatically
- Verified: SL-001 full record in SQLite has all 17 fields populated including JSON arrays

## Open right now

Nothing blocked. SL-007 is next.

## Outstanding questions needing outside input

None blocking. One open commitment: Phase 5 — Distribution (README, install script, plist templating, config.json setup) to be defined before Phase 4 wraps.

**Framework curator review — player-evaluation legacy format:**
player-evaluation is currently excluded from Solo Companion (`is_active=0`) because its backlog uses a legacy format that predates the records-spec. It doesn't have `plain_description`, `technical_description`, or other labeled fields the sync layer expects. Question for the curator: can the player-evaluation backlog be migrated to records-spec format so it can sync into the companion app? The overlay handles missing fields gracefully (sections are hidden, not crashed) — so a partial migration would still render. This needs a human to review the player-evaluation backlog and assess the migration cost.

## Next session picks up at

**SL-004 — Sidebar (Project List, Recency, Navigation).** First UI slice. Spec:
- Persistent left sidebar at 200px
- One row per active project: colored dot + project name + recency label
- Color deterministic from project name hash (8-color palette)
- Recency from projects.last_synced — format "synced Xm ago" / "synced Xh ago" / "synced today" / "never synced"
- Click navigates to /project/<name>
- Done criteria: sidebar visible, all active projects listed, color dots rendered, recency labels correct, click navigates correctly

## Key context to carry

- **The framework's slice schema is the spec.** 17 slice fields, 15 deliverable fields, 15 phase fields. All in SQLite. Overlays (SL-011/SL-012/SL-013) render every field — no subsets.
- **Design files are the visual contract.** `sprint-01-dashboard.html` overlay sections (Details grid, Plain language description, Technical description, Acceptance criteria, Four Anchors grid, Quality Gates grid). `deferred-decisions.md` line 25: "overlays — full detail."
- **Build cadence:** slice by slice. Solo-build → code-review-and-quality → solo-qa with browser sign-off. Slice status updated in backlog.md immediately on sign-off.
- **Player-evaluation is excluded.** Legacy backlog format, marked is_active=0 in SQLite. Not a bug — by design.
- **Distribution is real and near-term.** Partner queued to install after Phase 4. Phase 5 — Distribution committed. No hardcoded paths in any code — config-driven framework path, gitignored user state.
- **Repo:** `scoots31/solo-companion` (private).

## Resume Prompt

> "Resuming Solo Companion. Phase 1 Foundation complete: SL-001/002/003 Done. Data layer in SQLite verified correct. Begin SL-004 (Sidebar — Project List, Recency, Navigation) — first UI slice in Phase 2. Slice-by-slice with browser sign-off. Player-evaluation excluded (legacy format). Phase 5 — Distribution committed."
