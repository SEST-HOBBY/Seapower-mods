<# Install verified release data for a local beta playtest, retaining the exact
   reviewed beta code set. The canonical Steam upload stays in the repository. #>
[CmdletBinding()]
param(
    [ValidateSet('Install','Restore')][string]$Action = 'Install',
    [string]$RepositoryRoot = '', [string]$GameDirectory = '',
    [string]$WorkshopContentRoot = '', [string]$BetaPackageRoot = '',
    [string]$BackupDirectory = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
function J { $p=[string]$args[0]; for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Hash([string]$p) { if(Test-Path -LiteralPath $p -PathType Leaf){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}else{''} }
function Closed { if(@(Get-Process -Name 'Sea Power','SeaPower' -ErrorAction SilentlyContinue).Count){throw 'Close Sea Power before replacing data.'} }
function Entries([string]$root) {
    $prefix=$root.TrimEnd([char[]]'\/')+[IO.Path]::DirectorySeparatorChar
    @(Get-ChildItem -LiteralPath $root -File -Recurse -Force | ForEach-Object {
        if($_.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked file refused.'}
        [pscustomobject]@{path=$_.FullName.Substring($prefix.Length).Replace('\','/');bytes=$_.Length;sha256=(Hash $_.FullName)}
    } | Sort-Object path)
}
# Windows' limits without long-path support: 259 characters for a file, 247
# for a folder. Checked for every destination before anything is copied.
function Assert-Fits([string]$root,$files,[string]$what) {
    $base=[IO.Path]::GetFullPath($root).TrimEnd([char[]]'\/')
    foreach($e in $files){
        $rel=[string]$e.path
        $file=$base.Length+1+$rel.Length
        $folder=$base.Length+1+[Math]::Max(0,$rel.LastIndexOf('/'))
        if($file -gt 259 -or $folder -gt 247){throw ('Windows path limit: the '+$what+' would need '+$file+' characters for '+$rel+' under '+$base+' (Windows allows 259 for a file and 247 for a folder). Nothing was copied; use a shorter -BackupDirectory.')}
    }
}
function Verify([string]$root,$files) {
    $prefix=[IO.Path]::GetFullPath($root).TrimEnd([char[]]'\/')+[IO.Path]::DirectorySeparatorChar
    $actual=@(Get-ChildItem -LiteralPath $root -File -Recurse -Force)
    if($actual.Count -ne @($files).Count){throw 'Release file count differs.'}
    foreach($e in $files){
        if($e.path -match '(^|[/\\])\.\.([/\\]|$)|^[/\\]|^[A-Za-z]:'){throw 'Unsafe release path.'}
        $p=[IO.Path]::GetFullPath((J $root $e.path))
        if(!$p.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Release path escapes its root.'}
        if(!(Test-Path -LiteralPath $p -PathType Leaf)){throw "Missing release file: $($e.path)"}
        $f=Get-Item -LiteralPath $p -Force
        if(($f.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $f.Length -ne $e.bytes -or (Hash $p) -ne $e.sha256){throw "Release file differs: $($e.path)"}
    }
}
Closed
if($Action -eq 'Restore'){
    if(!$BackupDirectory){throw 'Supply the backup directory printed by Install.'}
    $record=Get-Content -LiteralPath (J $BackupDirectory 'data-install.json') -Raw | ConvertFrom-Json
    if($record.format -ne 1 -or $record.workshop_item_id -ne '3812461539' -or (Split-Path -Leaf $record.destination) -ne '3812461539'){throw 'Unrecognised data backup.'}
    $destination=$record.destination
    Verify $destination $record.installed_files
    $previous=J $BackupDirectory 'previous'
    if(!(Test-Path -LiteralPath $previous -PathType Container)){throw 'Previous data backup is missing or already restored.'}
    $retired=J $BackupDirectory ('replaced-'+[guid]::NewGuid().ToString('N').Substring(0,8))
    Move-Item -LiteralPath $destination -Destination $retired
    try { Move-Item -LiteralPath $previous -Destination $destination }
    catch { Move-Item -LiteralPath $retired -Destination $destination;throw }
    Write-Host 'Previous Workshop data restored. Beta code and the previous folder contents came back together.'
    return
}
if(!$RepositoryRoot){$RepositoryRoot=Split-Path -Parent $PSScriptRoot}
$RepositoryRoot=(Resolve-Path -LiteralPath $RepositoryRoot).ProviderPath
if(!$GameDirectory){$GameDirectory=J (${env:ProgramFiles(x86)}) 'Steam' 'steamapps' 'common' 'Sea Power'}
$GameDirectory=(Resolve-Path -LiteralPath $GameDirectory).ProviderPath
if(!$WorkshopContentRoot){$WorkshopContentRoot=J (Split-Path -Parent (Split-Path -Parent $GameDirectory)) 'workshop' 'content' '1286220'}
$WorkshopContentRoot=(Resolve-Path -LiteralPath $WorkshopContentRoot).ProviderPath
if((Split-Path -Leaf $WorkshopContentRoot) -ne '1286220'){throw 'WorkshopContentRoot must end in 1286220.'}
if(!$BetaPackageRoot){throw 'Supply the extracted reviewed repair directory with -BetaPackageRoot.'}
$receipt=Get-Content -LiteralPath (J $BetaPackageRoot 'payload' 'build-receipt.json') -Raw | ConvertFrom-Json
if($receipt.candidate_revision -notmatch '^R(?:[789]|10|11|12)-'){throw 'This data playtest requires a reviewed R7, R8, R9, R10, R11 or R12 beta repair.'}
if((Hash (J $GameDirectory 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll')) -ne $receipt.target_game_sha256){throw 'Game build differs from the reviewed repair.'}
$destination=J $WorkshopContentRoot '3812461539'
$code=[ordered]@{
    'SEST.RuntimeFixes.dll'=(J $destination 'plugins' 'SEST.RuntimeFixes.dll')
    'SEST.ContactsFix.dll'=(J $destination 'plugins' 'SEST.ContactsFix.dll')
    'SEST.IdentifyDataPaths.dll'=(J $destination 'plugins' 'SEST.IdentifyDataPaths.dll')
    'AnchorChain.dll'=(J $GameDirectory 'BepInEx' 'config' 'SEST-BetaAnchorChain' 'AnchorChain.dll')
    'SEST.BetaSafeBootstrap.dll'=(J $GameDirectory 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll')
}
foreach($name in $code.Keys){
    if((Hash $code[$name]) -ne $receipt.files.PSObject.Properties[$name].Value){throw "Install the matching beta repair before refreshing data: $name differs."}
}
$manifest=Get-Content -LiteralPath (J $RepositoryRoot 'docs' 'releases' '20261107' 'upload-manifest.json') -Raw | ConvertFrom-Json
if($manifest.workshop_item_id -ne '3812461539' -or $manifest.status -ne 'candidate-needs-gameplay'){throw 'Wrong Workshop release manifest.'}
$source=J $RepositoryRoot 'integration' 'dist' 'SEST_Integration'
Verify $source $manifest.files
$steamapps=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $WorkshopContentRoot))
if(!$BackupDirectory){$BackupDirectory=J $steamapps 'SEST-release-backups' ((Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+[guid]::NewGuid().ToString('N').Substring(0,8))}
$BackupDirectory=[IO.Path]::GetFullPath($BackupDirectory)
if(Test-Path -LiteralPath $BackupDirectory){throw 'Backup directory already exists; choose a fresh one.'}
$ready=J $BackupDirectory 'ready';$previous=J $BackupDirectory 'previous'
Assert-Fits $ready $manifest.files 'ready copy'
Assert-Fits (J $BackupDirectory 'replaced-00000000') $manifest.files 'restore copy'
Assert-Fits $destination $manifest.files 'Workshop item folder'
New-Item -ItemType Directory -Path $BackupDirectory | Out-Null
Copy-Item -LiteralPath $source -Destination $ready -Recurse
Verify $ready $manifest.files
foreach($name in @('SEST.RuntimeFixes.dll','SEST.ContactsFix.dll','SEST.IdentifyDataPaths.dll')){
    Copy-Item -LiteralPath $code[$name] -Destination (J $ready 'plugins' $name) -Force
    if((Hash (J $ready 'plugins' $name)) -ne $receipt.files.PSObject.Properties[$name].Value){throw 'Preserved beta code copy failed.'}
}
$installed=@(Entries $ready)
Closed
foreach($name in $code.Keys){if((Hash $code[$name]) -ne $receipt.files.PSObject.Properties[$name].Value){throw 'Installed beta code changed during preparation.'}}
$record=[ordered]@{format=1;workshop_item_id='3812461539';destination=$destination;installed_files=$installed}
[IO.File]::WriteAllText((J $BackupDirectory 'data-install.json'),($record | ConvertTo-Json -Depth 6),(New-Object Text.UTF8Encoding($false)))
Move-Item -LiteralPath $destination -Destination $previous
try { Move-Item -LiteralPath $ready -Destination $destination;Verify $destination $installed }
catch {
    if(Test-Path -LiteralPath $destination){Move-Item -LiteralPath $destination -Destination (J $BackupDirectory 'failed')}
    Move-Item -LiteralPath $previous -Destination $destination
    throw
}
Write-Host 'Refreshed Workshop data installed; all five verified beta code files retained.' -ForegroundColor Green
Write-Host ('Backup: '+$BackupDirectory)
Write-Host 'Steam branch, load order and saves were not changed. The repository remains the canonical Workshop upload.'
Write-Host ('Restore data with: powershell -NoProfile -ExecutionPolicy Bypass -File "'+$PSCommandPath+'" -Action Restore -BackupDirectory "'+$BackupDirectory+'"')
