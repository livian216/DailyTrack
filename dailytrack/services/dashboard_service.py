from __future__ import annotations

from dailytrack.services.task_service import ServiceContainer
from dailytrack.utils.date_utils import days_until, today_str


class DashboardService:
    def __init__(self, container: ServiceContainer):
        self.c = container

    def today_stats(self) -> dict:
        today = today_str()
        tasks = self.c.daily_repo.list_by_date(today)
        total = len(tasks)
        done = len([x for x in tasks if x["status"] == "已完成"])
        pending = len([x for x in tasks if x["status"] not in ("已完成", "已取消")])
        rate = 0 if total == 0 else round(done / total * 100, 1)
        high_priority = [
            x for x in tasks if x["priority"] == "高" and x["status"] not in ("已完成", "已取消")
        ]
        long_tasks = self.c.long_repo.list_all()
        upcoming = []
        overdue = []
        for item in long_tasks:
            if item["status"] in ("已完成", "已归档") or not item.get("due_date"):
                continue
            left = days_until(item["due_date"], today)
            if left <= 7 and left >= 0:
                upcoming.append(item)
            if left < 0:
                overdue.append(item)
        return {
            "date": today,
            "total": total,
            "done": done,
            "pending": pending,
            "rate": rate,
            "high_priority": high_priority,
            "upcoming": sorted(upcoming, key=lambda x: x["due_date"] or ""),
            "overdue": sorted(overdue, key=lambda x: x["due_date"] or ""),
        }
