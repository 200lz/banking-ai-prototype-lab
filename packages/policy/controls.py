"""Conservative examples, not a complete DLP, AML, or injection detection product."""

import re
import unicodedata
from dataclasses import dataclass, field

TOPICS: dict[str, tuple[str, ...]] = {
    "onboarding": (
        "onboard",
        "kyc",
        "identity",
        "identification",
        "open an account",
        "new account",
        "beneficial owner",
        "customer due diligence",
    ),
    "aml": (
        "aml",
        "suspicious",
        "money laundering",
        "sanction",
        "tipping off",
        "tipping-off",
        "structur",
        "sar",
    ),
    "credit": ("credit", "loan", "lending", "underwrit", "affordability"),
    "payments": ("payment", "transfer", "wire", "transaction", "beneficiary"),
    "privacy": (
        "privacy",
        "personal data",
        "personal information",
        "pii",
        "customer data",
        "customer record",
        "data breach",
        "email",
        "ssn",
        "redact",
    ),
    "complaints": ("complaint", "complain", "dissatisfied"),
    "retention": (
        "retention",
        "retain",
        "retained",
        "archive",
        "delete records",
        "recordkeeping",
        "records management",
    ),
    "deposit_insurance": ("deposit insurance", "fdic", "insured deposit", "insurance coverage"),
    "calculation": (
        "calculate",
        "calculation",
        "debt to income",
        "debt-to-income",
        "dti",
        "simple interest",
        "sum",
        "arithmetic",
    ),
    "ai_safety": (
        "agent",
        "ai safety",
        "ai assistant",
        "assistant",
        "tool allowlist",
        "prompt injection",
        "human approval",
    ),
    "conflicts": ("conflicting", "contradictory", "conflict"),
}

_PII = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[REDACTED_ACCOUNT]"),
    (
        re.compile(r"(?i)\b(account(?: number)?|customer id)\s*[:#]?\s*\d{5,12}\b"),
        "[REDACTED_ACCOUNT]",
    ),
]

_INJECTION = re.compile(
    r"ignore\s+(?:all\s+|the\s+)?(?:previous|prior|system|above)|"
    r"(?:system|developer)\s*(?:prompt|message|override)|"
    r"\b(?:system|developer|assistant)\s*:|\byou are now\b|"
    r"\[/?(?:INST|SYSTEM)\]|<\|(?:im_start|system)|"
    r"(?:execute|run)\s+(?:a\s+)?(?:shell|command|python|bash|powershell)|"
    r"(?:disable|bypass|override)\s+(?:the\s+)?(?:guardrail|safety|approval|policy|controls)|"
    r"(?:exfiltrat|reveal secrets|send secrets|tool_call|invoke_tool)",
    re.IGNORECASE,
)

_PROHIBITED = re.compile(
    r"\b(?:approve|grant|authori[sz]e|reject|deny)\b.{0,55}\b(?:credit|loan|mortgage|application)\b|"
    r"\b(?:execute|send|initiate|release|make|process)\b.{0,35}\b(?:transfer|payment|wire|transaction)\b|"
    r"\b(?:alter|update|edit|change|delete|overwrite)\b.{0,40}\b(?:customer|client|account)\b|"
    r"\b(?:bypass|skip|avoid|waive)\b.{0,35}\b(?:approval|review|verification|kyc|sanction)\b|"
    r"\b(?:binding|personalized|personalised)\b.{0,30}\b(?:investment|advice)\b|"
    r"\b(?:buy|sell|recommend)\b.{0,40}\b(?:stock|stocks|security|securities|investment|bitcoin)\b",
    re.IGNORECASE,
)

_SOURCE_AUTHORITY_ESCALATION = re.compile(
    r"\b(?:assistant|you)\s+(?:may|can|should|must|are allowed to|is allowed to)\s+"
    r"(?:approve\s+(?:all\s+)?(?:credit|loans?)|execute\s+(?:financial\s+)?(?:transactions?|payments?|transfers?)|"
    r"(?:alter|update)\s+customer\s+records?|provide\s+binding\s+investment\s+advice|"
    r"bypass\s+(?:required\s+)?(?:human\s+)?approval)",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKC", text) if unicodedata.category(c) != "Cf"
    )


def redact_pii(text: str) -> tuple[str, bool]:
    normalized = normalize(text)
    redacted = normalized
    for pattern, replacement in _PII:
        redacted = pattern.sub(replacement, redacted)
    return redacted, redacted != normalized


def is_injected(text: str) -> bool:
    normalized = normalize(text)
    return bool(_INJECTION.search(normalized) or _SOURCE_AUTHORITY_ESCALATION.search(normalized))


@dataclass
class Intent:
    topics: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    blocked: bool = False
    human_review_required: bool = False


def analyze_intent(
    question: str, has_calculation: bool = False, has_company_profile: bool = False
) -> Intent:
    text = normalize(question).lower()
    topics = [topic for topic, words in TOPICS.items() if any(word in text for word in words)]
    if has_calculation and "calculation" not in topics:
        topics.append("calculation")
    if has_company_profile and "credit" not in topics:
        topics.append("credit")
    risks: list[str] = []
    blocked = False
    if is_injected(text):
        risks.append("malicious_instruction")
        blocked = True
    if _PROHIBITED.search(text):
        risks.append("prohibited_action")
        blocked = True
    if not topics:
        risks.append("out_of_scope")
        blocked = True
    missing = []
    if (
        "calculation" in topics
        and not has_calculation
        and re.search(r"\b(?:calculate|compute|sum)\b", text)
    ):
        missing.append("Provide a typed calculation operation and numeric operands.")
    if re.search(
        r"\b(?:missing|unknown|unavailable|incomplete|not provided|not supplied|not verified|without documentation)\b",
        text,
    ):
        missing.append("Provide the missing scenario information before a case-specific decision.")
    if missing:
        risks.append("missing_information")
    review = (
        blocked
        or bool(missing)
        or bool(set(topics) & {"aml", "credit", "payments", "privacy", "conflicts"})
    )
    return Intent(topics, risks, missing, blocked, review)
