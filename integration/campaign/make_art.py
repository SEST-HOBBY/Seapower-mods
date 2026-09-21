"""The campaign's art: a mission card per mission, a dispatch sheet per beat.

Both are GENERATED from the same data the missions are, so a card cannot
describe a mission that changed underneath it. The mission card is a poster
first - the campaign map draws it small, so the number and the name carry it
at thumbnail size and the plot is a bold shape beneath. It shows own force,
the objective and the water, and never the opposition: several of these
missions are about finding it, and a card that plots the submarine ruins the
mission it advertises.

Pillow only. If it is not installed the pack builder keeps the committed PNGs
and says so, so a machine without it can still build the campaign.
"""
import math
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080                       # multiples of 4: DXT5 requires it
SURFACE   = (22, 24, 27)
PANEL     = (17, 19, 22)
INK       = (240, 238, 234)
INK_MUTE  = (150, 150, 148)
GRID      = (40, 44, 49)
FRAME     = (78, 82, 86)
BLUE      = (61, 143, 201)              # validated pair, deutan dE 18.6
BLUE_DIM  = (38, 84, 120)
F  = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono%s.ttf"
def font(px, bold=False, mono=False):
    return ImageFont.truetype((FM if mono else F) % ("-Bold" if bold else ""), px)

def sections(path):
    out, cur = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = line.strip(); m = re.match(r"^\[([^\]]+)\]", s)
        if m: cur = m.group(1); out[cur] = {}
        elif cur and "=" in s:
            k, _, v = s.partition("="); out[cur][k.strip()] = v.strip()
    return out

def card(ini, out_png, num, title, date, place, standfirst):
    S = sections(ini)
    afloat, goal = [], None
    for tag, keys in S.items():
        if not tag.startswith("Taskforce1") or "RelativePositionInNM" not in keys: continue
        if "LandUnit" in tag: continue                      # bases sit off-area
        b = keys["RelativePositionInNM"].split(",")
        try: x, z = float(b[0]), float(b[2])
        except ValueError: continue
        afloat.append((x, z, "air" if "Aircraft" in tag else
                             "sub" if "Submarine" in tag else "ship"))
    for tag, keys in S.items():
        if tag.startswith("Trigger") and keys.get("Condition_Condition1_Type") == "UnitsInTheArea":
            p = keys.get("Condition_Condition1_PositionNM", "").split(",")
            if len(p) == 3:
                goal = (float(p[0]), float(p[2]),
                        float(keys.get("Condition_Condition1_AreaRadiusNM", 10)))
            break

    img = Image.new("RGB", (W, H), SURFACE)
    d = ImageDraw.Draw(img, "RGBA")

    # --- the plot, as a full-bleed graphic behind the type -------------------
    PW, PH = 900, 900
    ox, oy = W - PW - 70, (H - PH) // 2 + 10
    d.rectangle([ox-2, oy-2, ox+PW+2, oy+PH+2], fill=PANEL, outline=FRAME, width=3)

    pts = [(x, z) for x, z, _ in afloat] or [(0, 0)]
    if goal: pts.append((goal[0], goal[1]))
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    span = max(max(xs)-min(xs), max(zs)-min(zs), 20.0) * 1.42
    cx, cz = (min(xs)+max(xs))/2, (min(zs)+max(zs))/2
    x0, z1 = cx - span/2, cz + span/2
    def to_px(x, z): return (ox + (x-x0)/span*PW, oy + (z1-z)/span*PH)

    step = next(s for s in (2, 5, 10, 20, 25, 50, 100) if span/s <= 7)
    g = math.ceil(x0/step)*step
    while g <= x0+span:
        px,_ = to_px(g,0); d.line([(px,oy),(px,oy+PH)], fill=GRID, width=2); g += step
    g = math.ceil((z1-span)/step)*step
    while g <= z1:
        _,py = to_px(0,g); d.line([(ox,py),(ox+PW,py)], fill=GRID, width=2); g += step

    if goal:                                        # one ring, unmissable
        gx, gy = to_px(goal[0], goal[1]); rr = max(26, goal[2]/span*PW)
        d.ellipse([gx-rr,gy-rr,gx+rr,gy+rr], fill=(61,143,201,26))
        for a in range(0, 360, 14):
            d.arc([gx-rr,gy-rr,gx+rr,gy+rr], a, a+8, fill=BLUE, width=7)

    for x, z, kind in afloat:                       # thick marks, no labels
        px, py = to_px(x, z)
        d.ellipse([px-26,py-26,px+26,py+26], fill=(61,143,201,38))
        d.ellipse([px-19,py-19,px+19,py+19], fill=PANEL)
        if kind == "air":
            d.polygon([(px,py-17),(px+16,py+13),(px-16,py+13)], fill=BLUE)
        elif kind == "sub":
            d.ellipse([px-17,py-10,px+17,py+10], outline=BLUE, width=6)
        else:
            d.ellipse([px-15,py-15,px+15,py+15], fill=BLUE)

    bar = step/span*PW
    bx, by = ox+40, oy+PH-46
    d.line([(bx,by),(bx+bar,by)], fill=INK_MUTE, width=5)
    for e in (bx, bx+bar): d.line([(e,by-13),(e,by+13)], fill=INK_MUTE, width=5)
    d.text((bx+bar/2, by-22), f"{step} NM", font=font(30, True), fill=INK_MUTE, anchor="ms")
    nx, ny = ox+PW-56, oy+68
    d.polygon([(nx,ny-40),(nx+14,ny+10),(nx,ny-4),(nx-14,ny+10)], fill=INK_MUTE)
    d.text((nx, ny+50), "N", font=font(32, True), fill=INK_MUTE, anchor="ms")

    # --- the type, sized to survive the thumbnail ---------------------------
    L = 86
    d.text((L, 128), num, font=font(300, True), fill=BLUE_DIM)
    d.text((L+6, 424), date.upper(), font=font(40, True, mono=True), fill=BLUE)
    lines = textwrap.wrap(title.upper(), 11)
    y = 456
    for line in lines:
        d.text((L, y), line, font=font(132, True), fill=INK); y += 132
    y += 18
    d.line([(L, y), (L+300, y)], fill=BLUE, width=7); y += 40
    d.text((L+4, y), place.upper(), font=font(46), fill=INK_MUTE)
    d.text((L+4, H-118), "SOUTHERN WATCH", font=font(34, True, mono=True), fill=INK_MUTE)
    d.text((L+4, H-72), "OWN FORCE ONLY · OPPOSITION NOT SHOWN",
           font=font(26, mono=True), fill=(96, 98, 100))
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {W}x{H}  {len(afloat)} marks, "
          f"objective={'yes' if goal else 'no'}, scale {step} NM")


