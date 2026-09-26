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

A scenario may also declare "extras", ships the source does not contain (see
the injection notes below). An extra is written only when some mod or SEST
pack in the load order defines its type, so build the packs first
(tools/build_all.py): the SEST packs are resolved from their consolidated
output.

    python3 integration/missions/make_scenarios.py            # build all
    python3 integration/missions/make_scenarios.py --list     # show formations
    python3 integration/missions/make_scenarios.py --source "OTHER MISSION"
"""
import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_civ_traffic import winning_file  # noqa: E402

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
        # HMAS Supply with the RAN screen she actually serves.
        "extras": [{"side": "Taskforce1", "type": "ran_aor_supply",
                    "formation": "RAN Inshore Screen"}],
    },
    {
        "file": "SEST NF3 - Bomber Stream",
        "title": "Bomber Stream",
        "desc": ("Nine H-6K Zhanshen in three packages and six Tu-95MS are inbound. Two F-22 "
                 "flights and their tankers are all that stands between them and the coast. "
                 "Pure air intercept - no surface units, no land clutter. Carved from NORTHERN "
                 "FRONT III."),
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
        # Blue already sails with the Kilauea AND the Sacramento; red had no
        # supplier at all. The Type 901 is the PLAN's actual carrier-group AOE,
        # so this evens a lopsided fight rather than inventing one.
        "extras": [{"side": "Taskforce2", "type": "plan_aor_type901",
                    "formation": "PLAN Carrier Group"}],
    },
    {
        "file": "SEST NF3 - SEAD over the Shelf",
        "title": "SEAD over the Shelf",
        "desc": ("An S-400 site and a supporting air-defence battery cover the shelf. Four "
                 "B-52s with ARRW and cruise missiles, escorted by four F-15EX carrying sixteen "
                 "AIM-260 each, have to open the corridor. Carved from NORTHERN FRONT III."),
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
        # An ASW hunt is the one fight that burns torpedoes, and the T-AKE
        # stocks 72 AirTorpedo with no size ceiling, second only to the
        # Kilauea's 90. The Type 903A is its RED counterpart: same job, less
        # than half the pool, and it makes the fight symmetric - both sides now
        # have an auxiliary worth sinking, which is the whole point of putting
        # one in an ASW scenario.
        "extras": [{"side": "Taskforce1", "type": "usn_take_lewis_clark",
                    "formation": "NATO Fleet A"},
                   {"side": "Taskforce2", "type": "plan_aor_type903a",
                    "formation": "PLAN SSBN Group"}],
    },
    # --- second wave: the formations the first five left on the table ---------
    # The source has 38 formations and the first five carve 24 of them. These
    # six take the other 14, and deliberately cover mission TYPES the first
    # five do not: ballistic-missile defence, a Euro-NATO surface fight, carrier
    # air (as opposed to Carrier Duel's surface gunline), close air support
    # against a coastal battery, fifth-generation air superiority, and a
    # deep-strike corridor through a different IADS than SEAD over the Shelf
    # opens.
    {
        "file": "SEST NF3 - Ballistic Shield",
        "title": "Ballistic Shield",
        "desc": ("Four DF-26B launchers and a mixed Iskander/Scud/Shahed battery range on the "
                 "northern bases. Darwin and Scherger have THAAD and PAC-3 and no depth to "
                 "trade - every leaker lands on an airfield. Carved from NORTHERN FRONT III."),
        "tf1": ["Darwin International Airport", "RAAF Base Scherger"],
        "tf2": ["Eastern AS Ballistic", "Ballistic Missile Battery"],
        "neutrals": False,
    },
    {
        "file": "SEST NF3 - Northern Fleet Sortie",
        "title": "Northern Fleet Sortie",
        "desc": ("Varyag, an improved Kirov and three modern escorts against a Euro-NATO group "
                 "of a Lafayette OPV, a K130, an Iver Huitfeldt and an F127. Five warships "
                 "against four, and NATO is also shepherding the Algol - a 288 m sealift hull "
                 "with no weapons that the whole group exists to keep alive. Carved from "
                 "NORTHERN FRONT III."),
        "tf1": ["NATO Fleet B"],
        "tf2": ["Russian Carrier Group"],
        "neutrals": False,
        # NATO brings the Algol already. Boris Chilikin is the Soviet fleet's
        # own purpose-built AOR and the deepest SovietAdvancedASM stock in the
        # pack (24), the category of the improved Kirov's SS-N-26. The Varyag's
        # SS-N-19 stays out of reach on purpose: the Chilikin's size ceiling
        # sits below the Granit (see common/ras.py).
        "extras": [{"side": "Taskforce2", "type": "wp_vt_boris_chilikin",
                    "formation": "Russian Carrier Group"}],
    },
    {
        "file": "SEST NF3 - Fujian Strike",
        "title": "Fujian Strike",
        "desc": ("Type 003 Fujian with a Type 055, a Type 09X boat, Red October and eight "
                 "J-15D against a Ford group. Where Carrier Duel is two gunlines in the same "
                 "water, this one is decided in the air. Carved from NORTHERN FRONT III."),
        "tf1": ["Carrier Group A"],
        "tf2": ["CN Carrier group", "Eastern Strike AS"],
        "neutrals": False,
        # The most on-the-nose injection in the set: the Type 901 Fuyu exists
        # to keep station with exactly this carrier, and a Ford group that
        # cannot reach it wins the sortie war by attrition instead.
        "extras": [{"side": "Taskforce2", "type": "plan_aor_type901",
                    "formation": "CN Carrier group"}],
    },
    {
        "file": "SEST NF3 - Coastal Ambush",
        "title": "Coastal Ambush",
        "desc": ("An HY-4 coastal battery with a ZSU-23-4, a Shahed launcher and fuel bunkers "
                 "sits on the headland. Two A-10Cs and the RAN inshore screen have to dig it "
                 "out. Thirteen units, one hill, no room to be clever. Carved from NORTHERN "
                 "FRONT III."),
        "tf1": ["A-10-1", "RAN Inshore Screen"],
        "tf2": ["Coastal Missile Site"],
        "neutrals": False,
    },
    {
        "file": "SEST NF3 - Fifth Generation Sweep",
        "title": "Fifth Generation Sweep",
        "desc": ("Three J-50 under six Su-35S and six J-16A, against eight Raptors and their "
                 "tankers. Stealth on both sides, nothing on the surface, and the tankers are "
                 "the only thing making the Raptors' fuel arithmetic work. Carved from "
                 "NORTHERN FRONT III."),
        "tf1": ["F-22 Group 1", "F-22 Group 2", "KC Group 1"],
        "tf2": ["Eastern Stealth Cover", "Eastern Strike Cover", "J-16 Flight"],
        "neutrals": False,
    },
    {
        "file": "SEST NF3 - Deep Strike Corridor",
        "title": "Deep Strike Corridor",
        "desc": ("A layered eastern IADS - HQ-16A, HQ-22A, HQ-19, a DF-21C and three Sejjil "
                 "launchers around a modern airbase. A strike package, its F-15 escort and two "
                 "A-10Cs have to open a corridor through it. A harder, deeper problem than SEAD "
                 "over the Shelf, against a different air-defence mix. Carved from NORTHERN "
                 "FRONT III."),
        "tf1": ["Strike Group 2", "F-15 Escort", "A-10-1"],
        "tf2": ["Eastern AA AS"],
        "neutrals": False,
    },
]


# ---------------------------------------------------------------------------
# Injecting units the parent mission does not contain.
#
# Carving can only ever subtract. Exercising SEST Replenishment At Sea needs
# the opposite: a supplier standing with a group that has none. Three of the
# source's eight warship groups already sail with one (Carrier Group A with
# both the Kilauea and the Sacramento, NATO Fleet B with the Algol, CN Carrier
# group with the Boris Chilikin) - so injection is aimed at the groups that do
# not, which is where it changes the fight rather than padding it. The one
# exception is the Type 901 in Fujian Strike, which joins the carrier it was
# built to serve.
#
# Most extras are SEST Replenishment's own hulls. One whose type no mod or
# SEST pack in the load order defines is left out with a note, never written
# as a unit the game cannot load, so a scenario still loads on a checkout
# that has not built the packs.
#
# A vessel section is self-contained, so writing one is mechanical. The only
# judgement is WHERE, and the honest answer is: with the group. The ship is
# placed at the centroid of the formation it joins, nudged clear of the nearest
# hull, on the formation's own heading, and appended to that formation's unit
# list so the AI keeps it in station rather than sailing it independently.

VESSEL_TEMPLATE = """[{section}]
Type={type}
VariantReference={variant}
UnlimitedFuel=False
CrewSkill=Trained
Morale=3
RelativePositionInNM={x:.2f},0,{z:.2f}
Telegraph=3
Heading={heading}
"""


def unit_position(body):
    m = re.search(r"^RelativePositionInNM=([-\d.]+),([-\d.]+),([-\d.]+)", body, re.M)
    return (float(m.group(1)), float(m.group(3))) if m else None


def unit_heading(body):
    m = re.search(r"^Heading=(-?\d+)", body, re.M)
    return m.group(1) if m else "0"


def place_with_group(by_header, units):
    """(x, z, heading) for a ship joining `units`: their centre, clear of hulls.

    Spacing matters. These groups sit inside a few nautical miles of each
    other, so the offset is 0.6 nm - far enough that the new hull is not
    stacked on an escort, close enough that it is unambiguously part of the
    formation. If 0.6 nm still lands on someone, it walks around the circle
    until it does not.
    """
    spots = [p for p in (unit_position(by_header.get(f"[{u}]", "")) for u in units) if p]
    if not spots:
        raise SystemExit(f"cannot place a unit with {units}: no positions found")
    cx = sum(s[0] for s in spots) / len(spots)
    cz = sum(s[1] for s in spots) / len(spots)
    headings = [unit_heading(by_header.get(f"[{u}]", "")) for u in units]
    heading = max(set(headings), key=headings.count)

    for step in range(12):
        angle = math.radians(step * 30)
        x, z = cx + 0.6 * math.cos(angle), cz + 0.6 * math.sin(angle)
        if all(math.dist((x, z), s) > 0.3 for s in spots):
            return x, z, heading
    return cx + 0.6, cz, heading


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

    # --- inject units the source does not have -------------------------------
    # Numbered after the carried units so the carve's numbering is untouched,
    # and pushed onto the target formation's list so the group sails as one.
    extra_sections, injected, skipped = [], [], []
    for extra in scenario.get("extras", ()):
        side = extra["side"]
        target = [(u, tail) for u, tail in kept_formations[side]
                  if formation_name(tail) == extra["formation"]]
        if not target:
            raise SystemExit(f"{scenario['file']}: extra {extra['type']} names formation "
                             f"{extra['formation']!r}, which this scenario does not carry")
        if winning_file(f"vessels/{extra['type']}.ini") is None:
            skipped.append(extra)
            continue
        injected.append(extra)
        units, _ = target[0]
        x, z, heading = place_with_group(by_header, units)
        cls = f"{side}Vessel"
        counters[cls] = counters.get(cls, 0) + 1
        section = f"{cls}{counters[cls]}"
        placeholder = f"__extra__{section}"
        renamed[placeholder] = section
        units.append(placeholder)
        extra_sections.append(VESSEL_TEMPLATE.format(
            section=section, type=extra["type"],
            variant=extra.get("variant", "Variant1"), x=x, z=z, heading=heading))

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
    # Injected sections go last. Unit sections are looked up by name, not by
    # position in the file, so appending is safe and keeps the carved body
    # byte-identical to what a pure carve would have produced.
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
            # The briefing's text pane shows the Description, and a source
            # saved without one (NORTHERN FRONT III has none) would leave the
            # scenario's pane blank. Give it one, beside the Name.
            if not any(l.startswith("Description=") for l in lines):
                at = next((i + 1 for i, l in enumerate(lines) if l.startswith("Name=")), 0)
                lines.insert(at, f"Description={scenario['desc']}")
            out.append(header + "\n" + "\n".join(lines).rstrip("\n") + "\n\n")
        elif re.fullmatch(r"(?:Taskforce[12]|Neutral)(?:" + "|".join(UNIT_CLASSES) + r")\d+", name):
            if name in renamed:
                out.append(f"[{renamed[name]}]\n" + sec_body)
        else:
            out.append(header + "\n" + sec_body)
    body_text = "".join(out)
    if extra_sections:
        body_text = body_text.rstrip("\n") + "\n" + "".join(extra_sections)
    return body_text, counters, injected, skipped


def write_readme(source_name, built):
    """Regenerate scenarios/README.md from what was just built.

    The file always CLAIMED to be generated, but it was hand-maintained, so
    it could drift: its "the smallest of the set" sat on Carrier Duel, and
    nothing would have moved it when a smaller scenario was added. Unit
    counts come from the build itself now, so the table cannot describe
    scenarios that do not exist or miss ones that do. `built` is [(scenario, total, injected)],
    where `injected` lists only the extras actually written.
    """
    smallest = min(built, key=lambda b: b[1])
    rows = []
    for scenario, total, injected in built:
        blurb = scenario["desc"].replace("Carved from NORTHERN FRONT III.", "").strip()
        if scenario is smallest[0]:
            blurb += " **The smallest of the set.**"
        if scenario["neutrals"]:
            blurb += " Includes the full civilian layer."
        for extra in injected:
            blurb += (f" **+{extra['type']}** injected into {extra['formation']}"
                      " (not in the parent mission).")
        rows.append(f"| **{scenario['title']}** | {total} | {blurb} |")

    ras = ""
    if any(injected for _, _, injected in built):
        ras = """
