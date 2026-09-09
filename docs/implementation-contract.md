# Shared implementation contract

Python packages live directly under services/ and packages/, imported as
`services.agent.*`, `services.api.*`, `packages.retrieval.*`, `packages.policy.*`.
Python 3.11+, Pydantic v2. Root owns packaging, corpus, retrieval, evaluation,
integration, and top-level documentation. Agents own backend, UI, and CDK.

## Retrieval (root implements)

`packages.retrieval.models.Document`: Pydantic model fields `id`, `title`, `text`,
`source_type` (synthetic/public), `source_url` (str | None), `classification`
(public/internal/restricted), `version` (str), `effective_date` (date), `topic`
(str), `tags` (list[str]), `supersedes` (list[str], default []), `sha256` property.
`SearchHit`: `document: Document`, `score: float`.
`Retriever` Protocol: `search(query: str, *, top_k: int = 5,
max_classification: str = "internal") -> list[SearchHit]` and
`get(document_id: str, *, max_classification: str = "internal") -> Document | None`.
`LocalRetriever(documents: list[Document] | None = None)` loads data by default.
`S3Retriever(bucket: str, prefix: str = "corpus/", client=None)` has same methods.
Document topics: onboarding, aml, credit, payments, privacy, complaints,
retention, deposit_insurance, calculation, ai_safety, conflicts.

## API/backend (backend agent implements)

`services.agent.models.AgentRequest`: question: str; calculation optional typed
`{operation: "debt_to_income" | "simple_interest" | "sum", operands: list[Decimal]}`.
Question length 1..4000; no other API input fields. DTI operands [debt, income],
interest [principal, annual_rate_percent, days] using actual/365; sum 1..20 values.
API operands use decimal strings or integers, with magnitude <=10^12 and exponent
-8..12; JSON floats and booleans are rejected. DTI requires nonnegative debt and
positive income for the same period. Interest rate is 0..100 percent and days
0..36500. All plan booleans are strict and unknown fields are rejected.
`services.agent.workflow.Workflow(retriever=None, planner=None, audit=None)` with
`.run(request: AgentRequest) -> AgentResponse`. Local default deterministic.
API: GET /health, POST /v1/query; optional GET /v1/config (safe mode information).
GET /v1/documents/{id} returns permitted original source text after safety checks;
unsafe sources return 404 rather than rewritten excerpts. No customer write routes.

Response JSON required fields: `request_id`, `answer` (str), `evidence` (list of
{id, document_id, claim, quote, source_hash}), `citations` (list of {evidence_id,
document_id, title, source_url, version, verified}), `assumptions` (str[]),
`missing_information` (str[]), `confidence` (float 0..1), `risk_flags` (str[]),
`human_review_required` (bool), `mode` (local/bedrock), `trace` (list of
{stage, duration_ms, status}), `tool_invocations` (list of {name, duration_ms,
status}), `metrics` ({latency_ms, model_latency_ms, retrieval_latency_ms,
input_tokens, output_tokens, estimated_cost_usd, cost_estimate_complete}). Response
extensions are `calculation` (value, inputs, units, formula, rounding),
`retrieved_document_ids`, and `disclaimer`. The server validates its complete
response schema with unknown fields forbidden; clients should tolerate future
additive response fields. Endpoint always says synthetic/demo; server config chooses mode.

Stages use snake_case names from acceptance criteria. Tools use policy_search,
document_retrieval, deterministic_calculation, risk_classification,
citation_verification. Evaluation imports Workflow, AgentRequest, LocalRetriever,
Document and independently checks the returned Pydantic JSON.
Stage `status=ok` denotes completed handling, including safe abstention after an
internal failure; risk flags carry that outcome. Tool failures use `status=error`.

## Infra (infra agent implements)

CDK Python package under infra/cdk using app.py and stack.py. Backend container
runs `uvicorn services.api.main:app --host 0.0.0.0 --port 8000`.
Lambda may use `services.api.main.handler` (Mangum, backend agent supplies).
Environment: AGENT_MODE=local|bedrock, RETRIEVAL_BACKEND=local|s3,
CORPUS_BUCKET, CORPUS_PREFIX=corpus/, AUDIT_TABLE, AWS_REGION,
BEDROCK_MODEL_ID, API_AUTH_MODE=local|gateway, OTEL_EXPORTER_OTLP_ENDPOINT.
Optional audit settings: AUDIT_LOG_PATH (default .runtime/audit.jsonl),
AUDIT_RETENTION_DAYS (default 90), AUDIT_CONSOLE=1 (automatically enabled in Lambda).
BEDROCK_INPUT_USD_PER_MILLION and BEDROCK_OUTPUT_USD_PER_MILLION configure estimates.
Use private encrypted S3 + narrow permissions and API Gateway JWT auth. CDK
should synth without account secrets; cloud deployment is not assumed authorized
without target configuration. Browser uses Next.js server route as API proxy;
local backend URL http://127.0.0.1:8000 from API_BASE_URL.
