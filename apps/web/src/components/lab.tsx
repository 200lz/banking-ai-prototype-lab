"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { FinancialProfileCard } from "@/components/financial-profile";
import {
  type AgentResponse,
  type QueryRequest,
  humanize,
  querySchema,
  responseSchema,
  safeSourceUrl,
  stages,
} from "@/lib/contracts";

type Operation = NonNullable<QueryRequest["calculation"]>["operation"];
const examples = [
  {
    name: "Customer onboarding",
    category: "Internal policy",
    question:
      "A synthetic business customer is missing beneficial ownership documents. What should the employee do before onboarding?",
    icon: "01",
  },
  {
    name: "Suspicious activity",
    category: "Escalation workflow",
    question:
      "A synthetic account has a suspicious activity alert. What is the triage and escalation procedure?",
    icon: "02",
  },
  {
    name: "Deposit insurance",
    category: "Public reference",
    question:
      "What is the standard FDIC deposit insurance coverage, and which ownership categories and details must an employee verify?",
    icon: "03",
  },
  {
    name: "Debt-to-income ratio",
    category: "Deterministic calculation",
    question:
      "Calculate the debt-to-income ratio for this synthetic case and explain the credit approval boundary.",
    icon: "04",
    calculation: true,
  },
  {
    name: "SME lending review",
    category: "Governed financial evidence",
    question:
      "Review the governed financial profile for this synthetic SME and explain the evidence and human review needed for a lending assessment.",
    icon: "05",
    companyId: "SYN-SME-001",
  },
];
const stageLabels: Record<string, string> = {
  user_request: "Receive request",
  request: "Receive request",
  intent_analysis: "Understand intent",
  retrieval: "Retrieve evidence",
  agent_planning: "Plan bounded actions",
  controlled_tool_execution: "Run approved tools",
  guardrail_validation: "Validate guardrails",
  policy_guardrail_validation: "Validate guardrails",
  citation_verification: "Verify citations",
  human_approval_decision: "Decide human review",
  final_response: "Return grounded answer",
};
const operationFields: Record<
  Operation,
  { labels: string[]; defaults: string[]; helper: string }
> = {
  debt_to_income: {
    labels: ["Monthly debt", "Monthly income"],
    defaults: ["1500", "5000"],
    helper:
      "Same currency and period. This ratio does not establish credit eligibility.",
  },
  simple_interest: {
    labels: ["Principal", "Annual rate (%)", "Days"],
    defaults: ["10000", "4.5", "90"],
    helper:
      "Simple interest using actual/365. An illustrative calculation, not a product quote.",
  },
  sum: {
    labels: ["Values, separated by commas"],
    defaults: ["125.50, 240, 89.25"],
    helper:
      "Add up to 20 synthetic values. Use the same currency or unit for every value.",
  },
};

function Arrow({ diagonal = false }: { diagonal?: boolean }) {
  return <span aria-hidden="true">{diagonal ? "↗" : "→"}</span>;
}

