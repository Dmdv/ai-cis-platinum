# Diagrams

Mermaid (`.mmd`) source files for all architecture diagrams referenced in the proposal.

## Inventory

| File | Description | Referenced in |
|---|---|---|
| `c4_context.mmd` | System context — users + external dependencies | `docs/02_high_level_architecture.md`, slides |
| `c4_containers.mmd` | Service-level decomposition of the platform | `docs/02_high_level_architecture.md` |
| `pillar1_ai.mmd` | Pillar 1: geometry-aware, target-aware, foundation, generative | `docs/03_pillar1_ai_modernization.md` |
| `pillar2_multimetal.mmd` | Pillar 2: strategy-pattern sanitization + multi-omics + KG | `docs/04_pillar2_multimetal.md` |
| `pillar3_dmta.mmd` | Pillar 3: agent role model + tool surface | `docs/05_pillar3_agentic_dmta.md` |
| `pillar4_mlops.mmd` | Pillar 4: CI/CD + model registry + observability + data tiers | `docs/06_pillar4_mlops_backend.md` |
| `data_flow.mmd` | End-to-end data flow literature → candidate dossier | `docs/07_data_architecture.md` |
| `dmta_campaign_example.mmd` | Worked example DMTA campaign timeline (Au(III) hit-to-lead) | `docs/05_pillar3_agentic_dmta.md` |
| **`dual_track_gantt.mmd`** | **18-month Gantt of Track A + Track B milestones (40+ items)** | `docs/12_dual_track_milestones.md` |
| **`resource_allocation_pie.mmd`** | **Phase 1 effort split — Track A 50 % / Track B 20 % / Shared 25 % / Wet-lab 5 %** | `docs/12_dual_track_milestones.md` |
| **`resource_allocation_phase2_pie.mmd`** | **Phase 2 effort split — Track A 35 / B 40 / Shared 15 / Wet 10** | `docs/12_dual_track_milestones.md` |
| **`resource_allocation_phase3_pie.mmd`** | **Phase 3 effort split — Track A 20 / B 60 / Shared 10 / Wet 10** | `docs/12_dual_track_milestones.md` |
| **`dual_track_architecture.mmd`** | **Architecture overlay showing how shared infrastructure feeds both tracks** | `docs/12_dual_track_milestones.md` |
| **`decision_register.mmd`** | **Mindmap of all 43 architectural decisions** | `docs/12_dual_track_milestones.md` |
| **`track_convergence.mmd`** | **Sequence diagram showing how Tracks A and B share infrastructure across Phase 1/2/3** | `docs/12_dual_track_milestones.md` |

## Rendering

### Locally with mmdc (Mermaid CLI)

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i pillar1_ai.mmd -o pillar1_ai.png -t neutral
```

### Render all to PNG

```bash
for f in *.mmd; do
  mmdc -i "$f" -o "${f%.mmd}.png" -t neutral -b transparent
done
```

### In VS Code

Install the **Markdown Preview Mermaid Support** extension; `.mmd` files preview directly.

### In a browser

Paste the contents into https://mermaid.live for live editing.

## Style conventions

- Pillar diagrams use a consistent colour scheme:
  - `#fff3cd` (yellow): inputs / users / external content
  - `#d1ecf1` (blue): internal services and processing
  - `#d4edda` (green): tools / outputs
  - `#f8d7da` (red): stores / databases
  - `#e2d6f3` (purple): knowledge graphs / registries
- Solid arrows = synchronous data flow; dashed arrows = async / observability / context.
