#!/usr/bin/env python3
"""Add civilian and natural depth to a mission without touching what exists.

Every unit this writes is APPENDED as a new [NeutralVesselN] /
[NeutralAircraftN] / [NeutralBiologicN] section past the highest index the
mission already uses, and the NumberOfNeutral* counts are bumped to match.
No existing section, waypoint, position or formation line is read back out
and rewritten, so a hand-edited mission keeps every placement exactly.

Positions are real geography: the mission's own MapCenter is read from
[Environment] and latitude/longitude are converted with the same mapping the
NORTHERN FRONT builder uses (x = (lon - centreLon) * 60, z = (lat - centreLat)
* 60, 1 nm = 1/60 degree). Routes follow the actual Arafura, Timor and Banda
Sea shipping lanes and the airways between real city pairs.

Re-running is a no-op: every added vessel carries a NameOverride from this
file's own fleet list, so their presence is the signature that the depth
pass already ran.

Usage (repo root):
    python3 integration/missions/add_civ_depth.py --mission "NORTHERN FRONT III"
    python3 integration/missions/add_civ_depth.py --mission "NORTHERN FRONT III" --write
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = Path(__file__).resolve().parent

Y = "220.4727"          # vanilla sea-level constant for vessel waypoints

# --- extra merchant traffic -------------------------------------------------
# (type, name, variant_slot, start lat/lon, route lat/lon points, telegraph)
MERCHANTS = [
    ("civ_ms_ritina", "MT Timor Trader", (-10.80, 128.60),
     [(-10.95, 127.20), (-11.20, 125.80)], 3),
    ("civ_ms_bulk", "MV Gove Endeavour", (-11.90, 137.40),
     [(-11.40, 138.60), (-10.80, 140.20)], 2),
    ("civ_ms_mairangi_bay", "MV Arafura Star", (-9.80, 134.60),
     [(-10.20, 136.40), (-10.55, 139.00)], 3),
    ("civ_ms_sealift_pacific", "MT Banda Spirit", (-8.40, 132.00),
     [(-9.10, 133.60), (-9.80, 135.80)], 2),
    ("civ_ms_car_carrier_a", "MV Southern Cross Carrier", (-10.60, 141.60),
     [(-10.45, 140.20), (-10.15, 138.00)], 3),
    ("civ_ms_c7s68", "MV Coral Trader", (-11.50, 131.60),
     [(-11.05, 133.20), (-10.75, 135.60)], 2),
    ("civ_ms_bulk", "MV Weipa Voyager", (-9.40, 129.60),
     [(-10.10, 131.00), (-10.60, 133.00)], 2),
    ("civ_ms_encounter", "MV Darwin Runner", (-12.20, 130.95),
     [(-11.60, 131.80), (-11.00, 133.40)], 2),
    ("civ_ms_andizhan", "MV Tiwi Coaster", (-11.70, 130.40),
     [(-11.95, 130.70), (-12.25, 130.85)], 1),
]

# --- extra fishing activity -------------------------------------------------
FISHING = [
    ("civ_fv_sterntrawler_c", "FV Arafura Dawn", (-9.20, 135.40),
     [(-9.05, 135.05), (-9.30, 134.75)], 1),
    ("civ_fv_okean", "FV Aru Banks", (-6.60, 134.20),
     [(-6.85, 133.95), (-6.55, 133.70)], 1),
    ("civ_fv_fishingboat_b", "FV Shoal Bay", (-10.95, 130.20),
     [(-10.75, 129.95), (-11.05, 129.70)], 1),
    ("civ_fv_sterntrawler_a", "FV Carpentaria Belle", (-11.55, 136.80),
     [(-11.30, 136.50), (-11.60, 136.25)], 1),
]

# --- extra civil air traffic -------------------------------------------------
# (type, squadron, start lat/lon, altitude ft, route lat/lon points)
AIRCRAFT = [
    ("civ_a330", "Squadron19", (-12.60, 130.40), 37000,     # China Airlines
     [(-9.50, 128.00), (-6.00, 125.50)]),
    ("civ_a320", "Squadron65", (-8.60, 130.00), 35000,      # Virgin Australia
     [(-10.50, 130.60), (-12.35, 130.90)]),
    ("civ_a380", "Squadron9", (-6.20, 133.50), 41000,       # Singapore Airlines
     [(-9.80, 136.50), (-13.20, 139.80)]),
    ("civ_a330", "Squadron48", (-13.00, 137.00), 39000,     # Korean Air
     [(-10.00, 134.50), (-6.50, 131.50)]),
    ("civ_a320", "Squadron21", (-11.20, 141.60), 33000,     # Thai
     [(-11.60, 138.00), (-12.30, 131.40)]),
]

# --- extra biologic presence -------------------------------------------------
# (type, lat/lon, random spawn range in nm)
BIOLOGICS = [
    ("bio_humpback_whale", (-11.30, 129.80), 22),   # Timor shelf calving water
    ("bio_humpback_whale", (-12.10, 132.40), 18),   # Van Diemen Gulf approaches
    ("bio_blue_whale", (-7.20, 128.90), 30),        # Banda Sea deep water
    ("bio_fin_whale", (-11.80, 137.60), 25),        # Gulf of Carpentaria
    ("bio_humpback_whale", (-9.60, 134.80), 20),    # central Arafura
    ("bio_blue_whale", (-6.40, 131.20), 28),        # Banda deep basin
]

VESSEL_TEMPLATE = """[NeutralVessel{n}]
Type={type}
NameOverride={name}
VariantReference={variant}
UnlimitedFuel=False
WeaponStatus=Free
RadarsActive=True
CrewSkill=Trained
Morale=3
RelativePositionInNM={x},0,{z}
Telegraph={telegraph}
Heading={heading}
Waypoints={waypoints}
"""

AIRCRAFT_TEMPLATE = """[NeutralAircraft{n}]
Type={type}
SquadronReference={squadron}
UnlimitedFuel=False
WeaponStatus=Free
RadarsActive=True
Morale=3
RelativePositionInNM={x},{alt},{z}
Telegraph=3
Heading={heading}
Waypoints={waypoints}
"""

BIOLOGIC_TEMPLATE = """[NeutralBiologic{n}]
Type={type}
VariantReference=Default
UnlimitedFuel=False
WeaponStatus=Free
CrewSkill=Trained
Morale=3
RelativePositionInNM={x},shallow,{z}
RandomSpawnCenter={x},shallow,{z}
RandomSpawnRange={range}
Telegraph=3
Heading=0
"""


def map_centre(text):
    lat = re.search(r"^MapCenterLatitude=([-\d.]+)", text, re.M)
    lon = re.search(r"^MapCenterLongitude=([-\d.]+)", text, re.M)
    if not (lat and lon):
        sys.exit("mission has no MapCenter — cannot place units by lat/lon")
    return float(lat.group(1)), float(lon.group(1))


def make_ll(text):
    clat, clon = map_centre(text)

    def ll(lat, lon):
        return round((lon - clon) * 60.0, 1), round((lat - clat) * 60.0, 1)
    return ll


def heading(ax, az, bx, bz):
    """Compass heading from point A to point B, in the mission's x/z frame."""
    import math
    return int(round(math.degrees(math.atan2(bx - ax, bz - az))))


