# Implementation and validation report

2026-09-10 JST. **Local application, Docker, GitHub Actions, AWS bootstrap and Bedrock discovery: PASS. Lambda quota: PENDING. Nova Lite inquiry: SUBMITTED / PENDING. AWS application deployment: NOT TESTED / BLOCKED. AWS smoke and live Bedrock evaluation: NOT TESTED. Previous Bedrock qualification: FAIL. Databricks authentication, Volume-backed wheel smoke, native pipeline, live table verification and real SDK/API integration: PASS. Live browser SME review: PASS; this revision's hosted CI: PENDING.** No real-bank affiliation; all internal policies, companies and financial records are synthetic.

The [authoritative verification matrix](docs/verification-matrix.md) links every PASS to executed evidence. Hosted CI was independently verified using `gh`; deployed AWS, live Bedrock and Databricks workspace success is not inferred from local or hosted tests.

The real Tokyo attempt verified the expected non-root sandbox identity, discovered
62 text-output models and completed a target CDK synth/diff. The subsequently
approved Tokyo bootstrap is now **PERFORMED / PASS**: `CDKToolkit` reached
`CREATE_COMPLETE` and all 11 reviewed resources passed actual verification.
Application deployment remains **NOT TESTED / BLOCKED** by Lambda capacity.
The request for 1,001 is **PENDING** (provider status `CASE_OPENED`); last-observed
applied concurrency is 10 and the application reservation remains three.
The default unconnected Amplify configuration has no secret dependency, but a
GitHub connection is still needed for a functioning hosted frontend; actual
creation of that unconnected configuration is unverified.
Nova Lite qualification failed with provider throttling, and all 166 queried
on-demand/daily-token account quotas were zero. No three-case smoke or twenty-case
live suite ran. Actual failed artifacts and redacted preflight evidence are
linked in [cloud validation](docs/cloud-validation.md).

The separate Tokyo Nova Lite capacity inquiry is **SUBMITTED / PENDING** under
Basic Support, with provider status **Unassigned** and stored routing
**Account / Service Quotas, General**. Submission establishes neither restored
capacity nor successful inference. [Confirmed case evidence](docs/validation/nova-lite-support-case-2026-09-09.json)
supersedes the earlier browser-login checkpoint in the escalation record.

The [bootstrap execution and cleanup record](docs/cdk-bootstrap.md) documents
same-account trust, the approved administrator execution role, 25 passing checks,
private/versioned/encrypted assets and the deliberate decision to keep bootstrap
for the planned sandbox deployment. Application runtime IAM was not changed.

## What was built and extended

- Preserved the FastAPI/Next.js product, nine-stage controller, local/S3 retrieval, five baseline tools, exact citations, guardrails, content-free audit/OTel and bounded Strands/Bedrock planner.
- Verified fresh API, web, collector and Lambda images. Added repeatable container acceptance, real health checks, isolated loopback networking, non-root probes, controlled traces, restart/audit verification and cleanup.
- Added SME Lending Review Copilot: synthetic RAW/Bronze/Silver/Gold, independent Decimal formulas, provenance/hashes, business-period freshness, missing-data handling, strict local/Databricks financial_profile_tool, mandatory review, native bundle/Delta publisher and a working financial evidence UI.
- Added checksum-pinned source/history secret scanning and pinned Actions. CI covers code quality, tests, evaluation, security, web/CDK builds and containers without cloud credentials.
- Added make aws-smoke with nine bounded resource/auth/audit checks and make live-eval with access preflight, one-case qualification, three-case smoke and twenty-case live suite. Mocked contract tests do not establish real integration.
- Added actual browser screenshots, milestone reports, architecture decisions, Japanese institution considerations, threat/readiness documentation and a [3–5 minute interview demo](docs/interview-demo.md).

## Databricks wheel and live data-platform validation: PASS

On 2026-09-10 JST, read-only diagnosis confirmed Workspace Files support enabled,
matching deployed paths, regular FILE objects, the expected run identity and
inherited CAN_MANAGE access. All four earlier traces failed at file reads before
RAW processing. The observation is a runtime Workspace Files read/mount failure;
its underlying cause remains unresolved.

