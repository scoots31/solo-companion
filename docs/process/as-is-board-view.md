# As-Is Process Map — Cross-Project Portfolio Orientation
**Feature:** Board View
**Date:** 2026-05-05

---

```mermaid
flowchart TD
    A([Solo opens companion app or cloud viewer]) --> B[Dashboard loads]
    B --> C{Needs cross-project picture?}
    C -- Yes --> D[Scans active phases bucket]
    D --> E[Scans active deliverables bucket]
    E --> F[Scans active slices bucket]
    F --> G{Need more context on a project?}
    G -- Yes --> H[Clicks sidebar project or Take me to this project]
    H --> I[Project Detail loads — Action tab]
    I --> J[Checks Progress tab]
    J --> K[Checks Backlog tab]
    K --> L{Another project to check?}
    L -- Yes --> H
    L -- No --> M[Mentally synthesizes across all projects]
    M --> N([Solo decides where to focus])
    G -- No --> N
    C -- No --> O([Done — dashboard was enough])
```

---

## Notes

- The dashboard buckets (phases, deliverables, slices) show active items but are not grouped by stage — the solo can't see at a glance what's in design vs. in build vs. in test across projects.
- Cross-project synthesis is entirely manual — the solo navigates project by project and builds the picture in their head.
- Each project requires at least 2–3 tab visits to understand its full state.
- The cloud viewer has the same limitation — project-by-project navigation, no portfolio stage view.
```
