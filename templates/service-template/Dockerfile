FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app.py /app/app.py

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" nats-py pydantic

EXPOSE 8000
CMD ["python", "-m", "app"]
