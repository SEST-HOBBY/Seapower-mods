<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## US Atlantic, specialist support and CONUS depots

**Region summary.**
- **Policies.** 11 nodes.
  - Populated: NS Norfolk and NAS Jacksonville.
  - Context-only: NAS Patuxent River, and Newport News Shipbuilding, which holds one carrier that is out of service (per the region note).
  - Abstract logistics only: NAS Whiting Field, the DLA network, DLA Susquehanna, DSC Richmond and the Anniston, Red River and Tobyhanna depots.
- **Scenario totals at start (all SCENARIO CHOICE).**
  - 12 hulls: 3 CVNs (one in RCOH, unavailable), 6 DDGs, 1 T-AOE stand-in, 1 T-AKE stand-in and 1 Algol T-AKR.
  - 43 aircraft: 30 embarked on carriers, 6 at NAS Norfolk and 7 at NAS Jacksonville.
  - Plus 8 MH-60R carried by the four Flight IIA hulls' own air groups.
  - SOURCE CLAIM for comparison: Norfolk 'over 75 ships and 134 aircraft' (R03:19, R01:15). That is a base total, not an instruction to place them.
- **Carrier ledger.** Each R03 table hull appears once in the world:
  - CVN-69 Eisenhower: training, carrier qualifications (CQ) in the Virginia Capes operating area.
  - CVN-75 Truman: underway in the western Atlantic.
  - CVN-74 Stennis: in servicing at Newport News, flagged CHECK.
  - No other region may allocate these three hulls.
  - Contingency (SCENARIO CHOICE, pre-stated in the Norfolk package): if Truman is in RCOH at the scenario date, it moves to servicing at Newport News, its air wing is left unallocated, and no carrier leads the underway Atlantic group. No hull is duplicated.
- **Engine facts that shape this region.** Collection inventory, with verify corrections applied:
  - No Nation=US shore unit can resupply ships. The vanilla East Coast ports are hidden from the Mission Editor, carry no supply system and reach a mission only through [BackgroundData] (untested for a sandbox). [BackgroundData] references a whole port file, with no per-entry selection: us_ports_atlantic.ini carries 12 entries (see the Norfolk CHECK).
  - Ship supply is ammunition only. No ship fuel is modelled, and supplier pools are never restocked.
  - A carrier cannot rearm its FlightDeck_ magazine at sea.
  - The SEST T-AO, T-AKE and T-AOE units are proxies: donor meshes with '(stand-in)' display names. Their transfers are still untested in game (integration/replenishment/README.md checklist item 5).
- **Placement.** Every position below is approximate and must be verified; placement is pending validation.
  - No mission has placed a unit within 60 NM of any node here. The nearest sea placement to Norfolk is about 206-211 NM away (Workshop 3766210676 Saronic Corsair tests, centre 34.0N 74.0W).
  - The builder's pool snapping fails here, so validation needs global_land_mask or a new coast extract.
  - Stock world data does have Atlantic nodes: KNGU, Port Norfolk, Port Jacksonville, Mayport, and the Chesapeake, Hampton Roads, Cape Hatteras and Jacksonville Fairway sea points.
  - The map centre is only a datum. If one mission spans Norfolk and the Indo-Pacific, the separation (Norfolk-Stirling about 10,150 NM) exceeds anything played and saved (3,450 NM). That is untested, not a known limit.

---

### usa_norfolk_naval_station_norfolk - Naval Station Norfolk

**Identity.**
- Operator: United States Navy. Host: United States (Virginia).
- node_kind naval_base; populate_policy **populate**.
- Sources: R01:15; R02:17; R03:19, 28, 48, 55, 60, 61.

**SOURCE CLAIM (role).**
- Largest naval base in the world by operational concentration and fleet density; 4,000-6,000 acres; 11 miles of pier and wharf (R03:19). R01:15 repeats only the 'largest naval base ... by operational concentration and fleet density' phrase and the '75 ships / 134 aircraft / 11 hangars' phrase; it gives no acreage, pier length or Fleet Forces HQ. Repetition is not corroboration.
- HQ of Fleet Forces Command (R03:19, R03:28).
- Primary force-generation hub for the Atlantic, Mediterranean and Middle Eastern theatres (R03:19).
- Hosts resident nuclear carriers and escorting destroyer squadrons; no counts given (R03:19).
- 'Over 75 ships and 134 aircraft across 11 hangars' (R03:19, R01:15); the table says 'Up to 75 surface ships, 134 aircraft' (R03:28).
- Eisenhower and Truman stage from Norfolk, with CQ off the Virginia Capes and in the Jacksonville operating areas (R03:48).
- Carrier table rows:
  - CVN 69: home port Norfolk, 'Fleet Replacement Squadron CQ' (R03:55).
  - CVN 74: home port Norfolk, 'RCOH', inactive (R03:60).
  - CVN 75: home port Norfolk, 'UNITAS Exercises / Workups', Atlantic / South America (R03:61).
