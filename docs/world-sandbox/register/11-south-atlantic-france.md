<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Region summary: South Atlantic outpost and French strategic context

This region has three nodes. Two are populated small: RAF Mount Pleasant and Mare Harbour, which work as a pair. One is context only: Ile Longue.

Every package keeps three labels apart:
- **SOURCE CLAIM** is what R01-R03 say, cited by report and line.
- **CHECK** is a known doubt or a verification still needed.
- **SCENARIO CHOICE** is our proposed allocation, quantity or activity.

Repetition across reports is not corroboration: R01:59 and R02:71 repeat R03 almost word for word. All routine activity is proposed and not implemented. Every unit id was re-resolved on branch sest-dev/sweet-lovelace-3kxsve with `find_unit_file`/`winning_file` (integration/missions/refine_civ_traffic.py). The inventory corrections are applied: Typhoon Squadron1 is "1(F) Squadron", so the packages use Default. The Voyager has no 10/101 Sqn names. The Tide is relabelled proxy (stand-in mesh). The Falklands placements come from mod 3491248180 "The Royal Navy" and lie at Goose Green and Stanley. UK-flagged ports exist only as hidden British-Isles world-database ports. The source-register fidelity fixes are also applied: R02:71 says "alongside", so the A400M's flight is ambiguous in both R02:71 and R03:144. The R03:144 role sentence is added. The R02:67 referent is corrected, and the nuclear exclusion is cited as seed:25.

Placed scenario footprint, kept deliberately small:
- **Mount Pleasant:** one base, 4 Typhoon, 1 Voyager, 1 A400M, 2 GBAD stand-in launchers and 1 civil airliner. Of the 4 Typhoon, 2 are parked for QRA in the base air group and 2 are the CAP pair, spawned airborne with the base as HomeBase. The base air group holds only the aircraft at the base, so no airframe is counted twice.
- **Mare Harbour:** one jetty, HMS Forth, one sealift charter in transit (`civ_ms_amra` Variant1), one Tide as a dormant reserve (`rn_aor_tide` Variant3, a stand-in hull), and 3 fishing vessels.
- **Brest approaches (scenario only):** 1 FREMM ASW with its NH90, 1 optional Atlantique 2, 2 fishing vessels and 2 merchants.
- **Triomphant:** none placed.

This is not a carrier battle (plan, South Atlantic row).

Findings that matter most (re-resolved here, not in the inventories):
1. **Voyager to Typhoon refuelling is missing_fit.** `uk_a330_mrtt` has a working RefuelSystem (ProbeAndDrogue tanker). Neither `raf_ef2000_fgr4` nor `raf_ef2000_fgr4_late` declares an `[AerialRefueling] ReceiverSystems=` block; 35 of 114 vanilla aircraft files declare one. `uk_a400m_airdroop-para` does declare `ReceiverSystems=ProbeAndDrogue`.
2. **No Sky Sabre (Land Ceptor) ground unit exists.** The CAMM round exists as `mbda_camm` (3629144864). The only UK ground-based air defence (GBAD) is vanilla `raf_rapier_launcher` (Default/Variant1 Nation=UK, variants from 3455404959), which serves as a labelled proxy.
3. **The proxy jetty `nv_pt_boats_docks` has an effectively unlimited shore supply** (AmmoCapacity 9,999,999,999). It must be disclosed or replaced by a finite UK clone.
4. **Falklands placement is unproven.** No vanilla unit lies within 959 NM. |z| = 5,629 from a 42N 20E centre is beyond played content (4,529). Pending probes P3b and P1 Variant C.
5. **`fr_ssbn_triomphant`'s only fit includes 16 M51 SLBMs,** alongside `fr__f21` torpedoes and `fr_sm39` missiles. No fit without the M51 exists, so it is not placed.

---

### satl_falklands_raf_mount_pleasant - RAF Mount Pleasant

**Identity:** United Kingdom (Royal Air Force). Host: Falkland Islands (UK). node_kind air_base. populate_policy **populate_small**. Source sections: R03:140-146, R02:69-71, R01:57-59.

