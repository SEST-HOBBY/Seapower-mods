#!/usr/bin/env python3
"""SEST World Sandbox -> Dynamic Campaign Mod campaign.json. DRAFT adapter.

    python3 integration/world-sandbox/build_dynamic_campaign.py
    python3 integration/world-sandbox/check_dynamic_campaign.py

Reads the world-population register (docs/world-sandbox/register/
packages.json) and writes a candidate data pack for Bungalow's Dynamic
Campaign Mod (Workshop 3813157776, plugin 0.24.0):

    integration/world-sandbox/draft/sest-world-sandbox/
        _info.ini
        dynamic_campaigns/sest-world-sandbox/campaign.json
    integration/world-sandbox/draft/conversion.json   every register row,
                                                       converted or skipped

Why this shape (docs/world-sandbox/DYNAMIC_CAMPAIGN_ADAPTER.md has the full
case): the static review of that plugin (docs/world-sandbox/engine-review/)
found its campaign menu scans every `dynamic_campaigns` directory for a
`campaign.json`, so a separately named SEST data pack may load beside
Bungalow's own campaign without touching the DLL. The schema used here is
the one the sample campaign and the validator's own error messages define;
check_dynamic_campaign.py re-applies those messages as rules.

What it is NOT: the register is the source of truth and stays engine-neutral.
Nothing here is installed by SETUP, built by tools/build_all.py or published
in the SEST Integration Pack. Nothing has run in the game. Every number this
adapter invents (unit values, depot choices, patrol rings, deployment areas,
replenishment tonnages, ranks, tiers) is a SCENARIO CHOICE and is labelled so
in the report; the register's own SOURCE CLAIMs are not changed by it.
"""
import collections
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs" / "world-sandbox" / "register" / "packages.json"
OUT = Path(__file__).resolve().parent / "draft"
PACK = OUT / "sest-world-sandbox"
CAMPAIGN_DIR = PACK / "dynamic_campaigns" / "sest-world-sandbox"

sys.path.insert(0, str(ROOT / "integration" / "campaign"))
sys.path.insert(0, str(ROOT / "integration" / "missions"))
import build_pack as bp                      # noqa: E402  winning-file resolver
from retarget_units import RETARGET           # noqa: E402  ids the collection retired

try:
    from global_land_mask import globe       # same optional dependency as the showcase builder
except ImportError:                            # pragma: no cover
    globe = None

CAMPAIGN_ID = "sest.world_sandbox_2028"
START = "2028-10-01T00:00:00Z"

# The world spans Jacksonville (81.7W) east-about to San Diego (117.2W), so one
# seam is unavoidable. GeoBounds.Continuous (0x060010ce) maps a longitude to
# the copy nearest the bounds' midpoint; the seam is put over Mexico at 102W,
# where no register node needs to cross it. Pacific longitudes east of the
# antimeridian are written as 180+ (San Diego = 242.8), as the sample writes
# Pearl Harbor (202.05). Untested at this extent: see the adapter doc.
BOUNDS = {"latMin": -62.0, "latMax": 74.0, "lonMin": -100.0, "lonMax": 258.0}
VIEW = {"lat": 25.0, "lon": 80.0, "pixelsPerDegree": 6.0}

BLUE = ["US", "Australia", "Japan", "France", "Italy", "UK", "Norway"]
RED = ["China", "Russia"]
SIDE_OF = {n: "blue" for n in BLUE} | {n: "red" for n in RED}

# Operator text -> game nation key (nations.ini; Russia is the key SEST
# Collection Fixes names). Read only up to "host", so "United States Navy
# (host nation Japan)" is the US. Order matters.
NATION_WORDS = [
    (r"\bPLA\b|China|Chinese", "China"),
    (r"Russia", "Russia"),
    (r"Royal Australian", "Australia"),
    (r"Japan", "Japan"),
    (r"France|French", "France"),
    (r"Italy|Italian", "Italy"),
    (r"United Kingdom|Royal Air Force|Royal Navy", "UK"),
    (r"Norway|Norwegian", "Norway"),
    (r"United States|US Defense|US Army|\bUS\b|USAF|Navy", "US"),
]
# Operator not stated in the reports; the register's forces there are US.
NATION_OVERRIDE = {"me_bahrain_muharraq_airfield": "US"}
# A neutral host-nation commercial port: the engine has two sides and no
# neutral bases (Validate: every base needs a known side), so it is left out.
SKIP_NODES = {"me_uae_jebel_ali_port": "neutral host-nation commercial port; the engine "
                                       "has no neutral bases"}

# Depots: where each side's supply originates (Validate: "supplyFrom" must name
# a depot; only a depot may carry production or convoys). SCENARIO CHOICE: the
# populated naval bases the register pairs with an abstract DLA or JLSF node
# (Yokosuka, Guam, Bahrain) and the fleet concentration bases behind the CONUS
# and PLA logistics chains. The abstract logistics nodes themselves stay
# abstract: the engine's depot is a base, not a distribution network.
DEPOTS = {
    "usp_sandiego_naval_base_san_diego": "US Pacific fleet concentration; DLA San Joaquin behind it",
    "usa_norfolk_naval_station_norfolk": "US Atlantic fleet concentration; DLA Susquehanna and Richmond behind it",
    "wpac_yokosuka_naval_base": "register pairs it with DLA Yokosuka",
    "wpac_guam_naval_base_apra_harbor": "register pairs it with DLA Guam",
    "me_bahrain_nsa_bahrain": "register pairs it with DLA Bahrain",
    "aus_stirling_hmas_stirling": "main Australian Indian Ocean naval base",
    "chn_zhejiang_ningbo_naval_base": "Eastern Theater; JLSF Wuxi behind it",
    "chn_hainan_yulin_naval_base": "Southern Theater; JLSF Guilin behind it",
    "satl_falklands_mare_harbour": "the only UK naval node",
    # Decided 10 Oct 2026 ("yes if realistic"): the research names DLA
    # Distribution Sigonella the "Mediterranean/European logistical gateway"
    # (R02:23, R02:34); Rota is described only as an operational gateway for
    # destroyers (R03:44). Sigonella is an air station, so its depot supplies by
    # airlift, which the validator allows a depot to carry. An air-station
    # depot is untested; if it cannot feed ships, Rota is the fallback.
    "med_sigonella_nas_sigonella": "register pairs it with DLA Distribution Sigonella, the research's "
                                   "Mediterranean/European logistical gateway",
    "hn_kola_olenya_airbase": "Russia has no naval node in the register; its air bases draw here",
}
SHIPYARDS = {"usp_kitsap_bremerton_psns", "usa_norfolk_naval_station_norfolk",
             "wpac_yokosuka_naval_base", "chn_zhejiang_ningbo_naval_base",
             "aus_stirling_hmas_stirling"}

