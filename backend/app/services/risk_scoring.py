from __future__ import annotations

from app.schemas.domain import (
    CertificateFinding,
    DnsFindings,
    EmailSecurityPosture,
    RiskResult,
    SourceStatusItem,
    TlsCertificateInfo,
    WebSecurityPosture,
)

TRANSIENT_SOURCE_ERRORS = {
    "timeout",
    "rate_limited",
    "server_error",
    "http_error",
    "unexpected_error",
}


class RiskScoringService:
    def score(
        self,
        *,
        dns: DnsFindings,
        rdap: dict[str, object],
        certificates: list[CertificateFinding],
        subdomains: list[str],
        sources: list[SourceStatusItem],
        email_security: EmailSecurityPosture | None = None,
        web_security: WebSecurityPosture | None = None,
        tls: TlsCertificateInfo | None = None,
    ) -> RiskResult:
        score = 0
        reasons: list[str] = []
        confidence = 100
        reliability_notes: list[str] = []
        sources_by_name = {source.name: source for source in sources}

        dns_source = sources_by_name.get("dns")
        if not any(dns.records.model_dump().values()) and _source_supports_finding(dns_source):
            score += 25
            reasons.append("No DNS records were discovered.")

        rdap_source = sources_by_name.get("rdap")
        if not rdap and _source_supports_finding(rdap_source):
            score += 15
            if rdap_source and rdap_source.error_type == "not_found":
                reasons.append("RDAP record was not found.")
            else:
                reasons.append("RDAP registration data was unavailable.")

        if len(subdomains) > 25:
            score += 15
            reasons.append("Certificate transparency revealed more than 25 subdomains.")
        elif len(subdomains) > 10:
            score += 8
            reasons.append("Certificate transparency revealed more than 10 subdomains.")

        crtsh_source = sources_by_name.get("crt.sh")
        if not certificates and _source_supports_finding(crtsh_source):
            score += 10
            reasons.append("No certificate transparency entries were discovered.")

        if email_security is not None:
            if not email_security.spf_present:
                score += 8
                reasons.append("SPF record was not found.")
            if not email_security.dmarc_present:
                score += 10
                reasons.append("DMARC record was not found.")

        if web_security is not None:
            missing_headers = [header.name for header in web_security.headers if not header.present]
            if len(missing_headers) >= 3:
                score += 12
                reasons.append("Multiple recommended web security headers are missing.")
            elif missing_headers:
                score += 5
                reasons.append("Some recommended web security headers are missing.")

        if tls is not None:
            if tls.status == "expired":
                score += 30
                reasons.append("TLS certificate is expired.")
            elif tls.status == "expiring_soon":
                score += 10
                reasons.append("TLS certificate expires soon.")

        for source in sources:
            confidence -= _confidence_reduction(source)
            if source.status == "partial":
                reliability_notes.append(f"{source.name} returned partial data.")
            elif source.status == "failed" and source.error_type in TRANSIENT_SOURCE_ERRORS:
                source_error = (source.error or "unavailable").rstrip(".")
                reliability_notes.append(f"{source.name} source reliability issue: {source_error}.")

        normalized_score = min(score, 100)
        return RiskResult(
            score=normalized_score,
            level=self._level_for_score(normalized_score),
            reasons=reasons,
            confidence=max(confidence, 0),
            reliability_notes=reliability_notes,
        )

    @staticmethod
    def _level_for_score(score: int) -> str:
        if score >= 75:
            return "Critical"
        if score >= 50:
            return "High"
        if score >= 25:
            return "Medium"
        return "Low"


def _source_supports_finding(source: SourceStatusItem | None) -> bool:
    if source is None:
        return False
    if source.status in {"completed", "partial"}:
        return True
    return source.error_type == "not_found"


def _confidence_reduction(source: SourceStatusItem) -> int:
    if source.status == "partial":
        return 5
    if source.status != "failed":
        return 0
    if source.error_type in {"timeout", "rate_limited", "server_error"}:
        return 10
    if source.error_type in {"http_error", "invalid_response", "unexpected_error"}:
        return 8
    return 0
