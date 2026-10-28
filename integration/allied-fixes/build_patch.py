#!/usr/bin/env python3
"""Build the SEST Allied Fixes patch: the P-8 Poseidon's anti-ship loadout.

usn_p8_2027 declares AvailableLoadouts=ASW,AntiShip - two options - and the
AntiShip one hangs four rounds of usn_agm-84g on WeaponSystem2. Nothing in the
collection defines usn_agm-84g. Not U.S. Navy 2027, which ships the aircraft;
not any of the other 128 mods; not vanilla. There is no real AGM-84G either.
So the Poseidon's only anti-ship fit puts nothing on the wings, and half of
what a maritime patrol aircraft is for quietly does not work.

It is a typo, and the mod answers it itself: U.S. Navy 2027 writes usn_agm-84n
nineteen times and usn_agm-84g four times, and all four are these station
lines. usn_agm-84n is its own Harpoon Block II+ ER - 522 kg, 150 nm - already
carried by its ships and its Super Hornets.

usn_p8 from mod 3602046770 has the identical four-line typo and the identical
ASW,AntiShip pair, so it gets the same substitution.

UPDATE, 2026-09-20 export: U.S. Navy 2027 fixed its own copy - usn_p8_2027
now writes Station1..4=usn_agm-84n, which is precisely what this patch was
substituting. That target was retired then; 3602046770's usn_p8 still
carries the typo four times and is still patched.

UPDATE, 28 Oct 2026: with the right Harpoon on the wings, neither P-8 could
guide it. usn_agm-84n is MidCourseCorrection=1, radio command. The game will
not fire such a round from a hardpoint that links no sensor, which is
usn_p8's case; usn_p8_2027 links only a FLIR, so its Harpoons fly with the
link lost from launch, no midcourse updates (P8_GUIDANCE below has the game
code). The owner's SW05 play test: "a player-allocated P-8 with AntiShip
Harpoons does not reliably fire". Both P-8s now link U.S. Navy 2027's
GPS_Receiver to their wing pylons - usn_p8 gains the sensor, which
usn_p8_2027 already carries - so usn_p8_2027 is shipped again, for that one
line. This is the fix the owner's PC already ran (GPT's PR #50 dist).

Not included, having checked each one:
  - usn_e-2d, fr_e2c, fr_e2d, usn_ch-46d, usaf_ac-130a_83, jmsdf_kv_107*
    all declare a loadout with no matching block, but every one of them is an
    unarmed aircraft whose blocks carry zero stores. The picker entry is
    cosmetic and an override would add a dependency for no gameplay change.
  - usn_p-3d is missing only its Recon block; ASW, AntiShip and Empty all
    work, and nothing fields it.
  - rn_merlin_hm1 and the two Lynxes look like they reference undefined
    DateBased_* stores. They do not - DateBased_ is a vanilla mechanic, used
    by stock submarines like usn_ssn_permit.

Usage (repo root):  python3 integration/allied-fixes/build_patch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "SEST_Allied_Fixes"

sys.path.insert(0, str(ROOT / "integration"))
from common.a10c import fix_squadron_count, register_ir_head  # noqa: E402
from common.ras import make_reloadable  # noqa: E402
from common.redback import add_fit as add_redback  # noqa: E402

MISSING = "usn_agm-84g"      # defined by nothing, anywhere
REPLACE = "usn_agm-84n"      # U.S. Navy 2027's own Harpoon Block II+ ER

# (workshop id, aircraft file)
TARGETS = [
    ("3602046770", "usn_p8.ini"),        # still carries the typo, 4x
]

# Targets retired because upstream adopted the fix: (workshop id, aircraft
# file, why). Each is unlinked below so a pack folder built before the
# retirement does not keep serving a stale copy. Empty since 28 Oct 2026:
# U.S. Navy 2027's usn_p8_2027 was retired on the 2026-09-20 export, when its
# AntiShip block began writing Station1..4=usn_agm-84n itself, and is shipped
# again for its guidance channel (P8_GUIDANCE) - its stations stay upstream's.
RETIRED = []

# The P-8 Harpoon's guidance channel (28 Oct 2026). usn_agm-84n is
# MidCourseCorrection=1, radio command. What Sea Power 0.8.7 does with that,
# read from Seapower-Scripts.dll on 28 Oct 2026:
# - AmmunitionParameters.loadWeaponParameters (IL_0497-IL_0523): 1 maps to
#   MidCourseCorrection.RadioCommand, whose AllowsLauncherGuidance makes the
#   round _requiresGuidance.
# - WeaponSystemHardpoint.UpdateEngageInterruptors (IL_0029-IL_00b3): a
#   _requiresGuidance round from a hardpoint with no AssociatedSensors ends
#   the engage task and logs "can not be launched without associated
#   sensor"; with some, it waits until WeaponSystem.hasFreeWeaponChannel
#   finds one that is on and has a free weapon channel. The weapon selector
#   (WeaponSystem.HasFreeGuidingSensors) passes an empty list, so the
#   Harpoons are offered all the same.
# - usn_p8 (3602046770) links nothing to its wing pylons: the engage ends.
#   usn_p8_2027 links only its MX-20HD FLIR. A sensors.ini entry with no
#   WeaponChannels key gets one channel (SensorRecord's constructor,
#   IL_0033), so that Harpoon does launch - but a FLIR is not a radar, and
#   WeaponBase.ActivateNonLaserGuidanceSystem, finding no radar to guide it,
#   marks the link lost for good at launch (IL_0332-IL_034a): the round gets
#   no midcourse updates. Neither pylon links the APY-10 either. (Under
#   SEST's load order the APY-10 that wins is US Naval Aviation's, 3737267013:
#   Type=Search, WeaponChannels=12. Only the Boeing P-8 mod's own copy says
#   WeaponChannels=0, so the missing link, not the radar, is the fault.)
# - U.S. Navy 2027's [GPS_Receiver] is Kind=Radar, Type=Targeting,
#   Mode=RadioCommand with 5000 weapon channels - the author's "GPS receiver
#   to allow for target updating for GPS weapons", which its own F/A-18E/F
#   link to their hardpoints the same way. A Targeting radar stays on from
#   spawn (BaseSystem.init sets IsOn; SensorSystemRadar.init switches off
#   only search radars), and EMCON switches off search radars, jammers and
#   towed systems, never it.
# - At launch, WeaponBase.ActivateNonLaserGuidanceSystem (IL_004d-IL_0162)
#   takes the first linked SensorSystemRadar that can guide the round as its
#   guiding radar. In flight Missile.CheckRadioConnection holds the link while
#   the missile stays inside the launcher's sensor range, control range and
#   line of sight, and for radio command ends in RadioCommandTargetIllumination
#   (IL_077f). If the link drops, the Harpoon flies on and finishes on its own
#   active seeker (AmmunitionParameters.CanFinishOnOwnSeeker,
#   Missile.OnUpdateEveryFrame IL_0155-IL_01b0).
# - ObjectBaseLoader.initWeaponParameters (IL_01a9-IL_036b) splits
#   AssociatedSensors= on commas with no trimming, looks each name up as a
#   section of the unit file, and logs an error for one it cannot find. When
#   that key is present, NumberOfAssociatedSensors is not read; the line is
#   kept because the owner's tested files and the author's Super Hornets
#   write it.
# The rest of each pylon's fits (sonobuoys; usn_p8_2027's LRASM, itself radio
# command, which the link also lets fly) is untouched. Every edit below
# checks the shape it expects and stops the build if upstream changed it.
GPS_SENSOR = "GPS_Receiver"
GPS_BLOCK = ("[SensorSystem6] # Harpoon midcourse provider\n"
             "Type=Radar\n"
             f"SystemName={GPS_SENSOR}\n"
             "Mount=Dummy\n"
             "MountPosition=0,0,0\n"
             "ModuleType=Sensor\n"
             "\n")
# aircraft file -> (workshop id, links the wing pylons have upstream, links SEST writes)
P8_GUIDANCE = {
    "usn_p8.ini": ("3602046770", [], ["SensorSystem6"]),
    "usn_p8_2027.ini": ("3606774881", ["SensorSystem5"], ["SensorSystem5", "SensorSystem6"]),
}

INFO_INI = """\
[Language_en]
Name=SEST Allied Fixes
Description=Small allied corrections: the P-8's anti-ship fit pointed at a \
Harpoon no mod defines (loaded empty), neither P-8 linked a guidance \
channel for its radio-command Harpoons, so one could not launch them and the \
other launched them with no midcourse updates (both now link U.S. Navy \
2027's GPS receiver to the wing pylons), HMS Ocean could not operate the \
Apache AH1 her sister hulls already support, the RNZAF and ROKN P-8 \
squadrons named nations the game has no flag for, and the A-10C's infrared \
head was never registered as a sensor module while its squadron file \
declared seven squadrons against two defined liveries. Also SEST's AGR-30 \
Redback - a fictional fire-and-forget active-homing 70mm guided rocket, \
30 nm, a ten-second boost, slow cruise and diving approach - as a SEST_REDBACK \
fit on the Apaches, the A-10s, the MQ-9s, \
the Seahawks and the RAAF Hornets.

