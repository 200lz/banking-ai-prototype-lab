# Banking AI Prototype Lab — web

A Next.js / TypeScript operations workspace for the fictional portfolio lab. It
shows real API responses, exact evidence excerpts, source versions and hashes,
review decisions, observed stage/tool traces, and measured latency/token/cost
fields. No evaluation scores or sample responses are fabricated in the UI.

## Develop and verify

Use Node.js 22.13+ (the Docker image uses Node 22).

```sh
npm ci
cp .env.example .env.local
npm run dev
# API must be running at http://127.0.0.1:8000
npm run format:check
npm run lint
npm run typecheck
npm test
npm run build
```

Open http://localhost:3000. Choose a sample, inspect or edit its question, then
submit. The calculation example supplies typed decimal strings, never evaluated
code. The local mode is an explicit deterministic baseline with zero LLM usage.
All internal data, questions and customer scenarios must remain synthetic.

The SME lending review scenario optionally sends a strict `SYN-SME-NNN` company
identifier to the API. Use `SYN-SME-001` for the complete synthetic profile,
`SYN-SME-002` for missing data, and `SYN-SME-003` for stale data. A separate Gold
evidence card shows exact deterministic indicators, definitions, as-of time,
missing/stale flags, dataset hash, formula version and synthetic record IDs.
No arithmetic is delegated to the browser or LLM. Missing indicators remain
unavailable. Profiles always require authorized human review and cannot approve
credit. The card distinguishes local and Databricks adapters; a local response
does not establish that a Databricks workspace has executed the pipeline.

The Docker build context is `apps/web`. `API_BASE_URL=http://api:8000` connects to
the backend in Compose. This setting stays server-side. The application exposes
`POST /api/query`; it validates strict input, uses a fixed server-configured API
destination, limits request/response bytes, checks the same-origin request,
refuses redirects, times out requests, validates response shape and disables
caching. API errors are mapped to safe messages. Public source links permit only
HTTP(S), and rendered content uses React text nodes rather than HTML/Markdown.

## Cognito deployment

Set these **server** environment variables for the deployed application:

```text
WEB_AUTH_MODE=cognito
API_BASE_URL=https://your-api.execute-api.us-east-1.amazonaws.com
APP_BASE_URL=https://your-lab.example
COGNITO_DOMAIN=https://your-domain.auth.us-east-1.amazoncognito.com
COGNITO_CLIENT_ID=your-public-client-id
```

Configure a Cognito **public** app client with authorization-code grant, PKCE
S256, `openid` and `banking-ai/query` scopes, callback
`APP_BASE_URL/api/auth/callback`, and sign-out URL `APP_BASE_URL`. The API Gateway
must validate the access token issuer, audience, expiry and `banking-ai/query`
scope. The browser starts sign-in at `/api/auth/login`; a server callback checks
state and exchanges the code plus PKCE verifier. Tokens stay in Secure, HttpOnly,
SameSite cookies; `/api/query` forwards the current user's access token. There is
no shared service bearer token and no token in browser local/session storage.
`/api/auth/session` reports presence only; API Gateway is the authority for token
validity. No refresh token is retained; users sign in again after expiration.

Cloud auth is implemented but cannot be claimed verified until a configured
Cognito deployment is exercised. This remains a portfolio prototype: extend
session revocation, nonce-based CSP, stronger CSRF/session lifecycle tests,
centralized rate limiting and accessibility/browser automation before real use.
The CSP permits inline script/style for Next.js hydration and blocks framing;
that is an explicit hardening limitation. TLS must terminate at the cloud edge.

Versions were checked against the npm registry on 2026-09-09: Next.js 15.5.25,
React 19.2.8. Next.js 15 is selected because
[AWS Amplify supports Next.js 12–15](https://docs.aws.amazon.com/amplify/latest/userguide/ssr-amplify-support.html).
The [August Next.js security release](https://nextjs.org/blog/august-2026-security-release)
sets a patched floor of 15.5.24; keep the lockfile and security CI current.
ESLint 10 uses the matching Next 15 rule plugin directly, together with current
TypeScript and React hooks rules. This avoids the ESLint 9-only peer requirement
of the legacy `eslint-config-next` wrapper and keeps the linter maintained.
The lockfile overrides Next 15's pinned PostCSS dependency with compatible
PostCSS 8.5.28 to address current source-map disclosure and CSS serialization
advisories. The production build and npm audit must pass with this override.
