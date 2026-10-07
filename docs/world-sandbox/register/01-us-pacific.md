<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## US Pacific generation (Southern California, Puget Sound) and West Coast distribution

Region code `usp`. Every package keeps three labels apart:
- **SOURCE CLAIM**: what R01-R03 say, cited as report:line.
- **CHECK**: a known doubt or a verification still needed. Sources are never silently corrected.
- **SCENARIO CHOICE**: our proposed allocation, quantity or activity.

Repetition between R01 and R03 is not corroboration. Routine activity is proposed, not implemented. Positions are approximate public locations (approx, verify); in-game placement is pending validation. Unit ids were re-resolved with `find_unit_file` at repo `fe480cd4` (2026-10-07). All resolve except the known-unresolved `usn_mh-60r_26`, which is not used.

### Region summary

- **Nodes.**
  - Populated: `usp_coronado_nas_north_island` (populate), `usp_coronado_nab_coronado` (populate_small), `usp_sandiego_naval_base_san_diego` (populate), `usp_kitsap_bremerton_psns` (populate).
  - Context only: `usp_coronado_naval_base_coronado`, `usp_kitsap_naval_base_kitsap`, `usp_kitsap_bangor`.
  - Abstract logistics only: `usp_dla_san_joaquin`.
- **R03 carrier table (R03:52-62).** Each carrier is allocated once. All five rows are undated "current/recent" claims, so each is a CHECK (seed:23 lists carrier status as a priority check).

| Asset | Hull (unit, variant) | SOURCE CLAIM | CHECK | SCENARIO CHOICE | Package |
|---|---|---|---|---|---|
| asset:usp:cvn68_nimitz | CVN-68 (usn_cvn_nimitz_2025 Variant1) | Home port Kitsap-Bremerton, status "Pre-decommissioning/Homeport shift" (R03:54). Operates out of Kitsap-Bremerton, with homeport shifts and deployments through San Diego (R03:48) | Public reporting has Nimitz inactivating and moving to Norfolk around 2026. The variant's ServiceDate runs 2025 to 2027 | reserve: non-ready at PSNS, no air wing, dormant | usp_kitsap_bremerton_psns |
| asset:usp:cvn70_carl_vinson | CVN-70 (usn_cvn_nimitz_2025 Variant3) | Homeported "in San Diego"; TSTA and FEP off Southern California before transiting west (R03:50, R03:56) | Reported deployed in 2025. Berth not resolved | training_test: SoCal operating area, with a reduced wing, 2 DDG and 1 T-AKE | usp_sandiego_naval_base_san_diego |
| asset:usp:cvn71_theodore_roosevelt | CVN-71 (Variant4) | "Recently departed San Diego" to relieve carriers in the CENTCOM AOR; status "Transiting to U.S. Central Command" (R03:50, R03:57) | Appears to reflect 2024 | transit: underway toward the Arabian Sea, **not at San Diego** | usp_sandiego_naval_base_san_diego (hand-off) |
| asset:usp:cvn72_abraham_lincoln | CVN-72 (Variant5) | Homeported in San Diego; status "Western Pacific Deployment" (R03:50, R03:58) | Dated claim | underway_deployed: Philippine Sea, **not at the pier** | usp_sandiego_naval_base_san_diego (hand-off) |
| asset:usp:cvn76_ronald_reagan | CVN-76 (usn_cvn_nimitz Variant9, legacy unit) | Home port Kitsap-Bremerton; "Drydocking Planned Incremental Avail."; "Inactive (Maintenance)" (R03:62). George Washington took over the Yokosuka role from Reagan (R03:38) | Dated claim | servicing_maintenance: PSNS drydock, not combat-ready, static | usp_kitsap_bremerton_psns |

- **Scale (SCENARIO CHOICE).**
  - 17 ships: the 5 named carriers plus 12 counted escorts, amphibious ships and auxiliaries.
  - 115 aircraft held in air groups: three representative carrier wings of 25, one LHD element of 14, 10 shore helicopters, and 16 MH-60R in eight destroyer flights of 2. Each flight is an embarked sub-asset (asset:usp:<ship id>_flt). Keeping each DDG's shipped MH-60R x2 is a SCENARIO CHOICE. If the AH-1W pair is omitted (see the scenario-date CHECK), the total is 113.
  - 3 installation clusters, 1 optional marker and 2 abstract records.
  - Report totals (57,000 acres, 36,000 personnel, 12,000 acres) are not placement quantities. plan:65 says a report's fleet size is not a placement instruction; this applies the same rule to other report totals. plan:11 adds that the plan itself asserts no new asset counts.
- **Hand-off rule.** R03 ties the CVN-71 and CVN-72 groups to San Diego, so each group (carrier, embarked wing, 2 DDG and their helicopter flights) is allocated here. Physically, though, they are in the Arabian Sea approaches and the Western Pacific. The Arabian Sea/Horn and Pacific-forward regional packages must **reference these asset ids, not allocate the hulls again**. George Washington (CVN-73) belongs to the Yokosuka package and is not allocated here.
- **Destroyer identity (SCENARIO CHOICE, world hull ledger).** Hull number (DDG-nn) is the identity key, not unit+variant. usn_ddg_arleigh_flt2A_099_2027 is a `#!alias` of usn_ddg_burke_f2a_099_late and names the same DDG-99 and DDG-101 to 107, so the _2027 set is not used. Pins: sd_ddg_1 DDG-99, sd_ddg_2 DDG-101, vinson_ddg_1 DDG-102, abe_ddg_1 DDG-103, abe_ddg_2 DDG-104 (_099_late V1 to V5); tr_ddg_1 DDG-108, tr_ddg_2 DDG-109 (_108_late V1, V2); vinson_ddg_2 DDG-125 (f3_125 V1).
- **Scenario date (CHECK).** No world date is set. With these pins, every placed ship and aircraft fits a world dated 2025 to 2027, except two items whose date filtering is untested: the AH-1W pair (usmc_ah-1w_late Default squadron dated 2003 to 2010) and the US_Los_Alamos scenery (1961 to 1991). The full list is in the NB San Diego checks.
- **Collection (inventories).**
  - No named NAS, West Coast port, shipyard or depot unit exists. Installations are labelled proxies: usa_airbase Variant1 "Naval Air Station", generic warehouses and fuel tanks, and the US_Los_Alamos floating dock.
  - The modern Nimitz units are exact hulls, but **no shipped variant wing works**, so every carrier needs a mission CustomAirGroup.
  - Missing or proxy aviation: MH-60S is a missing fit (an HH-60H serves as a labelled stand-in). There is no CMV-22B or C-2A, and no modern carrier tanker (only a dated KA-3B proxy).
  - Missing amphibious assets: no LCAC or LCU, and no modern LPD or LSD.
  - The auxiliaries are SEST stand-ins on donor meshes, so they are proxies.
