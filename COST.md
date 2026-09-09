# Cost and latency

## What has actually been measured

The completed local evaluations invoke no model: **0 input tokens, 0 output
tokens, $0 LLM cost**. The [61-case local run](evals/results/latest.json) recorded
workflow p50 **12.696 ms** and p95 **16.525 ms** on 2026-09-09. These timings
include policy retrieval, deterministic planning/tools, citation checks and local
audit writes. They exclude HTTP/browser time, remote persistence, cold starts,
network transfer and inference. The historical
[Docker acceptance](docs/milestones/01-containers.md) establishes local container
behavior separately; neither result is an LLM benchmark.

Two actual Tokyo single-case qualification attempts failed:
the [first](evals/results/bedrock-2026-09-09-single.json) took **2849.472 ms** and the
[retry](evals/results/bedrock-2026-09-09-retry-1-single.json) took **3145.194 ms**
of workflow time. Those are failed-request observations, not suite percentiles
or successful inference latency. Both stopped the harness in its first phase;
the three-case smoke and twenty-case suite did not run. **Qualification: FAIL;
twenty-case live Bedrock evaluation: NOT TESTED.**

| Measurement | Local baseline | Actual Tokyo attempts |
| --- | --- | --- |
| Cases | 61; all gates passed | Two attempts of one case; both failed |
| Workflow p50 / p95 | 12.696 / 16.525 ms | Unavailable for an unrun smoke/suite |
| Model tokens | Exactly zero; no model invoked | Unknown; usage was not returned |
| LLM cost | $0 for the local run | Unknown; reported zero is an incomplete lower bound |
| Infrastructure/billed cost | Not a cloud measurement | No AWS bill measured; no project resources created |

The API exposes model latency, retrieval latency, total workflow latency, token
counts, estimated cost, and `cost_estimate_complete`. Failed model calls can be
billed without returning usage; the reported numeric estimate is then a lower
bound, explicitly marked incomplete and surfaced as `model_cost_unavailable`.

## Verified Tokyo model rate and estimates

```text
estimated_model_cost_usd =
    (reported_input_tokens * input_usd_per_million
     + reported_output_tokens * output_usd_per_million) / 1_000_000
```

AWS's public regional catalog was verified on **2026-09-09** for
`amazon.nova-lite-v1:0`, Asia Pacific (Tokyo), `ap-northeast-1`, standard in-region
on-demand inference:

| Token direction | Catalog price per 1,000 tokens | USD per million tokens |
| --- | --- | --- |
| Uncached input | $0.000072 | **$0.072** |
| Output | $0.000288 | **$0.288** |

Both rate entries are effective **2026-08-01T00:00:00Z**. Catalog version
**20260901205051** was published **2026-09-01T20:50:51Z**. The downloaded current
catalog matched the [immutable AWS Tokyo pricing catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/20260901205051/ap-northeast-1/index.json)
byte-for-byte. The selected products explicitly identify `Nova Lite`, Tokyo,
`On-demand Inference`, and ordinary input/output tokens; batch and cache-read
rates were excluded. Per-million prices multiply the catalog's per-1,000 prices
by 1,000. The [AWS model card](https://docs.aws.amazon.com/us_en/bedrock/latest/userguide/model-card-amazon-nova-lite.html)
maps Nova Lite to this model ID.

Earlier portfolio examples used $0.06/$0.24 as illustrative input/output
assumptions. Those are not the verified Tokyo rates. Use the region-specific
values above for this qualification, and recheck
[Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) when the region,
model, service tier, or verification date changes. A published price and model
availability do not establish account capacity or successful invocation.

At the verified Tokyo rates, a hypothetical successful question using 1,500 input
and 150 output tokens would cost **$0.0001512**, or **$1.512 for 10,000 such
questions**, for model usage alone. A hypothetical pair of calls totaling 3,000
input and 1,200 output tokens would cost **$0.0005616**. These scenarios do not
measure the two failed attempts or guarantee a worst-case bill. The SDK adapter
aggregates reported usage across its bounded model-call loop; missing usage
remains incomplete.

## Infrastructure budget

No project AWS resources were created. Bootstrap was blocked by approval review.
The account's Lambda concurrent-execution quota was 10; a request for 1,001 with
support-case creation disabled returned `NOT_APPROVED`. The Amplify GitHub secret
was also absent. The subsequent Bedrock query returned 166 inference quota entries
with value zero, including Nova Lite's on-demand request, token-per-minute and
daily-token limits. These are deployment/capacity blockers, not a $0 cost claim.
See [cloud validation](docs/cloud-validation.md) for current evidence and the
remaining setup. The following table describes the existing template's potential
cost drivers, not provisioned or billed resources.

| Driver | Cost behavior / chosen control |
| --- | --- |
| Lambda | Memory × duration × calls; 1 GiB, 28-second timeout, reserved concurrency 3 |
| API Gateway | Requests; throttled to 2/second and burst 5 in the template |
| S3 | Corpus bytes, versions and reads; bounded corpus, 60-second warm cache |
| DynamoDB | Pay-per-request audit writes and storage; example 90-day TTL and PITR |
| CloudWatch / tracing | Log ingest, retention, dashboards, queries and traces; 30-day logs |
| Cognito / Amplify | Active users, builds, server compute, hosting and transfer |
| Optional OTLP service | Collector/runtime/export destination charges, configured separately |
| Databricks | Pipeline compute, SQL warehouse/serverless reads and Delta storage; development bundle has no recurring schedule and application reads one bounded Gold row |

Use the [AWS Pricing Calculator](https://calculator.aws/) with deployment-region
volumes. The optional CDK budget is **$25/month by default** and sends an email at
80% when configured; it monitors account-wide actual cost. It is an alert, not a
spending cap. CloudWatch alarms are visible on the dashboard and require an
on-call notification integration before production use.

## Cost and latency controls

The planner receives bounded evidence; typed calculation operands are excluded
from its payload, although numbers written in the question can remain after the
example redaction. It has at most 600 output
tokens per model call, two model calls, and no automatic retry strategy. Bedrock
connection/read timeouts bound individual calls; Lambda enforces the outer hard
limit. Source loading is capped at 256 documents; source refresh failures abstain.
The template uses a regional model ARN and does not silently enable cross-region
inference. Cold S3 loading and audit writes must be measured in the target region.

Destroying a stack deliberately retains the corpus, audit table and log groups;
delete retained artifacts only under a reviewed data-retention procedure.
Retained storage and Amplify builds may continue costing money after demo use.

## Databricks measurement boundary

Local Bronze/Silver/Gold computation uses synthetic files and ordinary Python;
it consumes no Databricks compute and is not a Databricks performance benchmark.
No workspace bill, job duration or SQL warehouse latency has been measured in
this environment. Choose warehouse size, serverless availability, auto-stop and
regional rates with the workspace owner before a live run. The model-cost field
excludes Databricks charges; combining it with a SQL query does not make the query
free. A successful workspace validation must report those measurements separately.
