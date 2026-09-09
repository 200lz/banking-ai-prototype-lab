"""Strict public contracts. Requests cannot supply roles, tools, or approvals."""

from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from packages.financial.models import CompanyId, FinancialProfile


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Calculation(StrictModel):
    operation: Literal["debt_to_income", "simple_interest", "sum"]
    operands: list[Decimal] = Field(min_length=1, max_length=20)

    @field_validator("operands", mode="before")
    @classmethod
    def exact_operand_types(cls, values: Any) -> Any:
        if not isinstance(values, list):
            raise ValueError("Operands must be a JSON array")
        if any(isinstance(value, (float, bool)) for value in values):
            raise ValueError("Supply exact quantities as decimal strings or integers")
        return values

    @field_validator("operands")
    @classmethod
    def bounded_operands(cls, values: list[Decimal]) -> list[Decimal]:
        for value in values:
            if not value.is_finite() or abs(value) > Decimal("1000000000000"):
                raise ValueError("Operands must be finite and at most 10^12 in magnitude")
            exponent = value.as_tuple().exponent
            if isinstance(exponent, int) and not -8 <= exponent <= 12:
                raise ValueError("Operands support exponents from -8 through 12")
        return values

    @model_validator(mode="after")
    def validate_operation(self) -> "Calculation":
        if self.operation == "debt_to_income":
            if len(self.operands) != 2 or self.operands[0] < 0 or self.operands[1] <= 0:
                raise ValueError("DTI requires nonnegative debt and positive income")
        if self.operation == "simple_interest":
            if len(self.operands) != 3 or any(x < 0 for x in self.operands):
                raise ValueError("Interest requires nonnegative principal, rate, and days")
            if self.operands[1] > 100 or self.operands[2] > 36500:
                raise ValueError("Interest rate must be <=100 percent; days <=36500")
        return self


class AgentRequest(StrictModel):
    question: str = Field(min_length=1, max_length=4000, strict=True)
    calculation: Calculation | None = None
    company_id: CompanyId | None = None

    @field_validator("question")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question must contain text")
        return value.strip()


class Evidence(StrictModel):
    id: str
    document_id: str
    claim: str
    quote: str
    source_hash: str


class Citation(StrictModel):
    evidence_id: str
    document_id: str
    title: str
    source_url: str | None
    version: str
    verified: bool


class StepTrace(StrictModel):
    stage: str
    duration_ms: float
    status: str


class ToolInvocation(StrictModel):
    name: str
    duration_ms: float
    status: str


class Metrics(StrictModel):
    latency_ms: float = Field(default=0, ge=0, allow_inf_nan=False)
    model_latency_ms: float = Field(default=0, ge=0, allow_inf_nan=False)
    retrieval_latency_ms: float = Field(default=0, ge=0, allow_inf_nan=False)
    input_tokens: int = Field(default=0, ge=0, strict=True)
    output_tokens: int = Field(default=0, ge=0, strict=True)
    estimated_cost_usd: float = Field(default=0, ge=0, allow_inf_nan=False)
    cost_estimate_complete: bool = Field(default=True, strict=True)


class CalculationResult(StrictModel):
    operation: str
    operands: list[str]
    value: str
    unit: str
    formula: str
    rounding: str = "ROUND_HALF_UP to 2 decimal places"


class AgentResponse(StrictModel):
    request_id: str
    answer: str
    evidence: list[Evidence]
    citations: list[Citation]
    assumptions: list[str]
    missing_information: list[str]
    confidence: float = Field(ge=0, le=1)
    risk_flags: list[str]
    human_review_required: bool
    mode: Literal["local", "bedrock"]
    trace: list[StepTrace]
    tool_invocations: list[ToolInvocation]
    metrics: Metrics
    calculation: CalculationResult | None = None
    financial_profile: FinancialProfile | None = None
    retrieved_document_ids: list[str] = Field(default_factory=list)
    disclaimer: str = "Synthetic demonstration only. No affiliation with any real bank."


class Plan(StrictModel):
    """Model selects bounded evidence IDs; it cannot author claims or tool arguments."""

    evidence_ids: list[Annotated[str, Field(min_length=1, max_length=100, strict=True)]] = Field(
        default_factory=list, max_length=12
    )
    calculate: bool = Field(default=False, strict=True)
    human_review_required: bool = Field(default=False, strict=True)
    abstain: bool = Field(default=False, strict=True)
