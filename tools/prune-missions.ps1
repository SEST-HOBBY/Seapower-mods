<#
.SYNOPSIS
    Clear out the game's user_missions folder, keeping only what you asked for.

.DESCRIPTION
    The installer used to ship every .ini under integration\missions\ - 69
    files, including eleven NORTHERN FRONT III backups, six NORTHERN FRONT II
    backups, five SULU SEA drafts and nine separate files whose internal name
    is "_TempMission". data\deploy-missions.txt now decides what ships; this
    removes what earlier runs already put there, plus anything else living in
    the folder.

    KEEPS exactly what data\deploy-missions.txt lists. Everything else in
    user_missions is either archived or deleted.

    SAFETY, because this touches saves and not repo files:

      - Dry run by DEFAULT. Nothing moves until you pass -Apply. The listing
        it prints is exactly what it would do.
      - Archives by default rather than deleting. -Delete removes instead.
      - Refuses to run while Sea Power is running, because the game rewrites
        this folder on exit and would undo the change.
      - Never touches _info.ini. That is the folder's own metadata, shipped by
        the game, and it is what the mission browser labels the folder with -
        not a mission at all.
      - Reports every file as REPO (this repo can regenerate it), BACKUP (an
        installer-made backup) or UNKNOWN. UNKNOWN means it exists only in
        your game folder - a mission you saved in the editor that the repo has
        never seen. Those are the ones worth looking at before deleting, and
        -Delete refuses to touch them unless you also pass -IncludeUnknown.

.EXAMPLE
    # see what would happen - changes nothing
    powershell -ExecutionPolicy Bypass -File .\tools\prune-missions.ps1

.EXAMPLE
    # move everything not on the keep list into an archive folder
    powershell -ExecutionPolicy Bypass -File .\tools\prune-missions.ps1 -Apply

.EXAMPLE
    # delete instead of archiving, including editor saves the repo never saw
    powershell -ExecutionPolicy Bypass -File .\tools\prune-missions.ps1 -Apply -Delete -IncludeUnknown
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir,
    [switch]$Apply,
    [switch]$Delete,
    [switch]$IncludeUnknown,
    [string]$ArchiveDir
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "lib\common.ps1")

# The repo already has this check; it matches both process names the game uses.
# Only gated on -Apply so a dry run is always safe to fire off.
if ((Test-SeaPowerRunning) -and $Apply) {
    throw ("Sea Power is running. It rewrites its mission folders on exit, which would " +
           "undo this. Quit the game and re-run.")
}

if (-not $StreamingAssetsDir) {
    $StreamingAssetsDir = Find-StreamingAssets
    if (-not $StreamingAssetsDir) {
        throw "Could not auto-detect StreamingAssets. Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'"
    }
}
$missionDir = Join-Path $StreamingAssetsDir "user\missions\user_missions"
if (-not (Test-Path $missionDir)) { throw "no user_missions folder at: $missionDir" }

# --- the keep list -----------------------------------------------------------
$manifest = Join-Path $repoRoot "data\deploy-missions.txt"
if (-not (Test-Path $manifest)) { throw "keep list not found: $manifest" }

