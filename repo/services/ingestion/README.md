# ingestion

Data ingestion pipelines for MB Finder v2.

- Nightly delta pulls from ChEMBL, PubChem, DrugBank, CSD, MetAP DB.
- Weekly literature ingestion (combined OCR + LLM-assisted structure recognition for figures).
- Real-time ELN webhook receivers (Benchling / LabArchives).
- ProteomeXchange / GEO mirror for lab-internal multi-omics submissions.

## Internal layout

```
src/
├── main.py
├── dags/                          ← Prefect flows
│   ├── chembl_delta.py
│   ├── pubchem_delta.py
│   ├── csd_delta.py
│   ├── literature_scrape.py
│   └── eln_webhook_consumer.py
├── parsers/
│   ├── molscribe.py               ← image-to-SMILES
│   ├── pdf_extractor.py
│   └── eln_payload.py
├── quality/
│   ├── great_expectations.py      ← schema + value rules
│   └── duplicate_detection.py
└── api/
    ├── webhook.py                 ← inbound webhooks
    └── health.py
```

## Storage layout

- Bronze tier: `/bronze/<source>/YYYY-MM-DD/...` immutable.
- Silver tier: PostgreSQL canonical tables (`compounds`, `cell_lines`, etc.).
- Promotion: bronze → silver only after Pydantic + Great Expectations validation.
