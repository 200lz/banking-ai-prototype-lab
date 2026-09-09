"""Rebuild fictional monthly source data and the committed local Gold snapshot."""

import calendar
import json
from pathlib import Path
from typing import Any

from packages.financial.pipeline import build_layers

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    rows: list[dict[str, Any]] = []
    revenue = [1000000, 1050000, 1100000, 1080000, 1150000, 1200000]
    inflow = [950000, 1000000, 1020000, 1070000, 1100000, 1140000]
    outflow = [800000, 810000, 790000, 850000, 830000, 860000]
    for company in range(1, 4):
        for index in range(6):
            year, month = (2025, 7 + index) if company == 3 else (2026, 3 + index)
            month_key = f"{year}-{month:02d}"
            row: dict[str, Any] = {
                "source_record_id": f"SYN-FIN-{company:03d}-{year}{month:02d}",
                "company_id": f"SYN-SME-{company:03d}",
                "month": month_key + "-01",
                "observed_at": f"{month_key}-{calendar.monthrange(year, month)[1]}T00:00:00Z",
                "currency": "JPY",
                "industry": ["manufacturing", "retail", "services"][company - 1],
                "monthly_revenue": str(revenue[index]),
                "cash_inflow": str(inflow[index]),
                "cash_outflow": str(outflow[index]),
                "debt_service_due": "90000",
                "closing_balance": str(1200000 + 80000 * index),
                "transaction_count": 100 + 10 * index,
            }
            if company == 2:
                if index == 2:
                    row["cash_inflow"] = None
                if index == 3:
                    row["monthly_revenue"] = None
                if index == 5:
                    row["closing_balance"] = None
            rows.append(row)
    rows.append(dict(rows[0]))
    rejected = dict(rows[6])
    rejected.update(source_record_id="SYN-FIN-002-INVALID", monthly_revenue="invalid-decimal")
    rows.append(rejected)
    payload = (json.dumps(rows, indent=2) + "\n").encode()
    (ROOT / "data/synthetic/financial_raw.json").write_bytes(payload)
    layers = build_layers(payload)
    (ROOT / "data/synthetic/financial_gold.json").write_text(
        json.dumps(layers["gold"], indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(layers["quality"], indent=2))


if __name__ == "__main__":
    main()
