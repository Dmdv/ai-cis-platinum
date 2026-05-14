# MB Finder v2 — Skeleton Repository

This is the architectural skeleton of the proposed MB Finder v2 platform. It is **not** a working implementation — no business logic is provided. The repository's purpose is to demonstrate that the design described in `../docs/` materialises into concrete services with well-defined contracts.

Each service directory contains:

- `pyproject.toml` (or `package.json` for JS) — declares the package and pinned dependencies.
- `Dockerfile` — container build recipe.
- `README.md` — service-specific overview.
- `src/` — module stubs with type signatures and docstrings.
- `tests/` — test file stubs.

ADRs (architectural decision records) live in `adrs/`. They capture the rationale for major choices that will need to be revisited.

## Repository layout

```
repo/
├── README.md                       ← this file
├── ARCHITECTURE.md                 ← high-level architecture entry point
├── pyproject.toml                  ← workspace-level Python config
├── Dockerfile                      ← multi-stage build template (extended per service)
├── docker-compose.yml              ← local dev orchestration
├── adrs/
│   ├── ADR-001-microservices.md
│   ├── ADR-002-postgresql-rdkit-cartridge.md
│   ├── ADR-003-mkano-backbone-strategy.md
│   ├── ADR-004-langgraph-orchestrator.md
│   ├── ADR-005-knowledge-graph-store.md
│   └── ADR-006-mlflow-model-registry.md
├── services/
│   ├── chemoinformatic-core/       ← metal-extended RDKit (Pillar 2)
│   ├── ingestion/                  ← data pipelines (Pillar 4)
│   ├── model-training/             ← MKANO+ + foundation-model training (Pillars 1, 4)
│   ├── inference-api/              ← FastAPI prediction endpoints (Pillars 1, 4)
│   ├── agentic-orchestrator/       ← LangGraph DMTA loop (Pillar 3)
│   └── web-ui/                     ← Next.js front-end (Pillar 4)
└── infra/
    ├── terraform/                  ← cloud infrastructure as code
    ├── kubernetes/                 ← K8s manifests / Helm charts
    └── docker/                     ← shared base images
```

## What works locally

If you `docker compose up` the stack, you get:

- PostgreSQL with RDKit cartridge.
- Redis cache.
- MinIO (S3-compatible object store).
- MLflow server (file-backed for local development).
- Stubs of every microservice with `/health` endpoints.

You do **not** get any AI inference, ingestion, or orchestration — those are the components the implementation roadmap delivers.

## Build (skeleton only)

```bash
# Python services
uv sync                    # workspace-level dep resolution

# JS services
pnpm install               # in services/web-ui

# Local infra
docker compose up -d       # background services

# Health check
curl localhost:8001/health  # chemoinformatic-core
curl localhost:8002/health  # inference-api
curl localhost:8003/health  # ingestion
curl localhost:8004/health  # orchestrator
```

## Why a skeleton, not a working demo

A working demo would require:

1. Acquiring the 3,725 Pt compound dataset from the lab.
2. Training MKANO on internal hardware (cost ~ US $1–2 K).
3. Setting up production credentials for external APIs.

Each of those steps is conditional on the lab accepting the proposal. The skeleton demonstrates *engineering capability* without committing to work that has not yet been authorised.

A working slice will be delivered immediately in Phase 1, milestone 3 of the roadmap (`../docs/08_implementation_roadmap.md`).
