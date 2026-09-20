#!/usr/bin/env python3
"""Build SEST Total Force 2026 - a twelve-mission linear campaign whose order
of battle is drawn from the whole collection.

WHY THIS EXISTS

128 Workshop subscriptions and 16 local packs are a lot of content to own and
never see. The Banda vignettes reached for the mods the sandbox left idle, one
family per scenario; this goes the rest of the way: a single campaign in which
EVERY active mod that can put something on the map does, and the ones that
cannot are named, with the reason, in docs/campaign-coverage.md.

"Incorporates all mods" is a claim about the load order, not about the folder
list, so it is computed the way the game resolves files. A mod is credited
only when the campaign places a unit that actually reads one of its files:

  unit      the mod's copy of <unit>.ini WINS the load order
  variant   it wins <unit>_variants.ini for a placed hull
  squadron  it wins <unit>_squadrons.ini for a placed airframe
  store     it wins an ammunition file the placed unit's chosen loadout hangs
  library   it wins no file any mission can name - systems, effects, UI or a
            bare _info.ini dependency marker - and applies install-wide
  shadowed  everything it ships is outranked; it cannot be reached at all

A mod placed in a mission but whose unit file is won by something else is
credited to the winner, never to the loser. That distinction is the whole
point: five mods here are invisible in game precisely because something above
them replaces their files, and the report says so instead of counting them.

WHY THE POSITIONS ARE HARVESTED, NOT INVENTED

Ships belong in water and land units on land, and nothing in this repo can
tell them apart from a coordinate. So every sea and land position is SNAPPED
to a position some already-loading mission put a unit of that kind on - the
repo's own missions plus the stock ones and the two stock campaigns, about
33,000 proven points. An anchor that lands on a coastline snaps to real water
a mile away; an anchor in the desert fails the build. Aircraft are airborne
and need no snapping.

Everything the game reads is derived here: hull variants, squadron references
and loadout names are resolved from the WINNING file at build time, so a mod
update that retires a variant fails this build rather than spawning a default
fit in mission seven.

Usage (repo root):
    python3 integration/campaign/build_pack.py              # build the pack
    python3 integration/campaign/build_pack.py --dry-run    # check only
"""
import argparse
import collections
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import load_order  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SEST_Campaign"
SLUG = "sest-southern-watch"
TITLE = "SEST Southern Watch"
DISPATCHES = "SEST Southern Watch - Dispatches"
MODS = ROOT / "mods-source"
UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units", "biologic")

# Families the mission format counts separately. (side, kind) -> section stem.
FAMILY = {
    ("blue", "vessel"): "Taskforce1Vessel",
    ("blue", "sub"): "Taskforce1Submarine",
    ("blue", "air"): "Taskforce1Aircraft",
    ("blue", "land"): "Taskforce1LandUnit",
    ("red", "vessel"): "Taskforce2Vessel",
    ("red", "sub"): "Taskforce2Submarine",
    ("red", "air"): "Taskforce2Aircraft",
    ("red", "land"): "Taskforce2LandUnit",
    ("neutral", "vessel"): "NeutralVessel",
    ("neutral", "sub"): "NeutralSubmarine",
    ("neutral", "air"): "NeutralAircraft",
    ("neutral", "land"): "NeutralLandUnit",
    ("neutral", "bio"): "NeutralBiologic",
}
# Order matters: the [Mission] header declares counts in this order, and the
# blocks are written in it, so a mission's file is stable across rebuilds.
COUNT_KEY = {
    "Taskforce1Vessel": "NumberOfTaskforce1Vessels",
    "Taskforce2Vessel": "NumberOfTaskforce2Vessels",
    "NeutralVessel": "NumberOfNeutralVessels",
    "Taskforce1Submarine": "NumberOfTaskforce1Submarines",
    "Taskforce2Submarine": "NumberOfTaskforce2Submarines",
    "NeutralSubmarine": "NumberOfNeutralSubmarines",
    "Taskforce1Aircraft": "NumberOfTaskforce1Aircraft",
    "Taskforce2Aircraft": "NumberOfTaskforce2Aircraft",
    "NeutralAircraft": "NumberOfNeutralAircraft",
    "Taskforce1LandUnit": "NumberOfTaskforce1LandUnits",
    "Taskforce2LandUnit": "NumberOfTaskforce2LandUnits",
    "NeutralLandUnit": "NumberOfNeutralLandUnits",
    "NeutralBiologic": "NumberOfNeutralBiologics",
}
FAMILY_ORDER = list(COUNT_KEY)


# --- the load order, as the game resolves it ---------------------------------

def providers():
    """(token, directory) highest priority first - the game's search order.

    The one SEST token in the canonical order is the consolidated pack, which
    only exists after every other builder has run; resolving through it would
    make this builder depend on its own downstream stage and break a
    --from-scratch build outright. The per-pack sources it is merged from are
    byte-identical by construction (tools/consolidate_packs.py fails the build
    on any disagreement), so they stand in for it here - and they name the
    pack that actually contributed each file, which the consolidated folder
    cannot.
    """
    out = []
    order = load_order()
    for token in order:
        if token.startswith("SEST_"):
            for pack in sorted((ROOT / "integration").glob("*/SEST_*")):
                if pack.parent.name != "dist":
                    out.append((pack.name, pack))
        elif (MODS / token).is_dir():
            out.append((token, MODS / token))
    listed = set(order)
    for d in sorted(p for p in MODS.iterdir() if p.is_dir() and p.name[0].isdigit()):
        if d.name not in listed:
            out.append((d.name, d))
    out.append(("_vanilla", MODS / "_vanilla" / "original"))
    return out


