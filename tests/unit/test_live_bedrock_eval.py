import copy
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from botocore.session import get_session
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from packages.evals import run as evaluations
from scripts import live_bedrock_eval as live
from services.agent.models import AgentRequest, Metrics, Plan
from services.agent.observability import AuditLogger, ContentFreeExporter
from services.agent.workflow import Workflow


@pytest.fixture(autouse=True)
def no_aws_calls(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Tests must not create a real AWS client or session")

    monkeypatch.setattr(live.boto3, "Session", forbidden)
    monkeypatch.setattr(live.boto3, "client", forbidden)
    monkeypatch.setattr(live.boto3, "resource", forbidden)
    monkeypatch.delenv("AUDIT_TABLE", raising=False)
    monkeypatch.setenv("AWS_IGNORE_CONFIGURED_ENDPOINT_URLS", "false")


def configured():
    return {
        "AWS_REGION": "us-east-1",
        "BEDROCK_MODEL_ID": "amazon.nova-lite-v1:0",
        "BEDROCK_INPUT_USD_PER_MILLION": "0.06",
        "BEDROCK_OUTPUT_USD_PER_MILLION": "0.24",
        "BEDROCK_RATE_VERIFIED_ON": datetime.now(UTC).date().isoformat(),
    }


class Session:
    def __init__(self, credentials=True, identity_error=None):
        self.credentials = credentials
        self.identity_error = identity_error
        self.calls = []
        self.detail = {
            "modelId": "amazon.nova-lite-v1:0",
            "inputModalities": ["TEXT"],
            "outputModalities": ["TEXT"],
            "inferenceTypesSupported": ["ON_DEMAND"],
        }
        self.availability = {
            "modelId": "amazon.nova-lite-v1:0",
            "authorizationStatus": "AUTHORIZED",
            "entitlementAvailability": "AVAILABLE",
            "regionAvailability": "AVAILABLE",
            "agreementAvailability": {"status": "AVAILABLE"},
        }

    def get_credentials(self):
        return object() if self.credentials else None

    def client(self, name, **kwargs):
        self.calls.append((name, kwargs))
        return self

    def get_caller_identity(self):
        if self.identity_error:
            raise self.identity_error
        return {"Account": "private-account", "Arn": "private-arn", "UserId": "private-user"}

    def get_foundation_model(self, **kwargs):
        self.calls.append(("model", kwargs))
        return {"modelDetails": self.detail}

    def get_foundation_model_availability(self, **kwargs):
        self.calls.append(("availability", kwargs))
        return self.availability


def phase_result(case_ids):
    return {
        "mode": "bedrock",
        "passed": True,
        "aggregate": {"total_estimated_llm_cost_usd": 0.001 * len(case_ids)},
        "cases": [
            {
                "id": case_id,
                "scores": {**{key: 1.0 for key in evaluations.GATES}, "hallucination_rate": 0.0},
                "response": {
                    "mode": "bedrock",
                    "metrics": Metrics(
                        input_tokens=50, output_tokens=10, estimated_cost_usd=0.001
                    ).model_dump(),
                },
            }
            for case_id in case_ids
        ],
    }


def test_settings_requires_fresh_explicit_bounded_prices_and_region():
    assert live.settings(configured()) == configured()
    for missing in configured():
        settings = configured()
        settings.pop(missing)
        with pytest.raises(ValueError):
            live.settings(settings)


@pytest.mark.parametrize(
    "key,value",
    [
        ("AWS_REGION", "https://example.com"),
        ("AWS_REGION", "us-east-1\n"),
        ("BEDROCK_MODEL_ID", "arn:aws:bedrock:region:account:foundation-model/x"),
        ("BEDROCK_MODEL_ID", "model\n"),
        ("BEDROCK_INPUT_USD_PER_MILLION", "0"),
        ("BEDROCK_OUTPUT_USD_PER_MILLION", "-1"),
        ("BEDROCK_INPUT_USD_PER_MILLION", "Infinity"),
        ("BEDROCK_OUTPUT_USD_PER_MILLION", "NaN"),
        ("BEDROCK_INPUT_USD_PER_MILLION", "1000"),
        ("BEDROCK_RATE_VERIFIED_ON", "2000-01-01"),
        ("BEDROCK_RATE_VERIFIED_ON", (datetime.now(UTC).date() + timedelta(days=1)).isoformat()),
        ("AUDIT_TABLE", "unexpected-cloud-audit"),
    ],
)
def test_invalid_settings_never_get_as_far_as_aws(key, value):
    with pytest.raises(ValueError):
        live.settings({**configured(), key: value})


def test_model_preflight_checks_identity_region_modality_and_entitlement():
    session = Session()
    result = live.check_model_access(session, configured())
    assert result == {"identity_verified": True, "model_access_verified": True}
    assert "private" not in json.dumps(result)
    assert [item[0] for item in session.calls] == ["sts", "bedrock", "model", "availability"]
    for _, kwargs in session.calls[:2]:
        assert kwargs["region_name"] == "us-east-1"
        assert kwargs["config"].retries == {"total_max_attempts": 1}
        assert kwargs["config"].ignore_configured_endpoint_urls is True
    assert session.calls[2][1] == {"modelIdentifier": configured()["BEDROCK_MODEL_ID"]}


def test_missing_or_invalid_credentials_prevent_model_calls():
    missing = Session(credentials=False)
    with pytest.raises(ValueError):
        live.check_model_access(missing, configured())
    assert not missing.calls
    invalid = Session(identity_error=RuntimeError("private credential detail"))
    with pytest.raises(RuntimeError):
        live.check_model_access(invalid, configured())
    assert [item[0] for item in invalid.calls] == ["sts"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("modelId", "other.model-v1:0"),
        ("inputModalities", ["IMAGE"]),
        ("outputModalities", ["EMBEDDING"]),
        ("inferenceTypesSupported", ["PROVISIONED"]),
    ],
)
def test_incompatible_regional_model_refused(field, value):
    session = Session()
    session.detail[field] = value
    with pytest.raises(ValueError):
        live.check_model_access(session, configured())
    assert "availability" not in [item[0] for item in session.calls]


