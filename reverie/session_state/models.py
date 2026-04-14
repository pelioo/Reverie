from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime

from .utils import now, parse_dt


@dataclass(slots=True)
class SessionState:
    session_id: str
    current_mode: str = "idle"
    current_turn_id: str | None = None
    current_task_tree: list[str] = field(default_factory=list)
    recent_tool_results: list[str] = field(default_factory=list)
    interrupt_flag: bool = False
    sleep_until: datetime | None = None
    current_active_goal: str | None = None
    last_user_input: str | None = None
    last_model_response: str | None = None
    last_memory_write: str | None = None
    total_turns: int = 0
    user_turns: int = 0
    autonomous_turns: int = 0
    last_updated_at: datetime = field(default_factory=now)

    def to_json_dict(self) -> dict:
        payload = asdict(self)
        payload["sleep_until"] = self.sleep_until.isoformat(timespec="seconds") if self.sleep_until else None
        payload["last_updated_at"] = self.last_updated_at.isoformat(timespec="seconds")
        return payload

    @classmethod
    def from_json_dict(cls, data: dict) -> SessionState:
        sleep_until = parse_dt(data.get("sleep_until"))
        updated = parse_dt(data.get("last_updated_at")) or now()
        return cls(
            session_id=data["session_id"],
            current_mode=data.get("current_mode", "idle"),
            current_turn_id=data.get("current_turn_id"),
            current_task_tree=data.get("current_task_tree", []),
            recent_tool_results=data.get("recent_tool_results", []),
            interrupt_flag=bool(data.get("interrupt_flag", False)),
            sleep_until=sleep_until,
            current_active_goal=data.get("current_active_goal"),
            last_user_input=data.get("last_user_input"),
            last_model_response=data.get("last_model_response"),
            last_memory_write=data.get("last_memory_write"),
            total_turns=int(data.get("total_turns", 0)),
            user_turns=int(data.get("user_turns", 0)),
            autonomous_turns=int(data.get("autonomous_turns", 0)),
            last_updated_at=updated,
        )
