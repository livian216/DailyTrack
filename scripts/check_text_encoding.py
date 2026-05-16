from __future__ import annotations

from pathlib import Path
import sys

# Common mojibake fragments seen in Chinese text encoding issues.
BAD_PATTERNS = [
    '锟', '鈥', '鏃', '閿', '鎿', '鍙', '浠', '澶', '璁', '闀', '棣',
]


def scan(root: Path) -> int:
    offenders = []
    for path in root.rglob('*.py'):
        if '.venv' in path.parts or '__pycache__' in path.parts:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except Exception as exc:
            offenders.append((path, f'READ_ERROR: {exc}'))
            continue
        for p in BAD_PATTERNS:
            if p in text:
                offenders.append((path, f'contains bad pattern: {p}'))
                break

    if offenders:
        print('Found potential text encoding issues:')
        for path, reason in offenders:
            print(f'- {path}: {reason}')
        return 1

    print('No obvious mojibake patterns found.')
    return 0


if __name__ == '__main__':
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('dailytrack')
    raise SystemExit(scan(base))
