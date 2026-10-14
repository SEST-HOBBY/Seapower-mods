#!/usr/bin/env python3
"""Build SEST Cross-Deck: allied flight decks operate the similar allied aircraft.

The user asked (13 Oct 2026) for "cross compatibility for ships and other
similar allied aircraft". A Sea Power hull's `[FlightDeck] AircraftSupported`
names the aircraft its deck will launch and recover; a hull with no list takes
anything carrier-capable (and any helicopter), a hull listing the game's own
`Helicopters` token takes every helicopter, and a hull with an explicit list
takes those types and nothing else. The mods write those lists for their own
navy: a Type 45 names the Royal Navy's Lynx, Merlin and Wildcat, an Iver
Huitfeldt the Danish MH-60R, an Italian FREMM its own SH-101A, AB 212 and
SH-90, a Maya the JMSDF's SH-60J/K and, as it happens, the US MH-60R. So the
campaigns' MH-60R could not land on a bought Iver Huitfeldt, a Royal Navy
Merlin on an Italian FREMM, a German Sea Lynx on a Type 45 or an Australian
S-70B-2 on a Maya, although allied navies cross-deck helicopters of one
family.

The rule here is the one the real navies use: a deck that already operates one
member of a family operates the allied members of that family. The families
are the airframes themselves - every Seahawk is an S-70B/H-60 whatever the
roundel, every NH90 NFH is the same helicopter, the Lynx and the Wildcat share
a deck footprint, the Merlin and the SH-101A are one EH101 - so a deck that
flies one of them can take the others. A deck gains nothing from a family it
does not already list: a frigate with a Seahawk does not get a Merlin, and a
Harrier carrier does not get an F-35B unless it lists an AV-8B already
(Juan Carlos and Canberra do; the Thai Chakri Naruebet, with AV-8S Matadors,
gets the Sea Harriers and nothing newer).

One `#!extend` stub per deck, in vessels_overwrite/ (Anchor Chain's own
mechanic, the way Euromod assigns combat systems and SEST Collection Fixes
does the same): the stub names the hull and sets `AircraftSupported` to the
winning file's own list plus the additions. The winning file is read at
build time, so an upstream list change is carried through on the next build,
and a type the mod lists that no mod ships (dk_mh-60r on the Iver Huitfeldt
was one until the Danish pack arrived; rn_aw159 on the Type 45 still is) is
left exactly as the author wrote it. Only aircraft that exist in the enabled
collection are added, only to decks registered to an allied navy, and never
to a deck that takes everything already.

Not demonstrated in game: whether the engine reads an `AircraftSupported`
set through `#!extend` (the CombatSystems stubs set other sections the same
way, and those are live). Test card: Southern Watch 6J.

Usage (repo root):  python3 integration/cross-deck/build_pack.py
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "SEST_Cross_Deck"
MODS = ROOT / "mods-source"

sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import load_order  # noqa: E402

INFO_INI = """\
[Language_en]
Name=SEST Cross-Deck
Description=Allied flight decks operate the similar allied aircraft: a deck \
that already flies one Seahawk, NH90, Lynx or Wildcat, Merlin, Sea King, \
AB 212, Panther, Seasprite, Cougar, Wasp, Alouette, CH-53, Osprey, Harrier, \
AV-8B/F-35B or catapult type takes the allied members of that family too, so \
an MH-60R lands on an Iver Huitfeldt, a Royal Navy Merlin on an Italian FREMM \
and a Rafale M on the Nimitz. One \
Anchor Chain extend per deck; the hull's own list is kept and only existing \
allied aircraft are added.

