<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Australia, Indian Ocean and the Afloat Prepositioning Fleet

### Region summary

- **Nodes, in register order:**
  - `io_diego_garcia_nsf`: populate
  - `glob_us_afloat_prepositioning_fleet`: abstract_logistics_only
  - `aus_stirling_hmas_stirling`: populate
  - `aus_tindal_raaf`: populate_small
- **What the sources give is thin.**
  - Stirling and Tindal share a single report line (R01:55).
  - Diego Garcia and the APF are covered by R01:23, R01:68, R02:7, R02:21, R02:25, R02:33, R02:78, R03:40 and R03:172. These lines largely repeat each other:
    - R02:25 and R03:40 repeat the lagoon / MPS sentence.
    - R01:23 and R02:25 repeat "out of range of many regional threats". R03:40 says the narrower "safely out of range of many regional theater ballistic missile threats" (theatre ballistic missiles only).
    - Repetition is not corroboration.
  - No report gives a hull name, squadron, ship count or loiter area for any of the four nodes. **Every quantity below is a SCENARIO CHOICE.**
- **Proposed population (SCENARIO):**
  - Placed: 11 ships and submarines, 5 land units, 9 aircraft in base air groups (2 B-52H and 2 B-1B at Diego Garcia; 4 F-35A and 1 MQ-4C at Tindal) and 2 embarked helicopters (one per Anzac; Eyre sails with an explicitly empty air group).
  - Finite reserve, not placed: 2 B-2A, 2 B-52H, 1 Collins SSG and 1 APF hull.
  - Neutral traffic: 5 merchants and 3 airliners, in 3 groups. Each hull or airliner has one allocation:
    - `asset:ausio:civ_io_lane` (Diego Garcia package): `civ_ms_bulk` (exact) and `civ_ms_encounter` (proxy, NameOverride 'period container ship (stand-in)').
    - `asset:ausio:civ_perth_traffic` (Stirling package): `anl_ms_bulk` V1 (exact), `civ_ms_act_1` (proxy, NameOverride 'period container ship (stand-in)') and `civ_ms_bulk` (exact).
    - `asset:ausio:civ_air`: one `civ_a330` Squadron61 (Australia) near Perth, in the Stirling package only; one `civ_a330` (Sri_Lanka / Singapore / UAE / Qatar squadron) and one `civ_a380` on the Indian Ocean lane, in the Diego Garcia package. Tindal has no airliner. Airliners are exact (installations lens mappings[72]).
    - Outcomes follow the installations lens: bulk carriers exact (mappings[63]); the 1970s-80s container designs are proxies to be labelled as period stand-ins (mappings[62]).
- **Existing content reused:**
  - `airbase_raaf_tindal`: an existing SEST named airbase with its own air group (SEST RAAF Bases). It is reused here, with the shipped air group replaced by a smaller override.
  - SEST RAN Fleet hulls.
  - The RADF `ran_pt_boats_docks` Variant2 marker, named 'Fleet Base West (HMAS Stirling)'.
  - The stock 'NSF Diego Garcia' airfield placement from vanilla '04 Chagos Gambit'.
- **Inventory corrections applied:**
  - SEST stand-in suppliers count as proxy: `ran_aor_supply` and the T-AO, T-AKE and T-AOE stand-ins. The same rule is applied to the Collins and Arafura stand-ins.
  - The Stirling port marker is missing_fit for port service.
  - Refuelling by the modded tankers is unverified.
  - Only the Chagos Gambit and Tindal placements are reusable anchors (each within about 1 NM of the real field).
  - Algol variants 2, 4, 5 and 8 end in 2025. Kilauea hulls are dated.
  - The Anzac depends on the deprecated mod 3440622312, which must stay enabled.
  - The period container hulls `civ_ms_act_1` and `civ_ms_encounter` are proxies with a visible stand-in label (installations lens mappings[62]).
- **Scope** (scope-and-performance §1-2; distances measured from the candidate centre 42N 20E):

| Check | Value | Played and saved evidence |
|---|---|---|
| Diego Garcia from centre | ~4,120 NM | up to 8,781 NM |
| Stirling from centre | ~6,890 NM | up to 8,781 NM |
| Tindal from centre | ~6,980 NM | up to 8,781 NM |
| Stirling \|z\| | ~4,454 | 4,529 |
| Diego Garcia–Stirling separation | 2,838 NM | 3,450 NM |
| Diego Garcia–Tindal separation | **3,553 NM** | 3,450 NM |

  - The Diego Garcia–Tindal separation exceeds what played content covers. That is untested, not a known limit.
  - No node is near the ±180° edge.
  - Absolute `GeoPosition` placement is available.
  - Capacity is unmeasured.
  - The builders' coastline extract (100–180E, 25–72S) covers Stirling only.
- **Identity:**
  - None of the hulls in R03's carrier table is allocated in this region. Roosevelt's 'Transiting to U.S. Central Command' (R03:57) stays in its home-port region's package, and any Indian Ocean leg must reuse that one identity.
  - `dts_b-52h` Squadron1 (2nd BW) is the only operational B-52H livery. The detachments here are separate airframes from any B-52H allocated in other regions.
  - No named US sealift hull is used. `civ_ms_roro_a` Variant6-10 are the Ready Reserve Force ro-ros Cape Ducato, Douglas, Domingo, Decision and Diamond (T-AKR-5051 to 5055), and `civ_ms_seabee` Variant1-3 are SS Cape May, Cape Mohican and Cape Mendocino (vanilla `language_en/vessel_names.ini`). They are RRF surge sealift, not MPS/APF ships, and the US Pacific package already pins `civ_ms_seabee` Variant1 world-wide. This region pins the unnamed Default for both units and leaves the named hulls to whichever region allocates US sealift.