- **Services (inventories).**
  - Finite ship-ammunition supply comes only from SEST-patched hulls. The RE-power freighters (civ_ms_freighter_a/b, civ_ms_super_p) and docks (nv_pt_boats_docks) carry very large finite pools (freighters 4.92-12 million points with no MaxAmmoPoints ceiling) or effectively unlimited ones (docks, 9,999,999,999), so they are avoided or disclosed.
  - No finite shore supplier exists.
  - Ship fuel is not modelled, and no unit file carries a repair system.
  - Supplier restocking: not established. It is untested; usaf_c-141b's PlaneCargoSupplySystem (1965-2006) is the one candidate mechanism. No way to top up carrier flight-deck magazines at sea is known either (untested).
  - Airbase ordnance is either usa_airbase's finite 2,000,000-point pool or, on an airbase_us clone, the undocumented engine default.
- **Positions (scope report).**
  - Store absolute lat/lon; the map centre is only a datum. With a candidate centre of 42N 20E, San Diego is x = -8,227 and PSNS x = -8,558. Both are inside proven |x| (11,361 in a played save).
  - No mission has ever placed a unit within 300 NM of San Diego or Kitsap. The nearest proven sea point to San Diego is about 430 NM WSW (mod 3810611344 "Bell Systems Test" missions, centre 30.0,-125.0). Kitsap's nearest proven sea point is a different point, about 990 NM away (installations lens). The Bell Systems centre is about 1,060 NM from Kitsap.
  - The builder pool fails at San Diego (766 NM) and Kitsap (980 NM) (scope B1).
  - Natural Earth 1:10m reads Hood Canal (47.73,-122.72) as land (scope B4), so Kitsap waters wait on probe P8.
  - San Diego to Western Pacific links cross ±180, the one engine edge on record. Probe P3a has not tested it.
  - The San Diego to CVN-72 separation (about 5,700 NM) and San Diego to CVN-71 (about 8,360 NM) both exceed the 3,450 NM spread in played content (scope §2.2). Neither is a known limit.
- **Fidelity fixes applied.**
  - NB San Diego: alias dropped; carrier home-port claims recast as city-level, with the berth unresolved (NB San Diego vs NAS North Island) and held on one record. CVN 68 now cited to R03:54.
  - R02:17 reworded for NB San Diego and PSNS, with no DLA centre asserted.
  - NAS North Island: colocation link to NB San Diego removed, and R03:17's "such as" wording for CVW-2/9/11/17 restored.
  - Kitsap: R03:21 now reads "strategically vital because it combines...". Bremerton = PSNS flagged as an inference, and the Bangor nuclear exclusion cited to seed:25.
  - plan:81 reworded, and San Joaquin's "Pacific" labelled authored.
  - Missing claims added: R03:17 simulation guidance, R03:27 (CVNs at Coronado), R01:17 drydocks, R03:29, R03:54, R02:15 (17-centre network) and R02:17 (CONUS-hub role).

---

### usp_coronado_naval_base_coronado - Naval Base Coronado

**Identity.**
- Alias NB Coronado. United States Navy, host United States.
- node_kind mixed_base; populate_policy **context_only**.
- Sources R01:15, R03:17 and R03:27.

**Role (SOURCE CLAIM).**
- About 57,000 acres; the USN's largest installation by footprint (R01:15, R03:17). In California; an aerospace-industrial complex with over 36,000 personnel (R03:17).
- Hosts the carrier-capable NAS North Island, major amphibious training grounds and Naval Special Warfare environments (R01:15, R03:17). Only R03:17 names the amphibious site as NAB Coronado.
- Simulation guidance: "complex air traffic control, carrier qualification cycles, and the integration of special operations deployments" (R03:17).
- Table row: "Pacific Fleet Hub, Aviation, Amphibious"; key assets "CVNs, F-35C, F/A-18, MH-60R/S, Special Warfare" (R03:27).

**Why context only.** This is the umbrella installation. Forces go to the component nodes so that no asset is allocated twice.
- Per the fidelity fix, the F-35C, F/A-18 and MH-60R/S families come from the umbrella table (R03:27). R03:17 prose places them at NAS North Island, so they are handled only there or in embarked wings.
- R03:27 is the only line that puts CVNs at Coronado. R03 gives the carriers' home port as "San Diego" (R03:50, R03:56-58), and those carriers are held on the NB San Diego record.

**Position.** Approx 32.7N, -117.2 (approx, verify), covering North Island and the Silver Strand.
- In-game: the stock world-database city point "San Diego" sits at 32.715,-117.163 (campaigns/us_cities_pacific.ini), about 3 NM away.
- There is no installation unit and no mission placement within 300 NM.
- No proven pool point exists (scope B1).

**Forces.**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:coronado_nsw_context | abstract | Naval Special Warfare environments | none | none | 0 | R01:15, R03:17; no facility named |

**Support.** Nothing at umbrella level; see the component packages.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usp_coronado_nas_north_island | parent of component air station | source | R01:15, R03:17 |
| usp_coronado_nab_coronado | parent of component amphibious training base | source | R03:17 |

NB San Diego is a separate installation. The reports state no relationship between it and Coronado, so no link is drawn.

**Routine activity.** None at the umbrella. R03:17's guidance becomes proposals at North Island (carrier qualifications) and NAB Coronado (amphibious training). Special operations integration is not populated.

**Checks.**
- R03:27 lists CVNs at Coronado. R03:17 only calls North Island a CSG embarkation point, and R03:50 and R03:56-58 say "San Diego". Check which pier hosts each carrier.
- Resident aircraft and squadrons are a priority check (seed:23).
- Acreage and personnel are report claims, not gameplay quantities (plan:65, applied to report totals; plan:11 as context).
- R01:15 and R03:17 are near-verbatim repeats of each other.
- Validation: research checked by three fidelity passes. Placement, runtime and save/load not tested.

**Gaps.**
- The NSW facility is unnamed (expansion backlog).
- There is no named Coronado installation unit.

---

### usp_coronado_nas_north_island - Naval Air Station North Island

**Identity.**
- Alias NAS North Island. United States Navy, host United States.
- node_kind naval_air_station; populate_policy **populate**.
- Sources R01:15, R03:17 and R03:27 (umbrella table).
- populate_reason, reworded per fidelity: "the only West Coast naval air station named in the reports".

**Role (SOURCE CLAIM).**
- A carrier-capable air station (R01:15, R03:17).
- "A primary embarkation point for Pacific-bound Carrier Strike Groups" (R03:17).
- Hosts "large concentrations of MH-60S and MH-60R Seahawk helicopters, alongside F/A-18 Super Hornets and F-35C Lightning IIs belonging to Carrier Air Wings such as CVW-2, CVW-9, CVW-11, and CVW-17" (R03:17). The air wings are examples, and "belonging to" applies to the fighters only.
- Simulation guidance on ATC, carrier qualification (CQ) cycles and special operations integration (R03:17).
- The R03:27 umbrella table lists CVNs (see Checks).

