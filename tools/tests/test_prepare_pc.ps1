<# Prepare-PC.ps1 (docs\releases\20261107) run end to end against a fixture
   toolkit, to show which beta step each journal phase gets and that the
   stops before it still hold:
     'enabled'                 -> Repair, then the data install
     'staged'                  -> Stage (no change), Enable, then the data install
     'staged', Steam refreshed -> Stage again, then stop for the menu check
     none, 'restored'          -> Stage, then stop for the menu check
   The beta scripts, the author-update check and the data/upload tools are
   stubs that keep the real scripts' parameter blocks (so a parameter the real
   script lacks fails here) and record what they were asked to do. No game,
   Steam, %LOCALAPPDATA% or real data is touched.
       pwsh -File tools/tests/test_prepare_pc.ps1 #>
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$repoSource=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$temp=Join-Path ([IO.Path]::GetTempPath()) ('spp-'+[guid]::NewGuid().ToString('N').Substring(0,8))
$checks=0
$pathBefore=$env:PATH
function J { $p=[string]$args[0];for($i=1;$i -lt $args.Count;$i++){$p=[IO.Path]::Combine($p,[string]$args[$i])};$p }
function Put([string]$Path,[string]$Text){New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null;[IO.File]::WriteAllText($Path,$Text)}
function Json([string]$Path,$Data){Put $Path ($Data | ConvertTo-Json -Depth 10)}
function Assert([bool]$Ok,[string]$Why){if(!$Ok){throw $Why};$script:checks++}
# A stub with the real script's [CmdletBinding()] and parameter block.
function Stub([string]$Real,[string]$Path,[string]$Body){
    $tokens=$null;$errors=$null
    $ast=[System.Management.Automation.Language.Parser]::ParseFile((J $repoSource $Real),[ref]$tokens,[ref]$errors)
    if(!$ast.ParamBlock){throw "No parameter block in $Real"}
    Put $Path ("[CmdletBinding()]`n"+$ast.ParamBlock.Extent.Text+"`n"+'$ErrorActionPreference=''Stop'''+"`n"+$Body+"`n")
}
$fixed='0123456789abcdef0123456789abcdef'
try{
    $toolkit=J $temp 'toolkit';$fixture=J $temp 'source';$log=J $temp 'calls.log'
    $prepare=J $toolkit 'Prepare-PC.ps1'
    New-Item -ItemType Directory -Path $toolkit,$fixture -Force | Out-Null
    Copy-Item -LiteralPath (J $repoSource 'docs' 'releases' '20261107' 'Prepare-PC.ps1') -Destination $prepare
    $env:SEST_PREPARE_LOG=$log
    $record='Add-Content -LiteralPath $env:SEST_PREPARE_LOG -Value '
    # The release the bundle carries: only the three tools Prepare-PC runs from
    # the imported checkout, as stubs.
    Stub 'tools/export-mod-configs.ps1' (J $fixture 'tools' 'export-mod-configs.ps1') ($record+'''check-updates''
$text=''Nothing has changed upstream.''
if($env:SEST_PREPARE_UPSTREAM){$text=''Changed upstream: fixture.ini''}
[IO.File]::WriteAllText($ReportPath,$text)')
    Stub 'tools/install-workshop-release-data.ps1' (J $fixture 'tools' 'install-workshop-release-data.ps1') ($record+'(''data beta=''+(Split-Path -Leaf $BetaPackageRoot))')
    Stub 'tools/prepare-workshop-upload.ps1' (J $fixture 'tools' 'prepare-workshop-upload.ps1') ($record+'(''verify-upload ''+[bool]$VerifyOnly)')
    & git -C $fixture init --quiet
    & git -C $fixture symbolic-ref HEAD refs/heads/sest-dev/fixture
    & git -C $fixture add .
    & git -C $fixture -c user.name=SEST-DEV -c user.email=fixture@example.invalid commit --quiet -m 'Prepare-PC fixture'
    if($LASTEXITCODE -ne 0){throw 'Cannot initialise fixture repository'}
    $head=(& git -C $fixture rev-parse HEAD).Trim()
    $bundle=J $toolkit 'SEST-Workshop-R14-fixture.bundle'
    & git -C $fixture bundle create $bundle refs/heads/sest-dev/fixture
    if($LASTEXITCODE -ne 0){throw 'Cannot bundle the fixture repository'}
    $receipt=[ordered]@{format=1;release_commit=$head;release_branch='sest-dev/fixture';beta_directory='R14'
        workshop_bundle=@{file='SEST-Workshop-R14-fixture.bundle';sha256=(Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash.ToLowerInvariant()}}
    Json (J $toolkit 'SOURCE-RECEIPT.json') $receipt
    # The toolkit's beta folder: the installer and repair scripts as stubs that
    # move the journal the way the real ones do for the step they are given.
    $journalCode='$journal=Join-Path (Join-Path $AppDataRoot ''BetaCompatibility'') ''current.json''
$state=$null;if(Test-Path -LiteralPath $journal){$state=Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json}
function Save([string]$Phase,[string]$Token){[IO.File]::WriteAllText($journal,(@{format=1;phase=$Phase;token=$Token} | ConvertTo-Json))}
'
    Stub 'integration/beta-feature-parity/Install-SEST-Beta.ps1' (J $toolkit 'R14' 'Install-SEST-Beta.ps1') ($journalCode+$record+'(''install ''+$Action+'' quiet=''+[bool]$Quiet+'' appdata=''+$AppDataRoot+'' game=''+$GameRoot)
New-Item -ItemType Directory -Path (Split-Path -Parent $journal) -Force | Out-Null
if($Action -eq ''Stage''){
    if($state -and $state.phase -eq ''installing''){throw ''An incomplete candidate journal exists. Run Restore before staging again.''}
    if($state -and $state.phase -eq ''staged'' -and !$env:SEST_PREPARE_REFRESHED){return}
    Save ''staged'' ([guid]::NewGuid().ToString(''N''))
}
if($Action -eq ''Enable''){
    if($env:SEST_PREPARE_NO_PROBE){throw ''A successful menu probe has not been recorded. Launch beta to the menu, wait 10 seconds, quit, and retry Enable.''}
    Save ''enabled'' $state.token
}')
    Stub 'integration/beta-feature-parity/Repair-SEST-Beta-Startup.ps1' (J $toolkit 'R14' 'Repair-SEST-Beta-Startup.ps1') ($journalCode+$record+'(''repair ''+$Action+'' appdata=''+$AppDataRoot+'' game=''+$GameRoot)')
    # The author-update check runs in Windows PowerShell; elsewhere pwsh
    # stands in for powershell.exe.
    if(!(Get-Command powershell.exe -CommandType Application -ErrorAction SilentlyContinue)){
        $bin=J $temp 'bin';$pwsh=@(Get-Command pwsh -CommandType Application -ErrorAction SilentlyContinue)
        $exe=if($pwsh.Count){$pwsh[0].Source}else{'pwsh'}
        Put (J $bin 'powershell.exe') ("#!/bin/sh`nexec '"+$exe+"' `"`$@`"`n")
        & chmod +x (J $bin 'powershell.exe')
        $env:PATH=$bin+[IO.Path]::PathSeparator+$env:PATH
    }
    $game=J $temp 'game'
    # One Prepare-PC run in its own folder (a fresh main repository, so each
    # run's dated checkout is new). $Phase: the journal to start from, '' for
    # none, $null to keep the journal $AppData already has.
    function Run([string]$Name,$Phase,[string]$AppData='',[hashtable]$Environment=@{}){
        $case=J $temp $Name;$main=J $case 'main'
        if(!$AppData){$AppData=J $case 'appdata'}
        New-Item -ItemType Directory -Path $main -Force | Out-Null
        & git -C $main init --quiet
        $journal=J $AppData 'BetaCompatibility' 'current.json'
        if($null -ne $Phase){
            if(Test-Path -LiteralPath $journal){Remove-Item -LiteralPath $journal -Force}
            if($Phase -eq 'unreadable'){Put $journal '{ not json'}
            elseif($Phase){Json $journal @{format=1;token=$fixed;phase=$Phase;game_root=$game;workshop_root=''}}
        }
        Put $log ''
        $prepared=J $toolkit 'PREPARED-PC.json'
        if(Test-Path -LiteralPath $prepared){Remove-Item -LiteralPath $prepared -Force}
        foreach($k in $Environment.Keys){Set-Item -Path ('Env:'+$k) -Value $Environment[$k]}
        $said=New-Object 'System.Collections.Generic.List[string]';$why=''
        try{& $prepare -MainRepository $main -GameRoot $game -AppDataRoot $AppData 6>&1 | ForEach-Object {$said.Add([string]$_)}}
        catch{$why=$_.Exception.Message}
        finally{foreach($k in $Environment.Keys){Remove-Item -Path ('Env:'+$k) -ErrorAction SilentlyContinue}}
        $after=''
        if(Test-Path -LiteralPath $journal){try{$after=[string](Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json).phase}catch{$after='unreadable'}}
        $calls=@(Get-Content -LiteralPath $log | Where-Object {$_})
        return [pscustomobject]@{calls=$calls;steps=@($calls | ForEach-Object {@($_ -split ' ' | Select-Object -First 2) -join ' '});said=($said -join "`n");why=$why;prepared=(Test-Path -LiteralPath $prepared);phase=$after;appdata=$AppData}
    }
    function Steps($r){return ($r.steps -join ', ')}

    $r=Run 'enabled' 'enabled'
    Assert ($r.why -eq '') ('enabled: Prepare-PC stopped: '+$r.why)
    Assert ((Steps $r) -eq 'check-updates, repair Repair, data beta=R14, verify-upload True') ('enabled: wrong steps: '+(Steps $r))
    Assert ($r.prepared) 'enabled: PREPARED-PC.json was not written'
    Assert (@($r.calls | Where-Object {$_ -like 'repair *'})[0] -like ('* appdata='+$r.appdata+' game='+$game)) 'enabled: -AppDataRoot or -GameRoot was not passed to Repair'
    $preparedRecord=Get-Content -LiteralPath (J $toolkit 'PREPARED-PC.json') -Raw | ConvertFrom-Json
    Assert ($preparedRecord.release_commit -eq $head -and $preparedRecord.game_root -eq $game) 'enabled: PREPARED-PC.json does not record the release and game'

    $r=Run 'staged' 'staged'
    Assert ($r.why -eq '') ('staged: Prepare-PC stopped: '+$r.why)
    Assert ((Steps $r) -eq 'check-updates, install Stage, install Enable, data beta=R14, verify-upload True') ('staged: wrong steps: '+(Steps $r))
    Assert ($r.calls[1] -like 'install Stage quiet=True appdata=*' -and $r.calls[2] -like 'install Enable quiet=False appdata=*') 'staged: Stage was not quiet or Enable was'
    Assert ($r.prepared -and $r.phase -eq 'enabled') 'staged: the run did not finish enabled and prepared'

    foreach($phase in @('','restored')){
        $label=if($phase){$phase}else{'no journal'}
        $r=Run ('stage-'+$label.Replace(' ','-')) $phase
        Assert ($r.why -eq '') ($label+': the stop for the menu check was reported as an error: '+$r.why)
        Assert ((Steps $r) -eq 'check-updates, install Stage') ($label+': wrong steps: '+(Steps $r))
        Assert (!$r.prepared -and $r.phase -eq 'staged') ($label+': the run went past Stage')
        Assert ($r.said -match 'main menu' -and $r.said -match '10 seconds' -and $r.said -match 'run Prepare-PC\.cmd again') ($label+': no instruction to reach the main menu and run Prepare-PC.cmd again')
        Assert ($r.said -match 'no release data was installed') ($label+': the stop does not say the data install is still to come')
    }

    $r=Run 'refreshed' 'staged' '' @{SEST_PREPARE_REFRESHED='1'}
    Assert ($r.why -eq '' -and (Steps $r) -eq 'check-updates, install Stage') ('Steam-refreshed staging: wrong steps: '+(Steps $r)+' '+$r.why)
    Assert (!$r.prepared -and $r.said -match 'run Prepare-PC\.cmd again') 'Steam-refreshed staging: Enable was tried without a new menu check'

    $r=Run 'no-probe' 'staged' '' @{SEST_PREPARE_NO_PROBE='1'}
    Assert ($r.why -match 'menu probe') ('staged without a menu check: Enable''s refusal was lost: '+$r.why)
    Assert ((Steps $r) -eq 'check-updates, install Stage, install Enable') ('staged without a menu check: wrong steps: '+(Steps $r))
    Assert (!$r.prepared -and $r.said -match 'main menu' -and $r.said -match 'run Prepare-PC\.cmd again') 'staged without a menu check: no instruction to run Prepare-PC.cmd again'

    $r=Run 'installing' 'installing'
    Assert ($r.why -match 'incomplete candidate journal') ('installing: Stage''s refusal was lost: '+$r.why)
    Assert ((Steps $r) -eq 'check-updates, install Stage' -and !$r.prepared) ('installing: wrong steps: '+(Steps $r))

    $r=Run 'unreadable' 'unreadable'
    Assert ($r.why -match 'cannot be read') ('unreadable journal: not refused clearly: '+$r.why)
    Assert ((Steps $r) -eq 'check-updates' -and !$r.prepared) ('unreadable journal: a beta step ran: '+(Steps $r))

    $r=Run 'upstream' 'enabled' '' @{SEST_PREPARE_UPSTREAM='1'}
    Assert ($r.why -match 'author configuration changed') ('author update: not refused: '+$r.why)
    Assert ((Steps $r) -eq 'check-updates' -and !$r.prepared) ('author update: a beta step ran: '+(Steps $r))

    # The owner's loop: no journal, run, menu check, run again, then a later run.
    $app=J $temp 'loop-appdata'
    $first=Run 'loop-1' '' $app
    $second=Run 'loop-2' $null $app
    $third=Run 'loop-3' $null $app
    Assert ((Steps $first) -eq 'check-updates, install Stage' -and !$first.prepared) ('loop: first run: '+(Steps $first))
    Assert ((Steps $second) -eq 'check-updates, install Stage, install Enable, data beta=R14, verify-upload True' -and $second.prepared) ('loop: second run: '+(Steps $second)+' '+$second.why)
    Assert ((Steps $third) -eq 'check-updates, repair Repair, data beta=R14, verify-upload True' -and $third.prepared) ('loop: third run: '+(Steps $third)+' '+$third.why)

    # Branch names: sest-dev/ (above) is accepted; others still refused before
    # anything is fetched.
    foreach($branch in @('claude/fixture','main','sest-dev/')){
        $receipt.release_branch=$branch;Json (J $toolkit 'SOURCE-RECEIPT.json') $receipt
        $r=Run ('branch-'+$branch.Replace('/','-')) 'enabled'
        Assert ($r.why -match 'Unrecognised release receipt') ('branch '+$branch+' was accepted')
        Assert (@($r.calls).Count -eq 0 -and !$r.prepared) ('branch '+$branch+': a step ran')
    }
    Write-Host "all checks passed: Prepare-PC beta step by journal phase ($checks); no game, Steam or real data touched."
}finally{
    $env:PATH=$pathBefore
    Remove-Item -Path 'Env:SEST_PREPARE_LOG' -ErrorAction SilentlyContinue
    if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp -Recurse -Force}
}
