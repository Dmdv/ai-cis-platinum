# inference-api

The synchronous and asynchronous prediction service for MB Finder v2.

Wraps the model registry (MLflow) and the chemoinformatic-core to serve:

- **Single-molecule prediction** — `POST /predict` returns active/inactive call + IC50 regression + geometry classification per requested cell line.
- **Target-aware prediction** — `POST /predict/target-aware` adds protein-target conditioning (COL3A1, BUB1B, etc.) via the AF3/Boltz-2 service.
- **Batch prediction** — `POST /predict/batch` enqueues an async job; result polled via `GET /predict/batch/{id}`.
- **Model selection** — `GET /models` lists deployed model versions; `?model=mkano-plus@2.1.0` selects.

## Internal architecture

```
src/
├── main.py                      ← FastAPI app factory
├── api/
│   ├── predict.py               ← /predict endpoints
│   ├── batch.py                 ← /predict/batch endpoints
│   ├── models.py                ← /models listing
│   └── health.py
├── inference/
│   ├── runner.py                ← TorchServe / Triton client
│   ├── target_aware.py          ← AF3 / Boltz-2 integration
│   └── ensemble.py              ← MKANO+ ↔ ChemFM-LoRA ensemble logic
├── caching/
│   └── redis_cache.py           ← memoise predictions by InChIKey + model version
└── observability/
    └── metrics.py               ← Prometheus counters / histograms
```

## SLA targets

- p95 single-molecule latency < 2 s.
- p95 batch throughput > 1000 compounds/min.
- Availability ≥ 99.5 % for the public endpoint.
