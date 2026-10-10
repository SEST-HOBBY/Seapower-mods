#!/usr/bin/env python3
"""Check the draft Dynamic Campaign definition before anyone loads it.

    python3 integration/world-sandbox/check_dynamic_campaign.py [campaign.json]

Three layers, reported separately:

  ENGINE   the rules Dynamic Campaign Mod 0.24.0's own validator states. They
           are read from its error messages (CampaignDefinition.Validate,
           token 0x060010c5, strings recorded in docs/world-sandbox/
           engine-review/dll-evidence.json) and from the sample campaign's
           pairings (Surface forces at a NavalBase or Port, Air forces at an
           AirBase, "port" naming a NavalBase). A rule the message implies but
           this file cannot see the code for is marked INFERRED.
  AUDIT    the review bundle's scoped reference checks: every placed or
           catalogued unit has a value, no duplicated ids.
  SEST     every unit id resolves to a file the SEST load order makes the
           winner, force types match unit types, an air base's field is an
           airbase land unit, and positions the engine will sail to are water.

Passing all three is NOT a load test. The game, BepInEx, Anchor Chain and the
plugin decide; this only removes the faults a file can show.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_dynamic_campaign as adapter      # noqa: E402  bounds, resolver, water test
bp = adapter.bp

DEFAULT = adapter.CAMPAIGN_DIR / "campaign.json"
SUPPLY_CLASSES = {"AirToAir", "SurfaceToAir", "AntiShip", "LandAttack", "AirToGround", "Torpedo",
                  "AntiSubmarine", "Bomb", "Rocket", "LightShell", "HeavyShell", "Sonobuoy",
                  "Countermeasure"}
BAD_NAME = re.compile(r"[;#\[\]]|//")
WING = re.compile(r"^(Squadron\d+,\d+)(\|Squadron\d+,\d+)*$")
SPEC = re.compile(r"^(?P<uid>\S+)(?: x(?P<n>\d+))?(?: named (?P<names>.+))?$")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    d = json.loads(path.read_text(encoding="utf-8"))
    engine, audit, sest, info = [], [], [], []
    b = d.get("bounds") or {}

    def inside(lat, lon):
        return b["latMin"] <= lat <= b["latMax"] and b["lonMin"] <= lon <= b["lonMax"]

    # --- ENGINE ---------------------------------------------------------------
    if not d.get("name"):
        engine.append('missing "name"')
    if not re.fullmatch(r"[A-Za-z0-9._-]+", d.get("id", "")):
        engine.append('"id" may only have letters, digits, ".", "_" and "-"')
    if not b:
        engine.append('"bounds" is missing or empty')
    sides = {s["id"]: s for s in d.get("sides", [])}
    if len(sides) < 2:
        engine.append('needs at least two "sides"')
    if sides and all(s.get("comingSoon") for s in sides.values()):
        engine.append('every side is "comingSoon": none to play')
    for side, polys in (d.get("territories") or {}).items():
        if side not in sides:
            engine.append(f'territories of unknown side "{side}"')
        for t in polys:
            if len(t.get("polygon", [])) < 3:
                engine.append(f'territory "{t.get("name")}" needs at least three [lat, lon] points')

    bases = {}
    for x in d.get("bases", []):
        bid = x.get("id")
        if bid in bases:
            engine.append(f'base id "{bid}" is used twice')
        bases[bid] = x
        if x.get("side") not in sides:
            engine.append(f'base "{bid}" has unknown side "{x.get("side")}"')
        if not inside(x["lat"], x["lon"]):
            engine.append(f'base "{bid}" is outside the campaign bounds')
        if BAD_NAME.search(x.get("name", "")):
            engine.append(f'base "{bid}": the name can\'t have ; # // [ or ]')
        if not x.get("nation"):
            engine.append(f'base "{bid}" needs a "nation"')
        if x.get("colocated") and not (x.get("kind") == "AirBase" and x.get("port")):
            engine.append(f'base "{bid}" is "colocated", which only an air base with a "port" can be')
        for key in ("convoys", "escorts", "airlifts", "production"):
            if key in x and (not x.get("depot") or x[key] < 0):
                engine.append(f'base "{bid}" has "{key}", which only a depot can have (never below 0)')
        if "startShare" in x and not 0 <= x["startShare"] <= 1:
            engine.append(f'base "{bid}" has a "startShare" outside 0-1')
        for cls, n in (x.get("stores") or {}).items():
            if cls not in SUPPLY_CLASSES or n <= 0:
                engine.append(f'base "{bid}" has a store "{cls}": {n}')
        for s in x.get("notObjectiveFor", []):
            if s not in sides or s == x.get("side"):
                engine.append(f'base "{bid}" has "notObjectiveFor" naming an unknown side or its own')
    for bid, x in bases.items():
        if "supplyFrom" in x and not bases.get(x["supplyFrom"], {}).get("depot"):
            engine.append(f'base "{bid}" has "supplyFrom": "{x["supplyFrom"]}", which must be a depot')
        if x.get("kind") == "AirBase" and "port" in x:
            p = bases.get(x["port"])
            if not p or p["kind"] not in ("Port", "NavalBase") or p["side"] != x["side"]:
                engine.append(f'air base "{bid}" has "port": "{x["port"]}", which must be a port or '
                              "naval base of its side")
    names = [x["name"] for x in bases.values()]
    for n in {n for n in names if names.count(n) > 1}:
        engine.append(f'the base "{n}" is named twice')

    forces = {}
    replenishers = set(d.get("replenishment", {}))
    for f in d.get("forces", []):
        n = f.get("name")
        if n in forces:
            engine.append(f'the force "{n}" is named twice')
        forces[n] = f
        if BAD_NAME.search(n or ""):
            engine.append(f'force "{n}": the name can\'t have ; # // [ or ]')
        base = bases.get(f.get("base"))
        if base is None:
            engine.append(f'force "{n}" is based at unknown base "{f.get("base")}"')
            continue
        if base["side"] != f.get("side"):
            engine.append(f'force "{n}" ({f.get("side")}) is based at "{base["id"]}", which belongs '
                          f'to {base["side"]}')
        allowed = {"Surface": ("NavalBase", "Port"), "Air": ("AirBase",)}.get(f.get("type"), ())
        if base["kind"] not in allowed:
            engine.append(f'force "{n}" is {f.get("type")} but "{base["id"]}" is a {base["kind"]} '
                          "(INFERRED from the sample's pairings)")
        if not f.get("units"):
            engine.append(f'force "{n}" has no units')
        if "at" in f and (f.get("type") != "Surface" or not inside(*f["at"])):
            engine.append(f'force "{n}" is "at" sea, but only a surface force can be, inside the bounds')
        for spec in f.get("units", []):
            m = SPEC.match(spec)
            if not m:
                engine.append(f'force "{n}": unit "{spec}" does not read as "unit xN named A; B"')
                continue
            count = int(m.group("n") or 1)
            if m.group("names"):
                if f.get("type") != "Surface":
                    engine.append(f'force "{n}" names its units, but only ships can be named')
                if len(m.group("names").split("; ")) > count:
                    engine.append(f'force "{n}" names more ships than it has')
        if "cargo" in f and (f["cargo"] != "full" or f.get("type") != "Surface" or
                             not any(SPEC.match(s).group("uid") in replenishers for s in f["units"])):
            engine.append(f'force "{n}" has "cargo": only "full", for a surface force with '
                          "replenishment ships")

    for lane in d.get("traffic", {}).get("lanes", []):
        if len(lane.get("points", [])) < 2:
            engine.append(f'shipping lane "{lane.get("name")}" needs at least two [lat, lon] points')
    for p in d.get("patrols", []):
        f = forces.get(p.get("force"))
        if not f or f.get("type") != "Surface":
            engine.append(f'patrol for "{p.get("force")}", which is not a surface force')
        if not p.get("points") or not all(inside(*pt) for pt in p["points"]):
            engine.append(f'patrol of "{p.get("force")}" needs [lat, lon] points inside the bounds')
    ai = d.get("ai", {})
    if not (ai.get("startTier", -1) >= 0 and ai.get("daysPerTier", 0) > 0):
        engine.append('"ai" needs a "startTier" of 0 or more and "daysPerTier" above 0')
    for u, r in d.get("replenishment", {}).items():
        if min(r.get("fuelT", 0), r.get("ammoT", 0)) < 0 or max(r.get("fuelT", 0), r.get("ammoT", 0)) <= 0:
            engine.append(f'"replenishment" {u} needs a "fuelT" or "ammoT" above 0')
    for u, r in d.get("tankers", {}).items():
        if r.get("fuelT", 0) <= 0:
            engine.append(f'"tankers" {u} needs a "fuelT" above 0')
    spy = d.get("spyShips")
    if spy and not (spy.get("units") and spy.get("side") in sides and spy.get("nation")
                    and 0 <= spy.get("chance", -1) <= 1 and spy.get("laneNm", 0) > 0
                    and 0 <= spy.get("minNm", -1) <= spy.get("maxNm", -2)):
        engine.append('"spyShips" needs units, a known side, a nation, a chance of 0-1, a laneNm above 0 '
                      'and 0 <= minNm <= maxNm')
    for carrier, wing in (d.get("airWings") or {}).items():
        for ac, line in wing.items():
            if line != "" and not WING.match(line):
                engine.append(f'"airWings" "{carrier}": "{ac}": "{line}" is no air wing line')
    for inv in d.get("invasions", []):
        engine.append("INFO: invasions present - the review's conquest checks apply")
    for side, ranks in (d.get("ranks") or {}).items():
        if side not in sides or not ranks or ranks[0].get("renown") != 0:
            engine.append(f'ranks of "{side}" need a known side and a first rank at 0 renown')
    for nation, ids in (d.get("yards") or {}).items():
        for y in (i.strip() for i in ids.split(",")):
            if y not in bases:
                engine.append(f'yard "{y}" of {nation} is not a base')
    for e in d.get("catalogue", []):
        if not (e.get("unit") and e.get("side") in sides and e.get("nation")):
            engine.append(f'catalogue entry "{e.get("unit")}" needs a unit, a known side and a nation')
        if e.get("max", 0) < 0:
            engine.append(f'catalogue entry "{e.get("unit")}" has a "max" below 0')
    values = d.get("values", {})
    for u, v in values.items():
        if not v > 0:
            engine.append(f'"values" gives "{u}" {v}; a value must be above 0')

    # --- AUDIT ----------------------------------------------------------------
    force_units = {SPEC.match(s).group("uid") for f in forces.values() for s in f["units"] if SPEC.match(s)}
    cat_units = [e["unit"] for e in d.get("catalogue", [])]
    for u in sorted(force_units - set(values)):
        audit.append(f"placed unit {u} has no value")
    for u in sorted(set(cat_units) - set(values)):
        audit.append(f"catalogued unit {u} has no value")
    for u in {u for u in cat_units if cat_units.count(u) > 1}:
        audit.append(f"catalogue lists {u} twice")

    # --- SEST -----------------------------------------------------------------
    def resolves(uid):
        return bp.unit_file(uid)[1] is not None

    for f in forces.values():
        want = {"Surface": ("Vessel", "Submarine"), "Air": ("Aircraft", "Helicopter", "VTOL")}[f["type"]]
        for s in f["units"]:
            uid = SPEC.match(s).group("uid")
            if not resolves(uid):
                sest.append(f'force "{f["name"]}": no enabled mod defines {uid}')
            elif bp.unit_type(uid) not in want:
                sest.append(f'force "{f["name"]}": {uid} is a {bp.unit_type(uid)}, not {"/".join(want)}')
        if "at" in f and adapter.is_water(*f["at"]) is False:
            sest.append(f'force "{f["name"]}" starts at {f["at"]}, which is land')
    for x in bases.values():
        fld = x.get("field")
        if fld:
            if not resolves(fld["unit"]) or adapter.category(fld["unit"]) != "airfield":
                sest.append(f'base "{x["id"]}": field unit {fld["unit"]} is not an airbase land unit')
            info.append(f'base "{x["id"]}": runway heading {fld["heading"]} is a placeholder')
        if x["kind"] in ("NavalBase", "Port") and adapter.is_water(x["lat"], x["lon"]) is False:
            info.append(f'base "{x["id"]}" anchor is on land (harbour anchors often are; the sample\'s are too)')
    for p in d.get("patrols", []):
        for pt in p["points"]:
            if adapter.is_water(*pt) is False:
                sest.append(f'patrol of "{p["force"]}": point {pt} is land')
    for lane in d.get("traffic", {}).get("lanes", []):
        pts = lane["points"]
        for i in range(len(pts) - 1):
            if not adapter.segment_wet(tuple(pts[i]), tuple(pts[i + 1]), step_nm=3):
                sest.append(f'lane "{lane["name"]}": leg {i} crosses land')
    ids = set(values) | set(cat_units) | set(d.get("replenishment", {})) | set(d.get("tankers", {}))
    g = d.get("ground", {})
    for section in ("garrisons", "airDefence", "troops"):
        for lst in g.get(section, {}).values():
            ids |= set(lst)
    ids |= set(g.get("lift", {}))
    c = d.get("convoys", {})
    for lst in c.get("merchants", {}).values():
        ids |= set(lst)
    ids |= set(c.get("escorts", {}).values()) | set(c.get("airlifts", {}).values())
    t = d.get("traffic", {})
    ids |= set(t.get("merchants", [])) | set(t.get("marineLife", []))
    for lst in t.get("fishing", {}).values():
        ids |= set(lst)
    ids |= set((spy or {}).get("units", []))
    for u in sorted(ids):
        if not resolves(u):
            sest.append(f"no enabled mod defines {u}")
    for a in set(t.get("airliners", [])) | {a for w in t.get("airways", []) for a in w.get("airliners", [])}:
        uid, _, sq = a.partition("/")
        if not resolves(uid):
            sest.append(f"airliner {a}: no enabled mod defines {uid}")
        elif sq and sq not in bp.squadrons(uid):
            sest.append(f"airliner {a}: {uid} has no {sq}")
    for n, nat in ((s["id"], s.get("nations", [])) for s in sides.values()):
        for nation in nat:
            for section in ("garrisons", "airDefence", "troops"):
                if nation not in g.get(section, {}):
                    info.append(f"ground.{section} has no entry for {nation} (INFERRED risk)")

    def show(title, items):
        print(f"{title}: {'PASS' if not items else f'{len(items)} problem(s)'}")
        for i in items:
            print("   ", i)

    print(f"{path}")
    print(f"  {len(bases)} bases, {len(forces)} forces, {len(d.get('patrols', []))} patrols, "
          f"{len(values)} values, {len(cat_units)} catalogue entries, "
          f"{len(t.get('lanes', []))} lanes")
    show("ENGINE rules (from the validator's own messages)", engine)
    show("AUDIT reference checks", audit)
    show("SEST collection and water checks", sest)
    if info:
        print(f"notes ({len(info)}):")
        for i in sorted(set(info))[:12]:
            print("   ", i)
        if len(set(info)) > 12:
            print(f"    ... and {len(set(info)) - 12} more")
    sys.exit(1 if engine or audit or sest else 0)


if __name__ == "__main__":
    main()
