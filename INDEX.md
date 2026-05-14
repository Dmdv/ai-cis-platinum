# Document Index

Complete navigation of every document in this repository. Each file is linked; every long document also has its own table of contents at the top.

---

## Architecture documents (`docs/`)

The written proposal, ordered as it should be read.

| # | Path | Time | Contents |
| --- | --- | --- | --- |
| 00 | [`docs/00_executive_summary.md`](docs/00_executive_summary.md) | 5 min | Elevator pitch: the opportunity, four-pillar architecture, roadmap, risk posture, headline numbers (16× more potent than cisplatin). |
| 01 | [`docs/01_problem_and_context.md`](docs/01_problem_and_context.md) | 10 min | Systemic problem · AI-for-metallodrugs gap · contribution of the source paper · stated roadmap · opportunity gap analysis. |
| 02 | [`docs/02_high_level_architecture.md`](docs/02_high_level_architecture.md) | 15 min | System overview · pillar mapping · 7-service component inventory · retrieval & embedding layer · cross-cutting concerns · architectural style. |
| 03 | [`docs/03_pillar1_ai_modernization.md`](docs/03_pillar1_ai_modernization.md) | 15 min | Geometry-aware ML (NatQG + SE(3)-equivariant) · AF3 / Boltz-2 target conditioning · ChemFM foundation backbone · equivariant-diffusion generative · PEFT decision matrix. |
| 04 | [`docs/04_pillar2_multimetal.md`](docs/04_pillar2_multimetal.md) | 15 min | Strategy-pattern metal-extended sanitization (Pt/Au/Cu/Re/Ru/Pd) · multi-metal MKANO+ · multi-omics MoA inference · ElementKG+ knowledge graph. |
| 05 | [`docs/05_pillar3_agentic_dmta.md`](docs/05_pillar3_agentic_dmta.md) | 15 min | Six-role agent decomposition (Supervisor + 5 specialists) · orchestration architecture · example campaign walkthrough · tool surface contracts · integration with ELN / LIMS. |
| 06 | [`docs/06_pillar4_mlops_backend.md`](docs/06_pillar4_mlops_backend.md) | 15 min | Reproducible training · three-tier inference serving · CI/CD · observability · data engineering · FAIR data · cost envelope. |
| 07 | [`docs/07_data_architecture.md`](docs/07_data_architecture.md) | 10 min | Data domains · logical schema · medallion architecture (Bronze/Silver/Gold) · schema evolution · identifier strategy · data-quality monitoring. |
| 08 | [`docs/08_implementation_roadmap.md`](docs/08_implementation_roadmap.md) | 10 min | Phase 1 (months 0–6) · Phase 2 (6–12) · Phase 3 (12–18) · team composition · critical path · success metrics. |
| 09 | [`docs/09_risks_and_mitigations.md`](docs/09_risks_and_mitigations.md) | 5 min | 16 risks across technical / data / operational / scientific-reputational / strategic categories, each with mitigation. |
| 10 | [`docs/10_value_proposition.md`](docs/10_value_proposition.md) | 5 min | Skill–component matrix · where the combined background is decisive · adjacent expertise the platform engineer does not claim. |
| 11 | [`docs/11_references.md`](docs/11_references.md) | reference | ≈ 90 peer-reviewed papers · datasets · agent-framework docs · practitioner-press citations. |
| 12 | [`docs/12_dual_track_milestones.md`](docs/12_dual_track_milestones.md) | **20 min** | **Dual-track consolidation** · Track A (extend MKANO/MB Finder) + Track B (build next-gen platform) · 43-decision register · phase-by-phase milestones. |

---

## Architecture Decision Records (`repo/adrs/`)

Each ADR captures one durable architectural commitment. Standard sections: Status · Context · Decision · Rationale · Consequences · Alternatives · Revisit conditions.

