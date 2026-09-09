# Development log

## Explicitly approved Tokyo CDK bootstrap (2026-09-09)

- The user explicitly approved the reviewed standard bootstrap, acknowledging
  persistent administrator-capable deployment roles. Conditions were same account,
  Tokyo only, no added trusted accounts, unchanged runtime IAM, complete inventory
  and preserved cleanup. This resolved the earlier automatic approval rejection;
  no further confirmation was requested for that exact action.
- Reverified the authorized non-root Identity Center role, Tokyo target and missing
  CDKToolkit/application stacks. The pinned template's SHA-256 still matched the
  completed review. Executed only the named Tokyo bootstrap with AWS-managed
  asset encryption, the explicit AdministratorAccess execution policy and no
  deployment/lookup trust arguments. CLI completed at 13:18:44 UTC with exit zero.
- Read actual CloudFormation, IAM, S3, ECR and SSM state. The stack is CREATE_COMPLETE,
  its template matches the reviewed template, and all 11 expected resources are
  CREATE_COMPLETE. All 25 checks passed at 13:21:27 UTC: five role trust policies,
  no additional trusted account, exact execution managed policy, private/versioned/
  encrypted/TLS-protected S3, immutable encrypted ECR, bootstrap version 32 and
  no customer-managed key. IAM roles are account-global; stack/S3/ECR/SSM are Tokyo.
- Verified the application stack remains missing and no application/runtime IAM
  source changed. No model invocation, Support case or Databricks call was made.
  The prior Lambda/Bedrock quota and Amplify prerequisites still block the broader
  application milestone; bootstrap PASS does not promote AWS application status.
- Preserved a full physical-ID inventory only in ignored local execution evidence
  and a public inventory with account identifiers redacted. Kept all 11 resources
  deliberately for planned sandbox deployment. S3 and ECR were empty when checked;
  no actual bill or zero-charge guarantee is claimed.
- Independent cleanup review noted that stack deletion retains the asset bucket
  while removing its separate TLS-deny bucket policy. The runbook checks identity,
  asset emptiness and stack protection before deletion, and separately removes the
  retained bucket. Four mocked cleanup cases passed; no cleanup was executed.
  [Bootstrap evidence and cleanup](cdk-bootstrap.md) record the full outcome.
- The preceding source commit `8e8c65f227cc9c876792ca835452d2a032d80fb2` passed
  hosted run `34354616969`, all 22 steps and artifact `evidence-and-infrastructure`.
  The Node.js 20 action-runtime warning remained non-blocking and unchanged.
- Publication checks passed: nine Markdown files parsed, one new JSON record
  validated, 99 local links/anchors resolved, LF/private-identifier checks passed,
  and source/history secret scans found no leaks. Runtime, infrastructure source,
  evaluation cases and test code have no changes in this bootstrap documentation
  update; full hosted regression remains the publication gate.

## Tokyo AWS and live Bedrock continuation (2026-09-09)

- Recorded [acceptance criteria](aws-live-acceptance.md) before deployment changes.
  Actual STS verified the authorized personal sandbox and non-root Identity Center
  role in `ap-northeast-1`; public evidence redacts account/principal identifiers.
  An initial local parser assumed the older `aws configure list` spacing; handling
  the installed CLI's colon separators correctly confirmed the region.
- Current hosted CI passed. All six existing local pre-deploy gates passed:
  lint, types, 284 Python/API/infrastructure and 26 frontend tests, 61-case
  deterministic evaluation, dependency/security audits and offline synthesis.
  Windows jsii cache permissions and sandbox registry access caused environment
  failures; a workspace cache and authorized public audit access resolved them
  without application changes. Original evaluation output was preserved locally.
- Actual Tokyo discovery returned 62 text-output models. The configured
  `amazon.nova-lite-v1:0` supports regional on-demand text inference and its
  agreement, authorization, entitlement and region checks are available. The
  availability API returned the canonical ID `amazon.nova-lite-v1`, while the
  model-detail API retained the exact versioned ID. This exposed a strict-ID
  comparison defect in the live preflight before any inference; any correction
  must retain exact model-detail verification and reject unrelated model IDs.
