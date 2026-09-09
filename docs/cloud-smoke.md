# AWS smoke verification

This verifier is a postdeployment acceptance check, not a deployment command.
Implementation acceptance criteria, recorded before implementation:

- Read only the named deployed stack and its resources; reject missing region,
  token, outputs, unexpected endpoints, or mismatched deployed outputs before
  sending a bearer token.
- Check CloudFormation completion, the reviewed S3 corpus and manifest, Lambda
  configuration, Cognito, and JWT protection on every application route.
- Make one synthetic suspicious-activity query and independently validate its
  response schema, source excerpts, nine stages, real model usage, and escalation.
- Query the exact response audit partition and bounded, correlated CloudWatch
  events. Follow bounded pagination and fail if verification is incomplete.
- Emit only check names, statuses, generic failure codes, counts, and model
  measurements. Never emit tokens, account/resource/request IDs, raw log events,
  SDK exception messages, prompts, or customer records.
- Test through injected clients and transport without AWS calls. Unit-test
  success is contract evidence only; it must never become a live AWS result.

The authenticated query is read-only operational guidance. It does create the
normal audit and telemetry records and can incur Bedrock and AWS request charges.
It cannot approve credit, move money, change customer records, or grant approval.

## Run after deployment

Use the same reviewed checkout as the deployment, Python 3.11+, and the project
dependencies. The CDK deployment must have written `.runtime/cloud-outputs.json`
and published the reviewed corpus. The verifier uses the `BankingAiPrototypeLab`
stack and the existing `ApiUrl`, `CorpusBucket`, `AuditTable`, `UserPoolId`,
`UserPoolClientId`, and `WebUrl` outputs. Lambda and log-group names are resolved
through that stack's resource list; they are never guessed or discovered through
account-wide scans.

Authenticate the operator using short-lived AWS credentials through the normal
AWS provider chain. Set `AWS_REGION` explicitly; `AWS_DEFAULT_REGION` alone is
insufficient. Set `AWS_SMOKE_ACCESS_TOKEN` in the process environment to an
unexpired Cognito **access token** obtained through the deployed employee login
with `banking-ai/query`. Do not place tokens in command arguments, checked-in
files, screenshots, shared terminals, or reports. The script does not create a
user, disable MFA, log in, refresh a token, or bypass the employee approval process.

```sh
python -m scripts.aws_smoke
```

The token goes only to the exact commercial AWS `execute-api` HTTPS endpoint
whose API ID matches the deployed stack. Redirects, endpoint configuration
overrides, custom API hosts, other-region hosts, URL credentials, and HTTP proxies
for the bearer request are disabled. This verifier intentionally does not support
GovCloud, China partitions, private API endpoints, or custom API domains.

The JSON output has no tokens, account IDs, resource names, request IDs, source
text, or raw log messages. It is suitable for a reviewed validation artifact.
Exit codes are:

| Code | Meaning |
| --- | --- |
| `0` | Every named check passed against the real clients selected by the CLI. |
| `1` | A called check failed or a service was unavailable; later checks remain `NOT TESTED`. |
| `2` | Required configuration or credentials are unavailable; no successful cloud validation is claimed. |

`execution: live_aws` identifies the CLI path; it does **not** imply success.
Read `status` and each check. Injected unit tests always use
`execution: injected_clients`, even when their simulated contracts pass.
The failure reason is deliberately generic because AWS exceptions can contain
identifiers or sensitive payloads. Diagnose permissions or deployment drift
through the approved operator console without copying raw output into the repo.

## What is verified

CloudFormation must be fully created or updated, tagged for this synthetic lab,
and agree with every consumed output and resource identity. The S3 bucket must
block public access and enable versioning; every encrypted document object must
match its SHA-256 manifest and the exact reviewed document in this checkout.

