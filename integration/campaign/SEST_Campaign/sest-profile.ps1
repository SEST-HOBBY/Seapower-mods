# SEST Integration Pack - which Sea Power build is installed, what the pack
# does on it, and whether the code mods loaded at the last launch. SETUP
# runs this in its step 1; run it by hand with the game closed:
#   powershell -ExecutionPolicy Bypass -File .\sest-profile.ps1 -GameDir "<...>\common\Sea Power"
#
# Read only: it changes no file, installs nothing and never stops SETUP.
# The build is told by the SHA-256 of Sea Power_Data\Managed\
# Seapower-Scripts.dll, since the game calls both builds 0.8.7:
#   eab2297b...  0.8.7 Build 261021, the stable build this pack targets.
#                SEST Runtime Fixes 1.5.0 and SEST UI Follow-up can start,
#                each only if its own SHA-256 checks pass.
#   3005bc6d...  0.8.7 Build 261026, the public beta. The pack's data
#                loads; both plugins stay off under those checks; the
#                Workshop Anchor Chain preloader finds no chainloader, so
#                no Anchor Chain mod loads; the bounded Anchor Chain loader
#                in SEST's source (integration\beta-anchorchain) is a test
#                candidate that nothing installs.
#   anything else: not a build SEST has checked; data only.
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
    [string]$CurrentBetaSha256 = '9b35a7aa4f0bd3c78211fb9cf1e3d6398d0dbbc0f787674e843cc9563fd93f53'
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
$build = 'unknown'
if ($hash -and $hash -eq $StableSha256.ToLowerInvariant()) { $build = 'stable' }
elseif ($hash -and $hash -eq $BetaSha256.ToLowerInvariant()) { $build = 'beta' }
elseif ($hash -and $hash -eq $CurrentBetaSha256.ToLowerInvariant()) { $build = 'beta-current' }
if ($build -eq 'stable') {
    Say '  [ok]   game build: Sea Power 0.8.7 Build 261021, the stable build this pack targets' 'Green'
    Say '         SEST Runtime Fixes 1.5.0 and SEST UI Follow-up can start, each only if its own SHA-256 checks pass.'
} elseif ($build -eq 'beta') {
    Say '  [note] game build: Sea Power 0.8.7 Build 261026, the public beta. This pack targets the stable Build 261021.'
    Say '         On the beta the pack''s campaigns and data load, but SEST Runtime Fixes 1.5.0 and SEST UI Follow-up stay off under their SHA-256 checks,'
    Say '         and the Workshop Anchor Chain preloader finds no chainloader, so no Anchor Chain mod loads, SEST''s or any other author''s.'
    Say '         A bounded Anchor Chain loader for the beta is in SEST''s source as a test candidate only; nothing installs it.'
} elseif ($build -eq 'beta-current') {
    Say '  [note] game build: Sea Power 0.8.7 Build 261106, captured 7 November 2026.'
    Say '         The Workshop pack targets stable Build 261021; its data loads, while the stable code plugins remain inactive.'
    Say '         The separate R7 beta repair candidate is required for this build; earlier beta repair candidates remain inactive.'
} elseif ($hash) {
    Say ('  [note] game build not recognised: Seapower-Scripts.dll SHA-256 ' + $hash.Substring(0, 16) + '..., neither Build 261021 nor Build 261026.')
    Say '         SEST has not checked this build: data only. SEST Runtime Fixes and SEST UI Follow-up stay off under their SHA-256 checks until the pack is updated for it.'
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
    Say '         hashes are the beta''s and its enable.flag is set; integration\beta-anchorchain\test.ps1 -Action Remove in SEST''s source takes it out.'
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
            if ($build -eq 'beta') { Say '         This is known on the public beta (Build 261026); the campaigns and data still play. It needs no action from you.' 'Yellow' }
            elseif ($build -eq 'beta-current') { Say '         This is known with the stock Build 261106 beta preloader; the data still loads. Use the separate R7 candidate for beta code testing.' 'Yellow' }
            else { Say '         Start the game once more and run SETUP again; if this is still here, reinstall the preloader from Anchor Chain''s Workshop page.' 'Yellow' }
        }
    }
}
if ($PassThru) { $warnings }