[Compatibility]
ApproximateVersion=0.8.7
"""


def _section(text, name):
    """(header start, body start, body end) of [name], or None. A body runs to
    the next line opening with '[', the files' '[---- ... ----]' banners
    included, as the game reads them."""
    m = re.search(rf"^\[{re.escape(name)}\][^\n]*\n", text, re.M)
    if not m:
        return None
    nxt = re.compile(r"^\[", re.M).search(text, m.end())
    return m.start(), m.end(), nxt.start() if nxt else len(text)


_COMMENT = re.compile(r";|//|#")


def _ini_values(text, key, section=None):
    """Every value of `key` in an ini text, as the game's IniHandler reads a
    line (ReadFileToIni IL_0093-IL_01a2, separators from its .cctor): cut at
    the first ';', '//' or '#', trimmed, split on '=', the key and each later
    piece trimmed and the pieces joined again with '='. In any section, or
    only under [section] when one is named, matched with case as the game's
    section table is (IniHandler.open IL_0247 builds it with no comparer)."""
    out, current = [], None
    for raw in text.splitlines():
        line = _COMMENT.split(raw, maxsplit=1)[0].strip()
        head = re.match(r"\[(.+)\]", line)
        if head:
            current = head.group(1)
            continue
        parts = line.split("=")
        if (len(parts) >= 2 and parts[0].strip().lower() == key.lower()
                and section in (None, current)):
            out.append("=".join(p.strip() for p in parts[1:]))
    return out


def _directive_paths(text, directive):
    """The paths a file's `#!extend`, `#!prepend`, `#!alias` or `#!copy`
    lines name, lower case, with '/' and a `.ini`, for check_gps_receiver().

    The game reads all four more narrowly. IniHandler.ScanForModifierFiles
    (IL_00da-IL_0298) reads #!extend and #!prepend from every .ini in an
    enabled folder and its subfolders: each line trimmed, up to the first
    line opening '['; from one opening '#!prepend' or '#!extend' (with case)
    that word is taken out wherever it stands, the rest trimmed and split on
    ','; each piece is trimmed, '\\' becomes '/', and the result is matched
    without case against the stubbed file's path in its folder
    (GetModifierFiles). ReadFileToIni (IL_0042-IL_0093) takes the rest of an
    '#!alias' line the same way, as one name, from any line. ReadCopyDirectives
    reads '#!copy' (without case, then a space or the line's end) from the
    lines before the first section, split on ',' and trimmed, '\\' to '/';
    CollectCopyFiles finds each through the load order (FileManager.GetFile)
    and adds that file's own #!copy sources in turn. open() reads the
    #!extend stubs, the file's own keys, its #!copy sources (IL_0311-IL_0353),
    its #!prepend stubs (IL_035b-IL_039c) and its #!alias base
    (IL_039d-IL_03d0), in that order, and a key already read is never
    replaced. None of them cuts a comment off, so
    "#!extend ammunition/usn_agm-84n.ini ; fix" names a file no folder has,
    and the game extends nothing with it.

    This reads every line, each directive in any case, splits every one on
    ',' and cuts each name at the first ';', '//' or '#', as a key line is
    cut. A file the game reads cannot slip past it, and one that a stray
    comment keeps from loading is held to the same rule: one edit makes it
    live.
    """
    out = []
    if directive.lower() not in text.lower():
        return out
    for line in text.splitlines():
        m = re.match(rf"\s*{re.escape(directive)}(.*)", line.lstrip("\ufeff"), re.I)
        if not m:
            continue
        for name in re.sub(re.escape(directive), "", m.group(1), flags=re.I).split(","):
            name = _COMMENT.split(name, maxsplit=1)[0].strip().replace("\\", "/").lower()
            if name:
                out.append(name if name.endswith(".ini") else name + ".ini")
    return out


def check_gps_receiver(root=ROOT):
    """Stop unless every [GPS_Receiver] in the export can guide a radio-command
    round. U.S. Navy 2027 (which this pack already needs for usn_agm-84n)
    defines it, and so do three other mods; the game merges systems/sensors.ini
    key by key, so each copy must hold: Kind=Radar, Type=Targeting (stays on,
    see P8_GUIDANCE), Mode=RadioCommand, WeaponChannels above 0, and not
    DatalinkGuidance=True, which would refuse a round that is not datalink
    (SensorSystem.CanGuideAmmo). The SEST packs' sensors.ini copies are held
    to the same.

    And stop unless every copy of the Harpoon lets that sensor guide it.
    SensorSystem.CanGuideAmmo (IL_001c-IL_003e) also returns false when the
    round's CompatibleGuidanceSystems list is not empty and does not hold the
    sensor's SystemName. AmmunitionParameters.loadWeaponParameters
    (IL_0528-IL_0582) reads that key from [Guidance], splits it on commas
    without trimming, and empties it only when the value itself is empty. So
    every copy of ammunition/usn_agm-84n.ini in the export or a SEST pack,
    every file in them whose #!extend or #!prepend names it (in any folder:
    U.S. Navy 2027 keeps its stubs in ammunition_overwrite/), and every file
    one of those names by #!alias or #!copy, must write no such value or one
    whose comma-separated names include GPS_Receiver exactly. The key is
    checked in any section of the file, not only [Guidance]. An #!alias base
    or #!copy source is checked unless the file that names it writes the key
    under [Guidance] itself, where its own value wins. #!alias bases are
    followed four deep, as build_pack.chain_owners does; #!copy sources as
    far as they go, as CollectCopyFiles does. Every copy of a named file is
    read, not only the copy the load order picks, and the bases and sources
    of stubs and bases are followed too, though the game follows only the
    file's own: a superset, so a list cannot reach the Harpoon unread."""
    owners = []
    for f in sorted([*(root / "mods-source").glob("*/systems/sensors.ini"),
                     *(root / "integration").glob("*/SEST_*/systems/sensors.ini")]):
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        span = _section(text, GPS_SENSOR)
        if not span:
            continue
        body = text[span[1]:span[2]]

        def key(k):
            m = re.search(rf"^{k}=([^/\s]+)", body, re.M)
            return m.group(1) if m else ""

        if ((key("Kind"), key("Type"), key("Mode")) != ("Radar", "Targeting", "RadioCommand")
                or not key("WeaponChannels").isdigit() or int(key("WeaponChannels")) < 1
                or key("DatalinkGuidance").lower() == "true"):
            sys.exit(f"{f.relative_to(root)}: [{GPS_SENSOR}] is no longer a radio-command "
                     "channel - re-check the P-8 Harpoon guidance link")
        owners.append(f.parts[-3])
    if P8_GUIDANCE["usn_p8_2027.ini"][0] not in owners:
        sys.exit(f"U.S. Navy 2027 no longer defines [{GPS_SENSOR}] - the P-8 Harpoon "
                 "guidance link has no channel")

    harpoon = f"ammunition/{REPLACE}.ini"
    files = {}   # path in its folder, lower case -> every copy, mods then SEST packs
    bases = [d for d in sorted((root / "mods-source").glob("*")) if not d.name.startswith("_")]
    bases += [*sorted((root / "integration").glob("*/SEST_*")),
              root / "mods-source" / "_vanilla" / "original"]
    for base in (b for b in bases if b.is_dir()):
        for f in sorted(base.rglob("*.ini")):
            files.setdefault(f.relative_to(base).as_posix().lower(), []).append(f)
    if harpoon not in files:
        sys.exit(f"nothing defines {harpoon} - the P-8 Harpoon has no round")

    def text_of(f):
        return f.read_text(encoding="utf-8-sig", errors="replace")

    def extends_it(f):
        text = text_of(f)
        return any(p in (harpoon, f"{REPLACE}.ini")
                   for d in ("#!extend", "#!prepend") for p in _directive_paths(text, d))

    queue = [(f, 0, "") for f in files[harpoon]]
    queue += [(f, 0, "") for rel in sorted(files) if rel != harpoon
              for f in files[rel] if extends_it(f)]
    seen = set()
    while queue:
        f, depth, via = queue.pop(0)
        if f in seen:
            continue
        seen.add(f)
        text = text_of(f)
        for value in _ini_values(text, "CompatibleGuidanceSystems"):
            if value and GPS_SENSOR not in value.split(","):
                sys.exit(f"{f.relative_to(root)}{via}: CompatibleGuidanceSystems={value} "
                         f"does not name {GPS_SENSOR}, so the game will not let it guide "
                         f"{REPLACE} - re-check the P-8 Harpoon guidance link")
        if _ini_values(text, "CompatibleGuidanceSystems", "Guidance"):
            continue
        for directive, what, deeper in (("#!alias", "#!alias base", 1),
                                        ("#!copy", "#!copy source", 0)):
            if depth + deeper > 4:
                continue
            for name in _directive_paths(text, directive):
                if "/" not in name:
                    name = f"{f.parent.name.lower()}/{name}"
                queue += [(base, depth + deeper, f" (the {what} of {f.relative_to(root)})")
                          for base in files.get(name, [])]


