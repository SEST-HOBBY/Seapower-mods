#Requires -Version 5.1
<# The pack's beta feature step. SETUP (sest-setup.ps1) runs it after the mod
   order is written, and the three "SEST beta features" launchers at the pack
   root run it through SETUP. The feature archive stays inert in the Workshop
   item: it is extracted to the player's SEST cache, and its own installer
   (staged, probed, journalled, every change backed up first) makes each code
   change. Nothing here loosens a hash check.

   -Action Setup, for whichever game build is installed:
     * the build the bundle was reviewed for: installs or updates the bundled
       features, unless the player switched them off (features-off.json);
     * any other build: if SEST's beta files are installed, puts the normal
       SEST plugins back from the restore journal (no opt-out is recorded, so
       the features return once the game is on the reviewed build again);
       otherwise says that the Workshop item's own plugins are in use.
     A refusal (a pinned game or author file changed, Steam still downloading
     the item) is one [!!] warning, nothing is forced, and SETUP finishes.
   -Action Disable  SEST's beta loader off; SETUP leaves the features off.
   -Action Restore  the normal SEST code back and SEST's beta files removed,
                    from the restore journal; SETUP leaves the features off.
   -Action Enable   clears that choice; the next Setup installs them again.
   -Action Collect  the reviewed capture of references and logs.
   -PassThru        ends with the number of [!!] warnings (SETUP counts them). #>
