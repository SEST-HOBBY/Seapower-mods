<#
.SYNOPSIS
    Install (or update) every SEST pack into Sea Power's StreamingAssets folder.

.DESCRIPTION
    Auto-detects the Sea Power install the same way export-mod-configs.ps1 does
    (Steam library manifests — no hardcoded paths), finds StreamingAssets, and
    copies every SEST pack folder found under this repo's integration\ directories
    into it. Safe to re-run any time: existing copies are overwritten in place,
    which is also how you take updates after a git pull.

.EXAMPLE
    # From the repo root, in PowerShell:
    git pull
    powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1

    # If auto-detection fails, point it at StreamingAssets directly:
    powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -StreamingAssetsDir "D:\...\Sea Power_Data\StreamingAssets"
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir
)

$ErrorActionPreference = "Stop"

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
. (Join-Path $scriptDir "lib\common.ps1")

# Discovered, not listed. A hardcoded roster is one more place to forget a new
# pack - and a pack that is never installed fails exactly like one that is
# installed but outranked: silently, with the game showing the unmodded unit.
$Packs = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot "integration") -Directory |
    ForEach-Object { Get-ChildItem -LiteralPath $_.FullName -Directory -Filter "SEST_*" } |
    ForEach-Object { $_.FullName.Substring($repoRoot.Length).TrimStart('\') } |
    Sort-Object)
if (-not $Packs.Count) { throw "no SEST_* packs found under $repoRoot\integration" }
Write-Host ("Found {0} SEST pack(s) to install." -f $Packs.Count)

# --- Locate StreamingAssets --------------------------------------------------
if (-not $StreamingAssetsDir) {
    $StreamingAssetsDir = Find-StreamingAssets
    if (-not $StreamingAssetsDir) {
        throw "Could not auto-detect Sea Power's StreamingAssets. Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'"
    }
}
if (-not (Test-Path $StreamingAssetsDir)) {
    throw "StreamingAssets dir not found: $StreamingAssetsDir"
}
Write-Host "Installing SEST packs into: $StreamingAssetsDir`n"

# --- Copy each pack ----------------------------------------------------------
$installed = 0
foreach ($rel in $Packs) {
    $src = Join-Path $repoRoot $rel
    if (-not (Test-Path $src)) {
        Write-Warning "pack missing in repo (run git pull?): $rel"
        continue
    }
    $name = Split-Path $src -Leaf
    $dest = Join-Path $StreamingAssetsDir $name
    $action = if (Test-Path $dest) { "updated " } else { "installed" }
    Copy-Item -LiteralPath $src -Destination $StreamingAssetsDir -Recurse -Force
    $files = (Get-ChildItem -LiteralPath $dest -Recurse -File).Count
    Write-Host ("  {0}  {1,-24} {2,3} files" -f $action, $name, $files)
    $installed++
}

# --- Missions ----------------------------------------------------------------
$missionSrc = Join-Path $repoRoot "integration\missions"
if (Test-Path $missionSrc) {
    $missionDest = Join-Path $StreamingAssetsDir "user\missions\user_missions"
    New-Item -ItemType Directory -Force -Path $missionDest | Out-Null
    foreach ($m in Get-ChildItem -LiteralPath $missionSrc -Filter "*.ini") {
        $destFile = Join-Path $missionDest $m.Name
        if (Test-Path $destFile) {
            $srcRaw = Get-Content -LiteralPath $m.FullName -Raw
            $dstRaw = Get-Content -LiteralPath $destFile -Raw
            if ($srcRaw -eq $dstRaw) {
                Write-Host ("  mission    {0} (unchanged)" -f $m.Name)
                continue
            }
            # The in-game copy differs (e.g. edited in the mission editor):
            # keep a timestamped backup next to it before overwriting.
            $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            Copy-Item -LiteralPath $destFile -Destination "$destFile.backup-$stamp" -Force
            Write-Host ("  backup     {0} -> {0}.backup-{1}" -f $m.Name, $stamp)
        }
        Copy-Item -LiteralPath $m.FullName -Destination $missionDest -Force
        Write-Host ("  mission    {0}" -f $m.Name)
    }
}

Write-Host "`n$installed of $($Packs.Count) packs in place."
Write-Host ("Next: launch Sea Power -> Mod Manager -> enable all {0} SEST entries and set the order" -f $Packs.Count)
Write-Host "(see docs\setup-runbook.md Phase 4 - the SEST patch packs must sit ABOVE their targets)."
