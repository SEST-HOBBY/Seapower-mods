#!/usr/bin/env python3
"""Build the SEST Replenishment At Sea pack: turn on the game's dormant
ship-to-ship supply system and make it reach the modern fleet.

Sea Power ships the whole mechanic and leaves it switched off. The only
`[SupplySystem1]` block on any hull in vanilla or in the 131 exported Workshop
mods is the commented one on the Sacramento
(mods-source/_vanilla/original/vessels/usn_aoe_sacramento.ini:298-316); the
three suppliers that actually work are land units running TruckSupplySystem.
Workshop item 3605013271, "RE-power: naval resupply in the missile age",
uncomments that block on the stock auxiliaries, and its own description
records where that stops: "Most guns and AA missiles can be replenished
without any issue, but most Anti-ship missiles and torpedoes cannot."

That sentence is the whole design brief for this pack, because there are two
separate reasons for it and neither is fixed by enabling the block:

  1. THE CATEGORY GATE. Ammunition carrying `SupplyCategory=X` can only be
     transferred by a supplier that lists `AccountableAmmunitionCategory_N=X`.
     Guns and point-defence SAMs carry no category, so they flow freely; every
     Harpoon, every ship torpedo and every SS-N-12/19/22 carries one. Vanilla
     stocks those categories on flight decks only, so `SovietAdvancedASM` is
     an outright orphan - stocked by zero suppliers anywhere - which makes the
     Soviet heavy anti-ship missiles unreplenishable by construction.

  2. THE LAUNCHER GATE. A launcher fed by an `AssociatedMagazine=` refills
     when its magazine does. A launcher holding a bare `Ammunition=` - a
     sealed canister, a deck rail, a fixed tube - is one-shot forever unless
     it carries `ReloadableWithoutMagazine=True`. Vanilla states the rule on
     the Long Beach's Mk141 Harpoon canisters, which set it False. Across
     vanilla and all 131 exported mods the flag appears on exactly
     11 units and every one is a land SAM TEL. No vessel anywhere sets it.

Gate 2 is far more expensive than it looks. Red Storm Arsenal - the largest
mod in the collection - models every Mk41 cell as its own launcher with a bare
`Ammunition=` line, so without this pack not one VLS round on any of its 115
hulls could ever be replenished, however many oilers were alongside.

And there is a third problem the mod cannot solve either: the collection has
twelve replenishment-capable hulls and all but two are Cold War. A 2025 task
force had nothing to replenish FROM, so this pack adds six modern auxiliaries
as new unit ids cloned from vanilla donors, the way integration/ran-fleet
clones its European donors. The donors are untouched and both ships coexist.

What this builder emits, in four stages:

  1. Suppliers   - ten upstream hulls get a tuned [SupplySystem1].
  2. Clones      - eight new modern auxiliaries, five BLUE and three RED, with variants and names.
  3. Ammunition  - every heavy ship/sub-launched missile gets one of two new
                   SEST_ categories so it is counted rather than free. Which
                   rounds those are is DERIVED from mods-source on each build,
                   not listed: a hand-written list caught the dash-named
                   vanilla and Euromod ids and missed Red Storm Arsenal's whole
                   underscore-named parallel family. Plus 4 rounds whose
                   vanilla AmmoPoints/SupplyCategory a stats stub strips.
  4. Launchers   - `ReloadableWithoutMagazine=True` on every bare launcher of
                   every modern hull, which is what makes stages 1-3 matter.

The tuning table lives in integration/common/ras.py, shared with
integration/ran-fleet/build_fleet.py, integration/jmsdf-mogami/build_patch.py
and integration/allied-fixes/build_patch.py so the hulls those packs own get
identical treatment without two packs ever shipping the same path.

Usage (repo root):  python3 integration/replenishment/build_patch.py
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
VANILLA = MODS / "_vanilla" / "original"
OUT = Path(__file__).resolve().parent / "SEST_Replenishment"

sys.path.insert(0, str(ROOT / "integration"))
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from common.ras import (                                          # noqa: E402
    CLONES, METER_CATEGORIES, METER_EXEMPT, METER_THRESHOLD,
    RESTORE_ROUNDS, STORE_FIXES, SUPPLIERS, apply_refit, apply_store_fix,
    insert_supply_block, make_reloadable)
from refine_civ_traffic import winning_file                       # noqa: E402

# Hulls whose supply block is emitted by ANOTHER pack's builder, from the same
# shared table. Listed here so this builder can prove it is not about to ship a
# colliding path: two packs shipping different bytes at one unit path is an
# unconditional consolidation failure.
FOREIGN_SUPPLIERS = {"ran_aor_supply"}

# Stage 4 scope. Every mod in the collection that fields post-1990 surface
# combatants or submarines, plus the Cold War Spanish pack because the Teide
# oiler and the Galicia amphibs sail with the modern Spanish fleet. Cold War
# only mods are deliberately left out: this is a modern-fleet integration and
# every file listed here becomes a tier-0 whole-file override.
MODERN_SOURCES = {
    "3390330875": "Modern US Navy",
    "3606774881": "U.S. Navy 2027 Capabilities",
    "3413868677": "Red Storm Arsenal",
    # Euromod Main (3629144864) is not here: it is a weapons and sensors
    # framework and ships no vessels/ directory at all.
    "3599752717": "Euromod - Modern British Navy",
    "3444379330": "Euromod - Modern Dutch Navy",
    "3575847216": "Euromod - Modern German Navy",
    "3642656500": "Euromod - Modern Nordic Navy",
    "3488139470": "Euromod - Modern Italian Navy",
    "3695809489": "Euromod - Modern JMSDF",
    "3731208477": "Euromod - Modern Spanish Navy",
    "3630495619": "Euromod - Cold War Spanish Navy",
    "3456859157": "Mogami-class Frigate",
    "3378409795": "Modern Royal Navy (Type 23)",
    "3417801942": "Chinese Navy (PLAN)",
    "3775128499": "PLAN Pack",
    "3597650470": "Russian Navy 21",
    "3406985435": "Kirov-class (Pyotr Velikiy Upgrade)",
    "3468260539": "Russian Submarines",
    "3594891803": "PLAN Submarines",
    "3433957933": "Virginia-, Seawolf-, and Ohio-class Submarines",
    "3461044389": "Gerald R. Ford-class CVN",
    "3432592449": "Nimitz Expanded",
    "3486502935": "Type 003 Fujian / Type 004 CVN",
    "3663564190": "Type 003 Fujian CV-18",
    "3774572038": "PLAN Type 071 LPD",
    "3774859959": "PLAN Type 001 Liaoning",
    "3438479626": "1143.5 Kuznetsov",
}

INFO_INI = """[Language_en]
Name=SEST Replenishment At Sea
Description=Working Replenishment At Sea for the modern fleet, alongside RE-power (3605013271). Ten auxiliaries (Sacramento, Kilauea, T2, Boris Chilikin, Kazbek, Don tender, Delvar, Sealift Pacific, Algol, Teide) get a tuned supply system - forked from RE-power's copies where it ships the hull, using its field-proven SystemName=TruckSupplySystem - and six modern replenishment ships arrive as new unit ids cloned from vanilla donors: Supply-class T-AOE, Lewis and Clark T-AKE, Henry J. Kaiser T-AO, JMSDF Mashuu, RFA Tide and PLAN Type 901 Fuyu. Every supplier targets Vessel,Submarine so a surfaced boat can rearm; heavy strike and area-SAM rounds are metered by two counted SEST_ categories, derived from the data on each build rather than hand-listed, with per-hull MaxAmmoPoints ceilings deciding what each class of auxiliary can pass. Four rounds whose vanilla AmmoPoints and SupplyCategory a stats stub strips get exactly those two keys back. Most importantly, ReloadableWithoutMagazine=True lands on every bare launcher of every modern hull - deck canisters, fixed tubes and Red Storm Arsenal's per-cell Mk41 VLS - because a launcher with no magazine and no such flag can never be reloaded, which is why anti-ship missiles and torpedoes do not replenish today. Must sit ABOVE every ship mod, RE-power included; this pack wins the hulls both touch and leaves RE-power's merchant suppliers to work below it.

