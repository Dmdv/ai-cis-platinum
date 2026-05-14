# ADR-010 — Retrieval architecture: hybrid dense + BM25 + GraphRAG + multimodal

**Contents**

- [Decision](#decision)
- [Storage](#storage)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** A multi-agent chemistry orchestrator (Pillar 3) with literature mining, ELN integration, and a knowledge graph (Pillar 2) needs a serious retrieval stack. A pgvector-only retrieval surface is insufficient for a 2026 chemistry system: it covers neither sparse (BM25) signals, nor knowledge-graph traversal, nor multi-modal retrieval of structural figures in chemistry PDFs.

## Decision

Adopt a multi-modal retrieval architecture with **phased rollout** — Phase 1 ships a small, defensible baseline, and the heavier-cost components (GraphRAG, ColPali) graduate on measurable gates.

### Phase-1 baseline (Must)

1. **Dense retrieval — BGE-M3** (open-source, multilingual, hybrid embeddings) as the default embedding model for text documents. BGE-M3 already produces dense + sparse + multi-vector signals; the proposal uses it in hybrid mode rather than running separate dense and sparse indices.
2. **Hybrid retrieval** combines BM25-style sparse + BGE-M3 dense with reciprocal-rank fusion; reranking via **bge-reranker-v2**.
3. **Molecule retrieval — MolFormer-XL** or a pretrained MKANO encoder produces compound embeddings stored in pgvector alongside the relational record.
4. **Contextual retrieval** (Anthropic, Sep 2024): prepend 50-100 token chunk-context summaries before embedding and before BM25 indexing. Anthropic's reported reductions in top-20-chunk retrieval failure: **35 %** (Contextual Embeddings alone), **49 %** (Contextual Embeddings + Contextual BM25), **67 %** (combined + reranking). One-time generation cost: $1.02 per million document tokens (Claude 3 Haiku + prompt caching).
5. **Semantic caching** of orchestrator-issued queries via GPTCache or equivalent.
6. **Sub-200K-token short-cut.** For narrow corpora (host-lab publication list, SOP collection, 19 PlatinAI-era compounds), skip retrieval entirely and load the corpus into the prompt with prompt caching, per Anthropic's recommendation. This bypass is cheaper *and* higher recall than retrieval for small fixed corpora.

### Phase-2 / Phase-3 graduations (gated, not committed by default)

7. **GraphRAG over ElementKG+** — promote to Phase 2 only when (a) ElementKG+ schema is stable for ≥ 3 months (per ADR-005's stability gate), and (b) at least 30 % of Design-agent queries are *traversal queries* (e.g. "compounds within N hops of target X") rather than text-retrieval queries. Until then, traversal queries are answered with direct Cypher / SQL over Neo4j; community-summary materialisation is not built.
8. **Multimodal retrieval over chemistry figures** via **ColPali** + **MolScribe** — promote to Phase 2 only when the Phase-1 text-retrieval failure-rate analysis shows that figure-only / structure-only PDF content is the limiting failure mode. ColPali is operationally heavier (PLAID / Vespa index, GPU embedding); not paying that cost until it pays for itself.
9. **OpenAI `text-embedding-3-large` fallback** — available as a non-default option for high-accuracy needs where data-sovereignty permits (rare).

## Storage

- **Text + molecule embeddings:** pgvector (same Postgres instance as the relational store; ADR-002).
- **Late-interaction (ColBERT/ColPali) indices:** dedicated PLAID or Vespa index.
- **GraphRAG community summaries:** materialised in PostgreSQL JSONB; refreshed weekly.

## Rationale

- **Hybrid retrieval beats either pure mode** on chemistry corpora — common knowledge among practitioners (Maarten Grootendorst, Anthropic engineering posts).
- **GraphRAG is the right fit for the ElementKG+ knowledge graph.** The KG is built in Pillar 2 (ADR-005); using it only for SQL queries leaves most of its value unrealised.
- **Multimodal retrieval is non-optional for chemistry PDFs.** Structures in figures cannot be retrieved by text embeddings alone.
- **BGE-M3 self-hosted aligns with Component 3.2.1's data-sovereignty argument.** A frontier embedding API would leak pre-publication compound names and structures.

## Consequences

- A new `retrieval-service` bounded context joins the service catalogue (added to `ARCHITECTURE.md`).
- Embedding pipelines must be re-run when models update; managed as a feature-store materialisation job.
- Phase-1 retrieval surface is **two pieces** (BGE-M3 hybrid + reranker, contextual chunking). GraphRAG and ColPali graduate only on their quantitative gates — keeps the Phase-1 ops burden small.
- ColPali / multimodal retrieval is operationally heavier than text-only and is gated; the cost is paid only when the failure-mode analysis justifies it.

## Alternatives considered

- **OpenAI / Cohere embeddings as default.** Rejected on data sovereignty.
- **Pinecone / Weaviate / Qdrant.** Strong alternatives; deferred — pgvector inside Postgres reduces operational surface and is adequate for the lab's scale.
- **LanceDB on object storage.** Compelling for cold corpora; evaluated as Phase 3 option.
- **Naive RAG (no graph, no multimodal).** Rejected — leaves Pillar 2's KG investment unused.

## Revisit conditions

- BGE-M3 supplanted by a clearly better open embedding model.
- pgvector outscales (multi-billion vectors); migrate to LanceDB or Milvus.
- GraphRAG superseded by a successor pattern.
