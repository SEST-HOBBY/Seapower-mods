<#
.SYNOPSIS
    Capture O10 map errors without changing game files or mod settings.
.DESCRIPTION
    Run after reproducing the problem and closing Sea Power. Writes a ZIP to
    Downloads containing recent logs, the saved LoadOrder, selected map-plugin
    DLLs/configs, and the installed Eagle/UAV/O10 definitions. Optionally includes
    Seapower-Scripts.dll for read-only inspection of the failing native method.
#>
[CmdletBinding()]
param(
    [string]$GameDirectory,
    [string]$WorkshopContentDir,
    [string]$UserDataDirectory,
    [string]$OutputDirectory,
    [string]$Repository,
    [switch]$IncludeGameAssembly
)
$ErrorActionPreference = 'Stop'
$SESTCommon = Join-Path $PSScriptRoot 'lib\common.ps1'
if (-not (Test-Path -LiteralPath $SESTCommon -PathType Leaf)) {
    if (-not $Repository) { $Repository = (Get-Location).Path }
    $SESTCommon = Join-Path $Repository 'tools\lib\common.ps1'
}
if (-not (Test-Path -LiteralPath $SESTCommon -PathType Leaf)) {
    throw 'SEST helpers not found. Pass -Repository with the existing Seapower-mods clone.'
}
. $SESTCommon
if (Test-SeaPowerRunning) { throw 'Close Sea Power after reproducing the error, then run this capture.' }
if (-not $GameDirectory) {
    $SESTAssets = Find-StreamingAssets
    if (-not $SESTAssets) { throw 'Sea Power was not found. Pass -GameDirectory with its install folder.' }
    $GameDirectory = Split-Path -Parent (Split-Path -Parent $SESTAssets)
}
$GameDirectory = [IO.Path]::GetFullPath($GameDirectory)
$SESTAssets = Join-Path $GameDirectory 'Sea Power_Data\StreamingAssets'
if (-not (Test-Path -LiteralPath $SESTAssets -PathType Container)) { throw 'StreamingAssets was not found under GameDirectory.' }
if (-not $WorkshopContentDir) { $WorkshopContentDir = Find-WorkshopContent }
if (-not $UserDataDirectory) { $UserDataDirectory = Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power' }
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $env:USERPROFILE 'Downloads' }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$SESTStage = Join-Path ([IO.Path]::GetTempPath()) ('SEST-map-review-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $SESTStage | Out-Null
$SESTMissing = New-Object System.Collections.Generic.List[string]
function Copy-MapFile([string]$Source, [string]$Relative) {
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { $SESTMissing.Add($Relative); return }
    $SESTTarget = Join-Path $SESTStage $Relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $SESTTarget) -Force | Out-Null
    Copy-Item -LiteralPath $Source -Destination $SESTTarget
}
function Copy-MapLog([string]$Source, [string]$Relative) {
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { $SESTMissing.Add($Relative); return }
    # Keep a bounded tail when a repeated exception has made a very large log.
    [string]$SESTText = if ((Get-Item -LiteralPath $Source).Length -gt 20971520) {
        "[Capture retained the last 12000 lines of a log larger than 20 MB.]`r`n" + ((Get-Content -LiteralPath $Source -Encoding UTF8 -Tail 12000) -join "`r`n")
    } else { Get-Content -LiteralPath $Source -Raw -Encoding UTF8 }
    if ($env:USERPROFILE) { $SESTText = $SESTText.Replace($env:USERPROFILE, '<USERPROFILE>').Replace($env:USERPROFILE.Replace('\', '/'), '<USERPROFILE>') }
    [IO.File]::WriteAllText((Join-Path $SESTStage $Relative), $SESTText, (New-Object Text.UTF8Encoding($false)))
}
Copy-MapLog (Join-Path $UserDataDirectory 'Player.log') 'Player.log'
Copy-MapLog (Join-Path $UserDataDirectory 'Player-prev.log') 'Player-prev.log'
Copy-MapLog (Join-Path $GameDirectory 'BepInEx\LogOutput.log') 'BepInEx.log'
$SESTSettings = Join-Path $UserDataDirectory 'usersettings.ini'
if (Test-Path -LiteralPath $SESTSettings) {
    $SESTRaw = Get-Content -LiteralPath $SESTSettings -Raw -Encoding UTF8
    $SESTOrder = [regex]::Match($SESTRaw, '(?ms)^\[LoadOrder\][^\r\n]*\r?\n.*?(?=^\[|\z)')
    if ($SESTOrder.Success) { [IO.File]::WriteAllText((Join-Path $SESTStage 'LoadOrder.ini'), $SESTOrder.Value, (New-Object Text.UTF8Encoding($false))) }
    else { $SESTMissing.Add('LoadOrder section') }
} else { $SESTMissing.Add('usersettings.ini') }
$SESTModIds = @('3380210757','3768036424','3790594162','3818251045','3807187341','3636386513')
$SESTExtensions = @('.dll','.ini','.cfg','.txt','.json','.xml','.md','.zip')
foreach ($SESTId in $SESTModIds) {
    $SESTModPath = if ($WorkshopContentDir) { Join-Path $WorkshopContentDir $SESTId } else { $null }
    if (-not $SESTModPath -or -not (Test-Path -LiteralPath $SESTModPath)) { $SESTMissing.Add('Workshop ' + $SESTId); continue }
    $SESTModPath = [IO.Path]::GetFullPath($SESTModPath).TrimEnd('\', '/')
    foreach ($SESTFile in Get-ChildItem -LiteralPath $SESTModPath -Recurse -File) {
        $SESTRel = $SESTFile.FullName.Substring($SESTModPath.Length + 1)
        if ($SESTRel -match '^assets[\\/]' -or $SESTFile.Length -gt 33554432 -or $SESTExtensions -notcontains $SESTFile.Extension.ToLowerInvariant()) { continue }
        Copy-MapFile $SESTFile.FullName (Join-Path ('plugins\' + $SESTId) $SESTRel)
    }
}
# Record all plugin identities without copying unrelated plugin binaries.
$SESTDLLRoots = @((Join-Path $GameDirectory 'BepInEx\plugins'))
if ($WorkshopContentDir) { $SESTDLLRoots += $WorkshopContentDir }
$SESTDLLRows = @(foreach ($SESTDLLRoot in $SESTDLLRoots) {
    if (-not (Test-Path -LiteralPath $SESTDLLRoot)) { continue }
    foreach ($SESTDLL in Get-ChildItem -LiteralPath $SESTDLLRoot -Recurse -File -Filter *.dll) {
        if ($SESTDLL.Extension -ine '.dll') { continue }
        $SESTAssembly = $null
        try { $SESTAssembly = [Reflection.AssemblyName]::GetAssemblyName($SESTDLL.FullName) } catch { }
        [pscustomobject]@{
            Root = if ($SESTDLLRoot -eq $WorkshopContentDir) { 'Workshop' } else { 'BepInEx-plugins' }
            Path = $SESTDLL.FullName.Substring($SESTDLLRoot.TrimEnd('\', '/').Length + 1).Replace('\', '/')
            Assembly = if ($SESTAssembly) { $SESTAssembly.Name } else { '' }
            Version = if ($SESTAssembly) { $SESTAssembly.Version.ToString() } else { '' }
            Bytes = $SESTDLL.Length
            SHA256 = (Get-FileHash -LiteralPath $SESTDLL.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        $SESTDLLKind = if ($SESTDLLRoot -eq $WorkshopContentDir) { 'Workshop' } else { 'BepInEx' }
        $SESTDLLRel = $SESTDLL.FullName.Substring($SESTDLLRoot.TrimEnd('\', '/').Length + 1)
        Copy-MapFile $SESTDLL.FullName (Join-Path ('all-plugin-dlls\' + $SESTDLLKind) $SESTDLLRel)
    }
})
$SESTDLLRows | Export-Csv -LiteralPath (Join-Path $SESTStage 'plugin-inventory.csv') -NoTypeInformation -Encoding UTF8
foreach ($SESTConfigRoot in @($UserDataDirectory, (Join-Path $GameDirectory 'BepInEx\config'))) {
    if (-not (Test-Path -LiteralPath $SESTConfigRoot)) { continue }
    foreach ($SESTConfig in Get-ChildItem -LiteralPath $SESTConfigRoot -Recurse -File -Filter *.cfg) {
        if ($SESTConfig.FullName -notmatch '(?i)squad|better.?tac|identify') { continue }
        $SESTConfigRel = $SESTConfig.FullName.Substring($SESTConfigRoot.TrimEnd('\', '/').Length + 1)
        $SESTConfigKind = if ($SESTConfigRoot -eq $UserDataDirectory) { 'user' } else { 'bepinex' }
        Copy-MapFile $SESTConfig.FullName (Join-Path ('config\' + $SESTConfigKind) $SESTConfigRel)
    }
}
$SESTLocal = Join-Path $SESTAssets 'SEST_Integration'
$SESTDefinitions = @(
    '_info.ini','CREDITS.txt',
    'aircraft\usaf_f-15ex_SEII.ini','aircraft\usaf_f-15ex_SEII_squadrons.ini',
    'land_units\sest_uav_forward.ini','land_units\sest_uav_forward_variants.ini',
    'language_en\aircraft_names.ini','language_en\land_units_names.ini',
    'missions\Southern Watch\Southern Watch O10 - Ballistic Shield.ini',
    'campaigns\sest-southern-watch\missions\Southern Watch O10 - Ballistic Shield.ini',
    'campaigns\sest-southern-watch-open\missions\Southern Watch O10 - Ballistic Shield.ini'
)
foreach ($SESTRel in $SESTDefinitions) { Copy-MapFile (Join-Path $SESTLocal $SESTRel) (Join-Path 'installed-SEST' $SESTRel) }
$SESTGameAssemblies = New-Object System.Collections.Generic.List[string]
if ($IncludeGameAssembly) {
    $SESTManaged = Join-Path $GameDirectory 'Sea Power_Data\Managed'
    foreach ($SESTAssemblyName in @('Seapower-Scripts.dll', 'Assembly-CSharp.dll')) {
        $SESTAssemblyPath = Join-Path $SESTManaged $SESTAssemblyName
        if (-not (Test-Path -LiteralPath $SESTAssemblyPath -PathType Leaf)) { continue }
        Copy-MapFile $SESTAssemblyPath (Join-Path 'game-reference' $SESTAssemblyName)
        $SESTGameAssemblies.Add($SESTAssemblyName)
    }
    if ($SESTGameAssemblies.Count -eq 0) {
        foreach ($SESTCandidate in Get-ChildItem -LiteralPath $SESTManaged -File -Filter *.dll) {
            $SESTIdentity = $null
            try { $SESTIdentity = [Reflection.AssemblyName]::GetAssemblyName($SESTCandidate.FullName) } catch { }
            if (-not $SESTIdentity -or $SESTIdentity.Name -ne 'Seapower-Scripts') { continue }
            Copy-MapFile $SESTCandidate.FullName (Join-Path 'game-reference' $SESTCandidate.Name)
            $SESTGameAssemblies.Add($SESTCandidate.Name)
        }
    }
    if ($SESTGameAssemblies.Count -eq 0) { throw 'The native game assembly was not found in Managed. No incomplete review ZIP was created.' }
}
foreach ($SESTCoreName in @('0Harmony.dll', 'BepInEx.dll')) {
    Copy-MapFile (Join-Path $GameDirectory ('BepInEx\core\' + $SESTCoreName)) (Join-Path 'loader-reference' $SESTCoreName)
}
# Read worker settings/status without writing a live mode request.
foreach ($SESTWorker in @('CombatWorker', 'ParallelRangeProbe', 'UiWorkerProbe')) {
    foreach ($SESTWorkerFile in @('settings.ini', 'live\status.txt', 'live\mode.request')) {
        $SESTWorkerRel = Join-Path $SESTWorker $SESTWorkerFile
        Copy-MapFile (Join-Path (Join-Path $UserDataDirectory 'Mods') $SESTWorkerRel) (Join-Path 'worker-status' $SESTWorkerRel)
    }
}
[ordered]@{
    captured_at = (Get-Date).ToString('o')
    reproduction_mission = 'Southern Watch O10 - Ballistic Shield'
    reports = @('Controllable F-15EX absent or unidentified on map','Forward UAV section MISSING','MapKnownUnits.Update NullReferenceException')
    capture_version = 2
    game_assembly_requested = [bool]$IncludeGameAssembly
    included_game_assembly = ($SESTGameAssemblies.Count -gt 0)
    captured_game_assemblies = @($SESTGameAssemblies.ToArray())
    included_all_plugin_dlls = $true
    missing_optional_files = @($SESTMissing.ToArray())
    modified_game_or_settings = $false
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $SESTStage 'capture.json') -Encoding UTF8
# Freeze the input list and compute rows before opening the manifest output.
$SESTFiles = @(Get-ChildItem -LiteralPath $SESTStage -Recurse -File)
$SESTRows = @(foreach ($SESTFile in $SESTFiles) {
    [pscustomobject]@{
        Path = $SESTFile.FullName.Substring($SESTStage.Length + 1).Replace('\', '/')
        Bytes = $SESTFile.Length
        SHA256 = (Get-FileHash -LiteralPath $SESTFile.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
})
$SESTRows | Export-Csv -LiteralPath (Join-Path $SESTStage 'file-manifest.csv') -NoTypeInformation -Encoding UTF8
$SESTZip = Join-Path $OutputDirectory ('SEST-map-review-complete-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,6) + '.zip')
Compress-Archive -Path (Join-Path $SESTStage '*') -DestinationPath $SESTZip -CompressionLevel Optimal
Remove-Item -LiteralPath $SESTStage -Recurse -Force
Write-Host ('Map review saved: ' + $SESTZip) -ForegroundColor Green
Write-Host 'Upload that ZIP with the O10 report. No game files or settings were changed.'