[Compatibility]
ApproximateVersion=0.8.2
"""


# ---------------------------------------------------------------------------
# Load-order resolution.

def load_order_rank():
    tokens = [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt")
              .read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")]
    return {t: i for i, t in enumerate(tokens)}


RANK = load_order_rank()


def supplier_source(unit, source):
    """The copy of a supplier hull this pack forks: VANILLA, deliberately.

    This is the one place the pack does NOT fork the load-order winner, and it
    is a reversal. RE-power wins nine of the ten supplier hulls, and the first
    version of this function forked its copy on the same principle
    winning_ammo() follows - fork what the player actually sees. That rested on
    a claim written into the old docstring, that RE-power's "only change is the
    supply block this pack replaces anyway".

    Measured, that claim is false. Diffing RE-power against vanilla, outside the
    supply block: 26 changed lines on the Sacramento, 21 on the Kilauea, 16 on
    the Boris Chilikin. It DELETES the whole [OpticalView] section (no
    binoculars), drops ArmorType from Minor to None, raises
    MaxAccelerationFactor from 0.21 to 2.4, retunes LinearDrag and the noise
    figures, and removes CavitationSpeed and Prairie.

    Forking that copy meant re-publishing every one of those edits at tier 0,
    under this pack's name, on hulls whose only reason to be here is a supply
    block. So: fork vanilla (or, for the Teide, the mod that is its only
    source), add the supply block, and inherit nothing else. RE-power still
    loads underneath for the fourteen merchant hulls this pack does not touch,
    which is where its own work is untouched.

    `source` is the copy validate() proved exists.
    """
    base = VANILLA if source == "vanilla" else MODS / source
    return base / "vessels" / f"{unit}.ini"


_FLAG_TOKENS = None


def resolve_flag(flag):
    """A flag texture name, resolved the same way a system name is.

    Textures are not .ini sections, so they cannot be looked up in an index -
    but a texture that no file anywhere NAMES is a texture no mod ships, and
    that is a usable proxy. Exactly one clone needs it: the Akademik Pashin
    wants RFN_Flag, the modern Russian ensign, which lives in Russian Navy 21
    (3597650470) and not in vanilla. Without the fallback a player without that
    mod gets a 2021 ship flying nothing; with it they get the Soviet ensign,
    which is wrong but visible.

    A plain string is passed straight through - seven of the eight clones fly
    a flag vanilla ships.
    """
    global _FLAG_TOKENS
    if isinstance(flag, str):
        return flag
    if _FLAG_TOKENS is None:
        _FLAG_TOKENS = set()
        for path in list(MODS.glob("*/vessels/*_variants.ini")) + \
                    list(VANILLA.glob("vessels/*_variants.ini")):
            _FLAG_TOKENS.update(re.findall(r"^FlagTexture=(\S+)", read(path), re.M))
    for name in flag:
        if name in _FLAG_TOKENS:
            return name
    sys.exit(f"none of the flag textures {flag} is referenced anywhere in the "
             "collection - the last entry must be one vanilla ships")


_SYSTEM_INDEX = None


def system_index():
    """Every system name vanilla or an exported mod defines, and who defines it.

    Sensors, weapons, modules and cargo all live in systems/*.ini as plain
    section headers, and - unlike a unit file - these MERGE key by key rather
    than one mod winning the whole file. So a name is available if ANY exported
    mod defines it; there is no load-order winner to resolve, which is why this
    returns every owner rather than the top one.

    Built once and cached: it is 1979 names across 130-odd files.
    """
    global _SYSTEM_INDEX
    if _SYSTEM_INDEX is None:
        idx = collections.defaultdict(set)
        for path in list(MODS.glob("*/systems/*.ini")) + list(VANILLA.glob("systems/*.ini")):
            mod = "vanilla" if VANILLA in path.parents else path.parts[-3]
            for m in re.finditer(r"^\[([^\]\n]+)\]", read(path), re.M):
                idx[m.group(1)].add(mod)
        _SYSTEM_INDEX = idx
    return _SYSTEM_INDEX


def resolve_system(prefs, unit_id, slot):
    """First name in `prefs` the collection actually defines.

    The refit table names the radar it WANTS first and falls back through to
    something vanilla defines, so a player who does not run Red Storm Arsenal
    or Euromod gets a working ship rather than a hull whose SystemName points
    at nothing. Nothing else in the pack degrades this way because nothing else
    references a systems/ definition - the launcher fix edits a key in place
    and the metering edits a category the pack itself defines.

    Two namespaces, and they are NOT the same lookup. A system name is a
    section header in systems/*.ini; a magazine round is a FILE in
    ammunition/. Checking a round against the systems index was the first
    version of this and it rejected every round in the table - correctly, and
    for entirely the wrong reason. The "@" prefix on a magazine slot is what
    picks the lookup.

    Falling off the end is a table bug, not a user's missing mod: every list
    is required to end in a name vanilla itself carries.
    """
    if slot.startswith("@"):
        available = lambda n: winning_file(f"ammunition/{n}.ini") is not None
        what = "ammunition file"
    else:
        idx = system_index()
        available = lambda n: n in idx
        what = "systems/ definition"
    for name in prefs:
        if available(name):
            return name
    sys.exit(f"{unit_id}: refit slot {slot} lists {prefs} and the collection has no "
             f"{what} for any of them - every preference list must end in a name "
             "vanilla itself carries")


_AMMO_INDEX = None


def winning_ammo(ammo_id):
    """The copy of an ammunition file the game actually loads.

    Unit files are whole-file overrides and the Mod Manager reads
    top-priority-first, so the mod with the lowest index in
    data/load-order.tokens.txt wins; vanilla loses to every mod. Forking the
    wrong copy would silently ship the wrong kinematics under the right
    category name, so the resolution is computed rather than hard-coded.

    Lookup is CASE-FOLDED: the game runs on case-insensitive NTFS, and units
    reference rounds in a different case than the filename (the Visby hangs
    swe_RBS15_mk4; the file is swe_rbs15_mk4.ini). A case-exact glob would
    silently drop those rounds from every derivation here.
    """
    global _AMMO_INDEX
    if _AMMO_INDEX is None:
        _AMMO_INDEX = {}
        for path in MODS.glob("*/ammunition/*.ini"):
            mod = path.parent.parent.name
            if mod == "_vanilla":
                continue
            _AMMO_INDEX.setdefault(path.stem.lower(), []).append(
                (RANK.get(mod, 10 ** 6), mod, path))
        for path in VANILLA.glob("ammunition/*.ini"):
            _AMMO_INDEX.setdefault(path.stem.lower(), []).append(
                (10 ** 7, "vanilla", path))
    found = _AMMO_INDEX.get(ammo_id.lower())
    if not found:
        return None, None
    _, mod, path = sorted(found)[0]
    return mod, path


# surrogateescape, not the usual errors="replace". This pack ships 337
# whole-file overrides, so every byte it does not deliberately change must
# survive the round trip - and three upstream files are not valid UTF-8:
#
#   3629144864/ammunition/usn_rgm-109e5a.ini  0xFF inside a mangled line,
#                                             plus two real NUL bytes
#   3575847216/vessels/ger_ffg_f124.ini       0xA0 (non-breaking space) in
#   3575847216/vessels/ger_ffg_f124_ASMD.ini  a sensor label comment
#
# errors="replace" turns each of those bytes into U+FFFD and writes back three
# bytes of garbage - a silent edit to somebody else's file. surrogateescape
# smuggles them through unchanged as long as the same codec writes them out.
# BOMs are read as a leading U+FEFF and written back rather than stripped, for
# the same reason; none of the files copied here has one today.
CODEC = dict(encoding="utf-8", errors="surrogateescape")


def read(path):
    return path.read_text(**CODEC)


def write(rel, text):
    # newline="\n" explicitly, not the default. Path.write_text leaves newline
    # translation on, so on Windows every "\n" would go out as "\r\n" and a
    # rebuild there would diff all 328 files against a Linux build.
    # .gitattributes pins pack output to LF; this makes the builder agree with
    # it on every platform. It is also why the one genuinely CRLF upstream file
    # (3629144864/ammunition/usn_rgm-109e5a.ini) ships as LF: that
    # normalisation is deliberate, and it is the only byte change this pack
    # makes that is not a line it inserted.
    target = OUT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="\n", **CODEC) as fh:
        fh.write(text)


# ---------------------------------------------------------------------------
# Which rounds get metered. See METER_THRESHOLD in common/ras.py for the rule.

def _alias_target(text):
    m = re.match(r"#!alias\s+(\S+)", text.lstrip())
    return m.group(1) if m else None


def ammo_facts(ammo_id, _seen=None):
    """(AmmoPoints, Type, TargetType, has_category) for the copy the game loads.

    Follows `#!alias ammunition/<file>` for any key the alias does not restate
    - 90 ammunition files in the export are aliases, and 21 of them restate
    AmmoPoints while inheriting everything else.
    """
    _seen = _seen or set()
    mod, path = winning_ammo(ammo_id)
    if not path or ammo_id in _seen:
        return None
    _seen.add(ammo_id)
    text = read(path)
    def key(name):
        m = re.search(rf"^{name}\s*=\s*([^\s/]+)", text, re.M)
        return m.group(1) if m else None
    points, kind, target = key("AmmoPoints"), key("Type"), key("TargetType")
    has_cat = bool(re.search(r"^SupplyCategory\s*=", text, re.M))
    target_file = _alias_target(text)
    if target_file and not (points and kind and target):
        parent = ammo_facts(Path(target_file).stem, _seen)
        if parent:
            points = points or parent[0]
            kind = kind or parent[1]
            target = target or parent[2]
            has_cat = has_cat or parent[3]
    return points, kind, target, has_cat


_ALIAS_CHILDREN = None


def alias_descendants(ammo_id):
    """Every ammunition id that inherits, directly or transitively, from this
    one via `#!alias`.

    Inheritance flows FROM the alias target TO the alias file, so tagging a
    parent tags every descendant that does not restate SupplyCategory itself.
    A descendant carried by an aircraft or land unit therefore vetoes tagging
    its parent, exactly as direct carriage does.
    """
    global _ALIAS_CHILDREN
    if _ALIAS_CHILDREN is None:
        _ALIAS_CHILDREN = {}
        for path in list(MODS.glob("*/ammunition/*.ini")) + list(VANILLA.glob("ammunition/*.ini")):
            target = _alias_target(read(path))
            if target:
                _ALIAS_CHILDREN.setdefault(Path(target).stem.lower(), set()).add(path.stem)
    out, queue = set(), [ammo_id.lower()]
    while queue:
        for child in _ALIAS_CHILDREN.get(queue.pop(), ()):
            if child not in out:
                out.add(child)
                queue.append(child.lower())
    return out


def ship_referenced():
    """Every ammunition id some vessel actually carries."""
    carried = set()
    for path in list(MODS.glob("*/vessels/*.ini")) + list(VANILLA.glob("vessels/*.ini")):
        carried |= set(re.findall(r"^Ammunition\d*=(\S+)", read(path), re.M))
    return carried


def land_carried():
    """Ammunition ids a land unit carries.

    The three vanilla land suppliers stock no accountable categories at all, so
    tagging a round they service removes the only supply path the game ships
    working. Red Storm Arsenal's usa_tomahawk_launcher fires usn_rgm-109b.
    """
    carried = set()
    for path in list(MODS.glob("*/land_units/*.ini")) + list(VANILLA.glob("land_units/*.ini")):
        carried |= set(re.findall(r"^Ammunition\d*=(\S+)", read(path), re.M))
    return carried


def metered_rounds():
    """-> (tagged, skipped, orphans, unpriced) - the four audit lists.

    tagged:   [(ammo_id, category, mod)] rounds that get a SEST_ category.
    skipped:  [(ammo_id, why)] rounds meeting every criterion except that an
              aircraft or land unit (or an alias descendant of theirs) carries
              them, or an explicit METER_EXEMPT entry.
    orphans:  heavy uncategorised missiles NO vessel carries - informative
              only, nothing is written for them.
    unpriced: ship/sub-carried missiles with no usable AmmoPoints anywhere in
              their alias chain. They cost nothing and can never be metered;
              inventing a price here would change every magazine that holds
              them, so they are reported, not repaired.
    """
    on_aircraft = {a.lower() for a in aircraft_carried()}
    on_land = {a.lower() for a in land_carried()}
    carried = ship_referenced()
    tag, skip, orphans, unpriced = [], [], [], []

    def qualifies(ammo_id):
        facts = ammo_facts(ammo_id)
        if not facts:
            return None
        points, kind, target, has_cat = facts
        if kind != "Missile" or target not in METER_CATEGORIES or has_cat:
            return None
        try:
            cost = float(points)
        except (TypeError, ValueError):
            return "unpriced"
        return METER_CATEGORIES[target] if cost > METER_THRESHOLD else None

    for ammo_id in sorted(carried):
        verdict = qualifies(ammo_id)
        if verdict == "unpriced":
            unpriced.append(ammo_id)
            continue
        if not verdict:
            continue
        if ammo_id in METER_EXEMPT:
            skip.append((ammo_id, METER_EXEMPT[ammo_id]))
            continue
        family = {ammo_id.lower()} | {d.lower() for d in alias_descendants(ammo_id)}
        if family & on_aircraft:
            skip.append((ammo_id, "carried by an aircraft (directly or via an alias "
                                  "descendant) - tagging would break deck rearming"))
            continue
        if family & on_land:
            skip.append((ammo_id, "carried by a land unit (directly or via an alias "
                                  "descendant) - the land suppliers stock no categories, "
                                  "so tagging removes its only supply path"))
            continue
        mod, _ = winning_ammo(ammo_id)
        tag.append((ammo_id, verdict, mod))

    # Heavy uncategorised missiles nothing at sea carries - candidates the
    # rule would tag the day a vessel arrives carrying one.
    tagged_or_skipped = {a.lower() for a, _, _ in tag} | {a.lower() for a, _ in skip}
    carried_fold = {c.lower() for c in carried}
    for key in sorted(_AMMO_INDEX or {}):
        if key in carried_fold or key in tagged_or_skipped:
            continue
        if key in on_aircraft or key in on_land:
            continue                      # an air or land weapon, not an orphan
        if qualifies(key) in METER_CATEGORIES.values():
            orphans.append(key)
    return tag, skip, orphans, unpriced


# ---------------------------------------------------------------------------
# Validation. Everything that could have moved upstream is checked before a
# single file is written, so a stale mods-source export fails loudly instead of
# shipping a half-applied pack.

def aircraft_carried():
    """Every ammunition id that hangs on an aircraft station, anywhere.

    Tagging a round with a SupplyCategory it did not have makes it
    unreplenishable by any supplier that does not stock that category -
    INCLUDING every carrier and airbase flight deck. So the tagging must touch
    only rounds no aircraft carries. This is recomputed on every build because
    a future mod could hang one of these on a pylon.
    """
    carried = set()
    for path in list(MODS.glob("*/aircraft/*.ini")) + list(VANILLA.glob("aircraft/*.ini")):
        text = read(path)
        for m in re.finditer(r"^Station\d+\s*=\s*([^\n]*)", text, re.M):
            for token in re.split(r"[,|]", m.group(1).split("//")[0]):
                token = token.strip()
                if token:
                    carried.add(token)
    return carried


def validate():
    problems = []

    for unit, spec in SUPPLIERS.items():
        if unit in FOREIGN_SUPPLIERS:
            continue
        src = (VANILLA if spec["source"] == "vanilla" else MODS / spec["source"]) / "vessels" / f"{unit}.ini"
        if not src.exists():
            problems.append(f"supplier hull missing (re-export mods-source?): {src}")

    for unit, clone in CLONES.items():
        mod, donor = clone["donor"]
        base = VANILLA if mod == "vanilla" else MODS / mod
        for suffix in (".ini", "_variants.ini"):
            if not (base / "vessels" / f"{donor}{suffix}").exists():
                problems.append(f"{unit}: donor file missing: {mod}/vessels/{donor}{suffix}")
        if (VANILLA / "vessels" / f"{unit}.ini").exists() or list(MODS.glob(f"*/vessels/{unit}.ini")):
            problems.append(f"{unit}: clone id already exists upstream - pick another id")

    tag, _, _, _ = metered_rounds()
    if not tag:
        problems.append("the metering rule matched no rounds at all - mods-source is "
                        "probably stale or the rule has drifted")

    for ammo_id, stripper in RESTORE_ROUNDS.items():
        vanilla = VANILLA / "ammunition" / f"{ammo_id}.ini"
        if not vanilla.exists():
            problems.append(f"restoration source missing: {vanilla}")
            continue
        good = read(vanilla)
        if not (re.search(r"^AmmoPoints\s*=", good, re.M)
                and re.search(r"^SupplyCategory\s*=", good, re.M)):
            problems.append(f"{ammo_id}: vanilla no longer carries both AmmoPoints and "
                            "SupplyCategory - rebase this restoration")
        stub = MODS / stripper / "ammunition" / f"{ammo_id}.ini"
        if not stub.exists():
            problems.append(f"{ammo_id}: the stripping mod {stripper} no longer ships it - "
                            "rebase, the restoration may be unnecessary")
        elif re.search(r"^SupplyCategory\s*=", read(stub), re.M):
            problems.append(f"{ammo_id}: {stripper} now declares SupplyCategory itself - "
                            "the defect is fixed upstream, drop this restoration")

    for mod in MODERN_SOURCES:
        if not (MODS / mod / "vessels").is_dir():
            problems.append(f"modern source has no vessels/ dir: mods-source/{mod}")

    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(problems))


