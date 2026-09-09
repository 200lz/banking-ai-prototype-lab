import hashlib
import io
import json
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from packages.retrieval.aws import S3Retriever
from packages.retrieval.local import LocalRetriever
from packages.retrieval.models import Document


def document(**updates):
    fields = dict(
        id="TEST-001",
        title="Onboarding identity",
        text="Verify identity before onboarding.",
        source_type="synthetic",
        classification="internal",
        version="1",
        effective_date="2026-01-01",
        topic="onboarding",
        tags=["kyc"],
    )
    return Document(**(fields | updates))


def test_default_corpus_retrieves_policy_and_public_context():
    retriever = LocalRetriever()
    assert (
        retriever.search("How should we verify identity during onboarding?")[0].document.id
        == "SYN-ONBOARD-001"
    )
    assert "PUB-FDIC-001" in {
        h.document.id for h in retriever.search("FDIC deposit insurance coverage")
    }


def test_classification_filters_before_retrieval_and_get():
    hidden = document(id="SECRET-001", classification="restricted")
    retriever = LocalRetriever([hidden, document(id="PUBLIC-001", classification="public")])
    assert [h.document.id for h in retriever.search("identity", max_classification="public")] == [
        "PUBLIC-001"
    ]
    assert retriever.get("SECRET-001") is None
    with pytest.raises(ValueError):
        retriever.search("identity", max_classification="admin")


def test_retired_and_future_versions_are_not_retrieved():
    retriever = LocalRetriever(
        [
            document(id="OLD"),
            document(id="NEW", supersedes=["OLD"]),
            document(id="FUTURE", effective_date=date.today() + timedelta(days=1)),
        ]
    )
    assert {h.document.id for h in retriever.search("identity")} == {"NEW"}
    assert retriever.get("OLD") is None
    assert retriever.get("FUTURE") is None


def test_unknown_or_empty_query_does_not_invent_evidence():
    retriever = LocalRetriever()
    assert retriever.search("xylophone marzipan") == []
    with pytest.raises(ValueError):
        retriever.search(" ")
    with pytest.raises(ValueError):
        retriever.search("identity", top_k=1000)


def test_duplicate_ids_and_untrusted_urls_are_rejected():
    with pytest.raises(ValueError):
        LocalRetriever([document(), document()])
    with pytest.raises(ValidationError):
        document(
            source_type="public", classification="public", source_url="https://evil.example/doc"
        )


class FakeS3:
    def __init__(self, objects):
        self.objects = objects
        self.calls = []

    def get_object(self, **kwargs):
        self.calls.append(kwargs)
        return {"Body": io.BytesIO(self.objects[kwargs["Key"]])}


def s3_fixture(**changes):
    payload = document().model_dump_json().encode()
    entry = {"key": "corpus/doc.json", "sha256": hashlib.sha256(payload).hexdigest()} | changes
    client = FakeS3(
        {
            "corpus/manifest.json": json.dumps({"version": 1, "documents": [entry]}).encode(),
            "corpus/doc.json": payload,
        }
    )
    return S3Retriever("test-bucket", client=client), client


@pytest.mark.aws
def test_s3_adapter_integrity_cache_and_classification():
    retriever, client = s3_fixture()
    assert retriever.search("identity")[0].document.id == "TEST-001"
    assert retriever.get("TEST-001").sha256 == document().sha256
    assert retriever.get("TEST-001", max_classification="public") is None
    assert len(client.calls) == 2
    assert all(c["Bucket"] == "test-bucket" for c in client.calls)


@pytest.mark.parametrize(
    "changes", [{"sha256": "0" * 64}, {"key": "private/secret"}, {"key": "corpus/../secret"}]
)
def test_s3_rejects_tampering_and_prefix_escape(changes):
    retriever, _ = s3_fixture(**changes)
    with pytest.raises(ValueError):
        retriever.search("identity")


def test_s3_manifest_limit():
    retriever = S3Retriever("test", client=FakeS3({"corpus/manifest.json": b" " * 131073}))
    with pytest.raises(ValueError, match="size limit"):
        retriever.search("identity")
