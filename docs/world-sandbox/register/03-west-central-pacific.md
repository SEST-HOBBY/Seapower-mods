<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Region: Western and Central Pacific forward basing and distribution

**Summary.** The region has six nodes from R01-R03. Three are populated: Yokosuka Naval Base, Naval Base Guam (Apra Harbor) and Andersen AFB. Three are abstract logistics nodes, following the register policy abstract_logistics_only: DLA Distribution Yokosuka, DLA Distribution Guam and DLA Distribution Pearl Harbor. The reports name exactly one physical asset in this region: USS George Washington (CVN 73), forward deployed and home-ported at Yokosuka (R03:38, R03:59). Every other force below is a labelled SCENARIO CHOICE. Guam naval, Andersen and DLA Guam stay as three separate packages (plan:34; register).

**Allocated in this region (SCENARIO CHOICE; each asset allocated once)**
- **Carrier:** George Washington, underway on patrol with a 31-aircraft embarked wing. 29 aircraft map exactly; 2 are labelled MH-60S stand-ins.
- **Surface combatants (6):**
  - 1 cruiser and 2 destroyers escorting George Washington;
  - 1 destroyer in maintenance at Yokosuka;
  - 1 destroyer on local patrol off Yokosuka;
  - 1 LCS escorting arrivals at Guam.
- **Submarines:** 2 attack submarines at Guam, one in maintenance and one on patrol.
- **Auxiliaries (5):**
  - 2 T-AKE stand-ins, one with the George Washington group and one at Apra;
  - 1 T-AO stand-in at Yokosuka;
  - 1 Algol-class sealift ship inbound to Guam;
  - 1 MSC T-AOT tanker arrival.
- **Andersen:** 4 B-52H and 2 KC-135, a rotational detachment.
- **Abstract, register only:** Seventh Fleet HQ, Marine expeditionary forces, and the three DLA centres.

**Referenced here but allocated elsewhere**
- **USS Abraham Lincoln (CVN 72):** the US Pacific region places it underway in the Western Pacific (R03:50, R03:58). It may visit or rendezvous here.
- **USS Ronald Reagan (CVN 76):** handed the Yokosuka role to George Washington (R03:38). Its home port is Kitsap-Bremerton and it is in maintenance (R03:62). It belongs to usp_kitsap_bremerton_psns.

**Region-wide checks**
- **Duplicate hulls:** the SEST auxiliary stand-ins have only four named hulls per class:
  - T-AKE 1, 2, 6 and 11;
  - T-AO 187, 189, 193 and 204.

  This region uses two T-AKEs and one T-AO. The world register must make sure no hull variant is used twice across regions, and no squadron livery appears on two carriers. Cruiser and destroyer hull variants are left to be chosen at build.
- **Stand-in labels:** every proxy or missing_fit unit that would otherwise display a real installation or hull name is to carry a visible stand-in label: "Yokosuka Naval Base (scenery stand-in)", "Naval Base Guam (scenery stand-in)", "Andersen AFB (generic airfield stand-in)", and usn_hh-60 "MH-60S stand-in". The T-AKE and T-AO labels are not yet confirmed (see below). guam_taot_arrival (civ_ms_sealift_pacific) has the generic class name "Medium Tanker,Merchant", but its named US "Sealift" variants display real MSC hull names (Variant1 "MV Sealift Pacific Ocean T-AOT-168" to Variant9 "MV Sealift Antarctic T-AOT-176"; vanilla and 3432592449 language_en/vessel_names.ini, key-level merge). CHECK in the editor: place the Default variant (no hull number) or add a NameOverride "<hull name> (T-AOT stand-in)".
  - The SEST T-AKE and T-AO named variants display real hull names (SEST language_en/vessel_names.ini, for example Variant1 "T-AKE 1 USNS Lewis and Clark" and "T-AO 187 USNS Henry J. Kaiser"). "(stand-in)" appears only in the Default class name.
  - CHECK in the editor that the "(stand-in)" class name is visible when a named variant is chosen. If it is not, add a NameOverride such as "<hull name> (T-AKE stand-in)" or "<hull name> (T-AO stand-in)".
- **Bomber pool (settled here):** the SEST airbase_raaf_tindal default [AirGroup] carries dts_b-52h=Squadron1,4 and usaf_stratotanker=Squadron1,2 (SEST land_units/airbase_raaf_tindal.ini lines 39 and 41). Squadron1 "2nd Bomb Wing" is the only operational B-52H livery.
  - Andersen owns the Pacific bomber task force (asset:wpac:andersen_b52, 4 B-52H) and the only KC-135 pair (asset:wpac:andersen_kc135).
  - Tindal's world placement (asset:ausio:tindal_base, Australia region) uses a CustomAirGroup without the shipped B-52H x4 and KC-135 x2.
  - The wing name repeats only on separately counted detachments. World B-52H total: 8 airframes, 6 placed (Andersen 4 at base; Diego Garcia 2, asset:ausio:dg_b52_det; Tindal 2 in reserve, not placed, asset:ausio:tindal_bomber_det). World KC-135 total: 2, both at Andersen.
  - A later rotation moves an allocation; it never copies one.
