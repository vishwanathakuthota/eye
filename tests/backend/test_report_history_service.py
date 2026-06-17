from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.domain_analysis import DomainAnalysis
from app.services.report_history import (
    ReportHistoryService,
    ReportNotFoundError,
    ReportValidationError,
)


def build_session() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_domain_report(db: Session) -> None:
    db.add(
        DomainAnalysis(
            report_id="rep_service",
            domain="example.com",
            risk_score=20,
            risk_level="Low",
            summary="Domain summary.",
            dns={"records": {"A": ["93.184.216.34"]}},
            rdap={},
            certificates=[],
            subdomains=[],
            sources=[{"name": "dns", "status": "completed"}],
            created_at=datetime.now(UTC),
        )
    )
    db.commit()


def test_report_history_service_lists_reports() -> None:
    session_factory = build_session()

    with session_factory() as db:
        seed_domain_report(db)
        result = ReportHistoryService().list_reports(db=db, limit=20, offset=0)

    assert result.total == 1
    assert result.items[0].report_id == "rep_service"


def test_report_history_service_gets_report_detail() -> None:
    session_factory = build_session()

    with session_factory() as db:
        seed_domain_report(db)
        result = ReportHistoryService().get_report(db=db, report_id="rep_service")

    assert result.type == "domain"
    assert result.payload.report_id == "rep_service"


@pytest.mark.parametrize(
    "report_id",
    ["", " rep_service", "../rep_service", "bad id", "abc_123"],
)
def test_report_history_service_rejects_invalid_report_ids(report_id: str) -> None:
    session_factory = build_session()

    with session_factory() as db:
        with pytest.raises(ReportValidationError):
            ReportHistoryService().get_report(db=db, report_id=report_id)


def test_report_history_service_raises_when_report_is_missing() -> None:
    session_factory = build_session()

    with session_factory() as db:
        with pytest.raises(ReportNotFoundError):
            ReportHistoryService().get_report(db=db, report_id="rep_missing")
