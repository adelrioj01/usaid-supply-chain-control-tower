# Metric definitions

| Metric | Definition | Grain and exclusions |
|---|---|---|
| Shipments | Rows in `FactShipments` | One ASN/delivery note. Blank ASN values receive a row-specific key. |
| Shipment lines | Rows in `FactShipmentLines` | Original USAID source grain. |
| On-time shipments | Actual delivery date on or before scheduled delivery date | Shipment grain. Both dates must exist. |
| On-time delivery rate | On-time shipments / shipments eligible for delivery analysis | Excludes rows missing either delivery date. |
| Late shipments | Actual delivery date after scheduled delivery date | Shipment grain. |
| Average late days | Average positive delivery delay among late shipments | On-time and early shipments excluded. |
| Order-to-delivery days | Actual delivery date minus PO-sent-to-vendor date | Excludes missing order dates. |
| Commodity value | Sum of line item value | Shipment-line grain. |
| Freight cost | Sum of freight cost after deduplicating to shipment grain | Excludes nonnumeric source labels. |
| Freight cost per kg | Freight cost / shipment weight | Includes shipments with both numeric weight and freight. |
| Logistics cost rate | Freight cost / commodity value | Uses shipment freight and line commodity value under shared filters. |
| Freight coverage | Shipments with numeric freight / total shipments | Completeness measure. |
| Weight coverage | Shipments with numeric weight / total shipments | Completeness measure. |
| First-line value share | Commodity value for first-line-designated records / commodity value | Shipment-line grain. |

## Source limitations

- `Freight Cost (USD)` contains text such as freight included in commodity cost or references to another ASN. Numeric measures treat those values as null.
- `Weight (Kilograms)` also contains nonnumeric references. The model reports coverage beside weight-based measures.
- Freight and weight describe the shipment and may repeat across line items. `FactShipments` retains one value per ASN/delivery note.
- Historical performance does not represent current USAID operations.
