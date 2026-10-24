# Workshop refresh, 23 October 2026

One capture on the PC, `87c0feb5` ("chore: capture workshop refresh
2026-10-23"), fast-forwarded on top of `28f62cd3`, the last built and
pushed SEST state, and taken with `28f62cd3` installed (`environment.txt`;
StreamingAssets holds the dist's 4,304 files). No game update: Sea Power is
still 0.8.7 Build 261021 (Steam build 26103404). **Eight author updates**,
no mod added or removed (199 Workshop mods, 200 Mod Manager entries with
the pack; 191 unchanged). The exporter's update check lists seven
(`workshop-updates.txt`, "unchanged ... 192"): the YF-23's update changed
only its DLL, and the check fingerprints text files only. Steam's own update
time and `plugin-dlls.txt` show it.

The facts are in `data/install-snapshot/workshop-refresh-summary.txt`
(regenerated for this capture); this is the judgement. Two readers took the
capture (the units and configs; the plugins, logs and player-facing text)
and tested in scratch worktrees. Every claim acted on below was re-read
against the tree here, and the whole of it was rebuilt from scratch.

Nothing in the capture breaks SEST's build or a gate, and no built file
changes: the capture touched only `mods-source/` and
`data/install-snapshot/`, and SEST forks none of the changed files. What
needed work was records, and one pending change-log sentence that the
authors' updates made untrue.

## 1. Other mods' code on 0.8.7, again

The 22 Oct review (section 1) recorded six components that switched
themselves off against 0.8.7's game assembly. All six authors updated on
23 Oct, for the same game build, and each now passes its own check and
loads as it did on 0.8.6 (the 20 Oct capture, `87b43e03`):

| Mod | DLL (`plugin-dlls.txt`) | 22 Oct `Player.log` | 23 Oct `Player.log` |
|---|---|---|---|
| Anduril FQ-44 Fury (3804868806) | XQ58Shadow 1.2.4 -> 1.2.5 | "Startup failed: ... Unsupported game assembly" | "Loaded; native optics, shadow contact and tracking enabled": Drone Control's Watch, Shadow and camera feed are back |
| EC-2 Stand Off Jammer (3813033771) | EC2CommsJamming 1.0.1 -> 1.1.1 | "off: verdict HookChanged" | "on: verdict UnchangedContract, 37 of 37 patches installed": radio and data-link jamming are back |
| Anduril Maritime Drones (3819522350) | K5KrakenContactStrike 1.0.0 -> 1.0.1 | "K5 contact strike off until a mod update" | "stays on", 8 Harmony hooks: the one-way-attack K5 releases its charge again |
| Saronic Corsair ASV (3766210676) | SaronicCorsairStrikeUSV 4.12.1 -> 4.12.2 | "Order hooks unavailable; original polling retained" | "stays on", 8 Harmony lifecycle hooks |
| MV-75 Cheyenne II (3810611344) | BellSystemsFixtureTilt 0.5.1 -> 0.5.2 | "systems off until a mod update" | "stays on" |
| YF-23 Black Widow II (3796349767), and the Fury's copy | AlpineSeaPower 0.3.1 -> 0.3.2, both copies byte-identical | "patches off until a mod update" | "stays on"; launchangles, salute and deckstate installed |

Three plugins still print their old version in their own start-up line
("Contact controller 4.12.1", "Contact controller 1.0.0", "0.5.1
initialized"). The file versions and hashes in `plugin-dlls.txt` and
BepInEx's "Loaded assembly ... Version=" lines are the record, and the
catalog notes quote those.

New, all loading: EC2Ejection 1.0.0 ("[EC-2 Ejection] loaded."), and the
MV-75's CheyenneCabinJoints 1.0.0, CheyenneDoorLining 1.0.0 and
MV75CrewEscape 1.0.1 (a BepInEx "Loaded plugin" line each, nothing in
`Player.log`). Unchanged and still on: FuryFormation, FuryLights,
FuryVoice, EC2Formation, EC2Lights, EC2Tooltip, MV75Formation,
YF23Ejection, YF23Formation and YF23Lights. The BepInEx log's distinct
warning and error lines are identical to the 22 Oct capture's, so the new
plugins add none.

**SEST's own plugins.** `Player.log` shows both `[SEST Runtime] ...
correction installed` lines and no `inactive` line, and the installed
`SEST.RuntimeFixes.dll` (`c844a759...`) and `SEST.MenuBackground.dll`
(`a1003674...`) are the dist's. That puts in the repository the owner's
23 Oct check after syncing `990dd7f9`. Neither correction was exercised:
the session stopped at the main menu, and the earlier one
(`player-prev.log`) shows no SEST plugin output at all. H.24 and the
acceptance tests in `docs/playtests/fleet-terrain-debrief-20261020.md` are
still open.

**The problems files.** `player.problems.txt` has three hits, down from
four. Saronic's and XQ58Shadow's lines are gone. CombatWorker's native
fallback (the SecondThrust conflict) and IDX's missing localisation file
are as before. The third is SEST's own debrief line, caught by the word
"missing" in "missing from section 3": a false positive, as it was in
`player-prev.problems.txt` on 22 Oct.

## 2. The updates

| Mod | Change | SEST |
|---|---|---|
| Euromod - Modern JMSDF (3695809489), v41 | The SH-60J and SH-60K gain modex numbers: a Modex submodel (`zapper.obj`'s `modex_jmsdf` mesh on the numbers material) and nine serial textures per squadron. The squadron comments name the HS-21 and HS-22 flights. The SH-60J's Squadron1 and Squadron2 take the plain `sh-60j.png` livery (Default keeps `sh-60j_hs21`). ApproximateVersion 0.8.0 -> 0.8.5 (information only to `check_game_version`). | Default, Squadron1 and Squadron2 keep their names, so everything SEST names still resolves: SEST JMSDF Mogami's `jmsdf_sh-60k=Default` and SEST Replenishment's Asahi, Atago and Maya forks' `jmsdf_sh-60j=Default`, the Southern Watch and Southern Reach rosters, SW10 Common Sea's and O9 Viper Zero's Squadron1, and the Banda and Northern Front seeds. Cross-Deck and the world campaign name only the ids. Visual only in play. |
| Saronic Corsair ASV (3766210676) | SaronicCorsairStrikeUSV 4.12.2 (section 1). `usn_steelfin`'s English description is reworded. | Steelfin's own copy, now the same text, wins. O5 Paper Trail's Corsair scout is unaffected. |
| Anduril FQ-44 Fury (3804868806) | All six airframes take new airframe materials (`fury_airframe_surface.ini`, `fury_airframe_surface2.ini`; files 59 -> 61), and ten marking and insignia submodels leave `[Submodels]`. XQ58Shadow 1.2.5 and AlpineSeaPower 0.3.2 (section 1). `SENSOR_CONTROLS.txt`: the controls appear only for a player-owned aircraft airborne in a mission. | No loadout, station, sensor, round or squadron changed. D6 Long Reach's Fury 61 (AirToAir) and Fury 62 (Empty) and Collection Fixes' `fury_aim424` extend rebuild identical. |
| MV-75 Cheyenne II (3810611344) | Both airframes: `Pilot=wp_pilot_d`, two pilot positions, EjectChance 0 -> 1, EjectDelay 0.3 s. BellSystemsFixtureTilt 0.5.2 and three new plugins (section 1). | D8 The Long Perimeter's Valor 73 keeps her Transport fit. If shot down, she should now eject her crew. |
| EC-2 Stand Off Jammer (3813033771) | `jasdf_ec-2`: `Pilot=wp_pilot_d`, two pilot positions, EjectDelay 0.6 s (no EjectChance key); its eight cockpit pilot meshes hide with the damage model. EC2CommsJamming 1.1.1 and the new EC2Ejection (section 1). | O9's Jammer 71 keeps Squadron2 and the EW fit. With comms jamming back, she should jam radio and data links as well as the frigate's search radar her briefing names (not yet seen in game). That adds to the briefing and does not contradict it. |
| Anduril Maritime Drones (3819522350) | K5KrakenContactStrike 1.0.1 (section 1). `usn_steelfin`'s description is reworded, as on the Corsair. | Paper Trail's reconnaissance K5 is unaffected. |
| Steelfin (3820576916) | Adds `LICENSE.txt` (files 19 -> 20): RSG's proprietary licence. | No unit, round or system changed. Section 4 covers the licence. |
| YF-23 Black Widow II (3796349767) | AlpineSeaPower 0.3.2 only (section 1). No exported file changed. | The airframe, `yf23_aim424_internal` and Collection Fixes' extend are unchanged. |

## 3. What was done

No build input changed. `build_all --from-scratch` reproduces the tree byte
for byte. The changes:

- **The pending 20 Oct change log** (`docs/campaigns/southern-watch/workshop-listing.md`).
  The bullet saying 0.8.7 "switched off parts of other mods' code until
  their authors update" (with the Corsair falling back to its original
  order handling) is replaced. The new bullet says the 23 Oct updates put
  each of them back on and that SEST needed no change. Its section is now
  "Sea Power 0.8.7 and the 22-23 October mod updates". The log is 7,854
  characters with the 19 Oct block (7,946 counting each line break as two),
  and `test_workshop_listing` passes. The notes above the log now cover the
  23 Oct updates, the capture's two `[SEST Runtime]` lines, and the
  required mods (unchanged).
- **A guard.** `tools/check_stale_phrases.py` (now 15 phrases) keeps the
  retired sentence, "until their authors update" and the Corsair's
  fall-back out of the player's text.
- **The 22 Oct review** keeps its text, as its own addendum did. Section
  1's table, section 2's YF-23 row and section 6's "Other mods" item are
  marked superseded on 23 Oct, pointing here.
- **Data:**
  - dated 23 Oct notes on eight catalog entries (the seven whose files
    changed, and the YF-23);
  - `docs/mod-catalog.md` regenerated;
  - the fingerprints rebased (`python3 tools/fingerprint_mods.py`: 199
    mods, all match). Seven moved. The YF-23 did not, because its update
    was code only;
  - the refresh summary regenerated: eight Workshop updates, seven changed
    and four new third-party plugin DLLs.
- **Steelfin's catalog entry** said "No SEST mission places its units".
  That has been untrue since 18 Oct, when Southern Watch O10 Ballistic
  Shield began placing `usa_steelfin_launcher` (its coverage credit). The
  23 Oct note corrects it.
- **Records of the runtime plugin.** `integration/runtime-fixes/README.md`
  (*On the PC (23 Oct 2026)*) adds the capture's evidence.
- **Southern Watch build notes:** a dated section on what differs in play.
- **Steam cards:** unchanged. No card line is false. The latest-update
  card's "Sea Power 0.8.7 / packs and runtime fixes matched" is about
  SEST's own plugin, and no card mentions other mods' code.

## 4. Considered and not changed

- **Licences.** Steelfin now ships RSG's proprietary licence. It lets a
  compatibility patch "add content alongside this mod, provided [it does]
  not copy, replace, override, or redistribute Original Project Material".
  SEST ships no Steelfin file. Collection Fixes' loadout name
  `Steelfin=Steelfin`, written on 16 Oct (before Steelfin was subscribed)
  for the YF-23, Fury and MV-75 fits, has the same key and text as
  Steelfin's own. It is a one-line name, not Steelfin's material.

  Not new in this capture: the Fury's and the YF-23's licences (in the
  export since 5 Oct) carry the same clause. SEST Collection Fixes ships
  Anchor Chain `#!extend` overrides of their AIM-424s
  (`ammunition_overwrite/fury_aim424_SEST.ini` and
  `yf23_aim424_internal_SEST.ini`, since 14 Oct, the player's decision).
  The catalog gave the licence as the reason SEST forks nothing of the
  EC-2, the Corsair and the Maritime Drones, but recorded no licence for
  the Fury or the YF-23 until today's notes. Whether the two extends need
  RSG's permission, or stay as a recorded exception, is for the owner.
  Nothing was changed.

  **Decision (23 Oct 2026, the owner): a known exception.** The two extends
  stay as they are, and RSG is not asked first. The record is here, in the
  Fury and YF-23 catalog notes, in `docs/conflicts-and-load-order.md`
  ("Four AIM-424s") and beside the AIM-424 build in
  `integration/collection-fixes/build_patch.py`. If RSG asks, those two ids
  come out of the AIM-424 build and the rounds fly as their author shipped
  them; the Workshop description already offers any author that.
- **The JMSDF textures.** `sh-60j.png`, the `modex_jmsdf` mesh and the
  serial-number textures are not in the export. Whether they exist on the
  PC is left to the next play test (section 5); if one is missing, only
  paint or numbers are lost.
- **The ejecting crews** are the authors' features, not SEST's, so they
  are not in SEST's change log. Whether rescue plugins such as Automatic
  SAR react to them has not been seen.
- **O9's briefing** keeps "blind the frigate's radar". It is still true;
  the comms jamming adds to it.
- **Tooling, left for a later pass:**
  - The exporter's `-CheckUpdates` fingerprints text files only, so it
    cannot see a DLL-only update such as the YF-23's. Steam's
    `appworkshop_1286220.acf` and `plugin-dlls.txt` caught it, and the
    refresh summary reads both.
  - `capture-context.ps1`'s problems filter matches SEST's own "...
    missing from section 3" success line. It should skip `[SEST Runtime]
    ... correction installed` lines. It already misses `inactive` and
    `off` lines (22 Oct review, section 5).
- **The vanilla drift baseline** stays `1bda58a6`, the 0.8.7 export. This
  capture did not touch `mods-source/_vanilla/`.

## 5. What to check in game

- **D6 Long Reach:** the Furys' new grey finish, without separate markings.
  Drone Control should be offered on a player-owned Fury in flight; the
  mission does not use it.
- **D8 The Long Perimeter (H.14):** Valor 73 is present. If she is shot
  down, her crew eject.
- **O9 Viper Zero:** Jammer 71 jams radio and data links as well as radar
  (the "[EC2 Comms] on" line), and her crew eject if she is shot down.
  Hyuga Flight's SH-60K shows modex numbers.
- **SW10 Common Sea:** the SH-60K's and SH-60J's modex numbers and the
  SH-60J's plain livery, with no missing texture.
- **O5 Paper Trail:** the Corsair scout and the reconnaissance K5 behave as
  before; neither makes a contact attack.
- **`Player.log`:** the six plugins of section 1 load as they do here.
  Both `[SEST Runtime] ... correction installed` lines appear; then run H.24
  and the acceptance tests.

## 6. Gates and tests

After `python3 tools/build_all.py --from-scratch` (25 packs and the
consolidated dist, 4,304 files, unchanged), with `git status` showing no
built file changed:

| check | result |
|---|---|
| check_pack_fidelity | pass: 419 files, every byte difference an intended insertion |
| check_campaign_coverage | pass: all 224 enabled mods and SEST packs accounted for |
| check_dependencies | pass |
| check_load_order | pass |
| preflight --all | pass |
| check_weapon_employment | pass: 10,528 contracts |
| check_alias_bases | pass: the same two pre-existing findings (`aces_aim-9m_stdm` with no base; `ae_ssk_s80_plus` firing the undefined `DateBased_HWT`) |
| check_scenarios | pass: 11 scenarios, 348 sections |
| check_stale_phrases | pass: 15 phrases |
| check_inventory | pass: 199 + 1 = 200 |
| check_game_version | pass: every pack 0.8.7 (JMSDF's ApproximateVersion 0.8.5 is information only) |
| check_vanilla_drift --since 1bda58a6 | pass: 4,049 files then and now, none changed |

Tests: tools 137 (seven PowerShell tests skipped, `pwsh` not on the path)
and campaign 299. The campaign pack builds byte-identical under
`PYTHONHASHSEED=4242`.
