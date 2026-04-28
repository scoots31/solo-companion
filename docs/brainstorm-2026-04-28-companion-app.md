# Brainstorm — Solo Companion App
**Date:** 2026-04-28
**Status:** Ready for Discover

---

## What We Understand

The Solo Companion is a read-only local web app that sits alongside the Solo Builder Framework. It gives the solo a single place to check the status of all their projects, find what needs attention, access framework-produced documents, and review completed work — without touching a terminal or digging through folders.

The primary value moment is pre-session orientation: the solo opens the app, sees what's active and what's blocked across all their projects, decides where to work, then opens Claude Code. A manual refresh button keeps the data current for solos who want to check it mid-session without leaving the dashboard open full-time.

The app is a separate module — the framework stays file-based and unchanged. SQLite sits between the framework files and the app, syncing on open and on manual refresh. The framework owns all decisions and process. The companion app observes and surfaces. It never writes to framework data.

---

## Going to Discover

The full product is ready for discovery. Core concept, structure, and key decisions are all clear. Discovery needs to establish the as-is process (how the solo currently checks status and finds actionable items across projects) and formalize the to-be flow.

---

## Going to Research

None identified. All capabilities described are technically feasible on the existing local app infrastructure.

---

## Preliminary Process Sketch

**As-is:** Solo checks project status by reading handoff.md directly, opening backlog files manually, and digging through project folders for framework documents. Fragmented across multiple terminal windows and file locations. No cross-project view exists — each project is checked independently.

**To-be:** Solo opens the companion app. Home dashboard shows all active work across projects, blocked and flagged items in two tiers, recency signals, and recently produced artifacts. To review a specific project: select it, land on the Action tab showing outstanding questions and blocked items, navigate to Progress, Materials, or Decisions tabs as needed. Review completed slice work directly from the app via review links. Start a stopped app from within the companion without touching a terminal.

---

## App Structure

### Home Dashboard
- Three buckets: phases, deliverables, slices — actively worked on, with project name on each entry
- Action section: blocked items (hard stop) and flagged items (soft signal) across all projects — two tiers
- Recency signal per project: "last active: N days ago"
- Recently produced artifacts across all projects
- Sync on open + manual refresh button with "last synced" timestamp

### Activity Feed (third view)
- Chronological cross-project timeline from session logs
- "Yesterday — SL-004 shipped, Project A. 2 days ago — Design sprint started, Project B."
- Narrative sense of momentum across all projects

### Project Detail — Action Tab (default view)
- Outstanding questions, needs attention, blocked items for this project
- Actionable, specific, always current
- First thing the solo sees when they open a project

### Project Detail — Progress Tab
- Current phase, backlog, slice statuses
- Phase progress counts: "Build — 7 of 12 slices Done"
- Slice review links — opens running app at the right address
- Running/stopped indicator per app; "Start & Review" if stopped

### Project Detail — Materials Tab
- Phase documents auto-surfaced from known framework locations, organized by phase:
  - Discover: discovery brief, as-is map, to-be map
  - Design: sprint screens, deferred decisions
  - Build: tech context, backlog
  - Continuity: handoff, onboarding doc
- Served through the companion app's port (not file:// links)

### Project Detail — Decisions & Changes Tab
- Decisions log
- Change log
- Institutional memory of the project, one click away

---

## Architecture Decisions Made

- **Framework stays file-based** — SQLite reads from framework files, framework never knows the companion exists
- **Read-only** — the companion observes the framework process, never writes to it. Framework owns decisions.
- **One exception: Start & Review** — companion can execute the app's start command from tech-context.md. Operational convenience, not a process action.
- **Local-first** — SQLite single file on disk, LaunchAgent startup, no network required
- **Future organizational layer** — API that posts updates to a central endpoint for multi-solo visibility. Designed for but not built in Phase 1.
- **Sync model** — sync on open + manual refresh. File watcher / real-time sync deferred to later phase.
- **Installer** — one-command setup: sets framework path (defaults to ~/Developer/engineering-playbook), reads projects.md for all project paths, registers LaunchAgent, creates desktop shortcut
- **Schema version check** — companion checks framework file schema version at startup, surfaces clear error if out of sync

---

## Held for Later

- **Discovery intake** — pre-build stakeholder capture using AI-assisted transcription. Feeds the framework's discover phase with richer inputs. Phase 2 of the companion.
- **Organizational API layer** — central database aggregating all solos' project state for portfolio dashboards and global visibility. Phase 3.
- **Velocity tracking** — framework session date data not consistent enough yet. Add when data is reliable.
- **Pinned/saved links** — manual curation of review links. Auto-surfaced artifacts covers the need for Phase 1.
- **Real-time sync / file watcher daemon** — add if during-work use becomes a confirmed need.

---

## Framework Change Required (Curator — separate pass)

**solo-build skill** needs two updates:
1. Always serve built UI work in the browser on slice completion — not on request, always.
2. Write the review URL to the slice record in a defined, consistent field so the companion app can reliably read it.

This change is not part of the companion app build — it's a framework improvement surfaced by the companion app's design.
