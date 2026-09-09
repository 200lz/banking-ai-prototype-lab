# Milestone 4: live Bedrock qualification

Status on 2026-09-09: **NOT TESTED**. No live invocation, model-access response,
token usage, inference cost or cloud latency has been measured. AWS CLI STS and
Boto3 preflight found no credentials or configured region.

`make live-eval` runs the existing governed Strands planner. Its preflight requires
explicit `AWS_REGION`, `BEDROCK_MODEL_ID`, both `BEDROCK_*_USD_PER_MILLION` rates,
and `BEDROCK_RATE_VERIFIED_ON` (ISO date within 31 days). Verify rates against
[official regional model pricing](https://aws.amazon.com/bedrock/pricing/).
The program checks identity, text/on-demand compatibility and
[model availability](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetFoundationModelAvailability.html)
before any inference. An access listing alone does not prove a successful model
invocation; the first harmless actual request establishes that next gate.

Execution order is one harmless synthetic case, three smoke cases, then twenty
fixed representative/adversarial IDs from the unchanged 61-case corpus. They
cover public/internal multi-document evidence, AML/review, payments/privacy,
deterministic arithmetic/DTI, missing information, prohibited approval and bypass,
malicious user instructions, out-of-scope requests, retrieved injection,
irrelevant evidence, conflicting policies and missing evidence. The controller
can reject unsafe cases before inference; twenty cases do not imply twenty LLM
calls. Each phase stops progression on failed gates.

Actual runs create `evals/results/bedrock-<date>.json`, a Markdown summary and
separate `-single`, `-smoke` and `-suite` per-case artifacts. They report scorer
quality/denominators, case pass counts, latency percentiles, actual reported
tokens and estimated cost, including probe/smoke cost. Unknown billed usage stays
incomplete. SDK/model/region/rate provenance and an in-memory controlled-export
trace check are recorded. Repeated runs should use unique `--output` names to
preserve failures; do not overwrite failed results when investigating regressions.

Local harness tests use injected clients/runners and temporary outputs. They are
not live model evidence. No `bedrock-<date>.json` is fabricated for an unavailable
account. The deterministic baseline remains separate and is not an LLM benchmark.

Qualification also refuses `AUDIT_TABLE` so its audit stays local as stated.
It ignores configured custom AWS endpoint overrides, keeping real-AWS
qualification separate from emulators such as LocalStack.
Single/smoke progression requires every individual case to pass; the final suite
runs all twenty and reports actual pass counts alongside aggregate thresholds.
The trace check validates approved metadata and rejects events/links; it is not
a universal sensitive-data detector. The first actual inference, rather than
the access API, establishes Strands/model compatibility.
