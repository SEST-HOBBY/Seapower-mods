# Workshop refresh, 17 October 2026

Capture `7fdb7be8` on `chore/workshop-refresh-20261017`: Euromod - Modern Royal
Australian Navy (3820759806), newly subscribed, plus updates to the Euromod
Italian (Modern and Cold War), Scandinavian, South Korean, British and Main
packs. Merged into `feature/workshop-update-20261017`.

## 1. Euromod - Modern Royal Australian Navy

Version 1.0.0.1, posted 16 Oct, updated 17 Oct; requires Euromod Main, US
Naval Aviation and the French Helicopter Package, all in the collection.
Ships: Hobart, Anzac (eight hulls, each with an S-70B-2 and an MH-60R variant)
and a wartime Anzac, Canberra and Adelaide (amphibious, air assault and an
LHD-CV carrier conversion), Collins, the Adelaide FFG upgrade and a
Quickmatch-class future destroyer; about twenty RAAF, RAN and Army aircraft.

Its Hobart, Anzac, Canberra and Collins use the unit ids SEST's campaigns
use. Before this change SEST RAN Fleet's stand-ins (Hobart on the Spanish
F-100, Canberra on the Juan Carlos, Collins on the S-80) and the old Anzac
mod would have hidden all four. Decision (the user, 17 Oct): SEST moves onto
the mod's ships.

