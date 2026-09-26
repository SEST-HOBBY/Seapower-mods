<#
.SYNOPSIS
    Clear backup clutter out of the game's user missions and settings folders.

.DESCRIPTION
    Git is the backup for everything this repo deploys, so the copies older
    tooling left in the game folders are only clutter in the mission list:

      user_missions   - any .ini with "backup" in its name (the old
                        "<name> backup-<stamp>" snapshots, and hand-made ones
                        such as "NORTHERN FRONT IIBACKUP"), "<name> - Copy.ini",
                        *.bak / *.old files, and "<name>_briefing" folders
                        whose mission is no longer there.
      settings folder - usersettings.ini.bak_<stamp> copies that
                        set-mod-order.ps1 writes on every sync; the newest
                        -KeepSettingsBackups are kept.

    Nothing else is touched: no mission without one of those marks, no save,
    no log, nothing outside the two folders. Links (junctions, symlinks) are
    never followed or removed. Run it with -WhatIfOnly first; it lists
    exactly what the real run removes.

.EXAMPLE
    # Game closed. Preview, then clean:
    powershell -ExecutionPolicy Bypass -File .\tools\clean-backups.ps1 -WhatIfOnly
    powershell -ExecutionPolicy Bypass -File .\tools\clean-backups.ps1
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir,
    [string]$SettingsDir = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power"),
    [int]$KeepSettingsBackups = 3,
    [switch]$WhatIfOnly
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")

if (-not $StreamingAssetsDir) { $StreamingAssetsDir = Find-StreamingAssets }
if (-not $StreamingAssetsDir) { throw "Sea Power's StreamingAssets folder not found - pass -StreamingAssetsDir" }
$missions = Join-Path $StreamingAssetsDir "user\missions\user_missions"
if (-not (Test-Path -LiteralPath $missions)) { throw "user_missions not found at $missions - stopping" }
if ($KeepSettingsBackups -lt 1) { throw "-KeepSettingsBackups must be at least 1" }

function Test-Link($item) { [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint) }

$targets = @()
foreach ($f in Get-ChildItem -LiteralPath $missions -File -Force) {
    if (Test-Link $f) { continue }
    $isBackup = ($f.Extension -eq ".ini" -and ($f.BaseName -match "backup" -or $f.BaseName -match " - Copy( \(\d+\))?$")) -or
                ($f.Extension -in ".bak", ".old")
    if ($isBackup -and $f.Name -ne "_info.ini") { $targets += $f }
}
foreach ($d in Get-ChildItem -LiteralPath $missions -Directory -Force) {
    if (Test-Link $d) { continue }
    if ($d.Name -notmatch "^(.+)_briefing$") { continue }
    if (Test-Path -LiteralPath (Join-Path $missions ($Matches[1] + ".ini"))) { continue }
    $targets += $d
}
$settingsBackups = @()
if (Test-Path -LiteralPath $SettingsDir) {
    # Stamped yyyyMMdd_HHmmss, so the name sorts by age; the copy keeps the
    # original's write time, so the timestamp on disk does not.
    $settingsBackups = @(Get-ChildItem -LiteralPath $SettingsDir -File -Filter "usersettings.ini.bak_*" |
        Where-Object { -not (Test-Link $_) } | Sort-Object Name -Descending |
        Select-Object -Skip $KeepSettingsBackups)
}

Write-Host "user_missions : $missions"
Write-Host "settings      : $SettingsDir"
$all = @($targets) + @($settingsBackups)
if (-not $all.Count) { Write-Host "`nnothing to clean." -ForegroundColor Green; exit 0 }
foreach ($t in $all) {
    $kind = if ($t.PSIsContainer) { "folder" } else { "file  " }
    if ($WhatIfOnly) { Write-Host ("  would remove {0} {1}" -f $kind, $t.FullName); continue }
    if ($t.PSIsContainer) { Remove-Item -LiteralPath $t.FullName -Recurse -Force }
    else { Remove-Item -LiteralPath $t.FullName -Force }
    Write-Host ("  removed      {0} {1}" -f $kind, $t.FullName)
}
if ($WhatIfOnly) {
    Write-Host ("`n{0} item(s) would go. Re-run without -WhatIfOnly to remove them." -f $all.Count) -ForegroundColor Yellow
} else {
    Write-Host ("`n{0} item(s) removed. The newest {1} settings backup(s) are kept." -f $all.Count, $KeepSettingsBackups) -ForegroundColor Green
}
