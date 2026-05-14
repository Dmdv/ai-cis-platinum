# `chemoinformatic-core` — service interface contract

**Contents**

- [Public endpoints](#public-endpoints)
- [Wire contract](#wire-contract)
- [Latency budget](#latency-budget)
- [Error semantics](#error-semantics)
- [Idempotency](#idempotency)
- [Resilience](#resilience)
- [SLO and dependent timeouts](#slo-and-dependent-timeouts)


This file is the **single source of truth for how external callers interact with the chemoinformatic-core service**. It is the Phase-1 deliverable mandated by the architecture-reviewer finding C12; every other service in the system ships an analogous `INTERFACE.md` (the templates are the same shape).

## Public endpoints

| Method | Path | Purpose | Stability |
| --- | --- | --- | --- |
| POST | `/api/v1/sanitize` | Sanitize one SMILES; return canonical metal-aware graph + optional NatQG features. | Stable |
| POST | `/api/v1/sanitize/batch` | Batched variant (≤ 1 000 per request). | Stable |
| GET  | `/api/v1/metals` | List the metal symbols with a registered sanitization strategy. | Stable |
| POST | `/api/v1/drug-likeness` | Apply the modified-Lipinski filter to a sanitized complex. | Stable |
| GET  | `/health` | Liveness probe; returns `{"status":"ok","schema_version":1}`. | Stable |

## Wire contract

All request and response bodies are JSON. Schemas are defined in `src/schemas.py` and exposed at `GET /api/v1/openapi.json` (OpenAPI 3.1). The `SCHEMA_VERSION` constant in `schemas.py` is the wire-contract version; consumers MUST check the `Schema-Version` HTTP response header on every response.

**Cross-service boundary discipline.** RDKit `Chem.Mol` types are **never** exposed across this service's boundary. Only the serializable Pydantic models in `schemas.py` (e.g. `SanitizedComplex`, `MolecularGraph`, `NatQGFeatures`) cross the boundary.

## Latency budget

| Endpoint | p50 target | p95 SLO | p99 SLO | Hard timeout |
| --- | --- | --- | --- | --- |
| `/sanitize` | 50 ms | **200 ms** | 500 ms | 2 s |
| `/sanitize/batch` (n=1 000) | 2 s | 5 s | 10 s | 30 s |
| `/metals` | 5 ms | 20 ms | 50 ms | 200 ms |
| `/drug-likeness` | 20 ms | 100 ms | 200 ms | 1 s |
| `/health` | 1 ms | 5 ms | 10 ms | 100 ms |

These budgets reconcile the three latency numbers previously scattered across `docs/02`, `docs/06`, and `repo/adrs/ADR-008`; the per-endpoint p95 SLO is authoritative.

## Error semantics

| Status | Meaning | Retry-safe? |
| --- | --- | --- |
| `200` | Sanitization succeeded. | n/a |
| `400 Bad Request` | SMILES is malformed or fails RDKit parse. | **No** — same input will fail again. |
| `422 Unprocessable Entity` | No sanitization strategy registered for the requested metal. | **No** — same metal will fail again. |
| `429 Too Many Requests` | Rate limit hit. Response includes `Retry-After` header. | **Yes** — back off and retry. |
| `500 Internal Server Error` | Unexpected error (likely an RDKit crash or storage issue). | **Yes** — single retry recommended. |
| `501 Not Implemented` | Endpoint or feature scoped to a later phase. | **No**. |
| `503 Service Unavailable` | Service degraded; consult `/health`. | **Yes** — back off and retry. |

Every error response is a JSON object: `{"error": {"code": "...", "message": "...", "request_id": "..."}}` so logs can be correlated by `request_id`.

## Idempotency

`/sanitize` and `/drug-likeness` are **naturally idempotent** (pure functions of input). Repeated requests with the same body return the same response; no idempotency key is required.

`/sanitize/batch` is also idempotent at the result level (same batch in → same batch out), though intermediate side-effects (e.g. populating the curation queue for ambiguous metals) deduplicate by `(inchi_key, request_id)`.

## Resilience

| Property | Phase-1 commitment |
| --- | --- |
| Replicas | KServe `minReplicas: 2`, `maxReplicas: 8` (paged tier per `docs/06a_slo_register.md`). |
| Circuit breaker | Outbound call to `inference-api` and `retrieval-service` wrapped in a 3-second timeout + 5-failure circuit-breaker (Hystrix-style; resilience4j or similar). |
| Retry budget | At most 1 retry per outbound call; further failures surface to the caller. |
| Graceful degradation | If pgvector is unavailable, NatQG geometry features are omitted from the response and a `Warning:` header signals the degradation. |
| Health check | Liveness via `/health`; readiness gated on Postgres + RDKit cartridge handshake. |

## SLO and dependent timeouts

Service-level objectives are tracked in `docs/06a_slo_register.md`. Callers that depend on this service should configure their dependent-timeout budgets accordingly:

- Callers requiring strong latency guarantees (e.g. the public web UI) should set a 500 ms timeout to `/sanitize` and either retry once or surface a friendly error to the user.
- Callers in the orchestrator's fan-out screen (e.g. the Design agent's 5,124-call sweep via the MCP code-execution block) should set a 2 s timeout per item and parallelize aggressively; the timeout chosen here exceeds p99 SLO with margin.

---

*This file uses the canonical INTERFACE.md template. The other services ship analogous files: `inference-api/INTERFACE.md`, `agentic-orchestrator/INTERFACE.md`, etc. The platform engineer drafts those alongside their respective Phase-1 milestones.*
