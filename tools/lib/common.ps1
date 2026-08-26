<#
    Shared helpers for the SEST tooling. Dot-source it:

        . (Join-Path $PSScriptRoot "lib\common.ps1")

    Everything here is detection only - nothing writes.
#>

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
