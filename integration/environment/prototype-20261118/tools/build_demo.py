"""Build offline demo data and single-file web viewer."""
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from environment_model import build_demo

def run():
    p=argparse.ArgumentParser()
    p.add_argument('--season',choices=('winter','summer'),default='winter')
    p.add_argument('--out',default=str(ROOT/'data'/'demo_environment.json'))
    a=p.parse_args()
    data=build_demo(Path(a.out),season=a.season)
    template=(ROOT/'web'/'template.html').read_text(encoding='utf-8')
    coast=json.loads((ROOT/'data'/'coastlines.json').read_text(encoding='utf-8'))
    obs=(ROOT/'data'/'example_observations.json')
    observations=json.loads(obs.read_text(encoding='utf-8')) if obs.exists() else {'schema':'mno.env.observations.v0.1','stations':[]}
    def embed(obj): return json.dumps(obj,separators=(',',':')).replace('<','\\u003c')
    out=template.replace('__EMBEDDED_ENV__',embed(data)).replace('__EMBEDDED_COAST__',embed(coast)).replace('__EMBEDDED_OBS__',embed(observations))
    (ROOT/'web'/'MNO_GCO_ENV_VIEWER.html').write_text(out,encoding='utf-8')
    print('Written',a.out,'and',ROOT/'web'/'MNO_GCO_ENV_VIEWER.html')
if __name__=='__main__': run()
