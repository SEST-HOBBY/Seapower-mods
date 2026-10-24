#!/usr/bin/env python3
"""Read-only contract check for the exact Combat Cost Tracker 0.7.1 capture.

No third-party code is copied, executed, modified or shipped. The F11 extension
accepts this same SHA256 at runtime. A changed tracker requires another review.
"""
import argparse
import hashlib
from pathlib import Path
import sys
from verify_native_api import Assembly

EXPECTED = '74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3'
OVERLAY = 'WeaponCostsMod.Overlay'
METHODS = {
    (OVERLAY, 'Update'): 'instance void()',
    (OVERLAY, 'OnGUI'): 'instance void()',
    (OVERLAY, 'ContentHeight'): 'instance float(class System.Collections.Generic.List`1<class WeaponCostsMod.OverlayLine>)',
    (OVERLAY, 'Styles'): 'instance void()',
    (OVERLAY, 'Toolbar'): 'instance void(float, float, float)',
    (OVERLAY, '<OnGUI>b__24'): 'instance float(class WeaponCostsMod.ComparisonLine)',
    (OVERLAY, 'DrawComparison'): 'instance void(float, float, float, float, class System.Collections.Generic.List`1<class WeaponCostsMod.ComparisonLine>)',
    (OVERLAY, 'DrawFaction'): 'instance void(float, float, string, class System.Collections.Generic.List`1<class WeaponCostsMod.OverlayLine>, float)',
    ('WeaponCostsMod.DisplayValues', 'get_Description'): 'instance string()',
}
FIELDS = {**{n: 'bool' for n in ('ready', 'visible', 'missionActive')},
          **{n: 'float' for n in ('top', 'right', 'scale', 'opacity')},
          **{n: 'class UnityEngine.GUIStyle' for n in ('label', 'title', 'muted', 'buttonStyle')},
          'mission': 'object', 'popup': 'string', 'toggle': 'valuetype UnityEngine.KeyCode',
          'display': 'class WeaponCostsMod.DisplayValues'}


def main():
    if sys.flags.optimize:
        raise SystemExit('Run without -O / PYTHONOPTIMIZE')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assembly', type=Path)
    args = parser.parse_args()
    assert hashlib.sha256(args.assembly.read_bytes()).hexdigest() == EXPECTED, 'uninspected tracker build'
    tracker = Assembly(args.assembly)
    for (owner, name), signature in METHODS.items():
        rows = [m.row for m in tracker.typedef(owner).MethodList if str(m.row.Name) == name]
        assert len(rows) == 1 and tracker.method(rows[0])[0] == signature, (owner, name)
        assert rows[0].Rva and rows[0].ImplFlags.miIL, (owner, name, 'patchable IL body')
    for name, signature in FIELDS.items():
        assert tracker.members(OVERLAY, name, False) == [('field', OVERLAY, name, signature)], (name, signature)
    print(f'Tracker 0.7.1 contract verified: exact hash, {len(METHODS)} hook/style methods, {len(FIELDS)} fields.')
    print('No tracker code executed or distributed. Native Unity/Harmony integration requires PC acceptance.')


if __name__ == '__main__':
    main()
