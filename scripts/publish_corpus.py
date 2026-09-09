"""Publish already reviewed synthetic corpus with manifest last, after CDK deploy."""

import hashlib
import json
import re
from pathlib import Path

import boto3

from packages.retrieval.models import Document


def prepare_uploads(directory: Path) -> list[tuple[Path, str]]:
    """Validate every local byte before acquiring an AWS client or publishing."""
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {"version", "documents"}:
        raise ValueError("Invalid corpus manifest schema")
    entries = manifest["documents"]
    if manifest["version"] != 1 or not isinstance(entries, list) or not 1 <= len(entries) <= 256:
        raise ValueError("Unsupported or empty corpus manifest")
    uploads: list[tuple[Path, str]] = []
    keys: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"key", "sha256"}:
            raise ValueError("Invalid corpus manifest entry")
        key = entry["key"]
        if (
            not isinstance(key, str)
            or not re.fullmatch(r"corpus/[A-Z0-9_-]+\.json", key)
            or key in keys
        ):
            raise ValueError("Manifest key is duplicated or outside the corpus prefix")
        keys.add(key)
        path = directory / key.removeprefix("corpus/")
        payload = path.read_bytes()
        if len(payload) > 65536 or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise ValueError("Corpus object does not match its integrity manifest")
        document = Document.model_validate_json(payload)
        if path.stem != document.id:
            raise ValueError("Corpus object key does not match the document ID")
        uploads.append((path, key))
    return [*uploads, (manifest_path, "corpus/manifest.json")]


def main() -> None:
    outputs = json.loads(Path(".runtime/cloud-outputs.json").read_text(encoding="utf-8"))
    bucket = outputs["BankingAiPrototypeLab"]["CorpusBucket"]
    if not isinstance(bucket, str) or not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", bucket):
        raise ValueError("Unexpected corpus bucket output")
    directory = Path(".runtime/corpus")
    uploads = prepare_uploads(directory)
    client = boto3.client("s3")
    for path, key in uploads:
        client.upload_file(
            str(path),
            bucket,
            key,
            ExtraArgs={"ContentType": "application/json", "ServerSideEncryption": "AES256"},
        )
    print(
        "Corpus published, manifest last. Complete authenticated API/model smoke checks in docs/cloud-deployment.md."
    )


if __name__ == "__main__":
    main()
