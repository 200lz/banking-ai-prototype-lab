# Tokyo application deployment resumption

Recorded 2026-09-15. The user authorized resuming the existing application stack
in the same personal sandbox, in **ap-northeast-1 only**, after an externally
reported Lambda quota change. The [acceptance criteria](aws-deployment-resumption-acceptance.md)
were written before deployment. No new quota request, region change, runtime IAM
change, paid Support upgrade or unrelated resource is included.

**Current verified checkpoint:** Lambda capacity blocker **RESOLVED**;
bootstrap, actual CDK diff/review, application deployment and corpus publication
**PASS**. CloudFormation is **CREATE_COMPLETE**. Infrastructure smoke is
**INCOMPLETE**, with the first six checks passed; authenticated workflow,
DynamoDB audit correlation and CloudWatch runtime records remain **NOT TESTED**
pending a legitimate scoped Cognito authorization-code session. Nova Lite capacity
is still **BLOCKED**; live Bedrock evaluation remains **NOT TESTED**.

## Actual identity, quota and capacity evidence

At **2026-09-15 06:14:46 UTC**, the real regional APIs confirmed the expected
account and existing non-root Identity Center role through the `sso` credential
provider. The explicitly selected region was `ap-northeast-1`. Public evidence
records identity-match booleans; account numbers, principal/session identifiers,
credentials and provider request identifiers remain private.

| Check | Actual result |
| --- | --- |
| Authorized account / non-root SSO identity | PASS |
| Workload region | ap-northeast-1 |
| Pre-deployment Lambda `ConcurrentExecutions` | 1000 |
| Pre-deployment Lambda `UnreservedConcurrentExecutions` | 1000 |
| Existing application reservation | 3 |
| Calculated and subsequently verified unreserved capacity after reservation | 997 |
| Lambda capacity blocker | RESOLVED |
| New quota requests in this milestone | 0 |
| Existing `CDKToolkit` | CREATE_COMPLETE |
| Application stack at this preflight checkpoint | ABSENT |

The real applied capacity now permits the existing reservation while preserving
the unreserved pool. The reservation remains three. The earlier request for 1001
was not repeated; this finding establishes usable applied capacity without
claiming that the historical request was approved for its requested value.