**Position.** Approx 32.7N, -117.2 (Halsey Field; approx, verify).
- In-game: no NAS unit. The stock "San Diego" city point is about 3 NM away, and the KLAX world-database airport about 96 NM.
- Nearest proven placements: sea 429 NM, land 3,298 NM (inventory, installations lens).
- Placement needs a new coast extract or the global land mask (scope B1, B3, B5).

**Forces.**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:ni_airfield | resident_at_base | Installation: naval air station with aviation stores | usa_airbase (Variant1 "Naval Air Station,NAS"; NameOverride "NAS North Island (stand-in)"; Nation=usa; CustomAirGroup) | proxy | 1 | R01:15, R03:17 (carrier-capable air station) |
| asset:usp:ni_hsm_det | resident_at_base (2 airframes fly the local patrol) | MH-60R shore detachment (ASW/SUW) | usn_mh-60r (US HSM squadron; not the RAN squadron) | exact | 6 | R03:17 "large concentrations" (no number given) |
| asset:usp:ni_hsc_det | resident_at_base | MH-60S logistics/SAR detachment | usn_hh-60, labelled "MH-60S stand-in" (alternative usn_sh-60f) | proxy (the MH-60S itself is a missing fit) | 4 | R03:17 |
| (not placed) | none | F/A-18 and F-35C ashore | usn_fa_18e_rsa, usn_fa_18f_rsa, usn_f-35c | exact | 0 ashore (SCENARIO CHOICE) | R03:17 claim; see CHECK |

SCENARIO CHOICE on the fighters: R03:17's fighter families are allocated only as embarked carrier wings (NB San Diego package), so each airframe exists once. None is placed ashore until the Lemoore check is resolved. The source claim is kept and not corrected.

Alternative installation (design proposal): a named SEST clone of airbase_us, following integration/raaf-bases. The clone must replace airbase_us's broken default air group (malformed S-70B-2 line, missing usmc_vh-3d Squadron1, ISAF usn_fa-18f Squadron3) and add FlightDeck_ stores, because airbase_us declares none.

**Support services.**
- **Aircraft turnaround and ordnance:**
  - usa_airbase holds a finite FlightDeck_AmmoCapacity of 2,000,000, with categories AirTorpedo 72, Ovod 144 and Harpoon 144. Capacity is 72 aircraft.
  - Recovery and repeat sorties are not tested.
  - On an airbase_us clone the ordnance stock is the undocumented engine default.
- **Ship ammunition:** none; this is an air station.
- **Supplier restocking:** not established.
  - No supplier is known to top up FlightDeck_ magazines (untested).
  - usaf_c-141b carries a PlaneCargoSupplySystem, the only air-cargo ammunition mechanism in the collection. It is untested, date-gated to 1965-2006 and not sourced here.
- **Fuel:** not established.
  - Ship fuel is not modelled.
  - Air-to-air refuelling: no modern carrier tanker exists. usn_ka-3b is a dated "MQ-25 stand-in" proxy with squadron dates 1956-1991, and it is not placed.
- **Repair:** not established.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usp_coronado_naval_base_coronado | parent | source | R01:15, R03:17 |
| usp_coronado_nab_coronado | sibling component | source | R03:17 |
| usp_sandiego_naval_base_san_diego | CSG embarkation point for the San Diego carrier record; carrier berth unresolved | source for the activity (R03:17: North Island is a Pacific-bound CSG embarkation point; R03:50 and R03:56-58 say only "San Diego", at city level). The node mapping is authored, because the berth is unresolved and holding the carriers on the NB San Diego record is a register choice | R03:17; R03:50, R03:56-58 |
| SoCal operating area | CQ cycles and deck operations | source for the activity (R03:17 guidance on carrier qualification cycles; R03:50 SoCal work-ups). Pairing these with CVN-70 is a SCENARIO CHOICE | R03:17, R03:50 |
| usp_sandiego_naval_base_san_diego | helicopter logistics and SAR support to ships | authored | n/a |

**Routine activity (proposed).**
- 2 x MH-60R fly a looping SUW/ASW patrol of the San Diego approaches. Routes must outlast the session, because aircraft orbit when their route ends.
- CQ and deck-cycle sorties use CVN-70's embarked wing in the SoCal operating area, with North Island as the divert field.
- The MH-60S stand-ins fly visual logistics shuttles to the Vinson group. Cargo transfer is not a game mechanic.
- Civil air uses only the stock world-database links in campaigns/airports.ini:
  - KLAX connects to EGLL, KJFK, KIAH, KMIA, KSFO and KSEA; KSFO to EGLL, KJFK, KIAH and KLAX; KSEA to EGLL, KIAH and KLAX.
  - The stock file has no Japanese, Chinese or Korean civil airport. No West Coast airport links to its Pacific entries, which are US-territory or military fields such as Saipan, Andersen, Hickam and Kadena.
  - airliners: civ_a320 (11 US liveries) and civ_a330 (US and UK liveries) on those US/Europe links;
  - trans-Pacific civ_a330 flights in Japan, China or Korea liveries would be authored airways crossing ±180, so they wait on probe P3a. They are not world-database traffic;
  - general aviation and business aviation: civ_c340, civ_h700;
  - civil helicopters: civ_as-350 (US liveries).
  - Civil aircraft need airways or they orbit.

**Checks.**
- Pacific air wings' strike-fighter and F-35C squadrons are commonly shore-based at NAS Lemoore, not North Island. Check before placing fighters here (register; seed:23).
- CVW-2/9/11/17 are R03's examples. No line pairs an air wing with a carrier.
- R03 never names the carrier berth, and R03:27 lists CVNs under Coronado. San Diego CVNs are generally reported as berthed at North Island (own knowledge, optional fidelity note). This needs checking.
- The parent_or_colocated link to NB San Diego was removed (fidelity): no report connects the two installations.
- HSM/HSC squadron-to-base pairings are not sourced.
- The usn_mh-60r model and FLIR depend on mod 3590477166.
- Editor round-trips drop empty CustomAirGroup lines and flatten ROE to Free. A default air group may spawn unless it is overridden.
- Validation: mapping re-resolved. Placement, runtime, turnaround and save/load not tested.

**Gaps.**
- No named NAS unit.
- No MH-60S unit or HSC squadron.
- No CMV-22B or C-2A.
- No MQ-25 (only a dated KA-3B proxy).
- No proven placement.

---

### usp_coronado_nab_coronado - Naval Amphibious Base Coronado

**Identity.**
- Alias NAB Coronado. United States Navy, host United States.
- node_kind training; populate_policy **populate_small**.
- Sources: R03:17 names the facility. R01:15 describes the same amphibious grounds without naming them, and R03:27 lists "Amphibious" in the umbrella table (optional context).

**Role (SOURCE CLAIM).** "Major amphibious training grounds at the Naval Amphibious Base Coronado" (R03:17). No units are named.

**Position.** Approx 32.7N, -117.2 (approx, verify). The Silver Strand is at about 32.68,-117.16. In-game evidence is the same as for North Island: no unit and no proven placement.

