<#
.SYNOPSIS
    Copy a mission you edited in the game back into this repo.

.DESCRIPTION
    The Sea Power mission editor saves into the game's own
    user\missions\user_missions folder, so a mission you just edited lives
    outside the repo. This finds the game the same way the other tools do,
    copies the named mission (or every user mission) into
    integration\missions\, and normalises CRLF to LF so the diff stays clean.

    Your edited file becomes the authoritative copy. Re-run the mission
    tooling afterwards (civilian dressing, depth pass, land check) - all of
    it is idempotent and preserves every placement you made.

.EXAMPLE
    # From the repo root, with the game closed:
    powershell -ExecutionPolicy Bypass -File .\tools\import-mission.ps1
    git add integration\missions ; git commit -m "Import edited mission" ; git push

.EXAMPLE
    # Bring in everything you have edited:
    powershell -ExecutionPolicy Bypass -File .\tools\import-mission.ps1 -All
#>
[CmdletBinding()]
param(
    [string]$Mission,
    [switch]$All,
    [string]$StreamingAssetsDir
)

$ErrorActionPreference = "Stop"

# -Mission is resolved after $repoRoot is known, below.
if ($Mission -and $Mission.StartsWith("-")) {
    throw "Mission name looks like a switch ('$Mission'). If you are calling this from another script, splat a HASHTABLE (@{Mission=...}) - array splatting binds positionally."
}
if ($StreamingAssetsDir -and -not (Test-Path -LiteralPath $StreamingAssetsDir)) {
    throw "StreamingAssetsDir does not exist: '$StreamingAssetsDir'"
}

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
. (Join-Path $scriptDir "lib\common.ps1")

if (-not $Mission -and -not $All) {
    $Mission = Get-ActiveMission $repoRoot
    Write-Host "No -Mission given; using the active mission: $Mission"
}
$destDir = Join-Path $repoRoot "integration\missions"

# --- Locate StreamingAssets --------------------------------------------------
if (-not $StreamingAssetsDir) {
    $StreamingAssetsDir = Find-StreamingAssets
    if (-not $StreamingAssetsDir) {
        throw "Could not auto-detect Sea Power's StreamingAssets. Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'"
    }
}

$srcDir = Join-Path $StreamingAssetsDir "user\missions\user_missions"
if (-not (Test-Path $srcDir)) { throw "user missions folder not found: $srcDir" }
Write-Host "Importing from: $srcDir`n"

$files = if ($All) {
    Get-ChildItem -LiteralPath $srcDir -Filter "*.ini" | Where-Object { $_.Name -ne "_info.ini" }
} else {
    $one = Join-Path $srcDir "$Mission.ini"
    if (-not (Test-Path -LiteralPath $one)) {
        throw "mission not found: $one`nAvailable: " + ((Get-ChildItem -LiteralPath $srcDir -Filter '*.ini' | ForEach-Object { $_.BaseName }) -join ', ')
    }
    Get-Item -LiteralPath $one
}

$imported = 0
foreach ($f in $files) {
    $dest = Join-Path $destDir $f.Name
    $text = Get-Content -LiteralPath $f.FullName -Raw
    $lf = $text -replace "`r`n", "`n"
    if ((Test-Path -LiteralPath $dest) -and ((Get-Content -LiteralPath $dest -Raw) -eq $lf)) {
        Write-Host ("  unchanged  {0}" -f $f.Name)
        continue
    }
    # Write LF-only so the repo diff shows real edits, not line endings.
    [System.IO.File]::WriteAllText($dest, $lf)
    Write-Host ("  imported   {0}  ({1:N0} bytes, saved {2})" -f $f.Name, $f.Length, $f.LastWriteTime)
    $imported++
}

Write-Host "`n$imported mission(s) imported into integration\missions."
Write-Host "Next:"
Write-Host "  git add integration\missions"
Write-Host "  git commit -m `"Import edited mission`""
Write-Host "  git push"
Write-Host "Then the mission tooling can be re-run over your edits (it is idempotent)."
