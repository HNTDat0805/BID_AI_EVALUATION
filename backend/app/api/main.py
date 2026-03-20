from fastapi import APIRouter

from .routes import auth, documents, evaluation


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(evaluation.router)

