from __future__ import annotations

import shutil
from pathlib import Path


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def safe_copy_file(src: Path, dst: Path) -> Path:
    if not dst.exists():
        shutil.copy2(src, dst)
        return dst
    stem = dst.stem
    suffix = dst.suffix
    idx = 1
    while True:
        candidate = dst.with_name(f"{stem}_copy{idx}{suffix}")
        if not candidate.exists():
            shutil.copy2(src, candidate)
            return candidate
        idx += 1


def copy_dir_contents(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_dir_contents(item, target)
        else:
            safe_copy_file(item, target)
