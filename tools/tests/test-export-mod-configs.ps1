# Standalone fixtures; never reads or changes the real Steam installation.
# powershell -ExecutionPolicy Bypass -File .\tools\tests\test-export-mod-configs.ps1
$ErrorActionPreference = 'Stop'
$exporter = Join-Path (Split-Path -Parent $PSScriptRoot) 'export-mod-configs.ps1'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('sest-export-test-' + [guid]::NewGuid().ToString('N'))
$source = Join-Path $fixture 'workshop'
$dest = Join-Path $fixture 'mods-source'
function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}
try {
    foreach ($rel in @('workshop/100', 'workshop/not-a-mod', 'mods-source/100', 'mods-source/200', 'mods-source/_vanilla')) {
        New-Item -ItemType Directory -Force -Path (Join-Path $fixture $rel) | Out-Null
    }
    Set-Content -LiteralPath (Join-Path $source '100/current.ini') -Value 'current' -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $source '100/skipped.bin') -Value 'binary'
    Set-Content -LiteralPath (Join-Path $dest '100/obsolete.ini') -Value 'preserve in backup'
    Set-Content -LiteralPath (Join-Path $dest '200/absent.ini') -Value 'absent mod'
    Set-Content -LiteralPath (Join-Path $dest '_vanilla/base.ini') -Value 'vanilla'
    & $exporter -WorkshopContentDir $source -DestDir $dest -NoPrune
    Assert-True (Test-Path -LiteralPath (Join-Path $dest '100/current.ini')) 'Current file missing'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $dest '100/obsolete.ini'))) 'Obsolete file survived refresh'
    Assert-True (Test-Path -LiteralPath (Join-Path $dest '200/absent.ini')) '-NoPrune lost absent mod'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $dest '100/skipped.bin'))) 'Binary was exported'
    $manifest = @(Import-Csv -LiteralPath (Join-Path $dest '_export-manifest.csv'))
    Assert-True ($manifest.Count -eq 1 -and $manifest[0].WorkshopId -eq '100' -and $manifest[0].FilesCopied -eq '1') 'Manifest differs from source'
    $files = @(Import-Csv -LiteralPath (Join-Path $dest '_export-files.csv'))
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $dest '100/current.ini') -Algorithm SHA256).Hash
    Assert-True ($files.Count -eq 1 -and $files[0].SHA256 -eq $actualHash) 'Hash manifest differs from exported bytes'
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $fixture '_export-backups') -Recurse -File -Filter 'obsolete.ini')
    Assert-True ($backups.Count -eq 1) 'Original file not retained in backup'

    # Inject a rename failure after the first folder was replaced. The original
    # snapshot (including the previous manifests) must be restored completely.
    $before = (Get-FileHash -LiteralPath (Join-Path $dest '100/current.ini')).Hash
    Set-Content -LiteralPath (Join-Path $source '100/current.ini') -Value 'updated' -Encoding UTF8
    # The shadow runs inside the exporter's script scope, where $script: means the
    # exporter's variables, not this file's - the flag read as $null there and the
    # injected failure never fired (2026-09-16, first Windows run). Only a global
    # is the same variable from both scripts, and a global function is visible
    # from both scopes without depending on how & nests them.
    $global:SestFixtureFailPublishOnce = $true
    function global:Move-Item {
        param([string]$LiteralPath, [string]$Destination)
        if ($global:SestFixtureFailPublishOnce -and $LiteralPath -match '_export-staging-' -and
            (Split-Path -Leaf $LiteralPath) -eq '_export-manifest.csv') {
            $global:SestFixtureFailPublishOnce = $false
            throw 'Injected publication failure'
        }
        Microsoft.PowerShell.Management\Move-Item -LiteralPath $LiteralPath -Destination $Destination
    }
    $failed = $false
    try { & $exporter -WorkshopContentDir $source -DestDir $dest } catch {
        Assert-True ($_.Exception.Message -match 'Injected publication failure') 'Unexpected failure in rollback fixture'
        $failed = $true
    } finally {
        Remove-Item Function:\global:Move-Item
        Remove-Variable -Name SestFixtureFailPublishOnce -Scope Global -ErrorAction SilentlyContinue
    }
    Assert-True $failed 'Publication failure was not exercised'
    Assert-True ((Get-FileHash -LiteralPath (Join-Path $dest '100/current.ini')).Hash -eq $before) 'Rollback lost previous content'
    Assert-True (Test-Path -LiteralPath (Join-Path $dest '200/absent.ini')) 'Rollback lost absent mod'
    $rolledBack = @(Import-Csv -LiteralPath (Join-Path $dest '_export-files.csv'))
    Assert-True ($rolledBack[0].SHA256 -eq $before) 'Rollback lost previous manifest'

    & $exporter -WorkshopContentDir $source -DestDir $dest
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $dest '200'))) 'Absent mod not archived'
    Assert-True (Test-Path -LiteralPath (Join-Path $dest '_vanilla/base.ini')) 'Unrequested vanilla export changed'
    Assert-True ((Get-FileHash -LiteralPath (Join-Path $dest '100/current.ini')).Hash -ne $before) 'Updated content not published'
    $failed = $false
    try { & $exporter -WorkshopContentDir $source -DestDir (Join-Path $source 'nested') } catch { $failed = $true }
    Assert-True $failed 'Overlapping destination was accepted'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $source 'nested'))) 'Overlap check wrote into source'
    Write-Host 'PASS: refresh, NoPrune, backups, hashes, rollback, pruning and overlap guard'
} finally {
    if (Test-Path -LiteralPath $fixture) { Remove-Item -LiteralPath $fixture -Recurse -Force }
}
