from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.dependencies import get_ip_intelligence_service
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.ip_analysis import IpAnalysis
from app.schemas.domain import RiskResult, SourceStatusItem
from app.schemas.ip import IpAnalysisResult, NetworkEnrichment, ReverseDnsFindings
from app.services.ip_validation import IpValidator


class StubIpIntelligenceService:
    def analyze(self, raw_ip: str, db: Session) -> IpAnalysisResult:
        ip_address = IpValidator().validate(raw_ip)
        result = IpAnalysisResult(
            report_id="ipr_test",
            ip=str(ip_address),
            ip_version=ip_address.version,
            risk=RiskResult(score=5, level="Low", reasons=[]),
            summary="8.8.8.8 was analyzed using passive IP Intelligence.",
            reverse_dns=ReverseDnsFindings(ptr_records=["dns.google"]),
            network=NetworkEnrichment(
                classification="global",
                note="Placeholder.",
                attributes={"is_global": True},
            ),
            sources=[SourceStatusItem(name="reverse_dns", status="completed")],
            created_at=datetime.now(UTC),
        )
        db.add(
            IpAnalysis(
                report_id=result.report_id,
                ip=result.ip,
                ip_version=result.ip_version,
                risk_score=result.risk.score,
                risk_level=result.risk.level,
                summary=result.summary,
                reverse_dns=result.reverse_dns.model_dump(mode="json"),
                network=result.network.model_dump(mode="json"),
                sources=[source.model_dump(mode="json") for source in result.sources],
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
    app.dependency_overrides[get_ip_intelligence_service] = StubIpIntelligenceService
    return TestClient(app), TestingSessionLocal


def test_ip_endpoint_returns_analysis_and_persists_record() -> None:
    client, session_factory = build_client()

    response = client.get("/api/v1/ip?ip=8.8.8.8")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["ip"] == "8.8.8.8"
    assert body["data"]["ip_version"] == 4
    assert body["data"]["report_id"] == "ipr_test"
    assert body["data"]["reverse_dns"]["ptr_records"] == ["dns.google"]

    with session_factory() as db:
        records = db.query(IpAnalysis).all()
        assert len(records) == 1
        assert records[0].ip == "8.8.8.8"


def test_ip_endpoint_returns_standard_error_for_invalid_ip() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/ip?ip=example.com")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "IP_INVALID"


def test_ip_endpoint_returns_standard_error_when_ip_is_missing() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/ip")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"
