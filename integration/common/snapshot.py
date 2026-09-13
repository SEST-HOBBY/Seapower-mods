"""Is mods-source behind the catalog, and which mods is it missing?

A builder that reads a workshop mod has two very different reasons to find
nothing there, and it must not treat them alike:

  - THE SNAPSHOT IS STALE. The mod is subscribed and in the catalog as active,
    but tools/export-mod-configs.ps1 has not been run since. The game is fine -
    it reads Steam's workshop folder, not this repo - and the builder should
    say what it is leaving out and carry on.
  - THE REFERENCE IS WRONG. Every active mod IS exported and the file still is
    not there. That is a typo or a dead id, and the build must fail.

Telling them apart by hand would mean a list of "expected to be missing" ids
that someone has to remember to prune. This computes it instead: the catalog
knows which mods are active, and the disk knows which are exported. The
difference is the staleness, and it empties itself the moment the next export
lands.

This mattered on 2026-09-13. An export taken while the B-52H (3741944366) and
B-1B (3652097318) were briefly unsubscribed pruned both from mods-source. The
user re-subscribed the same day, so both work in game, but SEST_B52_ARRW and
SEST_RAAF_Bases hard-failed the whole build over files no longer on disk.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"


def stale_mods():
    """-> {workshop_id: title} for catalog mods that are active but unexported."""
    catalog = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))
    return {m["workshop_id"]: m["title"] for m in catalog["mods"]
            if m.get("status") == "active" and m.get("workshop_id")
            and not (MODS / m["workshop_id"]).is_dir()}


def explain(ids=None):
    """One line naming the stale mods, for a builder's skip notice."""
    stale = stale_mods()
    if ids is not None:
        stale = {k: v for k, v in stale.items() if k in ids}
    if not stale:
        return ""
    names = ", ".join(f"{t} ({i})" for i, t in sorted(stale.items(), key=lambda kv: kv[1]))
    return (f"{names} " + ("is" if len(stale) == 1 else "are")
            + " subscribed and active in the catalog but not in mods-source - "
              "re-run tools/export-mod-configs.ps1 to restore")


def missing_is_stale(workshop_id):
    """True if this mod's absence is a stale snapshot rather than a bad id."""
    return workshop_id in stale_mods()
