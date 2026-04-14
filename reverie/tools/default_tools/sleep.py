from __future__ import annotations

from typing import Any

from ..policy import ToolPermissionPolicy
from ..registry import ToolBinding


def sleep_request_tool(args: dict[str, Any], p: ToolPermissionPolicy) -> dict[str, Any]:
    requested = float(args.get("requested_seconds", 0))
    approved = p.clamp_sleep(requested)
    reason = str(args.get("reason", ""))
    return {
        "requested_seconds": requested,
        "approved_seconds": approved,
        "reason": reason,
    }


def build_sleep_bindings() -> list[ToolBinding]:
    return [
        ToolBinding(
            name="sleep_request",
            handler=sleep_request_tool,
            description="Request sleep duration; clamped by policy",
            input_schema={"type": "object", "required": ["requested_seconds", "reason"]},
        )
    ]
