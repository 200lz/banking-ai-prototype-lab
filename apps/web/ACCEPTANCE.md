# Web acceptance criteria

Written before implementation.

- The landing page visibly identifies a fictional, synthetic portfolio lab with no bank affiliation.
- A real request form posts to a same-origin Next.js route, which forwards only a validated typed request to the configured backend. Credentials and backend configuration stay on the server.
- Four realistic sample scenarios and a typed deterministic calculation workflow are available. No action can approve credit, transact, alter records, or bypass review.
- Successful responses show every required response field, exact evidence excerpts, verified citation state, source version/hash, human review decision, all nine stage traces, tool records, latency, token usage, and estimated model cost.
- Empty, loading, invalid-input, unavailable-backend, and unsuccessful-response states are accessible. Changing the input does not silently submit a request.
- Public citation URLs accept HTTP(S) only. Backend errors and credentials are never reflected to the browser. The proxy uses a bounded timeout, body limit, no redirects, and no response caching.
- Local deterministic mode is labelled as such; the page makes no fabricated evaluation or LLM performance claim.
- Layout works on mobile and desktop with keyboard-visible focus and readable contrast.
- Formatting, linting, strict TypeScript, unit tests, and a production build pass. Proxy tests exercise malformed inputs, unsafe destinations, origin checks, and credential handling.

Cloud login uses Cognito authorization code plus PKCE with server-side exchange
and Secure, HttpOnly cookies. The proxy forwards the current user's access token
to API Gateway; no shared bearer token is accepted from frontend configuration.
This flow must be verified against a real configured deployment before claiming
cloud validation. Local development remains explicitly unauthenticated.

## Continuation: governed SME lending review

Acceptance criteria added before implementation on 2026-09-09.

- Preserve the existing design, four scenarios, deterministic calculations, proxy
  boundaries, and all 18 existing tests.
- Add an optional, strictly validated synthetic company identifier and an SME
  review scenario. Only `SYN-SME-NNN` identifiers are accepted; no SQL, raw rows,
  customer record editing, or lending approval controls exist.
- Show the governed Gold profile separately from policy excerpts, including
  Decimal values and metric definitions, JPY units, adapter source, period count,
  as-of time, provenance hash/version, and missing/stale indicators.
- Missing values remain visibly unavailable, never zero. All SME profile reviews
  show the mandatory human-review boundary. Local profiles never claim verified
  Databricks execution; actual source is supplied by the API.
- Add regression tests for the company schema, request forwarding, profile
  parsing, missing values, provenance, and untrusted extra financial fields.
- Run formatting, lint, TypeScript, tests, production build, and npm audit; perform
  real browser/API verification and capture an actual UI screenshot if the
  documented browser runtime supports exporting it.
