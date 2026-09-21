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


def render_all(camp_dir, missions, events, slug, title, subtitle):
    """Write every card and dispatch into the campaign's art folder.

    Returns {mission key: relative image path} and {event file: asset key} so
    the campaign.ini and the story pages can point at what was actually
    written, rather than at names somebody typed twice. The backdrop is
    written to the native filename, so campaign.ini's BackgroundImage is the
    one path here that is spelled rather than returned.
    """
    art = Path(camp_dir) / "art"
    art.mkdir(parents=True, exist_ok=True)
    sheets, assets, marks = {}, {}, []
    for m in missions:
        # Every mission contributes a mark to the backdrop. Only the ones the
        # CAMPAIGN lists get a card: MissionImage_/TileImagePath_ are
        # campaign.ini keys, and no key in the vanilla export gives a mission
        # BROWSER entry an image. The dispatches are browser-only, so a card
        # for one is 60 KB the download carries and nothing can display.
        ll = _ll(m["ini"])
        if ll:
            marks.append((m["num"], ll[0], ll[1], m["group"] == "core"))
        if m["group"] == "dispatch":
            continue
        name = f"southern_watch_{m['num'].lower()}_sheet.png"
        card(m["ini"], art / name, m["num"], m["key"], m["date"], m["place"], "")
        sheets[m["key"]] = f"campaigns/{slug}/art/{name}"
    backdrop(art / "00_campaign_background.png", marks, title, subtitle)
    for e in events:
        key = f"{e['file']}_image"
        dispatch(art / f"{key}.png",
                 e["dateline"].split("|")[-1].strip(), e["dateline"],
                 e["headline"], e["sub"], e["body"])
        assets[e["file"]] = key
    return sheets, assets


# --- the campaign backdrop ---------------------------------------------------
# Native key, attested three times: Pacific Strike, Molniya and the linear
# prototype all set BackgroundImage to art/00_campaign_background.png, and the
# prototype does it on DisplayFormat=Legacy - the format this campaign uses.
# The game's own PNGs are not in the repo's export (the export carries text
# only), so nothing here copies their look; what it copies is the key.
#
# It is a plotting sheet, not a map. Drawing a coastline would mean inventing
# one - there is no shoreline data in this repo - and a wrong Arafura Sea in
# the background of a campaign set there is worse than no shoreline at all.
# What IS real is where the missions happen: every mission file carries a
# MapCenterLatitude/Longitude, so the graticule, the track and the marks are
# read back out of the twelve files that just shipped.
#
# Everything is kept dark and low-contrast on purpose: this sits UNDER the
# campaign UI, and a backdrop that competes with the mission list is a bug.
DEEP   = (9, 12, 16)
SEA    = (13, 18, 24)
LINE   = (30, 40, 51)
LINE_H = (44, 58, 73)                   # the 5-degree lines, one step up
CHART  = (86, 104, 122)
TRACK  = (52, 110, 152)
TITLE_INK = (126, 140, 154)

def _ll(path):
    S = sections(path)
    env = S.get("Environment") or S.get("Mission") or {}
    for keys in S.values():
        if "MapCenterLatitude" in keys:
            env = keys
            break
    try:
        return float(env["MapCenterLatitude"]), float(env["MapCenterLongitude"])
    except (KeyError, ValueError):
        return None

def _hemi(v, pair):
    return f"{abs(v):.0f}{pair[0] if v >= 0 else pair[1]}"

