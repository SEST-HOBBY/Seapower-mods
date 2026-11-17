<# Import a reviewed release, bring the beta code to this toolkit's candidate,
   install backed-up data, and stage the canonical Workshop upload including
   bundled features. Never submits to Steam.
   The beta journal (BetaCompatibility\current.json under -AppDataRoot, the
   folder the beta scripts use: %LOCALAPPDATA%\SEST unless given) decides the
   beta step. 'enabled': Repair to this candidate, then the data install.
   'staged': Stage (no change unless Steam refreshed the staged files, which
   are staged again), then Enable and the data install. No journal, 'restored'
   or anything else: Stage, then stop until Sea Power has reached the main
   menu once; the next run enables. Stage refuses an incomplete journal.
   -AcceptUpdatedMods <Workshop ids>: the owner's one-off decision to install
   although those mods were updated by their authors after the capture. The
   pack keeps its own copies of their files from the capture until the next
   refresh. Any other change upstream (another updated mod, a new or removed
   subscription) still stops the run. #>
[CmdletBinding()]
param([string]$MainRepository='', [string]$GameRoot='', [string]$WorkshopContentRoot='', [switch]$ImportOnly, [string]$AppDataRoot='', [string[]]$AcceptUpdatedMods=@())
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$env:POWERSHELL_TELEMETRY_OPTOUT='1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT='1'
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function G { & git -C $MainRepository @args;if($LASTEXITCODE -ne 0){throw 'Git stopped; no later install step was run.'} }
# The beta journal's phase and token; an empty phase when there is no journal.
function Read-Journal([string]$Path) {
    $journal=[pscustomobject]@{phase='';token=''}
    if(!(Test-Path -LiteralPath $Path -PathType Leaf)){return $journal}
    try{$state=Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json;$journal.phase=[string]$state.phase;$journal.token=[string]$state.token}
    catch{throw ('The beta journal '+$Path+' cannot be read. No beta code was changed; keep the file for review.')}
    if(!$journal.phase){throw ('The beta journal '+$Path+' has no phase. No beta code was changed; keep the file for review.')}
    return $journal
}
if(@(Get-Process -Name 'Sea Power','SeaPower' -ErrorAction SilentlyContinue).Count){throw 'Close Sea Power first.'}
if(!$MainRepository){$MainRepository=J $env:USERPROFILE 'Seapower-mods'}
$MainRepository=(Resolve-Path -LiteralPath $MainRepository).ProviderPath
$receipt=Get-Content -LiteralPath (J $PSScriptRoot 'SOURCE-RECEIPT.json') -Raw | ConvertFrom-Json
$bundleName=[string]$receipt.workshop_bundle.file
if(!$bundleName -or (Split-Path -Leaf $bundleName) -cne $bundleName){throw 'Unsafe bundle filename in release receipt.'}
$bundle=J $PSScriptRoot $bundleName
if((Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash.ToLowerInvariant() -ne $receipt.workshop_bundle.sha256){throw 'Release bundle hash differs; extract the complete toolkit again.'}
$branch=[string]$receipt.release_branch
$betaName=if($receipt.PSObject.Properties['beta_directory']){[string]$receipt.beta_directory}else{'R7'}
# The release branch is normally beta, the branch the PC installs and tests
# (docs/BRANCHES.md); dev, a release/ branch, one of the owner's feature/,
# fix/ or chore/ branches or a sest-dev/ branch is accepted too
# (tools/build_pc_toolkit.py refuses any other branch with the same pattern).
if($branch -notmatch '^((release|feature|fix|chore|sest-dev)/[A-Za-z0-9._/-]+|beta|dev)$' -or $betaName -notmatch '^R\d+$'){throw 'Unrecognised release receipt.'}
G bundle verify $bundle
G fetch $bundle $branch
$checkout=J (Split-Path -Parent $MainRepository) ('Seapower-Workshop-'+$betaName+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
if(Test-Path -LiteralPath $checkout){throw 'The new checkout already exists; run again after the clock advances.'}
G worktree add --detach $checkout FETCH_HEAD
$actualCommit=(& git -C $checkout rev-parse HEAD).Trim()
if($LASTEXITCODE -ne 0 -or $actualCommit -ne $receipt.release_commit){throw 'The imported checkout does not match the release receipt.'}
Write-Host ('Release checkout: '+$checkout) -ForegroundColor Green
if($ImportOnly){return}
$report=J $PSScriptRoot ('check-updates-'+(Get-Date -Format 'HHmmss')+'.txt')
$checkArgs=@('-NoProfile','-ExecutionPolicy','Bypass','-File',(J $checkout 'tools' 'export-mod-configs.ps1'),'-CheckUpdates','-ReportPath',$report)
if($WorkshopContentRoot){$checkArgs+=@('-WorkshopContentDir',$WorkshopContentRoot)}
& powershell.exe @checkArgs
if($LASTEXITCODE -ne 0 -or !(Test-Path -LiteralPath $report)){throw 'The author-update check failed. No beta/data installation was attempted.'}
$upstream=[IO.File]::ReadAllText($report)
if($upstream -notmatch 'Nothing has changed upstream\.'){
    $accept=@($AcceptUpdatedMods | ForEach-Object {[string]$_ -split '[,\s]+'} | Where-Object {$_})
    $updatedIds=@()
    $section=[regex]::Match($upstream,'(?s)UPDATED by their authors[^\r\n]*\r?\n(.*?)(?:\r?\n[ \t]*\r?\n|$)')
    if($section.Success){$updatedIds=@([regex]::Matches($section.Groups[1].Value,'(?m)^[ \t]+(\d+)[ \t]') | ForEach-Object {$_.Groups[1].Value})}
    $onlyUpdates=($upstream -notmatch 'NEW subscriptions' -and $upstream -notmatch 'EXPORTED but no longer subscribed' -and $updatedIds.Count -gt 0)
    $unaccepted=@($updatedIds | Where-Object {$accept -notcontains $_})
    if(!$accept.Count -or !$onlyUpdates -or $unaccepted.Count){throw 'An author configuration changed after this capture. Keep the report and capture the new update before installation.'}
    Write-Host ('Accepted by -AcceptUpdatedMods: '+($updatedIds -join ', ')+' changed after the capture. The pack keeps its own copies of their files from the capture until the next refresh.') -ForegroundColor Yellow
}
$beta=J $PSScriptRoot $betaName
if(!$AppDataRoot){$AppDataRoot=J ([Environment]::GetFolderPath('LocalApplicationData')) 'SEST'}
$options=@{AppDataRoot=$AppDataRoot};if($GameRoot){$options.GameRoot=$GameRoot};if($WorkshopContentRoot){$options.WorkshopContentRoot=$WorkshopContentRoot}
$journalPath=J $AppDataRoot 'BetaCompatibility' 'current.json'
$journal=Read-Journal $journalPath
Write-Host ('Beta journal: '+$(if($journal.phase){$journal.phase}else{'none'})+' ('+$journalPath+')')
if($journal.phase -eq 'enabled'){
    & (J $beta 'Repair-SEST-Beta-Startup.ps1') @options -Action Repair
}else{
    # Stage refuses an incomplete journal and any SEST code it cannot account
    # for. On a staged journal it changes nothing, unless Steam refreshed the
    # staged files: then it restores them and stages again with a new token.
    & (J $beta 'Install-SEST-Beta.ps1') @options -Action Stage -Quiet
    $staged=Read-Journal $journalPath
    if($journal.phase -ne 'staged' -or $staged.token -ne $journal.token){
        Write-Host ('Beta '+$betaName+' staged. Its plugins stay inactive until Sea Power has reached the main menu once; no release data was installed yet.') -ForegroundColor Green
        Write-Host 'Next: start Sea Power, wait at the main menu about 10 seconds, quit, then run Prepare-PC.cmd again. That run switches the beta features on and installs the release data.' -ForegroundColor Yellow
        return
    }
    try{& (J $beta 'Install-SEST-Beta.ps1') @options -Action Enable}
    catch{
        if($_.Exception.Message -match 'menu probe'){Write-Host 'Start Sea Power, wait at the main menu about 10 seconds, quit, then run Prepare-PC.cmd again.' -ForegroundColor Yellow}
        throw
    }
}
$dataOptions=@{RepositoryRoot=$checkout;BetaPackageRoot=$beta}
if($GameRoot){$dataOptions.GameDirectory=$GameRoot};if($WorkshopContentRoot){$dataOptions.WorkshopContentRoot=$WorkshopContentRoot}
& (J $checkout 'tools' 'install-workshop-release-data.ps1') @dataOptions
# Verify the canonical upload only: the game's uploader cannot pick a copy
# outside StreamingAssets, and Upload-PC.cmd makes the publishing copy there.
& (J $checkout 'tools' 'prepare-workshop-upload.ps1') -RepositoryRoot $checkout -VerifyOnly
[ordered]@{format=1;repository_root=$checkout;release_commit=$actualCommit;game_root=$GameRoot;workshop_content_root=$WorkshopContentRoot;prepared_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (J $PSScriptRoot 'PREPARED-PC.json') -Encoding UTF8
Write-Host ('Beta playtest prepared. Launch the game, test the README items, quit and run '+$betaName+'\Capture-Repair-Results.cmd.') -ForegroundColor Green
Write-Host 'The verified Workshop folder includes the new feature installer. After gameplay checks, quit and run Upload-PC.cmd.'
