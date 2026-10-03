"""Shared definitions for Sea Power 0.8.3's combat-system (OODA) model.

Since 0.8.3 (Build 261001, 1 Oct 2026) a hull may carry

    [CombatSystems]
    NumberOfCombatSystems=1

    [CombatSystem1]
    SystemName=AEGIS_Mk7

naming a profile in `systems/combatsystems.ini`: ReactionTime band
(VerySlow..VeryFast), DatalinkTier (0-5), DatalinkSource, SignalProcessingBonus,
CICSlots (contacts the CIC can hold) and EvaluationSlots (contacts it works at
once). 126 vanilla hulls declare one; a hull that declares none is given a band
from its service year with default slots. Vanilla puts the block LAST in the
hull file, after the collider list, and so does this module. Every one of
vanilla's 46 submarines declares none, so this pack assigns nothing to a
submarine either - the game's own choice for that unit type stands.

Euromod (3629144864) ships 54 profiles of its own and assigns them by
`#!extend` to 162 hulls, including hulls of OTHER mods lower in the order
(Modern US Navy, the German, Danish, Dutch, Italian and British packs). That
is the mechanism SEST Collection Fixes uses for the mod hulls the campaigns
field that still declare none, and it is why the extend is known to work
across mods: the biggest pack in the collection relies on it.

The SEST profiles below are CLONES of Euromod profiles under SEST names, the
way Collection Fixes clones sensors: the pack then depends on no Euromod id,
and the shadow guard in defined_system_names() stops the build if anyone
starts defining a SEST_ name. Bodies are copied verbatim except where an
entry lists an override, and every override is a single key with its reason
beside it. Vanilla profiles are referenced by name where vanilla already
models the exact ship (ZKJ-3 for the Luda, Sapfir_U for the Sovremenny,
Lesorub_55 for the Kuznetsov, Alleya_2M for the Kirov).

Imported the same way as common/ras.py:

    sys.path.insert(0, str(ROOT / "integration"))
    from common.combat import PROFILES, set_combat_system, swap_systems
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / "mods-source"
VANILLA = MODS / "_vanilla" / "original"
EUROMOD = "3629144864"

# The one deliberate delta. Vanilla's own calibration puts every Soviet
# profile one datalink tier below its NATO contemporary (Alleya_2M, Lesorub,
# Sapfir_U: 4 against AEGIS_Mk7 and NTDS's 5; Koren 4 against ADAWS's 5), and
# ships no modern Russian profile at all. The Euromod bodies the Russian
# hulls borrow are NATO ones, so they take the same one-tier step down.
RU_DATALINK = {"DatalinkTier": "4"}

# SEST profile -> (donor mod folder, donor section, {key: value overrides}, why)
PROFILES = {
    # --- blue ----------------------------------------------------------
    "SEST_AEGIS_BL9": (EUROMOD, "AEGIS_BL9", {},
                       "Aegis Baseline 9: the Hobart (the RAN's Aegis refresh), the 2027 "
                       "Ticonderogas, Korea's KDX-III."),
    "SEST_AEGIS_BL10": (EUROMOD, "AEGIS_BL10", {},
                        "Aegis Baseline 10 with SPY-6: the 2030 Flight III Burke."),
    "SEST_SSDS_Carrier": (EUROMOD, "SSDS_Carrier", {},
                          "Ship Self-Defense System on a US carrier: Ford, Ford (JSF), the "
                          "2000s Nimitz."),
    "SEST_9LV_MLU": (EUROMOD, "9LV_Multirole_MLU", {},
                     "Saab 9LV Mk3E with CEAFAR: the ASMD Anzac."),
    "SEST_9LV_Compact": (EUROMOD, "9LV_Compact", {},
                         "Saab 9LV on a non-combatant or patrol hull: Canberra, Arafura, "
                         "Supply."),
    "SEST_9LV_Compact_MLU": (EUROMOD, "9LV_Compact_MLU", {},
                             "the FFG Upgrade Adelaide's ADACS."),
    "SEST_OYQ_Integrated": (EUROMOD, "OYQ_Integrated", {},
                            "JMSDF OYQ-1: the Mogami."),
    "SEST_CMS_SeaCeptor": (EUROMOD, "CMS_SeaCeptor", {},
                           "a Sea Ceptor Type 23, which is the refit the old Duke-class "
                           "mod models."),
    "SEST_SENIT_Carrier": (EUROMOD, "SENIT_Carrier", {},
                           "SENIT 8 on Charles de Gaulle."),
    "SEST_CMS_AAW_PAAMS": (EUROMOD, "CMS_AAW_PAAMS", {},
                           "PAAMS on the Horizon."),
    "SEST_SETIS_Integrated": (EUROMOD, "SETIS_Integrated", {},
                              "SETIS on the FDI Amiral Ronarc'h."),
    "SEST_SETIS_AAW": (EUROMOD, "SETIS_AAW", {},
                       "SETIS on the air-defence Aquitaine."),
    "SEST_SETIS_ASW_MLU": (EUROMOD, "SETIS_ASW_MLU", {},
                           "SETIS on the modernised ASW Aquitaine."),
    "SEST_CMS_Compact_Enhanced": (EUROMOD, "CMS_Compact_Enhanced", {},
                                  "a compact modern CMS: the modernised La Fayettes, Korea's "
                                  "Daegu."),
    # --- PLAN ----------------------------------------------------------
    "SEST_PLAN_AAW": (EUROMOD, "CMS_AAW_APAR", {},
                      "ZKJ-5 behind a four-face phased array: the Type 052C and 052D."),
    "SEST_PLAN_Cruiser": (EUROMOD, "CMS_AAW_APAR_MLU", {},
                          "the Type 055's integrated combat system; the Euromod MLU APAR "
                          "profile is the nearest shape (VeryFast, 144 contacts, 6 worked)."),
    "SEST_PLAN_Multirole": (EUROMOD, "CMS_Multirole_MLU", {},
                            "ZKJ-5 on a frigate: the Type 054 and 054A, the 2017 Shenzhen, "
                            "the Type 051M."),
    "SEST_PLAN_Compact": (EUROMOD, "9LV_Compact", {},
                          "a corvette's CMS: the Type 056A."),
    "SEST_PLAN_Carrier": (EUROMOD, "SSDS_Carrier", {},
                          "Liaoning, Shandong, Fujian, the Type 004, the export 1143."),
    "SEST_PLAN_Amphibious": (EUROMOD, "NTDS_Amphibious", {},
                             "the Type 071."),
    # --- Russia ---------------------------------------------------------
    "SEST_RU_AAW": (EUROMOD, "CMS_AAW_APAR", RU_DATALINK,
                    "Poliment-Redut: the Gorshkovs, the Project 21956, the Nakhimov refit."),
    "SEST_RU_Multirole": (EUROMOD, "CMS_Multirole_MLU", RU_DATALINK,
                          "Trebovanie-M on the Grigorovich."),
    "SEST_RU_Compact": (EUROMOD, "CMS_Compact_Enhanced", RU_DATALINK,
                        "Sigma-20380 on the Steregushchiy and Gremyashchiy."),
}

# Vanilla profiles this pack points hulls at by name, because vanilla already
# models the exact ship or its generation. Each is checked to exist.
VANILLA_PROFILES = {
    "ZKJ-3": "vanilla's Luda profile",
    "Sapfir_U": "vanilla's Sovremenny profile",
    "Lesorub_1164": "vanilla's Slava profile",
    "Lesorub_55": "vanilla's Kuznetsov profile",
    "Alleya_2M": "vanilla's Kirov profile",
    "Titanit": "vanilla's missile-boat target designation system",
    "PointDefence_Local": "vanilla's local point-defence profile",
}

PROFILE_KEYS = ("ReactionTime", "DatalinkTier", "DatalinkSource",
                "SignalProcessingBonus", "CICSlots", "EvaluationSlots")


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig", errors="replace").replace("\r", "")


def section(text, name):
    """Body of [name] (header comment tolerated, as 0.8.3 writes
    `[Gurzuf] # Side Globes`), or None."""
    m = re.search(rf"^\[{re.escape(name)}\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.S | re.M)
    return m.group(1) if m else None


def section_names(text):
    return [m.group(1).strip() for m in re.finditer(r"^\[([^\]\n]+)\]", text, re.M)]


def vanilla_profile_names():
    return set(section_names(read_text(VANILLA / "systems" / "combatsystems.ini")))


def defined_system_names():
    """name -> [folders defining it], across vanilla, every mod and every SEST
    pack (the dist excluded) - the shadow guard's input."""
    out = {}
    files = ([VANILLA / "systems" / "combatsystems.ini"]
             + sorted(MODS.glob("*/systems/combatsystems.ini"))
             + sorted(p for p in ROOT.glob("integration/*/SEST_*/systems/combatsystems.ini")
                      if "dist" not in p.parts))
    for f in files:
        if not f.exists():
            continue
        # mods-source/<id>/systems/, integration/<x>/SEST_<Pack>/systems/, or vanilla
        owner = "_vanilla" if "_vanilla" in f.parts else f.parts[-3]
        for name in section_names(read_text(f)):
            out.setdefault(name, []).append(owner)
    return out


