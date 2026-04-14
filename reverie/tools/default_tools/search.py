from __future__ import annotations

import re
from typing import Any

from ..policy import ToolPermissionPolicy
from ..registry import ToolBinding


def search_files_tool(args: dict[str, Any], p: ToolPermissionPolicy) -> dict[str, Any]:
    regex = str(args["regex"])
    base = p.resolve_path(str(args.get("path", ".")))
    file_glob = str(args.get("file_glob", "**/*"))
    limit = int(args.get("limit", 30))
    pattern = re.compile(regex, flags=re.I)
    matches: list[dict[str, Any]] = []

    files = [base] if base.is_file() else list(base.glob(file_glob))
    for fp in files:
        if not fp.is_file():
            continue
        try:
            content = fp.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        for i, line in enumerate(content.splitlines(), start=1):
            if pattern.search(line):
                matches.append(
                    {
                        "path": str(fp.relative_to(p.workspace_root)),
                        "line": i,
                        "text": line[:300],
                    }
                )
                if len(matches) >= limit:
                    return {"count": len(matches), "matches": matches}

    return {"count": len(matches), "matches": matches}


def build_search_bindings() -> list[ToolBinding]:
    return [
        ToolBinding(
            name="search_files",
            handler=search_files_tool,
            description="Search files by regex",
            input_schema={"type": "object", "required": ["regex"]},
        )
    ]
