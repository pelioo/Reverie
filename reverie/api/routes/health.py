from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import get_dashboard_service
from ..schemas import HealthResponse
from ..services.dashboard_service import DashboardService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(service: DashboardService = Depends(get_dashboard_service)) -> HealthResponse:
    return HealthResponse(**service.health())

