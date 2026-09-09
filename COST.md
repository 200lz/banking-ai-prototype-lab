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

| Measurement | Local baseline | Tokyo cloud activity |
| --- | --- | --- |
| Cases | 61; all gates passed | Two attempts of one case; both failed |
| Workflow p50 / p95 | 12.696 / 16.525 ms | Unavailable for an unrun smoke/suite |
| Model tokens | Exactly zero; no model invoked | Unknown; usage was not returned |
| LLM cost | $0 for the local run | Unknown; reported zero is an incomplete lower bound |
| Infrastructure/billed cost | Not a cloud measurement | CDK bootstrap resources persist; no AWS bill measured |

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

The explicitly approved Tokyo `CDKToolkit` bootstrap completed and its
[actual resource verification passed](docs/validation/cdk-bootstrap-2026-09-09.json)
on 2026-09-09: `CREATE_COMPLETE`, 11 reviewed resources, bootstrap version 32.
The five IAM roles, policy resources, S3 staging bucket and policy, ECR repository,
and SSM version parameter now persist for the planned sandbox deployment. The
bootstrap CloudFormation execution role's `AdministratorAccess` was explicitly
approved; role trust remains same-account or the CloudFormation service, with no
added external trust or change to application runtime IAM.

The private, versioned staging bucket uses AWS-managed KMS encryption. Both the
bucket and immutable-tag ECR repository were empty at verification. No
customer-managed KMS key, provisioned compute or application stack was created,
and the bootstrap made no model calls. Asset storage, encryption requests and
other API usage can incur charges as the bootstrap is used; empty storage is an
inventory observation, not a measured $0 bill. The deliberate disposition is to
**keep the bootstrap for the planned sandbox deployment**. See
[bootstrap inventory and cleanup](docs/cdk-bootstrap.md) before future removal.

Application deployment remains **NOT TESTED / BLOCKED**. The earlier Lambda
request for 1,001 without Support returned `NOT_APPROVED`. The subsequently
authorized request with Support enabled is **PENDING**, with provider status
`CASE_OPENED`; last-observed applied and unreserved concurrency remain **10**.
The application reservation stays **three**. Requesting a larger limit does not
provision running environments or change that reservation.
[Submission and applied-capacity evidence](docs/validation/support-escalation-2026-09-09.json)

Nova Lite's on-demand request, token-per-minute and daily-token limits were still
zero in the last check. The separately approved capacity inquiry is
**SUBMITTED / PENDING**, provider **Unassigned**, under Basic Support's stored
**Account / Service Quotas, General** routing. No paid Support plan/trial,
provisioned capacity or new paid resource was purchased, and no further model
calls followed the zero-capacity finding. No runtime IAM, workload region or
reservation changed. The inquiry has not established restored capacity or a
measured AWS bill. [Confirmed case evidence](docs/validation/nova-lite-support-case-2026-09-09.json)

The default unconnected Amplify template contains no repository/token reference
and therefore no missing-secret dependency. Its actual creation remains
unverified; Git authorization and a successful build are still required for a
functioning hosted frontend. Bootstrap does not resolve Lambda capacity or these
hosting requirements. See the [capacity/dependency review](docs/deployment-capacity-review.md)
and [cloud validation](docs/cloud-validation.md). AWS smoke and twenty-case live
evaluation remain **NOT TESTED**. Databricks Free Edition native pipeline and
Gold/browser integration passed through a Volume-backed wheel. The table
below describes potential application costs, not deployed application resources
or measured charges.

| Driver | Cost behavior / chosen control |
| --- | --- |
| Lambda | Memory 脳 duration 脳 calls; 1 GiB, 28-second timeout, reserved concurrency 3 |
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
On 2026-09-10 JST, two real job runs in user-confirmed Free Edition failed on
workspace file reads after 71.903 and 104.309 seconds. Those measured durations
are failed-run wall times, not successful pipeline latency or billable DBUs.
Free Edition is a [no-cost offering](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations),
so no charge is expected; an actual metered dollar amount was not exposed or
measured. No paid trial, payment method, paid resource or edition change occurred.
The subsequent managed-Volume wheel smoke passed in **33.733 s**, and the first
migrated native pipeline passed in **94.873 s**, each with one attempt and no retry.
Independent reads of all four tables took **33,391 ms**; the Bronze read included
cold warehouse startup (**23,172 ms**), while Gold took **1,984 ms**. Four actual
SDK/API profile cases plus distinct injected contracts took **10,399.707 ms**.

The first browser lookup safely abstained after **3,303.5 ms** for an unresolved
reason. Following a local API restart, complete/missing/stale profile workflow
times displayed in the browser were **5,495.2 / 3,965.7 / 3,804.7 ms**; credit refusal
took **19.6 ms** and performed no financial query. These individual observations
are not latency percentiles, DBU measurements or browser round-trip benchmarks.
All successful SQL results were real Databricks reads; the planner remained local
with zero model tokens and **$0 LLM cost**.

The existing 2X-Small serverless warehouse was **RUNNING** at final inspection with
unchanged **10-minute auto-stop**. The unscheduled job, bounded schema, one managed
Volume/wheel, four synthetic Delta tables and bundle files are retained. No new
warehouse or paid resource was created. See [evidence and cleanup](docs/databricks-validation.md).

Any future paid environment needs a separate cost review and approval. The
model-cost field excludes Databricks charges; job and query measurements are
reported separately above; an actual metered dollar amount remains unmeasured. AWS remains frozen.
