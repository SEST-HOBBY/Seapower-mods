<# Capture diagnostics after the canonical beta/r4-20261103 PC test.
   Reuse the installed beta journal to select the game folder; discover all
   Steam Workshop libraries and include the journal's library as an extra.
   Read-only against the installation, settings, history and Workshop files. #>
[CmdletBinding()]
param(
    [string]$GameRoot = '',
    [string[]]$WorkshopContentRoot = @(),
    [string]$PlayerDataRoot = '',
    [string]$OutDirectory = '',
    [string]$InstallJournal = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$options = @{}
if ($GameRoot) { $options.GameRoot = $GameRoot }
if ($WorkshopContentRoot.Count -gt 0) { $options.WorkshopContentRoot = $WorkshopContentRoot }
if ($PlayerDataRoot) { $options.PlayerDataRoot = $PlayerDataRoot }
if ($OutDirectory) { $options.OutDirectory = $OutDirectory }
if (!$GameRoot) {
    if (!$InstallJournal) {
        $InstallJournal = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'SEST/BetaCompatibility/current.json'
    }
    if (Test-Path -LiteralPath $InstallJournal -PathType Leaf) {
        $state = Get-Content -LiteralPath $InstallJournal -Raw | ConvertFrom-Json
        if ($state.format -ne 1 -or [string]::IsNullOrWhiteSpace([string]$state.game_root)) {
            throw 'The beta install journal has no usable game folder. Run again with -GameRoot "your Sea Power folder".'
        }
        $options.GameRoot = [string]$state.game_root
        if ($WorkshopContentRoot.Count -eq 0 -and $state.PSObject.Properties['workshop_root'] -and $state.workshop_root) {
            $options.AdditionalWorkshopContentRoot = @([string]$state.workshop_root)
        }
        Write-Host 'Using the Sea Power folder recorded by the installed beta repair.'
    }
}
& (Join-Path $PSScriptRoot 'capture-beta-references.ps1') @options