- Deployment review identified the missing CDKToolkit/application stacks, absent
  expected Amplify GitHub secret, and a regional Lambda concurrency quota of ten.
  The existing three-execution runtime reservation must remain intact; resolve
  quota/setup prerequisites instead of removing it. The Amplify SSR path requires
  GitHub authorization and a real Cognito scoped session for end-to-end smoke.
- Security review before changes: data permissions are scoped to corpus reads,
  audit PutItem and one regional Bedrock model; all API routes require Cognito
  scopes. Existing wildcard permissions cover Lambda's managed basic logging,
  X-Ray submission and Amplify log discovery. Bootstrap introduces administrator
  deployment permissions scoped by trust to the target sandbox. Retained corpus,
  audit, identity, logs and bootstrap assets require deliberate cost/cleanup work.
- Corrected the availability preflight to accept the API's canonical versionless
  ID while keeping exact versioned model-detail checks. Ten new regression cases
  cover the real response and reject mismatched IDs/versions. The 70 focused
  harness tests passed; final existing gates passed with 294 Python/API/infra
  and 26 frontend tests, formatting/lint/types and zero security/audit findings.
- Reviewed the pinned CDK v32 bootstrap template, five deployment roles, default
  administrator execution policy, private encrypted assets, same-account trust
  and retention. Automatic approval review rejected creating these persistent
  administrator roles without specific user approval. The bootstrap command did
  not execute; the concrete review and approval question were provided. No
  workaround or relaxed runtime/IAM boundary was used.
- Real target synthesis and read-only CloudFormation diff passed. The first diff
  referenced an incorrect local assembly path because the CLI overrides the
  CDK_OUTDIR environment default; the corrected absolute assembly path worked.
  No change set, bootstrap or application resource was created.
- The applied Lambda concurrency quota is ten. A no-Support-case request for 103
  was rejected because the API requires a value above its service default of
  1,000. The subsequent request for 1,001 with SupportCaseAllowed=false became
  NOT_APPROVED. The quota remains ten; support-backed escalation requires the
  separately requested authorization. The application still reserves only three.
- Verified Nova Lite's Tokyo standard on-demand rates from the versioned public
  AWS price catalog: $0.072/million input and $0.288/million output tokens. These
  replace illustrative global assumptions only for the recorded Tokyo attempts.
- While deployment prerequisites remained blocked, the independent local-audit/
  retrieval Bedrock harness attempted its single synthetic qualification. It
  failed and stopped before smoke/full evaluation. Strands initialization passed;
  one separately preserved diagnostic retry isolated ModelThrottledException.
  The installed SDK raises that exception for provider throttling. Raw SDK error
  messages and request identifiers were suppressed; their exact HTTP status and
  message were not captured and are not claimed.
- Actual Service Quotas then showed all 166 queried regional on-demand/daily-token
  entries at zero, including Nova Lite's request, token and daily limits. No
  further invocation retry, model switch, three-case smoke or twenty-case suite
  was attempted. Availability/entitlement alone does not establish usable capacity.
  Both failure artifacts retain incomplete usage/cost, safe abstention and a
  passing content-free telemetry probe; reported zeros are not zero-cost success.
- Updated public cloud, cost, evaluation and status evidence from these actual
  results. AWS deployment and live evaluation remain NOT TESTED; qualification
  failure is explicit. Databricks workspace remains NOT TESTED. No application
  or bootstrap resources were left running, and the deployment/cost decision
  remains pending a successful authorized deployment.
- Preserved the earlier missing-credentials preflight unchanged and wrote a
  separate redacted Tokyo record. Independent review found no further code or
  security defect. Public evidence checks passed for eleven Markdown files,
  seven JSON files, 94 local links/anchors, LF endings and excluded private
  identifiers. Source and complete-history secret scans passed. Original failed
  artifact bytes remain locally preserved; public copies only normalize LF.

