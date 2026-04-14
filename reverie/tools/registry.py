from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .types import ToolHandler, ToolSpec


@dataclass(slots=True)
class ToolBinding:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}
        self._specs: dict[str, ToolSpec] = {}

    def register_tool(
        self,
        *,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: ToolHandler,
    ) -> None:
        self._handlers[name] = handler
        self._specs[name] = ToolSpec(name=name, description=description, input_schema=input_schema)

    def register_binding(self, binding: ToolBinding) -> None:
        self.register_tool(
            name=binding.name,
            description=binding.description,
            input_schema=binding.input_schema,
            handler=binding.handler,
        )

    def register_many(self, bindings: list[ToolBinding]) -> None:
        for binding in bindings:
            self.register_binding(binding)

    def get(self, name: str) -> ToolHandler | None:
        return self._handlers.get(name)

    def available_tools(self) -> list[ToolSpec]:
        return [self._specs[k] for k in sorted(self._specs.keys())]
