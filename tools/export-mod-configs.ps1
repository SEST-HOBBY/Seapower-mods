<#
.SYNOPSIS
    Export locally downloaded Sea Power Workshop text/config files.
.DESCRIPTION
    Builds a fresh snapshot before replacing existing mod folders, so upstream
    file removals do not survive in mods-source. Replaced folders and manifests
    are retained in a sibling _export-backups directory. A failed publication
    rolls back the replacements. Nothing writes to Steam's content folders.

    _export-manifest.csv records mod IDs, names, counts and bytes.
    _export-files.csv records each Workshop file's path, size and SHA-256.
    This inventories local content, not the Steam account subscription list.

    -NoPrune retains absent mod folders, but still fully refreshes present mods.
    Retained absent folders will be reported by tools/check_inventory.py.
.EXAMPLE
    .\tools\export-mod-configs.ps1 -IncludeVanilla
.EXAMPLE
    .\tools\export-mod-configs.ps1 -WorkshopContentDir 'D:\SteamLibrary\steamapps\workshop\content\1286220' -DestDir '.\mods-source'
#>
[CmdletBinding()]
param(
    [string]$WorkshopContentDir,
    [string]$DestDir,
    [switch]$IncludeVanilla,
    [switch]$NoPrune,
    [string[]]$TextExtensions = @('.ini', '.txt', '.json', '.cfg', '.xml', '.md', '.yaml', '.yml', '.csv'),
    [long]$MaxFileBytes = 2MB
)

$ErrorActionPreference = 'Stop'
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $DestDir) { $DestDir = Join-Path $scriptDir '..\mods-source' }
. (Join-Path $scriptDir 'lib\common.ps1')

function Find-SeaPower {
    foreach ($lib in Get-SteamLibraries) {
        foreach ($acf in Get-ChildItem -LiteralPath $lib -Filter 'appmanifest_*.acf' -ErrorAction SilentlyContinue) {
            $raw = Get-Content -LiteralPath $acf.FullName -Raw
            if ($raw -match '"name"\s+"([^"]*Sea Power[^"]*)"') {
                $appId = [regex]::Match($acf.Name, '\d+').Value
                $installDir = [regex]::Match($raw, '"installdir"\s+"([^"]+)"').Groups[1].Value
                return [pscustomobject]@{
                    AppId = $appId
                    GameDir = Join-Path $lib "common\$installDir"
                    Workshop = Join-Path $lib "workshop\content\$appId"
                }
            }
        }
    }
}