Entries marked **+<type> injected** carry a unit the parent mission does not have. Carving can
only subtract, and three of the source's eight warship groups already sail with a supplier
(Carrier Group A with both the Kilauea and the Sacramento, NATO Fleet B with the Algol, CN
Carrier group with the Boris Chilikin) — so injection is aimed at the groups that had none, to
exercise SEST Replenishment At Sea where it actually changes the fight. The one exception is the
Type 901, which joins the Fujian, the carrier it was built to serve. Each injected ship is placed
at the centroid of the formation it joins, nudged clear of the nearest hull, on the formation's
own heading, and appended to that formation so the AI keeps it in station. An extra is written
only when a mod or SEST pack in the load order defines its type.
"""

    body = f"""# NF3 Scenarios

Small standalone missions carved out of **{source_name}** by
`../make_scenarios.py`. Every unit keeps the type, loadout, position and waypoints it
has in the parent mission — these are the same forces, fought in isolation.

**Generated, including this file. Do not edit by hand.** Change the scenario list in
`make_scenarios.py` and re-run; the parent mission is never modified, so re-importing a
newer save and regenerating gives you scenarios that match it.

| Scenario | Units | The fight |
|---|---|---|
""" + "\n".join(rows) + "\n" + ras + f"""
## Regenerating

