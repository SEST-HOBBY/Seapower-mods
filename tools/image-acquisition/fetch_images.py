#!/usr/bin/env python3
"""License-gated Wikimedia Commons acquisition for SEST Sea Power gallery.

Usage:
  py -3 fetch_images.py --mode all
  py -3 fetch_images.py --mode verified

The script NEVER installs to Sea Power or writes to GitHub. Candidate images
from categories/search are NOT automatically approved for public use.
"""
import argparse
import csv
import hashlib
import html
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
API='https://commons.wikimedia.org/w/api.php'
UA='SEST-Image-Audit/1.1 (https://github.com/SEST-HOBBY/Seapower-mods; Commons attribution audit)'

def req(url, json_output=False, attempts=4):
    last=None
    for i in range(attempts):
        try:
            request=Request(url,headers={'User-Agent':UA,'Accept':'application/json' if json_output else '*/*'})
            with urlopen(request,timeout=42) as r:
                if json_output:
                    data=r.read(9_000_000)
                    return json.loads(data.decode('utf-8-sig'))
                return r.read(35_000_001)
        except (HTTPError, URLError, TimeoutError, ValueError) as e:
            last=e
            if isinstance(e, HTTPError) and e.code in (403,404):
                break
            time.sleep(min(12,2**i))
    raise RuntimeError(f'{url}: {last}')

def mw(params):
    params={'action':'query','format':'json','formatversion':'2',**params}
    r=req(API+'?'+urlencode(params),json_output=True)
    if r.get('error'):raise RuntimeError(str(r['error']))
    return r

def read_master():
    with (ROOT/'SEST_IMAGE_MASTER_20261014.csv').open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def safe_filename(value):
    s=re.sub(r'[^a-zA-Z0-9._-]+','_',value).strip('._')
    return (s[:105] or 'image')

def license_key(s):
    s=(s or '').lower().replace('_','-')
    if 'noncommercial' in s or 'no-derivatives' in s or re.search(r'\b(by-nc|by-nd|nc-sa|nc-nd)\b',s):return 'REJECT'
    if 'cc0' in s or 'cc-zero' in s or 'creative commons zero' in s:return 'CC0'
    if 'public domain' in s or s.startswith('pd-'):return 'PD'
    if 'cc by-sa' in s or 'cc-by-sa' in s or 'attribution-sharealike' in s:return 'CC BY-SA'
    if 'cc by' in s or 'cc-by' in s or 'attribution ' in s:return 'CC BY'
    return ''

def license_version(s):
    m=re.search(r'(?<![0-9])([1-9]\.[0-9])',s or '')
    return m.group(1) if m else ''

def strip_tags(s):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',str(s or '')))).strip()

def get_imageinfo(name, width=1600):
    p=mw({'prop':'imageinfo','titles':name,'iiprop':'url|size|mime|extmetadata',
      'iiurlwidth':str(width),'iiextmetadatafilter':'LicenseShortName|LicenseUrl|Copyrighted|Artist|Credit|Attribution|ImageDescription|UsageTerms|Restrictions'})
    pages=p.get('query',{}).get('pages',[])
    if not pages or 'imageinfo' not in pages[0]:return None
    info=pages[0]['imageinfo'][0]
    ext=info.get('extmetadata',{})
    meta={k:strip_tags(v.get('value','')) for k,v in ext.items()}
    lic=meta.get('LicenseShortName','')
    accept=license_key(lic)
    copyrighted=meta.get('Copyrighted','').lower()
    if accept=='PD' and copyrighted in ('true','1'):
        accept='REJECT'
    if not accept or accept=='REJECT':return None
    if info.get('mime') not in ('image/jpeg','image/png','image/webp'):return None
    if info.get('width',0)<750 or info.get('height',0)<400:return None
    info['page_title']=pages[0].get('title',name)
    info['licence']=lic
    info['license_family']=accept
    info['meta_clean']=meta
    return info

