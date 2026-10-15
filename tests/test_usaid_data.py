"""Validate the USAID star-schema outputs and core business calculations."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
REPORT = ROOT / "outputs" / "usaid_data_quality.json"


def read(name):
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    facts = read("FactShipmentLines.csv")
    shipments = read("FactShipments.csv")
    require(report["raw_rows"] == 10324, "unexpected USAID raw row count")
    require(report["raw_columns"] == 33, "unexpected USAID raw column count")
    require(len(facts) == report["raw_rows"], "fact table must retain every source row")
    require(len({row["ShipmentLineKey"] for row in facts}) == len(facts), "shipment line keys must be unique")
    require(len({row["ShipmentKey"] for row in shipments}) == len(shipments), "shipment keys must be unique")
    require(sum(int(row["ShipmentLineCount"]) for row in shipments) == len(facts), "shipment lines must reconcile")
    require({row["ShipmentKey"] for row in facts} == {row["ShipmentKey"] for row in shipments}, "shipment keys must reconcile")

    dimension_checks = {
        "CountryKey": "DimCountry.csv",
        "VendorKey": "DimVendor.csv",
        "ProjectKey": "DimProject.csv",
        "ManufacturingSiteKey": "DimManufacturingSite.csv",
        "ShippingMethodKey": "DimShippingMethod.csv",
        "ProductKey": "DimProduct.csv",
    }
    for fact_key, filename in dimension_checks.items():
        dimension_keys = {row[fact_key] for row in read(filename)}
        orphan_count = sum(row[fact_key] not in dimension_keys for row in facts)
        require(orphan_count == 0, f"{fact_key} has {orphan_count} orphan values")

    eligible = [row for row in facts if row["OnTimeFlag"]]
    require(len(eligible) == report["eligible_delivery_rows"], "delivery eligibility mismatch")
    on_time_rate = sum(row["OnTimeFlag"] == "True" for row in eligible) / len(eligible)
    require(0 <= on_time_rate <= 1, "invalid on-time rate")
    require(report["source"]["local_sha256"], "source checksum missing")
    eligible_shipments = [row for row in shipments if row["OnTimeFlag"]]
    shipment_on_time_rate = sum(row["OnTimeFlag"] == "True" for row in eligible_shipments) / len(eligible_shipments)
    require(len(eligible_shipments) == report["eligible_delivery_shipments"], "shipment eligibility mismatch")
    print(f"Validated {len(facts):,} USAID lines and {len(shipments):,} shipments. On-time rate: {shipment_on_time_rate:.1%}.")


if __name__ == "__main__":
    main()
