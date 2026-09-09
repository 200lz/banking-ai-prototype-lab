"""Offline-synthesizable AWS boundary for the synthetic policy assistant."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    IgnoreMode,
    RemovalPolicy,
    SecretValue,
    Size,
    Stack,
    Tags,
)
from aws_cdk import (
    aws_amplify as amplify,
)
from aws_cdk import (
    aws_apigatewayv2 as apigateway,
)
from aws_cdk import (
    aws_apigatewayv2_authorizers as authorizers,
)
from aws_cdk import (
    aws_apigatewayv2_integrations as integrations,
)
from aws_cdk import (
    aws_budgets as budgets,
)
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
)
from aws_cdk import (
    aws_cognito as cognito,
)
from aws_cdk import (
    aws_dynamodb as dynamodb,
)
from aws_cdk import (
    aws_ecr_assets as ecr_assets,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk import (
    aws_s3 as s3,
)
from constructs import Construct

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATTERN = re.compile(r"^[a-z0-9]+\.[a-z0-9][a-z0-9.:-]{1,150}$")


@dataclass(frozen=True)
class DeploymentConfig:
    """Reviewed context values; credentials never belong in CDK context."""

    model_id: str = "amazon.nova-lite-v1:0"
    input_usd_per_million: str = "0.06"
    output_usd_per_million: str = "0.24"
    web_repository: str | None = None
    github_token_secret_name: str | None = None
    web_branch: str = "main"
    web_origin: str | None = None
    alert_email: str | None = None
    monthly_budget_usd: int = 25
    otlp_endpoint: str | None = None

    def __post_init__(self) -> None:
        if not MODEL_PATTERN.fullmatch(self.model_id) or self.model_id.startswith(
            ("us.", "eu.", "apac.", "global.")
        ):
            raise ValueError("model_id must be a regional foundation model ID, without wildcard")
        for rate in (self.input_usd_per_million, self.output_usd_per_million):
            if not re.fullmatch(r"\d+(?:\.\d{1,8})?", rate) or not 0 < float(rate) <= 1000:
                raise ValueError("model token rates must be explicit positive USD estimates")
        if bool(self.web_repository) != bool(self.github_token_secret_name):
            raise ValueError("web_repository and github_token_secret_name must be set together")
        if self.web_repository and not re.fullmatch(
            r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.web_repository
        ):
            raise ValueError("web_repository must be an HTTPS GitHub repository URL")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", self.web_branch):
            raise ValueError("web_branch must be a lowercase DNS-safe branch name")
        if self.web_origin:
            parsed = urlparse(self.web_origin)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.path not in ("", "/")
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("web_origin must be an HTTPS origin without path or credentials")
        if self.otlp_endpoint:
            parsed = urlparse(self.otlp_endpoint)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.username
                or parsed.password
            ):
                raise ValueError("cloud OTLP endpoint must use HTTPS without embedded credentials")
        if self.alert_email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", self.alert_email):
            raise ValueError("alert_email must be an email address")
        if not 1 <= self.monthly_budget_usd <= 10000:
            raise ValueError("monthly_budget_usd must be between 1 and 10000")


class BankingAiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        config: DeploymentConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        config = config or DeploymentConfig()
        Tags.of(self).add("Project", "banking-ai-prototype-lab")
        Tags.of(self).add("Data", "synthetic-only")

        corpus = s3.Bucket(
            self,
            "Corpus",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    noncurrent_version_expiration=Duration.days(90),
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                )
            ],
        )
        audit = dynamodb.Table(
            self,
            "AuditAndReview",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            time_to_live_attribute="expires_at",
            removal_policy=RemovalPolicy.RETAIN,
            deletion_protection=True,
        )
        application_logs = logs.LogGroup(
            self,
            "ApplicationLogs",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.RETAIN,
        )
        environment = {
            "AGENT_MODE": "bedrock",
            "RETRIEVAL_BACKEND": "s3",
            "CORPUS_BUCKET": corpus.bucket_name,
            "CORPUS_PREFIX": "corpus/",
            "AUDIT_TABLE": audit.table_name,
            "AUDIT_RETENTION_DAYS": "90",
            "API_AUTH_MODE": "gateway",
            "BEDROCK_MODEL_ID": config.model_id,
            "BEDROCK_INPUT_USD_PER_MILLION": config.input_usd_per_million,
            "BEDROCK_OUTPUT_USD_PER_MILLION": config.output_usd_per_million,
            "OTEL_SERVICE_NAME": "banking-ai-api",
            "OTEL_TRACES_SAMPLER": "parentbased_always_on",
            # Disables Strands automatic prompt/completion telemetry capture.
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "false",
        }
        if config.otlp_endpoint:
            environment["OTEL_EXPORTER_OTLP_ENDPOINT"] = config.otlp_endpoint
        function = lambda_.DockerImageFunction(
            self,
            "AgentApi",
            code=lambda_.DockerImageCode.from_image_asset(
                str(REPOSITORY_ROOT),
                file="infra/cdk/Dockerfile.lambda",
                platform=ecr_assets.Platform.LINUX_AMD64,
                ignore_mode=IgnoreMode.DOCKER,
                exclude=[
                    ".git",
                    ".venv*",
                    ".runtime",
                    ".artifacts",
                    "docs",
                    "apps",
                    "tests",
                    "evals",
                    "**/node_modules",
                    "**/.next",
                    "**/__pycache__",
                    "**/cdk.out*",
                    "**/.pytest_cache",
                    "**/.mypy_cache",
                    "**/.ruff_cache",
                    "**/.env*",
                    ".databrickscfg",
                    "**/.databrickscfg",
                    "**/.databricks",
                    ".aws",
                    "**/.aws",
                    "**/*.pem",
                    "**/*.key",
                ],
            ),
            architecture=lambda_.Architecture.X86_64,
            memory_size=1024,
            timeout=Duration.seconds(28),
            reserved_concurrent_executions=3,
            ephemeral_storage_size=Size.mebibytes(512),
            environment=environment,
            log_group=application_logs,
            tracing=lambda_.Tracing.ACTIVE,
        )
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"], resources=[corpus.arn_for_objects("corpus/*")]
            )
        )
        function.add_to_role_policy(
            iam.PolicyStatement(actions=["dynamodb:PutItem"], resources=[audit.table_arn])
        )
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                resources=[
                    f"arn:{Aws.PARTITION}:bedrock:{Aws.REGION}::foundation-model/{config.model_id}"
                ],
            )
        )

        user_pool = cognito.UserPool(
            self,
            "Employees",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=14,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
                require_symbols=True,
            ),
            mfa=cognito.Mfa.REQUIRED,
            mfa_second_factor=cognito.MfaSecondFactor(otp=True, sms=False),
            account_recovery=cognito.AccountRecovery.NONE,
            removal_policy=RemovalPolicy.RETAIN,
        )
        query_scope = cognito.ResourceServerScope(
            scope_name="query", scope_description="Read synthetic evidence and query the assistant"
        )
        resource_server = user_pool.add_resource_server(
            "AssistantScope", identifier="banking-ai", scopes=[query_scope]
        )
        domain = user_pool.add_domain(
            "SignIn",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"bailab-{Aws.ACCOUNT_ID}-{Aws.REGION}-{self.node.addr[-8:]}"
            ),
        )

        # App depends on no client token; branch receives auth configuration later,
        # preventing an Amplify-domain -> Cognito-client -> Amplify cycle.
        amplify_role = iam.Role(
            self, "WebHostingRole", assumed_by=iam.ServicePrincipal("amplify.amazonaws.com")
        )
        amplify_role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=[
                    f"arn:{Aws.PARTITION}:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:/aws/amplify/*"
                ],
            )
        )
        # DescribeLogGroups does not support resource-level IAM restrictions.
        amplify_role.add_to_policy(
            iam.PolicyStatement(actions=["logs:DescribeLogGroups"], resources=["*"])
        )
        web = amplify.CfnApp(
            self,
            "Web",
            name="banking-ai-prototype-lab",
            platform="WEB_COMPUTE",
            repository=config.web_repository,
            access_token=(
                SecretValue.secrets_manager(config.github_token_secret_name).unsafe_unwrap()
                if config.github_token_secret_name
                else None
            ),
            iam_service_role=amplify_role.role_arn,
            build_spec=(Path(__file__).parent / "amplify-build.yml").read_text(encoding="utf-8"),
            environment_variables=[
                amplify.CfnApp.EnvironmentVariableProperty(
                    name="AMPLIFY_MONOREPO_APP_ROOT", value="apps/web"
                )
            ],
        )
        web_origin = (
            config.web_origin.rstrip("/")
            if config.web_origin
            else f"https://{config.web_branch}.{web.attr_default_domain}"
        )
        web_logs = logs.LogGroup(
            self,
            "WebRuntimeLogs",
            log_group_name=f"/aws/amplify/{web.attr_app_id}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.RETAIN,
        )
        client = user_pool.add_client(
            "Browser",
            generate_secret=False,
            prevent_user_existence_errors=True,
            enable_token_revocation=True,
            access_token_validity=Duration.minutes(15),
            id_token_validity=Duration.minutes(15),
            refresh_token_validity=Duration.hours(8),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.resource_server(resource_server, query_scope),
                ],
                callback_urls=[f"{web_origin}/api/auth/callback"],
                logout_urls=[web_origin],
            ),
        )
        authorizer = authorizers.HttpJwtAuthorizer(
            "EmployeeAccessToken",
            jwt_issuer=user_pool.user_pool_provider_url,
            jwt_audience=[client.user_pool_client_id],
        )
        api = apigateway.HttpApi(
            self,
            "Api",
            create_default_stage=False,
            default_authorizer=authorizer,
            default_authorization_scopes=["banking-ai/query"],
        )
        integration = integrations.HttpLambdaIntegration("ControlledWorkflow", function)
        for path, method in (
            ("/health", apigateway.HttpMethod.GET),
            ("/v1/config", apigateway.HttpMethod.GET),
            ("/v1/query", apigateway.HttpMethod.POST),
            ("/v1/documents/{id}", apigateway.HttpMethod.GET),
        ):
            api.add_routes(path=path, methods=[method], integration=integration)
        access_logs = logs.LogGroup(
            self,
            "ApiAccessLogs",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.RETAIN,
        )
        apigateway.CfnStage(
            self,
            "ApiStage",
            api_id=api.api_id,
            stage_name="$default",
            auto_deploy=True,
            default_route_settings=apigateway.CfnStage.RouteSettingsProperty(
                throttling_burst_limit=5, throttling_rate_limit=2, detailed_metrics_enabled=True
            ),
            access_log_settings=apigateway.CfnStage.AccessLogSettingsProperty(
                destination_arn=access_logs.log_group_arn,
                # No request body, query string, Authorization header, or subject.
                format=json.dumps(
                    {
                        "requestId": "$context.requestId",
                        "route": "$context.routeKey",
                        "status": "$context.status",
                        "latencyMs": "$context.responseLatency",
                        "integrationStatus": "$context.integrationStatus",
                    }
                ),
            ),
        )
        web_env = {
            "WEB_AUTH_MODE": "cognito",
            "API_BASE_URL": api.api_endpoint,
            "COGNITO_DOMAIN": domain.base_url(),
            "COGNITO_CLIENT_ID": client.user_pool_client_id,
            "APP_BASE_URL": web_origin,
        }
        web_branch = amplify.CfnBranch(
            self,
            "WebBranch",
            app_id=web.attr_app_id,
            branch_name=config.web_branch,
            framework="Next.js - SSR",
            stage="PRODUCTION",
            enable_auto_build=bool(config.web_repository),
            environment_variables=[
                amplify.CfnBranch.EnvironmentVariableProperty(name=name, value=value)
                for name, value in web_env.items()
            ],
        )
        web_branch.node.add_dependency(web_logs)

        errors = function.metric_errors(period=Duration.minutes(5), statistic="Sum")
        duration = function.metric_duration(period=Duration.minutes(5), statistic="p95")
        cloudwatch.Alarm(self, "LambdaErrorAlarm", metric=errors, threshold=3, evaluation_periods=1)
        cloudwatch.Alarm(
            self, "LambdaLatencyAlarm", metric=duration, threshold=20000, evaluation_periods=2
        )
        cloudwatch.Alarm(
            self,
            "LambdaThrottleAlarm",
            metric=function.metric_throttles(period=Duration.minutes(5), statistic="Sum"),
            threshold=1,
            evaluation_periods=1,
        )
        dashboard = cloudwatch.Dashboard(self, "Operations")
        dashboard.add_widgets(
            cloudwatch.GraphWidget(title="API Lambda latency (p95 ms)", left=[duration]),
            cloudwatch.GraphWidget(title="Lambda invocation errors", left=[errors]),
            cloudwatch.LogQueryWidget(
                title="Redacted application audit and OpenTelemetry stage records",
                log_group_names=[application_logs.log_group_name],
                query_lines=["fields @timestamp, @message", "sort @timestamp desc", "limit 30"],
            ),
        )
        if config.alert_email:
            budgets.CfnBudget(
                self,
                "MonthlyBudget",
                budget=budgets.CfnBudget.BudgetDataProperty(
                    budget_type="COST",
                    time_unit="MONTHLY",
                    budget_limit=budgets.CfnBudget.SpendProperty(
                        amount=config.monthly_budget_usd, unit="USD"
                    ),
                    # Account-wide costs: intentionally useful without activating cost tags.
                ),
                notifications_with_subscribers=[
                    budgets.CfnBudget.NotificationWithSubscribersProperty(
                        notification=budgets.CfnBudget.NotificationProperty(
                            comparison_operator="GREATER_THAN",
                            notification_type="ACTUAL",
                            threshold=80,
                            threshold_type="PERCENTAGE",
                        ),
                        subscribers=[
                            budgets.CfnBudget.SubscriberProperty(
                                address=config.alert_email, subscription_type="EMAIL"
                            )
                        ],
                    )
                ],
            )

        for name, value in {
            "ApiUrl": api.api_endpoint,
            "CorpusBucket": corpus.bucket_name,
            "AuditTable": audit.table_name,
            "UserPoolId": user_pool.user_pool_id,
            "UserPoolClientId": client.user_pool_client_id,
            "CognitoDomain": domain.base_url(),
            "WebUrl": web_origin,
            "AmplifyAppId": web.attr_app_id,
            "CloudWatchDashboard": dashboard.dashboard_name,
            "DeploymentStatus": "Infrastructure definition only; verify build, corpus ingestion, auth and Bedrock after deployment",
        }.items():
            CfnOutput(self, name, value=value)
