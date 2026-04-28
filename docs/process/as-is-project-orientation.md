# As-Is Process — Project Orientation & Status Awareness
**Date:** 2026-04-28
**Status:** Validated

```mermaid
flowchart TD
    A[Solo wants to start a work session] --> B[Open Claude Code]
    B --> C[Ask framework: where are we?]
    C --> D[Framework responds with current phase and slice context]
    D --> E[Ask framework: what's next?]
    E --> F[Framework confirms next slice]
    F --> G[Work on slice]
    G --> H{Need to review built work?}
    H -->|Yes| I[Ask framework to spin up build in browser]
    I --> J[Framework opens app — manual step]
    J --> K[Solo reviews work]
    K --> G
    H -->|No| L{Need to check another project?}
    L -->|Yes| M[Ask framework about different project]
    M --> N[Framework conversation context contaminated]
    N --> O[Struggle to re-orient framework back to original project]
    O --> P{Context recovered?}
    P -->|Eventually| G
    P -->|Too difficult| Q[Abandon cross-project check — stay siloed]
    L -->|No| R[Continue session]
    R --> S[Session ends — no cross-project visibility gained]
```

## Key observations

- **Orientation is fully conversational.** Every piece of context — current phase, next slice, how this fits the deliverable — must be pulled through Claude Code by asking for it. There is no ambient view.
- **Cross-project visibility has a context cost.** Asking the framework about a different project pulls the conversation in a new direction. Getting back to the original project focus requires effort — often enough effort that solos avoid it entirely.
- **Build review is manual and prompted.** The solo must ask the framework to spin up the build. It is not automatic on slice completion.
- **Serial work is enforced by friction.** The tracking difficulty of even one project makes running multiple concurrent projects impractical. Solos work on one project at a time.
- **No end-of-session summary across projects.** When a session ends, there is no way to see progress across all projects without starting new conversations with the framework.
```
