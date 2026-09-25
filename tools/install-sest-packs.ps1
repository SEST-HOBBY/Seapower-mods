<#
.SYNOPSIS
    Install (or update) every SEST pack into Sea Power's StreamingAssets folder.

.DESCRIPTION
    Auto-detects the Sea Power install the same way export-mod-configs.ps1 does
    (Steam library manifests — no hardcoded paths), finds StreamingAssets, and
    installs the CONSOLIDATED pack, integration\dist\SEST_Integration — all
    SEST content as one Mod Manager entry, built by tools\consolidate_packs.py
    from the per-pack sources. Safe to re-run any time: the copy is mirrored in
    place, which is also how you take updates after a git pull.

    Any other SEST_* folder found in StreamingAssets (the fifteen per-pack
    folders earlier versions installed) is removed: they would double-define
    every unit alongside the consolidated pack.

    Missions are plain add-and-overwrite: every .ini under integration\missions
    is copied into the game's user_missions folder - new ones added, changed
    ones replaced in place, unchanged ones left alone, nothing deleted, no
    backup copies and no renaming. Git holds the history, so run
    import-mission.ps1 on anything you edited in game before installing.
    Each mission's "<name>_briefing" folder (its briefing map) is copied
    beside it. Old "<name> backup-<stamp>.ini" files are no longer deployed;
    -PurgeBackups removes the ones already in the game folder.

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

    # Install, and clear the old backup missions out of the game's mission list:
    powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -PurgeBackups

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
    [switch]$WhatIfOnly,
    [switch]$PurgeBackups
)

$ErrorActionPreference = "Stop"

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
. (Join-Path $scriptDir "lib\common.ps1")

# Only the consolidated pack deploys. The per-pack folders under integration\
# are build sources; installing them alongside the consolidated pack would
# define everything twice.
$Packs = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot "integration\dist") -Directory -Filter "SEST_*" -ErrorAction SilentlyContinue |
    ForEach-Object { $_.FullName.Substring($repoRoot.Length).TrimStart('\') } |
    Sort-Object)
if (-not $Packs.Count) { throw "integration\dist has no SEST_* pack - run python3 tools\build_all.py (or git pull)" }
Write-Host ("Found {0} consolidated pack(s) to install." -f $Packs.Count)

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
    foreach ($d in Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory -Filter "SEST_*") {
        if ($WhatIfOnly) { Write-Host "  would remove  $($d.Name)" }
        else { Remove-Item -LiteralPath $d.FullName -Recurse -Force; Write-Host "  removed    $($d.Name)" }
        $removed++
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
    # Mirror, don't overlay: a file the pack stops shipping must leave the
    # game too. Copy-Item alone only adds and replaces, so a unit dropped from
    # a pack would keep loading from a stale file the builder no longer writes.
    if (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Recurse -Force }
    Copy-Item -LiteralPath $src -Destination $StreamingAssetsDir -Recurse -Force
    $files = (Get-ChildItem -LiteralPath $dest -Recurse -File).Count
    Write-Host ("  {0}  {1,-24} {2,3} files" -f $action, $name, $files)
    $installed++
}

# --- Purge superseded per-pack folders ---------------------------------------
# Earlier versions installed fifteen SEST_* folders; alongside the consolidated
# pack they would define every unit twice. SEST_ is this repo's namespace, so
# anything in it that we did not just deploy is ours to remove.
$deployed = $Packs | ForEach-Object { Split-Path $_ -Leaf }
foreach ($d in Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory -Filter "SEST_*") {
    if ($deployed -contains $d.Name) { continue }
    if ($WhatIfOnly) { Write-Host ("  would purge  {0} (superseded per-pack folder)" -f $d.Name) }
    else {
        Remove-Item -LiteralPath $d.FullName -Recurse -Force
        Write-Host ("  purged     {0} (superseded per-pack folder)" -f $d.Name)
    }
}

# --- Missions ----------------------------------------------------------------
# Plain add-and-overwrite. Every .ini under integration\missions (scenarios\
# included; the game lists user_missions flat) is copied into the game's
# user_missions folder: new files are added, changed files are overwritten in
# place, unchanged files are left alone, and nothing the game has is ever
# deleted. There are no backup copies and no renaming - git is the backup, so
# import-mission.ps1 anything you edited in game BEFORE installing, or the
# in-game copy is replaced by the repo's. Files named "<name> backup-<stamp>.ini"
# (made by the old backup scheme) are not deployed; -PurgeBackups removes the
# ones already in the game folder.
$missionSrc = Join-Path $repoRoot "integration\missions"
if (Test-Path $missionSrc) {
    $missionDest = Join-Path $StreamingAssetsDir "user\missions\user_missions"
    New-Item -ItemType Directory -Force -Path $missionDest | Out-Null
    if ($PurgeBackups) {
        foreach ($bak in Get-ChildItem -LiteralPath $missionDest -Filter "* backup-*.ini") {
            if ($WhatIfOnly) { Write-Host ("  would purge  {0}" -f $bak.Name); continue }
            Remove-Item -LiteralPath $bak.FullName -Force
            Write-Host ("  purged     {0}" -f $bak.Name)
        }
    }
    $overwritten = @()
    foreach ($m in Get-ChildItem -LiteralPath $missionSrc -Filter "*.ini" -Recurse) {
        if ($m.BaseName -match ' backup-[0-9-]+$') { continue }
        $destFile = Join-Path $missionDest $m.Name
        if (Test-Path -LiteralPath $destFile) {
            if ((Get-Content -LiteralPath $m.FullName -Raw) -eq (Get-Content -LiteralPath $destFile -Raw)) {
                Write-Host ("  mission    {0} (unchanged)" -f $m.Name)
                continue
            }
            $overwritten += $m.Name
            if ($WhatIfOnly) { Write-Host ("  would update  {0}" -f $m.Name); continue }
            Copy-Item -LiteralPath $m.FullName -Destination $destFile -Force
            Write-Host ("  mission    {0} (updated)" -f $m.Name)
        } else {
            if ($WhatIfOnly) { Write-Host ("  would add     {0}" -f $m.Name); continue }
            Copy-Item -LiteralPath $m.FullName -Destination $destFile -Force
            Write-Host ("  mission    {0} (new)" -f $m.Name)
        }
    }
    if ($overwritten.Count -and $WhatIfOnly) {
        Write-Host ("  would replace the in-game copy of: {0}" -f ($overwritten -join ", ")) -ForegroundColor Yellow
        Write-Host "  (import-mission.ps1 any of those you edited in game before installing for real)"
    } elseif ($overwritten.Count) {
        Write-Host ("  replaced the in-game copy of: {0}" -f ($overwritten -join ", ")) -ForegroundColor Yellow
        Write-Host "  (if any of those carried unsaved editor work, it is gone - import-mission.ps1 first next time)"
    }
    # The briefing map pane reads "<mission>_briefing\" beside the .ini; without
    # it the right-hand pane is blank. Generated, so replaced wholesale.
    foreach ($b in Get-ChildItem -LiteralPath $missionSrc -Directory -Filter "*_briefing" -Recurse) {
        if ($WhatIfOnly) { Write-Host ("  would copy    {0}" -f $b.Name); continue }
        $destDir = Join-Path $missionDest $b.Name
        if (Test-Path -LiteralPath $destDir) { Remove-Item -LiteralPath $destDir -Recurse -Force }
        Copy-Item -LiteralPath $b.FullName -Destination $missionDest -Recurse -Force
        Write-Host ("  briefing   {0}" -f $b.Name)
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