Runtime Workspace Files reads failed repeatedly; switching the job artifact
boundary to a packaged wheel on a Unity Catalog Volume avoided that dependency.
No confirmed provider bug or unsupported Free Edition feature is claimed.

The financial-only wheel reuses the same models, formulas and typed publisher,
with the exact 20-row fixture read through `importlib.resources`. It contains no
API, Bedrock or Databricks adapter code. The existing catalog holds one dedicated
managed Volume under the synthetic development schema; no external storage or
cloud credential was created. The uploaded wheel was independently downloaded
and its SHA-256 verified:

```text
banking_ai_financial-0.1.0-py3-none-any.whl (11,407 bytes)
d5f2b811db9beb1d04aea256888c3831ddb8238fcffa4f72c2e0a56b466f3166
```

| Real check | Actual result |
| --- | --- |
| Installed-wheel smoke | PASS; 33.733 seconds, one attempt, zero retries; installed module hashes match the wheel, packaged fixture read, no Spark or table writes |
| Migrated serverless `python_wheel_task` | PASS; 94.873 seconds, one attempt, zero retries; environment 2, concurrency one and 900-second timeout retained |
| RAW / Bronze / Silver / rejected / Gold | 20 / 20 / 18 / 1 / 3; one duplicate collapsed |
| Independent live table verification | PASS; four fixed SELECTs checked all rows, twelve metric cells including nulls, business as-of metadata and dataset/profile hashes |
| Real `financial_profile_tool` through FastAPI | PASS; four real adapter reads for complete `001`, missing `002`, stale `003` and absent `999` synthetic companies |
| Citation, review and scope boundaries | PASS; policy evidence and nine controller stages verified; invalid input and prohibited credit approval made no additional financial calls |
| Malformed profile/columns, tampered hash and outage | PASS as injected contract tests only; no real warehouse permission denial or outage was induced |
| Browser → API → live Databricks | PASS; complete/missing/stale profiles and prohibited approval refusal, with policy citations, provenance and human review |
| Local regression | 314 Python/API/infrastructure tests, 26 frontend tests and all 61 deterministic cases PASS; Ruff, mypy, Bandit and dependency audits PASS |
| This revision's hosted CI | PENDING; prior completed baseline is dated separately below |

The four-table verification took 33.391 seconds; the four-read API scenario group
and its local boundary checks took 10.399707 seconds. These are bounded observed
runs, not p95 service-level or production capacity measurements. Browser workflow
latencies were 5,495.2 / 3,965.7 / 3,804.7 ms for complete/missing/stale profiles,
and 19.6 ms for prohibited credit refusal, which invoked no financial tool.
The three successful live profiles showed source/as-of metadata, exact indicators,
three policy citations and mandatory review; expanded formula/source-ID/hash
provenance was inspected. The initial browser request safely abstained after
3,303.5 ms. Its provider outcome and underlying cause remain unresolved; only the
local API was restarted with private diagnostic instrumentation, with no product
change. The three subsequent browser SQL reads succeeded; this is not evidence of
a confirmed fix or provider bug. The controller
used local planning/retrieval/audit; recorded AWS-call attempts and LLM invocations
were zero. A separate production Gold-only identity, effective denied-access tests
and cloud deadline behavior remain unverified. The workspace stayed Free Edition;
no trial/payment, edition change or paid-resource purchase occurred. Actual
metered Databricks cost was not measured.

[Sanitized wheel/live evidence](docs/validation/databricks-wheel-2026-09-10.json)
and [validation details](docs/databricks-validation.md) separate real results from
injected contracts. Prior failed runs remain below and in their immutable evidence.

## Historical Databricks workspace attempt: pipeline FAIL / BLOCKED

This was the earlier source-file attempt. Its failed results remain valid
historical evidence; the separately authorized wheel continuation above succeeded.

On 2026-09-10 JST, the user confirmed Free Edition. Official CLI 1.16.0 was
installed with checksum verification; CLI OAuth U2M authentication matched the
expected active user. At that earlier stage, the pinned SDK had not been used live.
Development bundle validation and deployment passed
without product or bundle code changes. Deployment created one unscheduled
serverless job using environment version 2, `pydantic==2.13.5`, a 900-second
timeout and maximum concurrency one. The existing catalog was selected; the
existing 2X-Small SQL warehouse was discovered and left STOPPED.

