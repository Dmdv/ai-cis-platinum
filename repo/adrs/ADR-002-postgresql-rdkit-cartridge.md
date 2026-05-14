# ADR-002 — PostgreSQL + RDKit cartridge as canonical chemistry store

**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** The system must index hundreds of thousands of compounds with sub-second substructure and similarity search. Chemistry-aware indexing is mandatory.

## Decision

Use PostgreSQL as the canonical relational store. Enable the open-source RDKit PostgreSQL extension (the "RDKit cartridge") for substructure search, similarity (Tanimoto) queries, and molecular descriptor computations directly in the database engine.

## Rationale

- The RDKit cartridge provides millisecond substructure search across hundreds of thousands of compounds — performance unattainable from application-layer scans.
- PostgreSQL is operationally well-understood, transactional, and supports both relational data and JSONB for flexible attributes.
- Same database serves general application data and chemistry-specific queries, reducing the operational surface.
- `pg_trgm` for fuzzy text search and `pgvector` for embeddings (NatQG, ChemFM) can coexist in the same instance.

## Consequences

- PostgreSQL version and RDKit cartridge version must be compatible; CI tests this matrix.
- The cartridge ties us to a Postgres-specific extension; not portable to other RDBMS without rewriting queries. Accepted as a non-issue — Postgres is the standard.
- Backups must include the RDKit cartridge extension state (handled by standard pg_dump).

## Alternatives considered

- **MongoDB + RDKit application layer:** rejected — document database does not give us SQL joins to cell-line and assay tables that compound queries naturally require.
- **ChEMBL deployment as backend:** rejected — too much overhead, and we need write access for lab data.
- **Vector-only stores (Pinecone, Weaviate):** considered for embeddings; rejected as primary store because substructure search remains the chemistry-first access pattern. pgvector inside Postgres covers embeddings adequately.