**Role (SOURCE CLAIM):**
- Maintained "to secure the South Atlantic and project power into the Antarctic region" (R03:142).
- "Provides a base for air-defense and transport operations." Added per fidelity check 3 (R03:144).
- Joint-force complex, opened 1985, 2,589 m primary runway, the islands' only international airport (R03:142).
- Commanded by No. 905 Expeditionary Air Wing. No. 1435 Flight operates four Typhoon FGR4 (Tranche 1) for air defence of the Falklands, South Georgia and the South Sandwich Islands (R03:144).
- No. 1312 Flight operates an Airbus Voyager KC2 for air-to-air refuelling to sustain the fighters, "alongside" an A400M Atlas C1 (R02:71, R03:144). R02:71 gives the A400M "tactical transport and supply drops". R03:144 gives it "tactical transport, search and rescue, and maritime patrol".
- R01:59 repeats the Voyager KC2 and A400M pairing but names no flight. In R01:59 the Voyager refuels "to sustain fighter patrols" and the A400M is "for tactical supply drops".
- Sky Sabre detachment of the 7th Air Defence Group (R03:144; repeated within R03 at R03:162).
- A "vital transport and logistics hub" because of the distance from the British Isles (R02:71).
- R02:71 adds No. 1312 Flight and the hub rationale. Only R03 adds 905 EAW, 1435 Flight and the Typhoons, the 7 ADG and Sky Sabre, and the runway and airport details.

**Position:**
- Approximately -51.8, -58.4 (approx, verify). Probe P3b uses -51.823, -58.447.
- In-game evidence: none at the site. Workshop mod 3491248180 ("The Royal Navy"), mission "The Falklands War/Mission 1 - Baptism of Fire", places `nato_small_airbase` at -51.83, -58.98 (Goose Green/Darwin, about 20 NM west). It places `airfield_small_1` (per-unit Nation=argentina) at Stanley airport, -51.68, -57.75 (about 27 NM).
- No vanilla unit lies within 959 NM. Stock world data has nothing nearer than Port Buenos Aires and the Rio de la Plata sea point (about 960-1,050 NM).
- Stock terrain has Biome3=Falklands, but heightmaps are not in the repo.
- Builder B1 pool snapping fails (2,965 NM from the pool), so the land mask or a new coast extract is needed.
- Placement is pending P3b (terrain) and P1 Variant C (|z| 5,629).

**Forces**

| Asset id | Allocation | Role | Unit id (winning source) | Outcome | Scenario qty | Basis |
|---|---|---|---|---|---|---|
| asset:satl:mpa_airbase | support | Installation: airbase, aviation turnaround | Interim: `is_airbase_akureyri` Variant2 (vanilla, Nation=UK, named "RAF Gibraltar"; relabel visibly and replace its US CustomAirGroup). Alternative: `nato_small_airbase` (vanilla). Its Default/Variant1 are Nation=US and its default [AirGroup] is a US wing: F-15A ×8, F-4E ×24, E-3A ×2, RA-5C ×6, EA-6B ×4, P-3C ×8 and CH-46 ×2. It therefore needs a per-unit Nation=UK, a visible NameOverride and a CustomAirGroup. Target: a SEST clone of `airbase_us` (3592460366) on the integration/raaf-bases pattern. Whichever unit is used, its mission CustomAirGroup holds only the aircraft at the base: `raf_ef2000_fgr4_late` Default ×2, `uk_a330_mrtt` ×1 and `uk_a400m_airdroop-para` ×1 | proxy (a named Mount Pleasant base: none yet) | 1 | SOURCE CLAIM R03:142. SCENARIO CHOICE: unit pick. Avoid `is_airbase_reykjavik`, whose Default stock includes the TacticalNuke category |
| asset:satl:typhoon_qra | resident_at_base | Air-defence alert (QRA) | `raf_ef2000_fgr4_late`, squadron Default (3587877691) | exact (platform) | 2 | SOURCE CLAIM four Typhoon FGR4 (R03:144). SCENARIO CHOICE: 2 of the 4 on alert, parked in the base CustomAirGroup |
| asset:satl:typhoon_cap | patrol | Sovereignty CAP | `raf_ef2000_fgr4_late`, Default | exact (platform) | 2 | Same claim. SCENARIO CHOICE: the other 2, spawned airborne at start with HomeBase = asset:satl:mpa_airbase. They are not also in the base air group |
| asset:satl:voyager | support | Tanker / air bridge | `uk_a330_mrtt`, Default/Squadron1 "A330 MRTT Voyager" (3758943352) | missing_fit (the sourced function, refuelling the Typhoons, is missing; the platform is exact) | 1 | SOURCE CLAIM "an" Voyager KC2 (R01:59, R02:71, R03:144) |
| asset:satl:a400m | resident_at_base | Transport / airdrop | `uk_a400m_airdroop-para`, Default "A400M Atlas" (3758943352) | missing_fit (the sourced supply-drop, SAR and maritime-patrol functions are missing; the transport platform is exact) | 1 | SOURCE CLAIM "an" A400M Atlas C1 (R01:59, R02:71, R03:144) |
| asset:satl:sky_sabre_det | fixed_defence | Ground-based air defence | `raf_rapier_launcher` Variant1 (unit vanilla; variants 3455404959, Nation=UK). Label: "Sky Sabre (stand-in: Rapier)" | proxy (Sky Sabre itself: none) | 2 launchers | SOURCE CLAIM Sky Sabre detachment (R03:144). SCENARIO CHOICE: 2 placements; not a real deployment layout |
| asset:satl:civ_airliner | transit | Neutral civil airliner, scenario population | `civ_a330` Squadron49 (LAN livery, Nation=Chile; 3746453639) | proxy (representative airliner) | 1, occasional | SOURCE CLAIM only international airport (R03:142). SCENARIO CHOICE: type and airline |

