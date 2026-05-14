# chemoinformatic-core

The single source of truth for "what is a valid transition-metal complex graph" in MB Finder v2. Generalises the 5-step RDKit metal-extended sanitization documented in Rusanov et al., 2026 from platinum-only into a strategy-pattern API supporting Pt, Au, Cu, Re, Ru, Pd (and easily extensible to others).

This is the **load-bearing chemoinformatic contribution** of Pillar 2. Every other service depends on it.

## What it provides

- `POST /sanitize` — accept SMILES, return sanitized molecular graph + NatQG geometry features.
- `POST /sanitize/batch` — bulk variant for ingestion pipelines.
- `GET /metals` — list supported transition-metal strategies.
- `POST /generate/combinatorial` — fragment-assembly generator (existing MKANO logic, generalised to all metals).
- `POST /drug-likeness` — Lipinski / modified-Lipinski filter for metallodrugs.

## Public API contract

```python
# mbfinder.schemas.chemoinformatic

class SmilesInput(BaseModel):
    smiles: str
    expected_metal: Literal["Pt", "Au", "Cu", "Re", "Ru", "Pd", "auto"] = "auto"
    return_geometry: bool = False

class SanitizedComplex(BaseModel):
    mb_id: str | None                              # if recognised
    inchi_key: str
    sanitized_smiles: str
    metal_centre: str
    oxidation_state: int
    coordination_geometry: Literal["square_planar", "octahedral", "tetrahedral", "linear", "half_sandwich", "unknown"]
    molecular_graph: MolecularGraph                # nodes + edges
    natqg_geometry: NatQGFeatures | None           # if requested
    sanitization_warnings: list[str]
```

## Internal architecture

```
src/
├── main.py                              ← FastAPI app factory
├── api/
│   ├── sanitize.py                      ← /sanitize endpoint
│   ├── generate.py                      ← /generate/combinatorial endpoint
│   └── drug_likeness.py                 ← /drug-likeness endpoint
├── strategies/
│   ├── __init__.py                      ← strategy registry
│   ├── base.py                          ← MetalSanitizer protocol
│   ├── platinum.py                      ← Pt strategy (mirrors paper's 5 steps)
│   ├── gold.py                          ← Au strategy (Au(I)/Au(III), auriophilic, linear)
│   ├── copper.py                        ← Cu strategy
│   ├── rhenium.py                       ← Re strategy (fac-Re(CO)3 motif)
│   ├── ruthenium.py                     ← Ru strategy
│   ├── palladium.py                     ← Pd strategy
│   └── generic.py                       ← fallback for unspecialised metals
├── geometry/
│   ├── natqg.py                         ← NatQG construction from sanitized graph
│   └── geometry_classifier.py           ← cis/trans / fac/mer head
├── combinatorial/
│   ├── fragment.py                      ← graph fragmentation
│   ├── ligand_library.py                ← top-K ligand extraction
│   └── reassembly.py                    ← combinatorial reassembly with chemical heuristics
└── drug_likeness/
    └── modified_lipinski.py             ← MW <500, logP ≤5, HBD ≤5, HBA ≤10, rotbonds ≤10, MR 40-130, atoms 20-70
```

## Reproduction note

The platinum strategy in `strategies/platinum.py` mirrors the published 5-step sanitization 1:1. Au and Cu strategies will be authored by the platform engineer in Phase 1; chemistry rules reviewed by the host-lab chemistry team.
