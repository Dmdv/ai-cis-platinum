# ADR-002 — PostgreSQL + RDKit cartridge as canonical chemistry store

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** The system must index hundreds of thousands of compounds with sub-second substructure and similarity search. Chemistry-aware indexing is mandatory.

## Decision

Use PostgreSQL as the canonical relational store across the system, but **logically split into two independently-operated clusters** to preserve failure isolation between the operational chemistry data plane and the MLOps metadata plane. Enable the open-source RDKit PostgreSQL extension (the "RDKit cartridge") for substructure search, similarity (Tanimoto) queries, and molecular descriptor computations directly in the database engine.

### Logical split

| Logical cluster | Tables / extensions | Service consumers | Why this cluster |
| --- | --- | --- | --- |
| **operational-pg** | RDKit cartridge; `pg_trgm`; relational chemistry data (compounds, cell lines, assays); orchestrator campaign state (`campaign_state.persisted` JSONB); molecule pgvector embeddings | `chemoinformatic-core`, `inference-api`, `ingestion`, `agentic-orchestrator`, `web-ui` | The hot path. A downtime here means MB Finder v2 is down. |
| **mlops-pg**       | MLflow metadata; experiment-tracking; GraphRAG community summaries; large text pgvector embeddings (BGE-M3); training-job queue                                  | `model-training`, `retrieval-service`           | A downtime here pauses retraining and retrieval, but **does not bring down the user-facing MB Finder v2** — i.e. ADR-001's failure-isolation rationale survives at the data layer. |

Both clusters run the RDKit cartridge image so a chemistry query *can* be served from either; routing is by service. Backups, upgrades, and incident response are independent.

### Instance-split escalation triggers (when a logical cluster gets its own *physical* instance)

The two clusters start as separate logical schemas on a single managed PostgreSQL instance (cheapest viable shape). The cluster split graduates to **two physical instances** when ANY of the following triggers fire on the lab's Prometheus dashboard for 7 consecutive days:

1. **CPU**: > 70 % average on the combined instance.
2. **Lock contention**: > 100 lock-wait events per minute (`pg_locks` cumulative).
3. **Working set**: combined `shared_buffers` working set exceeds 75 % of the allocated memory.
4. **Disaster-recovery contention**: incident in one logical schema causes detectable degradation in the other (cross-schema spillover).

Each trigger raises a Slack alert; passing the threshold a second time over 7 days advances the trigger to the freeze-on-burn policy (`docs/06a_slo_register.md`) and provisions the second physical instance.

## Rationale

- The RDKit cartridge provides millisecond substructure search across hundreds of thousands of compounds — performance unattainable from application-layer scans.
- PostgreSQL is operationally well-understood, transactional, and supports both relational data and JSONB for flexible attributes.
- Same engine family serves general application data and chemistry-specific queries, reducing the operational surface.
- `pg_trgm` for fuzzy text search and `pgvector` for embeddings (NatQG, ChemFM, BGE-M3) can coexist in the same instance.
- **The logical split addresses the architecture-review finding that ADR-001's failure-isolation rationale was silently negated at the data layer.** Failures in retraining (mlops-pg) no longer take down the chemist-facing UI (operational-pg).

## Consequences

- PostgreSQL version and RDKit cartridge version must be compatible; CI tests this matrix per cluster.
- The cartridge ties us to a Postgres-specific extension; not portable to other RDBMS without rewriting queries. Accepted as a non-issue — Postgres is the standard.
- **Disaster-recovery procedure** (Phase-1 deliverable):
  1. PostgreSQL binary + RDKit cartridge `.so` + pgvector `.so` installed at the *same pinned versions* used in production.
  2. `pg_restore` of the cluster dump.
  3. `CREATE EXTENSION rdkit; CREATE EXTENSION vector;` smoke test.
  4. Substructure-index rebuild benchmarked (sub-100 ms typical query) before declaring restore complete.
- The two-logical-cluster pattern adds one extra connection pool per service; the operational cost is small but real (≈ +10 % memory per service).

## Alternatives considered

- **Single physical PostgreSQL with all schemas.** This was the prior-draft default; rejected because a PG-wide outage took down every service (ADR-001 failure-isolation negated).
- **MongoDB + RDKit application layer:** rejected — document database does not give us SQL joins to cell-line and assay tables that compound queries naturally require.
- **ChEMBL deployment as backend:** rejected — too much overhead, and we need write access for lab data.
- **Vector-only stores (Pinecone, Weaviate):** considered for embeddings; rejected as primary store because substructure search remains the chemistry-first access pattern. pgvector inside Postgres covers embeddings adequately.
- **Per-service physical PG instance from day 1.** Rejected on cost — academic-budget operations cannot afford 5 managed-PG instances. The logical-split-with-triggers compromise lets the lab grow physical instances on demand.
