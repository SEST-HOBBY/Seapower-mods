<#
.SYNOPSIS
    Capture every installed Workshop mod and the live install in one step,
    and save a review ZIP of what changed.

.DESCRIPTION
    Runs, in order, what the "A Workshop refresh for review" block in
    docs\packaging-and-recovery.md runs by hand:

      1. capture-context.ps1 -Redact       (data\install-snapshot\)
      2. export-mod-configs.ps1 -CheckUpdates -ReportPath ...workshop-updates.txt
         export-mod-configs.ps1            (mods-source\, Workshop mods only)
      3. tools\fingerprint_mods.py, tools\workshop_refresh_summary.py and
         tools\check_inventory.py
      4. collects the changed and new mod files, the snapshot and the reports
      5. zips them into a review bundle outside the clone

    What it writes: data\install-snapshot\, mods-source\ (the Workshop mods'
    folders and _export-manifest.csv), data\mod-fingerprints.json, and the
    review folder and ZIP under -OutputDir. What it never does: commit, push,
    publish or upload anything; install, build or copy a DLL; change Steam,
    the game folder, BepInEx or the Workshop folders, which it only reads.
    It does not export the game's own files (no -IncludeVanilla), so
    mods-source\_vanilla keeps the build the pack targets even when the PC
    is on Steam's public beta.

    A stage that fails is recorded in the bundle's README.txt and the next
    stage still runs, so a failed diagnostic does not lose the Workshop
    export. It stops before writing anything only when Sea Power is running,
    the clone has uncommitted changes, the clone is on the deploy branch, the
    Workshop folder or Python 3 cannot be found, or the output path exists.

.EXAMPLE
    # game closed, on the chore/workshop-refresh-YYYYMMDD branch:
    powershell -ExecutionPolicy Bypass -File .\tools\capture-all-mod-updates.ps1
#>
[CmdletBinding()]
param(
    # Steam's Workshop folder for Sea Power; found in the Steam libraries when omitted.
    [string]$WorkshopContentDir = "",
    # The commit holding the previous capture; workshop_refresh_summary.py
    # finds it in the history when omitted.
    [string]$BaselineRef = "",
    # Where the review folder goes; the ZIP is written beside it.
    [string]$OutputDir = "",
    # Skip the full export and keep only the read-only update check.
    [switch]$SkipExport
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
. (Join-Path $PSScriptRoot "lib\common.ps1")

function Invoke-Python([object]$Python, [string[]]$Arguments) {
    # Windows PowerShell 5.1 turns a native command's stderr into an error
    # record when it is redirected, which "Stop" would make fatal. Run with
    # "Continue" so the output is kept as text and the exit code decides.
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $args2 = @($Python.Pre) + @($Arguments)
        $out = @(& $Python.Exe @args2 2>&1 | ForEach-Object { [string]$_ })
        return [pscustomobject]@{ Exit = $LASTEXITCODE; Lines = $out }
    }
    finally { $ErrorActionPreference = $saved }
}

