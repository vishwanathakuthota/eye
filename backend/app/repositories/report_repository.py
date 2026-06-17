from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.domain_analysis import DomainAnalysis
from app.models.ip_analysis import IpAnalysis
from app.schemas.domain import (
    CertificateFinding,
    DnsFindings,
    DomainAnalysisResult,
    IntelligenceValueLayer,
    RiskResult,
    SourceStatusItem,
)
from app.schemas.ip import IpAnalysisResult, NetworkEnrichment, ReverseDnsFindings
from app.schemas.report import ReportDetailResult, ReportListResult, ReportSummary


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_reports(self, *, limit: int, offset: int) -> ReportListResult:
        domain_reports = self._domain_summaries()
        ip_reports = self._ip_summaries()
        all_reports = sorted(
            [*domain_reports, *ip_reports],
            key=lambda item: item.created_at,
            reverse=True,
        )

        return ReportListResult(
            items=all_reports[offset : offset + limit],
            limit=limit,
            offset=offset,
            total=len(all_reports),
        )

    def get_report(self, report_id: str) -> ReportDetailResult | None:
        if report_id.startswith("ipr_"):
            return self._get_ip_report(report_id)
        if report_id.startswith("rep_"):
            return self._get_domain_report(report_id)

        return self._get_domain_report(report_id) or self._get_ip_report(report_id)

    def count_reports(self) -> int:
        domain_count = self._db.scalar(select(func.count()).select_from(DomainAnalysis)) or 0
        ip_count = self._db.scalar(select(func.count()).select_from(IpAnalysis)) or 0
        return domain_count + ip_count

    def _domain_summaries(self) -> list[ReportSummary]:
        records = self._db.scalars(
            select(DomainAnalysis).order_by(desc(DomainAnalysis.created_at))
        ).all()
        return [
            ReportSummary(
                report_id=record.report_id,
                type="domain",
                target=record.domain,
                risk_level=record.risk_level,
                risk_score=record.risk_score,
                created_at=record.created_at,
            )
            for record in records
        ]

    def _ip_summaries(self) -> list[ReportSummary]:
        records = self._db.scalars(select(IpAnalysis).order_by(desc(IpAnalysis.created_at))).all()
        return [
            ReportSummary(
                report_id=record.report_id,
                type="ip",
                target=record.ip,
                risk_level=record.risk_level,
                risk_score=record.risk_score,
                created_at=record.created_at,
            )
            for record in records
        ]

    def _get_domain_report(self, report_id: str) -> ReportDetailResult | None:
        record = self._db.scalar(
            select(DomainAnalysis).where(DomainAnalysis.report_id == report_id)
        )
        if record is None:
            return None

        payload = DomainAnalysisResult(
            report_id=record.report_id,
            domain=record.domain,
            risk=_risk_from_record(record.risk, record.risk_score, record.risk_level),
            summary=record.summary,
            dns=DnsFindings.model_validate(record.dns),
            rdap=record.rdap,
            certificates=[CertificateFinding.model_validate(item) for item in record.certificates],
            subdomains=record.subdomains,
            sources=[SourceStatusItem.model_validate(item) for item in record.sources],
            intelligence=(
                IntelligenceValueLayer.model_validate(record.intelligence)
                if record.intelligence is not None
                else IntelligenceValueLayer()
            ),
            created_at=record.created_at,
        )
        return ReportDetailResult(
            report_id=record.report_id,
            type="domain",
            target=record.domain,
            payload=payload,
        )

    def _get_ip_report(self, report_id: str) -> ReportDetailResult | None:
        record = self._db.scalar(select(IpAnalysis).where(IpAnalysis.report_id == report_id))
        if record is None:
            return None

        payload = IpAnalysisResult(
            report_id=record.report_id,
            ip=record.ip,
            ip_version=record.ip_version,
            risk=_risk_from_record(record.risk, record.risk_score, record.risk_level),
            summary=record.summary,
            reverse_dns=ReverseDnsFindings.model_validate(record.reverse_dns),
            network=NetworkEnrichment.model_validate(record.network),
            sources=[SourceStatusItem.model_validate(item) for item in record.sources],
            created_at=record.created_at,
        )
        return ReportDetailResult(
            report_id=record.report_id,
            type="ip",
            target=record.ip,
            payload=payload,
        )


def _risk_from_record(
    risk: dict[str, object] | None,
    risk_score: int,
    risk_level: str,
) -> RiskResult:
    if risk is not None:
        return RiskResult.model_validate(risk)

    return RiskResult(
        score=risk_score,
        level=risk_level,
    )
