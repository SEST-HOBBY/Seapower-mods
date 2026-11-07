$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Join-Path ([IO.Path]::GetTempPath()) ('sest-upload-fixture-' + [Guid]::NewGuid().ToString('N'))
$scriptFile = Join-Path (Split-Path -Parent $PSScriptRoot) 'prepare-workshop-upload.ps1'
$checks = 0
function Assert($Value, [string]$Why) { if (!$Value) { throw $Why }; $script:checks++ }
function Fails([scriptblock]$Action) { try { & $Action | Out-Null; return $false } catch { return $true } }
try {
    $repo = Join-Path $root 'repo'
    $dist = Join-Path $repo 'integration/dist/SEST_Integration'
    $docs = Join-Path $repo 'docs/releases/20261107'
    New-Item -ItemType Directory -Path $dist, $docs -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $dist '_info.ini'), '[Mod]')
    [IO.File]::WriteAllText((Join-Path $dist 'payload.txt'), 'stable payload')
    foreach ($name in 'README-FIRST.txt', 'STEAM-CHANGE-NOTE.txt') { [IO.File]::WriteAllText((Join-Path $docs $name), $name) }
    $files = @(Get-ChildItem -LiteralPath $dist -File | ForEach-Object {
        @{ path = $_.Name; bytes = $_.Length; sha256 = (Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant() }
    })
    $manifest = @{ workshop_item_id = '3812461539'; status = 'candidate-needs-gameplay'; files = $files }
    $manifestPath = Join-Path $docs 'upload-manifest.json'
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath
    $out = Join-Path $root 'upload'
    & $scriptFile -RepositoryRoot $repo -OutputDirectory $out -VerifyOnly
    Assert (!(Test-Path -LiteralPath $out)) 'VerifyOnly wrote output'
    & $scriptFile -RepositoryRoot $repo -OutputDirectory $out
    Assert ((Get-Content -LiteralPath (Join-Path $out 'SEST_Integration/payload.txt') -Raw) -eq 'stable payload') 'Valid release not copied'
    Assert ((@(Get-ChildItem -LiteralPath (Join-Path $out 'SEST_Integration') -File)).Count -eq 2) 'Release notes leaked into upload payload'
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -OutputDirectory $out }) 'Existing output was overwritten'
    [IO.File]::WriteAllText((Join-Path $dist 'payload.txt'), 'beta candidate')
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -VerifyOnly }) 'Same-length changed payload accepted'
    [IO.File]::WriteAllText((Join-Path $dist 'payload.txt'), 'stable payload')
    [IO.File]::WriteAllText((Join-Path $dist 'SEST.BetaSafeBootstrap.dll'), 'beta')
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -VerifyOnly }) 'Extra beta DLL accepted'
    Remove-Item -LiteralPath (Join-Path $dist 'SEST.BetaSafeBootstrap.dll')
    $manifest.files[0].path = '../outside.txt'
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -VerifyOnly }) 'Escaping manifest path accepted'
    Write-Host "all checks passed: upload preparation ($checks)"
} finally { if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force } }
