"""
WRAITHS Core Application

Main FastAPI application entry point for the WRAITHS cybersecurity platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
import structlog
import logging
from contextlib import asynccontextmanager
import os
import subprocess
from datetime import datetime, timezone

# Configure structured logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context replacing deprecated on_event hooks."""
    env = os.getenv("ENVIRONMENT", "dev")
    service = "wraiths-core"
    version = "1.0.0"

    # Resolve git metadata best-effort
    def _git(cmd: list[str]) -> str | None:
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            return out or None
        except Exception:
            return None

    commit = _git(["git", "rev-parse", "--short", "HEAD"]) or os.getenv("GIT_COMMIT")
    branch = _git(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or os.getenv("GIT_BRANCH")
    build_time = datetime.now(timezone.utc).isoformat()

    # Bind structured metadata
    log = logger.bind(service=service, environment=env, version=version, commit=commit, branch=branch)

    # Stash metadata on app.state for endpoints/tests
    app.state.started = False
    app.state.service_info = {
        "service": service,
        "version": version,
        "commit": commit,
        "branch": branch,
        "build_time": build_time,
        "environment": env,
    }

    # Optional: OpenTelemetry tracing wiring
    if os.getenv("OTEL_ENABLED", "false").lower() in {"1", "true", "yes"}:
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            resource = Resource.create({
                "service.name": service,
                "service.version": version,
                "deployment.environment": env,
            })
            provider = TracerProvider(resource=resource)
            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
            exporter = OTLPSpanExporter(endpoint=endpoint) if endpoint else OTLPSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)

            # Instrument FastAPI app
            try:
                from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

                FastAPIInstrumentor.instrument_app(app)
                log.info("OpenTelemetry instrumentation enabled")
            except Exception:
                log.warning("OpenTelemetry FastAPI instrumentation not available")
        except Exception as e:
            log.warning("Failed to configure OpenTelemetry", error=str(e))

    log.info("WRAITHS Core application starting up")
    app.state.started = True
    app.state.ready = True  # base readiness; external deps can flip this
    app.state.dependencies = {
        "nats": {
            "configured": bool(os.getenv("NATS_URL")),
            "connected": None,  # future: set True/False if we add a real client
            "required": os.getenv("NATS_REQUIRED", "false").lower() in {"1", "true", "yes"},
        }
    }
    try:
        yield
    finally:
        app.state.started = False
        log.info("WRAITHS Core application shutting down")


# Create FastAPI application
app = FastAPI(
    title="WRAITHS Core",
    description="Cybersecurity Tool Orchestration Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Trusted hosts and CORS based on environment
env = os.getenv("ENVIRONMENT", "dev")
allowed_hosts = os.getenv("ALLOWED_HOSTS", "*")
if allowed_hosts and allowed_hosts != "*":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[h.strip() for h in allowed_hosts.split(",") if h.strip()])

raw_origins = os.getenv("CORS_ORIGINS")
if raw_origins:
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
elif env == "prod":
    origins = ["https://example.com"]  # tighten default in prod; override via CORS_ORIGINS
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Correlation ID: use header if provided, else generate lightweight one
        corr = request.headers.get("x-correlation-id") or os.getenv("DEFAULT_CORRELATION_ID")
        if not corr:
            try:
                # Use a short random token without heavy deps
                corr = os.urandom(6).hex()
            except Exception:
                corr = "unknown"

        start = datetime.now(timezone.utc)
        bound = logger.bind(
            method=request.method,
            path=str(request.url.path),
            correlation_id=corr,
            service=app.state.service_info.get("service", "wraiths-core"),
            version=app.state.service_info.get("version", "1.0.0"),
        )
        bound.info("request.start")
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            bound = bound.bind(duration_ms=round(duration_ms, 2))
            bound.exception("request.error")
            raise exc
        duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        response.headers.setdefault("x-correlation-id", corr)
        bound.bind(status_code=response.status_code, duration_ms=round(duration_ms, 2)).info("request.end")
        return response


app.add_middleware(RequestLoggingMiddleware)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        # Basic hardening headers
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        if env != "dev":
            response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": app.state.service_info.get("service", "wraiths-core"),
        "version": app.state.service_info.get("version", "1.0.0"),
    }


@app.get("/version")
async def version_info():
    """Return service version and build metadata."""
    return app.state.service_info


@app.get("/ready")
async def readiness():
    """Readiness probe. Returns 200 when ready, else 503 with details."""
    deps = app.state.dependencies
    ready = bool(getattr(app.state, "started", False))
    # Honor required flags for dependencies (e.g., NATS)
    for name, info in deps.items():
        if info.get("required") and not info.get("connected"):
            ready = False
            break
    status_code = 200 if ready else 503
    return JSONResponse(
        content={
            "ready": ready,
            "dependencies": deps,
            "service": app.state.service_info.get("service"),
            "environment": app.state.service_info.get("environment"),
        },
        status_code=status_code,
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
