<#
.SYNOPSIS
    One command to take a mission you edited in game, re-run the SEST mission
    tooling over it, and put it back.

.DESCRIPTION
    Chains the whole round trip:

      1. import   - copy the mission out of the game's user_missions folder
                    into integration\missions (skip with -SkipImport)
      2. dress    - realistic hull types and airline liveries for the neutral
                    civilian traffic (refine_civ_traffic.py)
      3. depth    - add the extra merchants, airliners and whale pods if they
                    are not already present (add_civ_depth.py)
      4. names    - replace editor placeholder group labels ("Group Name 7")
                    with names describing the group (name_formations.py)
      5. water    - move any vessel or sea life that sits on land into the
                    water (fix_land_positions.py)
      6. squadrons- repair squadron references the editor left unresolved, and
                    re-split groups that an earlier repair collapsed
                    (fix_squadron_refs.py --spread)
      7. install  - copy the result back into the game (only with -Install)

    Every step is idempotent and preserves your placements, waypoints and
    formations, so it is safe to run after each editing session.

    Needs Python 3 on PATH. Step 5 also needs the land mask package; pass
    -InstallDeps once to fetch it, or the step is skipped with a warning.

    -Mission defaults to whatever data\active-mission.txt names, which is the
    same file the Python tools read - so running this with no arguments always
    works on the scenario you are actually developing, rather than a default
    baked in when some other mission was current.

.EXAMPLE
    # After editing the active mission in the editor (game closed):
    powershell -ExecutionPolicy Bypass -File .\tools\refresh-mission.ps1 -Install

.EXAMPLE
    # First run on a machine, to fetch the land-mask package too:
    powershell -ExecutionPolicy Bypass -File .\tools\refresh-mission.ps1 -InstallDeps -Install

.EXAMPLE
    # Re-run the tooling over the repo copy without touching the game:
    powershell -ExecutionPolicy Bypass -File .\tools\refresh-mission.ps1 -SkipImport
#>
[CmdletBinding()]
param(
    [string]$Mission,
    [switch]$SkipImport,
    [switch]$Install,
    [switch]$InstallDeps,
    [string]$StreamingAssetsDir
)

$ErrorActionPreference = "Stop"

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
$missionsDir = Join-Path $repoRoot "integration\missions"
. (Join-Path $scriptDir "lib\common.ps1")

# Not a param default: those are bound before $repoRoot exists.
if (-not $Mission) { $Mission = Get-ActiveMission $repoRoot }
Write-Host "Mission: $Mission"

# --- Find Python -------------------------------------------------------------
$py = Get-Python
if (-not $py) {
    Write-Host ""
    Write-Host "Python 3 was not found on PATH, so the mission tooling cannot run here." -ForegroundColor Yellow
    Write-Host "Either:"
    Write-Host "  * install it from https://www.python.org/downloads/windows/"
    Write-Host "    (tick 'Add python.exe to PATH' in the installer), then re-run this; or"
    Write-Host "  * push the imported mission and have it processed for you:"
    Write-Host "      powershell -ExecutionPolicy Bypass -File .\tools\import-mission.ps1 -Mission `"$Mission`""
    Write-Host "      git add integration\missions ; git commit -m `"Import edited mission`" ; git push"
    exit 1
}
Write-Host ("Python: {0} {1}" -f $py.Exe, ($py.Pre -join " "))

function Invoke-Py {
    # NOTE: the parameter must NOT be called $Args - that is an automatic
    # PowerShell variable and cannot be bound.
    param([string]$Script, [string[]]$ScriptArgs)
    $argList = @($py.Pre) + @(Join-Path $missionsDir $Script) + $ScriptArgs
    & $py.Exe @argList
    if ($LASTEXITCODE -ne 0) { throw "$Script failed (exit $LASTEXITCODE)" }
}

# --- 1. Import ---------------------------------------------------------------
if (-not $SkipImport) {
    Write-Host "`n[1/7] importing '$Mission' from the game..." -ForegroundColor Cyan
    # NOTE: splat a HASHTABLE, not an array. Array splatting binds
    # positionally, so @("-Mission", $Mission) would put the literal string
    # "-Mission" in $Mission and the mission name in the next positional
    # parameter ($StreamingAssetsDir).
    $importArgs = @{ Mission = $Mission }
    if ($StreamingAssetsDir) { $importArgs["StreamingAssetsDir"] = $StreamingAssetsDir }
    & (Join-Path $scriptDir "import-mission.ps1") @importArgs
} else {
    Write-Host "`n[1/7] import skipped (-SkipImport)" -ForegroundColor DarkGray
}

