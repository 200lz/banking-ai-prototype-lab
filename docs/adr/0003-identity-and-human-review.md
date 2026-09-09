# ADR 0003 — Authenticate users; keep review separate from execution

Status: accepted, 2026-09-09.

The API accepts no role, clearance or approval field. Local mode is loopback-only;
the cloud boundary is API Gateway JWT authorization with a Cognito query scope.
Next.js exchanges the code with PKCE server-side and sends the access token from
an HttpOnly cookie to the gateway. The backend checks verified event claims rather
than trusting a role header supplied by a browser. Self sign-up is disabled.

Human review is an output and an audit event. No approval-completion endpoint or
business execution service is included. This deliberately avoids implying that
a generated flag or a click could authorize credit or transactions. A real case
management system needs employee identity, permissions, reasons, conflict-of-duty
checks, retention, and controlled action handoff outside this agent.
