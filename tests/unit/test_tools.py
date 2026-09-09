from decimal import Decimal

import pytest
from pydantic import ValidationError

from packages.retrieval.local import LocalRetriever
from services.agent.models import Calculation, Evidence
from services.agent.observability import AuditLogger
from services.agent.tools import ToolRegistry, calculate


@pytest.mark.parametrize(
    ("operation", "operands", "expected"),
    [
        ("sum", ["0.1", "0.2"], "0.30"),
        ("debt_to_income", ["1000", "3000"], "33.33"),
        ("simple_interest", ["1000", "5", "365"], "50.00"),
        ("sum", ["1.005"], "1.01"),
    ],
)
def test_deterministic_decimal_arithmetic(operation, operands, expected):
    result = calculate(Calculation(operation=operation, operands=operands))
    assert result.value == expected


@pytest.mark.parametrize(
    "payload",
    [
        {"operation": "sum", "operands": ["NaN"]},
        {"operation": "sum", "operands": ["Infinity"]},
        {"operation": "sum", "operands": ["1e20"]},
        {"operation": "sum", "operands": ["0.000000001"]},
        {"operation": "debt_to_income", "operands": [1, 0]},
        {"operation": "simple_interest", "operands": [1000, 500, 3]},
        {"operation": "sum", "operands": [1], "code": "arbitrary"},
    ],
)
def test_invalid_calculations_fail_schema(payload):
    with pytest.raises(ValidationError):
        Calculation.model_validate(payload)


def test_registry_denies_unknown_tools_and_arguments(tmp_path):
    registry = ToolRegistry(LocalRetriever(), AuditLogger(tmp_path / "audit.jsonl"), "test")
    assert len(registry.schemas) == 5
    with pytest.raises(ValueError, match="allowlisted"):
        registry.invoke("shell", {"command": "whoami"})
    with pytest.raises(ValidationError):
        registry.invoke(
            "policy_search", {"query": "onboarding", "max_classification": "restricted"}
        )
    with pytest.raises(ValidationError):
        registry.invoke("policy_search", {"query": "onboarding", "top_k": "10"})


def test_citations_require_exact_claim_quote_and_current_hash(tmp_path):
    retriever = LocalRetriever()
    document = retriever.get("SYN-AML-001")
    assert document is not None
    registry = ToolRegistry(retriever, AuditLogger(tmp_path / "audit.jsonl"), "test")
    evidence = Evidence(
        id="E1",
        document_id=document.id,
        claim=document.text,
        quote=document.text,
        source_hash=document.sha256,
    )
    assert registry.verify_citations([evidence])[0].verified
    assert not registry.verify_citations(
        [evidence.model_copy(update={"claim": "Unsupported approval"})]
    )[0].verified
    assert not registry.verify_citations([evidence.model_copy(update={"source_hash": "0" * 64})])[
        0
    ].verified
    # A substring can remove a negation while still appearing verbatim in a document.
    fragment = "submit a regulatory report."
    assert fragment in document.text
    assert not registry.verify_citations(
        [evidence.model_copy(update={"claim": fragment, "quote": fragment})]
    )[0].verified
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")


@pytest.mark.parametrize("value", [True, False, 0.1, "0e999999", "0e-999999"])
def test_coercion_and_zero_exponent_extremes_are_rejected(value):
    with pytest.raises(ValidationError):
        Calculation(operation="sum", operands=[value])


def test_extreme_permitted_decimal_operand_is_exact():
    result = calculate(
        Calculation(operation="debt_to_income", operands=["1000000000000", "0.00000001"])
    )
    assert result.value == "10000000000000000000000.00"


@pytest.mark.parametrize(
    "field, value",
    [
        ("version", "123-45-6789"),
        ("title", "Contact private@example.test"),
        ("tags", ["customer 123-45-6789"]),
    ],
)
def test_source_metadata_pii_is_not_publishable(field, value):
    from services.agent.tools import safe_document

    document = LocalRetriever().get("SYN-AML-001")
    assert not safe_document(document.model_copy(update={field: value}))