$missionFile = Join-Path $missionsDir "$Mission.ini"
if (-not (Test-Path -LiteralPath $missionFile)) {
    throw "mission not in the repo: $missionFile (drop -SkipImport, or check the name)"
}

# --- 2. Dress the civilian traffic -------------------------------------------
Write-Host "`n[2/7] dressing civilian traffic..." -ForegroundColor Cyan
Invoke-Py "refine_civ_traffic.py" @("--mission", $Mission, "--repo-only", "--rename-to", $Mission)

# --- 3. Depth pass -----------------------------------------------------------
Write-Host "`n[3/7] adding civilian and natural depth..." -ForegroundColor Cyan
Invoke-Py "add_civ_depth.py" @("--mission", $Mission, "--write")

# --- 3b. Sanctioned shipping ---------------------------------------------------
# Idempotent: no-op when the fleet is already in the mission, and skips
# gracefully in a mission with no seized rigs to lift from.
Write-Host "`n[3b/7] sanctioned tanker fleet..." -ForegroundColor Cyan
Invoke-Py "add_sanctioned_shipping.py" @("--mission", $Mission, "--write")

# --- 3c. RSA reinforcements + Townsville --------------------------------------
# Idempotent: skips when already present, and skips missions with no Type 004.
Write-Host "`n[3c/7] RSA reinforcements + RAAF Townsville..." -ForegroundColor Cyan
Invoke-Py "add_nfiii_reinforcements.py" @("--mission", $Mission, "--write")

# --- 4. Name any placeholder formations --------------------------------------
Write-Host "`n[4/7] naming placeholder formations..." -ForegroundColor Cyan
Invoke-Py "name_formations.py" @("--mission", $Mission, "--write")

# --- 5. Keep everything in the water -----------------------------------------
Write-Host "`n[5/7] checking nothing sits on land..." -ForegroundColor Cyan
if ($InstallDeps) {
    Write-Host "  fetching the land-mask package..."
    $pipArgs = @($py.Pre) + @("-m", "pip", "install", "--quiet", "global-land-mask", "numpy")
    & $py.Exe @pipArgs
    if ($LASTEXITCODE -ne 0) { Write-Warning "pip install failed - the land check may not run" }
}
$probeArgs = @($py.Pre) + @("-c", "import global_land_mask")
& $py.Exe @probeArgs *> $null
if ($LASTEXITCODE -eq 0) {
    Invoke-Py "fix_land_positions.py" @("--mission", $Mission, "--write")
} else {
    Write-Warning "land mask not installed - skipping the water check."
    Write-Warning "Re-run once with -InstallDeps to enable it."
}

# --- 6. Squadron references ---------------------------------------------------
# The editor happily writes SquadronReference values the providing mod does not
# define; those aircraft then spawn with nothing resolved. --spread also undoes
# the earlier repair for it, now that the SEST packs define the missing
# squadrons - see the tool's docstring for why it is deliberately narrow.
Write-Host "`n[6/7] checking squadron references..." -ForegroundColor Cyan
Invoke-Py "fix_squadron_refs.py" @("--mission", $Mission, "--spread", "--write")

# --- 7. Put it back in the game ----------------------------------------------
if ($Install) {
    Write-Host "`n[7/7] installing back into the game..." -ForegroundColor Cyan
    $installArgs = @{}
    if ($StreamingAssetsDir) { $installArgs["StreamingAssetsDir"] = $StreamingAssetsDir }
    & (Join-Path $scriptDir "install-sest-packs.ps1") @installArgs
} else {
    Write-Host "`n[7/7] not installed (pass -Install to deploy it back)" -ForegroundColor DarkGray
}

Write-Host "`nDone. '$Mission' has been refreshed." -ForegroundColor Green
Write-Host "Commit the result so the repo keeps your edits:"
Write-Host "  git add integration\missions"
Write-Host "  git commit -m `"Refresh $Mission`""
Write-Host "  git push"
