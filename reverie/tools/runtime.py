from __future__ import annotations

import importlib
from typing import Any

from ..memory import MemoryManager
from .builtin import register_builtin_tools
from .executor import ToolExecutor
from .normalizer import ToolResultNormalizer
from .policy import ToolPermissionPolicy
from .registry import ToolBinding, ToolRegistry
from .types import ToolCall, ToolResult, ToolResultDigest, ToolSpec


class ToolRuntime:
    def __init__(self, executor: ToolExecutor) -> None:
        self.executor = executor

    def call_tool(self, call: ToolCall) -> tuple[ToolResult, ToolResultDigest]:
        return self.executor.call_tool(call)

    def available_tools(self) -> list[ToolSpec]:
        return self.executor.registry.available_tools()

    def summarize_result(self, result: ToolResult) -> ToolResultDigest:
        return self.executor.normalizer.summarize(result)

    def openai_tools(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []
        for spec in self.available_tools():
            schema = dict(spec.input_schema) if spec.input_schema else {}
            schema.setdefault("type", "object")
            schema.setdefault("properties", {})
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": spec.name,
                        "description": spec.description,
                        "parameters": schema,
                    },
                }
            )
        return tools

    def format_execution_log(self, requested_tool: str, result: ToolResult, digest: ToolResultDigest) -> str:
        lines = [
            f"Requested tool: {requested_tool}",
            f"Executed tool: {digest.tool_name}",
            f"Status: {'ok' if result.ok else 'error'}",
            f"Summary: {digest.summary}",
        ]
        if digest.key_facts:
            lines.append(f"Key facts: {', '.join(digest.key_facts)}")
        if digest.raw_ref:
            lines.append(f"Raw result: {digest.raw_ref}")
        return "\n".join(lines)


class ToolRuntimeBuilder:
    def __init__(
        self,
        *,
        workspace_root: str = ".",
        max_sleep_seconds: float = 5.0,
        max_command_seconds: float = 12.0,
        raw_dir: str = "runtime/tool_results",
    ) -> None:
        self.registry = ToolRegistry()
        self.policy = ToolPermissionPolicy(
            workspace_root=workspace_root,
            max_sleep_seconds=max_sleep_seconds,
            max_command_seconds=max_command_seconds,
        )
        self.normalizer = ToolResultNormalizer(raw_dir=raw_dir, workspace_root=workspace_root)

    def register_tool(
        self,
        *,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler,
    ) -> "ToolRuntimeBuilder":
        self.registry.register_tool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
        )
        return self

    def register_binding(self, binding: ToolBinding) -> "ToolRuntimeBuilder":
        self.registry.register_binding(binding)
        return self

    def register_many(self, bindings: list[ToolBinding]) -> "ToolRuntimeBuilder":
        self.registry.register_many(bindings)
        return self

    def build(self) -> ToolRuntime:
        return ToolRuntime(
            executor=ToolExecutor(
                registry=self.registry,
                policy=self.policy,
                normalizer=self.normalizer,
            )
        )


def load_user_tool_bindings(module_path: str = "reverie.user_tools") -> list[ToolBinding]:
    """Load external user tool bindings from `get_user_tool_bindings()`.

    Default module path is `reverie.user_tools` package.
    If module does not exist, returns empty list.
    """

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return []

    loader = getattr(module, "get_user_tool_bindings", None)
    if loader is None:
        return []

    bindings = loader()
    if not isinstance(bindings, list):
        return []
    return [b for b in bindings if isinstance(b, ToolBinding)]


def create_default_tool_runtime(
    memory_manager: MemoryManager,
    workspace_root: str = ".",
    max_sleep_seconds: float = 5.0,
    max_command_seconds: float = 12.0,
    raw_dir: str = "runtime/tool_results",
) -> ToolRuntime:
    builder = ToolRuntimeBuilder(
        workspace_root=workspace_root,
        max_sleep_seconds=max_sleep_seconds,
        max_command_seconds=max_command_seconds,
        raw_dir=raw_dir,
    )
    register_builtin_tools(builder.registry, memory_manager)
    builder.register_many(load_user_tool_bindings())
    return builder.build()
