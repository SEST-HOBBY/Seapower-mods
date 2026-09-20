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
  - Directive inheritance, both kinds. Around 94 ammunition files open with
    #!alias or #!extend, and both resolve their base through the load order, so
    a round can carry a band it never literally declares - the ESSM, RAM and
    SM-2 families all do, and one composes its band across two mods. A flat scan
    misses about 20 anti-air rounds and miscounts the one-sided total.

CAVEAT ON #!extend, and it is the important one. This tool resolves an extend
optimistically: it layers the stub onto the highest copy BELOW it, which is what
the directive means and what the game does WHEN THE ANCHOR CHAIN PRELOADER IS
WORKING. data/mod-catalog.json records that preloader as subscribed but never
verified. If it is not working, an extend stub that outranks its base does not
layer - it simply wins the whole-file override with only its own handful of
keys, and the round loses its TargetType, its warhead and its altitude band.
The EXTEND STUBS section below lists exactly which rounds are exposed to that,
so the reader can see what an unverified dependency is currently carrying.

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
    """Merged key map for an ammunition path, following BOTH directives through
    the load order. The stub's own keys win over the inherited ones.

    Two directives, resolved differently:
      #!alias  <path>   the base is whatever wins at <path> anywhere in the order.
      #!extend <path>   the base is the winner at <path> BELOW this file, since an
                        extend layers onto the copy it outranks. A stub that
                        outranks nothing has no base and contributes only its own
                        keys - which is how a round ends up with no TargetType and
                        no warhead, so the survey must see that rather than skip it.

    An earlier version followed only #!alias. When the load-order refresh moved
    the PLA AEP pack above Type 003, four rounds became extend stubs and silently
    dropped out of the anti-air population."""
    if rel in _cache:
        return _cache[rel]
    if rel in chain:
        return {"__cycle__": rel}
    won = R.winning_file(rel)
    if not won:
        return {}
    text = Path(won).read_text(encoding="utf-8-sig", errors="replace")
    own = kv(text)
    winner = Path(won).parts[-3]
    own["__winner__"] = winner
    m = re.match(r"^\s*#!(alias|extend)\s+(\S+)", text)
    if m:
        kind, target = m.group(1), m.group(2).strip()
        base = (resolve(target, chain + (rel,)) if kind == "alias"
                else resolve_below(target, winner, chain + (rel,)))
        merged = dict(base)
        merged.update(own)
        merged[f"__{kind}_of__"] = target
        merged["__alias_of__"] = target
        merged["__inherited_band__"] = any(
            k in base and k not in own
            for k in ("MinAttackAltitude", "MaxAttackAltitude"))
        merged["__no_base__"] = not base
        own = merged
    _cache[rel] = own
    return own


def _order():
    global _ORDER_INDEX
    if _ORDER_INDEX is None:
        toks = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt")
                .read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.lstrip().startswith("#")]
        _ORDER_INDEX = {t: i for i, t in enumerate(toks)}
    return _ORDER_INDEX


_ORDER_INDEX = None


def resolve_below(rel, above, chain=()):
    """Resolve `rel` using only providers ranked BELOW `above`. That is what an
    #!extend layers onto; a provider above it is not a base, it is a competitor."""
    idx = _order()
    here = idx.get(above)
    if here is None:
        return {}
    best, best_i = None, None
    for d in MODS.iterdir():
        if not d.is_dir() or d.name == above:
            continue
        i = idx.get(d.name)
        if i is None or i <= here:
            continue
        if (d / rel).exists() and (best_i is None or i < best_i):
            best, best_i = d, i
    if best is None:
        van = MODS / "_vanilla" / "original" / rel
        if not van.exists():
            return {}
        d2 = kv(van.read_text(encoding="utf-8-sig", errors="replace"))
        d2["__winner__"] = "original"
        return d2
    d2 = kv((best / rel).read_text(encoding="utf-8-sig", errors="replace"))
    d2["__winner__"] = best.name
    return d2


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
    rows, probes, extends, stats = [], [], [], dict.fromkeys(
        ("total", "alias", "extend", "cycles", "aaw", "banded", "onesided",
         "inherited", "inherits_speed", "inherits_alt", "inherits_both"), 0)
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
        if d.get("__extend_of__"):
            stats["extend"] += 1
            extends.append({"id": name[:-4], "winner": d.get("__winner__"),
                            "target": d["__extend_of__"],
                            "no_base": bool(d.get("__no_base__")),
                            "aaw": d.get("TargetType") == "AAW"
                                   or d.get("SecondaryTargetType") == "AAW"})
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
    return rows, probes, extends, stats


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
    rows, probes, extends, stats = survey()
    if "--json" in sys.argv:
        print(json.dumps({"stats": stats, "rows": rows, "probes": probes,
                          "extends": extends}, indent=1))
        return

    print("winning ammunition ids resolved   ", stats["total"])
    print("  of which #!alias stubs          ", stats["alias"])
    print("  of which #!extend stubs         ", stats["extend"])
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
    exposed = [e for e in extends if not e["no_base"]]
    orphan = [e for e in extends if e["no_base"]]
    print(f"\nEXTEND STUBS: {len(extends)} round(s) open with #!extend. This tool layers\n"
          "them onto the copy below, which is what happens only if the Anchor Chain\n"
          f"preloader is working. {len(exposed)} of them outrank a real base, so their\n"
          "stats depend on that unverified dependency; without it each loads as a bare\n"
          "stub. Verify the preloader, or rank the stub below its base to keep the\n"
          "base's values.")
    for e in sorted(exposed, key=lambda e: (not e["aaw"], e["id"]))[:14]:
        print(f"   {e['id']:28} {e['winner']:16} extends {e['target'].split('/')[-1]:26}"
              f"{'  [anti-air]' if e['aaw'] else ''}")
    if len(exposed) > 14:
        print(f"   ... and {len(exposed) - 14} more (--json, 'extends')")
    if orphan:
        print(f"   NO BASE AT ALL ({len(orphan)}): "
              f"{', '.join(e['id'] for e in orphan)} - these never fire either way")

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
