# AWS deployment acceptance and security review

> Historical September 9 record. Current Lambda capacity and Tokyo application
> deployment were reverified on September 15: Lambda RESOLVED and application
> CREATE_COMPLETE. See the [current execution record](aws-deployment-resumption.md)
> and [authoritative matrix](verification-matrix.md). Historical failures below
> remain preserved; they do not describe the current deployment state.

Review date: 2026-09-09. Target: the explicitly authorized personal sandbox in
`ap-northeast-1`, using the non-root IAM Identity Center profile `jdd-sandbox`.
Account numbers, session identifiers and credentials are deliberately omitted.
This document records a local infrastructure review and the deployment agent's
actual preflight observations. It does not declare bootstrap, deployment, smoke
or live evaluation complete.

## Acceptance criteria before application deployment

1. Reconfirm the authorized sandbox account, Identity Center assumed role and
   Tokyo region. Set explicit `CDK_DEFAULT_ACCOUNT` and `CDK_DEFAULT_REGION` in
   the operator environment; `AWS_REGION` alone does not override the CDK app's
   offline fallback account and region.
2. Preserve the existing local, container and hosted CI gates. Record actual
   results and the deployed source revision separately from earlier results.
3. Inspect the existing `CDKToolkit` state, bootstrap template and trust. If
   missing, obtain approval for the reviewed persistent privileged roles, bootstrap
   only this account/region, and verify the completed stack.
4. Verify sufficient **applied** Lambda concurrency for the existing function
   reservation of three. A submitted quota request is not capacity.
5. Review the real target CDK diff, including managed IAM policies, permissions,
   public exposure, retained resources and cost. Keep meaningful IAM approval;
   do not use `--require-approval never` to skip the review.
6. Discover a usable regional text model with real Bedrock APIs, verify account
   access and the existing Strands structured-output path, and configure reviewed
   regional token rates. Preserve the exact-model IAM boundary.
7. Configure Git-connected Amplify hosting and a Cognito demo session, publish
   the validated corpus with the manifest last, and then verify real resources,
   authentication, audit and telemetry. A completed stack alone is insufficient.

No product feature or runtime security control was changed during this review.
The existing [deployment runbook](cloud-deployment.md) and
[AWS/live acceptance criteria](aws-live-acceptance.md) remain applicable.

## Confirmed preflight blocker: Lambda concurrency

The deployment agent's actual Tokyo API checks returned:

| Check | Observation |
| --- | --- |
| `CDKToolkit` stack | MISSING at preflight |
| `BankingAiPrototypeLab` stack | MISSING at preflight |
| Lambda account concurrency | 10 |
| Lambda unreserved concurrency | 10 |
| Adjustable Service Quotas entry | `ConcurrentExecutions`, code `L-B99A9384` |
| Request for value 103 | Rejected with `IllegalArgumentException`: requested value must exceed the service default of 1000.0 |
| Request for value 1001 | Actual request status `NOT_APPROVED`; applied concurrency remains 10 and unreserved concurrency remains 10 |

AWS documents a reserve of 100 concurrency units for functions without a
reservation. With no existing reservations, 103 is the arithmetic minimum for
100 unreserved plus this application's three. However, **103 was not accepted
by the actual Service Quotas API**, despite the account's applied limit being 10.
The API's greater-than-default requirement makes 1001 the smallest whole-number
request satisfying its observed validation. This is a quota request value, not
the application's execution limit. [AWS concurrency documentation](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)

The deployment agent submitted the 1001 request with support-case creation
disabled. Its actual status is **NOT_APPROVED**; the applied limit is still 10.
No AWS Support case was created. Support escalation requires the separately
authorized operator action recorded by the deployment owner.
The application must keep `reserved_concurrent_executions=3`; do not remove the
reservation to work around the account restriction. Deployment remains blocked
until actual applied capacity permits it. Reserved concurrency itself has no
extra charge and a quota increase does not provision running compute. Requests
that need operator approval remain an external blocker; do not report success
from the requested number alone. [Reserved concurrency behavior](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)

## Locally inspected bootstrap template

Executed locally with the repository's pinned CDK CLI **2.1140.0**, supported
Node.js **24.19.0**, and the workspace jsii cache configuration:

```sh
node infra/cdk/node_modules/aws-cdk/bin/cdk bootstrap --show-template
```

The command succeeded without AWS calls or cloud mutation. The captured template
is version **32**, qualifier **hnb659fds**. Local raw evidence is ignored at
`.runtime/aws-review/bootstrap-template.yaml`; SHA-256 of those captured bytes:
`dc91dbee74bd71a259313d460f9cb4a64123d73e67d4bc7fad5d11a64f0ab9b6`.
The locally installed CLI bootstrap implementation was also inspected to resolve
its effective parameter defaults. [AWS template inspection guidance](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html)

For a new standard bootstrap with AWS-managed encryption and no example boundary,
the template creates **11 resources**:

