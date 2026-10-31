import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "habits.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_script = f.read()

    conn = get_db_connection()
    with conn:
        conn.executescript(schema_script)
    conn.close()