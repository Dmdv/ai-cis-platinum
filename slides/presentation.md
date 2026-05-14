---
marp: true
theme: babak-lab
size: 16:9
paginate: true
header: 'MB Finder v2 — research architecture'
footer: 'Rusanov et al., 2026 · ChemRxiv DOI 10.26434/chemrxiv-2025-pp32k/v2'
---

<!--
Marp slide deck — MB Finder v2: A Multi-Metal AI-Driven Metallodrug Discovery System.
Theme: see ./marp-theme.css.

To render to PDF:
  npm i -g @marp-team/marp-cli
  cd slides
  marp --theme-set marp-theme.css presentation.md -o presentation.pdf

This file is also readable directly on GitHub — every slide is pure
markdown so the github blob view is the intended audience for browsing.
-->

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# MB Finder v2

### A multi-metal, geometry-aware, agent-orchestrated AI drug-discovery system

A research architecture and 18-month implementation roadmap extending the published MKANO and MB Finder system.

> **Source paper:** Rusanov et al., 2026 · ChemRxiv DOI [10.26434/chemrxiv-2025-pp32k/v2](https://doi.org/10.26434/chemrxiv-2025-pp32k/v2)

---

<!-- _class: accent -->
<!-- _footer: '' -->

# Part 1 · The opportunity

The source paper describes the **first AI-validated metallodrug**. Its own conclusion declares a roadmap. This architecture operationalises it.

---

## Why this work, in one slide

**The MKANO / MB Finder source paper (Rusanov et al., 2026) describes the first AI-validated metallodrug — PlatinAI, March 2026.**

Its conclusion declares two limitations and a roadmap:

> *"Currently, a key limitation of our model is its inability to predict the geometry of complexes, e.g., cis/trans isomers. […] In future studies, we aim to address this constraint, as well as to develop generative ML models capable of creating novel metallodrugs beyond the de novo fragment-based approach proposed herein."*

This architecture **operationalises that roadmap**, generalises beyond Pt, and adds the production-grade engineering that academic metallodrug discovery groups typically lack a dedicated specialist for.

---

## What MKANO delivered — the foundation we extend

| Dimension | Value |
| --- | --- |
| Unique Pt complexes (curated) | **3,725** from 1,134 publications |
| IC50 values | **17,732** across 591 cell lines |
| Pretraining set | **214,373** Pt SMILES |
| Sanitization success | **94 %** |
| Training cell lines | A2780, MCF-7, A549, A2780cis (72 h) |
| HTS validation | 19 complexes, up to **72 %** agreement |
| De novo candidates | **427** novel scaffolds |
| **PlatinAI vs cisplatin (A2780cis)** | **1.5 µM** vs 24 µM — **16× more potent** |
| Mechanism | Protein signalling (COL3A1, BUB1B, PLK1, AURKB) — *no DNA adducts* |

> **Headline result.** PlatinAI is **16× more potent** than cisplatin in cisplatin-resistant A2780cis ovarian cancer, with a non-DNA mechanism of action.

---

<!-- _class: accent -->
<!-- _footer: '' -->

# Part 2 · The four-pillar extension

Geometry, multi-metal, agency, MLOps — each pillar a self-contained design unit.

---

## The four pillars

| # | Pillar | Focus | Key components |
| --- | --- | --- | --- |
| **1** | **AI modernization** | Bring the AI stack to 2026 capability | Geometry-aware GNN · AF3 / Boltz-2 target conditioning · ChemFM backbone · equivariant diffusion |
| **2** | **Multi-metal + adjacent science** | Extend beyond Pt to broader transition metals | Strategy-pattern sanitization (Pt/Au/Cu/Re/Ru/Pd) · multi-omics MoA · ElementKG+ knowledge graph |
| **3** | **Agentic DMTA orchestration** | Compress the wet-lab cycle from months to weeks | Supervisor + 5 specialists · MCP tool surface · cooperative agency · chemist sign-off gates |
| **4** | **MLOps and backend** | Productionise the entire stack | K8s + MLflow + DVC · three-tier serving · observability · FAIR data · cost-controlled |

Pillars 1 & 2 close the **scientific** roadmap stated in the source paper.
Pillars 3 & 4 close the **engineering and orchestration** gaps.

---

## Pillar 1 — AI modernization

**Goal:** bring the AI stack to 2026 capability.

- **Geometry-aware ML** — NatQG + SE(3)-equivariant GNN (Equiformer / MACE). Pretrained on the tmQM + tmQMg\* corpus (Kneiding et al., 2023; 160 K transition-metal complexes).
- **Target-aware design** — AlphaFold 3 + Boltz-2 conditioning on validated PlatinAI targets (COL3A1, BUB1B).
- **Foundation-model backbone** — ChemFM LoRA fine-tuning (3 B params, 178 M molecules pretraining).
- **Truly generative design** — equivariant diffusion, hybridised with the existing fragment assembly.

Every component cited is **published, validated, and operational in 2025–2026**.

---

## Local LLM fine-tuning — the 2026 PEFT recipe

**Pillar 1 / ADR-009**

| Precision | Recipe | Why |
| --- | --- | --- |
| **bf16 / fp16** | DoRA + rsLoRA | Best accuracy when GPU memory permits; always `use_rslora=True` |
| **4-bit (NF4)** | LoftQ (not QDoRA) | DoRA adapters can't merge cleanly with a quantised base |
| **DAPT phase** | Q-GaLore on 214 K Pt SMILES | Memory-efficient continual pretraining before SFT |
| **Task-specific heads** | LoReFT | Up to **50×** fewer params than LoRA at parity |
| **Phase 3 RL post-training** | GRPO (RLVR, not RLHF) | DeepSeek-R1's optimiser; verifiable chemistry rewards |

**Runtime: Unsloth** — Llama 3.1 on Alpaca completes in **2h34m** (vs 23h15m vanilla HF) on a Tesla T4 = **8.8× speedup** with **70 %+ VRAM reduction**. Cut Cross Entropy unlocks **89 K context** on Llama 3.3 70B.

**Why self-host:** regional data-protection (HKSAR PDPO / EU GDPR) · pre-publication compound confidentiality · access to chemistry-fine-tuned checkpoints (ChemDFM, host-lab-DAPT'd Llama 3). Cost crossover ≈ **25–50 M tokens/month** — Phase 2 hits this.

---

## Agent measurability — DSPy for what we can score

LangGraph + MCP make tools portable. Neither makes **prompts** measurable.

- **DSPy** (Stanford, ICLR 2024) for **Design** and **Analysis** agents — both have ground truth:
  - *Design eval:* the 19 PlatinAI-era complexes — does the top-5 include experimentally active ones?
  - *Analysis eval:* the 50 DEG-DEP pairs — does the top-5 target list include COL3A1 and BUB1B?
- **Teleprompters** (MIPRO, BootstrapFewShot) optimise prompts against the eval set — no more hand-tuning.
- **Langfuse + Phoenix (Arize)** for tracing, regression detection, prompt-cost dashboards.

The source paper's already-published validation data (compounds 1–19, omics deposits at GEO/PRIDE) becomes the eval substrate.

---

## Pillar 2 — Multi-metal + adjacent science

**Goal:** extend beyond Pt to the broader metallodrug publication record.

- **Strategy-pattern refactor** of the 5-step metal-extended sanitization. One strategy per metal: Pt, Au, Cu, Re, Ru, Pd (extensible to Ir, Ni, Co, Rh, Fe, Ti, Sn).
- **Multi-task multi-metal MKANO+** with metal-token conditioning.
- **Multi-omics MoA inference pipeline** automating the PlatinAI-style mechanism study (RNA-seq + proteomics + KEGG + CETSA).
- **ElementKG+ knowledge graph** unifying compounds · cell lines · proteins · pathways — linking metallodrug, microbiome, ICD, and tubulin research lines.

---

## Pillar 3 — Agentic DMTA orchestration

**Goal:** compress the wet-lab cycle from months to weeks — without replacing chemists.

**Six-role decomposition** (Supervisor + 5 specialists), refining OriGene's five-role design (Zhang et al., bioRxiv 2025 — nominated GPR160 in HCC at *p* = 0.0057, ARG2 in CRC at IC₅₀ 3.09 µM):

| Agent | Role | OriGene analogue |
| --- | --- | --- |
| **Supervisor** | Plans campaigns; arbitrates between agents; tracks budget | Coordinator |
| **Design** | Nominates candidates (MKANO+, target scorer, JT-VAE) | Reasoning |
| **Synthesis** | Plans routes; tracks ELN tasks | Planning (synth) |
| **Assay** | Schedules *in vitro* / *in vivo* work; statistical power | Planning (experiment) |
| **Analysis** | MoA inference; flags anomalies | Critic |
| **Report** | Drafts figures, tables, manuscript sections | Reporting |

> **Cooperative agency, not autonomy.** Every wet-lab step requires chemist sign-off. A-Lab's 71 %-then-retracted cautionary tale (Szymanski *Nature* 2023 → Palgrave/Schoop *PRX Energy* 2024) is why.

---

## Modern inference — three tiers (ADR-008)

| Tier | Workload | Stack | Latency target |
| --- | --- | --- | --- |
| **1** | Small models — MKANO+, geometry heads | **KServe** (CNCF-incubating) + PyTorch runtime + FP16 | Sub-50 ms p95 |
| **2** | LLMs & foundation — ChemFM-LoRA, Llama 3 70B, Qwen 2.5 32B, ChemDFM-13B | **vLLM v1 + AWQ 4-bit + FlashAttention** behind Triton | 100–500 ms TTFT |
| **3** | Structure prediction — AF3 / Boltz-2 / RoseTTAFold-AA | Custom batch service with FA3 on dedicated GPU pool | ≥ 45 s/job (batch, not interactive) |

**AWQ on Qwen2.5 72B:** 140 GB → **40 GB** without degradation.
**FA-3** on Hopper (~740 TFLOPs/s) · **FA-4** on Blackwell (**1613 TFLOPs/s**, 71 % utilisation, **2.7×** over Triton-baseline).

**Speculative decoding** on **SGLang** with EAGLE / BaldEagle drafts — measured **50.43 → 106.22 tok/s = 2.06×** on Qwen 2.5 7B / RTX 3090.
**llm-d cache-aware scheduling** (CNCF, 2025): **57× faster response · 2× throughput at scale** vs naive load balancing.
**Local sovereignty:** chemist Mac Studio M4 Max runs Llama 3.3 70B 4-bit locally at 8.8 tok/s — confidential lit triage stays on-premises.

---

## MCP code execution — the killer pattern

Per Anthropic engineering (Dec 2025): tools exposed as MCP servers, agents *write code* that calls them instead of one tool call per message.

> **98.7 % token reduction.** For 427 scaffolds × 4 cell lines × 3 protein targets = **5,124 inference calls**, the per-campaign token budget drops from **150,000 → 2,000** when the Design agent emits a single code block instead of 5,124 individual tool calls.

**Three of the six chemistry roles** have published Anthropic-cookbook reference implementations:

| Notebook | Maps to |
| --- | --- |
| `orchestrator_workers.ipynb` | Supervisor agent |
| `evaluator_optimizer.ipynb` | Analysis agent |
| `basic_workflows.ipynb` | Synthesis / Assay / Design (routing + parallelization) |

The proposal forks them and specialises to chemistry.

---

## External code — public reference implementations

| Repo | Size | Used for |
| --- | --- | --- |
| [`uiocompcat/tmcinvdes`](https://github.com/uiocompcat/tmcinvdes) | 306 MB | Strandgaard et al. (2025) JT-VAE workflow — shares co-author Balcells with the source paper |
| [`hjkgrp/pydentate`](https://github.com/hjkgrp/pydentate) | 38 MB | Kulik denticity prediction; pip-installable |
| [`Leash-Labs/chemist-style-leaderboard`](https://github.com/Leash-Labs/chemist-style-leaderboard) | 14 MB | Authorship-stratified eval methodology (incl. `clever_hans.pdf`) |
| [`anthropics/anthropic-cookbook`](https://github.com/anthropics/anthropic-cookbook) | 360 MB | Three agent-pattern reference notebooks |

All four are public GitHub repositories; the platform engineer clones them as Phase 1 dependencies. Detailed adoption notes in `docs/11_references.md`.

---

## Dual-track milestones

The architecture commits to **two parallel work tracks** sharing the same infrastructure investment.

### Track A — Evolve MKANO / MB Finder
*near-term scientific results*

- **A1.1** reproduce MKANO end-to-end
- **A1.3** Au sanitization strategy
- **A1.5** pydentate integration
- **A1.6** MB Finder v2 alpha deployed
- **A2.1** geometry-aware MKANO+
- **A2.4** AF3 / Boltz-2 service
- **A3.2** MB Finder v2 GA
- **A3.4** multi-metal open-data release

### Track B — Build next-generation platform
*long-term moat*

- **B1.1** MLOps stack live
- **B1.2** vLLM + AWQ + Triton serving
- **B2.2** JT-VAE on Pt corpus
- **B2.4** ELN / LIMS agents
- **B2.5** first wet-lab DMTA campaign
- **B3.2** diffusion-generated active metallodrug

> Resource-allocation pies and Gantt: `diagrams/dual_track_*.mmd`. Must-tagged milestones fit 75 % of one full-time engineer's capacity per phase, leaving 25 % for overhead and host-lab interruptions.

---

## Pillar 4 — MLOps and backend

**Goal:** the production engineering academic metallodrug discovery groups typically lack a full-time owner for.

- **Reproducibility** — every model, every figure regeneratable from a tagged commit + dataset hash. MLflow + DVC.
- **Reliability** — Kubernetes deployment · observability (Prometheus / Grafana / Loki / Tempo) · CI/CD with canary rollout.
- **Scalable inference** — three-tier serving (KServe small / vLLM v1 + AWQ + FlashAttention LLMs / custom batch AF3-Boltz2). Autoscale + scale-to-zero overnight.
- **FAIR data** — persistent identifiers · community ontologies · machine-readable licenses · DOI-stable releases.
- **Cost-controlled** — ≈ **US $3.5 K / month** run cost on cloud (comparable to one PhD stipend).

---

## Architecture at a glance

| Layer | Responsibility |
| --- | --- |
| **Presentation** | MB Finder web UI · REST / GraphQL API · Agentic chat UI |
| **Orchestration** *(Pillar 3)* | LLM-driven DMTA scheduler + agent registry (MCP / LangGraph / Skills) |
| **Models** *(Pillars 1 & 2)* | Geometry GNN · AF3 / Boltz-2 · generative diffusion · MKANO+ · ChemFM fine-tune · multi-omics MoA |
| **Chemoinformatic core** *(Pillar 2)* | Metal-extended RDKit (Pt / Au / Cu / Re / Ru / Pd) · NatQG geometry |
| **Data & platform** *(Pillar 4)* | PostgreSQL + RDKit cartridge · object store · MLflow registry · Kubernetes + CI/CD + observability |

---

## Phased roadmap

| Phase | Months | Headline deliverable |
| --- | --- | --- |
| **1 — Foundations** | 0 – 6 | MKANO reproduced · Au/Cu sanitization strategies · MB Finder v2 alpha · MLOps live |
| **2 — Modernisation** | 6 – 12 | Geometry-aware + target-aware models · first DMTA campaign · ChemFM LoRA benchmarked |
| **3 — Generative + scale** | 12 – 18 | Diffusion-generated validated hit · public release · FAIR audit |

**Critical path:** geometry-aware modelling (Pillar 1) and the first end-to-end DMTA pilot (Pillar 3) in Phase 2.
**Descoping order if needed:** cross-project KG → cost optimisation → instrument integration.

---

<!-- _class: accent -->
<!-- _footer: '' -->

# Part 3 · Why this profile

A single researcher with **combined AI, backend, and chemistry-engineering** expertise is uniquely positioned.

---

## Why this multidisciplinary profile

The MKANO paper's own conclusion identifies the bottleneck:

> *"A researcher possessing a combined, deep background in Artificial Intelligence, backend software development, and chemical engineering is uniquely, and perhaps exclusively, positioned to execute this exact paradigm of modern scientific discovery."*

This proposal maps each component to that exact skill set:

- The **metal-extended sanitization** needs chemistry + low-level RDKit — *chemistry engineering ↔ software*.
- The **agentic orchestrator** needs LLM tooling + host-lab workflow understanding — *AI ↔ chemistry*.
- The **MLOps stack** needs backend engineering — *the gap academic metallodrug discovery groups typically have no full-time owner for*.

---

## Risks — addressed, not hidden

| Risk | Mitigation |
| --- | --- |
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
├── docs/        13 markdown files, ~40 pages — the written proposal
├── slides/      this deck + marp-theme.css
├── repo/        skeleton service tree + ADRs (no business logic)
└── diagrams/    Mermaid sources for all architecture diagrams
```

The skeleton repo (`repo/`) demonstrates the architecture materialises into real services with real contracts — not vapourware.

---

## Bounded first-project candidates

Three concrete near-term project shapes, each bounded and falsifiable:

1. **Reproduce MKANO** in the new pipeline — Phase 1, ~3 months, parity-validated against the source paper.
2. **Au sanitization strategy** — Phase 1, ~2 months, unlocks parallel Au drug projects.
3. **MoA inference replay** on GSE320503 + PXD074892 — Phase 1, ~1 month, automates the PlatinAI-style mechanism analysis end-to-end.

---

<!-- _class: lead -->
<!-- _footer: '' -->

# References

**Source paper** — Rusanov et al., *Overcoming cisplatin resistance with AI-driven metallodrug discovery*. ChemRxiv 2026.
DOI [10.26434/chemrxiv-2025-pp32k/v2](https://doi.org/10.26434/chemrxiv-2025-pp32k/v2)

**Reference implementation** — [github.com/thebabaklab/MetalKANO](https://github.com/thebabaklab/MetalKANO)

**Full reference list** — `docs/11_references.md`

*Questions, refinements, or discussion are welcome.*
