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

Anything it cannot reach must carry a written reason in the builder's EXCUSES
table. Along the way every Type=, LoadoutVariant=, SquadronReference= and
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
from campaign_data import EXCUSES            # noqa: E402


def missions():
    pack = CAMPAIGN / "SEST_Campaign"
    if not pack.is_dir():
        sys.exit("no built campaign - run python3 integration/campaign/build_pack.py")
    found = sorted(f for f in pack.rglob("*.ini")
                   if f.name not in ("_info.ini", "campaign.ini",
                                     "player_task_force_roster.ini",
                                     "commander_settings.ini")
                   and not f.parent.name.endswith("_briefing"))
    # A campaign mission ships twice - once for the campaign, once for the
    # mission browser - and the two copies must stay byte-identical, or the
    # campaign and the browser quietly diverge.
    for f in found:
        if f.parent.parent.name != "campaigns" and "campaigns" not in f.parts:
            continue
        twin = pack / "missions" / "SEST Southern Watch" / f.name
        if twin.exists() and twin.read_bytes() != f.read_bytes():
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


def main():
    files = missions()
    credits, problems, units = {}, [], 0

    for f in files:
        rel = f.relative_to(ROOT)
        text = f.read_text(encoding="utf-8")
        parsed = blocks(text)
        problems += trigger_integrity(f, text, parsed)
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

    # The requisition roster is read from the BUILT file too: a unit the player
    # can buy is reached by the campaign, and a price naming a variant the hull
    # no longer offers is a purchase the game would refuse.
    roster = (CAMPAIGN / "SEST_Campaign" / "campaigns" / "sest-southern-watch"
              / "player_task_force_roster.ini")
    if not roster.exists():
        problems.append("no player_task_force_roster.ini in the built campaign")
    else:
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

    rows, missing = bp.coverage(credits, EXCUSES)
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
