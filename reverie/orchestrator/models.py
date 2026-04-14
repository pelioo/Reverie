from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


def _id() -> str:
    return uuid4().hex


@dataclass(slots=True)
class InputEvent:
    id: str = field(default_factory=_id)
    source: str = "cli"
    session_id: str = "default"
    user_id: Optional[str] = None
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    priority: int = 100
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class AutonomousIntent:
    id: str = field(default_factory=_id)
    kind: str = "explore"
    prompt: str = ""
    rationale: str = ""
    priority: float = 0.5
    suggested_tools: list[str] = field(default_factory=list)
    expected_memory_write: bool = False
    cooldown_hint_seconds: Optional[int] = None


@dataclass(slots=True)
class TurnResult:
    turn_type: str
    response: str
    memory_write: Optional[str] = None
