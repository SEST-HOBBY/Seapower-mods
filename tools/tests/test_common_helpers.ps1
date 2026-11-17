<#
.SYNOPSIS
    tools\lib\common.ps1's capture helpers on synthetic files: Steam's
    appworkshop acf read for ids, timeupdated and the pending counts; a log
    kept whole or as head and tail with a marker; SEST's Workshop copy found
    or not; a changelog's build line, and what a capture says when the
    installed game is not the exported one.

.DESCRIPTION
    Exit code 1 on any failed check.

        pwsh -File tools/tests/test_common_helpers.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path (Join-Path (Split-Path -Parent $PSScriptRoot) "lib") "common.ps1")
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("sest-common-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$failed = 0

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}

$acfText = @'
"AppWorkshop"
{
	"appid"		"1286220"
	"SizeOnDisk"		"123"
	"NeedsUpdate"		"0"
	"NeedsDownload"		"1"
	"WorkshopItemsInstalled"
	{
		"3373356293"
		{
			"size"		"1000"
			"timeupdated"		"1760000000"
			"manifest"		"111"
		}
		"3380210757"
		{
			"size"		"2000"
			"timeupdated"		"1760400000"
			"manifest"		"222"
		}
	}
	"WorkshopItemDetails"
	{
		"3373356293"
		{
			"manifest"		"111"
			"timeupdated"		"1760000001"
			"timetouched"		"1760000002"
		}
		"3380210757"
		{
			"manifest"		"222"
			"timeupdated"		"1760400000"
		}
		"3999999999"
		{
			"manifest"		"333"
		}
	}
}
'@

