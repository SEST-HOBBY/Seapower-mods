#!/usr/bin/env python3
"""Repair unresolved squadron references in a mission's airbase AirGroups.

An airbase [AirGroup] line reads

    <aircraft_id>=Squadron4,6|Squadron5,6

where each SquadronN must be a real section in that aircraft's
<id>_squadrons.ini. Missions built in the editor can name squadrons the
providing mod does not define (e.g. usaf_f-22_s6 offers only Default and
Squadron1, but a mission asks for Squadron4-7), which leaves those aircraft
without a livery at spawn.

This remaps every unresolved SquadronN to one the winning mod actually
defines (preferring Squadron1, else Default) and folds duplicates together
so the TOTAL AIRCRAFT COUNT on the line is preserved exactly. Nothing else
in the mission is touched.

--spread is the inverse, for after a SEST pack adds squadrons a mod never
defined: any single squadron holding a whole base's worth of one type gets
split back out across the squadrons that now exist, so the units read as
separate squadrons on the tacmap instead of one anonymous block. It is
opt-in precisely because collapsing was the earlier repair - running it by
accident on a hand-edited mission would undo a deliberate choice.

Squadron files are resolved through the canonical Mod Manager order, so both
checks match the copy the game really loads - SEST packs included.

Usage (repo root):
    python3 integration/missions/fix_squadron_refs.py                  # report only
    python3 integration/missions/fix_squadron_refs.py --write          # apply
    python3 integration/missions/fix_squadron_refs.py --mission "NORTHERN FRONT III" --write
    python3 integration/missions/fix_squadron_refs.py --spread --write # re-split collapsed groups
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_civ_traffic import winning_file  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = Path(__file__).resolve().parent

AIRGROUP_LINE = re.compile(r"^([A-Za-z0-9_.\-]+)=((?:Squadron\d+,\d+\|?)+)$")


def available(type_id):
    """Squadron section names the winning <type_id>_squadrons.ini defines."""
    f = winning_file(f"aircraft/{type_id}_squadrons.ini")
    if f is None:
        return None
    return set(re.findall(r"^\[(Squadron\d+|Default)\]", f.read_text(
        encoding="utf-8", errors="replace"), re.M))


def fallback(have):
    """Which squadron an unresolved reference should become."""
    if "Squadron1" in have:
        return "Squadron1"
    if "Default" in have:
        return "Default"
    return sorted(have)[0] if have else None


def fix_line(type_id, spec, have):
    """Return (new_spec, remaps) preserving the total aircraft count."""
    target = fallback(have)
    if target is None:
        return spec, []
    order, counts, remaps = [], {}, []
    for sq, n in re.findall(r"(Squadron\d+),(\d+)", spec):
        n = int(n)
        if sq not in have:
            remaps.append(f"{sq}->{target}")
            sq = target
        if sq not in counts:
            order.append(sq)
            counts[sq] = 0
        counts[sq] += n
    return "|".join(f"{sq},{counts[sq]}" for sq in order), remaps


# A collapsed group is bigger than any real single-squadron det. Four flights
# of four is already a large squadron, so only 16+ is treated as collapsed.
SPREAD_THRESHOLD = 16


def spread_line(type_id, spec, have):
    """Return (new_spec, note) splitting a collapsed single squadron.

    Deliberately narrow: it fires only on the exact signature fix_line leaves
    behind - ONE squadron, and specifically the one fallback() folds into,
    carrying SPREAD_THRESHOLD or more aircraft while the type now defines
    several. A hand-placed twelve-ship on Squadron2 or Squadron3 is somebody's
    choice, not damage, and is left alone. The total is preserved exactly.
    """
    parts = re.findall(r"(Squadron\d+),(\d+)", spec)
    if len(parts) != 1:
        return spec, None
    sq, total = parts[0][0], int(parts[0][1])
    if sq != fallback(have) or total < SPREAD_THRESHOLD:
        return spec, None
    real = sorted((s for s in have if s.startswith("Squadron")),
                  key=lambda s: int(s[8:]))
    if len(real) < 2 or sq not in real:
        return spec, None
    # Start at the squadron the line already names, so Squadron1 stays first.
    start = real.index(sq)
    ring = real[start:] + real[:start]
    n = min(len(ring), total // 4)          # flights of 4 or better
    if n < 2:
        return spec, None
    ring = ring[:n]
    base, extra = divmod(total, n)
    counts = [base + (1 if i < extra else 0) for i in range(n)]
    return ("|".join(f"{s},{c}" for s, c in zip(ring, counts)),
            f"{sq},{total} collapsed -> {n} squadrons")


FORMATION_LINE = re.compile(r"^(Taskforce\d_Formation\d+)=([^|]+)\|(.*)$", re.M)
UNIT_BLOCK = re.compile(r"^\[(Taskforce\dAircraft\d+)\]\n(.*?)(?=^\[|\Z)", re.S | re.M)


def spread_formations(text):
    """Give same-type airborne formations distinct squadrons.

    Every flight of a type sitting on the same fallback squadron is the other
    half of the collapse: the base roster says six squadrons but the aircraft
    in the air are all Squadron1, so they show up as one anonymous unit. This
    walks the formations of each type in order and hands them successive
    squadrons. Only formations that are ENTIRELY one type and ENTIRELY on the
    fallback squadron are touched - a mixed package, or a flight somebody
    already assigned, is left exactly as it is.

    Returns (new_text, [(formation, type_id, squadron), ...]).
    """
    unit_type, unit_sq = {}, {}
    for m in UNIT_BLOCK.finditer(text):
        ty = re.search(r"^Type=(\S+)", m.group(2), re.M)
        sq = re.search(r"^SquadronReference=(\S+)", m.group(2), re.M)
        if ty:
            unit_type[m.group(1)] = ty.group(1)
            unit_sq[m.group(1)] = sq.group(1) if sq else None

    by_type = {}
    for m in FORMATION_LINE.finditer(text):
        members = [x for x in m.group(2).split(",") if x in unit_type]
        if not members or len(members) != len(m.group(2).split(",")):
            continue
        types = {unit_type[x] for x in members}
        sqs = {unit_sq[x] for x in members}
        if len(types) != 1 or len(sqs) != 1:
            continue
        by_type.setdefault(types.pop(), []).append((m.group(1), members, sqs.pop()))

    changes = []
    for type_id, forms in by_type.items():
        have = available(type_id)
        if not have:
            continue
        target = fallback(have)
        real = sorted((s for s in have if s.startswith("Squadron")),
                      key=lambda s: int(s[8:]))
        forms = [f for f in forms if f[2] == target]
        if len(forms) < 2 or len(real) < 2:
            continue
        for i, (fname, members, _) in enumerate(forms):
            sq = real[i % len(real)]
            if sq == target and i == 0:
                continue                      # first flight keeps what it had
            for unit in members:
                block = re.search(rf"^\[{unit}\]\n(.*?)(?=^\[|\Z)", text, re.S | re.M)
                text = (text[:block.start(1)]
                        + re.sub(r"^SquadronReference=\S+", f"SquadronReference={sq}",
                                 block.group(1), count=1, flags=re.M)
                        + text[block.end(1):])
            changes.append((fname, type_id, sq))
    return text, changes


def process(path, write, spread=False):
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    out, changed, total_before, total_after = [], 0, 0, 0
    for line in text.split("\n"):
        m = AIRGROUP_LINE.match(line)
        if not m:
            out.append(line)
            continue
        type_id, spec = m.group(1), m.group(2)
        have = available(type_id)
        if have is None:
            out.append(line)
            continue
        new_spec, remaps = fix_line(type_id, spec, have)
        note = None
        if spread and not remaps:
            new_spec, note = spread_line(type_id, spec, have)
        before = sum(int(n) for n in re.findall(r",(\d+)", spec))
        after = sum(int(n) for n in re.findall(r",(\d+)", new_spec))
        total_before += before
        total_after += after
        if remaps or note:
            assert before == after, f"{type_id}: aircraft count changed {before}->{after}"
            what = ", ".join(remaps) if remaps else note
            print(f"  {path.name} {type_id}: {what}  "
                  f"({spec} -> {new_spec}, {after} aircraft kept)")
            changed += 1
            out.append(f"{type_id}={new_spec}")
        else:
            out.append(line)
    text = "\n".join(out)
    if spread:
        text, moves = spread_formations(text)
        for fname, type_id, sq in moves:
            print(f"  {path.name} {fname} ({type_id}) -> {sq}")
        changed += len(moves)
    if changed and write:
        path.write_text(text, encoding="utf-8", newline="\n")
    return changed, total_before, total_after


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", default=None,
                    help="mission name without .ini (default: every mission)")
    ap.add_argument("--write", action="store_true", help="apply the fixes")
    ap.add_argument("--spread", action="store_true",
                    help="also re-split single squadrons holding a collapsed group, "
                         "now that SEST packs define the squadrons that were missing")
    args = ap.parse_args()

    targets = ([MISSIONS / f"{args.mission}.ini"] if args.mission
               else sorted(MISSIONS.glob("*.ini")))
    total = 0
    for p in targets:
        if not p.exists():
            sys.exit(f"no such mission: {p}")
        changed, before, after = process(p, args.write, args.spread)
        total += changed
        if changed:
            print(f"  {p.name}: {changed} line(s), aircraft total {before} -> {after}")
    if not total:
        print("all squadron references already resolve"
              + ("" if args.spread else " (add --spread to re-split collapsed groups)"))
    elif not args.write:
        print(f"\n{total} line(s) would change - re-run with --write to apply")


if __name__ == "__main__":
    main()
