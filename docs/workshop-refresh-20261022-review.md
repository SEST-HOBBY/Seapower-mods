# Workshop refresh, 22 October 2026

One capture on the PC, `1bda58a6` ("chore: capture workshop refresh
2026-10-22"), fast-forwarded on top of `4cd47865`, the last built and
pushed SEST state. Two things moved at once:

- **The game:** Sea Power 0.8.7 Build 261021 (21 Oct 2026), Steam build
  25936448 -> 26103404. The public build before it was 0.8.6 Build 261014,
  so 0.8.7 also carries the fixes of the 261016 and 261019 test builds.
- **Ten author updates**, no mod added or removed (199 Workshop mods, 200
  Mod Manager entries with the pack; 189 unchanged).

The facts are in `data/install-snapshot/workshop-refresh-summary.txt`
(regenerated for this capture); this is the judgement. Five readers each
took a group of mods (the US group, the Euromod core, the Spanish and REDFOR
mods, Chile, and the game update) and tested their fixes in scratch
worktrees. Every claim acted on below was re-read against the tree here
before it was acted on, and the whole of it was rebuilt from scratch.
Two adversarial checks of the finished tree followed; what they found is
corrected below and was rebuilt again: the SM-6 and OHP claims in the
change log and on the card, the Type 209 stand-ins' names, the
Description's count of mods, and several of the records (section 4).

## 1. The game: Sea Power 0.8.7

**What changed.** The 21 Oct release note lists three fixes: a null
reference spawning a unit whose CIWS magazine has no ammunition, a
dev-mode respawn null reference, and null-reference spam and failed loading
of (modded) helicopters with a missing rotor or rotor-disc model. The
261019 build inside it fixed the null reference on returning to the
campaign map after a mission (the error SEST's menu plugin TileGuard
catches), terrain-texture memory, null references destroying units without
materials and rotating launchers without a mount. 261016 fixed missiles
taking recycled active-radar (ARH) tracks and going for random targets,
aircraft guns not firing early enough and the seeker-cone overlay (now the
real seeker, not the terminal distance), added picture-in-picture
supersampling, the stock Mirage III's missing parts and memory-leak fixes.
The ARH fix can change what an active-radar missile goes for, so missile
behaviour in 0.8.7 play need not match 0.8.6 play tests (section 6).

**The stock files.** `check_vanilla_drift --since e7b32f11` (the same
`_vanilla` as `729c5e97`, the 0.8.6 export): 4,049 files then and now, 7
changed, 8 with line endings only, nothing OVERRIDDEN, MERGED, PLACED or
NEW - PASS. The changes are the English and Chinese `ui.ini`
(picture-in-picture supersampling keys), Pacific Strike's Chinese medal
citations, rules page, credits and scenario name, and one Narvik intro
message in the newer popup form. SEST builds its rules page from the
English page, which did not change, ships no `ui.ini` and no Chinese
citations, and the six air-tasking role keys are unchanged. The tool's
BUILDER-READ hits on `commander_settings.ini` and `_info.ini` are SEST's own
files of the same names. The editor's `_TempMission.ini` adds 38 Caribbean
points to the proven-position pool, thousands of miles from any SEST
station.

**The drift baseline.** The tool's own rule (its docstring and
`packaging-and-recovery.md`, *After a Sea Power update*, step 1) is that
the baseline is the export before the one under review, which for this
capture is `e7b32f11`/`729c5e97`; that is what the gate ran with, and it
was not moved. Once this rebuild is committed, the next capture's
baseline is `1bda58a6`, the 0.8.7 export.

**The version.** `check_game_version` failed on 0.8.7 (26 packs, 25
builder literals; the Mod Manager accepts a higher patch, so players saw
no warning). `check_game_version.py --bump 0.8.7` rewrote the 25 builder
literals, one line each, with none left for a hand edit; the rebuild
regenerated the 26 `_info.ini` files and the check passes. The hand-written
"Built for Sea Power 0.8.6" in `docs/FEATURES.md`, the Steam card
(`cards.json`, pack 2) and the Workshop description now say 0.8.7. All 11
Workshop version ranges admit 0.8.7; both Spanish mods already declare it.

