from __future__ import annotations

import re
from datetime import datetime

from .types import MemoryRecord


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
    return [t for t in tokens if len(t) >= 2]


def score_record(record: MemoryRecord, keywords: list[str]) -> float:
    haystack_title = record.title.lower()
    haystack_content = record.content.lower()
    tags_lower = [t.lower() for t in record.tags]

    hit = 0.0
    for kw in keywords:
        if kw in haystack_title:
            hit += 2.0
        if kw in haystack_content:
            hit += 1.0
        if any(kw in t for t in tags_lower):
            hit += 1.5

    recency_boost = max(0.0, 2.0 - (datetime.now() - record.updated_at).total_seconds() / 86400)
    return hit + record.importance + recency_boost * 0.2


def make_excerpt(text: str, max_len: int = 220) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[:max_len] + "..."
