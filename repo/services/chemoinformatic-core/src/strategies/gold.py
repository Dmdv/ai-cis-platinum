"""
Gold (Au) sanitization strategy.

Generalises the platinum five-step procedure to Au(I) and Au(III)
metallodrugs that are active in the broader research community.

Au-specific chemistry encoded here:
    - Au(I): preferred linear two-coordinate geometry; auriophilic
      d10-d10 interactions occasionally present (handled as a graph
      feature, not a covalent edge).
    - Au(III): square-planar four-coordinate; isoelectronic with Pt(II)
      which simplifies many ligand-set rules.
    - NHC (N-heterocyclic carbene) ligands common across both
      oxidation states.

This file is currently a stub; the platform engineer authors the rules
in Phase 1 with chemistry review by the host-lab chemistry team.
"""

from __future__ import annotations

from typing import final

from rdkit import Chem

from ..schemas import SanitizedComplex
from .base import Geometry
from . import register_sanitizer


@final
@register_sanitizer("Au")
class GoldSanitizer:
    metal_symbol: str = "Au"
    typical_oxidation_states: tuple[int, ...] = (1, 3)
    typical_coordination_numbers: tuple[int, ...] = (2, 4)
    typical_geometries: tuple[Geometry, ...] = ("linear", "square_planar")
    active_threshold_uM: float = 1.0  # gold drugs typically more potent than platinum

    def strip_charges(self, mol: Chem.Mol) -> Chem.Mol:
        raise NotImplementedError("skeleton — chemistry rules pending review")

    def reassign_dative_bonds(self, mol: Chem.Mol) -> Chem.Mol:
        # Note: aurophilic interactions are *not* covalent bonds; do not
        # reassign such edges.
        raise NotImplementedError("skeleton")

    def override_valences(self, mol: Chem.Mol) -> Chem.Mol:
        raise NotImplementedError("skeleton")

    def correct_heteroatom_charges(self, mol: Chem.Mol) -> Chem.Mol:
        raise NotImplementedError("skeleton")

    def balance_metal_charge(self, mol: Chem.Mol) -> Chem.Mol:
        raise NotImplementedError("skeleton")

    def sanitize(self, smiles: str) -> SanitizedComplex:
        raise NotImplementedError("skeleton")
