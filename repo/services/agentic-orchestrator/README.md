# agentic-orchestrator

The Pillar 3 DMTA orchestrator. Built on LangGraph, persists state in PostgreSQL, runs five specialised agents (Supervisor, Design, Synthesis, Assay, Analysis, Report).

## Public API

- `POST /campaigns` — start a new DMTA campaign with a chemist objective.
- `GET /campaigns/{id}` — campaign state + draft Gantt + pending approvals.
- `POST /campaigns/{id}/approve` — chemist approves the proposed plan or a specific step.
- `POST /campaigns/{id}/halt` — emergency stop; freezes all agents.
- `GET /campaigns/{id}/audit` — append-only log of every agent action.

## Internal architecture

```
src/
├── main.py                          ← FastAPI app factory
├── graph/
│   ├── state.py                     ← CampaignState pydantic model (checkpointable)
│   ├── builder.py                   ← LangGraph state-machine assembly
│   ├── nodes/
│   │   ├── supervisor.py
│   │   ├── design.py
│   │   ├── synthesis.py
│   │   ├── assay.py
│   │   ├── analysis.py
│   │   └── report.py
│   └── tools/                       ← Tool[T,R] adapters (chemoinformatic, inference, KG, ELN, ...)
│       ├── base.py
│       ├── chemoinformatic_tool.py
│       ├── inference_tool.py
│       ├── retrosynthesis_tool.py
│       ├── kg_tool.py
│       ├── eln_tool.py
│       └── lims_tool.py
├── persistence/
│   ├── checkpointer.py              ← LangGraph checkpoint -> Postgres
│   └── audit_log.py                 ← append-only audit table
├── llm/
│   ├── provider.py                  ← OpenAI / Anthropic / self-hosted abstraction
│   └── budget.py                    ← per-campaign token-budget enforcement
└── api/
    ├── campaigns.py
    ├── approvals.py
    └── health.py
```

## Safety boundaries

Every Tool declares a `risk_level` (`safe` / `moderate` / `dangerous`) and a `requires_human_approval` flag. The Supervisor enforces both; agents cannot bypass them. The complete contract is documented in `../../../docs/05_pillar3_agentic_dmta.md`.

## LLM provider strategy

Default backbone via API (Claude 4 Opus or GPT-4-class). Per-agent override supported. Self-hosted Llama 3 / Qwen 2.5 fallback for privacy-sensitive workflows.