- **Excluded from rhetoric:** the "out of range" wording does not create any sanctuary, invulnerability or perfect-detection rule.

---

### io_diego_garcia_nsf - Naval Support Facility Diego Garcia

**Identity**

| Field | Value |
|---|---|
| Operator | United States Navy |
| Host | 'British Indian Ocean Territory' (report wording; see CHECK) |
| Kind | mixed_base |
| Aliases | NSF Diego Garcia, Diego Garcia |
| Policy | **populate** |

Populate reason, reworded per the fidelity check:
- Diego Garcia has a physical anchorage and an airfield.
- Allocate an authored subset of MPS hulls to the lagoon. Other APF ships are allocated at sea or in reserve under `glob_us_afloat_prepositioning_fleet`, each only once.
- The bombers are rotational detachments.

**SOURCE CLAIMS**
- **R01:23:** A premier deepwater anchorage and bulk fuel hub for APF vessels, out of range of many regional threats.
- **R02:25:**
  - In the BIOT, and a premier hub for the APF capability.
  - Its deepwater lagoon anchors Maritime Prepositioning Squadron ships heavily stocked with equipment.
  - The base stores fuel and ammunition out of range of many regional threats.
- **R02:33:** Table row: 'Afloat Prepositioning Fleet anchorage, bulk fuel/ammo'.
- **R03:40:**
  - Highly secretive and strategic; a vital logistics and bomber hub.
  - 'Located safely out of range of many regional theater ballistic missile threats', 3,800 km from Iran and 4,700 km from Beijing.
  - Its lagoon anchors MPS ships 'heavily stocked with equipment for ground invasions'.
  - Its airfield 'routinely accommodates strategic bombers including the B-52, B-1B, and B-2'.
  - A critical node for long-range strike into the Middle East and Asia.
- **R03:172:** Massive operational reach for US bombers and surface fleets, but it needs constant resupply via vulnerable sea lines of communication (SLOCs). This is a joint, island-level statement with Guam.
- **Qualifier (R01:23, R02:25):** APF ships 'loiter in strategic regions'.

**CHECK**
- Sovereignty and lease status after the 2025 UK–Mauritius Chagos agreement. The 'BIOT' wording may be dated.
- The R03:40 distances are not used:
  - The Beijing figure looks low (about 6,900 km great-circle).
  - The Iran figure fits only Iran's southern coast.
- 'Accommodates' means visiting or rotational, not resident.
- 'Out of range of many regional threats' (R01:23, R02:25) and 'safely out of range of many regional theater ballistic missile threats' (R03:40, narrower: theatre ballistic missiles only) are qualitative. There is no sanctuary or invulnerability rule (seed:23), and the base remains attackable.
- No report gives ship names, squadron numbers or counts.
- Inference, not a report claim (fidelity check 1): because APF ships loiter in strategic regions (R01:23, R02:25) and no report counts the lagoon ships, the lagoon holds only an authored subset of APF hulls.
- The APF link is a relationship, not colocation (fidelity fix).
- R02:33 lists Diego Garcia in R02's logistics table without calling it a DLA centre. Do not count it toward the OCONUS DLA hub total.
- R03:172 on Yulin submarine harassment: reading it as harassment of shipping bound for Diego Garcia is a contextual inference. Drop 'US' (fidelity fix).
- Repetition across R01:23, R02:25 and R03:40 is not corroboration. Only R03 adds the bombers and the distances, and it narrows the threat wording to theatre ballistic missiles.

**Role:** prepositioning anchorage, logistics storage, and a rotational heavy-bomber airfield.
- The storage is represented as target scenery, not as a service.

**Position**
- **Public location:** airfield / NSF about -7.3, 72.4. Lagoon anchorage inside the atoll at about -7.3 to -7.4, 72.4 (approx, verify).
- **In-game evidence:**
  - Stock vanilla `strike-group-molniya-campaign/missions/04 Chagos Gambit.ini` places `airfield_small_1` with NameOverride 'NSF Diego Garcia' (ShortName FJDG):
    - MapCenter -7.34/69.32, `RelativePositionInNM=183.99,low,2.73`, Heading -50.
    - This decodes to -7.295, 72.387, about 1-2 NM from the field. It is one of the two anchors the verify pass kept.
  - The same mission places `usn_ae_kilauea` about 123 NM offshore.
  - There is no world-database point; the nearest is Cochin, 1,063 NM away.
  - No sea unit has ever been placed in the lagoon.
- **Status:** placement pending validation. It needs an atoll land mask, and land units placed on water float at 1 m.

**Forces (SCENARIO CHOICES unless marked source)**

