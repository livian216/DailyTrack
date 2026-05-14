from __future__ import annotations

from dailytrack.database import Database


class LongTaskRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, payload: dict) -> int:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO long_tasks
                (title, goal, start_date, due_date, priority, status, progress, created_at, updated_at, completed_at, archived_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["title"],
                    payload.get("goal"),
                    payload.get("start_date"),
                    payload.get("due_date"),
                    payload.get("priority", "中"),
                    payload.get("status", "未开始"),
                    payload.get("progress", 0),
                    payload["created_at"],
                    payload["updated_at"],
                    payload.get("completed_at"),
                    payload.get("archived_at"),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_all(self) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM long_tasks ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def get(self, item_id: int) -> dict | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM long_tasks WHERE id=?", (item_id,)).fetchone()
            return dict(row) if row else None

    def update(self, item_id: int, payload: dict) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE long_tasks
                SET title=?, goal=?, start_date=?, due_date=?, priority=?, status=?, progress=?, updated_at=?, completed_at=?, archived_at=?
                WHERE id=?
                """,
                (
                    payload["title"],
                    payload.get("goal"),
                    payload.get("start_date"),
                    payload.get("due_date"),
                    payload.get("priority", "中"),
                    payload.get("status", "未开始"),
                    payload.get("progress", 0),
                    payload["updated_at"],
                    payload.get("completed_at"),
                    payload.get("archived_at"),
                    item_id,
                ),
            )
            conn.commit()

    def delete(self, item_id: int) -> None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM long_tasks WHERE id=?", (item_id,))
            conn.commit()