@pytest.mark.parametrize(
    "field,value",
    [
        ("modelId", "other.model-v1:0"),
        ("authorizationStatus", "NOT_AUTHORIZED"),
        ("entitlementAvailability", "NOT_AVAILABLE"),
        ("regionAvailability", "NOT_AVAILABLE"),
        ("agreementAvailability", {"status": "NOT_AVAILABLE"}),
    ],
)
def test_access_denials_prevent_qualification(field, value):
    session = Session()
    session.availability[field] = value
    with pytest.raises(ValueError):
        live.check_model_access(session, configured())


def test_observed_nova_availability_id_may_omit_version_without_changing_requested_model():
    session = Session()
    session.detail["inputModalities"] = ["TEXT", "IMAGE", "VIDEO"]
    session.detail["inferenceTypesSupported"] = ["INFERENCE_PROFILE", "ON_DEMAND"]
    session.availability["modelId"] = "amazon.nova-lite-v1"
    configuration = configured()
    assert live.check_model_access(session, configuration) == {
        "identity_verified": True,
        "model_access_verified": True,
    }
    assert configuration["BEDROCK_MODEL_ID"] == "amazon.nova-lite-v1:0"
    assert session.calls[-1] == ("availability", {"modelId": "amazon.nova-lite-v1:0"})
    assert session.calls[-2] == ("model", {"modelIdentifier": "amazon.nova-lite-v1:0"})


@pytest.mark.parametrize(
    "availability_id",
    [
        "amazon.nova-lite-v1:1",
        "amazon.nova-lite-v2",
        "amazon.nova-pro-v1",
        "other.nova-lite-v1",
        "amazon.nova-lite-v1:0:1",
        "amazon.nova-lite-v1\n",
        None,
    ],
)
def test_versionless_availability_exception_never_accepts_other_versions_or_models(availability_id):
    session = Session()
    session.availability["modelId"] = availability_id
    with pytest.raises(ValueError):
        live.check_model_access(session, configured())


@pytest.mark.parametrize("detail_id", ["amazon.nova-lite-v1", "amazon.nova-lite-v1:1"])
def test_availability_canonicalization_does_not_relax_exact_model_details(detail_id):
    session = Session()
    session.detail["modelId"] = detail_id
    session.availability["modelId"] = "amazon.nova-lite-v1"
    with pytest.raises(ValueError):
        live.check_model_access(session, configured())
    assert "availability" not in [name for name, _ in session.calls]


