// Render Steam page cards (1920x1080 JPEG) from cards.json.
//
// Each card is a darkened gallery photo with a kicker, a headline, three
// panels of four items, a two-line footer and the photo's credit. Paths in
// cards.json are relative to this folder; output goes to
// ../source/visuals/steam/, which build_patch.py copies into the pack's
// Gallery. Credit every background in ../source/VISUAL_CREDITS.txt
// (STEAM ARTWORK) and in visual_overhaul.html's Steam artwork captions.
//
//     cd integration/gallery/steam_art
//     NODE_PATH=$(npm root -g) node render.js cards.json
//
// Needs Node with Playwright and a Chromium; fonts are DejaVu Sans and
// DejaVu Sans Mono. A line that runs past its panel is printed as OVERFLOW.
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const file = path.resolve(process.argv[2] || path.join(__dirname, 'cards.json'));
const base = path.dirname(file);
const cards = JSON.parse(fs.readFileSync(file, 'utf8'));
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
function html(c) {
  const bg = 'data:image/jpeg;base64,' + fs.readFileSync(path.resolve(base, c.bg)).toString('base64');
  const cols = c.cols.map(col => `<div class="panel"><div class="lab">${esc(col.label)}</div>${
    col.items.map(([t,s]) => `<div class="it"><div class="t">${esc(t)}</div><div class="s">${esc(s)}</div></div>`).join('')}</div>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:1920px;height:1080px;overflow:hidden;font-family:'DejaVu Sans';color:#e8edf3;position:relative;background:#111}
  .bg{position:absolute;inset:0;background:url(${bg}) ${c.pos||'center'}/cover;filter:grayscale(.35)}
  .ov{position:absolute;inset:0;background:rgba(22,28,38,.84)}
  .k{position:absolute;left:110px;top:88px;font-family:'DejaVu Sans Mono';font-size:30px;letter-spacing:2px;color:#c3cad3;white-space:pre}
  .bar{position:absolute;left:110px;top:138px;width:121px;height:4px;background:#3a8fd6}
  .h{position:absolute;left:110px;top:162px;font-weight:bold;font-size:48px;letter-spacing:0}
  .cols{position:absolute;left:110px;top:320px;display:flex;gap:59px}
  .panel{width:527px;height:620px;background:rgba(8,10,15,.62);border:1px solid rgba(255,255,255,.14);padding:30px 35px}
  .lab{font-family:'DejaVu Sans Mono';font-size:26px;letter-spacing:1px;color:#4a9ad8;margin-bottom:34px}
  .it{height:126px}
  .t{font-weight:bold;font-size:31px;letter-spacing:.5px;white-space:nowrap}
  .t .new{color:#4a9ad8}
  .s{font-size:23px;letter-spacing:.5px;color:#c9d0d8;margin-top:8px;white-space:nowrap}
  .f{position:absolute;left:110px;top:964px;font-size:25px;letter-spacing:.5px;line-height:38px;color:#aab3bd}
  .cr{position:absolute;right:14px;bottom:12px;background:rgba(0,0,0,.72);padding:8px 12px;font-size:21px;letter-spacing:.5px;line-height:30px;text-align:right;color:#d8dde3}
  </style></head><body><div class="bg"></div><div class="ov"></div>
  <div class="k">${esc(c.kicker)}</div><div class="bar"></div><div class="h">${esc(c.head)}</div>
  <div class="cols">${cols}</div><div class="f">${c.foot.map(esc).join('<br>')}</div>
  <div class="cr">${c.credit.map(esc).join('<br>')}</div></body></html>`;
}
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const c of cards) {
    await p.setContent(html(c), { waitUntil: 'load' });
    const over = await p.evaluate(() => [...document.querySelectorAll('.t,.s,.h,.f')].filter(e => e.getBoundingClientRect().right > (e.closest('.panel')?.getBoundingClientRect().right ?? 1810) - (e.closest('.panel') ? 30 : 0)).map(e => e.textContent));
    if (over.length) console.log('OVERFLOW', c.out, over);
    await p.screenshot({ path: path.resolve(base, c.out), type: 'jpeg', quality: 90 });
    console.log('wrote', c.out);
  }
  await b.close();
})();
