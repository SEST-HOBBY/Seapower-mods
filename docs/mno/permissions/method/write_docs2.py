#!/usr/bin/env python3
"""INVENTORY.md, drafts/, TRACKER.csv, PHOTOS-SOURCE-SEARCH.md."""
import collections, csv, json, pickle, re, textwrap
from pathlib import Path

ROOT = Path("/home/claude/Seapower-mods")
DIST = ROOT / "integration/dist/SEST_Integration"
S = Path(__file__).resolve().parent
OUT = ROOT / "docs/mno/permissions"
st = pickle.load(open(S / "state.pkl", "rb"))
fj = json.loads((S / "final.json").read_text())
F, T, C = fj["final"], fj["titles"], fj["catalog"]
GROUPS, META, STATUS = st["GROUPS"], st["META"], st["STATUS"]
cred = json.loads((S / "credits_rows.json").read_text())

import importlib.util
spec = importlib.util.spec_from_file_location("wd", S / "write_docs.py")
# reuse helpers without re-running: copy the small ones here
def title(w):
    return (C.get(w) or {}).get("title") or T.get(w) or f"Workshop {w}"
def author(w):
    a = (C.get(w) or {}).get("author") or ""
    return "" if a.lower().startswith("unknown") else a

def items_of(g):
    return collections.Counter(F[r]["wid"] for r in GROUPS[g])

def gname(g):
    m = META.get(g, {})
    if m.get("name"):
        return m["name"]
    a = {author(w) for w in items_of(g)} - {""}
    if a:
        return ", ".join(sorted(a))
    return "Author of " + " / ".join(title(w) for w in items_of(g)) + " (name not recorded)"

def contact(g):
    m = META.get(g, {})
    if "contact" in m and m["contact"]:
        return m["contact"]
    a = {author(w) for w in items_of(g)} - {""}
    return sorted(a)[0] if a else None

def channel(g):
    m = META.get(g, {})
    if m.get("channel"):
        return m["channel"]
    its = items_of(g)
    c = contact(g)
    s = "Comment on " + "; ".join(f"{title(w)} ({w})" for w in its)
    return s + (f", or a Steam DM to {c}" if c else "; author name not recorded, so check the item page first")

def licence(g):
    return META.get(g, {}).get("licence") or \
        "None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default"

PACK_SHORT = {
    "replenishment": "replenishment at sea: adds a supply block and/or reload lines so the ship can rearm and refuel from a supply ship. Every other line is yours, unchanged (our build checks this byte for byte)",
    "collection-fixes": "compatibility fixes inside the collection (a broken reference, a clash between two mods' copies of a file, a nation or a model fix)",
    "allied-fixes": "allied fixes (a missing weapon id, a loadout or squadron the campaigns need)",
    "raaf-bases": "RAAF/RNZAF airbases, built as copies of your base unit and filled with the campaigns' aircraft",
    "ran-fleet": "RAN ships built from your hull (new ids, RAN air group)",
    "intercept-model": "puts back the game's intercept values that the round needs",
    "growler-ngj-malice": "new NGJ jamming and AIM-424 loadouts on the Growler / Super Hornet",
    "a10c-plus": "an upgraded A-10C+ as a new unit id beside yours",
    "b52-arrw": "AGM-183A ARRW on in-service B-52s, with a loft profile",
    "combat-costs": "the tracker's own prices kept, gaps filled with labelled SEST estimates",
    "f-15ex-revamp": "extra F-15EX loadouts",
    "rafale-f5": "JATM, MALICE and LRASM loadouts on the late Rafales",
    "raptor-squadrons": "real F-22 squadron definitions (the shipped ones point at placeholders)",
    "f-35c-jatm": "AIM-260 loadouts on the F-35C",
    "f-16cm-jatm": "AIM-260 / AIM-424 loadouts on the F-16CM",
    "jmsdf-mogami": "the JMSDF SH-60K air group on the Mogami",
    "world-sandbox": "a unit the world campaign places",
    "raaf-f-35a-jatm": "carries the aircraft after the item was removed, plus AIM-260 / AIM-424 loadouts",
}

def is_clone(rel):
    return "clone" in (F[rel].get("how") or "")

def fmt_files(rels, limit=8):
    if len(rels) <= limit:
        return ["  " + r for r in sorted(rels)]
    fol = collections.Counter(r.split("/")[0] for r in rels)
    ex = sorted(rels)[:4]
    return ["  " + ", ".join(f"{n} in {k}/" for k, n in fol.most_common()),
            "  for example " + ", ".join(ex)]

import sys as _sys
_sys.path.insert(0, str(ROOT / "integration"))
from common import ras as _ras

def _repaired(rel):
    r = F[rel]
    if r["pack"] != "replenishment" or not rel.startswith("vessels/") or not r.get("src"):
        return False
    stem = Path(rel).stem
    if stem in _ras.HULL_REPAIRS:
        return True
    up = (ROOT / r["src"]).read_text(encoding="utf-8", errors="replace")
    return any(re.search(r"(?<![A-Za-z0-9_.-])" + re.escape(k) + r"(?![A-Za-z0-9_.-])", up)
               for k in list(_ras.STORE_FIXES) + list(_ras.AIRGROUP_FIXES))

