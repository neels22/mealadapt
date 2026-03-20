"""
Shared helpers for API routes.
"""
from fastapi import HTTPException, status

from app.services.ai_service import AIBlocked, AIInvalidOutput, AIOutOfScope


def not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def bad_request(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def server_error(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


def raise_for_ai_error(error: Exception) -> None:
    if isinstance(error, AIOutOfScope):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "out_of_scope", "message": str(error)},
        )
    if isinstance(error, AIBlocked):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "blocked", "message": str(error)},
        )
    if isinstance(error, AIInvalidOutput):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "invalid_model_output", "message": str(error)},
        )
