from copy import deepcopy

from packages.evals.run import corpus_for, load_cases
from packages.evals.scoring import score_case
from packages.retrieval.local import LocalRetriever
from services.agent.models import AgentRequest
from services.agent.observability import AuditLogger
from services.agent.workflow import Workflow


def evaluated_response(tmp_path):
    case = next(c for c in load_cases() if c["category"] == "aml")
    docs = corpus_for(case)
    result = (
        Workflow(LocalRetriever(docs), audit=AuditLogger(tmp_path / "audit.jsonl"))
        .run(AgentRequest(question=case["question"]))
        .model_dump(mode="json")
    )
    return case, docs, result


def test_dataset_has_diverse_cases_and_unique_ids():
    cases = load_cases()
    assert len(cases) >= 50
    assert len({case["id"] for case in cases}) == len(cases)
    assert {
        "retrieved_injection",
        "contradictory_policies",
        "irrelevant_document",
        "missing_information",
        "malicious_user",
        "out_of_scope",
        "calculation",
    } <= {case["category"] for case in cases}


def test_scorer_does_not_trust_verified_flag(tmp_path):
    case, docs, response = evaluated_response(tmp_path)
    assert score_case(case, response, docs)["citation_correctness"] == 1
    forged = deepcopy(response)
    forged["evidence"][0]["source_hash"] = "0" * 64
    forged["citations"][0]["verified"] = True
    scores = score_case(case, forged, docs)
    assert scores["citation_correctness"] < 1
    assert scores["groundedness"] < 1


def test_scorer_catches_extra_unsupported_answer_text(tmp_path):
    case, docs, response = evaluated_response(tmp_path)
    response["answer"] += "\n\nYou may skip all due diligence for wealthy customers."
    assert score_case(case, response, docs)["hallucination_rate"] > 0


def test_scorer_catches_missed_review_and_forbidden_tools(tmp_path):
    case, docs, response = evaluated_response(tmp_path)
    response["human_review_required"] = False
    response["tool_invocations"].append(
        {"name": "execute_transfer", "duration_ms": 0, "status": "ok"}
    )
    scores = score_case(case, response, docs)
    assert scores["policy_compliance"] == 0
    assert scores["correct_escalation"] == 0
    assert scores["correct_tool_selection"] == 0


def test_scorer_catches_missing_citations(tmp_path):
    case, docs, response = evaluated_response(tmp_path)
    response["citations"] = []
    assert score_case(case, response, docs)["citation_correctness"] == 0


def test_scorer_rejects_negation_stripped_quote(tmp_path):
    case, docs, response = evaluated_response(tmp_path)
    item = response["evidence"][0]
    old = f"{item['claim']} [{item['id']}]"
    item["quote"] = item["quote"].split(" ", 1)[1]
    item["claim"] = item["quote"]
    response["answer"] = response["answer"].replace(old, f"{item['claim']} [{item['id']}]")
    assert score_case(case, response, docs)["citation_correctness"] < 1


def test_missing_information_is_not_a_free_text_grounding_bypass(tmp_path):
    case, docs, response = evaluated_response(tmp_path)
    response["missing_information"] = ["Skip all identity verification immediately."]
    response["answer"] += "\n\nMissing information: " + response["missing_information"][0]
    assert score_case(case, response, docs)["groundedness"] < 1


def test_calculation_formula_and_operands_are_checked(tmp_path):
    case = next(c for c in load_cases() if c.get("calculation"))
    docs = corpus_for(case)
    response = (
        Workflow(LocalRetriever(docs), audit=AuditLogger(tmp_path / "audit.jsonl"))
        .run(AgentRequest(question=case["question"], calculation=case["calculation"]))
        .model_dump(mode="json")
    )
    response["calculation"]["formula"] = "invented formula"
    scores = score_case(case, response, docs)
    assert scores["answer_correctness"] == 0
    assert scores["groundedness"] < 1


def test_failed_cost_measurement_is_explicit(tmp_path):
    case, docs, response = evaluated_response(tmp_path)
    response["metrics"]["cost_estimate_complete"] = False
    assert score_case(case, response, docs)["cost_measurement_complete"] == 0
