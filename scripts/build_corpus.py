"""Build the integrity manifest uploaded by the separate deployment identity."""

import argparse
import hashlib
import json
from pathlib import Path

from packages.retrieval.local import LocalRetriever


def build(output: Path, prefix: str = "corpus/") -> None:
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    for doc in LocalRetriever().documents:
        name = doc.id + ".json"
        payload = doc.model_dump_json(indent=2).encode()
        (output / name).write_bytes(payload)
        entries.append({"key": prefix + name, "sha256": hashlib.sha256(payload).hexdigest()})
    (output / "manifest.json").write_text(
        json.dumps({"version": 1, "documents": entries}, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".runtime/corpus"))
    parser.add_argument("--prefix", default="corpus/")
    args = parser.parse_args()
    build(args.output, args.prefix)
