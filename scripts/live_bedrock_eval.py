"""Explicit live-only qualification: model access, one case, smoke, then 20 cases."""

import argparse
import importlib.metadata
import json
import math
import os
import re
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config

from packages.evals.run import case_passes, evaluate
from services.agent.models import Metrics
from services.agent.observability import ContentFreeExporter, configure_private_sdk_logging

ROOT = Path(__file__).resolve().parents[1]
LIVE_CASE_IDS = [
    f"case-{number:03d}"
    for number in (1, 5, 9, 14, 17, 21, 25, 27, 30, 32, 36, 41, 45, 49, 50, 52, 54, 56, 57, 58)
]
PHASES = {
    "single": ["case-001"],
    "smoke": ["case-005", "case-036", "case-045"],
    "suite": LIVE_CASE_IDS,
}


def settings(environment: Mapping[str, str]) -> dict[str, str]:
    if environment.get("AUDIT_TABLE"):
        raise ValueError("Live evaluation requires local file audit; unset AUDIT_TABLE")
    required = (
        "AWS_REGION",
        "BEDROCK_MODEL_ID",
        "BEDROCK_INPUT_USD_PER_MILLION",
        "BEDROCK_OUTPUT_USD_PER_MILLION",
        "BEDROCK_RATE_VERIFIED_ON",
    )
    if any(not environment.get(key) for key in required):
        raise ValueError(
            "Configure explicit region, model, both token prices and rate verification date"
        )
    values = {key: environment[key] for key in required}
    if not re.fullmatch(r"[a-z]{2}(?:-[a-z]+)+-\d", values["AWS_REGION"]):
        raise ValueError("Invalid regional endpoint selection")
    if not re.fullmatch(r"[a-z0-9][a-z0-9.:-]{1,139}", values["BEDROCK_MODEL_ID"]):
        raise ValueError(
            "Use a regional foundation model ID; resource ARNs and inference profiles are excluded"
        )
    for key in required[2:4]:
        value = Decimal(values[key])
        if not value.is_finite() or not 0 < value < 1000:
            raise ValueError("Model rates must be positive bounded USD per million tokens")
    verified = date.fromisoformat(values["BEDROCK_RATE_VERIFIED_ON"])
    if not 0 <= (datetime.now(UTC).date() - verified).days <= 31:
        raise ValueError("Verify the regional model price within the last 31 days")
    return values


def check_model_access(session: Any, configuration: dict[str, str]) -> dict[str, Any]:
    if session.get_credentials() is None:
        raise ValueError("AWS credentials are unavailable")
    config = Config(
        connect_timeout=2,
        read_timeout=10,
        retries={"total_max_attempts": 1},
        ignore_configured_endpoint_urls=True,
    )
    kwargs = {"region_name": configuration["AWS_REGION"], "config": config}
    # Never persist Account/Arn/UserId from the identity response.
    session.client("sts", **kwargs).get_caller_identity()
    client = session.client("bedrock", **kwargs)
    model_id = configuration["BEDROCK_MODEL_ID"]
    detail = client.get_foundation_model(modelIdentifier=model_id)["modelDetails"]
    if (
        detail.get("modelId") != model_id
        or "TEXT" not in detail["inputModalities"]
        or "TEXT" not in detail["outputModalities"]
        or "ON_DEMAND" not in detail["inferenceTypesSupported"]
    ):
        raise ValueError("The selected model does not support this regional text inference path")
    availability = client.get_foundation_model_availability(modelId=model_id)
    # Bedrock can return a versionless ID for availability (observed for Nova Lite).
    # Details above still bind the exact requested model; never accept another explicit version.
    availability_ids = (model_id, re.sub(r":[0-9]+$", "", model_id))
    if (
        availability.get("modelId") not in availability_ids
        or availability.get("authorizationStatus") != "AUTHORIZED"
        or availability.get("entitlementAvailability") != "AVAILABLE"
        or availability.get("regionAvailability") != "AVAILABLE"
        or availability.get("agreementAvailability", {}).get("status") != "AVAILABLE"
    ):
        raise ValueError("Selected model access/entitlement/region/agreement is unavailable")
    return {"identity_verified": True, "model_access_verified": True}


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    rows = result["cases"]
    return {
        "passed": result["passed"],
        "case_count": len(rows),
        "passed_case_count": sum(case_passes(row["scores"]) for row in rows),
        "cases_with_reported_model_usage": sum(
            row["response"]["metrics"]["input_tokens"] > 0 for row in rows
        ),
        "total_input_tokens": sum(row["response"]["metrics"]["input_tokens"] for row in rows),
        "total_output_tokens": sum(row["response"]["metrics"]["output_tokens"] for row in rows),
        "cost_measurement_complete": all(
            row["response"]["metrics"]["cost_estimate_complete"] for row in rows
        ),
        "aggregate": result["aggregate"],
    }