- R02:17 names Norfolk as one of four sites into which 'major logistical operations are integrated'. Many DLA centres are said to be co-located with such bases, but no centre is named for Norfolk.

**CHECK.**
- Carrier statuses are undated report claims (seed:23). Check each at the scenario date:
  - Eisenhower was reported in maintenance after its 2023-24 deployment.
  - Truman deployed in 2024-25 and was reported as next due for RCOH. The collection's own winning variants file also annotates it: mods-source/3390330875/vessels/usn_cvn_nimitz_2025_variants.ini has '[Variant8] #CVN-75 Harry S Truman CVW-1 (AB) "Real World No CVW RCOH"' (and the same annotation on Variant7, CVN-74). The R03:61 'UNITAS Exercises / Workups' status may therefore be stale at the scenario date. The SOURCE CLAIM above is kept as written; the doubt comes from the collection itself, not only from outside reports.
  - Stennis's RCOH was reported extended to about 2026 or later.
- SCENARIO CHOICE (contingency, pre-stated): if Truman is in RCOH at the scenario date:
  - asset:usatl:cvn75_truman moves to servicing_maintenance at Newport News, under the same rules as CVN-74 (ledger entry by default, inert hull optional).
  - asset:usatl:cvn75_airwing is left unallocated: 22 aircraft drop out of the region totals, and no other carrier takes them.
  - No carrier leads the underway Atlantic group. CVN-69 stays in training_test (R03:55 'FRS CQ') and is not promoted; CVN-74 stays in RCOH.
  - The two Truman escorts and the T-AKE keep their asset ids. They either sail as a carrier-less surface group on the same southbound route, or return to Norfolk as resident_at_base. Either way each is allocated once.
  - No hull is duplicated, and no second CVN-75 appears anywhere in the world.
- Stennis: the R03:60 table lists home port Norfolk, while R03:50 places the RCOH 'at facilities like Newport News Shipbuilding', an example rather than an assertion. Allocated to servicing at Newport News; see that package.
- Fidelity fixes applied:
  - Newport News is removed from parent_or_colocated; only the hedged relationship remains.
  - The DLA wording is limited to what R02:17 says.
  - The R02:17 closing sentence ('these CONUS hubs represent the ultimate source of replacement airframes, deep-level maintenance components and bulk munitions') is applied as context only, and only to the nodes in this region that R02:15-17 names: Norfolk, Jacksonville, Susquehanna, Richmond, Anniston, Red River and Tobyhanna (plus the DLA network itself). It does not apply to Patuxent River, Whiting Field or Newport News, which R02 does not mention.
- Counts conflict internally: 'over 75 ships' (R03:19) against 'Up to 75 surface ships' (R03:28). Neither names classes or squadrons, and both are time-sensitive.
- port_eastcoast_norfolk is downgraded to proxy:
  - It is the commercial port (Role=Civil in us_ports_atlantic.ini), about 2 NM south of the naval piers.
  - It is HideIn=MissionEditor, has no SupplySystem and is misspelt 'Norflok'.
- Loading port_eastcoast_norfolk through [BackgroundData] means loading all of us_ports_atlantic.ini (only copy: vanilla campaigns/us_ports_atlantic.ini). That file has 12 entries, so it brings 11 others besides Port Norfolk:
  - Five with port units: Halifax (Canada, Civil), Charleston (Civil), Port Jacksonville (Civil), Mayport (LargeMilitary) and Newport (LargeMilitary).
  - Six location-only entries: Boston, Saint John (Canada), New York, New London (LargeMilitary), Philadelphia (LargeMilitary) and Baltimore (LargeCivil).
  - Four are Role=LargeMilitary (New London, Philadelphia, Mayport, Newport). None of the 11 is a research node or named in R01-R03; label them scenery, not research nodes.
  - Nine entries, Port Norfolk included, carry Movements=5 and Destinations={..., civ_} to 13 foreign ports. These may spawn engine civil traffic from the generic civ_ pool. That pool includes the RE-power freighters this package avoids (civ_ms_freighter_a/b, civ_ms_super_p: live supply blocks of 4.92-12 million points, no ceiling). Untested.
  - Whether LoadBackgroundData creates every entry is still open (scope-and-performance.md:245).
  - SCENARIO CHOICE: keep asset:usatl:port_norfolk_scenery as a ledger entry until a probe shows what the file spawns.
- Carrier-aviation types, outcomes per the corrected inventory (none allocated here):
  - MQ-25: proxy, usn_ka-3b labelled 'MQ-25 stand-in (KA-3B)'. Squadrons are date-gated 1956|1991. Not allocated.
  - CMV-22B: missing_fit, usmc_mv-22b (USMC VMM/VMMT liveries only; no Navy VRM livery).
  - C-2A: none.
  - MH-60S: missing_fit, usn_hh-60 or usn_sh-60f as a labelled stand-in. MH-60R is used instead as a SCENARIO CHOICE.
