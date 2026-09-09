import assert from "node:assert/strict";
import { test } from "node:test";
import {
  proxyQuery,
  apiDestination,
  readBoundedBody,
  sameOrigin,
} from "../src/lib/proxy";
import {
  querySchema,
  responseSchema,
  safeSourceUrl,
} from "../src/lib/contracts";

const fixture = {
  request_id: "test-run",
  answer: "Refer this synthetic case for review.",
  evidence: [],
  citations: [],
  assumptions: [],
  missing_information: ["Identity document"],
  confidence: 0.7,
  risk_flags: ["missing_information"],
  human_review_required: true,
  mode: "local",
  trace: [{ stage: "user_request", duration_ms: 1, status: "ok" }],
  tool_invocations: [],
  metrics: {
    latency_ms: 3,
    model_latency_ms: 0,
    retrieval_latency_ms: 1,
    input_tokens: 0,
    output_tokens: 0,
    estimated_cost_usd: 0,
    cost_estimate_complete: true,
  },
};
function request(
  body: unknown = { question: "What are the onboarding checks?" },
  headers: Record<string, string> = {},
) {
  return new Request("http://localhost:3000/api/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: "http://localhost:3000",
      ...headers,
    },
    body: JSON.stringify(body),
  });
}
const options = { apiBase: "http://127.0.0.1:8000", cloud: false };

test("missing cost completeness is treated as unknown rather than free model usage", () => {
  const incomplete = {
    ...fixture,
    metrics: { ...fixture.metrics, cost_estimate_complete: undefined },
  };
  assert.equal(
    responseSchema.parse(incomplete).metrics.cost_estimate_complete,
    false,
  );
});

test("typed request rejects tool injection, unknown fields and empty questions", () => {
  assert.equal(
    querySchema.safeParse({ question: "test", tool: "shell" }).success,
    false,
  );
  assert.equal(querySchema.safeParse({ question: "   " }).success, false);
  assert.equal(
    querySchema.safeParse({ question: "x".repeat(4001) }).success,
    false,
  );
  assert.equal(
    querySchema.safeParse({
      question: "test",
      calculation: { operation: "shell", operands: [1] },
    }).success,
    false,
  );
});

test("calculation validation preserves decimal strings and enforces arity and income", () => {
  assert.equal(
    querySchema.parse({
      question: "calculate",
      calculation: { operation: "sum", operands: ["0.10", "0.20"] },
    }).calculation?.operands[0],
    "0.10",
  );
  for (const calculation of [
    { operation: "debt_to_income", operands: [1] },
    { operation: "debt_to_income", operands: [1, 0] },
    { operation: "sum", operands: ["Infinity"] },
    { operation: "sum", operands: ["1e100"] },
    { operation: "sum", operands: Array(21).fill(1) },
  ]) {
    assert.equal(
      querySchema.safeParse({ question: "calculate", calculation }).success,
      false,
    );
  }
});

test("citation URLs reject script, data, credentials and malformed schemes", () => {
  for (const value of [
    "javascript:alert(1)",
    "data:text/html,<script>",
    "https://user:pass@example.com",
    "//evil.example",
    "not a url",
    null,
  ])
    assert.equal(safeSourceUrl(value), null);
  assert.equal(
    safeSourceUrl("https://www.fdic.gov/resources/"),
    "https://www.fdic.gov/resources/",
  );
});

test("API destination is fixed by trusted server configuration and enforces trust boundary", () => {
  assert.equal(
    apiDestination("http://api:8000", false).href,
    "http://api:8000/v1/query",
  );
  assert.equal(
    apiDestination("https://api.example.com/demo", true).href,
    "https://api.example.com/demo/v1/query",
  );
  for (const base of [
    "file:///tmp/a",
    "http://169.254.169.254",
    "https://example.com",
    "http://user:pass@localhost",
    "http://localhost?target=elsewhere",
  ])
    assert.throws(() => apiDestination(base, false));
  assert.throws(() => apiDestination("http://example.com", true));
});

test("proxy requires same origin and ignores untrusted forwarded host", async () => {
  assert.equal(
    sameOrigin(new Request("http://localhost:3000/api/query")),
    false,
  );
  assert.equal(
    sameOrigin(
      request(
        {},
        { Origin: "https://evil.example", "X-Forwarded-Host": "evil.example" },
      ),
    ),
    false,
  );
  const result = await proxyQuery(
    request({}, { Origin: "https://evil.example" }),
    options,
  );
  assert.equal(result.status, 403);
});

test("local origin check handles Next canonical host while rejecting DNS rebinding and mismatched hosts", () => {
  assert.equal(
    sameOrigin(
      request({}, { Origin: "http://127.0.0.1:3000", Host: "127.0.0.1:3000" }),
    ),
    true,
  );
  assert.equal(
    sameOrigin(
      request({}, { Origin: "http://localhost:3000", Host: "127.0.0.1:3000" }),
    ),
    false,
  );
  assert.equal(
    sameOrigin(
      request(
        {},
        {
          Origin: "http://attacker.example:3000",
          Host: "attacker.example:3000",
        },
      ),
    ),
    false,
  );
  assert.equal(
    sameOrigin(
      request(
        {},
        { Origin: "https://lab.example.com", Host: "internal-proxy" },
      ),
      "https://lab.example.com",
    ),
    true,
  );
});

