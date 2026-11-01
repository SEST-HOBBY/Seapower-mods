<#
.SYNOPSIS
  Regress the real capture-context.ps1 on Windows PowerShell StrictMode with
  empty, one-item, and mixed/mod-disabled LoadOrder data. No Steam required.
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
        $result = Get-Content -LiteralPath (Join-Path $dataDir "install-snapshot\load-order.live.txt") -Raw
        $snapDir = Join-Path $dataDir "install-snapshot"
        $dllReport = Get-Content -LiteralPath (Join-Path $snapDir "plugin-dlls.txt") -Raw
        if (-not $dllReport.Contains("[game]  1 DLL(s)")) { throw "Expected one loose DLL for $($case.Label)" }
        $problemReport = Get-Content -LiteralPath (Join-Path $snapDir "player.problems.txt") -Raw
        if (-not $problemReport.Contains("# 1 hit(s)")) { throw "Expected single error log match for $($case.Label)" }
        foreach ($expected in $case.Match) {
            if (-not $result.Contains($expected)) {
                throw "Expected '$expected' missing in $($case.Label)"
            }
        }
        Write-Host "PASS: $($case.Label)"
    }
    Write-Host "CAPTURE-CONTEXT STRICTMODE REGRESSION: PASS"
}
finally {
    Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue
}
