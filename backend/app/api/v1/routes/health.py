from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, object]:
    settings = get_settings()
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    return {
        "success": True,
        "data": {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        },
        "error": None,
        "meta": {
            "request_id": f"req_{uuid4().hex}",
            "timestamp": timestamp,
            "version": settings.app_version,
        },
    }
