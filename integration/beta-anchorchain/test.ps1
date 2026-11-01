param(
    [ValidateSet("Stage", "Enable", "Disable", "Remove", "Report")]
    [string]$Action = "Report",
    [string]$GameRoot = ""
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Standalone beta test operations; no overwrites of Workshop, native DLLs or
# SEST Runtime 1.5.0. Stage is INERT. Enable requires a successful probe log.
if (!$GameRoot) {
    $GameRoot = Join-Path $env:SystemDrive "Program Files (x86)\Steam\steamapps\common\Sea Power"
}
$managed = Join-Path $GameRoot "Sea Power_Data\Managed"
$native = Join-Path $managed "Seapower-Scripts.dll"
$bepinex = Join-Path $GameRoot "BepInEx"
$plugins = Join-Path $bepinex "plugins"
$payloadDir = Join-Path $bepinex "config\SEST-BetaAnchorChain"
$loaderDest = Join-Path $payloadDir "AnchorChain.dll"
$hashDest = Join-Path $payloadDir "AnchorChain.sha256"
$receiptDest = Join-Path $payloadDir "SEST-stage-receipt.json"
$flag = Join-Path $payloadDir "enable.flag"
$bootDest = Join-Path $plugins "SEST.BetaSafeBootstrap.dll"
$legacy = Join-Path $plugins "SEST.BetaAnchorBootstrap.dll"
$log = Join-Path $bepinex "LogOutput.log"
$player = Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\Player.log"
$outDir = Join-Path $PSScriptRoot "out"
$outReceipt = Join-Path $outDir "build-receipt.json"
$knownBeta = "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62"

function Hash-File([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Game-Closed {
    if (Get-Process -Name "Sea Power", "SeaPower" -ErrorAction SilentlyContinue) {
        throw "Close Sea Power first. No files changed."
    }
}
function Require-Beta {
    if (!(Test-Path -LiteralPath $native -PathType Leaf)
        -or (Hash-File $native) -ne $knownBeta) {
        throw "This test supports only verified Sea Power beta Build 261026. No files changed."
    }
}
function Read-Stage-Receipt {
    if (!(Test-Path -LiteralPath $receiptDest -PathType Leaf)) {
        throw "No staged SEST receipt at $receiptDest. No files changed."
    }
    $r = Get-Content -LiteralPath $receiptDest -Raw | ConvertFrom-Json
    if ($r.target_game_sha256 -ne $knownBeta) { throw "Staged receipt targets a different build." }
    return $r
}
function Check-Staged([object]$r) {
    foreach ($p in @($bootDest, $loaderDest, $hashDest)) {
        if (!(Test-Path -LiteralPath $p -PathType Leaf)) {
            throw "Staged file missing: $p"
        }
    }
    if ((Hash-File $bootDest) -ne [string]$r.bootstrap_dll_sha256) {
        throw "Staged bootstrap hash differs from receipt. Refusing to modify it."
    }
    if ((Hash-File $loaderDest) -ne [string]$r.fork_dll_sha256) {
        throw "Staged AnchorChain.dll hash differs from receipt. Refusing to modify it."
    }
    if ((Get-Content -LiteralPath $hashDest -Raw).Trim().ToLowerInvariant() -ne [string]$r.fork_dll_sha256) {
        throw "Staged AnchorChain.sha256 differs from receipt. Refusing to modify it."
    }
}

if ($Action -eq "Stage") {
    Game-Closed
    Require-Beta
    if (Test-Path -LiteralPath $legacy -PathType Leaf) {
        throw "Old experimental PR #53 plugin is installed. Remove it first with the old test.ps1 -Action Remove."
    }
    if (!(Test-Path -LiteralPath $outReceipt -PathType Leaf)) {
        throw "Compile the safe loader first: integration\beta-anchorchain\build.ps1"
    }
    $r = Get-Content -LiteralPath $outReceipt -Raw | ConvertFrom-Json
    $fork = Join-Path $outDir "AnchorChain.dll"
    $boot = Join-Path $outDir "SEST.BetaSafeBootstrap.dll"
    foreach ($pair in @(@($fork, [string]$r.fork_dll_sha256),
                        @($boot, [string]$r.bootstrap_dll_sha256))) {
        if (!(Test-Path -LiteralPath $pair[0] -PathType Leaf)
            -or (Hash-File $pair[0]) -ne $pair[1]) {
            throw "Local compiled file differs from its build receipt: $($pair[0])"
        }
    }
    if ($r.target_game_sha256 -ne $knownBeta) {
        throw "Compiled payload is for a different build."
    }
    if (Test-Path -LiteralPath $flag -PathType Leaf) {
        throw "Found active enable.flag. Disable before staging."
    }
    foreach ($p in @($loaderDest, $bootDest, $hashDest, $receiptDest)) {
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            throw "Staged artifact already exists. Do not overwrite: $p"
        }
    }
    if (!(Test-Path -LiteralPath $plugins -PathType Container)) {
        throw "BepInEx plugins directory missing."
    }
    if (!(Test-Path -LiteralPath $payloadDir -PathType Container)) {
        New-Item -ItemType Directory -Path $payloadDir -Force | Out-Null
    }
    Copy-Item -LiteralPath $fork -Destination $loaderDest
    Copy-Item -LiteralPath $boot -Destination $bootDest
    Set-Content -LiteralPath $hashDest -Value ([string]$r.fork_dll_sha256) -Encoding ASCII
    Copy-Item -LiteralPath $outReceipt -Destination $receiptDest
    Check-Staged $r
    Write-Host "BETA SAFE ANCHOR CHAIN STAGED (INACTIVE)" -ForegroundColor Green
    Write-Host "No enable.flag was created. First game launch is diagnostics-only."
}
elseif ($Action -eq "Enable") {
    Game-Closed
    Require-Beta
    $r = Read-Stage-Receipt
    Check-Staged $r
    if (!(Test-Path -LiteralPath $log -PathType Leaf)) {
        throw "No BepInEx log; run the staged/inactive probe game launch first."
    }
    if (!(Select-String -LiteralPath $log -SimpleMatch "BETA SAFE BOOTSTRAP READY; enable=False" -Quiet)) {
        throw "Ready/inactive probe not confirmed in last BepInEx log. No files changed."
    }
    if (Test-Path -LiteralPath $flag -PathType Leaf) {
        if ((Get-Content -LiteralPath $flag -Raw).Trim() -eq "enable-beta-261026") {
            Write-Host "Bounded beta loader already enabled." -ForegroundColor Yellow
            return
        }
        throw "Unknown existing enable.flag. Refusing to overwrite."
    }
    Set-Content -LiteralPath $flag -Encoding ASCII -Value "enable-beta-261026"
    Write-Host "BOUNDED LOADER ENABLED FOR NEXT LAUNCH" -ForegroundColor Yellow
    Write-Host "This test can still expose other third-party mod incompatibilities."
    Write-Host "If game hangs, quit it and run test.ps1 -Action Disable (or Remove)."
}
elseif ($Action -eq "Disable") {
    Game-Closed
    if (!(Test-Path -LiteralPath $flag -PathType Leaf)) {
        Write-Host "Loader already inactive; no enable.flag."
        return
    }
    if ((Get-Content -LiteralPath $flag -Raw).Trim() -ne "enable-beta-261026") {
        throw "Unexpected enable.flag contents. No file removed."
    }
    Remove-Item -LiteralPath $flag -Force
    Write-Host "BOUNDED LOADER DISABLED. Bootstrap remains installed but inert." -ForegroundColor Green
}
elseif ($Action -eq "Remove") {
    Game-Closed
    if (Test-Path -LiteralPath $flag -PathType Leaf) {
        if ((Get-Content -LiteralPath $flag -Raw).Trim() -ne "enable-beta-261026") {
            throw "Unexpected enable.flag; refusing to remove any file."
        }
    }
    $r = Read-Stage-Receipt
    Check-Staged $r
    if (Test-Path -LiteralPath $flag -PathType Leaf) {
        Remove-Item -LiteralPath $flag -Force
    }
    foreach ($p in @($bootDest, $loaderDest, $hashDest, $receiptDest)) {
        Remove-Item -LiteralPath $p -Force
    }
    if ((Get-ChildItem -LiteralPath $payloadDir -Force | Measure-Object).Count -eq 0) {
        Remove-Item -LiteralPath $payloadDir -Force
    }
    Write-Host "BOUNDED BETA TEST REMOVED. No Workshop or native game DLLs altered." -ForegroundColor Green
}
else {
    Write-Host "Safe beta loader staged: $(Test-Path -LiteralPath $bootDest -PathType Leaf)"
    Write-Host "Bounded loader enabled: $(Test-Path -LiteralPath $flag -PathType Leaf)"
    Write-Host ""
    if (Test-Path -LiteralPath $log -PathType Leaf) {
        Write-Host "BepInEx: $((Get-Item -LiteralPath $log).LastWriteTime)"
        $patterns = @("SEST Beta Safe Anchor Chain", "Beta safe loader",
                      "Safe probe tick=", "BETA SAFE BOOTSTRAP READY",
                      "Starting bounded Anchor", "Bounded Anchor Chain",
                      "Bounded loader failed", "Aborting chainload",
                      "Error loading plugin", "AnchorChain Preloader")
        Get-Content -LiteralPath $log -Tail 2000 |
            Select-String -Pattern $patterns |
            Select-Object -Last 100 |
            ForEach-Object { Write-Host $_.Line }
    }
    if (Test-Path -LiteralPath $player -PathType Leaf) {
        Write-Host ""
        Write-Host "Unity Player.log: $((Get-Item -LiteralPath $player).LastWriteTime)"
        $tail = @(Get-Content -LiteralPath $player -Tail 5000)
        $sar = @($tail | Select-String -SimpleMatch "[AutomaticSAR] Loaded.").Count
        Write-Host "AutomaticSAR Loaded messages (last 5000 lines): $sar"
        $tail | Select-String -Pattern "Exception|Initialization failed|patch failed|inactive: uninspected" |
            Select-Object -Last 25 |
            ForEach-Object { Write-Host $_.Line }
    }
}
