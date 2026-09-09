"""Guard the serverless wheel migration against workspace-source and retry regressions.

These tests inspect the deployment contract only. They do not establish workspace
execution or authenticate to Databricks. The deployer must separately validate the
required wheel_path value and compare the uploaded/downloaded artifact hashes.
"""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def bundle():
    return yaml.safe_load((ROOT / "databricks/databricks.yml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def job(bundle):
    return bundle["resources"]["jobs"]["financial_pipeline"]


def nested_items(value):
    """Include nested keys and strings so compute/source overrides cannot hide below tasks."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from nested_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_items(child)
    elif isinstance(value, str):
        yield value


def test_bundle_defines_one_unscheduled_development_pipeline(bundle, job):
    assert set(bundle["resources"]) == {"jobs"}
    assert set(bundle["resources"]["jobs"]) == {"financial_pipeline"}
    assert set(bundle["targets"]) == {"dev"}
    # Prevent a target-level resource override from silently undoing task controls.
    assert bundle["targets"]["dev"] == {"default": True, "mode": "development"}
    assert not {"schedule", "trigger", "triggers", "continuous"}.intersection(job)
    assert "max_concurrent_runs" not in bundle.get("presets", {})


def test_runtime_invokes_only_installed_financial_wheel(job):
    assert len(job["tasks"]) == 1
    task = job["tasks"][0]
    assert task["task_key"] == "publish_gold"
    assert {key for key in task if key.endswith("_task")} == {"python_wheel_task"}
    wheel = task["python_wheel_task"]
    assert wheel["package_name"] == "banking_ai_financial"
    assert wheel["entry_point"] == "publish"
    assert set(wheel) == {"package_name", "entry_point", "parameters"}
    # Synced inspection files are outside this runtime configuration subtree.
    runtime_strings = list(nested_items(job))
    for forbidden in ("/Workspace", "${workspace.", "run_pipeline.py", "--repo-root"):
        assert all(forbidden not in value for value in runtime_strings)


def test_wheel_receives_only_reviewed_catalog_and_schema_parameters(bundle, job):
    parameters = job["tasks"][0]["python_wheel_task"]["parameters"]
    assert parameters == ["--catalog", "${var.catalog}", "--schema", "${var.schema}"]
    assert "default" not in bundle["variables"]["catalog"]
    assert bundle["variables"]["schema"]["default"] == "banking_ai_synthetic"
    assert not job.get("parameters")


def test_required_uploaded_wheel_is_a_serverless_environment_dependency(bundle, job):
    variable = bundle["variables"]["wheel_path"]
    assert "default" not in variable
    assert "lookup" not in variable
    assert variable.get("type", "string") == "string"
    environments = job["environments"]
    assert len(environments) == 1
    environment = environments[0]
    assert environment["environment_key"] == job["tasks"][0]["environment_key"] == "financial"
    assert set(environment["spec"]) == {"environment_version", "dependencies"}
    assert environment["spec"]["environment_version"] == "2"
    dependencies = environment["spec"]["dependencies"]
    assert len(dependencies) == 2
    assert set(dependencies) == {"pydantic==2.13.5", "${var.wheel_path}"}
    # No implicit repo-relative wheel or task-level cluster library installation.
    assert "libraries" not in job["tasks"][0]


def test_pipeline_preserves_concurrency_timeout_and_at_most_once_task_controls(job):
    assert type(job["max_concurrent_runs"]) is int and job["max_concurrent_runs"] == 1
    assert type(job["timeout_seconds"]) is int and job["timeout_seconds"] == 900
    task = job["tasks"][0]
    assert type(task["max_retries"]) is int and task["max_retries"] == 0
    assert task["retry_on_timeout"] is False
    # Serverless auto-optimization otherwise permits retries beyond max_retries.
    assert task["disable_auto_optimization"] is True
    if "timeout_seconds" in task:
        assert type(task["timeout_seconds"]) is int
        assert 0 < task["timeout_seconds"] <= job["timeout_seconds"]


def test_pipeline_has_no_alternate_compute_or_source_execution_configuration(job):
    forbidden = {
        "job_clusters",
        "existing_cluster_id",
        "new_cluster",
        "job_cluster_key",
        "compute",
        "ai_runtime_task",
        "spark_python_task",
        "spark_submit_task",
        "notebook_task",
        "run_job_task",
        "sql_task",
        "init_scripts",
        "spark_conf",
        "git_source",
        "libraries",
    }
    assert not forbidden.intersection(nested_items(job))
