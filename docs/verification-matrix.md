# Authoritative verification matrix

Updated 2026-09-15 JST. Tokyo deployment and all nine authenticated infrastructure
smoke checks passed, followed by verified project cleanup in AWS and Databricks.
One automatic DynamoDB SYSTEM backup remains until October 20; the pre-existing
Databricks catalog and stopped warehouse remain. Cloud PASS rows describe dated
execution, not currently running project resources. PASS means the stated scope
was actually executed. SDK mocks,
offline synthesis, container images and local file adapters never establish a real
cloud/data-platform integration. NOT APPLICABLE means the column does not apply to
that capability; NOT TESTED means an applicable integration was not executed.

| Capability | Local | Docker | AWS | Live LLM | Databricks |
| --- | --- | --- | --- | --- | --- |
| Policy request → governed answer and citations | PASS | PASS | NOT TESTED | NOT TESTED | NOT APPLICABLE |
| Deterministic DTI with provenance | PASS | PASS | NOT TESTED | NOT TESTED | NOT APPLICABLE |
| Prohibited action refusal and human review | PASS | PASS | PASS (authenticated fixed refusal; zero model use) | NOT TESTED | PASS (controller; refusal makes no query) |
| Retrieved-document injection quarantine | PASS | PASS | NOT TESTED | NOT TESTED | NOT APPLICABLE |
| Content-free stage/tool telemetry | PASS | PASS | PASS (nine-stage audit/log correlation) | NOT TESTED | PASS (local API stages/audit with live Gold) |
| Published SME Gold profile → policy-backed review | PASS | PASS | NOT TESTED | NOT TESTED | PASS (real SDK / in-process API) |
| RAW → Bronze → Silver → Gold computation | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | PASS (Volume-backed wheel) |
| Databricks fixed-SQL adapter contract/failure handling | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | PASS reads / injected failure contracts only |
| Browser → API → live Gold | PASS (local Gold) | PASS (local Gold) | NOT TESTED | NOT APPLICABLE | PASS (complete/missing/stale/refusal) |
| Separate Gold-only identity / real permission denial | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED |
| Databricks expected-user authentication and dev bundle validation | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | PASS |
| Databricks unscheduled native job deployment | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | PASS |
| Production web build and API routing | PASS | PASS | NOT TESTED | NOT APPLICABLE | NOT APPLICABLE |
| Stack health, restart, audit persistence and clean shutdown | NOT APPLICABLE | PASS | NOT TESTED | NOT APPLICABLE | NOT APPLICABLE |
| Lambda handler and workflow execution | NOT APPLICABLE | PASS | PASS (fixed refusal through authenticated API) | NOT APPLICABLE | NOT APPLICABLE |
| CDK synthesis and infrastructure security assertions | PASS | NOT APPLICABLE | PASS (actual diff / deployed template and IAM) | NOT APPLICABLE | NOT APPLICABLE |
| Tokyo application CloudFormation deployment | NOT APPLICABLE | NOT APPLICABLE | PASS (34 resources / CREATE_COMPLETE) | NOT APPLICABLE | NOT APPLICABLE |
| Lambda reservation and deployed configuration | NOT APPLICABLE | NOT APPLICABLE | PASS (reservation 3 / regional limit 1000) | NOT APPLICABLE | NOT APPLICABLE |
| Published S3 corpus bytes and manifest | PASS | PASS | PASS (12 documents / 13 objects) | NOT APPLICABLE | NOT APPLICABLE |
| Cognito configuration and gateway JWT/scope validation | PASS | NOT APPLICABLE | PASS (legitimate scoped OAuth and refusal) | NOT APPLICABLE | NOT APPLICABLE |
| Real unauthorized API request rejection | PASS | PASS | PASS (all four routes return 401) | NOT APPLICABLE | NOT APPLICABLE |
| Unauthorized API request → metadata-only CloudWatch access log | NOT APPLICABLE | NOT APPLICABLE | PASS | NOT APPLICABLE | NOT APPLICABLE |
| DynamoDB active state, PITR, TTL and deletion protection | PASS (assertions) | NOT APPLICABLE | PASS | NOT APPLICABLE | NOT APPLICABLE |
| Scoped Cognito OAuth request with correlated audit and logs | PASS (contracts) | NOT APPLICABLE | PASS (real CLI, exact DynamoDB and CloudWatch records) | NOT APPLICABLE | NOT APPLICABLE |
| Approved CDK bootstrap and actual resource/trust verification | PASS (template review) | NOT APPLICABLE | PASS (bootstrap only) | NOT APPLICABLE | NOT APPLICABLE |
| 61-case deterministic regression | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE |
| Single-case live-model qualification and retry | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | FAIL | NOT APPLICABLE |
| Twenty-case live-model qualification | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED | NOT TESTED | NOT APPLICABLE |

