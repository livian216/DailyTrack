from __future__ import annotations

from datetime import date, datetime, timedelta


def today_str() -> str:
    return date.today().isoformat()


def tomorrow_str() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def now_str() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def is_valid_date(value: str) -> bool:
    try:
        parse_date(value)
        return True
    except ValueError:
        return False


def days_until(due_date: str, base: str | None = None) -> int:
    base_date = parse_date(base) if base else date.today()
    return (parse_date(due_date) - base_date).days
