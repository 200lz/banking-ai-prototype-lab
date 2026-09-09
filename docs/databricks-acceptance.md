# Milestone 5 acceptance criteria (before implementation)

Preserve the existing governed workflow and all 61 deterministic evaluation cases.
All SME entities and monthly records are synthetic; no execution or lending
approval capability is added.

1. Versioned synthetic monthly input includes company ID, revenue, operating cash
   inflow/outflow, scheduled debt service, closing balance, industry, transaction
   count, source record ID, and observation time.
2. A reproducible RAW → BRONZE → SILVER → GOLD pipeline preserves source hashes,
   validates types, deduplicates deterministically, rejects invalid rows, and
   explicitly carries missing fields. Gold uses Decimal arithmetic with documented
   revenue trend, cash-flow volatility, debt-service share and liquidity formulas.
3. A local adapter and a real Databricks Statement Execution adapter share a strict
   profile contract. The cloud adapter uses a fixed parameterized SELECT, named
   company-ID parameter, bounded wait/rows/bytes, governed Gold output only, and
   environment/unified authentication without committed credentials.
4. A sixth read-only financial_profile_tool accepts only a synthetic company ID;
   callers and the model cannot submit SQL, raw data, formulas, or tool arguments.
5. Company review responses retain policy citations and expose quantitative
   evidence, missing/stale flags and provenance separately. All company reviews
   require a human. Raw rows and quantitative profile values never enter prompts.
6. Regression tests cover formulas, nulls, bad IDs/types, duplicates, stale data,
   schema tampering, unsafe approval, adapter outage, model-input minimization,
   and the fixed parameterized SQL boundary. Existing tests/evals remain green.
7. A Databricks-native bundle and versioned Python pipeline make real deployment
   reproducible. Documentation distinguishes local/mocked verification from actual
   workspace execution; VERIFIED requires real tables, query and end-to-end use.
