"""The briefing map: the chart in the right-hand pane of the briefing screen.

The game draws that pane from `<mission>_briefing/BriefingMap_en.xml` beside
the mission .ini - a XAML fragment whose <Image> names an asset by file stem,
`Source="{Binding Assets[<stem>]}"`, resolved to an image in the same folder.
Every stock mission and every stock campaign mission ships one; no SEST
mission did, so the pane was blank on all of them.

What the chart shows, and why. Positions are read from the mission file on
the datum every SEST tool uses (lon = centre + x/60, lat = centre + z/60).
The player's units are drawn where they are. Enemy forces are drawn as a
reported area around each group, not as pins - the briefing is intelligence,
not the answer - and enemy submarines are not drawn at all, because finding
them is the mission more often than not; a note says the threat exists.
Neutrals appear as shipping. Coastlines are Natural Earth 1:10m (public
domain), fetched once into ~/.cache/sest-naturalearth.

Pillow only, the same single optional dependency as the campaign's art, and
the same rule: the PNGs are committed, so a machine without Pillow or without
the coastline data keeps the committed maps rather than shipping none.

The image is drawn at 2192x1328 - twice the 1095x662 canvas the stock maps
are laid out on, rounded up to multiples of 4 because the game DXT-compresses
what it loads and logs every image that is not - and the Viewbox scales it.
"""
import json
import math
import re
import urllib.request
from pathlib import Path

CACHE = Path.home() / ".cache" / "sest-naturalearth"
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
LAYERS = ("ne_10m_land", "ne_10m_minor_islands", "ne_10m_populated_places_simple")

# The stock canvas, used for the map's aspect; the pixels are PW x PH.
W, H = 1095, 662
PW, PH = 2192, 1328
S = PW / W                               # pixels per canvas unit

SEA, LAND, COAST = (22, 40, 58), (93, 107, 88), (169, 181, 154)
GRID, TEXT, MUTED = (44, 70, 96), (232, 238, 242), (159, 178, 194)
FRIEND, HOSTILE, NEUTRAL = (79, 179, 255), (255, 90, 79), (217, 195, 91)
BOX = (255, 213, 74)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"

# Places a briefing names that no unit in the mission marks. They widen the
# map so the thing the text talks about is actually on it.
LANDMARKS = {
    "Viper Zero": [("KENDAWANGAN\nINDUSTRIAL PARK", -2.52, 110.21)],
    "The Open Door": [("LANGGUR", -5.66, 132.73)],
    "Weather Alternate": [("LANGGUR", -5.66, 132.73)],
    # Southern Reach. A fourth element names the colour: "friend" for a port or
    # a station of ours, "muted" for a feature; a three-tuple stays the red
    # star the northern campaign used for an enemy-held place.
    "Southern Departure": [("HOBART", -42.88, 147.33, "friend")],
    "Silent Track": [("AUCKLAND ISLANDS", -50.70, 166.10, "muted")],
    "Macquarie Passage": [("MACQUARIE ISLAND\nSTATION", -54.50, 158.94, "friend")],
    "Broken Supply Line": [("BLUFF", -46.60, 168.34, "friend")],
    "The Gateway": [("LYTTELTON", -43.60, 172.72, "friend")],
    "Southern Line": [("CASEY STATION", -66.28, 110.53, "friend")],
    "Home Waters": [("MILFORD SOUND", -44.67, 167.93, "muted")],
    "Cook Strait": [("WELLINGTON", -41.29, 174.78, "friend"),
                    ("COOK STRAIT\nCABLE ROUTE", -41.40, 174.45, "muted")],
    "Chatham Watch": [("CHATHAM ISLANDS\n200 NM EAST", -44.00, 179.60, "muted")],
    "Bass Strait": [("DEVONPORT", -41.17, 146.36, "friend")],
    "Southern Air Bridge": [("SYDNEY", -33.87, 151.21, "friend")],
    "The Southern Convoy": [("PORTLAND", -38.35, 141.60, "friend")],
    "Northern Priority": [("AUCKLAND", -36.85, 174.76, "friend")],
    "Southern Priority": [("PORT ADELAIDE", -34.85, 138.50, "friend")],
}

UNIT = re.compile(r"^\[(Taskforce(\d)|Neutral)(Vessel|Aircraft|Submarine|LandUnit)(\d+)\]")