def foreign_paths():
    """Relative paths already shipped by a sibling SEST pack.

    consolidate_packs.py fails the build if two packs ship different bytes at
    one path, so this pack must never emit a file another pack owns. The set is
    computed from sibling output rather than listed, which is why this pack
    declares build_after on the packs that own vessels.
    """
    owned = set()
    for pack in sorted((ROOT / "integration").glob("*/SEST_*")):
        if pack.parent.name == "dist" or pack.name == OUT.name:
            continue
        for f in pack.rglob("*.ini"):
            owned.add(f.relative_to(pack).as_posix().lower())
    return owned


# ---------------------------------------------------------------------------
# Stages.

def stage_suppliers(owned):
    """Ten upstream hulls get a tuned [SupplySystem1]."""
    built = []
    for unit, spec in SUPPLIERS.items():
        if unit in FOREIGN_SUPPLIERS:
            continue
        rel = f"vessels/{unit}.ini"
        if rel.lower() in owned:
            sys.exit(f"{rel} is already shipped by another SEST pack - move this hull's "
                     "supply block into that pack's builder instead")
        text = read(supplier_source(unit, spec["source"]))
        text, _ = insert_supply_block(text, spec, unit)
        # A supplier is a receiver too: an oiler that has taken damage should
        # be able to take its own point-defence rounds back from a sister.
        text, reloadable = make_reloadable(text)
        write(rel, text)
        built.append((unit, spec, reloadable))
    return built


