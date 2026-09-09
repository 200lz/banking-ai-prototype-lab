"""Security assertions against the actual synthesized CloudFormation template."""

import json
from pathlib import Path

import pytest
from aws_cdk import App, Environment
from aws_cdk.assertions import Match, Template

from infra.cdk import stack as stack_module
from infra.cdk.stack import BankingAiStack, DeploymentConfig


@pytest.fixture(scope="module")
def template(tmp_path_factory: pytest.TempPathFactory) -> Template:
    app = App(outdir=str(tmp_path_factory.mktemp("cdk")))
    stack = BankingAiStack(
        app, "TestLab", env=Environment(account="111111111111", region="us-east-1")
    )
    result = Template.from_stack(stack)
    app.synth()
    return result


def test_corpus_is_private_encrypted_versioned_and_retained(template: Template) -> None:
    template.has_resource(
        "AWS::S3::Bucket",
        {
            "DeletionPolicy": "Retain",
            "Properties": {
                "BucketEncryption": {
                    "ServerSideEncryptionConfiguration": [
                        {"ServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
                    ]
                },
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True,
                },
                "VersioningConfiguration": {"Status": "Enabled"},
            },
        },
    )
    template.has_resource_properties(
        "AWS::S3::BucketPolicy",
        {
            "PolicyDocument": {
                "Statement": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "Effect": "Deny",
                                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
                            }
                        )
                    ]
                )
            }
        },
    )


def test_audit_has_recovery_and_expiry(template: Template) -> None:
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "BillingMode": "PAY_PER_REQUEST",
            "SSESpecification": {"SSEEnabled": True},
            "PointInTimeRecoverySpecification": {"PointInTimeRecoveryEnabled": True},
            "TimeToLiveSpecification": {"AttributeName": "expires_at", "Enabled": True},
            "DeletionProtectionEnabled": True,
        },
    )


def test_all_api_routes_require_access_token_scope(template: Template) -> None:
    routes = template.find_resources("AWS::ApiGatewayV2::Route")
    assert len(routes) == 4
    assert {r["Properties"]["RouteKey"] for r in routes.values()} == {
        "GET /health",
        "GET /v1/config",
        "POST /v1/query",
        "GET /v1/documents/{id}",
    }
    for route in routes.values():
        props = route["Properties"]
        assert props["AuthorizationType"] == "JWT"
        assert props["AuthorizationScopes"] == ["banking-ai/query"]
        assert "AuthorizerId" in props
    template.resource_count_is("AWS::Lambda::Url", 0)
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Authorizer",
        {"AuthorizerType": "JWT", "IdentitySource": ["$request.header.Authorization"]},
    )


def test_runtime_has_no_mutation_or_model_wildcard(template: Template) -> None:
    policies = template.find_resources("AWS::IAM::Policy")
    statements = [
        s for p in policies.values() for s in p["Properties"]["PolicyDocument"]["Statement"]
    ]
    actions = [
        a
        for s in statements
        for a in (s["Action"] if isinstance(s["Action"], list) else [s["Action"]])
    ]
    assert not {
        "s3:PutObject",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "bedrock:*",
        "lambda:InvokeFunction",
        "*",
    }.intersection(actions)
    assert "dynamodb:PutItem" in actions
    bedrock = [s for s in statements if "bedrock:InvokeModel" in s["Action"]]
    assert len(bedrock) == 1
    assert "foundation-model/amazon.nova-lite-v1:0" in json.dumps(bedrock)
    assert "*" not in json.dumps(bedrock)
    assert "s3:ListBucket" not in actions  # Manifest-based retrieval needs no enumeration.
    reads = [s for s in statements if s["Action"] == "s3:GetObject"]
    assert len(reads) == 1 and "corpus/*" in json.dumps(reads[0]["Resource"])


def test_identity_enforces_mfa_and_has_no_public_signup(template: Template) -> None:
    template.has_resource_properties(
        "AWS::Cognito::UserPool",
        {
            "AdminCreateUserConfig": {"AllowAdminCreateUserOnly": True},
            "MfaConfiguration": "ON",
            "EnabledMfas": ["SOFTWARE_TOKEN_MFA"],
        },
    )
    template.has_resource_properties(
        "AWS::Cognito::UserPoolClient",
        {
            "GenerateSecret": False,
            "AllowedOAuthFlows": ["code"],
            "AllowedOAuthScopes": Match.array_with(["openid"]),
            "AccessTokenValidity": 15,
        },
    )
    resource_servers = template.find_resources("AWS::Cognito::UserPoolResourceServer")
    resource_id, resource = next(iter(resource_servers.items()))
    assert resource["Properties"]["Identifier"] == "banking-ai"
    assert resource["Properties"]["Scopes"][0]["ScopeName"] == "query"
    client = next(iter(template.find_resources("AWS::Cognito::UserPoolClient").values()))
    assert {"Fn::Join": ["", [{"Ref": resource_id}, "/query"]]} in client["Properties"][
        "AllowedOAuthScopes"
    ]


