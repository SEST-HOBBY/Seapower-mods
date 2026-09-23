#!/usr/bin/env python3
"""Draw the briefing map for every SEST mission.

The briefing screen has two panes. The left one is text and the game fills it
from the mission's own Description, so it always worked. The right one is the
map, and the game draws it only from

    <mission name>_briefing/BriefingMap_en.xml

beside the mission .ini - a XAML fragment whose <Image> names an asset by
file stem: Source="{Binding Assets[<stem>]}". No SEST mission shipped that
folder, so the right pane was blank on every one of them.

The stem resolves to an image in the same _briefing folder. That is how the
Workshop missions that do show a map ship it - mod 3630495619 binds
Assets[ASW_EX_1973_Spanish_coast_briefing], an image named for its own folder,
and the YF-23 campaign binds Assets[OperationalChart]. The stock map names
(WesternPacificFar and friends) are not used here: nothing in the export
proves they resolve outside the missions that ship with the game, and a
missing asset is exactly the blank pane this fixes. Each image gets a
stem unique to its mission, because an asset shared by name across mods is a
collision waiting to happen.

WHAT THE MAP SHOWS

Positions come from the mission file, on the datum every SEST tool uses
(lon = centre + x/60, lat = centre + z/60, verified against Darwin and
Scherger). The player's units are drawn where they are. Enemy forces are
drawn as a reported area around the group, not as pins - the briefing is
intelligence, not the answer - and enemy submarines are not drawn at all,
because finding them is the mission in Narco Transit and Mogami's Corner.
Neutrals appear as shipping traffic.

Coastlines are Natural Earth 1:10m (public domain), fetched once into
~/.cache/sest-naturalearth; the PNGs are committed so building the missions
or the Workshop items never needs matplotlib or the network.

    python3 integration/missions/build_briefing_maps.py          # all SEST missions
    python3 integration/missions/build_briefing_maps.py --list   # what it would draw
"""
import argparse
import json
import math
import re
import sys
import urllib.request
from pathlib import Path

MISSIONS = Path(__file__).resolve().parent
CACHE = Path.home() / ".cache" / "sest-naturalearth"
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
LAYERS = ("ne_10m_land", "ne_10m_minor_islands", "ne_10m_populated_places_simple")

# Canvas the game's own briefing maps are laid out on; the image is drawn at
# twice that for a sharp result and scaled down by the Viewbox.
W, H = 1095, 662
SCALE = 2

SEA, LAND, COAST = "#16283a", "#5d6b58", "#a9b59a"
GRID, TEXT, MUTED = "#2c4660", "#e8eef2", "#9fb2c2"
FRIEND, HOSTILE, NEUTRAL = "#4fb3ff", "#ff5a4f", "#d9c35b"

UNIT = re.compile(r"^\[(Taskforce(\d)|Neutral)(Vessel|Aircraft|Submarine|LandUnit)(\d+)\]")


# --- mission parsing ---------------------------------------------------------

def parse(path):
    text = path.read_text(encoding="utf-8", errors="replace")
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

def layer(name):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{name}.geojson"
    if not f.exists():
        print(f"  fetching {name} (Natural Earth, public domain)")
        urllib.request.urlretrieve(NE + f"{name}.geojson", f)
    return json.loads(f.read_text(encoding="utf-8"))


def rings(geo, box):
    """Outer and hole rings of every polygon that touches box."""
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


def extent(units, pad=1.2, min_span=5.0):
    """Lon/lat box around every unit, padded, stretched to the canvas aspect."""
    lats = [u["lat"] for u in units]
    lons = [u["lon"] for u in units]
    clat = (max(lats) + min(lats)) / 2
    k = math.cos(math.radians(clat))
    span_lat = max(max(lats) - min(lats) + 2 * pad, min_span * 0.6)
    span_lon = max(max(lons) - min(lons) + 2 * pad, min_span)
    # the canvas is W:H in screen units; one degree of lon is k degrees of lat
    if span_lon * k / span_lat < W / H:
        span_lon = span_lat * (W / H) / k
    else:
        span_lat = span_lon * k / (W / H)
    clon = (max(lons) + min(lons)) / 2
    return (clon - span_lon / 2, clat - span_lat / 2,
            clon + span_lon / 2, clat + span_lat / 2)


# --- drawing -----------------------------------------------------------------

