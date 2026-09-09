"""Read-only local or explicitly selected live Databricks integration evidence.

Does not deploy jobs or create tables. Credentials stay in the SDK provider.
"""

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from packages.financial.adapters import LocalFinancialAdapter, provider_from_environment
from packages.financial.models import FinancialProfileArgs
from services.agent.models import AgentRequest
from services.agent.workflow import Workflow


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("local", "databricks"), default="local")
    parser.add_argument("--company-id", default="SYN-SME-001")
    parser.add_argument("--output", type=Path, default=Path(".runtime/databricks-profile.json"))
    args = parser.parse_args()
    FinancialProfileArgs(company_id=args.company_id)
    if args.backend == "databricks":
        if os.environ.get("FINANCIAL_BACKEND") != "databricks":
            parser.error("Live verification requires FINANCIAL_BACKEND=databricks")
        provider = provider_from_environment()
    else:
        provider = LocalFinancialAdapter()
    result = Workflow(financial=provider).run(
        AgentRequest(question="Prepare an SME lending review", company_id=args.company_id)
    )
    profile = result.financial_profile
    passed = (
        profile is not None
        and profile.source == args.backend
        and result.human_review_required
        and bool(result.evidence)
        and all(item.verified for item in result.citations)
        and "financial_profile_unavailable" not in result.risk_flags
    )
    evidence = {
        "recorded_at": datetime.now(UTC).isoformat(),
        "status": "PASS" if passed else "FAIL",
        "adapter": args.backend,
        "planner": "local",
        "workspace_execution": "NOT TESTED" if args.backend == "local" else "Gold read only",
        "pipeline_job_execution": "NOT TESTED",
        "company_id": args.company_id,
        "profile": None if profile is None else profile.model_dump(mode="json"),
        "policy_document_ids": sorted({item.document_id for item in result.evidence}),
        "human_review_required": result.human_review_required,
        "risk_flags": result.risk_flags,
        "tool_names": [item.name for item in result.tool_invocations],
        "latency_ms": result.metrics.latency_ms,
        "input_tokens": result.metrics.input_tokens,
        "output_tokens": result.metrics.output_tokens,
        "estimated_llm_cost_usd": result.metrics.estimated_cost_usd,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"status": evidence["status"], "adapter": args.backend, "output": str(args.output)}
        )
    )
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
