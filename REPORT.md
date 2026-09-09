# Implementation and validation report

2026-09-09. **Functional local and Docker prototype. External integrations remain NOT TESTED where authentication/setup is unavailable.** No real-bank affiliation; all internal policies, companies and financial records are synthetic.

The [authoritative verification matrix](docs/verification-matrix.md) links every PASS to executed evidence. No hosted CI, deployed AWS, live Bedrock or Databricks workspace success is inferred from local tests.

## What was built and extended

- Preserved the FastAPI/Next.js product, nine-stage controller, local/S3 retrieval, five baseline tools, exact citations, guardrails, content-free audit/OTel and bounded Strands/Bedrock planner.
- Verified fresh API, web, collector and Lambda images. Added repeatable container acceptance, real health checks, isolated loopback networking, non-root probes, controlled traces, restart/audit verification and cleanup.
- Added SME Lending Review Copilot: synthetic RAW/Bronze/Silver/Gold, independent Decimal formulas, provenance/hashes, business-period freshness, missing-data handling, strict local/Databricks financial_profile_tool, mandatory review, native bundle/Delta publisher and a working financial evidence UI.
- Added checksum-pinned source/history secret scanning and pinned Actions. CI covers code quality, tests, evaluation, security, web/CDK builds and containers without cloud credentials.
- Added make aws-smoke with nine bounded resource/auth/audit checks and make live-eval with access preflight, one-case qualification, three-case smoke and twenty-case live suite. Mocked contract tests do not establish real integration.
- Added actual browser screenshots, milestone reports, architecture decisions, Japanese institution considerations, threat/readiness documentation and a [3–5 minute interview demo](docs/interview-demo.md).

## Final test results

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
format/lint checks passed afterward. GitHub publication still requires CLI sign-in.

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
| Full cases | 61 | NOT TESTED |
| Mean / median workflow latency | 14.065 / 13.835 ms | NOT TESTED |
| Nearest-rank p95 workflow latency | 19.101 ms | NOT TESTED |
| Mean retrieval latency | 1.966 ms | NOT TESTED |
| Input / output model tokens | 0 / 0 | NOT TESTED |
| Estimated inference cost | $0 | NOT TESTED |

[latest.json](evals/results/latest.json) contains actual per-case responses, denominators and dataset hash. Measurements are in-process on Windows/Python 3.11.5 and exclude HTTP, cold starts and inference. This correlated authored development set is not a held-out benchmark or LLM accuracy result. Financial profiles are covered separately; the original 61 cases do not score them.

The initial failed baseline and two failed container runs remain available. They exposed missed escalation/injection, dropped calculation provenance and restart-port assumptions. New financial tests caught ingestion-time freshness and late unsafe-source profile clearing. Fixes and regressions are recorded in [the development log](docs/development-log.md).

## GitHub, AWS, Bedrock and Databricks status

| External milestone | Status | Actual blocker/evidence |
| --- | --- | --- |
| Public GitHub repository and hosted Actions | **NOT TESTED** | Official CLI 2.100.0 installed and checksum verified, but no authenticated host or remote; browser sign-in requested. No badge or hosted run claimed. |
| AWS deployment | **NOT TESTED** | Signed AWS CLI 2.36.41 installed; actual STS returned “Unable to locate credentials”; no profiles, configured region or sandbox identity. |
| Live Bedrock evaluation | **NOT TESTED** | No model-access API or inference request made. Actual harness exits 2 at missing setup; no fabricated live-results artifact. |
| Databricks workspace | **NOT TESTED** | No configured workspace/auth/warehouse/catalog/schema or CLI; no real job, Delta table or Statement Execution query was run. |

No cloud account was selected, bootstrapped or deployed. No AWS resource or live model/Databricks compute was created. The [AWS record](docs/cloud-validation.md), [Bedrock runbook](docs/milestone-4-bedrock.md), [GitHub milestone](docs/milestone-2-ci.md) and [Databricks validation](docs/databricks-validation.md) give exact remaining setup. Cloud integration tests remain separate from ordinary credential-free PR CI.

## Estimated cost

Observed project inference cost is $0 because local/container workflows use no model. No regional AWS/Databricks bill or live latency was measured. At the explicitly illustrative Nova Lite rates of $0.06/million input and $0.24/million output tokens, 1,500 input + 150 output would cost $0.000126/question or $1.26 per 10,000, excluding all platform costs. The live harness requires recently verified regional rates and reported usage; unknown billed usage stays incomplete.

Infrastructure costs depend on Lambda duration, API traffic, S3/DynamoDB storage, CloudWatch, Amplify/Cognito and Databricks compute/warehouse usage. The optional $25 account-wide budget is an alert, not a spend cap. Retained resources can cost money after stack deletion. [COST.md](COST.md) explains assumptions and drivers.

## Unresolved issues and security limitations

- External authentication/setup prevents verified publication, deployment and live-model/data-platform measurements. Offline SDK contracts cannot prove them.
- Keyword routing and heuristic injection/PII checks can miss new/multilingual attacks. Quote/hash correspondence does not establish truth or applicability.
- S3's 60-second cache can delay revocation. Source/Gold hashes do not authenticate a publisher that can replace both content and hash.
- Databricks publication uses bounded driver-side computation for synthetic data. Gold-last writes are not an atomic transaction across tables. Real permissions, tenant entitlements and reconciliation remain unverified.
- Combined slow Bedrock/Databricks calls or cold sequential S3 reads can exceed Lambda's 28-second deadline; hard termination can prevent final audit/trace completion. Cross-service deadline propagation is not implemented.
- Review is a routing flag/event, not a staffed approval process. Financial actions and customer writes do not exist. DynamoDB application append semantics are not WORM retention; runtime general egress and alarm ownership need review.
- Moving base-image tags, unhashed Python locks and unperformed OS image scanning/signing remain supply-chain gaps. Framework CSP permits required inline content.

## Next steps and recommended interview sequence

1. Complete GitHub CLI browser sign-in; create the authorized public repository, push, inspect the actual hosted workflow and fix any hosted failures.
2. Configure and identify an isolated AWS sandbox/region; run all gates, inspect bootstrap and CDK diff/IAM, deploy, publish corpus and configure demo identity. Execute make aws-smoke and preserve real resource/auth/audit evidence.
3. Verify a low-cost regional model and rates; run make live-eval, retain failures and compare actual token/cost/latency/quality with the baseline.
4. Configure a Databricks development workspace and native bundle, run it, query Gold and exercise the governed adapter with a separate read-only principal. Record real workspace evidence and cost separately.
5. For institutional use, complete [production-readiness gaps](PRODUCTION_READINESS.md), including independent Japanese policy/privacy/model-risk review.

Demo: **business problem → architecture → cited onboarding → malicious approval refusal → SME missing/stale review → deterministic DTI → evaluation/failures → honest cloud/data-platform status → production gaps**. The [timed interview script](docs/interview-demo.md) takes 3–5 minutes.

Native preview: http://127.0.0.1:3000; API: http://127.0.0.1:8000. Restart with make api/make web or their Windows task equivalents.