_INDEX = None


def index():
    """Lowercased relative path -> (token, path), resolved once.

    Only paths the game can name are listed: a unit file two directories deep
    (mods-source/3594891803/'PLAN mod test'/vessels/...) is unreachable, so
    crediting it would inflate the coverage report with content that cannot
    load. Keys are lowercased because the game runs on a case-insensitive
    filesystem and resolves them that way.
    """
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for token, base in providers():
            for f in base.rglob("*"):
                if not f.is_file():
                    continue
                rel = f.relative_to(base).as_posix().lower()
                if rel.split("/")[0] in UNIT_DIRS and rel.count("/") != 1:
                    continue
                _INDEX.setdefault(rel, (token, f))
    return _INDEX


def owner(relpath):
    hit = index().get(relpath.lower())
    return hit[0] if hit else None


def winning(relpath):
    hit = index().get(relpath.lower())
    return hit[1] if hit else None


def unit_file(uid):
    for kind in UNIT_DIRS:
        f = winning(f"{kind}/{uid}.ini")
        if f:
            return kind, f
    return None, None


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def unit_type(uid, depth=0):
    """UnitType of the winning file, following #!alias like the game does."""
    kind, f = unit_file(uid)
    if f is None or depth > 4:
        return None
    text = read(f)
    m = re.search(r"^\s*UnitType=(\S+)", text, re.M)
    if m:
        return m.group(1)
    a = re.search(r"#!alias\s+(\S+)", text)
    if a:
        return unit_type(Path(a.group(1)).stem, depth + 1)
    return None


# --- proven positions --------------------------------------------------------

POOL_ROOTS = ("integration/missions",
              "mods-source/_vanilla/original/missions",
              "mods-source/_vanilla/original/campaigns",
              "mods-source/_vanilla/user/missions")


def pool_kind(section):
    if "Submarine" in section:
        return "sea"          # a submarine's position is water like any other
    if "LandUnit" in section:
        return "land"
    if "Vessel" in section or "Biologic" in section:
        return "sea"
    return None               # aircraft need no proven ground


def harvest():
    """Every (lat, lon) a loading mission has already put a unit of that kind on.

    lat = centre + z/60, lon = centre + x/60: RelativePositionInNM is plain
    arcminutes on both axes. Checked against the two RAAF bases NORTHERN
    FRONT II places - Darwin resolves to -12.427,130.884 and Scherger to
    -12.603,142.040, both within a mile of the real airfields.
    """
    pool = {"sea": [], "land": []}
    for rel in POOL_ROOTS:
        for f in sorted((ROOT / rel).rglob("*.ini")):
            if OUT in f.parents:
                continue      # never feed this campaign's own output back in
            text = read(f)
            la = re.search(r"^MapCenterLatitude=(-?[\d.]+)", text, re.M)
            lo = re.search(r"^MapCenterLongitude=(-?[\d.]+)", text, re.M)
            if not (la and lo):
                continue
            clat, clon = float(la.group(1)), float(lo.group(1))
            section = None
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("[") and s.endswith("]"):
                    section = s[1:-1]
                    continue
                m = re.match(r"RelativePositionInNM=(-?[\d.]+),([^,]*),(-?[\d.]+)\s*$", s)
                if not (m and section):
                    continue
                kind = pool_kind(section)
                if kind:
                    pool[kind].append((clat + float(m.group(3)) / 60.0,
                                       clon + float(m.group(1)) / 60.0))
    for kind in pool:
        pool[kind] = sorted(set((round(a, 4), round(b, 4)) for a, b in pool[kind]))
    return pool


def nm_between(a, b):
    dlat = (a[0] - b[0]) * 60.0
    dlon = (a[1] - b[1]) * 60.0 * math.cos(math.radians((a[0] + b[0]) / 2.0))
    return math.hypot(dlat, dlon)


class Snapper:
    """Hands out proven points near an anchor, never the same one twice.

    Two ships on one coordinate is a collision the game resolves by shoving
    them apart, so used points are retired as they are handed out.
    """

    def __init__(self, pool, limit_nm=60.0):
        self.pool = pool
        self.limit = limit_nm
        self.used = set()

    def take(self, kind, anchor, exclude_nm=0.4):
        best, best_d = None, None
        for p in self.pool[kind]:
            if p in self.used:
                continue
            d = nm_between(p, anchor)
            if best_d is None or d < best_d:
                best, best_d = p, d
        if best is None or best_d > self.limit:
            raise SystemExit(
                f"no proven {kind} position within {self.limit:.0f} NM of "
                f"{anchor} - nearest is {best_d and round(best_d)} NM away. "
                f"Move the station onto water/ground some mission already uses.")
        self.used.add(best)
        return best, best_d


# --- what the game reads for one placed unit ---------------------------------

KIND_OF = {"Vessel": "vessel", "Submarine": "sub", "Aircraft": "air",
           "Helicopter": "air", "VTOL": "air", "LandUnit": "land",
           "Biologic": "bio"}


def variants(uid, kind):
    """Usable [VariantN] names from the WINNING variants file, or []."""
    f = winning(f"{kind}/{uid}_variants.ini")
    if f is None:
        return []
    body = read(f)
    names, seen = [], set()
    for n in re.findall(r"^\[(Variant\d+)\]", body, re.M):
        if n not in seen:
            seen.add(n)
            names.append(n)
    declared = re.search(r"^NumberOfVariants=(\d+)", body, re.M)
    if declared:
        names = names[:min(len(names), int(declared.group(1)))]
    return names


