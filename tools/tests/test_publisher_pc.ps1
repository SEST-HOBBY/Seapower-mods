$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$repoSource=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$temp=Join-Path ([IO.Path]::GetTempPath()) ('sest-publisher-fixture-'+[guid]::NewGuid().ToString('N'))
$checks=0
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Put([string]$Path,[string]$Text){New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null;[IO.File]::WriteAllText($Path,$Text)}
function Json([string]$Path,$Data){Put $Path ($Data | ConvertTo-Json -Depth 10)}
function Assert([bool]$Ok,[string]$Why){if(!$Ok){throw $Why};$script:checks++}
function Fails([scriptblock]$Action){try{& $Action | Out-Null;return $false}catch{return $true}}
try{
    $toolkit=J $temp 'toolkit';$repo=J $temp 'repo';$game=J $temp 'steamapps' 'common' 'Sea Power'
    $stream=J $game 'Sea Power_Data' 'StreamingAssets';$dist=J $repo 'integration' 'dist' 'SEST_Integration'
    $docs=J $repo 'docs' 'releases' '20261107';$scriptFile=J $toolkit 'Upload-PC.ps1'
    New-Item -ItemType Directory -Path $toolkit,$stream,$docs,(J $repo 'tools') -Force | Out-Null
    Copy-Item -LiteralPath (J $repoSource 'docs' 'releases' '20261107' 'Upload-PC.ps1') -Destination $scriptFile
    Copy-Item -LiteralPath (J $repoSource 'tools' 'prepare-workshop-upload.ps1') -Destination (J $repo 'tools' 'prepare-workshop-upload.ps1')
    Put (J $dist '_info.ini') '[Mod]';Put (J $dist 'payload.txt') 'REVIEWED PAYLOAD'
    Put (J $dist 'beta-support' 'SEST-Beta-Features.zip') 'INERT FIXTURE ARCHIVE'
    foreach($name in @('README-FIRST.txt','STEAM-CHANGE-NOTE.txt')){Put (J $docs $name) $name;Put (J $toolkit $name) $name}
    $files=@(Get-ChildItem -LiteralPath $dist -Recurse -File | ForEach-Object {@{path=$_.FullName.Substring($dist.Length+1).Replace('\','/');bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
    Json (J $docs 'upload-manifest.json') @{workshop_item_id='3812461539';status='candidate-needs-gameplay';release_revision='R12';beta_payload_included=$true;files=$files}
    & git -C $repo init --quiet
    & git -C $repo add .
    & git -C $repo -c user.name=SEST-DEV -c user.email=fixture@example.invalid commit --quiet -m 'Publisher fixture'
    if($LASTEXITCODE -ne 0){throw 'Cannot initialise fixture repository'}
    $head=(& git -C $repo rev-parse HEAD).Trim()
    Json (J $toolkit 'SOURCE-RECEIPT.json') @{beta_directory='R12';release_commit=$head}
    $native=J $game 'Sea Power_Data' 'Managed' 'native.dll';Put $native 'NATIVE MUST STAY'
    $oldMod=J $stream 'OtherMod' '_info.ini';Put $oldMod 'OTHER MOD MUST STAY'
    Assert (Fails {& $scriptFile -GameRoot $game}) 'Unprepared upload was accepted'
    Json (J $toolkit 'PREPARED-PC.json') @{repository_root=$repo;release_commit=$head;game_root=$game}
    & $scriptFile
    $record=Get-Content -LiteralPath (J $toolkit 'PUBLISHING-COPY.json') -Raw | ConvertFrom-Json
    Assert ((Split-Path -Parent $record.folder) -eq $stream -and (Test-Path -LiteralPath (J $record.folder '_info.ini'))) 'Publishing pack is not directly under StreamingAssets'
    Assert ([IO.File]::ReadAllText((J $record.folder 'beta-support' 'SEST-Beta-Features.zip')) -eq 'INERT FIXTURE ARCHIVE') 'Bundled features were omitted'
    Assert (Fails {& $scriptFile}) 'An active publishing folder was duplicated'
    Put (J $record.folder 'uploader-added.txt') 'PRESERVE UPLOADER CHANGES'
    & $scriptFile -Action Finish
    $finished=Get-Content -LiteralPath (J $toolkit 'PUBLISHING-COPY.json') -Raw | ConvertFrom-Json
    Assert (!(Test-Path -LiteralPath $record.folder) -and (Test-Path -LiteralPath $finished.moved_to)) 'Temporary pack was not moved outside the game'
    Assert ([IO.File]::ReadAllText((J $finished.moved_to 'uploader-added.txt')) -eq 'PRESERVE UPLOADER CHANGES') 'Uploader changes were lost'
    Assert ([IO.File]::ReadAllText($native) -eq 'NATIVE MUST STAY' -and [IO.File]::ReadAllText($oldMod) -eq 'OTHER MOD MUST STAY') 'Unrelated game/mod files changed'
    & $scriptFile -Action Finish
    Assert (Test-Path -LiteralPath $finished.moved_to) 'Repeat finish lost the saved copy'
    Put (J $dist 'payload.txt') 'UNREVIEWED CODE'
    Assert (Fails {& $scriptFile}) 'Modified canonical payload was staged'
    Assert (@(Get-ChildItem -LiteralPath $stream -Directory | Where-Object Name -like 'SEST_R12_UPLOAD_*').Count -eq 0) 'Failed preparation left a game-visible pack'
    Write-Host "Publisher PC fixture passed: $checks assertions; no real game or Steam submission."
}finally{if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp -Recurse -Force}}
