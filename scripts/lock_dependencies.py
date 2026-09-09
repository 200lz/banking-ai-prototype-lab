"""Record exact tested versions; regenerate only in a reviewed dependency update."""

import importlib.metadata as metadata
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]


def runtime_dependencies(requirements: list[str]) -> set[str]:
    """Preserve transitive extras such as PyJWT[crypto] in the pinned closure."""
    pending = [Requirement(raw) for raw in requirements]
    runtime: set[str] = set()
    processed: dict[str, set[str]] = {}
    while pending:
        requirement = pending.pop()
        name = canonicalize_name(requirement.name)
        active_extras = ({""} | set(requirement.extras)) - processed.get(name, set())
        if not active_extras:
            continue
        processed.setdefault(name, set()).update(active_extras)
        runtime.add(name)
        for raw in metadata.requires(name) or []:
            req = Requirement(raw)
            if req.marker is None or any(
                req.marker.evaluate({"extra": extra}) for extra in active_extras
            ):
                pending.append(req)
    return runtime


def lock() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    runtime = runtime_dependencies(project["project"]["dependencies"])
    all_names: set[str] = {
        str(canonicalize_name(d.metadata["Name"])) for d in metadata.distributions()
    }
    all_names -= {"banking-ai-prototype-lab", "pip", "setuptools", "wheel"}
    for filename, names in [
        ("requirements.lock", all_names),
        ("requirements-runtime.lock", runtime),
    ]:
        lines = [
            "# Exact tested dependency versions. Regenerate with scripts/lock_dependencies.py.",
            "# Python 3.11; Windows-only dependency has an explicit platform marker.",
        ]
        for locked_name in sorted(names):
            marker = '; sys_platform == "win32"' if locked_name == "pywin32" else ""
            lines.append(f"{locked_name}=={metadata.version(locked_name)}{marker}")
        (ROOT / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    lock()
