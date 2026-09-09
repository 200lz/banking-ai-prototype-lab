"""Run from repository root: python -m infra.cdk.app (synth only)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from aws_cdk import App, Environment

# Also support `cd infra/cdk && cdk synth` using the colocated cdk.json.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from infra.cdk.stack import BankingAiStack, DeploymentConfig  # noqa: E402


def main() -> None:
    app = App(outdir=os.environ.get("CDK_OUTDIR", str(Path(__file__).parent / "cdk.out")))
    context = {
        field: app.node.try_get_context(field)
        for field in DeploymentConfig.__dataclass_fields__
        if app.node.try_get_context(field) is not None
    }
    if "monthly_budget_usd" in context:
        context["monthly_budget_usd"] = int(context["monthly_budget_usd"])
    BankingAiStack(
        app,
        "BankingAiPrototypeLab",
        config=DeploymentConfig(**context),
        env=Environment(
            account=os.environ.get("CDK_DEFAULT_ACCOUNT", "111111111111"),
            region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
        ),
        description="Synthetic-only governed banking AI portfolio; no bank affiliation",
    )
    app.synth()


if __name__ == "__main__":
    main()
