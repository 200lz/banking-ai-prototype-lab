# Evaluation assets

`cases.jsonl` is a versioned, authored synthetic regression set. Expected policy
facts are written separately from runtime logic. Fixture documents are injected
through the retriever contract in tests only; the API has no document-injection
input. No real customer records appear here.

This is a development set, not a statistically representative held-out benchmark.
Paraphrases within topic families are correlated. Score definitions and gates
live in EVALUATION.md. Do not describe local baseline results as LLM accuracy.

Run `make eval` or `.venv/Scripts/python scripts/tasks.py eval` on Windows.
