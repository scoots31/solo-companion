# Retrospective — Solo Companion

---

## Design anchor not read before UI build — 2026-04-28
**Observed:** 1 time — Solo Build phase, SL-011
**Level:** Framework (solo-build skill) + Project

### What happened
During unit of work SL-011 (Slice Overlay Panel), the overlay was implemented as a full-height right-side sliding panel. The actual design in `sprint-01-dashboard.html` specifies a centered floating modal: `align-items:center; justify-content:center` on the backdrop, `background:#152035; border-radius:14px; max-height:88vh; box-shadow` on the panel. The builder did not read the design file before writing the code. Scott caught it during browser review — not during self-check.

### Root cause
No enforced step existed to read the design anchor before writing UI code. The builder inferred the layout from memory rather than from the actual file. The design anchor was listed in the slice record but not treated as a mandatory pre-build read. This is especially critical because the slice record says "all fields" — the overlay is supposed to render everything from the design, not a subset from memory.

### Impact
Entire overlay had to be rebuilt from scratch after Scott's review. One extra review cycle wasted. Trust in the self-review process degraded — this was the second time in the same session that Scott caught something the builder should have caught first.

### Proposed fix
For any slice with a visual/UI component: reading the design anchor file is the first step, before writing a single line of HTML. The rule is: **build from the file, not from memory.** Specifically for this project, `sprint-01-dashboard.html` is the design contract — every overlay, every bucket, every layout element maps back to it. If the file hasn't been read in the current session, read it before building.

This should be added to the solo-build skill as an explicit pre-build gate for visual slices:
> "If the slice has a design anchor, open and read it fully before writing any UI code. Do not build from memory of a previous read."

### Decision
- [x] Project adjustment — enforced for remaining UI slices on this project: read `sprint-01-dashboard.html` before building SL-012, SL-013, and any subsequent UI work
- [x] Queue for framework review → added to `framework-improvements.md`
