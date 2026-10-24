// Render the Steam page images from cards.json.
//
// Every card names its photo ("bg"), its output ("out") and its photo
// credit ("credit"); paths are relative to this folder, and output goes to
// ../source/visuals/steam/, which build_patch.py copies into the pack's
// Gallery. Credit every photo in ../source/VISUAL_CREDITS.txt (STEAM
// ARTWORK) and in visual_overhaul.html's Steam artwork captions.
//
// "layout" picks the design (1920x1080 JPEG unless noted):
//   cols        (the default) a darkened photo, kicker, headline, three
//               panels of four items, a footer.
//   steps       the same with one panel of numbered steps (or set "steps").
//   campaign    a campaign card: a dark left panel fading into the photo,
//               which starts at x = "photoX"; kicker, title, subtitle, meta
//               line, description (3 lines at most), counts (2 at most; "\n"
//               breaks the line), then the in-game campaign map ("map") with
//               its label and a note; the map moves down when the counts
//               take two lines. The map inset is the campaign screen's
//               backdrop, ../../dist/SEST_Integration/campaigns/<id>/art/
//               00_campaign_background.png, as a straight downscale to
//               520x292: rebuild the pack first so it is current.
//   cover       1024x1024: the photo under a gradient, a big title, an
//               optional second title, a mono line and a stats line; the
//               credit sits top right. "vars" overrides sizes and positions
//               (the CSS custom properties on .cv below).
//   collection  the collection background: the SEST wordmark, a mono title,
//               a subtitle, stats, four campaign tiles (photo, name, meta,
//               count; "pos" and "size" crop a tile's photo) and an install
//               line over the blurred, darkened photo; the credit lines last.
//
//     cd integration/gallery/steam_art
//     NODE_PATH=$(npm root -g) node render.js cards.json
//
// Needs Node with Playwright and a Chromium; fonts are DejaVu Sans and
// DejaVu Sans Mono. A line that runs past its box, or a block that wraps to
// more lines than it may, is printed as OVERFLOW.
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const file = path.resolve(process.argv[2] || path.join(__dirname, 'cards.json'));
const base = path.dirname(file);
const cards = JSON.parse(fs.readFileSync(file, 'utf8'));
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const uri = f => `data:image/${/\.png$/i.test(f) ? 'png' : 'jpeg'};base64,` + fs.readFileSync(path.resolve(base, f)).toString('base64');
const layoutOf = c => c.layout || (c.steps ? 'steps' : 'cols');
const sizeOf = c => layoutOf(c) === 'cover' ? [1024, 1024] : [1920, 1080];
// The palette every layout shares.
const TOKENS = `:root{--ink:#e8edf3;--kick:#c3cad3;--bar:#3a8fd6;--lab:#4a9ad8;--sub:#c9d0d8;--foot:#aab3bd;--cred:#d8dde3;
  --panel:rgba(8,10,15,.62);--night:#090c11;--sky:#9ccaeb;--dim:#7f8994;--bar2:#478ebf;--box:rgba(7,8,12,.98)}`;
// The campaign card's fade: solid night to x=660, the photo fully shown from
// x=960, the photo's share rising as t^1.4 in between.
const FADE = 'linear-gradient(90deg,var(--night) 660px,' + Array.from({ length: 11 }, (_, i) =>
  `rgba(9,12,17,${+(1 - Math.pow(i / 10, 1.4)).toFixed(3)}) ${660 + 30 * i}px`).join(',') + ')';

