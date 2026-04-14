from __future__ import annotations

"""User tool guide module."""

from typing import Any

from ..tools.policy import ToolPermissionPolicy


def user_tool_guide_tool(_: dict[str, Any], __: ToolPermissionPolicy) -> dict[str, Any]:
    """Return a short guide for developing user tools."""

    guide = [
        "1) Add a module under reverie/user_tools/ (e.g., my_tool.py)",
        "2) Implement the tool function: def my_tool(args: dict[str, Any], policy: ToolPermissionPolicy) -> dict[str, Any]",
        "3) Import the function in reverie/user_tools/__init__.py",
        "4) Register a ToolBinding in get_user_tool_bindings() (name/description/input_schema/handler)",
        "5) Run the CLI and it will auto-load (no extra flags needed)",
    ]
    return {"title": "User Tool Development Guide", "steps": guide}
