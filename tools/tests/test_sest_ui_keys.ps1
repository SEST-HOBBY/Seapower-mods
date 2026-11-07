<#
.SYNOPSIS
    integration\campaign\setup\sest-ui-keys.ps1 unbinds only Contact Log's
    two clashing defaults (ToggleWindow = F6, against Topographic Map's F6;
    RunProbe = F8, against Coordinated Strike Tool's F8 planner), changes no
    other byte, creates nothing, keeps one backup and leaves a file with a
    repeated key alone.

.DESCRIPTION
    Each case writes a com.seapower.contactlog.cfg (or none) into a
    synthetic game folder, runs the script twice and compares bytes. The
    layouts are the 23 the 27 Oct 2026 review tried on GPT's version, plus
    a few more. Exit code 1 on any failed check.

        pwsh -File tools/tests/test_sest_ui_keys.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$keys = Join-Path (Join-Path (Join-Path (Join-Path $repo "integration") "campaign") "setup") "sest-ui-keys.ps1"
$root = Join-Path ([IO.Path]::GetTempPath()) ("sest-uikeys-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$failed = 0
$latin = [Text.Encoding]::GetEncoding(28591)

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}
function Hex([byte[]]$b) { if ($null -eq $b) { return '<none>' }; return [BitConverter]::ToString($b) }
function B([string]$s) { return ,$latin.GetBytes($s) }
$defaults = "## Settings file was created by plugin Contact Log v1.2.0`n## Plugin GUID: com.seapower.contactlog`n`n[Input]`n`n" +
            "## Key that opens and closes the contact log window. [Example: F6, or LeftControl + F6]`n# Setting type: KeyboardShortcut`n# Default value: F6`nToggleWindow = F6`n`n" +
            "## Diagnostic probe [walks types/UI]`n# Setting type: KeyboardShortcut`n# Default value: F8`nRunProbe = F8`n`n" +
            "[Window]`n`n## Window rect`n# Setting type: String`n# Default value: [100, 100, 400, 300]`nRect = [100, 100, 400, 300]`n"
$unbound = $defaults.Replace("ToggleWindow = F6", "ToggleWindow = None").Replace("RunProbe = F8", "RunProbe = None")
function Crlf([string]$s) { return $s.Replace("`n", "`r`n") }
$bom = [byte[]](0xEF, 0xBB, 0xBF)

# name, cfg text before (or $null: no file), expected after (or $null: unchanged), a pre-existing .bak, words the output must hold
$cases = @(
    @('01 no cfg file', $null, $null, $null, ''),
    @('02 no [Input] section', (Crlf "## Plugin GUID: com.seapower.contactlog`n`n[Window]`nRect = [1, 2]`n"), $null, $null, 'neither holds'),
    @('03 defaults, CRLF', (Crlf $defaults), (Crlf $unbound), $null, "unbound (F6 clashes with Topographic Map's F6, the F8 probe with Coordinated Strike Tool's F8 planner): ToggleWindow F6, RunProbe F8 -> None"),
    @('04 defaults, LF', $defaults, $unbound, $null, 'ToggleWindow F6, RunProbe F8 -> None'),
    @('05 defaults, CRLF, BOM', ('BOM' + (Crlf $defaults)), ('BOM' + (Crlf $unbound)), $null, '-> None'),
    @('06 defaults, LF, BOM', ('BOM' + $defaults), ('BOM' + $unbound), $null, '-> None'),
    @('07 custom keys kept', (Crlf $defaults.Replace("ToggleWindow = F6", "ToggleWindow = F9").Replace("RunProbe = F8", "RunProbe = F12")), $null, $null, 'kept as set: ToggleWindow = F9, RunProbe = F12'),
    @('08 already None', (Crlf $unbound), $null, $null, 'neither holds'),
    @('09 ToggleWindow twice', (Crlf $defaults.Replace("ToggleWindow = F6`n", "ToggleWindow = F6`nToggleWindow = F6`n")), $null, $null, 'ToggleWindow is listed more than once'),
    @('10 RunProbe twice', (Crlf $defaults.Replace("RunProbe = F8`n", "RunProbe = F8`nRunProbe = F8`n")), $null, $null, 'RunProbe is listed more than once'),
    @('11 owner PC: ToggleWindow F9 from the 1.3.0 installer', (Crlf $defaults.Replace("ToggleWindow = F6", "ToggleWindow = F9")), (Crlf $defaults.Replace("ToggleWindow = F6", "ToggleWindow = F9").Replace("RunProbe = F8", "RunProbe = None")), $null, 'kept as set: ToggleWindow = F9'),
    @('14 key at the end, no line ending', "[Input]`r`nToggleWindow = F6", "[Input]`r`nToggleWindow = None", $null, 'ToggleWindow F6 -> None'),
    @('15 header at the end, no line ending', "[Window]`r`nRect = [1]`r`n[Input]", $null, $null, 'neither holds'),
    @('16 a longer key and another section', (Crlf "[Input]`nToggleWindowAlt = F6`nToggleWindow = F6`nRunProbe = F8`n[Input2]`nRunProbe = F8`nToggleWindow = F6`n"), (Crlf "[Input]`nToggleWindowAlt = F6`nToggleWindow = None`nRunProbe = None`n[Input2]`nRunProbe = F8`nToggleWindow = F6`n"), $null, '-> None'),
    @('17 indented header', "  [Input]`r`nToggleWindow = F6`r`nRunProbe = F8`r`n", "  [Input]`r`nToggleWindow = None`r`nRunProbe = None`r`n", $null, '-> None'),
    @('18 no spaces, trailing spaces, tabs', "[Input]`r`nToggleWindow=F6   `r`n`tRunProbe`t=`tF8`r`n", "[Input]`r`nToggleWindow=None   `r`n`tRunProbe`t=`tNone`r`n", $null, '-> None'),
    @('19 a byte that is not UTF-8', ("[Input]`r`n## Fen" + [char]0xEA + "tre (cp1252)`r`nToggleWindow = F6`r`nRunProbe = F8`r`n"), ("[Input]`r`n## Fen" + [char]0xEA + "tre (cp1252)`r`nToggleWindow = None`r`nRunProbe = None`r`n"), $null, '-> None'),
    @('20 empty file', '', $null, $null, 'neither holds'),
    @('21 ToggleWindow missing', (Crlf $defaults.Replace("ToggleWindow = F6`n", "")), (Crlf $defaults.Replace("ToggleWindow = F6`n", "").Replace("RunProbe = F8", "RunProbe = None")), $null, 'RunProbe F8 -> None'),
    @('22 header with trailing spaces', "[Input]   `r`nToggleWindow = F6`r`nRunProbe = F8`r`n", "[Input]   `r`nToggleWindow = None`r`nRunProbe = None`r`n", $null, '-> None'),
    @('23 [Input] twice (BepInEx merges them)', "[Input]`r`nToggleWindow = F9`r`n[Other]`r`nX=1`r`n[Input]`r`nRunProbe = F8`r`n", "[Input]`r`nToggleWindow = F9`r`n[Other]`r`nX=1`r`n[Input]`r`nRunProbe = None`r`n", $null, 'kept as set: ToggleWindow = F9'),
    @('30 an older backup is never overwritten', (Crlf $defaults), (Crlf $unbound), "# an earlier state`r`n", '-> None'),
    @('31 a custom key on another F key', "[Input]`r`nToggleWindow = F7`r`nRunProbe = None`r`n", $null, $null, 'kept as set: ToggleWindow = F7'),
    @('32 key names are case-sensitive', "[Input]`r`ntogglewindow = F6`r`nrunprobe = F8`r`n", $null, $null, 'neither holds'),
    @('33 only exactly F6 and F8', "[Input]`r`nToggleWindow = f6`r`nRunProbe = F8 + LeftShift`r`n", $null, $null, 'kept as set: ToggleWindow = f6, RunProbe = F8 + LeftShift'),
    @('34 commented-out default', "[Input]`r`n# ToggleWindow = F6`r`nToggleWindow = F9`r`n", $null, $null, 'kept as set: ToggleWindow = F9'),
    @('35 [input] in another case is another section', "[input]`r`nToggleWindow = F6`r`n", $null, $null, 'neither holds')
)

try {
    foreach ($case in $cases) {
        $name = $case[0]; $before = $case[1]; $after = $case[2]; $oldBak = $case[3]; $says = $case[4]
        $game = Join-Path $root ($name.Substring(0, 2))
        $dir = Join-Path (Join-Path $game "BepInEx") "config"
        $cfg = Join-Path $dir "com.seapower.contactlog.cfg"
        $bak = $cfg + ".sest-ui-keys.bak"
        New-Item -ItemType Directory -Force -Path $game | Out-Null
        $orig = $null
        if ($null -ne $before) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
            if ($before.StartsWith('BOM')) { $orig = [byte[]]($bom + (B $before.Substring(3))) } else { $orig = B $before }
            [IO.File]::WriteAllBytes($cfg, $orig)
        }
        if ($null -ne $oldBak) { [IO.File]::WriteAllBytes($bak, (B $oldBak)) }
        $want = $orig
        if ($null -ne $after) { if ($after.StartsWith('BOM')) { $want = [byte[]]($bom + (B $after.Substring(3))) } else { $want = B $after } }

        $out = ''; $err = $null
        try { $out = (& $keys -GameDir $game *>&1 | Out-String) } catch { $err = $_.Exception.Message }
        Check ($null -eq $err) "$name - runs without an error $err"
        if ($null -eq $before) {
            Check (-not (Test-Path -LiteralPath (Join-Path $game "BepInEx"))) "$name - creates no folder and no file"
            Check ($out.Trim() -eq '') "$name - says nothing"
            continue
        }
        $now = [IO.File]::ReadAllBytes($cfg)
        Check ((Hex $now) -eq (Hex $want)) "$name - bytes as expected"
        if ($says) { Check ($out.Contains($says)) "$name - says '$says' ($($out.Trim() -replace '\s+', ' '))" }
        if ($null -ne $oldBak) {
            Check ((Hex ([IO.File]::ReadAllBytes($bak))) -eq (Hex (B $oldBak))) "$name - the existing backup is left as it was"
        } elseif ($null -ne $after) {
            Check ((Test-Path -LiteralPath $bak) -and (Hex ([IO.File]::ReadAllBytes($bak))) -eq (Hex $orig)) "$name - the file as it was is kept in .sest-ui-keys.bak"
        } else {
            Check (-not (Test-Path -LiteralPath $bak)) "$name - no change, so no backup"
        }
        $files = @(Get-ChildItem -LiteralPath $dir -File | ForEach-Object { $_.Name })
        $expectFiles = 1; if ((Test-Path -LiteralPath $bak)) { $expectFiles = 2 }
        Check ($files.Count -eq $expectFiles) "$name - no other file is written ($($files -join ', '))"
        $bakBytes = $null; if (Test-Path -LiteralPath $bak) { $bakBytes = [IO.File]::ReadAllBytes($bak) }
        & $keys -GameDir $game *>&1 | Out-Null
        Check ((Hex ([IO.File]::ReadAllBytes($cfg))) -eq (Hex $now)) "$name - a second run changes nothing"
        if ($null -ne $bakBytes) { Check ((Hex ([IO.File]::ReadAllBytes($bak))) -eq (Hex $bakBytes)) "$name - a second run keeps the first backup" }
    }

    # A config folder with no Contact Log file: still nothing created.
    $game = Join-Path $root "40"
    $dir = Join-Path (Join-Path $game "BepInEx") "config"
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    & $keys -GameDir $game *>&1 | Out-Null
    Check (@(Get-ChildItem -LiteralPath $dir -Force).Count -eq 0) "40 config folder without the file - nothing created in it"

    # Windows PowerShell 5.1 and ASCII: no PowerShell 7 operators, no non-ASCII byte.
    $tokens = $null; $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($keys, [ref]$tokens, [ref]$errors) | Out-Null
    Check (-not $errors -or $errors.Count -eq 0) "the script parses"
    $raw = [IO.File]::ReadAllBytes($keys)
    Check (@($raw | Where-Object { $_ -gt 0x7E -or ($_ -lt 0x20 -and $_ -ne 0x0D -and $_ -ne 0x0A -and $_ -ne 0x09) }).Count -eq 0) "the script is plain ASCII"
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
