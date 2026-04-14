from __future__ import annotations

from typing import Any

from ..policy import ToolPermissionPolicy
from ..registry import ToolBinding


def read_file_tool(args: dict[str, Any], p: ToolPermissionPolicy) -> dict[str, Any]:
    path = p.resolve_path(str(args["path"]))
    max_chars = int(args.get("max_chars", 4000))
    text = path.read_text(encoding="utf-8")
    truncated = len(text) > max_chars
    return {
        "path": str(path.relative_to(p.workspace_root)),
        "content": text[:max_chars],
        "truncated": truncated,
    }


def write_file_tool(args: dict[str, Any], p: ToolPermissionPolicy) -> dict[str, Any]:
    path = p.resolve_path(str(args["path"]))
    content = str(args.get("content", ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"path": str(path.relative_to(p.workspace_root)), "bytes": len(content.encode("utf-8"))}


def build_file_io_bindings() -> list[ToolBinding]:
    return [
        ToolBinding(
            name="read_file",
            handler=read_file_tool,
            description="Read a text file in the workspace",
            input_schema={"type": "object", "required": ["path"]},
        ),
        ToolBinding(
            name="write_file",
            handler=write_file_tool,
            description="Write a file in the workspace",
            input_schema={"type": "object", "required": ["path", "content"]},
        ),
    ]
