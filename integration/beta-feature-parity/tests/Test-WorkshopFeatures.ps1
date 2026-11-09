[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Capture,[Parameter(Mandatory=$true)][string]$PublicPack)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$checks=0
$temp=Join-Path ([IO.Path]::GetTempPath()) ('SEST-Workshop-Features-'+[guid]::NewGuid().ToString('N'))
function J{$p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p}
function Sha([string]$p){if(Test-Path -LiteralPath $p -PathType Leaf){(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant()}else{''}}
function Put([string]$p,[string]$t){New-Item -ItemType Directory -Path (Split-Path -Parent $p) -Force|Out-Null;[IO.File]::WriteAllText($p,$t)}
function Seed([string]$a,[string]$b){New-Item -ItemType Directory -Path (Split-Path -Parent $b) -Force|Out-Null;Copy-Item -LiteralPath $a -Destination $b -Force}
function Assert($v,[string]$why){if(!$v){throw $why};$script:checks++}
function Fails([scriptblock]$f){try{& $f|Out-Null;$false}catch{$true}}
try {
    $game=J $temp 'steamapps' 'common' 'Sea Power';$ws=J $temp 'steamapps' 'workshop' 'content' '1286220'
    $pack=J $ws '3812461539';$player=J $temp 'player';$app=J $temp 'app' 'SEST'
    Seed (J $PublicPack 'sest-workshop-features.ps1') (J $pack 'sest-workshop-features.ps1')
    Copy-Item -LiteralPath (J $PublicPack 'beta-support') -Destination (J $pack 'beta-support') -Recurse
    foreach($n in @('Seapower-Scripts.dll','Noesis.NoesisGUI.dll','UnityEngine.CoreModule.dll','UnityEngine.InputLegacyModule.dll','UnityEngine.IMGUIModule.dll')){Seed (J $Capture 'references' 'managed' $n) (J $game 'Sea Power_Data' 'Managed' $n)}
    foreach($n in @('BepInEx.dll','0Harmony.dll','Mono.Cecil.dll')){Seed (J $Capture 'references' 'bepinex' 'core' $n) (J $game 'BepInEx' 'core' $n)}
    Seed (J $Capture 'references' 'bepinex' 'plugins' 'AnchorChain.Preloader.dll') (J $game 'BepInEx' 'plugins' 'AnchorChain.Preloader.dll')
    foreach($pair in @(@('3380210757','AnchorChain.dll'),@('3790594162','IdentifyExpanded.dll'),@('3807187341','CombatCosts.dll'),@('3819427362','ContactLog.dll'),@('3818251045','SeaPowerSquadPanel.dll'),@('3826396311','SeaPowerPopOut.dll'))){Seed (J $Capture 'references' 'workshop' 'library-1' $pair[0] $pair[1]) (J $ws $pair[0] $pair[1])}
    foreach($n in @('SEST.RuntimeFixes.dll','SEST.ContactsFix.dll')){Seed (J $PublicPack 'plugins' $n) (J $pack 'plugins' $n)}
    $stableRuntime=Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll');$stableUi=Sha (J $pack 'plugins' 'SEST.ContactsFix.dll')
    $settings=J $player 'usersettings.ini'
    $before="[LoadOrder]`r`nNumberOfModFiles=3`r`nMod1Directory=3812461539,True`r`nMod2Directory=3790594162,True`r`nMod3Directory=IdentifyExpanded,False`r`n"
    Put $settings $before;Put (J $player 'saves' 'world.save') 'NATIVE SAVE';Put (J $pack 'missions' 'keep.ini') 'MISSION'
    $local=J $game 'Sea Power_Data' 'StreamingAssets' 'IdentifyExpanded';Put (J $local 'audio' 'broadcast' 'keep.mp3') 'AUDIO'
    $frozen=@{};foreach($f in @(Get-ChildItem -LiteralPath (J $game 'Sea Power_Data' 'Managed') -File)+@(Get-ChildItem -LiteralPath $ws -Recurse -File|Where-Object{$_.FullName -notlike ($pack+'*')})){$frozen[$f.FullName]=Sha $f.FullName}
    $helper=J $pack 'sest-workshop-features.ps1';$options=@{GameRoot=$game;WorkshopContentRoot=$ws;PlayerDataRoot=$player;AppDataRoot=$app}
    $native=J $game 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll'
    Put $native 'OTHER GAME BUILD'; & $helper @options
    Assert (!(Test-Path -LiteralPath $app)) 'Unsupported game wrote a feature cache'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime) 'Unsupported game replaced normal-release code'
    Seed (J $Capture 'references' 'managed' 'Seapower-Scripts.dll') $native
    $archive=J $pack 'beta-support' 'SEST-Beta-Features.zip';$bytes=[IO.File]::ReadAllBytes($archive);Put $archive 'CHANGED'
    Assert (Fails {& $helper @options}) 'Altered Workshop archive was accepted'
    Assert (!(Test-Path -LiteralPath (J $game 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll'))) 'Bad archive installed a bootstrap'
    [IO.File]::WriteAllBytes($archive,$bytes)
    $badOptions=@{}+$options;$badOptions.AppDataRoot=J $game 'bad-cache'
    Assert (Fails {& $helper @badOptions}) 'Feature cache inside game was accepted'
    & $helper @options
    $statePath=J $app 'BetaCompatibility' 'current.json';$state=Get-Content -LiteralPath $statePath -Raw|ConvertFrom-Json
    $token=$state.token;$backup=J $app 'BetaCompatibility' 'backups' $token;$loader=J $game 'BepInEx' 'config' 'SEST-BetaAnchorChain'
    Assert ($state.phase -eq 'staged') 'First SETUP did not stage the bundled features'
    Assert (!(Test-Path -LiteralPath (J $loader 'enable.flag'))) 'First SETUP bypassed the menu probe'
    Assert ((Get-Content -LiteralPath $settings -Raw) -ceq $before) 'Stage changed load order'
    Assert (Test-Path -LiteralPath $local) 'Stage moved Identify data before a probe'
    $manifest=Get-Content -LiteralPath (J $pack 'beta-support' 'manifest.json') -Raw|ConvertFrom-Json
    $cache=J $app 'WorkshopFeatures' $manifest.archive_sha256 'package'
    $receipt=Get-Content -LiteralPath (J $cache 'payload' 'build-receipt.json') -Raw|ConvertFrom-Json
    $proof=@{format=1;token=$token;enabled=$false;native_sha256=$receipt.target_game_sha256;created_utc=[DateTime]::UtcNow.ToString('o')}
    Put (J $loader 'probe-ready.json') ($proof|ConvertTo-Json)
    & $helper @options
    Assert ((Get-Content -LiteralPath $statePath -Raw|ConvertFrom-Json).phase -eq 'enabled') 'Second SETUP did not enable features after the probe'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $receipt.files.'SEST.RuntimeFixes.dll') 'Workshop runtime feature payload missing'
    Assert (!(Test-Path -LiteralPath $local)) 'Identify local folder was not migrated'
    Assert ((Get-Content -LiteralPath (J $app 'IdentifyExpanded' 'audio' 'broadcast' 'keep.mp3') -Raw) -eq 'AUDIO') 'Identify audio lost'
    $backupHash=Sha (J $backup 'files' 'SEST.RuntimeFixes.dll')
    foreach($n in @('SEST.RuntimeFixes.dll','SEST.ContactsFix.dll')){Seed (J $PublicPack 'plugins' $n) (J $pack 'plugins' $n)}
    Remove-Item -LiteralPath (J $pack 'plugins' 'SEST.IdentifyDataPaths.dll')
    $journal=Get-Content -LiteralPath $statePath -Raw
    $fault=[pscustomobject]@{Fired=$false;Path=(J $cache 'payload' 'SEST.ContactsFix.dll')}
    try {
        function Copy-Item {[CmdletBinding()]param([string]$LiteralPath,[string]$Destination,[switch]$Force)
            if(!$fault.Fired -and $LiteralPath -eq $fault.Path){$fault.Fired=$true;throw 'Injected feature update failure'}
            Microsoft.PowerShell.Management\Copy-Item @PSBoundParameters
        }
        Assert (Fails {& $helper @options}) 'Steam refresh copy failure was not propagated'
    } finally {Remove-Item -LiteralPath 'Function:\Copy-Item'}
    Assert $fault.Fired 'Steam refresh copy failure did not reach the code copy'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime -and (Sha (J $pack 'plugins' 'SEST.ContactsFix.dll')) -eq $stableUi) 'Failed Steam refresh did not restore the observed code'
    Assert (!(Test-Path -LiteralPath (J $pack 'plugins' 'SEST.IdentifyDataPaths.dll'))) 'Failed refresh left a newly added shim'
    Assert ((Get-Content -LiteralPath $statePath -Raw) -ceq $journal) 'Failed refresh altered the original journal'
    & $helper @options
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $receipt.files.'SEST.RuntimeFixes.dll') 'Steam refresh did not reapply bundled features'
    Assert ((Get-Content -LiteralPath $statePath -Raw|ConvertFrom-Json).token -eq $token) 'Steam refresh replaced the original journal token'
    Assert ((Sha (J $backup 'files' 'SEST.RuntimeFixes.dll')) -eq $backupHash) 'Steam refresh overwrote original backups'
    Put (J $pack 'plugins' 'SEST.RuntimeFixes.dll') 'UNREVIEWED CODE'
    Assert (Fails {& $helper @options}) 'Unreviewed runtime was overwritten'
    Assert ((Get-Content -LiteralPath (J $pack 'plugins' 'SEST.RuntimeFixes.dll') -Raw) -eq 'UNREVIEWED CODE') 'Rejected repair changed unreviewed code'
    Seed (J $PublicPack 'plugins' 'SEST.RuntimeFixes.dll') (J $pack 'plugins' 'SEST.RuntimeFixes.dll')
    Seed (J $PublicPack 'plugins' 'SEST.ContactsFix.dll') (J $pack 'plugins' 'SEST.ContactsFix.dll')
    & $helper @options
    & $helper @options -Action Restore
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime) 'Original runtime did not restore'
    Assert ((Get-Content -LiteralPath $settings -Raw) -ceq $before) 'Original settings did not restore'
    Assert ((Get-Content -LiteralPath (J $local 'audio' 'broadcast' 'keep.mp3') -Raw) -eq 'AUDIO') 'Local Identify audio did not restore'
    Assert ((Get-Content -LiteralPath (J $player 'saves' 'world.save') -Raw) -eq 'NATIVE SAVE') 'Native save changed'
    Assert ((Get-Content -LiteralPath (J $pack 'missions' 'keep.ini') -Raw) -eq 'MISSION') 'Campaign data changed'
    foreach($file in $frozen.Keys){Assert ((Sha $file) -eq $frozen[$file]) ('Native/author file changed: '+$file)}
    Assert (@(Get-ChildItem -LiteralPath (J $pack 'beta-support') -Recurse -Filter '*.dll').Count -eq 0) 'Archive leaked active duplicate DLLs into Workshop'
    Write-Host "Workshop-included feature fixture passed: $checks assertions; no Unity gameplay."
} finally {if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp -Recurse -Force}}
