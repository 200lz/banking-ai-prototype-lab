# Milestone 2: publication and hosted CI

Status at 2026-09-09: **NOT TESTED** for GitHub-hosted execution.

The workflow installs locked dependencies, runs formatting, lint, types, Python
unit/API/infrastructure tests, frontend tests/build, evaluation smoke/full gates,
dependency audits, offline CDK synth, a checksum-pinned Gitleaks source scan, and
fresh container acceptance. Ordinary PR CI does not require cloud credentials.
The container verifier owns isolated startup, health, scenarios, trace inspection,
restart, diagnostics and cleanup. Its sanitized JSON is preserved as an artifact.

The official portable GitHub CLI 2.100.0 was installed in ignored `.runtime/tools/gh`
and its release checksum verified. `gh auth status` reported no authenticated
hosts. A connected GitHub account does not authenticate this CLI. The repository
has no remote yet; no hosted run, URL or badge is fabricated.

The implementation is committed locally (`ae07e2c`); the repository initially had
no history. Gitleaks source and history scans detected no leaks. An explicit
`.gitattributes` LF policy and LF-generating lock/fixture writers prevent Windows
checkout conversion from changing byte-hashed source inputs. Affected financial
and dependency regressions passed after this portability correction.

Minimum external action in PowerShell at the repository root:

```powershell
.\.runtime\tools\gh\bin\gh.exe auth login --hostname github.com --git-protocol https --web
```

After browser sign-in, verify the active GitHub identity, create the authorized
public `banking-ai-prototype-lab` repository, push the default branch, inspect the
actual Actions run, and fix any hosted failures. Never paste a token into a chat
or file. Run `scripts/check_secrets.py` before publication and scan Git history
after commits; a clean automated scan cannot guarantee absence of all secrets.
