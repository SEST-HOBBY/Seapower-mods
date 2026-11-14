<#
.SYNOPSIS
    The capture block the owner pastes (docs\packaging-and-recovery.md, the
    block under the "capture-block" marker), run as it stands against a
    disposable origin and clone: it cuts the capture branch from the base
    branch, runs the capture scripts, commits and pushes the capture, adds
    the game export as a second commit when the export script says it
    exported, and puts the clone back on the branch it was on. It refuses a
    clone with changes of its own, and commits nothing when the capture fails.

.DESCRIPTION
    The fixture's base branch carries stand-ins for the three scripts it runs,
    so no Steam, game or Workshop folder is needed. Three lines of the block
    are rewritten for the fixture and nothing else: the clone's path, the
    base branch's name, and, away from Windows, the name of the PowerShell
    executable and the path separators git and it are given. Nothing outside
    the temporary fixture is read or written.

        pwsh -File tools/tests/test_capture_block.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$src = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$root = Join-Path ([IO.Path]::GetTempPath()) ("SEST-capture-block-" + [guid]::NewGuid().ToString("N"))
$origin = Join-Path $root "origin.git"
$seed = Join-Path $root "seed"
$clone = Join-Path $root "clone"
$marker = Join-Path $root "reference-capture-ran.txt"
$windows = [IO.Path]::DirectorySeparatorChar -eq '\'
$shell = (Get-Process -Id $PID).Path
$failed = 0
function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}
function Invoke-Git([string]$Dir, [string[]]$GitArgs) {
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { $out = @(& git -C $Dir -c user.name=test -c user.email=test@example.invalid -c core.autocrlf=false @GitArgs 2>&1 | ForEach-Object { [string]$_ }) }
    finally { $ErrorActionPreference = $saved }
    return $out
}

# --- the block, from the document --------------------------------------------
$doc = [IO.File]::ReadAllText((Join-Path $src "docs\packaging-and-recovery.md")).Replace("`r`n", "`n")
$m = [regex]::Match($doc, '(?s)<!-- capture-block -->\n```powershell\n(.*?)\n```')
if (-not $m.Success) { Write-Host "  FAILED the document has no block under the capture-block marker"; exit 1 }
$block = $m.Groups[1].Value
Check ($block -notmatch '(?m)^\s*$') "the block has no blank line (a pasted blank line would run it early)"
Check ($block -match "Set-Location -LiteralPath 'C:\\Users\\rolyl\\Seapower-mods'") "the block goes to the owner's clone"
Check ($block -match '(?m)^\s*\$base = ''[^'']+''') "the block names its base branch on a line of its own"
Check ($block -notmatch 'IncludeVanilla') "the block never exports the game's own files"
Check ($block -notmatch '(?i)\bforce\b|--hard|clean -') "the block forces, resets and cleans nothing"

