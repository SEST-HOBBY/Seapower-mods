param(
    [Parameter(Mandatory=$true)][string]$GameRoot,
    [string]$OutDir = "",
    [string]$CompilerPath = ""
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Build only. Never install/change a game DLL, bypass a hash guard or publish
# to Workshop. This accepts the inspected PUBLIC BETA Build 261026 only.
$source = Join-Path $PSScriptRoot "AnchorChainBetaBootstrap.cs"
if (!(Test-Path -LiteralPath $source)) { throw "Missing source: $source" }
if (!$OutDir) { $OutDir = Join-Path $PSScriptRoot "out" }

$managed = Join-Path $GameRoot "Sea Power_Data\Managed"
$bep = Join-Path $GameRoot "BepInEx\core\BepInEx.dll"
$unity = Join-Path $managed "UnityEngine.CoreModule.dll"
$unityApi = Join-Path $managed "UnityEngine.dll"
$game = Join-Path $managed "Seapower-Scripts.dll"
foreach ($p in @($bep, $unity, $unityApi, $game)) {
    if (!(Test-Path -LiteralPath $p -PathType Leaf)) { throw "Missing dependency: $p" }
}
$expected = "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62"
$hash = (Get-FileHash -LiteralPath $game -Algorithm SHA256).Hash.ToLowerInvariant()
if ($hash -ne $expected) { throw "Not the inspected public beta Build 261026 ($hash). No output." }

# Windows PowerShell can use its installed .NET Framework csc.exe. No Mono
# installation is required when csc.exe is present.
$compilerKind = $null
$compilerExe = $null
if ($CompilerPath) {
    if (!(Test-Path -LiteralPath $CompilerPath -PathType Leaf)) {
        throw "Specified compiler does not exist: $CompilerPath"
    }
    $compilerExe = (Resolve-Path -LiteralPath $CompilerPath).ProviderPath
    $compilerKind = if ((Split-Path -Leaf $compilerExe) -ieq "mcs.exe") { "mcs" } else { "csc" }
}
else {
    $mcs = Get-Command "mcs" -ErrorAction SilentlyContinue
    if ($mcs) {
        $compilerExe = $mcs.Source
        $compilerKind = "mcs"
    }
    else {
        $candidates = @(
            (Join-Path $env:WINDIR "Microsoft.NET\Framework64\v4.0.30319\csc.exe")
            (Join-Path $env:WINDIR "Microsoft.NET\Framework\v4.0.30319\csc.exe")
        )
        foreach ($candidate in $candidates) {
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                $compilerExe = $candidate
                $compilerKind = "csc"
                break
            }
        }
        if (!$compilerExe) {
            $csc = Get-Command "csc.exe" -ErrorAction SilentlyContinue
            if ($csc) {
                $compilerExe = $csc.Source
                $compilerKind = "csc"
            }
        }
    }
}
if (!$compilerExe) {
    throw "No usable C# compiler. Checked mcs, Windows .NET Framework csc.exe and PATH. Install a C# compiler, then rerun. No DLL was produced."
}

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$dest = Join-Path $OutDir "SEST.BetaAnchorBootstrap.dll"
# Build in a temporary folder so a failed compile cannot overwrite a known DLL.
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("sest-beta-compile-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
$candidate = Join-Path $tmp "SEST.BetaAnchorBootstrap.dll"

try {
    $compilerArgs = @(
        "-nologo", "-target:library", "-optimize+",
        "-out:$candidate", "-r:$bep", "-r:$unity", "-r:$unityApi", "-r:System.Core.dll"
    )
    $standard = Join-Path $managed "netstandard.dll"
    if (Test-Path -LiteralPath $standard -PathType Leaf) {
        $compilerArgs += "-r:$standard"
    }
    $compilerArgs += $source

    Write-Host "Compiler: $compilerExe ($compilerKind)"
    & $compilerExe @compilerArgs
    $result = $LASTEXITCODE
    if ($result -ne 0 -or !(Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "Bootstrap compilation failed (exit $result). No existing output was overwritten."
    }
    Copy-Item -LiteralPath $candidate -Destination $dest -Force
}
finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

$receipt = [ordered]@{
    format = 1
    game_sha256 = $hash
    source_sha256 = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    dll_sha256 = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    binary = "SEST.BetaAnchorBootstrap.dll"
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    compiler = $compilerExe
}
$receiptPath = Join-Path $OutDir "build-receipt.json"
$receipt | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
Write-Host "Receipt: $receiptPath"

Write-Host "BETA BRIDGE COMPILED: $dest" -ForegroundColor Green
Write-Host "SHA256: $((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash)"
Write-Host "Candidate only: no installed game files changed. Runtime/UI beta compatibility still unverified."
