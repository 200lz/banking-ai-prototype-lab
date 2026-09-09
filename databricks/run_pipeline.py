"""Local compatibility CLI for the shared synthetic Delta publisher.

Databricks wheel jobs use the installed package entry point, never this workspace file.
Run make setup first so the repository package is installed in the local environment.
"""

import argparse
import json
from pathlib import Path
from typing import Any

from packages.financial.publisher import identifier, publish_bytes


def publish(repo_root: Path, catalog: str, schema: str, spark: Any) -> dict[str, Any]:
    catalog, schema = identifier(catalog), identifier(schema)
    return publish_bytes(
        (repo_root / "data/synthetic/financial_raw.json").read_bytes(), catalog, schema, spark
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()
    catalog, schema = identifier(args.catalog), identifier(args.schema)
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    print(json.dumps(publish(args.repo_root, catalog, schema, spark), sort_keys=True))


if __name__ == "__main__":
    main()