def variant_for(type_id, n):
    """A livery from the winning provider's pool, spread by section index."""
    sys.path.insert(0, str(MISSIONS))
    from refine_civ_traffic import variant_pool
    pool = variant_pool(type_id)
    return pool[(7 * n + 3) % len(pool)]


def highest(text, kind):
    idx = [int(m) for m in re.findall(rf"^\[Neutral{kind}(\d+)\]", text, re.M)]
    return max(idx) if idx else 0


def set_count(text, key, value):
    if re.search(rf"^{key}=", text, re.M):
        return re.sub(rf"^{key}=.*$", lambda _: f"{key}={value}", text, count=1, flags=re.M)
    # No count line yet: put it after the last one that does exist.
    return re.sub(r"^(NumberOfNeutral\w+=.*)$", lambda m: f"{m.group(1)}\n{key}={value}",
                  text, count=1, flags=re.M)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", required=True, help="mission name without .ini")
    ap.add_argument("--write", action="store_true", help="apply (default: report only)")
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

    names = [m[1] for m in MERCHANTS + FISHING]
    if any(f"NameOverride={n}" in text for n in names):
        print(f"{args.mission}: depth pass already applied — nothing to do")
        return

    ll = make_ll(text)
    v_n, a_n, b_n = (highest(text, k) for k in ("Vessel", "Aircraft", "Biologic"))
    added_v = added_a = added_b = 0
    blocks = []

    for type_id, name, start, route, telegraph in MERCHANTS + FISHING:
        v_n += 1
        added_v += 1
        sx, sz = ll(*start)
        pts = [ll(*p) for p in route]
        legs = "|".join(f"{x},{Y},{z}" for x, z in pts)
        legs += f"/SetTelegraph,{telegraph}"
        blocks.append(VESSEL_TEMPLATE.format(
            n=v_n, type=type_id, name=name, variant=variant_for(type_id, v_n),
            x=sx, z=sz, telegraph=telegraph,
            heading=heading(sx, sz, pts[0][0], pts[0][1]), waypoints=legs))

    for type_id, squadron, start, alt, route in AIRCRAFT:
        a_n += 1
        added_a += 1
        sx, sz = ll(*start)
        pts = [ll(*p) for p in route]
        legs = "|".join(f"{x},{alt},{z}" for x, z in pts)
        blocks.append(AIRCRAFT_TEMPLATE.format(
            n=a_n, type=type_id, squadron=squadron, x=sx, alt=alt, z=sz,
            heading=heading(sx, sz, pts[0][0], pts[0][1]), waypoints=legs))

    for type_id, at, rng in BIOLOGICS:
        b_n += 1
        added_b += 1
        bx, bz = ll(*at)
        blocks.append(BIOLOGIC_TEMPLATE.format(n=b_n, type=type_id, x=bx, z=bz, range=rng))

    body = text.rstrip("\n") + "\n\n" + "\n".join(blocks)
    body = set_count(body, "NumberOfNeutralVessels", v_n)
    body = set_count(body, "NumberOfNeutralAircraft", a_n)
    body = set_count(body, "NumberOfNeutralBiologics", b_n)

    print(f"{args.mission}: +{added_v} vessels (now {v_n}), "
          f"+{added_a} aircraft (now {a_n}), +{added_b} biologics (now {b_n})")
    if args.write:
        path.write_text(body, encoding="utf-8", newline="\n")
        print("  written")
    else:
        print("  re-run with --write to apply")


if __name__ == "__main__":
    main()
