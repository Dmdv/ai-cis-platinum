# Architecture Overview

This file is the engineering entry point into the MB Finder v2 codebase. It complements `../docs/02_high_level_architecture.md` (the narrative overview) and the ADRs (decision rationale).

## Bounded contexts

The system is decomposed into bounded contexts that map 1:1 to top-level directories under `services/`. The contexts are:

| Context | Service directory | Pillar | Owner |
|---|---|---|---|
| Chemoinformatic representation | `chemoinformatic-core` | 2 | platform engineer (with chemistry review) |
| Data ingestion | `ingestion` | 4 | platform engineer |
| Model training | `model-training` | 1, 4 | platform engineer (with ML reviewer) |
| Prediction serving | `inference-api` | 1, 4 | platform engineer |
| DMTA orchestration | `agentic-orchestrator` | 3 | platform engineer (with chemist UX review) |
| User interface | `web-ui` | 4 | platform engineer (with chemist UX review) |

## Interaction patterns

- **Public users (chemists, external researchers)** interact with `web-ui` (browser) or `inference-api` (programmatic). All public traffic terminates at an API gateway with rate limiting and auth.
- **Lab members** also interact with the `agentic-orchestrator` to run campaigns.
- **Service-to-service** calls are gRPC where latency-sensitive (inference, agent tool calls), HTTP/JSON otherwise.
- **Async coordination** uses a message bus (NATS or Kafka): ingestion completion, training-job completion, synthesis status updates.

## Data flow (end-to-end, simplified)

```
Literature / databases / ELN
       │
       ▼
ingestion ─► Bronze tier (object store)
       │
       ▼
chemoinformatic-core ─► Silver tier (PostgreSQL canonical)
       │
       ▼
model-training (Pillar 1) ─► Model registry (MLflow)
       │
       ▼
inference-api (real-time + batch)
       │
       ▼
agentic-orchestrator (Pillar 3) ─► web-ui ─► chemist
```

## Cross-cutting modules

All services share these libraries (Python workspace, single source of truth):

- `mbfinder.schemas` — Pydantic models for every cross-service entity.
- `mbfinder.chemoinformatic` — re-exported helpers from `chemoinformatic-core`.
- `mbfinder.observability` — OpenTelemetry config, structured logging.
- `mbfinder.auth` — OAuth helpers, JWT validation.
- `mbfinder.dataio` — DVC + object-store helpers.

## Testing strategy

- **Unit:** pytest in each service's `tests/` directory.
- **Integration:** docker-compose-backed integration tests in CI.
- **End-to-end:** Playwright (frontend) + REST contract tests (backend).
- **Scientific validation:** held-out test sets in `model-training/tests/scientific/`.

## Deployment topology

```
Production
├── 2 × API gateway pods (Cloudflare / NGINX Ingress)
├── 3 × web-ui pods
├── 3 × inference-api pods (CPU)
├── 1–4 × inference-api pods (GPU, autoscale)
├── 2 × ingestion workers
├── 2 × orchestrator pods
├── 1 × MLflow server pod
├── PostgreSQL primary + 1 replica (managed)
├── Redis cluster (3 nodes)
├── NATS / Kafka cluster (3 nodes)
└── Object store (S3 / Cloud Storage / MinIO)
```

Staging mirrors production at smaller scale; local dev runs everything single-instance via docker compose.

## Build matrix

| Service | Language | Container base | CI tests |
|---|---|---|---|
| chemoinformatic-core | Python 3.12 | python:3.12-slim + RDKit | pytest |
| ingestion | Python 3.12 | python:3.12-slim | pytest |
| model-training | Python 3.12 (CUDA 12.4) | nvidia/cuda:12.4-runtime + torch | pytest, scientific validation |
| inference-api | Python 3.12 (CPU + CUDA variants) | python:3.12-slim / nvidia/cuda | pytest, contract tests |
| agentic-orchestrator | Python 3.12 | python:3.12-slim | pytest, recording-replay |
| web-ui | TypeScript 5 / Node 20 | node:20-slim → nginx:alpine | vitest, playwright |

All container images are signed (cosign) and SBOM-tagged (syft).

## What to read next

- `adrs/` for major decision rationale.
- `services/*/README.md` for service-specific entry points.
- `../docs/` for the full proposal narrative.