def run_phases(
    output: Path,
    metadata: dict[str, Any],
    runner: Callable[..., dict[str, Any]] = evaluate,
    phase_probe: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    report: dict[str, Any] = {**metadata, "status": "FAIL", "phases": {}}
    for name, case_ids in PHASES.items():
        artifact = output.with_name(output.stem + "-" + name + ".json")
        try:
            result = runner(
                mode="bedrock", case_ids=case_ids, output=artifact, stop_on_failure=name != "suite"
            )
            report["phases"][name] = summarize(result)
            phase = report["phases"][name]
            # Qualification rejects individual defects; the final suite reports aggregate gates.
            valid_live_result = (
                result.get("mode") == "bedrock"
                and [row["id"] for row in result["cases"]] == case_ids
                and all(row["response"].get("mode") == "bedrock" for row in result["cases"])
                and (name == "suite" or phase["passed_case_count"] == len(case_ids))
                and phase["cost_measurement_complete"]
                and phase["total_input_tokens"] > 0
                and phase["total_output_tokens"] > 0
            )
            if phase_probe is not None:
                phase["telemetry_probe"] = phase_probe()
                valid_live_result = (
                    valid_live_result and phase["telemetry_probe"]["status"] == "PASS"
                )
            if not result["passed"] or not valid_live_result:
                phase["passed"] = False
                report["stopped_after"] = name
                break
        except Exception as error:
            # An invocation may have been billed even when no usable result was returned.
            report["phases"][name] = {
                "passed": False,
                "error_type": type(error).__name__,
                "cost_measurement_complete": False,
            }
            report["stopped_after"] = name
            break
    else:
        report["status"] = "PASS"
    report["total_reported_cost_usd_including_probe_and_smoke"] = sum(
        phase.get("aggregate", {}).get("total_estimated_llm_cost_usd", 0)
        for phase in report["phases"].values()
    )
    report["cost_measurement_complete"] = all(
        phase["cost_measurement_complete"] for phase in report["phases"].values()
    )
    return report


def configure_trace_probe() -> Any:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    exporter = InMemorySpanExporter()
    provider = TracerProvider(
        resource=Resource({"service.name": "banking-ai-prototype-lab-live-eval"})
    )
    provider.add_span_processor(SimpleSpanProcessor(ContentFreeExporter(exporter)))
    trace.set_tracer_provider(provider)
    return exporter


def trace_probe(exporter: Any) -> dict[str, Any]:
    spans = exporter.get_finished_spans()
    stages = {
        "user_request",
        "intent_analysis",
        "retrieval",
        "agent_planning",
        "controlled_tool_execution",
        "guardrail_validation",
        "citation_verification",
        "human_approval_decision",
        "final_response",
    }
    tools = {
        "policy_search",
        "document_retrieval",
        "deterministic_calculation",
        "risk_classification",
        "citation_verification",
        "financial_profile_tool",
        "denied",
    }
    risks = {
        "pii_redacted",
        "prompt_injection_detected",
        "unsafe_source",
        "conflicting_evidence",
        "insufficient_evidence",
        "retrieval_failure",
        "model_cost_unavailable",
        "planner_failure",
        "financial_data_stale",
        "financial_data_incomplete",
        "financial_profile_unavailable",
        "tool_failure",
        "citation_verification_failed",
        "malicious_instruction",
        "prohibited_action",
        "out_of_scope",
        "missing_information",
    }
    allowed = {
        "request.id",
        "agent.mode",
        "agent.human_review_required",
        "agent.risk_flags",
        "workflow.stage",
        "workflow.status",
        "tool.name",
        "tool.status",
    } | {"agent.metrics." + field for field in Metrics.model_fields}
    invalid = [key for span in spans for key in (span.attributes or {}) if key not in allowed]
    unsafe_values = 0
    for span in spans:
        attributes = span.attributes or {}
        for key, value in attributes.items():
            safe = True
            if key == "request.id":
                safe = (
                    isinstance(value, str)
                    and re.fullmatch(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}", value)
                    is not None
                )
            elif key == "agent.mode":
                safe = value == "bedrock"
            elif key in {"agent.human_review_required", "agent.metrics.cost_estimate_complete"}:
                safe = isinstance(value, bool)
            elif key == "agent.risk_flags":
                safe = isinstance(value, (list, tuple)) and all(item in risks for item in value)
            elif key == "workflow.stage":
                safe = value in stages
            elif key in {"workflow.status", "tool.status"}:
                safe = value in {"ok", "error"}
            elif key == "tool.name":
                safe = value in tools
            elif key.startswith("agent.metrics."):
                safe = type(value) in {int, float} and math.isfinite(value) and value >= 0
            unsafe_values += not safe
        safe_names = {"banking.workflow"} | stages | {"tool." + tool for tool in tools}
        unsafe_values += span.name not in safe_names
        unsafe_values += (
            span.instrumentation_scope is None
            or span.instrumentation_scope.name not in {"banking.governed-workflow", "banking.tools"}
        )
        unsafe_values += bool(span.status.description) or bool(span.links)
        resource = dict(span.resource.attributes)
        unsafe_values += resource != {"service.name": "banking-ai-prototype-lab-live-eval"}
    events = sum(len(span.events) for span in spans)
    complete_stages = stages <= {
        span.attributes.get("workflow.stage") for span in spans if span.attributes
    }
    workflow_present = any(span.name == "banking.workflow" for span in spans)
    return {
        "status": "PASS"
        if spans
        and not invalid
        and not unsafe_values
        and not events
        and complete_stages
        and workflow_present
        else "FAIL",
        "exported_span_count": len(spans),
        "unexpected_attribute_count": len(invalid),
        "unsafe_value_count": unsafe_values,
        "event_count": events,
        "nine_stages_present": complete_stages,
        "workflow_span_present": workflow_present,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / f"evals/results/bedrock-{datetime.now(UTC).date()}.json",
    )
    args = parser.parse_args()
    # This process claims real AWS qualification. Botocore honors this setting for
    # environment/profile endpoint overrides, including later Strands runtime clients.
    os.environ["AWS_IGNORE_CONFIGURED_ENDPOINT_URLS"] = "true"
    configure_private_sdk_logging()
    try:
        configuration = settings(os.environ)
        access = check_model_access(boto3.Session(), configuration)
    except Exception as error:
        print(
            json.dumps(
                {
                    "status": "NOT TESTED",
                    "phase": "preflight",
                    "error_type": type(error).__name__,
                    "reason": "Configure AWS credentials, explicit regional model access and verified token rates; no live evaluation was started",
                }
            )
        )
        raise SystemExit(2) from None
    exporter = configure_trace_probe()
    metadata = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "bedrock",
        "scope": "Actual bounded Strands/Bedrock inference; local synthetic retrieval and audit",
        "configuration": configuration,
        "configured_endpoint_overrides_ignored": True,
        "preflight": access,
        "strands_version": importlib.metadata.version("strands-agents"),
        "boto3_version": importlib.metadata.version("boto3"),
        "pricing_source": "https://aws.amazon.com/bedrock/pricing/",
    }
    report = run_phases(args.output, metadata, phase_probe=lambda: trace_probe(exporter))
    report["telemetry_probe"] = trace_probe(exporter)
    if report["telemetry_probe"]["status"] != "PASS":
        report["status"] = "FAIL"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown = [
        "# Live Bedrock evaluation",
        "",
        f"Status: **{report['status']}**",
        "",
        "One harmless case → three smoke cases → 20 representative cases; early failures stop progression.",
        "",
        "| Phase | Cases | Passed | Input/output tokens |",
        "| --- | --- | --- | --- |",
    ]
    for name, phase in report["phases"].items():
        markdown.append(
            f"| {name} | {phase.get('case_count', 'unknown')} | {phase.get('passed_case_count', 0)} | {phase.get('total_input_tokens', 'unknown')} / {phase.get('total_output_tokens', 'unknown')} |"
        )
    markdown.extend(
        [
            "",
            "See the JSON aggregate and separate per-case phase artifacts for quality, latency, reported cost and completeness. Failed unknown usage is not a verified $0 call. This is a development set, not held-out qualification.",
        ]
    )
    args.output.with_suffix(".md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "artifact": str(args.output),
                "cost_measurement_complete": report["cost_measurement_complete"],
            }
        )
    )
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
