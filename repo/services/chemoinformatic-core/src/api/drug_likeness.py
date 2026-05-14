"""/drug-likeness endpoint — modified Lipinski filter for metallodrugs."""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class LipinskiResult(BaseModel):
    passes: bool
    molecular_weight: float
    logp: float
    hbd: int
    hba: int
    rotatable_bonds: int
    molar_refractivity: float
    atom_count: int
    failed_rules: list[str]


@router.post("", response_model=LipinskiResult)
async def drug_likeness(smiles: str) -> LipinskiResult:
    """Apply modified Lipinski's Rule of Five thresholds.

    Thresholds (from source paper):
        molecular weight < 500 Da
        logP            ≤ 5
        hbd             ≤ 5
        hba             ≤ 10
        rotatable bonds ≤ 10
        molar refractivity 40-130
        atom count      20-70
    """
    raise NotImplementedError("skeleton — Phase 1 deliverable")
