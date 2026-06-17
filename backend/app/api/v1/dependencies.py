from __future__ import annotations

from app.services.domain_intelligence import DomainIntelligenceService
from app.services.ip_intelligence import IpIntelligenceService
from app.services.report_export import ReportExportService
from app.services.report_history import ReportHistoryService


def get_domain_intelligence_service() -> DomainIntelligenceService:
    return DomainIntelligenceService()


def get_ip_intelligence_service() -> IpIntelligenceService:
    return IpIntelligenceService()


def get_report_history_service() -> ReportHistoryService:
    return ReportHistoryService()


def get_report_export_service() -> ReportExportService:
    return ReportExportService()
