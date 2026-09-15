"""Injected service contracts only: these tests are never live AWS evidence."""

import copy
import hashlib
import io
import json
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest

from packages.retrieval.local import LocalRetriever
from scripts import aws_smoke as smoke
from services.agent.models import AgentRequest
from services.agent.observability import AuditLogger
from services.agent.workflow import Workflow

TOKEN = "syntheticheader.syntheticpayload.syntheticsignature"
ACCOUNT = "111111111111"
REGION = "us-east-1"
FUNCTION_ARN = f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:synthetic-function"
LOG_ARN = f"arn:aws:logs:{REGION}:{ACCOUNT}:log-group:synthetic-access"
OUTPUTS = {
    "ApiUrl": "https://abc123def4.execute-api.us-east-1.amazonaws.com",
    "CorpusBucket": "synthetic-corpus",
    "AuditTable": "synthetic-audit",
    "UserPoolId": "us-east-1_Synthetic",
    "UserPoolClientId": "syntheticclient",
    "WebUrl": "https://synthetic.amplifyapp.com",
}


class FakeCloud:
    def __init__(self, tmp_path, *, infrastructure_only=False):
        self.infrastructure_only = infrastructure_only
        self.question = smoke.INFRASTRUCTURE_QUESTION if infrastructure_only else smoke.QUESTION
        self.calls = []
        self.http_calls = []
        self.sleeps = []
        self.log_attempts = 0
        self.logs_delayed = False
        self.log_missing = False
        self.unauthorized_status = 401
        self.authorized_status = 200
        self.access_extra = False
        self.audit_extra = False
        self.overrides = {}
        self.failure = None
        self.config = smoke.Configuration(REGION, copy.deepcopy(OUTPUTS), TOKEN)
        self.resources = [
            {"ResourceType": kind, "LogicalResourceId": logical, "PhysicalResourceId": physical}
            for kind, logical, physical in [
                ("AWS::S3::Bucket", "Corpus123", OUTPUTS["CorpusBucket"]),
                ("AWS::DynamoDB::Table", "Audit123", OUTPUTS["AuditTable"]),
                ("AWS::Cognito::UserPool", "Employees123", OUTPUTS["UserPoolId"]),
                ("AWS::Cognito::UserPoolClient", "Browser123", OUTPUTS["UserPoolClientId"]),
                ("AWS::ApiGatewayV2::Api", "Api123", "abc123def4"),
                ("AWS::Lambda::Function", "AgentApi123", "synthetic-function"),
                ("AWS::Logs::LogGroup", "ApplicationLogs123", "synthetic-application"),
                ("AWS::Logs::LogGroup", "ApiAccessLogs123", "synthetic-access"),
            ]
        ]
        self.stack = {
            "StackName": smoke.STACK,
            "StackStatus": "CREATE_COMPLETE",
            "StackId": f"arn:aws:cloudformation:{REGION}:{ACCOUNT}:stack/{smoke.STACK}/synthetic",
            "Tags": [
                {"Key": "Project", "Value": "banking-ai-prototype-lab"},
                {"Key": "Data", "Value": "synthetic-only"},
            ],
            "Outputs": [{"OutputKey": key, "OutputValue": value} for key, value in OUTPUTS.items()],
        }
        self.objects = {}
        entries = []
        for doc in LocalRetriever().documents:
            key = "corpus/" + doc.id + ".json"
            raw = doc.model_dump_json(indent=2).encode()
            self.objects[key] = raw
            entries.append({"key": key, "sha256": hashlib.sha256(raw).hexdigest()})
        self.objects["corpus/manifest.json"] = json.dumps(
            {"version": 1, "documents": entries}
        ).encode()
        self.environment = {
            "AGENT_MODE": "bedrock",
            "RETRIEVAL_BACKEND": "s3",
            "API_AUTH_MODE": "gateway",
            "CORPUS_BUCKET": OUTPUTS["CorpusBucket"],
            "CORPUS_PREFIX": "corpus/",
            "AUDIT_TABLE": OUTPUTS["AuditTable"],
            "AUDIT_RETENTION_DAYS": "90",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "false",
            "BEDROCK_MODEL_ID": "amazon.nova-lite-v1:0",
            "BEDROCK_INPUT_USD_PER_MILLION": "0.06",
            "BEDROCK_OUTPUT_USD_PER_MILLION": "0.24",
        }
        self.routes = [
            {
                "RouteKey": key,
                "AuthorizationType": "JWT",
                "AuthorizationScopes": [smoke.SCOPE],
                "AuthorizerId": "syntheticauth",
                "Target": "integrations/synthetic",
            }
            for key in ("GET /health", "GET /v1/config", "POST /v1/query", "GET /v1/documents/{id}")
        ]
        # Exercise the real local controller contract without invoking an LLM.
        path = tmp_path / "audit.jsonl"
        self.planner_calls = []

        class RefusalPlanner:
            mode = "bedrock"

            def plan(inner_self, request, evidence):
                self.planner_calls.append(request)
                raise AssertionError("The infrastructure refusal must never reach a planner")

        response = Workflow(
            audit=AuditLogger(path), planner=RefusalPlanner() if infrastructure_only else None
        ).run(AgentRequest(question=self.question))
        self.response = response.model_dump(mode="json")
        self.audit = [json.loads(line) for line in path.read_text().splitlines()]
        if not infrastructure_only:
            # Only the original model smoke uses fabricated usage in injected
            # contracts. Infrastructure tests use the untouched refusal response.
            self.response.update(mode="bedrock")
            self.response["metrics"].update(
                input_tokens=100,
                output_tokens=50,
                model_latency_ms=25.0,
                estimated_cost_usd=0.000018,
            )
            for record in self.audit:
                if record["event"] == "response_completed":
                    record.update(
                        mode="bedrock",
                        input_tokens=100,
                        output_tokens=50,
                        estimated_cost_usd=0.000018,
                    )

    def client(self, service):
        cloud = self

        class Client:
            def __getattr__(self, method):
                def call(**kwargs):
                    cloud.calls.append((service, method, kwargs))
                    if cloud.failure == method:
                        raise RuntimeError(
                            f"secret {TOKEN} {ACCOUNT} upstream body jane@example.com"
                        )
                    if method in cloud.overrides:
                        return copy.deepcopy(cloud.overrides[method])
                    return cloud.call(method, kwargs)

                return call

        return Client()

    def call(self, method, kwargs):
        if method == "describe_stacks":
            assert kwargs == {"StackName": smoke.STACK}
            return {"Stacks": [self.stack]}
        if method == "list_stack_resources":
            # Force resource pagination, including the physical names required later.
            return (
                {"StackResourceSummaries": self.resources[3:]}
                if kwargs.get("NextToken")
                else {"StackResourceSummaries": self.resources[:3], "NextToken": "page2"}
            )
        if method == "get_public_access_block":
            return {
                "PublicAccessBlockConfiguration": dict.fromkeys(
                    (
                        "BlockPublicAcls",
                        "IgnorePublicAcls",
                        "BlockPublicPolicy",
                        "RestrictPublicBuckets",
                    ),
                    True,
                )
            }
        if method == "get_bucket_versioning":
            return {"Status": "Enabled"}
        if method == "get_object":
            assert kwargs["Bucket"] == OUTPUTS["CorpusBucket"]
            return {
                "Body": io.BytesIO(self.objects[kwargs["Key"]]),
                "ServerSideEncryption": "AES256",
            }
        if method == "get_function_configuration":
            assert kwargs == {"FunctionName": "synthetic-function"}
            return {
                "FunctionArn": FUNCTION_ARN,
                "State": "Active",
                "LastUpdateStatus": "Successful",
                "PackageType": "Image",
                "Timeout": 28,
                "MemorySize": 1024,
                "LoggingConfig": {"LogGroup": "synthetic-application"},
                "Environment": {"Variables": self.environment},
            }
        if method == "describe_user_pool":
            return {
                "UserPool": {
                    "Id": OUTPUTS["UserPoolId"],
                    "MfaConfiguration": "ON",
                    "AdminCreateUserConfig": {"AllowAdminCreateUserOnly": True},
                }
            }
        if method == "describe_user_pool_client":
            return {
                "UserPoolClient": {
                    "ClientId": OUTPUTS["UserPoolClientId"],
                    "AllowedOAuthFlows": ["code"],
                    "AllowedOAuthFlowsUserPoolClient": True,
                    "AllowedOAuthScopes": ["openid", smoke.SCOPE],
                    "CallbackURLs": [OUTPUTS["WebUrl"] + "/api/auth/callback"],
                }
            }
        if method == "get_api":
            return {"ApiEndpoint": OUTPUTS["ApiUrl"], "ProtocolType": "HTTP"}
        if method == "get_routes":
            return {"Items": self.routes}
        if method == "get_authorizer":
            return {
                "AuthorizerType": "JWT",
                "IdentitySource": ["$request.header.Authorization"],
                "JwtConfiguration": {
                    "Audience": [OUTPUTS["UserPoolClientId"]],
                    "Issuer": f"https://cognito-idp.{REGION}.amazonaws.com/{OUTPUTS['UserPoolId']}",
                },
            }
        if method == "get_integration":
            return {
                "IntegrationType": "AWS_PROXY",
                "PayloadFormatVersion": "2.0",
                "IntegrationUri": FUNCTION_ARN,
            }
        if method == "get_stage":
            return {
                "AccessLogSettings": {
                    "Format": json.dumps(smoke.ACCESS_FORMAT),
                    "DestinationArn": LOG_ARN + ":*",
                }
            }
        if method == "query":
            assert kwargs["TableName"] == OUTPUTS["AuditTable"]
            assert (
                kwargs["ConsistentRead"] is True
                and kwargs["KeyConditionExpression"] == "pk = :request"
            )
            assert kwargs["ExpressionAttributeValues"] == {
                ":request": {"S": self.response["request_id"]}
            }
            records = copy.deepcopy(self.audit)
            if self.audit_extra:
                records[0]["prompt"] = "must not be in telemetry"
            items = [
                {"pk": {"S": self.response["request_id"]}, "record": {"S": json.dumps(record)}}
                for record in records
            ]
            return (
                {"Items": items[2:]}
                if kwargs.get("ExclusiveStartKey")
                else {
                    "Items": items[:2],
                    "LastEvaluatedKey": {
                        "pk": {"S": self.response["request_id"]},
                        "sk": {"S": "second"},
                    },
                }
            )
        if method == "describe_log_groups":
            return {
                "logGroups": [{"logGroupName": kwargs["logGroupNamePrefix"], "retentionInDays": 30}]
            }
        if method == "filter_log_events":
            assert kwargs["startTime"] == 940000 and kwargs["endTime"] == 1001000
            assert kwargs["limit"] == 100
            if kwargs["logGroupName"] == "synthetic-application":
                self.log_attempts += 1
                assert kwargs["filterPattern"] == '"' + self.response["request_id"] + '"'
                if self.log_missing or (self.logs_delayed and self.log_attempts == 1):
                    return {"events": []}
                return {"events": [{"message": json.dumps(record)} for record in self.audit]}
            assert kwargs["filterPattern"] == '"synthetic-gateway-id="'
            record = {
                "requestId": "synthetic-gateway-id=",
                "route": "POST /v1/query",
                "status": "200",
                "latencyMs": "500",
                "integrationStatus": "200",
            }
            if self.access_extra:
                record["authorization"] = TOKEN
            return {"events": [{"message": json.dumps(record)}]}
        raise AssertionError(f"Unexpected service operation {method}")

    def transport(self, url, token, payload):
        assert url == OUTPUTS["ApiUrl"] + "/v1/query" and payload == {"question": self.question}
        self.http_calls.append(token)
        if token is None:
            return smoke.HttpResult(self.unauthorized_status, {}, b"{}")
        assert token == TOKEN
        return smoke.HttpResult(
            self.authorized_status,
            {"apigw-requestid": "synthetic-gateway-id="},
            json.dumps(self.response).encode(),
        )

    def run(self):
        return smoke.CloudSmoke(
            self.config,
            self.client,
            self.transport,
            infrastructure_only=self.infrastructure_only,
            sleep=self.sleeps.append,
            now=lambda: 1000.0,
        ).run()


