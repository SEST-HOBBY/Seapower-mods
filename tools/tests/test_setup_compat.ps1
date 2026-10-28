<#
.SYNOPSIS
    The pack's SETUP (integration\campaign\setup\sest-setup.ps1), run end to
    end on a stand-in PC: step 3 marks exactly the mods the game rejects as
    made for an older game version (a value the game cannot read judged by
    the two or three numbers it starts with) and the reviewed REDFOR, names
    and leaves the rest, judges its own marks again after a game update (up
    a version, and back down again), gives REDFOR's own file back once it
    holds a .dll, and turns a mod file it cannot read into one warning;
    -RestoreModFiles puts every file back byte for byte, and one that stops
    part-way says changes were made; -KeepDir moves the kept files; step 4
    runs sest-ui-keys.ps1 only when it and Contact Log's settings exist, a
    failure there is a warning, not a stop, and Contact Log downloaded with
    no settings yet is one note.

.DESCRIPTION
    Builds a synthetic Steam folder (game, Workshop items, the pack with
    this repository's SETUP files in it) and settings file under the temp
    folder, points SETUP at them through SEST_STEAM_ROOT, SEST_SETTINGS and
    LOCALAPPDATA, and runs it in a child PowerShell (the same executable as
    this one). Also checks that the setup folder's scripts are ASCII with
    CRLF line endings and use no PowerShell 7-only operator, since players
    run them in Windows PowerShell 5.1. Exit code 1 on any failed check.

        pwsh -File tools/tests/test_setup_compat.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$src = Join-Path (Join-Path (Join-Path $repo "integration") "campaign") "setup"
$root = Join-Path ([IO.Path]::GetTempPath()) ("sest-setup-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$exe = (Get-Process -Id $PID).Path
$failed = 0
$enc = New-Object Text.UTF8Encoding($false)
$marker = '; SEST marked this mod compatible'

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}
function J { $p = [string]$args[0]; for ($k = 1; $k -lt $args.Count; $k++) { $p = [IO.Path]::Combine($p, [string]$args[$k]) }; $p }
function Put([string]$path, [byte[]]$bytes) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $path) | Out-Null
    [IO.File]::WriteAllBytes($path, $bytes)
}
function Bytes([string]$s) { return ,$enc.GetBytes($s) }
function Hex([byte[]]$b) { if ($null -eq $b) { return '<none>' }; return [BitConverter]::ToString($b) }

# --- the setup folder's own bytes --------------------------------------------
foreach ($f in @(Get-ChildItem -LiteralPath $src -File)) {
    $b = [IO.File]::ReadAllBytes($f.FullName)
    $bad = 0; $lf = 0
    for ($i = 0; $i -lt $b.Length; $i++) {
        if ($b[$i] -gt 0x7E -or ($b[$i] -lt 0x20 -and $b[$i] -ne 0x0D -and $b[$i] -ne 0x0A -and $b[$i] -ne 0x09)) { $bad++ }
        if ($b[$i] -eq 0x0A -and ($i -eq 0 -or $b[$i - 1] -ne 0x0D)) { $lf++ }
        if ($b[$i] -eq 0x0D -and ($i + 1 -ge $b.Length -or $b[$i + 1] -ne 0x0A)) { $lf++ }
    }
    Check ($bad -eq 0) "$($f.Name) is plain ASCII"
    Check ($lf -eq 0 -and $b.Length -gt 0 -and $b[$b.Length - 1] -eq 0x0A) "$($f.Name) has CRLF line endings throughout"
    if ($f.Extension -eq '.ps1') {
        $tokens = $null; $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$tokens, [ref]$errors) | Out-Null
        Check (-not $errors -or $errors.Count -eq 0) "$($f.Name) parses"
        $ps7 = @($tokens | Where-Object { @('AndAnd', 'OrOr', 'QuestionQuestion', 'QuestionQuestionEquals', 'QuestionDot', 'QuestionLBracket', 'QuestionMark') -contains [string]$_.Kind })
        Check ($ps7.Count -eq 0) "$($f.Name) uses no PowerShell 7-only operator ($(($ps7 | ForEach-Object { $_.Text + ' line ' + $_.Extent.StartLineNumber }) -join ', '))"
    }
}

