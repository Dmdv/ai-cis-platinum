# ADR-001 — Polyglot microservices over monolith

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)


**Status:** Accepted (skeleton design).
**Date:** 2026-05-14.
**Context:** MB Finder v2 must support multiple workloads (web UI, ML inference, agentic orchestration, data ingestion) with different scaling characteristics. The MKANO source code is currently a research monolith.

## Decision

Decompose the system into seven loosely coupled services along bounded-context boundaries (chemoinformatic, ingestion, training, inference, orchestrator, UI, reporting). Use HTTP/JSON for public interfaces, gRPC internally where latency-critical, NATS/Kafka for async coordination.

## Rationale

- ML inference and web UI scale independently from ingestion or training; a monolith forces the worst-case GPU resourcing on every component.
- Different services can use different runtimes (Python for ML, Node for UI) without coupling.
- Multiple developers (or a single developer at different times) can iterate on services without merge friction.
- Failure isolation: an agentic-orchestrator outage does not kill the public MB Finder UI.

## Consequences

- Operational complexity is higher than a monolith. Mitigated by shared base images, shared observability stack, and a workspace-level package manifest.
- Local development requires docker compose — the orchestration is explicit, not implicit.
- Distributed-system failure modes (partial failures, eventual consistency) must be considered. Mitigated by explicit retry / circuit-breaker patterns and idempotent operations.

## Alternatives considered

- **Pure monolith:** rejected — does not scale across the diverse workloads.
- **Modular monolith:** considered seriously; rejected because the GPU/CPU resource asymmetry is real and dominant.
- **Function-as-a-service / serverless-first:** rejected — cold-start latency unacceptable for inference; vendor lock-in concerns.
