from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_report_history_service
from app.core.responses import error_response, success_response
from app.db.session import get_db
from app.services.report_history import (
    ReportHistoryService,
    ReportNotFoundError,
    ReportValidationError,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/reports")
def list_reports(
    db: Annotated[Session, Depends(get_db)],
    report_history: Annotated[
        ReportHistoryService,
        Depends(get_report_history_service),
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> JSONResponse:
    result = report_history.list_reports(db=db, limit=limit, offset=offset)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=success_response(result.model_dump(mode="json")),
    )


@router.get("/reports/{report_id}")
def get_report(
    report_id: Annotated[str, Path(min_length=1, max_length=84)],
    db: Annotated[Session, Depends(get_db)],
    report_history: Annotated[
        ReportHistoryService,
        Depends(get_report_history_service),
    ],
) -> JSONResponse:
    try:
        result = report_history.get_report(db=db, report_id=report_id)
    except ReportValidationError as exc:
        logger.info("report_validation_failed", extra={"source": "reports"})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                code="REPORT_INVALID",
                message=str(exc),
                details={"field": "report_id"},
            ),
        )
    except ReportNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="REPORT_NOT_FOUND",
                message=str(exc),
                details={"report_id": report_id},
            ),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=success_response(result.model_dump(mode="json")),
    )
