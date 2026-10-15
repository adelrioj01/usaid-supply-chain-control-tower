# Data quality rules

The pipeline preserves the original CSV in `data/external` and writes transformed tables to `data/processed`. It never overwrites the source.

| Rule | Result |
|---|---:|
| Raw rows retained | 10,324 |
| Raw columns detected | 33 |
| Freight values blank or nonnumeric | 4,126 line records |
| Weight values blank or nonnumeric | 3,952 line records |
| Missing insurance values | 287 line records |
| Shipment attribute conflicts | Retained as `AttributeConflictCount` for review |

## Transformation policy

- Parse known date formats and convert source labels such as `Date Not Captured` to null.
- Convert numeric fields only when the complete value parses as a number.
- Preserve nonnumeric freight and weight cases as quality flags instead of replacing them with zero.
- Aggregate repeated line values to one shipment using ASN/delivery note.
- Use the maximum numeric shipment weight and freight value within each ASN because the source defines both fields at shipment level.
- Assign a row-specific shipment key when ASN/delivery note is blank.
- Retain every source line and record its original row number.

`FactShipments[ShipmentLineCount]` reconciles to the 10,324 source lines. Every line has valid dimension keys and a valid `ShipmentKey`.
