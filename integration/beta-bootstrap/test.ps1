param(
    [ValidateSet("Install", "Report", "Remove")]
    [string]$Action = "Report",
    [string]$GameRoot = ""
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Beta-only smoke test. This script never overwrites game assemblies, SEST
# Runtime 1.5.0, existing plugins, or Workshop files. It installs/removes one
# uniquely named candidate plugin after verifying the hashes from the owner's
# successful Build 261026 compilation receipt.
if (!$GameRoot) {
    $GameRoot = Join-Path $env:SystemDrive "Program Files (x86)\Steam\steamapps\common\Sea Power"
}
$managed = Join-Path $GameRoot "Sea Power_Data\Managed"
$native = Join-Path $managed "Seapower-Scripts.dll"
$source = Join-Path $PSScriptRoot "out\SEST.BetaAnchorBootstrap.dll"
$dest = Join-Path $GameRoot "BepInEx\plugins\SEST.BetaAnchorBootstrap.dll"
$log = Join-Path $GameRoot "BepInEx\LogOutput.log"
$betaHash = "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62"
$legacyHash = "e2a029d6a33918227690e4f149197212154dee19f23b3618913f973cfc5ce72e"
$receiptPath = Join-Path $PSScriptRoot "out\build-receipt.json"
$receiptHash = $legacyHash
if (Test-Path -LiteralPath $receiptPath -PathType Leaf) {
    $receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
    if ($receipt.game_sha256 -ne $betaHash) { throw "Build receipt is for a different game build." }
    $receiptHash = [string]$receipt.dll_sha256
    $actualSourceHash = (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot "AnchorChainBetaBootstrap.cs") -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Action -eq "Install" -and $actualSourceHash -ne [string]$receipt.source_sha256) { throw "Build receipt source hash does not match current source. Rebuild first." }
}

function Read-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Require-GameClosed {
    if (Get-Process -Name "Sea Power", "SeaPower" -ErrorAction SilentlyContinue) {
        throw "Close Sea Power first. No files changed."
    }
}

if ($Action -eq "Install") {
    Require-GameClosed
    if (!(Test-Path -LiteralPath $native -PathType Leaf)) {
        throw "Sea Power managed assembly not found at $native"
    }
    if ((Read-Sha256 $native) -ne $betaHash) {
        throw "Not the inspected beta Build 261026. Refusing installation."
    }
    if (!(Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Compile the candidate first with integration\beta-bootstrap\build.ps1"
    }
    $candidateHash = Read-Sha256 $source
    if ($candidateHash -ne $receiptHash) {
        throw "Candidate DLL differs from the reviewed build receipt. Found: $candidateHash. No files changed."
    }
    if (Test-Path -LiteralPath $dest -PathType Leaf) {
        if ((Read-Sha256 $dest) -eq $receiptHash) {
            Write-Host "Bootstrap candidate is already installed." -ForegroundColor Yellow
            return
        }
        throw "Another SEST.BetaAnchorBootstrap.dll is present. Refusing to overwrite $dest"
    }
    $plugins = Split-Path -Parent $dest
    if (!(Test-Path -LiteralPath $plugins -PathType Container)) {
        throw "BepInEx plugins folder not found: $plugins"
    }
    Copy-Item -LiteralPath $source -Destination $dest -ErrorAction Stop
    if ((Read-Sha256 $dest) -ne $receiptHash) {
        Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
        throw "Copy hash verification failed; candidate removed."
    }
    Write-Host "BETA TEST PLUGIN INSTALLED" -ForegroundColor Green
    Write-Host "Only file added: $dest"
    Write-Host "Next: launch Sea Power beta, reach main menu, then quit."
    Write-Host "Then run this script with -Action Report."
    Write-Host "To undo: run this script with -Action Remove."
}
elseif ($Action -eq "Remove") {
    Require-GameClosed
    if (!(Test-Path -LiteralPath $dest -PathType Leaf)) {
        Write-Host "Nothing to remove. Candidate plugin is not installed."
        return
    }
    if ((Read-Sha256 $dest) -notin @($receiptHash, $legacyHash)) {
        throw "Installed file differs from known test candidates; refusing to remove: $dest"
    }
    Remove-Item -LiteralPath $dest -Force
    Write-Host "BETA TEST PLUGIN REMOVED" -ForegroundColor Green
    Write-Host "No other files were changed."
}
else {
    if (!(Test-Path -LiteralPath $log -PathType Leaf)) {
        throw "No BepInEx log at $log. Launch the game once, quit, then retry."
    }
    $info = Get-Item -LiteralPath $log
    Write-Host "BepInEx log: $log"
    Write-Host "Last written: $($info.LastWriteTime)"
    Write-Host "Candidate installed: $(Test-Path -LiteralPath $dest -PathType Leaf)"
    Write-Host ""
    Write-Host "BETA BOOTSTRAP / ANCHOR CHAIN DIAGNOSTICS" -ForegroundColor Cyan
    $patterns = @(
        "Chainloader started",
        "AnchorChain Preloader",
        "Could not find AnchorChain",
        "SEST Beta Anchor Chain Bootstrap",
        "Build 261026 verified",
        "Beta bootstrap",
        "Deferred Anchor Chain",
        "Loaded AnchorChain",
        "Anchor Chain setup failed",
        "Loaded plugin ",
        "Error loading plugin",
        "Error loading assembly",
        "FileManager discovery",
        "Probe tick=",
        "Steam Workshop",
        "Anchor Chain not ready",
        "Retry using"
    )
    $hits = @(
        Get-Content -LiteralPath $log -Tail 2000 |
            Select-String -Pattern $patterns
    )
    if ($hits.Count -eq 0) {
        Write-Host "No matching log entries. Paste the latest BepInEx log excerpt."
    }
    else {
        $hits | Select-Object -Last 80 | ForEach-Object { Write-Host $_.Line }
    }
    Write-Host ""
    Write-Host "The upstream early 'Could not find' line can remain in the log."
    Write-Host "Check for a later 'Deferred Anchor Chain LoadPlugins invoked' and upstream plugin-load lines."
}
