<#
.SYNOPSIS
  Runs the real capture-context.ps1 under StrictMode against a disposable
  fixture: empty, one-item and mixed LoadOrder sections, one loose DLL,
  one-line Player and BepInEx logs, and a clean session that must replace
  the previous session's problems summary. No Steam or game is needed and
  nothing outside the temporary fixture is written.

      pwsh -File tools/tests/test_capture_context.ps1
  (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$srcRepo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$fixture = Join-Path ([IO.Path]::GetTempPath()) ("SEST-capture-regression-" + [guid]::NewGuid().ToString("N"))
$toolDir = Join-Path $fixture "tools"
$libDir = Join-Path $toolDir "lib"
$dataDir = Join-Path $fixture "data"
$game = Join-Path $fixture "game\Sea Power_Data\StreamingAssets"
$settings = Join-Path $fixture "test-usersettings.ini"

try {
    foreach ($folder in @($libDir, $dataDir, (Join-Path $game "original"))) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
    Copy-Item -LiteralPath (Join-Path $srcRepo "tools\capture-context.ps1") -Destination $toolDir
    Copy-Item -LiteralPath (Join-Path $srcRepo "tools\lib\common.ps1") -Destination $libDir
    # A stub for media discovery, unrelated to the load-order Count regression.
    @'
param([string]$DataDir, [string]$OutFile)
"test-only" | Set-Content -LiteralPath $OutFile -Encoding UTF8
'@ | Set-Content -LiteralPath (Join-Path $toolDir "scan-ui-assets.ps1") -Encoding UTF8

    # Exercise a singleton DLL and one-line Player/BepInEx logs as well as
    # empty mods. Those were separately broken by pipeline unrolling.
    $gameRoot = Split-Path -Parent (Split-Path -Parent $game)
    $bepRoot = Join-Path $gameRoot "BepInEx"
    New-Item -ItemType Directory -Path $bepRoot -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $gameRoot "test-only.dll"), "fixture")
    [IO.File]::WriteAllText((Join-Path $fixture "Player.log"), "Error: synthetic test")
    [IO.File]::WriteAllText((Join-Path $fixture "Player-prev.log"), "synthetic prior session")
    [IO.File]::WriteAllText((Join-Path $bepRoot "LogOutput.log"), "[Info] synthetic BepInEx")
    # A summary left by an earlier session. Player-prev.log has no matching
    # line, so the capture must still replace this with "0 hit(s)".
    $snapDir = Join-Path $dataDir "install-snapshot"
    New-Item -ItemType Directory -Path $snapDir -Force | Out-Null
    $stale = "# STALE summary from an earlier session"
    [IO.File]::WriteAllText((Join-Path $snapDir "player-prev.problems.txt"), $stale)

    $cases = @(
        @{ Label = "absent-section"; Tokens = @("SEST_Integration"); Live = @(); Match = @() },
        @{ Label = "one-enabled"; Tokens = @("SEST_Integration"); Live = @("SEST_Integration,True"); Match = @(
            "canonical but not live (0)", "live but not canonical (0)", "disabled in game (0)"
        ) },
        @{ Label = "one-missing"; Tokens = @("SEST_Integration", "3819427362"); Live = @("SEST_Integration,True"); Match = @(
            "canonical but not live (1)", "live but not canonical (0)", "disabled in game (0)"
        ) },
        @{ Label = "one-extra-and-disabled"; Tokens = @("SEST_Integration"); Live = @("SEST_Integration,True", "3826396311,False"); Match = @(
            "canonical but not live (0)", "live but not canonical (1)", "disabled in game (1)"
        ) }
    )

    foreach ($case in $cases) {
        $canonical = Join-Path $dataDir "load-order.tokens.txt"
        [IO.File]::WriteAllLines($canonical, [string[]]$case.Tokens)
        $ini = [System.Collections.Generic.List[string]]::new()
        if ($case.Label -eq "absent-section") {
            $ini.Add("[Other]")
            $ini.Add("Enabled=True")
        } else {
            $ini.Add("[LoadOrder]")
            $ini.Add("NumberOfModFiles=$($case.Live.Count)")
            $i = 0
            foreach ($token in $case.Live) {
                $i++
                $ini.Add(("Mod{0}Directory={1}" -f $i, $token))
            }
            $ini.Add("")
            $ini.Add("[Other]")
            $ini.Add("Enabled=True")
        }
        [IO.File]::WriteAllLines($settings, $ini.ToArray())
        $report = Join-Path $fixture ("run-" + $case.Label + ".txt")
        try {
            & (Join-Path $toolDir "capture-context.ps1") -SettingsPath $settings -StreamingAssetsDir $game -Redact *> $report
        }
        catch {
            Get-Content -LiteralPath $report -ErrorAction SilentlyContinue | Select-Object -Last 20 | Write-Host
            Write-Host ("Failed case: " + $case.Label)
            Write-Host $_.InvocationInfo.PositionMessage
            Write-Host $_.ScriptStackTrace
            throw
        }
        $result = Get-Content -LiteralPath (Join-Path $snapDir "load-order.live.txt") -Raw
        $dllReport = Get-Content -LiteralPath (Join-Path $snapDir "plugin-dlls.txt") -Raw
        if (-not $dllReport.Contains("[game]  1 DLL(s)")) { throw "Expected one loose DLL for $($case.Label)" }
        $problemReport = Get-Content -LiteralPath (Join-Path $snapDir "player.problems.txt") -Raw
        if (-not $problemReport.Contains("# 1 hit(s)")) { throw "Expected single error log match for $($case.Label)" }
        $prevReport = Get-Content -LiteralPath (Join-Path $snapDir "player-prev.problems.txt") -Raw
        if ($prevReport.Contains("STALE") -or -not $prevReport.Contains("# 0 hit(s)")) {
            throw "A clean Player-prev.log left the earlier summary in place for $($case.Label)"
        }
        foreach ($expected in $case.Match) {
            if (-not $result.Contains($expected)) {
                throw "Expected '$expected' missing in $($case.Label)"
            }
        }
        Write-Host "PASS: $($case.Label)"
    }

    # A clean session after a session with errors: player.problems.txt held
    # one hit from the runs above and must now say 0 hit(s). With no
    # Player-prev.log at all, its summary says so instead of staying stale.
    [IO.File]::WriteAllText((Join-Path $fixture "Player.log"), "synthetic clean session")
    Remove-Item -LiteralPath (Join-Path $fixture "Player-prev.log")
    [IO.File]::WriteAllText((Join-Path $snapDir "player-prev.problems.txt"), $stale)
    $report = Join-Path $fixture "run-clean-session.txt"
    & (Join-Path $toolDir "capture-context.ps1") -SettingsPath $settings -StreamingAssetsDir $game -Redact *> $report
    $current = Get-Content -LiteralPath (Join-Path $snapDir "player.problems.txt") -Raw
    if ($current.Contains("synthetic test") -or -not $current.Contains("# 0 hit(s)")) {
        throw "A clean Player.log left the previous session's problems summary in place"
    }
    $prev = Get-Content -LiteralPath (Join-Path $snapDir "player-prev.problems.txt") -Raw
    if ($prev.Contains("STALE") -or -not $prev.Contains("was not present")) {
        throw "A missing Player-prev.log left the earlier problems summary in place"
    }
    Write-Host "PASS: clean-session"
    Write-Host "all checks passed (capture-context.ps1 under StrictMode)"
    # The isolated fixture is intentionally not a Git repository. Its
    # environment probe can leave LASTEXITCODE=128 even when every check passes.
    # Clear the native-command status so Windows Actions reports the test result.
    $global:LASTEXITCODE = 0
}
finally {
    Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue
}
