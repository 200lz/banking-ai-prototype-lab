"""Small-corpus lexical retrieval with classification/version filtering.

No embeddings, network calls, or inference. Synonym expansion helps the fixed
domain vocabulary; relevance and access control remain separate concerns.
"""

import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path

from packages.retrieval.models import CLASSIFICATION_RANK, Document, SearchHit

ROOT = Path(__file__).resolve().parents[2]
STOPWORDS = frozenset(
    "a an the is are was be can could should do does how what when for to of in and or i we our on it with please tell me about employee customer policy policies bank synthetic".split()
)
EXPANSIONS = {
    "kyc": "onboarding identity verification",
    "onboard": "onboarding identity",
    "account": "onboarding",
    "open": "onboarding",
    "identity": "onboarding verification",
    "suspicious": "aml suspicious escalation",
    "laundering": "aml",
    "sanctions": "aml",
    "loan": "credit",
    "lending": "credit",
    "approve": "approval",
    "transfer": "payments",
    "wire": "payments",
    "payment": "payments",
    "personal": "privacy pii",
    "ssn": "privacy pii",
    "email": "privacy pii",
    "complaint": "complaints",
    "retention": "retention archive",
    "retain": "retention",
    "fdic": "deposit_insurance insurance",
    "insured": "deposit_insurance insurance",
    "deposit": "deposit_insurance insurance",
    "coverage": "deposit_insurance insurance",
    "calculate": "calculation",
    "interest": "calculation",
    "ratio": "calculation",
    "dti": "calculation credit",
    "income": "calculation",
    "sum": "calculation",
    "ai": "ai_safety",
    "agent": "ai_safety",
    "conflict": "conflicts",
    "beneficial": "onboarding ownership",
    "cdd": "onboarding ownership",
}


def tokenize(value: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9_]+", value.lower()) if t not in STOPWORDS]


class LocalRetriever:
    def __init__(self, documents: list[Document] | None = None) -> None:
        if documents is None:
            documents = []
            for path in [
                ROOT / "data/synthetic/policies.json",
                ROOT / "data/public/documents.json",
            ]:
                documents.extend(
                    Document.model_validate(d) for d in json.loads(path.read_text(encoding="utf-8"))
                )
        if len({d.id for d in documents}) != len(documents):
            raise ValueError("Duplicate corpus document IDs")
        self.documents = tuple(documents)
        self._by_id = {d.id: d for d in documents}

    def _accessible(self, max_classification: str) -> list[Document]:
        if max_classification not in CLASSIFICATION_RANK:
            raise ValueError("Unknown data classification")
        candidates = [
            d
            for d in self.documents
            if d.effective_date <= date.today()
            and CLASSIFICATION_RANK[d.classification] <= CLASSIFICATION_RANK[max_classification]
        ]
        superseded = {doc_id for d in candidates for doc_id in d.supersedes}
        return [d for d in candidates if d.id not in superseded]

    def get(self, document_id: str, *, max_classification: str = "internal") -> Document | None:
        return next((d for d in self._accessible(max_classification) if d.id == document_id), None)

    def search(
        self, query: str, *, top_k: int = 5, max_classification: str = "internal"
    ) -> list[SearchHit]:
        if not 1 <= top_k <= 10:
            raise ValueError("top_k must be between 1 and 10")
        if not 1 <= len(query.strip()) <= 4000:
            raise ValueError("Query must contain 1..4000 characters")
        docs = self._accessible(max_classification)
        raw = tokenize(query)
        terms = set(raw)
        for term in raw:
            terms.update(tokenize(EXPANSIONS.get(term, "")))
        if not terms or not docs:
            return []
        tokens = {d.id: tokenize(f"{d.title} {d.topic} {' '.join(d.tags)} {d.text}") for d in docs}
        avg_length = sum(map(len, tokens.values())) / len(docs)
        df = Counter(t for ts in tokens.values() for t in set(ts))
        hits = []
        for doc in docs:
            tf = Counter(tokens[doc.id])
            score = 0.0
            for term in terms:
                frequency = tf[term]
                if frequency:
                    idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
                    score += (
                        idf
                        * frequency
                        * 2.2
                        / (frequency + 1.2 * (0.25 + 0.75 * len(tokens[doc.id]) / avg_length))
                    )
            if score > 0:
                hits.append(SearchHit(document=doc, score=round(score, 6)))
        return sorted(hits, key=lambda h: (-h.score, h.document.id))[:top_k]
