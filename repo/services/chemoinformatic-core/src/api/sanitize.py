"""/sanitize endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from schemas import SanitizedComplex
from strategies import get_strategy


router = APIRouter()


class SanitizeRequest(BaseModel):
    smiles: str
    metal: str = "auto"
    return_geometry: bool = False


@router.post("", response_model=SanitizedComplex)
async def sanitize(smiles: str, metal: str = "auto") -> SanitizedComplex:
    """Sanitize a SMILES string, returning the canonical metal-aware graph.

    Args:
        smiles: input SMILES string (may include charges, dative bonds, etc.).
        metal: explicit metal centre, or "auto" to detect.

    Raises:
        HTTPException 400: if SMILES is malformed.
        HTTPException 422: if no sanitization strategy is registered for the metal.
    """
    if metal == "auto":
        # Detection logic implemented in Phase 1.
        raise HTTPException(status_code=501, detail="auto-detection pending implementation")

    try:
        strategy = get_strategy(metal)
    except KeyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        return strategy.sanitize(smiles)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="skeleton — implementation pending")
