"""Build a minimal financial wheel offline from canonical allowlisted repository files.

Use the dev lock's pinned setuptools/wheel. The stage is temporary, so copied sources
and fixture bytes are build inputs, not a second maintained business implementation.
No repository package discovery, network dependency resolution, or cloud action occurs.
"""

import argparse
import hashlib
import json
import os

# Fixed developer-only offline build command, never a runtime agent tool.
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "packages/__init__.py",
    "packages/financial/__init__.py",
    "packages/financial/models.py",
    "packages/financial/pipeline.py",
    "packages/financial/publisher.py",
    "packages/financial/wheel_entrypoints.py",
)
FIXTURE_SOURCE = "data/synthetic/financial_raw.json"
FIXTURE_TARGET = "packages/financial/financial_raw.json"
FIXTURE_SHA256 = "3514bdb316c518976a13b06d5820885db73f76bb0b250c3e20c9b516c41fbe2a"
PROJECT = """[build-system]
requires = ["setuptools==84.0.0", "wheel==0.48.0"]
build-backend = "setuptools.build_meta"

[project]
name = "banking_ai_financial"
version = "0.1.0"
description = "Synthetic financial publisher and installed-wheel source-delivery diagnostic"
requires-python = ">=3.11"
dependencies = ["pydantic==2.13.5"]

[project.scripts]
smoke = "packages.financial.wheel_entrypoints:smoke"
publish = "packages.financial.wheel_entrypoints:publish"

[tool.setuptools]
packages = ["packages", "packages.financial"]
include-package-data = false

[tool.setuptools.package-data]
"packages.financial" = ["financial_raw.json"]
"""


def build_wheel(repo_root: Path, output_dir: Path) -> Path:
    raw = (repo_root / FIXTURE_SOURCE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise ValueError("Canonical fixture changed; review expected source before building")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    # TemporaryDirectory owns only its newly created path; no existing tree is deleted.
    with tempfile.TemporaryDirectory(prefix="banking-financial-wheel-") as temporary:
        stage = Path(temporary)
        for relative in SOURCE_FILES:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((repo_root / relative).read_bytes())
        (stage / FIXTURE_TARGET).write_bytes(raw)
        (stage / "pyproject.toml").write_text(PROJECT, encoding="utf-8", newline="\n")
        environment = dict(
            os.environ, SOURCE_DATE_EPOCH="946684800", PIP_DISABLE_PIP_VERSION_CHECK="1"
        )
        # Allowlisted inputs and fixed pip arguments; shell=False.
        subprocess.run(  # nosec B603
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--no-build-isolation",
                "--no-index",
                "--no-cache-dir",
                "--wheel-dir",
                str(output_dir),
                str(stage),
            ],
            cwd=stage,
            env=environment,
            check=True,
            stdout=sys.stderr,
        )
    artifact = output_dir / "banking_ai_financial-0.1.0-py3-none-any.whl"
    if not artifact.is_file():
        raise RuntimeError("Expected financial wheel was not built")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".runtime/financial-wheel/dist")
    args = parser.parse_args()
    artifact = build_wheel(ROOT, args.output_dir)
    payload = artifact.read_bytes()
    print(
        json.dumps(
            {
                "wheel": str(artifact),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "dataset_sha256": FIXTURE_SHA256,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
