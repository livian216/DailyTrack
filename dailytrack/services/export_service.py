from __future__ import annotations

import csv
import json
from pathlib import Path

from dailytrack.services.task_service import ServiceContainer
from dailytrack.utils.date_utils import now_str


def _timestamp() -> str:
    return now_str().replace("-", "").replace(":", "").replace(" ", "_")


class ExportService:
    def __init__(self, container: ServiceContainer):
        self.c = container

    def export_json(self, exports_dir: Path) -> Path:
        payload = {}
        with self.c.db.connect() as conn:
            for table in ["daily_tasks", "long_tasks", "long_task_stages", "progress_logs", "daily_reviews", "app_meta"]:
                rows = conn.execute(f"SELECT * FROM {table}").fetchall()
                payload[table] = [dict(row) for row in rows]
        out = exports_dir / f"dailytrack_export_{_timestamp()}.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return out

    def export_csv(self, exports_dir: Path) -> list[Path]:
        mapping = [
            ("daily_tasks", "daily_tasks"),
            ("long_tasks", "long_tasks"),
            ("daily_reviews", "daily_reviews"),
        ]
        files: list[Path] = []
        with self.c.db.connect() as conn:
            for table, prefix in mapping:
                rows = [dict(r) for r in conn.execute(f"SELECT * FROM {table}").fetchall()]
                out = exports_dir / f"{prefix}_{_timestamp()}.csv"
                with out.open("w", newline="", encoding="utf-8-sig") as f:
                    if rows:
                        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                        writer.writeheader()
                        writer.writerows(rows)
                    else:
                        f.write("")
                files.append(out)
        return files
