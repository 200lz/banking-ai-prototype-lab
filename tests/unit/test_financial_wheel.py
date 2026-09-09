"""Exercise the real built/installed wheel without repository or cloud access."""

import builtins
import hashlib
import importlib.util
import json
import subprocess
import sys
import zipfile
from email.parser import Parser
from pathlib import Path
from types import SimpleNamespace

import pydantic
import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from packages.financial import wheel_entrypoints
from packages.financial.publisher import publish_bytes

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "financial_wheel_builder", ROOT / "databricks/build_wheel.py"
)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


@pytest.fixture(scope="module")
def installed_wheel(tmp_path_factory):
    temporary = tmp_path_factory.mktemp("financial-wheel")
    artifact = BUILDER.build_wheel(ROOT, temporary / "dist")
    installed = temporary / "installed"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--no-index",
            "--no-cache-dir",
            "--disable-pip-version-check",
            "--target",
            str(installed),
            str(artifact),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return SimpleNamespace(artifact=artifact, installed=installed, outside=temporary)


def run_installed(wheel, body):
    # -I ignores cwd/PYTHONPATH and -S disables editable .pth hooks. Only the installed
    # wheel plus the existing dependency directory is admitted; no repo code is added.
    bootstrap = """
import sys
from pathlib import Path
installed, dependencies, repo = map(Path, sys.argv[1:4])
sys.argv = ["financial-wheel"]
sys.path.insert(0, str(installed))
sys.path.append(str(dependencies))
assert all(Path(p).resolve() != repo.resolve() for p in sys.path if p)
import importlib.abc
class DenyCloudAndSpark(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'boto3', 'botocore', 'strands', 'services', 'pyspark', 'databricks'}:
            raise RuntimeError('Forbidden import during wheel smoke: ' + fullname)
sys.meta_path.insert(0, DenyCloudAndSpark())
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            bootstrap + body,
            str(wheel.installed),
            str(Path(pydantic.__file__).parent.parent),
            str(ROOT),
        ],
        cwd=wheel.outside,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_wheel_contains_only_financial_sources_fixture_and_expected_metadata(installed_wheel):
    with zipfile.ZipFile(installed_wheel.artifact) as archive:
        names = archive.namelist()
        code_and_data = {name for name in names if ".dist-info/" not in name}
        assert code_and_data == {*BUILDER.SOURCE_FILES, BUILDER.FIXTURE_TARGET}
        for name in BUILDER.SOURCE_FILES:
            assert archive.read(name) == (ROOT / name).read_bytes()
        assert archive.read(BUILDER.FIXTURE_TARGET) == (ROOT / BUILDER.FIXTURE_SOURCE).read_bytes()
        metadata = Parser().parsestr(
            archive.read(next(n for n in names if n.endswith("/METADATA"))).decode()
        )
        assert metadata.get_all("Requires-Dist") == ["pydantic==2.13.5"]
        assert metadata["Requires-Python"] == ">=3.11"
        points = archive.read(next(n for n in names if n.endswith("/entry_points.txt"))).decode()
        assert "smoke = packages.financial.wheel_entrypoints:smoke" in points
        assert "publish = packages.financial.wheel_entrypoints:publish" in points


def test_actual_installed_smoke_reads_local_modules_without_repo_spark_or_cloud(installed_wheel):
    report = run_installed(
        installed_wheel,
        """
import importlib.metadata
distribution = importlib.metadata.distribution('banking_ai_financial')
entry = next(e for e in distribution.entry_points if e.name == 'smoke')
entry.load()()
""",
    )
    assert report["status"] == "PASS"
    assert report["source_boundary"] == "installed_wheel"
    assert report["workspace_source_reads_required"] is False
    assert report["spark_initialized"] is False and report["tables_written"] is False
    assert report["raw_rows"] == 20
    assert report["dataset_sha256"] == BUILDER.FIXTURE_SHA256
    assert set(report["module_sha256"]) == set(wheel_entrypoints.MODULES)
    assert str(ROOT) not in json.dumps(report)


def test_installed_packaged_pipeline_matches_all_committed_gold_and_quality(installed_wheel):
    layers = run_installed(
        installed_wheel,
        """
