<# Prepare or remove a temporary top-level publishing copy. Never submits to Steam.
   The game's Create Mod picker lists folders inside StreamingAssets, so the
   publishing copy is a direct child with a short name (SEST_UP_<8 hex>);
   the verified copy and the moved-out copy go to a short work folder
   (default %LOCALAPPDATA%\SEST\Upload), not the toolkit folder. Every path
   is checked against Windows' path limit before anything is copied. #>
[CmdletBinding()]
param([ValidateSet('Stage','Finish')][string]$Action='Stage',[string]$GameRoot='',[string]$WorkRoot='')
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$env:POWERSHELL_TELEMETRY_OPTOUT='1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT='1'
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Write-Json([string]$Path,$Data) { [IO.File]::WriteAllText($Path,($Data | ConvertTo-Json -Depth 8),(New-Object Text.UTF8Encoding($false))) }
function Inventory([string]$Root) {
    $prefix=$Root.TrimEnd([IO.Path]::DirectorySeparatorChar,[IO.Path]::AltDirectorySeparatorChar)+[IO.Path]::DirectorySeparatorChar
    $result=@{}
    foreach($file in @(Get-ChildItem -LiteralPath $Root -Recurse -File -Force)){
        if($file.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked files are not supported in a publishing copy.'}
        $result[$file.FullName.Substring($prefix.Length)]=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    return $result
}
# Windows' limits without long-path support: 259 characters for a file and
# 247 for a folder. Checked for the actual tree before it is copied.
function Assert-TreeFits([string]$From,[string]$To) {
    $prefix=$From.TrimEnd([IO.Path]::DirectorySeparatorChar,[IO.Path]::AltDirectorySeparatorChar)+[IO.Path]::DirectorySeparatorChar
    $base=[IO.Path]::GetFullPath($To).TrimEnd([IO.Path]::DirectorySeparatorChar,[IO.Path]::AltDirectorySeparatorChar)
    foreach($item in @(Get-ChildItem -LiteralPath $From -Recurse -Force)){
        $length=$base.Length+1+$item.FullName.Length-$prefix.Length
        $limit=259; if($item.PSIsContainer){$limit=247}
        if($length -gt $limit){throw ('Windows path limit: copying to '+$base+' would need '+$length+' characters for '+$item.FullName.Substring($prefix.Length)+' (Windows allows 259 for a file and 247 for a folder). Nothing was copied; keep this message for review.')}
    }
}
function Compare-Trees([string]$From,[string]$To) {
    $expected=Inventory $From;$actual=Inventory $To
    if($expected.Count -ne $actual.Count){throw 'Publishing copy file count differs; both copies have been retained.'}
    foreach($name in $expected.Keys){if(!$actual.ContainsKey($name) -or $expected[$name] -ne $actual[$name]){throw ('Publishing copy differs: '+$name+'. Both copies have been retained.')}}
}
if(@(Get-Process -Name 'Sea Power','SeaPower' -ErrorAction SilentlyContinue).Count){throw 'Close Sea Power first.'}
$recordPath=J $PSScriptRoot 'PUBLISHING-COPY.json'
function Default-WorkRoot {
    $local=[Environment]::GetFolderPath('LocalApplicationData')
    if(!$local){$local=[IO.Path]::GetTempPath()}
    return (J $local 'SEST' 'Upload')
}
if($Action -eq 'Finish'){
    if(!(Test-Path -LiteralPath $recordPath -PathType Leaf)){throw 'No publishing-copy receipt exists in this toolkit.'}
    $record=Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    $source=[IO.Path]::GetFullPath([string]$record.folder)
    $stream=[IO.Path]::GetFullPath((J $record.game_root 'Sea Power_Data' 'StreamingAssets'))
    # SEST_UP_<8 hex> since 10 Nov 2026; the longer earlier name is still
    # recognised so an older receipt's folder can be moved out.
    if((Split-Path -Parent $source) -ne $stream -or (Split-Path -Leaf $source) -notmatch '^(SEST_UP_[0-9a-f]{8}|SEST_R12_UPLOAD_[0-9]{8}-[0-9]{6}-[0-9a-f]{8})$'){throw 'Publishing-copy receipt is not a recognised temporary folder.'}
    if(!(Test-Path -LiteralPath $source -PathType Container)){
        if($record.PSObject.Properties['moved_to'] -and (Test-Path -LiteralPath $record.moved_to -PathType Container)){Write-Host ('Already moved out: '+$record.moved_to);return}
        throw 'The recorded publishing folder is missing; retain the receipt for review.'
    }
    if(!$WorkRoot -and $record.PSObject.Properties['work_root']){$WorkRoot=[string]$record.work_root}
    if(!$WorkRoot){$WorkRoot=Default-WorkRoot}
    $id=[guid]::NewGuid().ToString('N').Substring(0,8)
    if($record.PSObject.Properties['id'] -and [string]$record.id -match '^[0-9a-f]{8}$'){$id=[string]$record.id}
    $destination=J $WorkRoot ('U-'+$id)
    if(Test-Path -LiteralPath $destination){$destination=J $WorkRoot ('U-'+[guid]::NewGuid().ToString('N').Substring(0,8))}
    Assert-TreeFits $source $destination
    New-Item -ItemType Directory -Path $WorkRoot -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination -Recurse
    Compare-Trees $source $destination
    Remove-Item -LiteralPath $source -Recurse -Force
    $record | Add-Member -NotePropertyName moved_to -NotePropertyValue $destination -Force
    Write-Json $recordPath $record
    Write-Host ('Publishing copy moved out of the game: '+$destination) -ForegroundColor Green
    Write-Host 'The subscribed item can now use its normal SETUP command. Original game and Workshop files were not removed.'
    $kept=@($destination); if($record.PSObject.Properties['verified_source']){$kept+=Split-Path -Parent ([string]$record.verified_source)}
    Write-Host ('Once the update shows on Steam these copies can be deleted: '+($kept -join '; '))
    return
}
if(Test-Path -LiteralPath $recordPath){
    $prior=Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    if(Test-Path -LiteralPath $prior.folder){throw 'An earlier publishing copy remains in the game. Finish that upload and run Finish-Upload.cmd first.'}
}
$preparedPath=J $PSScriptRoot 'PREPARED-PC.json'
if(!(Test-Path -LiteralPath $preparedPath -PathType Leaf)){throw 'Run Prepare-PC.cmd successfully before staging the Steam publishing copy.'}
$prepared=Get-Content -LiteralPath $preparedPath -Raw | ConvertFrom-Json
$receipt=Get-Content -LiteralPath (J $PSScriptRoot 'SOURCE-RECEIPT.json') -Raw | ConvertFrom-Json
if($receipt.beta_directory -ne 'R12' -or $prepared.release_commit -ne $receipt.release_commit){throw 'Preparation belongs to another release; use the complete R12 toolkit.'}
$repo=(Resolve-Path -LiteralPath $prepared.repository_root).ProviderPath
$head=(& git -C $repo rev-parse HEAD).Trim()
if($LASTEXITCODE -ne 0 -or $head -ne $receipt.release_commit){throw 'The prepared checkout has changed; run Prepare-PC.cmd again.'}
if(!$GameRoot){$GameRoot=[string]$prepared.game_root}
if(!$GameRoot){$GameRoot='C:\Program Files (x86)\Steam\steamapps\common\Sea Power'}
$GameRoot=(Resolve-Path -LiteralPath $GameRoot).ProviderPath
$stream=J $GameRoot 'Sea Power_Data' 'StreamingAssets'
if(!(Test-Path -LiteralPath $stream -PathType Container)){throw 'Sea Power StreamingAssets folder not found. Supply -GameRoot with the correct installation path.'}
$manifest=Get-Content -LiteralPath (J $repo 'docs' 'releases' '20261107' 'upload-manifest.json') -Raw | ConvertFrom-Json
if($manifest.release_revision -ne 'R12' -or !$manifest.beta_payload_included){throw 'The source is not the R12 Workshop feature update.'}
if(!$WorkRoot){$WorkRoot=Default-WorkRoot}
$WorkRoot=[IO.Path]::GetFullPath($WorkRoot)
$streamFull=[IO.Path]::GetFullPath($stream).TrimEnd([IO.Path]::DirectorySeparatorChar,[IO.Path]::AltDirectorySeparatorChar)
if($WorkRoot.StartsWith($streamFull,[StringComparison]::OrdinalIgnoreCase)){throw 'Choose a work folder outside the game.'}
# Short names: each is part of every copied file's path (the longest pack path
# is 133 characters, and Windows allows 259 for a file).
$id=[guid]::NewGuid().ToString('N').Substring(0,8)
$verified=J $WorkRoot ('V-'+$id)
$folder=J $stream ('SEST_UP_'+$id)
if(Test-Path -LiteralPath $folder){throw 'The publishing folder already exists. No files were overwritten.'}
New-Item -ItemType Directory -Path $WorkRoot -Force | Out-Null
# Verifies every file and checks every destination path before any copy.
& (J $repo 'tools' 'prepare-workshop-upload.ps1') -RepositoryRoot $repo -OutputDirectory $verified -CheckPathRoot @($folder,(J $WorkRoot ('U-'+$id)))
$source=J $verified 'SEST_Integration'
$record=[ordered]@{format=1;id=$id;game_root=$GameRoot;folder=$folder;work_root=$WorkRoot;verified_source=$source;release_commit=$head;workshop_item_id='3812461539';created_utc=[DateTime]::UtcNow.ToString('o')}
# Record the owned path before copying so a stopped copy can be moved out safely.
Write-Json $recordPath $record
Copy-Item -LiteralPath $source -Destination $folder -Recurse
Compare-Trees $source $folder
if(Get-Command Set-Clipboard -ErrorAction SilentlyContinue){try{Set-Clipboard -Value ([IO.File]::ReadAllText((J $PSScriptRoot 'STEAM-CHANGE-NOTE.txt')))}catch{Write-Host 'Copy the change note manually from STEAM-CHANGE-NOTE.txt.'}}
Write-Host ''
Write-Host 'PICK THIS FOLDER IN THE GAME UPLOADER:' -ForegroundColor Green
Write-Host $folder
Write-Host 'Keep this temporary Local mod disabled. In Create Mod choose Update Existing and item 3812461539.'
Write-Host 'Submit only after the PC gameplay checks pass. After upload, quit the game and run Finish-Upload.cmd.'
Write-Host 'No Steam submission has been performed by this script.'
