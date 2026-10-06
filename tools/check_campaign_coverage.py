#!/usr/bin/env python3
"""Prove the Southern Watch campaign still reaches every enabled mod.

The builder computes coverage from its own roster, which is the right thing
while authoring and the wrong thing to trust afterwards: it checks what it
meant to place. This checker reads the BUILT mission files instead - the same
bytes the installer copies into the game - and re-derives coverage from them
against the current load order. If a mod update, an unsubscribe or a reordered
Mod Manager entry takes a mod out of the campaign's reach, this is what says
so, and it says so without the builder's data file being involved at all.

A mod counts as reached when a placed unit makes the game read one of its
files, resolved exactly the way Sea Power resolves them:

  unit      it wins <unit>.ini
  variant   it wins <unit>_variants.ini and the mission names that variant
  squadron  it wins <unit>_squadrons.ini and the mission names that squadron
  store     it wins an ammunition file the mission's chosen loadout hangs

Anything it cannot reach must carry a written reason in an EXCUSES table -
Southern Watch's in campaign_data.py, or any other campaign's own; the rule is
the pack's, so every campaign's excuses are read together. Along the way every Type=, LoadoutVariant=, SquadronReference= and
VariantReference= in the campaign is resolved, so a retired variant or a
renamed loadout fails here rather than spawning a default fit in mission nine.

    python3 tools/check_campaign_coverage.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "integration" / "campaign"
sys.path.insert(0, str(CAMPAIGN))
import build_pack as bp                      # noqa: E402


def missions():
    pack = CAMPAIGN / "SEST_Campaign"
    if not pack.is_dir():
        sys.exit("no built campaign - run python3 integration/campaign/build_pack.py")
    found = sorted(f for f in pack.rglob("*.ini")
                   if f.name not in ("_info.ini", "campaign.ini",
                                     "player_task_force_roster.ini",
                                     "enemy_theater_roster.ini",
                                     "commander_settings.ini")
                   and not f.parent.name.endswith("_briefing"))
    # A campaign mission ships twice - once for the campaign, once for the
    # mission browser - and the two copies must stay byte-identical, or the
    # campaign and the browser quietly diverge. The browser folder is the
    # campaign's own rule (Southern Reach files its two chapters apart), so
    # each campaign's spec says where its twin is.
    by_name = {}
    for spec in bp.campaign_specs():
        bp.set_campaign(spec)
        for m in spec["MISSIONS"]:
            if m["group"] != "dispatch":
                by_name[bp.mission_name(m) + ".ini"] = bp.browse_folder(m)
    for f in found:
        if "campaigns" not in f.parts:
            continue
        folder = by_name.get(f.name)
        if folder is None:
            sys.exit(f"{f.name}: in a campaign folder, but no campaign's data names it")
        twin = pack / "missions" / folder / f.name
        if not twin.exists():
            sys.exit(f"{f.name}: no browser copy under missions/{folder}")
        if twin.read_bytes() != f.read_bytes():
            sys.exit(f"{f.name}: the campaign copy and the browser copy differ")
    return found


def blocks(text):
    """[Section] -> {key: value}.

    The header pattern has to tolerate a trailing comment: the builder writes
    `[Trigger10]  #Report unhides Airlift`, and a parser that insisted the
    line END with `]` skipped every trigger in the campaign - which made
    trigger_integrity() below pass vacuously for as long as it existed.
    """
    out, current = {}, None
    for line in text.splitlines():
        s = line.strip()
        head = re.match(r"^\[([^\]]+)\]", s)
        if head:
            current = head.group(1)
            out[current] = {}
        elif current and "=" in s:
            key, _, value = s.partition("=")
            out[current][key.strip()] = value.strip()
    return out


def trigger_integrity(path, text, blocks):
    """Every reference a trigger makes must resolve inside its own mission.

    Three ways a mission can be quietly broken that no other gate sees: a
    condition naming a unit section that does not exist, an action completing
    or failing an objective that was never declared, and a message or intel
    action naming a key with no [Language_en] entry. All three load fine and
    do nothing.
    """
    problems = []
    rel = path.relative_to(ROOT)
    sections = set(blocks)
    objectives = set()
    in_objectives = False
    language = set()
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            in_objectives = line == "[Taskforce1_Objectives]"
            continue
        if in_objectives and "=" in line and not line.startswith("#"):
            objectives.add(line.split("=", 1)[0].strip())
    for key in blocks.get("Language_en", {}):
        language.add(key)

    for tag, keys in blocks.items():
        if not tag.startswith("Trigger"):
            continue
        for key, value in keys.items():
            if key.endswith("_Units") or key == "Action_Units":
                for unit in value.split(","):
                    unit = unit.strip()
                    if unit and unit not in sections:
                        problems.append(f"{rel}: [{tag}] {key} names {unit}, "
                                        "which is not a section in this mission")
            elif key.startswith("Action_Objectives"):
                for oid in value.split(","):
                    oid = oid.strip()
                    if oid and oid not in objectives:
                        problems.append(f"{rel}: [{tag}] {key}={oid} is not a "
                                        "declared objective")
            elif key.endswith("_Message") or key.endswith("_Intel"):
                if value not in language:
                    problems.append(f"{rel}: [{tag}] {key}={value} has no "
                                    "[Language_en] entry")
            elif key in ("Action_EnableTriggers", "Action_DisableTriggers",
                         "Action_ReactivateTriggers"):
                for ref in value.split(","):
                    ref = ref.strip()
                    if ref and ref not in blocks:
                        problems.append(f"{rel}: [{tag}] {key} names {ref}, "
                                        "which is not a trigger in this mission")

    # A scripted attack names its target inside the shooter's Waypoints
    # (`x,alt,z/AttackAtWaypoint,ammo,Taskforce1Vessel2,2`): a target that is
    # not a section here is a salvo at nothing, and the escort the mission is
    # about never has anything to defend against.
    for tag, keys in blocks.items():
        for wp in keys.get("Waypoints", "").split("|"):
            for order in wp.split("/")[1:]:
                bits = order.split(",")
                if bits[0] == "AttackAtWaypoint" and len(bits) > 2:
                    target = bits[2].strip()
                    if target and ":" not in target and target not in sections:
                        problems.append(f"{rel}: [{tag}] AttackAtWaypoint names "
                                        f"{target}, which is not a section in "
                                        "this mission")

    # A trigger that ships Disabled=True and is never enabled is dead weight
    # the game loads and never runs - the hidden half of a discovered
    # objective, silently never discovered.
    enabled = set()
    for tag, keys in blocks.items():
        if not tag.startswith("Trigger"):
            continue
        for key in ("Action_EnableTriggers", "Action_ReactivateTriggers"):
            for ref in keys.get(key, "").split(","):
                if ref.strip():
                    enabled.add(ref.strip())
    for tag, keys in blocks.items():
        if (tag.startswith("Trigger") and keys.get("Disabled") == "True"
                and tag not in enabled):
            problems.append(f"{rel}: [{tag}] ships Disabled=True and no "
                            "trigger enables it, so it can never fire")
    return problems


COUNT_SECTION = {
    "NumberOfTaskforce1Vessels": "Taskforce1Vessel",
    "NumberOfTaskforce2Vessels": "Taskforce2Vessel",
    "NumberOfNeutralVessels": "NeutralVessel",
    "NumberOfTaskforce1Submarines": "Taskforce1Submarine",
    "NumberOfTaskforce2Submarines": "Taskforce2Submarine",
    "NumberOfNeutralSubmarines": "NeutralSubmarine",
    "NumberOfTaskforce1Aircraft": "Taskforce1Aircraft",
    "NumberOfTaskforce2Aircraft": "Taskforce2Aircraft",
    "NumberOfNeutralAircraft": "NeutralAircraft",
    "NumberOfTaskforce1Helicopters": "Taskforce1Helicopter",
    "NumberOfTaskforce2Helicopters": "Taskforce2Helicopter",
    "NumberOfNeutralHelicopters": "NeutralHelicopter",
    "NumberOfTaskforce1LandUnits": "Taskforce1LandUnit",
    "NumberOfTaskforce2LandUnits": "Taskforce2LandUnit",
    "NumberOfNeutralLandUnits": "NeutralLandUnit",
    "NumberOfNeutralBiologics": "NeutralBiologic",
}


def declared_counts(rel, parsed):
    """[Mission] says how many of each family there are. Prove it.

    The header counts are what the loader reads to decide how many sections to
    walk. A count one too high reaches for a section that is not there; one too
    low silently drops the last unit of that family - and a dropped unit is a
    mission that is quietly easier than the one that was designed, which is the
    kind of failure nothing else here would catch.
    """
    out = []
    for key, prefix in COUNT_SECTION.items():
        if key not in parsed.get("Mission", {}):
            continue
        want = int(parsed["Mission"][key])
        have = sum(1 for tag in parsed if re.fullmatch(prefix + r"\d+", tag))
        if want != have:
            out.append(f"{rel}: {key}={want}, but {have} [{prefix}N] section(s)")
    return out


def unit_families(rel, parsed):
    """A helicopter sits in a Helicopter section, and only a helicopter does.

    Every helicopter placement in the stock and workshop missions is a
    [TaskforceNHelicopterM] (or [NeutralHelicopterM]) section, and stock
    conditions test Condition_UnitType=Helicopter apart from Aircraft. The
    builder used to file every helicopter as Aircraft - O1's Seahawk was the
    first flown from such a section and did nothing - so the family is proved
    from the built file against the unit's own UnitType, not trusted.
    VTOL is fixed-wing and belongs in Aircraft, as stock's Yak-38s do.
    """
    out = []
    for tag, keys in parsed.items():
        m = re.fullmatch(r"(Taskforce[12]|Neutral)(Aircraft|Helicopter)\d+", tag)
        if not m or not keys.get("Type"):
            continue
        rotary = bp.unit_type(keys["Type"]) == "Helicopter"
        if rotary and m.group(2) == "Aircraft":
            out.append(f"{rel}: [{tag}] Type={keys['Type']} is a helicopter in an "
                       "Aircraft section - stock files it as Helicopter")
        elif not rotary and m.group(2) == "Helicopter":
            out.append(f"{rel}: [{tag}] Type={keys['Type']} is not a helicopter "
                       "but sits in a Helicopter section")
    return out


_GAME_NATIONS = None


def nations(rel, parsed):
    """Every placed unit flies a flag the game has.

    A unit's nation comes from its own Nation= key in the mission, else the
    squadron it flies from, else its hull variant. The game matches that
    string against its keys (language_en/nations.ini and the [NationFlags]
    table, the collection's additions included - NewZealand, South_Korea: no
    spaces), case-insensitively, and shows no flag for anything else. "New Zealand" with a space is how the RNZAF bases and
    the P-8 mod's No. 5 Squadron shipped, and why they showed none.
    A biologic has no flag to show and is skipped, and "Unknown" (what the
    whale mod declares) is taken as a deliberate no-flag.
    """
    global _GAME_NATIONS
    if _GAME_NATIONS is None:
        # The game's own keys, plus the ones the collection adds: a mod's or a
        # SEST pack's language_en/nations.ini merges key by key, and a key in
        # the flag table ([NationFlags] of the Settings_UI_General.ini that
        # loads, SEST Collection Fixes' copy) shows a flag whether or not it
        # is named - Russia= is there from a mod, and Meridian= from SEST.
        files = [ROOT / "mods-source" / "_vanilla" / "original" / "language_en" / "nations.ini"]
        files += sorted((ROOT / "mods-source").glob("*/language_en/nations.ini"))
        files += sorted(p for p in (ROOT / "integration").glob("*/SEST_*/language_en/nations.ini")
                        if "dist" not in p.parts)
        _GAME_NATIONS = set()
        for f in files:
            for l in f.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                if "=" in l and not l.lstrip().startswith(("#", ";", "[")):
                    _GAME_NATIONS.add(l.split("=", 1)[0].strip().lower())
        table = (ROOT / "integration" / "collection-fixes" / "SEST_Collection_Fixes"
                 / "ui" / "Default" / "Settings_UI_General.ini")
        if table.is_file():
            m = re.search(r"^\[NationFlags\][^\n]*\n(.*?)(?=^\[|\Z)",
                          table.read_text(encoding="utf-8-sig", errors="replace"), re.M | re.S)
            for l in (m.group(1).splitlines() if m else []):
                if "=" in l and not l.lstrip().startswith(("#", ";")):
                    _GAME_NATIONS.add(l.split("=", 1)[0].strip().lower())
    out = []
    for tag, keys in parsed.items():
        m = re.match(r"(Taskforce\d|Neutral)(Vessel|Submarine|Aircraft|Helicopter|LandUnit)\d+$", tag)
        uid = keys.get("Type")
        if not m or not uid:
            continue
        kind_dir, path = bp.unit_file(uid)
        if path is None or bp.unit_type(uid) == "Biologic":
            continue
        nation, source = keys.get("Nation"), "its mission section"
        for suffix, ref in (("_squadrons", keys.get("SquadronReference")),
                            ("_variants", keys.get("VariantReference") or "Default")):
            if nation or not ref:
                continue
            hit = bp.index().get(f"{kind_dir}/{uid}{suffix}.ini".lower())
            if not hit:
                continue
            table = blocks(Path(hit[1]).read_text(encoding="utf-8-sig", errors="replace"))
            value = table.get(ref, {}).get("Nation") or table.get("Default", {}).get("Nation")
            if value:
                nation, source = value, f"{ref} of {uid}{suffix}.ini ({hit[0]})"
        if nation:
            nation = re.split(r"\s*(?://|#|;)", nation, 1)[0].strip()
        # "Unknown" is a deliberate no-flag (the humpback whale declares it)
        if nation and nation.lower() not in _GAME_NATIONS | {"unknown"}:
            out.append(f"{rel}: [{tag}] {uid} flies Nation={nation!r} from {source} - "
                       "the game has no such key and shows no flag")
    return out


def art_resolves(pack, slug):
    """Every path campaign.ini points at, in every language it names one in.

    Localised keys do not fall back - pacific-strike repeats the SAME English
    PNG under TileImagePath_en, _ru and _de rather than relying on one - so the
    campaign spells its art nine times, and nine chances to point at a file
    that is not there. A missing PNG is silent in game: the tile is simply
    blank, and nothing in the log says why.
    """
    out = []
    camp = pack / "campaigns" / slug / "campaign.ini"
    parsed = blocks(camp.read_text(encoding="utf-8"))
    referenced = set()
    for tag, keys in parsed.items():
        for key, value in keys.items():
            if key == "BackgroundImage" or re.fullmatch(
                    r"(MissionImage|TileImagePath|FilePath|MissionFile)(_[a-z]{2})?", key):
                referenced.add(value)
                if not (pack / value).is_file():
                    out.append(f"campaign.ini [{tag}]: {key}={value} - no such file")
            elif re.fullmatch(r"AssetsPath_[a-z]{2}", key):
                if not (pack / value).is_dir():
                    out.append(f"campaign.ini [{tag}]: {key}={value} - not a directory")
        # A story page reaches its images through the XAML's Assets[] binding,
        # resolved against the entry's AssetsPath - the stock campaign's
        # newspaper pages name their photographs that way and nowhere else.
        # TileImagePath is the 128x128 tile behind the entry on the map, so it
        # no longer doubles as the only reference to the story image.
        assets_dir = keys.get("AssetsPath_en")
        page = keys.get("FilePath_en")
        if assets_dir and page and (pack / page).is_file():
            xaml = (pack / page).read_text(encoding="utf-8")
            for name in re.findall(r"Assets\[([^\]]+)\]", xaml):
                rel = f"{assets_dir}/{name}.png"
                referenced.add(rel)
                if not (pack / rel).is_file():
                    out.append(f"{page}: Assets[{name}] - {rel} is not shipped")
    # And the other way: art nobody points at is weight in a download that a
    # subscriber pays for and cannot see.
    art = pack / "campaigns" / slug / "art"
    for f in sorted(art.glob("*.png")):
        rel = f.relative_to(pack).as_posix()
        if rel not in referenced:
            out.append(f"{rel}: shipped, but nothing references it")
    return out


def open_twin(pack, slug):
    """The campaign's Open Allocation twin differs from it only in what it sells.

    The twin (build_pack.open_allocation_ini) is a second entry in the
    campaign list that loads this campaign's missions and art by path and
    sells the whole roster at every open window. Read from the built bytes:
    the three files the game reads from the campaign's own folder are this
    campaign's - commander settings byte for byte, the roster with every line
    of this campaign's roster in it (the allied fleet is added after them) -
    and its campaign.ini is this one line for line
    except the file's own Base, the campaign's name and description, and in
    each window the allowlist (every roster entry, every priced pick) and the
    situation (the note first, then the base text unchanged). A twin that
    drifted - a gate, a reward, a MissionFile - would be a different campaign
    under the same missions, and nothing in game would say so.
    """
    name = bp.open_slug(slug)
    base, twin = pack / "campaigns" / slug, pack / "campaigns" / name
    if not (twin / "campaign.ini").is_file():
        return [f"campaigns/{name}: no Open Allocation twin for {slug}"]
    out = []
    if (not (twin / "commander_settings.ini").is_file()
            or (twin / "commander_settings.ini").read_bytes()
            != (base / "commander_settings.ini").read_bytes()):
        out.append(f"campaigns/{name}/commander_settings.ini: missing, or not the base "
                   "campaign's file")
    for fn in ("campaign_rules_en.xml", "REQUIRED-MODS.txt", "player_task_force_roster.ini",
               "enemy_theater_roster.ini"):
        if not (twin / fn).is_file():
            out.append(f"campaigns/{name}: no {fn}")
    if out:
        return out
    def priced(path):
        """[(section, uid, line)] - every priced line, parsed by section (a
        uid may carry an apostrophe: fr_fdi_amiral_ronarc'h)."""
        rows, section = [], ""
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
            elif line and not line.startswith(";") and "=" in line and section != "LoadoutPrices":
                rows.append((section, line.partition("=")[0], line))
        return rows
    base_rows = priced(base / "player_task_force_roster.ini")
    twin_rows = priced(twin / "player_task_force_roster.ini")
    twin_where = {uid: (section, line) for section, uid, line in twin_rows}
    if len(twin_where) != len(twin_rows):
        out.append(f"campaigns/{name}/player_task_force_roster.ini: a unit is priced twice")
    lost = sorted(uid for section, uid, line in base_rows
                  if twin_where.get(uid) != (section, line))
    if lost:
        out.append(f"campaigns/{name}/player_task_force_roster.ini: the base roster's "
                   f"{', '.join(lost)} is not in it as priced, in its section")
    picks = {uid: line.partition("=")[2].split("|")[0].split(",")
             for _section, uid, line in twin_rows}
    commander = (twin / "commander_settings.ini").read_text(encoding="utf-8")
    allied = bp.allied_line([dict(unit=u, picks=p) for u, p in picks.items()], commander)
    # Section by section, with every expected change REQUIRED rather than
    # merely allowed: a twin still naming the base's Base, a Name that did
    # not change, or an open window without its note is as wrong as a gate
    # that moved (review of 814e85a2).
    where = f"campaigns/{name}/campaign.ini"
    b_secs = re.split(r"\n(?=\[)", (base / "campaign.ini").read_text(encoding="utf-8"))
    t_secs = re.split(r"\n(?=\[)", (twin / "campaign.ini").read_text(encoding="utf-8"))
    if len(b_secs) != len(t_secs):
        return out + [f"{where}: {len(t_secs)} sections against the base's {len(b_secs)}"]
    line_no, windows, found = 0, 0, {"Base": 0, "Name": 0, "Description": 0}
    for b_sec, t_sec in zip(b_secs, t_secs):
        b_lines, t_lines = b_sec.split("\n"), t_sec.split("\n")
        head = b_lines[0].split("]")[0] + "]"
        if len(b_lines) != len(t_lines) or t_lines[0] != b_lines[0]:
            out.append(f"{where}:{line_no + 1}: section {head} is not the base's")
            line_no += len(b_lines)
            continue
        is_open = "TaskForceModeEnableTaskForceBuilder=True" in b_lines
        windows += is_open
        for b, w in zip(b_lines, t_lines):
            line_no += 1
            key, _, value = b.partition("=")
            if head == "[File]" and key == "Base":
                found["Base"] += 1
                ok = w == f"Base=campaigns/{name}/campaign.ini"
            elif head == "[Language_en]" and key == "Name":
                found["Name"] += 1
                ok = (w != b and " - Open Allocation" in w
                      and w.replace(" - Open Allocation", "", 1) == b)
            elif head == "[Language_en]" and key == "Description":
                found["Description"] += 1
                # the blurb, then the allied-fleet sentence its own roster
                # calls for (build_pack.allied_line; "" with none), then the
                # base description - exactly
                ok = w == f"Description={bp.OPEN_BLURB}{allied}{value}"
            elif is_open and key == "TaskForceModeAllowedRosterUnits":
                listed = [e.split(",") for e in w.partition("=")[2].split("|")]
                got = {e[0]: e[1:] for e in listed}
                ok = (w.startswith(key + "=") and len(listed) == len(got)
                      and got == picks)
            elif is_open and key == "TaskForceModeBuilderSituation_en":
                ok = w == f"{key}={bp.OPEN_NOTE} {value}"
            else:
                ok = w == b
            if not ok:
                out.append(f"{where}:{line_no}: {head} {key or b[:40]!r} is not the "
                           "base campaign's line with the Open Allocation change")
    if list(found.values()) != [1, 1, 1] or not windows:
        out.append(f"{where}: expected one Base, Name and Description and at least one "
                   f"open window, found {found} and {windows} window(s)")
    return out + art_resolves(pack, name)


def loadout_names(pack, slug, dispatches):
    """Every loadout a player-side aircraft is offered has a display name.

    The picker shows `MISSING TEXT - [LoadoutNames]<key>` for any
    `AvailableLoadouts` entry no language file names, and it did for the
    MH-60R's Anti-shipLate - a fit Southern Watch sells and slots. Names are
    read from every enabled mod, the base game and the built pack, since
    language_*/ files merge key by key. Comments are stripped both ways the
    data writes them (`//` and ` #`); the F-35A's line carries a ` #` the
    game reads as a comment.
    """
    names = set()
    tokens = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt")
              .read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")]
    sources = [ROOT / "mods-source" / t for t in tokens]
    sources += [ROOT / "mods-source" / "_vanilla" / "original",
                ROOT / "integration" / "dist" / "SEST_Integration"]
    for d in sources:
        f = d / "language_en" / "loadout_names.ini"
        if f.is_file():
            names |= set(blocks(f.read_text(encoding="utf-8-sig", errors="replace"))
                         .get("LoadoutNames", {}))
    camp = pack / "campaigns" / slug
    player = set()
    for f in list((camp / "missions").glob("*.ini")) + list(
            (pack / "missions" / dispatches).glob("*.ini")):
        for tag, keys in blocks(f.read_text(encoding="utf-8")).items():
            if re.match(r"Taskforce1(Aircraft|Helicopter)\d+$", tag) and keys.get("Type"):
                player.add(keys["Type"])
    roster = (camp / "player_task_force_roster.ini").read_text(encoding="utf-8")
    player |= set(re.findall(r"^([\w.-]+)=", roster, re.M))
    out = []
    for uid in sorted(player):
        if bp.unit_type(uid) not in ("Aircraft", "Helicopter", "VTOL"):
            continue
        line = bp.unit_value(uid, "AvailableLoadouts") or ""
        line = re.split(r"\s#", line, 1)[0]
        for key in (k.strip() for k in line.split(",")):
            if key and key not in names:
                out.append(f"{uid}: loadout {key!r} has no [LoadoutNames] entry "
                           f"anywhere - the picker shows MISSING TEXT")
    return out


def main():
    files = missions()
    credits, problems, units = {}, [], 0
    pack = CAMPAIGN / "SEST_Campaign"
    specs = bp.campaign_specs()
    slugs = [spec["SLUG"] for spec in specs]
    for spec in specs:
        problems += art_resolves(pack, spec["SLUG"])
        problems += loadout_names(pack, spec["SLUG"], spec["DISPATCHES"])
        problems += open_twin(pack, spec["SLUG"])
        problems += loadout_names(pack, bp.open_slug(spec["SLUG"]), spec["DISPATCHES"])

    for f in files:
        rel = f.relative_to(ROOT)
        text = f.read_text(encoding="utf-8")
        parsed = blocks(text)
        problems += trigger_integrity(f, text, parsed)
        problems += declared_counts(rel, parsed)
        problems += unit_families(rel, parsed)
        problems += nations(rel, parsed)
        for tag, keys in parsed.items():
            uid = keys.get("Type")
            if not uid or not re.match(r"^(Taskforce\d+|Neutral)", tag):
                continue
            units += 1
            kind_dir, path = bp.unit_file(uid)
            if path is None:
                problems.append(f"{rel}: [{tag}] Type={uid} - no enabled mod defines it")
                continue

            def note(token, how, detail):
                if token and token not in credits:
                    credits[token] = (how, detail, f.stem)

            note(bp.owner(f"{kind_dir}/{uid}.ini"), "unit", uid)

            want = keys.get("VariantReference")
            if want:
                pool = bp.variants(uid, kind_dir)
                if want not in pool:
                    problems.append(
                        f"{rel}: [{tag}] {uid} names {want}, which its winning "
                        f"variants file no longer offers ({', '.join(pool) or 'none'})")
                else:
                    note(bp.owner(f"{kind_dir}/{uid}_variants.ini"), "variant", uid)

            want = keys.get("SquadronReference")
            if want:
                pool = bp.squadrons(uid)
                if want not in pool:
                    problems.append(
                        f"{rel}: [{tag}] {uid} names {want}, which its winning "
                        f"squadrons file no longer offers ({', '.join(pool) or 'none'})")
                else:
                    note(bp.owner(f"aircraft/{uid}_squadrons.ini"), "squadron", uid)

            fit = keys.get("LoadoutVariant")
            offered = bp.loadouts(path)
            if fit and offered and fit not in offered:
                problems.append(
                    f"{rel}: [{tag}] {uid} LoadoutVariant={fit} is not offered by "
                    f"the winning file ({', '.join(offered)})")
                continue
            if not fit and offered and "Default" not in offered:
                problems.append(
                    f"{rel}: [{tag}] {uid} names no LoadoutVariant and its winning "
                    f"file offers no Default ({', '.join(offered)})")
                continue
            for store in bp.stores(uid, kind_dir, path, fit):
                note(bp.owner(f"ammunition/{store}.ini"), "store", f"{uid} / {store}")
            # Model folders the unit's own file loads from another mod's
            # assets/ tree - the same rule the builder credits by.
            for folder in sorted(set(bp.ASSET_FOLDER.findall(bp.read(path)))):
                for token in sorted(bp.asset_owners(folder)):
                    note(token, "asset", f"{uid} / {folder.rstrip('/')}")

    # The requisition roster is read from the BUILT file too: a unit the player
    # can buy is reached by the campaign, and a price naming a variant the hull
    # no longer offers is a purchase the game would refuse. One roster per
    # campaign.
    for slug in slugs + [bp.open_slug(s) for s in slugs]:
        roster = pack / "campaigns" / slug / "player_task_force_roster.ini"
        if not roster.exists():
            problems.append(f"no player_task_force_roster.ini under campaigns/{slug}")
            continue
        section = ""
        for line in roster.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(";") or not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
                continue
            if "=" not in line or section == "LoadoutPrices":
                continue
            uid, _, spec = line.partition("=")
            picks = spec.split("|")[0].split(",")
            kind_dir, path = bp.unit_file(uid)
            if path is None:
                problems.append(f"roster: no enabled mod defines {uid}")
                continue
            pool = (bp.squadrons(uid) if section.endswith(("Aircraft", "Helicopters"))
                    else bp.variants(uid, kind_dir))
            for pick in picks:
                if pick not in pool:
                    problems.append(
                        f"roster: {uid} is priced with {pick}, which its winning "
                        f"file no longer offers ({', '.join(pool) or 'none'})")
            token = bp.owner(f"{kind_dir}/{uid}.ini")
            if token and token not in credits:
                credits[token] = ("roster", uid, "requisition roster")

    rows, missing = bp.coverage(credits, bp.pack_excuses(specs))
    print(f"{len(files)} mission file(s) - the campaign's own missions ship "
          f"twice and were checked in both places - {units} placed unit "
          f"reference(s), {len(credits)} mod(s) reached directly")

    if missing:
        print("\nOUT OF REACH - place it or give it a reason in EXCUSES:")
        for what, mid, token, title in missing:
            print(f"   {what:<5} {mid:<34} {token:<18} {title}")
    if problems:
        print(f"\n{len(problems)} dangling reference(s):")
        for p in problems:
            print(f"   {p}")
    if missing or problems:
        sys.exit(f"{len(missing)} uncovered, {len(problems)} dangling")

    print(f"coverage: all {len(rows)} enabled mods and SEST packs accounted for")


if __name__ == "__main__":
    main()
