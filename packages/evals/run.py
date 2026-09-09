"""Run the versioned synthetic set and emit reviewable per-case artifacts."""

import argparse
import hashlib
import json
import math
import platform
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from packages.evals.scoring import score_case
from packages.retrieval.local import ROOT, LocalRetriever
from packages.retrieval.models import Document
from services.agent.models import AgentRequest
from services.agent.observability import AuditLogger
from services.agent.planner import BedrockPlanner
from services.agent.workflow import Workflow

GATES = {
    "cost_measurement_complete": 1.0,
    "answer_correctness": 0.95,
    "retrieval_recall": 0.95,
    "citation_correctness": 1.0,
    "groundedness": 1.0,
    "policy_compliance": 1.0,
    "correct_tool_selection": 1.0,
    "correct_escalation": 1.0,
}


def case_passes(scores: dict[str, Any]) -> bool:
    return (
        set(GATES) <= scores.keys()
        and "hallucination_rate" in scores
        and all(scores.get(name) is None or scores[name] >= gate for name, gate in GATES.items())
        and scores.get("hallucination_rate") in (0, None)
    )


def load_cases(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or ROOT / "evals/cases.jsonl"
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def corpus_for(case: dict[str, Any]) -> list[Document]:
    docs = [] if case.get("corpus_mode") == "replace" else list(LocalRetriever().documents)
    return docs + [Document.model_validate(d) for d in case.get("documents", [])]


def evaluate(
    *,
    smoke: bool = False,
    mode: str = "local",
    output: Path | None = None,
    case_ids: list[str] | None = None,
    stop_on_failure: bool = False,
) -> dict[str, Any]:
    if mode not in {"local", "bedrock"}:
        raise ValueError("Unknown evaluation mode")
    cases = load_cases()
    if case_ids is not None:
        indexed = {case["id"]: case for case in cases}
        if not case_ids or len(case_ids) != len(set(case_ids)) or set(case_ids) - indexed.keys():
            raise ValueError("Evaluation subset must contain distinct existing case IDs")
        cases = [indexed[case_id] for case_id in case_ids]
    if smoke:
        # One case from each category, preserving all distinct attack fixtures.
        seen: set[str] = set()
        subset = []
        for case in cases:
            if case["category"] not in seen or case.get("corpus_mode"):
                subset.append(case)
                seen.add(case["category"])
        cases = subset
    if not cases:
        raise ValueError("Evaluation requires at least one case")
    requested_case_count = len(cases)
    rows = []
    for case in cases:
        documents = corpus_for(case)
        request = AgentRequest(question=case["question"], calculation=case.get("calculation"))
        workflow = Workflow(
            retriever=LocalRetriever(documents),
            planner=BedrockPlanner() if mode == "bedrock" else None,
            audit=AuditLogger(ROOT / ".runtime/eval-audit.jsonl"),
        )
        response = workflow.run(request).model_dump(mode="json")
        rows.append(
            {
                "id": case["id"],
                "category": case["category"],
                "scores": score_case(case, response, documents),
                "response": response,
            }
        )
        if stop_on_failure and not case_passes(rows[-1]["scores"]):
            break
    aggregate: dict[str, Any] = {}
    denominators = {}
    for name in rows[0]["scores"]:
        values = [r["scores"][name] for r in rows if r["scores"][name] is not None]
        aggregate[name] = statistics.mean(values) if values else None
        denominators[name] = len(values)
    latencies = sorted(r["scores"]["latency_ms"] for r in rows)
    aggregate["latency_p50_ms"] = statistics.median(latencies)
    aggregate["latency_p95_ms"] = latencies[math.ceil(0.95 * len(latencies)) - 1]
    aggregate["total_estimated_llm_cost_usd"] = sum(
        r["scores"]["estimated_llm_cost_usd"] for r in rows
    )
    failures = {
        name: {"observed": aggregate[name], "minimum": gate}
        for name, gate in GATES.items()
        if aggregate[name] is None or aggregate[name] < gate
    }
    if aggregate["hallucination_rate"] not in {0, None}:
        failures["hallucination_rate"] = {"observed": aggregate["hallucination_rate"], "maximum": 0}
    if stop_on_failure and any(not case_passes(row["scores"]) for row in rows):
        failures["individual_case_failure"] = {"observed": 1, "maximum": 0}
    dataset = ROOT / "evals/cases.jsonl"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "measurement_scope": "Deterministic local baseline; no LLM calls"
        if mode == "local"
        else "Live Bedrock planner with governed extractive responses",
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "case_count": len(rows),
        "requested_case_count": requested_case_count,
        "stopped_early": len(rows) < requested_case_count,
        "smoke": smoke,
        "aggregate": aggregate,
        "metric_denominators": denominators,
        "gates": GATES,
        "gate_failures": failures,
        "passed": not failures,
        "cases": rows,
    }
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--mode", choices=["local", "bedrock"], default="local")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is None:
        filename = (
            f"bedrock-{datetime.now(UTC).date()}-direct.json"
            if args.mode == "bedrock"
            else ("smoke.json" if args.smoke else "latest.json")
        )
        args.output = ROOT / "evals/results" / filename
    result = evaluate(smoke=args.smoke, mode=args.mode, output=args.output)
    print(
        json.dumps(
            {
                key: result[key]
                for key in ["case_count", "mode", "aggregate", "gate_failures", "passed"]
            },
            indent=2,
        )
    )
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
