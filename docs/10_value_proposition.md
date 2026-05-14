# 10 — Value Proposition: Skill–Component Fit

**Contents**

- [The argument](#the-argument)
- [Skill–component matrix](#skillcomponent-matrix)
- [Where the combined background is decisive](#where-the-combined-background-is-decisive)
- [Adjacent expertise the platform engineer does not claim](#adjacent-expertise-the-platform-engineer-does-not-claim)
- [Specific deliverables for the platform engineer](#specific-deliverables-for-the-platform-engineer)
- [Why this profile compounds](#why-this-profile-compounds)


## The argument

The MKANO source paper makes its strongest hiring argument in its conclusion: *"A researcher possessing a combined, deep background in Artificial Intelligence, backend software development, and chemical engineering is uniquely, and perhaps exclusively, positioned to execute this exact paradigm of modern scientific discovery."*

This document instantiates that argument concretely, mapping each component of the proposed MB Finder v2 system to the skill profile required to build it. The intent is to demonstrate that a single platform engineer with combined AI, backend, software development, and chemistry-engineering expertise is sufficient — and arguably necessary — to execute the architecture end-to-end.

## Skill–component matrix

| Pillar | Component | AI/ML | Backend / SWE | Chemistry / chem. eng. |
|---|---|:---:|:---:|:---:|
| 2 | Generalised metal-extended sanitization (Pt → Au, Cu, Re, Ru, Pd) | — | ●●●● | ●●●●● |
| 1 | NatQG geometry pretraining + tmQM integration | ●●●●● | ●● | ●●● |
| 1 | Geometry-aware MKANO+ (SE(3)-equivariant GNN) | ●●●●● | ●● | ●● |
| 1 | AlphaFold 3 / Boltz-2 self-hosted inference service | ●●● | ●●●●● | ● |
| 1 | Target-aware scoring conditioned on COL3A1 / BUB1B | ●●●● | ●● | ●●● |
| 1 | ChemFM LoRA fine-tuning | ●●●● | ●●● | ● |
| 1 | Equivariant-diffusion generator | ●●●●● | ●● | ●●● |
| 2 | Multi-metal MKANO+ multi-task fine-tuning | ●●●● | ●●● | ●●● |
| 2 | Multi-omics MoA inference pipeline | ●●● | ●●●● | ●●● |
| 2 | ElementKG+ unified knowledge graph | ●● | ●●●● | ●●● |
| 3 | LangGraph multi-agent orchestrator | ●●●● | ●●●●● | ●● |
| 3 | Tool-surface contracts (chemoinformatic, retrosynthesis, LIMS) | ●● | ●●●●● | ●●● |
| 3 | ELN / LIMS integration | ● | ●●●●● | ●● |
| 4 | Kubernetes + CI/CD + ArgoCD | — | ●●●●● | — |
| 4 | MLflow model registry + DVC dataset versioning | ●●● | ●●●●● | — |
| 4 | PostgreSQL + RDKit cartridge + pgvector schema | — | ●●●●● | ●● |
| 4 | Observability (Prometheus, Grafana, Loki, Tempo) | — | ●●●●● | — |
| 4 | Data lake medallion architecture (Bronze / Silver / Gold) | ●● | ●●●●● | ●● |
| 4 | FastAPI + Next.js + RDKit-JS web stack | — | ●●●●● | ● |

Filled dots indicate the relative weight of expertise required. The matrix highlights that no single discipline alone covers the full system, and that the *interfaces* between disciplines — where requirements lose fidelity in translation between specialists — are the most demanding components.

## Where the combined background is decisive

### 1. The metal-extended sanitization pipeline
A software engineer without chemistry training would not know which transition-metal-coordination rules to encode. A chemist without backend experience would write a one-off script that does not generalise across metals or integrate cleanly with the rest of the pipeline. The strategy-pattern refactor proposed in Pillar 2 requires *simultaneous fluency* in (a) low-level RDKit internals and (b) coordination chemistry conventions across Pt, Au, Cu, Re, Ru, Pd. This is exactly the chemistry-engineering ↔ software-engineering bridge that the source paper itself identifies as the bottleneck.

### 2. The agentic orchestrator
LangGraph and similar frameworks are AI-engineering tooling, but the agent *prompts*, tool schemas, and risk-level taxonomies must encode the realities of synthesis, in vitro assays, and in vivo studies. A pure AI engineer would underestimate the scientific risk of certain agent actions; a pure chemist would not architect the agents as a clean state machine. The interface is the value.

### 3. The MLOps stack
Productionising a research-grade AI pipeline requires standard MLOps tooling — Kubernetes, MLflow, observability, CI/CD — none of which is novel to industry but is conspicuously *absent* from the typical academic metallodrug discovery group. A senior backend engineer can implement this; a chemist usually cannot. Conversely, configuring the stack so that it serves *chemists* (right ELN integration, right ontology choices, right data licenses) requires understanding the scientific workflow.

### 4. The multi-omics MoA inference pipeline
Statistical genomics (DESeq2, limma, MSstats), knowledge-graph reasoning, and chemistry context all converge. The PlatinAI mechanism analysis in the source paper synthesised these manually; the proposed automation requires a researcher comfortable with each.

### 5. The generative-diffusion architecture
Equivariant diffusion models are non-trivial AI engineering. Adapting them to the metallodrug context requires understanding cis-trans influence, coordination preferences, and synthetic accessibility. Pure AI researchers tend to optimise for valid graphs; chemists need *synthesisable* graphs. The combined profile bridges that gap.

## Adjacent expertise the platform engineer does not claim

To remain credible, the architecture also identifies what the platform engineer will *not* lead and where collaboration with existing team members is essential:

- **Synthetic route execution** — owned by the chemistry team.
- **In vivo studies (mouse models, dosing)** — owned by the biology team.
- **DFT / quantum chemistry interpretation** — owned by theoretical chemistry collaborators.
- **Clinical translation strategy** — owned by the principal investigator and external clinical collaborators.

The role described here is a *platform researcher* who builds the system that amplifies these specialists, not a researcher who replaces them.

## Specific deliverables for the platform engineer

The platform engineer authors the following components end-to-end:

| Component | Estimated personal contribution |
|---|---|
| Metal-extended sanitization refactor + Au/Cu/Re/Ru/Pd strategies | ~95 % (with chemistry review) |
| MLOps stack (Kubernetes, MLflow, DVC, CI/CD, observability) | ~100 % |
| Inference API + web UI v2 | ~85 % (UI design review by chemists) |
| Agentic orchestrator + tool contracts | ~95 % |
| Multi-omics MoA inference service | ~70 % (with bioinformatics review by the biology team) |
| Geometry-aware MKANO+ training pipeline | ~80 % (with theoretical-chemistry input) |
| Equivariant-diffusion generator | ~80 % |
| Cross-project knowledge graph | ~85 % |
| Data architecture + medallion pipeline | ~100 % |

## Why this profile compounds

A host lab investing in this profile receives, in addition to the deliverables above, three durable assets:

1. **Replicable infrastructure.** Each pillar's design is portable to other research lines the host lab may launch in future — the system is *not* a one-off metallodrug project.
2. **Published methods.** Pillar 1 (geometry-aware metallodrug ML) and Pillar 3 (agentic DMTA for metallodrugs) are each publishable contributions in their own right.
3. **Recruitment compounding.** A modernised platform attracts AI-curious chemistry students and chemistry-curious computational students; the host lab's interdisciplinary recruitment is reinforced.
