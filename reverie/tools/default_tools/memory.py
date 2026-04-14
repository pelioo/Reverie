from __future__ import annotations

from typing import Any

from ...memory import MemoryManager, MemoryRecord
from ..policy import ToolPermissionPolicy
from ..registry import ToolBinding


def memory_search_tool(args: dict[str, Any], _: ToolPermissionPolicy, memory_manager: MemoryManager) -> dict[str, Any]:
    query = str(args["query"])
    top_k = int(args.get("top_k", 4))
    snippets = memory_manager.search(query=query, top_k=top_k)
    payload = [
        {
            "id": item.memory_id,
            "kind": item.kind,
            "title": item.title,
            "path": item.path,
            "score": item.score,
            "excerpt": item.excerpt,
        }
        for item in snippets
    ]
    return {"count": len(payload), "items": payload}


def memory_write_tool(args: dict[str, Any], _: ToolPermissionPolicy, memory_manager: MemoryManager) -> dict[str, Any]:
    record = MemoryRecord(
        id=MemoryRecord.new_id(),
        kind=str(args.get("kind", "episodic")),
        title=str(args.get("title", "Tool Memory")),
        content=str(args.get("content", "")),
        source=str(args.get("source", "tool_runtime")),
        importance=float(args.get("importance", 0.4)),
    )
    path = memory_manager.write_memory(record)
    return {"path": path, "kind": record.kind, "title": record.title}


def build_memory_bindings(memory_manager: MemoryManager) -> list[ToolBinding]:
    return [
        ToolBinding(
            name="memory_search",
            handler=lambda args, p: memory_search_tool(args, p, memory_manager),
            description="Search Markdown memories",
            input_schema={"type": "object", "required": ["query"]},
        ),
        ToolBinding(
            name="memory_write",
            handler=lambda args, p: memory_write_tool(args, p, memory_manager),
            description="Write a Markdown memory",
            input_schema={"type": "object", "required": ["title", "content"]},
        ),
    ]
