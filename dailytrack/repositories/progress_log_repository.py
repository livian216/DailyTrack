from __future__ import annotations

from dailytrack.database import Database


class ProgressLogRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, payload: dict) -> int:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO progress_logs (long_task_id, log_date, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload["long_task_id"],
                    payload["log_date"],
                    payload["content"],
                    payload["created_at"],
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_by_task(self, long_task_id: int) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM progress_logs WHERE long_task_id=? ORDER BY log_date DESC, id DESC",
                (long_task_id,),
            ).fetchall()
            return [dict(row) for row in rows]
