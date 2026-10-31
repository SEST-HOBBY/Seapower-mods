param(
    [Parameter(Mandatory=$true)][string]$GameRoot,
    [string]$OutDir = ""
)
$ErrorActionPreference = "Stop"
# This script builds a NEW compatibility plugin only. It never installs, edits
# SEST.RuntimeFixes.dll, edits the Steam Workshop, or mutates game assemblies.
$source = Join-Path $PSScriptRoot "AnchorChainBetaBootstrap.cs"
if (!(Test-Path -LiteralPath $source)) { throw "Missing source: $source" }
if (!$OutDir) { $OutDir = Join-Path $PSScriptRoot "out" }
$managed = Join-Path $GameRoot "Sea Power_Data\Managed"
$bep = Join-Path $GameRoot "BepInEx\core\BepInEx.dll"
$unity = Join-Path $managed "UnityEngine.CoreModule.dll"
$game = Join-Path $managed "Seapower-Scripts.dll"
foreach ($p in @($bep,$unity,$game)) {
    if (!(Test-Path -LiteralPath $p)) { throw "Missing dependency: $p" }
}
$expected = "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62"
$hash = (Get-FileHash -LiteralPath $game -Algorithm SHA256).Hash.ToLowerInvariant()
if ($hash -ne $expected) { throw "Not inspected beta build 261026 ($hash). No output." }

$mcs = Get-Command "mcs" -ErrorAction SilentlyContinue
if (!$mcs) { throw "Mono mcs is required to compile. Install Mono or build with equivalent C# compiler using BepInEx.dll and UnityEngine.CoreModule.dll; no DLL was produced." }
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$dest = Join-Path $OutDir "SEST.BetaAnchorBootstrap.dll"
& $mcs.Source -nologo -target:library -optimize+ "-out:$dest" "-r:$bep" "-r:$unity" $source
if ($LASTEXITCODE -ne 0) { throw "Bootstrap compilation failed, exit $LASTEXITCODE" }
Write-Host "BETA BRIDGE COMPILED: $dest" -ForegroundColor Green
Write-Host "SHA256: $((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash)"
Write-Host "This is an unvalidated candidate. It has not been installed or tested in game."
