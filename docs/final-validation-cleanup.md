# Final validation and cloud cleanup

Recorded September 15, 2026. The prototype's actual AWS and Databricks validation
is preserved as dated evidence. The application, bootstrap and project workspace
resources have subsequently been removed. The local synthetic demo remains
reproducible. This milestone adds no product functionality.

## Actual verification

| Check | Executed result |
| --- | --- |
| Legitimate Cognito OAuth | PASS; fresh authorization-code/PKCE flow, state validation, endpoint HTTP 200 and required scope |
| Infrastructure-only CLI | PASS, all nine checks; 46.250 seconds including inspection and log delivery |
| Authenticated request | Fixed prohibited-credit refusal, six verified excerpts, mandatory human review |
| DynamoDB and CloudWatch | PASS; exact correlated audit, all nine stages, tools, review and API access record |
| Model usage | Zero input/output tokens, zero model latency and $0 estimated model cost |
| Live Bedrock | NOT TESTED / BLOCKED; previous qualification FAIL and zero-capacity finding preserved |
| Final local regressions | 342 Python/API/infrastructure tests (including 77 smoke contracts), 26 frontend tests, 61 deterministic cases PASS |

[Acceptance criteria](final-validation-cleanup-acceptance.md),
[actual AWS smoke](validation/aws-final-validation-2026-09-15.json), and
[local regression evidence](validation/final-local-regressions-2026-09-15.json)
define these scopes. The final-validation milestone commit `d93bf802d1d4a7376d912179e4703f26e5a5611f` passed
[hosted run 34951352510](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34951352510) on GitHub-hosted Linux. All **22 quality steps**
succeeded; artifact **evidence-and-infrastructure** was present and unexpired
when verified (146,860 bytes).
[Milestone CI evidence](validation/github-final-validation-2026-09-15.json)
records exact gates, runner and artifact integrity.

## Failure preserved and corrected

The first real authenticated run passed eight checks. Its API access record was
ingested **48.201 seconds** after the request, after the verifier had stopped.
The sixteen application audit records had already arrived. The developer-only
smoke verifier now allows 25 attempts and 120 seconds of total sleep, retaining
all correlation, privacy and response checks. Delayed-delivery and permanently
missing-log regressions passed before the same CLI was rerun successfully.
Application code, Cognito, runtime IAM, region and reservation did not change.
[Initial failure and ingestion evidence](validation/aws-infrastructure-smoke-initial-failure-2026-09-15.json)
remain public; a later PASS does not erase this result.

A prior pending OAuth transaction was discarded without redemption after its
callback was exposed. The fresh flow succeeded; a later local helper error did
not undo its successful completion. No callback, token, password, authenticator
data or private resource identifiers are included in the public evidence.

## AWS disposition

The exact 34-resource application and eleven-resource bootstrap inventories were
rechecked against recorded physical resources, templates and execution roles.
Only the authorized project resources were changed, using non-root SSO in Tokyo.

- Application CloudFormation deletion completed at **08:54:22 UTC**. The corpus
  bucket's thirteen versions, protected audit table, user pool and three retained
  log groups were then deliberately removed.
- All **14 application absence checks** passed, covering Lambda, API Gateway,
  Amplify, Cognito, DynamoDB, S3, application roles, logs, alarms and dashboard.
  Regional Lambda capacity returned to **1000 total / 1000 unreserved**.
- No active CloudFormation stack depended on bootstrap. A separate read-only
  inventory found no resources in the nine enumerated Tokyo compute groups.
  This is scoped dependency evidence, not a whole-account audit.
- Two bootstrap S3 versions and one ECR image digest were removed, followed by
  `CDKToolkit`, its retained bucket, repository, five deployment roles and SSM
  parameter. Bootstrap deletion completed at **08:59:55 UTC**; all **nine bootstrap
  absence checks** passed at the final verification ending **09:00:17 UTC**.

One **AWS-managed DynamoDB SYSTEM recovery backup** remains, expiring
**October 20, 2026 at 08:54:43.950 UTC**. AWS automatically created it because the
deleted table had PITR enabled; no manual backup was requested. AWS documents
35-day retention at no additional cost. [AWS backup policy](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BackupSummary.html)
Actual infrastructure billing was not measured, and cleanup does not reverse
earlier charges. Support history, SSO configuration, regional quotas and
AWS-managed keys remain outside the cleanup scope. Provider histories, metrics
and traces can outlive resource deletion; immediate physical erasure is not claimed.

[Sanitized AWS cleanup evidence](validation/aws-cleanup-2026-09-15.json) records
each stage, dependency coverage, retained backup and verification limits. The
first private Amplify absence probe used its CloudFormation ARN where `GetApp`
requires an app ID. Strict same-account/Tokyo conversion corrected only that
operator probe; arbitrary validation errors were never counted as absence.

## Databricks disposition

The actual Free Edition wheel/pipeline/Gold evidence was preserved before
deletion. Fresh identity and ownership checks matched one project job, four
managed Delta tables, the managed Volume and exact wheel hash, and the dedicated
development bundle. Twenty prior evidence files plus source exports and the
downloaded wheel were preserved privately.

Project cleanup passed and an independent invocation verified absence at
**08:58:57 UTC**. The job, bundle, four tables, wheel, Volume and synthetic schema
were removed. The pre-existing catalog and SQL warehouse remain; the warehouse
is **STOPPED**, with no active runs, queries or classic clusters. Cleanup started
no compute, bought no paid resource and changed no edition or payment setting.
Free Edition is grounded in the user's retained confirmation; no billing-console
revalidation or immediate physical-storage erasure is claimed.

[Databricks cleanup evidence](validation/databricks-cleanup-2026-09-15.json) and
[historical live validation](validation/databricks-wheel-2026-09-10.json) distinguish
successful execution from current resource disposition.

## Remaining external dependency

Tokyo Nova Lite account capacity remains the external model-validation blocker.
The Basic Support inquiry stays pending at its last verified checkpoint. No
Support plan was purchased, capacity provisioned, region changed, cross-region
inference enabled or model invoked in this milestone. Any future live-model
work needs separately confirmed usable capacity and a reviewed redeployment.
Institutional readiness additionally requires owned policies, effective
entitlements, independent model evaluation, staffed approval operations and
measured load, recovery and cost controls. See [production gaps](../PRODUCTION_READINESS.md).