| Asset id | Allocation | Role | Unit id (variant/squadron) | Qty | Outcome | Source basis | Notes |
|---|---|---|---|---|---|---|---|
| asset:ausio:dg_airfield | resident_at_base | Installation: airfield with NSF label | `airfield_small_1` Default, NameOverride 'NSF Diego Garcia (generic airfield stand-in)', ShortNameOverride FJDG (stock), per-unit Nation=usa, CustomAirGroup=True | 1 | proxy (labelled) | R03:40 airfield; stock precedent | The stock label 'NSF Diego Garcia' alone does not mark a stand-in, so the suffix is added. Capacity 48. FlightDeck_AmmoCapacity 1,000,000. The default group spawns F-4/E-3A/P-3C, so CustomAirGroup is mandatory. Heavy-bomber operation from this model is untested. A named SEST clone on the raaf-bases pattern would be new content (no such id exists). Host vs tenant flag still to decide. |
| asset:ausio:dg_fuel_store | resident_at_base | Bulk fuel storage, as target scenery | `tgt_fueltanks_large`, NameOverride 'Diego Garcia bulk fuel (target scenery)', per-unit Nation=usa | 1 | proxy (labelled) | R01:23, R02:25, R02:33 | Without the override it displays as the generic 'Fueltanks Large Depot'. Role=Target, no SupplySystem; Default Nation=Vietnam, so override it. Stands for the bulk fuel stocks as a target only. Supplies nothing. |
| asset:ausio:dg_ammo_store | resident_at_base | Ammunition storage, as target scenery | `warehouses_1`, NameOverride 'Diego Garcia ammunition storage (target scenery)', per-unit Nation=usa | 1 | proxy (labelled) | R02:25, R02:33 | Without the override it displays as the generic 'Warehouses 1'. Role=Target, no SupplySystem; Default Nation=Vietnam. Supplies nothing. |
| asset:ausio:dg_b52_det | resident_at_base (rotational detachment) | Strategic bomber | `dts_b-52h` Squadron1 '2nd Bomb Wing' (Nation=US) | 2 | exact | R03:40 'routinely accommodates' | Pin an explicit conventional LoadoutVariant (the inventory flags nuclear-tagged loadouts). No ReceiverSystems. |
| asset:ausio:dg_b1b_det | resident_at_base (rotational detachment) | Strategic bomber | `usaf_b-1b_dts` Squadron2 '7th BW' (Nation=US) | 2 | exact | R03:40 | Pin a conventional loadout (exclude Strike183N). Declares a Boom receiver. |
| asset:ausio:dg_b2_det | reserve (not placed) | Strategic bomber, alternate rotation | `usaf_b-2_spirit` Squadron1 '393rd BS' (Nation=US) | 2 | exact | R03:40 | Placed only after the B-2 is confirmed to load (it depends on SeaLifter, which is not subscribed). Joins only by replacing a detachment. |
| asset:ausio:dg_mps_1 | resident_at_base (anchored in lagoon) | Maritime Prepositioning Squadron ship | `civ_ms_c8` Default (Nation=US), NameOverride 'Maritime Prepositioning ship (stand-in)' | 1 | proxy (labelled) | R02:25, R03:40 (no names or counts) | Dated barge carrier, Role=Merchant. Has a SEST supply block. |
| asset:ausio:dg_mps_2 | resident_at_base (anchored in lagoon) | Maritime Prepositioning Squadron ship | `civ_ms_roro_a` Default only (unnamed, Nation=US), same '(stand-in)' label | 1 | proxy (labelled) | R02:25, R03:40 | Pin Default. Variants 1-5 are Norway and 11-13 Soviet. Variants 6-10 are the named RRF ro-ros Cape Ducato, Douglas, Domingo, Decision and Diamond (T-AKR-5051 to 5055): surge sealift, not MPS ships, and left to whichever region allocates US sealift. |
| asset:ausio:dg_resupply_tanker | transit (one inbound arrival) | Fuel resupply shipping (visual) | `civ_ms_sealift_pacific` Variant4 'MV Sealift Indian Ocean T-AOT-171' | 1 | proxy (labelled: MSC tanker stand-in, dated hull) | R03:172 resupply need (origin unnamed); R01:23, R02:33 bulk fuel | Arrives once and then stays; no respawn. Ship-to-ship fuel is not modelled. |

Not proposed:
- Any warship, submarine, MPA or tender. The us-navy lens node hints for an Ohio SSGN, P-8A, AS tender stand-in and T-AKE at Diego Garcia are not in R01-R03.
- Any GBAD (ground-based air defence). No defences are sourced.
- Any tanker (see Support).

**Support services**

| Service | Status |
|---|---|
| Ship ammunition | Finite SEST gameplay blocks on the MPS stand-ins. This is not evidence that real MPS ships rearm warships. Details below. |
| Aircraft turnaround / ordnance | `airfield_small_1` has a finite FlightDeck_AmmoCapacity of 1,000,000 and AircraftCapacity 48. B-52H/B-1B recovery and repeat sorties from this model are untested. |
| Supplier restocking | Not established. No port or unit restocks a supplier. `usaf_c-141b` PlaneCargoSupplySystem is the only air ammunition-cargo candidate; it is untested and date-gated 1965\|2006. |
| Fuel | Not established. Engine ship supply is ammunition only. The bulk fuel hub is scenery. |
| Repair | Not established. |
| Aerial refuelling | Not established. The modded US tankers lack an [AerialRefueling] block, and the B-52H and B-2 declare no ReceiverSystems. |

