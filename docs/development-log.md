# Development log

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
  ignored local tooling. CLI authentication is absent and browser sign-in was
  requested. Source-candidate secret scan found no leaks. CI actions now use
  immutable commit hashes and include source/history scans; hosted CI remains
  unverified until a real push and successful hosted run.

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
- The final report and one authoritative matrix retain external NOT TESTED
  statuses for unauthenticated GitHub, AWS/Bedrock and Databricks. No cloud evidence
  or model measurements were fabricated. Actual desktop/mobile screenshots and
  an interview sequence make the implemented local/container scope reviewable.

- Created the requested implementation milestone commit (`ae07e2c`); the existing
  repository had no commits or remote. Source and Git-history Gitleaks scans
  detected no leaks. Used the connected GitHub account's public noreply address,
  not its private email. CLI sign-in remains unavailable, so no push occurred.
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
