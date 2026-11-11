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
  deck      a placed ship embarks one of its aircraft (the block's own air
            group when it writes CustomAirGroup=True, else the winning
            variant's or the hull's), crediting that aircraft's unit,
            squadron and stores files as the builder does

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
    # each campaign's spec says where its browser copy is.
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


_TOKEN = re.compile(r"\s*(?:<Condition([1-9]\d*)>|(\()|(\))|(AND|OR|NOT)(?![\w>])|(\S+))")


def expression_problems(rel, tag, keys, blocks):
    """A trigger's ConditionsCompleted, held to the shapes stock writes.

    Stock writes AND, OR, AND NOT and brackets (Action in the Gulf of Sidra
    1986 line 629, `<Condition1> AND (<Condition2> OR <Condition3>)`). NOT
    comes only as `AND NOT <ConditionN>`, never leading, after OR or before
    a bracket, and AND and OR never share a bracket level unbracketed: how
    the game reads any other shape is not known, so this parser refuses it.
    Two stock lines fail the first check: 01 Red Sea Breakout 1988 line 273,
    `<Condition1> OR (<Condition2> AND <Condition>3)`, which loads and is
    malformed (nothing read the expression, so a typo there was silent), and
    04 Sunda Strait line 721, `<CONDITION2> AND NOT <CONDITION1>`, whose
    uppercase tokens this parser does not read: whether the game does is
    unconfirmed. Each <N> must be a numbered condition of the trigger, with
    no leading zero, and each numbered condition must be used; a
    TriggerCompleted condition names a [TriggerN] section of this mission.

    NOT on a UnitsInTheArea condition is the North Borneo shape (08 Defense
    of North Borneo, Trigger3 lines 1270-1286), and here it needs that
    mission's refresh loop, Trigger10 at lines 1334-1339: a trigger with a
    Time condition that can run (not Disabled=True, or enabled by another)
    and whose Action_ReactivateTriggers names this trigger and itself, so
    the area is tested again every 5 seconds. That is a deliberate SEST
    rule, stricter than stock: 05 Shadow of the Enterprise's Trigger6
    (lines 760-773) ships an unrefreshed `<Condition2> AND NOT <Condition1>`
    (Time=60 AND NOT an area) as a one-shot, which, since an area condition
    stays met once met, means "never in the area before minute one". SEST
    has no one-shot NOT-area form: a NOT on an area test takes the North
    Borneo refresh loop, and one that must start late is that loop shipped
    Disabled=True and enabled by a Time trigger at minute N (a refresh
    another trigger enables counts). A trigger without numbered conditions
    (the un-numbered Condition_Type= form) is not read here.
    """
    numbered, out = {}, []
    for key, value in keys.items():
        m = re.fullmatch(r"Condition_Condition(\d+)_Type", key)
        if m:
            if m.group(1).startswith("0"):
                out.append(f"{rel}: [{tag}] {key}: a condition number has no leading zero")
                continue
            numbered[int(m.group(1))] = value
    expr = keys.get("ConditionsCompleted")
    if expr is None:
        return out + ([f"{rel}: [{tag}] has numbered conditions and no ConditionsCompleted"]
                      if numbered else [])
    tokens, pos = [], 0
    while pos < len(expr):
        m = _TOKEN.match(expr, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        if m.group(1):
            tokens.append(("cond", int(m.group(1))))
        elif m.group(2) or m.group(3):
            tokens.append((m.group(2) or m.group(3), None))
        elif m.group(4):
            tokens.append((m.group(4), None))
        elif m.group(5):
            out.append(f"{rel}: [{tag}] ConditionsCompleted={expr}: {m.group(5)!r} is "
                       "not <ConditionN>, AND, OR, NOT or a bracket")
            return out
    negated, used, shape = set(), set(), []

    def term(i, neg=False):
        if i < len(tokens) and tokens[i][0] == "(":
            i = expression(i + 1)
            if i is None or i >= len(tokens) or tokens[i][0] != ")":
                return None
            return i + 1
        if i < len(tokens) and tokens[i][0] == "cond":
            used.add(tokens[i][1])
            if neg:
                negated.add(tokens[i][1])
            return i + 1
        if i < len(tokens) and tokens[i][0] == "NOT":
            shape.append("NOT is written only as 'AND NOT <ConditionN>', as stock writes it")
        return None

    def expression(i):
        i, ops = term(i), set()
        while i is not None and i < len(tokens) and tokens[i][0] in ("AND", "OR"):
            op, i, neg = tokens[i][0], i + 1, False
            ops.add(op)
            if i < len(tokens) and tokens[i][0] == "NOT":
                if op != "AND" or not (i + 1 < len(tokens) and tokens[i + 1][0] == "cond"):
                    shape.append("NOT is written only as 'AND NOT <ConditionN>', "
                                 "as stock writes it")
                    return None
                i, neg = i + 1, True
            i = term(i, neg)
        if len(ops) > 1:
            shape.append("AND and OR share a bracket level - stock brackets one of them")
        return i

    end = expression(0)
    if shape:
        out.append(f"{rel}: [{tag}] ConditionsCompleted={expr}: {shape[0]}")
        return out
    if end is None or end != len(tokens):
        out.append(f"{rel}: [{tag}] ConditionsCompleted={expr} does not parse: "
                   "an operator without a condition, or unbalanced brackets")
        return out
    for n in sorted(used - set(numbered)):
        out.append(f"{rel}: [{tag}] ConditionsCompleted uses <Condition{n}>, "
                   f"and the trigger has no Condition_Condition{n}_Type")
    for n in sorted(set(numbered) - used):
        out.append(f"{rel}: [{tag}] Condition{n} ({numbered[n]}) is never used "
                   "in ConditionsCompleted")
    for n, kind in sorted(numbered.items()):
        if kind == "TriggerCompleted":
            for ref in keys.get(f"Condition_Condition{n}_Triggers", "").split(","):
                if not is_trigger(ref, blocks):
                    out.append(f"{rel}: [{tag}] Condition{n} waits for {ref.strip()!r}, "
                               "which is not a trigger in this mission")
    for n in sorted(negated):
        if numbered.get(n) == "UnitsInTheArea" and not refreshed(tag, blocks):
            out.append(f"{rel}: [{tag}] NOT <Condition{n}> tests that no unit is in an "
                       "area, and no trigger refreshes this one - the North Borneo shape "
                       "is a Time trigger that can run and reactivates this one and "
                       "itself every 5 seconds")
    return out


def is_trigger(ref, blocks):
    """A reference to a [TriggerN] section this mission has."""
    ref = ref.strip()
    return bool(re.fullmatch(r"Trigger\d+", ref)) and ref in blocks


def _names(value):
    return [r.strip() for r in value.split(",")]


def refreshed(tag, blocks):
    """Does a refresh loop test trigger `tag` again: a trigger with a Time
    condition whose Action_ReactivateTriggers names `tag` and itself, and
    which runs - it is not Disabled=True, or a trigger enables it."""
    triggers = {t: k for t, k in blocks.items() if t.startswith("Trigger")}
    enabled = {r for k in triggers.values() for r in _names(k.get("Action_EnableTriggers", ""))}
    for t, k in triggers.items():
        again = _names(k.get("Action_ReactivateTriggers", ""))
        timed = any(re.fullmatch(r"Condition_Condition\d+_Type", key) and v == "Time"
                    for key, v in k.items()) or k.get("Condition_Type") == "Time"
        if tag in again and t in again and timed and (k.get("Disabled") != "True"
                                                      or t in enabled):
            return True
    return False


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
                    if ref and not is_trigger(ref, blocks):
                        problems.append(f"{rel}: [{tag}] {key} names {ref}, "
                                        "which is not a trigger in this mission")

    for tag, keys in blocks.items():
        if tag.startswith("Trigger"):
            problems += expression_problems(rel, tag, keys, blocks)

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

    # The same for a unit held back (enter=): Disabled=True on the unit and
    # nothing that switches it on (Action_SetEnabledStatus=True naming it, the
    # stock pattern) is a unit the mission places and never fields.
    switched_on = set()
    for tag, keys in blocks.items():
        if tag.startswith("Trigger") and keys.get("Action_SetEnabledStatus") == "True":
            switched_on |= {u.strip() for u in keys.get("Action_Units", "").split(",")
                            if u.strip()}
    for tag, keys in blocks.items():
        if (not tag.startswith("Trigger") and keys.get("Disabled") == "True"
                and tag not in switched_on):
            problems.append(f"{rel}: [{tag}] is placed Disabled=True and no "
                            "trigger switches it on, so it never takes part")
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


def open_twin(pack, slug, hold=()):
    """The campaign's Open Allocation twin differs from it only in what it sells.

    The twin (build_pack.open_allocation_ini) is a second entry in the
    campaign list that loads this campaign's missions and art by path and
    sells the whole roster at every open window - except a unit in `hold`
    (the spec's OPEN_HOLD), which it sells only where the base window's own
    allowlist does, under OPEN_NOTE_HELD. Read from the built bytes:
    the three files the game reads from the campaign's own folder are this
    campaign's - commander settings byte for byte, the roster with every line
    of this campaign's roster in it (the allied fleet is added after them) -
    and its campaign.ini is this one line for line
    except the file's own Base, the campaign's name and description, and in
    each window the allowlist (every roster entry, every priced pick) and the
    situation (the note first, then the base text unchanged). A twin that
    drifted - a gate, a reward, a MissionFile - would be a different campaign
    under the same missions, and nothing in game would say so.

    main() runs it only for a campaign that opts in (spec OPEN_ALLOCATION).
    None in the pack has since 21 Oct 2026; test_build_pack builds a twin
    into a temporary folder and holds it to this gate.
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
    # The allied sentence names what the twin adds to the base roster, never
    # the base's own units (20 Oct 2026: Sulu Line's twin called its Thai and
    # Australian partners an allied fleet).
    base_units = {uid for _section, uid, _line in base_rows}
    allied = bp.allied_line([dict(unit=u, picks=p) for u, p in picks.items()
                             if u not in base_units], commander)
    blurb = bp.OPEN_BLURB_HELD if hold else bp.OPEN_BLURB
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
        sold = next((set(e.split(",")[0] for e in b.partition("=")[2].split("|"))
                     for b in b_lines if b.startswith("TaskForceModeAllowedRosterUnits=")),
                    set(picks))
        offered = {u: p for u, p in picks.items() if u not in hold or u in sold}
        note = bp.OPEN_NOTE if len(offered) == len(picks) else bp.OPEN_NOTE_HELD
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
                # the blurb (the held one with an OPEN_HOLD), then the
                # allied-fleet sentence for what the twin adds to the base
                # roster (build_pack.allied_line; "" with none), then the
                # base description - exactly
                ok = w == f"Description={blurb}{allied}{value}"
            elif is_open and key == "TaskForceModeAllowedRosterUnits":
                listed = [e.split(",") for e in w.partition("=")[2].split("|")]
                got = {e[0]: e[1:] for e in listed}
                ok = (w.startswith(key + "=") and len(listed) == len(got)
                      and got == offered)
            elif is_open and key == "TaskForceModeBuilderSituation_en":
                ok = w == f"{key}={note} {value}"
            else:
                ok = w == b
            if not ok:
                out.append(f"{where}:{line_no}: {head} {key or b[:40]!r} is not the "
                           "base campaign's line with the Open Allocation change")
    if list(found.values()) != [1, 1, 1] or not windows:
        out.append(f"{where}: expected one Base, Name and Description and at least one "
                   f"open window, found {found} and {windows} window(s)")
    return out + art_resolves(pack, name)


def stray_campaigns(pack, specs):
    """Every folder under the pack's campaigns/ is a campaign or an opted-in twin.

    An Open Allocation twin is built only for a campaign that opts in to one
    (spec OPEN_ALLOCATION). None in the pack does since the owner retired the
    twins on 21 Oct 2026, and a folder under campaigns/ that is neither a
    campaign nor an opted-in twin is a campaign-list entry nothing builds or
    checks - a twin left behind by a stale pack, for one.
    """
    known = ([spec["SLUG"] for spec in specs]
             + [bp.open_slug(spec["SLUG"]) for spec in specs if spec.get("OPEN_ALLOCATION")])
    return [f"campaigns/{folder.name}: no campaign builds it"
            + (" - an Open Allocation twin, and its campaign does not "
               "opt in to one (OPEN_ALLOCATION)"
               if folder.name.endswith(bp.OPEN_SUFFIX) else "")
            for folder in sorted((pack / "campaigns").iterdir())
            if folder.name not in known]


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
    # An Open Allocation twin only for a campaign that opts in to one (spec
    # OPEN_ALLOCATION); none in the pack does since 21 Oct 2026, and
    # stray_campaigns() refuses a twin folder that nothing builds.
    twins = [bp.open_slug(spec["SLUG"]) for spec in specs if spec.get("OPEN_ALLOCATION")]
    for spec in specs:
        problems += art_resolves(pack, spec["SLUG"])
        problems += loadout_names(pack, spec["SLUG"], spec["DISPATCHES"])
        if spec.get("OPEN_ALLOCATION"):
            twin = bp.open_slug(spec["SLUG"])
            problems += open_twin(pack, spec["SLUG"], spec.get("OPEN_HOLD", ()))
            if (pack / "campaigns" / twin / "player_task_force_roster.ini").is_file():
                problems += loadout_names(pack, twin, spec["DISPATCHES"])
    problems += stray_campaigns(pack, specs)

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
            # A deck's aircraft fly from it whether or not the mission names
            # them: the builder has credited them since 20 Oct 2026
            # (deck_aircraft), and this check did not until a mod was reached
            # through a deck alone (The Royal Navy's Sea Lynx on the PN
            # FFG-150, 3 Nov 2026 export). The built block's own air group
            # wins when it writes CustomAirGroup=True.
            if keys.get("CustomAirGroup", "").casefold() == "true":
                embarked = [k for k, v in keys.items() if re.match(r"^\w+,\d+$", v)]
            else:
                embarked = bp.deck_aircraft(uid, kind_dir, path, keys.get("VariantReference"), {})
            for atype in embarked:
                for token, how, detail in bp.aircraft_credit(atype):
                    note(token, how, f"{uid} deck / {detail}")
            # Model folders the unit's own file loads from another mod's
            # assets/ tree - the same rule the builder credits by.
            for folder in sorted(set(bp.ASSET_FOLDER.findall(bp.read(path)))):
                for token in sorted(bp.asset_owners(folder)):
                    note(token, "asset", f"{uid} / {folder.rstrip('/')}")

    # The requisition roster is read from the BUILT file too: a unit the player
    # can buy is reached by the campaign, and a price naming a variant the hull
    # no longer offers is a purchase the game would refuse. One roster per
    # campaign, and one per opted-in twin.
    for slug in slugs + twins:
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