**Support services**
- **Aircraft turnaround and ordnance:**
  - The interim `is_airbase_akureyri` has FlightDeck_AmmoCapacity 1,500,000. Its accountable categories are AirTorpedo, Ovod and Harpoon, none of which the Typhoon needs.
  - The Typhoon air-to-air missiles declare no SupplyCategory: `raf_aim-132` 310 pts, `eu_aim-120d-3` 710, `eu_aim-120c-5` 655 and `eu_aim-9l-i` 126 (3587877691).
  - Typhoon loadouts set ReadyUpTime=15 min.
  - A SEST clone of `airbase_us` declares no FlightDeck_AmmoCapacity, which leaves an undocumented engine-default stock.
  - Turnaround is untested in game.
- **Air-to-air refuelling:**
  - `uk_a330_mrtt` has `[SupplySystem1]` RefuelSystem: FuelCapacity 13,000 kg, 40 kg/s, 5 mi, 3 targets, TargetTypes=Aircraft, TankerSystems=ProbeAndDrogue.
  - CHECK: the RAF Typhoon files declare no receiver, so Voyager-to-Typhoon refuelling is missing_fit. The fix is a SEST patch adding `ReceiverSystems=ProbeAndDrogue`.
  - Voyager to A400M (which declares a receiver) is possible in data but untested.
- **Air supply drops:** the A400M "Supply" store (3758943352 ammunition/Supply.ini) is Type=Paratrooper, not a supply system. No resupply effect is established.
- **GBAD reload:** not established.
  - LandUnit suppliers exist in the collection (inventory lenses us-air-and-land and installations-placement-support). `usa_car_m923` (vanilla, Nation=US) has a pool of 4,500, MaxAmmoPoints 200 and a 0.5 mi range. `usa_car_hemtt` (3605013271, Nation=US) has 13,500 with the same 200-point cap. `tgt_ammo_depot_small` (vanilla, Soviet) has 200,000 with MaxAmmoPoints commented out. `wp_car_ural` (vanilla, Soviet) has 6,800, cap 200. `nv_headquarters` (3605013271, Vietnam) is effectively unlimited.
  - None of them is UK-flagged.
  - `raf_rapier` (vanilla) costs AmmoPoints=90, declares no SupplyCategory and is magazine-fed (AssociatedMagazine=WeaponMagazineMissile, 16 rounds per launcher). It passes the 200-point cap and both gates in data. A labelled `usa_car_m923` with per-unit Nation=UK could therefore reload the stand-in launchers in data: about 2,880 points for both launchers (computed).
  - SCENARIO CHOICE whether to add one. None is placed, and transfer is untested.
