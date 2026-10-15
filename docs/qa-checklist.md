# Power BI QA checklist

Use this checklist after applying `model/build-model.tmdl` and refreshing the model.

## Data refresh

- [ ] Set the `DataRoot` parameter to the local `data/processed` directory.
- [ ] Refresh completes without Power Query errors.
- [ ] All nine model tables load.
- [ ] No relationship is many-to-many or bidirectional.
- [ ] There is no direct relationship between `FactShipments` and `FactShipmentLines`.

## Baseline reconciliation

These values must match `outputs/usaid_baseline_kpis.json` and the Python validator:

| Check | Expected result |
|---|---:|
| Shipment lines | 10,324 |
| Distinct shipments | 7,030 |
| Destination countries | 43 |
| On-time delivery rate | 88.6% |
| Late shipments | 804 |
| Average late days | 20.0 |
| Commodity value | approximately $1.63B |
| Freight cost | approximately $68.8M |
| Freight coverage | 88.2% |
| Freight cost per kg | approximately $3.24 |

## Measure behavior

- [ ] Product filters change commodity-value measures but do not alter shipment-grain freight measures.
- [ ] Country, vendor, project, manufacturing site, and shipping method filter both fact tables.
- [ ] The active date relationship uses actual delivery date.
- [ ] Order, scheduled-delivery, and delivery-recorded relationships remain inactive.
- [ ] Empty freight and weight values remain blank rather than becoming zero.
- [ ] Percentages use eligible records as their denominator.

## Report interactions

- [ ] Page and visual filters produce consistent totals.
- [ ] Cross-highlighting works without ambiguous results.
- [ ] Drill-through reaches shipment-level detail and preserves filter context.
- [ ] Tooltips explain units, date grain, and null handling.
- [ ] Reset-filter navigation returns every page to its intended default state.

## Presentation and accessibility

- [ ] Currency, percentages, weights, and dates have consistent formats.
- [ ] Titles state the business question answered by each visual.
- [ ] Color is not the only signal distinguishing good and poor performance.
- [ ] Text and chart contrast remain readable at 100% zoom.
- [ ] Visuals have useful alt text and a logical tab order.
- [ ] Pages avoid unnecessary scrolling at the target canvas size.

## Performance and release

- [ ] Performance Analyzer shows no unexpectedly slow visual.
- [ ] Unused columns and automatic date/time are disabled or removed.
- [ ] A clean refresh succeeds after reopening the project.
- [ ] Executive Overview screenshot contains no personal or local-path information.
- [ ] README figures match the final report.
- [ ] Historical scope and non-causal limitations are visible in the repository.
