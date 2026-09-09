"""Reproducible bounded RAW/BRONZE/SILVER/GOLD computation, shared with Databricks."""

import argparse
import calendar
import hashlib
import json
from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal, localcontext
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import Field, ValidationError, field_validator, model_validator

from packages.financial.models import (
    METRIC_DEFINITIONS,
    CompanyId,
    FinancialModel,
    FinancialProfile,
    FinancialProvenance,
    MissingField,
    gold_hash,
)

ROOT = Path(__file__).resolve().parents[2]
MONEY_FIELDS = (
    "monthly_revenue",
    "cash_inflow",
    "cash_outflow",
    "debt_service_due",
    "closing_balance",
)


class SilverRow(FinancialModel):
    source_record_id: str = Field(pattern=r"^SYN-FIN-[A-Z0-9-]{1,48}$")
    company_id: CompanyId
    month: date
    observed_at: datetime
    currency: Literal["JPY"] = "JPY"
    industry: Literal["manufacturing", "retail", "services"] | None
    monthly_revenue: Decimal | None
    cash_inflow: Decimal | None
    cash_outflow: Decimal | None
    debt_service_due: Decimal | None
    closing_balance: Decimal | None
    transaction_count: int | None = Field(ge=0, le=10000000, strict=True)

    @field_validator(*MONEY_FIELDS, mode="before")
    @classmethod
    def exact_money(cls, value: Any) -> Any:
        if isinstance(value, (float, bool)):
            raise ValueError("Financial input requires decimal strings or integers")
        return value

    @field_validator(*MONEY_FIELDS)
    @classmethod
    def bounded_money(cls, value: Decimal | None) -> Decimal | None:
        if value is not None:
            exponent = value.as_tuple().exponent
            if (
                not value.is_finite()
                or abs(value) > Decimal("1000000000000")
                or not isinstance(exponent, int)
                or not -8 <= exponent <= 12
            ):
                raise ValueError("Invalid financial decimal magnitude or precision")
        return value

    @field_validator("observed_at")
    @classmethod
    def aware_observation(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Observation requires a timezone")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def monthly_contract(self) -> "SilverRow":
        month_end = date(
            self.month.year,
            self.month.month,
            calendar.monthrange(self.month.year, self.month.month)[1],
        )
        if self.month.day != 1 or self.observed_at.date() < month_end:
            raise ValueError(
                "Monthly rows require first-day month keys and observations after month completion"
            )
        for name in MONEY_FIELDS[:-1]:
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError("Revenue and flow amounts must be nonnegative")
        return self


def _rounded(value: Decimal, places: int = 2) -> str:
    return format(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP), "f")


def make_gold(
    rows: list[SilverRow], dataset_hash: str, flags: set[MissingField] | None = None
) -> FinancialProfile:
    if not rows or len(rows) > 120 or len({row.company_id for row in rows}) != 1:
        raise ValueError("Gold requires 1..120 monthly rows for exactly one company")
    rows = sorted(rows, key=lambda row: row.month)
    if len({row.month for row in rows}) != len(rows):
        raise ValueError("Gold cannot consume duplicate months")
    missing: set[MissingField] = set(flags or ())
    for name in (*MONEY_FIELDS, "industry", "transaction_count"):
        if any(getattr(row, name) is None for row in rows):
            missing.add(cast(MissingField, name))
    month_indices = [row.month.year * 12 + row.month.month for row in rows]
    if month_indices[-1] - month_indices[0] + 1 != len(rows):
        missing.add("period_gap")
    if len(rows) < 2:
        missing.add("insufficient_history")
    trend = volatility = debt_ratio = liquidity = None
    with localcontext() as context:
        context.prec = 40
        if "monthly_revenue" not in missing and len(rows) >= 2:
            first = cast(Decimal, rows[0].monthly_revenue)
            last = cast(Decimal, rows[-1].monthly_revenue)
            if first > 0:
                trend = _rounded((last / first - 1) * 100)
            else:
                missing.add("non_positive_revenue_baseline")
        if not {"cash_inflow", "cash_outflow"}.intersection(missing) and len(rows) >= 2:
            net = [cast(Decimal, row.cash_inflow) - cast(Decimal, row.cash_outflow) for row in rows]
            mean = sum(net, Decimal(0)) / Decimal(len(rows))
            variance = sum(((value - mean) ** 2 for value in net), Decimal(0)) / Decimal(len(net))
            volatility = _rounded(variance.sqrt())
        if not {"cash_inflow", "debt_service_due"}.intersection(missing):
            inflow = sum((cast(Decimal, row.cash_inflow) for row in rows), Decimal(0))
            if inflow > 0:
                debt_ratio = _rounded(
                    sum((cast(Decimal, row.debt_service_due) for row in rows), Decimal(0)) / inflow,
                    4,
                )
            else:
                missing.add("non_positive_cash_inflow")
        if not {"cash_outflow", "closing_balance"}.intersection(missing):
            outflow = sum((cast(Decimal, row.cash_outflow) for row in rows), Decimal(0)) / Decimal(
                len(rows)
            )
            if outflow > 0:
                liquidity = _rounded(cast(Decimal, rows[-1].closing_balance) / outflow, 4)
            else:
                missing.add("non_positive_cash_outflow")
    draft = FinancialProfile(
        company_id=rows[0].company_id,
        source="local",
        revenue_trend=trend,
        cashflow_volatility=volatility,
        debt_service_ratio=debt_ratio,
        liquidity_indicator=liquidity,
        missing_fields=sorted(missing),
        data_as_of=datetime(
            rows[-1].month.year,
            rows[-1].month.month,
            calendar.monthrange(rows[-1].month.year, rows[-1].month.month)[1],
            tzinfo=UTC,
        ),
        stale=False,
        period_count=len(rows),
        provenance=FinancialProvenance(
            dataset_sha256=dataset_hash,
            gold_record_sha256="0" * 64,
            source_record_ids=[row.source_record_id for row in rows],
            metric_definitions=METRIC_DEFINITIONS,
        ),
    )
    return draft.model_copy(
        update={
            "provenance": draft.provenance.model_copy(
                update={"gold_record_sha256": gold_hash(draft)}
            )
        }
    )


