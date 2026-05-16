from __future__ import annotations

from dataclasses import dataclass

from dailytrack.config import PathConfig
from dailytrack.database import Database
from dailytrack.repositories.daily_task_repository import DailyTaskRepository
from dailytrack.repositories.long_task_repository import LongTaskRepository
from dailytrack.repositories.progress_log_repository import ProgressLogRepository
from dailytrack.repositories.review_repository import ReviewRepository
from dailytrack.repositories.stage_repository import StageRepository
from dailytrack.utils.date_utils import is_valid_date, now_str, today_str, tomorrow_str


@dataclass
class ServiceContainer:
    db: Database
    daily_repo: DailyTaskRepository
    long_repo: LongTaskRepository
    stage_repo: StageRepository
    log_repo: ProgressLogRepository
    review_repo: ReviewRepository

    @classmethod
    def build(cls, path_config: PathConfig) -> 'ServiceContainer':
        db = Database(path_config)
        return cls(
            db=db,
            daily_repo=DailyTaskRepository(db),
            long_repo=LongTaskRepository(db),
            stage_repo=StageRepository(db),
            log_repo=ProgressLogRepository(db),
            review_repo=ReviewRepository(db),
        )


class TaskService:
    def __init__(self, container: ServiceContainer):
        self.c = container

    def _validate_title(self, title: str) -> None:
        if not title or not title.strip():
            raise ValueError('标题不能为空')

    def _validate_date(self, date_text: str) -> None:
        if not is_valid_date(date_text):
            raise ValueError('日期格式不合法，必须是 YYYY-MM-DD')

    def _validate_estimated(self, minutes) -> int | None:
        if minutes in (None, ''):
            return None
        value = int(minutes)
        if value < 0:
            raise ValueError('预计耗时必须为非负整数')
        return value

    def create_daily_task(self, payload: dict) -> int:
        self._validate_title(payload.get('title', ''))
        self._validate_date(payload.get('task_date', ''))
        payload['estimated_minutes'] = self._validate_estimated(payload.get('estimated_minutes'))
        payload['created_at'] = now_str()
        payload['updated_at'] = payload['created_at']
        if payload.get('status') == '已完成':
            payload['completed_at'] = now_str()
        return self.c.daily_repo.create(payload)

    def update_daily_task(self, task_id: int, payload: dict) -> None:
        self._validate_title(payload.get('title', ''))
        self._validate_date(payload.get('task_date', ''))
        payload['estimated_minutes'] = self._validate_estimated(payload.get('estimated_minutes'))
        payload['updated_at'] = now_str()
        payload['completed_at'] = now_str() if payload.get('status') == '已完成' else None
        self.c.daily_repo.update(task_id, payload)

    def list_today_tasks(self) -> list[dict]:
        return self.c.daily_repo.list_by_date(today_str())

    def list_tasks_for_date(self, task_date: str) -> list[dict]:
        self._validate_date(task_date)
        return self.c.daily_repo.list_by_date(task_date)

    def complete_daily_task(self, task_id: int) -> None:
        task = self.c.daily_repo.get(task_id)
        if not task:
            raise ValueError('任务不存在')
        task['status'] = '已完成'
        task['updated_at'] = now_str()
        task['completed_at'] = now_str()
        self.c.daily_repo.update(task_id, task)

    def postpone_to_tomorrow(self, task_id: int) -> int:
        task = self.c.daily_repo.get(task_id)
        if not task:
            raise ValueError('任务不存在')
        task['status'] = '已推迟'
        task['updated_at'] = now_str()
        self.c.daily_repo.update(task_id, task)
        new_task = {
            'title': task['title'],
            'description': task.get('description'),
            'task_date': tomorrow_str(),
            'priority': task['priority'],
            'status': '未开始',
            'estimated_minutes': task.get('estimated_minutes'),
            'source_type': 'postponed',
            'source_long_task_id': task.get('source_long_task_id'),
        }
        return self.create_daily_task(new_task)

    def delete_daily_task(self, task_id: int) -> None:
        self.c.daily_repo.delete(task_id)

    def create_long_task(self, payload: dict) -> int:
        self._validate_title(payload.get('title', ''))
        if payload.get('start_date'):
            self._validate_date(payload['start_date'])
        if payload.get('due_date'):
            self._validate_date(payload['due_date'])
        progress = int(payload.get('progress', 0))
        payload['progress'] = max(0, min(progress, 100))
        payload['created_at'] = now_str()
        payload['updated_at'] = payload['created_at']
        if payload['progress'] == 100 or payload.get('status') == '已完成':
            payload['status'] = '已完成'
            payload['completed_at'] = now_str()
        return self.c.long_repo.create(payload)

    def update_long_task(self, task_id: int, payload: dict) -> None:
        self._validate_title(payload.get('title', ''))
        if payload.get('start_date'):
            self._validate_date(payload['start_date'])
        if payload.get('due_date'):
            self._validate_date(payload['due_date'])
        progress = int(payload.get('progress', 0))
        payload['progress'] = max(0, min(progress, 100))
        if payload['progress'] == 100:
            payload['status'] = '已完成'
            payload['completed_at'] = now_str()
        payload['updated_at'] = now_str()
        self.c.long_repo.update(task_id, payload)

    def list_long_tasks(self) -> list[dict]:
        return self.c.long_repo.list_all()

    def list_archived_long_tasks(self, keyword: str = '') -> list[dict]:
        rows = [x for x in self.c.long_repo.list_all() if x.get('status') == '已归档']
        if keyword:
            kw = keyword.lower()
            rows = [x for x in rows if kw in (x.get('title') or '').lower()]
        return rows

    def delete_long_task(self, task_id: int) -> None:
        self.c.long_repo.delete(task_id)

    def archive_long_task(self, task_id: int) -> None:
        task = self.c.long_repo.get(task_id)
        if not task:
            raise ValueError('长线任务不存在')
        task['status'] = '已归档'
        task['archived_at'] = now_str()
        task['updated_at'] = now_str()
        self.c.long_repo.update(task_id, task)

    def generate_daily_from_long_task(self, long_task_id: int, payload: dict) -> int:
        parent = self.c.long_repo.get(long_task_id)
        if not parent:
            raise ValueError('长线任务不存在')
        payload['source_type'] = 'long_task'
        payload['source_long_task_id'] = long_task_id
        payload['status'] = '未开始'
        return self.create_daily_task(payload)

    def list_stages(self, long_task_id: int) -> list[dict]:
        return self.c.stage_repo.list_by_task(long_task_id)

    def create_stage(self, payload: dict) -> int:
        self._validate_title(payload.get('title', ''))
        payload['created_at'] = now_str()
        payload['updated_at'] = payload['created_at']
        return self.c.stage_repo.create(payload)

    def update_stage(self, stage_id: int, payload: dict) -> None:
        self._validate_title(payload.get('title', ''))
        payload['updated_at'] = now_str()
        self.c.stage_repo.update(stage_id, payload)

    def delete_stage(self, stage_id: int) -> None:
        self.c.stage_repo.delete(stage_id)

    def create_progress_log(self, payload: dict) -> int:
        if not payload.get('content', '').strip():
            raise ValueError('日志内容不能为空')
        self._validate_date(payload.get('log_date', ''))
        payload['created_at'] = now_str()
        return self.c.log_repo.create(payload)

    def list_progress_logs(self, long_task_id: int) -> list[dict]:
        return self.c.log_repo.list_by_task(long_task_id)

    def load_review(self, review_date: str) -> dict | None:
        self._validate_date(review_date)
        return self.c.review_repo.get_by_date(review_date)

    def list_reviews(self) -> list[dict]:
        return self.c.review_repo.list_all()

    def save_review(self, payload: dict) -> None:
        self._validate_date(payload.get('review_date', ''))
        ts = now_str()
        payload['created_at'] = ts
        payload['updated_at'] = ts
        self.c.review_repo.upsert(payload)