- Carrier air groups: no shipped variant wing on usn_cvn_nimitz_2025 is usable, so a mission CustomAirGroup is mandatory.
  - usn_mh-60r_26 and usn_mh-60r_2027 do not resolve.
  - An editor round-trip drops empty CustomAirGroup lines and turns Hold/Tight into Free (restore_roe.py exists).
- E-2D squadron liveries are offset from their names: each squadron is painted as a different squadron.
- usn_takr_algol: use only Variant1, 3, 6 or 7 (Algol, Denebola, Regulus, Capella). The other variants' ServiceDates end in 2025.
- MH-60R model and FLIR depend on mod 3590477166.
- Choosing a destroyer's hull variant implies a real ship. Assign each hull once in the world ledger; no real home port is asserted.

**Position.** Approx, verify.
- NS piers about 36.95N 76.33W; NAS Norfolk (Chambers Field) about 36.94N 76.29W.
- In-game evidence:
  - Stock world data: KNGU 'NAS Norfolk' 36.937,-76.289 (Role=LargeMilitary) and Port Norfolk 36.9226,-76.3429 (Role=Civil).
  - Stock sea points: Hampton Roads 37.01,-76.24 (about 5 NM away), Chesapeake Fairway 1-3 and Cape Hatteras 35.15,-75.28.
  - A stock neutral waypoint reaches 37.09N 76.12W, about 13 NM away (UnderCoverOfTheRain.ini:503).
- Nearest unit placed by any mission: sea about 206 NM, land about 1,689 NM.

**Forces.** Quantities are SCENARIO CHOICE. Source basis is shown separately.

| Allocation | Asset id | Role | Unit id (outcome) | Qty | Source basis |
|---|---|---|---|---|---|
| training_test | asset:usatl:cvn69_eisenhower | FRS carrier qualifications in the Virginia Capes operating area, about 36.6N 74.9W | usn_cvn_nimitz_2025 Variant2 'CVN-69 Dwight D. Eisenhower' (exact hull) | 1 | R03:48, R03:55. Location and timing are scenario |
| training_test | asset:usatl:cvn69_cq_det | Embarked CQ detachment | usn_fa_18f_rsa Squadron6 (VFA-106 FRS) x6; usn_mh-60r (HSM index set at build) x2 (exact) | 8 | R03:55 says only 'FRS CQ'. Squadron and counts are scenario. MH-60S plane-guard type is missing_fit |
| escort | asset:usatl:ddg_vacapes_planeguard | Plane guard for CVN-69 | usn_ddg_burke_f1_054_late (exact; hull set in ledger) | 1 | R03:19 escort family only |
| underway_deployed | asset:usatl:cvn75_truman | Workups, southbound in the western Atlantic toward South America (UNITAS); start about 33.5N 74.0W | usn_cvn_nimitz_2025 Variant8 'CVN-75 Harry S. Truman' (exact hull) | 1 | R03:48, R03:61. Status CHECK: the collection annotates CVN-75 as in RCOH; see the contingency above |
| underway_deployed | asset:usatl:cvn75_airwing | Reduced workups air wing (CustomAirGroup) | usn_fa_18e_rsa (Sq1-17) x10, usn_fa_18f_rsa x4, usn_ea-18g_2020 x2, usn_e-2d x2, usn_mh-60r x4 (exact) | 22 | No air wing is named by R01-R03. All scenario |
| escort | asset:usatl:ddg_truman_esc_1 | CVN-75 escort | usn_ddg_burke_f2a_099_late (exact; MH-60R x2 in hull air group) | 1 | R03:19 family |
| escort | asset:usatl:ddg_truman_esc_2 | CVN-75 escort | usn_ddg_burke_f2a_099_late (exact) | 1 | R03:19 family |
| support | asset:usatl:take_truman | Ammunition supplier with the CVN-75 group | usn_take_lewis_clark Default '(stand-in)' (proxy) | 1 | None (scenario) |
| patrol | asset:usatl:ddg_vacapes_patrol | Patrol of the Chesapeake Fairway and Virginia Capes | usn_ddg_burke_f2a_099_late (exact) | 1 | R03:19 family |
| resident_at_base | asset:usatl:ddg_norfolk_ready | Ready destroyer alongside | usn_ddg_burke_f1_054_late (exact) | 1 | R03:19 family |
| reserve | asset:usatl:ddg_norfolk_reserve | Finite reserve; trigger-activated (Disabled=True, then Action_SetEnabledStatus) | usn_ddg_burke_f2a_099_late (exact) | 1 | R03:19 family |
| support | asset:usatl:taoe_norfolk | Ammunition supplier at the pier for returning ships | usn_taoe_supply Default '(stand-in)' (proxy) | 1 | None (scenario) |
| reserve | asset:usatl:takr_norfolk_relief | Finite relief and sealift with a slow ammunition pass | usn_takr_algol Variant1/3/6/7 (exact class) | 1 | None (scenario) |
| resident_at_base | asset:usatl:nas_norfolk_field | NAS Norfolk airfield | usa_airbase Variant1 'Naval Air Station' + NameOverride (proxy). Alternative: a new SEST named clone on the raaf-bases pattern (new id, not existing) | 1 | R03:19 '134 aircraft' (no types); KNGU |
| resident_at_base | asset:usatl:nas_norfolk_helo | Helicopter detachment ashore | usn_mh-60r (exact) | 4 | None (no Norfolk aircraft types in the reports) |
| resident_at_base | asset:usatl:nas_norfolk_aew | AEW detachment ashore | usn_e-2d (exact) | 2 | None (scenario) |
| abstract | asset:usatl:port_norfolk_scenery | Port scenery only; ledger entry until a probe shows what us_ports_atlantic.ini spawns | port_eastcoast_norfolk (proxy: civil, hidden, BackgroundData; the file also brings 11 other entries) | 1 (ledger entry by default) | R03:19 identity |
| abstract | asset:usatl:usff_hq | Fleet Forces Command HQ | none (abstract command node) | - | R03:19, R03:28 |

