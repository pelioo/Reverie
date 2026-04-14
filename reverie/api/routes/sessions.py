from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_dashboard_service
from ..schemas import SessionStateResponse
from ..services.dashboard_service import DashboardService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}/state", response_model=SessionStateResponse)
def session_state(session_id: str, service: DashboardService = Depends(get_dashboard_service)) -> SessionStateResponse:
    data = service.session_state(session_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return SessionStateResponse(**data)

