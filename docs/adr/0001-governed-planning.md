# ADR 0001 — Deterministic control around a bounded model planner

Status: accepted for the prototype, 2026-09-09.

The workflow needs natural-language assistance and multiple read-only capabilities,
but no model may authorize a regulated business action. An open-ended agent with
runtime tool discovery creates unnecessary authority and testing complexity.

Use a nine-stage Python controller. Strands/Bedrock returns typed evidence IDs,
calculation and abstention flags, and an optional review requirement. The controller
owns tool dispatch, argument validation, citation verification, and mandatory review.
The deterministic local planner uses the same contract and produces a measurable
baseline without an AWS account.

This trades generative flexibility for verifiable provenance. Answers preserve
whole source context and cannot introduce model-authored policy claims. The
portfolio must explain that local results do not measure an LLM and that planning
value still needs live comparison. A conventional search interface might be enough
for this small corpus; retaining it as a baseline makes that tradeoff testable.
