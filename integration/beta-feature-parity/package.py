"""Package a validated beta PC candidate without any captured reference DLLs."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--source-patch', type=Path)
p.add_argument('--repair-base', type=Path, help='Original Nov 1 candidate build-receipt.json')
p.add_argument('--repair-previous', type=Path, action='append', default=[], help='Additional reviewed candidate build-receipt.json')
a = p.parse_args()
here = Path(__file__).resolve().parent
root = here.parents[1]
candidate = a.candidate.resolve()
receipt = json.loads((candidate / 'build-receipt.json').read_text())
validation = json.loads((candidate / 'validation.json').read_text())
assert validation['status'] == 'managed-and-fixture-checks-passed-needs-pc-gameplay'
assert all(x['exit_code'] == 0 for x in validation['results'])
expected = {'AnchorChain.dll', 'SEST.BetaSafeBootstrap.dll', 'SEST.RuntimeFixes.dll',
            'SEST.ContactsFix.dll', 'SEST.IdentifyDataPaths.dll'}
assert set(receipt['files']) == expected
assert validation['tested_files'] == receipt['files'], 'Validation belongs to different payload bytes'
for name, expected_hash in receipt['files'].items():
    assert hashlib.sha256((candidate / name).read_bytes()).hexdigest() == expected_hash, name
for name, expected_hash in receipt['source_files'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected_hash, 'Source changed after verification: ' + name
readme = '''SEST BETA FUNCTIONALITY TEST — CAPTURED ASSEMBLY 499675cd, 9 NOVEMBER 2026

Stay on the beta game build. This is a beta compatibility test candidate,
with the complete pre-beta Runtime feature implementation; it is not yet
a gameplay-verified Steam release. Do not use the earlier stable restore ZIP.

PC STEPS (close Sea Power before each command)

1. Extract this ZIP into Downloads, then double-click 1-Stage-Beta.cmd.
2. Launch beta to the MAIN MENU. Wait about 10 seconds, then quit the game.
   This first launch only checks startup readiness; plugins remain inactive.
3. Double-click 2-Enable-Beta.cmd. It requires the successful menu probe,
   migrates local Identify data, removes its Local row and enables the loader.
4. Launch beta again and test the features listed below. Quit when finished.
5. Double-click 3-Capture-Test-Results.cmd and attach the resulting
   SEST-Beta-References-*.zip from Downloads to the chat.

If the first probe or Enable stops, run 3-Capture-Test-Results.cmd and send
the ZIP/error. Do not skip the probe by creating flags manually.

WHAT TO CHECK

- Mod Manager: Identify Expanded appears once, as Workshop; no Local entry.
- F11: Cumulative Combat Costs opens; current, last-game and campaign totals,
  quantities, loss values and history are present.
- Finish a mission: debrief cost rows and mission completion time display.
- Continue to a second mission: preparation map/units, preparation and start.
- Contacts: shortcut/opening; Space and +/- control time; pop out and return.
- Formation: original/enhanced controls, pop out/return and responsiveness.
- Compass: hidden on the tactical map, retained on unit video.

RESTORE

With the game closed, run Restore-Previous-SEST.cmd. Original SEST code is
backed up before staging, and local Identify data is backed up before moving.
New/migrated Identify data remains under %LOCALAPPDATA%\\SEST\\IdentifyExpanded.
Backups remain under %LOCALAPPDATA%\\SEST\\BetaCompatibility\\backups.
Settings restore byte for byte if unchanged since Enable; later edits are kept.

This candidate updates code inside your existing SEST Workshop item 3812461539.
It preserves campaign/data packs and saves, keeps the Workshop Identify DLL,
and does not change the Steam branch, game DLLs or original AnchorChain files.

The standard Steam game location is used directly. For another installation,
open PowerShell here and run, replacing the example path:

powershell -NoProfile -ExecutionPolicy Bypass -File .\\Install-SEST-Beta.ps1 -Action Stage -GameRoot "D:\\SteamLibrary\\steamapps\\common\\Sea Power"

Use the same -GameRoot for Enable, Collect or Restore. For Workshop content in
a separate Steam library, also supply -WorkshopContentRoot pointing directly
to that library's steamapps\\workshop\\content\\1286220 folder.

See BETA-FEATURE-PARITY.md for implementation, source provenance and build notes.
VALIDATION.json records the managed and fixture checks. In-game rendering,
second-monitor behavior and campaign progression remain to be verified on PC.
'''
commands = {
    '1-Stage-Beta.cmd': 'Stage', '2-Enable-Beta.cmd': 'Enable',
    '3-Capture-Test-Results.cmd': 'Collect', 'Restore-Previous-SEST.cmd': 'Restore',
}
repair_commands = {}
if a.repair_base:
    readme = (here / 'R11-PC-TESTS.txt').read_text(encoding='utf-8') + "\n\n" + readme
    repair_commands = {'Repair-Beta-Startup.cmd':'Repair', 'Disable-Beta-Test.cmd':'Disable',
                       'Capture-Repair-Results.cmd':'Collect'}
a.output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(a.output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name in sorted(expected):
        z.write(candidate / name, 'payload/' + name)
    z.write(candidate / 'build-receipt.json', 'payload/build-receipt.json')
    z.write(candidate / 'validation.json', 'VALIDATION.json')
    z.write(here / 'Install-SEST-Beta.ps1', 'Install-SEST-Beta.ps1')
    z.write(root / 'tools/capture-beta-references.ps1', 'capture-beta-references.ps1')
    z.write(here / 'README.md', 'BETA-FEATURE-PARITY.md')
    z.write(here.parent / 'beta-anchorchain/LICENSE.md', 'AnchorChain-LICENSE.md')
    z.write(here / 'third-party/SeaPowerTopo-LICENSE.txt', 'Topography-MIT-LICENSE.txt')
    if a.repair_base:
        base = json.loads(a.repair_base.read_text())
        z.write(here / 'Repair-SEST-Beta-Startup.ps1', 'Repair-SEST-Beta-Startup.ps1')
        previous = [json.loads(path.read_text())['files'] for path in a.repair_previous]
        z.writestr('repair-receipt.json', json.dumps({'format':1,'base_files':base['files'],'previous_files':previous},indent=2))
    z.writestr('README-FIRST.txt', readme.replace('\n', '\r\n').encode('utf-8-sig'))
    for name, action in commands.items():
        text = '@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-SEST-Beta.ps1" -Action ' + action
        text += '\r\nif errorlevel 1 echo Script stopped. Copy the error above into the chat.\r\npause\r\n'
        z.writestr(name, text)
    for name, action in repair_commands.items():
        text = '@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Repair-SEST-Beta-Startup.ps1" -Action ' + action
        text += '\r\nif errorlevel 1 echo Repair stopped. Copy the error above into chat.\r\npause\r\n'
        z.writestr(name, text)
    if a.source_patch:
        z.write(a.source_patch, 'SOURCE-CHANGES.patch')
with zipfile.ZipFile(a.output) as z:
    assert z.testzip() is None
    assert {Path(n).name for n in z.namelist() if n.lower().endswith('.dll')} == expected
    for name, expected_hash in receipt['files'].items():
        assert hashlib.sha256(z.read('payload/' + name)).hexdigest() == expected_hash
print(a.output.name, a.output.stat().st_size, 'bytes; payload allowlist/hashes and ZIP verified')
