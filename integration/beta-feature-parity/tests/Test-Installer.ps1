[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Capture, [Parameter(Mandatory=$true)][string]$Candidate,
      [string]$RepairPackage = '', [string]$PreviousPackage = '')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$source = Split-Path -Parent $PSScriptRoot
$temp = Join-Path ([IO.Path]::GetTempPath()) ('SEST-Beta-Installer-Test-' + [guid]::NewGuid().ToString('N'))
$checks = 0
function J { $p = [string]$args[0]; for ($i=1; $i -lt $args.Count; $i++) { $p = [IO.Path]::Combine($p,[string]$args[$i]) }; return $p }
function Assert([bool]$Ok, [string]$Why) { if (!$Ok) { throw $Why }; $script:checks++ }
function Hash([string]$Path) { if (Test-Path -LiteralPath $Path -PathType Leaf) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }; return '' }
function Put([string]$Path, [string]$Text) { New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null; [IO.File]::WriteAllText($Path,$Text) }
function Seed-File([string]$From, [string]$To) { New-Item -ItemType Directory -Path (Split-Path -Parent $To) -Force | Out-Null; Copy-Item -LiteralPath $From -Destination $To -Force }
try {
    $package = J $temp 'package'; $installer = J $package 'Install-SEST-Beta.ps1'
    Seed-File (J $source 'Install-SEST-Beta.ps1') $installer
    if ($PreviousPackage) {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip=[IO.Compression.ZipFile]::OpenRead($PreviousPackage)
        try {
            $entry=$zip.GetEntry('Install-SEST-Beta.ps1')
            $reader=New-Object IO.StreamReader($entry.Open())
            try { [IO.File]::WriteAllText($installer,$reader.ReadToEnd()) } finally { $reader.Dispose() }
        } finally { $zip.Dispose() }
    }
    $receipt = Get-Content -LiteralPath (J $Candidate 'build-receipt.json') -Raw | ConvertFrom-Json
    foreach ($file in @($receipt.files.PSObject.Properties.Name) + @('build-receipt.json')) { Seed-File (J $Candidate $file) (J $package 'payload' $file) }
    $game = J $temp 'steamapps' 'common' 'Sea Power'
    $workshop = J $temp 'steamapps' 'workshop' 'content' '1286220'
    foreach ($name in @('Seapower-Scripts.dll', 'Noesis.NoesisGUI.dll', 'UnityEngine.CoreModule.dll', 'UnityEngine.InputLegacyModule.dll', 'UnityEngine.IMGUIModule.dll')) { Seed-File (J $Capture 'references' 'managed' $name) (J $game 'Sea Power_Data' 'Managed' $name) }
    Seed-File (J $Capture 'references' 'bepinex' 'core' '0Harmony.dll') (J $game 'BepInEx' 'core' '0Harmony.dll')
    Seed-File (J $Capture 'references' 'bepinex' 'core' 'BepInEx.dll') (J $game 'BepInEx' 'core' 'BepInEx.dll')
    Seed-File (J $Capture 'references' 'bepinex' 'core' 'Mono.Cecil.dll') (J $game 'BepInEx' 'core' 'Mono.Cecil.dll')
    Seed-File (J $Capture 'references' 'bepinex' 'plugins' 'AnchorChain.Preloader.dll') (J $game 'BepInEx' 'plugins' 'AnchorChain.Preloader.dll')
    $ids = [ordered]@{
        '3380210757' = 'AnchorChain.dll'; '3790594162' = 'IdentifyExpanded.dll'; '3807187341' = 'CombatCosts.dll'
        '3819427362' = 'ContactLog.dll'; '3818251045' = 'SeaPowerSquadPanel.dll'; '3826396311' = 'SeaPowerPopOut.dll'
    }
    foreach ($id in $ids.Keys) { Seed-File (J $Capture 'references' 'workshop' 'library-1' $id $ids[$id]) (J $workshop $id $ids[$id]) }
    $plugins = J $workshop '3812461539' 'plugins'
    foreach ($name in @('SEST.RuntimeFixes.dll', 'SEST.ContactsFix.dll')) { Seed-File (J $Capture 'references' 'workshop' 'library-1' '3812461539' 'plugins' $name) (J $plugins $name) }
    $mission = J $workshop '3812461539' 'missions' 'test.ini'; Put $mission 'MISSION DATA MUST STAY'
    $saves = J $temp 'player' 'saves' 'campaign.sav'; Put $saves 'SAVE MUST STAY'
    $settings = J $temp 'player' 'usersettings.ini'
    $oldText = "[Options]`r`nMusic=0.5`r`n[LoadOrder]`r`nNumberOfModFiles=6`r`nMod1Directory=3812461539,True`r`nMod2Directory=3380210757,True`r`nMod3Directory=3790594162,True`r`nMod4Directory=IdentifyExpanded,False`r`nMod5Directory=BrandNewMod,False`r`nMod6Directory=ACConfigs,False`r`n[Other]`r`nValue=untouched`r`n"
    Put $settings $oldText
    $local = J $game 'Sea Power_Data' 'StreamingAssets' 'IdentifyExpanded'
    $localAudio = J $local 'audio' 'broadcast' 'track.mp3'; Put $localAudio 'LOCAL AUDIO'
    Put (J $local '_info.ini') '[Language_en]'
    $appRoot = J $temp 'app-data' 'SEST'
    $redirected = J $appRoot 'IdentifyExpanded' 'audio' 'broadcast' 'track.mp3'; Put $redirected 'OLDER REDIRECTED AUDIO'
    $options = @{ GameRoot = $game; WorkshopContentRoot = $workshop; PlayerDataRoot = (J $temp 'player'); AppDataRoot = $appRoot }
    $frozen = @{}
    foreach ($path in @((J $game 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll'), (J $game 'Sea Power_Data' 'Managed' 'Noesis.NoesisGUI.dll'), (J $game 'BepInEx' 'plugins' 'AnchorChain.Preloader.dll'), $mission, $saves)) { $frozen[$path] = Hash $path }
    foreach ($id in $ids.Keys) { $path = J $workshop $id $ids[$id]; $frozen[$path] = Hash $path }
    foreach ($name in @('UnityEngine.CoreModule.dll', 'UnityEngine.InputLegacyModule.dll', 'UnityEngine.IMGUIModule.dll')) { $path = J $game 'Sea Power_Data' 'Managed' $name; $frozen[$path] = Hash $path }
    $bep = J $game 'BepInEx' 'core' 'BepInEx.dll'; $frozen[$bep] = Hash $bep
    $originalRuntime = Hash (J $plugins 'SEST.RuntimeFixes.dll')
    $originalUi = Hash (J $plugins 'SEST.ContactsFix.dll')
    & $installer @options -Action Stage
    $stateFile = J $appRoot 'BetaCompatibility' 'current.json'
    $state = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
    $backup = J $appRoot 'BetaCompatibility' 'backups' $state.token
    $loader = J $game 'BepInEx' 'config' 'SEST-BetaAnchorChain'
    Assert ($state.phase -eq 'staged') 'Stage did not complete'
    Assert (!(Test-Path -LiteralPath (J $loader 'enable.flag'))) 'Stage activated the loader'
    Assert ((Hash (J $plugins 'SEST.RuntimeFixes.dll')) -eq $receipt.files.PSObject.Properties['SEST.RuntimeFixes.dll'].Value) 'Runtime payload mismatch'
    Assert ((Hash (J $backup 'files' 'SEST.RuntimeFixes.dll')) -eq $originalRuntime) 'Runtime backup mismatch'
    Assert ((Hash (J $backup 'files' 'SEST.ContactsFix.dll')) -eq $originalUi) 'UI backup mismatch'
    Assert ([IO.File]::ReadAllText($settings) -ceq $oldText) 'Stage changed load order'
    Assert (Test-Path -LiteralPath $localAudio) 'Stage moved local data before the probe'
    $blocked = $false; try { & $installer @options -Action Enable } catch { $blocked = $_.Exception.Message -match 'successful menu probe' }
    Assert $blocked 'Enable did not require a probe'
    $proof = [ordered]@{ format=1; token=('0' * 32); enabled=$false; native_sha256=$receipt.target_game_sha256; created_utc=[DateTime]::UtcNow.ToString('o') }
    Put (J $loader 'probe-ready.json') ($proof | ConvertTo-Json)
    $blocked = $false; try { & $installer @options -Action Enable } catch { $blocked = $_.Exception.Message -match 'does not match' }
    Assert $blocked 'An unrelated probe was accepted'
    $proof.token = $state.token; Put (J $loader 'probe-ready.json') ($proof | ConvertTo-Json)
    & $installer @options -Action Enable
    $state = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
    Assert ($state.phase -eq 'enabled') 'Enable did not complete'
    Assert ([IO.File]::ReadAllText((J $loader 'enable.flag')) -eq 'enable-beta-261026') 'Enable flag mismatch'
    Assert (!(Test-Path -LiteralPath $local)) 'Local Identify folder remains discoverable'
    Assert ([IO.File]::ReadAllText($redirected) -eq 'LOCAL AUDIO') 'Local audio was not migrated'
    Assert ([IO.File]::ReadAllText((J $backup 'IdentifyExpanded-previous-data' 'audio' 'broadcast' 'track.mp3')) -eq 'OLDER REDIRECTED AUDIO') 'Conflicting pre-existing redirected data was lost'
    Assert ([IO.File]::ReadAllText((J $backup 'IdentifyExpanded-local' 'audio' 'broadcast' 'track.mp3')) -eq 'LOCAL AUDIO') 'Local audio backup is missing'
    $newText = [IO.File]::ReadAllText($settings)
    Assert ($newText -match 'NumberOfModFiles=5' -and $newText -notmatch 'Directory=IdentifyExpanded,') 'Local load-order row was not removed'
    Assert ($newText -match '3790594162,True' -and $newText -match 'BrandNewMod,False' -and $newText -match 'Value=untouched') 'Workshop order, flags or other settings changed'
    & $installer @options -Action Stage
    $same = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
    Assert ($same.token -eq $state.token) 'Staging the enabled candidate was not idempotent'
    if ($RepairPackage) {
        $repairScript=J $RepairPackage 'Repair-SEST-Beta-Startup.ps1'
        $newReceipt=Get-Content -LiteralPath (J $RepairPackage 'payload' 'build-receipt.json') -Raw | ConvertFrom-Json
        # A repair replaces every candidate file; the shim is copied last, so a
        # failure there must roll the four earlier copies back.
        $codePaths=[ordered]@{
            'AnchorChain.dll'=(J $loader 'AnchorChain.dll')
            'SEST.BetaSafeBootstrap.dll'=(J $game 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll')
            'SEST.RuntimeFixes.dll'=(J $plugins 'SEST.RuntimeFixes.dll')
            'SEST.ContactsFix.dll'=(J $plugins 'SEST.ContactsFix.dll')
            'SEST.IdentifyDataPaths.dll'=(J $plugins 'SEST.IdentifyDataPaths.dll')
        }
        $beforeRepair=@{}
        foreach ($name in $codePaths.Keys) { $beforeRepair[$name]=Hash $codePaths[$name] }
        $fault=[pscustomobject]@{ Fired=$false; PayloadPath=(J $RepairPackage 'payload' 'SEST.IdentifyDataPaths.dll') }
        try {
            function Copy-Item {
                [CmdletBinding()]param([string]$LiteralPath,[string]$Destination,[switch]$Force)
                if (!$fault.Fired -and $LiteralPath -eq $fault.PayloadPath) { $fault.Fired=$true; throw 'Synthetic repair-copy failure' }
                Microsoft.PowerShell.Management\Copy-Item @PSBoundParameters
            }
            $blocked=$false
            try { & $repairScript @options } catch { $blocked=$_.Exception.Message -match 'Synthetic repair-copy failure' }
            Assert ($blocked -and $fault.Fired) 'Repair failure was not injected'
        } finally { Remove-Item -LiteralPath 'Function:\Copy-Item' }
        foreach ($name in $codePaths.Keys) { Assert ((Hash $codePaths[$name]) -eq $beforeRepair[$name]) "Failed repair did not restore $name" }
        Assert (!(Test-Path -LiteralPath (J $loader 'enable.flag'))) 'Failed repair reactivated the crashing setup'
        & $repairScript @options
        $repaired=Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
        foreach ($name in $codePaths.Keys) {
            Assert ((Hash $codePaths[$name]) -eq $newReceipt.files.PSObject.Properties[$name].Value) "Repaired file hash mismatch: $name"
            Assert (@($repaired.files | Where-Object { $_.name -eq $name -and $_.installed_sha256 -eq $newReceipt.files.PSObject.Properties[$name].Value }).Count -eq 1) "Restore journal does not recognize the repaired $name"
        }
        Assert ([IO.File]::ReadAllText((J $loader 'AnchorChain.sha256')) -eq $newReceipt.files.PSObject.Properties['AnchorChain.dll'].Value) 'Loader hash file was not updated'
        Assert ($repaired.token -eq $state.token -and $repaired.files.Count -eq $state.files.Count) 'Repair replaced the original restore journal'
        Assert ([IO.File]::ReadAllText($settings) -ceq $newText -and !(Test-Path -LiteralPath $local)) 'Repair changed settings or recreated Local Identify'
        & $repairScript @options
        $again=Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
        Assert ($again.token -eq $state.token) 'Repeated repair replaced the original journal token'
        Assert ((Hash (J $backup 'files' 'SEST.RuntimeFixes.dll')) -eq $originalRuntime) 'Repair overwrote the original backup'
        Put (J $loader 'AnchorChain.dll') 'UNREVIEWED INSTALLED LOADER'
        $blocked=$false
        try { & $repairScript @options } catch { $blocked=$_.Exception.Message -match 'not a reviewed beta candidate' }
        Assert $blocked 'Repair accepted unknown installed code'
        Assert (!(Test-Path -LiteralPath (J $loader 'enable.flag'))) 'Rejected repair left activation enabled'
        Assert ([IO.File]::ReadAllText((J $loader 'AnchorChain.dll')) -eq 'UNREVIEWED INSTALLED LOADER') 'Rejected repair overwrote unknown code'
        Seed-File (J $RepairPackage 'payload' 'AnchorChain.dll') (J $loader 'AnchorChain.dll')
        & $repairScript @options
    }
    $newAudio = J $appRoot 'IdentifyExpanded' 'audio' 'broadcast' 'created-during-test.mp3'; Put $newAudio 'NEW AUDIO'
    & $installer @options -Action Restore
    Assert ((Hash (J $plugins 'SEST.RuntimeFixes.dll')) -eq $originalRuntime) 'Runtime was not restored'
    Assert ((Hash (J $plugins 'SEST.ContactsFix.dll')) -eq $originalUi) 'UI was not restored'
    Assert (!(Test-Path -LiteralPath (J $plugins 'SEST.IdentifyDataPaths.dll'))) 'Added path shim was not removed'
    Assert (!(Test-Path -LiteralPath (J $game 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll'))) 'Added bootstrap was not removed'
    Assert ([IO.File]::ReadAllText($settings) -ceq $oldText) 'Unchanged settings did not restore byte for byte'
    Assert ([IO.File]::ReadAllText($localAudio) -eq 'LOCAL AUDIO') 'Local audio was not restored'
    Assert ([IO.File]::ReadAllText($newAudio) -eq 'NEW AUDIO') 'New redirected data was deleted during restore'
    foreach ($path in $frozen.Keys) { Assert ((Hash $path) -eq $frozen[$path]) ('Native/author/content/save file changed: ' + $path) }
    # Fail the second code copy after the first was installed. The actual
    # rollback path must restore the pair and remove partially added files.
    $fault = [pscustomobject]@{ Fired = $false; PayloadPath = (J $package 'payload' 'SEST.ContactsFix.dll') }
    try {
        function Copy-Item {
            [CmdletBinding()]param([string]$LiteralPath, [string]$Destination, [switch]$Force)
            if (!$fault.Fired -and $LiteralPath -eq $fault.PayloadPath) {
                $fault.Fired = $true; throw 'Synthetic second-copy failure'
            }
            Microsoft.PowerShell.Management\Copy-Item @PSBoundParameters
        }
        $blocked = $false; try { & $installer @options -Action Stage } catch { $blocked = $_.Exception.Message -match 'Synthetic second-copy failure'; if (!$blocked) { Write-Host $_.Exception.Message } }
        Assert ($blocked -and $fault.Fired) 'Copy failure was not injected'
    } finally { Remove-Item -LiteralPath 'Function:\Copy-Item' }
    Assert ((Hash (J $plugins 'SEST.RuntimeFixes.dll')) -eq $originalRuntime -and (Hash (J $plugins 'SEST.ContactsFix.dll')) -eq $originalUi) 'Partial stage failed to roll back'
    Assert (!(Test-Path -LiteralPath (J $loader 'enable.flag'))) 'Failed stage left activation enabled'
    $idPath = J $workshop '3790594162' 'IdentifyExpanded.dll'; $authorHash = Hash $idPath
    Put $idPath 'DIFFERENT AUTHOR DLL'
    $blocked = $false; try { & $installer @options -Action Stage } catch { $blocked = $_.Exception.Message -match 'changed since the reviewed beta capture' }
    Assert $blocked 'Changed third-party code was accepted'
    Assert ((Hash (J $plugins 'SEST.RuntimeFixes.dll')) -eq $originalRuntime) 'Failed preflight changed own code'
    Seed-File (J $Capture 'references' 'workshop' 'library-1' '3790594162' 'IdentifyExpanded.dll') $idPath
    Assert ((Hash $idPath) -eq $authorHash) 'Fixture author DLL was not restored'
    Write-Host "Beta installer fixture passed: $checks assertions. No real game files changed; no Windows/Unity gameplay claim." -ForegroundColor Green
} finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force } }