def draw(mission, out_png, geo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Ellipse, Rectangle
    from matplotlib import patheffects

    units = [u for u in mission["units"]
             if not (u["side"] == "hostile" and u["kind"] == "Submarine")]
    shown = units or mission["units"]
    box = extent(shown)
    w, s, e, n = box
    k = math.cos(math.radians((s + n) / 2))
    halo = [patheffects.withStroke(linewidth=3, foreground=SEA)]

    fig = plt.figure(figsize=(W * SCALE / 100, H * SCALE / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(SEA)
    fig.patch.set_facecolor(SEA)
    ax.set_xlim(w, e)
    ax.set_ylim(s, n)
    ax.set_aspect(1 / k)
    ax.axis("off")

    def land(axis, box, lw):
        for lyr in ("ne_10m_land", "ne_10m_minor_islands"):
            for poly in rings(geo[lyr], box):
                axis.add_patch(Polygon(poly[0], closed=True, fc=LAND, ec=COAST,
                                       lw=lw, zorder=1))
                for hole in poly[1:]:
                    axis.add_patch(Polygon(hole, closed=True, fc=SEA, ec=COAST,
                                           lw=lw, zorder=1))

    land(ax, box, 0.8)

    # graticule, every 1 or 2 degrees depending on the span
    step = 1 if (e - w) <= 12 else 2
    for lon in range(math.ceil(w / step) * step, int(e) + 1, step):
        ax.axvline(lon, color=GRID, lw=0.8, zorder=0.5)
        ax.text(lon, s + (n - s) * 0.012, f"{abs(lon)}°{'E' if lon >= 0 else 'W'}",
                color=MUTED, fontsize=9 * SCALE / 2, ha="center", zorder=5)
    for lat in range(math.ceil(s / step) * step, int(n) + 1, step):
        ax.axhline(lat, color=GRID, lw=0.8, zorder=0.5)
        ax.text(w + (e - w) * 0.006, lat, f"{abs(lat)}°{'S' if lat < 0 else 'N'}",
                color=MUTED, fontsize=9 * SCALE / 2, va="center", zorder=5)

    # towns, as orientation only - the bigger ones, never on top of a unit
    for feat in geo["ne_10m_populated_places_simple"]["features"]:
        p = feat["properties"]
        lon, lat = feat["geometry"]["coordinates"]
        if not (w < lon < e and s < lat < n) or p.get("scalerank", 10) > 6:
            continue
        ax.plot(lon, lat, "s", ms=3 * SCALE / 2, color=MUTED, zorder=3)
        ax.text(lon + (e - w) * 0.006, lat, p["name"], color=MUTED,
                fontsize=9 * SCALE / 2, va="center", zorder=3, path_effects=halo)

    # neutral shipping
    for u in units:
        if u["side"] == "neutral":
            ax.plot(u["lon"], u["lat"], "o", ms=4 * SCALE / 2, mfc="none",
                    mec=NEUTRAL, mew=1.5, zorder=4)

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
        ax.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry, fc=HOSTILE, alpha=0.18,
                             ec=HOSTILE, lw=1.5, ls="--", zorder=4))
        ax.text(cx, cy + ry + (n - s) * 0.015, f"REPORTED {label.upper()}",
                color=HOSTILE, fontsize=11 * SCALE / 2, ha="center",
                weight="bold", zorder=6, path_effects=halo)

    # player forces: every unit, one label per cluster ("VIPER x4")
    marker = {"Vessel": "D", "Aircraft": "^", "Submarine": "v", "LandUnit": "s"}
    friends = [u for u in units if u["side"] == "friend"]
    near = lambda a, b: abs(a["lat"] - b["lat"]) < 0.33 and abs(a["lon"] - b["lon"]) < 0.33 / k
    labelled = []
    for u in friends:
        ax.plot(u["lon"], u["lat"], marker[u["kind"]], ms=7 * SCALE / 2,
                mfc=FRIEND, mec="white", mew=0.8, zorder=7)
        if any(near(u, v) for v in labelled):
            continue
        labelled.append(u)
        count = sum(1 for v in friends if near(u, v))
        label = unit_label(u) + (f" x{count}" if count > 1 else "")
        ax.text(u["lon"] + (e - w) * 0.012, u["lat"], label, color=FRIEND,
                fontsize=11 * SCALE / 2, weight="bold", va="center", zorder=8,
                path_effects=halo)

    # a hidden submarine is still a threat the player should be told about
    if any(u["side"] == "hostile" and u["kind"] == "Submarine"
           for u in mission["units"]):
        ax.text(w + (e - w) * 0.015, n - (n - s) * 0.15,
                "SUBMARINE THREAT - POSITION UNKNOWN", color=HOSTILE,
                fontsize=11 * SCALE / 2, weight="bold", va="top", zorder=9,
                path_effects=halo)

    # title block
    ax.text(w + (e - w) * 0.015, n - (n - s) * 0.03, mission["title"].upper(),
            color=TEXT, fontsize=20 * SCALE / 2, weight="bold", va="top", zorder=9,
            path_effects=halo)
    stamp = " ".join(x for x in (mission["date"], mission["time"] and
                                 mission["time"] + "L") if x)
    ax.text(w + (e - w) * 0.015, n - (n - s) * 0.095,
            f"SEST SOUTHERN WATCH  |  {stamp}", color=MUTED,
            fontsize=11 * SCALE / 2, va="top", zorder=9, path_effects=halo)

    # scale bar, 50 or 100 nm
    nm = 100 if (e - w) * 60 * k > 500 else 50
    x0, y0 = w + (e - w) * 0.04, s + (n - s) * 0.06
    ax.plot([x0, x0 + nm / 60 / k], [y0, y0], color=TEXT, lw=2.5, zorder=9)
    ax.text(x0 + nm / 120 / k, y0 + (n - s) * 0.015, f"{nm} NM", color=TEXT,
            fontsize=10 * SCALE / 2, ha="center", zorder=9, path_effects=halo)

    # legend
    lx, ly = e - (e - w) * 0.22, s + (n - s) * 0.05
    rows = [("D", FRIEND, "Own forces")]
    if any(u["side"] == "neutral" for u in units):
        rows.append(("o", NEUTRAL, "Shipping"))
    if any(u["side"] == "hostile" for u in units):
        rows.append(("", HOSTILE, "Reported enemy"))
    for i, (mk, col, txt) in enumerate(rows):
        yy = ly + i * (n - s) * 0.045
        if mk:
            ax.plot(lx, yy, mk, ms=6 * SCALE / 2, mfc=col if mk != "o" else "none",
                    mec=col, zorder=9)
        else:
            ax.plot([lx - (e - w) * 0.008, lx + (e - w) * 0.008], [yy, yy],
                    color=col, lw=2, ls="--", zorder=9)
        ax.text(lx + (e - w) * 0.015, yy, txt, color=TEXT, fontsize=10 * SCALE / 2,
                va="center", zorder=9, path_effects=halo)

    # locator inset: the whole northern approaches, with this map's box on it
    ib = (93, -26, 162, 14)
    inset = fig.add_axes([0.745, 0.66, 0.24, 0.32])
    inset.set_facecolor(SEA)
    inset.set_xlim(ib[0], ib[2])
    inset.set_ylim(ib[1], ib[3])
    inset.set_aspect(1 / math.cos(math.radians(-6)))
    inset.set_xticks([])
    inset.set_yticks([])
    for sp in inset.spines.values():
        sp.set_color("white")
        sp.set_linewidth(2.5)
    for poly in rings(geo["ne_10m_land"], ib):
        inset.add_patch(Polygon(poly[0], closed=True, fc=LAND, ec="none", zorder=1))
    inset.add_patch(Rectangle((w, s), e - w, n - s, fc="none", ec="#ffd54a",
                              lw=2, zorder=2))

    fig.savefig(out_png, facecolor=SEA, dpi=100)
    plt.close(fig)


def unit_label(u):
    """'Viper 01' -> 'VIPER'; an unnamed 'ran_ddg_hobart' -> 'DDG HOBART'."""
    if u["name"]:
        return re.sub(r"\s*\d+$", "", u["name"]).upper()
    parts = u["type"].split("_")
    if len(parts) > 1 and parts[0].isalpha() and len(parts[0]) <= 5:
        parts = parts[1:]
    return " ".join(parts).upper()


def stem_for(title):
    return "sest_" + re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") + "_map"


XAML = """<Viewbox xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" \
Margin="12" HorizontalAlignment="Center" VerticalAlignment="Center">
    <Image Source="{{Binding Assets[{stem}]}}" Width="1095" Height="662"/>
</Viewbox>
"""


def targets():
    """Every hand-built SEST mission: one map each."""
    return sorted(MISSIONS.glob("SEST *.ini"))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for p in targets():
            m = parse(p)
            print(f"{p.stem}: {len(m['units'])} units")
        return

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        sys.exit("needs matplotlib: pip install matplotlib")
    geo = {name: layer(name) for name in LAYERS}

    for p in targets():
        m = parse(p)
        m["title"] = re.sub(r"^SEST (Banda|ANL Convoy) - ", "", p.stem)
        folder = MISSIONS / f"{p.stem}_briefing"
        folder.mkdir(exist_ok=True)
        stem = stem_for(m["title"])
        for old in folder.glob("*.png"):
            old.unlink()
        draw(m, folder / f"{stem}.png", geo)
        (folder / "BriefingMap_en.xml").write_bytes(XAML.format(stem=stem).encode("utf-8"))
        size = (folder / f"{stem}.png").stat().st_size // 1024
        print(f"  {p.stem}: {stem}.png ({size} KB)")


if __name__ == "__main__":
    main()
