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
      4. water    - move any vessel or sea life that sits on land into the
                    water (fix_land_positions.py)
      5. install  - copy the result back into the game (only with -Install)

    Every step is idempotent and preserves your placements, waypoints and
    formations, so it is safe to run after each editing session.

    Needs Python 3 on PATH. Step 4 also needs the land mask package; pass
    -InstallDeps once to fetch it, or the step is skipped with a warning.

.EXAMPLE
    # After editing NORTHERN FRONT III in the mission editor (game closed):
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
    [string]$Mission = "NORTHERN FRONT III",
    [switch]$SkipImport,
    [switch]$Install,
    [switch]$InstallDeps,
    [string]$StreamingAssetsDir
)

$ErrorActionPreference = "Stop"

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
$missionsDir = Join-Path $repoRoot "integration\missions"

# --- Find Python -------------------------------------------------------------
function Test-Python {
    # A candidate only counts if it actually runs and reports Python 3.
    # (The Windows Store ships a stub 'python.exe' that just opens the Store,
    # so presence on PATH proves nothing.)
    param([string]$Exe, [string[]]$Pre)
    try {
        $probe = @($Pre) + @("-c", "import sys; print(sys.version_info[0])")
        $out = & $Exe @probe 2>$null
        if ($LASTEXITCODE -eq 0 -and ("$out".Trim() -eq "3")) {
            return @{ Exe = $Exe; Pre = $Pre }
        }
    } catch { }
    return $null
}

function Get-Python {
    # Returns @{ Exe = <path or 'py'>; Pre = <array of leading args> }
    foreach ($cmd in "python", "python3") {
        $c = Get-Command $cmd -ErrorAction SilentlyContinue
        if (-not ($c -and $c.Source)) { continue }
        $found = Test-Python $c.Source @()
        if ($found) { return $found }
    }
    # The py launcher ships with the python.org installer.
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        $found = Test-Python "py" @("-3")
        if ($found) { return $found }
    }
    # Common install locations, in case PATH was never set up.
    $candidates = @()
    foreach ($root in @("$env:LOCALAPPDATA\Programs\Python", "$env:ProgramFiles\Python",
                        "${env:ProgramFiles(x86)}\Python", "C:\Python312", "C:\Python311")) {
        if (Test-Path -LiteralPath $root) {
            $candidates += Get-ChildItem -LiteralPath $root -Filter "python.exe" -Recurse -Depth 1 -ErrorAction SilentlyContinue
        }
    }
    foreach ($c in $candidates) {
        $found = Test-Python $c.FullName @()
        if ($found) { return $found }
    }
    return $null
}

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
    Write-Host "`n[1/5] importing '$Mission' from the game..." -ForegroundColor Cyan
    $importArgs = @("-Mission", $Mission)
    if ($StreamingAssetsDir) { $importArgs += @("-StreamingAssetsDir", $StreamingAssetsDir) }
    & (Join-Path $scriptDir "import-mission.ps1") @importArgs
} else {
    Write-Host "`n[1/5] import skipped (-SkipImport)" -ForegroundColor DarkGray
}

$missionFile = Join-Path $missionsDir "$Mission.ini"
if (-not (Test-Path -LiteralPath $missionFile)) {
    throw "mission not in the repo: $missionFile (drop -SkipImport, or check the name)"
}

# --- 2. Dress the civilian traffic -------------------------------------------
Write-Host "`n[2/5] dressing civilian traffic..." -ForegroundColor Cyan
Invoke-Py "refine_civ_traffic.py" @("--mission", $Mission, "--repo-only", "--rename-to", $Mission)

# --- 3. Depth pass -----------------------------------------------------------
Write-Host "`n[3/5] adding civilian and natural depth..." -ForegroundColor Cyan
Invoke-Py "add_civ_depth.py" @("--mission", $Mission, "--write")

# --- 4. Keep everything in the water -----------------------------------------
Write-Host "`n[4/5] checking nothing sits on land..." -ForegroundColor Cyan
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

# --- 5. Put it back in the game ----------------------------------------------
if ($Install) {
    Write-Host "`n[5/5] installing back into the game..." -ForegroundColor Cyan
    $installArgs = @()
    if ($StreamingAssetsDir) { $installArgs += @("-StreamingAssetsDir", $StreamingAssetsDir) }
    & (Join-Path $scriptDir "install-sest-packs.ps1") @installArgs
} else {
    Write-Host "`n[5/5] not installed (pass -Install to deploy it back)" -ForegroundColor DarkGray
}

Write-Host "`nDone. '$Mission' has been refreshed." -ForegroundColor Green
Write-Host "Commit the result so the repo keeps your edits:"
Write-Host "  git add integration\missions"
Write-Host "  git commit -m `"Refresh $Mission`""
Write-Host "  git push"
