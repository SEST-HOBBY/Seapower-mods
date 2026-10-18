<#
.SYNOPSIS
    tools\export-mod-configs.ps1 -CheckUpdates on a synthetic workshop
    content folder: SEST's own item (3812461539) is skipped, a fresh
    subscription and an updated mod are reported, and -ReportPath writes the
    report itself as UTF-8 without a byte-order mark, a Chinese name intact.

.DESCRIPTION
    The baseline is the repository's own data\mod-fingerprints.json, so
    3380210757 (Anchor Chain) with made-up content reads as UPDATED and an
    id of 100 as NEW. -DestDir points at a scratch folder because the script
    creates its destination before the check. Exit code 1 on any failed
    check.

        pwsh -File tools/tests/test_export_check_updates.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$export = Join-Path (Split-Path -Parent $PSScriptRoot) "export-mod-configs.ps1"
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("sest-export-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$failed = 0
$utf8 = New-Object Text.UTF8Encoding($false)
$chinese = [char]0x4F0A + [char]0x65AF + [char]0x574E + [char]0x5FB7 + [char]0x5C14   # the Iskander mod's name

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}

try {
    $ws = Join-Path $root "content"
    foreach ($pair in @(@("3812461539", "SEST Integration Pack"), @("100", $chinese), @("3380210757", "Anchor Chain"))) {
        $d = Join-Path $ws $pair[0]
        New-Item -ItemType Directory -Force -Path $d | Out-Null
        [IO.File]::WriteAllText((Join-Path $d "_info.ini"), "[Language_en]`r`nName=$($pair[1])`r`n", $utf8)
    }
    $dest = Join-Path $root "dest"
    $reportDir = Join-Path $root "snapshot"
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
    $report = Join-Path $reportDir "workshop-updates.txt"

    $out = New-Object System.Collections.Generic.List[string]
    try { & $export -CheckUpdates -WorkshopContentDir $ws -DestDir $dest -ReportPath $report *>&1 | ForEach-Object { $out.Add("$_") } }
    catch { $out.Add("ERROR: $($_.Exception.Message)") }
    $console = $out -join "`n"
    Check (-not ($console -match "ERROR:")) "ran without error ($(($out | Where-Object { $_ -match 'ERROR' }) -join ' '))"
    Check (Test-Path -LiteralPath $report) "the report file exists"
    $bytes = [IO.File]::ReadAllBytes($report)
    Check (-not ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)) "no byte-order mark"
    $text = $utf8.GetString($bytes)
    Check ($text.Contains("  100  $chinese")) "the Chinese name is intact in the report"
    Check ($text -match "skipped, SEST's own Workshop item: 3812461539") "SEST's own item reported as skipped"
    Check (-not ($text -match "(?m)^  3812461539  ")) "SEST's own item is in no list"
    Check ($text -match "(?m)^NEW subscriptions" -and $text -match "(?m)^  100  ") "the fresh subscription is listed as NEW"
    Check ($text -match "(?m)^UPDATED by their authors" -and $text -match "(?m)^  3380210757  Anchor Chain") "the changed mod is listed as UPDATED"
    Check ($text -match "(?m)^  workshop : ") "the locate lines are in the report"
    Check ($console -match "report written: ") "the console says where the report went"
    # With -WorkshopContentDir given the script prints no locate lines (it
    # does on auto-detection); either way they are not printed twice.
    Check (@($console -split "`n" | Where-Object { $_ -match "^  workshop : " }).Count -le 1) "the locate line is not printed twice"
    Check (($console -split "`n" | Where-Object { $_ -match "NEW subscriptions" }).Count -eq 1) "the report lines are printed once each"
    Check (-not (Test-Path -LiteralPath (Join-Path $dest "100"))) "nothing was exported in check mode"
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
