[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Capture,
    # A built public pack (integration/dist/SEST_Integration) with its
    # generated beta-support folder, sest-workshop-features.ps1 and plugins.
    [string]$PublicPack='',
    # Or a compiled candidate: the fixture then packs this repository's
    # current installer scripts with that payload, exactly as package.py and
    # build-workshop-support.py lay them out, so the source is what is tested.
    [string]$Candidate='',
    # Optional: the previously published stable UI (51b56f5e, from the
    # release's base commit), to check that a Restore keeps Steam's newer
    # normal-release copy rather than an older backup.
    [string]$PublishedUi=''
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
if([bool]$PublicPack -eq [bool]$Candidate){throw 'Pass either -PublicPack or -Candidate.'}
$checks=0
$temp=Join-Path ([IO.Path]::GetTempPath()) ('SEST-Workshop-Features-'+[guid]::NewGuid().ToString('N'))
$repoRoot=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
function J{$p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p}
function Sha([string]$p){if(Test-Path -LiteralPath $p -PathType Leaf){(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant()}else{''}}
function Put([string]$p,[string]$t){New-Item -ItemType Directory -Path (Split-Path -Parent $p) -Force|Out-Null;[IO.File]::WriteAllText($p,$t)}
function Seed([string]$a,[string]$b){New-Item -ItemType Directory -Path (Split-Path -Parent $b) -Force|Out-Null;Copy-Item -LiteralPath $a -Destination $b -Force}
function Assert($v,[string]$why){if(!$v){throw $why};$script:checks++}
function Fails([scriptblock]$f){try{& $f|Out-Null;$false}catch{$true}}
function State{Get-Content -LiteralPath $statePath -Raw|ConvertFrom-Json}
# SETUP's feature step as SETUP runs it: -PassThru, counting warnings. Its
# host lines are kept in $script:said for the wording checks.
function Step([hashtable]$o){
    if(!$o){$o=$options}
    $out=@(& $helper @o -PassThru 6>&1)
    $script:said=(@($out|Where-Object{$_ -is [Management.Automation.InformationRecord]}|ForEach-Object{[string]$_.MessageData}) -join "`n")
    if($script:said){Write-Host $script:said}
    $rest=@($out|Where-Object{$_ -isnot [Management.Automation.InformationRecord]})
    if($rest.Count -ne 1){throw ('Feature step returned '+$rest.Count+' values instead of its warning count')}
    return [int]$rest[0]
}
function Quiet([string]$what){
    Assert ($script:said -notmatch '2-Enable-Beta|3-Capture-Test-Results|Restore-Previous-SEST|Prepare-PC|Capture-Repair-Results|README-FIRST|Disable-Beta-Test') ($what+' showed owner-toolkit instructions to a subscriber')
}
function Probe{
    $receiptNow=Get-Content -LiteralPath (J $cache 'payload' 'build-receipt.json') -Raw|ConvertFrom-Json
    Put (J $loader 'probe-ready.json') (@{format=1;token=(State).token;enabled=$false;native_sha256=$receiptNow.target_game_sha256;created_utc=[DateTime]::UtcNow.AddSeconds(1).ToString('o')}|ConvertTo-Json)
}
try {
    if($Candidate){
        # Lay out the package and the pack's beta-support folder from source.
        $Candidate=(Resolve-Path -LiteralPath $Candidate).ProviderPath
        $built=J $temp 'built-pack';$pkg=J $temp 'built-package'
        $src=J $repoRoot 'integration' 'beta-feature-parity'
        $candidateReceipt=Get-Content -LiteralPath (J $Candidate 'build-receipt.json') -Raw|ConvertFrom-Json
        foreach($n in @($candidateReceipt.files.PSObject.Properties.Name)+@('build-receipt.json')){Seed (J $Candidate $n) (J $pkg 'payload' $n)}
        Seed (J $src 'Install-SEST-Beta.ps1') (J $pkg 'Install-SEST-Beta.ps1')
        Seed (J $src 'Repair-SEST-Beta-Startup.ps1') (J $pkg 'Repair-SEST-Beta-Startup.ps1')
        Seed (J $repoRoot 'tools' 'capture-beta-references.ps1') (J $pkg 'capture-beta-references.ps1')
        $stableRuntimeSource=J $repoRoot 'integration' 'runtime-fixes' 'SEST.RuntimeFixes.dll'
        $stableUiSource=J $repoRoot 'integration' 'ui-followup' 'SEST.ContactsFix.dll'
        $refresh=[ordered]@{'SEST.RuntimeFixes.dll'=(Sha $stableRuntimeSource);'SEST.ContactsFix.dll'=(Sha $stableUiSource)}
        Put (J $pkg 'repair-receipt.json') (([ordered]@{format=1;base_files=$candidateReceipt.files;previous_files=@();workshop_refresh_files=$refresh})|ConvertTo-Json -Depth 6)
        Seed (J $repoRoot 'integration' 'campaign' 'setup' 'sest-workshop-features.ps1') (J $built 'sest-workshop-features.ps1')
        Seed $stableRuntimeSource (J $built 'plugins' 'SEST.RuntimeFixes.dll')
        Seed $stableUiSource (J $built 'plugins' 'SEST.ContactsFix.dll')
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zipPath=J $built 'beta-support' 'SEST-Beta-Features.zip'
        New-Item -ItemType Directory -Path (Split-Path -Parent $zipPath) -Force|Out-Null
        $zip=[IO.Compression.ZipFile]::Open($zipPath,'Create')
        $fileHashes=[ordered]@{}
        try{
            foreach($f in @(Get-ChildItem -LiteralPath $pkg -Recurse -File|Sort-Object FullName)){
                $name=$f.FullName.Substring($pkg.Length+1).Replace('\','/')
                [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$f.FullName,$name)
                $fileHashes[$name]=Sha $f.FullName
            }
        }finally{$zip.Dispose()}
        $bundle=[ordered]@{format=1;workshop_item_id='3812461539';revision=$candidateReceipt.candidate_revision;archive='SEST-Beta-Features.zip'
            archive_sha256=(Sha $zipPath);target_game_sha256=$candidateReceipt.target_game_sha256;target_game_label='0.8.7-261107'
            files=$fileHashes;features=@('World Operations','world service ribbons','Coordinated Strike styling and weapon estimates')}
        Put (J $built 'beta-support' 'manifest.json') ($bundle|ConvertTo-Json -Depth 6)
        $PublicPack=$built
    }
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
    $statePath=J $app 'BetaCompatibility' 'current.json';$optOut=J $app 'BetaCompatibility' 'features-off.json'
    $loader=J $game 'BepInEx' 'config' 'SEST-BetaAnchorChain';$flag=J $loader 'enable.flag'
    $bootstrap=J $game 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll'
    $manifest=Get-Content -LiteralPath (J $pack 'beta-support' 'manifest.json') -Raw|ConvertFrom-Json
    $cache=J $app 'WorkshopFeatures' $manifest.archive_sha256 'package'

    # Another game build, nothing installed: an accurate line, no files.
    Put $native 'OTHER GAME BUILD'
    Assert ((Step) -eq 0) 'Unsupported game with nothing installed gave a warning'
    Assert ($said -match 'this game build uses the Workshop item''s own SEST plugins' -and $said -notmatch 'remain selected') 'Unsupported build message is not accurate'
    Assert (!(Test-Path -LiteralPath $app)) 'Unsupported game wrote a feature cache'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime) 'Unsupported game replaced normal-release code'
    Seed (J $Capture 'references' 'managed' 'Seapower-Scripts.dll') $native
    # A refused archive is one warning, not a stop, and installs nothing.
    $archive=J $pack 'beta-support' 'SEST-Beta-Features.zip';$bytes=[IO.File]::ReadAllBytes($archive);Put $archive 'CHANGED'
    Assert ((Step) -eq 1) 'Altered Workshop archive was not one warning'
    Assert ($said -match 'differs from its manifest') 'Altered archive warning does not say why'
    Assert (!(Test-Path -LiteralPath $bootstrap)) 'Bad archive installed a bootstrap'
    [IO.File]::WriteAllBytes($archive,$bytes)
    $badOptions=@{}+$options;$badOptions.AppDataRoot=J $game 'bad-cache'
    Assert (Fails {& $helper @badOptions}) 'Feature cache inside game was accepted'
    # A changed author DLL before anything is installed: one warning naming it.
    $contactLog=J $ws '3819427362' 'ContactLog.dll';$contactLogBytes=[IO.File]::ReadAllBytes($contactLog);Put $contactLog 'AUTHOR UPDATE'
    Assert ((Step) -eq 1) 'Author DLL drift before install was not one warning'
    Assert ($said -match 'off until SEST is updated for Contact Log \(Workshop 3819427362\)') 'Author drift warning does not name the file'
    Assert (!(Test-Path -LiteralPath $bootstrap) -and !(Test-Path -LiteralPath $statePath)) 'Author drift staged files'
    [IO.File]::WriteAllBytes($contactLog,$contactLogBytes)

    Assert ((Step) -eq 0) 'First SETUP warned'
    Quiet 'Stage'
    $state=State;$token=$state.token;$backup=J $app 'BetaCompatibility' 'backups' $token
    Assert ($state.phase -eq 'staged') 'First SETUP did not stage the bundled features'
    Assert ($said -match 'staged, still inactive') 'Stage did not tell the player to launch once'
    Assert (!(Test-Path -LiteralPath $flag)) 'First SETUP bypassed the menu probe'
    Assert ((Get-Content -LiteralPath $settings -Raw) -ceq $before) 'Stage changed load order'
    Assert (Test-Path -LiteralPath $local) 'Stage moved Identify data before a probe'
    $receipt=Get-Content -LiteralPath (J $cache 'payload' 'build-receipt.json') -Raw|ConvertFrom-Json
    # Steam refreshes the item while staged: re-staged, not stuck.
    foreach($n in @('SEST.RuntimeFixes.dll','SEST.ContactsFix.dll')){Seed (J $PublicPack 'plugins' $n) (J $pack 'plugins' $n)}
    Remove-Item -LiteralPath (J $pack 'plugins' 'SEST.IdentifyDataPaths.dll')
    Assert ((Step) -eq 0) 'Steam refresh while staged was not handled'
    Quiet 'Re-stage'
    $state=State
    Assert ($state.phase -eq 'staged' -and $state.token -ne $token) 'Steam refresh while staged did not stage again'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $receipt.files.'SEST.RuntimeFixes.dll' -and (Test-Path -LiteralPath (J $pack 'plugins' 'SEST.IdentifyDataPaths.dll'))) 'Re-stage did not put the beta payload back'
    Assert ((Sha (J $app 'BetaCompatibility' 'backups' $state.token 'files' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime) 'Re-stage backed up something other than the normal plugin'
    Assert ($said -match 'staged again') 'Re-stage was not reported'
    # A probe left from before the re-stage does not switch it on.
    Put (J $loader 'probe-ready.json') (@{format=1;token=$token;enabled=$false;native_sha256=$receipt.target_game_sha256;created_utc=[DateTime]::UtcNow.AddSeconds(1).ToString('o')}|ConvertTo-Json)
    Assert ((Step) -eq 0 -and (State).phase -eq 'staged' -and $said -match 'still inactive') 'A probe of the earlier staging enabled the re-staged files'
    $token=$state.token;$backup=J $app 'BetaCompatibility' 'backups' $token
    Probe
    Assert ((Step) -eq 0) 'Second SETUP warned'
    Quiet 'Enable'
    Assert ((State).phase -eq 'enabled') 'Second SETUP did not enable features after the probe'
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
        Assert ((Step) -eq 1) 'Steam refresh copy failure was not one warning'
    } finally {Remove-Item -LiteralPath 'Function:\Copy-Item'}
    Assert $fault.Fired 'Steam refresh copy failure did not reach the code copy'
    Assert ($said -match 'Injected feature update failure') 'Copy failure warning lost its reason'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime -and (Sha (J $pack 'plugins' 'SEST.ContactsFix.dll')) -eq $stableUi) 'Failed Steam refresh did not restore the observed code'
    Assert (!(Test-Path -LiteralPath (J $pack 'plugins' 'SEST.IdentifyDataPaths.dll'))) 'Failed refresh left a newly added shim'
    Assert ((Get-Content -LiteralPath $statePath -Raw) -ceq $journal) 'Failed refresh altered the original journal'
    Assert ((Step) -eq 0) 'Steam refresh repair warned'
    Assert ($said -match 'Steam had put the normal plugins back') 'Steam refresh was not reported'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $receipt.files.'SEST.RuntimeFixes.dll') 'Steam refresh did not reapply bundled features'
    Assert ((State).token -eq $token) 'Steam refresh replaced the original journal token'
    Assert ((Sha (J $backup 'files' 'SEST.RuntimeFixes.dll')) -eq $backupHash) 'Steam refresh overwrote original backups'
    Put (J $pack 'plugins' 'SEST.RuntimeFixes.dll') 'UNREVIEWED CODE'
    Assert ((Step) -eq 1) 'Unreviewed runtime was not one warning'
    Assert ((Get-Content -LiteralPath (J $pack 'plugins' 'SEST.RuntimeFixes.dll') -Raw) -eq 'UNREVIEWED CODE') 'Rejected repair changed unreviewed code'
    Assert (!(Test-Path -LiteralPath $flag)) 'Rejected repair left the loader on'
    Seed (J $PublicPack 'plugins' 'SEST.RuntimeFixes.dll') (J $pack 'plugins' 'SEST.RuntimeFixes.dll')
    Seed (J $PublicPack 'plugins' 'SEST.ContactsFix.dll') (J $pack 'plugins' 'SEST.ContactsFix.dll')
    Assert ((Step) -eq 0 -and (Test-Path -LiteralPath $flag)) 'Repair after a refusal did not switch the features back on'

    # An author DLL update while enabled: features off, one warning naming it,
    # back on by itself once the reviewed file is back (SEST updated).
    Put $contactLog 'AUTHOR UPDATE'
    Assert ((Step) -eq 1) 'Author DLL drift while enabled was not one warning'
    Assert ($said -match 'off until SEST is updated for Contact Log' -and $said -notmatch 'Unexpected') 'Author drift while enabled was not named'
    Assert (!(Test-Path -LiteralPath $flag)) 'Author drift left the loader on'
    [IO.File]::WriteAllBytes($contactLog,$contactLogBytes)
    Assert ((Step) -eq 0 -and (Test-Path -LiteralPath $flag)) 'Reviewed author DLL back did not switch the features on'

    # Disable: SETUP leaves the features off until they are switched on again.
    & $helper @options -Action Disable | Out-Null
    Assert (!(Test-Path -LiteralPath $flag) -and (Test-Path -LiteralPath $optOut)) 'Disable did not switch off and record the choice'
    Assert ((Step) -eq 0) 'SETUP after Disable warned'
    Assert (!(Test-Path -LiteralPath $flag)) 'SETUP after Disable turned the beta code back on'
    Assert ($said -match 'switched off by you' -and $said -match 'turn on\.cmd') 'SETUP after Disable did not say how to switch on'
    foreach($n in @('SEST.RuntimeFixes.dll','SEST.ContactsFix.dll')){Seed (J $PublicPack 'plugins' $n) (J $pack 'plugins' $n)}
    Assert ((Step) -eq 0 -and !(Test-Path -LiteralPath $flag) -and (Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime) 'SETUP after Disable and a Steam refresh reapplied the beta code'
    & $helper @options -Action Enable | Out-Null
    Assert (!(Test-Path -LiteralPath $optOut)) 'Enable did not clear the choice'
    Assert ((Step) -eq 0 -and (Test-Path -LiteralPath $flag) -and (Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $receipt.files.'SEST.RuntimeFixes.dll') 'Re-enable on request did not switch the features on'
    # The reviewed toolkit's own Disable records the same choice.
    & (J $cache 'Repair-SEST-Beta-Startup.ps1') @options -Action Disable -Quiet | Out-Null
    Assert ((Test-Path -LiteralPath $optOut) -and (Step) -eq 0 -and !(Test-Path -LiteralPath $flag)) 'Toolkit Disable was undone by SETUP'
    & $helper @options -Action Enable | Out-Null
    Assert ((Step) -eq 0 -and (Test-Path -LiteralPath $flag)) 'Re-enable after toolkit Disable failed'

    # Another game build with the features enabled (the player went back to
    # the stable branch, or the game updated): the normal plugins come back,
    # SEST's beta files go, and no opt-out is recorded...
    Put $native 'OTHER GAME BUILD'
    Assert ((Step) -eq 0) 'Leaving the reviewed build warned'
    Assert ($said -match 'normal SEST plugins put back') 'Leaving the reviewed build was not reported'
    Assert ((State).phase -eq 'restored' -and !(Test-Path -LiteralPath $optOut)) 'Automatic restore recorded an opt-out'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime -and (Sha (J $pack 'plugins' 'SEST.ContactsFix.dll')) -eq $stableUi) 'Other build kept the beta plugins'
    Assert (!(Test-Path -LiteralPath $bootstrap) -and !(Test-Path -LiteralPath (J $pack 'plugins' 'SEST.IdentifyDataPaths.dll')) -and !(Test-Path -LiteralPath $flag)) 'Other build kept SEST beta files'
    Assert ((Get-Content -LiteralPath (J $local 'audio' 'broadcast' 'keep.mp3') -Raw) -eq 'AUDIO') 'Other build did not return local Identify data'
    Assert ((Step) -eq 0 -and $said -match 'own SEST plugins') 'Second SETUP on the other build was not quiet'
    # ...so back on the reviewed build SETUP installs the newest features again.
    Seed (J $Capture 'references' 'managed' 'Seapower-Scripts.dll') $native
    Assert ((Step) -eq 0 -and (State).phase -eq 'staged') 'Back on the reviewed build SETUP did not stage again'
    Probe
    Assert ((Step) -eq 0 -and (State).phase -eq 'enabled' -and (Test-Path -LiteralPath $flag)) 'Back on the reviewed build SETUP did not enable again'

    # Remove (explicit Restore): normal code back; SETUP does not stage again.
    & $helper @options -Action Restore | Out-Null
    Assert ((State).phase -eq 'restored' -and (Test-Path -LiteralPath $optOut)) 'Remove did not record the choice'
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime) 'Original runtime did not restore'
    Assert ((Get-Content -LiteralPath (J $local 'audio' 'broadcast' 'keep.mp3') -Raw) -eq 'AUDIO') 'Local Identify audio did not restore'
    $restoredToken=(State).token
    Assert ((Step) -eq 0) 'SETUP after Remove warned'
    Assert ((State).phase -eq 'restored' -and (State).token -eq $restoredToken -and !(Test-Path -LiteralPath $bootstrap)) 'SETUP after Remove staged the beta code again'
    Assert ($said -match 'removed by you') 'SETUP after Remove did not say why'
    & $helper @options -Action Enable | Out-Null
    Assert ((Step) -eq 0 -and (State).phase -eq 'staged' -and (State).token -ne $restoredToken) 'Re-enable after Remove did not stage again'

    if($PublishedUi){
        # Staged over the previously published UI; Steam then brings the
        # current normal-release UI. Restore keeps Steam's copy, not the older
        # backup, and a Stage afterwards accepts it as the normal plugin.
        $publishedUiHash=Sha $PublishedUi
        Assert ($publishedUiHash -ne $stableUi) 'The published UI is the current one'
        & $helper @options -Action Restore | Out-Null
        & $helper @options -Action Enable | Out-Null
        Seed $PublishedUi (J $pack 'plugins' 'SEST.ContactsFix.dll')
        Assert ((Step) -eq 0 -and (State).phase -eq 'staged') 'Stage over the published UI failed'
        Assert ((Sha (J $app 'BetaCompatibility' 'backups' (State).token 'files' 'SEST.ContactsFix.dll')) -eq $publishedUiHash) 'Stage did not back up the published UI'
        $publishedToken=(State).token
        foreach($n in @('SEST.RuntimeFixes.dll','SEST.ContactsFix.dll')){Seed (J $PublicPack 'plugins' $n) (J $pack 'plugins' $n)}
        & $helper @options -Action Restore | Out-Null
        Assert ((Sha (J $pack 'plugins' 'SEST.ContactsFix.dll')) -eq $stableUi) 'Restore replaced Steam''s current UI with the older backup'
        Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime -and !(Test-Path -LiteralPath $bootstrap)) 'Restore after the refresh left beta files'
        & $helper @options -Action Enable | Out-Null
        Seed $PublishedUi (J $pack 'plugins' 'SEST.ContactsFix.dll')
        Assert ((Step) -eq 0 -and (State).token -ne $publishedToken) 'Second stage over the published UI failed'
        $publishedToken=(State).token
        Seed (J $PublicPack 'plugins' 'SEST.ContactsFix.dll') (J $pack 'plugins' 'SEST.ContactsFix.dll')
        Seed (J $PublicPack 'plugins' 'SEST.RuntimeFixes.dll') (J $pack 'plugins' 'SEST.RuntimeFixes.dll')
        Assert ((Step) -eq 0 -and (State).phase -eq 'staged' -and (State).token -ne $publishedToken) 'Refresh to the current UI while staged was not re-staged'
        Assert ((Sha (J $app 'BetaCompatibility' 'backups' (State).token 'files' 'SEST.ContactsFix.dll')) -eq $stableUi) 'Re-stage did not back up Steam''s current UI'
    } else { Write-Host 'Published-UI refresh case not run (no -PublishedUi).' }

    & $helper @options -Action Restore | Out-Null
    Assert ((Sha (J $pack 'plugins' 'SEST.RuntimeFixes.dll')) -eq $stableRuntime) 'Original runtime did not restore'
    Assert ((Get-Content -LiteralPath $settings -Raw) -ceq $before) 'Original settings did not restore'
    Assert ((Get-Content -LiteralPath (J $player 'saves' 'world.save') -Raw) -eq 'NATIVE SAVE') 'Native save changed'
    Assert ((Get-Content -LiteralPath (J $pack 'missions' 'keep.ini') -Raw) -eq 'MISSION') 'Campaign data changed'
    foreach($file in $frozen.Keys){Assert ((Sha $file) -eq $frozen[$file]) ('Native/author file changed: '+$file)}
    Assert (@(Get-ChildItem -LiteralPath (J $pack 'beta-support') -Recurse -Filter '*.dll').Count -eq 0) 'Archive leaked active duplicate DLLs into Workshop'
    Write-Host "Workshop-included feature fixture passed: $checks assertions; no Unity gameplay."
} finally {if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp -Recurse -Force}}
