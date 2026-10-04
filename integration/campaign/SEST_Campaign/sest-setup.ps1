# SEST Integration Pack - setup for Sea Power. Run with the game closed.
#
# Double-click "SETUP - double-click me.cmd" beside this file (Mod Manager >
# Open Folder on the pack gets you here). It checks that every Workshop mod
# the campaigns were built against is downloaded, installs the Anchor Chain
# preloader if it is missing, turns off one mod's debug logging that can
# freeze a mission, and writes the Mod Manager order: this pack first, then
# the mods in the order they were tested in, your other mods at the bottom
# as you had them. Safe to run again: it checks everything before it
# changes anything, and it backs up the game's settings first.
#
# From a console:  powershell -ExecutionPolicy Bypass -File .\sest-setup.ps1
param([switch]$Pause, [switch]$Elevated)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
function J { $p = [string]$args[0]; for ($k = 1; $k -lt $args.Count; $k++) { $p = [IO.Path]::Combine($p, [string]$args[$k]) }; $p }
function Say([string]$t, [string]$c = 'Gray') { Write-Host $t -ForegroundColor $c }
function Same([string]$a, [string]$b) {
    if (-not $a -or -not $b) { return $false }
    return [IO.Path]::GetFullPath($a).TrimEnd('\', '/') -ieq [IO.Path]::GetFullPath($b).TrimEnd('\', '/')
}
function Hold { if ($Pause) { Write-Host ''; [void](Read-Host 'Press Enter to close this window') } }
$changed = $false
$warnings = 0
function Fail([string]$t) {
    Write-Host ''
    Write-Host ('STOPPED: ' + $t) -ForegroundColor Red
    if ($changed) { Write-Host 'Some changes above were already made. Sort this out, then run SETUP again.' -ForegroundColor Red }
    else { Write-Host 'Nothing was changed. Sort that out, then run SETUP again.' -ForegroundColor Red }
    Hold
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
function IsPack([string]$dir) {
    return $dir -and (Test-Path -LiteralPath (J $dir 'LOAD-ORDER.txt')) -and (Test-Path -LiteralPath (J $dir 'campaigns' 'sest-southern-watch' 'campaign.ini'))
}
$AppId = '1286220'
try {
    Say 'SEST setup - checking your PC...' 'Cyan'

    if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) {
        Fail 'Sea Power is running. Quit the game completely first.'; return
    }

    # --- Steam, the game and its Workshop folder ---------------------------
    $steam = $env:SEST_STEAM_ROOT
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
    $settings = $env:SEST_SETTINGS
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
            $exe = (Get-Process -Id $PID).Path
            $argv = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $PSCommandPath + '"'), '-Elevated', '-Pause')
            try { Start-Process -FilePath $exe -ArgumentList $argv -Verb RunAs -Wait }
            catch { Fail 'Administrator permission was not given, so the preloader was not installed and nothing else was changed. Run SETUP again and click Yes, or install the preloader by hand from Anchor Chain''s Workshop page and run SETUP again.'; return }
            Say 'Finished in the administrator window.'
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
        New-Item -ItemType Directory -Path $tmp | Out-Null
        try {
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

    # 3. mod order: the SEST pack first, then every mod in the tested order
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
    Say '  - Campaigns: Southern Watch, Southern Reach - Tasman Shield, or Red Line - The Other Watch.'
    Say '    The "Open Allocation" versions sell the whole roster from the first mission; the others release it as the story goes.'
    Say 'Run SETUP again (game closed) whenever the pack updates, or if a mission freezes after Steam updates your mods.'
    Hold
}
catch { Fail ('Unexpected error: ' + $_.Exception.Message) }
