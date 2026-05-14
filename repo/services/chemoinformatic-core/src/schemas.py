"""
Cross-service contracts exposed by the chemoinformatic-core service.

This module is the **cross-service contract surface** — every other service
in the system (ingestion, model-training, inference-api, agentic-orchestrator,
reporting) consumes these Pydantic models as the wire format for sanitized
metal-complex data. Treat the schemas in this file as a versioned public API:

  - Every model declares `SCHEMA_VERSION` (single integer; semver-style
    breaking-vs-additive distinction lives at the field level).
  - Additive changes (new optional fields) do not bump the schema version.
  - Renames, type changes, or required-field additions DO bump the version
    and require a coordinated migration across consuming services.

RDKit `Chem.Mol` types are NEVER exposed across service boundaries — those
are implementation details of this service. Other services receive only the
serializable models defined here.

A future refactor extracts this file into a separate `chemoinformatic-contracts`
PyPI package (Phase 2 ADR). Until then, treat it as the de-facto contracts
package and version it accordingly.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

#: Schema version of the cross-service contracts in this module.
#: Bump on any breaking change to the wire format.
SCHEMA_VERSION: int = 1


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
    """Canonical sanitized representation of a metal complex.

    This is the load-bearing cross-service contract. Versioned by
    :data:`SCHEMA_VERSION` at the module level.
    """
    schema_version: int = Field(
        default=SCHEMA_VERSION,
        description="Schema version this payload conforms to. Consumers MUST check.",
    )
    inchi_key: str
    sanitized_smiles: str
    metal_centre: str
    oxidation_state: int
    coordination_geometry: Geometry
    molecular_graph: MolecularGraph
    natqg_geometry: NatQGFeatures | None = None
    sanitization_warnings: list[str] = Field(default_factory=list)
