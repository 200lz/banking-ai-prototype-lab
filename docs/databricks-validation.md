# Databricks integration validation

Updated 2026-09-10 JST. **Authentication, bundle validation and deployment: PASS.
Real pipeline: FAIL / BLOCKED. Gold query, real application adapter and end-to-end
workspace integration: NOT TESTED.** All financial entities and records are synthetic.

## Actual Free Edition workspace attempt

Acceptance criteria were recorded before execution: use the existing dev bundle
and synthetic data; verify exact layer counts, indicators and provenance; require
real Gold reads and governed SME review; preserve safe missing/stale/invalid and
failure behavior; make no AWS, billing, trial or edition changes. Workspace PASS
requires every real integration gate below, not merely deployment.

The user confirmed **Free Edition**. Installed the official standalone Databricks
CLI **1.16.0** from its checksum-verified Windows release, then authenticated using
OAuth U2M. `current-user me` verified the active expected user and `auth describe`
verified the supplied workspace mapping. Credentials remain outside the repository.
The existing SDK remains pinned to **0.136.0**. The earlier missing-CLI/profile
preflight is historical; authentication is now proven.

| Real check | Actual result |
| --- | --- |
| Workspace discovery | PASS: Unity Catalog, an existing managed catalog and one stopped serverless 2X-Small SQL warehouse. No target schema or matching project job existed before deployment. |
| `bundle validate -t dev` | PASS without bundle or product changes. Two non-failing exclusions matched no files. |
| `bundle deploy -t dev` | PASS: one unscheduled serverless job, one task, environment version 2, `pydantic==2.13.5`, one concurrent run and 900-second timeout; bundle source/data files uploaded. No catalog, warehouse or classic cluster created. |
| Initial pipeline run | FAIL: 71.903 seconds, including two automatic task attempts. Workspace file reads failed on the financial models module and then the entry script. |
| One bounded retry of the unchanged job | FAIL: 104.309 seconds, including two automatic task attempts. Reads failed on the pipeline module and then the entry script. No further run submitted. |
| Read-only diagnosis | Uploaded objects are regular `FILE` objects; exported `models.py` exactly matches the local bytes. All errors occurred before RAW loading and schema/table writes. |
| Final resource state | Target schema absent; SQL warehouse still STOPPED. Both job runs terminal. One unscheduled job and its bundle files retained. |
| Actual Bronze/Silver/Gold counts | NOT TESTED; no output tables were produced. Expected fixture counts below are not live results. |
| Gold query / real SDK adapter / SME review | NOT TESTED; no SQL statement was submitted after the publisher failed. |

