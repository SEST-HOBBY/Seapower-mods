<#
    Shared helpers for the SEST tooling. Dot-source it:

        . (Join-Path $PSScriptRoot "lib\common.ps1")

    Everything here is detection only - nothing writes.
#>

# SEST's own published Workshop item: 'SEST Integration Pack - Modernised
# Campaigns', the consolidated SEST_Integration folder as a subscriber gets it.
# It is this project's output, not an upstream mod: never exported into
# mods-source, never counted as a rival in a who-wins calculation, and never
# loaded beside the local SEST_Integration folder - the game must not load
# both copies (two packs fighting over the same files). Since the morning of
# 14 Oct 2026 the gaming PC runs this copy, under
# steamapps\workshop\content\1286220\3812461539, next to the other mods.
$SestOwnWorkshopIds = @('3812461539')
# The local folder's Mod Manager token: position 1 of data\load-order.tokens.txt.
$SestDistToken = 'SEST_Integration'
# Sea Power's Steam app id; the Workshop content folder is workshop\content\<id>.
$SeaPowerAppId = '1286220'

function Get-SteamLibraries {
    <# Every steamapps folder Steam knows about, from the registry and the
       library manifest. No hardcoded drive letters. #>
    $steamRoots = @()
    foreach ($regPath in "HKCU:\Software\Valve\Steam", "HKLM:\SOFTWARE\WOW6432Node\Valve\Steam") {
        try {
            $p = (Get-ItemProperty -Path $regPath -ErrorAction Stop).SteamPath
            if (-not $p) { $p = (Get-ItemProperty -Path $regPath -ErrorAction Stop).InstallPath }
            if ($p) { $steamRoots += $p }
        } catch { }
    }
    $steamRoots += "${env:ProgramFiles(x86)}\Steam", "$env:ProgramFiles\Steam"
    $libs = @()
    foreach ($root in $steamRoots | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique) {
        $libs += Join-Path $root "steamapps"
        $vdf = Join-Path $root "steamapps\libraryfolders.vdf"
        if (Test-Path $vdf) {
            foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) {
                $libs += Join-Path ($m.Groups[1].Value -replace '\\\\', '\') "steamapps"
            }
        }
    }
    return $libs | Where-Object { Test-Path $_ } | Select-Object -Unique
}

function Get-ModDisplayName {
    <# A mod's in-game display name: the Name= line of its _info.ini.

       Read as UTF-8 explicitly. Windows PowerShell 5.1 defaults Get-Content to
       the ANSI codepage for files without a BOM, which double-encoded every
       non-ASCII name written into mods-source\_export-manifest.csv - the
       Iskander mod's name landed as "ä¼Šæ–¯åŽå¾·å°”" instead of 伊斯坎德尔.

       Prefers _info.ini, which is the file the Mod Manager itself reads, and
       only falls back to other root-level text files for mods that ship none. #>
    param([Parameter(Mandatory)][string]$ModDir)

    # A typed list rather than `$array +=`: a pipeline that matches nothing is
    # common (plenty of mods ship only _info.ini) and can append a $null, and a
    # $null -LiteralPath is a binding error that -ErrorAction cannot suppress.
    $probes = [System.Collections.Generic.List[string]]::new()
    $info = Join-Path $ModDir "_info.ini"
    if (Test-Path -LiteralPath $info) { $probes.Add($info) }
    Get-ChildItem -LiteralPath $ModDir -File -Depth 1 -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in ".ini", ".txt" -and $_.FullName -ne $info } |
        Select-Object -First 5 |
        ForEach-Object { $probes.Add($_.FullName) }

    foreach ($probe in $probes) {
        $raw = Get-Content -LiteralPath $probe -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if (-not $raw) { continue }
        $m = [regex]::Match($raw, '(?im)^\s*(?:Name|Title|ModName)\s*=\s*(.+)$')
        if ($m.Success) { return $m.Groups[1].Value.Trim() }
    }
    return ""
}

function Find-StreamingAssets {
    <# Sea Power's StreamingAssets folder, or $null. #>
    foreach ($lib in Get-SteamLibraries) {
        foreach ($acf in Get-ChildItem -LiteralPath $lib -Filter "appmanifest_*.acf" -ErrorAction SilentlyContinue) {
            $raw = Get-Content -LiteralPath $acf.FullName -Raw
            if ($raw -match '"name"\s+"([^"]*Sea Power[^"]*)"') {
                $installDir = [regex]::Match($raw, '"installdir"\s+"([^"]+)"').Groups[1].Value
                $gameDir = Join-Path $lib "common\$installDir"
                $sa = Get-ChildItem -LiteralPath $gameDir -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue |
                    Where-Object { $_.Name -eq "StreamingAssets" } | Select-Object -First 1
                if ($sa) { return $sa.FullName }
            }
        }
    }
    return $null
}

