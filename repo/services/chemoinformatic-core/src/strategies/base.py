"""
Strategy protocol for transition-metal sanitization.

Each metal centre receives a concrete strategy implementing the five-step
metal-extended sanitization documented in Rusanov, Babak, Balcells et al.
(ChemRxiv 2026, DOI 10.26434/chemrxiv-2025-pp32k/v2). The protocol below
captures the procedure shape; concrete strategies live in the same package.

Steps (paraphrased from the paper):
    1. strip_charges          — remove SMILES charges before fingerprinting
    2. reassign_dative_bonds  — single bonds involving the metal → RDKit dative
    3. override_valences      — relax valency constraints for coordinating heteroatoms
    4. correct_heteroatom_charges  — recompute B, N, P charges where needed
    5. balance_metal_charge   — adjust metal-centre charge to sum to total

The protocol is deliberately simple so a chemist can implement a new metal
strategy by writing one file. Reviewers see chemistry, not boilerplate.
"""

from __future__ import annotations

from typing import Protocol, Literal, runtime_checkable

from rdkit import Chem

Geometry = Literal[
    "square_planar",
    "octahedral",
    "tetrahedral",
    "linear",
    "trigonal_planar",
    "trigonal_bipyramidal",
    "half_sandwich",
    "unknown",
]


@runtime_checkable
class MetalSanitizer(Protocol):
    """A sanitization strategy for one transition metal element."""

    metal_symbol: str                 # e.g. "Pt"
    typical_oxidation_states: list[int]
    typical_coordination_numbers: list[int]
    typical_geometries: list[Geometry]
    active_threshold_uM: float        # IC50 cutoff defining "active" for this metal

    def strip_charges(self, mol: Chem.Mol) -> Chem.Mol:
        """Step 1 — remove charges before RDKit fingerprint generation."""
        ...

    def reassign_dative_bonds(self, mol: Chem.Mol) -> Chem.Mol:
        """Step 2 — recast single bonds at the metal centre as dative bonds."""
        ...

    def override_valences(self, mol: Chem.Mol) -> Chem.Mol:
        """Step 3 — permit non-standard valences for coordinating heteroatoms."""
        ...

    def correct_heteroatom_charges(self, mol: Chem.Mol) -> Chem.Mol:
        """Step 4 — recompute B/N/P charges away from alkali/alkaline earths."""
        ...

    def balance_metal_charge(self, mol: Chem.Mol) -> Chem.Mol:
        """Step 5 — adjust the metal-centre formal charge to balance the complex."""
        ...

    def sanitize(self, smiles: str) -> "SanitizedComplex":
        """Run all five steps end-to-end, return a sanitized graph + metadata."""
        ...


# Imports placed at the bottom to avoid cycles in the skeleton.
from schemas import SanitizedComplex  # noqa: E402