The exact blocker is **`OSError: [Errno 5] Input/output error` while reading
workspace Python files**. The root cause remains unresolved. This error does not
establish that the required capability is unsupported by Free Edition: official
[workspace-file documentation](https://docs.databricks.com/aws/en/files/workspace)
supports Python modules, and [serverless documentation](https://docs.databricks.com/aws/en/compute/serverless/limitations)
recommends workspace files. No compute, networking, permission or edition workaround
was attempted. If a required capability is confirmed unsupported, stop and report
it; do not upgrade automatically.

[Sanitized machine-readable evidence](validation/databricks-workspace-2026-09-10.json)
records UTC start/end times, durations, attempt errors and public run-reference
hashes. Actual job/run/task IDs, workspace host, principal, user-specific paths and
raw provider responses are retained only in ignored local evidence. No credentials
or provider identifiers are published.

Free Edition is a [no-cost offering with fair-use limits and no SLA](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).
No charge is expected for this confirmed Free Edition execution; an actual metered
dollar amount was not exposed or measured. The two job runtimes total 176.212
seconds, which is not a DBU or billing measurement. No LLM was invoked. No trial,
payment method, paid resource or edition change occurred. AWS remains frozen.
This test used the developer identity; a separate application identity restricted
to Gold-only access has **not** been verified. Free Edition results do not establish
production security, reliability or capacity.

## Retained resources and cleanup

The retained dev job has no schedule and both runs have ended. Its uploaded files
contain only the existing publisher, financial package and synthetic fixtures.
The existing catalog and warehouse were not created by this milestone. The
proposed `banking_ai_synthetic` schema does not exist, so there are no project
tables to drop.

To remove this milestone's bundle-managed resources, first confirm the same
workspace/profile and exact dev bundle, then run from `databricks/`:

```sh
databricks bundle summary -t dev --var catalog=workspace -p banking-ai-dev
databricks bundle destroy -t dev --var catalog=workspace -p banking-ai-dev
```

Review the destroy plan and verify removal. Inspect any remaining personal bundle
files before deleting only that deployment directory. Preserve private run evidence
first. Do not delete the pre-existing catalog/warehouse, use a recursive schema
drop, or change billing. Cleanup has not been executed.

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

## Remaining real verification after the runtime blocker is resolved

1. Resolve the workspace-file read failure in the existing Free Edition workspace.
   Authentication, CLI installation and bundle deployment are already verified.
   Preserve the failed evidence and check the same workspace/profile before a
   subsequent bounded run. If OAuth expires, authenticate the deployment user
   with `databricks auth login --host <workspace-url>`; keep profiles and tokens
   outside this repository. See the official
   [OAuth login instructions](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m).
2. Use a dedicated development schema. The bundle overwrites the four named
   synthetic Delta tables on each run. Grant the publisher the required schema
   creation/write rights; use a separate application identity with Gold-only
   SELECT plus USE CATALOG, USE SCHEMA and warehouse CAN USE. Do not grant the
   application access to Bronze, Silver or underlying raw storage.
3. In `databricks/`, validate, deploy and run the versioned development bundle:

   ```sh
   databricks bundle validate -t dev --var catalog=<development_catalog>
   databricks bundle deploy -t dev --var catalog=<development_catalog>
   databricks bundle run -t dev --var catalog=<development_catalog> financial_pipeline
   ```

   Record the real run status and an appropriately sanitized run reference.
   Inspect all four tables: expected fixture counts are Bronze 20, Silver 18,
   rejected 1 and Gold 3. Check the exact raw dataset hash and profile hash against
   the committed local snapshot. The two actual runs above failed before this
   output-verification step; successful native publication remains unverified.
4. Configure the application process with `FINANCIAL_BACKEND=databricks`,
   `DATABRICKS_HOST`, `DATABRICKS_WAREHOUSE_ID`, `DATABRICKS_CATALOG` and
   `DATABRICKS_SCHEMA`. The adapter accepts AWS workspace HTTPS hosts and scoped
   lowercase catalog/schema identifiers. Authentication is supplied through
   [Databricks unified authentication](https://docs.databricks.com/aws/en/dev-tools/auth/unified-auth).
   A service principal can use `DATABRICKS_AUTH_TYPE=oauth-m2m`,
   `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET` injected by a secret
   provider; use workload federation where the actual deployment supports it.
   No credential value belongs in a command example, `.env` commit, log or report.
   The current CDK stack does not provision these credentials or workspace grants.
   For this AWS-frozen milestone, explicitly use `AGENT_MODE=local`,
   `RETRIEVAL_BACKEND=local`, `API_AUTH_MODE=local`, a local audit path, and unset
   `AUDIT_TABLE` and remote `OTEL_EXPORTER_OTLP_ENDPOINT` before running the helper
   or application. Use the authenticated `DATABRICKS_CONFIG_PROFILE`; no Bedrock
   or DynamoDB action is authorized.
5. From the repository root, perform an actual governed Gold read and local
   controller end-to-end check:

   ```sh
   .venv/bin/python databricks/verify_profile.py --backend databricks --company-id SYN-SME-001 --output .runtime/databricks-live.json
   ```

   This opt-in command uses the real SDK adapter and fixed parameterized SQL. It
   does not create tables or deploy jobs. It requires a valid profile plus verified
   policy citations and human review. Inspect adapter `databricks`, hashes, values,
   risk flags and tool invocation. Repeat with missing-data company `SYN-SME-002`,
   stale company `SYN-SME-003` and an absent company to confirm safe abstention.
   An absent company intentionally exits with failure; no metric is fabricated.
6. Start the API with the same server environment and use the web SME review form
   to submit `SYN-SME-001`. Verify that the response says `source: databricks`,
   displays policy citations plus Gold lineage, and requires human review. Confirm
   that a credit approval/bypass request is refused and makes no financial query.
   Check runtime logs for metadata only. Separately test the intended warehouse
   permission denial and outage. These real permission and network checks are
   not substitutes for the already passing mock contract tests.

Mark workspace integration PASS only after the native job actually produced the
tables, the governed tool queried Gold successfully and the end-to-end synthetic
scenario succeeded. Bedrock-backed quality and latency remain a separate live
evaluation milestone. Retain failed runs as evidence, and do not reinterpret local
or mock results as cloud verification.
