#!/usr/bin/env python3
"""Write docs/mno/permissions/ from final.json. Read-only over the repo except that folder."""
import collections, csv, io, json, re
from pathlib import Path

ROOT = Path("/home/claude/Seapower-mods")
DIST = ROOT / "integration/dist/SEST_Integration"
S = Path(__file__).resolve().parent
OUT = ROOT / "docs/mno/permissions"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "drafts").mkdir(exist_ok=True)

d = json.loads((S / "final.json").read_text())
F, T, C = d["final"], d["titles"], d["catalog"]

def title(w):
    return (C.get(w) or {}).get("title") or T.get(w) or f"Workshop {w}"

def author(w):
    a = (C.get(w) or {}).get("author") or ""
    return "" if a.lower().startswith("unknown") else a

# ---------------------------------------------------------------- groups
# Merge the two Spanish Navy items (one team per their Credits.txt).
for rel, r in F.items():
    if r.get("group") in ("3630495619", "3731208477"):
        r["group"] = "spanish-navy"

GROUPS = {}
for rel, r in F.items():
    if r["cls"] in ("close", "verbatim", "override") and r.get("group"):
        GROUPS.setdefault(r["group"], []).append(rel)

META = {
    "3514484654": dict(name="Greene", contact="Greene",
        channel="Steam profile comment or DM to Greene (the Workshop item 3514484654 was removed, so there is no item page)",
        licence="None found. The 4 Oct 2026 export (mods-source/_retired/3514484654) has no licence or readme; the model and textures come from a copy recovered on 5 Oct 2026 (integration/raaf-f-35a-jatm/recovered/SHA256SUMS)."),
    "rsg": dict(name="RSG (maintainer AlpineStatic)", contact="AlpineStatic",
        channel="Steam DM to AlpineStatic, or a comment on the YF-23 (3796349767) or Fury (3804868806) page",
        licence="RSG proprietary licence (LICENSE.txt in 3796349767 and 3804868806): compatibility patches may add content beside the mod 'provided they do not copy, replace, override, or redistribute Original Project Material'; anything else needs 'prior written authorization from RSG or AlpineStatic'."),
    "rats": dict(name="R.A.T.S. (Lukas Struckl, 'Ratte'; the owner's contact: kanalratte)", contact="Ratte",
        channel="The owner's existing conversation with the R.A.T.S. team (kanalratte)",
        licence="R.A.T.S. Source License 1.0 (mods-source/3826122523/LICENSE.txt) for versions released on or after 2026-11-18; Topographic Map 1.8.1 is dated 2026-11-22 (its CHANGELOG.md). The MIT notice SEST ships (integration/beta-feature-parity/third-party/SeaPowerTopo-LICENSE.txt, copied into the feature archive as Topography-MIT-LICENSE.txt) covers only the versions before 2026-11-18."),
    "mitchell600": dict(name="Mitchell600 / Euromod team", contact="Mitchell600",
        channel="Comment on Euromod - Main Pack (3629144864) or DM to Mitchell600; for the RAN mod (3820759806) also its co-authors Peter Garrett and USS Dogwater",
        licence=None),
    "maneuverwarfare": dict(name="ManeuverWarfare", contact="ManeuverWarfare", channel=None, licence=None),
    "misaka": dict(name="misaka", contact="misaka", channel=None, licence=None),
    "dingtools": dict(name="dingtools", contact="dingtools", channel=None,
        licence="Partial: mods-source/3741944366/assets/readme.txt says 'You can use these weapons freely in seapower, but please DO NOT re-upload them or copy the models to other places!'; mods-source/3652097318/.../agm-158/README.txt: 'Commercial use or reproduction is prohibited without permission'. Neither covers copying the .ini files into another item, so ask."),
    "mygo": dict(name="MyGo!!!!!鼓手椎名立希", contact="MyGo!!!!!鼓手椎名立希", channel=None, licence=None),
    "prof_ch4os": dict(name="Prof_CH4OS", contact="Prof_CH4OS", channel=None, licence=None),
    "skibidi": dict(name="SKIBIDI_RIZZLER123", contact="SKIBIDI_RIZZLER123", channel=None, licence=None),
    "flankymanga": dict(name="flankymanga", contact="flankymanga", channel=None, licence=None),
    "chevron9": dict(name="Chevron 9", contact="Chevron 9", channel=None, licence=None),
    "luzon-siam": dict(name="Author of The Luzon Line and The Siam Shield (name not recorded)", contact=None,
        channel="Comment on Philippines: The Luzon Line (3752415457) or Thailand: The Siam Shield (3711297532); the catalogue says one author made both", licence=None),
    "euromod-korea": dict(name="Author of the Euromod South Korea and HD Hyundai add-ons (name not recorded)", contact=None,
        channel="Comment on Euromod-South Korea Navy (3789208859) and Euromod-HD Hyundai Export Ships Mod (3812454152). Same author is likely (identical 'Euromod-Addon' descriptions), not confirmed", licence=None),
    "2154545636": dict(name="2154545636", contact="2154545636", channel=None, licence=None),
    "pogfrog": dict(name="Pog Frog", contact="Pog Frog", channel=None,
        licence="mods-source/3403661005/_info.ini, line 20: 'please feel free to iterate on this mod all I ask is that you credit those who worked on this before you'. Lines 7-8: the model is used with Jason Simpson's permission, which does not extend to his other models (MNO ships no model)."),
    "spanish-navy": dict(name="Spanish Navy Mod team (Jabeitor, Zzocalu, Jasoriab)", contact="Jabeitor",
        channel="Comment on Spanish Navy Mod (Modern) 3731208477 and (Cold War) 3630495619; their Credits.txt names Jasoriab for code",
        licence="None for the .ini files. Credits.txt in both items lists model permissions (Jason Simpson, Desdemicabina, Badcat109, CC BY / CC BY-NC-SA sources); MNO ships none of those models."),
    "3480965706": dict(name=None, contact=None, channel=None,
        licence="Credits.txt covers the third-party B-2 model (Rhine_Lab_Muelsyse, CC BY 4.0), not the mod's .ini files."),
}
STATUS = {g: "needs permission" for g in GROUPS}
STATUS["pogfrog"] = "licence already allows"
STATUS["rats"] = "needs permission"

