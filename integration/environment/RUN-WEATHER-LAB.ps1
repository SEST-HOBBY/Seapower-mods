<#
.SYNOPSIS
    MNO ENV-01 Weather Lab: build, install, remove, and collect results. One command for a quick test.
.DESCRIPTION
    Reads one INSTALLED vanilla mission (Hormuz or Breakthrough) from
    StreamingAssets\original\missions and never writes there. Builds a copy whose weather
    changes in eight stages, under integration\environment\out\<mission>-<time>\.
    -Install copies that ONE .ini into StreamingAssets\user\missions\user_missions, the
    folder the game lists player missions from (the same folder tools\refresh-mission.ps1
    uses). It refuses to overwrite a file of the same name.
    -Uninstall removes that one file, and only if its SHA-256 matches a build receipt here.
    -CollectLogs zips Player.log, BepInEx\LogOutput.log and the receipt into Downloads.
    No Steam upload, no Workshop change, no git operation, no change to MNO or R15 files.
    Written 18 Nov 2026; not yet run on Windows (the build container has no PowerShell).
.EXAMPLE
    # Quick test: 8 stages one minute apart, 10:00 start, built and installed in one go
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick
.EXAMPLE
    # Real weather: the ERA5 record at Hormuz's own map centre and date (21 Jul 1987), one real hour per minute
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick -RealWeather
.EXAMPLE
    # Today's ECMWF forecast at the same place
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick -Forecast
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -CollectLogs
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir = '',
    [ValidateSet('Hormuz', 'Breakthrough')][string]$Mission = 'Hormuz',
    [ValidateSet('front', 'procedural', 'real')][string]$Mode = 'front',
    [ValidateRange(30, 3600)][int]$Interval = 300,
    [string]$MissionTime = 'keep',
    [switch]$Quick,
    [switch]$RealWeather,
    [switch]$Forecast,
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$CollectLogs
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $here)
. (Join-Path $repoRoot 'tools\lib\common.ps1')

if ($RealWeather -and $Forecast) { throw 'Use -RealWeather (recorded, on the mission date) or -Forecast (today), not both.' }
if ($RealWeather -or $Forecast) { $Mode = 'real' }
if ($Quick) {
    $Install = $true
    if (-not $PSBoundParameters.ContainsKey('Interval')) { $Interval = 60 }
    if (-not $PSBoundParameters.ContainsKey('MissionTime')) { $MissionTime = '10,0' }
}

# The shared helpers were written without StrictMode; run them with it off so their fallbacks work.
if (-not $StreamingAssetsDir) { $StreamingAssetsDir = & { Set-StrictMode -Off; Find-StreamingAssets } }
if (-not $StreamingAssetsDir -or -not (Test-Path -LiteralPath $StreamingAssetsDir -PathType Container)) {
    throw "Sea Power's StreamingAssets was not found. Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'"
}
$gameDir = Split-Path -Parent (Split-Path -Parent $StreamingAssetsDir)
$userMissions = Join-Path $StreamingAssetsDir 'user\missions\user_missions'
$outRoot = Join-Path $here 'out'
$fileName = "MNO Weather Lab - $Mission.ini"
$installed = Join-Path $userMissions $fileName

function Get-Receipts {
    if (-not (Test-Path -LiteralPath $outRoot)) { return @() }
    return @(Get-ChildItem -LiteralPath $outRoot -Filter 'PLAYTEST_META.json' -Recurse -File |
        ForEach-Object { $m = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json; $m | Add-Member -NotePropertyName ReceiptPath -NotePropertyValue $_.FullName -PassThru })
}

function Get-DownloadsFolder {
    # The real Downloads folder (it may have been moved or redirected), else the profile's.
    try {
        $p = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
        if ($p -and (Test-Path -LiteralPath $p)) { return $p }
    } catch { }
    $fallback = Join-Path $env:USERPROFILE 'Downloads'
    New-Item -ItemType Directory -Force -Path $fallback | Out-Null
    return $fallback
}

