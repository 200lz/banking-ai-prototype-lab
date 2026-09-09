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
| 61-case deterministic regression | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE |
| Single-case live-model qualification and retry | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | FAIL | NOT APPLICABLE |
| Twenty-case live-model qualification | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED | NOT TESTED | NOT APPLICABLE |

## Evidence supporting PASS

- **Latest previously verified hosted run:** [34346854721](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34346854721)
  passed at commit `6f24ef61fcf5dcbb7d3906fc38aa3c124b436b19`. The following original-run details remain historical
  evidence. A hosted run covering the subsequent AWS evidence and harness change
  has not yet been recorded here.
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
| GitHub repository publication and hosted Actions | PASS | Latest previously verified run [34346854721](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34346854721), commit `6f24ef61fcf5dcbb7d3906fc38aa3c124b436b19`; earlier detailed hosted evidence above. Subsequent changes await a new hosted result. |
| AWS sandbox deployment and smoke | NOT TESTED | Tokyo identity/discovery/target synth/diff PASS. Bootstrap was not executed after automatic approval review rejected persistent administrator-capable roles. Lambda applied concurrency remains 10; quota request 1001 NOT_APPROVED. Amplify connection missing. |
| Live Bedrock twenty-case evaluation | NOT TESTED | Single-case qualification and diagnostic retry FAIL with `ModelThrottledException`; relevant Nova Lite quotas zero. Three-case and twenty-case phases did not run; token/cost reporting incomplete. |
| Databricks workspace pipeline and Gold read | NOT TESTED | No configured workspace, unified authentication, SQL warehouse/catalog/schema or CLI. |

The verified Node.js 20 action-runtime warning is **NON-BLOCKING**: GitHub forced
the pinned actions onto Node.js 24 and the job passed. Action pins were not
changed, and no warning fix is claimed.

See the [hosted CI evidence](../REPORT.md#github-hosted-ci-pass), [AWS preflight](cloud-validation.md),
[Bedrock runbook](milestone-4-bedrock.md), and
[Databricks validation](databricks-validation.md) for exact next actions.
Authentication was not inferred from an installed connector or elapsed time.
The earlier [GitHub milestone](milestone-2-ci.md) is a historical pre-publication
record; its GitHub NOT TESTED status is superseded by the verified run above.
