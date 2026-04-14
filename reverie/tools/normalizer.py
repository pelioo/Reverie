from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .types import ToolResult, ToolResultDigest


class ToolResultNormalizer:
    def __init__(self, raw_dir: str = "runtime/tool_results", workspace_root: str | None = None) -> None:
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else None

    def summarize(self, result: ToolResult) -> ToolResultDigest:
        if result.raw_ref is None:
            result.raw_ref = self._persist_raw(result)
        summary = self._make_summary(result)
        key_facts = self._make_key_facts(result)
        next_implications = [
            "If you need more detail, read the raw_ref file.",
            "Only inject the summary into context to avoid prompt bloat.",
        ]
        token_estimate = max(1, len(summary) // 4)
        return ToolResultDigest(
            tool_name=result.tool_name,
            raw_ref=result.raw_ref,
            summary=summary,
            key_facts=key_facts,
            next_implications=next_implications,
            token_estimate=token_estimate,
        )

    def _persist_raw(self, result: ToolResult) -> str:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"{stamp}-{result.tool_name}-{uuid4().hex[:6]}.json"
        path = self.raw_dir / name
        payload = {
            "tool_name": result.tool_name,
            "ok": result.ok,
            "error": result.error,
            "raw": result.raw,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if self.workspace_root is not None:
            try:
                return str(path.resolve().relative_to(self.workspace_root))
            except ValueError:
                pass
        return str(path)

    def _make_summary(self, result: ToolResult) -> str:
        if not result.ok:
            return f"{result.tool_name} failed: {result.error}"
        if result.tool_name == "sleep_request":
            return (
                f"Sleep request processed: requested {result.raw.get('requested_seconds')}s, "
                f"approved {result.raw.get('approved_seconds')}s"
            )
        if result.tool_name == "run_command":
            command = result.raw.get("command")
            stdout = result.raw.get("stdout")
            stdout = stdout if len(stdout) < 200 else stdout[:200] + "..."
            summary = (
                f"Command Completed: {command}.\n"
                f"{stdout}"
            )
            return summary
        if result.tool_name == "read_file":
            truncated = result.raw.get("truncated")
            suffix = " (truncated)" if truncated else ""
            return f"Read file {result.raw.get('path')}{suffix}"
        if result.tool_name == "write_file":
            return f"Wrote file {result.raw.get('path')}, bytes={result.raw.get('bytes')}"
        if result.tool_name == "search_files":
            return f"Search completed, hits {result.raw.get('count', 0)}"
        if result.tool_name == "memory_search":
            return f"Memory search completed, hits {result.raw.get('count', 0)}"
        if result.tool_name == "memory_write":
            return f"Memory written: {result.raw.get('title')}"
        return f"{result.tool_name} succeeded"

    def _make_key_facts(self, result: ToolResult) -> list[str]:
        if not result.ok:
            return [f"error={result.error}"]
        facts: list[str] = []
        for key in ("path", "count", "approved_seconds", "returncode", "bytes"):
            if key in result.raw:
                facts.append(f"{key}={result.raw[key]}")
        if result.tool_name == "read_file":
            facts.append(f"truncated={result.raw.get('truncated', False)}")
        if not facts:
            facts.append("ok=true")
        return facts[:6]
