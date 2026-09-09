"""Cross-platform equivalents for every Make target; never imported by the agent."""

import argparse
import os
import re
import shutil

# Developer-only process runner; the runtime agent cannot import or select this CLI.
import subprocess  # nosec B404
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(*arguments: str, cwd: Path = ROOT) -> None:
    command = list(arguments)
    executable = shutil.which(command[0])
    if executable:
        command[0] = executable
    # Fixed developer commands, shell=False; never called with runtime agent inputs.
    subprocess.run(command, cwd=cwd, check=True)  # nosec B603


def python(*arguments: str) -> None:
    run(str(VENV_PYTHON), *arguments)


def npm(*arguments: str) -> None:
    run("npm", *arguments, cwd=ROOT / "apps/web")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        choices=[
            "setup",
            "test",
            "eval",
            "demo",
            "deploy",
            "check",
            "format",
            "lint",
            "typecheck",
            "security",
            "api",
            "web",
            "up",
            "down",
            "synth",
            "container-smoke",
            "aws-smoke",
            "live-eval",
            "financial-pipeline",
            "financial-smoke",
        ],
    )
    target = parser.parse_args().target
    if target == "setup":
        if not VENV_PYTHON.exists():
            run(sys.executable, "-m", "venv", str(ROOT / ".venv"))
        python("-m", "pip", "install", "-r", "requirements.lock")
        python("-m", "pip", "install", "--no-deps", "-e", ".")
        npm("ci")
        run("npm", "ci", cwd=ROOT / "infra/cdk")
        return
    if not VENV_PYTHON.exists():
        parser.error("Run setup first to create .venv")
    if target in {"lint", "check"}:
        python(
            "-m",
            "ruff",
            "format",
            "--check",
            "services",
            "packages",
            "tests",
            "scripts",
            "infra/cdk",
            "databricks",
        )
        python(
            "-m",
            "ruff",
            "check",
            "services",
            "packages",
            "tests",
            "scripts",
            "infra/cdk",
            "databricks",
        )
        npm("run", "lint")
        npm("run", "format:check")
    if target == "format":
        python(
            "-m",
            "ruff",
            "format",
            "services",
            "packages",
            "tests",
            "scripts",
            "infra/cdk",
            "databricks",
        )
        npm("run", "format")
    if target in {"typecheck", "check"}:
        python("-m", "mypy", "services", "packages", "scripts", "infra/cdk", "databricks")
        npm("run", "typecheck")
    if target in {"test", "check"}:
        python("-m", "pytest", "tests", "infra/cdk/tests", "-q")
        npm("test")
    if target == "eval":
        python("-m", "packages.evals.run")
    if target == "demo":
        python("scripts/demo.py")
    if target in {"security", "check"}:
        python(
            "-m",
            "bandit",
            "-r",
            "services",
            "packages",
            "infra/cdk",
            "databricks",
            "-x",
            "infra/cdk/tests,infra/cdk/cdk.out,infra/cdk/node_modules",
            "-ll",
        )
        python("-m", "pip_audit", "-r", "requirements.lock", "--no-deps", "--disable-pip")
        npm("audit", "--audit-level=moderate")
        run("npm", "audit", "--audit-level=moderate", cwd=ROOT / "infra/cdk")
    if target == "api":
        python(
            "-m",
            "uvicorn",
            "services.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        )
    if target == "web":
        npm("run", "dev", "--", "--hostname", "127.0.0.1")
    if target == "up":
        run("docker", "compose", "up", "--build", "-d")
    if target == "down":
        run("docker", "compose", "down")
    if target == "synth":
        python("-m", "infra.cdk.app")
    if target == "container-smoke":
        python("scripts/verify_containers.py")
    if target == "aws-smoke":
        python("scripts/aws_smoke.py")
    if target == "live-eval":
        python("scripts/live_bedrock_eval.py")
    if target == "financial-pipeline":
        python("-m", "packages.financial.pipeline")
    if target == "financial-smoke":
        python("databricks/verify_profile.py", "--backend", "local")
    if target == "deploy":
        account = os.environ.get("CDK_DEFAULT_ACCOUNT", "")
        region = os.environ.get("CDK_DEFAULT_REGION", "")
        if (
            len(account) != 12
            or not account.isdigit()
            or account == "111111111111"
            or not re.fullmatch(r"[a-z]{2}(?:-[a-z]+)+-\d", region)
        ):
            parser.error(
                "Deployment requires a real CDK_DEFAULT_ACCOUNT and CDK_DEFAULT_REGION. See docs/cloud-deployment.md; synth is safe without credentials."
            )
        cli_path = ROOT / "infra/cdk/node_modules/aws-cdk/bin/cdk"
        if not cli_path.is_file():
            parser.error("Run setup first to install the pinned CDK CLI")
        python("scripts/build_corpus.py")
        # CDK's IAM approval prompt remains the final concrete review before deployment.
        app_command = f'"{VENV_PYTHON}" -m infra.cdk.app'
        cli = str(cli_path)
        run("node", cli, "--app", app_command, "diff")
        run(
            "node",
            cli,
            "--app",
            app_command,
            "deploy",
            "--require-approval",
            "broadening",
            "--outputs-file",
            ".runtime/cloud-outputs.json",
        )
        python("scripts/publish_corpus.py")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        # Child commands already report their diagnostic; preserve NOT TESTED=2.
        raise SystemExit(error.returncode) from None
