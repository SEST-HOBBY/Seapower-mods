#!/usr/bin/env python3
"""Set the enemy flags of the standalone missions: Nation= on every Taskforce2
unit whose unit file registers a nation this war does not have.

    python3 integration/missions/set_enemy_flags.py          # report only
    python3 integration/missions/set_enemy_flags.py --write  # rewrite in place

The campaign builder applies the same rule as it writes (build_pack.py);
this is the pass for the missions kept as .ini here - Northern Front, the
Banda Front family, the Indo-Pacific showcase - whose units take their flag
from the unit file when the mission says nothing. integration/common/flags.py
has the mapping and the reason: Soviet-registered Russian units fly the
Russian Federation flag, Iran-registered Meridian hulls the company's. A unit
with a Nation= of its own is left alone, whatever it says.

The registered nation is read the way the game reads it: the variant or
squadron the mission names, else that file's [Default], from the copy of the
file the load order makes the winner. Run it again after re-importing a
mission from the game or regenerating one with its builder. The Baltic
chapters and the 0.7 test file are out of theatre and left alone.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration"))
from common import flags  # noqa: E402

MODS = ROOT / "mods-source"
HERE = Path(__file__).resolve().parent
# The 2028 Indo-Pacific missions only: the Baltic chapters and the 0.7 test
# file keep their own flags.
OUT_OF_THEATRE = ("chapter ", "newest 0.7")


def load_rank():
    toks = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt").read_text(
        encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    return {t: i for i, t in enumerate(toks)}


def index():
    """lower-cased 'kind/file.ini' -> winning path, mods first by rank, SEST packs above all."""
    rank = load_rank()
    best = {}
    for p in MODS.glob("*/*/*_*.ini"):
        if p.parts[-3].startswith("_") or not p.name.endswith(("_variants.ini", "_squadrons.ini")):
            continue
        key = f"{p.parts[-2]}/{p.name}".lower()
        r = rank.get(p.parts[-3], 10**5)
        if key not in best or r < best[key][0]:
            best[key] = (r, p)
    for p in (MODS / "_vanilla" / "original").glob("*/*_*.ini"):
        if p.name.endswith(("_variants.ini", "_squadrons.ini")):
            best.setdefault(f"{p.parts[-2]}/{p.name}".lower(), (10**6, p))
    for p in (ROOT / "integration").glob("*/SEST_*/*/*_*.ini"):
        if "dist" not in p.parts and p.name.endswith(("_variants.ini", "_squadrons.ini")):
            best[f"{p.parts[-2]}/{p.name}".lower()] = (-1, p)
    return {k: v[1] for k, v in best.items()}


def registered(idx, uid, pick):
    for kind, suffix in (("vessels", "variants"), ("land_units", "variants"),
                         ("aircraft", "squadrons")):
        f = idx.get(f"{kind}/{uid}_{suffix}.ini".lower())
        if f is None:
            continue
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        for section in (pick, "Default"):
            m = re.search(rf"^\[{re.escape(section)}\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
            n = m and re.search(r"^[ \t]*Nation[ \t]*=[ \t]*(.*?)[ \t]*\r?$", m.group(1), re.M)
            value = n and re.split(r"\s*(?://|#|;)", n.group(1), 1)[0].strip()
            if value:
                return value
        return None
    return None


def rewrite(text, idx):
    """(new text, [(unit section, type, flag)])"""
    out, changes = [], []
    nl = "\r\n" if "\r\n" in text else "\n"
    for block in re.split(r"(?=^\[)", text, flags=re.M):
        head = block.split("\n", 1)[0].strip()
        m = re.match(r"\[(Taskforce2(?:Vessel|Submarine|Aircraft|Helicopter|LandUnit)\d+)\]", head)
        if m and not re.search(r"^Nation=", block, re.M):
            ty = re.search(r"^Type=(\S+)", block, re.M)
            pick = re.search(r"^(?:VariantReference|Squadron)=(\S+)", block, re.M)
            if ty:
                flag = flags.flag_for(registered(idx, ty.group(1), pick.group(1) if pick else "Default"),
                                      ty.group(1))
                if flag:
                    block = re.sub(r"^(Type=[^\r\n]*\r?\n)", rf"\g<1>Nation={flag}{nl}", block, count=1, flags=re.M)
                    changes.append((m.group(1), ty.group(1), flag))
        out.append(block)
    return "".join(out), changes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    idx = index()
    total = 0
    for f in sorted(HERE.glob("*.ini")):
        if " backup-" in f.name or f.name.lower().startswith(OUT_OF_THEATRE):
            continue
        raw = f.read_bytes()
        text = raw.decode("utf-8-sig", errors="replace")
        new, changes = rewrite(text, idx)
        if not changes:
            continue
        total += len(changes)
        by = {}
        for _s, ty, flag in changes:
            by.setdefault(flag, set()).add(ty)
        print(f"{f.name}: {len(changes)} unit(s) - "
              + "; ".join(f"{flag}: {', '.join(sorted(t))}" for flag, t in sorted(by.items())))
        if args.write:
            bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
            f.write_bytes(bom + new.encode("utf-8"))
    print(f"{total} unit(s) {'rewritten' if args.write else 'would be rewritten (add --write)'}")


if __name__ == "__main__":
    main()
