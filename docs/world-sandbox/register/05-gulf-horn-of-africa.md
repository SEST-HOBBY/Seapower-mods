<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Region: Persian Gulf and Horn of Africa (Djibouti cluster)

### Region summary

**Scope.** Nine register nodes, in this order: NSA Bahrain, Muharraq Airfield and Jebel Ali (Gulf, populate_small); DLA Distribution Bahrain (abstract_logistics_only); and five Djibouti facilities, each kept separate under its own operator: Camp Lemonnier (US), PLA Support Base (China), BA 188/Héron (France), the Japanese base and the Italian base (all populate_small).

**What the sources say.** The source lines are few:
- R03:42: Bahrain HQ, Muharraq aviation, Jebel Ali logistics.
- R02:23: DLA Bahrain.
- R01:49, R01:51, R01:70: the Djibouti cluster and the ROE guidance.
- R03:44: Camp Lemonnier's roles.
- R03:7: Hormuz as a chokepoint.

No report names a ship, aircraft type or squadron, or gives a force quantity (ships, aircraft or squadrons), for any node in this region. The only figures are not force counts: 4,500 personnel at Camp Lemonnier (R01:49) and the PLA base's $590 million cost (R01:51). The only platform-level hint is 'drone operations' at Camp Lemonnier (R03:44), with no types named. **Every force below is therefore a labelled SCENARIO CHOICE.** Each is deliberately small, and none reproduces a real deployment. R01 and R03 frame Camp Lemonnier the same way, which is repetition, not corroboration.

**Referenced, not allocated here.** CVN-71 Theodore Roosevelt is 'transiting to U.S. Central Command' (R03:57) and 'recently departed San Diego to relieve other carriers' (R03:50). It belongs to the US Pacific region package, which assigns its world asset id. This region offers only an authored arrival route and an optional RAS rendezvous.

Other source relationships that bear on this region are also referenced only. Nothing is re-allocated:
- Naval Station Norfolk (usa_norfolk_naval_station_norfolk) is 'the primary force generation hub for the Atlantic, Mediterranean, and Middle Eastern theaters' (R03:19). Eisenhower and Truman 'stage from Norfolk for Atlantic and Middle Eastern deployments' (R03:48).
- NSF Diego Garcia (io_diego_garcia_nsf) is 'a critical node for modeling long-range strike missions into the Middle East and Asia' (R03:40).
- **CHECK:** R03:50 has Roosevelt leaving 'to relieve other carriers in the Central Command area of responsibility', which implies other carriers are already in CENTCOM. None is named, and none is placed in this region.

**Collection constraints that shape every package** (collection inventory, with the verify corrections applied):
- **No named installations.** No node here has a named installation unit. Every site is a labelled proxy on a generic land unit with a per-unit Nation= override. That mechanism is proven: stock Dong Hoi places a Vietnamese-variant unit with Nation=china.
- **Missing content.** There is no Djibouti nation key or flag, no Bahraini or GCC military unit, no French or Italian replenishment ship, no modern JMSDF destroyer and no Kawasaki P-1.
- **Engine services:**
  - ship fuel is not modelled, so oilers pass ammunition only;
  - there is no repair outside Task Force Mode flags;
  - supplier pools cannot be restocked;
  - the only placeable shore supplier for surface ships is nv_pt_boats_docks (TargetTypes=Vessel). nv_pt_boats_docks_small is submarine-only (TargetTypes=Submarine, 3605013271 land_units/nv_pt_boats_docks_small.ini:58). Both are effectively unlimited (AmmoCapacity 9,999,999,999).
- **SCENARIO CHOICE on supply:** no unlimited shore supply is placed anywhere in this region, whether for ships, aircraft or land units. Ship ammunition comes only from three finite afloat suppliers: the T-AKE, the T-AO and the Type 903A.
  - Both HQ markers (NSA Bahrain and the PLA base) use FOB, which has no supply block.
  - nv_headquarters is rejected at both sites. Its [SupplySystem1] is an unlimited TruckSupplySystem for LandUnit targets (3605013271 land_units/nv_headquarters.ini:78-88).
  - Pier markers use ran_pt_boats_docks, which I re-resolved: Port subtype, no supply block.
- **Labelling corrections:**
  - the SEST stand-in auxiliaries (T-AKE, T-AO, Type 903A) are proxy, not exact;
  - usn_p_8a may use USN squadrons 1-14 only;
  - refuelling by the modded KC-135 and KC-46 is unverified, so neither is proposed.
- **Base names.** Renaming a placed land unit is a proven mechanism. The key is TaskforceNLandUnitMNameOverride= inside the mission's [Language_en] block.
  - Stock missions use it: '01A Senkaku Run.ini:5' sets 'Fuzhou Airbase', and 'Showdown off Guam Blue 1985.ini:19' sets 'Andersen AFB'.
  - SEST missions use it too: 'SEST Banda Front Lean.ini:5' sets 'RAAF Base Darwin'.
  - The repo has about 2,700 such keys, and the collection inventory records the same mechanism.
  - Every installation placement below is labelled this way, except the PLA stores scenery (asset:hoa:inst_pla_stores: warehouses_1, tgt_fueltanks_medium), which keeps its generic stock names.
  - A SEST named clone on the integration/raaf-bases pattern (clone airbase_us, write a custom [AirGroup], validate the squadrons) remains an optional long-term step, not a fallback. Such a clone carries no FlightDeck_AmmoCapacity, so one would have to be added.
- **Pier marker labels.** In 3455404959 language_en/land_units_names.ini, ran_pt_boats_docks displays 'RAN base' (Default). Variant1 is 'Fleet Base East (HMAS Kuttabul)' and Variant2 is 'Fleet Base West (HMAS Stirling)'. Variant2 is the Australia region's HMAS Stirling identity.
  - All four placements here (NSA Bahrain, Jebel Ali, Héron and the PLA base) pin VariantReference=Default and carry a mandatory NameOverride.
  - Variant1 and Variant2 must never be used outside the Australia region (one identity per asset; plan:73).

