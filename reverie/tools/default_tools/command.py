from __future__ import annotations

import subprocess
from typing import Any

from ..policy import ToolPermissionPolicy
from ..registry import ToolBinding


def run_command_tool(args: dict[str, Any], p: ToolPermissionPolicy) -> dict[str, Any]:
    command = str(args["command"])
    timeout = p.clamp_command_timeout(args.get("timeout_seconds"))
    try:
        done = subprocess.run(
            ["/bin/bash", "-lc", command],
            cwd=str(p.workspace_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": done.returncode,
            "stdout": done.stdout[-4000:],
            "stderr": done.stderr[-4000:],
            "timeout_seconds": timeout,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": -1,
            "stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
            "timeout_seconds": timeout,
            "timed_out": True,
        }


def build_command_bindings() -> list[ToolBinding]:
    return [
        ToolBinding(
            name="run_command",
            handler=run_command_tool,
            description="Run a command in the workspace (timeout enforced)",
            input_schema={"type": "object", "required": ["command"]},
        )
    ]
