#!/usr/bin/env python3
"""Validate every carved scenario in integration/missions/scenarios/.

Carving a mission is mostly bookkeeping, and bookkeeping is exactly what fails
quietly. `make_scenarios.py` collects the chosen units, renumbers each class
from 1, rewrites the two cross-reference sites and recomputes the counts - and
if any of that is off by one, the mission still loads. It just loads wrong: a
formation naming a unit that is not there, or a NumberOf line promising ships
the file does not contain.

So this checks the four invariants that carving can break, across every
scenario at once:

  1. Every NumberOf<Side><Class> equals the number of matching unit sections.
  2. Every unit named in a Taskforce<N>_Formation exists as a section.
  3. No unit section number is used twice - the duplicate-section defect that
     cost the Zumwalt a launcher, in mission form.
  4. <Side>_NumberOfFormations equals the number of Formation lines present.

It deliberately does NOT re-check unit types, loadouts or pylon stores:
tools/preflight.py already resolves those against mods-source, and a scenario
inherits them unchanged from a parent mission that preflight covers.

    python3 tools/check_scenarios.py

Exits non-zero if any invariant is violated, so it can gate a commit.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "integration" / "missions" / "scenarios"

SIDES = ("Taskforce1", "Taskforce2", "Neutral")
# NumberOf* uses the plural; section names use the singular. "Aircraft" is its
# own plural, which is the kind of detail that makes a hand-written check wrong.
CLASSES = {"Vessel": "Vessels", "Submarine": "Submarines", "Aircraft": "Aircraft",
           "LandUnit": "LandUnits", "Biologic": "Biologics"}

UNIT_SECTION = re.compile(
    r"^\[((?:Taskforce[12]|Neutral)(?:Vessel|Submarine|Aircraft|LandUnit|Biologic)\d+)\]",
    re.M)


def mission_body(text):
    m = re.search(r"^\[Mission\]\n(.*?)(?=^\[)", text, re.S | re.M)
    if not m:
        raise SystemExit("no [Mission] section")
    return m.group(1)


def check(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    body = mission_body(text)
    sections = set(re.findall(r"^\[([^\]\n]+)\]", text, re.M))
    problems = []

    # 1. declared counts vs real sections
    for side in SIDES:
        for singular, plural in CLASSES.items():
            declared = re.search(rf"^NumberOf{side}{plural}=(\d+)$", body, re.M)
            actual = sum(1 for s in sections if re.fullmatch(rf"{side}{singular}\d+", s))
            if declared is None:
                if actual:
                    problems.append(f"{actual} {side}{singular} section(s) but no "
                                    f"NumberOf{side}{plural} line")
            elif int(declared.group(1)) != actual:
                problems.append(f"NumberOf{side}{plural}={declared.group(1)} "
                                f"but {actual} section(s) present")

    # 2. formation members resolve, and 4. formation counts
    for side in SIDES:
        lines = re.findall(rf"^{side}_Formation\d+=([^\n]*)$", body, re.M)
        for spec in lines:
            for unit in (u.strip() for u in spec.split("|")[0].split(",")):
                if unit and unit not in sections:
                    problems.append(f"{side} formation names {unit}, which has no section")
        declared = re.search(rf"^{side}_NumberOfFormations=(\d+)$", body, re.M)
        if declared and int(declared.group(1)) != len(lines):
            problems.append(f"{side}_NumberOfFormations={declared.group(1)} "
                            f"but {len(lines)} Formation line(s)")

    # 3. no duplicate unit sections
    counts = collections.Counter(UNIT_SECTION.findall(text))
    for name, n in sorted(counts.items()):
        if n > 1:
            problems.append(f"[{name}] declared {n} times")

    return problems


def main():
    if not SCENARIOS.is_dir():
        sys.exit(f"no scenarios directory: {SCENARIOS.relative_to(ROOT)}")
    files = sorted(SCENARIOS.glob("*.ini"))
    if not files:
        sys.exit("no scenarios found — run integration/missions/make_scenarios.py first")

    failed, units = 0, 0
    for path in files:
        problems = check(path)
        units += len(UNIT_SECTION.findall(path.read_text(encoding="utf-8-sig", errors="replace")))
        if problems:
            failed += 1
            print(f"\n  FAIL  {path.stem}")
            for p in problems:
                print(f"          {p}")

    print(f"\nchecked {len(files)} scenario(s), {units} unit sections")
    if failed:
        sys.exit(f"{failed} scenario(s) failed — regenerate with "
                 "python3 integration/missions/make_scenarios.py")
    print("every count, formation reference and section number is consistent")


if __name__ == "__main__":
    main()
