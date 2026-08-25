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

    # Show what WOULD change without touching anything:
    powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -WhatIfOnly

    # Remove every installed pack again, leaving the workshop mods alone:
    powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -Uninstall

.NOTES
    The packs are patches, not standalone mods - 99 files and every one a .ini,
    with no model, texture or asset bundle among them. Each needs the workshop
    mod that supplies the geometry its .ini refers to. Run
    tools\check_dependencies.py to see what each one requires.
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir,
    [switch]$Uninstall,
    [switch]$WhatIfOnly
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

# --- Uninstall ---------------------------------------------------------------
# Each pack lives in its OWN folder under StreamingAssets and never writes into
# the game's own files, so removing one is just deleting its folder - the
# workshop mods and the base game are untouched. Order entries for a removed
# pack are skipped with a warning by set-mod-order.ps1, not an error.
if ($Uninstall) {
    $removed = 0
    foreach ($rel in $Packs) {
        $name = Split-Path (Join-Path $repoRoot $rel) -Leaf
        $dest = Join-Path $StreamingAssetsDir $name
        if (Test-Path -LiteralPath $dest) {
            if ($WhatIfOnly) { Write-Host "  would remove  $name" }
            else { Remove-Item -LiteralPath $dest -Recurse -Force; Write-Host "  removed    $name" }
            $removed++
        }
    }
    Write-Host ("`n{0} pack(s) {1}. Workshop mods and game files untouched." -f
        $removed, $(if ($WhatIfOnly) { "would be removed" } else { "removed" }))
    Write-Host "Re-run without -Uninstall to put them back."
    return
}

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
    if ($WhatIfOnly) {
        Write-Host ("  would {0}  {1}" -f $action.Trim(), $name)
        $installed++
        continue
    }
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
    # Backups are ordinary .ini missions so the game can list and load them
    # for recovery. Migrate any file from the two earlier schemes
    # ("<name>.ini.backup-<stamp>" and "<name>.backup-<stamp>.bak") into
    # "<name> backup-<stamp>.ini". One-time per file; harmless when empty.
    $legacy = @(Get-ChildItem -LiteralPath $missionDest -Filter "*.ini.backup-*") +
              @(Get-ChildItem -LiteralPath $missionDest -Filter "*.backup-*.bak")
    foreach ($old in $legacy) {
        if ($old.Name -notmatch '^(.*?)(?:\.ini)?\.backup-([0-9-]+)(?:\.bak)?$') { continue }
        $fixed = "{0} backup-{1}.ini" -f $Matches[1], $Matches[2]
        Rename-Item -LiteralPath $old.FullName -NewName $fixed
        Write-Host ("  renamed    {0} -> {1} (backups are loadable missions now)" -f $old.Name, $fixed)
    }
    # Restamp internal titles on any backup still carrying the original's -
    # the browser displays the INTERNAL name, so without this a mission with
    # several backups shows as that many identical entries. Idempotent: once
    # the titles carry the stamp, the replace finds nothing to change.
    foreach ($bak in Get-ChildItem -LiteralPath $missionDest -Filter "* backup-*.ini") {
        if ($bak.BaseName -notmatch '^(.*) backup-([0-9-]+)$') { continue }
        $base = $Matches[1]; $bstamp = $Matches[2]
        $raw = Get-Content -LiteralPath $bak.FullName -Raw
        $esc = [regex]::Escape($base)
        $new = $raw -replace "(?m)^Name=$esc\s*$", ("Name={0} backup-{1}" -f $base, $bstamp)
        if ($new -ne $raw) {
            Set-Content -LiteralPath $bak.FullName -Value $new -Encoding UTF8 -NoNewline
            Write-Host ("  restamped  {0} (internal titles now carry the backup stamp)" -f $bak.Name)
        }
    }
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
            # keep a timestamped backup before overwriting - saved as a real
            # .ini so the mission browser lists it and it can be opened for
            # recovery like any other mission. Its internal titles get the
            # stamp appended so the two entries are tellable apart; only
            # lines exactly matching this mission's own name are touched.
            $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $bakName = "{0} backup-{1}.ini" -f $m.BaseName, $stamp
            $esc = [regex]::Escape($m.BaseName)
            ($dstRaw -replace "(?m)^Name=$esc\s*$", ("Name={0} backup-{1}" -f $m.BaseName, $stamp)) |
                Set-Content -LiteralPath (Join-Path $missionDest $bakName) -Encoding UTF8 -NoNewline
            Write-Host ("  backup     {0} -> {1}" -f $m.Name, $bakName)
        }
        Copy-Item -LiteralPath $m.FullName -Destination $missionDest -Force
        Write-Host ("  mission    {0}" -f $m.Name)
    }
}

Write-Host "`n$installed of $($Packs.Count) packs in place."
# -AddMissing inserts a freshly installed pack into usersettings.ini at its
# canonical position, already enabled, which is exactly what this script has
# just made possible. Telling people to go tick boxes in the Mod Manager was
# leftover from before that flag existed.
Write-Host "Next, with the game CLOSED:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing"
Write-Host "(enables and positions every pack for you - no Mod Manager visit needed.)"