Build the packs first: extras are resolved against the load order, and the SEST packs
against their consolidated output.

```bash
python3 tools/build_all.py                                # the packs the extras come from
python3 integration/missions/make_scenarios.py            # build all + this README
python3 integration/missions/make_scenarios.py --list     # show the source's formations
python3 integration/missions/build_briefing_maps.py       # redraw the briefing maps
python3 tools/check_scenarios.py                          # validate every scenario
```

The generator renumbers each unit class from 1, rewrites the `Taskforce<N>_Formation`
lines and the `<Unit>NameOverride` keys to match, and recomputes every `NumberOf*` count —
the only cross-references a mission file has.

## In game

{len(built)} scenarios. They deploy with everything else (`tools\\install-sest-packs.ps1`
copies the missions under `integration\\missions`, this folder included, and the
`_briefing` folder beside each) and appear in the mission list alongside the full missions,
prefixed `SEST NF3 -`. The `scenarios/` subfolder is repo-side grouping only; the game
lists `user_missions` flat.
"""
    (SCENARIO_DIR / "README.md").write_text(body, encoding="utf-8")


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
    built = []
    for scenario in SCENARIOS:
        out_text, counters, injected, skipped = build(text, scenario)
        target = SCENARIO_DIR / f"{scenario['file']}.ini"
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out_text)
        total = sum(counters.values())
        detail = ", ".join(f"{n} {c.replace('Taskforce1', 'blue ').replace('Taskforce2', 'red ').replace('Neutral', 'neutral ')}"
                           for c, n in sorted(counters.items()) if n)
        print(f"  {scenario['file']:<34} {total:>3} units  ({detail})")
        for extra in injected:
            print(f"    + {extra['type']} with {extra['formation']}")
        for extra in skipped:
            print(f"    skipped {extra['type']}: not defined by any enabled mod")
        built.append((scenario, total, injected))
    write_readme(name, built)
    print(f"\n{len(SCENARIOS)} scenarios in {SCENARIO_DIR.relative_to(ROOT)} (README regenerated)")


if __name__ == "__main__":
    main()
