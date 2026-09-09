# Backend implementation notes

The backend is a working deterministic controller with a replaceable planner. Local
mode is an extractive baseline; no Bedrock call or cloud deployment has been made.
The agent never receives an execution, approval, transaction, customer-write,
shell, or arbitrary network capability.

## Architecture decisions

- Requests have only question and optional typed calculation. Unknown fields fail
  validation, so a caller cannot grant themselves a role or submit a tool plan.
- Five controller-owned tools have separate strict schemas. Numeric operations use
  bounded Decimal operands, explicit actual/365 interest, and HALF_UP rounding.
- The local planner selects permitted excerpt IDs. The Strands planner also
  returns only bounded IDs and booleans through a Pydantic structured output model.
  It receives zero business tools. The controller owns retrieval, arithmetic,
  guardrail, citation, and human review decisions.
- Quotes must match a complete sentence or entire current source, the claim must
  equal its quote, and the SHA-256 must still match at document fetch and final
  verification. Selecting a sentence preserves the other sentences in that source
  to avoid dropping a caveat. A token budget cannot truncate a source paragraph.
- Retrieval results are filtered by intent topic and classification. Public sources
  add context, but a request without a current synthetic policy abstains. Multiple
  distinct active synthetic policies in a topic cause conservative abstention;
  explicit supersedes relationships resolve versions, without model adjudication.
- PII examples redact emails, SSNs, and account-like numbers before retrieval or
  model input. Suspicious sources are quarantined instead of repaired by an LLM.
- Lambda gateway mode checks verified JWT subject/scope in Mangum's ASGI event;
  ordinary HTTP headers cannot supply that context. Local auth refuses Lambda.
- A parent OpenTelemetry workflow span contains nine stage spans and tool spans.
  Only application-owned content-free spans can be exported; Strands automatic
  spans are excluded because they may contain prompts/evidence. The parent records
  model/retrieval/overall latency, token usage, cost, risk, and review metrics.
- JSONL audit defaults to `.runtime/audit.jsonl`. DynamoDB records use request ID
  partition key, timestamp/UUID sort key, configurable expiry, and a conditional
  put preventing accidental overwrite. Audit failures prevent API success.
- Model configuration uses an explicit Bedrock model ID, 600 output tokens, two
  model calls maximum, no SDK retry strategy, and 2s connection/8s read timeouts.
  Cost uses accumulated SDK token usage and configurable illustrative per-million
  rates. Model errors explicitly mark cost incomplete; a zero lower bound does not
  mean no tokens were billed.

## Failures found and corrected

The first 61-case evaluation failed on missing-evidence escalation, DTI review,
unrecognized personal-information/assistant wording, and a role-spoofing document
that passed a narrower injection detector. Added general missing/unknown/incomplete
evidence rules, obligatory DTI review, broader intent synonyms, and normalized role
markers, with regression cases. No dataset strings or expected answers were added
to the runtime. The independent evaluation then passed all 61 cases.

A citation substring check could verify text after dropping its preceding negation.
Verification now requires a complete sentence or complete document, with a
regression test for this attack. Model-selected source caveats are retained.

Mypy identified Decimal's special exponent types and a nullable environment-path
inference. Both are corrected. Focused backend/API regression tests passed (66
tests after the adversarial review), plus Python lint/type checks. The final
Lambda audit-mirroring regression adds one test, for 67 backend/API tests; the
targeted workflow module passed after that change.
The Starlette/AnyIO dependency emits a harmless deprecated BlockingPortal alias
warning during TestClient tests; production routing does not use TestClient.

The independent adversarial review additionally found and fixed PII leakage through
source metadata and unknown validation-error field names, public-only model source
selection despite available internal policy, partial coverage of multi-topic
requests, dropped calculation requests, coerced plan booleans, extreme zero
exponents, and loss of incomplete-cost status on otherwise successful plans.
Decimal quantities must use strings or integers; binary JSON floats and booleans
are rejected. SDK logging is suppressed at the Strands/AWS/HTTP logger namespaces
because SDK DEBUG and error records can contain raw payloads. Application audit
events retain safe failure codes. Full ingress intent is classified inside the
deterministic policy boundary so redaction expansion cannot hide a trailing attack;
retrieval and model inputs receive redacted text.

## Limits to retain in portfolio documentation

This is not an institutional policy engine, complete DLP system, or robust semantic
injection detector. English lexical intent and heuristic source checks can miss
novel or multilingual attacks. Exact citation validity proves provenance, not that
a policy is correct, current in the real world, or relevant in every scenario.
Conflict detection conservatively flags different active texts even if compatible.
Human review is a persisted routing flag, not a staffed case-management integration
or completed approval. The local audit file is not immutable or encrypted by this
application; DynamoDB conditional inserts are application semantics, not WORM.
No live Bedrock quality, tokens, cost, AWS latency, Cognito login, or cloud traces
have been measured. Instrumentation filters trade SDK-internal detail for privacy.
Local auth relies on loopback publication in Compose and must not be internet-bound.
Stage `status=ok` means the controller completed that stage, including a deliberate
fail-closed recovery; response risk flags and the parent span describe recovered
planner/retrieval failures. Tool errors carry an explicit error status. SDK logging
suppression is process-wide, an intentional tradeoff in this dedicated prototype.
Lambda audit mirroring uses a dedicated `banking.audit` INFO handler, also enabled
with `AUDIT_CONSOLE=1` outside Lambda. It outputs the same allowlisted JSON and does
not enable verbose root or SDK logging. The source adapter retains its 60-second
warm S3 snapshot; repeated gets verify that snapshot rather than guaranteeing
immediate S3 revocation visibility.

## Official SDK references checked during implementation

- [Structured output](https://strandsagents.com/docs/user-guide/concepts/agents/structured-output/)
- [Bedrock model provider](https://strandsagents.com/docs/user-guide/concepts/model-providers/amazon-bedrock/)
- [Metrics](https://strandsagents.com/docs/user-guide/observability-evaluation/metrics/)
- [Traces](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/)

Current installed SDK signatures and actual Agent construction are also checked
locally. The adapter invocation/token test uses a fake result and is explicitly
not a live Bedrock integration test.
