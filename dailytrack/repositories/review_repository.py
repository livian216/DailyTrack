from __future__ import annotations

from dailytrack.database import Database


class ReviewRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_date(self, review_date: str) -> dict | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM daily_reviews WHERE review_date=?", (review_date,)).fetchone()
            return dict(row) if row else None

    def upsert(self, payload: dict) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO daily_reviews (review_date, summary, unfinished_reason, tomorrow_focus, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(review_date) DO UPDATE SET
                    summary=excluded.summary,
                    unfinished_reason=excluded.unfinished_reason,
                    tomorrow_focus=excluded.tomorrow_focus,
                    updated_at=excluded.updated_at
                """,
                (
                    payload["review_date"],
                    payload.get("summary"),
                    payload.get("unfinished_reason"),
                    payload.get("tomorrow_focus"),
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )
            conn.commit()

    def list_all(self) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM daily_reviews ORDER BY review_date DESC").fetchall()
            return [dict(row) for row in rows]
