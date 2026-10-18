<#
.SYNOPSIS
    One command: pull the repo, install the SEST packs, set the mod order.

.DESCRIPTION
    The whole update loop, in the order that actually works:

      0. branch   - refuse to run from a branch that is not the deploy branch
                    named in data\deploy-branch.txt. A pull on the wrong branch
                    prints "Already up to date", changes nothing, and installs
                    the wrong build - silently. Override with -AnyBranch.
      1. pull     - conclude any merge left half-done, then git pull,
                    resolving the one conflict this workflow keeps producing
                    (see below). Skip with -SkipPull.
      2. install  - copy every SEST pack into StreamingAssets
                    (tools\install-sest-packs.ps1). Missions are
                    overwritten in place with no backup copy, so
                    import-mission.ps1 anything edited in game first.
      3. order    - rewrite usersettings.ini [LoadOrder] from the canonical
                    list, INSERTING any newly installed pack as enabled
                    (tools\set-mod-order.ps1 -AddMissing)
      4. verify   - hash every deployed file against the built pack and say
                    IN LINE, or name what differs. The loop reports a fact
                    rather than assuming the copy worked.

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

    THE WORKSHOP COPY. Since 14 Oct 2026 this PC can run the published pack as
    a subscriber: Steam puts it under steamapps\workshop\content\1286220\
    3812461539, beside the other mods, and the game lists it by that id where
    the local folder would be SEST_Integration. The install step recreates
    the local folder, and the game must never load both copies - two packs
    fighting over the same files, which SETUP refuses too. So while that
    folder is on disk this script stops before it pulls or copies anything
    and says the two ways out: unsubscribe from 3812461539, wait until the
    folder is gone and run again (the local install, this PC's normal
    state); or keep the Workshop copy and run with -SkipInstall, which is the
    existing switch for exactly that - the pull and the order step still run,
    and set-mod-order.ps1 keeps 3812461539 at position 1. Both copies on
    disk at once is refused whatever the switches: one has to go first.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1

.EXAMPLE
    # also re-run the mission tooling over your imported edits
    powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1 -RefreshMissions

.EXAMPLE
    # the Workshop copy of SEST stays; pull and set the order, install nothing
    powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1 -SkipInstall
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir,
    # Steam's workshop\content\1286220 folder, when auto-detection is not
    # wanted (a second library; the tests). Passed on to set-mod-order.ps1.
    [string]$WorkshopContentDir,
    [switch]$SkipPull,
    [switch]$SkipInstall,
    [switch]$SkipOrder,
    [switch]$RefreshMissions,
    [switch]$AnyBranch,
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