def profile_body(name):
    """The SEST clone's body: the donor's lines, overrides applied in place."""
    donor_mod, donor_sec, overrides, _ = PROFILES[name]
    src = MODS / donor_mod / "systems" / "combatsystems.ini"
    if not src.exists():
        sys.exit(f"{name}: donor file missing (re-export {donor_mod}?): {src}")
    body = section(read_text(src), donor_sec)
    if body is None:
        sys.exit(f"{name}: donor profile [{donor_sec}] missing from {donor_mod} - rebase")
    # Key lines only: Euromod writes each profile's description as a comment
    # line ABOVE its header, which a body-to-next-header capture would carry
    # into the previous clone.
    lines = [l for l in body.strip().splitlines()
             if l.strip() and "=" in l and not l.lstrip().startswith("#")]
    keys = [l.split("=", 1)[0].strip() for l in lines]
    missing = [k for k in PROFILE_KEYS if k not in keys]
    if missing:
        sys.exit(f"{name}: donor [{donor_sec}] lacks {missing} - the profile shape changed")
    for key, value in overrides.items():
        if key not in keys:
            sys.exit(f"{name}: override key {key} is not in the donor - rebase")
        lines = [f"{key}={value}" if l.split("=", 1)[0].strip() == key else l for l in lines]
    return "\n".join(lines) + "\n"


