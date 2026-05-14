# ADR-009 — Fine-tuning methodology: QLoRA + DoRA via Unsloth as default

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** The proposal commits to fine-tuning ChemFM (or equivalent 3 B-class chemistry foundation model) on a 17,732-IC50 Pt-complex corpus (matching the published MKANO dataset), with optional continued pretraining on the 214,373 unlabeled SMILES. The choice of fine-tuning method determines reproducibility, hardware footprint, and the cost of running ablations and per-metal head specialisations.

## Decision

**Two-recipe default split by base precision**, both with `use_rslora=True` always enabled.

### Recipe A — bf16/fp16 base (preferred when GPU memory permits)
- **DoRA** (Liu et al., ICML 2024) with rsLoRA scaling (Kalajdzievski 2023): `use_rslora=True` divides the LoRA update by √r instead of r, "strictly better than standard LoRA with no downsides" (Srivastava, Dec 2025) and enables high-rank (r=32-64) adapters to actually contribute.
- Backed by Marie's head-to-head Qwen3-4B-Base benchmark (Kaitchup, Nov 2025): *"DoRA tracks standard LoRA quite closely… start with LoRA or DoRA. They behaved the most predictably here."*

### Recipe B — 4-bit (NF4) base (preferred for academic-budget single-GPU)
- **LoftQ** (Li et al., 2023), not QDoRA. Marie's benchmark (Kaitchup, Nov 2025): *"LoftQ gets the lowest loss. QDoRA is a bit better than QLoRA, but the extra DoRA parameters (which can be annoying to handle at inference) don't really justify the gain… they can't be merged easily since the model is quantized."*
- LoftQ is "quantization-aware LoRA" — initialises the adapter to compensate for quantisation error before training begins.
- Plain QLoRA remains the safe fallback when LoftQ tooling lags a specific base model.

### Recipe selection rule
```
if base_precision == "4-bit":   use LoftQ  (designed for quantized)
elif data_is_small:             use PiSSA or OLoRA with careful LR warmup
else:                           use DoRA + rsLoRA
always:                         use_rslora=True
```

### Common across both recipes
- **Runtime:** Unsloth (concrete numbers from Aggarwal, Medium, Aug 2025): **Llama 3.1 on Alpaca completes in 2h34m with Unsloth vs 23h15m with vanilla HuggingFace on a Tesla T4 — 8.8× speedup**; Llama-3 8B uses **6.7 GB VRAM (Unsloth) vs 22.8 GB (HuggingFace) = 70 %+ reduction**. Zero accuracy degradation reported. Unsloth achieves this via manually-derived backpropagation in custom OpenAI Triton kernels (not PyTorch autograd) plus **Dynamic 4-bit Quantization** (selective per-layer precision based on quantization-error analysis, ~10 % more VRAM than naive 4-bit but with vision-model-class quality recovery). 30+ model architectures supported including Llama 4 Scout, gpt-oss-120b.
- **Context-length unlock — Cut Cross Entropy** (Unsloth × Apple Engineers): the kernel computes matrix multiplications on-the-fly rather than materialising full logit tensors. Concrete payoff: **Llama 3.3 70B context window 6.9K → 89K on an 80 GB GPU (13× improvement) at 1.9 % compute overhead and 30 % memory reduction**. Llama 3.1 8B reaches **342K tokens, exceeding the model's native 128K**. For metallodrug discovery this matters when an agent reasons over multi-paper retrieval contexts during DMTA campaigns.
- **Pretraining strategy:** Domain-adaptive continued pretraining (DAPT) on the 214 K Pt corpus via **Q-GaLore** (Marie, The Salt, Sep 2024) — *"reduces the memory consumption of fine-tuning by up to 50% compared to LoRA and consistently outperforms QLoRA with bitsandbytes"*. Enables 7B-class continual pretraining on a 16 GB GPU.
- **Task-specific heads** (geometry, isomer, target-engagement): **LoReFT** (Stanford 2024) — *"up to 50× fewer trainable parameters than LoRA at parity"* per Marie's *ReFT* synthesis in The Salt (April 2024). Significant when the system ships many small heads via the model registry.

### Reinforcement post-training — RLVR with GRPO (Phase 3, evidence-grounded)

The Phase 3 RL recipe is **Reinforcement Learning with Verifiable Rewards (RLVR) using GRPO as the optimiser**, not RLHF. The RLVR/RLHF distinction is load-bearing and worth restating verbatim from Wolfe's *Deep (Learning) Focus* synthesis (Nov 2025):

- **RLHF** trains the LLM using RL with rewards derived from a *reward model* trained on human preferences. The reward model is itself a finetuned LLM. PPO is the typical optimiser.
- **RLVR** trains the LLM using RL with rewards derived from *rule-based or deterministic verifiers* — no reward model. GRPO is the typical optimiser. Used to train DeepSeek-R1, Qwen-3, Olmo-3, Kimi-K2, OpenAI o1/o3/o4-class models.

The reason RLVR matters more than RLHF for chemistry is reward-hacking risk. Quoting DeepSeek's own paper (cited in Wolfe):
> *"We do not apply the outcome or process neural reward model in developing DeepSeek-R1-Zero, because we find that the neural reward model may suffer from reward hacking in the large-scale reinforcement learning process."*