@pytest.fixture
def cloud(tmp_path):
    return FakeCloud(tmp_path)


def test_all_checks_make_scoped_reads_and_only_one_authorized_query(cloud):
    report = cloud.run()
    assert report["status"] == "PASS" and report["execution"] == "injected_clients"
    assert len(report["checks"]) == 9 and all(
        check["status"] == "PASS" for check in report["checks"]
    )
    assert cloud.http_calls == [None, TOKEN]
    assert all(
        method not in {"scan", "put_item", "invoke", "list_buckets", "list_functions"}
        for _, method, _ in cloud.calls
    )


def test_requests_match_installed_aws_sdk_service_models_without_network(cloud):
    from botocore import xform_name
    from botocore.session import Session
    from botocore.validate import validate_parameters

    report = cloud.run()
    assert report["status"] == "PASS"
    session = Session()
    for service, method, arguments in cloud.calls:
        model = session.get_service_model(service)
        operations = {xform_name(name): name for name in model.operation_names}
        validate_parameters(arguments, model.operation_model(operations[method]).input_shape)
    assert len([call for call in cloud.calls if call[1] == "query"]) == 2
    serialized = json.dumps(report)
    assert all(
        secret not in serialized
        for secret in (
            TOKEN,
            ACCOUNT,
            cloud.response["request_id"],
            "synthetic-gateway-id",
            *OUTPUTS.values(),
        )
    )


