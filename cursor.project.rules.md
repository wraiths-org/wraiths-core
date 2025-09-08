WRAITHS Project Rules

## Event-Driven Communication
- **Mandatory:** All inter-service communication MUST use the defined NATS subjects: \`tool.invoke.<domain>.<tool>\` and \`tool.result.<domain>.<tool>\`.
- **Schema Compliance:** Every event published MUST adhere to the official v1.0 JSON Schema defined in \`wraiths-core/specs/event-schema/v1.0.json\`. Validation against this schema is required.
- **Domains:** The \`<domain>\` segment MUST be one of: recon, web, bluetooth, sdr, exploitation, forensics, malware, wireless, mobile, anonymity.

## API-First Design
- Every microservice MUST expose a \`GET /health\` endpoint returning \`{"status": "ok"}\`.
- The primary interface is the event bus. HTTP APIs are secondary and must be documented with OpenAPI.

## Testing & Quality
- Target 80% test coverage minimum for all new code.
- All event handlers must include tests for both success and failure scenarios.
- Docker images must be minimal and based on \`python:3.11-slim\` unless otherwise justified.

## Secrets & Security
- **Never** commit secrets, API keys, or credentials.
- Use GitHub Secrets for all environment-specific configuration.
- Tool results containing sensitive data must be published with appropriate access controls.

## Commit Style
- Use Conventional Commits and scope by component (e.g., \`fix(bluetooth): handle scanner timeout\`).

## Cursor AI Boundaries
- Generate code only within: \`src/\`, \`tests/\`, \`docs/\`.
- Follow existing patterns: FastAPI for HTTP, NATS for messaging.
- Always include docstrings/Pydantic models for new data structures.
- Reference the central event schema when creating new tool wrappers.
