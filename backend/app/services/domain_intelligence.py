from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.repositories.domain_analysis_repository import DomainAnalysisRepository
from app.schemas.domain import DomainAnalysisResult
from app.services.crtsh_lookup import CrtShLookupService
from app.services.dns_lookup import DnsLookupService
from app.services.domain_validation import DomainValidator
from app.services.rdap_lookup import RdapLookupService
from app.services.risk_scoring import RiskScoringService
from app.services.summary import IntelligenceSummaryService

logger = logging.getLogger(__name__)


class DomainIntelligenceService:
    def __init__(
        self,
        *,
        validator: DomainValidator | None = None,
        dns_lookup: DnsLookupService | None = None,
        rdap_lookup: RdapLookupService | None = None,
        crtsh_lookup: CrtShLookupService | None = None,
        risk_scoring: RiskScoringService | None = None,
        summary: IntelligenceSummaryService | None = None,
    ) -> None:
        self._validator = validator or DomainValidator()
        self._dns_lookup = dns_lookup or DnsLookupService()
        self._rdap_lookup = rdap_lookup or RdapLookupService()
        self._crtsh_lookup = crtsh_lookup or CrtShLookupService()
        self._risk_scoring = risk_scoring or RiskScoringService()
        self._summary = summary or IntelligenceSummaryService()

    def analyze(self, raw_domain: str, db: Session) -> DomainAnalysisResult:
        domain = self._validator.validate(raw_domain)
        logger.info("domain_analysis_started", extra={"domain": domain})

        dns, dns_source = self._dns_lookup.lookup(domain)
        rdap, rdap_source = self._rdap_lookup.lookup(domain)
        certificates, subdomains, crtsh_source = self._crtsh_lookup.lookup(domain)
        sources = [dns_source, rdap_source, crtsh_source]

        risk = self._risk_scoring.score(
            dns=dns,
            rdap=rdap,
            certificates=certificates,
            subdomains=subdomains,
            sources=sources,
        )
        summary = self._summary.generate(
            domain=domain,
            dns=dns,
            rdap=rdap,
            certificates=certificates,
            subdomains=subdomains,
            risk=risk,
            sources=sources,
        )

        result = DomainAnalysisResult(
            report_id=f"rep_{uuid4().hex}",
            domain=domain,
            risk=risk,
            summary=summary,
            dns=dns,
            rdap=rdap,
            certificates=certificates,
            subdomains=subdomains,
            sources=sources,
            created_at=datetime.now(UTC),
        )
        DomainAnalysisRepository(db).create(result)

        logger.info("domain_analysis_completed", extra={"domain": domain})
        return result