Ship ammunition supply in detail (Vessel and Submarine receivers, untested in this world):
- `civ_ms_c8` [SupplySystem1] TruckSupplySystem:
  - Pool 300,000 AP, MaxAmmoPoints 8,000, 35 AP/s.
  - Range 0.5 NM, 1 receiver, supplier at 8 kn or less and receiver at 12 kn or less.
  - Categories: Harpoon 24, AirTorpedo 32, ALWT 16, SEST_LandAttack 16, SEST_LongRangeSAM 16.
- `civ_ms_roro_a`:
  - Pool 80,000 AP, cap 2,000.
  - Categories: Harpoon 8, AirTorpedo 16.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| glob_us_afloat_prepositioning_fleet | APF anchorage and bulk fuel hub (relationship, not colocation) | source | R01:23; R02:25; R02:33 |
| region: Middle East / Asia (unnamed targets) | Long-range strike reach | source | R03:40 |
| sea area: SLOCs to Diego Garcia and Guam | Vulnerable resupply route | source | R03:172 |
| usg_dla_distribution_network | Resupply origin (the reports name no origin) | authored | R03:172 states the need only |
| chn_hainan_yulin_naval_base | Threat: diesel-electric submarines harassing logistical shipping | source, with an inference flag | R03:172 (applying it to Diego Garcia shipping is contextual) |
| wpac_guam_naval_base_apra_harbor | Parallel example in a joint island-level statement; not a supply link | source | R03:172 |
| aus_stirling_hmas_stirling | Allied Indian Ocean transit / rendezvous link, ~2,840 NM great-circle | authored | none |
| aus_tindal_raaf | Bomber rotation alternate, ~3,550 NM | authored | R01:55 capability; R03:40 |
| me_bahrain_nsa_bahrain / hoa_djibouti_camp_lemonnier | Transit toward the Arabian Sea and CENTCOM AOR, ~2,380 / ~2,080 NM | authored | R03:57 carrier stays allocated in its own region |

**Routine activity (proposed, not implemented)**
- **Bomber sorties:** one pair at a time flies a long-range sortie on an authored route toward the Arabian Sea or the eastern Indian Ocean, then returns. Runway, turnaround and range checks are needed first.
- **MPS ships:** at anchor in the lagoon. An occasional authored exchange with the APF loiter ship keeps each hull in one allocation at a time.
- **Inbound tanker:** a single finite arrival.
- **Neutral traffic** on an authored lane well clear of the atoll:
  - `civ_ms_bulk` (India Variant42-44 or Liberia variants).
  - `civ_ms_encounter` (UK container): proxy, a 1970s-80s design, NameOverride 'period container ship (stand-in)' (installations lens mappings[62]). `civ_ms_bulk` is exact (mappings[63]).
  - Airliner overflight (group `asset:ausio:civ_air`): one `civ_a330` (Sri_Lanka / Singapore / UAE / Qatar squadrons) and one `civ_a380` (for example Squadron9 Singapore or Squadron5 UAE). These are two of the group's three airliners; the third, the Australian `civ_a330`, flies only near Perth.
  - This is scenario population, not a researched traffic schedule.

**Validation**
- **Research:** roles sourced; numbers and names unsourced.
- **Mapping:** bombers exact; MPS ships proxy only; installations are visibly labelled proxies.
- **Placement:** airfield anchor proven; lagoon unproven.
- **Runtime activation and save/load:** untested.

**Gaps**
- No named NSF Diego Garcia unit.
- No modern MPS, LMSR, ESB or ESD hulls.
- No US-flag port with finite ship supply. `nv_pt_boats_docks` is Vietnam-flagged and effectively unlimited, so it is not recommended.
- Heavy-bomber use of `airfield_small_1` is unverified.
- No aerial refuelling for the B-52H or B-2.
- No C-17 or C-5; the C-141B stand-in is date-gated.
- No fuel economy, repair or supplier restocking.
- The bomber ranges against the 2,380-2,680 NM legs to Bahrain and Yulin are untested.

---

### glob_us_afloat_prepositioning_fleet - Afloat Prepositioning Fleet (APF)

**Identity**

| Field | Value |
|---|---|
| Operator | United States |
| Host | none (afloat) |
| Kind | anchorage_prepositioning |
| Policy | **abstract_logistics_only** |

- It is a fleet-level capability. Physical hulls exist only as explicit authored allocations.
- The lagoon subset is allocated under `io_diego_garcia_nsf` and is **not** repeated here.

Fidelity fixes applied:
- 'Maritime Prepositioning Squadron ships' is removed as an alias and kept as a platform family. The MPS ships are a component of the APF, not a synonym.
- The DLA link moves from parent to source relationship.
- R02:33, R02:7 and the 'heavily stocked with equipment' claims are added.

