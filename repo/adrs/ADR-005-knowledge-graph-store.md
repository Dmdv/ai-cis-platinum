# ADR-005 — Knowledge graph: Neo4j first, with migration path to Postgres + pg_graph

**Status:** Accepted (provisionally).
**Date:** 2026-05-14.
**Context:** Pillar 2 introduces ElementKG+, a unified knowledge graph linking compounds, cell lines, proteins, pathways, and the lab's internal experiments. The store choice has long-term implications for query expressiveness, operational simplicity, and cost.

## Decision

Bootstrap with Neo4j Community Edition during Phases 1–2. Plan a migration to PostgreSQL + `pg_graph` (or equivalent SQL-graph extension) in Phase 3 once the schema stabilises.

## Rationale

- Neo4j's Cypher gives the team an immediate, productive graph query language; iteration speed is critical in the early prototyping phase.
- Cypher is well-documented and chemistry-oriented examples are widely available.
- Neo4j Community Edition is free for non-clustered use, sufficient for the academic scale.
- Long-term, operating two databases (Postgres + Neo4j) is a tax. Once schema is stable, migrating to a Postgres-native graph extension reduces operational surface.

## Consequences

- Two databases during the early phase.
- Migration will require rewriting queries to SQL-graph dialect (or a Cypher-compatible Postgres extension if it matures).
- Operational support for Neo4j (backups, upgrades) needs to be in place.

## Alternatives considered

- **Postgres + recursive CTEs:** rejected as initial choice — too verbose for chemist-readable queries; Cypher's pattern matching is qualitatively better for KG work.
- **Amazon Neptune / managed graph:** rejected — vendor lock-in; cost.
- **TigerGraph, Memgraph:** considered; Memgraph is interesting but smaller community; Neo4j remains the safe default.
- **GraphQL-only abstraction over Postgres:** rejected — covers some access patterns but not the graph traversal use cases (e.g. "compounds within 3 hops of COL3A1 in the protein interaction graph").

## Revisit conditions

- Phase 3 schema is stable for ≥3 months.
- A PostgreSQL graph extension passes performance and query-expressiveness bar for our KG workload.
- Operational cost of Neo4j becomes material.