[Compatibility]
ApproximateVersion=0.8.5
"""

# Navies whose decks and aircraft cross-deck with each other. The nation
# tokens are the ones the squadron and variant files use. Brazil, Chile,
# India, Indonesia and Pakistan ship allied-built types too, but no campaign
# here sails with them and their lists stay their authors'.
ALLIES = {
    "us", "uk", "france", "germany", "italy", "spain", "netherlands", "denmark",
    "norway", "poland", "belgium", "japan", "south_korea", "australia",
    "newzealand", "new_zealand", "philippines", "thailand",
}

# The airframe families. A deck that lists one member takes every allied
# member the collection ships. Ids are checked for existence at build time;
# a member no enabled mod ships is simply not added.
FAMILIES = {
    "Seahawk (S-70B / SH-60 / MH-60)": [
        "usn_mh-60r", "usn_mh-60r_26", "usn_mh-60r_p2", "usn_sh-60b", "usn_sh-60f", "usn_hh-60",
        "S-70B-2_Seahawk", "ran_S-70B-2_Seahawk", "ran_S-70B-2_Seahawk_late",
        "jmsdf_sh-60j", "jmsdf_sh-60k", "spa_sh-60b", "spa_sh-60b_block1",
        "spa_sh-60bv1", "spa_sh-60bv1_block1", "dk_mh-60r", "tha_S-70B-7_Seahawk",
        "rok_mh60"],
    "NH90 NFH": [
        "fr_nh90", "ger_nh90", "de_nh90", "nl_nh90", "ita_sh90", "be_nh90",
        "sp_nh90_mspt"],
    "Lynx / Wildcat": [
        "rn_wildcat", "rn_aw159", "rn_lynx", "rn_sea_lynx", "rn_sea_lynx_3",
        "rn_sea_lynx_has3", "rn_sea_lynx_mk8", "rn_lynx_has2", "rn_lynx_has3",
        "de_sea_lynx_mk88", "ger_sea_lynx_mk88", "nl_sea_lynx", "nl_sea_lynx_D",
        "fr_sea_lynx", "fr_sea_lynx_4"],
    "Merlin / EH101": ["rn_merlin_hm1", "rn_merlin_hm2", "ita_sh-101a"],
    "Sea King / SH-3": [
        "rn_sea_king", "rn_sea_king_aew", "rn_sea_king_has6", "rn_sea_king_hc4",
        "usn_sh-3h", "usn_sh-3j", "usn_sh_3h", "spa_sh-3d", "spa_sh-3d_AEW",
        "mm_sh-3", "mm_sh-3_91", "ran_westlandseaking", "ran_sea_king_aew2",
        "jmsdf_hss-2", "usmc_vh-3d"],
    "AB 212 / Bell 212": ["spa_ab212", "mm_ab212", "mm_ab212_91", "tha_ab212"],
    "Panther / S-76": ["fr_as-565_sa", "phl_h-76"],
    "Seasprite": ["usn_sh-2f", "usn_sh-2g", "rnzn_sh-2gi"],
    "Cougar / Super Puma / Caracal": [
        "fr_as_532C", "fr_as_532L", "fr_as_532L2", "fr_as_532SC", "fr_as_332B",
        "fr_as_332F", "fr_as_332M", "fr_ec_725"],
    "Wasp / Scout": ["rn_wasp", "rn_wasp_has1", "rnzn_wasp", "ran_scout"],
    "Alouette / Ecureuil": [
        "fr_alouette_II", "fr_sa-319", "fr_as-350", "ran_as350", "ran_as350_recon"],
    "CH-53": ["usmc_ch53_standalone", "jmsdf_ch53_standalone"],
    "Osprey": [
        "usmc_mv-22b", "mv22b_osprey", "jgsdf_mv22b_osprey", "jgsdf_mv-22b",
        "sv22_2024_osprey"],
    "Harrier (first generation)": [
        "usmc_av-8a", "spa_av-8a", "rn_sea_harrier", "rn_sea_harrier_early",
        "rn_harrier_gr3", "ran_sea_harrier84"],
    "AV-8B / F-35B": [
        "usmc_av-8b+", "usmc_av_8b", "usmc_av_8b_plus", "spa_av-8b",
        "spa_av-8b_plus", "mm_av-8b_plus", "usmc_f-35b", "jasdf_f-35b"],
    "Catapult carrier aircraft": [
        "usn_f-35c", "usn_f_35c", "usn_fa-18e", "usn_fa-18f", "usn_fa-18f_blk3",
        "usn_ea-18g", "usn_ea-18g_2020", "usn_e-2d", "usn_e-2c",
        "usn_e_2c_group2_plus", "fr_rafale_m", "fr_rafale_m_l", "fr_e2c", "fr_e2d"],
}

CATEGORY_TOKENS = {"Helicopters"}       # the game's own wildcard


def read(p):
    return Path(p).read_text(encoding="utf-8-sig", errors="replace")


def providers():
    """(token, directory) highest priority first, as the campaign builder
    resolves them: the per-pack SEST sources stand in for the consolidated
    pack (which does not exist yet on a from-scratch build), then the
    Workshop mods in Mod Manager order, then the game's own files."""
    out = []
    for token in load_order():
        if token.startswith("SEST_"):
            for pack in sorted((ROOT / "integration").glob("*/SEST_*")):
                if pack.parent.name != "dist" and pack != OUT:
                    out.append((pack.name, pack))
        elif (MODS / token).is_dir():
            out.append((token, MODS / token))
    out.append(("_vanilla", MODS / "_vanilla" / "original"))
    return out