import json
from packages.financial.wheel_entrypoints import packaged_fixture
from packages.financial.pipeline import build_layers
print(json.dumps(build_layers(packaged_fixture())))
""",
    )
    assert layers["gold"] == json.loads((ROOT / "data/synthetic/financial_gold.json").read_text())
    assert len(layers["bronze"]) == 20 and len(layers["silver"]) == 18
    assert len(layers["rejected"]) == 1 and len(layers["gold"]) == 3
    assert layers["quality"] == {
        "input_rows": 20,
        "silver_rows": 18,
        "duplicate_rows": 1,
        "rejected_rows": 1,
        "gold_profiles": 3,
        "dataset_sha256": BUILDER.FIXTURE_SHA256,
    }


def test_actual_installed_publish_entrypoint_uses_packaged_input_and_shared_writer(installed_wheel):
    quality = run_installed(
        installed_wheel,
        """
import importlib.metadata
import types
saved = []
class Frame:
    @property
    def write(self): return self
    def format(self, value):
        assert value == 'delta'
        return self
    def mode(self, value):
        assert value == 'overwrite'
        return self
    def option(self, key, value): return self
    def saveAsTable(self, table): saved.append(table)
class Spark:
    def sql(self, statement):
        assert statement == 'CREATE SCHEMA IF NOT EXISTS `catalog`.`synthetic`'
    def createDataFrame(self, rows, schema):
        assert len(rows) in (20, 18, 1, 3)
        return Frame()
sys.modules['pyspark.sql'] = types.SimpleNamespace(
    SparkSession=types.SimpleNamespace(builder=types.SimpleNamespace(getOrCreate=lambda: Spark())))