Two unchanged runs were submitted, including one bounded manual retry; each
performed two automatic task attempts. Both failed with `OSError: [Errno 5]`
reading workspace Python files before raw-data processing or schema writes.
Run durations were **71.903 seconds** and **104.309 seconds**. Workspace metadata
reported the uploaded object as FILE, and the exported models file matched the
local source exactly. These observations do not establish the root cause or an
unsupported Free Edition feature. The final schema was absent and the existing
warehouse was **STOPPED**; no further Databricks actions were taken in that earlier milestone.

| Check | Actual result |
| --- | --- |
| Expected-user authentication and development bundle validation | PASS |
| Native job deployment | PASS; one unscheduled serverless job |
| Native RAW → Bronze → Silver → Gold execution | FAIL / BLOCKED; both runs stopped before data processing |
| Real Gold query, SDK adapter and end-to-end policy review | NOT TESTED |
| Live missing/stale/invalid-data, refusal and permission/outage scenarios | NOT TESTED |
| Local financial regression | 53 tests PASS |
| Complete local Python/API/infrastructure regression | 294 tests PASS |
| Deterministic local evaluation | 61 cases PASS, all gates; not financial-profile or live-model measurement |
| Local formatting/lint and Python types | Ruff format/lint PASS; mypy PASS across 40 modules |
| Frontend regression and quality checks | 26 tests, formatting, lint and type checking PASS |

The [sanitized workspace record](docs/validation/databricks-workspace-2026-09-10.json)
and [Databricks validation](docs/databricks-validation.md) retain the failed-run
evidence. Private workspace/user/run identifiers remain outside public files.
No LLM, AWS or SQL calls, trial/payment, edition change or new paid resources were
part of this milestone. A separate production identity with Gold-only permissions
and its effective access remain unverified. The preceding AWS status is unchanged.

## Tokyo continuation regression results (2026-09-09)

Before AWS resource changes, all existing lint/type/test/evaluation/security/synth
gates passed: 284 Python/API/infrastructure tests, 26 frontend tests and all
61 deterministic cases. The fresh local baseline measured median 12.696 ms and
p95 16.525 ms, with zero model tokens and $0 inference cost.

Actual model access exposed one preflight defect: Bedrock's availability API may
return a canonical versionless model ID. The smallest fix accepts that observed
response shape while retaining exact versioned model-detail verification. Ten new
regressions reject unrelated models and mismatched versions; the focused harness
suite now passes 70 tests. No runtime tools, IAM boundaries or evaluation cases
were changed.

After that fix, the existing local task gates passed again:

| Gate | Actual result | Elapsed seconds |
| --- | --- | ---: |
| Formatting/lint | 53 Python files, Ruff, ESLint, web Prettier PASS | 6.928 |
| Type checking | 40 Python modules and TypeScript PASS | 4.764 |
| Tests | **294 Python/API/infrastructure + 26 frontend passed** | 49.451 |
| Security | Bandit zero findings; Python/web/CDK audits zero known vulnerabilities | 11.005 |

[Machine-readable continuation checks](docs/validation/aws-local-regressions-2026-09-09.json)
preserve commands, counts and the pre-deploy synthesis/evaluation record. The
existing Starlette/AnyIO deprecation warning remains non-failing. The following
table is historical evidence for the previously published product; browser,
coverage and container measurements were not silently rerun or relabeled.

Continuation documentation checks passed: Prettier Markdown parsing for eleven
files, seven JSON parses, 94 local links/anchors, LF and private-identifier
checks, `git diff --check`, and source/complete-history secret scans. Original
failed artifact bytes were preserved locally before LF normalization for Git.

## Previously published local test results

