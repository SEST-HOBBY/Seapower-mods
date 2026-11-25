"""Bring docs/releases/20261107/validation.json to R16 (run from the repo root).

usage: python3 update_validation_r16.py <file_count> <beta_package_sha256>
"""
import json, sys
from pathlib import Path
count, package_sha = int(sys.argv[1]), sys.argv[2]
p = Path('docs/releases/20261107/validation.json')
v = json.loads(p.read_text(encoding='utf-8'))
C = 'integration/beta-feature-parity/candidates/R16-20261125'
cand = json.loads(Path(C + '/validation.json').read_text(encoding='utf-8'))
receipt = json.loads(Path(C + '/build-receipt.json').read_text(encoding='utf-8'))
branch = 'feature/mno-r16'
v['revision'] = receipt['candidate_revision']
v['status'] = 'compiled-and-fixture-tested-pc-checks-pending'
v['target_game_sha256'] = receipt['target_game_sha256']
v['runtime_version'] = '1.8.0'
v['ui_version'] = '1.6.0'
v['limitations'] = [x for x in v['limitations'] if not x.startswith(('R14 (SEST code for Sea Power 0.9.2', 'R15 (SEST code for the Sea Power 0.9.3', 'R16 (SEST code for the Sea Power 0.9.3'))] + [
    'R16 (SEST code for the Sea Power 0.9.3 Build 261123 public beta, Seapower-Scripts.dll ea653e49, Noesis 99459006) is compiled and passes '
    'the 20 managed and installer checks against the 25 Nov 00:22 reference capture, with Dynamic Campaign Mod 1.0.2 (18a2416e) bridged onto '
    'the 261123 map, and the upgrade from the released R14, the R15 builds and GPT\'s 22 Nov 22:12 R15 (receipt in the repair chain; its '
    'rollback was not simulated because its 22 Nov reference capture is not here); it has not run in the game. The 0.9.3 default branch '
    '(Build 261116 public release) is a different file that has not been captured: R16 stays off on it (r16_093_261123_20261125).',
]
v['release_branch'] = (branch + ' (the branch the PC installs and tests from for this run: GPT\'s 22 Nov source merged with the storm branch, '
    'the 24 Nov 23:53 capture, the 261123 port, interoperability adapters, ice and weather changes)')
v['beta_package_sha256'] = package_sha
v['managed_and_installer'] = cand
v['r16_093_261123_20261125'] = {
    'branch': branch, 'date': '2026-11-25',
    'game': 'Sea Power 0.9.3 Build 261123 public beta (Seapower-Scripts.dll ea653e49632dbaaad16d33b9c51d79b3eec420e7c41954dbcd09d19157beb65a, Noesis 9945900638b4)',
    'capture': 'SEST-Beta-References-20261125-002204-4c3220.zip (uploaded in four parts); mod files from SEST-Workshop-Capture-20261124-235336.zip; '
               'Workshop DLLs from SEST-Extras-20261124.zip',
    'candidate': C, 'revision': receipt['candidate_revision'],
    'enable_flag': 'enable-093-261123-ea653e49',
    'dynamic_campaign_mod': '1.0.2 (18a2416e): hash pin moved from 1.0.1; on 261123 an adapter bridges 16 sites onto the unified map '
                            '(side colours exact; contact fading and the scene-editor timer lost; drawing frame is the game\'s equirectangular one)',
    'interoperability': 'Echidna, Ghost Shark and Better Tac Map started by SEST\'s loader as pinned BepInEx plugins (no Keel); adapters for '
                        'Enhanced Decoy, Multi-Stage Missiles, J-36 systems, Osprey Mechanics, Z-21 gun sync, Better Tac Map, Jiutian; '
                        'duplicate-assembly gate (Sensor View); R.A.T.S. Keel held by design',
    'ice_and_weather': 'one ice edge (10 %), separate floes below about 60 %, hull-contact slowing and effects, tactical-map ice layer, '
                       'mission-clock wait, polar frame from 85 degrees, regional Okhotsk/Bering/Chukchi seasons; local weather in every DCM battle',
    'verify_py': {r['name']: ('passed' if r['exit_code'] == 0 else 'FAILED') for r in cand['results']},
    'package': 'beta-support/SEST-Beta-Features.zip ' + package_sha + ' with a repair receipt of 29 earlier sets',
    'canonical_upload': f'refresh_upload_manifest.py here: {count} files match the manifest; prepare-workshop-upload.ps1 -VerifyOnly runs on the PC through Prepare-PC',
    'not_run': 'R16 has not run in the game',
    'not_for_posting': 'PC test build only; the public MNO post waits for permissions and a default-branch capture',
    'status': 'compiled-and-fixture-tested-pc-checks-pending',
}
p.write_text(json.dumps(v, indent=2) + '\n', encoding='utf-8')
print('validation.json updated:', v['revision'], count)