## Evidence supporting PASS

- **Tokyo application deployment (2026-09-15 JST): PASS.** Reverified the expected
  same-account non-root SSO identity and `ap-northeast-1`. Actual Lambda limits
  were 1000 concurrent and 1000 unreserved before deployment; reservation three
  was deployed and the unreserved value became 997. After cleanup the regional
  values were 1000/1000. No new quota request was made.
  The actual CDK diff passed 30 controls; deployment completed in 261.937 seconds.
  CloudFormation reached CREATE_COMPLETE with 34 resources, matching the reviewed
  template. Runtime IAM and the single-region model boundary were preserved.
  The safe publisher uploaded twelve documents and the manifest last; all thirteen
  encrypted objects matched their expected bytes. See the
  [deployment record](aws-deployment-resumption.md).
- **AWS authenticated infrastructure smoke: PASS, 9/9 (2026-09-15 JST).** The exact
  reviewed CLI ran after legitimate Cognito authorization-code/PKCE sign-in and
  state verification. All resource/auth checks, fixed refusal with six verified
  excerpts, required review, DynamoDB audit and CloudWatch runtime/API correlation
  passed. Model tokens, model latency and estimated inference cost were zero. The suite
  took 46.25 seconds; response/retrieval timings were 664.390/499.217 ms for one
  observation. See [final evidence](validation/aws-final-validation-2026-09-15.json).
  Normal model workflows and hosted Amplify frontend/SSR remain NOT TESTED.
- **Preserved first authenticated failure:** eight checks passed; the matching
  API access record arrived after the run ended, with 48.201 seconds ingestion lag.
  All sixteen runtime audit records had arrived earlier. The developer verifier
  delivery wait changed to 25 attempts and 120 seconds total sleep; validation,
  application code and runtime IAM were unchanged. The
  [initial run remains FAIL](validation/aws-infrastructure-smoke-initial-failure-2026-09-15.json).
- **AWS scoped cleanup: PASS, with a disclosed SYSTEM backup (2026-09-15 JST).**
  Application CloudFormation deletion completed at 08:54:22 UTC, followed by six
  retained project resources at 08:54:54 UTC. After a bounded dependency review,
  bootstrap deletion completed at 08:59:55 UTC. Independent verification at
  09:00:17 UTC passed 14 application and nine bootstrap absence checks, including
  all seven IAM roles. Corpus/bootstrap object versions and the ECR image were
  removed. One automatic DynamoDB SYSTEM backup remains AVAILABLE until
  2026-10-20T08:54:43.950Z; provider history, SSO and quota configuration remain
  outside scope. This is not a whole-account erasure claim. See
  [cleanup evidence](validation/aws-cleanup-2026-09-15.json).
- **Databricks scoped cleanup: PASS (2026-09-15 JST).** Ownership-checked removal
  and separate verification at 08:58:57 UTC confirmed the dedicated job/bundle,
  four managed tables, wheel, Volume and synthetic schema absent. The existing
  catalog and warehouse remain; the warehouse was STOPPED with no active work
  observed. Historical evidence and local exports were preserved. No new compute,
  pipeline run, paid action or edition switch occurred. The user-confirmed Free
  Edition basis is historical, not a new edition query. See
  [cleanup evidence](validation/databricks-cleanup-2026-09-15.json).
- **Supplemental live infrastructure checks: PASS.** All four API routes returned
  HTTP 401 without credentials. A corresponding metadata-only API Gateway access
  record was verified in CloudWatch. DynamoDB was ACTIVE, with PITR, TTL and
  deletion protection enabled. The synthetic Cognito user was confirmed and TOTP
  enrollment succeeded through the MFA_SETUP challenge. AdminGetUser did not return
  MFA preference metadata; no cause is inferred. The later actual OAuth and
  authenticated request are established separately by the final evidence above.