**SEST's runtime plugin is off on 0.8.7.** (Superseded 23 Oct: the
plugin is now matched to 0.8.7; see the addendum.) The 22 Oct `Player.log`
reads `[SEST Runtime] inactive: uninspected native assembly
eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd`.
`SestRuntimeFixes.cs` installs nothing unless `Seapower-Scripts.dll`
hashes to the inspected 0.8.6 build (`c913e31f...`), so it failed closed as
designed: the Tomahawk MST Block Va's 500 ft over land in cruise and the
task-force debrief's lost-ship rows are off for every player, since Steam
has moved everyone to 0.8.7. The plugin DLL itself (`9aa55df8...`) is
unchanged and loads. The new hash was not added: the DLL is not in the
repository to verify, and the assembly really changed (8,515,072 ->
8,528,384 bytes; other mods' plugins report `ObjectBase.LoadStateFromFile`
and `WeaponSystemLauncher.OnUpdate` changed, and `TaskForceDebrief` reads
the saved mission state the first of those handles).

What was made truthful instead:

- `SEST_RUNTIME_README.txt` gains a paragraph, *On Sea Power 0.8.7 both
  corrections are off*, and `sest_runtime.ini` says on its first lines that
  the options do nothing on any build but 0.8.6. Both are copied into the
  pack by the rebuild; neither is a plugin-build input, so the DLL and
  `plugin-build.json` are untouched and `test_runtime_plugin` passes.
- The pending Workshop change log no longer claims either correction; a new
  *Sea Power 0.8.7* section says both switch themselves off on 0.8.7.
- The Steam latest-update card's *MST over land* and *Lost ships in the
  debrief* items are gone (below).
- `docs/FEATURES.md` lists the plugin under *Not yet confirmed in game*
  with its 0.8.7 state; `docs/play-test-guide.md` section 0 has a step to
  read the `[SEST Runtime]` lines; the Southern Watch test card has H.24.

**Re-enabling it** needs the 0.8.7 DLL from the PC. The steps, in full in
`integration/runtime-fixes/README.md`:

1. PC, game closed: `.\tools\export-map-diagnostics.ps1
   -IncludeGameAssembly`; send the ZIP (Downloads,
   `SEST-map-review-complete-<date>-<id>.zip`, with
   `game-reference/Seapower-Scripts.dll`), record its hashes in a dated
   `data/*-review-*.json`, do not commit the DLL.
2. Check the DLL's SHA-256 is `eab2297b...`, the hash the log printed.
3. Extend `verify_native_api.py` to the members the plugin binds but the
   verifier never checks (`IniHandler.doesSectionExist` and `readValue`,
   `LinearCampaignMission._index`, the roster item's and snapshot items'
   properties, the debrief's `UnitRows`), proven first against the 0.8.6
   DLL in the owner's 20 Oct ZIP.
4. `pip install dnfile dncil`, set `EXPECTED` to the new hash and run it on
   the 0.8.7 DLL; every check must pass.
5. Diff the IL of `GetSafeAltitudeOverSurface`,
   `CrudeGetHighestTerrainHeightAhead`, `ReadUnitRows` and `ReadSnapshot`
   between the two builds; if the game's own `ReadUnitRows` now lists lost
   hulls, retire `TaskForceDebrief` rather than re-enable it.
6. Re-gate: `SestRuntimeFixes.cs` (`inspected`), the verifier's message,
   `sest_runtime.ini` and `SEST_RUNTIME_README.txt`.
7. `python3 integration/runtime-fixes/build_plugin.py` (Mono), then
   `tools/build_all.py --from-scratch`, the gates and both test suites.
8. PC: `Player.log` shows both `[SEST Runtime] ... correction installed`
   lines; then the ridge-crossing and sunk-ship acceptance tests of
   `docs/playtests/fleet-terrain-debrief-20261020.md`, never run on 0.8.6
   either. Only then do the two items go back into the change log and the
   card.

**TileGuard** still installs on 0.8.7 (`[SEST TileGuard] guarding
...LoadTile`) beside the game's own fix and only drops
`NullReferenceException`s from `LoadTile`, so it is harmless and may never
fire. FEATURES now asks the tester to report any `map tile skipped` line;
none over several returns to the map on 0.8.7 means it can retire.

**Other mods' code on 0.8.7.** (Superseded 23 Oct: the authors' 23 Oct
updates put all six back on; see `docs/workshop-refresh-20261023-review.md`,
section 1.) Six components switched themselves off against the new assembly;
their DLLs are byte-identical to the 20 Oct capture, so the game update
alone did it (report only - SEST forks none of them):