function Test-SeaPowerRunning {
    <# The game rewrites usersettings.ini when it exits, so any edit made while
       it is running is thrown away without a word. Worth checking before we
       spend effort on one. #>
    return [bool](Get-Process -Name "Sea Power", "SeaPower" -ErrorAction SilentlyContinue)
}

function Test-Python {
    <# A candidate only counts if it runs AND reports Python 3. The Windows
       Store ships a stub python.exe that just opens the Store, so presence on
       PATH proves nothing. #>
    param([string]$Exe, [string[]]$Pre)
    try {
        $probe = @($Pre) + @("-c", "import sys; print(sys.version_info[0])")
        $out = & $Exe @probe 2>$null
        if ($LASTEXITCODE -eq 0 -and ("$out".Trim() -eq "3")) { return @{ Exe = $Exe; Pre = $Pre } }
    } catch { }
    return $null
}

function Get-Python {
    <# Returns @{ Exe = <path or 'py'>; Pre = <leading args> }, or $null. #>
    foreach ($cmd in "python", "python3") {
        $c = Get-Command $cmd -ErrorAction SilentlyContinue
        if (-not ($c -and $c.Source)) { continue }
        $found = Test-Python $c.Source @()
        if ($found) { return $found }
    }
    # The py launcher ships with the python.org installer.
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        $found = Test-Python "py" @("-3")
        if ($found) { return $found }
    }
    # Common install locations, in case PATH was never set up.
    $candidates = @()
    foreach ($root in @("$env:LOCALAPPDATA\Programs\Python", "$env:ProgramFiles\Python",
                        "${env:ProgramFiles(x86)}\Python", "C:\Python313", "C:\Python312", "C:\Python311")) {
        if (Test-Path -LiteralPath $root) {
            $candidates += Get-ChildItem -LiteralPath $root -Filter "python.exe" -Recurse -Depth 1 -ErrorAction SilentlyContinue
        }
    }
    foreach ($c in $candidates) {
        $found = Test-Python $c.FullName @()
        if ($found) { return $found }
    }
    return $null
}

function Get-ActiveMission {
    <# The mission the tooling works on when none is named, from
       data\active-mission.txt. Declared in one place so the PowerShell and
       Python tools cannot drift onto different scenarios. #>
    param([string]$RepoRoot)
    $f = Join-Path $RepoRoot "data\active-mission.txt"
    if (Test-Path -LiteralPath $f) {
        $line = Get-Content -LiteralPath $f |
            Where-Object { $_.Trim() -and -not $_.TrimStart().StartsWith("#") } |
            Select-Object -First 1
        if ($line) { return $line.Trim() }
    }
    return "NORTHERN FRONT III FINAL"
}

function Find-WorkshopContent {
    <# Sea Power's Workshop content folder, steamapps\workshop\content\1286220,
       in whichever Steam library holds it; $null when no library has one. #>
    foreach ($lib in Get-SteamLibraries) {
        $d = Join-Path $lib "workshop\content\$SeaPowerAppId"
        if (Test-Path -LiteralPath $d) { return $d }
    }
    return $null
}

function Find-SestWorkshopCopy {
    <# The folder of SEST's own Workshop item (3812461539) when Steam has it
       on disk, or $null. -WorkshopContentDir names the content folder when
       auto-detection is not wanted (tests, a second library). #>
    param([string]$WorkshopContentDir)
    if (-not $WorkshopContentDir) { $WorkshopContentDir = Find-WorkshopContent }
    if (-not $WorkshopContentDir) { return $null }
    foreach ($id in $SestOwnWorkshopIds) {
        $d = Join-Path $WorkshopContentDir $id
        if (Test-Path -LiteralPath $d) { return $d }
    }
    return $null
}