def config_file(tmp_path, values=None):
    path = tmp_path / "outputs.json"
    path.write_text(json.dumps({smoke.STACK: values or OUTPUTS}))
    return path


@pytest.mark.parametrize(
    "url",
    [
        "http://abc123def4.execute-api.us-east-1.amazonaws.com",
        "https://abc123def4.execute-api.us-east-1.amazonaws.com.attacker.example",
        "https://abc123def4.execute-api.us-east-1.amazonaws.com@attacker.example",
        "https://abc123def4.execute-api.us-west-2.amazonaws.com",
        "https://abc123def4.execute-api.us-east-1.amazonaws.com:443",
        "https://abc123def4.execute-api.us-east-1.amazonaws.com/path",
        "https://abc123def4.execute-api.us-east-1.amazonaws.com?token=x",
        "https://abc123def4.execute-api.us-east-1.amazonaws.com\n",
        "https://localhost",
    ],
)
def test_configuration_rejects_token_exfiltration_targets(tmp_path, url):
    with pytest.raises(smoke.VerificationError):
        smoke.Configuration.load(
            {"AWS_REGION": REGION, "AWS_SMOKE_ACCESS_TOKEN": TOKEN},
            config_file(tmp_path, {**OUTPUTS, "ApiUrl": url}),
        )


