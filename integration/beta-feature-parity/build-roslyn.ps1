#Requires -Version 7.4
<#
Build the beta candidate with the Roslyn compiler that PowerShell 7 itself
ships (Microsoft.CodeAnalysis.CSharp, C# 12), from the owner's captured beta
references. It never installs a game file.

This is the same build as build.py, without a .NET SDK: the same captured
reference checks, the same source sets, the same generated files, the same
compiler switches (no standard library, no config, deterministic, optimised,
C# 12) and the same receipt. Only the compiler differs, so the output hashes
differ from a build.py build; the receipt records which compiler produced them.

    pwsh -NoProfile -File integration/beta-feature-parity/build-roslyn.ps1 `
        -Capture <extracted SEST-Beta-References-*> -Output <separate folder>
#>
param(
    [Parameter(Mandatory)][string]$Capture,
    [Parameter(Mandatory)][string]$Output,
    [string]$Revision = 'R12-20261109-workshop-features-499675cd'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$here = $PSScriptRoot
$root = (Resolve-Path (Join-Path $here '..' '..')).Path
$capture = (Resolve-Path $Capture).Path
$pins = @{
    'Seapower-Scripts.dll' = '499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9'
    'Noesis.NoesisGUI.dll' = '7b1fd6a6b90d0692297906f5907a1b4a2072bf3bf25a983b36aaa5b5c043ebdd'
    'AnchorChain.dll' = 'e272811050698640a8936834363da91769dbc83e017637e3629c21bca6bea764'
    'AnchorChain.Preloader.dll' = '1ee1570f1e7f457ffa63c24ee4085b2cdea8069ea8cebf146de5ef027eaa3984'
    'IdentifyExpanded.dll' = '9f0ec630e9d7659082bdce61743a87895de14f1903a44c68395f8f158af8afd7'
    'SeaPowerPopOut.dll' = 'a8f1092ac247032219ebf00aa773b91d14f4bb4a7f2575ca1a4594da57abd882'
    'ContactLog.dll' = 'a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e'
    'SeaPowerSquadPanel.dll' = '6230e8e78e2ba7ba222241d0c3dcc881d2507ebeeb4eab24b6401cc9144283dd'
    'CombatCosts.dll' = '8f7195ff1540d1901446b3783789c84e1f76bebe943da7606afd85f9dd3d78bc'
    '0Harmony.dll' = '1a21cc03424fc82c3dd1346905d16494536b9595ae4162228d99fb7c285c1031'
    'BepInEx.dll' = 'c65b42034bc8ffb9f0b336e416dc3884e3f99fc5a5a89eb1f2ff7868412322cd'
    'Mono.Cecil.dll' = '7ae470288fff4a402899c254d0a76cefef55877f5c54f96e83c797cc5bb6e2f6'
    'UnityEngine.CoreModule.dll' = 'e59403b80679d6200746b4132466acec651e225cd8e687ce2b96787a393d8c69'
    'UnityEngine.InputLegacyModule.dll' = '89c49ce8f2e25366a07f2d2fd56dc75c20066a0ed8c62fb19bb0ff5ce63fb3ac'
    'UnityEngine.IMGUIModule.dll' = '1f671635c05cfeecdac0e24fe26f9ebe26f182e6a1ba3c3b1031b1e8145a865d'
}

function Sha([string]$path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function J { $p = [string]$args[0]; for ($i = 1; $i -lt $args.Count; $i++) { $p = [IO.Path]::Combine($p, [string]$args[$i]) }; $p }

$receiptIn = Get-Content -LiteralPath (J $capture 'capture.json') -Raw | ConvertFrom-Json
if ($receiptIn.native_sha256 -ne $pins['Seapower-Scripts.dll']) { throw 'This candidate targets beta 0.8.7-261107 (499675cd) only.' }
foreach ($ref in $receiptIn.references) {
    if ((Sha (J $capture $ref.path)) -ne $ref.sha256) { throw ('Capture integrity failure: ' + $ref.path) }
}
$refs = J $capture 'references'
$managed = J $refs 'managed'
$core = J $refs 'bepinex' 'core'
$preloader = J $refs 'bepinex' 'plugins' 'AnchorChain.Preloader.dll'
$workshop = J $refs 'workshop' 'library-1'
$inputs = @{
    'AnchorChain.dll' = (J $workshop '3380210757' 'AnchorChain.dll')
    'IdentifyExpanded.dll' = (J $workshop '3790594162' 'IdentifyExpanded.dll')
    'SeaPowerPopOut.dll' = (J $workshop '3826396311' 'SeaPowerPopOut.dll')
    'ContactLog.dll' = (J $workshop '3819427362' 'ContactLog.dll')
    'SeaPowerSquadPanel.dll' = (J $workshop '3818251045' 'SeaPowerSquadPanel.dll')
    'CombatCosts.dll' = (J $workshop '3807187341' 'CombatCosts.dll')
    'AnchorChain.Preloader.dll' = $preloader
    '0Harmony.dll' = (J $core '0Harmony.dll')
    'BepInEx.dll' = (J $core 'BepInEx.dll')
    'Mono.Cecil.dll' = (J $core 'Mono.Cecil.dll')
}
foreach ($n in 'Seapower-Scripts.dll', 'Noesis.NoesisGUI.dll', 'UnityEngine.CoreModule.dll', 'UnityEngine.InputLegacyModule.dll', 'UnityEngine.IMGUIModule.dll') { $inputs[$n] = J $managed $n }
foreach ($name in $inputs.Keys) {
    if ((Sha $inputs[$name]) -ne $pins[$name]) { throw ('Uninspected reference: ' + $name) }
}
# The reconstruction's baseline is the owner's captured Runtime 1.5.0. A capture
# taken after a beta candidate was installed holds that candidate in the
# Workshop folder instead, so the repository's preserved copy of the same
# binary is accepted in its place; either way the hash must be 1.5.0's.
$originalHash = '7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986'
$original = J $workshop '3812461539' 'plugins' 'SEST.RuntimeFixes.dll'
if ((Sha $original) -ne $originalHash) {
    $original = J $root 'integration' 'runtime-fixes' 'SEST.RuntimeFixes.dll'
    if ((Sha $original) -ne $originalHash) { throw 'Runtime source provenance does not match the captured 1.5.0.' }
    Write-Host 'captured Workshop runtime is a candidate build; using the preserved 1.5.0 binary from integration/runtime-fixes'
}

$out = [IO.Path]::GetFullPath($Output)
foreach ($source in $capture, $here) { if ($out -eq $source) { throw 'Choose a separate build output directory.' } }
New-Item -ItemType Directory -Force -Path $out | Out-Null
$generated = J $out 'generated'
New-Item -ItemType Directory -Force -Path $generated | Out-Null

# Match Unity's actual Mono profile, as build.py does.
$names = 'mscorlib.dll', 'netstandard.dll', 'System.dll', 'System.Core.dll', 'System.Xml.dll', 'System.Numerics.dll',
    'Seapower-Scripts.dll', 'Noesis.NoesisGUI.dll', 'UnityEngine.dll', 'UnityEngine.CoreModule.dll',
    'UnityEngine.IMGUIModule.dll', 'UnityEngine.InputLegacyModule.dll', 'UnityEngine.ParticleSystemModule.dll'
$references = @($names | ForEach-Object { J $managed $_ })
$references += (J $core '0Harmony.dll'), (J $core 'BepInEx.dll'), (J $core 'Mono.Cecil.dll'), $preloader

$compilerAssembly = [Microsoft.CodeAnalysis.CSharp.CSharpCompilation].Assembly
$compilerInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($compilerAssembly.Location)
$parse = [Microsoft.CodeAnalysis.CSharp.CSharpParseOptions]::Default.WithLanguageVersion([Microsoft.CodeAnalysis.CSharp.LanguageVersion]::CSharp12)

function Compile([string]$name, [string[]]$sources, [bool]$anchor = $true) {
    $extra = @($references)
    if ($anchor) { $extra += (J $out 'AnchorChain.dll') }
    $trees = foreach ($src in $sources) {
        $text = [IO.File]::ReadAllText($src)
        [Microsoft.CodeAnalysis.CSharp.CSharpSyntaxTree]::ParseText($text, $parse, $src)
    }
    $metadata = foreach ($r in $extra) { [Microsoft.CodeAnalysis.MetadataReference]::CreateFromFile($r) }
    $kind = if ($name.EndsWith('.exe')) { [Microsoft.CodeAnalysis.OutputKind]::ConsoleApplication } else { [Microsoft.CodeAnalysis.OutputKind]::DynamicallyLinkedLibrary }
    $options = [Microsoft.CodeAnalysis.CSharp.CSharpCompilationOptions]::new($kind)
    $options = $options.WithOptimizationLevel([Microsoft.CodeAnalysis.OptimizationLevel]::Release).WithDeterministic($true).WithPlatform([Microsoft.CodeAnalysis.Platform]::AnyCpu)
    $compilation = [Microsoft.CodeAnalysis.CSharp.CSharpCompilation]::Create([IO.Path]::GetFileNameWithoutExtension($name),
        [Microsoft.CodeAnalysis.SyntaxTree[]]@($trees), [Microsoft.CodeAnalysis.MetadataReference[]]@($metadata), $options)
    $target = J $out $name
    $stream = [IO.File]::Create($target)
    try { $result = $compilation.Emit($stream) } finally { $stream.Dispose() }
    foreach ($d in $result.Diagnostics) {
        if ($d.Severity -eq [Microsoft.CodeAnalysis.DiagnosticSeverity]::Error) { Write-Host ('  ' + $d.ToString()) }
    }
    if (-not $result.Success) { Remove-Item -LiteralPath $target -ErrorAction SilentlyContinue; throw ('Compilation failed: ' + $name) }
    Write-Host ('compiled ' + $name)
}

$globalUsings = J $generated 'GlobalUsings.cs'
[IO.File]::WriteAllText($globalUsings, "global using System;`nglobal using System.IO;`nglobal using System.Linq;`nglobal using System.Collections.Generic;`n")
$version = J $generated 'AnchorVersion.cs'
[IO.File]::WriteAllText($version, "[assembly:System.Reflection.AssemblyVersion(`"1.1.0.0`")]`n[assembly:System.Reflection.AssemblyFileVersion(`"1.1.0.0`")]`n")

function SortedCs([string]$folder) {
    # The unary comma keeps a one-file folder an array when the function returns.
    $list = @(Get-ChildItem -LiteralPath $folder -Filter '*.cs' -File | Sort-Object -Property Name -Culture '' | ForEach-Object { $_.FullName })
    return ,$list
}
$anchorDir = J $here '..' 'beta-anchorchain'
$anchorSources = SortedCs (J $anchorDir 'source')
Compile 'AnchorChain.dll' ($anchorSources + @($globalUsings, $version)) $false
Compile 'SEST.BetaSafeBootstrap.dll' @((J $anchorDir 'SEST.BetaSafeBootstrap.cs')) $false
$runtimeSources = SortedCs (J $here 'runtime')
Compile 'SEST.RuntimeFixes.dll' $runtimeSources
$runtimeHash = Sha (J $out 'SEST.RuntimeFixes.dll')

function Pins([string]$namespace) {
    $path = J $generated ($namespace + '.Pins.cs')
    [IO.File]::WriteAllText($path, ('namespace ' + $namespace + ' { internal static class BuildPins { internal const string RuntimeSha256 = "' + $runtimeHash + '"; } }' + "`n"))
    $path
}
$uiSources = SortedCs (J $here 'ui')
$identifySources = SortedCs (J $here 'identify')
Compile 'SEST.ContactsFix.dll' ($uiSources + @((Pins 'Sest.UiFixes')))
Compile 'SEST.IdentifyDataPaths.dll' ($identifySources + @((Pins 'Sest.IdentifyDataPaths')))
Compile 'NativeBindingTests.exe' @((J $here 'tests' 'NativeBindingTests.cs'))
Compile 'CatalogueRuntimeTests.exe' @((J $here 'tests' 'CatalogueRuntimeTests.cs'))
Compile 'PathTests.exe' (@((J $here 'tests' 'PathTests.cs')) + $identifySources + @((Pins 'Sest.IdentifyDataPaths')))
Compile 'LoaderTests.exe' @((J $here 'tests' 'LoaderTests.cs'))
Compile 'RuntimeParityTests.exe' @((J $here 'tests' 'RuntimeParityTests.cs'))
Compile 'HookTests.exe' @((J $here 'tests' 'HookTests.cs'))
Compile 'AssemblyPolicyTests.exe' @((J $here 'tests' 'AssemblyPolicyTests.cs'))
# R6: BetaApiTests.cs plus one BetaApiTests.<Plugin>.cs per adapter.
Compile 'BetaApiTests.exe' @(Get-ChildItem -LiteralPath (J $here 'tests') -Filter 'BetaApiTests*.cs' -File | Sort-Object -Property Name -Culture '' | ForEach-Object { $_.FullName })
if (Test-Path -LiteralPath (J $here 'tests' 'CostRowsTests.cs')) { Compile 'CostRowsTests.exe' @((J $here 'tests' 'CostRowsTests.cs')) }

