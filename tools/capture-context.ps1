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
      player.log / -prev.log  the Unity log: mods loaded, missing files,
                              exceptions with stack traces. The KJ-500 crash
                              was diagnosed from a stack trace pasted by hand;
                              this makes that a file in the repo.
      game-build.txt          install build/version, so the packs'
                              ApproximateVersion claims can be checked
      workshop-subscriptions.txt  every subscribed id with its _info.ini name,
                              which is how new mods get catalogued
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
    [int]$LogTailLines = 4000
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
$lines = @("# Every subscribed Workshop item on disk, with its in-game name.",
           "# New ids here that are absent from data\load-order.tokens.txt need a position.", "")
$seen = @{}
foreach ($lib in Get-SteamLibraries) {
    $content = Join-Path $lib "workshop\content\1286220"
    if (-not (Test-Path $content)) { continue }
    foreach ($d in Get-ChildItem -LiteralPath $content -Directory | Sort-Object Name) {
        if ($seen.ContainsKey($d.Name)) { continue }
        $seen[$d.Name] = $true
        $lines += ("{0,-12} {1,-52} updated {2:yyyy-MM-dd}" -f $d.Name, (Get-ModDisplayName $d.FullName), $d.LastWriteTime)
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
Write-Snapshot "workshop-subscriptions.txt" $lines

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
