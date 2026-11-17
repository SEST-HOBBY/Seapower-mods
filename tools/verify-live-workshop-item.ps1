<#
.SYNOPSIS
  Compare the subscribed SEST Workshop item with the release upload manifest.
.DESCRIPTION
  Read-only. Nothing in the game, the Workshop item, BepInEx, the load order
  or the saves is changed; the only file written is the report.

  Every file the release manifest lists is looked up in the subscribed item
  (Workshop 3812461539) and compared by size and SHA-256. Files in the item
  that the manifest does not list are named too.

  SETUP replaces two published plugins in the item with the reviewed R14
  builds and adds a third. Those are recognised by the R14 build receipt and
  reported as SETUP's work, not as a difference.

  Exit code 0: every uploaded file is present and identical (allowing for
  SETUP's plugins). Exit code 1: something is missing or different.
.PARAMETER RepositoryRoot
  The release checkout that holds docs/releases/20261107/upload-manifest.json
  (the folder Prepare-PC printed as "Release checkout"). Default: the checkout
  this script is in.
.PARAMETER ItemFolder
  The subscribed item's folder. Default: found through Steam's libraries.
.PARAMETER ReportPath
  Where the report is written. Default: Downloads.
#>
[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [string]$ItemFolder,
    [string]$ReportPath
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ItemId = '3812461539'
$AppId = '1286220'
if (!$RepositoryRoot) { $RepositoryRoot = Split-Path -Parent $PSScriptRoot }
$RepositoryRoot = [IO.Path]::GetFullPath($RepositoryRoot)
$manifestPath = Join-Path $RepositoryRoot 'docs/releases/20261107/upload-manifest.json'
if (!(Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "No upload manifest at $manifestPath. Give -RepositoryRoot the release checkout." }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.workshop_item_id -ne $ItemId) { throw 'This is not the SEST release manifest.' }

function Find-ItemFolder {
    $roots = New-Object System.Collections.Generic.List[string]
    foreach ($key in 'HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam') {
        try {
            $p = Get-ItemProperty -Path $key -ErrorAction Stop
            foreach ($name in 'SteamPath', 'InstallPath') {
                if ($p.PSObject.Properties[$name] -and $p.$name) { $roots.Add([string]$p.$name) }
            }
        } catch { }
    }
    $roots.Add('C:\Program Files (x86)\Steam')
    $libraries = New-Object System.Collections.Generic.List[string]
    foreach ($root in @($roots)) {
        $libraries.Add($root)
        $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf -PathType Leaf) {
            foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) {
                $libraries.Add($m.Groups[1].Value.Replace('\\', '\'))
            }
        }
    }
    foreach ($library in $libraries) {
        $candidate = Join-Path $library ("steamapps\workshop\content\$AppId\$ItemId")
        if (Test-Path -LiteralPath $candidate -PathType Container) { return $candidate }
    }
    return $null
}
if (!$ItemFolder) { $ItemFolder = Find-ItemFolder }
if (!$ItemFolder -or !(Test-Path -LiteralPath $ItemFolder -PathType Container)) {
    throw "The subscribed item $ItemId was not found. Give -ItemFolder its folder (Mod Manager > Open Folder)."
}
$ItemFolder = [IO.Path]::GetFullPath($ItemFolder).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)

# What SETUP installs into the item's plugins folder: the reviewed R14 builds.
$setupFiles = @{}
$receiptPath = Join-Path $RepositoryRoot 'integration/beta-feature-parity/candidates/R14-20261114/build-receipt.json'
$revision = ''
if (Test-Path -LiteralPath $receiptPath -PathType Leaf) {
    $receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
    $revision = [string]$receipt.candidate_revision
    foreach ($name in 'SEST.RuntimeFixes.dll', 'SEST.ContactsFix.dll', 'SEST.IdentifyDataPaths.dll') {
        if ($receipt.files.PSObject.Properties[$name]) { $setupFiles['plugins/' + $name] = ([string]$receipt.files.$name).ToLowerInvariant() }
    }
}

function Get-Sha256([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }

$same = 0
$bySetup = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
$different = New-Object System.Collections.Generic.List[string]
$listed = @{}
foreach ($entry in $manifest.files) {
    $relative = [string]$entry.path
    if ($relative -match '(^|/)\.\.(/|$)|^[/\\]|^[A-Za-z]:') { throw 'Unsafe manifest path.' }
    $listed[$relative.ToLowerInvariant()] = $true
    $file = Join-Path $ItemFolder $relative.Replace('/', [IO.Path]::DirectorySeparatorChar)
    if (!(Test-Path -LiteralPath $file -PathType Leaf)) { $missing.Add($relative); continue }
    $item = Get-Item -LiteralPath $file -Force
    if ($item.Length -eq $entry.bytes -and (Get-Sha256 $file) -eq $entry.sha256) { $same++; continue }
    if ($setupFiles.ContainsKey($relative) -and (Get-Sha256 $file) -eq $setupFiles[$relative]) { $bySetup.Add($relative); continue }
    $different.Add($relative)
}
$extra = New-Object System.Collections.Generic.List[string]
$newest = $null
foreach ($file in @(Get-ChildItem -LiteralPath $ItemFolder -Recurse -File -Force)) {
    if (!$newest -or $file.LastWriteTime -gt $newest.LastWriteTime) { $newest = $file }
    $relative = $file.FullName.Substring($ItemFolder.Length + 1).Replace('\', '/')
    if ($listed.ContainsKey($relative.ToLowerInvariant())) { continue }
    if ($setupFiles.ContainsKey($relative) -and (Get-Sha256 $file.FullName) -eq $setupFiles[$relative]) { $bySetup.Add($relative); continue }
    $extra.Add($relative)
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('SEST live Workshop item check (read-only)')
$lines.Add('checked     : ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
$lines.Add('item folder : ' + $ItemFolder)
$lines.Add('manifest    : ' + $manifestPath)
$lines.Add('manifest has: ' + $manifest.files.Count + ' files')
if ($newest) { $lines.Add('newest file : ' + $newest.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss') + '  ' + $newest.FullName.Substring($ItemFolder.Length + 1)) }
$lines.Add('')
$lines.Add('identical to the upload : ' + $same)
$lines.Add('installed by SETUP      : ' + $bySetup.Count + $(if ($revision) { '  (' + $revision + ')' } else { '' }))
$lines.Add('missing from the item   : ' + $missing.Count)
$lines.Add('different from upload   : ' + $different.Count)
$lines.Add('not in the upload       : ' + $extra.Count)
foreach ($group in @(@('installed by SETUP', $bySetup), @('MISSING', $missing), @('DIFFERENT', $different), @('not in the upload', $extra))) {
    if ($group[1].Count) {
        $lines.Add('')
        $lines.Add($group[0] + ':')
        foreach ($name in ($group[1] | Sort-Object)) { $lines.Add('  ' + $name) }
    }
}
$lines.Add('')
$ok = ($missing.Count -eq 0 -and $different.Count -eq 0)
if ($ok) {
    $lines.Add('RESULT: every uploaded file is in the subscribed item and identical to the release manifest.')
    if ($bySetup.Count) { $lines.Add('SETUP has run since the download: its R14 plugins are in place.') }
    else { $lines.Add('SETUP has not run since the download: the plugins are the published ones. Run SETUP (game closed).') }
    if ($extra.Count) { $lines.Add('Files not in the upload are listed above for review; they do not fail this check.') }
} else {
    $lines.Add('RESULT: the subscribed item does NOT match the release manifest. Keep this report.')
    $lines.Add('Steam may still be downloading the update, or the upload was made from another folder.')
}
if (!$ReportPath) {
    $ReportPath = Join-Path ([Environment]::GetFolderPath('UserProfile')) ('Downloads/SEST-live-item-check-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt')
}
[IO.File]::WriteAllLines($ReportPath, $lines, (New-Object System.Text.UTF8Encoding($false)))
$lines | ForEach-Object { Write-Host $_ }
Write-Host ''
Write-Host ('report written: ' + $ReportPath)
if (!$ok) { exit 1 }
