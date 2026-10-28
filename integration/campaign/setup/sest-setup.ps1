# SEST Integration Pack - setup for Sea Power. Run with the game closed.
#
# Double-click "SETUP - double-click me.cmd" beside this file (Mod Manager >
# Open Folder on the pack gets you here). It checks that every Workshop mod
# the campaigns were built against is downloaded, installs the Anchor Chain
# preloader if it is missing, turns off one mod's debug logging that can
# freeze a mission, marks the mods made for an older game version compatible
# so the Mod Manager stops warning about them at start-up, unbinds Contact
# Log's default F6 and F8 keys if you have that mod (its F6 clashes with
# Topographic Map's F6, its F8 probe with Coordinated Strike Tool's F8
# planner), and writes the Mod Manager order: this pack first, then the
# mods in the order they were tested in, your other mods at the bottom as you
# had them. Safe to run again: it checks everything before it changes
# anything, and it backs up the game's settings and every mod file it changes
# first.
#
# From a console:  powershell -ExecutionPolicy Bypass -File .\sest-setup.ps1
# Put the marked mods' own files back:  ... -File .\sest-setup.ps1 -RestoreModFiles
param([switch]$Pause, [switch]$FromCmd, [switch]$Elevated, [string]$SteamRoot, [string]$Settings, [switch]$RestoreModFiles, [string]$KeepDir)
# -FromCmd: the launcher passes it; the window stays open at the end (the
#   launcher itself pauses after a failure, so Fail does not pause twice).
# -Elevated, -SteamRoot, -Settings, -KeepDir: the administrator relaunch
#   passes its own paths down, so a UAC prompt answered with another
#   account's password still works on the player's Steam, the player's
#   settings file and the player's kept mod files (KeepDir below).
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
function J { $p = [string]$args[0]; for ($k = 1; $k -lt $args.Count; $k++) { $p = [IO.Path]::Combine($p, [string]$args[$k]) }; $p }
function Say([string]$t, [string]$c = 'Gray') { Write-Host $t -ForegroundColor $c }
function Same([string]$a, [string]$b) {
    if (-not $a -or -not $b) { return $false }
    return [IO.Path]::GetFullPath($a).TrimEnd('\', '/') -ieq [IO.Path]::GetFullPath($b).TrimEnd('\', '/')
}
function Hold { if ($Pause -or $FromCmd) { Write-Host ''; [void](Read-Host 'Press Enter to close this window') } }
$changed = $false
$warnings = 0
function Fail([string]$t) {
    Write-Host ''
    Write-Host ('STOPPED: ' + $t) -ForegroundColor Red
    if ($changed) { Write-Host 'Some changes above were already made. Sort this out, then run SETUP again.' -ForegroundColor Red }
    else { Write-Host 'Nothing was changed. Sort that out, then run SETUP again.' -ForegroundColor Red }
    if ($Pause -and -not $FromCmd) { Hold }
    exit 1
}
function ReadText([string]$path) {
    $b = [IO.File]::ReadAllBytes($path)
    $bom = $b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF
    $o = 0; if ($bom) { $o = 3 }
    @{ Text = (New-Object Text.UTF8Encoding($false)).GetString($b, $o, $b.Length - $o); Bom = $bom }
}
function WriteText([string]$path, [string]$text, [bool]$bom) {
    [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding($bom)))
}
# Where the authors' own _info.ini files are kept when a mod is marked
# compatible (the same folder the SEST tools use on the author's PC), or
# the folder -KeepDir names (a full path by then: see the start of the run).
$CompatMarker = '; SEST marked this mod compatible'
function KeepDir {
    if ($KeepDir) { return $KeepDir }
    $base = $env:LOCALAPPDATA
    if (-not $base) { $base = [Environment]::GetFolderPath('LocalApplicationData') }
    if (-not $base) { $base = [IO.Path]::GetTempPath() }
    J $base 'SEST' 'compat-originals'
}
function IsPack([string]$dir) {
    return $dir -and (Test-Path -LiteralPath (J $dir 'LOAD-ORDER.txt')) -and (Test-Path -LiteralPath (J $dir 'campaigns' 'sest-southern-watch' 'campaign.ini'))
}

