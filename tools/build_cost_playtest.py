#!/usr/bin/env python3
"""Package the exact clean cost playtest as an offline Windows Git bundle.

Run after committing and validating. The baseline defaults to the owner's
confirmed deployed ancestor; no remote/deployment ref is changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PROFILES={
    'complete-combat-costs': ('fix/complete-combat-costs-20261024','complete-combat-costs-20261024','COMPLETE COMBAT COSTS'),
    'red-line-f11': ('fix/red-line-pacing-20261024','red-line-f11-20261024','RED LINE AND F11 CUMULATIVE COMBAT COSTS'),
}


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',choices=sorted(PROFILES),default='complete-combat-costs')
    parser.add_argument('--baseline',default='e7b32f11a906418b6e1343beff31b867d8dd7557')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if git('status','--porcelain'): raise SystemExit('Commit all intended changes before packaging.')
    commit=git('rev-parse','HEAD');baseline=git('rev-parse',args.baseline)
    subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',baseline,commit],check=True)
    branch=git('symbolic-ref','HEAD')
    expected,document,title=PROFILES[args.profile]
    review=document.replace("-20261024","-review-20261024")
    if branch!='refs/heads/'+expected: raise SystemExit('Package only the isolated branch selected by --profile.')
    installed=sum(p.is_file() for p in (ROOT/'integration/dist/SEST_Integration').rglob('*'))
    output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='sest-cost-package-') as tmp:
        stage=Path(tmp);bundle=stage/('SEST-'+args.profile+'.bundle')
        subprocess.run(['git','-C',str(ROOT),'bundle','create',str(bundle),branch,'^'+baseline],check=True)
        subprocess.run(['git','-C',str(ROOT),'bundle','verify',str(bundle)],check=True)
        manifest={'format':1,'profile':args.profile,'commit':commit,'baseline':baseline,'branch':branch,'bundle':bundle.name,
                  'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'installed_files':installed,
                  'tracker_sha256':'74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3',
                  'native_acceptance':'pending; private playtest','runtime_game_sha256':'eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd'}
        (stage/'playtest-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        for source,target in [('tools/install-cost-playtest.ps1','Install-SEST-Playtest.ps1'),
                              (f'docs/playtests/{document}.md','PC-TEST-CARD.md'),
                              ('docs/combat-costs/README.md','COSTS-README.md'),
                              ('docs/combat-costs/cost-list.csv','ALL-PRICES.csv'),
                              ('docs/combat-costs/backlog-resolution.md','ORIGINAL-BACKLOG-PRICES.md'),
                              ('docs/combat-costs/handoff-20261024.md','CLAUDE-HANDOFF.md'),
                              (f'data/{review}.json','VALIDATION.json'),
                              ('integration/combat-costs/coverage-policy.json','ESTIMATE-POLICY.json')]:
            shutil.copyfile(ROOT/source,stage/target)
        with (stage/'REVIEW.patch').open('w') as f:
            subprocess.run(['git','-C',str(ROOT),'diff','--binary','374634bc',commit],stdout=f,check=True)
        (stage/'INSTALL.txt').write_text(
            'PRIVATE SEST '+title+' PLAYTEST\n\n'
            f'Commit: {commit}\nExpected IN LINE: {installed} files, {commit[:8]}\n\n'
            'Close Sea Power. Extract the ZIP, then run Install-SEST-Playtest.ps1 with -Repository pointing to your existing Seapower-mods clone.\n'
            'The installer verifies the bundle, imports the exact commit, and syncs from a temporary detached worktree. It leaves your main checkout and branch in place.\n'
            'The bundle requires the existing '+baseline[:8]+' history or a descendant. No remote pull/push or Steam upload occurs.\n'
            'After successful install, fully restart the game and follow PC-TEST-CARD.md. F11 contains This mission, Cumulative Combat Costs and Last games; cumulative/history also open from the Task Force menu.\n'
            'All 4365 resolved equipment references have prices in both modes. Estimates are labelled; gameplay acceptance remains pending.\n')
        with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(stage.iterdir()):z.write(p,p.name)
    with zipfile.ZipFile(output) as z:
        bad=z.testzip()
        if bad: raise SystemExit('ZIP CRC failed: '+bad)
    print(json.dumps({'file':str(output),'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),**manifest},indent=2))


if __name__=='__main__': main()
