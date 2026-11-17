<#
.SYNOPSIS
    MNO ENV-01 Weather Lab: build, optionally install, or remove the local environmental playtest.
.DESCRIPTION
    Reads one INSTALLED vanilla mission (Hormuz or Breakthrough) from
    Sea Power_Data\StreamingAssets\original\missions and never writes there. Builds the
    MNO-Environmental-Playtest folder under this repository's integration\environment\out.
    With -Install, copies that folder to Sea Power_Data\StreamingAssets\content\ and refuses
    if the target exists. With -Uninstall, removes ONLY that content folder, and only if its
    PLAYTEST_META.json says it was made by this tool.
    No Steam upload, no Workshop change, no git operation, no change to MNO or R15 files.
    Written 18 Nov 2026; NOT YET RUN on Windows (the build container has no PowerShell).
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Mission Hormuz -MissionTime 10,0
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Mission Hormuz -MissionTime 10,0 -Install
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [string]$GameRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power',
    [ValidateSet('Hormuz', 'Breakthrough')][string]$Mission = 'Hormuz',
    [ValidateSet('front', 'procedural')][string]$Mode = 'front',
    [ValidateRange(30, 3600)][int]$Interval = 300,
    [string]$MissionTime = 'keep',
    [switch]$Install,
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$stream = Join-Path $GameRoot 'Sea Power_Data\StreamingAssets'
$target = Join-Path $stream 'content\MNO-Environmental-Playtest'
$outRoot = Join-Path $here 'out'
$built = Join-Path $outRoot 'MNO-Environmental-Playtest'

if (-not (Test-Path -LiteralPath $stream -PathType Container)) {
    throw "StreamingAssets not found under '$GameRoot'. Pass -GameRoot with the real Sea Power folder."
}
if (Get-Process -Name 'Sea Power' -ErrorAction SilentlyContinue) {
    throw 'Close Sea Power first.'
}

if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $target -PathType Container)) { Write-Host "Nothing to remove: $target"; return }
    $meta = Join-Path $target 'PLAYTEST_META.json'
    if (-not (Test-Path -LiteralPath $meta -PathType Leaf)) { throw "Refusing: $target has no PLAYTEST_META.json, so it was not made by this tool." }
    $m = Get-Content -LiteralPath $meta -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($m.status -notlike '*NOT TESTED IN GAME*' -or -not $m.rules_version) { throw "Refusing: $meta is not an MNO Weather Lab receipt." }
    Remove-Item -LiteralPath $target -Recurse -Force
    Write-Host "Removed $target (nothing else was touched)." -ForegroundColor Green
    return
}

$src = if ($Mission -eq 'Hormuz') { Join-Path $stream 'original\missions\NATO\Hormuz.ini' } else { Join-Path $stream 'original\missions\Warsaw Pact\Breakthrough.ini' }
if (-not (Test-Path -LiteralPath $src -PathType Leaf)) { throw "Installed vanilla mission not found: $src" }
$py = Get-Command py -ErrorAction SilentlyContinue
$pyArgs = @()
if ($py) { $pyExe = 'py'; $pyArgs = @('-3') } else { $pyExe = 'python' }
if (-not (Get-Command $pyExe -ErrorAction SilentlyContinue)) { throw 'Python 3 is required (py -3 or python).' }

if (Test-Path -LiteralPath $built) {
    throw "A previous build exists at $built. Inspect it, then delete that folder yourself to rebuild."
}
New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
$before = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
& $pyExe @pyArgs (Join-Path $here 'tools\build_weather_lab.py') --source $src --output $outRoot --mode $Mode --interval $Interval --mission-time $MissionTime --game-version 0.9.3
if ($LASTEXITCODE -ne 0) { throw "Builder refused or failed (exit $LASTEXITCODE). Nothing was installed." }
$after = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
if ($before -ne $after) { throw 'The vanilla source hash changed during the build. Stop and report this.' }
Write-Host "Vanilla source unchanged: $after" -ForegroundColor Green
$meta = Get-Content -LiteralPath (Join-Path $built 'PLAYTEST_META.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($meta.source_sha256 -ne $before) { throw 'Receipt hash does not match the source that was read.' }

if ($Install) {
    if (Test-Path -LiteralPath $target) { throw "Already installed: $target. Run with -Uninstall first; this script never overwrites." }
    Copy-Item -LiteralPath $built -Destination $target -Recurse
    $inst = Get-ChildItem -LiteralPath (Join-Path $target 'missions') -Filter '*.ini' | Select-Object -First 1
    $instHash = (Get-FileHash -LiteralPath $inst.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($instHash -ne $meta.mission_sha256) { throw 'Installed mission hash differs from the build receipt.' }
    Write-Host "Installed: $target" -ForegroundColor Cyan
    Write-Host "Mission SHA-256: $instHash"
    Write-Host 'Start Sea Power, enable "MNO - Environmental Playtest" in the Mod Manager if it is listed there, and open the Weather Lab scenario.'
} else {
    Write-Host "Built (not installed): $built" -ForegroundColor Cyan
    Write-Host 'Re-run with -Install to copy it into StreamingAssets\content.'
}
