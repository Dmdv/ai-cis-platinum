# ADR-004 — LangGraph for the agentic orchestrator

**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** Pillar 3 introduces a multi-agent DMTA orchestrator. Several frameworks are viable: LangChain, LangGraph, CrewAI, AutoGen, custom.

## Decision

Build the orchestrator on LangGraph. State persists in PostgreSQL; short-lived agent memory in Redis; vector memory in pgvector.

**Independent validation (Tran, *AI Agent Framework Landscape*, Medium, Nov 2025):** LangChain has itself publicly pivoted away from LangChain-for-agents toward LangGraph. Quoting the source: *"LangChain — the framework with 80K+ GitHub stars that dominated 2023 — publicly shifted its focus. The team's message is clear: 'Use LangGraph for agents, not LangChain.'"* LangGraph reached GA in May 2025 and now runs in production at LinkedIn (AI recruiter, internal SQL Bot), Uber (large-scale code migrations), Replit (AI copilot building software from scratch), Elastic (real-time threat detection), AppFolio, and ≈400 other companies.

## Rationale

- LangGraph models the system as a stateful graph of nodes — the natural fit for DMTA which is genuinely a state machine with explicit transitions (planning → synthesising → assaying → analysing).
- First-class support for checkpoints, replay, and human-in-the-loop interrupts, all of which the scientific context demands.
- Active development, large community, compatible with multiple LLM providers (OpenAI, Anthropic, self-hosted).
- Well-defined tool-calling primitives that match the proposed `Tool` contract (typed inputs/outputs, risk levels, audit).

## Consequences

- Adopts the LangChain ecosystem's evolving API surface. Mitigated by encapsulating LangGraph behind the orchestrator service's public contract — internal churn does not propagate.
- LangGraph is Python-only; this is acceptable as the orchestrator is naturally a Python service.

## Alternatives considered

- **LangChain Agents (classic):** rejected — less suitable for long-running, checkpointed workflows.
- **CrewAI Enterprise / Flows (2025):** opinionated about role definitions but matured significantly. As of mid-2025: $18M Series A, $3.2M revenue by July 2025, 100,000+ daily agent executions, 150+ enterprise customers, 60 % of Fortune 500. Ship time: ≈2 weeks vs ≈2 months for LangGraph (Tran, Nov 2025). **Rejected for this proposal specifically** because the architecture explicitly requires cycles, conditionals, and chemist sign-off gates that CrewAI's role-based abstraction struggles with. Tran's quoted real-world case is instructive: an e-commerce team built a CrewAI content-generation system in 2 weeks, then 6 months later needed conditional branching ("if writer produces low-quality content, send back to researcher for more data") — a feature *"possible in LangGraph, difficult/impossible in CrewAI"* — and burned 3 weeks rewriting **60 % of the codebase**. *Migration cost from CrewAI to LangGraph runs 50-80 % rewrite once requirements outgrow CrewAI's ceiling.* The proposed DMTA loop is exactly the kind of workflow that needs cycles from day one, so CrewAI is the wrong starting point — even if it would let the platform engineer ship faster initially.
- **Microsoft Agent Framework (Oct 2025 public preview, Q1 2026 GA):** merges AutoGen + Semantic Kernel into a unified Azure-integrated SDK. Multi-language (C#, Python, Java), production SLAs. Considered seriously and rejected on two grounds: (i) public preview means breaking-change risk before GA; (ii) deep Azure integration limits portability if the host lab later moves to a different cloud or internal HPC infrastructure. Worth revisiting in Q3 2026 after GA stabilises.
- **AutoGen v0.4 / Magentic-One (Microsoft, 2024-2025):** subsumed into Microsoft Agent Framework above. Was an actor-model rewrite from AutoGen v0.2; reasonable alternative, but LangGraph's explicit checkpointing better matches our auditability needs.
- **PydanticAI (2024):** type-safe agents with structured outputs; lower surface area than LangGraph but less mature checkpointing. Worth revisiting in 2026.
- **DSPy (Stanford, ICLR 2024):** declarative LM programs with optimisable prompts. *Complementary*, not alternative — used inside LangGraph nodes for the Design and Analysis agents (see Pillar 3 Component 3.4.2). DSPy compiles prompts against an evaluation set via teleprompters (MIPRO, BootstrapFewShot, COPRO); LangGraph remains the state-machine wrapper.
- **OpenAI Swarm / Agents SDK (2024 → 2025):** lightweight handoff pattern; lacks checkpointed state.
- **Claude Agent SDK + Claude Skills (Anthropic, 2025):** Anthropic's emerging recommendation for agentic systems. The proposal does NOT reject this; it adopts the **hybrid** position described in Pillar 3 Component 3.4.1a: LangGraph as the state-machine skeleton, Anthropic-style Skills as the durable scientific artefacts (markdown procedures + executables) loaded on-demand inside each agent. This makes the system forward-compatible to architecture #3.
- **Custom orchestrator:** rejected — unnecessary, given the maturity of LangGraph.

### The Three Architectures (Anthropic, December 2024 / Greyling synthesis January 2026)

Three production agent architectures co-exist in 2026:
1. **Monolithic single agent.** Central LLM + tools. Prototyping-grade.
2. **Multi-agent workflows (LangGraph-class).** The proposal's chosen architecture. Specialised agents in a workflow graph; cost-controlled; auditable.
3. **Skills (modular capabilities).** Anthropic's 2025 recommendation. Modular markdown procedures + optional executables loaded on-demand.

The proposal hybridises #2 and #3 explicitly. Pure architecture #2 alone is out of date for 2026; the design adds skill-curation as a first-class deliverable inside each LangGraph node (see ADR-011).

### The Low-Floor / High-Ceiling trade-off (Tran, Nov 2025)

Tran frames the 2025 framework choice in terms a hiring committee will recognise:

- **Low Floor / Low Ceiling** (CrewAI, OpenAI Swarm): easy to start, limited customisation. *"Perfect for MVPs and simple use cases. Risk: outgrowing the framework as requirements evolve."*
- **High Floor / High Ceiling** (LangGraph, Microsoft Agent Framework): steeper learning curve, extensive customisation. *"Suitable for complex production systems. Risk: over-engineering simple problems."*

The counter-intuitive advice (verbatim): *"Start with high-ceiling frameworks (LangGraph, Microsoft) even if they feel like overkill. 'Growing into' a framework is far easier than migrating out."*

The proposed DMTA campaign loop has cycles (analysis feeds back to design), conditionals (chemist-approval gates), checkpointing (multi-week wet-lab pauses), and observability (every action audit-logged for publication reproducibility). It is the canonical *high-floor* use case. LangGraph is correct from day one, even at the cost of 2× initial ship time vs CrewAI. ADR-011 (Skills) and ADR-007 (MCP) reduce the long-run integration risk further.

## Revisit conditions

- LangGraph deprecates checkpointing or state persistence APIs.
- A simpler model emerges that meets the same auditability requirements with less surface area.
- Anthropic's Skills ecosystem matures enough that architecture #3 alone subsumes the lab's needs (orchestrator becomes a thin Skills harness rather than a state machine).
- The MCP code-execution pattern (ADR-007) becomes powerful enough that the orchestrator simplifies into a single agent that writes code calling all chemistry tools as one execution block.