Compile 'WorldOperationsTests.exe' @((J $here 'tests' 'WorldOperationsTests.cs'))
Compile 'WorldBattleFlowTests.exe' @((J $here 'tests' 'WorldBattleFlowTests.cs'))

$outputs = 'AnchorChain.dll', 'SEST.BetaSafeBootstrap.dll', 'SEST.RuntimeFixes.dll', 'SEST.ContactsFix.dll', 'SEST.IdentifyDataPaths.dll'
$sourceFiles = @($runtimeSources) + @(Get-ChildItem -LiteralPath (J $here 'ui') -Filter '*.cs' -File | ForEach-Object { $_.FullName })
$sourceFiles += @(Get-ChildItem -LiteralPath (J $here 'identify') -Filter '*.cs' -File | ForEach-Object { $_.FullName })
$sourceFiles += @($anchorSources) + @((J $anchorDir 'SEST.BetaSafeBootstrap.cs'), (J $here 'build.py'), $PSCommandPath)
$sourceFiles += @(Get-ChildItem -LiteralPath (J $here 'tests') -File | Where-Object { $_.Name -like '*.cs' -or $_.Name -like '*.ps1' } | ForEach-Object { $_.FullName })
$sourceFiles += @((J $here 'R11-PC-TESTS.txt'), (J $here 'README.md'), (J $root 'tools' 'capture-beta-references.ps1'))
$sourceFiles += @((J $here 'Install-SEST-Beta.ps1'), (J $here 'Repair-SEST-Beta-Startup.ps1'), (J $here 'tests' 'check_runtime_contract.py'), (J $here 'verify.py'), (J $here 'package.py'))

