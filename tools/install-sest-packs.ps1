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

    Missions are not copied into user_missions. Every SEST mission ships
    inside the campaign pack; integration\mission-seeds\ (the early
    scenarios and editor saves) is an archive, never installed. Copies of
    those seeds that earlier versions of this script put into user_missions
    are moved out, once, into Documents\SEST-retired-missions; the player's
    own missions are not touched.
    -PurgeBackups removes the old "<name> backup-<stamp>.ini" copies.

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
    The patch packs are not standalone mods - nothing but .ini files, with
    no model, texture or asset bundle among them (only the campaign pack adds
    pages, maps and art). Each needs the workshop mod that supplies the
    geometry its .ini refers to. Run
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
# Nothing is copied into user_missions any more. Every SEST mission the game
# should list ships inside the campaign pack (integration\dist\SEST_Integration\
# missions\ and campaigns\), installed above with the pack. integration\
# mission-seeds\ is the archive of the early scenarios and editor saves the
# side operations are refined from; it is never installed. Until 17 Oct 2026
# this script copied all of it into user_missions, so a developer's game
# listed 60-odd drafts beside the player's own missions. This step moves those
# copies (matched by name against the seeds, so the player's own missions are
# untouched) out of the game into Documents\SEST-retired-missions, once.
$seedSrc = Join-Path $repoRoot "integration\mission-seeds"
$missionDest = Join-Path $StreamingAssetsDir "user\missions\user_missions"
if ($PurgeBackups -and (Test-Path -LiteralPath $missionDest)) {
    foreach ($bak in Get-ChildItem -LiteralPath $missionDest -Filter "* backup-*.ini") {
        # Only the old scheme's own "<name> backup-<yyyyMMdd-HHmmss>" names.
        # user_missions also holds the player's own missions, and a title
        # such as "Strait backup-plan" must survive the purge.
        if ($bak.BaseName -notmatch ' backup-[0-9-]+$') { continue }
        if ($WhatIfOnly) { Write-Host ("  would purge  {0}" -f $bak.Name); continue }
        Remove-Item -LiteralPath $bak.FullName -Force
        Write-Host ("  purged     {0}" -f $bak.Name)
    }
}
if ((Test-Path $seedSrc) -and (Test-Path -LiteralPath $missionDest)) {
    $retired = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "SEST-retired-missions"
    $moved = 0
    foreach ($m in Get-ChildItem -LiteralPath $seedSrc -Filter "*.ini" -Recurse) {
        foreach ($name in @($m.Name, ($m.BaseName + "_briefing"))) {
            $old = Join-Path $missionDest $name
            if (-not (Test-Path -LiteralPath $old)) { continue }
            if ($WhatIfOnly) { Write-Host ("  would retire  {0}" -f $name); $moved++; continue }
            New-Item -ItemType Directory -Force -Path $retired | Out-Null
            $target = Join-Path $retired $name
            if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
            Move-Item -LiteralPath $old -Destination $target -Force
            Write-Host ("  retired    {0}" -f $name)
            $moved++
        }
    }
    if ($moved -and -not $WhatIfOnly) {
        Write-Host ("  {0} old seed copies moved out of user_missions into {1}" -f $moved, $retired) -ForegroundColor Yellow
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
