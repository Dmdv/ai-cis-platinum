# MB Finder v2 — A Multi-Metal AI-Driven Drug Discovery System

A research architecture and 18-month implementation roadmap for MB Finder v2, a next-generation AI-driven metallodrug discovery platform. The design extends the published MKANO and MB Finder system (Rusanov et al., 2026; ChemRxiv DOI 10.26434/chemrxiv-2025-pp32k/v2) into a multi-metal, geometry-aware, agent-orchestrated, production-grade system.

---

## Reading order

| # | Path | Time | For whom |
|---|---|---|---|
| 1 | `docs/00_executive_summary.md` | 5 min | Anyone — the elevator pitch |
| 2 | `docs/01_problem_and_context.md` | 10 min | Reviewers — establishes shared understanding |
| 3 | `docs/02_high_level_architecture.md` | 15 min | Anyone evaluating fit |
| 4 | `docs/03_pillar1_ai_modernization.md` | 15 min | ML reviewers |
| 5 | `docs/04_pillar2_multimetal.md` | 15 min | Chemistry reviewers |
| 6 | `docs/05_pillar3_agentic_dmta.md` | 15 min | Lab-automation reviewers |
| 7 | `docs/06_pillar4_mlops_backend.md` | 15 min | Engineering reviewers |
| 8 | `docs/07_data_architecture.md` | 10 min | Bioinformatics reviewers |
| 9 | `docs/08_implementation_roadmap.md` | 10 min | Planning reviewers |
| 10 | `docs/09_risks_and_mitigations.md` | 5 min | Planning reviewers |
| 11 | `docs/10_value_proposition.md` | 5 min | Reviewers — fit of multidisciplinary profile to scope |
| 12 | `docs/11_references.md` | reference | All |
| 13 | **`docs/12_dual_track_milestones.md`** | **20 min** | **Reviewers / platform engineer — milestone consolidation across the two parallel tracks (Track A: extend the published MKANO / MB Finder system; Track B: build MB Finder v2). Includes 43-decision register and Phase 1/2/3 milestone IDs.** |

A presentation deck and a skeleton implementation repository accompany the written architecture:

- `slides/presentation.md` — 20-slide Marp-formatted deck.
- `repo/` — skeleton service tree (no business logic), demonstrating the proposed architecture is materialisable.
- `diagrams/` — Mermaid source for all architecture diagrams.

---

## What this package contains

A four-pillar system architecture, each pillar a self-contained design unit with components, contracts, technologies, risks, and a phased implementation plan:

1. **AI modernization** — geometry-aware ML (cis/trans isomer support), AlphaFold 3 / Boltz-2 integration for target-aware design, chemistry foundation models replacing the MKANO backbone, truly generative architectures beyond fragment assembly.
2. **Multi-metal generalisation + adjacent-science integration** — extending the metal-extended chemoinformatic pipeline from Pt-only to Au, Cu, Re, Ru, Pd, and beyond; integrating microbiome, ICD, and tubulin research threads.
3. **Agentic DMTA orchestration** — an LLM-supervised Design–Make–Test–Analyze loop that compresses the wet-lab cycle from months to weeks while preserving chemist oversight.
4. **MLOps and backend infrastructure** — productionised data pipelines, model registry, reproducibility tooling, FAIR data principles, scalable inference, observability — the engineering foundation that the typical academic metallodrug discovery group does not have an in-house specialist for.

---

## Why this specific multidisciplinary profile

The MKANO source paper (Rusanov et al., 2026) argues, in its conclusion, that bridging chemoinformatic theory, deep learning engineering, and backend platform development is the bottleneck of metallodrug AI. The architecture in this package operationalises that argument by mapping each technical capability — modified RDKit metal parsing, contrastive graph training, agentic orchestration, MLOps — to a concrete deliverable a single researcher with combined AI / backend / chemistry-engineering expertise can execute.

A breakdown of skill–component fit is provided in `docs/10_value_proposition.md`.

---

## Status

This is a research design document, not implemented code. The `repo/` directory contains scaffolded module stubs and architectural ADRs to demonstrate that the design is concrete and executable, but no business logic is implemented. The implementation roadmap in `docs/08_implementation_roadmap.md` lays out 6-, 12- and 18-month milestones for the proposed work.
