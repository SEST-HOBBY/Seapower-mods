#!/usr/bin/env python3
"""Stage the two Steam Workshop items: the pack, and the campaign that plays it.

    python3 tools/build_workshop.py            # stage both items + regenerate docs
    python3 tools/build_workshop.py --check    # docs only; exit 1 if they drifted

WHY TWO ITEMS AND NOT ONE

  Definitive Modernised Seapower   integration/dist/SEST_Integration, as is.
                                   A patch pack: every file is a .ini that edits
                                   another author's unit, so it only works
                                   with those mods subscribed and ranked below it.
  Southern Watch                   The scored SEST missions, as one campaign.
                                   It changes no unit, so it does not care
                                   about load order - it only needs its units.

Folded into one item, every pack fix would push a campaign update and every
mission tweak would re-download the pack, and a player who wants the balance
changes but not the missions (or the reverse) could not have one without the
other. Separately, the campaign lists the pack as a Required Item and Steam
asks the player to subscribe to both.

The third piece, the Workshop *collection* holding the full mod list, is not
something a file can stage - it is built on the Steam site. docs/workshop/
carries the list to build it from.

WHAT IS GENERATED WHERE

  integration/workshop/staging/<folder>/   the upload folders (gitignored: the
                                           pack is a copy of dist, and a copy
                                           in git is two places to go stale)
  docs/workshop/<item>.md                  Steam description (BBCode), Required
                                           Items and the upload checklist - committed,
                                           so a diff shows when the requirement
                                           list moved

Required Items are derived, never typed: the pack's from the files it
overrides and the stores and units it references (the same rules as
check_dependencies.py), the campaign's from every Type= and air group its
missions place. A hand-kept list would go stale the first time a loadout
moved to a different mod.
"""
import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import winning_file  # noqa: E402

MODS = ROOT / "mods-source"
DIST = ROOT / "integration" / "dist" / "SEST_Integration"
MISSIONS = ROOT / "integration" / "missions"
STAGING = ROOT / "integration" / "workshop" / "staging"
DOCS = ROOT / "docs" / "workshop"
UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units", "biologic")

PACK_FOLDER = "SEST_Integration"          # unchanged: it is the load-order token
PACK_TITLE = "Definitive Modernised Seapower - SEST Integration Pack"
CAMPAIGN_FOLDER = "SEST_Southern_Watch"
# In-game campaign name. "Southern Watch" alone would sit in the mission list
# beside "Black Widow - Southern Watch" (the YF-23 mod, 3796349767, which this
# collection also subscribes to), and a player could not tell them apart.
CAMPAIGN_NAME = "SEST Southern Watch"
CAMPAIGN_TITLE = "Southern Watch - A Definitive Modernised Seapower Campaign"

# Campaign running order: open with identification and single-ship problems,
# build to carrier air defence and deep strike, close on the convoy run. Only
# missions preflight resolves cleanly belong here - "NF3 Boomer Hunt" and
# "NF3 Carrier Duel" name DDG loadouts U.S. Navy 2027 has since renamed, and
# stay out until their parent mission is refreshed.
CAMPAIGN = [
    ("SEST Banda - Sanctioned Cargo",   "Sanctioned Cargo"),
    ("SEST Banda - Warramunga's Shot",  "Warramunga's Shot"),
    ("SEST Banda - Narco Transit",      "Narco Transit"),
    ("SEST Banda - Mogami's Corner",    "Mogami's Corner"),
    ("SEST Banda - Triton's Picture",   "Triton's Picture"),
    ("SEST Banda - Viper Zero",         "Viper Zero"),
    ("SEST Banda - Rafale, Timor Gap",  "Rafale, Timor Gap"),
    ("SEST Banda - Foxhound Sweep",     "Foxhound Sweep"),
    ("SEST Banda - Black Widow Debut",  "Black Widow Debut"),
    ("SEST Banda - Fujian's Shadow",    "Fujian's Shadow"),
    ("SEST Banda - The Biak Regiment",  "The Biak Regiment"),
    ("SEST Banda - Tigers over Papua",  "Tigers over Papua"),
    ("SEST ANL Convoy - Coral Sea",     "Coral Sea Convoy"),
]


