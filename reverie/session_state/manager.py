from __future__ import annotations

from datetime import timedelta

from .models import SessionState
from .store import SessionStateStore
from .utils import now


class SessionStateManager:
    def __init__(self, store: SessionStateStore, session_id: str) -> None:
        self.store = store
        self.session_id = session_id
        self.state = self.store.load(session_id) or SessionState(session_id=session_id)
        self.store.save(self.state)

    def on_turn_start(self, turn_id: str, mode: str, goal: str | None = None, user_input: str | None = None) -> None:
        self.state.current_turn_id = turn_id
        self.state.current_mode = mode
        self.state.current_active_goal = goal
        if goal:
            self.state.current_task_tree = [goal]
        if user_input:
            self.state.last_user_input = user_input
        self._touch()
        self.store.save(self.state)

    def on_turn_end(self, turn_type: str, response: str, memory_write: str | None = None) -> None:
        self.state.total_turns += 1
        if turn_type == "user":
            self.state.user_turns += 1
        else:
            self.state.autonomous_turns += 1

        self.state.last_model_response = response
        self.state.last_memory_write = memory_write
        self.state.current_turn_id = None
        self.state.current_mode = "idle"
        self._touch()
        self.store.save(self.state)

    def set_interrupt(self, value: bool) -> None:
        self.state.interrupt_flag = value
        self._touch()
        self.store.save(self.state)

    def add_tool_result(self, summary: str, keep_last: int = 8) -> None:
        if summary:
            self.state.recent_tool_results.append(summary)
        if len(self.state.recent_tool_results) > keep_last:
            self.state.recent_tool_results = self.state.recent_tool_results[-keep_last:]
        self._touch()
        self.store.save(self.state)

    def set_sleep(self, seconds: float) -> None:
        self.state.sleep_until = now() + timedelta(seconds=seconds)
        self.state.current_mode = "sleeping"
        self._touch()
        self.store.save(self.state)

    def clear_sleep(self) -> None:
        self.state.sleep_until = None
        if self.state.current_mode == "sleeping":
            self.state.current_mode = "idle"
        self._touch()
        self.store.save(self.state)

    def is_sleeping(self) -> bool:
        if not self.state.sleep_until:
            return False
        if now() < self.state.sleep_until:
            return True
        self.clear_sleep()
        return False

    def checkpoint(self) -> str:
        self._touch()
        self.store.save(self.state)
        return self.store.checkpoint(self.state)

    def _touch(self) -> None:
        self.state.last_updated_at = now()