| Executed verification | Actual result |
| --- | --- |
| Combined Python/API/retrieval/security/analytics/evaluator/CLI/CDK suite | **284 passed**, 52.39 seconds |
| Statement coverage over services/packages | **90%**; 1,377 statements, 134 uncovered |
| Frontend tests | **26 passed** |
| Python formatting, Ruff, mypy | PASS: 53 formatted files, 40 typed source files |
| Frontend formatting, ESLint, TypeScript, production build | PASS; Next.js 15.5.25 |
| Bandit runtime/infrastructure/native pipeline scan | Zero findings at all severities; zero skipped files |
| Locked Python dependency vulnerability audit | No known vulnerabilities found |
| Web and CDK npm audits | Zero vulnerabilities reported |
| Gitleaks source and Git-history scans | PASS: no leaks detected; automated scans are not an absolute guarantee |
| Dependency consistency | pip check passed |
| CDK offline synthesis and security assertions | PASS; no resource created |
| Native five-scenario demo | PASS |
| Native browser policy + SME review; mobile layout | PASS, actual screenshots saved |
| Local financial pipeline | RAW20 → Bronze20 → Silver18 → Gold3; 1 duplicate collapsed, 1 invalid row rejected |
| Databricks financial contract suite | 53 tests passed; injected SDK/Spark clients are not live integration |
| Live-harness contracts | 60 tests passed with fake clients/runners and temporary artifacts |
| AWS-smoke contracts | 49 tests passed without AWS calls |

[Machine-readable local evidence](docs/validation/local-final.json) records commands, coverage, evaluation and dependency-lock hashes. One upstream Starlette/AnyIO TestClient deprecation warning remains. Coverage excludes developer scripts, frontend and infrastructure; their tests/checks are reported separately.

