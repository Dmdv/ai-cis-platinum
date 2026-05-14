"""FastAPI app factory for the inference-api service."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="MB Finder v2 — Inference API",
        version="0.1.0-skeleton",
        description=(
            "Synchronous and asynchronous metallodrug activity prediction. "
            "Wraps the MLflow model registry and the AF3/Boltz-2 structure-prediction "
            "service. Combines MKANO+ and ChemFM-LoRA backbones into an ensemble."
        ),
    )

    # Routers registered in Phase 1.
    return app