**Positions and engine reach** (scope report §1-2):
- Every coordinate is a public approximation (approx, verify), not report data.
- Measured from a candidate centre of 42N 20E, these nodes lie about 1,750-2,200 NM out (|x| 1,380-2,200 and |z| 925-1,830 file units). That is inside what stock missions and the game-written save already load (3,900-12,000 NM) and far from the date line. GeoPosition= absolute placement is also available.
- The binding limits belong to our builders:
  - the snapper finds no proven point within 60 NM of Bahrain or Djibouti (Bahrain: land 162 NM, sea 86-90 NM; Djibouti: 62-68 NM; Jebel Ali: sea 43 NM);
  - the only coast extract covers 100-180E / 25-72S.
- So placement needs the global land mask (fix_land_positions.py, sea_routes.py) or a new extract (e.g. --box 40 10 60 31).
- Capacity is unmeasured. This region adds 9 warships and auxiliaries, 14 military aircraft (plus 7 embarked helicopters), 13 installation placements and a finite set of neutral traffic.

**Stock world data usable as a route skeleton.**
- vanilla campaigns/sea_points.ini and sea_links.ini give a chain: Bab El Mandeb 12.62N 43.34E - South Aden 11.74N 44.91E - Gulf of Aden 13.50N 50.79E - Al Qibliyah 17.13N 56.60E - Gulf of Oman 23.70N 61.16E - Ras al Kul 25.70N 57.16E - As Salamah (Hormuz) 26.58N 56.54E. A Suez - Bab El Mandeb link also exists.
- Inside the Gulf, sea_links.ini also has [Al Jubayl - As Salamah] and [Minah Al Ahmadi - As Salamah]. Their endpoints are ports.ini [Port Al Jubayl] at 27.054401,49.690686 (about 70 NM from NSA Bahrain) and [Port Minah Al Ahmadi] at 29.043814,48.164590.
  - These two links are the in-Gulf skeleton. Their geometry still needs sea_routes.py validation.
  - sea_points.ini has no point west of As Salamah, so only the short Bahrain and Jebel Ali spurs need authoring.
- Airport [OBBI] 'Bahrain' is at 26.270833,50.633611.

**Sea areas:**
- Persian Gulf, Red Sea and Arabian Sea (R03:42);
- Bab-el-Mandeb (R01:49, R03:44);
- Strait of Hormuz (R03:7; no forward-operating location named);
- US CENTCOM area of responsibility (R03:50, R03:57).

**Backlog retained (not populated):**
- the Kuwait and Oman logistics nodes and any other UAE installations (R03:42; unnamed, plan:46);
- the forward-operating locations that monitor Hormuz (R03:7; none named);
- a split of BA 188 and Héron (R01:51; seed:23);
- Chabelley airfield and other sites known only from outside knowledge (not in R01-R03);
- Djibouti host forces (no unit and no flag);
- a Bahrain clone of OHP Variant16 FFG-24 (its provider, 3403661005, is deprecated).

**Scenario allocation summary (all SCENARIO CHOICE)**

| Package | Military ships | Military aircraft | Installation placements (proxy) | Neutral traffic |
|---|---|---|---|---|
| NSA Bahrain | LCS (escort; alongside only if the pier check passes), DDG (patrol), T-AKE (support) | 3 embarked MH-60R | HQ marker, conditional pier marker | - |
| Muharraq | - | 2 P-8A | small airbase | 4 airliners |
| Jebel Ali | T-AO (transit) | - | pier marker | 2 VLCC, 1 car carrier, 3 dhows |
| DLA Bahrain | - | - | none (abstract) | - |
| Camp Lemonnier | - | 2 MQ-9A, 1 P-8A, 1 KC-130J, 2 HH-60H | small airbase | - |
| PLA Support Base | Type 052D (escort), Type 054A (patrol), Type 903A (support) | 2 embarked helicopters | HQ marker, 2 store units, conditional pier | - |
| BA 188 / Héron | La Fayette FFG (patrol) | 2 Mirage 2000-5F, 1 Puma stand-in, 1 Gazelle (+1 embarked AS565) | small airbase, pier marker | - |
| Japanese base | - | 2 P-3C | small airfield | - |
| Italian base | Thaon di Revel PPA (patrol) | (+1 embarked SH-101A) | warehouses marker | - |
| Region: Red Sea / Bab-el-Mandeb (not a node) | - | - | - | 1 VLCC, 1 bulk carrier, 1 container ship (period stand-in), 2 dhows |

**Regional neutral traffic (Red Sea / Bab-el-Mandeb sea area; not a node, allocated once here). SCENARIO CHOICE.**

| Asset | Unit | Outcome | Allocation | Qty | Notes |
|---|---|---|---|---|---|
| asset:hoa:civ_vlcc_1 | civ_ms_ritina | exact | transit | 1 | Liberia (x33) or Japan (x35) variant. Route Suez - Bab El Mandeb - Gulf of Aden. Candidate escortee for the PLAN group. |
| asset:hoa:civ_bulk_1 | civ_ms_bulk | exact | transit | 1 | Liberia or Greece variant. |
| asset:hoa:civ_box_1 | civ_ms_mairangi_bay | proxy | transit | 1 | Labelled 'container ship (period stand-in)'. A 1970s-80s container design, and no modern boxship exists; the installations lens maps 'container ship' as proxy. UK, US or Germany variant. |
| asset:hoa:civ_dhows_hoa | civ_fv_dhow | proxy | transit | 2 | Egypt or Iraq variant, labelled 'neutral dhow'. No Djibouti, Yemen or Somalia flag exists. |

- None of these units carries a supply block (re-resolved).
- RE-power merchants such as civ_ms_poltava are excluded as traffic because they carry live, effectively unlimited supply blocks.
- Traffic is a finite set of explicitly waypointed units. A [CivilianRoute] spawner would need a bounded MaxUnits and loss accounting.
- Djibouti's commercial port is not a register node, and no host-flagged traffic is possible.

---

### me_bahrain_nsa_bahrain - Naval Support Activity Bahrain

**Identity.**
- Operator: United States Navy (R03:42). Host: Bahrain.
- node_kind: headquarters_command. populate_policy: populate_small.
- Source section: R03:42 only.

**Role.**
- **SOURCE CLAIM:**
  - HQ of US Naval Forces Central Command and the Fifth Fleet, orchestrating operations in the Persian Gulf, Red Sea and Arabian Sea (R03:42);
  - supported by aviation at Muharraq Airfield and by logistics nodes in Kuwait, Oman and the UAE, specifically Jebel Ali (R03:42).
