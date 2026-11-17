$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Join-Path ([IO.Path]::GetTempPath()) ('sest-live-item-fixture-' + [Guid]::NewGuid().ToString('N'))
$scriptFile = Join-Path (Split-Path -Parent $PSScriptRoot) 'verify-live-workshop-item.ps1'
$checks = 0
function Assert($Value, [string]$Why) { if (!$Value) { throw $Why }; $script:checks++ }
function Fails([scriptblock]$Action) { try { & $Action | Out-Null; return $false } catch { return $true } }
function Sha([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Listing([string]$Folder) {
    return (@(Get-ChildItem -LiteralPath $Folder -Recurse -File -Force | Sort-Object FullName | ForEach-Object { $_.FullName + '|' + $_.Length + '|' + (Sha $_.FullName) }) -join "`n")
}
try {
    $repo = Join-Path $root 'repo'
    $docs = Join-Path $repo 'docs/releases/20261107'
    $candidate = Join-Path $repo 'integration/beta-feature-parity/candidates/R14-20261114'
    $item = Join-Path $root 'item'
    New-Item -ItemType Directory -Path $docs, $candidate, (Join-Path $item 'plugins'), (Join-Path $root 'r14') -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $item '_info.ini'), '[Mod]')
    [IO.File]::WriteAllText((Join-Path $item 'payload.txt'), 'stable payload')
    [IO.File]::WriteAllText((Join-Path $item 'plugins/SEST.RuntimeFixes.dll'), 'published runtime')
    $files = @(Get-ChildItem -LiteralPath $item -Recurse -File | ForEach-Object {
        @{ path = $_.FullName.Substring($item.Length + 1).Replace('\', '/'); bytes = $_.Length; sha256 = (Sha $_.FullName) }
    })
    $manifestPath = Join-Path $docs 'upload-manifest.json'
    @{ workshop_item_id = '3812461539'; status = 'candidate-needs-gameplay'; files = $files } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath
    # The R14 builds SETUP installs, as the build receipt records them.
    [IO.File]::WriteAllText((Join-Path $root 'r14/SEST.RuntimeFixes.dll'), 'r14 runtime')
    [IO.File]::WriteAllText((Join-Path $root 'r14/SEST.IdentifyDataPaths.dll'), 'r14 identify')
    @{ candidate_revision = 'R14-fixture'; files = @{
        'SEST.RuntimeFixes.dll' = (Sha (Join-Path $root 'r14/SEST.RuntimeFixes.dll'))
        'SEST.IdentifyDataPaths.dll' = (Sha (Join-Path $root 'r14/SEST.IdentifyDataPaths.dll'))
    } } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $candidate 'build-receipt.json')
    $report = Join-Path $root 'report.txt'
    function Run { & $scriptFile -RepositoryRoot $repo -ItemFolder $item -ReportPath $report *> $null; return $LASTEXITCODE }

    # 1. The item as Steam downloads it: identical, SETUP not yet run. Read-only.
    $before = Listing $item
    $global:LASTEXITCODE = 0
    Assert ((Run) -eq 0) 'An identical item was refused'
    $text = Get-Content -LiteralPath $report -Raw
    Assert ($text.Contains('identical to the upload : 3')) 'Identical files were not counted'
    Assert ($text.Contains('RESULT: every uploaded file is in the subscribed item and identical')) 'No pass result'
    Assert ($text.Contains('SETUP has not run since the download')) 'A fresh download was not told apart from a set-up one'
    Assert ((Listing $item) -eq $before) 'The check changed the item'

    # 2. After SETUP: the R14 runtime replaces the published one, Identify paths is added.
    Copy-Item -LiteralPath (Join-Path $root 'r14/SEST.RuntimeFixes.dll') -Destination (Join-Path $item 'plugins/SEST.RuntimeFixes.dll') -Force
    Copy-Item -LiteralPath (Join-Path $root 'r14/SEST.IdentifyDataPaths.dll') -Destination (Join-Path $item 'plugins/SEST.IdentifyDataPaths.dll')
    $global:LASTEXITCODE = 0
    Assert ((Run) -eq 0) 'SETUP''s plugins were counted as a difference'
    $text = Get-Content -LiteralPath $report -Raw
    Assert ($text.Contains('installed by SETUP      : 2  (R14-fixture)')) 'SETUP''s plugins were not recognised by the receipt'
    Assert ($text.Contains('SETUP has run since the download')) 'A set-up item was not reported as such'
    Assert ($text.Contains('not in the upload       : 0')) 'SETUP''s added plugin was listed as an extra'

    # 3. A plugin that is neither the published nor the R14 build is a difference.
    [IO.File]::WriteAllText((Join-Path $item 'plugins/SEST.RuntimeFixes.dll'), 'some other build')
    Assert ((Run) -eq 1) 'An unknown plugin build passed'
    Assert ((Get-Content -LiteralPath $report -Raw).Contains("DIFFERENT:`n  plugins/SEST.RuntimeFixes.dll".Replace("`n", [Environment]::NewLine))) 'The unknown plugin was not named'
    Copy-Item -LiteralPath (Join-Path $root 'r14/SEST.RuntimeFixes.dll') -Destination (Join-Path $item 'plugins/SEST.RuntimeFixes.dll') -Force

    # 4. A changed data file of the same length, and a missing file, each fail and are named.
    [IO.File]::WriteAllText((Join-Path $item 'payload.txt'), 'STABLE PAYLOAD')
    Assert ((Run) -eq 1) 'A same-length changed file passed'
    Assert ((Get-Content -LiteralPath $report -Raw).Contains('different from upload   : 1')) 'The changed file was not counted'
    Remove-Item -LiteralPath (Join-Path $item 'payload.txt')
    Assert ((Run) -eq 1) 'A missing file passed'
    $text = Get-Content -LiteralPath $report -Raw
    Assert ($text.Contains('missing from the item   : 1') -and $text.Contains('  payload.txt')) 'The missing file was not named'
    Assert ($text.Contains('does NOT match the release manifest')) 'No fail result'
    [IO.File]::WriteAllText((Join-Path $item 'payload.txt'), 'stable payload')

    # 5. A file the upload does not have is listed and does not fail the check.
    [IO.File]::WriteAllText((Join-Path $item 'notes.txt'), 'left by something else')
    $global:LASTEXITCODE = 0
    Assert ((Run) -eq 0) 'An extra file failed the check'
    $text = Get-Content -LiteralPath $report -Raw
    Assert ($text.Contains('not in the upload       : 1') -and $text.Contains('  notes.txt')) 'The extra file was not listed'

    # 6. Another item's manifest, a missing manifest and a missing folder are refused.
    @{ workshop_item_id = '1'; status = 'candidate-needs-gameplay'; files = $files } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -ItemFolder $item -ReportPath $report }) 'Another item''s manifest was accepted'
    Remove-Item -LiteralPath $manifestPath
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -ItemFolder $item -ReportPath $report }) 'A missing manifest was accepted'
    Assert (Fails { & $scriptFile -RepositoryRoot $repo -ItemFolder (Join-Path $root 'absent') -ReportPath $report }) 'A missing item folder was accepted'
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
Write-Host "all checks passed: live Workshop item check ($checks); no game, Steam or real data touched."