# --------------------------------------------------------------- reasons
PACK_WHY = {
    "replenishment": "replenishment at sea: our build adds a supply block and/or 'ReloadableWithoutMagazine' lines so the ship can rearm and refuel from a supply ship; every other byte is the author's (tools/check_pack_fidelity.py proves this)",
    "collection-fixes": "collection compatibility fix: a broken reference, a clash between two mods' copies, a nation or a model block",
    "cross-deck": "cross-deck: allied helicopters added to the ship's flight deck",
    "allied-fixes": "allied fixes: a missing weapon id, a loadout or a squadron the campaigns need",
    "raaf-bases": "RAAF/RNZAF airbases, each built as a copy of this airbase unit and filled with the campaigns' aircraft",
    "ran-fleet": "RAN fleet: RAN hulls built from this ship, with the RAN air group",
    "intercept-model": "intercept model: puts back the game's intercept keys the round needs",
    "growler-ngj-malice": "Growler / Super Hornet: NGJ jamming pods and AIM-424 MALICE loadouts added",
    "a10c-plus": "A-10C+: an upgraded A-10C as a new unit id beside the original",
    "b52-arrw": "B-52 ARRW: the AGM-183A put on in-service B-52s and given a loft profile",
    "combat-costs": "Combat Cost Tracker: the tracker's own prices kept, gaps filled with labelled SEST estimates",
    "f-15ex-revamp": "F-15EX: extra loadouts",
    "rafale-f5": "Rafale F5: JATM, MALICE and LRASM loadouts on the late Rafales",
    "raptor-squadrons": "F-22: real squadron definitions (the mod's squadron files point at placeholders)",
    "f-35c-jatm": "F-35C: AIM-260 loadouts",
    "f-16cm-jatm": "F-16CM: AIM-260 / AIM-424 loadouts",
    "jmsdf-mogami": "Mogami: the JMSDF SH-60K air group",
    "raaf-f-35a-jatm": "RAAF F-35A: carries the aircraft after its item was removed, plus AIM-260 / AIM-424 loadouts",
    "world-sandbox": "world campaign: a unit the world campaign places",
    "adf-persistent-isr": "MQ-4C Triton built from this airframe",
}

def short_why(rel, r):
    p = r["pack"]
    if p == "replenishment" and "clone" in (r.get("how") or ""):
        return "replenishment at sea: a new supply-ship id built as a copy of the author's hull, with a supply block and renamed systems"
    if r["cls"] == "override":
        return "AIM-424 consistency: every AIM-424 in the collection flies SEST's sest_aim-424 flight model (owner decision 14 Oct 2026)"
    return PACK_WHY.get(p, p)

