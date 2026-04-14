from __future__ import annotations

import os
from pathlib import Path

from .services.dashboard_service import DashboardService


def get_workspace_root() -> Path:
    root = os.getenv("REVERIE_WORKSPACE_ROOT", "workspace").strip() or "workspace"
    p = Path(root)
    if not p.is_absolute():
        p = Path.cwd() / p
    return p


def get_dashboard_service() -> DashboardService:
    return DashboardService(workspace_root=get_workspace_root())

