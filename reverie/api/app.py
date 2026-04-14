from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.dashboard import router as dashboard_router
from .routes.health import router as health_router
from .routes.memory import router as memory_router
from .routes.sessions import router as sessions_router


def create_app() -> FastAPI:
    app = FastAPI(title="Reverie API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(dashboard_router)
    app.include_router(memory_router)
    app.include_router(sessions_router)

    return app


app = create_app()