| Logical resource | Type and effective behavior |
| --- | --- |
| `StagingBucket` | Private, public-access blocked, versioned S3; SSE-KMS with the AWS-managed S3 key; retain on deletion/replacement; noncurrent versions expire after 30 days; incomplete multipart uploads after one day |
| `StagingBucketPolicy` | Denies non-TLS S3 operations to everyone; the `s3:*` wildcard is an explicit deny |
| `ContainerAssetsRepository` | Private ECR repository with immutable tags; untagged images expire after 365 days; tagged images have no expiry rule |
| `FilePublishingRole` | Same-account deployment identity assumes it to publish file assets |
| `ImagePublishingRole` | Same-account deployment identity assumes it to publish image assets |
| `LookupRole` | AWS `ReadOnlyAccess` managed policy plus an explicit `kms:Decrypt` deny |
| `FilePublishingRoleDefaultPolicy` | Asset-bucket object/list/write/delete operations and the configured encryption-key operations |
| `ImagePublishingRoleDefaultPolicy` | Image upload/read operations on the asset repository; `ecr:GetAuthorizationToken` on `*` |
| `DeploymentActionRole` | CloudFormation deployment operations, execution-role passing, asset/version reads and `AWSCloudFormationReadOnlyAccess` |
| `CloudFormationExecutionRole` | Trusted by CloudFormation; default `AdministratorAccess` when execution policies are omitted and no external trust is configured |
| `CdkBootstrapVersion` | SSM string parameter `/cdk-bootstrap/hnb659fds/version`, value `32` |

The template also declares three **conditional** resources: a customer-managed
KMS key, its alias, and the example permissions-boundary policy. They are not
created for the standard new CLI bootstrap described above. A subtle distinction
matters: the raw template's empty KMS parameter would create a customer key,
whereas the pinned CLI explicitly supplies `AWS_MANAGED_KEY` for a new bootstrap.
Use `--no-bootstrap-customer-key` to make the intended CLI behavior explicit;
do not deploy the raw template with unreviewed parameter defaults.

The repository policy permits Lambda image retrieval for functions in this
account/region. The generic bootstrap also includes EMR Serverless image-read
permission restricted to applications in this account/region; it does not create
an EMR service or application. The ECR resource uses default deletion behavior;
a nonempty repository may require deliberate image cleanup before deletion.

## Bootstrap identity, trust and privilege assessment

Standard bootstrap can use the existing non-root Identity Center assumed role
without adding cross-account trust. Keep `TrustedAccounts` and
`TrustedAccountsForLookup` empty; omit `--trust` and `--trust-for-lookup`. The
bootstrap roles' account-principal trust delegates to authorized identities in
the same account. It does **not** require root credentials. The SSO permission
set/session and any organization controls must still permit the necessary role
assumption and bootstrap actions. [AWS bootstrap command reference](https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-bootstrap.html)

The four operator-facing roles allow `sts:AssumeRole` and session tagging from
the same account. The default `DenyExternalId=true` parameter conditions the
AssumeRole allow on an absent ExternalId. CloudFormation alone is the service
principal for the execution role. The deploy role's `iam:PassRole` names that
execution role specifically.

The execution role's administrator policy is a **privileged deployment boundary**,
not a least-privilege runtime policy. The generic deploy role additionally has
wildcard CloudFormation operations and conditional cross-account artifact S3/KMS
permissions. Empty trust parameters do not remove those generic outbound actions;
they prevent adding trusted external deployment principals. This standard
toolchain is appropriate only within the expressly isolated sandbox context and
must be included in the real bootstrap/diff review. An institutional deployment
would require narrower execution policies or reviewed permission boundaries.

The bootstrap command must name only the verified account and `ap-northeast-1`,
use `--profile jdd-sandbox`, and retain default public-access blocking. No literal
account number is needed in this public review. Bootstrap is independently
reviewable while the quota blocker is unresolved; it does not clear that blocker.

**Actual execution outcome:** automatic approval review initially rejected the
standard bootstrap because it creates persistent administrator-capable roles.
The user subsequently explicitly approved those reviewed roles and the default
`AdministratorAccess` execution policy in the same Tokyo sandbox, with no added
trusted accounts or application runtime IAM change. Bootstrap was **PERFORMED**
and reached **CREATE_COMPLETE**. Actual verification passed all 25 checks and
matched the reviewed template and all 11 resources. The four operator-facing roles
trust only the same account principal; the execution role trusts CloudFormation.
See the [actual inventory and cleanup procedure](cdk-bootstrap.md).

## Actual Bedrock and application outcome

Authenticated Tokyo model discovery returned 62 entries. Nova Lite
`amazon.nova-lite-v1:0` returned authorized/available access metadata, but all
166 queried on-demand/daily quota entries were zero. The selected model's
requests/minute, tokens/minute and maximum tokens/day entries were zero with
`Adjustable=false`. This statement excludes batch and other quota types.

