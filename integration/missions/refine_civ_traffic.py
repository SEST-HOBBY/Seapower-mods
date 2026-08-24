#!/usr/bin/env python3
"""Refine a mission's civilian traffic in place.

Piggy-backs on the player's own edited mission. For mission <M> it reads
(first found)
  1. mods-source/_vanilla/user/missions/user_missions/<M>.ini
     (the copy exported from the game, carrying the player's hand edits)
  2. integration/missions/<M>.ini  (repo copy)
and writes integration/missions/<M>.ini. Pass --repo-only when the repo
copy IS the authoritative hand-edited file and must not be replaced by a
stale game export.

It ONLY touches, inside [NeutralVesselN] / [NeutralAircraftN] sections:
  - Type=            (re-types generic freighters into a realistic large-
                      commodity mix: VLCC + product tankers, capesize bulkers,
                      container ships, a car carrier; armed ran_ms_* coastal
                      traders become unarmed civilian coasters)
  - VariantReference= (spreads real liveries across each hull's variant pool)
  - SquadronReference=(spreads real airline liveries across the airliners)
  - NameOverride=     (names the two Darwin-trade tankers after the LNG runs)
Waypoints, positions, headings, telegraphs, groups and everything the player
placed stay byte-for-byte untouched.

Variant pools and squadron lists are parsed from the actual mod files under
mods-source/ — nothing is hardcoded that can drift.

Usage (repo root):
    python3 integration/missions/refine_civ_traffic.py
    python3 integration/missions/refine_civ_traffic.py \
        --mission "NORTHERN FRONT III" --repo-only --rename-to "NORTHERN FRONT III"
"""
import argparse
import functools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = Path(__file__).resolve().parent
MODS = ROOT / "mods-source"
ACTIVE_MISSION_FILE = ROOT / "data" / "active-mission.txt"


def active_mission():
    """The mission the tooling works on when none is named.

    Read from data/active-mission.txt so the working mission is declared once
    instead of being duplicated as a default in every tool, where the copies
    drift and a tool silently edits the wrong scenario.
    """
    try:
        for line in ACTIVE_MISSION_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    except OSError:
        pass
    return "NORTHERN FRONT III FINAL"


DEFAULT_MISSION = active_mission()

# Lane-merchant mix, cycled over the open-water merchants in section order.
# Darwin's real trades: LNG/condensate out of Ichthys and Bayu-Undan (VLCC and
# product-tanker hulls stand in - no LNG carrier exists in the mod set), Weipa
# bauxite and Gove alumina bulkers, and the Torres Strait container route.
LANE_MIX = [
    "civ_ms_ritina",            # Super Tanker (VLCC) - LNG trade stand-in
    "civ_ms_bulk",              # capesize bulker (Weipa bauxite)
    "civ_ms_mairangi_bay",      # container
    "civ_ms_sealift_pacific",   # medium product tanker
    "civ_ms_ritina",            # second tanker - LNG trade stand-in
    "civ_ms_c7s68",             # Lancer-class container
    "civ_ms_bulk",              # capesize bulker (Gove alumina)
    "civ_ms_car_carrier_a",     # car carrier
    "civ_ms_encounter",         # container
    "civ_ms_sealift_pacific",   # product tanker
    "civ_ms_bulk",              # capesize bulker
    "civ_ms_act_1",             # container
]
# civ_ms_ritina is a 253,000t crude VLCC (no LNG carrier exists in the mod
# set), so these are motor-tanker names rather than "LNG ..." ones.
TANKER_NAMES = ["MT Ichthys Venture", "MT Bayu Frontier"]

# The Auxilliary Merchant Pack's ran_ms_* hulls are ARMED auxiliary merchant
# cruisers - wrong for neutral civilian traffic. Swap to unarmed coasters.
COASTAL_MIX = ["civ_ms_andizhan", "civ_ms_freighter_d", "civ_ms_freighter_b"]

# Airline liveries per airliner type (squadron -> airline, from the livery
# texture names in each type's _squadrons.ini). Indo-Pacific carriers first.
SQUADRON_POOLS = {
    "civ_a330": ["Squadron61",  # Qantas
                 "Squadron38",  # Garuda
                 "Squadron17",  # Cathay Pacific
                 "Squadron35",  # Fiji Airways
                 "Squadron74",  # Virgin
                 "Squadron34"], # EVA Air
    "civ_a320": ["Squadron6",   # Asiana
                 "Squadron27",  # Garuda
                 "Squadron65",  # Virgin Australia
                 "Squadron21",  # Thai
                 "Squadron59"], # Air India
    "civ_a380": ["Squadron7",   # Qantas
                 "Squadron9",   # Singapore Airlines
                 "Squadron4",   # China Southern
                 "Squadron10"], # Thai
    "civ_dc-10": ["Squadron9",  # All Asian Airways (vanilla fictional)
                  "Squadron8"], # Siam Airways
}
# NOTE: no civil freighter type is usable here. civ_il-76t/td (Beriev mod)
# declare Nation=Soviet on every squadron and civ_il-18's cargo livery is
# Nation=Mali - either would spawn as foreign-flagged traffic that the player
# would have to identify in an Australian scenario, so airliner LIVERY variety
# carries the visual variety instead of a type swap.