def squadrons(uid):
    f = winning(f"aircraft/{uid}_squadrons.ini")
    if f is None:
        return []
    return re.findall(r"^\[(Squadron\d+)\]", read(f), re.M)


def loadouts(path):
    m = re.search(r"^AvailableLoadouts=(.+)$", read(path), re.M)
    return [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []


def pick_loadout(uid, path, want):
    """The loadout to write, and why. Never invents a name the file lacks."""
    offered = loadouts(path)
    if not offered:
        return None, "file offers none"
    if want:
        if want not in offered:
            raise SystemExit(f"{uid}: loadout {want!r} is not offered by the "
                             f"winning file (offers: {', '.join(offered)})")
        return want, "declared"
    if "Default" in offered:
        return "Default", "default"
    return offered[0], "first offered"


def stores(uid, kind, path, loadout):
    """Ammunition ids the placed unit hangs with this loadout.

    Sections are either bare (WeaponSystem3, WeaponMagazineVLS_1 - loaded
    whatever the fit) or suffixed with a loadout name (WeaponSystem1Malice424),
    which is how the aircraft files carry one pylon map per fit. Only the
    chosen fit's sections count, so the report credits the stores the mission
    actually flies with rather than every round the airframe can carry.
    """
    text = read(path)
    out, section = set(), ""
    known = set(loadouts(path))
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1]
            continue
        if not section.startswith(("WeaponSystem", "WeaponMagazine")):
            continue
        suffix = next((l for l in known if section.endswith(l)), None)
        if suffix and suffix != loadout:
            continue
        m = re.match(r"(?:Station\d+|Ammunition\d+)=([^\s#/]+)", s)
        if m:
            out.add(m.group(1).split("|")[0])
        m = re.match(r"DateBased_\w+=(\S+)", s)
        if m:
            for part in m.group(1).split("|"):
                bits = part.split(",")
                if len(bits) == 2:
                    out.add(bits[1])
    return sorted(x for x in out if x and not x[0].isdigit())


_TOKENS = None


def mod_token(mod_id):
    """Catalog id (or SEST pack folder) -> the token the load order uses."""
    global _TOKENS
    if _TOKENS is None:
        data = catalog()
        _TOKENS = {m["id"]: str(m["workshop_id"]) for m in data["mods"]}
        _TOKENS.update({p["folder"]: p["folder"] for p in data["local_packs"]})
        # Stock units carry no mod credit, and saying so in the roster is how
        # a unit that SHOULD come from a mod gets caught when something
        # unsubscribes and the game silently falls back to vanilla.
        _TOKENS["_vanilla"] = "_vanilla"
    if mod_id not in _TOKENS:
        raise SystemExit(f"roster names unknown mod {mod_id!r} - it is not in "
                         "data/mod-catalog.json")
    return _TOKENS[mod_id]


def resolve(spec):
    """Fill one authored unit in: winning file, kind, variant, squadron, fit.

    Returns the block keys the mission needs plus the credit set - every mod
    whose files this one unit makes the game read.
    """
    uid = spec["type"]
    kind_dir, path = unit_file(uid)
    if path is None:
        raise SystemExit(f"{spec['mission']}: no enabled mod defines {uid!r}")
    utype = unit_type(uid)
    kind = KIND_OF.get(utype)
    if kind is None:
        raise SystemExit(f"{spec['mission']}: {uid} has UnitType={utype!r}, "
                         "which is not a kind a mission can place")
    if spec.get("kind") and spec["kind"] != kind:
        raise SystemExit(f"{spec['mission']}: {uid} is a {kind}, but the roster "
                         f"files it as a {spec['kind']} - upstream changed it")

    keys, credit = {}, {}

    def note(token, how, detail):
        if token and token not in credit:
            credit[token] = (how, detail)

    note(owner(f"{kind_dir}/{uid}.ini"), "unit", uid)

    pool = variants(uid, kind_dir)
    if pool:
        want = spec.get("variant") or pool[0]
        if want not in pool:
            raise SystemExit(f"{spec['mission']}: {uid} has no {want} "
                             f"(has: {', '.join(pool)})")
        keys["VariantReference"] = want
        note(owner(f"{kind_dir}/{uid}_variants.ini"), "variant", uid)

    if kind == "air":
        sq = squadrons(uid)
        if sq:
            want = spec.get("squadron") or ("Squadron1" if "Squadron1" in sq else sq[0])
            if want not in sq:
                raise SystemExit(f"{spec['mission']}: {uid} has no {want} "
                                 f"(has: {', '.join(sq)})")
            keys["SquadronReference"] = want
            note(owner(f"aircraft/{uid}_squadrons.ini"), "squadron", uid)

    fit, _why = pick_loadout(uid, path, spec.get("loadout"))
    if fit:
        keys["LoadoutVariant"] = fit
    for store in stores(uid, kind_dir, path, fit):
        note(owner(f"ammunition/{store}.ini"), "store", f"{uid} / {store}")

    # The roster says which mod each unit is there to exercise. If the game
    # would read nothing of that mod's, the roster is wrong - either something
    # now outranks it, or the unit was mis-attributed. Either way it must be
    # said out loud rather than quietly counted as coverage.
    want = mod_token(spec["mod"])
    if want not in credit:
        raise SystemExit(
            f"{spec['mission']}: {uid} is rostered for {spec['mod']}, but the game "
            f"reads nothing of its from this unit. What it does read: "
            + ", ".join(f"{tok} ({how})" for tok, (how, _d) in sorted(credit.items())))

    return kind, keys, credit