def clone_variants(donor_text, clone, unit):
    """Australian-fleet recipe: keep the donor's [General] block, because the
    texture and reference wiring must match the donor mesh, then emit clean
    national variants with transparent hull numbers.
    """
    general = re.search(r"\[General\].*?(?=\[Default\])", donor_text, re.S)
    if not general:
        sys.exit(f"{unit}: [General] block not found in donor variants")
    head = re.sub(r"^NumberOfVariants=.*$", f"NumberOfVariants={len(clone['hulls'])}",
                  general.group(0).rstrip() + "\n", flags=re.M)
    body = (f"ResourcesHullnumberFolder=textures/Misc/\n"
            f"HullnumberTexture=transparent\n"
            f"ResourcesFlagFolder=ships/materials/textures/\n"
            f"FlagTexture={resolve_flag(clone['flag'])}\n"
            f"Nation={clone['nation']}\n"
            f"ServiceDate={clone['service']}")
    parts = [head, "", "[Default]", body]
    for i in range(1, len(clone["hulls"]) + 1):
        parts += ["", f"[Variant{i}]", body]
    return "\n".join(parts) + "\n"


def stage_clones(owned):
    """Six new modern auxiliaries, cloned from vanilla donors."""
    names = ["[********************* SEST Replenishment At Sea *********************]", ""]
    built = []
    for unit, clone in CLONES.items():
        rel = f"vessels/{unit}.ini"
        if rel.lower() in owned:
            sys.exit(f"{rel} collides with another SEST pack")
        mod, donor = clone["donor"]
        base = VANILLA if mod == "vanilla" else MODS / mod

        # No DisplayClassName rewrite: none of the three donors carries the key
        # (only vanilla vessels/test.ini does, anywhere). The class name comes
        # from Default= in language_en/vessel_names.ini, exactly as it does for
        # every RAN clone in integration/ran-fleet.
        text = read(base / "vessels" / f"{donor}.ini")
        spec = clone["supply"]
        text, _ = insert_supply_block(text, spec, unit)
        text, refitted = apply_refit(text, clone["refit"], resolve_system, unit)
        text, reloadable = make_reloadable(text)
        write(rel, text)

        write(f"vessels/{unit}_variants.ini",
              clone_variants(read(base / "vessels" / f"{donor}_variants.ini"), clone, unit))

        # The bloc rides in the category field of the Type= line, which is what
        # the mission editor groups the list by. It is one string, so "modern
        # supply, RED" and "modern supply, BLUE" become two adjacent blocks
        # instead of eight ships scattered through Fleet Auxiliary. Composed
        # here from hull_code + bloc rather than written out per ship: a
        # hand-written "AOE,Replenishment (BLUE)" on a RED hull is exactly the
        # kind of typo nothing else would catch.
        names += [f"[{unit}]", f"Type={clone['hull_code']},Replenishment ({clone['bloc']})",
                  f"Default={clone['class_name']},{clone['short']}",
                  f"DefaultDescription={clone['desc']}"]
        names += [f"Variant{i}={full},{short}"
                  for i, (full, short) in enumerate(clone["hulls"], start=1)]
        names.append("")
        built.append((unit, clone, reloadable, refitted))

    write("language_en/vessel_names.ini", "\n".join(names))
    return built