Lambda must be active with Bedrock/S3/gateway modes, the expected corpus and audit
table, message-content capture disabled, bounded timeout/memory, and positive
configured token rates. Cognito must require MFA, disable self signup, and use a
public authorization-code client with the expected callback and scopes. Every
API route must use the exact Cognito JWT audience/issuer and query scope. The
integration must target the stack's Lambda and the access-log format must contain
only the defined metadata fields.

One unauthenticated query must return 401/403. Only then is one authenticated
synthetic suspicious-activity query sent. HTTP 200 alone is insufficient: the
response must contain nine successful stages, the expected tool names, actual
Bedrock-mode token and latency metrics, complete positive estimated model cost,
human review, and citations independently checked against the retrieved S3
documents. A local-mode response or an abstention cannot pass this check.

The verifier queries only the returned request's DynamoDB partition using a
strongly consistent `Query`. It checks the nine stages, tools, review decision,
model counts, source IDs, and hashes. It reads only the two stack log groups and
filters for the application request ID and API Gateway request ID within a bounded
time window. Both groups must retain logs for 30 days; matching application audit
events and the successful API access event must be present without content or
credential fields.

CloudWatch delivery gets up to six five-second waits. Each paginated read is
limited to five pages and 1,000 returned records; repeating continuation tokens
fail. Individual SDK calls have connection/read timeouts and at most two attempts.
The API response is limited to 1 MiB and a 35-second request timeout. Ingestion
that exceeds the polling window produces a failed verification, never a false
pass. Rerunning makes another synthetic query and another set of audit events.

## Operator permissions and limits

The verifier needs a separate inspection role, not the runtime Lambda role:

- `cloudformation:DescribeStacks`, `cloudformation:ListStackResources` on the named stack.
- `s3:GetBucketPublicAccessBlock`, `s3:GetBucketVersioning` on its bucket and
  `s3:GetObject` on `corpus/*`.
- `lambda:GetFunctionConfiguration` on its function.
- `cognito-idp:DescribeUserPool`, `cognito-idp:DescribeUserPoolClient` on its pool.
- API Gateway management `apigateway:GET` for the named API, routes, authorizer,
  integration, and default stage.
- `dynamodb:Query` on the named audit table.
- `logs:FilterLogEvents` on the two named log groups and
  `logs:DescribeLogGroups` (this AWS operation requires resource `*`; the script
  supplies the exact group-name prefix and checks the exact returned name).

The token separately authorizes the fixed `POST /v1/query` operation. No IAM
write/delete, financial action, user-creation, or direct Lambda/Bedrock invocation
permission is required by the inspection role. AWS request and log reads can
still incur charges. The agent's normal execution identity performs its existing
model invocation and audit writes when the authenticated query runs.

This is one smoke case, not a live evaluation dataset, load test, penetration
test, authentication usability test, or proof of all logging privacy. It does not
verify Amplify hosting/builds, browser login/MFA enrollment, expired or wrong-scope
tokens, regional failover, alert delivery, X-Ray/remote OTel exports, Databricks,
or billed cost. Those remain separate acceptance evidence. The cost field is
the application's estimate from reported tokens and configured rates.

## Offline regression checks

```sh
python -m pytest tests/unit/test_aws_smoke.py -q
python -m ruff check scripts/aws_smoke.py tests/unit/test_aws_smoke.py
python -m mypy scripts/aws_smoke.py
python -m bandit -q scripts/aws_smoke.py
```

Tests inject every client and HTTP response; they also validate request argument
shapes against the installed botocore service models without acquiring credentials.
No AWS call or live deployment success is implied by these tests.

AWS references: [JWT route scopes](https://docs.aws.amazon.com/boto3/latest/reference/services/apigatewayv2/client/get_routes.html),
[JWT authorizer configuration](https://docs.aws.amazon.com/boto3/latest/reference/services/apigatewayv2/client/get_authorizer.html),
[bounded log-event pagination](https://docs.aws.amazon.com/botocore/latest/reference/services/logs/client/filter_log_events.html).
