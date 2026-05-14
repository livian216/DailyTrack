from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from dailytrack.config import DEFAULT_DATA_ROOT, PathConfig, save_path_config
from dailytrack.database import Database
from dailytrack.utils.file_utils import copy_dir_contents, ensure_dirs


@dataclass
class MigrationResult:
    old_root: Path
    new_root: Path
    changed: bool
    cleaned_old_root: bool


class PathService:
    def __init__(self, current: PathConfig):
        self.current = current

    def switch_data_root(self, new_root: Path, cleanup_old_root: bool = True) -> MigrationResult:
        old_root = self.current.data_root.resolve()
        new_root = new_root.resolve()
        if old_root == new_root:
            return MigrationResult(old_root=old_root, new_root=new_root, changed=False, cleaned_old_root=False)

        ensure_dirs(new_root, new_root / "backups", new_root / "exports")

        old_db = old_root / "dailytrack.db"
        new_db = new_root / "dailytrack.db"

        # 关键修复：始终让新目录主库文件名固定为 dailytrack.db，避免“复制到 *_copy1.db”导致重启后读错库
        if old_db.exists():
            if new_db.exists():
                backup_target = new_root / "dailytrack_pre_migration_backup.db"
                shutil.copy2(new_db, backup_target)
            shutil.copy2(old_db, new_db)

        copy_dir_contents(old_root / "backups", new_root / "backups")
        copy_dir_contents(old_root / "exports", new_root / "exports")

        # 验证新目录数据库可用
        new_cfg = PathConfig(data_root=new_root)
        Database(new_cfg).smoke_test()

        # 持久化新路径（固定配置目录）
        save_path_config(new_cfg)
        self.current = new_cfg

        cleaned = False
        # 可选：将旧目录清理，形成“剪切”效果
        if cleanup_old_root and old_root.exists():
            try:
                for child in old_root.iterdir():
                    if child.is_dir():
                        shutil.rmtree(child, ignore_errors=True)
                    else:
                        child.unlink(missing_ok=True)
                cleaned = True
            except Exception:
                cleaned = False

        return MigrationResult(old_root=old_root, new_root=new_root, changed=True, cleaned_old_root=cleaned)

    def reset_to_default(self, cleanup_old_root: bool = True) -> MigrationResult:
        return self.switch_data_root(DEFAULT_DATA_ROOT, cleanup_old_root=cleanup_old_root)