Push-Location -LiteralPath $repo
try {
    if (Test-SeaPowerRunning) {
        throw "Close Sea Power before capturing its installed state."
    }
    if (!(Test-Path -LiteralPath (Join-Path $repo ".git"))) {
        throw "Run from a Git clone of the repository."
    }
    $branch = "$(& git branch --show-current)".Trim()
    $deployFile = Join-Path $repo "data\deploy-branch.txt"
    $deploy = if (Test-Path -LiteralPath $deployFile) { "$(Get-Content -LiteralPath $deployFile -TotalCount 1)".Trim() } else { "" }
    if ($deploy -and $branch -eq $deploy) {
        throw "On the deploy branch $deploy. A capture goes on its own chore/workshop-refresh-YYYYMMDD branch first."
    }
    if (@(& git status --porcelain).Count -gt 0) {
        throw "The clone has uncommitted changes. Commit or remove them first so the capture's changes stand alone."
    }
    if (!$WorkshopContentDir) { $WorkshopContentDir = Find-WorkshopContent }
    if (!$WorkshopContentDir -or !(Test-Path -LiteralPath $WorkshopContentDir -PathType Container)) {
        throw "Sea Power's Workshop folder was not found. Pass -WorkshopContentDir."
    }
    $python = Get-Python
    if (!$python) { throw "Python 3 is required for the inventory tools." }

    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    if (!$OutputDir) {
        $OutputDir = Join-Path $env:USERPROFILE ("Downloads\SEST-Workshop-Capture-" + $stamp)
    }
    $zip = "$OutputDir.zip"
    if ((Test-Path -LiteralPath $OutputDir) -or (Test-Path -LiteralPath $zip)) {
        throw "The capture destination exists. Pass a different -OutputDir."
    }
    $bundle = Join-Path $OutputDir "review"
    New-Item -ItemType Directory -Path $bundle -Force | Out-Null
    $issues = New-Object System.Collections.Generic.List[string]

    $dirs = @(Get-ChildItem -LiteralPath $WorkshopContentDir -Directory |
        Where-Object { $_.Name -match '^\d{8,12}$' })
    Write-Host "Workshop folders found: $($dirs.Count)"

    Write-Host "[1/5] Capturing the live install (Steam record, DLLs, logs)..."
    try {
        & (Join-Path $PSScriptRoot "capture-context.ps1") -Redact
        if (!$?) { throw "capture-context.ps1 returned an unsuccessful status." }
    }
    catch {
        $reason = "Live capture failed: $($_.Exception.Message)"
        $issues.Add($reason)
        @($reason, [string]$_.ScriptStackTrace) |
            Set-Content -LiteralPath (Join-Path $bundle "capture-context-error.txt") -Encoding UTF8
        Write-Warning "The live capture is incomplete. Continuing with the Workshop export."
    }

    Write-Host "[2/5] Checking and exporting the Workshop mods' text files..."
    $updatesPath = Join-Path $repo "data\install-snapshot\workshop-updates.txt"
    try {
        & (Join-Path $PSScriptRoot "export-mod-configs.ps1") -WorkshopContentDir $WorkshopContentDir -CheckUpdates -ReportPath $updatesPath
        if (!$?) { throw "the update check returned an unsuccessful status." }
    }
    catch {
        $issues.Add("Mod update check failed: $($_.Exception.Message)")
        Write-Warning "The update check is incomplete. Continuing with the full export."
    }
    if (!$SkipExport) {
        try {
            & (Join-Path $PSScriptRoot "export-mod-configs.ps1") -WorkshopContentDir $WorkshopContentDir
            if (!$?) { throw "the export returned an unsuccessful status." }
        }
        catch {
            $issues.Add("Mod export failed: $($_.Exception.Message)")
            Write-Warning "The export is incomplete. Saving what was collected."
        }
    }

    Write-Host "[3/5] Fingerprinting, summarising and checking the inventory..."
    $fp = Invoke-Python $python @("tools/fingerprint_mods.py")
    $fp.Lines | ForEach-Object { Write-Host $_ }
    if ($fp.Exit -ne 0) { $issues.Add("fingerprint_mods.py exited $($fp.Exit).") }
    $summaryArgs = @("tools/workshop_refresh_summary.py")
    if ($BaselineRef) { $summaryArgs += @("--since", $BaselineRef, "--since-export", $BaselineRef) }
    $summary = Invoke-Python $python $summaryArgs
    $summary.Lines | ForEach-Object { Write-Host $_ }
    if ($summary.Exit -ne 0) { $issues.Add("workshop_refresh_summary.py exited $($summary.Exit).") }
    $inventory = Invoke-Python $python @("tools/check_inventory.py")
    $inventory.Lines | Set-Content -LiteralPath (Join-Path $bundle "inventory-gate.txt") -Encoding UTF8
    Write-Host "Inventory gate: $(if ($inventory.Exit -eq 0) { 'PASS' } else { 'drift found (report saved)' })"

    Write-Host "[4/5] Collecting the changed and new mod files..."
    $changed = @(& git -c core.quotepath=off diff --name-only -- mods-source)
    $untracked = @(& git -c core.quotepath=off ls-files --others --exclude-standard -- mods-source)
    $delta = @(@($changed) + @($untracked) | Where-Object { $_ } | Sort-Object -Unique)
    & git diff --name-status -- mods-source data/mod-fingerprints.json |
        Set-Content -LiteralPath (Join-Path $bundle "mod-export-diff.txt") -Encoding UTF8
    & git status --short -- mods-source data/mod-fingerprints.json data/install-snapshot |
        Set-Content -LiteralPath (Join-Path $bundle "git-status.txt") -Encoding UTF8
    $changedRoot = Join-Path $bundle "changed-mod-configs"
    $copied = 0
    foreach ($rel in $delta) {
        if ($rel -notmatch '^mods-source/') { continue }
        $src = Join-Path $repo $rel
        if (!(Test-Path -LiteralPath $src -PathType Leaf)) { continue }
        $dest = Join-Path $changedRoot $rel
        $parent = Split-Path -Parent $dest
        if (!(Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Copy-Item -LiteralPath $src -Destination $dest
        $copied++
    }

    $snapshot = Join-Path $repo "data\install-snapshot"
    $snapOut = Join-Path $bundle "snapshot"
    New-Item -ItemType Directory -Path $snapOut -Force | Out-Null
    foreach ($name in @("workshop-subscriptions.txt", "workshop-updates.txt",
                        "workshop-refresh-summary.txt", "plugin-dlls.txt",
                        "load-order.live.txt", "changelog.live.txt",
                        "player.problems.txt", "player-prev.problems.txt")) {
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
    $readme = @(
        "SEST ALL-MOD UPDATE CAPTURE",
        "Captured: $(Get-Date -Format o)",
        "Branch: $branch",
        "Previous capture: $(if ($BaselineRef) { $BaselineRef } else { 'found by workshop_refresh_summary.py' })",
        "Workshop folders: $($dirs.Count)",
        "Changed, new or deleted mod paths: $($delta.Count)",
        "Changed or new mod files copied: $copied",
        "Inventory gate exit: $($inventory.Exit)",
        "Stage problems: $($issues.Count)"
    )
    foreach ($issue in $issues) { $readme += "PROBLEM: $issue" }
    $readme += @(
        "The game's own files were not exported (no -IncludeVanilla).",
        "Steam, the game folder, BepInEx and the Workshop folders were only read.",
        "No DLL was built, copied or installed. Nothing was committed, pushed or uploaded.",
        "Raw Player logs and saves are not in this bundle."
    )
    $readme | Set-Content -LiteralPath (Join-Path $bundle "README.txt") -Encoding UTF8

    Write-Host "[5/5] Writing the review ZIP..."
    Compress-Archive -LiteralPath $bundle -DestinationPath $zip -CompressionLevel Optimal
    if ($issues.Count -eq 0) {
        Write-Host "SEST ALL-MOD CAPTURE COMPLETE" -ForegroundColor Green
    } else {
        Write-Host "SEST CAPTURE PARTIAL: $($issues.Count) stage problem(s), listed in README.txt in the ZIP." -ForegroundColor Yellow
    }
    Write-Host "Workshop folders: $($dirs.Count)"
    Write-Host "Changed, new or deleted mod paths: $($delta.Count)"
    Write-Host "Review ZIP: $zip" -ForegroundColor Green
    Write-Host "Nothing was committed or pushed. Review git status, then commit on this branch."
}
finally { Pop-Location }
