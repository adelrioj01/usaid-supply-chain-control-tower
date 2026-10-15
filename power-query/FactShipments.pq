let
    Source = fnLoadProcessedCsv(
        "FactShipments.csv",
        {
            {"ShipmentKey", Int64.Type}, {"ASNOrDeliveryNote", type text},
            {"ProjectKey", Int64.Type}, {"CountryKey", Int64.Type}, {"VendorKey", Int64.Type},
            {"ManufacturingSiteKey", Int64.Type}, {"ShippingMethodKey", Int64.Type},
            {"OrderDateKey", Int64.Type}, {"ScheduledDeliveryDateKey", Int64.Type},
            {"ActualDeliveryDateKey", Int64.Type}, {"DeliveryRecordedDateKey", Int64.Type},
            {"PurchaseOrderNumber", type text}, {"ShipmentLineCount", Int64.Type},
            {"LineItemQuantity", Int64.Type}, {"LineItemValueUSD", Currency.Type},
            {"InsuranceUSD", Currency.Type}, {"WeightKg", type number},
            {"FreightCostUSD", Currency.Type}, {"DeliveryDelayDays", Int64.Type},
            {"OrderToDeliveryDays", Int64.Type}, {"OnTimeFlag", type logical},
            {"LateFlag", type logical}, {"FirstLineDesignation", type logical},
            {"AttributeConflictCount", Int64.Type}, {"QualityIssueCount", Int64.Type}
        }
    )
in
    Source