function colsSteps(c) {
  const bg = uri(c.bg);
  const body = c.steps
    ? `<div class="steps">${c.steps.map(([t,s], i) => `<div class="st" style="top:${25 + i * 150}px"><div class="num">${i + 1}</div><div><div class="t">${esc(t)}</div><div class="s">${esc(s)}</div></div></div>`).join('')}</div>`
    : `<div class="cols">${c.cols.map(col => `<div class="panel"><div class="lab">${esc(col.label)}</div>${
        col.items.map(([t,s]) => `<div class="it"><div class="t">${esc(t)}</div><div class="s">${esc(s)}</div></div>`).join('')}</div>`).join('')}</div>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>${TOKENS}
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:1920px;height:1080px;overflow:hidden;font-family:'DejaVu Sans';color:var(--ink);position:relative;background:#111}
  .bg{position:absolute;inset:0;background:url(${bg}) ${c.pos||'center'}/cover;filter:grayscale(.35)}
  .ov{position:absolute;inset:0;background:rgba(22,28,38,.84)}
  .k{position:absolute;left:110px;top:88px;font-family:'DejaVu Sans Mono';font-size:30px;letter-spacing:2px;color:var(--kick);white-space:pre}
  .bar{position:absolute;left:110px;top:138px;width:121px;height:4px;background:var(--bar)}
  .h{position:absolute;left:110px;top:162px;font-weight:bold;font-size:48px;letter-spacing:0}
  .cols{position:absolute;left:110px;top:320px;display:flex;gap:59px}
  .panel{width:527px;height:620px;background:var(--panel);border:1px solid rgba(255,255,255,.14);padding:30px 35px}
  .lab{font-family:'DejaVu Sans Mono';font-size:26px;letter-spacing:1px;color:var(--lab);margin-bottom:34px}
  .it{height:126px}
  .t{font-weight:bold;font-size:31px;letter-spacing:.5px;white-space:nowrap}
  .t .new{color:var(--lab)}
  .s{font-size:23px;letter-spacing:.5px;color:var(--sub);margin-top:8px;white-space:nowrap}
  .f{position:absolute;left:110px;top:964px;font-size:25px;letter-spacing:.5px;line-height:38px;color:var(--foot)}
  .steps{position:absolute;left:80px;top:280px;width:1760px;height:625px;background:var(--panel)}
  .st{position:absolute;left:30px;height:90px;display:flex;align-items:center}
  .num{width:90px;height:90px;flex:none;margin-right:50px;border:3px solid var(--bar);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:44px}
  .st .t{font-size:38px}
  .st .s{font-size:25px;margin-top:6px}
  .cr{position:absolute;right:14px;bottom:12px;background:rgba(0,0,0,.72);padding:8px 12px;font-size:21px;letter-spacing:.5px;line-height:30px;text-align:right;color:var(--cred)}
  </style></head><body><div class="bg"></div><div class="ov"></div>
  <div class="k">${esc(c.kicker)}</div><div class="bar"></div><div class="h">${esc(c.head)}</div>
  ${body}<div class="f"${c.footTop ? ` style="top:${c.footTop}px"` : ''}>${c.foot.map(esc).join('<br>')}</div>
  <div class="cr">${c.credit.map(esc).join('<br>')}</div></body></html>`;
}

// Shared by the campaign, cover and collection layouts. data-r is the
// furthest right a line may reach, data-lines the most lines a block may
// wrap to, data-b the lowest its bottom may sit.
const HEAD = (c, w, h, css) => `<!doctype html><html><head><meta charset="utf-8"><style>${TOKENS}
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:${w}px;height:${h}px;overflow:hidden;font-family:'DejaVu Sans';color:var(--ink);position:relative;background:var(--night)}
  .mono{font-family:'DejaVu Sans Mono'}
  .one{white-space:pre}
  .ccr{position:absolute;background:var(--box);padding:4px 12px 5px;font-size:21px;letter-spacing:.5px;line-height:30px;text-align:right;color:var(--cred);white-space:pre}
  ${css}</style></head><body${c.vars ? ` style="${Object.entries(c.vars).map(([k, v]) => `${k}:${v}`).join(';')}"` : ''}>`;
const credit = (c, where) => `<div class="ccr" style="${where}">${c.credit.map(esc).join('<br>')}</div>`;