# --- the game's own compatibility rule (step 3) ------------------------------
# Sea Power's Mod Manager (ModCompatibility.Matches in Seapower-Scripts.dll,
# read for 0.8.7) judges the [Compatibility] section of each mod's _info.ini
# against the game's MAJOR.MINOR.PATCH:
#   - an ExactVersion, if there is one, must equal it;
#   - if not, an ApproximateVersion, if there is one, must be written
#     MAJOR.MINOR.PATCH (a -pre-release or +build part is allowed and
#     ignored) with the game's MAJOR and MINOR and a PATCH no higher than
#     the game's: 0.8.0 to 0.8.7 pass on 0.8.7; 0.8.8, 0.9.0, 0.7.9, 0.8
#     and 0.8.7.1 do not;
#   - if neither, GreaterThan(EqualTo)Version, LessThan(EqualTo)Version and
#     ExcludeVersions must admit it; a mod with none of these passes.
# Every mod that fails is listed as not compatible at each start-up. The
# Compat* functions read and judge a file the same way;
# tools\mark-mods-compatible.ps1 loads them from this file, so the two tools
# cannot drift apart. They only read and return values.
function CompatNum([string]$a, [string]$b) {
    # Two runs of ASCII digits compared by value, -1, 0 or 1, without
    # converting them, so a 20-digit component cannot overflow.
    $a = $a.TrimStart([char]'0'); $b = $b.TrimStart([char]'0')
    if ($a.Length -ne $b.Length) { if ($a.Length -lt $b.Length) { return -1 }; return 1 }
    return [Math]::Sign([string]::CompareOrdinal($a, $b))
}
function CompatCmp($a, $b) {
    for ($k = 0; $k -lt 3; $k++) { $d = CompatNum $a[$k] $b[$k]; if ($d -ne 0) { return $d } }
    return 0
}
function CompatMatch([string]$v) {
    # The game's SemVer 2.0 pattern (its \d written [0-9]).
    return [regex]::Match($v, '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*)?(?:\+[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)?$')
}
function CompatVer([string]$v) {
    # @(MAJOR, MINOR, PATCH) as digit strings, or $null when $v does not
    # match the pattern or a number is above 2147483647 (the game throws on
    # those instead of answering: counted here as not accepted).
    $m = CompatMatch $v
    if (-not $m.Success) { return $null }
    $r = @($m.Groups[1].Value, $m.Groups[2].Value, $m.Groups[3].Value)
    foreach ($x in $r) { if ((CompatNum $x '2147483647') -gt 0) { return $null } }
    return ,$r
}
function CompatCut([string]$s) {
    # Where the game cuts a value off: the first ;, // or #.
    $k = $s.Length
    foreach ($sep in ';', '//', '#') { $x = $s.IndexOf($sep, [StringComparison]::Ordinal); if ($x -ge 0 -and $x -lt $k) { $k = $x } }
    return $k
}
function CompatRead([string]$text) {
    # The [Compatibility] keys as the game's ini reader sees them: each line
    # trimmed; a line starting with //, # or ; skipped; a value cut off at
    # the first ;, // or # and trimmed; only the first [Compatibility]
    # section (the name is case-sensitive, and the game ignores a repeat of
    # it in the same file); key names in any case, the first of a repeated
    # key wins. At and Len locate the ApproximateVersion value in $text,
    # Line the start of its line, Eol that line's ending.
    $c = @{ ExactVersion = ''; ApproximateVersion = ''; GreaterThanVersion = ''; GreaterThanEqualToVersion = ''
            LessThanVersion = ''; LessThanEqualToVersion = ''; ExcludeVersions = ''; At = -1; Len = 0; Line = -1; Eol = '' }
    $keys = 'ExactVersion', 'ApproximateVersion', 'GreaterThanVersion', 'GreaterThanEqualToVersion', 'LessThanVersion', 'LessThanEqualToVersion', 'ExcludeVersions'
    $seen = @{}; $in = $false; $prev = "`r`n"
    foreach ($ln in [regex]::Matches($text, '([^\r\n]*)(\r\n|\n|\r|$)')) {
        $raw = $ln.Groups[1].Value; $eol = $ln.Groups[2].Value
        if (-not $eol) { $eol = $prev } else { $prev = $eol }
        $t = $raw.Trim()
        if ($t -match '^(//|#|;)') { continue }
        $t = $t.Substring(0, (CompatCut $t)).Trim()
        $h = [regex]::Match($t, '^\[(.+)\]')
        if ($h.Success) {
            if ($in) { break }
            $in = $h.Groups[1].Value -ceq 'Compatibility'
            continue
        }
        if (-not $in) { continue }
        $p = $t.Split([char]'=')
        if ($p.Count -lt 2) { continue }
        $key = $p[0].Trim()
        foreach ($n in $keys) {
            if (-not [string]::Equals($key, $n, [StringComparison]::OrdinalIgnoreCase) -or $seen.ContainsKey($n)) { continue }
            $seen[$n] = $true
            $c[$n] = (@($p[1..($p.Count - 1)] | ForEach-Object { $_.Trim() })) -join '='
            if ($n -eq 'ApproximateVersion') {
                $s = $raw.IndexOf([char]'=') + 1; $f = CompatCut $raw
                while ($s -lt $f -and [char]::IsWhiteSpace($raw[$s])) { $s++ }
                while ($f -gt $s -and [char]::IsWhiteSpace($raw[$f - 1])) { $f-- }
                $c.At = $ln.Index + $s; $c.Len = $f - $s; $c.Line = $ln.Index; $c.Eol = $eol
            }
        }
    }
    return $c
}
function CompatVerdict($c, $game) {
    # 'ok' when the game (@(MAJOR, MINOR, PATCH)) accepts what CompatRead
    # found; otherwise why not: 'older' or 'newer', an ApproximateVersion
    # made for an older or a newer game version; 'odd', an ApproximateVersion
    # with no MAJOR.MINOR to read; 'exact', an ExactVersion; 'range', the
    # range keys. A value not written MAJOR.MINOR.PATCH, which no game
    # version accepts, is judged by the two or three numbers it starts with
    # (PATCH 0 when there are two): 'newer' when they come above the game's
    # version, 'older' otherwise. So on 0.8.7, 0.8.08 and 0.8.8.1 are newer
    # (left alone), and 0.8, 0.8.07 and 0.8.7.1 older (marked). A value the
    # game's pattern takes but with a number above 2147483647, which the
    # game throws on, is 'older' whatever its numbers.
    if ($c.ExactVersion) {
        $v = CompatVer $c.ExactVersion
        if ($null -ne $v -and (CompatCmp $v $game) -eq 0) { return 'ok' }
        return 'exact'
    }
    if ($c.ApproximateVersion) {
        $v = CompatVer $c.ApproximateVersion
        if ($null -ne $v) {
            if ((CompatNum $v[0] $game[0]) -eq 0 -and (CompatNum $v[1] $game[1]) -eq 0 -and (CompatNum $v[2] $game[2]) -le 0) { return 'ok' }
        } elseif ((CompatMatch $c.ApproximateVersion).Success) {
            return 'older'
        } else {
            $m = [regex]::Match($c.ApproximateVersion, '^([0-9]+)\.([0-9]+)(?:\.([0-9]+))?')
            if (-not $m.Success) { return 'odd' }
            $patch = $m.Groups[3].Value; if (-not $patch) { $patch = '0' }
            $v = @($m.Groups[1].Value, $m.Groups[2].Value, $patch)
        }
        if ((CompatCmp $v $game) -le 0) { return 'older' }
        return 'newer'
    }
    $ex = @($c.ExcludeVersions.Split([char]',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if (-not ($c.GreaterThanVersion -or $c.GreaterThanEqualToVersion -or $c.LessThanVersion -or $c.LessThanEqualToVersion -or $ex.Count)) { return 'ok' }
    foreach ($x in $ex) {
        $v = CompatVer $x
        if ($null -eq $v) { if ((CompatMatch $x).Success) { return 'range' }; continue }
        if ((CompatCmp $game $v) -eq 0) { return 'range' }
    }
    $lo = $c.GreaterThanVersion; $open = $true
    if (-not $lo) { $lo = $c.GreaterThanEqualToVersion; $open = $false }
    if ($lo) {
        $v = CompatVer $lo; if ($null -eq $v) { return 'range' }
        $d = CompatCmp $game $v; if ($d -lt 0 -or ($open -and $d -eq 0)) { return 'range' }
    }
    $hi = $c.LessThanVersion; $open = $true
    if (-not $hi) { $hi = $c.LessThanEqualToVersion; $open = $false }
    if ($hi) {
        $v = CompatVer $hi; if ($null -eq $v) { return 'range' }
        $d = CompatCmp $game $v; if ($d -gt 0 -or ($open -and $d -eq 0)) { return 'range' }
    }
    return 'ok'
}
# Reviewed exceptions. A mod that declares a NEWER game version than the
# installed one is left alone: it may need that game. A Workshop id listed
# here is marked like an older mod instead, but only while its folder holds
# no .dll (data only). Once it holds one, an earlier mark is judged by the
# author's kept file (CompatCode): that file comes back if SETUP would leave
# it alone, and the mark stays if not; with no author's file kept the mod
# is named and left marked. Add an id only after reviewing that mod's files
# on the installed game.
#   3732654992  THE REDFOR MOD: data only; reviewed 27 Oct 2026 on game 0.8.7.
function CompatReviewed { return @('3732654992') }
function CompatHasCode([string]$dir) {
    return [bool]@(Get-ChildItem -LiteralPath $dir -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.Extension -ieq '.dll' }).Count
}
function CompatPlan([string]$text, $game, [string]$id, [string]$dir) {
    # One mod's _info.ini: @{ C = what CompatRead found; Why = CompatVerdict's
    # answer; Mark = $true when SETUP rewrites its ApproximateVersion (made
    # for an older game version, or a reviewed newer one with no .dll);
    # What = the declaration, for a report }.
    $c = CompatRead $text
    $why = CompatVerdict $c $game
    $p = @{ C = $c; Why = $why; Mark = ($why -eq 'older'); What = $c.ApproximateVersion }
    if ($why -eq 'exact') { $p.What = 'ExactVersion=' + $c.ExactVersion }
    elseif ($why -eq 'odd') { $p.What = 'ApproximateVersion=' + $c.ApproximateVersion }
    elseif ($why -eq 'range') {
        $p.What = (@('GreaterThanVersion', 'GreaterThanEqualToVersion', 'LessThanVersion', 'LessThanEqualToVersion', 'ExcludeVersions') |
                   Where-Object { $c[$_] } | ForEach-Object { $_ + '=' + $c[$_] }) -join ', '
    }
    elseif ($why -eq 'newer' -and @(CompatReviewed) -contains $id) {
        if (CompatHasCode $dir) { $p.What += ', now holds a .dll' } else { $p.Mark = $true }
    }
    return $p
}
function CompatBack($p, [byte[]]$kept, [string]$marker, $game, [string]$id, [string]$dir) {
    # $p: the CompatPlan of a file marked before (it carries $marker) whose
    # value the game now takes for one made for a NEWER game version, so
    # that mark is ahead of the game: the game went back a version (a player
    # leaving a public beta, say). Such a file is judged by its author's
    # file instead, the one kept when it was first marked ($kept; $null when
    # it is gone). If SETUP would mark the author's file, $p.Mark is set and
    # $p.Why becomes the author's ('older', or 'newer' for a reviewed mod):
    # only the value is rewritten again. If SETUP would leave the author's
    # file alone (the game accepts it, or it is made for a newer game version
    # too), $p.Why and $p.What become the author's and the answer is $true:
    # that file goes back as it is. With no kept file (or one that carries
    # the marker itself) the value is rewritten again as an older one.
    $p.Mark = $true; $p.Why = 'older'
    $t = CompatKept $kept $marker
    if ($null -eq $t) { return $false }
    $a = CompatPlan $t $game $id $dir
    $p.Why = $a.Why
    if ($a.Mark) { return $false }
    $p.Mark = $false; $p.What = $a.What
    return $true
}
function CompatKept([byte[]]$kept, [string]$marker) {
    # The author's kept file ($kept, its bytes) as text, or $null when there
    # is none or it carries $marker itself (so it is not the author's).
    if ($null -eq $kept) { return $null }
    $o = 0; if ($kept.Length -ge 3 -and $kept[0] -eq 0xEF -and $kept[1] -eq 0xBB -and $kept[2] -eq 0xBF) { $o = 3 }
    $t = (New-Object Text.UTF8Encoding($false)).GetString($kept, $o, $kept.Length - $o)
    if ($t.IndexOf($marker, [StringComparison]::Ordinal) -ge 0) { return $null }
    return $t
}
function CompatCode($p, [byte[]]$kept, [string]$marker, $game, [string]$id, [string]$dir) {
    # $p: the CompatPlan of a file marked before (it carries $marker, SETUP's
    # or GPT's) that the game does not take for one made for a newer game
    # version (CompatBack judges those). A reviewed mod (CompatReviewed) is
    # marked only while its folder holds no .dll; once it holds one, its
    # author's file ($kept, as for CompatBack) decides. 'back': SETUP would
    # leave the author's file alone, so it goes back as it is ($p.What
    # becomes its declaration). 'gone': there is no author's file to judge
    # by, so the mod is named and left as it is. '' for any other mod, and
    # when SETUP would mark the author's file anyway (made for an older game
    # version): the mark stands.
    if (@(CompatReviewed) -notcontains $id -or -not (CompatHasCode $dir)) { return '' }
    $t = CompatKept $kept $marker
    if ($null -eq $t) { return 'gone' }
    $a = CompatPlan $t $game $id $dir
    if ($a.Mark) { return '' }
    $p.What = $a.What
    return 'back'
}
function CompatMark([string]$text, $c, [string]$value, [string]$note) {
    # $text with its ApproximateVersion value replaced by $value and, unless
    # $note is empty, $note put on a line of its own above that line.
    $t = $text.Substring(0, $c.At) + $value + $text.Substring($c.At + $c.Len)
    if ($note) { $t = $t.Substring(0, $c.Line) + $note + $c.Eol + $t.Substring($c.Line) }
    return $t
}
function CompatIsUtf8([byte[]]$b) {
    # Only a file that is valid UTF-8 is rewritten: anything else would not
    # come back byte for byte.
    $o = 0; if ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) { $o = 3 }
    try { [void](New-Object Text.UTF8Encoding($false, $true)).GetString($b, $o, $b.Length - $o); return $true } catch { return $false }
}
$AppId = '1286220'
try {
    Say 'SEST setup - checking your PC...' 'Cyan'

    # -KeepDir as a full path, once, read against the folder PowerShell is in
    # (.NET's current folder can be another): the administrator relaunch
    # starts in another folder, so it is passed this full path.
    if ($KeepDir) {
        try { $KeepDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($KeepDir) }
        catch { Fail ('-KeepDir ' + $KeepDir + ' is not a folder SETUP can use: ' + $_.Exception.Message); return }
    }

    if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) {
        Fail 'Sea Power is running. Quit the game completely first.'; return
    }

    # --- Steam, the game and its Workshop folder ---------------------------
    $steam = $SteamRoot
    if (-not $steam) { $steam = $env:SEST_STEAM_ROOT }
    if (-not $steam) {
        foreach ($k in 'HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam') {
            $p = Get-ItemProperty -Path $k -ErrorAction SilentlyContinue
            foreach ($n in 'SteamPath', 'InstallPath') {
                if (-not $steam -and $p -and $p.$n -and (Test-Path -LiteralPath $p.$n)) { $steam = $p.$n }
            }
        }
    }
    if (-not $steam) { Fail 'Could not find Steam on this PC.'; return }
    $libs = New-Object System.Collections.Generic.List[string]
    $libs.Add((J $steam 'steamapps'))
    $vdf = J $steam 'steamapps' 'libraryfolders.vdf'
    if (Test-Path -LiteralPath $vdf) {
        foreach ($m in [regex]::Matches((ReadText $vdf).Text, '"path"\s+"([^"]+)"')) {
            $r = $m.Groups[1].Value -replace '\\\\', '\'
            if (-not (Test-Path -LiteralPath $r)) { continue }
            $l = J $r 'steamapps'
            if (-not ($libs -contains $l)) { $libs.Add($l) }
        }
    }
    $game = $null; $content = $null
    foreach ($lib in $libs) {
        $acf = J $lib ('appmanifest_' + $AppId + '.acf')
        if (-not $game -and (Test-Path -LiteralPath $acf)) {
            $dir = [regex]::Match((ReadText $acf).Text, '"installdir"\s+"([^"]+)"').Groups[1].Value
            $g = J $lib 'common' $dir
            if ($dir -and (Test-Path -LiteralPath (J $g 'Sea Power.exe'))) { $game = $g; $content = J $lib 'workshop' 'content' $AppId }
        }
    }
    if (-not $game) { Fail 'Could not find Sea Power in your Steam libraries. Is it installed?'; return }
    if (-not (Test-Path -LiteralPath $content)) {
        foreach ($lib in $libs) { $c = J $lib 'workshop' 'content' $AppId; if (-not (Test-Path -LiteralPath $content) -and (Test-Path -LiteralPath $c)) { $content = $c } }
    }
    if (-not (Test-Path -LiteralPath $content)) { Fail 'No Sea Power Workshop downloads found. Subscribe to the collection and let Steam finish downloading.'; return }
    $sa = J $game 'Sea Power_Data' 'StreamingAssets'
    Say ('  game      : ' + $game)
    Say ('  workshop  : ' + $content)

    if ($RestoreModFiles) {
        $put = 0; $gone = 0
        foreach ($kept in @(Get-ChildItem -LiteralPath (KeepDir) -Filter '*._info.ini' -File -ErrorAction SilentlyContinue)) {
            $id = $kept.Name.Substring(0, $kept.Name.Length - '._info.ini'.Length)
            $live = J $content $id '_info.ini'
            $marked = (Test-Path -LiteralPath $live) -and (ReadText $live).Text.IndexOf($CompatMarker, [StringComparison]::Ordinal) -ge 0
            $changed = $true
            if ($marked) { [IO.File]::WriteAllBytes($live, [IO.File]::ReadAllBytes($kept.FullName)); $put++ } else { $gone++ }
            Remove-Item -LiteralPath $kept.FullName -Force
        }
        Say ('  [done] ' + $put + ' mod file(s) put back as their authors shipped them; ' + $gone + ' already replaced by Steam') 'Green'
        Hold; return
    }

    # --- the SEST pack: the folder this script sits in, or a Workshop copy --
    # Run from inside the pack (the normal way) it knows which folder it is:
    # a Workshop download under the content folder, or a copy placed in
    # StreamingAssets by hand. Run from anywhere else it looks for the one
    # Workshop copy.
    $here = $PSScriptRoot
    $pack = $null; $mode = ''
    if (IsPack $here) {
        $parent = Split-Path -Parent $here
        if (Same $parent $content) { $pack = Get-Item -LiteralPath $here; $mode = 'workshop' }
        elseif (Same $parent $sa) { $pack = Get-Item -LiteralPath $here; $mode = 'local' }
    }
    $wsPacks = @(Get-ChildItem -LiteralPath $content -Directory | Where-Object { IsPack $_.FullName })
    if (-not $pack) {
        if ($wsPacks.Count -eq 0) { Fail 'The SEST Integration Pack is not downloaded yet. Press Subscribe to all on the collection and wait for Steam to finish.'; return }
        if ($wsPacks.Count -gt 1) { Fail ('More than one copy of the SEST pack is subscribed (' + (($wsPacks | ForEach-Object { $_.Name }) -join ', ') + '). Unsubscribe from all but one, keeping the one in the collection.'); return }
        $pack = $wsPacks[0]; $mode = 'workshop'
    }
    if ($mode -eq 'workshop') {
        $others = @($wsPacks | Where-Object { -not (Same $_.FullName $pack.FullName) })
        if ($others.Count) { Fail ('More than one copy of the SEST pack is subscribed (' + ((@($pack) + $others | ForEach-Object { $_.Name }) -join ', ') + '). Unsubscribe from all but this one.'); return }
        $local = @(Get-ChildItem -LiteralPath $sa -Directory -ErrorAction SilentlyContinue | Where-Object { IsPack $_.FullName })
        if ($local.Count) { Fail ('A copy of the pack is also in the game folder: ' + $local[0].FullName + '  Two copies fight over the same files. Delete that folder (the Workshop copy replaces it), or unsubscribe and run SETUP from that folder instead.'); return }
    } else {
        if ($wsPacks.Count) { Fail ('You are running SETUP from a copy in the game folder, but you are also subscribed to the pack on the Workshop (' + $wsPacks[0].Name + '). Two copies fight over the same files. Unsubscribe, or delete ' + $pack.FullName + ' and run SETUP from the Workshop copy.'); return }
    }
    $ids = New-Object System.Collections.Generic.List[string]
    $names = @{}
    $self = $false
    foreach ($line in [IO.File]::ReadAllLines((J $pack.FullName 'LOAD-ORDER.txt'))) {
        if ($line -match '^\s*\d+\.\s+\(this pack\)') { $self = $true }
        $m = [regex]::Match($line, '^\s*\d+\.\s+(\d{6,})\s+(.*\S)\s*$')
        if ($m.Success -and -not $ids.Contains($m.Groups[1].Value)) { $ids.Add($m.Groups[1].Value); $names[$m.Groups[1].Value] = $m.Groups[2].Value }
    }
    if (-not $self -or $ids.Count -lt 50) { Fail ('Could not read the mod list in ' + (J $pack.FullName 'LOAD-ORDER.txt')); return }
    if ($mode -eq 'workshop') { Say ('  SEST pack : Workshop item ' + $pack.Name + ', built against ' + $ids.Count + ' mods') }
    else { Say ('  SEST pack : ' + $pack.FullName + ' (local copy), built against ' + $ids.Count + ' mods') }

    $missing = @($ids | Where-Object {
        $d = J $content $_
        -not ((Test-Path -LiteralPath $d) -and (Get-ChildItem -LiteralPath $d -Force | Select-Object -First 1))
    })
    if ($missing.Count) {
        Say ''
        Say ('These ' + $missing.Count + ' mods are not downloaded:') 'Yellow'
        foreach ($i in $missing) { Say ('  ' + $i + '  ' + $names[$i] + '   https://steamcommunity.com/sharedfiles/filedetails/?id=' + $i) 'Yellow' }
        Fail 'Some mods are missing. Press Subscribe to all on the collection again (or open the links above) and wait for Steam to finish downloading. If a mod can no longer be subscribed to, say so in the pack''s Workshop comments.'; return
    }
    Say ('  all ' + $ids.Count + ' mods are downloaded') 'Green'

    # --- the game's settings file ------------------------------------------
    $settings = $Settings
    if (-not $settings) { $settings = $env:SEST_SETTINGS }
    if (-not $settings) { $settings = J $env:USERPROFILE 'AppData' 'LocalLow' 'Triassic Games' 'Sea Power' 'usersettings.ini' }
    if (-not (Test-Path -LiteralPath $settings)) {
        Fail ('No game settings yet (' + $settings + '). Start Sea Power once, wait for the main menu, quit, then run SETUP again. If Windows asked you for a different account''s password a moment ago, run SETUP from your own account instead.'); return
    }
    $st = ReadText $settings
    $nl = "`n"; if ($st.Text.Contains("`r`n")) { $nl = "`r`n" }
    $all = [regex]::Split($st.Text, '\r?\n')
    $h = -1
    for ($i = 0; $i -lt $all.Count; $i++) { if ($h -lt 0 -and $all[$i].Trim() -eq '[LoadOrder]') { $h = $i } }
    $end = $all.Count
    if ($h -ge 0) { for ($i = $all.Count - 1; $i -gt $h; $i--) { if ($all[$i].TrimStart().StartsWith('[')) { $end = $i } } }
    $body = New-Object System.Collections.Generic.List[string]
    if ($h -ge 0) { for ($i = $h + 1; $i -lt $end; $i++) { $body.Add($all[$i]) } }
    $bodyText = $body -join "`n"
    $num = [regex]::Match($bodyText, '(?m)^\s*NumberOfModFiles\s*=\s*(\d+)')
    if ($h -lt 0 -or -not $num.Success) {
        Fail 'The game has not listed your mods yet. Start Sea Power once, wait for the main menu, quit, then run SETUP again.'; return
    }

    # --- Anchor Chain preloader: needed, and can we install it? ------------
    $hasDll = Test-Path -LiteralPath (J $game 'winhttp.dll')
    $hasBep = Test-Path -LiteralPath (J $game 'BepInEx')
    $needPreloader = -not $hasDll -and -not $hasBep
    if ($needPreloader) {
        $canWrite = $true
        $probe = J $game ('sest-write-test-' + [guid]::NewGuid().ToString('N') + '.tmp')
        try { [IO.File]::WriteAllText($probe, 'x'); Remove-Item -LiteralPath $probe -Force } catch { $canWrite = $false }
        if ($env:SEST_FORCE_NOADMIN) { $canWrite = $false }
        if (-not $canWrite) {
            if ($Elevated) { Fail ('Even as administrator the game folder cannot be written (' + $game + '). Install the Anchor Chain preloader by hand from its Workshop page, then run SETUP again.'); return }
            Say ''
            Say 'The Anchor Chain preloader needs installing in the game folder, which needs administrator rights.' 'Yellow'
            Say 'Windows will ask for permission; click Yes. The rest of the setup continues in that window.' 'Yellow'
            # Relaunch a console host, not whatever is running this script:
            # powershell_ise.exe -File only opens the file in the editor.
            $exe = Join-Path $PSHOME $(if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' })
            if (-not (Test-Path -LiteralPath $exe)) { $exe = (Get-Process -Id $PID).Path }
            # A backslash just before the closing quote would escape it, so
            # a folder written with one at the end is passed with \. instead
            # (the same folder).
            $kd = KeepDir; if ($kd.EndsWith('\')) { $kd += '.' }
            $argv = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $PSCommandPath + '"'),
                      '-Elevated', '-Pause', '-SteamRoot', ('"' + $steam + '"'), '-Settings', ('"' + $settings + '"'),
                      '-KeepDir', ('"' + $kd + '"'))
            try { $child = Start-Process -FilePath $exe -ArgumentList $argv -Verb RunAs -Wait -PassThru }
            catch { Fail 'Administrator permission was not given, so the preloader was not installed and nothing else was changed. Run SETUP again and click Yes, or install the preloader by hand from Anchor Chain''s Workshop page and run SETUP again.'; return }
            if ($child -and $child.ExitCode -ne 0) { Fail 'The administrator window stopped with a problem; its last lines say what. Sort that out and run SETUP again.'; return }
            Say 'Finished in the administrator window.' 'Green'
            Hold; return
        }
    }

    # ======================= checks done: make the changes ==================
    Say ''
    Say 'Everything is in place. Making the changes...' 'Cyan'
    $changed = $true

    # 1. Anchor Chain preloader
    if ($needPreloader) {
        $tmp = J ([IO.Path]::GetTempPath()) ('sest-acp-' + [guid]::NewGuid().ToString('N'))
        try {
            New-Item -ItemType Directory -Path $tmp | Out-Null
            $zip = $env:SEST_PRELOADER_ZIP
            if (-not $zip) {
                $zip = J $tmp 'ACPreloader.zip'
                [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
                Say '  downloading the Anchor Chain preloader (ACPreloader.zip, latest release) from github.com/SeaPower-Modders/AnchorChain...'
                (New-Object Net.WebClient).DownloadFile('https://github.com/SeaPower-Modders/AnchorChain/releases/latest/download/ACPreloader.zip', $zip)
            }
            $x = J $tmp 'x'
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [IO.Compression.ZipFile]::ExtractToDirectory($zip, $x)
            $hits = @(Get-ChildItem -LiteralPath $x -Recurse -Force -Filter 'winhttp.dll')
            if ($hits.Count -ne 1) { throw ('expected one winhttp.dll in ACPreloader.zip, found ' + $hits.Count) }
            $src = $hits[0].DirectoryName
            foreach ($n in 'doorstop_config.ini', 'BepInEx') { if (-not (Test-Path -LiteralPath (J $src $n))) { throw ($n + ' is not next to winhttp.dll in ACPreloader.zip') } }
            $items = @(Get-ChildItem -LiteralPath $src -Force | Where-Object { $_.Name -ne 'changelog.txt' })
            $clash = @($items | Where-Object { Test-Path -LiteralPath (J $game $_.Name) })
            if ($clash.Count) { throw ('already in the game folder: ' + (($clash | ForEach-Object { $_.Name }) -join ', ')) }
            $items | Copy-Item -Destination $game -Recurse -Force
            Say ('  [done] Anchor Chain preloader installed: ' + (($items | ForEach-Object { $_.Name }) -join ', ')) 'Green'
        }
        catch {
            $warnings++
            Say ('  [!!] Anchor Chain preloader NOT installed: ' + $_.Exception.Message) 'Yellow'
            Say '       Install it by hand: Anchor Chain''s Workshop page links the ACPreloader.zip; copy everything in the folder that holds winhttp.dll next to Sea Power.exe.' 'Yellow'
        }
        finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
    } elseif ($hasDll -and $hasBep) {
        if (@(Get-ChildItem -LiteralPath (J $game 'BepInEx') -Recurse -Force -Filter '*AnchorChain*' -ErrorAction SilentlyContinue).Count) {
            Say '  [ok]   Anchor Chain preloader already installed' 'Green'
        } else {
            $warnings++
            Say '  [!!]   BepInEx is installed but Anchor Chain''s preloader is not in it. Left alone.' 'Yellow'
            Say '         Copy the BepInEx folder from ACPreloader.zip (Anchor Chain''s Workshop page links it) over the game''s one.' 'Yellow'
        }
    } else {
        $warnings++
        Say '  [!!]   The game folder has part of a BepInEx install (winhttp.dll or BepInEx, not both). Left alone.' 'Yellow'
        Say '         If Coordinated Strike Tool''s F8 planner does not open in a mission, reinstall the preloader from Anchor Chain''s page.' 'Yellow'
    }

    # 2. debug switch that can freeze missions
    $dbg = J $content '3789188689' 'debug.ini'
    if (Test-Path -LiteralPath $dbg) {
        try {
            $d = ReadText $dbg
            if ($d.Text -match '(?m)^\s*Enabled\s*=\s*1\b') {
                WriteText $dbg ([regex]::Replace($d.Text, '(?m)^(\s*Enabled\s*=\s*)1\b', '${1}0')) $d.Bom
                Say '  [done] PLA & PLAN & PLAAF AEP debug logging switched off' 'Green'
            } else { Say '  [ok]   PLA & PLAN & PLAAF AEP debug logging already off' 'Green' }
        }
        catch {
            $warnings++
            Say ('  [!!]   Could not switch off the PLA & PLAN & PLAAF AEP debug logging: ' + $_.Exception.Message) 'Yellow'
            Say ('         Open ' + $dbg + ' in Notepad and change Enabled=1 to Enabled=0.') 'Yellow'
        }
    }

    # 3. mods the Mod Manager lists as not compatible (the rule is above the
    # Compat* functions), although they load and play. SETUP rewrites only an
    # ApproximateVersion made for an OLDER game version (also one like 0.8 or
    # 0.8.7.1 that is not written MAJOR.MINOR.PATCH, judged by the numbers it
    # starts with: CompatVerdict), to the game's MAJOR.MINOR.0, which every
    # patch of this game version accepts, with a comment above it; the
    # author's file is kept first. A file it marked before is judged again,
    # so after a game update that lists it again only its value is rewritten
    # (the kept file stays the author's). If the game went back a version,
    # so that a mark is now ahead of it, the author's kept file decides
    # (CompatBack): marked again, or put back if SETUP would leave it alone.
    # One made for a NEWER game version is named and left alone, unless it is
    # a reviewed one (CompatReviewed) with no .dll. A reviewed one marked
    # before that now holds a .dll gets its author's kept file back if SETUP
    # would leave that file alone; with no author's file kept it is named and
    # left marked (CompatCode).
    # An ExactVersion or a range is named and left alone too. Only the mods
    # the pack lists; Steam puts a mod's own file back when the mod updates.
    # A mod whose file cannot be read, judged, kept or written is one [!!]
    # warning, and the next mod is checked.
    try {
        $gameVer = $null
        foreach ($chg in @((J $game 'changelog.txt'), (J $game 'Sea Power_Data' 'changelog.txt'))) {
            if ($gameVer -or -not (Test-Path -LiteralPath $chg)) { continue }
            $vm = [regex]::Match((ReadText $chg).Text, '(?m)^\d{1,2}-[A-Za-z]{3}-\d{4}:\s+(\d+\.\d+\.\d+)\s+Build')
            if ($vm.Success) { $gameVer = $vm.Groups[1].Value }
        }
        if (-not $gameVer) { throw 'the game''s version was not found in its changelog.txt' }
        $gameV = CompatVer $gameVer
        if ($null -eq $gameV) { throw ('the game''s version ' + $gameVer + ' in its changelog.txt is not MAJOR.MINOR.PATCH') }
        $newVer = $gameV[0] + '.' + $gameV[1] + '.0'
        $keep = KeepDir
        $older = 0; $again = 0; $already = 0; $back = 0; $leftOlder = $false; $reviewed = @(); $newer = @(); $left = @()
        $codeBack = @(); $codeLeft = @(); $broken = @()
        foreach ($i in $ids) {
            try {
                $inf = J $content $i '_info.ini'
                if (-not (Test-Path -LiteralPath $inf)) { continue }
                $r = ReadText $inf
                $was = $r.Text.IndexOf($CompatMarker, [StringComparison]::Ordinal) -ge 0
                $plan = CompatPlan $r.Text $gameV $i (J $content $i)
                if ($was -and $plan.Why -ne 'newer') {
                    # A reviewed mod marked before (by SETUP or GPT's script)
                    # that now holds a .dll: judged by the author's file.
                    $kp = J $keep ($i + '._info.ini'); $kb = $null
                    if (Test-Path -LiteralPath $kp) { $kb = [IO.File]::ReadAllBytes($kp) }
                    $code = CompatCode $plan $kb $CompatMarker $gameV $i (J $content $i)
                    if ($code -eq 'back') {
                        [IO.File]::WriteAllBytes($inf, $kb)
                        Remove-Item -LiteralPath $kp -Force
                        $codeBack += ($names[$i] + ' (' + $plan.What + ')')
                        continue
                    }
                    if ($code -eq 'gone') { $codeLeft += $names[$i]; continue }
                }
                if ($plan.Why -eq 'ok') { if ($was) { $already++ }; continue }
                if ($was -and $plan.Why -eq 'newer') {
                    # SETUP's own mark is ahead of the game: judged by the author's file.
                    $kp = J $keep ($i + '._info.ini'); $kb = $null
                    if (Test-Path -LiteralPath $kp) { $kb = [IO.File]::ReadAllBytes($kp) }
                    if (CompatBack $plan $kb $CompatMarker $gameV $i (J $content $i)) {
                        [IO.File]::WriteAllBytes($inf, $kb)
                        Remove-Item -LiteralPath $kp -Force
                        $back++
                        if ($plan.Why -eq 'ok') { continue }
                    }
                }
                if ($plan.Mark -and -not (CompatIsUtf8 ([IO.File]::ReadAllBytes($inf)))) { $plan.Mark = $false; $plan.What += ', not UTF-8 text' }
                if (-not $plan.Mark) {
                    if ($plan.Why -eq 'newer') { $newer += ($names[$i] + ' (' + $plan.What + ')') } else { $left += ($names[$i] + ' (' + $plan.What + ')') }
                    if ($plan.Why -eq 'older') { $leftOlder = $true }
                    continue
                }
                if ($was) {
                    WriteText $inf (CompatMark $r.Text $plan.C $newVer '') $r.Bom
                    if ($plan.Why -eq 'older') { $again++ }
                } else {
                    New-Item -ItemType Directory -Force -Path $keep | Out-Null
                    [IO.File]::WriteAllBytes((J $keep ($i + '._info.ini')), [IO.File]::ReadAllBytes($inf))
                    $note = $CompatMarker + ' (its author''s ApproximateVersion was ' + $plan.C.ApproximateVersion + '); SETUP -RestoreModFiles puts it back'
                    WriteText $inf (CompatMark $r.Text $plan.C $newVer $note) $r.Bom
                }
                if ($plan.Why -eq 'older') { $older++ } else { $reviewed += $names[$i] }
            }
            catch { $broken += ($names[$i] + ': ' + $_.Exception.Message) }
        }
        if ($older) {
            $t = '  [done] ' + $older + ' mod(s) made for an older game version marked compatible with ' + $gameVer + ' (the start-up warning about them stops'
            if ($again) { $t += '; ' + $again + ' of them marked before, for another game version' }
            Say ($t + ')') 'Green'
        }
        if ($reviewed.Count) { Say ('  [done] made for a newer game version but reviewed, so marked compatible with ' + $gameVer + ': ' + ($reviewed -join ', ')) 'Green' }
        if ($back) { Say ('  [done] ' + $back + ' mod file(s) SETUP had marked for a later game version than ' + $gameVer + ' put back as their authors shipped them') 'Green' }
        if ($codeBack.Count) { Say ('  [done] reviewed mod(s) whose folder now holds a .dll put back as their authors shipped them: ' + ($codeBack -join ', ')) 'Green' }
        if (-not $older -and -not $reviewed.Count) {
            # $broken holds the mods whose file could not be read, judged,
            # kept or written: each is a [!!] warning below, and this line
            # does not speak for them.
            $other = 'mod'; if ($leftOlder) { $other = 'mod that SETUP can change' }
            $tail = ''; if ($broken.Count) { $tail = ' (not counting the ' + $broken.Count + ' with a [!!] warning below)' }
            if ($already) { Say ('  [ok]   ' + $already + ' mod(s) already marked compatible with ' + $gameVer + '; no other ' + $other + ' is made for an older game version' + $tail) 'Green' }
            else { Say ('  [ok]   no ' + $other + ' is made for an older game version' + $tail) 'Green' }
        }
        if ($newer.Count) { Say ('         Not marked, made for a newer game version than ' + $gameVer + ' (listed as not compatible until the game catches up): ' + ($newer -join ', ')) }
        if ($left.Count) { Say ('         Not marked, declared in a way SETUP does not change (listed as not compatible): ' + ($left -join ', ')) }
        if ($codeLeft.Count) { Say ('         Left as marked before, reviewed mod(s) whose folder now holds a .dll, with no author''s file kept to put back: ' + ($codeLeft -join ', ')) }
        foreach ($f in $broken) {
            $warnings++
            Say ('  [!!]   Could not check or mark ' + $f) 'Yellow'
        }
        if ($broken.Count) { Say '         Run SETUP again with the game closed. Until then the Mod Manager may list them as not compatible at start-up; they load and play anyway.' 'Yellow' }
    }
    catch {
        $warnings++
        Say ('  [!!]   Could not mark the older mods compatible: ' + $_.Exception.Message) 'Yellow'
        Say '         The Mod Manager will list them as not compatible at start-up. They load and play anyway.' 'Yellow'
    }

    # 4. Contact Log's default keys, if that mod is installed: its window key
    # F6 clashes with Topographic Map's F6 and its diagnostic-probe key F8
    # with Coordinated Strike Tool's F8 planner (and the probe can stall the
    # game). sest-ui-keys.ps1, beside this file, sets just those two to None
    # while they still hold those defaults; a key the player chose is kept.
    # Only when Contact Log's settings file exists: nothing is created. With
    # Contact Log downloaded (Workshop 3819427362) but no settings file yet
    # (it is written when the game first starts with the mod), one note says
    # to start the game once and run SETUP again.
    $uiKeys = J $PSScriptRoot 'sest-ui-keys.ps1'
    $clCfg = J $game 'BepInEx' 'config' 'com.seapower.contactlog.cfg'
    if ((Test-Path -LiteralPath $uiKeys) -and (Test-Path -LiteralPath $clCfg)) {
        try { & $uiKeys -GameDir $game | Out-Null }
        catch {
            $warnings++
            Say ('  [!!]   Contact Log''s keys were not changed: ' + $_.Exception.Message) 'Yellow'
            Say ('         Its F6 clashes with Topographic Map''s F6 and its F8 probe with Coordinated Strike Tool''s F8 planner: set ToggleWindow and RunProbe to None in ' + $clCfg) 'Yellow'
        }
    } elseif ((Test-Path -LiteralPath $uiKeys) -and (Test-Path -LiteralPath (J $content '3819427362'))) {
        Say '  [note] Contact Log has no settings file yet. Start Sea Power once with it, quit, then run SETUP again to free its default F6 (Topographic Map''s F6) and F8 (Coordinated Strike Tool''s F8 planner).'
    }

    # 5. mod order: the SEST pack first, then every mod in the tested order
    $count = [int]$num.Groups[1].Value
    $current = [ordered]@{}
    foreach ($e in [regex]::Matches($bodyText, '(?m)^\s*Mod(\d+)Directory=([^,\r\n]+),(True|False)')) {
        if ([int]$e.Groups[1].Value -le $count -and -not $current.Contains($e.Groups[2].Value)) { $current[$e.Groups[2].Value] = $e.Groups[3].Value }
    }
    $want = @($pack.Name) + @($ids)
    $final = New-Object System.Collections.Generic.List[string]
    $flags = @{}
    $turnedOn = 0
    foreach ($t in $want) {
        $final.Add($t); $flags[$t] = 'True'
        if (-not $current.Contains($t) -or $current[$t] -ne 'True') { $turnedOn++ }
    }
    $others = @()
    foreach ($t in $current.Keys) {
        if ($final.Contains($t)) { continue }
        if ($t -match '^\d+$' -and -not (Test-Path -LiteralPath (J $content $t))) { continue }
        if ($t -notmatch '^\d+$' -and -not (Test-Path -LiteralPath (J $sa $t))) { continue }
        $final.Add($t); $flags[$t] = $current[$t]; $others += $t
    }
    $lines = @('[LoadOrder]', ('NumberOfModFiles=' + $final.Count))
    for ($i = 0; $i -lt $final.Count; $i++) { $lines += ('Mod' + ($i + 1) + 'Directory=' + $final[$i] + ',' + $flags[$final[$i]]) }
    $blank = 0
    for ($i = $body.Count - 1; $i -ge 0 -and $body[$i].Trim() -eq ''; $i--) { $blank++ }
    $out = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $h; $i++) { $out.Add($all[$i]) }
    foreach ($l in $lines) { $out.Add($l) }
    for ($i = 0; $i -lt $blank; $i++) { $out.Add('') }
    for ($i = $end; $i -lt $all.Count; $i++) { $out.Add($all[$i]) }
    $newText = $out -join $nl
    $backup = $settings + '.bak_sest_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
    Copy-Item -LiteralPath $settings -Destination $backup
    WriteText $settings $newText $st.Bom
    Say ('  [done] mod order set: SEST pack first, then the ' + $ids.Count + ' mods (' + $turnedOn + ' switched on or added)') 'Green'
    if ($others.Count) { Say ('         your ' + $others.Count + ' other mod(s) moved to the bottom, on/off as you had them') }
    Say ('         settings backup: ' + $backup)

    Say ''
    if ($warnings) { Say ('Done, but read the ' + $warnings + ' [!!] warning(s) above first. Then start Sea Power:') 'Yellow' }
    else { Say 'All done. Start Sea Power:' 'Cyan' }
    Say '  - Mod Manager: the SEST Integration Pack is at the top and ticked. If it offers to move or fix dependencies, say no.'
    Say '  - Campaigns: Southern Watch, Southern Reach - Tasman Shield, Red Line - The Other Watch, or Sulu Line - The Island Road.'
    Say '  - Dynamic campaigns (Dynamic Campaign Mod): in the Campaign menu, marked [Dynamic].'
    Say 'Run SETUP again (game closed) whenever the pack updates, or after Steam updates your mods (if a mission freezes, or the not-compatible warning is back).'
    Hold
}
catch { Fail ('Unexpected error: ' + $_.Exception.Message) }
