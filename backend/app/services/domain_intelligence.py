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
from app.services.email_security import EmailSecurityService
from app.services.intelligence_value import IntelligenceValueService
from app.services.rdap_lookup import RdapLookupService
from app.services.risk_scoring import RiskScoringService
from app.services.summary import IntelligenceSummaryService
from app.services.tls_inspection import TlsInspectionService
from app.services.web_security import WebSecurityService

logger = logging.getLogger(__name__)


class DomainIntelligenceService:
    def __init__(
        self,
        *,
        validator: DomainValidator | None = None,
        dns_lookup: DnsLookupService | None = None,
        rdap_lookup: RdapLookupService | None = None,
        crtsh_lookup: CrtShLookupService | None = None,
        email_security: EmailSecurityService | None = None,
        web_security: WebSecurityService | None = None,
        tls_inspection: TlsInspectionService | None = None,
        risk_scoring: RiskScoringService | None = None,
        intelligence_value: IntelligenceValueService | None = None,
        summary: IntelligenceSummaryService | None = None,
    ) -> None:
        self._validator = validator or DomainValidator()
        self._dns_lookup = dns_lookup or DnsLookupService()
        self._rdap_lookup = rdap_lookup or RdapLookupService()
        self._crtsh_lookup = crtsh_lookup or CrtShLookupService()
        self._email_security = email_security or EmailSecurityService()
        self._web_security = web_security or WebSecurityService()
        self._tls_inspection = tls_inspection or TlsInspectionService()
        self._risk_scoring = risk_scoring or RiskScoringService()
        self._intelligence_value = intelligence_value or IntelligenceValueService()
        self._summary = summary or IntelligenceSummaryService()

    def analyze(self, raw_domain: str, db: Session) -> DomainAnalysisResult:
        domain = self._validator.validate(raw_domain)
        logger.info("domain_analysis_started", extra={"domain": domain})

        dns, dns_source = self._dns_lookup.lookup(domain)
        rdap, rdap_source = self._rdap_lookup.lookup(domain)
        certificates, subdomains, crtsh_source = self._crtsh_lookup.lookup(domain)
        email_security, email_source = self._email_security.evaluate(
            domain,
            dns.records.TXT,
        )
        web_security, technology, web_source = self._web_security.evaluate(domain)
        tls, tls_source = self._tls_inspection.inspect(domain)
        sources = [dns_source, rdap_source, crtsh_source, email_source, web_source, tls_source]

        risk = self._risk_scoring.score(
            dns=dns,
            rdap=rdap,
            certificates=certificates,
            subdomains=subdomains,
            sources=sources,
            email_security=email_security,
            web_security=web_security,
            tls=tls,
        )
        intelligence = self._intelligence_value.build(
            domain=domain,
            dns=dns,
            rdap=rdap,
            certificates=certificates,
            subdomains=subdomains,
            risk=risk,
            sources=sources,
            email_security=email_security,
            web_security=web_security,
            tls=tls,
            technology=technology,
        )
        summary = self._summary.generate(
            domain=domain,
            dns=dns,
            rdap=rdap,
            certificates=certificates,
            subdomains=subdomains,
            risk=risk,
            sources=sources,
            intelligence=intelligence,
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
            intelligence=intelligence,
            created_at=datetime.now(UTC),
        )
        DomainAnalysisRepository(db).create(result)

        logger.info("domain_analysis_completed", extra={"domain": domain})
        return result