def render_profiles(names=None):
    """The systems/combatsystems.ini text for the named SEST profiles."""
    names = list(PROFILES) if names is None else list(names)
    blocks = []
    for name in names:
        donor_mod, donor_sec, overrides, why = PROFILES[name]
        delta = ("; " + ", ".join(f"{k} {_donor_value(donor_mod, donor_sec, k)} -> {v}"
                                  for k, v in overrides.items())) if overrides else ""
        blocks.append(f"# {name}: {why}\n"
                      f"# Cloned from [{donor_sec}] in {donor_mod}{delta}.\n"
                      f"[{name}]\n{profile_body(name)}")
    return "\n".join(blocks)


def _donor_value(donor_mod, donor_sec, key):
    body = section(read_text(MODS / donor_mod / "systems" / "combatsystems.ini"), donor_sec)
    m = re.search(rf"^{re.escape(key)}=([^\n]*)$", body or "", re.M)
    return m.group(1).strip() if m else "?"


def check_profiles(names):
    """Every name a hull is pointed at is a SEST profile or a vanilla one, and
    no SEST profile name is defined by anyone else."""
    vanilla = vanilla_profile_names()
    defined = defined_system_names()
    for name in names:
        if name in PROFILES:
            others = [o for o in defined.get(name, []) if not o.startswith("SEST_")]
            if others:
                sys.exit(f"{name} is now defined by {others} - rename the SEST profile "
                         "rather than shadowing upstream")
        elif name not in vanilla:
            sys.exit(f"{name}: not a SEST profile and not in vanilla's combatsystems.ini")
    for name, _ in VANILLA_PROFILES.items():
        if name not in vanilla:
            sys.exit(f"vanilla profile [{name}] is gone from the game - re-choose")


def combat_block(profile, note=""):
    comment = f"  // {note}" if note else ""
    return ("[CombatSystems]\n"
            "NumberOfCombatSystems=1\n"
            "\n"
            "[CombatSystem1]\n"
            f"SystemName={profile}{comment}\n")


_CS_BLOCK = re.compile(r"^\[CombatSystems\][^\n]*\n(?:(?!^\[).*(?:\n|$))*", re.M)
_CS1_BLOCK = re.compile(r"^\[CombatSystem1\][^\n]*\n(?:(?!^\[).*(?:\n|$))*", re.M)


def set_combat_system(text, profile, unit_id, note="SEST combat system"):
    """Give a hull `profile`: replace the SystemName of an existing
    [CombatSystem1], or append vanilla's block at the end of the file."""
    has = _CS_BLOCK.search(text)
    if has:
        m = re.search(r"^NumberOfCombatSystems=(\d+)", has.group(0), re.M)
        if not m or m.group(1) != "1":
            sys.exit(f"{unit_id}: [CombatSystems] declares "
                     f"{m.group(1) if m else 'no'} systems; this helper handles one")
        blk = _CS1_BLOCK.search(text)
        if not blk:
            sys.exit(f"{unit_id}: [CombatSystems] without a [CombatSystem1] - look")
        body, n = re.subn(r"^SystemName=([^\n]*)$",
                          lambda mm: f"SystemName={profile}  // {note}; was "
                                     f"{mm.group(1).split('//')[0].strip()}",
                          blk.group(0), count=1, flags=re.M)
        if n != 1:
            sys.exit(f"{unit_id}: [CombatSystem1] has no SystemName line")
        return text[:blk.start()] + body + text[blk.end():]
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n" + combat_block(profile, note)


def swap_systems(text, mapping, unit_id):
    """Rename `SystemName=OLD` lines to NEW for every pair in mapping; each
    pair must match at least once. -> (text, count)."""
    total = 0
    for old, new in mapping.items():
        text, n = re.subn(rf"^SystemName={re.escape(old)}([ \t]*(?://[^\n]*)?)$",
                          f"SystemName={new}  // SEST: was {old}", text, flags=re.M)
        if n == 0:
            sys.exit(f"{unit_id}: no SystemName={old} line to swap - donor changed, re-check")
        total += n
    return text, total