_INDEX = None


def winning_file(relpath):
    """The copy of <relpath> the game loads, resolved case-blind like NTFS."""
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for _token, base in reversed(providers()):
            for kind in ("vessels", "aircraft"):
                for f in (base / kind).glob("*.ini"):
                    _INDEX[f"{kind}/{f.name}".lower()] = f
    return _INDEX.get(relpath.lower())


def owner_of(path):
    """The mod token (or SEST pack) a winning file belongs to."""
    parts = Path(path).parts
    if "mods-source" in parts:
        return parts[parts.index("mods-source") + 1]
    if "integration" in parts:
        return parts[parts.index("integration") + 2]
    return "?"


def section_value(text, sections, key):
    """`key` from the first of `sections` that sets it, else None."""
    for name in sections:
        m = re.search(r"^\[" + re.escape(name) + r"\][^\n]*\n(.*?)(?=^\[|\Z)",
                      text, re.M | re.S)
        if m:
            v = re.search(r"^\s*" + re.escape(key) + r"=\s*([^\s/#]+)", m.group(1), re.M)
            if v:
                return v.group(1)
    return None


def nation(kind, uid):
    """The navy a unit is registered to, from its squadrons/variants file's
    first pick or [Default], else the unit file's own Nation=, lower-cased."""
    table = winning_file(f"{kind}/{uid}_{'squadrons' if kind == 'aircraft' else 'variants'}.ini")
    if table:
        n = section_value(read(table), ("Squadron1", "Variant1", "Default"), "Nation")
        if n:
            return n.lower()
    f = winning_file(f"{kind}/{uid}.ini")
    if f:
        m = re.search(r"^Nation=\s*([^\s/#]+)", read(f), re.M)
        if m:
            return m.group(1).lower()
    return ""


def aircraft_exists(uid):
    f = winning_file(f"aircraft/{uid}.ini")
    return f is not None


def every_vessel_id():
    ids = set()
    for f in MODS.glob("*/vessels/*.ini"):
        if not f.stem.endswith("_variants"):
            ids.add(f.stem)
    for f in (MODS / "_vanilla" / "original" / "vessels").glob("*.ini"):
        if not f.stem.endswith("_variants"):
            ids.add(f.stem)
    for f in (ROOT / "integration").glob("*/SEST_*/vessels/*.ini"):
        if not f.stem.endswith("_variants"):
            ids.add(f.stem)
    return sorted(ids)


def deck_list(text):
    """(section, list) of the hull's AircraftSupported, or (None, None)."""
    sec = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            sec = s[1:-1]
        elif s.startswith("AircraftSupported="):
            value = s.split("=", 1)[1].split("//")[0].split("#")[0]
            return sec, [t.strip() for t in value.split(",") if t.strip()]
    return None, None