- **Ship ammunition:** none at this node (see Mare Harbour).
- **Fuel:** ground or airbase fuel not established.
- **Repair:** not established.
- **Supplier restocking:** not established.

**Connections**
- satl_falklands_mare_harbour: operates in tandem with it, about 5 NM (approx). Source: R01:59, R02:71, R03:146.
- satl_falklands_mare_harbour: Typhoons and HMS Forth intercept unregistered vessels and escort foreign military assets together. Source: R03:146.
- Area: the Falklands, South Georgia and South Sandwich Islands air-defence area. Source: R03:144. South Georgia is about 800 NM and the South Sandwich Islands about 1,150 NM away (approx).
- Area: South Atlantic (source-register area). Source: R01:59, R02:71, R03:142, R03:146. Reference only; no routes.
- Area: Antarctic region, a power-projection reference (source-register area). Source: R03:142. Reference only; no routes or activity.
- Air bridge to an off-register UK home base (Voyager and A400M arrivals and departures): authored. R02:71 gives only the distance rationale. No route or far-end node is named; it stays on the backlog.

**Routine activity (proposed, not implemented)**
- The QRA pair launches on a trigger (an unidentified air contact) and recovers to base.
- The CAP pair (the airborne spawn, HomeBase Mount Pleasant) flies a racetrack over East and West Falkland. The route must outlast the session, because aircraft orbit when their route ends (scope §2.11).
- A joint intercept of an unlicensed or unregistered fishing vessel with HMS Forth. R03:146 is the basis; the event itself is a scenario choice. Nationality does not make the vessel hostile.
- Voyager tanker track near the islands, only after the receiver fix. Until then, air-bridge departures and arrivals only.
- Air-bridge movements reuse the one asset:satl:voyager and the one asset:satl:a400m. They depart from and recover to the base air group, and no extra copies are spawned.
- A400M local transport or airdrop sortie and a visual search pattern. The SAR and maritime-patrol roles come from R03:144 but have no game function.
- Occasional civil airliner arrival and departure.

**Checks**
- R03:144 says Tranche 1. Neither RAF Typhoon file models tranche. `raf_ef2000_fgr4` carries AIM-9L and AIM-120C-5 loadouts; `_late` carries ASRAAM and AIM-120D-3 and adds AirToAirIntercept. Pick the file per scenario date. UK Tranche 1 retirement may change the variant.
- Whether the A400M belongs to No. 1312 Flight is ambiguous in both R02:71 and R03:144. R01:59 names no flight.
- Verify the Sky Sabre detachment. Do not fabricate present-day defences (plan:24).
- "Heavily fortified" (R03:142) and "constant air defence" (R03:144) are rhetorical. No invulnerability, perfect-coverage or permanent-CAP rule follows from them.
- Reaching South Georgia or the South Sandwich Islands probably depends on air-to-air refuelling, which is missing_fit in game. Do not author routine CAPs there until it works.
- Unit and squadron naming: no 1435 Flight, 1312 Flight or 905 EAW names exist. Default names are used.
- The same unit files appear in other regions (Akrotiri). Asset ids here are distinct identities.
- Airframe count: this node holds 4 Typhoon, 1 Voyager and 1 A400M. The base air group holds Typhoon ×2, Voyager ×1 and A400M ×1, and the CAP pair is the only airborne spawn. Whether the airborne pair can recover into a base with a CustomAirGroup is untested. AircraftCapacity is 60 on the interim base and on `nato_small_airbase`, and 200 on `airbase_us`.