asset:usatl:cvn74_stennis is **not** at Norfolk. It is allocated once, under Newport News.

**Support services.**
- **Ship ammunition.**
  - usn_taoe_supply (alongside): [SupplySystem1] TruckSupplySystem, pool 700,000, no ceiling, 1.0 nm, 130 pts/s, 2 targets, own speed up to 13 kn and receiver up to 16 kn, Vessel and Submarine targets. Categories: Harpoon 40, AirTorpedo 60, ALWT 32, SEST_LandAttack 40, SEST_LongRangeSAM 48.
  - usn_take_lewis_clark (with Truman): pool 550,000, no ceiling. Categories: Harpoon 48, AirTorpedo 72, ALWT 40, SEST_LandAttack 48, SEST_LongRangeSAM 56.
  - usn_takr_algol (reserve): pool 500,000, 0.5 nm, 45 pts/s, own speed up to 8 kn and receiver up to 12 kn. Categories: Harpoon 40, AirTorpedo 48, ALWT 24, SEST_LandAttack 32, SEST_LongRangeSAM 32.
  - The port itself supplies nothing.
  - The SEST clones have not been tested in game.
- **Aircraft turnaround and ordnance.**
  - Carriers: FlightDeck_AmmoCapacity 1,200,000 (Phoenix 84, Harpoon 48, AirTorpedo 80, AdvancedARM 64). It cannot be topped up at sea.
  - usa_airbase: 2,000,000 (AirTorpedo 72, Ovod 144, Harpoon 144). A SEST airbase_us clone would have no FlightDeck_AmmoCapacity, so its stock would be the engine default.
- **Supplier restocking:** not established. Pools deplete, and no port restocks a supplier. The reserve Algol is the only finite relief.
- **Fuel:** not established. No vessel fuel is modelled and no tanker is allocated.
- **Repair:** not established. There is no shipyard function.
- **Command and DLA integration:** abstract.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usa_newport_news_shipbuilding | RCOH example facility for a carrier with Norfolk as home port | source (hedged) | R03:50, R03:60 |
| usg_dla_distribution_network | Major logistical operations integrated; no DLA centre asserted | source | R02:17 |
| Virginia Capes operating area | CQ area | source | R03:48 |
| Jacksonville operating areas | CQ area | source | R03:48 |
| Atlantic / South America | Truman operating focus | source | R03:61 |
| usa_dla_susquehanna | East Coast resupply origin | authored | R02:29 for the hub role only |
| usa_jacksonville_nas_jacksonville | P-8A ASW cover for departures | authored | - |
| med_rota_naval_station | Transit gateway for Mediterranean deployments | authored | R03:19, R03:44 (theatre roles) |
| me_bahrain_nsa_bahrain | Middle East deployment destination | authored | R03:48 (theatre only) |

**Routine activity.** Proposed, not implemented.
- CVN-69 flies CQ racetracks in the Virginia Capes operating area with its plane guard, then returns to Norfolk.
- The CVN-75 group transits south by Cape Hatteras toward the Windward or Mona Passage sea points, with a RAS rendezvous with the T-AKE.
- A DDG patrols a loop between Chesapeake Fairway 1 and Cape Hatteras.
- Arrivals and departures run Hampton Roads to Chesapeake Fairway; returning ships rearm from the T-AOE.
- The reserve DDG and the Algol are activated by trigger only.
- Helicopters fly local SAR and ASW sorties.
- **Civil traffic** (scenario, no supply blocks):
  - Ships: civ_ms_mairangi_bay (US variants), civ_ms_bulk (Liberia/Greece), civ_ms_car_carrier_a (Panama/Liberia), civ_ms_ritina (US/Liberia), civ_ms_c7s68 (US; Default ServiceDate 1968-2019, check date filtering), civ_fv_fishingboat_a and civ_fv_crabboat.
  - civ_fv_fishingboat_a must be pinned to VariantReference=Variant3, which displays 'Fishing boat US', or given a NameOverride. Its display names come from 3432592449 language_en/vessel_names.ini (Variant1 USSR, Variant2 Iceland, Variant3 US, Variant4 Japan, Variant5 China); every variant flag is Nation=US. A random variant off the Virginia Capes could show a Soviet- or Chinese-labelled boat.
  - Aircraft: civ_a320 (US Squadron14 etc.), civ_a330 (US Squadron25 etc.), civ_c340 and civ_h700.
  - Avoid RE-power freighters such as civ_ms_freighter_a and civ_ms_super_p, which carry very large supply pools (4.92-12 million points, no MaxAmmoPoints ceiling; mods-source/3605013271).

