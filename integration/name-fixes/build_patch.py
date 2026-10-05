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

A key another SEST pack already writes is left to that pack. Section and key
names are never added, only values replaced.

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
        if out:
            lines = [f"# SEST Name Fixes - {sum(len(v) for v in out.values())} corrected name(s);"
                     " each key replaces exactly one winning line (mod id in the comment)."]
            for s in sorted(out):
                lines += ["", s]
                for k, new, tok in out[s]:
                    lines += [f"# was {tok}", f"{k}={new}"]
            d = OUT / "language_en"
            d.mkdir(parents=True, exist_ok=True)
            (d / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
            wrote += sum(len(v) for v in out.values())
    if stale:
        sys.exit("upstream changed under these corrections - review and drop or update:\n  "
                 + "\n  ".join(stale))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO, encoding="utf-8")
    print(f"built {OUT.name}: {wrote} corrected names")


if __name__ == "__main__":
    main()
