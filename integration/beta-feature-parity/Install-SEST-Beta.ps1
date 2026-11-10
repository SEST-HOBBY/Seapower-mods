<#
.SYNOPSIS
    Stage, enable or restore the SEST beta compatibility candidate.
.DESCRIPTION
    Uses one existing SEST Workshop item. Backups precede every code change.
    Stage installs an inactive bootstrap; Enable requires a fresh successful
    menu probe, migrates Identify data and removes only its local load-order row.
    Never changes the Steam branch, game DLLs, author Workshop DLLs or saves.
    An explicit Restore records the player's opt-out (BetaCompatibility\
    features-off.json), which the pack's SETUP respects; a successful Stage or
    Enable clears it. A Stage that finds its staged files refreshed by Steam
    returns to the journal's state and stages again instead of stopping.
#>
[CmdletBinding()]
param(
    [ValidateSet('Stage', 'Enable', 'Restore', 'Collect', 'Report')][string]$Action = 'Stage',
    [string]$GameRoot = '',
    [string]$WorkshopContentRoot = '',
    [string]$PlayerDataRoot = '',
    [string]$AppDataRoot = '',
    [string]$OutDirectory = '',
    # Called by the pack's SETUP: none of the owner-toolkit instructions are
    # printed; SETUP reports the outcome in its own words.
    [switch]$Quiet,
    # Restore only: SETUP put the normal plugins back because the game build
    # changed. That is not the player's opt-out, so none is recorded.
    [switch]$Automatic
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
function J { $p = [string]$args[0]; for ($i = 1; $i -lt $args.Count; $i++) { $p = [IO.Path]::Combine($p, [string]$args[$i]) }; return $p }
function Hash([string]$Path) {
    if (!(Test-Path -LiteralPath $Path -PathType Leaf)) { return '' }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Note([string]$Text, [string]$Color = '') {
    if ($Quiet) { return }
    if ($Color) { Write-Host $Text -ForegroundColor $Color } else { Write-Host $Text }
}
function Write-Atomic([string]$Path, [string]$Text) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null
    $tmp = $Path + '.sest-' + [guid]::NewGuid().ToString('N')
    try {
        [IO.File]::WriteAllText($tmp, $Text, (New-Object Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $tmp -Destination $Path -Force
    } finally { if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force } }
}
function Copy-Verified([string]$From, [string]$To) {
    $expected = Hash $From
    if (!$expected) { throw "Backup or payload is missing: $From" }
    New-Item -ItemType Directory -Path (Split-Path -Parent $To) -Force | Out-Null
    $tmp = $To + '.sest-' + [guid]::NewGuid().ToString('N')
    try {
        Copy-Item -LiteralPath $From -Destination $tmp -Force
        if ((Hash $tmp) -ne $expected) { throw "Copy verification failed: $From" }
        Move-Item -LiteralPath $tmp -Destination $To -Force
    } finally { if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force } }
}
function Copy-Tree([string]$From, [string]$To, [switch]$OnlyMissing) {
    if (!(Test-Path -LiteralPath $From -PathType Container)) { return }
    $items = New-Object 'System.Collections.Generic.List[System.IO.FileSystemInfo]'
    $pending = New-Object 'System.Collections.Generic.Stack[System.IO.DirectoryInfo]'
    $pending.Push((Get-Item -LiteralPath $From))
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        if (($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'Identify data contains a link or junction. Migration stopped before removing that folder.'
        }
        $items.Add($directory)
        foreach ($item in @(Get-ChildItem -LiteralPath $directory.FullName -Force)) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'Identify data contains a link or junction. Migration stopped before removing that folder.'
            }
            if ($item.PSIsContainer) { $pending.Push($item) } else { $items.Add($item) }
        }
    }
    New-Item -ItemType Directory -Path $To -Force | Out-Null
    foreach ($item in @($items.ToArray() | Select-Object -Skip 1)) {
        $dest = J $To $item.FullName.Substring($From.TrimEnd([char[]]'\/').Length + 1)
        if ($item.PSIsContainer) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
        elseif (!$OnlyMissing -or !(Test-Path -LiteralPath $dest)) { Copy-Verified $item.FullName $dest }
    }
}
function New-IdentifyOrder([string]$Text) {
    $section = [regex]::Match($Text, '(?ims)^\[LoadOrder\][^\r\n]*\r?\n(.*?)(?=^\[|\z)')
    if (!$section.Success) { throw 'usersettings.ini has no LoadOrder section; no settings changed.' }
    $count = [regex]::Match($section.Groups[1].Value, '(?im)^\s*NumberOfModFiles\s*=\s*(\d+)')
    if (!$count.Success) { throw 'NumberOfModFiles is missing; no settings changed.' }
    $entries = @([regex]::Matches($section.Groups[1].Value, '(?im)^\s*Mod(\d+)Directory\s*=\s*([^,\r\n]+)\s*,\s*(True|False)\s*$') |
        Sort-Object { [int]$_.Groups[1].Value })
    if ($entries.Count -ne [int]$count.Groups[1].Value) { throw 'LoadOrder count is inconsistent; no settings changed.' }
    $keep = New-Object 'System.Collections.Generic.List[string]'
    $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $entries) {
        $token = $entry.Groups[2].Value.Trim()
        if ($token -ieq 'IdentifyExpanded') { continue }
        $flag = $entry.Groups[3].Value
        if ($token -in @('3790594162', '3812461539')) { $flag = 'True' }
        $keep.Add($token + ',' + $flag)
        $null = $seen.Add($token)
    }
    foreach ($required in @('3790594162', '3812461539')) {
        if (!$seen.Contains($required)) { throw "Required Workshop entry $required is absent; run SEST SETUP first." }
    }
    $lines = @('[LoadOrder]', ('NumberOfModFiles=' + $keep.Count)); $index = 0
    foreach ($entry in $keep) { $index++; $lines += "Mod${index}Directory=$entry" }
    $replacement = ($lines -join "`r`n") + "`r`n"
    return $Text.Substring(0, $section.Index) + $replacement + $Text.Substring($section.Index + $section.Length)
}

