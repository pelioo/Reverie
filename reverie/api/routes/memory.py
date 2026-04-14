from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..deps import get_dashboard_service
from ..schemas import MemoryOverviewResponse
from ..services.dashboard_service import DashboardService

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/overview", response_model=MemoryOverviewResponse)
def memory_overview(
    limit: int = Query(default=100, ge=1, le=500),
    service: DashboardService = Depends(get_dashboard_service),
) -> MemoryOverviewResponse:
    return MemoryOverviewResponse(**service.memory_overview(limit=limit))

