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
