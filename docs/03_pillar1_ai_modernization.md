# 03 — Pillar 1: AI Modernization

**Contents**

- [Goal](#goal)
- [Component 1.1 — Geometry-aware molecular representation](#component-11-geometry-aware-molecular-representation)
- [Component 1.2 — Target-aware design with AlphaFold 3 / Boltz-2](#component-12-target-aware-design-with-alphafold-3-boltz-2)
- [Component 1.3 — Foundation-model backbone](#component-13-foundation-model-backbone)
- [Component 1.4 — Truly generative architecture beyond fragment assembly](#component-14-truly-generative-architecture-beyond-fragment-assembly)
- [Technology choices](#technology-choices)
- [Risks and unknowns](#risks-and-unknowns)
- [Phase deliverables](#phase-deliverables)


## Goal

Bring the AI stack into 2026 capability: predict geometry, condition on protein targets, replace the GNN backbone with a chemistry foundation model, and add truly generative architectures alongside the existing fragment assembly. Every component proposed here is published, validated, and operational in current literature.

## Component 1.1 — Geometry-aware molecular representation

### Problem
MKANO consumes SMILES-derived molecular graphs. Two complexes that differ only in cis/trans configuration produce indistinguishable inputs. The source paper flags this as the foremost limitation: cis/trans geometry is widely acknowledged to be the most critical determinant of anticancer activity in Pt complexes.

### Approach
- **Adopt the Natural Quantum Graph (NatQG) representation** (Kneiding et al., *Digit. Discov.* 2, 618, 2023, with David Balcells as co-author of the supporting tmQM dataset programme). NatQGs are constructed from natural bond orbital analysis and explicitly encode coordination geometry, bond order, and orbital occupancy as graph features.
- **Pretrain a geometry-aware backbone on tmQM and tmQMg***. The tmQM dataset (86 K transition-metal complexes with DFT-optimised geometries) and tmQMg* (74 K with excited-state properties) provide a 160 K+ corpus that the source paper does not currently use.
- **Per-category NNP benchmarking discipline** (Wagen, *Benchmarking NNPs, Orb-v2, and MACE-MP-0*, Rowan Newsletter, Jan 2025): unlike DFT — where a level of theory can be validated on a few benchmarks — NNPs require category-specific benchmarking *for each new chemistry class* because the model has only "learned" what was in its pretraining set. Rowan publishes a benchmarking site (`benchmarks.rowansci.com`) with TorsionNet206, Folmsbee conformers, and Wiggle150 as molecular benchmarks. Important caveat from the same source: **Orb-v2 and MACE-MP-0 are less accurate than AIMNet2 for pure organic chemistry** — both were trained on materials-project data (MPtraj + Alexandria for Orb-v2) and shine at catalyst design, MOFs, molten salts; for the transition-metal pharmaceutical regime, NNP backbone choice must be benchmarked per metal × per ligand class. The proposal therefore commits to a metallodrug-specific NNP benchmark suite (Phase 3 deliverable) covering Pt, Au, Cu, Re, Ru, Pd × monodentate / bidentate / tridentate / NHC ligand families — analogous to Rowan's discipline but specialised to metallodrug discovery.
- **Integrate Toney/Kulik denticity + coordinating-atom prediction** (Toney et al., *PNAS* 122 (41), e2415658122, 2025; Kulik group, MIT). The published D-MPNN models achieve **88.5 % accuracy on denticity classification (ROC-AUC 0.98)** and **98.8 % overall / 84.8 % molecular accuracy on coordinating-atom identification** when trained on 70,069 unique CSD-derived ligands. The models are integrated with the molSimplify pipeline and were validated on 1,175 generated TMCs with DFT. **The Kulik group publishes `pydentate` as a pip-installable Python toolkit** (`pip install pydentate`; source: github.com/hjkgrp/pydentate) with two Jupyter tutorials — `tutorial1_intro.ipynb` (50 KB) and `tutorial2_hemilability.ipynb` (181 KB) — that demonstrate the full coordinating-atom-count and hemilability prediction pipeline on an `example_ligands.csv` set. *Scope note*: `pydentate`'s primary prediction task is total count of coordinating atoms (which the paper terms denticity for non-hemilabile ligands; the package's classification is on count, not on the chemist's strict denticity/hapticity distinction). For MB Finder v2, integrating this pretrained predictor upstream of the 5-step sanitization is a bounded **1–2 week** effort: pip dependency + adapter glue mapping `pydentate`'s output schema to the chemoinformatic-core's `SanitizedComplex` Pydantic model + a hand-validated test set of ≥ 100 Pt complexes from the host lab's archive. Not a from-scratch reimplementation, but not free either. The predictor proposes the coordination topology before any per-metal strategy is applied, making the sanitization pipeline robust to SMILES strings where the metal-coordination is implicit rather than explicit (the dominant failure mode of the current MKANO pipeline).
- **Add an explicit isomer-classification head** to MKANO+: given a NatQG, predict cis/trans (square-planar), facial/meridional (octahedral), and half-sandwich orientation. The Toney 2025 *JACS* follow-up on dynamic metal-ligand coordination modes (147 (52), 48218-48234) demonstrates that even *hemilability* — a harder problem — is now a learnable peer-reviewed task; isomer classification is a strictly easier sub-task and should be trainable to >90 % accuracy on the curated 3,725-complex Pt set.

### Architecture sketch
```
Input SMILES + (optional) 3D coords
     |
     v
Metal-extended RDKit (Pillar 2 chemoinformatic-core)
     |
     v
SMILES → 2D molecular graph
     |
     +--- if 3D coords absent: tmQM-pretrained NatQG estimator (geometry inferred)
     |
     v
SE(3)-equivariant GNN backbone (Equiformer or MACE)
     |
     +--- ElementKG functional-prompt cross-attention
     |
     v
Multi-head outputs:
  • cytotoxicity classifier (per cell line)
  • IC50 regression (per cell line)
  • geometry classifier (cis/trans/etc.)
  • property regressors (logP, MW, MR, HBD, HBA, rot. bonds)
```

### Validation strategy
- Hold-out test sets stratified by metal centre, geometry class, and scaffold cluster.
- Compare to MKANO baseline on the existing 17,732 IC50 dataset; expect at least retention of current performance, with measurable improvement on stereoisomer-rich subsets.
- Test on the 19 experimentally synthesised complexes from the source paper as a fixed benchmark.
- **Authorship-stratified split (mandatory):** Quigley/Leash Bio, *AI for chemistry in 2025 is like AI for images in 2010* (Substack, December 2025), demonstrates that on ChEMBL — the same kind of public chemistry corpus the source paper's 1,134-publication dataset draws from — a simple classifier reaches **top-5 accuracy of 60 % at identifying which of 1,815 prolific chemists made a molecule from structure alone**. More devastating: **authorship probability alone predicts molecule activity almost as well as molecular descriptors do**. The paper title is *Clever Hans in Chemistry: Chemist Style Signals Confound Activity Prediction on Public Benchmarks.* Standard random / scaffold / cluster splits leak chemist-style information across train and test, inflating accuracy. The proposal's evaluation harness therefore adds a **by-source-lab split**: complexes from the same research group are grouped together; the model is trained on one group of labs and tested on a disjoint group. This split is the most pessimistic of the four and the most diagnostic of true chemical generalisation. Combined with **hard-negative mining** (similar molecules across activity cliffs) and **Boltz-2-style synthetic decoys** (positives from other datasets used as decoys), this is the 2026 best-practice evaluation discipline. Caveat to internalise: in CASP16 affinity prediction, **molecular-weight alone tied for first place** — a starkness reminder that benchmark "wins" require careful interrogation before they generalise.

## Component 1.2 — Target-aware design with AlphaFold 3 / Boltz-2

### Problem
The PlatinAI mechanism study identified specific protein targets (COL3A1, BUB1B, possibly PLK1) that are engaged by the compound. The current pipeline does not exploit this knowledge: subsequent candidate prediction is still purely cell-line-based.

### Approach
- **Predict the protein receptor structure using AlphaFold 3** (Abramson et al., *Nature* 630, 2024). AF3 reports up to ≈76 % success on the PoseBusters-curated PDBbind protein–ligand pose benchmark. **Caveat — AF3's metal-ligand coverage is uneven**: the training and PoseBusters sets emphasise organic and biologically common metal cofactors (Zn, Mg, Ca, Fe, Mn). Pt(II), Au(III), Re(I), Ru(II) anticancer scaffolds are *under-represented*, and naive end-to-end docking of the Pt complex into AF3 is not yet reliable. The proposal therefore uses AF3 / Boltz-2 to predict the *receptor* (COL3A1, BUB1B, PLK1 holoforms), then applies a **metal-aware re-docking step** (Component 1.2.1) for the Pt complex itself.
- **Use Boltz-2** (Passaro et al., bioRxiv 2025, MIT/Recursion; open-weights, MIT licence) for two distinct tasks: (i) open-weights alternative receptor structure prediction (self-hosted, no commercial license issues); and (ii) **binding-affinity prediction** — Boltz-2's headline 2025 capability. **Honest performance characterisation from Rowan's deployment notes** (Wagen, *BREAKING: Boltz-2 Now Live On Rowan*, June 7 2025): Boltz-2 *"performs almost as well as the industry-standard FEP+ workflow and handily outperforms cheaper physics-based methods like MM/PBSA, although performance is considerably worse on internal targets from Recursion."* That is, Boltz-2 is FEP-comparable on public benchmarks but degrades on proprietary/novel targets — meaning the host lab should treat Boltz-2 affinity scores as a *ranking* signal (relative ordering) rather than as an absolute ΔG prediction. Each candidate receives a Boltz-2 affinity score against each validated target as a first-class ranking feature. Boltz-2 is operationally deployed in 2026 at Rowan (`rowansci.com`), in Tamarind, and in third-party platforms — the "operational in 2025-2026" claim has external confirmation.
- **Co-folding model alternatives.** **Chai-1** (Discovery, 2025) is a third-party alternative to AF3 / Boltz-2; Rowan now offers Boltz-1, Boltz-2, and Chai-1 side-by-side. The proposal's architecture treats the co-folding model as a swappable backend; the lab benchmarks all three on the 19 PlatinAI-era complexes before locking in a default.
- **Score candidates against the empirically validated targets** (COL3A1, BUB1B) reported in the source paper. The screening prioritises compounds predicted to bind these targets, complementing pure cytotoxicity-based ranking.
- **Feed binding-pocket descriptors + Boltz-2 affinity back into MKANO+** as a conditioning signal. Concretely: each candidate receives a `(target_id, boltz2_affinity, redocking_score, pocket_embedding)` vector concatenated with its NatQG embedding before the cytotoxicity head.
- **Use RoseTTAFold All-Atom** (Krishna et al., *Science* 384, 2024; Baker lab, U. Washington) as the open-source, US-academic-published alternative receptor model when commercial AF3 terms become a publication issue.

### Architecture sketch
```
                          +-------------------------+
                          |  AF3 / Boltz-2 service  |
                          |  (self-hosted GPU pool) |
                          +-----------+-------------+
                                      ^
candidate Pt complex (NatQG) ---------+--- protein target sequence (COL3A1, BUB1B, ...)
                                      |
                                      v
                          binding pose + interaction features
                                      |
                                      v
                          MKANO+ target-conditioned classifier
                                      |
                                      v
                          ranked candidate list with target rationale
```

### Validation strategy
- Retrospective: re-rank the 427 fragment-assembly scaffolds with target-conditioned scoring; assess whether PlatinAI's COL3A1-engaging chemotype ranks higher than under the untargeted baseline.
- Prospective: nominate 5–10 novel candidates conditioned on COL3A1 binding, synthesise top 3, measure CETSA shifts.

### Component 1.2.1 — Metal-aware re-docking (gap closure on AF3 limitations)

AF3 and Boltz-2 are excellent at predicting protein conformations, including residues coordinating biologically common metals (Zn, Mg, Mn). They are *not* yet reliable when the *ligand* is a Pt(II) bis-N-heterocyclic carbene or an Au(III) cyclometallated complex. Re-docking the Pt complex into the predicted receptor pocket therefore requires a metal-aware docker:

- **GOLD with a metal-aware force field** (Hartshorn et al.; commercial — CCDC) or **AutoDock-Metal** (open-source) as immediate options.
- **Equivariant metal-aware docker** (custom) as a Phase-3 deliverable, built on the same SE(3)-equivariant backbone as Pillar 1 Component 1.1. This is a publishable contribution in its own right.
- **Cellular thermal shift validation** (CETSA) on COL3A1 / BUB1B as the experimental ground truth for re-docking accuracy — the CETSA protocol is already operational in the host lab (used in the PlatinAI mechanism study; Rusanov et al., 2026).

This component closes the most credible reviewer objection to the AF3-conditioned design: that the headline 76 % protein–ligand accuracy does not apply to Pt-anticancer ligands without an explicit metal-aware fix.

## Component 1.3 — Foundation-model backbone

### Problem
MKANO is a domain-specific contrastive GNN trained on 214,373 unlabeled metal complexes. While effective for its size, modern chemistry foundation models — Cai et al.'s **ChemFM** family (Communications Chemistry 2025; the headline scaling claim is for a 3-billion-parameter checkpoint pre-trained on 178 M molecules; smaller deployed checkpoints on Hugging Face include 1B variants and are the practical starting point for academic fine-tuning), IBM's multimodal model (588 M samples / 29 B tokens, NeurIPS 2025), and OMol25 from Meta FAIR — demonstrate that scale-up yields large transfer gains.

### Approach
- **Treat foundation models as a swappable backbone**, not a replacement for ElementKG. The functional-prompt + knowledge-graph machinery from KANO remains valuable; it can sit on top of a much larger encoder.
- **Fine-tune the ChemFM checkpoint that fits the lab's GPU budget.** The published 3B checkpoint (Cai et al. 2025) is the headline; the smaller 1B HF deployment is the practical start for Phase-1 academic fine-tuning. The default recipe is **QLoRA with DoRA adapters** (4-bit NF4 quantised base + magnitude/direction decomposed low-rank adapters; Dettmers 2023; Liu et al. 2024) executed through the **Unsloth** runtime, which reports 2–5× wall-clock speedups and ≈80 % VRAM reduction versus naive PEFT (Kaitchup, *Advanced LoRA Fine-Tuning*, Nov 2025). On a 3 B ChemFM at 4-bit, QLoRA+DoRA fits on a single 24 GB GPU and trains a metallodrug fine-tune in 6–10 h; on the 1B checkpoint the run completes in 2–3 h on the same hardware.
- **Benchmark against MKANO under identical splits.** Replace only the encoder; keep the same evaluation harness. If MKANO outperforms on certain splits — likely on cluster-based splits where domain-specific pretraining matters more — retain it as the production model and use the foundation backbone as a secondary opinion.

### Component 1.3.1 — Fine-tuning methodology (PEFT decision matrix, evidence-grounded)

The proposal's choice of adapter method is *not* a minor implementation detail; it determines reproducibility, hardware cost, and the cost of running ablations. The matrix below cites Marie's head-to-head benchmark (Kaitchup *Advanced LoRA Fine-Tuning*, Nov 2025) which compared LoRA, DoRA, PiSSA, EVA, OLoRA (bf16) and QLoRA, QDoRA, LoftQ, QEVA (4-bit) on Qwen3-4B-Base on a fixed translation task.

| Method | When to use | VRAM (3 B base) | Marie benchmark verdict |
|---|---|---|---|
| **LoRA + rsLoRA** (Hu 2021 + Kalajdzievski 2023) | Always-on baseline. `use_rslora=True` is "strictly better with no downsides" (Srivastava, Dec 2025). | ≈14 GB | "LoRA is still the right default… cheap, stable, and good enough for many small-to-medium fine-tunes." |
| **DoRA + rsLoRA** (Liu et al. ICML 2024) | bf16/fp16 base. 1-3 % uplift over LoRA on most tasks. | ≈15 GB | "Start with LoRA or DoRA. They behaved the most predictably here." DoRA's main caveat: layers must often be merged to be inference-compatible. |
| **PiSSA / OLoRA + rsLoRA** | Small dataset / short run; methods that "start aligned" with layer structure. | ≈15 GB | "Pick the methods that 'start aligned'… but give them a friendlier warmup." Underperformed in Marie's experiment due to one-size-fits-all schedule — but likely best with tuned warmup. |
| **QLoRA** (Dettmers NeurIPS 2023) | Safe 4-bit fallback. | ≈18 GB at 4-bit | "QLoRA is still a solid baseline." |
| **LoftQ** (Li et al. 2023) — **PREFERRED 4-bit** | 4-bit base + best accuracy at 4-bit. | ≈18 GB at 4-bit | **"LoftQ gets the lowest loss"** in the 4-bit head-to-head. *"It was designed for [4-bit] and it shows."* Use this, not QDoRA. |
| **QDoRA** (Liu et al. + 4-bit) | Avoid at 4-bit. | ≈20 GB at 4-bit | "QDoRA is a bit better than QLoRA, but the extra DoRA parameters (which can be annoying to handle at inference) don't really justify the gain… can't be merged easily since the model is quantized." |
| **GaLore / Q-GaLore** (Zhao 2024) | DAPT phase on 214 K Pt corpus *before* SFT. | ≈16 GB for 7 B at 4-bit | Q-GaLore "reduces the memory consumption of fine-tuning by up to 50% compared to LoRA and consistently outperforms QLoRA with bitsandbytes" (Marie, Sep 2024). |
| **ReFT / LoReFT** (Stanford 2024) | Light task-specific heads (geometry, isomer, target). | <2 GB per head | Up to 50× fewer trainable params than LoRA at parity. |
| **Full fine-tune** | Never at academic budget. | >300 GB at FP16 | Rejected on cost. |

**Recipe by precision:**
- **bf16/fp16 base:** DoRA + `use_rslora=True`. Quick fallback to plain LoRA + rsLoRA if DoRA merge issues bite.
- **4-bit base:** **LoftQ**, not QDoRA. *"If you must quantize (4-bit / NF4): use LoftQ first."*
- **Continual pretraining on the 214 K corpus:** Q-GaLore (memory-efficient enough for a 16 GB GPU).
- **All small heads:** LoReFT.

**Pretraining strategy.** Before any SFT on the 17,732 labeled IC50 set, the proposal runs **domain-adaptive continued pretraining (DAPT)** on the 214,373 unlabeled Pt SMILES corpus using Q-GaLore. This "DAPT → SFT" pattern is standard in biomedical LLMs (PMC-LLaMA, BioMedLM) and is the right shape for the project's massive unlabeled / small labeled corpus structure.

**Tooling.** PEFT (Hugging Face), Unsloth, TRL for any DPO / KTO post-training, Axolotl as a configuration layer, bitsandbytes for 4-bit kernels, FlashAttention-3 for the H100/Blackwell forward pass. Apple Silicon prototyping uses MLX-LM (Simon Willison's Substack reports Llama-3.2-3B at 152 tok/s on an M3 Max).

**Reinforcement post-training (Phase 3).** If the lab wants the Supervisor agent (Pillar 3) to internalise verifiable chemistry rewards — e.g. "does this Pt(II) complex pass the metal-extended sanitization?" — **GRPO** (Group Relative Policy Optimization, used in DeepSeek-R1 training; covered by Cameron Wolfe's *Deep Learning Focus* Substack, Nov 2025) replaces PPO with an in-batch baseline and is now the standard RL optimizer for open reasoning models. TRL v1.0 (April 2026) provides the production implementation.

### Architecture sketch
```
candidate NatQG
     |
     v
+-----------------------+        +------------------------+
| MKANO (incumbent)     |        | ChemFM (proposed)      |
| ~M-sized GNN backbone |        | 3 B params, QLoRA+DoRA |
| (param count: see SI) |        | fine-tuned on Pt corpus |
+-----------------------+        +------------------------+
     |                                    |
     +----------- ensemble ----------------+
                          |
                          v
              calibrated probability with model-confidence breakdown
```
*Note on parameter counts: the MKANO parameter count is to be verified against the MetalKANO GitHub repository before publication; ChemFM is sized per Cai et al., Communications Chemistry 2025.*

### Validation strategy
- Test on identical splits used by Rusanov et al. (random, scaffold, cluster).
- Track Expected Calibration Error (ECE), the metric the source paper highlights as the key generalisation indicator.
- Public release of fine-tuned weights (subject to principal-investigator approval) — community visibility win.

## Component 1.4 — Truly generative architecture beyond fragment assembly

### Problem
The current de novo pipeline reassembles 20 most-frequent ligands combinatorially under chemical heuristics. The source paper itself flags this as the second target of future work.

### Approach

**Chemistry context — what makes organometallic generation different from organic.** Generic 3D-molecule diffusion (EDM, MiDi, GeoLDM) is trained on covalent organic graphs; transition-metal complexes break four standard assumptions: (i) dative bonds replace single bonds at the metal centre and require explicit edge tokens; (ii) coordination number is constrained per oxidation state (Pt(II) = 4, Pt(IV) = 6, Au(III) = 4, Re(I) ≈ 6 with fac-tricarbonyl); (iii) trans-influence and cis-trans isomerism determine activity; (iv) Lipinski's Rule of Five — designed for orally bioavailable organic small molecules in 1997 — is largely irrelevant for cytotoxic Pt/Au i.v. metallodrugs. The source paper itself uses *modified* Lipinski thresholds (atom count 20–70, molar refractivity 40–130) tuned to the metallodrug class. Any generative architecture proposed here must encode these constraints, not assume them.

- **Equivariant Neural Diffusion (END; Cornet et al., NeurIPS 2024)** on the NatQG representation. END improves on EDM/MiDi with a learnable, rigid-equivariant forward process and reports state-of-the-art on QM9 and GEOM-DRUGS. Operating on the (node, edge, 3D-coordinate, metal-token, oxidation-state) tuple natively respects the geometric constraints listed above.
- **Open architectural question (acknowledged):** Chaitanya Joshi's *Equivariance is dead, long live equivariance?* (Substack, June 2025) frames the architectural choice precisely. Quoting verbatim:
  > *"Roto-translation equivariance is still relevant for molecular simulation and property prediction problems. Diffusion-based generative models, on the other hand, are likely to move away from equivariance in favour of scaling."*

  The paradigm shift is documented across the field: AlphaFold2 used explicit roto-translation equivariance in its structure module; AlphaFold3 replaces this with a Transformer-based diffusion architecture and data augmentation. Joshi: *"AlphaFold3 is a very effective demonstration of geometric symmetries learnt at scale using a sufficiently expressive model."* Equivariant networks are *"orders of magnitude slower"* to train than standard Transformers on current hardware, but on small labeled chemistry data they remain competitive — Erik Bekkers' group (arXiv:2501.01999) has shown parameter-matched equivariant networks scale *better* than unconstrained denoisers on per-parameter terms.

  **Implication for the architecture.** The labeled Pt corpus (17,732 IC50 values across 4 cell lines) is small by foundation-model standards. Equivariance is the right call for Phase 1-2. Phase 3 should benchmark a scaled-transformer-diffusion variant (analogous to FAIR Chemistry's *All-atom Diffusion Transformers*, 2025) once the combined Pt + Au + Cu corpus crosses ≈100 K labeled examples or once the project adopts the OMol25 + tmQM combined pretraining corpus (≈250 K systems including transition metals). The proposal's commitment to equivariant diffusion in Phase 2 is therefore deliberately reversible.
- **Conditioning signals:** target protein embedding (from AF3 / Boltz-2; see Component 1.2), desired cell-line activity profile, target binding-affinity score (Boltz-2's affinity head — see below), and *modified-Lipinski* metallodrug drug-likeness as a soft penalty.
- **Synthesis-aware sampling, not synthesis-aware filtering.** Earlier de novo pipelines treat retrosynthesis as a post-hoc filter; the proposal embeds AiZynthFinder + IBM RXN retrosynthesis score into the sampler's reward (consistent with SynFormer, Gao/Luo/Coley PNAS 2025), so the generator never wastes capacity on unsynthesisable scaffolds.

### Component 1.4.1 — Direct precedent (Strandgaard et al., *JACS Au* 2025)

The single closest peer-reviewed precedent for the proposed work is **Strandgaard et al., *JACS Au* 5 (5), 2294-2308, April 2025** (DOI 10.1021/jacsau.5c00242). This paper shares a co-author (Balcells) with the MKANO source paper (Rusanov et al., 2026), so the existing external collaborator network already covers the theoretical-chemistry side of the proposed work.

**What Strandgaard et al. delivered:**
- A **Junction Tree Variational Autoencoder (JT-VAE)** for TM-ligand generation, trained on the tmQMg-L library (≈30K ligands derived from real TMCs in the CSD).
- A SMILES-based encoding of metal-ligand bonds using **[Li]/[Be]/[Ir] placeholder tokens** to bypass valence rules that do not apply to transition metals (e.g. κ¹-ethylenediamine = `NCCN→[Li]`, κ²-ethylenediamine = `C1N→[Ir]←NC1`). These placeholders are mapped to any real metal at decode time.
- Unconditional generation: **100 % valid (κ¹) / 96 % valid (κ²)** coordination modes; **95 % / 93 % novel** vs training; **69 % / 59 % unique** in 50K-sample sets. Training sets were 4,511 κ¹ + 4,582 κ² ligands (neutral, ≥4 heavy atoms).
- Conditional generation: jointly optimised HOMO-LUMO gap (ϵ) and metal-centre charge (q_Ir) for homoleptic [IrL₄]⁺ and [IrL₂]⁺ complexes; secondary conditioning on solubility (log P) and steric bulk.
- DFT validation with ORCA at PBE-D4/def2SVP (geometries) + PBE0-D4/def2TZVP (energies); molSimplify for complex assembly.

**Architectural choice: JT-VAE vs equivariant diffusion.** Strandgaard et al. chose JT-VAE for two reasons that remain valid in 2026: (i) the junction-tree formulation enforces chemical validity by fragment-by-fragment generation (more robust than atom-by-atom diffusion), and (ii) the encoder-decoder structure yields an interpretable latent space where optimisation trajectories can be inspected. The proposal's v3 commitment to *equivariant diffusion* (Component 1.4) is therefore deliberately complemented — not replaced — by a JT-VAE track in Phase 2. The two architectures cover complementary failure modes: diffusion explores broader chemical space at lower interpretability; JT-VAE delivers high validity with smaller exploration radius. Phase 3 benchmarks them head-to-head on the same conditioning objectives (anticancer activity, COL3A1 engagement).

**Adoption path.** The [Li]/[Be]/[Ir] SMILES encoding from Strandgaard et al. is directly portable into the Pillar 2 chemoinformatic-core sanitization pipeline as an optional pre-tokenisation step. The JT-VAE codebase can be extended from tmQMg-L (ligand-only) to a 17,732 Pt-IC50 corpus, with the conditioning targets swapped from (ϵ, q_Ir) to (cell-line activity, COL3A1 binding affinity). This is concretely a Phase 2 deliverable, executable by a single platform engineer in collaboration with the upstream theoretical-chemistry group.

**Code availability — direct fork-and-extend.** The published `tmcinvdes` repository (`github.com/uiocompcat/tmcinvdes`) contains the production code: `tmcinvdes/ligand_generation/` (training-set construction), `tmcinvdes/structure_generation/` (homoleptic TMC assembly), `tmcinvdes/quantum_chemistry/` (ORCA input + DFT property labelling), `tmcinvdes/analysis/` (SA score, outlier removal). The actual JT-VAE training code lives in the companion `github.com/Strandgaard96/JT-VAE-tmcinvdes` repository. The platform engineer clones both, swaps the tmQMg-L dataset link for the 17,732 IC50 set, and re-targets the conditional generation on (cell-line activity, COL3A1 affinity). The existing collaborator network covers the theoretical-chemistry side of both repos — *roughly 90 % of the Phase 2 generative pipeline has already shipped as published code*. This is the strongest single argument for why Phase 2 is months-of-work-not-years.
- **Hybrid generation strategy:** the fragment-assembly approach is *retained*. The diffusion sampler proposes novel geometries; a heuristic post-filter ensures synthesisability, including the chemical heuristics already implemented (cis-trans influence, ligand compatibility). The two strategies cover complementary regions of chemical space.

### Architecture sketch
```
target spec (cell line activity + protein target embedding + drug-likeness)
     |
     v
+----------------------+     +-----------------------------+
| Fragment-assembly    |     | Equivariant diffusion       |
| generator (incumbent)|     | generator (proposed)        |
+----------+-----------+     +--------------+--------------+
           |                                |
           +----------+---------------------+
                      |
                      v
              candidate union (Pt/Au/Cu/Re/Ru/Pd complexes)
                      |
                      v
              MKANO+ target-conditioned scorer (Component 1.2)
                      |
                      v
              ranked candidate list with rationale + synthesis route hint
```

### Validation strategy
- Generate 1,000 novel candidates conditioned on COL3A1 + A2780cis activity.
- Evaluate against fragment-assembly baseline on: chemical validity rate, synthesis-feasibility score (Retrosynthesis API), predicted activity rate.
- Synthesise top 5; benchmark experimentally.

## Technology choices

| Layer | Choice | Reason |
|---|---|---|
| Geometry-aware backbone | Equiformer / MACE | SE(3) equivariance; both have open-source implementations and strong precedent on transition-metal chemistry. |
| Functional prompt | Inherited from KANO | Validated against current MKANO; no reason to replace. |
| Structure prediction | AF3 (closed weights, paid inference) + Boltz-2 (open, self-hosted) | Dual-track preserves academic budget while accessing best-in-class. |
| Foundation backbone | ChemFM (open weights via Hugging Face) | Best published benchmark performance + permissive licensing. |
| Generative model | Equivariant diffusion (custom) | Native fit to metal geometry; reuses NatQG representation. |
| Training framework | PyTorch + PyTorch Lightning + DDP | Industry standard; aligns with MKANO codebase. |
| Hyperparameter search | Optuna | Open-source, integrates with MLflow. |

## Risks and unknowns

- **GPU budget.** Fine-tuning ChemFM and AF3 inference both require modern accelerators. Mitigation: lease cloud GPUs (institutional HPC where available; AWS / Lambda Labs as fallback). Estimated initial monthly compute: 2 × H100 + 4 × A100 ≈ US $3–5 K equivalent.
- **AF3 commercial terms.** Open weights but research-use license. The pipeline is engineered to work entirely with Boltz-2 if commercial restrictions tighten.
- **Equivariant diffusion training stability.** Equivariant architectures are sensitive to numerical precision and learning-rate schedules. Mitigation: start from published EDM / MACE training recipes; phase rollout — diffusion is a Phase 2 deliverable, not Phase 1.

## Phase deliverables

| Phase | Deliverable |
|---|---|
| Phase 1 (months 0–6) | Geometry-aware MKANO+ trained on tmQM + Pt data; baseline retained against original MKANO. |
| Phase 2 (months 6–12) | AF3 / Boltz-2 service running; target-conditioned scoring deployed; ChemFM LoRA-tuned backbone benchmarked. |
| Phase 3 (months 12–18) | Equivariant-diffusion generator producing novel candidates; first synthetic validation round complete. |