# One player-facing line per source pack, taken from each builder's docstring.
# A pack added to local_packs without a line here fails the build rather than
# shipping a description that silently omits it.
PACK_BLURBS = {
    "SEST ADF Persistent ISR": "the RAAF MQ-4C Triton maritime surveillance drone",
    "SEST Allied Fixes": "P-8 Poseidon anti-ship loadout",
    "SEST B-52 ARRW": "AGM-183A ARRW on every in-service B-52",
    "SEST Collection Fixes": "surgical fixes for mod-vs-mod clashes found in a full collection audit",
    "SEST F-15EX Revamp": "F-15EX Eagle II loadouts rebuilt, JATMs seated on the right pylons",
    "SEST F-16CM JATM": "AIM-260 and AIM-424 fits for the USAF F-16C",
    "SEST F-35C JATM": "AIM-260 loadout options for the F-35C",
    "SEST Growler NGJ + MALICE": "EA-18G Next Generation Jammer and MALICE compatibility",
    "SEST JMSDF Mogami": "the Mogami-class frigate with its real fit",
    "SEST RAAF Bases": "five Australian airbases populated with real RAAF squadrons",
    "SEST RAAF F-35A JATM": "AIM-260 loadout options for the RAAF F-35A",
    "SEST RAAF Wedgetail": "real RAAF squadrons for the E-7A Wedgetail",
    "SEST RAN Fleet": "Royal Australian Navy ships: Hobart, Canberra, Anzac, Supply and more",
    "SEST Rafale F5": "JATM, MALICE and LRASM fits for late Rafales",
    "SEST Raptor Squadrons": "real squadrons for the F-22",
    "SEST TacMap Colors": "readable waypoint lines on the tactical map",
}


def catalog():
    mods = json.loads((ROOT / "data" / "mod-catalog.json")
                      .read_text(encoding="utf-8"))["mods"]
    return {m["workshop_id"]: m for m in mods if m.get("workshop_id")}


def owner(path):
    """The workshop id a winning file comes from; None for vanilla or SEST."""
    rel = path.relative_to(ROOT).parts
    if rel[0] == "mods-source" and rel[1][0].isdigit():
        return rel[1]
    return None


def owners_index():
    idx = collections.defaultdict(set)
    for d in MODS.iterdir():
        if d.is_dir() and d.name[0].isdigit():
            for f in d.rglob("*.ini"):
                idx[f.relative_to(d).as_posix().lower()].add(d.name)
    return idx


def pack_requirements():
    """Workshop ids the pack overrides or hangs stores/units from."""
    idx, need = owners_index(), collections.Counter()
    for f in DIST.rglob("*.ini"):
        rel = f.relative_to(DIST).as_posix()
        if f.parent.name not in UNIT_DIRS + ("ammunition",):
            continue
        for t in idx.get(rel.lower(), ()):
            need[t] += 1
        text = f.read_text(encoding="utf-8", errors="replace")
        stores = {s.split("|")[0] for s in
                  re.findall(r"^Station\d+=([A-Za-z]\S*)", text, re.M)}
        stores |= set(re.findall(r"^Ammunition\d*=(\S+)", text, re.M))
        refs = [f"ammunition/{s}.ini" for s in stores]
        for uid in set(re.findall(r"^([A-Za-z0-9_.\-]+)=Squadron\d+,\d+", text, re.M)):
            refs += [f"{k}/{uid}.ini" for k in UNIT_DIRS]
        for r in refs:
            w = winning_file(r)
            if w and owner(w):
                need[owner(w)] += 1
    return need


def mission_requirements(path):
    """Workshop ids a mission's units and air groups come from; dangling ids."""
    need, missing = collections.Counter(), []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        m = (re.match(r"^Type=(.+?)\s*$", line)
             or re.match(r"^([a-z0-9_.\-]+)=Squadron\d+,\d+", line))
        if not m:
            continue
        uid = m.group(1)
        w = next((w for k in UNIT_DIRS if (w := winning_file(f"{k}/{uid}.ini"))), None)
        if w is None:
            missing.append(uid)
        elif owner(w):
            need[owner(w)] += 1
        elif "integration" in w.parts:
            need[PACK_FOLDER] += 1
    return need, missing


def info_ini(name, description, version):
    return (f"[Language_en]\nName={name}\nDescription={description}\n\n"
            f"[Compatibility]\nApproximateVersion={version}\n")


