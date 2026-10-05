#!/usr/bin/env python3
"""Build SEST Name Fixes: corrected display names, one key at a time.

language_*/ files merge key by key down the load order, and the SEST pack is
first, so a single key here replaces a single name and nothing else. This
pack writes only keys whose winning value is wrong:

- EXPLICIT: typos and wrong short names in units the campaigns use, each
  pinned to the exact text it replaces - if an upstream mod fixes or changes
  its line, the build stops so the entry can be dropped, never overwriting
  a newer name with an older correction;
- full-width punctuation (（ ） ， “ ”) in English name lines. The game's UI
  font has no glyphs for them, so "Su-30SM （14th GFAR）" shows as boxes;
  they become their ASCII forms. Applied to every winning Default, VariantN,
  SquadronN and Callsigns line, not only the campaigns' units. Nothing else
  in a line is touched: stray spaces are invisible and are left alone.

- MISSING_NAMES: units that have no English name at all - the encyclopedia
  lists them as "MISSING: <id> name or squadron", under Missing Type and
  Missing Class. Each gets a whole name section, based on a named sister
  unit of the same mod where there is one. A section is written only while
  no mod defines one, so it retires itself when the author adds names.

A key another SEST pack already writes is left to that pack.

    python3 integration/name-fixes/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
OUT = Path(__file__).resolve().parent / "SEST_Name_Fixes"
FILES = ("aircraft_names.ini", "vessel_names.ini", "land_units_names.ini")
NAME_KEY = re.compile(r"^(Default|Variant\d+|Squadron\d+|Callsigns)$")

# (file, section, key): (the winning text today, the correction)
EXPLICIT = {
    ("vessel_names.ini", "[ran_ffh_anzac]", "Default"):
        ("Anzac-class FFH,Frigate Helicopter", "Anzac-class FFH,Anzac"),
    ("vessel_names.ini", "[js_ffg_mogami]", "Variant4"):
        ("FFM-4 JS Mikuma,Mikma", "FFM-4 JS Mikuma,Mikuma"),
    ("vessel_names.ini", "[ko_ddg-991]", "Variant2"):
        ("Yulgok YiYi DDG-992 ,Sejong the Great", "Yulgok Yi I DDG-992,Sejong the Great"),
    ("aircraft_names.ini", "[usaf_f-15e_SE]", "Squadron3"):
        ("F-15E 336th FS 'Rockteers',F-15E", "F-15E 336th FS 'Rocketeers',F-15E"),
    ("aircraft_names.ini", "[pol_f-16c-bl52plus]", "Squadron1"):
        ("3th Tactical Squadron,F-16", "3rd Tactical Squadron,F-16"),
    ("land_units_names.ini", "[FOB]", "Variant1"):
        ("Forward Operating Base Deseert,FOB", "Forward Operating Base Desert,FOB"),
    ("land_units_names.ini", "[TBunkerTrench]", "Variant1"):
        ("T Bunker Trench Deseert,Bunker T", "T Bunker Trench Desert,Bunker T"),
    ("land_units_names.ini", "[Omega_trench]", "Variant1"):
        ("Omega Trench Deseert,U Trench", "Omega Trench Desert,U Trench"),
    ("land_units_names.ini", "[idf_dsws]", "Default"):
        ("Davids Sling Tel,Davids Sling", "David's Sling TEL,David's Sling"),
    ("land_units_names.ini", "[idf_dsws]", "Variant1"):
        ("Davids Sling Tel,Davids Sling", "David's Sling TEL,David's Sling"),
    ("land_units_names.ini", "[idf_dsws_radar]", "Default"):
        ("Davids Sling Radar,Davids Sling Radar", "David's Sling Radar,David's Sling Radar"),
    ("land_units_names.ini", "[idf_dsws_radar]", "Variant1"):
        ("Davids Sling Radar,Davids Sling Radar", "David's Sling Radar,David's Sling Radar"),
    ("aircraft_names.ini", "[usaf_rq-180]", "Callsigns"):
        ("Squadron1,蝙蝠,White Bat", "Squadron1,BAT,White Bat"),
}
SQN = lambda n, name: [f"Squadron{i}={name}" for i in range(1, n + 1)]
VAR = lambda n, name: [f"Variant{i}={name}" for i in range(1, n + 1)]
NOTE = "SEST: this unit ships with no English name; named by SEST Name Fixes."
# id: (file, [lines of its section])
MISSING_NAMES = {
    "jmsdf_ddh_ise": ("vessel_names.ini", [
        "Type=DDH,Helicopter Destroyer", "Default=Ise (Hyūga class),Ise",
        "DefaultDescription=JS Ise (DDH-182), the second Hyūga-class helicopter destroyer, "
        "commissioned in 2011. The mod builds her as her own unit with Hyūga's fit. " + NOTE,
        "Variant1=Ise DDH-182,Ise"]),
    "Virginia": ("vessel_names.ini", [
        "Type=SSN,Attack Submarine", "Default=Virginia-class SSN,Virginia",
        "DefaultDescription=Virginia-class nuclear attack submarine. " + NOTE,
        "Variant1=Virginia SSN-774,Virginia"]),
    "rn_oberon_class": ("vessel_names.ini", [
        "Type=SS,Patrol Submarine", "Default=Oberon-class submarine,Oberon",
        "DefaultDescription=Oberon-class diesel-electric patrol submarine of the Royal Navy. " + NOTE]
        + VAR(13, "Oberon-class submarine,Oberon")),
    "fr_sa-321G": ("aircraft_names.ini", [
        "Type=ASW Helicopter", "Default=SA 321G Super Frelon,SA.321G",
        "DefaultDescription=The SA 321G Super Frelon, the French Navy's anti-submarine "
        "version of the heavy helicopter. " + NOTE,
        "Squadron1=SA 321G France,SA.321G", "Squadron2=SA 321G France,SA.321G",
        "Squadron3=SA 321G France,SA.321G", "Squadron4=SA 321G Iraq,SA.321G"]),
    "wp_mi-24vp": ("aircraft_names.ini", [
        "Type=Attack Helicopter", "Default=Mi-24VP,Mi-24VP",
        "DefaultDescription=The Mi-24VP, a Mi-24V with a twin-barrel 23 mm gun in the nose turret. " + NOTE,
        "Squadron1=Mi-24VP Soviet,Mi-24VP"]),
    "fr_e2c": ("aircraft_names.ini", [
        "Type=AEW", "Default=E-2C Hawkeye (France),E-2C",
        "DefaultDescription=The French Navy's E-2C Hawkeye airborne early warning aircraft. " + NOTE]),
    "S2": ("aircraft_names.ini", [
        "Type=Maritime Patrol,MPA", "Default=Grumman S-2 Tracker,Tracker",
        "DefaultDescription=Grumman S-2 Tracker carrier-based anti-submarine aircraft. " + NOTE,
        "Squadron1=Tracker 816 Squadron RAN,Tracker", "Squadron2=Tracker 851 Squadron RAN,Tracker"]),
    "usn_a-4g": ("aircraft_names.ini", [
        "Type=Attack", "Default=Douglas A-4G Skyhawk,A-4G",
        "DefaultDescription=The A-4G Skyhawk, flown by the Royal Australian Navy's Fleet Air Arm. " + NOTE]
        + SQN(2, "A-4G Skyhawk RAN,A-4G")),
    "usn_a-4c": ("aircraft_names.ini", [
        "Type=Attack", "Default=Douglas A-4C Skyhawk,A-4C",
        "DefaultDescription=Douglas A-4C Skyhawk light attack aircraft. " + NOTE]
        + SQN(1, "A-4C Skyhawk,A-4C")),
    "Mirage_III": ("aircraft_names.ini", [
        "Type=Fighter", "Default=Dassault Mirage III,Mirage III",
        "DefaultDescription=Dassault Mirage III fighter. " + NOTE]
        + SQN(1, "Mirage III France,Mirage III") + ["Squadron2=Mirage III Australia,Mirage III"]),
    "h34": ("aircraft_names.ini", [
        "Type=ASW Helicopter", "Default=Sikorsky H-34,H-34",
        "DefaultDescription=Sikorsky H-34 helicopter. " + NOTE]
        + SQN(1, "H-34 Australia,H-34")),
    "rn_nimrod": ("aircraft_names.ini", [
        "Type=Maritime Patrol,MPA", "Default=Hawker Siddeley Nimrod (unfinished),Nimrod",
        "DefaultDescription=An unfinished Nimrod in The Royal Navy mod: its squadrons and role "
        "are still the airliner template it was copied from. The finished aircraft is the Nimrod MR.1. " + NOTE,
        "Squadron1=Nimrod 42 Squadron,Nimrod", "Squadron2=Nimrod 51 Squadron,Nimrod",
        "Squadron3=Nimrod 120/201/206 Squadron,Nimrod"]),
    "canberra_bomber": ("aircraft_names.ini", [
        "Type=Bomber", "Default=English Electric Canberra (unfinished),Canberra",
        "DefaultDescription=An unfinished Canberra in The Royal Navy mod: its squadrons and role "
        "are still the airliner template it was copied from. The finished aircraft is the RAF Canberra. " + NOTE]
        + SQN(8, "Canberra,Canberra")),
    "civ_car_pickup_1983_assault_wp": ("land_units_names.ini", [
        "Type=Vehicle", "Default=Assault Technical (Warsaw Pact),Assault Technical",
        "DefaultDescription=Pickup truck with a mounted weapon. " + NOTE,
        "Variant1=Assault Technical,Assault Technical"]),
    "wp_airbase_57": ("land_units_names.ini", [
        "Type=Airbase", "Default=Su-57 Airbase,Airbase",
        "DefaultDescription=Airbase laid out for the Su-57 mod. " + NOTE,
        "Variant1=Su-57 Airbase,Airbase"]),
}
FULLWIDTH = [(" （", " ("), ("（", " ("), ("）", ")"), ("，", ","), ("“", '"'), ("”", '"')]

INFO = """[Language_en]
Name=SEST Name Fixes
Description=Corrects unit and squadron display names one key at a time: typos (Rocketeers, Mikuma, Desert, David's Sling), the Anzac's short name, and full-width brackets and commas the game's font cannot show.

[Compatibility]
ApproximateVersion=0.8.4
"""


def load_order():
    toks = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt").read_text().splitlines()
            if l.strip() and not l.startswith("#")]
    return [t for t in toks if t.isdigit()] + ["_vanilla/original"]


def parse(path):
    """[(section, key, value)] in file order."""
    out, section = [], ""
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("["):
            section = s.split("]", 1)[0] + "]"
            continue
        m = re.match(r"^([^=#;/\s][^=]*?)\s*=(.*)$", line)
        if m:
            out.append((section, m.group(1).strip(), m.group(2).rstrip("\r")))
    return out


def sest_keys(name):
    keys = set()
    for f in (ROOT / "integration").glob(f"*/SEST_*/language_en/{name}"):
        if f.parts[-4] in ("dist", "name-fixes"):
            continue
        keys |= {(s, k) for s, k, _v in parse(f)}
    return keys


def fixed(value):
    v = value
    for a, b in FULLWIDTH:
        v = v.replace(a, b)
    return v


def main():
    order = load_order()
    if OUT.exists():
        import shutil
        shutil.rmtree(OUT)
    wrote, stale = 0, []
    for name in FILES:
        winners = {}
        for tok in order:
            f = MODS / tok / "language_en" / name
            if f.is_file():
                for s, k, v in parse(f):
                    winners.setdefault((s, k), (v, tok))
        taken = sest_keys(name)
        out = {}
        for (s, k), (v, tok) in winners.items():
            if (s, k) in taken or not NAME_KEY.match(k):
                continue
            ex = EXPLICIT.get((name, s, k))
            if ex:
                if v != ex[0]:
                    stale.append(f"{name} {s} {k}: now {v!r} (from {tok})")
                    continue
                new = ex[1]
            else:
                new = fixed(v)
            if new != v:
                out.setdefault(s, []).append((k, new, tok))
        for (fn, s, k), _ in EXPLICIT.items():
            if fn == name and (s, k) not in winners:
                stale.append(f"{name} {s} {k}: no longer defined by any mod")
        defined = {s.lower() for (s, k) in winners if k == "Default"}
        added = [(uid, body) for uid, (fn, body) in MISSING_NAMES.items()
                 if fn == name and f"[{uid}]".lower() not in defined]
        if out or added:
            lines = [f"# SEST Name Fixes - {sum(len(v) for v in out.values())} corrected name(s);"
                     " each key replaces exactly one winning line (mod id in the comment)."]
            for s in sorted(out):
                lines += ["", s]
                for k, new, tok in out[s]:
                    lines += [f"# was {tok}", f"{k}={new}"]
            if added:
                lines += ["", f"# {len(added)} unit(s) with no English name anywhere in the collection"]
                for uid, body in added:
                    lines += ["", f"[{uid}]"] + body
            d = OUT / "language_en"
            d.mkdir(parents=True, exist_ok=True)
            (d / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
            wrote += sum(len(v) for v in out.values()) + len(added)
    if stale:
        sys.exit("upstream changed under these corrections - review and drop or update:\n  "
                 + "\n  ".join(stale))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO, encoding="utf-8")
    print(f"built {OUT.name}: {wrote} corrected names")


if __name__ == "__main__":
    main()