- **Support:** ship-to-ship support is limited to finite ammunition in allocated auxiliaries. Aircraft turnaround relies on flight-deck stores (George Washington FlightDeck_AmmoCapacity 1,200,000; Andersen's airfield_small_1 1,000,000), which is untested. Fuel, repair and restocking are not established.
  - No US-flagged shore unit supplies ships from a finite stock.
  - The RE-power pier nv_pt_boats_docks is effectively unlimited, so it is not recommended unless that is disclosed.
- **Placement:**
  - Andersen has an anchor already proven by a stock mission.
  - Apra and Yokosuka have no proven water: Apra's nearest proven land is 9 NM away and its nearest proven sea point about 186 NM; for Yokosuka the figures are about 43 NM and 206 NM.
  - Apra's inner harbour reads as land in Natural Earth 1:10m (probe P8 pending).
  - The committed coastline extract (100-180E, 25-72S) covers none of these sites.
  - The builder's 60 NM snap to proven positions would misplace both Yokosuka and Apra.
- **Antimeridian:** Pearl Harbor lies at 157.9W, east of 180.
  - Its links to the western Pacific nodes cross the date line and wait on probe P3a and builder fix B7 (scope §1): the spine links to Yokosuka and Guam, and the Apra sealift route.
  - The link to usp_dla_san_joaquin (about 158W to 121W) does not cross 180.
  - Without longitude wrap the builder computes Guam to Pearl as 17,333 NM; the true distance is about 3,305 NM (scope B7).
- **Routine activity:** only proposed. Nothing in this section is implemented or tested.

---

### wpac_yokosuka_naval_base - Yokosuka Naval Base

**Identity.**
- Report name: Yokosuka Naval Base (R01:23, R03:38; R03:59 gives "Yokosuka, Japan").
- Operator: United States Navy. Host nation: Japan.
- Node kind: naval_base. Policy: populate.

**Role: SOURCE CLAIMS**
- HQ of the US Seventh Fleet and "most strategically vital" US overseas naval facility in the Indo-Pacific (R01:23, R03:38). The two lines are almost word for word the same; repetition is not corroboration.
- "The only overseas base globally that permanently hosts a forward-deployed aircraft carrier strike group" (R03:38).
- The group is currently centred on USS George Washington, which took over the role from USS Ronald Reagan (R03:38).
- Carrier table: CVN 73, home port Yokosuka, status "Forward Deployed Indo-Pacific patrol", focus Western Pacific / East China Sea (R03:59).
- Supported directly by DLA Distribution Yokosuka (R01:23). R02:31 adds "Forward supply for US Seventh Fleet", and R02:23 names the centre.
- Operates in tandem with Naval Base Guam (R03:38). This is a working relationship, not colocation.

**REGISTER (editorial).** Register populate_reason: "Main US forward naval base in the Western Pacific, with a named forward-deployed carrier. CSG escorts are not named, so any escort composition is authored." This is the register's reading, not a report claim. Keeping the Seventh Fleet HQ command role abstract (asset:wpac:c7f_hq) is a SCENARIO CHOICE.

**Position.**
- Public location: approx 35.29N 139.67E (approx, verify), on Tokyo Bay.
- No named unit exists.
- Stock world data has points only, with no land unit: asia_ports.ini [Yokohama] 35.4437,139.6380 (about 9 NM away) and [Tokyo] 35.6895,139.6917 (about 24 NM).
- Nearest proven land placements, about 43 NM away:
  - thaad_tel at 35.934,139.300 (user mission "GULF ATTACK .7.7");
  - airfield_us_large at 35.997,139.507 ("NK US ATTACK .7").
- Nearest proven sea placement: about 206 NM away, on the Sea of Japan side (36.55N 135.72E). No water in Tokyo Bay or Sagami Bay has been proven.
- Placement is pending. It needs a land mask or a new coastline extract; do not use the 60 NM snapper.

**Forces and initial allocation**

Everything is a SCENARIO CHOICE unless the Basis column says SOURCE.

| Asset id | Allocation | Role | Unit id (outcome) | Qty | Basis |
|---|---|---|---|---|---|
| asset:wpac:cvn73_george_washington | underway_deployed | Forward-deployed carrier on patrol | usn_cvn_nimitz_2025 Variant6 "CVN-73 George Washington" (exact) | 1 | SOURCE: hull, home port and patrol status (R03:38, R03:59). Starting at sea is a scenario choice. |
| asset:wpac:gw_airwing_core | underway_deployed (embarked) | Strike, EW, AEW and ASW helicopters | usn_fa_18e_rsa, usn_fa_18f_rsa, usn_ea-18g_2020, usn_e-2d, usn_mh-60r (exact) | 29: F/A-18E 12 (Sq1 VFA-27 x6, Sq8 VFA-195 x6); F/A-18F 6 (Sq4 VFA-102); EA-18G 4 (Sq16 VAQ-141); E-2D 3 (Sq9 VAW-125); MH-60R 4 (Sq17 HSM-77) | Scenario choice. No air wing is named. The squadron liveries are a public-knowledge hint, not report content. |
| asset:wpac:gw_airwing_hsc | underway_deployed (embarked) | Logistics and SAR helicopters (MH-60S role) | usn_hh-60 labelled "MH-60S stand-in" (missing_fit) | 2 | Scenario choice. |
| asset:wpac:gw_csg_cg1 | escort | Cruiser, air defence | usn_cg_bunker_hill_vls_2024 (exact; CG-64 Gettysburg V5; revised 10 Oct 2026 from the retired usn_cg_ticonderoga_vls_2025) | 1 | Scenario choice. Escorts are not named. |
| asset:wpac:gw_csg_ddg1 | escort | Destroyer, Flight IIA | usn_ddg_burke_f2a_099_late (exact; hull chosen at build) | 1 | Scenario choice. |
| asset:wpac:gw_csg_ddg2 | escort | Destroyer, Flight IIA | usn_ddg_burke_f2a_089_late (exact; hull chosen at build) | 1 | Scenario choice. |
| asset:wpac:gw_csg_take | support (underway with the group) | Ammunition replenishment ship | usn_take_lewis_clark (proxy; one of T-AKE 1/2/6/11) | 1 | Scenario choice. |
| asset:wpac:yoko_ddg_maint | servicing_maintenance (alongside) | Destroyer in an availability; becomes a finite reserve when released | usn_ddg_burke_f1_054_late (exact; no hangar) | 1 | Scenario choice. |
| asset:wpac:yoko_ddg_patrol | patrol | Sagami Bay / Uraga Channel / Izu approaches | usn_ddg_burke_f2a_091_late (exact; hull chosen at build) | 1 | Scenario choice. |
| asset:wpac:yoko_tao | resident_at_base | Small harbour supplier; physical stand-in for DLA Yokosuka stock | usn_tao_kaiser (proxy; one of T-AO 187/189/193/204) | 1 | Scenario choice, following the register's populate_reason. |
| asset:wpac:yoko_scenery | support (installation) | Pier, warehouse and fuel-farm scenery with no supply, labelled | warehouses_2 + tgt_fueltanks_medium (proxy; Nation=usa, NameOverride "Yokosuka Naval Base (scenery stand-in)") | 1 small cluster, optional | Scenario choice. |
| asset:wpac:c7f_hq | abstract | Seventh Fleet HQ (command) | none | register only | SOURCE: R01:23, R03:38. The collection has no fleet command ship. |

Notes on the carrier and escorts:
- **Air wing:** every shipped variant wing on both modern Nimitz units fails, so a mission CustomAirGroup is mandatory.
  - Use usn_fa_18e_rsa, not usn_fa-18e: the winning usn_fa-18e squadrons file defines only VFA-115 and VFA-143.
  - The E-2D liveries are offset from their names: Squadron9 "VAW-125" uses the vaw-126d texture.
  - **No alternate carrier unit.** usn_cvn_nimitz_2025 Variant6 is the only recommended George Washington unit. Its AircraftSupported whitelist is commented out (SEST vessels/usn_cvn_nimitz_2025.ini line 30), so the wing above can embark.
  - usn_cvn_nimitz_2027s_adou is dropped. Its [FlightDeck] AircraftSupported whitelist (mods-source/3606774881/vessels/usn_cvn_nimitz_2027s_adou.ini line 5) omits usn_fa_18e_rsa, usn_fa_18f_rsa, usn_ea-18g_2020 and usn_hh-60, so 24 of the 31 aircraft could not embark; only the E-2D and MH-60R could. A wing for that unit would need usn_fa-18e (VFA-115/143 only) and usn_fa-18f_blk3 (offset liveries), a labelled compromise.
  - The VFA, VAQ, VAW and HSM liveries must not be reused on another carrier anywhere in the world.
- **Escorts:** each cruiser, Flight IIA destroyer and the LCS carries its unit's default MH-60R air group: 2 per cruiser and destroyer, 1 on the LCS.

**Support (separate services)**
- **Ship ammunition, with the carrier group:** asset:wpac:gw_csg_take, usn_take_lewis_clark.
  - [SupplySystem1] TruckSupplySystem, TargetTypes Vessel,Submarine.
  - Pool 550,000 with no MaxAmmoPoints cap; range 1.0 NM; 2 targets; supplier up to 13 kn, receiver up to 16 kn.
  - Categories: Harpoon 48, AirTorpedo 72, ALWT 40, SEST_LandAttack 48, SEST_LongRangeSAM 56.
- **Ship ammunition, at Yokosuka:** asset:wpac:yoko_tao, usn_tao_kaiser.
  - Pool 80,000, cap 2,000 points, range 0.5 NM.
  - Categories: Harpoon 8, AirTorpedo 16.
  - It refuses Tomahawk (4,350 points) and SM-6 (8,000 points).
  - No finite US-flagged shore supplier exists.
- **Aircraft turnaround and ordnance:** the George Washington flight deck.
  - Capacity 85; FlightDeck_AmmoCapacity 1,200,000 (Phoenix 84, Harpoon 48, AirTorpedo 80, AdvancedARM 64).
  - Topping up flight-deck magazines at sea is not established. Repeat sorties are untested.
- **Supplier restocking:** not established. Pools deplete and nothing refills them. Relief comes only from other finite allocated ships: asset:wpac:guam_take and asset:wpac:sealift_algol1.
- **Fuel:** not established. Ships have no fuel keys, and there is no modern carrier-capable tanker.
- **Repair:** not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| wpac_yokosuka_dla_distribution | Supported by the DLA centre | source | R01:23; R02:31; R02:23 |
| wpac_guam_naval_base_apra_harbor | Operates in tandem (working relationship) | source | R03:38 |
| usp_kitsap_bremerton_psns | Reagan handed over the role; Reagan now at Kitsap-Bremerton in maintenance | source | R03:38 (handover); R03:62 (status). Bremerton = PSNS is a register inference. |
| US Pacific region: USS Abraham Lincoln | Visitor or rendezvous; not allocated here | authored | R03:50, R03:58 |
| Western Pacific / East China Sea | Patrol focus of George Washington | source | R03:59 |
| Philippine Sea patrol box (about 30N 137E) | Carrier group patrol route; geometry pending | authored | none |
| jpn_atsugi_naf | Geographic neighbour, about 12 NM; no reported relationship | authored | none |

**Routine activity (PROPOSED, not implemented)**
- **Carrier patrol cycle:** the group (carrier, cruiser, 2 destroyers, T-AKE) patrols the Philippine Sea box and returns to Yokosuka to service. Routes must last longer than the session.
- **Replenishment rendezvous:** the T-AKE meets the escorts. This is the test of transfer, category gating and depletion.
- **Local patrol and reserve:** yoko_ddg_patrol patrols the Sagami Bay approaches. yoko_ddg_maint stays dormant until a release trigger.
- **Lincoln:** the US Pacific region's Lincoln group may visit. Any transfer from this region's suppliers comes out of their stock.
- **Civilian traffic** (scenario population, not a researched schedule):
  - Tokyo Bay merchants: civ_ms_car_carrier_a, civ_ms_bulk and civ_ms_ritina (Japan variants); civ_ms_mairangi_bay (Japan variants), labelled as a period stand-in.
  - Fishing craft: civ_fv_fishingboat_c, civ_fv_fishingboat_d, civ_fv_sterntrawler_d.
  - Airliners: civ_a330 (Japan liveries) and civ_a320, flying set airways.
  - Avoid civ_ms_freighter_b and civ_ms_freighter_d: they carry live, effectively unlimited supply blocks.

**Checks**
- **Carrier date:** "currently centered around USS George Washington" is undated. This is a seed:23 priority check; confirm at the scenario date.
- **Unnamed forces:** no escorts, air wing or other ships are named. All of them are authored.
- **Fidelity check 2:**
  - Cite R03:38 for the Reagan handover and R03:62 for Reagan's home port and status.
  - The Guam tandem link is a relationship, not colocation.
  - Add R02:23 to the DLA citation.
- **Air wing ids:** re-check every CustomAirGroup id at build. The wing is valid only on usn_cvn_nimitz_2025 (whitelist commented out); confirm embarkation in the editor.
- **Duplicate hulls:** see the region-wide check.
- **Placement:** there is no proven water. The snapper would move a land unit to about 36.0N 139.4E.
- **Validation status:**
  - Source claims: recorded.
  - Unit ids: re-resolved with find_unit_file on this branch.
  - Placement, runtime activation and save/load: untested.

**Gaps**
- No named Yokosuka unit, and no US Pacific port scenery.
- No fleet command ship hull.
- Carrier aviation: no MH-60S or HSC squadron, no C-2A, no CMV-22B and no MQ-25. The only carrier tanker, usn_ka-3b, is Cold War era.
- No finite US-flagged shore supplier. No repair, ship fuel or restocking mechanics.
- JMSDF host-nation presence at Yokosuka is not described in R01-R03, so it is not populated.

---

### wpac_yokosuka_dla_distribution - DLA Distribution Yokosuka

**Identity.**
- Operator: US Defense Logistics Agency. Host nation: Japan.
- Node kind: distribution_depot. Policy: abstract_logistics_only.

**Role: SOURCE CLAIMS**
- Supports Yokosuka Naval Base directly (R01:23).
- A key overseas land-based hub in Japan. With Guam and Pearl Harbor it forms the Indo-Pacific Command's "logistical spine" (R02:23).
- Table entry: "Forward supply for US Seventh Fleet" (R02:31).
- One of the "network of seven overseas (OCONUS) distribution hubs" (R02:21; fidelity check 3 says this is not yet cited).

**REGISTER (editorial).** Register role: distribution (register populate_reason). This is the register's reading, not a report claim.

**Position.** Not placed. No report gives its site relative to the naval base.

**Forces**

| Asset id | Allocation | Role | Unit id (outcome) | Qty | Basis |
|---|---|---|---|---|---|
| asset:wpac:dla_yokosuka | abstract | Distribution centre | none | none placed | SOURCE: R01:23, R02:23, R02:31. Its physical stock is represented by asset:wpac:yoko_tao and asset:wpac:gw_csg_take (scenario choice). |

A marker built from warehouses_1 or warehouses_3 would be a proxy and is not recommended: those units have no supply function.

**Support.** Abstract. The node has no service of its own; ammunition availability is the finite stock of the named Yokosuka-package ships. Fuel, repair and restocking are not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| wpac_yokosuka_naval_base | Forward supply for the Seventh Fleet | source | R01:23; R02:31 |
| wpac_guam_dla_distribution | Indo-Pacific logistical spine | source | R02:23 |
| cpac_pearl_harbor_dla_distribution | Indo-Pacific logistical spine; crosses the antimeridian | source | R02:23 |
| usg_dla_distribution_network | Member of the seven OCONUS hubs | source | R02:21, R02:23 |
| usp_dla_san_joaquin | CONUS West Coast origin of Pacific resupply | authored | R02:30 calls it the West Coast hub; "Pacific" is authored (fidelity check 3) |

**Routine activity.** None at this node. Arrivals are allocated ships on the Guam package.

**Checks**
- **Centre counts (seed:23):** R02:21 says seven OCONUS hubs, but R02:23 names only six.
- **Site:** not stated, so colocation with the base is not asserted.
- **Repetition:** R01:23 and R02:23/R02:31 repeat the Yokosuka link; that is not corroboration.

**Gaps.** No DLA or depot unit with a supply function exists in the collection. Distribution links are register metadata, not an engine mechanic.

---

### wpac_guam_naval_base_apra_harbor - Naval Base Guam (Apra Harbor)

**Identity.**
- Operator: United States Navy. Host: United States (Guam).
- Node kind: naval_base. Policy: populate.

**Role: SOURCE CLAIMS**
- Situated in Apra Harbor, next to the "adjacent" Andersen AFB, and operates in tandem with Yokosuka (R03:38).
- An "unsinkable logistical and aviation hub in the Western Pacific", supported by DLA Distribution Guam (R01:23). R03:38 repeats the same phrase for "Guam"; repetition is not corroboration.
- Island-level (Guam): allows rapid dispatch of naval assets, strategic bombers and Marine expeditionary forces to the South China Sea, the Taiwan Strait and the Korean Peninsula (R03:38). The sentence's subject is Guam, not the naval base; the bombers are routed to Andersen as an authored link.
- Island-level (Guam): as sovereign US territory, Guam is not constrained by host-nation basing agreements (R03:38).
- R03:172 (a joint statement about Diego Garcia and Guam, at island level):
  - the two places "provide massive operational reach for United States bombers and surface fleets". The surface-fleet half is recorded on this naval node (joint with Diego Garcia; island-level); the bomber half is routed to Andersen as an authored link;
  - Guam needs constant resupply over vulnerable sea lines of communication. Two simulation-guidance ideas follow: mining the approaches to Apra, and harassment of logistics shipping by conventional submarines from Yulin.

**REGISTER (editorial).** Register role: forward naval logistics port (register populate_reason). This is the register's reading, not a report claim.

**Position.**
- Public location: approx 13.44N 144.65E (approx, verify).
- No named unit exists.
- Nearest proven land placement: 9 NM away. Stock "All Your Guam Belong to Us (Red Side)" places airfield_small_1 Variant1 at 13.296,144.701; the Blue side puts it at 13.298,144.712.
- Nearest proven sea placement: about 186 NM away (the stock "Showdown off Guam Blue 1985" surface group, near 15.7N 142.4E).
- The inner harbour (13.44, 144.66) reads as land in Natural Earth (scope B4; probe P8 pending). The fallback is pier-side land units plus an offshore anchorage west of the harbour entrance, which still needs validating.
- Do not use the snapper: it would pull pier units to the south-central airfield point.

**Forces and initial allocation**

Everything is a SCENARIO CHOICE unless the Basis column says SOURCE.

| Asset id | Allocation | Role | Unit id (outcome) | Qty | Basis |
|---|---|---|---|---|---|
| asset:wpac:guam_take | resident_at_base (Apra anchorage) | Forward-staging munitions stock; physical stand-in for DLA Guam | usn_take_lewis_clark (proxy; a different T-AKE variant from gw_csg_take) | 1 | Scenario choice, following the register's populate_reason. |
| asset:wpac:guam_ssn1 | servicing_maintenance (alongside) | Attack submarine in an availability; finite reserve | usn_ssn_virginia_block2_2026 (exact; hull chosen at build) | 1 | Scenario choice (public-knowledge hint; the reports name no submarines). |
| asset:wpac:guam_ssn2 | patrol | Western sea-lane approach; screen against diesel submarines | usn_ssn_los_angeles_flt3_2026 (exact; the unit starts at SSN-753) | 1 | Scenario choice; the activity reflects R03:172. |
| asset:wpac:guam_lcs1 | escort | Escorts inbound logistics shipping through the Apra approaches | usn_lcs_freedom_suw_late (exact; surface-warfare package only, no mine-countermeasures module) | 1 | Scenario choice; the class choice is authored. |
| asset:wpac:sealift_algol1 | transit (inbound; spawns west of 180, around 15N 170E) | Finite sealift relief that can also rearm, slowly | usn_takr_algol (exact; Variant1 Algol, 3 Denebola, 6 Regulus or 7 Capella only) | 1 | Scenario choice; reflects R03:172 "constant resupply". |
| asset:wpac:guam_taot_arrival | transit | MSC tanker arrival delivering DLA fuel (visual only) | civ_ms_sealift_pacific (proxy; class name "Medium Tanker,Merchant"; named "Sealift" variants show real hull names, label CHECK) | 1 | Scenario choice. |
| asset:wpac:apra_scenery | support (installation) | Pier, warehouse and fuel-farm scenery labelled "Naval Base Guam (scenery stand-in)", with no supply | warehouses_2 + tgt_fueltanks_medium (proxy; Nation=usa, NameOverride "Naval Base Guam (scenery stand-in)") | 1 small cluster | Scenario choice. |
| asset:wpac:guam_marine_exped | abstract | Marine expeditionary forces | none | not placed | SOURCE: R03:38. Ground forces are not represented. |

Notes on the auxiliaries:
- **guam_take:** it serves both Vessel and Submarine targets, so it also rearms the Guam submarines. Once it is spent, only the inbound sealift ship can take over. If T-AKE variants run out world-wide, the fallback is civ_ms_c8 in a US "Cape" variant: a proxy with a 300,000 pool and an 8,000-point cap that transfers only at 8 kn or less.
- **Algol variants:** Variants 2, 4, 5 and 8 end in 2025.
- **Spawn point:** the sealift ship starts west of 180 on purpose, so it does not depend on probe P3a.
- **T-AOT tanker:** it carries a small live ammunition block (AirTorpedo 8; pool 40,000, cap 2,000). It is US-flagged, not neutral.

**Support (separate services)**
- **Ship and submarine ammunition:** asset:wpac:guam_take, usn_take_lewis_clark, with the same supply block as gw_csg_take:
  - pool 550,000, no cap, range 1.0 NM, TargetTypes Vessel,Submarine;
  - categories Harpoon 48, AirTorpedo 72, ALWT 40, SEST_LandAttack 48, SEST_LongRangeSAM 56.
- **Relief supplier:** asset:wpac:sealift_algol1, usn_takr_algol.
  - Pool 500,000, no cap, 45 points per second, range 0.5 NM; supplier up to 8 kn, receiver up to 12 kn.
  - Categories: Harpoon 40, AirTorpedo 48, ALWT 24, SEST_LandAttack 32, SEST_LongRangeSAM 32.
- **Submarine torpedo and strike rounds:** whether they pass the category gate must be verified (integration/replenishment/README.md).
- **Submarine tender:** not allocated. The only proxy, usn_ae_kilauea, has variants whose ServiceDates end between 1980 and 1998, so it is likely filtered out of a 2026 mission.
- **Supplier restocking:** not established. The Algol cannot refill guam_take's pool; it is a second finite supplier.
- **Fuel:** not established. The T-AOT arrival is visual only.
- **Repair:** not established. US_Los_Alamos (AFDB-7, 1961|1991) is a target object only.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| wpac_guam_dla_distribution | Supported by the DLA centre | source | R01:23 (also R02:23, R02:32) |
| wpac_yokosuka_naval_base | Operates in tandem | source | R03:38 |
| wpac_guam_andersen_afb | Separate aviation site on the same island ("adjacent"; not a placement instruction) | source | R03:38 |
| South China Sea, Taiwan Strait, Korean Peninsula | Dispatch destinations | source | R03:38 |
| Approaches to Apra Harbor | Mining as simulation guidance | source | R03:172 |
| Sea lines of communication to Guam | Vulnerable resupply route | source | R03:172 (joint with Diego Garcia) |
| chn_hainan_yulin_naval_base | Threat link: diesel submarines harassing logistics shipping (simulation guidance; "US shipping" is an inference); about 2,045 NM | source | R03:172 |
| cpac_pearl_harbor_dla_distribution | Sealift relief route; crosses the antimeridian (P3a) | authored | none |
| usp_dla_san_joaquin | CONUS origin of the sealift | authored | none |
| glob_us_afloat_prepositioning_fleet | Prepositioning loiter areas are unnamed; Guam is not named as an anchorage; nothing allocated here | authored | R01:23, R02:25 |
| US Pacific region: USS Abraham Lincoln | Possible replenishment visitor; any transfer comes out of guam_take's stock | authored | R03:58 |

**Routine activity (PROPOSED, not implemented)**
- **Submarine patrol:** guam_ssn2 patrols west of Guam along the sea lane (about 13-16N, 138-143E; to be validated).
- **Sealift arrival:** sealift_algol1 arrives from the east, and guam_lcs1 meets it about 50 NM out.
- **Relief run:** guam_take sails to a Philippine Sea rendezvous (about 20N 138E) to relieve the George Washington group once gw_csg_take is spent.
- **Fuel delivery:** guam_taot_arrival makes a periodic visual delivery.
- **Civilian traffic:**
  - Ships: civ_ms_mairangi_bay (US variants, labelled as a period stand-in) as the primary US container ship; civ_fv_crabboat; civ_fv_fishingboat_a Variant3 "Fishing boat US". Avoid Variant5, which is labelled "China" but flagged US.
  - Optional: civ_ms_c7s68 (US container ship) is date-gated. Its winning vanilla variants file has Default ServiceDate=1968|2019 and no per-variant dates, so a 2026+ mission may filter it out; check in the editor before using it.
  - Airliners: civ_a330 in US, Japan and South Korea liveries, and civ_a320 in US and South Korea liveries only (it has no Japan livery), flying set airways.
- **Threat activity under R03:172:**
  - Yulin diesel-submarine harassment is a cross-region authored link; the submarines belong to the China package.
  - Mining cannot be implemented until mine mechanics are verified.
  - No instant-disable rule is applied.

**Checks**
- **"Unsinkable":** the word is rhetorical. No invulnerability rule is applied.
- **Mining:** R03:172 raises mining of the Apra approaches as simulation guidance, not a threat assessment. It describes no US mine-countermeasures function. Any MCM response is a scenario choice and is not modelled (no LCS MCM module, mine mechanics not established).
- **Fidelity check 1:**
  - The R03:172 reach statement is island-level and joint with Diego Garcia. Its surface-fleet half is recorded on this node; bombers are routed to Andersen as an authored link.
  - The R03:38 dispatch claim is marked island-level (Guam).
  - "Harassing logistical shipping" does not say US shipping.
- **DLA claims (fidelity check 1, missing claims):** R02:23, R02:32 and R01:67/R02:77 are recorded on the DLA Guam package.
- **Unnamed ships:** no resident ships are named. The submarines, LCS and auxiliaries are all authored.
- **Placement:** the inner harbour reads as land (P8). Guam is the Blue site in probe P2.
- **Duplicate hulls:** T-AKE and Algol variants must be checked across the world.
- **Dates:** civ_ms_c7s68 (1968|2019) and usn_ae_kilauea (variants ending 1980-1998) are date-gated; check them in the editor at the scenario date.
- **Validation status:** unit ids re-resolved; placement, activation and save/load untested.

**Gaps**
- No named Naval Base Guam unit, and no US Pacific port scenery.
- No submarine tender usable in 2026.
- No Avenger mine-countermeasures ship; the only mine-warfare proxy is the Cold War usn_mso_aggressive, and mine mechanics are not established.
- No hospital ship, salvage ship, tug, ESB/ESD or T-EPF.
- No ship fuel, repair or restocking.
- The coastline extract does not cover Guam.

---

### wpac_guam_andersen_afb - Andersen Air Force Base

**Identity.**
- Operator: United States Air Force. This is implied by the name; R03 does not state it.
- Host: United States (Guam).
- Node kind: air_base. Policy: populate_small.

**Role: SOURCE CLAIMS**
- Named only as the "adjacent" Andersen Air Force Base beside Naval Base Guam (R03:38).
- Island-level claims:
  - Guam allows dispatch of "strategic bombers" (R03:38);
  - "operational reach for United States bombers" (R03:172, joint with Diego Garcia);
  - as sovereign US territory, Guam is "unconstrained by host-nation basing agreements" (R03:38). This bears on access;
  - simulation guidance (R03:172, joint with Diego Garcia): heavily mining the approaches to Apra Harbor, or repeatedly harassing logistical shipping with conventional diesel-electric submarines from Yulin, could "effectively neutralize the combat effectiveness of the forward-deployed forces by starving them of fuel and munitions".
- No aircraft types are named.

**REGISTER (editorial).** Register role: aviation site for the Guam hub, kept separate from the naval base (register populate_reason). This is the register's reading, not a report claim. The split into a naval site and an aviation site comes from the plan (plan:34), not from the reports (fidelity check 2).

**Position.**
- Public location: approx 13.58N 144.93E (approx, verify), on northern Guam about 18 NM from Apra.
- Stock world data: airports.ini [PGUA] 13.583469,144.929158, LargeMilitary, Nation=US.
- Stock placement: "Showdown off Guam Blue 1985" places airfield_small_1 Variant1 with the NameOverride "Andersen AFB".
  - Its offset is RelativePositionInNM=172.5,low,-194.28 from a map centre of 16.83,142.06.
  - In the game's plain-arcminute convention (scope §2.1) that decodes to 13.592,144.935, about 0.6 NM from PGUA.
- CHECK: the us-air-and-land verification computed about 13.59N 145.06E (7.5 NM offshore) by scaling with cos(lat), which the game does not do. Confirm in the editor.

**Forces and initial allocation**

| Asset id | Allocation | Role | Unit id (outcome) | Qty | Basis |
|---|---|---|---|---|---|
| asset:wpac:andersen_airfield | support (installation) | Airfield labelled "Andersen AFB (generic airfield stand-in)" | airfield_small_1 Variant1 (proxy). Alternatives: airfield_us_large, or a named SEST clone of airbase_us | 1 | Scenario choice, following the stock precedent. |
| asset:wpac:andersen_b52 | resident_at_base (rotational) | Bomber task force | dts_b-52h Squadron1 "2nd Bomb Wing" (exact) | 4 | SOURCE at island level: strategic bombers (R03:38, R03:172). Basing at Andersen and the B-52H type are scenario choices. |
| asset:wpac:andersen_kc135 | support | Aerial refuelling | usaf_stratotanker Squadron1, 940th ARW (exact; displays "KC-135A") | 2 | Scenario choice. |

Notes:
- **Airfield:** always use CustomAirGroup. The unit's default air group spawns F-4s, an E-3A and P-3Cs.
  - airfield_us_large displays "Morden Air base", has no FlightDeck_AmmoCapacity and needs a NameOverride.
  - Cloning airbase_us is a design proposal on the integration/raaf-bases pattern. airbase_us declares no FlightDeck_AmmoCapacity and has a malformed default AirGroup line.
  - Reject nato_large_pvo_airbase1: its name reads "Barksdale Air Force Base".
- **Bombers:**
  - Pin a conventional LoadoutVariant.
  - dts_b-52h has no ReceiverSystems, so it cannot be shown to take fuel in the air.
  - The alternative is usaf_b-1b_dts (28th BW or 7th BW), also with a conventional loadout pinned.
  - Do not use the B-2: it needs SeaLifter, which is not subscribed.
  - Ownership is settled (region-wide Bomber pool check): this package owns the 4 B-52H and the 2 KC-135. Tindal's shipped B-52H x4 and KC-135 x2 are excluded by its CustomAirGroup.
- **Tankers:** the alternative is usaf_kc-46a_boom.
- **Fixed defence:** none proposed. R01:23, R03:38 and R03:172 mention no Guam defences. plan:24 allows local defence only where installed assets and evidence support it, and forbids fabricating present-day defensive deployments.

**Support (separate services)**
- **Aircraft turnaround and ordnance:** airfield_small_1 has FlightDeck_AmmoCapacity 1,000,000.
  - The stock precedent sets finite categories in the mission: Harpoon 86, AdvancedARM 16, AirTorpedo 100.
  - Whether B-52H conventional loads draw on these categories is untested, and so are repeat sorties.
- **Aerial refuelling:** RefuelSystem (Aircraft, 5 mi, 1 target), unverified in game.
  - The modded tanker lacks the [AerialRefueling] TankerSystems block, and the B-52H has no receiver.
  - Test against vanilla usaf_kc-10, as a reference only.
- **Restocking:** not established. The usaf_c-141b PlaneCargoSupplySystem is untested and date-gated (1965|2006).
- **Fuel stock and repair:** not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| wpac_guam_naval_base_apra_harbor | Separate naval site on the same island | source | R03:38 ("adjacent") |
| South China Sea, Taiwan Strait, Korean Peninsula | Dispatch destinations for Guam as a whole | source | R03:38 |
| Strategic bombers dispatched from Guam, routed to Andersen | Bomber basing | authored | R03:38, R03:172 (island-level; fidelity check 1) |
| wpac_guam_dla_distribution | Fuel and munitions tether for the detachment | authored | R01:67/R02:77 tether aircraft and ships to their bases' POL and name DLA Guam (simulation guidance); R01:23, R02:23 and R02:32 describe DLA Guam only; Andersen is not named |
| aus_tindal_raaf | Counted bomber pool: Tindal's shipped B-52H x4 and KC-135 x2 are excluded by its CustomAirGroup; its own 2 B-52H (asset:ausio:tindal_bomber_det) are separate airframes in reserve | authored | none |
| io_diego_garcia_nsf | Paired bomber hub in a reach statement | authored | R03:172 groups the two places; no link is stated |
| Sea lines of communication to Guam (Apra approaches; Yulin diesel submarines) | SLOC interdiction affects the detachment's fuel and munitions (simulation guidance; island-level, joint with Diego Garcia; applying it to the detachment is authored) | source | R03:172 |

**Routine activity (PROPOSED, not implemented)**
- **Presence sortie:** 2 of the 4 B-52H fly a sortie toward the Philippine Sea or East China Sea approaches and return. Routes must last longer than the session.
- **Tanker orbit:** only if refuelling passes a test.
- **Airlift:** a candidate airlift arrival would use usaf_c-141b labelled "C-17 (C-141B stand-in)". It is not allocated unless the date filter allows it.
- **Civilian traffic:** civ_a320 and civ_a330 transit Guam airspace on set airways.

**Checks**
- **Operator:** implied by the name, not stated.
- **"Adjacent":** not used for placement.
- **Aircraft:** no types are named; the detachment is authored and rotational.
- **Fidelity check 2:**
  - R01:23 gives the "unsinkable logistical and aviation hub" role to Naval Base Guam; R03:38 repeats it for "Guam". Neither gives the role to Andersen.
  - "Aviation half of the hub" comes from the plan.
  - The missing claims are applied: R03:38 sovereign-territory access and R03:172 interdiction (island-level, in the role and as an R03:172 connection); the R03:38 destinations (connection); R01:23, R02:23, R02:32 and R01:67/R02:77 as the tether through DLA Guam (connection).
- **Placement precedent:** the projection discrepancy described above.
- **Bomber count:** settled. Andersen owns 4 B-52H and 2 KC-135; Tindal's shipped B-52H x4 and KC-135 x2 are excluded. World B-52H total 8 airframes, 6 placed; KC-135 total 2 (see the region-wide Bomber pool check).
- **Defences:** do not add THAAD or Patriot from public knowledge (plan:24).
- **Validation status:** unit ids re-resolved. Placement anchor is proven in stock (0.6 NM). Activation and save/load untested.

**Gaps**
- No named Andersen unit.
- No C-17 or C-5; the C-141B proxy is date-gated.
- No USAF C-130J family; MQ-4C has no US squadron; no RQ-4, USAF F-35A or B-21.
- Modded tankers lack the refuelling block.
- airbase_us clones carry an undocumented default ordnance stock.

---

### wpac_guam_dla_distribution - DLA Distribution Guam

**Identity.**
- Operator: US Defense Logistics Agency. Host: United States (Guam).
- Node kind: distribution_depot. Policy: abstract_logistics_only.

**Role: SOURCE CLAIMS**
- Supports Naval Base Guam (R01:23).
- A key overseas land-based hub in the Marianas, part of the logistical spine (R02:23).
- Table entry: "Forward staging, munitions, and fuel" (R02:32).
- One of the seven OCONUS hubs (R02:21, per fidelity check 3).
- Simulation guidance: if it "runs dry", combat effectiveness must instantly degrade (R01:67, R02:77). The two lines repeat each other.

**REGISTER (editorial).** Register role: distribution (register populate_reason). This is the register's reading, not a report claim.

**Position.** Not placed. No report gives its site on Guam.

**Forces**

| Asset id | Allocation | Role | Unit id (outcome) | Qty | Basis |
|---|---|---|---|---|---|
| asset:wpac:dla_guam | abstract | Forward staging of munitions and fuel | none | none placed | SOURCE: R01:23, R02:23, R02:32. Munitions stock is asset:wpac:guam_take; fuel is the visual asset:wpac:guam_taot_arrival (scenario choice). |

**Support.**
- The node is abstract and has no service of its own.
- The R01:67/R02:77 "instantly degrade" rule is not implemented. Any degradation comes only from the finite stocks of allocated ships.
- Fuel, repair and restocking are not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| wpac_guam_naval_base_apra_harbor | Supports | source | R01:23 |
| wpac_yokosuka_dla_distribution | Logistical spine | source | R02:23 |
| cpac_pearl_harbor_dla_distribution | Logistical spine; crosses the antimeridian | source | R02:23 |
| usg_dla_distribution_network | OCONUS hub | source | R02:21, R02:23 |
| wpac_guam_andersen_afb | Tether for the air detachment | authored | none |
| usp_dla_san_joaquin | CONUS origin | authored | none |

**Routine activity.** None at this node. Arrivals are allocated on the Guam naval package.

**Checks**
- **Instant-disable wording (seed:23):** rhetorical. Test fuel, ammunition and supply separately (plan:83).
- **Repetition:** R01:67 and R02:77 repeat each other; that is not corroboration.
- **Centre counts (seed:23):** seven OCONUS hubs claimed versus six named.
- **Site:** not stated.

**Gaps.**
- No depot or fuel function in the collection.
- Ship fuel is not modelled.
- Fuel stock at airbases is not modelled.

---

### cpac_pearl_harbor_dla_distribution - DLA Distribution Pearl Harbor

**Identity.**
- Operator: US Defense Logistics Agency. Host: United States (Hawaii).
- Node kind: distribution_depot. Policy: abstract_logistics_only.

**Role: SOURCE CLAIMS**
- A key overseas land-based hub in Hawaii. With Yokosuka and Guam it forms the logistical spine of the Indo-Pacific Command (R02:23).
- It is missing from the R02 table (R02:27-34).
- No report describes a Pearl Harbor naval or air installation.

**REGISTER (editorial).** Register role: distribution (register populate_reason). This is the register's reading, not a report claim.

**Position.**
- Not placed.
- Public context only: approx 21.35N 157.95W (approx). This is east of the antimeridian.
- Stock world data: airports.ini [PHIK] Hickam 21.322461,-157.915976; us_cities_pacific.ini [Honolulu] 21.35,-157.91.
- Nearest proven sea placement: about 1,158 NM away (EUROMOD showcase, near the date line).

**Forces**

| Asset id | Allocation | Role | Unit id (outcome) | Qty | Basis |
|---|---|---|---|---|---|
| asset:cpac:dla_pearl | abstract | Distribution centre | none | none placed | SOURCE: R02:23 only. No physical representation; it is the notional origin of the Guam sealift (scenario choice). |

**Support.** Abstract. No services.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| wpac_yokosuka_dla_distribution | Logistical spine; crosses the antimeridian; about 3,350 NM | source | R02:23 |
| wpac_guam_dla_distribution | Logistical spine; crosses the antimeridian; about 3,305 NM | source | R02:23 |
| usg_dla_distribution_network | OCONUS hub | source | R02:21, R02:23 |
| usp_dla_san_joaquin | CONUS origin, about 2,100 NM; does not cross the antimeridian | authored | none |
| wpac_guam_naval_base_apra_harbor | Sealift relief route (P3a) | authored | none |

**Routine activity.** None. Any westbound traffic from Pearl toward Guam or Yokosuka waits on probe P3a; a San Joaquin leg would not.

**Checks**
- **R02 table:** the centre is missing from it; only R02 mentions this node.
- **Centre counts (seed:23):** a priority check.
- **Antimeridian:** the links to the western Pacific nodes (Yokosuka, Guam and the Apra sealift route) cross the date line and wait on P3a/B7. Builder distance maths without wrap gets them wrong (Guam to Pearl computes as 17,333 NM against a true 3,305 NM). The San Joaquin link (about 158W to 121W) does not cross 180.

**Gaps.**
- A Pearl Harbor naval or air installation is not in the reports; it stays on the expansion backlog.
- No named unit.
- Only 9 units have ever been placed in the Hawaii and central Pacific area.
- The coastline extract does not cover Hawaii.
