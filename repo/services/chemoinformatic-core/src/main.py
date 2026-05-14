"""FastAPI app factory for the chemoinformatic-core service."""

from fastapi import FastAPI

from api import sanitize, generate, drug_likeness, health


def create_app() -> FastAPI:
    app = FastAPI(
        title="MB Finder v2 — Chemoinformatic Core",
        version="0.1.0-skeleton",
        description=(
            "Metal-extended RDKit sanitization + NatQG geometry + combinatorial "
            "generation. The chemoinformatic backbone of Pillar 2."
        ),
    )

    app.include_router(health.router)
    app.include_router(sanitize.router, prefix="/sanitize", tags=["sanitization"])
    app.include_router(generate.router, prefix="/generate", tags=["combinatorial"])
    app.include_router(drug_likeness.router, prefix="/drug-likeness", tags=["filter"])

    return app