def why_lines(rels):
    out = []
    rep = [r for r in rels if F[r]["pack"] == "replenishment"]
    if rep:
        ves = [r for r in rep if r.startswith("vessels/")]
        amm = [r for r in rep if r.startswith("ammunition/")]
        clones = [r for r in ves if is_clone(r)]
        fixed = [r for r in ves if _repaired(r) and not is_clone(r)]
        if ves:
            t = (f"- {len(ves)}: replenishment at sea. Our build adds a supply block and/or reload lines so the "
                 "ship can rearm and refuel from a supply ship (on supply ships, SEST's supply block replaces the file's own)")
            if clones:
                t += f" ({len(clones)} of them are new supply-ship ids built as copies of your hull, with renamed systems)"
            t += ". Apart from those lines"
            if fixed:
                t += f" (and, on {len(fixed)}, a weapon, sensor or helicopter id your file names that no mod defines, pointed at one that exists)"
            t += ", every line is yours, unchanged; the build checks this byte for byte."
            out.append(t)
        if amm:
            out.append(f"- {len(amm)}: replenishment at sea. A SupplyCategory line per round so ships can be rearmed with it "
                       "(on a few, also an AmmoPoints line or a [General] header); the rest of the file is yours, unchanged.")
    pk = collections.Counter(F[r]["pack"] for r in rels if F[r]["pack"] != "replenishment")
    for p, n in pk.most_common():
        txt = PACK_SHORT.get(p, p)
        out.append(f"- {n}: {txt[0].upper() + txt[1:]}.")
    return out

def in_credits(w):
    return w in cred

INTRO = ("I'm SEST-DEV. I'm about to publish Modern Naval Operations (MNO), a free, non-commercial "
         "integration pack for Sea Power: it puts 163 Workshop mods into one working load order and adds "
         "campaigns that use them.")

ASK = ["Is this OK with you? A one-word answer is fine:",
       "- YES: keep the files as they are, with the credit above.",
       "- YES, WITH CONDITIONS: tell me what (credit wording, a link, only some files, anything else).",
       "- NO: I'll take them out, or rework them as small patch files that carry only SEST's changes and load on top of your mod, so nothing of yours is copied.",
       "I'm holding the public MNO post until I've heard back from the authors.",
       "", "Thanks for your work,", "SEST-DEV"]

def standard_draft(g):
    rels = GROUPS[g]
    its = items_of(g)
    c = contact(g)
    hello = f"Hi {c}," if c else "Hi,"
    names = ", ".join(f"{title(w)} ({w})" for w in its)
    L = [hello, ""]
    if not c:
        L += [f"(To the author of {names}.)", ""]
    L += [INTRO + f" {'Your mods stay Required Items' if len(its) > 1 else 'Your mod stays a Required Item'}: "
          f"MNO doesn't work without {'them' if len(its) > 1 else 'it'}, and players subscribe from your page"
          f"{'s' if len(its) > 1 else ''}. MNO ships none of your "
          "models, textures, audio or DLLs, only .ini data files.", ""]
    nverb = sum(1 for r in rels if F[r]["cls"] == "verbatim")
    L += [f"Before the public post I'd like your OK for {len(rels)} file{'s' if len(rels) > 1 else ''} in MNO "
          f"that {'are' if len(rels) > 1 else 'is'} based on your work"
          + (f" ({nverb} unchanged copies)" if nverb else "") + ":"]
    for w, n in its.most_common():
        sub = [r for r in rels if F[r]["wid"] == w]
        if len(its) > 1:
            fol = collections.Counter(r.split("/")[0] for r in sub)
            if len(rels) > 12:
                L.append(f"  {title(w)} ({w}): {n} ({', '.join(f'{c} {k}' for k, c in fol.most_common())})")
                continue
            L.append(f"{title(w)} ({w}): {n} file{'s' if n > 1 else ''}")
        L += fmt_files(sub)
    if len(rels) > 8:
        L.append("  (I can send you the full list.)")
    L += ["", "Why they're in MNO:" if len(rels) > 1 else "Why it's in MNO:"] + why_lines(rels)
    if g == "spanish-navy":
        L.append("- None of the models your Credits.txt lists (the Galicia, Simpson and Badcat109 models among them) are in MNO.")
    if g == "chevron9":
        L.append("- The three cost files extend the Combat Cost Tracker's catalogue (#!extend); the prices it ships are kept as they are.")
    if g == "mitchell600":
        L += ["", "For the Modern Royal Australian Navy mod (3820759806) I'm asking its co-authors Peter Garrett and USS Dogwater too."]
    L += [""]
    cr = [w for w in its if in_credits(w)]
    if len(cr) == len(its):
        listed = sum(1 for r in rels if F[r].get("credits_pct") is not None)
        if listed == len(rels):
            L += [("Credit: each of these files is listed under your mod's title and Workshop ID in MNO's CREDITS.txt, " if len(its) == 1 else "Credit: each of these files is listed under its mod's title and Workshop ID in MNO's CREDITS.txt, ")
                  + "and " +("the mods are Required Items" if len(its) > 1 else "the mod is a Required Item") + " on the MNO page."]
        else:
            L += [("Credit: your mod's title and Workshop ID are" if len(its) == 1 else "Credit: your mods' titles and Workshop IDs are") + f" in MNO's CREDITS.txt ({listed} of these files are "
                  + "listed there one by one; I'll add the rest), and " + ("the mods are Required Items" if len(its) > 1 else "the mod is a Required Item") + " on the MNO page."]
    else:
        miss = ", ".join(title(w) for w in its if w not in cr)
        L += [f"Credit: listed in MNO's CREDITS.txt (to be added for {miss}), and " + ("the mods are Required Items" if len(its) > 1 else "the mod is a Required Item") + " on the MNO page."]
    L += [""] + ASK
    return "\n".join(L)

