param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot
try {
    & $Python "src/prepare_usaid_data.py"
    & $Python "tests/test_usaid_data.py"
    & $Python "src/analyze_usaid.py"
}
finally {
    Pop-Location
}