- **CHECK:**
  - the role is HQ only; no piers, ships or services are described;
  - do not attach resupply, ammunition or repair services on the strength of the HQ role (plan:17; fidelity check 1 fix);
  - check pier and port facilities before placing ships;
  - no other place-specific claim exists in R01-R03 (fidelity check 0);
  - R02:23's DLA Distribution Bahrain is not linked to this node by any report.
- **SCENARIO CHOICE:** a passive labelled HQ marker, plus a small authored presence associated with the HQ. It is not a resident assignment.

**Position.**
- Public location approx 26.2N 50.6E (Juffair / Mina Salman, Manama). Approx, verify.
- In-game evidence:
  - no installation unit;
  - stock OBBI 'Bahrain' at 26.270833,50.633611 (vanilla campaigns/airports.ini and cities.ini), about 4 NM away; coordinate reference only;
  - hidden port_pg_dammam (world DB 26.5172,50.1935; its variants wrongly say Nation=Iceland), about 29 NM away; not usable as a stand-in;
  - proven placements: sea 86-90 NM, land 162-165 NM;
  - mission anchors: vanilla user 'Prime Chance' (centre 26.31,52.0; 75 NM) and SEST '01 Threads' / '02 Hot Gulf' (centre 25.87,53.73; 169 NM).
- Placement is pending. It needs the global land mask, because the snapper has no proof within 60 NM.

**Forces (SCENARIO CHOICE; no ship is named in R01-R03)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:me:inst_nsa_hq | FOB | proxy | resident_at_base | 1 | **HQ marker.** Nation=usa, NameOverride 'NSA Bahrain HQ (marker)'. 3600788156, Installation subtype; display name 'Forward Operating Base,FOB'. No AirGroup and no supply, deliberately. nv_headquarters is rejected because it gives unlimited land-unit rearm. |
| asset:me:inst_nsa_pier | ran_pt_boats_docks | proxy | resident_at_base | 1 (conditional) | **Pier marker only.** 3455404959, Port subtype, no [SupplySystem]. Nation=usa, VariantReference=Default (base text 'RAN base'), mandatory NameOverride 'NSA Bahrain pier (stand-in, no shore service)'. Place it only if the pier check passes. The inventory's nv_pt_boats_docks is not proposed: it offers unlimited rearm within 3 NM, which no source supports. |
| asset:me:lcs_1 | usn_lcs_freedom_suw_late (+ usn_mh-60r x1) | exact | escort | 1 ship | **Local escort.** Initial allocation: escort, underway with asset:me:tao_1 on the Jebel Ali - NSA Bahrain leg. Between legs it lies alongside the pier marker only if the pier check passes. If the check fails, it holds at an authored anchorage off Bahrain instead. It is never alongside while escorting. Hulls LCS-17 to 31; SUW package only, no MCM or ASW module. Flight deck 6,000 points. Hull pick is provisional. |
| asset:me:ddg_1 | usn_ddg_burke_f2a_099_late (+ usn_mh-60r x2) | exact | patrol | 1 ship | **Gulf / Hormuz approaches patrol.** 3390330875, #!alias of usn_ddg_burke_f2a_099: flight deck 13,800, AircraftCapacity 2. The SH-60B entry has count 0. Hulls DDG-99 to 107. While underway it is not at the pier. Hull pick is provisional. |
| asset:me:take_1 | usn_take_lewis_clark | proxy | support | 1 ship | **Finite afloat ammunition supplier.** Holds station in the Gulf of Oman. Labelled stand-in on the Kilauea mesh. Variants T-AKE 1/2/6/11; pick provisional, dedupe at merge. |

**Support services**
- **Ship ammunition:** asset:me:take_1, usn_take_lewis_clark [SupplySystem1] TruckSupplySystem:
  - pool 550,000 points with no ceiling, 110 points/s;
  - range 1.0 nm, 2 receivers at a time;
  - supplier speed up to 13 kn, receiver up to 16 kn; targets Vessel and Submarine;
  - categories Harpoon 48, AirTorpedo 72, ALWT 40, SEST_LandAttack 48, SEST_LongRangeSAM 56.

  Transfer, depletion and the negative cases are untested.
- **Shore rearm at NSA Bahrain:** none. The pier marker has no supply.
- **Aircraft turnaround:** embarked helicopters only (DDG flight deck 13,800 points, LCS 6,000). Fixed-wing aircraft belong to the Muharraq package.
- **Supplier restocking:** not established; no unit can refill a supplier's pool.
- **Fuel:** not established. Ship fuel is not modelled.
- **Repair:** not established.

**Connections**
- Source:
  - Muharraq Airfield: aviation support (R03:42);
  - Jebel Ali: logistics node supporting the HQ (R03:42);
  - Persian Gulf, Red Sea and Arabian Sea: Fifth Fleet operating areas (R03:42);
  - CVN-71 Theodore Roosevelt (US Pacific allocation): arrival into the CENTCOM area (R03:50, R03:57); not re-allocated here;
  - usa_norfolk_naval_station_norfolk, reference only: force-generation hub for the Middle Eastern theatre, where Eisenhower and Truman stage for Middle Eastern deployments (R03:19, R03:48). The link is theatre-level; no report names NSA Bahrain. Nothing is re-allocated;
  - io_diego_garcia_nsf, reference only: node for long-range strike missions into the Middle East (R03:40). The link is theatre-level. Nothing is re-allocated.
- **CHECK:** R03:50 sends Roosevelt 'to relieve other carriers in the Central Command area', which implies other carriers are already in CENTCOM. None is named, and none is placed here.
- Authored:
  - DLA Distribution Bahrain: same country; its stock is represented by asset:me:take_1;
  - Camp Lemonnier: a US transit link Hormuz - Gulf of Aden - Bab-el-Mandeb along the stock sea links;
  - optional RAS rendezvous between asset:me:take_1 and the CVN-71 group, only if the US Pacific package sends no supplier with it.
- Backlog: the Kuwait and Oman logistics nodes (R03:42; unnamed).