# A player can group neutral vessels with a labelled formation, e.g.
#   Neutral_Formation1=NeutralVessel1,NeutralVessel2|Bulk Carrier|Loose|1.5
# Retyping a member out of the type its label names would contradict the
# player's own intent, so a labelled member is dressed to MATCH the label;
# a label we cannot map leaves the member's hull exactly as the player set it.
# Ordered MOST specific first - the first match wins, so a broad token like
# "tanker" must never be tested before "medium tanker".
FORMATION_HULLS = [
    (("medium tanker", "product tanker", "coastal tanker"), "civ_ms_sealift_pacific"),
    (("bulk", "ore carrier", "bauxite", "alumina"), "civ_ms_bulk"),
    (("container", "boxship", "feeder"), "civ_ms_mairangi_bay"),
    (("car carrier", "roro", "ro-ro", "vehicle carrier"), "civ_ms_car_carrier_a"),
    (("lng", "vlcc", "crude", "supertanker", "tanker"), "civ_ms_ritina"),
]

# Our own signature, written into an allowed key (NameOverride). Its presence
# means the file was dressed before: hulls already drawn from our output mix
# are then left alone rather than reshuffled, so re-runs are idempotent.
# Nothing is appended to the file itself - a stray marker line would land
# inside whichever section happens to be last.


