from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.domain_analysis import DomainAnalysis
from app.repositories.domain_analysis_repository import DomainAnalysisRepository
from app.schemas.domain import (
    DnsFindings,
    DomainAnalysisResult,
    RiskResult,
    SourceStatusItem,
)


def test_domain_analysis_repository_persists_result() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    result = DomainAnalysisResult(
        report_id="rep_repo",
        domain="example.com",
        risk=RiskResult(score=10, level="Low", reasons=[]),
        summary="Passive summary.",
        dns=DnsFindings(),
        rdap={},
        certificates=[],
        subdomains=[],
        sources=[SourceStatusItem(name="dns", status="completed")],
        created_at=datetime.now(UTC),
    )

    with session_factory() as db:
        DomainAnalysisRepository(db).create(result)
        record = db.query(DomainAnalysis).filter_by(report_id="rep_repo").one()

    assert record.domain == "example.com"
    assert record.risk_score == 10