try {
    New-Item -ItemType Directory -Force -Path $root | Out-Null

    # --- Read-WorkshopAcf ----------------------------------------------------
    $acf = Join-Path $root "appworkshop_1286220.acf"
    [IO.File]::WriteAllText($acf, $acfText)
    $rec = Read-WorkshopAcf -Path $acf
    Check ($rec.Ids.Count -eq 3 -and $rec.Ids.ContainsKey("3999999999")) "acf: every id block counted, including one with no timeupdated ($($rec.Ids.Count))"
    $epoch = [DateTime]::new(1970, 1, 1, 0, 0, 0, [DateTimeKind]::Utc)
    Check ($rec.Updated.ContainsKey("3373356293") -and $rec.Updated["3373356293"].ToUniversalTime() -eq $epoch.AddSeconds(1760000000)) "acf: timeupdated read from the first block for the id (WorkshopItemsInstalled), as local time"
    Check ($rec.Updated["3380210757"].ToUniversalTime() -eq $epoch.AddSeconds(1760400000)) "acf: second id's timeupdated"
    Check (-not $rec.Updated.ContainsKey("3999999999")) "acf: an id without timeupdated has no date"
    Check ($rec.Size["3380210757"] -eq 2000) "acf: size read"
    Check ($rec.NeedsDownload -eq "1" -and $rec.NeedsUpdate -eq "0") "acf: NeedsDownload / NeedsUpdate read ($($rec.NeedsDownload) / $($rec.NeedsUpdate))"

    # --- Get-LogExcerpt ------------------------------------------------------
    $log = Join-Path $root "LogOutput.log"
    [IO.File]::WriteAllText($log, ((1..12 | ForEach-Object { "line $_" }) -join "`r`n") + "`r`n")
    $x = Get-LogExcerpt -Path $log
    Check ($x.Whole -and $x.Total -eq 12 -and $x.Lines.Count -eq 12 -and $x.Lines[11] -eq "line 12") "log under the cap: kept whole"
    $x = Get-LogExcerpt -Path $log -CapBytes 1 -HeadLines 2 -TailLines 3
    Check (-not $x.Whole -and $x.Total -eq 12 -and $x.Lines.Count -eq 6) "log over the cap: head, marker, tail ($($x.Lines.Count) lines)"
    Check ($x.Lines[0] -eq "line 1" -and $x.Lines[1] -eq "line 2" -and $x.Lines[3] -eq "line 10" -and $x.Lines[5] -eq "line 12") "log over the cap: the first 2 and last 3 lines"
    Check ($x.Lines[2] -like "# ... 7 line(s) left out here*") "log over the cap: the marker counts the lines left out ($($x.Lines[2]))"
    $x = Get-LogExcerpt -Path $log -CapBytes 1 -HeadLines 6 -TailLines 6
    Check ($x.Whole -and $x.Lines.Count -eq 12) "log over the cap but within head+tail lines: kept whole"

    # --- Find-SestWorkshopCopy -----------------------------------------------
    $ws = Join-Path $root "content"
    New-Item -ItemType Directory -Force -Path (Join-Path $ws "3380210757") | Out-Null
    Check ($null -eq (Find-SestWorkshopCopy -WorkshopContentDir $ws)) "no SEST copy: null"
    New-Item -ItemType Directory -Force -Path (Join-Path $ws "3812461539") | Out-Null
    $copy = Find-SestWorkshopCopy -WorkshopContentDir $ws
    Check ($copy -and (Split-Path -Leaf $copy) -eq "3812461539") "SEST copy present: its folder ($copy)"
    Check ($null -eq (Find-SestWorkshopCopy -WorkshopContentDir (Join-Path $root "nowhere"))) "content folder missing: null"
    Check ($SestOwnWorkshopIds -contains "3812461539" -and $SestDistToken -eq "SEST_Integration") "the shared constants"

    # --- Get-ChangelogBuild, Get-GameBuildNote --------------------------------
    $release = Join-Path $root "changelog-090.txt"
    [IO.File]::WriteAllText($release, "Change log`r`n----------`r`n`r`n=====`r`n`r`n11-Nov-2026: 0.9.0 Build 261111 Public Release`r`n-----`r`n[FIX] something`r`n`r`n07-Nov-2026: 0.8.7 Build 261107`r`n")
    $b = Get-ChangelogBuild -Path $release
    Check ($b -and $b.Version -eq "0.9.0" -and $b.Build -eq "261111" -and $b.Release -and
           $b.Line -eq "11-Nov-2026: 0.9.0 Build 261111 Public Release") "changelog head: the first build line, a release"
    $beta = Join-Path $root "changelog-beta.txt"
    [IO.File]::WriteAllText($beta, "Change log`r`n`r`n20-Nov-2026: 0.9.1 Build 261120`r`n[FIX] x`r`n11-Nov-2026: 0.9.0 Build 261111 Public Release`r`n")
    $b = Get-ChangelogBuild -Path $beta
    Check ($b -and $b.Version -eq "0.9.1" -and $b.Build -eq "261120" -and -not $b.Release) "changelog head: a beta's line has no Public Release"
    $old = Join-Path $root "changelog-old.txt"
    [IO.File]::WriteAllText($old, "26-Sep-2026: 0.8.1 Build #260926 (7)`r`n")
    $b = Get-ChangelogBuild -Path $old
    Check ($b -and $b.Version -eq "0.8.1" -and $b.Build -eq "260926") "changelog head: the older 'Build #N' form"
    $empty = Join-Path $root "changelog-empty.txt"
    [IO.File]::WriteAllText($empty, "no build line here`r`n")
    Check ($null -eq (Get-ChangelogBuild -Path $empty)) "changelog without a build line: null"
    Check ($null -eq (Get-ChangelogBuild -Path (Join-Path $root "nowhere.txt"))) "changelog missing: null"

    $note = @(Get-GameBuildNote -InstalledChangelog $release -ExportedChangelog $release)
    Check ($note.Count -eq 2 -and $note[0] -eq "Installed game: 11-Nov-2026: 0.9.0 Build 261111 Public Release" -and
           $note[1] -like "Exported game (mods-source\_vanilla): 11-Nov-2026: 0.9.0*") "same build: two lines, no warning"
    $newer = Join-Path $root "changelog-091.txt"
    [IO.File]::WriteAllText($newer, "20-Nov-2026: 0.9.1 Build 261120 Public Release`r`n11-Nov-2026: 0.9.0 Build 261111 Public Release`r`n")
    $note = @(Get-GameBuildNote -InstalledChangelog $newer -ExportedChangelog $release)
    Check ($note.Count -eq 4 -and $note[2] -like "THE INSTALLED GAME IS NOT THE EXPORTED ONE*" -and
           $note[3] -like "*public release*run the game export next*") "a newer release installed: the warning and the export step"
    $note = @(Get-GameBuildNote -InstalledChangelog $beta -ExportedChangelog $release)
    Check ($note.Count -eq 4 -and $note[2] -like "THE INSTALLED GAME IS NOT THE EXPORTED ONE*" -and
           $note[3] -like "*is a beta: leave mods-source\_vanilla as it is*") "a beta installed: the warning, and the export is left alone"
    $sameBuildOtherDay = Join-Path $root "changelog-redated.txt"
    [IO.File]::WriteAllText($sameBuildOtherDay, "12-Nov-2026: 0.9.0 Build 261111 Public Release`r`n")
    Check (@(Get-GameBuildNote -InstalledChangelog $sameBuildOtherDay -ExportedChangelog $release).Count -eq 2) "the same version and build under another date: no warning"
    $note = @(Get-GameBuildNote -InstalledChangelog (Join-Path $root "nowhere.txt") -ExportedChangelog $empty)
    Check ($note.Count -eq 2 -and $note[0] -like "Installed game: not captured*" -and
           $note[1] -like "*no build line in the export's changelog.txt") "nothing to read: two lines that say so"
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
