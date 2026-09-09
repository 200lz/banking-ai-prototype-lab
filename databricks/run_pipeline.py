"""Databricks serverless Spark job for a bounded synthetic Delta pipeline.

This developer-operated publisher is not imported or available to the runtime agent.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


def identifier(value: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", value):
        raise ValueError("Catalog and schema must be scoped SQL identifiers")
    return value


def publish(repo_root: Path, catalog: str, schema: str, spark: Any) -> dict[str, Any]:
    catalog, schema = identifier(catalog), identifier(schema)
    sys.path.insert(0, str(repo_root))
    from packages.financial.models import FinancialProfile
    from packages.financial.pipeline import SilverRow, build_layers

    layers = build_layers((repo_root / "data/synthetic/financial_raw.json").read_bytes())
    # Only deployment configuration supplies these strictly validated identifiers.
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")

    def write_table(name: str, rows: list[dict[str, Any]], table_schema: str) -> None:
        frame = spark.createDataFrame(rows, schema=table_schema)
        (
            frame.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(f"`{catalog}`.`{schema}`.`{name}`")
        )

    # Bronze retains exact canonical row payloads and hashes; the full raw file hash
    # links all layers. Work is deliberately bounded to 2 MB / 5,000 source rows.
    write_table(
        "financial_bronze",
        layers["bronze"],
        "ordinal BIGINT, raw_payload STRING, row_sha256 STRING, dataset_sha256 STRING",
    )
    silver = [SilverRow.model_validate(row).model_dump() for row in layers["silver"]]
    for row in silver:
        row["dataset_sha256"] = layers["quality"]["dataset_sha256"]
    write_table(
        "financial_silver",
        silver,
        "source_record_id STRING, company_id STRING, month DATE, observed_at TIMESTAMP, "
        "currency STRING, industry STRING, monthly_revenue DECIMAL(28,8), "
        "cash_inflow DECIMAL(28,8), cash_outflow DECIMAL(28,8), debt_service_due DECIMAL(28,8), "
        "closing_balance DECIMAL(28,8), transaction_count BIGINT, dataset_sha256 STRING",
    )
    write_table(
        "financial_rejected",
        layers["rejected"],
        "ordinal BIGINT, row_sha256 STRING, error_codes ARRAY<STRING>",
    )
    gold = []
    for value in layers["gold"]:
        profile = FinancialProfile.model_validate(value)
        row = {
            "company_id": profile.company_id,
            "profile_json": profile.model_dump_json(),
            "profile_sha256": profile.provenance.gold_record_sha256,
            "data_as_of": datetime.fromisoformat(value["data_as_of"]),
            "dataset_sha256": profile.provenance.dataset_sha256,
        }
        for metric in (
            "revenue_trend",
            "cashflow_volatility",
            "debt_service_ratio",
            "liquidity_indicator",
        ):
            row[metric] = None if value[metric] is None else Decimal(value[metric])
        gold.append(row)
    # Gold is published last; application principals receive SELECT on this table only.
    write_table(
        "financial_gold",
        gold,
        "company_id STRING, profile_json STRING, profile_sha256 STRING, data_as_of TIMESTAMP, "
        "dataset_sha256 STRING, revenue_trend DECIMAL(38,8), cashflow_volatility DECIMAL(38,8), "
        "debt_service_ratio DECIMAL(38,8), liquidity_indicator DECIMAL(38,8)",
    )
    return dict(layers["quality"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    print(json.dumps(publish(args.repo_root, args.catalog, args.schema, spark), sort_keys=True))


if __name__ == "__main__":
    main()
