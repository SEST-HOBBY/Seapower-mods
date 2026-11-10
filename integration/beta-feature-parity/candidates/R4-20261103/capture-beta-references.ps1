<#
.SYNOPSIS
    Capture beta build references for restoring SEST's pre-beta features.
.DESCRIPTION
    Read-only against Sea Power, Workshop and user settings. Writes a ZIP to
    Downloads; never installs a plugin, changes a Steam branch, or uploads files.
    Includes managed game/plugin DLLs, load order, redacted logs and SHA256s.
    Excludes saves, audio, images, credentials and arbitrary configuration files.
#>
[CmdletBinding()]
param(
    [string]$GameRoot = '',
    [string[]]$WorkshopContentRoot = @(),
    [string]$PlayerDataRoot = '',
    [string]$OutDirectory = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$knownStable = 'eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd'
$knownBeta = '3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62'
$profileRoot = [Environment]::GetFolderPath('UserProfile')

function Get-UniqueDirectories([string[]]$Paths) {
    $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($path in $Paths) {
        if (!$path -or !(Test-Path -LiteralPath $path -PathType Container)) { continue }
        $resolved = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $path).ProviderPath).TrimEnd([char[]]'\/')
        if ($seen.Add($resolved)) { $resolved }
    }
}

function Find-SteamApps {
    $roots = @()
    foreach ($key in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam')) {
        try {
            $props = Get-ItemProperty -LiteralPath $key
            foreach ($name in @('SteamPath', 'InstallPath')) {
                $value = $props.PSObject.Properties[$name]
                if ($value -and $value.Value) { $roots += [string]$value.Value }
            }
        } catch { }
    }
    foreach ($name in @('ProgramFiles(x86)', 'ProgramFiles')) {
        $value = [Environment]::GetEnvironmentVariable($name)
        if ($value) { $roots += Join-Path $value 'Steam' }
    }
    $apps = @()
    foreach ($root in @(Get-UniqueDirectories $roots)) {
        $apps += Join-Path $root 'steamapps'
        $vdf = Join-Path $root 'steamapps/libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf -PathType Leaf) {
            $raw = [IO.File]::ReadAllText($vdf)
            foreach ($match in [regex]::Matches($raw, '"path"\s+"([^"]+)"')) {
                $apps += Join-Path ($match.Groups[1].Value.Replace('\\', '\')) 'steamapps'
            }
        }
    }
    return @(Get-UniqueDirectories $apps)
}

function Get-TreeDlls([string]$Root) {
    if (!(Test-Path -LiteralPath $Root -PathType Container)) { return }
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($Root)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($item in @(Get-ChildItem -LiteralPath $directory -Force)) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
            if ($item.PSIsContainer) { $pending.Push($item.FullName) }
            elseif ($item.Extension -ieq '.dll') { $item }
        }
    }
}

function Redact-Text([string]$Text) {
    if ($profileRoot) { $Text = $Text.Replace($profileRoot, '<USER>') }
    if ($env:USERPROFILE) { $Text = $Text.Replace($env:USERPROFILE, '<USER>') }
    $Text = [regex]::Replace($Text, '(?i)[A-Z]:[\\/]Users[\\/][^\\/\r\n]+', '<USER>')
    $Text = [regex]::Replace($Text, '\b7656119\d{10}\b', '<STEAM_ID>')
    return $Text
}

