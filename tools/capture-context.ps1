<#
.SYNOPSIS
    Snapshot the live Sea Power install into the repo so reviews argue from
    evidence instead of assumption.

.DESCRIPTION
    Everything this repo knows is what SHOULD be true: the canonical order, the
    catalog, the built packs. What actually happened on the machine - which mods
    the game loaded, what it logged, what is really sitting in StreamingAssets -
    has only ever reached the repo as pasted terminal output, and every hard bug
    this session cost a round trip asking for it. This writes it into
    data\install-snapshot\ where it can be committed, diffed and reviewed.

    Read-only against the game. It copies and lists; it changes nothing.

    Captures:
      load-order.live.txt     the [LoadOrder] the game is really using, with
                              names, enabled flags, and the drift against
                              data\load-order.tokens.txt
      streaming-assets.txt    what is actually installed - the question that
                              took two round trips when the per-pack folders
                              were superseded by SEST_Integration
      streaming-media.txt     every picture and film under original\ and the
                              Workshop's loading/menu pictures - the folder a
                              replacement loading screen must use
      plugin-dlls.txt         every code DLL the game can load - Workshop mods,
                              BepInEx, the Anchor Chain preloader, SEST plugins -
                              with size, SHA-256 and version: a plugin update
                              changes behaviour with no .ini changing
      ui-assets.txt           the background, loading and menu picture names
                              inside the game's own Unity data and code - what
                              the SEST plugin must find to swap one
                              (tools\scan-ui-assets.ps1; rescanned only when
                              the game's data changes)
      player.log / -prev.log  the Unity log: mods loaded, missing files,
                              exceptions with stack traces, the SEST menu
                              plugin's [SEST Menu] and [SEST Pictures] lines.
                              The KJ-500 crash
                              was diagnosed from a stack trace pasted by hand;
                              this makes that a file in the repo.
      game-build.txt          install build/version, so the packs'
                              ApproximateVersion claims can be checked
      workshop-subscriptions.txt  every subscribed id with its _info.ini name,
                              which is how new mods get catalogued, checked
                              both ways against Steam's own record
                              (appworkshop_1286220.acf). "updated" is Steam's
                              timeupdated for the item from that record; the
                              folder's last-write time follows as a second
                              column, "folder". Until 14 Oct 2026 the folder
                              time was the only date, and it misses an update
                              that only rewrites files inside existing
                              subfolders
      bepinex.log             BepInEx\LogOutput.log, where the code mods write,
                              whole (a file over -BepInExCapBytes, 50 MB, is
                              kept as its first and last 20,000 lines with a
                              marker line between). Until 14 Oct 2026 only
                              the last 600 lines were kept
      environment.txt         when, on what, and by which tool version

    Logs can carry the local user name in paths; -Redact rewrites the profile
    path to <USER> before writing. Nothing else is filtered - read what you
    commit.

.EXAMPLE
    # game CLOSED (its log is only complete after exit), from the repo root:
    powershell -ExecutionPolicy Bypass -File .\tools\capture-context.ps1
    git add data\install-snapshot ; git commit -m "Capture install snapshot" ; git push
#>
[CmdletBinding()]
param(
    [string]$SettingsPath = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini"),
    [string]$StreamingAssetsDir,
    [switch]$Redact,
    [switch]$IncludeSaves,
    # 20,000 since 14 Oct 2026: the SEST menu plugin's [SEST Pictures] passes can
    # add several thousand lines, and the tail must still hold the whole log.
    [int]$LogTailLines = 20000,
    # BepInEx\LogOutput.log is copied whole up to this size; a larger one is
    # kept as its first and last $LogTailLines lines with a marker between.
    [long]$BepInExCapBytes = 50MB
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")

$repoRoot = Split-Path -Parent $scriptDir
$outDir   = Join-Path $repoRoot "data\install-snapshot"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Write-Snapshot([string]$Name, [string[]]$Lines) {
    $text = ($Lines -join "`r`n") + "`r`n"
    if ($Redact) { $text = $text.Replace($env:USERPROFILE, "<USER>").Replace($env:USERNAME, "<USER>") }
    [System.IO.File]::WriteAllText((Join-Path $outDir $Name), $text)
    Write-Host ("  wrote  {0,-30} {1} line(s)" -f $Name, $Lines.Count)
}

Write-Host "Capturing live install context into data\install-snapshot" -ForegroundColor Cyan
if (Test-SeaPowerRunning) {
    Write-Warning "Sea Power is RUNNING. Its log is written as it goes and is only complete after exit; the load order is rewritten on exit too. Capture again once you have quit."
}

# --- 1. the order the game is really using ----------------------------------
$lines = @("# The [LoadOrder] Sea Power is actually using, captured $(Get-Date -Format s).",
           "# Compare against data\load-order.tokens.txt - the canonical order.", "")
if (Test-Path -LiteralPath $SettingsPath) {
    $sec = [regex]::Match((Get-Content -LiteralPath $SettingsPath -Raw), "(?s)\[LoadOrder\]\r?\n(.*?)(?=\r?\n\[|$)")
    $live = [ordered]@{}
    if ($sec.Success) {
        $count = [int]([regex]::Match($sec.Groups[1].Value, "NumberOfModFiles=(\d+)").Groups[1].Value)
        foreach ($m in [regex]::Matches($sec.Groups[1].Value, "Mod(\d+)Directory=([^,\r\n]+),(True|False)")) {
            if ([int]$m.Groups[1].Value -le $count -and -not $live.Contains($m.Groups[2].Value)) {
                $live[$m.Groups[2].Value] = $m.Groups[3].Value
            }
        }
        $lines += "NumberOfModFiles=$count   entries parsed: $($live.Count)"; $lines += ""
        $i = 0
        foreach ($tok in $live.Keys) {
            $i++
            $name = ""
            foreach ($lib in Get-SteamLibraries) {
                $d = Join-Path $lib "workshop\content\1286220\$tok"
                if (Test-Path $d) { $name = Get-ModDisplayName $d; break }
            }
            $lines += ("{0,4}. {1,-12} {2,-6} {3}" -f $i, $tok, $(if ($live[$tok] -eq "False") { "OFF" } else { "on" }), $name)
        }
        $canonPath = Join-Path $repoRoot "data\load-order.tokens.txt"
        if (Test-Path $canonPath) {
            $canon = Get-Content -LiteralPath $canonPath | Where-Object { $_ -and $_ -notmatch "^#" }
            $lines += ""; $lines += "--- drift against the canonical order ---"
            $missing = $canon | Where-Object { -not $live.Contains($_) }
            $extra   = $live.Keys | Where-Object { $canon -notcontains $_ }
            $lines += "canonical but not live ($($missing.Count)): $($missing -join ', ')"
            $lines += "live but not canonical ($($extra.Count)): $($extra -join ', ')"
            $shared = $canon | Where-Object { $live.Contains($_) }
            $liveShared = $live.Keys | Where-Object { $canon -contains $_ }
            $lines += "order of shared entries matches: $(if (-not (Compare-Object $shared $liveShared -SyncWindow 0)) { 'YES' } else { 'NO - the game has reordered them' })"
            $off = $live.Keys | Where-Object { $live[$_] -eq "False" }
            $lines += "disabled in game ($($off.Count)): $($off -join ', ')"
        }
    } else { $lines += "[LoadOrder] section not found" }
} else { $lines += "usersettings.ini not found at $SettingsPath" }
Write-Snapshot "load-order.live.txt" $lines

# --- 2. what is actually installed ------------------------------------------
if (-not $StreamingAssetsDir) { $StreamingAssetsDir = Find-StreamingAssets }
$lines = @("# Contents of StreamingAssets - what is REALLY installed.", "")
if ($StreamingAssetsDir -and (Test-Path -LiteralPath $StreamingAssetsDir)) {
    $lines += "StreamingAssets: $StreamingAssetsDir"; $lines += ""
    foreach ($d in Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory | Sort-Object Name) {
        $n = @(Get-ChildItem -LiteralPath $d.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
        $lines += ("{0,-34} {1,6} file(s)   modified {2:yyyy-MM-dd HH:mm}" -f $d.Name, $n, $d.LastWriteTime)
    }
    $sest = @(Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory -Filter "SEST_*")
    $lines += ""; $lines += "SEST folders present: $($sest.Count) -> $(($sest | ForEach-Object Name) -join ', ')"
    $lines += "(expected: exactly one, SEST_Integration - per-pack folders are superseded)"
} else { $lines += "StreamingAssets not found" }
Write-Snapshot "streaming-assets.txt" $lines

# --- 2b. the game's own pictures and films ------------------------------------
# The loading screen draws its backgrounds through the game's FileManager
# (changelog: "LoadScreen to use FileManager to get backgrounds"), the same
# lookup that lets a mod's file stand in for one under original\ - but the
# repo's copy of original\ is text only, so which folder and names it reads
# was unknown (10 Oct 2026, the media pack). This lists every picture and
# film under original\ by relative path and size, and any Workshop mod's
# picture whose path says load, background, menu or splash, so the folder a
# replacement must use is read off the list instead of guessed.
$media = @(".png", ".jpg", ".jpeg", ".tga", ".dds", ".bmp", ".mp4", ".webm", ".ogv", ".mov")
$lines = @("# Pictures and films under StreamingAssets\original, and Workshop pictures named",
           "# for loading screens, backgrounds or menus. Relative path, size in KB.", "")
if ($StreamingAssetsDir -and (Test-Path -LiteralPath (Join-Path $StreamingAssetsDir "original"))) {
    $orig = Join-Path $StreamingAssetsDir "original"
    $files = @(Get-ChildItem -LiteralPath $orig -Recurse -File -ErrorAction SilentlyContinue |
               Where-Object { $media -contains $_.Extension.ToLower() } | Sort-Object FullName)
    $lines += "original\: $($files.Count) picture/film file(s)"
    $byDir = $files | Group-Object { Split-Path -Parent $_.FullName.Substring($orig.Length + 1) }
    foreach ($g in ($byDir | Sort-Object Name)) {
        $lines += ""; $lines += "[$(if ($g.Name) { $g.Name } else { '.' })]  $($g.Count) file(s)"
        foreach ($f in ($g.Group | Select-Object -First 60)) {
            $lines += ("  {0,-60} {1,8:N0}" -f $f.Name, ($f.Length / 1KB))
        }
        if ($g.Count -gt 60) { $lines += "  ... and $($g.Count - 60) more" }
    }
} else { $lines += "StreamingAssets\original not found" }
$lines += ""; $lines += "--- Workshop pictures named for loading screens, backgrounds or menus ---"
# Every match is listed, up to $maxPictureLines in all; the rest are counted.
# Until 14 Oct 2026 the list stopped at 200 entries, and 169 of those were
# the Custom Loadout Editor's ui\loadout_icons ("load" matched "loadout"), so
# SEST's own 80 loading screens never made the list. Loadout icons are no
# longer matched.
$maxPictureLines = 2000
$content = Find-WorkshopContent
if ($content) {
    $pics = @(Get-ChildItem -LiteralPath $content -Recurse -File -ErrorAction SilentlyContinue |
              Where-Object { $media -contains $_.Extension.ToLower() -and
                             $_.FullName.Substring($content.Length) -match "load(?!out)|background|menu|splash" } |
              Sort-Object FullName)
    $byMod = @($pics | Group-Object { ($_.FullName.Substring($content.Length).TrimStart('\', '/') -split '[\\/]')[0] })
    $lines += ("{0} file(s) in {1} mod(s): {2}" -f $pics.Count, $byMod.Count,
               (($byMod | Sort-Object Name | ForEach-Object { "$($_.Name) ($($_.Count))" }) -join ", "))
    foreach ($f in ($pics | Select-Object -First $maxPictureLines)) {
        $lines += ("  {0,-90} {1,8:N0}" -f $f.FullName.Substring($content.Length + 1), ($f.Length / 1KB))
    }
    if ($pics.Count -gt $maxPictureLines) { $lines += "  ... and $($pics.Count - $maxPictureLines) more (listing stops at $maxPictureLines entries)" }
} else { $lines += "no Workshop content folder found" }
Write-Snapshot "streaming-media.txt" $lines

# --- 2c. pictures built into the game's Unity data -----------------------------
# Every file-based loading screen is replaced, yet some screens still showed
# the game's pictures (10 Oct 2026: between menu pages, a first load, the Mod
# Manager) - pictures inside the game's Unity data, which only the SEST plugin
# can swap, and only by name. Read only; see the script.
if ($StreamingAssetsDir -and (Test-Path -LiteralPath $StreamingAssetsDir)) {
    try {
        & (Join-Path $scriptDir "scan-ui-assets.ps1") -DataDir (Split-Path -Parent $StreamingAssetsDir) `
            -OutFile (Join-Path $outDir "ui-assets.txt")
    } catch { Write-Warning "ui-assets.txt not written: $($_.Exception.Message)" }
}

# --- 2d. plugin DLLs -------------------------------------------------------------
# The export copies text only, so a code mod's update (Dynamic Campaign Mod,
# Identify Expanded, Anchor Chain, decoy and resupply plugins) left no trace in
# the repo though it can change what the game does. Name, size, SHA-256 and the
# file's own version for every DLL the game can load. Read only.
$lines = @("# Code DLLs the game can load: Workshop mods, the game folder (BepInEx, the",
           "# Anchor Chain preloader) and the SEST pack's plugins. Size in bytes, SHA-256,",
           "# file version / product version, last write time.", "")
$dllRoots = @()
foreach ($lib in Get-SteamLibraries) {
    $content = Join-Path $lib "workshop\content\1286220"
    if (Test-Path -LiteralPath $content) { $dllRoots += ,@("workshop", $content); break }
}
if ($StreamingAssetsDir -and (Test-Path -LiteralPath $StreamingAssetsDir)) {
    $gameDir = Split-Path -Parent (Split-Path -Parent $StreamingAssetsDir)
    foreach ($sub in @("BepInEx", "")) {
        $d = if ($sub) { Join-Path $gameDir $sub } else { $gameDir }
        if (Test-Path -LiteralPath $d) { $dllRoots += ,@("game\$sub".TrimEnd("\"), $d) }
    }
    $sestPlugins = Join-Path $StreamingAssetsDir "SEST_Integration\plugins"
    if (Test-Path -LiteralPath $sestPlugins) { $dllRoots += ,@("SEST_Integration\plugins", $sestPlugins) }
}
foreach ($root in $dllRoots) {
    $label, $dir = $root[0], $root[1]
    # the game folder itself: only the loose DLLs beside Sea Power.exe (winhttp.dll and friends)
    $files = if ($label -eq "game") { @(Get-ChildItem -LiteralPath $dir -File -Filter *.dll -ErrorAction SilentlyContinue) }
             else { @(Get-ChildItem -LiteralPath $dir -Recurse -File -Filter *.dll -ErrorAction SilentlyContinue) }
    $lines += "[$label]  $($files.Count) DLL(s)"
    foreach ($f in ($files | Sort-Object FullName)) {
        $rel = $f.FullName.Substring($dir.Length).TrimStart("\", "/")
        $hash = try { (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLower() } catch { "unreadable" }
        $vi = try { [System.Diagnostics.FileVersionInfo]::GetVersionInfo($f.FullName) } catch { $null }
        $ver = if ($vi) { "$($vi.FileVersion) / $($vi.ProductVersion)" } else { "-" }
        $lines += ("  {0}  {1,10}  {2}  {3}  {4:yyyy-MM-dd HH:mm}" -f $rel, $f.Length, $hash, $ver, $f.LastWriteTime)
    }
    $lines += ""
}
Write-Snapshot "plugin-dlls.txt" $lines

# --- 3. the game's own log ---------------------------------------------------
$logDir = Split-Path -Parent $SettingsPath
foreach ($pair in @(@("Player.log", "player.log"), @("Player-prev.log", "player-prev.log"))) {
    $src = Join-Path $logDir $pair[0]
    if (Test-Path -LiteralPath $src) {
        $all = Get-Content -LiteralPath $src -ErrorAction SilentlyContinue
        $keep = if ($all.Count -gt $LogTailLines) { $all[-$LogTailLines..-1] } else { $all }
        $head = @("# $($pair[0]) - last $($keep.Count) of $($all.Count) line(s), captured $(Get-Date -Format s).",
                  "# Unity writes this fresh each launch; -prev is the session before.", "")
        Write-Snapshot $pair[1] ($head + $keep)
        $bad = $all | Select-String -Pattern "Exception|Error|not found|missing|failed" -CaseSensitive:$false
        if ($bad) {
            Write-Snapshot ($pair[1] -replace "\.log$", ".problems.txt") `
                (@("# Lines from $($pair[0]) matching Exception/Error/not found/missing/failed.",
                   "# $($bad.Count) hit(s) - the first place to look when something did not load.", "") +
                 ($bad | ForEach-Object { "{0,7}: {1}" -f $_.LineNumber, $_.Line }))
        }
    } else { Write-Host ("  skipped {0,-30} not present" -f $pair[0]) }
}

# --- 3b. the code mods' log ----------------------------------------------------
# BepInEx writes what the code mods say (Identify Expanded, Anchor Chain and the
# mods it loads) to its own LogOutput.log beside the game, not to Player.log.
# A mod logging on every physics tick froze Steel Highway on 28 Sep and showed
# nowhere else. The whole file is kept: BepInEx starts it fresh each launch,
# so it holds one session, and the 600-line tail kept until 14 Oct 2026 lost
# the plugin load order and the first errors of a session. The cap guards
# against a mod logging every tick (the Steel Highway case): over
# -BepInExCapBytes the head and the tail are kept with a marker line.
if ($StreamingAssetsDir) {
    $bep = Join-Path (Split-Path -Parent (Split-Path -Parent $StreamingAssetsDir)) "BepInEx\LogOutput.log"
    if (Test-Path -LiteralPath $bep) {
        $item = Get-Item -LiteralPath $bep
        $x = Get-LogExcerpt -Path $bep -CapBytes $BepInExCapBytes -HeadLines $LogTailLines -TailLines $LogTailLines
        $what = if ($x.Whole) { "whole file, $($x.Total) line(s)" } else { "first $LogTailLines and last $LogTailLines of $($x.Total) line(s)" }
        Write-Snapshot "bepinex.log" (@("# BepInEx\LogOutput.log - $what, " +
                                        ("{0:N1} MB" -f ($item.Length / 1MB)) +
                                        ", last written $($item.LastWriteTime.ToString('s')).", "") + $x.Lines)
    } else { Write-Host "  skipped bepinex.log                   no BepInEx\LogOutput.log (BepInEx not installed?)" }
}

# --- 4. game build ------------------------------------------------------------
$lines = @("# Installed Sea Power build - what the packs' ApproximateVersion should track.", "")
$exe = $null
if ($StreamingAssetsDir) { $exe = Join-Path (Split-Path -Parent (Split-Path -Parent $StreamingAssetsDir)) "Sea Power.exe" }
if ($exe -and (Test-Path -LiteralPath $exe)) {
    $vi = (Get-Item -LiteralPath $exe).VersionInfo
    $lines += "exe            : $exe"
    $lines += "product version: $($vi.ProductVersion)"
    $lines += "file version   : $($vi.FileVersion)"
    $lines += "modified       : $((Get-Item -LiteralPath $exe).LastWriteTime.ToString('yyyy-MM-dd HH:mm'))"
} else { $lines += "Sea Power.exe not located" }
foreach ($lib in Get-SteamLibraries) {
    $acf = Join-Path $lib "appmanifest_1286220.acf"
    if (Test-Path $acf) {
        $raw = Get-Content -LiteralPath $acf -Raw
        foreach ($k in "buildid", "LastUpdated", "SizeOnDisk") {
            $m = [regex]::Match($raw, "`"$k`"\s+`"([^`"]+)`"")
            if ($m.Success) { $lines += ("steam {0,-12}: {1}" -f $k, $m.Groups[1].Value) }
        }
        break
    }
}
Write-Snapshot "game-build.txt" $lines

# --- 5. subscriptions ---------------------------------------------------------
# Steam's own record first (appworkshop_1286220.acf), because the per-item
# "updated" date comes from it: Steam's timeupdated for the installed version,
# shown in local time. The folder's last-write time follows as "folder"; until
# 14 Oct 2026 it was the only date, and an update that only rewrites files
# inside existing subfolders does not move it, so updates were missed. An id
# Steam has no time for shows "updated unknown".
$acfIds = @{}
$acfUpdated = @{}
$acfPaths = @()
$needsDownload = $null
$needsUpdate = $null
foreach ($lib in Get-SteamLibraries) {
    $acf = Join-Path $lib "workshop\appworkshop_$SeaPowerAppId.acf"
    # Get-SteamLibraries can return one library twice in different letter
    # case (registry vs Program Files); -contains compares case-insensitively.
    if (-not (Test-Path $acf) -or $acfPaths -contains $acf) { continue }
    $acfPaths += $acf
    $rec = Read-WorkshopAcf -Path $acf
    foreach ($id in $rec.Ids.Keys) { $acfIds[$id] = $true }
    foreach ($id in $rec.Updated.Keys) { if (-not $acfUpdated.ContainsKey($id)) { $acfUpdated[$id] = $rec.Updated[$id] } }
    if ($null -ne $rec.NeedsDownload -and $null -eq $needsDownload) { $needsDownload = $rec.NeedsDownload }
    if ($null -ne $rec.NeedsUpdate   -and $null -eq $needsUpdate)   { $needsUpdate   = $rec.NeedsUpdate }
}

$lines = @("# Every subscribed Workshop item on disk, with its in-game name.",
           "# New ids here that are absent from data\load-order.tokens.txt need a position.",
           "# updated = Steam's timeupdated for the installed version (appworkshop_$SeaPowerAppId.acf, local time);",
           "# folder = the folder's last-write time, which an update inside existing subfolders does not move.", "")
$seen = @{}
foreach ($lib in Get-SteamLibraries) {
    $content = Join-Path $lib "workshop\content\$SeaPowerAppId"
    if (-not (Test-Path $content)) { continue }
    foreach ($d in Get-ChildItem -LiteralPath $content -Directory | Sort-Object Name) {
        if ($seen.ContainsKey($d.Name)) { continue }
        $seen[$d.Name] = $true
        $when = if ($acfUpdated.ContainsKey($d.Name)) { $acfUpdated[$d.Name].ToString("yyyy-MM-dd HH:mm") } else { "unknown" }
        $lines += ("{0,-12} {1,-52} updated {2}  folder {3:yyyy-MM-dd HH:mm}" -f $d.Name, (Get-ModDisplayName $d.FullName), $when, $d.LastWriteTime)
    }
}
$canonPath = Join-Path $repoRoot "data\load-order.tokens.txt"
if (Test-Path $canonPath) {
    $canon = Get-Content -LiteralPath $canonPath | Where-Object { $_ -and $_ -notmatch "^#" }
    $new = $seen.Keys | Where-Object { $canon -notcontains $_ } | Sort-Object
    $gone = $canon | Where-Object { $_ -notmatch "^\d+$" -eq $false -and -not $seen.ContainsKey($_) }
    $lines += ""; $lines += "subscribed but UNPLACED ($($new.Count)): $($new -join ', ')"
    $lines += "placed but NOT SUBSCRIBED ($($gone.Count)): $($gone -join ', ')"
}

# --- cross-check the folders against Steam's own local record -------------------
# Everything above counts FOLDERS under workshop\content\1286220. Steam's client
# keeps its own list in appworkshop_1286220.acf, and the Steam UI shows a third
# number that lives on Valve's servers. They can all disagree, and when they do
# the repo has no way to know unless it says so here. Two questions this answers:
# an id Steam tracks with no folder is a download that never landed, and a folder
# Steam does not track is left over from an unsubscribe. The record was read
# above, where the per-item dates come from.
$lines += ""
$lines += "--- Steam client record (appworkshop_$SeaPowerAppId.acf) ---"
if ($acfPaths.Count -eq 0) {
    $lines += "acf not found in any Steam library - cross-check skipped."
} else {
    # @(...) so .Count is valid when the pipeline yields nothing, which is the
    # healthy case and would otherwise render blank instead of 0.
    $trackedNotOnDisk = @($acfIds.Keys | Where-Object { -not $seen.ContainsKey($_) } | Sort-Object)
    $onDiskNotTracked = @($seen.Keys   | Where-Object { -not $acfIds.ContainsKey($_) } | Sort-Object)
    $lines += ("acf file(s)              : {0}" -f ($acfPaths -join ", "))
    $lines += ("folders on disk          : {0}" -f $seen.Count)
    $lines += ("ids Steam tracks locally : {0}" -f $acfIds.Count)
    $lines += ("NeedsDownload / NeedsUpdate: {0} / {1}" -f
               $(if ($null -ne $needsDownload) { $needsDownload } else { "?" }),
               $(if ($null -ne $needsUpdate)   { $needsUpdate }   else { "?" }))
    $lines += ("tracked but NOT on disk ({0}): {1}" -f $trackedNotOnDisk.Count, ($trackedNotOnDisk -join ', '))
    $lines += ("on disk but NOT tracked ({0}): {1}" -f $onDiskNotTracked.Count, ($onDiskNotTracked -join ', '))
    $lines += ""
    $lines += "If the Steam UI's subscribed count is HIGHER than both numbers above, the"
    $lines += "extras are server-side only and there is nothing on this PC to find: the"
    $lines += "usual causes are subscribed Collections, which have no content to download,"
    $lines += "and items the author has delisted, which Steam keeps counting forever."
    $lines += "Neither can load in game, so neither belongs in the load order."
}
Write-Snapshot "workshop-subscriptions.txt" $lines

# --- 5b. what the game ships now ----------------------------------------------
# Everything this repo argues from - "native does X", the condition vocabulary,
# the Task Force Mode keys - is read out of mods-source\_vanilla\original,
# exported at 0.8.3 Build 261001 on 01-Oct-2026. If the installed game has moved
# on, some of those citations are stale and nothing here would say so.
$lines = @("# The live install's own changelog head and campaign list, against the",
           "# export this repo reasons from (0.8.3 Build 261001, 01-Oct-2026).", "")
if ($StreamingAssetsDir) {
    $gameRoot = Split-Path -Parent $StreamingAssetsDir
    $chg = Join-Path $gameRoot "changelog.txt"
    if (-not (Test-Path -LiteralPath $chg)) {
        $chg = Join-Path (Split-Path -Parent $gameRoot) "changelog.txt"
    }
    if (Test-Path -LiteralPath $chg) {
        Copy-Item -LiteralPath $chg -Destination (Join-Path $outDir "changelog.live.txt") -Force
        $lines += "changelog copied to changelog.live.txt; head:"
        $lines += (Get-Content -LiteralPath $chg -TotalCount 12 | ForEach-Object { "    $_" })
    } else { $lines += "changelog.txt not found beside the install" }

    $camp = Join-Path $StreamingAssetsDir "campaigns"
    if (Test-Path -LiteralPath $camp) {
        $have = @("campaign-proto-1", "linear-campaign-proto-1",
                  "pacific-strike-task-force", "strike-group-molniya-campaign")
        $lines += ""; $lines += "campaign folders installed:"
        foreach ($d in Get-ChildItem -LiteralPath $camp -Directory | Sort-Object Name) {
            $mark = if ($have -contains $d.Name) { "" } else { "   <-- NEW, not in the export" }
            $lines += ("    {0}{1}" -f $d.Name, $mark)
        }
    }
} else { $lines += "StreamingAssets not found" }
Write-Snapshot "game-content.txt" $lines

# --- 5c. campaign saves --------------------------------------------------------
# The single thing no amount of reading the shipped files can settle: what a
# Task Force Mode campaign actually PERSISTS. Whether a [CampaignVariables]
# flag survives, how the bought force is stored, how completion and CSAR points
# accumulate. The changelog says a campaign save is a real artefact
# ("Saving mid-mission now properly generates a companion campaign save"), so
# one from any Task Force Mode campaign is worth more than another week of
# inference. Listed always; copied only with -IncludeSaves, because a save is
# personal and may be large.
$saveRoots = @(
    (Join-Path (Split-Path -Parent $SettingsPath) "Saves"),
    (Join-Path (Split-Path -Parent $SettingsPath) "saves"),
    (Join-Path (Split-Path -Parent $SettingsPath) "SaveGames")
) | Where-Object { Test-Path -LiteralPath $_ }
$lines = @("# Campaign and mission saves. The campaign layer of this repo is",
           "# entirely inferred from shipped campaign.ini files; a save is the",
           "# only evidence of what survives between missions.", "")
if ($saveRoots) {
    foreach ($root in $saveRoots) {
        $lines += "root: $root"
        foreach ($f in Get-ChildItem -LiteralPath $root -Recurse -File | Sort-Object LastWriteTime -Descending) {
            $lines += ("    {0,-58} {1,10:N0} bytes  {2:yyyy-MM-dd HH:mm}" -f `
                       $f.FullName.Substring($root.Length).TrimStart('\'), $f.Length, $f.LastWriteTime)
        }
        if ($IncludeSaves) {
            # Campaign saves first, THEN by recency. Sorting on recency alone
            # took 42 MB of mid-mission saves and left the 1 KB campaign files
            # behind - which are the only ones that answer what carries over.
            $dest = Join-Path $outDir "saves"
            New-Item -ItemType Directory -Force -Path $dest | Out-Null
            Get-ChildItem -LiteralPath $root -Recurse -File |
                Sort-Object @{ Expression = {
                                 $_.FullName -notmatch '\\campaigns?\\' -and
                                 $_.BaseName -notmatch 'campaign' } },
                            @{ Expression = 'LastWriteTime'; Descending = $true } |
                Select-Object -First 6 |
                ForEach-Object {
                    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dest $_.Name) -Force
                    $lines += ("    copied: {0}  ({1:N0} bytes)" -f $_.Name, $_.Length)
                }
        } else {
            $lines += "    (listing only - re-run with -IncludeSaves to copy the campaign saves)"
        }
    }
} else { $lines += "no save folder found beside usersettings.ini" }
Write-Snapshot "campaign-saves.txt" $lines

# --- 6. provenance -------------------------------------------------------------
Write-Snapshot "environment.txt" @(
    "captured        : $(Get-Date -Format s)",
    "host os         : $([System.Environment]::OSVersion.VersionString)",
    "powershell      : $($PSVersionTable.PSVersion)",
    "repo commit     : $(try { (git -C $repoRoot rev-parse --short HEAD) } catch { 'unknown' })",
    "repo branch     : $(try { (git -C $repoRoot rev-parse --abbrev-ref HEAD) } catch { 'unknown' })",
    "redacted        : $Redact"
)

Write-Host "`nSnapshot written to data\install-snapshot" -ForegroundColor Green
Write-Host "Review it, then:  git add data\install-snapshot ; git commit -m `"Capture install snapshot`" ; git push"