- **Latest local regression: PASS.** 342 Python/API/infrastructure tests in 57.49
  seconds, including 77 smoke contract tests; 26 frontend tests and all 61
  deterministic cases passed. Ruff checked 58 files, mypy checked 43 source files,
  and Bandit found zero issues across 3,322 lines. Python/web/CDK dependency audits
  passed. [Local evidence](validation/final-local-regressions-2026-09-15.json) links
  the [full 61-case results](../evals/results/final-validation-2026-09-15.json).
  Application behavior and IAM are unchanged.
- **AWS deployment implementation hosted CI: PASS.**
  [run 34937568647](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34937568647)
  passed at commit `8a49bf849fcae5006f5c1ac529120224f6c0badf` on GitHub-hosted Linux.
  Actual `gh` reads verified the push to main, all 22 `quality` steps, and the
  unexpired `evidence-and-infrastructure` artifact (124,794 bytes). See
  [runner/gates/artifact evidence](validation/github-aws-deployment-2026-09-15.json).
  The subsequent status commit `ad9eb001717c7817834e1f2f77b4df9019a3c5af` passed
  [run 34938551581](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34938551581).
  Final validation/publication changes require a new hosted run. Hosted checks are
  credential-free; real authenticated AWS evidence is recorded separately.
- **Verified wheel implementation hosted CI: PASS.** [run 34377575941](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34377575941)
  passed at commit `87e6417d268bf9671820039f5e9c5bb422d82779` on GitHub-hosted Linux.
  All 22 `quality` steps succeeded; actual artifact `evidence-and-infrastructure`
  was present and unexpired. [Runner/gates/artifact evidence](validation/github-databricks-wheel-2026-09-10.json)
  is commit-specific; the badge links to current main. Node action deprecation is
  NON-BLOCKING; action pins remain unchanged.
- **Databricks wheel / pipeline / live SDK and API (2026-09-10 JST): PASS.**
  User-confirmed Free Edition, one managed artifact Volume, independent wheel
  upload/download SHA verification, smoke 33.733 seconds and first migrated job
  94.873 seconds; one attempt each, zero retries. Four bounded real SELECTs
  verified Bronze 20, Silver 18, rejected 1 and Gold 3 with exact cells/provenance.
  Four real SDK adapter reads exercised complete/missing/stale/absent companies
  through FastAPI. Required policy evidence, review and refusal boundaries passed.
  Injected malformed/outage checks do not establish actual workspace failure or
  denied access. Browser complete/missing/stale and credit-refusal scenarios passed;
  the initial safely abstained request remains a preserved failure of unresolved
  cause. No product fix is inferred from a later successful request. See
  [live evidence](validation/databricks-wheel-2026-09-10.json) and
  [validation details](databricks-validation.md).
- **Wheel continuation local regression: PASS.** 314 Python/API/infrastructure
  tests, 26 frontend tests, all 61 deterministic cases, formatting/lint/types,
  Bandit and dependency audits. Real installed-wheel tests run outside the checkout.
- **Actual CDK bootstrap: PASS / PERFORMED.** Explicit user approval cleared the
  prior administrator-role approval blocker. Tokyo `CDKToolkit` reached CREATE_COMPLETE;
  all 11 resources and 25 control checks passed. The deployed template matches
  the review, extra trusted accounts are absent and runtime IAM is unchanged.
  Its September 15 removal is recorded separately above. See
  [inventory/cleanup](cdk-bootstrap.md) and [actual AWS evidence](validation/cdk-bootstrap-2026-09-09.json).
- **Historical local AWS-harness correction:** 294 Python/API/infrastructure tests,
  26 frontend tests, formatting/lint/types and security checks passed; a focused
  70-test harness regression also passed. See [local regression evidence](validation/aws-local-regressions-2026-09-09.json).
- **Authenticated Tokyo preflight:** authorized non-root identity, 62-entry model
  discovery, actual target synthesis and diff passed. This establishes preflight
  only. See [sanitized Tokyo evidence](validation/aws-tokyo-preflight-2026-09-09.json).

