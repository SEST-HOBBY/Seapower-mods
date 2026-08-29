#!/usr/bin/env python3
"""Check that every weapon can actually be EMPLOYED, not merely resolved.

preflight walks references: does the id exist in the file that wins. This
walks contracts: given the round that actually loads, can the mount carrying
it actually shoot it? Those are different questions, and the gap between them
is where HMAS Warramunga sat on her NSMs for a whole mission with every
reference resolving perfectly.

That bug had a shape worth generalising. usn_rgm_184a is
MidCourseCorrection=3 - datalink midcourse - so its launcher must draw a
guidance channel from an associated sensor. The Anzac's MK141 blocks were
cloned from a donor firing vanilla's Harpoon (MidCourseCorrection=0, no
channel needed) and only the Ammunition= line was swapped. Nothing dangled;
the weapon simply never fired.

Every check here was calibrated against the collection before being trusted,
because a checker that cries wolf gets ignored:

  MCC=3 (datalink)     370 of 371 launcher blocks associate a sensor
  MCC=1 (radio cmd)    675 of 684 do
  MCC=2 (wire guided)   12 of 88 do - the wire IS the guidance, so wire-
                        guided rounds are EXEMPT here. Vanilla's own
                        submarines fire them from sensor-less tubes.

The exceptions at MCC=1/3 are SAM TELs (vanilla's SA-4/SA-6/SA-10 take their
channel from a separate battery radar vehicle) and ASW standoff rounds fired
at a datum, so both are allowed for by ALLOW below rather than by weakening
the rule.

    python3 tools/check_weapon_employment.py [mission name]

Exits non-zero if a weapon cannot be employed. Advisories print but pass.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import winning_file  # noqa: E402

UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units", "biologic")
MOUNT_KINDS = ("vessels", "submarines", "land_units")

# Findings verified benign, each with the evidence that settled it. Matching is
# by substring, so an entry pins one known case rather than muting a check.
ALLOW = {
    "usn_ssgn_virginia_blk5_vpm":
        "MCC=2 wire-guided rounds; vanilla submarines fire these from "
        "sensor-less tubes too (76 of 88 corpus-wide)",
    "ger_seaspider":
        "MCC=2 wire-guided anti-torpedo round, steered over its wire from the "
        "hull sonar picture",
    "usn_ea-18g_2020 (SEST_Growler_NGJ_MALICE/aircraft) WS1 -> WeaponMagazineM61":
        "upstream's own file, and correct in effect: the real EA-18G deletes "
        "the M61 (its bay holds the ALQ-218 receiver), so a gun with no "
        "magazine is a gun that never fires",
    "plan_j-15d (3486502935/aircraft)":
        "upstream writes |KH-31 against its own Kh-31Positions key - a case "
        "mismatch worth at most a ~17 cm seat offset on two YJ-91s; not worth "
        "overriding a 3000-line workshop aircraft file",
    "plan_cv_type_003 (3663564190/vessels) WeaponMagazine_FQF2500":
        "dead data: the FQF-2500 magazines hold Ammunition1_Count=0 and no "
        "weapon system references them",
    "plan_z-9d (3775128499/aircraft) loadout 'Transport'":
        "a transport fit carries no weapons by design",
}


def allowed(row):
    return next((why for key, why in ALLOW.items() if key in row), None)


def txt(p):
    return Path(p).read_text(encoding="utf-8-sig", errors="replace")


_ammo = {}


def ammo(aid):
    """Guidance and launch keys of the round that actually loads."""
    if aid not in _ammo:
        f = winning_file(f"ammunition/{aid}.ini")
        d = None
        if f:
            t = txt(f)

            def g(k, cast=str):
                m = re.search(rf"^{k}=([^/\s]+)", t, re.M)
                try:
                    return cast(m.group(1)) if m else None
                except ValueError:
                    return None

            d = {"gt": g("GuidanceType", int), "mcc": g("MidCourseCorrection", int),
                 "minalt": g("MinLaunchAltitude", float),
                 "maxalt": g("MaxLaunchAltitude", float)}
        _ammo[aid] = d
    return _ammo[aid]


_sensors = None


def sensor_defs():
    """SystemName -> capabilities, from the merged systems/sensors.ini stack."""
    global _sensors
    if _sensors is None:
        order = [l.strip() for l in txt(ROOT / "data/load-order.tokens.txt").splitlines()
                 if l.strip() and not l.startswith("#")]
        files = []
        for tok in order:
            if tok.startswith("SEST_"):
                files += sorted(ROOT.glob(f"integration/*/{tok}/systems/sensors.ini"))
            else:
                p = ROOT / "mods-source" / tok / "systems" / "sensors.ini"
                if p.exists():
                    files.append(p)
        files.append(ROOT / "mods-source/_vanilla/original/systems/sensors.ini")
        out = {}
        for f in files:                     # highest first; first wins
            for m in re.finditer(r"^\[([^\]]+)\]\n(.*?)(?=^\[|\Z)", txt(f), re.S | re.M):
                name = m.group(1).strip()
                if name in out:
                    continue

                def g(k, body=m.group(2)):
                    mm = re.search(rf"^{k}=([^/\s]+)", body, re.M)
                    return mm.group(1).strip() if mm else None

                out[name] = {"mode": g("Mode"), "wch": g("WeaponChannels")}
        _sensors = out
    return _sensors


def channels(name):
    try:
        return float((sensor_defs().get(name) or {}).get("wch") or 0)
    except ValueError:
        return 0


def weapon_blocks(text):
    """[WeaponSystem<name>] -> (name, body). Names carry hyphens: StrikeGBU-12."""
    return [(m.group(1), m.group(2)) for m in
            re.finditer(r"^\[WeaponSystem([^\]]+)\][^\n]*\n(.*?)(?=^\[)", text, re.S | re.M)]


def base_of(name):
    """'1StrikeGBU-12' -> '1'. Stations and seat groups live in the base block."""
    m = re.match(r"^(\d+)", name)
    return m.group(1) if m else name


def unit_sensors(text):
    out = {}
    for m in re.finditer(r"^\[SensorSystem(\d+)\][^\n]*\n(.*?)(?=^\[)", text, re.S | re.M):
        sn = re.search(r"^SystemName=(.+)$", m.group(2), re.M)
        if sn:
            out[int(m.group(1))] = sn.group(1).strip()
    return out


def assoc_names(body, sensors):
    idx = []
    for m in re.finditer(r"^(?:AssociatedSensors|AssociatedSensor\d+)=(.+)$", body, re.M):
        idx += [int(x) for x in re.findall(r"SensorSystem(\d+)", m.group(1))]
    return [sensors.get(i) for i in idx if sensors.get(i)]


def mission_units(name):
    t = txt(ROOT / "integration" / "missions" / f"{name}.ini")
    queue = list(set(re.findall(r"^Type=(.+?)\s*$", t, re.M)) |
                 set(re.findall(r"^([a-z0-9_.\-]+)=Squadron\d+,\d+", t, re.M)))
    seen = set()
    while queue:                            # carriers and bases spawn air groups
        uid = queue.pop()
        if uid in seen:
            continue
        seen.add(uid)
        for kind in UNIT_DIRS:
            f = winning_file(f"{kind}/{uid}.ini")
            if f:
                queue += [s for s in re.findall(r"^([a-z0-9_.\-]+)=Squadron\d+,\d+",
                                                txt(f), re.M) if s not in seen]
                break
    return seen


def scan(mission):
    """-> (failures, advisories, waived, checked)"""
    fail, note, waived, checked = defaultdict(list), defaultdict(list), [], 0

    targets = {}
    for uid in sorted(mission_units(mission)):
        for kind in UNIT_DIRS:
            f = winning_file(f"{kind}/{uid}.ini")
            if f:
                targets[(uid, kind)] = (f, True)
                break
    for pack in sorted((ROOT / "integration").glob("*/SEST_*")):
        if pack.parent.name == "dist":      # checked through its source packs
            continue
        for f in sorted(pack.rglob("*.ini")):
            if f.parent.name in UNIT_DIRS:
                targets.setdefault((f.stem, f.parent.name), (f, False))

    def record(bucket, check, row):
        why = allowed(row)
        if why:
            waived.append((row, why))
        else:
            bucket[check].append(row)

    for (uid, kind), (f, fielded) in sorted(targets.items()):
        t = txt(f)
        sensors = unit_sensors(t)
        blocks = weapon_blocks(t)
        by_name = dict(blocks)
        mags = {m.group(1).lower(): (m.group(1), m.group(2)) for m in
                re.finditer(r"^\[WeaponMagazine([^\]]+)\]\n(.*?)(?=^\[)", t, re.S | re.M)}
        where = f"{'MISSION' if fielded else 'sest'} {uid} ({f.parts[-3]}/{kind})"

        for wsname, body in blocks:
            am = re.search(r"^Ammunition=(\S+)", body, re.M)
            a = ammo(am.group(1).split("|")[0]) if am else None
            aid = am.group(1).split("|")[0] if am else ""
            names = assoc_names(body, sensors)
            checked += 1

            # midcourse guidance needs a channel; wire guidance (2) does not
            if a and a["mcc"] and a["mcc"] in (1, 3) and kind in MOUNT_KINDS:
                if not any(channels(n) > 0 for n in names):
                    record(fail, "midcourse round with no guidance channel",
                           f"{where} WS{wsname} {aid} (MCC={a['mcc']}) -> "
                           f"{names or 'no associated sensor'}")

            # semi-active homing needs something lighting the target
            if a and a["gt"] == 2 and kind in MOUNT_KINDS:
                if not any((sensor_defs().get(n) or {}).get("mode") == "Illuminate"
                           and channels(n) > 0 for n in names):
                    record(fail, "semi-active round with no illuminator",
                           f"{where} WS{wsname} {aid} -> {names or 'no associated sensor'}")

            for mm in re.finditer(r"^AssociatedMagazine=WeaponMagazine([^\s/]+)", body, re.M):
                entry = mags.get(mm.group(1).lower())
                mb = entry[1] if entry else None
                if mb is None:
                    record(fail, "weapon points at a magazine the file never defines",
                           f"{where} WS{wsname} -> WeaponMagazine{mm.group(1)}")
                else:
                    counts = [int(c) for c in re.findall(r"^Ammunition\d+_Count=(\d+)", mb, re.M)]
                    if counts and sum(counts) == 0:
                        record(fail, "weapon wired to a magazine holding zero rounds",
                               f"{where} WS{wsname} -> WeaponMagazine{mm.group(1)}")

            # a seat group the block never defines: the MH-60R's |MK46 shape
            seats = body + by_name.get(base_of(wsname), "")
            for st in re.finditer(r"^Station\d+=[^\s|]+\|([^\s/#]+)", body, re.M):
                if not re.search(rf"^{re.escape(st.group(1))}Positions=", seats, re.M):
                    record(fail, "store seated in a position group that is never defined",
                           f"{where} WS{wsname} |{st.group(1)}")

            # a loadout may not hang stores on a mount that has none
            if base_of(wsname) != wsname:
                bb = by_name.get(base_of(wsname), "")
                nst = re.search(r"^NumberOfStations=(\d+)", bb, re.M)
                if nst:
                    over = sorted({int(x) for x in
                                   re.findall(r"^Station(\d+)=[A-Za-z]", body, re.M)
                                   if int(x) > int(nst.group(1))})
                    if over:
                        record(fail, "loadout uses stations the mount does not have",
                               f"{where} WS{wsname} stations {over} > {nst.group(1)}")

            if re.search(r"^Type=Missile", body, re.M):
                nc = re.search(r"^NumberOfContainers=(\d+)", body, re.M)
                if nc and int(nc.group(1)) == 0:
                    record(fail, "missile mount declares zero containers",
                           f"{where} WS{wsname}")

        for mname, mbody in mags.values():
            for k, v in re.findall(r"^(Ammunition\d+)=([^/\s]+)", mbody, re.M):
                checked += 1
                if not winning_file(f"ammunition/{v}.ini"):
                    record(fail, "magazine holds a round no enabled mod defines",
                           f"{where} WeaponMagazine{mname} {k}={v}")

        # every selectable loadout should hang something
        av = re.search(r"^AvailableLoadouts=([^#\n]*)", t, re.M)
        if av:
            armed = any(re.search(r"^Station\d+=[A-Za-z]", b, re.M) for _, b in blocks)
            for key in [k.strip() for k in av.group(1).split(",") if k.strip()]:
                if key in ("Empty", "Ferry"):
                    continue
                checked += 1
                if not any(n.endswith(key) for n in by_name):
                    row = f"{where} loadout '{key}'"
                    if armed:
                        record(fail, "selectable loadout has no weapon-system block", row)
                    else:
                        record(note, "loadout with no block on an unarmed unit (cosmetic)", row)

        # a store the aircraft cannot release from the altitude it flies at.
        # Calibrated on the GBU-53, whose 9900-10100 ft window left an F-35C
        # cruising at 36000 exactly one usable rung.
        if kind == "aircraft":
            cru = re.search(r"^CruiseAltitude=(\d+)", t, re.M)
            alt = re.search(r"^Altitudes=([\d,\s]+)", t, re.M)
            band = [float(x) for x in alt.group(1).split(",") if x.strip()] if alt else []
            if cru:
                cruise, seen = float(cru.group(1)), set()
                for wsname, body in blocks:
                    for st in re.finditer(r"^Station\d+=([A-Za-z][^\s|]*)", body, re.M):
                        sid = st.group(1)
                        a = ammo(sid)
                        if sid in seen or not a:
                            continue
                        if a["minalt"] is None and a["maxalt"] is None:
                            continue
                        lo = a["minalt"] or 0.0
                        hi = a["maxalt"] if a["maxalt"] is not None else 1e9
                        if lo <= cruise <= hi:
                            continue
                        seen.add(sid)
                        checked += 1
                        usable = [x for x in band if lo <= x <= hi]
                        row = (f"{where} {sid} releases {lo:.0f}-{hi:.0f} ft, "
                               f"cruise {cruise:.0f} ft, {len(usable)}/{len(band)} rungs usable")
                        record(fail if len(usable) <= 1 else note,
                               "store cannot be released from the altitude the aircraft flies"
                               if len(usable) <= 1 else
                               "store unusable from cruise altitude (lower rungs work)", row)
    return fail, note, waived, checked


def main():
    name = " ".join(sys.argv[1:]) or next(
        l.strip() for l in txt(ROOT / "data" / "active-mission.txt").splitlines()
        if l.strip() and not l.startswith("#"))
    print(f"mission: {name}\n")
    fail, note, waived, checked = scan(name)

    for check in sorted(note):
        rows = sorted(set(note[check]))
        print(f"advisory - {check} [{len(rows)}]")
        for r in rows[:8]:
            print(f"    {r}")
        if len(rows) > 8:
            print(f"    ... and {len(rows) - 8} more")
        print()

    if waived:
        print(f"waived as verified benign: {len(waived)} (see ALLOW in this file)\n")

    if not fail:
        print(f"checked {checked} weapon/loadout contract(s)\n")
        print("every weapon can be employed by the mount that carries it")
        return 0

    for check in sorted(fail):
        print(f"CANNOT EMPLOY - {check}:")
        for r in sorted(set(fail[check])):
            print(f"    {r}")
        print()
    print("A weapon here will silently never fire: every id resolves, but the "
          "mount cannot satisfy what the round needs. Wire the mount (see "
          "integration/ran-fleet/build_fleet.py for the NSM precedent), or "
          "override the round.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
