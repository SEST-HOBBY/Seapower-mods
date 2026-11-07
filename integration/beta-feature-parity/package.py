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
readme = '''SEST BETA FUNCTIONALITY TEST — 2 NOVEMBER 2026

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
    readme = '''R6 BETA REPAIR: SEVEN MORE AUTHOR PLUGINS. 7 NOVEMBER 2026

R6 includes all of R5 and R4. It accepts an installed R1, R2, R3, R4 or R5.
1. Close Sea Power and extract this NEW ZIP into a fresh folder.
2. Run Repair-Beta-Startup.cmd. It replaces all five candidate files, keeps
   the original backups and re-enables only after every copy verifies.
3. Launch beta. BepInEx.log should hold an "ADAPTED <plugin> in private
   cache" line for each of WeaponLauncherEffects, SubModelStabilization,
   OptimalTargetDist, MissileControlMod, ParallelRangeProbe, TestRange,
   BetterTacMap, AutomaticSAR and OspreyMechanics, and no "SKIPPED" line for
   AutomaticSAR, OspreyMechanics or OspreyDeckOps. Then check in a mission:
   - an ESSM or Aster 30 VLS shot climbs clear and tips over smoothly, and a
     Mk 41 launch shows its flame and smoke;
   - a German F123's radar platform stays level in a seaway while its radar
     is on;
   - the Map Layers menu lists BetterTacMap's eight Contact Info and Weapon
     Info entries, and a quiet contact's "Last seen" line keeps counting;
   - right-click a ship near a sunk ship with life rafts: "Start automatic
     SAR" is offered and the ship goes to the rafts;
   - an MV-22B on an LHD unfolds, lifts off vertically and converts;
   - F10 > Spawn shows the Test Range tab;
   - fire an AGR-30 Redback, then open F11: the round is listed with its
     price, as in R5;
   - Contacts and the formation window pop out to the second monitor.
4. Quit, run Capture-Repair-Results.cmd and attach its ZIP.
BETA-FEATURE-PARITY.md lists every plugin's full PC checks, what each
brings back and what still needs its author.

Disable-Beta-Test.cmd stops this test activation. Restore-Previous-SEST.cmd
restores the original backed-up code; the repair updates that restore journal.

What R6 changes over R5 (the loader only):
- Seven more Euromod and community plugins that stopped on the beta work
  again through hash-pinned adapters: OptimalTargetDist launch sharing,
  MissileControlMod launch control, ParallelRangeProbe's workers, TestRange,
  BetterTacMap, AutomaticSAR and the MV-22 OspreyMechanics with DeckOps.
- Still off until their authors port them: MultiStageMissiles (so staged
  rounds stage natively and the SS-N-26 hands off after about 6 s),
  ParallelRangeProbe's trajectory preview, UiWorkerProbe and CombatWorker
  (performance only). ExtendedGuidance stays off, as SEST plays it.

Included from R5: WeaponLauncherEffects and SubModelStabilization adapters
and the Pop-Out Windows 1.1.3 pin. From R4: the hidden version watermark,
the #!extend rescan and the cost catalog fallback.

Not in R6: the clipped tab borders (send a full-window screenshot and your
Windows display scaling) and the Global Hawk range (its data is unchanged;
it needs the same mission tried on both Steam branches).

--------------------------------------------------------------------------

''' + readme
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