def build_layers(raw_bytes: bytes) -> dict[str, Any]:
    if len(raw_bytes) > 2_000_000:
        raise ValueError("Synthetic financial source exceeds 2 MB")
    raw = json.loads(raw_bytes)
    if not isinstance(raw, list) or not 1 <= len(raw) <= 5000:
        raise ValueError("Synthetic financial source requires 1..5000 rows")
    dataset_hash = hashlib.sha256(raw_bytes).hexdigest()
    bronze, rejected = [], []
    candidates: dict[tuple[str, date], list[SilverRow]] = defaultdict(list)
    flags: dict[str, set[MissingField]] = defaultdict(set)
    for ordinal, value in enumerate(raw):
        serialized = json.dumps(value, sort_keys=True, separators=(",", ":"))
        row_hash = hashlib.sha256(serialized.encode()).hexdigest()
        bronze.append(
            {
                "ordinal": ordinal,
                "raw_payload": serialized,
                "row_sha256": row_hash,
                "dataset_sha256": dataset_hash,
            }
        )
        try:
            row = SilverRow.model_validate(value)
            candidates[(row.company_id, row.month)].append(row)
        except ValidationError as error:
            rejected.append(
                {
                    "ordinal": ordinal,
                    "row_sha256": row_hash,
                    "error_codes": sorted({item["type"] for item in error.errors()}),
                }
            )
            if isinstance(value, dict) and isinstance(value.get("company_id"), str):
                flags[value["company_id"]].add("rejected_records")
    silver: list[SilverRow] = []
    duplicate_count = 0
    for (company_id, _), group in sorted(candidates.items()):
        # Only byte-equivalent normalized duplicate records may collapse silently.
        fingerprints = {row.model_dump_json() for row in group}
        if len(fingerprints) != 1:
            flags[company_id].add("conflicting_duplicate")
            continue
        duplicate_count += len(group) - 1
        silver.append(group[0])
    by_company: dict[str, list[SilverRow]] = defaultdict(list)
    for row in silver:
        by_company[row.company_id].append(row)
    gold = [
        make_gold(rows, dataset_hash, flags[company_id])
        for company_id, rows in sorted(by_company.items())
    ]
    return {
        "bronze": bronze,
        "silver": [row.model_dump(mode="json") for row in silver],
        "gold": [profile.model_dump(mode="json") for profile in gold],
        "rejected": rejected,
        "quality": {
            "input_rows": len(raw),
            "silver_rows": len(silver),
            "duplicate_rows": duplicate_count,
            "rejected_rows": len(rejected),
            "gold_profiles": len(gold),
            "dataset_sha256": dataset_hash,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/synthetic/financial_raw.json")
    parser.add_argument("--output", type=Path, default=ROOT / ".runtime/financial")
    args = parser.parse_args()
    layers = build_layers(args.input.read_bytes())
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in layers.items():
        (args.output / (name + ".json")).write_text(
            json.dumps(rows, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(layers["quality"], indent=2))


if __name__ == "__main__":
    main()