# Groups the register describes as away from their home node. Each is the
# register's own words; the position is a SCENARIO CHOICE inside that area.
DEPLOYED_AT = {
    "asset:usp:cvn72_abraham_lincoln": ((20.0, 133.0), "'Western Pacific deployment' - Philippine Sea"),
    "asset:usp:cvn71_theodore_roosevelt": ((18.0, 168.0), "'underway toward the CENTCOM AOR' - west of Hawaii"),
    "asset:usatl:cvn75_truman": ((28.0, -70.0), "'southbound in the western Atlantic'"),
    "asset:wpac:cvn73_george_washington": ((22.0, 128.0), "'Indo-Pacific patrol' - Philippine Sea"),
    "asset:chn:scs_cv_1": ((16.0, 114.0), "'South China Sea carrier group'"),
}

# Unit values: the engine's points and purchase prices. The plugin's sample
# prices are the author's design; these follow its scale, not its numbers.
# Ships: fitted on the sample's 102 priced hulls against each hull's own
# Displacement= (log-log, R^2 0.72). Aircraft: the sample's median value for
# the aircraft's own Role= (mass explains only R^2 0.11 of the sample).
SHIP_VALUE = (0.48926, 0.677)
# The sample prices its replenishment and cargo ships at about a third of that
# fit (AO T2 0.35, AE Kilauea 0.34, AOE Sacramento 0.28, LKA Charleston 0.31).
AUX_FACTOR = 0.32
AUX_PATTERN = re.compile(r"_(tao|taoe|take|takr|aor|aoe|ao|ae)(_|$)|sealift")
AIR_ROLE_VALUE = {"AEW": 242, "Bomber": 78, "EW": 118, "Fighter": 46, "HeavyBomber": 172,
                  "StrategicBomber": 172, "MPA": 89, "MaritimePatrol": 89, "Recon": 28,
                  "Transport": 23, "Tanker": 60, "Airliner": 2, "ASW": 39, "ASuW": 39,
                  "Attack": 25, "Targeting": 25, "Utility": 21}
AIR_DEFAULT_VALUE = 40

# Replenishment ships and tankers present in the world. Approximate public
# cargo capacities in tonnes, rounded - SCENARIO CHOICE, not register claims.
REPLENISHMENT = {
    "usn_tao_kaiser": {"fuelT": 24000, "ammoT": 0},
    "usn_take_lewis_clark": {"fuelT": 2400, "ammoT": 5000},
    "usn_taoe_supply": {"fuelT": 21000, "ammoT": 1800},
    "ran_aor_supply": {"fuelT": 8000, "ammoT": 300},
    "plan_aor_type903a": {"fuelT": 10500, "ammoT": 250},
    "plan_aor_type901": {"fuelT": 25000, "ammoT": 1500},
    "rn_aor_tide": {"fuelT": 16000, "ammoT": 0},
}
TANKERS = {"usaf_stratotanker": {"fuelT": 70}, "uk_a330_mrtt": {"fuelT": 100},
           "wp_il-78": {"fuelT": 60}, "usmc_kc-130j": {"fuelT": 25}}

SUPPLY_REACH_NM = 4000
AT_SEA = {"escort", "underway_deployed", "transit", "training_test"}
IN_PORT = {"resident_at_base", "servicing_maintenance", "reserve", "support"}
GENERIC_TOKENS = {"ddg", "cg", "ffg", "take", "tao", "taoe", "flt", "esc", "csg", "cvg",
                  "airwing", "core", "hsc", "cvw", "aoe", "1", "2", "3", "ddg1", "ddg2",
                  "cg1", "det", "cq"}


def clean_name(text):
    """Validate: a name cannot contain ; # // [ or ]."""
    text = re.sub(r"[;#\[\]]", " ", text).replace("//", "/")
    if text.count("'") % 2:
        text = text.replace("'", "")       # an unpaired quote left over from the register's prose
    return re.sub(r"\s+", " ", text).strip(" ,'\"")


def parse_position(text):
    """The first plausible lat/lon pair in a register position note."""
    pat = re.compile(r"(-?\d{1,2}(?:\.\d+)?)\s*([NS])?\s*,?\s+(-?\d{1,3}(?:\.\d+)?)\s*([EW])?")
    for m in pat.finditer(text.replace("°", "")):
        lat, ns, lon, ew = float(m.group(1)), m.group(2), float(m.group(3)), m.group(4)
        if "." not in m.group(1) and "." not in m.group(3) and not (ns or ew):
            continue                       # "57,000 acres", "R03 17" and similar
        if ns == "S":
            lat = -abs(lat)
        if ew == "W":
            lon = -abs(lon)
        if abs(lat) <= 90 and abs(lon) <= 180:
            return lat, lon
    return None


def continuous(lon):
    """Longitude in the bounds' representation (Pacific east of 180 as 180+)."""
    return lon + 360 if lon < BOUNDS["lonMin"] else lon


def nation_of(pkg):
    if pkg["world_id"] in NATION_OVERRIDE:
        return NATION_OVERRIDE[pkg["world_id"]], "SCENARIO CHOICE (operator not stated)"
    text = re.split(r"(?i)\bhost\b", pkg["operator"], 1)[0]
    for pat, nation in NATION_WORDS:
        if re.search(pat, text):
            return nation, "operator"
    return None, "operator not recognised"


HOME_WORDS = {"US": "United States", "Australia": "Australia", "Japan": "Japan", "Norway": "Norway",
              "China": "China", "Russia": "Russia", "France": "France", "Italy": "Italy",
              "UK": "United Kingdom"}


def homeland(pkg, nation):
    """True where the operator is in its own country: no host is named, or the
    host the register names is the operator's own (Guam, Japan, Norway).
    Overseas territories (Falklands, Diego Garcia) are not homeland."""
    host = re.search(r"(?i)\bhost[^;)]*", pkg["operator"])
    if not host:
        return True
    return HOME_WORDS.get(nation, "\0") in host.group(0) and "Falkland" not in host.group(0)