function Get-FixtureBlock([string]$CloneDir) {
    $text = $block.Replace("'C:\Users\rolyl\Seapower-mods'", "'" + $CloneDir.Replace("'", "''") + "'")
    $text = [regex]::Replace($text, '(?m)^(\s*\$base = )''[^'']+''', '$1''base-test''')
    if (-not $windows) {
        # git and a -File argument are given the paths as typed; only Windows reads '\' as a separator.
        $text = $text.Replace('.\tools\', './tools/').Replace('data\install-snapshot', 'data/install-snapshot').Replace('data\mod-fingerprints.json', 'data/mod-fingerprints.json')
    }
    # The same PowerShell that runs this test stands in for "powershell".
    return [regex]::Replace($text, '(?m)^(\s*)powershell -ExecutionPolicy Bypass -File ', ('$1& ''' + $shell.Replace("'", "''") + ''' -NoProfile -ExecutionPolicy Bypass -File '))
}
function Invoke-Block([string]$CloneDir, [string]$Log) {
    $script = Join-Path $root ("block-" + [guid]::NewGuid().ToString("N") + ".ps1")
    [IO.File]::WriteAllText($script, (Get-FixtureBlock $CloneDir))
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $shell -NoProfile -ExecutionPolicy Bypass -File $script *> $Log; $code = $LASTEXITCODE }
    finally { $ErrorActionPreference = $saved }
    return $code
}

$savedMarker = $env:SEST_TEST_REFERENCE_MARKER
$savedFail = $env:SEST_TEST_CAPTURE_FAILS
$savedExport = $env:SEST_TEST_GAME_EXPORT
try {
    New-Item -ItemType Directory -Path $root -Force | Out-Null
    $null = Invoke-Git $root @("init", "-q", "--bare", "-b", "main", $origin)
    New-Item -ItemType Directory -Path (Join-Path $seed "tools"), (Join-Path $seed "data\install-snapshot"), (Join-Path $seed "mods-source\3812454152") -Force | Out-Null
    $null = Invoke-Git $seed @("init", "-q", "-b", "main")
    [IO.File]::WriteAllText((Join-Path $seed "README.txt"), "fixture`n")
    $null = Invoke-Git $seed @("add", "-A")
    $null = Invoke-Git $seed @("commit", "-q", "-m", "root")
    # The branch the PC lives on: no capture scripts, as on the owner's PC in November 2026.
    $null = Invoke-Git $seed @("branch", "pc-own")
    # The base branch: an export, and stand-ins for the two capture scripts.
    $null = Invoke-Git $seed @("checkout", "-q", "-b", "base-test")
    [IO.File]::WriteAllText((Join-Path $seed "mods-source\3812454152\_info.ini"), "Name=Old`n")
    [IO.File]::WriteAllText((Join-Path $seed "data\install-snapshot\environment.txt"), "captured        : before`n")
    [IO.File]::WriteAllText((Join-Path $seed "data\mod-fingerprints.json"), "{}`n")
    [IO.File]::WriteAllText((Join-Path $seed "tools\capture-all-mod-updates.ps1"), @'
if ($env:SEST_TEST_CAPTURE_FAILS) { Write-Host "stand-in capture: refusing"; exit 1 }
$repo = Split-Path -Parent $PSScriptRoot
[IO.File]::WriteAllText((Join-Path $repo "mods-source/3812454152/_info.ini"), "Name=Updated`n")
[IO.File]::WriteAllText((Join-Path $repo "data/install-snapshot/environment.txt"), "captured        : now`n")
[IO.File]::WriteAllText((Join-Path $repo "data/mod-fingerprints.json"), "{`"mods`":{}}`n")
Write-Host "stand-in capture: done"
exit 0
'@)
    [IO.File]::WriteAllText((Join-Path $seed "tools\export-game.ps1"), @'
if ($env:SEST_TEST_GAME_EXPORT -ne "release") { Write-Host "stand-in game export: nothing to do"; exit 3 }
$repo = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Path (Join-Path $repo "mods-source/_vanilla") -Force | Out-Null
[IO.File]::WriteAllText((Join-Path $repo "mods-source/_vanilla/changelog.txt"), "13-Nov-2026: 0.9.2 Build 261113 Public Release`n")
Write-Host "stand-in game export: exported"
exit 0
'@)
    [IO.File]::WriteAllText((Join-Path $seed "tools\capture-beta-references.ps1"), @'
[IO.File]::WriteAllText($env:SEST_TEST_REFERENCE_MARKER, "ran on " + (& git branch --show-current))
exit 0
'@)
    $null = Invoke-Git $seed @("add", "-A")
    $null = Invoke-Git $seed @("commit", "-q", "-m", "base: export and capture scripts")
    $baseHead = "$(Invoke-Git $seed @('rev-parse', 'HEAD'))".Trim()
    $null = Invoke-Git $seed @("remote", "add", "origin", $origin)
    $null = Invoke-Git $seed @("push", "-q", "origin", "main", "pc-own", "base-test")

    $null = Invoke-Git $root @("clone", "-q", "--branch", "pc-own", $origin, $clone)
    foreach ($pair in @(@("user.name", "test"), @("user.email", "test@example.invalid"), @("core.autocrlf", "false"))) {
        $null = Invoke-Git $clone @("config", $pair[0], $pair[1])
    }
    $env:SEST_TEST_REFERENCE_MARKER = $marker
    $env:SEST_TEST_CAPTURE_FAILS = $null
    $env:SEST_TEST_GAME_EXPORT = $null

    # --- a clone with changes of its own: refused, nothing made ----------------
    [IO.File]::WriteAllText((Join-Path $clone "README.txt"), "edited`n")
    $code = Invoke-Block $clone (Join-Path $root "run-dirty.txt")
    $log = Get-Content -LiteralPath (Join-Path $root "run-dirty.txt") -Raw
    Check ($code -ne 0 -and $log -match "uncommitted changes \(1;") "refuses a clone with uncommitted changes, and counts them"
    Check ($log -match "(?m)^\s*M\s+README\.txt") "and lists them, so the refusal can be reported as it stands"
    Check (@(Invoke-Git $origin @("branch", "--list", "chore/*")).Count -eq 0) "and pushes nothing"
    Check ("$(Invoke-Git $clone @('branch', '--show-current'))".Trim() -eq "pc-own") "and leaves the clone on its branch"
    $null = Invoke-Git $clone @("checkout", "-q", "--", "README.txt")

    # --- the capture fails: nothing committed, and the block says where it stopped
    $env:SEST_TEST_CAPTURE_FAILS = "1"
    $code = Invoke-Block $clone (Join-Path $root "run-failed.txt")
    $log = Get-Content -LiteralPath (Join-Path $root "run-failed.txt") -Raw
    Check ($code -ne 0 -and $log -match "capture refused or failed") "a capture that fails stops the block"
    Check (@(Invoke-Git $origin @("branch", "--list", "chore/*")).Count -eq 0) "and nothing is pushed"
    $stopped = "$(Invoke-Git $clone @('branch', '--show-current'))".Trim()
    Check ($stopped -like "chore/workshop-refresh-*" -and $log.Contains($stopped)) "the clone is on the capture branch the message names ($stopped)"
    Check ("$(Invoke-Git $clone @('rev-parse', 'HEAD'))".Trim() -eq $baseHead) "with no commit on it"
    Check (-not (Test-Path -LiteralPath $marker)) "and the reference capture has not run"
    $env:SEST_TEST_CAPTURE_FAILS = $null
    $null = Invoke-Git $clone @("checkout", "-q", "pc-own")
    $null = Invoke-Git $clone @("branch", "-D", $stopped)

    # --- the capture ------------------------------------------------------------
    $code = Invoke-Block $clone (Join-Path $root "run.txt")
    $log = Get-Content -LiteralPath (Join-Path $root "run.txt") -Raw
    Check ($code -eq 0) "the block runs to its end (exit $code)"
    if ($code -ne 0) { Write-Host $log }
    $pushed = @(Invoke-Git $origin @("for-each-ref", "--format=%(refname:short)", "refs/heads/chore") | Where-Object { $_ })
    Check ($pushed.Count -eq 1 -and $pushed[0] -match '^chore/workshop-refresh-\d{8}-\d{4}$') "one capture branch is pushed, named for the day and the minute ($($pushed -join ', '))"
    if ($pushed.Count -eq 1) {
        $b = $pushed[0]
        Check ($log.Contains("Captured and pushed: $b")) "the block ends by naming it"
        Check ("$(Invoke-Git $origin @('rev-parse', "$b~1"))".Trim() -eq $baseHead) "the capture is one commit on the base branch"
        $names = @(Invoke-Git $origin @("show", "--name-only", "--format=", $b) | Where-Object { $_ } | Sort-Object)
        Check (($names -join "|") -eq "data/install-snapshot/environment.txt|data/mod-fingerprints.json|mods-source/3812454152/_info.ini") "it holds the captured paths and nothing else ($($names -join ', '))"
        Check ("$(Invoke-Git $origin @('show', "${b}:mods-source/3812454152/_info.ini"))".Trim() -eq "Name=Updated") "with the updated mod's file"
        Check ((Test-Path -LiteralPath $marker) -and ((Get-Content -LiteralPath $marker -Raw) -eq "ran on $b")) "the reference capture ran after it, from the capture branch"
    }
    Check ("$(Invoke-Git $clone @('branch', '--show-current'))".Trim() -eq "pc-own") "the clone is back on the branch it was on"
    Check (@(Invoke-Git $clone @("status", "--porcelain")).Count -eq 0) "and has no changes left in it"
    # --- the same with a newer public release installed: the game export follows --
    Remove-Item -LiteralPath $marker
    $env:SEST_TEST_GAME_EXPORT = "release"
    # A capture branch is named for the minute: wait for the next one, so the
    # second run cannot reuse the first run's branch name.
    while ((Get-Date -Format 'yyyyMMdd-HHmm') -eq ($pushed[0] -replace '^chore/workshop-refresh-', '')) { Start-Sleep -Seconds 2 }
    $code = Invoke-Block $clone (Join-Path $root "run-export.txt")
    $log = Get-Content -LiteralPath (Join-Path $root "run-export.txt") -Raw
    Check ($code -eq 0) "with a newer release installed the block runs to its end (exit $code)"
    if ($code -ne 0) { Write-Host $log }
    $second = @(Invoke-Git $origin @("for-each-ref", "--format=%(refname:short)", "refs/heads/chore") | Where-Object { $_ -and $_ -ne $pushed[0] })
    Check ($second.Count -eq 1) "a second capture branch is pushed ($($second -join ', '))"
    if ($second.Count -eq 1) {
        $b2 = $second[0]
        Check ("$(Invoke-Git $origin @('rev-parse', "$b2~2"))".Trim() -eq $baseHead) "it is two commits on the base branch: the capture, then the game export"
        Check ("$(Invoke-Git $origin @('log', '-1', '--format=%s', $b2))".Trim() -eq "Game export after the Sea Power update") "the second commit is the game export"
        $names = @(Invoke-Git $origin @("show", "--name-only", "--format=", $b2) | Where-Object { $_ })
        Check (($names -join "|") -eq "mods-source/_vanilla/changelog.txt") "and holds the exported game files only ($($names -join ', '))"
        Check ((Test-Path -LiteralPath $marker) -and ((Get-Content -LiteralPath $marker -Raw) -eq "ran on $b2")) "the reference capture still ran after it"
    }
    Check ("$(Invoke-Git $clone @('branch', '--show-current'))".Trim() -eq "pc-own" -and
           @(Invoke-Git $clone @("status", "--porcelain")).Count -eq 0) "and the clone is back on its branch, clean"
    Check ("$(Invoke-Git $origin @('rev-parse', 'base-test'))".Trim() -eq $baseHead -and
           "$(Invoke-Git $origin @('rev-parse', 'pc-own'))".Trim() -eq "$(Invoke-Git $seed @('rev-parse', 'pc-own'))".Trim()) "the base branch and the PC's branch are untouched on origin"
}
finally {
    $env:SEST_TEST_REFERENCE_MARKER = $savedMarker
    $env:SEST_TEST_CAPTURE_FAILS = $savedFail
    $env:SEST_TEST_GAME_EXPORT = $savedExport
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
$global:LASTEXITCODE = 0
if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
