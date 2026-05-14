# 09 — Risks and Mitigations

**Contents**

- [Technical risks](#technical-risks)
- [Data risks](#data-risks)
- [Operational risks](#operational-risks)
- [Scientific and reputational risks](#scientific-and-reputational-risks)
- [Strategic risks](#strategic-risks)
- [Risk register summary](#risk-register-summary)


A frank assessment of what can go wrong with the proposed system and how each risk is addressed in the architecture.

## Technical risks

### R1 — Geometry-aware ML may not lift accuracy meaningfully
The source paper hypothesises geometry is critical for activity, but the empirical lift on the host lab's actual dataset is not known a priori. Adding geometry could underperform if the labeled dataset is too small to leverage geometric features.

**Mitigation:**
- Pretrain on the 86 K tmQM corpus before fine-tuning on Pt data, so the geometry encoder is not learning from scratch on the host lab's small labeled set.
- Run as an ablation: baseline (SMILES only) vs geometry-aware on identical splits. Promote geometry only if the lift is significant.
- Retain the baseline MKANO+ in the model registry as a fallback.

### R2 — AF3 / Boltz-2 inaccuracy on transition metals (hardened with primary-source numbers)
AF3's ≈76 % protein–ligand binding pose accuracy is reported on the PoseBusters-curated PDBbind subset, not specifically on metal-containing ligands. Additional independently documented failure modes (per Perera synthesis, *The Lab Without Scientists*, Jan 2026, citing peer-reviewed evaluations):
- **AF3 hallucinated structured conformations in 22 % of intrinsically disordered proteins** in a 72-protein DisProt analysis (October 2025 preprint) — imposes order where none naturally exists.
- **AF3 chirality violation rate: 4.4 %** on PoseBusters — molecules predicted with the wrong handedness. For Pt-anticancer work where cis/trans isomerism determines activity, this is a load-bearing risk.

**Mitigation:**
- Validate AF3 / Boltz-2 against the 19 experimentally-screened Pt complexes from the source paper — if either predicts known PlatinAI–COL3A1 binding, that is corroborating evidence.
- Use structure predictions as conditioning signals, not as hard predictions; the downstream scorer learns whether to weight them.
- Combine AF3 + Boltz-2 as an ensemble; trust agreement, flag disagreement.
- **Mandatory metal-aware re-docking** (Pillar 1 Component 1.2.1) on every AF3 receptor prediction; never rely on AF3 alone for the Pt-complex pose.
- **Chirality cross-check** as a hard gate in Pillar 3's Design agent — any candidate whose predicted geometry contradicts the metal's known coordination geometry is rejected before reaching a chemist.

### R3 — ChemFM fine-tuning fails to beat MKANO
Domain-specialised models sometimes outperform much larger generalist ones on narrow datasets.

**Mitigation:**
- Treat ChemFM as a *secondary* opinion, not a replacement. MKANO+ remains the primary classifier.
- LoRA-adapter fine-tuning keeps GPU cost manageable; if ChemFM does not deliver, the experiment is cheap to retire.
- Ensemble approach can extract the best of both.

### R4 — Equivariant-diffusion stability and synthesisability on the small Pt corpus
Equivariant diffusion is an under-tested choice for a 17,732-labelled-IC50 + 214 K-unlabelled Pt corpus. Joshi (*Equivariance is dead, long live equivariance?*, Substack June 2025) explicitly argues that diffusion-generation is moving away from equivariance toward scaling; equivariant networks are "orders of magnitude slower" to train than standard Transformers, and the Pt corpus is small by foundation-model standards. The training-stability risk on the specialised Pt corpus is real, and even valid samples may be synthetically inaccessible.

**Mitigation:**
- **JT-VAE (Strandgaard / Balcells *JACS Au* 2025) is the Phase-2 primary generative track**, not equivariant diffusion. JT-VAE has working open-source code, a published wet-lab-validated precedent on transition-metal ligands, and the junction-tree formulation enforces chemical validity by construction.
- Equivariant diffusion is downgraded to a **Phase-3 conditional benchmark** with explicit retirement criteria (Pillar 1 Component 1.4.2): if training stability fails, or if Phase-3 head-to-head benchmark shows ≥ 5-point worse chemical-validity × novelty × IC50-rank-recall vs JT-VAE, or if wall-clock cost ≥ 3× JT-VAE, the diffusion track is retired.
- All sampled candidates pass through the chemoinformatic core's drug-likeness and synthesis-feasibility filters before being shown to a chemist.
- Retrosynthesis analysis (AiZynthFinder + IBM RXN) is a required step before any candidate is nominated for synthesis.
- The generator stack remains *hybrid* with fragment assembly: fragment-based candidates retain known synthesisability while the chosen ML generator (JT-VAE primary, diffusion conditional) supplies novelty.

### R5 — Agent hallucination
LLM agents may propose incorrect or unsafe chemistry.

**Mitigation:**
- Every Design-agent output is sanitized through the chemoinformatic core before being shown to a human.
- All wet-lab steps require explicit chemist sign-off via the web UI.
- All agent actions are logged with justifications and replayable.
- Risk levels on tools (`safe` / `moderate` / `dangerous`) gate auto-execution; dangerous actions always require human approval.

## Data risks

### R6 — Curation backlog
Literature mining + manual ChemDraw redrawing is slow; the 3,725-compound dataset took the source authors years to assemble.

**Mitigation:**
- Pillar 4 includes AI-assisted OCR + structure recognition (MolScribe, RxnScribe) to triage candidates for human review.
- The curation queue is a first-class UI; chemists can review a flagged compound in < 2 min.
- Au / Cu / Re datasets bootstrap from MetAP DB + targeted literature pulls.

### R7 — Per-metal sanitization rules may misclassify edge cases
Each metal strategy encodes empirical rules; edge cases will exist.

**Mitigation:**
- Failure rate is tracked per metal as a data-quality metric.
- Failed complexes route to the curation queue, not to silent rejection.
- Rule documentation is a markdown file per metal, reviewed by senior chemists.

### R8 — Cell-line metadata drift
Cellosaurus updates can rename or merge lines; archived data may carry inconsistent names.

**Mitigation:**
- Nightly reconciliation job against Cellosaurus.
- All cell lines carry an immutable internal ID; external aliases are mutable.
- Schema migrations are reversible.

## Operational risks

### R9 — Cloud cost overruns
GPU spend can run away.

**Mitigation:**
- Hard budget cap per project; alert at 110 %.
- Scale-to-zero overnight; spot instances for training.
- Caching at every layer (Redis for inference, MLflow for trained models, browser-side for the UI).
- Quarterly cost review by the platform engineer.

### R10 — Operational fragility around a single engineer
If the platform engineer leaves, the stack risks becoming unmaintained.

**Mitigation:**
- Every architectural decision captured as an ADR.
- Each pillar carries a runbook (operate / debug / extend).
- Cross-train one or two team members as secondary operators for routine ops (deploys, dashboards, backups).
- Avoid bespoke technology where standard alternatives exist.

### R11 — Vendor lock-in
ELN APIs, LLM APIs, structure-prediction APIs evolve.

**Mitigation:**
- All external dependencies behind adapter interfaces.
- Open-source equivalents always identified for each commercial dependency.

## Scientific and reputational risks

### R12 — A model output influences a published claim incorrectly
The system supports decisions that lead to publications; an undetected model error could compromise the host lab's reputation.

**Mitigation:**
- All model outputs in published material carry version + dataset hash + confidence interval.
- The MoA inference module always presents *ranked* candidate targets with evidence scores, never a single "the answer".
- Chemists are the authorial decision-makers; the system is an assistant.

### R13 — Open-data release accidentally exposes proprietary or pre-publication data
An open-access posture is a strength but creates leak surface.

**Mitigation:**
- All datasets carry a `release_state` field (`internal`, `pre-publication`, `public`).
- Public APIs filter on `release_state = public`.
- Releases require explicit principal-investigator approval.

### R14 — Regulatory / licensing pitfalls in AI-driven drug design
Some jurisdictions are evolving rules around AI-derived novel chemical matter.

**Mitigation:**
- Every claim about a candidate compound carries the model and dataset metadata.
- The system is positioned as a research-acceleration tool, not as a regulatory-submission-ready instrument.
- The host institution's research office is consulted before any commercial-direction extensions.

## Strategic risks

### R15 — Scope creep
The proposal is ambitious; mid-project addition of new ideas can derail the roadmap.

**Mitigation:**
- The roadmap is the contract; any addition must replace an existing item or extend a phase.
- The four-pillar structure is the architectural contract — new features must fit a pillar; orphan features are declined.
- Quarterly steering reviews with the principal investigator to keep the architecture in scope.

### R16 — Existing workflow is disrupted in transition
Introducing new tools to a working lab carries change-management cost.

**Mitigation:**
- The existing MB Finder system remains operational during the transition; v2 launches alongside, not replacing it.
- Chemists are involved in design from Phase 1; the system is built *for* them.
- Adoption metrics are tracked (active users, weekly campaigns); friction is escalated and addressed.

## Risk register summary

| ID | Risk | Likelihood | Impact | Mitigation status |
|---|---|---|---|---|
| R1 | Geometry doesn't help | Low | Low | Strong mitigation (ablation) |
| R2 | AF3 inaccurate on metals | Medium | Medium | Mitigated (ensemble + validation) |
| R3 | ChemFM doesn't beat MKANO | Medium | Low | Mitigated (treated as secondary) |
| R4 | Unsynthesisable diffusion outputs | High | Medium | Mitigated (filters + retrosynthesis) |
| R5 | Agent hallucination | High | High | Strongly mitigated (sanitization + HITL) |
| R6 | Curation backlog | Medium | Medium | Mitigated (AI-assist + queue) |
| R7 | Sanitization edge cases | Medium | Low | Mitigated (tracked + queued) |
| R8 | Cell-line metadata drift | Low | Low | Mitigated (nightly sync) |
| R9 | Cloud cost overruns | Medium | Medium | Mitigated (caps + scale-to-zero) |
| R10 | Single-engineer fragility | Medium | High | Partially mitigated (ADRs + cross-training) |
| R11 | Vendor lock-in | Low | Medium | Mitigated (adapters) |
| R12 | Model error in publication | Low | High | Strongly mitigated (versioning + HITL) |
| R13 | Pre-publication leak | Low | High | Mitigated (release_state field + principal-investigator approval) |
| R14 | Regulatory pitfalls | Low | Medium | Mitigated (compliance review) |
| R15 | Scope creep | High | Medium | Mitigated (roadmap-as-contract) |
| R16 | Workflow disruption | Medium | Medium | Mitigated (parallel run + chemist involvement) |
