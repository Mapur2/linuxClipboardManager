"""
database.py — SQLite persistence for clipboard history.
Stores up to 100 entries; duplicates are moved to the top.
"""

import sqlite3
import os
from datetime import datetime


class Database:
    MAX_ENTRIES = 100

    def __init__(self):
        db_dir = os.path.expanduser("~/.local/share/clipboard_manager")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "clipboard.db")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    content   TEXT    NOT NULL,
                    timestamp TEXT    NOT NULL
                )
            """)
            conn.commit()

    # ------------------------------------------------------------------ #
    #  Write operations                                                    #
    # ------------------------------------------------------------------ #

    def add_entry(self, content: str):
        """Insert new text; if it already exists move it to the top."""
        content = content.strip()
        if not content:
            return

        with sqlite3.connect(self.db_path) as conn:
            # Remove duplicate so the new insert becomes the latest
            conn.execute(
                "DELETE FROM clipboard_history WHERE content = ?", (content,)
            )
            conn.execute(
                "INSERT INTO clipboard_history (content, timestamp) VALUES (?, ?)",
                (content, datetime.now().isoformat()),
            )
            # Prune oldest entries beyond MAX_ENTRIES
            conn.execute(f"""
                DELETE FROM clipboard_history
                WHERE id NOT IN (
                    SELECT id FROM clipboard_history
                    ORDER BY timestamp DESC
                    LIMIT {self.MAX_ENTRIES}
                )
            """)
            conn.commit()

    def delete_entry(self, entry_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM clipboard_history WHERE id = ?", (entry_id,)
            )
            conn.commit()

    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM clipboard_history")
            conn.commit()

    # ------------------------------------------------------------------ #
    #  Read operations                                                     #
    # ------------------------------------------------------------------ #

    def get_entries(self, search: str = "") -> list[tuple]:
        """Return list of (id, content, timestamp) newest-first."""
        with sqlite3.connect(self.db_path) as conn:
            if search:
                cursor = conn.execute(
                    """SELECT id, content, timestamp
                       FROM clipboard_history
                       WHERE content LIKE ?
                       ORDER BY timestamp DESC""",
                    (f"%{search}%",),
                )
            else:
                cursor = conn.execute(
                    """SELECT id, content, timestamp
                       FROM clipboard_history
                       ORDER BY timestamp DESC"""
                )
            return cursor.fetchall()

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM clipboard_history"
            ).fetchone()[0]