def test_lambda_and_api_bound_cost_and_latency(template: Template) -> None:
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "PackageType": "Image",
            "Timeout": 28,
            "MemorySize": 1024,
            "ReservedConcurrentExecutions": 3,
            "TracingConfig": {"Mode": "Active"},
            "Environment": {
                "Variables": Match.object_like(
                    {
                        "AGENT_MODE": "bedrock",
                        "API_AUTH_MODE": "gateway",
                        "RETRIEVAL_BACKEND": "s3",
                        "CORPUS_PREFIX": "corpus/",
                        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "false",
                    }
                )
            },
        },
    )
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Stage",
        {
            "DefaultRouteSettings": {
                "ThrottlingBurstLimit": 5,
                "ThrottlingRateLimit": 2,
                "DetailedMetricsEnabled": True,
            }
        },
    )
    template.resource_count_is("AWS::CloudWatch::Alarm", 3)
    template.resource_count_is("AWS::CloudWatch::Dashboard", 1)


def test_access_log_does_not_capture_question_or_credentials(template: Template) -> None:
    stages = template.find_resources("AWS::ApiGatewayV2::Stage")
    fmt = next(iter(stages.values()))["Properties"]["AccessLogSettings"]["Format"]
    assert set(json.loads(fmt)) == {
        "requestId",
        "route",
        "status",
        "latencyMs",
        "integrationStatus",
    }
    for log in template.find_resources("AWS::Logs::LogGroup").values():
        assert log["Properties"]["RetentionInDays"] == 30


def test_web_uses_cognito_server_configuration(template: Template) -> None:
    template.has_resource_properties("AWS::Amplify::App", {"Platform": "WEB_COMPUTE"})
    branch = next(iter(template.find_resources("AWS::Amplify::Branch").values()))["Properties"]
    env = {p["Name"]: p["Value"] for p in branch["EnvironmentVariables"]}
    assert env["WEB_AUTH_MODE"] == "cognito"
    assert set(env) == {
        "WEB_AUTH_MODE",
        "API_BASE_URL",
        "COGNITO_DOMAIN",
        "COGNITO_CLIENT_ID",
        "APP_BASE_URL",
    }
    assert "TOKEN" not in json.dumps(env)
    assert not branch["EnableAutoBuild"]  # Repository connection has not been configured.


def test_config_rejects_wildcards_profiles_and_insecure_callbacks() -> None:
    for model in ("*", "amazon.*", "us.amazon.nova-lite-v1:0", "arn:aws:bedrock:*:*:*"):
        with pytest.raises(ValueError):
            DeploymentConfig(model_id=model)
    for origin in (
        "http://example.com",
        "https://user:pass@example.com",
        "https://example.com/callback",
    ):
        with pytest.raises(ValueError):
            DeploymentConfig(web_origin=origin)
    with pytest.raises(ValueError):
        DeploymentConfig(web_repository="https://github.com/example/repo")
    with pytest.raises(ValueError):
        DeploymentConfig(otlp_endpoint="http://collector:4318")
    with pytest.raises(ValueError):
        DeploymentConfig(input_usd_per_million="0")


def test_optional_git_connection_and_budget(tmp_path: Path) -> None:
    app = App(outdir=str(tmp_path))
    stack = BankingAiStack(
        app,
        "ConfiguredLab",
        config=DeploymentConfig(
            web_repository="https://github.com/example/banking-ai-prototype-lab",
            github_token_secret_name="portfolio/amplify-github",
            alert_email="operator@example.test",
        ),
        env=Environment(account="111111111111", region="us-east-1"),
    )
    template = Template.from_stack(stack)
    template.has_resource_properties("AWS::Amplify::Branch", {"EnableAutoBuild": True})
    app_props = next(iter(template.find_resources("AWS::Amplify::App").values()))["Properties"]
    assert "resolve:secretsmanager:" in json.dumps(app_props["AccessToken"])
    template.has_resource_properties(
        "AWS::Budgets::Budget",
        {
            "Budget": {
                "BudgetLimit": {"Amount": 25, "Unit": "USD"},
                "BudgetType": "COST",
                "TimeUnit": "MONTHLY",
            }
        },
    )
    app.synth()


def test_docker_asset_excludes_runtime_audits_and_secrets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = tmp_path / "repository"
    dockerfile = repository / "infra/cdk/Dockerfile.lambda"
    dockerfile.parent.mkdir(parents=True)
    dockerfile.write_text("FROM scratch\n", encoding="utf-8")
    for name in (
        ".runtime/audit.json",
        ".artifacts/trace.json",
        ".env.production",
        "docs/private.md",
    ):
        path = repository / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("SENSITIVE_SENTINEL", encoding="utf-8")
    monkeypatch.setattr(stack_module, "REPOSITORY_ROOT", repository)
    outdir = tmp_path / "assembly"
    app = App(outdir=str(outdir))
    BankingAiStack(
        app, "AssetBoundary", env=Environment(account="111111111111", region="us-east-1")
    )
    app.synth()
    assets = json.loads((outdir / "AssetBoundary.assets.json").read_text(encoding="utf-8"))
    source = next(iter(assets["dockerImages"].values()))["source"]
    staged = outdir / source["directory"]
    staged_names = {
        path.relative_to(staged).as_posix() for path in staged.rglob("*") if path.is_file()
    }
    assert staged_names == {"infra/cdk/Dockerfile.lambda"}
