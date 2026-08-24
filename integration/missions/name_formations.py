#!/usr/bin/env python3
"""Give placeholder formations a name that says what they are.

The mission editor labels new groups "Group Name 7", "Group Name 28" and so
on, which is what the tacmap then shows. This replaces those placeholders
with a name derived from what the group actually CONTAINS - a carrier group,
an S-400 site, a bomber flight - so the map reads properly.

Only placeholder labels are touched: anything you named yourself
("Carrier Group A", "RAN Inshore Screen", "Bulk Carrier") is left exactly as
it is. Editor placeholders are recognised by pattern; a few legacy scratch
labels of our own are listed in LEGACY_PLACEHOLDERS so they get upgraded too.

Nothing but the label field of a formation line changes - members, shape,
spacing and OverrideSpawnPositions are preserved verbatim.

Usage (repo root):
    python3 integration/missions/name_formations.py --mission "NORTHERN FRONT III"
    python3 integration/missions/name_formations.py --mission "NORTHERN FRONT III" --write
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_civ_traffic import active_mission  # noqa: E402

MISSIONS = Path(__file__).resolve().parent

PLACEHOLDER = re.compile(r"^(group name\s*\d*|new group\s*\d*|unnamed\s*\d*|)$", re.I)
LEGACY_PLACEHOLDERS = re.compile(r"^baddies\s*\d*$", re.I)

# Nation flavour from the unit-id prefix.
NATIONS = [
    (("plan_", "pla_", "plaf_", "plaaf_"), "PLAN"),
    (("ru_", "rfn_", "wp_", "vmf_"), "Russian"),
    (("usn_", "usaf_", "usa_"), "US"),
    (("ran_",), "RAN"),
    (("js_", "jmsdf_"), "JMSDF"),
]

# First rule that matches the group's unit types wins, so the most
# characteristic unit decides the name.
RULES = [
    (("ssbn",),                              "{nation} SSBN Group"),
    (("cvn", "_cv_", "carrier"),             "{nation} Carrier Group"),
    (("lpd", "lha", "lhd", "lst"),           "{nation} Amphibious Group"),
    (("sa-21", "s-400", "s400"),             "S-400 SAM Site"),
    (("thaad", "patriot", "mim-104"),        "Air Defence Battery"),
    (("ss-26", "iskander", "scud", "sejjil"), "Ballistic Missile Battery"),
    (("rubezh", "hy-4", "ssm", "bastion"),   "Coastal Missile Site"),
    (("hq-9", "sa-8", "sa-4", "sa-6", "spaa", "aaa", "zsu"), "Air Defence Site"),
    (("shahed", "drone", "uav"),             "Drone Launch Site"),
    (("depot", "warehouse", "fueltank", "tgt_"), "Logistics Site"),
    (("ssn", "ssk", "ssg", "submarine"),     "{nation} Submarine Group"),
    (("ddg", "ffg", "rkr", "cg_"),           "{nation} Surface Action Group"),
    (("mbt", "apc", "tank", "car_"),         "Ground Element"),
]

# Aircraft groups are named after the type they fly.
AIRFRAMES = [
    ("tu-95", "Tu-95 Bomber Flight"), ("tu-160", "Tu-160 Bomber Flight"),
    ("tu-22", "Tu-22M Bomber Flight"), ("h-6", "H-6 Bomber Flight"),
    ("b-52", "B-52 Bomber Flight"), ("b-1b", "B-1B Bomber Flight"),
    ("b-2", "B-2 Flight"), ("j16", "J-16 Flight"), ("j-16", "J-16 Flight"),
    ("j20", "J-20 Flight"), ("j-20", "J-20 Flight"), ("j10", "J-10 Flight"),
    ("j-10", "J-10 Flight"), ("j11", "J-11 Flight"), ("j-11", "J-11 Flight"),
    ("j15", "J-15 Flight"), ("j-15", "J-15 Flight"),
    ("su-57", "Su-57 Flight"), ("su-35", "Su-35 Flight"), ("su-30", "Su-30 Flight"),
    ("su-27", "Su-27 Flight"), ("su-24", "Su-24 Flight"), ("mig-31", "MiG-31 Flight"),
    ("mig-29", "MiG-29 Flight"), ("f-35", "F-35 Flight"), ("f-22", "F-22 Flight"),
    ("f-15", "F-15 Flight"), ("f-16", "F-16 Flight"), ("fa-18", "Super Hornet Flight"),
    ("ea-18", "Growler Flight"), ("p8", "P-8 Patrol"), ("p-8", "P-8 Patrol"),
    ("kj-", "AEW Flight"), ("a-50", "AEW Flight"), ("e-7", "AEW Flight"),
    ("e-2", "AEW Flight"), ("e-3", "AEW Flight"),
]


def nation_of(types):
    for prefixes, name in NATIONS:
        if any(t.startswith(prefixes) for t in types):
            return name
    return "Enemy"


def name_for(types, kind):
    """A descriptive name for a group of these unit types."""
    blob = " ".join(types).lower()
    nation = nation_of(types)
    if kind == "Aircraft":
        for token, label in AIRFRAMES:
            if token in blob:
                return label
        return f"{nation} Air Group"
    for tokens, template in RULES:
        if any(tok in blob for tok in tokens):
            return template.format(nation=nation)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", default=active_mission(),
                    help="mission name without .ini "
                         "(default: whatever data/active-mission.txt names)")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--include-legacy", action="store_true", default=True,
                    help="also upgrade our own old scratch labels (BADDIES n)")
    args = ap.parse_args()

    path = MISSIONS / f"{args.mission}.ini"
    if not path.exists():
        sys.exit(f"no such mission: {path}")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    text = text.replace("\r\n", "\n")

    # Map every unit section to its Type, so a formation can be described.
    unit_type = {}
    for chunk in re.split(r"(?=^\[)", text, flags=re.M):
        h = re.match(r"^\[((?:Taskforce\d+|Neutral)\w*?\d+)\]", chunk)
        if not h:
            continue
        ty = re.search(r"^Type=(\S+)", chunk, re.M)
        if ty:
            unit_type[h.group(1)] = ty.group(1)

    renames = []

    def rewrite(m):
        key, value = m.group(1), m.group(2)
        fields = value.split("|")
        if len(fields) < 2:
            return m.group(0)
        label = fields[1].strip()
        is_placeholder = bool(PLACEHOLDER.match(label)) or (
            args.include_legacy and bool(LEGACY_PLACEHOLDERS.match(label)))
        if not is_placeholder:
            return m.group(0)
        members = [x.strip() for x in fields[0].split(",") if x.strip()]
        types = [unit_type.get(x, "") for x in members]
        kind = ("Aircraft" if all("Aircraft" in x for x in members)
                else "LandUnit" if all("LandUnit" in x for x in members) else "Vessel")
        new = name_for([t for t in types if t], kind)
        if not new:
            return m.group(0)
        fields[1] = new
        renames.append(f"{key}: '{label}' -> '{new}'  ({len(members)} units)")
        return f"{key}={'|'.join(fields)}"

    out = re.sub(r"^(\w+_Formation\d+)=(.+)$", rewrite, text, flags=re.M)

    for r in renames:
        print("  " + r)
    if not renames:
        print(f"{args.mission}: no placeholder formations to name")
    elif args.write:
        path.write_text(out, encoding="utf-8", newline="\n")
        print(f"{args.mission}: {len(renames)} formation(s) named")
    else:
        print(f"{args.mission}: {len(renames)} would change - re-run with --write")


if __name__ == "__main__":
    main()
