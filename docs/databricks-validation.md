# Databricks integration validation

Updated 2026-09-15 JST. **Historical real Free Edition workspace validation:
PASS (2026-09-10 JST). Current project cleanup: PASS (2026-09-15 JST).** The
historical execution covered the Volume-backed wheel smoke, native pipeline,
exact live table reconciliation, Gold query, real SDK/API tool and browser SME
review. All entities and records are synthetic. AWS was frozen at that historical
checkpoint; no model was invoked during either Databricks milestone.

[Acceptance criteria](databricks-wheel-acceptance.md) were recorded before
implementation. [Historical execution evidence](validation/databricks-wheel-2026-09-10.json)
preserves actual timings, artifact hashes, checks and sanitized run references.
The [earlier failed execution](validation/databricks-workspace-2026-09-10.json)
remains historical evidence; it has not been relabeled as successful.

## Current cleanup verification (2026-09-15)

[Cleanup evidence](validation/databricks-cleanup-2026-09-15.json) records the
reviewed inventory, guarded deletion and separate live verification. Cleanup
completed at **08:58:35 UTC**; independent verification passed at **08:58:57 UTC**.
The project job, dedicated bundle, four managed Delta tables, wheel, managed
artifact Volume and synthetic schema were removed. The pre-existing catalog and
SQL warehouse were retained; the warehouse was **STOPPED**, with no active runs
or queries. Private execution outputs, data exports, source exports and the
hash-verified wheel were preserved before deletion. Immediate physical storage
erasure is not claimed.

Exact workspace identity, ownership and resource contents matched the reviewed
inventory. Free Edition is based on the retained explicit user confirmation,
not a newly queried edition endpoint. Cleanup started no compute, submitted no
SQL statements or jobs, and made no payment, trial or edition changes.

Two private inventory-helper compatibility findings were resolved before any
deletion: the Jobs API rejected a page size of 100 with a maximum of 26, so the
helper used 25 with complete SDK pagination and a 200-object bound; the bundle
contained an empty `artifacts/.internal` directory, which was allowed only at that
exact path after a fresh empty-directory check. Both original failures were
preserved. Neither finding establishes an unsupported Free Edition capability.

The following execution narrative describes the **2026-09-10 JST checkpoint**.
Its retained resources and RUNNING warehouse observation are historical; they
are superseded by the cleanup evidence above. Reproduction now requires a newly
approved deployment of the removed project resources.

## Historical diagnosis and source-delivery change (2026-09-10)

The two historical `spark_python_task` runs failed after **71.903 s** and
**104.309 s**, including four task attempts. All four full traces were inspected.
Each failed before RAW processing/table writes with `OSError: [Errno 5]
Input/output error` on different Workspace Python files. No unchanged pipeline
retry was submitted in this milestone.

Read-only checks returned `enableWorkspaceFilesystem=true`. Exact deployed paths
matched the bundle; source objects were regular `FILE` objects; the current user
or group had `CAN_MANAGE` on every inspected folder/file. The run-as user matched
the authenticated developer, environment version was 2, and exported `models.py`
matched local bytes. These observations support **B: observed runtime Workspace
Files read/mount failure**. The underlying cause is unresolved; no deterministic
path defect, permission denial, documented Free Edition restriction or confirmed
Databricks platform bug was established.

**Runtime Workspace Files reads failed repeatedly; switching the job artifact
boundary to a packaged wheel on a Unity Catalog Volume avoided that dependency.**

The financial-only wheel includes the shared models, unchanged formulas, shared
typed publisher, two entry points and the exact 20-row fixture through
`importlib.resources`. It excludes API/web/Bedrock code. The builder copies an
explicit source allowlist into a temporary build stage; there is no second
maintained business implementation. Runtime module origins must match the
installed distribution, and runtime code does not change `sys.path` or read the
bundle's Workspace source tree. Bundle-synced files remain available for inspection.

## Historical actual live results (2026-09-10)

Official CLI **1.16.0** and SDK **0.136.0** used the existing OAuth U2M development
profile. Credentials remain outside Git. User-confirmed **Free Edition** was
retained throughout.

