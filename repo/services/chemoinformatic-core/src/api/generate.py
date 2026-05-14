"""/generate/combinatorial endpoint — fragment assembly generation (Pillar 2)."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/combinatorial")
async def combinatorial(
    metal: str,
    seed_ligand_set: list[str] | None = None,
    n_candidates: int = 100,
) -> dict:
    """Combinatorially assemble candidate complexes.

    Mirrors the paper's fragment-assembly approach:
      1. extract top-K ligand fragments from active actives,
      2. permute under chemical heuristics (cis-trans influence,
         electronic/steric compatibility),
      3. filter by modified-Lipinski drug-likeness,
      4. cross-reference against existing databases (novelty check),
      5. return ranked candidate list for downstream scoring.
    """
    raise NotImplementedError("skeleton — Phase 1 deliverable")
