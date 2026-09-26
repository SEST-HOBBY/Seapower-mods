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

W, H = 1920, 1080                       # story images and backdrop; multiples of 4 (DXT5)
# The mission sheet is the stock size. Pacific Strike's fourteen
# pacific_strike_*_sheet.png are all 1184x640 (measured on an installed copy),
# and the briefing panel that draws MissionImage_ was laid out for that. The
# card is drawn at exactly twice that and halved with Lanczos so the type
# stays crisp; nothing here guesses a size the game never asked for.
SHEET_W, SHEET_H = 1184, 640
# The tile behind a story event on the campaign map. Stock ships two,
# bkg_tile_message.png and bkg_tile_newspaper.png, both 128x128, and points
# TileImagePath_ at them - never at the story image itself.
TILE = 128
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

def card(ini, out_png, num, title, date, place, standfirst, label="SOUTHERN WATCH"):
    S = sections(ini)
    afloat, goal = [], None
    for tag, keys in S.items():
        if not tag.startswith("Taskforce1") or "RelativePositionInNM" not in keys: continue
        if "LandUnit" in tag: continue                      # bases sit off-area
        b = keys["RelativePositionInNM"].split(",")
        try: x, z = float(b[0]), float(b[2])
        except ValueError: continue
        afloat.append((x, z, "air" if ("Aircraft" in tag or "Helicopter" in tag) else
                             "sub" if "Submarine" in tag else "ship"))
    for tag, keys in S.items():
        if tag.startswith("Trigger") and keys.get("Condition_Condition1_Type") == "UnitsInTheArea":
            p = keys.get("Condition_Condition1_PositionNM", "").split(",")
            if len(p) == 3:
                goal = (float(p[0]), float(p[2]),
                        float(keys.get("Condition_Condition1_AreaRadiusNM", 10)))
            break

    CW, CH = SHEET_W * 2, SHEET_H * 2               # drawn at 2x, halved below
    img = Image.new("RGB", (CW, CH), SURFACE)
    d = ImageDraw.Draw(img, "RGBA")

    # --- the plot, as a full-bleed graphic behind the type -------------------
    PW, PH = 1100, 1100
    ox, oy = CW - PW - 80, (CH - PH) // 2
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
    d.text((L+4, CH-118), label, font=font(34, True, mono=True), fill=INK_MUTE)
    d.text((L+4, CH-72), "OWN FORCES · CONTACTS NOT PLOTTED",
           font=font(26, mono=True), fill=(96, 98, 100))
    img = img.resize((SHEET_W, SHEET_H), Image.LANCZOS)
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {SHEET_W}x{SHEET_H}  {len(afloat)} marks, "
          f"objective={'yes' if goal else 'no'}, scale {step} NM")


def tile(out_png, kind):
    """A 128x128 tile for the campaign map, the stock size and the stock names.

    "newspaper" is the cream stock the press sheets are set on; "message" is
    the dark surface every other form (signal, log, INTSUM) shares. Plain on
    purpose: the map draws the event's title over it.
    """
    if kind == "newspaper":
        img = Image.new("RGB", (TILE, TILE), STOCK)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, TILE - 1, TILE - 1], outline=RULE, width=2)
        d.line([(12, 30), (TILE - 12, 30)], fill=RULE, width=3)
        for y in (48, 60, 72, 84, 96):
            d.line([(12, y), (TILE - 12, y)], fill=PAPER_MUTE, width=1)
    else:
        img = Image.new("RGB", (TILE, TILE), PANEL)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, TILE - 1, TILE - 1], outline=FRAME, width=2)
        d.line([(12, 30), (TILE - 12, 30)], fill=BLUE, width=3)
        for y in (48, 60, 72, 84, 96):
            d.line([(12, y), (TILE - 12, y)], fill=GRID, width=1)
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {TILE}x{TILE}  tile ({kind})")


