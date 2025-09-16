"""
WRAITHS Core Application

Main FastAPI application entry point for the WRAITHS cybersecurity platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

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

# Create FastAPI application
app = FastAPI(
    title="WRAITHS Core",
    description="Cybersecurity Tool Orchestration Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": "wraiths-core",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("WRAITHS Core application starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("WRAITHS Core application shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
