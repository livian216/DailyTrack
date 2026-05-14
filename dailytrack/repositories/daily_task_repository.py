from __future__ import annotations

from dailytrack.database import Database


class DailyTaskRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, payload: dict) -> int:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO daily_tasks
                (title, description, task_date, priority, status, estimated_minutes, source_type, source_long_task_id, created_at, updated_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["title"],
                    payload.get("description"),
                    payload["task_date"],
                    payload.get("priority", "中"),
                    payload.get("status", "未开始"),
                    payload.get("estimated_minutes"),
                    payload.get("source_type", "manual"),
                    payload.get("source_long_task_id"),
                    payload["created_at"],
                    payload["updated_at"],
                    payload.get("completed_at"),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_by_date(self, task_date: str) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM daily_tasks WHERE task_date=? ORDER BY created_at DESC",
                (task_date,),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_all(self) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM daily_tasks ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def get(self, task_id: int) -> dict | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM daily_tasks WHERE id=?", (task_id,)).fetchone()
            return dict(row) if row else None

    def update(self, task_id: int, payload: dict) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE daily_tasks
                SET title=?, description=?, task_date=?, priority=?, status=?, estimated_minutes=?, updated_at=?, completed_at=?
                WHERE id=?
                """,
                (
                    payload["title"],
                    payload.get("description"),
                    payload["task_date"],
                    payload.get("priority", "中"),
                    payload.get("status", "未开始"),
                    payload.get("estimated_minutes"),
                    payload["updated_at"],
                    payload.get("completed_at"),
                    task_id,
                ),
            )
            conn.commit()

    def delete(self, task_id: int) -> None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM daily_tasks WHERE id=?", (task_id,))
            conn.commit()