def game_version():
    m = re.search(r"^ApproximateVersion=(.+)$",
                  (DIST / "_info.ini").read_text(encoding="utf-8"), re.M)
    return m.group(1).strip()


def author(m):
    """Catalog author, or '' where the catalog does not really know it."""
    a = (m.get("author") or "").strip()
    return "" if a.lower().startswith("unknown") else a


def ordered(need, cat):
    """The pack first (it is what the player must rank), then by title."""
    return sorted(need, key=lambda t: (t != PACK_FOLDER,
                                       cat.get(t, {}).get("title", t).lower()))


def req_table(need, cat):
    rows = ["| Workshop item | Author | Link |", "|---|---|---|"]
    for t in ordered(need, cat):
        if t == PACK_FOLDER:
            rows.append(f"| {PACK_TITLE} | SEST | *(this collection's pack item - "
                        "add once it is published)* |")
            continue
        m = cat.get(t, {})
        rows.append(f"| {m.get('title', t)} | {author(m) or '?'} | "
                    f"https://steamcommunity.com/sharedfiles/filedetails/?id={t} |")
    return "\n".join(rows)


def bb_list(need, cat):
    out = []
    for t in ordered(need, cat):
        if t == PACK_FOLDER:
            out.append(f"[*]{PACK_TITLE}")
        else:
            m = cat.get(t, {})
            out.append(f"[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id={t}]"
                       f"{m.get('title', t)}[/url]"
                       + (f" by {author(m)}" if author(m) else ""))
    return "[list]\n" + "\n".join(out) + "\n[/list]"


def pack_contents():
    """What the pack changes, one line per source pack, from dist's _info.ini."""
    m = re.search(r"Consolidated from: (.+?)\. Built by",
                  (DIST / "_info.ini").read_text(encoding="utf-8"))
    return [s.strip() for s in m.group(1).split(",")]


def mission_blurb(path, least=60, limit=260):
    """The mission's own opening, cut at a sentence boundary."""
    m = re.search(r"^Description=(.+)$", path.read_text(encoding="utf-8"), re.M)
    out = ""
    for sentence in re.findall(r"[^.]+\.", m.group(1) if m else ""):
        if len(out) >= least and len(out) + len(sentence) > limit:
            break
        out += sentence
    return out.strip()


CHECKLIST = """\
## Upload checklist

1. `python tools/build_workshop.py` on the gaming PC (after `build_all.py`).
2. Copy `integration/workshop/staging/{folder}/` into
   `Sea Power_Data/StreamingAssets/` - the same place `install-sest-packs.ps1`
   puts local packs.{pack_note}
3. Add a `preview.png` (Steam wants a square image under 1 MB) - the staging
   folder does not ship one.
4. Publish with the game's own Workshop upload flow. Title and description
   below; tags: {tags}.
5. On the item page, *Add/Remove Required Items*: add everything in the table.
6. Visibility: start **Unlisted** or **Friends only**, subscribe from a second
   profile or a clean mod list, play one mission, then go **Public**.
"""