BAD_NAME = re.compile(r'(?i)(?:\b(?:logo|flag|diagram|map|sketch|illustration|infographic|insignia|badge|drawing|screenshot|render|model|poster|coat.of.arms|schematic|sideview|side.view|silhouette|cross.section)\b|\\.svg$)')

def candidate_name_score(filename, row):
    name=filename.lower().replace('_',' ')
    if not re.search(r'\.(jpg|jpeg|png|webp)$',name):return -1_000_000
    if BAD_NAME.search(name):return -700
    label=row['unit_label'].lower()
    tokens=[x for x in re.findall('[a-z0-9]+',label) if len(x)>2 and x not in {'the','class','base','2027','2026','stand','modern','type','systems','airforce','silo','radar','ship','launch'}]
    score=0
    for t in tokens:score+=7 if t in name else 0
    for t in ('warship','ship','aircraft','photo','2024','2025','2023','frigate','destroyer','submarine','patrol','helicopter','launcher','tel'):
        if t in name:score+=1
    # Short ambiguous names: reward filenames that contain a substantial portion of the label.
    if any(t in name for t in ('exercise','at sea','sailing','in flight','airport','operation')):score+=3
    return score

def get_category_files(category, max_subcats=10):
    titles=[]; cats=[]; cont={}; pages_seen=0
    while True:
        p=mw({'list':'categorymembers','cmtitle':category,'cmtype':'file|subcat','cmlimit':'200',**cont})
        for a in p.get('query',{}).get('categorymembers',[]):
            if a.get('ns')==6:titles.append(a['title'])
            elif a.get('ns')==14:cats.append(a['title'])
        cont=p.get('continue',{})
        pages_seen+=1
        if not cont or pages_seen>=3:break
    # Only descend if direct listings scarce. Prefer exact-platform subcategories.
    if len(titles)<3:
        for sub in cats[:max_subcats]:
            try:
                part=mw({'list':'categorymembers','cmtitle':sub,'cmtype':'file','cmlimit':'100'})
                titles += [a['title'] for a in part.get('query',{}).get('categorymembers',[]) if a.get('ns')==6]
            except Exception as exc:
                print(f'  subcategory warning: {sub}: {exc}')
            if len(titles)>150:break
    return list(dict.fromkeys(titles))

def get_search_files(query):
    p=mw({'list':'search','srsearch':query,'srnamespace':'6','srlimit':'35'})
    return [x['title'] for x in p.get('query',{}).get('search',[]) if x.get('ns')==6]

def candidates(row):
    ref=row['source_ref']
    mode=row['acquisition_mode']
    if mode=='file':return [ref]
    if mode=='category':return get_category_files(ref)
    if mode=='search':return get_search_files(ref)
    return []

def choose(row,width):
    names=candidates(row)
    if not names:return None
    if row['acquisition_mode']=='file':names=names[:1]
    else:
        names=sorted(names,key=lambda n:candidate_name_score(n,row),reverse=True)[:12]
    scored=[]
    for n in names:
        if row['acquisition_mode']!='file' and candidate_name_score(n,row)<0:continue
        try:i=get_imageinfo(n,width)
        except Exception as exc:
            print(f'  license check error on {n}: {exc}')
            continue
        if not i:continue
        expected=row.get('licence_checked_from_web','')
        if expected and (license_key(expected)!=i['license_family'] or (license_version(expected) and license_version(i['licence']) and license_version(expected)!=license_version(i['licence']))):
            print(f'  LICENSE CHANGE on pinned {n}: expected {expected}, currently {i["licence"]}; SKIPPED')
            continue
        score=candidate_name_score(n,row)+min(i.get('width',0)/300,20)
        if i.get('width',0)/max(1,i.get('height',1))>1.15:score+=4
        if row['acquisition_mode']=='category':score+=40
        if row['acquisition_mode']=='file':score+=1000
        scored.append((score,i))
    if not scored:return None
    scored.sort(key=lambda x:x[0],reverse=True)
    return scored[0][1]

