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
    [switch]$Status,
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
    $pyS = & { Set-StrictMode -Off; Get-Python }
    $tag = ''
    if ($pyS) {
        $sArgs = @($pyS.Pre) + @((Join-Path $here 'tools\build_gco_weather.py'), '--cache', $cache, '--years', "$Years", '--status')
        & $pyS.Exe @sArgs
        if ($LASTEXITCODE -ne 0) { $tag = '-PARTIAL'; Write-Host 'The pack is not complete yet; the ZIP is marked PARTIAL.' -ForegroundColor Yellow }
    }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $dl = $null
    try { $dl = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path } catch { }
    if (-not $dl -or -not (Test-Path -LiteralPath $dl)) { $dl = Join-Path $env:USERPROFILE 'Downloads'; New-Item -ItemType Directory -Force -Path $dl | Out-Null }
    $zip = Join-Path $dl "MNO-GCO-weather$tag-$stamp.zip"
    $items = @(Get-ChildItem -LiteralPath $cache -File | ForEach-Object { $_.FullName })
    Compress-Archive -Path $items -DestinationPath $zip
    Write-Host "Weather pack ZIP (snapshots + manifest, raw responses left out): $zip" -ForegroundColor Green
    return
}

$py = & { Set-StrictMode -Off; Get-Python }
if (-not $py) { throw 'Python 3.10 or newer is required (python.org installer; tick "Add to PATH").' }
$pyArgs = @($py.Pre) + @((Join-Path $here 'tools\build_gco_weather.py'), '--cache', $cache, '--years', "$Years")
if ($Plan) { $pyArgs += '--plan' }
if ($Status) { $pyArgs += '--status' }
& $py.Exe @pyArgs
switch ($LASTEXITCODE) {
    0 { if (-not $Plan -and -not $Status) { Write-Host 'COMPLETE. Next: -Package, then send the ZIP.' -ForegroundColor Green } }
    1 { if ($Status) { Write-Host 'Not complete yet: run the script again (tomorrow if it stopped at the daily limit).' } else { throw "Weather download failed (exit 1)." } }
    3 { Write-Host 'Daily limit reached. Run the same command tomorrow; it continues where it stopped.' -ForegroundColor Yellow }
    default { throw "Weather download failed (exit $LASTEXITCODE). Copy the message above." }
}
