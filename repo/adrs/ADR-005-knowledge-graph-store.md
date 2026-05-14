# ADR-005 — Knowledge graph: Neo4j Community Edition, with Apache AGE evaluation in Phase 3

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted (provisionally).
**Date:** 2026-05-14.
**Context:** Pillar 2 introduces ElementKG+, a unified knowledge graph linking compounds, cell lines, proteins, pathways, and the host lab's internal experiments. The store choice has long-term implications for query expressiveness, operational simplicity, and cost.

## Decision

Bootstrap and operate on **Neo4j Community Edition** through the full Phases 1–3 of the proposed roadmap. Evaluate **Apache AGE** (PostgreSQL graph extension; openCypher-compatible) in **Phase 3** against measurable performance and coverage gates before any migration is committed.

(Prior drafts named "PostgreSQL + `pg_graph`" as the migration target. There is no production-grade PostgreSQL extension called `pg_graph`; the realistic openCypher-on-Postgres option is Apache AGE — currently incubating, with documented Cypher-coverage gaps vs Neo4j. The decision is therefore *not* to migrate by default, but to evaluate AGE only when concrete thresholds are met.)

## Rationale

- Neo4j Community's Cypher gives the team an immediate, productive graph-query surface; iteration speed is critical for Phases 1–2.
- Cypher is well-documented and chemistry-KG examples are widely available.
- Neo4j Community Edition is free for non-clustered single-instance use, sufficient for the academic scale (≤ 1 B node-relationships) the proposal expects.
- Apache AGE is the *only* serious Postgres-native graph extension as of 2026; alternatives like `pg_graph` are not real production extensions. AGE's openCypher coverage is improving but still trails Neo4j Cypher on traversal performance and procedure-call surface.
- Operating two databases (Postgres + Neo4j) is a real tax. The honest position is that the tax is acceptable for Phases 1–3 because the per-query developer-productivity gain on Cypher exceeds the operational overhead; the migration option exists but is gated.

## Consequences

- Two databases during the entire proposed roadmap.
- Neo4j Community licensing limits the lab to single-instance operation (no clustering); HA is via PostgreSQL-style backup / restore drills, not native clustering.
- AGE migration is contingent on measurable Phase-3 evaluation passing the gates below.
- If AGE evaluation fails, the host lab stays on Neo4j Community indefinitely or upgrades to Neo4j Enterprise at the appropriate licensing cost.

## Alternatives considered

- **Postgres + recursive CTEs:** rejected — too verbose for chemist-readable queries; Cypher's pattern matching is qualitatively better for KG work.
- **Amazon Neptune / managed graph:** rejected — vendor lock-in; cost; not on-prem-deployable for data-sovereignty requirements.
- **TigerGraph, Memgraph:** considered; Memgraph is interesting but smaller community; Neo4j Community remains the safe default.
- **GraphQL-only abstraction over Postgres:** rejected — covers some access patterns but not the graph traversal use cases (e.g. "compounds within 3 hops of COL3A1 in the protein interaction graph").

## Revisit conditions (AGE migration gate — Phase 3)

Migration from Neo4j to Apache AGE is committed *only* if **all** of the following measurable gates pass on the host lab's ElementKG+ schema with Phase-3-realistic data volume:

1. **Traversal latency.** Sub-100 ms p95 on a representative 3-hop chemistry traversal benchmark ("compounds within 3 hops of a protein target in the cisplatin-resistance signature").
2. **Cypher coverage.** All Cypher patterns used in production (path-finding, list comprehensions, named subqueries, OPTIONAL MATCH chains, APOC-equivalent procedures) have AGE-supported equivalents.
3. **Operational overhead.** Replication, backup, and version-upgrade procedures on AGE are no worse than Neo4j Community.
4. **Migration cost.** Query-rewrite effort across all production Cypher (chemoinformatic, retrieval, agentic-orchestrator) is bounded at ≤ 2 weeks of platform-engineer effort.

If any gate fails at Phase-3 evaluation, the host lab stays on Neo4j. The migration option remains open in a future round but is not committed by this ADR.