if (@(Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue).Count) { throw 'Close Sea Power first.' }
if (!$GameRoot) {
    $programs = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if (!$programs) { throw 'Run again with -GameRoot "your Sea Power folder".' }
    $GameRoot = J $programs 'Steam' 'steamapps' 'common' 'Sea Power'
}
$GameRoot = (Resolve-Path -LiteralPath $GameRoot).ProviderPath.TrimEnd([char[]]'\/')
if (!$WorkshopContentRoot) { $WorkshopContentRoot = J (Split-Path -Parent (Split-Path -Parent $GameRoot)) 'workshop' 'content' '1286220' }
$WorkshopContentRoot = (Resolve-Path -LiteralPath $WorkshopContentRoot).ProviderPath.TrimEnd([char[]]'\/')
if (!$PlayerDataRoot) { $PlayerDataRoot = J ([Environment]::GetFolderPath('UserProfile')) 'AppData' 'LocalLow' 'Triassic Games' 'Sea Power' }
if (!$AppDataRoot) { $AppDataRoot = J ([Environment]::GetFolderPath('LocalApplicationData')) 'SEST' }
$AppDataRoot = [IO.Path]::GetFullPath($AppDataRoot).TrimEnd([char[]]'\/')
foreach ($root in @($GameRoot, $WorkshopContentRoot)) {
    if ($AppDataRoot.Equals($root, [StringComparison]::OrdinalIgnoreCase) -or
        $AppDataRoot.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Choose a data/backup location outside Sea Power and Workshop.'
    }
}
$pack = J $WorkshopContentRoot '3812461539'
$settings = J $PlayerDataRoot 'usersettings.ini'
$stateRoot = J $AppDataRoot 'BetaCompatibility'
$statePath = J $stateRoot 'current.json'
# The player's "beta features off" choice. It lives beside the journal, outside
# the game and Workshop folders, so a Steam update of the item cannot undo it.
$optOutPath = J $stateRoot 'features-off.json'
$payloadRoot = J $GameRoot 'BepInEx' 'config' 'SEST-BetaAnchorChain'
$dataTarget = J $AppDataRoot 'IdentifyExpanded'
$localIdentify = J $GameRoot 'Sea Power_Data' 'StreamingAssets' 'IdentifyExpanded'
$payload = J $PSScriptRoot 'payload'
$receipt = Get-Content -LiteralPath (J $payload 'build-receipt.json') -Raw | ConvertFrom-Json
$map = [ordered]@{
    'SEST.RuntimeFixes.dll' = (J $pack 'plugins' 'SEST.RuntimeFixes.dll')
    'SEST.ContactsFix.dll' = (J $pack 'plugins' 'SEST.ContactsFix.dll')
    'SEST.IdentifyDataPaths.dll' = (J $pack 'plugins' 'SEST.IdentifyDataPaths.dll')
    'AnchorChain.dll' = (J $payloadRoot 'AnchorChain.dll')
    'SEST.BetaSafeBootstrap.dll' = (J $GameRoot 'BepInEx' 'plugins' 'SEST.BetaSafeBootstrap.dll')
}
$support = [ordered]@{
    'AnchorChain.sha256' = (J $payloadRoot 'AnchorChain.sha256')
    'probe-token.txt' = (J $payloadRoot 'probe-token.txt')
    'probe-ready.json' = (J $payloadRoot 'probe-ready.json')
    'enable.flag' = (J $payloadRoot 'enable.flag')
}
# The reviewed normal-release (stable) Workshop plugins: the only SEST code Stage
# replaces, and the exact copies Steam may put back when it refreshes the item.
$normalRelease = @{
    'SEST.RuntimeFixes.dll' = @('7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986')
    'SEST.ContactsFix.dll' = @('51b56f5efb4c32dcd7f9d71633564613707e6484c3cffdea1adc891b589588f7', '62b49fe4f162e4181a2a51b74ade7522e24d87ee3003d2947003e79bd81a65ea', '6db6de221336fc46a7e85d1aec37e1ff202b1f6872ff2af29b2ec76e530baaff')
}
# The same package's repair receipt names the exact canonical plugins its
# Workshop item ships (workshop_refresh_files); those are normal release too.
$repairReceiptPath = J $PSScriptRoot 'repair-receipt.json'
if (Test-Path -LiteralPath $repairReceiptPath -PathType Leaf) {
    $repairReceipt = Get-Content -LiteralPath $repairReceiptPath -Raw | ConvertFrom-Json
    if ($repairReceipt.PSObject.Properties['workshop_refresh_files']) {
        foreach ($name in @($normalRelease.Keys)) {
            $canonical = $repairReceipt.workshop_refresh_files.PSObject.Properties[$name]
            if ($canonical -and [string]$canonical.Value -match '^[0-9a-f]{64}$' -and @($normalRelease[$name]) -notcontains [string]$canonical.Value) {
                $normalRelease[$name] = @($normalRelease[$name]) + @([string]$canonical.Value)
            }
        }
    }
}
function Set-OptOut([string]$Why) {
    Write-Atomic $optOutPath (([ordered]@{ format = 1; action = $Why; created_utc = [DateTime]::UtcNow.ToString('o') }) | ConvertTo-Json)
}
function Clear-OptOut { if (Test-Path -LiteralPath $optOutPath) { Remove-Item -LiteralPath $optOutPath -Force } }
function Save-State { Write-Atomic $statePath ($script:state | ConvertTo-Json -Depth 8) }
function Load-State {
    if (!(Test-Path -LiteralPath $statePath -PathType Leaf)) { throw 'No staged SEST beta candidate was found.' }
    $script:state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    if ($state.format -ne 1 -or $state.token -notmatch '^[0-9a-f]{32}$' -or
        $state.game_root -ine $GameRoot -or $state.workshop_root -ine $WorkshopContentRoot) {
        throw 'The saved candidate belongs to another installation. No files changed.'
    }
    $script:backup = J $stateRoot 'backups' $state.token
}
function Check-External {
    $external = [ordered]@{
        'Seapower-Scripts.dll' = (J $GameRoot 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll')
        'Noesis.NoesisGUI.dll' = (J $GameRoot 'Sea Power_Data' 'Managed' 'Noesis.NoesisGUI.dll')
        'UnityEngine.CoreModule.dll' = (J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.CoreModule.dll')
        'UnityEngine.InputLegacyModule.dll' = (J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.InputLegacyModule.dll')
        'UnityEngine.IMGUIModule.dll' = (J $GameRoot 'Sea Power_Data' 'Managed' 'UnityEngine.IMGUIModule.dll')
        'BepInEx.dll' = (J $GameRoot 'BepInEx' 'core' 'BepInEx.dll')
        'Mono.Cecil.dll' = (J $GameRoot 'BepInEx' 'core' 'Mono.Cecil.dll')
        '0Harmony.dll' = (J $GameRoot 'BepInEx' 'core' '0Harmony.dll')
        'AnchorChain.Preloader.dll' = (J $GameRoot 'BepInEx' 'plugins' 'AnchorChain.Preloader.dll')
        'AnchorChain.dll' = (J $WorkshopContentRoot '3380210757' 'AnchorChain.dll')
        'IdentifyExpanded.dll' = (J $WorkshopContentRoot '3790594162' 'IdentifyExpanded.dll')
        'CombatCosts.dll' = (J $WorkshopContentRoot '3807187341' 'CombatCosts.dll')
        'ContactLog.dll' = (J $WorkshopContentRoot '3819427362' 'ContactLog.dll')
        'SeaPowerSquadPanel.dll' = (J $WorkshopContentRoot '3818251045' 'SeaPowerSquadPanel.dll')
        'SeaPowerPopOut.dll' = (J $WorkshopContentRoot '3826396311' 'SeaPowerPopOut.dll')
    }
    foreach ($name in $external.Keys) {
        if ((Hash $external[$name]) -ne $receipt.captured_references.PSObject.Properties[$name].Value) {
            throw "Build or mod changed since the reviewed beta capture: $name. No compatibility override applied."
        }
    }
    if (Test-Path -LiteralPath (J $GameRoot 'BepInEx' 'plugins' 'SEST.BetaAnchorBootstrap.dll')) {
        throw 'The obsolete PR #53 bootstrap is present. Remove that test plugin before staging this candidate.'
    }
}
function Check-Installed {
    foreach ($name in $map.Keys) {
        if ((Hash $map[$name]) -ne $receipt.files.PSObject.Properties[$name].Value) { throw "Staged candidate was changed: $name" }
    }
}
function Restore-Candidate {
    # Check the whole code restore before replacing anything. A Steam update
    # must not be overwritten with an older backup without noticing.
    $steamCopies = @{}
    foreach ($entry in $state.files) {
        $dest = if ($map.Contains($entry.name)) { $map[$entry.name] } else { $support[$entry.name] }
        if (!$dest) { throw 'Unrecognized file in restore journal.' }
        if ($entry.is_code) {
            $current = Hash $dest
            if ($current -and $current -ne $entry.installed_sha256 -and $current -ne $entry.original_sha256) {
                # Steam refreshed the item: an exact reviewed normal-release
                # plugin is already back, so it is kept, not an older backup.
                if ($normalRelease.ContainsKey($entry.name) -and @($normalRelease[$entry.name]) -contains $current) { $steamCopies[$entry.name] = $true }
                else { throw "Restore stopped: $($entry.name) changed independently. Backups remain at $backup" }
            }
        }
        if ($entry.existed -and (Hash (J $backup 'files' $entry.name)) -ne $entry.original_sha256) {
            throw "Backup verification failed: $($entry.name). Nothing restored."
        }
    }
    # Disable first, before returning the original Runtime and UI pair.
    if (Test-Path -LiteralPath $support['enable.flag']) { Remove-Item -LiteralPath $support['enable.flag'] -Force }
    foreach ($entry in $state.files) {
        if ($steamCopies.ContainsKey($entry.name)) { continue }
        $dest = if ($map.Contains($entry.name)) { $map[$entry.name] } else { $support[$entry.name] }
        if ($entry.existed) { Copy-Verified (J $backup 'files' $entry.name) $dest }
        elseif (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Force }
    }
    if ($state.local_migration_started) { Copy-Tree (J $backup 'IdentifyExpanded-local') $localIdentify -OnlyMissing }
    if ($state.settings_after_sha256 -and (Hash $settings) -eq $state.settings_after_sha256) {
        Copy-Verified (J $backup 'usersettings-before-enable.ini') $settings
    }
    $state.phase = 'restored'; Save-State
    Note 'Original SEST code restored. Migrated Identify data is retained outside the game.' 'Green'
    if ($steamCopies.Count) { Note ('Steam''s own normal-release copy kept: ' + (@($steamCopies.Keys | Sort-Object) -join ', ')) }
    Note "Backups retained: $backup"
}

if ($Action -eq 'Collect') {
    $captureArgs = @{ GameRoot = $GameRoot; WorkshopContentRoot = @($WorkshopContentRoot); PlayerDataRoot = $PlayerDataRoot }
    if ($OutDirectory) { $captureArgs.OutDirectory = $OutDirectory }
    & (J $PSScriptRoot 'capture-beta-references.ps1') @captureArgs
    return
}
if ($Action -eq 'Restore') {
    Load-State; Restore-Candidate
    # An explicit Restore is the player's choice: the pack's SETUP must not
    # stage the features again until they are switched back on.
    if (!$Automatic) { Set-OptOut 'Restore' }
    return
}
if ($Action -eq 'Report') {
    Load-State
    Write-Host "Candidate phase: $($state.phase)"
    Write-Host "Local IdentifyExpanded folder exists: $(Test-Path -LiteralPath $localIdentify)"
    Write-Host "Identify data: $dataTarget"
    foreach ($name in $map.Keys) { Write-Host "$name : $(Hash $map[$name])" }
    return
}
Check-External
foreach ($name in $map.Keys) {
    if ((Hash (J $payload $name)) -ne $receipt.files.PSObject.Properties[$name].Value) { throw "Payload integrity failure: $name" }
}
if (!(Test-Path -LiteralPath $settings -PathType Leaf)) { throw 'usersettings.ini is missing. Launch and quit beta once before staging.' }
$null = New-IdentifyOrder ([IO.File]::ReadAllText($settings))

if ($Action -eq 'Stage') {
    if (Test-Path -LiteralPath $statePath) {
        Load-State
        if ($state.phase -in @('staged', 'enabled')) {
            $drift = $null
            try { Check-Installed } catch { $drift = $_ }
            if (!$drift) {
                Clear-OptOut
                Note "Candidate is already $($state.phase). No files changed."
                return
            }
            if ($state.phase -ne 'staged') { throw $drift }
            # Staged but never enabled, and the files are no longer this
            # bundle's: Steam refreshed the item (its normal plugins are back)
            # or a newer bundle arrived. Nothing was migrated yet, so return to
            # the journal's state, which refuses any file it cannot account
            # for, and stage this bundle afresh with a new probe token.
            Restore-Candidate
            Note 'The staged files were changed by a Steam update of the item; staging the current bundle again.'
        } elseif ($state.phase -ne 'restored') { throw 'An incomplete candidate journal exists. Run Restore before staging again.' }
    }
    foreach ($name in $map.Keys) {
        if ($normalRelease.ContainsKey($name)) {
            if (@($normalRelease[$name]) -notcontains (Hash $map[$name])) { throw "Existing SEST code differs from the captured baseline: $name" }
        } elseif (Test-Path -LiteralPath $map[$name]) { throw "An earlier candidate file already exists: $($map[$name]). Keep it for review before installing another." }
    }
    $token = [guid]::NewGuid().ToString('N')
    $backup = J $stateRoot 'backups' $token
    $files = @()
    foreach ($dictionary in @($map, $support)) {
        foreach ($name in $dictionary.Keys) {
            $dest = $dictionary[$name]; $hash = Hash $dest
            if (Test-Path -LiteralPath $dest -PathType Container) { throw "A file location is occupied by a folder: $dest" }
            if ($hash) { Copy-Verified $dest (J $backup 'files' $name) }
            $files += [ordered]@{
                name = $name; existed = [bool]$hash; original_sha256 = $hash
                is_code = $map.Contains($name)
                installed_sha256 = $(if ($map.Contains($name)) { $receipt.files.PSObject.Properties[$name].Value } else { '' })
            }
        }
    }
    $state = [pscustomobject]@{
        format = 1; token = $token; phase = 'installing'; game_root = $GameRoot; workshop_root = $WorkshopContentRoot
        created_utc = [DateTime]::UtcNow.ToString('o'); files = $files
        local_migration_started = $false; settings_after_sha256 = ''
    }
    Save-State
    try {
        foreach ($name in $map.Keys) { Copy-Verified (J $payload $name) $map[$name] }
        foreach ($name in @('enable.flag', 'probe-ready.json')) {
            if (Test-Path -LiteralPath $support[$name]) { Remove-Item -LiteralPath $support[$name] -Force }
        }
        Write-Atomic $support['AnchorChain.sha256'] $receipt.files.PSObject.Properties['AnchorChain.dll'].Value
        Write-Atomic $support['probe-token.txt'] $token
        $state.phase = 'staged'; Save-State
    } catch {
        $failure = $_
        Restore-Candidate
        throw $failure
    }
    Clear-OptOut
    Note 'Beta candidate staged; plugin loading is still inactive.' 'Green'
    Note 'Launch beta to the main menu, wait about 10 seconds, quit, then run 2-Enable-Beta.cmd.'
    return
}

Load-State
if ($state.phase -eq 'enabled') { Check-Installed; Clear-OptOut; Note 'This candidate is already enabled.'; return }
if ($state.phase -ne 'staged') { throw 'Stage the candidate before enabling it.' }
Check-Installed
if (!(Test-Path -LiteralPath $support['probe-ready.json'])) { throw 'A successful menu probe has not been recorded. Launch beta to the menu, wait 10 seconds, quit, and retry Enable.' }
$proof = Get-Content -LiteralPath $support['probe-ready.json'] -Raw | ConvertFrom-Json
if ($proof.format -ne 1 -or $proof.token -ne $state.token -or $proof.enabled -ne $false -or
    $proof.native_sha256 -ne $receipt.target_game_sha256 -or
    [DateTime]::Parse($proof.created_utc).ToUniversalTime() -lt [DateTime]::Parse($state.created_utc).ToUniversalTime()) {
    throw 'The menu probe does not match this staged candidate. No activation performed.'
}
try {
    $text = [IO.File]::ReadAllText($settings)
    $updated = New-IdentifyOrder $text
    Copy-Verified $settings (J $backup 'usersettings-before-enable.ini')
    if (Test-Path -LiteralPath $localIdentify -PathType Container) {
        # Keep both old locations before merging. The formerly active local
        # data takes precedence; pre-existing redirected data remains backed up.
        Copy-Tree $localIdentify (J $backup 'IdentifyExpanded-local')
        Copy-Tree $dataTarget (J $backup 'IdentifyExpanded-previous-data')
        $state.local_migration_started = $true; Save-State
        Copy-Tree $localIdentify $dataTarget
        Remove-Item -LiteralPath $localIdentify -Recurse -Force
    }
    $state.settings_after_sha256 = [BitConverter]::ToString(([Security.Cryptography.SHA256]::Create()).ComputeHash([Text.Encoding]::UTF8.GetBytes($updated))).Replace('-', '').ToLowerInvariant()
    Save-State
    Write-Atomic $settings $updated
    Write-Atomic $support['enable.flag'] 'enable-beta-261106-499675cd'
    $state.phase = 'enabled'; Save-State
} catch {
    $failure = $_
    Restore-Candidate
    throw $failure
}
Clear-OptOut
Note 'Beta candidate enabled. Local IdentifyExpanded was migrated; its Workshop copy remains enabled.' 'Green'
Note 'Launch beta and test F11 costs/history, debrief, preparation, Contacts and Formation pop-out/return.'
Note 'After quitting, run 3-Capture-Test-Results.cmd. Run Restore-Previous-SEST.cmd to restore the prior code.'