**Forces.**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:nab_marker | resident_at_base | Training-site marker and landing objective | FOB (mod 3600788156, "Forward Operating Base,FOB"; Nation=All, set to usa; NameOverride "NAB Coronado (marker)") | proxy | 0-1, optional | design choice |
| (no new asset) | n/a | Amphibious training ship | provided by asset:usp:sd_lhd_1 (NB San Diego package) | n/a | 0 here | design choice; not duplicated |
| (none) | n/a | Ship-to-shore connectors | none: no LCAC or LCU unit exists | none | 0 | gap |

The marker carries no supply. Do not use nv_headquarters here: it renders as a Vietnamese HQ and carries unlimited land-unit supply.

**Support services.**
- Ship ammunition: none.
- Aircraft turnaround and ordnance: none; the LHD's deck serves its own aviation element.
- Supplier restocking, fuel and repair: not established.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usp_coronado_naval_base_coronado | parent | source | R03:17 |
| usp_coronado_nas_north_island | sibling component | source | R03:17 |
| usp_sandiego_naval_base_san_diego (asset:usp:sd_lhd_1) | amphibious training partner | authored | n/a |

**Routine activity (proposed).**
- Periodic amphibious training serials by asset:usp:sd_lhd_1 off the Silver Strand.
- MV-22B and UH-1Y sorties to the marker. Connector landings are impossible because no LCAC or LCU exists.

**Checks.**
- Neither report places the Naval Special Warfare environments at NAB. Keep NSW at the umbrella.
- The training role is a source claim; every unit here is a design choice.
- FOB is Nation=All and must carry a per-unit Nation.
- Validation: placement and runtime not tested.

**Gaps.**
- No LCAC or LCU.
- No San Antonio LPD or Whidbey Island/Harpers Ferry LSD; only the Cold War proxies usn_lpd_austin and usn_lst_newport.
- No real America-class LHA; only the fictional "Tripoli-class" proxy.
- No NAB unit.

---

### usp_sandiego_naval_base_san_diego - Naval Base San Diego

**Identity.**
- United States Navy, host United States.
- node_kind naval_base; populate_policy **populate**.
- Fidelity: the alias "San Diego (R03 carrier home-port wording)" is dropped.
- Sources R02:17; R03:48, R03:50, R03:56-58 (city-level "San Diego"); R03:54 (cross-reference for the Nimitz row).

**Role (SOURCE CLAIM).**
- R02:17, reworded per fidelity: NB San Diego is named as one of four bases into which "major logistical operations are integrated". That follows a sentence saying many DLA centres are co-located with the largest force-generation bases. No DLA centre is named or asserted here.
- R03:50: Vinson and Lincoln are "homeported in San Diego" and conduct TSTA and FEP off Southern California before transiting west. Roosevelt "recently departed San Diego" for the CENTCOM AOR.
- Table rows: Vinson R03:56, Roosevelt R03:57, Lincoln R03:58.
- R03:48: Nimitz homeport shifts and deployments run through San Diego. The hull number and status come from R03:54.
- **Fidelity: these are city-level home-port claims.** The berth is unresolved between this node and NAS North Island. As a register choice, the carriers are held once here as the "San Diego home-port (unresolved)" record. North Island points to it through an authored link.
- The populate reason's "Pacific" is authored.

**Position.**
- NB San Diego: approx 32.7N, -117.1 (32nd Street piers; approx, verify). In-game: the stock "San Diego" city point is about 3 NM away. There is no port unit and no mission placement; the nearest proven sea point is about 430 NM away.
- SoCal operating area (R03:50, "off the Southern California coast"): approx 32.0N, -119.0, an illustrative offshore box centre about 100 NM WSW of the base (approx, verify).

**Forces: base and local group (SCENARIO CHOICE; the reports name no non-carrier ships).**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:sd_pier_scenery | resident_at_base | Pier and logistics scenery; provides no service | warehouses_1 + tgt_fueltanks_large (Nation=usa, NameOverride) | proxy | 1 cluster (2 objects) | design |
| asset:usp:sd_ddg_1 | patrol | Destroyer on a local patrol of the San Diego approaches | usn_ddg_burke_f2a_099_late Variant1 "DDG-99 Farragut" (ServiceDate 2022 onward) | exact | 1 | none (design) |
| asset:usp:sd_ddg_1_flt | patrol (embarked on sd_ddg_1) | Destroyer helicopter flight | usn_mh-60r x2 (shipped AirGroup, Default squadron) | exact | 2 | design |
| asset:usp:sd_ddg_2 | reserve | In-port destroyer, dormant until activated | usn_ddg_burke_f2a_099_late Variant2 "DDG-101 Gridley" (2022 onward) | exact | 1 | none (design) |
| asset:usp:sd_ddg_2_flt | reserve (embarked on sd_ddg_2) | Destroyer helicopter flight | usn_mh-60r x2 (shipped) | exact | 2 | design |
| asset:usp:sd_lhd_1 | resident_at_base | Amphibious assault ship; NAB training partner | usn_lhd_wasp (hull chosen at build; not LHD-6, whose dates end in 2021) | exact | 1 | design (R03:17 amphibious role is the link) |
| asset:usp:sd_lhd_1_ace | resident_at_base (embarked) | LHD aviation element | usmc_f-35b x4 (VMFA-211, the only squadron); usmc_mv-22b x6; usmc_ah-1w_late x2, labelled "AH-1Z stand-in (AH-1W late)" (Default squadron dated 2003 to 2010; date filtering untested; alternative: omit the pair); usmc_uh-1y x2 (displays "UH-1N") | exact, except the AH-1 (proxy) | 14 | design |
| asset:usp:sd_tao_1 | resident_at_base | Local replenishment with a small stock. Starts alongside at the NB San Diego piers; an authored trigger sends it to meet sd_ddg_1 on the approaches | usn_tao_kaiser Variant1 "T-AO 187 USNS Henry J. Kaiser" (stand-in, Teide mesh; pinned once world-wide) | proxy | 1 | design |
| asset:usp:sd_relief_cargo_1 | reserve | Finite relief supplier, released by an authored San Joaquin flow | civ_ms_seabee Variant1 "SS Cape May" (pinned once world-wide; Variants 2-3 stay unused), labelled "RRF relief cargo stand-in" | proxy (dated Seabee-class, Role=Merchant) | 1 | authored from R02:30 |

