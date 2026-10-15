# Semantic model specification

Use single-direction relationships from dimensions to facts. Keep shipment and shipment-line facts separate because freight and weight occur at shipment grain while product value occurs at line grain.

| Table | Grain |
|---|---|
| `FactShipments` | One ASN/delivery note, or one source row when ASN is blank |
| `FactShipmentLines` | One original USAID shipment line |
| `DimDate` | One calendar date |
| `DimCountry` | One destination country |
| `DimVendor` | One vendor |
| `DimProject` | One project code |
| `DimManufacturingSite` | One manufacturing site |
| `DimShippingMethod` | One managed-by, fulfill-via, Incoterm and shipment-mode combination |
| `DimProduct` | One source product-description combination |

## Relationships

- `DimCountry`, `DimVendor`, `DimProject`, `DimManufacturingSite` and `DimShippingMethod` filter both facts.
- `DimProduct` filters `FactShipmentLines` only.
- `DimDate[DateKey]` has an active relationship to `FactShipments[ActualDeliveryDateKey]`.
- Keep order, scheduled-delivery and delivery-recorded date relationships inactive.
- Do not create a direct fact-to-fact relationship.

## Measure ownership

- Delivery, lead-time, weight and freight measures use `FactShipments`.
- Product, quantity, insurance and commodity-value measures use `FactShipmentLines`.
- Product filters do not apply to freight measures because the source does not allocate shipment freight to individual products.

## Display folders

- `01 Volume and value`
- `02 Delivery performance`
- `03 Freight efficiency`
- `04 Product portfolio`
- `05 Data quality`
- `90 Time intelligence`
