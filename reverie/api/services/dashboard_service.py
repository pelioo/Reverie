from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .memory_reader import MemoryReader
from .runtime_reader import RuntimeReader


@dataclass(slots=True)
class DashboardService:
    workspace_root: Path
    default_session_id: str = "default"
    runtime: RuntimeReader = field(init=False)
    memory: MemoryReader = field(init=False)

    def __post_init__(self) -> None:
        self.runtime = RuntimeReader(self.workspace_root)
        self.memory = MemoryReader(self.workspace_root)

    def now_iso(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def resolve_session_id(self, session_id: str | None) -> str | None:
        preferred = session_id or self.default_session_id
        return self.runtime.resolve_session_id(preferred)

    def health(self) -> dict[str, Any]:
        sessions, _, _ = self.runtime.counts()
        return {
            "ok": True,
            "runtime_dir": self.runtime.runtime_dir.exists(),
            "memory_dir": self.memory.memory_dir.exists(),
            "session_count": sessions,
            "memory_count": self.memory.memory_count(),
            "generated_at": self.now_iso(),
        }

    def session_state(self, session_id: str | None) -> dict[str, Any] | None:
        data = self.runtime.load_session(session_id)
        if not data:
            return None
        return {
            "session_id": str(data.get("session_id") or ""),
            "current_mode": str(data.get("current_mode") or "unknown"),
            "current_task_tree": data.get("current_task_tree") or [],
            "recent_tool_results": data.get("recent_tool_results") or [],
            "interrupt_flag": bool(data.get("interrupt_flag", False)),
            "sleep_until": data.get("sleep_until"),
            "current_active_goal": data.get("current_active_goal"),
            "last_user_input": data.get("last_user_input"),
            "last_model_response": data.get("last_model_response"),
            "last_memory_write": data.get("last_memory_write"),
            "total_turns": int(data.get("total_turns", 0)),
            "user_turns": int(data.get("user_turns", 0)),
            "autonomous_turns": int(data.get("autonomous_turns", 0)),
            "last_updated_at": data.get("last_updated_at"),
        }

    def dashboard_overview(self, session_id: str | None, *, activity_limit: int = 50, tool_limit: int = 20) -> dict[str, Any] | None:
        session = self.runtime.load_session(session_id)
        if not session:
            return None
        sid = str(session.get("session_id") or "")
        intent_rec = self.runtime.latest_intent(sid)
        recent_tools = self.runtime.list_tool_results(limit=tool_limit)

        mode = str(session.get("current_mode") or "unknown")
        intent = (intent_rec or {}).get("intent") or {}
        intent_kind = str(session.get("current_active_goal") or intent.get("kind") or "").strip()
        intensity, color = self._hero_by_mode(mode)

        stats = [
            {"label": "mode", "value": mode, "hint": f"workspace/runtime/sessions/{sid}.json"},
            {"label": "session", "value": sid},
            {"label": "active goal", "value": str(session.get("current_active_goal") or "-")},
            {
                "label": "last intent",
                "value": self._last_intent_label(intent_rec),
            },
            {"label": "total turns", "value": str(int(session.get("total_turns", 0)))},
            {"label": "autonomous turns", "value": str(int(session.get("autonomous_turns", 0)))},
            {"label": "recent tool results", "value": str(len(session.get("recent_tool_results") or []))},
            {"label": "checkpoint", "value": str(session.get("last_updated_at") or "-")},
        ]

        activity = self._build_activity(session, intent_rec, recent_tools, activity_limit)
        intent = self._build_intent_payload(intent_rec, session, recent_tools)

        return {
            "session": {
                "session_id": sid,
                "mode": mode,
                "active_goal": session.get("current_active_goal"),
                "last_updated_at": session.get("last_updated_at"),
            },
            "hero": {
                "mind_state": self._mind_state_by_mode(mode, intent_kind),
                "intensity": intensity,
                "color_hint": color,
            },
            "stats": stats,
            "intent": intent,
            "activity": activity,
            "generated_at": self.now_iso(),
        }

    def memory_overview(self, *, limit: int = 100) -> dict[str, Any]:
        counts, nodes, edges, groups = self.memory.workspace_artifacts_overview(limit=limit)
        edge_items = [{"from_": e["from"], "to": e["to"]} for e in edges]
        return {
            "counts": counts,
            "nodes": nodes,
            "edges": edge_items,
            "groups": groups,
            "generated_at": self.now_iso(),
        }

    def _build_activity(
        self,
        session: dict[str, Any],
        intent_rec: dict[str, Any] | None,
        tools: list[dict[str, Any]],
        limit: int,
    ) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        if intent_rec:
            intent = intent_rec.get("intent") or {}
            items.append(
                {
                    "time": str(intent_rec.get("recorded_at") or ""),
                    "kind": "intent",
                    "text": f"subconscious intent recorded: {intent.get('kind', 'unknown')}",
                }
            )

        for t in tools:
            tool_name = str(t.get("tool_name") or "tool")
            ok = bool(t.get("ok", False))
            raw = t.get("raw") or {}
            summary = self._tool_summary(tool_name, ok, raw)
            items.append(
                {
                    "time": str(t.get("created_at") or ""),
                    "kind": "tool",
                    "text": summary,
                }
            )

        for s in session.get("recent_tool_results") or []:
            items.append(
                {
                    "time": str(session.get("last_updated_at") or ""),
                    "kind": "result",
                    "text": str(s),
                }
            )

        items.append(
            {
                "time": str(session.get("last_updated_at") or ""),
                "kind": "scheduler",
                "text": f"session state persisted, mode={session.get('current_mode','unknown')}",
            }
        )

        items.sort(key=lambda x: x.get("time", ""), reverse=True)
        return items[:limit]

    def _build_intent_payload(
        self,
        intent_rec: dict[str, Any] | None,
        session: dict[str, Any],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        intent = (intent_rec or {}).get("intent") or {}
        tool_results = []
        for t in tools[:20]:
            raw = t.get("raw") or {}
            tool_results.append(
                {
                    "tool": str(t.get("tool_name") or "tool"),
                    "status": "ok" if bool(t.get("ok", False)) else "error",
                    "summary": self._tool_summary(str(t.get("tool_name") or "tool"), bool(t.get("ok", False)), raw),
                    "raw_path": str(t.get("_path") or ""),
                }
            )

        model_text = str(session.get("last_model_response") or "")
        return {
            "title": str(intent.get("kind") or session.get("current_active_goal") or "unknown"),
            "source": "subconscious_prompter",
            "priority": str(intent.get("priority") or "0.50"),
            "rationale": str(intent.get("rationale") or ""),
            "guided_prompt": str(intent.get("prompt") or ""),
            "model_thinking": self._extract_model_thinking(model_text),
            "tool_results": tool_results,
            "memory_write_path": self._extract_memory_write_path(model_text),
        }

    def _extract_model_thinking(self, text: str) -> str:
        if not text:
            return ""

        head = text.split("\n[tool-result]", 1)[0].split("[tool-result]", 1)[0].strip()
        if not head:
            return ""

        if head.startswith("["):
            end = head.find("]")
            if end != -1:
                maybe_body = head[end + 1 :].lstrip()
                if maybe_body:
                    return maybe_body
        return head

    def _extract_memory_write_path(self, text: str) -> str | None:
        if not text:
            return None
        for line in text.splitlines():
            if "Wrote file " in line:
                return line.split("Wrote file ", 1)[-1].split(",", 1)[0].strip()
        return None

    def _last_intent_label(self, intent_rec: dict[str, Any] | None) -> str:
        if not intent_rec:
            return "-"
        intent = intent_rec.get("intent") or {}
        kind = intent.get("kind") or "unknown"
        priority = intent.get("priority")
        return f"{kind} · p={priority}" if priority is not None else str(kind)

    def _tool_summary(self, tool_name: str, ok: bool, raw: dict[str, Any]) -> str:
        status = "ok" if ok else "error"
        if tool_name == "run_command":
            cmd = raw.get("command", "")
            return f"run_command {status}: {cmd}".strip()
        if tool_name == "write_file":
            path = raw.get("path", "")
            bytes_ = raw.get("bytes")
            return f"write_file {status}: {path} · bytes={bytes_}".strip()
        return f"{tool_name} {status}"

    def _hero_by_mode(self, mode: str) -> tuple[float, str]:
        m = mode.lower()
        if m == "idle":
            return 0.35, "slate"
        if m == "user":
            return 0.72, "indigo"
        return 0.55, "cyan"

    def _mind_state_by_mode(self, mode: str, intent_kind: str | None = None) -> str:
        kind = (intent_kind or "").strip().lower()
        allowed = {
            "reflect",
            "consolidate",
            "explore",
            "practice",
            "curate",
            "pursue_goal",
            "rest",
        }
        if kind in allowed:
            return kind

        m = mode.lower()
        if m == "idle":
            return "rest"
        if m == "user":
            return "practice"
        return "consolidate"