def link_gps(text, name):
    """The P-8's wing pylons (WeaponSystem2, the WingHardpoint that hangs the
    AntiShip Harpoons) link a GPS_Receiver as the radio-command channel;
    usn_p8 gets the sensor first, as [SensorSystem6] after its FLIR. The link
    goes at the top of [WeaponSystem2], replacing any it had, exactly as on
    the owner's PC (GPT's PR #50 dist). Stops if the file is not the shape
    expected."""
    _mod, had, links = P8_GUIDANCE[name]

    def stop(why):
        sys.exit(f"{name}: {why} - upstream changed, re-check the Harpoon guidance link")

    fit = _section(text, "WeaponSystem2AntiShip")
    if not fit or len(re.findall(rf"^Station[1-4]={re.escape(REPLACE)}\s*$",
                                 text[fit[1]:fit[2]], re.M)) != 4:
        stop(f"[WeaponSystem2AntiShip] no longer hangs four {REPLACE}")
    if not had:
        # usn_p8 has five sensors and no GPS: add U.S. Navy 2027's as the sixth.
        if re.search(rf"^SystemName={GPS_SENSOR}\s*$", text, re.M):
            stop(f"it carries a {GPS_SENSOR} of its own now; link that, do not add one")
        text, k = re.subn(r"^NumberOfSensorSystems=5([ \t]*)$", r"NumberOfSensorSystems=6\1",
                          text, count=1, flags=re.M)
        flir = _section(text, "SensorSystem5")
        if k != 1 or not flir or _section(text, "SensorSystem6"):
            stop("expected NumberOfSensorSystems=5 and [SensorSystem1-5]")
        text = text[:flir[2]] + GPS_BLOCK + text[flir[2]:]
    gps = _section(text, "SensorSystem6")
    if not gps or not re.search(rf"^Type=Radar\s*\n(?:[^\[\n][^\n]*\n)*?SystemName={GPS_SENSOR}\s*$",
                                text[gps[1]:gps[2]], re.M):
        stop(f"[SensorSystem6] is not a Type=Radar {GPS_SENSOR}")
    pylons = _section(text, "WeaponSystem2")
    body = text[pylons[1]:pylons[2]] if pylons else ""
    if not re.search(r"^SystemName=WingHardpoint\s*$", body, re.M):
        stop("[WeaponSystem2] is not the WingHardpoint")
    linked = [v.strip() for v in re.findall(r"^AssociatedSensors=([^\n]*)$", body, re.M)]
    if (re.search(r"^(?:NumberOfAssociatedSensors|AssociatedSensor\d+)=", body, re.M)
            or linked != ([",".join(had)] if had else [])):
        stop(f"its wing pylons link {linked or 'nothing'}, expected {had or 'nothing'}")
    body = re.sub(r"^AssociatedSensors=[^\n]*\n", "", body, flags=re.M)
    body = (f"NumberOfAssociatedSensors={len(links)}\n"
            f"AssociatedSensors={','.join(links)}\n" + body)
    return text[:pylons[1]] + body + text[pylons[2]:]