function DetailList({
  title,
  items,
  empty,
}: {
  title: string;
  items: string[];
  empty: string;
}) {
  return (
    <div className="detail-list">
      <h3>{title}</h3>
      {items.length ? (
        <ul>
          {items.map((item, index) => (
            <li key={`${index}-${item}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">{empty}</p>
      )}
    </div>
  );
}

function Evidence({ response }: { response: AgentResponse }) {
  return (
    <section
      id="evidence"
      className="evidence-section"
      aria-labelledby="evidence-title"
    >
      <div className="section-heading">
        <h2 id="evidence-title">Evidence ledger</h2>
        <span className="count">
          {response.evidence.length.toString().padStart(2, "0")} excerpts
        </span>
      </div>
      <p className="section-note">
        Inspect the excerpt behind each claim. Verification checks source
        integrity and support; it does not establish legal authority.
      </p>
      {response.evidence.length === 0 && (
        <div className="empty-evidence">
          No supporting evidence was returned. Treat this response as an
          abstention, not authority to proceed.
        </div>
      )}
      {response.evidence.map((item, index) => {
        const citations = response.citations.filter(
          (c) => c.evidence_id === item.id,
        );
        return (
          <article
            className="evidence-card"
            key={item.id}
            id={`evidence-${index + 1}`}
          >
            <div className="evidence-header">
              <span className="evidence-number">
                {(index + 1).toString().padStart(2, "0")}
              </span>
              <div>
                <h3>{citations[0]?.title || item.document_id}</h3>
                <p>
                  {item.document_id} · {item.id}
                </p>
              </div>
              <span
                className={`pill ${citations.length && citations.every((c) => c.verified) ? "good" : "warning"}`}
              >
                {citations.length && citations.every((c) => c.verified)
                  ? "Verified"
                  : "Unverified"}
              </span>
            </div>
            {item.claim !== item.quote && <p className="claim">{item.claim}</p>}
            <blockquote>{item.quote}</blockquote>
            <div className="evidence-footer">
              {citations.map((citation, i) => {
                const source = safeSourceUrl(citation.source_url);
                return (
                  <span key={`${citation.evidence_id}-${i}`}>
                    Version {citation.version} ·{" "}
                    {source ? (
                      <a
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Public source <Arrow diagonal />
                      </a>
                    ) : (
                      "Synthetic internal policy"
                    )}
                  </span>
                );
              })}
              <details>
                <summary>Source fingerprint</summary>
                <code>{item.source_hash}</code>
              </details>
            </div>
          </article>
        );
      })}
      {response.citations
        .filter((c) => !response.evidence.some((e) => e.id === c.evidence_id))
        .map((citation, i) => (
          <p className="warning-text" key={i}>
            Citation {citation.document_id} has no matching evidence excerpt.
            Human verification is required.
          </p>
        ))}
    </section>
  );
}

function Trace({ response }: { response: AgentResponse | null }) {
  const trace =
    response?.trace ??
    stages.map((stage) => ({ stage, duration_ms: 0, status: "waiting" }));
  return (
    <section id="trace" className="trace-section" aria-labelledby="trace-title">
      <div className="section-heading">
        <h2 id="trace-title">Execution trace</h2>
        <span className="count">
          {response ? "Observed run" : "9 controlled stages"}
        </span>
      </div>
      <ol className="trace-grid">
        {trace.map((step, index) => (
          <li
            key={`${step.stage}-${index}`}
            className={response ? "complete" : ""}
          >
            <span className="stage-number">
              {(index + 1).toString().padStart(2, "0")}
            </span>
            <div>
              <span className="stage-label">
                {stageLabels[step.stage] || humanize(step.stage)}
              </span>
              <span className="stage-status">
                {response
                  ? `${humanize(step.status)} · ${step.duration_ms.toFixed(2)} ms`
                  : "Awaiting request"}
              </span>
            </div>
          </li>
        ))}
      </ol>
      {response && (
        <div className="tool-log">
          <h3>
            Tool invocations <span>{response.tool_invocations.length}</span>
          </h3>
          {response.tool_invocations.length ? (
            <div className="table-scroll">
              <table>
                <caption className="sr-only">
                  Read-only tools invoked during this request
                </caption>
                <thead>
                  <tr>
                    <th>Allowlisted tool</th>
                    <th>Status</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {response.tool_invocations.map((tool, index) => (
                    <tr key={`${tool.name}-${index}`}>
                      <td>
                        <code>{tool.name}</code>
                      </td>
                      <td>{humanize(tool.status)}</td>
                      <td>{tool.duration_ms.toFixed(2)} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="muted">No tools were invoked for this request.</p>
          )}
        </div>
      )}
    </section>
  );
}

export function Lab() {
  const [question, setQuestion] = useState(examples[0].question);
  const [activeExample, setActiveExample] = useState(0);
  const [calculation, setCalculation] = useState(false);
  const [includeCompany, setIncludeCompany] = useState(false);
  const [companyId, setCompanyId] = useState("SYN-SME-001");
  const [operation, setOperation] = useState<Operation>("debt_to_income");
  const [values, setValues] = useState(["1500", "5000"]);
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [session, setSession] = useState<{
    cloud: boolean;
    authenticated: boolean;
  } | null>(null);
  const resultRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/auth/session", { cache: "no-store", signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error();
        return r.json();
      })
      .then((data) => {
        setSession(data);
        if (
          new URLSearchParams(window.location.search).get("auth") === "failed"
        )
          setError(
            "Sign-in could not be completed. Please try signing in again.",
          );
      })
      .catch(() => {
        if (!controller.signal.aborted)
          setError(
            "Could not check the application session. Refresh the page to retry.",
          );
      });
    return () => controller.abort();
  }, []);

  function chooseExample(index: number) {
    setActiveExample(index);
    setQuestion(examples[index].question);
    setCalculation(Boolean(examples[index].calculation));
    setIncludeCompany(Boolean(examples[index].companyId));
    setCompanyId(examples[index].companyId || "SYN-SME-001");
    setOperation("debt_to_income");
    setValues(operationFields.debt_to_income.defaults);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    const parsed = querySchema.safeParse({
      question,
      ...(includeCompany ? { company_id: companyId } : {}),
      ...(calculation
        ? {
            calculation: {
              operation,
              operands:
                operation === "sum"
                  ? values[0].split(",").map((v) => v.trim())
                  : values,
            },
          }
        : {}),
    });
    if (!parsed.success) {
      setError(
        parsed.error.issues[0]?.message ||
          "Check your question and calculation.",
      );
      return;
    }
    setPending(true);
    setResponse(null);
    try {
      const result = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed.data),
        signal: AbortSignal.timeout(65_000),
      });
      const data = await result.json();
      if (!result.ok) {
        if (result.status === 401)
          setSession({ cloud: true, authenticated: false });
        throw new Error(data.error || "The request could not be completed.");
      }
      const validated = responseSchema.safeParse(data);
      if (!validated.success)
        throw new Error(
          "The service returned an unexpected response. Please retry.",
        );
      setResponse(validated.data);
      window.setTimeout(
        () => resultRef.current?.focus({ preventScroll: true }),
        0,
      );
    } catch (cause) {
      setError(
        cause instanceof Error && cause.name !== "TimeoutError"
          ? cause.message
          : "The request timed out. Check the backend and try again.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#workspace">
        Skip to workspace
      </a>
      <aside className="sidebar">
        <a
          href="#workspace"
          className="brand"
          aria-label="Banking AI Prototype Lab home"
        >
          <span className="brand-mark" aria-hidden="true">
            <i />
            <i />
            <i />
          </span>
          <span>
            banking.ai<span className="brand-sub">PROTOTYPE LAB</span>
          </span>
        </a>
        <div className="nav-label">THE WORKSPACE</div>
        <nav aria-label="Workspace">
          <a className="nav-link active" href="#workspace">
            <span aria-hidden="true">▧</span> Operations desk{" "}
            <span className="nav-arrow">↗</span>
          </a>
          <a className="nav-link" href="#evidence">
            <span aria-hidden="true">▤</span> Evidence ledger
          </a>
          <a className="nav-link" href="#trace">
            <span aria-hidden="true">⌁</span> Execution trace
          </a>
          <a className="nav-link" href="#boundaries">
            <span aria-hidden="true">◇</span> Safety boundaries
          </a>
        </nav>
        <div className="sidebar-note">
          <span className="small-label">DESIGNED FOR OVERSIGHT</span>
          <p>Every useful answer should leave an evidence trail.</p>
          <div className="note-line" />
          <span>
            Read-only tools.
            <br />
            Accountable decisions.
            <br />
            Humans in control.
          </span>
        </div>
        <div className="sidebar-footer">
          <span className="status-dot" /> Portfolio environment
          <span>All internal data is synthetic</span>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <span>
            Solution architecture <span className="slash">/</span> Banking
            operations
          </span>
          <div className="topbar-right">
            <span className="synthetic-badge">
              <span /> SYNTHETIC DATA ONLY
            </span>
            {session?.cloud &&
              (session.authenticated ? (
                <form action="/api/auth/logout" method="post">
                  <button className="text-button" type="submit">
                    Sign out <Arrow />
                  </button>
                </form>
              ) : (
                <a className="text-button" href="/api/auth/login">
                  Sign in <Arrow />
                </a>
              ))}
          </div>
        </header>
        <main id="workspace">
          <section className="hero">
            <div>
              <div className="eyebrow">
                <span /> GOVERNED AI · EXPERIMENT 001
              </div>
              <h1>Evidence before action.</h1>
              <p>
                A controlled AI workspace for banking operations.
                <br className="desktop-break" /> Ask a question. Inspect the
                sources. Know when to escalate.
              </p>
            </div>
            <div className="hero-stamp">
              <span>FICTIONAL BANKING LAB</span>
              <strong>
                Human judgment
                <br />
                stays in the loop.
              </strong>
              <span className="stamp-rule" />
              <small>No real bank affiliation.</small>
            </div>
          </section>
          <div className="workspace-grid">
            <section
              className="question-panel"
              aria-labelledby="question-title"
            >
              <div className="panel-label">
                <span>01 / YOUR QUESTION</span>
                <span className="tiny-dot" />
              </div>
              <h2 id="question-title">What needs clarity?</h2>
              <p className="question-intro">
                Choose a scenario or ask an operational question using synthetic
                information.
              </p>
              <div className="examples" aria-label="Synthetic sample questions">
                {examples.map((sample, index) => (
                  <button
                    key={sample.name}
                    type="button"
                    className={`example ${activeExample === index ? "selected" : ""}`}
                    disabled={pending}
                    onClick={() => chooseExample(index)}
                  >
                    <span className="example-icon">{sample.icon}</span>
                    <span>
                      <strong>{sample.name}</strong>
                      <small>{sample.category}</small>
                    </span>
                    <Arrow />
                  </button>
                ))}
              </div>
              <form onSubmit={submit} className="question-form">
                <label htmlFor="question">Operational question</label>
                <textarea
                  id="question"
                  maxLength={4000}
                  rows={6}
                  value={question}
                  onChange={(e) => {
                    setQuestion(e.target.value);
                    setActiveExample(-1);
                  }}
                  disabled={pending}
                  required
                  aria-describedby="question-help"
                />
                <div id="question-help" className="field-help">
                  <span>No real personal or customer data.</span>
                  <span>{question.length}/4000</span>
                </div>
                <label className="calculation-toggle">
                  <input
                    type="checkbox"
                    checked={includeCompany}
                    onChange={(e) => setIncludeCompany(e.target.checked)}
                    disabled={pending}
                  />
                  <span>Include a synthetic SME profile</span>
                </label>
                {includeCompany && (
                  <fieldset
                    className="calculation-fields company-fields"
                    disabled={pending}
                  >
                    <legend>Governed company lookup</legend>
                    <label htmlFor="company-id">Synthetic company ID</label>
                    <input
                      id="company-id"
                      type="text"
                      value={companyId}
                      onChange={(e) => setCompanyId(e.target.value)}
                      maxLength={11}
                      pattern="SYN-SME-[0-9]{3}"
                      required
                      aria-describedby="company-help"
                      autoComplete="off"
                      spellCheck={false}
                    />
                    <p id="company-help">
                      SYN-SME-001: complete · 002: missing data · 003: stale.
                      Only governed Gold indicators are retrieved. An authorized
                      employee must review all lending cases.
                    </p>
                  </fieldset>
                )}
                <label className="calculation-toggle">
                  <input
                    type="checkbox"
                    checked={calculation}
                    onChange={(e) => setCalculation(e.target.checked)}
                    disabled={pending}
                  />
                  <span>Include a deterministic calculation</span>
                </label>
                {calculation && (
                  <fieldset className="calculation-fields" disabled={pending}>
                    <legend>Calculation inputs</legend>
                    <label htmlFor="operation">Operation</label>
                    <select
                      id="operation"
                      value={operation}
                      onChange={(e) => {
                        const value = e.target.value as Operation;
                        setOperation(value);
                        setValues(operationFields[value].defaults);
                      }}
                    >
                      <option value="debt_to_income">
                        Debt-to-income ratio
                      </option>
                      <option value="simple_interest">
                        Simple interest · actual/365
                      </option>
                      <option value="sum">Sum of values</option>
                    </select>
                    <div className={operation !== "sum" ? "operand-grid" : ""}>
                      {operationFields[operation].labels.map((label, index) => (
                        <div key={label}>
                          <label htmlFor={`operand-${index}`}>{label}</label>
                          <input
                            id={`operand-${index}`}
                            type="text"
                            inputMode={operation === "sum" ? "text" : "decimal"}
                            value={values[index] || ""}
                            maxLength={operation === "sum" ? 500 : 32}
                            onChange={(e) =>
                              setValues(
                                values.map((value, i) =>
                                  i === index ? e.target.value : value,
                                ),
                              )
                            }
                            required
                          />
                        </div>
                      ))}
                    </div>
                    <p>{operationFields[operation].helper}</p>
                  </fieldset>
                )}
                {error && (
                  <div className="error-message" role="alert">
                    <strong>Request needs attention</strong>
                    <p>{error}</p>
                  </div>
                )}
                {session?.cloud && !session.authenticated ? (
                  <a className="submit-button" href="/api/auth/login">
                    Sign in to ask <Arrow />
                  </a>
                ) : (
                  <button
                    className="submit-button"
                    disabled={pending || !question.trim() || !session}
                    type="submit"
                  >
                    {pending ? (
                      <>
                        <span className="spinner" /> Checking evidence…
                      </>
                    ) : (
                      <>
                        Generate grounded response <Arrow />
                      </>
                    )}
                  </button>
                )}
                <p className="submit-note">
                  {session?.cloud
                    ? "Authenticated workspace · controlled, read-only tools"
                    : "Local baseline · no AWS credentials or LLM required"}
                </p>
              </form>
            </section>
            <div className="response-column">
              <section
                className="response-panel"
                aria-labelledby="response-title"
                aria-busy={pending}
                tabIndex={-1}
                ref={resultRef}
              >
                <div className="response-toolbar">
                  <span className="panel-label">02 / GROUNDED RESPONSE</span>
                  <span className={`pill ${response ? "good" : "neutral"}`}>
                    <span className="pill-dot" />
                    {pending
                      ? "Processing"
                      : response
                        ? response.mode === "local"
                          ? "Local baseline"
                          : "Bedrock planner"
                        : "Ready for a question"}
                  </span>
                </div>
                <div aria-live="polite" className="sr-only">
                  {pending
                    ? "Running the governed workflow. Please wait."
                    : response
                      ? `Response ready. Human review ${response.human_review_required ? "required" : "not required for this response"}.`
                      : ""}
                </div>
                {response ? (
                  <>
                    <div
                      className={`review-banner ${response.human_review_required ? "review-required" : "review-clear"}`}
                    >
                      <span aria-hidden="true">
                        {response.human_review_required ? "◇" : "✓"}
                      </span>
                      <div>
                        <strong>
                          {response.human_review_required
                            ? "Human review required"
                            : "Human review not required for this response"}
                        </strong>
                        <p>
                          {response.human_review_required
                            ? "An authorized employee must review the evidence before any operational decision."
                            : "This response grants no authority to approve credit, transact, or alter records."}
                        </p>
                      </div>
                    </div>
                    {response.financial_profile && (
                      <FinancialProfileCard
                        profile={response.financial_profile}
                      />
                    )}
                    <div className="answer-content">
                      <h2 id="response-title">A considered next step.</h2>
                      <p className="answer-text">{response.answer}</p>
                      <div className="answer-meta">
                        <span>
                          <span className="confidence-bar">
                            <i
                              style={{ width: `${response.confidence * 100}%` }}
                            />
                          </span>
                          {Math.round(response.confidence * 100)}% reported
                          confidence
                        </span>
                        <a href="#evidence">
                          Inspect {response.evidence.length} evidence item
                          {response.evidence.length === 1 ? "" : "s"} <Arrow />
                        </a>
                      </div>
                      <p className="confidence-note">
                        Confidence is a workflow signal, not a calibrated
                        probability of correctness.
                      </p>
                      {response.risk_flags.length > 0 && (
                        <div className="risk-flags" aria-label="Risk flags">
                          {response.risk_flags.map((flag) => (
                            <span key={flag}>{humanize(flag)}</span>
                          ))}
                        </div>
                      )}
                      {response.risk_flags.length === 0 && (
                        <p className="muted small-copy">
                          No risk flags reported by the workflow.
                        </p>
                      )}
                      <div className="detail-grid">
                        <DetailList
                          title="Assumptions"
                          items={response.assumptions}
                          empty="No assumptions were reported."
                        />
                        <DetailList
                          title="Missing information"
                          items={response.missing_information}
                          empty="No missing information was reported."
                        />
                      </div>
                    </div>
                  </>
                ) : (
                  <div
                    className={`empty-state ${pending ? "loading-state" : ""}`}
                  >
                    <div className="evidence-orbit" aria-hidden="true">
                      <span className="orbit-node node-one" />
                      <span className="orbit-node node-two" />
                      <span className="orbit-node node-three" />
                      <span className="orbit-center">
                        {pending ? "⌁" : "✓"}
                      </span>
                    </div>
                    <div className="eyebrow">
                      {pending
                        ? "FOLLOWING THE EVIDENCE"
                        : "READY WHEN YOU ARE"}
                    </div>
                    <h2 id="response-title">
                      {pending
                        ? "A little rigor goes a long way."
                        : "Useful answers. Visible reasoning."}
                    </h2>
                    <p>
                      {pending
                        ? "Retrieving sources, validating controlled actions, and checking citations. The completed trace will appear below."
                        : "Your response will connect operational guidance to its source evidence, surface uncertainty, and make human review explicit."}
                    </p>
                    <div className="empty-features">
                      <span>
                        <i>01</i> Source-backed claims
                      </span>
                      <span>
                        <i>02</i> Bounded tools
                      </span>
                      <span>
                        <i>03</i> Visible escalation
                      </span>
                    </div>
                  </div>
                )}
                <div
                  className="metrics-strip"
                  aria-label="Request measurements"
                >
                  <div>
                    <span>Total latency</span>
                    <strong>
                      {response
                        ? `${response.metrics.latency_ms.toFixed(1)}`
                        : "—"}
                      <small>{response ? " ms" : ""}</small>
                    </strong>
                  </div>
                  <div>
                    <span>Retrieval</span>
                    <strong>
                      {response
                        ? response.metrics.retrieval_latency_ms.toFixed(1)
                        : "—"}
                      <small>{response ? " ms" : ""}</small>
                    </strong>
                  </div>
                  <div>
                    <span>Model tokens</span>
                    <strong>
                      {response
                        ? `${response.metrics.input_tokens} / ${response.metrics.output_tokens}`
                        : "—"}
                    </strong>
                    <small>input / output</small>
                  </div>
                  <div>
                    <span>Est. model cost</span>
                    <strong>
                      {response
                        ? response.metrics.cost_estimate_complete
                          ? `$${response.metrics.estimated_cost_usd.toFixed(6)}`
                          : "Unknown"
                        : "—"}
                    </strong>
                    <small>
                      {response && !response.metrics.cost_estimate_complete
                        ? `Recorded ≥ $${response.metrics.estimated_cost_usd.toFixed(6)}`
                        : "USD / request"}
                    </small>
                  </div>
                </div>
                {response && (
                  <div className="run-footer">
                    <code>RUN {response.request_id}</code>
                    <span>
                      Model latency{" "}
                      {response.metrics.model_latency_ms.toFixed(1)} ms
                    </span>
                  </div>
                )}
              </section>
              {response ? (
                <Evidence response={response} />
              ) : (
                <div id="evidence" className="evidence-placeholder">
                  <span aria-hidden="true">▤</span>
                  <p>
                    <strong>An evidence ledger, not a black box.</strong> Source
                    excerpts, versions, and integrity hashes appear here after
                    your first request.
                  </p>
                </div>
              )}
              <Trace response={response} />
            </div>
          </div>
          <section id="boundaries" className="boundaries">
            <div>
              <span className="eyebrow">THE OPERATING BOUNDARY</span>
              <h2>
                Assistance has limits.
                <br />
                They are deliberate.
              </h2>
            </div>
            <div className="boundary-copy">
              <p>
                This fictional portfolio lab searches synthetic internal
                policies and selected public references. It supports an
                employee’s judgment; every important recommendation should
                expose its evidence.
              </p>
              <div className="boundary-tags">
                <span>No credit approval</span>
                <span>No transactions</span>
                <span>No binding investment advice</span>
                <span>No record changes</span>
                <span>No approval bypass</span>
              </div>
              <p className="small-copy">
                Local mode measures a deterministic baseline. Bedrock mode uses
                an LLM planner inside the same controlled workflow. Cost
                estimates cover model usage only; public references require
                freshness and jurisdiction checks.
              </p>
            </div>
          </section>
          <footer className="page-footer">
            <span>BANKING AI PROTOTYPE LAB</span>
            <span>
              Synthetic scenarios. Explicit boundaries. No real bank
              affiliation.
            </span>
            <a href="#workspace">Back to workspace ↑</a>
          </footer>
        </main>
      </div>
    </div>
  );
}
