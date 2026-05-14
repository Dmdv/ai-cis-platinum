# 08 — Implementation Roadmap

**Contents**

- [Principles](#principles)
- [Phase 1 — Foundations (months 0–6)](#phase-1-foundations-months-06)
- [Phase 2 — Modernisation (months 6–12)](#phase-2-modernisation-months-612)
- [Phase 3 — Generative + Scale (months 12–18)](#phase-3-generative-scale-months-1218)
- [Team composition assumptions](#team-composition-assumptions)
- [Critical path](#critical-path)
- [Risk-weighted timeline (Gantt summary)](#risk-weighted-timeline-gantt-summary)
- [Success metrics](#success-metrics)


## Principles

- **Reproduce first, extend second.** Before any new capability ships, the existing MKANO + MB Finder behaviour must be reproducible in the new system.
- **Vertical slices, not horizontal layers.** Each milestone delivers an end-to-end thin slice (data → model → API → UI), not a complete layer in isolation.
- **Continuous chemist involvement.** Every milestone is reviewed by a chemist collaborator; the system is built *with* the host lab, not handed to it.
- **Public visibility.** Major milestones are accompanied by an open-access dataset release or a preprint, maintaining an open-science posture.

## Phase 1 — Foundations (months 0–6)

**Objective:** A reproducible, productionised baseline of MKANO + MB Finder, extended to two additional metals (Au, Cu).

### Milestones

| Month | Milestone | Pillar |
|---|---|---|
| 1 | Repo + CI/CD operational; container builds; PostgreSQL + RDKit-cartridge deployed. | 4 |
| 1 | Ingestion of the 3,725 Pt complex dataset + 214,373 unlabeled SMILES into the data lake. | 4 |
| 2 | Strategy-pattern refactor of the metal-extended sanitization; Pt strategy ports MKANO logic 1:1. | 2 |
| 2 | Geometry-aware backbone (Equiformer + tmQM pretraining) initial benchmark. | 1 |
| 3 | MKANO reproduced inside the new training pipeline; matches paper numbers within tolerance. | 1 |
| 3 | Au sanitization strategy operational; first 100 Au complexes ingested. | 2 |
| 4 | Inference API live; web UI v2 alpha serving single-molecule predictions. | 4 |
| 4 | Cu sanitization strategy operational. | 2 |
| 5 | Multi-omics MoA service replays PlatinAI mechanism study; matches manually identified targets. | 2 |
| 5 | First agentic Design + Analysis pilot (compute-only, no wet-lab) on a synthetic objective. | 3 |
| 6 | MB Finder v2 alpha released for internal review; principal-investigator sign-off; internal dogfooding begins. | 4 |
| 6 | Phase 1 retrospective + Phase 2 plan reviewed. | — |

### Definition of done
- All paper-reported numbers reproducible from a tagged commit.
- Two metals beyond Pt operating end-to-end.
- Observability, CI/CD, model registry live.
- Source-paper test set passing without regression.

## Phase 2 — Modernisation (months 6–12)

**Objective:** Bring the AI stack into 2026 capability and put the first agentic DMTA loop in front of chemists.

### Milestones

| Month | Milestone | Pillar |
|---|---|---|
| 7 | AlphaFold 3 (self-hosted) + Boltz-2 service deployed; first target-aware prediction run. | 1 |
| 7 | ChemFM LoRA fine-tune trained; benchmarked against MKANO+. | 1 |
| 8 | Geometry-aware MKANO+ replaces baseline MKANO for production scoring; cis/trans classification head live. | 1 |
| 9 | Re and Ru sanitization strategies operational. | 2 |
| 9 | Synthesis + Assay agents (Pillar 3) connected to ELN / LIMS. | 3 |
| 10 | First end-to-end DMTA campaign on a real lab objective (e.g. Au(III) hit-to-lead for A2780cis). | 3 |
| 11 | Cross-project knowledge graph (ElementKG+) live; first cross-project insight surfaced. | 2 |
| 11 | Multi-omics MoA pipeline applied to one ICD compound + one tubulin compound. | 2 |
| 12 | Phase 2 review; preprint draft on multi-metal modernisation. | — |

### Definition of done
- Geometry-aware + target-aware predictions live.
- One real DMTA campaign completed through the agent loop.
- All six target metals supported end-to-end.
- Multi-omics MoA pipeline validated on three independent compound classes.

## Phase 3 — Generative + Scale (months 12–18)

**Objective:** Truly generative metallodrug design; production-grade scale; public visibility.

### Milestones

| Month | Milestone | Pillar |
|---|---|---|
| 13 | Equivariant-diffusion generator producing novel candidates; hybrid with fragment assembly. | 1 |
| 14 | First batch of 5 diffusion-generated candidates synthesised; assayed; results back. | 1, 3 |
| 15 | Instrument integration (HPLC, plate reader) where SiLA/OPC-UA available. | 3 |
| 16 | Cost optimisation: scale-to-zero outside business hours; spot instance use for training. | 4 |
| 16 | Public API SDKs (Python, JS) released; FAIR-data audit. | 4 |
| 17 | Preprint and major-release announcement; updated MB Finder v2 dataset CC-BY-4.0 release. | — |
| 18 | Phase 3 retrospective; next 18-month plan. | — |

### Definition of done
- At least one diffusion-generated, experimentally validated metallodrug.
- FAIR-data audit passed.
- Public open-data release accompanied by preprint.

## Team composition assumptions

This roadmap assumes one dedicated full-time platform engineer plus the host lab's existing team. The platform engineer is the sole operator of Pillar 4 and a primary contributor to Pillars 1–3, in collaboration with:

- **Principal investigator** — strategic direction, prioritisation, manuscript leadership.
- **Chemistry team** — synthesis routes, chemoinformatic rule validation.
- **Biology team** — in vitro / in vivo execution, MoA validation.
- **Theoretical chemistry collaborators** — geometry-aware modelling input, tmQM dataset access.
- **PhD students / research assistants** — campaign execution, dataset curation.

The roadmap is deliberately conservative on team-growth assumptions: it does not require new hires beyond the platform engineer.

## Critical path

The single most critical thread is the **geometry-aware modelling work in Phase 1–2** (Pillar 1). Without geometry support, none of the downstream improvements (target-aware design, multi-metal generalisation, generative diffusion) deliver their full value. If a phase needs descoping, the recommended order of cuts is:

1. Cross-project knowledge graph (Phase 2 → Phase 3).
2. Cost-optimisation and SDKs (Phase 3 → Phase 4).
3. Instrument integration (Phase 3 → Phase 4).

Geometry-aware modelling, multi-metal sanitization, and the agentic-DMTA pilot are non-negotiable.

## Risk-weighted timeline (Gantt summary)

```
Phase 1   |█████████████████████|                                          |
Phase 2                         |██████████████████████|                   |
Phase 3                                                |██████████████████|
          0    1    2    3    4    5    6    7    8    9   10   11  ... 18 months

Critical-path items (Pillar 1 + Pillar 3 wet-lab integration) shown as ▒ overlay
```

## Success metrics

| Phase | Metric | Target |
|---|---|---|
| Phase 1 | MKANO reproduction parity | within ±2 % ROC-AUC of paper baseline |
| Phase 1 | Au + Cu sanitization success rate | ≥ 90 % per metal |
| Phase 1 | API availability | ≥ 99.5 % |
| Phase 2 | Geometry classification accuracy | ≥ 90 % on held-out cis/trans isomers |
| Phase 2 | DMTA cycle time (1st campaign) | ≤ 4 weeks vs prior 12+ weeks |
| Phase 2 | Multi-omics MoA accuracy | top-5 target list contains the validated target |
| Phase 3 | Diffusion-generated hits | ≥ 1 experimentally validated active candidate |
| Phase 3 | FAIR data audit score | passing across all four FAIR criteria |
| Phase 3 | Cost per inference | ≤ US $0.001 single-molecule prediction |
