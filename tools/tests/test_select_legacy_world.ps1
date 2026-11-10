$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$root=Join-Path ([IO.Path]::GetTempPath()) ('sest-legacy-world-'+[guid]::NewGuid().ToString('N'))
$scriptFile=Join-Path (Split-Path -Parent $PSScriptRoot) 'select-legacy-world.ps1'
$checks=0
function Assert($ok,[string]$why){if(!$ok){throw $why};$script:checks++}
try {
    $source=Join-Path $root 'legacy_campaigns/sest-world-sandbox/campaign.json'
    $target=Join-Path $root 'dynamic_campaigns/sest-world-sandbox/campaign.json'
    $modern=Join-Path $root 'dynamic_campaigns/sest-world-regions-2028/campaign.json'
    $save=Join-Path $root 'native-save.json'
    New-Item -ItemType Directory -Path (Split-Path $source), (Split-Path $modern) -Force | Out-Null
    [IO.File]::WriteAllText($source,'{"id":"sest.world_sandbox_2028","name":"original"}')
    [IO.File]::WriteAllText($modern,'{"id":"sest.world_sandbox_2028.regional","name":"modern"}')
    [IO.File]::WriteAllText($save,'original user save')
    $hash=(Get-FileHash -LiteralPath $save).Hash
    & $scriptFile -PackPath $root
    Assert ((Get-Content -LiteralPath $source -Raw) -ceq (Get-Content -LiteralPath $target -Raw)) 'Legacy activation changed definition'
    Assert (Test-Path -LiteralPath $modern) 'Modern world disappeared'
    & $scriptFile -PackPath $root -Disable
    Assert (!(Test-Path -LiteralPath $target)) 'Legacy entry did not disable'
    Assert (Test-Path -LiteralPath $modern) 'Disable removed modern world'
    & $scriptFile -PackPath $root
    [IO.File]::WriteAllText($target,'user modification')
    $refused=$false;try{& $scriptFile -PackPath $root -Disable}catch{$refused=$true}
    Assert $refused 'Locally edited definition was removed'
    Assert ((Get-FileHash -LiteralPath $save).Hash -eq $hash) 'Native save changed'
    Write-Host "all checks passed: reversible legacy-world selection ($checks)"
} finally {if(Test-Path -LiteralPath $root){Remove-Item -LiteralPath $root -Recurse -Force}}
