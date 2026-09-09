# Cost and latency

## What has actually been measured

The completed local evaluations invoke no model: **0 input tokens, 0 output
tokens, $0 LLM cost**. Local workflow timings in `evals/results/latest.json`
include policy retrieval, deterministic planning/tools, citation checks and local
audit writes. They exclude HTTP/browser time, remote persistence, cold starts,
network transfer and inference. No AWS bill or live Bedrock latency was measured.

The API exposes model latency, retrieval latency, total workflow latency, token
counts, estimated cost, and `cost_estimate_complete`. Failed model calls can be
billed without returning usage; the reported numeric estimate is then a lower
bound, explicitly marked incomplete and surfaced as `model_cost_unavailable`.

## Model estimate

```text
estimated_model_cost_usd =
    (reported_input_tokens * input_usd_per_million
     + reported_output_tokens * output_usd_per_million) / 1_000_000
```

The default `amazon.nova-lite-v1:0` example uses configurable illustrative rates of
$0.06 per million input tokens and $0.24 per million output tokens. These are
configuration assumptions, not a current regional quote. Verify the selected
model, region, service tier, availability, and rate in
[Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) before deployment.
The SDK adapter aggregates usage across its bounded model-call loop.

At those illustrative rates, 1,500 input tokens and 150 output tokens cost
**$0.000126 per question**, or **$1.26 for 10,000 such questions**, for model usage
alone. Two attempts totaling 3,000 input and 1,200 output tokens would be
$0.000468. Neither example is a measurement or worst-case bill guarantee.

## Infrastructure budget

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