def build_page(title):
    return 'https://commons.wikimedia.org/wiki/'+quote(title.replace(' ','_'),safe=':/()')

def attr_author(meta):
    return meta.get('Attribution') or meta.get('Artist') or meta.get('Credit') or '(see source page)'

def write_csv(path,rows,cols):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)

def build_html(asset_rows):
    cards=[]
    for d in sorted(asset_rows,key=lambda a:(a.get('review_state',''),a.get('asset_group',''))):
        label=html.escape(d['unit_labels']);f=html.escape(d['local_file']);lic=html.escape(d['licence'])
        page=html.escape(d['source_page'],quote=True);caption=html.escape(d['source_file_title'])
        review=html.escape(d['review_state']);group=html.escape(d['asset_group'])
        cards.append(f'<article><a href="{page}" target="_blank"><img loading="lazy" src="{f}" alt="{label}"></a><p><b>{label}</b></p><p><code>{group}</code> · {review}</p><p>{caption}</p><p>{lic}</p></article>')
    doc='''<!doctype html><html lang="en"><meta charset="utf-8"><title>SEST · Gallery candidate image contact sheet</title>
<style>body{font:15px system-ui,sans-serif;background:#0d1520;color:#e7eaf0;margin:24px}h1{font-size:26px}
section{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:18px}article{background:#18293a;padding:12px;border:1px solid #2f4355;border-radius:7px}
img{height:200px;width:100%;object-fit:contain;background:#091019}p{margin:8px 0;line-height:1.35;overflow-wrap:anywhere}code{color:#91ddfa}a{color:#91ddfa}</style>
<h1>SEST · Image candidates (review required)</h1>
<p>Every card links to its Wikimedia Commons source. Category/search results are NOT approved until the depicted subject and individual licence are checked. Nothing is installed in Sea Power.</p>
<section>'''+''.join(cards)+'</section></html>'
    (ROOT/'CONTACT_SHEET.html').write_text(doc,encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=['verified','categories','all'],default='all',help='verified=pinned File pages only; categories=+Commons classes; all=+search candidates (default)')
    ap.add_argument('--width',type=int,default=1600,help='max media width (default 1600)')
    ap.add_argument('--limit',type=int,default=0,help='limit unique groups for testing')
    ap.add_argument('--list-only',action='store_true',help='show acquisition groups without network access')
    args=ap.parse_args()
    master=read_master()
    groups=defaultdict(list)
    for r in master:groups[r['asset_group']].append(r)
    # Prefer pinned candidates for a family if several unit mappings share it.
    precedence={'file':0,'category':1,'search':2,'permission':3,'hold':4,'reuse':5}
    targets=sorted((sorted(rows,key=lambda r:precedence[r['acquisition_mode']])[0] for rows in groups.values()),
        key=lambda r: (r['priority'],r['asset_group']))
    print(f'{len(master)} unit records, {len(targets)} distinct asset groups. Modes:', dict(Counter(x['acquisition_mode'] for x in targets)))
    if args.list_only:
        for i,r in enumerate(targets):print(f'{i+1:3} {r["asset_group"]:28} {r["acquisition_mode"]:10} {r["source_ref"][:80]}')
        return
    selected=[];pending=[]
    for ix,r in enumerate(targets,1):
        if args.limit and ix>args.limit:break
        group=r['asset_group'];mode=r['acquisition_mode']
        if mode in ('reuse','permission','hold'):
            pending.append({'asset_group':group,'status':r['import_status'],'reason':r['notes'],'unit_ids':'; '.join(x['unit_id'] for x in groups[group])})
            continue
        if mode=='category' and args.mode=='verified':continue
        if mode=='search' and args.mode!='all':continue
        print(f'[{ix}/{len(targets)}] {group} ({mode})',flush=True)
        try:
            info=choose(r,args.width)
            if not info:raise ValueError('No acceptable real, sufficiently sized licensed image was found')
            folder=ROOT/'downloaded' / ('verified_file_pages' if mode=='file' else 'REVIEW_REQUIRED')
            folder.mkdir(parents=True,exist_ok=True)
            url=info.get('thumburl') or info['url']
            ext={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}[info['mime']]
            local=folder/(safe_filename(group)+ext)
            if not local.is_file():
                data=req(url)
                if len(data)>35_000_000:raise RuntimeError('Oversize download refused')
                magic=(data.startswith(b'\xff\xd8') or data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'RIFF'))
                if not magic:raise RuntimeError('Downloaded content is not a supported image')
                local.write_bytes(data)
            else:data=local.read_bytes()
            meta=info['meta_clean'];title=info['page_title'];sourcepage=build_page(title)
            labels='; '.join(x['unit_label'] for x in groups[group])
            d={'asset_group':group,'unit_ids':'; '.join(x['unit_id'] for x in groups[group]),'unit_labels':labels,
              'local_file':str(local.relative_to(ROOT)).replace('\\','/'),
              'review_state':'PINNED SOURCE - visual review' if mode=='file' else 'CANDIDATE - manual identity review REQUIRED',
              'image_exactness_claim':r['image_exactness'],'source_file_title':title,'source_page':sourcepage,
              'direct_url':info['url'],'downloaded_url':url,
              'width':info.get('width',''),'height':info.get('height',''),'mime':info['mime'],
              'licence':info['licence'],'licence_url':meta.get('LicenseUrl',''),
              'author':attr_author(meta),'description':meta.get('ImageDescription',''),
              'sha256':hashlib.sha256(data).hexdigest(),
              'changes':'resized by Wikimedia Commons thumbnail service' if info.get('thumburl') else 'unmodified original',
              'date_checked':time.strftime('%Y-%m-%d'),
              'source_mode':mode}
            selected.append(d)
            print(f'  -> {local.name} {len(data):,} bytes · {info["licence"]}')
            time.sleep(0.15)
        except Exception as e:
            print(f'  SKIPPED {e}')
            pending.append({'asset_group':group,'status':'FAILED / review required','reason':str(e),'unit_ids':'; '.join(x['unit_id'] for x in groups[group])})
    cols=['asset_group','unit_ids','unit_labels','local_file','review_state','image_exactness_claim','source_file_title',
          'source_page','direct_url','downloaded_url','width','height','mime','licence','licence_url','author','description','sha256','changes','date_checked','source_mode']
    write_csv(ROOT/'ACQUIRED_IMAGES.csv',selected,cols)
    write_csv(ROOT/'PENDING_IMAGES.csv',pending,['asset_group','unit_ids','status','reason'])
    credits=['# SEST image candidates — source and licence record','',
        'Every licence applies to that image, not to the SEST game or to the entire pack.',
        'All class/search-selected photographs require manual identity and source review.',
        'No endorsement by authors, the armed forces, or Wikimedia is implied.','']
    for r in selected:
        credits.extend([f'## {r["asset_group"]} — {r["unit_labels"]}',
           f'- Source: {r["source_page"]}',f'- File: {r["source_file_title"]}',
           f'- Author/credit: {r["author"]}',f'- Licence: {r["licence"]} ({r["licence_url"]})',
           f'- Change: {r["changes"]}',f'- SHA-256: `{r["sha256"]}`',
           f'- Review: {r["review_state"]}',''])
    (ROOT/'ATTRIBUTION_CANDIDATES.md').write_text('\n'.join(credits),encoding='utf-8')
    build_html(selected)
    print('RESULT: images',len(selected),'pending',len(pending),'see CONTACT_SHEET.html and ACQUIRED_IMAGES.csv')
    print('Nothing was installed or published. Reviewed images only should be imported to SEST.')

if __name__=='__main__':
    main()
