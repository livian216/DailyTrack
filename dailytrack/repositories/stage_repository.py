from __future__ import annotations

from dailytrack.database import Database


class StageRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, payload: dict) -> int:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO long_task_stages (long_task_id, title, description, status, sort_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["long_task_id"],
                    payload["title"],
                    payload.get("description"),
                    payload.get("status", "未开始"),
                    payload.get("sort_order", 0),
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_by_task(self, long_task_id: int) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM long_task_stages WHERE long_task_id=? ORDER BY sort_order ASC, id ASC",
                (long_task_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def update(self, stage_id: int, payload: dict) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE long_task_stages
                SET title=?, description=?, status=?, sort_order=?, updated_at=?
                WHERE id=?
                """,
                (
                    payload["title"],
                    payload.get("description"),
                    payload.get("status", "未开始"),
                    payload.get("sort_order", 0),
                    payload["updated_at"],
                    stage_id,
                ),
            )
            conn.commit()

    def delete(self, stage_id: int) -> None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM long_task_stages WHERE id=?", (stage_id,))
            conn.commit()
