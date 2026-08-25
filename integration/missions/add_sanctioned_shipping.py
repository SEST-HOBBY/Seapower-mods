#!/usr/bin/env python3
"""Add a sanctioned tanker fleet, with undercover escorts, to the enemy side.

Eight large merchants of eastern origin lift from the mission's seized rigs
and run north-west out of the operating area. They are EMCON-silent, will not
respond, and are valid, destroyable targets - plus four escorts posing as more
merchants. Twelve hulls total, all appended to Taskforce2.

WHY TASKFORCE2 AND NOT NEUTRAL. Two reasons, both from this repo's own data:
  - Targetable: Taskforce2 is EnemyTaskforce, so engaging them is legal for
    the AI and costs no neutral-engagement penalty.
  - The [SANCTIONED] tag survives: the mission editor STRIPS NameOverride
    from Neutral units when it saves (documented in add_civ_depth.py), but
    taskforce overrides survive - the seized-rig names prove it.

THE FLEET. Merchants: RadarsActive=False, WeaponStatus=Hold - dark, dumb,
non-reactive. Escorts are vanilla hulls built for exactly this masquerade:
  - wp_ms_andizhan_armed x2 - Andizhan freighter with concealed 57mm/14.5mm.
  - wp_ms_roro_b          x1 - RoRo with SA-8 and SA-N-5 pop-up SAMs.
  - wp_ms_mercur_decoy    x1 - containerised deception emitters mimicking a
    Soviet combatant's radars. The ONE ship radiating (RadarsActive=True),
    because radiating wrong is its entire job; the armed pair stay dark with
    WeaponStatus=Tight so they unmask only when the fleet is engaged.

GEOGRAPHY IS READ, NOT ASSUMED. The lift clusters anchor on the mission's own
seized rigs - every Taskforce2 land unit of Type=civ_spar_rig_helo, wherever
the editor has them today. The transit pair runs NW from the rig centroid.
No rigs in the mission means nothing to add, and the pass says so and exits.

Idempotent: the escort hulls appear in no mission otherwise, so their
presence (or any of our NameOverride names, if an editor round-trip has not
eaten them) marks the pass as already run. Only appends and count bumps -
no existing line is rewritten.

Usage (repo root):
    python3 integration/missions/add_sanctioned_shipping.py --mission "NORTHERN FRONT III FINAL"
    python3 integration/missions/add_sanctioned_shipping.py --mission "NORTHERN FRONT III FINAL" --write
"""
import argparse
import re
import sys
from pathlib import Path

MISSIONS = Path(__file__).resolve().parent
WPT_Y = "220.4727"          # the y the editor writes on every vessel waypoint

# (hull, variant, name, short) - names in the flag-of-convenience register the
# real shadow fleet uses. Merchants carry the tag; escorts carry cover names.
MERCHANTS = [
    ("civ_ms_ritina",           "Variant14", "MT Sakhalin Dawn [SANCTIONED]",  "SAK DAWN"),
    ("civ_ms_slavyansk",        "Variant6",  "MV Progress Aral [SANCTIONED]",  "PROGRESS"),
    ("civ_ms_ritina",           "Variant38", "MT Ocean Faye [SANCTIONED]",     "OCN FAYE"),
    ("civ_ms_kommunist",        "Variant12", "MV Krasny Vostok [SANCTIONED]",  "KRASNY V"),
    ("civ_ms_bulk",             "Variant51", "MV Kittiwake Star [SANCTIONED]", "KITTIWAKE"),
    ("civ_ms_metallurg_anosov", "Variant9",  "MV Amber Nine [SANCTIONED]",     "AMBER 9"),
    ("civ_ms_ritina",           "Variant77", "MT Turbo Voyager [SANCTIONED]",  "TURBO V"),
    ("civ_ms_irkutsk",          "Variant17", "MV Lena Horizon [SANCTIONED]",   "LENA HZN"),
]
ESCORTS = [
    ("wp_ms_andizhan_armed", "Variant2", "MV Fergana Trader",    "FERGANA"),
    ("wp_ms_andizhan_armed", "Variant3", "MV Andizhan Pride",    "ANDIZHAN"),
    ("wp_ms_roro_b",         "Variant1", "MV Vostochny Express", "VOSTOCHNY"),
    ("wp_ms_mercur_decoy",   "Variant4", "MV Baltika Line",      "BALTIKA"),
]
ALL_NAMES = [n for _, _, n, _ in MERCHANTS + ESCORTS]
MARKER_TYPES = {"wp_ms_andizhan_armed", "wp_ms_roro_b", "wp_ms_mercur_decoy"}