def write_doc(path, text, check, drift):
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            drift.append(path.relative_to(ROOT).as_posix())
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="do not stage; fail if docs/workshop is stale")
    args = ap.parse_args()

    if not DIST.exists():
        sys.exit("integration/dist/SEST_Integration missing - run tools/build_all.py first")
    cat, version, drift = catalog(), game_version(), []

    # --- item 1: the pack --------------------------------------------------
    pack_need = pack_requirements()
    pack_desc = ("Balance, loadout and integration fixes for a large modern "
                 "Sea Power mod list, as one pack. Must sit at the TOP of the "
                 "Mod Manager list. Needs its Required Items subscribed.")
    unknown = [c for c in pack_contents() if c not in PACK_BLURBS]
    if unknown:
        sys.exit("add a PACK_BLURBS line for: " + ", ".join(unknown))
    contents = "\n".join(f"[*][b]{c.replace('SEST ', '', 1)}[/b] - {PACK_BLURBS[c]}"
                         for c in pack_contents())
    pack_bb = f"""[h1]{PACK_TITLE}[/h1]

One pack that makes a big modern mod list play together: weapons seated on the
pylons they belong on, missiles that fly like the real rounds, fleets and air
bases fitted out for the 2020s, and fixes for the clashes that appear when
140-odd mods share one game.

[h2]What it changes[/h2]
[list]
{contents}
[/list]

[h2]Load order - read this[/h2]
This pack edits other mods' unit files. It only works when it sits [b]above[/b]
every mod it patches:
[olist]
[*]Subscribe to this item and every Required Item below.
[*]Launch Sea Power, open the Mod Manager, enable everything.
[*]Move [b]{PACK_TITLE}[/b] to the very top. If anything outranks it, the fixes for that mod silently do nothing.
[/olist]

[h2]Required items[/h2]
Steam will offer to subscribe to these. The pack contains no models or
textures of its own - every unit it touches is drawn from these mods.
{bb_list(pack_need, cat)}

[h2]Credits[/h2]
All models, textures and the original unit files belong to the authors of the
mods listed above - this pack only edits their configuration. Please rate and
support their work. If you are one of those authors and want your mod left out,
comment below and it will be removed from the next update.

[h2]Campaign[/h2]
[b]{CAMPAIGN_TITLE}[/b] is built on this pack: thirteen short, scored missions
across the Banda, Timor, Arafura and Coral Seas.
"""
    pack_md = (f"# Workshop item: {PACK_TITLE}\n\n"
               "Generated by `tools/build_workshop.py` - do not edit by hand.\n\n"
               f"- Upload folder: `integration/workshop/staging/{PACK_FOLDER}/`\n"
               f"- In-game name: {PACK_TITLE}\n"
               f"- Game version: {version}\n\n"
               + CHECKLIST.format(
                   folder=PACK_FOLDER, tags="Modern, Units, Weapons",
                   pack_note="\n   Remove the local copy first "
                   "(`install-sest-packs.ps1 -Uninstall`) or the game lists two.")
               + f"\n## Required items ({len(pack_need)})\n\n"
               + req_table(pack_need, cat)
               + "\n\n## Steam description (paste as-is)\n\n```\n" + pack_bb + "```\n")
    write_doc(DOCS / "definitive-modernised-seapower.md", pack_md, args.check, drift)

    # --- item 2: the campaign ----------------------------------------------
    camp_need, missing = collections.Counter(), []
    lines = []
    for i, (src, title) in enumerate(CAMPAIGN, 1):
        path = MISSIONS / f"{src}.ini"
        if not path.exists():
            sys.exit(f"campaign mission missing: {path}")
        need, miss = mission_requirements(path)
        camp_need.update(need)
        missing += [f"{src}: {u}" for u in miss]
        lines.append((i, title, path))
    if missing:
        sys.exit("campaign units no mod defines:\n  " + "\n  ".join(missing))
    camp_need[PACK_FOLDER] += 1     # the campaign is balanced against the pack

    missions_bb = "\n".join(
        f"[*][b]{title}[/b] - {mission_blurb(p)}"
        for _, title, p in lines)
    camp_bb = f"""[h1]{CAMPAIGN_TITLE}[/h1]

September 2026. A red lodgement in Papua and a sanctions war across the
archipelago have turned Australia's northern approaches into a front line.
Thirteen short missions, each one problem with a way to win and a way to
lose, sized for about forty minutes.

[h2]Missions[/h2]
[olist]
{missions_bb}
[/olist]

[h2]How to play[/h2]
[olist]
[*]Subscribe to this item and to every Required Item (Steam will offer).
[*]Put [b]{PACK_TITLE}[/b] at the top of the Mod Manager list.
[*]Missions appear under [b]{CAMPAIGN_NAME}[/b].
[/olist]

[h2]Required items[/h2]
{bb_list(camp_need, cat)}

Scenario is fictional. Units belong to their mod authors - see the pack's page
for full credits.
"""
    camp_md = (f"# Workshop item: {CAMPAIGN_TITLE}\n\n"
               "Generated by `tools/build_workshop.py` - do not edit by hand.\n\n"
               f"- Upload folder: `integration/workshop/staging/{CAMPAIGN_FOLDER}/`\n"
               f"- In-game campaign: {CAMPAIGN_NAME}\n"
               f"- Missions: {len(lines)}\n\n"
               + CHECKLIST.format(folder=CAMPAIGN_FOLDER, tags="Missions, Modern",
                                  pack_note="")
               + "\nPublish the pack first: its Workshop id is a Required Item here.\n"
               + f"\n## Required items ({len(camp_need)})\n\n"
               + req_table(camp_need, cat)
               + "\n\n## Steam description (paste as-is)\n\n```\n" + camp_bb + "```\n")
    write_doc(DOCS / "southern-watch.md", camp_md, args.check, drift)

    # --- the collection: everything the load order enables ------------------
    tokens = [t.strip() for t in (ROOT / "data" / "load-order.tokens.txt")
              .read_text(encoding="utf-8").splitlines()
              if t.strip() and not t.startswith("#") and t.strip()[0].isdigit()]
    required = set(pack_need) | set(camp_need)
    rows = ["| # | Workshop item | Author | Required by an item | Link |",
            "|---|---|---|---|---|"]
    for i, t in enumerate(tokens, 1):
        m = cat.get(t, {})
        rows.append(f"| {i} | {m.get('title', t)} | {author(m) or '?'} | "
                    f"{'yes' if t in required else ''} | "
                    f"https://steamcommunity.com/sharedfiles/filedetails/?id={t} |")
    col_md = ("# Workshop collection: Definitive Modernised Seapower\n\n"
              "Generated by `tools/build_workshop.py` - do not edit by hand.\n\n"
              "A Steam collection is a list of links, not a copy of anyone's "
              "work, so it can hold the whole mod list. Create it on the "
              "Workshop (*Create Collection*), add the two SEST items first, "
              "then the rows below. Order in a collection does not set the "
              "in-game load order - the pack's page tells players to move it "
              "to the top.\n\n"
              f"{len(tokens)} mods from `data/load-order.tokens.txt`; "
              f"{len(required & set(tokens))} are Required Items of a SEST item, "
              "the rest make up the wider modernised game.\n\n"
              + "\n".join(rows) + "\n")
    write_doc(DOCS / "collection.md", col_md, args.check, drift)

    if args.check:
        if drift:
            sys.exit("stale, re-run tools/build_workshop.py:\n  " + "\n  ".join(drift))
        print("docs/workshop is current")
        return

    # --- staging -----------------------------------------------------------
    if STAGING.exists():
        shutil.rmtree(STAGING)
    pack_out = STAGING / PACK_FOLDER
    shutil.copytree(DIST, pack_out)
    (pack_out / "_info.ini").write_bytes(
        info_ini(PACK_TITLE, pack_desc, version).encode("utf-8"))

    camp_out = STAGING / CAMPAIGN_FOLDER
    folder = camp_out / "missions" / CAMPAIGN_NAME
    folder.mkdir(parents=True)
    (camp_out / "_info.ini").write_bytes(info_ini(
        CAMPAIGN_TITLE,
        f"{len(lines)} scored missions across Australia's northern approaches, "
        f"2026. Requires {PACK_TITLE}.", version).encode("utf-8"))
    (folder / "_info.ini").write_bytes(
        (f"[Language_en]\nName={CAMPAIGN_NAME}\nDescription=Thirteen short "
         "missions across the Banda, Timor, Arafura and Coral Seas. September "
         "2026; fictional conflict.\n").encode("utf-8"))
    for i, title, path in lines:
        text = path.read_text(encoding="utf-8")
        # The campaign folder already says "SEST Southern Watch"; the number
        # sorts the list into the intended running order.
        text = re.sub(r"^Name=.*$", lambda _: f"Name={i:02d} {title}", text,
                      count=1, flags=re.M)
        (folder / f"{i:02d} {title}.ini").write_bytes(text.encode("utf-8"))
        # The briefing folder is named for its mission, so it follows the rename.
        brief = path.with_name(f"{path.stem}_briefing")
        if not brief.is_dir():
            sys.exit(f"no briefing map for {path.stem}: "
                     "run integration/missions/build_briefing_maps.py")
        shutil.copytree(brief, folder / f"{i:02d} {title}_briefing")

    print(f"staged {PACK_FOLDER}: {sum(1 for _ in pack_out.rglob('*') if _.is_file())} "
          f"files, {len(pack_need)} required items")
    print(f"staged {CAMPAIGN_FOLDER}: {len(lines)} missions, "
          f"{len(camp_need)} required items")
    print("descriptions + checklists: docs/workshop/")


if __name__ == "__main__":
    main()