| Check | Actual result |
| --- | --- |
| Managed storage | PASS: one new bounded `workspace.banking_ai_synthetic` schema and one MANAGED `banking_ai_artifacts` Volume, both owned by the current developer. Existing catalog reused. |
| Actual privileges | Catalog effective grants include `USE_CATALOG`; schema/Volume effective-grant arrays contain no explicit assignments. Ownership was independently verified; empty arrays are not evidence of denied owner access. |
| Minimal wheel | PASS: `banking_ai_financial-0.1.0-py3-none-any.whl`, 11,407 bytes, only `pydantic==2.13.5` as runtime dependency. |
| Upload integrity | PASS: official CLI upload followed by independent download; downloaded SHA-256 equals local SHA-256. |
| Minimal serverless wheel smoke | PASS: 33.733 s, one task attempt, zero retries. Installation/imports, installed-module hashes and packaged 20-row fixture reads verified; no Spark or table writes. |
| Existing bundle migration | PASS: validate/deploy and re-read deployed settings. `python_wheel_task`, `publish`, environment 2, exact Volume wheel, max concurrency 1, timeout 900 s. No classic compute or schedule. |
| Native pipeline | PASS: first migrated run, 94.873 s, one attempt, zero retries; no pipeline retry required. |
| Actual counts | RAW 20; Bronze **20**; Silver **18**; rejected **1**; collapsed duplicate **1**; Gold **3**. |
| Independent table reconciliation | PASS: four fixed bounded SELECTs; all Bronze payload/hash pairs, every Silver field, rejected errors and all three full Gold profiles match exactly. Twelve typed metric cells (including four nulls), timestamps, source IDs and dataset/Gold hashes verified. |
| SQL timing | Four-table verification 33,391 ms; individual reads Bronze 23,172 / Silver 2,937 / rejected 1,782 / Gold 1,984 ms. Bronze includes cold warehouse startup. |
| Real SDK/API | PASS: four Gold reads for complete/missing/stale/absent companies; 108 total checks across live and separately injected contracts, 10,399.707 ms overall. No model or AWS calls. |
| Input/scope controls | Invalid IDs and supplied SQL produce HTTP 422 with no financial query; prohibited credit approval is refused and escalated with no financial query. |
| Browser SME review | PASS: actual local Next.js to FastAPI to Databricks. Complete, missing and stale cards, policy excerpts, exact metrics, expanded hashes/formulas/source IDs and mandatory human review verified. Credit approval refused without the financial tool. |

Uploaded wheel SHA-256:

```text
d5f2b811db9beb1d04aea256888c3831ddb8238fcffa4f72c2e0a56b466f3166
```

The Volume path is
`/Volumes/workspace/banking_ai_synthetic/banking_ai_artifacts/<wheel-sha256>/banking_ai_financial-0.1.0-py3-none-any.whl`.
The complete SHA-resolved path is in the evidence JSON. A hash-named directory is
an operator integrity convention, not immutable storage or a signature.

The first browser lookup safely abstained after 3,303.5 ms. Its underlying failure
was not captured and remains unresolved. Restarting only the local API with private
SDK diagnostics was followed by three successful real statements; no product,
pipeline or workspace settings changed. Successful browser-displayed workflow
times were **5,495.2 / 3,965.7 / 3,804.7 ms** for complete/missing/stale and **19.6 ms**
for refusal. These are individual workflow observations, not browser round-trip
percentiles or an availability guarantee. The initial failure is retained in the
evidence instead of being removed from the record.

Malformed profiles/columns, tampered hashes and provider outage were tested through
**injected contracts**, distinctly from successful live reads. Actual warehouse
permission denial and a real outage remain **NOT TESTED**. A separate production
identity restricted to Gold-only SELECT remains **NOT TESTED**; this milestone
used the current development owner as explicitly approved.

## Reproduce the approved artifact boundary

