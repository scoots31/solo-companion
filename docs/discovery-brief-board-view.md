# Discovery Brief — Board View
**Date:** 2026-05-05
**Status:** Ready for design sprint

---

## The Story

A solo running multiple projects at the same time has no single place to see where everything stands across the full portfolio. The companion's dashboard surfaces blocked and flagged items well, and the project detail tabs give a complete picture of any individual project — but neither answers the question the solo is actually asking when they sit down to work: *what's ready to build, what's still in design, what's in test right now across everything I'm tracking?* That question requires opening each project individually and mentally synthesizing the picture. It's manual, slow, and the whole point of the companion is to not do that.

The Board view adds a kanban-style tab to the Solo Companion — visible in both the local app and the cloud viewer. When the solo opens it, they see every active deliverable across all their projects grouped by stage: Design Sprint, Planning, In Build, In Test. The default view is all projects at once, because the cross-project picture is the primary value. A project filter lets them narrow when they want to focus on one. A toggle switches the card unit between deliverables and slices — deliverable view for the portfolio picture, slice view for granular build state.

The journey is short by design. The solo opens the Board, reads the columns, and knows where everything stands. If they need more on a specific item, they click the card and the existing overlay opens with the full record. No new overlay design needed — the board is a new entry point into a system the companion already has. The payoff moment is the first time the solo can orient across all their projects in under ten seconds, without clicking into a single project detail page.

The Board surfaces in both the local companion and the cloud viewer with the same parity as existing tabs — the solo should be able to check the portfolio picture from anywhere.

---

## Key Moments

- **Board opens to the full portfolio** — All Projects loaded by default, deliverable cards grouped by stage. This is the primary view — the cross-project snapshot that doesn't exist today.
- **Project filter narrows the picture** — dropdown lets the solo collapse to one project when they need project-specific focus. Same filter pattern already in use elsewhere in the companion.
- **Deliverable / Slice toggle** — the solo can stay at deliverable level for a high-level read, or switch to slice level to see exactly what's in flight. Two valid modes, same column structure.
- **Card click opens the overlay** — no new detail surface needed. The existing slice and deliverable overlays carry all the detail. The board is navigation, not a new data layer.

---

## Open Threads

- Column assignment logic for deliverables: a deliverable with slices in mixed states (some In Build, some Planning) lands in the column matching its most-advanced slice — confirm this rule in design sprint.
- Card density for slice cards: slice ID + name + deliverable name + project is likely enough — confirm during design sprint visual pass.
- Sort order within columns: by project, by last activity, or by slice/deliverable ID — not resolved, leave to design sprint.
- Empty column treatment: hide the column entirely or show an empty state — leave to design sprint.

---

## What We're Not Building (Yet)

- Framework skill changes — parallel pipeline mode detection, Pipeline mode field in handoff.md, and the `start` soft prompt are a separate curator track. This build is companion-only.
- Done deliverables and slices on the board — active work only.
- Real-time board updates — sync-on-open covers this, same as all other companion tabs.
- Drag-to-reorder or status-change from the board — read-only view.

---

## Design On-Ramp

**Path:** From scratch — extending existing companion design system
**Details:** Match the visual language of the existing local app (sprint-01-dashboard.html, sprint-02-project-detail.html) and cloud viewer. Kanban column layout is new but card components and overlay wiring reuse existing patterns.