function Read-WorkshopAcf {
    <# Steam's own record of one app's Workshop items, appworkshop_<appid>.acf.

       Returns @{ Ids = <hashtable id -> $true>; Updated = <hashtable id ->
       DateTime, local time>; Size = <hashtable id -> bytes>; NeedsDownload;
       NeedsUpdate }. Updated is Steam's own "timeupdated" for the item - the
       Workshop upload time of the version installed, in Unix seconds - taken
       from the first block that carries it for each id (WorkshopItemsInstalled
       comes before WorkshopItemDetails in the file). The folder's last-write
       time, which the capture used until 14 Oct 2026, is not that: an update
       that only rewrites files inside existing subfolders does not move it,
       and so missed updates. An id with no timeupdated is in Ids only. #>
    param([Parameter(Mandatory)][string]$Path)
    $raw = Get-Content -LiteralPath $Path -Raw
    $ids = @{}; $updated = @{}; $size = @{}
    foreach ($m in [regex]::Matches($raw, '(?s)"(\d{9,10})"\s*\{([^{}]*)\}')) {
        $id = $m.Groups[1].Value
        $ids[$id] = $true
        $t = [regex]::Match($m.Groups[2].Value, '"timeupdated"\s*"(\d+)"')
        if ($t.Success -and -not $updated.ContainsKey($id)) {
            $updated[$id] = [DateTimeOffset]::FromUnixTimeSeconds([long]$t.Groups[1].Value).ToLocalTime().DateTime
        }
        $s = [regex]::Match($m.Groups[2].Value, '"size"\s*"(\d+)"')
        if ($s.Success -and -not $size.ContainsKey($id)) { $size[$id] = [long]$s.Groups[1].Value }
    }
    $md = [regex]::Match($raw, '"NeedsDownload"\s*"(\d+)"')
    $mu = [regex]::Match($raw, '"NeedsUpdate"\s*"(\d+)"')
    return @{
        Ids = $ids; Updated = $updated; Size = $size
        NeedsDownload = $(if ($md.Success) { $md.Groups[1].Value } else { $null })
        NeedsUpdate   = $(if ($mu.Success) { $mu.Groups[1].Value } else { $null })
    }
}

function Get-LogExcerpt {
    <# A log file's lines for the snapshot: the whole file while it is within
       -CapBytes, otherwise its first -HeadLines and last -TailLines with one
       marker line between them saying how many lines were left out. Returns
       @{ Lines = <string[]>; Total = <line count>; Whole = <bool> }. #>
    param([Parameter(Mandatory)][string]$Path,
          [long]$CapBytes = 50MB, [int]$HeadLines = 20000, [int]$TailLines = 20000)
    $all = @(Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue)
    $length = (Get-Item -LiteralPath $Path).Length
    if ($length -le $CapBytes -or $all.Count -le $HeadLines + $TailLines) {
        return @{ Lines = $all; Total = $all.Count; Whole = $true }
    }
    $left = $all.Count - $HeadLines - $TailLines
    $lines = @($all[0..($HeadLines - 1)]) +
             @("# ... $left line(s) left out here: the file is {0:N1} MB, over the {1:N0} MB cap; first $HeadLines and last $TailLines lines kept ..." -f ($length / 1MB), ($CapBytes / 1MB)) +
             @($all[-$TailLines..-1])
    return @{ Lines = $lines; Total = $all.Count; Whole = $false }
}

# --- Mods marked compatible (tools\mark-mods-compatible.ps1) -----------------
# The Mod Manager warns at start-up about every mod whose _info.ini declares an
# ApproximateVersion whose MAJOR.MINOR differs from the game's. On the gaming
# PC, mark-mods-compatible.ps1 rewrites that one line in each such mod's
# Workshop folder and keeps the author's file here. The exporter reads the
# author's copy back from here, so mods-source stays a faithful mirror.
$SestCompatMarker = '; SEST marked this mod compatible'

function Get-CompatBackupDir {
    <# Where mark-mods-compatible.ps1 keeps the authors' own _info.ini files. #>
    $base = $env:LOCALAPPDATA
    if (-not $base) { $base = [Environment]::GetFolderPath('LocalApplicationData') }
    if (-not $base) { $base = [IO.Path]::GetTempPath() }
    return (Join-Path (Join-Path $base "SEST") "compat-originals")
}

function Get-AuthorModFileBytes {
    <# A Workshop file's bytes as its author shipped them: for a mod's own
       _info.ini that mark-mods-compatible.ps1 has rewritten, the kept
       original; for every other file, the file itself. -BackupDir overrides
       the default store (tests). #>
    param([Parameter(Mandatory)][string]$ModId, [Parameter(Mandatory)][string]$Path,
          [Parameter(Mandatory)][string]$Rel, [string]$BackupDir)
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($Rel -ine '_info.ini') { return ,$bytes }
    if (-not $BackupDir) { $BackupDir = Get-CompatBackupDir }
    $kept = Join-Path $BackupDir "$ModId._info.ini"
    if (-not (Test-Path -LiteralPath $kept)) { return ,$bytes }
    $text = (New-Object Text.UTF8Encoding($false)).GetString($bytes)
    if ($text.IndexOf($SestCompatMarker, [StringComparison]::Ordinal) -lt 0) { return ,$bytes }
    return ,([IO.File]::ReadAllBytes($kept))
}
