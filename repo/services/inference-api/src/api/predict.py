"""/predict endpoints for the inference-api service."""

from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field


router = APIRouter()


#: Public model-alias surface. Clients select via the alias; the server resolves
#: the alias to a concrete MLflow registry version at request time. Concrete
#: versions are returned via the ``X-Model-Version`` response header so that
#: clients can record reproducibility metadata without coupling to MLflow's
#: naming scheme.
ModelAlias = Literal["latest", "stable", "experimental"]


class PredictRequest(BaseModel):
    smiles: str = Field(..., description="Input SMILES string of the candidate complex.")
    cell_lines: list[str] = Field(default_factory=lambda: ["A2780", "A2780cis", "MCF-7", "A549"])
    model_alias: ModelAlias = Field(
        default="stable",
        description=(
            "Public model selector. The server resolves this alias to a "
            "concrete model version at request time and reports the resolved "
            "version in the X-Model-Version response header."
        ),
    )
    return_explainability: bool = False
    return_geometry_classification: bool = True


class CellLineActivity(BaseModel):
    cell_line: str
    predicted_class: Literal["active", "inactive"]
    probability: float
    predicted_ic50_uM: float | None
    confidence_interval: tuple[float, float] | None


class GeometryPrediction(BaseModel):
    coordination_geometry: str       # square_planar / octahedral / ...
    cis_trans: Literal["cis", "trans", "n/a"] | None


class PredictResponse(BaseModel):
    mb_id: str | None
    inchi_key: str
    model_version: str                # concrete version actually used (mkano-plus@2.1.0)
    activities: list[CellLineActivity]
    geometry: GeometryPrediction | None
    target_engagement: dict[str, float] | None    # protein_id -> binding score


class TargetAwarePredictRequest(PredictRequest):
    protein_targets: list[str] = Field(
        ..., description="UniProt IDs of protein targets to condition on (e.g. ['P02462'] for COL3A1)."
    )


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest, response: Response) -> PredictResponse:
    """Synchronous single-molecule prediction.

    Server resolves ``request.model_alias`` to a concrete version via the
    MLflow registry and sets the ``X-Model-Version`` response header for
    client-side reproducibility logging.
    """
    raise NotImplementedError("skeleton — Phase 1 deliverable")


@router.post("/predict/target-aware", response_model=PredictResponse)
async def predict_target_aware(request: TargetAwarePredictRequest, response: Response) -> PredictResponse:
    """Target-aware prediction conditioned on protein binding (AF3/Boltz-2 integration)."""
    raise NotImplementedError("skeleton — Phase 2 deliverable")
