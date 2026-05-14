from __future__ import annotations

import unittest
from pathlib import Path
import shutil

from dailytrack.config import PathConfig
from dailytrack.services.path_service import PathService
from dailytrack.services.task_service import ServiceContainer, TaskService
from dailytrack.utils.date_utils import today_str


class TestServices(unittest.TestCase):
    def setUp(self):
        self.tmp_root = Path(".test_tmp")
        self.tmp_root.mkdir(parents=True, exist_ok=True)
        self.root = self.tmp_root / "root1"
        if self.root.exists():
            shutil.rmtree(self.root, ignore_errors=True)
        self.container = ServiceContainer.build(PathConfig(data_root=self.root))
        self.service = TaskService(self.container)

    def tearDown(self):
        shutil.rmtree(self.tmp_root, ignore_errors=True)

    def test_daily_task_create_and_postpone(self):
        task_id = self.service.create_daily_task({"title": "A", "task_date": today_str(), "priority": "高"})
        self.service.postpone_to_tomorrow(task_id)
        old = self.service.c.daily_repo.get(task_id)
        self.assertEqual(old["status"], "已推迟")

    def test_long_task_progress_clamp(self):
        task_id = self.service.create_long_task({"title": "L", "progress": 200})
        item = self.service.c.long_repo.get(task_id)
        self.assertEqual(item["progress"], 100)
        self.assertEqual(item["status"], "已完成")

    def test_switch_path(self):
        self.service.create_daily_task({"title": "B", "task_date": today_str()})
        new_root = self.tmp_root / "root2"
        ps = PathService(self.container.db.path_config)
        result = ps.switch_data_root(new_root)
        self.assertTrue(result.changed)
        self.assertTrue((new_root / "dailytrack.db").exists())


if __name__ == "__main__":
    unittest.main()
