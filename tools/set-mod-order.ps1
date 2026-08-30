<#
.SYNOPSIS
    Write the canonical SEST mod order into Sea Power's usersettings.ini.

.DESCRIPTION
    Rewrites the [LoadOrder] section of usersettings.ini from
    data\load-order.tokens.txt (the canonical order). CLOSE THE GAME FIRST -
    it rewrites this file on exit and would clobber the change. The script
    checks and refuses if it finds Sea Power running.

    Safety: a timestamped backup is written next to the file every run; each
    entry's enabled/disabled flag is preserved from your current settings; mods
    present in your settings but not in the canonical list are appended at the
    end (with a warning) rather than dropped; the stale duplicate tail the game
    leaves beyond NumberOfModFiles is cleaned away.

    -AddMissing removes the one manual step left in the loop. A SEST pack you
    have just installed is not in usersettings.ini yet, because the game only
    learns about a folder by scanning at startup - so without this it gets
    skipped, and you have to launch the game, tick it in the Mod Manager, quit,
    and run this again. With -AddMissing, any canonical SEST_* pack that exists
    in StreamingAssets is inserted at its canonical position, enabled, and the
    game picks it up already in the right place.

    A workshop id is still never INVENTED - Steam owns those, and a made-up id
    would be a dead entry. But if Steam has actually downloaded the mod, the id
    is a fact rather than a guess, so -AddMissing now places any canonical
    workshop id it can see in the workshop content folder. That removes the
    launch-the-game-first step for a freshly subscribed mod. It also recovers a
    canonical mod the game has discovered but parked beyond NumberOfModFiles,
    where it was previously invisible.

.EXAMPLE
    # game CLOSED, from the repo root:
    powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -DryRun         # preview
    powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing     # apply
