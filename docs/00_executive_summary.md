# 00 — Executive Summary

## The opportunity

In March 2026 the source paper *Overcoming cisplatin resistance with AI-driven metallodrug discovery* (Rusanov et al., ChemRxiv 2026, DOI 10.26434/chemrxiv-2025-pp32k/v2) reported the first end-to-end deep-learning pipeline that successfully designed, synthesised, and *in vivo* validated a novel platinum complex (PlatinAI) capable of bypassing cisplatin resistance. The work combined a manually curated dataset of 3,725 Pt complexes, a metal-extended RDKit sanitization routine, a knowledge-graph-enhanced contrastive GNN (MKANO), and the publicly deployed MB Finder web platform.

The paper's own conclusion identifies two limitations and a stated roadmap: (i) inability to predict cis/trans geometry, and (ii) the de novo design is fragment-based rather than truly generative. It declares an intent to address both, plus to scale across the metal-based chemistry the source authors are publishing on (Au, Cu, Re, tin).

## The architecture in one paragraph

This document specifies **MB Finder v2**, the next-generation evolution of the MKANO / MB Finder system: a multi-metal, geometry-aware, agent-orchestrated, production-grade AI drug-discovery platform. The design is structured as four self-contained engineering pillars. Pillar 1 modernises the AI stack (geometry-aware models, AF3 / Boltz-2 integration for target-aware design, chemistry foundation models replacing the MKANO backbone, equivariant diffusion for truly generative design). Pillar 2 generalises the metal-extended pipeline beyond platinum to the broader transition-metal therapeutic space, and links the system to adjacent research lines in the metallodrug community (microbiome cancer therapies, immunogenic cell death, tubulin targeting). Pillar 3 wraps the system in an LLM-orchestrated Design–Make–Test–Analyze loop that compresses the wet-lab cycle while preserving chemist oversight. Pillar 4 productionises the entire stack with MLOps, reproducibility, FAIR data, scalable inference, and observability — engineering capabilities that academic metallodrug discovery groups typically lack a dedicated specialist for.

## Why this multidisciplinary profile

The MKANO source paper (Rusanov et al., 2026) explicitly argues that the field's bottleneck is the rare convergence of chemoinformatic expertise, AI engineering, and backend software development in a single operator. A single researcher with combined AI, backend, software development, and chemistry engineering expertise can execute every component of MB Finder v2: modifying RDKit's low-level metal parser, training contrastive GNNs, designing PostgreSQL chemical schemas, deploying containerised model microservices, and writing the LLM-agent code that orchestrates the DMTA loop. The architecture maps each technical artefact to that skill set.

## Headline numbers and commitments

| Dimension | MKANO (current) | MB Finder v2 (proposed) | Source of improvement |
|---|---|---|---|
| Metals supported | Pt only | Pt, Au, Cu, Re, Ru, Pd | Pillar 2 multi-metal parser |
| Geometry awareness | None (SMILES only) | cis/trans, octahedral, square-planar | Pillar 1 geometry models + tmQM pretraining |
| Target awareness | None | AF3 / Boltz-2 conditioning on protein targets | Pillar 1 |
| De novo strategy | Fragment assembly (427 scaffolds) | Equivariant diffusion + fragment hybrid | Pillar 1 |
| DMTA cycle time | Months (manual) | Weeks (agent-orchestrated) | Pillar 3 |
| Reproducibility | Research-grade | Production MLOps, FAIR data | Pillar 4 |
| Scale of inference | Static batch | Real-time multi-tenant API | Pillar 4 |
| Adjacent-science integration | None | Microbiome / ICD / tubulin multi-omics | Pillar 2 |

## Roadmap snapshot

The architecture commits to a phased implementation:

- **Months 0–6:** Reproduce MKANO in the new system; add multi-metal sanitization; deploy productionised MB Finder v2 alpha.
- **Months 6–12:** Geometry-aware modelling; AF3/Boltz-2 target-aware extension; first generative-diffusion prototype; first agentic DMTA pilot.
- **Months 12–18:** Cross-project integration (microbiome, ICD, tubulin), multi-omics MoA inference pipeline, public release of MB Finder v2.

## Risk posture

The architecture does not promise capabilities that are scientifically unproven. Every component cited (AF3, Boltz-2, ChemFM, ChemCrow, equivariant diffusion, tmQM datasets) is published, validated, and operational in 2025–2026. Risk mitigation is treated as a first-class concern in `docs/09_risks_and_mitigations.md`. The primary residual risk is engineering throughput — addressed by the phased roadmap and by a dedicated full-time platform owner.
