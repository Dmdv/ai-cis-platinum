"""FastAPI app factory for the agentic-orchestrator service."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="MB Finder v2 — Agentic Orchestrator",
        version="0.1.0-skeleton",
        description=(
            "LangGraph-based DMTA orchestrator. Five specialised agents "
            "(Supervisor, Design, Synthesis, Assay, Analysis, Report) coordinate "
            "metallodrug discovery campaigns with human-in-the-loop on every "
            "wet-lab step."
        ),
    )
    return app
