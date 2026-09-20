#!/usr/bin/env python3
"""Build the SEST Second Screen pack: tactical map and roster on monitor 2.

Sea Power draws its entire interface inside ONE Unity window. Nothing in the
game data opens a second OS window and no launch flag splits the HUD across
displays - that would need a code mod. What the data does expose is where the
two biggest panels sit inside that window. ui/Default/Settings_UI_Tactical.ini
carries:

    [TacticalMap_Geometry]       MapSize, MapPosition            (Left, Bottom)
    [FormationManager_Geometry]  DefaultSize, MinSize, MaxSize,
                                 WindowPosition                  (Left, Top)

So the second screen is reached the way flight sims reach it: make the game
window span both monitors (NVIDIA Surround / AMD Eyefinity, or a borderless
window sized to the pair - see docs/second-screen.md), then push those panels
into the half of the window lying over monitor 2. Monitor 1 keeps the 3D view
to itself and the map stops eating a corner of it.

What this canNOT move, because the game exposes no geometry for it:

    * the bottom unit / weapons / sensors row and its context menus
    * the right-click order menus (they open at the cursor)
    * the event log and camera control windows - drag them across once, the
      game remembers per user; their position is not in mod data
    * pause, options and mission-end menus

The monitor layout is data, not a constant: data/display-layout.json is the
source of record and tools/detect-displays.ps1 rewrites it from the live
desktop, so a different pair of monitors is a re-run rather than an edit.
With mode=single-screen the pack deliberately ships vanilla geometry, which is
what you want before playing on one monitor - otherwise the map sits at an
x the window no longer has and you cannot see it.

Usage (repo root):
    python3 integration/second-screen/build_pack.py
    python3 integration/second-screen/build_pack.py --margin 24 --fm-width 420
    python3 integration/second-screen/build_pack.py --map-size 1200
    python3 integration/second-screen/build_pack.py --plan-only
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
LAYOUT = ROOT / "data" / "display-layout.json"
OUT = Path(__file__).resolve().parent / "SEST_Second_Screen"

REL = "ui/Default/Settings_UI_Tactical.ini"

# Vanilla Formation Manager bounds, for reference in messages: 320x300 default,
# 200x100 min, 400x800 max, parked at 12,12.
FM_MIN = "200,100"

INFO = """[Language_en]
Name=SEST Second Screen
Description={desc}

