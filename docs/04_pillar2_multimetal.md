# 04 — Pillar 2: Multi-Metal Generalisation and Adjacent-Science Integration

**Contents**

- [Goal](#goal)
- [Component 2.1 — Generalised metal-extended chemoinformatic core](#component-21-generalised-metal-extended-chemoinformatic-core)
- [Component 2.2 — Multi-metal MKANO+](#component-22-multi-metal-mkano)
- [Component 2.3 — Multi-omics MoA inference module](#component-23-multi-omics-moa-inference-module)
- [Component 2.4 — Cross-project knowledge graph](#component-24-cross-project-knowledge-graph)
- [Adjacent-science applications](#adjacent-science-applications)
- [Technology choices](#technology-choices)
- [Risks and unknowns](#risks-and-unknowns)
- [Phase deliverables](#phase-deliverables)


## Goal

Two intertwined objectives:

1. **Generalise the chemoinformatic and ML pipeline** from platinum-only scope to the broader transition-metal therapeutic space: **Pt, Au, Cu, Re, Ru, Pd**, and the easily extensible **Ir, Ni, Co, Rh, Fe, Ti**.
2. **Connect the system to adjacent research lines** — microbiome cancer therapies, immunogenic cell death (ICD), and tubulin targeting — so that data assets accumulated under separate projects compound rather than fragment.

## Component 2.1 — Generalised metal-extended chemoinformatic core

### Problem
The 5-step RDKit sanitization documented in the source paper is platinum-tuned. Step 5 explicitly *"Adjust the localized numerical charge value on the platinum node"* — the rule does not transparently extend to Au(I)/Au(III), Cu(I)/Cu(II), Re(I)/Re(VII), Ru(II)/Ru(III), Pd(II), or Ir(III). Independently, Rasmussen et al. (*J. Cheminform.*, 2025) document parallel SMILES-conversion failures for transition metals more broadly. Au and Cu drug discovery are active parallel research lines, so an unwritten rule per metal forces duplicated bespoke pipelines.

### Approach
- **Refactor the sanitization pipeline into a strategy-pattern API** with one strategy per metal centre.
```python
class MetalSanitizer(Protocol):
    metal_symbol: str          # "Pt", "Au", "Cu", ...
    typical_oxidation_states: list[int]
    typical_coordination_numbers: list[int]
    typical_geometries: list[str]  # ["square-planar", "octahedral", ...]

    def strip_charges(self, mol: rdkit.Chem.Mol) -> rdkit.Chem.Mol: ...
    def reassign_dative_bonds(self, mol) -> rdkit.Chem.Mol: ...
    def override_valences(self, mol) -> rdkit.Chem.Mol: ...
    def correct_heteroatom_charges(self, mol) -> rdkit.Chem.Mol: ...
    def balance_metal_charge(self, mol) -> rdkit.Chem.Mol: ...
    def sanitize(self, smiles: str) -> SanitizedComplex: ...
```
- **Implement one concrete strategy per metal**, encoding metal-specific empirical chemistry rules. For example, AuSanitizer handles auriophilic interactions and linear coordination at Au(I); ReSanitizer handles the *fac*-tricarbonyl Re(I) motif common in radiopharmaceuticals.
- **Generalise the metal-charge balancing step** to the entire periodic-table block, parameterised on each strategy's `typical_oxidation_states`.
- **Provide a fallback `GenericTransitionMetalSanitizer`** for metals not yet specialised; logs warnings and tracks failure rates as a data-quality signal.
- **Unify the dative-bond reassignment** so that a single RDKit-patched code path supports all metals; the per-metal strategy provides the metal-symbol predicate.

### Validation strategy
- For each metal, curate a labeled subset of at least 100 complexes from the literature with manually verified structures. Use Rasmussen et al. corpus where overlap exists.
- Measure SMILES parsing success rate per metal. Target ≥90 %, matching the platinum baseline of 94 %.
- Manual chemist review of 50 randomly sampled successful conversions per metal.

## Component 2.2 — Multi-metal MKANO+

### Problem
A single classifier trained only on Pt will not transfer cleanly to Au or Cu drug discovery. At the same time, training separate models per metal squanders cross-metal regularities (e.g. coordination geometry priors, ligand-class effects).

### Approach
- **Multi-task fine-tuning.** The geometry-aware backbone from Pillar 1 is pretrained on the union of tmQM + curated host-lab metal datasets (Pt-curated, Au-curated, etc.). Fine-tuning heads are per metal × cell-line.
- **Metal-token conditioning.** The metal centre identity is provided as a learnable embedding concatenated with the NatQG embedding before the heads. This allows a single backbone with metal-aware heads.
- **Per-metal active/inactive thresholds.** The 5 µM cutoff used for Pt is not universal; gold compounds are typically more potent (sub-µM), copper compounds less. Each metal carries its own threshold metadata.

### Validation strategy
- Hold-out tests per metal × cell-line × split-protocol matrix.
- Cross-metal transfer experiment: train on Pt + Au, evaluate on Cu (zero-shot).
- Comparison to single-metal baselines.

## Component 2.3 — Multi-omics MoA inference module

### Problem
The PlatinAI mechanism study (Rusanov et al., 2026) was a manual, multi-week analysis involving RNA-seq, proteomics, KEGG pathway enrichment, CETSA, Western blot, and kinase activity assays. Similar workflows apply to ICD studies, tubulin work, and microbiome interventions. The integration step (DEG ↔ DEP correlation, target prioritisation) is reproducible enough to automate.

### Approach
- **MoA inference service** ingesting:
  - Transcriptomic count matrices (RNA-seq).
  - Proteomic quantitation tables (label-free or TMT).
  - Optional CETSA / DARTS / TPP thermal shift data.
  - Optional pathway enrichment (KEGG, Reactome).
- **Pipeline:**
  1. Differential expression (DESeq2 / limma) → DEGs.
  2. Proteomic differential abundance (MSstats) → DEPs.
  3. Cross-omics correlation by gene symbol / UniProt → DEG–DEP pairs.
  4. Knowledge-graph traversal (StringDB + PathwayCommons) to suggest signalling axes.
  5. Target ranking by combined evidence score (correlation strength + KG centrality + literature support).
- **Output:** a target dossier per compound, machine-readable JSON + human-readable PDF.

### Validation strategy
- Replay PlatinAI study end-to-end: feed the published RNA-seq (GEO GSE320503) + proteomics (PXD074892) into the pipeline; check whether it surfaces COL3A1, BUB1B, PLK1, AURKB as top candidates in the same priority order as the manual analysis.
- Apply to one ICD compound and one tubulin compound from host-lab archived data — assess whether known MoAs are recovered.

## Component 2.4 — Cross-project knowledge graph

### Problem
The broader metallodrug publication record spans cisplatin resistance, microbiome cancer therapies, ICD in mesothelioma, tubulin-targeting compounds, and tin-based anticancer agents. Each project produces overlapping but currently disconnected data: cell lines tested across projects, proteins implicated across MoA studies, ligand chemistries shared across metal scaffolds.

### Approach
- **Unified knowledge graph (ElementKG+)** extending the source paper's ElementKG with:
  - Compounds (linked to PubChem, ChEMBL, MetAP DB).
  - Cell lines (Cellosaurus).
  - Proteins and pathways (UniProt, Reactome, KEGG).
  - Phenotypes (Disease Ontology, MeSH).
  - Host-lab internal experiments (linked back to ELN entries).
- **Storage:** PostgreSQL with `pg_graph` or Neo4j (decision in `repo/adrs/ADR-005-knowledge-graph-store.md`).
- **Update cadence:** nightly ingestion from external sources; real-time updates from host-lab experiments via the orchestrator (Pillar 3).
- **Query surface:** Cypher / SPARQL / a GraphQL wrapper for the web UI.

### Surface examples
- *"Show all compounds in the portfolio (Pt + Au + Cu + tin + tubulin + microbiome) that target the COL3A1 pathway."*
- *"Which cell lines are shared between the ICD project and the cisplatin-resistance project, and what is the activity correlation?"*
- *"For a candidate Au(III) complex, what published Au(I)/Au(III) precedents have similar ligand chemistry and what were their MoAs?"*

These queries are currently expressible only as a senior chemist's accumulated memory; the system makes them programmable.

## Adjacent-science applications

| Research thread | What MB Finder v2 contributes |
|---|---|
| Microbiome cancer therapies | Compound–microbe interaction prediction via the unified KG; multi-omics MoA inference on host transcriptomes. |
| Immunogenic cell death (mesothelioma) | MoA inference; KEGG pathway scoring against ICD signatures. |
| Tubulin-targeting compounds | Target-aware design (Pillar 1) explicitly conditioning on tubulin isoforms; MoA inference on cytoskeletal pathways. |
| Tin and other main-group metals | Multi-metal sanitization extends naturally to Sn(IV), Sb(III), Bi(III) — same strategy-pattern API. |
| Cancer care equity (Lancet manifesto) | Open-access platform: MB Finder v2 retains the open-access, low-resource-friendly deployment posture of the published MB Finder system. |

## Technology choices

| Layer | Choice | Reason |
|---|---|---|
| Sanitization base | RDKit (current dependency) | No reason to rewrite; maintain compatibility with MKANO codebase. |
| Strategy pattern | Plain Python protocols | Keeps each metal's logic readable to chemists. |
| Multi-omics framework | scverse stack (anndata, scanpy, muon) + DESeq2 / limma / MSstats | Industry standard for biomedical multi-omics. |
| Knowledge graph | Neo4j (initial) with option to migrate to PG + pg_graph | Faster developer iteration; can move to Postgres if licensing matters. |
| External data sync | Airflow / Prefect | Standard DAG-based ETL scheduling. |

## Risks and unknowns

- **Per-metal chemistry rules require domain expertise.** Au and Cu sanitization rules are not standardised in the literature. Mitigation: each rule set ships with a chemist-readable specification document; rules are validated empirically per metal subset.
- **Cross-omics integration is data-hungry.** Host-lab archival data may be limited or inconsistently labelled. Mitigation: the MoA inference service degrades gracefully — if proteomics is absent, returns transcriptomic-only inference; if both absent, returns KG-only priors.
- **KG accuracy.** External KGs (StringDB, Reactome) contain noise. Mitigation: KG queries return evidence scores and source citations; the chemist remains the final arbiter.

## Phase deliverables

| Phase | Deliverable |
|---|---|
| Phase 1 (months 0–6) | Strategy-pattern sanitization refactor; Au and Cu strategies; tin extension if time permits. |
| Phase 2 (months 6–12) | Multi-metal MKANO+ training; MoA inference service replayed against PlatinAI; KG bootstrap. |
| Phase 3 (months 12–18) | Cross-project KG live; surfacing cross-project insights through web UI. |
