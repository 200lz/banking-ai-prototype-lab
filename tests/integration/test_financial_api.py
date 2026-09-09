import pytest
from fastapi.testclient import TestClient

from services.agent.observability import AuditLogger
from services.agent.workflow import Workflow
from services.api.main import create_app


@pytest.mark.integration
def test_financial_api_typed_profile_and_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("API_AUTH_MODE", "local")
    monkeypatch.delenv("AWS_LAMBDA_FUNCTION_NAME", raising=False)
    client = TestClient(create_app(Workflow(audit=AuditLogger(tmp_path / "audit"))))
    result = client.post(
        "/v1/query", json={"question": "Prepare an SME lending review", "company_id": "SYN-SME-001"}
    )
    assert result.status_code == 200
    data = result.json()
    assert data["human_review_required"] and data["financial_profile"]["source"] == "local"
    assert data["financial_profile"]["provenance"]["layer"] == "gold"
    assert len(data["financial_profile"]["provenance"]["gold_record_sha256"]) == 64
    for company_id in ["SYN-SME-001\n", "customer@example.com", "' OR 1=1"]:
        response = client.post(
            "/v1/query", json={"question": "lending review", "company_id": company_id}
        )
        assert response.status_code == 422 and company_id not in response.text
    assert (
        client.post(
            "/v1/query",
            json={"question": "lending", "company_id": "SYN-SME-001", "sql": "SELECT * FROM raw"},
        ).status_code
        == 422
    )
