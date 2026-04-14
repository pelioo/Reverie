from __future__ import annotations

import json
from pathlib import Path

from .models import SessionState
from .utils import now


class SessionStateStore:
    def __init__(self, base_dir: str = "runtime/sessions") -> None:
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        (self.base / "checkpoints").mkdir(parents=True, exist_ok=True)

    def load(self, session_id: str) -> SessionState | None:
        path = self.path_for(session_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return SessionState.from_json_dict(data)

    def path_for(self, session_id: str) -> Path:
        return self.base / f"{session_id}.json"

    def exists(self, session_id: str) -> bool:
        return self.path_for(session_id).exists()

    def save(self, session: SessionState) -> None:
        path = self.base / f"{session.session_id}.json"
        path.write_text(json.dumps(session.to_json_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def checkpoint(self, session: SessionState) -> str:
        ts = now().strftime("%Y%m%d-%H%M%S")
        path = self.base / "checkpoints" / f"{session.session_id}-{ts}.json"
        path.write_text(json.dumps(session.to_json_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)
