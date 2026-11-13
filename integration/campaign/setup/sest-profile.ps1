# SEST Integration Pack - which Sea Power build is installed, what the pack
# does on it, and whether the code mods loaded at the last launch. SETUP
# runs this in its step 1; run it by hand with the game closed:
#   powershell -ExecutionPolicy Bypass -File .\sest-profile.ps1 -GameDir "<...>\common\Sea Power"
#
# Read only: it changes no file, installs nothing and never stops SETUP.
# SEST's own code plugins are each matched to one game file, so what this
# reports is the SHA-256 of Sea Power_Data\Managed\Seapower-Scripts.dll:
#   eab2297b...  0.8.7 Build 261021, the build SEST Runtime Fixes 1.5.0 and
#                SEST UI Follow-up are matched to. They can start, each only
#                if its own SHA-256 checks pass.
#   3005bc6d...  0.8.7 Build 261026, a beta of October 2026. The pack's data
#                loads; both plugins stay off under those checks; the
#                Workshop Anchor Chain preloader finds no chainloader, so
#                no Anchor Chain mod loads; the bounded Anchor Chain loader
#                in SEST's source (integration\beta-anchorchain) is a test
#                candidate that nothing installs.
#   499675cd...  the 0.8.7-261107 beta the bundled beta features were
#                reviewed for; 9b35a7aa... the beta image before it.
#   anything else, Sea Power 0.9.0 (11 Nov 2026) included until its file has
#                been captured: not a file any SEST plugin is matched to, so
#                the plugins stay off. The pack's campaigns and data files
#                do not depend on that file. The note names the version the
#                game's own changelog.txt gives, and the one the pack's data
#                declares (ApproximateVersion in the _info.ini beside this
#                script, when there is one).
# It also names two beta test plugins in BepInEx\plugins: the discontinued
# PR #53 SEST.BetaAnchorBootstrap.dll, with which the beta did not open (one
# [!!] warning, with the step that removes it), and the inert
# SEST.BetaSafeBootstrap.dll (a note). Last, when BepInEx\LogOutput.log
# (rewritten at every launch) shows that Anchor Chain did not load at the
# last launch, 'Could not find AnchorChain chainloader', or no 'Loaded
# assembly AnchorChain,' after the last 'AnchorChain Preloader started', it
# gives one [!!] warning.
#
# -PassThru: the number of [!!] warnings goes to the pipeline (SETUP adds
# it to its own count). -StableSha256 and -BetaSha256 are for the setup
# tests; SETUP passes neither.
param(
    [Parameter(Mandatory = $true)][string]$GameDir,
    [switch]$PassThru,
    [string]$StableSha256 = 'eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd',
    [string]$BetaSha256 = '3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62',
    [string]$CurrentBetaSha256 = '499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9',
    [string]$PreviousBetaSha256 = '9b35a7aa4f0bd3c78211fb9cf1e3d6398d0dbbc0f787674e843cc9563fd93f53'
)
$ErrorActionPreference = 'Stop'
function J { $p = [string]$args[0]; for ($k = 1; $k -lt $args.Count; $k++) { $p = [IO.Path]::Combine($p, [string]$args[$k]) }; $p }
function Say([string]$t, [string]$c = 'Gray') { Write-Host $t -ForegroundColor $c }
$warnings = 0

# --- the game build ----------------------------------------------------------
$scripts = J $GameDir 'Sea Power_Data' 'Managed' 'Seapower-Scripts.dll'
$hash = ''
if (Test-Path -LiteralPath $scripts -PathType Leaf) {
    try { $hash = (Get-FileHash -LiteralPath $scripts -Algorithm SHA256).Hash.ToLowerInvariant() } catch { $hash = '' }
}
# What the game calls itself: the first dated line of its changelog.txt, as
# SETUP's own step 3 reads it. What the pack's data is built for: the
# ApproximateVersion of the pack this script sits in.
$named = ''
foreach ($chg in @((J $GameDir 'changelog.txt'), (J $GameDir 'Sea Power_Data' 'changelog.txt'))) {
    if ($named -or -not (Test-Path -LiteralPath $chg -PathType Leaf)) { continue }
    try {
        $vm = [regex]::Match([IO.File]::ReadAllText($chg), '(?m)^\d{1,2}-[A-Za-z]{3}-\d{4}:\s+(\d+\.\d+\.\d+)\s+Build\s+(\d+)')
        if ($vm.Success) { $named = 'Sea Power ' + $vm.Groups[1].Value + ' Build ' + $vm.Groups[2].Value }
    } catch { $named = '' }
}
$builtFor = ''
$packInfo = J $PSScriptRoot '_info.ini'
if (Test-Path -LiteralPath $packInfo -PathType Leaf) {
    try {
        $pm = [regex]::Match([IO.File]::ReadAllText($packInfo), '(?m)^ApproximateVersion=(\d+\.\d+\.\d+)\s*$')
        if ($pm.Success) { $builtFor = ' The pack''s data files are built for Sea Power ' + $pm.Groups[1].Value + '.' }
    } catch { $builtFor = '' }
}
$build = 'unknown'
if ($hash -and $hash -eq $StableSha256.ToLowerInvariant()) { $build = 'stable' }
elseif ($hash -and $hash -eq $BetaSha256.ToLowerInvariant()) { $build = 'beta' }
elseif ($hash -and $hash -eq $CurrentBetaSha256.ToLowerInvariant()) { $build = 'beta-current' }
elseif ($hash -and $hash -eq $PreviousBetaSha256.ToLowerInvariant()) { $build = 'beta-previous' }
if ($build -eq 'stable') {
    Say '  [ok]   game code: Sea Power 0.8.7 Build 261021, the build SEST Runtime Fixes 1.5.0 and SEST UI Follow-up are matched to' 'Green'
    Say '         SEST Runtime Fixes 1.5.0 and SEST UI Follow-up can start, each only if its own SHA-256 checks pass.'
    if ($builtFor) { Say ('        ' + $builtFor) }
} elseif ($build -eq 'beta') {
    Say ('  [note] game code: Sea Power 0.8.7 Build 261026, a beta build of October 2026.' + $builtFor)
    Say '         On this build the pack''s campaigns and data load, but SEST Runtime Fixes 1.5.0 and SEST UI Follow-up stay off under their SHA-256 checks,'
    Say '         and the Workshop Anchor Chain preloader finds no chainloader, so no Anchor Chain mod loads, SEST''s or any other author''s.'
    Say '         A bounded Anchor Chain loader for that beta is in SEST''s source as a test candidate only; nothing installs it.'
} elseif ($build -eq 'beta-current') {
    Say '  [note] game assembly: 499675cd..., reviewed 9 November 2026 for the bundled Workshop feature update.'
    Say ('         This is the 0.8.7-261107 beta build; the pack''s data loads, while the plugins matched to Build 261021 remain inactive.' + $builtFor)
    Say '         The R12 Workshop item bundles the R13 beta features (World Operations, strike features and the debrief mission ribbons); SETUP installs them on this build.'
} elseif ($build -eq 'beta-previous') {
    Say '  [note] older beta assembly: 9b35a7aa..., captured 7 November 2026. R7 targets this image; the plugins matched to Build 261021 remain inactive.'
} elseif ($hash) {
    $says = ''; if ($named) { $says = ' The game''s changelog says ' + $named + '.' }
    Say ('  [note] game code: Seapower-Scripts.dll SHA-256 ' + $hash.Substring(0, 16) + '... is not a file SEST''s own code plugins are matched to.' + $says)
    Say ('         SEST Runtime Fixes and SEST UI Follow-up check that file themselves and stay off on it. The pack''s campaigns and data files do not depend on it.' + $builtFor)
} else {
    Say ('  [note] game build not identified: ' + $scripts + ' could not be read.')
    Say '         SEST Runtime Fixes and SEST UI Follow-up stay off under their own SHA-256 checks; the pack''s data is not affected.'
}

