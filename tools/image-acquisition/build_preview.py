#!/usr/bin/env python3
import csv,html,json
from pathlib import Path
from urllib.parse import quote
R=Path(__file__).resolve().parent
with (R/'SEST_IMAGE_MASTER_20261014.csv').open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))

cats={
'file':('Verified Commons file','Exact source file page inspected; image still needs downloading and visual review.'),
'category':('Commons category','Photo selected later from a real platform category; individual file licence still needs validation.'),
'search':('Commons search','Only a search queue, not a verified exact image.'),
'hold':('Image on hold','No safely supportable exact photograph selected.'),
'permission':('Permission required','Anduril product or mod render rights must be cleared before publication.'),
'reuse':('Reuse existing asset','Shares an approved image with the parent platform; no duplicate required.'),
}
items=[]
for r in rows:
    mode=r['acquisition_mode']; unit=html.escape(r['unit_label']);uid=html.escape(r['unit_id']);
    source=r['source_page']
    photo=''
    if mode=='file':
        direct='https://commons.wikimedia.org/wiki/Special:FilePath/'+quote(r['source_ref'].replace(' ','_'),safe=':/()')+'?width=640'
        photo=f'<img loading="lazy" src="{html.escape(direct,quote=True)}" alt="{unit} candidate" onerror="this.style.display=\'none\'">'
    if not photo:photo='<div class="noimg">SOURCE CANDIDATE</div>'
    tag=html.escape(cats[mode][0]);lic=html.escape(r['licence_checked_from_web'] or 'Licence to verify when selected')
    label=html.escape(r['image_exactness']); provider=html.escape(r['provider_id'])
    link=f'<a target="_blank" href="{html.escape(source,quote=True)}">View source</a>' if source else '<span class="faint">Not cleared</span>'
    items.append(f'''<article data-query="{html.escape((r["unit_label"]+" "+r["unit_id"]+" "+r["source_ref"]).lower(),quote=True)}" data-mode="{mode}" data-priority="{r["priority"][0:2]}">
      <div class="photo">{photo}</div><div class="details"><div class="mode">{tag} · {html.escape(r["priority"])}</div>
      <h3>{unit}</h3><code>{uid}</code><p>{label} · <span class="faint">{provider}</span></p><p>{lic}</p>
      <p class="note">{html.escape(r["notes"][:190])}</p>{link}</div></article>''')

markup='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SEST · Media Acquisition Master 2026-10-14</title>
<style>
:root{color-scheme:dark}body{background:#0a121d;color:#e8eff7;font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0}header{padding:34px max(4vw,22px);border-bottom:1px solid #243c50;background:linear-gradient(135deg,#172939,#101721)}
h1{font-weight:600;font-size:28px;margin:3px 0 10px}header p{line-height:1.5;color:#b9c8d7;max-width:1060px;font-size:14px}.stats{color:#92d7eb;font-size:15px}.toolbar{padding:18px max(4vw,22px);display:flex;flex-wrap:wrap;gap:10px;position:sticky;top:0;background:#0c1724f5;z-index:2;border-bottom:1px solid #294154}
input,select{background:#1a2c3e;border:1px solid #426176;color:#fff;padding:12px 14px;border-radius:6px}input{min-width:260px;flex:1}.grid{padding:20px max(4vw,22px);display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px}
article{background:#162637;border:1px solid #2b485f;border-radius:7px;overflow:hidden}.photo{height:177px;background:#101e2a;display:flex;align-items:center;justify-content:center}.photo img{width:100%;height:100%;object-fit:contain}.noimg{font-size:12px;letter-spacing:.11em;color:#637e91}
.details{padding:15px}.mode{font-size:11px;letter-spacing:.02em;color:#82bcd9;margin-bottom:10px}.details h3{font-size:16px;font-weight:600;margin:0 0 7px}.details code{color:#9ebfd0}.details p{font-size:12px;line-height:1.4;margin:9px 0}.note{color:#bdcbd6}.faint{color:#8b9eaf}a{color:#8dd5f1;font-size:13px}footer{padding:18px max(4vw,22px);color:#97a8b8;border-top:1px solid #2b4659;font-size:13px}
</style></head><body>
<header><div class="stats">SEST / SEA POWER / IMAGE AUDIT / 14 OCT 2026</div><h1>Master image acquisition list</h1>
<p><b>116 unit-image mapping actions:</b> 89 legacy missing/weak records and 27 October additions, including five Anduril media families. Source-file thumbnails are remote previews, not files saved into this package. All category/search entries need an image selection and licence review; no AI imagery is included.</p>
<p><b>Use the downloader</b> in this pack to acquire image files and produce a local contact sheet and credits. Anduril media require explicit permission for redistribution, and the new mod's exact internal variant IDs must come from a new export.</p></header>
<div class="toolbar"><input id="q" placeholder="Search unit, ID, aircraft, ship, weapon..." aria-label="Search units">
<select id="mode"><option value="">All source states</option>'''+''.join(f'<option value="{m}">{html.escape(v[0])}</option>' for m,v in cats.items())+'''</select>
<select id="priority"><option value="">All priorities</option><option>P0</option><option>P1</option><option>P2</option><option>P4</option></select>
<span id="count" style="align-self:center"></span></div><main class="grid" id="cards">'''+''.join(items)+'''</main>
<footer>Candidate image pages are independently licensed by their creators; this index does not transfer rights or mean the candidate depicts a unit exactly. Public domain status for a country may not apply worldwide. Keep attribution and copyright notes.</footer>
<script>const q=document.getElementById('q'),m=document.getElementById('mode'),p=document.getElementById('priority'),cards=[...document.querySelectorAll('article')],n=document.getElementById('count');
function f(){let count=0;for(const x of cards){const yes=x.dataset.query.includes(q.value.toLowerCase())&&(!m.value||x.dataset.mode===m.value)&&(!p.value||x.dataset.priority===p.value);x.hidden=!yes;if(yes)count++}n.textContent=count+' entries'}[q,m,p].forEach(x=>x.addEventListener('input',f));f();</script></body></html>'''
(R/'IMAGE_SOURCING_INDEX.html').write_text(markup,encoding='utf-8')
print('Created source browser:',len(rows),'cards')
