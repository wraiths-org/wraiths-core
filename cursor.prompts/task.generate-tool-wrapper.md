Task: Generate a WRAITHS tool wrapper microservice.

Listen: \`tool.invoke.<domain>.<tool_name>\`

Execute: CLI with parameters from \`event.parameters\`

Publish: \`tool.result.<domain>.<tool_name>\`

Structure outputs per tool schema; include Dockerfile; robust error handling.

Deliver:
- \`src/service-name/app.py\`
- \`src/service-name/Dockerfile\`
- \`tests/test_service.py\`
- \`docs/API.md\`
