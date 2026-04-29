"""
Markdown parsers for framework files.

Section-anchored at the document level (## Section Name).
Field-anchored at the record level (FieldName:).

Captures every field per record without depending on field order. List-typed
fields detected by indentation/bullet shape and returned as Python lists.
Scalar fields returned as strings.

Format compatibility:
- is_records_spec_format(text) gates whether sync attempts content parsing
- Backlogs missing the required sections are treated as legacy and skipped
"""

import re

# ── Record format detection ─────────────────────────────────────────────

RECORDS_SPEC_REQUIRED_SECTIONS = (
    "## Phase Records",
    "## Deliverable Records",
    "## Slice Detail",
)


def is_records_spec_format(backlog_text):
    """True iff the backlog uses the records-spec.md format."""
    return all(section in backlog_text for section in RECORDS_SPEC_REQUIRED_SECTIONS)


# ── Section + record splitting ──────────────────────────────────────────

def extract_section(text, section_header):
    """Return the contents of a `## SectionName` section, up to the next `## ` or EOF."""
    pattern = re.compile(
        rf"^{re.escape(section_header)}\s*\n(.*?)(?=^## |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(text)
    return m.group(1) if m else ""


def split_records(section_text):
    """Split a section into [(header_line, body_text), ...]. Each record starts at ### ."""
    parts = re.split(r"^### ", section_text, flags=re.MULTILINE)
    records = []
    for part in parts[1:]:
        lines = part.split("\n", 1)
        header = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ""
        body = re.sub(r"\n---\s*\n?$", "", body).rstrip()
        records.append((header, body))
    return records


# ── Field extraction ────────────────────────────────────────────────────

def parse_fields(block_text, field_names):
    """Extract labeled fields from a record block.

    Returns dict mapping field_name -> value. Value is a string (scalar) or
    list of strings (bulleted/numbered/checkmark). Missing fields omitted.
    """
    lines = block_text.split("\n")

    # Locate the start line for each known field
    starts = []
    for i, line in enumerate(lines):
        for fname in field_names:
            if line == fname + ":" or line.startswith(fname + ": "):
                starts.append((i, fname))
                break
    starts.append((len(lines), None))  # sentinel for last field's end

    result = {}
    for idx in range(len(starts) - 1):
        line_idx, fname = starts[idx]
        end_idx = starts[idx + 1][0]
        if fname is None:
            continue

        first_line = lines[line_idx]
        inline = first_line[len(fname) + 1:].lstrip()  # content after "FieldName:"
        body_lines = lines[line_idx + 1:end_idx]

        while body_lines and not body_lines[-1].strip():
            body_lines.pop()

        if inline and not body_lines:
            result[fname] = inline
            continue

        if inline and body_lines:
            # Rare — inline value with continuation. Treat as block paragraph.
            result[fname] = (inline + "\n" + "\n".join(body_lines)).strip()
            continue

        non_blank = [l for l in body_lines if l.strip()]
        if not non_blank:
            result[fname] = None
            continue

        # List shape: every non-blank line begins with a list marker
        list_items = []
        is_list = True
        for line in non_blank:
            stripped = line.strip()
            if stripped.startswith("- "):
                list_items.append(stripped[2:].strip())
            elif stripped.startswith(("✓ ", "✗ ")):
                list_items.append(stripped[2:].strip())
            elif re.match(r"^\d+\.\s+", stripped):
                list_items.append(re.sub(r"^\d+\.\s+", "", stripped))
            else:
                is_list = False
                break

        if is_list:
            result[fname] = list_items
        else:
            # Block paragraph — collapse internal blank lines, preserve content lines
            result[fname] = "\n".join(non_blank).strip()

    return result


# ── Field name lists per record type (canonical order from records-spec.md) ─

PHASE_FIELDS = (
    "Status",
    "Plain language description",
    "Technical description",
    "Question this phase answers",
    "Deliverables",
    "Process steps completed",
    "Proves / de-risks",
    "Explicitly out of scope",
    "Blocked by",
    "Definition of done",
    "Acceptance criteria",
    "Self-verification checklist",
    "Builder confirmation",
    "Notes",
)

DELIVERABLE_FIELDS = (
    "Status",
    "Type",
    "Phase",
    "Plain language description",
    "Technical description",
    "Screens",
    "Acceptance criteria",
    "Self-verification checklist",
    "Builder confirmation",
    "Slices",
    "References",
    "Depends on",
    "Notes",
)

SLICE_FIELDS = (
    "Status",
    "Phase",
    "Deliverable",
    "Plain language description",
    "Technical description",
    "Design anchor",
    "Data anchor",
    "Process anchor",
    "References",
    "Done criteria",
    "Self-verification checklist",
    "Builder confirmation",
    "Review URL",
    "Depends on",
    "Notes",
    "Distribution note",
)


# ── Header parsing helpers ──────────────────────────────────────────────

PHASE_HEADER = re.compile(r"^Phase\s+(\d+)\s*[·—-]\s*(.+)$")
DELIVERABLE_HEADER = re.compile(r"^(D-\d+)\s*[·—-]\s*(.+)$")
SLICE_HEADER = re.compile(r"^(SL-[A-Za-z0-9-]+)\s*[·—-]\s*(.+)$")


def parse_phase_header(header):
    """Return (phase_name, display_name) or (None, None) if not a phase header."""
    m = PHASE_HEADER.match(header)
    if not m:
        return None, None
    return f"Phase {m.group(1)}", m.group(2).strip()


def parse_deliverable_header(header):
    """Return (deliverable_id, name) or (None, None)."""
    m = DELIVERABLE_HEADER.match(header)
    if not m:
        return None, None
    return m.group(1), m.group(2).strip()


def parse_slice_header(header):
    """Return (slice_id, name) or (None, None)."""
    m = SLICE_HEADER.match(header)
    if not m:
        return None, None
    return m.group(1), m.group(2).strip()


# ── Decisions / changes parsers (different format) ──────────────────────

def parse_decisions(decisions_md_text):
    """Parse decisions.md style entries: ## Title — DATE / **Phase:** / etc.

    Returns list of dicts with keys:
      title, date, phase, status, body, why, alternatives, tradeoffs
    """
    entries = []
    # Each entry starts with "## " header (skip the file's "# Decision Log" h1)
    blocks = re.split(r"^## ", decisions_md_text, flags=re.MULTILINE)
    for block in blocks[1:]:
        lines = block.split("\n", 1)
        header = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ""

        # Header form: "Title — YYYY-MM-DD"
        title, date = header, None
        m = re.match(r"^(.+?)\s+[—-]\s+(\d{4}-\d{2}-\d{2})\s*$", header)
        if m:
            title = m.group(1).strip()
            date = m.group(2)

        # Body has bold-labeled fields: **Phase:** ... \n **Status:** ...
        # Find each label and capture its value
        entry = {"title": title, "date": date, "phase": None, "status": None,
                 "body": None, "why": None, "alternatives": None, "tradeoffs": None}
        for label, key in (
            ("Phase", "phase"),
            ("Status", "status"),
            ("Decision", "body"),
            ("Why", "why"),
            ("Alternatives considered", "alternatives"),
            ("Tradeoffs acknowledged", "tradeoffs"),
        ):
            pattern = re.compile(
                rf"^\*\*{re.escape(label)}:\*\*\s*(.*?)(?=^\*\*[A-Z]|^---|\Z)",
                re.DOTALL | re.MULTILINE,
            )
            m = pattern.search(body)
            if m:
                entry[key] = m.group(1).strip() or None

        entries.append(entry)
    return entries
