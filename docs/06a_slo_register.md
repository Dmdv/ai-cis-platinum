# 06a — Service-Level Objective register

**Contents**

- [Why this register exists](#why-this-register-exists)
- [SLI / SLO definitions](#sli--slo-definitions)
- [Service-level objectives by surface](#service-level-objectives-by-surface)
- [Error-budget policy (freeze-on-burn)](#error-budget-policy-freeze-on-burn)
- [Cold-start budgets](#cold-start-budgets)
- [Alerting](#alerting)


## Why this register exists

`docs/06_pillar4_mlops_backend.md` lists the observability stack (Prometheus / Grafana / Loki / Tempo) and a `success metric: API availability ≥ 99.5 %`. That is *alert design*, not SLO discipline — there are no Service-Level Indicators, no error budgets, no commitment to which services are tier-1 vs tier-3, and no freeze-on-burn policy.

This document is the operational contract. It is referenced by every service's `INTERFACE.md` (Phase-1 deliverable) and by the api-governance document.

## SLI / SLO definitions

A **Service-Level Indicator (SLI)** is a measurable quantity (latency, error rate, freshness). A **Service-Level Objective (SLO)** is a target on that SLI over a measurement window. An **error budget** is `(100 % − SLO)` over the same window.

The platform commits to **rolling 30-day measurement windows** for all SLOs.

## Service-level objectives by surface

| Surface | Tier | SLI | SLO target | Error budget (30 d) | Owner |
| --- | --- | --- | --- | --- | --- |
| Public `inference-api` `/predict` (single-molecule) | 1 — paged | (a) success rate; (b) p95 latency | **99.0 %** success AND p95 < 500 ms | 7.2 hours of failure | Platform engineer |
| Public `inference-api` `/predict/target-aware` | 1 — paged | success rate, p95 latency | **99.0 %** AND p95 < 2 s | 7.2 hours | Platform engineer |
| Public `chemoinformatic-core` `/sanitize` | 1 — paged | success rate, p95 latency | **99.0 %** AND p95 < 200 ms | 7.2 hours | Platform engineer |
| Public web-UI `/` | 2 — Slack | availability (HTTP 200 on healthcheck) | **99.0 %** | 7.2 hours | Platform engineer |
| `agentic-orchestrator` campaign-step | 2 — Slack | (a) step completes within 5 min; (b) no unhandled exception | **99.5 %** | 3.6 hours | Platform engineer |
| `model-training` job submission | 3 — async | job accepted within 30 s | **99.5 %** | 3.6 hours | Platform engineer |
| Internal MLflow / Postgres / KServe control plane | — | n/a (deps) | best-effort | — | — |

Tier definitions:

- **Tier 1 — paged:** PagerDuty alert at 50 % budget burn rate; primary on-call interrupts non-work hours.
- **Tier 2 — Slack:** Slack ping at 50 % burn; reviewed next business day.
- **Tier 3 — async:** weekly review.

**Public-API SLO is 99.0 %, not 99.5 %.** The honest position for a single-engineer / one-person-on-call operation is 99.0 % (7.2 h/mo budget). The earlier "99.5 %" success metric (3.6 h/mo) was a 2× tighter commitment than the staffing model can defend without a paid SRE rotation.

## Error-budget policy (freeze-on-burn)

When a service consumes its 30-day error budget, the following policy applies:

| Budget consumed | Action |
| --- | --- |
| 0 – 50 % | Normal operation; feature work continues. |
| 50 – 80 % | Slack alert to platform engineer; new-feature merges require explicit justification. |
| 80 – 100 % | Page; **feature freeze** on that service — only reliability work, bug fixes, and rollback PRs are merged. Continues until the budget window rolls over or 30 days of clean operation pass. |
| > 100 % (budget exhausted) | All feature-flag rollouts pause across the platform until a post-incident review identifies the root cause and a remediation lands. |

The freeze-on-burn policy is not an exception process — it is the default. A service that cannot meet its SLO is more valuable to fix than to extend.

## Cold-start budgets

Per `docs/06_pillar4_mlops_backend.md` §4.2 (per-tier scale policy), each scale-to-zero tier has a documented cold-start budget:

| Tier | Cold-start SLO (p95) | Mitigation |
| --- | --- | --- |
| Tier 1 (small classifier) | ≤ 30 s | Warm pool of 1 GPU; KServe `minReplicas: 1` for paged endpoints |
| Tier 2 (Llama 3 70B AWQ) | ≤ 180 s (when scale-to-zero is chosen over 24×7) | AWQ-loaded weight checkpoint cached in fast object storage; cold load benchmarked monthly |
| Tier 3 (AF3 / Boltz-2 batch) | n/a — async batch | Queue depth alert > 100 jobs |

If a tier's cold-start p95 exceeds its SLO, the tier is upgraded to 24×7 or its warm pool is enlarged. This decision is made against the error-budget evidence, not on intuition.

## Alerting

- **PagerDuty** routes Tier-1 paged alerts to the on-call engineer.
- **Slack** routes Tier-2 alerts to `#ai-cis-platinum-ops`.
- **Email digest** routes Tier-3 weekly summaries.
- **Grafana dashboards** display rolling 30-day SLO compliance per service; the freeze-on-burn status is a first-class dashboard panel.
- **LLM token observability** (per `docs/06_pillar4_mlops_backend.md` §4.4): the Grafana panel `llm_tokens_total{campaign_id, agent_id, model}` triggers a per-campaign budget alert at 80 % of the configured token cap; freeze-on-burn applies analogously.

## What this register does NOT cover

- Customer-facing uptime guarantees (the platform is not under SLA contract).
- Vendor-dependent SLOs (OpenAI / Anthropic API availability — those are upstream best-effort).
- Skills Hub availability (Phase-3 deliverable; SLOs added in the Phase-3 update to this register).
