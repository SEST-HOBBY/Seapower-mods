#Requires -Version 5.1
<# Temporarily expose the archived ORIGINAL world definition for an old save.
   The combined modern world remains the default. No save file is edited. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$PackPath,
    [switch]$Disable
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) { throw 'Close Sea Power before selecting the legacy definition.' }
$root = (Resolve-Path -LiteralPath $PackPath).Path
$source = Join-Path $root 'legacy_campaigns\sest-world-sandbox\campaign.json'
$target = Join-Path $root 'dynamic_campaigns\sest-world-sandbox\campaign.json'
if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw 'This pack does not contain the preserved original definition.' }
$data = Get-Content -LiteralPath $source -Raw | ConvertFrom-Json
if ($data.id -ne 'sest.world_sandbox_2028') { throw 'Unexpected original campaign identity.' }
if (Test-Path -LiteralPath $target) {
    if ((Get-FileHash -LiteralPath $source).Hash -ne (Get-FileHash -LiteralPath $target).Hash) {
        throw 'The legacy menu definition has local edits; preserve them before changing it.'
    }
}
if ($Disable) {
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target }
    Write-Host 'Original-world menu entry removed. Modernised Worldwide Campaign remains available. Saves are unchanged.'
} else {
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Force
    Write-Host 'Original-world entry enabled for older original saves. Use -Disable to return to one world menu entry. Saves are unchanged.'
}