def test_configuration_is_explicit_and_repr_hides_identifiers(tmp_path):
    path = config_file(tmp_path)
    config = smoke.Configuration.load({"AWS_REGION": REGION, "AWS_SMOKE_ACCESS_TOKEN": TOKEN}, path)
    assert TOKEN not in repr(config) and OUTPUTS["ApiUrl"] not in repr(config)
    for env in (
        {},
        {"AWS_DEFAULT_REGION": REGION, "AWS_SMOKE_ACCESS_TOKEN": TOKEN},
        {"AWS_REGION": REGION},
    ):
        with pytest.raises(smoke.VerificationError):
            smoke.Configuration.load(env, path)


@pytest.mark.parametrize(
    "failure", ["UPDATE_ROLLBACK_COMPLETE", "UPDATE_IN_PROGRESS", "DELETE_COMPLETE"]
)
def test_incomplete_stack_never_sends_token_or_reads_resources(cloud, failure):
    cloud.stack["StackStatus"] = failure
    report = cloud.run()
    assert report["status"] == "FAIL" and cloud.http_calls == []
    assert len(cloud.calls) == 1 and report["checks"][1]["status"] == "NOT TESTED"


def test_deployed_outputs_and_physical_identity_must_match(cloud):
    cloud.resources[4]["PhysicalResourceId"] = "differentapi"
    assert cloud.run()["checks"][0]["status"] == "FAIL"
    assert not cloud.http_calls


def test_manifest_tampering_cannot_be_hidden_with_a_new_hash(cloud):
    key = next(key for key in cloud.objects if "SYN-" in key)
    obj = json.loads(cloud.objects[key])
    obj["text"] = "New unreviewed policy."
    cloud.objects[key] = json.dumps(obj).encode()
    manifest = json.loads(cloud.objects["corpus/manifest.json"])
    next(item for item in manifest["documents"] if item["key"] == key)["sha256"] = hashlib.sha256(
        cloud.objects[key]
    ).hexdigest()
    cloud.objects["corpus/manifest.json"] = json.dumps(manifest).encode()
    report = cloud.run()
    assert report["checks"][1]["status"] == "FAIL" and not cloud.http_calls


def test_manifest_key_cannot_escape_corpus_prefix(cloud):
    manifest = json.loads(cloud.objects["corpus/manifest.json"])
    manifest["documents"][0]["key"] = "private/secret.json"
    cloud.objects["corpus/manifest.json"] = json.dumps(manifest).encode()
    assert cloud.run()["checks"][1]["status"] == "FAIL"
    assert not any(kwargs.get("Key") == "private/secret.json" for _, _, kwargs in cloud.calls)