function Assert-Outside([string]$Output, [string]$Source) {
    $prefix = [IO.Path]::GetFullPath($Source).TrimEnd([char[]]'\/')
    if ($Output.Equals($prefix, [StringComparison]::OrdinalIgnoreCase) -or
        $Output.StartsWith($prefix + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Choose an output directory outside the game, Workshop and player data folders.'
    }
}

$libraries = @(Find-SteamApps)
if (!$GameRoot) {
    $candidates = @(Get-UniqueDirectories @($libraries | ForEach-Object { Join-Path $_ 'common/Sea Power' }) |
        Where-Object { Test-Path -LiteralPath (Join-Path $_ 'Sea Power_Data/Managed/Seapower-Scripts.dll') })
    if ($candidates.Count -eq 0) {
        throw 'Sea Power was not found in the detected Steam libraries. Run again with -GameRoot "your Sea Power folder".'
    }
    if ($candidates.Count -gt 1) {
        throw ("Multiple Sea Power installations found. Run again with -GameRoot and one of these folders:`r`n" + ($candidates -join "`r`n"))
    }
    $GameRoot = $candidates[0]
}
$GameRoot = (Resolve-Path -LiteralPath $GameRoot).ProviderPath
$managed = Join-Path $GameRoot 'Sea Power_Data/Managed'
$native = Join-Path $managed 'Seapower-Scripts.dll'
if (!(Test-Path -LiteralPath $native -PathType Leaf)) { throw 'Seapower-Scripts.dll is missing from that installation.' }
if (@(Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Close Sea Power before capturing the beta references.'
}
$nativeHash = (Get-FileHash -LiteralPath $native -Algorithm SHA256).Hash.ToLowerInvariant()
if ($nativeHash -eq $knownStable) {
    throw 'This installation is the stable build. Select the Steam beta, let it update, launch once, quit, and rerun this capture. No game files changed.'
}
$buildStatus = 'unreviewed-build-captured-for-inspection'
if ($nativeHash -eq $knownBeta) { $buildStatus = 'beta-261026' }
if (!$PlayerDataRoot -and $profileRoot) {
    $PlayerDataRoot = Join-Path $profileRoot 'AppData/LocalLow/Triassic Games/Sea Power'
}
if ($WorkshopContentRoot.Count -eq 0) {
    $sameLibrary = Split-Path -Parent (Split-Path -Parent $GameRoot)
    $WorkshopContentRoot = @(@($sameLibrary) + $libraries | ForEach-Object { Join-Path $_ 'workshop/content/1286220' } |
        Where-Object { Test-Path -LiteralPath $_ -PathType Container } | Select-Object -Unique)
}
$WorkshopContentRoot = @(Get-UniqueDirectories @($WorkshopContentRoot | ForEach-Object { (Resolve-Path -LiteralPath $_).ProviderPath }))
if (!$OutDirectory) { $OutDirectory = Join-Path $profileRoot 'Downloads' }
$OutDirectory = [IO.Path]::GetFullPath($OutDirectory)
foreach ($source in @($GameRoot) + $WorkshopContentRoot + @($PlayerDataRoot)) {
    if ($source) { Assert-Outside $OutDirectory $source }
}
$stage = Join-Path ([IO.Path]::GetTempPath()) ('SEST-Beta-References-' + [guid]::NewGuid().ToString('N'))
$records = New-Object 'System.Collections.Generic.List[object]'
$missing = New-Object 'System.Collections.Generic.List[string]'

function Copy-Reference([IO.FileInfo]$File, [string]$Relative, [switch]$ManagedOnly) {
    $identity = ''
    try { $identity = [Reflection.AssemblyName]::GetAssemblyName($File.FullName).FullName }
    catch { if ($ManagedOnly) { return } }
    $before = (Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $dest = Join-Path $stage $Relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
    Copy-Item -LiteralPath $File.FullName -Destination $dest
    $after = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($after -ne $before) { throw "A reference changed during capture: $Relative. Let Steam finish updating and rerun." }
    $records.Add([ordered]@{ path = $Relative.Replace('\', '/'); sha256 = $after; bytes = $File.Length; assembly = $identity })
}

function Write-Report([string]$Relative, [string]$Text) {
    $dest = Join-Path $stage $Relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
    [IO.File]::WriteAllText($dest, (Redact-Text $Text), (New-Object Text.UTF8Encoding($false)))
}

try {
    New-Item -ItemType Directory -Path $stage | Out-Null
    Write-Host 'Capturing beta game references and installed code mods. No installation changes.' -ForegroundColor Cyan
    foreach ($file in @(Get-ChildItem -LiteralPath $managed -File -Filter '*.dll')) {
        if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) {
            Copy-Reference $file ('references/managed/' + $file.Name) -ManagedOnly
        }
    }
    $capturedNative = @($records | Where-Object { $_.path -eq 'references/managed/Seapower-Scripts.dll' })
    if ($capturedNative.Count -ne 1 -or $capturedNative[0].sha256 -ne $nativeHash) {
        throw 'The game reference is invalid or changed during capture. Let Steam finish updating and rerun.'
    }
    foreach ($sub in @('core', 'plugins')) {
        $root = Join-Path $GameRoot ('BepInEx/' + $sub)
        if (!(Test-Path -LiteralPath $root)) { $missing.Add('BepInEx/' + $sub); continue }
        foreach ($file in @(Get-TreeDlls $root)) {
            Copy-Reference $file ('references/bepinex/' + $sub + '/' + $file.FullName.Substring($root.Length + 1)) -ManagedOnly
        }
    }
    $libraryIndex = 0
    foreach ($root in $WorkshopContentRoot) {
        $libraryIndex++
        foreach ($file in @(Get-TreeDlls $root)) {
            Copy-Reference $file ('references/workshop/library-' + $libraryIndex + '/' + $file.FullName.Substring($root.Length + 1)) -ManagedOnly
        }
    }
    if ($WorkshopContentRoot.Count -eq 0) { $missing.Add('Workshop content directory') }
    $streaming = Join-Path $GameRoot 'Sea Power_Data/StreamingAssets'
    $localRows = @()
    if (Test-Path -LiteralPath $streaming) {
        foreach ($dir in @(Get-ChildItem -LiteralPath $streaming -Directory)) {
            if ($dir.Name -in @('original', 'user', 'EntityScenes') -or
                ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
            $localRows += $dir.Name
            foreach ($file in @(Get-TreeDlls $dir.FullName)) {
                Copy-Reference $file ('references/local/' + $dir.Name + '/' + $file.FullName.Substring($dir.FullName.Length + 1)) -ManagedOnly
            }
        }
    }
    Write-Report 'reports/local-mod-folders.txt' ($localRows -join "`r`n")
    if ($PlayerDataRoot -and (Test-Path -LiteralPath $PlayerDataRoot)) {
        $settings = Join-Path $PlayerDataRoot 'usersettings.ini'
        if (Test-Path -LiteralPath $settings) {
            $order = [regex]::Match([IO.File]::ReadAllText($settings), '(?ims)^\[LoadOrder\][^\r\n]*\r?\n.*?(?=^\[|\z)')
            if ($order.Success) { Write-Report 'reports/load-order.ini' $order.Value }
            else { $missing.Add('usersettings.ini [LoadOrder]') }
        }
    }
    $logs = [ordered]@{ 'BepInEx.log' = (Join-Path $GameRoot 'BepInEx/LogOutput.log') }
    if ($PlayerDataRoot) {
        $logs['Player.log'] = Join-Path $PlayerDataRoot 'Player.log'
        $logs['Player-prev.log'] = Join-Path $PlayerDataRoot 'Player-prev.log'
    }
    foreach ($name in $logs.Keys) {
        $path = $logs[$name]
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { $missing.Add($name); continue }
        if ((Get-Item -LiteralPath $path).Length -le 20MB) { $text = [IO.File]::ReadAllText($path) }
        else {
            $first = @(Get-Content -LiteralPath $path -Encoding UTF8 -TotalCount 20000)
            $last = @(Get-Content -LiteralPath $path -Encoding UTF8 -Tail 20000)
            $text = ($first + @('[SEST CAPTURE: middle of oversized log omitted]') + $last) -join "`r`n"
        }
        Write-Report ('reports/' + $name) $text
    }
    $receipt = [ordered]@{
        format = 1; purpose = 'Beta game with full pre-beta SEST feature parity'
        created_utc = [DateTime]::UtcNow.ToString('o'); build_status = $buildStatus
        native_sha256 = $nativeHash; powershell = $PSVersionTable.PSVersion.ToString()
        installation_changed = $false; references = @($records.ToArray()); missing = @($missing.ToArray())
    }
    Write-Report 'capture.json' ($receipt | ConvertTo-Json -Depth 8)
    New-Item -ItemType Directory -Path $OutDirectory -Force | Out-Null
    $archive = Join-Path $OutDirectory ('SEST-Beta-References-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 6) + '.zip')
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::CreateFromDirectory($stage, $archive, [IO.Compression.CompressionLevel]::Optimal, $false)
    Write-Host "Saved: $archive" -ForegroundColor Green
    Write-Host "Build: $buildStatus; reference files: $($records.Count)"
    Write-Host 'Attach this ZIP to the chat so the beta compatibility work can continue.'
    if ($missing.Count -gt 0) { Write-Host ('Missing optional capture inputs: ' + ($missing -join ', ')) }
} finally {
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}
