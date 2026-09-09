import type { FinancialProfile as Profile } from "@/lib/contracts";
import { humanize } from "@/lib/contracts";

const metrics = [
  { key: "revenue_trend", label: "Revenue trend", unit: "%" },
  { key: "cashflow_volatility", label: "Cash-flow volatility", unit: "JPY" },
  { key: "debt_service_ratio", label: "Debt-service ratio", unit: "ratio" },
  { key: "liquidity_indicator", label: "Liquidity indicator", unit: "months" },
] as const;

export function FinancialProfileCard({ profile }: { profile: Profile }) {
  return (
    <section
      className="financial-profile"
      aria-labelledby="financial-profile-title"
    >
      <div className="section-heading">
        <h2 id="financial-profile-title">Governed financial profile</h2>
        <span className="pill good">GOLD · {profile.currency}</span>
      </div>
      <p className="profile-source">
        <strong>{profile.company_id}</strong>
        <span>
          {profile.source === "local"
            ? "Local deterministic adapter"
            : "Databricks Gold adapter"}{" "}
          · {profile.period_count} periods
        </span>
      </p>
      <div className="profile-metrics">
        {metrics.map((metric) => (
          <div key={metric.key}>
            <h3>{metric.label}</h3>
            <p
              className={
                profile[metric.key] === null ? "metric-unavailable" : ""
              }
            >
              {profile[metric.key] ?? "Unavailable"}
              {profile[metric.key] !== null && <small>{metric.unit}</small>}
            </p>
          </div>
        ))}
      </div>
      <div className="profile-asof">
        <span>
          Data as of{" "}
          <time dateTime={profile.data_as_of}>{profile.data_as_of}</time>
        </span>
        <span className={`pill ${profile.stale ? "warning" : "good"}`}>
          {profile.stale ? "Stale data" : "Within freshness policy"}
        </span>
      </div>
      {profile.stale && (
        <p className="profile-warning">
          The data is stale. Obtain current evidence before the authorized
          lending review.
        </p>
      )}
      {profile.missing_fields.length > 0 ? (
        <div className="profile-warning">
          <strong>Missing or invalid data</strong>
          <ul>
            {profile.missing_fields.map((field) => (
              <li key={field}>{humanize(field)}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="profile-note">
          No missing fields reported by the governed tool.
        </p>
      )}
      <details className="profile-provenance">
        <summary>Inspect formulas and provenance</summary>
        <dl>
          {metrics.map((metric) => (
            <div key={metric.key}>
              <dt>{metric.label}</dt>
              <dd>{profile.provenance.metric_definitions[metric.key]}</dd>
            </div>
          ))}
          <div>
            <dt>Formula version / layer</dt>
            <dd>
              {profile.provenance.formula_version} / {profile.provenance.layer}{" "}
              / {profile.provenance.source_table}
            </dd>
          </div>
          <div>
            <dt>Dataset SHA-256</dt>
            <dd>
              <code>{profile.provenance.dataset_sha256}</code>
            </dd>
          </div>
          <div>
            <dt>Gold record SHA-256</dt>
            <dd>
              <code>{profile.provenance.gold_record_sha256}</code>
            </dd>
          </div>
          <div>
            <dt>Synthetic source record IDs</dt>
            <dd>
              {profile.provenance.source_record_ids.join(", ") ||
                "No source record identifiers provided."}
            </dd>
          </div>
        </dl>
      </details>
      <p className="profile-boundary">
        Human review is mandatory. These deterministic indicators do not
        establish credit eligibility or approve lending.
      </p>
      {profile.source === "local" && (
        <p className="profile-note">
          Local Gold output is not evidence of a verified Databricks workspace
          run. No raw financial records are displayed.
        </p>
      )}
    </section>
  );
}