**Validation.**
- Research: report claims only.
- Mapping: hulls exact; auxiliaries, port and airfield are proxies.
- Placement, activation and save/load: untested.

---

### usa_jacksonville_nas_jacksonville - Naval Air Station Jacksonville

**Identity.**
- Operator: United States Navy. Host: United States (Florida).
- node_kind naval_air_station; populate_policy **populate**.
- Sources: R01:17; R02:17; R03:23, 31.

**SOURCE CLAIM.**
- Premier ASW hub; 3,800 acres (R03:23). R01:17 repeats only 'premier hub for anti-submarine warfare' and the P-8A / MQ-4C pairing; it gives no acreage.
- Over 100 aircraft, including P-8A, MH-60R, C-130T and MQ-4C (R03:23). The table lists P-8A, MH-60R and MQ-4C (R03:31).
- Focus: tracking submarines in the Atlantic and Caribbean (R03:23).
- Named in R02:17 among the sites with integrated 'major logistical operations'.

**CHECK.**
- Resident aircraft and squadrons are a priority check (seed:23); the reports give no squadrons or per-type counts.
- The Triton is often reported as Jacksonville-based, flying East Coast missions from NAS Mayport.
- Fidelity fix: no DLA centre is asserted at Jacksonville.
- The Jacksonville operating areas (R03:48) are a sea area, not the air station.
- usn_p_8a: use Squadron1-14 only; Squadron15-26 are foreign.
- port_eastcoast_jacksonville is a civil port (proxy, hidden). Only port_eastcoast_mayport is Role=LargeMilitary, and Mayport is not a research node.

**Position.** Approx, verify.
- About 30.24N 81.68W.
- Evidence: stock Port Jacksonville 30.3278,-81.6437 (about 6 NM away), stock Mayport 30.4028,-81.4263 (about 16 NM) and the Jacksonville Fairway sea point 30.39,-81.32.
- Nearest placed sea unit: about 450 NM.

**Forces.** Quantities are SCENARIO CHOICE; R03:23 gives only types and an 'over 100 aircraft' total, with no per-type counts.

| Allocation | Asset id | Role | Unit id (outcome) | Qty | Source basis |
|---|---|---|---|---|---|
| resident_at_base | asset:usatl:nas_jax_field | Airfield | usa_airbase Variant1 + NameOverride 'NAS Jacksonville' (proxy; SEST clone optional) | 1 | R03:23 |
| patrol | asset:usatl:p8a_jax_patrol | Airborne ASW patrol over the Atlantic approaches and Caribbean | usn_p_8a Sq1-14 (exact) | 1 | R03:23 type and focus |
| resident_at_base | asset:usatl:p8a_jax_base | In base air group for turnaround | usn_p_8a (exact) | 2 | R03:23 type |
| reserve | asset:usatl:p8a_jax_reserve | Finite reserve | usn_p_8a (exact) | 1 | R03:23 type |
| resident_at_base | asset:usatl:mh60r_jax | ASW helicopters | usn_mh-60r (exact) | 3 | R03:23 type |
| abstract (not allocated) | gap:usatl:c130t_jax | C-130T transport | missing_fit: usmc_kc-130t (squadron ServiceDates end 2002-2021); usmc_kc-130j (adds a RefuelSystem the C-130T lacks) | 0 | R03:23 |
| abstract (not allocated) | gap:usatl:mq4c_jax | MQ-4C Triton | missing_fit: raaf_mq-4c_triton (Australian squadrons only) | 0 | R01:17, R03:23 |

**Support services.**
- **Aircraft turnaround and ordnance:** usa_airbase stores, 2,000,000 points (AirTorpedo 72, Harpoon 144, Ovod 144). P-8A torpedo and Harpoon categories are present. Sortie repeatability is untested.
- **Ship ammunition:** none; this is an air station and the civil port has no supply.
- **Restocking, fuel and repair:** not established.

**Connections.**
- usg_dla_distribution_network: source, R02:17.
- Atlantic and Caribbean ASW focus: source, R03:23.
- Jacksonville operating areas: source, R03:48.
- usa_norfolk_naval_station_norfolk: authored, ASW cover for the CVN-75 departure.
- usa_richmond_defense_supply_center: authored, aircraft spares.
- usa_whiting_nas_whiting_field: authored, abstract aircrew supply.