def first_sest_comment(rel):
    try:
        txt = (DIST / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    for l in txt.splitlines()[:40]:
        s = l.strip()
        if s.startswith(("#", ";")) and "SEST" in s:
            return re.sub(r"\s+", " ", s.lstrip("#; "))[:160]
    return ""

# ------------------------------------------------------------ FILE-LIST.csv
rows = []
for g, rels in GROUPS.items():
    for rel in sorted(rels):
        r = F[rel]
        rows.append({
            "author_group": g, "workshop_id": r["wid"], "workshop_title": title(r["wid"]),
            "class": {"close": "close adaptation", "verbatim": "verbatim copy",
                      "override": "override of the author's file (SEST values)"}[r["cls"]],
            "shipped_path": rel, "author_source": r.get("src") or "",
            "author_share": "" if r.get("overlap") is None else f"{r['overlap']:.0%}",
            "credits_txt": "" if r.get("credits_pct") is None else f"{r['credits_pct']}%",
            "sest_pack": r["pack"], "why": short_why(rel, r),
            "evidence": r.get("how") or "", "sest_note_in_file": first_sest_comment(rel)})
rows.sort(key=lambda x: (x["author_group"], x["workshop_id"], x["shipped_path"]))
with open(OUT / "FILE-LIST.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

# ------------------------------------------------------------- summaries
def gsum(g):
    rels = GROUPS.get(g, [])
    items = collections.Counter(F[r]["wid"] for r in rels)
    cls = collections.Counter(F[r]["cls"] for r in rels)
    folders = collections.Counter(r.split("/")[0] for r in rels)
    packs = collections.Counter(F[r]["pack"] for r in rels)
    return rels, items, cls, folders, packs

def gname(g):
    m = META.get(g, {})
    if m.get("name"):
        return m["name"]
    items = gsum(g)[1]
    a = {author(w) for w in items} - {""}
    if a:
        return ", ".join(sorted(a))
    return "Author of " + " / ".join(title(w) for w in items) + " (name not recorded)"

def gchannel(g):
    m = META.get(g, {})
    if m.get("channel"):
        return m["channel"]
    items = gsum(g)[1]
    return "Comment on " + "; ".join(f"{title(w)} ({w})" for w in items) + \
        (f", or DM to {m.get('contact') or gname(g)}" if (m.get("contact") or author(next(iter(items)))) else "")

def glicence(g):
    m = META.get(g, {})
    return m.get("licence") or "None found in the export (no LICENSE, readme or permission text in the item's mods-source folder): all rights reserved by default"

# referencing-only items (SEST-original files that patch or name a mod)
SKIP_TOP = {"LOAD-ORDER.txt", "REQUIRED-MODS.txt", "CREDITS.txt", "COST-COMPATIBILITY.txt",
            "CROSS-DECK.txt", "SEST-PROFILES.txt", "WORLD-CAMPAIGN-READ-ME.txt", "RIBBONS.txt",
            "LOADING-SCREEN-CREDITS.txt"}
ref = collections.defaultdict(collections.Counter)
for rel, r in F.items():
    if r["cls"] == "sest" and r.get("wid") and rel not in SKIP_TOP and "/" in rel \
            and not rel.startswith(("plugins/", "beta-support/", "Gallery/")):
        ref[r["wid"]][r["pack"]] += 1
derived_wids = {F[r]["wid"] for rels in GROUPS.values() for r in rels}
ref_only = {w: c for w, c in ref.items() if w not in derived_wids}

vanilla = [(rel, r) for rel, r in F.items() if r["cls"].startswith("vanilla")]
diffs = [(rel, r) for rel, r in F.items() if r.get("diff_reason")]
cred_extra = [rel for rel, r in F.items() if r["cls"] in ("close", "verbatim") and r.get("wid")
              and r.get("credits_pct") is None]

tot = collections.Counter(F[r]["cls"] for rels in GROUPS.values() for r in rels)
order = sorted(GROUPS, key=lambda g: (-len(GROUPS[g]), gname(g).lower()))
need = [g for g in order if STATUS[g] == "needs permission"]

json.dump({"order": order, "need": need, "tot": dict(tot), "ref_only": {w: dict(c) for w, c in ref_only.items()},
           "vanilla": len(vanilla), "diffs": len(diffs), "cred_extra": len(cred_extra),
           "groups": {g: {"name": gname(g), "n": len(GROUPS[g]), "status": STATUS[g]} for g in order}},
          open(S / "summary.json", "w"), indent=1, ensure_ascii=False)

# expose for the next script
import pickle
pickle.dump(dict(GROUPS=GROUPS, META=META, STATUS=STATUS, order=order, need=need, rows=rows,
                 ref_only={w: dict(c) for w, c in ref_only.items()}, vanilla=vanilla, diffs=diffs,
                 cred_extra=cred_extra, tot=dict(tot)),
            open(S / "state.pkl", "wb"))
print(len(GROUPS), "groups;", len(need), "need permission;", dict(tot))
print("ref-only items:", len(ref_only), "vanilla-derived:", len(vanilla), "credits rows dropped:", len(diffs),
      "derived files not in CREDITS:", len(cred_extra))
for g in order:
    print(f"  {STATUS[g]:24} {len(GROUPS[g]):4} {gname(g)}")
