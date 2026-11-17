# SEST Integration Pack - which Sea Power build is installed, what the pack
# does on it, and whether the code mods loaded at the last launch. SETUP
# runs this in its step 1; run it by hand with the game closed:
#   powershell -ExecutionPolicy Bypass -File .\sest-profile.ps1 -GameDir "<...>\common\Sea Power"
#
# Read only: it changes no file, installs nothing and never stops SETUP.
# SEST's own code plugins are each matched to one game file, so what this
# reports is the SHA-256 of Sea Power_Data\Managed\Seapower-Scripts.dll:
#   3f56861f...  Sea Power 0.9.2 Build 261113 (13 Nov 2026), the public
#                release SEST's bundled R14 features (beta-support\ beside
#                this script) were reviewed for: SETUP's last step installs
#                or updates them unless the player switched them off. SEST
#                Runtime Fixes 1.5.0 and SEST UI Follow-up stay off on it
#                under their own SHA-256 checks.
#   eab2297b...  0.8.7 Build 261021, the build SEST Runtime Fixes 1.5.0 and
#                SEST UI Follow-up are matched to. They can start, each only
#                if its own SHA-256 checks pass.
#   3005bc6d...  0.8.7 Build 261026, a beta of October 2026. The pack's data
#                loads; both plugins stay off under those checks; the
#                Workshop Anchor Chain preloader finds no chainloader, so
#                no Anchor Chain mod loads; the bounded Anchor Chain loader
#                in SEST's source (integration\beta-anchorchain) is a test
#                candidate that nothing installs.
#   499675cd...  the 0.8.7-261107 beta the earlier R13 features were
#                reviewed for; 9b35a7aa... the beta image before it. The
#                bundled R14 features make no code change on either.
#   anything else, Sea Power 0.9.0 (11 Nov 2026) included: not a file any
#                SEST plugin is matched to, so the plugins stay off, and the
#                bundled R14 features make no code change on it. The pack's
#                campaigns and data files do not depend on that file. The
#                note names the version the game's own changelog.txt gives,
#                and the one the pack's data declares (ApproximateVersion in
#                the _info.ini beside this script, when there is one).
# It also names two beta test plugins in BepInEx\plugins: the discontinued
# PR #53 SEST.BetaAnchorBootstrap.dll, with which the beta did not open (one
# [!!] warning, with the step that removes it), and the inert
# SEST.BetaSafeBootstrap.dll (a note). Last, when BepInEx\LogOutput.log
# (rewritten at every launch) shows that Anchor Chain did not load at the
# last launch, 'Could not find AnchorChain chainloader', or no 'Loaded
# assembly AnchorChain,' after the last 'AnchorChain Preloader started', it
# gives one [!!] warning. If SEST's bundled loader ran to the end in that
# launch ('BETA SAFE BOOTSTRAP READY; enable=True', then 'Bounded Anchor
# Chain loader returned to bootstrap.', and no 'Bounded loader failed
# closed' after the READY line), and Anchor Chain logged 'Loaded AnchorChain
# V' with no abort line after it, it started Anchor Chain itself: that is
# one [ok] line, whatever Anchor Chain's own preloader logged. If Anchor
# Chain stopped inside the bounded run, that is one [!!] naming the log
# line. On 0.9.2 the preloader always finds no chainloader, since it looks
# before the Workshop folders are registered; SEST's bootstrap waits for them.
#
# -PassThru: the number of [!!] warnings goes to the pipeline (SETUP adds
# it to its own count). -ReleaseSha256, -StableSha256, -BetaSha256,
# -CurrentBetaSha256 and -PreviousBetaSha256 are for the setup tests; SETUP
# passes none of them.
param(
    [Parameter(Mandatory = $true)][string]$GameDir,
    [switch]$PassThru,
    [string]$ReleaseSha256 = '3f56861f09e867f315b194c81a7a2450154ccc6bb5afb769b4956dfd4a00503a',
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
if ($hash -and $hash -eq $ReleaseSha256.ToLowerInvariant()) { $build = 'release' }
elseif ($hash -and $hash -eq $StableSha256.ToLowerInvariant()) { $build = 'stable' }
elseif ($hash -and $hash -eq $BetaSha256.ToLowerInvariant()) { $build = 'beta' }
elseif ($hash -and $hash -eq $CurrentBetaSha256.ToLowerInvariant()) { $build = 'beta-current' }
elseif ($hash -and $hash -eq $PreviousBetaSha256.ToLowerInvariant()) { $build = 'beta-previous' }
if ($build -eq 'release') {
    Say '  [ok]   game code: Sea Power 0.9.2 Build 261113, the build SEST''s bundled R14 features were reviewed for' 'Green'
    Say '         SETUP''s last step installs or updates them on this build, unless you switched them off.'
    Say '         Without them, SEST Runtime Fixes 1.5.0 and SEST UI Follow-up, matched to Build 261021, stay off on it under their own SHA-256 checks.'
    if ($builtFor) { Say ('        ' + $builtFor) }
} elseif ($build -eq 'stable') {
    Say '  [ok]   game code: Sea Power 0.8.7 Build 261021, the build SEST Runtime Fixes 1.5.0 and SEST UI Follow-up are matched to' 'Green'
    Say '         SEST Runtime Fixes 1.5.0 and SEST UI Follow-up can start, each only if its own SHA-256 checks pass.'
    if ($builtFor) { Say ('        ' + $builtFor) }
} elseif ($build -eq 'beta') {
    Say ('  [note] game code: Sea Power 0.8.7 Build 261026, a beta build of October 2026.' + $builtFor)
    Say '         On this build the pack''s campaigns and data load, but SEST Runtime Fixes 1.5.0 and SEST UI Follow-up stay off under their SHA-256 checks,'
    Say '         and the Workshop Anchor Chain preloader finds no chainloader, so no Anchor Chain mod loads, SEST''s or any other author''s.'
    Say '         A bounded Anchor Chain loader for that beta is in SEST''s source as a test candidate only; nothing installs it.'
} elseif ($build -eq 'beta-current') {
    Say '  [note] game code: Sea Power 0.8.7-261107 (499675cd...), the beta SEST''s earlier R13 features were reviewed for on 9 November 2026.'
    Say '         The bundled features are now R14, for Sea Power 0.9.2 Build 261113 only: SETUP installs none of them on this build and puts the'
    Say ('         normal SEST plugins back if SEST''s beta files are installed. The plugins matched to Build 261021 stay off on it.' + $builtFor)
} elseif ($build -eq 'beta-previous') {
    Say '  [note] older beta assembly: 9b35a7aa..., captured 7 November 2026. R7 targets this image; the plugins matched to Build 261021 remain inactive.'
} elseif ($hash) {
    $says = ''; if ($named) { $says = ' The game''s changelog says ' + $named + '.' }
    Say ('  [note] game code: Seapower-Scripts.dll SHA-256 ' + $hash.Substring(0, 16) + '... is not a file SEST''s own code plugins are matched to.' + $says)
    Say ('         SEST Runtime Fixes and SEST UI Follow-up check that file themselves and stay off on it. The pack''s campaigns and data files do not depend on it.' + $builtFor)
    Say '         SEST''s bundled R14 features are for the Sea Power 0.9.2 Build 261113 file (3f56861f...) only; SETUP does not install them on this one.'
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
        # SEST's bundled loader (SEST.BetaSafeBootstrap.dll) in the same
        # launch: switched on, then returned from Anchor Chain, or failed
        # closed. It returns even when Anchor Chain stopped inside, so a run
        # counts only with Anchor Chain's own completion line and no abort.
        $bounded = $false; $closed = $false; $stopped = $false
        $ready = $run.LastIndexOf('BETA SAFE BOOTSTRAP READY; enable=True', [StringComparison]::Ordinal)
        if ($ready -ge 0) {
            $after = $run.Substring($ready)
            $closed = $after.IndexOf('Bounded loader failed closed', [StringComparison]::Ordinal) -ge 0
            $returned = (-not $closed) -and $after.IndexOf('Bounded Anchor Chain loader returned to bootstrap.', [StringComparison]::Ordinal) -ge 0
            $aborted = $false
            foreach ($stop in @('Anchor Chain loader aborted safely', 'Anchor Chain setup failed', 'Aborting chainload')) {
                if ($after.IndexOf($stop, [StringComparison]::Ordinal) -ge 0) { $aborted = $true }
            }
            $bounded = $returned -and (-not $aborted) -and $after.IndexOf('Loaded AnchorChain V', [StringComparison]::Ordinal) -ge 0
            $stopped = $returned -and (-not $bounded)
        }
        if ($stopped) {
            $warnings++
            Say '  [!!]   The code mods did not all load at the last launch: SEST''s bundled loader started Anchor Chain, but Anchor Chain stopped before it finished loading its mods.' 'Yellow'
            Say '         BepInEx\LogOutput.log gives the reason on its ''Anchor Chain loader aborted safely'', ''Anchor Chain setup failed'' or ''Aborting chainload'' line. Keep that log for review; the campaigns and data still play.' 'Yellow'
        } elseif ($bounded) {
            Say '  [ok]   last launch: SEST''s bundled loader started Anchor Chain and ran its mod loading to the end (BepInEx\LogOutput.log).' 'Green'
            if ($why) { Say ('         Before it, the log says ' + $why + ': that is Anchor Chain''s own preloader, which looks before the Workshop folders are registered. That alone is not a fault.') }
        } elseif ($why) {
            $warnings++
            Say ('  [!!]   The code mods did not load at the last launch: BepInEx\LogOutput.log says ' + $why + '.') 'Yellow'
            Say '         Anchor Chain loaded none of its mods, so SEST Runtime Fixes, the combat costs and every other Anchor Chain mod were off.' 'Yellow'
            if ($closed) { Say '         SEST''s bundled loader then stopped too: the log''s ''Bounded loader failed closed'' line gives the reason. Keep that log for review; the campaigns and data still play.' 'Yellow' }
            elseif ($ready -ge 0) { Say '         SEST''s bundled loader was on but never got back from Anchor Chain (the game may have closed while starting). Start it to the main menu once more, then run SETUP again; if this stays, keep that log for review.' 'Yellow' }
            elseif ($build -eq 'release') {
                if ($run.IndexOf('Safe bootstrap never observed a stable, registered Workshop directory', [StringComparison]::Ordinal) -ge 0) {
                    Say '         SEST''s bundled loader was on but gave up after 60 seconds without seeing Anchor Chain''s Workshop folder registered (the log''s ''Safe bootstrap never observed'' line). Check that Anchor Chain is subscribed and on, start the game to the main menu and wait, then run SETUP again; if this stays, keep that log for review.' 'Yellow'
                } elseif ($run.IndexOf('Beta safe loader failed closed during probe setup', [StringComparison]::Ordinal) -ge 0 -or $run.IndexOf('Beta safe loader INACTIVE', [StringComparison]::Ordinal) -ge 0) {
                    Say '         SEST''s bundled loader stopped before it started: the log''s ''Beta safe loader'' line gives the reason. Keep that log for review; the campaigns and data still play.' 'Yellow'
                } elseif ($run.IndexOf('BETA SAFE BOOTSTRAP READY; enable=False', [StringComparison]::Ordinal) -ge 0) {
                    Say '         SEST''s bundled loader is installed but was not switched on at that launch: staged and waiting for SETUP to switch it on, or switched off by you. SETUP''s last step says which.' 'Yellow'
                } else {
                    Say '         On 0.9.2 Anchor Chain''s own preloader always finds no chainloader; SEST''s bundled loader starts Anchor Chain instead, once SETUP''s last step has installed and switched on the bundled features in the subscribed Workshop item.' 'Yellow'
                }
            }
            elseif ($build -eq 'beta') { Say '         This is known on the beta Build 261026; the campaigns and data still play. It needs no action from you.' 'Yellow' }
            elseif ($build -eq 'beta-current') { Say '         On this beta Anchor Chain''s own preloader finds no chainloader, and SEST''s bundled features, now for Sea Power 0.9.2 Build 261113 only, do not start it here.' 'Yellow' }
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
