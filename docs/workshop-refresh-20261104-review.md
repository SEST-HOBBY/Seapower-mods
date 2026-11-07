# Workshop refresh, 3 November 2026

One capture on the PC, `530129ec` ("Capture installed Workshop mod updates")
on `chore/workshop-refresh-20261104`, taken at 23:22 on 3 Nov 2026 (Brisbane)
from `57a23ee8`, the consolidated release's head. The PC was on the public
beta (Steam build 26223125, 0.8.7 Build 261026). The capture never exports the
game's own files, so `mods-source/_vanilla` keeps the stable Build 261021
export the pack is built from.

Steam lists 30 items as updated since the 28 Oct 2026 capture: 23 changed
exported data files, seven rebuilt only their DLLs, and BetterTacMap's
`settings.cfg` changed on the PC without a Workshop update. The diff holds 807
paths (124 added, 1 deleted, 668 modified, 14 renamed); no subscription was
added or removed. This document is the judgement; the facts are in
`data/install-snapshot/workshop-refresh-summary.txt` and the dated notes in
`data/mod-catalog.json`.

## 1. What stopped the build, and what changed in SEST

The from-scratch build on the export stopped in two builders.

- **SEST Collection Fixes** stopped on its own retirement check: Euromod RAN's
  1 Nov 2026 update ships the Sea King Mk.50A/B squadron table under the name
  its aircraft reads (`ran_seakingmk50ab_squadrons.ini`, same content), so
  SEST's copy of the misspelt table is no longer needed. It is retired: the
  builder now deletes any old output and stops only if the author's file
  disappears again. While Collection Fixes was stopped, three later checks
  failed with it (SEST Replenishment's free-round check on `usn_cal_40mm`, the
  alias gate's ten stale Euromod overwrites, two campaign excuses); all three
  pass once it builds.
- **SEST Campaign** stopped because the pack now reaches The Royal Navy
  (3491248180). Euromod-HD Hyundai's update embarks its `rn_sea_lynx_3` on the
  PN FFG-06 and FFG-150s in place of Euromod South Korea's `rok_mk99_a`, and
  every Sulu Line mission fields the FFG-150. The coverage excuse for The Royal
  Navy is removed, so the builder credits it; it was already subscribed and in
  the collection. Sulu Line's coverage no longer credits Euromod South Korea
  through the frigate's deck. The release gate that re-derives coverage from
  the built missions (`tools/check_campaign_coverage.py`) had never learnt the
  builder's deck rule of 20 Oct 2026 and reported The Royal Navy unreached; it
  now credits a placed ship's embarked aircraft the same way.

Everything else the authors changed is absorbed by the rebuild: SEST
Replenishment's forks, the Cross-Deck stubs and the Allied Fixes, Growler NGJ
and F-35C JATM forks rebase on the new files.

## 2. Author changes worth knowing

- **Modern US Navy (v633)** split its Flight IIA Burkes into eight new
  `_early` hulls (2000 to 2011, SH-60B) and moved the base hulls to the
  MH-60R era. Seven late hulls lost their `[AirGroup]` and now embark no
  helicopter: `usn_ddg_burke_f2a_081_late`, `_091_late`, `_091_sewip`,
  `_097_late`, `_097_sewip`, `_099_late` and `_100_late`. No SEST mission
  places them; the World Sandbox sells them.
- **Euromod-HD Hyundai Export Ships Mod** is the new title of
  `euromod-philippines` (3812454152; the slug stays). It received the KDDX and
  PKG-711 SCL from Euromod South Korea and adds three export hulls.
- **US Naval Aviation (v114)** replaced the P-8A's ASWAdvanced and LRASM
  loadouts with ASWLongRange and AntiShipHeavy. No SEST mission or roster
  names either, and the 2027 P-8 that SEST ships keeps its own sections.
- **Red Storm Arsenal** adds the beta's `Volume` key to 343 files and nothing
  else; with Custom Loadout Editor, Flight Deck Ops, U.S. Navy 2027 and the
  Spanish packs, 393 lines of `Volume` and nine of `MinTakeoffDistance`
  arrive. The stable build ignores keys it does not know (the same fact the
  TacMap Colors keys rely on), so SEST's forks carry them as the authors wrote
  them and the beta reads them.
- **New ids**: 23 units (the eight early Burkes, the BBG Ulysses S. Grant,
  three Trieste LHDs, the Type 053H2G and 054B Phase 1, two Chilean F-16s and
  three Hyundai export hulls) and 22 rounds. No SEST mission places any of
  them. The Chilean F-16s use F-16C Fighting Falcon (modern)'s model and
  sensors, a dependency their mod does not declare. The cost model priced
  the new units by its rough types, but four hulls matched no type and fell
  to the $75M merchant default; they now take a same-family price from the
  Combat Cost Tracker author's catalog (`integration/combat-costs/mappings.json`):
  the 054B Phase 1 as Red Storm Arsenal's Type 054B, the 053H2G as its
  successor the 053H3, the HDF-3600 as the Daegu-class frigate and the BBG
  Ulysses S. Grant as the same mod's BBG Trump.
- **Code mods**: Pop-Out Windows 1.1.3 and Topographic Map 1.5.0; Custom
  Loadout Editor's "fixed mod not working on beta"; Saronic Corsair now ships
  its own bootstrap, a `version.dll` the player copies beside `Sea Power.exe`
  by hand, which SETUP does not install; AutomaticSAR was rebuilt on 1 Nov
  2026, and that build is the one the beta loader already holds back.

## 3. The beta session in this capture

The session before the capture ran the beta with SEST's R3 candidate
installed (`SEST.RuntimeFixes.dll` a0fb4279, `SEST.ContactsFix.dll`
d60e662b): the R4 repair of 3 Nov 2026 had not been applied. Its log shows
`[WeaponCosts] Missing WeaponCosts: sest_agr-30 (ASM)` after an AGR-30 launch,
which is the beta's one-shot `#!extend` scan that R4's Runtime repairs, and
the nine author plugins that stop on the beta's changed signatures
(`docs/dual-build-workshop-update-plan.md`, section 4).

The owner's loadout screenshot of the same session shows "No radar or night
vision: this aircraft cannot find air targets at night" on a Redback MH-60R
(56 rounds, 25 chaff). The AGR-30 keeps air targets as a secondary type, so the
game treats it as an air-to-air round, and the RAN MH-60R's only radar is a
surface-search set. Release `d19ce922` writes each Redback helicopter's FLIR
night vision level into its own unit file, so the check holds on both builds
whatever the merged sensors file says.

## 4. Decisions for the owner

1. **The seven late Burkes without helicopters.** SEST could fork the seven
   hulls to restore their MH-60R pair, but that ships seven whole-file
   overrides of Modern US Navy that would shadow the author's next fix.
   Recommended: report it to the author and leave the hulls as they are.
2. **The beta keys in SEST's forks** (`Volume`, `MinTakeoffDistance`): carried
   as the authors wrote them, as above. Say if the stable target should strip
   them instead.
3. **The PN frigates' Sea Lynx.** Kept as the author chose; The Royal Navy is
   already in the collection.

## 5. Checks

From-scratch build and the 18 release gates on the integration branch, which
also carries the consolidated release's 4 Nov 2026 commits (the TacMap beta
keys and the Redback night vision); the counts are in the pull request.
Nothing here was run in the game.
