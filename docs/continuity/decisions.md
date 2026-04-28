# Decision Log

---

## Companion app is a separate module — 2026-04-28
**Phase:** Brainstorm
**Status:** Active

**Decision:** The companion app is a standalone module — the framework stays file-based and unchanged.

**Why:** The framework's independence is load-bearing. Any solo can use the framework without the companion app. Making the companion a dependency would block adoption and add maintenance surface.

**Alternatives considered:**
- Embedding companion features in the framework — rejected because it creates a hard dependency and violates the framework's standalone design

**Tradeoffs acknowledged:** Framework file format changes can break the companion app's reader silently. Schema version check at startup mitigates this.

---

## Companion app is read-only — 2026-04-28
**Phase:** Brainstorm
**Status:** Active

**Decision:** The companion app never writes to framework data. It observes the process — it does not participate in it.

**Why:** The framework owns decisions and the decision process. A solo updating slice status outside the framework would be acting outside the process, breaking integrity. Read-only is not just a technical choice — it's a product principle.

**Alternatives considered:**
- Two-way sync — rejected because write-back creates a process violation, not just a sync problem

**Tradeoffs acknowledged:** The one exception (Start & Review executing the app's start command) is an operational action, not a process action. That boundary must hold.

---

## SQLite as the data layer — 2026-04-28
**Phase:** Brainstorm
**Status:** Active

**Decision:** SQLite sits between the framework files and the companion app. The app reads SQLite; SQLite syncs from framework files.

**Why:** Framework files are text/markdown — not optimized for querying across multiple projects. SQLite enables structured reads without changing the framework. Single file on disk, no server, negligible footprint.

**Alternatives considered:**
- App reads framework files directly — rejected because markdown parsing is fragile and slow for cross-project queries
- Postgres — rejected for local use; appropriate only for the future organizational layer

---

## Sync model: on-open plus manual refresh — 2026-04-28
**Phase:** Brainstorm
**Status:** Active

**Decision:** The app syncs from framework files when opened, plus a manual refresh button with a "last synced" timestamp. No background file watcher in Phase 1.

**Why:** Keeps v1 simple and reliable. Pre-session use (the primary value moment) doesn't need real-time sync. During-work use is served by the refresh button. File watcher adds infrastructure complexity that isn't yet justified by a confirmed use case.

**Alternatives considered:**
- Real-time file watcher daemon — deferred to later phase if during-work use is confirmed as a real need

---

## Dashboard action section uses two tiers — 2026-04-28
**Phase:** Brainstorm
**Status:** Active

**Decision:** The blocked/flagged section on the dashboard uses two tiers: blocked (hard stop — work cannot proceed) and flagged (soft signal — worth attention).

**Why:** Treating all alerts the same urgency risks genuinely blocking items getting lost in noise. The solo needs to distinguish "I cannot move until this is resolved" from "this is worth looking at."

---

## Phase 1–3 build scrapped — rebuild from SL-001 — 2026-04-28
**Phase:** Build (post-Phase-3 audit)
**Status:** Active

**Decision:** All code from the Phase 1–3 build (app.py, db.py, data.py, sync.py, all templates, companion.db) is deleted. Slices SL-001 through SL-022 reset from Done to Ready. Phases 1–3 reset from Done to Planning. Rebuild begins from SL-001 with full slice-by-slice discipline against the design and slice specs.

**Why:** A multi-hour overlay debug session in the prior session revealed two structural failures stacked on each other:
1. **Sync layer truncation** — `sync.py` parsed only a subset of fields per record. The framework's slice schema has 16+ structured fields (descriptions, three anchors, references, done criteria, self-verification, builder confirmation, depends on, notes); only status, phase, deliverable, and a few derived flags reached SQLite. 80%+ of the framework's content was silently dropped before the app ever saw it.
2. **Overlay JS hardcoded subset** — `dashboard.html`'s `openOverlay()` rendered a flat 4–6 row attribute strip with hardcoded `attr('Label', data.field)` calls. The design sprint (`sprint-01-dashboard.html`) explicitly called for a sectioned overlay with multi-grid layouts: Details, Plain language description, Technical description, Acceptance criteria, Four Anchors, Quality Gates. None of that was built. `deferred-decisions.md` confirmed "overlays — slice, deliverable, phase with all attributes — Phase 1, full detail" was the agreed scope.

Builder confirmation entries existed for SL-001–SL-010 but the work didn't deliver to the slice specs in those records. The chain of code-review-and-quality → solo-qa was either skipped or rubber-stamped — drift went undetected through nine Done slices.

**Alternatives considered:**
- Patch the sync to add the missing fields, patch the overlay to render them — rejected. The same pattern of "add this field, add that field" was the cause; another patch round repeats the failure mode.
- Keep the sync, rewrite only the overlay — rejected. Sync would still drop 80% of the framework data; overlay rebuild has nothing to render.
- Selective scrap (keep Phase 1 sync, scrap UI) — rejected. The sync IS the problem. Foundation has to be right or everything above it is built on bad ground.

**Tradeoffs acknowledged:**
- All build effort to date is being thrown away as code. The slice plan, design files, decisions, and process maps are intact and were correct — only the implementation against them was wrong.
- Repeats the build calendar. New work begins at SL-001.
- The git history of the failed build is preserved on `main` for retrospective reference.

**Affected by:** `deferred-decisions.md` line 25 (overlays full detail), `sprint-01-dashboard.html` overlay design (sections + grids, not flat strip)

---

## Distribution work scoped to Phase 5 — 2026-04-28
**Phase:** Build (planning)
**Status:** Active

**Decision:** Install/distribution work (README, plist templating, install script, config.json setup, LaunchAgent registration helper) is scoped as a Phase 5 — Distribution that follows Phase 4. Phase 1–4 build assumes the local Mac it runs on is Scott's; Phase 5 makes the project clone-and-run on any user's machine.

**Why:** A real partner is queued to install the app once it's working. Distribution is a near-term need, not hypothetical. But building install slices alongside Phase 1 foundation work scope-creeps a rebuild that already has structural cleanup to do. Sequencing: ship a working app to its first user (Scott), then ship a clean install path to its second (partner).

**Baked in from day one to support distribution without scope:**
- Zero hardcoded paths in code. Framework path read from `config.json` (gitignored) with a graceful default + setup-instructions fallback.
- `.gitignore` covers all user-specific files: `companion.db`, `companion.log`, `config.json`.
- LaunchAgent plist remains committed for now (works for Scott, repo is private). Phase 5 templates it.

**Alternatives considered:**
- Build install slices into Phase 1 — rejected as scope creep on a rebuild that's already correcting two structural failures.
- Build install slices ad-hoc when Phase 4 wraps — rejected because ad-hoc loses the design + done-criteria discipline that the framework provides.

**Tradeoffs acknowledged:** Partner install waits until Phase 5. Scott absorbs that timeline so the rebuild stays focused.
