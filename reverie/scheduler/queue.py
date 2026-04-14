from __future__ import annotations

from collections import deque
from typing import Optional

from ..orchestrator import InputEvent


class InputQueue:
    """In-memory FIFO queue with user-first semantics."""

    def __init__(self) -> None:
        self._events: deque[InputEvent] = deque()

    def put(self, event: InputEvent) -> None:
        self._events.append(event)

    def get(self) -> Optional[InputEvent]:
        if not self._events:
            return None
        return self._events.popleft()

    def has_user_input(self) -> bool:
        return bool(self._events)
