#!/usr/bin/env python3
"""Draw the briefing map for every hand-built SEST mission in this folder.

The briefing screen has two panes. The left one is text and the game fills it
from the mission's own Description, so it always worked. The right one is the
map, and the game draws it only from `<mission>_briefing/BriefingMap_en.xml`
beside the .ini. No SEST mission shipped that folder, so the right pane was
blank on every one of them. `briefing_maps.py` is the renderer (Pillow, with
Natural Earth coastlines fetched once into ~/.cache/sest-naturalearth); the
campaign builder uses the same module for the campaign's own missions. The
PNGs are committed, so installing never needs Pillow or the network.

    python3 integration/missions/build_briefing_maps.py          # all SEST missions
    python3 integration/missions/build_briefing_maps.py --list   # what it would draw
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import briefing_maps as bm  # noqa: E402

MISSIONS = Path(__file__).resolve().parent

SERIES = {"Banda": "SEST BANDA", "NF3": "SEST NORTHERN FRONT III",
          "ANL Convoy": "SEST ANL CONVOY"}


def targets():
    """Every hand-built SEST mission, including scenarios/: one map each."""
    return sorted(MISSIONS.rglob("SEST *.ini"))


def split(stem):
    m = re.match(r"^SEST (Banda|NF3|ANL Convoy) - (.+)$", stem)
    if m:
        return m.group(2), SERIES[m.group(1)]
    return stem.replace("SEST ", "", 1), "SEST"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for p in targets():
            m = bm.parse(p)
            print(f"{p.stem}: {len(m['units'])} units")
        return

    geo, reason = bm.available()
    if geo is None:
        sys.exit(f"cannot draw: {reason}")
    for p in targets():
        title, series = split(p.stem)
        folder = p.parent / f"{p.stem}_briefing"       # beside the .ini, scenarios/ included
        stem = bm.render(p, folder, title, geo, series=series)
        size = (folder / f"{stem}.png").stat().st_size // 1024
        print(f"  {p.stem}: {stem}.png ({size} KB)")


if __name__ == "__main__":
    main()
