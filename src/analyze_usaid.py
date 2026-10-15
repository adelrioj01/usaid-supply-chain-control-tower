"""Calculate independent portfolio KPIs from the processed USAID model."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUTPUT = ROOT / "outputs" / "usaid_baseline_kpis.json"


def read(name):
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value):
    return float(value) if value != "" else None


def safe_divide(numerator, denominator):
    return numerator / denominator if denominator else None


def main():
    shipments = read("FactShipments.csv")
    shipment_lines = read("FactShipmentLines.csv")
    countries = {row["CountryKey"]: row["Country"] for row in read("DimCountry.csv")}
    shipping = {row["ShippingMethodKey"]: row for row in read("DimShippingMethod.csv")}

    eligible_delivery = [row for row in shipments if row["OnTimeFlag"]]
    freight_rows = [row for row in shipments if row["FreightCostUSD"]]
    weight_freight_rows = [row for row in shipments if row["FreightCostUSD"] and row["WeightKg"]]
    late_rows = [row for row in eligible_delivery if row["LateFlag"] == "True"]
    lead_time_rows = [row for row in shipments if row["OrderToDeliveryDays"]]

    country_stats = defaultdict(lambda: {"shipments": 0, "commodity_value_usd": 0.0, "freight_cost_usd": 0.0, "late": 0})
    mode_stats = defaultdict(lambda: {"shipments": 0, "freight_cost_usd": 0.0, "weight_kg": 0.0, "late": 0, "eligible": 0})
    year_stats = defaultdict(lambda: {"shipments": 0, "late": 0, "eligible": 0, "commodity_value_usd": 0.0})
    line_year_counts = defaultdict(int)
    for row in shipment_lines:
        year = row["ActualDeliveryDateKey"][:4] if row["ActualDeliveryDateKey"] else "Unknown"
        line_year_counts[year] += 1

    for row in shipments:
        country = countries[row["CountryKey"]]
        mode = shipping[row["ShippingMethodKey"]]["ShipmentMode"]
        country_stats[country]["shipments"] += 1
        country_stats[country]["commodity_value_usd"] += number(row["LineItemValueUSD"]) or 0
        country_stats[country]["freight_cost_usd"] += number(row["FreightCostUSD"]) or 0
        mode_stats[mode]["shipments"] += 1
        mode_stats[mode]["freight_cost_usd"] += number(row["FreightCostUSD"]) or 0
        mode_stats[mode]["weight_kg"] += number(row["WeightKg"]) or 0

        if row["OnTimeFlag"]:
            mode_stats[mode]["eligible"] += 1
            if row["LateFlag"] == "True":
                mode_stats[mode]["late"] += 1
                country_stats[country]["late"] += 1

        year = row["ActualDeliveryDateKey"][:4] if row["ActualDeliveryDateKey"] else "Unknown"
        year_stats[year]["shipments"] += 1
        year_stats[year]["commodity_value_usd"] += number(row["LineItemValueUSD"]) or 0
        if row["OnTimeFlag"]:
            year_stats[year]["eligible"] += 1
            if row["LateFlag"] == "True":
                year_stats[year]["late"] += 1

    result = {
        "shipment_count": len(shipments),
        "shipment_line_count": sum(int(row["ShipmentLineCount"]) for row in shipments),
        "on_time_rate": safe_divide(sum(row["OnTimeFlag"] == "True" for row in eligible_delivery), len(eligible_delivery)),
        "late_shipment_count": len(late_rows),
        "average_late_days": safe_divide(sum(int(row["DeliveryDelayDays"]) for row in late_rows), len(late_rows)),
        "average_order_to_delivery_days": safe_divide(sum(int(row["OrderToDeliveryDays"]) for row in lead_time_rows), len(lead_time_rows)),
        "commodity_value_usd": sum(number(row["LineItemValueUSD"]) or 0 for row in shipments),
        "freight_cost_usd": sum(number(row["FreightCostUSD"]) or 0 for row in freight_rows),
        "freight_coverage_rate": safe_divide(len(freight_rows), len(shipments)),
        "weight_coverage_rate": safe_divide(sum(bool(row["WeightKg"]) for row in shipments), len(shipments)),
        "freight_cost_per_kg": safe_divide(
            sum(number(row["FreightCostUSD"]) or 0 for row in weight_freight_rows),
            sum(number(row["WeightKg"]) or 0 for row in weight_freight_rows),
        ),
        "countries": len(countries),
        "top_countries_by_shipments": sorted(
            ({"country": key, **value} for key, value in country_stats.items()),
            key=lambda item: item["shipments"], reverse=True
        )[:10],
        "shipment_modes": [
            {
                "mode": key,
                **value,
                "on_time_rate": safe_divide(value["eligible"] - value["late"], value["eligible"]),
            }
            for key, value in sorted(mode_stats.items(), key=lambda item: item[1]["shipments"], reverse=True)
        ],
        "yearly": [
            {
                "year": key,
                **value,
                "shipment_lines": line_year_counts[key],
                "on_time_rate": safe_divide(value["eligible"] - value["late"], value["eligible"]),
            }
            for key, value in sorted(year_stats.items())
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
