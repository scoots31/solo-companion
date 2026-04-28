# Project Handoff — 2026-04-28

**Current phase:** Phase 1 — Foundation (rebuild)
**Overall status:** Phase 1–3 build scrapped. Code deleted, slice statuses reset, backlog clean. Ready to begin SL-001 from scratch.

## Where we are

A multi-hour debug session revealed that the prior build had two stacked structural failures: the sync layer dropped 80%+ of the framework's per-record fields, and the overlay JS rendered a hardcoded flat strip instead of the sectioned full-detail layout the design called for. Patches stacked on patches couldn't fix it because each patch added one field at a time to a system designed wrong at the schema level.

Decision: scrap all Phase 1–3 code and rebuild slice by slice with strict adherence to the slice specs and design files. The slice plan, design files, decisions, and process maps were correct — only the implementation against them was wrong. Those artifacts are intact.

## What was just completed

- Full audit of failed build — root causes identified (see `decisions.md` "Phase 1–3 build scrapped" entry)
- Comprehensive review of every project doc to ground the rebuild
- GitHub repo created at `scoots31/solo-companion` (private), main pushed
- LaunchAgent unloaded, port 8710 freed
- Code deleted: `app.py`, `db.py`, `data.py`, `sync.py`, all templates, `companion.db`, `companion.log`, `__pycache__/`
- `.gitignore` tightened to cover `config.json`, `.venv/`, editor scratch files
- `backlog.md` reset: SL-001–022 from Done to Ready (22 slices), Phases 1–3 from Done to Planning (3 phases), 10 builder confirmation blocks reset to "Pending build", traffic table next-up updated to SL-001
- Decision log entries added for the scrap and for Phase 5 distribution scope

## Open right now

Nothing in flight. Clean slate at SL-001.

## Outstanding questions needing outside input

None blocking. One open commitment: Phase 5 — Distribution (README, install script, plist templating, config.json setup) to be defined as a real phase before Phase 4 wraps.

## Next session picks up at

**SL-001 — App Startup and Server.** First slice of the rebuild. Spec:
- Flask server on port 8710
- LaunchAgent registered (plist already in repo from prior build, still works for Scott)
- Routes for `/` (dashboard) and `/project/<name>` — no real content yet, just confirmed responses
- No external packages beyond Flask
- Done criteria: server starts on login, http://localhost:8710 returns dashboard with no errors, server restart recovers cleanly

After SL-001 ships and signs off, SL-002 (sync project discovery) and SL-003 (sync field parsing — full schema this time) follow.

## Key context to carry

- **The framework's slice schema is the spec.** Each slice has 16+ structured fields. Each deliverable has 14+. Each phase has 15. Sync (SL-003) extracts every field. Overlay (SL-011/SL-012/SL-013) renders every field. No hardcoded subsets, no "add it later" — full detail or the slice isn't done.
- **Design files are the visual contract.** `sprint-01-dashboard.html` overlay sections (Details grid, Plain language description, Technical description, Acceptance criteria, Four Anchors grid, Quality Gates grid) are what the build must deliver. `deferred-decisions.md` line 25 confirms: "overlays — full detail."
- **Build cadence:** slice by slice, no batching. Each slice goes solo-build → code-review-and-quality → solo-qa with browser sign-off from Scott. No moving to the next slice until current is genuinely Done against its spec. Slice status updated in backlog.md immediately on sign-off.
- **Player-evaluation is excluded from sync.** Its backlog uses the legacy table format; solo-companion's backlog is the new schema. Sync will skip projects whose backlog doesn't match the new format (mark inactive). Onboarding player-evaluation to the new schema is a future concern.
- **Distribution is real and near-term.** Scott has a partner queued to install once Phase 4 ships. Phase 5 — Distribution is committed (README, install script, plist templating, config setup). Code in Phase 1–4 must avoid hardcoded paths to support this — config-driven framework path, gitignored user state.
- **Repo is private on GitHub.** `scoots31/solo-companion`. Failed-state commits preserved on main for retrospective.

## Resume Prompt

> "Resuming Solo Companion. Phase 1–3 build was scrapped on 2026-04-28 after a structural audit. Code deleted, backlog reset, repo on GitHub at scoots31/solo-companion. Begin SL-001 (App Startup and Server) — Flask + LaunchAgent + routes, no data yet. Slice-by-slice with browser sign-off at each solo-qa. Player-evaluation excluded from sync. Phase 5 — Distribution committed for after Phase 4."
