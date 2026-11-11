$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$repoSource=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
# A short fixture root, so the game and work folders below can be given the
# exact lengths of their defaults on Windows.
$temp=Join-Path ([IO.Path]::GetTempPath()) ('spf-'+[guid]::NewGuid().ToString('N').Substring(0,8))
$checks=0
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Put([string]$Path,[string]$Text){New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null;[IO.File]::WriteAllText($Path,$Text)}
function Json([string]$Path,$Data){Put $Path ($Data | ConvertTo-Json -Depth 10)}
function Assert([bool]$Ok,[string]$Why){if(!$Ok){throw $Why};$script:checks++}
function Fails([scriptblock]$Action){try{& $Action | Out-Null;return $false}catch{return $true}}
# A folder under the fixture root whose full path has exactly $Length
# characters once $Tail is appended, or $null when the root is already longer.
function Sized([int]$Length,[string]$Tail,[string]$Name){
    $pad=$Length-$temp.Length-2-$Tail.Length
    if($pad -lt 1){return $null}
    return (J $temp ($Name+('x'*($pad-1))) $Tail)
}
try{
    # The real longest path in the canonical upload (133 characters for R12).
    $real=Get-Content -LiteralPath (J $repoSource 'docs' 'releases' '20261107' 'upload-manifest.json') -Raw | ConvertFrom-Json
    $longest=@($real.files | ForEach-Object { [string]$_.path } | Sort-Object Length -Descending)[0]
    $toolkit=J $temp 'toolkit';$repo=J $temp 'repo'
    $dist=J $repo 'integration' 'dist' 'SEST_Integration'
    $docs=J $repo 'docs' 'releases' '20261107';$scriptFile=J $toolkit 'Upload-PC.ps1'
    # The default game folder's StreamingAssets has 86 characters on Windows
    # (C:\Program Files (x86)\Steam\steamapps\common\Sea Power\...), and the
    # default work folder 54 for a 20-character user name
    # (C:\Users\<name>\AppData\Local\SEST\Upload).
    $tail=[IO.Path]::Combine('steamapps','common','Sea Power')
    $game=Sized (86-('Sea Power_Data'.Length+'StreamingAssets'.Length+2)) $tail 'g'
    $exact=[bool]$game
    if(!$exact){$game=J $temp 'g' $tail;Write-Host 'Fixture root too long to give the folders their Windows default lengths; shorter folders used.'}
    $work=Sized 54 'Upload' 'w'; if(!$work){$work=J $temp 'w' 'Upload'}
    $stream=J $game 'Sea Power_Data' 'StreamingAssets'
    if($exact){Assert ($stream.Length -eq 86 -and $work.Length -eq 54) 'Fixture folders do not have the Windows default lengths'}
    New-Item -ItemType Directory -Path $toolkit,$stream,$docs,(J $repo 'tools') -Force | Out-Null
    Copy-Item -LiteralPath (J $repoSource 'docs' 'releases' '20261107' 'Upload-PC.ps1') -Destination $scriptFile
    Copy-Item -LiteralPath (J $repoSource 'tools' 'prepare-workshop-upload.ps1') -Destination (J $repo 'tools' 'prepare-workshop-upload.ps1')
    Put (J $dist '_info.ini') '[Mod]';Put (J $dist 'payload.txt') 'REVIEWED PAYLOAD'
    Put (J $dist 'beta-support' 'SEST-Beta-Features.zip') 'INERT FIXTURE ARCHIVE'
    Put (J $dist ($longest.Replace('/',[string][IO.Path]::DirectorySeparatorChar))) 'LONGEST REAL PATH'
    foreach($name in @('README-FIRST.txt','STEAM-CHANGE-NOTE.txt')){Put (J $docs $name) $name;Put (J $toolkit $name) $name}
    $files=@(Get-ChildItem -LiteralPath $dist -Recurse -File | ForEach-Object {@{path=$_.FullName.Substring($dist.Length+1).Replace('\','/');bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
    Json (J $docs 'upload-manifest.json') @{workshop_item_id='3812461539';status='candidate-needs-gameplay';release_revision='R12';beta_payload_included=$true;files=$files}
    & git -C $repo init --quiet
    & git -C $repo add .
    & git -C $repo -c user.name=SEST-DEV -c user.email=fixture@example.invalid commit --quiet -m 'Publisher fixture'
    if($LASTEXITCODE -ne 0){throw 'Cannot initialise fixture repository'}
    $head=(& git -C $repo rev-parse HEAD).Trim()
    Json (J $toolkit 'SOURCE-RECEIPT.json') @{beta_directory='R13';release_commit=$head}
    $native=J $game 'Sea Power_Data' 'Managed' 'native.dll';Put $native 'NATIVE MUST STAY'
    $oldMod=J $stream 'OtherMod' '_info.ini';Put $oldMod 'OTHER MOD MUST STAY'
    Assert (Fails {& $scriptFile -GameRoot $game -WorkRoot $work}) 'Unprepared upload was accepted'
    Json (J $toolkit 'PREPARED-PC.json') @{repository_root=$repo;release_commit=$head;game_root=$game}
    & $scriptFile -WorkRoot $work
    $record=Get-Content -LiteralPath (J $toolkit 'PUBLISHING-COPY.json') -Raw | ConvertFrom-Json
    Assert ((Split-Path -Parent $record.folder) -eq $stream -and (Test-Path -LiteralPath (J $record.folder '_info.ini'))) 'Publishing pack is not directly under StreamingAssets'
    Assert ((Split-Path -Leaf $record.folder) -match '^SEST_UP_[0-9a-f]{8}$') 'Publishing folder does not have the short name'
    Assert ([IO.File]::ReadAllText((J $record.folder 'beta-support' 'SEST-Beta-Features.zip')) -eq 'INERT FIXTURE ARCHIVE') 'Bundled features were omitted'
    $deepest=J $record.folder ($longest.Replace('/',[string][IO.Path]::DirectorySeparatorChar))
    Assert ([IO.File]::ReadAllText($deepest) -eq 'LONGEST REAL PATH') 'The longest real path was not copied'
    if($exact){Assert ($deepest.Length -le 259) ('The longest real path needs '+$deepest.Length+' characters in the default game folder')}
    Assert ($record.verified_source.StartsWith($work) -and @(Get-ChildItem -LiteralPath $toolkit -Directory | Where-Object { $_.Name -like 'Verified-Upload-*' }).Count -eq 0) 'The verified copy was not made in the short work folder'
    Assert (@(Get-ChildItem -LiteralPath $work -Directory | Where-Object { $_.Name -like '*.tmp*' }).Count -eq 0) 'A staging folder was left behind'
    Assert (Fails {& $scriptFile -WorkRoot $work}) 'An active publishing folder was duplicated'
    Put (J $record.folder 'uploader-added.txt') 'PRESERVE UPLOADER CHANGES'
    $said=(& $scriptFile -Action Finish 6>&1 | Out-String)
    $finished=Get-Content -LiteralPath (J $toolkit 'PUBLISHING-COPY.json') -Raw | ConvertFrom-Json
    Assert (!(Test-Path -LiteralPath $record.folder) -and (Test-Path -LiteralPath $finished.moved_to)) 'Temporary pack was not moved outside the game'
    Assert ((Split-Path -Parent $finished.moved_to) -eq $work -and (Split-Path -Leaf $finished.moved_to) -eq ('U-'+$record.id)) 'The moved-out copy is not in the work folder'
    Assert ($said -match 'can be deleted') 'Finish did not say which copies can be deleted'
    Assert ([IO.File]::ReadAllText((J $finished.moved_to 'uploader-added.txt')) -eq 'PRESERVE UPLOADER CHANGES') 'Uploader changes were lost'
    Assert ([IO.File]::ReadAllText($native) -eq 'NATIVE MUST STAY' -and [IO.File]::ReadAllText($oldMod) -eq 'OTHER MOD MUST STAY') 'Unrelated game/mod files changed'
    & $scriptFile -Action Finish
    Assert (Test-Path -LiteralPath $finished.moved_to) 'Repeat finish lost the saved copy'
    # A game folder 23 characters longer than the default puts the longest
    # real path at 260: refused before anything is copied, with the reason.
    $longGame=Sized (86+23-('Sea Power_Data'.Length+'StreamingAssets'.Length+2)) $tail 'L'
    if(!$longGame){$longGame=J $temp ('L'*[Math]::Max(1,260-$temp.Length-$longest.Length-80)) $tail}
    $longStream=J $longGame 'Sea Power_Data' 'StreamingAssets';New-Item -ItemType Directory -Path $longStream -Force | Out-Null
    $before=@(Get-ChildItem -LiteralPath $work).Count
    $why='';try{& $scriptFile -GameRoot $longGame -WorkRoot $work | Out-Null}catch{$why=$_.Exception.Message}
    Assert ($why -match 'Windows path limit' -and $why -match '259') 'A publishing path over the Windows limit was not refused clearly'
    Assert (@(Get-ChildItem -LiteralPath $longStream).Count -eq 0 -and @(Get-ChildItem -LiteralPath $work).Count -eq $before) 'A refused publishing copy left files behind'
    $kept=Get-Content -LiteralPath (J $toolkit 'PUBLISHING-COPY.json') -Raw | ConvertFrom-Json
    Assert ($kept.moved_to -eq $finished.moved_to) 'A refused publishing copy replaced the receipt'
    Assert (Fails {& $scriptFile -GameRoot $game -WorkRoot $stream}) 'A work folder inside the game was accepted'
    Put (J $dist 'payload.txt') 'UNREVIEWED CODE'
    Assert (Fails {& $scriptFile -WorkRoot $work}) 'Modified canonical payload was staged'
    Assert (@(Get-ChildItem -LiteralPath $stream -Directory | Where-Object Name -like 'SEST_UP_*').Count -eq 0) 'Failed preparation left a game-visible pack'
    Write-Host "all checks passed: publisher PC ($checks); no real game or Steam submission."
}finally{if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp -Recurse -Force}}
