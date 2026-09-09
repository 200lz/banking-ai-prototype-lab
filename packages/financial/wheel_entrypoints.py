"""Installed-wheel diagnostics and publication; no workspace source or agent tools."""

import argparse
import hashlib
import importlib
import importlib.metadata
import importlib.resources
import json
from pathlib import Path
from typing import Any

from packages.financial.publisher import identifier, publish_bytes

DISTRIBUTION = "banking_ai_financial"
FIXTURE_SHA256 = "3514bdb316c518976a13b06d5820885db73f76bb0b250c3e20c9b516c41fbe2a"
MODULES = ("models", "pipeline", "publisher", "wheel_entrypoints")


def installed_files() -> dict[str, str]:
    """Require modules from this installed distribution, never the Workspace Files mount."""
    distribution = importlib.metadata.distribution(DISTRIBUTION)
    hashes = {}
    for name in MODULES:
        module = importlib.import_module("packages.financial." + name)
        if module.__file__ is None:
            raise ValueError("Financial wheel module has no installed file")
        path = Path(module.__file__).resolve()
        expected = Path(str(distribution.locate_file(f"packages/financial/{name}.py"))).resolve()
        if "workspace" in {part.casefold() for part in path.parts} or path != expected:
            raise ValueError(
                "Financial modules must come from the installed wheel outside Workspace"
            )
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def packaged_fixture() -> bytes:
    raw = (
        importlib.resources.files("packages.financial").joinpath("financial_raw.json").read_bytes()
    )
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise ValueError("Packaged synthetic fixture integrity mismatch")
    values = json.loads(raw)
    if not isinstance(values, list) or len(values) != 20:
        raise ValueError("Packaged synthetic fixture must contain exactly 20 rows")
    return raw


def smoke_report() -> dict[str, Any]:
    """Only imports and installed-file reads: no Spark session, SQL, or publication."""
    module_hashes = installed_files()
    raw = packaged_fixture()
    return {
        "status": "PASS",
        "distribution": DISTRIBUTION,
        "version": importlib.metadata.version(DISTRIBUTION),
        "source_boundary": "installed_wheel",
        "workspace_source_reads_required": False,
        "module_sha256": module_hashes,
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_rows": len(json.loads(raw)),
        "spark_initialized": False,
        "tables_written": False,
    }


def smoke() -> None:
    parser = argparse.ArgumentParser(description="Read installed financial wheel and fixture only")
    parser.parse_args()
    print(json.dumps(smoke_report(), sort_keys=True))


def publish() -> None:
    parser = argparse.ArgumentParser(
        description="Publish only the packaged synthetic financial data"
    )
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()
    # Validate operator configuration before creating a Spark session or reading data.
    catalog, schema = identifier(args.catalog), identifier(args.schema)
    installed_files()
    raw = packaged_fixture()
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    print(json.dumps(publish_bytes(raw, catalog, schema, spark), sort_keys=True))
