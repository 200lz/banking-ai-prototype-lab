"""Developer deployment safeguards: no AWS calls or writes are used by these tests."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from scripts import publish_corpus, tasks
from scripts.build_corpus import build


@pytest.mark.parametrize(
    ("account", "region"),
    [
        ("", "us-east-1"),
        ("111111111111", "us-east-1"),
        ("12345", "us-east-1"),
        ("123456789012", ""),
        ("123456789012", "not-a-region"),
    ],
)
def test_deploy_rejects_invalid_target_before_any_command(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, account: str, region: str
) -> None:
    interpreter = tmp_path / "python"
    interpreter.touch()
    monkeypatch.setattr(tasks, "VENV_PYTHON", interpreter)
    monkeypatch.setenv("CDK_DEFAULT_ACCOUNT", account)
    monkeypatch.setenv("CDK_DEFAULT_REGION", region)
    monkeypatch.setattr(sys, "argv", ["tasks.py", "deploy"])
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(tasks, "run", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(SystemExit) as error:
        tasks.main()
    assert error.value.code == 2
    assert not calls


def test_deploy_keeps_diff_before_iam_approval_and_publish_last(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    interpreter = tmp_path / "python"
    interpreter.touch()
    cli = tmp_path / "infra/cdk/node_modules/aws-cdk/bin/cdk"
    cli.parent.mkdir(parents=True)
    cli.touch()
    monkeypatch.setattr(tasks, "ROOT", tmp_path)
    monkeypatch.setattr(tasks, "VENV_PYTHON", interpreter)
    monkeypatch.setenv("CDK_DEFAULT_ACCOUNT", "123456789012")
    monkeypatch.setenv("CDK_DEFAULT_REGION", "us-east-1")
    monkeypatch.setattr(sys, "argv", ["tasks.py", "deploy"])
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(tasks, "run", lambda *args, **kwargs: calls.append(args))
    tasks.main()
    assert calls[0][-1] == "scripts/build_corpus.py"
    assert calls[1][-1] == "diff"
    assert "deploy" in calls[2]
    assert calls[2][calls[2].index("--require-approval") + 1] == "broadening"
    assert calls[3][-1] == "scripts/publish_corpus.py"


def test_deploy_requires_pinned_cli_before_building_corpus(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    interpreter = tmp_path / "python"
    interpreter.touch()
    monkeypatch.setattr(tasks, "ROOT", tmp_path)
    monkeypatch.setattr(tasks, "VENV_PYTHON", interpreter)
    monkeypatch.setenv("CDK_DEFAULT_ACCOUNT", "123456789012")
    monkeypatch.setenv("CDK_DEFAULT_REGION", "us-east-1")
    monkeypatch.setattr(sys, "argv", ["tasks.py", "deploy"])
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(tasks, "run", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(SystemExit):
        tasks.main()
    assert not calls


def setup_corpus(tmp_path: Path) -> Path:
    directory = tmp_path / ".runtime/corpus"
    build(directory)
    (tmp_path / ".runtime/cloud-outputs.json").write_text(
        json.dumps({"BankingAiPrototypeLab": {"CorpusBucket": "synthetic-corpus-example"}}),
        encoding="utf-8",
    )
    return directory


def test_publisher_preflights_all_documents_before_creating_aws_client(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    directory = setup_corpus(tmp_path)
    manifest = json.loads((directory / "manifest.json").read_text())
    last = directory / manifest["documents"][-1]["key"].removeprefix("corpus/")
    last.write_bytes(last.read_bytes() + b" changed")
    monkeypatch.chdir(tmp_path)
    clients: list[str] = []
    monkeypatch.setattr(publish_corpus.boto3, "client", lambda name: clients.append(name))
    with pytest.raises(ValueError, match="integrity"):
        publish_corpus.main()
    assert not clients


def test_publisher_uploads_verified_manifest_last(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    setup_corpus(tmp_path)
    monkeypatch.chdir(tmp_path)
    uploaded: list[str] = []

    class FakeS3:
        def upload_file(self, source: str, bucket: str, key: str, **kwargs: Any) -> None:
            assert Path(source).is_file()
            assert bucket == "synthetic-corpus-example"
            assert kwargs["ExtraArgs"]["ServerSideEncryption"] == "AES256"
            uploaded.append(key)

    monkeypatch.setattr(publish_corpus.boto3, "client", lambda name: FakeS3())
    publish_corpus.main()
    assert len(uploaded) > 2
    assert uploaded[-1] == "corpus/manifest.json"
    assert len(uploaded) == len(set(uploaded))


@pytest.mark.parametrize("attack", ["duplicate", "escape", "unsupported_version"])
def test_publisher_rejects_invalid_manifest_before_aws(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, attack: str
) -> None:
    directory = setup_corpus(tmp_path)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    if attack == "duplicate":
        manifest["documents"].append(manifest["documents"][0])
    elif attack == "escape":
        manifest["documents"][-1]["key"] = "corpus/../../private.json"
    else:
        manifest["version"] = 999
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    clients: list[str] = []
    monkeypatch.setattr(publish_corpus.boto3, "client", lambda name: clients.append(name))
    with pytest.raises(ValueError):
        publish_corpus.main()
    assert not clients
