# AWS sandbox validation

Date: 2026-09-09. **AWS deployment: NOT TESTED. Live Bedrock: NOT TESTED.**

The Docker gate passed before AWS preflight began. See
[actual container evidence](validation/containers-2026-09-09.json).

## Executed preflight

| Check | Observed result |
| --- | --- |
| AWS CLI | Official signed Windows MSI verified, extracted into ignored workspace tooling; `aws-cli/2.36.41 Python/3.14.6 Windows/11 exe/AMD64` |
| `aws configure get region` | No configured region |
| `aws sts get-caller-identity --region us-east-1` | Unable to locate credentials; no identity was obtained. The region argument selected the STS endpoint only, not a deployment target. |
| Boto3 credential-provider lookup | No credentials, zero profiles, no AWS config or credentials file |
| Sandbox account intent | No account available to assess; no production/sandbox assumption made |
| Bootstrap / CloudFormation / IAM / Bedrock access APIs | NOT TESTED because authenticated account and region are missing |
| CDK diff / bootstrap / deploy | NOT TESTED; no cloud mutation attempted |

Account identifiers, credentials and principals are not included in this report.
No AWS resource or live model usage was created during this session.

## Intended deployment and locally executed checks

The existing `BankingAiPrototypeLab` CDK stack defines Bedrock, S3, DynamoDB,
Lambda, API Gateway, Cognito, CloudWatch and Amplify. Confirm the actual configured
stack name in `infra/cdk/app.py` before deployment. Offline security assertions
check scoped runtime IAM, private encrypted/versioned S3, encrypted audit storage,
JWT/scopes, mandatory MFA, throttling, runtime limits and 30-day logs. Actual
synthesis and the local non-root, network-disabled Lambda image probe passed;
these do not verify any deployed AWS behavior.

The sandbox retains corpus, audit and log resources deliberately. Retention is
safer for evidence but creates cleanup/cost work after stack destruction. General
runtime egress, unactioned alarm notifications, non-WORM audit storage and the
absence of a production collector remain limitations. Regional model access and
Amplify compatibility must be checked in the chosen account before provisioning.

## Exact remaining external setup

Configure an authorized isolated sandbox through the AWS credential provider,
preferably `aws configure sso --profile banking-ai-sandbox`, then
`aws sso login --profile banking-ai-sandbox`. Supply the intended profile/region
and confirm the account is disposable development. Do not paste access keys.

The extracted CLI on this workstation is
`.runtime/tools/aws-cli/extracted/Amazon/AWSCLIV2/aws.exe`; it is ignored tooling,
not a portable repository dependency. Other developers can install the official
[AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

Then execute the [deployment runbook](cloud-deployment.md): all local gates,
synth, account/region identity check, bootstrap inspection, concrete CDK diff and
IAM/public-exposure review, bootstrap if needed, and the smallest existing stack.
`make deploy` preserves CDK's security approval prompt. Publish the synthetic
manifest and configure an authorized Cognito demo user/session.

`make aws-smoke` (Windows: `.venv\Scripts\python scripts/tasks.py aws-smoke`)
performs the resource/auth/audit checks described in [cloud-smoke.md](cloud-smoke.md).
It requires actual stack outputs, credentials, region and an access token supplied
through the environment. An authenticated synthetic query creates ordinary audit
and log events and can incur model cost if the stack uses Bedrock. Missing setup
is NOT TESTED, never PASS. Record actual results here after execution.

Cost drivers are Lambda duration, API requests, corpus/audit storage, CloudWatch,
Amplify/Cognito and model usage; [COST.md](../COST.md) gives the assumptions. No
measured cloud bill or regional live latency exists yet.
