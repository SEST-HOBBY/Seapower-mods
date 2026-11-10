"""Run the beta candidate's managed and installer checks, without launching Unity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--capture', type=Path, required=True)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--flat-references', type=Path, required=True)
p.add_argument('--mono', required=True)
p.add_argument('--powershell', required=True)
p.add_argument('--previous-package', type=Path, action='append', default=[])
p.add_argument('--previous-payload', type=Path, action='append', default=[])
p.add_argument('--repair-package', type=Path)
p.add_argument('--previous-capture', type=Path, action='append', default=[], help='Capture each previous candidate was reviewed and staged against: one for all, or one per --previous-package in order; defaults to --capture')
p.add_argument('--workshop-references', type=Path, help='Newer captured Workshop DLL tree for compatibility checks')
a = p.parse_args()
here = Path(__file__).resolve().parent
root = here.parents[1]
capture = a.capture.resolve()
# A previous candidate's own installer refuses author DLLs newer than its
# review (Pop-Out Windows 1.1.1 became 1.1.3 on 3 Nov 2026), while the repair
# checks only the game, BepInEx and Identify references, which both captures
# share. So an upgrade test stages the previous candidate on its own capture.
previous_captures = [c.resolve() for c in a.previous_capture] or [capture]
out = a.candidate.resolve()
flat = a.flat_references.resolve()
workshop = a.workshop_references.resolve() if a.workshop_references else capture / 'references/workshop/library-1'
original = capture / 'references/workshop/library-1/3812461539/plugins/SEST.RuntimeFixes.dll'
# A capture taken after a candidate was installed holds that candidate in the
# Workshop folder; the parity checks then use the repository's preserved 1.5.0.
if hashlib.sha256(original.read_bytes()).hexdigest() != '7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986':
    original = root / 'integration/runtime-fixes/SEST.RuntimeFixes.dll'
    assert hashlib.sha256(original.read_bytes()).hexdigest() == '7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986', 'preserved Runtime 1.5.0 missing'
runtime, ui = out / 'SEST.RuntimeFixes.dll', out / 'SEST.ContactsFix.dll'
results = []
(out / 'validation.json').unlink(missing_ok=True)


def run(name, command):
    result = subprocess.run([str(x) for x in command], cwd=root, env=os.environ.copy(), capture_output=True, text=True)
    stdout = result.stdout
    stderr = result.stderr
    stdout = re.sub(r'[/\\]tmp[/\\]SEST-(?:Beta-Installer-Test|Workshop-Features)-[^\s]+', '<FIXTURE>', stdout)
    results.append({'name': name, 'exit_code': result.returncode, 'stdout': stdout.strip(), 'stderr': stderr.strip()})
    if result.returncode:
        print(name, 'FAILED\n', stdout, stderr)
        raise SystemExit(result.returncode)
    print(name, 'passed')


run('runtime-api-preservation', [sys.executable, here / 'tests/check_runtime_contract.py', original, runtime])
run('native-bindings', [a.mono, out / 'NativeBindingTests.exe', flat, runtime, workshop])
run('native-plugin-transpilers', [a.mono, out / 'HookTests.exe', flat, runtime, ui, workshop])
run('runtime-history-policy-parity', [a.mono, out / 'RuntimeParityTests.exe', flat, original, runtime])
run('price-factory-caching', [a.mono, out / 'CatalogueRuntimeTests.exe', flat, runtime, ui])
run('identify-path-detours', [a.mono, out / 'PathTests.exe', workshop / '3790594162/IdentifyExpanded.dll'])
run('bounded-loader-scheduler', [a.mono, out / 'LoaderTests.exe'])
run('assembly-preload-policy-and-identify-geometry', [a.mono, out / 'AssemblyPolicyTests.exe', workshop, flat / 'Seapower-Scripts.dll'])
run('campaign-scenario-beta-api-regressions', [a.mono, out / 'BetaApiTests.exe', workshop, flat / 'Seapower-Scripts.dll'])
run('cost-rows-and-sest-catalog-fallback', [a.mono, out / 'CostRowsTests.exe', flat, runtime])
run('world-service-and-strike-bindings', [a.mono, out / 'WorldOperationsTests.exe', flat, runtime, workshop])
run('world-battle-preparation-and-exit', [a.mono, out / 'WorldBattleFlowTests.exe', flat, ui, workshop / '3813157776/DynamicCampaignMod.dll'])
run('installer-rollback', [a.powershell, '-NoLogo', '-NoProfile', '-File', here / 'tests/Test-Installer.ps1', '-Capture', capture, '-Candidate', out])
# The pack's SETUP feature step with this source's installer and payload:
# opt-out after Disable/Remove, another game build, author-file drift and a
# Steam refresh while staged. The previously published stable UI (the release
# base commit's) checks that a Restore keeps Steam's newer normal-release copy.
published_ui = out.parent / (out.name + '.published-ui.dll')
shown = subprocess.run(['git', '-C', str(root), 'show', '72129cb45d3ec49d145ab323f16111089d868edb:integration/ui-followup/SEST.ContactsFix.dll'], capture_output=True)
feature_step = [a.powershell, '-NoLogo', '-NoProfile', '-File', here / 'tests/Test-WorkshopFeatures.ps1', '-Capture', capture, '-Candidate', out]
if shown.returncode == 0 and hashlib.sha256(shown.stdout).hexdigest() == '51b56f5efb4c32dcd7f9d71633564613707e6484c3cffdea1adc891b589588f7':
    published_ui.write_bytes(shown.stdout)
    feature_step += ['-PublishedUi', published_ui]
try:
    run('workshop-setup-feature-step', feature_step)
finally:
    published_ui.unlink(missing_ok=True)
if len(a.previous_package) != len(a.previous_payload):
    raise SystemExit('Pair every previous package with its matching payload.')
if len(previous_captures) not in (1, len(a.previous_package)) and a.previous_package:
    raise SystemExit('Give one --previous-capture for all previous packages, or one for each.')
if a.repair_package:
    for index, (package, payload) in enumerate(zip(a.previous_package, a.previous_payload), 1):
        previous_capture = previous_captures[0] if len(previous_captures) == 1 else previous_captures[index - 1]
        run('existing-candidate-repair-rollback-' + str(index), [a.powershell, '-NoLogo', '-NoProfile', '-File', here / 'tests/Test-Installer.ps1',
            '-Capture', previous_capture, '-Candidate', payload.resolve(), '-RepairPackage', a.repair_package.resolve(), '-PreviousPackage', package.resolve(), '-RepairCapture', capture])
run('loader-source-contracts', [sys.executable, here.parent / 'beta-anchorchain/test_source_contract.py'])
report = {
    'format': 1, 'status': 'managed-and-fixture-checks-passed-needs-pc-gameplay',
    'limitations': ['No Unity/game launch', 'No Noesis native rendering', 'No second-monitor test',
                    'PowerShell installer fixture used the available host; Windows PowerShell 5.1 execution still needs PC testing'],
    'results': results,
    'tested_files': {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                     for name in json.loads((out / 'build-receipt.json').read_text())['files']},
}
(out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print('All managed/installer checks passed. PC gameplay validation remains required.')
