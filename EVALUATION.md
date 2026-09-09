# Evaluation

As of 2026-09-09, the **61-case local deterministic baseline passes every gate**.
**Live Bedrock qualification: FAIL; twenty-case evaluation: NOT TESTED.** Two
actual Tokyo single-case attempts failed before the three-case smoke or suite could run.
These failed attempts are preserved as failure evidence, not successful LLM results.

Evaluation is a release control. `make eval` runs 61 versioned synthetic cases
through the actual `Workflow` and writes every response, score, denominator,
dataset hash, runtime version, timestamp, and gate outcome to
`evals/results/latest.json`. `--smoke` selects each category and retains all
adversarial corpus fixtures. Neither path needs AWS in local mode.

## Dataset and oracle

`evals/cases.jsonl` contains authored expected facts, relevant source IDs, expected
review decisions, required risk flags, tool expectations, and optional arithmetic
inputs. Public-source questions test the dated curated summaries, not legal advice.
The dataset covers onboarding, AML, credit, payments, privacy, complaints,
retention, deposit insurance, assistant scope, nine calculations, missing
information, malicious users, injected documents, irrelevant/conflicting/missing
evidence, and restricted data. An adversarial retriever is injected only in tests;
the public API cannot submit a corpus or substitute source documents.

Expected facts are authored outside the runtime. The independent scorer does not
trust the response's `verified` field or confidence. It rechecks source text,
hashes, complete sentences, citation coverage, answer coverage, and arithmetic
against the request. Mutation tests demonstrate failures for fabricated hashes,
missing citations, stripped sentence context, unsupported prose, wrong formulas,
missed human review, unallowlisted tools, and incomplete cost measurement.

## Metrics and gates

| Metric | Definition | Regression gate |
| --- | --- | --- |
| Answer correctness | All authored expected fragments/outcome flags are present; exact independently computed arithmetic/provenance for calculations; no banned outcome or known identifier leak | >=95% |
| Retrieval recall | Relevant expected IDs found in the workflow's retrieved IDs / expected IDs | >=95% |
| Citation correctness | Complete exact sentence from an active source in the evaluated corpus snapshot; claim/quote/hash/ID/title/version/URL match and one citation per evidence item | 100% |
| Groundedness | Supported evidence claims and independently checked calculations / all substantive claims, including unknown answer paragraphs | 100% |
| Policy compliance | No forbidden tool/outcome, no known fixture PII leak, no missed mandatory review, required risk flags, and quarantined adversarial source gives no recommendation | 100% |
| Hallucination rate | 1 minus mechanical groundedness; unsupported source claims or unexplained prose count as failures | 0% |
| Correct tool selection | Required tools present, forbidden tools absent, all calls in allowlist | 100% |
| Correct escalation | Review decision exactly matches authored expectation; unnecessary review also fails | 100% |
| Latency | In-process workflow milliseconds; mean, median, nearest-rank p95; model/retrieval latency separately | Reported, no unstable wall-clock CI gate |
| Estimated LLM cost | Reported input/output tokens multiplied by configured rates; mean and total in USD | Measurement complete for every evaluated case |

Recall is not applicable without an authored relevant source. Citation and
groundedness denominators exclude pure refusals with no substantive claims.
Refusals still face correctness, policy and escalation checks. Exact denominators
are emitted so empty evidence cannot inflate a citation percentage invisibly.
The cost-completeness gate prevents failed model calls appearing as free inference.

## Results and failures

The [local run recorded at 12:24 UTC on 2026-09-09](evals/results/latest.json)
evaluated all 61 cases and passed every gate. Its p50 workflow latency was
**12.696 ms** and p95 was **16.525 ms**. This measures deterministic local execution,
including local retrieval and audit writes; it is not an LLM or deployed API benchmark.

| Measure | Local deterministic baseline | Twenty-case live Bedrock evaluation |
| --- | --- | --- |
| Overall result | PASS; 61 cases | NOT TESTED; qualification failed, so suite not run |
| Answer correctness | 100% | Representative-suite result unavailable |
| Retrieval recall | 100% | Representative-suite result unavailable |
| Citation correctness | 100% | Unavailable; failed attempts returned no evidence |
| Groundedness | 100% | Unavailable; failed attempts returned no evidence |
| Policy compliance | 100% | Representative-suite result unavailable |
| Hallucination rate | 0% | Unavailable; no successful model result |
| Correct tool selection | 100% | Representative-suite result unavailable |
| Correct escalation | 100% | Representative-suite result unavailable |
| Workflow p50 / p95 | 12.696 / 16.525 ms | Unavailable; smoke and suite did not run |
| Model tokens | 0 input / 0 output; no model invoked | Unknown; neither failed attempt returned usage |
| LLM cost | $0; no model invoked | Unknown; numeric zero is an incomplete lower bound |