def tag_ammunition(text, category, ammo_id):
    """Add one SupplyCategory line to an ammunition file, inside [General].

    SupplyCategory is a [General] key: every one of the 106 files that declares
    it does so there, next to AmmoPoints. Euromod's eu_mu_90_air.ini is the
    reference for the alias case - `#!alias ammunition/eu_mu_90_ship.ini`, then
    a real `[General]` section carrying nothing but the overrides. Putting the
    key above the first section header instead would file it under the
    nameless section and it would never be read.

    Three shapes occur among the rounds tagged here:
      - AmmoPoints present in [General]  -> insert straight after it.
      - [General] present, no AmmoPoints -> insert after the section header
        (usn_ugm-109j, an alias that inherits its points).
      - no [General] at all              -> synthesise one after the alias
        directive (usn_ugm-109e5a, which opens on [SensorData]).
    """
    line = (f"SupplyCategory={category}"
            "              // For Supply System. Makes that presence of such "
            "category is required for replenishment of this weapon\n")

    general = re.search(r"^\[General\][^\n]*\n", text, re.M)
    if general:
        end_of_general = re.compile(r"^\[", re.M).search(text, general.end())
        stop = end_of_general.start() if end_of_general else len(text)
        anchor = re.compile(r"^AmmoPoints\s*=[^\n]*\n", re.M).search(text, general.end(), stop)
        at = anchor.end() if anchor else general.end()
        return text[:at] + line + text[at:]

    alias = re.search(r"^#!alias[^\n]*\n", text, re.M)
    if alias:
        return text[:alias.end()] + f"\n[General]\n{line}" + text[alias.end():]

    sys.exit(f"{ammo_id}: no [General] section and no #!alias directive to anchor "
             "SupplyCategory to - re-check this file")


