"""FastAPI app factory for the ingestion service."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="MB Finder v2 — Ingestion",
        version="0.1.0-skeleton",
        description="Data ingestion pipelines: external databases, literature, ELN.",
    )
    return app
