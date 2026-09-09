# AWS infrastructure acceptance criteria

Recorded before implementation. This portfolio uses synthetic banking records;
it does not claim affiliation, certification, or an actual cloud deployment.

- CDK synthesizes offline without an AWS lookup, Docker daemon, credentials, or
  a live model call. Deployment separately requires Docker, CDK bootstrap,
  explicit account/region configuration, and authorized AWS credentials.
- Corpus storage blocks public access, enforces TLS, encrypts objects, versions
  them, and grants the agent read access only under `corpus/`.
- DynamoDB encrypts retained audit/review items, has point-in-time recovery and
  expiry, and gives the runtime only append permissions (no update/delete).
- HTTP API protects **every** application route with a Cognito JWT authorizer
  and a custom access-token scope; self sign-up is disabled. No function URL or
  unauthenticated customer-write route exists.
- The bounded Lambda container exposes the FastAPI Mangum handler, uses the
  repository's pinned Python requirements, and can invoke only a selected
  Bedrock foundation-model ARN. No cross-region inference profile wildcard.
- CloudWatch has retained/redacted application and access logs, throttles,
  concurrency limits, latency/error alarms, and a usage dashboard. An optional
  billing alert is explicit about account-wide scope and delivery configuration.
- Next.js has an Amplify SSR app/branch and a reproducible monorepo build spec;
  Git connection and Cognito callback configuration are documented. The browser
  authenticates each person and forwards their access token, never an application
  wide service token.
- Application OpenTelemetry span export limitations are explicit: structured
  spans can reach CloudWatch logs; Lambda X-Ray tracing is infrastructure tracing
  only until an authenticated OTLP collector is configured and verified.
- Assertion tests verify encryption, retention, IAM boundaries, route auth,
  resource limits, frontend environment wiring, and reject invalid model or
  callback configuration. Synth and tests do not deploy billable resources.
