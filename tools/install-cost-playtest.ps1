#requires -Version 5.1
param([string]$Repository = (Join-Path $env:USERPROFILE 'Seapower-mods'))
$ErrorActionPreference = 'Stop'
if (Get-Process -Name 'Sea Power','SeaPower' -ErrorAction SilentlyContinue) { throw 'Close Sea Power before installing.' }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is required; use the existing SEST clone.' }
$Repository = (Resolve-Path -LiteralPath $Repository).Path
$SESTManifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'playtest-manifest.json') -Raw | ConvertFrom-Json
if ($SESTManifest.commit -notmatch '^[0-9a-f]{40}$' -or $SESTManifest.bundle_sha256 -notmatch '^[0-9a-f]{64}$') { throw 'Invalid playtest manifest.' }
if ([IO.Path]::GetFileName($SESTManifest.bundle) -cne $SESTManifest.bundle -or $SESTManifest.branch -notmatch '^refs/heads/fix/[a-z0-9-]+$') { throw 'Invalid bundle name/ref.' }
$SESTBundle = Join-Path $PSScriptRoot $SESTManifest.bundle
if ((Get-FileHash -LiteralPath $SESTBundle -Algorithm SHA256).Hash.ToLowerInvariant() -cne $SESTManifest.bundle_sha256) { throw 'Bundle hash mismatch; download/extract the ZIP again.' }
& git -C $Repository rev-parse --show-toplevel
if ($LASTEXITCODE) { throw 'Repository is not a Git clone.' }
& git -C $Repository bundle verify $SESTBundle
if ($LASTEXITCODE) { throw 'Bundle verification failed. Keep the original SEST clone with its existing history.' }
& git -C $Repository fetch --no-tags $SESTBundle $SESTManifest.branch
if ($LASTEXITCODE) { throw 'Import failed.' }
$SESTFetched = (& git -C $Repository rev-parse FETCH_HEAD).Trim()
if ($LASTEXITCODE -or $SESTFetched -cne $SESTManifest.commit) { throw 'Imported commit does not match the manifest.' }
$SESTWorktree = Join-Path $env:TEMP ('SEST-playtest-' + [guid]::NewGuid().ToString('N'))
$SESTCreated = $false
try {
    & git -C $Repository worktree add --detach $SESTWorktree $SESTManifest.commit
    if ($LASTEXITCODE) { throw 'Could not create an isolated playtest checkout.' }
    $SESTCreated = $true
    $SESTSync = Join-Path $SESTWorktree 'tools\sync-sest.ps1'
    & powershell -NoProfile -ExecutionPolicy Bypass -File $SESTSync -SkipPull -AnyBranch
    if ($LASTEXITCODE) { throw 'Sync failed; read its last lines before starting the game.' }
    Write-Host ('Playtest {0} installed. Expected: IN LINE: all {1} installed files match this commit ({0}).' -f $SESTManifest.commit.Substring(0,8),$SESTManifest.installed_files) -ForegroundColor Green
    Write-Host 'Fully restart Sea Power. F11 in a mission = this mission; F11 in the Task Force menu = campaign totals. Follow PC-TEST-CARD.md; native acceptance is pending.'
} finally {
    if ($SESTCreated) {
        & git -C $Repository worktree remove $SESTWorktree
        if ($LASTEXITCODE) { Write-Warning ('Temporary checkout retained at ' + $SESTWorktree + '; your main checkout/branch was not changed.') }
    }
}
