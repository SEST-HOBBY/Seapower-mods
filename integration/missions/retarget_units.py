#!/usr/bin/env python3
"""Repoint mission unit ids that no longer exist onto their replacements.

Unsubscribing a mod does not just remove a mod: every mission that fielded
one of its units now names a type nothing defines. The game cannot place the
unit, and a mission written around it quietly loses whatever that unit was
doing - a SEAD escort that never appears is not a smaller mission, it is a
broken one.

That is what happened to usn_ea-18g_2020s. Its only provider was the
deprecated F/A-18E/F (3426791311), unsubscribed in the 2026-09-20 export, and
no other mod ships that id. Thirteen live missions still field it.

Each retarget is a judgement, so each one is recorded with the evidence that
made it safe rather than being a blind rename:

  usn_ea-18g_2020s -> usn_ea-18g_2020
      Same aircraft, same lineage, same NGJ meshes - the F/A-18E/F mod's
      Growler and US Naval Aviation's are the "2020s"/"2020" pair, and
      SEST_Growler_NGJ_MALICE already patched both identically. The loadouts
      line up exactly: the retired unit declared AvailableLoadouts=SEAD and
      nothing else, and the replacement declares SEAD plus three SEST fits,
      so every mission reference (all of them SEAD) resolves unchanged.

  jp_sh-60k -> jmsdf_sh-60k, jp_sh-60j -> jmsdf_sh-60j   (applied by hand)
      Euromod JMSDF renamed its Seahawks on 19 Sep 2026. Its
      aircraft_names.ini names only the jmsdf_ ids, and mods-source holds 43
      of its files against the 37 the last export copied: the jp_ unit and
      squadron files are leftovers the exporter never deleted. Each jmsdf_
      airframe offers every loadout its jp_ twin did, plus Transport, and
      ships Squadron1, so the missions' `jmsdf_sh-60k=Squadron1,1` air groups
      resolve unchanged. The six live NORTHERN FRONT saves and
      scenarios/SEST NF3 - Boomer Hunt were edited whole-token instead of
      through RETARGET, because the guard in main() refuses an old id that
      mods-source still defines. Add the pair to RETARGET once an export with
      the deletion mirror has removed the jp_ files.

Scope: live missions only. The timestamped *backup-*.ini files are snapshots
of a mission at a moment, and rewriting them would destroy the only thing
they are for.

    python3 integration/missions/retarget_units.py            # report
    python3 integration/missions/retarget_units.py --write    # apply

Idempotent: a mission already retargeted reports no change.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = ROOT / "integration" / "missions"
MODS = ROOT / "mods-source"

# retired id -> replacement id
RETARGET = {
    "usn_ea-18g_2020s": "usn_ea-18g_2020",
}

# (unit id, loadout the mission asks for) -> loadout it should ask for.
#
# Separate from RETARGET because it is a different kind of repair: the unit
# resolves, the FIT does not. Only one case, and it predates the retarget -
# the retired Growler declared AvailableLoadouts=SEAD and nothing else, so
# "chapter 4 - Kill KuznetsovCUSTOM" was already asking two of its Growlers
# for an AntiShip fit that no Growler in this collection has ever had. The
# aircraft would have fallen back on load. SEAD is what a Growler is for and
# what both the retired unit and its replacement declare, so that is where
# the two entries point now.
RELOADOUT = {
    ("usn_ea-18g_2020", "AntiShip"): "SEAD",
}


def defined_ids():
    """Every unit id the collection can still place, packs included."""
    out = set()
    for root in (MODS, ROOT / "integration"):
        for f in root.rglob("*.ini"):
            if f.parent.name in ("aircraft", "vessels", "submarines",
                                 "land_units", "biologic"):
                out.add(f.stem)
    return out


def live_missions():
    return sorted(p for p in MISSIONS.glob("*.ini")
                  if not re.search(r"backup-\d{8}-\d{6}", p.name))


def reloadout(text):
    """Repoint a LoadoutVariant the unit does not offer, unit by unit.

    Scoped to the entry it belongs to: a mission is a flat file where the
    same LoadoutVariant= key appears under dozens of units, so this walks
    entries and only rewrites the line that follows the Type= it is keyed
    on. Flight-deck ready-up tasks name unit and loadout on one line and are
    handled directly."""
    counts, out, unit = {}, [], None
    for line in text.splitlines(keepends=True):
        s = line.strip()
        m = re.match(r"Type=(\S+)$", s)
        if m:
            unit = m.group(1)
        elif s.startswith("["):
            unit = None
        lv = re.match(r"LoadoutVariant=(.+)$", s)
        if lv and unit and (unit, lv.group(1).strip()) in RELOADOUT:
            new = RELOADOUT[(unit, lv.group(1).strip())]
            key = f"{unit} loadout {lv.group(1).strip()} -> {new}"
            counts[key] = counts.get(key, 0) + 1
            line = line.replace(f"LoadoutVariant={lv.group(1).strip()}",
                                f"LoadoutVariant={new}")
        fd = re.match(r"(FlightDeck_ReadyUpTask\d+=)(\S+?),([^,]+),([^,]+),(.*)$", s)
        if fd and (fd.group(2), fd.group(3)) in RELOADOUT:
            new = RELOADOUT[(fd.group(2), fd.group(3))]
            key = f"{fd.group(2)} ready-up {fd.group(3)} -> {new}"
            counts[key] = counts.get(key, 0) + 1
            line = line.replace(f",{fd.group(3)},", f",{new},", 1)
        out.append(line)
    return "".join(out), counts


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="apply the changes")
    args = ap.parse_args()

    known = defined_ids()
    # Refuse to retarget onto something that is not there either - that would
    # turn one broken reference into another and report success doing it.
    for old, new in RETARGET.items():
        if new not in known:
            sys.exit(f"replacement {new!r} for {old!r} is not defined by any mod "
                     "or pack - re-check the retarget table")
        if old in known:
            sys.exit(f"{old!r} is defined again (re-subscribed?) - drop it from "
                     "the retarget table rather than rewriting missions")

    touched, total = [], 0
    for m in live_missions():
        text = original = m.read_text(encoding="utf-8", errors="replace")
        counts = {}
        for old, new in RETARGET.items():
            # Whole-token only: usn_ea-18g_2020s must not match inside a
            # longer id, and the replacement must not be re-replaced.
            text, n = re.subn(rf"(?<![\w-]){re.escape(old)}(?![\w-])", new, text)
            if n:
                counts[f"{old} -> {new}"] = n
        text, extra = reloadout(text)
        counts.update(extra)
        if text == original:
            continue
        total += sum(counts.values())
        touched.append((m.name, counts))
        if args.write:
            m.write_text(text, encoding="utf-8")

    if not touched:
        print("every live mission already resolves - nothing to retarget")
        return
    verb = "retargeted" if args.write else "would retarget"
    for name, counts in touched:
        detail = ", ".join(f"{k} x{v}" for k, v in counts.items())
        print(f"  {name}: {detail}")
    print(f"\n{verb} {total} reference(s) across {len(touched)} live mission(s)"
          + ("" if args.write else " - re-run with --write to apply"))


if __name__ == "__main__":
    main()
