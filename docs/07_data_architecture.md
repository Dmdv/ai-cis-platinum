# 07 — Data Architecture

**Contents**

- [Goal](#goal)
- [Data domains](#data-domains)
- [Logical schema (selected entities)](#logical-schema-selected-entities)
- [Data tiers (medallion architecture)](#data-tiers-medallion-architecture)
- [Schema evolution and migrations](#schema-evolution-and-migrations)
- [Identifier strategy](#identifier-strategy)
- [Data quality monitoring](#data-quality-monitoring)
- [Provenance and reproducibility](#provenance-and-reproducibility)
- [Open-data publication](#open-data-publication)
- [Data architecture diagram](#data-architecture-diagram)


## Goal

A coherent, FAIR, versioned data foundation that supports the four pillars above. The architecture distinguishes three layers: raw experimental data, sanitized canonical entities, and analytical / training feature stores.

## Data domains

| Domain | Sources | Identifiers |
|---|---|---|
| Metal complexes | Lab synthesis records, ChEMBL, PubChem, CSD, MetAP DB, internal SMILES | MB Finder ID (e.g. `MB-Pt-003232`), InChIKey, CAS |
| Cell lines | Cellosaurus, internal experimental records | Cellosaurus accession (e.g. `CVCL_0134` for A2780) |
| Proteins | UniProt, AlphaFold structure database | UniProt ID (e.g. `P02462` for COL3A1) |
| Pathways & ontologies | KEGG, Reactome, MeSH, ChEBI | KEGG ID, Reactome ID, MeSH term |
| Assays | MTT, SRB, resazurin, direct count, CETSA, kinase assays | Internal assay ID + protocol version |
| Experimental measurements | IC50, EC50, GI50, % inhibition, ΔTm (CETSA) | Bound to (compound, cell line, assay, time, replicate) |
| Multi-omics | RNA-seq (GEO), proteomics (PRIDE), other | Accession + sample metadata |
| Literature | DOIs, PubMed IDs | DOI |
| Lab experiments / ELN | Internal ELN entries (Benchling / LabArchives) | ELN entry ID |

## Logical schema (selected entities)

```
ENTITY: Compound
  - mb_id (PK)                  e.g. MB-Pt-003232
  - inchi_key
  - smiles_raw
  - smiles_sanitized
  - molecular_graph_json
  - natqg_geometry_json         (Pillar 1 geometry)
  - metal_centre                "Pt" | "Au" | "Cu" | "Re" | "Ru" | "Pd" | ...
  - oxidation_state             integer
  - coordination_geometry       enum: square_planar | octahedral | tetrahedral | linear | half_sandwich
  - synthesised_in_lab          bool
  - synthesis_route_eln_id      FK to ELN
  - first_seen_publication      DOI
  - license                     "CC-BY-4.0" by default for lab data

ENTITY: CellLine
  - cellosaurus_id (PK)         e.g. CVCL_0134
  - common_name                 "A2780"
  - tissue                      "ovary"
  - phenotype                   array["cisplatin-resistant"]
  - parent_line_id              FK self
  - source_lab
  - cell_count
  - growth_medium

ENTITY: ProteinTarget
  - uniprot_id (PK)             e.g. P02462
  - gene_symbol                 "COL3A1"
  - sequence_hash
  - alphafold_struct_id
  - kg_node_id                  link into ElementKG+

ENTITY: ActivityMeasurement
  - id (PK)
  - compound_id                 FK Compound
  - cell_line_id                FK CellLine
  - assay_id                    FK Assay
  - incubation_time_hours
  - ic50_uM, ec50_uM, gi50_uM
  - confidence_interval
  - n_replicates
  - source_doi
  - extracted_by                "manual" | "auto-extracted" | "ELN-direct"
  - extraction_confidence_score
  - reviewer_id
  - reviewed_at

ENTITY: PredictionRun
  - id (PK)
  - compound_id                 FK Compound
  - model_version               FK ModelRegistryEntry (e.g. mkano-plus@2.1.0)
  - cell_line_id                FK CellLine
  - protein_target_id           FK ProteinTarget  (optional)
  - predicted_class             "active" | "inactive"
  - predicted_probability
  - predicted_ic50_uM           (regression)
  - feature_vector_hash         for reproducibility
  - created_at

ENTITY: Experiment / Campaign        (Pillar 3 orchestrator state)
  - campaign_id (PK)
  - objective
  - state                       "planning" | "synthesising" | "assaying" | "analysing" | "complete"
  - supervisor_log              JSONB
  - candidates                  array of compound_ids
  - decisions                   JSONB array
  - approved_by                 user_id
  - created_at, updated_at
```

## Data tiers (medallion architecture)

### Bronze tier (raw)
- Immutable copies of every literature scrape, ELN export, database dump, ingested file.
- Stored as Parquet or original file format in the object store, prefixed by source + ISO date.
- Retained indefinitely. Cheap.

### Silver tier (sanitized)
- Schema-conformed, deduplicated, identifier-normalised.
- Pydantic models validate every row before promotion.
- Great Expectations rules enforce data quality (e.g. IC50 values must be positive; molecular formulas must balance).
- This is the canonical layer used by all downstream services for read.

### Gold tier (analytical / training features)
- Versioned feature stores (Feast or equivalent) for ML training.
- Pre-computed embeddings (NatQG, ChemFM, ElementKG functional prompts) cached for fast retraining.
- Train / validation / test splits frozen, hashed, registered in MLflow.

## Schema evolution and migrations

- Database migrations via Alembic; every schema change carries a migration script.
- Backward-incompatible changes require a deprecation window (one minor release).
- New columns default to nullable; legacy rows backfilled lazily.

**Lazy backfill policy (explicit).** Every silver-tier row carries an integer `schema_version` field. When a column is added or a transformation changes, the bronze-to-silver materialisation logic emits new rows at the new `schema_version`; **legacy rows are NOT updated on read**. Backfill is performed by an explicit **Prefect job** (`schema_migration_v{N}_to_v{N+1}`) that:

1. Streams rows at `schema_version = N` in batches.
2. Applies the migration transformation.
3. Writes the result at `schema_version = N+1` (preserving the original row via a soft-delete `is_current` flag for auditability).
4. Records progress in MLflow (run name = `schema_migration_v{N}_v{N+1}_yyyymmdd`).
5. Stops on first error; never partial-completes silently.

The Prefect job is run by the platform engineer (or co-PI per R20) on-demand when a schema bump is published. Reading code MUST handle both `schema_version` values during the migration window; deprecation of the old version follows the api-governance policy (≥ 2 minor SDK releases or 6 months whichever longer).

## Identifier strategy

Every entity carries an external identifier (Cellosaurus, UniProt, ChEMBL, etc.) **and** an internal MB Finder identifier. The internal identifier is durable across upstream renamings and database reorgs.

External identifier sync is handled by a nightly reconciliation job:
- New external IDs → assign internal MB Finder ID, store mapping.
- Renamed external IDs → update mapping; emit warning to lab Slack channel.
- Removed external IDs → mark as deprecated; never delete.

## Data quality monitoring

| Signal | Detection method |
|---|---|
| Incoming SMILES distribution shift | Kolmogorov–Smirnov test on element-occurrence distribution vs training distribution |
| Duplicate compound entries | InChIKey collision detection |
| Conflicting IC50 measurements | Variance > 1 log unit across publications for same (compound, cell line) |
| Cell-line nomenclature drift | Periodic sync against Cellosaurus |
| Assay protocol consistency | Categorical check against protocol library |
| OCR / manual extraction errors | Sampling review by chemists |

Failures route to a curation queue, not to the production data tier.

## Provenance and reproducibility

Every gold-tier row carries:
- Hash of its silver-tier source rows.
- Hash of the transformation code.
- Timestamp.
- (Optional) reviewer ID.

This makes every machine-learning feature regeneratable from raw bronze data plus a Git commit.

## Open-data publication

MB Finder v2 inherits and extends the open-access posture of the source paper:

- The full curated compound + activity dataset is published with each major release under CC-BY-4.0.
- All trained model weights are released under permissive terms (license matched to upstream training-data terms).
- Public BigQuery / Hugging Face mirrors of the dataset planned for visibility.
- DOI-stable releases via Zenodo for citation.

## Data architecture diagram

```
+-------------------------------+
|  External sources             |
|  ChEMBL, PubChem, CSD, MetAP, |
|  literature, ELN, MS, RNA-seq |
+---------------+---------------+
                |
                v
+---------------+---------------+
|       Ingestion service       |
|  (Prefect DAGs + scrapers)     |
+---------------+---------------+
                |
                v
+---------------+---------------+
|     BRONZE tier (raw)         |
|     Immutable object store    |
+---------------+---------------+
                |
                v
+---------------+---------------+
|   Sanitization + validation   |
|  (Pillar 2 chemoinformatic    |
|   core + Pydantic + GE)       |
+---------------+---------------+
                |
                v
+---------------+---------------+
|     SILVER tier (canonical)   |
|     PostgreSQL + RDKit        |
+---------------+---------------+
                |
                v
+---------------+---------------+
|   Feature engineering         |
|   (geometry, embeddings, KG)  |
+---------------+---------------+
                |
                v
+---------------+---------------+
|     GOLD tier (analytical)    |
|     Feast / Iceberg + MLflow  |
+---------------+---------------+
                |
                +----> training jobs --> Model registry
                |
                +----> serving / inference API
                |
                +----> web UI / agentic orchestrator
                |
                +----> public open-data release
```