| Mod | On 0.8.7 | SEST's use |
|---|---|---|
| Anduril FQ-44 Fury (3804868806) | XQ58Shadow 1.2.4: "Startup failed: Unsupported game assembly" - Drone Control's Watch, Shadow and camera feed gone; formation, lights, voice and loss observer load | D6 Long Reach's Fury 61/62 fly on loadout and orders |
| Anduril Maritime Drones (3819522350) | K5 contact strike off (`LoadStateFromFile` changed) | O5 Paper Trail's K5 is the reconnaissance variant |
| Saronic Corsair (3766210676) | "Order hooks unavailable; original polling retained"; the contact controller loads | Paper Trail's scout makes no contact attack |
| EC-2 Stand Off Jammer (3813033771) | radio and data-link jamming off ("verdict HookChanged", `WeaponSystemLauncher.OnUpdate`); radar jamming is the game's | O9 Viper Zero's Jammer 71 jams a search radar only |
| MV-75 Cheyenne II (3810611344) | the systems hook off; tilt component and formation load | D8's Valor 73: what the hook drives is not documented (test card H.14) |
| YF-23 Black Widow II (3796349767) | AlpineSeaPower 0.3.1 "patches off until a mod update"; its new YF23Ejection 1.1.0 loads | D6's Black Widow 11/12: what the fixes covered is not documented |

CombatWorker's native fallback (the SecondThrust conflict), IDX's missing
localisation file and the HarmonyX warnings are as they were on 0.8.6.
Dynamic Campaign Mod 0.25.0 loads but logs nothing at start, so its state
on 0.8.7 is not shown.

## 2. The updates

