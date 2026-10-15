// Create a text parameter named pProcessedFolder that points to data\processed.
(fileName as text, columnTypes as list) as table =>
let
    Source = Csv.Document(
        File.Contents(pProcessedFolder & "\\" & fileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, columnTypes, "en-US")
in
    TypedColumns
