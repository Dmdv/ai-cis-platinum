# 12 — Dual-Track Milestones: Consolidation and Decision Register

**Contents**

- [Executive summary — the two tracks](#executive-summary-the-two-tracks)
- [Track A — Evolve the existing lab platform](#track-a-evolve-the-existing-lab-platform)
- [Track B — Build the next-gen platform (in parallel)](#track-b-build-the-next-gen-platform-in-parallel)
- [Where the tracks converge — shared infrastructure](#where-the-tracks-converge-shared-infrastructure)
- [Resource allocation across phases](#resource-allocation-across-phases)
- [Decision register](#decision-register)
- [Risk matrix per track](#risk-matrix-per-track)
- [Convergence and divergence](#convergence-and-divergence)
- [Visual artefacts (Mermaid sources)](#visual-artefacts-mermaid-sources)
- [How to use this document](#how-to-use-this-document)


**Purpose.** This document consolidates the architectural decisions, primary-source evidence, and code-grounded adoption paths into **two parallel work tracks** with explicit milestones, resource allocation, and convergence points.

The two tracks are not alternatives — they run in parallel and share the same underlying infrastructure. The researcher operates on both simultaneously, with the allocation shifting across phases.

---

## Executive summary — the two tracks

```
TRACK A — EVOLVE the existing lab platform                TRACK B — BUILD the next-gen platform
       (MKANO + MB Finder + extensions)                          (in parallel, on shared infra)

  Near-term, low-risk, high near-term value             Long-term, higher-risk, high competitive moat
  ─────────────────────────────────────────             ───────────────────────────────────────────
  Reproduce MKANO in new system                        Foundation-model backbone (ChemFM-LoRA)
  Multi-metal sanitization (Au, Cu, Re, Ru, Pd)         Equivariant diffusion + JT-VAE generative
  Geometry-aware MKANO+ (cis/trans head)                Agentic DMTA (Supervisor + 5 specialists, MCP, Skills)
  MB Finder v2 alpha (production-grade)                 RLVR + GRPO training
  Multi-omics MoA inference                             Cross-project knowledge graph
  ELN / LIMS integration                                Skills marketplace (public release)
  Public-facing dataset release                         Multi-modal retrieval (ColPali figures)
```

Both tracks share infrastructure (data layer, model registry, chemoinformatic core, retrieval layer, MLOps stack, knowledge graph) so investment in one accelerates the other. The convergence diagram is in `diagrams/dual_track_architecture.mmd`.

---

## Track A — Evolve the existing lab platform

**Premise.** The published MKANO + MB Finder system (Rusanov et al., 2026) is operational; the proposal extends what exists rather than replacing it. Track A delivers near-term scientific results the host lab can publish and the principal investigator can show to reviewers within the first 6-12 months.

**Risk posture.** Low. Every Track A milestone has either (a) a published peer-reviewed precedent, (b) a working reference implementation available as a public GitHub repository (see references in `docs/11_references.md`), or both.

### Track A milestones (per phase)

### Capacity reality check — milestone priorities

The proposal's full milestone list (36 items over 18 months) would over-commit one platform engineer by approximately 2× if every milestone were required. Treating every milestone as mandatory is dishonest planning. The lists below use a three-tier priority annotation that the engineer, the principal investigator, and reviewers can use to track which items must close per phase:

- **M** (Must) — required to declare the phase complete. ≈50 % of milestones; total effort fits within the 26-week phase window with overhead allowance.
- **S** (Should) — completed within the phase if capacity permits; otherwise rolls to the next phase. ≈30 % of milestones.
- **X** (Stretch) — only attempted if all M and S items in the current phase close. ≈20 % of milestones; explicit candidates for descoping.

The sum of M-tagged effort per phase is targeted at ≤ 75 % of a single engineer's 26-week capacity, with the remaining 25 % absorbed by collaboration overhead, debugging, code review, and lab interruption (wet-lab questions, chemist UX iterations, the occasional half-day spent on something not in this list).

#### Phase 1 — Foundations (months 0–6) — TRACK A WEIGHT: ≈70 %

| ID | Pri | Milestone | Source / dependency | Effort | Success criterion |
|---|---|---|---|---|---|
| A1.1 | **M** | Reproduce MKANO end-to-end in the new repo | `github.com/thebabaklab/MetalKANO` | 4 wks | ROC-AUC ± 2 % of source-paper baseline on all 4 cell lines |
| A1.2 | **M** | Metal-extended sanitization refactored to strategy-pattern API | ADR-002, Pillar 2 | 3 wks | Pt strategy passes the 94 % parsing-success benchmark |
| A1.3 | **M** | Au sanitization strategy (κ¹ Au(I) linear + κ² Au(III) square-planar + NHC) | Chemistry review by the chemistry team | 3 wks | ≥ 90 % parsing on ≥ 100 manually curated Au complexes |
| A1.4 | S | Cu sanitization strategy (Cu(I), Cu(II)) | Pillar 2 | 2 wks | ≥ 90 % parsing on ≥ 100 Cu complexes |
| A1.5 | **M** | **`pydentate` integration** upstream of sanitization | github.com/hjkgrp/pydentate | 1-2 wks | Toney coordinating-atom-count model exposed via chemoinformatic-core API |
| A1.6 | S | MB Finder v2 alpha deployed | Pillar 4 production stack | 4 wks | API live; replicates MB Finder v1 functionality on K8s |
| A1.7 | S | Multi-omics MoA service replays PlatinAI mechanism study | Pillar 2 Component 2.3; GSE320503 + PXD074892 | 3 wks | Re-derives COL3A1, BUB1B, PLK1 as top-5 from raw RNA-seq + proteomics |

Phase 1 Track A: 11–12 wks Must (≈45 % of 26-wk capacity, leaving room for Track B + shared infra below).

**Phase 1 outputs published / shipped:**
- MB Finder v2 alpha deployed to a staging URL.
- Open-data release: lab's 17,732 IC50 dataset re-published with versioned API.
- Internal manuscript draft: "Reproducing MKANO and extending to Au and Cu metallodrugs."

#### Phase 2 — Modernisation (months 6–12) — TRACK A WEIGHT: ≈50 %

| ID | Pri | Milestone | Effort | Success criterion |
|---|---|---|---|---|
| A2.1 | **M** | Geometry-aware MKANO+ (cis/trans classification head) | 6 wks | ≥ 90 % cis/trans accuracy on held-out Pt(II) isomer pairs |
| A2.2 | **M** | tmQM + tmQMg* pretraining run | 4 wks | Geometry encoder pretrained on 160 K+ TM corpus |
| A2.3 | S | Re, Ru sanitization strategies | 4 wks | ≥ 90 % parsing per metal |
| A2.4 | **M** | AF3 / Boltz-2 receptor prediction service (Tier 3 inference) | 4 wks | Per-protein predictions for COL3A1, BUB1B, PLK1, AURKB |
| A2.5 | S | Metal-aware re-docking (Pillar 1 Component 1.2.1) | 4 wks | CETSA-validated docking score for PlatinAI–COL3A1 |
| A2.6 | X | Multi-omics MoA on ICD + tubulin compounds from lab archive | 4 wks | MoA dossiers for ≥ 2 non-Pt lab projects |

Phase 2 Track A: 14 wks Must (≈54 % of 26-wk capacity).

**Phase 2 outputs:**
- Public manuscript on geometry-aware MKANO+.
- ICD / tubulin MoA results integrated into lab's broader publication pipeline.

#### Phase 3 — Steady-state (months 12–18) — TRACK A WEIGHT: ≈30 %

| ID | Pri | Milestone | Effort | Success criterion |
|---|---|---|---|---|
| A3.1 | S | Pd sanitization + multi-metal MKANO+ retraining | 4 wks | All six metals (Pt/Au/Cu/Re/Ru/Pd) supported |
| A3.2 | **M** | MB Finder v2 public GA release | 6 wks | Public-facing platform; SDK in Python + JS; FAIR audit passed |
| A3.3 | S | Cross-project KG (ElementKG+) live | 6 wks | First cross-project insight surfaced (Pt-portfolio × tubulin overlap) |
| A3.4 | **M** | Open-data release: multi-metal corpus | 2 wks | CC-BY-4.0 release; Zenodo DOI; preprint |

Phase 3 Track A: 8 wks Must (≈31 % of 26-wk capacity).

---

## Track B — Build the next-gen platform (in parallel)

**Premise.** The lab's competitive moat over time is not MKANO itself — it is the *platform* that produces MKANO + future models reliably. Track B builds that platform: agentic, generative, foundation-model-backed, MCP-exposed, skill-curated.

**Risk posture.** Medium. Every Track B milestone has a published reference (citations throughout the proposal), but the combination as applied to metallodrugs is novel. Higher upside, higher uncertainty.

### Track B milestones (per phase)

#### Phase 1 — Foundations (months 0–6) — TRACK B WEIGHT: ≈30 %

| ID | Pri | Milestone | Source / dependency | Effort | Success criterion |
|---|---|---|---|---|---|
| B1.1 | **M** | MLOps stack stood up (K8s, MLflow, DVC, CI/CD) | Pillar 4; ADR-006 | 4 wks | Every Track A model is registered + reproducible |
| B1.2 | **M** | vLLM v1 + AWQ + Triton inference pool deployed | ADR-008 | 3 wks | Llama 3 70B serves at < 500 ms TTFT, 4-bit AWQ |
| B1.3 | S | MCP server: chemoinformatic-core | ADR-007 | 2 wks | MCP server callable from Claude Desktop |
| B1.4 | S | MCP server: inference-api | ADR-007 | 2 wks | Single-molecule predictions via MCP |
| B1.5 | S | LangGraph orchestrator skeleton (Supervisor + Design only) | Pillar 3 Component 3.4; anthropic-cookbook fork | 4 wks | First end-to-end virtual campaign (no wet-lab) |
| B1.6 | X | Initial Skills library (9 SKILL.md files per ADR-011) | ADR-011 | 3 wks | pt-retrosynthesis, mtt-protocol, cetsa-analysis, kegg-enrichment, etc. checked in |

Phase 1 Track B: 7 wks Must (≈27 % of 26-wk capacity). Phase 1 Tracks A+B Must total: 18–19 wks (≈73 % of capacity, leaving 7 wks overhead).

**Phase 1 outputs:**
- Production-grade infrastructure live.
- First Supervisor + Design loop runs a virtual campaign (no chemistry yet).
- MCP servers reusable across Track A and Track B.

#### Phase 2 — Modernisation (months 6–12) — TRACK B WEIGHT: ≈50 %

| ID | Pri | Milestone | Effort | Success criterion |
|---|---|---|---|---|
| B2.1 | S | ChemFM-LoRA fine-tune on Pt corpus (QLoRA + DoRA via Unsloth) | 6 wks | Benchmarked vs MKANO+ on identical splits |
| B2.2 | **M** | **`tmcinvdes` fork: JT-VAE training on lab's Pt corpus** | 8 wks | First Pt JT-VAE generates ≥ 70 % valid κ² complexes |
| B2.3 | X | Equivariant diffusion generator (END / MACE backbone) — *parallel track to B2.2; pick one for Phase 2* | 8 wks | Diversity benchmark on 1K generated candidates |
| B2.4 | **M** | Synthesis + Assay agents wired to ELN / LIMS | 4 wks | First chemist-approved synthesis kicked off via agentic-orchestrator |
| B2.5 | **M** | First end-to-end DMTA campaign (real lab project: Au(III) hit-to-lead) | 8 wks (wet-lab gated) | Inter-step latency ≤ days; wet-lab clocks retained |
| B2.6 | S | Contextual retrieval + GraphRAG over ElementKG+ | 6 wks | 49 %+ retrieval-failure-rate reduction per Anthropic benchmark |
| B2.7 | X | DSPy compilation of Design + Analysis prompts | 3 wks | Measurable agent quality on the 19 PlatinAI-era benchmark |

Phase 2 Track B: ≈14 wks Must (B2.2 in parallel with B2.4→B2.5 critical path; wet-lab gating on B2.5 means engineer waits, doesn't burn 8 wks). Phase 2 Tracks A+B Must total: 26–28 wks — at the upper edge of 26-wk capacity, with B2.5's wet-lab waits absorbing the overrun.

**Phase 2 outputs:**
- First chemistry foundation model fine-tune deployed.
- First wet-lab DMTA campaign closed.
- Preprint: "Agentic DMTA orchestration for metallodrug discovery."

#### Phase 3 — Generative + Scale (months 12–18) — TRACK B WEIGHT: ≈70 %

| ID | Pri | Milestone | Effort | Success criterion |
|---|---|---|---|---|
| B3.1 | S | RLVR + GRPO post-training of the Supervisor LLM | 8 wks | Verifiable-reward function on 5 chemistry rules; measurable lift on benchmark campaigns |
| B3.2 | **M** | First diffusion- or JT-VAE-generated, experimentally-validated active metallodrug | 12 wks (wet-lab gated) | One novel candidate confirmed active in cell-line assay |
| B3.3 | X | Multi-modal retrieval (ColPali) over chemistry figures | 4 wks | Chemistry-PDF figure search live in MB Finder v2 |
| B3.4 | X | Skills marketplace public release | 6 wks | ≥ 10 reusable Skills published; first external lab adoption |
| B3.5 | X | Metallodrug-specific NNP benchmark suite | 6 wks | Pt/Au/Cu/Re/Ru/Pd × ligand-family matrix published |
| B3.6 | S | Public API SDKs (Python, JS) | 4 wks | Third-party MCP clients can query the platform's tools |

Phase 3 Track B: 12 wks Must (B3.2 alone, wet-lab-gated; engineer time inside the wait is allocated to S items). Phase 3 Tracks A+B Must total: 20 wks (≈77 % of 26-wk capacity).

**Phase 3 outputs:**
- Generative metallodrug hit experimentally validated.
- Skills marketplace seeded.
- Two more preprints / papers in flight.

---

## Where the tracks converge — shared infrastructure

Both tracks share the same underlying primitives, which is why running them in parallel is cheaper than running either alone.

| Shared component | Used by Track A for | Used by Track B for |
|---|---|---|
| **Metal-extended chemoinformatic core** | Sanitisation of MKANO inputs; multi-metal extension | Sanitisation of JT-VAE / diffusion outputs; pydentate upstream |
| **PostgreSQL + RDKit cartridge + pgvector** | Compound database, IC50 store, multi-omics warehouse | Vector store for retrieval; campaign state for agents |
| **MLflow model registry** | MKANO+, multi-metal heads, geometry head | ChemFM-LoRA, JT-VAE, diffusion generator, RLVR-trained Supervisor |
| **vLLM + Triton + AWQ inference pool** | Single-molecule predictions for the public web UI | Orchestrator LLM calls, retrieval, MoA inference |
| **MCP server surface** | Sanitisation + prediction tools | Plus retrosynth, ELN, LIMS, KG, Skills |
| **KServe + Kubernetes + CI/CD** | MB Finder v2 alpha deployment | All Track B services |
| **Multi-omics MoA pipeline (Pillar 2.3)** | PlatinAI mechanism replay; ICD / tubulin MoA | Analysis agent's primary tool |
| **ElementKG+ knowledge graph** | Cross-project insight queries | GraphRAG substrate for Design + Analysis agents |
| **Skill library (ADR-011)** | Reproducible procedure documentation | Loaded on-demand by each agent |

**Investment in any shared component accelerates both tracks.** This is the load-bearing argument for the dual-track approach — it is *cheaper* than picking one track because the infrastructure investment is reused.

---

## Resource allocation across phases

The platform engineer's effort split shifts as the project matures. The percentages below are **approximate time-share** across all engineering activities (milestone work + code review + debugging + documentation + lab meetings + chemist-UX iteration). They aggregate the Must milestones above plus the standard overhead any engineering role carries — they are *not* a sum of milestone-effort weeks. The Must totals at the end of each phase block above are the load-bearing capacity check.

| Phase | Track A weight | Track B weight | Shared infra weight | Wet-lab support |
|---|---|---|---|---|
| Phase 1 (months 0–6) | 50 % | 20 % | 25 % | 5 % |
| Phase 2 (months 6–12) | 35 % | 40 % | 15 % | 10 % |
| Phase 3 (months 12–18) | 20 % | 60 % | 10 % | 10 % |

Pie chart: `diagrams/resource_allocation_pie.mmd`. Gantt: `diagrams/dual_track_gantt.mmd`. Architecture overlay: `diagrams/dual_track_architecture.mmd`.

---

## Decision register

The architectural commitments the proposal commits to. The platform engineer references them when implementing each milestone.

### Architecture and data
| # | Decision | ADR |
|---|---|---|
| D-01 | Polyglot microservices (not monolith) | ADR-001 |
| D-02 | PostgreSQL + RDKit cartridge + pgvector | ADR-002 |
| D-03 | Knowledge graph in Neo4j initially; migrate to pg-graph in Phase 3 | ADR-005 |
| D-04 | MLflow as model registry + experiment tracker | ADR-006 |
| D-05 | Medallion architecture (Bronze/Silver/Gold) | Pillar 4 / Pillar 7 |

### AI and modelling
| # | Decision | ADR |
|---|---|---|
| D-06 | MKANO retained as primary; ChemFM-LoRA as secondary opinion | ADR-003 |
| D-07 | **bf16/fp16 fine-tune = DoRA + rsLoRA**; **4-bit fine-tune = LoftQ** (NOT QDoRA) | ADR-009 |
| D-08 | Always `use_rslora=True` | ADR-009 |
| D-09 | Q-GaLore for domain-adaptive continued pretraining (DAPT) on 214 K Pt corpus | ADR-009 |
| D-10 | LoReFT for task-specific heads (geometry, isomer, target) | ADR-009 |
| D-11 | RLVR with GRPO (not RLHF / PPO) for Phase-3 Supervisor post-training | ADR-009 |
| D-12 | Equivariance for property prediction; benchmark scaled-transformer diffusion in Phase 3 | Pillar 1.4 |
| D-13 | JT-VAE (Strandgaard/Balcells) as complementary track to equivariant diffusion | Pillar 1.4.1 |
| D-14 | NatQG geometry representation; tmQM + tmQMg* pretraining | Pillar 1.1 |
| D-15 | `pydentate` (Kulik) as upstream denticity predictor — pip-installable | Pillar 1.1 |

### Inference and serving
| # | Decision | ADR |
|---|---|---|
| D-16 | Three-tier serving: KServe (small) / vLLM (LLM) / custom (AF3/Boltz-2) | ADR-008 |
| D-17 | AWQ as default 4-bit quantisation; AutoRound + HQQ per-model | ADR-008 |
| D-18 | **vLLM v1 only** (no v0 fallback) | ADR-008 |
| D-19 | Speculative decoding on SGLang (EAGLE/BaldEagle), not vLLM v1 yet | ADR-008 |
| D-20 | FA3 on Hopper; FA4 on Blackwell when procured | ADR-008 / ADR-009 |
| D-21 | Disaggregated prefill/decode is a Phase 3 optimization above 30 concurrent users | Pillar 4 |
| D-22 | Boltz-2 affinity = ranking signal, NOT absolute ΔG; Chai-1 evaluated as alternative | Pillar 1.2 |
| D-23 | RoseTTAFold-AA as open-source US-academic alternative to AF3 | Pillar 1.2 |

### Agents
| # | Decision | ADR |
|---|---|---|
| D-24 | LangGraph as orchestrator state machine | ADR-004 |
| D-25 | Six-role decomposition: Supervisor + 5 specialists (Design/Synthesis/Assay/Analysis/Report) | Pillar 3 Component 3.1 |
| D-26 | **OriGene (Zhang et al. 2025) as direct biology precedent** for the Supervisor + 5 specialists / six-role design (refines OriGene's 5 roles) | Pillar 3 Component 3.1.1 |
| D-27 | MCP for the tool surface — "USB-C port for AI applications" | ADR-007 |
| D-28 | **Code execution with MCP** for fragment screens — 98.7 % token reduction | Pillar 3 Component 3.4.1 |
| D-29 | Hybrid architecture #2 (LangGraph) + #3 (Skills) per Anthropic | ADR-004 |
| D-30 | Skill curation as first-class deliverable; ADR-011 + Hermes patterns | ADR-011 |
| D-31 | DSPy for measurable Design + Analysis agents | Pillar 3 Component 3.4.2 |
| D-32 | Cooperative agency, NOT full autonomy — A-Lab cautionary tale cited | Pillar 3 |
| D-33 | Target Level 2 (constraint-aware planning) in Phase 1-2; Level 3 in Phase 3 | ADR-012 |
| D-34 | Four-layer memory model (working/sessions/memory/artifacts) — Nate context-engineering | Pillar 3 |

### Validation and retrieval
| # | Decision | ADR |
|---|---|---|
| D-35 | Contextual Retrieval (Anthropic): 35 % / 49 % / 67 % failure-rate reductions | ADR-010 |
| D-36 | Hybrid retrieval: BGE-M3 dense + BM25 + reranker | ADR-010 |
| D-37 | GraphRAG over ElementKG+ | ADR-010 |
| D-38 | ColPali for chemistry-figure multi-modal retrieval | ADR-010 |
| D-39 | **Authorship-stratified split as 4th validation method** (Clever Hans defence) | Pillar 1.1 validation |
| D-40 | Per-category NNP benchmarking discipline (Rowan-style) | Pillar 1.1 |

### Data sovereignty and deployment
| # | Decision | ADR |
|---|---|---|
| D-41 | Regional data-protection (HKSAR PDPO / EU GDPR) + pre-publication IP → self-host LLMs for sensitive data | Pillar 3 Component 3.2.1 |
| D-42 | Apple Silicon (Mac Studio M4 Max) for chemist-workstation dev | ADR-009 |
| D-43 | Host-lab archetype: ScienceData-as-a-Service / Lab Orchestration (Yang taxonomy) | ADR-012 |

---

## Risk matrix per track

### Track A risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| MKANO reproduction differs from paper | Low | Medium | Strict numerical-equivalence test on 4 cell lines; if differs, halt and diagnose |
| Per-metal sanitization rules incomplete | Medium | Low | Failed compounds routed to curation queue; chemist review |
| Multi-omics MoA pipeline mis-attributes targets | Medium | Medium | Replay PlatinAI as fixed validation; require recovery of COL3A1, BUB1B |

### Track B risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ChemFM-LoRA underperforms MKANO | Medium | Low | Treated as secondary opinion; MKANO retained as primary |
| JT-VAE / diffusion produces invalid metallodrugs | Medium | Medium | Mandatory chemoinformatic-core sanitisation gate before chemist sees output |
| Agentic orchestrator context-rot in multi-week campaigns | Medium | High | Four-layer memory model (Pillar 3 / Nate context-engineering); bounded working context |
| AF3 weak on Pt-containing ligands | High | Medium | Metal-aware re-docking step (Component 1.2.1); ensemble AF3 + Boltz-2 |
| Boltz-2 internal-target performance degradation | High | Low | Used only as ranking signal, not absolute (D-22) |
| RLVR reward hacking | Low | Medium | Verifiable rewards only; length-controlled; track failure modes |
| Cost overrun (frontier-LLM + GPU) | Medium | Medium | Self-host crossover at ≈25 M tokens/month; pre-budget tracker |

---

## Convergence and divergence

**Where Track A and Track B converge:** the shared-infrastructure table above. Same chemoinformatic core, same model registry, same MCP surface, same retrieval, same observability.

**Where they diverge:**
- Track A optimises for **near-term scientific publications** the host lab can show reviewers in 2026-2027.
- Track B optimises for **long-term competitive moat** — when other labs catch up to MKANO, the host lab is already running an agentic platform on a Skills marketplace with a generative diffusion track.

**The argument for parallel pursuit, not sequential:**
1. Sequential would mean a 12-month gap before Track B starts → the host lab falls behind. Other groups (FutureHouse, Periodic Labs, Lila Sciences) are building Track B-class systems now.
2. Shared infrastructure means parallel is cheaper than sequential.
3. Track A funds Track B by producing the 6-month "scientific result we shipped" that justifies the platform investment.
4. The platform engineer's skill profile (AI + backend + chemistry-engineering) makes parallel feasible with one full-time owner.

---

## Visual artefacts (Mermaid sources)

See `diagrams/` for renderable Mermaid sources:

| File | Diagram type | Shows |
|---|---|---|
| `dual_track_gantt.mmd` | Gantt | Two-track timeline across 18 months with milestones |
| `resource_allocation_pie.mmd` | Pie | Effort allocation per phase (Track A / Track B / Shared / Wet-lab) |
| `dual_track_architecture.mmd` | Flowchart | Architecture overlay showing what each track contributes |
| `decision_register.mmd` | Mindmap | 43-decision register grouped by domain |
| `track_convergence.mmd` | Flow | Where Track A and Track B share components |

---

## How to use this document

- **For grant reviewers / PI:** read this document first. It contains the milestone table that maps every architectural decision to a concrete deliverable with timing and success criteria.
- **For the platform engineer (post-hire):** treat this document as the contract. Each milestone has an ID (A1.1 … B3.6) that should appear in commit messages, sprint planning, and progress reports.
- **For the chemistry team:** the Track A column tells you what to expect from the new system over the first 6-12 months. Most of the chemistry-facing work is Track A.
- **For the agentic-orchestrator chemist users:** Track B is what enables the DMTA loop the host lab will operate in Year 2 and beyond.

This document is updated each time a milestone closes, an ADR changes, or a primary-source citation is added or revised.
