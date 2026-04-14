from __future__ import annotations

from pathlib import Path


class ToolPermissionPolicy:
    def __init__(
        self,
        workspace_root: str = ".",
        max_sleep_seconds: float = 5.0,
        max_command_seconds: float = 12.0,
    ) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.max_sleep_seconds = max_sleep_seconds
        self.max_command_seconds = max_command_seconds

    def resolve_path(self, rel_path: str) -> Path:
        rel = rel_path.strip()
        if not rel:
            raise ValueError("path cannot be empty")
        target = (self.workspace_root / rel).resolve()
        if self.workspace_root not in [target, *target.parents]:
            raise PermissionError(f"path escapes workspace: {rel_path}")
        return target

    def clamp_sleep(self, requested_seconds: float) -> float:
        safe = max(0.0, float(requested_seconds))
        return min(safe, self.max_sleep_seconds)

    def clamp_command_timeout(self, timeout_seconds: float | None) -> float:
        raw = self.max_command_seconds if timeout_seconds is None else float(timeout_seconds)
        raw = max(0.5, raw)
        return min(raw, self.max_command_seconds)