if ($CollectLogs) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $stage = Join-Path $env:TEMP "MNO-WeatherLab-results-$stamp"
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    $sources = @(
        (Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power\Player.log'),
        (Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power\Player-prev.log'),
        (Join-Path $gameDir 'BepInEx\LogOutput.log')
    )
    foreach ($s in $sources) { if (Test-Path -LiteralPath $s) { Copy-Item -LiteralPath $s -Destination $stage } }
    $receipts = @(Get-Receipts)
    $lines = @("Weather Lab results $stamp", '')
    $matched = @()
    foreach ($name in @('MNO Weather Lab - Hormuz.ini', 'MNO Weather Lab - Breakthrough.ini')) {
        $p = Join-Path $userMissions $name
        if (-not (Test-Path -LiteralPath $p)) { $lines += "$name : not installed"; continue }
        $h = (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
        $r = $receipts | Where-Object { $_.mission_sha256 -eq $h } | Select-Object -First 1
        if ($r) { $matched += $r; $lines += "$name : installed, matches receipt $($r.ReceiptPath) (mode $($r.mode))" }
        else { $lines += "$name : installed, sha256 $h matches NO build receipt here" }
    }
    if ($matched.Count -eq 0) {
        $lines += 'No installed file matches a build receipt here, so no stage list is given; reply with what you saw.'
    }
    foreach ($r in $matched) {
        Copy-Item -LiteralPath $r.ReceiptPath -Destination (Join-Path $stage ("PLAYTEST_META-" + (Split-Path -Leaf (Split-Path -Parent (Split-Path -Parent $r.ReceiptPath))) + ".json"))
        $prefix = if ($r.mission -like '*Breakthrough*') { 'B' } else { 'H' }
        $lines += '', "Stages expected for $($r.mission) (write PASS / FAIL / NOT SEEN after each; reply with e.g. $prefix-W4):"
        $k = 1
        foreach ($st in $r.stages) {
            $wx = @()
            if ($st.rain) { $wx += 'rain' }
            if ($st.fog) { $wx += 'fog' }
            if ($st.thunderstorm) { $wx += 'thunder' }
            if ($st.snow) { $wx += 'snow' }
            if ($wx.Count -eq 0) { $wx = @('dry') }
            $min = [math]::Round($st.at_s / 60, 1)
            $lines += ("{0}-W{1} at {2} min: {3}, sea state {4}, {5}:" -f $prefix, $k, $min, $st.clouds, $st.sea_state, ($wx -join '+'))
            $k++
        }
    }
    $lines += '', "W9 the mission's own scripted weather changes did not happen:", 'W10 objectives and end of mission worked:',
        'W11 the normal mission afterwards has its own weather:', 'Wave height you saw at the roughest stage (m):'
    $lines | Set-Content -LiteralPath (Join-Path $stage 'RESULTS.txt') -Encoding UTF8
    $zip = Join-Path (Get-DownloadsFolder) "MNO-WeatherLab-results-$stamp.zip"
    try {
        Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -ErrorAction Stop
    } catch {
        Write-Warning "Could not write $zip ($($_.Exception.Message)). The files are in $stage"
        return
    }
    # A copy of RESULTS.txt beside the ZIP: Explorer cannot save edits back into a ZIP.
    $note = Join-Path (Get-DownloadsFolder) "MNO-WeatherLab-results-$stamp-RESULTS.txt"
    Copy-Item -LiteralPath (Join-Path $stage 'RESULTS.txt') -Destination $note
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Results ZIP: $zip" -ForegroundColor Green
    Write-Host "Fill in $note in Notepad (or just reply with the W numbers that failed) and send both."
    return
}

if (Test-SeaPowerRunning) { throw 'Close Sea Power first.' }

if ($Uninstall) {
    $any = $false
    foreach ($name in @('MNO Weather Lab - Hormuz.ini', 'MNO Weather Lab - Breakthrough.ini')) {
        $p = Join-Path $userMissions $name
        if (-not (Test-Path -LiteralPath $p)) { continue }
        $any = $true
        $h = (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
        $match = Get-Receipts | Where-Object { $_.mission_sha256 -eq $h } | Select-Object -First 1
        if (-not $match) { Write-Warning "Left in place: $p does not match any build receipt in $outRoot (edited, or not made here)."; continue }
        Remove-Item -LiteralPath $p -Force
        Write-Host "Removed $p" -ForegroundColor Green
    }
    if (-not $any) { Write-Host "Nothing installed in $userMissions" }
    return
}

$src = if ($Mission -eq 'Hormuz') { Join-Path $StreamingAssetsDir 'original\missions\NATO\Hormuz.ini' } else { Join-Path $StreamingAssetsDir 'original\missions\Warsaw Pact\Breakthrough.ini' }
if (-not (Test-Path -LiteralPath $src -PathType Leaf)) { throw "Installed vanilla mission not found: $src" }
$py = & { Set-StrictMode -Off; Get-Python }
if (-not $py) { throw 'Python 3.10 or newer is required (python.org installer; tick "Add to PATH").' }
if ($Install -and (Test-Path -LiteralPath $installed)) {
    throw "Already installed: $installed. Run with -Uninstall first; this script never overwrites."
}

$runDir = Join-Path $outRoot ("{0}-{1}" -f $Mission, (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$before = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
$pyArgs = @($py.Pre) + @((Join-Path $here 'tools\build_weather_lab.py'), '--source', $src, '--output', $runDir,
    '--mode', $Mode, '--interval', "$Interval", '--mission-time', $MissionTime, '--game-version', '0.9.3')
if ($Mode -eq 'real') {
    $src_ = if ($Forecast) { 'ifs' } else { 'era5' }
    $pyArgs += @('--real-source', $src_, '--raw-dir', (Join-Path $runDir 'raw'))
}
& $py.Exe @pyArgs
if ($LASTEXITCODE -ne 0) { throw "Builder refused or failed (exit $LASTEXITCODE). Nothing was installed." }
$after = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
if ($before -ne $after) { throw 'The vanilla source hash changed during the build. Stop and report this.' }
Write-Host "Vanilla source unchanged: $after" -ForegroundColor Green
$built = Join-Path $runDir 'MNO-Environmental-Playtest'
$meta = Get-Content -LiteralPath (Join-Path $built 'PLAYTEST_META.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($meta.source_sha256 -ne $before) { throw 'Receipt hash does not match the source that was read.' }
$builtIni = Join-Path $built "missions\$fileName"

if ($Install) {
    New-Item -ItemType Directory -Force -Path $userMissions | Out-Null
    Copy-Item -LiteralPath $builtIni -Destination $installed
    $instHash = (Get-FileHash -LiteralPath $installed -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($instHash -ne $meta.mission_sha256) { throw 'Installed mission hash differs from the build receipt.' }
    $minutes = [math]::Round($Interval * 7 / 60, 1)
    Write-Host ''
    Write-Host "Installed: $installed" -ForegroundColor Cyan
    Write-Host "In the game: open your custom/user missions, start 'MNO Weather Lab: $Mission'."
    if ($Mode -eq 'real') {
        Write-Host "Real weather: one real hour every $Interval s of mission time (data: Open-Meteo / ECMWF; see the mission description)."
    } else {
        Write-Host "Weather changes every $Interval s of mission time; all eight stages take $minutes min at 1x."
    }
    Write-Host 'After the test: -CollectLogs, then -Uninstall.'
} else {
    Write-Host "Built (not installed): $builtIni" -ForegroundColor Cyan
}