PAPER_INK = (24, 24, 26)
STOCK = (238, 234, 224)
RULE = (24, 24, 26)
PAPER_MUTE, ACCENT = (108, 104, 98), (150, 42, 36)
SER  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono%s.ttf"
def serif(px, bold=False): return ImageFont.truetype(SER % ("-Bold" if bold else ""), px)
def mono(px, bold=False):  return ImageFont.truetype(MONO % ("-Bold" if bold else ""), px)

def dispatch(out_png, masthead, dateline, headline, sub, body):
    img = Image.new("RGB", (W, H), STOCK)
    d = ImageDraw.Draw(img)
    M = 96

    d.line([(M, 92), (W-M, 92)], fill=RULE, width=6)
    d.text((M, 112), masthead.upper(), font=mono(30, True), fill=PAPER_INK)
    d.text((W-M, 112), dateline.split("|")[0].strip().upper(),
           font=mono(30), fill=PAPER_MUTE, anchor="ra")
    d.line([(M, 162), (W-M, 162)], fill=RULE, width=2)

    y = 208
    for line in textwrap.wrap(headline.upper(), 28):
        d.text((M, y), line, font=serif(86, True), fill=PAPER_INK); y += 96
    y += 26
    d.line([(M, y), (M+220, y)], fill=ACCENT, width=6); y += 40
    for line in textwrap.wrap(sub, 62):
        d.text((M, y), line, font=serif(40), fill=PAPER_MUTE); y += 52

    y += 34
    d.line([(M, y), (W-M, y)], fill=RULE, width=2)
    top, floor = y + 42, H - 196

    # Two columns, set to fit. The body is wrapped, split evenly, and if it
    # still runs past the footer the type steps down a point and it is set
    # again - so a long dispatch is smaller, never truncated and never
    # printed through the rule at the bottom.
    CW, GAP = (W - 2*M - 96) // 2, 96
    for size in (29, 27, 25, 23, 21, 19):
        fnt, LH = serif(size), int(size * 1.52)
        # Wrap on measured width, not an estimate: a guessed character count
        # is what put the right column through the margin.
        def fit(para):
            out, cur = [], ""
            for word in para.split():
                trial = f"{cur} {word}".strip()
                if d.textlength(trial, font=fnt) <= CW:
                    cur = trial
                else:
                    if cur: out.append(cur)
                    cur = word
            if cur: out.append(cur)
            return out
        lines = []
        for para in body:
            lines += fit(para) + [""]
        if lines and lines[-1] == "": lines.pop()
        per = max(1, (floor - top) // LH)
        if len(lines) <= per * 2:
            break
    half = min(per, (len(lines) + 1) // 2)
    for i, col in enumerate((lines[:half], lines[half:half + per])):
        cx, cy = M + i * (CW + GAP), top
        for line in col:
            if line: d.text((cx, cy), line, font=fnt, fill=PAPER_INK)
            cy += LH
    d.line([(M + CW + GAP//2, top), (M + CW + GAP//2, floor)],
           fill=(198, 192, 180), width=2)

    d.line([(M, H-132), (W-M, H-132)], fill=RULE, width=6)
    d.text((M, H-112), "SOUTHERN WATCH", font=mono(26, True), fill=PAPER_MUTE)
    d.text((W-M, H-112), dateline.split("|")[-1].strip().upper(),
           font=mono(26), fill=PAPER_MUTE, anchor="ra")
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {W}x{H}  "
          f"{len(lines)} body lines at {size}pt")


def render_all(camp_dir, missions, events, slug):
    """Write every card and dispatch into the campaign's art folder.

    Returns {mission key: relative image path} and {event file: asset key} so
    the campaign.ini and the story pages can point at what was actually
    written, rather than at names somebody typed twice.
    """
    art = Path(camp_dir) / "art"
    art.mkdir(parents=True, exist_ok=True)
    sheets, assets = {}, {}
    for m in missions:
        name = f"southern_watch_{m['num'].lower()}_sheet.png"
        card(m["ini"], art / name, m["num"], m["key"], m["date"], m["place"], "")
        sheets[m["key"]] = f"campaigns/{slug}/art/{name}"
    for e in events:
        key = f"{e['file']}_image"
        dispatch(art / f"{key}.png",
                 e["dateline"].split("|")[-1].strip(), e["dateline"],
                 e["headline"], e["sub"], e["body"])
        assets[e["file"]] = key
    return sheets, assets
