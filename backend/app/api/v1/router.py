from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes.domain import router as domain_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.ip import router as ip_router

api_router = APIRouter()
api_router.include_router(domain_router, tags=["domain"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(ip_router, tags=["ip"])