**Gaps**
- No named Mount Pleasant base. A SEST clone is needed: Nation=UK, with an AirGroup that holds only the aircraft at the base (`raf_ef2000_fgr4_late` Default ×2, `uk_a330_mrtt` ×1 and `uk_a400m_airdroop-para` ×1). The CAP pair is the other 2 Typhoons, spawned airborne with this base as HomeBase.
- No 1435 Flight or 1312 Flight squadron names (a name patch is needed).
- No Sky Sabre/Land Ceptor ground launcher. `mbda_camm` exists, so a SEST land-unit clone is the fix path.
- Typhoon air-to-air refuelling receiver missing.
- No UK-flagged LandUnit supplier for the GBAD stand-in. A re-nationed, labelled `usa_car_m923` is the path in data.
- A400M supply-drop, SAR and maritime-patrol functions missing (missing_fit).
- No modern UK SAR or support helicopter, but none is sourced either.
- Falklands terrain unverified (P3b) and z-extent unproven (P1 Variant C).
- No South Atlantic stock world-data points for routes.
- `nato_ewr_station` Variant2 (UK) exists, but no radar is sourced at Mount Pleasant. It is not populated.

---

### satl_falklands_mare_harbour - Mare Harbour

**Identity:** United Kingdom; supports the Royal Navy. Host: Falkland Islands (UK). node_kind naval_base. populate_policy **populate_small**. Source sections: R03:146, R02:71, R01:59. Fidelity check 1 found no further place-specific claims.

**Role (SOURCE CLAIM):**
- Operates in tandem with Mount Pleasant and supports the Royal Navy's permanent South Atlantic "patrol ships" (R01:59).
- "Supports and resupplies" those patrol ships (R02:71).
- Hosts "the" permanent South Atlantic patrol ship: since 2020 primarily HMS Forth (P222), a River-class Batch 2 OPV in service since 2018 (R03:146).
- HMS Forth conducts counter-piracy, fishery-protection and sovereignty patrols. R03:146 gives 5,500 nm range, 25 kt and 35 days endurance. These are R03's figures, not build parameters.

**Scale (SCENARIO CHOICE, per plan:42; not a source claim):** a single patrol ship's support facility, not a fleet base.

**Position:**
- Approximately -51.9, -58.5 (approx, verify), about 5 NM from Mount Pleasant.
- In-game evidence, sea placements about 29 NM away: Workshop 3491248180 "Falklands Testing" places `rn_ff_rothesay` at -51.66, -59.14 (Falkland Sound). Its mission "Mission 1 - Baptism of Fire" places neutral merchants off Stanley at -51.66, -57.78.
- No vanilla unit lies nearby.
- Builder B2 accepts offshore points here unvalidated, so the land mask (fix_land_positions.py) is needed. Placement is pending P3b.

**Forces**

| Asset id | Allocation | Role | Unit id (winning source) | Outcome | Scenario qty | Basis |
|---|---|---|---|---|---|---|
| asset:satl:mare_harbour_jetty | support | Installation: jetty, ship service | `nv_pt_boats_docks` (3605013271), per-unit Nation=UK, label "Mare Harbour (stand-in)". Marker-only alternative: `ran_pt_boats_docks_small` (3455404959). It displays "RAN base small" or HMAS Waterhen, Cairns or Coonawarra (Nation=Australia) and has no [SupplySystem]. It would be missing_fit for the R02:71 resupply role (allies-and-hosts inventory correction for `ran_pt_boats_docks`), and it needs a per-unit Nation=UK and a NameOverride if used | proxy (`nv_pt_boats_docks`, which carries the service; the marker alternative would be missing_fit) | 1 | SOURCE CLAIM supports and resupplies the patrol ship (R02:71). SCENARIO CHOICE: unit pick |
| asset:satl:hms_forth | patrol | South Atlantic patrol ship | `rn_opv_river_batch2` Variant1 "(P222) HMS Forth" (unit SEST_Integration; variants 3599752717; Nation=UK, ServiceDate 2018) | exact | 1 | SOURCE CLAIM R03:146. SCENARIO CHOICE: underway on patrol at start, so not also at the pier |
| asset:satl:sealift_charter | transit | Authored resupply charter or RFA stand-in | `civ_ms_amra` Variant1 "MV Strathcarrol" (Nation=UK; unit 3605013271, variants vanilla), with a mission NameOverride "Authored charter (stand-in hull)". This hull is reserved here world-wide | proxy | 1, periodic | SCENARIO CHOICE (not sourced) |
| asset:satl:rfa_tide_relief | reserve | Finite at-sea relief supplier (dormant) | `rn_aor_tide` Variant3 "A138 RFA Tidesurge" (SEST_Integration; usn_aoe_sacramento mesh), with a mission NameOverride "RFA Tidesurge (stand-in hull)". Only Default's display name carries "(stand-in)". This hull is reserved here world-wide | proxy (inventory correction) | 1, optional | SCENARIO CHOICE (not sourced). Roster or dormant: Disabled=True plus a trigger |
| asset:satl:civ_fishing | underway_deployed | Neutral fishing traffic in the patrol area | `civ_fv_sterntrawler_b` Default/Variant1 (UK, vanilla); `civ_fv_okean` Variant6 (Spain) or Variant4 (UK) (vanilla) | proxy (period hulls) | 3 | Fishery protection (R03:146). SCENARIO CHOICE: numbers and flags |