**Routine activity.** Proposed.
- One P-8A always airborne, on a box east of Jacksonville and sorties toward the N Florida Straits sea point. It rotates with the base aircraft, which also exercises turnaround.
- MH-60R train in the Jacksonville operating areas.
- **Civil traffic:**
  - Ships at the Jacksonville Fairway: civ_ms_car_carrier_a, civ_ms_bulk, civ_ms_c7s68 (date check), civ_fv_fishingboat_a (pinned to Variant3 'Fishing boat US' or given a NameOverride, as at Norfolk), civ_fv_crabboat.
  - Aircraft: civ_a320/civ_a330 (US squadrons), civ_c340 and civ_v35.

**Validation.**
- Mapping: P-8A and MH-60R exact; C-130T and MQ-4C missing_fit.
- Placement and turnaround: untested.

---

### usa_patuxent_nas_patuxent_river - Naval Air Station Patuxent River

**Identity.**
- Operator: United States Navy (Maryland). node_kind research_test; populate_policy **context_only**.
- 'Pax River' is an editorial alias.

**SOURCE CLAIM.**
- Nerve centre for naval aviation research, development and test; 6,400 acres; over 17,000 personnel (R03:23). R01:17 repeats only 'nerve center for naval aviation research'; it gives no acreage or personnel figure.
- Hosts NAVAIR (R03:23, R03:30) and the Naval Test Pilot School (R03:23 only).
- Flight and weapons integration testing of the P-8A, F-35 variants and unmanned systems (R03:23). The table lists 'Test variants of F-35, P-8, Unmanned systems' (R03:30).

**CHECK.**
- Test variants are not combat-ready resident forces and are never counted as available.
- Fidelity: R03:30 gives only 'NAVAIR HQ'. No further place-specific claims exist.
- R02:17's 'these CONUS hubs' sentence does not apply here; R02 does not mention Patuxent River.

**Position.** Approx, verify.
- About 38.29N 76.41W.
- Evidence: stock sea point Chesapeake Bay 2 (37.88,-76.16), about 27 NM away. Nearest placed sea unit: about 278 NM.

**Forces.** Not populated by default.
- Optional marker, asset:usatl:pax_field_marker: usa_airbase Variant1 (preferred by the verify) or nato_small_airbase (proxy; us-navy inventory installation mapping, Nation=US in its vanilla variants file). Either takes a NameOverride 'NAS Patuxent River', since both display generic names. It must be given an explicitly empty air group, because default groups spawn Cold War aircraft and the editor drops empty CustomAirGroup lines. Quantity: SCENARIO CHOICE (optional, default 0).
- Test aircraft (gap:usatl:pax_test_aircraft): **missing_fit**. No VX-23, VX-20, HX-21, VX-1 or UX-24 livery exists. The nearest are usn_f-35c Squadron2 (VX-9 paint), usn_fa_18e_rsa Squadron18 (VX-4) and usn_p_8a labelled 'test det'. There is no unmanned test type.
- Quantity: SCENARIO CHOICE (optional, default 0; at most 1-2 static aircraft as dressing). They never sortie and are never counted.

**Support:** none (context). **Connections:** authored context with Jacksonville only (the P-8A type, R03:23); no logistics link. **Routine activity:** none; optional civil traffic in the Chesapeake Bay.

---

### usa_whiting_nas_whiting_field - Naval Air Station Whiting Field

**Identity.**
- Operator: United States Navy (Florida). node_kind training; populate_policy **abstract_logistics_only**.

**SOURCE CLAIM.**
- Conducts over 60 percent of primary flight training for the Navy, Marine Corps and Coast Guard, and is needed to simulate pilot pipelines (R03:23).
- About 250 primary training aircraft, type not named (R03:23, R03:32).

**CHECK.**
- Check the location before any placement.
- Sea Power may have no pilot-pipeline mechanic.
- The 250 count is not a placement figure.
- T-6B and TH-73 are lookup terms from the inventory, not from R03.
- R02:17's 'these CONUS hubs' sentence does not apply here; R02 does not mention Whiting Field.

**Position.** Approx, verify: about 30.72N 87.02W. No stock world-data node, and no mission centred within 300 NM.

**Forces.**
- asset:usatl:whiting_pipeline: abstract aircrew-replacement source.
- Trainer proxies, used only as optional background traffic:
  - civ_v35, labelled 'T-6B stand-in' (a civil light single, Role=Airliner).
  - fr_as-350 Squadron2 (Nation=US), labelled 'TH-73 stand-in'.
  - Installation proxy: nato_very_small_airbase.
- Quantity: SCENARIO CHOICE (optional, default 0).

**Support:** not applicable. **Connections:** authored abstract aircrew supply to Jacksonville and Norfolk; source role from R03:23. **Routine activity:** none unless the Gulf coast is active.

