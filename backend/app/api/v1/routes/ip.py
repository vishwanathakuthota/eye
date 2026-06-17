from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_ip_intelligence_service
from app.core.responses import error_response, success_response
from app.db.session import get_db
from app.services.ip_intelligence import IpIntelligenceService
from app.services.ip_validation import IpValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/ip")
def analyze_ip(
    ip: Annotated[str, Query(min_length=1)],
    db: Annotated[Session, Depends(get_db)],
    ip_intelligence: Annotated[
        IpIntelligenceService,
        Depends(get_ip_intelligence_service),
    ],
) -> JSONResponse:
    try:
        result = ip_intelligence.analyze(ip, db)
    except IpValidationError as exc:
        logger.info("ip_validation_failed", extra={"ip": ip})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                code="IP_INVALID",
                message=str(exc),
                details={"field": "ip"},
            ),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=success_response(result.model_dump(mode="json")),
    )
