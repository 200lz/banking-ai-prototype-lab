# AWS sandbox validation

Date: 2026-09-09. Region: **ap-northeast-1 (Tokyo)**.
**AWS deployment and twenty-case live Bedrock evaluation: NOT TESTED.**
The single-case live qualification and diagnostic retry **FAILED**. Databricks
workspace execution remains **NOT TESTED**.

Authenticated preflight now supersedes the earlier missing-credentials blocker.
The [historical preflight](validation/aws-preflight-2026-09-09.json) is preserved
unchanged. The [Tokyo evidence summary](validation/aws-tokyo-preflight-2026-09-09.json)
contains sanitized observations; the [security review](aws-deployment-review.md)
records bootstrap privilege, runtime IAM, retention and cost concerns. Private
account numbers, principals, provider request IDs, credentials and raw logs are
excluded from published evidence.

## Actual preflight and deployment outcome

| Check | Observed result |
| --- | --- |
| Identity and target | PASS: authorized isolated sandbox, non-root Identity Center role and Tokyo region verified |
| Bedrock model discovery | PASS: 62 regional model entries returned |
| Nova Lite access metadata | AUTHORIZED; agreement, entitlement and region AVAILABLE. Successful inference was not established |
| Actual target CDK synthesis and diff | PASS: reviewed target configuration with regional Nova Lite pricing; these checks created no infrastructure |
| `CDKToolkit` and application stack | Both MISSING at preflight |
| Bootstrap | NOT TESTED: automatic approval review rejected persistent administrator-capable deployment-role creation; explicit user approval remains required |
| Application deployment and AWS smoke | NOT TESTED: no stack was created |
| Lambda concurrency | Applied limit 10, unreserved 10; required application reservation remains three |
| Lambda quota requests | 103 rejected because the API requires more than default 1000; 1001 request NOT_APPROVED, support-case creation disabled |
| Bedrock quota checks | All 166 queried on-demand/daily entries returned zero; this is not a claim about every Bedrock quota type |
| Amplify repository connection secret | MISSING; user connection remains required |
| Single-case live qualification and diagnostic retry | FAIL: provider diagnostic `ModelThrottledException`; usage/cost reporting incomplete |
| Three-case smoke and twenty-case suite | NOT TESTED: the qualification gate stopped both runs before these phases |

The Docker gate passed before AWS preflight. The final local gates after the
model-availability ID correction passed **294 Python/API/infrastructure tests**,
**26 frontend tests**, formatting, lint, types and security checks. A focused
70-test harness regression also passed. See the
[local regression evidence](validation/aws-local-regressions-2026-09-09.json) and
[verification matrix](verification-matrix.md). Local tests do not establish cloud
execution.

## Actual model discovery

The table is a representative subset of the 62 returned model entries. Support
and lifecycle are discovery metadata, not successful invocation results. Nova
Lite was selected for the existing exact regional model IAM boundary; no
cross-region inference profile was substituted.

| Provider | Model | Model ID | Returned inference types | Lifecycle |
| --- | --- | --- | --- | --- |
| Amazon | Nova Lite | `amazon.nova-lite-v1:0` | ON_DEMAND, INFERENCE_PROFILE | ACTIVE |
| Amazon | Nova Micro | `amazon.nova-micro-v1:0` | INFERENCE_PROFILE | ACTIVE |
| Amazon | Nova Pro | `amazon.nova-pro-v1:0` | INFERENCE_PROFILE | ACTIVE |
| Anthropic | Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | ON_DEMAND | LEGACY |
| Mistral AI | Mistral Large 3 | `mistral.mistral-large-3-675b-instruct` | ON_DEMAND | ACTIVE |
| Qwen | Qwen3 32B (dense) | `qwen.qwen3-32b-v1:0` | ON_DEMAND | ACTIVE |
| Google | Gemma 3 12B IT | `google.gemma-3-12b-it` | ON_DEMAND | ACTIVE |

For Nova Lite, the returned on-demand requests/minute (`L-E386A278`), on-demand
tokens/minute (`L-70423BF8`) and model-invocation maximum tokens/day (`L-45E0AD92`)
quotas were each **0**, with **Adjustable=false**. Batch and other quota types
are outside this finding. Availability metadata therefore did not establish
usable on-demand capacity. An authorized operator must resolve the account
restriction before another qualification attempt.

