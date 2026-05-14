"""
Training entrypoint for MB Finder v2 models.

Invoke via:
    python train.py +model=mkano_plus_geometry +data=platinum_v1

Hydra resolves the model and data configs from `configs/`. MLflow tracking
URI is read from $MLFLOW_TRACKING_URI. DVC dataset version is captured
automatically from the working tree.
"""

from __future__ import annotations


def main() -> None:
    """Skeleton entrypoint — implementation in Phase 1 milestone 3."""
    raise NotImplementedError(
        "skeleton — Phase 1 milestone 3 implements MKANO+ training "
        "with parity validation against the source paper baseline."
    )


if __name__ == "__main__":
    main()
