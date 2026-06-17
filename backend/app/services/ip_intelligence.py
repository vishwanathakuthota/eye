from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.repositories.ip_analysis_repository import IpAnalysisRepository
from app.schemas.ip import IpAnalysisResult
from app.services.ip_network_enrichment import IpNetworkEnrichmentService
from app.services.ip_risk_scoring import IpRiskScoringService
from app.services.ip_summary import IpSummaryService
from app.services.ip_validation import IpValidator
from app.services.reverse_dns_lookup import ReverseDnsLookupService

logger = logging.getLogger(__name__)


class IpIntelligenceService:
    def __init__(
        self,
        *,
        validator: IpValidator | None = None,
        reverse_dns_lookup: ReverseDnsLookupService | None = None,
        network_enrichment: IpNetworkEnrichmentService | None = None,
        risk_scoring: IpRiskScoringService | None = None,
        summary: IpSummaryService | None = None,
    ) -> None:
        self._validator = validator or IpValidator()
        self._reverse_dns_lookup = reverse_dns_lookup or ReverseDnsLookupService()
        self._network_enrichment = network_enrichment or IpNetworkEnrichmentService()
        self._risk_scoring = risk_scoring or IpRiskScoringService()
        self._summary = summary or IpSummaryService()

    def analyze(self, raw_ip: str, db: Session) -> IpAnalysisResult:
        ip_address = self._validator.validate(raw_ip)
        ip = str(ip_address)
        logger.info("ip_analysis_started", extra={"ip": ip})

        reverse_dns, reverse_dns_source = self._reverse_dns_lookup.lookup(ip_address)
        network, network_source = self._network_enrichment.enrich(ip_address)
        sources = [reverse_dns_source, network_source]

        risk = self._risk_scoring.score(
            reverse_dns=reverse_dns,
            network=network,
            sources=sources,
        )
        summary = self._summary.generate(
            ip=ip,
            ip_version=ip_address.version,
            reverse_dns=reverse_dns,
            network=network,
            risk=risk,
            sources=sources,
        )

        result = IpAnalysisResult(
            report_id=f"ipr_{uuid4().hex}",
            ip=ip,
            ip_version=ip_address.version,
            risk=risk,
            summary=summary,
            reverse_dns=reverse_dns,
            network=network,
            sources=sources,
            created_at=datetime.now(UTC),
        )
        IpAnalysisRepository(db).create(result)

        logger.info("ip_analysis_completed", extra={"ip": ip})
        return result