**Forces: San Diego home-port carrier record (city-level R03 claims; berth unresolved).**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:cvn70_carl_vinson | training_test | CVN in TSTA/FEP in the SoCal operating area (approx 32.0N, -119.0) | usn_cvn_nimitz_2025 Variant3 "CVN-70 Carl Vinson" | exact hull; CustomAirGroup mandatory | 1 | R03:50, R03:56 |
| asset:usp:cvw_vinson | training_test (embarked) | Reduced representative wing; no CVW designation assigned | usn_fa_18e_rsa x8, usn_fa_18f_rsa x4, usn_f-35c x4, usn_ea-18g_2020 x2, usn_e-2d x2, usn_mh-60r x3, usn_hh-60 x2 (MH-60S stand-in) | exact, except the MH-60S stand-in (proxy) | 25 | R03:17 families; CVW examples only |
| asset:usp:vinson_ddg_1 | escort | Escort during work-ups | usn_ddg_burke_f2a_099_late Variant3 "DDG-102 Sampson" (2022 onward) | exact | 1 | design |
| asset:usp:vinson_ddg_1_flt | escort (embarked) | Destroyer helicopter flight | usn_mh-60r x2 (shipped) | exact | 2 | design |
| asset:usp:vinson_ddg_2 | escort | Escort during work-ups | usn_ddg_burke_f3_125 Variant1 "DDG-125 Jack H. Lucas" (Flight III; 2023 onward) | exact | 1 | design |
| asset:usp:vinson_ddg_2_flt | escort (embarked) | Destroyer helicopter flight | usn_mh-60r x2 (shipped) | exact | 2 | design |
| asset:usp:vinson_take_1 | support | Replenishment ship for the training group; at-sea ammunition test fixture | usn_take_lewis_clark Variant1 "T-AKE 1 USNS Lewis and Clark" (stand-in, Kilauea mesh; pinned once world-wide) | proxy | 1 | design |
| asset:usp:cvn71_theodore_roosevelt | transit | Underway toward the CENTCOM AOR (Arabian Sea); scenario position approx 8N, 66E, open northern Indian Ocean heading WNW | usn_cvn_nimitz_2025 Variant4 | exact hull; CustomAirGroup | 1 | R03:50, R03:57 |
| asset:usp:cvw_roosevelt | transit (embarked) | Reduced representative wing | as cvw_vinson | as cvw_vinson | 25 | design |
| asset:usp:tr_ddg_1 | escort | Escort for CVN-71 | usn_ddg_burke_f2a_108_late Variant1 "DDG-108 Wayne E. Meyer" (2024 onward; replaces the _2027 set) | exact | 1 | design |
| asset:usp:tr_ddg_1_flt | escort (embarked on tr_ddg_1; hand-off) | Destroyer helicopter flight | usn_mh-60r x2 (shipped) | exact | 2 | design |
| asset:usp:tr_ddg_2 | escort | Escort for CVN-71 | usn_ddg_burke_f2a_108_late Variant2 "DDG-109 Jason Dunham" (2024 onward) | exact | 1 | design |
| asset:usp:tr_ddg_2_flt | escort (embarked on tr_ddg_2; hand-off) | Destroyer helicopter flight | usn_mh-60r x2 (shipped) | exact | 2 | design |
| asset:usp:cvn72_abraham_lincoln | underway_deployed | Western Pacific deployment; scenario position approx 17N, 135E (Philippine Sea) | usn_cvn_nimitz_2025 Variant5 | exact hull; CustomAirGroup | 1 | R03:50, R03:58 |
| asset:usp:cvw_lincoln | underway_deployed (embarked) | Reduced representative wing | as cvw_vinson | as cvw_vinson | 25 | design |
| asset:usp:abe_ddg_1 | escort | Escort for CVN-72 | usn_ddg_burke_f2a_099_late Variant4 "DDG-103 Truxtun" (2022 onward) | exact | 1 | design |
| asset:usp:abe_ddg_1_flt | escort (embarked on abe_ddg_1; hand-off) | Destroyer helicopter flight | usn_mh-60r x2 (shipped) | exact | 2 | design |
| asset:usp:abe_ddg_2 | escort | Escort for CVN-72 | usn_ddg_burke_f2a_099_late Variant5 "DDG-104 Sterett" (2022 onward) | exact | 1 | design |
| asset:usp:abe_ddg_2_flt | escort (embarked on abe_ddg_2; hand-off) | Destroyer helicopter flight | usn_mh-60r x2 (shipped) | exact | 2 | design |

Notes on these allocations:
- Roosevelt is placed late in its transit so that it reaches the Arabian Sea early in play. R03:50 says "recently departed", so an early-transit position in the eastern Pacific is an equally valid SCENARIO CHOICE. Pick one at build.
- Fallback for Vinson: usn_cvn_nimitz_2000s cannot carry CVN-70, because its Variant3 lies beyond NumberOfVariants=2.
- Destroyer identity is the hull number (DDG-nn), never unit+variant. usn_ddg_arleigh_flt2A_099_2027 (3606774881) is a `#!alias` of usn_ddg_burke_f2a_099_late. Its Variant1-8 name the same DDG-99 and DDG-101 to 107, and every variant is ServiceDate 2027 onward. The _2027 set is therefore not used anywhere in this region.
- The hull pins follow the world hull ledger (SCENARIO CHOICE). _099_late V6-V8 (DDG-105 to 107) are not used here; the proposed world hull ledger (register/00-world-integration.md section 1.5) reserves them for wpac:gw_csg_ddg1, me:ddg_1 and usatl:ddg_truman_esc_1. Those packages have not yet applied the pins, so CHECK the world-wide DDG-99/101-107 draw at merge (integration C1). The reports name no destroyers. The real home ports of the pinned hulls are not checked, and some may be Atlantic-based.
- Each destroyer keeps its shipped MH-60R x2 (usn_mh-60r=Default,2 in the _099_late, _108_late and f3_125 [AirGroup]) as an embarked sub-asset, counted in the region total. The Default squadron wears the HSM-40 (Atlantic Fleet FRS) livery. A Pacific HSM squadron can be set by mission CustomAirGroup (SCENARIO CHOICE). Re-check the air group after every editor round-trip.

**Support services.**
- **Ship ammunition:**
  - asset:usp:vinson_take_1, usn_take_lewis_clark: TruckSupplySystem with a 550,000 pool, no ceiling, 110 pts/s, 1.0 nm range, 2 targets, own speed up to 13 kn and receiver up to 16 kn, Vessel and Submarine targets. Categories: Harpoon 48, AirTorpedo 72, ALWT 40, SEST_LandAttack 48, SEST_LongRangeSAM 56.
  - asset:usp:sd_tao_1, usn_tao_kaiser Variant1 (T-AO 187): 80,000 pool, MaxAmmoPoints 2,000, 0.5 nm range. Categories: Harpoon 8, AirTorpedo 16. It refuses Tomahawk (4,350 points) and SM-6 (8,000 points).
  - asset:usp:sd_relief_cargo_1, civ_ms_seabee: 300,000 pool, ceiling 8,000, 35 pts/s, 0.5 nm range, own speed up to 8 kn, receiver up to 12 kn. Categories: Harpoon 24, AirTorpedo 32, ALWT 16, SovietAdvancedASM 8, SEST_LandAttack 16, SEST_LongRangeSAM 16.
  - Pier-side rearm with a finite supplier is not established. nv_pt_boats_docks would give effectively unlimited rearm, so it is not recommended; if it is ever used, disclose the unlimited supply.
