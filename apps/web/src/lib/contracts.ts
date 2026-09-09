import { z } from "zod";

const operand = z.union([
  z.number().finite(),
  z.string().regex(/^-?\d+(\.\d+)?$/),
]);

export const querySchema = z.strictObject({
  question: z.string().trim().min(1).max(4000),
  company_id: z
    .string()
    .length(11)
    .regex(
      /^SYN-SME-[0-9]{3}$/,
      "Use a synthetic company ID such as SYN-SME-001.",
    )
    .optional(),
  calculation: z
    .strictObject({
      operation: z.enum(["debt_to_income", "simple_interest", "sum"]),
      operands: z.array(operand).min(1).max(20),
    })
    .superRefine((value, ctx) => {
      const expected = { debt_to_income: 2, simple_interest: 3, sum: 0 }[
        value.operation
      ];
      if (expected && value.operands.length !== expected) {
        ctx.addIssue({
          code: "custom",
          message: `This calculation requires ${expected} operands.`,
        });
      }
      if (
        value.operands.some(
          (n) => !Number.isFinite(Number(n)) || Math.abs(Number(n)) > 1e12,
        )
      ) {
        ctx.addIssue({
          code: "custom",
          message: "Operands must be finite and at most one trillion.",
        });
      }
      if (
        value.operation === "debt_to_income" &&
        Number(value.operands[1]) <= 0
      ) {
        ctx.addIssue({
          code: "custom",
          message: "Monthly income must be greater than zero.",
        });
      }
    })
    .optional(),
});

const nonnegative = z.number().finite().min(0);
export const calculationResultSchema = z.strictObject({
  operation: z.enum(["debt_to_income", "simple_interest", "sum"]),
  operands: z.array(z.string()).min(1).max(20),
  value: z.string(),
  unit: z.string(),
  formula: z.string(),
  rounding: z.string(),
});
const financialValue = z
  .string()
  .max(36)
  .regex(/^-?[0-9]{1,30}\.[0-9]{2,4}$/)
  .refine((value) => value.trim() === value)
  .nullable();
export const financialProfileSchema = z.strictObject({
  company_id: z
    .string()
    .length(11)
    .regex(/^SYN-SME-[0-9]{3}$/),
  source: z.enum(["local", "databricks"]),
  revenue_trend: financialValue,
  cashflow_volatility: financialValue,
  debt_service_ratio: financialValue,
  liquidity_indicator: financialValue,
  missing_fields: z.array(z.string()),
  data_as_of: z.iso.datetime({ offset: true }),
  stale: z.boolean(),
  period_count: z.number().int().min(1).max(120),
  currency: z.literal("JPY"),
  provenance: z.strictObject({
    dataset_sha256: z
      .string()
      .length(64)
      .regex(/^[a-f0-9]{64}$/),
    gold_record_sha256: z
      .string()
      .length(64)
      .regex(/^[a-f0-9]{64}$/),
    source_record_ids: z
      .array(
        z
          .string()
          .max(56)
          .regex(/^SYN-FIN-[A-Z0-9-]{1,48}$/)
          .refine((value) => value.trim() === value),
      )
      .min(1)
      .max(120),
    formula_version: z.literal("sme-gold-v1"),
    layer: z.literal("gold"),
    source_table: z.literal("financial_gold"),
    metric_definitions: z.strictObject({
      revenue_trend: z.string(),
      cashflow_volatility: z.string(),
      debt_service_ratio: z.string(),
      liquidity_indicator: z.string(),
    }),
  }),
});
export const responseSchema = z
  .object({
    request_id: z.string(),
    answer: z.string(),
    evidence: z.array(
      z.object({
        id: z.string(),
        document_id: z.string(),
        claim: z.string(),
        quote: z.string(),
        source_hash: z.string(),
      }),
    ),
    citations: z.array(
      z.object({
        evidence_id: z.string(),
        document_id: z.string(),
        title: z.string(),
        source_url: z.string().nullable(),
        version: z.string(),
        verified: z.boolean(),
      }),
    ),
    assumptions: z.array(z.string()),
    missing_information: z.array(z.string()),
    confidence: z.number().min(0).max(1),
    risk_flags: z.array(z.string()),
    human_review_required: z.boolean(),
    mode: z.enum(["local", "bedrock"]),
    calculation: calculationResultSchema.nullish(),
    financial_profile: financialProfileSchema.nullish(),
    retrieved_document_ids: z.array(z.string()).optional(),
    disclaimer: z.string().optional(),
    trace: z.array(
      z.object({
        stage: z.string(),
        duration_ms: nonnegative,
        status: z.string(),
      }),
    ),
    tool_invocations: z.array(
      z.object({
        name: z.string(),
        duration_ms: nonnegative,
        status: z.string(),
      }),
    ),
    metrics: z.object({
      latency_ms: nonnegative,
      model_latency_ms: nonnegative,
      retrieval_latency_ms: nonnegative,
      input_tokens: nonnegative,
      output_tokens: nonnegative,
      estimated_cost_usd: nonnegative,
      cost_estimate_complete: z.boolean().default(false),
    }),
  })
  .superRefine((value, ctx) => {
    if (value.financial_profile && !value.human_review_required) {
      ctx.addIssue({
        code: "custom",
        message: "Financial profiles require human review.",
      });
    }
  });

export type QueryRequest = z.infer<typeof querySchema>;
export type AgentResponse = z.infer<typeof responseSchema>;
export type FinancialProfile = z.infer<typeof financialProfileSchema>;

export function safeSourceUrl(value: string | null): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) &&
      !url.username &&
      !url.password
      ? url.href
      : null;
  } catch {
    return null;
  }
}

export const stages = [
  "user_request",
  "intent_analysis",
  "retrieval",
  "agent_planning",
  "controlled_tool_execution",
  "guardrail_validation",
  "citation_verification",
  "human_approval_decision",
  "final_response",
] as const;

export function humanize(value: string) {
  return value.replaceAll("_", " ");
}
