from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.dependencies import get_domain_intelligence_service
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.domain_analysis import DomainAnalysis
from app.schemas.domain import (
    CertificateFinding,
    DnsFindings,
    DnsRecordSet,
    DomainAnalysisResult,
    RiskResult,
    SourceStatusItem,
)
from app.services.domain_validation import DomainValidator


class StubDomainIntelligenceService:
    def analyze(self, raw_domain: str, db: Session) -> DomainAnalysisResult:
        domain = DomainValidator().validate(raw_domain)
        result = DomainAnalysisResult(
            report_id="rep_test",
            domain=domain,
            risk=RiskResult(score=20, level="Low", reasons=[]),
            summary="example.com was analyzed using passive Domain Intelligence sources.",
            dns=DnsFindings(records=DnsRecordSet(A=["93.184.216.34"])),
            rdap={"handle": "EXAMPLE"},
            certificates=[CertificateFinding(name_value="www.example.com")],
            subdomains=["www.example.com"],
            sources=[
                SourceStatusItem(name="dns", status="completed"),
                SourceStatusItem(name="rdap", status="completed"),
                SourceStatusItem(name="crt.sh", status="completed"),
            ],
            created_at=datetime.now(UTC),
        )
        db.add(
            DomainAnalysis(
                report_id=result.report_id,
                domain=result.domain,
                risk_score=result.risk.score,
                risk_level=result.risk.level,
                summary=result.summary,
                dns=result.dns.model_dump(mode="json"),
                rdap=result.rdap,
                certificates=[
                    item.model_dump(mode="json") for item in result.certificates
                ],
                subdomains=result.subdomains,
                sources=[item.model_dump(mode="json") for item in result.sources],
                created_at=result.created_at,
            )
        )
        db.commit()
        return result


def build_client() -> tuple[TestClient, sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_domain_intelligence_service] = (
        StubDomainIntelligenceService
    )
    return TestClient(app), TestingSessionLocal


def test_domain_endpoint_returns_analysis_and_persists_record() -> None:
    client, session_factory = build_client()

    response = client.get("/api/v1/domain?domain=Example.com")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["domain"] == "example.com"
    assert body["data"]["report_id"] == "rep_test"
    assert body["data"]["risk"]["level"] == "Low"

    with session_factory() as db:
        records = db.query(DomainAnalysis).all()
        assert len(records) == 1
        assert records[0].domain == "example.com"


def test_domain_endpoint_returns_standard_error_for_invalid_domain() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/domain?domain=https://example.com/path")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "DOMAIN_INVALID"


def test_domain_endpoint_returns_standard_error_when_domain_is_missing() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/domain")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"