#>
[CmdletBinding()]
param(
    [string]$SettingsPath = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini"),
    [string]$StreamingAssetsDir,
    [switch]$AddMissing,
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")

$tokensPath = Join-Path (Split-Path -Parent $scriptDir) "data\load-order.tokens.txt"

if (-not (Test-Path -LiteralPath $SettingsPath)) { throw "settings file not found: $SettingsPath" }
if (-not (Test-Path -LiteralPath $tokensPath)) { throw "canonical order not found (git pull?): $tokensPath" }

if ((Test-SeaPowerRunning) -and -not $DryRun -and -not $Force) {
    throw ("Sea Power is running. It rewrites usersettings.ini when it exits, " +
           "which would silently undo this. Quit the game and re-run (-Force to override).")
}

$canonical = Get-Content -LiteralPath $tokensPath | Where-Object { $_ -and $_ -notmatch "^#" }
$text = Get-Content -LiteralPath $SettingsPath -Raw

# --- carve out the [LoadOrder] section --------------------------------------
$m = [regex]::Match($text, "(?s)\[LoadOrder\]\r?\n(.*?)(?=\r?\n\[|$)")
if (-not $m.Success) { throw "[LoadOrder] section not found in $SettingsPath" }
$section = $m.Groups[1].Value

$numMatch = [regex]::Match($section, "NumberOfModFiles=(\d+)")
if (-not $numMatch.Success) { throw "NumberOfModFiles not found in [LoadOrder]" }
$activeCount = [int]$numMatch.Groups[1].Value

# current entries in listed order; only the first $activeCount are live.
# BEYOND that count the game leaves two different things: a stale duplicate
# tail (junk, cleaned away below) and, sometimes, a mod it has just discovered
# but parked as inactive. The second kind is real - a newly subscribed mod can
# land there - so a token the canonical order names is picked up wherever it
# sits, while unknown tokens outside the live range stay ignored as before.
$current = [ordered]@{}
$parked = [ordered]@{}
foreach ($em in [regex]::Matches($section, "Mod(\d+)Directory=([^,\r\n]+),(True|False)")) {
    $idx = [int]$em.Groups[1].Value
    $dir = $em.Groups[2].Value
    if ($idx -le $activeCount) {
        if (-not $current.Contains($dir)) { $current[$dir] = $em.Groups[3].Value }
    } elseif (($canonical -contains $dir) -and -not $parked.Contains($dir)) {
        $parked[$dir] = $em.Groups[3].Value
    }
}
foreach ($k in $parked.Keys) {
    if (-not $current.Contains($k)) {
        Write-Host ("found parked beyond NumberOfModFiles, bringing it in: {0}" -f $k) -ForegroundColor Green
        $current[$k] = "True"
    }
}
Write-Host ("current active entries : {0} (NumberOfModFiles={1})" -f $current.Count, $activeCount)
Write-Host ("canonical order        : {0} entries" -f $canonical.Count)

# --- which local packs are actually on disk ---------------------------------
# Only used by -AddMissing; a pack that is not installed must not be added.
$installed = @{}
if ($AddMissing) {
    if (-not $StreamingAssetsDir) { $StreamingAssetsDir = Find-StreamingAssets }
    if (-not $StreamingAssetsDir -or -not (Test-Path -LiteralPath $StreamingAssetsDir)) {
        throw ("-AddMissing needs StreamingAssets and it could not be found. " +
               "Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'.")
    }
    foreach ($d in Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory -ErrorAction SilentlyContinue) {
        $installed[$d.Name] = $true
    }
    Write-Host ("StreamingAssets        : {0}" -f $StreamingAssetsDir)
}

# Which workshop mods has Steam actually downloaded? Used to place a freshly
# subscribed mod without waiting for the game to scan it. The app id is not
# hardcoded: pick the content folder holding the ids this repo tracks.
$workshopIds = @{}
if ($AddMissing) {
    $numericTokens = @($canonical | Where-Object { $_ -match '^\d+$' })
    $bestCount = 0; $bestDir = $null
    foreach ($lib in Get-SteamLibraries) {
        $content = Join-Path $lib "workshop\content"
        if (-not (Test-Path -LiteralPath $content)) { continue }
        foreach ($app in Get-ChildItem -LiteralPath $content -Directory -ErrorAction SilentlyContinue) {
            $hits = @(Get-ChildItem -LiteralPath $app.FullName -Directory -ErrorAction SilentlyContinue |
                      Where-Object { $numericTokens -contains $_.Name }).Count
            if ($hits -gt $bestCount) { $bestCount = $hits; $bestDir = $app.FullName }
        }
    }
    if ($bestDir) {
        foreach ($d in Get-ChildItem -LiteralPath $bestDir -Directory -ErrorAction SilentlyContinue) {
            $workshopIds[$d.Name] = $true
        }
        Write-Host ("Workshop content       : {0} ({1} mods downloaded)" -f $bestDir, $workshopIds.Count)
    }
}

# --- build the final order ---------------------------------------------------
$final = New-Object System.Collections.Generic.List[string]
$flags = @{}
$added = @()
foreach ($tok in $canonical) {
    if ($current.Contains($tok)) {
        $final.Add($tok)
        $flags[$tok] = $current[$tok]
        continue
    }
    # Not in your settings. Only a local pack that really exists on disk may be
    # invented here - a workshop id belongs to Steam, and fabricating one just
    # leaves a dead entry the game has to clean up.
    if ($AddMissing -and $tok -like "SEST_*" -and $installed.ContainsKey($tok)) {
        $final.Add($tok)
        $flags[$tok] = "True"
        $added += $tok
        continue
    }
    # A workshop id is Steam's to own, so it is never INVENTED - but if the mod
    # is sitting downloaded in the workshop content folder, the id is a fact
    # rather than a guess, and waiting for the game to notice it is a manual
    # step for nothing. Only ids we can see on disk are added.
    if ($AddMissing -and $tok -match '^\d+$' -and $workshopIds.ContainsKey($tok)) {
        $final.Add($tok)
        $flags[$tok] = "True"
        $added += $tok
        continue
    }
    if ($tok -like "SEST_*" -and $AddMissing) {
        Write-Warning "canonical pack not installed in StreamingAssets (run install-sest-packs.ps1): $tok"
    } elseif ($tok -match '^\d+$' -and $AddMissing) {
        # Interpolation, not -f: PowerShell binds + tighter than the format
        # operator, so "{0}..." -f $tok + "more" appends into the placeholder.
        Write-Warning ("workshop mod $tok is in the canonical order, but Steam has not " +
                       "downloaded it and the game has never listed it - so there is " +
                       "nothing to place. Subscribe in Steam, let it finish downloading, " +
                       "then re-run.")
    } else {
        Write-Warning "in canonical order but not in your settings (skipped): $tok"
    }
}
foreach ($tok in $current.Keys) {
    if ($final -notcontains $tok) {
        # A numeric token is a workshop id. If it is not in the canonical
        # order it is either freshly subscribed (the game re-adds it on the
        # next launch by itself) or an unsubscribed leftover - and keeping a
        # leftover ENABLED kept the phantom KJ-500 mod alive as entry 144,
        # implicated in the duplicate-key crash on quit. Drop numeric
        # unknowns; keep non-numeric ones (local packs we do not manage).
        if ($tok -match '^\d+$') {
            Write-Warning "dropped stale workshop entry (game re-adds it if still subscribed): $tok"
        } elseif ($tok -like "SEST_*") {
            # Our own packs: the canonical list is authoritative for them, so a
            # SEST_* name that is not in it has been retired - the per-pack
            # folders superseded by SEST_Integration, for instance. The
            # installer deletes those folders; leaving their order entries
            # behind is exactly the phantom-entry state that kept the
            # unsubscribed KJ-500 mod alive.
            Write-Warning "dropped retired SEST pack entry (folder is removed by the installer): $tok"
        } else {
            Write-Warning "in your settings but not in canonical order (appended at end): $tok"
            $final.Add($tok)
            $flags[$tok] = $current[$tok]
        }
    }
}

$newLines = @("[LoadOrder]", "NumberOfModFiles=$($final.Count)")
for ($i = 0; $i -lt $final.Count; $i++) {
    $newLines += ("Mod{0}Directory={1},{2}" -f ($i + 1), $final[$i], $flags[$final[$i]])
}
$newSection = ($newLines -join "`r`n") + "`r`n"
$newText = $text.Substring(0, $m.Index) + $newSection + $text.Substring($m.Index + $m.Length)

Write-Host "`nfirst 25 of the new order:"
$final | Select-Object -First 25 | ForEach-Object -Begin { $i = 0 } -Process {
    $i++
    $mark = if ($added -contains $_) { " <- added, enabled" } elseif ($flags[$_] -eq "False") { " (disabled)" } else { "" }
    Write-Host ("  {0,3}. {1}{2}" -f $i, $_, $mark)
}
if ($added) { Write-Host "`nADDED and enabled: $($added -join ', ')" -ForegroundColor Green }

# A SEST pack sitting disabled is the usual reason "the patch did nothing".
$sestOff = $final | Where-Object { $_ -like "SEST_*" -and $flags[$_] -eq "False" }
if ($sestOff) { Write-Warning "SEST packs present but DISABLED: $($sestOff -join ', ')" }
$disabled = ($flags.GetEnumerator() | Where-Object { $_.Value -eq "False" }).Name
if ($disabled) { Write-Host "`npreserved as DISABLED: $($disabled -join ', ')" }

if ($DryRun) { Write-Host "`nDRY RUN - nothing written. Re-run without -DryRun to apply."; exit 0 }

$backup = "$SettingsPath.bak_$(Get-Date -Format yyyyMMdd_HHmmss)"
Copy-Item -LiteralPath $SettingsPath -Destination $backup
[System.IO.File]::WriteAllText($SettingsPath, $newText)
Write-Host "`nApplied ($($final.Count) entries). Backup: $backup"
Write-Host "Launch Sea Power and open the Mod Manager to verify the order."
