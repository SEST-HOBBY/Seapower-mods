#!/usr/bin/env python3
"""Carve small standalone scenarios out of a large mission, by formation.

NORTHERN FRONT III FINAL NEWEST is a 269-unit theatre mission - superb as a
campaign centrepiece, heavy for a quick fight. Its units are already grouped
into 38 named formations ("PLAN Carrier Group", "Sanctioned Lift Ichthys",
"H-6K Zhanshen"), and each one is a ready-made scenario component.

This picks formations by name and writes a self-contained mission for each
selection. The SOURCE IS NEVER MODIFIED - re-import a newer save over it and
re-run this to regenerate every scenario from the new state.

What carving a mission actually requires: unit sections are self-contained
(type, position, waypoints, air group), and the ONLY cross-references are the
Taskforce<N>_Formation lines in [Mission] plus the <Unit>NameOverride keys in
the [Language_*] blocks. So extraction is: collect the chosen units, renumber
each class from 1, rewrite those two reference sites, and recompute the
NumberOf* counts. Positions are absolute, so every unit keeps the geography
it was designed around.

    python3 integration/missions/make_scenarios.py            # build all
    python3 integration/missions/make_scenarios.py --list     # show formations
    python3 integration/missions/make_scenarios.py --source "OTHER MISSION"
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = ROOT / "integration" / "missions"
SCENARIO_DIR = MISSIONS / "scenarios"

UNIT_CLASSES = ("Vessel", "Submarine", "Aircraft", "LandUnit", "Biologic")
SIDES = ("Taskforce1", "Taskforce2", "Neutral")

# Each scenario names formations from the source. "neutrals" pulls in the
# civilian shipping, airliners and whale pods, which are what make a fight
# feel like it happens somewhere rather than in a void - worth the units on
# the convoy and patrol scenarios, wasted on a pure air intercept.
SCENARIOS = [
    {
        "file": "SEST NF3 - Sanctioned Convoy",
        "title": "Sanctioned Convoy Intercept",
        "desc": ("Three sanctioned tanker lifts are running out of Bayu-Undan, Ichthys and "
                 "Montara under escort. A RAN inshore screen and a single strike pair have to "
                 "sort neutral traffic from sanctioned traffic and stop the latter. Carved "
                 "from NORTHERN FRONT III."),
        "tf1": ["RAN Inshore Screen", "Strike Group 1"],
        "tf2": ["Sanctioned Lift Bayu-Undan", "Sanctioned Lift Ichthys",
                "Sanctioned Lift Montara", "Sanctioned Transit Group"],
        "neutrals": True,
    },
    {
        "file": "SEST NF3 - Bomber Stream",
        "title": "Bomber Stream",
        "desc": ("Nine H-6K Zhanshen inbound in three packages. Two F-22 flights and their "
                 "tankers are all that stands between them and the coast. Pure air intercept - "
                 "no surface units, no land clutter. Carved from NORTHERN FRONT III."),
        "tf1": ["F-22 Group 1", "KC Group 1", "F-22 Group 2", "KC Group 2"],
        "tf2": ["H-6K Zhanshen", "Tu-95 Bomber Flight"],
        "neutrals": False,
    },
    {
        "file": "SEST NF3 - Carrier Duel",
        "title": "Carrier Duel",
        "desc": ("A Ford-class group and a PLAN carrier group in the same water, each with its "
                 "own escort and air wing, and nothing else to hide behind. Carved from "
                 "NORTHERN FRONT III."),
        "tf1": ["Carrier Group A"],
        "tf2": ["PLAN Carrier Group"],
        "neutrals": False,
    },
    {
        "file": "SEST NF3 - SEAD over the Shelf",
        "title": "SEAD over the Shelf",
        "desc": ("An S-400 site and a supporting air-defence battery cover the shelf. A strike "
                 "package with dedicated escort has to open the corridor. The SEST MALICE and "
                 "AGM-88 fits are what this one is for. Carved from NORTHERN FRONT III."),
        "tf1": ["Strike Group 2", "F-15 Escort"],
        "tf2": ["S-400 SAM Site", "Air Defence Site"],
        "neutrals": False,
    },
    {
        "file": "SEST NF3 - Boomer Hunt",
        "title": "Boomer Hunt",
        "desc": ("A PLAN SSBN group is transiting with escort. A NATO surface group and a "
                 "single ASW pair have to find it before it reaches open water. Carved from "
                 "NORTHERN FRONT III."),
        "tf1": ["NATO Fleet A", "ASW-1"],
        "tf2": ["PLAN SSBN Group"],
        "neutrals": True,
    },
]


def split_sections(text):
    """[(header, body)] in file order; body keeps its exact bytes."""
    parts = re.split(r"(?m)^(\[[^\]\n]+\])[ \t]*\n", text)
    out = []
    if parts[0].strip():
        out.append((None, parts[0]))
    for i in range(1, len(parts), 2):
        out.append((parts[i], parts[i + 1]))
    return out


def parse_formations(mission_body):
    """side -> [(units, tail)] where tail is the |name|shape|... suffix."""
    formations = {s: [] for s in SIDES}
    for line in mission_body.splitlines():
        m = re.match(r"^(Taskforce[12]|Neutral)_Formation\d+=(.*)$", line.strip())
        if not m:
            continue
        spec = m.group(2)
        head, sep, tail = spec.partition("|")
        units = [u.strip() for u in head.split(",") if u.strip()]
        formations[m.group(1)].append((units, sep + tail))
    return formations


def formation_name(tail):
    return tail.lstrip("|").split("|")[0] if tail else "(unnamed)"


def build(source_text, scenario):
    sections = split_sections(source_text)
    by_header = {h: b for h, b in sections if h}
    mission_body = by_header["[Mission]"]
    formations = parse_formations(mission_body)

    # --- choose units --------------------------------------------------------
    chosen, kept_formations, missing = [], {s: [] for s in SIDES}, []
    for side, wanted in (("Taskforce1", scenario["tf1"]), ("Taskforce2", scenario["tf2"])):
        for want in wanted:
            hits = [(u, t) for u, t in formations[side] if formation_name(t) == want]
            if not hits:
                missing.append(f"{side}: {want!r}")
                continue
            for units, tail in hits:            # a name may repeat (3x H-6K Zhanshen)
                kept_formations[side].append((units, tail))
                chosen.extend(units)
    if missing:
        raise SystemExit(f"{scenario['file']}: formation(s) not in source: {missing}")

    if scenario["neutrals"]:
        chosen.extend(h[1:-1] for h, _ in sections
                      if h and re.fullmatch(r"\[Neutral(?:Vessel|Aircraft|Biologic)\d+\]", h))
        for units, tail in formations["Neutral"]:
            if all(u in chosen for u in units):
                kept_formations["Neutral"].append((units, tail))

    # --- renumber each class from 1, preserving source order -----------------
    chosen_set = set(chosen)
    order = [h[1:-1] for h, _ in sections if h and h[1:-1] in chosen_set]
    renamed, counters = {}, {}
    for unit in order:
        m = re.fullmatch(r"((?:Taskforce[12]|Neutral)(?:" + "|".join(UNIT_CLASSES) + r"))(\d+)", unit)
        if not m:
            raise SystemExit(f"unexpected unit section name: {unit}")
        cls = m.group(1)
        counters[cls] = counters.get(cls, 0) + 1
        renamed[unit] = f"{cls}{counters[cls]}"

    # --- rebuild [Mission] ---------------------------------------------------
    out_mission = []
    for line in mission_body.splitlines():
        s = line.strip()
        if re.match(r"^NumberOf\w+=", s) or re.match(r"^(Taskforce[12]|Neutral)_(Number|Formation)", s):
            continue
        out_mission.append(line)
    counts = []
    for side in SIDES:
        for cls in UNIT_CLASSES:
            key = f"{side}{cls}"
            n = counters.get(key, 0)
            plural = "Aircraft" if cls == "Aircraft" else cls + "s"
            counts.append(f"NumberOf{side}{plural}={n}")
    body = "\n".join(out_mission).rstrip("\n") + "\n" + "\n".join(counts) + "\n"
    for side in SIDES:
        keep = kept_formations[side]
        body += f"{side}_NumberOfFormations={len(keep)}\n"
        for i, (units, tail) in enumerate(keep, 1):
            body += f"{side}_Formation{i}=" + ",".join(renamed[u] for u in units) + tail + "\n"

    # --- assemble ------------------------------------------------------------
    out = []
    for header, sec_body in sections:
        if header is None:
            out.append(sec_body)
            continue
        name = header[1:-1]
        if name == "Mission":
            out.append(header + "\n" + body)
        elif name.startswith("Language_"):
            lines = []
            for line in sec_body.splitlines():
                m = re.match(r"^((?:Taskforce[12]|Neutral)\w*?\d+)(\w*Override)=(.*)$", line.strip())
                if m:
                    if m.group(1) in renamed:       # follow the renumbering
                        lines.append(f"{renamed[m.group(1)]}{m.group(2)}={m.group(3)}")
                    continue                        # drop overrides for dropped units
                if re.match(r"^(Name|ShortName|Description)=", line.strip()):
                    key = line.split("=")[0].strip()
                    if key == "Name":
                        lines.append(f"Name={scenario['title']}")
                        continue
                    if key == "Description":
                        lines.append(f"Description={scenario['desc']}")
                        continue
                lines.append(line)
            out.append(header + "\n" + "\n".join(lines).rstrip("\n") + "\n\n")
        elif re.fullmatch(r"(?:Taskforce[12]|Neutral)(?:" + "|".join(UNIT_CLASSES) + r")\d+", name):
            if name in renamed:
                out.append(f"[{renamed[name]}]\n" + sec_body)
        else:
            out.append(header + "\n" + sec_body)
    return "".join(out), counters


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="mission name (default: data/active-mission.txt)")
    ap.add_argument("--list", action="store_true", help="list the source's formations and exit")
    args = ap.parse_args()

    name = args.source or next(
        l.strip() for l in (ROOT / "data" / "active-mission.txt").read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.startswith("#"))
    src = MISSIONS / f"{name}.ini"
    if not src.exists():
        sys.exit(f"source mission not found: {src.relative_to(ROOT)}")
    text = src.read_text(encoding="utf-8-sig", errors="replace")

    if args.list:
        formations = parse_formations({h: b for h, b in split_sections(text) if h}["[Mission]"])
        print(f"{name}:")
        for side in SIDES:
            for units, tail in formations[side]:
                print(f"  {side:<11} {formation_name(tail):<28} {len(units):>2} units")
        return

    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    print(f"source: {name}  (not modified)\n")
    for scenario in SCENARIOS:
        out_text, counters = build(text, scenario)
        target = SCENARIO_DIR / f"{scenario['file']}.ini"
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out_text)
        total = sum(counters.values())
        detail = ", ".join(f"{n} {c.replace('Taskforce1', 'blue ').replace('Taskforce2', 'red ').replace('Neutral', 'neutral ')}"
                           for c, n in sorted(counters.items()) if n)
        print(f"  {scenario['file']:<34} {total:>3} units  ({detail})")
    print(f"\n{len(SCENARIOS)} scenarios in {SCENARIO_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