# --- a stand-in PC ------------------------------------------------------------
$steam = J $root "Steam"
$apps = J $steam "steamapps"
$game = J $apps "common" "Sea Power"
$content = J $apps "workshop" "content" "1286220"
$pack = J $content "3812461539"
$settings = J $root "LocalLow" "usersettings.ini"
$keep = J $root "appdata" "SEST" "compat-originals"
$cl = J $game "BepInEx" "config" "com.seapower.contactlog.cfg"
Put (J $apps "appmanifest_1286220.acf") (Bytes "`"AppState`"`n{`n`t`"installdir`"`t`t`"Sea Power`"`n}`n")
Put (J $game "Sea Power.exe") (Bytes "x")
Put (J $game "winhttp.dll") (Bytes "x")
Put (J $game "BepInEx" "plugins" "AnchorChain.dll") (Bytes "x")
function GameVersion([string]$line) { Put (J $game "changelog.txt") (Bytes "Change log`r`n----------`r`n`r`n$line`r`n----`r`n") }
GameVersion "21-Oct-2026: 0.8.7 Build 261021 Public Release"
Put (J $pack "campaigns" "sest-southern-watch" "campaign.ini") (Bytes "x")
foreach ($n in 'sest-setup.ps1', 'sest-ui-keys.ps1') { Put (J $pack $n) ([IO.File]::ReadAllBytes((J $src $n))) }
$clBefore = Bytes "[Input]`r`n# Default value: F6`r`nToggleWindow = F6`r`n`r`n# Default value: F8`r`nRunProbe = F8`r`n`r`n[Window]`r`nRect = [100, 100, 400, 300]`r`n"
Put $cl $clBefore

$redfor = "[Language_en]`r`nName=THE REDFOR MOD`r`nDescription=by SKIBIDI RIZZLER`r`n`r`n`r`n`r`n[Compatibility]`r`n" +
          ";ApproximateVersion is the second check and will override all statements below. This checks MAJOR and MINOR match but will accept higher PATCH.`r`n" +
          ";Would recommend this as a default case for starters.`r`nApproximateVersion=0.8.8`r`n"
# id, name, _info.ini bytes, what step 3 does on 0.8.7: 'mark' (old line -> new line, declared) or 'keep'
$mods = New-Object System.Collections.Generic.List[object]
function Mod([string]$id, [string]$name, [byte[]]$info, [string]$old, [string]$new, [string]$was) { $mods.Add(@{ Id = $id; Name = $name; Info = $info; Old = $old; New = $new; Was = $was }) }
Mod '9000001' 'Old LF' (Bytes "[Language_en]`nName=Old LF`n`n[Compatibility]`nApproximateVersion=0.7.2`n") "ApproximateVersion=0.7.2`n" "ApproximateVersion=0.8.0`n" '0.7.2'
Mod '9000002' 'Partial CRLF' (Bytes "[Language_en]`r`nName=Partial CRLF`r`n`r`n[Compatibility]`r`nApproximateVersion=0.4`r`n") "ApproximateVersion=0.4`r`n" "ApproximateVersion=0.8.0`r`n" '0.4'
Mod '9000003' 'Old BOM' ([byte[]](@(0xEF, 0xBB, 0xBF) + (Bytes "[Compatibility]`nApproximateVersion=0.6.1`n[Other]`nX=1`n"))) "ApproximateVersion=0.6.1`n" "ApproximateVersion=0.8.0`n" '0.6.1'
Mod '9000004' 'Old Spaced' (Bytes "[Compatibility] ; c`r`n`tapproximateversion =  0.7.10  // old`r`n") "`tapproximateversion =  0.7.10  // old`r`n" "`tapproximateversion =  0.8.0  // old`r`n" '0.7.10'
Mod '9000005' 'Odd Older' (Bytes "[Compatibility]`r`nApproximateVersion=0.8.07`r`n") "ApproximateVersion=0.8.07`r`n" "ApproximateVersion=0.8.0`r`n" '0.8.07'
Mod '9000006' 'Four Part Older' (Bytes "[Compatibility]`nApproximateVersion=0.8.7.1`n") "ApproximateVersion=0.8.7.1`n" "ApproximateVersion=0.8.0`n" '0.8.7.1'
$p = 0
foreach ($v in '0.8.0', '0.8.1', '0.8.2', '0.8.3 // fine', '0.8.4', '0.8.5', '0.8.6', '0.8.7') { Mod ('900010' + $p) ('Current ' + $v) (Bytes "[Compatibility]`nApproximateVersion=$v`n") $null $null $null; $p++ }
Mod '9000201' 'Newer Patch' (Bytes "[Compatibility]`nApproximateVersion=0.8.8`n") $null $null $null
Mod '9000202' 'Newer Minor' (Bytes "[Compatibility]`r`nApproximateVersion=0.9.0`r`n") $null $null $null
Mod '9000203' 'Huge Patch' (Bytes "[Compatibility]`nApproximateVersion=0.8.99999999999`n") "ApproximateVersion=0.8.99999999999`n" "ApproximateVersion=0.8.0`n" '0.8.99999999999'
Mod '9000204' 'Partial Newer' (Bytes "[Compatibility]`nApproximateVersion=0.9`n") $null $null $null
Mod '9000205' 'Odd Newer' (Bytes "[Compatibility]`nApproximateVersion=0.8.08`n") $null $null $null
Mod '9000206' 'Four Part Newer' (Bytes "[Compatibility]`r`nApproximateVersion=0.8.8.1`r`n") $null $null $null
Mod '9000301' 'Exact' (Bytes "[Compatibility]`nExactVersion=0.8.6`nApproximateVersion=0.7.0`n") $null $null $null
Mod '9000302' 'Unreadable' (Bytes "[Compatibility]`nApproximateVersion=v-next`n") $null $null $null
Mod '9000303' 'Not UTF8' ([byte[]]((Bytes "[Language_en]`r`nName=Caf") + [byte[]](0xE9) + (Bytes "`r`n[Compatibility]`r`nApproximateVersion=0.6.0`r`n"))) $null $null $null
Mod '9000304' 'Range Out' (Bytes "[Compatibility]`nGreaterThanEqualToVersion=0.9.0`n") $null $null $null
Mod '9000305' 'Range In' (Bytes "[Compatibility]`nGreaterThanEqualToVersion=0.8.3`nLessThanVersion=0.9.0`n") $null $null $null
Mod '9000306' 'Empty Value' (Bytes "[Compatibility]`nApproximateVersion=   `n") $null $null $null
Mod '9000307' 'No Section' (Bytes "[Language_en]`nName=No Section`n") $null $null $null
Mod '3732654992' 'THE REDFOR MOD' (Bytes $redfor) "ApproximateVersion=0.8.8`r`n" "ApproximateVersion=0.8.0`r`n" '0.8.8'
for ($k = 0; $k -lt 40; $k++) { Mod ('95000' + $k.ToString('00')) ('Filler ' + $k) (Bytes "[Language_en]`nName=Filler`n") $null $null $null }
$lo = New-Object System.Collections.Generic.List[string]
$lo.Add('   #  workshop id   mod'); $lo.Add(''); $lo.Add('   1. (this pack)   SEST_Integration')
for ($k = 0; $k -lt $mods.Count; $k++) {
    $m = $mods[$k]
    $lo.Add(('{0,4}. {1,-13} {2}' -f ($k + 2), $m.Id, $m.Name))
    Put (J $content $m.Id '_info.ini') $m.Info
    Put (J $content $m.Id 'units' 'x.ini') (Bytes "[General]`n")
}
Put (J $pack "LOAD-ORDER.txt") (Bytes (($lo -join "`r`n") + "`r`n"))
Put $settings (Bytes "[General]`r`nX=1`r`n[LoadOrder]`r`nNumberOfModFiles=1`r`nMod1Directory=9000001,True`r`n`r`n[Other]`r`nY=2`r`n")

function Live([string]$id) { return ,[IO.File]::ReadAllBytes((J $content $id '_info.ini')) }
function Kept([string]$id) { $k = J $keep ($id + '._info.ini'); if (Test-Path -LiteralPath $k) { return ,[IO.File]::ReadAllBytes($k) }; return $null }
function Text([byte[]]$b) { $o = 0; if ($b.Length -ge 3 -and $b[0] -eq 0xEF) { $o = 3 }; return $enc.GetString($b, $o, $b.Length - $o) }
function Expected($m, [string]$value) {
    # The author's file with the marker above the version line and the value replaced.
    $eol = "`n"; if ($m.Old.EndsWith("`r`n")) { $eol = "`r`n" }
    $t = (Text $m.Info).Replace($m.Old, $marker + " (its author's ApproximateVersion was " + $m.Was + "); SETUP -RestoreModFiles puts it back" + $eol + $m.New.Replace('0.8.0', $value))
    $b = Bytes $t
    if ($m.Info[0] -eq 0xEF) { $b = [byte[]](@(0xEF, 0xBB, 0xBF) + $b) }
    return ,$b
}
function Setup([string[]]$more) {
    $a = @('-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', (J $pack 'sest-setup.ps1')) + $more
    $o = (& $exe @a 2>&1 | Out-String) -replace ([string][char]27 + '\[[0-9;]*m'), ''
    return @{ Out = $o; Code = $LASTEXITCODE }
}
function AllAsShipped {
    foreach ($m in $mods) { if ((Hex (Live $m.Id)) -ne (Hex $m.Info)) { return $m.Id } }
    return ''
}

$saved = @{ SEST_STEAM_ROOT = $env:SEST_STEAM_ROOT; SEST_SETTINGS = $env:SEST_SETTINGS; LOCALAPPDATA = $env:LOCALAPPDATA }
try {
    $env:SEST_STEAM_ROOT = $steam; $env:SEST_SETTINGS = $settings; $env:LOCALAPPDATA = J $root "appdata"

    # 1. First run on 0.8.7.
    $r = Setup @()
    Check ($r.Code -eq 0 -and $r.Out -match 'All done') "run 1 on 0.8.7 finishes with no warning (exit $($r.Code))"
    Check ($r.Out -match '\[done\] 7 mod\(s\) made for an older game version marked compatible with 0\.8\.7 \(the start-up warning about them stops\)') "run 1 marks the seven older mods (0.8.07 and 0.8.7.1, which the game cannot read, and an 11-digit patch its pattern takes but cannot hold, among them)"
    Check ($r.Out -match '\[done\] made for a newer game version but reviewed, so marked compatible with 0\.8\.7: THE REDFOR MOD') "run 1 marks the reviewed REDFOR"
    Check ($r.Out -match 'Not marked, made for a newer game version than 0\.8\.7 \(listed as not compatible until the game catches up\): Newer Patch \(0\.8\.8\), Newer Minor \(0\.9\.0\), Partial Newer \(0\.9\), Odd Newer \(0\.8\.08\), Four Part Newer \(0\.8\.8\.1\)\r?\n') "run 1 names the newer mods in one line, 0.8.08 and 0.8.8.1 among them"
    Check ($r.Out -match 'Not marked, declared in a way SETUP does not change \(listed as not compatible\): Exact \(ExactVersion=0\.8\.6\), Unreadable \(ApproximateVersion=v-next\), Not UTF8 \(0\.6\.0, not UTF-8 text\), Range Out \(GreaterThanEqualToVersion=0\.9\.0\)') "run 1 names the ExactVersion, unreadable, non-UTF-8 and range mods"
    $bad = @()
    foreach ($m in $mods) {
        if ($m.Old) {
            if ((Hex (Live $m.Id)) -ne (Hex (Expected $m '0.8.0')) -or (Hex (Kept $m.Id)) -ne (Hex $m.Info)) { $bad += $m.Id }
        } elseif ((Hex (Live $m.Id)) -ne (Hex $m.Info) -or $null -ne (Kept $m.Id)) { $bad += $m.Id }
    }
    Check ($bad.Count -eq 0) "run 1: marked files are the author's with one comment line and the value 0.8.0, authors' files kept, every other file untouched ($($bad -join ', '))"
    Check ((Text ([IO.File]::ReadAllBytes($cl))) -ceq (Text $clBefore).Replace('ToggleWindow = F6', 'ToggleWindow = None').Replace('RunProbe = F8', 'RunProbe = None')) "run 1 unbinds Contact Log's F6 and F8"
    Check ((Hex ([IO.File]::ReadAllBytes($cl + '.sest-ui-keys.bak'))) -eq (Hex $clBefore)) "run 1 keeps Contact Log's settings as they were"
    Check ($r.Out -match "\[done\] Contact Log's default keys unbound") "run 1 says so"
    $order = Text ([IO.File]::ReadAllBytes($settings))
    Check ($order -match "NumberOfModFiles=$($mods.Count + 1)" -and $order -match 'Mod1Directory=3812461539,True' -and $order -match '\[Other\]\r\nY=2') "run 1 still writes the mod order"

    # 2. Second run: nothing changes.
    $snap = @{}; foreach ($m in $mods) { $snap[$m.Id] = Hex (Live $m.Id) }
    $clSnap = Hex ([IO.File]::ReadAllBytes($cl))
    $r = Setup @()
    $same = $true; foreach ($m in $mods) { if ((Hex (Live $m.Id)) -ne $snap[$m.Id]) { $same = $false } }
    Check ($r.Code -eq 0 -and $same -and (Hex ([IO.File]::ReadAllBytes($cl))) -eq $clSnap) "run 2 changes no mod file and no key"
    Check ($r.Out -match '\[ok\]   8 mod\(s\) already marked compatible with 0\.8\.7; no other mod that SETUP can change is made for an older game version') "run 2 counts the eight as already marked (the one not UTF-8 is named below, not counted)"
    Check ($r.Out -match "\[ok\]   Contact Log's keys: neither holds its clashing default") "run 2 finds Contact Log's keys done"

    # 3. -RestoreModFiles puts every author's file back.
    $r = Setup @('-RestoreModFiles')
    $wrong = AllAsShipped
    Check ($r.Code -eq 0 -and -not $wrong -and @(Get-ChildItem -LiteralPath $keep -File).Count -eq 0) "-RestoreModFiles puts every file back byte for byte and empties the kept folder ($wrong)"
    Check ($r.Out -match '\[done\] 8 mod file\(s\) put back') "-RestoreModFiles counts eight"

    # 4. REDFOR as GPT's reviewed-compat script left it on the owner's PC.
    $redforMod = $mods | Where-Object { $_.Id -eq '3732654992' }
    $gpt = Bytes ($redfor.Replace('ApproximateVersion=0.8.8', $marker + " (reviewed REDFOR 0.8.8 declaration on native 0.8.7); SETUP -RestoreModFiles puts it back`r`nApproximateVersion=0.8.7"))
    Put (J $content '3732654992' '_info.ini') $gpt
    Put (J $keep '3732654992._info.ini') $redforMod.Info
    $r = Setup @()
    Check ($r.Code -eq 0 -and (Hex (Live '3732654992')) -eq (Hex $gpt) -and (Hex (Kept '3732654992')) -eq (Hex $redforMod.Info)) "GPT's REDFOR mark is accepted as it is, its kept file untouched"
    Check ($r.Out -match '\[done\] 7 mod\(s\) made for an older game version' -and $r.Out -notmatch 'but reviewed') "the seven older mods are marked; REDFOR counts as already marked"

    # 5. The game moves to 0.9.0: SETUP's marks and GPT's are judged again.
    GameVersion "01-Jan-2027: 0.9.0 Build 270101 Public Release"
    $r = Setup @()
    Check ($r.Code -eq 0) "run on 0.9.0 finishes (exit $($r.Code))"
    Check ($r.Out -match '\[done\] 20 mod\(s\) made for an older game version marked compatible with 0\.9\.0 \(the start-up warning about them stops; 8 of them marked before, for another game version\)') "on 0.9.0: 20 marked, the 8 marked before among them"
    $bad = @()
    foreach ($m in $mods | Where-Object { $_.Old -and $_.Id -ne '3732654992' }) {
        if ((Hex (Live $m.Id)) -ne (Hex (Expected $m '0.9.0')) -or (Hex (Kept $m.Id)) -ne (Hex $m.Info)) { $bad += $m.Id }
    }
    Check ($bad.Count -eq 0) "on 0.9.0: a file marked before gets only its value rewritten, one comment line, the author's file still kept ($($bad -join ', '))"
    Check ((Hex (Live '3732654992')) -eq (Hex (Bytes ((Text $gpt).Replace('ApproximateVersion=0.8.7', 'ApproximateVersion=0.9.0')))) -and (Hex (Kept '3732654992')) -eq (Hex $redforMod.Info)) "on 0.9.0: GPT's REDFOR mark is re-marked, the author's file still kept"
    $m87 = $mods | Where-Object { $_.Id -eq '9000107' }
    Check ((Text (Live '9000107')) -ceq ("[Compatibility]`n" + $marker + " (its author's ApproximateVersion was 0.8.7); SETUP -RestoreModFiles puts it back`nApproximateVersion=0.9.0`n") -and (Hex (Kept '9000107')) -eq (Hex $m87.Info)) "on 0.9.0: a 0.8.7 mod is older now and marked"
    Check ($r.Out -match 'Not marked, declared in a way SETUP does not change \(listed as not compatible\): Exact \(ExactVersion=0\.8\.6\), Unreadable \(ApproximateVersion=v-next\), Not UTF8 \(0\.6\.0, not UTF-8 text\), Range In \(GreaterThanEqualToVersion=0\.8\.3, LessThanVersion=0\.9\.0\)') "on 0.9.0: the range that now excludes the game is named"

    # 6. The game goes back to 0.8.7 (a player leaving a beta, say): every
    # mark is now ahead of it, so the author's kept file decides. The older
    # mods and REDFOR are marked 0.8.0 again, value only; the ones the game
    # accepts as shipped, or made for a newer game version, go back as their
    # authors shipped them. None of SETUP's marks is named as newer.
    GameVersion "21-Oct-2026: 0.8.7 Build 261021 Public Release"
    $r = Setup @()
    Check ($r.Code -eq 0 -and $r.Out -match 'All done') "back on 0.8.7: finishes with no warning (exit $($r.Code))"
    Check ($r.Out -match '\[done\] 7 mod\(s\) made for an older game version marked compatible with 0\.8\.7 \(the start-up warning about them stops; 7 of them marked before, for another game version\)') "back on 0.8.7: the seven older mods are marked again"
    Check ($r.Out -match '\[done\] made for a newer game version but reviewed, so marked compatible with 0\.8\.7: THE REDFOR MOD') "back on 0.8.7: REDFOR is marked again as a reviewed one"
    Check ($r.Out -match '\[done\] 12 mod file\(s\) SETUP had marked for a later game version than 0\.8\.7 put back as their authors shipped them') "back on 0.8.7: twelve put back (the eight 0.8.x, Newer Patch, Partial Newer, Odd Newer and Four Part Newer)"
    Check ($r.Out -match 'Not marked, made for a newer game version than 0\.8\.7 \(listed as not compatible until the game catches up\): Newer Patch \(0\.8\.8\), Newer Minor \(0\.9\.0\), Partial Newer \(0\.9\), Odd Newer \(0\.8\.08\), Four Part Newer \(0\.8\.8\.1\)\r?\n') "back on 0.8.7: only the mods whose authors declared a newer version are named as newer"
    $bad = @()
    foreach ($m in $mods) {
        if ($m.Old -and $m.Id -ne '3732654992') {
            if ((Hex (Live $m.Id)) -ne (Hex (Expected $m '0.8.0')) -or (Hex (Kept $m.Id)) -ne (Hex $m.Info)) { $bad += $m.Id }
        } elseif ($m.Id -ne '3732654992' -and ((Hex (Live $m.Id)) -ne (Hex $m.Info) -or $null -ne (Kept $m.Id))) { $bad += $m.Id }
    }
    Check ($bad.Count -eq 0) "back on 0.8.7: the older mods hold 0.8.0 with one comment line and their kept files; every other mod is its author's file with nothing kept ($($bad -join ', '))"
    Check ((Hex (Live '3732654992')) -eq (Hex (Bytes ((Text $gpt).Replace('ApproximateVersion=0.8.7', 'ApproximateVersion=0.8.0')))) -and (Hex (Kept '3732654992')) -eq (Hex $redforMod.Info)) "back on 0.8.7: REDFOR holds 0.8.0, the author's file still kept"
    $snap = @{}; foreach ($m in $mods) { $snap[$m.Id] = Hex (Live $m.Id) }
    $r = Setup @()
    $same = $true; foreach ($m in $mods) { if ((Hex (Live $m.Id)) -ne $snap[$m.Id]) { $same = $false } }
    Check ($r.Code -eq 0 -and $same -and $r.Out -match '\[ok\]   8 mod\(s\) already marked compatible with 0\.8\.7' -and $r.Out -notmatch 'put back') "back on 0.8.7, run again: nothing changes, eight already marked"
    $r = Setup @('-RestoreModFiles')
    $wrong = AllAsShipped
    Check ($r.Code -eq 0 -and -not $wrong -and @(Get-ChildItem -LiteralPath $keep -File).Count -eq 0) "-RestoreModFiles after the game moved up and back puts every file back byte for byte, REDFOR's as its author shipped it ($wrong)"

    # 6b. -RestoreModFiles straight after a game update.
    GameVersion "01-Jan-2027: 0.9.0 Build 270101 Public Release"
    $r = Setup @()
    Check ($r.Out -match '\[done\] 20 mod\(s\) made for an older game version marked compatible with 0\.9\.0 \(the start-up warning about them stops\)') "fresh on 0.9.0: 20 marked, REDFOR's 0.8.8 among them as an older one"
    $r = Setup @('-RestoreModFiles')
    $wrong = AllAsShipped
    Check ($r.Code -eq 0 -and -not $wrong -and $r.Out -match '\[done\] 20 mod file\(s\) put back') "-RestoreModFiles on 0.9.0 puts every file back byte for byte ($wrong)"

    # 7. A reviewed mod that now holds a .dll is not marked.
    GameVersion "21-Oct-2026: 0.8.7 Build 261021 Public Release"
    Put (J $content '3732654992' 'plugins' 'Code.dll') (Bytes 'MZ')
    $r = Setup @()
    Check ((Hex (Live '3732654992')) -eq (Hex $redforMod.Info) -and $r.Out -match 'THE REDFOR MOD \(0\.8\.8, now holds a \.dll\)') "REDFOR with a .dll is named and left alone"
    # 7b. Marked as a reviewed mod before the .dll came: the author's file
    # goes back and is named; REDFOR is not counted as already marked.
    Remove-Item -LiteralPath (J $content '3732654992' 'plugins') -Recurse -Force
    $r = Setup @()
    Check ($r.Out -match '\[done\] made for a newer game version but reviewed, so marked compatible with 0\.8\.7: THE REDFOR MOD' -and (Hex (Kept '3732654992')) -eq (Hex $redforMod.Info)) "without the .dll REDFOR is marked again"
    Put (J $content '3732654992' 'plugins' 'Code.dll') (Bytes 'MZ')
    $r = Setup @()
    Check ($r.Code -eq 0 -and (Hex (Live '3732654992')) -eq (Hex $redforMod.Info) -and $null -eq (Kept '3732654992') -and $r.Out -match '\[done\] reviewed mod\(s\) whose folder now holds a \.dll put back as their authors shipped them: THE REDFOR MOD \(0\.8\.8, now holds a \.dll\)' -and $r.Out -match '\[ok\]   7 mod\(s\) already marked compatible') "REDFOR marked before its .dll came: its author's file is back and named, not counted as already marked"
    # 7c. GPT's mark and no kept file: named and left as it is.
    Put (J $content '3732654992' '_info.ini') $gpt
    $r = Setup @()
    Check ($r.Code -eq 0 -and (Hex (Live '3732654992')) -eq (Hex $gpt) -and $r.Out -match "Left as marked before, reviewed mod\(s\) whose folder now holds a \.dll, with no author's file kept to put back: THE REDFOR MOD" -and $r.Out -match '\[ok\]   7 mod\(s\) already marked compatible') "GPT's REDFOR mark with a .dll and no kept file: named and left, not counted as already marked"
    Put (J $content '3732654992' '_info.ini') $redforMod.Info
    Remove-Item -LiteralPath (J $content '3732654992' 'plugins') -Recurse -Force
    Setup @('-RestoreModFiles') | Out-Null

    # 8. The key helper fails: one warning, the rest of SETUP still runs.
    Put (J $pack 'sest-ui-keys.ps1') (Bytes "param([string]`$GameDir)`r`nthrow 'simulated failure'`r`n")
    Put $settings (Bytes "[General]`r`nX=1`r`n[LoadOrder]`r`nNumberOfModFiles=1`r`nMod1Directory=9000001,True`r`n")
    $r = Setup @()
    Check ($r.Code -eq 0 -and $r.Out -match "\[!!\]   Contact Log's keys were not changed: simulated failure" -and $r.Out -match 'read the 1 \[!!\] warning') "a failing key helper is one warning, not a stop"
    Check ((Text ([IO.File]::ReadAllBytes($settings))) -match 'Mod1Directory=3812461539,True') "and the mod order is still written"

    # 9. No helper beside SETUP, or no Contact Log: step 4 is skipped quietly.
    Remove-Item -LiteralPath (J $pack 'sest-ui-keys.ps1') -Force
    $r = Setup @()
    Check ($r.Code -eq 0 -and $r.Out -notmatch 'Contact Log' -and $r.Out -match 'All done') "no sest-ui-keys.ps1: nothing said, no warning"
    Put (J $pack 'sest-ui-keys.ps1') ([IO.File]::ReadAllBytes((J $src 'sest-ui-keys.ps1')))
    Remove-Item -LiteralPath (J $game 'BepInEx' 'config') -Recurse -Force
    $r = Setup @()
    Check ($r.Code -eq 0 -and $r.Out -notmatch 'Contact Log' -and -not (Test-Path -LiteralPath (J $game 'BepInEx' 'config'))) "no Contact Log settings: nothing said, nothing created"
    Setup @('-RestoreModFiles') | Out-Null

    # 10. A mod file SETUP cannot read: one warning for that mod; the other
    # mods are still checked and the mod order is still written.
    $hp = J $content '9000203' '_info.ini'
    $hpInfo = ($mods | Where-Object { $_.Id -eq '9000203' }).Info
    Remove-Item -LiteralPath $hp -Force
    New-Item -ItemType Directory -Path $hp | Out-Null
    Put $settings (Bytes "[General]`r`nX=1`r`n[LoadOrder]`r`nNumberOfModFiles=1`r`nMod1Directory=9000001,True`r`n")
    $r = Setup @()
    Check ($r.Code -eq 0 -and $r.Out -match '\[!!\]   Could not check or mark Huge Patch: ' -and $r.Out -match 'read the 1 \[!!\] warning' -and $r.Out -match '\[done\] 6 mod\(s\) made for an older game version marked compatible' -and $r.Out -match 'but reviewed, so marked compatible with 0\.8\.7: THE REDFOR MOD') "a mod file that cannot be read is one warning; the other older mods and REDFOR are still marked"
    Check ((Text ([IO.File]::ReadAllBytes($settings))) -match 'Mod1Directory=3812461539,True') "and the mod order is still written"

    # 11. -RestoreModFiles stopped part-way, after putting files back, does
    # not say that nothing was changed.
    Put (J $keep '9000203._info.ini') $hpInfo
    $order = @(Get-ChildItem -LiteralPath $keep -Filter '*._info.ini' -File | ForEach-Object { $_.Name })
    $r = Setup @('-RestoreModFiles')
    Check ($order[-1] -eq '9000203._info.ini' -and $r.Code -ne 0 -and $r.Out -match 'Some changes above were already made' -and $r.Out -notmatch 'Nothing was changed' -and (Hex (Live '9000001')) -eq (Hex ($mods | Where-Object { $_.Id -eq '9000001' }).Info)) "-RestoreModFiles stopped by a file it cannot read, after putting others back, says changes were made"
    Remove-Item -LiteralPath $hp -Recurse -Force
    Put $hp $hpInfo
    $r = Setup @('-RestoreModFiles')
    $wrong = AllAsShipped
    Check ($r.Code -eq 0 -and -not $wrong -and @(Get-ChildItem -LiteralPath $keep -File).Count -eq 0) "run again, it finishes: every file as shipped, nothing kept ($wrong)"

    # 12. -KeepDir (the administrator relaunch passes the player's own): the
    # authors' files are kept there, and -RestoreModFiles takes them back.
    $alt = J $root 'player' 'compat-originals'
    $r = Setup @('-KeepDir', $alt)
    Check ($r.Code -eq 0 -and @(Get-ChildItem -LiteralPath $alt -File).Count -eq 8 -and @(Get-ChildItem -LiteralPath $keep -File -ErrorAction SilentlyContinue).Count -eq 0 -and (Hex ([IO.File]::ReadAllBytes((J $alt '9000001._info.ini')))) -eq (Hex ($mods | Where-Object { $_.Id -eq '9000001' }).Info)) "-KeepDir: the authors' files are kept in that folder, none in the default one"
    $r = Setup @('-RestoreModFiles', '-KeepDir', $alt)
    $wrong = AllAsShipped
    Check ($r.Code -eq 0 -and -not $wrong -and @(Get-ChildItem -LiteralPath $alt -File).Count -eq 0 -and $r.Out -match '\[done\] 8 mod file\(s\) put back') "-RestoreModFiles -KeepDir puts them back from that folder ($wrong)"
    Check ([IO.File]::ReadAllText((J $src 'sest-setup.ps1')).Contains("'-KeepDir', ('" + '"' + "' + `$kd + '" + '"' + "')")) "the administrator relaunch passes -KeepDir"

    # 13. Contact Log downloaded but no settings file yet: one note, not a
    # warning, and nothing created.
    Put (J $content '3819427362' 'ContactLog.dll') (Bytes 'MZ')
    $r = Setup @()
    Check ($r.Code -eq 0 -and $r.Out -match "\[note\] Contact Log has no settings file yet\. Start Sea Power once with it, quit, then run SETUP again to free its default F6 \(Topographic Map's F6\) and F8 \(Coordinated Strike Tool's F8 planner\)\." -and $r.Out -match 'All done' -and -not (Test-Path -LiteralPath (J $game 'BepInEx' 'config'))) "Contact Log downloaded with no settings file: one note, no warning, nothing created"
    Remove-Item -LiteralPath (J $content '3819427362') -Recurse -Force
    Setup @('-RestoreModFiles') | Out-Null
} finally {
    foreach ($k in $saved.Keys) { Set-Item -Path ("env:" + $k) -Value $saved[$k] -ErrorAction SilentlyContinue; if ($null -eq $saved[$k]) { Remove-Item -Path ("env:" + $k) -ErrorAction SilentlyContinue } }
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
