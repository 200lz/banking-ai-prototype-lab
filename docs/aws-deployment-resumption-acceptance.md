# Tokyo application deployment acceptance (2026-09-15)

The user reports applied Tokyo Lambda concurrency of 1000 and authorizes resuming
the existing application deployment. The earlier AWS freeze is superseded only
for this milestone. No new quota request, region change, runtime IAM weakening,
paid Support plan or unrelated resource is authorized. Databricks is unchanged.

1. Reverify the existing non-root `jdd-sandbox` SSO profile, expected account and
   role, and explicit `ap-northeast-1` target. Preserve raw responses privately.
2. Read actual Tokyo Lambda account settings. Mark the concurrency blocker
   RESOLVED only if applied and unreserved capacity allow reservation three while
   preserving AWS's unreserved minimum. Do not request 1001 again.
3. Review a fresh target CDK diff of the existing stack, including runtime IAM,
   Cognito/JWT, public API, encryption, logs, retention and cost. Keep reservation
   three, exact regional model IAM, required MFA and scoped JWT routes. Retain the
   already supported unconnected Amplify configuration if no Git connection exists.
4. Deploy only the reviewed Tokyo stack, retaining meaningful CDK IAM approval.
   Wait for terminal CloudFormation success; preserve any failures and fixes.
5. Verify outputs and run the existing safe corpus publisher: prevalidate every
   synthetic/public document, encrypted uploads, manifest last. Verify actual bytes.
6. Separate infrastructure smoke from model qualification. The existing full
   smoke invokes Bedrock; add an explicitly selected infrastructure-only mode that
   uses the existing deterministic prohibited-credit refusal before planning.
   It must require zero model tokens, zero model latency/cost, cited evidence and
   mandatory human review, while retaining all resource, audit and logging checks.
7. Verify real Lambda state/reservation/IAM, API Gateway JWT scopes, Cognito MFA
   and authorization, unauthenticated rejection, S3 corpus, DynamoDB correlated
   audit and CloudWatch records. Use a legitimate scoped Cognito access token;
   fabricated gateway claims cannot establish authentication. Keep any synthetic
   test-user credentials/token material private and suppress invitation messages.
8. Do not invoke Bedrock while Nova Lite capacity remains unavailable. Read-only
   capacity findings and historical failed qualifications stay separate from AWS
   infrastructure status. No live-model PASS can follow from refusal-path smoke.
9. Test any necessary harness/deployment corrections, run applicable local quality
   and secret/privacy checks, and update public evidence only from actual results.
   Record resources retained for the demo and preserve explicit cleanup steps.
10. Commit/push to main and require the real hosted GitHub CI run to pass before
    handoff. Report deployment, smoke, authentication and live-model statuses
    independently; preserve any remaining external blockers.