**SOURCE CLAIMS**
- **R01:23:** Specialised ships permanently loaded with Marine Corps support cargo, Air Force munitions and DLA fuels, loitering in strategic regions.
- **R02:21:** The US relies on seven OCONUS distribution hubs and a fleet of prepositioned ships. The two are presented as separate pillars.
- **R02:25:** The same cargo list plus hospital equipment. They loiter in strategic regions. MPS ships anchored at Diego Garcia are 'heavily stocked with equipment'; R03:40 adds 'for ground invasions' but never names the APF.
- **R02:33:** The only line that explicitly calls Diego Garcia the 'Afloat Prepositioning Fleet anchorage'.
- **R02:7:** Adversaries will target afloat prepositioning ships to starve forward-deployed forces.
- **R01:68 / R02:78:**
  - The ships are highly vulnerable.
  - R02:78 adds that they are 'slow-moving civilian-crewed' and exposed to submarine attack or long-range strikes.
  - Disrupting them should cause cascading reinforcement delays at frontline bases.

**CHECK**
- No report gives ship names, classes, counts or loiter areas other than Diego Garcia.
- Avoid double allocation with the Diego Garcia node.
- 'Highly vulnerable' is guidance, not a deterministic rule. There is no instant-disable effect.
- The cascading-delay mechanic is a proposal that needs a reinforcement system not yet built.
- The cargo lists differ: hospital equipment appears only in R02.
- The proxy hulls are Role=Merchant. Their SEST supply block is a gameplay abstraction; the R01:23 'Air Force munitions' are not naval rounds.

**Role:** distribution and prepositioning capability (abstract).

**Position:**
- Afloat.
- The lagoon subset is positioned under `io_diego_garcia_nsf`.
- The loiter area is unnamed (R01:23, R02:25). It becomes an authored Indian Ocean area, position pending.

**Forces**

| Asset id | Allocation | Role | Unit id | Qty | Outcome | Source basis | Notes |
|---|---|---|---|---|---|---|---|
| abstract:ausio:apf_capability | abstract | Fleet-level cargo capability: USMC support cargo, USAF munitions, hospital equipment, DLA fuels | (none) | n/a | none (no fleet-level unit) | R01:23; R02:25 | Represented only by the explicit hulls in this region. Not a physical asset. |
| asset:ausio:apf_loiter_1 | underway_deployed | APF ship loitering in an authored area | `civ_ms_seabee` Default (Nation=US), NameOverride 'Afloat prepositioning ship (stand-in)' | 1 (SCENARIO) | proxy (labelled) | R01:23, R02:25 'loiter' (no area named) | Pin Default (unnamed). Variants 7-8 are Soviet. Variants 1-3 are the named RRF ships SS Cape May, Cape Mohican and Cape Mendocino (RRF, not APF; the US Pacific package pins Variant1 world-wide), and Variants 4-6 are named commercial hulls, so none is used here. |
| asset:ausio:apf_reserve_1 | reserve (not placed) | Finite relief hull | `civ_ms_c8` Default (Nation=US), same label | 1 (SCENARIO) | proxy (labelled) | R01:68 / R02:78 vulnerability; plan:81 finite reserve | Activated only to replace a lost or departed hull. Never respawns. |

The lagoon hulls `asset:ausio:dg_mps_1` and `asset:ausio:dg_mps_2` are cross-referenced here, not re-allocated.

**Support services**

| Service | Status |
|---|---|
| Ship ammunition (SEST gameplay; untested) | `civ_ms_seabee`: pool 300,000 AP, cap 8,000, 0.5 NM, 1 receiver, supplier at 8 kn or less and receiver at 12 kn or less. Categories: Harpoon 24, AirTorpedo 32, ALWT 16, SovietAdvancedASM 8, SEST_LandAttack 16, SEST_LongRangeSAM 16. |
| Fuel | Not established. The DLA fuels cargo cannot be transferred ship-to-ship in the engine. |
| Hospital equipment | No representation. |
| Restocking | Not established. |
| Repair | Not established. |

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| io_diego_garcia_nsf | Only located anchorage; bulk fuel hub | source | R01:23; R02:25; R02:33 |
| usg_dla_distribution_network | Cargo includes DLA fuels (relationship, not parent; R02:21 keeps hubs and prepositioned ships separate) | source | R01:23; R02:25; R02:21 |
| sea area: APF loiter 'strategic regions' (unnamed) | Loiter areas | source | R01:23; R02:25 |
| frontline bases (unnamed) | Disruption causes cascading reinforcement delays | source (guidance) | R01:68; R02:78 |
| chn_hainan_yulin_naval_base | Submarine threat to logistics shipping | authored (inference) | R02:7; R02:78; R03:172 |

**Routine activity (proposed, not implemented)**
- **Loiter ship:** a slow racetrack in the authored area, at 8 kn or less so that it stays supply-capable. An occasional exchange with a lagoon hull.
- **On a scenario trigger:** the loiter ship sails to a forward rendezvous.
- **Reserve hull:** activates only to replace a lost hull.

**Validation**
- **Research:** capability sourced; hulls unsourced.
- **Mapping:** proxy only.
- **Placement:** pending.
- **Runtime:** untested.

**Gaps**
- Loiter regions, ship names and counts are unnamed (backlog).
- The frontline bases are unnamed (backlog).
- No modern MPS container or RoRo ship, LMSR, ESB or ESD.
- No T-AH.
- The cascading-delay mechanic is not implemented.

---

### aus_stirling_hmas_stirling - HMAS Stirling

**Identity**

| Field | Value |
|---|---|
| Operator | Royal Australian Navy |
| Host | Australia |
| Kind | naval_base |
| Alias | Fleet Base West |
| Policy | **populate** |