def find_rigs(text):
    """Positions of every seized rig, straight from the mission."""
    rigs = []
    for m in re.finditer(r"^\[Taskforce2LandUnit\d+\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S):
        if re.search(r"^Type=civ_spar_rig_helo\s*$", m.group(1), re.M):
            p = re.search(r"^RelativePositionInNM=([-\d.]+),\w+,([-\d.]+)", m.group(1), re.M)
            if p:
                rigs.append((float(p.group(1)), float(p.group(2))))
    return rigs


def vessel(idx, hull, variant, x, z, heading, telegraph, wpts,
           radars=False, status="Hold"):
    lines = [f"[Taskforce2Vessel{idx}]",
             f"Type={hull}",
             f"VariantReference={variant}",
             "UnlimitedFuel=False",
             f"WeaponStatus={status}",
             f"RadarsActive={'True' if radars else 'False'}",
             "CrewSkill=Trained",
             "Morale=3",
             f"RelativePositionInNM={x:.2f},0,{z:.2f}",
             f"Telegraph={telegraph}",
             f"Heading={heading}"]
    if wpts:
        lines.append("Waypoints=" + "|".join(f"{wx:.3f},{WPT_Y},{wz:.3f}{sfx}"
                                             for wx, wz, sfx in wpts))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mission", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    f = MISSIONS / f"{args.mission}.ini"
    if not f.exists():
        sys.exit(f"no such mission: {f}")
    text = f.read_text(encoding="utf-8", errors="replace")

    present = set(re.findall(r"^Type=(\S+)", text, re.M))
    if (MARKER_TYPES & present
            or any(f"NameOverride={n}" in text for n in ALL_NAMES)):
        print("sanctioned shipping already present - nothing to do")
        return

    rigs = find_rigs(text)
    if not rigs:
        # A graceful skip, not a failure - this pass runs inside the
        # refresh-mission chain for every mission, most of which have no rigs.
        print("no seized rigs (Taskforce2 civ_spar_rig_helo) in this mission - "
              "nothing for the fleet to lift from, skipping")
        return
    print(f"anchoring on {len(rigs)} seized rig(s): "
          + ", ".join(f"({x:.0f},{z:.0f})" for x, z in rigs))

    cx = sum(x for x, _ in rigs) / len(rigs)
    cz = sum(z for _, z in rigs) / len(rigs)
    # NW-bound exit lane from the rig centroid, matching the neutral lanes' scale.
    lane = [(cx - 140, cz + 85), (cx - 260, cz + 160)]

    n0 = max(int(m) for m in re.findall(r"^\[Taskforce2Vessel(\d+)\]", text, re.M))
    sections, overrides, groups = [], [], []
    idx = n0

    # --- two merchants alongside each rig, round-robin -----------------------
    per_rig = [[] for _ in rigs]
    for i, (hull, var, name, short) in enumerate(MERCHANTS[:6]):
        rx, rz = rigs[i % len(rigs)]
        side = 1 if i % 2 else -1
        x, z = rx + side * 1.6, rz + side * 1.1
        idx += 1
        # laden crawl toward the exit lane; SetTelegraph once clear of the rig
        sections.append(vessel(idx, hull, var, x, z, -49, 1,
                               [(x - 6, z + 4, "/SetTelegraph,2"),
                                (lane[0][0], lane[0][1], ""),
                                (lane[1][0], lane[1][1], "")]))
        overrides.append((idx, name, short))
        per_rig[i % len(rigs)].append(idx)

    # --- the pair already in transit ------------------------------------------
    transit = []
    for j, (hull, var, name, short) in enumerate(MERCHANTS[6:]):
        x, z = cx - 118 + j * 4.5, cz + 68 - j * 3.5
        idx += 1
        sections.append(vessel(idx, hull, var, x, z, -49, 3,
                               [(lane[0][0], lane[0][1], ""),
                                (lane[1][0], lane[1][1], "")]))
        overrides.append((idx, name, short))
        transit.append(idx)

    # --- escorts --------------------------------------------------------------
    # armed Andizhans shadow the first two lift clusters, dark, weapons Tight
    for k in range(2):
        hull, var, name, short = ESCORTS[k]
        rx, rz = rigs[k % len(rigs)]
        idx += 1
        sections.append(vessel(idx, hull, var, rx - 3.2, rz - 2.4, -49, 1,
                               [(rx - 8, rz + 2, "/SetTelegraph,2"),
                                (lane[0][0], lane[0][1], ""),
                                (lane[1][0], lane[1][1], "")], status="Tight"))
        overrides.append((idx, name, short))
        per_rig[k % len(rigs)].append(idx)
    # SAM RoRo rides with the transit pair
    hull, var, name, short = ESCORTS[2]
    idx += 1
    sections.append(vessel(idx, hull, var, cx - 121, cz + 61, -49, 3,
                           [(lane[0][0], lane[0][1], ""),
                            (lane[1][0], lane[1][1], "")], status="Tight"))
    overrides.append((idx, name, short))
    transit.append(idx)
    # the decoy orbits the last rig, radiating like a warship group
    hull, var, name, short = ESCORTS[3]
    rx, rz = rigs[-1]
    idx += 1
    sections.append(vessel(idx, hull, var, rx - 4.8, rz + 3.5, 120, 2,
                           [(rx + 3, rz + 6, ""), (rx - 6, rz - 4, "")],
                           radars=True, status="Tight"))
    overrides.append((idx, name, short))
    per_rig[len(rigs) - 1].append(idx)

    added = idx - n0
    assert added == len(MERCHANTS) + len(ESCORTS), added

    # --- splice ---------------------------------------------------------------
    # counts
    text = re.sub(r"^NumberOfTaskforce2Vessels=\d+$",
                  f"NumberOfTaskforce2Vessels={idx}", text, count=1, flags=re.M)
    # formations, one per lift cluster plus the transit group
    fm = re.search(r"^Taskforce2_NumberOfFormations=(\d+)$", text, re.M)
    fnum = int(fm.group(1))
    rig_labels = ["Bayu-Undan", "Ichthys", "Montara"]
    flines = ""
    for r, members in enumerate(per_rig):
        if not members:
            continue
        fnum += 1
        label = rig_labels[r] if r < len(rig_labels) else f"Rig {r+1}"
        flines += (f"Taskforce2_Formation{fnum}="
                   + ",".join(f"Taskforce2Vessel{m}" for m in members)
                   + f"|Sanctioned Lift {label}|Loose|1.5\n")
    fnum += 1
    flines += (f"Taskforce2_Formation{fnum}="
               + ",".join(f"Taskforce2Vessel{m}" for m in transit)
               + "|Sanctioned Transit Group|Loose|1.5\n")
    text = re.sub(r"^Taskforce2_NumberOfFormations=\d+$",
                  f"Taskforce2_NumberOfFormations={fnum}", text, count=1, flags=re.M)
    last_f = list(re.finditer(r"^Taskforce2_Formation\d+=[^\n]*\n", text, re.M))[-1]
    text = text[:last_f.end()] + flines + text[last_f.end():]

    # name overrides ride in [Mission] beside the seized-rig ones
    olines = "".join(f"Taskforce2Vessel{i}NameOverride={n}\n"
                     f"Taskforce2Vessel{i}ShortNameOverride={s}\n"
                     for i, n, s in overrides)
    anchor = list(re.finditer(r"^Taskforce2LandUnit\d+(?:Short)?NameOverride=[^\n]*\n",
                              text, re.M))
    if anchor:
        pos = anchor[-1].end()
    else:
        pos = re.search(r"^\[Mission\][^\n]*\n(?:Name=[^\n]*\n)?", text, re.M).end()
    text = text[:pos] + olines + text[pos:]

    # the vessel sections themselves, straight after the current last one
    tail = re.search(rf"^\[Taskforce2Vessel{n0}\]\n.*?(?=^\[)", text, re.M | re.S)
    text = text[:tail.end()] + "".join(sections) + text[tail.end():]

    print(f"added {added} vessels (8 sanctioned merchants, 4 undercover escorts), "
          f"{len([m for m in per_rig if m]) + 1} formations")
    if args.write:
        f.write_text(text, encoding="utf-8")
        print(f"written: {f}")
    else:
        print("dry run - pass --write to apply")


if __name__ == "__main__":
    main()
