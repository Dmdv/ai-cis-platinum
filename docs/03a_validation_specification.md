# 03a — Validation specification (authorship-stratified split)

**Contents**

- [Why this document exists](#why-this-document-exists)
- [Lab attribution data source](#lab-attribution-data-source)
- [Split-generation procedure](#split-generation-procedure)
- [Split artefact (frozen and DVC-tracked)](#split-artefact-frozen-and-dvc-tracked)
- [Hard-negative mining protocol](#hard-negative-mining-protocol)
- [Synthetic-decoy protocol](#synthetic-decoy-protocol)
- [Reproducibility check](#reproducibility-check)


## Why this document exists

`docs/03_pillar1_ai_modernization.md` Component 1.1 commits the platform to an **authorship-stratified split** as the fourth validation methodology (alongside random, scaffold, and cluster splits). The Component 1.1 narrative describes the principle in one paragraph — a reviewer correctly flagged that this is not a *specification*, only an *aspiration*. This document is the missing operational specification.

A validation strategy that cannot be re-implemented by a third party is not a strategy. The sections below define the lab-attribution data source, the split-generation procedure, the frozen-split artefact format, the singleton-handling rule, and the reproducibility check.

## Lab attribution data source

Each compound in the host lab's 17,732-IC50 corpus is attributed to a **publishing lab** via the following resolution chain:

1. **Primary** — DOI of the source publication → corresponding-author affiliation parsed from CrossRef / PubMed.
2. **Secondary** — author-list affiliations parsed from CrossRef when corresponding author is ambiguous.
3. **Disambiguation** — affiliations are resolved to a stable lab identifier via [Research Organization Registry](https://ror.org) (ROR ID) plus principal-investigator name (Levenshtein-bounded).
4. **Singleton handling** — compounds whose source paper has fewer than 5 unique structures attributed to the same lab are grouped into a meta-group `__SINGLETON__`. The singleton group is never split; either entirely in train or entirely in test per the fold.

Manual-curation overrides (when the automatic resolution is wrong) are recorded in `data/lab_attribution_overrides.tsv` and DVC-tracked.

## Split-generation procedure

```python
# Pseudo-code; production implementation at scripts/generate_author_split.py
import random
from collections import defaultdict
import hashlib

def generate_author_stratified_split(
    compounds: list[Compound],
    seed: int = 20260514,
    test_frac: float = 0.2,
    min_lab_size: int = 5,
) -> dict[str, set[CompoundId]]:
    """Generate train / test split where each lab is wholly in one set."""
    rng = random.Random(seed)

    # Group compounds by lab attribution
    by_lab: dict[LabId, list[CompoundId]] = defaultdict(list)
    for c in compounds:
        lab_id = c.lab_id if c.lab_size >= min_lab_size else "__SINGLETON__"
        by_lab[lab_id].append(c.compound_id)

    # Shuffle labs deterministically
    lab_ids = sorted(by_lab.keys())                  # sort first for determinism
    rng.shuffle(lab_ids)

    # Greedy assignment: largest labs first, fill test toward target frac
    total = sum(len(by_lab[l]) for l in lab_ids)
    test_target = int(total * test_frac)
    test_compounds: set[CompoundId] = set()
    train_compounds: set[CompoundId] = set()
    for lab in sorted(lab_ids, key=lambda l: len(by_lab[l]), reverse=True):
        if len(test_compounds) + len(by_lab[lab]) <= test_target:
            test_compounds.update(by_lab[lab])
        else:
            train_compounds.update(by_lab[lab])
    return {"train": train_compounds, "test": test_compounds}
```

**Determinism:** the seed (`20260514` — the proposal commit date) is fixed; any change to the seed bumps a frozen-split version (see below).

## Split artefact (frozen and DVC-tracked)

Every published model evaluation references a **frozen split artefact**:

```
splits/author_stratified_v1.tsv          # compound_id<TAB>fold[train|test]
splits/author_stratified_v1.meta.json    # seed, schema version, lab count,
                                         # singleton count, generation timestamp
```

The artefact is:

- Tracked via DVC; its content hash is recorded in every MLflow run that uses it.
- **Immutable once published.** Changes (corrected lab attributions, additional compounds, new singleton-handling rule) bump a version (`v2`, `v3`, …) and produce a new artefact; the prior version stays available for reproducibility.
- Cross-validated against a deterministic-hash check: `sha256(sorted-lines-of-tsv)` is published in the meta.json and verified by CI.

## Hard-negative mining protocol

Hard negatives are inactive compounds within a Tanimoto similarity of ≥ 0.6 to an active compound, with a measured Δlog(IC50) of ≥ 1 (i.e. a clear "activity cliff"). The protocol:

1. For every (active, cell-line) pair, find all compounds within Tanimoto ≥ 0.6 on the Morgan-2-fingerprint similarity.
2. Filter to inactives (IC50 > 5 µM per the source-paper threshold).
3. Require Δlog(IC50) ≥ 1 to qualify as a hard negative.
4. Cap the per-active hard-negative count at 5 to avoid corpus skew.
5. Hard negatives stay in the train fold per the lab-stratified rule (i.e. a hard negative from lab X follows lab X's fold).

## Synthetic-decoy protocol

Boltz-2-style synthetic decoys (positives from other public datasets used as decoys in our task) are sourced from:

- BindingDB (filtered to organometallic and metal-containing complexes)
- PubChem BioAssay (filtered analogously)

Decoys are:

- Sanitized through the chemoinformatic-core (same pipeline as native compounds).
- Tagged `synthetic_decoy: true` in the corpus metadata.
- Never used in the test fold of the author-stratified split — only in train, to add hard negatives without leakage.

## Reproducibility check

The split is reproducible from this specification: a third party with access to the 17,732-IC50 corpus + the lab-attribution data source + this seed should generate a byte-identical TSV. CI runs the check on every commit that touches the split-generation script.

If the byte-identical check fails, the script change is treated as a versioned split bump (`v1` → `v2`), not a fix.
