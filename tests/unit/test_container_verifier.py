import json

import pytest

from packages.retrieval.local import LocalRetriever
from scripts import verify_containers as verifier
from services.agent.models import AgentRequest
from services.agent.observability import AuditLogger
from services.agent.workflow import Workflow


@pytest.mark.parametrize("scenario", list(verifier.SCENARIOS))
def test_container_assertions_accept_real_local_workflow(tmp_path, scenario):
    result = Workflow(audit=AuditLogger(tmp_path / "audit.jsonl")).run(
        AgentRequest.model_validate(verifier.SCENARIOS[scenario])
    )
    summary = verifier.validate_response(result.model_dump(mode="json"), scenario)
    assert summary["status"] == "PASS"
    assert "answer" not in summary and "question" not in summary


def test_container_assertions_independently_reject_bad_source_hash(tmp_path):
    result = (
        Workflow(audit=AuditLogger(tmp_path / "audit.jsonl"))
        .run(AgentRequest.model_validate(verifier.SCENARIOS["normal_policy"]))
        .model_dump(mode="json")
    )
    result["evidence"][0]["source_hash"] = "0" * 64
    with pytest.raises(AssertionError, match="versioned local source"):
        verifier.validate_response(result, "normal_policy")


def test_telemetry_requires_received_spans_and_rejects_payloads():
    logs = "banking.governed-workflow workflow.stage " + " ".join(verifier.STAGES)
    assert verifier.validate_telemetry(logs, [])["payload_matches"] == 0
    with pytest.raises(AssertionError, match="OpenTelemetry"):
        verifier.validate_telemetry("collector started", [])
    for payload in (
        "123-45-6789",
        "SYN-SME-001",
        verifier.INJECTION_TEXT,
        verifier.SCENARIOS["normal_policy"]["question"],
    ):
        with pytest.raises(AssertionError, match="runtime logs"):
            verifier.validate_telemetry(logs + " " + payload, [])
    document = LocalRetriever().documents[0]
    with pytest.raises(AssertionError, match="runtime logs"):
        verifier.validate_telemetry(
            logs + document.text, [{"evidence": [{"quote": document.text}]}]
        )


def test_verifier_refuses_existing_projects_without_cleanup(monkeypatch, tmp_path):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    runner = verifier.ContainerVerifier("banking-ai-validation-unit")
    commands = []

    def run(*arguments, **kwargs):
        commands.append(arguments)
        if arguments[0] == "version":
            return json.dumps({"Version": "test", "Os": "linux", "Arch": "amd64"})
        if arguments[0] == "ps":
            return "existing-container"
        raise AssertionError("No mutating command is allowed when a project already exists")

    monkeypatch.setattr(runner, "run", run)
    report = runner.verify()
    assert report["status"] == "FAIL"
    assert "existing Compose project" in report["failure"]["message"]
    assert not any("down" in command or "build" in command for command in commands)


def test_verifier_rejects_non_verification_project_name():
    with pytest.raises(ValueError, match="isolated"):
        verifier.ContainerVerifier("production")


def test_ephemeral_binding_is_rediscovered_and_remains_loopback():
    assert verifier.loopback_web_base("127.0.0.1:49100\n") == "http://127.0.0.1:49100"
    assert verifier.loopback_web_base("127.0.0.1:49200\n") == "http://127.0.0.1:49200"
    for binding in ("0.0.0.0:49100", "example.com:49100", "127.0.0.1:0", "127.0.0.1:99999"):
        with pytest.raises(AssertionError, match="loopback"):
            verifier.loopback_web_base(binding)
