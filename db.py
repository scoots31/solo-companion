"""
Database layer — SQLite schema definition and connection management.
All tables created here; no table is created elsewhere.
"""

import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "companion.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            path        TEXT    NOT NULL,
            color       TEXT    NOT NULL DEFAULT '#2563EB',
            last_synced TEXT,
            is_active   INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS phases (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id   INTEGER NOT NULL REFERENCES projects(id),
            name         TEXT    NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'Planning',
            started_date TEXT,
            gate_status  TEXT,
            progress_pct INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS deliverables (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id   INTEGER NOT NULL REFERENCES projects(id),
            phase_name   TEXT    NOT NULL,
            name         TEXT    NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'Defined',
            type         TEXT,
            slice_count  INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS slices (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id       INTEGER NOT NULL REFERENCES projects(id),
            phase_name       TEXT,
            deliverable_name TEXT,
            slice_id         TEXT    NOT NULL,
            name             TEXT    NOT NULL,
            status           TEXT    NOT NULL DEFAULT 'Ready',
            review_url       TEXT,
            last_modified    TEXT,
            is_blocked       INTEGER NOT NULL DEFAULT 0,
            is_flagged       INTEGER NOT NULL DEFAULT 0,
            flagged_reason   TEXT
        );

        CREATE TABLE IF NOT EXISTS materials (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL REFERENCES projects(id),
            phase_name  TEXT,
            name        TEXT    NOT NULL,
            type        TEXT    NOT NULL,
            file_path   TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL REFERENCES projects(id),
            title       TEXT    NOT NULL,
            phase       TEXT,
            date        TEXT,
            body        TEXT,
            why         TEXT
        );

        CREATE TABLE IF NOT EXISTS changes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL REFERENCES projects(id),
            title       TEXT    NOT NULL,
            date        TEXT,
            was_value   TEXT,
            became_value TEXT
        );

        CREATE TABLE IF NOT EXISTS questions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id     INTEGER NOT NULL REFERENCES projects(id),
            text           TEXT    NOT NULL,
            source         TEXT,
            who_can_answer TEXT,
            open_days      INTEGER
        );

        CREATE TABLE IF NOT EXISTS flags (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id    INTEGER NOT NULL REFERENCES projects(id),
            text          TEXT    NOT NULL,
            object_type   TEXT,
            object_id     TEXT,
            flagged_reason TEXT
        );
    """)

    conn.commit()
    conn.close()
