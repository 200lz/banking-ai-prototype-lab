"""Content-free OpenTelemetry and append-only structured audit records."""

import json
import logging
import os
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter, time
from typing import Any
from uuid import uuid4

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
    SpanExportResult,
)

from services.agent.models import StepTrace

_LOCK = threading.Lock()
_CONFIGURED = False


def configure_private_sdk_logging() -> None:
    """SDK debug/error payloads must not bypass the content-free audit boundary."""
    namespaces = ("strands", "botocore", "boto3", "urllib3", "databricks")
    names = set(namespaces) | {
        name
        for name in list(logging.Logger.manager.loggerDict)
        if name.startswith(tuple(prefix + "." for prefix in namespaces))
    }
    for name in names:
        logger = logging.getLogger(name)
        logger.handlers = [logging.NullHandler()]
        logger.propagate = False


def configure_audit_console() -> None:
    """Mirror only allowlisted audit JSON to the Lambda log stream when enabled."""
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME") and os.getenv("AUDIT_CONSOLE") != "1":
        return
    logger = logging.getLogger("banking.audit")
    with _LOCK:
        if not any(handler.name == "banking.audit.console" for handler in logger.handlers):
            handler = logging.StreamHandler()
            handler.set_name("banking.audit.console")
            handler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False


class ContentFreeExporter(SpanExporter):
    """Only our explicitly content-free spans may cross the telemetry boundary."""

    def __init__(self, downstream: SpanExporter) -> None:
        self.downstream = downstream

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        safe = [
            span
            for span in spans
            if span.instrumentation_scope is not None
            and span.instrumentation_scope.name.startswith("banking.")
        ]
        return self.downstream.export(safe) if safe else SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        self.downstream.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return self.downstream.force_flush(timeout_millis)


def configure_telemetry() -> None:
    global _CONFIGURED
    configure_private_sdk_logging()
    with _LOCK:
        if _CONFIGURED:
            return
        provider = TracerProvider(
            resource=Resource.create({"service.name": "banking-ai-prototype-lab"})
        )
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if endpoint:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            provider.add_span_processor(
                BatchSpanProcessor(
                    ContentFreeExporter(
                        OTLPSpanExporter(endpoint=endpoint.rstrip("/") + "/v1/traces")
                    )
                )
            )
        elif os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            provider.add_span_processor(
                BatchSpanProcessor(ContentFreeExporter(ConsoleSpanExporter()))
            )
        trace.set_tracer_provider(provider)
        _CONFIGURED = True


class AuditLogger:
    """Never receives prompts, documents, arguments, outputs, or exception details."""

    def __init__(self, path: str | Path | None = None, table: Any = None) -> None:
        configure_audit_console()
        self.path = Path(
            path if path is not None else os.environ.get("AUDIT_LOG_PATH", ".runtime/audit.jsonl")
        )
        self.table = table
        if self.table is None and os.getenv("AUDIT_TABLE"):
            import boto3

            self.table = boto3.resource("dynamodb").Table(os.environ["AUDIT_TABLE"])

    def emit(self, request_id: str, event: str, **metadata: Any) -> None:
        # Metadata is explicitly allowlisted so accidental future prompt logging fails closed.
        allowed = {
            "stage",
            "status",
            "duration_ms",
            "tool",
            "risk_flags",
            "human_review_required",
            "mode",
            "input_tokens",
            "output_tokens",
            "estimated_cost_usd",
            "cost_estimate_complete",
            "document_ids",
            "source_hashes",
        }
        if set(metadata) - allowed:
            raise ValueError("Audit metadata contains unapproved fields")
        record = {
            "request_id": request_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            **metadata,
        }
        line = json.dumps(record, separators=(",", ":"), sort_keys=True)
        logging.getLogger("banking.audit").info(line)
        if self.table is not None:
            self.table.put_item(
                Item={
                    "pk": request_id,
                    "sk": record["timestamp"] + "#" + str(uuid4()),
                    "expires_at": int(time())
                    + int(os.getenv("AUDIT_RETENTION_DAYS", "90")) * 86400,
                    "record": line,
                },
                ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
            )
        else:
            with _LOCK:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as stream:
                    stream.write(line + "\n")


class Recorder:
    def __init__(self, request_id: str, audit: AuditLogger) -> None:
        self.request_id = request_id
        self.audit = audit
        self.steps: list[StepTrace] = []
        self.tracer = trace.get_tracer("banking.governed-workflow")

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        started = perf_counter()
        status = "ok"
        # Automatic exception recording is disabled: exception text may contain PII.
        with self.tracer.start_as_current_span(
            name, record_exception=False, set_status_on_exception=False
        ) as span:
            span.set_attribute("request.id", self.request_id)
            span.set_attribute("workflow.stage", name)
            try:
                yield
            except Exception:
                status = "error"
                raise
            finally:
                elapsed = round((perf_counter() - started) * 1000, 3)
                self.steps.append(StepTrace(stage=name, duration_ms=elapsed, status=status))
                span.set_attribute("workflow.status", status)
                self.audit.emit(
                    self.request_id,
                    "stage_completed",
                    stage=name,
                    status=status,
                    duration_ms=elapsed,
                )
