from __future__ import annotations

from fastapi import FastAPI

from .api.main import api_router
from app.api import module_danh_gia, module_quan_ly, module_upload
from .core.config import settings
from .core.db import init_db


app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(api_router)
app.include_router(module_danh_gia.router)
app.include_router(module_upload.router)
app.include_router(module_quan_ly.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

