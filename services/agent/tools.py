"""Five baseline capabilities plus a bounded optional synthetic Gold-profile read."""

import os
import re
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal, localcontext
from time import perf_counter
from typing import Any, Literal
from urllib.parse import unquote

from opentelemetry import trace
from pydantic import BaseModel, Field

from packages.financial.adapters import FinancialProfileProvider, provider_from_environment
from packages.financial.models import FinancialProfileArgs, verify_profile
from packages.policy.controls import analyze_intent, is_injected, redact_pii
from packages.retrieval.models import Document, Retriever
from services.agent.models import (
    Calculation,
    CalculationResult,
    Citation,
    Evidence,
    StrictModel,
    ToolInvocation,
)
from services.agent.observability import AuditLogger


class SearchArgs(StrictModel):
    query: str = Field(min_length=1, max_length=4000, strict=True)
    top_k: int = Field(default=5, ge=1, le=10, strict=True)


class DocumentArgs(StrictModel):
    document_id: str = Field(
        min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.-]+$", strict=True
    )


class RiskArgs(StrictModel):
    question: str = Field(min_length=1, max_length=4000, strict=True)
    has_calculation: bool = Field(default=False, strict=True)
    has_company_profile: bool = Field(default=False, strict=True)


class CitationArgs(StrictModel):
    evidence: list[Evidence] = Field(max_length=12)


ToolName = Literal[
    "policy_search",
    "document_retrieval",
    "deterministic_calculation",
    "risk_classification",
    "citation_verification",
    "financial_profile_tool",
]


def calculate(calculation: Calculation) -> CalculationResult:
    values = calculation.operands
    with localcontext() as context:
        context.prec = 40
        if calculation.operation == "debt_to_income":
            value = values[0] / values[1] * Decimal(100)
            unit, formula = "percent", "periodic debt / income for the same period * 100"
        elif calculation.operation == "simple_interest":
            value = values[0] * values[1] / Decimal(100) * values[2] / Decimal(365)
            unit, formula = "currency units", "principal * annual_rate_percent / 100 * days / 365"
        else:
            value = sum(values, Decimal(0))
            unit, formula = "numeric units", "sum(operands)"
        result = format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")
    return CalculationResult(
        operation=calculation.operation,
        operands=[str(v) for v in values],
        value=result,
        unit=unit,
        formula=formula,
    )


def safe_document(document: Document) -> bool:
    # Provenance metadata is untrusted too: versions, URLs, IDs, and tags can leak PII.
    content = unquote(document.model_dump_json())
    return (
        document.classification in {"internal", "public"}
        and not is_injected(content)
        and not redact_pii(content)[1]
    )


class ToolRegistry:
    schemas: dict[str, type[BaseModel]] = {
        "policy_search": SearchArgs,
        "document_retrieval": DocumentArgs,
        "deterministic_calculation": Calculation,
        "risk_classification": RiskArgs,
        "citation_verification": CitationArgs,
    }

    def __init__(
        self,
        retriever: Retriever,
        audit: AuditLogger,
        request_id: str,
        *,
        financial: FinancialProfileProvider | None = None,
        enable_financial: bool = False,
    ) -> None:
        self.retriever = retriever
        self.audit = audit
        self.request_id = request_id
        self.invocations: list[ToolInvocation] = []
        self.schemas = dict(type(self).schemas)
        self.financial = financial
        if enable_financial:
            self.schemas["financial_profile_tool"] = FinancialProfileArgs

    def invoke(self, name: str, arguments: dict[str, Any]) -> Any:
        started = perf_counter()
        status = "ok"
        with trace.get_tracer("banking.tools").start_as_current_span(
            "tool." + (name if name in self.schemas else "denied"),
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            try:
                if name not in self.schemas:
                    raise ValueError("Tool is not allowlisted")
                args = self.schemas[name].model_validate(arguments)
                if isinstance(args, SearchArgs):
                    return self.retriever.search(
                        args.query, top_k=args.top_k, max_classification="internal"
                    )
                if isinstance(args, DocumentArgs):
                    document = self.retriever.get(args.document_id, max_classification="internal")
                    return document if document and safe_document(document) else None
                if isinstance(args, Calculation):
                    return calculate(args)
                if isinstance(args, RiskArgs):
                    return analyze_intent(
                        args.question, args.has_calculation, args.has_company_profile
                    )
                if isinstance(args, CitationArgs):
                    return self.verify_citations(args.evidence)
                if isinstance(args, FinancialProfileArgs):
                    provider = (
                        self.financial
                        if self.financial is not None
                        else provider_from_environment()
                    )
                    profile = provider.get_profile(args.company_id)
                    if profile is None:
                        return None
                    return verify_profile(
                        profile,
                        args.company_id,
                        now=datetime.now(UTC),
                        max_age_days=int(os.environ.get("FINANCIAL_MAX_AGE_DAYS", "45")),
                        source=profile.source,
                    )
                raise ValueError("Tool dispatch failed")
            except Exception:
                status = "error"
                raise
            finally:
                elapsed = round((perf_counter() - started) * 1000, 3)
                safe_name = name if name in self.schemas else "denied"
                self.invocations.append(
                    ToolInvocation(name=safe_name, duration_ms=elapsed, status=status)
                )
                span.set_attribute("tool.name", safe_name)
                span.set_attribute("tool.status", status)
                self.audit.emit(
                    self.request_id,
                    "tool_invoked",
                    tool=safe_name,
                    status=status,
                    duration_ms=elapsed,
                )

    def verify_citations(self, evidence: list[Evidence]) -> list[Citation]:
        citations = []
        for item in evidence:
            document = self.retriever.get(item.document_id, max_classification="internal")
            verified = bool(
                document
                and safe_document(document)
                and item.source_hash == document.sha256
                and item.claim == item.quote
                and item.quote.strip()
                and (
                    item.quote == document.text
                    or item.quote in re.split(r"(?<=[.!?])\s+", document.text)
                )
            )
            citations.append(
                Citation(
                    evidence_id=item.id,
                    document_id=item.document_id,
                    title=document.title if document else "Unavailable source",
                    source_url=document.source_url if document else None,
                    version=document.version if document else "unknown",
                    verified=verified,
                )
            )
        return citations