def test_main_preflight_failure_is_not_tested_without_any_live_artifact(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(live, "settings", lambda _: configured())
    monkeypatch.setattr(live.boto3, "Session", lambda: Session(credentials=False))
    monkeypatch.setattr(
        "sys.argv", ["live_bedrock_eval.py", "--output", str(tmp_path / "bedrock.json")]
    )
    with pytest.raises(SystemExit) as caught:
        live.main()
    assert caught.value.code == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "NOT TESTED" and result["phase"] == "preflight"
    assert not list(tmp_path.iterdir())


def test_main_bad_config_does_not_even_construct_aws_session(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.setattr(
        "sys.argv", ["live_bedrock_eval.py", "--output", str(tmp_path / "bedrock.json")]
    )
    with pytest.raises(SystemExit) as caught:
        live.main()
    assert caught.value.code == 2 and "NOT TESTED" in capsys.readouterr().out
    assert not list(tmp_path.iterdir())


def test_harness_ignores_custom_endpoints_for_preflight_and_later_planner_clients(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    monkeypatch.setenv("AWS_ENDPOINT_URL_BEDROCK_RUNTIME", "https://custom.invalid")
    monkeypatch.setattr(live, "settings", lambda _: configured())

    def session_factory():
        # SDK configuration lookup is local only; no clients or network are created.
        assert get_session().get_config_variable("ignore_configured_endpoint_urls") is True
        return Session(credentials=False)

    monkeypatch.setattr(live.boto3, "Session", session_factory)
    monkeypatch.setattr(
        "sys.argv", ["live_bedrock_eval.py", "--output", str(tmp_path / "bedrock.json")]
    )
    with pytest.raises(SystemExit) as caught:
        live.main()
    assert caught.value.code == 2
    assert get_session().get_config_variable("ignore_configured_endpoint_urls") is True
    assert "NOT TESTED" in capsys.readouterr().out and not list(tmp_path.iterdir())


def test_phase_sequence_uses_real_mode_and_all_twenty_final_cases(tmp_path):
    calls = []

    def runner(**kwargs):
        calls.append(kwargs)
        assert kwargs["output"].parent == tmp_path
        kwargs["output"].write_text("test fixture only")
        return phase_result(kwargs["case_ids"])

    report = live.run_phases(tmp_path / "test-results.json", {}, runner=runner)
    assert report["status"] == "PASS" and report["cost_measurement_complete"]
    assert [len(call["case_ids"]) for call in calls] == [1, 3, 20]
    assert [call["stop_on_failure"] for call in calls] == [True, True, False]
    assert all(call["mode"] == "bedrock" for call in calls)
    assert report["total_reported_cost_usd_including_probe_and_smoke"] == pytest.approx(0.024)
    assert report["phases"]["suite"]["total_input_tokens"] == 1000


@pytest.mark.parametrize(
    "fault",
    [
        "local_mode",
        "local_response",
        "no_tokens",
        "no_output",
        "unknown_cost",
        "missing_case",
        "wrong_case",
        "case_failure",
        "gate_failure",
    ],
)
def test_single_case_failure_stops_before_smoke(tmp_path, fault):
    calls = []

    def runner(**kwargs):
        calls.append(kwargs)
        result = phase_result(kwargs["case_ids"])
        row = result["cases"][0]
        if fault == "local_mode":
            result["mode"] = "local"
        elif fault == "local_response":
            row["response"]["mode"] = "local"
        elif fault == "no_tokens":
            row["response"]["metrics"]["input_tokens"] = 0
        elif fault == "no_output":
            row["response"]["metrics"]["output_tokens"] = 0
        elif fault == "unknown_cost":
            row["response"]["metrics"]["cost_estimate_complete"] = False
        elif fault == "missing_case":
            result["cases"] = []
        elif fault == "wrong_case":
            row["id"] = "case-005"
        elif fault == "case_failure":
            row["scores"]["answer_correctness"] = 0
        else:
            result["passed"] = False
        return result

    report = live.run_phases(tmp_path / "test.json", {}, runner=runner)
    assert report["status"] == "FAIL" and report["stopped_after"] == "single"
    assert len(calls) == 1 and not report["phases"]["single"]["passed"]


def test_smoke_individual_failure_cannot_hide_in_aggregate_pass(tmp_path):
    calls = []

    def runner(**kwargs):
        calls.append(kwargs)
        result = phase_result(kwargs["case_ids"])
        if len(calls) == 2:
            result["cases"][0]["scores"]["answer_correctness"] = 0
        return result

    report = live.run_phases(tmp_path / "test.json", {}, runner=runner)
    assert report["status"] == "FAIL" and report["stopped_after"] == "smoke" and len(calls) == 2


def test_final_suite_records_all_twenty_and_actual_failed_case_count(tmp_path):
    def runner(**kwargs):
        result = phase_result(kwargs["case_ids"])
        if len(kwargs["case_ids"]) == 20:
            result["cases"][0]["scores"]["answer_correctness"] = 0
            result["aggregate"]["answer_correctness"] = 0.95
        return result

    report = live.run_phases(tmp_path / "test.json", {}, runner=runner)
    assert report["status"] == "PASS"  # Final status reflects configured aggregate gates.
    assert report["phases"]["suite"]["passed_case_count"] == 19
    assert report["phases"]["suite"]["case_count"] == 20


def test_exception_preserves_prior_reported_cost_marks_unknown_and_redacts_error(tmp_path):
    calls = []

    def runner(**kwargs):
        calls.append(kwargs)
        if len(calls) == 2:
            raise RuntimeError("Bearer private-secret customer@example.com")
        return phase_result(kwargs["case_ids"])

    report = live.run_phases(tmp_path / "test.json", {}, runner=runner)
    assert report["status"] == "FAIL" and not report["cost_measurement_complete"]
    assert report["total_reported_cost_usd_including_probe_and_smoke"] == 0.001
    assert report["phases"]["smoke"]["error_type"] == "RuntimeError"
    assert "private-secret" not in json.dumps(report) and "customer@example" not in json.dumps(
        report
    )


def test_trace_failure_stops_before_more_live_calls(tmp_path):
    calls = []

    def runner(**kwargs):
        calls.append(kwargs)
        return phase_result(kwargs["case_ids"])

    report = live.run_phases(
        tmp_path / "test.json", {}, runner=runner, phase_probe=lambda: {"status": "FAIL"}
    )
    assert report["status"] == "FAIL" and report["stopped_after"] == "single" and len(calls) == 1


@pytest.fixture
def recorded_spans(tmp_path, monkeypatch):
    exporter = InMemorySpanExporter()
    provider = TracerProvider(
        resource=Resource({"service.name": "banking-ai-prototype-lab-live-eval"})
    )
    provider.add_span_processor(SimpleSpanProcessor(ContentFreeExporter(exporter)))
    monkeypatch.setattr(trace, "get_tracer", provider.get_tracer)

    class StubPlanner:
        mode = "bedrock"

        def plan(self, request, evidence):
            return Plan(evidence_ids=[item.id for item in evidence]), Metrics(
                input_tokens=50, output_tokens=10, estimated_cost_usd=0.001
            )

    Workflow(planner=StubPlanner(), audit=AuditLogger(tmp_path / "audit.jsonl")).run(
        AgentRequest(question="What is the onboarding procedure?")
    )
    yield exporter
    provider.shutdown()


def test_trace_probe_accepts_actual_workflow_attribute_names(recorded_spans):
    result = live.trace_probe(recorded_spans)
    assert result["status"] == "PASS" and result["nine_stages_present"]
    assert result["workflow_span_present"] and result["exported_span_count"] >= 10


@pytest.mark.parametrize(
    "location",
    [
        "unknown_attribute",
        "metric_name",
        "metric_value",
        "request_id",
        "risk_flag",
        "span_name",
        "event",
        "status",
        "resource",
        "scope",
        "link",
    ],
)
def test_probe_rejects_unexpected_content_without_returning_it(recorded_spans, location):
    spans = list(recorded_spans.get_finished_spans())
    source = spans[-1]
    fake = SimpleNamespace(
        name=source.name,
        attributes=dict(source.attributes),
        events=source.events,
        status=source.status,
        links=source.links,
        resource=source.resource,
        instrumentation_scope=source.instrumentation_scope,
    )
    secret = "private-secret customer@example.com"
    if location == "unknown_attribute":
        fake.attributes["prompt"] = secret
    elif location == "metric_name":
        fake.attributes["agent.metrics.prompt"] = secret
    elif location == "metric_value":
        fake.attributes["agent.metrics.input_tokens"] = secret
    elif location == "request_id":
        fake.attributes["request.id"] = secret
    elif location == "risk_flag":
        fake.attributes["agent.risk_flags"] = [secret]
    elif location == "span_name":
        fake.name = secret
    elif location == "event":
        fake.events = [secret]
    elif location == "status":
        fake.status = SimpleNamespace(description=secret)
    elif location == "resource":
        fake.resource = Resource(
            {"service.name": "banking-ai-prototype-lab-live-eval", "prompt": secret}
        )
    elif location == "scope":
        fake.instrumentation_scope = SimpleNamespace(name=secret)
    elif location == "link":
        fake.links = [secret]
    spans[-1] = fake
    result = live.trace_probe(SimpleNamespace(get_finished_spans=lambda: spans))
    assert result["status"] == "FAIL" and secret not in json.dumps(result)


def test_empty_probe_never_claims_privacy_was_verified():
    result = live.trace_probe(InMemorySpanExporter())
    assert result["status"] == "FAIL" and result["exported_span_count"] == 0


def test_evaluation_subset_preserves_order_and_rejects_unknown_modes(tmp_path, monkeypatch):
    cases = evaluations.load_cases()
    monkeypatch.setattr(evaluations, "load_cases", lambda: cases)
    monkeypatch.setattr(evaluations, "ROOT", tmp_path)
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals/cases.jsonl").write_text("synthetic test fixture hash input")
    result = evaluations.evaluate(case_ids=["case-005", "case-001"], output=tmp_path / "local.json")
    assert [row["id"] for row in result["cases"]] == ["case-005", "case-001"]
    assert result["mode"] == "local" and result["aggregate"]["input_tokens"] == 0
    for bad in [[], ["case-001", "case-001"], ["case-999"]]:
        with pytest.raises(ValueError):
            evaluations.evaluate(case_ids=bad, output=tmp_path / "never-written.json")
    with pytest.raises(ValueError):
        evaluations.evaluate(mode="bedrocck", output=tmp_path / "never-written.json")
    assert not (tmp_path / "never-written.json").exists()


def test_qualification_evaluation_stops_after_failing_case(tmp_path, monkeypatch):
    cases = copy.deepcopy(evaluations.load_cases())
    cases[0]["required_answer_fragments"] = ["deliberately impossible synthetic test requirement"]
    monkeypatch.setattr(evaluations, "load_cases", lambda: cases)
    monkeypatch.setattr(evaluations, "ROOT", tmp_path)
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals/cases.jsonl").write_text("synthetic test fixture hash input")
    result = evaluations.evaluate(
        case_ids=["case-001", "case-005"],
        stop_on_failure=True,
        output=tmp_path / "local-failure.json",
    )
    assert result["case_count"] == 1 and result["requested_case_count"] == 2
    assert result["stopped_early"] and not result["passed"]
    assert "individual_case_failure" in result["gate_failures"]


@pytest.mark.parametrize(
    "arguments,expected",
    [
        ([], "latest.json"),
        (["--smoke"], "smoke.json"),
        (["--mode", "bedrock"], f"bedrock-{datetime.now(UTC).date()}-direct.json"),
        (["--mode", "bedrock", "--smoke"], f"bedrock-{datetime.now(UTC).date()}-direct.json"),
    ],
)
def test_cli_defaults_separate_live_smoke_and_full_local_artifacts(
    tmp_path, monkeypatch, capsys, arguments, expected
):
    calls = []

    def fake_evaluate(**kwargs):
        calls.append(kwargs)
        return {
            "case_count": 1,
            "mode": kwargs["mode"],
            "aggregate": {},
            "gate_failures": {},
            "passed": True,
        }

    monkeypatch.setattr(evaluations, "ROOT", tmp_path)
    monkeypatch.setattr(evaluations, "evaluate", fake_evaluate)
    monkeypatch.setattr("sys.argv", ["packages.evals.run", *arguments])
    with pytest.raises(SystemExit) as caught:
        evaluations.main()
    assert caught.value.code == 0
    assert calls[0]["output"] == tmp_path / "evals/results" / expected
    assert not list(tmp_path.iterdir())  # Mocked commands never create claimed live results.
    capsys.readouterr()
