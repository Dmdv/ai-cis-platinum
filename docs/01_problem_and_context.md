# 01 — Problem and Context

## The systemic problem

Pharmaceutical R&D has a structural cost problem that AI has begun to compress in the organic small-molecule domain. A new drug now takes 12–15 years and ≈US $2.6 B per approved entity to develop; fewer than 10 % of compounds entering Phase I clinical trials reach regulatory approval; high-throughput screening alone produces hit rates as low as 2.5 % (Ferreira & Carneiro, *ACS Omega* 10, 23889, 2025; Zhang et al., *Nat. Med.* 31, 45, 2025).

In the platinum-based oncology subfield, the problem is more acute. Cisplatin, oxaliplatin, and carboplatin remain first-line agents across ovarian, lung, head-and-neck, and bladder cancers, but cisplatin resistance is now the dominant clinical failure mode. Resistance arises through multifactorial mechanisms — reduced uptake, elevated glutathione, enhanced DNA repair, altered apoptosis signalling, off-target pro-survival pathways — and no new platinum drug designed to circumvent these has reached approval.

## The AI-for-metallodrugs gap

While AI-driven drug discovery has matured for organic molecules (Mol-BERT, ChemBERTa, DiffDock, generative chemistry foundation models, ChemFM, OMol25), its application to metal-based therapeutics has lagged for three interrelated reasons:

1. **Chemoinformatic representation failure.** SMILES strings, canonical molecular graphs, and the RDKit sanitization routines that underpin nearly every chemistry ML library were engineered for covalent organic chemistry. Transition-metal complexes feature dative bonds, hypervalent coordination spheres, dynamic oxidation states, and stereochemistries (square-planar, octahedral, half-sandwich) that violate the implicit valence rules. Default RDKit sanitization fails on >70 % of CSD-derived metal complex strings and >40 % of unfiltered metal complexes overall.
2. **Data scarcity.** Platinum complexes comprise less than 0.3 % of compounds in ChEMBL, NCI-DTP, DrugBank, DrugCentral, e-Drug3D, or NCGC. Of all metal-focused databases, MetAP DB — the only specialised one — contained four Pt-based compounds at the time of the source paper.
3. **Architectural mismatch.** Standard GNNs (GCN, GAT, PNA) suffer from over-squashing when forced to propagate information through long-range coordination spheres; they capture neither the empirical chemical priors (electronegativity, hypervalency rules) nor the geometric primitives essential to metal centres.

## Contribution of the source paper

The March 2026 paper (Rusanov, Babak, Balcells, et al., ChemRxiv DOI 10.26434/chemrxiv-2025-pp32k/v2) directly attacks the first two of these problems and partially addresses the third.

### What the paper delivered

- **A manually curated dataset:** 3,725 unique Pt complexes drawn from 1,134 publications, with 17,732 experimentally determined IC50 values across 591 cell lines and 30 incubation periods. Most comprehensive Pt anticancer dataset to date.
- **A metal-extended RDKit sanitization pipeline:** a five-step modification (charge stripping, dative bond reassignment, dynamic valency override, heteroatom charge correction, metal-centre charge balancing) that lifts the SMILES parsing rate to 94 %.
- **MKANO:** a metal-pretrained variant of the KANO (knowledge-graph-enhanced molecular contrastive learning with functional prompt) architecture. Pretrained on 214,373 unlabeled Pt-complex graphs, fine-tuned on the four-cell-line labeled subset (A2780, MCF-7, A549, A2780cis at 72 h).
- **High-throughput virtual screening:** the trained MKANO was run on all 214,373 Pt complexes; 19 structurally diverse predictions were synthesised, giving up to 72 % agreement between predicted and experimental cytotoxicity.
- **De novo design:** a fragment-assembly algorithm generated 427 novel platinum scaffolds from active ligand fragments, ranked by MKANO probability.
- **PlatinAI:** the top scaffold — a bis-N-heterocyclic carbene Pt(II) complex — was synthesised, characterised, and assayed. It exhibited 1.5 ± 0.4 µM IC50 in cisplatin-resistant A2780cis (16-fold more potent than cisplatin in the same line), comparable in vivo efficacy in a murine xenograft model, no kidney or liver toxicity, and — most importantly — a non-DNA mechanism of action targeting protein signalling networks (COL3A1, BUB1B, PLK1, AURKB).
- **MB Finder:** the deployed public web platform documented in Rusanov et al., 2026 — integrates the database, similarity search, and the single-molecule prediction module.

This is, to the best of public knowledge, the first end-to-end AI-driven metallodrug pipeline to deliver an experimentally validated novel candidate against a clinically relevant resistance mechanism.

## Stated roadmap (from the source paper)

The conclusion of the source paper explicitly identifies two limitations and pledges to address them:

> *"Currently, a key limitation of our model is its inability to predict the geometry of complexes, e.g., cis/trans isomers. This structural parameter is widely acknowledged to be one of the most, if not the most, critical factors determining the anticancer activity of platinum complexes. In future studies, we aim to address this constraint, as well as to develop generative ML models capable of creating novel metallodrugs beyond the de novo fragment-based approach proposed herein."*

Independently of the paper, the broader metallodrug research community has the following observable characteristics:

- Au-, Cu-, Re-based therapeutics are active research lines.
- Multi-omics mechanism studies (transcriptomics + proteomics + biochemistry + CETSA) are routine for hit characterisation.
- Academic groups working on AI-driven metallodrug discovery typically lack a full-time platform engineer; production work behind such platforms is often carried by chemists and bioinformaticians.
- Microbiome-based cancer therapies, immunogenic cell death, and tubulin-targeting are parallel research lines that share underlying technical infrastructure with platinum-based work.

## The opportunity the proposed system addresses

Five concrete gaps emerge from the above context:

| # | Gap | What is missing |
|---|---|---|
| 1 | Geometry blindness | The current model treats cis and trans isomers as equivalent SMILES strings. |
| 2 | Target blindness | No explicit conditioning on protein targets (COL3A1, BUB1B, etc.) the lab has now confirmed PlatinAI engages. |
| 3 | Metal-specific over-fitting | The 5-step sanitization is platinum-tuned; Au/Cu/Re each require analogous but slightly different rules currently unwritten. |
| 4 | Manual DMTA orchestration | Synthesis, in vitro, in vivo, and MoA steps are scheduled and analysed by hand. |
| 5 | Research-grade engineering | No CI/CD, no model registry, no observability, no reproducibility infrastructure. The current GitHub repo is research code, not production code. |

The proposed MB Finder v2 system, structured into four pillars, addresses each gap explicitly. The remainder of this document set develops the architecture, components, contracts, and roadmap.
