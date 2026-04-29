# Framework Improvements — Solo Companion

Queued improvements that should be applied to the engineering playbook at the start of the next project or during a dedicated framework review.

---

## solo-build: Enforce design anchor read before UI build — 2026-04-28
**Source:** SL-011 deficiency (see retrospective.md)
**Skill to update:** `~/Developer/engineering-playbook/skills/solo-build/SKILL.md`

**Proposed addition — pre-build gate for visual slices:**

Add a mandatory step immediately before writing code for any slice that has a design anchor:

> **Design anchor check (visual slices only):** If the slice has a design anchor, open and read the full design file before writing any code. Do not build from a prior read or from memory. Verify: layout, colors, spacing, element hierarchy, and any states (hover, disabled, empty). Build from what the file says — not from what you expect it to say.

This step should appear in the self-verification checklist section, framed as a pre-condition rather than a post-check.

**Why:** Builders can infer incorrectly from memory. The design file is the contract — "design anchor" is only meaningful if the file is actually consulted. A single missed read produced a full overlay rebuild on SL-011.
