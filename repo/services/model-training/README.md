# model-training

Training jobs for every ML model in MB Finder v2. Not a long-running service — invoked by CI, by the agentic orchestrator (on demand), or by humans for ad-hoc experimentation. Each invocation is an MLflow-tracked run.

## Models trained here

- **MKANO+** (geometry-aware contrastive GNN on tmQM + Pt corpus, classifier + IC50 regressor + geometry head).
- **ChemFM-LoRA** (foundation-model fine-tune).
- **Equivariant-diffusion generator** (Phase 3).
- **MoA inference pipeline components** (DEG/DEP correlation, target-ranking models).
- **Per-metal classifier heads** (Pt, Au, Cu, Re, Ru, Pd).

## Layout

```
src/
├── train.py                       ← entrypoint; hydra-configured
├── models/
│   ├── mkano_plus.py              ← MKANO + geometry head
│   ├── chemfm_lora.py             ← LoRA adapter on ChemFM
│   ├── diffusion.py               ← equivariant diffusion (Phase 3)
│   └── moa_models.py
├── data/
│   ├── datasets.py                ← PyTorch Geometric dataset loaders
│   ├── splits.py                  ← random / scaffold / cluster splits
│   └── geometry_pretraining.py    ← tmQM / tmQMg* corpora
├── eval/
│   ├── metrics.py                 ← ROC-AUC, F1, ECE
│   ├── scientific_validation.py   ← regression tests vs paper baseline
│   └── reports.py
└── configs/                       ← hydra YAML configs per model
    ├── mkano_plus_base.yaml
    ├── mkano_plus_geometry.yaml
    └── chemfm_lora.yaml
```

## Reproducibility

Every run records:
- Git commit hash (auto).
- DVC dataset hash (`dvc.lock`).
- Hydra config hash.
- Container image digest.

Promoted models pass a frozen held-out test set with no regression versus the paper baseline (within ±2 % ROC-AUC).
