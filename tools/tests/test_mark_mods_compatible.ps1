<#
.SYNOPSIS
    tools\mark-mods-compatible.ps1 rewrites only the out-of-date
    ApproximateVersion lines, keeps the authors' files, hands them back to the
    exporter, follows a Steam update, and -Restore puts every file back.

.DESCRIPTION
    A synthetic Workshop folder, game folder and backup folder stand in for
    the PC's (-WorkshopContentDir, -GameDir, -BackupDir). Exit code 1 on any
    failed check.

        pwsh -File tools/tests/test_mark_mods_compatible.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$tools = Split-Path -Parent $PSScriptRoot
$mark = Join-Path $tools "mark-mods-compatible.ps1"
. (Join-Path $tools "lib\common.ps1")
$root = Join-Path ([IO.Path]::GetTempPath()) ("sest-compat-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$failed = 0

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}
function Put([string]$path, [byte[]]$bytes) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $path) | Out-Null
    [IO.File]::WriteAllBytes($path, $bytes)
}
function Same([byte[]]$a, [byte[]]$b) {
    if ($a.Length -ne $b.Length) { return $false }
    for ($i = 0; $i -lt $a.Length; $i++) { if ($a[$i] -ne $b[$i]) { return $false } }
    return $true
}
$enc = New-Object Text.UTF8Encoding($false)
function Bytes([string]$s) { return ,$enc.GetBytes($s) }

try {
    $ws = Join-Path $root "content"; $game = Join-Path $root "game"; $bak = Join-Path $root "kept"
    # 1001: out of date, with a byte-order mark and CRLF.
    $old = [byte[]](0xEF, 0xBB, 0xBF) + (Bytes "[Language_en]`r`nName=Old Mod`r`n`r`n[Compatibility]`r`nApproximateVersion=0.4.0`r`n")
    Put (Join-Path $ws "1001\_info.ini") $old
    $fresh = Bytes "[Language_en]`nName=Fresh`n[Compatibility]`nApproximateVersion=0.8.4`n"
    Put (Join-Path $ws "1002\_info.ini") $fresh
    $ranged = Bytes "[Language_en]`nName=Ranged`n[Compatibility]`nGreaterThanEqualToVersion=0.7.0`n"
    Put (Join-Path $ws "1003\_info.ini") $ranged
    $plain = Bytes "[Language_en]`nName=None`n"
    Put (Join-Path $ws "1004\_info.ini") $plain
    $own = Bytes "[Compatibility]`nApproximateVersion=0.5.0`n"
    Put (Join-Path $ws "3812461539\_info.ini") $own
    Put (Join-Path $game "changelog.txt") (Bytes "Change log`n----------`n`n12-Oct-2026: 0.8.6 Build 261014 Public Release`n")

    $out = (& $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-String)
    $live = [IO.File]::ReadAllBytes((Join-Path $ws "1001\_info.ini"))
    $text = $enc.GetString($live)
    Check ($out -match "1 mod\(s\) marked compatible") "one mod marked ($(($out -split "`n" | Select-Object -Last 2) -join ' '))"
    Check ($text -match "(?m)^ApproximateVersion=0\.8\.6\r$") "its line now reads the game's version, CRLF kept"
    Check ($text.Contains($SestCompatMarker)) "the marker line is above it"
    Check ($live[0] -eq 0xEF -and $live[1] -eq 0xBB -and $live[2] -eq 0xBF) "its byte-order mark is kept"
    Check (Same ([IO.File]::ReadAllBytes((Join-Path $bak "1001._info.ini"))) $old) "the author's file is kept, byte for byte"
    Check (Same ([IO.File]::ReadAllBytes((Join-Path $ws "1002\_info.ini"))) $fresh) "a matching 0.8.x mod is untouched"
    Check (Same ([IO.File]::ReadAllBytes((Join-Path $ws "1003\_info.ini"))) $ranged) "a range-only mod is untouched"
    Check (Same ([IO.File]::ReadAllBytes((Join-Path $ws "1004\_info.ini"))) $plain) "a mod with no version line is untouched"
    Check (Same ([IO.File]::ReadAllBytes((Join-Path $ws "3812461539\_info.ini"))) $own) "SEST's own Workshop item is untouched"

    $export = Get-AuthorModFileBytes -ModId "1001" -Path (Join-Path $ws "1001\_info.ini") -Rel "_info.ini" -BackupDir $bak
    Check (Same $export $old) "the exporter is handed the author's file"
    $export2 = Get-AuthorModFileBytes -ModId "1002" -Path (Join-Path $ws "1002\_info.ini") -Rel "_info.ini" -BackupDir $bak
    Check (Same $export2 $fresh) "an unmarked mod exports as it is"

    $again = (& $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-String)
    Check ($again -match "0 mod\(s\) marked compatible; 1 already marked") "a second run changes nothing"

    # Steam updates 1001: the author's new file replaces the marked one.
    $v2 = Bytes "[Language_en]`r`nName=Old Mod v2`r`n[Compatibility]`r`nApproximateVersion=0.4.1`r`n"
    Put (Join-Path $ws "1001\_info.ini") $v2
    & $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-Null
    Check (Same ([IO.File]::ReadAllBytes((Join-Path $bak "1001._info.ini"))) $v2) "after a Steam update the kept copy is the new author file"

    $r = (& $mark -WorkshopContentDir $ws -BackupDir $bak -Restore *>&1 | Out-String)
    Check (Same ([IO.File]::ReadAllBytes((Join-Path $ws "1001\_info.ini"))) $v2) "-Restore puts the author's file back"
    Check (-not (Test-Path -LiteralPath (Join-Path $bak "1001._info.ini"))) "-Restore drops the kept copy"

    $noGame = $null
    try { & $mark -WorkshopContentDir $ws -GameDir (Join-Path $root "nowhere") -BackupDir $bak *>&1 | Out-Null }
    catch { $noGame = $_.Exception.Message }
    Check ($noGame -match "version was not found") "no changelog: it says so instead of guessing"
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
