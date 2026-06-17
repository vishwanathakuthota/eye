from __future__ import annotations

import httpx

from app.schemas.domain import DnsFindings, DnsRecordSet, SourceStatusItem
from app.services.crtsh_lookup import CrtShLookupService
from app.services.rdap_lookup import RdapLookupService
from app.services.risk_scoring import RiskScoringService
from app.services.summary import IntelligenceSummaryService


def test_rdap_http_error_returns_structured_source_status(monkeypatch) -> None:
    request = httpx.Request("GET", "https://rdap.test/domain/example.com")

    def fake_get(url: str, timeout: float) -> httpx.Response:
        return httpx.Response(500, request=request)

    monkeypatch.setattr("app.services.rdap_lookup.httpx.get", fake_get)

    rdap, source = RdapLookupService(base_url="https://rdap.test/domain").lookup(
        "example.com"
    )

    assert rdap == {}
    assert source.status == "failed"
    assert source.error_type == "server_error"
    assert source.status_code == 500
    assert source.error == "RDAP source returned a server error."


def test_rdap_timeout_returns_structured_source_status(monkeypatch) -> None:
    def fake_get(url: str, timeout: float) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    monkeypatch.setattr("app.services.rdap_lookup.httpx.get", fake_get)

    rdap, source = RdapLookupService(base_url="https://rdap.test/domain").lookup(
        "example.com"
    )

    assert rdap == {}
    assert source.status == "failed"
    assert source.error_type == "timeout"
    assert source.status_code is None
    assert source.error == "RDAP lookup timed out."


def test_crtsh_timeout_returns_no_results_without_crashing(monkeypatch) -> None:
    def fake_get(
        url: str,
        params: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    monkeypatch.setattr("app.services.crtsh_lookup.httpx.get", fake_get)

    certificates, subdomains, source = CrtShLookupService(
        base_url="https://crt.test/"
    ).lookup("example.com")

    assert certificates == []
    assert subdomains == []
    assert source.status == "failed"
    assert source.error_type == "timeout"
    assert source.error == "Certificate transparency data could not be retrieved."


def test_crtsh_deduplicates_subdomains_and_caps_certificate_results(
    monkeypatch,
) -> None:
    request = httpx.Request("GET", "https://crt.test/")
    payload = [
        {
            "common_name": "www.example.com",
            "name_value": "www.example.com\n*.api.example.com",
            "issuer_name": "Example CA",
            "not_before": "2026-01-01T00:00:00",
            "not_after": "2027-01-01T00:00:00",
        },
        {
            "common_name": "duplicate.example.com",
            "name_value": "www.example.com\napi.example.com",
            "issuer_name": "Example CA",
            "not_before": "2026-01-01T00:00:00",
            "not_after": "2027-01-01T00:00:00",
        },
        {
            "common_name": "mail.example.com",
            "name_value": "mail.example.com",
            "issuer_name": "Example CA",
            "not_before": "2026-01-02T00:00:00",
            "not_after": "2027-01-02T00:00:00",
        },
    ]

    def fake_get(
        url: str,
        params: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        return httpx.Response(200, json=payload, request=request)

    monkeypatch.setattr("app.services.crtsh_lookup.httpx.get", fake_get)

    certificates, subdomains, source = CrtShLookupService(
        base_url="https://crt.test/",
        max_results=2,
    ).lookup("example.com")

    assert len(certificates) == 2
    assert subdomains == ["api.example.com", "www.example.com"]
    assert source.status == "partial"
    assert source.error == "Certificate transparency results capped at 2."


def test_risk_score_does_not_jump_on_transient_source_timeout() -> None:
    result = RiskScoringService().score(
        dns=DnsFindings(records=DnsRecordSet(A=["93.184.216.34"])),
        rdap={},
        certificates=[],
        subdomains=[],
        sources=[
            SourceStatusItem(name="dns", status="completed"),
            SourceStatusItem(
                name="rdap",
                status="failed",
                error="RDAP lookup timed out.",
                error_type="timeout",
            ),
            SourceStatusItem(
                name="crt.sh",
                status="failed",
                error="Certificate transparency data could not be retrieved.",
                error_type="timeout",
            ),
        ],
    )

    assert result.score == 0
    assert result.level == "Low"
    assert result.confidence == 80
    assert result.reliability_notes == [
        "rdap source reliability issue: RDAP lookup timed out.",
        "crt.sh source reliability issue: Certificate transparency data could not be retrieved.",
    ]
    assert result.reasons == []


def test_summary_says_certificate_transparency_could_not_be_retrieved() -> None:
    summary = IntelligenceSummaryService().generate(
        domain="example.com",
        dns=DnsFindings(records=DnsRecordSet(A=["93.184.216.34"])),
        rdap={"handle": "EXAMPLE"},
        certificates=[],
        subdomains=[],
        risk=RiskScoringService().score(
            dns=DnsFindings(records=DnsRecordSet(A=["93.184.216.34"])),
            rdap={"handle": "EXAMPLE"},
            certificates=[],
            subdomains=[],
            sources=[
                SourceStatusItem(name="dns", status="completed"),
                SourceStatusItem(name="rdap", status="completed"),
                SourceStatusItem(
                    name="crt.sh",
                    status="failed",
                    error="Certificate transparency data could not be retrieved.",
                    error_type="timeout",
                ),
            ],
        ),
        sources=[
            SourceStatusItem(name="dns", status="completed"),
            SourceStatusItem(name="rdap", status="completed"),
            SourceStatusItem(
                name="crt.sh",
                status="failed",
                error="Certificate transparency data could not be retrieved.",
                error_type="timeout",
            ),
        ],
    )

    assert "Certificate transparency data could not be retrieved." in summary
    assert "0 certificate transparency entries" not in summary
    assert "Failed sources: crt.sh" in summary
