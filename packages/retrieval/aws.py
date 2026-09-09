"""S3 manifest-backed retrieval for a bounded, curated small corpus.

The deployment ingestion identity writes an integrity manifest; the runtime only
reads. This implementation is deliberately replaceable with Bedrock Knowledge
Bases/OpenSearch for scale, without changing controller/tool contracts.
"""

import hashlib
import json
import time
from typing import Any

from packages.retrieval.local import LocalRetriever
from packages.retrieval.models import Document, SearchHit


class S3Retriever:
    def __init__(self, bucket: str, prefix: str = "corpus/", client: Any = None) -> None:
        if not bucket or not prefix.endswith("/") or ".." in prefix or prefix.startswith("/"):
            raise ValueError("A bucket and scoped corpus prefix are required")
        if client is None:
            import boto3

            client = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix
        self.client = client
        self._cached: LocalRetriever | None = None
        self._loaded_at = 0.0

    def _read(self, key: str, limit: int) -> bytes:
        if not key.startswith(self.prefix) or ".." in key or "\\" in key:
            raise ValueError("Object key escapes the corpus prefix")
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body = response["Body"]
        try:
            data: bytes = body.read(limit + 1)
        finally:
            body.close()
        if len(data) > limit:
            raise ValueError("Corpus object exceeds size limit")
        return data

    def _corpus(self) -> LocalRetriever:
        if self._cached is not None and time.monotonic() - self._loaded_at < 60:
            return self._cached
        manifest = json.loads(self._read(self.prefix + "manifest.json", 131072))
        if set(manifest) != {"version", "documents"} or manifest["version"] != 1:
            raise ValueError("Unsupported corpus manifest")
        entries = manifest["documents"]
        if not isinstance(entries, list) or not 1 <= len(entries) <= 256:
            raise ValueError("Manifest must contain 1..256 documents")
        docs = []
        keys: set[str] = set()
        for entry in entries:
            if set(entry) != {"key", "sha256"} or entry["key"] in keys:
                raise ValueError("Invalid or duplicate manifest entry")
            keys.add(entry["key"])
            payload = self._read(entry["key"], 65536)
            if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
                raise ValueError("Corpus integrity check failed")
            docs.append(Document.model_validate_json(payload))
        self._cached = LocalRetriever(docs)
        self._loaded_at = time.monotonic()
        return self._cached

    def get(self, document_id: str, *, max_classification: str = "internal") -> Document | None:
        return self._corpus().get(document_id, max_classification=max_classification)

    def search(
        self, query: str, *, top_k: int = 5, max_classification: str = "internal"
    ) -> list[SearchHit]:
        return self._corpus().search(query, top_k=top_k, max_classification=max_classification)
