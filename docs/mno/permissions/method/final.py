#!/usr/bin/env python3
"""Combine derive.json (line overlap + check_pack_fidelity) with the measured
CREDITS.txt list (difflib >= 90 %, same logic as tools/consolidate_packs.py),
settle the differences, group by author, write final.json + FILE-LIST rows."""
import collections, difflib, json, re
from pathlib import Path

ROOT = Path("/home/claude/Seapower-mods")
MS = ROOT / "mods-source"
S = Path(__file__).resolve().parent
d = json.loads((S / "derive.json").read_text())
cred = json.loads((S / "credits_rows.json").read_text())
T, C = d["titles"], d["catalog"]
R = {r["rel"]: r for r in d["records"]}

def lines(p):
    return [l.rstrip() for l in Path(p).read_bytes().decode("utf-8-sig", "replace")
            .replace("\r\n", "\n").split("\n")]

def src_path(wid, name, kind):
    for base in (MS / wid, MS / "_retired" / wid):
        for f in base.rglob(name):
            if f.is_file():
                return f
    return None

DIST = ROOT / "integration/dist/SEST_Integration"
notes = []
credit_of = {}
for wid, v in cred.items():
    for rel, pct, origin in v["files"]:
        credit_of[rel] = (wid, pct, origin or rel.split("/")[-1])

final = {}
for rel, r in R.items():
    final[rel] = dict(r)

# 1. CREDITS rows my same-name matcher could not see (renamed derivations)
for rel, (wid, pct, origin) in credit_of.items():
    r = final[rel]
    if r["cls"] in ("close", "verbatim") and r.get("wid") == wid:
        r["credits_pct"] = pct
        continue
    if r["cls"] in ("close", "verbatim") and r.get("wid") != wid:
        r["credits_pct"] = pct
        r["credits_wid"] = wid
        notes.append(f"{rel}: CREDITS names {wid}, line overlap names {r['wid']}")
        continue
    if r["cls"].startswith("vanilla"):
        r["credits_wid"] = wid
        r["credits_pct"] = pct
        r["diff_reason"] = ("check_pack_fidelity resolves the upstream to the game's own file"
                            if "fidelity" in (r.get("how") or "") else
                            "the shipped file matches the game's own file more closely than the mod's")
        continue
    # sest with no same-name candidate: adopt the measured CREDITS row, after a vanilla check
    kind = rel.split("/")[0]
    sp = src_path(wid, origin, kind)
    van = MS / "_vanilla/original" / kind / origin
    vr = difflib.SequenceMatcher(None, lines(DIST / rel), lines(van)).ratio() if van.is_file() else 0
    ar = difflib.SequenceMatcher(None, lines(DIST / rel), lines(sp)).ratio() if sp else pct / 100
    if vr >= ar:
        r.update(cls="vanilla-close", diff_reason=f"game file {origin} is as alike ({vr:.0%})",
                 credits_wid=wid, credits_pct=pct)
        continue
    r.update(cls="close", wid=wid, src=str(sp.relative_to(ROOT)) if sp else None,
             overlap=round(ar, 3), credits_pct=pct,
             how=f"renamed copy of {origin}: {ar:.0%} alike (difflib, as CREDITS.txt measures)")

# 2. weapons.ini: section merge that is mostly the game's own text
w = final["systems/weapons.ini"]
w.update(cls="vanilla-close", author_wid=w["wid"], wid=None,
         how="section merge: 890/1055 lines are the game's own weapons.ini, 751 the Tu-95MS mod's "
             "copy of it (which is itself the game's text); SEST restores the game's sections")

# 3. combat-cost files: Chevron 9's tracker prices preserved; weapon file is borderline (49 %)
for rel in ("systems/sest_weapon_costs.ini",):
    r = final[rel]
    r.update(cls="close", how=r["how"] + "; classed close: 1807 of its lines are the tracker's "
             "own price lines, kept as the file says ('existing usable prices are preserved')")

# 4. classify Greene binaries explicitly
for rel, r in final.items():
    if rel.startswith("assets/") and r["cls"] == "verbatim":
        r["how"] = "sha256 equal to integration/raaf-f-35a-jatm/recovered (Greene's model/textures)"

# 5. the two RSG AIM-424 overrides
for rel in ("ammunition_overwrite/fury_aim424_SEST.ini",
            "ammunition_overwrite/yf23_aim424_internal_SEST.ini"):
    final[rel]["cls"] = "override"
    final[rel]["how"] = ("SEST values (integration/common/aim424.py) laid over the author's round by "
                         "#!extend; 22 generic lines coincide; no RSG text copied, but it overrides an "
                         "RSG file, which RSG's LICENSE.txt does not allow without written permission")

# --- author groups
GROUP_OF = {}
def put(gid, wids):
    for w in wids:
        GROUP_OF[w] = gid
put("mitchell600", ["3629144864", "3390330875", "3488139470", "3695809489", "3444379330",
                    "3642656500", "3820759806"])
put("maneuverwarfare", ["3433957933", "3468260539", "3461044389", "3486502935", "3594891803",
                        "3782020901"])
put("misaka", ["3737267013", "3425450153", "3418252667", "3459682829", "3414146266", "3567228449"])
put("dingtools", ["3636386513", "3741944366", "3652097318"])
put("mygo", ["3438479626", "3503670861", "3559495372"])
put("prof_ch4os", ["3606774881", "3607989779"])
put("skibidi", ["3564792549", "3715323261"])
put("flankymanga", ["3631042692", "3629269283"])
put("chevron9", ["3575847216", "3807187341"])
put("luzon-siam", ["3752415457", "3711297532"])
put("euromod-korea", ["3789208859", "3812454152"])
put("2154545636", ["3591563716", "3509329205"])
put("pogfrog", ["3403661005", "3499239964"])
put("rsg", ["3766210676", "3796349767", "3804868806", "3810611344", "3813033771", "3819522350",
            "3821992229"])

rows = collections.defaultdict(list)
for rel, r in final.items():
    if r["cls"] in ("close", "verbatim", "override") and r.get("wid"):
        g = GROUP_OF.get(r["wid"], r["wid"])
        r["group"] = g
        rows[g].append(rel)

out = {"final": final, "groups": {g: sorted(v) for g, v in rows.items()}, "notes": notes,
       "titles": T, "catalog": C}
(S / "final.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
cnt = collections.Counter(r["cls"] for r in final.values())
print(cnt)
der = [r for r in final.values() if r["cls"] in ("close", "verbatim") and r.get("wid")]
print("derived (author) files:", len(der), "items:", len({r["wid"] for r in der}),
      "groups:", len({r["group"] for r in der}))
print("override:", sum(1 for r in final.values() if r["cls"] == "override"))
print("credits rows excluded as vanilla:", sum(1 for r in final.values() if r.get("diff_reason")))
for n in notes:
    print("NOTE", n)
