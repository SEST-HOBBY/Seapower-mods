# Workshop refresh, 25 October 2026

One capture on the PC, `0a74b07f` ("chore: capture workshop refresh
2026-10-25") on `chore/workshop-refresh-20261025`, taken at `c350b2ca` (the
live 24 Oct build, which the PC clone had been aligned to that morning) and
fast-forwarded into `sest-dev/jolly-ride-rptj4t`. No game update: Sea Power is
still 0.8.7 Build 261021 (Steam build 26103404). **Six author updates**, no
mod added or removed (199 Workshop mods; 193 unchanged). The facts are in
`data/install-snapshot/workshop-refresh-summary.txt` (regenerated here); this
is the judgement.

The capture broke one SEST builder, on purpose: the Anchorchain pack changed
its SM-3 overwrites, and SEST Collection Fixes stops on any change to them so
that the choice is made by hand. RAAF Bases, Replenishment, Combat Costs and
the campaign pack failed after it, only because they read Collection Fixes'
output (its MH-60R squadrons and its 40 mm round). With the SM-3 fold rebased,
everything builds.

The other change matters to subscribers now. US Naval Aviation renamed the
HH-60H (`usn_hh-60` to `usn_hh-60h`), and **both World Sandbox campaigns on the
Workshop name the old id**: two forces (North Island, Camp Lemonnier), the
price table and the purchase list. That is how Euromod Chile's frigate rename
stopped START CAMPAIGN on 24 Oct, so the live worlds very likely fail the same
way for anyone whose US Naval Aviation has updated, until the next upload.
Fixed here as the frigate was: new campaigns name the new id, and an alias
keeps saves made before the rename loading. SEST Cross-Deck named the old id
too.

## 1. SEST in the logged sessions

`plugin-dlls.txt` shows the live 24 Oct build installed: SEST runtime
`41ff20d9...`, the hash in `data/campaign-costs-panel-review-20261024.json`,
and `SEST_Integration` at 4,297 files. `player.log` and `player-prev.log` show
every runtime module installing on 0.8.7, among them
`F11 campaign combat costs installed: Task Force menu totals; the mission
panel is the tracker's own`. The earlier session reached the campaign map;
neither log has a debrief. The problem lists have only the usual three: SEST's
"missing from section 3" false positive, CombatWorker's SecondThrust fallback
and IDX's missing localisation file. Dynamic Campaign Mod 0.25.0.1 loads
("Game members: all 704 found", "Patched").

## 2. The updates

