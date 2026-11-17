
from fastapi.testclient import TestClient

from app.api.main import app


def test_metrics_endpoint_returns_prometheus_metrics():
    with TestClient(app) as client:
        # Generate one API request so that request metrics exist.
        health_response = client.get("/health")
        assert health_response.status_code == 200

        metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "rag_api_requests_total" in metrics_response.text
    assert "rag_api_request_duration_seconds" in metrics_response.text
    assert "rag_api_errors_total" in metrics_response.text


def test_health_request_is_recorded_in_metrics():
    with TestClient(app) as client:
        client.get("/health")
        metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert 'endpoint="/health"' in metrics_response.text
    assert 'method="GET"' in metrics_response.text
