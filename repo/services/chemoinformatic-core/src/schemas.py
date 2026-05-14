"""Pydantic schemas exposed by the chemoinformatic-core service."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


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


class GraphNode(BaseModel):
    idx: int
    element: str
    formal_charge: int
    is_metal: bool


class GraphEdge(BaseModel):
    src: int
    dst: int
    bond_type: Literal["single", "double", "triple", "aromatic", "dative"]


class MolecularGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class NatQGFeatures(BaseModel):
    """Natural Quantum Graph features inferred from the sanitized molecule."""
    coordination_number: int
    geometry: Geometry
    metal_centre_charge: int
    ligand_orbital_signatures: list[str] = Field(default_factory=list)


class SanitizedComplex(BaseModel):
    inchi_key: str
    sanitized_smiles: str
    metal_centre: str
    oxidation_state: int
    coordination_geometry: Geometry
    molecular_graph: MolecularGraph
    natqg_geometry: NatQGFeatures | None = None
    sanitization_warnings: list[str] = Field(default_factory=list)