# --- rendering ---------------------------------------------------------------

BLOCK_ORDER = ("Type", "VariantReference", "SquadronReference", "LoadoutVariant",
               "Nation", "UnlimitedFuel", "WeaponStatus", "RadarsActive",
               "CrewSkill", "Morale", "RelativePositionInNM", "Heading",
               "Telegraph")


def block(tag, keys):
    lines = [f"[{tag}]"]
    for k in BLOCK_ORDER:
        if k in keys:
            lines.append(f"{k}={keys[k]}")
    for k, v in keys.items():
        if k not in BLOCK_ORDER:
            lines.append(f"{k}={v}")
    return "\n".join(lines)


# Most direct reason first: a mod that supplies a hull the mission places is
# reported by that hull, not by a round the hull happens to carry.
STRENGTH = {"unit": 0, "variant": 1, "squadron": 2, "store": 3}


def place(mission, snapper):
    """Give every authored unit a section id, a position and its credits."""
    centre = mission["centre"]
    placed = collections.defaultdict(list)     # family -> [(tag, keys)]
    members = collections.defaultdict(list)    # station -> [tag]
    credits = {}
    seats = collections.Counter()              # per-station air spacing
    worst = 0.0

    for spec in mission["units"]:
        spec = dict(spec, mission=mission["key"])
        st = mission["stations"][spec["station"]]
        kind, keys, credit = resolve(spec)
        family = FAMILY[(spec["side"], kind)]
        idx = len(placed[family]) + 1
        tag = f"{family}{idx}"

        if kind == "air":
            n = seats[spec["station"]]
            seats[spec["station"]] += 1
            lat = st["at"][0] - (n // 3) * 0.05
            lon = st["at"][1] + (n % 3) * 0.05
            alt = spec.get("alt", st.get("alt", 25000))
        else:
            # An oil rig is a LandUnit that belongs in water; everything else
            # takes the pool its kind implies.
            want = spec.get("snap") or ("land" if kind == "land" else "sea")
            (lat, lon), dist = snapper.take(want, st["at"])
            worst = max(worst, dist)
            alt = "low" if kind == "land" else 0

        keys = dict(Type=spec["type"], **keys)
        keys.update(UnlimitedFuel="False", WeaponStatus=spec.get("weapons", "Free"),
                    RadarsActive=spec.get("radars", "True"),
                    CrewSkill=spec.get("skill", "Trained"), Morale="3")
        keys["RelativePositionInNM"] = (
            f"{(lon - centre[1]) * 60:.2f},{alt},{(lat - centre[0]) * 60:.2f}")
        keys["Heading"] = spec.get("heading", st.get("heading", 90))
        if spec.get("nation"):
            keys["Nation"] = spec["nation"]
        for k, v in spec.get("extra", {}).items():
            keys[k] = v

        placed[family].append((tag, keys, spec.get("name")))
        members[spec["station"]].append(tag)
        for token, why in credit.items():
            best = credits.get(token)
            if best is None or STRENGTH[why[0]] < STRENGTH[best[0]]:
                credits[token] = (why[0], why[1], mission["key"])
    return placed, members, credits, worst


def render(mission, placed, members):
    name = f"{mission['num']} {mission['key']}"
    L = ["[Language_en]", f"Name={name}", f"Description={mission['brief']}"]
    for oid, text, _spec in mission["objectives"]:
        L.append(f"Objective_{oid}={text}")
    L.append(f"Taskforce1StartMessage=<color=yellow>{mission['key']}</color>|{mission['brief']}")
    L.append(f"Taskforce1VictoryMessage=<color=lime>Mission complete.</color>|{mission['win']}")
    L.append(f"Taskforce1DefeatMessage=<color=red>Mission failed.</color>|{mission['lose']}")
    L.append(f"Taskforce2VictoryMessage=<color=lime>Red victory.</color>|{mission['lose']}")
    L.append(f"Taskforce2DefeatMessage=<color=red>Red defeat.</color>|{mission['win']}")
    neutrals = [f for f in placed if f.startswith("Neutral")]
    if neutrals:
        L.append("NeutralLossMessage=<color=orange>Neutral contact hit.</color>|"
                 "That one was not ours to shoot. It goes in the record.")
    for family in FAMILY_ORDER:
        for tag, _keys, unit_name in placed.get(family, []):
            if unit_name:
                L.append(f"{tag}NameOverride={unit_name}")
    L.append("")

    d, t = mission["date"], mission["time"]
    L += ["[Environment]", f"Date={d[0]},{d[1]},{d[2]}", f"Time={t[0]},{t[1]}",
          "ConvertTimeToLocal=True", f"SeaState={mission['sea']}",
          f"Clouds={mission['clouds']}", f"WindDirection={mission['wind']}",
          f"MapCenterLatitude={mission['centre'][0]}",
          f"MapCenterLongitude={mission['centre'][1]}",
          "LoadBackgroundData=False", ""]

    L += ["[Mission]", f"Difficulty={mission.get('difficulty', 1)}",
          "PlayerTaskforce=Taskforce1", "EnemyTaskforce=Taskforce2",
          f"Taskforce1_Nation={mission['blue_nation']}",
          f"Taskforce2_Nation={mission['red_nation']}"]
    for family in FAMILY_ORDER:
        if placed.get(family):
            L.append(f"{COUNT_KEY[family]}={len(placed[family])}")

    # One formation per station that holds more than one unit of one side, so
    # the tactical map shows named groups instead of a scatter of contacts.
    forms = collections.defaultdict(list)
    for station, tags in members.items():
        by_side = collections.defaultdict(list)
        for tag in tags:
            by_side["Taskforce1" if tag.startswith("Taskforce1") else
                    "Taskforce2" if tag.startswith("Taskforce2") else
                    "Neutral"].append(tag)
        for side, group in by_side.items():
            if len(group) > 1:
                forms[side].append((mission["stations"][station].get("label", station), group))
    for side, groups in sorted(forms.items()):
        L.append(f"{side}_NumberOfFormations={len(groups)}")
        for i, (label, group) in enumerate(groups, 1):
            shape = "Vic" if "Aircraft" in group[0] else "Loose"
            spacing = "0.1" if shape == "Vic" else "1.5"
            L.append(f"{side}_Formation{i}={','.join(group)}|{label}|{shape}|{spacing}")
    triggers = (3 + (1 if mission.get("protect") else 0)
                + (1 if placed.get("Taskforce1Vessel") or
                   placed.get("Taskforce1Aircraft") else 0)
                + (1 if neutrals else 0))
    L.append(f"NumberOfTriggers={triggers}")
    L.append("")

    for family in FAMILY_ORDER:
        for tag, keys, _n in placed.get(family, []):
            L.append(block(tag, keys))
            L.append("")

    # StatusAtMissionEnd is what the objective is left as when the mission ends
    # without a trigger resolving it. Exactly one trigger here COMPLETES an
    # objective - the victory one - so only its objective may end in Fail.
    # Everything else is something you are asked not to lose: it ends Complete
    # and the protect or neutral trigger is what fails it. One objective was
    # written the other way round and could only ever fail, which is what this
    # check exists to catch.
    resolved = {mission["victory"]["objective"]}
    L.append("[Taskforce1_Objectives]")
    L.append("#ID=CompletedScore,FailedScore,StatusAtMissionEnd")
    for oid, _text, spec in mission["objectives"]:
        status = spec.split(",")[2] if len(spec.split(",")) > 2 else ""
        if status == "Fail" and oid not in resolved:
            raise SystemExit(
                f"{mission['key']}: objective {oid} ends Fail but no trigger "
                "completes it - make it Complete, or give it a trigger")
        L.append(f"{oid}={spec}")
    L.append("")

    # --- triggers -----------------------------------------------------------
    # Two victory shapes, because a convoy campaign cannot express its wins as
    # a body count: "arrive" tests UnitsInTheArea at a named handover point,
    # "destroy" tests UnitDestroyed. Failure is always a protected unit dying,
    # never the absence of a kill. Both resolve before the mission-exit timer.
    victory = mission["victory"]
    if victory["kind"] == "arrive":
        win_units = members[victory["station"]]
    else:
        win_units = [tag for st in victory["stations"] for tag in members[st]]
    if not win_units:
        raise SystemExit(f"{mission['key']}: the victory condition names no "
                         "placed unit")
    # "convoy" protects every unit at that station; "convoy#1" protects one
    # named hull, which is how a mission can say "three of four may arrive,
    # but not without the medical ship".
    protect = []
    for entry in mission.get("protect", []):
        station, _, index = entry.partition("#")
        group = members[station]
        protect += [group[int(index) - 1]] if index else group

    n = 0
    n += 1
    L += [f"[Trigger{n}]  #Mission exit", "Name=Mission exit", "Disabled=True",
          "Condition_Type=Time", f"Condition_Time={mission.get('minutes', 90)}",
          "Action_EndMission=True", "Action_EndMissionDelay=0", ""]
    n += 1
    L += [f"[Trigger{n}]  #Start message", "Name=Start message",
          "Condition_Type=Time", "Condition_Time=0.5",
          "Action_Taskforce1_Message=Taskforce1StartMessage", ""]
    n += 1
    L += [f"[Trigger{n}]  #Objective met", "Name=Objective met"]
    if victory["kind"] == "arrive":
        centre = mission["centre"]
        at = victory["at"]
        L += ["Condition_Condition1_Type=UnitsInTheArea",
              "Condition_Condition1_PositionNM="
              f"{(at[1] - centre[1]) * 60:.2f},0,{(at[0] - centre[0]) * 60:.2f}",
              f"Condition_Condition1_AreaRadiusNM={victory.get('radius', 20)}",
              "Condition_Condition1_AreaDisplaySide=Blue",
              f"Condition_Condition1_Units={','.join(win_units)}",
              f"Condition_Condition1_MinimumUnits={victory.get('min_units', len(win_units))}",
              "ConditionsCompleted=<Condition1>"]
    else:
        L += ["Condition_Condition1_Type=UnitDestroyed",
              f"Condition_Condition1_Units={','.join(win_units)}",
              f"Condition_Condition1_MinimumUnits={victory.get('min_units', len(win_units))}",
              "ConditionsCompleted=<Condition1>"]
    L += ["Action_Taskforce1_Message=Taskforce1VictoryMessage",
          "Action_Taskforce2_Message=Taskforce2DefeatMessage",
          "Action_Victory=Taskforce1", "Action_EndMission=True",
          "Action_EndMissionDelay=60",
          f"Action_ObjectivesCompleted={victory['objective']}", ""]
    if protect:
        n += 1
        L += [f"[Trigger{n}]  #Protected unit lost", "Name=Protected unit lost",
              "Condition_Condition1_Type=UnitDestroyed",
              f"Condition_Condition1_Units={','.join(protect)}",
              f"Condition_Condition1_MinimumUnits={mission.get('protect_min', 1)}",
              "ConditionsCompleted=<Condition1>",
              "Action_Taskforce1_Message=Taskforce1DefeatMessage",
              "Action_Victory=Taskforce2",
              f"Action_ObjectivesFailed={mission['protect_objective']}",
              "Action_EnableTriggers=Trigger1",
              "Action_ReactivateTriggers=Trigger1", ""]
    if placed.get("Taskforce1Vessel") or placed.get("Taskforce1Aircraft"):
        n += 1
        L += [f"[Trigger{n}]  #Player force gone", "Name=Player force gone",
              "Condition_Type=HasNoUnitsOfType", "Condition_Taskforce=Taskforce1",
              "Condition_UnitType=" + ("Vessel" if placed.get("Taskforce1Vessel")
                                       else "Aircraft"),
              "Action_Taskforce1_Message=Taskforce1DefeatMessage",
              "Action_Victory=Taskforce2", "Action_EnableTriggers=Trigger1",
              "Action_ReactivateTriggers=Trigger1", ""]
    if neutrals:
        n += 1
        tags = [tag for f in neutrals for tag, _k, _n2 in placed[f]]
        L += [f"[Trigger{n}]  #Neutral harmed", "Name=Neutral harmed",
              "Condition_Condition1_Type=UnitDestroyed",
              f"Condition_Condition1_Units={','.join(tags)}",
              f"Condition_Condition1_MinimumUnits={mission.get('neutral_limit', 1)}",
              "ConditionsCompleted=<Condition1>",
              "Action_Taskforce1_Message=NeutralLossMessage",
              f"Action_ObjectivesFailed={mission['neutral_objective']}", ""]
    if n != triggers:
        raise SystemExit(f"{mission['key']}: declared {triggers} triggers, wrote {n}")
    return name, "\n".join(L) + "\n"


# --- the campaign, its events and its briefings ------------------------------

EVENT_XML = """<Page xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  d:DesignWidth="1920" d:DesignHeight="1080"
  xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" mc:Ignorable="d">
  <Viewbox>
    <Border Background="#F2EFE6" Width="1100" Height="760" Padding="60"
            TextElement.FontFamily="Times New Roman" TextElement.Foreground="Black">
      <StackPanel Orientation="Vertical">
        <Rectangle HorizontalAlignment="Stretch" Height="4" Fill="Black"/>
        <TextBlock Text="{dateline}" Margin="0,14,0,14" FontSize="26"/>
        <Rectangle HorizontalAlignment="Stretch" Height="4" Fill="Black"/>
        <TextBlock Text="{headline}" FontWeight="Bold" FontSize="54"
                   TextWrapping="Wrap" TextAlignment="Center" Margin="0,26,0,26"/>
        <Rectangle HorizontalAlignment="Stretch" Height="2" Fill="Black"/>
{paragraphs}
      </StackPanel>
    </Border>
  </Viewbox>
</Page>
"""

BRIEF_XML = """<ScrollViewer xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" \
VerticalScrollBarVisibility="Auto"><StackPanel Margin="24">{body}</StackPanel></ScrollViewer>
"""


def xml_escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;"))


def event_page(event):
    paras = "\n".join(
        f'        <TextBlock Text="{xml_escape(p)}" FontSize="24" '
        'TextWrapping="Wrap" TextAlignment="Justify" Margin="0,18,0,0"/>'
        for p in event["body"])
    return EVENT_XML.format(dateline=xml_escape(event["dateline"]),
                            headline=xml_escape(event["headline"]),
                            paragraphs=paras)


def briefing_page(mission):
    parts = []

    def section(head, text):
        parts.append(f'<TextBlock FontSize="20" Margin="0,14,0,6" '
                     f'Text="{xml_escape(head)}"/>')
        parts.append(f'<TextBlock FontSize="16" TextWrapping="Wrap" '
                     f'Text="{xml_escape(text)}"/>')

    section("SITUATION", mission["brief"].replace("\\n\\n", "  "))
    section("TASK", "  ".join(f"{oid}: {text}"
                              for oid, text, _s in mission["objectives"]))
    section("FORCES", mission["forces"])
    # Named from the roster rather than hand-written, so the list cannot drift
    # from the order of battle the mission actually ships.
    titles = catalog()
    by_id = {m["id"]: m["title"] for m in titles["mods"]}
    by_id.update({p["folder"]: p["title"] for p in titles["local_packs"]})
    seen = []
    for spec in mission["units"]:
        name = by_id.get(spec["mod"], spec["mod"])
        if name not in seen:
            seen.append(name)
    section("MODS IN PLAY", ", ".join(seen) + ".")
    return BRIEF_XML.format(body="".join(parts))


def campaign_ini(missions, events):
    """The campaign spine: an opening event, twelve missions, a closing event.

    Entries are numbered in one sequence and chained with Parents, which is how
    both stock linear campaigns gate progression. No image keys are written:
    a MissionImage or BackgroundImage pointing at a .png this repo cannot
    produce is a dangling reference, and the stock UI is happy without one.
    """
    entries = []
    for slot in _spine(missions, events):
        entries.append(slot)
    L = ["[File]", f"Base=campaigns/{SLUG}/campaign.ini", "",
         "[Campaign]", "Type=Linear", "Difficulty=3", f"Length={len(missions)}",
         "DisplayFormat=Legacy", "",
         "[Language_en]", f"Name={TITLE} (Allied)",
         "Description=" + CAMPAIGN_BLURB, "",
         "[Missions]", f"NumberOfMissions={len(entries)}", ""]
    for i, entry in enumerate(entries, 1):
        L.append(f"[Mission{i}]  #{entry['comment']}")
        L.append(f"Type={entry['type']}")
        if entry["type"] == "Mission":
            L.append(f"MissionFile=campaigns/{SLUG}/missions/{entry['file']}.ini")
            L.append("RequiredResult=CostlyVictory")
        L.append(f"IsUnlocked={'True' if i == 1 else 'False'}")
        L.append("IsComplete=False")
        if i > 1:
            L.append(f"Parents={i - 1}")
        L.append("")
        L.append(f"Name_en={entry['name']}")
        L.append(f"Description_en={entry['sub']}")
        if entry["type"] == "Mission":
            L.append(f"MissionSequenceName_en={entry['seq']}")
            L.append(f"MapShortName_en={entry['short']}")
            L.append(f"MissionIntro_en={entry['intro']}")
        else:
            L.append(f"AssetsPath_en=campaigns/{SLUG}/art")
            L.append(f"FilePath_en=campaigns/{SLUG}/art/{entry['file']}.xml")
        L.append("")
    return "\n".join(L)


def _spine(missions, events):
    out = [dict(type="FreeEvent", comment="Opening", file=events[0]["file"],
                name=events[0]["title"], sub=events[0]["sub"])]
    for m in missions:
        for ev in events[1:-1]:
            if ev.get("before") == m["key"]:
                # The title carries a literal \n for the campaign card's second
                # line; the section comment is for a human reading the file.
                out.append(dict(type="FreeEvent",
                                comment=ev["title"].replace("\\n", " - "),
                                file=ev["file"], name=ev["title"], sub=ev["sub"]))
        out.append(dict(type="Mission", comment=f"{m['num']} {m['key']}",
                        file=f"{m['num']} {m['key']}",
                        name=f"{m['key'].upper()}", sub=m["place"],
                        seq=f"MISSION {int(m['num'])}", short=m["num"],
                        intro=m["intro"]))
    out.append(dict(type="FreeEvent", comment="Closing", file=events[-1]["file"],
                    name=events[-1]["title"], sub=events[-1]["sub"]))
    return out


# --- coverage ----------------------------------------------------------------

HOW_TEXT = {
    "unit": "places the unit; this mod wins its file",
    "variant": "supplies the hull variant the placed unit uses",
    "squadron": "supplies the squadron the placed airframe flies from",
    "store": "supplies a round the placed unit's loadout hangs",
}


def catalog():
    import json
    return json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))