def load_order():
    """Mod tokens highest-priority first, from the canonical Mod Manager order.

    Sea Power resolves a duplicated file path in favour of the mod listed
    HIGHER in the Mod Manager, so a variant pool must be read from the
    winning provider - not from vanilla, which every mod outranks.
    """
    f = ROOT / "data" / "load-order.tokens.txt"
    if not f.exists():
        return []
    return [l.strip() for l in f.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


_ORDER = None


@functools.lru_cache(maxsize=None)
def _ci_index(base):
    """Lowercased relative path -> real path, for one mod directory."""
    b = Path(base)
    if not b.is_dir():
        return {}
    return {q.relative_to(b).as_posix().lower(): q
            for q in b.rglob("*") if q.is_file()}


def _resolve(base, relpath):
    """<base>/<relpath> as the GAME sees it.

    Sea Power runs on Windows, where NTFS is case-insensitive: a mod shipping
    ammunition/Shahed_136_white.ini and another shipping shahed_136_white.ini
    are fighting over ONE file, and only the higher one loads. Checking with a
    plain exists() on Linux misses that entirely and reports two mods as
    conflict-free when in game one is overwriting the other.
    """
    f = base / relpath
    if f.exists():
        return f
    return _ci_index(str(base)).get(relpath.lower())


def winning_file(relpath):
    """The copy of <relpath> the game actually loads, or None."""
    global _ORDER
    if _ORDER is None:
        _ORDER = load_order()
    for token in _ORDER:
        # SEST packs live in the repo, not in mods-source, but they occupy
        # real positions in the Mod Manager order and win files there.
        if token.startswith("SEST_"):
            for pack in (ROOT / "integration").glob(f"*/{token}"):
                f = _resolve(pack, relpath)
                if f:
                    return f
            continue
        f = _resolve(MODS / token, relpath)
        if f:
            return f
    # Mods not listed in the canonical order still outrank vanilla.
    for d in sorted(p for p in MODS.iterdir() if p.is_dir() and p.name[0].isdigit()):
        f = _resolve(d, relpath)
        if f:
            return f
    return _resolve(MODS / "_vanilla" / "original", relpath)


def find_unit_file(kind, type_id):
    """Locate the winning <type_id>.ini for its <kind>/ dir."""
    return winning_file(f"{kind}/{type_id}.ini")


def variant_pool(type_id):
    """Usable [VariantN] section names for a vessel type (skips [-VariantN])."""
    f = find_unit_file("vessels", type_id)
    if f is None:
        sys.exit(f"vessel type not found in mods-source: {type_id}")
    vf = winning_file(f"vessels/{type_id}_variants.ini")
    if vf is None:
        return ["Default"]
    body = vf.read_text(encoding="utf-8", errors="replace")
    names = re.findall(r"^\[(Variant\d+)\]", body, re.M)
    # dedupe, keep order (some vanilla files carry duplicate sections)
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    # Files disagree with themselves: vanilla civ_ms_sealift_pacific declares
    # NumberOfVariants=27 but ships 37 sections, while Merchants Expanded
    # declares 37 and ships 36. Stay inside BOTH bounds so a pick is valid
    # however the engine builds its pool.
    declared = re.search(r"^NumberOfVariants=(\d+)", body, re.M)
    if declared:
        out = out[:min(len(out), int(declared.group(1)))]
    return out or ["Default"]


def squadron_exists(type_id, squadron):
    f = find_unit_file("aircraft", type_id)
    if f is None:
        sys.exit(f"aircraft type not found in mods-source: {type_id}")
    sf = winning_file(f"aircraft/{type_id}_squadrons.ini")
    if sf is None:
        return squadron == "Default"
    return re.search(rf"^\[{squadron}\]", sf.read_text(encoding="utf-8", errors="replace"), re.M) is not None


def formation_labels(text):
    """Map 'NeutralVesselN' -> the label of the player formation it belongs to.

    Line form: Neutral_Formation1=NeutralVessel1,NeutralVessel2|Label|Shape|1.5
    """
    out = {}
    for line in re.findall(r"^Neutral_Formation\d+=(.+)$", text, re.M):
        fields = line.split("|")
        label = fields[1].strip() if len(fields) > 1 else ""
        for member in fields[0].split(","):
            member = member.strip()
            if member:
                out[member] = label
    return out


def hull_for_label(label):
    """Hull id a formation label names, or None when it names nothing we map."""
    low = label.lower()
    for keys, hull in FORMATION_HULLS:
        if any(k in low for k in keys):
            return hull
    return None


def set_key(body, key, value):
    """Set key=value inside a section body: replace if present, else insert
    after the Type= line."""
    if re.search(rf"^{key}=", body, re.M):
        return re.sub(rf"^{key}=.*$", lambda _: f"{key}={value}", body, count=1, flags=re.M)
    return re.sub(r"^(Type=.*)$", lambda m: f"{m.group(1)}\n{key}={value}",
                  body, count=1, flags=re.M)


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mission", default=DEFAULT_MISSION,
                    help="mission name without .ini (default: %(default)s)")
    ap.add_argument("--repo-only", action="store_true",
                    help="treat integration/missions/<mission>.ini as authoritative "
                         "and ignore any game export of it")
    ap.add_argument("--rename-to", default=None,
                    help="rewrite every [Language_*] Name= entry to this title")
    return ap.parse_args()


