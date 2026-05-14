"""/sanitize endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..schemas import SanitizedComplex
from ..strategies import get_strategy

router = APIRouter()


class SanitizeRequest(BaseModel):
    """Input contract for the /sanitize endpoint.

    Sent as a JSON body (not query parameters) because SMILES of organometallic
    complexes routinely exceed 200 characters; many CDNs / load balancers cap
    query strings at 2 KB which would refuse long valid inputs.
    """
    smiles: str = Field(..., description="Input SMILES (may include charges, dative bonds, etc.).")
    metal: str = Field(default="auto", description='Explicit metal symbol or "auto" to detect.')
    return_geometry: bool = Field(
        default=False,
        description="If true, the response includes the NatQG geometry features (extra compute).",
    )


@router.post("", response_model=SanitizedComplex)
async def sanitize(req: SanitizeRequest) -> SanitizedComplex:
    """Sanitize a SMILES string, returning the canonical metal-aware graph.

    Raises:
        HTTPException 400: if SMILES is malformed.
        HTTPException 422: if no sanitization strategy is registered for the metal.
    """
    metal = req.metal
    if metal == "auto":
        # Detection logic implemented in Phase 1.
        raise HTTPException(status_code=501, detail="auto-detection pending implementation")

    try:
        strategy = get_strategy(metal)
    except KeyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        result = strategy.sanitize(req.smiles)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="skeleton — implementation pending")

    # Drop the natqg_geometry payload unless explicitly requested.
    if not req.return_geometry:
        result.natqg_geometry = None
    return result
