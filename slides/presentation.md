<!--
Marp slide deck — MB Finder v2: A Multi-Metal AI-Driven Drug Discovery System

To render: `marp presentation.md -o presentation.pdf` (install Marp CLI first: `npm i -g @marp-team/marp-cli`)
Or view live with the VSCode Marp extension.
-->

---
marp: true
theme: default
size: 16:9
paginate: true
header: 'MB Finder v2 — research architecture'
style: |
  section { font-family: 'IBM Plex Sans', sans-serif; padding: 60px; }
  h1 { color: #1a3a5c; }
  h2 { color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; }
  table { font-size: 80%; }
  code { font-size: 90%; }
---

<!-- _class: lead -->

# MB Finder v2

## A multi-metal, geometry-aware, agent-orchestrated AI drug-discovery system

A research architecture and implementation roadmap that extends the published MKANO and MB Finder system (Rusanov et al., 2026).

---

## Why this work, in one slide

**The MKANO / MB Finder source paper (Rusanov et al., 2026) describes the first AI-validated metallodrug (PlatinAI, March 2026).**
Its conclusion declares two limitations and a roadmap:

> *"Currently, a key limitation of our model is its inability to predict the geometry of complexes, e.g., cis/trans isomers. […] In future studies, we aim to address this constraint, as well as to develop generative ML models capable of creating novel metallodrugs beyond the de novo fragment-based approach proposed herein."*

**This architecture operationalises that roadmap, generalises beyond Pt, and adds the production-grade engineering that academic metallodrug discovery groups typically lack a dedicated specialist for.**

---

## What MKANO delivered (the foundation we extend)

| Dimension | Value |
|---|---|
| Unique Pt complexes (curated) | 3,725 (from 1,134 publications) |
| IC50 values | 17,732 across 591 cell lines |
| Pretraining set | 214,373 Pt SMILES (94 % sanitization success) |
| Final training cell lines | A2780, MCF-7, A549, A2780cis (72 h) |
| HTS validation | 19 complexes, up to 72 % agreement |
| De novo candidates | 427 novel scaffolds; PlatinAI synthesised |
| PlatinAI vs cisplatin in A2780cis | 1.5 µM vs 24 µM — 16× more potent |
| Mechanism | Protein signalling (COL3A1, BUB1B, PLK1) — *no DNA adducts* |

Source: Rusanov, Babak, Balcells et al., ChemRxiv 2026, DOI 10.26434/chemrxiv-2025-pp32k/v2.

---

## The four-pillar extension

```
                ┌────────────────────────────────────────────────┐
                │  MB Finder v2 — Multi-metal Drug Discovery OS  │
                └────────────────────────────────────────────────┘
                                      │
   ┌──────────────────┬──────────────┴───────────────┬──────────────────┐
   ▼                  ▼                              ▼                  ▼
┌──────────┐    ┌────────────┐               ┌──────────┐         ┌──────────┐
│ Pillar 1 │    │ Pillar 2   │               │ Pillar 3 │         │ Pillar 4 │
│ AI mod.  │    │ Multi-metal│               │ Agentic  │         │ MLOps +  │
│          │    │ + adjacent │               │ DMTA     │         │ backend  │
└──────────┘    └────────────┘               └──────────┘         └──────────┘
```

Pillars 1 & 2 close the source paper's stated scientific roadmap; Pillars 3 & 4 close engineering and orchestration gaps.

---

## Pillar 1 — AI modernization

**Goal:** bring the AI stack to 2026 capability.

- **Geometry-aware ML** via NatQG + SE(3)-equivariant GNN (Equiformer / MACE).
  Pretrained on the tmQM + tmQMg* corpus (Kneiding et al., 2023; 160 K transition-metal complexes).
- **Target-aware design** via AlphaFold 3 + Boltz-2 conditioning on validated PlatinAI targets (COL3A1, BUB1B).
- **Foundation-model backbone** via ChemFM LoRA fine-tuning (3 B params, 178 M molecules pretraining).
- **Truly generative design** via equivariant diffusion, hybridised with the existing fragment assembly.

Every component cited is published, validated, and operational in 2025–2026.

---

## Local LLM fine-tuning — the 2026 PEFT recipe

**Pillar 1 / ADR-009:**
- bf16 base → **DoRA + rsLoRA** (always `use_rslora=True`).
- 4-bit base → **LoftQ**, NOT QDoRA — DoRA adapters can't merge cleanly with a quantised base.
- **DAPT → SFT**: continued pretraining on 214 K Pt SMILES (Q-GaLore) before supervised fine-tuning on the 17,732 IC50 set.
- **LoReFT** for task-specific heads (geometry, isomer, target) — up to 50× fewer params than LoRA.
- Runtime: **Unsloth** — Llama 3.1 on Alpaca completes in **2h34m** (vs 23h15m vanilla HF) on a Tesla T4 = **8.8× speedup**; **70 %+ VRAM reduction**. Cut Cross Entropy unlocks **89 K context on Llama 3.3 70B**.
- Phase 3: **GRPO** (DeepSeek-R1's RL optimiser, RLVR not RLHF) for the Supervisor agent with verifiable chemistry rewards.

**Why self-host (Pillar 3):** regional data-protection (HKSAR PDPO / EU GDPR); pre-publication compound confidentiality; access to chemistry-fine-tuned checkpoints (ChemDFM, host-lab-DAPT'd Llama 3). Cost crossover ≈25–50M tokens/month — Phase 2 hits this.

**Protocol layer:** every tool exposed as an **MCP server** so the platform's chemistry tools work with Claude Desktop, ChatGPT, Cursor, and any future MCP client — not just LangGraph.

---

## Agent measurability — DSPy for what we can score

LangGraph + MCP make tools portable, but neither makes *prompts* measurable.

- **DSPy** (Stanford, ICLR 2024) for the **Design** and **Analysis** agents — these have ground truth:
  - Design agent eval: the 19 PlatinAI-era complexes; metric = does the top-5 include the experimentally active ones?
  - Analysis agent eval: the 50 DEG-DEP pairs; metric = does the top-5 target list include COL3A1 and BUB1B?
- **Teleprompters** (MIPRO, BootstrapFewShot) optimise prompts against the eval set — no more hand-tuning.
- **Langfuse + Phoenix (Arize)** for tracing, regression detection, prompt-cost dashboards.

This is what *quantitative* agent quality looks like in 2026. The source paper's already-published validation data (compounds 1–19, the omics deposits at GEO/PRIDE) become the eval substrate.

---

## Pillar 2 — Multi-metal + adjacent science

**Goal:** extend beyond Pt to the broader metallodrug publication record.

- **Strategy-pattern refactor** of the 5-step metal-extended sanitization.
  One strategy per metal: Pt, Au, Cu, Re, Ru, Pd (extensible).
- **Multi-task multi-metal MKANO+** with metal-token conditioning.
- **Multi-omics MoA inference pipeline** automating the PlatinAI-style mechanism study (RNA-seq + proteomics + KEGG + CETSA).
- **ElementKG+ knowledge graph** unifying compounds, cell lines, proteins, pathways — linking the metallodrug, microbiome, ICD, and tubulin research lines.

---

## Pillar 3 — Agentic DMTA orchestration

**Goal:** compress the wet-lab cycle from months to weeks — without replacing chemists.

**Six-role decomposition** (a Supervisor + five specialists), refining OriGene's five-role design (Zhang et al., bioRxiv 2025) which nominated GPR160 in HCC (p=0.0057) and ARG2 in CRC (IC₅₀ 3.09 µM):

| Agent | Role | OriGene analogue |
|---|---|---|
| Supervisor | Plans campaigns; arbitrates between agents; tracks budget | Coordinator |
| Design | Nominates candidates (MKANO+, target scorer, JT-VAE) | Reasoning |
| Synthesis | Plans routes; tracks ELN tasks | Planning (synth side) |
| Assay | Schedules in vitro / in vivo work; statistical power | Planning (experiment side) |
| Analysis | MoA inference; flags anomalies | Critic |
| Report | Drafts figures, tables, manuscript sections | Reporting |

**Cooperative agency, not autonomy.** Every wet-lab step requires chemist sign-off. A-Lab's 71%-then-retracted cautionary tale (Szymanski Nature 2023 → Palgrave/Schoop PRX Energy 2024) is why.

---

## Modern inference — three tiers

**Pillar 4 / ADR-008:**
- **Tier 1** — small models (MKANO+, geometry heads) → **KServe** (CNCF-incubating; LLM-Compressor track). Sub-50 ms p95.
- **Tier 2** — LLMs (ChemFM-LoRA, Llama 3 70B, Qwen 2.5 32B, ChemDFM-13B) → **vLLM v1 + AWQ 4-bit + FlashAttention** behind Triton. AWQ on Qwen2.5 72B: **140 GB → 40 GB without degradation**. **FA-3** on Hopper (~740 TFLOPs/s); **FA-4** on Blackwell (**1613 TFLOPs/s, 71 % utilisation, up to 2.7× over Triton-baseline**).
- **Tier 3** — Structure prediction (AF3 / Boltz-2 / RoseTTAFold-AA) → batch service, dedicated GPU pool.

**Speculative decoding** lives on **SGLang** with **EAGLE** (BaldEagle) draft models — measured **50.43 → 106.22 tok/s = 2.06× speedup** on Qwen 2.5 7B / RTX 3090. Not yet supported on vLLM v1.

**llm-d cache-aware scheduling** (CNCF, 2025) delivers **57× faster response times and 2× throughput at scale** vs naive load balancing.

**Local sovereignty**: Chemist Mac Studio M4 Max runs Llama 3.3 70B 4-bit locally at 8.8 tok/s — confidential lit triage stays on-premises.

---

## MCP code execution — the killer pattern

Per Anthropic engineering (Dec 2025): tools exposed as MCP servers, agents *write code* that calls them instead of one-tool-call-per-message. Token usage **150,000 → 2,000 = 98.7% reduction**. For 427 scaffolds × 4 cell lines × 3 protein targets = 5,124 inference calls → one code block.

**Three of our 5 specialists have published Anthropic-cookbook reference implementations** (`orchestrator_workers.ipynb`, `evaluator_optimizer.ipynb`, `basic_workflows.ipynb`).

The proposal forks them and specialises to chemistry.

---

## External code — public reference implementations

The repos that turn the plan from "we will build this" into "we will assemble these":

| Repo | Size | Used for |
|---|---|---|
| `uiocompcat/tmcinvdes` | 306 MB | Strandgaard et al. (2025) JT-VAE workflow — **shares co-author Balcells with the source paper (Rusanov et al., 2026)** |
| `hjkgrp/pydentate` | 38 MB | Kulik denticity prediction; pip-installable |
| `Leash-Labs/chemist-style-leaderboard` | 14 MB (incl. `clever_hans.pdf`) | Authorship-stratified eval methodology |
| `anthropics/anthropic-cookbook` | 360 MB | Three agent-pattern reference notebooks |

All four are public GitHub repositories; the platform engineer clones them as Phase 1 dependencies. Detailed adoption notes are cited in `docs/11_references.md`.

---

## Dual-track milestones

The proposal commits to **two parallel work tracks** that share the same shared-infrastructure investment:

**Track A — Evolve MKANO/MB Finder** (near-term scientific results)
A1.1 reproduce MKANO · A1.3 Au strategy · A1.5 pydentate integration · A1.6 MB Finder v2 alpha · A2.1 geometry-aware MKANO+ · A2.4 AF3/Boltz-2 service · A3.2 MB Finder v2 GA · A3.4 multi-metal open-data

**Track B — Build next-gen platform** (long-term moat)
B1.1 MLOps stack · B1.2 vLLM + AWQ + Triton · B2.2 JT-VAE on Pt corpus · B2.4 ELN/LIMS agents · B2.5 first wet-lab DMTA campaign · B3.2 diffusion-generated active metallodrug

Resource allocation pie charts and Gantt: `diagrams/dual_track_*.mmd`. Capacity check: Must-tagged milestones fit 75% of one full-time engineer's capacity per phase, leaving 25% for overhead and host-lab interruptions.

---

## Pillar 4 — MLOps and backend

**Goal:** the production engineering academic metallodrug discovery groups typically lack a full-time owner for.

- **Reproducibility:** every model, every figure regeneratable from a tagged commit + dataset hash. MLflow + DVC.
- **Reliability:** Kubernetes deployment, observability (Prometheus / Grafana / Loki / Tempo), CI/CD with canary rollout.
- **Scalable inference:** three-tier serving — KServe (small classifiers), vLLM v1 + AWQ + FlashAttention (LLMs), custom batch service (AF3/Boltz-2). Autoscale + scale-to-zero overnight.
- **FAIR data:** persistent identifiers, community ontologies, machine-readable licenses, DOI-stable releases.
- **Cost-controlled:** ≈ US $3.5 K / month run cost on cloud (comparable to one PhD stipend).

---

## Architecture at a glance

```
+----------------------------------------------------------------------+
|                   PRESENTATION LAYER                                 |
|   MB Finder web UI  |  REST/GraphQL API  |  Agentic chat UI          |
+----------------------------------------------------------------------+
|                   ORCHESTRATION (PILLAR 3)                           |
|         LLM-driven DMTA scheduler  +  agent registry                 |
+----------------------------------------------------------------------+
|                   MODELS (PILLARS 1, 2)                              |
|  geometry GNN | AF3 / Boltz-2 | generative diffusion | MKANO+        |
|  ChemFM fine-tune | multi-omics MoA                                  |
+----------------------------------------------------------------------+
|                   CHEMOINFORMATIC CORE (PILLAR 2)                    |
|   metal-extended RDKit (Pt/Au/Cu/Re/Ru/Pd)  |  NatQG geometry        |
+----------------------------------------------------------------------+
|                   DATA & PLATFORM (PILLAR 4)                         |
|   PostgreSQL + RDKit cartridge  |  Object store  |  MLflow registry  |
|   Kubernetes + CI/CD + observability                                 |
+----------------------------------------------------------------------+
```

---

## Phased roadmap

| Phase | Months | Headline deliverable |
|---|---|---|
| 1 — Foundations | 0–6 | MKANO reproduced + Au/Cu strategies + MB Finder v2 alpha + MLOps live |
| 2 — Modernisation | 6–12 | Geometry-aware + target-aware models + first DMTA campaign |
| 3 — Generative + scale | 12–18 | Diffusion-generated validated hit + public release + FAIR audit |

Critical path: geometry-aware modelling (Pillar 1) and the first end-to-end DMTA pilot (Pillar 3) in Phase 2.

Descoping order if needed: cross-project KG → cost optimisation → instrument integration.

---

## Why this specific multidisciplinary profile

The MKANO paper's own conclusion identifies the bottleneck:

> *"A researcher possessing a combined, deep background in Artificial Intelligence, backend software development, and chemical engineering is uniquely, and perhaps exclusively, positioned to execute this exact paradigm of modern scientific discovery."*

This proposal maps each component to that exact skill set:

- The metal-extended sanitization needs chemistry + low-level RDKit — *chemistry engineering ↔ software*.
- The agentic orchestrator needs LLM tooling + host-lab workflow understanding — *AI ↔ chemistry*.
- The MLOps stack needs backend engineering — *the gap academic metallodrug discovery groups typically have no full-time owner for*.

---

## Risks — addressed, not hidden

| Risk | Mitigation |
|---|---|
| Geometry doesn't improve accuracy | Ablation pass — promote only if lift is significant |
| AF3 inaccurate on metals | Ensemble with Boltz-2; condition, don't predict |
| ChemFM doesn't beat MKANO | Treated as secondary opinion; MKANO remains primary |
| Unsynthesisable diffusion outputs | Synthesis-feasibility filter + retrosynthesis required |
| Agent hallucination | Sanitization + human-in-the-loop on every wet-lab step |
| Cloud cost overruns | Hard caps + scale-to-zero + spot training |
| Single-engineer fragility | ADRs + runbooks + cross-training |

Full risk register: `docs/09_risks_and_mitigations.md`.

---

## Repository layout

```
ai-cis-platinum/
├── README.md
├── docs/        13 markdown files, ≈ 40 pages total — the written proposal
├── slides/      this deck
├── repo/        skeleton service tree + ADRs, no business logic
└── diagrams/    Mermaid sources for all architecture diagrams
```

The skeleton repo (`repo/`) demonstrates that the proposed architecture materialises into real services with real contracts — not vapourware.

---

## Bounded first-project candidates

Three concrete near-term project shapes, each bounded and falsifiable:

1. **Reproduce MKANO in the new pipeline** — Phase 1 milestone, ~3 months work, parity-validated against the source paper.
2. **Au sanitization strategy** — Phase 1 milestone, ~2 months work, unlocks parallel Au drug projects.
3. **MoA inference replay on GSE320503 + PXD074892** — Phase 1 milestone, ~1 month work, automates the PlatinAI-style mechanism analysis end-to-end.

---

## References

- Source paper: Rusanov et al., ChemRxiv 2026, DOI 10.26434/chemrxiv-2025-pp32k/v2
- Reference implementation: https://github.com/thebabaklab/MetalKANO
- Full reference list: `docs/11_references.md`

*Questions, refinements, or discussion are welcome.*