- **GitHub Actions: PASS.** Independently queried with `gh`: workflow
  `Quality and safety regression`, [run 34344534926](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34344534926),
  commit `827888ab0d3c82f937d8106b51f8bf04f4a3fcc4` on `main`. Job `quality`
  passed all 22 recorded steps on GitHub-hosted Linux (`ubuntu-latest`, runner
  `GitHub Actions 1000000254`, group `GitHub Actions`). Gates covered dependency
  installation, formatting/lint/types, Python/API/infrastructure/frontend tests,
  evaluation smoke/full gates, security analysis/dependency audits, production
  Next.js build, credential-free CDK synthesis, source/complete-history secret
  scans, fresh Docker build, health, scenarios, telemetry, restart and cleanup.
  Artifact preservation passed; actual artifact `evidence-and-infrastructure`
  (ID `10101336517`, 119,231 bytes) was present and unexpired when checked.
  [REPORT](../REPORT.md#github-hosted-ci-pass) records the artifact digest and
  runner evidence. These checks do not establish AWS, live LLM or workspace execution.
- **Local workflow, safety, arithmetic, adapters and CDK:** executed Python/API/
  infrastructure tests and scoped regressions, with final command/count record in
  [REPORT](../REPORT.md) and [local verification record](validation/local-final.json).
  Tests of fake vendor clients establish contracts only.
- **61-case baseline:** actual full responses, scorer denominators, timings and
  dataset hash in [latest.json](../evals/results/latest.json); earlier continuation
  runs remain separate. Zero model tokens are expected in deterministic mode.
- **Native web/profile:** actual browser scenario and mobile layout results in
  [browser evidence](validation/browser-2026-09-09.json), captured
  [desktop screenshot](demo/sme-workbench.png), frontend build/tests and actual
  same-origin web-to-API requests recorded in REPORT.
- **Local financial pipeline/profile:** [local data-platform record](validation/databricks-local.json)
  and [Databricks validation](databricks-validation.md), including independent
  formula tests and exact reconstruction from the synthetic source file.
- **Docker:** [canonical fresh-build/runtime report](validation/containers-2026-09-09.json)
  records all four built images, health, six scenarios, controlled exporter,
  restart and cleanup. [SME supplement](validation/container-sme-2026-09-09.json)
  matches those exact image IDs and adds the seventh scenario. Its reused-image
  run does not claim a second fresh build. [Milestone report](milestones/01-containers.md)
  explains preserved failures, fixes and security-check scope.

## External integrations

| Integration | Status | Evidence or blocker |
| --- | --- | --- |
| GitHub repository publication and hosted Actions | PASS (previous checkpoint) | Implementation run 34937568647 and subsequent [status run 34938551581](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34938551581), commit `ad9eb001717c7817834e1f2f77b4df9019a3c5af`, passed. Final validation changes require their own hosted PASS. |
| CDK sandbox bootstrap | PASS / PERFORMED; subsequently removed | Approved standard stack reached CREATE_COMPLETE in Tokyo, 11 resources, 25 passing checks; no extra trusted accounts or application runtime IAM changes. Cleanup PASS below. |
| Lambda Tokyo quota | RESOLVED | Total/unreserved 1000/1000 before deployment, 1000/997 with reservation three, and 1000/1000 after function removal. No new request for 1001. Earlier Support case status is historical and was not re-queried. |
| AWS sandbox application deployment | PASS; subsequently removed | Tokyo CloudFormation reached CREATE_COMPLETE, 34 resources, reviewed template and unchanged runtime IAM verified. Amplify was an unconnected shell; working hosted SSR remains NOT TESTED. |
| AWS infrastructure smoke | PASS (9/9) | Real reviewed CLI after legitimate scoped Cognito OAuth; fixed refusal, six verified excerpts, required review and exact DynamoDB/CloudWatch correlation. Zero model usage; normal model smoke NOT TESTED. |
| S3 corpus publication | PASS | Twelve documents plus manifest uploaded with full validation and manifest last; all thirteen encrypted objects independently matched expected bytes. |
| Lambda / API Gateway / Cognito | PASS | Reservation three and required Cognito MFA retained; all four routes returned 401 without credentials. Actual OAuth/PKCE and the scoped JWT-protected fixed refusal passed. |
| DynamoDB / CloudWatch | PASS (configuration and authenticated correlation) | Exact refusal audit, nine controller stages, tools/review metadata, runtime logs and matching API access log verified. First delivery-wait failure preserved separately. |
| AWS application cleanup | PASS with disclosed SYSTEM backup | Stack and six retained resources removed; 14 independent absence checks passed. One automatic DynamoDB recovery backup remains until October 20; [exact scope](validation/aws-cleanup-2026-09-15.json). |
| CDK bootstrap cleanup | PASS | Following application deletion and reviewed dependencies, stack/assets/ECR/roles/parameter removed; nine independent absence checks passed. |
| Databricks project cleanup | PASS | Dedicated job/bundle, four tables, wheel/Volume/schema absent. Existing catalog and STOPPED warehouse preserved; no active work observed; [exact scope](validation/databricks-cleanup-2026-09-15.json). |
| Bedrock discovery | PASS | Authenticated Tokyo discovery returned 62 models; selected Nova Lite access metadata AUTHORIZED/AVAILABLE. Metadata does not establish inference success. |
| Bedrock qualification | FAIL (previous attempts) | Single-case qualification and diagnostic retry failed with ModelThrottledException. All three relevant Tokyo Nova Lite quotas were re-queried at zero on 2026-09-15. No invocation after the zero-capacity finding; failed token/cost reporting incomplete. |
| Nova Lite capacity inquiry | SUBMITTED / PENDING | Last verified Basic Support state: Unassigned, Account / Service Quotas, General, severity General question. Support was not re-queried this milestone; current zero quotas establish no usable capacity. No paid plan or capacity purchase. |
| Live Bedrock twenty-case evaluation | NOT TESTED | Three-case smoke and twenty-case phases did not run after failed qualification. |
| Databricks authentication, managed Volume and wheel smoke | PASS | Expected-user OAuth U2M, one managed Volume and independently verified wheel; smoke completed once in Free Edition. |
| Databricks native pipeline and exact live tables | PASS | First migrated wheel run passed in 94.873 seconds; actual rows, metrics and hashes verified by four SELECTs. Prior source-file failures remain preserved. |
| Databricks Gold read, real adapter and API scenarios | PASS | Four live reads verified complete/missing/stale/absent behavior; policy evidence, mandatory review and controller refusal passed. Browser complete/missing/stale/refusal PASS; initial safe-abstention failure preserved. |
| Databricks production access isolation and actual denial/outage | NOT TESTED | Developer identity used; malformed/tampered/outage cases used injected clients. |

The [support-capacity milestone record](validation/support-capacity-milestone-2026-09-09.json)
preserves the 2026-09-09 submission states and that milestone's AWS freeze. The
user subsequently authorized the existing Tokyo application deployment after
Lambda capacity changed externally. The 2026-09-15 applied quota and successful
deployment supersede the earlier Lambda/application blockers. No paid Support
plan, region change, runtime IAM weakening or reservation change occurred. Nova
Lite remains a separate capacity dependency; no model invocation was retried.

The [earlier Databricks record](validation/databricks-workspace-2026-09-10.json)
preserves two failed source-file runs, each with two automatic task attempts,
lasting 71.903 and 104.309 seconds before RAW/schema writes. Later read-only
inspection confirmed Workspace Files support, file types, paths and permissions.
Runtime Workspace Files reads failed repeatedly; switching the job artifact
boundary to a packaged wheel on a Unity Catalog Volume avoided that dependency.
The provider root cause remains unresolved; no confirmed platform bug or Free
Edition restriction is claimed. The [wheel continuation](validation/databricks-wheel-2026-09-10.json)
used real serverless execution and SQL reads, with zero AWS calls or LLM
invocations. No trial/payment, edition change or paid-resource purchase occurred.
A separate production Gold-only identity and effective denied-access tests remain
unverified. The 61-case local evaluation does not measure financial-profile or
live-model quality.

The verified Node.js 20 action-runtime warning is **NON-BLOCKING**: GitHub forced
the pinned actions onto Node.js 24 and the job passed. Action pins were not
changed, and no warning fix is claimed.

See the [hosted CI evidence](../REPORT.md#github-hosted-ci-pass), [AWS preflight](cloud-validation.md),
[Bedrock runbook](milestone-4-bedrock.md), and
[Databricks validation](databricks-validation.md) for exact next actions.
Authentication was not inferred from an installed connector or elapsed time.
The earlier [GitHub milestone](milestone-2-ci.md) is a historical pre-publication
record; its GitHub NOT TESTED status is superseded by the verified run above.
