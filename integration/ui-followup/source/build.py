"""Build with Roslyn and the captured references. No game files are modified."""
import argparse
import pathlib
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--dotnet', required=True)
p.add_argument('--compiler', required=True)
p.add_argument('--framework', required=True, help='NETStandard.Library.Ref 2.1.0 ref/netstandard2.1')
p.add_argument('--references', required=True, help='Captured game/BepInEx DLL folder')
p.add_argument('--output', required=True)
p.add_argument('--runtime', help='Captured SEST.RuntimeFixes.dll; run factory/transpiler differential checks when supplied')
a = p.parse_args()
here = pathlib.Path(__file__).resolve().parent
out = pathlib.Path(a.output).resolve()
out.mkdir(parents=True, exist_ok=True)
framework = pathlib.Path(a.framework).resolve()
refs = pathlib.Path(a.references).resolve()
prefix = [a.dotnet, a.compiler, '-nologo', '-noconfig', '-nostdlib+', '-deterministic+', '-optimize+', '-langversion:9']
base_refs = ['-r:' + str(f) for f in sorted(framework.glob('*.dll'))]
def compile(extra):
    result = subprocess.run(prefix + base_refs + extra)
    if result.returncode:
        raise SystemExit(result.returncode)
compile(['-target:library', '-out:' + str(out / 'AnchorChain.dll'), str(here / 'AnchorChain.Reference.cs')])
assemblies = ['0Harmony.dll', 'BepInEx.dll', 'Noesis.NoesisGUI.dll', 'Seapower-Scripts.dll',
              'UnityEngine.CoreModule.dll', 'UnityEngine.IMGUIModule.dll', 'UnityEngine.InputLegacyModule.dll']
compile(['-target:library', '-out:' + str(out / 'SEST.ContactsFix.dll'), '-r:' + str(out / 'AnchorChain.dll')]
        + ['-r:' + str(refs / n) for n in assemblies]
        + [str(here / n) for n in ['InputPolicy.cs', 'ContactsFix.cs', 'ContactsSurfaceFix.cs', 'FormationModeState.cs', 'FormationUiMode.cs',
                                  'LookupCache.cs', 'UiRefreshGate.cs', 'FlightFlagReader.cs', 'PerformanceReview.cs',
                                  'UiText.cs', 'UiRefinements.cs', 'FormationPerformance.cs', 'FormationBoundsGate.cs', 'CameraCompass.cs', 'CompassRouting.cs',
                                  'CleanupBatchGate.cs', 'TerrainCleanup.cs', 'FrameWindow.cs', 'FramePacing.cs', 'StutterDiagnostics.cs', 'DiagnosticModules.cs', 'ScopeValueCache.cs', 'CostCatalogueCache.cs']])
compile(['-target:exe', '-out:' + str(out / 'InputPolicyTests.dll'), str(here / 'InputPolicy.cs'), str(here / 'InputPolicyTests.cs')])
(out / 'InputPolicyTests.runtimeconfig.json').write_text('{"runtimeOptions":{"tfm":"net8.0","framework":{"name":"Microsoft.NETCore.App","version":"8.0.0"}}}')
subprocess.run([a.dotnet, str(out / 'InputPolicyTests.dll')], check=True)
compile(['-target:exe', '-out:' + str(out / 'FormationModeTests.dll'), str(here / 'FormationModeState.cs'), str(here / 'FormationModeTests.cs')])
(out / 'FormationModeTests.runtimeconfig.json').write_text((out / 'InputPolicyTests.runtimeconfig.json').read_text())
subprocess.run([a.dotnet, str(out / 'FormationModeTests.dll')], check=True)
compile(['-target:exe', '-out:' + str(out / 'PerformancePolicyTests.dll'), str(here / 'LookupCache.cs'),
         str(here / 'FlightFlagReader.cs'), str(here / 'UiRefreshGate.cs'), str(here / 'PerformancePolicyTests.cs')])
(out / 'PerformancePolicyTests.runtimeconfig.json').write_text((out / 'InputPolicyTests.runtimeconfig.json').read_text())
subprocess.run([a.dotnet, str(out / 'PerformancePolicyTests.dll')], check=True)
compile(['-target:exe', '-out:' + str(out / 'UiRefinementTests.dll'), str(here / 'UiText.cs'),
         str(here / 'CompassRouting.cs'), str(here / 'FormationBoundsGate.cs'), str(here / 'UiRefinementTests.cs')])
(out / 'UiRefinementTests.runtimeconfig.json').write_text((out / 'InputPolicyTests.runtimeconfig.json').read_text())
subprocess.run([a.dotnet, str(out / 'UiRefinementTests.dll')], check=True)
compile(['-target:exe', '-out:' + str(out / 'StutterPolicyTests.dll'), str(here / 'CleanupBatchGate.cs'),
         str(here / 'FrameWindow.cs'), str(here / 'StutterPolicyTests.cs')])
(out / 'StutterPolicyTests.runtimeconfig.json').write_text((out / 'InputPolicyTests.runtimeconfig.json').read_text())
subprocess.run([a.dotnet, str(out / 'StutterPolicyTests.dll')], check=True)
if a.runtime:
    compile(['-target:exe', '-out:' + str(out / 'CatalogueRuntimeTests.dll'), '-r:' + str(refs / '0Harmony.dll'),
             str(here / 'CatalogueRuntimeTests.cs')])
    (out / 'CatalogueRuntimeTests.runtimeconfig.json').write_text((out / 'InputPolicyTests.runtimeconfig.json').read_text())
    subprocess.run([a.dotnet, str(out / 'CatalogueRuntimeTests.dll'), str(refs), str(pathlib.Path(a.runtime).resolve()),
                    str(out / 'SEST.ContactsFix.dll')], check=True)
print('Build and regression checks passed. Install SEST.ContactsFix.dll only.')
