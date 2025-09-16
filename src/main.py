"""
WRAITHS Core Application

Main FastAPI application entry point for the WRAITHS cybersecurity platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog
from contextlib import asynccontextmanager
import os
import subprocess
from datetime import datetime, timezone

# Configure structured logging
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

    log.info("WRAITHS Core application starting up")
    app.state.started = True
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