| Mod | Change | SEST |
|---|---|---|
| Euromod - Modern US Navy (3390330875), v621 | The OHP long hull's Mk 13 names `WeaponMagazineMK13` - the author's own fix of the 20 Oct defect. The MH-60R Phase II is reworked (ASW, ASWLongRange, ASWPatrol, Strike, AntiShipEarly/Late/LateLongRange, Transport; drop tanks, TransportCapacity 3, EO views) and its sonobuoys and torpedo move to `usn_ssq-53h`, `usn_ssq-62g` and `usn_mk54_2_air`, which only Euromod - Main Pack ships. The 2025 Nimitz's variant wings embark it instead of `usn_mh-60r` (Truman 18 -> 13). The Wasp is 'Wasp-class (Late)' with new VTOL and STOVL recovery circuits (landing interval 30 s, was 60 and 50); its variants' MV-22Bs take US Naval Aviation's new squadrons. The Spruance LAMPS-3 hulls are '(VLS SH-60B)' and '(RAM SH-60B)'. | `ras.py`'s HULL_REPAIRS entry stopped SEST_Replenishment and `check_pack_fidelity`, as it is meant to ("the author now ships ... drop this repair"); dropped, with a dated note in its place. The Replenishment fork now carries the author's line; its Wasp fork carries the new circuits (it outranks the author's file, so until this rebuild it masked them). No SEST mission, air-tasking row or allied pick flies the Phase II; the world campaign's 2025 Nimitzes now embark it, and every squadron their variants name exists. SW08's Roosevelt keeps the wing SEST writes. |
| US Naval Aviation (3737267013), v104 | No round changed. MV-22B squadrons 5 -> 21; P-8A adds VP-9 as Squadron5; the F-35B's CAS hangs six GBU-12D and a new CASHeavy takes the GBU-32s; 70/-70 pitch limits on the F-35C, Super Hornets and EA-18Gs, others on the ES-3A and AV-8B+; E-2D silhouette areas. | Collection Fixes' AIM-9L, AIM-9M guard and the GBU-39, GBU-12D and MH-60R donors rebuild byte-identical. SEST Growler's `usn_ea-18g_2020` (Southern Watch 11) takes the pitch keys; SEST's F-35C and Super Hornets are built on other bases, which outrank this mod, and do not. Every loadout a built mission names still exists. |
| YF-23 Black Widow II (3796349767) | YF23Ejection.dll 1.1.0; canopy and pilot parts hide with the damage model. | Unchanged for SEST: the AIM-424 extend and D6's fit rebuild identical. Its AlpineSeaPower copy is off on 0.8.7 (section 1; on again from its 23 Oct 0.3.2). |
| Euromod - Main Pack (3629144864), v486 | 35 ECM sections gain `NoiseJamPower` (21 non-zero, 0.025 to 4; vanilla's SLQ-32 is 10); `eu_EW-1017` ESM; `bra_Grifo-F` displays as EL/M-2032; DS30B/M become OpenMount guns; RBS-15 Mk3 seeker re-gained; eight Russian SAMs lose an orientation flag. | Reaches SEST's JMSDF, Burke, Wasp, Karel Doorman, Zeven Provincien and F123 forks as noise jamming; Allied Fixes' Ocean's DS30M are plain guns now (not in the CIWS retune). No build change. The Brazilian F-5EM also shows "EL/M-2032" (one key for both; upstream). |
| Euromod - Anchorchain Expansion Pack (3784474738) | Withdraws the 19 Oct flight-model overwrites, each file back byte for byte to 18 Oct: AIM-120A/C/C7/D/D3 cosmetic again, `usn_aim-174b_OVWR` and `usn_jsm_OVWR` deleted, the NSM loses MissileDefenceBonus 0.75 and RCS 0.0001, the SM-6 Block I/IAU lose MaxFlightTime=300. New ExtendedGuidance 0.5.0 and ACPackSettings 1.0.0; every DLL rebuilt; MultiStageMissiles 1.7.16. | No SEST builder or gate applies the withdrawn files. In game the rounds again match the files SEST's tools read: U.S. Navy 2027's AIM-174B (2650 kt, 325 NM), the round SEST's AIM-424 is aligned to and D10's Gunslinger fit carries, so D10 runs flown 19-21 Oct do not compare; the F-35C JATM's JSM; the RAN NSM at 0.30/0.001. SEST keeps the SM-6 Block I at the overwrite's 300 s (section 4). ExtendedGuidance is off by default and must stay off for SEST play (section 5). |
| Euromod - Modern JMSDF (3695809489), v40 | The JASDF F-35B's stations and fits are rebuilt (bay racks, StormBreaker, JSM, AirToAirLongRange, CASHeavy, StrikeStandoff; 70/-70 pitch). The SH-60K's ASW Long Range (Late) fit hangs `usn_ssq-53f`/`-62e`: the undefined `usn_ssq-53e` of 14 Oct is gone. Two unreferenced `jp_mh-60r` materials deleted. | Every new store resolves. SEST names the F-35B only in the world campaign's buy list and Cross-Deck's STOVL list; no change. |
| Spanish Navy Mod (Cold War) (3630495619), v3.57/3.58 | Squadron dates restated (AB 212 blue 1974-87, grey from 1988); BR-125 bomb and four Mirage III tank rounds; Mirage III/F1 fits; the F-104's tank re-rated at 645 l and 0.8 kg/l (1500 -> 516 kg) and the new Mirage III tanks rated the same way (the AV-8S tank is unchanged); the late Dedalo's static AV-8A and taxi paths. ApproximateVersion 0.8.7. | SEST forks none of the changed files. Combat Costs lists the five new rounds as unpriced (weapons eligible 2165 -> 2170). D3's AB 212 flies Squadron1, outside its dates in 2028 before and after. |
| Spanish Navy Mod (Modern) (3731208477), v1.48 | The Juan Carlos I's deck loadouts `noDeck2`/`Deck2` become `Default`, `Empty_deck` and `Empty`; class names gain pennant or type; EF-18A dates to 2026; drop tanks lose a fifth. ApproximateVersion 0.8.7. | SEST Replenishment re-forks her (four reload flags still the only change). D3 The Relief Ship now writes `LoadoutVariant=Default` where it named the gone `noDeck2`; the two RAN rosters' comment lines and the allied-fleet notes follow the new names. Every allied reserve pick still resolves. |
| THE REDFOR MOD (3732654992) | Nine of its hulls declare vanilla combat systems; a Su-35S refuelling probe, 5V55R areas, Su-30 squadron edits. | The airframe and round files lose to Sukhoi Su-27 and Euromod Main; the hulls reach SEST only through the world campaign's buy list, which did not change. |
| Euromod - Modern Armada de Chile (3776730617) | First update since 6 Aug. Five hulls renamed: `ch_ff_type23` -> `ch_ffg_type23`, `ch_ff_type23_pida` -> `ch_ffg_type23_pida`, `ch_ffg_karel` -> `ch_ffg_karel_doorman`, `ch_type22b2_barak` -> `ch_ffg_type22b2_barak`, `type_209` -> `ch_ss_thomson_mlu`. New L class (`ch_ffg_jvh`, 2005-2020). The Thomson boats carry their refit (SUBTICS, Thales sonars, 16 Black Shark, 4 SM-39 Block 2, quieter). `systems/sensors.ini` drops 36 sections for Euromod Main's `eu_*` copies. | Stopped SEST_World_Campaign ("no enabled mod defines ch_ff_type23_pida, ch_ffg_karel, type_209"); the ids are renamed (section 4). Combat Costs, the Williams' encyclopedia picture and four other mods' sensors followed (sections 3 and 4). |

## 3. Mods that did not update but moved: Chile's dropped sensors

Chile's sensors file had been the only definition of several names other
mods use, and the winner of others:

- **[ZW06]**, the Brazilian Niteroi and Niteroi 2005's search radar: now
  defined nowhere, and the world campaign places two Niteroi 2005 at Rio.
  SEST Collection Fixes supplies it (section 4).
- **[STIR]**: only RADF's `vessels/Legacy Files/` hull names it; nothing that
  loads is affected.
- **[AR-700S5] and [IPS CSU 3]**: The Royal Navy's Oberon names them under
  commented-out headers (the keys fold into SensorSystem5 and 7);
  **[Colibri]**: the Siam Shield's AB 212's ECM. Neither unit is placed by
  a SEST mission or a world-campaign force; the world campaign's buy list
  sells both, so a player who buys one gets it without that sensor.
  Accepted and recorded, not supplied (section 5).
- **[DA-05] and [EL/M-2032]** now load from the Luzon Line's own copies,
  **[AN/APS-88]** from the game's. The FA-50PH Sulu Line fields in six
  missions flies its author's EL/M-2032 (MaxRange 148 -> 170 km, PeakPower
  13 -> 5 kW); the Siam Shield's Ratanakosin and RADF's Van Speijk (world
  campaign only) take the Luzon Line's DA-05 (MaxRange 237.1 -> 155).