def backdrop(out_png, marks, title, subtitle):
    """marks: [(number, lat, lon, is_core)] in campaign order."""
    img = Image.new("RGB", (W, H), DEEP)
    d = ImageDraw.Draw(img, "RGBA")

    lats = [m[1] for m in marks] or [-10.0]
    lons = [m[2] for m in marks] or [131.0]
    # Pad to the frame's aspect so the theatre is centred rather than stretched.
    pad = 2.2
    la0, la1 = min(lats) - pad, max(lats) + pad
    lo0, lo1 = min(lons) - pad, max(lons) + pad
    if (lo1 - lo0) / (la1 - la0) < W / H:
        need = (la1 - la0) * W / H
        mid = (lo0 + lo1) / 2
        lo0, lo1 = mid - need / 2, mid + need / 2
    else:
        need = (lo1 - lo0) * H / W
        mid = (la0 + la1) / 2
        la0, la1 = mid - need / 2, mid + need / 2
    def to_px(lat, lon):
        return ((lon - lo0) / (lo1 - lo0) * W, (la1 - lat) / (la1 - la0) * H)

    for y in range(0, H, 4):            # a shallow sea-to-deep gradient
        t = y / H
        d.rectangle([0, y, W, y + 4], fill=tuple(
            int(a + (b - a) * t) for a, b in zip(SEA, DEEP)))

    lo = math.ceil(lo0)
    while lo <= lo1:                    # meridians, every degree
        px, _ = to_px(0, lo)
        heavy = lo % 5 == 0
        d.line([(px, 0), (px, H)], fill=LINE_H if heavy else LINE,
               width=2 if heavy else 1)
        if heavy:
            d.text((px + 10, H - 38),
                   f"{abs(lo):.0f}°{'E' if lo >= 0 else 'W'}",
                   font=mono(22), fill=(58, 72, 86))
        lo += 1
    la = math.ceil(la0)
    while la <= la1:                    # parallels, every degree
        _, py = to_px(la, 0)
        heavy = la % 5 == 0
        d.line([(0, py), (W, py)], fill=LINE_H if heavy else LINE,
               width=2 if heavy else 1)
        if heavy:
            # Hemisphere from the sign, not from the theatre: padding the
            # frame out to 16:9 pushes the top edge over the equator, and a
            # parallel labelled 0S would be the one wrong thing on the chart.
            d.text((14, py - 30), "EQUATOR" if la == 0 else
                   f"{abs(la):.0f}°{'S' if la < 0 else 'N'}",
                   font=mono(22), fill=(58, 72, 86))
        la += 1

    # Several missions share one patch of water - 01, 12 and the optional beat
    # all sail from the same place - so the marks land on top of each other and
    # the numbers turn to mud. Push them apart in PIXELS, not in degrees: a
    # fixed angular offset is a different distance on every chart, and the
    # first attempt at this shoved 01 straight into 05 a degree away.
    marks.sort(key=lambda m: (not m[3], m[0]))
    pos = [[m[0], *to_px(m[1], m[2]), m[3]] for m in marks]
    for _ in range(140):
        moved = False
        for i, a in enumerate(pos):
            for b in pos[i+1:]:
                gap = 62 if (a[3] and b[3]) else 46
                dx, dy = b[1] - a[1], b[2] - a[2]
                dist = math.hypot(dx, dy)
                if dist >= gap:
                    continue
                if dist < 1e-6:         # exactly coincident: pick a direction
                    dx, dy, dist = math.cos(i), math.sin(i), 1.0
                push = (gap - dist) / 2 / dist
                a[1] -= dx * push; a[2] -= dy * push
                b[1] += dx * push; b[2] += dy * push
                moved = True
        if not moved:
            break

    core = [m for m in pos if m[3]]
    if len(core) > 1:                   # the campaign's track, in its own order
        d.line([(m[1], m[2]) for m in core],
               fill=(52, 110, 152, 96), width=3, joint="curve")
    for num, px, py, is_core in pos:
        if is_core:
            d.ellipse([px-38, py-38, px+38, py+38], fill=(52, 110, 152, 26))
            d.ellipse([px-21, py-21, px+21, py+21], fill=DEEP, outline=TRACK, width=4)
            d.text((px, py + 1), num, font=font(22, True), fill=CHART,
                   anchor="mm")
        else:                           # the optional beats: present, not loud
            d.ellipse([px-13, py-13, px+13, py+13], outline=(44, 74, 98), width=3)

    cx, cy, r = W - 190, 190, 96        # compass rose, quiet
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(38, 52, 66), width=3)
    d.ellipse([cx-r+22, cy-r+22, cx+r-22, cy+r-22], outline=(30, 42, 54), width=2)
    for a in range(0, 360, 15):
        t = math.radians(a)
        k = r if a % 45 == 0 else r - 12
        d.line([(cx + math.sin(t)*(r-22), cy - math.cos(t)*(r-22)),
                (cx + math.sin(t)*k, cy - math.cos(t)*k)], fill=(46, 62, 78), width=2)
    d.polygon([(cx, cy-r+30), (cx+15, cy+16), (cx, cy+2), (cx-15, cy+16)],
              fill=(58, 80, 100))
    d.text((cx, cy + 62), "N", font=font(26, True), fill=(70, 92, 112), anchor="ms")

    for i in range(260):                # vignette: the UI sits on top of this
        a = int(120 * (1 - i / 260) ** 2.1)   # darkest at the edge, gone by the middle
        if a:
            d.rectangle([i, i, W-1-i, H-1-i], outline=(0, 0, 0, a), width=1)

    d.text((92, H - 232), title.upper(), font=font(104, True), fill=TITLE_INK)
    d.line([(96, H - 118), (96 + 260, H - 118)], fill=(52, 110, 152), width=5)
    d.text((96, H - 100), subtitle.upper(), font=mono(28), fill=(72, 84, 96))
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {W}x{H}  "
          f"{len(core)} core marks, {len(marks)-len(core)} optional, "
          f"{_hemi(la1, 'NS')}..{_hemi(la0, 'NS')}, "
          f"{_hemi(lo0, 'EW')}..{_hemi(lo1, 'EW')}")
