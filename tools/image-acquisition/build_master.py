#!/usr/bin/env python3
"""Build the static manifest from the 13-14 October SEST repo/photo audit."""
import csv
import datetime
from pathlib import Path
from urllib.parse import quote
from collections import Counter

DIR=Path(__file__).resolve().parent

def rows(name):
    with (DIR/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f,delimiter='|'))

old=rows('legacy_gaps.tsv')
extra=rows('additions.tsv')
selectors={x['unit_id']:x for x in rows('curated_sources.tsv')}
assert len(old)==89 and len(extra)==27 and len(selectors)==116

legacy_meta={x['unit_id']:x for x in old}
new_meta={x['unit_id']:x for x in extra}

def priority(unit,legacy,missions):
    if unit.startswith('anduril:'):
        return 'P0 - newly installed, permissions needed'
    high={'E7A_Wedgetail','plan_type_001','plan_j-15','plan_j-15d','plan_cv_type_003','ran_opv_arafura','ir_ptg_peykaap_3','wp_buk-m3','ina_prithvi_tel','wp_ss-27_tel','pla_df-41_tel','rok_kf21','usaf_f-15ex_SEII'}
    if unit in high:return 'P1 - recognition/high value'
    if legacy:
        if int(missions)>=2:return 'P1 - fielded frequently'
        if unit in {'Coal_PowerPlant','FOB','Liberty','Oil_pump','4tentgroup','civ_humpback','airbase_us','airfield_a-10','airfield_us'}:return 'P4 - context/low priority'
        return 'P2 - fill/review'
    return 'P2 - new equipment'

def page(ref,mode):
    if not ref:return ''
    if mode=='file':return 'https://commons.wikimedia.org/wiki/'+quote(ref.replace(' ','_'),safe=':/()')
    if mode=='category':return 'https://commons.wikimedia.org/wiki/'+quote(ref.replace(' ','_'),safe=':/()')
    if mode=='search':return 'https://commons.wikimedia.org/w/index.php?search='+quote(ref)+'&title=Special:MediaSearch&type=image'
    return ''

fields=['unit_id','unit_label','origin','provider_id','was_missing','legacy_missions','priority','asset_group','acquisition_mode','source_ref','source_page','image_exactness','licence_checked_from_web','import_status','notes']
master=[]
for item in old+extra:
    uid=item['unit_id'];sel=selectors[uid];isold=uid in legacy_meta
    mode=sel['source_mode'];ref=sel['commons_ref'];
    if mode=='file':status='source_verified_web; await API check and download'
    elif mode=='category':status='category candidate; individual photo and licence need review'
    elif mode=='search':status='search candidate; photo and licence need review'
    elif mode=='reuse':status='reuse shared asset after parent is approved'
    elif mode=='permission':status='HOLD: obtain rights/authorized mod model render; no automatic download'
    else:status='HOLD: do not mislabel conceptual or unidentified hardware'
    provider=item.get('provider','') if not isold else 'see current repo mapping'
    d={
        'unit_id':uid,'unit_label':item['label'],'origin':'2026-10-13 legacy fielded-unit action list' if isold else '2026-10-14 additions / definitions to verify',
        'provider_id':provider,'was_missing':item.get('existing_state','NOT YET INVENTORIED'),
        'legacy_missions':item.get('missions',''),'priority':priority(uid,isold,item.get('missions','0')),
        'asset_group':sel['asset_group'],'acquisition_mode':mode,'source_ref':ref,
        'source_page':page(ref,mode),'image_exactness':sel['image_exactness'],
        'licence_checked_from_web':sel['verified_web_license'],'import_status':status,
        'notes':'; '.join(filter(None,[item.get('note',''),sel['note']]))
    }
    master.append(d)
master.sort(key=lambda r: (r['priority'], -(int(r['legacy_missions']) if r['legacy_missions'].isdigit() else 0),r['unit_label'].lower()))
with (DIR/'SEST_IMAGE_MASTER_20261014.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fields);w.writeheader();w.writerows(master)

# The gallery's 10 Anduril variants remain unresolved: no fabricated INI identifiers.
with (DIR/'ANDURIL_VARIANT_RECONCILIATION.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['workshop_mod','family','unit_id_from_export','variant_name_from_export','shared_asset','status'])
    for name,aid in [
        ('Dive-LD','anduril_dive_ld'),('Dive-XL','anduril_dive_xl'),('Copperhead-100','anduril_copperhead_100'),
        ('Copperhead-500','anduril_copperhead_500'),('K5 KRAKEN','anduril_k5_kraken')]:
        w.writerow(['3819522350',name,'','',aid,'Await Steam export; alias its actual variants to family image'])

with (DIR/'PINNED_VERIFIED_FILE_PAGES.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,['unit_id','unit_label','filename','source_page','web_verified_licence','asset_group'])
    w.writeheader();w.writerows([{'unit_id':r['unit_id'],'unit_label':r['unit_label'],'filename':r['source_ref'],
       'source_page':r['source_page'],'web_verified_licence':r['licence_checked_from_web'],'asset_group':r['asset_group']}
        for r in master if r['acquisition_mode']=='file'])

print('master rows',len(master),'modes',dict(Counter(r['acquisition_mode'] for r in master)))