- Chile no longer redefines the E-3G's **[AN/APY-2]** or **[Optics]**, so
  the reason the canonical order gave for its place is gone; the place
  itself is still right (below RADF and Euromod RAN, whose sections win).

Catalog notes for Brazil, RADF, The Royal Navy, the Siam Shield, the Luzon
Line and Euromod Main record each.

## 4. Fixes made in this pass

- **OHP long hull** (`integration/common/ras.py`): the HULL_REPAIRS entry
  goes, with a dated comment in its place; the guard did its job.
- **The world campaign's Chilean ids** (`world-sandbox/home_bases.py`,
  `submarines.py`): Talcahuano's PIDAA Type 23s and Thomson boats, Punta
  Arenas's Karel Doorman, and the Type 209 stand-ins at Salamis, Golcuk,
  Jinhae and Alexandria. `ch_ss_thomson_mlu` is still a fair stand-in: the
  same 61.2 m, 1,440 t Type 209/1400 hull on the same `ships/type_209/`
  model, still Chile's flag, now in Chile's refit fit; MAPPINGS keeps
  "same class" for Turkey, Egypt and South Korea and "same family" for
  Greece. Unnamed, a stand-in shows the hull's default name, which is now
  Chile's lead boat, "Thomson"; so the Salamis, Golcuk and Alexandria
  boats, unnamed until now, sail under their real boats' names as Jinhae's
  already did: Greece's four Type 214s (HS Papanikolis S-120 to HS
  Katsonis S-123, the boats sure to be in service in 2028 while the older
  209s are being replaced; MAPPINGS now says the Greek boats stand for the
  214, same family), Turkey's Gur class (TCG Gur S-357 to TCG Birinci Inonu
  S-360) and Egypt's S41 to S44 (861-870; they have numbers, not names).
  The L class is not placed: it left service in 2020, and the two
  Adelaides at Talcahuano carry its names. It joins Chile's buy list on its
  own (no date cut, by design; Chile 7 -> 8 ships). `check_dynamic_campaign`
  passes inside the build; `campaign.json` changes by the renames, the L
  class, two displacement values (Scorpene 74 -> 75, Williams 152 -> 154)
  and the twelve boats' names (their forces now follow Jinhae's in the
  file; the same 267 forces and 49 patrols).
- **Combat Costs** (`combat-costs/mappings.json`): the tracker still prices
  the five renamed hulls under their old ids, so five reviewed mappings
  carry those prices to the new ids, and `ch_ffg_jvh` takes the tracker's
  own Jacob van Heemskerck entry (`rnn_ffg_van_heemskerck`), the same class.
  Vessels priced: 809/936 -> 810/937.
- **The Williams' encyclopedia picture** (`gallery/profiles.tsv`): the row
  follows her new id, so `ui/profiles/ch_ffg_type22b2_barak.png` replaces
  the one that matched nothing. `refresh_index.py` RENAMES gains the five
  Chilean renames (the script still stops earlier, on 26 other records).
- **SM-6 Block I flight time** (`collection-fixes/build_patch.py`): the
  base file keeps `TimeLimited` commented out, but the Anchorchain
  overwrite sets `TimeLimited=True` whenever the preloader SETUP installs
  is present, which made the base file's 240 s a hard limit: at 3600 kt it
  covers 240 NM against a declared 260. SEST's `usn_rim-174a` now flies the
  author's own 19-21 Oct figure, 300 s; the RIM-174B inherits it through
  SEST Replenishment's alias. A guard stops the build if the overwrite sets
  a flight time again or drops `TimeLimited`. Unlike the SM-3s' flight
  times, 300 s is not sized with headroom for the round's speed bleed
  (`VelocityBleed=0.3` after a 50 s burn), so whether it now reaches 260 NM
  is for the game to show; the listing, the card and FEATURES say only that
  it keeps 300 s (section 6).