- **Aircraft turnaround and ordnance:**
  - Each usn_cvn_nimitz_2025 carrier has FlightDeck_AmmoCapacity 1,200,000 (Phoenix 84, Harpoon 48, AirTorpedo 80, AdvancedARM 64).
  - usn_lhd_wasp has 45,000 (Raft, Harpoon, AdvancedARM).
  - No supplier is known to top up these magazines at sea (untested), so carrier ordnance is treated as finite for each sortie cycle until tested otherwise.
- **Supplier restocking:** not established. It is untested; usaf_c-141b's PlaneCargoSupplySystem (1965-2006) is the one candidate mechanism, and it is not placed. The answer here is the explicitly finite relief asset sd_relief_cargo_1.
- **Fuel:** not established. Ship fuel is not modelled, and oilers pass ammunition only.
- **Repair:** not established. No unit file has a repair system; Task Force Mode flags work only between missions.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usg_dla_distribution_network | major logistical operations integrated (no DLA centre asserted) | source | R02:17 |
| usp_dla_san_joaquin | West Coast resupply origin feeding sd_relief_cargo_1 | authored | R02:30 (role only) |
| usp_kitsap_bremerton_psns | Nimitz homeport shifts and deployments through San Diego | source for the activity (R03:48 names the cities "San Diego" and "Kitsap-Bremerton"). The node mapping is authored: the San Diego berth is unresolved, and Bremerton = PSNS is inferred | R03:48, R03:54 |
| usp_coronado_nas_north_island | carrier embarkation point; berth unresolved | source for the activity (R03:17: Pacific-bound CSG embarkation; R03:50 and R03:56-58: city-level "San Diego"). The node mapping is authored, because the berth is unresolved | R03:17; R03:50, R03:56-58 |
| usp_coronado_nas_north_island | helicopter logistics and SAR support to ships | authored | n/a |
| usp_coronado_nab_coronado | LHD amphibious training partner | authored | n/a |
| SoCal operating area | TSTA/FEP area | source | R03:50 |
| me_bahrain_nsa_bahrain (Fifth Fleet operating areas) | CVN-71 transit destination, the CENTCOM AOR | source for the AOR; the node mapping is authored | R03:50, R03:57; R03:42 |
| wpac_guam_naval_base_apra_harbor / wpac_yokosuka_naval_base | CVN-72 deployment area, Western Pacific | source for the area; the node mapping is authored; crosses ±180 | R03:50, R03:58 |
| cpac_pearl_harbor_dla_distribution | transpacific resupply waypoint | authored | n/a |

**Routine activity (proposed).**
- The Vinson group conducts TSTA/FEP in the SoCal operating area: flight operations, CQ, and ASW/SUW serials. One replenishment-at-sea serial with vinson_take_1 serves as the ammunition-transfer test fixture. It later transits west (authored; crosses ±180, P3a).
- sd_ddg_1 patrols a loop from the San Diego approaches toward San Clemente Island.
- sd_relief_cargo_1 departs on an authored trigger to rendezvous with a group. It is finite and is never respawned.
- sd_lhd_1 runs amphibious training serials with NAB Coronado.
- The CVN-71 group continues its transit, and the CVN-72 group patrols the Philippine Sea. Both are handed off.
- Civilian and neutral traffic (scenario population):
  - container: civ_ms_mairangi_bay, US variants (1978 design; label as a period stand-in);
  - bulk: civ_ms_bulk (Liberia, Japan, Greece);
  - vehicles: civ_ms_car_carrier_a (Japan, Panama, Liberia);
  - tankers: civ_ms_ritina (US, Liberia, Japan) and civ_ms_sealift_pacific Variant2 "MV Sealift Arabian Sea T-AOT-169" (pinned once world-wide; V1 is reserved for the Guam T-AOT and V4 for the Diego Garcia tanker per integration C11; label it, because it carries a live 40,000-point supply block with a 2,000 ceiling);
  - fishing: civ_fv_fishingboat_a Variant3 "Fishing boat US" (avoid Variant5, which reads "China") and civ_fv_crabboat;
  - biologics: civ_humpback.
- Avoid two hull groups:
  - civ_ms_c7s68: its Default ServiceDate ends in 2019, so it may be date-filtered.
  - The RE-power US-flag freighters (civ_ms_freighter_a/b, civ_ms_super_p): they carry live supply pools of 4.92-12 million points with no MaxAmmoPoints ceiling.

**Checks.**
- Carrier statuses are dated (seed:23). Vinson was reported deployed in 2025, and Roosevelt's transit appears to reflect 2024. Check every hull at the scenario date. seed:21 mentions a 2028 schedule, so revalidate the variant ServiceDates if the world is dated 2028.
- **Scenario date (one region-wide CHECK).** No world date is set. These are the date-gated choices, read from the winning variants and squadron files:
  - Carriers: usn_cvn_nimitz_2025 Variant1 (CVN-68) is 2025 to 2027, so it is out of date from 2028. Variants 3, 4 and 5 (CVN-70, 71, 72) are 2025 onward.
  - Destroyers: usn_ddg_burke_f2a_099_late V1-V5 are 2022 onward, and usn_ddg_burke_f2a_108_late V1-V2 are 2024 onward. usn_ddg_burke_f3_125 V1 (DDG-125) is 2023 onward; its V2 is 2027, V3 2026, and V4 onward run 2028 to 2037 (none used).
  - usn_lhd_wasp is 2015 onward. V6, Bonhomme Richard (2015 to 2021), is excluded.
  - usmc_ah-1w_late: the Default squadron in 3737267013 aircraft/usmc_ah-1w_late_squadrons.ini is ServiceDate 2003 to 2010, and its squadrons set no date of their own. Date filtering is untested. Either accept the risk (the shipped usn_lhd_wasp variants, dated 2015 onward, embark this unit) or omit the AH-1 pair, which leaves an ACE of 12.
  - Aircraft start dates: usmc_f-35b 2015 onward, the usn_e-2d Default squadron 2020 onward, and usn_f-35c squadrons starting between 2012 and 2023 (pick one in date).
  - Auxiliaries: usn_tao_kaiser 1986 to 2055, usn_take_lewis_clark 2006 to 2060, civ_ms_seabee Default 1972.
  - Scenery: US_Los_Alamos (PSNS scenery) is 1961 to 1991; date filtering is untested.
  - Proposed civilian traffic and civil aircraft carry start dates only (1972 to 1978, open-ended) or none. civ_ms_c7s68 is the exception, and it is avoided.
  - Avoided or not placed: usn_ddg_arleigh_flt2A_099_2027 (2027 onward), civ_ms_c7s68 (Default ends 2019), usaf_c-141b (1965-2006), usn_ka-3b (squadrons 1956-1991).
  - Result: everything placed fits a world dated 2025 to 2027, except the AH-1W pair and the Los Alamos scenery.
