"""Command history management with SQLite."""
import sqlite3
import os
from datetime import datetime
from typing import Optional
import platformdirs


class History:
    """Manage command history with SQLite for persistence."""
    
    def __init__(self, app_name: str = "walter"):
        self.data_dir = platformdirs.user_data_dir(app_name)
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "history.db")
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    @property
    def conn(self) -> sqlite3.Connection:
        """Lazy connection to database."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def _init_db(self):
        """Initialize database schema."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                command TEXT NOT NULL,
                provider TEXT,
                executed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON history(created_at DESC)
        """)
        self.conn.commit()
    
    def add(self, prompt: str, command: str, provider: str = "", executed: bool = False):
        """Add command to history."""
        self.conn.execute(
            "INSERT INTO history (prompt, command, provider, executed) VALUES (?, ?, ?, ?)",
            (prompt, command, provider, int(executed))
        )
        self.conn.commit()
    
    def mark_executed(self, command: str):
        """Mark a command as executed."""
        self.conn.execute(
            "UPDATE history SET executed = 1 WHERE command = ? AND executed = 0 ORDER BY id DESC LIMIT 1",
            (command,)
        )
        self.conn.commit()
    
    def get_recent(self, limit: int = 50) -> list[dict]:
        """Get recent history entries."""
        cursor = self.conn.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Search history by prompt or command."""
        cursor = self.conn.execute(
            """SELECT * FROM history 
               WHERE prompt LIKE ? OR command LIKE ? 
               ORDER BY created_at DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_last_command(self) -> Optional[str]:
        """Get the most recent command."""
        cursor = self.conn.execute(
            "SELECT command FROM history ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return row["command"] if row else None
    
    def clear(self):
        """Clear all history."""
        self.conn.execute("DELETE FROM history")
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
