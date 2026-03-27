from __future__ import annotations

from fastapi import APIRouter

from ...models import EvaluationRunResponse


router = APIRouter(tags=["evaluation"])


@router.post("/evaluation/run", response_model=EvaluationRunResponse)
def run_evaluation() -> EvaluationRunResponse:
    # Placeholder: evaluation logic will consume documents/criteria.
    return EvaluationRunResponse(
        status="placeholder",
        message="Evaluation module is not implemented yet.",
    )

