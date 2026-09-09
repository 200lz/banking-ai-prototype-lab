"""Gold-only local and Databricks reads; no caller-supplied SQL or model credentials."""

import json
import os
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlparse

from packages.financial.models import FinancialProfile, FinancialProfileArgs, verify_profile

ROOT = Path(__file__).resolve().parents[2]
FIXED_PROFILE_SQL = (
    "SELECT profile_json, profile_sha256 FROM financial_gold WHERE company_id = :company_id LIMIT 2"
)


class FinancialProfileProvider(Protocol):
    def get_profile(self, company_id: str) -> FinancialProfile | None: ...


class FinancialUnavailableError(RuntimeError):
    """Safe service error; no credentials, query results or raw vendor message."""


def utc_now() -> datetime:
    return datetime.now(UTC)


class LocalFinancialAdapter:
    """The application reads only a published Gold artifact, never raw monthly rows."""

    def __init__(
        self,
        path: Path | None = None,
        *,
        now: Callable[[], datetime] = utc_now,
        max_age_days: int = 45,
    ) -> None:
        self.path = path if path is not None else ROOT / "data/synthetic/financial_gold.json"
        self.now = now
        self.max_age_days = max_age_days

    def get_profile(self, company_id: str) -> FinancialProfile | None:
        FinancialProfileArgs(company_id=company_id)
        payload = self.path.read_bytes()
        if len(payload) > 2_000_000:
            raise FinancialUnavailableError("Gold artifact exceeds size limit")
        values = json.loads(payload)
        if not isinstance(values, list) or len(values) > 1000:
            raise FinancialUnavailableError("Gold artifact has invalid shape")
        profiles = [FinancialProfile.model_validate(value) for value in values]
        if len({profile.company_id for profile in profiles}) != len(profiles):
            raise FinancialUnavailableError("Gold artifact contains duplicate company IDs")
        profile = next((profile for profile in profiles if profile.company_id == company_id), None)
        return (
            None
            if profile is None
            else verify_profile(profile, company_id, now=self.now(), max_age_days=self.max_age_days)
        )


class DatabricksFinancialAdapter:
    """One fixed parameterized Statement Execution request against a governed Gold table."""

    def __init__(
        self,
        *,
        warehouse_id: str,
        catalog: str,
        schema: str,
        client: Any = None,
        now: Callable[[], datetime] = utc_now,
        max_age_days: int = 45,
    ) -> None:
        if not re.fullmatch(r"[a-f0-9]{16}", warehouse_id):
            raise ValueError("A valid SQL warehouse identifier is required")
        if any(not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name) for name in (catalog, schema)):
            raise ValueError("Catalog and schema must be scoped SQL identifiers")
        self.warehouse_id, self.catalog, self.schema = warehouse_id, catalog, schema
        self.client = client
        self.now, self.max_age_days = now, max_age_days

    def _api(self) -> Any:
        if self.client is not None:
            return self.client
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.core import Config

        from services.agent.observability import configure_private_sdk_logging

        configure_private_sdk_logging()
        host = os.environ.get("DATABRICKS_HOST", "")
        parsed = urlparse(host)
        if (
            parsed.scheme != "https"
            or not (parsed.hostname or "").endswith(".cloud.databricks.com")
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
            or parsed.port not in {None, 443}
        ):
            raise FinancialUnavailableError(
                "A configured AWS Databricks workspace HTTPS host is required"
            )
        # Unified auth uses environment/provider credentials; no token enters this contract.
        config = Config(
            host=host,
            http_timeout_seconds=12,
            retry_timeout_seconds=1,
            debug_headers=False,
            debug_truncate_bytes=0,
        )
        self.client = WorkspaceClient(config=config).api_client
        return self.client

    def get_profile(self, company_id: str) -> FinancialProfile | None:
        FinancialProfileArgs(company_id=company_id)
        body = {
            "warehouse_id": self.warehouse_id,
            "catalog": self.catalog,
            "schema": self.schema,
            "statement": FIXED_PROFILE_SQL,
            "parameters": [{"name": "company_id", "value": company_id, "type": "STRING"}],
            "wait_timeout": "10s",
            "on_wait_timeout": "CANCEL",
            "format": "JSON_ARRAY",
            "disposition": "INLINE",
            "row_limit": 2,
            "byte_limit": 65536,
        }
        try:
            response = self._api().do("POST", "/api/2.0/sql/statements", body=body)
            if (
                not isinstance(response, dict)
                or len(json.dumps(response)) > 131072
                or response.get("status", {}).get("state") != "SUCCEEDED"
            ):
                raise FinancialUnavailableError("Gold statement did not complete successfully")
            manifest, result = response.get("manifest", {}), response.get("result", {})
            columns = manifest.get("schema", {}).get("columns", [])
            if (
                manifest.get("truncated", False)
                or result.get("next_chunk_index") is not None
                or result.get("external_links")
                or [(column.get("name"), column.get("type_name")) for column in columns]
                != [("profile_json", "STRING"), ("profile_sha256", "STRING")]
            ):
                raise FinancialUnavailableError(
                    "Gold statement response exceeds the approved schema"
                )
            rows = result.get("data_array", [])
            if (
                not isinstance(rows, list)
                or len(rows) > 1
                or manifest.get("total_row_count") != len(rows)
            ):
                raise FinancialUnavailableError("Gold statement returned ambiguous company records")
            if not rows:
                return None
            if (
                not isinstance(rows[0], list)
                or len(rows[0]) != 2
                or not all(isinstance(value, str) for value in rows[0])
            ):
                raise FinancialUnavailableError("Gold statement returned invalid data")
            profile = FinancialProfile.model_validate_json(rows[0][0])
            if rows[0][1] != profile.provenance.gold_record_sha256:
                raise FinancialUnavailableError("Gold record hash column mismatch")
            return verify_profile(
                profile,
                company_id,
                now=self.now(),
                max_age_days=self.max_age_days,
                source="databricks",
            )
        except Exception:
            raise FinancialUnavailableError(
                "Governed Databricks Gold profile is unavailable"
            ) from None


def provider_from_environment() -> FinancialProfileProvider:
    backend = os.environ.get("FINANCIAL_BACKEND", "local")
    max_age = int(os.environ.get("FINANCIAL_MAX_AGE_DAYS", "45"))
    if backend == "local":
        return LocalFinancialAdapter(max_age_days=max_age)
    if backend == "databricks":
        return DatabricksFinancialAdapter(
            warehouse_id=os.environ["DATABRICKS_WAREHOUSE_ID"],
            catalog=os.environ["DATABRICKS_CATALOG"],
            schema=os.environ["DATABRICKS_SCHEMA"],
            max_age_days=max_age,
        )
    raise ValueError("Unknown financial profile backend")
