# Power Query setup

1. Run `src/prepare_usaid_data.py` to create `data\processed`.
2. Create a text parameter named `pProcessedFolder` that points to that directory.
3. Create a blank function query named `fnLoadProcessedCsv`.
4. Add the shipment and shipment-line queries included here.
5. Load each dimension CSV with the same function and explicit column types.
6. Apply the relationships in `model/model-spec.md`.

Python owns source parsing, shipment-level deduplication and reproducible quality reporting. Power Query owns file ingestion, data types and refresh inside Power BI. This separation keeps transformations testable outside the report.