$game = $null
if (-not $WorkshopContentDir) {
    $game = Find-SeaPower
    if (-not $game) { throw 'Sea Power not found. Supply -WorkshopContentDir explicitly.' }
    $WorkshopContentDir = $game.Workshop
}
$source = Get-Item -LiteralPath $WorkshopContentDir
if (-not $source.PSIsContainer) { throw 'WorkshopContentDir must be a directory.' }
if ($MaxFileBytes -lt 0) { throw 'MaxFileBytes must not be negative.' }
$WorkshopContentDir = $source.FullName.TrimEnd('\', '/')
$DestDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($DestDir).TrimEnd('\', '/')

# Reject overlapping trees, including paths reached through a junction/symlink.
function Assert-NoLinks {
    param([string]$Path)
    $probe = $Path
    while ($probe) {
        if (Test-Path -LiteralPath $probe) {
            $item = Get-Item -LiteralPath $probe -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Reparse point is not supported in an export path: $probe"
            }
        }
        $parent = Split-Path -Parent $probe
        if ($parent -eq $probe) { break }
        $probe = $parent
    }
}
function Assert-SeparateTrees {
    param([string]$First, [string]$Second)
    $a = $First.Replace('\', '/').TrimEnd('/') + '/'
    $b = $Second.Replace('\', '/').TrimEnd('/') + '/'
    if ($a.StartsWith($b, [StringComparison]::OrdinalIgnoreCase) -or
        $b.StartsWith($a, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Source and destination must be separate trees: $First / $Second"
    }
}
Assert-NoLinks $WorkshopContentDir
Assert-NoLinks $DestDir
Assert-SeparateTrees $WorkshopContentDir $DestDir

$modDirs = @(Get-ChildItem -LiteralPath $WorkshopContentDir -Directory |
    Where-Object { $_.Name -match '^[0-9]+$' } | Sort-Object Name)
if (-not $modDirs.Count) { throw 'No numeric Workshop folders found; existing exports were not changed.' }
$sources = @($modDirs | ForEach-Object { [pscustomobject]@{ Id = $_.Name; Root = $_.FullName } })
if ($IncludeVanilla) {
    if (-not $game) { $game = Find-SeaPower }
    if (-not $game) { throw 'Cannot export vanilla: Sea Power game directory was not found.' }
    $sa = Get-ChildItem -LiteralPath $game.GameDir -Directory -Recurse -Depth 2 |
        Where-Object { $_.Name -eq 'StreamingAssets' } | Select-Object -First 1
    if (-not $sa) { throw 'Cannot export vanilla: StreamingAssets was not found.' }
    Assert-NoLinks $sa.FullName
    Assert-SeparateTrees $sa.FullName $DestDir
    $sources += [pscustomobject]@{ Id = '_vanilla'; Root = $sa.FullName }
}

$parentDir = Split-Path -Parent $DestDir
$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N')
$stage = Join-Path $parentDir ("_export-staging-" + $stamp)
$backup = Join-Path (Join-Path $parentDir '_export-backups') $stamp
$manifest = [System.Collections.Generic.List[object]]::new()
$fileManifest = [System.Collections.Generic.List[object]]::new()
$saved = [System.Collections.Generic.List[string]]::new()
$published = [System.Collections.Generic.List[string]]::new()

try {
    New-Item -ItemType Directory -Path $stage | Out-Null
    Write-Host "Staging $($modDirs.Count) local Workshop items..."
    foreach ($entry in $sources) {
        Assert-NoLinks $entry.Root
        $targetRoot = Join-Path $stage $entry.Id
        New-Item -ItemType Directory -Path $targetRoot | Out-Null
        $copied = 0; [long]$bytes = 0
        # Fail on links rather than following them outside the declared source.
        $items = @(Get-ChildItem -LiteralPath $entry.Root -Recurse -Force)
        if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) {
            throw "Source contains a reparse point: $($entry.Root)"
        }
        foreach ($f in $items | Where-Object { -not $_.PSIsContainer -and
                $TextExtensions -contains $_.Extension.ToLowerInvariant() -and $_.Length -le $MaxFileBytes }) {
            $rel = $f.FullName.Substring($entry.Root.Length).TrimStart('\', '/')
            if ($entry.Id -eq '_vanilla' -and $rel -match '^SEST_') { continue }
            $target = Join-Path $targetRoot $rel
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $f.FullName -Destination $target
            $length = (Get-Item -LiteralPath $target).Length
            $copied++; $bytes += $length
            if ($entry.Id -ne '_vanilla') {
                $fileManifest.Add([pscustomobject]@{
                    WorkshopId = $entry.Id
                    RelativePath = $rel.Replace('\', '/')
                    Bytes = $length
                    SHA256 = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
                })
            }
        }
        if ($entry.Id -ne '_vanilla') {
            $name = Get-ModDisplayName -ModDir $targetRoot
            $manifest.Add([pscustomobject]@{
                WorkshopId = $entry.Id; DisplayName = $name; FilesCopied = $copied; Bytes = $bytes
            })
            Write-Host ("  {0}  {1,4} files  {2,10:N0} B  {3}" -f $entry.Id, $copied, $bytes, $name)
        }
    }
    $manifest | Sort-Object WorkshopId | Export-Csv -LiteralPath (Join-Path $stage '_export-manifest.csv') -NoTypeInformation -Encoding UTF8
    if ($fileManifest.Count) {
        $fileManifest | Sort-Object WorkshopId, RelativePath | Export-Csv -LiteralPath (Join-Path $stage '_export-files.csv') -NoTypeInformation -Encoding UTF8
    } else {
        '"WorkshopId","RelativePath","Bytes","SHA256"' | Set-Content -LiteralPath (Join-Path $stage '_export-files.csv') -Encoding UTF8
    }

    # Publish only after all copies/hashes succeeded. Keep original data outside
    # mods-source and restore it if any rename fails. A crash may require manual
    # restoration from the printed backup directory; no backup is auto-deleted.
    New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
    New-Item -ItemType Directory -Force -Path $backup | Out-Null
    Write-Host "Previous snapshot backup: $backup"
    $names = @($sources | ForEach-Object { $_.Id }) + @('_export-manifest.csv', '_export-files.csv')
    if (-not $NoPrune) {
        $names += @(Get-ChildItem -LiteralPath $DestDir -Directory |
            Where-Object { $_.Name -match '^[0-9]+$' -and $_.Name -notin $modDirs.Name } |
            ForEach-Object { $_.Name })
    }
    foreach ($name in $names) {
        $dest = Join-Path $DestDir $name
        if (Test-Path -LiteralPath $dest) {
            Assert-NoLinks $dest
            Move-Item -LiteralPath $dest -Destination (Join-Path $backup $name)
            $saved.Add($name)
        }
        $next = Join-Path $stage $name
        if (Test-Path -LiteralPath $next) {
            Move-Item -LiteralPath $next -Destination $dest
            $published.Add($name)
        }
    }
} catch {
    $failure = $_
    foreach ($name in $published) { Remove-Item -LiteralPath (Join-Path $DestDir $name) -Recurse -Force }
    foreach ($name in $saved) { Move-Item -LiteralPath (Join-Path $backup $name) -Destination (Join-Path $DestDir $name) }
    throw $failure
} finally {
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}
Write-Host "Done: $($modDirs.Count) local Workshop IDs. Manifest: $(Join-Path $DestDir '_export-manifest.csv')"
Write-Host 'Next: python tools/check_inventory.py; review the diff before committing or installing.'
