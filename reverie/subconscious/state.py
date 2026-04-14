from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class SubconsciousState:
    autonomous_turn_count: int = 0
    last_intent_kind: Optional[str] = None
    last_intent_prompt: Optional[str] = None
    last_intent_rationale: Optional[str] = None
    last_turn_response: Optional[str] = None
    last_intent_at: Optional[datetime] = None
    last_cooldown_seconds: Optional[int] = None
    max_sleep_seconds: int = 5
