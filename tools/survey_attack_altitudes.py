#!/usr/bin/env python3
"""Survey attack-altitude bands across the winning copy of every ammunition id.

Produces the figures integration/intercept-model/build_patch.py cites, and the
harm classification behind its "two rounds need fixing" claim. Committed so the
next mods-source export can re-run it rather than take those numbers on trust:
a new mod, or a reorder, can move a band into the danger set without any file
this repo owns changing.

Why a dedicated tool. Restoring vanilla's ammunition/damage.ini arms
InterceptChanceOutOfAltitudeOverride=0.05, a hard 5% ceiling on any intercept
where the target sits outside the round's MinAttackAltitude/MaxAttackAltitude
band. A round whose band excludes what it is actually shot at becomes a dead
weapon. This finds those rounds.

Two things it does that a plain grep cannot:

  - Load order. Only the WINNING copy of an id matters; ammunition/ is a
    whole-file override (docs/design-notes.md). Resolution goes through the
    repo's own winning_file(), so the answer matches what the game loads.
  - #!alias inheritance. 80 ammunition files are alias stubs, and an alias
    resolves its base through the load order too, so a round can carry a band
    it never literally declares - the ESSM, RAM and SM-2 families all do, and
    one composes its band across two mods. A flat scan misses 17 anti-air
    rounds and miscounts the one-sided total.

    python3 tools/survey_attack_altitudes.py            # summary + harm classes
    python3 tools/survey_attack_altitudes.py --json     # every banded round
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "integration" / "missions"))
import refine_civ_traffic as R  # noqa: E402  (needs the path above)

MODS = ROOT / "mods-source"

# A floor this high means the round is scored out-of-altitude against ordinary
# air targets; a ceiling this low means the same for anything at altitude.
HIGH_FLOOR_FT = 1000
LOW_CEILING_FT = 5000


def ammunition_ids():
    """Every ammunition id anyone ships, workshop mods AND the SEST packs.

    Discovering names only under mods-source/ is not enough: a SEST pack may
    introduce an entirely NEW round rather than override an existing one, and
    resolution cannot find a name nothing told it to look for. Five ids exist
    only in SEST packs (sest_aim-424, sest_agr-30, sest_agr-30_pod,
    sest_agr-20er, sest_apkws_er), two of them anti-air. An earlier version of
    this tool missed all five."""
    ids = set()
    for d in MODS.iterdir():
        if d.is_dir() and (d / "ammunition").is_dir():
            ids |= {f.name for f in (d / "ammunition").glob("*.ini")}
    ids |= {f.name for f in (MODS / "_vanilla/original/ammunition").glob("*.ini")}
    for pack in local_packs():
        amm = pack / "ammunition"
        if amm.is_dir():
            ids |= {f.name for f in amm.glob("*.ini")}
    return ids


def local_packs():
    """Built pack directories, from the local_packs registry plus the
    consolidated dist that is what actually deploys."""
    out = []
    catalog = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))
    for entry in catalog.get("local_packs", []):
        d = ROOT / entry["source"] / entry["folder"]
        if d.is_dir():
            out.append(d)
    dist = ROOT / "integration" / "dist" / "SEST_Integration"
    if dist.is_dir():
        out.append(dist)
    return out


def kv(text):
    """First occurrence of each key wins, matching how the engine reads a file
    top-down. damage.ini and the round files have sections but do not reuse a
    key across them, so a flat map is safe."""
    d = {}
    for ln in text.splitlines():
        s = ln.split("//", 1)[0].strip()
        if not s or s[0] in "#;[":
            continue
        if "=" in s:
            k, v = s.split("=", 1)
            d.setdefault(k.strip(), v.strip())
    return d


_cache = {}


def resolve(rel, chain=()):
    """Merged key map for an ammunition path, following #!alias through the
    load order. The stub's own keys win over the inherited ones."""
    if rel in _cache:
        return _cache[rel]
    if rel in chain:
        return {"__cycle__": rel}
    won = R.winning_file(rel)
    if not won:
        return {}
    text = Path(won).read_text(encoding="utf-8-sig", errors="replace")
    own = kv(text)
    own["__winner__"] = Path(won).parts[-3]
    m = re.match(r"^\s*#!alias\s+(\S+)", text)
    if m:
        base = resolve(m.group(1).strip(), chain + (rel,))
        merged = dict(base)
        merged.update(own)
        merged["__alias_of__"] = m.group(1).strip()
        merged["__inherited_band__"] = any(
            k in base and k not in own
            for k in ("MinAttackAltitude", "MaxAttackAltitude"))
        own = merged
    _cache[rel] = own
    return own


def feet(value):
    """Altitude as a float, or the raw string if it will not parse. A value the
    game might read differently from us (a thousands separator, say) must stay
    visible rather than being silently normalised."""
    if value is None:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return value


# The two of the eight global keys that HAVE a per-round form. A round that
# declares neither inherits both from damage.ini, which is what makes it a valid
# probe for "does a deleted global fall back to vanilla's value?".
PENALTY_KEYS = ("InterceptSpeedPenaltyMultiplier", "InterceptOutOfAltitudePenalty")