def greene_draft():
    rels = sorted(GROUPS["3514484654"])
    L = ["Hi Greene,", "",
         INTRO + " Your RAAF F-35A Lighting II (3514484654) was removed from the Workshop in October, and "
         "MNO's campaigns place the RAAF F-35A, so MNO currently carries the aircraft itself. It is the one "
         "case where MNO ships another author's model:", "",
         "Model and textures (unchanged copies, from a copy of your mod recovered on 5 Oct 2026):",
         "  assets/models/vehicle/aircraft/f-35/f-35a.obj",
         "  assets/models/vehicle/aircraft/f-35/textures/f-35a_tex.png, f-35a_nm.png, f-35a_spec.png",
         "  assets/textures/f-35/raaf_f-35a.png (the RAAF livery)",
         "Data files:",
         "  unchanged: aircraft/raaf_f-35a_squadrons.ini, ammunition/raaf_f-35_gun_pod.ini, ammunition/usaf_aim-120c7.ini, animations/animations_raaf_f-35a.ini, assets/models/vehicle/aircraft/f-35/f-35a_mat.ini",
         "  adapted: aircraft/raaf_f-35a.ini (new AIM-260 / AIM-424 loadouts), ammunition/usaf_gbu-31_v1.ini, usaf_gbu-53.ini, usaf_jsm.ini, usaf_jsm_land.ini (their weapon models weren't recovered, so they point at models still in the collection), and three of your weapon names in language_en/ammunition_names.ini",
         "", "Stats, loadouts, squadrons and callsigns are yours. No DLLs of yours are involved.", "",
         "Credit: CREDITS.txt names you and the mod as the source of the model, textures and files; "
         "I'm happy to word it however you like.", "",
         "Is this OK with you? A one-word answer is fine:",
         "- YES: keep it as it is, with that credit.",
         "- YES, WITH CONDITIONS: tell me what (credit wording, a link, no livery, anything else).",
         "- NO: I'll remove the aircraft and its files from MNO. If you ever re-upload the mod, I'll drop the copies and make it a Required Item instead.",
         "I'm holding the public MNO post until I've heard back.", "", "Thanks for the F-35A,", "SEST-DEV"]
    return "\n".join(L)

def rsg_draft():
    L = ["Hi AlpineStatic,", "",
         INTRO + " RSG's YF-23 Black Widow II (3796349767) and Anduril FQ-44 Fury (3804868806) stay Required "
         "Items; MNO ships none of RSG's models, textures, audio, DLLs or .ini files.", "",
         "Your LICENSE.txt asks that patches don't override RSG's files without written permission, and MNO "
         "has two small override files that do, so I'm asking before the public post:",
         "  ammunition_overwrite/yf23_aim424_internal_SEST.ini (#!extend ammunition/yf23_aim424_internal.ini)",
         "  ammunition_overwrite/fury_aim424_SEST.ini (#!extend ammunition/fury_aim424.ini)", "",
         "Why: every AIM-424 in the collection flies the same SEST AIM-424 flight model and model block, so the "
         "missile behaves the same on every aircraft. The files set only SEST's own guidance and model values; "
         "your round keeps its warhead, kill probability, mass, cost, signature, effects, sounds and name. The "
         "Fury file also sets ResourcesMeshRotation=0,0,0 for the AGM-88G mesh SEST's round renders with. "
         "No RSG text is copied into them.", "",
         "Credit: the YF-23 and Fury are Required Items on the MNO page, and I'll add them to MNO's CREDITS.txt with these two files.", "",
         "Is this OK with you? A one-word answer is fine:",
         "- YES: keep both files.",
         "- YES, WITH CONDITIONS: tell me what.",
         "- NO: I'll remove both files and your rounds fly with RSG's own values.",
         "I'm holding the public MNO post until I've heard back.", "", "Thanks,", "SEST-DEV"]
    return "\n".join(L)

def rats_draft():
    L = ["Hi Ratte,", "",
         "One more item for our R.A.T.S. list, separate from the Keel conversation and only about what ships "
         "in Modern Naval Operations (MNO) today. MNO is SEST's free, non-commercial integration pack; "
         "Topographic Map (3826122523) and R.A.T.S. Rigging (3843688859) are Required Items and come from "
         "your pages. MNO ships none of your files: no DLL, code, sounds, pictures or texts.", "",
         "What MNO does have: on Sea Power 0.9.3 Build 261123, SEST's loader (SEST's Anchor Chain fork, in MNO's "
         "beta feature archive beta-support/SEST-Beta-Features.zip) checks SeaPowerTopo.dll 1.8.1 by SHA-256 "
         "(4c3c0868...). At game start it writes an adapted copy of that DLL, read from your Workshop folder, to a "
         "private cache on the player's own PC (BepInEx\\config\\SEST-BetaAnchorChain\\beta-api-r16-261123\\...) and "
         "loads that copy. The only change is one constant: the shallow-water threshold in "
         "SeaPowerTopo.Render.Raster.SimHeight goes from -48 to -50 m, to match the game's 50 m boundary. Your "
         "Workshop file is not touched, and with any other hash nothing is adapted. Source: "
         "AssemblyAdapters.Topography.cs.", "",
         "Topographic Map 1.8.1 is under the R.A.T.S. Source License 1.0, and the archive still carries the old "
         "MIT notice for Topography (Topography-MIT-LICENSE.txt). I'll replace that with whatever wording you "
         "prefer.", "",
         "Credit: Topographic Map and Rigging are Required Items on the MNO page; I'll also credit them, and this adapter, in MNO's CREDITS.txt in words you're happy with.", "",
         "Is this OK with you?",
         "- YES: keep the adapter as it is.",
         "- YES, WITH CONDITIONS: tell me what (wording, a version check, a switch to turn it off, anything else).",
         "- NO: I'll take the adapter out; Topographic Map then runs unchanged.",
         "", "Thanks,", "SEST-DEV"]
    return "\n".join(L)

# --------------------------------------------------------------- drafts
for p in (OUT / "drafts").glob("*.txt"):
    p.unlink()