**Routine activity (proposed, not implemented)**
- asset:me:ddg_1 runs a looped patrol: NSA Bahrain approaches - central Gulf - Hormuz (As Salamah) - back. The inside-Gulf legs follow the stock Al Jubayl - As Salamah link plus a short authored Bahrain spur. Both need sea_routes.py validation.
- asset:me:lcs_1 starts as the escort for asset:me:tao_1 on the Jebel Ali - NSA Bahrain leg. Between legs it goes alongside the pier marker if the pier check passes, and otherwise to an authored anchorage off Bahrain.
- asset:me:take_1 holds a replenishment station near Ras al Kul / Gulf of Oman. It meets ddg_1 and lcs_1 for RAS when their stores run low, with no free top-ups.
- The CVN-71 group (reference only) arrives through the Gulf of Oman.
- Neutral traffic is carried in the Jebel Ali and Muharraq packages, not duplicated here.

**Validation and gaps**
- Unit ids were re-resolved with find_unit_file / winning_file. Placement, runtime activation and save/load are untested.
- Hull picks need a global dedupe.
- Editor round-trips turn Hold into Free; restore_roe.py is the mitigation.
- Gaps:
  - no US Gulf facility unit (none);
  - no Bahrain-flagged military unit (missing_fit);
  - MCM exists only as the Cold War usn_mso_aggressive proxy and is not proposed, because no report names MCM;
  - no hospital ship, tug, salvage ship or EPF (none).

---

### me_bahrain_muharraq_airfield - Muharraq Airfield

**Identity.**
- Operator: not stated. Aviation assets supporting NSA Bahrain operate from the airfield (R03:42), but their nationality is not stated (fidelity check 1 fix). Host: Bahrain.
- node_kind: air_base. populate_policy: populate_small.

**Role.**
- **SOURCE CLAIM:** NSA Bahrain 'is supported by aviation assets operating out of Muharraq Airfield' (R03:42). No types, units or nationality are given.
- **CHECK:**
  - which Bahraini airfield hosts US naval aviation (Muharraq or another);
  - the operator and the host-access terms.
- **SCENARIO CHOICE:** a host-nation airfield with a small labelled US maritime-patrol detachment and neutral airline traffic.

**Position.**
- Public location approx 26.3N 50.6E. Approx, verify.
- In-game evidence: vanilla airports.ini [OBBI] at 26.270833,50.633611 (Role=Civil, Nation=Bahrain, Movements=75, linked to KJFK, EDDF and VIDP). It is a coordinate reference with no land unit.
- Whether the stock civil movements reach a sandbox mission through [BackgroundData] is untested.

**Forces (SCENARIO CHOICE)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:me:inst_muharraq | nato_small_airbase | proxy | resident_at_base | 1 | **Airfield stand-in.** Nation=bahrain, NameOverride 'Muharraq Airfield (stand-in)'. AircraftCapacity 60; FlightDeck_AmmoCapacity 1,500,000. The Cold War default [AirGroup] must be replaced with an explicit CustomAirGroup. A host base with foreign squadrons follows the SEST RAAF Tindal precedent. |
| asset:me:p8a_1 | usn_p_8a | exact | patrol | 1 | Gulf / Hormuz surveillance. Squadron1-14 only. |
| asset:me:p8a_2 | usn_p_8a | exact | resident_at_base | 1 | On the ground in turnaround; swaps with p8a_1. |
| asset:me:civair_obbi_1 | civ_a320 Squadron27 (Gulf Air, Nation=Bahrain) | exact | transit | 1 | Neutral. OBBI arrival and departure. |
| asset:me:civair_obbi_2 | civ_a330 Squadron40 (Gulf Air, Nation=Bahrain) | exact | transit | 1 | Neutral. OBBI arrival and departure. |
| asset:me:civair_obbi_3 | civ_a380 Squadron5 (Emirates, Nation=UAE) | exact | transit | 1 | Neutral. Gulf airway overflight. |
| asset:me:civair_obbi_4 | civ_a320 Squadron7 (Qatar Airways, Nation=Qatar) | exact | transit | 1 | Neutral. Gulf airway overflight. |

These four airframes are the whole finite neutral set (3746453639; I re-checked the nations in the squadron files). The other Gulf liveries (A320 Sq25/26, A330 Sq29/30/33, A380 Sq8/12) are alternates and are not allocated. Each airliner needs airways, because an aircraft orbits at its last waypoint.

**Support services**
- **Aircraft turnaround:** a finite base stock of 1,500,000 points. Whether the P-8A can recover, rearm and fly again here is untested, and whether the base stock refills is not established.
- **Aerial refuelling:** none proposed. The modded tankers are unverified.
- **Ship ammunition:** not applicable.
- **Fuel:** ground refuelling is undocumented; not established.
- **Restocking:** not established.
- **Repair:** not established.

**Connections**
- Source: NSA Bahrain, aviation support (R03:42).
- Authored:
  - Gulf / Hormuz patrol areas (R03:7 names Hormuz but no base);
  - Camp Lemonnier operates the same P-8A type with a separate airframe;
  - OBBI's stock civil destinations.

**Routine activity (proposed, not implemented)**
- One P-8A is airborne at a time and the other is in turnaround.
- Gulf Air arrivals and departures (civair_obbi_1, civair_obbi_2), plus Emirates and Qatar overflights on Gulf airways (civair_obbi_3, civair_obbi_4).
- Optional: Iran-flagged civil liveries exist (A320 Sq2 Mahan Air, Sq8 Iran Air, Sq12 Kish Air). No Iranian military is proposed, because no report names an Iranian node.

**Validation and gaps**
- How a host-flag base behaves with US squadrons is untested.
- Gaps:
  - no named Muharraq unit;
  - no Bahraini military aircraft;
  - no MH-60S (missing_fit);
  - no C-17 or C-5; the C-141B proxy is dated 1965-2006.

---

### me_uae_jebel_ali_port - Jebel Ali Port Facility

**Identity.**
- Operator: not stated. Host: United Arab Emirates.
- node_kind: port_commercial (assumed). populate_policy: populate_small.

**Role.**
- **SOURCE CLAIM:** named as the specific UAE logistics node supporting NSA Bahrain, alongside unnamed nodes in Kuwait and Oman (R03:42).
- **CHECK:** R03 does not state the port's operator, ownership, commercial status or US status. Treating it as a host-nation commercial port is a design assumption to check (fidelity check 2 fix).
- **SCENARIO CHOICE:** neutral shipping, plus authored logistic visits by one finite US oiler.

