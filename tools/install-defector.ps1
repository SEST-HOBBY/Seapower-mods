<#
.SYNOPSIS
    Back up the current Sea Power installation, then install the defector build.
.DESCRIPTION
    Run from the isolated checkout described in defector-handover.md. Verifies
    the exact commit, backs up installed SEST packs, StreamingAssets\user and
    the Sea Power profile, then calls the existing installer without pulling.
    Never merges, resets, stashes or pushes the user's working repository.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')]
    [string]$ExpectedCommit,
    [string]$StreamingAssetsDir
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'lib\common.ps1')

if (Test-SeaPowerRunning) { throw 'Close Sea Power, then run this again.' }
$head = & git -C $repoRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or "$head".Trim() -ne $ExpectedCommit) {
    throw 'This checkout is not the requested defector commit. Nothing installed.'
}
$changes = & git -C $repoRoot status --porcelain
if ($LASTEXITCODE -ne 0 -or $changes) {
    throw 'This installation checkout has local changes. Nothing installed.'
}
$pack = Join-Path $repoRoot 'integration\dist\SEST_Integration'
$mission = 'missions\Tasman Shield\Tasman Shield 08A - The Defector.ini'
if (-not (Test-Path -LiteralPath (Join-Path $pack $mission))) {
    throw 'The built defector mission is missing. Nothing installed.'
}
if (-not $StreamingAssetsDir) { $StreamingAssetsDir = Find-StreamingAssets }
if (-not $StreamingAssetsDir -or -not (Test-Path -LiteralPath $StreamingAssetsDir -PathType Container)) {
    throw 'Sea Power was not found. Re-run with -StreamingAssetsDir pointing to Sea Power_Data\StreamingAssets.'
}

$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$backup = Join-Path $env:USERPROFILE "SEST-Backups\Defector-$stamp"
$gameBackup = Join-Path $backup 'StreamingAssets'
New-Item -ItemType Directory -Path $gameBackup -Force | Out-Null
Write-Host "Backing up current packs, user missions and saves to $backup" -ForegroundColor Cyan

# The normal installer replaces SEST folders and existing editor missions.
# Keep every affected folder outside the game so no backup is loaded as a mod.
foreach ($dir in Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory -Filter 'SEST_*') {
    Copy-Item -LiteralPath $dir.FullName -Destination $gameBackup -Recurse -Force
}
$gameUser = Join-Path $StreamingAssetsDir 'user'
if (Test-Path -LiteralPath $gameUser) {
    Copy-Item -LiteralPath $gameUser -Destination $gameBackup -Recurse -Force
}
$profilePath = Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power'
if (Test-Path -LiteralPath $profilePath) {
    Copy-Item -LiteralPath $profilePath -Destination (Join-Path $backup 'SeaPowerProfile') -Recurse -Force
}
@{
    installedCommit = $ExpectedCommit
    streamingAssets = $StreamingAssetsDir
    profile = $profilePath
    created = (Get-Date).ToString('o')
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backup 'locations.json') -Encoding UTF8

try {
    & (Join-Path $PSScriptRoot 'sync-sest.ps1') -SkipPull -AnyBranch -StreamingAssetsDir $StreamingAssetsDir

    # sync-sest reports mismatches; this wrapper also makes them a failure.
    $installed = Join-Path $StreamingAssetsDir 'SEST_Integration'
    $sources = @(Get-ChildItem -LiteralPath $pack -Recurse -File)
    if (@(Get-ChildItem -LiteralPath $installed -Recurse -File).Count -ne $sources.Count) {
        throw 'Installed pack has an unexpected number of files.'
    }
    foreach ($source in $sources) {
        $relative = $source.FullName.Substring($pack.Length).TrimStart('\')
        $target = Join-Path $installed $relative
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
            throw "Installed file missing: $relative"
        }
        if ((Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash -ne
            (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash) {
            throw "Installed file differs: $relative"
        }
    }
} catch {
    Write-Warning "Installation did not complete. Backups are in $backup; keep them before retrying."
    throw
}

Write-Host "Verified $($sources.Count) pack files at $ExpectedCommit" -ForegroundColor Green
Write-Host "Backup: $backup"
Write-Host 'Test: Mission browser > Tasman Shield > Tasman Shield 08A - The Defector'
Write-Host 'Use a NEW Southern Reach campaign. Existing campaign saves are not migrated.' -ForegroundColor Yellow
