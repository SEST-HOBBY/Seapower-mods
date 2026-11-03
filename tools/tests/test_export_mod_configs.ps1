<#
.SYNOPSIS
    Windows PowerShell 5.1 regression: new Workshop ID and 0/1/N file counts.
.DESCRIPTION
    Runs the real export script against a disposable fake Workshop installation.
    Never touches Steam, the current repo's mods-source or any live game file.
#>
[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$root = Join-Path ([IO.Path]::GetTempPath()) ("SEST-export-test-" + [guid]::NewGuid().ToString("N"))
$tools = Join-Path $root "tools"
$dest = Join-Path $root "mods-source"
$workshop = Join-Path $root "steamapps\workshop\content\1286220"
$data = Join-Path $root "data"
try {
    foreach ($dir in @((Join-Path $tools "lib"), $dest, $workshop, $data)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Copy-Item -LiteralPath (Join-Path $repo "tools\export-mod-configs.ps1") -Destination $tools
    Copy-Item -LiteralPath (Join-Path $repo "tools\lib\common.ps1") -Destination (Join-Path $tools "lib")
    [IO.File]::WriteAllText((Join-Path $data "mod-fingerprints.json"),
        '{"mods":{"3812454152":{"fingerprint":"old-mod-hash"}}}')

    foreach ($entry in @(
        @("3812454152","Euromod-HD Hyundai Export Ships Mod"),
        @("3819427362","Contact Log"),
        @("3812461539","SEST Integration Pack")
    )) {
        $folder = Join-Path $workshop $entry[0]
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $folder "_info.ini"), ("Name=" + $entry[1]))
        [IO.File]::WriteAllText((Join-Path $folder "settings.ini"),
            ("[Mod]" + [Environment]::NewLine + "Enabled=True"))
    }

    $report = Join-Path $root "workshop-updates.txt"
    & (Join-Path $tools "export-mod-configs.ps1") -WorkshopContentDir $workshop -CheckUpdates -ReportPath $report
    if (!(Test-Path -LiteralPath $report)) {
        throw "Read-only update report not created"
    }
    $text = Get-Content -LiteralPath $report -Raw
    if (!$text.Contains("3819427362  Contact Log")) {
        throw "A newly subscribed Workshop ID was not reported as NEW"
    }
    if (!$text.Contains("3812454152  Euromod-HD Hyundai Export Ships Mod")) {
        throw "Existing Workshop mod content change was not reported as UPDATED"
    }
    if ($text.Contains("3812461539  SEST Integration Pack")) {
        throw "The published SEST Workshop item was counted as an upstream update"
    }
    Write-Host "PASS: read-only update comparison with missing baseline property" -ForegroundColor Green

    & (Join-Path $tools "export-mod-configs.ps1") -WorkshopContentDir $workshop -DestDir $dest -NoPrune
    $manifest = @(Import-Csv -LiteralPath (Join-Path $dest "_export-manifest.csv"))
    if ($manifest.Count -ne 2) {
        throw "Expected exactly 2 third-party Workshop mods; found $($manifest.Count)"
    }
    foreach ($id in @("3812454152", "3819427362")) {
        if (!(Test-Path -LiteralPath (Join-Path $dest "$id\_info.ini"))) {
            throw "Missing exported mod $id"
        }
    }
    if (Test-Path -LiteralPath (Join-Path $dest "3812461539")) {
        throw "The SEST Workshop item was exported into its own source"
    }
    Write-Host "PASS: complete export and manifest with 2 third-party mods and 1 skipped SEST item" -ForegroundColor Green

    # Zero upstream inputs must not trigger StrictMode .Count errors.
    Remove-Item -LiteralPath (Join-Path $workshop "3812454152") -Recurse -Force
    Remove-Item -LiteralPath (Join-Path $workshop "3819427362") -Recurse -Force
    & (Join-Path $tools "export-mod-configs.ps1") -WorkshopContentDir $workshop -DestDir $dest -NoPrune
    $empty = @(Import-Csv -LiteralPath (Join-Path $dest "_export-manifest.csv"))
    if ($empty.Count -ne 0) { throw "Expected empty upstream manifest" }
    Write-Host "PASS: empty upstream Workshop export" -ForegroundColor Green
    Write-Host "all checks passed (export-mod-configs.ps1 under StrictMode)"
}
finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
