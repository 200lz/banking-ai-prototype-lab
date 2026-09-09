# Authoritative verification matrix

Recorded 2026-09-09. PASS means the stated scope was actually executed. SDK mocks,
offline synthesis, container images and local file adapters never establish a real
cloud/data-platform integration. NOT APPLICABLE means the column does not apply to
that capability; NOT TESTED means an applicable integration was not executed.

| Capability | Local | Docker | AWS | Live LLM | Databricks |
| --- | --- | --- | --- | --- | --- |
| Policy request → governed answer and citations | PASS | PASS | NOT TESTED | NOT TESTED | NOT APPLICABLE |
| Deterministic DTI with provenance | PASS | PASS | NOT TESTED | NOT TESTED | NOT APPLICABLE |
| Prohibited action refusal and human review | PASS | PASS | NOT TESTED | NOT TESTED | NOT TESTED |
| Retrieved-document injection quarantine | PASS | PASS | NOT TESTED | NOT TESTED | NOT APPLICABLE |
| Content-free stage/tool telemetry | PASS | PASS | NOT TESTED | NOT TESTED | NOT TESTED |
| Published SME Gold profile → policy-backed review | PASS | PASS | NOT TESTED | NOT TESTED | NOT TESTED |
| RAW → Bronze → Silver → Gold computation | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED |
| Databricks fixed-SQL adapter contract/failure handling | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED |
| Production web build and API routing | PASS | PASS | NOT TESTED | NOT APPLICABLE | NOT APPLICABLE |
| Stack health, restart, audit persistence and clean shutdown | NOT APPLICABLE | PASS | NOT TESTED | NOT APPLICABLE | NOT APPLICABLE |
| Lambda handler import and direct workflow smoke | NOT APPLICABLE | PASS | NOT TESTED | NOT APPLICABLE | NOT APPLICABLE |
| CDK synthesis and infrastructure security assertions | PASS | NOT APPLICABLE | NOT TESTED | NOT APPLICABLE | NOT APPLICABLE |
| Approved CDK bootstrap and actual resource/trust verification | PASS (template review) | NOT APPLICABLE | PASS (bootstrap only) | NOT APPLICABLE | NOT APPLICABLE |
| 61-case deterministic regression | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE |
| Single-case live-model qualification and retry | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | FAIL | NOT APPLICABLE |
| Twenty-case live-model qualification | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED | NOT TESTED | NOT APPLICABLE |

## Evidence supporting PASS

- **Verified hosted baseline:** [34357464386](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34357464386)
  passed all 22 steps at commit `4c3b1437b1f1caf41ef07b68811be8f8873bc02a`,
  including fresh Docker validation and artifact `evidence-and-infrastructure`.
  The following original-run details remain historical evidence. This baseline
  includes the bootstrap documentation; each later documentation commit requires
  its own hosted result. The README badge links to current main-branch execution.
- **Actual CDK bootstrap: PASS / PERFORMED.** Explicit user approval cleared the
  prior administrator-role approval blocker. Tokyo `CDKToolkit` is CREATE_COMPLETE;
  all 11 resources and 25 control checks passed. The deployed template matches
  the review, extra trusted accounts are absent and runtime IAM is unchanged.
  See [inventory/cleanup](cdk-bootstrap.md) and [actual AWS evidence](validation/cdk-bootstrap-2026-09-09.json).
- **Current local AWS-harness correction:** 294 Python/API/infrastructure tests,
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
| GitHub repository publication and hosted Actions | PASS | Verified baseline [34357464386](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34357464386), commit `4c3b1437b1f1caf41ef07b68811be8f8873bc02a`; all 22 steps and artifact preservation passed. Later documentation requires its own hosted result. |
| CDK sandbox bootstrap | PASS / PERFORMED | Approved standard stack CREATE_COMPLETE in Tokyo, 11 resources, 25 passing checks; no extra trusted accounts or application runtime IAM changes. Kept for planned sandbox deployment. |
| Lambda quota request | PENDING | Approved request for 1001 submitted with Support enabled; provider CASE_OPENED. Last applied/unreserved limit 10; application reservation remains three. Prior no-Support NOT_APPROVED request is historical. |
| AWS sandbox application deployment | NOT TESTED / BLOCKED | Application stack absent. Lambda reservation cannot be configured at last applied quota. Default unconnected Amplify has no missing-secret dependency; working SSR still needs GitHub connection. |
| AWS smoke | NOT TESTED | No deployed application stack or authenticated cloud workflow was exercised. |
| Bedrock discovery | PASS | Authenticated Tokyo discovery returned 62 models; selected Nova Lite access metadata AUTHORIZED/AVAILABLE. Metadata does not establish inference success. |
| Bedrock qualification | FAIL (previous attempts) | Single-case qualification and diagnostic retry failed with ModelThrottledException; last relevant regional quotas zero. No further invocation after the zero-capacity finding; failed token/cost reporting incomplete. |
| Nova Lite capacity inquiry | SUBMITTED / PENDING | Basic Support accepted the Tokyo inquiry; Unassigned, stored Account / Service Quotas, General, severity General question. No paid plan or capacity approval. |
| Live Bedrock twenty-case evaluation | NOT TESTED | Three-case smoke and twenty-case phases did not run after failed qualification. |
| Databricks workspace pipeline and Gold read | NOT TESTED | No configured workspace, unified authentication, SQL warehouse/catalog/schema or CLI. |

The [support-capacity milestone record](validation/support-capacity-milestone-2026-09-09.json)
consolidates these states and links the preserved submission evidence. Finalization
is documentation, privacy checks and GitHub CI only: no further AWS account,
resource, model or quota operations are authorized while both dependencies are
pending. No application resources, paid Support plan, region change, runtime IAM
change or reserved-concurrency change occurred in the support milestone.

The verified Node.js 20 action-runtime warning is **NON-BLOCKING**: GitHub forced
the pinned actions onto Node.js 24 and the job passed. Action pins were not
changed, and no warning fix is claimed.

See the [hosted CI evidence](../REPORT.md#github-hosted-ci-pass), [AWS preflight](cloud-validation.md),
[Bedrock runbook](milestone-4-bedrock.md), and
[Databricks validation](databricks-validation.md) for exact next actions.
Authentication was not inferred from an installed connector or elapsed time.
The earlier [GitHub milestone](milestone-2-ci.md) is a historical pre-publication
record; its GitHub NOT TESTED status is superseded by the verified run above.