def coverage(credits, excuses):
    """Every ENABLED mod and local pack, with how the campaign reaches it.

    Enabled, not active: data/load-order.tokens.txt is the subscription list
    the game loads, and five of its entries are catalogued deprecated and two
    WIP while still being required donors - the Anzac hull SEST patches and
    the Wedgetail among them. Coverage that skipped them would be measuring
    the catalog instead of the install.
    """
    data = catalog()
    by_workshop = {str(m["workshop_id"]): m for m in data["mods"]
                   if m.get("workshop_id")}
    rows, missing = [], []
    wanted = []
    for token in load_order():
        if token.startswith("SEST_"):
            continue          # the consolidated pack; its sources are below
        mod = by_workshop.get(token)
        if mod is None:
            raise SystemExit(f"load order names {token}, which is not catalogued")
        wanted.append(("mod", mod["id"], token, mod["title"]))
    wanted += [("pack", p["folder"], p["folder"], p["title"])
               for p in data["local_packs"]]
    for what, mid, token, title in sorted(wanted):
        if token in credits:
            how, detail, mission = credits[token]
            rows.append((mid, title, how, detail, mission))
        elif mid in excuses:
            rows.append((mid, title, excuses[mid][0], excuses[mid][1], "-"))
        else:
            missing.append((what, mid, token, title))
    return rows, missing


