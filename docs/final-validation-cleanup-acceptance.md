# Final validation, cleanup and portfolio acceptance

The user authorizes final validation and removal of this project's sandbox
resources after evidence is preserved. This milestone adds no product features.
All internal policies, companies, customer examples and records remain synthetic;
the public project implies no affiliation with a bank.

1. Complete the real Cognito authorization-code/PKCE handoff with MFA. A browser
   sign-in report alone does not establish the local code exchange: require its
   successful private completion marker and a valid scoped access token. Never
   publish credentials, authenticator data, codes, tokens or private identifiers.
2. Reverify the authorized non-root SSO identity and Tokyo target. Run only
   `python -m scripts.aws_smoke --infrastructure-only`, using private token state.
   Require all nine checks, authenticated refusal, correlated DynamoDB/CloudWatch
   records and zero model usage. Do not invoke Bedrock or infer model quality.
3. Preserve sanitized deployment, resource, OAuth, smoke, audit and logging
   evidence before removal. Retain previous failures and distinguish historical
   verification from the current post-cleanup resource state.
4. Inventory live application resources against the exact recorded stack and
   outputs. Delete only this project, handling retained S3 versions, DynamoDB
   deletion protection, Cognito identities and CloudWatch logs deliberately.
   Verify absence of project Lambda, API Gateway, Amplify, table, pool, logs and
   corpus objects. Never remove unrelated resources or close the account.
5. Once no application stack depends on bootstrap and no immediate deployment
   needs it, inventory and remove the reviewed CDKToolkit resources, including
   asset versions, ECR images/repository, deployment roles/policies and bootstrap
   parameter. Verify deletion and disclose anything deliberately retained. Leave
   Support history untouched; buy no Support plan or model capacity.
6. Preserve the real Databricks Free Edition evidence, then inventory and remove
   only this project's job, development bundle files, synthetic schema/tables,
   managed artifact Volume and wheel. Check ownership and active runs first;
   verify no project run/compute remains and the existing warehouse is stopped.
   Preserve unrelated workspace resources and the Free Edition boundary.
7. Polish README presentation and one compact Mermaid architecture diagram.
   Show verified AWS/data-platform boundaries prominently and disclose blocked,
   untested live Bedrock evaluation. Update the 3–5 minute interview sequence and
   a concise account of failures, lessons and production-readiness gaps.
8. Run all local regressions, formatting/lint/types, security/dependency scans,
   full source/history secret scans and documentation checks. Use actual counts.
   Commit, push main and require the final real hosted GitHub workflow to pass.
9. The final report must separately state OAuth, nine-check smoke, audit/log
   correlation, Bedrock, application/bootstrap/Databricks cleanup, retained items,
   final tests/scans, commit, hosted CI, repository, demo and external dependency.

If any required gate fails, preserve the failure and fix or report the concrete
blocker. Do not delete evidence-bearing resources before successful verification
and preservation, or label an incomplete check PASS.

## Observed CloudWatch delivery delay

The first authenticated run passed eight checks. Its API access record arrived
48.201 seconds after the request, after the verifier's original six five-second
waits had ended. The runtime's sixteen audit records were already delivered.
Before retrying, accept only a developer-verifier correction that tolerates this
observed delay with a finite polling bound, still fails missing/malformed logs,
and preserves all nine checks, exact correlation, zero model use and the existing
CLI. Add a delayed-delivery regression and run the smoke contract tests. Do not
change application behavior, runtime IAM, Cognito, region or reserved concurrency.