[CmdletBinding()]
param(
    [ValidateSet('Setup','Collect','Restore','Disable','Enable')][string]$Action='Setup',
    [string]$GameRoot='', [string]$WorkshopContentRoot='',
    [string]$PlayerDataRoot='', [string]$AppDataRoot='', [string]$OutDirectory='',
    [switch]$PassThru
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Sha([string]$p){if(Test-Path -LiteralPath $p -PathType Leaf){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}else{''}}
function Say([string]$t,[string]$c='Gray'){Write-Host $t -ForegroundColor $c}
$script:warnings=0
function Warn([string]$t,[string[]]$more=@()){
    $script:warnings++
    Say ('  [!!]   '+$t) 'Yellow'
    foreach($m in $more){if($m){Say ('         '+$m) 'Yellow'}}
}
function Read-Json([string]$p){if(Test-Path -LiteralPath $p -PathType Leaf){Get-Content -LiteralPath $p -Raw | ConvertFrom-Json}else{$null}}
function Write-Text([string]$p,[string]$t){
    New-Item -ItemType Directory -Path (Split-Path -Parent $p) -Force | Out-Null
    $tmp=$p+'.sest-'+[guid]::NewGuid().ToString('N')
    try{[IO.File]::WriteAllText($tmp,$t,(New-Object Text.UTF8Encoding($false)));Move-Item -LiteralPath $tmp -Destination $p -Force}
    finally{if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Force}}
}
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
$stateRoot=J $AppDataRoot 'BetaCompatibility'
$statePath=J $stateRoot 'current.json'
# The player's "beta features off" choice, written by Disable and Restore here
# and by the reviewed installer's own Disable/Restore. It lives outside the
# game and Workshop folders, so a Steam update of the item cannot undo it.
$optOutPath=J $stateRoot 'features-off.json'
$loaderRoot=J $GameRoot 'BepInEx' 'config' 'SEST-BetaAnchorChain'
$flag=J $loaderRoot 'enable.flag'
$plugins=J $WorkshopContentRoot '3812461539' 'plugins'
$native=J $GameRoot 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll'
$bundleRoot=J $PSScriptRoot 'beta-support'
$options=@{GameRoot=$GameRoot;WorkshopContentRoot=$WorkshopContentRoot;PlayerDataRoot=$PlayerDataRoot;AppDataRoot=$AppDataRoot}
function Set-OptOut([string]$why){Write-Text $optOutPath (([ordered]@{format=1;action=$why;created_utc=[DateTime]::UtcNow.ToString('o')}) | ConvertTo-Json)}
function Get-Manifest {
    $m=Read-Json (J $bundleRoot 'manifest.json')
    if(!$m -or $m.format -ne 1 -or $m.workshop_item_id -ne '3812461539' -or $m.archive -cne 'SEST-Beta-Features.zip' -or
       $m.archive_sha256 -notmatch '^[a-f0-9]{64}$' -or [string]$m.target_game_sha256 -notmatch '^[a-f0-9]{64}$'){throw 'Unrecognised Workshop feature bundle.'}
    return $m
}
function Target-Label($m){
    if($m.PSObject.Properties['target_game_label'] -and $m.target_game_label){return [string]$m.target_game_label}
    return ('the reviewed beta (Seapower-Scripts '+([string]$m.target_game_sha256).Substring(0,8)+')')
}
# Verify the pinned archive, check every entry name, and extract it once into
# the player's cache keyed by the archive's SHA-256. Returns the package folder.
function Open-Package($m){
    $archive=J $bundleRoot $m.archive
    if((Sha $archive) -ne $m.archive_sha256){throw 'the Workshop copy of the feature archive differs from its manifest (Steam may still be downloading the item)'}
    $cache=J $AppDataRoot 'WorkshopFeatures' $m.archive_sha256
    $package=J $cache 'package'
    $prefix=[IO.Path]::GetFullPath($package).TrimEnd([char[]]'\/')+[IO.Path]::DirectorySeparatorChar
    $expected=@($m.files.PSObject.Properties).Count
    $check={param([string]$root)
        if(!(Test-Path -LiteralPath $root -PathType Container)){return $false}
        if((Get-Item -LiteralPath $root -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked feature cache refused.'}
        $actual=@(Get-ChildItem -LiteralPath $root -Recurse -Force -File)
        if($actual.Count -ne $expected){return $false}
        foreach($entry in $m.files.PSObject.Properties){
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
            # ExternalAttributes exists from .NET Framework 4.7.2; older
            # frameworks never extract an entry as a link, so it is read only
            # where it exists.
            $link=$false
            if($entry.PSObject.Properties['ExternalAttributes']){$link=((($entry.ExternalAttributes -shr 16) -band 61440) -eq 40960)}
            if(!$name -or $name -match '(^|/)\.\.(/|$)|^/|:|\x00' -or $name.EndsWith('/') -or
               !$seen.Add($name) -or !$m.files.PSObject.Properties[$name] -or $link){throw 'Unsafe or unexpected feature archive entry.'}
            if(![IO.Path]::GetFullPath((J $package $name)).StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Feature entry escapes its cache.'}
        }
        if($seen.Count -ne $expected){throw 'Feature archive entry count differs.'}
    } finally {$zip.Dispose()}
    if(!(& $check $package)){
        New-Item -ItemType Directory -Path $cache -Force | Out-Null
        if(Test-Path -LiteralPath $package){Move-Item -LiteralPath $package -Destination ($package+'.kept-'+[guid]::NewGuid().ToString('N'))}
        $temporary=$package+'.extract-'+[guid]::NewGuid().ToString('N')
        [IO.Compression.ZipFile]::ExtractToDirectory($archive,$temporary)
        if(!(& $check $temporary)){throw 'Extracted feature files failed verification.'}
        Move-Item -LiteralPath $temporary -Destination $package
    }
    return $package
}
# The files the reviewed installer pins (its Check-External list), named for
# players. Read-only: it only lets the warning name what changed.
function Changed-References($receipt){
    $refs=[ordered]@{
        'Seapower-Scripts.dll'=@((J $GameRoot 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll'),'the game (Seapower-Scripts.dll)')
        'Noesis.NoesisGUI.dll'=@((J $GameRoot 'Sea Power_Data' 'Managed' 'Noesis.NoesisGUI.dll'),'the game (Noesis.NoesisGUI.dll)')
        'UnityEngine.CoreModule.dll'=@((J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.CoreModule.dll'),'the game (UnityEngine.CoreModule.dll)')
        'UnityEngine.InputLegacyModule.dll'=@((J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.InputLegacyModule.dll'),'the game (UnityEngine.InputLegacyModule.dll)')
        'UnityEngine.IMGUIModule.dll'=@((J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.IMGUIModule.dll'),'the game (UnityEngine.IMGUIModule.dll)')
        'BepInEx.dll'=@((J $GameRoot 'BepInEx' 'core' 'BepInEx.dll'),'BepInEx (BepInEx\core\BepInEx.dll)')
        'Mono.Cecil.dll'=@((J $GameRoot 'BepInEx' 'core' 'Mono.Cecil.dll'),'BepInEx (BepInEx\core\Mono.Cecil.dll)')
        '0Harmony.dll'=@((J $GameRoot 'BepInEx' 'core' '0Harmony.dll'),'BepInEx (BepInEx\core\0Harmony.dll)')
        'AnchorChain.Preloader.dll'=@((J $GameRoot 'BepInEx' 'plugins' 'AnchorChain.Preloader.dll'),'the Anchor Chain preloader (BepInEx\plugins\AnchorChain.Preloader.dll)')
        'AnchorChain.dll'=@((J $WorkshopContentRoot '3380210757' 'AnchorChain.dll'),'Anchor Chain (Workshop 3380210757)')
        'IdentifyExpanded.dll'=@((J $WorkshopContentRoot '3790594162' 'IdentifyExpanded.dll'),'Identify Expanded (Workshop 3790594162)')
        'CombatCosts.dll'=@((J $WorkshopContentRoot '3807187341' 'CombatCosts.dll'),'Combat Cost Tracker (Workshop 3807187341)')
        'ContactLog.dll'=@((J $WorkshopContentRoot '3819427362' 'ContactLog.dll'),'Contact Log (Workshop 3819427362)')
        'SeaPowerSquadPanel.dll'=@((J $WorkshopContentRoot '3818251045' 'SeaPowerSquadPanel.dll'),'Group Manager (Workshop 3818251045)')
        'SeaPowerPopOut.dll'=@((J $WorkshopContentRoot '3826396311' 'SeaPowerPopOut.dll'),'Pop-Out Windows (Workshop 3826396311)')
    }
    $changed=@()
    foreach($p in $receipt.captured_references.PSObject.Properties){
        if($refs.Contains($p.Name) -and (Sha $refs[$p.Name][0]) -ne [string]$p.Value){$changed+=$refs[$p.Name][1]}
    }
    return ,$changed
}
function Report-Refusal($changed,$err){
    if(@($changed).Count){
        Warn ('SEST beta features are off until SEST is updated for '+(@($changed) -join ', ')+'.') @(
            'That file differs from the one the features were reviewed against, so nothing is forced onto it.',
            'On this beta build Workshop code mods load only through SEST''s beta loader, so they stay off too; data mods and campaigns are unaffected.',
            'Run SETUP again after the SEST pack updates. The rest of SETUP is done.')
    } else {
        Warn ('SEST beta features were not installed or updated: '+$err.Exception.Message) @('Nothing was forced, and the rest of SETUP is done. Keep this message for review.')
    }
}
function Off-Hint{Say '         Turn them on again with "SEST beta features - turn on.cmd" in the pack folder (game closed).'}

function Invoke-Step {
    if($Action -eq 'Disable'){
        $was='were already off'
        if(Test-Path -LiteralPath $flag){Move-Item -LiteralPath $flag -Destination ($flag+'.disabled') -Force;$was='are now off'}
        Set-OptOut 'Disable'
        Say ('  [done] SEST beta features '+$was+'; SETUP leaves them off. Game branch, saves and data are unchanged.') 'Green'
        Off-Hint
        return
    }
    if($Action -eq 'Enable'){
        if(Test-Path -LiteralPath $optOutPath){Remove-Item -LiteralPath $optOutPath -Force;Say '  [done] SEST beta features switched back on: SETUP installs them on the game build they were reviewed for.' 'Green'}
        else{Say '  [ok]   SEST beta features were not switched off.' 'Green'}
        return
    }
    $manifest=Get-Manifest
    $state=Read-Json $statePath
    $phase=''; if($state){$phase=[string]$state.phase}
    if($Action -eq 'Collect'){
        $package=Open-Package $manifest
        $collect=@{}+$options; if($OutDirectory){$collect.OutDirectory=$OutDirectory}
        & (J $package 'Repair-SEST-Beta-Startup.ps1') @collect -Action Collect
        return
    }
    if($Action -eq 'Restore'){
        if(!$state){
            Set-OptOut 'Restore'
            Say '  [ok]   SEST beta files are not installed (no restore journal); SETUP will not install them.' 'Green'
            Off-Hint
            return
        }
        $package=Open-Package $manifest
        & (J $package 'Repair-SEST-Beta-Startup.ps1') @options -Action Restore -Quiet | Out-Null
        Set-OptOut 'Restore'
        Say '  [done] Normal SEST code put back and SEST''s beta files removed; SETUP leaves them off.' 'Green'
        Say ('         Backups kept in '+(J $stateRoot 'backups' ([string]$state.token)))
        Off-Hint
        return
    }

    # ---- Setup -------------------------------------------------------------
    $label=Target-Label $manifest
    if((Sha $native) -ne $manifest.target_game_sha256){
        if($phase -in @('staged','enabled')){
            # Beta files from SEST are installed but do nothing on this build:
            # put the normal plugins back through the journal, keeping no opt-out.
            try {
                $package=Open-Package $manifest
                & (J $package 'Repair-SEST-Beta-Startup.ps1') @options -Action Restore -Quiet -Automatic | Out-Null
                Say ('  [done] beta features: this game build is not '+$label+', the build they were reviewed for, so SEST''s beta files were removed and the normal SEST plugins put back.') 'Green'
                Say ('         Backups kept in '+(J $stateRoot 'backups' ([string]$state.token))+'. SETUP installs the features again when the game is on that build.')
            } catch {
                Warn ('SEST''s beta files are installed for another game build, and SETUP could not put the normal plugins back: '+$_.Exception.Message) @(
                    'The beta plugins do nothing on this build. With the game closed, run "SEST beta features - remove.cmd" in the pack folder; if that stops too, keep both messages for review.')
            }
        } elseif($phase -and $phase -ne 'restored'){
            Warn 'An incomplete SEST feature-install journal exists; nothing was changed.' @('Keep '+$statePath+' for review.')
        } else {
            $betaRuntime=''
            if($manifest.files.PSObject.Properties['payload/SEST.RuntimeFixes.dll']){$betaRuntime=[string]$manifest.files.'payload/SEST.RuntimeFixes.dll'}
            if($betaRuntime -and (Sha (J $plugins 'SEST.RuntimeFixes.dll')) -eq $betaRuntime){
                Warn ('The beta SEST plugins are in '+$plugins+', but no SEST restore journal was found, so SETUP cannot put the normal ones back.') @('They do nothing on this build. Steam puts the normal plugins back when it next updates the item.')
            } else {
                Say ('  [ok]   beta features: for '+$label+' only; this game build uses the Workshop item''s own SEST plugins (no beta files installed)') 'Green'
            }
        }
        return
    }
    if(Test-Path -LiteralPath $optOutPath){
        # Any marker is the player's choice; its details only word the line.
        $how='switched off'; $when=''
        try{
            $optOut=Read-Json $optOutPath
            if([string]$optOut.action -eq 'Restore'){$how='removed'}
            $when=' on '+([DateTime]::Parse([string]$optOut.created_utc).ToLocalTime().ToString('d MMM yyyy'))
        }catch{}
        Say ('  [ok]   SEST beta features: '+$how+' by you'+$when+'; SETUP leaves them off.') 'Green'
        Off-Hint
        return
    }
    if(!(Test-Path -LiteralPath (J $plugins 'SEST.RuntimeFixes.dll'))){
        Warn 'SEST beta features install only into the subscribed Workshop item 3812461539, which is not downloaded here.'
        return
    }
    try {$package=Open-Package $manifest}
    catch {Warn ('SEST beta features were not installed or updated: '+$_.Exception.Message+'.') @('Let Steam finish downloading the item, then run SETUP again. The rest of SETUP is done.');return}
    $receipt=Read-Json (J $package 'payload' 'build-receipt.json')
    $changed=Changed-References $receipt
    $installer=J $package 'Install-SEST-Beta.ps1'
    $repair=J $package 'Repair-SEST-Beta-Startup.ps1'
    $features=@($manifest.features) -join ', '
    if($phase -eq 'enabled'){
        $journalRuntime=''
        foreach($entry in @($state.files)){if($entry.name -eq 'SEST.RuntimeFixes.dll'){$journalRuntime=[string]$entry.installed_sha256}}
        $refreshed=(Sha (J $plugins 'SEST.RuntimeFixes.dll')) -ne $journalRuntime
        # Repair switches the loader off first and on again only after every
        # check and copy verifies, so a refusal leaves the features off.
        try {& $repair @options -Action Repair -Quiet | Out-Null}
        catch {Report-Refusal $changed $_;return}
        Say ('  [done] SEST beta features on and up to date ('+$receipt.candidate_revision+'): '+$features) 'Green'
        if($refreshed){Say '         Steam had put the normal plugins back with the item update; the beta plugins were applied again (original backups kept).'}
        return
    }
    if($phase -and $phase -notin @('staged','restored')){
        Warn 'An incomplete SEST feature-install journal exists; nothing was changed.' @('Keep '+$statePath+' for review.')
        return
    }
    # The installer refuses changed references before it changes anything.
    if(@($changed).Count){Report-Refusal $changed $null;return}
    $tokenBefore=''; if($state){$tokenBefore=[string]$state.token}
    try {& $installer @options -Action Stage -Quiet | Out-Null}
    catch {Report-Refusal $changed $_;return}
    $state=Read-Json $statePath
    if($phase -eq 'staged' -and $tokenBefore -and [string]$state.token -ne $tokenBefore){
        Say '  [done] Steam updated the pack while the beta features were staged; they were staged again from the restore journal.' 'Green'
    }
    # Enable only after a menu probe of this staging (the bootstrap writes it at
    # the next launch); the installer checks the probe again before enabling.
    $probed=$false
    try{
        $probe=Read-Json (J $loaderRoot 'probe-ready.json')
        $probed=[bool]($probe -and [string]$probe.token -eq [string]$state.token -and [string]$probe.native_sha256 -eq $manifest.target_game_sha256 -and $probe.enabled -eq $false)
    }catch{$probed=$false}
    if(!$probed){
        Say '  [done] SEST beta features staged, still inactive. Start Sea Power to the main menu, wait about 10 seconds, quit, then run SETUP again to switch them on.' 'Cyan'
        return
    }
    try {& $installer @options -Action Enable -Quiet | Out-Null}
    catch {Report-Refusal $changed $_;return}
    Say ('  [done] SEST beta features switched on ('+$receipt.candidate_revision+'): '+$features) 'Green'
    $state=Read-Json $statePath
    if($state.local_migration_started){Say ('         Your local Identify Expanded data was moved to '+(J $AppDataRoot 'IdentifyExpanded')+' and is read from there; its Workshop copy stays enabled.')}
}
Invoke-Step
if($PassThru){$script:warnings}
