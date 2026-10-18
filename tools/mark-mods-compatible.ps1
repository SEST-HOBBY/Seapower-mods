<#
.SYNOPSIS
    Stop the Mod Manager's start-up warning about mods "not compatible" with
    this game version, by marking each such mod compatible on this PC.

.DESCRIPTION
    The Mod Manager reads [Compatibility] from every mod's _info.ini. Its
    ApproximateVersion check needs MAJOR and MINOR to match the game's
    (tools/check_game_version.py), so a mod whose author last set that line
    for 0.4 to 0.7 is listed as not compatible at every start-up although it
    loads and plays. On 18 Oct 2026 that was 68 of the collection's mods.

    For each Workshop mod whose ApproximateVersion has a different MAJOR.MINOR
    from the installed game's, this rewrites that one line to the game's
    version and puts one comment line above it saying so. Nothing else in the
    file changes: its encoding, byte-order mark and line endings stay as they
    were. The author's own file is kept under
    %LOCALAPPDATA%\SEST\compat-originals, and tools\export-mod-configs.ps1
    exports that kept copy, so mods-source stays the authors' files.

    Left alone: mods whose ApproximateVersion already matches; mods that
    declare only a version range (GreaterThanEqualToVersion/LessThanVersion);
    mods with no [Compatibility] section; SEST's own Workshop item.

    Steam puts a mod's own _info.ini back whenever the mod updates, so
    tools\sync-sest.ps1 runs this every time. It only touches this PC; a
    player who subscribes to the collection still sees the game's warning
    for the same mods, because their files are their authors'.

    Run with the game closed; the Mod Manager reads the files at start-up.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\mark-mods-compatible.ps1
    powershell -ExecutionPolicy Bypass -File .\tools\mark-mods-compatible.ps1 -WhatIfOnly
    # Put every author's file back:
    powershell -ExecutionPolicy Bypass -File .\tools\mark-mods-compatible.ps1 -Restore
#>
[CmdletBinding()]
param(
    [switch]$Restore,
    [switch]$WhatIfOnly,
    [string]$WorkshopContentDir,
    [string]$GameVersion,
    [string]$GameDir,
    [string]$StreamingAssetsDir,
    [string]$BackupDir
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")

if (-not $WorkshopContentDir) { $WorkshopContentDir = Find-WorkshopContent }
if (-not $WorkshopContentDir -or -not (Test-Path -LiteralPath $WorkshopContentDir)) {
    throw "Sea Power's Workshop folder not found. Re-run with -WorkshopContentDir '<...>\steamapps\workshop\content\1286220'"
}
if (-not $BackupDir) { $BackupDir = Get-CompatBackupDir }
$utf8 = New-Object Text.UTF8Encoding($false)

function Read-Text([byte[]]$bytes) {
    $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    $skip = 0
    if ($bom) { $skip = 3 }
    return @{ Bom = $bom; Text = $utf8.GetString($bytes, $skip, $bytes.Length - $skip) }
}

function Write-Text([string]$path, [string]$text, [bool]$bom) {
    [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding($bom)))
}

$mods = @(Get-ChildItem -LiteralPath $WorkshopContentDir -Directory |
    Where-Object { $SestOwnWorkshopIds -notcontains $_.Name } | Sort-Object Name)

# --- Restore ------------------------------------------------------------------
if ($Restore) {
    $put = 0; $stale = 0
    foreach ($kept in @(Get-ChildItem -LiteralPath $BackupDir -Filter "*._info.ini" -File -ErrorAction SilentlyContinue)) {
        $id = $kept.Name.Substring(0, $kept.Name.Length - "._info.ini".Length)
        $live = Join-Path (Join-Path $WorkshopContentDir $id) "_info.ini"
        $marked = (Test-Path -LiteralPath $live) -and
                  ((Read-Text ([IO.File]::ReadAllBytes($live))).Text.IndexOf($SestCompatMarker, [StringComparison]::Ordinal) -ge 0)
        if ($WhatIfOnly) {
            if ($marked) { Write-Host ("  would restore {0}" -f $id) } else { Write-Host ("  would drop    {0} (Steam has since replaced the file)" -f $id) }
            continue
        }
        if ($marked) { [IO.File]::WriteAllBytes($live, [IO.File]::ReadAllBytes($kept.FullName)); $put++ } else { $stale++ }
        Remove-Item -LiteralPath $kept.FullName -Force
    }
    Write-Host ("{0} author's _info.ini put back; {1} kept copies dropped because Steam had already replaced the file." -f $put, $stale)
    return
}

