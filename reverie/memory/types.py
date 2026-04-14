from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


def _new_id() -> str:
    return f"mem-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"


@dataclass(slots=True)
class MemoryRecord:
    id: str
    kind: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    importance: float = 0.5
    related: list[str] = field(default_factory=list)

    @staticmethod
    def new_id() -> str:
        return _new_id()


@dataclass(slots=True)
class MemorySnippet:
    memory_id: str
    kind: str
    title: str
    excerpt: str
    score: float
    path: str