# --- the Workshop copy of SEST ----------------------------------------------
# Checked before anything is pulled or copied, so a stop here changes nothing.
# See THE WORKSHOP COPY in the header. -SkipInstall is the way to keep the
# Workshop copy; both copies on disk at once is refused with any switches.
$wsCopy = Find-SestWorkshopCopy -WorkshopContentDir $WorkshopContentDir
if ($wsCopy) {
    $wsId = Split-Path -Leaf $wsCopy
    $saDir = $StreamingAssetsDir
    if (-not $saDir) { $saDir = Find-StreamingAssets }
    $localCopy = $(if ($saDir) { Join-Path $saDir $SestDistToken } else { $null })
    $localPresent = [bool]($localCopy -and (Test-Path -LiteralPath $localCopy))
    if ($localPresent -or -not $SkipInstall) {
        Write-Host ""
        Write-Host "  The Workshop copy of SEST is on disk:" -ForegroundColor Red
        Write-Host "      $wsCopy" -ForegroundColor Red
        if ($localPresent) {
            Write-Host "  and so is the local copy this script installs:" -ForegroundColor Red
            Write-Host "      $localCopy" -ForegroundColor Red
        }
        Write-Host "  The game must never load both it and the local StreamingAssets\$SestDistToken" -ForegroundColor Yellow
        Write-Host "  folder: two packs fighting over the same files. Two ways out:" -ForegroundColor Yellow
        Write-Host "    1. Unsubscribe from $wsId in Steam, wait until that folder is gone, and run" -ForegroundColor Yellow
        Write-Host "       this script again (the local install - this PC's normal state)." -ForegroundColor Yellow
        if ($localPresent) {
            Write-Host "    2. Keep the Workshop copy: with the game closed, delete the local folder named" -ForegroundColor Yellow
            Write-Host "       above, then re-run with -SkipInstall." -ForegroundColor Yellow
            throw "both copies of SEST are on disk (Workshop item $wsId and the local $SestDistToken) - remove one first."
        }
        Write-Host "    2. Keep the Workshop copy: re-run with -SkipInstall. The pull and the order step" -ForegroundColor Yellow
        Write-Host "       still run, and set-mod-order.ps1 keeps $wsId at position 1 in place of $SestDistToken." -ForegroundColor Yellow
        throw "the Workshop copy of SEST ($wsId) is on disk - not installing the local copy beside it."
    }
    Write-Host "Workshop copy of SEST on disk ($wsCopy): -SkipInstall given, so no local copy is installed and the order step keeps $wsId at position 1." -ForegroundColor Yellow
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

    $missions = @($conflicts | Where-Object { $_ -like "integration/mission-seeds/*.ini" })
    $others   = @($conflicts | Where-Object { $_ -notlike "integration/mission-seeds/*.ini" })
    if ($others) {
        Write-Host ""
        Write-Warning "conflicts outside integration\mission-seeds - stopping, these need you:"
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

# --- 0. the right branch -----------------------------------------------------
# The failure this guards against is silent and cost a whole evening: standing
# on another branch, "git pull" fetches, updates the remote-tracking ref, prints
# "Already up to date" for the branch you are actually on, and changes nothing.
# Everything looks like it worked. The install then deploys whatever that other
# branch built, and a fix that is provably correct in git is simply absent from
# the game. Nothing downstream can detect it, so it is checked here first.
$branchFile = Join-Path $repoRoot "data\deploy-branch.txt"
$want = if (Test-Path -LiteralPath $branchFile) {
    (Get-Content -LiteralPath $branchFile | Where-Object { $_ -and $_ -notmatch '^#' } |
     Select-Object -First 1).Trim()
} else { "" }
$have = (& git rev-parse --abbrev-ref HEAD).Trim()
if ($want -and $have -ne $want) {
    Write-Host ""
    Write-Host "  You are on branch : $have" -ForegroundColor Red
    Write-Host "  Deploys come from : $want" -ForegroundColor Red
    Write-Host ""
    Write-Host "  A pull here would say 'Already up to date' and install the WRONG build." -ForegroundColor Yellow
    Write-Host "  Switch with:  git checkout $want" -ForegroundColor Yellow
    Write-Host "  Or, if you meant to deploy $have, re-run with -AnyBranch." -ForegroundColor Yellow
    if (-not $AnyBranch) { throw "refusing to sync from '$have' (expected '$want')." }
    Write-Warning "-AnyBranch given: syncing from '$have' anyway."
} elseif ($want) {
    Write-Host "branch: $have" -ForegroundColor DarkGray
}

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

    # Only TRACKED changes are dangerous here: a merge on top of edits to files
    # git is following can lose them. Untracked files ('??') cannot be lost -
    # if an incoming file would land on one, git refuses the merge outright
    # rather than overwriting. Blocking on those just stopped the loop dead over
    # a local scratch folder, so they are reported and stepped over.
    $status = (& git status --porcelain) | Where-Object { $_ }
    $dirty = $status | Where-Object { $_ -notmatch '^\?\?' }
    $untracked = $status | Where-Object { $_ -match '^\?\?' }
    if ($dirty) {
        Write-Warning "you have uncommitted changes to tracked files:"
        $dirty | ForEach-Object { Write-Host "    $_" }
        throw "commit or stash them first - a merge on top of uncommitted work is how edits get lost."
    }
    if ($untracked) {
        Write-Host "  untracked (left alone, cannot be lost by a merge):" -ForegroundColor DarkGray
        $untracked | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
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
    if ($WorkshopContentDir) { $orderArgs["WorkshopContentDir"] = $WorkshopContentDir }
    if ($Force) { $orderArgs["Force"] = $true }
    & (Join-Path $scriptDir "set-mod-order.ps1") @orderArgs
} else {
    Write-Host "`n[3/3] mod order skipped (-SkipOrder)" -ForegroundColor DarkGray
}

# --- mods' own debug switches ------------------------------------------------
# A mod update puts its author's file back, debug switch and all; see
# quiet-mod-debug.ps1 for the one that froze Steel Highway.
Write-Host "`nchecking mod debug switches..." -ForegroundColor Cyan
& (Join-Path $scriptDir "quiet-mod-debug.ps1")

# --- the start-up "not compatible" warning ------------------------------------
# A mod update puts its author's _info.ini back too; see mark-mods-compatible.ps1.
Write-Host "`nmarking out-of-date mods compatible..." -ForegroundColor Cyan
$compatArgs = @{}
if ($WorkshopContentDir) { $compatArgs["WorkshopContentDir"] = $WorkshopContentDir }
if ($StreamingAssetsDir) { $compatArgs["StreamingAssetsDir"] = $StreamingAssetsDir }
# A start-up warning is not worth stopping the sync for: say what went wrong
# and carry on.
try { & (Join-Path $scriptDir "mark-mods-compatible.ps1") @compatArgs }
catch { Write-Warning ("mods not marked compatible: " + $_.Exception.Message) }

# --- optional: re-run the mission tooling ------------------------------------
if ($RefreshMissions) {
    Write-Host "`nre-running the mission tooling..." -ForegroundColor Cyan
    $py = Get-Python
    if (-not $py) {
        Write-Warning "Python 3 not found - skipping. Install it from python.org (tick 'Add to PATH')."
    } else {
        $tool = Join-Path $repoRoot "integration\mission-seeds\fix_squadron_refs.py"
        $argList = @($py.Pre) + @($tool, "--spread", "--write")
        & $py.Exe @argList
        # civil aircraft that would reach the end of their route and circle
        # get one waypoint further along their airway; idempotent
        $tool = Join-Path $repoRoot "integration\mission-seeds\extend_civil_airways.py"
        $argList = @($py.Pre) + @($tool, "--write")
        & $py.Exe @argList
        Write-Host "`nFor the full civilian-traffic and water passes on one mission, use:"
        Write-Host "  .\tools\refresh-mission.ps1 -Mission `"NORTHERN FRONT III FINAL`" -SkipImport"
    }
}

# --- verify: is the game actually in line with the repo? ---------------------
# The whole point of the loop, stated as a fact rather than a hope. Compares the
# deployed pack against the built one file by file.
if (-not $SkipInstall) {
    $sa = $StreamingAssetsDir
    if (-not $sa) { $sa = Find-StreamingAssets }
    $src = Join-Path $repoRoot "integration\dist\SEST_Integration"
    $dst = Join-Path $sa "SEST_Integration"
    if ((Test-Path -LiteralPath $src) -and (Test-Path -LiteralPath $dst)) {
        $diff = @()
        foreach ($f in Get-ChildItem -LiteralPath $src -Recurse -File) {
            $rel = $f.FullName.Substring($src.Length).TrimStart('\')
            $t = Join-Path $dst $rel
            if (-not (Test-Path -LiteralPath $t)) { $diff += "missing: $rel"; continue }
            if ((Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash -ne
                (Get-FileHash -LiteralPath $t -Algorithm SHA256).Hash) { $diff += "differs: $rel" }
        }
        $n = (Get-ChildItem -LiteralPath $src -Recurse -File).Count
        if ($diff) {
            Write-Host "`nINSTALL IS NOT IN LINE - $($diff.Count) of $n file(s):" -ForegroundColor Red
            $diff | Select-Object -First 10 | ForEach-Object { Write-Host "    $_" }
            if ($diff.Count -gt 10) { Write-Host "    ... and $($diff.Count - 10) more" }
        } else {
            Write-Host "`nIN LINE: all $n installed files match this commit ($((& git rev-parse --short HEAD).Trim()))." -ForegroundColor Green
        }
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
