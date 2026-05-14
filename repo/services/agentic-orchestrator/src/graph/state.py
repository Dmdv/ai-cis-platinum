"""
Campaign state — the checkpointable object that the entire DMTA loop mutates.

LangGraph persists this between agent invocations. PostgreSQL is the durable
store; Redis is the short-lived working memory.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


CampaignStage = Literal[
    "planning",
    "designing",
    "awaiting_chemist_approval",
    "synthesising",
    "assaying",
    "analysing",
    "reporting",
    "complete",
    "halted",
]


class CandidateCompound(BaseModel):
    mb_id: str | None
    smiles: str
    proposed_by_agent: str             # "design"
    predicted_probability: dict[str, float]   # cell_line -> probability
    target_engagement: dict[str, float] | None  # protein -> binding score
    drug_likeness_passes: bool
    novelty_verified: bool


class SynthesisRecord(BaseModel):
    candidate_mb_id: str
    eln_entry_id: str | None
    retrosynthesis_steps: int
    status: Literal["pending", "in_progress", "complete", "failed"]


class AssayResult(BaseModel):
    candidate_mb_id: str
    cell_line: str
    ic50_uM: float
    confidence_interval: tuple[float, float]
    n_replicates: int
    raw_data_lake_uri: str


class CampaignDecision(BaseModel):
    timestamp: datetime
    agent: str
    decision: str
    rationale: str
    requires_human_approval: bool
    approved_by_user_id: str | None
    approved_at: datetime | None


class CampaignState(BaseModel):
    campaign_id: str
    objective: str                     # chemist's natural-language objective
    stage: CampaignStage = "planning"
    candidates: list[CandidateCompound] = Field(default_factory=list)
    syntheses: list[SynthesisRecord] = Field(default_factory=list)
    assay_results: list[AssayResult] = Field(default_factory=list)
    decisions: list[CampaignDecision] = Field(default_factory=list)
    token_budget_remaining: int
    started_at: datetime
    updated_at: datetime