def report(rows, missions, worst):
    counts = collections.Counter(r[2] for r in rows)
    L = [f"# {TITLE} — mod coverage", "",
         "Generated by `integration/campaign/build_pack.py`. Do not edit.", "",
         f"The campaign is {len(missions)} missions built from "
         f"{sum(len(m['units']) for m in missions)} placed units. Every mod in "
         "the canonical load order (`data/load-order.tokens.txt`) and every "
         "SEST source pack appears below, with the mechanism that makes the "
         "game read its files. Coverage is measured on the load order rather "
         "than on catalog status, because five enabled entries are catalogued "
         "deprecated and two WIP while still being required donors.", "",
         "| class | meaning | mods |", "|---|---|---|"]
    meaning = dict(HOW_TEXT)
    meaning["library"] = ("ships no file a mission can name — systems, effects, "
                          "UI or a bare dependency marker — and applies install-wide")
    meaning["shadowed"] = ("every file it ships is outranked by something above "
                           "it; nothing it contains can load")
    meaning["campaign"] = "this pack - the campaign being measured"
    for how in ("unit", "variant", "squadron", "store", "library", "shadowed",
                "campaign"):
        if counts.get(how):
            L.append(f"| `{how}` | {meaning[how]} | {counts[how]} |")
    L += ["", f"Sea and land positions are snapped to points already used by a "
          f"loading mission; the furthest any anchor had to move is "
          f"{worst:.1f} NM.", "",
          "| mod / pack | title | class | via | mission |", "|---|---|---|---|---|"]
    for mid, title, how, detail, mission in rows:
        L.append(f"| `{mid}` | {title} | `{how}` | {detail} | {mission} |")
    L.append("")
    return "\n".join(L)


