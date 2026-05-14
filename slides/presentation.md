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
Theme: see ./marp-theme.css (~200 lines of styling extracted from this file).

To render to PDF:
  npm i -g @marp-team/marp-cli   # one-time
  cd slides
  marp --theme-set marp-theme.css presentation.md -o presentation.pdf

For an HTML preview:
  marp --theme-set marp-theme.css presentation.md -o presentation.html

For live preview, install the VSCode Marp extension and set:
  "markdown.marp.themes": ["./marp-theme.css"]
in your workspace settings.
-->

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# MB Finder v2

## A multi-metal, geometry-aware, agent-orchestrated AI drug-discovery system

<div class="accent-bar"></div>

A research architecture and 18-month implementation roadmap extending the published MKANO and MB Finder system.

<p class="source-line">Rusanov et al., 2026 · ChemRxiv DOI 10.26434/chemrxiv-2025-pp32k/v2</p>

---

<!-- _class: accent -->
<!-- _footer: '' -->

<p class="eyebrow">Part 1</p>

## The opportunity

The source paper describes the **first AI-validated metallodrug**. Its own conclusion declares a roadmap. This architecture operationalises it.

---

## Why this work, in one slide

**The MKANO / MB Finder source paper (Rusanov et al., 2026) describes the first AI-validated metallodrug — PlatinAI, March 2026.**

Its conclusion declares two limitations and a roadmap:

> *"Currently, a key limitation of our model is its inability to predict the geometry of complexes, e.g., cis/trans isomers. […] In future studies, we aim to address this constraint, as well as to develop generative ML models capable of creating novel metallodrugs beyond the de novo fragment-based approach proposed herein."*

This architecture **operationalises that roadmap**, generalises beyond Pt, and adds the production-grade engineering that academic metallodrug discovery groups typically lack a dedicated specialist for.

---

## What MKANO delivered — the foundation we extend

<div class="cols-2">
<div>

| Dimension | Value |
|---|---|
| Unique Pt complexes (curated) | 3,725 from 1,134 publications |
| IC50 values | 17,732 across 591 cell lines |
| Pretraining set | 214,373 Pt SMILES |
| Sanitization success | 94 % |
| Training cell lines | A2780, MCF-7, A549, A2780cis (72 h) |
| HTS validation | 19 complexes, up to 72 % agreement |
| De novo candidates | 427 novel scaffolds |
| Mechanism | Protein signalling — *no DNA adducts* |

</div>
<div>

<div class="hero">
<div class="num">16×</div>
<div class="label">PlatinAI vs cisplatin in cisplatin-resistant A2780cis<br/>(1.5 µM IC50 vs 24 µM)</div>
</div>

**Engaged targets:** COL3A1, BUB1B, PLK1, AURKB

</div>
</div>

---

<!-- _class: accent -->
<!-- _footer: '' -->

<p class="eyebrow">Part 2</p>

## The four-pillar extension

Geometry, multi-metal, agency, MLOps — each a self-contained design unit.

---

## The four pillars

<div class="cols-4">
<div class="pillar p1">
<div class="num">Pillar 1</div>
<h3>AI modernization</h3>
<p>Geometry-aware GNN · AF3 / Boltz-2 target conditioning · ChemFM backbone · equivariant diffusion generative.</p>
</div>
<div class="pillar p2">
<div class="num">Pillar 2</div>
<h3>Multi-metal + adjacent</h3>
<p>Strategy-pattern sanitization (Pt/Au/Cu/Re/Ru/Pd) · multi-omics MoA · ElementKG+ knowledge graph.</p>
</div>
<div class="pillar p3">
<div class="num">Pillar 3</div>
<h3>Agentic DMTA</h3>
<p>Supervisor + 5 specialists · MCP tool surface · cooperative agency · chemist sign-off gates.</p>
</div>
<div class="pillar p4">
<div class="num">Pillar 4</div>
<h3>MLOps & backend</h3>
<p>K8s + MLflow + DVC · three-tier serving · observability · FAIR data · cost-controlled.</p>
</div>
</div>

Pillars 1 & 2 close the **scientific** roadmap stated in the source paper.
Pillars 3 & 4 close the **engineering and orchestration** gaps.

---

## Pillar 1 — AI modernization

**Goal:** bring the AI stack to 2026 capability.

