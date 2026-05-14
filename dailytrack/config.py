from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "DailyTrack"
APP_VERSION = "1.0.0"
PUBLISHER = "DailyTrack Project"

# 默认数据目录（可迁移）
DEFAULT_DATA_ROOT = Path(os.getenv("APPDATA", str(Path.home()))) / APP_NAME
def _get_app_base_dir() -> Path:
    # 打包后：放在 exe 所在目录；开发时：放在项目根目录
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


APP_BASE_DIR = _get_app_base_dir()
CONFIG_FILE = APP_BASE_DIR / "app_config.json"
# 兼容历史版本（曾放在 %APPDATA%）
LEGACY_CONFIG_FILE = (Path(os.getenv("APPDATA", str(Path.home()))) / f"{APP_NAME}Config" / "app_config.json")

DAILY_PRIORITIES = ["高", "中", "低"]
DAILY_STATUSES = ["未开始", "进行中", "已完成", "已推迟", "已取消"]
LONG_STATUSES = ["未开始", "进行中", "已完成", "已暂停", "已归档"]
STAGE_STATUSES = ["未开始", "进行中", "已完成", "已暂停"]


@dataclass
class PathConfig:
    data_root: Path

    @property
    def db_path(self) -> Path:
        return self.data_root / "dailytrack.db"

    @property
    def backups_dir(self) -> Path:
        return self.data_root / "backups"

    @property
    def exports_dir(self) -> Path:
        return self.data_root / "exports"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _read_config(path: Path) -> dict | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def load_path_config() -> PathConfig:
    ensure_dir(DEFAULT_DATA_ROOT)

    payload = _read_config(CONFIG_FILE)
    if payload is None:
        payload = _read_config(LEGACY_CONFIG_FILE)
        # 首次发现旧配置时自动搬到程序目录
        if payload is not None:
            CONFIG_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    data_root = DEFAULT_DATA_ROOT
    if payload:
        configured = payload.get("data_root_path")
        if configured:
            data_root = Path(configured)
    return PathConfig(data_root=data_root)


def save_path_config(config: PathConfig) -> None:
    payload = {"data_root_path": str(config.data_root)}
    CONFIG_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