**SOURCE CLAIMS**
- **R01:55:** HMAS Stirling, on Garden Island near Perth in Western Australia, serves as Fleet Base West.
- **R01:55:** It is the cornerstone of the RAN's Indian Ocean presence and submarine operations.

**CHECK**
- R01:55 is the only line. Check 0 found no further place-specific claims.
- No hulls or classes are named. Every hull pick below is a scenario choice.
- Real home ports and the in-service status of each named hull at the scenario date are unverified.
- The planned AUKUS rotational submarine presence at Stirling is not in R01. Check it for a dated scenario; it is not populated here.

**Role:** naval support and submarine operations.

**Position**
- **Public location:** Garden Island, about -32.2, 115.7 (approx, verify).
- **In-game evidence:**
  - The named marker has never been placed.
  - The nearest placed unit is `ran_pt_boats_docks_small` at Fremantle, -32.03, 115.739, about 13 NM north. It comes from RADF 'Australian Bases Showcase 1968' and carries a per-unit Nation=argentina. Per the verify correction, that point belongs to `_small`, not to `ran_pt_boats_docks`.
- **Validation tools:** the area lies inside the SEST coastline extract (100–180E, 25–72S), so builder land/sea checks can run.
- **Status:** placement pending.

**Forces (SCENARIO CHOICES)**

| Asset id | Allocation | Role | Unit id (variant) | Qty | Outcome | Source basis | Notes |
|---|---|---|---|---|---|---|---|
| asset:ausio:stirling_port | resident_at_base | Installation marker 'Fleet Base West (HMAS Stirling)' | `ran_pt_boats_docks` Variant2 (Nation=Australia) | 1 | missing_fit | R01:55 identity | Exact as a named visual marker but has no SupplySystem (verify correction). A working port needs a SEST clone of `nv_pt_boats_docks` with Nation=Australia, which is new content. |
| asset:ausio:ssg_waller | resident_at_base | Submarine, ready alongside | `ran_ssg_collins` Variant3 'SSG 75 HMAS Waller' | 1 | proxy (stand-in mesh, self-labelled) | R01:55 'submarine operations' (class not named) | S-80 Plus mesh; identity and operator data exact. ServiceDate 1996-2040. |
| asset:ausio:ssg_farncomb | servicing_maintenance | Submarine in maintenance alongside | `ran_ssg_collins` Variant2 'SSG 74 HMAS Farncomb' | 1 | proxy | R01:55 | Placed but not available for tasking. The maintenance state is an abstract label. |
| asset:ausio:ssg_rankin | patrol | Submarine on Indian Ocean patrol | `ran_ssg_collins` Variant6 'SSG 78 HMAS Rankin' | 1 | proxy | R01:55 Indian Ocean presence | Authored patrol box west of Perth. |
| asset:ausio:ssg_sheean | reserve (not placed) | Finite relief submarine | `ran_ssg_collins` Variant5 'SSG 77 HMAS Sheean' | 1 | proxy | R01:55 | Relieves the patrol boat. Never duplicated. |
| asset:ausio:ffh_warramunga | patrol | Frigate, Indian Ocean presence | `ran_ffh_anzac` Variant3 'Warramunga FFH-152' | 1 | exact | R01:55 | Carries 1x MH-60R. Depends on the deprecated 3440622312, which must stay enabled. |
| asset:ausio:ffh_warramunga_helo | patrol (embarked) | Naval helicopter | `usn_mh-60r` Squadron20 '816 Squadron RAN' (Nation=Australia) | 1 | exact | ship air group | Follows the ship's allocation. |
| asset:ausio:ffh_toowoomba | resident_at_base | Frigate, ready alongside | `ran_ffh_anzac` Variant7 'Toowoomba FFH-156' | 1 | exact | R01:55 | — |
| asset:ausio:ffh_toowoomba_helo | resident_at_base (embarked) | Naval helicopter | `usn_mh-60r` Squadron20 | 1 | exact | ship air group | — |
| asset:ausio:opv_eyre | patrol | OPV, local approaches | `ran_opv_arafura` Variant2 'OPV 204 HMAS Eyre', CustomAirGroup=True with no aircraft | 1 | proxy (stand-in, self-labelled) | SCENARIO (not sourced) | Meteoro mesh. The winning SEST_Integration `ran_opv_arafura.ini` [AirGroup] spawns `usn_mh-60r` Squadron20 x1 (AircraftCapacity=1), and the variants file sets no CustomAirGroup. Eyre is therefore placed with an explicitly empty CustomAirGroup=True, matching the RAN Fleet design (integration/ran-fleet/README.md:20, air group none). No helicopter sails with her. An editor re-save drops empty CustomAirGroup lines (installations lens placement_and_engine[9]), so re-check after any editor save. |
| asset:ausio:aor_stalwart | support | Replenishment ship; the node's finite ship-ammunition supplier | `ran_aor_supply` Variant2 'A304 HMAS Stalwart' | 1 | proxy (stand-in; verify correction) | SCENARIO (R01:55 names no auxiliaries) | Donor mesh. ServiceDate 2021-2060. |

Not allocated here, to avoid identical fleet clusters (real basing is unverified and unsourced):
- Hobart DDG, Canberra LHD and Choules: available, but held back.
- The Mogami-based RAN frigate (`js_ffg_mogami` V11-16): a future-dated option only.
- No Hunter class exists in the collection.