The single-case qualification and diagnostic retry both failed; provider
inspection returned `ModelThrottledException`. Three-case smoke and twenty-case
evaluation did not run. Token/cost reporting was incomplete, so neither zero
billing nor model-quality results can be inferred. Configured Tokyo standard
rates were verified at $0.072 input and $0.288 output per million tokens.

Actual target synthesis and diff passed. Both stacks were initially missing;
the later approved `CDKToolkit` bootstrap now exists successfully. The application
stack is still absent and the last inspected Amplify connection secret was missing.
Overall AWS deployment/smoke and the live evaluation remain **NOT TESTED**,
with **FAIL** recorded separately for the two qualification attempts. Bootstrap
is deliberately retained for planned deployment, with a preserved cleanup
procedure. See the [cloud validation record](cloud-validation.md)
and [sanitized Tokyo evidence](validation/aws-tokyo-preflight-2026-09-09.json).

## Planned application controls and remaining concerns

| Boundary | Existing implementation and assessment |
| --- | --- |
| Banking-data IAM | Lambda has only `s3:GetObject` under the corpus bucket's `corpus/*`, `dynamodb:PutItem` on the audit table, and two Bedrock invoke actions on one exact regional foundation-model ARN |
| Logging IAM | The generated Lambda role also attaches `AWSLambdaBasicExecutionRole`, whose logging resources are `*`; this broader managed grant must be disclosed or narrowed to the explicit application log group. X-Ray submission and Amplify `logs:DescribeLogGroups` also use `*` |
| Invocation | Public HTTP API with four JWT/custom-scope routes; Lambda invoke grants are restricted to this API's route ARNs. No function URL. Gateway claims are checked inside the application for operational routes |
| Cognito | Invited users only, required TOTP MFA, public code-flow client with PKCE in the web application, 15-minute access/ID tokens and eight-hour refresh tokens. Runtime users cannot create a credit-approval capability |
| Corpus | Public access blocked, TLS required, SSE-S3, versioning, 90-day noncurrent expiry, retained current content. Publisher trust and the 60-second retrieval cache remain limitations |
| Audit | AWS-managed KMS, on-demand DynamoDB, PITR, deletion protection, 90-day record TTL and retained table. Conditional inserts are application append semantics, not immutable/WORM storage |
| Logs and telemetry | Application/API/Amplify SSR log groups have 30-day retention and are retained. Audit and OTel metadata are content-free by design; cloud transport still needs actual verification. API access logs exclude request bodies and identity |
| Runtime/egress | 1-GB Lambda, 28-second timeout, reservation of three; API rate two/second and burst five. General outbound network access exists; sequential cold retrieval/model calls can exceed the deadline |
| Operations | Three Lambda alarms and one dashboard. Alarm notification actions are not configured. Optional account-wide budget alerts are delayed notifications, not spending caps |

Amplify's default no-repository configuration cannot establish a functioning
frontend. Git-connected deployment requires the Tokyo Amplify GitHub App to be
installed for this repository, a suitable PAT supplied through the existing
Secrets Manager reference, and successful hosting build verification. Copy only
the five allowlisted non-secret web settings into SSR build configuration.
[AWS GitHub integration requirements](https://docs.aws.amazon.com/amplify/latest/userguide/setting-up-GitHub-access.html)

The existing AWS smoke command needs a Cognito access token containing
`banking-ai/query`; an IAM SSO token is not interchangeable. Supplement its nine
checks with actual role-policy inspection and Amplify build/site verification.
Its authorized synthetic query already invokes Bedrock, so account for that
usage separately from the later one-case qualification and live evaluation.

## Cost and removal review

Usage charges can arise from model tokens, Lambda duration, API calls,
Amplify SSR/builds/bandwidth, Cognito active users and telemetry. Storage, DynamoDB
PITR, CloudWatch alarms/detailed metrics/dashboard, bootstrap assets and a GitHub
token secret can incur continuing charges with little application traffic.
Free-tier eligibility is not assumed. No running compute is created by a quota
increase or a concurrency reservation.

Application-stack deletion retains the corpus bucket, audit table, Cognito user
pool and explicit log groups. DynamoDB deletion protection remains enabled.
Deleting the application does not delete `CDKToolkit`, its retained S3 bucket,
ECR image assets or an independently created token secret. Tagged ECR images and
current S3 asset versions can persist indefinitely. Deleting a retained-data key
without reviewing its consumers could make data unreadable; the reviewed standard
new bootstrap avoids introducing a customer-managed key.

Choose and record KEEP FOR INTERVIEW DEMO or DESTROY AFTER VALIDATION once the
actual deployment outcome is known. Follow a resource inventory and the
[cleanup/retention runbook](cloud-deployment.md) rather than assuming `cdk destroy`
removes all retained resources or ends every charge. Bootstrap's actual inventory,
empty asset state and KEEP decision are now recorded in [its execution record](cdk-bootstrap.md).
Application deployment and model-capacity validation remain separate milestones.