sys.argv = ['publish', '--catalog', 'catalog', '--schema', 'synthetic']
distribution = importlib.metadata.distribution('banking_ai_financial')
next(e for e in distribution.entry_points if e.name == 'publish').load()()
assert len(saved) == 4 and saved[-1] == '`catalog`.`synthetic`.`financial_gold`'
""",
    )
    assert quality["input_rows"] == 20 and quality["gold_profiles"] == 3
    assert quality["dataset_sha256"] == BUILDER.FIXTURE_SHA256


@pytest.mark.parametrize("bad", ["/Workspace/Users/person/models.py", "/workspace/models.py"])
def test_smoke_refuses_workspace_file_origins(monkeypatch, bad):
    monkeypatch.setattr(
        wheel_entrypoints.importlib.metadata,
        "distribution",
        lambda _: SimpleNamespace(locate_file=lambda _: bad),
    )
    monkeypatch.setattr(
        wheel_entrypoints.importlib, "import_module", lambda _: SimpleNamespace(__file__=bad)
    )
    with pytest.raises(ValueError, match="outside Workspace"):
        wheel_entrypoints.installed_files()


def test_smoke_refuses_source_shadowing_installed_distribution(monkeypatch, tmp_path):
    monkeypatch.setattr(
        wheel_entrypoints.importlib.metadata,
        "distribution",
        lambda _: SimpleNamespace(locate_file=lambda _: tmp_path / "other.py"),
    )
    with pytest.raises(ValueError, match="installed wheel"):
        wheel_entrypoints.installed_files()


def test_packaged_fixture_integrity_fails_closed(monkeypatch, tmp_path):
    (tmp_path / "financial_raw.json").write_bytes(b"[]")
    monkeypatch.setattr(wheel_entrypoints.importlib.resources, "files", lambda _: tmp_path)
    with pytest.raises(ValueError, match="integrity"):
        wheel_entrypoints.packaged_fixture()


def test_build_rejects_changed_canonical_fixture_before_output(tmp_path):
    raw = tmp_path / BUILDER.FIXTURE_SOURCE
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"[]")
    with pytest.raises(ValueError, match="Canonical fixture"):
        BUILDER.build_wheel(tmp_path, tmp_path / "output")
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize(
    "args",
    [
        ["--catalog", "catalog; DROP TABLE", "--schema", "synthetic"],
        ["--catalog", "catalog", "--schema", "synthetic\n"],
    ],
)
def test_publish_validates_identifiers_before_spark_or_fixture(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["publish", *args])
    monkeypatch.setattr(
        wheel_entrypoints, "installed_files", lambda: pytest.fail("Source read before validation")
    )
    real_import = builtins.__import__

    def guarded(name, *pos, **kwargs):
        if name.startswith("pyspark"):
            pytest.fail("Spark imported before identifier validation")
        return real_import(name, *pos, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    with pytest.raises(ValueError, match="scoped SQL"):
        wheel_entrypoints.publish()


def test_shared_publisher_has_typed_exact_rows_and_gold_last():
    from datetime import date, datetime
    from decimal import Decimal

    written, statements = [], []

    class Frame:
        def __init__(self, rows, schema):
            self.rows, self.schema = rows, schema

        @property
        def write(self):
            return self

        def format(self, value):
            assert value == "delta"
            return self

        def mode(self, value):
            assert value == "overwrite"
            return self

        def option(self, key, value):
            assert (key, value) == ("overwriteSchema", "true")
            return self

        def saveAsTable(self, table):
            written.append((table, self.rows, self.schema))

    spark = SimpleNamespace(sql=statements.append, createDataFrame=Frame)
    quality = publish_bytes(
        (ROOT / BUILDER.FIXTURE_SOURCE).read_bytes(), "catalog", "synthetic", spark
    )
    assert statements == ["CREATE SCHEMA IF NOT EXISTS `catalog`.`synthetic`"]
    assert [table for table, _, _ in written] == [
        f"`catalog`.`synthetic`.`financial_{layer}`"
        for layer in ("bronze", "silver", "rejected", "gold")
    ]
    assert [len(rows) for _, rows, _ in written] == [20, 18, 1, 3]
    silver = written[1][1][0]
    assert isinstance(silver["monthly_revenue"], Decimal) and isinstance(silver["month"], date)
    assert isinstance(silver["observed_at"], datetime)
    gold = written[-1][1]
    assert gold[0]["revenue_trend"] == Decimal("20.00")
    assert gold[0]["cashflow_volatility"] == Decimal("44596.96")
    assert gold[0]["debt_service_ratio"] == Decimal("0.0860")
    assert gold[0]["liquidity_indicator"] == Decimal("1.9433")
    assert gold[1]["revenue_trend"] is None
    assert all(row["dataset_sha256"] == quality["dataset_sha256"] for row in gold)


def test_builder_pins_toolchain_and_is_network_independent():
    assert '"setuptools==84.0.0"' in BUILDER.PROJECT
    assert '"wheel==0.48.0"' in BUILDER.PROJECT
    assert (
        hashlib.sha256((ROOT / BUILDER.FIXTURE_SOURCE).read_bytes()).hexdigest()
        == BUILDER.FIXTURE_SHA256
    )


def test_lock_regeneration_retains_explicit_build_tools_without_runtime_expansion(
    tmp_path, monkeypatch
):
    spec = importlib.util.spec_from_file_location(
        "wheel_lock_generator", ROOT / "scripts/lock_dependencies.py"
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    (tmp_path / "pyproject.toml").write_bytes((ROOT / "pyproject.toml").read_bytes())
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    generator.lock()
    development = (tmp_path / "requirements.lock").read_text()
    assert "setuptools==84.0.0\n" in development and "wheel==0.48.0\n" in development

    def applicable_pins(path):
        pins = {}
        for line in path.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            requirement = Requirement(line)
            if requirement.marker is None or requirement.marker.evaluate():
                pins[canonicalize_name(requirement.name)] = str(requirement.specifier)
        return pins

    # The checked-in Windows lock includes a pywin32 marker; Linux regeneration
    # correctly omits that dependency. Compare only requirements active here.
    runtime = applicable_pins(tmp_path / "requirements-runtime.lock")
    assert runtime == applicable_pins(ROOT / "requirements-runtime.lock")
    assert not {"setuptools", "wheel"}.intersection(runtime)
