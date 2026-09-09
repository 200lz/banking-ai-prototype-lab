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
| Twenty-case live-model qualification | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED | NOT TESTED | NOT APPLICABLE |

## Evidence supporting PASS

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

| Integration | Status | Observed blocker |
| --- | --- | --- |
| GitHub repository publication and hosted Actions | NOT TESTED | Official CLI installed; no authenticated host or remote. Browser sign-in requested. |
| AWS sandbox | NOT TESTED | STS cannot locate credentials; no profile, region or sandbox identity. |
| Live Bedrock | NOT TESTED | No AWS identity/model access; staged harness is ready but no live run exists. |
| Databricks workspace pipeline and Gold read | NOT TESTED | No configured workspace, unified authentication, SQL warehouse/catalog/schema or CLI. |

See [GitHub milestone](milestone-2-ci.md), [AWS preflight](cloud-validation.md),
[Bedrock runbook](milestone-4-bedrock.md), and
[Databricks validation](databricks-validation.md) for exact next actions.
Authentication was not inferred from an installed connector or elapsed time.
