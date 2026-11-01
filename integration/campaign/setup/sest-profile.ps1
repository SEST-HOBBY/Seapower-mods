<#
.SYNOPSIS
    Select the appropriate SEST compatibility profile for one Workshop pack.
.DESCRIPTION
    Read-only; examines the actual Seapower-Scripts.dll SHA256 rather than
    relying on 0.8.7 text, which is identical on the stable and beta branch.
    One pack supports both profiles. A runtime DLL is never silently replaced.
.EXAMPLE
    .\sest-profile.ps1 -GameDir "C:\Program Files (x86)\Steam\steamapps\common\Sea Power"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$GameDir,
    [string]$PackDir = "",
    [ValidateSet("Auto","Beta","Stable")][string]$Mode = "Auto"
)
$ErrorActionPreference = "Stop"
$stable = "eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd"
$beta = "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62"
$gameDll = Join-Path $GameDir "Sea Power_Data\Managed\Seapower-Scripts.dll"
$legacy = Join-Path $GameDir "BepInEx\plugins\SEST.BetaAnchorBootstrap.dll"
$experimental = Join-Path $GameDir "BepInEx\plugins\SEST.BetaSafeBootstrap.dll"

if (!(Test-Path -LiteralPath $gameDll -PathType Leaf)) {
    Write-Host "[SEST profile] Game assembly missing. Installation not verified." -ForegroundColor Red
    exit 2
}
$gameHash = (Get-FileHash -LiteralPath $gameDll -Algorithm SHA256).Hash.ToLowerInvariant()
$detected = "Unknown"
if ($gameHash -eq $stable) { $detected = "Stable" }
if ($gameHash -eq $beta) { $detected = "Beta" }
if ($Mode -ne "Auto" -and $Mode -ne $detected) {
    Write-Host "[SEST profile] Requested $Mode but installed game is $detected; refusing to force compatibility." -ForegroundColor Red
    exit 2
}
Write-Host ""
Write-Host "SEST INTEGRATION PACK - SINGLE MOD, DUAL GAME PROFILES" -ForegroundColor Cyan
Write-Host "Game assembly SHA256: $gameHash"
Write-Host "Detected profile: $detected"
Write-Host "Primary development target: Beta 0.8.7 Build 261026"
Write-Host "Also supported: Stable 0.8.7 Build 261021"
if (Test-Path -LiteralPath $legacy -PathType Leaf) {
    Write-Host "[BLOCKED] Unsafe experimental PR #53 bootstrap is still installed:" -ForegroundColor Red
    Write-Host "  $legacy"
    Write-Host "Remove it with integration\beta-bootstrap\test.ps1 -Action Remove before running SETUP."
    exit 3
}
if ($detected -eq "Stable") {
    Write-Host "[Stable] SEST Runtime 1.5.0 and UI Follow-up 1.4.2 may activate when their other exact dependency hashes match." -ForegroundColor Green
    Write-Host "[Stable] Existing campaign, cost and UI behavior preserved; additional UI bridges remain version gated."
    if (Test-Path -LiteralPath $experimental) {
        Write-Host "[WARN] Separate beta test plugin detected; it should not be needed on stable." -ForegroundColor Yellow
    }
}
elseif ($detected -eq "Beta") {
    Write-Host "[Beta] Data campaigns and Workshop list remain available; runtime code compatibility is not yet validated." -ForegroundColor Yellow
    Write-Host "[Beta] Runtime 1.5.0 and UI Follow-up 1.4.2 intentionally remain inactive under their SHA256 guards."
    Write-Host "[Beta] Anchor Chain preloader from the Workshop cannot reliably locate its chainloader in Build 261026."
    Write-Host "[Beta] The separate bounded Anchor Chain fork is a test candidate, not yet part of this public pack."
    if (Test-Path -LiteralPath $experimental) {
        Write-Host "[WARN] Inert-first beta test bootstrap is installed. Do not enable it without a clean probe and review." -ForegroundColor Yellow
    }
}
else {
    Write-Host "[UNVERIFIED] Unknown game assembly hash. Do not assume compatibility with a future Steam build." -ForegroundColor Red
    Write-Host "The pack's static data may load, but SEST does not claim that its plugins or missions work on this build."
    exit 2
}
if ($PackDir) { Write-Host "SEST pack: $PackDir" }
Write-Host "No files changed by profile detection."
exit 0
