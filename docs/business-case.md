# Business case

## Program context

USAID's Supply Chain Management System supported deliveries of antiretroviral medicines, HIV rapid diagnostic tests and laboratory commodities to public-health programs. The source records shipment dates, destination countries, vendors, products, shipment modes, weights and costs.

## Decision problem

Program managers need to understand where delivery delays and freight costs concentrate. The report distinguishes shipment-level logistics metrics from product-line values so users do not double-count weight or freight repeated across shipment lines.

## Users

- Supply chain director: delivery reliability, cost and country performance
- Logistics manager: mode utilization, freight efficiency and delay
- Procurement manager: vendor performance and commodity value
- Country program manager: shipment history, late deliveries and product mix
- Data steward: missing numeric values, source coverage and transformation checks

## Decisions supported

1. Identify countries and shipment modes with persistent delivery delays.
2. Compare freight cost per kilogram across routes and modes where both values exist.
3. Prioritize investigation of late, high-value shipments.
4. Evaluate vendor and manufacturing-site delivery performance.
5. Separate data-quality gaps from operational outcomes.

## Scope

The dataset contains 10,324 shipment lines and 7,030 distinct shipments delivered from 2006 through 2015. It covers 43 destination countries. The source does not contain inventory balances, demand forecasts, supplier capacity or warehouse operations, so the report does not infer those measures.