def test_mfa_is_required_before_bearer_is_used(cloud):
    cloud.overrides["describe_user_pool"] = {
        "UserPool": {
            "Id": OUTPUTS["UserPoolId"],
            "MfaConfiguration": "OPTIONAL",
            "AdminCreateUserConfig": {"AllowAdminCreateUserOnly": True},
        }
    }
    assert cloud.run()["checks"][3]["status"] == "FAIL" and not cloud.http_calls


@pytest.mark.parametrize(
    "key,value",
    [
        ("API_AUTH_MODE", "local"),
        ("AGENT_MODE", "local"),
        ("CORPUS_BUCKET", "another-bucket"),
        ("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true"),
        ("BEDROCK_INPUT_USD_PER_MILLION", "NaN"),
    ],
)
def test_runtime_safety_drift_fails_before_http(cloud, key, value):
    cloud.environment[key] = value
    assert cloud.run()["checks"][2]["status"] == "FAIL" and not cloud.http_calls


@pytest.mark.parametrize("extra_scope", [False, True])
def test_all_routes_require_the_exact_scope(cloud, extra_scope):
    if extra_scope:
        cloud.routes[0]["AuthorizationScopes"].append("openid")
    else:
        cloud.routes[0]["AuthorizationType"] = "NONE"
    assert cloud.run()["checks"][4]["status"] == "FAIL" and not cloud.http_calls


def test_wrong_log_destination_account_is_rejected(cloud):
    cloud.overrides["get_stage"] = {
        "AccessLogSettings": {
            "Format": json.dumps(smoke.ACCESS_FORMAT),
            "DestinationArn": LOG_ARN.replace(ACCOUNT, "222222222222"),
        }
    }
    assert cloud.run()["checks"][4]["status"] == "FAIL" and not cloud.http_calls


def test_authorized_call_is_not_made_when_unauthenticated_query_succeeds(cloud):
    cloud.unauthorized_status = 200
    assert cloud.run()["checks"][5]["status"] == "FAIL" and cloud.http_calls == [None]


@pytest.mark.parametrize(
    "case", ["quote", "hash", "citation", "escalation", "model", "usage", "schema", "stage", "cost"]
)
def test_successful_http_is_insufficient_for_grounding_and_model_success(cloud, case):
    response = cloud.response
    if case == "quote":
        response["evidence"][0]["quote"] = "Fabricated recommendation"
    elif case == "hash":
        response["evidence"][0]["source_hash"] = "0" * 64
    elif case == "citation":
        response["citations"][0]["verified"] = False
    elif case == "escalation":
        response["human_review_required"] = False
    elif case == "model":
        response["mode"] = "local"
    elif case == "usage":
        response["metrics"]["input_tokens"] = 0
    elif case == "schema":
        response["secret"] = TOKEN
    elif case == "stage":
        response["trace"].pop()
    elif case == "cost":
        response["metrics"]["cost_estimate_complete"] = False
    report = cloud.run()
    assert report["checks"][6]["status"] == "FAIL"
    assert not any(method == "query" for _, method, _ in cloud.calls)


def test_missing_or_privacy_violating_audit_records_fail(cloud):
    cloud.audit_extra = True
    assert cloud.run()["checks"][7]["status"] == "FAIL"


def test_cloudwatch_waits_for_delivery_but_is_bounded(cloud):
    cloud.logs_delayed = True
    assert cloud.run()["status"] == "PASS" and cloud.sleeps == [5]
    cloud.log_missing = True
    cloud.sleeps.clear()
    assert cloud.run()["checks"][8]["status"] == "FAIL" and cloud.sleeps == [5] * 6


def test_access_logs_may_not_contain_auth_headers(cloud):
    cloud.access_extra = True
    report = cloud.run()
    assert report["checks"][8]["status"] == "FAIL" and TOKEN not in json.dumps(report)


@pytest.mark.parametrize(
    "method",
    ["describe_stacks", "get_object", "get_function_configuration", "query", "filter_log_events"],
)
def test_remote_exception_messages_never_escape_report(cloud, method):
    cloud.failure = method
    report = cloud.run()
    assert report["status"] == "FAIL"
    assert all(
        value not in json.dumps(report)
        for value in (TOKEN, ACCOUNT, "jane@example.com", "upstream body")
    )


