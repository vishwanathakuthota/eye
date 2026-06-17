from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.domain_analysis import DomainAnalysis
from app.models.ip_analysis import IpAnalysis


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
    return TestClient(app), TestingSessionLocal


def seed_reports(db: Session) -> None:
    now = datetime.now(UTC)
    db.add(
        DomainAnalysis(
            report_id="rep_api",
            domain="example.com",
            risk_score=20,
            risk_level="Low",
            summary="Domain summary.",
            dns={"records": {"A": ["93.184.216.34"]}},
            rdap={"handle": "EXAMPLE", "unsafe": "<script>alert('x')</script>"},
            certificates=[{"name_value": "www.example.com"}],
            subdomains=["www.example.com"],
            sources=[{"name": "dns", "status": "completed"}],
            created_at=now - timedelta(minutes=10),
        )
    )
    db.add(
        IpAnalysis(
            report_id="ipr_api",
            ip="8.8.8.8",
            ip_version=4,
            risk_score=5,
            risk_level="Low",
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


def test_reports_endpoint_lists_domain_and_ip_reports() -> None:
    client, session_factory = build_client()
    with session_factory() as db:
        seed_reports(db)

    response = client.get("/api/v1/reports")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 2
    assert body["data"]["limit"] == 20
    assert body["data"]["offset"] == 0
    assert body["data"]["items"][0]["report_id"] == "ipr_api"
    assert body["data"]["items"][0]["type"] == "ip"
    assert body["data"]["items"][0]["target"] == "8.8.8.8"
    assert body["data"]["items"][1]["report_id"] == "rep_api"
    assert body["data"]["items"][1]["type"] == "domain"


def test_reports_endpoint_paginates_reports() -> None:
    client, session_factory = build_client()
    with session_factory() as db:
        seed_reports(db)

    response = client.get("/api/v1/reports?limit=1&offset=1")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 2
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["report_id"] == "rep_api"


def test_report_detail_endpoint_returns_domain_payload() -> None:
    client, session_factory = build_client()
    with session_factory() as db:
        seed_reports(db)

    response = client.get("/api/v1/reports/rep_api")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["type"] == "domain"
    assert body["data"]["target"] == "example.com"
    assert body["data"]["payload"]["domain"] == "example.com"
    assert body["data"]["payload"]["dns"]["records"]["A"] == ["93.184.216.34"]


def test_report_detail_endpoint_returns_ip_payload() -> None:
    client, session_factory = build_client()
    with session_factory() as db:
        seed_reports(db)

    response = client.get("/api/v1/reports/ipr_api")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["type"] == "ip"
    assert body["data"]["target"] == "8.8.8.8"
    assert body["data"]["payload"]["ip"] == "8.8.8.8"
    assert body["data"]["payload"]["reverse_dns"]["ptr_records"] == ["dns.google"]


def test_report_detail_endpoint_returns_not_found_error() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/reports/rep_missing")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "REPORT_NOT_FOUND"


def test_report_detail_endpoint_returns_validation_error() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/reports/bad%20id")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "REPORT_INVALID"


def test_reports_endpoint_returns_standard_error_for_invalid_pagination() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/reports?limit=101")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_report_json_export_endpoint_returns_full_report_document() -> None:
    client, session_factory = build_client()
    with session_factory() as db:
        seed_reports(db)

    response = client.get("/api/v1/reports/rep_api/export/json")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="eye-rep_api.json"'
    )
    body = response.json()
    assert body["metadata"]["product"] == "Eye"
    assert body["metadata"]["report_id"] == "rep_api"
    assert body["metadata"]["type"] == "domain"
    assert body["metadata"]["target"] == "example.com"
    assert body["report"]["domain"] == "example.com"
    assert body["report"]["rdap"]["unsafe"] == "<script>alert('x')</script>"


def test_report_html_export_endpoint_returns_printable_html_and_escapes_content() -> (
    None
):
    client, session_factory = build_client()
    with session_factory() as db:
        seed_reports(db)

    response = client.get("/api/v1/reports/rep_api/export/html")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert (
        response.headers["content-disposition"] == 'inline; filename="eye-rep_api.html"'
    )
    assert "Executive Investigation Report" in response.text
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in response.text
    assert "<script>alert('x')</script>" not in response.text


def test_report_json_export_endpoint_returns_not_found_error() -> None:
    client, _session_factory = build_client()

    response = client.get("/api/v1/reports/rep_missing/export/json")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "REPORT_NOT_FOUND"


def test_report_html_export_endpoint_returns_ip_report() -> None:
    client, session_factory = build_client()
    with session_factory() as db:
        seed_reports(db)

    response = client.get("/api/v1/reports/ipr_api/export/html")

    assert response.status_code == 200
    assert "IP intelligence report for <strong>8.8.8.8</strong>" in response.text
    assert "Reverse DNS" in response.text
