# Multi-stage Dockerfile template, extended per service via ARG SERVICE_NAME.
# Concrete per-service Dockerfiles import from this one.

ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy workspace-level deps first for layer caching.
COPY pyproject.toml ./
COPY services/__shared__ ./services/__shared__

FROM base AS deps
ARG SERVICE_NAME
COPY services/${SERVICE_NAME}/pyproject.toml ./services/${SERVICE_NAME}/
RUN uv sync --project services/${SERVICE_NAME}

FROM deps AS runtime
ARG SERVICE_NAME
COPY services/${SERVICE_NAME}/src ./services/${SERVICE_NAME}/src
ENV SERVICE_NAME=${SERVICE_NAME}
EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--factory", "main:create_app"]
