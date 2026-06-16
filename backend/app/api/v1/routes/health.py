from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.responses import success_response

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, object]:
    settings = get_settings()

    return success_response(
        {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        }
    )
