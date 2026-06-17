from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.ip_analysis import IpAnalysis
from app.repositories.ip_analysis_repository import IpAnalysisRepository
from app.schemas.domain import RiskResult, SourceStatusItem
from app.schemas.ip import IpAnalysisResult, NetworkEnrichment, ReverseDnsFindings


def test_ip_analysis_repository_persists_result() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    result = IpAnalysisResult(
        report_id="ipr_repo",
        ip="8.8.8.8",
        ip_version=4,
        risk=RiskResult(score=5, level="Low", reasons=[]),
        summary="Passive IP summary.",
        reverse_dns=ReverseDnsFindings(ptr_records=["dns.google"]),
        network=NetworkEnrichment(
            classification="global",
            note="Placeholder.",
            attributes={"is_global": True},
        ),
        sources=[SourceStatusItem(name="reverse_dns", status="completed")],
        created_at=datetime.now(UTC),
    )

    with session_factory() as db:
        IpAnalysisRepository(db).create(result)
        record = db.query(IpAnalysis).filter_by(report_id="ipr_repo").one()

    assert record.ip == "8.8.8.8"
    assert record.ip_version == 4
    assert record.risk_score == 5
    assert record.reverse_dns["ptr_records"] == ["dns.google"]
