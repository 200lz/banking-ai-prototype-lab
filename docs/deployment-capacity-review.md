# Deployment capacity and dependency review

Date: 2026-09-09. Target: the approved personal sandbox in `ap-northeast-1`.
This review distinguishes resource provisioning, frontend hosting readiness and
successful model inference. No resource, runtime IAM, reservation, authentication
control or application code was changed during the static review.

**Later authorized action:** the Lambda request for 1001 was submitted with
Support enabled and reached **CASE_OPENED**; milestone status **PENDING**. Last
observed applied concurrency remains 10.
The separately approved Nova Lite inquiry was subsequently **SUBMITTED** through
Basic Support's General quota channel and is **Unassigned**, or **SUBMITTED /
PENDING** for the milestone. The direct Support
API remains unavailable under the existing plan; browser sign-in resolved the
earlier console access gate.
See [authorized escalation outcome](#authorized-escalation-outcome).

## Acceptance criteria

1. Re-read actual Lambda applied and unreserved concurrency, its quota/request
   status, and selected Bedrock on-demand/daily capacity using the approved CLI
   identity. Record timestamps; requested capacity is not applied capacity.
2. Run the actual-target diff with the existing regional Nova Lite model and
   verified Tokyo token rates. Review the resource set, IAM and retained data;
   preserve Lambda reservation three and every existing security control.
3. Separate A: provisionable resource definitions, B: Lambda reservation blockers,
   C: Git-connected hosting readiness, and D: successful-inference requirements.
   An offline template or completed bootstrap does not prove deployment success.
4. Use only existing supported configuration. Do not split the stack, add a
   backend-only mode, delete Amplify resources, relax concurrency, substitute
   models/regions or bypass authentication to create a partial success claim.
5. Preserve real failures and unavailable usage. Update actual deployment/smoke
   results only after execution, with sanitized evidence and cleanup inventory.

## Fresh AWS evidence and actual diff

Fresh authenticated APIs completed at **13:52:24 UTC on 2026-09-09**. The non-root
Identity Center actor and authorized Tokyo sandbox matched. Lambda applied and
unreserved concurrency are both **10**, with zero functions. Service Quotas marks
`L-B99A9384` adjustable and reports default 1000. The earlier request for 1001 is
still **NOT_APPROVED**, with no Support case. No request was submitted again.

AWS preserves 100 executions for unreserved functions, so this application's
reservation of three requires at least 103 available beforehand. Ten cannot
satisfy that constraint. The previously observed API rejected 103 because it
requires more than its default of 1000; the prepared request is therefore 1001,
while the application reservation stays three. This is not a request for 1001
provisioned environments. [Lambda concurrency rules](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)

| Nova Lite runtime quota | Code | Current value | Adjustable |
| --- | --- | ---: | --- |
| On-demand requests/minute | `L-E386A278` | 0 | false |
| On-demand tokens/minute | `L-70423BF8` | 0 | false |
| Maximum tokens/day | `L-45E0AD92` | 0 | false |
| Cross-region requests/minute | `L-89F8391A` | 0 | false |
| Cross-region tokens/minute | `L-7C42E72A` | 0 | true |

The system-defined `apac.amazon.nova-lite-v1:0` profile is ACTIVE and lists Tokyo,
Seoul, Osaka, Mumbai, Singapore and Sydney. Its existence does not provide usable
capacity: the applicable cross-region request/token quotas are also zero. It was
not selected or invoked. Batch quota entries have positive values, but do not
establish synchronous runtime capacity and are not a substitute for this agent.
Access metadata remains AUTHORIZED/AVAILABLE. **Runtime capacity is BLOCKED;
zero model calls were made.** No region/profile/model substitution occurred.

The actual-target synth and read-only `cdk diff --no-change-set` passed at
**13:57:23 UTC**, using source commit `4c3b1437b1f1caf41ef07b68811be8f8873bc02a`.
Synthesis took 47.188 seconds and diff 2.750 seconds. There are 33 application
resources plus CDK metadata; no change set or resource was created. Verified
reservation three, four JWT/custom-scope routes, required Cognito MFA, private
S3, no Lambda function URL, no token/repository reference and no profile switch.
The configured rates remain the reviewed Tokyo 0.072/0.288 USD per million tokens.

[Actual reassessment and diff evidence](validation/capacity-reassessment-2026-09-09.json)
contains timestamps, quota values, profile metadata and resource counts without
account/principal/request identifiers. `CDKToolkit` remains CREATE_COMPLETE; the
application stack and expected Amplify connection secret remain absent. The
[bootstrap inventory](validation/cdk-bootstrap-2026-09-09.json) still accounts for
the 11 kept resources. Application deployment, AWS smoke and live evaluation
remain NOT TESTED; the earlier failed qualifications are preserved unchanged.

## Existing configuration and dependency findings

The configuration lives in [stack.py](../infra/cdk/stack.py), with context values
loaded by [app.py](../infra/cdk/app.py). The reviewed default template contains
33 application resources plus CDK metadata. It has one stack, `BankingAiPrototypeLab`; there is no
backend-only stack or `enable_amplify`/`disable_web` option.

| Existing mode | Configuration | Synthesized behavior | Readiness consequence |
| --- | --- | --- | --- |
| Unconnected hosting shell | Omit both `web_repository` and `github_token_secret_name` | Amplify App and Branch still exist; Repository/AccessToken/OauthToken are absent; `EnableAutoBuild=false` | No missing-secret dynamic reference; no functioning hosted frontend yet |
| Git-connected hosting | Set both the HTTPS GitHub repository and token-secret name | Amplify gets a Secrets Manager dynamic reference and enables branch builds | Secret resolution, repository access and actual SSR build must succeed |
| Custom callback origin | Optional HTTPS `web_origin` | Changes Cognito callback/logout and web configuration | Does not remove Amplify or provision domain/DNS association |

Providing only one of the repository and secret-name settings fails local
configuration validation. Configuring connected mode with a missing secret can
fail CloudFormation secret resolution. Missing GitHub authentication is therefore
not a synthesized dependency of the default unconnected mode. The
[existing runbook](cloud-deployment.md) explicitly describes connecting that shell
later; the infrastructure tests verify disabled builds in default mode and the
secret reference/enabled builds in connected mode.

This is evidence of a supported repository configuration, not a claim that a
real `WEB_COMPUTE` shell has been provisioned. AWS marks Repository and the token
properties optional, while the token-property prose nevertheless says a token
is required when creating a new app. Those statements do not conclusively verify
creation of this no-token `WEB_COMPUTE` shell; actual service acceptance remains
unverified until creation succeeds. [Amplify CloudFormation resource reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-amplify-app.html)

A manual artifact upload is not a supported substitute for this Next.js SSR
hosting flow: AWS excludes SSR apps from manual deployment. [Amplify manual deployment limits](https://docs.aws.amazon.com/amplify/latest/userguide/manual-deploys.html)

The default Cognito client callback references the Amplify app's default domain.
The API JWT authorizer references that Cognito client; Lambda integration and
permissions reference the Lambda function. The Amplify branch references the API,
Cognito client/domain and its log group. This avoids a circular dependency, but
keeps the components in one CloudFormation transaction. `cdk deploy --exclusively`
selects stacks, not an arbitrary resource subset, and cannot turn this stack into
a backend-only deployment.

## Resource and readiness classification

| Class | Existing resources or operation | Meaning for the current stack |
| --- | --- | --- |
| A: no identified Lambda/Bedrock capacity prerequisite | Corpus S3/bucket policy, audit DynamoDB, IAM roles/policies, Cognito user pool/resource server/domain, API/application log groups and API control-plane definitions | These do not consume the application's Lambda reservation or invoke a model. Their actual creation remains NOT TESTED; the single stack cannot be declared deployable from these definitions alone |
| A/C: unconnected hosting definitions | Amplify App/Branch, hosting log group, default-domain Cognito client and dependent JWT authorizer | Existing default configuration omits Git credentials. Service creation remains unverified; the shell would not serve the demo. Connected-mode credentials are a separate readiness requirement |
| B: reservation three and dependent runtime | Lambda function, invoke permissions/integration, working API routes, Lambda alarms/dashboard references | Lambda creation requires enough actual capacity while preserving AWS's unreserved pool. If fresh applied capacity is still 10, this known blocker prevents successful completion of the existing whole stack |
| C: Git-connected frontend | Repository authorization, token-secret access, Amplify branch build, SSR runtime and working Cognito browser callback | A missing connection blocks the functioning hosted frontend. It should not be described as a proven missing-secret failure for a default template that contains no secret reference |
| D: successful model inference | Selected model access plus usable on-demand/daily quotas, successful Strands call, usage reporting, grounded response and citations | CDK creates no Bedrock model resource and performs no model call. Zero capacity can block workflow success even after infrastructure creation; discovery/authorization metadata alone is insufficient |

Some API and telemetry definitions can be created before Lambda, but their
end-to-end behavior still depends on B. No application resources should be
reported as deployed merely because their definition belongs to A.

## Existing CLI path and evidence limits

The direct pinned CDK CLI accepts the existing context without infrastructure
changes. For this Tokyo review, both diff and a later authorized deployment must
use the same `model_id=amazon.nova-lite-v1:0`,
`input_usd_per_million=0.072`, and `output_usd_per_million=0.288` context values,
with privately verified `CDK_DEFAULT_ACCOUNT` and Tokyo `CDK_DEFAULT_REGION`.
Omitting both Git settings selects the existing unconnected shell.

The default `make deploy` wrapper does not forward arbitrary additional command
arguments into CDK context; do not infer that model-price environment variables
alter `DeploymentConfig`. Review the explicit target configuration used by the
deployment owner. Never place GitHub token values in command arguments or context.
The deploy wrapper publishes reviewed corpus documents and the manifest only
after CloudFormation succeeds; it does not connect Amplify or create a usable
Cognito browser session.

Static checks confirmed the default template omits all three Amplify repository/
token properties, disables auto-build, preserves reservation three and has the
dependency references described above. Existing unit tests cover both configuration
modes and the security boundaries. These checks neither invoked AWS nor establish
that a model call or authenticated cloud smoke passed.

## Historical request preparation and human gate

The [prepared Lambda request](validation/lambda-quota-request-prepared.json)
records the exact normal and support-backed payloads, justification, current
limit, requested value and cost/impact boundaries. Neither was submitted during
this reassessment. The SDK/API has no justification field; that explanatory text
belongs in the approval record or a separately authorized Support interaction.

`SupportCaseAllowed` defaults to true. Explicit false prevents Support-case
creation and can result in NOT_APPROVED; the earlier result does not establish a
Support-reviewed denial. Repeating the unchanged no-Support request is not a
supported remedy demonstrated by current evidence. An account-level request and
any Support escalation require the user's explicit authorization at this gate.
[AWS request semantics](https://docs.aws.amazon.com/servicequotas/2019-06-24/apireference/API_RequestServiceQuotaIncrease.html)

The prepared no-Support request is:

```sh
aws service-quotas request-service-quota-increase --service-code lambda --quota-code L-B99A9384 --desired-value 1001 --no-support-case-allowed --profile jdd-sandbox --region ap-northeast-1 --no-cli-pager
```

If the user separately authorizes the Support-backed variant, the same command
uses `--support-case-allowed` instead. It may create an AWS Support case. Recheck
the applied quota and request history before submission to avoid duplicating an
active request. A limit increase creates no running Lambda environments and does
not change the application's reservation three. Service Quotas and reserved
concurrency themselves have no additional charge; subsequent workloads are billed.
No paid support-plan purchase or provisioned concurrency is part of the request.

Bedrock needs a **separately authorized capacity inquiry** because the relevant
on-demand/day limits are zero and reported non-adjustable. The prepared inquiry is:

> Please investigate in-region Amazon Nova Lite capacity in ap-northeast-1 for
> this isolated personal synthetic portfolio sandbox. On 2026-09-09 the model
> amazon.nova-lite-v1:0 had AUTHORIZED/AVAILABLE access metadata, but L-E386A278,
> L-70423BF8 and L-45E0AD92 were all zero and reported Adjustable=false. Earlier
> safe single-case requests failed with ModelThrottledException. What account
> restriction causes this, and what supported steps enable modest regional
> on-demand use for a one-case qualification followed by three and twenty cases?
> No cross-region inference, provisioned capacity, paid plan or runtime IAM
> expansion is requested.

At preparation time, the next step was to inspect actual Support API entitlement
and supported channels. Subsequent review established that `CreateCase` cannot
request quota increases, so the approved capacity inquiry used the available
free console channel described below. No Support API interaction or case creation
had occurred during this earlier read-only reassessment.

## Authorized escalation outcome

The user subsequently approved Lambda 1001, the Lambda Support escalation and the
separate Tokyo Nova Lite capacity inquiry. Acceptance criteria were to recheck
identity and request history, submit at most one new Lambda request, distinguish
request status from applied quota, and use only the existing free Support channel
if the direct Support API is unavailable. Paid Support upgrades, region changes,
cross-region inference, runtime IAM weakening and other paid resources were
expressly excluded.

At **14:12:54 UTC**, `RequestServiceQuotaIncrease` returned HTTP 200 for
`lambda` / `L-B99A9384`, `DesiredValue=1001`, `SupportCaseAllowed=true`. The
pre-submission history contained only the prior NOT_APPROVED request, so there
was no active request to duplicate. The new request initially returned PENDING;
at **14:15:45 UTC** it was **CASE_OPENED**, with a Support case identifier present.
Applied and unreserved concurrency remained **10**, with **zero functions**.
This establishes successful submission and Support escalation, not an approved
or applied increase. No separate duplicate Lambda case was created. The private
request/case identifiers are retained only in ignored local tracking evidence.

The same fresh check found Nova Lite requests/minute, tokens/minute and daily
tokens still **0**, all **Adjustable=false**. No inference was attempted.
The cause of the zero capacity remains unknown; authorization metadata does not
establish account eligibility or usable model capacity.

The actual `DescribeServices` call returned **SubscriptionRequiredException /
HTTP 400** at **14:14:15 UTC**. No `CreateCase` call was attempted, no service or
category code was invented, and no Support plan was changed. AWS maps Tokyo
Support administration to `support.us-east-1.amazonaws.com`; the Support-only
client used that endpoint and signing region while the AWS session, Lambda,
Service Quotas and model target remained `ap-northeast-1`. Support is a global
case-management service; this administrative routing did not deploy resources or
enable inference outside Tokyo. [AWS Support endpoints](https://docs.aws.amazon.com/general/latest/gr/awssupport.html),
[global Support service behavior](https://docs.aws.amazon.com/awssupport/latest/user/about-support-api.html)

The Support API requires an eligible plan. Service-limit requests instead have
a Support Center channel available without buying technical support; `CreateCase`
does not itself support quota increase requests. The free console route must use
an actually available service/category, not assume the selected model is listed.
[API requirements](https://docs.aws.amazon.com/awssupport/latest/APIReference/API_DescribeServices.html),
[quota request channel](https://docs.aws.amazon.com/awssupport/latest/user/create-service-quota-increase.html),
[case eligibility](https://docs.aws.amazon.com/awssupport/latest/user/case-management.html)

The first browser attempt returned the AWS **Sign In** page. No login credentials
were entered, and the inquiry was NOT SUBMITTED at that historical checkpoint.
The user subsequently signed in and explicitly confirmed the existing non-root
Identity Center session. The rendered browser matched the approved account and
showed Basic Support. The menu did not independently expose the role name; that
identity detail is user-confirmed, not an independently verified browser claim.
Automatic approval review rejected opening Security credentials for a further
identity check as outside the Support task. That navigation was not executed or
retried; the agent continued only within the already authorized Support workflow.

### Nova Lite inquiry submitted through Basic Support

Acceptance criteria for this continuation were to use an available Basic Support
channel, retain the reviewed Tokyo-only inquiry and cost/security restrictions,
avoid duplicating the Lambda case, and verify an actual created case rather than
an interaction draft or a submission spinner.

The current console routes **Create case** through Support interactions. Its case
form exposed **Service limit increase**, service **Service Limit Increase**, and
category **General**; the other available categories were messaging and SES.
The General category was used for the already authorized inquiry. The form
accepted **General question** severity and **English / Web** communication, with
no additional contacts or attachments supplied. No paid plan, upgrade or trial
was selected. The inquiry asks AWS to determine the cause of zero regional quotas
and the supported steps for modest Tokyo-only on-demand qualification; it does
not assume an account-verification cause or request provisioned capacity.

The actual case details and stored correspondence confirmed creation at
**2026-09-09T14:27:47.291Z**:

| Field | Observed result |
| --- | --- |
| Subject | Tokyo Nova Lite zero regional quotas — capacity and account eligibility inquiry |
| Status | Unassigned |
| Stored case type | Account |
| Stored category | Service Quotas, General |
| Severity / language | General question / English |
| Support plan | Basic Support |
| Model and requested operating region | `amazon.nova-lite-v1:0`, `ap-northeast-1`, specified in the correspondence |

The final stored type is **Account**, despite selecting Service limit increase
in the form. This records an accepted General quota inquiry, not a claim of a
Bedrock technical-support assignment, quota approval or restored capacity.
The form had no separate regional field for this category; the subject/body
explicitly identify Tokyo, and no workload region setting was changed.

[Browser-confirmed case evidence](validation/nova-lite-support-case-2026-09-09.json)
preserves the exact inquiry and sanitized final routing. The private case and
interaction identifiers remain only in ignored local tracking. The original
Lambda case was observed Work in progress and was not modified. No application
model invocation, quota change, deployment or bill measurement was performed
during this console continuation. Waiting for AWS's response is the remaining
external dependency. The finalization instruction freezes further AWS account,
resource and model actions while both support/quota dependencies are pending;
only local documentation checks and GitHub publication/CI proceed.

[Sanitized submission, case status and access evidence](validation/support-escalation-2026-09-09.json)
records the earlier API submission and browser-login checkpoint. These operations created no application resources,
invoked no model, changed no runtime controls and purchased no Support plan.
The quota request itself provisions no capacity; future workload usage remains
billable. Bootstrap resources and their cleanup procedure remain unchanged.
Application deployment, AWS smoke and the twenty-case live evaluation remain
NOT TESTED; earlier failed qualifications remain FAIL.