test("proxy rejects bad schema without contacting the backend", async () => {
  const result = await proxyQuery(
    request({ question: "x", execute: "transfer" }),
    {
      ...options,
      fetcher: async () => {
        throw new Error("Must not fetch");
      },
    },
  );
  assert.equal(result.status, 400);
});

test("proxy restricts JSON content and bounded request bodies", async () => {
  assert.equal(
    (await proxyQuery(request({}, { "Content-Type": "text/plain" }), options))
      .status,
    415,
  );
  assert.equal(
    (await proxyQuery(request({ question: "x".repeat(25000) }), options))
      .status,
    400,
  );
  await assert.rejects(
    () => readBoundedBody(new Response("abcdef").body, 5),
    /too large/,
  );
});

test("proxy forwards a validated request but strips client cookie and authorization", async () => {
  let called = false;
  const result = await proxyQuery(
    request(undefined, {
      Cookie: "sensitive=secret",
      Authorization: "Bearer client-secret",
    }),
    {
      ...options,
      token: "unused-token",
      fetcher: async (url, init) => {
        called = true;
        assert.equal(String(url), "http://127.0.0.1:8000/v1/query");
        assert.deepEqual(init?.headers, { "Content-Type": "application/json" });
        assert.equal(init?.redirect, "error");
        assert.equal(init?.cache, "no-store");
        assert.ok(init?.signal);
        return Response.json(fixture);
      },
    },
  );
  assert.equal(called, true);
  assert.equal(result.status, 200);
  assert.equal(result.headers.get("cache-control"), "no-store");
  assert.deepEqual(await result.json(), fixture);
});

test("cloud proxy requires user authentication and forwards only server-read access token", async () => {
  const cloud = { apiBase: "https://api.example.com", cloud: true };
  assert.equal((await proxyQuery(request(), cloud)).status, 401);
  const result = await proxyQuery(request(), {
    ...cloud,
    token: "user.access.token",
    fetcher: async (_url, init) => {
      assert.equal(
        (init?.headers as Record<string, string>).Authorization,
        "Bearer user.access.token",
      );
      return Response.json(fixture);
    },
  });
  assert.equal(result.status, 200);
});

test("proxy validates responses and never reflects upstream errors or secrets", async () => {
  const invalid = await proxyQuery(request(), {
    ...options,
    fetcher: async () => Response.json({ answer: "incomplete" }),
  });
  assert.equal(invalid.status, 502);
  const failed = await proxyQuery(request(), {
    ...options,
    fetcher: async () =>
      new Response("AWS_SECRET_ACCESS_KEY=private", { status: 500 }),
  });
  assert.equal(failed.status, 502);
  assert.equal((await failed.text()).includes("private"), false);
});

test("network failures become actionable generic errors", async () => {
  const result = await proxyQuery(request(), {
    ...options,
    fetcher: async () => {
      throw new Error("private network details");
    },
  });
  assert.equal(result.status, 502);
  assert.match((await result.json()).error, /backend is running/);
});

test("upstream throttling is preserved without reflecting the upstream body", async () => {
  const result = await proxyQuery(request(), {
    ...options,
    fetcher: async () => new Response("secret", { status: 429 }),
  });
  assert.equal(result.status, 429);
  assert.match((await result.json()).error, /busy/);
});

test("proxy preserves structured calculation and retrieved document provenance", async () => {
  const calculation = {
    operation: "debt_to_income",
    operands: ["1200", "4000"],
    value: "30.00",
    unit: "percent",
    formula: "periodic debt / income for the same period * 100",
    rounding: "ROUND_HALF_UP to 2 decimal places",
  };
  const result = await proxyQuery(
    request({
      question: "Calculate the DTI ratio",
      calculation: { operation: "debt_to_income", operands: ["1200", "4000"] },
    }),
    {
      ...options,
      fetcher: async (_url, init) => {
        assert.deepEqual(JSON.parse(String(init?.body)).calculation.operands, [
          "1200",
          "4000",
        ]);
        return Response.json({
          ...fixture,
          calculation,
          retrieved_document_ids: ["SYN-CALC-001"],
          disclaimer:
            "Synthetic demonstration only. No affiliation with any real bank.",
        });
      },
    },
  );
  assert.equal(result.status, 200);
  const body = await result.json();
  assert.deepEqual(body.calculation, calculation);
  assert.deepEqual(body.retrieved_document_ids, ["SYN-CALC-001"]);
  assert.match(body.disclaimer, /Synthetic demonstration/);
  assert.equal(
    responseSchema.safeParse({
      ...fixture,
      calculation: { ...calculation, execute: "approve_credit" },
    }).success,
    false,
  );
});
