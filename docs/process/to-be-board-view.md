# To-Be Process Map — Cross-Project Portfolio Orientation
**Feature:** Board View
**Date:** 2026-05-05

---

```mermaid
flowchart TD
    A([Solo opens companion — local or cloud viewer]) --> B[Clicks Board tab]
    B --> C[Board loads — All Projects view, Deliverable cards]
    C --> D{Want to narrow to one project?}
    D -- Yes --> E[Selects project from filter dropdown]
    E --> F[Board re-renders — single project cards only]
    D -- No --> F2[All projects visible across columns]
    F --> G{Want slice-level detail?}
    F2 --> G
    G -- Yes --> H[Toggles to Slice view]
    H --> I[Cards re-render as slices, same column structure]
    G -- No --> I2[Stays in Deliverable view]
    I --> J{Card needs detail?}
    I2 --> J
    J -- Yes --> K[Clicks card]
    K --> L[Existing deliverable or slice overlay opens]
    L --> M[Solo reviews full record detail]
    M --> N([Solo knows where to focus])
    J -- No --> N
```

---

## Kanban Column Structure

| Column | What lives here |
|---|---|
| Design Sprint | Deliverables/slices with status In Review |
| Planning | Deliverables/slices with status Planning, Ready, or Upcoming |
| In Build | Deliverables/slices with status In Build or In QA |
| In Test | Deliverables/slices with status In Test |

Active work only — Done deliverables and slices do not appear on the board.

---

## Card Content

**Deliverable card:** deliverable name · project name (All Projects view) · slice count · status breakdown (how many slices in each state)

**Slice card:** slice ID · slice name · deliverable name · project name (All Projects view) · status badge

---

## Decision Points

- **All Projects / Single Project** — filter dropdown, defaults to All Projects on load
- **Deliverable / Slice toggle** — segmented control, defaults to Deliverable view
- **Card click** — opens existing overlay (reuses SL-011 for slices, SL-012 for deliverables)

---

## Notes

- Board available in both local companion and cloud viewer (Cloudflare) — same parity model as existing tabs.
- Framework skill changes (parallel pipeline mode, handoff.md Pipeline mode field) are a separate curator track — not part of this build.
