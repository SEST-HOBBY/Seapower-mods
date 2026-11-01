<#
.SYNOPSIS
  Capture all installed Workshop mod updates since the 28 Oct SEST export.
.DESCRIPTION
  Capture Steam subscriptions and DLL hashes, export current mod text configs,
  compare against Git, and save a review ZIP. Nothing is installed or uploaded.
.EXAMPLE
  .\tools\capture-all-mod-updates.ps1
#>
[CmdletBinding()]
param(
    [string]$GameRoot = "C:\Program Files (x86)\Steam\steamapps\common\Sea Power",
    [string]$BaselineRef = "origin/integ/capture-20261028",
    [string]$OutputDir = "",
    [switch]$SkipExport,
    [switch]$SkipBetaBuild
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
Push-Location $repo
try {
    if (Get-Process -Name "Sea Power", "SeaPower" -ErrorAction SilentlyContinue) {
        throw "Close Sea Power before capturing its installed state."
    }
    if (!(Test-Path -LiteralPath (Join-Path $repo ".git"))) {
        throw "Run from a Git clone with a .git directory."
    }
    $branch = (& git branch --show-current).Trim()
    if ($branch -ne "release/sest-workshop-20261101") {
        throw "Switch to release/sest-workshop-20261101 first. Current: $branch"
    }
    $steamApps = Split-Path -Parent (Split-Path -Parent $GameRoot)
    $workshop = Join-Path $steamApps "workshop\content\1286220"
    if (!(Test-Path -LiteralPath $GameRoot -PathType Container)) {
        throw "Game folder missing: $GameRoot"
    }
    if (!(Test-Path -LiteralPath $workshop -PathType Container)) {
        throw "Workshop folder missing: $workshop"
    }
    $py = Get-Command "py" -ErrorAction SilentlyContinue
    $python = Get-Command "python" -ErrorAction SilentlyContinue
    if (!$py -and !$python) { throw "Python 3 is required for SEST inventory tools." }

    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    if (!$OutputDir) {
        $OutputDir = Join-Path $env:USERPROFILE ("Downloads\SEST-Workshop-Capture-" + $stamp)
    }
    $zip = "$OutputDir.zip"
    if ((Test-Path -LiteralPath $OutputDir) -or (Test-Path -LiteralPath $zip)) {
        throw "Capture destination exists. Use a different OutputDir to prevent overwriting."
    }
    $bundle = Join-Path $OutputDir "review"
    New-Item -ItemType Directory -Path $bundle -Force | Out-Null

    $dirs = @(Get-ChildItem -LiteralPath $workshop -Directory |
        Where-Object { $_.Name -match '^\d{8,12}$' })
    Write-Host "Workshop folders detected: $($dirs.Count)"
    Write-Host "[1/6] Capturing Steam Workshop and installed DLLs..."
    & (Join-Path $PSScriptRoot "capture-context.ps1") -Redact
    if (!$?) { throw "Live capture failed; partial data remains in the repo." }

    Write-Host "[2/6] Checking and exporting all Workshop mod text files..."
    $updatesPath = Join-Path $repo "data\install-snapshot\workshop-updates.txt"
    & (Join-Path $PSScriptRoot "export-mod-configs.ps1") -WorkshopContentDir $workshop -CheckUpdates -ReportPath $updatesPath
    if (!$?) { throw "Mod update comparison failed." }
    if (!$SkipExport) {
        & (Join-Path $PSScriptRoot "export-mod-configs.ps1") -WorkshopContentDir $workshop
        if (!$?) { throw "Mod config export failed; partial data preserved." }
    }

    Write-Host "[3/6] Fingerprinting, summarising and checking inventory..."
    if ($py) { & $py.Source -3 "tools/fingerprint_mods.py" }
    else { & $python.Source "tools/fingerprint_mods.py" }
    if ($LASTEXITCODE -ne 0) { throw "Fingerprint update failed." }
    if ($py) { & $py.Source -3 "tools/workshop_refresh_summary.py" --since $BaselineRef --since-export $BaselineRef }
    else { & $python.Source "tools/workshop_refresh_summary.py" --since $BaselineRef --since-export $BaselineRef }
    if ($LASTEXITCODE -ne 0) { throw "Workshop summary failed." }
    if ($py) { $inventory = @(& $py.Source -3 "tools/check_inventory.py" 2>&1) }
    else { $inventory = @(& $python.Source "tools/check_inventory.py" 2>&1) }
    $inventoryExit = $LASTEXITCODE
    $inventory | Set-Content -LiteralPath (Join-Path $bundle "inventory-gate.txt") -Encoding UTF8
    Write-Host "Inventory gate: $(if ($inventoryExit -eq 0) { 'PASS' } else { 'DRIFT detected (report saved)' })"

    Write-Host "[4/6] Collecting changed/new mod configs..."
    $changed = @(& git diff --name-only -- mods-source)
    if ($LASTEXITCODE -ne 0) { throw "Git diff failed." }
    $untracked = @(& git ls-files --others --exclude-standard -- mods-source)
    if ($LASTEXITCODE -ne 0) { throw "Git untracked listing failed." }
    $delta = @($changed + $untracked | Sort-Object -Unique | Where-Object { $_ -ne "" })
    & git diff --name-status -- mods-source data/mod-fingerprints.json |
        Set-Content -LiteralPath (Join-Path $bundle "mod-export-diff.txt") -Encoding UTF8
    & git status --short -- mods-source data/mod-fingerprints.json data/install-snapshot |
        Set-Content -LiteralPath (Join-Path $bundle "git-status.txt") -Encoding UTF8
    $changedRoot = Join-Path $bundle "changed-mod-configs"
    $copied = 0
    foreach ($rel in $delta) {
        if ($rel -notmatch '^mods-source/') { continue }
        $src = Join-Path $repo ($rel.Replace("/", "\"))
        if (!(Test-Path -LiteralPath $src -PathType Leaf)) { continue }
        $dest = Join-Path $changedRoot ($rel.Replace("/", "\"))
        $parent = Split-Path -Parent $dest
        if (!(Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Copy-Item -LiteralPath $src -Destination $dest
        $copied++
    }

    $snapshot = Join-Path $repo "data\install-snapshot"
    $snapOut = Join-Path $bundle "snapshot"
    New-Item -ItemType Directory -Path $snapOut | Out-Null
    $names = @(
        "workshop-subscriptions.txt",
        "workshop-updates.txt",
        "workshop-refresh-summary.txt",
        "plugin-dlls.txt",
        "load-order.live.txt",
        "changelog.live.txt"
    )
    foreach ($name in $names) {
        $f = Join-Path $snapshot $name
        if (Test-Path -LiteralPath $f -PathType Leaf) {
            Copy-Item -LiteralPath $f -Destination (Join-Path $snapOut $name)
        }
    }
    foreach ($item in @(
        @("mods-source\_export-manifest.csv", "export-manifest.csv"),
        @("data\mod-fingerprints.json", "mod-fingerprints.json")
    )) {
        $src = Join-Path $repo $item[0]
        if (Test-Path -LiteralPath $src -PathType Leaf) {
            Copy-Item -LiteralPath $src -Destination (Join-Path $bundle $item[1])
        }
    }
    @(
        "SEST ALL-MOD UPDATE CAPTURE",
        "Captured: $(Get-Date -Format o)",
        "Branch: $branch",
        "Baseline: $BaselineRef",
        "Workshop folders: $($dirs.Count)",
        "Changed/new/deleted mod paths: $($delta.Count)",
        "Changed/new mod files copied: $copied",
        "Inventory gate exit: $inventoryExit",
        "Steam or installed mod files modified: none",
        "Beta test DLLs installed: none",
        "Raw Player logs and user saves intentionally excluded."
    ) | Set-Content -LiteralPath (Join-Path $bundle "README.txt") -Encoding UTF8

    Write-Host "[5/6] Checking beta loader sources and compiling candidate (no installation)..."
    $buildReport = Join-Path $bundle "beta-build.txt"
    if ($SkipBetaBuild) {
        "Beta compilation skipped by -SkipBetaBuild." |
            Set-Content -LiteralPath $buildReport -Encoding UTF8
    }
    else {
        try {
            $betaTest = Join-Path $repo "integration\beta-anchorchain\test_source_contract.py"
            $betaBuilder = Join-Path $repo "integration\beta-anchorchain\build.ps1"
            $log = New-Object System.Collections.Generic.List[string]
            if ($py) { $code = @(& $py.Source -3 $betaTest 2>&1) }
            else { $code = @(& $python.Source $betaTest 2>&1) }
            $exitCode = $LASTEXITCODE
            foreach ($line in $code) { $log.Add([string]$line) }
            if ($exitCode -ne 0) { throw "Beta source-contract tests failed ($exitCode)." }
            $log.Add("Source-contract tests: PASS")
            $output = @(& $betaBuilder -GameRoot $GameRoot 2>&1)
            foreach ($line in $output) { $log.Add([string]$line) }
            $log.Add("Beta build script completed. No DLL installed in Sea Power.")
            $log | Set-Content -LiteralPath $buildReport -Encoding UTF8
            Write-Host "Beta build: see beta-build.txt in capture ZIP" -ForegroundColor Green
        }
        catch {
            @("BETA BUILD NOT VERIFIED / CANDIDATE NOT INSTALLED",
              $_.Exception.Message,
              "This does not invalidate the mod capture. Stable pack and game files remain unchanged.") |
                Set-Content -LiteralPath $buildReport -Encoding UTF8
            Write-Host "Beta build did not complete; error preserved in ZIP. No game DLL was installed." -ForegroundColor Yellow
        }
    }
    Write-Host "[6/6] Creating shareable review ZIP..."
    Compress-Archive -LiteralPath $bundle -DestinationPath $zip -CompressionLevel Optimal
    Write-Host "SEST ALL-MOD CAPTURE COMPLETE" -ForegroundColor Green
    Write-Host "Workshop folders: $($dirs.Count)"
    Write-Host "Changed/new mod paths: $($delta.Count)"
    Write-Host "Review ZIP: $zip" -ForegroundColor Green
    Write-Host "No Steam install, mod order or GitHub contents were changed by capture."
}
finally { Pop-Location }
