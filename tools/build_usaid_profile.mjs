import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const outputs = path.join(root, "outputs");
const previews = path.join(outputs, "previews");
const processed = path.join(root, "data", "processed");
const kpis = JSON.parse(await fs.readFile(path.join(outputs, "usaid_baseline_kpis.json"), "utf8"));
const qualityReport = JSON.parse(await fs.readFile(path.join(outputs, "usaid_data_quality.json"), "utf8"));
const font = "Arial";
const color = {
  navy: "#16324F", blue: "#176B87", teal: "#2A9D8F", amber: "#E9C46A",
  red: "#C44536", ink: "#1F2933", muted: "#627D98", pale: "#F5F7FA",
  border: "#D9E2EC", white: "#FFFFFF",
};

const workbook = Workbook.create();
const overview = workbook.worksheets.add("Overview");
const countryMode = workbook.worksheets.add("Country and mode");
const quality = workbook.worksheets.add("Data quality");
const dictionary = workbook.worksheets.add("Data dictionary");
const source = workbook.worksheets.add("Source");

for (const sheet of [overview, countryMode, quality, dictionary, source]) sheet.showGridLines = false;

function title(sheet, heading, subtitle, width = "L") {
  sheet.getRange("A2").values = [[heading]];
  sheet.getRange("A2").format.font = { name: font, size: 16, bold: true, color: color.navy };
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange("A3").format.font = { name: font, size: 10, italic: true, color: color.muted };
  sheet.getRange(`A4:${width}4`).format.borders = { bottom: { style: "thin", color: color.blue } };
}

function header(range) {
  range.format = {
    fill: color.navy,
    font: { name: font, size: 10, bold: true, color: color.white },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { insideVertical: { style: "thin", color: color.white } },
  };
  range.format.rowHeight = 24;
}

function body(range) {
  range.format.font = { name: font, size: 10, color: color.ink };
  range.format.borders = { insideHorizontal: { style: "thin", color: color.border } };
  range.format.verticalAlignment = "center";
}

title(overview, "USAID supply chain data profile", "Historical health-commodity deliveries | 2006–2015 | shipment and line-item model", "Q");
overview.getRange("A6:B6").values = [["Metric", "Value"]];
header(overview.getRange("A6:B6"));
overview.getRange("A7:A14").values = [
  ["Shipments"], ["Shipment lines"], ["On-time delivery rate"], ["Late shipments"],
  ["Commodity value (USD)"], ["Freight cost (USD)"], ["Freight coverage"], ["Freight cost per kg"]
];
overview.getRange("B7:B14").formulas = [
  ["=SUM(G7:G16)"], ["=SUM(H7:H16)"], ["=1-SUM(I7:I16)/SUM(G7:G16)"], ["=SUM(I7:I16)"],
  ["=SUM(J7:J16)"], ["=SUM(N7:N11)"], [`=${kpis.freight_coverage_rate}`], [`=${kpis.freight_cost_per_kg}`]
];
body(overview.getRange("A7:B14"));
overview.getRange("B7:B8").format.numberFormat = "#,##0";
overview.getRange("B9:B9").format.numberFormat = "0.0%";
overview.getRange("B10:B10").format.numberFormat = "#,##0";
overview.getRange("B11:B12").format.numberFormat = '"$"#,##0';
overview.getRange("B13:B13").format.numberFormat = "0.0%";
overview.getRange("B14:B14").format.numberFormat = '"$"0.00';

overview.getRange("F6:J6").values = [["Year", "Shipments", "Shipment lines", "Late shipments", "Commodity value (USD)"]];
header(overview.getRange("F6:J6"));
const yearlyRows = kpis.yearly.filter(row => row.year !== "Unknown").map(row => [
  Number(row.year), row.shipments, row.shipment_lines, row.late, row.commodity_value_usd
]);
overview.getRange(`F7:J${6 + yearlyRows.length}`).values = yearlyRows;
body(overview.getRange(`F7:J${6 + yearlyRows.length}`));
overview.getRange(`F7:I${6 + yearlyRows.length}`).format.numberFormat = "#,##0";
overview.getRange(`J7:J${6 + yearlyRows.length}`).format.numberFormat = '"$"#,##0';

overview.getRange("M6:Q6").values = [["Mode", "Freight cost (USD)", "Weight (kg)", "Shipments", "On-time rate"]];
header(overview.getRange("M6:Q6"));
const modeRows = kpis.shipment_modes.map(row => [row.mode, row.freight_cost_usd, row.weight_kg, row.shipments, row.on_time_rate]);
overview.getRange(`M7:Q${6 + modeRows.length}`).values = modeRows;
body(overview.getRange(`M7:Q${6 + modeRows.length}`));
overview.getRange(`N7:N${6 + modeRows.length}`).format.numberFormat = '"$"#,##0';
overview.getRange(`O7:P${6 + modeRows.length}`).format.numberFormat = "#,##0";
overview.getRange(`Q7:Q${6 + modeRows.length}`).format.numberFormat = "0.0%";

