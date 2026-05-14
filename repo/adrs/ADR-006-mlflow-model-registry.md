# ADR-006 — MLflow as model registry and experiment tracker

**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** Every model in MB Finder v2 must be versioned, reproducibly built, and tied to its training data. The choice of registry sets the operational pattern for the next several years.

## Decision

Use MLflow as the registry and experiment tracker. Back its store with PostgreSQL (metadata) and S3/MinIO (artifacts). Pair with DVC for dataset versioning.

## Rationale

- MLflow is the de facto open-source standard; long-term maintenance and community support are strong.
- Native integration with PyTorch, PyTorch Lightning, and Hydra.
- Registry stages (`None` / `Staging` / `Production` / `Archived`) match our deployment lifecycle.
- Self-hostable; no vendor lock-in.
- Pairs cleanly with DVC: training-run records reference both code commit and DVC dataset hash.

## Consequences

- The MLflow server is now a critical-path service; downtime blocks training and deployment. Mitigated by HA deployment in production (PostgreSQL replica + redundant MLflow server pods).
- Backups must include both PostgreSQL metadata and S3 artifacts. Standard backup procedures cover both.

## Alternatives considered

- **Weights & Biases:** rejected — hosted commercial product; cost and data-sovereignty concerns for academic research.
- **Neptune.ai, Comet:** similar concerns as W&B.
- **Hand-rolled tracking in PostgreSQL:** rejected — reinventing the wheel; MLflow is already what we would build.
- **Hugging Face Hub:** considered for public release of models; complements rather than replaces MLflow.

## Revisit conditions

- MLflow goes out of active maintenance.
- An open-source alternative substantially exceeds MLflow's feature set on the dimensions we care about (lineage, registry, evaluation reproducibility).
