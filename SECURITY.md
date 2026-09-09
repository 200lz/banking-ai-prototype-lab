# Security

## Governed financial analytics boundary

The sixth capability, `financial_profile_tool`, accepts only a syntactically
restricted fictional company ID. It reads a published Gold profile through a
replaceable adapter. Raw financial rows, profile values, SQL, workspace credentials
and calculation operands are excluded from the model's structured payload.
Numbers voluntarily written in the question remain subject to the example
redactor's limitations.

The Databricks adapter fixes its SQL and uses a bound company parameter, one
bounded inline result and a Gold-only schema. It rejects unexpected columns,
duplicate companies, hash mismatch, oversized results and incomplete statements.
Failures produce a generic unavailability response and mandatory review. Production
permissions must separately enforce SELECT on the approved Gold table and deny
Bronze/Silver access; application checks do not grant or prove those permissions.

Gold hashes establish snapshot correspondence, not trusted publication: a writer
that can replace both data and hash can change the underlying facts. Formula
versioning, source IDs, data quality and business-period freshness make review
possible; a real institution needs approved publishers, access policies and
independent reconciliation. No profile or ratio authorizes lending.

This is a synthetic portfolio prototype, not a regulated production system or a
claim of security certification. There are no customer-write or financial-action
capabilities. The strongest safety boundary is capability absence, not a prompt.

## Explicit trust boundaries

| Boundary | Control | Remaining limitation |
| --- | --- | --- |
| User to API | Strict Pydantic fields, 16 KiB body limit, bounded question, same-origin proxy, bounded concurrency | Local mode has no identity; keyword intent analysis is incomplete |
| Browser to cloud | Server-side Cognito code/PKCE, state, HttpOnly secure cookie, API Gateway scope | Live identity lifecycle and hosted login require account validation |
| Document to controller | Classification/version filters, injection checks, source quarantine | Heuristics can miss novel attacks or reject legitimate prose |
| Model to tools | Typed bounded plan, known evidence IDs, fixed five-tool registry | Model may omit useful evidence or over-escalate |
| Evidence to answer | Full-sentence exact quote, source ID/version/hash re-verification | Source matching does not establish truth, legal applicability, or freshness |
| Runtime to AWS | Scoped S3 reads, regional model invocation, audit PutItem, no customer systems | Deployment identity is more privileged; AWS data plane untested here |
| Runtime to logs | Allowlisted audit metadata; prompts, operands, bodies and SDK spans excluded; SDK payload loggers suppressed | Broader platform instrumentation must be separately reviewed |

## Prompt injection and unsafe intent

User and document text are data. Unicode normalization and detection patterns
catch common role spoofing, instruction overrides, secrets requests, exfiltration,
and dangerous execution requests. Retrieved injection is quarantined and forces
abstention/review; it never reaches model planning. Conflicting active synthetic
policies also force review. The model cannot change classifications, invoke tools
by name, introduce evidence IDs, supply calculation operands, or waive review.

These checks are layers, not complete injection prevention. An undetected poisoned
policy could still be quoted as a recommendation. A hash authenticates content
relative to the manifest, not its author. Real use requires reviewed ingestion,
signed provenance, independent semantic policy checks, source lifecycle controls,
and continuous red-team evaluation.

## Data handling

Only `public` and `internal` documents are available to this prototype audience;
`restricted` data is filtered from both search and get. There is no client role or
classification field. Real deployment needs per-user/per-document entitlements,
purpose limits, jurisdiction, consent and residency controls.

The redactor demonstrates email, SSN and account/card-style identifier handling before
model/retrieval use. It is not comprehensive: names, addresses, multilingual text,
novel formats, context and false positives require an approved DLP system. Inputs
must remain synthetic even when this layer is enabled. Malformed API inputs do
not echo the submitted PII or unknown user-controlled field names in validation
responses. Policy source text and decoded metadata, including titles, versions,
URLs, tags and IDs, are checked for detected PII and rejected rather than altering
their evidence text/hash. Full ingress intent is analyzed inside the deterministic
policy boundary; that tool never logs its arguments.

## Tools and approval

Only `policy_search`, `document_retrieval`, `deterministic_calculation`,
`risk_classification`, and `citation_verification` are dispatchable. Unknown tools
and extra fields fail schema validation. No runtime tool can run a shell, read
arbitrary paths, access arbitrary URLs, write records, trade, transfer, approve
credit, or skip approval. Developer Make/CDK scripts are not imported by the agent.

`human_review_required` is a conservative decision to seek review. It is never
accepted as an input and cannot authorize an action. The portfolio has no real
reviewer queue, approval completion, or financial execution integration.

## Audit and telemetry

Audit metadata has an explicit allowlist and never includes prompts, documents,
full request/response payloads, calculation operands, exception messages, or auth
tokens. Each stage, tool, review decision and completion record shares a request
ID. DynamoDB writes use a uniqueness condition and the runtime has no update or
delete grants. This is append-only application behavior, not WORM storage:
administrators can still modify data and there is no cryptographic audit chain.
The example retention defaults are operational choices, not legal retention rules.

OTel exports only controlled `banking.*` spans; Strands automatic content spans
are filtered. Strands, boto3, botocore and urllib3 payload loggers are suppressed
process-wide; application audit codes retain failure visibility. A dedicated
`banking.audit` INFO handler mirrors allowlisted records in Lambda or when
`AUDIT_CONSOLE=1`; local JSONL and cloud DynamoDB remain the persistence targets.
Audit failure suppresses the normal response. OTel export itself is
best effort and must not be mistaken for guaranteed durable evidence. Add regulated
retention, signed event integrity, audit access separation and SIEM integration.

## Verification and reporting

Unit and integration tests cover source injection, missing/restricted/changed
documents, citation forgery, negation stripping, tool/schema rejection, PII,
mandatory review, gateway claims, and redacted telemetry. CI runs Bandit, pip-audit,
npm audit, evaluation gates, and CDK security assertions. This is not penetration
testing or a full dependency supply-chain assessment. See the
[threat model](docs/threat-model/README.md) and [readiness gaps](PRODUCTION_READINESS.md).

Report a synthetic reproduction through the repository issue process without
secrets, real identifiers, or third-party data. There is no promise of a staffed
security response service for this portfolio.
