<#
.SYNOPSIS
    tools\sync-sest.ps1 stops while the Workshop copy of SEST (3812461539) is
    on disk, names the two ways out, refuses both copies at once, and goes
    on with -SkipInstall.

.DESCRIPTION
    A synthetic workshop content folder and StreamingAssets folder stand in
    for Steam's and the game's (-WorkshopContentDir, -StreamingAssetsDir).
    The guard runs before the pull, so the stop cases touch no git at all;
    the two cases that go past it skip the pull, the install and the order
    step (-SkipPull -SkipInstall -SkipOrder -AnyBranch), so the only git
    command they run is the branch check's read of HEAD in this repository.
    Exit code 1 on any failed check.

        pwsh -File tools/tests/test_sync_sest_guard.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$sync = Join-Path (Split-Path -Parent $PSScriptRoot) "sync-sest.ps1"
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("sest-sync-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$failed = 0

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}

# Every stream, line by line as it streams, so what the script printed
# before it threw is kept too; the thrown error is the last line.
function Run([hashtable]$params) {
    $lines = New-Object System.Collections.Generic.List[string]
    try { & $sync @params *>&1 | ForEach-Object { $lines.Add("$_") } } catch { $lines.Add("ERROR: $($_.Exception.Message)") }
    return ($lines -join "`n")
}

try {
    $ws = Join-Path $root "content"
    New-Item -ItemType Directory -Force -Path (Join-Path $ws "3812461539") | Out-Null
    [IO.File]::WriteAllText((Join-Path (Join-Path $ws "3812461539") "_info.ini"), "[Language_en]`r`nName=SEST Integration Pack`r`n")
    $wsNone = Join-Path $root "content-none"
    New-Item -ItemType Directory -Force -Path $wsNone | Out-Null
    $saEmpty = Join-Path $root "sa-empty"
    New-Item -ItemType Directory -Force -Path $saEmpty | Out-Null
    $saLocal = Join-Path $root "sa-local"
    New-Item -ItemType Directory -Force -Path (Join-Path $saLocal "SEST_Integration") | Out-Null

    # 1. the Workshop copy alone, a normal run: stop, say both ways out, install nothing
    $text = Run @{ WorkshopContentDir = $ws; StreamingAssetsDir = $saEmpty; SkipPull = $true }
    Check ($text -match "ERROR: the Workshop copy of SEST \(3812461539\) is on disk") "stops with the Workshop copy on disk"
    Check ($text -match "Unsubscribe from 3812461539") "way out 1: unsubscribe and run again"
    Check ($text -match "re-run with -SkipInstall") "way out 2: keep the Workshop copy with -SkipInstall"
    Check ($text -match "never load both") "says the game must never load both"
    Check (-not (Test-Path -LiteralPath (Join-Path $saEmpty "SEST_Integration"))) "nothing was installed"
    Check (-not ($text -match "pulling")) "stopped before the pull step"

    # 2. both copies on disk: refused even with -SkipInstall
    $text = Run @{ WorkshopContentDir = $ws; StreamingAssetsDir = $saLocal; SkipPull = $true; SkipInstall = $true }
    Check ($text -match "ERROR: both copies of SEST are on disk") "both copies: refused with -SkipInstall too"
    Check ($text -match "delete the local folder") "both copies: says to delete the local folder or unsubscribe"

    # 3. the Workshop copy alone with -SkipInstall: goes on, says so
    $text = Run @{ WorkshopContentDir = $ws; StreamingAssetsDir = $saEmpty; SkipPull = $true; SkipInstall = $true; SkipOrder = $true; AnyBranch = $true }
    Check (-not ($text -match "ERROR:")) "-SkipInstall: no error ($(($text -split "`n" | Where-Object { $_ -match 'ERROR' }) -join ' '))"
    Check ($text -match "Workshop copy of SEST on disk" -and $text -match "keeps 3812461539 at position 1") "-SkipInstall: says the order step keeps the item at position 1"
    Check ($text -match "Done\.") "-SkipInstall: ran to the end"

    # 4. no Workshop copy: nothing said about it
    $text = Run @{ WorkshopContentDir = $wsNone; StreamingAssetsDir = $saEmpty; SkipPull = $true; SkipInstall = $true; SkipOrder = $true; AnyBranch = $true }
    Check (-not ($text -match "Workshop copy")) "no Workshop copy: the guard is silent"
    Check ($text -match "Done\.") "no Workshop copy: ran to the end"
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