- **[ZW06]** (`collection-fixes/build_patch.py`, MISSING_SENSORS): cloned
  from Euromod Main's `eu_zw06`, the definition Chile moved to, the same
  way Collection Fixes supplies the other sensors units mount and no mod
  defines; it stops the build if any mod defines `[ZW06]` again.
- **Texts that had become untrue:** the Chile and Anchorchain coverage
  reasons in `campaign_data.py` (the first named sensors Chile no longer
  defines, the second counts that were already wrong), Chile's
  load-order note in `tools/generate_load_order.py`, the allied-fleet notes
  that become roster comments (`allied_fleet.py`: Wasp-class (Late) and the
  three Spanish classes as the mods now name them).
- **Version, runtime claims, change log and cards** (section 1).
- **Data:** dated notes on 20 catalog entries (the ten updated mods, the
  five whose sensors Chile's update moved, and the five whose code 0.8.7
  switched off), Chile's `load_order` text corrected,
  `docs/mod-catalog.md` regenerated, the fingerprints rebased (`python3
  tools/fingerprint_mods.py`: 199 mods, all match), the load-order docs
  regenerated (Chile's in-game name is now "Euromod - Modern Armada de
  Chile"), and the refresh summary written for this capture.
- **Steam cards:** on the latest-update card *MST over land* becomes *SM-6
  flight time* (300 s kept, Euromod's own figure), *Lost ships in the
  debrief* becomes *Sea Power 0.8.7*, *AIM-9L and OHP fixed* becomes
  *AIM-9L fixed* (the Mk 13 is now the author's own fix), and *Latest mod
  updates* names this capture's (Chile, Wasp, MH-60R, Spain, JMSDF); the
  kicker keeps the month only. Pack 2's footer reads 0.8.7. No OVERFLOW;
  only those two pictures changed.
- **The pending change log** no longer credits SEST with the OHP long
  hull's Mk 13 (Modern US Navy fixes it itself; the log says so and that
  SEST's repair is retired), says of the SM-6 only that it keeps 300 s, and
  the Description's count of mods the campaigns name reads 165, as
  REQUIRED-MODS.txt has since 20 Oct.
- **Campaign notes:** a dated section in each campaign's build notes; test
  card rows H.23 (D3's deck) and H.24 (the runtime plugin's state).

## 5. Considered and not changed

- **D3's Juan Carlos deck.** `Default` is the first loadout the hull lists
  and her variant's own, and it shows the author's parked deck where
  `noDeck2` had hidden the static aircraft. No loadout equals `noDeck2`
  (`Empty_deck` also hides the deck crew and equipment), so SEST keeps the
  author's default and the test card asks whether the static models get in
  the way of her own aircraft (H.23); `loadout="Empty_deck"` on her `U()`
  in `campaign_data.py` is the fix if they do.
- **D3's AB 212** flies Squadron1, now dated 1974-87, in 2028; it was
  outside its dates before this update too, and the grey Squadron2 ends in
  2024. Left.
- **US Naval Aviation's pitch limits** reach only the airframes built on
  its files; SEST's F-35C and Super Hornets are left as their winning
  authors have them.
- **[Colibri], [AR-700S5], [IPS CSU 3]:** the Siam Shield's AB 212 and The
  Royal Navy's Oberon, which name them, are placed by no SEST mission and no
  world-campaign force, unlike the Niteroi 2005 that [ZW06] was supplied
  for; the world campaign's buy list sells both, and a bought one sails
  without that sensor. Accepted. Upstream: the Brazilian author could name `eu_zw06`, and
  the Chilean author's [SensorSystem89] numbering on the Williams and the
  PIDAA's Type 675(2) past its sensor count mean neither loads.
- **A second E-3D** at Santiago (the mod now has two tails) and refreshing
  the world campaign adapter's nation table (stale for nine other nations
  too): optional.
- **ExtendedGuidance** stays as shipped, off. Turned on, its own shots
  bypass the game's Pk, decoy and ECM decisions, which SEST Intercept Model
  and the SM-3 and AIM-424 tuning assume; that would be a balance change
  SEST has not calibrated. The 22 Oct log shows it loaded and not started.
- **The 0.8.7 hash** (section 1).
- **The Gallery's unit index** (`Gallery/catalogue.js` and its
  `Gallery/data/*.csv`, shipped in SEST_Gallery and the dist) still lists
  Chile's five renamed hulls under their old ids and source files, and has
  no `ch_ffg_jvh`: `refresh_index.py` stops on 26 older stale records from
  other mods before it reaches them. Its RENAMES now carry the five Chilean
  records over when it next runs; `ch_ffg_jvh` needs indexing as a new
  unit (the script only renames); and `existing-profiles.tsv`'s rows for
  the old Chilean ids stay stale until `tools/list-profiles.ps1` is re-run
  on the PC. Left for a later pass: those unit records feed the Gallery
  pages only, and the encyclopedia pictures come from `profiles.tsv`,
  already on the new ids.
- **Tooling, left for a later pass:** no gate notices the runtime plugin
  being off (a check could read `player.log` for `[SEST Runtime] inactive`
  or compare its hash with `SestRuntimeFixes.cs`); `capture-context.ps1`'s
  problems filter misses `inactive`/`off` lines and still writes a 0.8.3
  header into `game-content.txt`. `packaging-and-recovery.md`'s update
  narrative now reaches 0.8.7, and its step 3 says to read the
  `[SEST Runtime]` line after a game update.

## 6. What to check in game

- `Player.log` after the menu: since the 23 Oct re-gate (addendum), both
  `[SEST Runtime] ... correction installed` lines and no `inactive` line
  on 0.8.7 (play-test guide, section 0; H.24); then a Tomahawk MST ridge
  crossing and a debrief on a save that lost a ship.
- **The world campaign:** start it once on 0.8.7 (Dynamic Campaign Mod
  logs nothing at start). Talcahuano's Type 23s and Thomson boats, Punta
  Arenas's Karel Doorman and the Type 209 stand-ins at Salamis, Golcuk,
  Jinhae and Alexandria should all spawn, each stand-in under its real
  boat's name (Dynamic Campaign Mod logs that a stand-in "sails as its
  class's default hull under that name"). The 2025 Nimitzes embark MH-60R Phase IIs; the Niteroi 2005s
  at Rio have a search radar again.
- **D3 The Relief Ship:** the Juan Carlos's parked deck and her own
  aircraft (H.23).
- **TileGuard:** any `[SEST TileGuard] map tile skipped` line on 0.8.7.
- **Anchorchain:** ExtendedGuidance off in the AC Pack submod menu, and
  every other AC Pack plugin "bereit" in `Player.log` (ExtendedGuidance
  prints nothing while off; CombatWorker reports its native fallback); the new MultiStageMissiles
  stage effects on the SM-6 and other staged rounds are visual only.
- **Missiles:** whether the SM-6 Block I, with its 300 s, reaches past
  240 NM (with the preloader); active-radar missiles under the game's
  261016 fix for recycled ARH tracks, which may make them behave unlike
  the 0.8.6 play tests;
  the RAN NSM, back to the base file's 0.30 defence bonus, intercepted more
  often than in 19-22 Oct play; D10's Gunslinger AIM-174B on U.S. Navy
  2027's figures (discard D10 comparisons flown 19-21 Oct).
- **Other mods on 0.8.7:** (23 Oct: their hooks load again after the
  authors' updates; see the 23 Oct review, section 5.) D8's Valor 73 (H.14)
  and D6's Black Widows, whose runtime hooks are off; the YF-23's new
  ejection is the author's.
- **The Wasp** (allied reserve): F-35B and MV-22B recovery on the new
  circuits.

## 7. Gates and tests

After `python3 tools/build_all.py --from-scratch` (25 packs and the
consolidated dist, 4,304 files, unchanged):

| check | result |
|---|---|
| check_pack_fidelity | pass: 419 files, every byte difference an intended insertion |
| check_campaign_coverage | pass: all 224 enabled mods and SEST packs accounted for |
| check_dependencies | pass |
| check_load_order | pass |
| preflight --all | pass |
| check_weapon_employment | pass: 10,528 contracts |
| check_alias_bases | pass: two pre-existing findings, the round with no base (3755769170's `aces_aim-9m_stdm`) and Spanish Navy Mod (Modern)'s `ae_ssk_s80_plus` firing the undefined `DateBased_HWT` (unchanged by this capture) |
| check_scenarios | pass |
| check_stale_phrases | pass |
| check_inventory | pass |
| check_game_version | pass: every pack 0.8.7 |
| check_vanilla_drift --since e7b32f11 | pass: 7 changed, 8 line endings only, nothing needs a human |

Tests: tools 133 and campaign 299, none skipped (the tools suite's seven
PowerShell tests ran under PowerShell 7.4.6; without `pwsh` on the path
they skip). The campaign pack builds byte-identical under
`PYTHONHASHSEED=4242`.

## Addendum, 23 Oct 2026: the runtime plugin matched to 0.8.7

The owner's export `SEST-map-review-complete-20261023-020525-bfb148.zip`
(7,198,415 bytes, SHA-256 `d77f18e2...`; 142 manifest files verified;
recorded in `data/map-capture-review-20261023.json`) carries
`game-reference/Seapower-Scripts.dll` at SHA-256 `eab2297b...`, the hash
the 22 Oct `Player.log` named. The DLL is not committed. The steps of
section 1 (in full in `integration/runtime-fixes/README.md`) were followed,
adapted where they could not be run as written:

- **Steps 3 and 4, the verifier.** As it stood, `verify_native_api.py`
  failed on 0.8.7 with the API unchanged: ten of its checks compared raw
  signature blobs, whose TypeDef row numbers moved when 0.8.7 inserted
  three types. It now compares decoded type names, and checks every member
  the plugin binds that it never checked (the list in step 3), parameter
  order, inheritance and the terrain sampler's reach: all pass on 0.8.7.
  The 0.8.6 DLL was not to hand, so step 3's run against 0.8.6 could not be
  done; the additions are checked on 0.8.7 only, as its docstring says.
- **Step 5, behaviour.** No IL diff against 0.8.6 was possible; a review of
  0.8.7's own IL replaced it. The terrain correction's assumptions hold:
  the 0.405 nm weapon lookahead, samples through 1.08 nm, `minAltOverSea`
  in place of the land clearance for weapons, all ten stage names. The
  debrief: a Generated or Replaced mission (52 of the 69 in the four
  campaigns) shows the rows saved from the post-mission snapshot, which
  drops destroyed surface hulls, so `TaskForceDebrief` stays on rather than
  retiring. A mission played as authored (the other 17) marks a player
  unit Lost only from its `Mission_<i>_<tag>` `IsDestroyed` record, which
  the game writes only for a unit with a `CampaignTag`; no SEST mission
  file tags a player unit, so by 0.8.7's code a ship sunk there is listed
  as Undamaged, and the plugin, which reads the same record, cannot add a
  Lost row either. Tagging those units is separate work. The plugin skips
  an id already shown, so no ship is listed twice.
- **Steps 6 and 7.** `SestRuntimeFixes.cs` accepts `eab2297b...` only, not
  0.8.6 as well: Steam has moved every player on. `sest_runtime.ini` and
  `SEST_RUNTIME_README.txt` say 0.8.7, and the README's debrief paragraph
  says which missions the correction fills in and why the ones played as
  written show no loss. The mocked tests take the game's shapes (nested
  `FlightStage` and `CrewSkill`, a read-only snapshot, the competing
  `readValue` overloads) and pin the no-op over a loss the native rows
  already list: 38 assertions. `build_plugin.py`,
  under Ubuntu 24.04's mcs 6.8.0.105 unpacked into a prefix, rebuilt
  `SEST.RuntimeFixes.dll` as `c844a759...` (was `9aa55df8...`), the same
  bytes on a second run.
- **Text.** The pending change log has its Tomahawk MST and debrief lines
  back, the debrief's narrowed to missions you pick a force for, with a
  note to check `Player.log` before Submit and to drop a correction's line
  if it is not installed (7,901 characters with the 19 Oct block, 7,993
  counting each line break as two). FEATURES, the play-test guide
  (section 0), `packaging-and-recovery.md`, the Southern Watch, Red Line
  and Southern Reach build notes and test card H.24 say the plugin is
  matched to 0.8.7, and H.24 records what section 3 shows after O2;
  section 6's first item above is now "both `correction installed`
  lines". The Steam card is
  unchanged: "Sea Power 0.8.7: every pack rebuilt for it" stays true, and
  the README keeps the corrections off it until the PC has shown both lines.
- **Still to do, on the PC:** sync; `Player.log` must show both
  `[SEST Runtime] ... correction installed` lines and no `inactive` line;
  then H.24 and the acceptance tests in
  `docs/playtests/fleet-terrain-debrief-20261020.md` (a Tomahawk MST ridge
  crossing, the debrief of a Generated mission that lost a ship, and an
  older debrief reopened after a reload). Neither correction has yet been
  watched working, on 0.8.6 or 0.8.7.

After `python3 tools/build_all.py --from-scratch` (25 packs and the
consolidated dist, 4,304 files, unchanged in number; the only built files
that changed are the plugin's DLL, README and ini in `SEST_Campaign` and
the dist) all twelve gates of section 7 pass with the same results, and the
tests: tools 133 (`test_runtime_plugin` included; seven PowerShell tests
skipped, `pwsh` not on the path) and campaign 299.