**Support services**
- **Ship ammunition, shore:**
  - `nv_pt_boats_docks` `[SupplySystem1]` TruckSupplySystem: AmmoCapacity 9,999,999,999 (effectively unlimited), no MaxAmmoPoints, 3 mi range, 6 targets, own speed ≤5 kt, receiver ≤10 kt, TargetTypes=Vessel, no accountable categories.
  - HMS Forth carries `eu_30mm_bushmaster` ×3,500 (0.67 pts each) and `nato_03cal` ×8,000 (0.01 pts each). Both are magazine-fed and declare no SupplyCategory, so they pass the category and launcher gates (integration/replenishment/README.md). A full reload is about 2,425 points (computed).
  - Transfer is untested in game. SCENARIO CHOICE: use a finite UK-flag SEST clone before relying on it, or disclose the unlimited stock.
- **Ship ammunition, at sea (optional):**
  - `rn_aor_tide` TruckSupplySystem: pool 180,000, MaxAmmoPoints 5,000, 90 pts/s, 0.6 nm, 2 targets, own ≤13 kt, receiver ≤16 kt, TargetTypes Vessel and Submarine.
  - Accountable categories: Harpoon 16, AirTorpedo 32, SEST_LandAttack 8, SEST_LongRangeSAM 16. Forth's gun rounds are uncategorised.
  - Its own Sea Ceptor magazine refills for free, a documented accepted exception.
- **Charter:**
  - `civ_ms_amra` TruckSupplySystem: AmmoCapacity 12,000,000, no ceiling, 1.5 mi, ≤10 kt, TargetTypes=Vessel.
  - This makes it a latent near-unlimited supplier. Its behaviour when neutral is untested.
  - SCENARIO CHOICE: treat it as a cargo arrival. Do not use it as Forth's rearm path unless that is chosen and disclosed.
- **Supplier restocking:** not established. No port restocks a supplier, and the charter does not restock the jetty.
- **Ship fuel:** not established.
- **Repair:** not established.
- **Aviation:** none. The River B2 unit declares no AircraftSupported or flight deck.

**Connections**
- satl_falklands_raf_mount_pleasant: in tandem. Source: R01:59, R02:71, R03:146.
- Joint intercepts and escorts with the Mount Pleasant Typhoons. Source: R03:146.
- Area: South Atlantic patrol area. Source: R03:146.
- Sealift arrival lane from the north: authored. Route geometry is unvalidated, and stock sea points south of 25S are only Table Bay and the Rio de la Plata.
- Dormant Tide relief arrival and replenishment-at-sea (RAS) rendezvous with Forth: authored.

**Routine activity (proposed, not implemented)**
- HMS Forth runs a finite fishery and sovereignty patrol circuit around the islands (R03:146) and returns to Mare Harbour to rearm.
- Fishing vessels work the patrol area.
- One scripted unlicensed-vessel intercept with Typhoon support (scenario).
- An optional escort of a transiting foreign warship (R03:146 wording). Nationality does not make it hostile.
- The charter arrives periodically, berths and departs.
- The Tide is woken by trigger only for a finite relief.

