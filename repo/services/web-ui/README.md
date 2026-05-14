# web-ui

The chemist-facing browser front-end for MB Finder v2. Next.js + React + TypeScript. Uses RDKit-JS for client-side molecular rendering and 3Dmol.js for 3D viewing.

## Surfaces

- **/** — landing / login.
- **/search** — Substances, Cell Lines, References tabs (replicating MB Finder v1 layout).
- **/predict** — single-molecule prediction panel (Substances + Cell Lines selectable).
- **/predict/target-aware** — target-aware prediction with protein selector.
- **/campaigns** — agentic DMTA campaigns: list, detail, approval views.
- **/campaigns/{id}/approval/{step}** — chemist approval gate.
- **/admin** — model registry browser, dataset versions, deployment controls.

## Layout

```
src/
├── pages/                       ← Next.js pages router
├── components/
│   ├── molecules/               ← molecule rendering
│   ├── search/
│   ├── campaign/
│   └── prediction/
├── hooks/
├── api-client/                  ← typed OpenAPI client (generated)
├── stores/                      ← Zustand
└── public/
```

## Backwards compatibility

The Substances / Cell Lines / References tab layout intentionally mirrors MB Finder v1 (Figure 5 of Rusanov et al., 2026) so chemists do not need to relearn the UI. New surfaces (campaigns, target-aware, admin) are additions.
