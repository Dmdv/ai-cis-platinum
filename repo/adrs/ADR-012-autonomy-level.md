# ADR-012 — Autonomy level commitment (L2 with L3 in Phase 3)

**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** Reviewers of an AI-driven drug discovery proposal will reasonably ask: *"how autonomous is this thing, really?"*. Without a recognised yardstick, the answer is rhetorically squishy. Evans & Desai's 5-level autonomy ladder (TechPolitik, *Self-driving labs = infrastructure, not just intelligence*, February 2026) — modelled on SAE driving levels — is the most defensible vocabulary the field has produced.

## Decision

The MB Finder v2 system commits to the following per-phase autonomy levels, using Evans & Desai's framework:

| Phase | Target level | What it means operationally |
|---|---|---|
| Phase 1 (months 0-6) | L2 — Constraint-aware planning | Supervisor agent reasons explicitly about cost, time, safety, uncertainty, and multi-objective trade-offs across the five chemistry verifiers. Chemists approve every wet-lab step. |
| Phase 2 (months 6-12) | L2 → L3 in flight | Adds model-driven exploration: agents propose experiments leveraging prior experiments, literature retrieval, and cross-modal reasoning (geometry + sequence + omics). Still chemist-approved. |
| Phase 3 (months 12-18) | L3 with L4 stubs | Equivariant diffusion + JT-VAE generative track searches known chemical space "more intelligently" (Evans & Desai's L3 definition); data-drift detection (Pillar 4 §4.4) provides the L4 self-maintenance stub. |
| Beyond 18 months | L4 / L5 | Out of current scope. Flagged as future opportunities. |

## Rationale

- **L2 is honest.** The lab today is L1 (closed-loop optimisation around MKANO). Jumping straight to L4/L5 claims would be implausible and would attract the same reviewer scepticism the A-Lab incident attracted (see Pillar 3 / Risks R2). L2 is the next defensible step.
- **L3 in Phase 3 is achievable.** Per Evans & Desai's own examples, current L3 players (Periodic Labs, Lila Sciences, Recursion, Chemify) reached L3 via large capital injections and infrastructure investment. A host lab can reach L3 *for metallodrug discovery* with one platform engineer + the existing chemist team, because the scope is narrower and the host lab already has Pillar 1 / Pillar 2 building blocks via the published MKANO / MB Finder system.
- **L4/L5 are explicitly deferred.** L4 requires automation-native instruments and drift-detection discipline borrowed from manufacturing; L5 requires industry-wide standardisation that no single lab can deliver. Both are correctly out-of-scope for an 18-month plan.
- **The level commitment de-risks the proposal.** A reviewer who asks "isn't this just autonomy hype?" gets a precise answer: "We target L2 in Phase 1 with concrete L3 deliverables in Phase 3, per Evans & Desai's framework. L4 self-maintenance is a future opportunity, not a 2026 promise."

## Consequences

- The roadmap (`docs/08_implementation_roadmap.md`) success metrics should be cross-referenced against this ladder.
- The Pillar 3 "Why not full autonomy" section already cites the A-Lab cautionary tale; this ADR codifies the positive commitment.
- The architecture stays compatible with L4 (drift detection) and L5 (portability via MCP + Cellosaurus + Skills) even though those levels are not committed.

### Lab-automation archetype positioning (Yang, *The Lab Automation Startup Ecosystem*, Republic of Science, Sep 2025)

Yang's archetype taxonomy further locates the proposal within the 2025-2026 lab-automation ecosystem:

| Archetype | What they do | Examples | MB Finder v2 relationship |
|---|---|---|---|
| **Discovery-as-a-Service (DaaS)** | Bundle automation + in-silico, commercialise/license discoveries | Periodic Labs ($300M), Lila Sciences ($235M), Recursion | Not the proposal's archetype — DaaS requires vertical commercialisation infrastructure most academic labs do not have. |
| **Infrastructure-as-a-Service (Cloud Labs)** | Remote access to automated lab infrastructure | Emerald Cloud Lab, Strateos | Not the proposal's archetype — requires massive CapEx and physical-lab build-out. |
| **ScienceData-as-a-Service / Lab Orchestration** | Software wrapper layer atop existing instruments | Benchling, labOS (Acceleration Consortium) | **The proposal's archetype.** MB Finder v2 sits on top of the lab's existing instruments, exfiltrates data, orchestrates experiments, layers in AI for analysis. |
| **Lab-in-a-Box** | Standalone automation products (liquid handlers, workcells) | OpenTrons, ChemSpeed, Tecan, Mito Robotics, Flow Robotics, North Robotics, Unchained Labs, Trilo Bio | **Complementary** — the lab buys these and the proposal orchestrates them via MCP. |
| **General-Purpose Lab Robotics** | Humanoid / multi-purpose robots for chemistry | Medra AI, Zeon Systems | Out of scope at lab budget; revisit if cost-performance reaches inflection. |

**The structural gap Yang identifies** — *"a conspicuous gap is companies building science instruments designed from the ground up for automation. Most existing startups abstract over the limitations of today's fragmented instrument landscape"* — is not within scope for the host lab, but the proposal's architecture is *future-compatible* with such instruments via MCP. When automation-native instruments emerge with first-class Python APIs, MB Finder v2 consumes them like any other MCP server with zero code changes. ADR-007 (MCP) is the load-bearing decision that makes this work.

## Alternatives considered

- **No level commitment** (status quo before v5). Rejected — leaves the proposal vulnerable to "is this just autonomy theatre?" questions without a structured answer.
- **L3 from Phase 1.** Rejected as over-promising; L2 with L3-in-flight is the honest commitment.
- **L0 framing ("we're just automation, not autonomy").** Rejected as under-claiming; the Supervisor agent's cost/safety/uncertainty reasoning is genuinely L2.

## Revisit conditions

- A successor autonomy framework displaces Evans & Desai's ladder.
- The lab acquires L4-capable instruments (drift-detecting hardware) — at which point L4 becomes scope-able.
- A consortium standardises Pillar 3 / Pillar 2 outputs sufficiently that L5 portability becomes a near-term goal.
