from __future__ import annotations

from app.schemas.domain import DnsFindings, DnsRecordSet, SourceStatusItem
from app.services.risk_scoring import RiskScoringService


def test_risk_scoring_returns_low_for_complete_low_signal_findings() -> None:
    result = RiskScoringService().score(
        dns=DnsFindings(
            records=DnsRecordSet(A=["93.184.216.34"], NS=["a.iana-servers.net"])
        ),
        rdap={"handle": "EXAMPLE"},
        certificates=[],
        subdomains=[],
        sources=[
            SourceStatusItem(name="dns", status="completed"),
            SourceStatusItem(name="rdap", status="completed"),
            SourceStatusItem(name="crt.sh", status="completed"),
        ],
    )

    assert result.score == 10
    assert result.level == "Low"


def test_risk_scoring_increases_when_observed_intelligence_is_missing() -> None:
    result = RiskScoringService().score(
        dns=DnsFindings(),
        rdap={},
        certificates=[],
        subdomains=[],
        sources=[
            SourceStatusItem(name="dns", status="completed"),
            SourceStatusItem(name="rdap", status="failed", error_type="not_found"),
            SourceStatusItem(name="crt.sh", status="completed"),
        ],
    )

    assert result.score == 50
    assert result.level == "High"
