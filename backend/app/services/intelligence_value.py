from __future__ import annotations

from app.schemas.domain import (
    CertificateFinding,
    DnsFindings,
    EmailSecurityPosture,
    IntelligenceSection,
    IntelligenceSummaryV2,
    IntelligenceValueLayer,
    RiskResult,
    SourceStatusItem,
    TechnologyFingerprint,
    TlsCertificateInfo,
    WebSecurityPosture,
)

MAJOR_SOURCES = {"dns", "rdap", "crt.sh", "web_security", "tls"}


class IntelligenceValueService:
    def build(
        self,
        *,
        domain: str,
        dns: DnsFindings,
        rdap: dict[str, object],
        certificates: list[CertificateFinding],
        subdomains: list[str],
        risk: RiskResult,
        sources: list[SourceStatusItem],
        email_security: EmailSecurityPosture,
        web_security: WebSecurityPosture,
        tls: TlsCertificateInfo | None,
        technology: TechnologyFingerprint,
    ) -> IntelligenceValueLayer:
        failed_major_sources = [
            source
            for source in sources
            if source.name in MAJOR_SOURCES and source.status == "failed"
        ]
        partial_sources = [source for source in sources if source.status == "partial"]
        intelligence_confidence = _confidence_label(risk.confidence, failed_major_sources)
        incomplete = bool(failed_major_sources or risk.confidence < 80)
        confidence_notes = _confidence_notes(
            confidence=risk.confidence,
            failed_major_sources=failed_major_sources,
            partial_sources=partial_sources,
        )
        recommendations = _recommendations(
            email_security=email_security,
            web_security=web_security,
            tls=tls,
            incomplete=incomplete,
        )
        summary_v2 = _summary_v2(
            domain=domain,
            dns=dns,
            rdap=rdap,
            certificates=certificates,
            subdomains=subdomains,
            risk=risk,
            email_security=email_security,
            web_security=web_security,
            tls=tls,
            technology=technology,
            confidence_label=intelligence_confidence,
            confidence_notes=confidence_notes,
            recommendations=recommendations,
        )

        return IntelligenceValueLayer(
            intelligence_confidence=intelligence_confidence,
            incomplete_intelligence=incomplete,
            confidence_notes=confidence_notes,
            email_security=email_security,
            web_security=web_security,
            tls=tls,
            technology=technology,
            recommendations=recommendations,
            summary_v2=summary_v2,
        )


def _confidence_label(
    confidence: int,
    failed_major_sources: list[SourceStatusItem],
) -> str:
    if confidence < 70 or len(failed_major_sources) >= 2:
        return "Low"
    if confidence < 90 or failed_major_sources:
        return "Medium"
    return "High"


def _confidence_notes(
    *,
    confidence: int,
    failed_major_sources: list[SourceStatusItem],
    partial_sources: list[SourceStatusItem],
) -> list[str]:
    notes = [f"Source coverage confidence is {confidence}/100."]
    for source in failed_major_sources:
        notes.append(
            f"{source.name} did not return usable data: "
            f"{source.error or source.error_type or 'unavailable'}."
        )
    for source in partial_sources:
        notes.append(f"{source.name} returned partial data.")
    if failed_major_sources:
        notes.append("Incomplete Intelligence: one or more major sources failed.")
    return notes


def _recommendations(
    *,
    email_security: EmailSecurityPosture,
    web_security: WebSecurityPosture,
    tls: TlsCertificateInfo | None,
    incomplete: bool,
) -> list[str]:
    recommendations = [
        *email_security.recommendations,
        *web_security.recommendations,
    ]
    if tls is not None:
        recommendations.extend(tls.recommendations)
    if incomplete:
        recommendations.append("Re-run analysis when failed sources are available.")
    return sorted(set(recommendations))


def _summary_v2(
    *,
    domain: str,
    dns: DnsFindings,
    rdap: dict[str, object],
    certificates: list[CertificateFinding],
    subdomains: list[str],
    risk: RiskResult,
    email_security: EmailSecurityPosture,
    web_security: WebSecurityPosture,
    tls: TlsCertificateInfo | None,
    technology: TechnologyFingerprint,
    confidence_label: str,
    confidence_notes: list[str],
    recommendations: list[str],
) -> IntelligenceSummaryV2:
    dns_count = sum(len(values) for values in dns.records.model_dump().values())
    tls_status = tls.status if tls else "unavailable"

    return IntelligenceSummaryV2(
        executive_summary=IntelligenceSection(
            title="Executive Summary",
            body=(
                f"{domain} currently has observed risk {risk.level} ({risk.score}/100) "
                f"with {confidence_label} intelligence confidence."
            ),
            bullets=[*risk.reasons, *risk.reliability_notes],
        ),
        attack_surface_snapshot=IntelligenceSection(
            title="Attack Surface Snapshot",
            body=(
                f"Observed {dns_count} DNS records, {len(subdomains)} subdomains, "
                f"and {len(certificates)} certificate transparency entries."
            ),
            bullets=[
                f"RDAP data is {'available' if rdap else 'unavailable'}.",
                f"TLS status is {tls_status}.",
            ],
        ),
        email_security=IntelligenceSection(
            title="Email Security",
            body=f"Email security posture score is {email_security.score}/100.",
            bullets=email_security.findings,
        ),
        web_security=IntelligenceSection(
            title="Web Security",
            body=f"Web security header posture score is {web_security.score}/100.",
            bullets=web_security.findings,
        ),
        infrastructure=IntelligenceSection(
            title="Infrastructure",
            body="Infrastructure signals are derived from passive DNS, TLS, and HTTP headers.",
            bullets=technology.findings,
        ),
        confidence_notes=IntelligenceSection(
            title="Confidence Notes",
            body=f"Intelligence confidence is {confidence_label}.",
            bullets=confidence_notes,
        ),
        recommendations=IntelligenceSection(
            title="Recommendations",
            body="Prioritized next steps based on observed findings.",
            bullets=recommendations,
        ),
    )
