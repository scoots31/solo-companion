"""
Database layer — SQLite connection + schema.

SL-002: projects table only. Other tables arrive in SL-003 when full
framework-file parsing comes online.
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
    """)
    conn.commit()
    conn.close()
