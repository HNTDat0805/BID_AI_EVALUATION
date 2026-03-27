from __future__ import annotations

# Shim to make `uvicorn app.main:app --reload` work from the repository root.
# The actual FastAPI application lives in `backend/app/main.py`.

from backend.app.main import app  # noqa: F401