def survey():
    rows, probes, stats = [], [], dict.fromkeys(
        ("total", "alias", "cycles", "aaw", "banded", "onesided", "inherited",
         "inherits_speed", "inherits_alt", "inherits_both"), 0)
    for name in sorted(ammunition_ids()):
        d = resolve(f"ammunition/{name}")
        if not d:
            continue
        stats["total"] += 1
        if "__cycle__" in d:
            stats["cycles"] += 1
            continue
        if d.get("__alias_of__"):
            stats["alias"] += 1
        if d.get("TargetType") != "AAW" and d.get("SecondaryTargetType") != "AAW":
            continue
        stats["aaw"] += 1
        inh_speed = PENALTY_KEYS[0] not in d
        inh_alt = PENALTY_KEYS[1] not in d
        stats["inherits_speed"] += inh_speed
        stats["inherits_alt"] += inh_alt
        stats["inherits_both"] += (inh_speed and inh_alt)
        mn, mx = d.get("MinAttackAltitude"), d.get("MaxAttackAltitude")
        if inh_speed and inh_alt and mn is not None and mx is not None:
            probes.append({"id": name[:-4], "winner": d.get("__winner__"),
                           "min": mn, "max": mx})
        if mn is None and mx is None:
            continue
        stats["banded"] += 1
        if (mn is None) != (mx is None):
            stats["onesided"] += 1
        if d.get("__inherited_band__"):
            stats["inherited"] += 1
        rows.append({
            "id": name[:-4], "winner": d.get("__winner__"),
            "alias_of": d.get("__alias_of__"),
            "inherited": bool(d.get("__inherited_band__")),
            "min": mn, "max": mx,
            "auto": d.get("AutoAttackOutsideAltitudes"),
            "secondary": d.get("SecondaryTargetType"),
            "land": d.get("LandAttackCapability"),
        })
    return rows, probes, stats


def classify(rows):
    """The four ways a band can make the clamp bite. Anything here is a
    candidate override for SEST_Intercept_Model."""
    out = {"malformed": [], "inverted": [], "high_floor": [], "low_ceiling": []}
    for r in rows:
        lo, hi = feet(r["min"]), feet(r["max"])
        if isinstance(lo, str) or isinstance(hi, str) \
                or (r["min"] and "," in r["min"]) or (r["max"] and "," in r["max"]):
            out["malformed"].append(r)
            continue
        if lo is not None and hi is not None and lo >= hi:
            out["inverted"].append(r)
        if lo is not None and lo >= HIGH_FLOOR_FT:
            out["high_floor"].append(r)
        if hi is not None and hi <= LOW_CEILING_FT:
            out["low_ceiling"].append(r)
    return out


def main():
    rows, probes, stats = survey()
    if "--json" in sys.argv:
        print(json.dumps({"stats": stats, "rows": rows, "probes": probes}, indent=1))
        return

    print("winning ammunition ids resolved   ", stats["total"])
    print("  of which #!alias stubs          ", stats["alias"])
    print("  alias cycles (should be 0)      ", stats["cycles"])
    print("anti-air-capable rounds           ", stats["aaw"])
    print("  declaring an altitude band      ", stats["banded"])
    print("    band inherited via alias      ", stats["inherited"])
    print("    one side of the band only     ", stats["onesided"])
    print("  inheriting the restored penalties:")
    print("    InterceptSpeedPenaltyMultiplier", stats["inherits_speed"])
    print("    InterceptOutOfAltitudePenalty  ", stats["inherits_alt"])
    print("    both, and a two-sided band     ", len(probes),
          f"(of {stats['inherits_both']} inheriting both)")

    groups = classify(rows)
    for label, key in (("MALFORMED (would not parse as written)", "malformed"),
                       ("INVERTED or EMPTY (min >= max)", "inverted"),
                       (f"HIGH FLOOR (min >= {HIGH_FLOOR_FT} ft)", "high_floor"),
                       (f"LOW CEILING (max <= {LOW_CEILING_FT} ft)", "low_ceiling")):
        found = groups[key]
        print(f"\n{label}: {len(found)}")
        for r in sorted(found, key=lambda r: str(r["min"])):
            tag = "  [band inherited]" if r["inherited"] else ""
            print(f"   {r['id']:28} {r['winner']:16} "
                  f"min={str(r['min']):>8} max={str(r['max']):>9}{tag}")

    print("\nA round listed above is not automatically a defect - a dedicated\n"
          "ballistic-missile interceptor SHOULD have a high floor. Judge each\n"
          "against its own role and against what comparable rounds use; see\n"
          "integration/intercept-model/build_patch.py for the calls already made.")
    print(f"\nPROBE ROUNDS for the missing-global test: {len(probes)} anti-air rounds\n"
          "declare NEITHER penalty and carry a closed band, so they inherit both from\n"
          "damage.ini and an engagement inside their band is not confounded by the\n"
          "out-of-altitude clamp. Do NOT use the SM-3 for this - SEST_Aegis_BMD gives\n"
          "it explicit values for both penalties, so it inherits neither. A sample:")
    for r in probes[:12]:
        print(f"   {r['id']:28} {r['winner']:16} "
              f"min={str(r['min']):>8} max={str(r['max']):>9}")
    print("   (full list: --json, 'probes')")

    print("\nRead the winner column: this resolves the tree INCLUDING the SEST packs,\n"
          "which sit at tier 0, so a round SEST already overrides shows SEST's values\n"
          "and a defect already fixed reads clean. usn_rim_174a/b/c and idf_stunner\n"
          "are the four this pack owns - to see what upstream still ships, read their\n"
          "donors under mods-source/ directly.")


if __name__ == "__main__":
    main()
