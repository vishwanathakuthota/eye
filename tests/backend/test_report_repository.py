from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.domain_analysis import DomainAnalysis
from app.models.ip_analysis import IpAnalysis
from app.repositories.report_repository import ReportRepository


def build_session() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_reports(db: Session) -> None:
    now = datetime.now(UTC)
    db.add(
        DomainAnalysis(
            report_id="rep_domain",
            domain="example.com",
            risk_score=20,
            risk_level="Low",
            risk={
                "score": 20,
                "level": "Low",
                "reasons": ["Domain reason."],
                "confidence": 95,
                "reliability_notes": [],
            },
            summary="Domain summary.",
            dns={"records": {"A": ["93.184.216.34"]}},
            rdap={"handle": "EXAMPLE"},
            certificates=[{"name_value": "www.example.com"}],
            subdomains=["www.example.com"],
            sources=[{"name": "dns", "status": "completed"}],
            created_at=now - timedelta(minutes=5),
        )
    )
    db.add(
        IpAnalysis(
            report_id="ipr_ip",
            ip="8.8.8.8",
            ip_version=4,
            risk_score=5,
            risk_level="Low",
            risk={
                "score": 5,
                "level": "Low",
                "reasons": ["IP reason."],
                "confidence": 100,
                "reliability_notes": [],
            },
            summary="IP summary.",
            reverse_dns={"ptr_records": ["dns.google"]},
            network={
                "classification": "global",
                "note": "Placeholder.",
                "attributes": {"is_global": True},
            },
            sources=[{"name": "reverse_dns", "status": "completed"}],
            created_at=now,
        )
    )
    db.commit()


def test_report_repository_lists_domain_and_ip_reports_by_created_at() -> None:
    session_factory = build_session()

    with session_factory() as db:
        seed_reports(db)
        result = ReportRepository(db).list_reports(limit=20, offset=0)

    assert result.total == 2
    assert [item.report_id for item in result.items] == ["ipr_ip", "rep_domain"]
    assert result.items[0].type == "ip"
    assert result.items[0].target == "8.8.8.8"
    assert result.items[1].type == "domain"
    assert result.items[1].target == "example.com"


def test_report_repository_paginates_report_list() -> None:
    session_factory = build_session()

    with session_factory() as db:
        seed_reports(db)
        result = ReportRepository(db).list_reports(limit=1, offset=1)

    assert result.total == 2
    assert len(result.items) == 1
    assert result.items[0].report_id == "rep_domain"


def test_report_repository_returns_full_domain_report_detail() -> None:
    session_factory = build_session()

    with session_factory() as db:
        seed_reports(db)
        result = ReportRepository(db).get_report("rep_domain")

    assert result is not None
    assert result.type == "domain"
    assert result.target == "example.com"
    assert result.payload.report_id == "rep_domain"
    assert result.payload.domain == "example.com"
    assert result.payload.risk.reasons == ["Domain reason."]
    assert result.payload.risk.confidence == 95


def test_report_repository_returns_full_ip_report_detail() -> None:
    session_factory = build_session()

    with session_factory() as db:
        seed_reports(db)
        result = ReportRepository(db).get_report("ipr_ip")

    assert result is not None
    assert result.type == "ip"
    assert result.target == "8.8.8.8"
    assert result.payload.report_id == "ipr_ip"
    assert result.payload.ip == "8.8.8.8"
    assert result.payload.risk.reasons == ["IP reason."]
