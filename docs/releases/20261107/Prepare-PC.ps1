<# Import a reviewed release, repair beta code, install backed-up data, and
   stage the canonical Workshop upload including bundled features. Never submits to Steam. #>
[CmdletBinding()]
param([string]$MainRepository='', [string]$GameRoot='', [string]$WorkshopContentRoot='', [switch]$ImportOnly)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$env:POWERSHELL_TELEMETRY_OPTOUT='1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT='1'
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function G { & git -C $MainRepository @args;if($LASTEXITCODE -ne 0){throw 'Git stopped; no later install step was run.'} }
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
if($branch -notmatch '^release/[A-Za-z0-9._/-]+$' -or $betaName -notmatch '^R\d+$'){throw 'Unrecognised release receipt.'}
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
if([IO.File]::ReadAllText($report) -notmatch 'Nothing has changed upstream\.'){throw 'An author configuration changed after this capture. Keep the report and capture the new update before installation.'}
$beta=J $PSScriptRoot $betaName
$options=@{};if($GameRoot){$options.GameRoot=$GameRoot};if($WorkshopContentRoot){$options.WorkshopContentRoot=$WorkshopContentRoot}
& (J $beta 'Repair-SEST-Beta-Startup.ps1') @options -Action Repair
$dataOptions=@{RepositoryRoot=$checkout;BetaPackageRoot=$beta}
if($GameRoot){$dataOptions.GameDirectory=$GameRoot};if($WorkshopContentRoot){$dataOptions.WorkshopContentRoot=$WorkshopContentRoot}
& (J $checkout 'tools' 'install-workshop-release-data.ps1') @dataOptions
& (J $checkout 'tools' 'prepare-workshop-upload.ps1') -RepositoryRoot $checkout
[ordered]@{format=1;repository_root=$checkout;release_commit=$actualCommit;game_root=$GameRoot;workshop_content_root=$WorkshopContentRoot;prepared_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (J $PSScriptRoot 'PREPARED-PC.json') -Encoding UTF8
Write-Host ('Beta playtest prepared. Launch the game, test the README items, quit and run '+$betaName+'\Capture-Repair-Results.cmd.') -ForegroundColor Green
Write-Host 'The verified Workshop folder includes the new feature installer. After gameplay checks, quit and run Upload-PC.cmd.'
