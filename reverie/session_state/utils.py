from __future__ import annotations

from datetime import datetime


def now() -> datetime:
    return datetime.now()


def parse_dt(text: str | None) -> datetime | None:
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None
