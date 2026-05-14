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

Adopt a multi-modal retrieval architecture composed of:

1. **Dense retrieval — BGE-M3** (open-source, multilingual, hybrid embeddings) as the default embedding model for text documents; fallback to OpenAI `text-embedding-3-large` when accuracy critical and data-sovereignty permits.
2. **Molecule retrieval — MolFormer-XL** or a pretrained MKANO encoder produces compound embeddings stored in pgvector alongside the relational record.
3. **Hybrid retrieval** combines BM25 (sparse) + BGE-M3 (dense) with reciprocal-rank fusion; reranking via **bge-reranker-v2** or Voyage rerank-2.
4. **GraphRAG over ElementKG+** (Microsoft, 2024) for queries that traverse the lab's compound-target-pathway knowledge graph. Particularly relevant for Design-agent reasoning ("which Pt complexes target proteins in the cisplatin-resistance signature?").
5. **Multimodal retrieval over chemistry figures** via **ColPali** (late-interaction retrieval on document images) + **MolScribe** (image-to-SMILES) — chemistry PDFs are often dominated by structural figures, not text.
6. **Contextual retrieval** (Anthropic, Sep 2024): prepend 50-100 token chunk-context summaries before embedding *and* before BM25 indexing. Anthropic's reported reductions in top-20-chunk retrieval failure: **35 %** (Contextual Embeddings alone), **49 %** (Contextual Embeddings + Contextual BM25), **67 %** (combined + reranking). One-time generation cost: $1.02 per million document tokens (Claude 3 Haiku + prompt caching). Recommended embedding models: Gemini Text 004, Voyage.
7. **Semantic caching** of orchestrator-issued queries via GPTCache or equivalent — orchestrator runs reuse retrieved evidence aggressively.

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
- ColPali / multimodal retrieval is operationally heavier than text-only — accepted for the chemistry value.

## Alternatives considered

- **OpenAI / Cohere embeddings as default.** Rejected on data sovereignty.
- **Pinecone / Weaviate / Qdrant.** Strong alternatives; deferred — pgvector inside Postgres reduces operational surface and is adequate for the lab's scale.
- **LanceDB on object storage.** Compelling for cold corpora; evaluated as Phase 3 option.
- **Naive RAG (no graph, no multimodal).** Rejected — leaves Pillar 2's KG investment unused.

## Revisit conditions

- BGE-M3 supplanted by a clearly better open embedding model.
- pgvector outscales (multi-billion vectors); migrate to LanceDB or Milvus.
- GraphRAG superseded by a successor pattern.