def stage_ammunition(owned):
    tagged, restored, skipped = [], [], []
    tag, skipped, orphans, unpriced = metered_rounds()
    for ammo_id, category, mod in tag:
        rel = f"ammunition/{ammo_id}.ini"
        if rel.lower() in owned:
            sys.exit(f"{rel} collides with another SEST pack")
        _, path = winning_ammo(ammo_id)
        write(rel, tag_ammunition(read(path), category, ammo_id))
        tagged.append((ammo_id, category, mod))

    for ammo_id, stripper in RESTORE_ROUNDS.items():
        rel = f"ammunition/{ammo_id}.ini"
        if rel.lower() in owned:
            sys.exit(f"{rel} collides with another SEST pack")
        mod, path = winning_ammo(ammo_id)
        text, keys = restore_keys(read(path), read(VANILLA / "ammunition" / f"{ammo_id}.ini"),
                                  ammo_id)
        write(rel, text)
        restored.append((ammo_id, stripper, mod, keys))
    return tagged, restored, skipped, orphans, unpriced


def restore_keys(current, vanilla, ammo_id):
    """Put the two stripped keys back WITHOUT reverting anything else.

    Shipping the vanilla file wholesale would be a much bigger change than the
    defect: 3395022688's wp_ss-n-19 differs from vanilla by 118 lines, and
    reverting it would quietly undo that mod's whole point (Power 137 -> 82,
    ImpactSize VeryLarge -> Large, the sea-skimming profile). The defect is
    exactly two missing [General] keys, so exactly two lines go back, into the
    copy the game actually loads.
    """
    lines = []
    for key in ("AmmoPoints", "SupplyCategory"):
        if re.search(rf"^{key}\s*=", current, re.M):
            continue
        m = re.search(rf"^{key}\s*=[^\n]*\n", vanilla, re.M)
        if not m:
            sys.exit(f"{ammo_id}: vanilla has no {key} line to restore - rebase")
        lines.append(m.group(0))
    if not lines:
        sys.exit(f"{ammo_id}: nothing left to restore, the winning copy has both keys - "
                 "drop it from RESTORE_ROUNDS")
    general = re.search(r"^\[General\][^\n]*\n", current, re.M)
    if not general:
        sys.exit(f"{ammo_id}: no [General] section to restore the keys into - rebase")
    at = general.end()
    return current[:at] + "".join(lines) + current[at:], [l.split("=")[0] for l in lines]


