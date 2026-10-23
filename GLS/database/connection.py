"""
Thread-safe SQLite connection manager for GLORENZA SALON AHMEDABAD.
Configures WAL journal mode, 30s busy timeout, and auto-cleanup to prevent locks.
"""

import sqlite3
import os
from typing import Any, List, Dict, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "glorenza_salon.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a resilient SQLite connection with timeout and WAL mode."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode and normal synchronization to prevent 'database is locked' errors
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    return conn


def execute_query(query: str, params: Tuple[Any, ...] = ()) -> int:
    """Executes an INSERT/UPDATE/DELETE query and closes connection safely."""
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            last_id = cursor.lastrowid
            return last_id if last_id is not None else 0
    finally:
        conn.close()


def fetch_all(query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
    """Fetches all rows as Python dictionaries."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_one(query: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
    """Fetches a single row as a Python dictionary."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()