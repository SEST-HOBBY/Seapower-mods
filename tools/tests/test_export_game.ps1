<#
.SYNOPSIS
    tools\export-game.ps1 against a disposable game folder and export: it
    exports a newer public release, and refuses the same build, a beta, an
    older build and a game with no changelog, each with its own exit code
    and without writing anything.

.DESCRIPTION
    The real export-mod-configs.ps1 does the copying, from a fake game
    folder and a fake Workshop folder. No Steam or game is needed and
    nothing outside the temporary fixture is read or written.

        pwsh -File tools/tests/test_export_game.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$src = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$root = Join-Path ([IO.Path]::GetTempPath()) ("SEST-export-game-" + [guid]::NewGuid().ToString("N"))
$tools = Join-Path $root "tools"
$dest = Join-Path $root "mods-source"
$gameDir = Join-Path $root "game"
$data = Join-Path $gameDir "Sea Power_Data"
$streaming = Join-Path $data "StreamingAssets"
$workshop = Join-Path $root "steamapps\workshop\content\1286220"
$shell = (Get-Process -Id $PID).Path
$failed = 0
function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}
function Get-TreeHash([string]$Dir) {
    $sha = [Security.Cryptography.SHA256]::Create()
    $parts = @(Get-ChildItem -LiteralPath $Dir -Recurse -File | Sort-Object FullName | ForEach-Object {
        $_.FullName.Substring($Dir.Length) + "=" + [BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($_.FullName)))
    })
    return ($parts -join "|")
}
function Invoke-ExportGame([string]$Log, [string[]]$Extra = @()) {
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $scriptArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $tools "export-game.ps1"),
                        "-GameDir", $gameDir, "-WorkshopContentDir", $workshop, "-DestDir", $dest) + $Extra
        & $shell @scriptArgs *> $Log
        $code = $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $saved }
    return $code
}
$release090 = "Change log`r`n----------`r`n`r`n11-Nov-2026: 0.9.0 Build 261111 Public Release`r`n[FIX] x`r`n"
$release092 = "Change log`r`n----------`r`n`r`n13-Nov-2026: 0.9.2 Build 261113 Public Release`r`n[FIX] y`r`n`r`n11-Nov-2026: 0.9.0 Build 261111 Public Release`r`n"
$beta092 = "Change log`r`n----------`r`n`r`n13-Nov-2026: 0.9.2 Build 261113`r`n[FIX] y`r`n`r`n11-Nov-2026: 0.9.0 Build 261111 Public Release`r`n"
$release087 = "Change log`r`n`r`n21-Oct-2026: 0.8.7 Build 261021 Public Release`r`n"

