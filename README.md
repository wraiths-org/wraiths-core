# WRAITHS Core

Core orchestration and AI layer for the WRAITHS cybersecurity framework. This repository serves as the central hub for managing microservices, event-driven communication, and AI-powered cybersecurity operations.

## 🏗️ Architecture

WRAITHS Core follows a microservice architecture with event-driven communication using NATS JetStream. Each framework (recon, exploitation, forensics, etc.) operates as an independent service while communicating through a standardized event schema.

### Key Components

- **Event-Driven Communication**: All services communicate via NATS subjects
- **API Gateway**: Central FastAPI application for request routing
- **Event Schema**: Standardized message format across all services
- **Cursor AI Integration**: AI-powered development with strict architectural guardrails

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- NATS Server
- VS Code with Cursor extension (recommended)

### Installation

1. Clone the repository:
```bash
git clone --recursive https://github.com/wraiths-org/wraiths-core.git
cd wraiths-core
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn src.main:app --reload
```

4. Access the API documentation at `http://localhost:8000/docs`

Key endpoints:

- `GET /health` – service health and version
- `GET /version` – detailed build metadata (service, version, commit, branch, build_time, environment)

### Docker Development

```bash
docker build -t wraiths-core .
docker run -p 8000:8000 wraiths-core
```

### Developer Shortcuts

This repo includes a simple `Makefile`:

```bash
make install   # pip install -r requirements.txt
make test      # run pytest
make run       # uvicorn src.main:app --reload
make lint      # flake8
make format    # black & isort
```

## 📋 Project Structure

```
wraiths-core/
├── src/                    # Application source code
├── tests/                  # Test suites
├── frameworks/             # Framework submodules
├── specs/                  # API and event schemas
├── cursor.prompts/         # AI development templates
├── .github/workflows/      # CI/CD pipelines
├── cursor.project.rules.md # Cursor AI rules
├── cursor.context.urls.txt # AI context URLs
└── .mcp.json              # MCP server configuration
```

## 🤖 Cursor AI Configuration

This project includes comprehensive Cursor AI configuration:

- **Project Rules**: Architectural guidelines in `cursor.project.rules.md`
- **Context URLs**: External documentation links in `cursor.context.urls.txt`
- **Prompt Templates**: Development templates in `cursor.prompts/`
- **MCP Integration**: Figma and Linear integration via `.mcp.json`

### Development Workflow

1. **Event-Driven Communication**: Use NATS subjects `tool.invoke.<domain>.<tool>` and `tool.result.<domain>.<tool>`
2. **API-First Design**: Every service exposes `/health` endpoint
3. **Testing**: Maintain 80%+ code coverage
4. **Commits**: Use Conventional Commits format

## 🔧 Configuration

### Environment Variables

- `NATS_URL`: NATS server connection string
- `SERVICE_PORT`: Port to bind the service (default: 8000)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARN, ERROR)
- `ENVIRONMENT`: Deployment environment (dev, staging, prod)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARN, ERROR)
- `SERVICE_PORT`: HTTP port (default: 8000)
- `DEFAULT_CORRELATION_ID`: Fallback correlation id when header is missing

### Correlation ID and Logging

- Requests may include `x-correlation-id` header. The server echoes this header in responses.
- If missing, a lightweight id is generated and returned as `x-correlation-id`.
- All requests are logged via `structlog` with JSON, including `method`, `path`, `status_code`, and `duration_ms`.

### Event Schema

All events must conform to the schema defined in `specs/event-schema/v1.0.json`. Example:

```json
{
  "eventId": "123e4567-e89b-12d3-a456-426614174000",
  "correlationId": "123e4567-e89b-12d3-a456-426614174001",
  "timestamp": "2025-09-14T10:30:00Z",
  "source": {
    "service": "recon-scanner",
    "version": "1.2.3"
  },
  "subject": "tool.invoke.recon.port-scan",
  "eventType": "invoke",
  "payload": {
    "target": "192.168.1.1",
    "ports": "1-1000"
  }
}
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ --cov=src/ --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

## 🚀 Deployment

### CI/CD Pipeline

The project includes GitHub Actions workflows for:

- **Testing**: Automated test execution with coverage reporting
- **Security Scanning**: Trivy vulnerability scanning
- **Docker Building**: Multi-stage container builds
- **Deployment**: Environment-based deployment strategies

### Production Deployment

1. **Environment Setup**: Configure GitHub Secrets for `NATS_URL`, `DOCKERHUB_USERNAME`, etc.
2. **Branch Protection**: Enable protection rules for `main` and `dev` branches
3. **Container Registry**: Push images to `ghcr.io/wraiths-org/wraiths-core`

## 🛡️ Security

- **Secrets Management**: Never commit secrets; use GitHub Secrets or environment variables
- **Vulnerability Scanning**: Automated Trivy scans in CI/CD
- **Code Owners**: Defined in `CODEOWNERS` for automatic review assignment
- **Content Exclusion**: `.copilotignore` prevents sensitive files from AI exposure

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/amazing-feature`
3. **Commit** changes: `git commit -m 'feat(core): add amazing feature'`
4. **Push** to branch: `git push origin feat/amazing-feature`
5. **Open** a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use Black for code formatting
- Include type hints for all functions
- Write comprehensive docstrings
- Maintain 80%+ test coverage

## 📚 Documentation

- **API Docs**: Available at `/docs` when running locally
- **Event Schema**: `specs/event-schema/v1.0.json`
- **Architecture**: See `cursor.prompts/system.architect.md`
- **Templates**: Development templates in `cursor.prompts/`

## 🤖 Cursor Handoff Notes

Cursor is configured with project rules, prompts, and context URLs. To start coding with Cursor:

1. Open this repository in Cursor.
2. Review `cursor.project.rules.md` and the prompts in `cursor.prompts/`.
3. Use the provided schema at `specs/event-schema/v1.0.json` when creating or consuming events.
4. Generate code only in `src/`, `tests/`, or `docs/` per project rules.

Quick commands:

```bash
pip install -r requirements.txt
pytest -q
uvicorn src.main:app --reload
```

Optional developer setup:

```bash
pip install pre-commit
pre-commit install
```

### Git LFS Notes

This repository has Git LFS hooks enabled. If pushes fail due to missing LFS, install and initialize LFS locally:

- macOS (Homebrew):

  ```bash
  brew install git-lfs
  git lfs install
  ```

- Debian/Ubuntu:

  ```bash
  sudo apt-get install -y git-lfs
  git lfs install
  ```

- Alpine (with permissions):

  ```bash
  apk add --no-cache git-lfs
  git lfs install
  ```

If pushing from an environment without LFS and you need to proceed urgently, you can bypass hooks once:

```bash
git push --no-verify origin main
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [WRAITHS Recon](https://github.com/wraiths-org/wraiths-recon)
- [WRAITHS Exploitation](https://github.com/wraiths-org/wraiths-exploitation)
- [WRAITHS Forensics](https://github.com/wraiths-org/wraiths-forensics)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/wraiths-org/wraiths-core/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wraiths-org/wraiths-core/discussions)
- **Documentation**: [docs.wraiths.org](https://docs.wraiths.org)
