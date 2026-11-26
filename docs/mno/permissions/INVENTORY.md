# MNO third-party permissions: inventory (25 Nov 2026)

Drafted for the owner of Modern Naval Operations (MNO, SEST-DEV). Nothing here has been sent. It implements the decision in `docs/mno/OWNER-DECISIONS-20261125.md`: draft permission requests for the third-party material, keep the material as it is, and hold the public post until the requests are answered.

Files in this folder:

- `INVENTORY.md`: this file.
- `drafts/NN-<author>.txt`: one message per author group that needs permission, ready to paste (a Steam comment holds 1,000 characters, so most drafts go in a Steam DM, or in two comments).
- `TRACKER.csv`: one row per request for the owner to fill in.
- `FILE-LIST.csv`: every shipped file that derives from another author's file, with its source file, share of the author's content, the SEST pack that made it, why, and the evidence.
- `PHOTOS-SOURCE-SEARCH.md`: the 21 owner-supplied photos with no recorded source.
- `method/`: the scripts that rebuilt this inventory. They only read the repo, apart from this folder. Run them in this order: `derive.py derive.json`, `parse_credits.py`, `final.py`, `write_docs.py`, `write_docs2.py`. Intermediate JSON goes beside the scripts.

## 1. Result

Shipped item: `integration/dist/SEST_Integration/`, 4,930 files (the same count as `docs/releases/20261107/upload-manifest.json`).

| Class | Files | Meaning |
|---|---|---|
| Verbatim copy | 10 | Byte-identical (or identical apart from line endings) to the author's file. All are Greene's RAAF F-35A: 5 model and texture files and 5 .ini files |
| Close adaptation | 552 | Mostly the author's content with SEST edits (supply blocks, loadouts, fixes, renamed copies) |
| Override of an author's file with SEST values | 2 | The 2 RSG AIM-424 files: no RSG text, but they override RSG files, which RSG's licence forbids without permission |
| Game's own file, patched | 58 | Derived from Sea Power's own data (`mods-source/_vanilla/original`), not from a mod author. Outside this request |
| SEST-original | 4308 | Campaigns, missions, gallery, plugins, SETUP, and patches that only name another mod's units, such as `#!extend` overrides and cross-deck lists. No permission needed |

Author groups: **48** requests (drafts 01-47, with 02 covering two things). That is 41 groups whose files MNO carries, R.A.T.S. (Topographic Map adapter), Bungalow (Dynamic Campaign Mod, draft 42), and 5 authors whose DLLs SEST's loader adapts on 261123 (drafts 43-47). The Euromod team's draft 02 also covers the 5 DLLs adapted in their Anchorchain Expansion Pack. One group, Pog Frog, has a licence that already allows it. 20 more Workshop items are only referenced by SEST-original files (section 4).

**Revision 25 Nov 16:10 UTC.** The first version counted only authors whose *files* MNO carries, so it left out Bungalow and every author whose DLL SEST adapts without shipping it. Both are added below (3.5, 3.6). Check used: every `AssemblyAdapters.*.cs` in `integration/beta-anchorchain/source/`, each mapped to its Workshop item by SHA-256 against the 261123 and 19 Nov captures, plus every `runtime/*.cs` that hooks another mod by name.

### How close this is to '~550 files from 67 author groups'

- **550** is the measured list in the shipped `CREDITS.txt`, written by `tools/consolidate_packs.py` (`credits_text`): every shipped file in a unit folder (aircraft, vessels, land_units, ammunition...) that difflib finds 90 % or more like a mod file of the same kind. That list has 550 files in **66** Workshop items. I could not find a 67th. The earlier count was probably by Workshop item, not by author, and may have counted one item twice or added Greene's model files as a separate entry. That analysis is not in the repo, so this is a guess.
- This inventory finds **562 author-derived files in 66 Workshop items**, which come from **40 authors or teams** (several authors own more than one item: Mitchell600 has 7, ManeuverWarfare 6, misaka 6), plus RSG's 2 override files.
- From the 550 to 562: **21 CREDITS rows are not an author's file.** `check_pack_fidelity.py` resolves 17 of them to the game's own file: 15 hulls SEST forks from vanilla that CREDITS credits to RE-power (3605013271), plus `wp_ss-n-14b` and `rfn_aor_pashin`. The other 4 match the game's own file line for line: `damage.ini`, `knm_terne_shell.ini`, `rn_squid_shell.ini` and `usn_ssq-47.ini`. Then **33 files CREDITS does not measure are added**: Greene's 5 model and texture files and the other files outside unit folders (animations, `f-35a_mat.ini`, `systems/`, `language_*`, `ui/Default`), plus unit files between 50 % and 90 % alike (squadron files, the Block III Super Hornet, ammunition). 550 - 21 + 33 = 562.
- CREDITS.txt credits RE-power (3605013271) and the Alizé mod (3628203171) for files that are really the game's. That credit costs nothing and can stay. Neither item needs a request.

### Method (evidence)