Metallodrug discovery has *natively verifiable* reward signals — exactly the precondition RLVR requires:
- **Sanitization pass/fail.** Does the metal-extended RDKit pipeline (Pillar 2) accept the proposed structure? Binary, deterministic, no model in the loop.
- **Modified-Lipinski drug-likeness.** Hard thresholds (MW, logP, HBD, HBA, rotatable bonds, MR, atom count) — pure rule check.
- **Novelty.** Tanimoto similarity vs CSD / PubChem / host-lab portfolio — deterministic.
- **Synthetic accessibility.** Retrosynthesis score from AiZynthFinder or IBM RXN — deterministic given a fixed building-block library.
- **Geometry validity.** Coordination number per metal × oxidation state, cis/trans well-defined.

Each of these is a verifiable reward at low risk of being hacked. GRPO computes the policy update by sampling multiple completions per prompt and using an **in-batch baseline** (the group's average advantage), eliminating the learned critic that PPO requires. This is *the* reason GRPO has displaced PPO for open reasoning model training, and is the correct choice for a chemistry-Supervisor that must reason over verifiable chemistry constraints.

**Recipe (Phase 3):**
- Verifiable reward function = weighted sum of the five chemistry verifiers above.
- Generate N=8 candidate Pt complexes per prompt; compute reward per candidate; GRPO group-relative advantage; update policy.
- Run length-controlled to prevent reward-hacking via overly-long reasoning chains.
- TRL v1.0 (April 2026) for the production GRPO implementation.

**External precedent — ether0 (FutureHouse).** Narayanan et al., June 2025 preprint *Training a Scientific Reasoning Model for Chemistry* (per Decoding Bio *BioByte 120*) is the closest published precedent for GRPO-on-chemistry. ether0 is a **24 B-param Mistral-Small-24B base, GRPO-trained across seven chemistry sub-tasks** (retrosynthesis, solubility editing, etc.) on **640,730 experimentally grounded problems spanning 375 tasks**. Result: *"ether0 not only outperforms general-purpose LLMs (Claude, o1, o3) on open-answer chemistry questions, but also beats specialized tools and even human experts in molecular design tasks."* This validates the proposal's GRPO recipe shape on a published, weight-released model. The proposed RLVR setup is a specialised analogue: same optimiser (GRPO), same verifiable-reward principle, narrower domain (metallodrug discovery), smaller curated training set (≈18 K labeled IC50 + verifiable chemistry-rule rewards).

**Attention kernel — FlashAttention-4 on Blackwell (Lambda MLE, March 2026).** When the host lab's GPU pool includes B200 / GB300 NVL72 hardware (Phase 2-3 procurement option), the recommended attention kernel is **FlashAttention-4** (`pip install flash-attn-4`). Concrete benchmarks from the FA4 paper: **1613 TFLOPs/s peak forward at 71 % hardware utilization on B200 BF16**; **up to 1.3× speedup over cuDNN 9.13**; **up to 2.7× speedup over Triton**. Gains are strongest at ≥4K context lengths — exactly the regime the Supervisor agent operates in during a multi-week DMTA campaign. FA4 introduces three load-bearing techniques: (1) redesigned async pipeline with warp specialization (Blackwell's MMA is fully asynchronous); (2) software-emulated exponentials on FMA units (moves the bottleneck off SFUs that Blackwell has fewer of); (3) conditional softmax rescaling (~10× fewer rescaling ops per Tri Dao's Hot Chips 2025 presentation). Implemented in **CuTe-DSL**, a Python-embedded DSL inside NVIDIA's CUTLASS — installs and compiles in seconds vs the minutes/hours of older CUDA kernel workflows. On Hopper hardware, **FA3 remains the standard** (≈740 TFLOPs/s at 75 % utilization).

**Tooling:** PEFT (Hugging Face), Unsloth, TRL v1.0 (April 2026) for DPO / KTO / GRPO, Axolotl as configuration layer.

### Dependency fallback matrix (Phase-1 reproducibility safety net)

Several components named above pin to versions that were forward-dated at the time this ADR was written. The recipe is therefore paired with a fallback matrix so reproducibility does not depend on a single upstream release landing on schedule:

| Component | Phase-1 pinned version (works 2026-05-14) | Phase-2 / Phase-3 upgrade target | Fallback if upgrade slips |
| --- | --- | --- | --- |
| **Unsloth** | `unsloth>=2025.x` (latest 2025.x release at proposal start) | `unsloth>=2026.x` when Llama-4-Scout / gpt-oss-120b kernels stabilise | Pin to last-known-good 2025.x release; defer larger-model support to Phase 3 |
| **TRL** | `trl>=0.13` (current stable 2025-Q4 release; provides GRPO / DPO / KTO without v1.0 dependency) | `trl>=1.0` (April 2026 release, per FutureHouse / Anthropic adoption) | Stay on `trl>=0.13`; use the Phase-1 GRPO implementation if TRL 1.0 ships with breaking changes |
| **FlashAttention** | **FA-3** on Hopper (≈740 TFLOPs/s, 75 % utilisation) | **FA-4** on Blackwell when B200 / GB300 NVL72 hardware is procured | FA-3 remains production-grade on Hopper indefinitely; FA-4 is a Blackwell-only Phase-2/3 upgrade |
| **PyTorch** | `torch>=2.5` (current stable) | `torch>=2.7` for Blackwell native support | Stay on 2.5 LTS-equivalent; defer Blackwell support to Phase 3 |
| **bitsandbytes** | `bitsandbytes>=0.43` | `bitsandbytes>=0.45` when AWQ kernel improvements land | 0.43 covers the AWQ / NF4 production paths; upgrade is optional |
| **CUDA** | 12.4+ (Hopper); 12.6+ when Blackwell is on-prem | 12.8+ when CuTe-DSL becomes mandatory | Hold on the lab's actual CUDA driver version; defer Blackwell-only kernels |

**Reproducibility rule:** every fine-tuning run records all six versions in MLflow alongside the dataset DVC hash and the Hydra config hash. A failed reproducibility check is a stop-the-line event.

## Rationale

- **QLoRA at 4-bit is the 2025-2026 default** for academic-budget LLM fine-tuning. It is the most-cited method in practitioner press (Kaitchup, Maarten Grootendorst, Unsloth docs) and the only method that consistently delivers fine-tuning of 70 B-class models on single-GPU hardware.
- **DoRA over plain LoRA** is the cheapest reliable accuracy uplift (no extra VRAM, modest extra compute). The Kaitchup *Advanced LoRA Fine-Tuning* article (Nov 2025) makes this the headline recommendation.
- **Unsloth over raw PEFT** is the production runtime; the speedup is well-documented and the configuration overhead is minimal.
- **Q-GaLore for DAPT** enables continual pretraining on a growing unlabelled corpus *without* an H100 fleet. This is uniquely well-suited to the academic lab budget.
- **LoReFT for heads** is the parameter-efficient extreme for the many small task-specific heads the architecture deploys — a fit the proposal would otherwise miss.

## Consequences

- The fine-tuning code is opinionated and version-locked (`unsloth>=2025.x`, `peft>=0.11`, `bitsandbytes>=0.43`, `trl>=1.0`).
- Reproducibility requires Unsloth's specific kernel paths (typically Linux + NVIDIA only).
- Apple Silicon fallback uses **MLX-LM + MLX-LoRA + the `llm-mlx` plugin** for chemist-workstation dev/prototyping (Willison, Feb 2025) — not production training.

### Apple Silicon dev/inference profile (concrete numbers, Willison Feb 2025)

Host-lab chemists run Mac workstations; the platform supports them as a first-class dev target. Concrete throughput numbers on Apple Silicon (from Willison's measurements):

| Model | 4-bit weight size | Throughput | RAM use | Notes |
|---|---|---|---|---|
| Qwen2.5-0.5B-Instruct | 278 MB | 510 tok/s on M4 Max; >150 tok/s on iPhone 16 Pro | <1 GB | "Whopping" speed; routine helpers |
| Llama-3.2-3B-Instruct | 1.8 GB | **152 tok/s** on M-series Mac | ≈3 GB | Sweet spot for chemist-workstation literature triage |
| Mistral-7B-Instruct-v0.3 | 4.08 GB | (not measured) | ≈5 GB | |
| Mistral-Small-24B-Instruct | 13.26 GB | (not measured) | ≈14 GB | *"Feels GPT-4 quality despite only needing around 12 GB of RAM"* |
| DeepSeek-R1-Distill-Qwen-32B | 18.5 GB | (not measured) | ≈20 GB | Reasoning-style `<think>` blocks |
| Llama-3.3-70B-Instruct | 40 GB | **8.8 tok/s** | **37.5 GB** | Runs on 64 GB Mac; *"very capable"* |

Implication for the host lab: a chemist with a Mac Studio (64 GB RAM) can run **Llama-3.3-70B locally** for confidential literature triage, novel-scaffold reasoning, and MoA hypothesis generation without sending data to a cloud API. Slow (8.8 tok/s) but private — the right trade-off for pre-publication compound work where data sovereignty trumps latency. A Mac Studio with M4 Max (≈US $5K capex, no recurring cloud cost) is the recommended chemist-workstation configuration.

## Alternatives considered

- **Plain LoRA.** Rejected on accuracy parity grounds; DoRA dominates at the same cost.
- **PiSSA + LoftQ.** Strong alternative when initialising from a quantised base; evaluated per-model.
- **Full fine-tuning.** Rejected on cost (>300 GB VRAM at FP16 for 3 B base, and orders worse for 70 B).
- **DPO / ORPO / KTO without prior GRPO.** Considered for the Supervisor agent; deferred to Phase 3 because verifiable chemistry rewards (sanitization, drug-likeness) are a better fit for GRPO.

## Revisit conditions

- A successor PEFT method displaces DoRA (e.g. rsLoRA, X-LoRA, EVA) with measurable lift.
- Unsloth ceases active development.
- An open-weights chemistry foundation model substantially exceeds ChemFM and changes the default backbone.
