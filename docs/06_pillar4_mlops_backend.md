# 06 — Pillar 4: MLOps and Backend Infrastructure

**Contents**

- [Goal](#goal)
- [Component 4.1 — Reproducible training and evaluation](#component-41-reproducible-training-and-evaluation)
- [Component 4.2 — Model registry and serving](#component-42-model-registry-and-serving)
- [Component 4.3 — Continuous integration and deployment](#component-43-continuous-integration-and-deployment)
- [Component 4.4 — Observability](#component-44-observability)
- [Component 4.5 — Data engineering](#component-45-data-engineering)
- [Component 4.6 — Security, licensing, and FAIR data](#component-46-security-licensing-and-fair-data)
- [Component 4.7 — Backup, disaster recovery, and audit](#component-47-backup-disaster-recovery-and-audit)
- [Technology choices](#technology-choices)
- [Cost envelope (estimated)](#cost-envelope-estimated)
- [Risks and unknowns](#risks-and-unknowns)
- [Phase deliverables](#phase-deliverables)


## Goal

Take research-grade code (typically a Jupyter-notebook-and-shell-scripts assembly with manually trained checkpoints) and turn it into production infrastructure that supports:

- **Reproducibility:** every figure, every model, every published result must be regeneratable from a tagged commit + dataset version.
- **Reliability:** the public MB Finder service should remain available for thousands of external users.
- **Velocity:** the host lab should be able to retrain and redeploy models in hours, not weeks.
- **Compliance:** FAIR data principles, open-source license hygiene, dataset and code citation.
- **Cost control:** academic budgets are finite; the system must scale to zero when idle.

This pillar is where a researcher with backend / software-development expertise demonstrably amplifies a chemistry-focused team — these are capabilities the typical academic metallodrug discovery group has no full-time owner for.

## Component 4.1 — Reproducible training and evaluation

### Approach
- **MLflow** for experiment tracking, model registry, and artifact storage.
- **DVC** (Data Version Control) for dataset versioning; every training run records a dataset hash.
- **Hydra** for configuration management; every run is fully described by a single YAML.
- **PyTorch Lightning** training pattern, identical across all model types.
- **Continuous evaluation:** every promoted model is re-evaluated on a frozen held-out test set; regressions block deployment.

### Pattern
```
training-run = {
    code commit hash,
    dataset DVC hash,
    Hydra config hash,
    container image digest,
    model checkpoint (MLflow artifact),
    eval report (MLflow artifact),
    citation BibTeX (auto-generated)
}
```
Every artefact in this tuple is content-addressable; combined, they form a falsifiable scientific claim.

## Component 4.2 — Model registry and serving

### Approach
- **Model registry:** MLflow registry, with semantic-versioned model names (e.g. `mkano-plus@2.1.0`).
- **Serving — three workload tiers** (full detail in Component 4.2.1 below). In summary: small classifiers on KServe, LLMs on vLLM behind Triton, structure prediction (AF3 / Boltz-2) on a dedicated batch service.
- **Inference modes:**
  - Real-time single-molecule predictions (web UI → REST API → KServe or vLLM).
  - Batch predictions (queued, asynchronous, results materialised to data lake).
  - Internal microservice calls from the orchestrator (gRPC for latency, MCP for tool exposure).
- **Scaling — per-tier policy.** Different components have different always-on vs scale-to-zero profiles:

  | Component | Policy | Why |
  | --- | --- | --- |
  | Agentic orchestrator (LangGraph process) | **Always-on** (small CPU pod; ≈ $10 / mo) | A DMTA campaign spans weeks; the orchestrator must react to wet-lab events (assay results arriving, ELN updates) at any hour — including overnight. Always-on cost is negligible vs the latency cost of cold-starting the campaign loop. |
  | Tier 1 (small classifiers) and Tier 3 (AF3 / Boltz-2 batch) | **Scale-to-zero** with cold-start mitigated by a warm pool of 1 GPU | Stateless small models and batch workloads cold-start cheaply (sub-30 s). Warm pool absorbs morning rush. |
  | Tier 2 — Llama 3 70B (Supervisor orchestrator) | **Explicit choice: 24×7 OR scale-to-zero with budgeted cold-start.** Default Phase-1 = scale-to-zero with documented cold-start SLO ≤ 180 s. The 24×7 alternative is ≈ $1,500–2,150 / mo (Lambda H100 reserved vs on-demand). | A 70B AWQ-loaded weight loads in 60-180 s on H100; that latency is bounded and acceptable for non-interactive Supervisor decisions. Interactive web-UI chat traffic, if introduced, may require the 24×7 alternative. |
- **Cold-start SLO budget.** Each tier ships with an explicit cold-start budget recorded in the SLO register (`docs/06a_slo_register.md`, Phase 1 deliverable).
- **Model rollout:** canary deployment — 5 % of traffic routed to a new model version while production sees the prior version; automated rollback on metric regression.

### Component 4.2.1 — Inference serving stack and quantisation (the modern serving picture)

A 2026-grade serving plan differentiates three workload classes: small GNN classifiers, LLM inference, and structure prediction. Each has different latency, batching, and GPU-utilisation profiles. A single serving stack would be suboptimal everywhere; the proposal commits to a three-tier design.

**Tier 1 — small classifier (MKANO+ GNN, geometry heads, per-metal heads).** Latency target sub-50 ms. Stack: **KServe** (K8s-native, CNCF-incubating per InferenceOps' *State of Model Serving* Substack, Oct 2025) with a PyTorch runtime. FP16 quantisation; no special acceleration needed.

**Tier 2 — foundation-model and LLM inference (ChemFM-LoRA scorer, Llama 3 / Qwen 2.5 / ChemDFM for the orchestrator).** Latency target 100–500 ms TTFT. Stack:
- **vLLM v1** (Kwon et al., SOSP 2023) with PagedAttention, continuous batching, and prefix caching. >1 M weekly installs (InferenceOps, Oct 2025). Lab-budget GPU strategy prioritises Hopper/Blackwell, or modern Ada cards with workload-by-workload throughput validation; older Ampere cards remain usable but require per-workload v1 throughput verification before commitment. Speculative decoding lives on **SGLang** with **EAGLE / BaldEagle** draft models.
- **Quantisation policy:** **AWQ** 4-bit (Lin et al., MLSys 2024) is the default — *"due to optimized inference kernels, AWQ and (AutoRound) GPTQ models are preferable over bitsandbytes and HQQ models"* (Marie, Mar 2025). Hard data point: Qwen2.5 72B 4-bit AWQ = 140 GB → 40 GB *"without any performance degradation in downstream tasks"* — this is the load-bearing number for serving a 70B-class orchestrator on a single H100.
- **Speculative decoding:** runs on **SGLang** with an **EAGLE** (or BaldEagle) draft model — NOT vLLM. Per Marie (Mar 2025), speculative decoding is not yet supported in vLLM v1. Concrete benchmark (Frugal GPU, June 2025, BaldEagle-Qwen-2.5-7B-Instruct on RTX 3090): **50.43 → 106.22 tok/s = 2.06× speedup**, acceptance length 3.55 (vs 1.00 baseline). Each foundation model in the registry ships with a co-trained EAGLE draft.
- **Attention kernel:** **FlashAttention-3** on Hopper; **FlashAttention-4** (Lambda MLE, Mar 2026: *"redesigned async pipeline with warp specialization… 1613 TFLOPs/s peak forward on Blackwell"*) on Blackwell once available.
- **Serving framework choice:** vLLM directly for single-tenant; **NVIDIA Triton Inference Server with vLLM backend** for multi-tenant production. **SGLang** is the speculative-decoding tier and the alternative when JSON-mode / structured outputs dominate (relevant for the agentic orchestrator's tool-calling traffic).
- **Disaggregated prefill/decode** (compute-bound prefill on one GPU pool, memory-bandwidth-bound decode on another; Neural Maze, April 2026) is the Phase-3 optimisation. Quoting that source on the underlying physics: *"serving a single 512-token request on a 66-billion parameter model generates over a gigabyte of KV cache data. When serving hundreds of requests per second, transferring this data from prefill GPUs to decoding GPUs demands immense network bandwidth — often requiring 90 Gbps or more."* Disaggregation crosses over above ≈30 sustained concurrent users; NVIDIA Dynamo or llm-d are the targets at that scale.
- **Chunked prefill** (smooth TTFT vs TPOT trade) is the intermediate-scale optimisation, enabled by default in vLLM v1 and SGLang.

**Tier 3 — structure prediction (AlphaFold 3, Boltz-2, RoseTTAFold-AA).** Long-running, ≥45 s/job, not interactive. Stack: custom containers with FA3, batch queue via NATS, results written to the data lake. No vLLM (these are diffusion models, not autoregressive LLMs).

**Local-LLM stack for chemist workstations and laptops** (developer-loop, not production):
- **Ollama** for laptop iteration on prompts.
- **MLX-LM** on Apple Silicon (Mac Studio / Mac Pro chemist workstations) — 152 tok/s for 3 B-class models per Simon Willison's Substack.
- **LM Studio** for chemists who prefer GUI.

These run in dev mode only; production traffic always flows through the vLLM / KServe stack above.

**Inference cost tracking.** Each prediction is tagged with `(model_version, quantisation, GPU_type, tokens_in, tokens_out, latency_ms)`; aggregated nightly. Per-prediction marginal cost is observable at the dashboard layer (see Component 4.4 observability extensions).

ADR-008 captures this three-tier decision; ADR-009 captures the quantisation method choices.

## Component 4.3 — Continuous integration and deployment

### Approach
- **Trunk-based development.** Feature branches short-lived; PR-based review.
- **CI pipeline (GitHub Actions):**
  1. Lint (ruff, mypy, eslint).
  2. Unit tests (pytest, vitest).
  3. Schema validation (Pydantic, OpenAPI lint).
  4. Container build + vulnerability scan (Trivy).
  5. Integration tests in ephemeral Kubernetes.
  6. Smoke tests against deployed staging.
  7. Promotion to production gated by chemist UX review for any UI changes.
- **CD pipeline:**
  - GitOps style — production state declared in a Git repo; ArgoCD reconciles.
  - Database migrations via Alembic; checked in CI.
  - Model promotions go through MLflow registry stages: `staging → production`, with manual approval.

## Component 4.4 — Observability

### Approach
- **Metrics:** Prometheus + Grafana. Dashboards for inference latency (p50/p95/p99), model error rate, data-ingestion throughput, training job durations.
- **Logging:** Loki (or self-hosted ELK), structured JSON logs with `trace_id`, `model_version`, `user_id`.
- **Tracing:** OpenTelemetry across services; visualised in Tempo / Jaeger.
- **Alerting:** PagerDuty-style on-call rotation for production-facing failures; lower-priority alerts route to a lab Slack channel.

### What is observed
| Domain | Metric | Threshold / action |
|---|---|---|
| Inference | p95 single-molecule latency | < 2 s; alert on > 5 s |
| Inference | Error rate | < 1 %; alert on > 5 % |
| Data drift | KS test on incoming SMILES feature distribution vs training distribution | alert on p < 0.01 |
| Training | Job success rate | > 90 %; alert if 3 consecutive failures |
| Storage | Object store growth rate | informational |
| Cost | Monthly cloud spend | alert on > 110 % budget |

## Component 4.5 — Data engineering

### Approach
- **Ingestion pipelines (Airflow / Prefect):**
  - Nightly pull from public databases (ChEMBL, PubChem, DrugBank delta).
  - Weekly literature scrape (using lab's existing manual workflow plus AI assistance for OCR of structural figures).
  - Real-time updates from host-lab internal experiments (via ELN webhooks).
- **Storage tiers:**
  - **Bronze** — raw ingested data, immutable.
  - **Silver** — sanitized, deduplicated, schema-conformed.
  - **Gold** — feature-engineered, train/val/test split, registered in feature store.
- **Schema enforcement:** all transitions enforce Pydantic schemas + Great Expectations data-quality rules. Bad data is quarantined, not silently dropped.

## Component 4.6 — Security, licensing, and FAIR data

### Approach
- **Secrets:** managed via HashiCorp Vault or cloud KMS; no secrets in code or CI logs.
- **Authentication:** OAuth 2.0 (institutional SSO) for host-lab members; API-key-based access for external researchers; rate-limited.
- **Licensing hygiene:**
  - All model weights labelled with their training-data license.
  - Foundation-model fine-tunes carry the upstream license.
  - The lab's own data is published CC-BY-4.0 by default (matching the source paper's preprint license).
- **FAIR data principles:**
  - **Findable:** every compound, dataset, and model has a persistent DOI / identifier.
  - **Accessible:** REST + GraphQL public APIs; UI-accessible search.
  - **Interoperable:** community ontologies (Cellosaurus, ChEBI, UniProt, MeSH).
  - **Reusable:** machine-readable licenses, provenance metadata, dataset cards.

## Component 4.7 — Backup, disaster recovery, and audit

### Approach
- **PostgreSQL:** continuous WAL backup to S3 / equivalent; point-in-time recovery up to 7 days.
- **Object store:** versioned + cross-region replication for the data lake.
- **MLflow artifact backup:** nightly snapshot to a separate region.
- **Audit log:** all chemist-facing actions (compound nominations, synthesis approvals, model promotions) are recorded in an immutable append-only log.

## Technology choices

| Layer | Choice | Reason |
|---|---|---|
| Container orchestration | Kubernetes (or Nomad for smaller scope) | Industry standard; supports GPU scheduling. |
| CI/CD | GitHub Actions + ArgoCD | Matches typical academic-group GitHub presence. |
| Experiment tracking | MLflow | De facto open standard; supports the model-registry pattern. |
| Data versioning | DVC | Git-friendly; preserves academic workflow. |
| Workflow scheduling | Prefect (preferred) or Airflow | Modern, Python-native, lower operational burden. |
| Observability | Prometheus + Grafana + Loki + Tempo | Self-hostable; cloud-portable. |
| Secrets | HashiCorp Vault or cloud KMS | Standard. |
| Object store | S3 / Cloud Storage / MinIO | Same API across clouds and self-hosted. |
| Database | PostgreSQL + RDKit cartridge + pgvector | Same as MKANO blueprint; battle-tested. |
| Cache + queue | Redis + NATS (or Kafka) | Standard. |
| Backend framework | FastAPI (Python) | Aligns with the team's Python skill set; auto-OpenAPI. |
| Frontend | Next.js + RDKit-JS + 3Dmol.js | Industry standard; chemistry-aware libraries available. |

## Cost envelope (estimated)

Three scenarios. A host institution may absorb some infrastructure internally (institutional HPC, on-prem GPU allocation); the numbers below are external-cloud-rental baselines for transparency. All in US $; figures rounded to the nearest US $100.

### Steady-state operating cost (no active DMTA campaign)

| Item | Cloud-rental | Self-hosted on lab GPUs (3-yr amortised) | Notes |
|---|---|---|---|
| K8s control plane (managed) | 200 | 0 (lab K8s on existing hardware) | |
| Small-model inference (Tier 1, MKANO+) | 300 | 50 | Auto-scales to zero overnight |
| LLM inference (Tier 2, 1×H100 24×7 AWQ Llama 3 70B) | 1,800 | 1,000 | Lambda Labs ≈ $1.50/hr |
| Structure prediction (Tier 3, AF3/Boltz-2, on-demand) | 400 | 200 | Spot capacity, batch jobs |
| PostgreSQL managed | 300 | 50 | RDS or equivalent |
| Object storage (10 TB) | 200 | 50 | S3 / MinIO local |
| Observability stack | 150 | 50 | Self-hostable |
| Frontier LLM API tokens (low-sensitivity workflows) | 200 | 200 | Routine code generation, lit search |
| **Steady-state subtotal** | **≈ 3,550** | **≈ 1,600** | |

### Active-campaign cost (one DMTA campaign in flight)

| Additional item | Cloud-rental | Self-hosted | Notes |
|---|---|---|---|
| AF3 inference (per scaffold × target screen) | 1,500–4,000 | 800 | 427 scaffolds × 3 targets at ≈$2 / pose |
| Equivariant-diffusion training (Phase 3 only) | 3,000–6,000 | 1,500 | 1–2 weeks on H100, intermittent |
| Orchestrator LLM tokens (heavy use) | 1,500–3,500 | 0 (covered by self-host) | Claude 4 Opus ≈ $15/$75 per M tokens |
| **Active-campaign add-on** | **≈ 6,000–13,500** | **≈ 2,300** | Per simultaneous campaign |

### Annual total

- **Cloud-rental, baseline + 6 campaigns/year:** ≈ US $80–110 K.
- **Self-hosted on lab GPUs (assumes 1×H100 + 2×A100 capex amortised over 3 years at ≈ US $20 K/year):** ≈ US $40–55 K including capex amortisation.

The self-hosted scenario is competitive once the host lab runs more than ≈4 campaigns/year *or* the orchestrator's token volume crosses ≈25M tokens/month — both of which are reached during Phase 2 of the roadmap. The crossover argument is the load-bearing rationale for Pillar 3's data-sovereignty Component 3.2.1.

This budget is dominated by GPU time. Compared to a stalled wet-lab campaign — synthesis chemist salaries plus reagent costs plus equipment time on an MTT plate-reader queue — the platform is inexpensive.

### On-prem hardware sketch (Phase 1–2 acquisition option)

Three concrete hardware options sized to a typical academic-lab budget:

| Option | Hardware | Capex (US $) | Best for |
|---|---|---|---|
| Workstation | 4× NVIDIA L40S in a single ProLiant workstation | ≈ 80 K | Phase 1: MKANO+ training, single-tenant inference, LLM dev |
| Server | 8× RTX 6000 Ada in a 2U server | ≈ 100 K | Phase 2: multi-tenant inference + structure prediction batch |
| Lab DGX | NVIDIA DGX H100 (8×H100) | ≈ 300 K | Phase 3: equivariant-diffusion training + multi-campaign DMTA in parallel |

The L40S workstation is the recommended Phase 1 acquisition — it delivers ChemFM-LoRA fine-tuning, AWQ-quantised Llama 3 70B serving, and AF3 inference on a single budget line item.

## Risks and unknowns

- **Operational burden.** A modern MLOps stack is non-trivial to maintain. Mitigation: the researcher owning this pillar is the dedicated platform engineer; the stack is built to be operated by a single person.
- **Vendor lock-in vs cost.** Managed services are convenient but expensive. Mitigation: design abstractions to be portable; revisit annually.
- **Talent retention.** Loss of the platform engineer leaves the stack unmaintained. Mitigation: rigorous documentation (every ADR captured); training of one or two team members as secondary operators.

## Phase deliverables

| Phase | Deliverable |
|---|---|
| Phase 1 (months 0–6) | Kubernetes cluster + CI/CD pipeline + MLflow + DVC operational. MB Finder v2 alpha deployed. |
| Phase 2 (months 6–12) | Full observability stack; data ingestion pipelines automated; backup + DR tested. |
| Phase 3 (months 12–18) | FAIR-data certification; public API SDKs; cost optimisation review; ADR catalogue published. |
