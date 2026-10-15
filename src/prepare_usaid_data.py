"""Prepare the public USAID shipment-pricing dataset for Power BI.

The raw file remains unchanged in data/external. This script creates a star
schema in data/processed and a quality report in outputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "external" / "usaid_supply_chain_shipment_pricing.csv"
OUTPUT = ROOT / "data" / "processed"
REPORTS = ROOT / "outputs"


def blank(value: str | None) -> bool:
    return value is None or not value.strip()


def parse_date(value: str | None) -> date | None:
    if blank(value):
        return None
    text = value.strip()
    if text.lower() in {"date not captured", "pre-pq process", "n/a - from rdc", "n/a"}:
        return None
    for pattern in ("%d-%b-%y", "%d-%b-%Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            pass
    return None


def parse_number(value: str | None) -> float | None:
    if blank(value):
        return None
    text = value.strip().replace(",", "").replace("$", "")
    try:
        return float(text)
    except ValueError:
        return None


def date_key(value: date | None) -> int | str:
    return int(value.strftime("%Y%m%d")) if value else ""


def write_csv(path: Path, records: list[dict], columns: list[str] | None = None):
    if not records:
        raise ValueError(f"No rows available for {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    names = columns or list(records[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def make_dimension(values, key_name, attribute_names):
    cleaned = sorted(set(values), key=lambda item: tuple(str(value).casefold() for value in item))
    rows = []
    lookup = {}
    for key, attrs in enumerate(cleaned, start=1):
        row = {key_name: key}
        row.update(dict(zip(attribute_names, attrs)))
        rows.append(row)
        lookup[attrs] = key
    return rows, lookup


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source file: {SOURCE}")

    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))

    expected_columns = {
        "id", "project code", "country", "managed by", "fulfill via", "vendor inco term",
        "shipment mode", "po sent to vendor date", "scheduled delivery date",
        "delivered to client date", "delivery recorded date", "product group",
        "sub classification", "vendor", "item description", "molecule/test type",
        "brand", "dosage", "dosage form", "unit of measure (per pack)",
        "line item quantity", "line item value", "pack price", "unit price",
        "manufacturing site", "first line designation", "weight (kilograms)",
        "freight cost (usd)", "line item insurance (usd)"
    }
    missing_columns = expected_columns - set(raw_rows[0])
    if missing_columns:
        raise ValueError(f"Source schema changed. Missing columns: {sorted(missing_columns)}")

    country_rows, country_key = make_dimension(
        [(row["country"].strip() or "Unknown",) for row in raw_rows], "CountryKey", ["Country"]
    )
    vendor_rows, vendor_key = make_dimension(
        [(row["vendor"].strip() or "Unknown",) for row in raw_rows], "VendorKey", ["Vendor"]
    )
    project_rows, project_key = make_dimension(
        [(row["project code"].strip() or "Unknown",) for row in raw_rows], "ProjectKey", ["ProjectCode"]
    )
    site_rows, site_key = make_dimension(
        [(row["manufacturing site"].strip() or "Unknown",) for row in raw_rows],
        "ManufacturingSiteKey", ["ManufacturingSite"]
    )
    shipping_values = [(
        row["managed by"].strip() or "Unknown",
        row["fulfill via"].strip() or "Unknown",
        row["vendor inco term"].strip() or "Unknown",
        row["shipment mode"].strip() or "Unknown",
    ) for row in raw_rows]
    shipping_rows, shipping_key = make_dimension(
        shipping_values, "ShippingMethodKey", ["ManagedBy", "FulfillVia", "VendorIncoterm", "ShipmentMode"]
    )
    product_values = [(
        row["product group"].strip() or "Unknown",
        row["sub classification"].strip() or "Unknown",
        row["item description"].strip() or "Unknown",
        row["molecule/test type"].strip() or "Unknown",
        row["brand"].strip() or "Unknown",
        row["dosage"].strip() or "Not specified",
        row["dosage form"].strip() or "Not specified",
        row["unit of measure (per pack)"].strip() or "Not specified",
    ) for row in raw_rows]
    product_rows, product_key = make_dimension(
        product_values,
        "ProductKey",
        ["ProductGroup", "SubClassification", "ItemDescription", "MoleculeOrTestType", "Brand", "Dosage", "DosageForm", "UnitsPerPack"],
    )

    facts = []
    issue_counter = Counter()
    valid_dates = []
    id_counter = Counter(row["id"].strip() for row in raw_rows)
    for source_row_number, row in enumerate(raw_rows, start=2):
        order_date = parse_date(row["po sent to vendor date"])
        scheduled_date = parse_date(row["scheduled delivery date"])
        delivered_date = parse_date(row["delivered to client date"])
        recorded_date = parse_date(row["delivery recorded date"])
        valid_dates.extend(value for value in (order_date, scheduled_date, delivered_date, recorded_date) if value)

        quantity = parse_number(row["line item quantity"])
        line_value = parse_number(row["line item value"])
        pack_price = parse_number(row["pack price"])
        unit_price = parse_number(row["unit price"])
        weight = parse_number(row["weight (kilograms)"])
        freight = parse_number(row["freight cost (usd)"])
        insurance = parse_number(row["line item insurance (usd)"])

        issues = []
        if id_counter[row["id"].strip()] > 1:
            issues.append("Duplicate source ID")
        if not scheduled_date:
            issues.append("Missing scheduled delivery date")
        if not delivered_date:
            issues.append("Missing delivered date")
        if weight is None:
            issues.append("Weight not numeric")
        if freight is None:
            issues.append("Freight cost not numeric")
        if insurance is None:
            issues.append("Insurance missing")
        if quantity is None or quantity < 0:
            issues.append("Invalid line item quantity")
        if line_value is None or line_value < 0:
            issues.append("Invalid line item value")
        for issue in issues:
            issue_counter[issue] += 1

        delay_days = (delivered_date - scheduled_date).days if delivered_date and scheduled_date else None
        lead_time_days = (delivered_date - order_date).days if delivered_date and order_date else None
        shipment_tuple = (
            row["managed by"].strip() or "Unknown",
            row["fulfill via"].strip() or "Unknown",
            row["vendor inco term"].strip() or "Unknown",
            row["shipment mode"].strip() or "Unknown",
        )
        product_tuple = (
            row["product group"].strip() or "Unknown",
            row["sub classification"].strip() or "Unknown",
            row["item description"].strip() or "Unknown",
            row["molecule/test type"].strip() or "Unknown",
            row["brand"].strip() or "Unknown",
            row["dosage"].strip() or "Not specified",
            row["dosage form"].strip() or "Not specified",
            row["unit of measure (per pack)"].strip() or "Not specified",
        )
        facts.append({
            "ShipmentLineKey": int(row["id"]),
            "SourceRowNumber": source_row_number,
            "ProjectKey": project_key[(row["project code"].strip() or "Unknown",)],
            "CountryKey": country_key[(row["country"].strip() or "Unknown",)],
            "VendorKey": vendor_key[(row["vendor"].strip() or "Unknown",)],
            "ProductKey": product_key[product_tuple],
            "ManufacturingSiteKey": site_key[(row["manufacturing site"].strip() or "Unknown",)],
            "ShippingMethodKey": shipping_key[shipment_tuple],
            "OrderDateKey": date_key(order_date),
            "ScheduledDeliveryDateKey": date_key(scheduled_date),
            "ActualDeliveryDateKey": date_key(delivered_date),
            "DeliveryRecordedDateKey": date_key(recorded_date),
            "PurchaseOrderNumber": row["po / so #"].strip(),
            "ASNOrDeliveryNote": row["asn/dn #"].strip(),
            "FirstLineDesignation": row["first line designation"].strip().lower() == "true",
            "LineItemQuantity": int(quantity) if quantity is not None else "",
            "LineItemValueUSD": line_value if line_value is not None else "",
            "PackPriceUSD": pack_price if pack_price is not None else "",
            "UnitPriceUSD": unit_price if unit_price is not None else "",
            "WeightKg": weight if weight is not None else "",
            "FreightCostUSD": freight if freight is not None else "",
            "InsuranceUSD": insurance if insurance is not None else "",
            "DeliveryDelayDays": delay_days if delay_days is not None else "",
            "OrderToDeliveryDays": lead_time_days if lead_time_days is not None else "",
            "OnTimeFlag": delivered_date <= scheduled_date if delivered_date and scheduled_date else "",
            "LateFlag": delivered_date > scheduled_date if delivered_date and scheduled_date else "",
            "WeightAvailableFlag": weight is not None,
            "FreightCostAvailableFlag": freight is not None,
            "QualityIssueCount": len(issues),
            "QualityIssues": "; ".join(issues),
        })

    shipment_groups = {}
    for fact in facts:
        business_key = fact["ASNOrDeliveryNote"] or f"ROW-{fact['ShipmentLineKey']}"
        shipment_groups.setdefault(business_key, []).append(fact)

    shipment_rows = []
    for shipment_key_value, (business_key, lines) in enumerate(sorted(shipment_groups.items()), start=1):
        for line in lines:
            line["ShipmentKey"] = shipment_key_value

        def first_value(field):
            return next((line[field] for line in lines if line[field] != ""), "")

        def sum_values(field):
            return sum(float(line[field]) for line in lines if line[field] != "")

        def max_value(field):
            values = [float(line[field]) for line in lines if line[field] != ""]
            return max(values) if values else ""

        attribute_fields = [
            "ProjectKey", "CountryKey", "VendorKey", "ManufacturingSiteKey", "ShippingMethodKey",
            "OrderDateKey", "ScheduledDeliveryDateKey", "ActualDeliveryDateKey", "DeliveryRecordedDateKey",
            "PurchaseOrderNumber", "OnTimeFlag", "LateFlag", "DeliveryDelayDays", "OrderToDeliveryDays",
        ]
        conflicts = sum(len({line[field] for line in lines if line[field] != ""}) > 1 for field in attribute_fields)
        shipment_rows.append({
            "ShipmentKey": shipment_key_value,
            "ASNOrDeliveryNote": business_key,
            "ProjectKey": first_value("ProjectKey"),
            "CountryKey": first_value("CountryKey"),
            "VendorKey": first_value("VendorKey"),
            "ManufacturingSiteKey": first_value("ManufacturingSiteKey"),
            "ShippingMethodKey": first_value("ShippingMethodKey"),
            "OrderDateKey": first_value("OrderDateKey"),
            "ScheduledDeliveryDateKey": first_value("ScheduledDeliveryDateKey"),
            "ActualDeliveryDateKey": first_value("ActualDeliveryDateKey"),
            "DeliveryRecordedDateKey": first_value("DeliveryRecordedDateKey"),
            "PurchaseOrderNumber": first_value("PurchaseOrderNumber"),
            "ShipmentLineCount": len(lines),
            "LineItemQuantity": int(sum_values("LineItemQuantity")),
            "LineItemValueUSD": round(sum_values("LineItemValueUSD"), 2),
            "InsuranceUSD": round(sum_values("InsuranceUSD"), 2),
            "WeightKg": max_value("WeightKg"),
            "FreightCostUSD": max_value("FreightCostUSD"),
            "DeliveryDelayDays": first_value("DeliveryDelayDays"),
            "OrderToDeliveryDays": first_value("OrderToDeliveryDays"),
            "OnTimeFlag": first_value("OnTimeFlag"),
            "LateFlag": first_value("LateFlag"),
            "FirstLineDesignation": any(line["FirstLineDesignation"] for line in lines),
            "AttributeConflictCount": conflicts,
            "QualityIssueCount": sum(line["QualityIssueCount"] for line in lines),
        })

    min_date, max_date = min(valid_dates), max(valid_dates)
    date_rows = []
    current = min_date
    while current <= max_date:
        date_rows.append({
            "DateKey": int(current.strftime("%Y%m%d")), "Date": current.isoformat(),
            "Year": current.year, "Quarter": f"Q{((current.month - 1) // 3) + 1}",
            "MonthNumber": current.month, "MonthName": current.strftime("%B"),
            "YearMonth": current.strftime("%Y-%m"), "WeekNumber": int(current.strftime("%W")) + 1,
        })
        current += timedelta(days=1)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    tables = {
        "DimDate.csv": date_rows,
        "DimCountry.csv": country_rows,
        "DimVendor.csv": vendor_rows,
        "DimProject.csv": project_rows,
        "DimManufacturingSite.csv": site_rows,
        "DimShippingMethod.csv": shipping_rows,
        "DimProduct.csv": product_rows,
        "FactShipments.csv": shipment_rows,
        "FactShipmentLines.csv": facts,
    }
    for filename, records in tables.items():
        write_csv(OUTPUT / filename, records)

    source_sha256 = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    quality_report = {
        "source": {
            "title": "Supply Chain Shipment Pricing Data",
            "publisher": "U.S. Agency for International Development",
            "original_portal_id": "a3rc-nmf6",
            "catalog_url": "https://catalog.data.gov/dataset/supply-chain-shipment-pricing-dataset",
            "mirror_repository": "https://github.com/UmbertoFasci/Supply-Chain-Pricing-USAID",
            "mirror_file_sha": "f65bdd023f4c816990690c50847ca2cb82d51c52",
            "local_sha256": source_sha256,
            "downloaded_on": "2026-10-06",
        },
        "raw_rows": len(raw_rows),
        "raw_columns": len(raw_rows[0]),
        "date_range": [min_date.isoformat(), max_date.isoformat()],
        "output_rows": {filename: len(records) for filename, records in tables.items()},
        "quality_issues": dict(sorted(issue_counter.items())),
        "eligible_delivery_rows": sum(bool(row["OnTimeFlag"] != "") for row in facts),
        "eligible_delivery_shipments": sum(bool(row["OnTimeFlag"] != "") for row in shipment_rows),
        "eligible_freight_rows": sum(row["FreightCostAvailableFlag"] for row in facts),
        "eligible_weight_rows": sum(row["WeightAvailableFlag"] for row in facts),
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "usaid_data_quality.json").write_text(json.dumps(quality_report, indent=2), encoding="utf-8")
    print(json.dumps(quality_report, indent=2))


if __name__ == "__main__":
    main()
