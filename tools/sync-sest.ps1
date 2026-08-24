<#
.SYNOPSIS
    One command: pull the repo, install the SEST packs, set the mod order.

.DESCRIPTION
    The whole update loop, in the order that actually works:

      1. pull     - conclude any merge left half-done, then git pull,
                    resolving the one conflict this workflow keeps producing
                    (see below). Skip with -SkipPull.
      2. install  - copy every SEST pack into StreamingAssets
                    (tools\install-sest-packs.ps1)
      3. order    - rewrite usersettings.ini [LoadOrder] from the canonical
                    list, INSERTING any newly installed pack as enabled
                    (tools\set-mod-order.ps1 -AddMissing)

    That third step is the point. Until now a new pack meant: install, launch
    the game, find it in the Mod Manager, tick it, quit so the game writes
    usersettings.ini, then run set-mod-order.ps1. Now it is in the right place
    and enabled before the game has ever seen it.

    THE PULL CONFLICT. You edit a mission in game and import it; meanwhile the
    mission tooling has committed changes to the same file. Both sides changed
    it from the same base, so git stops. Your imported copy always wins - it is
    the one with your latest hand edits - and the tooling is idempotent, so
    re-running it puts its changes back on top. This script does exactly that
    and tells you when it has. Conflicts in ANY OTHER file are left alone and
    the script stops: those need a human.

    CLOSE THE GAME FIRST. It rewrites usersettings.ini on exit, so an edit made
    while it is running is silently thrown away. The script checks.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1

.EXAMPLE
    # also re-run the mission tooling over your imported edits
    powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1 -RefreshMissions
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir,
    [switch]$SkipPull,
    [switch]$SkipInstall,
    [switch]$SkipOrder,
    [switch]$RefreshMissions,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
. (Join-Path $scriptDir "lib\common.ps1")

if ((Test-SeaPowerRunning) -and -not $Force) {
    throw ("Sea Power is running. It rewrites usersettings.ini when it exits, which would " +
           "undo the mod order this sets. Quit the game and re-run (-Force to override).")
}

function Resolve-MissionConflicts {
    <# Stage every unmerged file, keeping YOUR copy for missions. Returns the
       mission paths kept, or throws if something else is conflicted.

       --ours during a merge means the local commit - the mission you imported
       from the game, with your hand edits. The tooling that touched the same
       file is idempotent, so re-running it puts its changes back on top. Any
       other conflicted file is a real decision and stops the script. #>
    $conflicts = @((& git diff --name-only --diff-filter=U) | Where-Object { $_ })
    if (-not $conflicts) { return @() }

    $missions = @($conflicts | Where-Object { $_ -like "integration/missions/*.ini" })
    $others   = @($conflicts | Where-Object { $_ -notlike "integration/missions/*.ini" })
    if ($others) {
        Write-Host ""
        Write-Warning "conflicts outside integration\missions - stopping, these need you:"
        $others | ForEach-Object { Write-Host "    $_" }
        throw "resolve them, run 'git commit', then re-run this script."
    }
    foreach ($f in $missions) {
        Write-Host "  keeping YOUR imported copy of $f" -ForegroundColor Yellow
        & git checkout --ours -- $f
        & git add -- $f
    }
    return $missions
}

