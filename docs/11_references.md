# 11 — References

**Contents**

- [Source paper](#source-paper)
- [AI / ML foundations](#ai-ml-foundations)
- [Transition-metal-specific datasets and methods](#transition-metal-specific-datasets-and-methods)
- [Agentic AI for chemistry and drug discovery](#agentic-ai-for-chemistry-and-drug-discovery)
- [Reviews and overviews](#reviews-and-overviews)
- [Multi-omics and target deconvolution](#multi-omics-and-target-deconvolution)
- [Self-driving labs](#self-driving-labs)
- [Cisplatin biology and mechanism](#cisplatin-biology-and-mechanism)
- [Cheminformatics tooling](#cheminformatics-tooling)
- [Local LLM fine-tuning and inference](#local-llm-fine-tuning-and-inference)
- [Agent frameworks and protocols](#agent-frameworks-and-protocols)
- [American peer-reviewed venues](#american-peer-reviewed-venues)
- [Practitioner press (Substack / Medium / blogs)](#practitioner-press-substack-medium-blogs)
- [Public code repositories](#public-code-repositories)
- [Source-paper adjacent research lines (cited for context)](#source-paper-adjacent-research-lines-cited-for-context)


## Source paper

1. Rusanov, D. A.; Matnurov, E. M.; Dolgov, D.; Brezgunov, D. Yu.; Ivanov-Rostovtsev, P. A.; Kriukov, K.; Pashaliev, B. L.; Choe, H.-J.; Yarshova, M.; Luk, J. H. K. K.; Petrović, T.; Abylova, B.; Aitkulova, D.; Alfadul, S. M.; D'Cruz, G.; Vetrova, V. V.; Balcells, D.; Babak, M. V. *Overcoming cisplatin resistance with AI-driven metallodrug discovery*. ChemRxiv preprint, 2 March 2026. DOI: [10.26434/chemrxiv-2025-pp32k/v2](https://doi.org/10.26434/chemrxiv-2025-pp32k/v2). Code: [github.com/thebabaklab/MetalKANO](https://github.com/thebabaklab/MetalKANO). Platform: [mb-finder.org](https://www.mb-finder.org).

## AI / ML foundations

2. Fang, Y.; Zhang, Q.; Zhang, N.; Chen, Z.; Zhuang, X.; Shao, X.; Fan, X.; Chen, H. *Knowledge graph-enhanced molecular contrastive learning with functional prompt*. Nature Machine Intelligence 5, 542–553 (2023).

3. Abramson, J. et al. *Accurate structure prediction of biomolecular interactions with AlphaFold 3*. Nature 630, 493–500 (2024).

4. Levine, D. S. et al. *The open molecules 2025 (OMol25) dataset, evaluations, and models*. arXiv:[2505.08762](https://arxiv.org/abs/2505.08762) (2025).

5. ChemFM: scaling-law-guided chemistry foundation model pre-trained on informative chemicals. Communications Chemistry (2025).

6. Boltz-2: an open-source structure-prediction model. MIT, 2025.

7. Corso, G.; Stärk, H.; Jing, B.; Barzilay, R.; Jaakkola, T. *DiffDock: diffusion steps, twists, and turns for molecular docking*. ICLR 2023.

8. Hoogeboom, E.; Satorras, V. G.; Vignac, C.; Welling, M. *Equivariant diffusion for molecule generation in 3D*. ICML 2022.

## Transition-metal-specific datasets and methods

9. Balcells, D.; Skjelstad, B. B. *tmQM dataset — quantum geometries and properties of 86k transition metal complexes*. Journal of Chemical Information and Modeling 60, 6135–6146 (2020).

10. Kneiding, H.; Nova, A.; Balcells, D. *Directional multiobjective optimization of metal complexes at the billion-system scale*. Nature Computational Science 4, 263–273 (2024).

11. Kneiding, H.; Balcells, D. *tmQMg\*: Dataset of excited-state properties of 74k transition metal complexes*. Journal of Chemical Information and Modeling 65, 11766–11777 (2025).

12. Kneiding, H. et al. *Deep learning metal complex properties with natural quantum graphs*. Digital Discovery 2, 618–633 (2023).

13. Strandgaard, M.; Linjordet, T.; Kneiding, H.; Burnage, A. L.; Nova, A.; Jensen, J. H.; Balcells, D. *A Deep Generative Model for the Inverse Design of Transition Metal Ligands and Complexes*. JACS Au 5 (5), 2294–2308 (April 2025). DOI [10.1021/jacsau.5c00242](https://doi.org/10.1021/jacsau.5c00242). Code: [github.com/uiocompcat/tmcinvdes](https://github.com/uiocompcat/tmcinvdes); [github.com/Strandgaard96/JT-VAE-tmcinvdes](https://github.com/Strandgaard96/JT-VAE-tmcinvdes).

14. Rasmussen, M. H. et al. *SMILES all around: structure to SMILES conversion for transition metal complexes*. Journal of Cheminformatics 17, 1–13 (2025).

15. Orsi, M.; Shing Loh, B.; Weng, C.; Ang, W. H.; Frei, A. *Using machine learning to predict the antibacterial activity of ruthenium complexes*. Angewandte Chemie International Edition 63, e202317901 (2024).

16. López-López, E.; Medina-Franco, J. L. *MetAP DB and Metal-FP: a database and fingerprint framework for advancing metal-based drug discovery*. Journal of Computer-Aided Molecular Design 40, 8 (2025).

17. Janet, J. P.; Kulik, H. J. *Accurate multiobjective design in a space of millions of transition metal complexes with neural-network-driven efficient global optimization*. ACS Central Science 6, 513–524 (2020).

## Agentic AI for chemistry and drug discovery

18. Bran, A. M. et al. *Augmenting large language models with chemistry tools (ChemCrow)*. Nature Machine Intelligence 6, 525–535 (2024).

19. Boiko, D. A. et al. *Autonomous chemical research with large language models*. Nature 624, 570–578 (2023).

20. Tippy: a multi-agent framework for the Design–Make–Test–Analyze cycle. arXiv:[2507.09023](https://arxiv.org/abs/2507.09023) (2025).

21. Coley, C. W.; Eyke, N. S.; Jensen, K. F. *Autonomous discovery in the chemical sciences part II: outlook*. Angewandte Chemie International Edition 59, 23414–23436 (2020).

22. Amazon Bio Discovery announcement, AWS, April 2026. *Agentic AI for drug discovery with 40+ biological foundation models*. Press release.

## Reviews and overviews

23. Ferreira, F. J. N.; Carneiro, A. S. *AI-driven drug discovery: a comprehensive review*. ACS Omega 10, 23889–23903 (2025).

24. Zhang, K.; Yang, X.; Wang, Y. et al. *Artificial intelligence in drug development*. Nature Medicine 31, 45–59 (2025).

25. Schneider, P. et al. *Rethinking drug design in the artificial intelligence era*. Nature Reviews Drug Discovery 19, 353–364 (2020).

26. Vamathevan, J. et al. *Applications of machine learning in drug discovery and development*. Nature Reviews Drug Discovery 18, 463–477 (2019).

## Multi-omics and target deconvolution

27. Schulte-Sasse, R. et al. *Integration of multiomics data with graph convolutional networks to identify new cancer genes and their associated molecular mechanisms*. Nature Machine Intelligence 3, 513–526 (2021).

28. Gogleva, A. et al. *Knowledge graph-based recommendation framework identifies drivers of resistance in EGFR mutant non-small cell lung cancer*. Nature Communications 13, 1667 (2022).

29. Allesøe, R. L. et al. *Discovery of drug-omics associations in type 2 diabetes with generative deep-learning models*. Nature Biotechnology 41, 399–408 (2023).

## Self-driving labs

30. Self-driving laboratories: a review of technology and applications. PMC12368842 (2025).

31. RoboChem-Flex: a flexible and affordable self-driving laboratory for automated reaction optimization. Nature Synthesis (2026).

32. Bai, J. et al. *A dynamic knowledge graph approach to distributed self-driving laboratories*. Nature Communications 15, 462 (2024).

## Cisplatin biology and mechanism

33. Galluzzi, L. et al. *Molecular mechanisms of cisplatin resistance*. Oncogene 31, 1869–1883 (2012).

34. Galluzzi, L. et al. *Systems biology of cisplatin resistance: past, present and future*. Cell Death and Disease 5, e1257 (2014).

35. Wang, L.; Sun, Y.; Guo, Z.; Liu, H. *COL3A1 overexpression associates with poor prognosis and cisplatin resistance in lung cancer*. Balkan Medical Journal 39, 393–400 (2022).

36. Casini, A.; Pöthig, A. *Metals in cancer research: beyond platinum metallodrugs*. ACS Central Science 10, 242–250 (2024).

## Cheminformatics tooling

37. RDKit: open-source cheminformatics software. [rdkit.org](http://www.rdkit.org).

38. Weininger, D. *SMILES, a chemical language and information system. 1. Introduction to methodology and encoding rules*. Journal of Chemical Information and Computer Sciences 28, 31–36 (1988).

39. Lipinski, C. A.; Lombardo, F.; Dominy, B. W.; Feeney, P. J. *Experimental and computational approaches to estimate solubility and permeability in drug discovery and development settings*. Advanced Drug Delivery Reviews 23, 3–25 (1997).

## Local LLM fine-tuning and inference

40. Hu, E. J. et al. *LoRA: Low-Rank Adaptation of Large Language Models*. ICLR 2022 (arXiv:[2106.09685](https://arxiv.org/abs/2106.09685), 2021).

41. Kalajdzievski, D. *A Rank-Stabilization Scaling Factor for Fine-Tuning with LoRA (rsLoRA)*. arXiv:[2312.03732](https://arxiv.org/abs/2312.03732) (2023).

42. Dettmers, T. et al. *QLoRA: Efficient Finetuning of Quantized LLMs*. NeurIPS 2023.

43. Liu, S.-Y. et al. *DoRA: Weight-Decomposed Low-Rank Adaptation*. ICML 2024.

44. Zhao, J. et al. *GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection*. ICML 2024.

45. Zhang, R. et al. *Q-GaLore: Quantized GaLore with INT4 Projection and Layer-Adaptive Low-Rank Gradients*. 2024.

46. Wu, Z. et al. *ReFT: Representation Finetuning for Language Models*. Stanford, 2024.

47. Kwon, W. et al. *Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)*. SOSP 2023.

48. Zheng, L. et al. *SGLang: Efficient Execution of Structured Language Model Programs*. NeurIPS 2024.

49. Lin, J. et al. *AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration*. MLSys 2024.

50. Frantar, E. et al. *GPTQ: Accurate Post-Training Quantization for Generative Pre-Trained Transformers*. ICLR 2023.

51. Shah, J. et al. *FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-Precision*. 2024.

52. Leviathan, Y.; Kalman, M.; Matias, Y. *Fast Inference from Transformers via Speculative Decoding*. ICML 2023.

53. Li, Y. et al. *EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty*. 2024.

54. Li, Y. et al. *LoftQ: LoRA-Fine-Tuning-Aware Quantization for Large Language Models*. ICLR 2024 (arXiv:[2310.08659](https://arxiv.org/abs/2310.08659), 2023).

## Agent frameworks and protocols

55. Anthropic. *Building Effective Agents*. Anthropic Engineering, December 2024. [anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents)

56. Anthropic. *Code execution with MCP: building more efficient AI agents*. Anthropic Engineering, December 2025.

57. Anthropic. *Model Context Protocol (MCP) Specification*. 2024–2025. [modelcontextprotocol.io](https://modelcontextprotocol.io)

58. Anthropic. *How we built our multi-agent research system*. Anthropic Engineering, 2025.

59. Khattab, O. et al. *DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines*. ICLR 2024.

60. Shao, Z. et al. *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models* (introduces GRPO). 2024.

61. Microsoft Research. *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*. 2024.

62. Anthropic. *Introducing Contextual Retrieval*. Anthropic Engineering, September 2024.

63. Bekkers, E. et al. *Parameter-efficient equivariant networks scale*. arXiv:[2501.01999](https://arxiv.org/abs/2501.01999) (2025).

64. Narayanan, S. et al. (FutureHouse). *Training a Scientific Reasoning Model for Chemistry (ether0)*. arXiv preprint, June 2025.

## American peer-reviewed venues

65. Toney, J. W. et al. *Graph neural networks for predicting metal-ligand coordination of transition metal complexes*. PNAS 122 (41), e2415658122 (2025). DOI [10.1073/pnas.2415658122](https://doi.org/10.1073/pnas.2415658122).

66. Toney, J. W. et al. *Identifying Dynamic Metal-Ligand Coordination Modes with Ensemble Learning*. JACS 147 (52), 48218–48234 (2025). DOI [10.1021/jacs.5c17169](https://doi.org/10.1021/jacs.5c17169).

67. *(See Ref 13: Strandgaard et al., A Deep Generative Model for the Inverse Design of Transition Metal Ligands and Complexes. JACS Au 5 (5), 2294–2308, 2025.)*

68. Lu, R. et al. *Generative Design of Functional Metal Complexes Utilizing the Internal Knowledge and Reasoning Capability of Large Language Models*. JACS 147 (36), 32377–32388 (2025). DOI [10.1021/jacs.5c02097](https://doi.org/10.1021/jacs.5c02097).

69. Nandy, A.; Duan, C.; Taylor, M. G.; Liu, F.; Steeves, A. H.; Kulik, H. J. *Computational Discovery of Transition-Metal Complexes: From High-Throughput Screening to Machine Learning*. Chem. Rev. 121 (16), 9927–10000 (2021). DOI [10.1021/acs.chemrev.1c00347](https://doi.org/10.1021/acs.chemrev.1c00347).

70. Smaldone, A. M. et al. *Quantum Machine Learning in Drug Discovery: Applications in Academia and Pharmaceutical Industries*. Chem. Rev. 125 (5), 5436–5460 (2025). DOI [10.1021/acs.chemrev.4c00678](https://doi.org/10.1021/acs.chemrev.4c00678).

71. Krishna, R. et al. *Generalized biomolecular modeling and design with RoseTTAFold All-Atom*. Science 384 (6693), eadl2528 (2024). DOI [10.1126/science.adl2528](https://doi.org/10.1126/science.adl2528).

72. Passaro, S. et al. *Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction*. bioRxiv (2025). DOI [10.1101/2025.06.14.659707](https://doi.org/10.1101/2025.06.14.659707).

73. Gao, S. et al. (Zitnik group). *Empowering biomedical discovery with AI agents*. Cell 187 (22), 6125–6151 (2024). DOI [10.1016/j.cell.2024.09.022](https://doi.org/10.1016/j.cell.2024.09.022).

74. Bunne, C. et al. *How to build the virtual cell with artificial intelligence: Priorities and opportunities*. Cell 187 (25), 7045–7063 (2024). DOI [10.1016/j.cell.2024.11.015](https://doi.org/10.1016/j.cell.2024.11.015).

75. Gao, W.; Luo, S.; Coley, C. W. *Generative AI for navigating synthesizable chemical space (SynFormer)*. PNAS 122 (41), e2415665122 (2025). DOI [10.1073/pnas.2415665122](https://doi.org/10.1073/pnas.2415665122).

76. Cornet, F. et al. *Equivariant Neural Diffusion for Molecule Generation*. NeurIPS 2024.

77. Liao, Y.-L. et al. *EquiformerV2: Improved Equivariant Transformer for Scaling to Higher-Degree Representations*. ICLR 2024.

78. Boiko, D. A.; MacKnight, R.; Kline, B.; Gomes, G. *Autonomous chemical research with large language models* (Coscientist). Nature 624, 570–578 (2023). DOI [10.1038/s41586-023-06792-0](https://doi.org/10.1038/s41586-023-06792-0).

79. Szymanski, N. J. et al. *An autonomous laboratory for the accelerated synthesis of novel materials* (A-Lab). Nature 624, 86–91 (2023). DOI [10.1038/s41586-023-06734-w](https://doi.org/10.1038/s41586-023-06734-w).

80. Bran, A. M. et al. *Augmenting large language models with chemistry tools* (ChemCrow). Nat. Mach. Intell. 6, 525–535 (2024). DOI [10.1038/s42256-024-00832-8](https://doi.org/10.1038/s42256-024-00832-8).

81. Cai, F. et al. *ChemFM as a scaling-law-guided foundation model pre-trained on informative chemicals*. Commun. Chem. 9, 3 (2025). DOI [10.1038/s42004-025-01793-8](https://doi.org/10.1038/s42004-025-01793-8).

82. Pyzer-Knapp, E. et al. *A Perspective on Foundation Models in Chemistry*. JACS Au (2024). DOI [10.1021/jacsau.4c01160](https://doi.org/10.1021/jacsau.4c01160).

83. Levine, D. S. et al. *The Open Molecules 2025 (OMol25) Dataset, Evaluations, and Models*. arXiv:[2505.08762](https://arxiv.org/abs/2505.08762) (2025).

84. Wei, J. et al. *Machine Learning Approach to Anticancer Activity Prediction of Transition-Metal Complexes Based on a Large-Scale Experimental Database (MetalCytoToxDB)*. J. Med. Chem. (2026, in press). DOI [10.1021/acs.jmedchem.5c02755](https://doi.org/10.1021/acs.jmedchem.5c02755).

85. Casini, A.; Pöthig, A. *Metals in Cancer Research: Beyond Platinum Metallodrugs*. ACS Cent. Sci. 10 (2), 242–250 (2024). DOI [10.1021/acscentsci.3c01340](https://doi.org/10.1021/acscentsci.3c01340).

## Practitioner press (Substack / Medium / blogs)

86. Marie, B. *A Comparison of 5 Quantization Methods for LLMs*. The Kaitchup (Substack), March 2025. [kaitchup.substack.com/p/a-comparison-of-5-quantization-methods](https://kaitchup.substack.com/p/a-comparison-of-5-quantization-methods)

87. Marie, B. *Advanced LoRA Fine-Tuning: How to Pick LoRA, QLoRA, DoRA, PiSSA, OLoRA, EVA, and LoftQ for LLMs*. The Kaitchup, November 2025. [kaitchup.substack.com/p/advanced-lora-fine-tuning-how-to](https://kaitchup.substack.com/p/advanced-lora-fine-tuning-how-to)

88. Marie, B. *Q-GaLore: Pre-Train 7B Parameter LLMs on a 16 GB GPU*. The Salt (Substack), September 2024. [thesalt.substack.com/p/q-galore-pre-train-7b-parameter-llms](https://thesalt.substack.com/p/q-galore-pre-train-7b-parameter-llms)

89. Marie, B. *vLLM v1 Engine: How Faster Is It for RTX and Mid-Range GPUs?*. The Kaitchup, March 2025. [kaitchup.substack.com/p/vllm-v1-engine-how-faster-is-it-for](https://kaitchup.substack.com/p/vllm-v1-engine-how-faster-is-it-for)

90. Marie, B. *vLLM vs Ollama: Which LLM Inference Tool Should You Use?*. The Kaitchup, July 2025. [kaitchup.substack.com/p/vllm-vs-ollama-how-they-differ-and](https://kaitchup.substack.com/p/vllm-vs-ollama-how-they-differ-and)

91. Marie, B. *AI Notebooks — 198 Colab notebooks for fine-tuning, quantization, and inference*. The Kaitchup (Substack), 2024–2026.

92. The Neural Maze. *A Practical Guide to LLM Inference at Scale*. The Neural Maze (Substack), April 2026. [theneuralmaze.substack.com/p/a-practical-guide-to-llm-inference](https://theneuralmaze.substack.com/p/a-practical-guide-to-llm-inference)

93. Tang, Y. et al. *State of the Model Serving Communities — October 2025*. InferenceOps (Substack), October 2025. [inferenceops.substack.com/p/state-of-the-model-serving-communities-269](https://inferenceops.substack.com/p/state-of-the-model-serving-communities-269)

94. Liu, N. *How to Train Your Own EAGLE Speculative Decoding Model (BaldEagle)*. Frugal GPU (Substack), June 2025. [frugalgpu.substack.com/p/how-to-train-your-own-eagle-speculative](https://frugalgpu.substack.com/p/how-to-train-your-own-eagle-speculative)

95. Willison, S. *Run LLMs on macOS using llm-mlx and Apple's MLX framework*. Simon Willison's Newsletter (Substack), February 2025. [simonw.substack.com/p/run-llms-on-macos-using-llm-mlx-and](https://simonw.substack.com/p/run-llms-on-macos-using-llm-mlx-and)

96. Wolfe, C. R. *Group Relative Policy Optimization (GRPO)*. Deep (Learning) Focus (Substack), November 2025. [cameronrwolfe.substack.com/p/grpo](https://cameronrwolfe.substack.com/p/grpo)

97. Greyling, C. *Anthropic Says Don't Build Agents, Build Skills Instead!*. Cobus Greyling (Substack), January 2026. [cobusgreyling.substack.com/p/anthropic-says-dont-build-agents](https://cobusgreyling.substack.com/p/anthropic-says-dont-build-agents)

98. Huang, K. *Chapter 12: The Skill System Pattern*. Ken Huang (Substack), April 2026. [kenhuangus.substack.com/p/chapter-12-the-skill-system-pattern](https://kenhuangus.substack.com/p/chapter-12-the-skill-system-pattern)

99. McGuinness, P. *Design Patterns for Effective AI Agents*. AI Changes Everything (Substack), March 2025. [patmcguinness.substack.com/p/design-patterns-for-effective-ai](https://patmcguinness.substack.com/p/design-patterns-for-effective-ai)

100. Wagen, A. *Benchmarking NNPs, Orb-v2, and MACE-MP-0*. Rowan Newsletter (Substack), January 2025. [rowansci.substack.com/p/benchmarking-nnps-orb-v2-and-mace](https://rowansci.substack.com/p/benchmarking-nnps-orb-v2-and-mace)

101. Wagen, A. *BREAKING: Boltz-2 Now Live On Rowan*. Rowan Newsletter (Substack), June 7 2025.

102. Quigley, I.; Blevins, A. *AI for chemistry in 2025 is like AI for images in 2010*. Leash Biosciences (Substack), December 2025. [leashbio.substack.com/p/ai-for-chemistry-in-2025-is-like](https://leashbio.substack.com/p/ai-for-chemistry-in-2025-is-like) (companion preprint *Clever Hans in Chemistry: Chemist Style Signals Confound Activity Prediction on Public Benchmarks*).

103. Joshi, C. *Equivariance is dead, long live equivariance?*. Chaitanya Joshi (Substack), June 2025. [chaitjo.substack.com](https://chaitjo.substack.com)

104. Decoding Bio. *BioByte 120: FutureHouse launches ether0, OriGene, and Boltz-2*. Decoding Bio (Substack), June 2025. [decodingbio.substack.com/p/biobyte-120-futurehouse-launches](https://decodingbio.substack.com/p/biobyte-120-futurehouse-launches)

105. Tran, N. *AI Agent Framework Landscape 2025: LangGraph vs CrewAI vs Microsoft Agent Framework vs OpenAI Agents SDK*. Medium, November 2025.

106. Aggarwal, R. *Speeding up Llama 3.1 fine-tuning on Tesla T4 with Unsloth (2h34m vs 23h15m)*. Medium, August 2025.

107. Srivastava, A. *rsLoRA: when `use_rslora=True` is strictly better than the default*. Substack practitioner note, December 2025.

108. Lambda Labs MLE Team. *FlashAttention-4 on Blackwell: 1613 TFLOPs/s peak forward at 71 % hardware utilization*. Lambda blog, March 2026.

109. Dao, T. *FlashAttention-4 design notes*. Hot Chips 2025 presentation, August 2025.

110. Evans, A.; Desai, R. *Self-driving labs = infrastructure, not just intelligence*. TechPolitik (Substack), February 2026.

111. Yang, T. *Science startup taxonomy: ScienceData-as-a-Service vs Lab Orchestration vs Discovery-as-a-Service vs Automation-Native Instruments*. Substack, 2025–2026.

112. BoringBot. *Skills, MCP, and the architecture most teams discover last*. May 2026.

113. Perera, P. *The Lab Without Scientists*. Substack, January 2026 (synthesises AlphaFold 3 failure-mode evaluations).

114. Frugal GPU. *Disaggregated prefill/decode in production LLM serving*. Substack, 2025.

## Public code repositories

The following public GitHub repositories are cited inline throughout the proposal as reference implementations the platform engineer adopts or forks during Phase 1. All four are public, MIT- or Apache-licensed unless otherwise noted, and ship with documentation that reduces integration to days rather than months.

115. **MetalKANO** — the published reference implementation accompanying the source paper. [github.com/thebabaklab/MetalKANO](https://github.com/thebabaklab/MetalKANO). Status: ground truth for reproducing the 5-step metal-extended RDKit sanitization, the MKANO contrastive GNN training pipeline, and the 19 PlatinAI-era HTS predictions.

116. **tmcinvdes** — Strandgaard / Balcells workflow layer for transition-metal complex JT-VAE design. [github.com/uiocompcat/tmcinvdes](https://github.com/uiocompcat/tmcinvdes). Companion training repo: [github.com/Strandgaard96/JT-VAE-tmcinvdes](https://github.com/Strandgaard96/JT-VAE-tmcinvdes). Status: Phase 2 fork-and-extend target for the generative-diffusion / JT-VAE track.

117. **pydentate** — Kulik group pip-installable denticity + coordinating-atom predictor (Toney et al., PNAS 2025; JACS 2025). [github.com/hjkgrp/pydentate](https://github.com/hjkgrp/pydentate). Status: Phase 1 upstream dependency for the chemoinformatic-core sanitization pipeline; `pip install pydentate` + adapter glue ≈ 1–2 weeks integration work.

118. **chemist-style-leaderboard** — Leash Biosciences authorship-stratified evaluation methodology. [github.com/Leash-Labs/chemist-style-leaderboard](https://github.com/Leash-Labs/chemist-style-leaderboard). Ships with the *Clever Hans in Chemistry* PDF (2 MB, included in the repo). Status: Phase 1 evaluation-harness dependency for the by-source-lab split.

119. **anthropic-cookbook** — Anthropic-maintained pattern library; `patterns/agents/` directory contains three reference notebooks that directly map to three of the six chemistry roles in Pillar 3. [github.com/anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook). Status: Phase 1 fork-and-specialise target for Supervisor / Analysis / Synthesis-Assay-Design agent prompts.

120. **Unsloth** — production fine-tuning runtime (8.8× speedup vs vanilla HuggingFace; 70 %+ VRAM reduction; Llama 4 Scout, gpt-oss-120b support). [github.com/unslothai/unsloth](https://github.com/unslothai/unsloth). Status: default fine-tuning runtime for Pillar 1 and ADR-009.

## Source-paper adjacent research lines (cited for context)

121. Adjacent research lines published by the source-paper authors include: *Modulating the microbiome as an approach to anticancer drug development* (PNAS 2025); *Immunogenic cell death in mesothelioma* (JACS 2025); *Cancer care in conflict-affected populations* (The Lancet 2024); hydrogen-peroxide complex of tin (Nature Communications 2024). Full citations available via the corresponding author of Rusanov et al., 2026.
