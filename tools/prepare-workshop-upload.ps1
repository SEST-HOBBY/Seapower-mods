<#
.SYNOPSIS
  Verify and prepare the canonical Workshop upload without altering the game.
.DESCRIPTION
  Copies only integration/dist/SEST_Integration to a fresh output directory.
  The release manifest checks every file and rejects extras, including a beta
  DLL substituted by a test installation. Game folders, BepInEx, load order,
  Workshop subscriptions, saves and the Steam branch are never changed.
#>
[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [string]$OutputDirectory,
    [switch]$VerifyOnly
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (!$RepositoryRoot) { $RepositoryRoot = Split-Path -Parent $PSScriptRoot }
$RepositoryRoot = [IO.Path]::GetFullPath($RepositoryRoot)
$manifestPath = Join-Path $RepositoryRoot 'docs/releases/20261107/upload-manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.workshop_item_id -ne '3812461539' -or $manifest.status -ne 'candidate-needs-gameplay') {
    throw 'This is not the reviewed SEST release manifest.'
}
$source = Join-Path $RepositoryRoot 'integration/dist/SEST_Integration'
function Test-ReleaseTree([string]$Root) {
    $prefix = $Root.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    $actual = @(Get-ChildItem -LiteralPath $Root -Recurse -File -Force)
    if ($actual.Count -ne $manifest.files.Count) { throw "Wrong file count: $($actual.Count), expected $($manifest.files.Count)." }
    $expected = @{}
    foreach ($entry in $manifest.files) {
        if ($entry.path -match '(^|/)\.\.(/|$)|^[/\\]|^[A-Za-z]:') { throw 'Unsafe manifest path.' }
        $file = [IO.Path]::GetFullPath((Join-Path $Root $entry.path))
        if (!$file.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Manifest path escapes upload folder.' }
        $expected[$file] = $true
        if (!(Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing release file: $($entry.path)" }
        $item = Get-Item -LiteralPath $file -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked release file refused: $($entry.path)" }
        if ($item.Length -ne $entry.bytes -or
            (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
            throw "Release file differs: $($entry.path). Fetch the release branch again; do not upload this folder."
        }
    }
    foreach ($file in $actual) {
        if (!$expected.ContainsKey($file.FullName)) { throw "Unexpected release file: $($file.FullName)" }
    }
}
Test-ReleaseTree $source
Write-Host "VERIFIED: all $($manifest.files.Count) canonical upload files match the release manifest."
if ($VerifyOnly) { return }
if (!$OutputDirectory) {
    $OutputDirectory = Join-Path ([Environment]::GetFolderPath('UserProfile')) ('Downloads/SEST-Workshop-20261107-' + (Get-Date -Format HHmmss))
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Output already exists; choose a fresh output directory.' }
if ($OutputDirectory.StartsWith($RepositoryRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Choose an output folder outside the repository.'
}
$stage = $OutputDirectory + '.staging-' + [Guid]::NewGuid().ToString('N')
$upload = Join-Path $stage 'SEST_Integration'
try {
    New-Item -ItemType Directory -Path $upload -Force | Out-Null
    foreach ($entry in $manifest.files) {
        $target = Join-Path $upload $entry.path
        New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $source $entry.path) -Destination $target
    }
    Test-ReleaseTree $upload
    Copy-Item -LiteralPath (Join-Path $RepositoryRoot 'docs/releases/20261107/STEAM-CHANGE-NOTE.txt') -Destination $stage
    Copy-Item -LiteralPath (Join-Path $RepositoryRoot 'docs/releases/20261107/README-FIRST.txt') -Destination $stage
    Copy-Item -LiteralPath $manifestPath -Destination $stage
    Move-Item -LiteralPath $stage -Destination $OutputDirectory
} catch {
    # Keep a failed stage for diagnosis; it has no effect on the installed game.
    throw
}
Write-Host ''
Write-Host 'UPLOAD FOLDER:' -ForegroundColor Green
Write-Host (Join-Path $OutputDirectory 'SEST_Integration')
Write-Host 'Use Update Existing for Workshop item 3812461539 after the gameplay checks in README-FIRST.txt.'
Write-Host 'The beta installation and Steam branch were not changed.'