def dangling_stores(text):
    """Ammunition ids this hull hangs that nothing anywhere defines.

    tools/check_dependencies.py fails the build when a SEST pack ships a file
    naming a store no mod, pack or vanilla file provides - deliberately, so a
    pruned provider fails loudly instead of quietly dropping out of the
    dependency report. Several upstream modern hulls already carry such
    references (usn_rim_162essm, usn_rgm-84, plan_hhq-7a, wp_ss-n-27,
    ita_cal_127mm_vulcano, a handful of amphibious _spawner_ ids, and the
    Visby's swe_RBS15_mk2/mk4 which differ from the real filenames only in
    case). Shipping a tier-0 copy of one of those would make SEST the owner of
    somebody else's broken reference, so those hulls are left alone.

    Resolution goes through the same winning_file() the checker uses, so the
    skip set can never drift out of step with what the gate flags.
    """
    stores = {s.split("|")[0] for s in re.findall(r"^Station\d+=([A-Za-z]\S*)", text, re.M)}
    stores |= live_ammunition(text)

    # DateBased_<slot> is a stock mechanic, not a store: the file declares
    # `DateBased_HWT=0,ger_dm2a4|2035,ger_dm2a5` and then writes
    # `Ammunition1=DateBased_HWT`, so the NAME resolves to whichever round the
    # scenario date selects. Nineteen declarations across the collection use
    # it, vanilla submarines included. integration/allied-fixes already
    # recorded this - "DateBased_ is a vanilla mechanic, used by stock
    # submarines like usn_ssn_permit" - and this function did not know, so it
    # reported the S-80's torpedo room as a dangling reference and skipped the
    # hull. Substitute the real rounds and check those instead.
    for name in [s for s in stores if s.startswith("DateBased_")]:
        stores.discard(name)
        decl = re.search(rf"^{re.escape(name)}=([^\n]*)$", text, re.M)
        if decl:
            for step in decl.group(1).split("|"):
                parts = step.split(",")
                if len(parts) > 1 and parts[1].strip():
                    stores.add(parts[1].strip())
    return sorted(s for s in stores if winning_file(f"ammunition/{s}.ini") is None)


_SECTION = re.compile(r"^\[[^\]\n]*\][^\n]*\n((?:(?!^\[).*(?:\n|$))*)", re.M)


def live_ammunition(text):
    """Ammunition ids the engine will actually read.

    A magazine declares `NumberOfAmmunitionTypes=N` and the engine reads
    Ammunition1..N. Entries past N are dead text - the Han's torpedo room
    declares 3 and lists 4, and that fourth is `wp_ss-n-15`, which nothing
    defines. Counting it made a dead line skip a live hull. Only two files in
    the collection do this, which is exactly why it was worth finding rather
    than guessing at.
    """
    live = set()
    for m in _SECTION.finditer(text):
        body = m.group(1)
        cap = re.search(r"^NumberOfAmmunitionTypes=(\d+)", body, re.M)
        for a in re.finditer(r"^Ammunition(\d*)=(\S+)", body, re.M):
            if cap and a.group(1) and int(a.group(1)) > int(cap.group(1)):
                continue
            live.add(a.group(2))
    return live


def stage_launchers(owned, already_written):
    """`ReloadableWithoutMagazine=True` on every bare launcher of every modern
    hull. This is the stage that makes the other three matter.
    """
    hulls, launchers, by_mod, fixed, unfixable, foreign = 0, 0, {}, [], [], []
    for rel, mod, title in modern_hulls():
        if rel in already_written:
            continue
        if rel.lower() in owned:
            # A sibling SEST pack owns this hull, so it must apply the launcher
            # fix in its own builder (ran-fleet and jmsdf-mogami do). Reported
            # rather than dropped, so a pack that has not been wired up yet is
            # visible instead of quietly missing out.
            foreign.append(rel)
            continue
        text = read(MODS / mod / rel)
        # Repair what upstream mistyped, then report whatever is still broken.
        # These hulls used to be SKIPPED outright, which cost them the launcher
        # fix over a reference that was broken with or without this pack: 77
        # launchers on 10 hulls, including the Kansas-class's 20 ESSM cells,
        # sat unreloadable to avoid owning somebody else's typo. Shipping the
        # hull does not make the typo worse, and six of the eleven were a
        # variant letter away from a round the same mod ships.
        text, repaired = apply_store_fix(text, resolve_system, Path(rel).stem)
        if repaired:
            fixed.append((rel, title, repaired))
        broken = dangling_stores(text)
        if broken:
            unfixable.append((rel, title, broken))
        patched, n = make_reloadable(text)
        if not n:
            continue
        if len(patched.splitlines()) - len(text.splitlines()) != n:
            sys.exit(f"{rel}: line delta {len(patched.splitlines()) - len(text.splitlines())} "
                     f"for {n} launchers - the transform is not a pure insertion")
        write(rel, patched)
        hulls += 1
        launchers += n
        by_mod[title] = by_mod.get(title, 0) + n
    return hulls, launchers, by_mod, fixed, unfixable, foreign


def unused_rounds(ammo_ids):
    """Tagged rounds that no vessel anywhere references.

    Harmless - the tag simply never fires - but a table that silently
    accumulates dead entries stops being reviewable, so the build says which
    ones they are.
    """
    carried = set()
    for path in list(MODS.glob("*/vessels/*.ini")) + list(VANILLA.glob("vessels/*.ini")):
        carried |= set(re.findall(r"^Ammunition\d*=(\S+)", read(path), re.M))
    return [a for a in ammo_ids if a not in carried]


