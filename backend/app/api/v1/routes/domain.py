from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_domain_intelligence_service
from app.core.responses import error_response, success_response
from app.db.session import get_db
from app.services.domain_intelligence import DomainIntelligenceService
from app.services.domain_validation import DomainValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/domain")
def analyze_domain(
    domain: Annotated[str, Query(min_length=1)],
    db: Annotated[Session, Depends(get_db)],
    domain_intelligence: Annotated[
        DomainIntelligenceService,
        Depends(get_domain_intelligence_service),
    ],
) -> JSONResponse:
    try:
        result = domain_intelligence.analyze(domain, db)
    except DomainValidationError as exc:
        logger.info("domain_validation_failed", extra={"domain": domain})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                code="DOMAIN_INVALID",
                message=str(exc),
                details={"field": "domain"},
            ),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=success_response(result.model_dump(mode="json")),
    )
