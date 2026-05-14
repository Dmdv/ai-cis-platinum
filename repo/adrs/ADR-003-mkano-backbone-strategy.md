# ADR-003 — MKANO retained alongside foundation-model backbone

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** Pillar 1 introduces a chemistry foundation model (ChemFM-LoRA) as a candidate replacement for the MKANO contrastive GNN backbone. The decision is whether to replace or to add.

## Decision

Retain MKANO+ (the geometry-enhanced upgrade of MKANO) as the primary production model. Treat ChemFM-LoRA as a *secondary opinion* model, deployed in parallel. Final predictions surface both scores and an ensemble.

## Rationale

- MKANO was carefully tuned for transition-metal chemistry and pretrained on 214,373 metal complexes — a corpus ChemFM does not include.
- Domain-specialised models frequently outperform much larger generalist ones on narrow datasets; the source paper itself benchmarks this for KANO vs MKANO.
- Replacing MKANO without overwhelming evidence would erase a proven, peer-reviewed component.
- Running both is operationally cheap: both fit in the same model registry; the second-opinion call adds <200 ms.
- The dual-model ensemble provides a calibration cross-check: divergence between models is a useful signal for chemist review.

## Consequences

- Two models must be maintained, retrained, and registered. Mitigated by the unified training pipeline.
- Slightly higher inference cost (≈1.2× single-model) — well within budget.
- ECE-style calibration metrics may differ between models; the system tracks both.

## Alternatives considered

- **Replace MKANO with ChemFM:** rejected — premature given MKANO's published performance.
- **Use ChemFM only as a featuriser** (frozen encoder feeding MKANO classifier head): considered; will be evaluated as a third configuration in benchmarking. Not the default.
- **Train ChemFM from scratch on metals:** rejected — prohibitive compute cost; LoRA fine-tuning gets >90 % of the benefit.

## Revisit conditions

- ChemFM-LoRA exceeds MKANO+ by ≥5 % ROC-AUC across all four cell lines and under all three split protocols.
- A successor chemistry foundation model (e.g. ChemFM v2) is released with substantially better metal-complex coverage.
