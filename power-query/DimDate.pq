let
    Source = fnLoadProcessedCsv(
        "DimDate.csv",
        {
            {"DateKey", Int64.Type}, {"Date", type date}, {"Year", Int64.Type},
            {"Quarter", type text}, {"MonthNumber", Int64.Type}, {"MonthName", type text},
            {"YearMonth", type text}, {"WeekNumber", Int64.Type}
        }
    )
in
    Source
