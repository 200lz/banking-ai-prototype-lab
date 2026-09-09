# Evaluation

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

The final local development run passes all gates with 100% on the quality checks
above and a 0% unsupported-claim rate. Tokens and LLM cost are zero because local
mode invokes no model. See `REPORT.md` for the final measured timings and test count.

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

The report makes no live LLM claim. To qualify Bedrock explicitly, configure
credentials, regional model access, verified rates and the verification date,
then run the staged harness:

```bash
make live-eval
# Windows: .venv\Scripts\python scripts/tasks.py live-eval
```

This makes billable requests for eligible nonblocked cases only after explicit
preflight. One harmless request precedes a three-case smoke and a twenty-case
suite. It records model/region/rates/SDKs, per-case scores, measured latency,
reported tokens/cost and controlled trace checks. Failure artifacts stay separate
from local results; missing credentials produce NOT TESTED without fabricated
live responses. See [the live runbook](docs/milestone-4-bedrock.md).
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
