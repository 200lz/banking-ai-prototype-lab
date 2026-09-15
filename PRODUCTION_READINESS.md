# Production readiness

**Status: functional synthetic portfolio prototype; not approved for real financial
operations.** Tokyo AWS bootstrap and application deployment passed. Lambda
capacity is RESOLVED: applied 1000, reservation three and post-deployment
unreserved capacity 997 during deployment. Legitimate scoped Cognito OAuth and
all nine infrastructure-only smoke checks passed, including the deterministic
refusal, DynamoDB audit and CloudWatch correlation with zero model use. Required
MFA and all-route unauthorized rejection were verified within their recorded
scope. The first smoke exposed delayed API access-log delivery; only the bounded
developer verifier was corrected. Application and bootstrap cleanup subsequently
passed; regional concurrency returned to 1000/1000. One automatic SYSTEM recovery
backup remains until October 20. See [final evidence and disposition](docs/final-validation-cleanup.md).
Previous live qualification attempts failed with provider throttling; the three
selected regional quotas were still zero on September 15. The Nova Lite capacity
inquiry is pending and live evaluation remains NOT TESTED. See
[actual AWS scope](docs/aws-deployment-resumption.md). Databricks Free Edition validation
passed with a managed-Volume wheel, real native tables, governed Gold adapter and
browser SME review. Earlier Workspace Files failures and one initial browser lookup
abstention remain recorded; their underlying causes are unresolved. See
[actual workspace evidence](docs/databricks-validation.md).

| Area | Implemented and verified scope | Required before real use |
| --- | --- | --- |
| Workflow | Nine-stage controller, five baseline tools plus governed financial_profile_tool, typed responses | Institution-approved scope and operating model |
| Financial analytics | Synthetic Bronze/Silver/Gold, Decimal formulas, provenance, missing/stale flags, local and Databricks adapters | Institution-approved and independently reconciled formulas, separate governed publisher and Gold-only runtime grants; real synthetic workspace execution passed |
| Evidence | Exact full-sentence citations, hashes, versions, conflicts, access filtering; real encrypted S3 corpus publication and byte verification | Signed ingestion, ownership, freshness SLAs, applicability and entitlement rules |
| Model | Real Strands/Bedrock adapter, bounded typed plan, SDK construction/contract tests | Live model evaluation, held-out expert cases, model-risk approval |
| Identity | Real Cognito scoped OAuth/PKCE, required-MFA configuration, authenticated refusal and unauthorized API rejection | Enterprise IdP, joiner/mover/leaver controls, complete session lifecycle and broader effective entitlement tests |
| Human review | Mandatory routing with JSONL persistence; conditional DynamoDB event adapter | Staffed review queue, reviewer identity, approval reasons, SLA and segregation of duties |
| Privacy | Synthetic-only corpus, example redactor, content-free telemetry | Approved DLP, data inventory, purpose/retention/residency controls and privacy assessment |
| Security | Allowlisted capabilities, restrictive IAM, schema/abuse tests, dependency audits | Threat validation, penetration testing, supply-chain attestations, continuous attack evaluation |
| Resilience | Error abstention, concurrency bounds, timeouts, audit failure blocks output | Load/failure/chaos tests, dependency budgets, backups/restore drills, RTO/RPO |
| Observability | OTel parent/step/tool spans, latency/tokens/cost, Lambda audit mirror and flush; real correlated runtime audit and API access records, including measured delivery delay | Production remote OTel exporter, actionable alerts, staffed on-call ownership and SLOs |
| Audit | Real correlated DynamoDB events; encrypted table with PITR, TTL and deletion protection verified before cleanup | Tamper evidence, regulated retention, independent audit access, replay/reconciliation design |
| Delivery | Locked dependencies, Docker/Compose and hosted CI; real Tokyo CREATE_COMPLETE, nine-check smoke and scoped resource cleanup | Working hosted SSR, image signing, staged release and rollback exercise; final publication requires its own hosted CI |
| Cost | Model estimate and incomplete-cost flag, verified Tokyo model rates, optional AWS budget definition | Measured usage envelope and recurring cost ownership |

Current container, hosted CI, cloud and data-platform verification is recorded in
the [authoritative matrix](docs/verification-matrix.md). A local Docker or SDK
contract pass does not establish regional cloud behavior or production readiness.
Implementation [hosted run 34937568647](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34937568647)
passed all 22 steps at `8a49bf849fcae5006f5c1ac529120224f6c0badf`; the actual
artifact was `evidence-and-infrastructure`. This does not establish a PASS for the
subsequent status-update commit.

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