PAPER_INK = (24, 24, 26)
STOCK = (238, 234, 224)
RULE = (24, 24, 26)
PAPER_MUTE, ACCENT = (108, 104, 98), (150, 42, 36)
SER  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono%s.ttf"
def serif(px, bold=False): return ImageFont.truetype(SER % ("-Bold" if bold else ""), px)
def mono(px, bold=False):  return ImageFont.truetype(MONO % ("-Bold" if bold else ""), px)

def dispatch(out_png, masthead, dateline, headline, sub, body, label="SOUTHERN WATCH"):
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
    else:
        # Never set a page that drops its last paragraph: Southern Reach's
        # first draft lost its closing orders this way. Say so and stop.
        raise SystemExit(f"{Path(out_png).name}: the front page needs {len(lines)} "
                         f"lines at {size}pt and has room for {per * 2} - shorten "
                         "the body, the sub or the headline")
    left, right = _split_columns(lines, per)
    for i, col in enumerate((left, right)):
        cx, cy = M + i * (CW + GAP), top
        for line in col:
            if line: d.text((cx, cy), line, font=fnt, fill=PAPER_INK)
            cy += LH
    d.line([(M + CW + GAP//2, top), (M + CW + GAP//2, floor)],
           fill=(198, 192, 180), width=2)

    d.line([(M, H-132), (W-M, H-132)], fill=RULE, width=6)
    d.text((M, H-112), label, font=mono(26, True), fill=PAPER_MUTE)
    d.text((W-M, H-112), dateline.split("|")[-1].strip().upper(),
           font=mono(26), fill=PAPER_MUTE, anchor="ra")
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {W}x{H}  "
          f"{len(lines)} body lines at {size}pt")


def _split_columns(lines, per):
    """Two newspaper columns from wrapped lines ('' marks a paragraph break).

    An even split by line count ignores the paragraphs, and on Southern
    Reach's front page it stranded one word of a sentence ("Tasmania.") at the
    head of the second column. Every split point that fits both columns is
    scored: a paragraph break costs nothing, a break inside a paragraph costs
    a little if at least two of its lines stay on each side and a lot if one
    is stranded, and the columns should come out close to level.
    """
    n = len(lines)
    best = None
    for i in range(1, n + 1):
        left = lines[:i]
        right = lines[i:]
        while right and right[0] == "":
            right = right[1:]
        while left and left[-1] == "":
            left = left[:-1]
        if len(left) > per or len(right) > per:
            continue
        at_break = (i == n) or lines[i - 1] == "" or lines[i] == ""
        if at_break:
            cost = 0
        else:
            j = i
            while j > 0 and lines[j - 1] != "":
                j -= 1
            k = i
            while k < n and lines[k] != "":
                k += 1
            cost = 4 if (i - j >= 2 and k - i >= 2) else 60
        score = cost + abs(len(left) - len(right))
        if best is None or score < best[0]:
            best = (score, left, right)
    if best is None:
        raise SystemExit("front page: the body does not fit two columns")
    return best[1], best[2]


def _optional(event, **params):
    """The labels an event chooses to set, as keyword arguments: event key ->
    parameter name. A key the event leaves out keeps the page's own default,
    so Southern Watch's and Southern Reach's pages are drawn as they were."""
    return {param: event[key] for key, param in params.items() if event.get(key)}


def render_all(camp_dir, missions, events, slug, title, subtitle,
               prefix="southern_watch", label="SOUTHERN WATCH",
               tiles=("newspaper", "message")):
    """Write every card and dispatch into the campaign's art folder.

    Returns {mission key: relative image path} and {event file: asset key} so
    the campaign.ini and the story pages can point at what was actually
    written, rather than at names somebody typed twice. The backdrop is
    written to the native filename, so campaign.ini's BackgroundImage is the
    one path here that is spelled rather than returned.

    `tiles` is the map tiles the campaign's events stand on (the builder's
    event_tiles()). Only those are written: a campaign with no press page
    that shipped bkg_tile_newspaper.png would carry a file nothing points at.

    The pages were drawn from the coalition's side of the table. An event may
    relabel them: `note_label` on a signal or a log (default ANALYST NOTE /
    MASTER'S NOTE), `log_heading` and `master_label` on a log (DECK LOG
    EXTRACT / MASTER), `marking` on an intelligence summary.
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
            marks.append((m.get("code", m["num"]), ll[0], ll[1], m["group"] == "core"))
        if m["group"] == "dispatch":
            continue
        name = f"{prefix}_{m.get('code', m['num']).lower()}_sheet.png"
        # A campaign with two series says which one on the date line, so a
        # card numbered 01 cannot be mistaken for the other chapter's 01.
        dated = f"{m['series'].upper()}  ·  {m['date']}" if m.get("series") else m["date"]
        card(m["ini"], art / name, m["num"], m["key"], dated, m["place"], "", label=label)
        sheets[m["key"]] = f"campaigns/{slug}/art/{name}"
    backdrop(art / "00_campaign_background.png", marks, title, subtitle)
    for kind in ("newspaper", "message"):
        if kind in tiles:
            tile(art / f"bkg_tile_{kind}.png", kind)
    for e in events:
        key = f"{e['file']}_image"
        form = e.get("form", "press")
        if form == "press":
            dispatch(art / f"{key}.png",
                     e["dateline"].split("|")[-1].strip(), e["dateline"],
                     e["headline"], e["sub"], e["body"], label=label)
        elif form == "signal":
            signal(art / f"{key}.png", e["header"], e["body"],
                   strap=e.get("strap"), note=e.get("note"), label=label,
                   **_optional(e, note_label="note_label"))
        elif form == "log":
            log(art / f"{key}.png", e["ship"], e["master"], e["date"],
                e["entries"], note=e.get("note"), label=label,
                **_optional(e, log_heading="heading", master_label="master_label",
                            note_label="note_label"))
        elif form == "intsum":
            intsum(art / f"{key}.png", e["org"], e["ref"], e["date"],
                   e["subject"], e["body"], note=e.get("note"), label=label,
                   **_optional(e, marking="marking"))
        else:
            raise SystemExit(f"{e['file']}: unknown story form {form!r}")
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
            d.text((px, py + 1), num, font=font(22 if len(num) <= 2 else 15, True),
                   fill=CHART, anchor="mm")
        else:                           # the optional beats: present, not loud
            d.ellipse([px-13, py-13, px+13, py+13], outline=(44, 74, 98), width=3)

    # The compass rose, quiet, in the first corner that has no mark under
    # it: top-right by preference (every Southern Watch mark is south-west
    # of it), else bottom-right, else top-left. A rose over a mission mark
    # hides the mission.
    r = 96
    cx, cy = W - 190, 190
    for ccx, ccy in ((W - 190, 190), (W - 190, H - 190), (190, 190)):
        if all(math.hypot(px - ccx, py - ccy) > r + 40 for _n, px, py, _c in pos):
            cx, cy = ccx, ccy
            break
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


# --- three more document forms ---------------------------------------------
# Pacific Strike tells its story in at least ten forms - breaking news,
# newspaper, INTSUM, JCS sitrep, logistics advisory, coastwatcher report, two
# intercept transcripts, targeting intel, a BDA report, a combat record - and
# that variety is how it makes six weeks feel like six weeks. This campaign
# had one form. These are three more, chosen because the campaign's cast
# writes in them: a liaison officer sends a cable, a master keeps a log, an
# intelligence cell writes an INTSUM. Same 1920x1080, same multiples-of-4 rule.

SIG_STOCK  = (226, 230, 224)            # a grey-green teleprinter roll
SIG_INK    = (28, 32, 30)
SIG_RULE   = (120, 128, 122)
SIG_STRAP  = (150, 42, 36)
LOG_STOCK  = (240, 236, 224)
LOG_RULE   = (196, 190, 176)
LOG_INK    = (30, 28, 26)
LOG_MARGIN = (170, 60, 50)
RPT_STOCK  = (250, 250, 248)
RPT_INK    = (20, 20, 22)
RPT_BAND   = (24, 24, 26)

def _fit_lines(d, text, fnt, width):
    out, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur: out.append(cur)
            cur = word
    if cur: out.append(cur)
    return out

def _set_block(d, lines, x, y, fnt, width, lh, fill):
    """Wrap and draw a list of paragraphs; returns the y after the last line.
    A paragraph is drawn as-is if it already fits (so a pre-formatted signal
    line keeps its spacing), wrapped if it does not, and '' is a blank line.
    A line that opens with a speaker tag ('A:  ') or a paragraph number
    ('1. ') hangs its continuation under the text, not under the tag."""
    for para in lines:
        if para == "":
            y += lh; continue
        m = re.match(r"^([A-Z]:\s+|\d+\.\s+|[a-z]\.\s+)", para)
        hang = d.textlength(m.group(1), font=fnt) if m else 0
        if d.textlength(para, font=fnt) <= width:
            chunk = [para]
        else:
            head, rest = (m.group(1), para[m.end():]) if m else ("", para)
            wrapped = _fit_lines(d, rest, fnt, width - hang)
            chunk = [head + wrapped[0]] + wrapped[1:]
        for i, line in enumerate(chunk):
            d.text((x + (hang if i else 0), y), line, font=fnt, fill=fill); y += lh
    return y


def signal(out_png, header, body, strap=None, note=None, label="SOUTHERN WATCH",
           note_label="ANALYST NOTE"):
    """A cable, a memo or an intercept: monospace on teleprinter stock.

    `header` is a list of (label, value) rows for the ruled box at the top -
    FROM/TO/DTG/PREC/SUBJ for a cable, or a single INTERCEPT line. `strap` is
    the red word across the top when the page is an intercept. `note` is the
    box at the foot, or None, headed `note_label`: an analyst's on a page the
    coalition read, the sender's own on a signal the other side kept.
    """
    img = Image.new("RGB", (W, H), SIG_STOCK)
    d = ImageDraw.Draw(img)
    M, y = 110, 84
    for x in range(0, W, 3):                     # faint perforation track
        d.point((x, 40), fill=SIG_RULE); d.point((x, H-40), fill=SIG_RULE)
    if strap:
        d.text((M, y), strap, font=mono(30, True), fill=SIG_STRAP); y += 50
    d.line([(M, y), (W-M, y)], fill=SIG_INK, width=3); y += 18
    lab = mono(24, True); val = mono(24)
    for k, v in header:
        d.text((M, y), f"{k:<6}", font=lab, fill=SIG_INK)
        for line in _fit_lines(d, v, val, W - 2*M - 130):
            d.text((M + 130, y), line, font=val, fill=SIG_INK)
            y += 34
    y += 10
    d.line([(M, y), (W-M, y)], fill=SIG_INK, width=3); y += 40
    note_lines = _fit_lines(d, note, mono(21), W-2*M) if note else []
    note_height = 50 + len(note_lines)*30 if note else 0
    floor = H - 100 - note_height - (36 if note else 0)
    for size in (28, 26, 24, 22, 20):
        fnt, lh = mono(size), int(size * 1.5)
        # measure first; only draw at the size that fits above the floor
        yy = y
        for para in body:
            if para == "": yy += lh; continue
            hang = re.match(r"^([A-Z]:\s+|\d+\.\s+|[a-z]\.\s+)", para)
            indent = d.textlength(hang.group(1), font=fnt) if hang else 0
            content = para[hang.end():] if hang else para
            n = len(_fit_lines(d, content, fnt, W-2*M-indent))
            yy += n * lh
        if yy <= floor: break
    if yy > floor:
        raise ValueError(f"{out_png}: signal body exceeds the page")
    y = _set_block(d, body, M, y, fnt, W-2*M, lh, SIG_INK)
    if note:
        ny = H - 100 - note_height
        d.rectangle([M-16, ny-16, W-M+16, H-80], outline=SIG_RULE, width=3)
        d.text((M, ny), note_label, font=mono(22, True), fill=SIG_STRAP)
        _set_block(d, [note], M, ny+34, mono(21), W-2*M, 30, SIG_INK)
    d.text((W-M, H-64), label, font=mono(20), fill=SIG_RULE, anchor="ra")
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {W}x{H}  signal, {len(body)} lines at {size}pt")


def log(out_png, ship, master, date, entries, note=None, label="SOUTHERN WATCH",
        heading="DECK LOG EXTRACT", master_label="MASTER", note_label="MASTER'S NOTE"):
    """A deck log extract: a ruled page with a time column and a master's note.

    `entries` is a list of (time, text); a time of '' continues the previous
    entry. `note` is the master's remark, boxed at the foot. A warship's log
    is headed and signed differently - `heading`, `master_label` (the line
    that names `master`) and `note_label` say how. The heading sits
    clear of the red margin rule, which runs only beside the entries; each
    entry's wrapped lines hang under its first, ruled at the baseline; and
    the type steps down until every entry fits - an entry is never dropped.
    """
    img = Image.new("RGB", (W, H), LOG_STOCK)
    d = ImageDraw.Draw(img)
    M = 120
    muted = (100, 96, 90)

    y = 70
    d.text((M, y), heading, font=mono(24, True), fill=muted)
    d.text((W-M, y), date.upper(), font=mono(24), fill=muted, anchor="ra")
    y += 44
    d.text((M, y), ship.upper(), font=serif(46, True), fill=LOG_INK)
    y += 60
    d.text((M, y), f"{master_label}: {master.upper()}", font=mono(22), fill=muted)
    y += 44
    d.line([(M, y), (W-M, y)], fill=LOG_INK, width=3)
    y += 14
    d.text((M, y), "TIME", font=mono(18, True), fill=muted)
    TCOL = 170
    d.text((M + TCOL, y), "REMARKS", font=mono(18, True), fill=muted)
    y += 34
    top = y
    # Measure the note before reserving space, including a separate signature.
    sig = re.search(r"\s+-\s*([A-Z][A-Za-z.]{0,5}\.?)\s*$", note) if note else None
    note_body = note[:sig.start()] if sig else note
    note_lines = _fit_lines(d, note_body, serif(26), W-2*M-56) if note else []
    note_height = 56 + len(note_lines)*38 + (54 if sig else 28) if note else 0
    box_top = H - 98 - note_height
    floor = box_top - 36 if note else H - 120

    for size in (28, 27, 26, 25, 24, 23, 22, 21, 20):
        fnt, tf = serif(size), mono(size, True)
        lh, gap = int(size * 1.62), int(size * 0.55)
        need = sum(len(_fit_lines(d, text, fnt, W - M - TCOL - M)) * lh + gap
                   for _t, text in entries)
        if top + need <= floor:
            break
    else:
        raise ValueError(f"{out_png}: deck log exceeds the page; shorten or split the extract")

    rule_x = M + TCOL - 28
    for t, text in entries:
        lines = _fit_lines(d, text, fnt, W - M - TCOL - M)
        if t:
            d.text((rule_x - 22, y), t, font=tf, fill=LOG_INK, anchor="ra")
        for line in lines:
            d.text((M + TCOL, y), line, font=fnt, fill=LOG_INK)
            y += lh
            d.line([(M, y - 10), (W-M, y - 10)], fill=LOG_RULE, width=1)
        y += gap
    d.line([(rule_x, top - 6), (rule_x, max(y, top + lh))], fill=LOG_MARGIN, width=2)

    if note:
        d.rectangle([M, box_top, W-M, H-98], outline=LOG_RULE, width=2)
        d.text((M + 28, box_top + 22), note_label, font=mono(18, True), fill=LOG_MARGIN)
        # a trailing "  - L.S." is a signature: set it right, never wrapped
        for i, line in enumerate(note_lines):
            d.text((M+28, box_top+56+i*38), line, font=serif(26), fill=LOG_INK)
        if sig:
            d.text((W - M - 28, H - 98 - 22), f"- {sig.group(1)}", font=serif(26, True),
                   fill=LOG_INK, anchor="rd")
    d.text((W-M, H-64), label, font=mono(20), fill=LOG_RULE, anchor="ra")
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {W}x{H}  log, {len(entries)} entries at {size}pt")


def intsum(out_png, org, ref, date, subject, paras, note=None, label="SOUTHERN WATCH",
           marking="SECRET  //  RELEASABLE TO COALITION PARTNERS"):
    """A typed intelligence summary. `paras` is a list of strings; a string starting
    with a letter-and-dot ('a. ...') is a sub-paragraph and indents."""
    img = Image.new("RGB", (W, H), RPT_STOCK)
    d = ImageDraw.Draw(img)
    M = 120
    for by in (0, H-56):
        d.rectangle([0, by, W, by+56], fill=RPT_BAND)
        d.text((W/2, by+28), marking, font=mono(24, True),
               fill=RPT_STOCK, anchor="mm")
    y = 96
    # The originator and the reference share the top line, as on a typed
    # form; only an originator too long for that drops the reference below
    # it. Stacking them always cost the Meridian summary two sizes of type.
    head, refdate = org.upper(), f"{ref}  ·  {date.upper()}"
    hf, rf = mono(24, True), mono(23)
    d.text((M, y), head, font=hf, fill=RPT_INK)
    if d.textlength(head, font=hf) + 40 + d.textlength(refdate, font=rf) <= W - 2*M:
        d.text((W-M, y), refdate, font=rf, fill=RPT_INK, anchor="ra"); y += 44
    else:
        y += 38
        d.text((M, y), refdate, font=rf, fill=RPT_INK); y += 44
    for line in _fit_lines(d, f"SUBJECT: {subject.upper()}", mono(28, True), W-2*M):
        d.text((M, y), line, font=mono(28, True), fill=RPT_INK)
        y += 40
    d.line([(M, y), (W-M, y)], fill=RPT_INK, width=2); y += 30
    # A trailing "  - Cdre Mercer" is a signature: it keeps its two spaces
    # and is never split, on the last line if it fits there, else its own.
    sig = re.search(r"\s{2,}-\s*([A-Z][A-Za-z. ]{0,30}?)\s*$", note) if note else None
    note_body = note[:sig.start()] if sig else note
    note_lines = _fit_lines(d, note_body, serif(26), W-2*M) if note else []
    if sig:
        signed = f"{note_lines[-1]}  - {sig.group(1)}" if note_lines else f"- {sig.group(1)}"
        if note_lines and d.textlength(signed, font=serif(26)) <= W-2*M:
            note_lines[-1] = signed
        else:
            note_lines.append(f"- {sig.group(1)}")
    note_height = len(note_lines)*36 + 28 if note else 0
    floor = H - 100 - note_height
    for size in (26, 24, 22, 20, 18):
        fnt, lh = mono(size), int(size * 1.5)
        yy = y
        for i, p in enumerate(paras):
            ind = 70 if re.match(r"^[a-z]\. ", p) else 0
            yy += lh * len(_fit_lines(d, p, fnt, W-2*M-ind))
            # the half-line is the gap BETWEEN paragraphs; nothing follows the last
            yy += (lh // 2) if i < len(paras) - 1 else 0
        if yy <= floor: break
    if yy > floor:
        raise ValueError(f"{out_png}: intelligence summary exceeds the page")
    for p in paras:
        ind = 70 if re.match(r"^[a-z]\. ", p) else 0
        for line in _fit_lines(d, p, fnt, W-2*M-ind):
            d.text((M+ind, y), line, font=fnt, fill=RPT_INK); y += lh
        y += lh // 2
    if note:
        for i, line in enumerate(note_lines):
            d.text((M, H-100-note_height+28+i*36), line, font=serif(26), fill=(60, 60, 120))
    img.save(out_png)
    print(f"wrote {Path(out_png).name}  {W}x{H}  intsum, {len(paras)} paras at {size}pt")
