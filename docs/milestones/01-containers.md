# Milestone 1: actual container verification

**PASS — executed on 2026-09-09.** The API, Next.js web application, and
OpenTelemetry collector were built without cache, started together, exercised,
restarted, and removed. The Lambda image was also built without cache and probed
locally. This is deterministic container validation; it does not establish AWS,
live Bedrock, or Databricks workspace success.

Acceptance criteria were recorded before implementation in
[continuation-acceptance.md](../continuation-acceptance.md). Machine-readable
evidence is in [the fresh-build result](../validation/containers-2026-09-09.json)
and [the governed SME result](../validation/container-sme-2026-09-09.json).

## Commands and environment

Docker Desktop was safely started using its signed installed executable. The
actual server reported Docker Engine `20.10.17`, Linux, AMD64 under WSL2. No
engine reset, reinstall, or global prune was performed. Existing native processes
on ports 3000 and 8000 were left running; validation used isolated Compose project
`banking-ai-validation-ae306e2633` and ephemeral loopback ports.

```sh
.venv/Scripts/python.exe scripts/verify_containers.py --output docs/validation/containers-2026-09-09.json
```

The script executed `docker compose ... build --pull --no-cache` and
`docker build --pull --no-cache -f infra/cdk/Dockerfile.lambda ...`. The successful
fresh run lasted 151.5 seconds, including build, health checks, scenarios, restart,
and shutdown. Compose build took 70.463 seconds; Lambda build took 24.389 seconds.
These are measurements from this workstation, not deployment performance targets.

For future full validation use `make container-smoke`, or on Windows
`python scripts/tasks.py container-smoke`. The current verifier includes the SME
scenario as well as the original six. Ordinary CI invokes this same script.

The supplemental SME run reused the exact image IDs from the fresh build:

```sh
.venv/Scripts/python.exe scripts/verify_containers.py --project banking-ai-validation-ae306e2633 --skip-build --output docs/validation/containers-financial-2026-09-09.json
```

`--skip-build` deliberately exits nonzero and labels the overall fresh-build claim
`NOT TESTED`; its seven scenario results, health, restart, and shutdown checks
all passed. The separate SME evidence links both runs and records verified image
identity, so this supplemental execution is not presented as another fresh build.

## Executed checks

| Check | Result | Evidence |
| --- | --- | --- |
| API, web, collector fresh builds | PASS | Full `--pull --no-cache` command metadata |
| Lambda fresh build and local handler import/workflow | PASS | Network disabled, read-only root, UID 10001, nine stages, zero model tokens |
| All three Compose health checks | PASS | Docker health state before and after restart |
| Web to API through container DNS | PASS | Request from web container to `http://api:8000/health` |
| Normal policy request through web proxy | PASS | Six verified citations, nine governed stages |
| Deterministic DTI | PASS | 1200 / 4000 = 30.00%, controlled calculation tool, review required |
| Prohibited credit approval | PASS | `prohibited_action`, required human review |
| Suspicious activity review | PASS | Three verified citations, required human review |
| Retrieved prompt injection | PASS | Source excluded, zero evidence/confidence, injection flag, review required |
| Synthetic PII canary | PASS | Redaction flag; email and SSN absent from runtime logs |
| SME financial review | PASS | Local Gold values, governed tool, three policy citations, quantitative provenance, review required |
| Content-free OTel transport | PASS | Every governed stage and scenario request ID reached the collector; no questions/source excerpts/PII canaries |
| Restart reproducibility | PASS | Identical answer hash; audit records persisted and grew from 95 to 111 |
| Runtime logs | PASS | Zero detected exceptions/errors and zero warnings |
| Python dependencies inside API | PASS | `pip check` |
| Cleanup | PASS | Only the verifier's stack and synthetic audit volume removed; no project containers remained |

The injection fixture is fixed developer-owned Python sent to the API container
over standard input. It does not create an API route or give the runtime agent
shell access. The collector has a fixed-purpose static HTTP health probe, not a
general command runner.

The SME profile returned revenue trend `20.00`, cash-flow volatility `44596.96`,
debt-service ratio `0.0860`, and liquidity indicator `1.9433`. The adapter reported
`local`. All four values were checked against the synthetic Gold fixture. A
separate log scan checked the company-ID canary too. This is not an assertion
that any Databricks workspace ran.

## Image and privilege evidence

Sizes are Docker's reported uncompressed image bytes, not registry transfer sizes.

| Image | Bytes | Runtime privilege check |
| --- | ---: | --- |
| API | 240,676,967 | `lab`, all capabilities dropped, no new privileges, read-only root |
| Web | 244,157,518 | `nextjs`, all capabilities dropped, no new privileges |
| Collector | 366,967,838 | `10001:10001`, all capabilities dropped, no new privileges, read-only root |
| Lambda | 810,790,963 | Local probe explicitly used UID 10001, no network, read-only root, all capabilities dropped |

The web filesystem remains writable for Next.js runtime caching. The Lambda
probe overrides its entrypoint to import the actual handler and run the bounded
workflow; it is not a Lambda Runtime Interface Emulator or real AWS invocation.
AWS supplies its own least-privileged execution user for a deployed Lambda image.
Moving base tags remain a release gap: production promotion should pin reviewed
digests and scan/sign the final images. An OS-package vulnerability image scan
was **NOT TESTED**; runtime privilege checks and Python/npm dependency audits
must not be described as that scan.

## Failures found and fixed

1. A true Linux build exposed missing `cryptography`, `cffi`, and `pycparser`
   transitives from `PyJWT[crypto]`. The lock generator now propagates dependency
   extras through the dependency graph. Both locks were regenerated and image
   installation plus `pip check` passed.
2. The first web calculation request lost its structured calculation because
   the frontend response schema stripped the field. The schema now retains and
   validates it, with a regression test. The actual first failure is preserved
   in [initial-failure evidence](../validation/containers-2026-09-09-initial-failure.json).
3. Docker 20 reassigned a port requested as `0` after restart. The verifier used
   the old port and failed to connect even though services were healthy. It now
   rediscovers and validates the loopback binding after restart. The prior result
   is preserved in [restart-probe failure evidence](../validation/containers-2026-09-09-restart-probe-failure.json).

The current verifier, dependency-lock, and developer-CLI tests passed **25 tests**.
The repository's complete baseline and final expanded suite results are recorded
centrally in [REPORT.md](../../REPORT.md). The CDK npm audit returned zero
vulnerabilities. Root-level security checks additionally run Python dependency
audit, web dependency audit, static analysis, and secret scanning.

Raw local logs remain under ignored `.runtime/container-runs/`; committed evidence
contains counts, timings, image IDs, source/answer hashes, and synthetic request
IDs. No external credentials, financial/customer payloads, or account identifiers
were added to these artifacts.
