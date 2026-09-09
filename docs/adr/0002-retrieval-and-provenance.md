# ADR 0002 — Replaceable retrieval and manifest-based S3 corpus

Status: accepted for the small-corpus prototype, 2026-09-09.

Local tests need fast, reproducible retrieval and deployment needs a real AWS
storage adapter. Use a protocol with search/get and explicit classification limits.
The local implementation uses lexical scoring; S3 verifies a bounded manifest and
document JSON hashes, then builds the same index. Search and get share access and
version rules.

This avoids a mandatory managed vector index for a twelve-document demonstration
while preserving a replacement boundary. It does not provide enterprise semantic
recall, hybrid ranking, per-user entitlements, incremental indexing or a freshness
guarantee. Future managed retrieval must pass the same contract tests plus scale,
relevance and authorization tests.

Exact source sentences and text hashes support mechanical citations. All sentences
from a selected source are preserved to avoid stripping a qualification. Distinct
active synthetic sources on one topic cause conservative review unless superseded.
This is intentionally stricter than semantic conflict adjudication and will require
document-section/applicability modelling at institutional scale.