order = [g for g in st["order"] if STATUS[g] == "needs permission"]
special = {"3514484654": greene_draft, "rsg": rsg_draft}
draft_files = {}
n = 0
def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:50] or "author"
all_drafts = order + ["rats"]
for g in all_drafts:
    n += 1
    if g == "rats":
        text, name = rats_draft(), "rats-topographic-map"
    elif g in special:
        text, name = special[g](), slug(gname(g))
    else:
        text = standard_draft(g)
        name = slug(contact(g) or " ".join(title(w) for w in items_of(g)))
        if not re.search(r"[a-z0-9]{3}", name) or name in ("of", "author"):
            name = "author-of-" + "-".join(items_of(g))
    fn = f"{n:02d}-{name}.txt"
    (OUT / "drafts" / fn).write_text(text + "\n", encoding="utf-8")
    draft_files[g] = (fn, len(text))

# --------------------------------------------------------------- tracker
with open(OUT / "TRACKER.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["author_group", "workshop_ids", "channel", "status", "date_sent", "answer", "notes"])
    for g in all_drafts:
        ids = "3826122523 3843688859" if g == "rats" else " ".join(items_of(g))
        name = "R.A.T.S. (Lukas Struckl, 'Ratte')" if g == "rats" else gname(g)
        ch = META["rats"]["channel"] if g == "rats" else channel(g)
        nfiles = "Topographic Map 1.8.1 load-time adapter (adapted copy written to the player's local cache); 0 files of theirs shipped" if g == "rats" else f"{len(GROUPS[g])} files"
        w.writerow([name, ids, ch, "not sent", "", "", f"draft {draft_files[g][0]}; {nfiles}"])
    w.writerow([gname("pogfrog"), " ".join(items_of("pogfrog")), channel("pogfrog"), "not sent", "", "",
                "no request needed: licence already allows (3403661005/_info.ini line 20, credit required); optional courtesy note"])
    w.writerow(["Owner-supplied photos (21, rights holder unknown)", "", "source search by the owner (PHOTOS-SOURCE-SEARCH.md)",
                "not sent", "", "", "not a permission request until each photo's source is found"])

# --------------------------------------------------------------- photos
cat = json.loads(re.match(r"window\.CATALOGUE=(.*);\s*$", (DIST / "Gallery/catalogue.js").read_text(), re.S).group(1))
assets = {a["asset_id"]: a for a in cat["assets"]}
prof = [l.rstrip("\n").split("\t") for l in (ROOT / "integration/gallery/profiles.tsv").read_text().splitlines()
        if l and not l.startswith("#") and not l.startswith("unit_id")]
added = list(csv.DictReader(open(ROOT / "integration/gallery/added-photo-credits.csv", encoding="utf-8")))
HINT = {
 "mpq65": "US Army / DoD imagery is likely (DVIDS, army.mil); if so, public domain. Also check Raytheon press images (not free).",
 "df21": "Probably a PLA parade photo (Chinese state media, Xinhua/CCTV, or a Commons upload). Rights unclear until found.",
 "fob": "File is named 'FOB Salerno' (Khost, Afghanistan): likely a US Army/DoD photo on DVIDS or Commons; public domain if so.",
 "drydock": "Generic floating dry dock: check Commons and the US Navy (navy.mil) photo archive first; could equally be a shipyard's press photo.",
 "caracal": "H225M/EC725: Airbus Helicopters press images are copyrighted (press use only); Commons has free ones. Look for the exact frame.",
 "j35": "J-35 naval fighter (1835x1080, video-frame size): likely from Chinese state media or an air-show photographer; rights unclear.",
 "c130j": "KC-130J (4251x2391): very likely a USMC/DoD photo (DVIDS, marines.mil); public domain if so.",
 "kj2000": "KJ-2000: likely Chinese state media or a spotter site (Airliners.net, JetPhotos), which are copyrighted.",
 "oto127": "File name says Leonardo: likely a Leonardo press image (copyrighted; press use). Commons has free OTO 127/64 photos as a replacement.",
 "hmmwv": "M1151A1 HMMWV: likely a US Army/DoD photo (DVIDS, Commons); public domain if so.",
 "alconbury": "930x971 PNG of RAF Alconbury: possibly an aerial or satellite map capture (Google/Maxar imagery is not free). Check first.",
 "s3b": "S-3B Viking: likely a US Navy photo (navy.mil, DVIDS, Commons); public domain if so.",
 "sewip": "SEWIP Block 3: likely a US Navy or Northrop Grumman image; Navy = public domain, Northrop Grumman = copyrighted.",
 "shahed136": "Shahed-136 (392x220 thumbnail): likely a news-agency or social-media frame; rights unclear and hard to clear. Consider replacing.",
 "df26": "DF-26: likely a 2015/2019 parade photo from Chinese state media or Commons.",
 "f16a": "Labelled 'F-16C (93rd Fighter Squadron)' but the gallery notes it as a ROCAF F-16A: check the subject as well as the source. USAF photos (af.mil, DVIDS) are public domain.",
 "hq7": "HQ-7 / FM-90 launcher: could be a Commons photo, an exhibition photo or a manufacturer (CPMIEC) image.",
 "j11": "J-11B: likely Chinese state media or a spotter photo; rights unclear.",
 "j15": "J-15 (2000x1488): likely Chinese state media (China Military Online, Xinhua) or Commons.",
 "east_sale": "RAAF Base East Sale: Australian Defence images are Commonwealth copyright (not free without permission); Commons may have a free one.",
 "scud": "Scud TEL: many public-domain US DoD photos and Commons uploads exist; find the exact one.",
}
P = ["# Owner-supplied photos without a recorded source (21)", "",
     "These are the photos in `integration/gallery/added/` whose row in "
     "`integration/gallery/added-photo-credits.csv` has no creator, licence or source page (the 22nd row, "
     "`b-52g.jpg`, records U.S. Air Force, public domain, af.mil, and is left out). The gallery "
     "(`Gallery/catalogue.js`, `Gallery/PHOTO_CREDITS.txt`) shows each as 'Credit to be added · Not recorded', "
     "'Supplied by: the SEST author (October 2026)'.", "",
     "**This is a source search, not a permission request.** The rights holder of each photo is unknown, so "
     "there is nobody to ask yet. For each photo the owner first needs to find where it came from (the site, "
     "the photographer or agency, the licence). Then one of three things follows:", "",
     "1. Free licence or public domain (for example a US government photo, or Wikimedia Commons under CC BY / CC BY-SA): "
     "record creator, licence and source page in `added-photo-credits.csv`, run "
     "`integration/gallery/apply_added_photos.py`, rebuild. No request needed.",
     "2. Copyrighted with a findable owner: ask that owner (the tracker has one line for all of these; add a line per "
     "owner once known).",
     "3. Not found, or not clearable: replace it with a reviewed Commons photo, or remove it from the gallery, profiles and briefings.", "",
     "How to search: reverse image search on the original file in `integration/gallery/added/` (Google Lens, TinEye, "
     "Bing Visual Search, Yandex for Chinese and Russian subjects), then Wikimedia Commons, DVIDS (dvidshub.net) "
     "and the service photo sites for US subjects. The hints below are guesses from the file name, size and "
     "subject, not findings.", "",
     "Where each photo ships: `Gallery/images/...` (the original bytes, checked against `added/` by "
     "`integration/gallery/build_patch.py`), encyclopedia pictures `ui/profiles/<unit>.png` (resized with the "
     "credit line on the picture), and mission-briefing recognition pictures `sest_rec_<asset>.png` / banners "
     "`sest_banner_<asset>.png` (each briefing ships twice: under `campaigns/` and `missions/`).", "",
     "| # | Supplied file | Asset id | What it shows (gallery label) | Shipped as | Ships in | Source hint |",
     "|---|---|---|---|---|---|---|"]
k = 0
for row in added:
    if row["creator"].strip() or row["source_page"].strip():
        continue
    k += 1
    aid = row["asset_id"]
    a = assets[aid]
    profs = [p[0] for p in prof if len(p) > 2 and p[1] == aid and p[2] in ("same_type", "same_family")
             and (DIST / "ui/profiles" / f"{p[0]}.png").is_file()]
    rec = sorted(str(p.relative_to(DIST)) for p in DIST.rglob(f"sest_rec_{aid}.png"))
    ban = sorted(str(p.relative_to(DIST)) for p in DIST.rglob(f"sest_banner_{aid}.png"))
    where = [f"gallery"]
    if profs:
        where.append(f"{len(profs)} profile picture{'s' if len(profs) > 1 else ''} ({', '.join(profs)})")
    if rec:
        where.append(f"{len(rec)} briefing picture files")
    if ban:
        where.append(f"{len(ban)} briefing banner files")
    label = a.get("label", "")
    note = a.get("reference_note") or ""
    P.append(f"| {k} | `{row['file']}` | {aid} | {label} ({a.get('width')}x{a.get('height')})"
             + (f"; gallery note: {note}" if note and len(note) < 160 else "") +
             f" | `Gallery/{a['file']}` | {'; '.join(where)} | {HINT.get(aid, '')} |")
P += ["", f"Count: {k} photos.", "",
      "Briefings that show one of these photos say 'Photo supplied by the SEST author' under the picture "
      "(`integration/campaign/build_pack.py`, `photo_credit`). Once a source is recorded, a rebuild puts the real "
      "credit there, on the profile pictures and in `Gallery/PHOTO_CREDITS.txt`.", ""]
(OUT / "PHOTOS-SOURCE-SEARCH.md").write_text("\n".join(P), encoding="utf-8")
assert k == 21, k

# --------------------------------------------------------------- inventory
tot = st["tot"]
L = ["# MNO third-party permissions: inventory (25 Nov 2026)", "",
     "Drafted for the owner of Modern Naval Operations (MNO, SEST-DEV). Nothing here has been sent. It implements the "
     "decision in `docs/mno/OWNER-DECISIONS-20261125.md`: draft permission requests for the third-party material, keep "
     "the material as it is, and hold the public post until the requests are answered.", "",
     "Files in this folder:", "",
     "- `INVENTORY.md`: this file.",
     "- `drafts/NN-<author>.txt`: one message per author group that needs permission, ready to paste "
     "(a Steam comment holds 1,000 characters, so most drafts go in a Steam DM, or in two comments).",
     "- `TRACKER.csv`: one row per request for the owner to fill in.",
     "- `FILE-LIST.csv`: every shipped file that derives from another author's file, with its source file, "
     "share of the author's content, the SEST pack that made it, why, and the evidence.",
     "- `PHOTOS-SOURCE-SEARCH.md`: the 21 owner-supplied photos with no recorded source.",
     "- `method/`: the scripts that rebuilt this inventory. They only read the repo, apart from this folder. Run "
     "them in this order: `derive.py derive.json`, `parse_credits.py`, `final.py`, `write_docs.py`, `write_docs2.py`. "
     "Intermediate JSON goes beside the scripts.", "",
     "## 1. Result", "",
     f"Shipped item: `integration/dist/SEST_Integration/`, 4,930 files (the same count as "
     "`docs/releases/20261107/upload-manifest.json`).", "",
     "| Class | Files | Meaning |", "|---|---|---|",
     f"| Verbatim copy | {tot.get('verbatim', 0)} | Byte-identical (or identical apart from line endings) to the author's file. All are Greene's RAAF F-35A: 5 model and texture files and 5 .ini files |",
     f"| Close adaptation | {tot.get('close', 0)} | Mostly the author's content with SEST edits (supply blocks, loadouts, fixes, renamed copies) |",
     f"| Override of an author's file with SEST values | {tot.get('override', 0)} | The 2 RSG AIM-424 files: no RSG text, but they override RSG files, which RSG's licence forbids without permission |",
     f"| Game's own file, patched | {len(st['vanilla'])} | Derived from Sea Power's own data (`mods-source/_vanilla/original`), not from a mod author. Outside this request |",
     f"| SEST-original | {4930 - tot.get('verbatim', 0) - tot.get('close', 0) - tot.get('override', 0) - len(st['vanilla'])} | Campaigns, missions, gallery, plugins, SETUP, and patches that only name another mod's units, such as `#!extend` overrides and cross-deck lists. No permission needed |",
     "",
     f"Author groups: **{len(GROUPS) + 1}**, which is {len(GROUPS)} groups whose files MNO carries plus R.A.T.S. "
     "(Topographic Map adapter, no files). "
     f"**{len(all_drafts)} need permission** (drafts 01-{len(all_drafts):02d}). One group, Pog Frog, has a licence that "
     f"already allows it. {len(st['ref_only'])} more Workshop items are only referenced by SEST-original files "
     "(section 4).", "",
     "### How close this is to '~550 files from 67 author groups'", "",
     "- **550** is the measured list in the shipped `CREDITS.txt`, written by `tools/consolidate_packs.py` "
     "(`credits_text`): every shipped file in a unit folder (aircraft, vessels, land_units, ammunition...) that "
     "difflib finds 90 % or more like a mod file of the same kind. That list has 550 files in **66** Workshop items. "
     "I could not find a 67th. The earlier count was probably by Workshop item, not by author, and may have counted "
     "one item twice or added Greene's model files as a separate entry. That analysis is not in the repo, so this is a guess.",
     f"- This inventory finds **{tot.get('verbatim', 0) + tot.get('close', 0)} author-derived files in 66 Workshop "
     f"items**, which come from **{len(GROUPS) - 1} authors or teams** (several authors own more than one item: "
     "Mitchell600 has 7, ManeuverWarfare 6, misaka 6), plus RSG's 2 override files.",
     f"- From the 550 to {tot.get('verbatim', 0) + tot.get('close', 0)}: **{len(st['diffs'])} CREDITS rows are not "
     "an author's file.** `check_pack_fidelity.py` resolves 17 of them to the game's own file: 15 hulls SEST forks "
     "from vanilla that CREDITS credits to RE-power (3605013271), plus `wp_ss-n-14b` and `rfn_aor_pashin`. The other "
     "4 match the game's own file line for line: `damage.ini`, `knm_terne_shell.ini`, `rn_squid_shell.ini` and "
     "`usn_ssq-47.ini`. Then **33 files CREDITS does not measure are added**: Greene's 5 model and texture files and "
     "the other files outside unit folders (animations, `f-35a_mat.ini`, `systems/`, `language_*`, `ui/Default`), "
     "plus unit files between 50 % and 90 % alike (squadron files, the Block III Super Hornet, ammunition). "
     "550 - 21 + 33 = " + str(tot.get('verbatim', 0) + tot.get('close', 0)) + ".",
     "- CREDITS.txt credits RE-power (3605013271) and the Alizé mod (3628203171) for files that are really the "
     "game's. That credit costs nothing and can stay. Neither item needs a request.", "",
     "### Method (evidence)", "",
     "1. Every shipped file is mapped to the SEST pack that built it (`integration/*/SEST_*`, the inputs of `tools/consolidate_packs.py`).",
     "2. **Replenishment pack (452 files):** the upstream of each file comes from `tools/check_pack_fidelity.py`'s own "
     "`upstream_for()` (the builder's load-order resolution). That checker passes on this tree: "
     "'every byte difference is an intended insertion'. So each file is exactly its upstream plus SEST's supply block "
     "or reload lines. Its 8 generated `_variants` files have no upstream and count as SEST-original. Where the upstream "
     "is `mods-source/_vanilla/original`, the file is the game's.",
     "3. **Every other text file** is compared with each same-named file (and its `#!extend` target) in "
     "`mods-source/<id>/` and `mods-source/_retired/<id>/`, and with the game's file in `_vanilla/original`. "
     "Measure: the share of the shipped file's content lines (no comments, no bare section headers) found in the source. "
     "'Close' means 50 % or more, and at least 3 lines, are the author's. Where the game's file explains as many lines "
     "(90 % or more), the file counts as the game's.",
     "4. **Renamed copies** (for example RAAF airbases built from `airfield_us_large.ini`) come from the CREDITS.txt "
     "measurement (difflib ≥ 90 %), each re-checked against the game's file of that name.",
     "5. **Binary files:** `mods-source` is a text-only export, so binaries were matched by SHA-256 against "
     "`integration/raaf-f-35a-jatm/recovered/` (Greene). All other shipped binaries are SEST's: photos and pictures "
     "made from the gallery, ribbons, SEST DLLs, and the menu film.",
     "6. Two manual calls, both recorded in `FILE-LIST.csv`. `systems/weapons.ini` is a section merge that is mostly "
     "the game's own text (890 of 1,055 lines), so it counts as the game's. `systems/sest_weapon_costs.ini` (49 %) "
     "counts as a close adaptation of the Combat Cost Tracker, like its sister files (75 %), because it keeps the "
     "tracker's prices.",
     "7. Authors come from `data/mod-catalog.json`, `_info.ini`, `CREDITS.txt` and the items' own Credits/LICENSE files.", "",
     "## 2. Author groups", "",
     "Status key: **needs permission** = no licence found that allows copying or overriding the files; "
     "**licence already allows** = the author's own text allows it (cited); **no permission needed** = section 4.", "",
     "| # | Author group | Workshop items (files) | Verbatim / close / override | Example paths | Licence found | Evidence | Status | Draft |",
     "|---|---|---|---|---|---|---|---|---|"]
i = 0
def ev(g):
    pk = collections.Counter(F[r]["pack"] for r in GROUPS[g])
    s = "; ".join(f"{n} by {p}" for p, n in pk.most_common())
    return s + ("; fidelity-checked upstream" if "replenishment" in pk else "")
for g in st["order"] + []:
    i += 1
    rels = GROUPS[g]
    its = items_of(g)
    cls = collections.Counter(F[r]["cls"] for r in rels)
    ex = ", ".join(f"`{r}`" for r in sorted(rels)[:3])
    L.append(f"| {i} | {gname(g)} | " + "<br>".join(f"{title(w)} ({w}): {n}" for w, n in its.most_common())
             + f" | {cls.get('verbatim', 0)} / {cls.get('close', 0)} / {cls.get('override', 0)} | {ex} | "
             f"{licence(g)} | {ev(g)} | {STATUS[g]} | {draft_files.get(g, ('-',))[0]} |")
i += 1
L.append(f"| {i} | R.A.T.S. (Lukas Struckl, 'Ratte') | Sea Power Topographic Map (3826122523), R.A.T.S. Rigging (3843688859): 0 files | 0 / 0 / 0 (load-time adapter) | `beta-support/SEST-Beta-Features.zip` (payload/AnchorChain.dll, Topography-MIT-LICENSE.txt) | {META['rats']['licence']} | section 3.3 | needs permission | {draft_files['rats'][0]} |")
L += ["", f"Totals: {tot.get('verbatim', 0)} verbatim, {tot.get('close', 0)} close, {tot.get('override', 0)} override. "
      "Channels are in `TRACKER.csv`. Groups whose author name is not recorded in the repo are marked; the "
      "owner should confirm the name on the item page before sending.", "",
      "## 3. The named material", "",
      "### 3.1 Greene RAAF F-35A (3514484654, removed from the Workshop)", "",
      "MNO carries the aircraft itself (`integration/raaf-f-35a-jatm/README.md`). 16 files:", "",
      "| Class | Files |", "|---|---|",
      "| Verbatim, binary (from `integration/raaf-f-35a-jatm/recovered/`, SHA-256 in its `SHA256SUMS`) | `assets/models/vehicle/aircraft/f-35/f-35a.obj`, `.../textures/f-35a_tex.png`, `f-35a_nm.png`, `f-35a_spec.png`, `assets/textures/f-35/raaf_f-35a.png` |",
      "| Verbatim, text (= `mods-source/_retired/3514484654`) | `aircraft/raaf_f-35a_squadrons.ini`, `ammunition/raaf_f-35_gun_pod.ini`, `ammunition/usaf_aim-120c7.ini`, `animations/animations_raaf_f-35a.ini`, `assets/models/vehicle/aircraft/f-35/f-35a_mat.ini` |",
      "| Close | `aircraft/raaf_f-35a.ini` (91 %; AIM-260/AIM-424 loadouts), `ammunition/usaf_gbu-31_v1.ini`, `usaf_gbu-53.ini`, `usaf_jsm.ini`, `usaf_jsm_land.ini` (model references moved), `language_en/ammunition_names.ini` (3 of Greene's names in SEST's merged file) |",
      "", "Licence: none found. CREDITS.txt already names Greene as the source of the model and textures. This is "
      "the only place where MNO ships another author's model, so LICENSE.md section 3 ('does not redistribute "
      "third-party 3D models') and the CREDITS.txt opening line need this exception until Greene answers.", "",
      "### 3.2 RSG AIM-424 overrides (2 files)", "",
      "`ammunition_overwrite/fury_aim424_SEST.ini` (`#!extend ammunition/fury_aim424.ini`, Anduril FQ-44 Fury "
      "3804868806) and `ammunition_overwrite/yf23_aim424_internal_SEST.ini` (`#!extend "
      "ammunition/yf23_aim424_internal.ini`, YF-23 Black Widow II 3796349767), both from SEST Collection Fixes. "
      "They set SEST's AIM-424 guidance and model block (`integration/common/aim424.py`). 22 of their 77 lines "
      "coincide with RSG's file, all generic values such as camera distances, `GuidanceType=3` and the collider. "
      "No RSG text is copied. RSG's LICENSE.txt (in both items): patches may add content 'provided they do not copy, "
      "replace, override, or redistribute Original Project Material'. So these need written permission. The "
      "catalogue records the owner's 23 Oct 2026 call: the Fury override 'stays, and comes out if RSG asks'. "
      "No other shipped file overrides an RSG file. The cost files name RSG units in price lists, which is a "
      "reference only.", "",
      "### 3.3 Topographic Map 1.8.1 adapter", "",
      "- What ships: `beta-support/SEST-Beta-Features.zip` contains `payload/AnchorChain.dll` (SEST's Anchor Chain "
      "fork, MIT), `Topography-MIT-LICENSE.txt` (a copy of "
      "`integration/beta-feature-parity/third-party/SeaPowerTopo-LICENSE.txt`, MIT, Lukas Struckl) and "
      "`SOURCE-CHANGES.patch` (SEST source, including the adapter). **No Topographic Map or Rigging file is in the "
      "item.** The DLL comes from the author's Workshop item.",
      "- What the adapter does (`integration/beta-anchorchain/source/AssemblyAdapters.Topography.cs`): it accepts only "
      "`SeaPowerTopo.dll` with SHA-256 `4c3c0868f3cd420d…475c` (1.8.1). It checks the shape of "
      "`HeightReader..ctor` and of `Raster.SimHeight`, and changes one constant in `SimHeight`, the "
      "shallow-water threshold, from -48 to -50 m. It also checks the game's native terrain scaling. It is not "
      "purely in memory: `AssemblyPolicy.Prepare`/`WritePrivateImage` write the adapted DLL to "
      "`BepInEx\\config\\SEST-BetaAnchorChain\\beta-api-r16-261123\\<sha>\\<workshop folder>\\SeaPowerTopo.dll` "
      "on the player's PC and load it from there. The Workshop file stays unchanged.",
      "- Licence: 1.8.1 is dated 2026-11-22 (`mods-source/3826122523/CHANGELOG.md`). It therefore falls under the "
      "R.A.T.S. Source License 1.0, which forbids sharing 'the Work or a build of it, changed or unchanged' and "
      "using any part of it in another mod without written permission. A modified copy made on the player's own "
      "PC is arguably not distribution by SEST, but it is a changed build of the Work. The MIT notice MNO ships covers only "
      "the versions before 2026-11-18. HANDOFF.md and LICENSE.md treat Topography as MIT, which is out of date for 1.8.1.",
      "- Keel: the owner is in talks with the R.A.T.S. team (kanalratte) about moving onto R.A.T.S. Keel. The draft "
      "is worded to sit beside that conversation, and no Keel request is drafted.", "",
      "### 3.4 Owner-supplied photos (21)", "",
      "See `PHOTOS-SOURCE-SEARCH.md`. The rights holder of each photo is unknown, so this is a source search for the "
      "owner first and a permission request only where the source turns out to be copyrighted.", "",
      "## 4. No permission needed", "",
      f"### 4.1 Items only referenced by name ({len(st['ref_only'])} Workshop items)", "",
      "SEST-original files that name these items' units, or patch them with a few keys of SEST's own "
      "(`#!extend` overrides, cross-deck `AircraftSupported` lists, nation fixes, model-block stubs). None of the "
      "author's content is copied, so no permission is needed. Referring to a unit by its id is how every mod "
      "interoperates. RSG's two files are the exception (section 3.2), because RSG's licence names overriding.", "",
      "| Workshop item | Author (catalogue) | SEST files naming it | Reason |", "|---|---|---|---|"]
for w, c in sorted(st["ref_only"].items(), key=lambda kv: title(kv[0]).lower()):
    L.append(f"| {title(w)} ({w}) | {author(w) or 'not recorded'} | " + ", ".join(f"{n} in {p}" for p, n in c.items())
             + " | SEST-written patch, under 50 % of lines shared, or a reference only |")
L += ["", "Groups in section 2 also have SEST-original reference files (for example 131 cross-deck lists naming 24 items). "
      "Those files need nothing either.", "",
      f"### 4.2 The game's own files ({len(st['vanilla'])})", "",
      "Files derived from Sea Power's own data, not a mod's: 39 replenishment hulls whose upstream "
      "`check_pack_fidelity.py` resolves to `_vanilla/original` (clones and vanilla forks), and 19 others that match the "
      "game's file more closely than any mod's copy (`ammunition/damage.ini`, `systems/weapons.ini`, `ui/minimap.ini`, "
      "several gun rounds). They are not a mod author's, so they are outside this request. LICENSE.md section 5 covers "
      "the game.", "",
      "### 4.3 Pog Frog: licence already allows", "",
      "`aircraft/S-70B-2_Seahawk.ini` (99 % of S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles, 3403661005). Its "
      "`_info.ini` says: 'please feel free to iterate on this mod all I ask is that you credit those who worked on "
      "this before you'. CREDITS.txt credits it. The model is Jason Simpson's and MNO does not ship it. No request is "
      "needed. A courtesy note is optional.", "",
      "## 5. Uncertain or open", "",
      f"- Author names not recorded in the repo for {sum(1 for g in GROUPS if 'not recorded' in gname(g))} groups (marked 'name not recorded'). Two merges rest on "
      "evidence that is not conclusive. The Luzon Line and The Siam Shield are merged because the catalogue says "
      "'by the author of the Luzon Line'. The two Euromod Korea add-ons are merged because their descriptions are "
      "identical. Mitchell600's group includes the Modern RAN mod, which has two co-authors.",
      "- The 50 % threshold for 'close' is a judgment. The 26 close files that CREDITS.txt does not list at 90 % "
      "or more (mostly squadron files, loadout additions and `systems/` merges) are counted as the author's. Files "
      "below 50 % are counted as SEST's. The per-file share is in `FILE-LIST.csv`.",
      "- Binary files of other authors can be detected only for Greene, because the export has no binaries. "
      "The file types and the build scripts show no other carried binaries, but that is not a byte-level proof.",
      "- `language_*` files are SEST's merged name files, and a few of their lines are authors' unit names. Two are "
      "counted (`language_en/ammunition_names.ini` under Greene, `language_cn/loadout_names.ini` under misaka). "
      "The others fall under 50 %.",
      "- Not in the decision's list, so not drafted: SEST's other load-time adapters for author DLLs "
      "(Enhanced Decoy, Multi-Stage Missiles, J-36, Osprey, Z-21, Better Tac Map, Jiutian, Dynamic Campaign Mod; "
      "see `integration/beta-anchorchain/source/AssemblyAdapters.*.cs`) and the Pop-Out Windows and Rigging hash "
      "pins. The owner already decided to ship and credit the DCM adapter. The others may deserve the same question "
      "as Topographic Map.",
      "- HANDOFF.md says the licence is GPT's personal-play notice (`gpt/WORKSHOP-DRAFT.md`), while LICENSE.md says "
      "MIT plus CC BY-NC-ND. The drafts claim neither; they say only 'free, non-commercial'.", ""]
(OUT / "INVENTORY.md").write_text("\n".join(L), encoding="utf-8")
print("drafts:", len(draft_files), "max chars:", max(v[1] for v in draft_files.values()))
for g, (fn, n) in draft_files.items():
    print(f"  {fn} {n}")