**Position.**
- Public location approx 25.0N 55.1E. Approx, verify.
- In-game evidence:
  - no unit and no world-data entry for Jebel Ali;
  - vanilla cities.ini [Dubai] at 25.2134,55.2685, about 17 NM away (it wrongly declares Nation=Saudi Arabia);
  - hidden port_pg_fujairah (25.1082,56.3537; unit variants Nation=Iceland), about 70 NM away on the Gulf of Oman coast; rejected;
  - proven sea placement 43 NM away (Boris Chilikin in SEST '01 Threads');
  - mission centres Hormuz 25.78,55.74 and Gulf 25.87,53.73;
  - stock As Salamah sea point about 123 NM away.

**Forces (SCENARIO CHOICE)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:me:inst_jebel_ali | ran_pt_boats_docks | proxy | resident_at_base | 1 | **Pier marker.** Nation=uae, VariantReference=Default (base text 'RAN base'), mandatory NameOverride 'Jebel Ali (stand-in, no shore service)'. No supply block. nv_pt_boats_docks is rejected because its unlimited rearm would serve whoever owns the port. |
| asset:me:tao_1 | usn_tao_kaiser | proxy | transit | 1 ship | **Jebel Ali - NSA Bahrain shuttle.** Labelled stand-in on the Teide mesh. Its oiler role is visual only. Variant pick provisional. |
| asset:me:civ_vlcc_1, asset:me:civ_vlcc_2 | civ_ms_ritina | exact | transit | 2 | Liberia, Japan or Kuwait variants. Outbound via Hormuz. |
| asset:me:civ_carcarrier_1 | civ_ms_car_carrier_a | exact | transit | 1 | Panama or Liberia variant, inbound. |
| asset:me:civ_dhows_gulf | civ_fv_dhow | proxy | transit | 3 | Variant1 (Dhow fishing boat white, Nation=Iraq), labelled 'neutral dhow'. No GCC flag exists except Kuwait, on merchants. |

**Support services**
- **Shore services:** none established.
- **Ship ammunition:** asset:me:tao_1, TruckSupplySystem:
  - pool 80,000 points with MaxAmmoPoints 2,000, so it refuses strike rounds;
  - 60 points/s, 0.5 nm, 2 receivers;
  - categories Harpoon 8 and AirTorpedo 16.
- **Fuel:** not established (not modelled).
- **Restocking:** not established. Jebel Ali cannot refill tao_1 or take_1.
- **Repair:** not established.

**Connections**
- Source: NSA Bahrain logistics (R03:42).
- Authored:
  - the stock Hormuz chain As Salamah - Ras al Kul - Gulf of Oman;
  - the stock in-Gulf links Al Jubayl - As Salamah and Minah Al Ahmadi - As Salamah (vanilla sea_links.ini). Their geometry needs sea_routes.py validation. Only the Jebel Ali spur needs authoring;
  - candidate neutral destinations: ports.ini [Port Al Jubayl] (27.054401,49.690686, Nation=Saudi Arabia) and [Port Minah Al Ahmadi] (29.043814,48.164590, Nation=Kuwait), both of which carry civ_ms_ritina Destinations; also the hidden persian_gulf_ports.ini entries (Dammam, Kuwait, Minah Al Ahmadi, Bandar Abbas). All untested.
- Backlog: the Kuwait and Oman nodes.

**Routine activity (proposed, not implemented)**
- tao_1 shuttles to Bahrain, escorted by lcs_1 on part of the leg.
- The VLCCs head out through Hormuz to the Gulf of Oman, and the car carrier comes in.
- The dhows run looped coastal fishing tracks.
- All traffic is finite, with explicit waypoints.

**Validation and gaps**
- Excluded: civ_ms_poltava's Kuwait variants carry a live 4,800,000-point supply block.
- Gaps:
  - no Jebel Ali unit and no UAE navy;
  - UAE air units exist (uae_m2k-9, exp_rafale_c_l Sq5, dts_saab_ge, uae_a330_mrtt), but no report names a UAE airbase;
  - no LNG carrier and no modern container ship;
  - no UAE, Bahrain, Saudi or Oman merchant flag.

---

### me_bahrain_dla_distribution - DLA Distribution Bahrain

**Identity.**
- Operator: US Defense Logistics Agency. Host: Bahrain.
- node_kind: distribution_depot. populate_policy: abstract_logistics_only.

**Role.**
- **SOURCE CLAIM:** Middle East and Europe sustainment flows through DLA Distribution Bahrain, DLA Distribution Sigonella and DLA Distribution Europe at Germersheim (R02:23).
- **CHECK:**
  - absent from the R02 table (R02:27-34);
  - no location within Bahrain is given;
  - DLA scope and counts are a priority check (seed:23);
  - no link to NSA Bahrain is stated;
  - no other claims exist (fidelity check 0).
- **SCENARIO CHOICE:** an abstract node. Its stock appears physically only through asset:me:take_1 (an authored link).

**Position.** Not given in R02, so none is assigned. There is no in-game depot unit.

**Forces**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:me:dla_bahrain_stock | - | none | abstract | 0 | **Abstract distribution stock.** No DLA depot unit exists. tgt_ammo_depot_small and nv_headquarters serve land units only. |

**Support services.**
- Abstract only. Nothing in game can top up asset:me:take_1.
- Fuel: not established. Repair: not established.

**Connections**
- Source:
  - Sigonella and Germersheim DLA: the sustainment trio (R02:23);
  - usg_dla_distribution_network: parent network (R02:23).
- Authored:
  - NSA Bahrain;
  - a later depot-to-theatre link through labelled RRF ro-ros (civ_ms_roro_c, Nation=US variants); backlog only.

**Routine activity.** None (abstract).

---

### hoa_djibouti_camp_lemonnier - Camp Lemonnier

**Identity.**
- Operator: United States. Host: Djibouti.
- node_kind: mixed_base. populate_policy: populate_small.