# --- The game's version -----------------------------------------------------
# The first "dd-Mon-yyyy: X.Y.Z Build #N" line of the game's changelog.txt,
# as tools/check_game_version.py reads it.
if (-not $GameVersion) {
    if (-not $GameDir) {
        $sa = $StreamingAssetsDir
        if (-not $sa) { $sa = Find-StreamingAssets }
        # The folder above StreamingAssets, as tools\capture-context.ps1 reads
        # it: changelog.txt is there or one level up.
        if ($sa) { $GameDir = Split-Path -Parent $sa }
    }
    $candidates = @()
    if ($GameDir) {
        $candidates += Join-Path $GameDir "changelog.txt"
        $up = Split-Path -Parent $GameDir
        if ($up) { $candidates += Join-Path $up "changelog.txt" }
    }
    foreach ($chg in $candidates) {
        if (-not (Test-Path -LiteralPath $chg)) { continue }
        $m = [regex]::Match((Get-Content -LiteralPath $chg -Raw), '(?m)^\d{1,2}-[A-Za-z]{3}-\d{4}:\s+(\d+\.\d+\.\d+)\s+Build')
        if ($m.Success) { $GameVersion = $m.Groups[1].Value; break }
    }
}
if (-not $GameVersion -or $GameVersion -notmatch '^\d+\.\d+\.\d+$') {
    throw "The game's version was not found in its changelog.txt. Re-run with -GameVersion X.Y.Z"
}
$gameMinor = ($GameVersion -split '\.')[0..1] -join '.'
Write-Host ("Game version {0}: marking mods whose ApproximateVersion is not {1}.x" -f $GameVersion, $gameMinor)

# --- Mark ---------------------------------------------------------------------
$marked = 0; $already = 0; $fine = 0; $range = 0; $none = 0
foreach ($mod in $mods) {
    $path = Join-Path $mod.FullName "_info.ini"
    if (-not (Test-Path -LiteralPath $path)) { $none++; continue }
    $bytes = [IO.File]::ReadAllBytes($path)
    $r = Read-Text $bytes
    $text = $r.Text
    if ($text.IndexOf($SestCompatMarker, [StringComparison]::Ordinal) -ge 0) { $already++; continue }
    $sec = [regex]::Match($text, '(?ms)^[ \t]*\[Compatibility\][^\r\n]*\r?\n(.*?)(?=^[ \t]*\[|\z)')
    if (-not $sec.Success) { $none++; continue }
    $line = [regex]::Match($sec.Groups[1].Value, '(?m)^([ \t]*ApproximateVersion[ \t]*=[ \t]*)(\d+(?:\.\d+)*)([^\r\n]*?)(\r?)$')
    if (-not $line.Success) { $range++; continue }
    $declared = $line.Groups[2].Value
    if ((($declared -split '\.')[0..1] -join '.') -eq $gameMinor) { $fine++; continue }
    if ($WhatIfOnly) { Write-Host ("  would mark   {0}  ApproximateVersion {1} -> {2}" -f $mod.Name, $declared, $GameVersion); $marked++; continue }

    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    [IO.File]::WriteAllBytes((Join-Path $BackupDir ("{0}._info.ini" -f $mod.Name)), $bytes)
    $eol = "`n"
    if ($line.Groups[4].Value -eq "`r") { $eol = "`r`n" }
    $at = $sec.Groups[1].Index + $line.Index
    $replacement = "{0} (its author's ApproximateVersion was {1}); tools\mark-mods-compatible.ps1 -Restore puts it back{2}{3}{4}{5}{6}" -f
        $SestCompatMarker, $declared, $eol, $line.Groups[1].Value, $GameVersion, $line.Groups[3].Value, $line.Groups[4].Value
    $new = $text.Substring(0, $at) + $replacement + $text.Substring($at + $line.Length)
    Write-Text $path $new $r.Bom
    Write-Host ("  marked       {0}  ApproximateVersion {1} -> {2}" -f $mod.Name, $declared, $GameVersion) -ForegroundColor Yellow
    $marked++
}
$verb = "marked compatible"
if ($WhatIfOnly) { $verb = "would be marked compatible" }
Write-Host ("{0} mod(s) {1}; {2} already marked; {3} already matching {4}.x; {5} declare only a range; {6} with no version line (left alone)." -f
    $marked, $verb, $already, $fine, $gameMinor, $range, $none)
