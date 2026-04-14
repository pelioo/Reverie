from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..deps import get_dashboard_service
from ..schemas import DashboardOverviewResponse
from ..services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def dashboard_overview(
    session_id: str | None = Query(default=None),
    activity_limit: int = Query(default=50, ge=1, le=300),
    tool_limit: int = Query(default=20, ge=1, le=100),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOverviewResponse:
    data = service.dashboard_overview(session_id=session_id, activity_limit=activity_limit, tool_limit=tool_limit)
    if not data:
        raise HTTPException(status_code=404, detail="No session state found")
    return DashboardOverviewResponse(**data)

