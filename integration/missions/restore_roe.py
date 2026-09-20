#!/usr/bin/env python3
"""Restore the rules of engagement an editor round-trip flattened.

WHAT THE EDITOR DOES. Saving a mission in Sea Power's own editor rewrites
every unit section from the editor's in-memory model, and that model does not
round-trip WeaponStatus: every Hold and every Tight comes back as Free, and a
handful of units lose the key outright. Nothing warns you - the save looks
clean, the unit count is right, and the scenario is a different scenario.

WHY IT MATTERS HERE. Hold and Tight are not decoration in this repo's
missions; they are the scenario. add_sanctioned_shipping.py builds convoys
that run "dark, dumb, non-reactive" on WeaponStatus=Hold behind escorts on
WeaponStatus=Tight "so they unmask only when the fleet is engaged", and the
Allied carrier group sits on Tight so it shadows rather than shoots. Flatten
all of that to Free and the first contact is a general engagement.

WHAT THIS PASS DOES. It aligns the mission against a reference copy - the
last committed state, by default - unit by unit, and restores WeaponStatus
wherever the reference says Hold or Tight and the mission no longer does.
Nothing else is touched.

WHAT IT DELIBERATELY DOES NOT DO. The same save also drops MissionType=
NoMission, RadarsActive=False, ActiveSonarsEnabled=False and TowedArray
Deployed=False, and strips Waypoints from formation followers. Those are not
losses: the editor omits a key whose value is the default (every dropped
RadarsActive was False and every surviving one is True), and a follower's
waypoints were only ever a copy of its leader's, which the leader keeps. See
docs/design-notes.md.

ALIGNMENT IS BY POSITION IN THE TYPE SEQUENCE, NOT BY SECTION NAME. Inserting
one vessel renumbers every section after it, so [Taskforce1Vessel8] before a
save and [Taskforce1Vessel8] after it are routinely different ships. Units
inside an inserted or deleted run are skipped entirely rather than guessed at.

Usage (repo root):
    python3 integration/missions/restore_roe.py --mission "SEST Banda Front Lean v2"
    python3 integration/missions/restore_roe.py --mission "SEST Banda Front Lean v2" --write
"""
import argparse
import collections
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = Path(__file__).resolve().parent

RESTRAINT = ("Hold", "Tight")
# The editor's own key order, used to place a key it dropped entirely.
AFTER_KEY = ("UnlimitedFuel", "VariantReference", "SquadronReference", "Type")
INDEXED = re.compile(r"^(.*?)(\d+)$")


def parse(text):
    """[Section] -> ordered {key: value}. Unit sections only ever hold one
    level, so a flat dict per section is the whole file."""
    sections, order, cur = {}, [], None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            cur = s[1:-1]
            sections.setdefault(cur, collections.OrderedDict())
            order.append(cur)
        elif "=" in s and cur is not None:
            k, v = s.split("=", 1)
            sections[cur][k.strip()] = v.strip()
    return sections, order


def align(ref, cur):
    """Pair reference sections with current ones by their Type sequence
    within each index family. Only equal runs are paired."""
    fam = collections.defaultdict(lambda: ([], []))
    for i, d in ((0, ref), (1, cur)):
        for name in d:
            m = INDEXED.match(name)
            if m:
                fam[m.group(1)][i].append((int(m.group(2)), name))
    pairs = []
    for prefix in sorted(fam):
        a, b = fam[prefix]
        a.sort()
        b.sort()
        ta = [ref[n].get("Type", "") for _, n in a]
        tb = [cur[n].get("Type", "") for _, n in b]
        sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    pairs.append((a[i1 + k][1], b[j1 + k][1]))
    return pairs


def reference_text(path, rev):
    rel = path.relative_to(ROOT).as_posix()
    if rev is None:
        log = subprocess.run(
            ["git", "log", "--format=%H", "--", rel],
            cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        if len(log) < 2:
            sys.exit(f"{rel}: only {len(log)} commit(s) touch this mission - "
                     f"pass --ref explicitly")
        rev = log[1]
    out = subprocess.run(["git", "show", f"{rev}:{rel}"],
                         cwd=ROOT, capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"git show {rev}:{rel} failed: {out.stderr.strip()}")
    return rev, out.stdout


def restore(text, fixes):
    """Rewrite in place, line by line, so every byte we are not fixing -
    key order, spacing, the lines the editor reformatted - is preserved."""
    want = {name: value for name, value in fixes}
    out, cur, done = [], None, set()
    for line in text.splitlines(keepends=True):
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            cur = s[1:-1]
        elif cur in want and s.startswith("WeaponStatus="):
            eol = line[len(line.rstrip("\r\n")):]
            out.append(f"WeaponStatus={want[cur]}{eol}")
            done.add(cur)
            continue
        out.append(line)
    # Units the editor dropped the key from need it inserted, in the editor's
    # own key order: directly after the last of AFTER_KEY that unit carries.
    missing = {n: v for n, v in want.items() if n not in done}
    if missing:
        text2, cur, anchor = [], None, None
        for line in out:
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                if anchor is not None:
                    text2.insert(anchor[0], anchor[1])
                    anchor = None
                cur = s[1:-1]
                text2.append(line)
                continue
            text2.append(line)
            if cur in missing and "=" in s:
                key = s.split("=", 1)[0].strip()
                if key in AFTER_KEY and (
                        anchor is None
                        or AFTER_KEY.index(key) <= AFTER_KEY.index(anchor[2])):
                    eol = line[len(line.rstrip("\r\n")):] or "\n"
                    anchor = (len(text2), f"WeaponStatus={missing[cur]}{eol}", key)
        if anchor is not None:
            text2.insert(anchor[0], anchor[1])
        out = text2
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mission", required=True)
    ap.add_argument("--ref", default=None,
                    help="git revision to read the mission from "
                         "(default: the commit before the most recent one "
                         "that touched it)")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    path = MISSIONS / f"{args.mission}.ini"
    if not path.exists():
        sys.exit(f"no such mission: {path}")
    rev, ref_text = reference_text(path, args.ref)
    cur_text = path.read_text(encoding="utf-8-sig")
    ref, _ = parse(ref_text)
    cur, _ = parse(cur_text)

    pairs = align(ref, cur)
    names = ref.get("Language_en", {})
    fixes, already = [], 0
    for a, b in pairs:
        was = ref[a].get("WeaponStatus")
        now = cur[b].get("WeaponStatus")
        if was not in RESTRAINT:
            continue
        if now == was:
            already += 1
            continue
        fixes.append((b, was))
        label = names.get(a + "NameOverride", "")
        print(f"  {b:<24} {cur[b].get('Type',''):<26} "
              f"{str(now):<5} -> {was:<5} {label}")

    print(f"\nreference {rev[:8]}  aligned {len(pairs)} units  "
          f"already correct {already}  to restore {len(fixes)}")
    if not fixes:
        return
    if not args.write:
        print("dry run - pass --write to apply")
        return
    new = restore(cur_text, fixes)
    check, _ = parse(new)
    bad = [(n, v) for n, v in fixes if check.get(n, {}).get("WeaponStatus") != v]
    if bad or len(check) != len(cur):
        sys.exit(f"refusing to write: {len(bad)} unapplied, "
                 f"{len(check)} sections vs {len(cur)}")
    path.write_text(new, encoding="utf-8", newline="")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
