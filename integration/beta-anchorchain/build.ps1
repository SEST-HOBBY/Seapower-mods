param(
    [Parameter(Mandatory=$true)][string]$GameRoot,
    [string]$OutDir = ""
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Safe source-only beta build. No writes to Steam game or Workshop folders.
if (!$OutDir) { $OutDir = Join-Path $PSScriptRoot "out" }
$native = Join-Path $GameRoot "Sea Power_Data\Managed\Seapower-Scripts.dll"
$plugin = Join-Path $GameRoot "BepInEx\plugins\AnchorChain.Preloader.dll"
$source = Join-Path $PSScriptRoot "source\Main.cs"
$project = Join-Path $PSScriptRoot "source\AnchorChain.csproj"
$knownBeta = "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62"
$knownPreloader = "1ee1570f1e7f457ffa63c24ee4085b2cdea8069ea8cebf146de5ef027eaa3984"
$knownWorkshop = "e272811050698640a8936834363da91769dbc83e017637e3629c21bca6bea764"

function Hash-File([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$steamCommon = Split-Path -Parent $GameRoot
if ((Split-Path -Leaf $steamCommon) -ine "common") {
    throw "Expected a Steam common/Sea Power installation. No files changed."
}
$steamapps = Split-Path -Parent $steamCommon
$upstream = Join-Path $steamapps "workshop\content\1286220\3380210757\AnchorChain.dll"
foreach ($p in @($native, $plugin, $upstream, $source, $project)) {
    if (!(Test-Path -LiteralPath $p -PathType Leaf)) { throw "Required reference missing: $p" }
}
if ((Hash-File $native) -ne $knownBeta) {
    throw "Uninspected game build. This fork is pinned to beta 0.8.7-261026 only."
}
if ((Hash-File $plugin) -ne $knownPreloader) {
    throw "Anchor Chain preloader changed since captured reference. Review before building."
}
if ((Hash-File $upstream) -ne $knownWorkshop) {
    throw "Upstream Workshop AnchorChain.dll differs from inspected v1.1.0. Review before building."
}

$dotnet = Get-Command "dotnet" -ErrorAction SilentlyContinue
if (!$dotnet) { throw "This fork needs a .NET 8 (or newer) SDK with C# 12. The old Windows Framework csc.exe cannot compile upstream Anchor Chain 1.1.0. No files changed." }
$sdkList = @(& $dotnet.Source --list-sdks)
if ($LASTEXITCODE -ne 0 -or @($sdkList | Where-Object { $_ -match '^([89]|1[0-9])\.' }).Count -eq 0) {
    throw "A .NET 8+ SDK is required. dotnet --list-sdks: $($sdkList -join '; ')"
}

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
& $dotnet.Source build $project "--configuration" "Release" "--property:SESTGameRoot=$GameRoot" "--property:ContinuousIntegrationBuild=true" "--nologo"
if ($LASTEXITCODE -ne 0) { throw "Safe Anchor Chain fork build failed. Nothing installed." }
$candidate = Join-Path $PSScriptRoot "source\bin\Release\netstandard2.1\AnchorChain.dll"
if (!(Test-Path -LiteralPath $candidate -PathType Leaf)) {
    throw "Build reported success but AnchorChain.dll was not found. No files installed."
}
$dest = Join-Path $OutDir "AnchorChain.dll"
Copy-Item -LiteralPath $candidate -Destination $dest -Force
$receipt = [ordered]@{
    format = 1
    target_game_sha256 = (Hash-File $native)
    upstream_workshop_sha256 = (Hash-File $upstream)
    upstream_preloader_sha256 = (Hash-File $plugin)
    fork_source_sha256 = (Hash-File $source)
    fork_dll_sha256 = (Hash-File $dest)
    fork_dll = "AnchorChain.dll"
    created_utc = [DateTime]::UtcNow.ToString("o")
    status = "built-not-gameplay-verified"
}
$receiptPath = Join-Path $OutDir "build-receipt.json"
$receipt | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
Write-Host "SAFE ANCHOR CHAIN SOURCE FORK COMPILED" -ForegroundColor Green
Write-Host "DLL: $dest"
Write-Host "SHA256: $($receipt.fork_dll_sha256)"
Write-Host "Receipt: $receiptPath"
Write-Host "Build only. No Steam/Workshop file was modified or installed."