const trendChart = overview.charts.add("line", [overview.getRange(`F6:F${6 + yearlyRows.length}`), overview.getRange(`G6:G${6 + yearlyRows.length}`), overview.getRange(`I6:I${6 + yearlyRows.length}`)]);
trendChart.title = "Shipments and late shipments by year";
trendChart.titleTextStyle.typeface = font;
trendChart.legend = { position: "top", textStyle: { typeface: font } };
trendChart.xAxis = { axisType: "textAxis", textStyle: { typeface: font, fontSize: 9 } };
trendChart.yAxis = { numberFormatCode: "#,##0", numberFormatSourceLinked: false, textStyle: { typeface: font, fontSize: 9 } };
trendChart.setPosition("A17", "H31");
if (trendChart.series.items[0]) trendChart.series.items[0].line = { fill: color.blue, style: "solid", width: 2 };
if (trendChart.series.items[1]) trendChart.series.items[1].line = { fill: color.red, style: "solid", width: 2 };

title(countryMode, "Country and shipment-mode profile", "Counts use shipment grain; freight excludes nonnumeric source values", "J");
countryMode.getRange("A6:E6").values = [["Country", "Shipments", "Late shipments", "Commodity value (USD)", "Freight cost (USD)"]];
header(countryMode.getRange("A6:E6"));
const countryRows = kpis.top_countries_by_shipments.map(row => [row.country, row.shipments, row.late, row.commodity_value_usd, row.freight_cost_usd]);
countryMode.getRange(`A7:E${6 + countryRows.length}`).values = countryRows;
body(countryMode.getRange(`A7:E${6 + countryRows.length}`));
countryMode.getRange(`B7:C${6 + countryRows.length}`).format.numberFormat = "#,##0";
countryMode.getRange(`D7:E${6 + countryRows.length}`).format.numberFormat = '"$"#,##0';
countryMode.getRange("G6:J6").values = [["Shipment mode", "Shipments", "On-time rate", "Freight cost (USD)"]];
header(countryMode.getRange("G6:J6"));
countryMode.getRange(`G7:J${6 + modeRows.length}`).values = modeRows.map(row => [row[0], row[3], row[4], row[1]]);
body(countryMode.getRange(`G7:J${6 + modeRows.length}`));
countryMode.getRange(`H7:H${6 + modeRows.length}`).format.numberFormat = "#,##0";
countryMode.getRange(`I7:I${6 + modeRows.length}`).format.numberFormat = "0.0%";
countryMode.getRange(`J7:J${6 + modeRows.length}`).format.numberFormat = '"$"#,##0';
const countryChart = countryMode.charts.add("bar", [countryMode.getRange("A6:A16"), countryMode.getRange("B6:B16")]);
countryChart.title = "Top countries by shipment count";
countryChart.titleTextStyle.typeface = font;
countryChart.hasLegend = false;
countryChart.xAxis = { textStyle: { typeface: font, fontSize: 9 } };
countryChart.yAxis = { numberFormatCode: "#,##0", numberFormatSourceLinked: false, textStyle: { typeface: font, fontSize: 9 } };
countryChart.setPosition("A19", "H34");
if (countryChart.series.items[0]) countryChart.series.items[0].fill = color.blue;

title(quality, "Data quality and metric coverage", "Missing numeric values remain null and appear in coverage measures", "F");
quality.getRange("A6:C6").values = [["Check", "Count", "Treatment"]];
header(quality.getRange("A6:C6"));
const qualityRows = [
  ["Raw shipment lines", qualityReport.raw_rows, "Retained"],
  ["Distinct shipments", kpis.shipment_count, "Aggregated by ASN/delivery note"],
  ["Freight blank or nonnumeric", qualityReport.quality_issues["Freight cost not numeric"], "Null; excluded from freight measures"],
  ["Weight blank or nonnumeric", qualityReport.quality_issues["Weight not numeric"], "Null; excluded from weight measures"],
  ["Insurance missing", qualityReport.quality_issues["Insurance missing"], "Null; excluded from insurance totals"],
  ["Delivery-eligible shipments", qualityReport.eligible_delivery_shipments, "Included in on-time rate"],
];
quality.getRange("A7:C12").values = qualityRows;
body(quality.getRange("A7:C12"));
quality.getRange("B7:B12").format.numberFormat = "#,##0";
quality.getRange("A15:B15").values = [["Coverage", "Rate"]];
header(quality.getRange("A15:B15"));
quality.getRange("A16:B17").values = [["Freight coverage", kpis.freight_coverage_rate], ["Weight coverage", kpis.weight_coverage_rate]];
body(quality.getRange("A16:B17"));
quality.getRange("B16:B17").format.numberFormat = "0.0%";

