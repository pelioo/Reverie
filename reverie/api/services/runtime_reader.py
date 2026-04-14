from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RuntimeReader:
    workspace_root: Path

    @property
    def runtime_dir(self) -> Path:
        return self.workspace_root / "runtime"

    @property
    def sessions_dir(self) -> Path:
        return self.runtime_dir / "sessions"

    @property
    def intents_dir(self) -> Path:
        return self.runtime_dir / "subconscious_intents"

    @property
    def tool_results_dir(self) -> Path:
        return self.runtime_dir / "tool_results"

    def list_session_ids(self) -> list[str]:
        if not self.sessions_dir.exists():
            return []
        ids: list[str] = []
        for p in self.sessions_dir.glob("*.json"):
            if p.is_file():
                ids.append(p.stem)
        return sorted(ids)

    def resolve_session_id(self, session_id: str | None) -> str | None:
        ids = self.list_session_ids()
        if not ids:
            return None
        if session_id and session_id in ids:
            return session_id
        if session_id in {None, "", "latest"}:
            latest = self._latest_file(self.sessions_dir)
            return latest.stem if latest else ids[0]
        if session_id == "default" and "default" in ids:
            return "default"
        return ids[0]

    def load_session(self, session_id: str | None = None) -> dict[str, Any] | None:
        sid = self.resolve_session_id(session_id)
        if sid is None:
            return None
        p = self.sessions_dir / f"{sid}.json"
        return self._read_json(p)

    def list_intents(self, session_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if not self.intents_dir.exists():
            return []
        all_items: list[dict[str, Any]] = []
        for p in self.intents_dir.glob("*.json"):
            data = self._read_json(p)
            if not data:
                continue
            if session_id and data.get("session_id") != session_id:
                continue
            data["_path"] = str(p.relative_to(self.workspace_root))
            all_items.append(data)
        all_items.sort(key=lambda x: x.get("recorded_at", ""), reverse=True)
        return all_items[:limit]

    def latest_intent(self, session_id: str | None = None) -> dict[str, Any] | None:
        intents = self.list_intents(session_id=session_id, limit=1)
        return intents[0] if intents else None

    def list_tool_results(self, limit: int = 50, since: str | None = None) -> list[dict[str, Any]]:
        if not self.tool_results_dir.exists():
            return []
        items: list[dict[str, Any]] = []
        since_dt = self._parse_dt(since) if since else None
        for p in self.tool_results_dir.glob("*.json"):
            data = self._read_json(p)
            if not data:
                continue
            created = data.get("created_at")
            created_dt = self._parse_dt(created)
            if since_dt and created_dt and created_dt < since_dt:
                continue
            data["_path"] = str(p.relative_to(self.workspace_root))
            items.append(data)
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]

    def counts(self) -> tuple[int, int, int]:
        sessions = len(self.list_session_ids())
        intents = len(list(self.intents_dir.glob("*.json"))) if self.intents_dir.exists() else 0
        tools = len(list(self.tool_results_dir.glob("*.json"))) if self.tool_results_dir.exists() else 0
        return sessions, intents, tools

    def _read_json(self, path: Path) -> dict[str, Any] | None:
        if not path.exists() or not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _latest_file(self, directory: Path) -> Path | None:
        if not directory.exists():
            return None
        files = [p for p in directory.glob("*.json") if p.is_file()]
        if not files:
            return None
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return files[0]

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

