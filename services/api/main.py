"""FastAPI boundary: fixed read-only routes and gateway claims from ASGI scope only."""

import os
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mangum import Mangum
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from starlette.responses import Response

from services.agent.models import AgentRequest, AgentResponse
from services.agent.observability import configure_telemetry
from services.agent.tools import safe_document
from services.agent.workflow import Workflow


def require_access(request: Request) -> None:
    mode = os.getenv("API_AUTH_MODE", "local")
    if mode == "local":
        if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            raise HTTPException(503, "Local authentication mode is disabled in Lambda")
        return
    if mode != "gateway":
        raise HTTPException(503, "Authentication configuration is invalid")
    # Mangum inserts the verified event. Headers/body cannot create this ASGI scope key.
    event = request.scope.get("aws.event", {})
    claims = event.get("requestContext", {}).get("authorizer", {}).get("jwt", {}).get("claims", {})
    if not claims.get("sub") or "banking-ai/query" not in claims.get("scope", "").split():
        raise HTTPException(401, "A verified gateway access token with query scope is required")


def create_app(workflow: Workflow | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        configure_telemetry()
        yield
        provider = trace.get_tracer_provider()
        if isinstance(provider, TracerProvider):
            # Mangum runs lifespan around each invocation; flush before Lambda freezes.
            provider.force_flush(timeout_millis=1000)

    application = FastAPI(
        title="Banking AI Prototype Lab",
        version="0.1.0",
        description="Synthetic portfolio demonstration; no bank affiliation. Read-only operational guidance.",
        lifespan=lifespan,
    )
    capacity = threading.BoundedSemaphore(8)

    @lru_cache(maxsize=1)
    def get_workflow() -> Workflow:
        return workflow if workflow is not None else Workflow.from_environment()

    @application.middleware("http")
    async def security_boundary(request: Request, call_next: Any) -> Response:
        if request.method == "POST":
            length = request.headers.get("content-length")
            if length is not None and (not length.isdigit() or int(length) > 16384):
                return JSONResponse(
                    {"detail": "Request body exceeds the 16 KiB limit"}, status_code=413
                )
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 16384:
                    return JSONResponse(
                        {"detail": "Request body exceeds the 16 KiB limit"}, status_code=413
                    )
            request._body = bytes(body)
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Demo-Data"] = "synthetic-only"
        return response

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
        # FastAPI defaults echo invalid input; never echo PII from rejected requests.
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid request schema",
                "errors": [
                    {
                        "location": [
                            field
                            if field
                            in {
                                "body",
                                "question",
                                "calculation",
                                "operation",
                                "operands",
                                "company_id",
                            }
                            else "<unknown>"
                            for field in item["loc"]
                        ],
                        "type": item["type"],
                    }
                    for item in error.errors()
                ],
            },
        )

    @application.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "synthetic": True, "service": "banking-ai-prototype-lab"}

    @application.get("/v1/config", dependencies=[Depends(require_access)])
    def config() -> dict[str, Any]:
        return {
            "mode": os.getenv("AGENT_MODE", "local"),
            "synthetic": True,
            "read_only": True,
            "auth_mode": os.getenv("API_AUTH_MODE", "local"),
            "allowed_tools": [
                "policy_search",
                "document_retrieval",
                "deterministic_calculation",
                "risk_classification",
                "citation_verification",
                "financial_profile_tool",
            ],
        }

    @application.post(
        "/v1/query", response_model=AgentResponse, dependencies=[Depends(require_access)]
    )
    def query(payload: AgentRequest) -> AgentResponse:
        if not capacity.acquire(blocking=False):
            raise HTTPException(429, "Request capacity exceeded; retry later")
        try:
            return get_workflow().run(payload)
        except Exception as error:
            # Do not return service, SDK, or policy exception text to an untrusted caller.
            raise HTTPException(
                503, "The governed workflow is unavailable; human review is required"
            ) from error
        finally:
            capacity.release()

    @application.get("/v1/documents/{document_id}", dependencies=[Depends(require_access)])
    def document(document_id: str) -> dict[str, Any]:
        if len(document_id) > 80 or not all(c.isalnum() or c in "_-" for c in document_id):
            raise HTTPException(404, "Document unavailable")
        try:
            found = get_workflow().retriever.get(document_id, max_classification="internal")
        except Exception as error:
            raise HTTPException(503, "Document service unavailable") from error
        if found is None or not safe_document(found):
            raise HTTPException(404, "Document unavailable")
        return {
            **found.model_dump(mode="json"),
            "source_hash": found.sha256,
            "synthetic_demo": True,
        }

    return application


app = create_app()
handler = Mangum(app, lifespan="auto")