- **Geometry-aware ML** via NatQG + SE(3)-equivariant GNN (Equiformer / MACE).
  Pretrained on the tmQM + tmQMg\* corpus (Kneiding et al., 2023; 160 K transition-metal complexes).
- **Target-aware design** via AlphaFold 3 + Boltz-2 conditioning on validated PlatinAI targets (COL3A1, BUB1B).
- **Foundation-model backbone** via ChemFM LoRA fine-tuning (3 B params, 178 M molecules pretraining).
- **Truly generative design** via equivariant diffusion, hybridised with the existing fragment assembly.

Every component cited is **published, validated, and operational in 2025–2026**.

---

## Local LLM fine-tuning — the 2026 PEFT recipe

**Pillar 1 / ADR-009**

- **bf16 base** → DoRA + rsLoRA (always `use_rslora=True`)
- **4-bit base** → LoftQ (not QDoRA — DoRA adapters can't merge cleanly with a quantised base)
- **DAPT → SFT**: continued pretraining on 214 K Pt SMILES (Q-GaLore) before SFT on the 17,732 IC50 set
- **LoReFT** for task-specific heads (geometry, isomer, target) — up to 50× fewer params than LoRA
- **Runtime: Unsloth** — <span class="tag">8.8× speedup</span> <span class="tag">70 %+ VRAM cut</span> <span class="tag">89 K context on Llama 3.3 70B</span>
- **Phase 3:** GRPO (DeepSeek-R1's RL optimiser, RLVR not RLHF) for the Supervisor agent with verifiable chemistry rewards

**Why self-host:** regional data-protection (HKSAR PDPO / EU GDPR) · pre-publication compound confidentiality · access to chemistry-fine-tuned checkpoints (ChemDFM, host-lab-DAPT'd Llama 3). Cost crossover ≈ 25–50 M tokens/month — Phase 2 hits this.

---

## Agent measurability — DSPy for what we can score

LangGraph + MCP make tools portable. Neither makes **prompts** measurable.

- **DSPy** (Stanford, ICLR 2024) for **Design** and **Analysis** agents — both have ground truth:
  - *Design eval:* the 19 PlatinAI-era complexes — does the top-5 include experimentally active ones?
  - *Analysis eval:* the 50 DEG-DEP pairs — does the top-5 target list include COL3A1 and BUB1B?
- **Teleprompters** (MIPRO, BootstrapFewShot) optimise prompts against the eval set — no more hand-tuning.
- **Langfuse + Phoenix (Arize)** for tracing, regression detection, prompt-cost dashboards.

This is what *quantitative* agent quality looks like in 2026. The source paper's published validation data (compounds 1–19, omics deposits at GEO/PRIDE) becomes the eval substrate.

---

## Pillar 2 — Multi-metal + adjacent science

**Goal:** extend beyond Pt to the broader metallodrug publication record.

- **Strategy-pattern refactor** of the 5-step metal-extended sanitization. One strategy per metal: Pt, Au, Cu, Re, Ru, Pd (extensible).
- **Multi-task multi-metal MKANO+** with metal-token conditioning.
- **Multi-omics MoA inference pipeline** automating the PlatinAI-style mechanism study (RNA-seq + proteomics + KEGG + CETSA).
- **ElementKG+ knowledge graph** unifying compounds · cell lines · proteins · pathways — linking metallodrug, microbiome, ICD, and tubulin research lines.

---

## Pillar 3 — Agentic DMTA orchestration

**Goal:** compress the wet-lab cycle from months to weeks — without replacing chemists.

**Six-role decomposition** (Supervisor + 5 specialists), refining OriGene's five-role design (Zhang et al., bioRxiv 2025; nominated GPR160 in HCC at *p* = 0.0057, ARG2 in CRC at IC₅₀ 3.09 µM):

| Agent | Role | OriGene analogue |
|---|---|---|
| **Supervisor** | Plans campaigns; arbitrates between agents; tracks budget | Coordinator |
| **Design** | Nominates candidates (MKANO+, target scorer, JT-VAE) | Reasoning |
| **Synthesis** | Plans routes; tracks ELN tasks | Planning (synth) |
| **Assay** | Schedules *in vitro* / *in vivo* work; statistical power | Planning (experiment) |
| **Analysis** | MoA inference; flags anomalies | Critic |
| **Report** | Drafts figures, tables, manuscript sections | Reporting |

**Cooperative agency, not autonomy.** Every wet-lab step requires chemist sign-off. A-Lab's 71 %-then-retracted cautionary tale (Szymanski *Nature* 2023 → Palgrave/Schoop *PRX Energy* 2024) is why.

---

## Modern inference — three tiers (ADR-008)

<div class="cols-3">
<div class="tier t1">
<div class="meta">Tier 1</div>
<h3>Small models</h3>
<p>MKANO+, geometry heads → <strong>KServe</strong> (CNCF-incubating). Sub-50 ms p95.</p>
</div>
<div class="tier t2">
<div class="meta">Tier 2</div>
<h3>LLMs &amp; foundation</h3>
<p>ChemFM-LoRA, Llama 3 70B, Qwen 2.5 32B, ChemDFM-13B → <strong>vLLM v1 + AWQ 4-bit + FlashAttention</strong> behind Triton. AWQ on Qwen2.5 72B: <strong>140 GB → 40 GB</strong> without degradation.</p>
</div>
<div class="tier t3">
<div class="meta">Tier 3</div>
<h3>Structure prediction</h3>
<p>AF3 / Boltz-2 / RoseTTAFold-AA → batch service, dedicated GPU pool. Long-running, not interactive.</p>
</div>
</div>

**FA-3** on Hopper (~740 TFLOPs/s) · **FA-4** on Blackwell (**1613 TFLOPs/s, 71 % utilisation, 2.7× over Triton-baseline**).

**Speculative decoding** on **SGLang** with **EAGLE / BaldEagle** drafts — measured **50.43 → 106.22 tok/s = 2.06×** on Qwen 2.5 7B / RTX 3090.

**llm-d cache-aware scheduling** (CNCF, 2025): **57× faster response · 2× throughput at scale** vs naive load balancing.

**Local sovereignty:** chemist Mac Studio M4 Max runs Llama 3.3 70B 4-bit locally at 8.8 tok/s — confidential lit triage stays on-premises.

---

## MCP code execution — the killer pattern

<div class="cols-2">
<div>

Per Anthropic engineering (Dec 2025): tools exposed as MCP servers, agents *write code* that calls them instead of one tool call per message.

For 427 scaffolds × 4 cell lines × 3 protein targets = **5,124 inference calls** → one code block.

**Three of the six chemistry roles** have published Anthropic-cookbook reference implementations:

- `orchestrator_workers.ipynb` → Supervisor
- `evaluator_optimizer.ipynb` → Analysis
- `basic_workflows.ipynb` → Synthesis / Assay / Design

The proposal forks them and specialises to chemistry.

</div>
<div>

<div class="hero">
<div class="num">98.7%</div>
<div class="label">Token reduction<br/>(150,000 → 2,000 per campaign step)</div>
</div>

</div>
</div>

---

## External code — public reference implementations

The repos that turn the plan from "we will build this" into "we will assemble these":

| Repo | Size | Used for |
|---|---|---|
| `uiocompcat/tmcinvdes` | 306 MB | Strandgaard et al. (2025) JT-VAE workflow — **shares co-author Balcells with the source paper (Rusanov et al., 2026)** |
| `hjkgrp/pydentate` | 38 MB | Kulik denticity prediction; pip-installable |
| `Leash-Labs/chemist-style-leaderboard` | 14 MB | Authorship-stratified eval methodology (incl. `clever_hans.pdf`) |
| `anthropics/anthropic-cookbook` | 360 MB | Three agent-pattern reference notebooks |

All four are public GitHub repositories; the platform engineer clones them as Phase 1 dependencies. Detailed adoption notes in `docs/11_references.md`.

---

## Dual-track milestones

The architecture commits to **two parallel work tracks** sharing the same infrastructure investment.

<div class="cols-2">
<div class="track">
<div class="label">Track A</div>
<h3>Evolve MKANO / MB Finder</h3>
<p><em>near-term scientific results</em></p>
<ul>
<li>A1.1 reproduce MKANO</li>
<li>A1.3 Au sanitization strategy</li>
<li>A1.5 pydentate integration</li>
<li>A1.6 MB Finder v2 alpha</li>
<li>A2.1 geometry-aware MKANO+</li>
<li>A2.4 AF3 / Boltz-2 service</li>
<li>A3.2 MB Finder v2 GA</li>
<li>A3.4 multi-metal open-data release</li>
</ul>
</div>
<div class="track b">
<div class="label">Track B</div>
<h3>Build next-gen platform</h3>
<p><em>long-term moat</em></p>
<ul>
<li>B1.1 MLOps stack</li>
<li>B1.2 vLLM + AWQ + Triton</li>
<li>B2.2 JT-VAE on Pt corpus</li>
<li>B2.4 ELN / LIMS agents</li>
<li>B2.5 first wet-lab DMTA campaign</li>
<li>B3.2 diffusion-generated active metallodrug</li>
</ul>
</div>
</div>

Resource-allocation pies and Gantt: `diagrams/dual_track_*.mmd`. Must-tagged milestones fit 75 % of one full-time engineer's capacity per phase, leaving 25 % for overhead and host-lab interruptions.

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

<div class="stack">
<div class="layer l1">
<div class="label">Presentation</div>
<div class="body">MB Finder web UI · REST / GraphQL API · Agentic chat UI</div>
</div>
<div class="layer l2">
<div class="label">Orchestration · Pillar 3</div>
<div class="body">LLM-driven DMTA scheduler + agent registry (MCP / LangGraph / Skills)</div>
</div>
<div class="layer l3">
<div class="label">Models · Pillars 1, 2</div>
<div class="body">Geometry GNN · AF3 / Boltz-2 · generative diffusion · MKANO+ · ChemFM fine-tune · multi-omics MoA</div>
</div>
<div class="layer l4">
<div class="label">Chemoinformatic core · Pillar 2</div>
<div class="body">Metal-extended RDKit (Pt / Au / Cu / Re / Ru / Pd) · NatQG geometry</div>
</div>
<div class="layer l5">
<div class="label">Data &amp; platform · Pillar 4</div>
<div class="body">PostgreSQL + RDKit cartridge · object store · MLflow registry · Kubernetes + CI/CD + observability</div>
</div>
</div>

---

## Phased roadmap

<div class="cols-3">
<div class="phase">
<div class="months">Months 0 – 6</div>
<h3>Phase 1 — Foundations</h3>
<p>MKANO reproduced · Au/Cu sanitization strategies · MB Finder v2 alpha · MLOps live.</p>
</div>
<div class="phase p2">
<div class="months">Months 6 – 12</div>
<h3>Phase 2 — Modernisation</h3>
<p>Geometry-aware + target-aware models · first DMTA campaign · ChemFM LoRA benchmarked.</p>
</div>
<div class="phase p3">
<div class="months">Months 12 – 18</div>
<h3>Phase 3 — Generative + scale</h3>
<p>Diffusion-generated validated hit · public release · FAIR audit.</p>
</div>
</div>

**Critical path:** geometry-aware modelling (Pillar 1) and the first end-to-end DMTA pilot (Pillar 3) in Phase 2.

**Descoping order if needed:** cross-project KG → cost optimisation → instrument integration.

---

<!-- _class: accent -->
<!-- _footer: '' -->

<p class="eyebrow">Part 3</p>

## Why this specific profile

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

## Repository layout · bounded first-project candidates

<div class="cols-2">
<div>

### Repository layout

```
ai-cis-platinum/
├── README.md
├── docs/        13 markdown files, ~40 pages
├── slides/      this deck
├── repo/        skeleton service tree + ADRs
└── diagrams/    Mermaid sources
```

The skeleton repo (`repo/`) demonstrates the architecture materialises into real services with real contracts — not vapourware.

</div>
<div>

### First-project candidates

Three concrete near-term project shapes, each bounded and falsifiable:

1. **Reproduce MKANO** in the new pipeline — Phase 1, ~3 months, parity-validated against the source paper.
2. **Au sanitization strategy** — Phase 1, ~2 months, unlocks parallel Au drug projects.
3. **MoA inference replay** on GSE320503 + PXD074892 — Phase 1, ~1 month, automates the PlatinAI-style mechanism analysis end-to-end.

</div>
</div>

---

<!-- _class: lead -->
<!-- _footer: '' -->

# References

<div class="accent-bar"></div>

**Source paper:** Rusanov et al., ChemRxiv 2026
DOI [10.26434/chemrxiv-2025-pp32k/v2](https://doi.org/10.26434/chemrxiv-2025-pp32k/v2)

**Reference implementation:** [github.com/thebabaklab/MetalKANO](https://github.com/thebabaklab/MetalKANO)

**Full reference list:** `docs/11_references.md`

<p class="source-line">Questions, refinements, or discussion are welcome.</p>
