<#
.SYNOPSIS
    MNO file-layer probe: find out how Sea Power 0.9.x file layers work before any per-mission
    [Sonar] override is written. Scan first, then install ONE probe at a time, look, uninstall.
.DESCRIPTION
    -Scan     reads (never runs, never changes) the game's script assemblies in Sea Power_Data\Managed
              and lists the type, field, method and literal-string names about layers, overrides,
              mounts and missions; lists every overrides\ folder in StreamingAssets and the Workshop
              mods with what each file adds or changes; records the installed environment.ini [Sonar]
              keys and its SHA-256. Writes Downloads\MNO-LayerProbe-scan-<time>.zip.
    -Install  one probe (A-mod, A-user1, A-user2, A2, B1, B2, B3, C, D; see
              docs\environment\SENSOR-PC-TESTS.md). Refuses to overwrite anything.
    -Uninstall <probe|all> deletes exactly the files a probe wrote, and only if unchanged.
    -Status   lists installed probes and what to look for.
    -Collect  zips the probe manifest, the scans and Player.log into Downloads.
    No Steam upload, no Workshop change, no git operation, no vanilla file is written.
    Written 19 Nov 2026; not yet run on Windows (the build container has no PowerShell).
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Scan
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install A-mod
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install B1
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install C -From B1
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall all
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir = '',
    [switch]$Scan,
    [ValidateSet('', 'A-mod', 'A-user1', 'A-user2', 'A2', 'B1', 'B2', 'B3', 'C', 'D')][string]$Install = '',
    [string]$Mission = '',
    [string]$Template = '',
    [ValidateSet('', 'B1', 'B2', 'B3')][string]$From = '',
    [ValidateSet('', 'all', 'A-mod', 'A-user1', 'A-user2', 'A2', 'B1', 'B2', 'B3', 'C', 'D')][string]$Uninstall = '',
    [switch]$Status,
    [switch]$Collect
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $here)
. (Join-Path $repoRoot 'tools\lib\common.ps1')