1. Every shipped file is mapped to the SEST pack that built it (`integration/*/SEST_*`, the inputs of `tools/consolidate_packs.py`).
2. **Replenishment pack (452 files):** the upstream of each file comes from `tools/check_pack_fidelity.py`'s own `upstream_for()` (the builder's load-order resolution). That checker passes on this tree: 'every byte difference is an intended insertion'. So each file is exactly its upstream plus SEST's supply block or reload lines. Its 8 generated `_variants` files have no upstream and count as SEST-original. Where the upstream is `mods-source/_vanilla/original`, the file is the game's.
3. **Every other text file** is compared with each same-named file (and its `#!extend` target) in `mods-source/<id>/` and `mods-source/_retired/<id>/`, and with the game's file in `_vanilla/original`. Measure: the share of the shipped file's content lines (no comments, no bare section headers) found in the source. 'Close' means 50 % or more, and at least 3 lines, are the author's. Where the game's file explains as many lines (90 % or more), the file counts as the game's.
4. **Renamed copies** (for example RAAF airbases built from `airfield_us_large.ini`) come from the CREDITS.txt measurement (difflib ≥ 90 %), each re-checked against the game's file of that name.
5. **Binary files:** `mods-source` is a text-only export, so binaries were matched by SHA-256 against `integration/raaf-f-35a-jatm/recovered/` (Greene). All other shipped binaries are SEST's: photos and pictures made from the gallery, ribbons, SEST DLLs, and the menu film.
6. Two manual calls, both recorded in `FILE-LIST.csv`. `systems/weapons.ini` is a section merge that is mostly the game's own text (890 of 1,055 lines), so it counts as the game's. `systems/sest_weapon_costs.ini` (49 %) counts as a close adaptation of the Combat Cost Tracker, like its sister files (75 %), because it keeps the tracker's prices.
7. Authors come from `data/mod-catalog.json`, `_info.ini`, `CREDITS.txt` and the items' own Credits/LICENSE files.

## 2. Author groups

Status key: **needs permission** = no licence found that allows copying or overriding the files; **licence already allows** = the author's own text allows it (cited); **no permission needed** = section 4.