**Checks**
- "Since 2020" is dated. Check the current guardship at the scenario date. The other hulls in the unit file (Medway, Trent, Tamar, Spey) must not duplicate Forth.
- R03:146 says one patrol ship; R01:59 and R02:71 say "patrol ships". SCENARIO CHOICE: one ship.
- The game unit's speed and endurance have not been compared with R03:146's figures.
- No hull may be allocated twice across regions. This package reserves `rn_opv_river_batch2` Variant1 (Forth), `rn_aor_tide` Variant3 (Tidesurge) and `civ_ms_amra` Variant1 (Strathcarrol). Other River B2 hulls may be used elsewhere. So may the other Tide variants (Variant1 Tidespring, Variant2 Tiderace, Variant4 Tideforce; the inventory also maps the Tide to Akrotiri, Bahrain and Diego Garcia) and other Amra hulls.

**Gaps**
- No UK port unit. UK-flagged ports exist only as hidden, British-Isles-named world-database ports, so a finite UK-flag SEST jetty clone is the fix.
- No HMS Protector or ice-patrol ship, none of which is sourced.
- No Fort Victoria, Wave or Bay class.
- Ship fuel and repair are absent.
- In-game rearm of Forth is untested.

---

### eur_brest_ile_longue - Île Longue

**Identity:** France (Marine Nationale). Host: France, in the Brest roadstead. node_kind naval_base. populate_policy **context_only**. Source sections: R03:148-152, R02:65-67, R01:61.

**Role (SOURCE CLAIM):**
- Located on a peninsula in the Brest roadstead. Described as the most secretive and heavily defended French installation. The exclusive base of the Force Océanique Stratégique (R03:150).
- Hosts four Triomphant-class submarines. Fusiliers Marins provide perimeter defence (R03:152).
- R02:67 says France's strategic deterrence relies on [secure handling at Île Longue, not extracted], the base for its ballistic-missile submarine force. The referent is corrected per fidelity check 3.
- R01:61 repeats this.

**Policy: why context only (plan:43; seed:25; not a source claim):**
- Only the bare fact of a strategic submarine force is recorded. Zone layouts, storage, covered docks, the loading bunker and missile works are deliberately excluded (seed:25; plan:43).
- No report describes a conventional Brest naval base or surface units; that item is on the expansion backlog.
- No French base unit exists in the collection.