if (-not $StreamingAssetsDir) { $StreamingAssetsDir = & { Set-StrictMode -Off; Find-StreamingAssets } }
if (-not $StreamingAssetsDir -or -not (Test-Path -LiteralPath $StreamingAssetsDir -PathType Container)) {
    throw "Sea Power's StreamingAssets was not found. Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'"
}
# Absolute, no trailing backslash: PowerShell 5.1 would otherwise pass '...StreamingAssets\"' to Python as one broken argument.
$StreamingAssetsDir = (Resolve-Path -LiteralPath $StreamingAssetsDir).ProviderPath.TrimEnd('\', '/')
$dataDir = Split-Path -Parent $StreamingAssetsDir
$py = & { Set-StrictMode -Off; Get-Python }
if (-not $py) { throw 'Python 3.10 or newer is required (python.org installer; tick "Add to PATH").' }
$tool = Join-Path $here 'tools\probe_file_layers.py'
$outDir = Join-Path $here 'out\layer-probes'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Invoke-Probe([string[]]$arguments) {
    $all = @($py.Pre) + @($tool) + $arguments
    & $py.Exe @all
    if ($LASTEXITCODE -ne 0) { throw "probe_file_layers.py stopped (exit $LASTEXITCODE); nothing further was done." }
}

function Get-DownloadsFolder {
    try {
        $p = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
        if ($p -and (Test-Path -LiteralPath $p)) { return $p }
    } catch { }
    $fallback = Join-Path $env:USERPROFILE 'Downloads'
    New-Item -ItemType Directory -Force -Path $fallback | Out-Null
    return $fallback
}

function Assert-GameClosed {
    if (& { Set-StrictMode -Off; Test-SeaPowerRunning }) { throw 'Close Sea Power first: probes are installed and removed with the game closed.' }
}

$did = $false
if ($Scan) {
    $did = $true
    $managed = Join-Path $dataDir 'Managed'
    $dlls = @(Get-ChildItem -LiteralPath $managed -Filter '*.dll' -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^(Sea ?Power|Seapower)|^Assembly-CSharp' })
    if ($dlls.Count -eq 0) { Write-Warning "No Sea Power script assembly found in $managed" }
    foreach ($d in $dlls) {
        Write-Host "Reading $($d.Name) (metadata only; the game is not run)"
        Invoke-Probe @('scan-dll', $d.FullName, '--out', (Join-Path $outDir ("scan-dll-" + $d.BaseName + ".json")))
    }
    Invoke-Probe @('scan-mods', $StreamingAssetsDir, '--original', (Join-Path $StreamingAssetsDir 'original'),
        '--out', (Join-Path $outDir 'scan-mods-streamingassets.json'))
    $ws = & { Set-StrictMode -Off; Find-WorkshopContent }
    if ($ws) {
        Invoke-Probe @('scan-mods', $ws, '--original', (Join-Path $StreamingAssetsDir 'original'),
            '--out', (Join-Path $outDir 'scan-mods-workshop.json'))
    }
    Invoke-Probe @('capture-env', $StreamingAssetsDir, '--out', (Join-Path $outDir 'environment-installed.json'))
    $zip = Join-Path (Get-DownloadsFolder) ("MNO-LayerProbe-scan-" + (Get-Date -Format 'yyyyMMdd-HHmmss') + ".zip")
    Compress-Archive -Path (Join-Path $outDir '*.json') -DestinationPath $zip -Force
    Write-Host ""
    Write-Host "Scan written to $zip - send it. Nothing in the game was changed."
}

if ($Install) {
    $did = $true
    Assert-GameClosed
    $probeArgs = @('install', $Install, '--streaming-assets', $StreamingAssetsDir)
    if ($Install -match '^(B1|B2|B3|C|D)$') {
        if (-not $Mission) {
            $Mission = Join-Path $StreamingAssetsDir 'user\missions\user_missions\MNO Weather Lab - Hormuz.ini'
        }
        if (-not (Test-Path -LiteralPath $Mission -PathType Leaf)) {
            throw "Mission file not found: $Mission. Install the Weather Lab first (RUN-WEATHER-LAB.ps1 -Quick) or pass -Mission <path to a .ini>."
        }
        $Mission = (Resolve-Path -LiteralPath $Mission).ProviderPath   # a relative path would put the probe in the wrong folder
        $probeArgs += @('--mission', $Mission)
        if ($Template) { $probeArgs += @('--template', $Template) }
        elseif ($From) { $probeArgs += @('--from', $From) }
        elseif ($Install -match '^(C|D)$') { throw "-Install $Install needs -From B1/B2/B3 (the location a B probe proved) or -Template." }
    }
    Invoke-Probe $probeArgs
    if ($Install -in @('A-mod', 'A2')) {
        Write-Host ""
        Write-Host "Now open Sea Power's Mod Manager, enable the probe mod, drag it to the TOP of the list (top wins), Apply,"
        Write-Host "then quit and restart the game before you look. Disable it again before -Uninstall."
    }
}

if ($Uninstall) {
    $did = $true
    Assert-GameClosed
    Invoke-Probe @('uninstall', $Uninstall, '--streaming-assets', $StreamingAssetsDir)
    Write-Host "If a probe mod was enabled in the Mod Manager, it is gone now; the Mod Manager may show it as missing once."
}

if ($Status) {
    $did = $true
    Invoke-Probe @('status', '--streaming-assets', $StreamingAssetsDir)
}

if ($Collect) {
    $did = $true
    $stage = Join-Path $env:TEMP ("MNO-LayerProbe-results-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    Get-ChildItem -LiteralPath $outDir -File | Copy-Item -Destination $stage
    foreach ($s in @((Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power\Player.log'),
                     (Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power\Player-prev.log'))) {
        if (Test-Path -LiteralPath $s) { Copy-Item -LiteralPath $s -Destination $stage }
    }
    $stamp = Split-Path -Leaf $stage
    $zip = Join-Path (Get-DownloadsFolder) ($stamp + ".zip")
    # RESULTS.txt sits beside the ZIP, not inside it: Explorer cannot save edits back into a ZIP.
    $note = Join-Path (Get-DownloadsFolder) ($stamp + "-RESULTS.txt")
    @('MNO layer probe results', '', 'For each probe you tried, one line: what you saw, for example',
      '  A-mod: F-14A shows "F-14A MNO-PROBE-A"; F-14A squadrons and description intact; other aircraft normal',
      '  B1: not seen (after a restart)', '  C: Ocean Noise 75 -> 105 dB before 1:00; sky and night normal; vanilla Hormuz normal after', '') |
        Set-Content -LiteralPath $note -Encoding UTF8
    try { Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -Force -ErrorAction Stop }
    catch { Write-Warning "Could not write $zip ($($_.Exception.Message)). The files are in $stage"; return }
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Results written to $zip"
    Write-Host "Fill in $note in Notepad (or just reply with one line per probe) and send both."
}

if (-not $did) {
    Write-Host 'Nothing to do. Use -Scan, -Install <probe>, -Uninstall <probe|all>, -Status or -Collect (see the examples at the top).'
}