**Support services**

| Service | Status |
|---|---|
| Ship ammunition | `ran_aor_supply`, finite; details below. Untested in game. |
| Port service | None. The marker has no SupplySystem. Re-flagging `nv_pt_boats_docks(_small)` to Australia would give unlimited free rearm, so it is not recommended. |
| Aviation | Embarked MH-60R recovery and turnaround on Anzac decks are untested. |
| Restocking | Not established. |
| Fuel | Not established. |
| Repair | Not established. |

`ran_aor_supply` [SupplySystem1] TruckSupplySystem in detail:
- Pool 160,000 AP, MaxAmmoPoints 8,000, 90 AP/s.
- Range 0.5 NM, 2 receivers, supplier at 12 kn or less and receiver at 16 kn or less. Vessel and Submarine receivers.
- Categories: Harpoon 16, AirTorpedo 24, SEST_LandAttack 8, SEST_LongRangeSAM 16.

Category-gate check (data level):

| Round | Hull | Category | AmmoPoints | Passes? |
|---|---|---|---|---|
| DM2A4 torpedo | Collins | none | 4,800 | yes |
| ESSM | Anzac | none | 700 | yes |
| NSM | Anzac | SEST_LandAttack | 8,000 | yes |

- RAN launchers carry ReloadableWithoutMagazine=True (SEST RAN Fleet).
- These are SEST gameplay rules, not proof of real-world handling.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| sea area: Indian Ocean | Indian Ocean presence anchor | source | R01:55 |
| io_diego_garcia_nsf | Allied transit / rendezvous link, ~2,840 NM; route unvalidated | authored | none |
| aus_tindal_raaf | National network link, ~1,400 NM; no air cover implied | authored | R01:55 names both, no relationship stated |
| sea area: Strait of Malacca | Northern transit / patrol reach, ~2,130 NM | authored | R03:7 (chokepoint; no forward operating location named) |
| `airbase_raaf_pearce` (SEST named base, not a register node) | Nearest named RAAF base, context only | authored | proposed backlog addition (not in source-register expansion_backlog; listed in the collection inventory) |

**Routine activity (proposed, not implemented)**
- **Submarines:** a three-boat cycle (patrol, ready, maintenance) that swaps the same identities on return. The reserve boat is used only for relief.
- **Rankin:** patrols the authored box.
- **Frigates:** Warramunga patrols the Indian Ocean approaches and holds a rendezvous with Stalwart, which also exercises the ship-ammunition test.
- **OPV:** Eyre patrols off Cockburn Sound.
- **Neutral traffic** (scenario population, not research):
  - Fremantle-area shipping: `anl_ms_bulk` V1 (Australia; exact), `civ_ms_act_1` (Australia container; proxy, a 1970s-80s design, NameOverride 'period container ship (stand-in)', installations lens mappings[62]), and `civ_ms_bulk` (a Liberia or Greece variant; exact).
  - `civ_a330` Squadron61 (Australia) overflight near Perth. It is the region's only Australian airliner and is allocated here only (group `asset:ausio:civ_air`).
  - Avoid `ran_ms_bulk` (Role=Spy) and `civ_ms_freighter_b`, which carries an unlimited RE-power supply block.

**Validation**
- **Research:** one-line source.
- **Mapping:** combatants exact; stand-ins proxy; port missing_fit; the `civ_ms_act_1` traffic hull is a labelled proxy.
- **Placement and runtime:** pending and untested.

**Gaps**
- No port service.
- No Hunter class.
- The AUKUS presence is unsourced.
- No maritime patrol aircraft at the node. RAAF P-8 squadrons exist (`usn_p8` Squadron3, `usn_p_8a` Squadron21/22), but their base is not a register node.
- Pearce, Learmonth and Curtin are SEST named bases but not research nodes. They are proposed backlog additions, not existing source-register expansion_backlog entries.
- The marker placement is unproven.

---

### aus_tindal_raaf - RAAF Base Tindal

**Identity**

| Field | Value |
|---|---|
| Operator | Royal Australian Air Force |
| Host | Australia |
| Kind | air_base |
| Policy | **populate_small** |

**Reuse:** `airbase_raaf_tindal` already exists as a named SEST airbase unit (SEST RAAF Bases) with an air group, and it is reused here.
- Shipped air group: F-35A Sq3 x12, F-15EX Sq5 x8, B-52H x4, B-2 x2, KC-135 x2, MQ-9A x4, MQ-4C Sq2 x2.
- That group is SEST campaign-authored and is not research-sourced.
- Re-checked against R01:55, it is replaced by a smaller CustomAirGroup override at placement. This uses the existing mission-level mechanism.

**SOURCE CLAIMS**
- **R01:55:** In the remote Northern Territory, Tindal is a primary military air base capable of hosting strike fighters and long-range allied bomber deployments.

**CHECK**
- R01:55 describes capability, not resident assignment, and names no types.
- The location is inland. Check its maritime relevance.
- The pairing of No. 75 Sqn with Tindal comes from the SEST squadron file comment, not from the research.
- `dts_b-52h` offers nuclear-tagged loadouts, so pin a conventional loadout.
- If the shipped F-15EX were kept, its Strike183N loadout would also need excluding.

