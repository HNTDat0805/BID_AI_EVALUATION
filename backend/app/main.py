from __future__ import annotations

from fastapi import FastAPI

from .api.main import api_router
from .core.config import settings
from .core.db import init_db


app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(api_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

