# To-Be Process — Project Orientation & Status Awareness
**Date:** 2026-04-28
**Status:** Agreed — process contract

```mermaid
flowchart TD
    A[Solo wants to start a work session] --> B[Open Solo Companion app]
    B --> C[Dashboard loads — syncs from framework files]
    C --> D{Review dashboard}
    D --> E[See all active phases, deliverables, slices across all projects]
    D --> F[See blocked items — hard stops across all projects]
    D --> G[See flagged items — soft signals across all projects]
    D --> H[See recency signals — last active per project]
    E & F & G & H --> I[Solo orients — decides what to work on]
    I --> J{Single or multiple sessions?}
    J -->|Single| K[Open Claude Code — one project]
    J -->|Multiple| L[Open multiple Claude Code sessions — parallel projects]
    K & L --> M[Work on slice — framework fully focused on this project]
    M --> N{Slice complete?}
    N -->|Yes — UI slice| O[Review link appears in companion app]
    O --> P{App running?}
    P -->|Yes| Q[Click Review — opens running app in browser]
    P -->|No| R[Click Start and Review — companion starts app, opens in browser]
    Q & R --> S[Solo reviews completed work]
    S --> T{Need to check another project?}
    T -->|Yes| U[Open companion app — zero framework context cost]
    U --> V[See that project's Action tab — questions, blocks, flags]
    V --> W[Return to Claude Code session — context untouched]
    T -->|No| X[Continue session]
    N -->|No| M
    X --> Y{Session end}
    W --> Y
    Y --> Z[Companion app shows updated progress across all projects]
    Z --> AA[Phases closing across multiple projects — hours not days]
```

## Process contract

Every step in this map is what we are building. Screens in the design sprint must trace to steps here. Slices in the backlog must implement steps here. Anything that does not trace to this map is a scope decision — not a silent addition.

## Key improvements over as-is

- **Orientation is ambient.** The solo sees project state without asking for it. No conversational overhead.
- **Cross-project visibility has zero context cost.** Checking another project means opening the companion app — the framework conversation is never touched.
- **Build review is one click.** Review links surface automatically on slice completion. No asking, no manual spin-up.
- **Parallel builds are now practical.** With ambient cross-project tracking, the solo can run multiple concurrent framework sessions without losing the thread on any project.
- **Phases close faster.** Parallel work across projects compresses time-to-phase-completion from days to hours.
- **Tokens freed for building.** Every orientation question asked of the framework consumes context window tokens. Those tokens are spent on overhead, not building. The companion app eliminates that overhead — tokens that previously went to "where are we" and "what's next" are now available for actual build work. Sessions run longer, context pressure is lower, and more gets built per session.

## Steps by screen (to be annotated after design sprint)

| Step | Screen | Slice |
|------|--------|-------|
| Dashboard loads | — | — |
| Active work buckets | — | — |
| Blocked / flagged section | — | — |
| Project detail — Action tab | — | — |
| Project detail — Progress tab | — | — |
| Project detail — Materials tab | — | — |
| Project detail — Decisions & Changes tab | — | — |
| Review link / Start & Review | — | — |
| Activity feed | — | — |
