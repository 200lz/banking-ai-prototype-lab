"""Scan the Git candidate files, excluding ignored dependencies and local secrets."""

import argparse
import shutil
import subprocess  # nosec B404 - developer-only fixed commands
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scan(executable: str) -> int:
    scanner = shutil.which(executable)
    git = shutil.which("git")
    if scanner is None or git is None:
        raise SystemExit("Install Gitleaks 8.30.1 and Git, or provide --gitleaks PATH.")
    result = subprocess.run(  # nosec B603
        [git, "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
    with tempfile.TemporaryDirectory(prefix="banking-ai-secret-scan-") as temporary:
        destination = Path(temporary)
        for name in paths:
            source = ROOT / name
            if not source.exists():
                continue
            if source.is_symlink() or not source.resolve().is_relative_to(ROOT):
                raise SystemExit("Refusing to scan a candidate outside the repository.")
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        completed = subprocess.run(  # nosec B603
            [scanner, "dir", str(destination), "--redact=100", "--no-banner"],
            check=False,
        )
    print(f"Secret scan examined {len(paths)} Git candidate paths; exit={completed.returncode}.")
    return completed.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gitleaks", default="gitleaks")
    raise SystemExit(scan(parser.parse_args().gitleaks))


if __name__ == "__main__":
    main()
