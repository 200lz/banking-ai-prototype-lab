"""Nine-stage deterministic safety controller surrounding a replaceable planner."""

import os
import re
from datetime import date
from time import perf_counter
from uuid import uuid4

from opentelemetry import trace

from packages.financial.adapters import FinancialProfileProvider
from packages.financial.models import FinancialProfile
from packages.policy.controls import is_injected, redact_pii
from packages.retrieval.local import LocalRetriever
from packages.retrieval.models import Document, Retriever
from services.agent.models import (
    AgentRequest,
    AgentResponse,
    CalculationResult,
    Evidence,
    Metrics,
    Plan,
)
from services.agent.observability import AuditLogger, Recorder
from services.agent.planner import BedrockPlanner, LocalPlanner, Planner
from services.agent.tools import ToolRegistry, safe_document


def excerpts(documents: list[Document]) -> list[Evidence]:
    items: list[Evidence] = []
    for document in documents:
        document_items = []
        for index, sentence in enumerate(re.split(r"(?<=[.!?])\s+", document.text)):
            if sentence.strip():
                document_items.append(
                    Evidence(
                        id=f"{document.id}#{index + 1}",
                        document_id=document.id,
                        claim=sentence,
                        quote=sentence,
                        source_hash=document.sha256,
                    )
                )
        # Keep whole source paragraphs. Truncation must not remove a later caveat.
        if len(items) + len(document_items) <= 12:
            items.extend(document_items)
    return items


def active_documents(documents: list[Document]) -> tuple[list[Document], bool]:
    current = [document for document in documents if document.effective_date <= date.today()]
    superseded = {old for document in current for old in document.supersedes}
    current = [document for document in current if document.id not in superseded]
    by_topic: dict[str, set[str]] = {}
    for document in current:
        if document.source_type == "synthetic":
            by_topic.setdefault(document.topic, set()).add(document.sha256)
    # Conservative conflict rule: no attempt to adjudicate two distinct active versions.
    return current, any(len(hashes) > 1 for hashes in by_topic.values())


