from __future__ import annotations

import sqlite3
from pathlib import Path

from dailytrack.config import APP_VERSION, PathConfig
from dailytrack.utils.file_utils import ensure_dirs


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS daily_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    task_date TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT '中',
    status TEXT NOT NULL DEFAULT '未开始',
    estimated_minutes INTEGER,
    source_type TEXT DEFAULT 'manual',
    source_long_task_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT
);
CREATE TABLE IF NOT EXISTS long_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    goal TEXT,
    start_date TEXT,
    due_date TEXT,
    priority TEXT NOT NULL DEFAULT '中',
    status TEXT NOT NULL DEFAULT '未开始',
    progress INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    archived_at TEXT
);
CREATE TABLE IF NOT EXISTS long_task_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    long_task_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT '未开始',
    sort_order INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(long_task_id) REFERENCES long_tasks(id)
);
CREATE TABLE IF NOT EXISTS progress_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    long_task_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(long_task_id) REFERENCES long_tasks(id)
);
CREATE TABLE IF NOT EXISTS daily_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_date TEXT NOT NULL UNIQUE,
    summary TEXT,
    unfinished_reason TEXT,
    tomorrow_focus TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS app_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_daily_tasks_task_date ON daily_tasks(task_date);
CREATE INDEX IF NOT EXISTS idx_daily_tasks_status ON daily_tasks(status);
CREATE INDEX IF NOT EXISTS idx_long_tasks_due_date ON long_tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_long_tasks_status ON long_tasks(status);
CREATE INDEX IF NOT EXISTS idx_daily_reviews_review_date ON daily_reviews(review_date);
"""


class Database:
    def __init__(self, path_config: PathConfig):
        self.path_config = path_config
        self._initialize_storage()

    @property
    def db_path(self) -> Path:
        return self.path_config.db_path

    def _initialize_storage(self) -> None:
        ensure_dirs(self.path_config.data_root, self.path_config.backups_dir, self.path_config.exports_dir)
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.execute("INSERT OR IGNORE INTO app_meta(key, value) VALUES ('schema_version', '1')")
            conn.execute(
                "INSERT OR IGNORE INTO app_meta(key, value) VALUES ('app_version', ?)",
                (APP_VERSION,),
            )
            conn.commit()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def smoke_test(self) -> None:
        with self.connect() as conn:
            conn.execute("SELECT value FROM app_meta WHERE key='schema_version'").fetchone()