| ADR | Path | Subject |
| --- | --- | --- |
| ADR-001 | [`repo/adrs/ADR-001-microservices.md`](repo/adrs/ADR-001-microservices.md) | Polyglot microservices over a monolith. |
| ADR-002 | [`repo/adrs/ADR-002-postgresql-rdkit-cartridge.md`](repo/adrs/ADR-002-postgresql-rdkit-cartridge.md) | PostgreSQL + RDKit cartridge + pgvector as the single store. |
| ADR-003 | [`repo/adrs/ADR-003-mkano-backbone-strategy.md`](repo/adrs/ADR-003-mkano-backbone-strategy.md) | MKANO retained as primary; ChemFM as secondary opinion. |
| ADR-004 | [`repo/adrs/ADR-004-langgraph-orchestrator.md`](repo/adrs/ADR-004-langgraph-orchestrator.md) | LangGraph for the agentic-DMTA orchestrator state machine. |
| ADR-005 | [`repo/adrs/ADR-005-knowledge-graph-store.md`](repo/adrs/ADR-005-knowledge-graph-store.md) | Neo4j initially; migrate to pg-graph in Phase 3. |
| ADR-006 | [`repo/adrs/ADR-006-mlflow-model-registry.md`](repo/adrs/ADR-006-mlflow-model-registry.md) | MLflow as model registry + experiment tracker. |
| ADR-007 | [`repo/adrs/ADR-007-mcp-tool-surface.md`](repo/adrs/ADR-007-mcp-tool-surface.md) | MCP as the canonical tool-surface protocol. |
| ADR-008 | [`repo/adrs/ADR-008-inference-serving-stack.md`](repo/adrs/ADR-008-inference-serving-stack.md) | Three-tier inference serving (KServe / vLLM v1 + AWQ / custom batch). |
| ADR-009 | [`repo/adrs/ADR-009-fine-tuning-methodology.md`](repo/adrs/ADR-009-fine-tuning-methodology.md) | bf16 = DoRA + rsLoRA; 4-bit = LoftQ; GRPO for RL post-training. |
| ADR-010 | [`repo/adrs/ADR-010-retrieval-architecture.md`](repo/adrs/ADR-010-retrieval-architecture.md) | Hybrid BGE-M3 + BM25 + GraphRAG + ColPali multimodal retrieval. |
| ADR-011 | [`repo/adrs/ADR-011-skill-curation.md`](repo/adrs/ADR-011-skill-curation.md) | Skill curation as a first-class deliverable. |
| ADR-012 | [`repo/adrs/ADR-012-autonomy-level.md`](repo/adrs/ADR-012-autonomy-level.md) | Target autonomy L2 (Phase 1-2), L3 (Phase 3) per Evans & Desai. |

---

## Presentation deck (`slides/`)

| Path | Description |
| --- | --- |
| [`slides/presentation.md`](slides/presentation.md) | 22-slide Marp markdown deck — renders cleanly as github markdown and as a styled PDF via Marp CLI. |
| [`slides/marp-theme.css`](slides/marp-theme.css) | Arctic Frost theme — steel blue + ice blue + silver + crisp white palette, DejaVu Sans typography. |

To render the PDF:

```bash
npm i -g @marp-team/marp-cli
cd slides
marp --theme-set marp-theme.css presentation.md -o presentation.pdf
```

---

## Architecture diagrams (`diagrams/`)

Mermaid (`.mmd`) source files. See [`diagrams/README.md`](diagrams/README.md) for the inventory and rendering instructions.

