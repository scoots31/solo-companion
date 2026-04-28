# Discovery Brief — Solo Companion
**Date:** 2026-04-28
**Status:** Ready for design sprint

---

## The Story

The solo builder is running multiple framework projects simultaneously — each at a different phase, each with its own backlog of slices, decisions, and open questions. The problem is not the work itself. It's the overhead of knowing where everything stands. Every piece of context must be pulled through a conversation with the framework: where are we, what's next, how does this fit, can you show me what was built. That conversational overhead stacks up fast, and it gets worse when more than one project is running. Checking on a second project means pulling the framework into a different conversation — contaminating the current session context and making it hard to get focused again. The friction is high enough that most solos work on one project at a time, in serial, and move slowly.

The Solo Companion removes that ceiling. It is a local read-only app that runs alongside the framework and makes project state ambient — always visible, always current, no asking required. Before starting a session, the solo opens the companion app and orients in under a minute: what's active across all projects, what's blocked, what was last touched, what needs attention. They decide where to work, open Claude Code — possibly in multiple concurrent sessions — and the framework stays completely focused on the work. Any time they need cross-project awareness, they glance at the companion app instead of asking the framework. The framework conversation is never contaminated.

There is a second benefit that compounds this: tokens. Every orientation question asked of the framework — where are we, what's next, how does this fit — consumes tokens from the context window. Those tokens are spent on overhead, not building. The companion app eliminates that overhead entirely. Tokens that previously went to re-establishing context are now available for actual build work. Sessions run longer, context pressure is lower, and more gets shipped per session.

The payoff is a fundamentally different way of working. Parallel builds become practical. Phases that used to take days to close — because the solo could only work on one thing at a time — now close in hours across multiple projects simultaneously. The companion app does not replace the framework. It gives the solo the awareness layer that makes the framework's full power accessible.

---

## Key Moments

- **Pre-session orientation** — Solo opens the companion app before starting Claude Code. Dashboard shows all active work, blocked and flagged items, and recency signals across every project. Solo knows exactly where to start in under a minute.

- **Cross-project check** — Mid-session, solo needs to know where a different project stands. They open the companion app, read the Action tab for that project, and return to their active Claude Code session — context untouched, no friction.

- **Slice review** — A UI slice completes. The review link surfaces in the companion app automatically. Solo clicks it, the running app opens in the browser. If the app was stopped, Start & Review handles it — no terminal required.

- **Project deep dive** — Solo needs to recall a design decision made three weeks ago, or find the original discovery brief, or read the to-be process map. Everything is on the project detail page — organized by phase, one click away.

- **End of day** — Solo closes their sessions. Companion app shows updated progress across all projects. Multiple deliverables reviewed, phases visibly closing. What used to take days is happening in hours.

---

## Open Threads

- **Project naming** — the app has no name yet. Working name is "Solo Companion." Final name is a future decision.
- **Companion app's own name** — the framework itself also has no name yet. Same conversation, same day.
- **Installer detail** — one-command setup is agreed but the specific installer implementation is a tech-context decision, not a design decision.

---

## What We're Not Building (Yet)

- **Discovery intake** — pre-build stakeholder capture using AI-assisted transcription, feeding the framework's discover phase. Phase 2 of this product.
- **Organizational API layer** — central database aggregating all solos' project state for portfolio dashboards and multi-solo visibility. Phase 3.
- **Real-time sync / file watcher** — sync on open and manual refresh covers Phase 1. File watcher daemon deferred until during-work use is confirmed as a real need.
- **Velocity tracking** — framework session date data not consistent enough yet. Deferred.
- **Pinned / saved links** — auto-surfaced artifacts covers the Phase 1 need.

---

## Design On-Ramp

**Path:** Reference-based
**Details:** Visual design of the Solo Builder Framework communications documents (`~/Developer/engineering-playbook/docs/communications/`). Design sprint reads these first to extract the design language before producing any screens. Goal is visual consistency — the companion app should feel like it belongs in the same world as the framework's own materials.