function campaign(c) {
  return HEAD(c, 1920, 1080, `
  .cbg{position:absolute;top:0;bottom:0;right:0;left:${c.photoX ?? 660}px;background:url(${uri(c.bg)}) ${c.pos || 'left center'}/cover}
  .cfade{position:absolute;inset:0;background:${FADE}}
  .ck{position:absolute;left:100px;top:163px;font-size:24px;line-height:24px;color:var(--foot)}
  .cbar{position:absolute;left:100px;top:201px;width:101px;height:4px;background:var(--bar2)}
  .ct{position:absolute;left:100px;top:234px;font-weight:bold;font-size:64px;line-height:64px;color:var(--ink)}
  .cs{position:absolute;left:100px;top:314px;font-size:36px;line-height:36px;color:var(--sky)}
  .cm{position:absolute;left:100px;top:373px;font-size:22px;line-height:22px;color:var(--foot)}
  .cflow{position:absolute;left:100px;top:427px;width:760px}
  .ctext{min-height:196px;padding-bottom:28px}
  .cd{font-size:26px;line-height:38px;color:var(--sub)}
  .cc{margin-top:24px;font-size:22px;line-height:30px;color:var(--foot);white-space:pre-line}
  .cml{font-size:22px;line-height:22px;color:var(--ink)}
  .cmap{display:block;margin-top:14px;width:522px;height:294px;border:1px solid rgba(255,255,255,.25)}
  .cn{margin-top:22px;font-size:24px;line-height:24px;color:var(--foot)}`) + `
  <div class="cbg"></div><div class="cfade"></div>
  <div class="ck mono one tx" data-r="860">${esc(c.kicker)}</div><div class="cbar"></div>
  <div class="ct one tx" data-r="900">${esc(c.title)}</div>
  <div class="cs one tx" data-r="900">${esc(c.subtitle)}</div>
  <div class="cm mono one tx" data-r="860">${esc(c.meta)}</div>
  <div class="cflow"><div class="ctext"><div class="cd tx" data-lines="3">${esc(c.desc)}</div><div class="cc tx" data-lines="2">${esc(c.counts)}</div></div>
  <div class="cml mono one tx" data-r="860">${esc(c.mapLabel)}</div><img class="cmap" src="${uri(c.map)}">
  <div class="cn mono one tx" data-r="860" data-b="1045">${esc(c.note)}</div></div>
  ${credit(c, 'right:13px;bottom:12px')}</body></html>`;
}

function cover(c) {
  return HEAD(c, 1024, 1024, `
  .cv{--title-size:210px;--title-top:523px;--title-x:72px;--t2-top:742px;--bar-top:833px;--bar-w:220px;--bar-h:6px;
    --sub-size:40px;--sub-top:866px;--line-size:26px;--line-top:923px}
  .vbg{position:absolute;inset:0;background:url(${uri(c.bg)}) ${c.pos || 'center'}/cover}
  .vfade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(9,12,17,0) 35.5%,rgba(9,12,17,.97) 100%)}
  .vt{position:absolute;left:var(--title-x);top:var(--title-top);font-weight:bold;font-size:var(--title-size);line-height:1;color:var(--ink)}
  .vt2{position:absolute;left:78px;top:var(--t2-top);font-weight:bold;font-size:66px;line-height:1;color:var(--ink)}
  .vbar{position:absolute;left:78px;top:var(--bar-top);width:var(--bar-w);height:var(--bar-h);background:var(--bar2)}
  .vs{position:absolute;left:78px;top:var(--sub-top);font-size:var(--sub-size);line-height:1;color:var(--foot)}
  .vl{position:absolute;left:78px;top:var(--line-top);font-size:var(--line-size);line-height:1;letter-spacing:.5px;color:var(--dim)}`).replace('<body', '<body class="cv"') + `
  <div class="vbg"></div><div class="vfade"></div>
  <div class="vt one tx" data-r="984">${esc(c.title)}</div>
  ${c.title2 ? `<div class="vt2 one tx" data-r="984">${esc(c.title2)}</div>` : ''}<div class="vbar"></div>
  <div class="vs mono one tx" data-r="984">${esc(c.sub)}</div>
  <div class="vl one tx" data-r="984">${esc(c.line)}</div>
  ${credit(c, 'right:7px;top:10px')}</body></html>`;
}

