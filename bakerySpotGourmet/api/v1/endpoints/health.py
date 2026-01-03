from typing import Dict

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    Returns 200 OK if the service is running.
    """
    return {"status": "ok"}


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, str]:
    """
    Readiness probe for k8s/platforms.
    Checks if the service is ready to accept traffic (e.g. DB connection).
    """
    # TODO: Add DB check later
    return {"status": "ready"}


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe for k8s/platforms.
    Checks if the application is alive.
    """
    return {"status": "alive"}
