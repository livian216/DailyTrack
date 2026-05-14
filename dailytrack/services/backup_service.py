from __future__ import annotations

import shutil
from pathlib import Path

from dailytrack.utils.date_utils import now_str


class BackupService:
    def create_backup(self, db_path: Path, backups_dir: Path) -> Path:
        name = f"dailytrack_backup_{now_str().replace('-', '').replace(':', '').replace(' ', '_')}.db"
        out = backups_dir / name
        shutil.copy2(db_path, out)
        return out
