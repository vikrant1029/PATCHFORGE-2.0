
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


class PatchForgeDatabase:
    """
    PATCHFORGE 2.0
    Persistent SQLite Database Manager
    """

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    DB_DIR = PROJECT_ROOT / "data"
    DB_PATH = DB_DIR / "patchforge.db"

    def __init__(self):
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    def get_connection(self):
        connection = sqlite3.connect(self.DB_PATH, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def serialize(data: Any) -> dict:
        if hasattr(data, "model_dump"):
            return data.model_dump(mode="json")
        if isinstance(data, dict):
            return data
        raise TypeError("Task must be a dictionary or Pydantic model.")

    def initialize_database(self):
        with self.get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    issue TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT,
                    result_json TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_status
                ON tasks(status)
            """)

            connection.commit()

    def save_task(self, task: Any):
        data = self.serialize(task)

        task_id = data.get("task_id")
        if not task_id:
            raise ValueError("Task ID is required.")

        now = datetime.now(timezone.utc).isoformat()

        issue = data.get("issue", "")
        status = data.get("status", "UNKNOWN")
        created_at = data.get("created_at") or now
        updated_at = data.get("updated_at") or now

        with self.get_connection() as connection:
            connection.execute("""
                INSERT INTO tasks (
                    task_id, issue, status,
                    created_at, updated_at, result_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    issue = excluded.issue,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    result_json = excluded.result_json
            """, (
                str(task_id),
                str(issue),
                str(status),
                str(created_at),
                str(updated_at),
                json.dumps(data, default=str)
            ))
            connection.commit()

        return {
            "success": True,
            "task_id": str(task_id),
            "message": "Task saved successfully."
        }

    def get_task(self, task_id: str):
        with self.get_connection() as connection:
            row = connection.execute("""
                SELECT * FROM tasks WHERE task_id = ?
            """, (task_id,)).fetchone()

        if row is None:
            return None

        return {
            "task_id": row["task_id"],
            "issue": row["issue"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "data": json.loads(row["result_json"])
        }

    def get_all_tasks(self):
        with self.get_connection() as connection:
            rows = connection.execute("""
                SELECT task_id, issue, status, created_at, updated_at
                FROM tasks
                ORDER BY created_at DESC
            """).fetchall()

        return [dict(row) for row in rows]

    def delete_task(self, task_id: str):
        with self.get_connection() as connection:
            cursor = connection.execute("""
                DELETE FROM tasks WHERE task_id = ?
            """, (task_id,))
            connection.commit()

        return cursor.rowcount > 0

    def get_database_status(self):
        with self.get_connection() as connection:
            total = connection.execute(
                "SELECT COUNT(*) FROM tasks"
            ).fetchone()[0]

        return {
            "database": "SQLite",
            "path": str(self.DB_PATH),
            "connected": True,
            "total_tasks": total
        }


# Shared database instance
database = PatchForgeDatabase()
