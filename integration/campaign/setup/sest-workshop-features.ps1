#Requires -Version 5.1
<# Installs the feature bundle carried INSIDE the Workshop item.
   Archive stays inert in Workshop; extraction goes to the user's SEST cache.
   The existing staged/probed installer and restore journal own code changes. #>
[CmdletBinding()]
param(
    [ValidateSet('Setup','Collect','Restore','Disable')][string]$Action='Setup',
    [string]$GameRoot='', [string]$WorkshopContentRoot='',
    [string]$PlayerDataRoot='', [string]$AppDataRoot='', [string]$OutDirectory=''
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Sha([string]$p){if(Test-Path -LiteralPath $p -PathType Leaf){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}else{''}}
if(@(Get-Process -Name 'Sea Power','SeaPower' -ErrorAction SilentlyContinue).Count){throw 'Close Sea Power before installing or restoring features.'}
if(!$GameRoot){$GameRoot=J ([Environment]::GetEnvironmentVariable('ProgramFiles(x86)')) 'Steam' 'steamapps' 'common' 'Sea Power'}
$GameRoot=(Resolve-Path -LiteralPath $GameRoot).ProviderPath
if(!$WorkshopContentRoot){
    if((Split-Path -Leaf $PSScriptRoot) -eq '3812461539'){$WorkshopContentRoot=Split-Path -Parent $PSScriptRoot}
    else{$WorkshopContentRoot=J (Split-Path -Parent (Split-Path -Parent $GameRoot)) 'workshop' 'content' '1286220'}
}
$WorkshopContentRoot=(Resolve-Path -LiteralPath $WorkshopContentRoot).ProviderPath
if(!$AppDataRoot){$AppDataRoot=J ([Environment]::GetFolderPath('LocalApplicationData')) 'SEST'}
if(!$PlayerDataRoot){$PlayerDataRoot=J ([Environment]::GetFolderPath('UserProfile')) 'AppData' 'LocalLow' 'Triassic Games' 'Sea Power'}
$AppDataRoot=[IO.Path]::GetFullPath($AppDataRoot)
foreach($protectedRoot in @($GameRoot,$WorkshopContentRoot)){
    $protected=[IO.Path]::GetFullPath($protectedRoot).TrimEnd([char[]]'\/')
    if($AppDataRoot.Equals($protected,[StringComparison]::OrdinalIgnoreCase) -or $AppDataRoot.StartsWith($protected+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Choose a feature cache outside the game and Workshop folders.'}
}
$bundleRoot=J $PSScriptRoot 'beta-support'
$manifest=Get-Content -LiteralPath (J $bundleRoot 'manifest.json') -Raw | ConvertFrom-Json
if($manifest.format -ne 1 -or $manifest.workshop_item_id -ne '3812461539' -or $manifest.archive -cne 'SEST-Beta-Features.zip' -or
   $manifest.archive_sha256 -notmatch '^[a-f0-9]{64}$'){throw 'Unrecognised Workshop feature bundle.'}
$native=J $GameRoot 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll'
if((Sha $native) -ne $manifest.target_game_sha256){
    if($Action -eq 'Setup'){
        Write-Host 'The bundled beta features are for a different game build. The normal Workshop plugins remain selected; no beta files were installed.'
        return
    }
}
$archive=J $bundleRoot $manifest.archive
if((Sha $archive) -ne $manifest.archive_sha256){throw 'Workshop feature archive differs. Let Steam finish downloading the item, then rerun SETUP.'}
$cache=J $AppDataRoot 'WorkshopFeatures' $manifest.archive_sha256
$package=J $cache 'package'
$prefix=[IO.Path]::GetFullPath($package).TrimEnd([char[]]'\/')+[IO.Path]::DirectorySeparatorChar
function Check-Package([string]$root){
    if(!(Test-Path -LiteralPath $root -PathType Container)){return $false}
    if((Get-Item -LiteralPath $root -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked feature cache refused.'}
    $actual=@(Get-ChildItem -LiteralPath $root -Recurse -Force -File)
    if($actual.Count -ne @($manifest.files.PSObject.Properties).Count){return $false}
    foreach($entry in $manifest.files.PSObject.Properties){
        $file=J $root $entry.Name
        if(!(Test-Path -LiteralPath $file -PathType Leaf) -or
           ((Get-Item -LiteralPath $file -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -or
           (Sha $file) -ne $entry.Value){return $false}
    }
    return $true
}
# Validate all entry names before extraction, even though the archive is pinned.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try {
    $seen=New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach($entry in $zip.Entries){
        $name=$entry.FullName.Replace('\','/')
        if(!$name -or $name -match '(^|/)\.\.(/|$)|^/|:|\x00' -or $name.EndsWith('/') -or
           !$seen.Add($name) -or !$manifest.files.PSObject.Properties[$name] -or
           (($entry.ExternalAttributes -shr 16) -band 61440) -eq 40960){throw 'Unsafe or unexpected feature archive entry.'}
        if(![IO.Path]::GetFullPath((J $package $name)).StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Feature entry escapes its cache.'}
    }
    if($seen.Count -ne @($manifest.files.PSObject.Properties).Count){throw 'Feature archive entry count differs.'}
} finally {$zip.Dispose()}
if(!(Check-Package $package)){
    New-Item -ItemType Directory -Path $cache -Force | Out-Null
    if(Test-Path -LiteralPath $package){Move-Item -LiteralPath $package -Destination ($package+'.kept-'+[guid]::NewGuid().ToString('N'))}
    $temporary=$package+'.extract-'+[guid]::NewGuid().ToString('N')
    [IO.Compression.ZipFile]::ExtractToDirectory($archive,$temporary)
    if(!(Check-Package $temporary)){throw 'Extracted feature files failed verification.'}
    Move-Item -LiteralPath $temporary -Destination $package
}
$options=@{GameRoot=$GameRoot;WorkshopContentRoot=$WorkshopContentRoot;PlayerDataRoot=$PlayerDataRoot;AppDataRoot=$AppDataRoot}
$installer=J $package 'Install-SEST-Beta.ps1'
$repair=J $package 'Repair-SEST-Beta-Startup.ps1'
if($Action -ne 'Setup'){
    if($OutDirectory){$options.OutDirectory=$OutDirectory}
    & $repair @options -Action $Action
    return
}
if(!(Test-Path -LiteralPath (J $WorkshopContentRoot '3812461539' 'plugins' 'SEST.RuntimeFixes.dll'))){throw 'Subscribe to Workshop item 3812461539 before enabling its bundled features.'}
$statePath=J $AppDataRoot 'BetaCompatibility' 'current.json'
$phase=''
if(Test-Path -LiteralPath $statePath){$phase=[string](Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json).phase}
if($phase -eq 'enabled'){
    & $repair @options -Action Repair
    Write-Host 'Workshop feature update ready: F11 World Operations, service progress and Coordinated Strike refinements.' -ForegroundColor Green
    return
}
if($phase -and $phase -notin @('staged','restored')){throw 'An incomplete feature-install journal exists. Retain it for review before continuing.'}
& $installer @options -Action Stage
$probe=J $GameRoot 'BepInEx' 'config' 'SEST-BetaAnchorChain' 'probe-ready.json'
if(Test-Path -LiteralPath $probe){
    & $installer @options -Action Enable
    Write-Host 'Workshop features enabled. Start Sea Power and check F11 World Operations and Coordinated Strike.' -ForegroundColor Green
}else{
    Write-Host 'FEATURE SETUP: launch Sea Power to the main menu, wait about 10 seconds, quit, then run SETUP once more.' -ForegroundColor Cyan
}