Git initially had no commits or remote. The verified implementation was committed
as `ae07e2c` using the connected GitHub identity's public noreply address. A final
portability change enforces LF checkouts and generated lock/fixture text, keeping
byte-hashed inputs stable across Windows and Linux; 55 affected regressions and
format/lint checks passed afterward. The resulting commit
`827888ab0d3c82f937d8106b51f8bf04f4a3fcc4` is now published in the
[public repository](https://github.com/200lz/banking-ai-prototype-lab) and passed
the independently verified hosted workflow below.

## GitHub hosted CI: PASS

Verified with GitHub CLI REST queries for the run, jobs, artifacts and check-run
annotations, supplemented by job logs read through the connected GitHub app.
The hosted job completed on 2026-09-09 at 11:21:25 UTC; all 22 recorded
steps concluded `success`, including setup, preservation and post-job cleanup.

| Hosted evidence | Verified value |
| --- | --- |
| Workflow | `Quality and safety regression` (`.github/workflows/ci.yml`) |
| Original run | [34344534926](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34344534926), workflow run number 1, event `push` |
| Tested commit / branch | `827888ab0d3c82f937d8106b51f8bf04f4a3fcc4` / `main` |
| Job | `quality`, job ID `102442885999`, **PASS** |
| Hosted Linux runner | `ubuntu-latest`; runner `GitHub Actions 1000000254`, group `GitHub Actions` |
| Runner image from job logs | Ubuntu 24.04.5 LTS, image `ubuntu-24.04`, version `20260907.300.1` |
| Hosted test counts | 284 Python/API/infrastructure tests passed in 8.94 seconds; 26 frontend tests passed |
| Preserved artifact | `evidence-and-infrastructure`, artifact ID `10101336517`, 119,231 bytes, not expired when checked |
| Artifact SHA-256 | `4859f99f1ed94d0b6f1a434c33865371aa598c04553dcb819522fa3c7bcc8ccd` |

The actual successful gates were:

- Exact dependency installation; formatting and linting; type checking.
- Python unit/API integration tests, infrastructure security assertions and
  frontend tests through `make test`.
- Evaluation smoke gates and full deterministic evaluation gates.
- Security analysis and dependency vulnerability audits.
- Next.js production build and CDK synthesis without credentials.
- Checksum-verified secret-scanner installation, source candidate scan and complete
  Git history secret scan.
- Fresh Docker build, health checks, scenario acceptance, telemetry validation,
  restart validation and cleanup.
- Artifact preservation for evaluation JSON, synthesized templates and the
  container validation report.

**Node action deprecation: NON-BLOCKING.** The check-run warning names pinned
`actions/checkout`, `actions/setup-python`, `actions/setup-node` and
`actions/upload-artifact` as targeting Node.js 20 and being forced by GitHub to run
on Node.js 24. The job passed with that warning. The action pins are unchanged;
the warning has not been fixed. A separate maintenance change should update the
pins and verify another hosted run. This concerns the actions' runtime, not a
change to the application's configured Node.js version.

Local checks for this documentation update passed: `git diff --check`, Prettier
Markdown `--debug-check` for the four edited files, and checks of 50 local
links/anchors, LF endings, code fences, verified run metadata, the `main` badge,
unchanged cloud statuses and documentation-only scope.

The follow-up documentation commit `6f24ef61fcf5dcbb7d3906fc38aa3c124b436b19`
also passed [hosted run 34346854721](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34346854721)
on GitHub-hosted Linux, with all 22 steps successful and artifact
`evidence-and-infrastructure` (ID `10102261921`). That is the independently
reverified hosted baseline for the Tokyo continuation; the current `main` badge
links to subsequent workflow runs.

The Tokyo evidence and canonical model-ID fix then passed
[hosted run 34354616969](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34354616969)
at commit `8e8c65f227cc9c876792ca835452d2a032d80fb2`. All 22 steps passed on
GitHub-hosted `ubuntu-latest`, job `quality` (`102476028977`), including Docker
validation. Artifact `evidence-and-infrastructure`, ID `10105375539`, was
124,595 bytes and unexpired when verified; SHA-256
`b487fb985de0735ee96ac63c4400fe8c975dacb7adc5815eb301c6bba03ab95f`.
This is the verified hosted baseline preceding the bootstrap documentation update.

The independently verified 2026-09-09 hosted baseline was
[run 34357464386](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34357464386)
at commit `4c3b1437b1f1caf41ef07b68811be8f8873bc02a`: job `quality` completed
successfully at 13:36:53 UTC, with all 22 steps successful. Its preserved artifact
was `evidence-and-infrastructure`, 124,946 bytes, SHA-256
`1a1f21c8916c35f31eaed497e5361bb9d7f97596dd90d132d2b92cfd77565c92`.
The same Node action warning remained non-blocking. This is commit-specific
historical evidence; each subsequent documentation commit requires its own
completed result in the [hosted workflow history](https://github.com/200lz/banking-ai-prototype-lab/actions/workflows/ci.yml).

The subsequent documentation baseline [run 34365266090](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34365266090)
passed at commit `ff03313f33cb060491b6f50a91140d0e403c4a95`. The latest completed
prior baseline is [run 34370908568](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34370908568),
**PASS** at commit `712fda9c5fd690fc8146009d7104e155b7290713` on 2026-09-09 UTC.
This predates the wheel implementation; the new revision's hosted run is PENDING.
No new CI success or action-runtime warning fix is claimed here.

## Docker status: PASS

The installed Docker Desktop was started safely. Actual Linux/AMD64 Engine 20.10.17 built all four runtime images with --pull --no-cache. The canonical run took 151.5 seconds and verified three healthy services, web-to-API container DNS, policy citations, 30.00% DTI, prohibited approval refusal, human review, PII canary and retrieved-document injection quarantine. Exported traces contained all nine stages and no tested payload canaries; runtime logs had zero errors/warnings. Restart retained the original audit event and produced the same policy answer. The isolated stack shut down cleanly.

A supplementary seventh scenario verified the SME profile, all four exact indicators, three policy citations and mandatory review against the same built image IDs. The Lambda probe imported the handler and ran the controller directly as UID 10001 without network; it did not invoke AWS or the Lambda event handler.

| Image | Measured bytes |
| --- | ---: |
| API | 240,676,967 |
| Web | 244,157,518 |
| Collector | 366,967,838 |
| Lambda | 810,790,963 |

See [container milestone](docs/milestones/01-containers.md), [fresh-build evidence](docs/validation/containers-2026-09-09.json), and [SME supplement](docs/validation/container-sme-2026-09-09.json). OS-package image vulnerability scanning and signing were NOT TESTED. Dependency audits and privilege checks do not replace them.

## Evaluation results

The unchanged **61-case deterministic baseline** and **20-case smoke set** passed every configured gate. The independent mechanical scorer reports 100% authored correctness, retrieval recall, applicable citation correctness/groundedness, policy compliance, tool selection, expected escalation and cost completeness; unsupported-claim rate is 0% under that scorer.

| Measurement | Deterministic local | Live Bedrock |
| --- | --- | --- |
| Full cases | 61 | 20-case suite NOT RUN; qualification failed |
| Mean / median workflow latency | 12.999 / 12.696 ms | Unavailable for unrun suite |
| Nearest-rank p95 workflow latency | 16.525 ms | Unavailable for unrun suite |
| Mean retrieval latency | 1.856 ms | Unavailable for unrun suite |
| Input / output model tokens | 0 / 0 | Unavailable; qualification usage incomplete |
| Estimated inference cost | $0 | Unavailable; reported lower bound is not a bill |

[latest.json](evals/results/latest.json) contains actual per-case responses, denominators and dataset hash. Measurements are in-process on Windows/Python 3.11.5 and exclude HTTP, cold starts and inference. This correlated authored development set is not a held-out benchmark or LLM accuracy result. Financial profiles are covered separately; the original 61 cases do not score them.

The initial failed baseline and two failed container runs remain available. They exposed missed escalation/injection, dropped calculation provenance and restart-port assumptions. New financial tests caught ingestion-time freshness and late unsafe-source profile clearing. Fixes and regressions are recorded in [the development log](docs/development-log.md).

The [first live qualification](evals/results/bedrock-2026-09-09.json) and
[diagnostic retry](evals/results/bedrock-2026-09-09-retry-1.json) each executed one
case and failed before smoke/suite phases. Both returned safe abstention and
human review, but the normal-workflow case did not pass its answer/escalation
expectations. Citation correctness, groundedness and unsupported-claim rate are
not applicable without an answer. Each probe exported 13 controlled spans with
all nine stages, no unexpected attributes and no events. This verifies failure
telemetry, not successful Bedrock planning, model usage or AWS deployment.

## GitHub, AWS, Bedrock and Databricks status

| External milestone | Status | Actual blocker/evidence |
| --- | --- | --- |
| Public GitHub repository and prior hosted Actions | **PASS** | Verified prior hosted baseline [34370908568](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34370908568), commit `712fda9c5fd690fc8146009d7104e155b7290713`; wheel revision hosted CI PENDING. |
| CDK bootstrap | **PASS / PERFORMED** | Tokyo `CDKToolkit` is CREATE_COMPLETE; all 11 resources and 25 control checks passed after explicit approval. No extra trusted accounts or runtime IAM change. |
| Lambda quota increase | **PENDING** | Approved request for 1,001 submitted with Support enabled; provider `CASE_OPENED`, last-observed applied/unreserved capacity 10, application reservation unchanged at three. |
| AWS application deployment | **NOT TESTED / BLOCKED** | Stack absent; Lambda capacity blocks completion. Default unconnected Amplify omits Git secrets; creation is unverified and a working hosted frontend still requires Git authorization/build. |
| AWS smoke | **NOT TESTED** | No deployed application to exercise; bootstrap and template checks do not establish runtime/auth/audit behavior. |
| Bedrock discovery/access preflight | **PASS** | Tokyo text-model discovery and exact Nova Lite access metadata verified; this does not establish inference capacity. |
| Previous Bedrock qualification | **FAIL** | Both single-case attempts failed with provider throttling; last-observed regional Nova Lite runtime quotas remain zero. Failed artifacts and incomplete usage are preserved. |
| Nova Lite capacity inquiry | **SUBMITTED / PENDING** | Basic Support case confirmed; provider `Unassigned`, stored type Account, category Service Quotas, General. No quota approval or capacity restoration verified. |
| Live Bedrock evaluation | **NOT TESTED** | No successful qualification, three-case smoke or twenty-case suite. No model calls followed the zero-capacity finding. |
| Databricks authentication / managed Volume / wheel smoke | **PASS** | Expected-user OAuth U2M; one managed Volume, verified wheel hash and one successful installed-package smoke in Free Edition. |
| Databricks native pipeline and exact live tables | **PASS** | First migrated wheel execution succeeded; actual Bronze 20, Silver 18, rejected 1 and Gold 3 independently verified. Prior source-file failures preserved. |
| Databricks Gold / real adapter / API SME scenarios | **PASS** | Four real SDK adapter reads; citations, mandatory review, missing/stale/absent behavior and refusal boundaries verified. Browser complete/missing/stale/refusal checks also PASS; initial safe-abstention failure preserved. |
| Databricks production identity isolation / real denial or outage | **NOT TESTED** | Developer identity used; injected malformed/outage tests are local contracts, not live access-control or infrastructure failure evidence. |

The authorized personal sandbox was verified in `ap-northeast-1`; public evidence
omits account and principal identifiers. Automatic approval review initially
rejected bootstrap's persistent administrator roles; the user subsequently
explicitly approved that exact boundary. Bootstrap completed at 13:18:44 UTC and
the deployed template and actual resources passed verification at 13:21:27 UTC.
The five bootstrap IAM roles are account-global; regional resources and the stack
are in Tokyo. No additional account was trusted. The application stack is absent.

The earlier Lambda request without Support remains historical **NOT_APPROVED**
evidence. The newly authorized request reached `CASE_OPENED` at the 14:15:45 UTC
check, while applied concurrency remained ten. The separate Nova Lite inquiry
was confirmed at 14:27:47 UTC; its Basic Support submission did not change quotas.
The [escalation evidence](docs/validation/support-escalation-2026-09-09.json) and
[capacity/dependency review](docs/deployment-capacity-review.md) distinguish these
states. No paid plan or trial, new paid resources, region/profile switch, runtime
IAM change or reservation change occurred during these capacity/Support steps.
No further model calls were made after zero capacity was established. Bootstrap
and earlier failed qualification evidence remain unchanged; no Databricks
workspace operation was run during those earlier AWS capacity/Support steps.

The [AWS record](docs/cloud-validation.md), [deployment security review](docs/aws-deployment-review.md),
[Bedrock runbook](docs/milestone-4-bedrock.md) and [Databricks validation](docs/databricks-validation.md)
give the remaining setup. Earlier milestone records describe historical states.
Cloud integration tests remain separate from credential-free PR CI.

## Estimated cost

Local/container inference cost is $0 because those workflows use no model.
Failed Tokyo qualification usage and cost are **unavailable/incomplete**; their
reported zero is not a billing measurement. The two failed request latencies were
2,849.472 ms and 3,145.194 ms, not a successful-model latency distribution.

Actual Tokyo standard regional Nova Lite rates were verified in the
[versioned AWS price catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/20260901205051/ap-northeast-1/index.json):
$0.072/million input and $0.288/million output tokens. An illustrative 1,500 input
+ 150 output request would cost $0.0001512, or $1.512 per 10,000 requests,
excluding platform costs. This is an estimate, not a measured bill.

Infrastructure costs depend on Lambda duration, API traffic, S3/DynamoDB storage, CloudWatch, Amplify/Cognito and Databricks compute/warehouse usage. The optional $25 account-wide budget is an alert, not a spend cap. Retained resources can cost money after stack deletion. [COST.md](COST.md) explains assumptions and drivers.

The 11 bootstrap resources are deliberately **kept for the planned sandbox
deployment**. The S3 bucket and ECR repository were empty when verified; no
provisioned compute or customer-managed key was created. No actual AWS bill was
measured. Asset storage, versions and requests can incur costs when used. The
[bootstrap cleanup procedure](docs/cdk-bootstrap.md) inventories resources before
deletion and separately handles the retained versioned bucket. Application
resources and an AWS-hosted interview demo have not been deployed.

The pending Lambda quota request and Basic Support inquiry provision no running
capacity. No paid Support plan, trial, provisioned throughput or new paid resource
was purchased during this milestone. Any later application/model usage remains
billable; pending cases are not evidence of available capacity or a $0 AWS bill.

The Databricks continuation used user-confirmed Free Edition, the existing catalog
and existing SQL warehouse. It added one managed artifact Volume in the synthetic
schema and migrated the unscheduled job to the verified wheel. Real serverless
execution and SQL reads consumed the Free Edition allowance; no paid trial,
payment, edition change, external storage or paid-resource purchase occurred.
Smoke/pipeline and query timings were measured; an actual metered dollar amount
was not. The existing 2X-Small serverless warehouse was RUNNING at final inspection
with its unchanged ten-minute auto-stop setting. The earlier stopped-warehouse/no-SQL observation applies only to the
failed source-file milestone. See [cost boundaries](COST.md) and
[retained resources/cleanup](docs/databricks-validation.md).

## Unresolved issues and security limitations

- AWS identity and bootstrap are verified; Lambda approval and the Nova Lite capacity response are pending. Applied Lambda capacity and last-observed zero Bedrock quotas still block deployment/live validation. Amplify Git authorization blocks a functioning hosted frontend, not secret resolution in the default unconnected template. The Databricks wheel pipeline and real SDK/API integration passed separately; the underlying Workspace Files read issue remains unresolved, and production isolation is unverified. Offline contracts and hosted CI do not establish external integrations.
- Pinned GitHub actions emit a non-blocking Node.js 20 runtime deprecation warning; the warning remains unresolved.
- Keyword routing and heuristic injection/PII checks can miss new/multilingual attacks. Quote/hash correspondence does not establish truth or applicability.
- S3's 60-second cache can delay revocation. Source/Gold hashes do not authenticate a publisher that can replace both content and hash.
- Databricks publication uses bounded driver-side computation for synthetic data. Gold-last writes are not an atomic transaction across tables. A separate production Gold-only identity, effective permission isolation and reconciliation remain unverified; successful deployment does not establish them.
- Combined slow Bedrock/Databricks calls or cold sequential S3 reads can exceed Lambda's 28-second deadline; hard termination can prevent final audit/trace completion. Cross-service deadline propagation is not implemented.
- Review is a routing flag/event, not a staffed approval process. Financial actions and customer writes do not exist. DynamoDB application append semantics are not WORM retention; runtime general egress and alarm ownership need review.
- Moving base-image tags, unhashed Python locks and unperformed OS image scanning/signing remain supply-chain gaps. Framework CSP permits required inline content.

## Next steps and recommended interview sequence

Finalization performs only documentation review, privacy/secret scans and GitHub
publication/CI. No additional AWS account, resource or model actions are authorized
while the two existing capacity dependencies are pending. The following are
future milestones; any new paid resources require separate authorization.
The authorized Databricks wheel continuation has passed native publication and
real SDK/API and browser verification. The new hosted CI result is pending;
no additional pipeline retry is needed. Preserve the earlier source-file and
initial browser failures.

1. Update the pinned GitHub actions for the Node.js 20 runtime deprecation in a separate maintenance change, then verify a new hosted run. Publication and the original hosted CI milestone are complete.
2. Follow the existing Lambda Support case and verify applied quota before deployment; resolve the Amplify GitHub connection for a functioning frontend. Revalidate identity and diff, use the verified Tokyo bootstrap, deploy, publish corpus and configure the Cognito demo session within the approved scope. Execute make aws-smoke and preserve real resource/auth/audit evidence.
3. Follow the submitted Nova Lite inquiry and verify usable Tokyo-only inference capacity before any new model request; then repeat one qualification, the three-case smoke and unchanged twenty-case suite. Preserve prior failures and compare actual usage, cost, latency and quality with the deterministic baseline.
4. Complete hosted CI for the wheel change. In a separately authorized production-readiness milestone, verify a Gold-only identity, denied-access and real outage behavior, reconciliation and deadline handling. Preserve failed source-file runs and successful wheel evidence; investigate the original mount issue without calling it a confirmed platform bug.
5. For institutional use, complete [production-readiness gaps](PRODUCTION_READINESS.md), including independent Japanese policy/privacy/model-risk review.

Demo: **business problem → architecture → cited onboarding → malicious approval refusal → SME missing/stale review → deterministic DTI → evaluation/failures → honest cloud/data-platform status → production gaps**. The [timed interview script](docs/interview-demo.md) takes 3–5 minutes.

Native preview: http://127.0.0.1:3000; API: http://127.0.0.1:8000. Restart with make api/make web or their Windows task equivalents.
