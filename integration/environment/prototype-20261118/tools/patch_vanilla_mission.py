"""Generate a NON-DESTRUCTIVE Sea Power 0.9.x vanilla weather playtest mod.

Confirm action fields against original vanilla Breakthrough/Hormuz. This script
never edits its source file or the game's original files. Compilable INI only;
run-time behaviour requires an actual in-game test.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from environment_model import bilinear

CLOUDS = ('Clear','Scattered','Scattered_1','Scattered_2','Broken','Broken_2','Broken_3','Overcast')
WEATHER_ACTIONS = {'Action_SetSeaState','Action_SetClouds','Action_SetRain','Action_SetSnow','Action_SetThunderstorm','Action_SetFog'}
PRESET = [
    {'cloud':'Broken','sea':3,'rain':False,'fog':False,'storm':False},
    {'cloud':'Overcast','sea':5,'rain':True,'fog':False,'storm':False},
    {'cloud':'Overcast','sea':7,'rain':True,'fog':False,'storm':True},
    {'cloud':'Overcast','sea':8,'rain':True,'fog':True,'storm':True},
    {'cloud':'Broken_3','sea':7,'rain':True,'fog':True,'storm':False},
    {'cloud':'Broken_2','sea':5,'rain':True,'fog':False,'storm':False},
    {'cloud':'Scattered_2','sea':4,'rain':False,'fog':False,'storm':False},
    {'cloud':'Clear','sea':2,'rain':False,'fog':False,'storm':False},
]

def cloud_code(percent):
    if percent>=91:return 'Overcast'
    if percent>=78:return 'Broken_3'
    if percent>=66:return 'Broken_2'
    if percent>=55:return 'Broken'
    if percent>=45:return 'Scattered_2'
    if percent>=34:return 'Scattered_1'
    if percent>=22:return 'Scattered'
    return 'Clear'

def scale_sea(wave):
    # Calibration target only; Sea Power field is not a precise wave-height API.
    return max(0,min(10,round(wave/1.15+1)))

def state_from_grid(data,lat,lon,frame):
    return {'cloud':cloud_code(bilinear(data,frame,lat,lon,'cloud_pct')),
            'sea':scale_sea(bilinear(data,frame,lat,lon,'wave_m')),
            'rain':bilinear(data,frame,lat,lon,'precip_mm_h')>=0.55,
            'fog':False,
            'storm':bilinear(data,frame,lat,lon,'precip_mm_h')>=4.5}

def partition(content):
    marks=list(re.finditer(r'(?m)^\[Trigger(\d+)\][^\r\n]*',content))
    if not marks:raise ValueError('No [TriggerN] sections: cannot safely add test triggers')
    prefix=content[:marks[0].start()]
    blocks=[]
    for idx,m in enumerate(marks):
        end=marks[idx+1].start() if idx+1<len(marks) else len(content)
        blocks.append((int(m.group(1)),content[m.start():end]))
    return prefix,blocks

def section(content,name):
    m=re.search(r'(?m)^\['+re.escape(name)+r'\]\s*\r?\n',content)
    if not m:return None
    n=re.search(r'(?m)^\[[^\]\r\n]+\]',content[m.end():])
    stop=m.end()+n.start() if n else len(content)
    return m.start(),stop,content[m.start():stop]

def is_weather_only(block):
    actions=re.findall(r'(?m)^\s*(Action_\w+)\s*=',block)
    return bool(actions) and all(a in WEATHER_ACTIONS for a in actions)

def mark_disabled(block):
    if re.search(r'(?m)^Disabled\s*=\s*True',block):return block
    return re.sub(r'(?m)^(\[Trigger\d+\][^\r\n]*\r?\n)',r'\1Disabled=True\n',block,count=1)

def patch(content,states,interval=300,title='MNO Weather Lab'):
    if '[Mission]' not in content or '[Environment]' not in content:
        raise ValueError('Source is not a standard Sea Power mission INI')
    if not re.search(r'(?m)^\s*NumberOfTriggers=\d+',content):
        raise ValueError('Missing NumberOfTriggers; refusing to guess source format')
    normalized=content.replace('\r\n','\n').replace('\r','\n')
    prefix,blocks=partition(normalized)
    original_names={i for i,b in blocks}
    maxnum=max(original_names)
    # Existing only-weather triggers are disabled, not removed/renumbered.
    # Do not disable a trigger if another original trigger refers to it.
    modified=[]
    for i,b in blocks:
        refs=bool(re.search(r'(?m)^Action_(?:Enable|Reactivate|Disable)Triggers\s*=.*\bTrigger'+str(i)+r'\b',normalized))
        if is_weather_only(b) and not refs:b=mark_disabled(b)
        modified.append((i,b))
    first=states[0]
    envsec=section(prefix,'Environment')
    if not envsec:raise ValueError('Environment section not located before trigger blocks')
    a,b,s=envsec
    replacements={'SeaState':first['sea'],'Clouds':first['cloud'],'Weather':','.join(x for x,y in [('Rain',first['rain']),('Fog',first['fog']),('Thunderstorm',first['storm'])] if y)}
    for key,val in replacements.items():
        if key=='Weather' and not val:
            s=re.sub(r'(?m)^Weather\s*=.*\n?','',s)
        elif re.search(r'(?m)^'+key+r'=',s):
            # Some vanilla missions include duplicate Clouds= entries. Remove all,
            # then write one authoritative value at the bottom of Environment.
            s=re.sub(r'(?m)^'+key+r'=.*\n?', '', s)
            s=s.rstrip('\n')+f'\n{key}={val}\n'
        else:s=s.rstrip('\n')+f'\n{key}={val}\n'
    prefix=prefix[:a]+s+prefix[b:]
    # Rename only English-facing scenario fields, preserving all other languages.
    eng=section(prefix,'Language_en')
    if eng:
        a,b,s=eng
        if re.search(r'(?m)^Name=',s):s=re.sub(r'(?m)^Name=.*$',f'Name={title}',s,count=1)
        if re.search(r'(?m)^Description=',s):s=re.sub(r'(?m)^Description=.*$',
          'Description=Environmental mechanics test; scripted changing clouds, rain, fog, thunderstorms and sea state. Synthetic and accelerated for testing. The source scenario remains otherwise unchanged.',s,count=1)
        prefix=prefix[:a]+s+prefix[b:]
    original_max=int(re.search(r'(?m)^\s*NumberOfTriggers=(\d+)',prefix).group(1))
    if original_max<maxnum:raise ValueError(f'Original NumberOfTriggers={original_max} below highest Trigger{maxnum}')
    appended=[]
    for index,state in enumerate(states[1:],start=1):
        tid=maxnum+index
        actions=[f'Action_SetClouds={state["cloud"]}',f'Action_SetSeaState={state["sea"]}',
                 f'Action_SetRain={str(state["rain"])}',f'Action_SetFog={str(state["fog"])}',
                 f'Action_SetThunderstorm={str(state["storm"])}']
        appended.append(f'[Trigger{tid}]  # MNO ENV LAB scheduled weather stage {index}\nName=MNO Environmental Stage {index}\nCondition_Type=Time\nCondition_Time={interval*index}\n'+'\n'.join(actions)+'\n\n')
    # Trigger IDs must remain unique and counter updated.
    prefix=re.sub(r'(?m)^(\s*NumberOfTriggers=)\d+',lambda m:m.group(1)+str(maxnum+len(states)-1),prefix,count=1)
    result=prefix+''.join(b for _,b in modified).rstrip('\n')+'\n\n'+''.join(appended)
    ids=[int(n) for n in re.findall(r'(?m)^\[Trigger(\d+)\]',result)]
    if len(ids)!=len(set(ids)) or max(ids)!=maxnum+len(states)-1:raise AssertionError('Trigger number validation failed')
    return result, {'source_trigger_count':len(blocks),'new_trigger_count':len(states)-1,'total_number_of_triggers':max(ids),'disabled_weather_only':sum('Disabled=True' in b and is_weather_only(b) for _,b in modified)}

def main():
    parser=argparse.ArgumentParser(description='Make a standalone vanilla or R15 mission weather test without editing sources')
    parser.add_argument('--source',type=Path,required=True,help='Existing vanilla or mod scenario .ini to clone')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'examples'/'MNO-Environmental-Playtest')
    parser.add_argument('--mode',choices=('front','grid'),default='front',help='front = dramatic accelerated test; grid = weather sampled from demonstration dataset')
    parser.add_argument('--latitude',type=float,default=-54,help='Grid sample latitude; defaults to Southern Ocean demonstration cyclone')
    parser.add_argument('--longitude',type=float,default=-49)
    parser.add_argument('--interval',type=int,default=300,help='Seconds per trigger step; 300 is deliberately accelerated')
    parser.add_argument('--frames',type=int,default=8)
    args=parser.parse_args()
    if not args.source.is_file():parser.error(f'Source mission missing: {args.source}')
    if args.interval<30 or args.frames<2 or args.frames>13:parser.error('interval >= 30, 2 <= frames <= 13')
    if args.mode=='front' and args.frames>len(PRESET):parser.error('front mode supports at most eight stages')
    raw=args.source.read_text(encoding='utf-8-sig',errors='replace')
    if args.mode=='front':states=PRESET[:args.frames]
    else:
        data=json.loads((ROOT/'data'/'demo_environment.json').read_text(encoding='utf-8'))
        states=[state_from_grid(data,args.latitude,args.longitude,k) for k in range(args.frames)]
    target_name='MNO Weather Lab - '+args.source.stem
    mission,stats=patch(raw,states,args.interval,title=target_name)
    target=args.output_dir/'missions'/f'{target_name}.ini'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(mission,encoding='utf-8')
    info=args.output_dir/'_info.ini'
    if not info.exists():info.write_text('[General]\nType=Scenario\n\n[Language_en]\nName=MNO - Environmental Playtest\nDescription=Non-release test missions for Modern Naval Operations environment development.\n',encoding='utf-8')
    (args.output_dir/'PLAYTEST_META.json').write_text(json.dumps({'status':'GENERATED_UNTESTED_IN_GAME','source':str(args.source),'output':str(target),'mode':args.mode,'interval_s':args.interval,'states':states,'statistics':stats},indent=2),encoding='utf-8')
    print(json.dumps({'output':str(target),'metadata':stats,'source_unchanged':True,'game_tested':False},indent=2))
    print('Copy the entire',args.output_dir.name,'folder to Sea Power_Data/StreamingAssets/content/ (not original/).')

if __name__=='__main__':main()
