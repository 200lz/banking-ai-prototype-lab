# Contributing

Continuation validation includes `make container-smoke`, `make financial-pipeline`
and `make financial-smoke`. `make aws-smoke` and `make live-eval` require explicit
external configuration and must remain separate from credential-free PR checks.
All Make targets have `python scripts/tasks.py <target>` equivalents (use the
project virtual environment after setup). Native Databricks scripts are included
in formatting, lint, type and static security checks.

Before publication, install Gitleaks 8.30.1 from its checksum-verified official
release and run `python scripts/check_secrets.py --gitleaks <executable>` plus
`gitleaks git --redact=100 --no-banner` after commits. CI repeats both scans.
Never add `.runtime`, credentials, local cloud configuration or workspace tokens.

This public portfolio lab has no bank affiliation. Contributions must use only
synthetic internal policies, invented scenarios, and approved public sources.
Never include real customer records, credentials, confidential bank policies, or
claims of regulatory certification.

1. Read `docs/acceptance-criteria.md`, `ARCHITECTURE.md`, and `SECURITY.md`.
2. Before a substantial feature, write observable acceptance criteria and note
   affected trust boundaries. Keep changes small enough to review.
3. Install Python 3.11, Node 22, and optionally Docker with Compose. `make setup`
   installs the tested Python and npm dependency locks. On Windows use
   `python scripts/tasks.py setup` and `.venv/Scripts/python scripts/tasks.py test`.
4. Run `make lint`, `make typecheck`, `make test`, `make eval`, `make security`,
   `npm --prefix apps/web run build`, and `make synth` before submitting a PR.
5. Add independent evaluation expectations for new workflow behavior. Do not
   weaken a gate to hide a failure. Document intentional policy/oracle changes.
6. Record significant design decisions and failures in `docs/development-log.md`;
   add an ADR for a new model, retrieval store, authorization path, or write tool.

For dependency updates, update constraints, install in a clean virtual environment,
run `python scripts/lock_dependencies.py`, regenerate npm locks, and repeat all
checks plus dependency audits. The Python lock pins versions but is not a signed
or hash-locked supply-chain artifact; release hardening must add verified hashes,
SBOMs, image digests, and provenance attestations.

The runtime must never import the developer deployment/CLI modules. No new tool
may execute shell commands, mutate customer records, perform financial actions,
or grant approval. An approval flag is a review routing outcome, not a permission
token. Security reports should include a synthetic reproduction with secrets
removed; do not test against a financial institution's systems.
