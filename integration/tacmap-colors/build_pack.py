#!/usr/bin/env python3
"""Build the SEST TacMap Colors pack: readable waypoint lines.

Vanilla draws waypoint lines as ARGB 100,0,0,220 - a dark blue at 39% alpha -
which turns into an unreadable dark tangle once a mission has a lot of
routes on screen. This rewrites the tactical map's colour block so the lines
are solid black or solid white, and can thicken them at the same time.

IMPORTANT - THERE IS NO AIR/GROUND SPLIT. The game exposes exactly one
waypoint line colour (WaypointsLineColor) plus a night variant and a
selected-waypoint colour. Nothing in ui/ distinguishes an aircraft's route
from a ship's or a ground unit's, so a per-domain colour is not possible
through data alone - it would need a code mod.

What CAN be separated is day vs night: the game swaps to the Night* set
automatically, so black is used by day and white at night by default, which
keeps the lines readable against both map backgrounds.

The pack ships the whole file, so it also has to carry every key the game
reads. It is built from the game's own current file, which is how it follows
a game update. In October 2026 a beta, Build 261026, read 32 tactical map
keys (28 colours, 4 thicknesses) that the released game's file did not have
yet, and logged "UI_Parameters: Settings_UI_Tactical.ini has no map setting
'<key>'" for each one missing from the pack's copy. BETA_KEYS holds them
with that beta's default values, and the builder appends any the export
lacks to the end of their sections. Since Sea Power 0.9.0 (11 Nov 2026) the
game's file has all 32 itself, so none is appended and the table only
guards an older export.

Usage (repo root):
    python3 integration/tacmap-colors/build_pack.py                  # black day / white night
    python3 integration/tacmap-colors/build_pack.py --waypoints white
    python3 integration/tacmap-colors/build_pack.py --waypoints black --thickness 2
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VANILLA = ROOT / "mods-source" / "_vanilla" / "original"
OUT = Path(__file__).resolve().parent / "SEST_TacMap_Colors"

REL = "ui/Default/Settings_UI_Tactical.ini"

# ARGB, fully opaque.
BLACK = "255,0,0,0"
WHITE = "255,255,255,255"

# The beta's additions (Build 261026, ui/Default/Settings_UI_Tactical.ini of
# the 28 Oct 2026 export), with the beta's default values, by section.
BETA_KEYS = {
    "TacticalMap_Colors": [
        ("InvisibleColor", "0,0,0,0"),
        ("WeaponNoEscapeRangeColor", "255,255,0,170"),
        ("NightWeaponNoEscapeRangeColor", "255,255,0,170"),
        ("FiringArcColor", "204,255,158,26"),
        ("NightFiringArcColor", "224,255,179,61"),
        ("DrawingPresetDefault", "255,0,0,0"),
        ("DrawingPresetRed", "255,204,0,0"),
        ("DrawingPresetBlue", "255,0,0,204"),
        ("DrawingPresetGreen", "255,0,170,0"),
        ("DrawingPresetYellow", "255,204,170,0"),
        ("DrawingPresetOrange", "255,221,102,0"),
        ("DrawingPresetCyan", "255,0,153,170"),
        ("DrawingPresetMagenta", "255,170,0,153"),
        ("DrawingPresetWhite", "255,68,68,68"),
        ("NightDrawingPresetDefault", "255,255,255,255"),
        ("NightDrawingPresetRed", "255,255,102,102"),
        ("NightDrawingPresetBlue", "255,102,153,255"),
        ("NightDrawingPresetGreen", "255,102,255,102"),
        ("NightDrawingPresetYellow", "255,255,255,102"),
        ("NightDrawingPresetOrange", "255,255,170,68"),
        ("NightDrawingPresetCyan", "255,102,255,255"),
        ("NightDrawingPresetMagenta", "255,255,102,255"),
        ("NightDrawingPresetWhite", "255,255,255,255"),
        ("SeekerHiddenColor", "0,0,0,0"),
        ("PlayAreaFillColor", "94,10,14,20"),
        ("PlayAreaStrokeColor", "179,224,87,76"),
        ("DrawingPolygonFillColor", "170,170,0,0"),
        ("DrawingEraseHighlightColor", "255,255,0,0"),
    ],
    "TacticalMap_Geometry": [
        ("PlayAreaStrokeThickness", "2"),
        ("SeekerConeStrokeThickness", "2"),
        ("JamConeThickness", "2"),
        ("WeaponWireThickness", "1"),
    ],
}
BETA_NOTE = "#Keys the beta Build 261026 read before the game's own file had them, at that beta's defaults"

INFO = """[Language_en]
Name=SEST TacMap Colors
Description={desc}

