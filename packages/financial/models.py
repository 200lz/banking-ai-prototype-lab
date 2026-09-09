"""Strict, content-bounded quantitative evidence contracts."""

import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CompanyId = Annotated[
    str, Field(pattern=r"^SYN-SME-[0-9]{3}$", min_length=11, max_length=11, strict=True)
]
Metric = Annotated[str, Field(pattern=r"^-?[0-9]{1,30}\.[0-9]{2,4}$", strict=True)]
FORMULA_VERSION: Literal["sme-gold-v1"] = "sme-gold-v1"
METRIC_DEFINITIONS = {
    "revenue_trend": "(last monthly revenue / first monthly revenue - 1) * 100; percent",
    "cashflow_volatility": "population standard deviation of monthly operating cash inflow minus outflow; JPY",
    "debt_service_ratio": "sum scheduled debt service / sum operating cash inflow; ratio, not a credit threshold",
    "liquidity_indicator": "latest closing balance / average monthly operating cash outflow; months",
}
MissingField = Literal[
    "monthly_revenue",
    "cash_inflow",
    "cash_outflow",
    "debt_service_due",
    "closing_balance",
    "transaction_count",
    "industry",
    "period_gap",
    "insufficient_history",
    "conflicting_duplicate",
    "rejected_records",
    "non_positive_revenue_baseline",
    "non_positive_cash_inflow",
    "non_positive_cash_outflow",
]


class FinancialModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FinancialProfileArgs(FinancialModel):
    company_id: CompanyId


class FinancialProvenance(FinancialModel):
    dataset_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    gold_record_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_record_ids: list[Annotated[str, Field(pattern=r"^SYN-FIN-[A-Z0-9-]{1,48}$")]] = Field(
        min_length=1, max_length=120
    )
    formula_version: Literal["sme-gold-v1"] = FORMULA_VERSION
    layer: Literal["gold"] = "gold"
    source_table: Literal["financial_gold"] = "financial_gold"
    metric_definitions: dict[str, str]

    @field_validator("metric_definitions")
    @classmethod
    def trusted_definitions(cls, value: dict[str, str]) -> dict[str, str]:
        if value != METRIC_DEFINITIONS:
            raise ValueError("Unknown financial formula definitions")
        return value


class FinancialProfile(FinancialModel):
    company_id: CompanyId
    source: Literal["local", "databricks"]
    revenue_trend: Metric | None
    cashflow_volatility: Metric | None
    debt_service_ratio: Metric | None
    liquidity_indicator: Metric | None
    missing_fields: list[MissingField] = Field(max_length=20)
    data_as_of: datetime
    stale: bool = Field(strict=True)
    period_count: int = Field(ge=1, le=120, strict=True)
    currency: Literal["JPY"] = "JPY"
    provenance: FinancialProvenance

    @field_validator("data_as_of")
    @classmethod
    def aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("data_as_of must have a timezone")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def invariant_checks(self) -> "FinancialProfile":
        for value in (self.cashflow_volatility, self.debt_service_ratio):
            if value is not None and Decimal(value) < 0:
                raise ValueError("Volatility and debt service cannot be negative")
        if len(set(self.provenance.source_record_ids)) != len(self.provenance.source_record_ids):
            raise ValueError("Duplicate quantitative provenance IDs")
        if len(set(self.missing_fields)) != len(self.missing_fields):
            raise ValueError("Duplicate missing-data flags")
        return self


def gold_hash(profile: FinancialProfile) -> str:
    """Hash a Gold snapshot; delivery adapter and request-time freshness are excluded."""
    value = profile.model_dump(mode="json")
    value.pop("source", None)
    value.pop("stale", None)
    provenance = dict(value["provenance"])
    provenance.pop("gold_record_sha256", None)
    value["provenance"] = provenance
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify_profile(
    profile: FinancialProfile,
    company_id: str,
    *,
    now: datetime,
    max_age_days: int = 45,
    source: Literal["local", "databricks"] = "local",
) -> FinancialProfile:
    FinancialProfileArgs(company_id=company_id)
    if (
        profile.company_id != company_id
        or gold_hash(profile) != profile.provenance.gold_record_sha256
    ):
        raise ValueError("Financial profile identity or integrity mismatch")
    age = now.astimezone(UTC) - profile.data_as_of
    if age.total_seconds() < 0:
        raise ValueError("Financial profile observation is in the future")
    if not 1 <= max_age_days <= 365:
        raise ValueError("Financial freshness window must be 1..365 days")
    return profile.model_copy(
        update={"source": source, "stale": age.total_seconds() > max_age_days * 86400}
    )