$files = [ordered]@{}
foreach ($n in $outputs) { $files[$n] = Sha (J $out $n) }
$sourceHashes = [ordered]@{}
foreach ($p in ($sourceFiles | ForEach-Object { [IO.Path]::GetFullPath($_) } | Sort-Object -Unique)) {
    $rel = [IO.Path]::GetRelativePath($root, $p).Replace('\', '/')
    $sourceHashes[$rel] = Sha $p
}
$manifest = [ordered]@{
    format = 1
    status = 'compiled-candidate-needs-pc-gameplay-test'
    candidate_revision = $Revision
    target_game_sha256 = $pins['Seapower-Scripts.dll']
    target_noesis_sha256 = $pins['Noesis.NoesisGUI.dll']
    runtime_source = 'reconstructed-from-captured-1.5.0; original-project-not-recovered'
    original_runtime_sha256 = (Sha $original)
    original_runtime_path = [IO.Path]::GetRelativePath($root, $original).Replace('\', '/')
    captured_references = $pins
    compiler = ('PowerShell ' + $PSVersionTable.PSVersion + ' bundled Microsoft.CodeAnalysis.CSharp ' + $compilerInfo.ProductVersion + ' (C# 12, deterministic, optimised, no standard library)')
    compiler_sha256 = (Sha $compilerAssembly.Location)
    files = $files
    source_files = $sourceHashes
}
[IO.File]::WriteAllText((J $out 'build-receipt.json'), (($manifest | ConvertTo-Json -Depth 5) + "`n"))
Write-Host 'Beta candidate compiled. No game or Workshop files installed.'