| # | Author group | Workshop items (files) | Verbatim / close / override | Example paths | Licence found | Evidence | Status | Draft |
|---|---|---|---|---|---|---|---|---|
| 1 | cent | Red Storm Arsenal (3413868677): 130 | 0 / 130 / 0 | `aircraft/usaf_b-52o.ini`, `ammunition/plan_cj_10a.ini`, `ammunition/plan_yj12_ship.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 122 by replenishment; 4 by collection-fixes; 3 by intercept-model; 1 by b52-arrw; fidelity-checked upstream | needs permission | 01-cent.txt |
| 2 | Mitchell600 / Euromod team | Euromod - Main Pack (3629144864): 33<br>Modern US Navy (3390330875): 33<br>Euromod - Modern Royal Australian Navy Mod (3820759806): 10<br>Euromod - Modern Italian Navy (3488139470): 10<br>Euromod - Modern Japanese Maritime Self Defence Force (3695809489): 7<br>Euromod - Modern Dutch navy (3444379330): 7<br>Euromod - Modern Nordic Navy (3642656500): 5 | 0 / 105 / 0 | `aircraft/adf_ah-64e.ini`, `aircraft/raaf_fa-18a_2011.ini`, `aircraft/raaf_fa-18f.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 89 by replenishment; 6 by collection-fixes; 5 by allied-fixes; 4 by ran-fleet; 1 by a10c-plus; fidelity-checked upstream | needs permission | 02-mitchell600.txt |
| 3 | misaka | F-22 Raptor (3418252667): 20<br>United States Naval Aviation (3737267013): 10<br>AH-64 Apache (3425450153): 6<br>A-10C (3459682829): 3<br>A-10A Thunderbolt II (3414146266): 2<br>French Helicopter Package (3567228449): 1 | 0 / 42 / 0 | `aircraft/uk_ah_mk_1.ini`, `aircraft/usa_a-10a.ini`, `aircraft/usa_a-10c.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 17 by raaf-bases; 9 by allied-fixes; 5 by collection-fixes; 3 by raptor-squadrons; 3 by growler-ngj-malice; 2 by a10c-plus; 1 by f-35c-jatm; 1 by world-sandbox; 1 by f-15ex-revamp | needs permission | 03-misaka.txt |
| 4 | 八一of军魂 | Modern PLAN Systems (3775128499): 39 | 0 / 39 / 0 | `ammunition/plan_48n6e1.ini`, `ammunition/plan_cj-10.ini`, `ammunition/plan_hhq-9b.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 39 by replenishment; fidelity-checked upstream | needs permission | 04-author-of-3775128499.txt |
| 5 | Author of the Euromod South Korea and HD Hyundai add-ons (name not recorded) | Euromod-South Korea Navy (3789208859): 17<br>Euromod-HD Hyundai Export Ships Mod (3812454152): 12 | 0 / 29 / 0 | `ammunition/ko_Antiship_2.ini`, `ammunition/rok_L-sam.ini`, `ammunition/rok_harm-II.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 28 by replenishment; 1 by intercept-model; fidelity-checked upstream | needs permission | 05-euromod-south-korea-navy-euromod-hd-hyundai-export.txt |
| 6 | ManeuverWarfare | Virginia-, Seawolf-, and Ohio-class Submarines (3433957933): 7<br>Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes) (3468260539): 5<br>Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies) (3461044389): 4<br>Type 003 Fujian / Type 004 CVN Aircraft Carriers (3486502935): 3<br>PLAN Submarines (3594891803): 1<br>Y-20 / KJ-3000 (3782020901): 1 | 0 / 21 / 0 | `ammunition/pla_yj-19_mw.ini`, `ammunition/plaaf_kd-88.ini`, `land_units/plaaf_airlift_airbase.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 18 by replenishment; 3 by collection-fixes; fidelity-checked upstream | needs permission | 06-maneuverwarfare.txt |
| 7 | Prof_CH4OS | U.S. Navy 2027 Capabilities mod (3606774881): 19<br>F-35C Lightning II Alt. Loadouts (3607989779): 2 | 0 / 21 / 0 | `aircraft/usn_ea-18g.ini`, `aircraft/usn_f-35c.ini`, `aircraft/usn_fa-18e.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 13 by replenishment; 3 by growler-ngj-malice; 2 by allied-fixes; 2 by collection-fixes; 1 by f-35c-jatm; fidelity-checked upstream | needs permission | 07-prof-ch4os.txt |
| 8 | Chevron 9 | Euromod - Modern German Navy (3575847216): 17<br>Combat Cost Tracker (3807187341): 3 | 0 / 20 / 0 | `systems/sest_aircraft_costs.ini`, `systems/sest_vessel_costs.ini`, `systems/sest_weapon_costs.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 17 by replenishment; 3 by combat-costs; fidelity-checked upstream | needs permission | 08-chevron-9.txt |
| 9 | Author of The Luzon Line and The Siam Shield (name not recorded) | Thailand: The Siam Shield (3711297532): 15<br>Philippines: The Luzon Line (3752415457): 4 | 0 / 19 / 0 | `vessels/phl_ff_hamilton.ini`, `vessels/phl_fs_pohang.ini`, `vessels/phl_lpd_tarlac.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 19 by replenishment; fidelity-checked upstream | needs permission | 09-philippines-the-luzon-line-thailand-the-siam-shiel.txt |
| 10 | Spanish Navy Mod team (Jabeitor, Zzocalu, Jasoriab) | Euromod - Cold War Spanish Navy (3630495619): 11<br>Euromod - Modern Spanish Navy (3731208477): 8 | 0 / 19 / 0 | `vessels/ae_ao_teide.ini`, `vessels/ae_cvl_dedalo.ini`, `vessels/ae_cvl_dedalo_late.ini` | None for the .ini files. Credits.txt in both items lists model permissions (Jason Simpson, Desdemicabina, Badcat109, CC BY / CC BY-NC-SA sources); MNO ships none of those models. | 16 by replenishment; 3 by ran-fleet; fidelity-checked upstream | needs permission | 10-jabeitor.txt |
| 11 | Author of Royal Australian Defence Forces (name not recorded) | Royal Australian Defence Forces (3455404959): 18 | 0 / 18 / 0 | `aircraft/S-70B-2_Seahawk_squadrons.ini`, `ammunition/sest_agr-30_pod19.ini`, `land_units/airbase_raaf_amberley_variants.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 15 by raaf-bases; 2 by allied-fixes; 1 by collection-fixes | needs permission | 11-royal-australian-defence-forces.txt |
| 12 | Greene | RAAF F-35A Lighting II (3514484654): 16 | 10 / 6 / 0 | `aircraft/raaf_f-35a.ini`, `aircraft/raaf_f-35a_squadrons.ini`, `ammunition/raaf_f-35_gun_pod.ini` | None found. The 4 Oct 2026 export (mods-source/_retired/3514484654) has no licence or readme; the model and textures come from a copy recovered on 5 Oct 2026 (integration/raaf-f-35a-jatm/recovered/SHA256SUMS). | 15 by raaf-f-35a-jatm; 1 by allied-fixes | needs permission | 12-greene.txt |
| 13 | Pointinthevoid | Russian Navy 21 (3597650470): 15 | 0 / 15 / 0 | `ammunition/rfn_3m14.ini`, `ammunition/rfn_3m22.ini`, `ammunition/rfn_3m54.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 15 by replenishment; fidelity-checked upstream | needs permission | 13-pointinthevoid.txt |
| 14 | 5_12 | Euromod - Modern British Navy (3599752717): 12 | 0 / 12 / 0 | `vessels/rn_ddg_type45.ini`, `vessels/rn_ddg_type45_22.ini`, `vessels/rn_ddg_type45_26.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 11 by replenishment; 1 by allied-fixes; fidelity-checked upstream | needs permission | 14-author-of-3599752717.txt |
| 15 | dingtools | F-15 EX Eagle II (3636386513): 3<br>B-52H Stratofortress (3741944366): 2<br>B-1B Lancer (3652097318): 1 | 0 / 6 / 0 | `aircraft/dts_b-52h.ini`, `aircraft/usaf_b-1b_dts.ini`, `aircraft/usaf_f-15ex_SEII.ini` | Partial: mods-source/3741944366/assets/readme.txt says 'You can use these weapons freely in seapower, but please DO NOT re-upload them or copy the models to other places!'; mods-source/3652097318/.../agm-158/README.txt: 'Commercial use or reproduction is prohibited without permission'. Neither covers copying the .ini files into another item, so ask. | 4 by b52-arrw; 2 by f-15ex-revamp | needs permission | 15-dingtools.txt |
| 16 | MyGo!!!!!鼓手椎名立希 | 1143.5 Kuznetsov (3438479626): 3<br>General Atomics MQ-9 Reaper (3503670861): 2<br>Lockheed AC-130 Pack (3559495372): 1 | 0 / 6 / 0 | `aircraft/usaf_mq-9_er.ini`, `aircraft/usaf_mq-9a.ini`, `ammunition/usn_cal_30mm.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 3 by replenishment; 2 by allied-fixes; 1 by collection-fixes; fidelity-checked upstream | needs permission | 16-mygo.txt |
| 17 | Cropgun | F/A-18 Murder Hornet with AIM-174B (3430135740): 5 | 0 / 5 / 0 | `aircraft/usn_ea-18g_squadrons.ini`, `aircraft/usn_fa-18f_blk3_squadrons.ini`, `aircraft/usn_fa-18f_squadrons.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 4 by growler-ngj-malice; 1 by replenishment; fidelity-checked upstream | needs permission | 17-cropgun.txt |
| 18 | ltjgbeam | Chinese Navy (PLAN) (3417801942): 4 | 0 / 4 / 0 | `vessels/plan_ddg_luda_typ_051.ini`, `vessels/plan_ddg_luda_typ_051d.ini`, `vessels/plan_ddg_luda_typ_051dt.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 4 by replenishment; fidelity-checked upstream | needs permission | 18-ltjgbeam.txt |
| 19 | Author of French Air Force (name not recorded) | French Air Force (3758943352): 3 | 0 / 3 / 0 | `aircraft/fr_rafale_b_l.ini`, `aircraft/fr_rafale_c_l.ini`, `aircraft/fr_rafale_m_l.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 3 by rafale-f5 | needs permission | 19-french-air-force.txt |
| 20 | aaaaaaaaaaaaaaaabcd | Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke) (3395022688): 2 | 0 / 2 / 0 | `ammunition/wp_ss-n-12.ini`, `ammunition/wp_ss-n-19.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by replenishment; fidelity-checked upstream | needs permission | 20-aaaaaaaaaaaaaaaabcd.txt |
| 21 | Author of ARRW (AGM-183) (name not recorded) | ARRW (AGM-183) (3502273861): 2 | 0 / 2 / 0 | `aircraft/usaf_b-52h_419_flts.ini`, `ammunition/usn_arrw.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by b52-arrw | needs permission | 21-arrw-agm-183.txt |
| 22 | Author of Mogami-class Frigate (name not recorded) | Mogami-class Frigate (3456859157): 2 | 0 / 2 / 0 | `vessels/js_ffg_mogami.ini`, `vessels/js_ffg_mogami_improved.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by jmsdf-mogami; 1 by replenishment; fidelity-checked upstream | needs permission | 22-mogami-class-frigate.txt |
| 23 | Author of Pakistani Pack (name not recorded) | Pakistani Pack (3812140001): 2 | 0 / 2 / 0 | `ammunition/plan_cm-302.ini`, `ammunition/plan_yj-18e.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by replenishment; fidelity-checked upstream | needs permission | 23-pakistani-pack.txt |
| 24 | Author of Road Mobile ICBMs (Topol-M, DF-41) (name not recorded) | Road Mobile ICBMs (Topol-M, DF-41) (3571718093): 2 | 0 / 2 / 0 | `land_units/pla_df-41_tel.ini`, `land_units/wp_ss-27_tel.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by collection-fixes | needs permission | 24-road-mobile-icbms-topol-m-df-41.txt |
| 25 | Author of Royal Navy Type 23 'Duke Class' Frigate [OLD] (name not recorded) | Royal Navy Type 23 'Duke Class' Frigate [OLD] (3378409795): 2 | 0 / 2 / 0 | `vessels/rn_type23.ini`, `vessels/rn_type23_refit.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by replenishment; fidelity-checked upstream | needs permission | 25-royal-navy-type-23-duke-class-frigate-old.txt |
| 26 | flankymanga | Modern Chinese Airbase (Large) (3631042692): 1<br>Modern Russian Airbase (Large) (3629269283): 1 | 0 / 2 / 0 | `land_units/pla_airbase_modern.ini`, `land_units/wp_airbase_modern.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by collection-fixes | needs permission | 26-flankymanga.txt |
| 27 | Kirameki | Boeing P-8 Poseidon (3602046770): 2 | 0 / 2 / 0 | `aircraft/usn_p8.ini`, `aircraft/usn_p8_squadrons.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by allied-fixes | needs permission | 27-kirameki.txt |
| 28 | RSG (maintainer AlpineStatic) | Anduril FQ-44 Fury US Navy Carrier Wingmen (3804868806): 1<br>YF-23 Black Widow II (3796349767): 1 | 0 / 0 / 2 | `ammunition_overwrite/fury_aim424_SEST.ini`, `ammunition_overwrite/yf23_aim424_internal_SEST.ini` | RSG proprietary licence (LICENSE.txt in 3796349767 and 3804868806): compatibility patches may add content beside the mod 'provided they do not copy, replace, override, or redistribute Original Project Material'; anything else needs 'prior written authorization from RSG or AlpineStatic'. | 2 by collection-fixes | needs permission | 28-rsg-maintainer-alpinestatic.txt |
| 29 | SKIBIDI_RIZZLER123 | BUK-M3 (3564792549): 2 | 0 / 2 / 0 | `land_units/wp_buk-m3.ini`, `land_units/wp_bukslave.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by collection-fixes | needs permission | 29-skibidi-rizzler123.txt |
| 30 | Zero Two | F-16C Fighting Falcon (modern) (3758320372): 2 | 0 / 2 / 0 | `aircraft/usaf_f-16cm-bl52d.ini`, `ammunition/usn_agm-88.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by f-16cm-jatm; 1 by collection-fixes | needs permission | 30-zero-two.txt |
| 31 | 东武藏境 | XIAN JH-7A (歼轰-7A 飞豹) (3526982088): 2 | 0 / 2 / 0 | `aircraft/plaaf_jh7a.ini`, `aircraft/plaaf_jh7a_squadrons.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 2 by collection-fixes | needs permission | 31-author-of-3526982088.txt |
| 32 | 2154545636 | J-20 (歼-20 威龙) (3591563716): 1 | 0 / 1 / 0 | `aircraft/plaaf_j-20a.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by collection-fixes | needs permission | 32-2154545636.txt |
| 33 | Author of David's Sling (name not recorded) | David's Sling (3558173926): 1 | 0 / 1 / 0 | `ammunition/idf_stunner.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by intercept-model | needs permission | 33-david-s-sling.txt |
| 34 | Author of EUROMOD-Armada de Chile (name not recorded) | EUROMOD-Armada de Chile (3776730617): 1 | 0 / 1 / 0 | `vessels/ch_ffg_jvh_variants.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by world-sandbox | needs permission | 34-euromod-armada-de-chile.txt |
| 35 | Author of Kirov-class (Pyotr Velikiy Upgrade) (name not recorded) | Kirov-class (Pyotr Velikiy Upgrade) (3406985435): 1 | 0 / 1 / 0 | `vessels/wp_rkr_kirov_improved.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by replenishment; fidelity-checked upstream | needs permission | 35-kirov-class-pyotr-velikiy-upgrade.txt |
| 36 | Author of Operation STEADFAST LANTERN (name not recorded) | Operation STEADFAST LANTERN (3779799226): 1 | 0 / 1 / 0 | `ui/Default/Settings_UI_General.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by collection-fixes | needs permission | 36-operation-steadfast-lantern.txt |
| 37 | LLinqs | Charles De Gaulle & Modern French Navy Pack (WIP) (3567256221): 1 | 0 / 1 / 0 | `ammunition/fr__mdcn_sub.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by replenishment; fidelity-checked upstream | needs permission | 37-llinqs.txt |
| 38 | Meltemi | PLAN Type 071 Amphibious Transport Dock (3774572038): 1 | 0 / 1 / 0 | `vessels/plan_lpd_type_071.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by replenishment; fidelity-checked upstream | needs permission | 38-meltemi.txt |
| 39 | Pog Frog | [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles (3403661005): 1 | 0 / 1 / 0 | `aircraft/S-70B-2_Seahawk.ini` | mods-source/3403661005/_info.ini, line 20: 'please feel free to iterate on this mod all I ask is that you credit those who worked on this before you'. Lines 7-8: the model is used with Jason Simpson's permission, which does not extend to his other models (MNO ships no model). | 1 by allied-fixes | licence already allows | - |
| 40 | Stroh Vogel | B-2 Spirit (3480965706): 1 | 0 / 1 / 0 | `ammunition/b-2_jsow_ecm.ini` | Credits.txt covers the third-party B-2 model (Rhine_Lab_Muelsyse, CC BY 4.0), not the mod's .ini files. | 1 by collection-fixes | needs permission | 39-stroh-vogel.txt |
| 41 | Username | Nimitz Expanded (3432592449): 1 | 0 / 1 / 0 | `vessels/usn_cvn_nimitz_variants.ini` | None found: no LICENSE, readme or permission text in the export (mods-source/<id>/), so all rights are reserved by default | 1 by collection-fixes | needs permission | 40-username.txt |
| 42 | R.A.T.S. (Lukas Struckl, 'Ratte') | Sea Power Topographic Map (3826122523), R.A.T.S. Rigging (3843688859): 0 files | 0 / 0 / 0 (load-time adapter) | `beta-support/SEST-Beta-Features.zip` (payload/AnchorChain.dll, Topography-MIT-LICENSE.txt) | R.A.T.S. Source License 1.0 (mods-source/3826122523/LICENSE.txt) for versions released on or after 2026-11-18; Topographic Map 1.8.1 is dated 2026-11-22 (its CHANGELOG.md). The MIT notice SEST ships (integration/beta-feature-parity/third-party/SeaPowerTopo-LICENSE.txt, copied into the feature archive as Topography-MIT-LICENSE.txt) covers only the versions before 2026-11-18. | section 3.3 | needs permission | 41-rats-topographic-map.txt |

Totals: 10 verbatim, 552 close, 2 override. Channels are in `TRACKER.csv`. Groups whose author name is not recorded in the repo are marked; the owner should confirm the name on the item page before sending.

## 3. The named material

### 3.1 Greene RAAF F-35A (3514484654, removed from the Workshop)

MNO carries the aircraft itself (`integration/raaf-f-35a-jatm/README.md`). 16 files:

| Class | Files |
|---|---|
| Verbatim, binary (from `integration/raaf-f-35a-jatm/recovered/`, SHA-256 in its `SHA256SUMS`) | `assets/models/vehicle/aircraft/f-35/f-35a.obj`, `.../textures/f-35a_tex.png`, `f-35a_nm.png`, `f-35a_spec.png`, `assets/textures/f-35/raaf_f-35a.png` |
| Verbatim, text (= `mods-source/_retired/3514484654`) | `aircraft/raaf_f-35a_squadrons.ini`, `ammunition/raaf_f-35_gun_pod.ini`, `ammunition/usaf_aim-120c7.ini`, `animations/animations_raaf_f-35a.ini`, `assets/models/vehicle/aircraft/f-35/f-35a_mat.ini` |
| Close | `aircraft/raaf_f-35a.ini` (91 %; AIM-260/AIM-424 loadouts), `ammunition/usaf_gbu-31_v1.ini`, `usaf_gbu-53.ini`, `usaf_jsm.ini`, `usaf_jsm_land.ini` (model references moved), `language_en/ammunition_names.ini` (3 of Greene's names in SEST's merged file) |

Licence: none found. CREDITS.txt already names Greene as the source of the model and textures. This is the only place where MNO ships another author's model, so LICENSE.md section 3 ('does not redistribute third-party 3D models') and the CREDITS.txt opening line need this exception until Greene answers.

### 3.2 RSG AIM-424 overrides (2 files)

`ammunition_overwrite/fury_aim424_SEST.ini` (`#!extend ammunition/fury_aim424.ini`, Anduril FQ-44 Fury 3804868806) and `ammunition_overwrite/yf23_aim424_internal_SEST.ini` (`#!extend ammunition/yf23_aim424_internal.ini`, YF-23 Black Widow II 3796349767), both from SEST Collection Fixes. They set SEST's AIM-424 guidance and model block (`integration/common/aim424.py`). 22 of their 77 lines coincide with RSG's file, all generic values such as camera distances, `GuidanceType=3` and the collider. No RSG text is copied. RSG's LICENSE.txt (in both items): patches may add content 'provided they do not copy, replace, override, or redistribute Original Project Material'. So these need written permission. The catalogue records the owner's 23 Oct 2026 call: the Fury override 'stays, and comes out if RSG asks'. No other shipped file overrides an RSG file. The cost files name RSG units in price lists, which is a reference only.

### 3.3 Topographic Map 1.8.1 adapter

- What ships: `beta-support/SEST-Beta-Features.zip` contains `payload/AnchorChain.dll` (SEST's Anchor Chain fork, MIT), `Topography-MIT-LICENSE.txt` (a copy of `integration/beta-feature-parity/third-party/SeaPowerTopo-LICENSE.txt`, MIT, Lukas Struckl) and `SOURCE-CHANGES.patch` (SEST source, including the adapter). **No Topographic Map or Rigging file is in the item.** The DLL comes from the author's Workshop item.
- What the adapter does (`integration/beta-anchorchain/source/AssemblyAdapters.Topography.cs`): it accepts only `SeaPowerTopo.dll` with SHA-256 `4c3c0868f3cd420d…475c` (1.8.1). It checks the shape of `HeightReader..ctor` and of `Raster.SimHeight`, and changes one constant in `SimHeight`, the shallow-water threshold, from -48 to -50 m. It also checks the game's native terrain scaling. It is not purely in memory: `AssemblyPolicy.Prepare`/`WritePrivateImage` write the adapted DLL to `BepInEx\config\SEST-BetaAnchorChain\beta-api-r16-261123\<sha>\<workshop folder>\SeaPowerTopo.dll` on the player's PC and load it from there. The Workshop file stays unchanged.
- Licence: 1.8.1 is dated 2026-11-22 (`mods-source/3826122523/CHANGELOG.md`). It therefore falls under the R.A.T.S. Source License 1.0, which forbids sharing 'the Work or a build of it, changed or unchanged' and using any part of it in another mod without written permission. A modified copy made on the player's own PC is arguably not distribution by SEST, but it is a changed build of the Work. The MIT notice MNO ships covers only the versions before 2026-11-18. HANDOFF.md and LICENSE.md treat Topography as MIT, which is out of date for 1.8.1.
- Keel: the owner is in talks with the R.A.T.S. team (kanalratte) about moving onto R.A.T.S. Keel. The draft is worded to sit beside that conversation, and no Keel request is drafted.

### 3.4 Owner-supplied photos (21)

See `PHOTOS-SOURCE-SEARCH.md`. The rights holder of each photo is unknown, so this is a source search for the owner first and a permission request only where the source turns out to be copyrighted.

### 3.5 Bungalow: Dynamic Campaign Mod (3813157776), draft 42

MNO depends on this item more than on any other. It ships none of DCM's files, but:
- **GCO** (Global Command Operations) is SEST content written in DCM's campaign format.
- **The 261123 bridge** (`AssemblyAdapters.Campaign261123.cs`) applies to DCM 1.0.2 (18a2416e) only. It covers six removed or re-signed game members, with 11 rule kinds across 36 sites. The loader writes an adapted copy of `DynamicCampaignMod.dll` to the player's cache and loads it. Known costs: contact fading and the scene-editor timer are off.
- **Runtime add-ons** use Harmony to hook DCM types in 7 files (`LocalWeatherView`, `WorldStorms`, `WorldStormsMap`, `CampaignIce`, `WorldOpeningBriefing`, `WorldOperations`, `WorldShipyard`).
- **Portrait offer:** a modern officer portrait set (real, licensed photos) for DCM's manifest, with era tags. The owner wants the system unchanged.

### 3.6 Author DLLs adapted by SEST's loader (no files shipped)

For each of these, the loader checks the exact DLL by SHA-256. On 261123 it writes an adapted copy to the player's cache (`BepInEx\config\SEST-BetaAnchorChain\...`) and loads that copy. The Workshop file is never changed.

| Draft | Item | DLL (hash) | What the adapter changes |
|---|---|---|---|
| 02 | Euromod - Anchorchain Expansion Pack 3784474738 | MissileControlMod 0.1.18.1 (de8ba98e), TestRange (f1639294), OptimalTargetDist (61068dd0) | Fits steering and launcher code to 0.9.x (`CapturedStartup.cs`) |
| 02 | same | EnhancedDecoyMod 0.5.4 (7cd4f160) | Chaff-band round; flare requests passed to the game; air-decoy lifetime extension and per-search ignore off |
| 02 | same | MultiStageMissiles 1.7.18 (33a8841b) | Two chaff-submunition calls fit the 261123 signatures |
| 43 | Better Tac Map 3768036424 (toemel) | BetterTacMap 0.2.0 (bdc41864) | Launch-range default, ECS World type, drawing-save targets |
| 44 | J-36 Tailless Fighter 3801549552 | J36AfterburnerNozzle (0d4e89cc) | Reads through a SEST bridge for a property and a moved drag field |
| 45 | Chinese UAV Collection 3836566168 | Jiutian Reference Units 1.4.7 (230f38f6) | Widens one reflection lookup to the new signature |
| 46 | V-22 Osprey / SV-22 3806466625 | OspreyMechanics 1.1.46 (7761f0a9) | Hover fuel burn through a SEST bridge |
| 47 | PLA Z-21 3774746803 | Z21GunMoveFire (6de88b8b) | Container-field lookup through WeaponParameters |

Echidna, Ghost Shark and Keel are only started (BepInEx) or held. No image of theirs is rewritten, so no request is drafted. The Topographic Map adapter is 3.3, draft 41.

**CREDITS.txt correction needed:** it says DCM is adapted "in memory". The loader actually writes a cached adapted DLL (`AssemblyPolicy.cs` `WritePrivateImage`). The same is true for every DLL in this section.

## 4. No permission needed

### 4.1 Items only referenced by name (20 Workshop items)

SEST-original files that name these items' units, or patch them with a few keys of SEST's own (`#!extend` overrides, cross-deck `AircraftSupported` lists, nation fixes, model-block stubs). None of the author's content is copied, so no permission is needed. Referring to a unit by its id is how every mod interoperates. RSG's two files are the exception (section 3.2), because RSG's licence names overriding.

| Workshop item | Author (catalogue) | SEST files naming it | Reason |
|---|---|---|---|
| [DEPRECATED] E-7A Wedgetail (3499239964) | Pog Frog | 1 in raaf-wedgetail | SEST-written patch, under 50 % of lines shared, or a reference only |
| Air Deck Operations Upgrade - Nimitz (2000s) (3461091581) | sgtobliterator | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| Italian Navy Mod (3505420313) | zzocalu | 15 in cross-deck | SEST-written patch, under 50 % of lines shared, or a reference only |
| JMSDF Hyūga Class — Hyūga & Ise (3802216383) | not recorded | 2 in cross-deck | SEST-written patch, under 50 % of lines shared, or a reference only |
| Ka-27RLD (3776340577) | Filip7370 | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| MIG-29 Family (3417446309) | not recorded | 5 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| MiG-31 Foxhound (3799742828) | not recorded | 2 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| MiG-35 Fulcrum-F (米格-35 支点-F) (3659742367) | 2154545636 | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| MORE SU-24M VARIANTS (3716049886) | SKIBIDI_RIZZLER123 | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| PLAAF Aircraft Pack (3812111085) | not recorded | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| PLAN Type 001 Aircraft Carrier Liaoning (3774859959) | Meltemi | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| Small and Medium-Sized UAV Series [WIP] (中小型无人机系列) (3601891050) | FallschimJager705 | 2 in collection-fixes, 1 in allied-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| Soviet AEW&C + Transport Aircraft (A-50 / Il-76) (3524112296) | Zero Two | 3 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| Su-25 Frogfoot (3451166840) | misaka | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| Su-30SM2 (3762023575) | SKIBIDI_RIZZLER123 | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| SU-57 Felon (重刑犯) (3503594612) | 2154545636 | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| Sukhoi Flanker Family (苏霍伊侧卫家族) (3434072450) | MyGo!!!!!鼓手椎名立希 | 5 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| THE REDFOR MOD (3732654992) | SKIBIDI_RIZZLER123 | 6 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |
| The Royal Navy (3491248180) | Royal Navy/Falklands mod team | 12 in cross-deck | SEST-written patch, under 50 % of lines shared, or a reference only |
| Tu-214R Family (图-214R家族) (3780118683) | 鸣山 | 1 in collection-fixes | SEST-written patch, under 50 % of lines shared, or a reference only |

Groups in section 2 also have SEST-original reference files (for example 131 cross-deck lists naming 24 items). Those files need nothing either.

### 4.2 The game's own files (58)

Files derived from Sea Power's own data, not a mod's: 39 replenishment hulls whose upstream `check_pack_fidelity.py` resolves to `_vanilla/original` (clones and vanilla forks), and 19 others that match the game's file more closely than any mod's copy (`ammunition/damage.ini`, `systems/weapons.ini`, `ui/minimap.ini`, several gun rounds). They are not a mod author's, so they are outside this request. LICENSE.md section 5 covers the game.

### 4.3 Pog Frog: licence already allows

`aircraft/S-70B-2_Seahawk.ini` (99 % of S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles, 3403661005). Its `_info.ini` says: 'please feel free to iterate on this mod all I ask is that you credit those who worked on this before you'. CREDITS.txt credits it. The model is Jason Simpson's and MNO does not ship it. No request is needed. A courtesy note is optional.

## 5. Uncertain or open

- Author names not recorded in the repo for 13 groups (marked 'name not recorded'). Two merges rest on evidence that is not conclusive. The Luzon Line and The Siam Shield are merged because the catalogue says 'by the author of the Luzon Line'. The two Euromod Korea add-ons are merged because their descriptions are identical. Mitchell600's group includes the Modern RAN mod, which has two co-authors.
- The 50 % threshold for 'close' is a judgment. The 26 close files that CREDITS.txt does not list at 90 % or more (mostly squadron files, loadout additions and `systems/` merges) are counted as the author's. Files below 50 % are counted as SEST's. The per-file share is in `FILE-LIST.csv`.
- Binary files of other authors can be detected only for Greene, because the export has no binaries. The file types and the build scripts show no other carried binaries, but that is not a byte-level proof.
- `language_*` files are SEST's merged name files, and a few of their lines are authors' unit names. Two are counted (`language_en/ammunition_names.ini` under Greene, `language_cn/loadout_names.ini` under misaka). The others fall under 50 %.
- Not in the decision's list, so not drafted: SEST's other load-time adapters for author DLLs (Enhanced Decoy, Multi-Stage Missiles, J-36, Osprey, Z-21, Better Tac Map, Jiutian, Dynamic Campaign Mod; see `integration/beta-anchorchain/source/AssemblyAdapters.*.cs`) and the Pop-Out Windows and Rigging hash pins. The owner already decided to ship and credit the DCM adapter. The others may deserve the same question as Topographic Map.
- HANDOFF.md says the licence is GPT's personal-play notice (`gpt/WORKSHOP-DRAFT.md`), while LICENSE.md says MIT plus CC BY-NC-ND. The drafts claim neither; they say only 'free, non-commercial'.
