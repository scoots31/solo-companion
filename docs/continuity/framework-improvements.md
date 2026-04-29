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

---

## solo-build / solo-qa: Write status-change timestamps into slice records — Future

**Source:** Solo Companion activity feed design review (2026-04-29)  
**Skills to update:** `~/Developer/engineering-playbook/skills/solo-build/SKILL.md`, `~/Developer/engineering-playbook/skills/solo-qa/SKILL.md`, and any other skill that transitions slice status

**The problem:** The Solo Companion activity feed needs to know *when* a slice changed status. The current sync layer can only detect *that* a status changed (by diffing against the previous SQLite state). For the event timestamp, it falls back to the file's last-modified time — which is file-level, not slice-level, and only as accurate as when the file was last saved.

**Proposed addition — timestamp on every status transition:**

When any skill writes a status change to a slice record in backlog.md, append a `Status changed:` field with an ISO timestamp:

```markdown
Status: Done
Status changed: 2026-04-29T14:23:00
```

The sync layer reads this field and uses it as the event timestamp. Slice-level accuracy, no git dependency, no inference.

**Skills that would need this change:**
- `solo-build` — sets In Build, In QA, Done
- `solo-qa` — sets In Test
- `phase-test` — sets Done (final gate)
- Any other skill that modifies Status directly

**Why deferred:** Option A (file mtime, already in SQLite as `last_modified`) is accurate enough for the activity feed's use case — scanning what changed and when across sessions. Option C is the right long-term upgrade when timestamp precision matters (e.g., velocity tracking, time-per-slice analytics). Implement in a dedicated framework curator pass, not as part of a feature build.
