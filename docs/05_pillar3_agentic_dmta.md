# 05 — Pillar 3: Agentic DMTA Orchestration

**Contents**

- [Goal](#goal)
- [Component 3.1 — Agent role model](#component-31-agent-role-model)
- [Component 3.2 — Orchestration architecture](#component-32-orchestration-architecture)
- [Component 3.3 — Example campaign walkthrough](#component-33-example-campaign-walkthrough)
- [Component 3.4 — Tool surface contracts](#component-34-tool-surface-contracts)
- [Component 3.5 — Integration with existing lab tools](#component-35-integration-with-existing-lab-tools)
- [Why this architecture, not full autonomy](#why-this-architecture-not-full-autonomy)
- [Technology choices](#technology-choices)
- [Risks and unknowns](#risks-and-unknowns)
- [Phase deliverables](#phase-deliverables)


## Goal

Compress the Design–Make–Test–Analyze cycle from months to weeks by introducing an LLM-supervised multi-agent orchestrator that schedules computational and wet-lab tasks, calls the system's prediction services, and surfaces decisions to chemists for approval. Crucially, the agent does **not** generate scientific data autonomously — it coordinates, schedules, and synthesises results. The chemist remains the final approver of every wet-lab step.

This pillar maps onto a documented field paradigm shift. In 2025–2026, agentic systems (ChemCrow, AstraZeneca's ChatInvent, Amazon Bio Discovery, Tippy) have moved from research curiosity to operational tooling. The proposal adopts the same paradigm but specialises it to the existing metallodrug-discovery workflow stages.

## Component 3.1 — Agent role model

The DMTA loop is decomposed into a Supervisor plus five specialist agents (six roles total), each with a constrained tool surface. The decomposition follows the Tippy framework (Supervisor / Molecule / Lab / Analysis / Report) but is tuned to a metallodrug discovery context.

| Agent | Role | Tool surface |
|---|---|---|
| **Supervisor** | Plans the overall DMTA campaign for a target / cell-line objective; arbitrates between agents; tracks budget and time. | All other agents; project-state read/write; calendar; budget service. |
| **Design** | Nominates candidate compounds for a given objective. | Inference API (MKANO+, target-conditioned scorer, generative diffusion); knowledge graph; chemoinformatic core. |
| **Synthesis** | Plans synthetic routes and tracks wet-lab execution. | Retrosynthesis API (open-source AiZynthFinder + IBM RXN); ELN integration; chemist task queue. |
| **Assay** | Plans in-vitro / in-vivo experiments; schedules cell-line orders; computes statistical power. | LIMS integration; assay protocol library; statistical service. |
| **Analysis** | Runs MoA inference + result interpretation; flags anomalies. | Multi-omics MoA service (Pillar 2); knowledge graph; data lake. |
| **Report** | Generates draft figures, tables, and a draft manuscript section. | Reporting service; ELN integration. |

### Safety boundary

Every agent operates under a "human-in-the-loop" constraint:
- Wet-lab steps require explicit chemist sign-off via the web UI.
- Compound nominations exceeding a configurable risk threshold (e.g. unusual oxidation state, high predicted hepatotoxicity) require a senior reviewer.
- The Supervisor's plan is presented as a Gantt-style draft for approval before execution.

This is *cooperative agency*, not autonomy. The system accelerates the chemist; it does not replace them.

### Component 3.1.1 — Why a Supervisor + 5 specialists: the OriGene precedent (Zhang et al., bioRxiv 2025)

The decomposition into a **Supervisor agent plus five specialist agents** (six roles in total) is a deliberate refinement of OriGene's five-role design — the closest published precedent for an LLM-multi-agent system that produced wet-lab-validated cancer targets in 2025. OriGene runs five roles (Coordinator / Planning / Reasoning / Critic / Reporting); MB Finder v2 splits OriGene's *Planning* role into Synthesis and Assay because metallodrug chemistry has *two qualitatively different* planning surfaces (synthetic-route planning vs in-vitro / in-vivo experimental planning). The resulting six roles — Supervisor (= OriGene's Coordinator) + Design (= Reasoning) + Synthesis + Assay (= split Planning) + Analysis (= Critic) + Report (= Reporting) — are a strict superset of OriGene's pattern.

Per Decoding Bio's *BioByte 120* (June 2025):

> *"Under the hood, five agents — Coordinator, Planning, Reasoning, Critic, and Reporting — pass ideas around in a tight feedback loop that mimics how a real scientist brainstorms, checks, and refines a theory. Each agent can call on 568 specialized databases and analytical tools spanning disease biology, pharmacology, and competitive-landscape intel, all exposed through the OriGeneHub API."*

OriGene's empirical results (Zhang et al., *bioRxiv*, June 2025) — directly relevant to MB Finder v2's six-role design (a refinement of OriGene's five roles):

| Result | Detail |
|---|---|
| LitQA accuracy scaling | 62.81 % at 1× iteration budget → 78.39 % at 9× — *more agent iterations improves accuracy quantitatively* |
| TRQA-lit multiple choice | 60.1 % accuracy, **comfortably ahead of human experts using Google** and ahead of GPT-4o-search or TxAgent |
| TRQA-lit short answer | 82.8 % recall |
| TRQA-db | 72.1 % recall |
| HCC case study | 125 candidates → converged on **GPR160**; up-regulation in tumor datasets; inverse link to recurrence-free survival (p = 0.0057); designed gene-knockdown + cytokine + immune-context coculture assays; small molecule inhibitor validated in patient-derived organoids and tumor fragments |
| CRC case study | Nominated **ARG2**; dose-dependent kill curve with IC₅₀ = 3.09 µM in HCT116 cells; viability drops across four patient-derived organoids |

**The mapping is near-identical**, with role names adapted to the chemistry context:

| OriGene role | MB Finder v2 equivalent | Why |
|---|---|---|
| Coordinator | Supervisor | Plans, arbitrates, tracks budget |
| Planning | Synthesis + Assay (split by domain) | Sequences the next set of experiments |
| Reasoning | Design | Nominates candidates from prior evidence |
| Critic | Analysis (evaluator side) | Checks results against hypothesis |
| Reporting | Report | Writes the campaign summary / manuscript draft |

OriGene is the strongest single peer-reviewed-ish precedent for the proposal's agent architecture — a multi-role feedback loop, wet-lab validated, in biology, with measurable scaling laws on agent iteration count. **A caveat to the analogy:** OriGene operates on target-identification (a biology problem with verifiable text-and-database evidence); MB Finder v2 operates on structure-design (a chemistry problem with verifiable synthesis-and-assay evidence). The architectural primitives transfer; the failure modes and verification surfaces do not. The proposal therefore inherits OriGene's role decomposition and feedback-loop pattern, but specialises the verification rubric (chemoinformatic sanitization, drug-likeness, novelty, retrosynthesis, geometry) to the chemistry context — see the five chemistry verifiers in ADR-009.

## Component 3.2 — Orchestration architecture

```
                +------------------------------------+
                |          Chemist (web UI)          |
                +-----------------+------------------+
                                  | reviews & approves
                                  v
+---------------------------------+-----------------------------------+
|                          Supervisor Agent                            |
|   - LangGraph state machine                                          |
|   - GPT-4 / Claude / Gemini class LLM backbone                        |
|   - Persistent memory in Postgres + vector store                      |
+----+-------------+-------------+-------------+-----------------------+
     |             |             |             |
     v             v             v             v
 +--------+   +--------+   +--------+   +--------+   +--------+
 | Design |   | Synth. |   | Assay  |   | Analy. |   | Report |
 | agent  |   | agent  |   | agent  |   | agent  |   | agent  |
 +---+----+   +---+----+   +---+----+   +---+----+   +---+----+
     |            |            |            |            |
     v            v            v            v            v
 +----------------------------------------------------------------+
 |                       Tool surface (services)                   |
 |  inference-api | chemoinformatic-core | KG | LIMS | ELN | ...   |
 +----------------------------------------------------------------+
```

### State management
- Each campaign is a versioned state object: `{objective, candidates, syntheses, assays, results, decisions, log}`.
- State is checkpointed after every agent action to enable replay, audit, and rollback.
- Long-running campaigns (multi-week wet-lab work) resume from checkpoints across agent restarts.

### Context engineering (Nate, *Long-Running AI Agents*, Dec 2025) — keeping the desk clear

A multi-week metallodrug campaign generates thousands of tool calls, dozens of synthesis attempts, RNA-seq + proteomic datasets, and a growing body of chemist decisions. The naive approach — append everything to the context window — fails systematically. Quoting Nate's synthesis of Google ADK + Stanford/SambaNova ACE + Manus's four-redesign lessons:

> *"The problem isn't that agents can't hold enough information. The problem is that every token you add to the context window competes for the model's attention. Stuff a hundred thousand tokens of history into the window and the model's ability to reason about what actually matters degrades. The critical constraint from step three gets buried under the noise from steps four through forty."*

The phenomenon has a name: **context rot**. Bigger context windows make it worse, not better. Multi-week DMTA campaigns are exactly the regime where this matters — a campaign spans weeks; the Supervisor agent makes thousands of decisions; longer-context Claude / GPT models do not solve the problem.

**The four-layer memory model adopted from Nate's synthesis:**

| Layer | What it holds | Where it lives | Refresh policy |
|---|---|---|---|
| **Working context** | The current step's inputs, outputs, immediate reasoning | LLM context window (kept ≤ ~30 KB) | Compiled fresh each step |
| **Sessions** | The current campaign's recent decisions, last 5-10 agent turns | Redis (per-campaign) | Sliding window |
| **Memory** | The campaign's full audit log + intermediate results | PostgreSQL `campaigns` table (with retrieval) | Append-only; queried on demand |
| **Artifacts** | RNA-seq matrices, assay plate-reader outputs, MoA dossiers, manuscript drafts | Object store (S3/MinIO) | Reference by URI, never inlined |

**The architectural rule (Manus-style):** the agent does not "see" everything that has happened; at each step the Supervisor *compiles a view* containing only what is relevant for the current decision — campaign objective, last 2-3 actions, the specific assay result that triggered the current step, and any cached retrievals.

**Practical consequence for the design.** The Supervisor's working context is bounded at ≈30 KB. Larger artefacts (RNA-seq counts, full proteomic tables, 100-page literature blocks) are *referenced* (URIs), not inlined. When a candidate's COL3A1-binding score is needed, the agent retrieves it from the artifact store as a single number, not as a 50,000-line raw proteomic export. This is the same principle MCP code-execution exploits (Component 3.4.1) — keep the model's attention on decisions, push the data into the execution environment.

**Why this matters for grant reviewers.** A reviewer who has tracked the 2025 agent literature will know that the gap between "demo that works for 10 minutes" and "production agent that survives a 6-week campaign" is exactly this context-engineering work. The proposal commits to it explicitly.

### LLM choice
- Default backbone: Claude 4 Opus or GPT-4-class model via API for low-volume, low-sensitivity workflows.
- **Self-hosted local LLMs** for privacy-sensitive, high-volume, or domain-fine-tuned workflows: Llama 3.x 70B or Qwen 2.5 72B, AWQ-quantised to 4-bit (≈40 GB on a single H100), served on **vLLM** with PagedAttention + continuous batching. For chemistry-fine-tuned variants, ChemDFM-13B or a QLoRA+DoRA fine-tune of Llama 3 8B on the host lab's chemistry corpus, served identically.
- Model is swappable per agent — Design might use a chemistry-specialised model (ChemDFM), while Synthesis can use a code-tuned model for retrosynthesis script generation.

### Component 3.2.1 — When to self-host: data sovereignty and the academic threat model

The "API by default, local fallback for privacy-sensitive" sentence above is short because the *decision* is not contentious. The *reasons* it must be made deliberately, however, are specific to academic chemistry labs working with pre-publication data under regional data-protection regulations and deserve explicit treatment.

**Threat model.** Four data classes carry materially different sensitivity:

| Data class | Sensitivity | Default destination | Required mitigation |
|---|---|---|---|
| Public literature, public DB content (ChEMBL, PubChem, CSD) | Low | Frontier API ok | Standard rate limiting |
| Routine lab code, analysis scripts | Low | Frontier API ok | Strip credentials |
| Pre-publication compound structures, novel scaffolds from de novo design | High | **Self-host required** | No API egress; structures stay in lab |
| Patient-derived or clinical-collaborator data; un-anonymised omics | Very high | **Never leaves lab network** | Self-host + on-prem GPU + audit log |

**Why this matters under regional data-protection law.** Under regional data-protection regulations (e.g. HKSAR PDPO, EU GDPR) and most institutional research-ethics frameworks, cross-border transfer of patient-derived data to US-hosted commercial APIs (OpenAI, Anthropic) is at minimum a process burden, and for some collaborator data classes is contractually forbidden. The pre-publication confidentiality posture of de novo scaffolds is also concrete: sending a novel Au(III) candidate to a frontier API before patent submission risks prior-art exposure. A self-hosted stack eliminates both concerns.

**Why this matters scientifically.** Self-hosting is the *only* way to deploy domain-fine-tuned checkpoints — ChemDFM, a chemistry-DAPT-tuned Llama, or a QLoRA-DoRA ChemFM specialised on a 17,732 IC50 corpus. Such checkpoints simply do not exist behind frontier APIs.

**Concrete self-hosted serving stack** (Pillar 4 implements; see Component 4.2.1):
- **Llama 3.x 70B AWQ** on **vLLM** v1, single H100 (≈80 GB VRAM headroom for 4-bit + KV cache), 100–500 ms TTFT, continuous batching.
- **Qwen 2.5 32B AWQ** on a single A100-80 for the Design agent's routine generation.
- **ChemDFM-13B or a chemistry-DAPT Llama 3 8B** on an L40S for the Analysis agent.
- **EAGLE speculative decoding** draft model (≈2× decode speedup per Frugal GPU, June 2025) shipped alongside each base model in the MLflow registry.
- **MLX-LM on lab Macs** for offline / per-chemist literature triage on confidential structures (Apple Silicon at 152 tok/s for 3B-class models; Simon Willison, Feb 2025).
- **Ollama on chemist workstations** as a developer-loop convenience for prompt exploration; not for production traffic (vLLM vs Ollama distinction per Kaitchup, July 2025).

**Cost crossover.** Per the cost envelope in Pillar 4, 1×H100 24×7 amortised at academic cloud rates (Lambda Labs ≈ US $1,500–1,800/mo, or fully on-prem amortised over 3 years at ≈US $1,000/mo equivalent) breaks even against frontier-API spend around ≈25M–50M tokens/month sustained. A DMTA campaign with the agent decomposition described below routinely exceeds that — the platform hits this crossover within Phase 2.

## Component 3.3 — Example campaign walkthrough

A worked example illustrates the loop in action.

**Objective entered by chemist:**
> *"Find an Au(III) candidate active against A2780cis with predicted COL3A1 engagement and synthesis route under 6 steps."*

**Supervisor plan (Gantt draft, approved by chemist):**
1. Design agent generates 20 candidate Au(III) complexes (diffusion + fragment-assembly hybrid).
2. Design agent ranks them by target-conditioned MKANO+ score.
3. Synthesis agent produces retrosynthetic routes for top 5.
4. Chemist reviews and selects top 2 for synthesis.
5. Synthesis agent registers ELN tasks; tracks completion.
6. Assay agent schedules MTT assay on A2780cis + A2780; calculates statistical power.
7. Analysis agent processes assay results; flags discrepancies with prediction.
8. If any hit, MoA inference is launched on lab RNA-seq + proteomics output.
9. Report agent drafts results section for the host lab's internal weekly meeting.

**Loop closure.** Analysis agent's output feeds the Design agent for the next iteration. The Supervisor decides convergence ("active hit confirmed in resistance line") or escalation ("3 failed rounds — escalate to PI").

## Component 3.4 — Tool surface contracts

Every agent invokes tools through a normalised contract that ensures safe, auditable behaviour:

```python
class Tool(Protocol):
    name: str
    description: str           # what the agent sees
    input_schema: pydantic.BaseModel
    output_schema: pydantic.BaseModel
    risk_level: Literal["safe", "moderate", "dangerous"]
    requires_human_approval: bool

    def call(self, request: BaseModel) -> BaseModel: ...
    def explain(self, request: BaseModel) -> str: ...   # human-readable justification

    def audit(self) -> AuditRecord: ...                  # what was called, when, by whom
```

The `risk_level` and `requires_human_approval` flags are enforced by the Supervisor; agents cannot bypass them.

### Component 3.4.1 — Tool surface as Model Context Protocol (MCP) servers

The Python `Tool` protocol above is the *internal* contract. The *external* contract — how the orchestrator's tools are exposed to LLMs and to other AI clients — is the **Model Context Protocol (MCP)**, Anthropic's 2024 open specification now adopted across the industry. Per Anthropic's own engineering blog (December 2025): *"Since launching MCP in November 2024, adoption has been rapid: the community has built thousands of MCP servers, SDKs are available for all major programming languages, and the industry has adopted MCP as the de-facto standard for connecting agents to tools and data."*

**Why MCP and not a bespoke protocol.** Exposing the platform's chemistry tools (chemoinformatic-core sanitization, inference-api prediction, retrosynthesis, ELN, KG query) as MCP servers means:
- Any MCP client — Claude Desktop, ChatGPT's tool-use, Cursor, future lab-member AI assistants — can use the platform's chemistry tools without bespoke integration.
- The LangGraph orchestrator becomes *one of many* possible MCP clients, not the sole consumer. This eliminates LangGraph as a single point of risk.
- Tool definitions are reusable across labs — the host lab could publish a chemoinformatic-core MCP server and other metallodrug labs adopt it directly.

**Code execution with MCP — the load-bearing 2025-2026 efficiency pattern.** Anthropic's December 2025 engineering post *Code execution with MCP* documents a paradigm shift: rather than the LLM calling tools one-at-a-time (each call passing through the model's context), the agent **writes code** that calls MCP-exposed tools as if they were a TypeScript SDK on a filesystem. Servers and tools are exposed as a file tree (`./servers/chemoinformatic/sanitize.ts`, `./servers/inference/predict.ts`, `./servers/eln/createEntry.ts`); the agent reads only the tools it needs, executes a single code block that orchestrates many calls, and only logs intermediate results that matter.

The benchmark Anthropic reports is striking: *"This reduces the token usage from 150,000 tokens to 2,000 tokens — a time and cost saving of 98.7 %."* Cloudflare independently confirmed the same pattern, calling it "Code Mode."

Specifically for fragment-assembly screening, this is the right pattern: the 427 de novo scaffolds × 4 cell lines × 3 protein targets = 5,124 inference calls collapse into a *single* code block written by the Design agent, executed in a sandbox, with only the final ranked list returned to the model. Without code execution, the same workflow would burn the orchestrator's token budget on intermediate predictions.

**Implementation.** Each service in Pillar 4 (`chemoinformatic-core`, `inference-api`, `agentic-orchestrator`'s tool subset) ships an `mcp-server` mode alongside the standard REST API. The Design and Analysis agents (Component 3.4.2) operate in code-execution mode by default; the Supervisor falls back to direct tool-call mode for short workflows where the code-execution overhead is unjustified. ADR-007 captures this decision.

### Component 3.4.1a — Three agent architectures (and why we chose this one)

Cobus Greyling's January 2026 synthesis of Anthropic's *Building Effective Agents* (December 2024) identifies three architectural patterns now in production:

1. **Monolithic single agent** — central LLM + tools. Excels at prototyping, falters under tool overload.
2. **Multi-agent workflows** — specialised agents in a workflow graph (LangGraph-style). Supports parallelism, cost control, predictability. The lab's chosen pattern.
3. **Skills / modular capabilities** — Anthropic's 2025 recommendation. Skills are markdown procedures + optional executables loaded on-demand; reduce tool bloat and replace many multi-agent designs.

This proposal commits to architecture #2 with explicit forward compatibility to #3:
- The six-role decomposition (Supervisor + Design + Synthesis + Assay + Analysis + Report) is a workflow graph.
- Each agent's domain knowledge — e.g. "how to plan a retrosynthesis for a Pt(II) NHC complex" — is packaged as a **Skill** (markdown procedure file) that the agent loads on demand. The Design agent does not have route-planning baked into its prompt; it discovers the `pt-retrosynthesis` Skill and loads it.
- This means as the field moves further toward architecture #3 (which Anthropic openly advocates), the host lab's investment in skill curation transfers cleanly. The LangGraph state machine remains; the skill registry becomes the durable scientific artefact.

The architecture trichotomy also clarifies the cost picture: heavy multi-agent designs (architecture #2 by itself) carry significant LLM overhead; the proposal's hybrid #2+#3 design is the lower-cost shape Anthropic itself now recommends for production scientific workflows.

### Component 3.4.1c — Concrete primitive mapping (isolation spectrum)

Beyond the architecture trichotomy (3.4.1a) and the pattern mapping (3.4.1b below), the proposal commits to a concrete primitive decomposition borrowed from the Claude Code primitive model (BoringBot, *Claude Code: Skills, Subagents, Hooks, Plugins, and Harnesses*, May 2026). That model identifies six distinct primitives on an *isolation spectrum*:

```
Skills ──────────── Subagents ──────────── Agent Teams
(Same Context)    (Isolated Context)    (Separate Process)
  Low cost              ↕                  High isolation
  Fast                  ↕                  Parallelism
```

The lab's system maps to these primitives as follows:

| Primitive | What it is | Concrete instance in MB Finder v2 |
|---|---|---|
| **Harness** | The runtime around the orchestrator | The `agentic-orchestrator` microservice itself (LangGraph + Postgres state + Redis cache + audit log) |
| **Main agent** | The reasoning loop inside the harness | The Supervisor agent |
| **Subagents** | Isolated workers; their context never pollutes the main session | The 5 specialised agents (Design, Synthesis, Assay, Analysis, Report) — each gets its own context window and returns only a structured summary |
| **Skills** | In-context, on-demand procedures (markdown + optional code) | `pt-retrosynthesis.SKILL.md`, `mtt-protocol.SKILL.md`, `cetsa-analysis.SKILL.md`, `kegg-enrichment.SKILL.md` — packaged scientific procedures the host lab already executes by hand. Loaded by agents when judged relevant. |
| **Plugins** | Extend what any agent can *touch* (tool surface) | MCP servers for chemoinformatic-core, inference-api, retrosynthesis, ELN, LIMS, knowledge graph |
| **Hooks** | Deterministic control points at lifecycle events | Pre-tool-call sanitization (chemoinformatic-core validates any compound before downstream use); post-experiment chemist sign-off gate (any wet-lab action requires explicit approval); pre-synthesis novelty/IP check |

Quoting the source on why the wrong primitive choice is the dominant failure mode:
> *"Most developers hit a wall somewhere around their third or fourth Claude Code workflow… The root cause is almost always the same: practitioners are using the right tools in the wrong layer. A behavioral constraint that should be a hook gets written into a system prompt. A reusable workflow that should be a skill gets copied and pasted into every conversation."*

For an academic metallodrug discovery group specifically, the highest-leverage primitive is **Skills**. Tacit knowledge — "how this lab synthesises a Pt(II) bis-NHC complex," "how this lab runs an MTT assay on A2780cis with the local cell-culture protocol," "how this lab interprets a CETSA shift" — is currently in PhD-student-and-postdoc heads. Codifying each as a SKILL.md file makes the procedure (a) reusable across campaigns, (b) version-controlled with the rest of the codebase, (c) loadable on-demand by any of the 5 specialised agents, and (d) — critically — durable when staff turn over. Manuscript-grade reproducibility requires this artefact category; the proposal makes it explicit. ADR-007 (MCP) and ADR-011 (Skill curation) capture the operational details.

### Component 3.4.1d — Working reference implementations (Anthropic Cookbook)

Anthropic publishes working notebook implementations of the six patterns the proposal maps onto, at `github.com/anthropics/anthropic-cookbook` (path: `patterns/agents/`):

| Notebook | Implements | MB Finder v2 agent that uses it |
|---|---|---|
| `basic_workflows.ipynb` | Prompt chaining, routing, parallelization (sectioning + voting) | Synthesis (chaining), Assay (routing), Design (parallelization for diverse candidate generation) |
| `orchestrator_workers.ipynb` | Central LLM delegates to specialised workers, synthesises results | **Supervisor** — this is the direct reference implementation for the proposal's Supervisor agent |
| `evaluator_optimizer.ipynb` | One LLM generates, another evaluates, loop until convergence | **Analysis** — this is the direct reference for the MoA-hypothesis-and-evaluation loop |

The Pillar 3 implementation begins by *forking these notebooks and specialising them*, not by re-implementing the patterns from scratch. The Supervisor agent's first prompt template is `orchestrator_workers.ipynb`'s orchestrator prompt with the worker list swapped to the chemistry-specialised agents; the Analysis agent's loop is `evaluator_optimizer.ipynb` with the evaluator's evaluation criteria swapped for the proposal's MoA-fitness rubric.

This converts Pillar 3 from "novel multi-agent architecture" into "validated Anthropic patterns specialised to metallodrug discovery" — a much smaller credibility ask of the reviewer.

### Component 3.4.1b — Mapping our 6 roles to Anthropic's 6 patterns

The six chemistry roles map cleanly to Anthropic's six canonical patterns (*Building Effective Agents*, Dec 2024). The mapping is not cosmetic — each pattern carries different cost, latency, and observability implications:

| Agent | Anthropic pattern | Why |
|---|---|---|
| Supervisor | **Orchestrator-workers** | Dynamically breaks down campaign objective into subtasks delegated to the four specialised agents; synthesises results. |
| Design | **Augmented LLM + Routing** | LLM with retrieval (KG, literature, MCP-exposed inference) routed by chemistry sub-domain (Pt, Au, Cu). |
| Synthesis | **Prompt chaining** | Decomposes "synthesise this candidate" into fixed substeps: retrosynthesis → route validation → ELN task creation. |
| Assay | **Routing** | Routes by assay type (MTT vs CETSA vs in vivo) to specialised protocol planners. |
| Analysis | **Evaluator-optimizer** | One LLM call generates the MoA hypothesis; another evaluates it against the multi-omics data, iterating until convergence. |
| Report | **Prompt chaining** | Outline → figure draft → manuscript section, with chemist gate at each step. |

Three of these patterns (orchestrator-workers, evaluator-optimizer, augmented-LLM) are the patterns Anthropic itself most strongly recommends; routing and prompt chaining are the simplest stable patterns. The proposal *deliberately avoids* the parallelization pattern (multiple agents on the same subtask with voting) — the wet-lab nature of metallodrug discovery does not reward Monte-Carlo-style redundant nominations.

### Component 3.4.2 — DSPy for the Design and Analysis agents

LangGraph (the state machine) and MCP (the tool wire format) together do not solve a third problem: making agent *prompts* measurable and optimisable. **DSPy** (Stanford; ICLR 2024) is the practitioner answer. Rather than hand-tuning prompts, DSPy programs declare modular pipelines (signatures, modules) and use *teleprompters* (MIPRO, BootstrapFewShot, COPRO) to compile them against a held-out evaluation set.

For this proposal, two agents are good DSPy candidates because their outputs are measurable:
- **Design agent.** Eval set: the 19 PlatinAI-era complexes from the source paper. Metric: top-5 ranking includes the experimentally active complexes. DSPy compiles the Design-agent prompt against this set; the Supervisor swaps in the optimised prompt automatically.
- **Analysis agent.** Eval set: the 50 DEG–DEP pairs from the PlatinAI MoA study. Metric: top-5 protein targets include COL3A1 and BUB1B.

The Synthesis, Assay, and Report agents are less directly measurable and remain plain LangGraph nodes for now. Anthropic's *Building Effective Agents* (Dec 2024) and the patterns-distillation pieces by Patrick McGuinness (2025) provide the framework for choosing.

## Component 3.5 — Integration with existing lab tools

The agentic layer is meaningful only if it integrates with existing workflow surfaces:

- **ELN.** Read/write integration with Benchling or LabArchives (whichever the host institution licenses). Synthesis tasks appear as ELN entries with auto-populated structural data.
- **LIMS.** Read sample inventory; write assay schedules. Where no formal LIMS is in place, the system exposes a lightweight LIMS-equivalent built on PostgreSQL + the web UI.
- **Calendar.** Integrate with lab calendars (Google Workspace) to respect personnel availability.
- **Instrument integration (Phase 3).** Direct integration with HPLC, NMR, plate readers via SiLA 2 / OPC-UA when standardised; otherwise via file-watch + parsing.

## Why this architecture, not full autonomy

The published literature includes more aggressive autonomous-lab paradigms — and a particularly instructive cautionary tale. The proposal stops short of full autonomy for four reasons documented in primary sources:

1. **Academic publication norms.** A wet-lab experiment whose execution decision was made solely by an LLM is currently unpublishable in most peer-reviewed venues. Cooperative agency keeps the chemist in the authorial / decision-making position.
2. **Safety.** Organometallic synthesis involves air-sensitive reagents (Schlenk-line / glove-box-handled organolithium, organozinc, low-oxidation-state transition-metal precursors), radioactive isotopes where radiopharmaceutical work touches them (e.g. Re-188 as a β-emitter for theranostic Re complexes; Tc-99m as a γ-emitter for SPECT imaging), and biohazards in cell culture. Human judgment remains the right safety gate.
3. **The A-Lab cautionary tale.** Berkeley's A-Lab claimed to have synthesised **41 new inorganic compounds from 58 attempted targets in 17 days, a 71 % success rate** (Szymanski et al., *Nature* 624, 86, November 29 2023). Six months later, Palgrave (UCL) and Schoop (Princeton) published an independent re-analysis in *PRX Energy* (March 7 2024) concluding that "the main claim of discovery of new materials is wrong" — the AI had misinterpreted X-ray diffraction patterns, confusing known compounds for new ones due to a failure to account for compositional disorder. Palgrave characterised the diffraction-analysis model's quality as *"very bad, very beginner, completely novice human level"* (per Perera, *The Lab Without Scientists*, Jan 2026). This is the canonical example of what happens when AI autonomy outruns AI understanding in a research setting where ground truth is ambiguous.
4. **The AF3 hallucination evidence.** Even Nobel-tier prediction systems have documented failure modes. Per the same Perera synthesis, independent analysis of 72 DisProt-database proteins (preprint, October 2025) found that **AlphaFold3 hallucinated structured conformations in 22 % of intrinsically disordered proteins**, imposing order where none naturally exists. A **4.4 % chirality violation rate** persists on the PoseBusters benchmark — molecules predicted with the wrong handedness. For metallodrug work where cis/trans isomerism *is* the activity-determining feature, these failure modes are not acceptable without human verification.

**Positive precedents that the proposal explicitly endorses** (these are how cooperative agency *should* look):
- **Coscientist** (Boiko, MacKnight, Kline, Gomes, *Nature* 624, 570, December 20 2023): GPT-4-driven autonomous palladium-catalysed cross-coupling. The AI browsed literature, selected reagents and conditions, wrote control code for liquid handlers, and *human researchers verified by GC-MS*. The verification step is the load-bearing element.
- **ChemCrow** (Bran, Cox, Schilter, Baldassari, White, Schwaller; *Nat. Mach. Intell.* 6, 525, May 8 2024): GPT-4 + 18 expert chemistry tools. Synthesised DEET, three thiourea organocatalysts, and a novel chromophore via IBM RoboRXN. Notable: "ChemCrow outperformed raw GPT-4 on chemical accuracy" — the tool layer is what makes the system credible, not the LLM alone.
- **Rainbow** (NCSU, *Nat. Commun.* August 22 2025): multi-robot perovskite quantum dot optimisation at **1,000 experiments/day**, with the ML component generating *interpretable insights* about which chemical parameters matter rather than opaque predictions.

The proposal's design mirrors these three precedents (human-verified outputs, rich tool surface, interpretable ML decisions) and explicitly avoids the A-Lab failure pattern (autonomous decisions on ambiguous data without human verification).

Full autonomy is an explicit non-goal of this proposal.

### The 5-level autonomy ladder — where MB Finder v2 sits, where it goes

Evans & Desai's *Self-driving labs = infrastructure, not just intelligence* (TechPolitik, February 2026) proposes an autonomy ladder analogous to the SAE driving levels. This proposal commits to specific levels per phase, so reviewers can locate the work on a recognised yardstick:

| Level | Capability | Lab examples | MB Finder v2 commitment |
|---|---|---|---|
| **L0** — Automated execution | Robots run pre-defined scripts; no decisions | OpenTrons, Chemspeed, Tecan, Flow Robotics, North Robotics | Out of scope (most host labs already operate at L0 for routine pipetting, plate reading) |
| **L1** — Closed-loop optimisation | Run experiment → fit model → choose next experiment | Most early SDL papers; the MKANO HTS loop | **The lab is here today.** MKANO + manual chemist judgment closes the loop. |
| **L2** — Constraint-aware planning | Reasons about time, cost, safety, uncertainty, multi-objective trade-offs | Emerald Cloud Lab (200+ instrument types), Strateos (Eli Lilly partner), Arctoris, Culture Biosciences, Intrepid Labs Valiant, Molecule One, Automata | **MB Finder v2 Phase 1-2 target.** Supervisor agent does explicit cost/time/safety reasoning; agents trade off across the five chemistry verifiers (sanitization, drug-likeness, novelty, synthesis-accessibility, geometry validity). |
| **L3** — Model-driven exploration | Better priors from literature + prior experiments + cross-modal reasoning; navigates known search spaces intelligently | Periodic Labs ($300M seed), Lila Sciences ($235M for AI Science Factories), Recursion (65 PB biological data), Edison Scientific, Chemify | **MB Finder v2 Phase 3 target.** Equivariant diffusion (Pillar 1.4) + agentic literature + KG traversal explicitly fits the L3 definition. |
| **L4** — Self-maintenance | Detects drift, runs verification, recalibrates | Nobody at scale (per Evans & Desai) | Out of scope for the 18-month roadmap. Data-drift detection (Pillar 4 Component 4.4) is the L4 stub. |
| **L5** — Portability | Workflows transfer across instruments, sites, operators | The cloud labs partially solve this | Out of scope; flagged as a future opportunity via the open MB Finder v2 platform + Cellosaurus + Skills (ADR-011). |

L0-L3 describe what the system can *do*; L4-L5 describe *infrastructure maturity that doesn't add new capabilities but determines whether the lower levels work reliably at scale*. The proposal is honest about which levels it commits to and which it does not.

**Industry context (Evans & Desai, Feb 2026):**
- NIST is writing standards for the modular autonomous laboratory ecosystem.
- UK Sovereign AI Unit issued an open call for autonomous lab proposals in late 2025.
- ARIA AI Scientist programme doubled to £6M funding 12 projects.
- Periodic Labs ($300M seed), Lila Sciences ($235M Flagship-backed) emerged in 2025.

This positions the proposal not as ambitious autonomy theatre but as well-scoped infrastructure work at the level the field has actually validated.

## Technology choices

| Layer | Choice | Reason |
|---|---|---|
| Agent framework | LangGraph (Python) | First-class support for stateful, multi-agent graphs; production-friendly. |
| State store | PostgreSQL + Redis | PostgreSQL for campaign state durability; Redis for short-lived agent memory. |
| Vector store | pgvector | Same Postgres instance; reduces operational surface. |
| LLM access | OpenAI / Anthropic API + self-hosted Llama 3 / Qwen | Dual-provider for resilience. |
| Retrosynthesis | AiZynthFinder (open-source) + IBM RXN (paid fallback) | Open default, premium optional. |
| ELN integration | Benchling SDK or LabArchives API | Whichever the host institution licenses; pluggable. |

## Risks and unknowns

- **LLM hallucination.** Agents may propose chemically invalid compounds. Mitigation: every Design agent output flows through the chemoinformatic core (Pillar 2) for sanitization + drug-likeness filtering before it ever reaches a chemist.
- **API cost.** Frontier LLM costs can escalate. Mitigation: aggressive caching; per-campaign token budget enforced by the Supervisor; open-source fallback for routine tasks.
- **Change management.** Chemists may resist an "AI manager" perception. Mitigation: the system is positioned and marketed internally as a *coordinator that frees chemists from logistics*, never as a manager. Every agent interaction logs justification and is reviewable.
- **Vendor lock-in.** LangGraph / OpenAI / Benchling APIs evolve. Mitigation: explicit ports/adapter pattern in the orchestrator; each external dependency has a documented adapter interface.

## Phase deliverables

| Phase | Deliverable |
|---|---|
| Phase 1 (months 0–6) | Supervisor + Design + Analysis agents operational on virtual-only loops (no wet-lab integration). |
| Phase 2 (months 6–12) | Synthesis + Assay agents integrated with ELN / LIMS; first end-to-end DMTA campaign run on a real lab project (e.g. an Au(III) hit-to-lead). |
| Phase 3 (months 12–18) | Instrument integration; cross-project campaigns; agent performance benchmarked vs manual baselines (cycle time, hit rate, cost). |
