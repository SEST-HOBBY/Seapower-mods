<# Upgrade the staged Nov 1 candidate without replacing its original backups.
   Default action disables activation first, verifies inputs, applies the repair,
   updates the restore journal and re-enables only after all copies verify. #>
[CmdletBinding()]
param(
    [ValidateSet('Repair','Disable','Restore','Collect')][string]$Action = 'Repair',
    [string]$GameRoot = '', [string]$WorkshopContentRoot = '',
    [string]$PlayerDataRoot = '', [string]$AppDataRoot = '', [string]$OutDirectory = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
function J { $p=[string]$args[0]; for ($i=1;$i -lt $args.Count;$i++) { $p=[IO.Path]::Combine($p,[string]$args[$i]) }; return $p }
function Hash([string]$Path) { if (Test-Path -LiteralPath $Path -PathType Leaf) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }; return '' }
function Write-Atomic([string]$Path,[string]$Text) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null
    $temp=$Path+'.sest-'+[guid]::NewGuid().ToString('N')
    try { [IO.File]::WriteAllText($temp,$Text,(New-Object Text.UTF8Encoding($false))); Move-Item -LiteralPath $temp -Destination $Path -Force }
    finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
}
function Copy-Verified([string]$From,[string]$To) {
    $hash=Hash $From; if (!$hash) { throw "Missing repair/backup file: $From" }
    New-Item -ItemType Directory -Path (Split-Path -Parent $To) -Force | Out-Null
    $temp=$To+'.sest-'+[guid]::NewGuid().ToString('N')
    try {
        Copy-Item -LiteralPath $From -Destination $temp -Force
        if ((Hash $temp) -ne $hash) { throw "Copy verification failed: $From" }
        Move-Item -LiteralPath $temp -Destination $To -Force
    } finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
}
if (@(Get-Process -Name 'Sea Power','SeaPower' -ErrorAction SilentlyContinue).Count) { throw 'Close Sea Power first.' }
if (!$GameRoot) {
    $programs=[Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if (!$programs) { throw 'Supply -GameRoot "your Sea Power folder".' }
    $GameRoot=J $programs 'Steam' 'steamapps' 'common' 'Sea Power'
}
$GameRoot=(Resolve-Path -LiteralPath $GameRoot).ProviderPath.TrimEnd([char[]]'\/')
if (!$WorkshopContentRoot) { $WorkshopContentRoot=J (Split-Path -Parent (Split-Path -Parent $GameRoot)) 'workshop' 'content' '1286220' }
$WorkshopContentRoot=(Resolve-Path -LiteralPath $WorkshopContentRoot).ProviderPath.TrimEnd([char[]]'\/')
if (!$AppDataRoot) { $AppDataRoot=J ([Environment]::GetFolderPath('LocalApplicationData')) 'SEST' }
if (!$PlayerDataRoot) { $PlayerDataRoot=J ([Environment]::GetFolderPath('UserProfile')) 'AppData' 'LocalLow' 'Triassic Games' 'Sea Power' }
$loader=J $GameRoot 'BepInEx' 'config' 'SEST-BetaAnchorChain'
$flag=J $loader 'enable.flag'
$statePath=J $AppDataRoot 'BetaCompatibility' 'current.json'
$payload=J $PSScriptRoot 'payload'
$common=@{ GameRoot=$GameRoot; WorkshopContentRoot=$WorkshopContentRoot; PlayerDataRoot=$PlayerDataRoot; AppDataRoot=$AppDataRoot }
if ($Action -eq 'Collect') {
    if ($OutDirectory) { $common.OutDirectory=$OutDirectory }
    & (J $PSScriptRoot 'Install-SEST-Beta.ps1') @common -Action Collect
    return
}
if ($Action -eq 'Restore') { & (J $PSScriptRoot 'Install-SEST-Beta.ps1') @common -Action Restore; return }
# Leave the old, failing activation disabled even when preflight rejects a
# changed installation. No author/plugin settings or data are moved here.
if (Test-Path -LiteralPath $flag) { Move-Item -LiteralPath $flag -Destination ($flag+'.disabled') -Force }
if ($Action -eq 'Disable') { Write-Host 'Beta test activation disabled. Game branch and data retained.'; return }
$new=Get-Content -LiteralPath (J $payload 'build-receipt.json') -Raw | ConvertFrom-Json
$repair=Get-Content -LiteralPath (J $PSScriptRoot 'repair-receipt.json') -Raw | ConvertFrom-Json
if (!(Test-Path -LiteralPath $statePath)) { throw 'This repair requires the previously staged beta test. Use the full installer for a new installation.' }
$state=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
if ($state.format -ne 1 -or $state.phase -ne 'enabled' -or
    $state.game_root -ine $GameRoot -or $state.workshop_root -ine $WorkshopContentRoot -or
    $state.token -notmatch '^[0-9a-f]{32}$') { throw 'Candidate journal does not match this installation. Activation remains disabled.' }
$checks=[ordered]@{
    'Seapower-Scripts.dll'=(J $GameRoot 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll')
    'Noesis.NoesisGUI.dll'=(J $GameRoot 'Sea Power_Data' 'Managed' 'Noesis.NoesisGUI.dll')
    'BepInEx.dll'=(J $GameRoot 'BepInEx' 'core' 'BepInEx.dll')
    '0Harmony.dll'=(J $GameRoot 'BepInEx' 'core' '0Harmony.dll')
    'Mono.Cecil.dll'=(J $GameRoot 'BepInEx' 'core' 'Mono.Cecil.dll')
    'AnchorChain.Preloader.dll'=(J $GameRoot 'BepInEx' 'plugins' 'AnchorChain.Preloader.dll')
    'IdentifyExpanded.dll'=(J $WorkshopContentRoot '3790594162' 'IdentifyExpanded.dll')
    'AnchorChain.dll'=(J $WorkshopContentRoot '3380210757' 'AnchorChain.dll')
    'SeaPowerPopOut.dll'=(J $WorkshopContentRoot '3826396311' 'SeaPowerPopOut.dll')
    'ContactLog.dll'=(J $WorkshopContentRoot '3819427362' 'ContactLog.dll')
    'SeaPowerSquadPanel.dll'=(J $WorkshopContentRoot '3818251045' 'SeaPowerSquadPanel.dll')
    'CombatCosts.dll'=(J $WorkshopContentRoot '3807187341' 'CombatCosts.dll')
    'UnityEngine.CoreModule.dll'=(J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.CoreModule.dll')
    'UnityEngine.InputLegacyModule.dll'=(J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.InputLegacyModule.dll')
    'UnityEngine.IMGUIModule.dll'=(J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.IMGUIModule.dll')
}
foreach ($name in $checks.Keys) {
    if ((Hash $checks[$name]) -ne $new.captured_references.PSObject.Properties[$name].Value) { throw "Reference changed: $name. Activation remains disabled." }
}
# Every candidate file is replaced: the loader, the bootstrap, the Runtime, the
# UI follow-up and the Identify data shim. The installed set must be one reviewed
# candidate as a whole (the first candidate, any earlier repair or this one), and
# the original Stage backups are kept untouched.
$map=[ordered]@{
    'AnchorChain.dll'=(J $loader 'AnchorChain.dll')
    'SEST.BetaSafeBootstrap.dll'=(J $GameRoot 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll')
    'SEST.RuntimeFixes.dll'=(J $WorkshopContentRoot '3812461539' 'plugins' 'SEST.RuntimeFixes.dll')
    'SEST.ContactsFix.dll'=(J $WorkshopContentRoot '3812461539' 'plugins' 'SEST.ContactsFix.dll')
    'SEST.IdentifyDataPaths.dll'=(J $WorkshopContentRoot '3812461539' 'plugins' 'SEST.IdentifyDataPaths.dll')
}
$known=@($repair.base_files, $new.files)
if ($repair.PSObject.Properties['previous_files']) { $known+=@($repair.previous_files) }
$installed=[ordered]@{}
foreach ($name in $map.Keys) { $installed[$name]=Hash $map[$name] }
$accepted=$false
foreach ($version in $known) {
    $matches=$true
    foreach ($name in $map.Keys) {
        if ($installed[$name] -ne $version.PSObject.Properties[$name].Value) { $matches=$false }
    }
    if ($matches) { $accepted=$true; break }
}
if (!$accepted) { throw 'Installed candidate files are not a reviewed beta candidate. Activation remains disabled.' }
foreach ($name in $map.Keys) {
    if ((Hash (J $payload $name)) -ne $new.files.PSObject.Properties[$name].Value) { throw "Repair payload failed verification: $name" }
    $entries=@($state.files | Where-Object { $_.name -eq $name -and $_.is_code })
    if ($entries.Count -ne 1 -or $entries[0].installed_sha256 -ne $installed[$name]) { throw "Original restore journal does not match installed code: $name" }
}
$backup=J $AppDataRoot 'BetaCompatibility' 'startup-repairs' ([guid]::NewGuid().ToString('N'))
foreach ($name in $map.Keys) { Copy-Verified $map[$name] (J $backup $name) }
Copy-Verified $statePath (J $backup 'current-before-repair.json')
Copy-Verified (J $loader 'AnchorChain.sha256') (J $backup 'AnchorChain.sha256')
try {
    foreach ($name in $map.Keys) { Copy-Verified (J $payload $name) $map[$name] }
    Write-Atomic (J $loader 'AnchorChain.sha256') $new.files.PSObject.Properties['AnchorChain.dll'].Value
    foreach ($entry in $state.files) {
        if ($map.Contains($entry.name)) { $entry.installed_sha256=$new.files.PSObject.Properties[$entry.name].Value }
    }
    # Original backup locations/hashes are retained. Restore now recognizes the
    # repaired files instead of treating them as an unrelated external overwrite.
    $state.phase='enabled'
    Write-Atomic $statePath ($state | ConvertTo-Json -Depth 8)
    Write-Atomic $flag 'enable-beta-261106-499675cd'
} catch {
    $failure=$_
    if (Test-Path -LiteralPath $flag) { Remove-Item -LiteralPath $flag -Force }
    foreach ($name in $map.Keys) { Copy-Verified (J $backup $name) $map[$name] }
    Copy-Verified (J $backup 'AnchorChain.sha256') (J $loader 'AnchorChain.sha256')
    Copy-Verified (J $backup 'current-before-repair.json') $statePath
    throw $failure
}
Write-Host 'R8 beta repair installed for the 8 November captured game assembly 499675cd; original backups and Identify data retained.' -ForegroundColor Green
Write-Host 'Runtime 1.5.5 and UI 1.4.8 beta support the captured Combat Cost Tracker 0.8 and Pop-Out Windows 1.1.3.'
Write-Host 'EnhancedDecoyMod, Topographic Map and MultiStageMissiles remain inactive pending native API ports. ExtendedGuidance stays disabled by the SEST profile.'
Write-Host 'Launch beta, test F11, debrief, campaign continuation, formation/Contacts, SAR and Osprey fuel use, then Capture-Repair-Results.cmd.'
