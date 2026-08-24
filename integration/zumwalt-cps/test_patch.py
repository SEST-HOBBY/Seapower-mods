#!/usr/bin/env python3
"""Test the Zumwalt CPS fix without launching the game.

The claim being tested is specific: the shipped hull declares [WeaponSystem1]
twice, so a section-keyed loader keeps only one of {LMVLS, MK57 1}, and since
usn_ircps can ONLY be fired by the LMVLS (Launcher1=eu_lmvls_apm), the ship
may have no way to fire its hypersonic missile at all.

The honest gap: nobody here can observe which block Sea Power's parser keeps.
So this simulates BOTH resolution rules a keyed loader can use - first-wins and
last-wins - and asserts the fix is correct under either. That is what makes the
result trustworthy without the game: the patch does not depend on guessing the
parser, because it removes the ambiguity entirely.

Run from the repo root:  python3 integration/zumwalt-cps/test_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import winning_file  # noqa: E402

UPSTREAM = ROOT / "mods-source" / "3390330875" / "vessels" / "usn_ddg-1000_cps.ini"
PATCHED = Path(__file__).resolve().parent / "SEST_Zumwalt_CPS" / "vessels" / "usn_ddg-1000_cps.ini"
EUROMOD = ROOT / "mods-source" / "3629144864"

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"\n          {detail}" if detail else ""))
    return ok


def load_weapon_systems(text, rule):
    """Simulate a section-keyed loader. rule is 'first' or 'last'.

    A keyed loader stores sections in a dict by name, so a repeated name either
    keeps the first occurrence and ignores later ones, or is overwritten by the
    last. Returns {number: label} as the ship would actually see it.
    """
    out = {}
    for m in re.finditer(r"^\[WeaponSystem(\d+)\]([^\n]*)\n(.*?)(?=^\[|\Z)", text, re.S | re.M):
        n, label = int(m.group(1)), m.group(2).strip()
        if rule == "first" and n in out:
            continue
        out[n] = label
    return out


def magazine_for(text, label_fragment):
    """The magazine a named weapon system binds, and what it holds."""
    for m in re.finditer(r"^\[WeaponSystem\d+\]([^\n]*)\n(.*?)(?=^\[|\Z)", text, re.S | re.M):
        if label_fragment not in m.group(1):
            continue
        mag = re.search(r"^AssociatedMagazine=(\S+)", m.group(2), re.M)
        if not mag:
            return None, None
        block = re.search(rf"^\[{re.escape(mag.group(1))}\]\n(.*?)(?=^\[|\Z)", text, re.S | re.M)
        if not block:
            return mag.group(1), None
        ammo = re.search(r"^Ammunition1=(\S+)", block.group(1), re.M)
        cnt = re.search(r"^Ammunition1_Count=(\d+)", block.group(1), re.M)
        return mag.group(1), (ammo.group(1) if ammo else None, int(cnt.group(1)) if cnt else 0)
    return None, None


def main():
    up = UPSTREAM.read_text(encoding="utf-8", errors="replace")
    if not PATCHED.exists():
        sys.exit("pack not built — run: python3 integration/zumwalt-cps/build_patch.py")
    fx = PATCHED.read_text(encoding="utf-8", errors="replace")
    declared = int(re.search(r"^NumberOfWeaponSystems=(\d+)", fx, re.M).group(1))

    print("\n1. Loader simulation — what the ship actually ends up with")
    for rule in ("first", "last"):
        u = load_weapon_systems(up, rule)
        lost = [lab for n, lab in
                [(1, "# LMVLS"), (1, "# MK57 1")] if lab not in u.values()]
        check(f"upstream, {rule}-wins: a launcher is lost",
              len(u) < declared and bool(lost),
              f"{len(u)}/{declared} systems load; missing: {lost or 'none'}")
    for rule in ("first", "last"):
        f = load_weapon_systems(fx, rule)
        check(f"patched, {rule}-wins: all {declared} systems load",
              len(f) == declared and sorted(f) == list(range(1, declared + 1)),
              f"{len(f)}/{declared} systems load")

    print("\n2. The IRCPS chain, end to end")
    mag, holds = magazine_for(fx, "# LMVLS")
    check("patched: the LMVLS survives and binds a magazine", mag is not None, f"magazine: {mag}")
    check("that magazine holds 12x usn_ircps", holds == ("usn_ircps", 12), f"holds: {holds}")

    ircps = EUROMOD / "ammunition" / "usn_ircps.ini"
    itxt = ircps.read_text(encoding="utf-8", errors="replace") if ircps.exists() else ""
    check("usn_ircps exists and can ONLY be fired by the LMVLS",
          "Launcher1=eu_lmvls_apm" in itxt and "NumberOfLaunchers=1" in itxt,
          "Launcher1=eu_lmvls_apm, NumberOfLaunchers=1 — this is why losing that block "
          "takes the weapon off the ship")

    weapons = (EUROMOD / "systems" / "weapons.ini").read_text(encoding="utf-8", errors="replace")
    apm = re.search(r"^\[eu_lmvls_apm\]\n(.*?)(?=^\[|\Z)", weapons, re.S | re.M)
    att = int(re.search(r"^NumberOfAttachments=(\d+)", apm.group(1), re.M).group(1)) if apm else 0
    lm = re.search(r"^\[WeaponSystem1\]([^\n]*)\n(.*?)(?=^\[|\Z)", fx, re.S | re.M)
    containers = int(re.search(r"^NumberOfContainers=(\d+)", lm.group(2), re.M).group(1))
    check("launcher capacity matches the magazine", containers * att == 12,
          f"{containers} containers x {att} attachments = {containers * att}, magazine holds 12")

    print("\n3. Fire control")
    have = {int(n) for n in re.findall(r"^\[SensorSystem(\d+)\]", fx, re.M)}
    starved = []
    for m in re.finditer(r"^\[WeaponSystem(\d+)\]([^\n]*)\n(.*?)(?=^\[|\Z)", fx, re.S | re.M):
        a = re.search(r"^AssociatedSensors=(\S+)", m.group(3), re.M)
        if a and not [s for s in a.group(1).split(",")
                      if s.startswith("SensorSystem") and int(s[12:]) in have]:
            starved.append(m.group(2).strip())
    check("patched: every launcher has at least one usable sensor", not starved,
          f"starved: {starved or 'none'}")

    up_starved = []
    for m in re.finditer(r"^\[WeaponSystem(\d+)\]([^\n]*)\n(.*?)(?=^\[|\Z)", up, re.S | re.M):
        a = re.search(r"^AssociatedSensors=(\S+)", m.group(3), re.M)
        uh = {int(n) for n in re.findall(r"^\[SensorSystem(\d+)\]", up, re.M)}
        if a and not [s for s in a.group(1).split(",")
                      if s.startswith("SensorSystem") and int(s[12:]) in uh]:
            up_starved.append(m.group(2).strip())
    check("upstream: the LMVLS had no usable sensor (the defect being fixed)",
          up_starved == ["# LMVLS"], f"starved upstream: {up_starved}")

    print("\n4. Does the game load OUR copy?")
    win = winning_file("vessels/usn_ddg-1000_cps.ini")
    check("the SEST pack wins this file through the canonical load order",
          win is not None and "SEST_Zumwalt_CPS" in str(win),
          f"winning copy: {win}")

    print("\n5. The patch matches the mod author's own working copies")
    alts = list((ROOT / "mods-source" / "3390330875" / "ships" / "usn_ddg-1000" / "alt")
                .glob("*_cps*.ini"))
    ours = [(n, l.strip()) for n, l in re.findall(r"^\[WeaponSystem(\d+)\]([^\n]*)", fx, re.M)][:3]
    agree = 0
    for a in alts:
        at = a.read_text(encoding="utf-8", errors="replace")
        theirs = [(n, l.strip()) for n, l in
                  re.findall(r"^\[WeaponSystem(\d+)\]([^\n]*)", at, re.M)][:3]
        if theirs == ours:
            agree += 1
    check("the author's backup copies use the numbering this patch restores",
          agree > 0 and agree == len(alts),
          f"{agree}/{len(alts)} backups agree: {ours}")

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{'-' * 66}")
    print(f"{len(results) - len(failed)}/{len(results)} checks passed")
    if failed:
        print("FAILED: " + "; ".join(failed))
        sys.exit(1)
    print("The fix is correct under BOTH loader resolution rules, so it does not\n"
          "depend on knowing which block Sea Power's parser would have kept.")


if __name__ == "__main__":
    main()
