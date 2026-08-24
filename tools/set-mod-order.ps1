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
    game picks it up already in the right place. Workshop ids are never
    invented this way: Steam owns those, and a made-up id would be a dead entry.

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

# current entries in listed order; only the first $activeCount are live
$current = [ordered]@{}
foreach ($em in [regex]::Matches($section, "Mod(\d+)Directory=([^,\r\n]+),(True|False)")) {
    $idx = [int]$em.Groups[1].Value
    if ($idx -le $activeCount -and -not $current.Contains($em.Groups[2].Value)) {
        $current[$em.Groups[2].Value] = $em.Groups[3].Value
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
    if ($tok -like "SEST_*" -and $AddMissing) {
        Write-Warning "canonical pack not installed in StreamingAssets (run install-sest-packs.ps1): $tok"
    } else {
        Write-Warning "in canonical order but not in your settings (skipped): $tok"
    }
}
foreach ($tok in $current.Keys) {
    if ($final -notcontains $tok) {
        Write-Warning "in your settings but not in canonical order (appended at end): $tok"
        $final.Add($tok)
        $flags[$tok] = $current[$tok]
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
