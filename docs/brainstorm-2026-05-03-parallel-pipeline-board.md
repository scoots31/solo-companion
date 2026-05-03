# Brainstorm — Parallel Pipeline Board View
**Date:** 2026-05-03
**Status:** Ready for Discover

---

## The Problem

As solos work on multi-deliverable projects, deliverables naturally reach different phases at different times. Some are ready to build. Others are still in design sprint. Others are waiting on a decision. The companion today shows project status well but doesn't give the solo a way to see this divergence at a glance — or make an informed call about where to focus.

The companion is also the right home for a cross-project portfolio view. A solo running three projects wants to open one place and see where everything stands — not open three separate project views.

---

## The Idea

A Board view added to the Solo Companion. One new tab — visible across all projects or filtered to one. Deliverables shown as cards, grouped by their current phase stage. The solo can see at a glance what's ready to build, what's still in design, what's in test, what's done.

This view makes the parallel pipeline concept tangible. When the framework detects divergent deliverable states and surfaces a prompt ("3 deliverables Ready, 1 still in design review"), the Board is where the solo goes to understand the full picture.

---

## What We Know

**The companion already has the foundation:**
- Multi-project support is in place — projects.md registry, project selector, cross-project dashboard
- sync.py reads all project backlog data into SQLite on every sync
- push.py includes full project snapshots in the Cloudflare KV payload
- The cloud viewer (index.js) already has routing, tab infrastructure, and card components

**The data is already there:**
- Every deliverable has a phase assignment and a status
- Every slice has a status that drives deliverable and phase state derivation
- The framework already produces the state the board needs to render — no new data model required at the framework level

**What needs to be added:**
- A Board view route in index.js — new tab alongside Dashboard, Activity, Search
- A kanban column structure mapping to phase stages
- Deliverable cards with slice count, status breakdown, and project label
- Project filter (All Projects / single project)
- sync.py and push.py additions if any new deliverable-level fields are needed (to confirm in discovery)

---

## What This Is Not

**Framework skill changes are a separate track.** The `start` soft prompt (detecting parallel state, surfacing the one-liner), the `Pipeline mode` field in handoff.md, and the parallel invoke orchestration are all handled by the framework curator workflow — not this build. This brainstorm is scoped to the companion view only.

---

## Kanban Structure (Preliminary)

Columns map to phase stages a deliverable can be in:

| Column | What lives here |
|---|---|
| Design Sprint | Deliverables with slices In Review or in active design sprint |
| Planning | Deliverables with slices in Planning / Ready state |
| In Build | Deliverables with one or more slices In Build or In QA |
| In Test | Deliverables at In Test state |
| Done | Deliverables fully completed |

Each card shows: deliverable name, project name (when viewing All Projects), slice count, status breakdown, phase label.

---

## Cross-Project View

The Board operates at two levels:
- **All Projects** — every active deliverable across every project in the registry, grouped by column
- **Single Project** — filtered to one project, same column structure

The project filter is the same pattern already used elsewhere in the companion. No new infrastructure needed for the filter itself.

---

## Open Questions for Discovery

1. Does the column structure above match how solos actually think about deliverable state, or does it need adjustment?
2. Should the board show only active deliverables, or include Done deliverables with a visual distinction?
3. What's the right card density — minimal (name + status) or richer (slice counts, last activity)?
4. Does the cloud viewer (Cloudflare) need to support the Board view, or is this local-only initially?
5. Any new fields needed in sync.py / push.py, or is existing deliverable data sufficient?
6. Should the Board view be the default landing tab for sessions where parallel pipeline mode is active?

---

## Going to Discover

Core concept is clear. Discovery needs to establish: the as-is experience (how does the solo currently assess cross-deliverable state across projects), the to-be flow, and the exact data model additions required. The kanban column structure and card design go to design sprint after discovery closes.

---

## Going to Research

None identified. All capabilities are technically feasible on existing companion infrastructure. No new dependencies.
