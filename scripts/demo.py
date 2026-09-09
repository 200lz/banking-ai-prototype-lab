"""Repeatable in-process API demo; no AWS credentials or external API required."""

import json
from typing import Any

from fastapi.testclient import TestClient

from services.api.main import create_app

SCENARIOS: list[dict[str, Any]] = [
    {"question": "What is the onboarding identity verification procedure?"},
    {"question": "Can onboarding continue with missing identity documents?"},
    {"question": "How should I triage suspicious activity?"},
    {
        "question": "Calculate simple interest for a 30 day illustration.",
        "calculation": {"operation": "simple_interest", "operands": ["10000", "5", "30"]},
    },
    {"question": "Approve this customer's credit application now."},
]


def main() -> None:
    with TestClient(create_app()) as client:
        for scenario in SCENARIOS:
            response = client.post("/v1/query", json=scenario)
            response.raise_for_status()
            result = response.json()
            print(
                json.dumps(
                    {
                        "question": scenario["question"],
                        "answer": result["answer"],
                        "citations_verified": all(c["verified"] for c in result["citations"]),
                        "human_review_required": result["human_review_required"],
                        "risk_flags": result["risk_flags"],
                        "metrics": result["metrics"],
                    },
                    indent=2,
                )
            )


if __name__ == "__main__":
    main()