**Role.**
- **SOURCE CLAIM:**
  - Djibouti sits at the entrance to the Red Sea and the Bab-el-Mandeb and hosts the densest cluster of foreign bases. The US operates Camp Lemonnier, a former French Foreign Legion base with 4,500 personnel, the 'primary operational headquarters for U.S. Africa Command in the region' (R01:49).
  - AFRICOM relies on it as a critical node for counter-terrorism, drone operations and maritime security at the Bab-el-Mandeb (R03:44).
  - Players must navigate the presence of the PLA base 'without triggering unintended escalation' (R01:70).
- **CHECK:**
  - AFRICOM's HQ is in Stuttgart, and the Lemonnier command is usually called CJTF-HOA; treat it as a regional hub;
  - the personnel figure is time-sensitive and is not an asset count;
  - no drone types are named;
  - the camp shares the airport area with the French and Japanese sites (outside knowledge), so separate airbase units next to one runway need an editor check.
- **SCENARIO CHOICE:** a small expeditionary air element. No ships.

**Position.**
- Public location approx 11.55N 43.15E (south side of Djibouti-Ambouli airport). Approx, verify.
- In-game evidence:
  - no unit;
  - proven points 62-68 NM away;
  - mod 3796349767 missions centred at 13.17,43.15;
  - stock Bab El Mandeb sea point about 65 NM away.
- Placement needs the land mask.

**Forces (SCENARIO CHOICE)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:hoa:inst_lemonnier | nato_small_airbase | proxy | resident_at_base | 1 | **Airfield stand-in.** Nation=usa, NameOverride 'Camp Lemonnier (stand-in)', explicit CustomAirGroup. Finite 1,500,000 stock, AircraftCapacity 60. The alternative, airbase_us, displays 'U.S. Air Force Base' (NameOverride required), has no FlightDeck stock and has broken default entries. Optional long-term step: a raaf-bases clone, which would need FlightDeck_AmmoCapacity added. It is not a fallback, because NameOverride labelling is proven. |
| asset:hoa:mq9_1 | usaf_mq-9a | exact | patrol | 1 | Bab-el-Mandeb ISR orbit (R03:44 role). Only armed loadouts exist (Strike, SEST_REDBACK), so set Hold. |
| asset:hoa:mq9_2 | usaf_mq-9a | exact | resident_at_base | 1 | Turnaround; swaps with mq9_1. |
| asset:hoa:p8a_1 | usn_p_8a | exact | patrol | 1 | Maritime security (R03:44). Squadron1-14. A separate airframe from Muharraq's. |
| asset:hoa:kc130j_1 | usmc_kc-130j | exact | support | 1 | **Theatre airlift and tanker.** ProbeAndDrogue only. Labelled 'C-130J stand-in' if shown as USAF. Airlift is visual, since aircraft have no cargo mechanic. |
| asset:hoa:hh60_1, asset:hoa:hh60_2 | usn_hh-60 | proxy | reserve | 2 | SAR alert. Each is labelled 'HH-60W stand-in (HH-60H)'. No CV-22B is placed. If one is wanted, it is a separately allocated usmc_mv-22b labelled 'CV-22B stand-in (MV-22B)'. |

**Support services**
- **Aircraft turnaround:** a finite base stock of 1,500,000 points. Repeat sorties are untested.
- **Aerial refuelling:** the KC-130J offers ProbeAndDrogue only. Receiver compatibility is not checked, so not established.
- **Ship ammunition:** none. There is no pier, and no report states US ship support here.
- **Air-cargo ammunition:** usaf_c-141b carries a PlaneCargoSupplySystem (60,000 points), but it is dated 1965-2006 and untested. Not proposed.
- **Restocking, fuel, repair:** not established.

**Connections**
- Source:
  - PLA Support Base: ROE neighbour (R01:51 'just down the coast'; R01:70);
  - the French, Japanese and Italian sites: same cluster 'within miles' (R01:49); colocation not stated;
  - Bab-el-Mandeb maritime security (R03:44);
  - AFRICOM regional hub (R01:49, R03:44).
- Authored:
  - NSA Bahrain (overlapping Red Sea and Arabian Sea areas, R03:42);
  - the regional neutral traffic.

**Routine activity (proposed, not implemented)**
- One MQ-9A orbits over the Bab-el-Mandeb at any time.
- The P-8A patrols the South Aden - Gulf of Aden sea link.
- The KC-130J makes finite departures and arrivals.
- The HH-60H pair stands SAR alert.
- **ROE:**
  - the US forces sit in their own taskforce, and each neighbour keeps its own side;
  - Hold and neutral behaviour must be tested;
  - no escalation or espionage mechanic and no sanctuary rule is invented from R01:69-70.

**Validation and gaps.**
- No named base unit.
- No HH-60W (HH-60H proxy). No CV-22B (none placed; a labelled usmc_mv-22b would be a separate allocation).
- No USAF C-130J (missing_fit).
- No C-17 or C-5.
- No Djibouti host forces or flag.
- Chabelley stays in the backlog.

---

### hoa_djibouti_pla_support_base - PLA Support Base (Djibouti)

**Identity.**
- Operator: China (PLA). Host: Djibouti.
- node_kind: logistics_centre. populate_policy: populate_small.

**Role.**
- **SOURCE CLAIM:**
  - 'Just down the coast' from Camp Lemonnier, China operates its first overseas military installation, established at a cost of $590 million (R01:51).
  - Its presence calls for careful ROE that model espionage and diplomatic tension 'without triggering unintended escalation' (R01:70).
  - Djibouti hosts 'rival global powers within miles of one another' (R01:49).
- **CHECK:**
  - no function, facilities or assets are stated;
  - check for a pier usable by PLAN ships before placing any;
  - the cost figure is unsourced;
  - the French, Japanese and Italian sites are nearby within the cluster (R01:49, R01:51), not colocated (fidelity check 2 fix).
- **SCENARIO CHOICE:**
  - a labelled support-base marker set with no airfield;
  - one visiting PLAN escort group;
  - the group's composition is a scenario choice;
  - not hostile by default (plan:22).

**Position.**
- Public location approx 11.6N 43.05E (Doraleh area), about 6 NM from Camp Lemonnier. Approx, verify.
- In-game evidence: the same as Camp Lemonnier.

