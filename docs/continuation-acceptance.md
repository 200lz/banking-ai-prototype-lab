# End-to-end continuation acceptance criteria

Defined before implementation, 2026-09-09. Preserve the existing 109 Python,
18 frontend, and 61 deterministic evaluation cases. Never label planned or mocked
work as executed integration. All financial information remains synthetic.

## 1. Containers

Inspect existing images, runtime users, networking, health checks and telemetry.
Build without cache, run an isolated Compose project, check all expected health
signals, exercise five representative scenarios (including an injected retriever
fixture inside the API image), verify content-free OTel, restart, and shut down.
Provide a repeatable container-smoke command and measured evidence. If the engine
cannot be safely started, record the actual blocker and exact operator action.

## 2. Hosted CI

Preserve and complete the current quality/security/container workflow without
requiring cloud credentials for PRs. Scan tracked content before the first commit.
Use authenticated GitHub CLI to publish only if available; verify a real hosted
run and fix actual failures. No badge before a hosted workflow exists. Authentication
blockers must specify the minimum human action and are not PASS.

## 3. AWS sandbox

Only start after container PASS or a documented external Docker blocker. Inspect
credentials/account intent without displaying secrets or committing account IDs.
Require an unambiguous sandbox target before synth/diff/bootstrap/deploy. Add a
read-only aws-smoke verifier and record real resource/auth/audit checks, or the
specific credential/environment blocker. Offline synth is not deployment evidence.

## 4. Live Bedrock

Verify availability/access programmatically, run one harmless case then a small
smoke, then approximately 20 representative cases. Preserve failed results and
actual usage/latency/cost. Keep live outputs separate from baseline. No credentials
means NOT TESTED, not zero-cost live success.

## 5. Governed financial analytics

Add synthetic SME data with raw provenance, deterministic Bronze/Silver/Gold
normalization and formulas, missing/invalid/duplicate/stale handling, and a strict
read-only financial_profile_tool(company_id). Provide local and genuine Databricks
adapters plus reproducible native project configuration. The LLM must not compute
features, select SQL, access raw records or decide credit. Profile-backed answers
retain quantitative provenance and policy citations; review is mandatory. Cover
formulas, schema, invalid ID, missing/stale data, outage, prompt minimization and
approval refusal. Real Databricks PASS requires an actual job and queried Gold
output; without a workspace finish local code/tests and document setup.

## 6. Portfolio handoff

Re-run relevant complete suites, record actual counts, and generate one authoritative
PASS/FAIL/NOT TESTED/NOT APPLICABLE matrix with evidence. Finalize README's requested
order, architecture decisions, 3–5 minute interview demo, milestone reports,
development log and final REPORT. Commit successful local milestones separately;
never commit credentials, private cloud identifiers, or fabricated external results.
