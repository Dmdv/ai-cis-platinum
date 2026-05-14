# ADR-008 — Three-tier inference serving stack

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Quantisation policy](#quantisation-policy)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** MB Finder v2 serves three qualitatively different inference workloads: a small GNN classifier (MKANO+), foundation-model and LLM inference (ChemFM-LoRA, Llama 3 / Qwen 2.5 / ChemDFM), and structure prediction (AlphaFold 3 / Boltz-2 / RoseTTAFold All-Atom). Each has different latency, batching, and GPU-utilisation profiles. A single serving stack would be suboptimal everywhere.

## Decision

Adopt a three-tier serving stack with **phased rollout** to keep Phase-1 operational surface small:

| Tier | Workloads | Phase-1 stack (minimum operational) | Phase-2 / Phase-3 graduations (gated) |
|---|---|---|---|
| Tier 1 — small models | MKANO+ GNN classifier, geometry heads, per-metal heads | **KServe** (CNCF-incubating, K8s-native), PyTorch runtime, FP16. Sub-50 ms p95. | — (already simple) |
| Tier 2 — LLMs and foundation models | ChemFM-LoRA scorer, Llama 3 70B (orchestrator), Qwen 2.5 32B (design), ChemDFM-13B (analysis) | **vLLM v1** + **AWQ** 4-bit + **FlashAttention-3** behind KServe (single-tenant). 100–500 ms TTFT. | (a) **NVIDIA Triton + vLLM backend** for multi-tenant when ≥ 10 sustained concurrent campaigns. (b) **SGLang + EAGLE / BaldEagle speculative decoding** when measured TTFT shortfall on the Supervisor workload exceeds the SLO budget. (c) **Disaggregated prefill / decode (NVIDIA Dynamo or llm-d)** at ≥ 30 sustained concurrent users. |
| Tier 3 — structure prediction | AF3, Boltz-2, RoseTTAFold-AA | Custom containers with FA3, batch queue via NATS, results to data lake. Long-running, not interactive. | — (already batch) |

**Phase-1 operational surface = KServe + vLLM v1 + a custom AF3 batch wrapper.** SGLang, Triton multi-tenant, llm-d, and disaggregation are deferred to Phase 2 / Phase 3 and activated only against the **quantitative triggers** in the table above — not on a calendar date. The earlier draft of this ADR specified all of these as Phase-1 stack components; the architecture critic review correctly flagged that as over-engineering for a single-engineer / ≤ 30-concurrent-user academic-lab system.

**Known-good fallback image.** The Phase-1 vLLM v1 image is paired with a pinned **vLLM v0 fallback image** in the container registry. The runtime cost of carrying the v0 image is zero (it is referenced only when needed); the optionality is real — older Ampere SKUs occasionally underperform on v1, and the v0 fallback removes a cliff-edge risk for the lab's pre-Hopper hardware.

## Rationale

- **TorchServe is the wrong tool for LLMs.** It lacks PagedAttention, continuous batching, and speculative decoding — every 2025-2026 LLM-serving innovation that materially affects throughput and cost.
- **vLLM is the 2025-2026 default.** >1M weekly installs (InferenceOps, Oct 2025); 200–250 contributions/week; Red Hat + IBM together contribute 25 % of all commits; frontier OSS model support includes Qwen3-Next and DeepSeek-V3.2-Exp; KV cache CPU offloading native; supported by all major LLM providers; native AWQ/GPTQ/GGUF quantisation; KServe-compatible. **KServe is now an official CNCF incubating project** (passed TOC vote, October 2025) — this is the load-bearing decision that future-proofs the lab's Kubernetes-native serving stack against vendor lock-in. Companion project **llm-d** (46 K installs in September 2025, up from 24 K in August) provides distributed inference; its cache-aware scheduling reports **57× faster response times and 2× throughput at scale** vs naive load balancing.
- **Lab-budget GPU strategy.** Prioritise Hopper/Blackwell (where vLLM v1 wins decisively on throughput) or modern Ada cards. Older Ampere remains usable, but the platform engineer validates per-workload v1 throughput before committing a model to that hardware. **SGLang** is the dedicated speculative-decoding tier.
- **SGLang complements vLLM for speculative-decoding workflows.** EAGLE/BaldEagle training and benchmarking is documented in the SGLang ecosystem (Frugal GPU, June 2025); reported gains: 50.43 → 106.22 tok/s = 2.06× speedup on Qwen2.5-7B-Instruct on a single RTX 3090.
- **KServe over TorchServe.** Native Kubernetes integration; model-mesh for many-model deployments; serverless inference; modern observability hooks; CNCF stewardship. TorchServe still has the simpler Python model-handler surface but lags on operational features.

## Quantisation policy

- **AWQ 4-bit** (Lin et al., MLSys 2024) is the default for LLM weight quantisation — Marie's benchmark (Kaitchup, March 2025): *"All 4-bit quantization methods yield similar performance, with no clear winner. However, due to optimized inference kernels, AWQ and (AutoRound) GPTQ models are preferable over bitsandbytes and HQQ models."*
- **Concrete capacity gain:** *"Qwen2.5 72B compresses 140 GB → 40 GB at 4-bit without any performance degradation in downstream tasks"* (same source). This is the load-bearing argument for serving a 70B-class orchestrator on a single H100.
- **AutoRound** evaluated per-model; the same study notes *"AutoRound may produce unstable models for generative tasks"* (Qwen2.5 72B 4-bit and 8-bit failed on IFEval) — avoid for generative/agentic workloads until per-model verified.
- **GPTQ** retained for compatibility with pre-2024 checkpoints.
- **GGUF** retained for llama.cpp on Apple Silicon (chemist workstations) only — never for production serving.
- **bitsandbytes** = most user-friendly but inferior inference kernels; OK for dev, suboptimal for prod (same Kaitchup source).
- **FP8** on Hopper, **NVFP4** on Blackwell when available — Phase 3.
- **Lower bit (2-bit, 3-bit)**: avoid for generative tasks (Marie: *"leads to a more significant performance drop, particularly for generative tasks"*).

## Consequences

- **Phase-1 operational footprint is two runbooks** (KServe + vLLM, custom AF3 batch). Triton multi-tenant, SGLang spec-decoding, and disaggregation add runbooks only when their quantitative triggers fire.
- The platform engineer must maintain familiarity with vLLM, KServe, and the custom AF3/Boltz-2 wrappers from Phase 1; SGLang / Triton operational expertise is acquired on demand.
- Cost monitoring becomes per-tier; observability dashboards reflect the split.
- A pinned vLLM v0 image stays in the registry as fallback (zero recurring cost; insurance against Ampere v1 regressions).

## Alternatives considered

- **Single TorchServe everywhere.** Rejected: TorchServe lacks PagedAttention, continuous batching, and speculative decoding — fine for the small GNN classifier in Tier 1, wrong for LLMs in Tier 2.
- **Ray Serve as the universal layer.** Compelling for orchestration of the three tiers under one control plane. Reconsidered in Phase 3 once steady-state load is known.
- **vLLM directly (no KServe / no Triton).** Single-tenant fine; multi-tenant + canary deployment require KServe / Triton.
- **SGLang in place of vLLM.** Better for structured generation (JSON tool-calling) but smaller community; deferred as a Phase 2 evaluation.

## Revisit conditions

- vLLM project momentum changes.
- KServe goes inactive at CNCF.
- A unified inference runtime materially closes the gap to per-tier optimal.