Push-Location $repoRoot
# Never let git open an editor from a script - a stale editor swap file on
# MERGE_MSG is exactly what strands a merge half-done.
$env:GIT_EDITOR = "true"
try {

# --- 1. pull -----------------------------------------------------------------
if (-not $SkipPull) {
    Write-Host "`n[1/3] pulling..." -ForegroundColor Cyan

    # A merge left unconcluded (MERGE_HEAD present) blocks every future pull
    # with "You have not concluded your merge". Usually the commit editor was
    # closed without saving. Finish it before doing anything else.
    $gitDir = (& git rev-parse --git-dir).Trim()
    if (Test-Path -LiteralPath (Join-Path $gitDir "MERGE_HEAD")) {
        Write-Host "  a previous merge was never concluded - finishing it" -ForegroundColor Yellow
        $kept = Resolve-MissionConflicts
        # --no-edit keeps git from opening an editor; a stale .swp on MERGE_MSG
        # is what usually stranded the merge in the first place.
        & git commit --no-edit
        if ($LASTEXITCODE -ne 0) { throw "could not conclude the pending merge - run 'git status' and finish it by hand." }
        if ($kept) { $script:MissionsMerged = $kept }
        Write-Host "  pending merge concluded" -ForegroundColor Green
    }

    $dirty = (& git status --porcelain) | Where-Object { $_ }
    if ($dirty) {
        Write-Warning "you have uncommitted changes:"
        $dirty | ForEach-Object { Write-Host "    $_" }
        throw "commit or stash them first - a merge on top of uncommitted work is how edits get lost."
    }

    & git pull --no-rebase --no-edit
    if ($LASTEXITCODE -ne 0) {
        $kept = Resolve-MissionConflicts
        if (-not $kept) { throw "git pull failed (exit $LASTEXITCODE) - see the output above." }
        & git commit --no-edit
        if ($LASTEXITCODE -ne 0) { throw "could not complete the merge commit - resolve by hand." }
        $script:MissionsMerged = @($script:MissionsMerged) + $kept | Where-Object { $_ } | Select-Object -Unique
    }
    if ($script:MissionsMerged) {
        Write-Host "  merged. Re-run the mission tooling to put its changes back on top" -ForegroundColor Yellow
        Write-Host "  (this script does it for you with -RefreshMissions)." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[1/3] pull skipped (-SkipPull)" -ForegroundColor DarkGray
}

# --- 2. install --------------------------------------------------------------
if (-not $SkipInstall) {
    Write-Host "`n[2/3] installing packs..." -ForegroundColor Cyan
    $installArgs = @{}
    if ($StreamingAssetsDir) { $installArgs["StreamingAssetsDir"] = $StreamingAssetsDir }
    # NOTE: splat a HASHTABLE. Array splatting binds POSITIONALLY, so
    # @("-StreamingAssetsDir", $x) would pass the literal switch name as a value.
    & (Join-Path $scriptDir "install-sest-packs.ps1") @installArgs
} else {
    Write-Host "`n[2/3] install skipped (-SkipInstall)" -ForegroundColor DarkGray
}

# --- 3. mod order ------------------------------------------------------------
if (-not $SkipOrder) {
    Write-Host "`n[3/3] setting the mod order..." -ForegroundColor Cyan
    $orderArgs = @{ AddMissing = $true }
    if ($StreamingAssetsDir) { $orderArgs["StreamingAssetsDir"] = $StreamingAssetsDir }
    if ($Force) { $orderArgs["Force"] = $true }
    & (Join-Path $scriptDir "set-mod-order.ps1") @orderArgs
} else {
    Write-Host "`n[3/3] mod order skipped (-SkipOrder)" -ForegroundColor DarkGray
}

# --- optional: re-run the mission tooling ------------------------------------
if ($RefreshMissions) {
    Write-Host "`nre-running the mission tooling..." -ForegroundColor Cyan
    $py = Get-Python
    if (-not $py) {
        Write-Warning "Python 3 not found - skipping. Install it from python.org (tick 'Add to PATH')."
    } else {
        $tool = Join-Path $repoRoot "integration\missions\fix_squadron_refs.py"
        $argList = @($py.Pre) + @($tool, "--spread", "--write")
        & $py.Exe @argList
        Write-Host "`nFor the full civilian-traffic and water passes on one mission, use:"
        Write-Host "  .\tools\refresh-mission.ps1 -Mission `"NORTHERN FRONT III FINAL`" -SkipImport"
    }
}

Write-Host "`nDone." -ForegroundColor Green
if ($script:MissionsMerged) {
    Write-Host "Your imported mission(s) were kept over the incoming changes:" -ForegroundColor Yellow
    $script:MissionsMerged | ForEach-Object { Write-Host "    $_" }
    Write-Host "Commit and push when you are happy:  git push" -ForegroundColor Yellow
}
Write-Host "Launch Sea Power - the Mod Manager should already show the SEST packs enabled and in order."

} finally {
    Pop-Location
}