def main():
    args = parse_args()
    out = MISSIONS / f"{args.mission}.ini"
    export = MODS / "_vanilla" / "user" / "missions" / "user_missions" / f"{args.mission}.ini"
    candidates = [out] if args.repo_only else [export, out]
    src = next((p for p in candidates if p.exists()), None)
    if src is None:
        sys.exit(f"no {args.mission}.ini found in {[str(c) for c in candidates]}")
    # The game-exported copy has CRLF endings; normalize so the regex edits
    # and the git history stay clean (the game reads LF fine). Try UTF-8
    # strictly first; a player-edited export may be cp1252 — fall back rather
    # than silently mangling bytes.
    raw = src.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    text = text.replace("\r\n", "\n")
    # "Has this file been dressed before?" Two independent signals, because
    # the mission editor strips NameOverride from neutral units when it saves:
    #   1. our own tanker names survive
    #   2. every neutral merchant hull is already one WE would have chosen
    #      (a raw mission always carries hulls outside the mix - ran_ms_*
    #      armed auxiliaries, civ_ms_super_p, civ_ms_c8, civ_ms_roro_b ...)
    # Either is enough. Without the second, an editor round-trip would look
    # raw and the whole LANE_MIX cycle would reshuffle the player's hulls.
    ours = set(LANE_MIX) | set(COASTAL_MIX)
    merchants = [m.group(1) for m in re.finditer(r"^Type=(\S+)", text, re.M)
                 if m.group(1).startswith(("civ_ms_", "anl_ms_", "ran_ms_"))]
    already_refined = (any(n in text for n in TANKER_NAMES)
                       or (len(merchants) >= 4 and all(t in ours for t in merchants)))

    # Split into (header, body) chunks, preserving everything verbatim.
    parts = re.split(r"(^\[[^\]]+\]\s*$)", text, flags=re.M)
    # parts = [pre, header1, body1, header2, body2, ...]

    lane_i = coast_i = 0
    tanker_names = list(TANKER_NAMES)
    labels = formation_labels(text)
    air_seen = {}
    changes = []
    pool_cache = {}

    for i in range(1, len(parts) - 1, 2):
        header, body = parts[i], parts[i + 1]
        m_v = re.match(r"\[NeutralVessel\d+\]", header)
        m_a = re.match(r"\[NeutralAircraft\d+\]", header)
        if not (m_v or m_a):
            continue
        tm = re.search(r"^Type=(\S+)", body, re.M)
        if not tm:
            continue
        old_type = tm.group(1)

        if m_v:
            if old_type.startswith("bio_"):
                continue
            if already_refined and old_type in set(LANE_MIX) | set(COASTAL_MIX):
                continue                                  # dressed on a prior run
            label = labels.get(header.strip("[]"))
            civilian_merchant = old_type.startswith(("civ_ms_", "anl_ms_", "ran_ms_"))
            if label is not None and civilian_merchant:
                # Player grouped this hull in a labelled formation: match the
                # label, or leave their choice alone when it names no hull.
                new_type = hull_for_label(label) or old_type
            elif label is not None:
                # Labelled but NOT a civilian merchant (warship, rig, fishing
                # boat the player grouped deliberately): leave it entirely
                # alone - it is not ours to dress.
                continue
            elif old_type.startswith("civ_fv_"):
                new_type = old_type                       # fishing: keep hull
            elif old_type.startswith(("ran_ms_", "ran_fv_")):
                new_type = COASTAL_MIX[coast_i % len(COASTAL_MIX)]
                coast_i += 1
            elif old_type.startswith(("civ_ms_", "anl_ms_")):
                new_type = LANE_MIX[lane_i % len(LANE_MIX)]
                lane_i += 1
            else:
                continue                                  # rigs etc: untouched
            if new_type not in pool_cache:
                pool_cache[new_type] = variant_pool(new_type)
            pool = pool_cache[new_type]
            n = int(re.search(r"\d+", header).group(0))
            variant = pool[(7 * n + 3) % len(pool)]
            body = set_key(body, "Type", new_type)
            body = set_key(body, "VariantReference", variant)
            if new_type == "civ_ms_ritina" and tanker_names and label is None:
                body = set_key(body, "NameOverride", tanker_names.pop(0))
            changes.append(f"{header.strip()} {old_type} -> {new_type} ({variant})")
        else:
            pool_type = new_type = old_type
            k = air_seen.get(old_type, 0)
            air_seen[old_type] = k + 1
            # Same idempotence rule the vessels get: once a file has been
            # dressed, an aircraft that already names a real squadron keeps
            # it. Without this, adding one airliner reshuffles every livery
            # in the mission (and overwrites deliberately chosen ones).
            existing_sq = re.search(r"^SquadronReference=(\S+)", body, re.M)
            if already_refined and existing_sq and existing_sq.group(1) != "Default":
                continue
            pool = SQUADRON_POOLS.get(pool_type)
            if not pool:
                continue
            squadron = pool[k % len(pool)]
            if not squadron_exists(pool_type, squadron):
                sys.exit(f"{pool_type}: {squadron} missing from squadrons file")
            body = set_key(body, "SquadronReference", squadron)
            changes.append(f"{header.strip()} {old_type} -> {new_type} ({squadron})")

        parts[i + 1] = body

    out_text = "".join(parts)

    # Retitle the mission, scoped STRICTLY to [Language_*] sections. A bare
    # Name= key also appears in [TriggerN] and [TaskforceN_Objectives]
    # sections, where it names a trigger or objective - rewriting those with
    # the mission title would silently destroy mission logic.
    renamed = 0
    if args.rename_to:
        chunks = re.split(r"(?=^\[)", out_text, flags=re.M)
        for j, chunk in enumerate(chunks):
            if not re.match(r"^\[Language_[^\]]*\]", chunk):
                continue
            chunks[j], n = re.subn(r"^Name=.*$", lambda _: f"Name={args.rename_to}",
                                   chunk, flags=re.M)
            renamed += n
        out_text = "".join(chunks)

    out.write_text(out_text, encoding="utf-8", newline="\n")
    for c in changes:
        print("  " + c)
    print(f"refined {src.relative_to(ROOT)} -> {out.relative_to(ROOT)}: "
          f"{len(changes)} neutral units re-dressed "
          f"({lane_i} lane merchants, {coast_i} coasters)"
          + (f", {renamed} language titles set to '{args.rename_to}'" if renamed else ""))


if __name__ == "__main__":
    main()
