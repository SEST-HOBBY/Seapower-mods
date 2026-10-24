#!/usr/bin/env python3
"""Gate complete resolved cost coverage and the exact generated catalogs."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integration'))
from common.cost_completion import build_complete,render_complete,render_config,reports


def main():
    maps=json.loads((ROOT/'integration/combat-costs/mappings.json').read_text())
    result,_=build_complete(ROOT,maps)
    generated=ROOT/'integration/combat-costs/SEST_Combat_Costs/systems'
    expected={generated/f'sest_{kind}_costs.ini':render_complete(kind,result) for kind in result['extensions']}
    expected[generated/'sest_cost_visibility.ini']=render_config(ROOT,result)
    md,table=reports(result)
    expected[ROOT/'docs/combat-costs/cost-list.md']=md
    expected[ROOT/'docs/combat-costs/cost-list.csv']=table
    expected[ROOT/'docs/combat-costs/coverage.json']=json.dumps(result,indent=2)+'\n'
    bad=[str(p.relative_to(ROOT)) for p,text in expected.items() if not p.exists() or p.read_text(encoding='utf-8')!=text]
    for path in generated.glob('*.ini'):
        installed=ROOT/'integration/dist/SEST_Integration/systems'/path.name
        if not installed.exists() or installed.read_bytes()!=path.read_bytes(): bad.append(str(installed.relative_to(ROOT)))
    if bad:
        print('Combat cost outputs stale; rebuild:',*bad,sep='\n  ')
        return 1
    total=sum(v['eligible'] for v in result['coverage'].values())
    print(f'Complete cost coverage: {total} resolved references in both modes; generated source/dist catalogs agree.')
    print(f"Preserved {result['completion']['known_fields_preserved']} usable fields; filled {sum(result['completion']['filled_fields'].values())} missing fields with labelled estimates.")
    return 0


if __name__=='__main__':
    raise SystemExit(main())
