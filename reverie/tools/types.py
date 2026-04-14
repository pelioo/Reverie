from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from .policy import ToolPermissionPolicy


@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(slots=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(slots=True)
class ToolResult:
    tool_name: str
    ok: bool
    raw: dict[str, Any]
    error: str | None = None
    raw_ref: str | None = None


@dataclass(slots=True)
class ToolResultDigest:
    tool_name: str
    raw_ref: str
    summary: str
    key_facts: list[str]
    next_implications: list[str]
    token_estimate: int


ToolHandler = Callable[[dict[str, Any], ToolPermissionPolicy], dict[str, Any]]