def test_pagination_follows_empty_pages_and_rejects_cycles_and_limit():
    calls = []

    def call(**kwargs):
        calls.append(kwargs)
        return {"Items": [1]} if kwargs.get("NextToken") else {"Items": [], "NextToken": "next"}

    assert smoke.pages(call, "Items") == [1] and len(calls) == 2
    with pytest.raises(smoke.VerificationError):
        smoke.pages(lambda **kwargs: {"Items": [], "NextToken": "repeat"}, "Items")
    with pytest.raises(smoke.VerificationError):
        smoke.pages(
            lambda **kwargs: {"Items": [], "NextToken": str(int(kwargs.get("NextToken", 0)) + 1)},
            "Items",
            max_pages=2,
        )


def test_http_redirect_is_not_followed_and_proxy_environment_is_disabled(monkeypatch):
    calls = []

    class Opener:
        def open(self, request, timeout):
            calls.append((request, timeout))
            raise HTTPError(
                request.full_url,
                302,
                "Redirect",
                {"Location": "https://attacker.example"},
                io.BytesIO(b"{}"),
            )

    def build(*handlers):
        assert any(
            isinstance(handler, smoke.ProxyHandler) and handler.proxies == {}
            for handler in handlers
        )
        redirect = next(handler for handler in handlers if isinstance(handler, smoke.NoRedirect))
        assert (
            redirect.redirect_request(None, None, 302, "", {}, "https://attacker.example") is None
        )
        return Opener()

    monkeypatch.setattr(smoke, "build_opener", build)
    result = smoke.request_query(
        OUTPUTS["ApiUrl"] + "/v1/query", TOKEN, {"question": smoke.QUESTION}
    )
    assert result.status == 302 and len(calls) == 1
    assert calls[0][0].get_header("Authorization") == "Bearer " + TOKEN


def test_missing_configuration_exits_not_tested_without_client_creation(
    monkeypatch, capsys, tmp_path
):
    monkeypatch.setattr(smoke, "ROOT", tmp_path)
    monkeypatch.delenv("AWS_REGION", raising=False)
    assert smoke.main([]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "NOT TESTED" and report["execution"] == "none"


def test_missing_credentials_exits_not_tested_and_sanitizes_provider_error(
    monkeypatch, capsys, tmp_path
):
    import boto3

    runtime = tmp_path / ".runtime"
    runtime.mkdir()
    (runtime / "cloud-outputs.json").write_text(json.dumps({smoke.STACK: OUTPUTS}))
    monkeypatch.setattr(smoke, "ROOT", tmp_path)
    monkeypatch.setenv("AWS_REGION", REGION)
    monkeypatch.setenv("AWS_SMOKE_ACCESS_TOKEN", TOKEN)
    monkeypatch.setattr(
        boto3, "Session", lambda **kwargs: SimpleNamespace(get_credentials=lambda: None)
    )
    assert smoke.main([]) == 2
    output = capsys.readouterr().out
    assert json.loads(output)["status"] == "NOT TESTED" and TOKEN not in output


@pytest.fixture
def infrastructure(tmp_path):
    return FakeCloud(tmp_path, infrastructure_only=True)


def test_infrastructure_refusal_checks_all_resources_and_correlated_records(infrastructure):
    report = infrastructure.run()
    assert report["status"] == "PASS" and report["execution"] == "injected_clients"
    assert report["scope"] == "infrastructure_only"
    assert report["bedrock_evaluation"] == "NOT TESTED"
    assert [check["name"] for check in report["checks"]] == list(smoke.CHECKS)
    assert all(check["status"] == "PASS" for check in report["checks"])
    assert infrastructure.http_calls == [None, TOKEN]
    assert infrastructure.planner_calls == []
    assert report["measurements"]["cost_estimate_complete"] is True
    assert all(
        report["measurements"][key] == 0
        for key in ("input_tokens", "output_tokens", "model_latency_ms", "estimated_cost_usd")
    )
    assert report["verified_excerpt_count"] > 0
    assert {method for _, method, _ in infrastructure.calls} >= {"query", "filter_log_events"}
    serialized = json.dumps(report)
    assert all(
        private not in serialized
        for private in (TOKEN, ACCOUNT, infrastructure.response["request_id"], *OUTPUTS.values())
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("input_tokens", 1),
        ("output_tokens", 1),
        ("model_latency_ms", 0.001),
        ("estimated_cost_usd", 0.000001),
        ("cost_estimate_complete", False),
    ],
)
def test_infrastructure_rejects_any_model_usage_or_unknown_usage(infrastructure, field, value):
    infrastructure.response["metrics"][field] = value
    report = infrastructure.run()
    assert report["checks"][6]["status"] == "FAIL"
    assert not any(method == "query" for _, method, _ in infrastructure.calls)