def plan():
    """[(uid, owner, nation, section, current, {family: [adds]})]."""
    members = {}                      # family -> allied members that exist
    for fam, ids in FAMILIES.items():
        kept = []
        for uid in ids:
            if not aircraft_exists(uid):
                continue
            # A member another navy flies (fr_as_532SC is Chile's Cougar) is
            # not added anywhere; a deck that lists it keeps it.
            n = nation("aircraft", uid)
            if n and n not in ALLIES:
                continue
            kept.append(uid)
        members[fam] = kept
    out = []
    for uid in every_vessel_id():
        f = winning_file(f"vessels/{uid}.ini")
        if f is None:
            continue
        text = read(f)
        if text.lstrip().startswith("#!extend"):
            continue                  # a same-name patch: its base is listed on its own
        aliased = text.lstrip().startswith("#!alias")
        if not aliased and not re.search(r"^UnitType=Vessel\s*$", text, re.M):
            continue
        # An alias with a deck list of its own (U.S. Navy 2027's Nimitz, an
        # alias of ADOU's hull carrying its own air wing) is a deck in its
        # own right; an alias without one takes its base's, listed there.
        sec, current = deck_list(text)
        if aliased and not current:
            continue
        if not current or CATEGORY_TOKENS & set(current):
            continue                  # takes everything already, or has no deck
        n = nation("vessels", uid)
        if n not in ALLIES:
            continue
        have = set(current)
        adds = collections.OrderedDict()
        for fam, ids in members.items():
            if have & set(FAMILIES[fam]):
                new = [a for a in ids if a not in have]
                if new:
                    adds[fam] = new
        if adds:
            out.append((uid, owner_of(f), n, sec, current, adds))
    return out


def stub(uid, owner, nat, current, adds):
    added = [a for ids in adds.values() for a in ids]
    lines = [f"#!extend vessels/{uid}.ini", "",
             f"# SEST Cross-Deck: {owner}'s {uid} ({nat}) lists {len(current)} type(s). It",
             "# already flies one of each family below, so it operates the allied",
             "# members too (the hull's own list is kept; only aircraft the enabled",
             "# collection ships are added; read from the winning file at build):"]
    for fam, ids in adds.items():
        lines.append(f"#   {fam}: {', '.join(ids)}")
    lines += ["", "[FlightDeck]",
              "AircraftSupported=" + ",".join(current + added), ""]
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    out_dir = OUT / "vessels_overwrite"
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*_CrossDeck_SEST.ini"):
        stale.unlink()
    print("SEST_Cross_Deck")
    rows = plan()
    bad_section = [r for r in rows if r[3] != "FlightDeck"]
    if bad_section:
        sys.exit("AircraftSupported outside [FlightDeck] on: "
                 + ", ".join(f"{r[0]} ([{r[3]}])" for r in bad_section)
                 + " - the stub would set the key in the wrong section")
    table = ["SEST Cross-Deck - which allied aircraft each deck now operates",
             "", "Generated by integration/cross-deck/build_pack.py. A deck that already",
             "flies one member of an airframe family takes the allied members too;",
             "the hull's own list is kept. Nothing here changes a deck that already",
             "accepts every helicopter or every carrier aircraft.", ""]
    by_nation = collections.Counter()
    for uid, owner, nat, _sec, current, adds in rows:
        (out_dir / f"{uid}_CrossDeck_SEST.ini").write_text(
            stub(uid, owner, nat, current, adds), encoding="utf-8")
        by_nation[nat] += 1
        added = [a for ids in adds.values() for a in ids]
        table.append(f"{uid} ({nat}, {owner}): +{len(added)}")
        for fam, ids in adds.items():
            table.append(f"    {fam}: {', '.join(ids)}")
        print(f"  {uid:40} {nat:12} +{len(added):2}  "
              + "; ".join(f"{fam.split(' (')[0]} {len(ids)}" for fam, ids in adds.items()))
    (OUT / "CROSS-DECK.txt").write_text("\n".join(table) + "\n", encoding="utf-8")
    print(f"  {len(rows)} deck(s) extended: "
          + ", ".join(f"{n} {c}" for n, c in sorted(by_nation.items())))
    if not rows:
        sys.exit("no deck to extend - the families or the nation table no longer match the collection")


if __name__ == "__main__":
    main()
