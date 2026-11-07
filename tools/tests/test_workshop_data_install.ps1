$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$root=Join-Path ([IO.Path]::GetTempPath()) ('sest-data-fixture-'+[guid]::NewGuid().ToString('N'))
$installer=Join-Path (Split-Path -Parent $PSScriptRoot) 'install-workshop-release-data.ps1'
$checks=0
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Put([string]$p,[string]$s){New-Item -ItemType Directory -Path (Split-Path -Parent $p) -Force|Out-Null;[IO.File]::WriteAllText($p,$s)}
function Sha([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function Assert($v,[string]$why){if(!$v){throw $why};$script:checks++}
function Fails([scriptblock]$f){try{& $f |Out-Null;$false}catch{$true}}
try {
    $repo=J $root 'repo';$source=J $repo 'integration' 'dist' 'SEST_Integration';$game=J $root 'steamapps' 'common' 'Sea Power'
    $ws=J $root 'steamapps' 'workshop' 'content' '1286220';$pack=J $ws '3812461539';$package=J $root 'R7'
    Put (J $source '_info.ini') 'SEST';Put (J $source 'new-data.ini') 'REFRESHED';Put (J $source 'plugins' 'SEST.RuntimeFixes.dll') 'STABLE RUNTIME';Put (J $source 'plugins' 'SEST.ContactsFix.dll') 'STABLE UI'
    Put (J $pack '_info.ini') 'OLD SEST';Put (J $pack 'retired.ini') 'OLD DATA';Put (J $pack 'my-note.txt') 'KEEP IN BACKUP'
    $gameDll=J $game 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll';Put $gameDll 'NATIVE GAME'
    $code=[ordered]@{
        'SEST.RuntimeFixes.dll'=(J $pack 'plugins' 'SEST.RuntimeFixes.dll')
        'SEST.ContactsFix.dll'=(J $pack 'plugins' 'SEST.ContactsFix.dll')
        'SEST.IdentifyDataPaths.dll'=(J $pack 'plugins' 'SEST.IdentifyDataPaths.dll')
        'AnchorChain.dll'=(J $game 'BepInEx' 'config' 'SEST-BetaAnchorChain' 'AnchorChain.dll')
        'SEST.BetaSafeBootstrap.dll'=(J $game 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll')
    }
    $hashes=[ordered]@{};foreach($n in $code.Keys){Put $code[$n] ('R7 '+$n);$hashes[$n]=Sha $code[$n]}
    $receipt=@{candidate_revision='R7-fixture';target_game_sha256=(Sha $gameDll);files=$hashes}
    Put (J $package 'payload' 'build-receipt.json') ($receipt|ConvertTo-Json -Depth 5)
    $prefix=$source+[IO.Path]::DirectorySeparatorChar
    $files=@(Get-ChildItem -LiteralPath $source -Recurse -File|ForEach-Object{@{path=$_.FullName.Substring($prefix.Length).Replace('\','/');bytes=$_.Length;sha256=(Sha $_.FullName)}})
    Put (J $repo 'docs' 'releases' '20261107' 'upload-manifest.json') (@{workshop_item_id='3812461539';status='candidate-needs-gameplay';files=$files}|ConvertTo-Json -Depth 6)
    $options=@{RepositoryRoot=$repo;GameDirectory=$game;WorkshopContentRoot=$ws;BetaPackageRoot=$package}
    $backup=J $root 'backup-1'
    & $installer @options -BackupDirectory $backup
    Assert ((Get-Content -LiteralPath (J $pack 'new-data.ini') -Raw) -eq 'REFRESHED') 'New data missing'
    Assert (!(Test-Path -LiteralPath (J $pack 'retired.ini'))) 'Obsolete override remained active'
    Assert ((Get-Content -LiteralPath (J $backup 'previous' 'my-note.txt') -Raw) -eq 'KEEP IN BACKUP') 'Custom file lost from backup'
    foreach($n in $code.Keys){Assert ((Sha $code[$n]) -eq $hashes[$n]) "Beta code changed: $n"}
    Assert ((Get-Content -LiteralPath (J $source 'plugins' 'SEST.RuntimeFixes.dll') -Raw) -eq 'STABLE RUNTIME') 'Canonical upload was modified'
    Put (J $pack 'new-data.ini') 'USER EDIT'
    Assert (Fails { & $installer -Action Restore -BackupDirectory $backup }) 'Restore overwrote a later edit'
    Put (J $pack 'new-data.ini') 'REFRESHED'
    & $installer -Action Restore -BackupDirectory $backup
    Assert ((Get-Content -LiteralPath (J $pack 'retired.ini') -Raw) -eq 'OLD DATA') 'Previous data did not restore'
    Assert (!(Test-Path -LiteralPath (J $pack 'new-data.ini'))) 'Restore kept the new data active'
    Put $code['SEST.RuntimeFixes.dll'] 'UNKNOWN CODE'
    Assert (Fails { & $installer @options -BackupDirectory (J $root 'bad-code') }) 'Unknown beta code accepted'
    Assert (!(Test-Path -LiteralPath (J $root 'bad-code'))) 'Failed code preflight wrote files'
    Put $code['SEST.RuntimeFixes.dll'] 'R7 SEST.RuntimeFixes.dll'
    Put (J $source 'new-data.ini') 'CORRUPT'
    Assert (Fails { & $installer @options -BackupDirectory (J $root 'bad-data') }) 'Corrupt source accepted'
    Assert ((Get-Content -LiteralPath (J $pack 'retired.ini') -Raw) -eq 'OLD DATA') 'Rejected update changed installed data'
    Put (J $source 'new-data.ini') 'REFRESHED'
    $fault=[pscustomobject]@{Fired=$false;Ready=(J $root 'rollback' 'ready')}
    try {
        function Move-Item {
            [CmdletBinding()]param([string]$LiteralPath,[string]$Destination)
            if(!$fault.Fired -and $LiteralPath -eq $fault.Ready){$fault.Fired=$true;throw 'Synthetic data swap failure'}
            Microsoft.PowerShell.Management\Move-Item @PSBoundParameters
        }
        Assert (Fails { & $installer @options -BackupDirectory (J $root 'rollback') }) 'Swap fault was ignored'
        Assert $fault.Fired 'Swap fault was not injected'
    } finally {Remove-Item -LiteralPath 'Function:\Move-Item'}
    Assert ((Get-Content -LiteralPath (J $pack 'retired.ini') -Raw) -eq 'OLD DATA') 'Failed swap did not restore previous data'
    foreach($n in $code.Keys){Assert ((Sha $code[$n]) -eq $hashes[$n]) "Rollback changed beta code: $n"}
    Write-Host "all checks passed: Workshop data update and restore ($checks)"
} finally {if(Test-Path -LiteralPath $root){Remove-Item -LiteralPath $root -Recurse -Force}}
