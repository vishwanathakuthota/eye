from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.domain import (
    DnsFindings,
    DomainAnalysisResult,
    RiskResult,
    SourceStatusItem,
)
from app.schemas.report import ReportDetailResult
from app.services.report_export import ReportExportService


def build_report(summary: str = "Executive summary.") -> ReportDetailResult:
    payload = DomainAnalysisResult(
        report_id="rep_export",
        domain="example.com",
        risk=RiskResult(
            score=20,
            level="Low",
            reasons=["Reason one."],
            confidence=90,
            reliability_notes=["Source note."],
        ),
        summary=summary,
        dns=DnsFindings(),
        rdap={"handle": "<script>alert('x')</script>"},
        certificates=[],
        subdomains=[],
        sources=[SourceStatusItem(name="dns", status="completed")],
        created_at=datetime.now(UTC),
    )
    return ReportDetailResult(
        report_id="rep_export",
        type="domain",
        target="example.com",
        payload=payload,
    )


def test_report_export_service_builds_json_export_document() -> None:
    result = ReportExportService().build_json_export(build_report())

    assert result["metadata"]["product"] == "Eye"
    assert result["metadata"]["format"] == "json"
    assert result["metadata"]["report_id"] == "rep_export"
    assert result["metadata"]["type"] == "domain"
    assert result["metadata"]["target"] == "example.com"
    assert result["report"]["report_id"] == "rep_export"
    assert result["report"]["risk"]["confidence"] == 90


def test_report_export_service_escapes_html_output() -> None:
    result = ReportExportService().build_html_export(
        build_report(summary="<strong>unsafe</strong>")
    )

    assert "<!doctype html>" in result
    assert "&lt;strong&gt;unsafe&lt;/strong&gt;" in result
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in result
    assert "<script>alert('x')</script>" not in result