- R03 never names NB San Diego as the berth. R03:27 puts CVNs at Coronado, and North Island is the likely berth (own knowledge). Check.
- R02:17 does not call NB San Diego a "largest force-generation base", and it does not assert a DLA centre here.
- Hand-off: the Arabian Sea and Pacific-forward packages must reference the cvn71/cvn72 groups and must not re-allocate them.
- No usn_cvn_nimitz_2025 variant wing works as shipped. A mission CustomAirGroup is mandatory, and every override id must be re-checked (usn_mh-60r_26 is unresolved).
- Livery mismatches:
  - every usn_e-2d squadron is painted as a different squadron;
  - avoid usn_fa-18f_blk3 and the SEST usn_ea-18g, whose liveries are mismatched;
  - avoid usn_f-35c Squadron1 (name and livery mismatch);
  - restrict usn_fa_18f_rsa to US squadrons.
- usn_lhd_wasp's shipped "AH-1Z" is really an AH-1W (late), per inventory verification.
- The auxiliaries are labelled stand-ins. sd_tao_1 starts alongside, but in-harbour water is untested. The fallback is to start it at sea in company with sd_ddg_1.
- Ticonderoga hulls are not used, pending retirement checks.
- Validation: mapping re-resolved. Placement, routes, transfers and save/load not tested.

**Gaps.**
- No San Diego port unit or West Coast port scenery.
- No finite shore supplier.
- No John Lewis T-AO, hospital ship, tug, salvage ship or T-EPF.
- No modern LPD or LSD.
- No ship fuel and no repair.
- The reports name no non-carrier resident forces.
- Point Loma submarine base: PROPOSED backlog addition (inventory lookup hint, not in R01-R03).

---

### usp_kitsap_naval_base_kitsap - Naval Base Kitsap

**Identity.**
- Alias NB Kitsap. United States Navy, host United States.
- node_kind mixed_base; populate_policy **context_only**.
- Sources R01:17, R03:21 and R03:29.

**Role (SOURCE CLAIM).**
- Merges the former NS Bremerton and NSB Bangor, and combines massive drydock facilities with the basing of the Pacific Fleet's ballistic-missile submarines (R01:17).
- In the western Puget Sound; about 12,000 acres. Per fidelity: "strategically vital because it combines" drydock and maintenance facilities capable of servicing Nimitz-class carriers at PSNS with that SSBN basing (R03:21).
- Table row: "Nuclear Deterrence, CVN Maintenance"; "SSBNs, Nimitz-class CVNs (maintenance)" (R03:29).
- R03:21's nuclear-weapons-facility sentence is deliberately not extracted (seed:25).

**Position.** Approx 47.6N, -122.7 (approx, verify).
- In-game: the stock "Seattle" city point and KSEA airport (47.449,-122.309) are about 15-25 NM away.
- There is no installation unit. The nearest proven sea point is about 990 NM away (installations lens; not the Bell Systems point). The builder pool fails at 980 NM (scope B1).
- Natural Earth reads Hood Canal as land (scope B4), so the placement status is "Natural Earth land, pending P8".

**Forces.**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:kitsap_ssbn_context | abstract | Strategic submarine force: bare fact only | usn_ssbn_ohio (inventory: for broad strategic presence only) | exact | 0 placed; roster context, no patrol mechanics | R01:17, R03:21, R03:29 (stated for Kitsap as a whole) |

The carriers are allocated in the PSNS package.

**Support services.** None at umbrella level.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usp_kitsap_bremerton_psns | parent of the Bremerton/PSNS component (equivalence inferred) | source | R01:17, R03:21 |
| usp_kitsap_bangor | parent of the Bangor component | source | R01:17, R03:21 |

**Routine activity.** None. No SSBN patrol or deterrence modelling.

**Checks.**
- Neither report says which component bases the SSBNs. Bangor is the commonly reported answer; check it.
- NS Bremerton and PSNS are named separately, so treating them as one place is the register's inference.
- R01:17 and R03:21 repeat each other.
- No nuclear storage, handling or employment detail (seed:25).

**Gaps.**
- No named unit.
- Water validation is pending.
- NAS Whidbey Island and NS Everett: PROPOSED backlog addition (inventory lookup hint, not in R01-R03).

---

### usp_kitsap_bremerton_psns - Puget Sound Naval Shipyard (Naval Base Kitsap - Bremerton)

**Identity.**
- Aliases PSNS, "Kitsap-Bremerton" (R03 carrier table) and "former Naval Station Bremerton". Per fidelity, the colocation is inferred, not stated by R01 or R03.
- United States Navy, host United States.
- node_kind shipyard_maintenance; populate_policy **populate**.

**Role (SOURCE CLAIM).**
- Drydock and maintenance facilities capable of servicing Nimitz-class carriers at PSNS (R03:21).
- Kitsap combines massive drydock facilities with SSBN basing; PSNS is unnamed in R01 (R01:17, added claim).
- "CVN Maintenance"; "Nimitz-class CVNs (maintenance)" (R03:29, added claim).
- R02:17, reworded: PSNS is listed among the sites into which "major logistical operations are integrated". No DLA centre is named or asserted.
- Nimitz "operates out of Kitsap-Bremerton" (R03:48), with the hull row at R03:54. Reagan's row is R03:62.

**Position.** Approx 47.6N, -122.6 (Sinclair Inlet, Bremerton; approx, verify).
- In-game: KSEA and the Seattle city point are about 15 NM away. There is no unit, and the nearest proven sea point is about 990 NM away (installations lens).
- Narrow Puget Sound inlets may read as land in Natural Earth 1:10m. Sinclair Inlet itself is untested, so this waits on P8; pier-side land units are the fallback.

**Forces.**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:cvn68_nimitz | reserve | CVN, non-ready (pre-decommissioning), no air wing, dormant | usn_cvn_nimitz_2025 Variant1 "CVN-68 Nimitz" (ServiceDate 2025 to 2027) | exact | 1 | R03:48, R03:54 |
| asset:usp:cvn76_ronald_reagan | servicing_maintenance | CVN in a drydock availability, not combat-ready, static, no air wing | usn_cvn_nimitz Variant9 "Ronald Reagan CVN-76" (legacy 1980s-pattern unit; usn_cvn_nimitz_2025 and the 2027s_adou unit lack CVN-76) | proxy (label "CVN-76, legacy-fit unit") | 1 | R03:62 |
| asset:usp:psns_yard_scenery | resident_at_base | Shipyard scenery; provides no service | US_Los_Alamos (labelled "PSNS drydock stand-in (AFDB-7 model)"; OilRig subtype, Role=Target, ServiceDate 1961 to 1991) + warehouses_2 (Nation=usa) | proxy | 1 cluster | design (R03:21 drydock role) |

**Support services.**
- **Repair:** not established.
  - The shipyard role is narrative only. No unit file defines repair.
  - Task Force Mode repair flags work only between missions. The changelog mentions "rearm and repair trigger actions", but no mission uses them, so they are a candidate test.
  - By extension of plan:81 (service ships and airfields give a reason to return), the shipyard could serve as a return node. That is a design choice.
