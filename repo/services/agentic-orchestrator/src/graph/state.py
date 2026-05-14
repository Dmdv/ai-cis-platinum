"""
Campaign state — the checkpointable object that the entire DMTA loop mutates.

LangGraph persists this between agent invocations. PostgreSQL is the durable
store; Redis is the short-lived working memory.

Two shapes:

    CampaignStatePersisted — the durable audit-trail representation.
        Holds every candidate, every synthesis record, every assay result,
        every decision. Grows monotonically over a multi-week campaign.
        Stored in PostgreSQL (campaign_state.persisted JSONB column).

    CampaignStateView      — the compact projection the Supervisor's working
        context sees on each step. Bounded at ≈ 30 KB (per Pillar 3
        context-engineering rule): objective, stage, last few decisions,
        current-step inputs, references (URIs) to large artefacts in the
        data lake. Reconstructed from the Persisted state on demand.

This split implements the Pillar 3 §3.2 context-engineering rule: artefacts
are *referenced* not *inlined* into the working LLM context.
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
    proposed_by_agent: str                              # "design"
    predicted_probability: dict[str, float]             # cell_line -> probability
    target_engagement: dict[str, float] | None          # protein -> binding score
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


# ---------------------------------------------------------------------------
# Durable representation
# ---------------------------------------------------------------------------

class CampaignStatePersisted(BaseModel):
    """Durable, append-mostly campaign state. Source-of-truth for audit /
    reproducibility / regulatory traceability.
    """
    campaign_id: str
    objective: str                                      # chemist's natural-language objective
    stage: CampaignStage = "planning"
    candidates: list[CandidateCompound] = Field(default_factory=list)
    syntheses: list[SynthesisRecord] = Field(default_factory=list)
    assay_results: list[AssayResult] = Field(default_factory=list)
    decisions: list[CampaignDecision] = Field(default_factory=list)
    token_budget_remaining: int
    started_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Bounded working-context projection
# ---------------------------------------------------------------------------

class CandidateRef(BaseModel):
    """Compact reference to a candidate; full record fetched on demand."""
    mb_id: str | None
    smiles: str
    predicted_probability: dict[str, float]


class CampaignStateView(BaseModel):
    """Compact view of campaign state the Supervisor agent reasons over per step.

    Bounded at ≈ 30 KB. Heavy artefacts (raw proteomics tables, full assay
    data, lengthy decision rationales) are accessed via URI references in the
    durable :class:`CampaignStatePersisted`, never inlined here.
    """
    campaign_id: str
    objective: str
    stage: CampaignStage
    recent_decisions: list[CampaignDecision] = Field(
        default_factory=list,
        description="Last 2–3 decisions in the campaign timeline. Older decisions are URI-referenced.",
    )
    current_step_candidates: list[CandidateRef] = Field(
        default_factory=list,
        description="Candidate refs the current step is reasoning about. Full payloads in Persisted.",
    )
    token_budget_remaining: int
    artefact_uris: dict[str, str] = Field(
        default_factory=dict,
        description='URI handles for large artefacts. Keys: "proteomics_table", "rna_seq_counts", '
                    '"assay_raw", etc. Values are object-store URIs the agent can fetch via tool call.',
    )


# Legacy export — kept as an alias so existing imports continue to work
# during the transition to the Persisted/View split.
CampaignState = CampaignStatePersisted