def main():
    if not (ROOT / "mods-source" / "3606774881" / "ammunition" / f"{REPLACE}.ini").exists():
        sys.exit(f"{REPLACE} not found - U.S. Navy 2027 must be exported first")
    check_gps_receiver()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
    print("SEST_Allied_Fixes")

    for _mod, name, why in RETIRED:
        stale = OUT / "aircraft" / name
        if stale.exists():
            stale.unlink()
            print(f"    removed aircraft/{name} - {why}")

    built = 0
    for mod, name in TARGETS:
        src = ROOT / "mods-source" / mod / "aircraft" / name
        dst = OUT / "aircraft" / name
        if not src.exists():
            if dst.exists():
                dst.unlink()
                print(f"    removed stale aircraft/{name} (upstream no longer exported)")
            print(f"  {name}  SKIPPED - {mod} not exported")
            continue
        text = src.read_text(encoding="utf-8-sig")
        n = len(re.findall(rf"^Station\d+={re.escape(MISSING)}\s*$", text, re.M))
        if not n:
            sys.exit(f"{name}: no {MISSING} station lines left - upstream fixed it, "
                     f"drop this target")
        out = re.sub(rf"^(Station\d+=){re.escape(MISSING)}(\s*)$", rf"\g<1>{REPLACE}\g<2>",
                     text, flags=re.M)
        if MISSING in out:
            sys.exit(f"{name}: {MISSING} still present after substitution")
        extra = ""
        if name in P8_GUIDANCE:
            out = link_gps(out, name)
            extra = f", wing pylons linked to a {GPS_SENSOR} for the Harpoon"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out, encoding="utf-8")
        print(f"  aircraft/{name}  ({n}x {MISSING} -> {REPLACE}{extra})")
        built += 1

    # The P-8s whose stations are already right upstream - usn_p8_2027 since
    # the 2026-09-20 export - ship for the Harpoon guidance link alone; every
    # other line is upstream's.
    for name, (mod, _had, _links) in P8_GUIDANCE.items():
        if any(name == target for _m, target in TARGETS):
            continue                        # linked above, after its station fix
        src = ROOT / "mods-source" / mod / "aircraft" / name
        dst = OUT / "aircraft" / name
        if not src.exists():
            if dst.exists():
                dst.unlink()
                print(f"    removed stale aircraft/{name} (upstream no longer exported)")
            print(f"  {name}  SKIPPED - {mod} no longer ships it")
            continue
        text = src.read_text(encoding="utf-8-sig")
        if MISSING in text:
            sys.exit(f"{name}: {MISSING} is back upstream - add it to TARGETS again")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(link_gps(text, name), encoding="utf-8")
        print(f"  aircraft/{name}  (wing pylons linked to its {GPS_SENSOR} for the Harpoon)")
        built += 1

    # The P-8's squadron flags. 3602046770 writes Nation=New Zealand for its
    # No. 5 Squadron RNZAF livery and Nation=South Korea for its ROKN one,
    # but the game's nation keys have no spaces (language_en/nations.ini:
    # NewZealand, South_Korea; Settings_UI_General.ini maps those keys to the
    # flag art). An unknown key shows no flag, which is what the RNZAF
    # Poseidons of the Southern Reach campaign did. Only the Nation= values
    # change; every livery, serial and emblem line is upstream's.
    sq_src = ROOT / "mods-source" / "3602046770" / "aircraft" / "usn_p8_squadrons.ini"
    sq_dst = OUT / "aircraft" / "usn_p8_squadrons.ini"
    nations_ini = ROOT / "mods-source" / "_vanilla" / "original" / "language_en" / "nations.ini"
    if not sq_src.exists():
        if sq_dst.exists():
            sq_dst.unlink()
            print("    removed stale aircraft/usn_p8_squadrons.ini (upstream gone)")
        print("  usn_p8_squadrons.ini  SKIPPED - P-8 mod not exported")
    else:
        game_keys = {l.split("=", 1)[0].strip().lower()
                     for l in nations_ini.read_text(encoding="utf-8-sig").splitlines()
                     if "=" in l}
        spelled = {"new zealand": "NewZealand", "south korea": "South_Korea"}
        text = sq_src.read_text(encoding="utf-8-sig")
        fixed = []

        def respell(m):
            value = m.group(2).strip()
            key = spelled.get(value.lower())
            if key:
                fixed.append(f"{value} -> {key}")
                return f"{m.group(1)}{key}{m.group(3)}"
            return m.group(0)

        text = re.sub(r"^(Nation=)([^\r\n/#;]*?)(\s*(?://.*|#.*|;.*)?)$", respell, text, flags=re.M)
        left = [v for v in re.findall(r"^Nation=([^\r\n/#;]*)", text, re.M)
                if v.strip().lower() not in game_keys]
        if left:
            sys.exit(f"usn_p8_squadrons.ini: nation(s) the game has no key for: {left}")
        if not fixed:
            sys.exit("usn_p8_squadrons.ini: every Nation= is already a game key - "
                     "upstream fixed it, drop this patch")
        sq_dst.parent.mkdir(parents=True, exist_ok=True)
        sq_dst.write_text(text, encoding="utf-8")
        print(f"  aircraft/usn_p8_squadrons.ini  ({'; '.join(fixed)})")

    # HMS Ocean vs the Apache: her own sister hulls in the same mod
    # (rn_lph_ocean_asw_00 and _asw_13) already list uk_ah_mk_1 - the British
    # Army Apache AH1 that really flew from Ocean off Libya in 2011 - but the
    # base rn_lph_ocean only ever got the Lynx. One appended id fixes it.
    src = ROOT / "mods-source" / "3599752717" / "vessels" / "rn_lph_ocean.ini"
    dst = OUT / "vessels" / "rn_lph_ocean.ini"
    if not src.exists():
        if dst.exists():
            dst.unlink()
            print("    removed stale vessels/rn_lph_ocean.ini (upstream gone)")
        print("  rn_lph_ocean.ini  SKIPPED - Modern British Navy not exported")
    else:
        text = src.read_text(encoding="utf-8-sig")
        if "uk_ah_mk_1" in text:
            sys.exit("rn_lph_ocean.ini: upstream now supports the Apache - drop this fix")
        # APPEND to whatever the line holds rather than matching an expected
        # value: the 2026-09-20 export added rn_sea_king_hc4 to it, which an
        # exact match read as "upstream changed, stop". The fix is still
        # needed (no uk_ah_mk_1 anywhere in the file), so the patch now adds
        # the Apache to the list as it finds it and prints what it appended to.
        lines = re.findall(r"^AircraftSupported=([^\n]*?)\s*$", text, re.M)
        if len(lines) != 1:
            sys.exit(f"rn_lph_ocean.ini: expected 1 AircraftSupported line, found {len(lines)}")
        had = lines[0]
        text, n = re.subn(r"^AircraftSupported=[^\n]*?\s*$",
                          f"AircraftSupported={had},uk_ah_mk_1", text, flags=re.M)
        if n != 1:
            sys.exit(f"rn_lph_ocean.ini: AircraftSupported substitution hit {n} lines")
        # SEST Replenishment At Sea owns the launcher fix for every modern hull,
        # but it cannot touch this one - THIS pack ships rn_lph_ocean.ini, and
        # two packs shipping different bytes at one path is an unconditional
        # consolidation failure. So the transform is imported and applied here.
        text, reloadable = make_reloadable(text)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        print(f"  vessels/rn_lph_ocean.ini  (+uk_ah_mk_1 Apache AH1 supported, "
              f"{reloadable} launcher(s) made reloadable for RAS)")

    # AGR-30 Redback: SEST's one upgraded 70mm guided rocket. The decision of
    # 19 Oct 2026 retired the 8 nm laser APKWS II-ER (its rocket, its pod and
    # the Ocean Apache's SEST_APKWS_ER fit) and asked for this one round,
    # everywhere: 30 nm and a rocket's boost then a slower cruise. It stays
    # dts_apkws-ii - the proven in-pod rocket it was rebased onto after two
    # freezes, the weapon pack's counter-drone APKWS - with the minimum deltas:
    # The second 19 Oct request extends the visible motor to ten seconds and
    # asks for gentler slowdown, an approximately 45-degree final descent and
    # some terminal speed pickup. Legacy phase caps keep the fictional slow
    # cruise without modelling an unpowered 70mm rocket's real-world stall.
    # AS-4 demonstrates TerminalVelocity and Deceleration (see the slow-down
    # below for the value).
    # A 6562-ft loft over 1.1 horizontal NM gives about 44.5 degrees to a
    # sea-level target. IgnoreHeightDifferenceForTargetDist is essential to
    # that geometry. This is not a verified fixed-pitch control: terrain,
    # target height, short shots and target motion change the approach.
    # AIM-54A's timed SustainerEffect supplies the ten-second visible motor,
    # without an everlasting InFlightEffect or a new flame in terminal.
    # Fire and forget (23 Oct 2026). The 19 Oct follow-up made the round radio
    # command (MidCourseCorrection=1) for retargeting, and radio command needs
    # a guidance channel: a radar or command link the launching hardpoint
    # names in AssociatedSensors=. The Seahawks name none (the RAN MH-60R's
    # only radar, APS-147, has no weapon channels), nor do the A-10A/C - on
    # the evidence, why the game listed the AGR-30 and never launched it in
    # the owner's 23 Oct report, an attack ordered on a boat. The stock
    # game's radio-command stores come with their channel (the AS-2's Rubin
    # radar, the AGM-12B's ARW-77), as does the MQ-9's GBU-49 (the author's
    # guidance pod). So the round is the donor's MidCourseCorrection=0
    # again, like the Hellfire L the MH-60R already fires (active radar,
    # Ka-band, 11 kW), and the GBU-53 that US Naval Aviation's BRU-61
    # container holds: no channel, on any carrier. Retargetable stays, as on
    # six of the collection's MidCourseCorrection=0 rounds (the ROK
    # Hyunmoo-4-2 and HGV are active radar too); whether the game retargets
    # one without a link, play shows.
    # Seen firing (23 Oct 2026, second report, on 57375598): the RAN MH-60R
    # fired it from its pods, so MidCourseCorrection=0 stays. The owner also
    # saw a shorter boost than on the build they played before it (71bd3004,
    # the 19 Oct follow-up's round; the last recorded Workshop upload,
    # e7b32f11, is older) and asked for a realistic slow-down to the cruise
    # speed.
    # Game rules this profile rests on (Sea Power 0.8.7, read from the game's
    # code on 23 Oct 2026; ApplyKinematics=False, the game's simpler speed
    # model):
    # - The flame is a timer: the SustainerEffect shows from launch for
    #   SustainerAccelerationTime (10 s), whatever the round is doing.
    # - Speed has a target per stage: MaxVelocity while the round launches
    #   and turns onto its bearing, MaxLoftVelocity through the climb and
    #   the whole cruise, TerminalVelocity from TerminalApproachDist in.
    #   Above the target the speed falls in a straight line at Deceleration
    #   x 19.05 kt/s; below it the motor pushes it up at Acceleration x
    #   22.9 kt/s, never past the target.
    # - Fired from an aircraft, the motor works only with AccelerationTime=6,
    #   the game's own default (the 19 Oct 0.01 gave no thrust at all, so the
    #   round kept roughly its launcher's speed).
    # So: a hard run-up toward 450 kt as it leaves the pod, a straight-line
    # bleed of about 4.8 kt/s to the 150 kt climb-and-cruise (450 to 150 kt
    # in about a minute) while the flame burns its ten seconds, and a pick-up
    # to 220 kt at TerminalApproachDist. How fast it is when the run-up ends
    # depends on how long the game's launch stages last, which the play test
    # shows. The 8 NM TerminalApproachDist of 57375598 put every shot inside
    # 8 NM straight into terminal approach, which holds its height: no climb.
    # 2 NM, 71bd3004's value, restores the 2 km climb on every shot from
    # about 3.6 NM.
    for stale in ("sest_apkws_er.ini", "sest_agr-20er.ini"):
        if (OUT / "ammunition" / stale).exists():
            (OUT / "ammunition" / stale).unlink()
            print(f"    removed ammunition/{stale} - the APKWS II-ER is retired")
    rb_src = ROOT / "mods-source" / "3760871384" / "ammunition" / "dts_apkws-ii.ini"
    pod_src = ROOT / "mods-source" / "3425450153" / "ammunition" / "usn_agr-20b_apache.ini"
    for need in (rb_src, pod_src):
        if not need.exists():
            sys.exit(f"{need.relative_to(ROOT)} missing - export it first")
    rb = rb_src.read_text(encoding="utf-8-sig", errors="replace")
    swaps = [
        # Surface attack is the primary AI job; retain counter-drone eligibility.
        # The laser donor had no active-radar transmitter or target-height band.
        (r"^TargetType=AAW[^\n]*", "TargetType=ASuW"),
        (r"^SecondaryTargetType=ASuW[^\n]*", "SecondaryTargetType=AAW"),
        (r"^GuidanceType=5\b", "GuidanceType=3"),
        (r"^MidCourseCorrection=0[^\n]*", "MidCourseCorrection=0  // fire and forget: needs no guidance channel on the carrier (23 Oct 2026)"),
        (r"^SeekerPassiveRange=6\.0[^\n]*", "SeekerPassiveRange=0\nSeekerActiveRange=35\nSeekerGain=50\nFrequency=Ka-Band\nPeakPower=11.0\nMinAttackAltitude=0\nMaxAttackAltitude=20000\nSeekerReliability=0.99\nTargetMemory=True\nRetargetable=True\nSelfDestructAfterTargetGone=False"),
        (r"^MaxLaunchRange=6\b", "MaxLaunchRange=30"),
        (r"^MaxLoftAngle=5\.0[^\n]*", "MaxLoftAngle=35.0"),
        (r"^MaxLoftAlt=1500[^\n]*", "MaxLoftAlt=6562  // feet: approximately 2 km\nMaxLoftVelocity=150  // climb and cruise speed target, knots"),
        (r"^TerminalApproachDist=100[^\n]*", "TerminalApproachDist=2.0  // seeker on 2 NM out, after the 2 km climb (23 Oct 2026)"),
        (r"^TerminalDiveDistance=2[^\n]*", "TerminalDiveDistance=1.1\nTerminalVelocity=220  // legacy terminal phase target, knots\nIgnoreHeightDifferenceForTargetDist=True"),
        (r"^MaxVelocity=2000[^\n]*", "MaxVelocity=450  // launch run-up speed target, knots\nApplyKinematics=False\nMaxFlightTime=1500\nTimeLimited=True"),
        (r"^AccelerationTime=1[^\n]*", "AccelerationTime=6  // the game's default: the motor also works when an aircraft fires it"),
        (r"^Acceleration=200[^\n]*", "Acceleration=12  // about 275 kt/s run-up\nDeceleration=0.25  // about 4.8 kt/s bleed to the 150 kt cruise (23 Oct 2026)\nSustainerAccelerationTime=10  // the flame's ten seconds\nSustainerAcceleration=8"),
        (r"^MaxTurnRate=50\.0[^\n]*", "MaxTurnRate=20.0  // soften the nose-over while retaining target correction"),
        (r"^KillProbability=0\.6\b", "KillProbability=0.95"),
        (r"^SeekerFOV=15\b", "SeekerFOV=60"),
        (r"^SeekerGimbalFOV=90\b", "SeekerGimbalFOV=120"),
        (r"^BoosterEffect=[^\n]*\nBoosterEffectPosition=[^\n]*\n", ""),
        (r"^InFlightEffectClass=[^\n]*\nInFlightEffectPosition=[^\n]*\nInFlightEffectStartTime=[^\n]*",
         "SustainerEffect=effects/weapons/emitters/missile_sustainer_small_effect\n"
         "SustainerEffectPosition=0,0,-0.02\nSustainerEffectStartTime=0"),
    ]
    for pat, rep in swaps:
        rb, k = re.subn(pat, rep, rb, count=1, flags=re.M)
        if k != 1:
            sys.exit(f"dts_apkws-ii: {pat} matched {k} times - upstream changed")
    # Preserve the donor's target classes, including mobile land targets.
    for key in (r"TargetType=ASuW", r"SecondaryTargetType=AAW",
                r"LandAttackCapability=All", r"TerminalAlt=Maintain"):
        if not re.search(rf"^{key}\b", rb, re.M):
            sys.exit(f"dts_apkws-ii: {key} changed upstream - re-check the Redback profile")
    (OUT / "ammunition").mkdir(parents=True, exist_ok=True)
    (OUT / "ammunition" / "sest_agr-30.ini").write_text(
        "# SEST AGR-30 Redback - fictional 30 nm guided rocket.\n"
        "# Ten-second flame / run-up toward 450 kt / straight-line bleed to a 150 kt climb and cruise / 220 kt terminal target.\n"
        "# 2 km loft and 1.1 horizontal NM dive start approximate a 45-degree surface attack.\n"
        "# Active radar seeker, fire and forget: no carrier guidance channel needed. Playtest required.\n"
        + rb, encoding="utf-8")
    rbpod, k = re.subn(r"^Ammunition=usa_apkws_2_m282\s*$", "Ammunition=sest_agr-30",
                       pod_src.read_text(encoding="utf-8-sig", errors="replace"), flags=re.M)
    if k != 1:
        sys.exit("usn_agr-20b_apache: Ammunition line changed upstream (Redback pod)")
    (OUT / "ammunition" / "sest_agr-30_pod.ini").write_text(
        "# SEST LAU-68 pod loaded with the AGR-30 Redback.\n" + rbpod, encoding="utf-8")
    # The 19-tube pod, for a single pylon: the game's own LAU-3/A (its model
    # ships with the game, so the pod needs no mod) with the Redback in place
    # of the Hydra, and a salvo of two like the 7-tube pod's - eight was for
    # unguided rockets spread over an area. The Euromod RAN mod's
    # usn_lau-3a_APKWS already flies 19 guided rockets from this pod.
    lau3 = (ROOT / "mods-source" / "_vanilla" / "original" / "ammunition"
            / "usn_lau-3a.ini").read_text(encoding="utf-8-sig", errors="replace")
    for pat, rep in ((r"^Ammunition=usn_hydra\b", "Ammunition=sest_agr-30"),
                     (r"^SalvoFireAmount=8\b", "SalvoFireAmount=2")):
        lau3, k = re.subn(pat, rep, lau3, count=1, flags=re.M)
        if k != 1:
            sys.exit(f"usn_lau-3a: {pat} matched {k} times - the game changed the pod")
    (OUT / "ammunition" / "sest_agr-30_pod19.ini").write_text(
        "# SEST LAU-3/A pod loaded with 19 AGR-30 Redbacks, a salvo of two.\n" + lau3,
        encoding="utf-8")

    lang = OUT / "language_en"
    lang.mkdir(parents=True, exist_ok=True)
    (lang / "ammunition_names.ini").write_text(
        "[AmmunitionNames]\n"
        "sest_agr-30=AGR-30,Redback,GFFAR,"
        "What-if evolution of the 70mm guided rocket family: the AGR-30 "
        "Redback adds fire-and-forget active radar homing out to 30 nautical "
        "miles, its seeker searching from 2 nautical miles out. It leaves the "
        "pod hard, climbs to approximately 2 km under a ten-second motor "
        "flame and slows steadily to a 150-knot cruise. The final descent "
        "is tuned for roughly 45 degrees against surface targets, with a "
        "220-knot terminal speed target. This is an experimental game profile. "
        "Eligible against aircraft, drones, ships and land targets. Its slow "
        "cruise is intended for surface targets and slow aircraft. Same "
        "airframe and warhead as the APKWS II.\n",
        encoding="utf-8")
    (lang / "loadout_names.ini").write_text(
        "[LoadoutNames]\nSEST_REDBACK=SEST Redback Strike (AGR-30 guided rockets)\n",
        encoding="utf-8")
    print("  Redback: sest_agr-30 (30 nm, boost + cruise, loft and dive, surface first), "
          "its LAU-68 and LAU-3 pods")

    # The fit, on every carrier whose file this pack ships. Each clones a fit
    # it already flies and puts Redback pods on the pylons named (common/
    # redback.py). The A-10C+, F-16CM and US Super Hornets are other SEST
    # packs' files and get the same fit from their own builders. The 19-tube
    # pod goes on a single pylon, on the airframe's own mount for a store its
    # size; the 7-tube stays where a rack hangs several (the A-10's TERs, the
    # Hornets' twin mounts, the MH-60R's M299 Hellfire rails), on the MQ-9's
    # light pylons and on the S-70B-2's Penguin arm, whose gap between the
    # Hellfire rails a 19-tube overfills.
    ROLLOUT = [
        # Apaches: four 19-tube pods on the mod's own LAU-3 mount, as its
        # Default fit hangs them.
        ("3425450153", "uk_ah_mk_1.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usa_ah-64a.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usa_ah-64d.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usa_ah-64e.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3425450153", "usn_ah-64na.ini", "Strike", [("usn_agr-20b_apache", "pod19", 4, "LAU-3")]),
        ("3820759806", "adf_ah-64e.ini", "StrikePrecision",
         [("usn_agr-20b_apache", "pod19", 2, "LAU-3"), ("usn_lau-3a_APKWS", "pod19", 2)]),
        # A-10s: a 19-tube pod on each single outer pylon, on the 2,000 lb
        # bomb's mount (the files write MK-82's twice, the second about 20 m
        # below the wing); the TERs keep three or two 7-tube pods on their
        # own points.
        ("3459682829", "usa_a-10c.ini", "CAS1",
         [("usn_agr-20b", "pod19", 1, "MK-84", (3,)), ("usn_agr-20b", "pod", 4)]),
        ("3414146266", "usa_a-10a.ini", "CAS",
         [("usn_lau-68", "pod19", 2, "MK-84", (3, 4)), ("usn_lau-68", "pod", 2)]),
        # MQ-9s (23 Oct 2026): one 7-tube pod under each outer pylon, its
        # twin Hellfire launcher (agm-114_pyl_l/r) hidden. Hung on the
        # launcher's AGM-114 seat, two pods a side sat on the launcher's rail
        # points - the "pods on the Hellfire rails" the Seahawk had. The SEST
        # RedbackMQ9 mount is the centre of that seat: the author's Hellfire
        # height, which the ER's own AirToAir fit also uses for the AIM-9X it
        # hangs on that pylon with the launcher hidden. The inner pair keep
        # their 7-tube pods on the GBU-49's mount.
        ("3503670861", "usaf_mq-9a.ini", "Strike",
         [("uav_agm-114k", "pod", 2, "RedbackMQ9"), ("uav_gbu-49", "pod", 2)],
         dict(hide=("agm-114_pyl_l", "agm-114_pyl_r"),
              positions={"RedbackMQ9": "0,-0.001655,0.000803"})),
        ("3503670861", "usaf_mq-9_er.ini", "Strike",
         [("uav_agm-114k", "pod", 2, "RedbackMQ9"), ("uav_gbu-49", "pod", 2)],
         dict(hide=("agm-114_pyl_l", "agm-114_pyl_r"),
              positions={"RedbackMQ9": "0,-0.001655,0.000803"})),
        # Seahawks (23 Oct 2026). The MH-60R's M299 Hellfire launcher
        # (H60_Pylon114) has two rail points a side, upper (Stations 10/11)
        # and lower (12/13), each hanging two missiles on the TERAGM114 seat.
        # The owner's second report of the day, on 57375598, whose 19-tube
        # pods had taken the auxiliary tanks' Stations 1/2: tanks back, and
        # the AGR on the launcher in the Hellfires' place, not clipping it.
        # So the fit is the donor's - tanks on 1/2, the Penguin arm
        # (H60_Pylon119) hidden, the launcher drawn - with a 7-tube pod for
        # each of its eight Hellfires: 56 rounds. A side's four missile
        # points form a box 0.49 m across and 0.39 m deep. A LAU-68 (about
        # 0.24 m, and a Hellfire's length) fills it with room between pods;
        # a LAU-3 (0.41 m) cannot, and fewer, larger pods sat in the bottom
        # of the rack (27153767) or floated with the launcher hidden
        # (d9755f4e). The pod is fatter than a Hellfire, so on the Hellfire's
        # own seat its top would cut 3-7 cm into the rail. The SEST
        # RedbackM299 seat is TERAGM114 lowered 0.04 m, which brings the
        # pod's top to within about 3 cm of where the Hellfire's meets the
        # rail. No mesh is in the export: the loadout preview confirms it
        # (docs/playtest-20261023-redback.md), and the seat's height is the
        # one number to move.
        # The S-70B-2's Penguin hangs between the four Hellfire rails, 0.35 m
        # apart: the 7-tube pod is the Penguin's size, the 19-tube pod was
        # wider than the gap. Provisional: the launcher stays drawn, as in
        # the author's Penguin fit, so if the preview shows the pod inside it
        # the two S-70B-2 rows come out before the next upload.
        ("3606774881", "usn_mh-60r.ini", "AntiShipLateLongRange",
         [("usa_agm-114l_mm", "pod", 2, "RedbackM299"), ("usa_agm-114k_hh", "pod", 2, "RedbackM299")],
         dict(positions={"RedbackM299": "0.002461,-0.0004,0|-0.002405,-0.0004,0"})),
        ("3820759806", "ran_mh-60r.ini", "AntiShip",
         [("usa_agm-114l_mm", "pod", 2, "RedbackM299"), ("usa_agm-114k_hh", "pod", 2, "RedbackM299")],
         dict(positions={"RedbackM299": "0.002461,-0.0004,0|-0.002405,-0.0004,0"})),
        ("3403661005", "S-70B-2_Seahawk.ini", "AntiShip", [("knm_penguin_mk2", "pod", 1)]),
        ("3820759806", "ran_S-70B-2_Seahawk.ini", "AntiShip", [("knm_penguin_mk2", "pod", 1)]),
        # RAAF Hornets. The F/A-18A's CAS fit already flies the layout: wing
        # tanks, and two 7-tube pods on the pylon outboard of them (the twin
        # Zuni mount). The F/A-18F takes it from its long-range anti-ship
        # fit, whose wing and centreline tanks stay: two 7-tube pods on the
        # mid pylon (a twin mount at the A's spacing, which SEST adds), and a
        # 19-tube pod on the outboard pylon, on the bombs' outer mount.
        ("3820759806", "raaf_fa-18f.ini", "AntishipLongRange",
         [("usn_aim-9x", "pod19", 2, "GBU24A", (3, 4)), ("DateBased_AShM", "pod", 2, "RedbackTwin")],
         dict(positions={"RedbackTwin": "-0.004146,-0.001,0|0.004146,-0.001,0"})),
        ("3820759806", "raaf_fa-18a_2011.ini", "CAS", [("usn_lau-10a", "pod", 2)]),
    ]
    for mod, fname, donor, pylons, *opts in ROLLOUT:
        csrc = ROOT / "mods-source" / mod / "aircraft" / fname
        cdst = OUT / "aircraft" / fname
        if not csrc.exists():
            if cdst.exists():
                cdst.unlink()
            if fname == "usa_a-10c.ini":
                stale_sq = cdst.parent / "usa_a-10c_squadrons.ini"
                if stale_sq.exists():
                    stale_sq.unlink()
            print(f"  {fname}  SKIPPED - {mod} not exported")
            continue
        ct = csrc.read_text(encoding="utf-8-sig", errors="replace")
        extra = ""
        if fname == "uk_ah_mk_1.ini":
            # Upstream's Default fit names Station3 and Station4 twice - a
            # LAU-3 rocket pod AND a Brimstone on each inner pylon - so the
            # encyclopedia and the default loadout draw the pod and the
            # missiles on top of each other. Every other fit puts the rocket
            # pods on the outer pylons (Stations 1/2), and this one already
            # hides the outer missile rails for them, so the pods move there.
            ct, k = re.subn(r"(\[WeaponSystem1Default\][^\[]*?)"
                            r"^Station3=usa_lau-3a_apache\|LAU-3\n^Station4=usa_lau-3a_apache\|LAU-3\n",
                            r"\1Station1=usa_lau-3a_apache|LAU-3\nStation2=usa_lau-3a_apache|LAU-3\n",
                            ct, count=1, flags=re.M | re.S)
            if k != 1:
                sys.exit("uk_ah_mk_1: Default fit's doubled inner-pylon rocket pods not found - "
                         "upstream changed, re-check the overlap fix")
            extra = ", Default fit's doubled pods moved outboard"
        ct = add_redback(ct, fname, donor, pylons, **(opts[0] if opts else {}))
        if fname == "usa_a-10c.ini":
            # Two defects in the standard aircraft, repaired here because
            # this pack already ships the file. They are bugs, not the
            # upgrade: SEST A-10C+ carries the added sensors and AIM-9X on
            # a separate unit id, and applies these same two repairs from
            # integration/common/a10c.py so the pair cannot drift.
            ct = register_ir_head(ct, fname)
            sqsrc = ROOT / "mods-source" / mod / "aircraft" / "usa_a-10c_squadrons.ini"
            sq, was, defined = fix_squadron_count(
                sqsrc.read_text(encoding="utf-8-sig", errors="replace"), sqsrc.name)
            (cdst.parent / sqsrc.name).parent.mkdir(parents=True, exist_ok=True)
            (cdst.parent / sqsrc.name).write_text(sq, encoding="utf-8")
            extra = f", IR head registered, squadrons {was}->{defined}"
        cdst.parent.mkdir(parents=True, exist_ok=True)
        cdst.write_text(ct, encoding="utf-8")
        print(f"  aircraft/{fname}  SEST_REDBACK (donor {donor}){extra}")
        built += 1

    if not built:
        sys.exit("nothing built - no target mod is exported")
    # Use the collection's actual field-drone squad geometry and its tested
    # catapult/recovery positions, not a runway and hangars on hostile ground.
    # Keep only one fixed-wing lane and RQ-7 inventory. The donor also carries
    # unrelated one-way attack drones, a GPS sensor 3.5 km above its model and
    # an orphan third hit zone; none belongs in this reconnaissance section.
    drone_source = ROOT / "mods-source/3601891050/land_units/dronesquad705_1.ini"
    team = drone_source.read_text(encoding="utf-8-sig")
    edits = {
        "General": {"DisplayClassName": "RQ-7 field detachment", "DefaultCameraDistance": "0.15",
                    "MinCameraDistanceForeAft": "0.08", "MinCameraDistanceBroadside": "0.08"},
        "AirGroup": {"usn_rq7705": "Squadron1,2"},
        "FlightDeck": {"AircraftCapacity": "3", "NumberOfElevators": "1",
                       "NumberOfLaunchPoints": "1", "NumberOfRecoveryPoints": "1",
                       "NumberOfTaxiPaths": "2", "AircraftSupported": "usn_rq7705"},
        "SensorSystems": {"NumberOfSensorSystems": "1"},
        "SensorSystem1": {"MountPosition": "0,0.02,0"},
        "WeaponSystems": {"NumberOfWeaponSystems": "0"},
        "TargetingData": {"NumberOfTargetPoints": "2",
                          "TargetPointPosition1": "0,0.017,-0.0023",
                          "TargetPointPosition2": "0,0.003,-0.0023"},
    }
    drop = {"SensorSystem2", "WeaponSystem1", "WeaponMagazineMissile",
            "Elevator2", "LaunchPoint2", "RecoveryPoint2", "TaxiPath3", "TaxiPath4"}
    chunks = []
    for chunk in re.split(r"(?=^\[)", team, flags=re.M):
        match = re.match(r"^\[([^]\n]+)\]", chunk)
        section = match[1] if match else ""
        if section in drop:
            continue
        if section == "AirGroup":
            chunk = "[AirGroup]\n"
        if section == "Submodels":
            chunk = "[Submodels]\nSubModel1=net\n\n"
        for key, value in edits.get(section, {}).items():
            pattern = rf"^{re.escape(key)}=[^\n]*$"
            if re.search(pattern, chunk, re.M):
                chunk = re.sub(pattern, f"{key}={value}", chunk, flags=re.M)
            else:
                chunk = chunk.rstrip() + f"\n{key}={value}\n"
        if section == "TargetingData":
            chunk = re.sub(r"^TargetPoint(?:Position|AssociatedSystems|Priority)3=[^\n]*\n?", "", chunk, flags=re.M)
        chunks.append(chunk)
    (OUT / "land_units").mkdir(parents=True, exist_ok=True)
    team = ("# SEST RQ-7 field team. Model and launch/recovery layout from\n"
            "# FallschimJager705, Small and Medium-Sized UAV Series (3601891050).\n"
            "# Uses the subscribed mod's dronesquad assets; no mesh is redistributed.\n"
            + "".join(chunks))
    (OUT / "land_units/sest_uav_forward.ini").write_text(team, encoding="utf-8")
    # The new unit id needs its own companion variants file for the native
    # class/variant lookup. Do not inherit the donor's national air groups.
    # Missions supply their nation and two-aircraft custom air group.
    (OUT / "land_units/sest_uav_forward_variants.ini").write_text(
        "[General]\nAllVariantsAreOfSameNation=True\nNumberOfVariants=1\n\n"
        "[Default]\nNation=Australia\n\n[Variant1]\nNation=Australia\n",
        encoding="utf-8")
    (OUT / "language_en/land_units_names.ini").write_text(
        "[sest_uav_forward]\nType=RQ-7 field detachment\n"
        "Default=Forward UAV team,UAV team\n"
        "Variant1=Forward UAV team,UAV team\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
