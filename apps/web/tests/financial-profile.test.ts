import assert from "node:assert/strict";
import { test } from "node:test";
import {
  financialProfileSchema,
  querySchema,
  responseSchema,
} from "../src/lib/contracts";
import { proxyQuery } from "../src/lib/proxy";

const profile = {
  company_id: "SYN-SME-001",
  source: "local",
  revenue_trend: "25.0000",
  cashflow_volatility: "15275.2523",
  debt_service_ratio: "0.1250",
  liquidity_indicator: "3.2000",
  missing_fields: [],
  data_as_of: "2026-09-01T00:00:00Z",
  stale: false,
  period_count: 6,
  currency: "JPY",
  provenance: {
    dataset_sha256: "a".repeat(64),
    gold_record_sha256: "b".repeat(64),
    source_record_ids: ["SYN-FIN-001-2026-08"],
    formula_version: "sme-gold-v1",
    layer: "gold",
    source_table: "financial_gold",
    metric_definitions: {
      revenue_trend: "(last revenue / first revenue - 1) * 100 percent",
      cashflow_volatility:
        "Population standard deviation of monthly operating inflow minus outflow (JPY)",
      debt_service_ratio: "Sum scheduled debt service / sum cash inflow",
      liquidity_indicator:
        "Latest closing balance / mean monthly operating outflow (months)",
    },
  },
};
const result = {
  request_id: "synthetic-test",
  answer: "Authorized human lending review is required.",
  evidence: [],
  citations: [],
  assumptions: [],
  missing_information: [],
  confidence: 0.7,
  risk_flags: ["lending_review"],
  human_review_required: true,
  mode: "local",
  financial_profile: profile,
  trace: [],
  tool_invocations: [
    { name: "financial_profile_tool", duration_ms: 1, status: "ok" },
  ],
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

test("company ID admits only the strict synthetic namespace", () => {
  assert.equal(
    querySchema.parse({
      question: "Review this SME",
      company_id: "SYN-SME-001",
    }).company_id,
    "SYN-SME-001",
  );
  for (const company_id of [
    "REAL-CUSTOMER-1",
    "SYN-SME-001; DROP TABLE gold",
    "SYN-SME-01",
    "syn-sme-001",
    "../SYN-SME-001",
    "SYN-SME-001\n",
    "",
  ]) {
    assert.equal(
      querySchema.safeParse({ question: "Review this SME", company_id })
        .success,
      false,
    );
  }
});

test("profile parser preserves exact decimal strings, source and provenance", () => {
  const parsed = financialProfileSchema.parse(profile);
  assert.equal(parsed.revenue_trend, "25.0000");
  assert.equal(parsed.debt_service_ratio, "0.1250");
  assert.equal(parsed.provenance.dataset_sha256, "a".repeat(64));
  assert.deepEqual(
    parsed.provenance.source_record_ids,
    profile.provenance.source_record_ids,
  );
  assert.equal(
    financialProfileSchema.parse({ ...profile, source: "databricks" }).source,
    "databricks",
  );
});

test("missing and stale profiles remain explicit and never coerce null into zero", () => {
  const parsed = financialProfileSchema.parse({
    ...profile,
    revenue_trend: null,
    cashflow_volatility: null,
    missing_fields: ["monthly_revenue"],
    stale: true,
  });
  assert.equal(parsed.revenue_trend, null);
  assert.equal(parsed.cashflow_volatility, null);
  assert.equal(parsed.stale, true);
  assert.deepEqual(parsed.missing_fields, ["monthly_revenue"]);
});

test("profile schema rejects raw records, SQL and invalid quantitative values", () => {
  for (const financial_profile of [
    { ...profile, raw_records: [{ account_number: "synthetic" }] },
    { ...profile, sql: "SELECT * FROM bronze" },
    { ...profile, revenue_trend: "Infinity" },
    { ...profile, debt_service_ratio: 0.125 },
    { ...profile, data_as_of: "unknown" },
    { ...profile, provenance: { ...profile.provenance, layer: "bronze" } },
    {
      ...profile,
      provenance: { ...profile.provenance, dataset_sha256: "invalid" },
    },
  ])
    assert.equal(
      financialProfileSchema.safeParse(financial_profile).success,
      false,
    );
});

test("a returned financial profile cannot remove the human review requirement", () => {
  assert.equal(responseSchema.safeParse(result).success, true);
  assert.equal(
    responseSchema.safeParse({ ...result, human_review_required: false })
      .success,
    false,
  );
  assert.equal(
    responseSchema.parse({ ...result, financial_profile: null })
      .financial_profile,
    null,
  );
});

test("proxy forwards only the typed company ID and validated governed Gold output", async () => {
  const request = new Request("http://localhost:3000/api/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: "http://localhost:3000",
    },
    body: JSON.stringify({
      question: "Review synthetic SME lending evidence",
      company_id: "SYN-SME-001",
    }),
  });
  const response = await proxyQuery(request, {
    apiBase: "http://api:8000",
    cloud: false,
    fetcher: async (_url, init) => {
      assert.deepEqual(JSON.parse(String(init?.body)), {
        question: "Review synthetic SME lending evidence",
        company_id: "SYN-SME-001",
      });
      return Response.json(result);
    },
  });
  assert.equal(response.status, 200);
  const json = await response.json();
  assert.equal(json.financial_profile.provenance.layer, "gold");
  assert.equal(json.human_review_required, true);
  assert.equal(json.financial_profile.revenue_trend, "25.0000");
});

test("a company lookup outage cannot silently remove required human review", async () => {
  const request = new Request("http://localhost:3000/api/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: "http://localhost:3000",
    },
    body: JSON.stringify({
      question: "Review synthetic SME evidence",
      company_id: "SYN-SME-001",
    }),
  });
  const response = await proxyQuery(request, {
    apiBase: "http://api:8000",
    cloud: false,
    fetcher: async () =>
      Response.json({
        ...result,
        financial_profile: null,
        human_review_required: false,
      }),
  });
  assert.equal(response.status, 502);
});
