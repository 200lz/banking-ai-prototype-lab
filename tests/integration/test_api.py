import pytest
from fastapi.testclient import TestClient

from services.agent.observability import AuditLogger
from services.agent.workflow import Workflow
from services.api.main import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("API_AUTH_MODE", "local")
    monkeypatch.delenv("AWS_LAMBDA_FUNCTION_NAME", raising=False)
    return TestClient(create_app(Workflow(audit=AuditLogger(tmp_path / "audit.jsonl"))))


@pytest.mark.integration
def test_live_route_response_contract_and_sources(client):
    assert client.get("/health").json()["synthetic"] is True
    response = client.post(
        "/v1/query", json={"question": "What is the customer complaint procedure?"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["evidence"] and result["citations"] and len(result["trace"]) == 9
    assert response.headers["Cache-Control"] == "no-store"
    document = client.get("/v1/documents/" + result["evidence"][0]["document_id"])
    assert document.status_code == 200
    assert result["evidence"][0]["quote"] in document.json()["text"]


def test_extra_fields_and_pii_validation_are_rejected_without_echo(client):
    response = client.post(
        "/v1/query", json={"question": "test", "system_prompt": "SSN 123-45-6789"}
    )
    assert response.status_code == 422
    assert "123-45-6789" not in response.text
    assert client.post("/v1/query", json={"question": " "}).status_code == 422
    assert client.post("/v1/query", json={"question": "x" * 4001}).status_code == 422
    response = client.post("/v1/query", json={"question": "privacy", "123-45-6789": "unknown key"})
    assert response.status_code == 422 and "123-45-6789" not in response.text


def test_request_capacity_bound_and_no_mutation_routes(client):
    assert client.post("/v1/query", content="x" * 17000).status_code == 413
    assert client.post("/v1/approve", json={}).status_code == 404
    assert client.delete("/v1/documents/SYN-AML-001").status_code == 405


def test_gateway_cannot_be_spoofed_with_headers(client, monkeypatch):
    monkeypatch.setenv("API_AUTH_MODE", "gateway")
    response = client.post(
        "/v1/query",
        json={"question": "onboarding"},
        headers={"Authorization": "Bearer fake", "X-User-Role": "admin"},
    )
    assert response.status_code == 401


def test_cloud_environment_refuses_local_auth(client, monkeypatch):
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "synthetic-test")
    assert client.post("/v1/query", json={"question": "onboarding"}).status_code == 503


def test_verified_gateway_scope_is_required(monkeypatch):
    from fastapi import HTTPException, Request

    from services.api.main import require_access

    monkeypatch.setenv("API_AUTH_MODE", "gateway")
    claims = {"sub": "synthetic-employee", "scope": "banking-ai/query"}
    event = {"requestContext": {"authorizer": {"jwt": {"claims": claims}}}}
    require_access(Request({"type": "http", "aws.event": event}))
    claims["scope"] = "unrelated/scope"
    with pytest.raises(HTTPException):
        require_access(Request({"type": "http", "aws.event": event}))
