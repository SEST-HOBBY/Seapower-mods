<#
.SYNOPSIS
    tools\mark-mods-compatible.ps1 rewrites only the ApproximateVersion
    values the game rejects as made for an older game version (and SETUP's
    reviewed newer ones), names and leaves the rest, keeps the authors'
    files, hands them back to the exporter, follows a Steam update and a game
    update, and -Restore puts every file back byte for byte.

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
    Check ($text -match "(?m)^ApproximateVersion=0\.8\.0\r$") "its value is now the game's MAJOR.MINOR.0, CRLF kept"
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

    # --- The game's own rule, on 0.8.7 ------------------------------------
    $ws = Join-Path $root "content2"; $bak = Join-Path $root "kept2"
    $marker = $SestCompatMarker
    function Note([string]$was, [string]$eol) { return "$marker (its author's ApproximateVersion was $was); tools\mark-mods-compatible.ps1 -Restore puts it back$eol" }
    $files = [ordered]@{}
    $files["2001"] = Bytes "[Language_en]`nName=Older`n`n[Compatibility]`nApproximateVersion=0.7.3`n"
    $files["2002"] = Bytes "[Language_en]`r`nName=Partial`r`n[Compatibility]`r`nApproximateVersion=0.4`r`n"
    $p = 0
    foreach ($v in "0.8.0", "0.8.1", "0.8.2", "0.8.3", "0.8.4", "0.8.5", "0.8.6", "0.8.7") { $files["21" + $p] = Bytes "[Compatibility]`nApproximateVersion=$v`n"; $p++ }
    $files["2201"] = Bytes "[Language_en]`nName=Newer Patch`n[Compatibility]`nApproximateVersion=0.8.8`n"
    $redfor = Bytes "[Language_en]`r`nName=THE REDFOR MOD`r`nDescription=by SKIBIDI RIZZLER`r`n`r`n`r`n`r`n[Compatibility]`r`n;ApproximateVersion is the second check and will override all statements below. This checks MAJOR and MINOR match but will accept higher PATCH.`r`n;Would recommend this as a default case for starters.`r`nApproximateVersion=0.8.8`r`n"
    $files["3732654992"] = $redfor
    $files["2301"] = Bytes "[Compatibility]`nExactVersion=0.8.6`nApproximateVersion=0.7.0`n"
    $files["2302"] = Bytes "[Compatibility]`nApproximateVersion=abc`n"
    $files["2303"] = Bytes "[Compatibility]`nApproximateVersion=0.8.99999999999`n"
    $files["2304"] = Bytes "[Compatibility]`nApproximateVersion=`n"
    $files["2305"] = Bytes "[Compatibility]`n  approximateversion  =  0.7.0   ; old`n"
    $files["2306"] = [byte[]]((Bytes "[Language_en]`r`nName=Caf") + [byte[]](0xE9) + (Bytes "`r`n[Compatibility]`r`nApproximateVersion=0.6.0`r`n"))
    $files["2307"] = Bytes "[Compatibility]`nLessThanVersion=0.8.7`n"
    foreach ($k in $files.Keys) { Put (Join-Path $ws "$k\_info.ini") $files[$k] }
    Put (Join-Path $ws "3732654992\units\x.ini") (Bytes "[General]`n")
    Put (Join-Path $game "changelog.txt") (Bytes "21-Oct-2026: 0.8.7 Build 261021 Public Release`n")
    function Now([string]$id) { return ,[IO.File]::ReadAllBytes((Join-Path $ws "$id\_info.ini")) }
    function Kept([string]$id) { $k = Join-Path $bak "$id._info.ini"; if (Test-Path -LiteralPath $k) { return ,[IO.File]::ReadAllBytes($k) }; return $null }

    $out = (& $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-String)
    Check ($out -match "4 mod\(s\) marked compatible") "on 0.8.7: four mods marked ($(($out -split "`n" | Select-Object -Last 2) -join ' '))"
    Check ((Same (Now "2001") (Bytes ("[Language_en]`nName=Older`n`n[Compatibility]`n" + (Note "0.7.3" "`n") + "ApproximateVersion=0.8.0`n"))) -and (Same (Kept "2001") $files["2001"])) "an older 0.7.x mod is marked 0.8.0 and its file kept"
    Check ((Same (Now "2002") (Bytes ("[Language_en]`r`nName=Partial`r`n[Compatibility]`r`n" + (Note "0.4" "`r`n") + "ApproximateVersion=0.8.0`r`n"))) -and (Same (Kept "2002") $files["2002"])) "a partial '0.4' is marked, CRLF kept"
    $same = $true; foreach ($k in "210", "211", "212", "213", "214", "215", "216", "217") { if (-not (Same (Now $k) $files[$k]) -or $null -ne (Kept $k)) { $same = $false } }
    Check $same "0.8.0 to 0.8.7 are left as they are"
    Check ((Same (Now "2201") $files["2201"]) -and $null -eq (Kept "2201") -and $out -match "left alone   2201  made for a newer game version \(0\.8\.8\)") "a 0.8.8 mod not reviewed is named and left alone"
    $redforMarked = Bytes ([Text.Encoding]::UTF8.GetString($redfor).Replace("ApproximateVersion=0.8.8`r`n", (Note "0.8.8" "`r`n") + "ApproximateVersion=0.8.0`r`n"))
    Check ((Same (Now "3732654992") $redforMarked) -and (Same (Kept "3732654992") $redfor) -and $out -match "marked       3732654992.*reviewed") "THE REDFOR MOD's reviewed 0.8.8 is marked 0.8.0"
    Check ((Same (Now "2301") $files["2301"]) -and $out -match "2301.*ExactVersion=0\.8\.6") "an ExactVersion the game rejects is named and left alone, ApproximateVersion and all"
    Check ((Same (Now "2302") $files["2302"]) -and $out -match "2302.*ApproximateVersion=abc") "an unreadable value is named and left alone"
    Check ((Same (Now "2303") $files["2303"]) -and $out -match "2303  made for a newer game version") "a 20-digit patch does not crash it; it counts as newer"
    Check (Same (Now "2304") $files["2304"]) "an empty value is what the game ignores: left alone"
    Check (Same (Now "2305") (Bytes ("[Compatibility]`n" + (Note "0.7.0" "`n") + "  approximateversion  =  0.8.0   ; old`n"))) "spaces, key case and an inline comment are kept around the new value"
    Check ((Same (Now "2306") $files["2306"]) -and $out -match "2306.*not UTF-8 text") "a file that is not UTF-8 is named and left alone"
    Check ((Same (Now "2307") $files["2307"]) -and $out -match "2307.*LessThanVersion=0\.8\.7") "a range that excludes the game is named and left alone"

    $snap = @{}; foreach ($k in $files.Keys) { $snap[$k] = Now $k }
    $again = (& $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-String)
    $same = $true; foreach ($k in $files.Keys) { if (-not (Same (Now $k) $snap[$k])) { $same = $false } }
    Check ($same -and $again -match "0 mod\(s\) marked compatible; 4 already marked") "a second run on 0.8.7 changes nothing"

    # REDFOR as GPT's reviewed-compat script left it on the owner's PC: its own
    # marker (same prefix) over ApproximateVersion=0.8.7, the author's file kept.
    $gpt = Bytes ([Text.Encoding]::UTF8.GetString($redfor).Replace("ApproximateVersion=0.8.8", "$marker (reviewed REDFOR 0.8.8 declaration on native 0.8.7); SETUP -RestoreModFiles puts it back`r`nApproximateVersion=0.8.7"))
    Put (Join-Path $ws "3732654992\_info.ini") $gpt
    $o3 = (& $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-String)
    Check ((Same (Now "3732654992") $gpt) -and (Same (Kept "3732654992") $redfor) -and $o3 -match "0 mod\(s\) marked compatible; 4 already marked") "REDFOR marked by GPT's script counts as already marked"

    # The game moves to 0.9.0: every marked file is listed again and re-marked
    # (value only, kept copies untouched); the 0.8.x mods are now older too.
    Put (Join-Path $game "changelog.txt") (Bytes "01-Jan-2027: 0.9.0 Build 270101 Public Release`n")
    $o4 = (& $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-String)
    Check ((Same (Now "2001") (Bytes ("[Language_en]`nName=Older`n`n[Compatibility]`n" + (Note "0.7.3" "`n") + "ApproximateVersion=0.9.0`n"))) -and (Same (Kept "2001") $files["2001"])) "on 0.9.0: a marked mod gets only its value rewritten; its kept file stays the author's"
    Check ((Same (Now "3732654992") (Bytes ([Text.Encoding]::UTF8.GetString($gpt).Replace("ApproximateVersion=0.8.7", "ApproximateVersion=0.9.0")))) -and (Same (Kept "3732654992") $redfor)) "on 0.9.0: GPT's REDFOR mark is re-marked, the author's 0.8.8 still kept"
    Check ((Same (Now "217") (Bytes ("[Compatibility]`n" + (Note "0.8.7" "`n") + "ApproximateVersion=0.9.0`n"))) -and (Same (Kept "217") $files["217"])) "on 0.9.0: a 0.8.7 mod is now older and marked"
    Check ($o4 -match "14 mod\(s\) marked compatible \(4 of them marked before") "on 0.9.0: 14 marked, 4 of them again ($(($o4 -split "`n" | Select-Object -Last 2) -join ' '))"

    # And with a .dll in it, a reviewed mod is no longer marked.
    Put (Join-Path $game "changelog.txt") (Bytes "21-Oct-2026: 0.8.7 Build 261021 Public Release`n")
    & $mark -WorkshopContentDir $ws -BackupDir $bak -Restore *>&1 | Out-Null
    $same = $true; foreach ($k in $files.Keys) { if ($k -ne "3732654992" -and -not (Same (Now $k) $files[$k])) { $same = $false } }
    Check ($same -and (Same (Now "3732654992") $redfor) -and @(Get-ChildItem -LiteralPath $bak -File).Count -eq 0) "-Restore puts every file back byte for byte, REDFOR's as its author shipped it"
    Put (Join-Path $ws "3732654992\plugins\Code.DLL") (Bytes "MZ")
    $o5 = (& $mark -WorkshopContentDir $ws -GameDir $game -BackupDir $bak *>&1 | Out-String)
    Check ((Same (Now "3732654992") $redfor) -and $o5 -match "3732654992  made for a newer game version \(0\.8\.8, now holds a \.dll\)") "a reviewed mod that now holds a .dll is left alone and named"
    & $mark -WorkshopContentDir $ws -BackupDir $bak -Restore *>&1 | Out-Null
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