| File | Description | Referenced in |
| --- | --- | --- |
| [`c4_context.mmd`](diagrams/c4_context.mmd) | C4 system context: users + external dependencies | docs/02 |
| [`c4_containers.mmd`](diagrams/c4_containers.mmd) | C4 container view: service decomposition | docs/02 |
| [`pillar1_ai.mmd`](diagrams/pillar1_ai.mmd) | Pillar 1 components — geometry-aware ML, foundation models, generative diffusion | docs/03 |
| [`pillar2_multimetal.mmd`](diagrams/pillar2_multimetal.mmd) | Pillar 2 components — strategy-pattern sanitization, multi-omics MoA | docs/04 |
| [`pillar3_dmta.mmd`](diagrams/pillar3_dmta.mmd) | Pillar 3 components — six-role agent model + tool surface | docs/05 |
| [`pillar4_mlops.mmd`](diagrams/pillar4_mlops.mmd) | Pillar 4 components — CI/CD, model registry, observability, data tiers | docs/06 |
| [`data_flow.mmd`](diagrams/data_flow.mmd) | End-to-end data flow: literature → candidate dossier | docs/07 |
| [`dmta_campaign_example.mmd`](diagrams/dmta_campaign_example.mmd) | Worked example DMTA campaign (Au(III) hit-to-lead) | docs/05 |
| [`dual_track_gantt.mmd`](diagrams/dual_track_gantt.mmd) | 18-month Gantt: Track A + Track B milestones | docs/12 |
| [`resource_allocation_pie.mmd`](diagrams/resource_allocation_pie.mmd) | Phase 1 effort split (Track A 50 % / B 20 % / Shared 25 % / Wet 5 %) | docs/12 |
| [`resource_allocation_phase2_pie.mmd`](diagrams/resource_allocation_phase2_pie.mmd) | Phase 2 effort split (Track A 35 / B 40 / Shared 15 / Wet 10) | docs/12 |
| [`resource_allocation_phase3_pie.mmd`](diagrams/resource_allocation_phase3_pie.mmd) | Phase 3 effort split (Track A 20 / B 60 / Shared 10 / Wet 10) | docs/12 |
| [`dual_track_architecture.mmd`](diagrams/dual_track_architecture.mmd) | Architecture overlay — how shared infrastructure feeds both tracks | docs/12 |
| [`decision_register.mmd`](diagrams/decision_register.mmd) | Mindmap of all 43 architectural decisions | docs/12 |
| [`track_convergence.mmd`](diagrams/track_convergence.mmd) | Sequence diagram of Track A / Track B sharing infrastructure across phases | docs/12 |

---

## Skeleton service tree (`repo/`)

Demonstrates the architecture materialises into real services with real contracts. No business logic; module stubs and Dockerfiles only.

| Path | Service |
| --- | --- |
| [`repo/README.md`](repo/README.md) | Repo overview + setup instructions |
| [`repo/ARCHITECTURE.md`](repo/ARCHITECTURE.md) | Service catalogue + public contracts |
| [`repo/services/chemoinformatic-core/README.md`](repo/services/chemoinformatic-core/README.md) | Metal-extended RDKit sanitization core (Pillar 2). |
| [`repo/services/ingestion/README.md`](repo/services/ingestion/README.md) | Literature mining + ELN ingestion. |
| [`repo/services/model-training/README.md`](repo/services/model-training/README.md) | MKANO+ / ChemFM / diffusion training pipeline. |
| [`repo/services/inference-api/README.md`](repo/services/inference-api/README.md) | FastAPI gateway → three-tier serving (KServe / vLLM / batch). |
| [`repo/services/agentic-orchestrator/README.md`](repo/services/agentic-orchestrator/README.md) | LangGraph multi-agent orchestrator (Pillar 3). |
| [`repo/services/web-ui/README.md`](repo/services/web-ui/README.md) | Next.js + React + RDKit-JS public web UI. |

Infrastructure stubs: [`repo/Dockerfile`](repo/Dockerfile) · [`repo/docker-compose.yml`](repo/docker-compose.yml) · [`repo/pyproject.toml`](repo/pyproject.toml).

---

## Root files

| Path | Purpose |
| --- | --- |
| [`README.md`](README.md) | Project overview + reading-order pointer. |
| [`INDEX.md`](INDEX.md) | This file — complete document index. |
| [`.gitignore`](.gitignore) | Excludes `research-notes/`, build artefacts, IDE noise. |
