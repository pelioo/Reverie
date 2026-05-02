from __future__ import annotations

import os
import subprocess
from typing import Any

from ..policy import ToolPermissionPolicy
from ..registry import ToolBinding


def _is_windows() -> bool:
    return os.name == "nt"


def _build_shell_cmd(command: str) -> list[str]:
    if _is_windows():
        # Use cmd.exe on Windows - better compatibility with Unix-style commands
        return ["cmd", "/c", command]
    return ["/bin/bash", "-lc", command]


def run_command_tool(args: dict[str, Any], p: ToolPermissionPolicy) -> dict[str, Any]:
    command = str(args["command"])
    timeout = p.clamp_command_timeout(args.get("timeout_seconds"))
    shell_cmd = _build_shell_cmd(command)
    try:
        done = subprocess.run(
            shell_cmd,
            cwd=str(p.workspace_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": done.returncode,
            "stdout": (done.stdout or "")[-4000:],
            "stderr": (done.stderr or "")[-4000:],
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
