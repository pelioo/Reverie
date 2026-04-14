from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SchedulerState:
    last_user_activity_at: datetime | None = None
    last_autonomous_turn_at: datetime | None = None
    max_idle_interval: float = 1.0
