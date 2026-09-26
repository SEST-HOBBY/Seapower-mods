"""Is mods-source behind the catalog, and which mods is it missing?

A reference that resolves to nothing has two very different causes, and a
tool must not report them alike:

  - THE SNAPSHOT IS STALE. The mod is subscribed and in the catalog as active,
    but tools/export-mod-configs.ps1 has not been run since. The game is fine -
    it reads Steam's workshop folder, not this repo - and the report should
    say which mods are missing rather than blame the reference.
  - THE REFERENCE IS WRONG. Every active mod IS exported and the file still is
    not there. That is a typo or a dead id.

Telling them apart by hand would mean a list of "expected to be missing" ids
that someone has to remember to prune. This computes it instead: the catalog
knows which mods are installed, and the disk knows which are exported. The
difference is the staleness, and it empties itself the moment the next export
lands.

This mattered on 2026-09-13. An export taken while the B-52H (3741944366) and
B-1B (3652097318) were briefly unsubscribed pruned both from mods-source. The
user re-subscribed the same day, so both work in game, but SEST_B52_ARRW and
SEST_RAAF_Bases hard-failed the whole build over files no longer on disk.

The same export pruned two more, the SAAB AEW&C pack (3673250557) and the Type
003 Fujian (3663564190), which were then judged unsubscribed for good and had
their references repaired by hand. The 2026-09-16 export returned all four.
So "absent from mods-source" never proved anything about the Steam account,
and this module still does not claim that it does.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"


def stale_mods():
    """-> {workshop_id: title} for catalog mods that are installed but unexported.

    Installed means active, deprecated or wip: the last two describe a mod's
    quality, not whether it is on disk, so they count here. unsubscribed is
    the status that means "do not expect a folder".
    """
    catalog = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))
    return {m["workshop_id"]: m["title"] for m in catalog["mods"]
            if m.get("status") in {"active", "deprecated", "wip"} and m.get("workshop_id")
            and not (MODS / m["workshop_id"]).is_dir()}