try {
    foreach ($dir in @((Join-Path $tools "lib"), (Join-Path $dest "_vanilla\original"), (Join-Path $streaming "original\missions"),
                       (Join-Path $streaming "SEST_Integration"), (Join-Path $workshop "3812454152"))) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    foreach ($name in @("export-game.ps1", "export-mod-configs.ps1")) {
        Copy-Item -LiteralPath (Join-Path $src "tools\$name") -Destination $tools
    }
    Copy-Item -LiteralPath (Join-Path $src "tools\lib\common.ps1") -Destination (Join-Path $tools "lib")
    # The export as the repository holds it: 0.9.0, with one file the game still has and one it dropped.
    [IO.File]::WriteAllText((Join-Path $dest "_vanilla\changelog.txt"), $release090)
    [IO.File]::WriteAllText((Join-Path $dest "_vanilla\original\kept.ini"), "old text")
    [IO.File]::WriteAllText((Join-Path $dest "_vanilla\original\dropped.ini"), "no longer in the game")
    # The install: the kept file changed, a new mission, a picture, and an installed SEST pack.
    [IO.File]::WriteAllText((Join-Path $streaming "original\kept.ini"), "new text")
    [IO.File]::WriteAllText((Join-Path $streaming "original\missions\new.ini"), "[Mission]")
    [IO.File]::WriteAllText((Join-Path $streaming "original\picture.png"), "not text")
    [IO.File]::WriteAllText((Join-Path $streaming "SEST_Integration\_info.ini"), "Name=SEST")
    [IO.File]::WriteAllText((Join-Path $workshop "3812454152\_info.ini"), "Name=A Mod")
    $before = Get-TreeHash $dest

    # --- the same build: nothing to do ------------------------------------------
    [IO.File]::WriteAllText((Join-Path $data "changelog.txt"), $release090)
    $code = Invoke-ExportGame (Join-Path $root "run-same.txt")
    Check ($code -eq 3 -and (Get-TreeHash $dest) -eq $before) "the build the export already holds: exit 3, nothing written (exit $code)"

    # --- a beta: refused ------------------------------------------------------------
    [IO.File]::WriteAllText((Join-Path $data "changelog.txt"), $beta092)
    $code = Invoke-ExportGame (Join-Path $root "run-beta.txt")
    $log = Get-Content -LiteralPath (Join-Path $root "run-beta.txt") -Raw
    Check ($code -eq 4 -and (Get-TreeHash $dest) -eq $before -and $log -match "is a beta") "a newer beta: exit 4, said, nothing written (exit $code)"

    # --- an older release: refused ---------------------------------------------------
    [IO.File]::WriteAllText((Join-Path $data "changelog.txt"), $release087)
    $code = Invoke-ExportGame (Join-Path $root "run-older.txt")
    Check ($code -eq 6 -and (Get-TreeHash $dest) -eq $before) "an older release installed: exit 6, nothing written (exit $code)"

    # --- no changelog: a release cannot be told from a beta -------------------------
    Remove-Item -LiteralPath (Join-Path $data "changelog.txt")
    $code = Invoke-ExportGame (Join-Path $root "run-none.txt")
    Check ($code -eq 5 -and (Get-TreeHash $dest) -eq $before) "no changelog beside the install: exit 5, nothing written (exit $code)"

    # --- the changelog beside the executable instead, a newer public release ---------
    [IO.File]::WriteAllText((Join-Path $gameDir "changelog.txt"), $release092)
    $code = Invoke-ExportGame (Join-Path $root "run-release.txt")
    $log = Get-Content -LiteralPath (Join-Path $root "run-release.txt") -Raw
    Check ($code -eq 0) "a newer public release: exported (exit $code)"
    if ($code -ne 0) { Write-Host $log }
    Check ($log.Contains("Installed game: 13-Nov-2026: 0.9.2 Build 261113 Public Release") -and
           $log.Contains("Exported: 13-Nov-2026: 0.9.2 Build 261113 Public Release")) "it names the build it found and the build it exported"
    Check ((Get-Content -LiteralPath (Join-Path $dest "_vanilla\original\kept.ini") -Raw) -eq "new text") "a changed game file is the new text"
    Check (Test-Path -LiteralPath (Join-Path $dest "_vanilla\original\missions\new.ini")) "a new game file is exported"
    Check (-not (Test-Path -LiteralPath (Join-Path $dest "_vanilla\original\picture.png"))) "a picture is not"
    Check (-not (Test-Path -LiteralPath (Join-Path $dest "_vanilla\SEST_Integration"))) "an installed SEST pack is not exported as game files"
    Check (Test-Path -LiteralPath (Join-Path $dest "_vanilla\original\dropped.ini")) "a file the game dropped is left for the repository to remove"
    Check ((Get-Content -LiteralPath (Join-Path $dest "_vanilla\changelog.txt") -Raw).Contains("0.9.2 Build 261113 Public Release")) "the export's changelog is the installed one"
    Check (Test-Path -LiteralPath (Join-Path $dest "3812454152\_info.ini")) "the exporter exported the mods too"

    # --- again: now the same build ---------------------------------------------------
    $after = Get-TreeHash $dest
    $code = Invoke-ExportGame (Join-Path $root "run-again.txt")
    Check ($code -eq 3 -and (Get-TreeHash $dest) -eq $after) "run again: exit 3, nothing written (exit $code)"
    $code = Invoke-ExportGame (Join-Path $root "run-force.txt") @("-Force")
    Check ($code -eq 0) "-Force exports the same build again (exit $code)"
}
finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
$global:LASTEXITCODE = 0
if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