XAML = """<Viewbox xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" \
Margin="12" HorizontalAlignment="Center" VerticalAlignment="Center">
    <Image Source="{{Binding Assets[{stem}]}}" Width="1095" Height="662"/>
</Viewbox>
"""


class Unavailable(RuntimeError):
    """Pillow or the coastline data is missing: keep the committed maps."""


# --- mission parsing ---------------------------------------------------------

def parse(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    num = lambda k: float(re.search(rf"^{k}=([-\d.]+)", text, re.M).group(1))
    clat, clon = num("MapCenterLatitude"), num("MapCenterLongitude")
    player = re.search(r"^PlayerTaskforce=Taskforce(\d)", text, re.M)
    player = player.group(1) if player else "1"
    lang = re.search(r"^\[Language_en\]\n(.*?)(?=^\[)", text, re.M | re.S).group(1)
    overrides = dict(re.findall(r"^(\w+?)NameOverride=(.+)$", lang, re.M))

    units = []
    for chunk in re.split(r"(?=^\[)", text, flags=re.M):
        m = UNIT.match(chunk)
        if not m:
            continue
        pos = re.search(r"^RelativePositionInNM=([-\d.]+),[^,\n]*,([-\d.]+)", chunk, re.M)
        if not pos:
            continue
        x, z = float(pos.group(1)), float(pos.group(2))
        side = ("neutral" if m.group(1) == "Neutral"
                else "friend" if m.group(2) == player else "hostile")
        key = m.group(0)[1:-1]
        utype = re.search(r"^Type=(.+)$", chunk, re.M).group(1).strip()
        units.append({"side": side, "kind": m.group(3), "key": key,
                      "type": utype, "name": overrides.get(key),
                      "lat": clat + z / 60.0, "lon": clon + x / 60.0})

    date = re.search(r"^Date=(\d+),(\d+),(\d+)", text, re.M)
    time = re.search(r"^Time=(\d+),(\d+)", text, re.M)
    name = re.search(r"^Name=(.+)$", lang, re.M).group(1).strip()
    return {"name": name, "units": units,
            "date": "{}-{:02d}-{:02d}".format(*map(int, date.groups())) if date else "",
            "time": "{:02d}{:02d}".format(*map(int, time.groups())) if time else ""}


# --- geography ---------------------------------------------------------------

def layers(fetch=True):
    """The three Natural Earth layers, from the cache or the network.

    Raises Unavailable rather than returning half a map: a chart with no
    coastline is worse than the committed one.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    geo = {}
    for name in LAYERS:
        f = CACHE / f"{name}.geojson"
        if not f.exists():
            if not fetch:
                raise Unavailable(f"{name}.geojson is not cached")
            try:
                print(f"  fetching {name} (Natural Earth, public domain)")
                urllib.request.urlretrieve(NE + f"{name}.geojson", f)
            except Exception as exc:          # offline: no map, keep the old one
                raise Unavailable(f"could not fetch {name}: {exc}") from exc
        geo[name] = json.loads(f.read_text(encoding="utf-8"))
    return geo


def rings(geo, box):
    """Outer and hole rings of every polygon that touches box (w, s, e, n)."""
    w, s, e, n = box
    for feat in geo["features"]:
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            xs = [p[0] for p in poly[0]]
            ys = [p[1] for p in poly[0]]
            if max(xs) < w or min(xs) > e or max(ys) < s or min(ys) > n:
                continue
            yield poly


def extent(points, pad=1.2, min_span=5.0):
    """Lon/lat box around every point, padded, stretched to the canvas aspect."""
    lats = [p["lat"] for p in points]
    lons = [p["lon"] for p in points]
    clat = (max(lats) + min(lats)) / 2
    k = math.cos(math.radians(clat))
    span_lat = max(max(lats) - min(lats) + 2 * pad, min_span * 0.6)
    span_lon = max(max(lons) - min(lons) + 2 * pad, min_span)
    if span_lon * k / span_lat < W / H:
        span_lon = span_lat * (W / H) / k
    else:
        span_lat = span_lon * k / (W / H)
    clon = (max(lons) + min(lons)) / 2
    return (clon - span_lon / 2, clat - span_lat / 2,
            clon + span_lon / 2, clat + span_lat / 2)


# --- drawing -----------------------------------------------------------------

def _font(px, bold=False):
    from PIL import ImageFont
    return ImageFont.truetype(F % ("-Bold" if bold else ""), int(px))


def _land(img, d, geo, box, to_px, coast_w):
    from PIL import ImageDraw
    for lyr in ("ne_10m_land", "ne_10m_minor_islands"):
        for poly in rings(geo[lyr], box):
            outer = [to_px(p[0], p[1]) for p in poly[0]]
            if len(outer) >= 3:
                d.polygon(outer, fill=LAND, outline=COAST if coast_w else None,
                          width=coast_w)
            for hole in poly[1:]:
                pts = [to_px(p[0], p[1]) for p in hole]
                if len(pts) >= 3:
                    d.polygon(pts, fill=SEA, outline=COAST if coast_w else None,
                              width=coast_w)


def _text(d, xy, text, font, fill, anchor="la", halo=3):
    d.multiline_text(xy, text, font=font, fill=fill, anchor=anchor if "\n" not in text else "la",
                     stroke_width=halo, stroke_fill=SEA, spacing=4)


def _dashed_ellipse(d, cx, cy, rx, ry, fill, width):
    for a in range(0, 360, 12):
        d.arc([cx - rx, cy - ry, cx + rx, cy + ry], a, a + 7, fill=fill, width=width)


def unit_label(u):
    """'Viper 01' -> 'VIPER'; an unnamed 'ran_ddg_hobart' -> 'DDG HOBART'."""
    if u["name"]:
        return re.sub(r"\s*\d+$", "", u["name"]).upper()
    parts = u["type"].split("_")
    if len(parts) > 1 and parts[0].isalpha() and len(parts[0]) <= 5:
        parts = parts[1:]
    return " ".join(parts).upper()


def draw(mission, out_png, geo, series="SEST SOUTHERN WATCH", focus_nm=None,
         inset_box=None):
    """focus_nm: a base further than this from the player's ships and aircraft
    is left off the chart and named in a corner instead - a Poseidon's field
    640 NM away would otherwise shrink Storm Bay to a dot. inset_box: the
    locator inset's own (w, s, e, n); the northern approaches by default."""
    from PIL import Image, ImageDraw

    units = [u for u in mission["units"]
             if not (u["side"] == "hostile" and u["kind"] == "Submarine")]
    marks = [m if len(m) == 4 else (*m, "hostile") for m in LANDMARKS.get(mission["title"], [])]
    offmap = []
    if focus_nm:
        core = [u for u in units if u["kind"] != "LandUnit"] or units
        clat = sum(u["lat"] for u in core) / len(core)
        clon = sum(u["lon"] for u in core) / len(core)
        kk = math.cos(math.radians(clat))

        def far(u):
            return math.hypot((u["lat"] - clat) * 60, (u["lon"] - clon) * 60 * kk)
        offmap = [u for u in units if u["kind"] == "LandUnit" and far(u) > focus_nm]
        units = [u for u in units if u not in offmap]
    shown = (units or mission["units"]) + [{"lat": la, "lon": lo} for _, la, lo, _c in marks]
    w, s, e, n = box = extent(shown)
    k = math.cos(math.radians((s + n) / 2))

    def to_px(lon, lat):
        return ((lon - w) / (e - w) * PW, (n - lat) / (n - s) * PH)

    img = Image.new("RGB", (PW, PH), SEA)
    d = ImageDraw.Draw(img, "RGBA")
    _land(img, d, geo, box, to_px, coast_w=2)

    # graticule, every 1 or 2 degrees depending on the span
    step = 1 if (e - w) <= 12 else 2
    small = _font(9 * S)
    for lon in range(math.ceil(w / step) * step, int(e) + 1, step):
        x, _ = to_px(lon, s)
        d.line([(x, 0), (x, PH)], fill=GRID, width=2)
        _text(d, (x, PH - 10 * S), f"{abs(lon)}°{'E' if lon >= 0 else 'W'}", small,
              MUTED, anchor="ms", halo=2)
    for lat in range(math.ceil(s / step) * step, int(n) + 1, step):
        _, y = to_px(w, lat)
        d.line([(0, y), (PW, y)], fill=GRID, width=2)
        _text(d, (8 * S, y), f"{abs(lat)}°{'S' if lat < 0 else 'N'}", small,
              MUTED, anchor="lm", halo=2)

    # towns, as orientation only - the bigger ones
    for feat in geo["ne_10m_populated_places_simple"]["features"]:
        p = feat["properties"]
        lon, lat = feat["geometry"]["coordinates"]
        if not (w < lon < e and s < lat < n) or p.get("scalerank", 10) > 6:
            continue
        x, y = to_px(lon, lat)
        d.rectangle([x - 3 * S / 2, y - 3 * S / 2, x + 3 * S / 2, y + 3 * S / 2], fill=MUTED)
        _text(d, (x + 8 * S, y), p["name"], small, MUTED, anchor="lm", halo=2)

    label_f = _font(11 * S, bold=True)
    for label, la, lo, colour in marks:
        col = {"friend": FRIEND, "muted": MUTED}.get(colour, HOSTILE)
        x, y = to_px(lo, la)
        r = 9 * S
        star = [(x + r * math.cos(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45),
                 y + r * math.sin(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45))
                for i in range(10)]
        d.polygon(star, fill=col, outline=(255, 255, 255), width=2)
        lines = label.split("\n")
        ly = y - (len(lines) - 1) * 7 * S
        for line in lines:
            _text(d, (x - 14 * S, ly), line, label_f, col, anchor="rm")
            ly += 14 * S

    # neutral shipping
    for u in units:
        if u["side"] == "neutral":
            x, y = to_px(u["lon"], u["lat"])
            r = 4 * S
            d.ellipse([x - r, y - r, x + r, y + r], outline=NEUTRAL, width=int(1.5 * S))

    # enemy: one reported area per kind, not pins
    kinds = {"Vessel": "surface group", "Aircraft": "air activity",
             "LandUnit": "ground forces"}
    for kind, label in kinds.items():
        grp = [u for u in units if u["side"] == "hostile" and u["kind"] == kind]
        if not grp:
            continue
        la = [u["lat"] for u in grp]
        lo = [u["lon"] for u in grp]
        cy, cx = sum(la) / len(la), sum(lo) / len(lo)
        ry = max((max(la) - min(la)) / 2 + 0.35, 0.45)
        rx = max((max(lo) - min(lo)) / 2 + 0.35 / k, 0.45 / k)
        x0, y0 = to_px(cx - rx, cy + ry)
        x1, y1 = to_px(cx + rx, cy - ry)
        d.ellipse([x0, y0, x1, y1], fill=HOSTILE + (46,))
        _dashed_ellipse(d, (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2,
                        HOSTILE, int(1.5 * S))
        _text(d, ((x0 + x1) / 2, y0 - 6 * S), f"REPORTED {label.upper()}", label_f,
              HOSTILE, anchor="ms")

    # player forces: every unit, one label per cluster ("VIPER x4")
    friends = [u for u in units if u["side"] == "friend"]
    near = lambda a, b: abs(a["lat"] - b["lat"]) < 0.33 and abs(a["lon"] - b["lon"]) < 0.33 / k
    labelled = []
    for u in friends:
        x, y = to_px(u["lon"], u["lat"])
        r = 6 * S
        if u["kind"] == "Vessel":
            pts = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
        elif u["kind"] == "Aircraft":
            pts = [(x, y - r), (x + r, y + r * 0.8), (x - r, y + r * 0.8)]
        elif u["kind"] == "Submarine":
            pts = [(x - r, y - r * 0.8), (x + r, y - r * 0.8), (x, y + r)]
        else:
            pts = [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]
        d.polygon(pts, fill=FRIEND, outline=(255, 255, 255), width=2)
        if any(near(u, v) for v in labelled):
            continue
        labelled.append(u)
        count = sum(1 for v in friends if near(u, v))
        label = unit_label(u) + (f" x{count}" if count > 1 else "")
        _text(d, (x + 12 * S, y), label, label_f, FRIEND, anchor="lm")

    # a hidden submarine is still a threat the player should be told about
    if any(u["side"] == "hostile" and u["kind"] == "Submarine" for u in mission["units"]):
        _text(d, (16 * S, PH * 0.15), "SUBMARINE THREAT - POSITION UNKNOWN", label_f,
              HOSTILE, anchor="la")
    # the fields left off the chart, with a bearing and distance from the force
    for i, u in enumerate(offmap):
        brg = (math.degrees(math.atan2((u["lon"] - clon) * kk, u["lat"] - clat)) + 360) % 360
        pt = "NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW N".split()[int((brg + 11.25) // 22.5) % 16]
        col = FRIEND if u["side"] == "friend" else NEUTRAL if u["side"] == "neutral" else HOSTILE
        _text(d, (16 * S, PH * (0.20 + 0.04 * i)),
              f"OFF CHART: {unit_label(u)}  {far(u):.0f} NM {pt}", _font(10 * S, bold=True),
              col, anchor="la")

    # title block
    _text(d, (16 * S, PH * 0.03), mission["title"].upper(), _font(20 * S, bold=True),
          TEXT, anchor="la")
    stamp = " ".join(x for x in (mission["date"], mission["time"] and
                                 mission["time"] + "L") if x)
    _text(d, (16 * S, PH * 0.095), f"{series}  |  {stamp}", _font(11 * S), MUTED,
          anchor="la")

    # scale bar, 50 or 100 nm
    nm = 100 if (e - w) * 60 * k > 500 else 50
    x0, y0 = PW * 0.04, PH * 0.94
    bar = nm / 60 / k / (e - w) * PW
    d.line([(x0, y0), (x0 + bar, y0)], fill=TEXT, width=int(2.5 * S))
    _text(d, (x0 + bar / 2, y0 - 8 * S), f"{nm} NM", _font(10 * S), TEXT, anchor="ms")

    # legend
    lx, ly = PW * 0.78, PH * 0.95
    rows = [("D", FRIEND, "Own forces")]
    if any(u["side"] == "neutral" for u in units):
        rows.append(("o", NEUTRAL, "Shipping"))
    if any(u["side"] == "hostile" for u in units):
        rows.append(("-", HOSTILE, "Reported enemy"))
    leg_f = _font(10 * S)
    for i, (mk, col, txt) in enumerate(rows):
        yy = ly - i * PH * 0.045
        r = 5 * S
        if mk == "D":
            d.polygon([(lx, yy - r), (lx + r, yy), (lx, yy + r), (lx - r, yy)], fill=col)
        elif mk == "o":
            d.ellipse([lx - r, yy - r, lx + r, yy + r], outline=col, width=int(1.5 * S))
        else:
            for a in (-1.6, -0.2, 1.2):
                d.line([(lx + a * r, yy), (lx + (a + 0.9) * r, yy)], fill=col, width=int(2 * S))
        _text(d, (lx + 14 * S, yy), txt, leg_f, TEXT, anchor="lm")

    # locator inset: the whole theatre, with this map's box on it
    ib = tuple(inset_box) if inset_box else (93, -26, 162, 14)
    iw = int(PW * 0.24)
    ih = int(iw * (ib[3] - ib[1]) / ((ib[2] - ib[0]) * math.cos(math.radians((ib[1] + ib[3]) / 2))))
    inset = Image.new("RGB", (iw, ih), SEA)
    di = ImageDraw.Draw(inset)

    def to_in(lon, lat):
        return ((lon - ib[0]) / (ib[2] - ib[0]) * iw, (ib[3] - lat) / (ib[3] - ib[1]) * ih)

    for poly in rings(geo["ne_10m_land"], ib):
        pts = [to_in(p[0], p[1]) for p in poly[0]]
        if len(pts) >= 3:
            di.polygon(pts, fill=LAND)
    bx0, by0 = to_in(w, n)
    bx1, by1 = to_in(e, s)
    di.rectangle([bx0, by0, bx1, by1], outline=BOX, width=3)
    di.rectangle([0, 0, iw - 1, ih - 1], outline=(255, 255, 255), width=4)
    img.paste(inset, (int(PW * 0.745), int(PH * 0.02)))

    img.save(out_png)


def stem_for(title):
    return "sest_" + re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") + "_map"


def render(ini, folder, title, geo, series="SEST SOUTHERN WATCH", focus_nm=None,
           inset_box=None):
    """Write <stem>.png and BriefingMap_en.xml into folder; returns the stem."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    m = parse(ini)
    m["title"] = title
    stem = stem_for(title)
    for old in folder.glob("*.png"):
        old.unlink()
    draw(m, folder / f"{stem}.png", geo, series=series, focus_nm=focus_nm,
         inset_box=inset_box)
    (folder / "BriefingMap_en.xml").write_bytes(XAML.format(stem=stem).encode("utf-8"))
    return stem


def available():
    """Pillow importable and the layers present or fetchable; else the reason."""
    try:
        import PIL  # noqa: F401
    except ImportError as exc:
        return None, str(exc)
    try:
        return layers(), None
    except Unavailable as exc:
        return None, str(exc)
