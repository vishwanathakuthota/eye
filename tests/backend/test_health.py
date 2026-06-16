from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_standard_success_shape() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["error"] is None
    assert body["data"]["status"] == "ok"
    assert body["data"]["service"] == "eye-api"
    assert body["meta"]["version"] == "v0.1.0-alpha"
    assert body["meta"]["request_id"].startswith("req_")