[Compatibility]
ApproximateVersion=0.9.0
"""


def set_key(text, key, value):
    """Replace key=... , keeping any trailing comment. Fails loudly if absent."""
    pattern = rf"^({re.escape(key)}=)([^\s#/]+)(.*)$"
    new, n = re.subn(pattern, lambda m: f"{m.group(1)}{value}{m.group(3)}",
                     text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"{key} not found in {REL} — upstream layout changed")
    return new


def add_beta_keys(text):
    """Append each BETA_KEYS entry the file lacks to the end of its section.

    Returns the new text and the number of keys added. A key already present
    (a newer export) is left exactly as the export has it.
    """
    lines = text.splitlines()
    present = {m.group(1) for m in (re.match(r"^([A-Za-z0-9_]+)=", ln) for ln in lines) if m}
    added = 0
    for section, keys in BETA_KEYS.items():
        missing = [(k, v) for k, v in keys if k not in present]
        if not missing:
            continue
        start = next((i for i, ln in enumerate(lines) if ln.strip() == f"[{section}]"), None)
        if start is None:
            sys.exit(f"[{section}] not found in {REL} — upstream layout changed")
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("[")), len(lines))
        # Insert before the blank lines that close the section.
        insert = end
        while insert > start + 1 and lines[insert - 1].strip() == "":
            insert -= 1
        block = [BETA_NOTE] + [f"{k}={v}" for k, v in missing]
        lines[insert:insert] = block
        added += len(missing)
    return "\n".join(lines) + "\n", added


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--waypoints", choices=("black", "white", "auto"), default="auto",
                    help="line colour: black, white, or auto (black by day, white by night)")
    ap.add_argument("--thickness", type=float, default=1.5,
                    help="waypoint line thickness (vanilla 1)")
    args = ap.parse_args()

    src = VANILLA / REL
    if not src.exists():
        sys.exit(f"vanilla file missing (re-export mods-source?): {src}")
    text = src.read_text(encoding="utf-8-sig", errors="replace")

    if args.waypoints == "black":
        day = night = BLACK
    elif args.waypoints == "white":
        day = night = WHITE
    else:                       # auto: whichever reads better on each background
        day, night = BLACK, WHITE

    # The day/night pair the game swaps between automatically.
    text = set_key(text, "WaypointsLineColor", day)
    text = set_key(text, "NightWaypointsLineColor", night)
    # Keep the selected route obviously distinct from the rest.
    text = set_key(text, "WaypointSelectedColor", "255,255,0,0")
    text = set_key(text, "NightWaypointSelectedColor", "255,255,80,80")
    # Formation tethers share the tangle; make them faint so routes dominate.
    text = set_key(text, "FormationMembershipLineColor", "48,0,0,255")
    text = set_key(text, "NightFormationMembershipLineColor", "48,107,207,255")
    text = set_key(text, "WaypointLineThickness", f"{args.thickness:g}")
    text, beta_added = add_beta_keys(text)

    (OUT / "ui" / "Default").mkdir(parents=True, exist_ok=True)
    (OUT / REL).write_text(text, encoding="utf-8")
    scheme = ("black by day and white at night" if args.waypoints == "auto"
              else f"solid {args.waypoints}")
    (OUT / "_info.ini").write_text(INFO.format(
        desc=("Makes tactical map waypoint lines readable: vanilla draws them at 39 percent "
              f"alpha which turns into a dark tangle on a busy map. Lines are now {scheme}, "
              f"fully opaque, at {args.thickness:g}x thickness, with the selected route in red "
              "and formation tethers faded back. Note the game has only ONE waypoint line "
              "colour - air, surface and ground routes cannot be coloured separately through "
              "data. " + (
                  f"Carries {beta_added} map keys a later game build reads, at that build's "
                  "defaults, so it logs no missing setting. " if beta_added else
                  "It is the game's current file with those colours changed, so it carries "
                  "every map key the game reads. ")
              + "Place ABOVE nothing in particular; it only overrides the vanilla UI file.")),
        encoding="utf-8")

    # Sanity: we shipped the whole file, not a fragment (unit inis are
    # whole-file overrides and the UI file behaves the same way).
    out_lines = len((OUT / REL).read_text(encoding="utf-8-sig").splitlines())
    src_lines = len(text.splitlines())
    if out_lines != src_lines or out_lines < 150:
        sys.exit(f"output looks truncated: {out_lines} lines vs {src_lines}")

    print(f"built {OUT.relative_to(ROOT)}: waypoints {scheme}, "
          f"thickness {args.thickness:g}, {out_lines} lines (complete file), "
          f"{beta_added} beta keys added")


if __name__ == "__main__":
    main()