**Forces (SCENARIO CHOICE)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:hoa:inst_pla_hq | FOB | proxy | resident_at_base | 1 | **HQ marker.** Nation=china, NameOverride 'PLA Support Base Djibouti (stand-in)'. 3600788156, Installation subtype. No AirGroup and no supply block, matching the NSA Bahrain HQ marker. nv_headquarters is rejected: its [SupplySystem1] is an unlimited TruckSupplySystem for LandUnit targets (3605013271 land_units/nv_headquarters.ini:78-88). |
| asset:hoa:inst_pla_stores | warehouses_1, tgt_fueltanks_medium | proxy | resident_at_base | 2 units | Scenery and targets. The fuel tanks are visual only. |
| asset:hoa:inst_pla_pier | ran_pt_boats_docks | proxy | resident_at_base | 1 (conditional) | No supply. Nation=china, VariantReference=Default (base text 'RAN base'), mandatory NameOverride 'PLA Support Base pier (stand-in, no shore service)'. Placed only if the pier check passes. nv_pt_boats_docks is rejected for its unlimited rearm. |
| asset:hoa:plan_ddg_1 | plan_type_052d_p3 (+ plan_z-20f x1) | exact | escort | 1 | Hull pick provisional; avoid Variant9 'Guilin (164)', which collides with the JLSF centre's name. |
| asset:hoa:plan_ffg_1 | plan_type_054a_p5 (+ plan_z-9f x1) | exact | patrol | 1 | Dated 2022 onward. Its yu-7c torpedo is unpriced, so replenishing it is unmetered. |
| asset:hoa:plan_aor_1 | plan_aor_type903a | proxy | support | 1 | Labelled stand-in, unarmed. |

**Support services**
- **Ship ammunition:** plan_aor_1 TruckSupplySystem:
  - pool 220,000 points with a 5,000 ceiling, 80 points/s;
  - range 0.6 nm, 2 receivers, supplier up to 13 kn, receiver up to 16 kn;
  - categories AirTorpedo 32, SovietAdvancedASM 8, SEST_LandAttack 16, SEST_LongRangeSAM 24.
- **Shore supply:** none. The FOB HQ marker, the stores and the pier marker have no supply block.
- **Helicopters:** on deck, AircraftCapacity 1 each.
- **Restocking, fuel, repair:** not established.

**Connections**
- Source:
  - Camp Lemonnier (R01:51, R01:70);
  - the French, Japanese and Italian sites (R01:49, R01:51).
- Authored:
  - the Chinese maritime region as the group's origin (owned by the China package; route unvalidated);
  - a plaaf_yy-20a air bridge as a link only (no airfield, not allocated);
  - the Gulf of Aden escort corridor along the stock sea links.

**Routine activity (proposed, not implemented)**
- The group escorts asset:hoa:civ_vlcc_1 through the Gulf of Aden.
- RAS from plan_aor_1.
- A port visit only if the pier check passes.
- **ROE:** a separate taskforce, neutral to all neighbours by default. R01:70 is implemented only as tested Hold and neutral behaviour.

**Validation and gaps.**
- No named PLA Djibouti unit.
- No PLAN hospital ship (none).
- No Chinese merchant flag.

---

### hoa_djibouti_fr_ba188_heron - Base Aérienne 188 / Héron naval base (Djibouti) - report naming

**Identity.**
- Operator: France. Host: Djibouti.
- node_kind: mixed_base. populate_policy: populate_small.

**Role.**
- **SOURCE CLAIM:** 'France maintains a significant presence at Base Aérienne 188 (also known as the Héron naval base), one of its largest military installations abroad' (R01:51).
- **CHECK:**
  - the French naming is a priority check (seed:23); the air-base and naval-base names are likely separate facilities, so the node may split (backlog);
  - no assets are named, and no further claims exist (fidelity check 0);
  - the cluster links read 'same Djibouti cluster (R01:49); not stated as colocated' (fidelity check 0 fix).
- **SCENARIO CHOICE:** an air element and a naval pier marker inside one package until the naming check resolves, plus one frigate on patrol (not a resident assignment).

**Position.**
- BA 188: approx 11.55N 43.16E (airport area).
- Héron: approx 11.6N 43.15E (port area).
- Both are approx, verify, and come from outside knowledge.

**Forces (SCENARIO CHOICE)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:hoa:inst_ba188 | nato_small_airbase | proxy | resident_at_base | 1 | **Air-base stand-in.** Nation=france, NameOverride 'BA 188 Djibouti (stand-in)', explicit CustomAirGroup, finite 1,500,000 stock. No France-flagged airbase variant exists. |
| asset:hoa:inst_heron | ran_pt_boats_docks | proxy | resident_at_base | 1 | **Pier marker.** Nation=france, VariantReference=Default (base text 'RAN base'), mandatory NameOverride 'Héron naval base (stand-in pier)'. No supply. |
| asset:hoa:fr_m2k_1, asset:hoa:fr_m2k_2 | fr_m2k-5f | exact | resident_at_base | 2 | Air-defence alert. Squadron4 'EC 3/11 Corse Esc Chat'. Whether this detachment is current is unverified. |
| asset:hoa:fr_puma_1 | fr_as_332M | proxy | support | 1 | SAR and utility. Squadron2 (1/67), labelled 'SA330 Puma stand-in'. Avoid Squadron3, a Spanish unit name under a French flag. |
| asset:hoa:fr_gazelle_1 | fr_sa_342_gazelle | exact | resident_at_base | 1 | French Forces in Djibouti army aviation (a verify missed asset). |
| asset:hoa:fr_ffg_1 | fr_ffg_lafayette_modernized (+ fr_as-565_sa x1) | exact | patrol | 1 | Red Sea / Gulf of Aden patrol. Mod 3567256221 is catalogued as WIP. Hull pick (F710/F712/F713) provisional. |

**Support services**
- **Aircraft turnaround:** a finite base stock.
- **Aerial refuelling:** none placed. On paper fr_a330_mrtt (TankerSystems=ProbeAndDrogue) can refuel fr_m2k-5f (ReceiverSystems=ProbeAndDrogue); untested.
- **Ship ammunition:** no French replenishment ship exists (none). No in-region rearm source exists for French ships. The only option is cross-nation RAS from a US (asset:me:take_1) or PLAN (asset:hoa:plan_aor_1) supplier, which is untested. This is an option only, not an allocation: asset:me:take_1 keeps its single allocation on the Gulf of Oman station and is not tasked to Djibouti. Returning to the Héron pier marker is presence only, because it has no supply block.
- **Restocking, fuel, repair:** not established.