# --- main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    # Writing is the default: tools/build_all.py runs every builder with no
    # arguments, and a builder that only reports unless asked produces an
    # empty pack folder and a consolidated dist with no campaign in it.
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve and check everything, emit nothing")
    args = ap.parse_args()

    sys.path.insert(0, str(HERE))
    from campaign_data import (MISSIONS, EVENTS, EXCUSES, INFO_DESC,  # noqa: E402
                               DISPATCH_DESC)
    globals()["CAMPAIGN_BLURB"] = INFO_DESC

    pool = harvest()
    print(f"proven positions: {len(pool['sea'])} sea, {len(pool['land'])} land")

    built, credits, worst = [], {}, 0.0
    for mission in MISSIONS:
        snapper = Snapper(pool, limit_nm=mission.get("snap_limit", 60.0))
        placed, members, mission_credits, far = place(mission, snapper)
        worst = max(worst, far)
        name, text = render(mission, placed, members)
        built.append((name, text, mission))
        for token, why in mission_credits.items():
            best = credits.get(token)
            if best is None or STRENGTH[why[0]] < STRENGTH[best[0]]:
                credits[token] = why
        units = sum(len(v) for v in placed.values())
        print(f"  {name:<34} {units:>3} units  "
              f"{len(mission_credits):>3} mods  snap<= {far:4.1f} NM")

    rows, missing = coverage(credits, EXCUSES)
    if missing:
        print("\nNOT INCORPORATED — every active mod must be placed or excused:")
        for what, mid, token, title in missing:
            print(f"   {what:<5} {mid:<34} {token:<18} {title}")
        sys.exit(f"{len(missing)} mod(s) uncovered")
    stale = [m for m in EXCUSES if m in credits or
             m in {r[0] for r in rows if r[2] in HOW_TEXT}]
    if stale:
        sys.exit("excuse no longer needed (the campaign now reaches it): "
                 + ", ".join(sorted(stale)))
    print(f"\ncoverage: {len(rows)} mods and packs, all accounted for")

    if args.dry_run:
        print("(dry run — nothing written)")
        return

    import shutil
    if OUT.exists():
        shutil.rmtree(OUT)
    camp = OUT / "campaigns" / SLUG
    browse = OUT / "missions" / TITLE
    extra = OUT / "missions" / DISPATCHES
    (camp / "missions").mkdir(parents=True)
    (camp / "art").mkdir(parents=True)
    browse.mkdir(parents=True)
    extra.mkdir(parents=True)

    def emit(base, name, text, mission):
        (base / f"{name}.ini").write_text(text, encoding="utf-8")
        brief = base / f"{name}_briefing"
        brief.mkdir(exist_ok=True)
        (brief / "_info.ini").write_text("[General]\nHidden=True\n",
                                         encoding="utf-8")
        (brief / "BriefingText_en.xml").write_text(briefing_page(mission),
                                                   encoding="utf-8")

    # The twelve core missions ship twice: once under campaigns/, which is what
    # the linear campaign loads, and once under missions/, so they are also
    # listed in the ordinary mission browser. Same bytes, one builder - and it
    # means the campaign is playable mission by mission even on an install
    # where the Mod Manager does not surface a mod-supplied campaign.
    for name, text, mission in built:
        if mission["group"] == "core":
            emit(camp / "missions", name, text, mission)
            emit(browse, name, text, mission)
        else:
            emit(extra, name, text, mission)
    for event in EVENTS:
        (camp / "art" / f"{event['file']}.xml").write_text(event_page(event),
                                                           encoding="utf-8")
    (camp / "campaign.ini").write_text(
        campaign_ini([m for _n, _t, m in built if m["group"] == "core"],
                     EVENTS) + "\n", encoding="utf-8")
    (browse / "_info.ini").write_text(
        f"[Language_en]\nName={TITLE}\nDescription={INFO_DESC}\n", encoding="utf-8")
    (extra / "_info.ini").write_text(
        f"[Language_en]\nName={DISPATCHES}\nDescription={DISPATCH_DESC}\n",
        encoding="utf-8")
    (OUT / "_info.ini").write_text(
        f"[Language_en]\nName={TITLE}\nDescription={INFO_DESC}\n\n"
        "[Compatibility]\nApproximateVersion=0.8.2\n", encoding="utf-8")
    (ROOT / "docs" / "campaign-coverage.md").write_text(
        report(rows, MISSIONS, worst), encoding="utf-8")

    files = sum(1 for f in OUT.rglob("*") if f.is_file())
    print(f"\nbuilt {OUT.relative_to(ROOT)}: {files} files, "
          f"{len(built)} missions, {len(EVENTS)} campaign events")
    print("wrote docs/campaign-coverage.md")


CAMPAIGN_BLURB = ""

if __name__ == "__main__":
    main()
