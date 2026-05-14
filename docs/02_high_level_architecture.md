# 02 — High-Level Architecture

**Contents**

- [System overview](#system-overview)
- [Pillar mapping](#pillar-mapping)
- [Component inventory](#component-inventory)
- [Retrieval and embedding layer](#retrieval-and-embedding-layer)
- [Cross-cutting concerns](#cross-cutting-concerns)
- [Architectural style](#architectural-style)
- [Why this shape](#why-this-shape)
- [Component diagrams](#component-diagrams)


## System overview

MB Finder v2 is a multi-metal, geometry-aware, agent-orchestrated, production-grade AI drug-discovery platform. It is organised as a set of loosely coupled services around a shared chemoinformatic core, a shared data lake, and a shared model registry. Four functional pillars sit on top of this shared infrastructure.

```
+----------------------------------------------------------------------+
|                   PRESENTATION LAYER                                 |
|  MB Finder web UI  |  REST/GraphQL API  |  Agentic chat interface   |
+----------------------------------------------------------------------+
|                   ORCHESTRATION LAYER (PILLAR 3)                     |
|        LLM-driven DMTA scheduler   +   agent registry                |
+----------------------------------------------------------------------+
|              MODEL LAYER (PILLAR 1, PILLAR 2)                        |
|   geometry-aware GNN  |  AF3/Boltz-2  |  generative diffusion        |
|   MKANO+ classifier   |  ChemFM fine-tunes  |  multi-omics MoA       |
+----------------------------------------------------------------------+
|              CHEMOINFORMATIC CORE (PILLAR 2)                         |
|     metal-extended RDKit (Pt/Au/Cu/Re/Ru/Pd) | NatQG geometry        |
|     fragment library / combinatorial generator                       |
+----------------------------------------------------------------------+
|              DATA LAYER (PILLAR 4)                                   |
|   PostgreSQL + RDKit cartridge  | object store | feature store       |
|   Redis cache  |  message bus  |  experiment tracking (MLflow)       |
+----------------------------------------------------------------------+
|              PLATFORM LAYER (PILLAR 4)                               |
|   K8s, observability, CI/CD, model registry, secret management       |
+----------------------------------------------------------------------+
```

## Pillar mapping

| Pillar | Primary deliverable | Lab's gap closed |
|---|---|---|
| 1. AI modernization | Geometry-aware ML, AF3 target-aware design, foundation-model fine-tuning, generative diffusion | Gaps 1 (geometry blindness), 2 (target blindness) |
| 2. Multi-metal + adjacent science | Generalised metal sanitization, multi-omics MoA, cross-project knowledge graph | Gap 3 (metal-specific over-fitting), plus latent value in linking lab's parallel projects |
| 3. Agentic DMTA orchestration | LLM-coordinated Design–Make–Test–Analyze loop | Gap 4 (manual orchestration) |
| 4. MLOps and backend | CI/CD, model registry, FAIR data, observability, scalable inference | Gap 5 (research-grade infrastructure) |

## Component inventory

The system decomposes into seven services and three shared platforms. The skeleton repository at `repo/services/` mirrors this decomposition.

### Services

1. **`chemoinformatic-core`** — the metal-extended RDKit + NatQG geometry layer. Single source of truth for "what is a valid Pt/Au/Cu/Re/Ru/Pd complex graph". Used by every downstream service.
2. **`ingestion`** — extracts SMILES + cytotoxicity from literature, databases (ChEMBL, PubChem, CSD), and ELN exports. Includes the curation queue + reviewer UI.
3. **`model-training`** — training jobs for MKANO+ classifiers, geometry-aware GNNs, foundation-model fine-tunes, and generative diffusion. Tracked end-to-end in MLflow.
4. **`inference-api`** — synchronous and asynchronous prediction endpoints (single-molecule, batch, structure-aware). FastAPI gateway routing to the three-tier serving stack (KServe for small classifiers; vLLM v1 + AWQ for LLMs; custom batch service for AF3 / Boltz-2). See ADR-008 for the full stack.
5. **`agentic-orchestrator`** — LangGraph-style multi-agent service driving DMTA. Tool surface: every other service in the system, plus external services (literature search, ELN, structure prediction).
6. **`web-ui`** — the public MB Finder front-end (Next.js or React + RDKit JS). **Publication-ready figures, tables, and candidate dossiers** are rendered by routes inside `web-ui` (the earlier draft listed a separate `reporting` service; that decomposition didn't earn its keep — folded into web-ui until reporting has a distinct bounded context worth a service split).
7. **`mcp-code-runner`** — sandbox runtime that hosts MCP code-execution blocks emitted by the Design / Analysis agents. Pyodide-based for Phase-1; gVisor + CPython graduation in Phase-2/3 when native binaries are required. See ADR-013 for the full decision.

### Shared platforms

1. **Data lake + feature store** — versioned chemical and biological data; Parquet / Iceberg + Feast or equivalent.
2. **Model registry** — MLflow registry of trained checkpoints, with lineage to training data versions.
3. **Knowledge graph (ElementKG+)** — extended periodic-table + functional-group + protein-target knowledge graph; Neo4j or Postgres-pgvector hybrid.
4. **Retrieval and embedding layer** — hybrid dense + sparse retrieval over the host lab's literature, ELN, and knowledge graph (see below).

## Retrieval and embedding layer

A chemistry orchestrator with literature mining, ELN integration, and a knowledge graph needs a serious retrieval substrate — not just a vector column tacked onto Postgres. The proposal therefore introduces a dedicated retrieval layer with four complementary components (full design in ADR-010):

- **Text retrieval — BGE-M3 (self-hosted)** as the default dense embedding model for literature, ELN entries, and assay protocols. Hybrid with BM25 sparse retrieval and reciprocal-rank fusion; reranking via bge-reranker-v2. OpenAI `text-embedding-3-large` is a non-default fallback when accuracy is critical and data-sovereignty constraints permit (see Pillar 3 Component 3.2.1).
- **Molecule retrieval — MolFormer-XL or pretrained MKANO encoder embeddings**, stored in pgvector alongside the relational compound record. Enables semantic search over the 3,725 curated Pt complexes and the 214,373 unlabeled corpus.
- **GraphRAG over ElementKG+** (Microsoft, 2024) for traversal queries — "find all compounds in the portfolio that target proteins in the cisplatin-resistance signature" — using a vector index over knowledge-graph community summaries, materialised weekly.
- **Multimodal retrieval over chemistry figures** via ColPali (late-interaction retrieval on document images) combined with MolScribe / RxnScribe (image-to-SMILES). Chemistry PDFs are figure-dominated; text-only retrieval misses most of the structural content.

Beyond raw retrieval, the layer ships **contextual chunking** (Anthropic, *Introducing Contextual Retrieval*, September 2024) and **semantic caching** (GPTCache or equivalent) so orchestrator-issued queries reuse retrieved evidence across DMTA steps.

Anthropic's reported numbers on their internal benchmark are the load-bearing justification for this layer:
- **Contextual Embeddings alone reduce the top-20-chunk retrieval failure rate by 35 %** (5.7 % → 3.7 %).
- **Contextual Embeddings + Contextual BM25 combined reduce failure rate by 49 %** (5.7 % → 2.9 %).
- **With reranking added, total reduction reaches 67 %**.

Implementation cost: prepend a 50–100 token chunk-specific context (generated by a small fast LLM via prompt caching) before embedding and BM25 indexing. Anthropic's reported one-time cost: **US $1.02 per million document tokens** when using Claude 3 Haiku + prompt caching. Effective embedding models on their benchmark: **Gemini Text 004** and **Voyage**. The lab's chemistry corpus is a particularly good fit for contextualisation — a chunk that reads *"the resulting complex showed IC50 of 1.5 µM"* is uninterpretable without the chunk-context preamble (*"This chunk is from a 2024 study on a Pt(II) NHC complex tested in A2780cis cells at 72 h…"*) — exactly the failure mode Anthropic describes for SEC filings.

For knowledge bases smaller than 200K tokens (≈500 pages), Anthropic's own recommendation applies: skip RAG entirely and load the corpus directly into the prompt with prompt caching. Several narrow knowledge bases (e.g. the host lab's own publication list, the SOP collection, the 19 PlatinAI-era compounds and their assays) fit comfortably under that bound and bypass the retrieval layer entirely.

This layer is exposed to the orchestrator's agents through MCP servers (see Pillar 3 Component 3.4.1) so any MCP client — including a chemist's personal Claude Desktop — can query the host lab's literature and KG with the same retrieval guarantees.

## Cross-cutting concerns

| Concern | Implementation strategy |
|---|---|
| Reproducibility | Every experiment is a Git-tagged training config + dataset hash + model checkpoint + evaluation report, registered in MLflow. |
| FAIR data | Datasets carry persistent identifiers; schemas conform to community standards (Cellosaurus for cell lines, ChEBI for chemicals, UniProt for proteins). |
| Observability | OpenTelemetry across services; Grafana dashboards for inference latency, training success rate, data drift on ingestion. |
| Security | Read-only API keys for public users; signed JWTs for lab members; secrets via Vault or cloud KMS. |
| Cost control | Foundation-model inference cached aggressively (Redis); training jobs use spot instances; inference scales to zero outside business hours. |
| Lab compatibility | All public APIs are documented OpenAPI; SDKs in Python and JavaScript; chemists can use the web UI without touching code. |

## Architectural style

- **Polyglot microservices** with HTTP/JSON public interfaces and gRPC internal interfaces where latency matters (inference, agent tool calls).
- **Event-driven where useful** — model-training completions, ingestion-batch arrivals, and synthesis status updates are published to a message bus (NATS or Kafka) and consumed by the orchestrator.
- **Stateless services, stateful platforms** — every service is horizontally scalable; state lives only in PostgreSQL, the data lake, the message bus, or the model registry.
- **Reproducibility-first** — no model in production was trained on a dataset whose hash is not recorded; no experiment is published from results that cannot be rebuilt from a tagged commit.

## Why this shape

The architecture deliberately avoids two anti-patterns common in academic AI-drug-discovery code:

1. **The monolithic Jupyter notebook.** A single 5,000-line notebook that performs ingestion, sanitization, training, prediction, and figure generation is fast to write and slow to evolve. MB Finder v2 splits each concern into a service with a single clear contract, so the dataset team, the model team, and the orchestration team can iterate independently.
2. **The "research-only" deployment.** Code that runs only on the original author's laptop, with hard-coded paths and no environment lock, cannot be transferred. Every service in MB Finder v2 ships as a Docker image, lockfile-pinned, with a documented contract.

The trade-off is upfront engineering investment. This is precisely the investment that a multidisciplinary AI + backend + chemistry-engineering researcher is positioned to make and is the strongest justification for adding such a profile to the team.

## Component diagrams

Higher-resolution architecture diagrams are in `diagrams/`:

- `c4_context.mmd` — system context (users, external services).
- `c4_containers.mmd` — service-level architecture.
- `pillar1_ai.mmd` — model-layer detail.
- `pillar2_multimetal.mmd` — chemoinformatic-core detail.
- `pillar3_dmta.mmd` — agent loop and tool surface.
- `pillar4_mlops.mmd` — CI/CD, model registry, observability.
- `data_flow.mmd` — end-to-end dataflow from raw literature to candidate dossier.
