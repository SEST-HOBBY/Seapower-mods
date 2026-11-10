<#
.SYNOPSIS
  Verify and prepare the canonical Workshop upload without altering the game.
.DESCRIPTION
  Copies only integration/dist/SEST_Integration to a fresh output directory.
  The release manifest checks every file and rejects extras, including a beta
  DLL substituted by a test installation. Game folders, BepInEx, load order,
  Workshop subscriptions, saves and the Steam branch are never changed.
  Before anything is copied, every manifest path under the output folder (and
  under each -CheckPathRoot) must fit Windows' path limit: 259 characters for
  a file and 247 for a folder, which Windows PowerShell 5.1 cannot exceed.
  This copy is for verification: the game's Create Mod picker lists only
  folders inside Sea Power_Data\StreamingAssets, where Upload-PC.cmd puts the
  publishing copy.
#>
[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [string]$OutputDirectory,
    [switch]$VerifyOnly,
    # Further folders that will each receive the whole pack (Upload-PC passes
    # its StreamingAssets publishing folder and its moved-out copy); checked
    # against the path limit with the output folder, before any copy.
    [string[]]$CheckPathRoot = @()
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
# Windows' limits without long-path support: MAX_PATH (260) less the closing
# NUL for a file, and less 12 more for a folder (CreateDirectory).
$MaxFilePath = 259
$MaxFolderPath = 247
$longestFile = ''
$longestFolder = ''
foreach ($entry in $manifest.files) {
    $relative = ([string]$entry.path).Replace('/', [IO.Path]::DirectorySeparatorChar)
    if ($relative.Length -gt $longestFile.Length) { $longestFile = $relative }
    $folder = Split-Path -Parent $relative
    if ($folder -and $folder.Length -gt $longestFolder.Length) { $longestFolder = $folder }
}
function Assert-PathFits([string]$Root, [string]$What) {
    $base = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $file = $base.Length + 1 + $longestFile.Length
    $folder = $base.Length + 1 + $longestFolder.Length
    if ($file -gt $MaxFilePath -or ($longestFolder -and $folder -gt $MaxFolderPath)) {
        throw ("Windows path limit: in the $What ($base) the longest file would need $file characters and the longest folder $folder; " +
               "Windows allows $MaxFilePath for a file and $MaxFolderPath for a folder. The longest is " +
               [IO.Path]::Combine($base, $longestFile) + '. Nothing was copied; use a shorter folder.')
    }
}
foreach ($root in @($CheckPathRoot)) { if ($root) { Assert-PathFits $root 'publishing folder' } }
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
# A short staging suffix: this name is part of every copied file's path.
$stage = $OutputDirectory + '.tmp' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
if (Test-Path -LiteralPath $stage) { throw 'The staging folder already exists; run again.' }
$upload = Join-Path $stage 'SEST_Integration'
Assert-PathFits $upload 'staging copy'
Assert-PathFits (Join-Path $OutputDirectory 'SEST_Integration') 'verified copy'
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
Write-Host 'VERIFIED COPY (for checking; the game uploader cannot pick it):' -ForegroundColor Green
Write-Host (Join-Path $OutputDirectory 'SEST_Integration')
Write-Host 'The game''s Create Mod picker lists only folders inside Sea Power_Data\StreamingAssets; Upload-PC.cmd puts the publishing copy there.'
Write-Host 'The beta installation and Steam branch were not changed.'