---

### usa_newport_news_shipbuilding - Newport News Shipbuilding

**Identity.**
- Operator not stated in the reports (commercial shipyard). Host: United States (Virginia).
- node_kind shipyard_maintenance; populate_policy **context_only**, holding one asset that is out of service.

**SOURCE CLAIM.**
- 'Carriers like USS John C. Stennis undergo years-long Refueling and Complex Overhauls at facilities like Newport News Shipbuilding, removing them from the strategic chessboard' (R03:50).
- R03:60 lists Stennis with home port Norfolk and status RCOH.

**CHECK.**
- 'Facilities like' makes this an example, not an assertion.
- Check where the Stennis RCOH is held and when it completes (reported extended to about 2026 or later). If it is complete at the scenario date, reallocate the hull once, for example to Norfolk.
- If Truman has entered RCOH instead, it moves here and is removed from the Atlantic allocation (the collection's variants file annotates CVN-75 'Real World No CVW RCOH'). It arrives without its air wing, which stays unallocated; see the Norfolk contingency.
- Fidelity: parent_or_colocated should be empty.
- R02:17's 'these CONUS hubs' sentence does not apply here; R02 does not mention Newport News.

**Position.** Approx, verify.
- About 36.99N 76.44W.
- Evidence: stock Port Norfolk node about 6 NM away; Hampton Roads sea point about 10 NM.

**Forces.**

| Allocation | Asset id | Role | Unit id (outcome) | Qty | Source basis |
|---|---|---|---|---|---|
| servicing_maintenance | asset:usatl:cvn74_stennis | Carrier in RCOH; unavailable | usn_cvn_nimitz_2025 Variant7 'CVN-74 John C. Stennis' (exact hull; the 2027s_adou unit lacks CVN-74) | 1 | R03:50, R03:60 |

SCENARIO CHOICE: keep it as a ledger entry until placement is validated. As an option, place it as an inert static hull with weapons on Hold and no air group. That needs a restore step, because the editor drops empty CustomAirGroup lines and the broken default wing would come back.

**Support.**
- Repair and overhaul: not modelled. There is no shipyard or drydock function. US_Los_Alamos (AFDB-7, 1961-1991 target object) is not representative.

**Connections.** usa_norfolk_naval_station_norfolk: source (hedged), R03:50 and R03:60.

**Routine activity.** None.

---

### usg_dla_distribution_network - Defense Logistics Agency distribution network (agency-wide)

**Identity.**
- Operator: US Defense Logistics Agency. No site.
- populate_policy **abstract_logistics_only**.

**SOURCE CLAIM.**
- Supplies 86 percent of spare parts and nearly 100 percent of fuel and troop-support consumables (R02:11). R01:21 repeats only the 86 percent spares and nearly 100 percent fuel figures, without 'troop support consumables'.
- 17 major CONUS distribution centres, the origin points of supply chains (R02:15).
- Many centres are co-located with the largest force-generation bases. Major logistical operations are integrated into NS Norfolk, NB San Diego, NAS Jacksonville and PSNS (R02:17).
- CONUS hubs are the ultimate source of replacement airframes, deep-maintenance components and bulk munitions (R02:17).
- Seven OCONUS hubs plus prepositioned ships (R02:21).
- Named centres: R02:15, R02:23 and R02:29-34. R01:23 repeats Yokosuka and Guam, which is repetition, not corroboration.

**CHECK.**
- 'Managed primarily by the DLA' likely overstates DLA's role.
- Seven OCONUS hubs are claimed, but only six are named. R02:33 lists Diego Garcia in the same table without calling it a DLA centre.
- 17 CONUS centres are claimed (R02:15), but only Susquehanna and San Joaquin are named.
- R02:17 states co-location only generically ('many DLA distribution centers'). No centre at Norfolk, Jacksonville, San Diego or PSNS is asserted or named; those four are only sites into which 'major logistical operations are integrated'.
- The same correction applies to the register's expansion_backlog line "DLA centres co-located with Norfolk, San Diego, Jacksonville and PSNS are implied but unnamed (R02:17)": it should read "R02:17 states co-location only generically; no DLA centre at Norfolk, San Diego, Jacksonville or PSNS is asserted or named."
- Treating Richmond, the Army depots and the APF as members of the network is an authored grouping (fidelity).

**Position.** None; agency-wide.

**Forces.**
- asset:usatl:dla_network: abstract. There is no engine distribution mechanic.

**Support.**
- 'Restock' can only be represented by finite relief hulls in the world allocation, such as asset:usatl:takr_norfolk_relief. Never as unlimited spawns.
- usaf_c-141b PlaneCargoSupplySystem is the one candidate air-cargo ammunition mechanism. It is untested and date-gated to 1965-2006.

**Connections.**
- Source:
  - Susquehanna and San Joaquin: R02:15.
  - Yokosuka, Guam, Pearl Harbor, Bahrain, Sigonella and Germersheim: R02:23.
  - Norfolk, San Diego, Jacksonville and PSNS: R02:17.
  - APF cargo includes DLA fuels: R01:23, R02:25.
- Authored: Richmond and the three Army depots.

---

### usa_dla_susquehanna - DLA Distribution Susquehanna

**Identity.** Operator: DLA (Pennsylvania). populate_policy **abstract_logistics_only**.

**SOURCE CLAIM.**
- One of the massive primary hubs anchoring the CONUS network; with San Joaquin it manages the bulk of cross-country and international materiel routing (R02:15).
- 'Primary East Coast CONUS distribution hub' (R02:29).

**CHECK.**
- DLA centre counts and scope are a priority check.
- R02:17's 'these CONUS hubs' sentence is applied as context only.

**Position.** Approx, verify: about 40.2N 76.9W (New Cumberland area; R02 says only 'Pennsylvania'). Inland; stock Baltimore node about 58 NM away.

**Forces.**
- asset:usatl:dla_susquehanna: abstract.
- Optional marker: warehouses_1 or warehouses_3 and tgt_fueltanks_large, with Nation=usa and a NameOverride (proxy; static, no function). Quantity: SCENARIO CHOICE (optional, default 0).
- usa_car_hemtt is left out of the marker. It is not a static target: 3605013271:land_units/usa_car_hemtt.ini has a working TruckSupplySystem (pool 13,500, MaxAmmoPoints 200, 0.5 nmi, 6 targets, LandUnit only). It would act as a mobile land-unit resupply truck and can reload unpriced Patriot rounds. It reaches nothing at sea.

**Connections.**
- usg_dla_distribution_network and usp_dla_san_joaquin: source, R02:15.
- Norfolk and Jacksonville: authored, East Coast resupply origin.

---

### usa_richmond_defense_supply_center - Defense Supply Center Richmond

**Identity.** Operator not stated (DLA implied). populate_policy **abstract_logistics_only**.

**SOURCE CLAIM.** A dedicated supply installation specialising in aircraft parts (R02:17).

**CHECK.**
- Renamed DLA Aviation around 2010.
- Its DLA membership is an authored grouping.
- The engine has no aircraft-spares or airframe-replacement mechanic.

**Position.** Approx, verify: about 37.4N 77.4W. Stock Hampton Roads sea point about 62 NM away.

**Forces.** asset:usatl:dsc_richmond: abstract. Optional warehouses_3 marker (proxy). Quantity: SCENARIO CHOICE (optional, default 0).

**Connections.**
- usg_dla_distribution_network: authored grouping.
- Jacksonville and Norfolk: authored, aviation spares.

---

### usa_army_depot_anniston - Anniston (Army depot)

**Identity.** US Army; populate_policy **abstract_logistics_only**.

**SOURCE CLAIM.** Listed among 'various Army depots' in the other dedicated supply installations (R02:17).

**CHECK.**
- R02 gives no state, location or function.
- The inventory's 'maintenance/ammunition depot' label is lookup context, not R02.

**Position.** Approx, verify: about 33.6N 86.0W (Alabama; public, not R02). Far inland.

**Forces.**
- asset:usatl:anniston_depot: abstract.
- Optional static marker: tgt_industry_buildings_1, warehouses_3 and Ammo_Bunker (proxy). Quantity: SCENARIO CHOICE (optional, default 0).
- tgt_ammo_depot_small and nv_headquarters resupply land units only and serve nothing at sea.

**Connections.** Norfolk: authored, port of embarkation via RRF sealift (civ_ms_roro_c US variants as a labelled option).

---

### usa_army_depot_red_river - Red River (Army depot)

**Identity.** US Army; populate_policy **abstract_logistics_only**.

**SOURCE CLAIM.** Listed among the Army depots (R02:17).

**CHECK.** R02 gives no state, location or function.

**Position.** Approx, verify: about 33.4N 94.3W (Texas; public, not R02). About 800 NM from the nearest proven sea point.

**Forces.** asset:usatl:red_river_depot: abstract. Optional marker as for Anniston (proxy). Quantity: SCENARIO CHOICE (optional, default 0).

**Connections.** Norfolk: authored, as for Anniston.

---

### usa_army_depot_tobyhanna - Tobyhanna (Army depot)

**Identity.** US Army; populate_policy **abstract_logistics_only**.

**SOURCE CLAIM.** Listed among the Army depots (R02:17).

**CHECK.**
- R02 gives no state, location or function.
- The inventory's 'C4ISR depot' label is lookup context, not R02.

**Position.** Approx, verify: about 41.2N 75.4W (Pennsylvania; public, not R02). Stock New York node about 81 NM away.

**Forces.** asset:usatl:tobyhanna_depot: abstract. Optional civ_comm_buildings marker (proxy, Nation=US). Quantity: SCENARIO CHOICE (optional, default 0).

**Connections.** Norfolk: authored, as for Anniston.
