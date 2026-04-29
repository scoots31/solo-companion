"""
Database layer — SQLite connection + schema.

Schema mirrors ~/Developer/engineering-playbook/docs/records-spec.md.
Every field defined there for phases, deliverables, and slices is captured
as a column. List-typed fields (references, criteria, checklists, etc.)
stored as JSON-encoded TEXT — see sync.py for encoding/decoding.

Project color is computed at render time from the project name hash
(SL-004) — not persisted here.
"""

import os, sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "companion.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            path        TEXT    NOT NULL,
            last_synced TEXT,
            is_active   INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS phases (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id               INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            name                     TEXT    NOT NULL,
            status                   TEXT,
            plain_description        TEXT,
            technical_description    TEXT,
            question_answered        TEXT,
            deliverables_list        TEXT,   -- JSON array
            process_steps_completed  TEXT,
            proves_de_risks          TEXT,
            out_of_scope             TEXT,
            blocked_by               TEXT,
            definition_of_done       TEXT,
            acceptance_criteria      TEXT,   -- JSON array
            self_verification        TEXT,   -- JSON array
            builder_confirmation     TEXT,   -- JSON array (empty when "Pending build")
            notes                    TEXT,
            UNIQUE(project_id, name)
        );

        CREATE TABLE IF NOT EXISTS deliverables (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id               INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            deliverable_id           TEXT    NOT NULL,   -- "D-01"
            name                     TEXT    NOT NULL,   -- "Sync Layer"
            status                   TEXT,
            type                     TEXT,
            phase                    TEXT,
            plain_description        TEXT,
            technical_description    TEXT,
            screens                  TEXT,   -- JSON array
            acceptance_criteria      TEXT,   -- JSON array
            self_verification        TEXT,   -- JSON array
            builder_confirmation     TEXT,   -- JSON array
            slices_list              TEXT,   -- JSON array of slice IDs
            references_list          TEXT,   -- JSON array
            depends_on               TEXT,
            notes                    TEXT,
            UNIQUE(project_id, deliverable_id)
        );

        CREATE TABLE IF NOT EXISTS slices (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id               INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            slice_id                 TEXT    NOT NULL,   -- "SL-001"
            name                     TEXT    NOT NULL,
            status                   TEXT,
            phase                    TEXT,
            deliverable_ref          TEXT,                -- "D-01" as written in the slice record
            plain_description        TEXT,
            technical_description    TEXT,
            design_anchor            TEXT,
            data_anchor              TEXT,
            process_anchor           TEXT,
            references_list          TEXT,                -- JSON array
            done_criteria            TEXT,                -- JSON array
            self_verification        TEXT,                -- JSON array
            builder_confirmation     TEXT,                -- JSON array
            depends_on               TEXT,
            notes                    TEXT,
            distribution_note        TEXT,                -- optional 17th field
            -- derived at parse time
            is_blocked               INTEGER NOT NULL DEFAULT 0,
            is_flagged               INTEGER NOT NULL DEFAULT 0,
            flagged_reason           TEXT,
            review_url               TEXT,
            last_modified            TEXT,
            UNIQUE(project_id, slice_id)
        );

        CREATE TABLE IF NOT EXISTS materials (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            phase_name  TEXT,
            name        TEXT    NOT NULL,
            type        TEXT    NOT NULL,
            file_path   TEXT    NOT NULL,
            UNIQUE(project_id, file_path)
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title        TEXT    NOT NULL,
            phase        TEXT,
            date         TEXT,
            status       TEXT,
            body         TEXT,
            why          TEXT,
            alternatives TEXT,
            tradeoffs    TEXT
        );

        CREATE TABLE IF NOT EXISTS changes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title        TEXT    NOT NULL,
            phase        TEXT,
            date         TEXT,
            was_value    TEXT,
            became_value TEXT,
            why          TEXT,
            affects      TEXT
        );

        CREATE TABLE IF NOT EXISTS questions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            text            TEXT    NOT NULL,
            surfaced_during TEXT,
            blocking        TEXT,
            who_can_answer  TEXT,
            status          TEXT,
            answer          TEXT
        );

        CREATE TABLE IF NOT EXISTS flags (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id     INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            text           TEXT    NOT NULL,
            object_type    TEXT,
            object_id      TEXT,
            flagged_reason TEXT
        );

        CREATE TABLE IF NOT EXISTS events (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            project_name TEXT    NOT NULL,
            event_type   TEXT    NOT NULL,
            object_type  TEXT    NOT NULL,
            object_id    TEXT    NOT NULL,
            object_name  TEXT,
            event_ts     TEXT    NOT NULL,
            review_url   TEXT
        );
    """)
    conn.commit()
    # Add runtime columns to projects if not present (safe on existing DBs)
    for col, defn in [("start_command", "TEXT"), ("app_port", "TEXT")]:
        try:
            conn.execute(f"ALTER TABLE projects ADD COLUMN {col} {defn}")
            conn.commit()
        except Exception:
            pass  # column already exists
    conn.close()
