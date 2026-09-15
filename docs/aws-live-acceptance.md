# AWS and live Bedrock validation acceptance (2026-09-09)

Historical acceptance and execution checkpoint. The later
[final validation and cleanup](final-validation-cleanup.md) records successful
application deployment, nine-check infrastructure smoke and verified removal.
Live Bedrock remains separately blocked and untested.

Scope: deploy and validate the existing synthetic portfolio architecture in the
explicitly authorized personal Tokyo sandbox. No new product features, unrelated
services, real banking data or Databricks workspace work.

1. Actual STS and configuration checks must match the authorized account,
   `jdd-sandbox` Identity Center assumed role and `ap-northeast-1`. Root or any
   identity/region mismatch stops deployment. Public evidence redacts account,
   principal and credential identifiers.
2. Actual regional Bedrock discovery and access APIs must establish a compatible
   regional on-demand text model. Select current verified token rates before
   inference; cross-region profiles require explicit boundary review.
3. Hosted CI and existing local formatting/lint/type/test/evaluation/security/
   synthesis gates must pass before resource creation. Preserve genuine failures.
4. Inspect actual CDKToolkit state. If missing, review the bootstrap template and
   bootstrap only the authorized account/region; verify successful stack state.
5. Review a real target-environment CDK diff, documenting IAM, network/auth,
   encryption, logs, retention and cost concerns before any corrective changes.
   Keep meaningful CDK IAM approval; no security-boundary weakening.
6. Deploy the existing stack, publish the reviewed synthetic corpus, and configure
   the existing Amplify/Cognito demo path. Diagnose real failures and apply only
   necessary correctness, security or deployment fixes with regressions.
7. Run the existing AWS smoke suite against real deployed resources, including
   authorized and unauthorized API paths, runtime execution, corpus, audit,
   logs, Cognito and IAM. AWS becomes PASS only after deployment and smoke pass.
8. Execute exactly one safe synthetic Bedrock qualification request first, then
   the existing small smoke set, then the unchanged twenty-case live evaluation.
   Require bounded planning, deterministic citation/tool controls, escalation,
   measured latency, reported tokens and complete estimated cost accounting.
   Unknown failed usage remains unavailable/incomplete, never zero-cost success.
9. Preserve separate real single/smoke/suite artifacts and failures. Compare live
   results with the 61-case deterministic development baseline without changing
   expected answers to improve scores. The baseline is not an LLM benchmark.
10. Make an explicit keep-for-demo or destroy decision, identify ongoing and
    retained resources/costs, and provide the exact cleanup runbook. Update public
    status only from actual evidence; Databricks workspace remains NOT TESTED.
11. Commit and publish evidence/configuration changes to `main`, then verify the
    newly triggered real hosted GitHub workflow passes before handoff.

The user's deployment instruction authorizes the reviewed existing sandbox
architecture and necessary bootstrap. A concrete IAM diff is still reviewed
before accepting CDK's deployment prompt. Credentials remain in providers or
secret stores and are never placed in public evidence.

Execution outcome: automatic approval review initially required specific approval
for the standard bootstrap's persistent administrator roles. The user then
explicitly approved that boundary, and Tokyo bootstrap completed successfully.
The [execution and inventory](cdk-bootstrap.md) record all 11 resources and 25
passing checks. At that September 9 checkpoint, application deployment remained
blocked by the recorded prerequisites; no runtime IAM boundary was relaxed.