title(dictionary, "Processed data dictionary", "Columns generated by the reproducible source-to-model pipeline", "C");
dictionary.getRange("A6:C6").values = [["Table", "Column", "Role"]];
header(dictionary.getRange("A6:C6"));
const files = (await fs.readdir(processed)).filter(name => name.endsWith(".csv")).sort();
const dictionaryRows = [];
for (const file of files) {
  const firstLine = (await fs.readFile(path.join(processed, file), "utf8")).split(/\r?\n/, 1)[0];
  for (const column of firstLine.split(",")) {
    let role = "Attribute";
    if (/Quantity|Value|Price|Cost|Weight|Days|Count$/.test(column)) role = "Measure input";
    if (/Flag|Issues|Mode|Group|Class|Designation/.test(column)) role = "Filter / quality";
    if (column.endsWith("Key")) role = "Key / relationship";
    if (column.endsWith("DateKey")) role = "Date relationship";
    dictionaryRows.push([file.replace(".csv", ""), column, role]);
  }
}
dictionary.getRange(`A7:C${6 + dictionaryRows.length}`).values = dictionaryRows;
body(dictionary.getRange(`A7:C${6 + dictionaryRows.length}`));
dictionary.tables.add(`A6:C${6 + dictionaryRows.length}`, true, "ProcessedDataDictionary").style = "TableStyleMedium2";
dictionary.freezePanes.freezeRows(6);

title(source, "Source and scope", "Public historical dataset with versioned download provenance", "D");
source.getRange("A6:B6").values = [["Field", "Value"]];
header(source.getRange("A6:B6"));
const sourceRows = [
  ["Dataset", qualityReport.source.title],
  ["Publisher", qualityReport.source.publisher],
  ["Original portal ID", qualityReport.source.original_portal_id],
  ["Coverage", `${qualityReport.date_range[0]} to ${qualityReport.date_range[1]}`],
  ["Raw records", qualityReport.raw_rows],
  ["Downloaded", qualityReport.source.downloaded_on],
  ["Local SHA-256", qualityReport.source.local_sha256],
  ["Data.gov catalog", qualityReport.source.catalog_url],
  ["Versioned mirror", qualityReport.source.mirror_repository],
  ["Mirror Git blob SHA", qualityReport.source.mirror_file_sha],
];
source.getRange("A7:B16").values = sourceRows;
body(source.getRange("A7:B16"));
source.getRange("B11:B11").format.numberFormat = "#,##0";
source.getRange("A19").values = [["Scope note"]];
source.getRange("A19").format.font = { name: font, size: 11, bold: true, color: color.navy };
source.getRange("A20").values = [["The report describes historical deliveries from 2006 through 2015. It does not measure current USAID performance."]];
source.getRange("A20").format.font = { name: font, size: 10, color: color.ink };

overview.getRange("A:B").format.columnWidth = 24;
overview.getRange("F:J").format.columnWidth = 18;
overview.getRange("M:Q").format.columnWidth = 18;
countryMode.getRange("A:J").format.autofitColumns();
countryMode.getRange("A:A").format.columnWidth = 22;
quality.getRange("A:C").format.autofitColumns();
quality.getRange("A:A").format.columnWidth = 34;
quality.getRange("C:C").format.columnWidth = 40;
dictionary.getRange("A:C").format.autofitColumns();
dictionary.getRange("A:A").format.columnWidth = 28;
dictionary.getRange("B:B").format.columnWidth = 30;
dictionary.getRange("C:C").format.columnWidth = 24;
source.getRange("A:B").format.autofitColumns();
source.getRange("A:A").format.columnWidth = 24;
source.getRange("B:B").format.columnWidth = 76;

workbook.recalculate();
await fs.mkdir(outputs, { recursive: true });
await fs.mkdir(previews, { recursive: true });
for (const sheetName of ["Overview", "Country and mode", "Data quality", "Data dictionary", "Source"]) {
  const image = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(path.join(previews, `${sheetName.replaceAll(" ", "_")}.png`), new Uint8Array(await image.arrayBuffer()));
}
const check = await workbook.inspect({ kind: "table", range: "Overview!A1:Q31", include: "values,formulas", tableMaxRows: 31, tableMaxCols: 17 });
await fs.writeFile(path.join(outputs, "usaid_profile_inspect.ndjson"), check.ndjson, "utf8");
const errors = await workbook.inspect({
  kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan",
});
await fs.writeFile(path.join(outputs, "usaid_profile_errors.ndjson"), errors.ndjson, "utf8");
const output = await SpreadsheetFile.exportXlsx(workbook);
const target = path.join(outputs, "USAID_Supply_Chain_Data_Profile.xlsx");
await output.save(target);
console.log(JSON.stringify({ target, sheets: 5, dictionaryRows: dictionaryRows.length }, null, 2));
