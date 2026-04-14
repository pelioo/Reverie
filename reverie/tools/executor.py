from __future__ import annotations

from .normalizer import ToolResultNormalizer
from .policy import ToolPermissionPolicy
from .registry import ToolRegistry
from .types import ToolCall, ToolResult


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        policy: ToolPermissionPolicy,
        normalizer: ToolResultNormalizer,
    ) -> None:
        self.registry = registry
        self.policy = policy
        self.normalizer = normalizer

    def call_tool(self, call: ToolCall):
        handler = self.registry.get(call.name)
        if handler is None:
            result = ToolResult(tool_name=call.name, ok=False, raw={}, error=f"Unknown tool: {call.name}")
            return result, self.normalizer.summarize(result)

        try:
            raw = handler(call.arguments, self.policy)
            result = ToolResult(tool_name=call.name, ok=True, raw=raw)
        except Exception as exc:  # noqa: BLE001
            result = ToolResult(tool_name=call.name, ok=False, raw={}, error=str(exc))

        digest = self.normalizer.summarize(result)
        return result, digest
