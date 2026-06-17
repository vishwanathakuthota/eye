from __future__ import annotations

import logging
import re

from sqlalchemy.orm import Session

from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportDetailResult, ReportListResult

REPORT_ID_PATTERN = re.compile(r"^(rep|ipr)_[a-fA-F0-9A-Za-z_-]{3,80}$")

logger = logging.getLogger(__name__)


class ReportValidationError(ValueError):
    pass


class ReportNotFoundError(LookupError):
    pass


class ReportHistoryService:
    def list_reports(self, *, db: Session, limit: int, offset: int) -> ReportListResult:
        logger.info("report_history_list_started", extra={"source": "reports"})
        result = ReportRepository(db).list_reports(limit=limit, offset=offset)
        logger.info("report_history_list_completed", extra={"source": "reports"})
        return result

    def get_report(self, *, db: Session, report_id: str) -> ReportDetailResult:
        normalized_report_id = self._validate_report_id(report_id)
        logger.info("report_detail_started", extra={"source": "reports"})
        result = ReportRepository(db).get_report(normalized_report_id)
        if result is None:
            raise ReportNotFoundError("Report was not found.")

        logger.info("report_detail_completed", extra={"source": "reports"})
        return result

    @staticmethod
    def _validate_report_id(report_id: str | None) -> str:
        if report_id is None or not report_id.strip():
            raise ReportValidationError("Report ID is required.")

        candidate = report_id.strip()
        if candidate != report_id or not REPORT_ID_PATTERN.fullmatch(candidate):
            raise ReportValidationError("Report ID is invalid.")

        return candidate