Configured standard in-region rates are **$0.072 input / $0.288 output per million
tokens**, verified against the regional AWS catalog on 2026-09-09. These are
pricing inputs, not a measured bill. [AWS Tokyo pricing snapshot](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/20260901205051/ap-northeast-1/index.json)

## Failed qualification evidence

These attempts used local reviewed retrieval and file audit with real Bedrock.
They did not execute deployed Lambda, S3 retrieval, DynamoDB or CloudWatch.

| Attempt | Qualification cases | Result | Workflow duration | Failed model-attempt duration | Usage and cost |
| --- | --- | --- | --- | --- | --- |
| Initial | 1 | FAIL; 0 passed | 2,849.472 ms | 2,837.741 ms | Unavailable/incomplete |
| Diagnostic retry | 1 | FAIL; 0 passed | 3,145.194 ms | 3,133.456 ms | Unavailable/incomplete |

Preserved artifacts: [initial harness result](../evals/results/bedrock-2026-09-09.json),
[initial case](../evals/results/bedrock-2026-09-09-single.json),
[retry harness result](../evals/results/bedrock-2026-09-09-retry-1.json) and
[retry case](../evals/results/bedrock-2026-09-09-retry-1-single.json).
Both runs stopped at the single-case gate. The provider diagnostic was
`ModelThrottledException`; fallback responses required human review and flagged
planner failure and unavailable model cost. The local content-free telemetry
probe passed in both attempts, but no successful live-model answer or quality
benchmark was produced.

Numeric zero usage/cost fields in the original failed artifacts are paired with
`cost_measurement_complete=false`; they do not prove zero billed usage. The
sanitized Tokyo summary uses null for unavailable usage and cost. Failed-attempt
durations are not successful-response latency benchmarks. No three-case smoke
or twenty-case evaluation results are claimed.

## Remaining external actions

1. Obtain explicit approval for the reviewed standard bootstrap's persistent
   administrator-capable deployment roles before retrying that action.
2. Resolve Lambda applied concurrency and Bedrock on-demand capacity through
   separately authorized operator/support actions. Keep reservation three and
   the exact regional model IAM scope. No Support case has been created.
3. Connect the repository to Tokyo Amplify using the required user-controlled
   GitHub App/secret, and prepare an authorized Cognito demo session.
4. Once prerequisites pass, follow the [deployment runbook](cloud-deployment.md),
   review the current diff, deploy, publish the synthetic corpus manifest last,
   and execute [AWS smoke checks](cloud-smoke.md), actual IAM inspection and
   Amplify build/site verification.
5. Run one successful qualification, then three-case smoke, then the twenty-case
   suite. Preserve failures, real token usage and regional cost estimates.

The previously verified GitHub Actions
[run 34346854721](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34346854721)
passed at commit `6f24ef61fcf5dcbb7d3906fc38aa3c124b436b19`. That hosted result does not certify the subsequent
AWS evidence and harness correction; a new hosted run must be recorded separately.

## Resource inventory and cleanup

No bootstrap or application resources were created. Both stacks were missing
at preflight; no running application stack, API, Amplify site or retained data
resources were provisioned by this deployment attempt. There is no newly created
infrastructure to destroy. Quota requests do not provision running compute.
Actual inference billing is unavailable; no zero-bill claim is made.

For a future deployed stack selected for destruction, first reverify the same
non-root sandbox identity and inventory the retained resources. These exact
AWS CLI commands delete and wait for the named Tokyo application stack; they
were **not executed** in this attempt:

```sh
aws cloudformation delete-stack --stack-name BankingAiPrototypeLab --profile jdd-sandbox --region ap-northeast-1
aws cloudformation wait stack-delete-complete --stack-name BankingAiPrototypeLab --profile jdd-sandbox --region ap-northeast-1
```

This application cleanup does not delete `CDKToolkit`, its retained asset bucket,
ECR assets or an independently created Amplify token secret. The retained corpus
bucket, audit table, Cognito pool and three explicit log groups need their own
reviewed cleanup; deleting the stack alone does not stop their storage charges.

If a later deployment succeeds, record KEEP FOR INTERVIEW DEMO or DESTROY AFTER
VALIDATION and follow the [retention/cleanup runbook](cloud-deployment.md).
Application and bootstrap deletion can leave retained S3, DynamoDB, Cognito,
log and asset resources. General runtime egress, unactioned alarms, non-WORM
audit storage and unverified cloud telemetry remain documented limitations.