**Position:**
- Approximately 48.3, -4.5 (approx, verify).
- Stock world data: `campaigns/ports.ini [Port Brest Fr]` at 48.3904, -4.4861, Nation=France, no LandUnit, about 5 NM away.
- `sea_links.ini [Ushant - Brest]/[Brest - Ushant]` connect to the Ushant TSS points (48.90, -5.80 and 48.78, -5.60), about 52-62 NM away.
- `patrol_areas.ini [Manche Fishing]` lists Port Brest Fr as a civ_fv_ spawn.
- No proven mission placement lies within 138 NM (sea) or 481 NM (land). B1 pool snapping is 512 NM away, and builder east-west distances are ×1.49 here (B6).
- Proposed Brest approaches (Iroise) patrol box: approximately 48.15-48.33N, 4.8-5.2W (approx, verify), mostly open water west of Crozon and south of the Molène archipelago. CHECK: the Les Pierres Noires reef and lighthouse (about 48.31N, 4.91W) lies inside the box, and Béniguet (about 48.35N, 4.88W) lies just north of it (approx, verify; outside knowledge, below the land mask's resolution). Keep waypoints clear of both.
- The earlier 48.2-48.4N, 4.7-5.2W box took in the Pointe Saint-Mathieu and Le Conquet shore. A global-land-mask scan at 0.01° found land at 48.34-48.40N, 4.70-4.78W, and none in the trimmed box. Islets and reefs below the mask's resolution remain a CHECK.
- Run integration/missions/fix_land_positions.py (global land mask) on every waypoint before placement.

**Forces**

| Asset id | Allocation | Role | Unit id (winning source) | Outcome | Scenario qty | Basis |
|---|---|---|---|---|---|---|
| asset:eur:ile_longue_ssbn_force | abstract | Strategic submarine force (bare fact) | `fr_ssbn_triomphant` (3567256221). Its only fit includes `fr__m51` ×16, besides `fr__f21` ×18 and `fr_sm39` ×8. No fit without the M51 exists | missing_fit | 0 placed | SOURCE CLAIM four Triomphant-class (R03:152). Not placed, no movements, no nuclear detail |
| asset:eur:ile_longue_site | abstract | Installation (context) | none. `nv_pt_boats_docks_small` exists but is not proposed: its submarine supply would depict SSBN servicing | none | 0 | SOURCE CLAIM R03:150 |
| asset:eur:brest_fremm_asw | patrol | Conventional ASW presence in the Brest approaches | `fr_ffg_aquitaine_asw` Variant1-4 (D650, D652, D653, D654) or `fr_ffg_aquitaine_modernized_asw` Variant1/2 (D651 Normandie, D655 Bretagne); both 3567256221, WIP mod, Nation=France. Variant pick pending. The placement must set CustomAirGroup=True with `fr_nh90=Squadron1,1`, because both files' default [AirGroup] is `fr_nh90=Squadron1,10` against AircraftCapacity=1 | exact | 1 | SCENARIO CHOICE (not sourced) |
| asset:eur:brest_fremm_nh90 | patrol | Embarked ASW helicopter | `fr_nh90` Squadron1 (3567228449). It is the FREMM's one embarked helicopter, its CustomAirGroup row, and not a separate spawn (AircraftSupported, capacity 1) | exact | 1 | SCENARIO CHOICE |
| asset:eur:brest_atl2 | patrol | Maritime patrol over the approaches | `fr_atl2` Squadron1/2 (21F/23F; 3567256221) | exact | 1, optional | SCENARIO CHOICE. Home base off-register, spawns airborne |
| asset:eur:brest_civ_fishing | underway_deployed | Neutral fishing traffic | `civ_fv_sterntrawler_c` Default/Variant1 (France); `civ_fv_okean` Variant5 (France) (vanilla) | proxy (period hulls) | 2 | SCENARIO CHOICE (stock Manche Fishing spawn) |
| asset:eur:ushant_civ_merchants | transit | Neutral merchants on the Ushant TSS | `civ_ms_ritina` Variant76-79 (France); `civ_ms_car_carrier_a` (vanilla). Neither has a supply block | proxy (representative) | 2 | SCENARIO CHOICE |

**Support services**
- Not established. No French base unit exists, no French replenishment ship exists (outcome none), and no French vessel carries a supply system.
- FREMM rearm: not established.
- Atlantique 2 turnaround: not established (no French air base node).
- Fuel and repair: not established.
- Port Brest Fr is world data only, with no supply.
- Do not borrow allied suppliers unless that is authored and disclosed.

**Connections**
- Area: Brest roadstead. Source: R03:150.
- Stock world data, Port Brest Fr and the Ushant TSS sea links: authored use.
- Backlog: Brest naval base and French Atlantic surface forces (source-register expansion_backlog).
- No source link to any other world node.

**Routine activity (proposed, not implemented)**
- The FREMM ASW patrols the Iroise and Brest approaches, with NH90 sorties.
- The optional Atlantique 2 flies a long-endurance track that outlasts the session.
- Fishing traffic from Port Brest Fr; merchants on the Ushant TSS.
- No strategic-submarine departures, escorts of strategic transits, deployment cycles or nuclear detail.

**Checks**
- "Most secretive and heavily defended" is rhetorical. No fabricated defences (plan:24).
- Mod 3567256221 is catalogued as WIP.
- The FREMM variant and home port need checking. The candidates are `fr_ffg_aquitaine_asw` Variant1-4 and `fr_ffg_aquitaine_modernized_asw` Variant1/2 (D651, D655). The allies-and-hosts inventory verify pass lists the modernized unit as unmapped, and it has the same AirGroup quirk. Coordinate with the Horn of Africa and Arabian Sea packages so that no French hull is allocated twice.
- Never place the FREMM with its default air group (10 NH90 against a 1-aircraft deck). The engine's behaviour in that case is undocumented.
- Never use `fr_rafale_b_l_nuclear` or `fr_rafale_m_l_nuclear`.
- The Triomphant appears only as abstract context.

**Gaps**
- No French naval base unit.
- No M51-free Triomphant fit (not proposed).
- No French replenishment ship.
- No French air base node for the Atlantique 2.
- Brest placement is unproven and needs the land mask.
- Brest naval base is not described in R01-R03 (backlog).