# --- beta test plugins -------------------------------------------------------
$plugins = J $GameDir 'BepInEx' 'plugins'
$old = J $plugins 'SEST.BetaAnchorBootstrap.dll'
if (Test-Path -LiteralPath $old -PathType Leaf) {
    $warnings++
    Say '  [!!]   SEST.BetaAnchorBootstrap.dll, the discontinued PR #53 beta test plugin, is installed. With it the beta did not open.' 'Yellow'
    Say ('         Close the game and delete ' + $old + ' (the only file that test installed). SETUP leaves it alone.') 'Yellow'
}
$safe = J $plugins 'SEST.BetaSafeBootstrap.dll'
if (Test-Path -LiteralPath $safe -PathType Leaf) {
    Say '  [note] SEST.BetaSafeBootstrap.dll, the beta Anchor Chain test bootstrap, is installed. It stays inactive unless the game and preloader'
    Say '         files are the ones it was built for and its enable.flag is set. It came with SEST''s beta features: "SEST beta features - remove.cmd"'
    Say '         in the pack folder takes them out, and SETUP''s last step does so itself when the game is on another build than theirs.'
}

# --- the last launch ---------------------------------------------------------
$log = J $GameDir 'BepInEx' 'LogOutput.log'
if (Test-Path -LiteralPath $log -PathType Leaf) {
    $text = $null
    try {
        $fs = New-Object IO.FileStream($log, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
        try { $text = (New-Object IO.StreamReader($fs)).ReadToEnd() } finally { $fs.Dispose() }
    } catch { $text = $null }
    if ($null -ne $text) {
        $why = ''
        $start = $text.LastIndexOf('AnchorChain Preloader started', [StringComparison]::Ordinal)
        $run = $text; if ($start -ge 0) { $run = $text.Substring($start) }
        if ($run.IndexOf('Could not find AnchorChain chainloader', [StringComparison]::Ordinal) -ge 0) { $why = '''Could not find AnchorChain chainloader''' }
        elseif ($start -ge 0 -and $run.IndexOf('Loaded assembly AnchorChain,', [StringComparison]::Ordinal) -lt 0) { $why = 'the Anchor Chain preloader started but never loaded Anchor Chain' }
        if ($why) {
            $warnings++
            Say ('  [!!]   The code mods did not load at the last launch: BepInEx\LogOutput.log says ' + $why + '.') 'Yellow'
            Say '         Anchor Chain loaded none of its mods, so SEST Runtime Fixes, the combat costs and every other Anchor Chain mod were off.' 'Yellow'
            if ($build -eq 'beta') { Say '         This is known on the beta Build 261026; the campaigns and data still play. It needs no action from you.' 'Yellow' }
            elseif ($build -eq 'beta-current') { Say '         This can occur with the stock beta preloader. This SETUP installs the bundled R13 beta features for the reviewed assembly.' 'Yellow' }
            elseif ($build -eq 'beta-previous') { Say '         This is the older 7 November beta image; use its matching R7 candidate for code testing.' 'Yellow' }
            elseif ($build -eq 'stable') { Say '         Start the game once more and run SETUP again; if this is still here, reinstall the preloader from Anchor Chain''s Workshop page.' 'Yellow' }
            else {
                Say '         SEST has no record of Anchor Chain loading on this game build. Its Workshop page is where its author says what a game version needs;' 'Yellow'
                Say '         the pack''s campaigns and data files play without it.' 'Yellow'
            }
        }
    }
}
if ($PassThru) { $warnings }