**Connections**
- Source: the cluster (R01:49, R01:51).
- Authored:
  - the BA 188 - Héron internal link, pending the split;
  - the frigate's patrol area.

**Routine activity (proposed, not implemented).**
- The frigate patrols the Gulf of Aden.
- The Mirages fly occasional local air patrols.
- The Puma stands SAR alert.

**Validation and gaps.**
- No French base unit.
- No French replenishment ship.
- No Puma or Fennec (proxy).
- No Falcon 50M or Floréal.
- Mistral and Charles de Gaulle exist but are not proposed, since no report places them here.

---

### hoa_djibouti_jp_base - Japanese defense force base, Djibouti (unnamed in R01)

**Identity.**
- Operator: Japan. Host: Djibouti.
- node_kind: mixed_base. populate_policy: populate_small.

**Role.**
- **SOURCE CLAIM:** Japan operates its own dedicated defense force base, used for anti-piracy, counter-terrorism and intelligence gathering across the Red Sea and the broader Indo-Pacific (R01:51).
- **CHECK:**
  - unnamed in R01; check the official name and the supported assets;
  - the sentence is shared with Italy, so its wording is not corroboration;
  - R01 names no aircraft type. If a P-1 is intended, relabel both P-3Cs as proxy: 'P-1 (P-3C stand-in)'.
- **SCENARIO CHOICE:** a small maritime-patrol detachment. No surface escort is proposed.

**Position.** Public location approx 11.55N 43.14E (NW side of the airport). Approx, verify; outside knowledge.

**Forces (SCENARIO CHOICE)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:hoa:inst_jp | airfield_small_1 | proxy | resident_at_base | 1 | **Airfield stand-in.** Variant5 'Airbase - small (Japan)', native Nation=Japan. AircraftCapacity 48; FlightDeck 1,000,000. Replace its Cold War group (F-1, T-2, F-4EJ, PS-1, US-1, HSS-2) with an explicit CustomAirGroup. NameOverride 'JSDF Djibouti facility (stand-in)'. |
| asset:hoa:jp_p3c_1 | usn_p-3c | exact | patrol | 1 | Anti-piracy surveillance (role from R01:51). A Japan-flagged P-3C presented as a P-3C, since R01 names no type. The Gulf of Aden track is a SCENARIO CHOICE. Squadron21-29 (Nation=Japan). |
| asset:hoa:jp_p3c_2 | usn_p-3c | exact | resident_at_base | 1 | Turnaround; same unit and squadron range as jp_p3c_1. |

**Support services.**
- Aircraft turnaround: a finite base stock of 1,000,000 points (airfield_small_1). Repeat sorties are untested.
- No ship support.
- Restocking, fuel, repair: not established.

**Connections**
- Source:
  - the cluster (R01:49, R01:51);
  - Red Sea: anti-piracy patrol area (R01:51).
- Authored:
  - Gulf of Aden patrol area (not named in R01-R03);
  - context links to the Japanese patrol network (Atsugi, Kanoya, Naha).

**Routine activity (proposed, not implemented).** One P-3C on patrol and one in turnaround.

**Validation and gaps.**
- The usn_p-3c squadrons file has [Default] ServiceDate=1977|1995, and the Japan squadrons carry no date of their own. Check in the editor whether a 2026+ mission filters them out.
- No P-1.
- No modern JMSDF destroyer. jmsdf_aoe_mashuu exists (proxy) but is not proposed without escorts.
- No named base.

---

### hoa_djibouti_it_base - Italian defense force base, Djibouti (unnamed in R01)

**Identity.**
- Operator: Italy. Host: Djibouti.
- node_kind: mixed_base. populate_policy: populate_small.

**Role.**
- **SOURCE CLAIM:** Italy operates its own dedicated defense force base for anti-piracy, counter-terrorism and intelligence gathering across the Red Sea and the broader Indo-Pacific (R01:51).
- **CHECK:**
  - unnamed; check the name and assets;
  - the cluster links need R01:49 and R01:51 citations, read as 'nearby within the cluster' (fidelity check 2 fix);
  - whether the base has its own airfield is unknown.
- **SCENARIO CHOICE:** a base marker with no airfield, plus one patrol vessel.

**Position.** Approx 11.5N 43.2E. Approx, verify; low confidence, outside knowledge.

**Forces (SCENARIO CHOICE)**

| Asset | Unit id(s) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:hoa:inst_it | warehouses_3 | proxy | resident_at_base | 1 | **Base marker.** Nation=italy, NameOverride 'Italian national support base Djibouti (stand-in)'. Installation subtype, no supply. nato_very_small_airbase is not proposed: it would add a runway the base may not have. |
| asset:hoa:it_ppa_1 | ita_ffg_ppa (+ ita_sh-101a x1) | exact | patrol | 1 | Anti-piracy patrol (role from R01:51). The Gulf of Aden track is a SCENARIO CHOICE. Flight deck 2,800. Variants P430-P436 (2022-2026); pick provisional. |

**Support services.**
- No Italian replenishment ship exists (none).
- No shore supply: the warehouses_3 marker has no supply block.
- No in-region rearm source exists for Italian ships. The only option is cross-nation RAS from a US (asset:me:take_1) or PLAN (asset:hoa:plan_aor_1) supplier, which is untested. This is an option only, not an allocation: asset:me:take_1 keeps its single allocation on the Gulf of Oman station and is not tasked to Djibouti. Returning to the base marker is presence only.
- Restocking, fuel, repair: not established.

**Connections**
- Source:
  - the cluster (R01:49, R01:51);
  - Red Sea: anti-piracy patrol area (R01:51).
- Authored: Gulf of Aden patrol area (not named in R01-R03).

**Routine activity (proposed, not implemented).** A looped PPA patrol along South Aden - Gulf of Aden.

**Validation and gaps.**
- No Italian supply ship.
- No named base.
- No Italian aircraft mapped for Djibouti.
- mm_ddgh_durand_de_la_penne_02 (3505420313; Variant2 D561 Francesco Mimbelli) and mm_ffg_maestrale (3505420313) exist as verify missed assets, but neither is proposed.