function collection(c) {
  const tile = (t, i) => `<div class="xtile" style="left:${80 + 450 * i}px">
    <div class="xph" style="background:url(${uri(t.photo)}) ${t.pos || 'center'}/${t.size || 'cover'} no-repeat"></div>
    <div class="xbar"></div><div class="xn one tx" data-r="${80 + 450 * i + 410}">${esc(t.name)}</div>
    <div class="xm mono one tx" data-r="${80 + 450 * i + 410}">${esc(t.meta)}</div>
    <div class="xc mono one tx" data-r="${80 + 450 * i + 410}">${esc(t.count)}</div></div>`;
  return HEAD(c, 1920, 1080, `
  .xbg{position:absolute;inset:-12px;background:url(${uri(c.bg)}) ${c.pos || 'center'}/cover;filter:blur(3px)}
  .xov{position:absolute;inset:0;background:rgba(0,0,0,.7)}
  .xt{position:absolute;left:80px;top:247px;font-weight:bold;font-size:132px;line-height:1;color:var(--ink)}
  .xk{position:absolute;left:486px;top:261px;font-size:34px;line-height:1;color:var(--foot)}
  .xs{position:absolute;left:488px;top:317px;font-size:30px;line-height:1;color:var(--foot)}
  .xstats{position:absolute;right:80px;top:252px;display:flex;gap:52px}
  .xnum{font-weight:bold;font-size:64px;line-height:1;color:var(--ink)}
  .xlab{margin-top:10px;font-size:20px;line-height:1;color:var(--foot)}
  .xrule{position:absolute;left:80px;top:390px;width:201px;height:4px;background:var(--bar)}
  .xtile{position:absolute;top:410px;width:410px}
  .xph{width:410px;height:230px;outline:1px solid rgba(255,255,255,.08)}
  .xbar{margin-top:17px;width:60px;height:3px;background:var(--bar2)}
  .xn{margin-top:11px;font-weight:bold;font-size:32px;line-height:1;color:var(--ink)}
  .xm{margin-top:11px;font-size:20px;line-height:1;color:var(--foot)}
  .xc{margin-top:8px;font-size:20px;line-height:1;color:var(--foot)}
  .xi{position:absolute;left:80px;top:833px;font-size:24px;line-height:1;color:var(--foot)}
  .xcr{position:absolute;left:80px;top:870px;font-size:19px;line-height:28px;letter-spacing:.5px;color:var(--foot)}`) + `
  <div class="xbg"></div><div class="xov"></div>
  <div class="xt one tx" data-r="470">${esc(c.title)}</div>
  <div class="xk mono one tx" data-r="1350">${esc(c.kicker)}</div>
  <div class="xs one tx" data-r="1350">${esc(c.sub)}</div>
  <div class="xstats">${c.stats.map(([n, l]) => `<div><div class="xnum tx" data-r="1840">${esc(n)}</div><div class="xlab mono tx" data-r="1840">${esc(l)}</div></div>`).join('')}</div>
  <div class="xrule"></div>${c.tiles.map(tile).join('')}
  <div class="xi one tx" data-r="1840">${esc(c.install)}</div>
  <div class="xcr one tx" data-r="1840">${c.credit.map(esc).join('<br>')}</div></body></html>`;
}

const LAYOUTS = { cols: colsSteps, steps: colsSteps, campaign, cover, collection };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const c of cards) {
    const [w, h] = sizeOf(c);
    await p.setViewportSize({ width: w, height: h });
    await p.setContent(LAYOUTS[layoutOf(c)](c), { waitUntil: 'load' });
    // A line's extent is its text's, not its box's; a wrapping block counts
    // its line boxes.
    const over = await p.evaluate(() => [...document.querySelectorAll('.t,.s,.h,.f,.tx')].filter(e => {
      const r = document.createRange(); r.selectNodeContents(e);
      const box = r.getBoundingClientRect(), holder = e.closest('.panel,.steps');
      const right = holder ? holder.getBoundingClientRect().right - 30 : +(e.dataset.r || 1810);
      const lines = new Set([...r.getClientRects()].map(q => Math.round(q.bottom))).size;
      return box.right > right || (e.dataset.lines && lines > +e.dataset.lines) || (e.dataset.b && e.getBoundingClientRect().bottom > +e.dataset.b);
    }).map(e => e.textContent));
    if (over.length) console.log('OVERFLOW', c.out, over);
    await p.screenshot({ path: path.resolve(base, c.out), type: 'jpeg', quality: 90 });
    console.log('wrote', c.out);
  }
  await b.close();
})();
