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
    # Windows' path limit (259 for a file), checked before any copy: a
    # destination whose longest path would pass it is refused with a clear
    # message and leaves nothing behind; one that fits is accepted.
    $deep = 'missions/' + ('d' * 40) + '/' + ('e' * 40) + '_briefing/' + ('f' * 30) + '.png'
    [IO.File]::WriteAllText((Join-Path $dist '_deep.tmp'), 'x')
    New-Item -ItemType Directory -Path (Split-Path -Parent (Join-Path $dist $deep)) -Force | Out-Null
    Move-Item -LiteralPath (Join-Path $dist '_deep.tmp') -Destination (Join-Path $dist $deep)
    $files = @(Get-ChildItem -LiteralPath $dist -Recurse -File | ForEach-Object {
        @{ path = $_.FullName.Substring($dist.Length + 1).Replace('\', '/'); bytes = $_.Length; sha256 = (Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant() }
    })
    $manifest = @{ workshop_item_id = '3812461539'; status = 'candidate-needs-gameplay'; files = $files }
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath
    $room = 259 - $deep.Length - 1
    $tooLong = Join-Path $root ('L' * [Math]::Max(1, $room - $root.Length))
    $why = ''; try { & $scriptFile -RepositoryRoot $repo -VerifyOnly -CheckPathRoot $tooLong | Out-Null } catch { $why = $_.Exception.Message }
    Assert ($why -match 'Windows path limit' -and $why -match '259') 'A publishing folder over the path limit was not refused clearly'
    $fits = Join-Path $root ('K' * [Math]::Max(1, $room - $root.Length - 2))
    & $scriptFile -RepositoryRoot $repo -VerifyOnly -CheckPathRoot $fits | Out-Null
    Assert $true 'A publishing folder within the path limit was refused'
    $longOut = Join-Path $root ('M' * [Math]::Max(1, $room - $root.Length - 17))
    $why = ''; try { & $scriptFile -RepositoryRoot $repo -OutputDirectory $longOut | Out-Null } catch { $why = $_.Exception.Message }
    Assert ($why -match 'Windows path limit') 'An output folder over the path limit was not refused clearly'
    Assert (@(Get-ChildItem -LiteralPath $root -Directory | Where-Object { $_.Name -like 'M*' }).Count -eq 0) 'A refused output left a folder behind'
    $manifest.files[0].path = '../outside.txt'
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -VerifyOnly }) 'Escaping manifest path accepted'
    Write-Host "all checks passed: upload preparation ($checks)"
} finally { if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force } }
