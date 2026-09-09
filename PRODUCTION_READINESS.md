# Production readiness

**Status: functional local portfolio prototype; not approved for real financial
operations.** AWS bootstrap passed; application deployment is NOT TESTED / BLOCKED.
Previous live qualification attempts failed with provider throttling and the
last regional quotas were zero. Lambda quota and Nova Lite capacity cases are
pending; live evaluation and Databricks workspace execution remain NOT TESTED.

| Area | Implemented and locally checked | Required before real use |
| --- | --- | --- |
| Workflow | Nine-stage controller, five baseline tools plus governed financial_profile_tool, typed responses | Institution-approved scope and operating model |
| Financial analytics | Synthetic Bronze/Silver/Gold, Decimal formulas, provenance, missing/stale flags, local and Databricks adapters | Real workspace execution, independently reconciled formulas, governed publisher and Gold-only runtime grants |
| Evidence | Exact full-sentence citations, hashes, versions, conflicts, access filtering | Signed ingestion, ownership, freshness SLAs, applicability and entitlement rules |
| Model | Real Strands/Bedrock adapter, bounded typed plan, SDK construction/contract tests | Live model evaluation, held-out expert cases, model-risk approval |
| Identity | Cognito/PKCE server flow, gateway JWT scope, MFA CDK settings | Live login verification, enterprise IdP, joiner/mover/leaver controls and session lifecycle |
| Human review | Mandatory routing with JSONL persistence; conditional DynamoDB event adapter | Staffed review queue, reviewer identity, approval reasons, SLA and segregation of duties |
| Privacy | Synthetic-only corpus, example redactor, content-free telemetry | Approved DLP, data inventory, purpose/retention/residency controls and privacy assessment |
| Security | Allowlisted capabilities, restrictive IAM, schema/abuse tests, dependency audits | Threat validation, penetration testing, supply-chain attestations, continuous attack evaluation |
| Resilience | Error abstention, concurrency bounds, timeouts, audit failure blocks output | Load/failure/chaos tests, dependency budgets, backups/restore drills, RTO/RPO |
| Observability | OTel parent/step/tool spans, latency/tokens/cost, dedicated Lambda audit log mirror, bounded span flush and CloudWatch definition | Live exporter verification, actionable on-call alerts, dashboards/SLO ownership |
| Audit | JSONL local; conditional DynamoDB events in cloud design | Tamper evidence, regulated retention, independent audit access, replay/reconciliation design |
| Delivery | Locked dependencies, verified Docker/Compose and hosted CI, synthesized CDK and verified sandbox bootstrap | Image signing, staged application deployment and rollback exercise |
| Cost | Model estimate and incomplete-cost flag, verified Tokyo model rates, optional AWS budget definition | Measured usage envelope and recurring cost ownership |

Current container, hosted CI, cloud and data-platform verification is recorded in
the [authoritative matrix](docs/verification-matrix.md). A local Docker or SDK
contract pass does not establish regional cloud behavior or production readiness.

The S3 adapter intentionally serves a small curated corpus. For enterprise scale,
introduce a retrieval backend with document entitlements applied before search,
semantic and lexical evaluation, signed source versions, transactional publishing,
and evidence revocation. A content hash cannot protect against a compromised
publisher that controls both source and manifest.
The current warm S3 snapshot can defer revocation visibility by 60 seconds; real
policy freshness and emergency revocation requirements need an explicit design.

The combined Bedrock plus Databricks slow path has not been qualified against
Lambda's 28-second deadline. Individual SDK timeouts do not establish a total
request budget, and sequential cold S3 reads can consume that budget. A hard
process timeout fails without a business action, but can prevent final response
and audit/trace completion. Deadline propagation and remote dependency tests are
required before enabling both live services in the deployed request path.

Do not connect core banking APIs to this prototype. Any future write action would
need a separate narrowly scoped service, authenticated reviewer workflow, explicit
business authorization, idempotency, transaction semantics, compensation and
audit controls, and a new reviewed threat model. Current review output is never
an execution authorization.

Release criteria should include a named business owner, compliance/privacy/security
approval, independent evaluation sign-off, tested deployment/rollback, support
runbook, incident response owner, cost owner, and post-release monitoring plan.