**Role:** aviation, as a forward fighter and bomber deployment base.

**Position**
- **Public location:** about -14.5, 132.4 (approx, verify).
- **In-game evidence:**
  - `airbase_raaf_tindal` is placed at -14.521, 132.378 in SEST 'Southern Watch 05 - Weapons Free' (MapCenter -9.0/131.0, `RelativePositionInNM=82.67,low,-331.27`, Heading 90).
  - SEST Banda Front and Indo-Pacific Land Assets use the same point, within about 0.1 NM of the public coordinates.
  - 'Southern Watch 06' decodes to -14.48, 132.47, about 6 NM ENE. Prefer SW05.

**Forces (SCENARIO CHOICES)**

| Asset id | Allocation | Role | Unit id (squadron) | Qty | Outcome | Source basis | Notes |
|---|---|---|---|---|---|---|---|
| asset:ausio:tindal_base | resident_at_base | Named airbase (reused SEST unit) | `airbase_raaf_tindal` Variant1 (Nation=Australia), CustomAirGroup=True | 1 | exact | R01:55 | AircraftCapacity 200. No FlightDeck_AmmoCapacity. |
| asset:ausio:tindal_f35a | resident_at_base | Strike fighters | `raaf_f-35a` Squadron3 'No. 75 Squadron RAAF' (Nation=Australia) | 4 (shipped: 12) | exact | R01:55 'strike fighters' (types not named) | Squadron pairing is SEST-authored. Four aircraft (two pairs) keep the presence small under populate_small; one pair flies the proposed activity. |
| asset:ausio:tindal_mq4c | patrol | Maritime ISR orbit (optional) | `raaf_mq-4c_triton` Squadron2 'MQ-4C Det Tindal' (Nation=Australia) | 1 | proxy (label it 'MQ-4C (MQ-9 ER mesh stand-in)') | not sourced | Flies the MQ-9 ER mesh: `ResourcesRoot=mq-9.obj`, integration/adf-persistent-isr/README.md:3-5, and the SEST aircraft_names description ('Flies the collection's MQ-9 ER mesh as an accepted stand-in'); also us-air-and-land lens mappings[16] and gaps[3]. Depends on 3503670861. |
| asset:ausio:tindal_bomber_det | reserve (not placed) | Long-range allied bomber deployment | `dts_b-52h` Squadron1 '2nd Bomb Wing' (Nation=US) | 2 | exact | R01:55 capability | Separate airframes from asset:ausio:dg_b52_det. Arrives only on a scenario trigger. |

Shipped entries not adopted (SEST-authored and unsourced; still available for a later labelled rotation):
- F-15EX x8.
- B-2 x2. Leaving these out avoids a second B-2 detachment in the region.
- KC-135 x2, MQ-9A x4.
- The extra Triton and the B-52H x4.

The fixed defences that existing SEST missions authored around Tindal are not adopted:
- Fuel tanks, ammunition depot, HEMTT, SHORAD, Patriot, THAAD and `wp_an_tpy_2`.
- They are campaign content, not sourced, and the verify pass found `wp_an_tpy_2` to be a non-passive radar (3,000 km range, datalinked).

**Support services**

| Service | Status |
|---|---|
| Aircraft turnaround / ordnance | The base has no FlightDeck_AmmoCapacity, so its stock is the undocumented engine default and is untested. Finite stock needs a per-mission FlightDeck_ override or a change to the clone. |
| Aerial refuelling | Not established. `raaf_f-35a` declares no ReceiverSystems, `aus_a330_mrtt` is ProbeAndDrogue, and the modded KC-135 lacks [AerialRefueling]. |
| Land-unit resupply | `tgt_ammo_depot_small` serves LandUnit targets only (200,000 AP, 1.5 NM). Relevant only if ground units are placed. |
| Fuel | Not established. |
| Repair | Not established. |
| Restocking | Not established. |

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| io_diego_garcia_nsf | Bomber rotation alternate, ~3,550 NM (origin of allied bombers unnamed) | authored | R01:55; R03:40 |
| wpac_guam_andersen_afb | Bomber deployment routing, ~1,830 NM | authored | R03:38 (bombers dispatched from Guam; site not named) |
| aus_stirling_hmas_stirling | National network link | authored | none |
| `airbase_raaf_darwin` (SEST named base, not a register node) | Context only | authored | proposed backlog addition (not in source-register expansion_backlog) |
| sea area: Timor / Arafura Sea | ISR orbit area | authored | none |

**Routine activity (proposed, not implemented)**
- **F-35A:** a pair flies training or CAP sorties over the Top End.
- **MQ-4C:** an ISR orbit over the Timor / Arafura Sea.
- **Bomber detachment:** arrives from reserve on a scenario trigger and later departs. It is finite.
- **Neutral traffic:** none. The optional `civ_a330` Australia overflight was dropped: that airliner is allocated to the Perth overflight in the Stirling package, and each airliner has one allocation.

**Validation**
- **Research:** one-line capability claim.
- **Mapping:** exact.
- **Placement:** proven.
- **Runtime, save/load and turnaround:** untested.

**Gaps**
- Finite ordnance stock is undefined.
- No aerial refuelling.
- No sourced aircraft types.
- The bomber origin is unnamed.
- There is no evidence for fixed defences.