- `integration/ran-fleet/build_fleet.py`: the four are patches of the mod's
  files (`"euromod": True`). Kept from SEST: the RAN MH-60R air group
  (`usn_mh-60r` Squadron20, the one the rosters sell), AircraftSupported for
  both RAN Seahawks and the mod's own (`ran_mh-60r`, `ran_S-70B-2_Seahawk`),
  the Canberra's CH-53E and MV-22B, the reload flag, and HMAS names for
  Variant1..N. Dropped as redundant on these hulls: the NSM swap, Tomahawk
  refresh, Mk41 repair, combat-system and Phalanx swaps, and the stand-ins'
  variants files (the mod's carry real hull numbers and emblems). The NSM
  guidance check now reads a loadout's own block (`[WeaponSystem7Late]`):
  Hobart 10 NSM mounts across its fits, Anzac 2, each with a sensor.
- Variant numbering matches: the mod's Variant1-8 are FFH-150..157 in the
  same order, Hobart 1-3, Canberra 1-2 and Collins 1-6 as before, so no
  mission's named ship changes.
- Load order: directly above the Anzac Class Frigate mod, so its own Anzac
  variants win; catalog entry added (205 mods).
- Name Fixes: the pin on the old Anzac mod's "Frigate Helicopter" class
  name is retired; the winning name is the mod's "Anzac-class, Anzac".

## 2. Dated fits

`pick_loadout` wrote `Default` when a mission named no fit. The mod's ships
date their fits (`LoadoutDate_<fit>=year`, the stock mechanism), and Default
is the oldest: the Anzac's carries no NSM. The builder now takes the latest
fit in service by the mission's year, ties to the first offered. Across all
SEST missions: Anzac -> AMCAP Late (59 placements), Hobart -> Late (21),
Collins -> Phase 6 Modernisation (10), Canberra -> AmphibiousAssault (its
only fit), and four others in 2028 missions -> Late (two Udaloys, an Italian
FREMM, an Adelaide short hull). The campaign gates (opening ranges, closure,
pacing, reach) pass on the new fits. Test added.

## 3. Checks

Gates 11 of 12 (`check_inventory`, the four CR-stripped mods); campaign
tests 201, tool tests 105.

Before the next upload: add Euromod - Modern Royal Australian Navy
(3820759806) to collection 3812390790 and to the SEST item's Required Items.

## 4. Second capture: Steelfin and the afternoon updates

Capture `908e1a70` on `chore/workshop-refresh-20261017b` (taken 15:35, after
the player started and quit the game once): Steelfin (3820576916), newly
subscribed, and fresh exports of the F-35C Alt. Loadouts, the Euromod
Anchorchain Expansion Pack, Main Pack, British, South Korean and RAN packs and
the PLAAF Aircraft Pack. U.S. Navy 2027 Capabilities (3606774881) is unchanged
in the export: Steam still dates it 10 Oct, so whatever update the Workshop
showed had not touched its config files.

- **Steelfin** (19 files, no DLL, no dependencies). The Anduril interceptor
  as its own mod: the ship round `usn_steelfin`, the air-launched
  `usn_steelfin_air`, a Steelfin cruiser (`usn_cg_steelfin`, a copy of the
  vanilla Bunker Hill with Steelfin in every Mk 41 magazine, in service
  2027-2100), a land container launcher with its own radar
  (`usa_steelfin_launcher`), its weapon and radar systems and a test
  scenario. The two rounds were already shipped by five mods (Saronic
  Corsair and Anduril Maritime Drones the ship round; YF-23, FQ-44 Fury and
  MV-75 the air round); this mod's copies differ from theirs only in the
  three camera distances, and its material file is byte-identical. Placed
  directly above Saronic Corsair ASV so its own copies win; catalogued (206
  mods); `check_mod_conflicts` finds nothing SEST fields. No SEST mission
  places its units, so the campaign coverage rule carries a written excuse
  for it, as for Anduril Maritime Drones. The world campaign's buy list
  does not take the Steelfin cruiser: its unit and variants files are
  `#!copy` overlays of the Bunker Hill, which the arsenal reader does not
  follow, so it finds no unit type or nation in them.
- **Steelfin loadout name.** SEST Collection Fixes named the YF-23, Fury and
  MV-75 "Steelfin" fit "Steelfin (air-defence interceptor)" on 16 Oct,
  because no mod named it. The Steelfin mod now names it "Steelfin". The
  entry stays (none of the three aircraft mods requires the Steelfin mod, so
  without it the picker would read MISSING TEXT) but now carries the
  author's text, "Steelfin".
- **F-35C Alt. Loadouts** (3607989779). Only rounds changed: AIM-120D-3 and
  AIM-260A get more drag and a terminal loft, the GBU-31(V)4 an impact fuze,
  a very large impact and an 8 m error radius, and the three JDAMs gain
  frontal and side areas. This mod outranks the F-22 and US Naval Aviation
  copies, so these are the rounds the collection flies. Its `usn_f-35c.ini`
  is unchanged, so SEST F-35C JATM (built on it) rebuilds identical.
- **Euromod - Modern Royal Australian Navy** (v1.0.0.2). The Hobart's EOST
  material folder is corrected and the LHD-CV Canberra's deck ammunition
  rises from 55,000 to 135,000 points. SEST RAN Fleet's Hobart picks up the
  fix on rebuild; the Canberra SEST sails is the amphibious hull, which did
  not change.
- **Euromod - South Korea Navy.** The Marado (LPH-6112) is now its own unit,
  `ko_lph-6112`, instead of Variant2 of the Dokdo (`ko_lph-6111`); the ROK
  MH-60R gets a name and a corrected material path, and the Dokdo's sensor
  fit is rewritten (12 sensors, was 8). SEST's world campaign places one
  `ko_lph-6111`, which keeps its Variant1 (Dokdo); its buy list takes the
  Marado on rebuild (tier 2, South Korea's 16th ship type), and SEST
  Replenishment ships the reload flag for both hulls.
- **Euromod - Main Pack and British Navy.** The Main Pack now ships the
  Starstreak (`rn_starstreak`) and an air-launched copy (`rn_starstreak_air`);
  neither was in the previous export, so the British pack's Army Air Corps
  Apache (`raac_ah_mk_1`) had named a round nothing defined. It now carries
  the air copy. SEST does not field that Apache.
- **PLAAF Aircraft Pack.** Missile retunes (the PL-15 and PL-15S to 125 NM
  from 108, the PL-17 to 320 NM from 250, shorter seeker and terminal ranges
  on these and the PL-12/12A) that do not reach the game: those five files
  are shipped by mods placed higher (the PLA & PLAN & PLAAF AEP at position
  4 wins the PL-15, PL-15S and PL-17; 3436170138 the PL-12 and PL-12A), and
  the PLAAF pack sits at position 187. What does reach the game is the
  `Volume=` it adds to the Kh-29TE, PL-2, PL-5B and its bomb racks, which
  only it ships.
- **Euromod - Anchorchain Expansion Pack.** Hull Damage (a new plugin), new
  kinetic-kill and high-speed warhead effects with matching ammunition
  overlays, retuned rocket smoke, and three experimental "worker" plugins
  (CombatWorker 0.2.0, ParallelRangeProbe 0.12.0, UiWorkerProbe 0.2.0). Their
  README says they have not been tested in game. In this session's log
  CombatWorker switched itself off at start ("Conflicting hook:
  io.github.yourname.second-thrust"), because the PLA & PLAN & PLAAF AEP's
  SecondThrustMod hooks the same thrust method; the game runs on its own
  code for that, which is harmless. The other two started. If the game
  stutters or stalls after this update, these two are the first suspects.
  Their README gives a per-session off switch (`off` written to
  `Mods\<name>\live\mode.request` under the game's LocalLow folder) and
  CombatWorker an `Enabled=` line in its settings.ini; the other two follow
  the AC Pack's own checkbox.

The SEST plugin in the log is still the Workshop copy of 16 Oct (31,232
bytes); 1.2.2 reaches the PC with the next sync.

Checks: gates 11 of 12 (`check_inventory`, the four CR-stripped mods, as
before); campaign tests 201, tool tests 105. `check_mod_conflicts 3820576916`:
two whole-file collisions (the Steelfin rounds), none with anything SEST
fields.

Before the next upload, add to collection 3812390790: Euromod - Modern Royal
Australian Navy (3820759806, also a Required Item of the SEST item, since
SEST RAN Fleet patches its ships) and Steelfin (3820576916). SETUP now checks
for Steelfin, as for every mod in LOAD-ORDER.txt, but no SEST file needs it,
so it belongs in the collection rather than the Required Items.

## 5. Third capture: U.S. Navy 2027, PLAN Pack, South Korea; line endings restored

Capture `9e9ad29e` on `chore/workshop-refresh-20261017c`, taken with the
line-ending repair in the same commit.

- **Line endings.** The four mods whose files had lost their carriage returns
  in the repo (PLAN Pack 3775128499, Ka-31 3776340577, Tu-214R 3780118683,
  E-3G 3781062859) were re-staged with `git add --renormalize`. The Ka-31,
  Tu-214R and E-3G show no content change ignoring line endings; the PLAN
  Pack's content change is its author's update (below). Cause, for the
  record: the files were committed as LF before `mods-source/** -text` was
  set, and the exporter's `Copy-Item` keeps file times, so git never saw the
  real bytes as a change until they were renormalized.
- **U.S. Navy 2027 Capabilities (3606774881)**, ApproximateVersion 0.8.6.
  - The MH-60R, which SEST's RAN air group flies (816 Squadron, Squadron20),
    moves its three ASW sonobuoys to Euromod Main's lettered rounds
    (`usn_ssq-53h`, `usn_ssq-77c`, `usn_ssq-62g`), all three shipped by
    Euromod Main, which SEST already requires.
  - Every 2027 Burke (25 hulls) and the 2027 Ticonderoga: search radars
    listed per launcher (`AssociatedSearchSensors`), Mk 41 cells grouped
    (`SystemGroup=MK41_aft`), the external guiding systems commented out, and
    the deck torpedo stock 28 -> 34 of 40. The Ticonderoga's variants get
    their real hull numbers, emblems, the Bunker Hill livery and a two-
    Seahawk air group (Squadron1, 13 and 14; all three in SEST's composed
    20-squadron table).
  - Rounds: AIM-424 reaches 360 NM (was 350); SM-6 Block I and IB
    (`usn_rim-174a`, `usn_rim-174c`), SM-2MR Block IIIC (`usn_rim-66p`), ESSM
    Block II (`usn_rim-162e`) and RAM Block II (`usn_rim-116c`) retuned (kill probabilities, terminal loft,
    reliabilities); the Tomahawk J ship and submarine rounds
    (`usn_rgm-109j`, `usn_ugm-109j`) switch to `MidCourseCorrection=4`, the
    satellite mid-course guidance of the Euromod Anchorchain pack's SATCOM
    plugin. SEST's own AIM-424 (`sest_aim-424`) is unaffected.
  - SEST re-forks what it ships of these: eight hulls and four rounds in SEST
    Replenishment, the SM-6 Block I (`usn_rim-174a`) in SEST Collection Fixes.
  - The author's update also moved a stray `vessels/Virginia.ini` into a new
    `vessels/Backup/261017/` folder and left a full older copy of
    `usn_cg_ticonderoga_vls_2027.ini` there. If the game reads subfolders of
    `vessels/`, that copy is a second definition of the same id; whether it
    does is not known (the same open question as `systems/` subfolders).
- **PLAN Pack (3775128499).** Every named hull's `ServiceDate` rewritten,
  mostly to an open-ended commissioning year (`2018|`); `Volume=` added to
  rounds; the Type 055 variants gain sections. No PLAN hull a SEST mission
  places leaves service by 2028 (Type 003, 052D, 054A P5 Variant1-4 and
  056A checked against the new dates).
- **Euromod - South Korea Navy (3789208859).** The K-SAM II's 70,000 ft
  engagement floor is fixed upstream (now 10 ft), and the kill
  probabilities above 1 on it and the L-SAM are corrected to 0.98; the L-SAM
  reaches 135 NM (was 120); the SAAM-400K retuned; one line on
  `ko_ddg-995`.
  - SEST Intercept Model carried that floor fix. Its builder stopped the
    build when the upstream file already had the low floor; the override is
    now a tag-only copy, as for Red Storm's SM-6 A and C, because SEST
    Replenishment meters the round and reads its tag from SEST's copy. The
    pack's description and FEATURES.md say so.

## 6. The campaign-map error box: SEST's tile guard (plugin 1.3.0)

The player asked for the error box after a campaign mission to go
(`docs/playtest-20261016-review.md`, section 2: `NullReferenceException` in
`SeapowerTileMap.RenderTileFromHeightmap`, from `LoadTile`, under the Harmony-
patched `LoadTiles`, while the mission scene unloads). SEST cannot change the
Dynamic Campaign Mod's files, but its own plugin can stop the exception short
of the dialog.

- `SestMenuBackground.cs` gains `TileGuard`: a Harmony finalizer on
  `Seapower.SceneEditor.SeapowerTileMap.LoadTile` that drops a
  `NullReferenceException` (that one tile is skipped; the rest of the return
  step, which selects the next campaign event, now completes) and lets any
  other exception through. It finds HarmonyX, the type and the method by name
  at run time, so nothing is referenced at compile time, and installs nothing,
  with one log line, if any is missing. The first three skips are logged in
  full (`[SEST TileGuard]`), later ones counted.
- `TileGuard=1` in the shipped `sest_menu.ini`, on unless 0; README.txt in the
  pack's plugins folder says so. Version 1.3.0; the DLL is 37,888 bytes.
- Checked: HarmonyX 2.10.2's own API documentation (its NuGet package's
  `0Harmony.xml`, read, not run) has the three members the guard calls,
  `Harmony(string)`, `HarmonyMethod(MethodInfo)` and `Patch(MethodBase,
  prefix, postfix, transpiler, finalizer[, ilmanipulator])`. A test against
  stand-ins for Harmony, the tile map and Unity's log (compiled with the guard's
  own source, run under Mono) shows it patches `LoadTile` with the finalizer
  only, drops a null reference, passes any other exception on, logs three
  skips, and installs nothing when Harmony or the map type is missing.
- Not seen in game: whether the skipped tile draws on the next viewport move,
  and whether the error ever came from anything but this path.

## 7. Fourth capture: Red Storm Arsenal and Royal Australian Defence Forces

Capture `4d4744e8` on `chore/workshop-refresh-20261017d`.

- **Red Storm Arsenal (3413868677).** One file: the Constellation frigate's
  RAM launcher moves to its proper mount (`RAM_2` -> `RAM_1`, its container
  likewise). SEST Replenishment's fork of `usn_ffg_constellation` follows.
- **Royal Australian Defence Forces (3455404959), v0.7.5.0.3.**
  - Moved into `Legacy Files/` and `Legacy/` subfolders, which the game is
    not known to read: the late S-70B-2 Seahawk (`ran_S-70B-2_Seahawk_late`),
    the late Adelaide (`ran_ffg_adelaide_late`) and six rounds. Of the rounds,
    the Nixie decoy, the Mk 2 noisemaker, the ESSM `usn_rim-162a` and the
    SSQ-53D/62C sonobuoys are still shipped by other mods; `ran_rim_66m_rail`
    now is not, and nothing else names it. No SEST mission placed either unit.
    On rebuild the world campaign's buy list drops both (Australia 44 ships, 48
    aircraft; catalogue 1,554) and SEST Cross-Deck drops the late Seahawk from
    its Seahawk family on 36 allied decks. The offline Gallery's catalogue
    (compiled 5 Oct) still lists both; it is a static photo list the game
    never reads.
  - The sonobuoy `ran_ssq-81b` is renamed `ran_ssq-801`, with a new
    `ran_ssq-801b`, and the S-70B-2 takes them by date
    (`DateBased_Sonobouy`). The S-70B-2 SEST flies is Euromod RAN's, which
    loads above and wins, so this does not reach it.
  - The New Zealand Leanders' sonar is renamed (`Type_177` -> `Type177`) and
    the SH-2G(I) moves from AGM-65F to AGM-65B. RADF is the only shipper of
    both units, and no SEST mission places them.

Checks: all 12 gates pass; nothing SEST builds names a unit that no longer
loads.

## 8. 18 Oct capture: five overnight updates

Capture `532c082e` on `chore/workshop-refresh-20261018`, taken on the PC at
`9ad230d7` with the 16 Oct menu plugin (1.2.2) still installed.

- **US Naval Aviation (3737267013).** Two new rounds, the AGM-154C JSOW
  Block II (`usn_agm-154c`, a BROACH penetrator for hardened targets) and the
  Block III (`usn_agm-154c-1`, datalinked, anti-ship as well), with their
  model material and names; the infrared sensor's look-down multiplier
  0.8 -> 1.0. No aircraft in the mod loads them yet.
- **Euromod - Main Pack (3629144864).** The Indian BrahMos and BrahMos-ER
  gain seeker and warhead reliability (0.8), a circular error against
  installations and the infrared display flag.
- **Euromod - India Navy (3807164392).** New Shivalik-class frigate
  (`ins_p-17a`, three variants, Indian, in service 2010), with the Barak-1,
  Barak-8 ER and Shtil-1 rounds it fires.
- **Spanish Navy Mod (Cold War) (3630495619), v3.56.** New loadouts on the
  Dedalo (R01) and Principe de Asturias (R11), deck crew on R11, the Mirage
  IIIEE in all three squadrons (111, 112 and 11) with its own air-to-air
  fits, and a static AV-8A/S Matador. SEST Replenishment's two carrier
  forks (`ae_cvl_dedalo`, `ae_cvl_principe_asturias`) re-fork from the new
  files.
- **Euromod - Anchorchain Expansion Pack (3784474738).** Every plugin
  rebuilt (Hull Damage 0.4.2 -> 0.5.7; the old one left as `HullDamage.dll_`,
  which nothing loads); the high-speed hit effects removed again from 65
  of its ammunition overlays; READMEs moved under `readme/`. CombatWorker still
  stands down on the PLA AEP's SecondThrust hook, as before.
  - The SM-3 Block IIB's overlay (`usn_rim-161d_OVWR.ini`) now also sets
    `TerminalLoft=True` and `OptimizeLoftAlt=True`. SEST Collection Fixes
    folds that overlay's flight model into the round, so it flies the same
    without the Anchor Chain preloader, and its builder stopped on the two
    new keys. Both are engine keys, so they are folded for the IIB only
    (`SM3_OVWR_ROUND_ONLY`); the IIA and IB overlays do not set them.

Rebuilt: the SM-3 Block IIB, the two Spanish carriers' Replenishment forks,
and the world campaign's buy list, which takes the Shivalik for India (five
ship types; catalogue 1,555). All 12 gates pass; campaign tests 201, tool
tests 105.

**Seen in game, at last:** this session's Player.log shows the 16 Oct plugin's
loading-screen watcher working. It found the loading screen's picture
(`LoadScreen.BackgroundImage`), watched it every frame, and painted SEST
photographs over the stock and other mods' loading pictures (lines 118, 126,
1012 and 1147). The PC has not yet synced plugin 1.3.0 (the tile guard).