class Workflow:
    def __init__(
        self,
        retriever: Retriever | None = None,
        planner: Planner | None = None,
        audit: AuditLogger | None = None,
        financial: FinancialProfileProvider | None = None,
    ) -> None:
        self.retriever = retriever if retriever is not None else LocalRetriever()
        self.planner = planner if planner is not None else LocalPlanner()
        self.audit = audit if audit is not None else AuditLogger()
        self.financial = financial

    @classmethod
    def from_environment(cls) -> "Workflow":
        backend = os.getenv("RETRIEVAL_BACKEND", "local")
        mode = os.getenv("AGENT_MODE", "local")
        if mode not in {"local", "bedrock"} or backend not in {"local", "s3"}:
            raise ValueError("Unknown backend or agent mode")
        retriever: Retriever
        if backend == "s3":
            from packages.retrieval.aws import S3Retriever

            retriever = S3Retriever(
                os.environ["CORPUS_BUCKET"], prefix=os.getenv("CORPUS_PREFIX", "corpus/")
            )
        else:
            retriever = LocalRetriever()
        return cls(
            retriever=retriever, planner=BedrockPlanner() if mode == "bedrock" else LocalPlanner()
        )

    def run(self, request: AgentRequest) -> AgentResponse:
        with trace.get_tracer("banking.governed-workflow").start_as_current_span(
            "banking.workflow", record_exception=False, set_status_on_exception=False
        ) as span:
            result = self._run(request)
            span.set_attribute("request.id", result.request_id)
            span.set_attribute("agent.mode", result.mode)
            span.set_attribute("agent.human_review_required", result.human_review_required)
            span.set_attribute("agent.risk_flags", result.risk_flags)
            for key, value in result.metrics.model_dump().items():
                span.set_attribute("agent.metrics." + key, value)
            return result

    def _run(self, request: AgentRequest) -> AgentResponse:
        started = perf_counter()
        request_id = str(uuid4())
        recorder = Recorder(request_id, self.audit)
        tools = ToolRegistry(
            self.retriever,
            self.audit,
            request_id,
            financial=self.financial,
            enable_financial=request.company_id is not None,
        )
        metrics = Metrics()
        risks: list[str] = []
        documents: list[Document] = []
        retrieved_ids: list[str] = []
        candidates: list[Evidence] = []
        selected: list[Evidence] = []
        calculation: CalculationResult | None = None
        financial_profile: FinancialProfile | None = None
        failure = False

        with recorder.stage("user_request"):
            redacted, pii_found = redact_pii(request.question)
            # Redaction placeholders can expand short identifiers; bound downstream input.
            clean_request = request.model_copy(update={"question": redacted[:4000]})
            if pii_found:
                risks.append("pii_redacted")

        with recorder.stage("intent_analysis"):
            intent = tools.invoke(
                "risk_classification",
                {
                    # Risk classification is deterministic and never logs arguments. Use
                    # full ingress text so redaction expansion cannot hide a trailing attack.
                    "question": request.question,
                    "has_calculation": request.calculation is not None,
                    "has_company_profile": request.company_id is not None,
                },
            )
            risks.extend(intent.risks)

        with recorder.stage("retrieval"):
            retrieval_started = perf_counter()
            query = (clean_request.question[:3000] + " " + " ".join(intent.topics)).strip()
            if intent.blocked:
                query = "ai assistant scope safety " + query
            try:
                hits = tools.invoke("policy_search", {"query": query, "top_k": 10})
                relevant = [
                    hit.document
                    for hit in hits
                    if hit.document.topic in intent.topics
                    or (intent.blocked and hit.document.topic == "ai_safety")
                ]
                retrieved_ids = list(
                    dict.fromkeys(
                        document.id for document in relevant if not redact_pii(document.id)[1]
                    )
                )
                for document in relevant:
                    if is_injected(
                        document.title + "\n" + document.text + "\n" + " ".join(document.tags)
                    ):
                        risks.append("prompt_injection_detected")
                        failure = True
                    elif not safe_document(document):
                        risks.append("unsafe_source")
                        failure = True
                    else:
                        documents.append(document)
                documents, conflict = active_documents(documents)
                if conflict:
                    risks.append("conflicting_evidence")
                    failure = True
                required_topics = set(intent.topics) - {"conflicts"}
                supported_topics = {
                    document.topic for document in documents if document.source_type == "synthetic"
                }
                if not supported_topics or (
                    required_topics - supported_topics and not intent.blocked
                ):
                    risks.append("insufficient_evidence")
                    failure = True
                candidates = excerpts(documents) if not failure else []
            except Exception:
                risks.append("retrieval_failure")
                failure = True
            metrics.retrieval_latency_ms = round((perf_counter() - retrieval_started) * 1000, 3)

        with recorder.stage("agent_planning"):
            if intent.blocked or failure:
                plan = Plan(
                    evidence_ids=[item.id for item in candidates],
                    abstain=True,
                    human_review_required=True,
                )
            else:
                planning_started = perf_counter()
                try:
                    plan, model_metrics = self.planner.plan(clean_request, candidates)
                    metrics.model_latency_ms = model_metrics.model_latency_ms
                    metrics.input_tokens = model_metrics.input_tokens
                    metrics.output_tokens = model_metrics.output_tokens
                    metrics.estimated_cost_usd = model_metrics.estimated_cost_usd
                    metrics.cost_estimate_complete = model_metrics.cost_estimate_complete
                    if not metrics.cost_estimate_complete:
                        risks.append("model_cost_unavailable")
                    known = {item.id for item in candidates}
                    if (
                        set(plan.evidence_ids) - known
                        or len(set(plan.evidence_ids)) != len(plan.evidence_ids)
                        or (plan.calculate and request.calculation is None)
                    ):
                        raise ValueError("Planner exceeded the evidence or calculation boundary")
                    if not plan.evidence_ids:
                        risks.append("insufficient_evidence")
                        plan.abstain = True
                    if not plan.abstain:
                        selected_ids = {
                            item.document_id for item in candidates if item.id in plan.evidence_ids
                        }
                        selected_topics = {
                            document.topic
                            for document in documents
                            if document.id in selected_ids and document.source_type == "synthetic"
                        }
                        if required_topics - selected_topics or (
                            request.calculation is not None and not plan.calculate
                        ):
                            raise ValueError(
                                "Planner omitted required policy or calculation coverage"
                            )
                except Exception:
                    metrics.model_latency_ms = (
                        round((perf_counter() - planning_started) * 1000, 3)
                        if self.planner.mode == "bedrock"
                        else 0
                    )
                    risks.append("planner_failure")
                    if self.planner.mode == "bedrock":
                        metrics.cost_estimate_complete = False
                        risks.append("model_cost_unavailable")
                    failure = True
                    plan = Plan(abstain=True, human_review_required=True)

        with recorder.stage("controlled_tool_execution"):
            selected_documents = {
                item.document_id for item in candidates if item.id in plan.evidence_ids
            }
            # Selecting any claim retains that source's caveats in the final answer.
            selected = [item for item in candidates if item.document_id in selected_documents]
            try:
                for document_id in dict.fromkeys(item.document_id for item in selected):
                    fetched = tools.invoke("document_retrieval", {"document_id": document_id})
                    if fetched is None or any(
                        item.source_hash != fetched.sha256
                        for item in selected
                        if item.document_id == document_id
                    ):
                        raise ValueError("Source changed during the request")
                if (
                    plan.calculate
                    and not intent.blocked
                    and not failure
                    and not plan.abstain
                    and request.calculation is not None
                ):
                    calculation = tools.invoke(
                        "deterministic_calculation", request.calculation.model_dump()
                    )
                if (
                    request.company_id is not None
                    and not intent.blocked
                    and not failure
                    and not plan.abstain
                ):
                    try:
                        financial_profile = tools.invoke(
                            "financial_profile_tool", {"company_id": request.company_id}
                        )
                        if financial_profile is None:
                            raise ValueError("No governed Gold profile for the company")
                        if financial_profile.stale:
                            risks.append("financial_data_stale")
                        if financial_profile.missing_fields:
                            risks.append("financial_data_incomplete")
                    except Exception:
                        risks.append("financial_profile_unavailable")
                        financial_profile = None
                        failure = True
            except Exception:
                risks.append("tool_failure")
                failure = True

        with recorder.stage("guardrail_validation"):
            # Source text never grants permission. Even a malicious model cannot waive this.
            if intent.blocked or failure:
                calculation = None
                financial_profile = None
            if failure:
                selected = []
            if any(not safe_document(document) for document in documents):
                selected = []
                calculation = None
                financial_profile = None
                risks.append("unsafe_source")
                failure = True

        with recorder.stage("citation_verification"):
            try:
                citations = tools.invoke(
                    "citation_verification", {"evidence": [item.model_dump() for item in selected]}
                )
                if any(not citation.verified for citation in citations):
                    raise ValueError("Citation verification failed")
            except Exception:
                risks.append("citation_verification_failed")
                failure = True
                selected, citations, calculation = [], [], None
                financial_profile = None

        with recorder.stage("human_approval_decision"):
            credit_calculation = (
                request.calculation is not None
                and request.calculation.operation == "debt_to_income"
            )
            review = (
                intent.human_review_required
                or plan.human_review_required
                or plan.abstain
                or failure
                or pii_found
                or credit_calculation
                or request.company_id is not None
            )
            missing = list(intent.missing_information)
            if "insufficient_evidence" in risks:
                missing.append(
                    "A relevant, permitted, current synthetic policy source is required."
                )
            if "conflicting_evidence" in risks:
                missing.append("A policy owner must resolve the conflicting active sources.")
            if "financial_profile_unavailable" in risks:
                missing.append("A validated governed Gold financial profile is required.")
            if "financial_data_stale" in risks:
                missing.append("Refresh the stale financial snapshot before a lending assessment.")
            if "financial_data_incomplete" in risks:
                missing.append(
                    "Resolve the financial data-quality and missing-field flags before a lending assessment."
                )
            # This is a routing decision only. There is no approval or execution endpoint.
            self.audit.emit(
                request_id,
                "review_decision",
                human_review_required=review,
                risk_flags=sorted(set(risks)),
            )

        with recorder.stage("final_response"):
            paragraphs = []
            if intent.blocked:
                paragraphs.append(
                    "This read-only synthetic prototype cannot perform the requested action or follow instructions that exceed its allowed operational scope."
                )
            elif failure or plan.abstain:
                paragraphs.append(
                    "I cannot provide a supported recommendation from the available evidence."
                )
            else:
                paragraphs.append(
                    "Synthetic operational guidance based on the following verified excerpts:"
                )
            if not failure:
                paragraphs.extend(f"{item.claim} [{item.id}]" for item in selected)
            if calculation is not None:
                paragraphs.append(
                    f"Deterministic {calculation.operation} result: {calculation.value} {calculation.unit}. Formula: {calculation.formula}. Inputs: {', '.join(calculation.operands)}. {calculation.rounding}."
                )
            if financial_profile is not None:
                profile = financial_profile
                paragraphs.append(
                    f"Quantitative Gold evidence for {profile.company_id}: revenue trend {profile.revenue_trend or 'unavailable'} percent; "
                    f"operating cash-flow volatility {profile.cashflow_volatility or 'unavailable'} JPY; "
                    f"scheduled debt-service share of inflow {profile.debt_service_ratio or 'unavailable'}; "
                    f"liquidity runway {profile.liquidity_indicator or 'unavailable'} months. "
                    f"Source: {profile.source}/{profile.provenance.source_table}; data as of {profile.data_as_of.isoformat()}; "
                    f"Gold SHA-256: {profile.provenance.gold_record_sha256}. These indicators do not establish credit eligibility."
                )
            if missing:
                paragraphs.append("Missing information: " + " ".join(missing))
            if review:
                paragraphs.append(
                    "Human review is required before any operational decision or action. This response grants no approval."
                )
            assumptions = [
                "All internal policies and scenarios are synthetic.",
                "Only public and internal corpus classifications are permitted.",
                "Confidence is a deterministic evidence-completeness heuristic, not a calibrated probability.",
            ]
            if any(document.source_type == "public" for document in documents):
                assumptions.append(
                    "Public references are dated educational context and cannot authorize internal operations."
                )
            if self.planner.mode == "local":
                assumptions.append(
                    "Local mode uses a deterministic extractive baseline without an LLM."
                )
            else:
                assumptions.append(
                    "Model cost is estimated from reported tokens and configured illustrative rates; it excludes AWS infrastructure."
                )
                if not metrics.cost_estimate_complete:
                    assumptions.append(
                        "Model usage is incomplete; reported cost is a lower bound and may omit billed tokens."
                    )
            if calculation is not None:
                assumptions.append(
                    "Operands are supplied by the user; same-period income and debt and consistent currency units are assumed."
                )
            if financial_profile is not None:
                assumptions.append(
                    "Financial indicators were computed deterministically over valid observed months; no financial rows or profile values were sent to the model."
                )
            answer = "\n\n".join(paragraphs)
            self.audit.emit(
                request_id,
                "response_completed",
                mode=self.planner.mode,
                input_tokens=metrics.input_tokens,
                output_tokens=metrics.output_tokens,
                estimated_cost_usd=metrics.estimated_cost_usd,
                cost_estimate_complete=metrics.cost_estimate_complete,
                document_ids=[item.document_id for item in selected],
                source_hashes=[item.source_hash for item in selected],
            )

        metrics.latency_ms = round((perf_counter() - started) * 1000, 3)
        return AgentResponse(
            request_id=request_id,
            answer=answer,
            evidence=selected,
            citations=citations,
            assumptions=assumptions,
            missing_information=missing,
            confidence=0.0
            if failure or intent.blocked or plan.abstain
            else (0.55 if missing else 0.85),
            risk_flags=sorted(set(risks)),
            human_review_required=review,
            mode=self.planner.mode,
            trace=recorder.steps,
            tool_invocations=tools.invocations,
            metrics=metrics,
            calculation=calculation,
            financial_profile=financial_profile,
            retrieved_document_ids=retrieved_ids,
        )