[Compatibility]
ApproximateVersion=0.8.2
"""


def set_key(text, key, value):
    """Replace key=... , keeping any trailing comment. Fails loudly if absent.

    Commented-out twins (#DefaultSize=150,300 sits above the live one) do not
    match: the pattern is anchored at the start of the line."""
    pattern = rf"^({re.escape(key)}=)([^\s#/]+)(.*)$"
    new, n = re.subn(pattern, lambda m: f"{m.group(1)}{value}{m.group(3)}",
                     text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"{key} not found in {REL} — upstream layout changed")
    return new


def shown(path):
    """Repo-relative when it is in the repo, verbatim when --layout points
    somewhere else; Path.relative_to raises on the latter."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_layout(path):
    """The desktop description, validated hard - bad geometry here means a
    panel parked where no monitor can show it, which is invisible in-game."""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        sys.exit(f"missing {shown(path)} — run tools/detect-displays.ps1 -Write")
    except json.JSONDecodeError as e:
        sys.exit(f"{shown(path)} is not valid JSON: {e}")

    mode = data.get("mode", "second-screen")
    if mode not in ("second-screen", "single-screen"):
        sys.exit(f"mode must be 'second-screen' or 'single-screen', got {mode!r}")

    regions = data.get("regions") or []
    if not regions:
        sys.exit(f"{shown(path)}: no regions listed")
    for r in regions:
        if not isinstance(r, dict):
            sys.exit(f"{shown(path)}: every region must be an object, got {r!r}")
        for field in ("id", "role", "x", "y", "width", "height"):
            if field not in r:
                sys.exit(f"region {r.get('id', '?')!r} is missing {field!r}")
        for field in ("x", "y", "width", "height"):
            if not isinstance(r[field], int) or isinstance(r[field], bool):
                sys.exit(f"region {r['id']!r}: {field} must be a whole number of "
                         f"pixels, got {r[field]!r}")
        if r["width"] <= 0 or r["height"] <= 0:
            sys.exit(f"region {r['id']!r} has a non-positive size")

    panels = [r for r in regions if r["role"] == "panels"]
    if mode == "second-screen" and len(panels) != 1:
        sys.exit(f"expected exactly one region with role 'panels', found {len(panels)}")

    # The window is the bounding box of every region. When the geometry is
    # going to be used, the regions must also tile that box exactly: a gap
    # means part of the window is over no monitor at all, and an overlap means
    # the recorded layout is not a real desktop.
    left = min(r["x"] for r in regions)
    top = min(r["y"] for r in regions)
    right = max(r["x"] + r["width"] for r in regions)
    bottom = max(r["y"] + r["height"] for r in regions)
    covered = sum(r["width"] * r["height"] for r in regions)
    if mode == "second-screen" and covered != (right - left) * (bottom - top):
        # Only fatal when the geometry is about to be used: in single-screen
        # mode the pack ships vanilla either way, and a staggered desktop -
        # which is exactly what the detector records when it gives up - must
        # not take the whole build down with it.
        sys.exit("regions do not tile a rectangle (gap or overlap) — the game "
                 "window cannot span this desktop; see docs/second-screen.md")

    window = {"left": left, "top": top,
              "width": right - left, "height": bottom - top}
    return data, mode, regions, panels[0] if panels else None, window


def plan(panel, window, margin, fm_width, fm_max_height, map_size):
    """Pixel geometry for the two movable panels, in game-window coordinates.

    The window's origin is the top-left of the whole desktop rectangle, so a
    region's window-space x is its desktop x minus the window's. MapPosition
    counts from the BOTTOM edge, WindowPosition from the top - the two keys
    disagree in vanilla and the game keeps that convention."""
    px = panel["x"] - window["left"]
    py = panel["y"] - window["top"]

    usable_h = panel["height"] - 2 * margin
    # margin | map | margin | roster | margin, all inside the panel region.
    avail_w = panel["width"] - 3 * margin - fm_width
    side = map_size if map_size else min(usable_h, avail_w)

    if side < 200:
        sys.exit(f"panel region {panel['id']!r} ({panel['width']}x{panel['height']}) "
                 f"leaves only {side}px for the map — lower --fm-width or --margin")
    if side > avail_w:
        sys.exit(f"--map-size {side} does not fit beside a {fm_width}px roster "
                 f"in {panel['width']}px (max {avail_w})")
    if side > usable_h:
        sys.exit(f"--map-size {side} is taller than the {panel['height']}px region "
                 f"(max {usable_h})")

    map_left = px + margin
    # Distance from the window's bottom edge up to the region's bottom margin.
    map_bottom = window["height"] - (py + panel["height"]) + margin
    # Roster right-aligned to the outer edge, so the map sits nearest the 3D
    # view and the strip between them stays free for the event log window.
    fm_left = px + panel["width"] - margin - fm_width
    fm_top = py + margin
    fm_height = min(usable_h, fm_max_height)

    if map_left + side > fm_left:
        sys.exit("map and roster overlap — lower --map-size or --fm-width")

    return {
        "MapSize": f"{side},{side}",
        "MapPosition": f"{map_left},{map_bottom}",
        "DefaultSize": f"{fm_width},{fm_height}",
        "MinSize": FM_MIN,
        "MaxSize": f"{fm_width},{usable_h}",
        "WindowPosition": f"{fm_left},{fm_top}",
    }


def describe(mode, panel, window, geometry):
    if mode == "single-screen":
        return ("Parks the tactical map and the Formation Manager window on the second "
                "monitor when the game window spans both. Currently built in single-screen "
                "mode, so it ships vanilla geometry and changes nothing: re-run "
                "tools/detect-displays.ps1 -Write and rebuild after plugging the second "
                "monitor back in.")
    mw, mh = window["width"], window["height"]
    return (f"Parks the tactical map ({geometry['MapSize'].split(',')[0]}px square) and the "
            f"Formation Manager window on the '{panel['id']}' monitor, for a game window "
            f"spanning {mw}x{mh}. The 3D view keeps the other monitor to itself. REQUIRES a "
            f"window that actually spans both screens (Surround/Eyefinity, or a borderless "
            f"window sized to the pair) - on a single {panel['width']}px-wide screen the map "
            f"lands off-view. The bottom unit row, right-click order menus and the pause "
            f"menus stay on the main screen: the game exposes no geometry for them. Rebuild "
            f"in single-screen mode before playing on one monitor.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--layout", type=Path, default=LAYOUT,
                    help="desktop description (default data/display-layout.json)")
    ap.add_argument("--margin", type=int, default=None,
                    help="gap from the region edges in px (default: the layout file's)")
    ap.add_argument("--fm-width", type=int, default=400,
                    help="Formation Manager width in px (vanilla max 400)")
    ap.add_argument("--fm-height", type=int, default=1200,
                    help="height it opens at; it can still be dragged to the region height")
    ap.add_argument("--map-size", type=int, default=0,
                    help="force the tactical map's square side in px (default: as large "
                         "as the region allows beside the roster)")
    ap.add_argument("--plan-only", action="store_true",
                    help="print the computed geometry and write nothing")
    args = ap.parse_args()

    src = VANILLA / REL
    if not src.exists():
        sys.exit(f"vanilla file missing (re-export mods-source?): {src}")
    text = src.read_text(encoding="utf-8-sig", errors="replace")

    data, mode, _regions, panel, window = load_layout(args.layout)
    margin = args.margin if args.margin is not None else int(data.get("margin", 12))

    if mode == "second-screen":
        geometry = plan(panel, window, margin, args.fm_width, args.fm_height, args.map_size)
        for key, value in geometry.items():
            text = set_key(text, key, value)
        summary = (f"panels on {panel['id']} ({panel['width']}x{panel['height']} at "
                   f"{panel['x']},{panel['y']}), window {window['width']}x{window['height']}, "
                   + ", ".join(f"{k}={v}" for k, v in geometry.items()))
    else:
        geometry = {}
        summary = "single-screen mode: vanilla geometry, pack is a no-op"

    if args.plan_only:
        print(summary)
        if mode == "second-screen":
            print(f"launch options: -screen-fullscreen 0 -popupwindow "
                  f"-screen-width {window['width']} -screen-height {window['height']}")
        return

    (OUT / "ui" / "Default").mkdir(parents=True, exist_ok=True)
    (OUT / REL).write_text(text, encoding="utf-8")
    (OUT / "_info.ini").write_text(
        INFO.format(desc=describe(mode, panel, window, geometry)), encoding="utf-8")

    # Sanity: the UI file is a whole-file override like the unit inis, so a
    # truncated copy would silently drop every key it no longer carries.
    out_lines = len((OUT / REL).read_text(encoding="utf-8-sig").splitlines())
    src_lines = len(text.splitlines())
    if out_lines != src_lines or out_lines < 150:
        sys.exit(f"output looks truncated: {out_lines} lines vs {src_lines}")

    print(f"built {OUT.relative_to(ROOT)}: {summary}, {out_lines} lines (complete file)")


if __name__ == "__main__":
    main()