$keep = New-Object System.Collections.Generic.HashSet[string] ([StringComparer]::OrdinalIgnoreCase)
$keepScenarios = $false
foreach ($line in Get-Content -LiteralPath $manifest) {
    $entry = $line.Trim()
    if (-not $entry -or $entry.StartsWith("#")) { continue }
    if ($entry -eq "scenarios/*") { $keepScenarios = $true; continue }
    [void]$keep.Add($entry)
}
if ($keepScenarios) {
    foreach ($s in Get-ChildItem -LiteralPath (Join-Path $repoRoot "integration\missions\scenarios") `
                                 -Filter "*.ini" -ErrorAction SilentlyContinue) {
        [void]$keep.Add($s.BaseName)
    }
}

# Everything the repo holds, so a file can be reported as recoverable or not.
$inRepo = New-Object System.Collections.Generic.HashSet[string] ([StringComparer]::OrdinalIgnoreCase)
foreach ($m in Get-ChildItem -LiteralPath (Join-Path $repoRoot "integration\missions") `
                             -Filter "*.ini" -Recurse -ErrorAction SilentlyContinue) {
    [void]$inRepo.Add($m.BaseName)
}

# --- classify ----------------------------------------------------------------
# _info.ini is NOT a mission. It is the folder's own metadata, shipped by the
# game - "[Language_en] Name=User Missions" and the same in de/ru/cn - and it
# is what the mission browser labels the folder with. Vanilla ships one in
# user\missions\user_missions\ and in every NEW MISSIONS CLEAN subfolder.
# The first version of this script swept it up as an editor save; it survived
# only because the UNKNOWN guard refused to delete it. Never touch it.
$neverTouch = @("_info.ini")

$kept = @(); $going = @()
foreach ($f in Get-ChildItem -LiteralPath $missionDir -Filter "*.ini" | Sort-Object Name) {
    if ($neverTouch -contains $f.Name) {
        Write-Host ("  protect    {0} (game folder metadata, not a mission)" -f $f.Name)
        continue
    }
    if ($keep.Contains($f.BaseName)) { $kept += $f; continue }
    $origin = if ($inRepo.Contains($f.BaseName)) { "REPO" }
              elseif ($f.BaseName -match ' backup-\d{8}-\d{6}$') { "BACKUP" }
              else { "UNKNOWN" }
    $going += [pscustomobject]@{ File = $f; Origin = $origin }
}

Write-Host "`nuser_missions: $missionDir`n"
Write-Host "KEEPING $($kept.Count):"
foreach ($f in $kept) { Write-Host ("  keep       {0}" -f $f.Name) }

$verb = if ($Delete) { "delete" } else { "archive" }
Write-Host "`n$($verb.ToUpper()) $($going.Count):"
foreach ($g in $going) {
    $note = switch ($g.Origin) {
        "REPO"    { "in the repo - regenerable" }
        "BACKUP"  { "installer backup" }
        "UNKNOWN" { "NOT IN REPO - editor save, exists only here" }
    }
    Write-Host ("  {0,-9}  {1,-52} {2}" -f $g.Origin, $g.File.Name, $note)
}

$unknown = @($going | Where-Object { $_.Origin -eq "UNKNOWN" })
if ($unknown.Count -and $Delete -and -not $IncludeUnknown) {
    Write-Host ("`n{0} file(s) exist ONLY in your game folder. -Delete will not remove those " -f $unknown.Count)
    Write-Host "without -IncludeUnknown; they will be archived instead so nothing is lost."
}

if (-not $Apply) {
    Write-Host "`nDRY RUN - nothing changed. Re-run with -Apply to $verb the $($going.Count) file(s) above."
    return
}

# --- act ---------------------------------------------------------------------
if (-not $ArchiveDir) {
    # OUTSIDE the game install, deliberately. The game's missions folder uses
    # subfolders - vanilla ships _temp, "NEW MISSIONS CLEAN" and newest under
    # user\missions\ - so an archive dropped anywhere beneath it risks being
    # listed as missions again, which is the opposite of the point. The repo
    # root is somewhere you will find it, and _mission-archive is gitignored.
    $ArchiveDir = Join-Path $repoRoot ("_mission-archive\" + (Get-Date -Format "yyyyMMdd-HHmmss"))
}
$moved = 0; $removed = 0
foreach ($g in $going) {
    $reallyDelete = $Delete -and ($g.Origin -ne "UNKNOWN" -or $IncludeUnknown)
    if ($reallyDelete) {
        Remove-Item -LiteralPath $g.File.FullName -Force
        $removed++
    } else {
        New-Item -ItemType Directory -Force -Path $ArchiveDir | Out-Null
        Move-Item -LiteralPath $g.File.FullName -Destination $ArchiveDir -Force
        $moved++
    }
}

Write-Host "`n$removed deleted, $moved archived, $($kept.Count) kept."
if ($moved) {
    Write-Host "Archive: $ArchiveDir"
    Write-Host "That is outside the game install, so nothing there can be listed as a mission."
    Write-Host "Delete the folder once you are happy."
}
Write-Host "`nRe-running tools\install-sest-packs.ps1 will now only ship what"
Write-Host "data\deploy-missions.txt lists, so the clutter does not come back."