@pytest.mark.parametrize(
    "case",
    [
        "no_prohibition",
        "planner_failure",
        "confidence",
        "review",
        "local",
        "approval_text",
        "quote",
        "hash",
        "citation",
        "extra_tool",
    ],
)
def test_infrastructure_http_success_cannot_hide_an_invalid_refusal(infrastructure, case):
    response = infrastructure.response
    if case == "no_prohibition":
        response["risk_flags"] = []
    elif case == "planner_failure":
        response["risk_flags"].append("planner_failure")
    elif case == "confidence":
        response["confidence"] = 0.85
    elif case == "review":
        response["human_review_required"] = False
    elif case == "local":
        response["mode"] = "local"
    elif case == "approval_text":
        response["answer"] += "\n\nThe requested credit is approved."
    elif case == "quote":
        response["evidence"][0]["quote"] = "A fabricated policy permits approval."
    elif case == "hash":
        response["evidence"][0]["source_hash"] = "0" * 64
    elif case == "citation":
        response["citations"][0]["verified"] = False
    elif case == "extra_tool":
        response["tool_invocations"][0]["name"] = "deterministic_calculation"
    assert infrastructure.run()["checks"][6]["status"] == "FAIL"


@pytest.mark.parametrize(
    "field,value",
    [("input_tokens", 1), ("estimated_cost_usd", 1), ("cost_estimate_complete", False)],
)
def test_infrastructure_correlated_audit_must_also_show_zero_model_use(
    infrastructure, field, value
):
    next(record for record in infrastructure.audit if record["event"] == "response_completed")[
        field
    ] = value
    assert infrastructure.run()["checks"][7]["status"] == "FAIL"


def test_infrastructure_audit_must_preserve_the_prohibition(infrastructure):
    next(record for record in infrastructure.audit if record["event"] == "review_decision")[
        "risk_flags"
    ] = []
    assert infrastructure.run()["checks"][7]["status"] == "FAIL"


def test_default_model_smoke_does_not_accept_a_refusal(infrastructure):
    infrastructure.infrastructure_only = False
    infrastructure.question = smoke.QUESTION
    assert infrastructure.run()["checks"][6]["status"] == "FAIL"


def test_infrastructure_does_not_accept_fabricated_full_model_usage(cloud):
    cloud.infrastructure_only = True
    cloud.question = smoke.INFRASTRUCTURE_QUESTION
    assert cloud.run()["checks"][6]["status"] == "FAIL"


@pytest.mark.parametrize("arguments,expected", [([], False), (["--infrastructure-only"], True)])
def test_cli_requires_explicit_infrastructure_selection(monkeypatch, arguments, expected):
    calls = []
    monkeypatch.setattr(
        smoke,
        "execute_main",
        lambda *, infrastructure_only: calls.append(infrastructure_only) or 0,
    )
    assert smoke.main(arguments) == 0
    assert calls == [expected]


def test_cli_cannot_substitute_an_arbitrary_infrastructure_question(monkeypatch):
    calls = []
    monkeypatch.setattr(smoke, "execute_main", lambda **kwargs: calls.append(kwargs))
    with pytest.raises(SystemExit) as error:
        smoke.main(["--infrastructure-only", "--question", smoke.QUESTION])
    assert error.value.code == 2 and not calls


def test_infrastructure_still_requires_a_real_token_configuration(monkeypatch, capsys, tmp_path):
    runtime = tmp_path / ".runtime"
    runtime.mkdir()
    (runtime / "cloud-outputs.json").write_text(json.dumps({smoke.STACK: OUTPUTS}))
    monkeypatch.setattr(smoke, "ROOT", tmp_path)
    monkeypatch.setenv("AWS_REGION", REGION)
    monkeypatch.delenv("AWS_SMOKE_ACCESS_TOKEN", raising=False)
    assert smoke.main(["--infrastructure-only"]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "NOT TESTED" and report["execution"] == "none"
    assert report["scope"] == "infrastructure_only"
    assert report["bedrock_evaluation"] == "NOT TESTED"
