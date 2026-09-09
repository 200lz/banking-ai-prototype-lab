# Databricks integration validation

Recorded 2026-09-09. **Local adapter and contract tests: PASS. Real Databricks
workspace execution: NOT TESTED.** All financial entities and records are synthetic.

Environment preflight found no Databricks CLI installation, no `DATABRICKS_*`
environment configuration and no `~/.databrickscfg` profile. No authenticated
workspace is available. No real job/run identifier, Delta table creation,
Statement Execution API call, workspace Gold query or cloud end-to-end scenario
has been verified. The Databricks SDK is installed and pinned to 0.136.0 in the
runtime and development locks; package presence is not an integration result.

## Executed evidence

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

## Remaining external setup and real verification

1. Obtain an AWS Databricks development workspace with Unity Catalog, a catalog
   authorized for this synthetic exercise, serverless job capability, and a SQL
   warehouse. Install a supported Databricks CLI. Authenticate the deployment user
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
   the committed local snapshot. This step has not been executed here.
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
