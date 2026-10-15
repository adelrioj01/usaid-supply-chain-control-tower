let
    Source = fnLoadProcessedCsv(
        "FactShipmentLines.csv",
        {
            {"ShipmentLineKey", Int64.Type}, {"SourceRowNumber", Int64.Type},
            {"ProjectKey", Int64.Type}, {"CountryKey", Int64.Type}, {"VendorKey", Int64.Type},
            {"ProductKey", Int64.Type}, {"ManufacturingSiteKey", Int64.Type},
            {"ShippingMethodKey", Int64.Type}, {"OrderDateKey", Int64.Type},
            {"ScheduledDeliveryDateKey", Int64.Type}, {"ActualDeliveryDateKey", Int64.Type},
            {"DeliveryRecordedDateKey", Int64.Type}, {"PurchaseOrderNumber", type text},
            {"ASNOrDeliveryNote", type text}, {"FirstLineDesignation", type logical},
            {"LineItemQuantity", Int64.Type}, {"LineItemValueUSD", Currency.Type},
            {"PackPriceUSD", Currency.Type}, {"UnitPriceUSD", Currency.Type},
            {"WeightKg", type number}, {"FreightCostUSD", Currency.Type},
            {"InsuranceUSD", Currency.Type}, {"DeliveryDelayDays", Int64.Type},
            {"OrderToDeliveryDays", Int64.Type}, {"OnTimeFlag", type logical},
            {"LateFlag", type logical}, {"WeightAvailableFlag", type logical},
            {"FreightCostAvailableFlag", type logical}, {"QualityIssueCount", Int64.Type},
            {"QualityIssues", type text}, {"ShipmentKey", Int64.Type}
        }
    )
in
    Source
