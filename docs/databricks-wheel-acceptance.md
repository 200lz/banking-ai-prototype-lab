# Databricks wheel/Volume acceptance (2026-09-10 JST)

Recorded before implementation. This changes source delivery for the existing
synthetic publisher; financial formulas, outputs and application authority stay
unchanged. AWS remains frozen and the workspace remains Free Edition.

1. Inspect all four failed task traces, Workspace Files configuration, exact
   deployed paths, regular file types, run identity and inherited permissions.
   Classify the observed boundary separately from an unproven provider root cause.
   Never retry the unchanged `spark_python_task`.
2. Create at most one dedicated managed Unity Catalog Volume in the existing
   synthetic development schema (create that bounded schema if absent). Use the
   current developer identity and existing catalog. Record privileges; create no
   external storage, credentials, paid resources, trial or edition change.
3. Build a financial-only wheel from an explicit source allowlist. Reuse the same
   models, formulas and typed publisher; embed the exact committed 20-row fixture
   as package data accessed through `importlib.resources`. Exclude API, web,
   Bedrock, credentials and unrelated application code. Runtime entry points must
   not alter `sys.path` or read the bundle's Workspace Files source tree.
4. Upload the wheel to the managed Volume using official CLI/SDK facilities.
   Download it independently and require its SHA-256 to match the local artifact.
5. Run one minimal serverless wheel smoke with automatic retries disabled. Prove
   installation, imports and installed-package file/fixture reads. It must not
   require Workspace Files reads or write financial tables. If the same Errno 5
   occurs, stop and preserve evidence; do not begin another retry sequence.
6. Only after smoke PASS, migrate the existing pipeline job to a Volume-backed
   `python_wheel_task`, retaining environment version 2, serverless compute,
   concurrency one, 900-second timeout, existing catalog/schema and exact formulas.
7. Submit one pipeline execution first. Require real RAW 20, Bronze 20, Silver 18,
   rejected 1, collapsed duplicate 1 and Gold 3; verify actual rows, exact metrics,
   as-of metadata and provenance. Diagnose failure before considering at most one
   bounded retry after a concrete fix. Never change expected results for PASS.
8. Verify real Gold, complete/missing/stale profiles, the governed SDK adapter and
   SME review. Require separately cited policies, visible provenance, exact values,
   safe invalid/malformed/unavailable handling, refusal of credit approval and
   mandatory human review. Distinguish injected failure contracts from live tests.
9. Run financial/full Python/API/infrastructure and frontend regressions,
   deterministic evaluation, formatting/lint/types and security/source/history
   scans. Publish only actual, sanitized evidence; preserve prior failures and a
   cleanup inventory. Commit/push and require real hosted CI PASS.

If successful, describe the result precisely: runtime Workspace Files reads
failed repeatedly; switching the job artifact boundary to a packaged wheel on a
Unity Catalog Volume avoided that dependency. Do not claim a confirmed platform
bug or an unsupported Free Edition capability without supporting evidence.