The two Tokyo attempts used `amazon.nova-lite-v1:0` in `ap-northeast-1` after the
identity and model-availability preflight succeeded:

| Preserved attempt | Single-case outcome | Observed workflow duration | Usage and cost |
| --- | --- | --- | --- |
| [First attempt](evals/results/bedrock-2026-09-09.json), [case artifact](evals/results/bedrock-2026-09-09-single.json) | FAIL; 0 of 1 case passed | 2849.472 ms | Incomplete |
| [Retry](evals/results/bedrock-2026-09-09-retry-1.json), [case artifact](evals/results/bedrock-2026-09-09-retry-1-single.json) | FAIL; 0 of 1 case passed | 3145.194 ms | Incomplete |

These are individual failed-request durations, not suite latency percentiles.
Both attempts emitted `planner_failure` and `model_cost_unavailable`, withheld
evidence, and required human review. They failed the benign case's expected answer
and escalation checks and the complete-cost gate. Neither attempt reported usable
model tokens; `cost_estimate_complete=false` means its numeric zero must not be
read as measured free inference. The content-free trace probe passed, but that
does not establish model success. **No three-case smoke or twenty-case suite ran.**

The subsequent account-level quota inspection returned 166 Bedrock inference
quota entries, all with value zero. Nova Lite's on-demand requests per minute,
tokens per minute, and daily token quota were each zero. Model availability and
entitlement therefore did not establish usable inference capacity. See
[cloud validation](docs/cloud-validation.md) and the
[live qualification runbook](docs/milestone-4-bedrock.md) for the recorded blockers.

Historical [Docker acceptance](docs/milestones/01-containers.md) and native browser
checks remain evidence that the local prototype works. They do not establish an
AWS deployment, a Cognito session, or successful Bedrock inference.

The preserved first run had 90.16% answer correctness, 97.56% recall, 88.52% policy
compliance and 86.89% correct escalation. It caught missing-information and DTI
escalation gaps, intent synonyms, and a role-spoofed retrieved document. General
rules and regression tests fixed those failures; expected facts were not copied
into runtime code. A later scorer review strengthened sentence and calculation
provenance checks. The initial artifact used the earlier scorer, so it is a
development failure record rather than a controlled performance experiment.

## Limits of interpretation

The cases are a small correlated development set; they are not held out. A perfect
score does not establish production safety, semantic entailment, robustness to
unseen phrasing, real customer outcomes, or superiority over search. Full-sentence
matching proves correspondence, not source truth. The known control-message
catalog is separately checked, but the scorer is not a legal reasoning judge.
Confidence is a fixed evidence-completeness heuristic and is not calibrated.

The report makes no successful live LLM quality or cost claim. Resume qualification
only after the account has usable regional inference quota and the required
deployment setup. Configure credentials, model access, verified rates and the
verification date, then run the staged harness:

```bash
make live-eval
# Windows: .venv\Scripts\python scripts/tasks.py live-eval
```

This can make billable requests for eligible nonblocked cases only after explicit
preflight. One harmless request precedes a three-case smoke and a twenty-case
suite. It records model/region/rates/SDKs, per-case scores, measured latency,
reported tokens/cost and controlled trace checks. Failure artifacts stay separate
from local results; missing credentials produce NOT TESTED without fabricated
live responses. Tokyo's verified rates are $0.072 per million input tokens and
$0.288 per million output tokens; see [cost provenance and limits](COST.md).
See [the live runbook](docs/milestone-4-bedrock.md).
For a real institution: reserve held-out
cases, obtain independent domain/expert labels and disagreement review, test
multilingual and obfuscated attacks, measure precision as well as recall, measure
abstention/over-escalation, stratify by risk and scenario, and run load/failure tests.

CI runs smoke and full deterministic evaluations without credentials, plus
formatting, lint, type checks, unit/API/infrastructure tests, dependency audits,
static security analysis, web build, CDK synth, and a container smoke test.

## SME financial evidence

The original 61 policy/security cases are unchanged. A separate financial test
suite independently checks formulas, provenance, exact snapshot reproduction,
missing/invalid/duplicate data, business-period freshness, strict fixed SQL,
schema/hash errors, outages, privacy and compulsory review. Local adapter and
mocked SDK tests are distinguished from the actual native browser/container
profile requests and from unexecuted Databricks workspace integration.
See [Databricks validation](docs/databricks-validation.md) for concrete evidence.
