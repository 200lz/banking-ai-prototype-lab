# Acceptance criteria

These criteria precede implementation. All internal policies, examples, employees,
and customer scenarios are synthetic. The project has no bank affiliation.

## Milestone 1 — governed local workflow

- A typed FastAPI request runs nine observable stages: request, intent analysis,
  retrieval, agent planning, controlled tool execution, guardrail validation,
  citation verification, human approval decision, and final response.
- The default local mode is deterministic and requires neither AWS nor an LLM.
  It is explicitly labelled a baseline, never presented as measured LLM quality.
- Each material policy claim maps to an exact excerpt of an identified, hashed
  source. Unsupported/contradictory evidence leads to abstention or review.
- The runtime has exactly five read-only tool capabilities; strict schemas reject
  unknown tools/fields. Calculations use Decimal and bounded operands.
- No execution, approval, customer mutation, or approval bypass capability exists.
- Injection, PII, missing evidence, conflicts, and unauthorized access have tests.

## Milestone 2 — demonstrable product

- Next.js UI sends real API requests and displays answer, evidence, citations,
  assumptions, missing information, confidence, risks, review status, stage traces,
  latency, tokens, and estimated model cost; errors and loading are usable.
- Synthetic sample prompts and a repeatable command-line demo work locally.
- Compose wires web/API/OTLP collector; Make targets have Windows equivalents.
- Formatting, lint, Python/TypeScript checks, unit and integration tests pass.

## Milestone 3 — evaluation and security

- At least 50 versioned synthetic cases cover ordinary, arithmetic, ambiguous,
  malicious-user, injected-source, irrelevant-source, conflicting-policy,
  missing-information, and out-of-scope requests.
- Evaluator measures correctness, recall, citations, groundedness, compliance,
  hallucination, tool selection, escalation, latency, and model cost with explicit
  definitions, per-case artifacts, dataset hash, and CI thresholds.
- Regression gates fail on unsupported claims, missed review, or forbidden tools.
- OpenTelemetry spans and redacted structured audit events record all stages.

## Milestone 4 — AWS and portfolio handoff

- Replaceable local and S3 retrieval implementations share one contract; AWS
  retrieval enforces corpus prefix/classification and bounded document loading.
- A real Strands/Bedrock planner adapter consumes only sanitized evidence and
  returns typed, bounded plans which the deterministic controller validates.
- CDK synthesizes a deployment with Bedrock IAM, private/encrypted S3, DynamoDB
  audit/review persistence, CloudWatch, authenticated API, web hosting, and OTEL.
- CI runs all required quality/security gates. README, architecture, threat model,
  ADRs, security/evaluation/cost/readiness/contributing docs and REPORT exist.
- No claim of a cloud deployment or Bedrock result without actual evidence.

## Verification policy

Run relevant tests after each milestone. Record significant failures and decisions
in `docs/development-log.md`; keep real measured results in `evals/results/` and
report remaining limitations honestly. Do not deploy billable infrastructure
without a configured AWS account and concrete reviewed deployment plan.

## Implementation interpretation notes

The nine-stage trace covers completed responses, including safe refusals. A stage
marked `ok` may have handled an error by abstaining; response risk flags and tool
error status expose that distinction. Audit persistence failure blocks the normal
response, so complete records cannot be guaranteed during a failed audit write.
Source verification uses the retriever snapshot: S3's bounded 60-second cache is
an explicit freshness limitation, not instantaneous source-revocation enforcement.
Cloud resources and exporters must still be tested in a deployed account; local
contract tests and CDK synthesis do not establish live cloud behavior.
