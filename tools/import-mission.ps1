<#
.SYNOPSIS
    Copy a mission you edited in the game back into this repo.

.DESCRIPTION
    The Sea Power mission editor saves into the game's own
    user\missions\user_missions folder, so a mission you just edited lives
    outside the repo. This finds the game the same way the other tools do,
    copies the named mission (or every user mission) into
    integration\missions\, and normalises CRLF to LF so the diff stays clean.

    Your edited file becomes the authoritative copy. Re-run the mission
    tooling afterwards (civilian dressing, depth pass, land check) - all of
    it is idempotent and preserves every placement you made.

.EXAMPLE
    # From the repo root, with the game closed:
    powershell -ExecutionPolicy Bypass -File .\tools\import-mission.ps1 -Mission "NORTHERN FRONT III"
    git add integration\missions ; git commit -m "Import edited NORTHERN FRONT III" ; git push

.EXAMPLE
    # Bring in everything you have edited:
    powershell -ExecutionPolicy Bypass -File .\tools\import-mission.ps1 -All
#>
[CmdletBinding()]
param(
    [string]$Mission,
    [switch]$All,
    [string]$StreamingAssetsDir
)

$ErrorActionPreference = "Stop"

if (-not $Mission -and -not $All) {
    throw "Give -Mission '<name>' (without .ini) or -All"
}

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
$destDir = Join-Path $repoRoot "integration\missions"

function Get-SteamLibraries {
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

# --- Locate StreamingAssets --------------------------------------------------
if (-not $StreamingAssetsDir) {
    foreach ($lib in Get-SteamLibraries) {
        foreach ($acf in Get-ChildItem -LiteralPath $lib -Filter "appmanifest_*.acf" -ErrorAction SilentlyContinue) {
            $raw = Get-Content -LiteralPath $acf.FullName -Raw
            if ($raw -match '"name"\s+"([^"]*Sea Power[^"]*)"') {
                $installDir = [regex]::Match($raw, '"installdir"\s+"([^"]+)"').Groups[1].Value
                $gameDir = Join-Path $lib "common\$installDir"
                $sa = Get-ChildItem -LiteralPath $gameDir -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue |
                    Where-Object { $_.Name -eq "StreamingAssets" } | Select-Object -First 1
                if ($sa) { $StreamingAssetsDir = $sa.FullName }
                break
            }
        }
        if ($StreamingAssetsDir) { break }
    }
    if (-not $StreamingAssetsDir) {
        throw "Could not auto-detect Sea Power's StreamingAssets. Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'"
    }
}

$srcDir = Join-Path $StreamingAssetsDir "user\missions\user_missions"
if (-not (Test-Path $srcDir)) { throw "user missions folder not found: $srcDir" }
Write-Host "Importing from: $srcDir`n"

$files = if ($All) {
    Get-ChildItem -LiteralPath $srcDir -Filter "*.ini" | Where-Object { $_.Name -ne "_info.ini" }
} else {
    $one = Join-Path $srcDir "$Mission.ini"
    if (-not (Test-Path -LiteralPath $one)) {
        throw "mission not found: $one`nAvailable: " + ((Get-ChildItem -LiteralPath $srcDir -Filter '*.ini' | ForEach-Object { $_.BaseName }) -join ', ')
    }
    Get-Item -LiteralPath $one
}

$imported = 0
foreach ($f in $files) {
    $dest = Join-Path $destDir $f.Name
    $text = Get-Content -LiteralPath $f.FullName -Raw
    $lf = $text -replace "`r`n", "`n"
    if ((Test-Path -LiteralPath $dest) -and ((Get-Content -LiteralPath $dest -Raw) -eq $lf)) {
        Write-Host ("  unchanged  {0}" -f $f.Name)
        continue
    }
    # Write LF-only so the repo diff shows real edits, not line endings.
    [System.IO.File]::WriteAllText($dest, $lf)
    Write-Host ("  imported   {0}  ({1:N0} bytes, saved {2})" -f $f.Name, $f.Length, $f.LastWriteTime)
    $imported++
}

Write-Host "`n$imported mission(s) imported into integration\missions."
Write-Host "Next:"
Write-Host "  git add integration\missions"
Write-Host "  git commit -m `"Import edited mission`""
Write-Host "  git push"
Write-Host "Then the mission tooling can be re-run over your edits (it is idempotent)."
