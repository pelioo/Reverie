"""User-defined tools entry package.

Reverie tries to import `reverie.user_tools` on startup and calls
`get_user_tool_bindings()` to register additional tools.

Suggested usage:
1) Add a tool module in this package (e.g., hello.py)
2) Implement the tool function in that module
3) Import and register it in `get_user_tool_bindings()`
"""

from __future__ import annotations

from ..tools.registry import ToolBinding

from .user_tool_guide import user_tool_guide_tool
from .web_search import get_web_search_binding


def get_user_tool_bindings() -> list[ToolBinding]:
    """Return user-defined tool bindings."""

    return [
        ToolBinding(
            name="user_tool_guide",
            description="User tool development guide",
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=user_tool_guide_tool,
        ),
        # Web search tool
        get_web_search_binding(),
    ]