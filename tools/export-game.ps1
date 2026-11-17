<#
.SYNOPSIS
    Export the installed game's own text files into mods-source\_vanilla,
    but only when the installed game is a newer public release than the
    one the export holds.

.DESCRIPTION
    mods-source\_vanilla is the game the pack is built on: the builders
    fork it, and the checks compare with it. It has to follow a game
    release and must never follow a Steam beta (the 28 Oct 2026 capture
    wrote a beta over it; docs\packaging-and-recovery.md, "When the PC is
    on a Steam beta"). The game's own changelog says which is installed:
    a release's line ends "Public Release", a beta's does not.

    This reads that line and the export's, says what it found, and runs
    tools\export-mod-configs.ps1 -IncludeVanilla only when the installed
    build is a public release and newer than the export. It writes
    nothing itself, never commits or pushes, and only reads the game.

    The exporter copies over the export and removes nothing, so a file the
    update dropped stays in mods-source\_vanilla\original. Run
    tools\capture-context.ps1 first (the one-command capture does): its
    game-files-dropped.txt lists those files, and tools/apply_dropped_files.py
    removes them in the repository once the export is in.

    Exit codes, for the block that runs this:
      0  exported
      3  nothing to do: the export already holds the installed build
      4  not exported: the installed build is a beta
      5  not exported: the game, or its changelog, was not found or the
         game is running
      6  not exported: the installed build is older than the export

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\export-game.ps1
#>
[CmdletBinding()]
param(
    # The game folder, the one that holds Sea Power.exe; found through Steam when omitted.
    [string]$GameDir = "",
    # Steam's Workshop folder for Sea Power; the exporter finds it when omitted.
    [string]$WorkshopContentDir = "",
    # Where mods-source is; this clone's when omitted.
    [string]$DestDir = "",
    # Export although the export already holds the installed build.
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")
if (-not $DestDir) { $DestDir = Join-Path (Split-Path -Parent $scriptDir) "mods-source" }
$DestDir = [IO.Path]::GetFullPath($DestDir)

function Get-BuildOrder([object]$Build) {
    # A build as something that sorts: the version's numbers, then the build number.
    $parts = @($Build.Version -split '\.' | ForEach-Object { [int]$_ })
    while ($parts.Count -lt 4) { $parts += 0 }
    $number = 0
    if (-not [int]::TryParse(($Build.Build -replace '\D', ''), [ref]$number)) { $number = 0 }
    return ("{0:D5}.{1:D5}.{2:D5}.{3:D5}.{4:D9}" -f $parts[0], $parts[1], $parts[2], $parts[3], $number)
}

if (Test-SeaPowerRunning) {
    Write-Host "Sea Power is running: close it first. Nothing was exported."
    exit 5
}
$streaming = $null
if ($GameDir) {
    if (Test-Path -LiteralPath $GameDir -PathType Container) {
        $found = Get-ChildItem -LiteralPath $GameDir -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq "StreamingAssets" } | Select-Object -First 1
        if ($found) { $streaming = $found.FullName }
    }
} else {
    $streaming = Find-StreamingAssets
}
if (-not $streaming) {
    Write-Host "Sea Power's StreamingAssets folder was not found. Nothing was exported."
    exit 5
}
$dataDir = Split-Path -Parent $streaming
$changelog = Join-Path $dataDir "changelog.txt"
if (-not (Test-Path -LiteralPath $changelog -PathType Leaf)) {
    $changelog = Join-Path (Split-Path -Parent $dataDir) "changelog.txt"
}
$installed = Get-ChangelogBuild -Path $changelog
if (-not $installed) {
    Write-Host "The game's changelog.txt was not found beside the install, or has no build line."
    Write-Host "Without it a release cannot be told from a beta. Nothing was exported."
    exit 5
}
$exported = Get-ChangelogBuild -Path (Join-Path $DestDir "_vanilla\changelog.txt")
Write-Host "Installed game: $($installed.Line)"
Write-Host ("Exported game (mods-source\_vanilla): " + $(if ($exported) { $exported.Line } else { "none yet" }))

if ($exported -and -not $Force) {
    if ($installed.Version -eq $exported.Version -and $installed.Build -eq $exported.Build) {
        Write-Host "The export already holds the installed build. Nothing to do."
        exit 3
    }
    if ((Get-BuildOrder $installed) -lt (Get-BuildOrder $exported)) {
        Write-Host "The installed build is OLDER than the export. Nothing was exported."
        exit 6
    }
}
if (-not $installed.Release) {
    Write-Host "The installed build's line does not say Public Release, so it is a beta."
    Write-Host "A beta's files do not go into mods-source\_vanilla. Nothing was exported."
    exit 4
}

Write-Host "Exporting the game's own files (and the mods, which the exporter always does)..."
$exportArgs = @{ IncludeVanilla = $true; DestDir = $DestDir; GameDir = (Split-Path -Parent $dataDir) }
if ($WorkshopContentDir) { $exportArgs.WorkshopContentDir = $WorkshopContentDir }
& (Join-Path $scriptDir "export-mod-configs.ps1") @exportArgs
$after = Get-ChangelogBuild -Path (Join-Path $DestDir "_vanilla\changelog.txt")
if (-not $after -or $after.Version -ne $installed.Version -or $after.Build -ne $installed.Build) {
    Write-Host "The exporter ran, but mods-source\_vanilla\changelog.txt does not show the installed build. Read its lines above."
    exit 5
}
Write-Host "Exported: $($after.Line)"
Write-Host "Files this build no longer ships are still in mods-source\_vanilla\original:"
Write-Host "data\install-snapshot\game-files-dropped.txt lists them (tools\capture-context.ps1)."
exit 0