def modern_hulls():
    """(rel, mod, title) for each modern hull, resolved by LOAD ORDER.

    Six vessel files are shipped by two of these mods at once - plan_cv_fujian
    and the Type 039A/B boats. Iterating the mods and writing as we go would
    fork whichever copy happened to come last, which for the Fujian is the
    Type 003/004 mod even though Chinese Navy (PLAN) outranks it. Forking the
    loser and shipping it at tier 0 would silently replace the hull the player
    actually sees with a different mod's version - the same trap winning_ammo()
    exists to avoid on the ammunition side.
    """
    best = {}
    for mod, title in MODERN_SOURCES.items():
        for path in (MODS / mod / "vessels").glob("*.ini"):
            rel = f"vessels/{path.name}"
            rank = RANK.get(mod, 10 ** 6)
            if rel not in best or rank < best[rel][0]:
                best[rel] = (rank, mod, title)
    return [(rel, mod, title) for rel, (_, mod, title) in sorted(best.items())]


def main():
    validate()
    owned = foreign_paths()

    if OUT.exists():
        import shutil
        shutil.rmtree(OUT)

    suppliers = stage_suppliers(owned)
    clones = stage_clones(owned)
    tagged, restored, meter_skips, orphans, unpriced = stage_ammunition(owned)
    written = {f"vessels/{u}.ini" for u, _, _ in suppliers} | \
              {f"vessels/{u}.ini" for u, *_ in clones} | \
              {f"vessels/{u}_variants.ini" for u, *_ in clones}
    hulls, launchers, by_mod, store_fixed, unfixable, foreign = stage_launchers(owned, written)

    # No systemgroups entry is needed: the emitted SystemName is
    # TruckSupplySystem, which vanilla already localises as "Ammunition
    # supply" (language_en/systemgroups.ini:1140).
    write("_info.ini", INFO_INI)

    supplier_launchers = sum(n for _, _, n in suppliers) + sum(n for _, _, n, _ in clones)
    print(f"built {OUT.relative_to(ROOT)}:")
    print(f"  {len(suppliers)} upstream auxiliaries given a working supply system")
    blocs = collections.Counter(c["bloc"] for _, c, _, _ in clones)
    print(f"  {len(clones)} new modern replenishment hulls cloned "
          f"({sum(len(c['hulls']) for _, c, _, _ in clones)} named ships) - "
          + ", ".join(f"{n} {b}" for b, n in sorted(blocs.items())))
    # The refit is printed per ship rather than counted, because a preference
    # list that fell through to its vanilla tail looks identical to one that
    # got what it asked for - and the difference is whether the player has the
    # mod. Reading the arrows is the only way to see which happened.
    for unit, clone, _, refitted in clones:
        swaps = [f"{old}->{new}" for hits in refitted.values()
                 for _, old, new in hits if old != new]
        if swaps:
            print(f"      {clone['bloc']:4} {unit:<22} {', '.join(sorted(set(swaps)))}")
        else:
            print(f"      {clone['bloc']:4} {unit:<22} donor fit kept - nothing "
                  "the collection defines improves on it")
    by_category = collections.Counter(c for _, c, _ in tagged)
    print(f"  {len(tagged)} heavy rounds metered ("
          + ", ".join(f"{n} {c}" for c, n in sorted(by_category.items())) + ")")
    for ammo_id, why in meter_skips:
        print(f"      not metered: {ammo_id} - {why}")
    if orphans:
        print(f"  {len(orphans)} heavy uncategorised missile(s) NOTHING carries - "
              f"nothing written, listed so a future mod's arrival is visible: "
              f"{', '.join(orphans)}")
    if unpriced:
        print(f"  {len(unpriced)} ship/sub-carried missile(s) have no usable AmmoPoints "
              f"anywhere in their alias chain - they cost nothing and cannot be metered; "
              f"prices are the upstream mods' to set, not this pack's:")
        for i in range(0, len(unpriced), 6):
            print("      " + ", ".join(unpriced[i:i + 6]))
    print(f"  {len(restored)} rounds had their stripped keys put back:")
    for ammo_id, stripper, mod, keys in restored:
        print(f"      restored {'+'.join(keys)} on {ammo_id} in the {mod} copy "
              f"(stripped by {stripper})")
    print(f"  {launchers + supplier_launchers} launchers made reloadable across "
          f"{hulls + len(suppliers) + len(clones)} hulls, from {len(by_mod)} mods")
    for title, n in sorted(by_mod.items(), key=lambda kv: -kv[1])[:5]:
        print(f"      {n:>5} {title}")
    orphans = unused_rounds([r for r, _, _ in tagged])
    if orphans:
        print(f"  {len(orphans)} metered round(s) no vessel in the collection carries "
              f"- tagging them is forward-looking, not active: {', '.join(orphans)}")
    if foreign:
        print(f"  {len(foreign)} modern hull(s) owned by a sibling SEST pack, which must "
              f"apply the launcher fix itself: {', '.join(foreign)}")
    if store_fixed:
        n = sum(len(r) for _, _, r in store_fixed)
        print(f"  {n} broken upstream store reference(s) repaired on "
              f"{len(store_fixed)} hull(s) - the weapon had no round at all:")
        for rel, title, repaired in store_fixed:
            arrows = ", ".join(f"{a}->{b}" for a, b in sorted(repaired.items()))
            print(f"      {rel:<44} {arrows}  ({title})")
    if unfixable:
        # Never silent. These hulls ARE patched - the launcher fix is worth
        # having either way - but the named store still resolves to nothing, so
        # that weapon carries no round in game. Upstream's to fix, ours to say.
        print(f"  {len(unfixable)} hull(s) still name a store nothing defines. Patched "
              "anyway; the weapon holding it has no round, with or without this pack:")
        for rel, title, broken in unfixable:
            print(f"      {rel:<44} {', '.join(broken)}  ({title})")


if __name__ == "__main__":
    main()
