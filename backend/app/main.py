from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.main import api_router
from app.api import module_quan_ly, module_upload
from .core.config import settings
from .core.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(api_router)
app.include_router(module_upload.router)
app.include_router(module_quan_ly.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

