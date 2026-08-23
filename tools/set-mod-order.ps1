<#
.SYNOPSIS
    Write the canonical SEST mod order into Sea Power's usersettings.ini.

.DESCRIPTION
    Rewrites the [LoadOrder] section of usersettings.ini from
    data\load-order.tokens.txt (the canonical 132-entry order). CLOSE THE GAME
    FIRST - it rewrites this file on exit and would clobber the change.

    Safety: a timestamped backup is written next to the file every run; each
    entry's enabled/disabled flag is preserved from your current settings; mods
    present in your settings but not in the canonical list are appended at the
    end (with a warning) rather than dropped; the stale duplicate tail the game
    leaves beyond NumberOfModFiles is cleaned away.

.EXAMPLE
    # game CLOSED, from the repo root:
    powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -DryRun   # preview only
    powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1           # apply
#>
[CmdletBinding()]
param(
    [string]$SettingsPath = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini"),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$tokensPath = Join-Path (Split-Path -Parent $scriptDir) "data\load-order.tokens.txt"

if (-not (Test-Path -LiteralPath $SettingsPath)) { throw "settings file not found: $SettingsPath" }
if (-not (Test-Path -LiteralPath $tokensPath)) { throw "canonical order not found (git pull?): $tokensPath" }

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

# --- build the final order ---------------------------------------------------
$final = New-Object System.Collections.Generic.List[string]
foreach ($tok in $canonical) {
    if ($current.Contains($tok)) { $final.Add($tok) }
    else { Write-Warning "in canonical order but not in your settings (skipped): $tok" }
}
foreach ($tok in $current.Keys) {
    if ($final -notcontains $tok) {
        Write-Warning "in your settings but not in canonical order (appended at end): $tok"
        $final.Add($tok)
    }
}

$newLines = @("[LoadOrder]", "NumberOfModFiles=$($final.Count)")
for ($i = 0; $i -lt $final.Count; $i++) {
    $flag = $current[$final[$i]]
    $newLines += ("Mod{0}Directory={1},{2}" -f ($i + 1), $final[$i], $flag)
}
$newSection = ($newLines -join "`r`n") + "`r`n"
$newText = $text.Substring(0, $m.Index) + $newSection + $text.Substring($m.Index + $m.Length)

Write-Host "`nfirst 25 of the new order:"
$final | Select-Object -First 25 | ForEach-Object -Begin { $i = 0 } -Process { $i++; Write-Host ("  {0,3}. {1}" -f $i, $_) }
$disabled = ($current.GetEnumerator() | Where-Object { $_.Value -eq "False" }).Name
if ($disabled) { Write-Host "`npreserved as DISABLED: $($disabled -join ', ')" }

if ($DryRun) { Write-Host "`nDRY RUN - nothing written. Re-run without -DryRun to apply."; exit 0 }

$backup = "$SettingsPath.bak_$(Get-Date -Format yyyyMMdd_HHmmss)"
Copy-Item -LiteralPath $SettingsPath -Destination $backup
[System.IO.File]::WriteAllText($SettingsPath, $newText)
Write-Host "`nApplied. Backup: $backup"
Write-Host "Launch Sea Power and open the Mod Manager to verify - the list should match data\load-order.preview.txt."
