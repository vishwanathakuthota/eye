from __future__ import annotations

import httpx

from app.schemas.domain import (
    DnsFindings,
    DnsRecordSet,
    EmailSecurityPosture,
    RiskResult,
    SourceStatusItem,
    TechnologyFingerprint,
    TlsCertificateInfo,
    WebSecurityPosture,
)
from app.services.email_security import EmailSecurityService
from app.services.intelligence_value import IntelligenceValueService
from app.services.risk_scoring import RiskScoringService
from app.services.web_security import WebSecurityService


def test_email_security_detects_spf_and_missing_dmarc(monkeypatch) -> None:
    def fake_lookup_dmarc(self: EmailSecurityService, domain: str):
        return None, SourceStatusItem(name="email_security", status="completed")

    monkeypatch.setattr(EmailSecurityService, "_lookup_dmarc", fake_lookup_dmarc)

    posture, source = EmailSecurityService().evaluate(
        "example.com",
        ["v=spf1 include:_spf.example.com -all"],
    )

    assert source.status == "completed"
    assert posture.spf_present is True
    assert posture.dmarc_present is False
    assert posture.score == 65
    assert "Publish a DMARC TXT record at _dmarc." in posture.recommendations


def test_web_security_detects_missing_and_present_headers(monkeypatch) -> None:
    request = httpx.Request("HEAD", "https://example.com/")
    response = httpx.Response(
        200,
        headers={
            "Strict-Transport-Security": "max-age=31536000",
            "X-Content-Type-Options": "nosniff",
            "Server": "cloudflare",
            "CF-Ray": "test",
        },
        request=request,
    )

    def fake_request(self: WebSecurityService, url: str) -> httpx.Response:
        return response

    monkeypatch.setattr(WebSecurityService, "_request", fake_request)

    posture, technology, source = WebSecurityService().evaluate("example.com")

    assert source.status == "completed"
    assert posture.checked_url == "https://example.com/"
    assert posture.score == 55
    assert any(
        header.name == "Content-Security-Policy" and not header.present
        for header in posture.headers
    )
    assert technology.server == "cloudflare"
    assert technology.cdn_or_security == ["Cloudflare"]


def test_risk_scoring_uses_observed_email_web_and_tls_findings() -> None:
    result = RiskScoringService().score(
        dns=DnsFindings(records=DnsRecordSet(A=["93.184.216.34"])),
        rdap={"handle": "EXAMPLE"},
        certificates=[],
        subdomains=[],
        sources=[
            SourceStatusItem(name="dns", status="completed"),
            SourceStatusItem(name="rdap", status="completed"),
            SourceStatusItem(name="crt.sh", status="completed"),
            SourceStatusItem(name="web_security", status="completed"),
            SourceStatusItem(name="tls", status="completed"),
        ],
        email_security=EmailSecurityPosture(spf_present=False, dmarc_present=False),
        web_security=WebSecurityPosture(
            headers=[
                {"name": "Strict-Transport-Security", "present": False},
                {"name": "Content-Security-Policy", "present": False},
                {"name": "X-Frame-Options", "present": False},
            ]
        ),
        tls=TlsCertificateInfo(checked_host="example.com", status="expiring_soon"),
    )

    assert result.score == 50
    assert result.level == "High"
    assert "DMARC record was not found." in result.reasons
    assert "Multiple recommended web security headers are missing." in result.reasons


def test_intelligence_value_marks_incomplete_when_major_sources_fail() -> None:
    risk = RiskResult(
        score=0,
        level="Low",
        confidence=70,
        reasons=[],
        reliability_notes=["rdap source reliability issue: timeout."],
    )

    result = IntelligenceValueService().build(
        domain="example.com",
        dns=DnsFindings(records=DnsRecordSet(A=["93.184.216.34"])),
        rdap={},
        certificates=[],
        subdomains=[],
        risk=risk,
        sources=[
            SourceStatusItem(name="dns", status="completed"),
            SourceStatusItem(
                name="rdap", status="failed", error="timeout", error_type="timeout"
            ),
            SourceStatusItem(
                name="crt.sh", status="failed", error="timeout", error_type="timeout"
            ),
        ],
        email_security=EmailSecurityPosture(),
        web_security=WebSecurityPosture(),
        tls=None,
        technology=TechnologyFingerprint(),
    )

    assert result.intelligence_confidence == "Low"
    assert result.incomplete_intelligence is True
    assert (
        "Incomplete Intelligence: one or more major sources failed."
        in result.confidence_notes
    )
    assert result.summary_v2 is not None
    assert result.summary_v2.confidence_notes.title == "Confidence Notes"
