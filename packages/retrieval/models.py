"""Typed corpus boundary: documents are untrusted data, never instructions."""

import hashlib
from datetime import date
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

Classification = Literal["public", "internal", "restricted"]
CLASSIFICATION_RANK = {"public": 0, "internal": 1, "restricted": 2}


class Document(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(pattern=r"^[A-Z0-9][A-Z0-9_-]{0,79}$")
    title: str = Field(min_length=1, max_length=250)
    text: str = Field(min_length=1, max_length=16000)
    source_type: Literal["synthetic", "public"]
    source_url: str | None = None
    classification: Classification = "internal"
    version: str = Field(min_length=1, max_length=30)
    effective_date: date
    topic: str = Field(min_length=1, max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=50)
    supersedes: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_source(self) -> "Document":
        from urllib.parse import urlparse

        if self.source_type == "public":
            parsed = urlparse(self.source_url or "")
            if parsed.scheme != "https" or parsed.hostname not in {
                "www.fdic.gov",
                "www.fincen.gov",
            }:
                raise ValueError("Public sources must use the curated HTTPS publisher allowlist")
            if self.classification != "public":
                raise ValueError("Public sources must have public classification")
        elif self.source_url is not None:
            raise ValueError("Synthetic documents have no external source URL")
        return self

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


class SearchHit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    document: Document
    score: float = Field(ge=0)


class Retriever(Protocol):
    def search(
        self, query: str, *, top_k: int = 5, max_classification: str = "internal"
    ) -> list[SearchHit]: ...

    def get(self, document_id: str, *, max_classification: str = "internal") -> Document | None: ...