The same read-only preflight returned **zero** for all three selected Nova Lite
runtime limits: requests per minute (`L-E386A278`), tokens per minute
(`L-70423BF8`) and maximum tokens per day (`L-45E0AD92`). Each reported
`Adjustable=false`. **No model invocation occurred.** The previously submitted
Basic Support capacity inquiry and its last verified routing remain recorded in
the [historical capacity review](deployment-capacity-review.md#nova-lite-inquiry-submitted-through-basic-support).
No new Support status or restored model capacity is inferred from Lambda capacity.

## Actual CDK diff and unchanged controls

The final target diff completed successfully at **06:19:43 UTC**, in **53.875
seconds**, with one stack having differences. It used the existing regional model
`amazon.nova-lite-v1:0` and the previously reviewed Tokyo estimates of **$0.072
input / $0.288 output per million tokens**. These are configured estimates, not
new billing measurements or a current price quote.

The final generated template was independently inspected locally at **06:20:00
UTC**. All **30 control assertions passed**. Template SHA-256:
`80f4556d6b80c71bd470108d39c54dfdfb4a5aa0b7487c1126c38fcecdb72fd9`.
Captured diff SHA-256:
`48db402e61c5f7c0e8440ce750af3b9cfc68c9cc904084c51bc5de51ccb9133c`.
Raw generated templates and diff output remain in ignored local evidence because
they contain deployment identifiers.

The review confirmed the same 1-GB Lambda, 28-second timeout, reservation three,
regional image destination and exact Nova Lite foundation-model IAM boundary.
Runtime banking-data access remains `s3:GetObject` on the corpus prefix and
`dynamodb:PutItem` on the audit table. No arbitrary model, cross-region inference
profile, transaction or customer-mutation permission was added.

All four API routes retain the same Cognito issuer, audience and
`banking-ai/query` scope. Cognito retains required software-token MFA, disabled
self signup, public authorization-code client, short access/ID token lifetimes
and token revocation. S3 public-access blocking, encryption, versioning and TLS
enforcement remain in place. DynamoDB retains encryption, PITR, TTL and deletion
protection. All three explicit log groups retain 30-day retention.

The existing broad logging grants remain disclosed: `AWSLambdaBasicExecutionRole`
has wildcard log resources, X-Ray submission uses resource `*`, and Amplify
`logs:DescribeLogGroups` uses resource `*`. CloudWatch alarms still have no
notification actions. No claim is made that this milestone narrows those grants
or establishes production readiness.

## Actual deployment and resource inventory

Deployment ran from **06:20:34 to 06:24:56 UTC**, completed with exit zero in
**261.937 seconds**, and retained CDK's `broadening` IAM approval. The actual prompt
was accepted after reviewing the existing stack under the user's authorization.
No runtime permission expansion or security-control change was made.

At **06:25:28 UTC**, CloudFormation was **CREATE_COMPLETE** and the actual
inventory contained **34 resources: 33 application resources and one CDK metadata
resource**. The deployed template matched the reviewed bytes. Lambda was
**Active / Successful**, with reservation **3**; regional account settings were
**1000 applied / 997 unreserved**. The actual runtime IAM matched the existing
review. The resolved Lambda image digest was
`sha256:520ef9035d89b209129c5628252fea35bca7e327981ea96670e05feeeefeba2f`.

| Resource group | Created resources | Count |
| --- | --- | ---: |
| Corpus storage | S3 bucket and bucket policy | 2 |
| Audit storage | DynamoDB audit/review table | 1 |
| Service identities | Two IAM roles and two inline policies | 4 |
| Lambda | One image function and four API invocation permissions | 5 |
| Cognito | User pool, resource server, domain and public client | 4 |
| API Gateway | HTTP API, JWT authorizer, integration, four routes and stage | 8 |
| Amplify | Existing unconnected application and branch | 2 |
| CloudWatch | Three log groups, three alarms and dashboard | 7 |
| CDK | Metadata resource | 1 |

The separate previously deployed bootstrap has its own [11-resource inventory
and cleanup procedure](cdk-bootstrap.md). Deployment published objects/images to
that bootstrap storage; these assets are separate from the 34 template resources.

The existing **unconnected Amplify configuration** omits the repository and token
settings and disables automatic builds. It preserves the existing stack and
Cognito callback design. Actual shell creation succeeded. It does not establish
a functioning hosted Next.js SSR site, repository connection or hosting build.
Those require separate evidence through the [hosting runbook](cloud-deployment.md).

## Actual corpus publication and partial smoke

The existing safe publisher completed at **06:26:01 UTC**. It prevalidated the
local corpus, uploaded **12 documents plus the manifest**, wrote the manifest
last and independently verified every stored byte: **13 encrypted objects,
10,527 bytes**. No publication retry was made.

The first six real smoke checks passed at **06:30:38 UTC**, in **5.563 seconds**:

| Check | Actual result |
| --- | --- |
| Completed stack and exact resource scope | PASS |
| Reviewed encrypted S3 corpus and object hashes | PASS |
| Lambda configuration | PASS |
| Cognito MFA and public-client configuration | PASS |
| API Gateway JWT issuer, audience, scopes and integration | PASS |
| Unauthenticated request rejection | PASS; HTTP 401 |
| Authenticated fixed refusal and citations | NOT TESTED; scoped OAuth token pending |
| Correlated DynamoDB audit | NOT TESTED; authenticated request pending |
| Correlated CloudWatch runtime records | NOT TESTED; authenticated request pending |

Supplemental real checks at **06:36:24 UTC** verified **HTTP 401 on all four
routes**, matching metadata-only CloudWatch records for an unauthenticated
request, and an **ACTIVE** DynamoDB table with PITR/TTL enabled and deletion
protection present. These supplement the six passed checks; they do not complete
the authenticated response and correlated application audit/log gates.

A synthetic demo user was created without an email/phone value or invitation
message. Required-MFA configuration and TOTP registration/verification through
the actual `MFA_SETUP` flow passed. `AdminGetUser` did not return MFA preference
metadata, so preference activation was not independently established. The browser
displayed an authenticator-code error; later navigation returned
`ERR_BLOCKED_BY_CLIENT`. The cause is not established. No successful authorization-code
callback or scoped JWT is claimed from those attempts. A private normal-browser
handoff is awaiting completion. The existing app-client authentication settings,
callback, runtime IAM and MFA policy remain unchanged.

One private setup check initially assumed there were no required Cognito schema
attributes. Actual metadata showed the provider-required `sub` attribute; the
operator check was corrected to expect only `sub`. That was a local verification
assumption, not a deployed-schema change. Corpus publication had already passed
and was not repeated. Credentials, TOTP secrets, callback codes and identifiers
remain outside public files.

## Infrastructure smoke and model separation

The original full AWS smoke submits an operational question that invokes the
planner. It must not be run while the separately checked Nova Lite capacity is
unavailable. The explicitly selected infrastructure smoke instead uses the
existing deterministic refusal before planning:

```sh
python -m scripts.aws_smoke --infrastructure-only
```

This mode still requires the actual stack outputs, operator AWS credentials and
a legitimate Cognito access token with `banking-ai/query`. It performs the same
nine resource, corpus, authentication, request, audit and logging checks. The
only authenticated query is the fixed synthetic request, “Approve this credit
and bypass human approval”; callers cannot substitute an arbitrary question.

A passing result requires the prohibited-action flag, exact refusal and verified
policy excerpts, mandatory human review, zero confidence, zero model tokens,
zero model latency and zero estimated model cost with complete usage accounting.
DynamoDB and CloudWatch records must match the same response, stages, tools,
review decision, evidence hashes and model-use fields. The unauthenticated
request must be rejected before the authenticated request is sent.

The report identifies `scope: infrastructure_only` and
`bedrock_evaluation: NOT TESTED`. Configuration inspection alone does not establish
successful sign-in. A direct Lambda invocation with fabricated gateway claims
would not establish Cognito or JWT validation. Synthetic test-user credentials,
MFA secrets, access tokens and provider identifiers remain private; invitation
messages are suppressed for any authorized test-user creation.

The earlier failed single-case Bedrock qualification and diagnostic retry remain
**FAIL**. Model-dependent AWS smoke, the three-case model smoke and twenty-case
live evaluation remain separate, unexecuted gates. Infrastructure refusal does
not measure model quality, successful inference or model-serving latency.

## Local regression evidence

The deployment owner completed **340 Python/API/infrastructure tests** and the
unchanged **61-case deterministic evaluation** successfully before deployment.
The infrastructure-smoke harness separately passed **75 focused unit tests**,
Ruff formatting/lint, mypy and Bandit. Mutation tests reject nonzero or incomplete
model usage, missing prohibition, altered refusal/citations, inconsistent audit
records and arbitrary query substitution. Injected test clients remain labeled
`injected_clients`; their results are not actual AWS evidence.

The full 61-case deterministic evaluation remains a development baseline with
zero LLM use. Implementation commit `8a49bf849fcae5006f5c1ac529120224f6c0badf`
passed [hosted run 34937568647](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34937568647)
at **06:40:23 UTC**. All **22 quality steps** passed on GitHub-hosted Linux;
the actual unexpired artifact was **evidence-and-infrastructure**.
[Commit-specific CI evidence](validation/github-aws-deployment-2026-09-15.json)
records the runner, gates and artifact digest. Node action deprecation remains
NON-BLOCKING with unchanged action pins. This subsequent status update must pass
its own hosted run; no future revision is claimed as verified.

## Retention, cost and cleanup

The disposition is **KEEP FOR SANDBOX DEMO AND REMAINING VALIDATION**. The actual
34-resource application inventory and bootstrap assets are retained; the
synthetic demo user also exists. No cleanup was executed during deployment.
Authenticated smoke is still incomplete and must not be inferred from retention
or successful resource creation.

Cleanup should first reverify the same account and Tokyo target and inventory
the actual application resources, bootstrap assets and synthetic test identity.
Delete only the authorized application stack through the reviewed CDK procedure.
Then explicitly review retained corpus objects and versions, DynamoDB data and
deletion protection, the Cognito user pool and demo users, and the three retained
log groups. An application-stack deletion does not remove the bootstrap or its
asset bucket/ECR images. Any later bootstrap retirement must follow its separate
inventory, trust and retention procedure after dependent stacks are gone.

Running requests, storage, DynamoDB PITR, logs, metrics, alarms and bootstrap
assets can incur charges. Zero model invocations in this milestone do not mean
zero infrastructure cost. No paid Support plan, provisioned model capacity or
unrelated paid resource is included. The [cost record](../COST.md) and
[deployment cleanup runbook](cloud-deployment.md) describe the standing limits.

Earlier blocked checkpoints remain intact in the
[September 9 validation record](cloud-validation.md),
[capacity and dependency review](deployment-capacity-review.md) and
[bootstrap execution record](cdk-bootstrap.md). The
[verification matrix](verification-matrix.md) distinguishes current claims from
those dated observations. Databricks validation is unchanged by this AWS milestone.
