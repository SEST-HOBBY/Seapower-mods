'use strict';
const D=window.CATALOGUE;
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const byId=Object.fromEntries(D.assets.map(a=>[a.asset_id,a]));
const titleStatus=s=>s.replaceAll('_',' ');
const modToken=m=>m.id==='3812461539'?'SEST_Integration':m.id;
const entryMods=e=>e.providers||[e.winning_source];
const mappedByAsset=Object.fromEntries(D.assets.map(a=>[a.asset_id,[...D.entries,...D.systems].filter(e=>e.asset_id===a.asset_id)]));
let view='photos',page=0;const size=48;
$('#stats').innerHTML=[[D.assets.length,'photo assets'],[D.mods.length,'collection mods'],[D.entries.length,'source unit/config records'],[D.summary.definitions_with_candidate_photo,'candidate photo mappings']].map(([n,l])=>`<div class="stat"><strong>${n.toLocaleString()}</strong><span>${l}</span></div>`).join('');
const categories=[...new Set([...D.assets,...D.entries].map(x=>x.category))].sort();
$('#category').innerHTML+=[...categories].map(x=>`<option>${esc(x)}</option>`).join('');
$('#mod').innerHTML+=D.mods.slice().sort((a,b)=>a.title.localeCompare(b.title)).map(m=>`<option value="${esc(modToken(m))}">${esc(m.title)}</option>`).join('');
const input=()=>({q:$('#search').value.toLowerCase().trim(),cat:$('#category').value,mod:$('#mod').value,status:(view==='mods'||view==='systems')?'':$('#status').value});
function entryFilter(e,f){
 if(f.status==='quality'&&!['P1','P2'].includes(byId[e.asset_id]?.quality_review?.priority))return false;
 if(f.cat&&e.category!==f.cat)return false;
 if(f.mod&&!entryMods(e).includes(f.mod))return false;
 if(f.q&&![e.label,e.unit_id,e.mod_title,e.category,e.mapping_status].join(' ').toLowerCase().includes(f.q))return false;
 if(f.status==='mapped'&&!e.asset_id)return false;
 if(f.status==='missing'&&(e.asset_id||e.mapping_status==='non_gallery_config'))return false;
 if(f.status==='future'&&!/concept|upgrade|prototype/.test(e.mapping_status))return false;
 if(f.status==='context'&&!/context|system_reference|weapon_reference/.test(e.mapping_status))return false;
 return true;
}
function photoFilter(a,f){
 if(f.status==='quality'&&!['P1','P2'].includes(a.quality_review?.priority))return false;
 const entries=mappedByAsset[a.asset_id]||[];
 if(f.cat&&a.category!==f.cat)return false;
 if(f.mod&&!entries.some(e=>entryMods(e).includes(f.mod)))return false;
 if(f.q&&![a.label,a.asset_id,a.creator,a.license,...entries.map(e=>e.unit_id+' '+e.mod_title)].join(' ').toLowerCase().includes(f.q))return false;
 if(f.status==='missing')return false;
 if(f.status==='future'&&!entries.some(e=>/concept|upgrade|prototype/.test(e.mapping_status))&&a.reference_type!=='prototype_reference')return false;
 if(f.status==='context'&&!entries.some(e=>/context|system_reference|weapon_reference/.test(e.mapping_status)))return false;
 return true;
}
function openPhoto(id,entryId){
 const a=byId[id];if(!a)return;
 const e=entryId?[...D.entries,...D.systems].find(e=>e.entry_id===entryId):null;
 $('#modalTitle').textContent=e?.label||a.label;
 const variants=mappedByAsset[id]||[];
 $('#modalContent').innerHTML=`<img class="hero" src="${esc(a.file)}" alt="${esc(a.label)}"><div class="detail"><span class="tag">${esc(a.category)} · ${a.width} × ${a.height}</span>${e?`<p><code>${esc(e.unit_id)}</code> · ${esc(titleStatus(e.mapping_status))}</p><p><strong>Mapping:</strong> ${esc(e.mapping_note)}</p>`:''}<p><strong>Screening:</strong> photo quality ${esc(a.quality_review?.quality_grade)} · subject visibility ${esc(a.quality_review?.subject_visibility_grade)} · ${esc(a.quality_review?.priority)}.</p><p>${esc(a.quality_review?.reason)}</p><p><strong>Suggested action:</strong> ${esc(a.quality_review?.replacement_brief)}</p><p><strong>Reference:</strong> ${esc(a.reference_note)}</p><p><strong>Source caption:</strong> ${esc(a.photo_description)}</p><p><strong>Creator:</strong> ${esc(a.creator)}</p><p><strong>Licence:</strong> ${esc(a.license)} · <strong>Photo date:</strong> ${esc(a.photo_date||'See source')}</p><div class="links"><a href="${esc(a.file)}" target="_blank" rel="noopener">Open clean image</a><a href="${esc(a.source_page)}" target="_blank" rel="noopener">Source & licence record</a><a href="${esc(a.license_url||a.source_page)}" target="_blank" rel="noopener">Licence terms</a></div><p class="source">${esc(a.credit_line)}<br>${esc(a.modifications)}</p><h3>${variants.length} candidate record mappings</h3><div class="variants">${variants.length?variants.map(e=>`<div class="variant"><strong>${esc(e.label)}</strong><br><code>${esc(e.unit_id)}</code> · ${esc(titleStatus(e.mapping_status))}<br><span class="source">${esc(e.mod_title)}</span></div>`).join(''):'Additional subject reference; no matching exported unit ID was assigned.'}</div></div>`;
 $('#detail').showModal();
}
function render(){
 const f=input();let list=[];
 if(view==='photos')list=D.assets.filter(a=>photoFilter(a,f));
 if(view==='units')list=D.entries.filter(e=>entryFilter(e,f));
 if(view==='systems')list=D.systems.filter(e=>entryFilter(e,f));
 if(view==='mods')list=D.mods.filter(m=>(!f.mod||modToken(m)===f.mod)&&(!f.q||[m.title,m.id].join(' ').toLowerCase().includes(f.q))&&(!f.cat||m.categories[f.cat]));
 const pages=Math.max(1,Math.ceil(list.length/size));page=Math.min(page,pages-1);const slice=list.slice(page*size,(page+1)*size);
 $('#count').textContent=`${list.length.toLocaleString()} ${view==='photos'?'photos':view==='mods'?'collection mods':'records'} · page ${page+1} of ${pages}`;
 const notes={photos:'Open a photo to read its source caption and see the candidate unit mappings. Family photographs can represent several variants; they do not verify unseen upgrades or exact game models.',units:'Every unit and configuration record is indexed, including attachments and fixtures. When several mods ship the same unit, each copy is listed, and the card says which copy the game loads. The image status separates exact photos, family photos, context references and gaps.',mods:'All 190 Workshop mods in the collection and the SEST Integration Pack are indexed. Counts are per-source records and overlap across mods; the winner count is how many of a mod\'s records the game actually loads under the collection\'s load order. Photo coverage is partial.',systems:'Weapon-mount and sensor sections from all 190 Workshop mods. Many are modes, aliases or internal systems rather than separate hardware.'};
 $('#viewnote').textContent=notes[view];
 if(!slice.length)$('#content').innerHTML='<div class="empty">No records match these filters. Reset filters or use the Unit index to inspect missing images.</div>';
 else if(view==='photos')$('#content').innerHTML='<div class="grid">'+slice.map(a=>`<article class="card"><button class="photo" data-photo="${esc(a.asset_id)}" aria-label="View ${esc(a.label)}"><img loading="lazy" src="${esc(a.file)}" alt="${esc(a.label)}"></button><div class="body"><span class="tag">${esc(a.category)}</span><h2>${esc(a.label)}</h2><div class="badges"><span>Quality ${esc(a.quality_review?.quality_grade)} · Subject ${esc(a.quality_review?.subject_visibility_grade)} · ${esc(a.quality_review?.priority)}</span><span>${esc(a.license)}</span><span>${(mappedByAsset[a.asset_id]||[]).length} record references</span></div><p>${esc(a.reference_note)}</p><button class="open" data-photo="${esc(a.asset_id)}">Photo & mappings</button></div></article>`).join('')+'</div>';
 else if(view==='units')$('#content').innerHTML='<div class="grid">'+slice.map(e=>`<article class="card">${e.asset_id?`<button class="photo" data-photo="${esc(e.asset_id)}" data-entry="${esc(e.entry_id)}" aria-label="View ${esc(e.label)}"><img loading="lazy" src="${esc(e.image_file)}" alt="${esc(byId[e.asset_id].label)}"></button>`:`<div class="missing">${e.mapping_status==='photo_gap'?'Photo still needed':'Configuration / equipment record'}</div>`}<div class="body"><span class="tag">${esc(e.category)}</span><h2>${esc(e.label)}</h2><div class="id">${esc(e.unit_id)}</div><p><strong>${esc(titleStatus(e.mapping_status))}</strong></p><p>${esc(e.mapping_note)}</p><p>${esc(e.mod_title)}</p>${e.is_winning_copy?'<p><strong>Loaded in game</strong></p>':`<p>Overridden: the game loads ${esc(e.winning_source)}</p>`}${e.asset_id?`<button class="open" data-photo="${esc(e.asset_id)}" data-entry="${esc(e.entry_id)}">Inspect reference</button>`:''}</div></article>`).join('')+'</div>';
 else if(view==='mods')$('#content').innerHTML='<div class="grid">'+slice.map(m=>`<article class="card"><div class="body"><span class="tag">Workshop ${esc(m.id)}</span><h2>${esc(m.title)}</h2><div class="countbar"><i style="width:${m.definition_count?Math.round(100*m.photo_mapped_definitions/m.definition_count):0}%"></i></div><p><strong>${m.photo_mapped_definitions} / ${m.definition_count}</strong> supplied definitions with photo references</p><p>${m.winning_definition_count} of these are the copy the game loads · ${m.system_count} exported system sections</p><p>${esc(m.scope_note)}</p><p>${esc(Object.entries(m.categories).map(([k,n])=>k+': '+n).join(' · '))}</p><button class="open" data-mod="${esc(modToken(m))}">Browse entries</button> <a href="${esc(m.url)}" target="_blank" rel="noopener">Workshop</a></div></article>`).join('')+'</div>';
 else $('#content').innerHTML='<div class="tablewrap"><table><thead><tr><th>Hardware reference</th><th>System ID</th><th>Type</th><th>Source mod</th><th>Image status</th></tr></thead><tbody>'+slice.map(e=>`<tr><td>${e.asset_id?`<button class="photo" style="width:100px;height:70px" data-photo="${esc(e.asset_id)}" data-entry="${esc(e.entry_id)}"><img loading="lazy" src="${esc(e.image_file)}" alt="${esc(byId[e.asset_id].label)}"></button>`:"—"}</td><td class="code">${esc(e.unit_id)}</td><td>${esc(e.system_type)}</td><td>${esc(e.mod_title)}</td><td>${esc(e.mapping_note)}</td></tr>`).join('')+'</tbody></table></div>';
 $('#paging').innerHTML=`<button id="prev" ${page===0?'disabled':''}>Previous</button><span>${page+1} / ${pages}</span><button id="next" ${page===pages-1?'disabled':''}>Next</button>`;
 $('#prev').onclick=()=>{page--;render();window.scrollTo({top:300,behavior:'smooth'})};$('#next').onclick=()=>{page++;render();window.scrollTo({top:300,behavior:'smooth'})};
 document.querySelectorAll('[data-photo]').forEach(b=>b.onclick=()=>openPhoto(b.dataset.photo,b.dataset.entry));
 document.querySelectorAll('[data-mod]').forEach(b=>b.onclick=()=>{$('#mod').value=b.dataset.mod;$('#search').value='';setView('units')});
}
function setView(v){view=v;page=0;document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b.dataset.view===v));$('#status').disabled=v==='mods'||v==='systems';render()}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>setView(b.dataset.view));
for(const name of ['search','category','mod','status'])$('#'+name).addEventListener(name==='search'?'input':'change',()=>{page=0;render()});
$('#reset').onclick=()=>{for(const s of ['search','category','mod','status'])$('#'+s).value='';page=0;render()};
$('#close').onclick=()=>$('#detail').close();$('#detail').addEventListener('click',e=>{if(e.target===$('#detail'))$('#detail').close()});
render();
