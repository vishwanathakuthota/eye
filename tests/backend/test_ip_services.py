from __future__ import annotations

import ipaddress

from app.schemas.domain import SourceStatusItem
from app.schemas.ip import NetworkEnrichment, ReverseDnsFindings
from app.services.ip_network_enrichment import IpNetworkEnrichmentService
from app.services.ip_risk_scoring import IpRiskScoringService
from app.services.ip_summary import IpSummaryService


def test_ip_network_enrichment_returns_local_placeholder() -> None:
    enrichment, source = IpNetworkEnrichmentService().enrich(
        ipaddress.ip_address("8.8.8.8")
    )

    assert enrichment.classification == "global"
    assert enrichment.asn is None
    assert enrichment.source == "local-placeholder"
    assert enrichment.attributes["is_global"] is True
    assert source.name == "network_enrichment"
    assert source.status == "completed"


def test_ip_risk_scoring_is_low_for_global_ip_with_ptr() -> None:
    result = IpRiskScoringService().score(
        reverse_dns=ReverseDnsFindings(ptr_records=["dns.google"]),
        network=NetworkEnrichment(
            classification="global",
            note="Placeholder.",
            attributes={"is_global": True},
        ),
        sources=[
            SourceStatusItem(name="reverse_dns", status="completed"),
            SourceStatusItem(name="network_enrichment", status="completed"),
        ],
    )

    assert result.score == 0
    assert result.level == "Low"


def test_ip_risk_scoring_flags_special_use_address() -> None:
    result = IpRiskScoringService().score(
        reverse_dns=ReverseDnsFindings(),
        network=NetworkEnrichment(
            classification="private",
            note="Placeholder.",
            attributes={"is_private": True},
        ),
        sources=[
            SourceStatusItem(
                name="reverse_dns",
                status="completed",
                error="No PTR records were found.",
                error_type="not_found",
            ),
            SourceStatusItem(name="network_enrichment", status="completed"),
        ],
    )

    assert result.score == 20
    assert result.level == "Low"
    assert "IP address is classified as private." in result.reasons
    assert "No reverse DNS PTR records were found." in result.reasons


def test_ip_summary_mentions_placeholder_enrichment() -> None:
    summary = IpSummaryService().generate(
        ip="8.8.8.8",
        ip_version=4,
        reverse_dns=ReverseDnsFindings(ptr_records=["dns.google"]),
        network=NetworkEnrichment(
            classification="global",
            note="Placeholder.",
            attributes={"is_global": True},
        ),
        risk=IpRiskScoringService().score(
            reverse_dns=ReverseDnsFindings(ptr_records=["dns.google"]),
            network=NetworkEnrichment(
                classification="global",
                note="Placeholder.",
                attributes={"is_global": True},
            ),
            sources=[SourceStatusItem(name="reverse_dns", status="completed")],
        ),
        sources=[SourceStatusItem(name="reverse_dns", status="completed")],
    )

    assert "8.8.8.8 was analyzed as an IPv4 address" in summary
    assert "ASN and network ownership enrichment are placeholders" in summary
