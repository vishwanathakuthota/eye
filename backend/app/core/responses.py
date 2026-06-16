from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.core.config import get_settings


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def new_request_id() -> str:
    return f"req_{uuid4().hex}"


def success_response(data: Any, request_id: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": {
            "request_id": request_id or new_request_id(),
            "timestamp": utc_now_iso(),
            "version": settings.app_version,
        },
    }


def error_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "meta": {
            "request_id": request_id or new_request_id(),
            "timestamp": utc_now_iso(),
            "version": settings.app_version,
        },
    }