- **Ship ammunition:** none. nv_pt_boats_docks and nv_pt_boats_docks_small are unlimited and not recommended.
- **Aircraft:** none.
- **Supplier restocking and fuel:** not established.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usp_kitsap_naval_base_kitsap | parent (Bremerton = PSNS inferred) | source | R01:17, R03:21 |
| usp_kitsap_bangor | sibling component | source | R01:17, R03:21 |
| usp_sandiego_naval_base_san_diego | Nimitz homeport shifts and deployments through San Diego | source for the activity (R03:48 names the cities "Kitsap-Bremerton" and "San Diego"). The node mapping is authored: Bremerton = PSNS is inferred, and the San Diego berth is unresolved | R03:48, R03:54 |
| wpac_yokosuka_naval_base | Reagan's former forward-deployed role | source for the role (R03:38: George Washington assumed the Yokosuka role from Reagan). The node mapping is authored: R03:62 gives Reagan's home port only at city level ("Kitsap-Bremerton"), and Bremerton = PSNS is inferred | R03:38 (hand-over), R03:62 (home port) |
| usg_dla_distribution_network | major logistical operations integrated (no centre asserted) | source | R02:17 |
| usa_norfolk_naval_station_norfolk | possible Nimitz inactivation move (public reporting, not R01-R03) | authored (CHECK only) | n/a |

**Routine activity (proposed).**
- Nimitz and Reagan stay dormant.
- An optional authored Nimitz homeport-shift transit to San Diego (R03:48) is not implemented.
- Puget Sound civilian traffic: civ_fv_crabboat (US); civ_ms_mairangi_bay US variants and civ_ms_car_carrier_a calling at Seattle/Tacoma (authored).
- There is no ferry hull, so the Puget Sound ferries cannot be represented.

**Checks.**
- Public reporting had Nimitz inactivating and moving to Norfolk around 2026. If the scenario date is after that move, remove Nimitz from this package and allocate it once in the Atlantic package. If the world is dated 2028, Variant1 is out of date. See the region-wide scenario-date CHECK in the NB San Diego package.
- Reagan's status is dated.
- Only the legacy unit carries CVN-76, so it needs a visible label.
- The Bremerton/PSNS merge is an inference.
- plan:81 misattribution corrected.
- Editor re-saves can drop empty CustomAirGroup lines and revive the broken shipped wing. Verify after every round-trip.

**Gaps.**
- No shipyard or drydock function and no repair.
- No named PSNS unit. US_Los_Alamos carries the wrong name and era, so it is labelled.
- No tugs.

---

### usp_kitsap_bangor - Naval Base Kitsap - Bangor

**Identity.**
- Alias "former Naval Submarine Base Bangor". United States Navy, host United States.
- node_kind naval_base; populate_policy **context_only**.
- Sources R01:17 and R03:21 (the merger sentence only).

**Role (SOURCE CLAIM).** Bangor is named only as one of the two bases merged into Kitsap (R01:17, R03:21). The reports give it no role of its own. The SSBN basing claim covers Kitsap as a whole and is recorded at the umbrella (asset:usp:kitsap_ssbn_context).

**Position.** Approx 47.7N, -122.7 (Hood Canal; approx, verify).
- In-game: KSEA is about 23 NM away.
- Natural Earth 1:10m reads Hood Canal (47.73,-122.72) as land (scope B4). Use pier-side land units plus an offshore anchorage, or a water override after P8.

**Forces.** None placed. A conventional harbour-security presence is a design option, not a claim, but the inventories verify no suitable US patrol craft (no Mark VI). The SSBN context is held at the umbrella and not duplicated here.

**Support services.** None.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usp_kitsap_naval_base_kitsap | parent | source | R01:17, R03:21 |
| usp_kitsap_bremerton_psns | sibling component | source | R01:17, R03:21 |

**Routine activity.** None.

**Checks.**
- That Bangor is the SSBN component is unverified.
- No nuclear storage or handling detail (seed:25; plan:43 is an analogy only).

**Gaps.** No unit, and water validation is pending.

---

### usp_dla_san_joaquin - DLA Distribution San Joaquin

**Identity.**
- US Defense Logistics Agency, host United States.
- node_kind distribution_depot; populate_policy **abstract_logistics_only**.
- Sources R02:15 and R02:30, plus two added claims: R02:15's 17-centre network and R02:17's CONUS-hub role.

**Role (SOURCE CLAIM).**
- In California. One of the massive primary hubs anchoring the CONUS network; with Susquehanna it manages "the bulk of cross-country and international materiel routing" (R02:15).
- Table row: "Primary West Coast CONUS distribution hub" (R02:30).
- R02:15: the CONUS network has "17 major DLA Distribution centers that serve as the origin points for global military supply chains".
- R02:17: "these CONUS hubs represent the ultimate source of replacement airframes, deep-level maintenance components, and bulk munitions".
- Per fidelity, "Pacific resupply origin" is an authored label.

**Position.** Approx 37.7N, -121.4 (Tracy/Lathrop area; approx, verify). It is inland, about 45 NM from the KSFO world-database airport and about 370 NM from NB San Diego. There is no in-game evidence, and a tactical representation adds little.

**Forces.**

| Asset | Allocation | Role | Unit ids | Outcome | Scenario qty | Source basis |
|---|---|---|---|---|---|---|
| asset:usp:dla_san_joaquin_abstract | abstract | Abstract West Coast distribution origin | (optional marker only: warehouses_1, warehouses_3, tgt_fueltanks_large, with Nation=usa and a NameOverride) | proxy (marker, not placed) | 0 placed | R02:15, R02:30 |

**Support services.**
- No in-game supply mechanism: the depot units have no function, or only land-unit supply.
- The R02:17 "bulk munitions" role is expressed only through finite relief assets (asset:usp:sd_relief_cargo_1, authored).
- Fuel, repair and restocking are not established.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| usg_dla_distribution_network | parent network | source | R02:15 |
| usa_dla_susquehanna | paired primary hub | source | R02:15 |
| usp_sandiego_naval_base_san_diego | West Coast resupply origin (releases sd_relief_cargo_1) | authored | R02:30 (role only) |
| cpac_pearl_harbor_dla_distribution / wpac_guam_dla_distribution | Pacific resupply chain | authored ("Pacific" is our inference) | n/a |

**Routine activity (proposed).** An abstract dispatch trigger releases the finite relief asset from San Diego. Optionally, civ_ms_roro_c US variants (RRF names, no supply system) can show visual sealift.

**Checks.**
- DLA centre counts and scope are a priority check (seed:23); the 17-centre CONUS count is unverified.
- R02:17 states co-location only generically.

**Gaps.**
- No US depot unit and no distribution mechanic.
- No C-17 or C-5. The C-141B stand-in is date-gated to 2006.
- The RRF ro-ros are visual only.
