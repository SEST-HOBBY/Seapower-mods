<#
.SYNOPSIS
    Download GCO's real weather pack (ERA5 recorded weather, 2025 onwards) on this PC. Resumable.
.DESCRIPTION
    Runs integration\environment\tools\build_gco_weather.py. Writes only under
    integration\environment\out\gco-weather (snapshots, manifest, raw responses). Nothing is
    installed into the game. Run once a day until it says COMPLETE; then -Package makes a ZIP in
    Downloads to send back. Written 18 Nov 2026; not yet run on Windows.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-GCO-WEATHER.ps1
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-GCO-WEATHER.ps1 -Package
#>
[CmdletBinding()]
param(
    [ValidateRange(1, 3)][int]$Years = 1,
    [switch]$Plan,
    [switch]$Package
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $here)
. (Join-Path $repoRoot 'tools\lib\common.ps1')
$cache = Join-Path $here 'out\gco-weather'

if ($Package) {
    if (-not (Test-Path -LiteralPath (Join-Path $cache 'manifest.json'))) { throw "Nothing downloaded yet in $cache" }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $zip = Join-Path ([Environment]::GetFolderPath('UserProfile')) "Downloads\MNO-GCO-weather-$stamp.zip"
    $items = @(Get-ChildItem -LiteralPath $cache -File | ForEach-Object { $_.FullName })
    Compress-Archive -Path $items -DestinationPath $zip
    Write-Host "Weather pack ZIP (snapshots + manifest, raw responses left out): $zip" -ForegroundColor Green
    return
}

$py = Get-Python
if (-not $py) { throw 'Python 3 is required (python.org installer; tick "Add to PATH").' }
$pyArgs = @($py.Pre) + @((Join-Path $here 'tools\build_gco_weather.py'), '--cache', $cache, '--years', "$Years")
if ($Plan) { $pyArgs += '--plan' }
& $py.Exe @pyArgs
switch ($LASTEXITCODE) {
    0 { if (-not $Plan) { Write-Host 'COMPLETE. Next: -Package, then send the ZIP.' -ForegroundColor Green } }
    3 { Write-Host 'Daily limit reached. Run the same command tomorrow; it continues where it stopped.' -ForegroundColor Yellow }
    default { throw "Weather download failed (exit $LASTEXITCODE). Copy the message above." }
}
