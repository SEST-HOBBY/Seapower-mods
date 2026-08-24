<#
.SYNOPSIS
    Install (or update) the seven SEST packs into Sea Power's StreamingAssets folder.

.DESCRIPTION
    Auto-detects the Sea Power install the same way export-mod-configs.ps1 does
    (Steam library manifests — no hardcoded paths), finds StreamingAssets, and
    copies the seven SEST pack folders from this repo's integration\ directories
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

$Packs = @(
    "integration\f-15ex-revamp\SEST_F-15EX_Revamp",
    "integration\f-35c-jatm\SEST_F-35C_JATM",
    "integration\growler-ngj-malice\SEST_Growler_NGJ_MALICE",
    "integration\raaf-f-35a-jatm\SEST_RAAF_F-35A_JATM",
    "integration\raaf-bases\SEST_RAAF_Bases",
    "integration\ran-fleet\SEST_RAN_Fleet",
    "integration\jmsdf-mogami\SEST_JMSDF_Mogami"
)

function Get-SteamLibraries {
    $steamRoots = @()
    foreach ($regPath in "HKCU:\Software\Valve\Steam", "HKLM:\SOFTWARE\WOW6432Node\Valve\Steam") {
        try {
            $p = (Get-ItemProperty -Path $regPath -ErrorAction Stop).SteamPath
            if (-not $p) { $p = (Get-ItemProperty -Path $regPath -ErrorAction Stop).InstallPath }
            if ($p) { $steamRoots += $p }
        } catch { }
    }
    $steamRoots += "${env:ProgramFiles(x86)}\Steam", "$env:ProgramFiles\Steam"
    $libs = @()
    foreach ($root in $steamRoots | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique) {
        $libs += Join-Path $root "steamapps"
        $vdf = Join-Path $root "steamapps\libraryfolders.vdf"
        if (Test-Path $vdf) {
            foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) {
                $libs += Join-Path ($m.Groups[1].Value -replace '\\\\', '\') "steamapps"
            }
        }
    }
    return $libs | Where-Object { Test-Path $_ } | Select-Object -Unique
}

# --- Locate StreamingAssets --------------------------------------------------
if (-not $StreamingAssetsDir) {
    foreach ($lib in Get-SteamLibraries) {
        foreach ($acf in Get-ChildItem -LiteralPath $lib -Filter "appmanifest_*.acf" -ErrorAction SilentlyContinue) {
            $raw = Get-Content -LiteralPath $acf.FullName -Raw
            if ($raw -match '"name"\s+"([^"]*Sea Power[^"]*)"') {
                $installDir = [regex]::Match($raw, '"installdir"\s+"([^"]+)"').Groups[1].Value
                $gameDir = Join-Path $lib "common\$installDir"
                $sa = Get-ChildItem -LiteralPath $gameDir -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue |
                    Where-Object { $_.Name -eq "StreamingAssets" } | Select-Object -First 1
                if ($sa) { $StreamingAssetsDir = $sa.FullName }
                break
            }
        }
        if ($StreamingAssetsDir) { break }
    }
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
Write-Host "Next: launch Sea Power -> Mod Manager -> enable the seven SEST entries and set the order"
Write-Host "(see docs\setup-runbook.md Phase 4 - the four SEST loadout patches must sit ABOVE their targets)."
