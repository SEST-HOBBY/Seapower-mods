<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. -->

# World register: integration sections (corrected regional packages merged)

**Inputs.** This is checked against the eleven final regional sections, `01-us-pacific.md` to `11-south-atlantic-france.md` in this folder (Australia/IO passed its second check unchanged). Their structured form is `packages.json`, and the review trail is `review-log.json`.
- Together they hold 70 packages: one for each of the 69 register nodes in `source-register.json`, plus the world-level US sealift reserve (`reserve:us_sealift`, not a register node).
- Every package's populate_policy matches the register.
- The four nodes that were register-derived in the previous version (Naha, Mount Pleasant, Mare Harbour, Île Longue) and the end of the Atsugi package now come from real packages. No register-derived placeholder remains.
- The second-skeptic results for all eleven regions are now applied in the final packages (see each file's `applied` list) and are reflected here wherever they touch identity, allocation, connections, gaps or counts. Indian Ocean/Australia had none open. Section 5.4 lists the region items still open after the final pass.

**Unit ids.** Every unit id was re-resolved on branch sest-dev/sweet-lovelace-3kxsve (HEAD 1647837f, 2026-10-07; no unit, variant or ammunition file has changed since c9d8bf51) with `find_unit_file` / `winning_file` from `integration/missions/refine_civ_traffic.py`. This covers the 148 distinct ids in the final force rows and 72 more ids named in these sections: 46 vessel, aircraft and land-unit ids (including four Burke files written in shorthand: `_081_late`, `_085_late`, `_097_late`, `_100_late`) and 26 ammunition ids, 220 in all. Variant names come from the language_en stack and ServiceDates from the winning variants files. Two ids do not resolve, and neither is used:
- `ita_ddg_durand_de_la_penne` was refuted; `mm_ddgh_durand_de_la_penne_02` and `mm_ffg_maestrale` resolve but are not proposed.
- `usn_mh-60r_26` is unresolved.

**Labels.**
- SOURCE CLAIM: R01–R03 with line number.
- CHECK: a known doubt.
- SCENARIO CHOICE: our proposal. Integration resolutions here are SCENARIO CHOICES unless marked otherwise.
- Repetition across reports is not corroboration.
- Outcomes are only exact, proxy, missing_fit or none.

**Numbering.** C1–C23 keep their numbers from the previous version, with their current status. C24–C31 are new. C32–C33 were added at the final consistency check.

---

## 1. World identity check

### 1.1 Rules applied world-wide
- **Identity key.**
  - Ships are keyed by hull number (DDG-nn, T-AKE n, and so on), never by unit plus variant. Several unit files carry the same hulls:
    - `usn_ddg_burke_f2a_099_late` and its `#!alias` `usn_ddg_arleigh_flt2A_099_2027` both name DDG-99 and DDG-101 to 107;
    - DDG-117 is on both `usn_ddg_burke_f2a_117` V1 and `usn_ddg_burke_f2a_113` V5;
    - the PLAN pins recur in RSA and older files (see C23).
  - Aircraft are keyed by world asset id plus airframe count. A squadron livery may repeat across airframes of one squadron. One squadron may not sit in two air wings, and may not appear on two aircraft types (see C6).
- **Pin variants now, not "at build".**
  - Surplus demand on a named-hull pool uses the unnamed `Default` variant, with a unique, asset-specific NameOverride.
  - The only pools left to build-time choice are those that one package alone draws on: the La Fayette (Djibouti), the Thaon di Revel PPA (Djibouti), the FREMM (Brest approaches) and the Wasp LHD (any variant except V6).
- **Labels.**
  - Land-unit renaming is proven: `TaskforceNLandUnitMNameOverride=` inside `[Language_en]`, for example stock `Showdown off Guam Blue 1985.ini:19` "Andersen AFB". There are about 2,700 such keys in the repo.
  - A visible stand-in label is needed only where a proxy or missing_fit unit would otherwise display a real installation or hull name. Generic stock names need none:
    - PLA stores scenery: "Warehouses 1" / "Fueltanks Medium Depot";
    - a Default `civ_ms_sealift_pacific`: "Medium Tanker,Merchant".
  - SEST T-AKE and T-AO named variants show real hull names, and "(stand-in)" appears only on Default. Whether the class name is also visible is an editor CHECK. Until it passes, a pinned named variant carries a NameOverride such as "<hull name> (T-AKE stand-in)".
- **Embarked aircraft.**
  - Embarked aircraft are sub-assets of their ship (`<ship id>_flt` or `_helos`), count in totals, and **take the host ship's allocation**, for example "escort (embarked on tr_ddg_1; hand-off)" (C30).
  - The ship's shipped AirGroup is a SCENARIO CHOICE unless a mission CustomAirGroup replaces it.
- **Base air groups.**
  - Every placed base gets an explicit CustomAirGroup that lists only its allocated at-base aircraft. Shipped default groups would otherwise spawn unallocated duplicate identities (C8).
  - An AirGroup line holds squadron and count only. A ready at-base airframe gets its loadout from `FlightDeck_ReadyUpTaskN=<type>,<squadron>,<loadout>,<count>,0` on the base entry. Vanilla precedent: `Showdown off Guam Blue 1985.ini:523` `FlightDeck_ReadyUpTask2=usn_p-3c,Squadron14,Recon,1,0`; also `integration/missions/DARWIN US SUPPLY.ini:70-72`. Servicing and reserve airframes get no ready-up task, and runtime behaviour is untested.
  - Editor round-trips drop empty CustomAirGroup lines and flatten ROE, so the restore step is needed (`restore_roe.py`).
- **Aircraft labels.**
  - No repo or mods-source mission sets a display name on an aircraft entry (1,041 files, per the Japan/Norway second check). So a name override, even once proven, could label only separate airborne entries, never airframes inside a CustomAirGroup.
  - Labelled at-base stand-ins (the Japanese P-1s) therefore need a SEST squadron patch.
- **Airborne at t0.** An aircraft is either launched from its base group or placed airborne, never both.
- **Strategic forces.**
  - These are recorded as bare facts only, and 0 are placed anywhere (C17).
  - No storage, handling or employment detail is recorded.
  - Nuclear-effect loadouts are excluded by whitelist:
    - `wp_tu95ms`: LandAttack or Default only;
    - `wp_tu-160`: StrikeLongRangeKH101 or StrikeLongRange only, never StrikeNuclear, Default or Strike.
- **Support claims.**
  - Support is listed separately from forces, and is claimed only from unit-file or inventory evidence.
  - Ship fuel, repair and supplier restocking are not established.
  - Cross-nation replenishment is an untested option, never an allocation (C31).

### 1.2 Carriers (R03 table CVN 68–76, R03:52–62) and other capital ships

| Hull | World asset id | Unit / variant (re-resolved; ServiceDate) | Owning node | Initial allocation (SCENARIO CHOICE) | Source basis | Referenced elsewhere (not re-allocated) | Status / resolution |
|---|---|---|---|---|---|---|---|
| CVN-68 Nimitz | asset:usp:cvn68_nimitz | usn_cvn_nimitz_2025 V1 (2025–2027) | usp_kitsap_bremerton_psns | reserve, dormant, no wing | R03:48, R03:54 | NB San Diego (homeport-shift link) | Single. CHECK: reported inactivation and move to Norfolk around 2026. If that predates the scenario date, move it once to the Atlantic package. |
| CVN-69 Eisenhower | asset:usatl:cvn69_eisenhower | V2 (2025–2030) | usa_norfolk_naval_station_norfolk | training_test, Virginia Capes CQ | R03:48, R03:55 | – | Single. CHECK: reported in maintenance after 2023–24. Not promoted if CVN-75 enters RCOH. |
| CVN-70 Carl Vinson | asset:usp:cvn70_carl_vinson | V3 (2025 onward) | usp_sandiego_naval_base_san_diego (city-level home-port record) | training_test, SoCal operating area | R03:50, R03:56 | NAS North Island (CQ; berth) | Single. CHECK: berth (R03:27 vs R03:50/56–58); reported deployed in 2025. |
| CVN-71 Theodore Roosevelt | asset:usp:cvn71_theodore_roosevelt | V4 | usp_sandiego_naval_base_san_diego | transit, ~8N 66E | R03:50, R03:57 | me_bahrain_nsa_bahrain (arrival; optional RAS, C31); io_diego_garcia_nsf | Hand-off consistent. CHECK: the status appears to reflect 2024. |
| CVN-72 Abraham Lincoln | asset:usp:cvn72_abraham_lincoln | V5 | usp_sandiego_naval_base_san_diego | underway_deployed, ~17N 135E | R03:50, R03:58 | wpac_yokosuka, wpac_guam (visitor; any transfer debits their suppliers) | Single. Links cross ±180 (P3a). |
| CVN-73 George Washington | asset:wpac:cvn73_george_washington | V6 | wpac_yokosuka_naval_base | underway_deployed, Philippine Sea box ~30N 137E; never also at the pier | R03:38, R03:59 | US Pacific does not allocate it | Single. The alternate `usn_cvn_nimitz_2027s_adou` is dropped: its whitelist rejects 24 of the 31 proposed aircraft. CHECK: "currently" is undated. |
| CVN-74 John C. Stennis | asset:usatl:cvn74_stennis | V7 | usa_newport_news_shipbuilding | servicing_maintenance (ledger entry by default; optional inert hull) | R03:50 ("facilities like"), R03:60 | Norfolk (home port, R03:60) | Single. CHECK: RCOH location and completion. If complete, re-allocate once. |
| CVN-75 Harry S. Truman | asset:usatl:cvn75_truman | V8 (the winning variants file annotates it "Real World No CVW RCOH") | usa_norfolk_naval_station_norfolk | underway_deployed, southbound from ~33.5N 74W | R03:48, R03:61 | – | **Contingency applied in the US Atlantic package:** if in RCOH, it moves to servicing at Newport News, asset:usatl:cvn75_airwing is left unallocated, and the escorts and T-AKE keep their ids. No hull is duplicated. |
| CVN-76 Ronald Reagan | asset:usp:cvn76_ronald_reagan | usn_cvn_nimitz (legacy, 3373960386) V9; proxy, labelled "CVN-76, legacy-fit unit" | usp_kitsap_bremerton_psns | servicing_maintenance, static | R03:62; former Yokosuka role R03:38 | wpac_yokosuka (former role only) | Single. |
| CVN-77 to 79 | – | – | – | none | Not in the R03 table | – | Backlog: build the carrier pool from separately checked data. |
| Fujian CV-18 | asset:chn:scs_cv_1 | plan_cv_type_003 V1 "PLANS Fujian CV18" | chn_hainan_longpo_naval_base | underway_deployed, northern SCS | SCENARIO CHOICE (R03:99 names no carrier) | Lingshui (air cover, authored) | Single. The same hull is in plan_cv_fujian and plan_cv_fujian_rsa, which must not be placed. Embarked wing count not set (C7). Liaoning and Shandong are not allocated. |
| US SSBN | asset:usp:kitsap_ssbn_context | usn_ssbn_ohio | usp_kitsap_naval_base_kitsap | abstract, 0 placed | R01:17, R03:21, R03:29 | – | Bare fact only. |
| PLAN SSBN | asset:chn:longpo_ssbn_force | plan_ssbn_type_094a (missing_fit) | chn_hainan_longpo_naval_base | abstract, 0 placed | R01:31, R03:99 ("primary harbor" is R03:99 only) | – | Bare fact only. |
| French SSBN | asset:eur:ile_longue_ssbn_force | fr_ssbn_triomphant (missing_fit: its only fit includes the strategic missile) | eur_brest_ile_longue | abstract, 0 placed | R03:150, R03:152 | – | Bare fact only (plan:43, seed:25). |
| Russian SSBN | asset:rus:barents_ssbn_1, asset:rus:okhotsk_ssbn_1 | wp_ssbn_borei Default (live strategic-weapon system; not detailed) | Russian regional naval context (sea-area record) | patrol at quantity 0 (an abstract sea-area marker until a weapons-hold test passes) | R03:66 (bastions) | Evenes (hunt context only) | C17 applied. Placement only after a passed weapons-hold test. |

### 1.3 Other single named assets

| Asset | Identity | Owner | Allocation | Status |
|---|---|---|---|---|
| HMS Forth (P222) | asset:satl:hms_forth; `rn_opv_river_batch2` V1 "(P222) HMS Forth" (2018 onward) | satl_falklands_mare_harbour | patrol, South Atlantic sovereignty and fishery patrol; not also at the pier | Single; no other region uses River B2. SOURCE R03:146. CHECK: "since 2020" is dated; R03:146 says one patrol ship, R01:59 and R02:71 say patrol ships. |
| RFA Tidesurge | asset:satl:rfa_tide_relief; `rn_aor_tide` V3 "A138 RFA Tidesurge", NameOverride "RFA Tidesurge (stand-in hull)" | satl_falklands_mare_harbour | reserve (dormant, optional) | Single; no other region allocates `rn_aor_tide`. |
| MV Strathcarrol | asset:satl:sealift_charter; `civ_ms_amra` V1 (Nation=UK), NameOverride "Authored charter (stand-in hull)" | satl_falklands_mare_harbour | transit (periodic) | Single. |
| RNoAF P-8A Vingtor, Viking, Ulabrand, Hugin, Munin | asset:mpn:p8a_vingtor / _viking / _ulabrand / _hugin / _munin; `usn_p8` Squadron5 "P-8A No.333 Squadron RNoAF" | hn_evenes_air_station | Vingtor patrol (separate airborne entry); Viking resident, ready; Ulabrand resident; Hugin servicing; Munin reserve (ready-up tasks applied in the final package: Viking usn_p8,Squadron5,ASW,1,0; Ulabrand usn_p8,Squadron5,AntiShip,1,0; Munin none) | Each once. SOURCE R03:115. CHECK: per-airframe names cannot be shown inside one squadron livery. |
| Rota destroyers | asset:med:rota_ddg84 (DDG-84 Bulkeley, _084_late V1), rota_ddg117 (DDG-117 Paul Ignatius, _117 V1), rota_ddg80 (DDG-80 Roosevelt, _080_late V1), rota_ddg79 (DDG-79 Oscar Austin, _079_late V1, 2024 onward); each with a `_helos` pair (usn_mh-60r Squadron19 "HSM-79") | med_rota_naval_station | underway_deployed / patrol / servicing_maintenance / reserve | Applied (C2, C3). The hulls come from mod name text, not R03 (R03:44 gives class and role only). DDG-51 is held, unallocated. |
| Collins boats | `ran_ssg_collins` V3 Waller, V2 Farncomb, V6 Rankin, V5 Sheean | aus_stirling_hmas_stirling | resident / servicing / patrol / reserve (not placed) | Single each. Proxy: S-80 Plus stand-in mesh. |
| Anzac / Arafura / Supply | `ran_ffh_anzac` V3 Warramunga and V7 Toowoomba, each with 1 MH-60R Sq20 "816 Squadron RAN"; `ran_opv_arafura` V2 Eyre (empty CustomAirGroup); `ran_aor_supply` V2 Stalwart | aus_stirling_hmas_stirling | as package | Single. |
| Fleet Base West marker | asset:ausio:stirling_port; `ran_pt_boats_docks` V2 "Fleet Base West (HMAS Stirling)" | aus_stirling_hmas_stirling | resident (missing_fit for port service) | Single. V1 and V2 are reserved to Australia (C12). |
| Naha P-3C | asset:mpn:naha_p3c_1–4; `usn_p-3c` Squadron25 "P-3C 5th FAS 'Pegasus'" | jpn_okinawa_naha | 1 patrol (airborne entry), 2 resident (ready-up tasks applied: naha_p3c_2 ASW, naha_p3c_3 AntiShip), 1 servicing | Exact. CHECK: date filter of the Japan squadrons (5.3); Naha platform (P-1 vs P-3C). |
| Brest FREMM | asset:eur:brest_fremm_asw, with asset:eur:brest_fremm_nh90 as its CustomAirGroup row (`fr_nh90=Squadron1,1`) | eur_brest_ile_longue (context node; Brest approaches at sea) | patrol | Single user of the pool: `fr_ffg_aquitaine_asw` V1–4 or `fr_ffg_aquitaine_modernized_asw` V1/2, pick at build. Never placed with the default group. |
| SEST named bases | `wp_airbase_1` Default "Olenya Airbase" (Variant1 carries an F-14A group; avoid); `wp_airbase_modern` V1 "Engels airforce base"; `airbase_raaf_tindal` V1 | Olenya / Engels / Tindal | installations | Single. Ukrainka and Belaya use `wp_airbase_modern` **Default** (labelled), never V1. |
| PLAN pinned hulls | see 1.5 | Yulin, Longpo, Ningbo, PLA Djibouti | as packages | China maritime pins applied; Djibouti pins to apply (C13). |

### 1.4 Conflicts found and resolutions

| # | Conflict | Status now | Resolution (SCENARIO CHOICE unless stated) |
|---|---|---|---|
| C1 | **Burke Flight IIA pool overdrawn.** DDG-99 and DDG-101 to 107 (8 hulls on `_099_late` and its `_2027` alias) were drawn 13 times. | **Partly applied.** US Pacific pins DDG-99 and DDG-101 to 104 (V1–V5), moved its CVN-71 escorts to DDG-108/109 (`_108_late` V1/V2) and pinned DDG-125 (f3_125 V1). No region uses `_2027` now. **Still open:** US Atlantic draws 4 unpinned `_099_late` hulls, W/C Pacific's gw_csg_ddg1 is "hull chosen at build" and Gulf's me:ddg_1 is "provisional". That is 6 demands for the 3 remaining hulls (V6–V8). US Pacific's line 320 and its San Diego package check now say that V6–V8 are reserved by this ledger and not yet applied in those regions (corrected in the final package). | Key on hull number. Apply the 1.5 ledger. V6–V8 go to wpac:gw_csg_ddg1, me:ddg_1 and usatl:ddg_truman_esc_1. The other three US Atlantic hulls move to `_081_late` V1, `_085_late` V1 and `_100_late` V1. CHECK the world-wide DDG-99/101–107 draw at merge. |
| C2 | DDG-117 exists on two unit files. | Applied. | Rota owns DDG-117 through `usn_ddg_burke_f2a_117` V1. `usn_ddg_burke_f2a_113` V5 (ServiceDate 2019–2022) is barred world-wide. |
| C3 | The Rota DDG-51 name text reads as a past tour. | Applied. | DDG-79 (`_079_late` V1) is the reserve hull, with the new id asset:med:rota_ddg79; asset:med:rota_ddg51 is retired. DDG-51 (`usn_ddg_burke_f1_051_late`) is held, unallocated anywhere. CHECK: Rota hull count at the scenario date. |
| C4 | **T-AKE overdrawn:** 6 demands for 4 named hulls. | Partly applied. V1 → usp:vinson_take_1 and V4 → med:take_1 are pinned. US Atlantic placed take_truman on Default "(stand-in)". wpac:gw_csg_take, wpac:guam_take and me:take_1 are still "dedupe at merge". | Revised ledger: V1 vinson_take_1, V3 (T-AKE 6) gw_csg_take, V4 med:take_1. **Default** for take_truman (accepted in place of the earlier V2 pin), guam_take and me:take_1, each with a unique NameOverride (C28). V2 is now free. Alternative for surplus: `usn_taoe_supply` V2/V3. |
| C5 | T-AO, T-AOE and Algol were unpinned. | Partly applied. T-AO V1 → sd_tao_1 is pinned. Algol V6 → med:relief_sealift_1 is pinned. US Atlantic placed taoe_norfolk on Default. | T-AO: V2 (T-AO 189) yoko_tao, V3 (T-AO 193) me:tao_1, V4 free. T-AOE: Default accepted, since it is the only T-AOE in the world. Algol: V1 takr_norfolk_relief, V3 sealift_algol1. Both those packages must drop V6 from their option lists. V7 Capella is free; V2/V4/V5/V8 end in 2025 and are barred. |
| C6 | Carrier-wing squadrons are unassigned in four wings; CVN-75's "F/A-18E Sq1–17" can collide with GW's Sq1/Sq8. | Partly applied. GW pins F/A-18E Sq1 (VFA-27) and Sq8 (VFA-195), F/A-18F Sq4 (VFA-102), EA-18G Sq16 (VAQ-141), E-2D Sq9 (VAW-125) and MH-60R Sq17 (HSM-77). The Norfolk CQ det pins F/A-18F Sq6 (VFA-106). Open: Vinson, Roosevelt, Lincoln, Truman, the Norfolk ashore E-2D pair and every HSM pick. | Squadron ledger from the remaining pools, re-counted here: usn_fa_18e_rsa Sq2–7 and Sq9–17 (Sq18 is VX-4: avoid); usn_fa_18f_rsa 9 left; usn_ea-18g_2020 19 sections but 16 squadrons (pairs 9/10, 12/13, 14/15 repeat VAQ-137/139/140); usn_e-2d 8 left (liveries offset from names); usn_f-35c 13 sections (avoid Sq1, which has a name/livery mismatch; Sq3/13, 5/6 and 9/12 repeat a squadron). **New rule:** VFA-86, VFA-97 and VFA-115 exist as both F/A-18E (Sq13, Sq12, Sq5) and F-35C (Sq8, Sq7, Sq10); use each on one type only. |
| C7 | **Embarked helicopters uncounted.** | Partly applied. US Pacific (16 MH-60R in 8 `_flt` sub-assets), Rota (8), Gulf (3), RAN (2, with Eyre empty), PLAN Djibouti (2), French and Italian (1 each) and Brest NH90 (1) are counted. **Not yet carried as sub-assets** (shipped AirGroups re-read here): US Atlantic 8 MH-60R on four Flight IIA hulls (mentioned in its summary only); W/C Pacific 9 (CG 2, gw_csg_ddg1 2, gw_csg_ddg2 2 (DDG-89 V1 CustomAirGroup MH-60R Sq9), yoko_ddg_patrol 2, guam_lcs1 1; the Flight I hull has none); China maritime 9 (Z-9F on 054A p5, 054A p3, 054 p2, 052D p1; Z-20F ×2 on the 055 and ×1 each on 052D p3 and p4; Ka-28 on the 956E; the 056A has none); Russian context 3 (Ka-27PL ×2 on the Udaloy, Ka-27 on the 20380); Fujian's wing (unit default; count not set). | Apply the `_flt` rule (1.1) in those four regions. Fujian gets an explicit, small CustomAirGroup before placement and is uncounted until then. |
| C8 | Shipped base groups duplicate world identities: Tindal B-52H/B-2/KC-135; airfield_small_1 V5 P-3C Sq23 ×4; nato_small_airbase (54 Cold War aircraft); usa_airbase (57/96); china_large_airbase V2 (unresolved plaaf_j5 Sq5); wp_airbase_1 V1 F-14A; is_airbase_akureyri V2 (US group). | Applied as design in every package; untested. | A mandatory CustomAirGroup holding at-base allocated aircraft only (1.1), with ready-up tasks for ready airframes. Tindal excludes every shipped bomber and tanker. Restore after every editor round-trip. |
| C9 | Olenya patrol aircraft could be double-listed; Belaya's tanker had no id. | Applied. | The Olenya group holds the at-base rows only. The patrol Tu-95MS and Tu-142M are airborne at t0. asset:rus:belaya_il78_opt is separate (0 by default). |
| C10 | The Evenes USN P-8A is "counted against Jacksonville". | **Open.** Japan/Norway carries asset:mpn:evenes_usn_p8a_det (underway_deployed). US Atlantic still lists asset:usatl:p8a_jax_reserve (reserve, 1), so world USN P-8A reads 12, not 11. | asset:usatl:p8a_jax_reserve is retired. asset:mpn:evenes_usn_p8a_det is the 4th Jacksonville airframe: owning node usa_jacksonville_nas_jacksonville, allocation underway_deployed at Evenes, placed as a visitor entry in the Evenes package. Jacksonville then reads 1 patrol, 2 at base and 1 deployed. |
| C11 | **Named RRF/MSC merchant variants could be used twice.** | Partly applied. Seabee V1 "SS Cape May" → sd_relief_cargo_1 and Sealift V4 "MV Sealift Indian Ocean T-AOT-171" → dg_resupply_tanker are pinned. The JLSF hulls use Default with unique labels E-1, E-2, S-1, S-2. The DG/APF hulls use Default but share two labels (C28). wpac:guam_taot_arrival is an unpinned "US 'Sealift' variant". The San Diego traffic tanker is now pinned to V2 "MV Sealift Arabian Sea T-AOT-169" and labelled (US Pacific final). | `civ_ms_sealift_pacific`: V1 "MV Sealift Pacific Ocean T-AOT-168" → Guam T-AOT; **V2 "MV Sealift Arabian Sea T-AOT-169" → the San Diego traffic tanker** (second check; V2 is within NumberOfVariants=37); V4 → DG; V3 free. Each pinned Sealift hull displays a named MSC tanker and carries a live 40,000-point block with a 2,000 ceiling, so each is labelled. Only a Default hull displays "Medium Tanker,Merchant". Seabee V2–3, roro_a V6–10 (Cape D-class) and C8 V23–26 (Cape F-class) stay unused, reserved for a future US sealift allocation. |
| C12 | `ran_pt_boats_docks` V2 is "Fleet Base West (HMAS Stirling)". | Applied (gulf-horn). | NSA Bahrain, Jebel Ali, Héron and the PLA base pin Default with a mandatory NameOverride. V1/V2 are reserved to Australia. If the Med option option:med:rota_berth_marker (quantity 0) is ever placed, it follows the same rule. The Mare Harbour alternative `ran_pt_boats_docks_small` displays RAN names, so it would need a NameOverride too. |
| C13 | PLAN pools used twice. | Applied in China maritime (every hull pinned); Djibouti picks are still provisional in Gulf/Horn. China maritime pinned 052D p3 **V1 "Zibo (156)"** for Longpo, which conflicts with the earlier ledger's V4. | Ledger updated to keep the region pin: 052D p3 Longpo V1 "Zibo (156)", Djibouti **V10 "Zhanjiang (165)"**, never V9 "Guilin (164)"; V4 "Nanning (162)" is now free. 054A p5 Djibouti V2 "Honghe (523)". 903A Djibouti V3 "963 CNS Honghu"; V4 free. 901 V2 free. |
| C14 | JLSF relief escorts had no named asset. | Applied in the China maritime and China support final packages (see C24). | Kept as stated: asset:chn:ningbo_ffg_1 escorts asset:chn-jlsf:wuxi-mob-roro-1 from t0, and asset:chn:yulin_corvette_2 escorts asset:chn-jlsf:guilin-mob-cargo-1 from t0. Each moves from resident_at_base to escort. Escorts for a reserve release are other at-base hulls, removed from the base count when they sail. |
| C15 | One Australian airliner was used over Perth and the Top End. | Applied. | civ_a330 Sq61 (the only Australia A330 squadron) is near Perth only. The IO lane has one civ_a330 and one civ_a380. Tindal has no airliner. |
| C16 | Muharraq "4 airliners" had no composition. | Applied. | asset:me:civair_obbi_1–4: civ_a320 Sq27 Gulf Air, civ_a330 Sq40 Gulf Air, civ_a380 Sq5 Emirates, civ_a320 Sq7 Qatar. |
| C17 | Strategic forces were treated inconsistently. | Applied. | 0 placed world-wide. The Borei rows are "0 until a weapons-hold test passes", and the bastions are abstract sea-area markers until then. Triomphant and 094A are missing_fit and not placed; Ohio is context only. |
| C18 | Dated carrier contingencies (CVN-68, 74, 75). | Applied (CVN-75 contingency pre-stated; move-once rules stated for CVN-68 and 74). | Each hull moves once; no hull appears in two packages. |
| C19 | The Algol relief ship was parented to the abstract DLA Sigonella node. | Applied. | asset:med:relief_sealift_1 sits in `reserve:us_sealift` (world-level, not a register node), with authored links to DLA Sigonella, Rota and Souda. |
| C20 | Typhoon / Voyager / A400M at Akrotiri and Mount Pleasant. | No conflict; both packages now exist. | Separate airframes: Akrotiri 2/1/1, Mount Pleasant 4/1/1. |
| C21 | JMSDF P-3C squadron liveries. | Partly applied. Naha is pinned to Sq25 (exact). The Kanoya and Atsugi stand-ins wait for SEST labelled squadrons (numbers assigned when the patch is built). The Djibouti jp_p3c_1/2 still read "Squadron21–29". | Pin the Djibouti detachment to a squadron not used at Kanoya (21), Atsugi (23) or Naha (25). Proposed: Squadron22 "P-3C 2nd FAS 'Poseidon'"; 24 or 26–29 are equally valid. Replace the airfield_small_1 V5 group. The same date CHECK applies. |
| C22 | LCS and CG unpinned. | Open (W/C Pacific, Gulf). | Pins in 1.5. |
| C23 | Ship names that equal node names. | Applied in China maritime, with the list extended. | Do not place: 055 V4 "Wuxi (104)"; 052D p3 V9 "Guilin (164)"; 052D p1 V5 "Xining (117)"; "Wuhan (169)"; "Shenyang (115)"; "Zhengzhou (151)"; 956E (early and late) V4 "Ningbo DDG-139"; plan_em_sovremenny V4 "Ningbo 956EM"; 054A p2 V1 "Yulin (569)" and V11 "Sanya (574)"; RSA 054A "Yulin FFG-569" / "Sanya FFG-574"; plan_ffg_krivak2 V5 "Yulin FFG-569"; "Wuxi FF-512"; Luda-family "Guilin DDG-164". **Duplicate-file guard:** pinned PLAN hulls must not be placed from their duplicate files. This now includes **Dazhou (135), which RSA spells `plan_ddg_type_052D_rsa` V28 "Dazhou DDG-157"** (pennant differs between mods; the guard is now in China maritime, in the markdown bullet 'A pin binds the physical ship' and the ningbo_ddg_2 notes). |
| C24 | **China relief escorts: the two second checks disagree.** The China support fix gave the t0 escort slots new ids (asset:chn:ningbo_relief_escort_1, asset:chn:yulin_relief_escort_1) and made ningbo_ffg_1 and yulin_corvette_2 the *release* escorts. That double-books both hulls against C14. The China maritime check proposed declaring C14 superseded and running the relief transits unescorted. Neither register holds the new ids, and China maritime then listed both hulls as resident_at_base. | Applied in both final packages. China maritime: both hulls are escorts from t0, out of their base counts, with the release-escort rule. China support follows C14. One stale phrase remains: China support still says the hand-over is "not yet in china-maritime" (5.4). | **C14 stands.** The two proposed ids are withdrawn, because they exist in no register and invented ids are not allowed. The China maritime "C14 superseded" line is declined. China support follows C14 (the escort bullets, the region line, the packages, named_assets, and its two "Escort reciprocity" checks), and states that the Ningbo and Yulin packages *must* record the hand-over, not that they already do. China maritime changes ningbo_ffg_1 and yulin_corvette_2 to escort from t0, removes them from the base counts, and states the release-escort rule. One allocation at a time. |
| C25 | Atsugi says a Djibouti JMSDF MPA detachment must be "taken from this allocation". Gulf/Horn allocates two exact P-3Cs with their own ids. | Open (wording). | Separate allocations. asset:hoa:jp_p3c_1/2 are owned by hoa_djibouti_jp_base and are not drawn from Atsugi's four P-1 stand-ins, which are a different type and label. The Atsugi–Djibouti link becomes context only. |
| C26 | Atsugi's link to Yokosuka names "JMSDF escorts and the Mashuu AOE in that package". | Open (wording). | No JMSDF ship is allocated anywhere: the Yokosuka package holds US assets only, and `jmsdf_aoe_mashuu` (proxy) is not proposed. The link stays a geographic-neighbour row and the asset reference is dropped. |
| C27 | Tokyo Bay civil traffic is described twice: asset:mpn:atsugi_civ_pool is "merged with the Yokosuka Tokyo Bay pool", while the Yokosuka package proposes its own unquantified Tokyo Bay traffic. | Open (wording). | One pool, asset:mpn:atsugi_civ_pool, owned by the jpn_atsugi_naf package as written. The Yokosuka routine-activity line references it and places nothing of its own. |
| C28 | Default stand-in labels are not unique. asset:ausio:dg_mps_1 and dg_mps_2 share "Maritime Prepositioning ship (stand-in)"; apf_loiter_1 and apf_reserve_1 share "Afloat prepositioning ship (stand-in)". Three Default T-AKEs (C4) need labels. | Open. | Add an asset-specific suffix, for example "Maritime Prepositioning ship 1 (stand-in)". Each Default T-AKE gets its own NameOverride naming its group. |
| C29 | **Neutral-traffic merchants are named ships.** For example, `civ_ms_ritina` V1 is "MV Gatto Sicilia", `civ_ms_bulk` V1 "MV Universe Kure" and `civ_ms_car_carrier_a` V1 "MV Don Carlos". Pools: ritina 121, bulk 92, car carrier 54, mairangi_bay 48, encounter 7, act_1 11 variants. Regions draw on overlapping nation pools: Japan car carriers at San Diego and Atsugi; Liberia or Japan VLCCs at San Diego, the Gulf and the Horn; Liberia or Greece bulk carriers at Norfolk, San Diego and the Horn; US mairangi_bay at San Diego, Puget Sound and Norfolk; an Ushant TSS car carrier with no nation stated (Brest approaches, asset:eur:ushant_civ_merchants). | Open. Only the Evenes car carrier (V24 "MV Dyvi Skagerak") is pinned. | A build-time world traffic ledger gives each placed traffic hull a distinct variant world-wide, or uses Default. Fishing and dhow variants carry generic names and are exempt. |
| C30 | The embarked flights on CVN-71/72 escorts are labelled "transit (embarked)" or "underway_deployed (embarked)", while their hosts are "escort". | Applied (US Pacific final: markdown, packages and named_assets). | Rule 1.1: a `_flt` takes its host's allocation. "escort (embarked on tr_ddg_1; hand-off)", and likewise for tr_ddg_2, abe_ddg_1 and abe_ddg_2, in the markdown, packages and named_assets. |
| C31 | Replenishment options named across packages: the French and Italian Djibouti lines name asset:me:take_1 and asset:hoa:plan_aor_1 for cross-nation RAS; Gulf offers asset:me:take_1 for a CVN-71 RAS. | Clarified here. The Gulf/Horn French and Italian Djibouti lines now carry the "option only, not an allocation" sentence (final). | These are options, not allocations. asset:me:take_1 keeps its one allocation (support, Gulf of Oman station) and is not tasked to Djibouti. asset:hoa:plan_aor_1 keeps its PLAN group support allocation. Any transfer debits the supplier's own finite pool, and cross-nation RAS is untested. |
| C32 | **PLAN round pricing through `#!extend` stubs.** China maritime (final) follows the file stack and keeps plan_yj-18 metered: its 3789188689 stub sits on the 3775128499 base, which has AmmoPoints 4800. By the same stack, plan_hhq-9c (5,300), plan_yj-17 (10,100), plan_yj-18a (4,800) and plan_yj-20 (11,050) are also priced, with no SupplyCategory. China support (final, markdown lines 62–71, Wuxi support_services[3] and checks[7]) still lists all five as unrationed, reading only the winning stub. | Open (decision). | Proposed: follow the file stack, as `integration/campaign/build_pack.py` `all_copies()` documents for `#!extend` (the stub leaves the rest to the copy below it). The five rounds are then rationed by each supplier's point ceiling only, with no category gate. China support aligns its list. CHECK in the editor. |
| C33 | **Yulin release escort.** China support and China maritime say the guilin-mob-roro-2 release escort is "another Yulin hull at base at release time". At t0 Yulin's only resident_at_base hull is yulin_ssk_1 (039B): corvette_1 patrols, corvette_2 and ffg_1 escort, and ssk_3 is in servicing. | Open (decision). | Name the source, for example yulin_corvette_1 once it is back from patrol, or state that roro-2 sails unescorted when no surface hull is at base. One allocation at a time. |

### 1.5 Hull ledger (pins; ServiceDate from the winning variants files)

"Applied" means the corrected regional package already carries the pin. "To apply" names the package that still has to change.

| Pool | Pins (asset → hull, unit variant) | State | Free / barred |
|---|---|---|---|
| Burke Flight IIA, `_099_late` | usp:sd_ddg_1 → DDG-99 V1; usp:sd_ddg_2 → DDG-101 V2; usp:vinson_ddg_1 → DDG-102 V3; usp:abe_ddg_1 → DDG-103 V4; usp:abe_ddg_2 → DDG-104 V5 | Applied | – |
| | wpac:gw_csg_ddg1 → DDG-105 Dewey V6; me:ddg_1 → DDG-106 Stockdale V7; usatl:ddg_truman_esc_1 → DDG-107 Gravely V8 | To apply (W/C Pacific, Gulf, US Atlantic) | – |
| Burke Flight IIA, other files | usp:tr_ddg_1 / tr_ddg_2 → DDG-108 / 109 (`_108_late` V1/V2, 2024 onward) | Applied | Free: DDG-82, 83 (`_081_late` V2/V3); 86, 87 (`_085_late` V2/V3); 90 (`_089_late` V2); 94, 96 (`_091_late` V4/V6); 98 (`_097_late` V2); 110–112 (`_108_late` V3–V5); 113–116, 118 (`_113` V1–V4, V6). The non-late files `_081`, `_085`, `_089`, `_091`, `_097` and `_108` all end between 2018 and 2024 and are not used. |
| | usatl:ddg_truman_esc_2 → DDG-81 (`_081_late` V1); usatl:ddg_vacapes_patrol → DDG-85 (`_085_late` V1); usatl:ddg_norfolk_reserve → DDG-100 (`_100_late` V1); each is a **unit change** from `_099_late` | To apply (US Atlantic) | Barred: the `_2027` set (2027 onward; alias of `_099_late`); `_091_late` V1/V3/V5 (end 2022); `_097_late` V1 (ends 2025); `_113` V5 (ends 2022; DDG-117 duplicate). |
| | wpac:gw_csg_ddg2 → DDG-89 (`_089_late` V1, which carries its own MH-60R Sq9 pair); wpac:yoko_ddg_patrol → DDG-92 (`_091_late` V2) | To apply (W/C Pacific) | |
| | Rota: DDG-84 (`_084_late` V1), DDG-117 (`_117` V1), DDG-80 (`_080_late` V1), DDG-79 (`_079_late` V1) | Applied | DDG-51 held, unallocated. |
| Burke Flight I, `_054_late` (all 2025 onward) | usatl:ddg_vacapes_planeguard → DDG-54 V1; usatl:ddg_norfolk_ready → DDG-56 V2; wpac:yoko_ddg_maint → DDG-58 V3 | To apply (US Atlantic, W/C Pacific) | V4–V13 (DDG-59 to 70) free. |
| Burke Flight III, `f3_125` | usp:vinson_ddg_2 → DDG-125 V1 (2023 onward) | Applied | V3 DDG-128 is 2026 onward; V2 2027; V4 onward 2028–2037. |
| CG, `usn_cg_bunker_hill_vls_2024` (was `usn_cg_ticonderoga_vls_2025`, retired by Modern US Navy on 9 Oct 2026) | wpac:gw_csg_cg1 → CG-64 Gettysburg V5 | To apply (W/C Pacific) | Revised 10 Oct 2026: the author folded the Ticonderoga fits into one hull with nine named ships (V1 CG-58 to V9 CG-71). Check V5's ServiceDate window at build. |
| LCS, `usn_lcs_freedom_suw_late` | wpac:guam_lcs1 → LCS-27 V6 (2024 onward); me:lcs_1 → LCS-29 V7 (2024 onward) | To apply (W/C Pacific, Gulf) | V8 LCS-31 is 2026 onward. |
| SSN (2026 units, both 2026 onward) | wpac:guam_ssn1 → SSN-778 New Hampshire (`virginia_block2_2026` V1); wpac:guam_ssn2 → SSN-753 Albany (`los_angeles_flt3_2026` V1) | To apply (W/C Pacific) | |
| LHD | usp:sd_lhd_1 → any `usn_lhd_wasp` variant except V6 (2015–2021) | Single user; pick at build | |
| CVN | as 1.2 | Applied | `usn_cvn_nimitz_2025` Default and the 2027s_adou unit are not used. |
| T-AKE | usp:vinson_take_1 → T-AKE 1 V1; med:take_1 → T-AKE 11 V4 | Applied | V2 (T-AKE 2) free. |
| | wpac:gw_csg_take → T-AKE 6 V3 | To apply (W/C Pacific) | |
| | Default with a unique NameOverride: usatl:take_truman (Default applied; label to add), wpac:guam_take, me:take_1 | To apply (US Atlantic label, W/C Pacific, Gulf) | |
| T-AO | usp:sd_tao_1 → T-AO 187 V1 | Applied | V4 (T-AO 204) free. |
| | wpac:yoko_tao → T-AO 189 V2; me:tao_1 → T-AO 193 V3 | To apply (W/C Pacific, Gulf) | |
| T-AOE | usatl:taoe_norfolk → Default "(stand-in)" | Applied; accepted | V1–V4 (T-AOE 6, 7, 8, 10) free. |
| Algol | med:relief_sealift_1 → Regulus V6 | Applied | V7 Capella free. V2/V4/V5/V8 end 2025 (barred). |
| | usatl:takr_norfolk_relief → Algol V1; wpac:sealift_algol1 → Denebola V3 (drop V6 from both option lists) | To apply (US Atlantic, W/C Pacific) | |
| MSC tanker, `civ_ms_sealift_pacific` | ausio:dg_resupply_tanker → T-AOT-171 V4 | Applied | V3 free. |
| | NB San Diego traffic tanker → T-AOT-169 V2 (labelled) | Applied (US Pacific) | |
| | wpac:guam_taot_arrival → T-AOT-168 V1 | To apply (W/C Pacific) | |
| RRF / MSC / charter merchants | usp:sd_relief_cargo_1 → `civ_ms_seabee` V1 "SS Cape May"; satl:sealift_charter → `civ_ms_amra` V1 "MV Strathcarrol" | Applied | Seabee V2–3, roro_a V6–10 and C8 V23–26 are reserved, unused. |
| | Default with a unique label: JLSF E-1, E-2, S-1, S-2 | Applied | |
| | Default with a unique label: ausio:dg_mps_1, dg_mps_2, apf_loiter_1, apf_reserve_1 | Default applied; labels to make unique (C28) | |
| UK / RAN | `rn_opv_river_batch2` V1 HMS Forth; `rn_aor_tide` V3 Tidesurge; `ran_ssg_collins` V3/V2/V6/V5; `ran_ffh_anzac` V3/V7; `ran_opv_arafura` V2; `ran_aor_supply` V2; `ran_pt_boats_docks` V2 | Applied | Tide V1/V2/V4 free. |
| PLAN | 039B V1/V2 Yulin, V3 Ningbo; 039A V1; 056A V1/V2; 054A p5 V1 "Ziyang (522)" Yulin; 903A V1 Taihu (Yulin), V2 Chaohu (Ningbo); 003 V1; 055 V1 "Nanchang (101)" (not V4); 052D p3 V1 "Zibo (156)" Longpo; 901 V1 "965 CNS Hulunhu"; 956E early V1 "Hangzhou DDG-136"; 052D p4 V1 "Dazhou (135)"; 052D p1 V1 "Kunming (172)" (not V5); 054A p3 V1 "Daqin (576)"; 054 p2 V1 "Maanshan (525)"; 037IIE V1/V2; 039 (Song) V1; Kilo V1 (364) | Applied | |
| | hoa:plan_ddg_1 → 052D p3 V10 "Zhanjiang (165)"; hoa:plan_ffg_1 → 054A p5 V2 "Honghe (523)"; hoa:plan_aor_1 → 903A V3 "963 CNS Honghu" | To apply (Gulf/Horn) | 903A V4 "964 CNS Luomahu" and 901 V2 "967 CNS Chaganhu" free. Never 052D p3 V9. |
| French / Italian, single-use pools | hoa:fr_ffg_1 `fr_ffg_lafayette_modernized` V1–V3 (F710/F712/F713); hoa:it_ppa_1 `ita_ffg_ppa` V1–V5 (P 430–436; V5 is 2026 onward); eur:brest_fremm_asw | Single user each; pick at build | |

### 1.6 Counted aviation pools (world totals; each airframe once)

| Pool | Allocation | World total |
|---|---|---|
| B-52H (`dts_b-52h` Sq1 "2nd Bomb Wing"; the only operational livery) | Andersen 4 at base; DG 2 rotational; Tindal 2 reserve, not placed. Tindal's shipped 4 are excluded (C8). | 8 (6 placed) |
| B-1B (`usaf_b-1b_dts` Sq2) / B-2 (`usaf_b-2_spirit` Sq1) | DG 2 / DG 2 reserve, not placed. Tindal's shipped B-2 are excluded. | 2 / 2 (B-1B 2 placed at DG; B-2 0 placed) |
| KC-135 (`usaf_stratotanker` Sq1) | Andersen 2 (refuelling unverified). Tindal's shipped 2 are excluded. | 2 |
| P-8A, USN (`usn_p_8a` Sq1–14 only) | Jacksonville 4 (1 patrol, 2 at base, 1 reserve); Evenes detachment 1 (counted against Jacksonville); Muharraq 2; Lemonnier 1; Sigonella 3; Souda 1 | 12 as recorded; 11 once C10 is applied |
| P-8A / Poseidon, allied (`usn_p8`) | RNoAF Sq5 ×5 (Evenes); RAF Sq4 "No.54 Squadron" ×1 (Evenes visitor) | 6 |
| Typhoon FGR4 (`raf_ef2000_fgr4_late`) | Akrotiri 2 (1 resident, 1 servicing); Mount Pleasant 4 (2 QRA in the base group, 2 CAP airborne with HomeBase) | 6 |
| Voyager (`uk_a330_mrtt`) / A400M | Akrotiri 1/1; Mount Pleasant 1/1. At Mount Pleasant, AAR to the Typhoons and the A400M's supply-drop, SAR and maritime-patrol roles are missing_fit. | 2 / 2 |
| F-35A (`raaf_f-35a` Sq3) | Tindal 4 (cut from 8). Evenes QRA 2 are missing_fit and not placed. | 4 placed (+2 pending a Norway squadron) |
| MQ-9A / MQ-4C / KC-130J | Lemonnier 2 / Tindal 1 optional (SEST-authored "Det Tindal" squadron) / Lemonnier 1 | 2 / 0–1 / 1 |
| RC-135 (`boeing-rc135`) | Evenes Sq2 ×1. R03:117 states no operator; the US operator is SCENARIO. The named tails Sq3–7 are unallocated (allocate once if used). | 1 |
| Russian LRA | Tu-22M2 (proxy for M3): Olenya 6, Belaya 3. Tu-95MS: Olenya 2, Engels 2, Ukrainka 3. Tu-160 (Tu-160M proxy at Engels): Olenya 1, Engels 2. Tu-142M 1, Il-76MD (An-12 proxy) 1 and Il-78 1 (optional), all at Olenya. Belaya Il-78 0 (optional 1). A dispersal event moves an allocation; it never copies it. | 9 / 7 / 3 / 1 / 1 / 1 (+1 optional) |
| US carrier-embarked wings | Vinson 25, Roosevelt 25, Lincoln 25, GW 31, Truman 22 (unallocated in the RCOH contingency), Ike CQ det 8; LHD ACE 14 (12 without the AH-1W pair) | 150 |
| Escort-embarked helicopters | Counted: US Pacific 16, Rota 8, Gulf 3 (MH-60R); RAN 2 (MH-60R Sq20); PLAN Djibouti 2; French AS565 1; Italian SH-101A 1; Brest NH90 1. Not yet counted (C7): US Atlantic 8, W/C Pacific 9, China maritime 9, Russian context 3. | 34 counted (+29 pending) |
| Shore helicopters | North Island 6 MH-60R and 4 MH-60S stand-ins; Norfolk 4 MH-60R; Jacksonville 3 MH-60R; Lemonnier 2 HH-60 ("HH-60W stand-in"); Akrotiri 1 Merlin (SAR stand-in); BA 188 1 Puma stand-in and 1 Gazelle | 22 |
| JMSDF MPA | Naha 4 P-3C (Sq25, exact); Djibouti 2 P-3C (exact; squadron pin pending, C21); Kanoya 3 and Atsugi 4 P-1 stand-ins (pending proxy, not placed until a label route exists); Kanoya P-3C 0 (held) | 6 placed (+7 pending) |
| Other fixed-wing | BA 188 Mirage 2000-5F ×2; Lingshui J-15 ×4, KJ-500 ×2, Y-8FQ ×2; Brest approaches ATL2 ×1 (optional) | 2 / 8 / 0–1 |
| Fujian embarked wing | Unit-file default (not source). A CustomAirGroup trim is proposed; the count is not set. | Not counted (C7) |
| Civil airliners (traffic) | Muharraq 4; Indian Ocean 3; Mount Pleasant 1 (`civ_a330` Sq49, proxy); Japanese pools `civ_a330` Sq43/44 (Kanoya optional, Atsugi, Naha); Evenes optional `civ_as-350` (LoadoutVariant=Transport) | Counted per pool |

---

## 2. Connections register

**Conventions.**
- `↔` is a symmetric relationship (one row only). `→` is directional (hierarchy, flow, transit).
- **Basis** is one of:
  - **S**: SOURCE CLAIM;
  - **S-area**: the source names an area, city or theatre, and the node mapping is authored;
  - **S-guid**: simulation guidance, not fact;
  - **A**: authored (SCENARIO CHOICE).
- **GC** is an indicative great-circle distance between approximate anchors, not a route length.
- **±180** means the link crosses the antimeridian (P3a/B7). **NSN** means no stock sea-network coverage (stock sea_points.ini covers only longitudes −87.47 to 61.16).
- All route geometry is unvalidated.
- Rows 1–129 keep their numbers. Rows 130 onward are new.

### 2.1 Command, network and colocation relationships

| # | From | To | Kind | Basis | Source ref | Notes |
|---|---|---|---|---|---|---|
| 1 | chn_jlsf_wuhan_base | Wuxi, Guilin, Xining, Shenyang, Zhengzhou JLSCs | parent HQ of the five JLSCs | S | R02:44 (count R01:35) | GC 254–802 |
| 2 | usg_dla_distribution_network | usa_dla_susquehanna, usp_dla_san_joaquin | named primary CONUS hubs | S | R02:15, R02:29, R02:30 | 17 claimed, 2 named |
| 3 | usg_dla_distribution_network | DLA Yokosuka, Guam, Pearl Harbor, Bahrain, Sigonella, Germersheim | OCONUS hubs (6 named, 7 claimed) | S | R02:21, R02:23; table R02:31/32/34; R01:23 repeats Yokosuka and Guam | DG (R02:33) is not counted as DLA |
| 4 | usg_dla_distribution_network | ↔ Norfolk, NB San Diego, NAS Jax, PSNS | "major logistical operations are integrated"; no DLA centre asserted at any of them | S | R02:17 | co-location stated only generically |
| 5 | usg_dla_distribution_network | Richmond, Anniston, Red River, Tobyhanna | grouping ("other dedicated supply installations") | A | R02:17 (set apart from DLA centres) | |
| 6 | glob_us_afloat_prepositioning_fleet | ↔ usg_dla_distribution_network | APF cargo includes DLA fuels; not a parent | S | R01:23, R02:25, R02:21 | |
| 7 | usp_coronado_naval_base_coronado | NAS North Island; NAB Coronado | umbrella of components | S | R01:15, R03:17 / R03:17 | no NB San Diego link stated |
| 8 | NAS North Island | ↔ NAB Coronado | sibling components | S | R03:17 | |
| 9 | usp_kitsap_naval_base_kitsap | PSNS; Bangor | umbrella (Bremerton = PSNS is an inference) | S | R01:17, R03:21 | |
| 10 | PSNS | ↔ Bangor | sibling components | S | R01:17, R03:21 | |
| 11 | satl_falklands_raf_mount_pleasant | ↔ satl_falklands_mare_harbour | operate in tandem; joint intercepts and escorts (Typhoons with HMS Forth) | S | R01:59, R02:71, R03:146 | GC ~5 |
| 12 | med_naples_nsa_naples | ↔ med_sigonella_nas_sigonella | joint C2 and maritime-patrol coverage (Med and N. Africa) | S | R03:44 | role split inferred; GC ~212 |
| 13 | med_sigonella_nas_sigonella | ↔ med_souda_bay_nsa | Mediterranean ASW and intelligence backbone | S | R03:44 | GC ~461 |
| 14 | eur_deveselu | ↔ eur_redzikowo | companion Aegis Ashore sites | S | R03:44 | GC ~685; no coverage rule |
| 15 | DLA Bahrain | ↔ DLA Sigonella ↔ DLA Germersheim | Middle East and Europe sustainment trio | S | R02:23 | |
| 16 | DLA Yokosuka | ↔ DLA Guam | Indo-Pacific logistical spine | S | R02:23 | GC ~1,338 |
| 17 | DLA Pearl Harbor | ↔ DLA Yokosuka; ↔ DLA Guam | Indo-Pacific logistical spine | S | R02:23 | GC ~3,350 / ~3,305; **±180**, NSN |
| 18 | wpac_yokosuka_naval_base | ↔ DLA Yokosuka | supported by the DLA centre | S | R01:23, R02:31, R02:23 | site not stated |
| 19 | wpac_guam_naval_base_apra_harbor | ↔ DLA Guam | supported by the DLA centre | S | R01:23, R02:23, R02:32 | |
| 20 | wpac_yokosuka_naval_base | ↔ wpac_guam_naval_base_apra_harbor | "operating in tandem" (working relationship, not colocation) | S | R03:38 | GC ~1,338; NSN |
| 21 | Apra | ↔ wpac_guam_andersen_afb | same island ("adjacent"; not a placement instruction) | S | R03:38 | GC ~18 |
| 22 | Andersen | → DLA Guam | fuel and munitions tether | A | R02:32 describes DLA Guam only; R01:67/R02:77 tether guidance names DLA Guam, not Andersen | |
| 23 | me_bahrain_muharraq_airfield | → me_bahrain_nsa_bahrain | aviation support | S | R03:42 | nationality not stated |
| 24 | me_uae_jebel_ali_port | → NSA Bahrain | logistics node (asset:me:tao_1 shuttle, A) | S | R03:42 | GC ~254 |
| 25 | Kuwait / Oman logistics nodes (unnamed) | → NSA Bahrain | logistics | S | R03:42 | backlog; no node (plan:46) |
| 26 | NSA Bahrain | ↔ DLA Bahrain | same country; stock represented by asset:me:take_1 | A | R02:23 names the centre only | |
| 27 | Djibouti cluster: Lemonnier, PLA, BA 188/Héron, JP, IT (all pairs) | ↔ | nearby, "within miles"; not colocated | S | R01:49, R01:51 | separate operators and sides |
| 28 | Camp Lemonnier | ↔ PLA Support Base | rival neighbours; ROE "without triggering unintended escalation" | S / S-guid | R01:51, R01:70 | no espionage mechanic |
| 29 | JP facility | ↔ IT facility | share the R01:51 role sentence | S | R01:51 | |
| 30 | BA 188 air element | ↔ Héron naval element | internal link pending the naming/split check | A | R01:51; seed:23 | |
| 31 | Yulin | ↔ Lingshui; Longpo ↔ Lingshui | operate in tandem | S | R01:31, R03:101 | GC ~29 / ~25 |
| 32 | Yulin | ↔ Longpo | neighbours (Longpo further east on Yalong Bay) | S | R03:99 | GC ~6 |
| 33 | Ukrainka | ↔ Belaya | co-listed relocation destinations | S | R01:41, R03:80 | GC ~919 |
| 34 | Engels-2 | ↔ Belaya | joint strike-vulnerability statement (status, not logistics) | S | R03:160 | no deterministic rule |
| 35 | Kanoya | ↔ Atsugi ↔ Naha | JMSDF Fleet Air Force network (FAW1/4/5) | S | R03:123; R03:127 (Atsugi's 3rd Squadron; P-1); R01:61 (Naha/Atsugi) | GC 354–822; FAW4 subordination of the 3rd Squadron not stated (CHECK) |

### 2.2 Source-described sea lines, fleet movements and operating areas

| # | From | To | Kind | Basis | Source ref | Notes |
|---|---|---|---|---|---|---|
| 36 | NB San Diego | → SoCal operating area (~32N 119W) | TSTA/FEP work-ups | S | R03:50 | GC ~100; NSN |
| 37 | NAS North Island | → SoCal operating area | CQ and deck cycles | S-guid; CVN-70 pairing A | R03:17, R03:50 | |
| 38 | NB San Diego | ↔ NAS North Island | Pacific-bound CSG embarkation; berth unresolved | S-area | R03:17; R03:50, R03:56–58 (city "San Diego") | the parent link was removed by the fidelity pass |
| 39 | NB San Diego | → CENTCOM AOR (mapped to NSA Bahrain) | CVN-71 transit | S-area | R03:50, R03:57; R03:42 | GC ~8,350 to 8N 66E; **±180**; NSN |
| 40 | NB San Diego | → Western Pacific (mapped to the Guam and Yokosuka areas) | CVN-72 deployment | S-area | R03:50, R03:58 | GC ~5,700; **±180**; NSN |
| 41 | NB San Diego | ↔ PSNS | Nimitz homeport shifts and deployments; both endpoints city-level | S-area | R03:48, R03:54 | GC ~927; NSN |
| 42 | Yokosuka | → PSNS | Reagan's former forward-deployed role; Reagan now in maintenance | **S (role); node mapping A** | R03:38 (George Washington assumed the role from Reagan); R03:62 gives Reagan's home port only as the city "Kitsap-Bremerton"; Bremerton = PSNS is inferred | GC ~4,161; **±180**. The US Pacific PSNS row now reads "source (role); node mapping authored" (final). The W/C Pacific Yokosuka row still says plain "source" (5.4). |
| 43 | Norfolk | ↔ Newport News | RCOH example facility ("facilities like") | S (hedged) | R03:50, R03:60 | GC ~6; not parent or colocated |
| 44 | Norfolk | → Virginia Capes operating area; → Jacksonville operating areas | CQ before deployment | S | R03:48 | GC ~72 / ~483 |
| 45 | Norfolk | → Atlantic / South America | CVN-75 UNITAS / work-ups | S | R03:61 | CHECK RCOH (C18) |
| 46 | Norfolk | → Mediterranean (Rota gateway) | force generation for the Med theatre | S-area | R03:19, R03:44 | GC ~3,282 |
| 47 | Norfolk | → Middle East (NSA Bahrain) | force generation; Ike and Truman stage for ME deployments | S-area | R03:19, R03:48 | GC ~5,971; real route via the Med and Suez |
| 48 | NAS Jacksonville | → Atlantic and Caribbean | ASW focus | S | R03:23 | |
| 49 | Yokosuka | → Western Pacific / East China Sea | GW patrol focus | S | R03:59 | box ~30N 137E is A (GC ~345) |
| 50 | Guam (island) | → South China Sea, Taiwan Strait, Korean Peninsula | dispatch destinations | S | R03:38 | island-level; bombers routed to Andersen is A |
| 51 | Guam, Diego Garcia | ↔ SLOCs | vulnerable resupply routes. Mining Apra's approaches or SSK harassment "could effectively neutralize the combat effectiveness of the forward-deployed forces by starving them of fuel and munitions" | S-guid | R03:172 (joint, island-level) | applying it to the Andersen detachment is A |
| 52 | Yulin | → SLOCs to Guam and Diego Garcia | SSK harassment of logistical shipping; target identity contextual | S-guid | R03:172 | GC ~2,040 / ~2,682; NSN |
| 53 | Apra approaches | – | mining | S-guid | R03:172 | mine mechanics not established; no US MCM function described |
| 54 | Diego Garcia | ↔ APF | APF anchorage and bulk fuel hub (relationship) | S | R01:23, R02:25, R02:33 | lagoon subset only (inference, fidelity check 1) |
| 55 | APF | → unnamed "strategic regions" | loiter | S | R01:23, R02:25 | authored Indian Ocean area |
| 56 | APF | → frontline bases (unnamed) | disruption causes cascading delays | S-guid | R01:68, R02:78 | backlog; no mechanic |
| 57 | Diego Garcia | → Middle East and Asia | long-range strike reach | S | R03:40 | "theater ballistic missile threats" qualifier is R03:40's |
| 58 | Rota | ↔ Strait of Gibraltar | Atlantic–Med gateway | S-area | R03:44 ("gateway between the Atlantic and the Mediterranean"; the Strait is not named) | Comes from the Rota role_source, not a package connection row. DDG-117's Gibraltar patrol box and the stock sea links Rota–Banco Majuan are authored. |
| 59 | Rota | ↔ NATO missile-defence shield | destroyer role integration | S | R03:44 | no intercept rule |
| 60 | Akrotiri | → Eastern Mediterranean | forward operating, SAR, crisis staging | S | R01:59 | |
| 61 | HMAS Stirling | → Indian Ocean | presence anchor | S | R01:55 | |
| 62 | Evenes | → Barents Sea (QRA intercepts of Tu-142/Tu-95 "in international airspace"); → Kola bastions and departure area (ASW axis); → GIUK | | S | R03:117; R03:115, R03:166; R01:61, R03:115 | CHECK GIUK geography |
| 63 | Evenes | ↔ allied UK/US MPA | "United States and United Kingdom P-8A Poseidons, as well as RC-135 Rivet Joint intelligence aircraft" stage from Evenes; data hand-off | S (staging); S-guid (R03:166) | R03:117, R03:166 | RC-135 operator not stated (the US pick is SCENARIO). R03:166 asks for shared situational awareness; the scenario adds none beyond the engine's datalink (CHECK). No perfect-detection rule. |
| 64 | Kola bastions (no node) | → GIUK → North Atlantic | Russian submarine transit | S | R03:115, R03:166 | asset:rus:barents_ssgn_1 transit is A |
| 65 | Olenya | ↔ GIUK / North Atlantic | proximity | S | R03:70 | |
| 66 | Olenya | → southbound standoff axis | strike sorties (off-map, not modelled) | S | R03:72 | |
| 67 | Kanoya, Atsugi (Naha via R01:61) | → First Island Chain | sonobuoy barriers / ASW web | S | R03:168, R01:61, R03:123 | NSN |
| 68 | Kanoya, Atsugi | ↔ Yulin, Longpo | allied ASW curtain against submarines | S | R03:168 | |
| 69 | Kanoya, Atsugi | ↔ Lingshui | J-15/Y-8Q counter-screen | S | R03:168 | GC ~1,369 / ~1,863 |
| 70 | Lingshui | → SCS (ISR on foreign naval assets); disputed outposts | | S | R03:101 | |
| 71 | Ningbo | → East China Sea; → Taiwan Strait | control / contingency posture | S | R03:105 (ECS); R01:31, R03:105 (Taiwan) | |
| 72 | Mount Pleasant | → Falklands, South Georgia and South Sandwich Islands air-defence area | Typhoon coverage | S | R03:144 | SG ~800, SSI ~1,150 NM (approx) |
| 73 | Mare Harbour (HMS Forth) | ↔ Mount Pleasant Typhoons | intercepts and escorts | S | R03:146 | |
| 74 | Mare Harbour | → South Atlantic | counter-piracy, fishery and sovereignty patrols | S | R03:146 | |
| 75 | Shenyang / Xining / Zhengzhou | → Yellow Sea–Korea / Western / Central (reserve) | supported theatre | S | R02:57 / R02:58 / R02:59 | |
| 76 | Guilin, Wuxi | → Yulin, Longpo, Ningbo | joint fuel and munitions anchor ("would feed"); no per-base pairing | S | R02:48 | |
| 77 | Engels-2 | → unnamed secondary airfields | dispersal | S | R03:78 | backlog |
| 78 | Île Longue | – Brest roadstead | location only | S | R03:150 | context only; no nuclear detail (plan:43, seed:25) |
| 130 | JP facility; IT facility | → Red Sea | anti-piracy, counterterrorism and intelligence area | S | R01:51 ("Both Japan and Italy ... across the Red Sea") | The Italian package now has the same split as Japan's (final): Red Sea (source, R01:51) and Gulf of Aden (authored, row 143) |
| 131 | Mount Pleasant, Mare Harbour | → South Atlantic area | reference only, no routes | S | R01:59; R02:71; R03:142, R03:146 | |
| 132 | Mount Pleasant | → Antarctic region | power-projection reference only; no routes or activity | S | R03:142 | |
| 133 | Camp Lemonnier | → US Africa Command (no node) | regional operational hub | S | R01:49, R03:44 | |
| 134 | Atsugi | → South Korea | incident context only; no hostility rule | S | R03:127 | |

### 2.3 Authored logistics lines and air routes (labelled; implied by the reports)

| # | From | To | Kind | Basis | Source ref (role only) | Notes |
|---|---|---|---|---|---|---|
| 79 | San Joaquin | ↔ Susquehanna | paired primary CONUS hubs | S | R02:15 | GC ~2,060 |
| 80 | San Joaquin | → NB San Diego | West Coast resupply origin; releases asset:usp:sd_relief_cargo_1 | A | R02:30 | GC ~367 |
| 81 | San Joaquin | → DLA Pearl Harbor | CONUS → forward hub | A | "Pacific" is authored (fidelity) | GC ~2,100; does not cross 180 |
| 82 | DLA Pearl Harbor | → DLA Guam / Apra | sealift relief route (the Algol spawns west of 180, ~15N 170E, to avoid the dependency) | A | R02:23 spine | GC ~3,305; **±180** |
| 83 | DLA Pearl Harbor | ↔ NB San Diego | transpacific waypoint | A | – | GC ~2,270 |
| 84 | Susquehanna | → Norfolk, Jacksonville | East Coast resupply origin | A | R02:29 | GC ~197 / ~642 |
| 85 | Richmond | → Jacksonville, Norfolk | aviation spares (abstract) | A | R02:17 | |
| 86 | Anniston, Red River, Tobyhanna | → Norfolk | port of embarkation via RRF ro-ro (`civ_ms_roro_c`, not allocated) | A | R02:17 | |
| 87 | Whiting | → Jacksonville, Norfolk | aircrew replacement (abstract) | A | R03:23 | |
| 88 | Patuxent | ↔ Jacksonville | P-8A type context only | A | R03:23 | |
| 89 | Jacksonville | → Norfolk | P-8A cover for departures and the CVN-75 transit | A | – | |
| 90 | Jacksonville | → Evenes | home allocation of the visiting USN P-8A | A | R03:117 (staging) | GC ~3,901; C10 still to apply in US Atlantic |
| 91 | NB San Diego | ↔ NAS North Island | helicopter logistics / SAR | A | – | |
| 92 | NB San Diego | ↔ NAB Coronado | LHD amphibious training partner | A | R03:17 (training role) | |
| 93 | PSNS | → Norfolk | possible Nimitz inactivation move (public reporting; CHECK only) | A | – | GC ~2,118; real route via Panama |
| 94 | Norfolk | → Rota → Souda / Sigonella | Med transit gateway; T-AKE rendezvous | A | R03:19, R03:44 | GC ~3,282, ~1,474, ~1,016 |
| 95 | US sealift reserve (asset:med:relief_sealift_1) | → Rota (DDG-117 escort) → Souda | finite relief through Gibraltar | A | R02:23, R02:34 (gateway) | C19 |
| 96 | Germersheim | → Rota, Sigonella NAS | abstract materiel flow | A | R02:23 | GC ~991 / ~762 |
| 97 | Sigonella NAS | ↔ DLA Sigonella | name association; colocation not stated | A | R02:34; R03:44 | |
| 98 | Sigonella NAS | → Rota | P-8A cover for destroyer transits | A | – | |
| 99 | Rota | ↔ Deveselu, Redzikowo | missile-defence context (same paragraph, not linked) | A | R03:44 | |
| 100 | Souda | ↔ Akrotiri | eastern-Med neighbours | A | – | GC ~438 |
| 101 | Souda | → NSA Bahrain via Suez | transit (stock sea points Port Said, Suez) | A | – | GC ~1,466; route longer |
| 102 | Naples | → Rota, Souda | theatre command context | A | – | |
| 103 | NSA Bahrain | ↔ Camp Lemonnier | US transit Hormuz–Gulf of Aden–Bab-el-Mandeb | A | R03:42 (areas), R03:44 | GC ~975 |
| 104 | Diego Garcia (APF / DG suppliers) | → NSA Bahrain; → Lemonnier | Indian Ocean → Arabian Sea / Bab-el-Mandeb | A | R03:40, R02:25 | GC ~2,377 / ~2,080 |
| 105 | Diego Garcia | ↔ HMAS Stirling | allied transit / rendezvous | A | – | GC ~2,836; NSN |
| 106 | Diego Garcia | ↔ Tindal | bomber rotation alternate | A | R01:55, R03:40 | GC ~3,552 (beyond the played 3,450) |
| 107 | Diego Garcia | ↔ Andersen | paired in the joint reach statement; no link stated | A | R03:172 | GC ~4,497 |
| 108 | Andersen | ↔ Tindal | counted bomber pool and routing | A | R03:38 (bombers dispatched from Guam; site not named) | GC ~1,830 |
| 109 | Stirling | ↔ Tindal | national network | A | R01:55 names both | GC ~1,401 |
| 110 | Stirling | → Strait of Malacca | northern reach | A | R03:7 (chokepoint only) | GC ~2,130 |
| 111 | Tindal | → Timor / Arafura Sea | ISR orbit | A | – | |
| 112 | Guilin | → Yulin (Qiongzhou approach → Yulin) | primary pairing; mobilised relief run | A | R02:44, R02:56 | GC ~136–150 (run); NSN |
| 113 | Wuxi | → Ningbo (Yangtze approach → Ningbo) | primary pairing; mobilised relief run | A | R02:44, R02:55 | GC ~71 (run) |
| 114 | Wuhan rail hubs (unnamed) | → Ningbo, Yulin | reinforcement-timing modifier (a delay, never instant) | A | R01:68, R02:78 | |
| 115 | Yulin | ↔ Ningbo | inter-theatre transfer | A | – | GC ~964 |
| 116 | Yulin / Longpo | → PLA Support Base Djibouti | optional route for the escort group; no Hainan hull moves (the Djibouti hulls are owned by hoa_djibouti_pla_support_base) | A | R01:51 (base exists only) | GC ~3,855 |
| 117 | Lingshui | → asset:chn:scs_cv_1 | land-based air cover (role R03:101; pairing ours) | A | R03:101 | the carrier wing never also appears at Lingshui |
| 118 | Lingshui | ↔ Andersen | opposing overlap | A | R03:38, R03:101 | GC ~2,033 |
| 119 | Ningbo | ↔ Naha | opposing patrol overlap near the Taiwan Strait | A | R03:123 (Naha proximity only) | GC ~380 |
| 120 | Ningbo | ↔ Yokosuka | opposing overlap (GW ECS focus) | A | R03:59 | GC ~963 |
| 121 | Yokosuka | ↔ Atsugi | geographic neighbours; no reported relationship | A | – | GC ~12–14. No JMSDF escort or Mashuu AOE exists to pair with (C26). |
| 122 | Yokosuka, Apra | ↔ CVN-72 group | visitor / rendezvous (transfers debit local suppliers) | A | R03:58 | |
| 123 | NSA Bahrain | ↔ CVN-71 group | optional RAS with asset:me:take_1 (an option, C31) | A | R03:57 | only if US Pacific sends no supplier |
| 124 | Evenes | ↔ Olenya | QRA intercept context | A | R03:117 (origin unnamed), R03:72 | GC ~371 |
| 125 | Olenya | → Barents Sea | maritime-strike and patrol area | A | R03:66, R03:72, R03:117 | GC ~233 |
| 126 | Engels-2 | → Olenya | relocation / dispersal inflow | A | R03:72 ("deeper inside European Russia"); R03:162 (no origin named) | GC ~1,067 |
| 127 | Engels-2 | → Ukrainka, Belaya | relocation context (not Engels-specific) | A | R01:41, R03:80 | GC ~2,912 / ~2,055 |
| 128 | Ukrainka / Belaya | → Sea of Okhotsk | Pacific patrol / maritime-strike reach | A | R03:80, R03:66 | GC ~738 / ~1,546 |
| 129 | Mount Pleasant | ↔ UK air bridge (no UK node) | Voyager/A400M arrivals and departures; distance rationale | S (R02:71 rationale); route A; node backlog | R02:71 | |
| 135 | Ningbo (asset:chn:ningbo_ffg_1) | → Wuxi relief run (wuxi-mob-roro-1) | escort from t0 (C14/C24) | A | – | removed from the Ningbo base count |
| 136 | Yulin (asset:chn:yulin_corvette_2) | → Guilin relief run (guilin-mob-cargo-1) | escort from t0 (C14/C24) | A | – | removed from the Yulin base count |
| 137 | Mare Harbour | ← sealift lane from the north (asset:satl:sealift_charter) | periodic charter arrival and departure | A | – | stock sea points south of 25S: Table Bay and Rio de la Plata only |
| 138 | Mare Harbour | ↔ asset:satl:rfa_tide_relief | dormant relief arrival; RAS with HMS Forth | A | – | |
| 139 | Brest approaches (Île Longue context) | → FREMM ASW patrol box ~48.15–48.33N, 4.8–5.2W | ASW patrol | A | R03:150 locates Île Longue only | CHECK reefs and islets (section 4) |
| 140 | Atsugi | ↔ JMSDF Djibouti facility | context only; nothing subtracted from either allocation (C25) | A | R01:51 names no aircraft | Japan/Norway (final) still says "optional source of a JMSDF MPA detachment (subtract from this allocation)" (markdown line 352 and the package connection), and atsugi_p1_4 still says "take it from this allocation" (C25, 5.4). |
| 141 | Russian Okhotsk context (no node) | ↔ Kanoya, Atsugi, Naha | Russian Pacific Fleet counterpart of the JMSDF network | A | R03:121 (target only) | |
| 142 | Naha | ↔ Lingshui | opposing ISR / counter-screen | A | R03:168 names Kanoya and Atsugi, not Naha | |
| 143 | JP facility; IT facility | → Gulf of Aden | patrol track | A | not named in R01–R03 | |

### 2.4 Stock engine data usable as route skeletons (engine data, not research)
- **Sea links:**
  - Rota–Banco Majuan, Rota–Cabo de São Vicente;
  - Naples–Genoa / Iles Cani; Canale di Malta;
  - Port Said / Suez;
  - Al Jubayl–As Salamah and Minah Al Ahmadi–As Salamah (the in-Gulf skeleton; only the Bahrain and Jebel Ali spurs need authoring). Their endpoints are ports.ini [Port Al Jubayl] and [Port Minah Al Ahmadi];
  - As Salamah–Ras al Kul–Gulf of Oman; South Aden–Gulf of Aden–Bab El Mandeb;
  - Chesapeake Fairway–Cape Hatteras;
  - Ofotfjorden / North West Andøya / Lofoten Basin;
  - Ushant–Brest and Brest–Ushant to the Ushant TSS points.
- **Patrol areas "Barents Fishing", "Loefoten Fishing" and "Manche Fishing"** are **geometry precedent only**. Their LinkedSpawns are campaign spawns (for "Barents Fishing": Port Reykjavik, Port Narvik and Port Murmansk with `civ_fv_fishingboat_a`, `civ_fv_okean`, `civ_fv_sidetrawler`; vanilla campaigns/patrol_areas.ini:206). They draw from the whole variant pool, so they cannot honour a variant pin and do not include `civ_fv_sterntrawler_a`. Pinned Russian, Norwegian or French fishing is mission-placed as NeutralVessel entries with VariantReference.
- **Airports:**
  - KLAX, KSFO and KSEA link only to US and European airports, so trans-Pacific airways are authored and **±180**;
  - stock airports.ini has no Japanese, Chinese or Korean civil airport;
  - OBBI → KJFK, EDDF, VIDP.
- The stock sea network does not cover the Pacific or the Indian Ocean east of 61E.

---

## 3. Collection gaps

| Platform / function | Operator | Outcome | Affected nodes | Suggested resolution |
|---|---|---|---|---|
| Named naval air station / air base unit | US | proxy (usa_airbase V1 "Naval Air Station", airfield_small_1, nato_small_airbase) | North Island, NAS Norfolk, NAS Jax, Sigonella, Souda, Lemonnier, Patuxent (marker 0), Andersen, DG | Now: labelled proxy with an at-base-only CustomAirGroup. SEST pack: airbase_us clones on the integration/raaf-bases pattern; add FlightDeck_AmmoCapacity and fix the malformed default AirGroup lines. |
| Named UK air base | UK | proxy now; a named unit is none | Akrotiri, Mount Pleasant | Akrotiri: nato_small_airbase, Nation=uk, labelled. Mount Pleasant interim: is_airbase_akureyri V2 ("RAF Gibraltar", Nation=UK) relabelled with its US group replaced. Avoid is_airbase_reykjavik. SEST: "RAF Akrotiri" and "RAF Mount Pleasant" clones (Nation=UK). |
| Named Norway air base | Norway | proxy (nato_small_airbase, Nation=norway) | Evenes | SEST airbase_us clone, Nation=Norway, with usn_p8 Sq5. |
| Named JMSDF bases | Japan | proxy (airfield_small_1 V5; Cold War group of 44 aircraft) | Kanoya, Atsugi, Naha, JMSDF Djibouti | V5 labelled, group replaced. Atsugi's usa_airbase alternative only with the same at-base-only group. SEST: named clones. |
| Named PLAN air base | China | proxy (china_large_airbase V2; a named Lingshui unit is missing_fit) | Lingshui | V2 labelled; the mission CustomAirGroup replaces V2's own group (plaaf_j5 Sq5 does not resolve). SEST: named clone. |
| Named Russian bases (Ukrainka, Belaya) | Russia | proxy (wp_airbase_modern Default; wp_airbase_4) | Ukrainka, Belaya | Labelled stand-in; optional SEST clone. |
| Finite shore ship-ammunition supplier / port | all | missing_fit. nv_pt_boats_docks (Vessel) and nv_pt_boats_docks_small (Submarine) are effectively unlimited (AmmoCapacity 9,999,999,999). ran_pt_boats_docks and _small have no supply block. Every vanilla port_* is HideIn=MissionEditor. | San Diego, PSNS, Yokosuka, Apra, Rota (option 0), Souda (option 0), Stirling, Mare Harbour, NSA Bahrain, Jebel Ali, Héron, PLA pier, Yulin, Longpo, Ningbo | SEST pack: capped port clone (finite pool and categories) per nation. Until then: visual or berth marker only, or a disclosed unlimited abstraction (Yulin, Longpo, Ningbo and Mare Harbour use nv_pt_boats_docks and must disclose it). |
| Shore command / HQ installation | US, China | none (FOB marker proxy; nv_headquarters rejected for its unlimited land-unit supply) | USFF HQ, NAVCENT, C7F, Naples, Wuhan, PLA Djibouti HQ | Abstract, or a labelled FOB / warehouses_3 marker. |
| Depot / distribution installation | US, China | none (generic warehouses are static targets; usa_car_hemtt is a working land resupplier and is kept out of markers) | All DLA centres, Army depots, JLSCs | Abstract only. |
| Shipyard / drydock / repair | US | none (US_Los_Alamos is a 1961–1991 target object) | PSNS, Newport News | Labelled scenery; test the changelog's "rearm and repair trigger actions" (candidate). |
| Command ship | US | none | Seventh Fleet, Naples | Backlog. |
| MH-60S / HSC squadron | US | missing_fit; placed rows are proxy usn_hh-60 (or usn_sh-60f), labelled "MH-60S stand-in" | North Island, CVN wings | SEST names / squadron patch. |
| C-2A / CMV-22B / MQ-25 | US | none / missing_fit (usmc_mv-22b, USMC liveries only) / proxy (usn_ka-3b, squadrons 1956–1991, not allocated) | Carrier groups | Backlog; SEST squadron patch for CMV-22B. |
| USN C-130T; USAF C-130J / HC-/MC-130J | US | missing_fit (usmc_kc-130t squadrons end 2002–2021; usmc_kc-130j adds a refuel system) | Jax, Lemonnier | Label "C-130J stand-in (KC-130J)" where used. |
| MQ-4C, US squadron | US | missing_fit (raaf_mq-4c_triton: Australian squadrons only, MQ-9 ER mesh) | Jax, Sigonella option | SEST squadron patch. |
| C-17 / C-5 | US | none; usaf_c-141b is dated 1965–2006 | Andersen, DG, Lemonnier, Muharraq | Date-filter test; otherwise no airlift. |
| CV-22B / HH-60W | US | proxy (usmc_mv-22b / usn_hh-60, separate labels) | Lemonnier | One type label per airframe. |
| America LHA; San Antonio LPD; LSD; LCAC/LCU | US | proxy (fictional "Tripoli"); Cold War proxies; none | NB San Diego, NAB | Backlog. |
| T-AH, tug, salvage, T-EPF, ESB/ESD, LMSR, modern MPS | US | none; MPS stand-ins are civ_ms_c8 / roro_a / seabee Default (Role=Merchant) | DG, APF, US bases | Labelled Default hulls (C11, C28); backlog. |
| Avenger MCM; LCS MCM module; MH-53E | US | proxy (usn_mso_aggressive, Cold War) / missing_fit / none | Guam, Bahrain | Not proposed (no MCM is sourced); mine mechanics are not established. |
| Submarine tender | US | effectively none (usn_ae_kilauea variants end 1980–1998) | Guam | Backlog. |
| Modern Nimitz shipped air wings | US | missing_fit (every shipped variant wing fails) | All CVN rows | Mission CustomAirGroup (mandatory); optional SEST variant fix. |
| CVN-76 on a modern unit | US | proxy (legacy usn_cvn_nimitz V9) | PSNS | Visible label. |
| Test-squadron liveries / unmanned test types | US | missing_fit | Patuxent | Not placed. |
| Military trainers (T-6B, TH-73) | US | none; civ_v35 / fr_as-350 labelled proxies | Whiting | Abstract. |
| Aegis Ashore (SPY-1, land SM-3) | US | none; radar-marker proxies at quantity 0 | Deveselu, Redzikowo | Marker only, labelled "not modelled". |
| US rounds with no SupplyCategory | US | data fact, not a gap: no category gate rations them, only the supplier's point ceiling | Rota (DDG-117) | DDG-117's alias base (usn_ddg_burke_f2a_113) loads SM-2 `usn_rim-66m-5` (3629144864), which has no SupplyCategory and inherits 1,768 AP from `usn_rim-66g`, and ESSM `usn_rim-162a` (500 AP). Its SM-3 `usn_rim-161c` (9,000) and SM-6 `usn_rim-174a` (4,200) are SEST_LongRangeSAM. DDG-84/80/79 carry `usn_rim-161d`, `usn_rim-174c` (8,000) and `usn_rim-66p` (2,500), all SEST_LongRangeSAM. A 2,000-ceiling supplier blocks `usn_rim-66p` but not `usn_rim-66m-5`. |
| NASAMS III; counter-UAS | Norway | proxy (usa_SLAMRAAM_radar ×1 and usa_SLAMRAAM_launcher ×2) / none | Evenes | Labelled small layer (plan:24); CHECK. |
| Sky Sabre (Land Ceptor) | UK | none; raf_rapier_launcher V1 (Nation=UK) is the labelled proxy "Sky Sabre (stand-in: Rapier)" | Mount Pleasant | 2 launchers. No UK-flagged GBAD reloader exists: usa_car_m923, usa_car_hemtt, wp_car_ural, tgt_ammo_depot_small and nv_headquarters all target LandUnit and none is UK-flagged. A re-nationed usa_car_m923 is a SCENARIO option; transfer untested. |
| AAR receivers: Typhoon, Tu-95MS, Tu-160, F-35A, B-52H/B-2, P-8; modded US tankers lack [AerialRefueling] | UK, Russia, US, AUS | missing_fit | Mount Pleasant, Akrotiri, Olenya, Engels, Ukrainka, Tindal, Andersen | Use only declared pairs: Voyager→A400M; Il-78→Tu-22M2/Tu-142M; KC-130J; FR MRTT→M2000-5F. Test. |
| A400M supply drop / SAR / maritime patrol | UK | missing_fit (its Supply store is Type=Paratrooper) | Mount Pleasant | The transport platform is exact; the sourced functions are missing. |
| 1435 Flight Typhoon identity | UK | missing_fit (use Default FGR4; Squadron1 is "1(F) Squadron") | Mount Pleasant | SEST names patch. |
| Modern UK SAR / Chinook / Puma | UK | none; rn_merlin_hm2 is the labelled SAR stand-in | Akrotiri, Mount Pleasant | Backlog. |
| UK F-35B; RFA solid stores (Fort Victoria, Wave, Argus, Bay) | UK | missing_fit / none (rn_aor_tide is a labelled proxy) | Akrotiri, South Atlantic | Tide V3 is the only RFA supplier (Mare Harbour reserve). |
| F-35A in Norwegian service | Norway | missing_fit | Evenes QRA | SEST squadron pack on raaf_f-35a. |
| Maud; Nansen; Ula; Norway-flag airliner | Norway | none / missing_fit / proxy (knm_ss_kobben) / none | Evenes | Backlog. |
| Kawasaki P-1 (and HPS-106, MAD, Type 97, ASM-1C) | Japan | proxy (usn_p-3c Japan squadron), **pending: not placed until a label route exists** | Kanoya, Atsugi | A mission name override, even if proven, can label only the separate airborne entries (kanoya_p1_1, atsugi_p1_1). The at-base stand-ins inside a CustomAirGroup need the SEST squadron patch (labelled Japan squadrons reusing the 1st/3rd FAS liveries). CHECK: usn_p-3c [Default] ServiceDate is 1977–1995 and Squadron21–29 set none of their own, so a 2026+ mission may filter them. That affects Naha's exact P-3Cs, the Djibouti P-3Cs and every stand-in. |
| Kongo / Akizuki / Murasame / Takanami | Japan | none (jmsdf_aoe_mashuu exists as a proxy supplier, not proposed) | Djibouti JP, Yokosuka | Backlog; no JMSDF ship is allocated (C26). |
| PLAN sub tender (926), rescue/salvage, MCM, AGI 815 | China | none | Yulin, Ningbo | Backlog. |
| PLAN Marine / SOF | China | none (generic PLA vehicles resolve but do not represent SOF) | Yulin | Abstract. |
| CCG / maritime militia; Chinese-flag merchant or fishing | China | none; civ_fv_fishingboat_a V5 with Nation=china is a proxy (flag rendering untested) | Hainan, Ningbo, JLSF | Backlog; test the vessel Nation override (it gates the JLSF hulls too). |
| Type 022; Kilo 636/636M; 094A context fit; 075/076 | China | none (037IIE proxy) / missing_fit / missing_fit / none | Ningbo, Longpo | Backlog. |
| KJ-200, Chinese UAVs, PLANAF Y-8Q livery | China | none / missing_fit | Lingshui | Backlog. |
| **Unmetered PLAN rounds** (no AmmoPoints and no SupplyCategory, following each round's file stack) | China | missing_fit: any supplier refills them free, including a Ro-Ro and the unlimited pier | All PLAN escorts and relief runs | Per pinned hull (China maritime final). 956E: plan_3m_80mbe, plan_hq16. 054A p3, 054 p2 and 052D p1: plan_yu-7c_ship. 054A p5: plan_hq-16c, plan_yu-7c_ship. 056A: plan_yu-7c_ship. 039B: plan_yu-6a (Default and Late loadouts), plan_yu-6 and plan_yu-9 (Early loadout). 039A: plan_yu-6, plan_yu-9. Song: pla_yj-18, pla_yu-6. Kilo: plan_yu-5, plan_yu-6. 052D p4: none carried. pla_hq-11 has no AmmoPoints but sits only in the AntiAirHeavy loadout, which AvailableLoadouts (:350) leaves out. 052D p3, 052D p4 and 055 carry no unpriced round. plan_hhq-9c (5,300), plan_yj-17 (10,100), plan_yj-18a (4,800) and plan_yj-20 (11,050) are priced through their 3789188689 `#!extend` stubs over the 3775128499 base, as plan_yj-18 (4,800) is, but have no SupplyCategory. plan_yj12_ship is not carried by these hulls. China support still lists these rounds as unrationed (C32). **Priced exception:** the Ningbo relief escort's 054A p3 SAM `plan_hq-16` is 1,700 AP with no category, so it is metered. Its Yu-8 (2,600) is refused by a 2,000-ceiling Ro-Ro. SEST pack: add AmmoPoints and SupplyCategory. Disclose until then. |
| Tu-22M3 / Tu-160M / An-12 / Tu-142MK-MZ | Russia | proxy (wp_tu-22m2) / proxy (wp_tu-160) / proxy (wp_il-76md) / none (Tu-142M only) | Olenya, Engels, Belaya | Labels; backlog. |
| wp_tu95ms and wp_tu-160 loadouts and behaviour | Russia | missing_fit (fit check) | Olenya, Engels, Ukrainka | wp_tu95ms declares Role=MPA,ASW on the Tu-142M mesh, so bomber tasking is a runtime test. Loadout whitelists: wp_tu95ms LandAttack or Default only; wp_tu-160 StrikeLongRangeKH101 or StrikeLongRange only, never StrikeNuclear, Default or Strike. The Engels Tu-160 markdown row and package note now carry this whitelist (final). |
| Russian civil fishing flag | Russia | missing_fit | Barents, Okhotsk | Mission-placed NeutralVessel entries with VariantReference: civ_fv_sterntrawler_a V1 and civ_fv_okean Default/V1, then mission Nation=russia / flag_civ_rus. Not campaign spawns (2.4). |
| Borei / strategic boats without a strategic weapon system | Russia, France, China | missing_fit (fr_ssbn_triomphant and plan_ssbn_type_094a have no context-only fit; wp_ssbn_borei carries a live system) | Russian bastions, Île Longue, Longpo | 0 placed (C17). A SEST inert patch only if ever needed. |
| French replenishment ship; named French Djibouti base; Floréal; Falcon 50M/2000; Puma / Fennec | France | none / none / none / none / proxy (fr_as_332M Sq2) | Djibouti FR | Cross-nation RAS is untested and an option only (C31); backlog. FREMM, NH90, ATL2, La Fayette, Mirage 2000-5F and Gazelle map exactly. |
| Italian replenishment; named Italian base | Italy | none | Djibouti IT | Backlog. |
| Stirling working port | Australia | missing_fit (ran_pt_boats_docks V2 is a marker only) | Stirling | SEST capped clone, Nation=Australia. |
| Hunter-class; AUKUS presence | Australia | none; unsourced | Stirling | Backlog. |
| NSA Bahrain / Muharraq / Jebel Ali units; Bahrain or UAE military; GCC merchant flags; LNG / modern container | Gulf | none / missing_fit / none / none (container hulls are period proxies) | Gulf and Horn nodes | Labelled markers; "container ship (period stand-in)" labels (civ_ms_mairangi_bay, civ_ms_act_1, civ_ms_encounter). |
| Civil freighter aircraft | civil | missing_fit (civ_il-76t/td, Soviet flag) | all | Backlog. |
| Hardened aircraft shelters | Russia | none | Engels | Not modelled. |
| Ship fuel; repair; supplier restocking | engine | not established (usaf_c-141b PlaneCargoSupplySystem, 1965–2006, is the only restocking candidate; untested) | world-wide | Finite relief hulls; probes and tests (5.4). |
| Laos nation key | – | none | Ban Keun | do_not_populate. |

**Backlog wording correction (register, to apply).** The source-register expansion_backlog line "DLA centres co-located with Norfolk, San Diego, Jacksonville and PSNS are implied but unnamed (R02:17)" should read: "R02:17 states co-location only generically; no DLA centre at Norfolk, San Diego, Jacksonville or PSNS is asserted or named." The rest of that line (17 CONUS centres claimed, 2 named; the seventh OCONUS hub unnamed) stands.

**Proposed backlog additions.** These come from inventory lookup hints or outside knowledge, not R01–R03, and are labelled as proposals: Point Loma, NAS Whidbey Island, NS Everett, Chabelley, RAAF Pearce / Learmonth / Curtin / Darwin, Mayport (Triton operations), and a UK home-base node for the Falklands air bridge.

---

## 4. Placement overview

**Placement status** uses the scope §5.1 categories: proven (pool), Natural Earth water, Natural Earth land pending P8, pier-side fallback, no stock terrain evidence. All positions are approximate public locations to be verified, not report data. All placement is pending validation, and nothing below has been placed or run.

| Node | Approx position | Existing in-game evidence | New asset a placement needs | Blockers / status |
|---|---|---|---|---|
| usp_coronado_nas_north_island | 32.7N 117.2W | Stock city point "San Diego" (~3 NM, coordinate only); KLAX ~96 NM; nearest proven sea 429 NM, land 3,298 NM | SEST named NAS clone, or usa_airbase V1 labelled | B1 fails (766 NM); needs the global land mask (B5) or an extract (B3); CustomAirGroup restore |
| usp_coronado_nab_coronado | 32.68N 117.16W | as above | optional FOB marker (Nation=usa) | as above; no LCAC/LCU |
| usp_sandiego_naval_base_san_diego | 32.7N 117.1W; SoCal box ~32N 119W | as above; nearest proven sea ~430 NM (Bell Systems Test centre 30.0, −125.0) | labelled scenery; optional capped port clone | B1; no Pacific sea network; CVN-71/72 links ±180 (P3a); separations ~8,350 / ~5,700 NM, beyond the played 3,450 |
| usp_kitsap_bremerton_psns | 47.6N 122.6W | KSEA/Seattle ~15 NM; nearest proven sea ~990 NM (installations lens; a different point from Bell Systems, which is ~1,060 NM away) | none (dormant hulls, labelled scenery) | Natural Earth land pending P8 (Hood Canal at Bangor; Sinclair Inlet untested); dormancy and save test |
| usa_norfolk_naval_station_norfolk | 36.95N 76.33W | KNGU 36.937, −76.289; Port Norfolk (hidden, Role=Civil) ~2 NM; Hampton Roads sea point ~5 NM; stock neutral waypoint ~13 NM; nearest placed sea ~206 NM, land ~1,689 NM | optional SEST NAS Norfolk clone | B1 (989 NM). us_ports_atlantic.ini is all-or-nothing: 12 entries, 11 besides Port Norfolk; 9 carry Movements=5 and civ_ destinations and may draw the RE-power supply freighters (untested). Whether LoadBackgroundData creates every entry is open (scope-and-performance.md:245). port_norfolk_scenery stays a ledger entry until probed. |
| usa_newport_news_shipbuilding (context) | 36.99N 76.44W | Port Norfolk node ~6 NM; Hampton Roads ~10 NM | none (CVN-74 is a ledger entry; inert hull optional) | Restore step if the hull is placed |
| usa_jacksonville_nas_jacksonville | 30.24N 81.68W | Port Jacksonville (hidden, Civil) ~6 NM; Mayport (LargeMilitary) ~16 NM; Jax Fairway sea point; nearest placed sea ~450 NM | usa_airbase V1 labelled or SEST clone | B1; Triton CHECK |
| wpac_yokosuka_naval_base | 35.29N 139.67E | Yokohama ~9 NM, Tokyo ~24 NM (world points only); proven land ~43 NM (user missions), sea ~206 NM (Sea of Japan side) | labelled scenery only | No proven water in Tokyo or Sagami Bay; the extract does not cover Japan; do not use the 60 NM snapper |
| wpac_guam_naval_base_apra_harbor | 13.44N 144.65E | airfield_small_1 ~9 NM (stock "All Your Guam Belong to Us"); sea ~186 NM (Showdown off Guam Blue 1985) | none; optional capped port | Apra inner harbour reads as Natural Earth land (P8); offshore anchorage fallback; P2 Blue site |
| wpac_guam_andersen_afb | 13.58N 144.93E | PGUA world data; stock airfield_small_1 "Andersen AFB" decodes to 13.592, 144.935 (~0.6 NM) under the game convention (§2.1) | none (stock precedent) | B-52H runway and turnaround test; Tindal exclusion (C8) |
| io_diego_garcia_nsf | 7.3S 72.4E | stock 04 Chagos Gambit airfield_small_1 "NSF Diego Garcia" decodes to −7.295, 72.387 (~1–2 NM); no world-data point | none; labels | Lagoon reads as Natural Earth water (P8 control); DG–Tindal 3,552 NM; heavy-bomber fit untested |
| med_rota_naval_station | 36.62N 6.33W | stock world port Rota (no LandUnit); Mare Nostrum '28 mission 02 nato_small_airbase decodes to 36.60, −6.26 (~4 NM); Gibraltar sea points | capped SEST port clone only if a functional pier is wanted (the pier is an option at 0) | Unlimited-pier decision; Med coast extract or land mask |
| med_sigonella_nas_sigonella | 37.4N 14.9E | Mare Nostrum '28 mission 08 nato_small_airbase decodes to 37.03N 14.87E under §2.1 (~22–23 NM S; do not reuse); tgt_fueltanks_large at Augusta ~16 NM | usa_airbase V1 labelled or SEST clone | Recompute in the editor |
| med_souda_bay_nsa | 35.5N 24.15E | stock Dangerous Straits 1985 airfield_small_1 (per-unit Nation=greece) decodes to 35.52N 24.15E (~1 NM) under §2.1 | airfield_small_1 V1 labelled | Facility-type CHECK; B1 (92 NM); editor confirmation |
| med_akrotiri_raf | 34.6N 33.0E | no precedent or world point; sea 89 NM, land 147 NM | nato_small_airbase (Nation=uk) labelled, or SEST clone | Land mask; Sovereign Base Area host label |
| eur_deveselu / eur_redzikowo (context) | 44.1N 24.4E / 54.5N 17.1E | nearest placements ~244 NM / air 32, land 50 NM | markers at 0 | Inland terrain untested |
| aus_stirling_hmas_stirling | 32.2S 115.7E | ran_pt_boats_docks_small at Fremantle −32.03, 115.739 (~13 NM; RADF showcase, per-unit Nation=argentina); inside the SEST coast extract; Cockburn Sound is a P8 control | SEST capped port clone, Nation=Australia | B1 (927 NM); \|z\| ~4,454 vs 4,529 proven |
| aus_tindal_raaf | 14.5S 132.4E | airbase_raaf_tindal at −14.521, 132.378 (SEST Southern Watch 05; ~0.1 NM) | none (reuse) | Engine-default stock (no FlightDeck_AmmoCapacity); C8 override |
| hn_evenes_air_station | 68.5N 16.7E | Ofotfjorden sea point ~3 NM; Port Narvik ~17 NM; proven land 26 NM, sea 36 NM | SEST Norway airbase clone; Norway F-35A squadron | No Norway extract; high-latitude geometry (B6, P7, P3b) |
| hn_kola_olenya_airbase | 68.15N 33.46E | named wp_airbase_1 "Olenya Airbase" (never placed here); one Kola precedent (Kill Kuznetsov, centre 69.25, 33.23, in 17 copies; partly stale ship ids); port_ussr_severomorsk ~57 NM; proven air 44 NM, land 69 NM | none | Runway fit for Tu-160/Tu-95MS; P3b at 69N; Kola Bay reads as Natural Earth land |
| chn_hainan_yulin_naval_base | ~18.2N 109.6E | stock PLAN 02 airfield_small_1 "Sanya Airbase", Nation=china, at 18.29, 109.43 (~11 NM WNW; original :506–517, NameOverride :38–39; the same block is at :475–486 in the NEW MISSIONS CLEAN user copy); wp_airbase_4 at 18.30, 109.72 (~9 NM NE, nearest land); nearest sea ~110 NM | optional capped port clone | Coast extract lacks Hainan; unlimited-pier decision; P2 Red site |
| chn_hainan_longpo_naval_base | 18.2N 109.7E | wp_airbase_4 ~6 NM (land proof only); sea ~108 NM | optional capped port clone | as Yulin |
| chn_hainan_lingshui_airbase | 18.5N 110.0E | pla_q-5 airborne ~5 NM (air only); land ~20 NM | SEST named Lingshui clone, or china_large_airbase V2 labelled | V2's group must be replaced |
| chn_zhejiang_ningbo_naval_base | 29.9N 121.7E | airfield_small_1 V3 at 28.54, 121.42 (~80–88 NM); Shanghai world port ~80 NM; sea ~200 NM | optional capped port clone | No proven point within 80 NM; extract or land mask |
| jpn_kanoya_air_base | 31.4N 130.85E | proven air 31 NM; land ~337 NM; Kagoshima world port ~19 NM | airfield_small_1 V5 labelled; SEST JMSDF clone; P-1 label route | Land mask; P-1 stand-ins held (label route) |
| jpn_atsugi_naf | 35.45N 139.45E | proven land 30 NM (thaad_tel), air ~142 NM; ~14 NM from Yokosuka | airfield_small_1 V5 labelled (usa_airbase only with the same group) | Host and access labelling (US-designated facility shared with the JMSDF; register CHECK); P-1 stand-ins held |
| jpn_okinawa_naha | 26.2N 127.65E | proven land 12 NM, sea 16 NM, air 9 NM; asia_ports [Naha] ~2 NM; Futenma ~7 NM and Kadena ~11 NM (US; not in this package) | airfield_small_1 V5 labelled | Platform CHECK (P-1 vs P-3C); P-3C date CHECK; shared airfield (JASDF, civil) CHECK |
| me_bahrain_nsa_bahrain | 26.2N 50.6E | OBBI ~4 NM (coordinate only); hidden Dammam port ~29 NM (bad nation); proven sea 86–90 NM, land 162–165 NM; mission centres Prime Chance, SEST 01/02 | FOB marker; ran_pt_boats_docks Default pier (conditional) | Pier check; B1 (90 NM); in-Gulf spurs need the land mask |
| me_bahrain_muharraq_airfield | 26.3N 50.6E | OBBI airports.ini (Civil, Nation=Bahrain) | nato_small_airbase, Nation=bahrain, labelled | Host-flag behaviour test; which-airfield CHECK |
| me_uae_jebel_ali_port | 25.0N 55.1E | Dubai city ~17 NM (bad nation); proven sea 43 NM | ran_pt_boats_docks Default labelled | Operator and status CHECK |
| hoa_djibouti_camp_lemonnier | 11.55N 43.15E | proven land/sea 62–68 NM; mod 3796349767 centres (13.17, 43.15); Bab El Mandeb sea point ~65 NM | nato_small_airbase labelled or SEST clone | Shared-runway editor check (US/FR/JP); land mask |
| hoa_djibouti_pla_support_base | 11.6N 43.05E | as Lemonnier | FOB marker (replaces nv_headquarters); stores scenery (generic names); pier conditional | Pier check |
| hoa_djibouti_fr_ba188_heron | 11.55N 43.16E / 11.6N 43.15E | as Lemonnier | nato_small_airbase (Nation=france); Default pier | Naming / split CHECK |
| hoa_djibouti_jp_base | 11.55N 43.14E | as Lemonnier | airfield_small_1 V5 labelled | Shared runway |
| hoa_djibouti_it_base | 11.5N 43.2E (low confidence) | as Lemonnier | warehouses_3 marker | Name and airfield CHECK |
| satl_falklands_raf_mount_pleasant | 51.8S 58.4W (P3b uses −51.823, −58.447) | 3491248180 "The Royal Navy" Mission 1: nato_small_airbase at Goose Green (~20 NM W), airfield_small_1 (per-unit argentina) at Stanley (~27 NM); no vanilla unit within 959 NM | interim is_airbase_akureyri V2 relabelled with an at-base-only group; target SEST airbase_us clone | B1 (2,965 NM); **\|z\| 5,629 beyond the played 4,529 (P1 Variant C)**; Falklands terrain unverified (P3b) |
| satl_falklands_mare_harbour | 51.9S 58.5W | "Falklands Testing" rn_ff_rothesay ~29 NM; Mission 1 merchants off Stanley ~30 NM | nv_pt_boats_docks (Nation=UK, labelled; effectively unlimited, so disclose it) or a ran_pt_boats_docks_small marker (missing_fit for resupply; relabel) | as Mount Pleasant; B2 accepts offshore points unvalidated |
| eur_brest_ile_longue (context; Brest approaches at sea) | Île Longue ~48.3N 4.5W (not placed); FREMM patrol box ~48.15–48.33N, 4.8–5.2W | Port Brest Fr ~5 NM; Ushant TSS links ~52–62 NM; no proven placement within 138 NM (sea) or 481 NM (land); B1 512 NM | none for the site | Mostly open water west of Crozon and south of the Molène archipelago. **CHECK:** the Les Pierres Noires reef and lighthouse (~48.31N 4.91W) lies inside the box, and Béniguet (~48.35N 4.88W) just north of it (outside knowledge, below the land mask's resolution). Keep waypoints clear and run fix_land_positions.py on every waypoint. B6 overstates east-west distance ×1.49 here. |
| rus_engels2_airbase | 51.48N 46.21E | wp_airbase_modern V1 "Engels airforce base"; nearest placement 726 NM | none | Inland terrain; possibly an off-map raid origin |
| rus_ukrainka_airbase | 51.17N 128.45E | UHKG ~465 NM; nearest 590 NM | labelled wp_airbase_modern Default | Inland; NSN |
| rus_belaya_airbase | 52.92N 103.58E | nearest 1,271 NM | labelled stand-in | Inland; likely off-map |

**Physical assets under nodes that are not themselves placed** (each owned once, as listed):
- **APF** (glob_us_afloat_prepositioning_fleet): asset:ausio:apf_loiter_1 (authored Indian Ocean loiter area, position pending) and apf_reserve_1 (dormant).
- **US sealift reserve** (reserve:us_sealift): asset:med:relief_sealift_1, dormant outside the region with a Gibraltar entry.
- **Newport News:** CVN-74, a ledger entry by default (optional inert hull ~36.99N 76.44W).
- **Wuxi JLSC:** wuxi-mob-roro-1 underway from the Yangtze approach (~31.0N 122.2E) to the Ningbo approaches (~29.9N 122.2E), escorted by ningbo_ffg_1 (C24); wuxi-mob-cargo-2 dormant.
- **Guilin JLSC:** guilin-mob-cargo-1 underway from the Qiongzhou approach (~20.1N 110.9E) to the Yulin anchorage, escorted by yulin_corvette_2 (C24); guilin-mob-roro-2 held ~20.0N 111.0E.
- **Île Longue (context):** Brest approaches FREMM ASW with its NH90, ATL2 (optional), 2 fishing vessels and 2 merchants. The SSBN force and site are abstract.
- **Russian naval context (sea-area record):**
  - Barents patrol area ~70.5–72.5N 33–40E: Yasen (transit to GIUK), Udaloy, Chilikin.
  - Okhotsk ~52–57N 145–150E: Kilo (V7–11 or Default), 20380, Chilikin (reserve).
  - Borei ×2 at 0 (C17).
  - Fishing groups.
- **Red Sea / Bab-el-Mandeb regional traffic** (Gulf/Horn record): 1 VLCC, 1 bulk carrier, 1 container ship (period stand-in), 2 dhows.

**Not placed:**
- 9 context_only nodes: Coronado umbrella, Kitsap umbrella, Bangor, Patuxent (optional marker 0), Newport News (ledger hull), Naples, Deveselu and Redzikowo (markers 0), Île Longue (the site; the approaches carry scenario units at sea).
- 21 abstract_logistics_only nodes.
- Ban Keun (do_not_populate).

**Regional footprints as stated by each package** (SCENARIO CHOICE; listed side by side, not summed into a capacity claim):
- **US Pacific:** 17 ships; 115 aircraft (113 without the AH-1W pair); 3 installation clusters plus 1 optional marker.
- **US Atlantic:** 12 hulls (CVN-74 a ledger entry; the reserve DDG and the Algol dormant); 43 aircraft plus 8 MH-60R in Flight IIA air groups; 2 airfield proxies plus a port ledger entry.
- **W/C Pacific:** 14 hulls; 37 aircraft (31 embarked, 6 at Andersen) plus 9 escort helicopters not yet counted; 1 airfield and 2 scenery clusters (1 optional).
- **Australia / IO / APF:**
  - placed: 11 ships and submarines, 5 land units, 9 aircraft in base groups and 2 embarked;
  - reserve, not placed: 2 B-2A, 2 B-52H, 1 Collins and 1 APF hull;
  - neutral: 5 merchants and 3 airliners.
- **Gulf and Horn:** 9 warships and auxiliaries; 14 military aircraft plus 7 embarked helicopters; 13 installation placements; finite neutral traffic.
- **Med / Europe:** 4 DDG with 8 MH-60R; 4 P-8A; 1 T-AKE; 2 Typhoon, 1 Voyager, 1 A400M and 1 SAR helicopter; 3 installation stand-ins; plus the dormant Algol in the world reserve.
- **China maritime:** 22 hulls; 8 land-based aircraft, plus the Fujian wing (count not set) and 9 escort helicopters not yet counted; 6 shore stand-ins.
- **China JLSF:** 4 mobilised hulls, 2 underway and 2 dormant.
- **Russia:**
  - bases: 21 aircraft (Olenya 11, Engels 4, Ukrainka 3, Belaya 3), plus an optional Il-78 at Olenya, an optional Il-78 at Belaya (0 by default) and an optional SAM site (0 by default);
  - naval context: 6 hulls (Borei at 0) and 5 fishing boats.
- **Japan / Norway:** Evenes 5 P-8A, 3 visitors and a 3-unit NASAMS proxy; Naha 4 P-3C; 7 P-1 stand-ins and 2 F-35A held; 3 JMSDF airfield proxies; 4 civilian pools.
- **South Atlantic / France:**
  - Mount Pleasant: 4 Typhoon, 1 Voyager, 1 A400M, 2 Rapier and 1 airliner;
  - Mare Harbour: HMS Forth, 1 charter, 1 Tide (dormant, optional) and 3 fishing vessels;
  - Brest approaches: 1 FREMM with NH90, 1 ATL2 (optional), 2 fishing vessels and 2 merchants.

### Scope implications (scope-and-performance.md §1–2, §4–5)

**What the evidence supports**
- The map centre is a datum, not a boundary. Units 3,900–12,000 NM from it load in stock content and in a game-written save (298 units, 6,444–8,781 NM out).
- With a candidate centre at 42N 20E, every anchor lies within 7,002 NM (Pearl Harbor) and \|x\| ≤ 10,677, inside what has already loaded, run and saved. **The exception is Mount Pleasant and Mare Harbour, at \|z\| 5,629** against 4,529 in the save.
- Absolute `GeoPosition=` placement exists (MFI:436–440). No SEST tool emits it yet (B12).
- The ±180 date line is the one recorded engine edge. It affects:
  - every Pearl Harbor link to the western Pacific;
  - US West Coast–WestPac carrier links;
  - Yokosuka–PSNS;
  - trans-Pacific civil airways.

**What the evidence does not support**
- Capacity is unmeasured. The largest played and saved mission is 298 units plus 634 aircraft. The regional footprints above must not be summed and presented as feasible until P0b/P4/P5 measure them.
- Whether an unobserved theatre keeps simulating, whether saves reload, and whether LoadBackgroundData creates every global entry (scope §4, item 12) are all unknown.

**Authorable now, whatever the probes show**
- Every record above as absolute lat/lon.
- Allocation and run state: active, dormant (Disabled=True plus trigger; vessel precedent Officer_Training_1.ini:88, :105–106), or roster-only.
- Air inventories split into parked (CustomAirGroup, ready-up tasks) and airborne.
- Per-field provenance.
- Link fields: great-circle distance, NSN flag, ±180 flag, and resupply capability (which needs SEST Replenishment).
- Placement-status flags.
- Route duration (routes must outlast the session, because aircraft orbit when their route ends).
- Idle radar posture.

Do not bake in a map centre, x/z values, a per-mission unit budget or a regional split.

**Decisions that wait on probes** (working default in brackets)

| Decision | Waits on | Affects |
|---|---|---|
| Single origin, or partition at distance D [one origin ~42N 20E] | P1 A/B/C | Mount Pleasant/Mare Harbour (\|z\| 5,629) and all separations above 3,450 NM: Norfolk–Stirling ~10,150, Yokosuka–Mount Pleasant ~9,541, San Diego–CVN-71 ~8,350, San Diego–CVN-72 ~5,700, Evenes–Naha ~4,381, DG–Tindal ~3,552. These are untested, not known limits. |
| Pacific east of 180 in the same mission [yes, links flagged] | P3a | Pearl DLA, US West Coast nodes ↔ Guam/Yokosuka, CVN-71/72 transits, Yokosuka–PSNS |
| Theatres active simultaneously [assume yes] | P2 (Guam vs Hainan, 2,057 NM) | Guam/Andersen and the Hainan cluster first |
| Active population size; use of dormancy [record run state; no cap] | P0b, P4, P5 | All regions |
| Persistence vehicle | P0a, P6, P6-L | Supplier CurrentAmmo, damage, trigger state |
| Distance metric | P7 | Builder routes at high latitude (Evenes, Olenya, Falklands) and at Brest (B6 ×1.49) |
| Water overrides | P8 (Hood Canal, Kola Bay, Apra inner; controls DG lagoon and Cockburn Sound); P3b (Falklands) | PSNS/Bangor, Olenya context, Apra, Mount Pleasant/Mare Harbour |

**Builder prerequisites (ours, not engine limits)**
- B10: own output root.
- B5 / B3: global land mask or extract. This removes B1's failures at San Diego, Norfolk, Pearl, Kitsap, Stirling, Brest, Mount Pleasant, Bahrain and Souda.
- B7: longitude wrap.
- B6: great-circle distance.
- B11: preflight path argument (preflight also checks only `[TaskforceNAircraftM]` / `[TaskforceNHelicopterM]`, so neutral aircraft loadouts are set by hand).
- B12: optional GeoPosition emission.

---

## 5. Register status and next checks

### 5.1 Counts
- **Register nodes: 69.**
  - Policies: populate 19, populate_small 19, context_only 9, abstract_logistics_only 21, do_not_populate 1.
  - Also 37 sea areas/routes and 26 backlog lines.
- **Packages: 70.** That is 69 node packages (every node now has a real package) plus the world-level `reserve:us_sealift`. Second-skeptic results were received for all 11 regions; Australia/IO had none open.
- **Force rows, recomputed by script from the final packages (identical to the corrected packages; the final pass changed no row count or outcome):**

| Region | Nodes | Rows | exact | proxy | missing_fit | none |
|---|---|---|---|---|---|---|
| US Pacific | 8 | 38 | 27 | 10 | 0 | 1 |
| US Atlantic / CONUS | 11 | 36 | 18 | 12 | 3 | 3 |
| W/C Pacific | 6 | 26 | 13 | 7 | 1 | 5 |
| Australia / IO / APF | 4 | 27 | 10 | 15 | 1 | 1 |
| Gulf and Horn | 9 | 44 | 24 | 19 | 0 | 1 |
| Med / Europe (+ US sealift reserve) | 9 (+1) | 32 | 17 | 11 | 1 | 3 |
| China maritime | 4 | 34 | 20 | 10 | 1 | 3 |
| China JLSF + Ban Keun | 7 | 11 | 0 | 4 | 0 | 7 |
| Russia (bases) | 4 | 21 | 13 | 8 | 0 | 0 |
| Japan / Norway | 4 | 30 | 13 | 14 | 2 | 1 |
| South Atlantic / France | 3 | 19 | 6 | 9 | 3 | 1 |
| **Total** | **69 (+1)** | **318** | **161** | **119** | **12** | **26** |

- **What changed since the previous count (275 rows):**
  - US Pacific +8 (`_flt` sub-assets);
  - Gulf/Horn +3 (airliners split into four);
  - Med/Europe +2;
  - Russia +1 (belaya_il78_opt);
  - Japan/Norway +10 (Atsugi complete, Naha added);
  - South Atlantic/France +19 (new packages).
- **Identity check on the rows.** All 318 asset ids are unique world-wide, and each row carries exactly one allocation. Physical-identity conflicts are on shared hull and variant pools, not on ids: see C1, C4, C5, C11, C13, C21, C22, C28–C29 and C33 (C24 is now applied).
- **Not counted in the table** (each still has one owner):
  - Traffic and context groups:
    - Australia 3 civil groups (DG and Stirling packages);
    - Horn 4 regional traffic rows (Red Sea / Bab-el-Mandeb record);
    - Russia 8 naval-context rows (2 Borei at 0) and 2 fishing groups (missing_fit), on the Russian sea-area record;
    - Japan/Norway 4 civilian pools (Evenes, Kanoya, Atsugi (one Tokyo Bay pool, C27), Naha);
    - unpinned routine-activity traffic proposals in US Pacific, US Atlantic, W/C Pacific and Kitsap (C29).
  - Embarked helicopters not yet carried as rows: 29 (C7), plus the Fujian wing.
  - Held, retired or withdrawn:
    - DDG-51 (held, unallocated);
    - asset:med:rota_ddg51 (retired id);
    - asset:usatl:p8a_jax_reserve (to retire, C10);
    - asset:chn:ningbo_relief_escort_1 / yulin_relief_escort_1 (withdrawn, C24).
- **Caveats:**
  - Rows are not units. At least 53 rows place nothing by default (abstract, quantity 0 or option rows). 9 more are held until a label route (7 P-1 stand-ins) or a fit (2 Evenes F-35A) exists.
  - Some rows mix outcomes. The CVN wings carry the MH-60S stand-in, and the LHD ACE carries an AH-1W (late) proxy.
  - C24 is applied: ningbo_ffg_1 and yulin_corvette_2 are escorts from t0 in the final China maritime package. Allocations change again when C10 is applied: the Jacksonville reserve is retired.

### 5.2 Validation state
- **Research:** three fidelity passes and two skeptic passes per region. Their fixes are applied in the final packages, apart from the region items in 5.4 and the items each file records as declined.
- **Unit ids:** 220 re-resolved on this branch (148 in force rows, 46 further unit ids and 26 ammunition ids; 2 known non-resolving ids, unused). Variant names and dates were re-read from the winning files for every pool in 1.5.
- **Untested everywhere:** placement, routes, transfers, turnaround, ready-up loadouts, runtime activation and save/load.

**Open cross-cutting wording fixes**
- plan:11 says the *plan itself* asserts no new asset counts. It is not about the register. plan:65 is the report-size rule.
- The register's DLA expansion_backlog line (section 3).
- "Register role" is editorial: quote the register's populate_reason verbatim and keep it out of SOURCE blocks. For example, Yokosuka's is "Main US forward naval base in the Western Pacific, with a named forward-deployed carrier. CSG escorts are not named, so any escort composition is authored." Keeping the Seventh Fleet HQ command role abstract is a SCENARIO CHOICE.
- Quote R03:172 in full: "effectively neutralize the combat effectiveness of the forward-deployed forces by starving them of fuel and munitions".
- Stand-in labels apply only where a real name would otherwise show (1.1). Never say "every proxy shows a label" where generic names or unconfirmed T-AKE/T-AO labels remain.

### 5.3 Most important CHECK items
1. **Dated carrier statuses (R03:48–62).**
   - CVN-68: pre-decommissioning (R03:54); inactivation and a move to Norfolk reported around 2026; unit ServiceDate 2025–2027.
   - CVN-69: FRS CQ (R03:55) vs reported maintenance; unit V2 ServiceDate 2025–2030.
   - CVN-70: TSTA/FEP (R03:56) vs a reported 2025 deployment.
   - CVN-71: CENTCOM transit (R03:57), apparently 2024.
   - CVN-72: WestPac (R03:58).
   - CVN-73: "currently" (R03:38/59) is undated.
   - CVN-74: RCOH (R03:60), reported extended.
   - CVN-75: UNITAS / work-ups (R03:61) vs the collection's "No CVW RCOH" annotation.
   - CVN-76: drydock (R03:62).
   - Also the berth question (R03:27 vs R03:50/56–58).
2. **A scenario date must be fixed first.** Date-gated choices:
   - CVN-68 V1 (to 2027) and CVN-69 V2 (to 2030);
   - `_2027` (2027 onward; not used);
   - CG V1 (ends 2027);
   - `_091_late` V1/3/5 and `_097_late` V1;
   - f3_125 V2 onward;
   - LCS V8 and the PPA V5 (2026 onward);
   - usmc_ah-1w_late Default squadron (2003–2010);
   - **usn_p-3c Japan squadrons, which inherit [Default] 1977–1995** (Naha exact P-3C, Djibouti, every P-1 stand-in);
   - civ_ms_c7s68 (ends 2019);
   - C-141B (1965–2006);
   - Algol V2/4/5/8;
   - Kilauea;
   - US_Los_Alamos (1961–1991);
   - es_ss_galerna (only V1 to 2026).
3. **Lingshui assignments (R01:31, R03:101).** No units, numbers or dates are given; the service is not stated; Y-8Q vs Y-8FQ; R03:133 is type-level only.
4. **French Djibouti naming (R01:51).** R01 equates Base Aérienne 188 with the Héron naval base; a split is possible (backlog).
5. **DLA scope.**
   - 17 CONUS centres claimed, 2 named (R02:15).
   - Seven OCONUS hubs claimed vs six named (R02:21 vs R02:23); DG in the R02:33 table is not a DLA centre.
   - R02:17 co-location is generic.
   - "Managed primarily" (R01:21, R02:11) likely overstates DLA's role.
   - The Richmond name may be dated.
6. **JLSF "Arm" 2024 (R02:38, R01:35).** Terminology priority check; Central-theatre overlap (Wuhan R02:54, Zhengzhou R02:59). Per-unit vessel Nation for the mobilised hulls is unproven.
7. **Triton site.** R01:17, R03:23 and R03:31 place the MQ-4C at NAS Jacksonville; it is commonly reported as flying from NAS Mayport (outside knowledge). No US Triton squadron exists in the collection, and the Tindal "Det" squadron is SEST-authored, not sourced.
8. **Olenya counts (R03:72).** "Up to 35 Tu-22M3, 10 Tu-95MS, several Tu-160, An-12" is a 2024–25 imagery snapshot and may reflect dispersal; the scenario uses 6/2/1/1. Related:
   - the 40th CAR designation;
   - the R03:74 drone-mechanism wording;
   - Belaya's "up to 42" is historical;
   - Engels Tu-95MS losses are uncounted.
9. **Labels and fits to confirm in the editor:**
   - T-AKE/T-AO named-variant labels;
   - mixed-nation visitors at Evenes;
   - vessel Nation override (JLSF hulls, Russian fishing);
   - FlightDeck_ReadyUpTask loadouts on placed bases;
   - wp_tu95ms bomber tasking.
10. **Also check:**
    - resident squadrons (seed:23) at North Island, Jax, Sigonella, Akrotiri and Mount Pleasant;
    - Tranche 1 Typhoon retirement;
    - HMS Forth "since 2020";
    - Sky Sabre and NASAMS III;
    - Naha P-1 vs P-3C;
    - Atsugi host labelling and the 3rd Squadron's wing;
    - Evenes vs GIUK geography;
    - Redzikowo operational date;
    - Chagos 2025 sovereignty wording;
    - Rota hull count (C3);
    - which Kitsap component bases the SSBNs;
    - Iroise box reefs (Les Pierres Noires, Béniguet);
    - the Ban Keun claim (do_not_populate).

### 5.4 Ordered next steps
1. **Apply the integration resolutions to the regional packages.** Each item names its C entry or second-check source.

| Region | To apply |
|---|---|
| US Pacific | Squadron pins for the Vinson, Roosevelt and Lincoln wings and every HSM pick, from the C6 ledger. (Applied in the final package: the row 42 basis, the San Diego traffic tanker V2, the C30 `_flt` allocations, the line 320 and package-check C1 wording, and the plan:11 paraphrase.) |
| US Atlantic | Pins: esc_1 DDG-107 (`_099_late` V8); esc_2 DDG-81 (`_081_late` V1); vacapes_patrol DDG-85 (`_085_late` V1); norfolk_reserve DDG-100 (`_100_late` V1); planeguard DDG-54 and norfolk_ready DDG-56 (`_054_late` V1/V2); takr_norfolk_relief Algol V1; take_truman Default with a unique NameOverride. 8 MH-60R as `_flt` rows (C7). Retire p8a_jax_reserve (C10). Squadron pins for the Truman wing and the NAS Norfolk E-2D pair (C6). Routine-activity line (markdown line 165 and the Norfolk package routine_activity): RE-power freighters carry "live supply blocks of 4.92–12 million points with no ceiling", not "unlimited supply blocks" (declined as out of scope in the final pass). (Applied: the DLA backlog flag and the Norfolk LoadBackgroundData CHECK.) |
| W/C Pacific | Pins: CG-64 V2; DDG-105 V6; DDG-89 (`_089_late` V1); DDG-92 (`_091_late` V2); DDG-58 (`_054_late` V3); T-AKE 6 V3; T-AO 189 V2; guam_take Default with a unique label; SSN-778 and SSN-753 V1; LCS-27 V6; Algol Denebola V3 (drop V6); guam_taot_arrival Sealift V1, labelled. 9 escort MH-60R as `_flt` rows (C7). Connection to usp_kitsap_bremerton_psns (row 42): basis "source (role); node mapping authored", matching US Pacific. Tokyo Bay traffic references asset:mpn:atsugi_civ_pool (C27). (Applied: the Yokosuka REGISTER line and register_role, the Andersen R03:172 quote and the stand-in labels bullet.) |
| Australia / IO / APF | Unique Default labels for dg_mps_1/2 and apf_loiter_1 / apf_reserve_1 (C28). |
| Gulf and Horn | Pins: me:ddg_1 DDG-106 V7; me:lcs_1 LCS-29 V7; me:tao_1 T-AO 193 V3; me:take_1 Default with a unique label; hoa:plan_ddg_1 052D p3 V10; plan_ffg_1 054A p5 V2; plan_aor_1 903A V3; jp_p3c_1/2 Squadron22 (or 24, 26–29). (Applied in the final package: the Italian Red Sea / Gulf of Aden split, the PLA stores label exception and the C31 option sentence.) |
| Med / Europe | None open. DDG-117 round compatibility and the take_1 label note are applied in the final package. |
| China maritime | 9 escort helicopters as `_flt` rows, and an explicit Fujian CustomAirGroup count (C7). Name the Yulin release-escort source (C33). (Applied in the final package: the C24 hand-over and release-escort rule, the per-hull metering lists, the Dazhou guard, the Yulin user-copy range and the R03:105/R03:107 citation.) |
| China support | Align the unrationed list (markdown lines 62–71, Wuxi support_services[3] and checks[7]) with the C32 decision. (Applied: C14/C24, the hand-over wording "recorded in china-maritime", and the stale escort text.) |
| Russia | None open. The Barents fishing route, the Engels Tu-160 whitelist and the scope paragraph are applied in the final package. |
| Japan / Norway | Drop the JMSDF escorts and Mashuu AOE reference from the Atsugi–Yokosuka connection (markdown line 351 and the package connection) (C26). The Djibouti link is context only (C25): replace "if the Djibouti package authors a JMSDF MPA detachment, take it from this allocation" (markdown line 352), the package connection "optional source of a JMSDF MPA detachment (subtract from this allocation)" and the matching sentence in the atsugi_p1_4 notes. (Applied in the final package: label-route limits, RC-135 operator wording, the Naha usn_p-3c ServiceDate CHECK and the ready-up rows.) |
| South Atlantic / France | None open. The Mare Harbour `scale` field and the Iroise box CHECK are applied in the final package. |

2. **Fix the scenario date**, then run a date-gate pass on every pinned variant and squadron (5.3 item 2).
3. **Builder prerequisites:** B10, B5/B3, B7, B6 and B11; B12 is optional.
4. **Pass C placement packages by region, in order of readiness:**
   - (a) proven anchors: Guam/Andersen, Diego Garcia, Tindal/Stirling, the Hainan cluster, Djibouti, the Gulf, Rota/Souda/Sigonella, Olenya/Evenes, Naha;
   - (b) land mask or extract needed: the US West and East Coasts, Yokosuka/Atsugi/Kanoya, Ningbo, Akrotiri, the Brest approaches;
   - (c) probe-gated: the Falklands (P3b, P1 Variant C), east of 180 and Pearl (P3a), and Kitsap / Apra inner / Kola Bay (P8).
5. **Probes in scope order:** P0a and P0b, then P1 and P3a, then P3b and P2, then P6, then P4 and P5, then P7 and P8. Each is to be written as an opt-in file under docs/world-sandbox/probes/ (not yet written) and never deployed.
6. **Support wiring (Pass D), each tested on its own:**
   - Ship ammunition with finite SEST suppliers (T-AKE / T-AO / T-AOE / Algol / Tide / 903A / 901 / ran_aor_supply / C8 Default). Include the category gates, the uncategorised and unmetered rounds (rim-66m-5; the PLAN list) and the negative cases (a 2,000-ceiling supplier refusing Yu-8, Tomahawk and SM-6).
   - Aircraft turnaround and ready-up tasks on FlightDeck-stocked bases vs engine-default bases (Tindal, wp_airbase_modern, airbase_us clones).
   - Supplier restocking: the C-141B candidate, otherwise finite relief hulls.
   - The unlimited-pier decision, then the capped SEST port clone.
   - The declared AAR pairs.
   - Vessel dormancy wake at the pier (precedent Officer_Training_1.ini:88, :105–106).
   - Hold and neutral behaviour (Djibouti cluster; Russian patrols vs Evenes QRA; mixed-nation visitors).
   - A weapons-hold test before any strategic submarine is placed.
   - Save/load of supplier CurrentAmmo.
7. **SEST pack work list**, from section 3:
   - named base clones (NAS, UK, Norway, JMSDF, Lingshui);
   - capped port clones;
   - squadron packs: Norway F-35A, US MQ-4C, MH-60S, CMV-22B, 1435 Flight, and the labelled JMSDF P-1 stand-in squadrons;
   - PLAN round metering;
   - P-1 content.