These are operator instructions for an approved synthetic development environment,
not runtime-agent capabilities. Confirm edition, workspace/profile and exact
schema/Volume ownership first; do not upgrade when a capability is unavailable.
The official [wheel-task instructions](https://docs.databricks.com/aws/en/jobs/tasks/python-wheel)
describe packaged entry points and serverless environments; [Volume documentation](https://docs.databricks.com/aws/en/files/volumes)
describes managed file storage.

From the repository root after `make setup` (use `.venv/Scripts/python.exe` on
Windows), build offline with the locked developer tools:

```sh
.venv/bin/python databricks/build_wheel.py
```

Record the emitted SHA and artifact size. The builder uses pinned setuptools
84.0.0/wheel 0.48.0, fixed timestamps, no dependency resolution or build cache.
Require the canonical fixture hash below; compare each built module with source.
Reuse the single approved Volume. Set `WHEEL_SHA`, `WHEEL_FILE` and `WHEEL_PATH`
locally from the inspected output; `WHEEL_PATH` must be an absolute path under that
Volume with a SHA-specific directory. Do not use a Workspace Files wheel path.

```sh
databricks fs mkdir "dbfs:/Volumes/workspace/banking_ai_synthetic/banking_ai_artifacts/$WHEEL_SHA" -p banking-ai-dev
databricks fs cp "$WHEEL_FILE" "dbfs:$WHEEL_PATH" -p banking-ai-dev
databricks fs cp "dbfs:$WHEEL_PATH" .runtime/downloaded-financial.whl -p banking-ai-dev
sha256sum "$WHEEL_FILE" .runtime/downloaded-financial.whl
```

On PowerShell use `Get-FileHash -Algorithm SHA256` for both files. Require equal
hashes before any execution. `wheel_path` is a required bundle string; its Volume
boundary and hash are enforced by this operator preflight, not by YAML type validation.

Submit **one** minimal `python_wheel_task` with package `banking_ai_financial`,
entry point `smoke`, environment version 2 and dependencies `pydantic==2.13.5` plus
the verified absolute wheel path. Set `max_retries=0`, `retry_on_timeout=false`,
`disable_auto_optimization=true`, task/job timeout 300 seconds. Record the returned
run ID privately and inspect the one task's output. Require `status=PASS`,
`source_boundary=installed_wheel`, 20 fixture rows, installed module hash matches,
`spark_initialized=false`, `tables_written=false` and no Workspace source reads.
If the same Errno 5 occurs, stop. This milestone used a one-time Jobs submission,
not another saved diagnostic job.

Only after that gate passes, from `databricks/`:

```sh
databricks bundle validate -t dev --var catalog=workspace --var "wheel_path=$WHEEL_PATH" -p banking-ai-dev
databricks bundle deploy -t dev --var catalog=workspace --var "wheel_path=$WHEEL_PATH" -p banking-ai-dev
databricks bundle run -t dev --var catalog=workspace --var "wheel_path=$WHEEL_PATH" -p banking-ai-dev financial_pipeline
```

Inspect deployed settings and actual tables. Retain environment 2, timeout 900,
max concurrency one and disabled task retries/optimization. Do not rerun a failure
without diagnosis and a concrete bounded fix. These four named Delta tables are
overwritten; use only the approved synthetic schema.

Configure the API privately with `FINANCIAL_BACKEND=databricks`, authenticated
`DATABRICKS_CONFIG_PROFILE`, `DATABRICKS_AUTH_TYPE=databricks-cli`, workspace host,
warehouse ID, catalog and schema. Keep `AGENT_MODE=local`, `RETRIEVAL_BACKEND=local`,
`API_AUTH_MODE=local`, local audit, and no remote audit/OTLP or model configuration.
From the repository root, the committed read-only helper exercises the actual
adapter and policy workflow:

```sh
.venv/bin/python databricks/verify_profile.py --backend databricks --company-id SYN-SME-001 --output .runtime/databricks-live.json
```

Verify real complete/missing/stale/absent profiles and actual browser behavior;
do not reinterpret injected failures as live permission testing. Keep workspace
hosts, identities, job/task/statement IDs and raw provider responses private.

## Historical retained resources and cleanup procedure (2026-09-10)

At the September 10 checkpoint, the existing unscheduled job had been updated;
the one-time smoke and first wheel pipeline runs were terminal. Retained project
resources then comprised the bounded schema,
one MANAGED Volume, one wheel, four named Delta tables and bundle inspection files.
No catalog, warehouse, classic cluster, external storage or cloud credentials were
created. The existing serverless **2X-Small** SQL warehouse was **RUNNING** at that
inspection with its unchanged **10-minute auto-stop**. This differed from the
STOPPED state before that milestone; final auto-stop completion was not asserted
then. The September 15 independent verification now establishes **STOPPED**.

[Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)
is no-cost with fair-use limits and no SLA. No charge is expected; a metered dollar
amount was not exposed or measured. Job durations are not DBUs. No paid trial,
payment method, paid resource or edition change occurred. See [cost boundaries](../COST.md).

Cleanup had **not** been executed at the September 10 checkpoint; the September
15 cleanup above is now **PASS**. The following procedure is retained for a
future separately approved deployment. Preserve private evidence and confirm the
exact workspace/profile and ownership before removing anything. From `databricks/`,
inspect `bundle summary`, then `bundle destroy` with `-t dev`, the same catalog,
`wheel_path` and profile variables above. Review the plan; verify only this job and
its deployment files are removed. Inspect any residual personal bundle directory
before deleting only that directory.

Separately remove the four exact project tables (`financial_gold`,
`financial_rejected`, `financial_silver`, `financial_bronze`) in
`workspace.banking_ai_synthetic`; remove the single MANAGED `banking_ai_artifacts`
Volume, then drop the schema only after confirming it is empty. Do not use a
recursive schema drop, delete the pre-existing catalog/warehouse or change billing.
Deleting managed objects can delete their data; preserve the intended evidence
first. No cleanup instruction is an autonomous runtime-agent tool.

## Historical local evidence (2026-09-09)

| Check | Actual result |
| --- | --- |
| `python -m packages.financial.pipeline` | PASS: 20 Bronze rows, 18 valid Silver rows, 1 collapsed duplicate, 1 rejected row, 3 Gold profiles. |
| Financial unit/API suite | PASS: 53 tests, including Decimal formulas, missing data, schema/ID validation, provenance, stale data, SQL contract, outage, no approval bypass and model-input minimization. |
| Complete Python regression at this milestone | PASS: 163 tests; final repository report records the authoritative count after other milestones. |
| Existing deterministic evaluation | PASS: 61 cases, all gates; no LLM calls. The existing evaluation does not measure the new financial profile scenarios. |
| Financial/service/native-job type checking | PASS: 18 modules including the read-only verification helper. |
| Financial/native Bandit checks | PASS: no findings at any severity. |
| Native Spark publisher | PASS against a local fake Spark contract, including typed schemas and Gold-last writes; no actual Spark/Delta execution. |
| Real Databricks HTTP adapter | PASS against injected response fixtures; no live network calls. |
| Local policy + Gold tool integration | PASS: actual local controller request, cited credit policy, quantitative evidence and mandatory human review. |

The machine-readable [local profile evidence](validation/databricks-local.json)
records the executed request and its actual local latency. It reports zero model
tokens and zero inference cost because it uses the deterministic planner. No
Databricks compute cost was measured.

The exact raw fixture hash is:

```text
3514bdb316c518976a13b06d5820885db73f76bb0b250c3e20c9b516c41fbe2a
```

The complete example `SYN-SME-001` covers six months through 2026-08-31. Its
revenue trend is 20.00%, cash-flow volatility is JPY 44,596.96, debt-service share
is 0.0860, and liquidity indicator is 1.9433 months. Formula definitions and source
record IDs accompany the result. `SYN-SME-002` demonstrates unavailable dependent
indicators and missing/invalid-data flags; `SYN-SME-003` demonstrates old financial
periods. Freshness is recomputed at request time, so fixture dates will age.

Reproduce locally from the repository root after `make setup` (PowerShell uses
`.venv/Scripts/python.exe`):

```sh
.venv/bin/python -m packages.financial.pipeline
.venv/bin/python -m pytest tests/unit/test_financial.py tests/integration/test_financial_api.py -q
.venv/bin/python databricks/verify_profile.py --backend local --output .runtime/databricks-local.json
```

To reproduce the complete fixture itself, run
`python databricks/generate_fixture.py`. The generator writes only synthetic
financial source/Gold artifacts. A regression compares committed Gold exactly
against a rebuild of the committed raw file.
