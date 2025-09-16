<<<<<<< HEAD
Task: Scaffold a new microservice following WRAITHS rules (FastAPI + NATS).
Requirements: \`/health\` endpoint, NATS subjects per rules, Dockerfile, unit tests.
Deliver: \`src/...\`, \`tests/...\`, \`docs/README.md\`.
=======
# Generate Microservice Template

## Task: Create a new microservice

### Required Parameters
- `service_name`: Name of the service (e.g., "recon-scanner")
- `domain`: Domain category (e.g., "recon", "exploitation", "forensics")
- `port`: Service port number (e.g., 8001)

### Generated Structure
```
{service_name}/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py          # Health check endpoint
│   │   └── routes.py          # Service-specific routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   └── events.py          # NATS event handlers
Task: Scaffold a new microservice following WRAITHS rules (FastAPI + NATS).
Requirements: `/health` endpoint, NATS subjects per rules, Dockerfile, unit tests.
Deliver: `src/...`, `tests/...`, `docs/README.md`.
│   └── utils/
