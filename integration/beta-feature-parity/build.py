"""Build the beta candidate from captured references; never install game files.

The complete Runtime reconstruction is derived from the owner's captured 1.5.0,
not the older 1.2 fork base. Output is beta-only and separate from the stable pack.
Use Roslyn 4.12+ and a .NET 8 host. No native/third-party reference DLL is shipped.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    'Seapower-Scripts.dll': '499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9',
    'Noesis.NoesisGUI.dll': '7b1fd6a6b90d0692297906f5907a1b4a2072bf3bf25a983b36aaa5b5c043ebdd',
    'AnchorChain.dll': 'e272811050698640a8936834363da91769dbc83e017637e3629c21bca6bea764',
    'AnchorChain.Preloader.dll': '1ee1570f1e7f457ffa63c24ee4085b2cdea8069ea8cebf146de5ef027eaa3984',
    'IdentifyExpanded.dll': '9f0ec630e9d7659082bdce61743a87895de14f1903a44c68395f8f158af8afd7',
    'SeaPowerPopOut.dll': 'a8f1092ac247032219ebf00aa773b91d14f4bb4a7f2575ca1a4594da57abd882',
    'ContactLog.dll': 'a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e',
    'SeaPowerSquadPanel.dll': '6230e8e78e2ba7ba222241d0c3dcc881d2507ebeeb4eab24b6401cc9144283dd',
    'CombatCosts.dll': '8f7195ff1540d1901446b3783789c84e1f76bebe943da7606afd85f9dd3d78bc',
    '0Harmony.dll': '1a21cc03424fc82c3dd1346905d16494536b9595ae4162228d99fb7c285c1031',
    'BepInEx.dll': 'c65b42034bc8ffb9f0b336e416dc3884e3f99fc5a5a89eb1f2ff7868412322cd',
    'Mono.Cecil.dll': '7ae470288fff4a402899c254d0a76cefef55877f5c54f96e83c797cc5bb6e2f6',
    'UnityEngine.CoreModule.dll': 'e59403b80679d6200746b4132466acec651e225cd8e687ce2b96787a393d8c69',
    'UnityEngine.InputLegacyModule.dll': '89c49ce8f2e25366a07f2d2fd56dc75c20066a0ed8c62fb19bb0ff5ce63fb3ac',
    'UnityEngine.IMGUIModule.dll': '1f671635c05cfeecdac0e24fe26f9ebe26f182e6a1ba3c3b1031b1e8145a865d',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--dotnet', required=True)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    capture = a.capture.resolve()
    receipt = json.loads((capture / 'capture.json').read_text(encoding='utf-8-sig'))
    if receipt['native_sha256'] != PINS['Seapower-Scripts.dll']:
        raise SystemExit('This candidate targets beta 0.8.7-261107 (499675cd) only.')
    for ref in receipt['references']:
        if sha(capture / ref['path']) != ref['sha256']:
            raise SystemExit('Capture integrity failure: ' + ref['path'])
    refs = capture / 'references'
    managed = refs / 'managed'
    core = refs / 'bepinex/core'
    preloader = refs / 'bepinex/plugins/AnchorChain.Preloader.dll'
    workshop = refs / 'workshop/library-1'
    author = {
        'AnchorChain.dll': workshop / '3380210757/AnchorChain.dll',
        'IdentifyExpanded.dll': workshop / '3790594162/IdentifyExpanded.dll',
        'SeaPowerPopOut.dll': workshop / '3826396311/SeaPowerPopOut.dll',
        'ContactLog.dll': workshop / '3819427362/ContactLog.dll',
        'SeaPowerSquadPanel.dll': workshop / '3818251045/SeaPowerSquadPanel.dll',
        'CombatCosts.dll': workshop / '3807187341/CombatCosts.dll',
    }
    inputs = dict(author)
    inputs.update({n: managed / n for n in ['Seapower-Scripts.dll', 'Noesis.NoesisGUI.dll',
        'UnityEngine.CoreModule.dll', 'UnityEngine.InputLegacyModule.dll', 'UnityEngine.IMGUIModule.dll']})
    inputs.update({'AnchorChain.Preloader.dll': preloader, '0Harmony.dll': core / '0Harmony.dll', 'BepInEx.dll': core / 'BepInEx.dll', 'Mono.Cecil.dll': core / 'Mono.Cecil.dll'})
    for name, path in inputs.items():
        if sha(path) != PINS[name]:
            raise SystemExit('Uninspected reference: ' + name)
    original = workshop / '3812461539/plugins/SEST.RuntimeFixes.dll'
    if sha(original) != '7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986':
        raise SystemExit('Runtime source provenance does not match the captured 1.5.0.')
    out = a.output.resolve()
    for source in [capture, HERE]:
        if out == source:
            raise SystemExit('Choose a separate build output directory.')
    out.mkdir(parents=True, exist_ok=True)
    generated = out / 'generated'
    generated.mkdir(exist_ok=True)
    # Match Unity's actual Mono profile. The separate netstandard compiler
    # facades cannot resolve Harmony's mscorlib System.Reflection.Emit.Label.
    names = ['mscorlib.dll', 'netstandard.dll', 'System.dll', 'System.Core.dll',
             'System.Xml.dll', 'System.Numerics.dll', 'Seapower-Scripts.dll',
             'Noesis.NoesisGUI.dll', 'UnityEngine.dll', 'UnityEngine.CoreModule.dll',
             'UnityEngine.IMGUIModule.dll', 'UnityEngine.InputLegacyModule.dll',
             'UnityEngine.ParticleSystemModule.dll']
    references = [managed / n for n in names]
    references += [core / '0Harmony.dll', core / 'BepInEx.dll', core / 'Mono.Cecil.dll', preloader]
    prefix = [a.dotnet, str(a.compiler.resolve()), '-nologo', '-noconfig', '-nostdlib+',
              '-deterministic+', '-optimize+', '-langversion:12']

    def compile(name, sources, anchor=True):
        extra = references + ([out / 'AnchorChain.dll'] if anchor else [])
        args = prefix + ['-target:' + ('exe' if name.endswith('.exe') else 'library'),
                         '-out:' + str(out / name)]
        subprocess.run(args + ['-r:' + str(p) for p in extra] + [str(p) for p in sources], check=True)

    global_usings = generated / 'GlobalUsings.cs'
    global_usings.write_text('global using System;\nglobal using System.IO;\n'
                             'global using System.Linq;\nglobal using System.Collections.Generic;\n')
    version = generated / 'AnchorVersion.cs'
    version.write_text('[assembly:System.Reflection.AssemblyVersion("1.1.0.0")]\n'
                       '[assembly:System.Reflection.AssemblyFileVersion("1.1.0.0")]\n')
    anchor_sources = sorted((HERE.parent / 'beta-anchorchain/source').glob('*.cs'))
    compile('AnchorChain.dll', anchor_sources + [global_usings, version], False)
    compile('SEST.BetaSafeBootstrap.dll', [HERE.parent / 'beta-anchorchain/SEST.BetaSafeBootstrap.cs'], False)
    runtime_sources = sorted((HERE / 'runtime').glob('*.cs'))
    compile('SEST.RuntimeFixes.dll', runtime_sources)
    runtime_hash = sha(out / 'SEST.RuntimeFixes.dll')

    def pins(namespace):
        path = generated / (namespace + '.Pins.cs')
        path.write_text('namespace ' + namespace + ' { internal static class BuildPins {'
                        ' internal const string RuntimeSha256 = "' + runtime_hash + '"; } }\n')
        return path

    compile('SEST.ContactsFix.dll', sorted((HERE / 'ui').glob('*.cs')) + [pins('Sest.UiFixes')])
    compile('SEST.IdentifyDataPaths.dll', list((HERE / 'identify').glob('*.cs')) + [pins('Sest.IdentifyDataPaths')])
    compile('NativeBindingTests.exe', [HERE / 'tests/NativeBindingTests.cs'])
    compile('CatalogueRuntimeTests.exe', [HERE / 'tests/CatalogueRuntimeTests.cs'])
    compile('PathTests.exe', [HERE / 'tests/PathTests.cs'] + list((HERE / 'identify').glob('*.cs')) + [pins('Sest.IdentifyDataPaths')])
    compile('LoaderTests.exe', [HERE / 'tests/LoaderTests.cs'])
    compile('RuntimeParityTests.exe', [HERE / 'tests/RuntimeParityTests.cs'])
    compile('HookTests.exe', [HERE / 'tests/HookTests.cs'])
    compile('AssemblyPolicyTests.exe', [HERE / 'tests/AssemblyPolicyTests.cs'])
    compile('BetaApiTests.exe', sorted((HERE / 'tests').glob('BetaApiTests*.cs')))
    compile('CostRowsTests.exe', [HERE / 'tests/CostRowsTests.cs'])
    compile('WorldOperationsTests.exe', [HERE / 'tests/WorldOperationsTests.cs'])
    compile('WorldBattleFlowTests.exe', [HERE / 'tests/WorldBattleFlowTests.cs'])
    compile('MissionAwardsTests.exe', [HERE / 'tests/MissionAwardsTests.cs'])
    outputs = ['AnchorChain.dll', 'SEST.BetaSafeBootstrap.dll', 'SEST.RuntimeFixes.dll',
               'SEST.ContactsFix.dll', 'SEST.IdentifyDataPaths.dll']
    source_files = runtime_sources + list((HERE / 'ui').glob('*.cs')) + list((HERE / 'identify').glob('*.cs'))
    source_files += anchor_sources + [HERE.parent / 'beta-anchorchain/SEST.BetaSafeBootstrap.cs', Path(__file__)]
    source_files += list((HERE / 'tests').glob('*.cs')) + list((HERE / 'tests').glob('*.ps1'))
    source_files += [HERE / 'README.md', HERE / 'R11-PC-TESTS.txt', ROOT / 'tools/capture-beta-references.ps1']
    source_files += [HERE / 'Install-SEST-Beta.ps1', HERE / 'Repair-SEST-Beta-Startup.ps1', HERE / 'tests/check_runtime_contract.py', HERE / 'verify.py', HERE / 'package.py']
    manifest = {
        'format': 1, 'status': 'compiled-candidate-needs-pc-gameplay-test',
        'candidate_revision': 'R12-20261109-workshop-features-499675cd',
        'target_game_sha256': PINS['Seapower-Scripts.dll'], 'target_noesis_sha256': PINS['Noesis.NoesisGUI.dll'],
        'runtime_source': 'reconstructed-from-captured-1.5.0; original-project-not-recovered',
        'original_runtime_sha256': sha(original), 'captured_references': PINS,
        'compiler_sha256': sha(a.compiler),
        'files': {n: sha(out / n) for n in outputs},
        'source_files': {p.relative_to(ROOT).as_posix(): sha(p) for p in source_files},
    }
    (out / 'build-receipt.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Beta candidate compiled. No game or Workshop files installed.')


if __name__ == '__main__':
    main()