| Mod | Change | SEST |
|---|---|---|
| Euromod - Main Pack (3629144864) | Seven new material files (`eu_da05`, `eu_da08`, `eu_lirod`, `eu_lw03`, `eu_lw08`, `eu_stir1.8`, `eu_zw06`). | None. |
| US Naval Aviation (3737267013) | **HH-60H renamed** `usn_hh-60` to `usn_hh-60h`, with its squadrons; the file is reworked. MH-60R, SH-60B and SH-60F: the second rotor-blade pair gets its own keys (`Rotor1_Blade3/4`), and the animation block moves up. SH-60F squadrons rewritten. | Hand fixes. The World Sandbox: `usn_hh-60 -> usn_hh-60h` joins the table of retired ids (`integration/mission-seeds/retarget_units.py`), which the world builder resolves through, so both worlds keep their HH-60H forces (without it the builder had moved North Island to SH-60Fs and dropped Camp Lemonnier's pair); `usn_hh-60.ini` is now an alias of the new file, with a copy of its squadrons and name, for saves. SEST Cross-Deck's Seahawk family named `usn_hh-60`, and a member no mod ships is dropped silently, so 36 allied decks would have lost the HH-60H. It now names `usn_hh-60h`. No SEST mission or campaign places the HH-60H; the Banda Front seeds (never installed) still name the old id. SEST's MH-60R is U.S. Navy 2027's (Allied Fixes), which keeps the repeated `Rotor1_Blade1/2` keys. That is the game's own form (vanilla's Alouette, AS-350 and others), and no vanilla file names a third blade key, so the author's rename is not carried. |
| Euromod - Anchorchain Expansion Pack (3784474738) | Code: every DLL rebuilt; ExtendedGuidance 0.5.0 to 0.8.7, with seeker profiles for SPY-1, APAR, Sea Fire and other radars; new TestRange; a disabled `SeaPowerDLSS.dll_` (59 MB); the old `HullDamage.dll_` gone. A 500 kt surface nuclear effect (123 files). Overwrites: the SM-3 Block IB and IIA (`usn_rim-161b`, `_c`) take `TerminalLoft`, `OptimizeLoftAlt` and `MaxFlightTime=3000`, as the IIB had; the IIB (`_d`) takes `MidCourseCorrection=3`; NSM 1A takes `SeekerFOV=120`. | Hand fix, SEST Collection Fixes' SM-3 fold: the IB and IIA now fold the terminal loft and the optimised loft altitude, as the IIB has since 18 Oct, so they fly the same with or without the preloader. The IIB folds `MidCourseCorrection=3`, the value vanilla's SM-2s fly (`usn_rim-66c/d/h`, `usn_rim-67b`). The 3,000 s flight time stays declined for all three: SEST keeps 600, 600 and 900 s, sized to each block's range, and with the preloader the overwrite still applies on top. SEST Replenishment's NSM 1A copy already has a 120° seeker (`SeekerFOV=120,10`). |
| JMSDF Hyūga-class (3802216383), R10.56 | V-22 compatibility: the Hyūga takes `jgsdf_mv-22b` and `jgsdf_v-22` (the second is shipped by no mod); deck spot positions adjusted. The file now starts with a UTF-8 byte-order mark. | SEST Cross-Deck's Hyūga copy follows. Because the deck now names an Osprey, it takes the collection's other Ospreys as well (`usmc_mv-22b`, `mv22b_osprey`, `jgsdf_mv22b_osprey`, `sv22_2024_osprey`). |
| Dynamic Campaign Mod (3813157776) | 0.25.0 to 0.25.0.1: the DLL is rebuilt. Its three campaigns' JSON is identical once parsed (whitespace only). | None needed. SEST's two worlds were built and checked against 0.25.0's rules, and no data change shows here. The Regional Expansion's start was seen on 0.25.0 (24 Oct), not yet on 0.25.0.1. |
| Euromod - Modern Royal Australian Navy (3820759806) | New: RAAF F-35A and F-35A Block 4 (`raaf_f-35a`, `raaf_f-35a_blk4`, with squadrons and their own model), a late RAN F-35B (`ran_f-35b_late`), a 25 mm APEX round. NASAMS launcher and rounds in `WIP/`, and a test USAF F-35A in `Testing/`: subfolders the game is not known to read. The Canberra LHDs take the F-35B; the F-35B's loadouts are renamed (date-based AMRAAM); F-111C AUP cruise range 1,160 to 2,400; RAAF Hornet squadrons gain service dates. Its `systemgroups.ini` now also carries a pasted copy of weapon sections. | **`raaf_f-35a` collides with SEST's.** SEST carries Greene's RAAF F-35A (the mod left the Workshop; SEST rebuilds it from a pinned copy with its recovered model) and loads first, so Euromod's F-35A file and squadrons are hidden behind it. Euromod's Block 4 has its own id and is visible. Which F-35A SEST should fly is the owner's call (section 3). The new units are priced by the cost list's models (`usn_hh-60h`, `raaf_f-35a_blk4`, `ran_f-35b_late`, `usn_cal_25mm_apex`); the `WIP/` and `Testing/` units are not. No SEST mission flies the F-35B or the Hornet squadrons. |

## 3. For the owner

- **Upload soon.** Until the World Sandbox fix is on the Workshop, a new
  World Sandbox or Regional Expansion campaign will very likely not start for
  subscribers with the current US Naval Aviation. Before Submit, start one
  as a new campaign (and Continue a copy of a save made before 25 Oct).

- **The RAAF F-35A.** Euromod RAN now ships its own `raaf_f-35a`, with a
  model, three squadrons and a Block 4 sibling. SEST's copy of Greene's
  retired mod wins and hides it. Keeping SEST's needs nothing: it is what the
  campaigns were built and checked with, AIM-260 fits included. Moving to
  Euromod's would mean retiring SEST RAAF F-35A JATM and re-checking every
  mission that flies the F-35A against Euromod's loadouts and squadrons.
  Recommended: keep SEST's for now, and use Euromod's Block 4 where a new
  mission wants a late F-35A.

## 4. Validation

- `tools/build_all.py --from-scratch`, run three times: the first stopped at
  the SM-3 fold (section 2); the third, with every fix here, built all 25
  packs, 4,299 files. The two more than the live build are the HH-60 save
  alias and its squadrons.
- All 13 gates pass, `check_combat_costs.py` included (4,370 references
  priced in both modes), and `check_dynamic_campaign.py` passes both worlds:
  267 forces and 1,561 purchase entries in the original, 293 and 1,561 in the
  Regional Expansion.
- Tools suite 189 tests (7 skipped), with a new rename test in
  `test_world_sandbox_legacy.py`; campaign suites 300. All pass.
- No mission file changed. The changed packs are Collection Fixes (the three
  SM-3s), Cross-Deck (36 decks, the Hyūga among them), Combat Costs (the new units),
  World Campaign (both worlds and the save alias) and the consolidated dist.
- `CREDITS.txt` still lists 528 files: the HH-60 save squadrons join it, and
  SEST's SM-3 Block IIA leaves it. With the two folded lines the IIA is 89.8%
  like the Main Pack's file, under the 90% the list measures, as the IIB has
  been since 18 Oct. Both headers still name their base (3629144864).
- `data/deploy-branch.txt` now names `sest-dev/jolly-ride-rptj4t`.
  `sync-sest.ps1` refuses any other branch, and the file still named
  `sest-dev/loving-bell-3cnvvw`, which the deploy branch has contained since
  23 Oct.