def gc_nm(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3440.065 * 2 * math.asin(min(1, math.sqrt(d)))


def offset(lat, lon, bearing_deg, nm):
    b, d = math.radians(bearing_deg), nm / 3440.065
    la1, lo1 = math.radians(lat), math.radians(lon)
    la2 = math.asin(math.sin(la1) * math.cos(d) + math.cos(la1) * math.sin(d) * math.cos(b))
    lo2 = lo1 + math.atan2(math.sin(b) * math.sin(d) * math.cos(la1),
                           math.cos(d) - math.sin(la1) * math.sin(la2))
    return round(math.degrees(la2), 3), round(continuous(((math.degrees(lo2) + 180) % 360) - 180), 3)


def is_water(lat, lon):
    if globe is None:
        return None
    lon = ((lon + 180) % 360) - 180
    return not bool(globe.is_land(lat, lon))


def in_bounds(lat, lon):
    return (BOUNDS["latMin"] <= lat <= BOUNDS["latMax"]
            and BOUNDS["lonMin"] <= lon <= BOUNDS["lonMax"])


def segment_wet(a, b, step_nm=4):
    n = max(1, int(gc_nm(a, b) / step_nm))
    for i in range(n + 1):
        lat = a[0] + (b[0] - a[0]) * i / n
        lon = a[1] + (b[1] - a[1]) * i / n
        if is_water(lat, lon) is False:
            return False
    return True


def water_ring(lat, lon):
    """Four patrol points on water, in bounds, joined by water, round an
    offshore centre near the base. SCENARIO CHOICE: the register names the
    patrolled waters in prose only."""
    for r in (35, 25, 18, 12, 8):                 # the widest ring that fits
        for centre_nm in (0, 15, 25, 40, 60, 80):
            bearings = [0] if centre_nm == 0 else range(0, 360, 15)
            for cb in bearings:
                c = (lat, lon) if centre_nm == 0 else offset(lat, lon, cb, centre_nm)
                if centre_nm and is_water(*c) is False:
                    continue
                for start in range(0, 90, 15):
                    pts = [offset(c[0], c[1], start + k * 90, r) for k in range(4)]
                    if all(in_bounds(*p) and is_water(*p) is not False for p in pts) and \
                       all(segment_wet(pts[i], pts[(i + 1) % 4], step_nm=2) for i in range(4)):
                        return pts, f"{r} NM ring centred {centre_nm} NM off the base"
    return None, None


def water_point(lat, lon, radii=(25, 40, 60, 90, 130, 180)):
    for r in radii:
        for b in range(0, 360, 10):
            p = offset(lat, lon, b, r)
            if in_bounds(*p) and is_water(*p) is not False:
                return p
    return None


# --- the collection ----------------------------------------------------------

def resolve(uid):
    """(unit id the collection still defines, how) - RETARGET from the missions
    tooling is the one table of ids the collection retired."""
    if bp.unit_file(uid)[1] is not None:
        return uid, "as registered"
    new = RETARGET.get(uid)
    if new and bp.unit_file(new)[1] is not None:
        return new, f"retargeted from {uid} (integration/missions/retarget_units.py)"
    return None, "no enabled mod defines it"


_TEXT = {}


def text_of(uid, depth=0):
    if uid in _TEXT:
        return _TEXT[uid]
    kind, f = bp.unit_file(uid)
    t = bp.read(f) if f else ""
    a = re.search(r"#!alias\s+(\S+)", t)
    if a and depth < 4:
        t = t + "\n" + text_of(Path(a.group(1)).stem, depth + 1)
    _TEXT[uid] = t
    return t


def num(uid, key):
    m = re.search(rf"^\s*{key}\s*=\s*(\d+(?:\.\d+)?)", text_of(uid), re.M)
    return float(m.group(1)) if m else None


def role(uid):
    m = re.search(r"^\s*Role\s*=\s*([^\n/]+)", text_of(uid), re.M)
    return m.group(1).split(",")[0].strip() if m else ""


def category(uid):
    ty = bp.unit_type(uid)
    if uid.startswith("civ_"):
        return "civil_air" if ty in ("Aircraft", "Helicopter", "VTOL") else "civil_ship"
    if ty in ("Vessel", "Submarine"):
        return "ship"
    if ty in ("Aircraft", "Helicopter", "VTOL"):
        return "air"
    if ty == "LandUnit":
        return "airfield" if re.search(r"^\s*LandUnitSubType\s*=\s*Airbase", text_of(uid), re.M) \
            else "land"
    return "other"


def is_carrier(uid):
    cap = num(uid, "AircraftCapacity")
    return bool(cap and cap >= 20 and bp.unit_type(uid) == "Vessel")


def value_of(uid):
    ty = bp.unit_type(uid)
    if ty in ("Vessel", "Submarine"):
        disp = num(uid, "Displacement")
        if disp:
            a, b = SHIP_VALUE
            if uid in REPLENISHMENT or AUX_PATTERN.search(uid):
                return max(5, round(AUX_FACTOR * a * disp ** b)), \
                    f"Displacement {disp:.0f} t, auxiliary x{AUX_FACTOR}"
            return max(5, round(a * disp ** b)), f"Displacement {disp:.0f} t"
        return 100, "no Displacement: default"
    if ty in ("Aircraft", "Helicopter", "VTOL"):
        r = role(uid)
        return AIR_ROLE_VALUE.get(r, AIR_DEFAULT_VALUE), f"Role {r or 'none'}"
    return 10, "default"


_NAMES = None


def display(uid):
    global _NAMES
    if _NAMES is None:
        _NAMES = {}
        files = sorted(ROOT.glob("mods-source/*/language_en/*_names.ini")) + \
            sorted(p for p in ROOT.glob("integration/*/SEST_*/language_en/*_names.ini")
                   if "dist" not in p.parts)
        for f in files:
            for m in re.finditer(r"^\[([^\]]+)\][^\n]*\n(?:(?!^\[).)*?^Default=([^,\n]+)",
                                 f.read_text(encoding="utf-8", errors="replace"), re.M | re.S):
                _NAMES[m.group(1).strip().lower()] = m.group(2).strip()
    return clean_name(_NAMES.get(uid.lower(), uid))


# --- the register ------------------------------------------------------------

def quantity(row):
    q = str(row["scenario_quantity"]).strip()
    if re.match(r"(?i)\s*(abstract|none|0\b|0-1)", q):
        return 0
    m = re.match(r"\s*(\d+)", q)
    return int(m.group(1)) if m else 1


def hull_names(row, qty):
    """Ship names the register gives: hull_name, a quoted name after the
    variant, or - for the carriers - the name in the asset id."""
    if row.get("hull_name"):
        names = [n for n in re.split(r";\s*", row["hull_name"]) if n.strip()]
    else:
        names = re.findall(r"Variant\d+\s+'([^']+)'", str(row["scenario_quantity"]))
    if not names:
        m = re.match(r"cvn(\d+)_([a-z_]+)$", row["asset_id"].split(":")[-1])
        if m:
            names = [f"CVN-{m.group(1)} " + m.group(2).replace("_", " ").title()]
    return [clean_name(n) for n in names][:qty]


def embarked(row):
    a, r = row["allocation"].lower(), row["role"].lower()
    return "embarked" in a or "embarked" in r or "aviation element" in r or \
        re.search(r"\b(cvw|airwing|air wing|cq_det)\b", row["asset_id"].lower() + " " + r) is not None


def tokens(asset_id):
    local = asset_id.split(":")[-1].lower()
    return {t for t in re.split(r"[_\-]", local) if t and t not in GENERIC_TOKENS}


def carrier_numbers(row):
    found = set(re.findall(r"CVN?[- ]?(\d{2})", row["role"] + " " + row["asset_id"].upper()))
    found |= set(re.findall(r"cvn(\d{2})", row["asset_id"].lower()))
    return found


def group_at_sea(rows):
    """Escort and support rows -> the carrier group they sail with, by the
    register's own links: a CVN number in the role or asset id, a shared
    name token (truman, scs, vinson), or the carrier name's initials (gw)."""
    carriers = [r for r in rows if r["_carrier"] and r["allocation"] in AT_SEA]
    groups = {c["asset_id"]: [c] for c in carriers}
    loose = []
    for r in rows:
        if r in carriers:
            continue
        home = None
        nums = carrier_numbers(r)
        for c in carriers:
            if nums & carrier_numbers(c):
                home = c
                break
        if home is None:
            for c in carriers:
                ct = tokens(c["asset_id"])
                initials = "".join(w[0] for w in re.findall(r"[a-z]+", c["asset_id"].split(":")[-1].lower())
                                   if w not in ("cvn", "cv") and not w.isdigit())
                if tokens(r["asset_id"]) & ct or (len(initials) >= 2 and initials[-2:] in tokens(r["asset_id"])):
                    home = c
                    break
        if home is None and len(carriers) == 1 and r["allocation"] in AT_SEA:
            home = carriers[0]
        if home is not None:
            groups[home["asset_id"]].append(r)
        else:
            loose.append(r)
    return groups, loose


def unit_spec(uid, qty, names):
    spec = uid + (f" x{qty}" if qty > 1 else "")
    if names:
        spec += " named " + "; ".join(names)
    return spec


def build():
    reg = json.loads(REGISTER.read_text(encoding="utf-8"))
    report = {"register": str(REGISTER.relative_to(ROOT)), "rows": [], "bases": [],
              "skipped_nodes": [], "forces": [], "notes": []}
    bases, forces, patrols, used = [], [], [], collections.Counter()
    base_ids, force_names = set(), set()
    node_base, node_air = {}, {}
    pending_air = collections.defaultdict(collections.Counter)

    def row_report(pkg, row, outcome, why, **extra):
        report["rows"].append({"node": pkg["world_id"], "asset_id": row["asset_id"],
                               "allocation": row["allocation"], "units": row["unit_ids"],
                               "outcome": outcome, "why": why} | extra)

    def add_force(name, side, base, ftype, units, at=None, extra=None):
        name = clean_name(name)
        n, k = name, 2
        while n in force_names:
            n, k = f"{name} {k}", k + 1
        force_names.add(n)
        f = {"name": n, "side": side, "base": base, "type": ftype}
        if at:
            f["at"] = [at[0], at[1]]
        f["units"] = units
        if extra:
            f.update(extra)
        forces.append(f)
        return f

    for pkg in reg["packages"]:
        wid = pkg["world_id"]
        policy = pkg["populate_policy"].split(" ")[0]
        if wid in SKIP_NODES or policy not in ("populate", "populate_small"):
            why = SKIP_NODES.get(wid, f"populate_policy {policy}: kept abstract, as the register says")
            report["skipped_nodes"].append({"node": wid, "why": why})
            for row in pkg["forces"]:
                row_report(pkg, row, "skipped", "node not converted")
            continue
        pos = parse_position(pkg["position"])
        nation, nation_how = nation_of(pkg)
        if pos is None or nation is None:
            why = "no parsable position" if pos is None else nation_how
            report["skipped_nodes"].append({"node": wid, "why": why})
            for row in pkg["forces"]:
                row_report(pkg, row, "skipped", "node not converted: " + why)
            continue
        side = SIDE_OF[nation]
        lat, lon = pos[0], continuous(pos[1])

        # classify every row once
        ships, aircraft, fields, defences = [], [], [], []
        for row in pkg["forces"]:
            if row["outcome"] not in ("exact", "proxy"):
                row_report(pkg, row, "skipped", f"register outcome {row['outcome']}")
                continue
            qty = quantity(row)
            if qty == 0:
                row_report(pkg, row, "skipped", "scenario quantity 0 / optional / abstract")
                continue
            resolved = []
            for u in row["unit_ids"]:
                r, how = resolve(u)
                resolved.append((u, r, how))
            first = next(((u, r, how) for u, r, how in resolved if r), None)
            if first is None:
                row_report(pkg, row, "skipped", "no unit id resolves in the collection")
                continue
            cat = category(first[1])
            row = dict(row, _uid=first[1], _how=first[2], _qty=qty, _cat=cat,
                       _carrier=is_carrier(first[1]) if cat == "ship" else False)
            if cat == "ship":
                ships.append(row)
            elif cat == "air":
                if embarked(row):
                    row_report(pkg, row, "skipped", "embarked flight or carrier wing: the engine "
                               "flies a hull's own air group; ship flights are not separate forces")
                else:
                    aircraft.append(row)
            elif cat == "airfield":
                fields.append(row)
            elif cat == "land" and row["allocation"].startswith("fixed_defence"):
                defences.append(row)
            elif cat in ("civil_ship", "civil_air"):
                row_report(pkg, row, "traffic", "civil unit: listed in traffic, not a force",
                           unit=first[1])
                used["civil:" + first[1]] += qty
            else:
                row_report(pkg, row, "skipped", "installation scenery or land unit: the engine "
                           "places its own garrisons (ground section)", unit=first[1])

        if not ships and not aircraft and not fields:
            report["skipped_nodes"].append({"node": wid, "why": "nothing convertible"})
            continue

        kind = ("Port" if pkg["node_kind"].startswith("port_commercial") else
                "AirBase" if (pkg["node_kind"] in ("air_base", "naval_air_station") and not ships)
                or not ships else "NavalBase")
        bid = re.sub(r"[^a-z0-9_]", "_", wid.lower())
        base = {"id": bid, "name": clean_name(pkg["name"]), "side": side, "nation": nation,
                "kind": kind, "lat": round(lat, 3), "lon": round(lon, 3),
                "income": 6 if wid in DEPOTS else 3 if kind == "NavalBase" else 1}
        if wid in SHIPYARDS:
            base["shipyard"] = True
        if wid in DEPOTS:
            base.update({"depot": True, "production": 1})
            base["airlifts" if kind == "AirBase" else "convoys"] = 10
        if homeland(pkg, nation):
            base["homeland"] = True
        field_uid = next((r["_uid"] for r in fields), None)
        if kind == "AirBase":
            base["field"] = {"unit": field_uid or "airfield_small_1", "heading": 0,
                             "lat": round(lat, 4), "lon": round(lon, 4)}
        bases.append(base)
        base_ids.add(bid)
        node_base[wid] = bid
        air_bid = bid if kind == "AirBase" else None
        if aircraft and kind != "AirBase":
            air_bid = bid + "_air"
            bases.append({"id": air_bid, "name": clean_name(pkg["name"]) + " airfield",
                          "side": side, "nation": nation, "kind": "AirBase",
                          "lat": round(lat, 3), "lon": round(lon, 3), "income": 1,
                          "port": bid, "colocated": True,
                          "field": {"unit": field_uid or "airfield_small_1", "heading": 0,
                                    "lat": round(lat, 4), "lon": round(lon, 4)}})
            base_ids.add(air_bid)
        node_air[wid] = air_bid
        report["bases"].append({"node": wid, "base": bid, "kind": kind, "nation": nation,
                                "nation_from": nation_how, "position": [lat, lon],
                                "anchor_on_water": is_water(lat, lon),
                                "companion_airbase": air_bid if air_bid != bid else None,
                                "field_unit": (field_uid or "airfield_small_1") if air_bid else None,
                                "field_heading": "0 - SCENARIO CHOICE, runway heading not in the register"
                                if air_bid else None})
        for r in fields:
            row_report(pkg, r, "converted", "airfield unit of the base", base=air_bid or bid)
        for r in defences:
            row_report(pkg, r, "ground", "fixed defence: listed under ground.airDefence for "
                       f"{nation}", unit=r["_uid"])
            used[f"defence:{nation}:{r['_uid']}"] += 1

        # surface forces
        # At sea only where the register says so: a carrier in maintenance or in
        # reserve, or an amphibious ship alongside, stays in harbour.
        at_sea = [r for r in ships if r["allocation"] in AT_SEA
                  or (r["allocation"] == "support" and "with" in r["role"].lower())]
        patrol_rows = [r for r in ships if r["allocation"].startswith("patrol") and r not in at_sea]
        port_rows = [r for r in ships if r not in at_sea and r not in patrol_rows]
        groups, loose = group_at_sea(at_sea)
        port_rows += [r for r in loose if r["allocation"] == "support"]
        loose = [r for r in loose if r["allocation"] != "support"]
        short = clean_name(pkg["name"])

        def specs(rows):
            out = []
            for r in rows:
                names = hull_names(r, r["_qty"])
                out.append(unit_spec(r["_uid"], r["_qty"], names))
                used[r["_uid"]] += r["_qty"]
            return out

        for key, rows in groups.items():
            carrier = rows[0]
            if key in DEPLOYED_AT:
                where, why = DEPLOYED_AT[key]
                at = (where[0], continuous(where[1]))
            else:
                at, why = water_point(lat, lon), "near the home base - SCENARIO CHOICE"
            label = (hull_names(carrier, 1) or [display(carrier["_uid"])])[0]
            extra = {"cargo": "full"} if any(r["_uid"] in REPLENISHMENT for r in rows) else None
            f = add_force(f"{label} group", side, bid, "Surface", specs(rows), at=at, extra=extra)
            report["forces"].append({"force": f["name"], "node": wid, "rows": [r["asset_id"] for r in rows],
                                     "at": f.get("at"), "at_why": why})
            for r in rows:
                row_report(pkg, r, "converted", "surface force at sea", force=f["name"], unit=r["_uid"],
                           resolved=r["_how"])
        if loose:
            at = water_point(lat, lon)
            extra = {"cargo": "full"} if any(r["_uid"] in REPLENISHMENT for r in loose) else None
            f = add_force(f"{short} task group", side, bid, "Surface", specs(loose), at=at, extra=extra)
            report["forces"].append({"force": f["name"], "node": wid, "rows": [r["asset_id"] for r in loose],
                                     "at": f.get("at"), "at_why": "near the home base - SCENARIO CHOICE"})
            for r in loose:
                row_report(pkg, r, "converted", "surface force at sea", force=f["name"], unit=r["_uid"],
                           resolved=r["_how"])
        # A submarine on patrol is its own force: it does not keep station with
        # the surface ships of the same base.
        subs = [r for r in patrol_rows if bp.unit_type(r["_uid"]) == "Submarine"]
        for label, prows in (("patrol", [r for r in patrol_rows if r not in subs]),
                             ("submarine patrol", subs)):
            if not prows:
                continue
            f = add_force(f"{short} {label}", side, bid, "Surface", specs(prows))
            ring, how = water_ring(lat, lon)
            if ring:
                patrols.append({"force": f["name"], "points": [list(p) for p in ring]})
            report["forces"].append({"force": f["name"], "node": wid,
                                     "rows": [r["asset_id"] for r in prows],
                                     "patrol": f"{how} - SCENARIO CHOICE" if ring
                                     else "no water ring found: in harbour, no patrol"})
            for r in prows:
                row_report(pkg, r, "converted", label + " force", force=f["name"], unit=r["_uid"],
                           resolved=r["_how"])
        if port_rows:
            extra = {"cargo": "full"} if any(r["_uid"] in REPLENISHMENT for r in port_rows) else None
            f = add_force(f"{short} harbour", side, bid, "Surface", specs(port_rows), extra=extra)
            report["forces"].append({"force": f["name"], "node": wid,
                                     "rows": [r["asset_id"] for r in port_rows]})
            for r in port_rows:
                row_report(pkg, r, "converted", "in harbour (resident, maintenance, reserve, "
                           "support)", force=f["name"], unit=r["_uid"], resolved=r["_how"])

        # air forces: one per aircraft type at the node's air base
        for r in aircraft:
            pending_air[(wid, air_bid, side, short)][r["_uid"]] += r["_qty"]
            row_report(pkg, r, "converted", "air force at the node's air base", unit=r["_uid"],
                       resolved=r["_how"], base=air_bid)

    for (wid, air_bid, side, short), counts in pending_air.items():
        for uid, qty in counts.items():
            f = add_force(f"{short} {display(uid)}", side, air_bid, "Air",
                          [uid + (f" x{qty}" if qty > 1 else "")])
            used[uid] += qty
            report["forces"].append({"force": f["name"], "node": wid, "aircraft": uid, "count": qty})

    # supply lines: every base draws from its own nation's nearest depot within
    # reach, else its side's nearest. SCENARIO CHOICE - the register keeps the
    # real logistics network abstract.
    depots = [b for b in bases if b.get("depot")]
    for b in bases:
        if b.get("depot") or b.get("colocated"):
            continue

        def dist(d):
            return gc_nm((b["lat"], b["lon"]), (d["lat"], d["lon"]))
        own = [d for d in depots if d["nation"] == b["nation"] and dist(d) <= SUPPLY_REACH_NM]
        same = own or [d for d in depots if d["side"] == b["side"]]
        if same:
            b["supplyFrom"] = min(same, key=dist)["id"]

    return reg, report, bases, forces, patrols, used


# --- world-level sections ------------------------------------------------------

# Main sea lanes, authored for this draft and checked for water at 4 NM steps.
LANES = [
    ("Malacca and Singapore Straits", 4,
     [(6.2, 94.8), (5.5, 97.5), (3.6, 100.0), (2.3, 101.6), (1.25, 103.3), (1.2, 104.2)]),
    ("South China Sea", 4, [(1.4, 104.6), (5.0, 107.0), (10.0, 111.5), (16.0, 115.5), (21.0, 117.5)]),
    ("Taiwan Strait to the East China Sea", 3,
     [(21.8, 118.2), (23.6, 119.0), (25.5, 120.6), (28.0, 122.6), (31.0, 123.4)]),
    ("East China Sea to Tokyo Bay", 3,
     [(31.0, 123.6), (30.5, 128.0), (31.5, 133.0), (33.6, 137.5), (34.9, 139.8)]),
    ("Trans-Pacific", 2, [(34.6, 140.3), (30.0, 160.0), (24.0, 190.0), (21.0, 202.2), (27.0, 225.0),
                          (32.6, 242.6)]),
    ("Gulf of Aden and the Red Sea", 4,
     [(12.0, 52.0), (12.3, 46.0), (12.55, 43.45), (14.5, 42.2), (20.0, 38.6), (24.0, 36.0),
      (27.0, 34.2), (27.9, 33.7), (28.5, 33.1), (29.7, 32.6)]),
    ("Strait of Hormuz to Bahrain", 3,
     [(23.5, 59.5), (25.6, 57.4), (26.5, 56.4), (26.1, 54.5), (26.4, 51.5), (26.3, 50.75)]),
    ("Mediterranean", 3,
     [(31.4, 32.3), (33.3, 28.5), (35.0, 24.6), (36.3, 20.0), (37.0, 15.5), (37.4, 11.2),
      (37.5, 6.0), (36.4, -1.0), (35.95, -5.4), (36.3, -7.5)]),
    ("North Atlantic", 2, [(36.3, -7.8), (38.0, -20.0), (40.0, -40.0), (38.5, -60.0),
                           (36.9, -75.8)]),
    ("Indian Ocean", 2, [(5.8, 95.0), (2.0, 85.0), (-7.0, 72.6), (5.0, 66.0), (12.0, 55.0)]),
    ("Cape Leeuwin to the Sunda Strait", 1, [(-32.3, 115.4), (-25.0, 108.0), (-15.0, 104.0),
                                             (-6.9, 104.8)]),
]
AIRWAYS = [
    ("Gulf to Singapore", 2, [(26.27, 50.63), (6.9, 79.9), (1.35, 103.99)],
     ["civ_a330/Squadron1", "civ_a380/Squadron2", "civ_a320/Squadron3"]),
    ("Mediterranean corridor", 2, [(36.65, -6.35), (37.47, 15.07), (35.53, 24.15), (34.59, 32.99)],
     ["civ_a320/Squadron4", "civ_a330/Squadron5"]),
    ("Tokyo to Guam", 1, [(35.55, 139.78), (26.2, 127.65), (13.48, 144.8)],
     ["civ_a320/Squadron6", "civ_a330/Squadron2"]),
    ("Honolulu to San Diego", 1, [(21.32, 202.08), (32.73, 242.81)],
     ["civ_a330/Squadron3", "civ_dc-10/Squadron2"]),
]


def detour(a, b, depth=0):
    """Points from a to b that stay on water: the straight leg if it is wet,
    else a midpoint pushed sideways until both halves are. None if not found."""
    if segment_wet(a, b, step_nm=3):
        return [a, b]
    if depth >= 4:
        return None
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    brg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    for off in (5, 10, 20, 35, 60, 90, 130):
        for side in (90, -90):
            m = offset(mid[0], mid[1], brg + side, off)
            if not in_bounds(*m) or is_water(*m) is False:
                continue
            left, right = detour(a, m, depth + 1), detour(m, b, depth + 1)
            if left and right:
                return left[:-1] + right
    return None


def lanes_checked(report):
    out = []
    for name, weight, pts in LANES:
        pts = [(la, continuous(lo)) for la, lo in pts]
        path, failed = [pts[0]], []
        for i in range(len(pts) - 1):
            leg = detour(pts[i], pts[i + 1])
            if leg is None:
                failed.append(i)
                path.append(pts[i + 1])
            else:
                path += leg[1:]
        report["lanes"].append({"lane": name, "authored_points": len(pts), "points": len(path),
                                "detour_points_added": len(path) - len(pts),
                                "legs_on_land": failed, "kept": not failed})
        if not failed:
            out.append({"name": name, "weight": weight,
                        "points": [[round(p[0], 3), round(p[1], 3)] for p in path]})
    return out


def nation_units(nations):
    """Per-nation unit lists the engine draws on for garrisons, convoys and
    escorts. Every id resolves in the collection or the build stops; a nation
    without its own entry borrows its side's lead nation's."""
    table = {
        "garrisons": {"US": ["usa_spa_m109a2"], "China": ["pla_spa_plz-83"], "Russia": ["wp_mbt_t-72a"],
                      "Japan": ["jsdf_mbt_type74"], "France": ["fr_apc_vab_top"], "UK": ["uk_ifv_fv510"],
                      "Italy": ["it_spaa_sidam_25"]},
        "airDefence": {"US": ["usa_sam_site_pac-3_small"], "China": ["pla_sam_site_hq-9"],
                       "Russia": ["wp_sam_site_sa-21"], "Japan": ["jsdf_sam_type81"],
                       "France": ["fr_sam_site_samp-t_small"], "UK": ["raf_rapier_launcher"],
                       "Norway": ["usa_SLAMRAAM_launcher"]},
        "troops": {"US": ["usa_mbt_abrams", "usa_ifv_bradley", "usa_aaa_vulcan"],
                   "China": ["pla_mbt_ztz-99a", "pla_ifv_zbd-04a", "pla_spaa_pgz-09"],
                   "Russia": ["wp_mbt_t-72a", "ru_spaa_mt-lb_sosna"],
                   "Japan": ["jsdf_mbt_type74", "jsdf_apc_type73"],
                   "France": ["fr_mbt_leclerc", "fr_ifv_vbci"], "UK": ["uk_mbt_fv4030_4", "uk_ifv_fv510"]},
        "merchants": {"US": ["civ_ms_sealift_pacific", "civ_ms_c8", "civ_ms_roro_a"],
                      "China": ["civ_ms_bulk", "civ_ms_freighter_a"],
                      "Russia": ["civ_ms_amra", "civ_ms_freighter_a"],
                      "Japan": ["civ_ms_car_carrier_a", "civ_ms_ritina"],
                      "Australia": ["civ_ms_freighter_a", "civ_ms_bulk"]},
        "escorts": {"US": "usn_lcs_freedom_suw_late", "China": "plan_type_054a_p5",
                    "Russia": "rfn_ffg_22350_1-4", "Australia": "ran_ffh_anzac",
                    "France": "fr_ffg_lafayette_modernized", "Italy": "ita_ffg_ppa",
                    "UK": "rn_opv_river_batch2"},
        "airlifts": {"US": "usmc_kc-130j", "China": "plaaf_y-20a", "Russia": "wp_il-76md",
                     "UK": "uk_a400m_airdroop-para"},
    }
    lead = {"blue": "US", "red": "China"}
    out = {}
    for section, per in table.items():
        out[section] = {}
        for n in nations:
            out[section][n] = per.get(n, per.get(lead[SIDE_OF[n]]))
    return out


# --- the buy list: each side's whole arsenal in the collection ----------------
# The engine's catalogue is what a side can order (Validate: an entry needs a
# unit, a known side and a nation; the audit lists a unit once). The author
# asked on 10 Oct 2026 for the combined arsenals: every ship, submarine and
# aircraft the collection gives a side's nations, not only the types in the
# opening forces. The operator is the Nation= of the winning *_variants.ini or
# *_squadrons.ini sections (Default's where a section has none); a type several
# nations fly is listed under the side's nation with the most sections, ties in
# side order. No era cut: most of the collection's units carry no ServiceDate,
# so a 2028 filter would drop the J-10C and the KJ-500 as readily as the Knox;
# the tier (the price band) orders the list instead. Left out: what is not a
# fighting unit - civil and fishing hulls, merchant and intelligence roles,
# target drones, satellites, balloons, decoys, rafts and mines - and ids with a
# space, which a campaign cannot name.
ARSENAL_DIRS = ("vessels", "submarines", "aircraft")
ARSENAL_TYPES = {"Vessel", "Submarine", "Aircraft", "Helicopter", "VTOL"}
NATION_KEY = {n: n for n in BLUE + RED} | {"Soviet": "Russia", "RU": "Russia"}
NOT_ARSENAL_ROLES = {"Merchant", "Spy", "SeaMine", "Deco"}
NOT_ARSENAL_ID = re.compile(r"^civ_|satellite|balloon|septar|target|decoy|raft|sea_mine|sampan|"
                            r"_ms_|_fv_|fishing|trawler|\s")
SIDE_ORDER = {n: i for i, n in enumerate(BLUE + RED)}


def operators(kind, uid):
    """The Nation= of every variant or squadron section of the winning file."""
    f = bp.winning(f"{kind}/{uid}_{'squadrons' if kind == 'aircraft' else 'variants'}.ini")
    if f is None:
        return []
    sections, default = [], None
    for line in bp.read(f).splitlines():
        head = re.match(r"\s*\[([^\]]+)\]", line)
        if head:
            sections.append([head.group(1).strip(), None])
            continue
        nat = re.match(r"\s*Nation\s*=\s*([^\s/]+)", line)
        if nat and sections and sections[-1][1] is None:
            sections[-1][1] = nat.group(1)
    for name, nat in sections:
        if name == "Default":
            default = nat
    return [nat or default for name, nat in sections if name != "General" and (nat or default)]


def arsenal():
    """uid -> (side, nation) for every fighting unit a side's nations operate,
    and a report of what was left out and why."""
    found, left, other = {}, collections.defaultdict(list), collections.Counter()
    for rel, (_token, path) in sorted(bp.index().items()):
        kind, _, name = rel.partition("/")
        if kind not in ARSENAL_DIRS or "/" in name or not name.endswith(".ini"):
            continue
        uid = path.stem
        if re.search(r"_(variants|squadrons|loadouts)$", uid, re.I) or uid in found:
            continue
        if bp.unit_type(uid) not in ARSENAL_TYPES:
            continue
        nations = [NATION_KEY[n] for n in operators(kind, uid) if n in NATION_KEY]
        if not nations:
            for n in set(operators(kind, uid)):
                other[n] += 1
            continue
        if NOT_ARSENAL_ID.search(uid.lower()):
            left["not a fighting unit (id)"].append(uid)
            continue
        if role(uid) in NOT_ARSENAL_ROLES:
            left[f"role {role(uid)}"].append(uid)
            continue
        per = collections.Counter(nations)
        best = max(per, key=lambda n: (per[n], -SIDE_ORDER[n]))
        found[uid] = (SIDE_OF[best], best)
    return found, {"left_out": {k: sorted(v) for k, v in sorted(left.items())},
                   "other_nations": dict(other.most_common())}


def check_ids(ids, where):
    missing = sorted({u for u in ids if bp.unit_file(u.split("/")[0])[1] is None})
    if missing:
        sys.exit(f"{where}: no enabled mod defines {', '.join(missing)}")


def main():
    reg, report, bases, forces, patrols, used = build()
    report["lanes"] = []
    nations = sorted({b["nation"] for b in bases}, key=lambda n: (SIDE_OF[n], n))
    units = nation_units(nations)

    # values for every military unit the definition names
    military = sorted({u for u in used if ":" not in u} | set(units["escorts"].values())
                      | set(REPLENISHMENT) & set(used) | set(TANKERS) & set(used))
    check_ids(military, "forces/escorts")
    values, value_basis = {}, {}
    for u in military:
        values[u], value_basis[u] = value_of(u)

    def tier(v):
        return next(i for i, cap in enumerate((120, 250, 450, 800, 1200, 10 ** 9)) if v <= cap)

    nation_of_unit = {}
    for f in forces:
        nat = next(b["nation"] for b in bases if b["id"] == f["base"])
        for spec in f["units"]:
            nation_of_unit.setdefault(spec.split(" ")[0], (f["side"], nat))
    for n, u in units["escorts"].items():
        nation_of_unit.setdefault(u, (SIDE_OF[n], n))

    # The buy list: both sides' whole arsenals, and every type in the opening
    # forces. A type a force fields stays on that force's side; its nation is
    # the operator's where the operator is on that side, else the base's.
    armoury, arsenal_report = arsenal()
    buyable = {u: sn for u, sn in armoury.items() if sn[1] in nations}
    for u in military:
        side, nat = nation_of_unit[u]
        if buyable.get(u, ("", ""))[0] != side:
            buyable[u] = (side, nat)
    for u in buyable:
        if u not in values:
            values[u], value_basis[u] = value_of(u)
    is_air = lambda u: bp.unit_type(u) in ("Aircraft", "Helicopter", "VTOL")   # noqa: E731
    catalogue = []
    for u in sorted(buyable, key=lambda u: (buyable[u][0] != "blue", SIDE_ORDER[buyable[u][1]],
                                            is_air(u), tier(values[u]), u)):
        side, nat = buyable[u]
        e = {"unit": u, "side": side, "nation": nat, "tier": tier(values[u])}
        if is_air(u):
            e["aircraft"] = True
        elif values[u] > 800:
            e["days"] = 20
        catalogue.append(e)
    report["arsenal"] = dict(arsenal_report, catalogue_by_side_nation={
        f"{s} {n}": {"ships": sum(1 for u, sn in buyable.items() if sn == (s, n) and not is_air(u)),
                     "aircraft": sum(1 for u, sn in buyable.items() if sn == (s, n) and is_air(u))}
        for s, n in sorted(set(buyable.values()), key=lambda sn: SIDE_ORDER[sn[1]])})

    present = lambda table: {k: v for k, v in table.items() if k in used}   # noqa: E731
    defence = collections.defaultdict(list)
    for key in used:
        if key.startswith("defence:"):
            _, nat, uid = key.split(":", 2)
            defence[nat].append(uid)
    air_defence = {n: sorted(set(units["airDefence"][n]) | set(defence.get(n, []))) for n in nations}

    civil = sorted({k.split(":", 1)[1] for k in used if k.startswith("civil:")})
    merchants = sorted({c for c in civil if bp.unit_type(c) == "Vessel" and not c.startswith("civ_fv")}
                       | {"civ_ms_bulk", "civ_ms_freighter_a", "civ_ms_car_carrier_a",
                          "civ_ms_ritina", "civ_ms_roro_a", "civ_ms_amra"})
    fishing = {"China": ["civ_fv_sampan", "civ_fv_fishingboat_c", "civ_fv_sterntrawler_a"],
               "Russia": ["civ_fv_okean", "civ_fv_sterntrawler_b"],
               "Japan": ["civ_fv_fishingboat_a", "civ_fv_sterntrawler_b"],
               "default": ["civ_fv_fishingboat_a", "civ_fv_dhow", "civ_fv_sterntrawler_a"]}
    airliners = sorted({a for _, _, _, al in AIRWAYS for a in al})
    lift = {u: n for u, n in {"usn_lhd_wasp": 3, "plan_lpd_type_071": 2}.items()}
    every = (military + merchants + civil + [u for v in fishing.values() for u in v] + airliners
             + list(lift) + [u for n in nations for s in ("garrisons", "troops") for u in units[s][n]]
             + [u for n in nations for u in air_defence[n]] + [u for v in units["merchants"].values() for u in v]
             + list(units["airlifts"].values()) + ["wp_agi_okean", "bio_humpback_whale",
                                                    "bio_fin_whale", "bio_blue_whale"])
    check_ids(every, "world sections")

    yards = collections.defaultdict(list)
    for b in bases:
        if b.get("shipyard"):
            yards[b["nation"]].append(b["id"])

    campaign = {
        "id": CAMPAIGN_ID,
        "name": "SEST World Sandbox 2028 (draft)",
        "description": ("DRAFT generated from the SEST world-population register. A persistent "
                        "2028 world built from the SEST research: real bases, their resident and "
                        "deployed forces, supply ships and routine patrols, mapped to the SEST "
                        "collection. Minimal story. Not tested in game."),
        "start": START,
        "bounds": BOUNDS,
        "view": VIEW,
        "sides": [
            {"id": "blue", "name": "United States and partners", "nations": [n for n in BLUE if n in nations],
             "hq": "SEST WORLD - BLUE", "command": "SEST WORLD - BLUE COMMAND",
             "color": "#4A90E2", "startingPoints": 400},
            # Playable, decided 10 Oct 2026. The sample keeps red "comingSoon";
            # playing red with blue as the AI is untested.
            {"id": "red", "name": "China and Russia", "nations": [n for n in RED if n in nations],
             "hq": "SEST WORLD - RED", "command": "SEST WORLD - RED COMMAND",
             "color": "#E24A4A", "startingPoints": 400},
        ],
        "bases": bases,
        "labels": [{"text": t, "lat": la, "lon": continuous(lo)} for t, la, lo in (
            ("North Pacific", 40.0, 175.0), ("Philippine Sea", 20.0, 130.0),
            ("South China Sea", 13.0, 113.0), ("Indian Ocean", -10.0, 80.0),
            ("Arabian Sea", 15.0, 64.0), ("Mediterranean Sea", 35.0, 18.0),
            ("North Atlantic", 40.0, -40.0), ("South Atlantic", -35.0, -20.0),
            ("Norwegian Sea", 68.0, 5.0), ("Tasman Sea", -38.0, 160.0))],
        "forces": forces,
        "fogOfWar": True,
        "enemyAirlifts": False,
        "ai": {"startTier": 5, "daysPerTier": 30},
        "invasions": [],
        "story": {"opening": {"blue": {"situation": [
            "October 2028. This is a sandbox, not a story: the bases, fleets and air groups "
            "on the map are the ones the SEST research places around the world, as they would "
            "normally be - in harbour, on patrol, working up or deployed.",
            "What happens next is decided by the campaign engine and by you. Ships use what "
            "they carry until a supply ship or a depot refills them."]},
            "red": {"situation": [
                "October 2028. This is a sandbox, not a story: the Chinese and Russian bases, "
                "fleets and air groups on the map are the ones the SEST research places, as they "
                "would normally be - in harbour, on patrol or deployed, from Hainan to the Kola "
                "Peninsula and Djibouti.",
                "What happens next is decided by the campaign engine and by you. Ships use what "
                "they carry until a supply ship or a depot refills them."]}}},
        "patrols": patrols,
        "ranks": {
            "blue": [{"name": n, "renown": r} for n, r in (
                ("Captain", 0), ("Commodore", 1500), ("Rear Admiral", 4000),
                ("Vice Admiral", 8000), ("Admiral", 14000))],
            "red": [{"name": n, "renown": r} for n, r in (
                ("Captain", 0), ("Rear Admiral", 3000), ("Vice Admiral", 7000),
                ("Admiral", 12000))]},
        "yards": {n: ", ".join(ids) for n, ids in yards.items()},
        "airWings": {},
        "replenishment": present(REPLENISHMENT),
        "tankers": present(TANKERS),
        "territories": {"blue": [], "red": []},
        "values": values,
        "catalogue": catalogue,
        "ground": {"units": [],
                   "garrisons": {n: units["garrisons"][n] for n in nations},
                   "airDefence": air_defence,
                   "troops": {n: units["troops"][n] for n in nations},
                   "garrisonSize": {"NavalBase": {"airDefence": 2, "troops": 2},
                                    "Port": {"airDefence": 1, "troops": 1},
                                    "AirBase": {"airDefence": 2, "troops": 1}},
                   "garrisonStrength": {"NavalBase": 0, "Port": 0, "AirBase": 0},
                   "lift": lift},
        "convoys": {"merchants": {n: units["merchants"][n] for n in nations},
                    "escorts": {n: units["escorts"][n] for n in nations},
                    "airlifts": {n: units["airlifts"][n] for n in nations}},
        "spyShips": {"units": ["wp_agi_okean"], "side": "red", "nation": "Russia", "chance": 0.15,
                     "laneNm": 60, "minNm": 10, "maxNm": 25},
        "traffic": {"lanes": lanes_checked(report), "merchants": merchants, "fishing": fishing,
                    "marineLife": ["bio_humpback_whale", "bio_fin_whale", "bio_blue_whale"],
                    "airliners": airliners,
                    "airways": [{"name": n, "weight": w, "suspended": False,
                                 "points": [[la, continuous(lo)] for la, lo in pts], "airliners": al}
                                for n, w, pts, al in AIRWAYS]},
    }

    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)
    (CAMPAIGN_DIR / "campaign.json").write_text(json.dumps(campaign, indent=2, ensure_ascii=True) + "\n",
                                                encoding="utf-8")
    (PACK / "_info.ini").write_text(
        "[Language_en]\n"
        "Name=SEST World Sandbox (Dynamic Campaign draft)\n"
        "Description=DRAFT, not tested in game. A data pack for Bungalow's Dynamic Campaign Mod "
        "(Workshop 3813157776): the SEST 2028 world - bases, fleets, air groups, supply ships and "
        "patrols from the SEST research - as a persistent campaign. Requires the Dynamic Campaign "
        "Mod, BepInEx and Anchor Chain, and the SEST Integration Pack with its collection.\n\n"
        "[Compatibility]\nGreaterThanEqualToVersion=0.8.3\nLessThanVersion=0.9.0\n",
        encoding="utf-8")
    report["values_basis"] = value_basis
    report["counts"] = {
        "register_rows": len(report["rows"]),
        "rows_by_outcome": dict(collections.Counter(r["outcome"] for r in report["rows"])),
        "bases": len(bases), "bases_by_kind": dict(collections.Counter(b["kind"] for b in bases)),
        "forces": len(forces), "forces_by_type": dict(collections.Counter(f["type"] for f in forces)),
        "patrols": len(patrols), "catalogue": len(catalogue), "values": len(values),
        "lanes_kept": len(campaign["traffic"]["lanes"]), "lanes_authored": len(LANES),
        "skipped_nodes": len(report["skipped_nodes"])}
    (OUT / "conversion.json").write_text(json.dumps(report, indent=1, ensure_ascii=True) + "\n",
                                         encoding="utf-8")
    c = report["counts"]
    print(f"wrote {CAMPAIGN_DIR.relative_to(ROOT)}/campaign.json")
    print(f"  {c['bases']} bases {c['bases_by_kind']}, {c['forces']} forces {c['forces_by_type']}, "
          f"{c['patrols']} patrols, {c['catalogue']} catalogue entries, "
          f"{c['lanes_kept']}/{c['lanes_authored']} lanes on water")
    print(f"  register rows: {c['rows_by_outcome']}; {c['skipped_nodes']} nodes not converted")
    if globe is None:
        print("  WARNING: global_land_mask not installed - water checks skipped "
              "(pip install global-land-mask numpy)")


if __name__ == "__main__":
    main()