## Hosted GitHub CI verification and status update (2026-09-09)

- Acceptance criteria for this documentation milestone: independently verify
  original run `34344534926` with `gh`, confirm hosted Linux execution, exact
  commit, successful gates and artifact; update only the four requested status
  documents and add a real workflow badge; preserve AWS, live Bedrock and
  Databricks workspace as NOT TESTED; run local documentation checks; commit,
  push and verify the newly triggered hosted workflow before handoff.
- GitHub CLI run/jobs/artifacts/check-run annotation queries independently
  confirmed [run 34344534926](https://github.com/200lz/banking-ai-prototype-lab/actions/runs/34344534926)
  for commit `827888ab0d3c82f937d8106b51f8bf04f4a3fcc4` on `main` in the public
  `200lz/banking-ai-prototype-lab` repository. Workflow `Quality and safety
  regression` (`.github/workflows/ci.yml`), run number 1, job `quality`
  (`102442885999`) completed successfully at 11:21:25 UTC. All 22 recorded steps
  passed on GitHub-hosted Linux: label `ubuntu-latest`, runner
  `GitHub Actions 1000000254`, group `GitHub Actions`.
- Supplementary job logs, read through the connected GitHub app, confirmed Ubuntu
  24.04.5 LTS / image `ubuntu-24.04` version `20260907.300.1`, 284 passing Python
  tests in 8.94 seconds, 26 passing frontend tests and container validation PASS.
- Actual gates: exact dependency installation; formatting/lint/types;
  Python/API/infrastructure/frontend tests; smoke/full evaluation; security
  analysis/dependency audits; Next.js production build; credential-free CDK
  synthesis; checksum-verified scanner; source/complete-history secret scans;
  fresh Docker build, health, scenarios, telemetry, restart, cleanup; artifact
  preservation. Actual artifact `evidence-and-infrastructure`, ID `10101336517`,
  119,231 bytes, was unexpired when checked. Its SHA-256 digest is recorded in
  [REPORT](../REPORT.md#github-hosted-ci-pass).
- Confirmed the non-failing Node.js 20 deprecation annotation for the pinned
  checkout/setup-python/setup-node/upload-artifact actions. GitHub forced their
  execution onto Node.js 24. Classified **NON-BLOCKING**, retained as maintenance,
  and made no workflow/action changes or claim that the warning was fixed.
- Replaced current GitHub NOT TESTED/publication-blocked statements with verified
  PASS and a real `main` workflow badge. Earlier milestone records remain
  historical. No product functionality, AWS work, live Bedrock inference or
  Databricks workspace execution is part of this update.
- Local documentation checks passed: `git diff --check`, Prettier Markdown
  `--debug-check` for all four edited files, and checks of 50 local links/anchors,
  LF endings, balanced code fences, original-run metadata, badge branch,
  unchanged capability/cloud statuses and documentation-only scope.
- The local CLI and Git Credential Manager had no saved GitHub login. Public
  `gh api` queries still verified run metadata; the existing authenticated GitHub
  app supplied job logs and write access for publication. No credential was
  copied into repository files. The local source secret scan passed with no leaks.

## Continuation: container and data-platform validation (2026-09-09)

- Read the continuation request and recorded milestone acceptance criteria in
  `docs/continuation-acceptance.md` before implementing new features. Preserved
  the 61-case corpus; a fresh continuation baseline passed all gates.
- Safely started the installed Docker Desktop. Linux Engine 20.10.17 became
  available; no reset or reinstall was needed. Fresh API, web and collector
  images built. Real runtime checks then found a dropped calculation response:
  the web proxy's Zod parser omitted deterministic calculation provenance.
  The failed container artifact is retained while a regression fix is tested.
- Runtime dependency installation revealed that the lock generator discarded
  transitive extras such as `PyJWT[crypto]`. Fixed closure traversal and added
  regression tests so image builds do not silently resolve unpinned dependencies.
- Added official Databricks SDK 0.136.0 with exact locks. Its protobuf constraint
  selected 6.33.6; `pip check` and the complete locked Python vulnerability audit
  passed. The application retains local mode without Databricks credentials.
- Independent financial review identified that ingestion time could mask old
  business periods. Requested month-end business freshness and a regression;
  an ingestion timestamp must not imply current financial data.
- The Windows Next.js build stalled on files held by the existing preview.
  Releasing the owned preview process allowed a clean production build and
  restart. The actual policy-workbench browser screenshot was saved; it is not
  a rendered mockup.
- Installed checksum-verified official GitHub CLI 2.100.0 and Gitleaks 8.30.1 in
  ignored local tooling. CLI authentication was absent and browser sign-in was
  requested. Source-candidate secret scan found no leaks. CI actions now use
  immutable commit hashes and include source/history scans; hosted CI was still
  unverified at that point, before a real push and successful hosted run.

- Container acceptance subsequently passed all four fresh runtime image builds,
  three service health checks, six required/safety scenarios, exact controller
  stage export, restart audit persistence, identical answer and clean shutdown.
  Docker 20 reallocated an ephemeral port on restart; fixed verifier rediscovery
  and retained its failing artifact. An additional seventh SME scenario passed
  against identical image IDs, without falsely calling the reuse a fresh build.
  Runtime logs reported zero errors/warnings. OS image vulnerability scanning is
  separate and was not executed.
- The late unsafe-source branch initially retained a Gold profile after clearing
  policy evidence. Independent review reproduced this; the guardrail now clears
  the profile as well and a regression preserves that failure-path guarantee.
  The 53 financial tests and native browser/profile checks passed. Actual local
  RAW20 → Silver18 → Gold3 computation is recorded separately from workspace work.
- After Docker PASS, installed the signature-verified AWS CLI 2.36.41 as ignored
  workspace tooling. Actual CLI version, region and STS preflight found no
  configured region or credentials. SDK lookup found zero profiles and no config
  files. No account was selected, bootstrapped or deployed, and no live model or
  Databricks workspace request occurred. External authentication/setup was
  requested while local work continued.
- Full repository Python/API/CDK regression after analytics: 175 passed, 87%
  statement coverage. The final report records later counts including cloud-tool
  contract tests. The unchanged 61-case corpus remains the deterministic baseline.

- Final cloud-verifier review added 60 live-harness and 49 AWS-smoke contract
  tests. It found mismatched trace attribute names, insufficient telemetry checks,
  aggregate qualification masking individual failures, local-mode result labeling
  and output filenames that could overwrite the baseline. The harness now checks
  actual metadata schemas, preserves local/live artifacts separately, qualifies
  one → three cases before the full twenty, and ignores custom emulator endpoints.
  Actual unconfigured commands exit 2 with NOT TESTED and create no live result.
- Final complete suite: 284 Python/API/infrastructure tests, zero failures or
  skips; 90% statement coverage (1,377 statements, 134 missing). Frontend 26 tests,
  formatting/lint/types/production build and restored native preview passed.
  Final 61-case local and 20-case smoke evaluations passed all gates; measured
  full-set median 13.835ms, p95 19.101ms, zero model tokens/cost. Bandit reported
  no findings at any severity and locked Python/web/CDK dependency audits passed.
- At that point, the final report and authoritative matrix retained NOT TESTED
  statuses for unauthenticated GitHub, AWS/Bedrock and Databricks. No cloud evidence
  or model measurements were fabricated. Actual desktop/mobile screenshots and
  an interview sequence make the implemented local/container scope reviewable.

- Created the requested implementation milestone commit (`ae07e2c`); the existing
  repository had no commits or remote. Source and Git-history Gitleaks scans
  detected no leaks. Used the connected GitHub account's public noreply address,
  not its private email. CLI sign-in was unavailable then, so no push occurred.
- Git's Windows autocrlf warnings exposed a future checkout/provenance risk.
  Confirmed raw financial/evaluation source bytes currently match Git; normalized
  remaining generated text and added an explicit LF policy so future Windows
  checkouts cannot change raw-byte hashes. Lock/Gold writers now explicitly emit
  LF. Updated recorded lock hashes to those canonical bytes; all 55 affected
  financial/lock tests and formatting/lint checks passed.

## 2026-09-09 — acceptance and architecture baseline

- Started from an empty Git repository. Defined acceptance criteria before large
  features and a shared API/retrieval contract to support parallel implementation.
- Chose deterministic orchestration around an optional Strands/Bedrock planner:
  the model proposes bounded evidence/tool selections; code owns safety decisions.
- Local measurements will describe a deterministic baseline, not LLM capability.
- Environment: Python 3.11.5, Node 20.10.0, npm 10.2.3. GNU Make and uv absent.
  Docker CLI exists but cannot read its user config; daemon availability pending.
- Public-source research found 2026 FinCEN exceptive relief. Corpus notes must
  avoid treating historical beneficial-ownership guidance as unqualified current
  law. Public content is attributed, dated educational context only.

## Milestone 1 — retrieval and controller

- Implemented local lexical retrieval and the S3 manifest adapter behind one
  protocol. Ten initial retrieval tests passed, including classification-before-
  ranking, superseded/future versions, integrity, object size and prefix escape.
- Added twelve source documents: ten entirely synthetic policies and two dated,
  attributed public summaries. The document schema prevents invented external
  links for synthetic policies and restricts public URLs to curated publishers.
- Implemented the real nine-stage workflow, five read-only tools, strict API,
  deterministic Decimal arithmetic, citation/source checks and review routing.
  The Strands adapter returns only known evidence IDs and bounded flags, with no
  business execution tools. Whole source context is preserved to retain caveats.
- First dependency install failed with sandbox socket restrictions. An approved
  registry download installed dependencies into the project virtual environment.
  Exact runtime and development versions are captured in separate locks.

## Milestone 2 — independent evaluation exposed failures

- Authored 61 synthetic cases before evaluating the completed controller. The first
  run scored 90.16% answer checks, 97.56% recall, 88.52% policy compliance and
  86.89% expected escalation. Preserved `evals/results/initial-baseline.json`.
- Missing-information wording and DTI inputs failed to trigger review; two intent
  synonyms were missed; a retrieved SYSTEM role spoof was treated as evidence.
  General normalization/routing rules and regression tests corrected these issues.
  No expected answer table was introduced into runtime code.
- Subsequent local evaluations passed all gates. A separate review then exposed
  scorer weaknesses: substring citations, trusted missing-information prose,
  calculation formula/operand tampering, and incomplete model cost. Strengthened
  the independent scorer and added mutation tests that must score these as failures.

## Milestone 3 — security hardening and observability

- A citation could drop preceding negation while retaining a substring. Requiring
  complete source sentences and preserving full selected source context closes
  that attack. Hash checks do not prove semantic relevance or source truth.
- Additional adversarial tests found metadata PII leaks, validation-field-name
  echo, public-only planner selection, partial-topic/calc omission, boolean/float
  coercion, extreme decimal exponents, and incomplete-cost propagation. Fixed
  the boundaries and added focused tests; inputs require decimal strings/integers.
- Added a parent OTel trace with nine stage spans, tool spans and latency/token/
  cost/review attributes. Filter SDK spans and suppress raw SDK logging; audit
  metadata remains content-free. Model failures expose incomplete cost explicitly.
- Unit/API/retrieval/scorer tests, Python formatting/lint/type checks and Bandit
  passed. Public Python vulnerability audit found no known issues in the lock.
  Starlette's TestClient emits an upstream AnyIO deprecation warning; tests pass.

## Milestone 4 — web and AWS deployment compatibility

- Built a Next.js evidence workbench with live server proxy, presets, typed
  calculations, trace/tools, risks, missing details, confidence and cost metrics.
  Added server-side Cognito authorization-code/PKCE flow and secure token cookies.
- Initial Next 16 choice was incompatible with Amplify's documented support.
  Verified AWS guidance and switched to patched Next 15.5.25. A PostCSS transitive
  advisory required a compatible 8.5.28 override; npm audit then found zero issues.
- Next's legacy lint wrapper required EOL ESLint 9. Used maintained ESLint 10 with
  matching Next rules and compatible TypeScript/React hooks plugins; lint, type,
  format, auth/proxy tests and production builds passed.
- Live HTTP smoke found that Next canonicalized Request.url's host, rejecting
  legitimate 127.0.0.1 requests. Local origin validation now requires a matching
  loopback Host; cloud validation still uses the configured HTTPS application
  origin. Added regression coverage before repeating browser acceptance.
- CDK implements encrypted/versioned private S3, protected DynamoDB, restricted
  runtime IAM, authenticated/throttled API, Cognito MFA, Amplify, logs, dashboards
  and alarms. Eleven initial infrastructure assertions and synth passed offline.
- Initial CDK/constructs versions conflicted; corrected the constraint. An OAuth
  assertion incorrectly expected a literal instead of a CloudFormation reference;
  corrected the test to inspect the actual synthesized scope relationship.
- System Node 20.10 was outdated; used bundled Node 24.19 for verification and
  selected Node 22 for container/Amplify/CI builds. Windows sandbox process access
  required approved offline CDK tests; no AWS resource was created.

## Local execution and release evidence

- Compose validates, but Docker Engine is not running on this host. The older
  Docker CLI initially also denied config access and panicked on a formatted info
  request; a plain authorized check established the missing daemon. Native local
  servers provide the functional demo; container execution remains unverified.
- `make` is absent on this Windows host. The shared `scripts/tasks.py` implements
  every Make target and is used for native verification. CI is configured for
  Linux Make and container smoke checks; no GitHub Actions run has been claimed.
- Deployment requires a real account/region, concrete CDK diff and IAM review,
  then publishes the corpus manifest last. No account was selected or provisioned,
  no GitHub remote was published, and no billable model invocation was performed.
- The final `REPORT.md` records verified results and the remaining cloud/container,
  semantic safety, privacy, review operations and production-readiness limitations.

## Final verification and handoff

- Independent deployment review found that corpus publication could start before
  validating later entries or changed bytes. Added full schema/key/duplicate/ID/
  hash preflight before creating an AWS client, plus twelve developer CLI/publish
  regression tests. Missing/invalid account, region or CLI refuses deployment.
- Confirmed the collector image exists for AMD64/ARM64 and all 55 Linux runtime
  dependency wheels resolve for the Python 3.11 target. This is dependency/manifest
  validation, not an actual Docker build. Added nested secret-file exclusions.
- Added dedicated Lambda audit JSON mirroring at INFO without enabling SDK/root
  debug logs. Documentation now distinguishes warm S3 snapshot verification from
  fresh object reads and explicitly records the 60-second revocation delay.
- Final combined Python/API/retrieval/evaluator/CLI/CDK suite: 109 tests passed,
  with 87% statement coverage over services/packages. Web: eighteen tests passed,
  formatting/lint/TypeScript/production build passed, npm audit zero findings.
- Browser acceptance verified onboarding review and six excerpts, a 30.00% DTI
  result with source/calculation provenance, and prohibited-credit refusal.
  The final responsive layout had no horizontal overflow at the tested mobile
  viewport. An independent native HTTP web-to-API smoke check passed.
- Final full evaluation: all 61 cases passed the configured quality/cost-completeness
  gates; 20 smoke cases passed. Latest results have zero model tokens/cost because
  mode is local. Measurements remain development-set baseline results.
