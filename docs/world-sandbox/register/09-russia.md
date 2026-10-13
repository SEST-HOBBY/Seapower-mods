<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Russian long-range aviation and northern/Pacific maritime context

**Scope.** This region has four sourced nodes, all of them air bases: Olenya (Kola), Engels-2 (Saratov), Ukrainka (Amur) and Belaya (Irkutsk). Every node-specific claim comes from one R03 section (R03:64-89), plus R03:160-162; the sea-area context draws on R03:66, R03:115, R03:117, R03:121 and R03:166. R01:41 is a one-paragraph summary that repeats R03's sentences, and repetition is not corroboration. R02 says nothing about Russia. No report names a Russian naval base. In naval terms, the Barents Sea and the Sea of Okhotsk appear only as SSBN "bastions" (R03:66), and Kola only as a submarine departure area (R03:115, R03:166). The Barents Sea is also the airspace of the Tu-142/Tu-95 intercepts (R03:117), and Kola is Olenya's location (R01:41, R03:70).

**Approach (SCENARIO CHOICE).** Each node gets a small bomber detachment with a visible label. Quantities sit far below the report snapshots: Olenya has 6 Tu-22M3 proxies, 2 Tu-95MS and 1 Tu-160 against "up to 35 / 10 / several" (R03:72), and Belaya has 3 against "historically up to 42" (R03:80). Engels, Ukrainka and Belaya are populate_small. If the active scene is maritime, they can be held as off-map raid origins. A small naval context with no home port is proposed for the two bastions; the fleet bases go to the backlog.

**Collection headline.** All ids were re-resolved with find_unit_file on this branch.
- exact: wp_airbase_1 'Olenya Airbase' (Default variant), wp_airbase_modern Variant1 'Engels airforce base', wp_tu95ms (Tu-95MS), wp_tu-160 (Tu-160), wp_tu-142m.
- proxy: wp_tu-22m2 for Tu-22M3; wp_tu-160 for Tu-160M; wp_il-76md for An-12 (newly resolved: Nation=Soviet, no supply system); wp_airbase_modern Default for Ukrainka and Belaya.
- none: hardened aircraft shelters; Russian submarine-base and Pacific land units.
- The in-game tanker wp_il-78 (probe and drogue) cannot refuel the Tu-95MS or Tu-160, because neither declares ReceiverSystems.
- wp_tu95ms is exact for name and loadout only with LandAttack (KH-101) or Default (KH-555). Its StrikePrecision loads KH-55, the same nuclear-effect model as the excluded wp_tu-160 StrikeNuclear, and its CAS loads KH-55SM; both are excluded on every Tu-95MS row. The file declares Role=MPA,ASW on the Tu-142M mesh, so AI tasking as a bomber is untested (CHECK).

**Operator keys.** Unit files use Nation=Soviet. Repo missions use Nation=russia / russia_navy and the registered flag_rus / flag_civ_rus (russia-lens verify correction). Use those mission keys rather than new textures.

**Positions.** All four nodes lie within about 4,100 NM of the candidate world centre 42N 20E. That is inside the 8,781 NM range of units that have already loaded and been saved (scope report section 2.2), and none is near the date line. Distance to the nearest proven repo placement: Olenya 44 NM by air and 69 NM by land; Engels 726 NM, Ukrainka 590 NM and Belaya 1,271 NM. Inland terrain is untested. Absolute GeoPosition placement exists (MFI:436-440), but no SEST tool writes it. The coordinates below are public approximations (approx, verify), not R01-R03 data.

**Single allocation.** The Russian aircraft that Evenes QRA intercepts (R03:117) are allocated here, as asset:rus:olenya_tu95ms_2 and asset:rus:olenya_tu142_1. The Kola-departing submarine that Evenes P-8As hunt (R03:115/166) is asset:rus:barents_ssgn_1. Other regions should reference these assets, not duplicate them. The two Olenya patrol aircraft are airborne at t0 and are not also listed in the Olenya CustomAirGroup. Belaya's optional tanker is asset:rus:belaya_il78_opt, a separate airframe from asset:rus:olenya_il78_1.

#### Regional naval context (sea areas, not node packages) - SCENARIO CHOICE

**SOURCE CLAIM:**
- The Barents Sea and the Sea of Okhotsk are "heavily defended coastal 'bastions'" that protect ballistic-missile submarines (R03:66).
- Russian submarines leave Kola for the GIUK Gap and must first evade Evenes P-8As (R03:115, R03:166).
- The JMSDF network is aimed at Russian Pacific Fleet movements (R03:121).
- No ship or base is named.

**CHECK:** Hull-to-fleet allocation comes from general knowledge (russia lens), so use the class Default variant until a named hull's fleet is verified. Every hull below is underway with no home pier assigned.

**CHECK (SSBN posture):** the wp_ssbn_borei unit file carries a live strategic-weapon system (not detailed here). Leaving out launch orders does not stop the AI from using it under weapons-free. The SSBNs stay presence or hunt objectives only. Place wp_ssbn_borei only after a test run shows it holds a verified non-engagement / weapons-hold posture and never fires that system. Until this CHECK passes, represent the R03:66 bastion presence abstractly as a sea-area marker and do not place the unit. No further weapon detail is recorded.

| Asset id | Unit id (variant) | Outcome | Allocation | Qty | Role / notes |
|---|---|---|---|---|---|
| asset:rus:barents_ssbn_1 | wp_ssbn_borei (Default; Variants 1-8 only) | exact | patrol | 0 until the posture CHECK passes, then 1 | Bare fact of a strategic submarine force in the Barents bastion (R03:66). Presence or hunt objective only: no launch orders and no nuclear or weapons-employment detail. Until a test run verifies a weapons-hold posture (CHECK above), the bastion is an abstract sea-area marker and the unit is not placed. |
| asset:rus:barents_ssgn_1 | wp_ssgn_yasen (Default) | exact | transit | 1 | Transit from Kola through the Norwegian Sea to the GIUK Gap (R03:115, R03:166). This is the boat Evenes hunts. |
| asset:rus:barents_ddg_1 | wp_bpk_udaloy_98 (Default) | exact | patrol | 1 | Authored ASW screen for the bastion. No report names a ship. |
| asset:rus:barents_aor_1 | wp_vt_boris_chilikin (Default) | exact | support | 1 | At-sea rearm in a Barents holding area. |
| asset:rus:okhotsk_ssbn_1 | wp_ssbn_borei (Default) | exact | patrol | 0 until the posture CHECK passes, then 1 | Bare-fact presence in the Okhotsk bastion (R03:66), with the same limits as above. Abstract sea-area marker until the weapons-hold CHECK passes. |
| asset:rus:okhotsk_ssk_1 | wp_ss_improved_kilo (Default or Pacific Variants 7-11) | exact | patrol | 1 | Authored. Variants 1-6 carry Black Sea names; avoid them (correction). |
| asset:rus:okhotsk_cvt_1 | rfn_cvt_20380_3-6 (Default) | exact | patrol | 1 | Authored coastal patrol. The Pacific hull candidates (Sovershennyy 333, Gromkiy 335) come from general knowledge; verify. The RFN_Flag.png binary is not in the mirror. |
| asset:rus:okhotsk_aor_1 | wp_vt_boris_chilikin (Default) | exact | reserve | 1 | A finite relief supplier, not a respawn. |
| asset:rus:barents_civ_fishing | civ_fv_okean (Default or Variant1) x2, civ_fv_sterntrawler_a (Variant1) x1 | missing_fit | transit | 3 | Neutral fishing, mission-placed as NeutralVessel entries with VariantReference set to the pinned variants, inside the area of the vanilla campaigns/patrol_areas.ini 'Barents Fishing' polygon (geometry precedent only; its Port Murmansk campaign spawns list civ_fv_fishingboat_a, civ_fv_okean and civ_fv_sidetrawler, not civ_fv_sterntrawler_a, and cannot honour a variant pin). Pin the variants: civ_fv_sterntrawler_a Default is Nation=Norway / flag_nor and Variant2 is DDR, so only Variant1 is Soviet; civ_fv_okean is Soviet only on Default and Variant1 (Variants 2-8 are Cuba, DDR, UK, France, Spain, Germany, Poland). The pinned variants carry the Soviet civil flag; then set mission Nation=russia / flag_civ_rus. |
| asset:rus:okhotsk_civ_fishing | civ_fv_okean (Default or Variant1) x2 | missing_fit | transit | 2 | Neutral fishing. Same variant pin (civ_fv_okean Default/Variant1 only) and flag fix. The stock sea network has no Pacific coverage. |

**Ship ammunition supply.**
- wp_vt_boris_chilikin [SupplySystem1]: AmmoCapacity 200000, MaxAmmoPoints 13000, SupplyRange 0.5 nm, MaxTargets 2, TargetTypes Vessel,Submarine. Categories: SovietAdvancedASM 24, AirTorpedo 40, SEST_LandAttack 16.
- It is the only open-dated supplier for rounds of 8,000-13,000 points, such as SS-N-14 (12000) on Udaloy_98.
- It passes wp_fizik-2 torpedoes (4695) and cannot pass SS-N-19 (21000).
- Unpriced, uncategorised Oniks and Kalibr variants on Yasen reload free from any Vessel+Submarine supplier (verify correction).
- port_ussr_severomorsk has no SupplySystem.

**Not established:** fuel transfer, repair and supplier restocking.

**Positions (approx, verify):**
- Barents patrol area 70.5-72.5N 33-40E. A sea point 1 NM off Severomorsk is proven in 'chapter 4 - Kill Kuznetsov'.
- Okhotsk 52-57N 145-150E. Unproven.

**Connection (authored):** the Okhotsk context links to the JMSDF nodes as their Russian Pacific Fleet counterpart (R03:121).

#### Backlog (not populated as sourced nodes)
- **Northern Fleet bases.** Severomorsk: port_ussr_severomorsk exists, is hidden from the editor, has a vanilla anchor at 69.0964,33.4313 and a Kola mission precedent. Gadzhiyevo, Vidyayevo, Polyarny and Zaozersk have no land units.
- **Pacific Fleet bases.** Vladivostok, Fokino and Vilyuchinsk / Petropavlovsk-Kamchatsky exist only as vanilla coordinate points, with no land units.
- **Tu-142 base(s)** (R03:117, R03:134): none named.
- **Kola naval airfields** (Severomorsk-1/-3, Kipelovo, Monchegorsk): no units.
- **Gremikha** (wp_large_pvo_airbase Variant1): Kola air defence context, not in the reports.
- **Kamenny Ruchey**: the language comment on wp_tu-22m2 Squadron7/8 reads 'Pacific Fleet'; airports.ini UHKG is at 49.2373,140.1915. Not in the reports.
- **Engels-2 dispersal 'secondary airfields'** (R03:78): unnamed.

---

### hn_kola_olenya_airbase - Olenya Airbase

**Identity.**
- Country: Russia. Operator: Russian Long-Range Aviation (R01:41, R03:70).
- Location: Kola Peninsula, Murmansk Oblast, "92 kilometers south of Murmansk" (R03:70).
- Kind: air_base. Policy: populate.

**Role (SOURCE CLAIM).**
- "One of the most critical installations for Russian Long-Range Aviation" (R01:41, R03:70).
- Table function: "Maritime/Land Strike, Staging" (R03:86).
- Home of the 40th Composite Aviation Regiment, operating Tu-22M3 "in maritime-attack and land-strike roles" (R03:72).
- Bombers "routinely fly extended combat sorties southward to launch standoff cruise missiles" from over 2,000 km away (R03:72). The register omitted this claim; it is restored here per the fidelity check.

**Other SOURCE CLAIMS.**
- R03:72: imagery from 2024 and 2025 "confirmed the presence of dozens of aircraft", "including up to 35 Tu-22M3 ..., 10 Tu-95MS ..., and several Tu-160 ..., alongside An-12 transport aircraft". The report frames this as an influx of bombers "seeking sanctuary".
- R03:74: during Operation Spider's Web (June 2025), "long-range autonomous drone swarms successfully navigated the immense distance to strike Olenya, damaging Tu-22M3 and Tu-95MS airframes".
- R03:70: the base is near the GIUK Gap, the North Atlantic and the Norwegian border.
- R03:162: redeployment to Olenya brings longer flights, more fuel, wear, maintenance failures and more adversary warning time.
- Table assets (R03:86): Tu-22M3, Tu-95MS, Tu-160, An-12.

**CHECKS.**
- The R03:72 counts are an unsourced 2024-25 imagery snapshot, not a standing order of battle, and may reflect dispersal. They are scaled down below as scenario choices.
- Verify the 40th Composite Aviation Regiment designation.
- The R03:74 attack mechanism is disputed. Widely reported accounts describe drones launched from trucks near the targets. Status after June 2025 is time-sensitive, and no specific losses are represented.
- "Sanctuary" (R01:41, R03:72) and "distance no longer guarantees immunity" (R03:74) are rhetoric. Do not derive a sanctuary, invulnerability or deterministic vulnerability rule from them (seed:23).
- The R03:70 Cold War and 1961 history is left out as a conservative choice under seed:25. The register's plan:43 citation is corrected to seed:25.
- **Collection.** wp_airbase_1 Default and Variant1 both display 'Olenya Airbase'. Variant1 carries a vanilla usn_f-14a CustomAirGroup, so use Default with a mission CustomAirGroup. This reconciles the two lens notes.
- **Collection.** Do not use wp_tu-22m2 Squadron2 '924th GuMRAP': its 'based in Olenya' comment would give the aircraft a Cold War regiment identity that conflicts with R03:72.
- **Collection.** Exclude nuclear loadouts: wp_tu-160 StrikeNuclear, and its Default Kh-55SM loadout. wp_tu95ms: LandAttack/Default only. Its StrikePrecision loads KH-55, which the winning ammunition file models with nuclear effects (the same munition as the excluded Tu-160 StrikeNuclear), and its CAS loads KH-55SM; exclude both. Prefer wp_tu95ms over wp_tu-95ms, which has Standoff and AntiShip Nuclear loadouts.
- **Collection.** wp_tu95ms declares Role=MPA,ASW. It is a Tu-142M-derived file (AssetBundleMesh wp_tu-142m, torpedo and sonobuoy stations in WeaponSystem1), so AI tasking as a bomber is untested. The outcome stays exact for name and loadout; verify behaviour in the placement or runtime test. This applies to every Tu-95MS row (Olenya, Engels, Ukrainka).
- **Collection.** wp_tu95ms display merge: a lower-priority language block (3732654992) mislabels it 'IL-78 203rd GARP'. The higher-priority 3715323261 wins key by key, giving 'Tu-95MS' / '315 regiment'. Confirm in game.
- **Allocation.** The Olenya CustomAirGroup holds only the at-base rows: Tu-22M2 4+2, Tu-95MS 1 (olenya_tu95ms_1), Tu-160 1, Il-76MD 1 and the optional Il-78 1. The patrol Tu-95MS (olenya_tu95ms_2) and Tu-142M (olenya_tu142_1) are placed as airborne units at t0. Alternatively they can be added to the group and launched at t0, but never both, so neither is counted twice.

**Position.**
- Approx 68.15N 33.46E (approx, verify; public knowledge, consistent with R03:70).
- In-game evidence:
  - wp_airbase_1, whose header says its layout is 'based on Olenegorsk/Olenya'.
  - No repo mission has placed it at these coordinates. The nearest proven placements are 44 NM by air and 69 NM by land.
  - One Kola positional precedent: 'chapter 4 - Kill Kuznetsov' (map centre 69.25,33.23), present in several copies, variants and backups (17 files under integration/missions and mods-source/_vanilla/user/missions). Its Russian ship ids are partly stale: 4 of its 7 surface-ship types do not resolve with find_unit_file.
  - port_ussr_severomorsk sits about 57 NM north (69.0964,33.4313), and airports.ini XLMF Afrikanda at 67.4567,32.7867.
- From the candidate centre 42N 20E: x about 808, z about 1,569 (about 1,630 NM). Runway and terrain fit for the heavy bombers is unvalidated.

**Forces (all quantities are SCENARIO CHOICES).**

| Asset id | Unit id | Outcome | Allocation | Qty | Source basis | Notes |
|---|---|---|---|---|---|---|
| asset:rus:olenya_base | wp_airbase_1 (Default) | exact | resident_at_base | 1 | R01:41, R03:70, R03:86 | Installation. AircraftCapacity 96. Replace the Cold War default AirGroup with a CustomAirGroup holding only the at-base rows below: Tu-22M2 4+2, Tu-95MS 1, Tu-160 1, Il-76MD 1, optional Il-78 1. The two patrol aircraft are airborne at t0 and are not also listed. |
| asset:rus:olenya_tu22m3_ready | wp_tu-22m2 (Default squadron) | proxy | resident_at_base | 4 | R03:72, R03:86, R01:41; quantity scaled from 'up to 35' | Label 'Tu-22M2 standing in for Tu-22M3'. Loadouts: AntiShip, AntiShipLongRange, StrikeLongRange. ProbeAndDrogue receiver. |
| asset:rus:olenya_tu22m3_svc | wp_tu-22m2 | proxy | servicing_maintenance | 2 | Scenario choice reflecting R03:74 damage and R03:82/R03:162 maintenance strain | Not a damage-state claim. |
| asset:rus:olenya_tu95ms_1 | wp_tu95ms (Default squadron) | exact | resident_at_base | 1 | R03:72 'up to 10', R03:86 | Loadout LandAttack (KH-101) only; Default (KH-555) is also conventional. Never StrikePrecision (KH-55, the nuclear-effect model also used by the excluded Tu-160 StrikeNuclear) or CAS (KH-55SM). No AAR receiver. May be a dispersal arrival (CHECK). Role=MPA,ASW file: bomber tasking untested (CHECK). |
| asset:rus:olenya_tu95ms_2 | wp_tu95ms | exact | patrol | 1 | Activity type from R03:117 (Tu-95 over the Barents, intercepted by Evenes; origin base not named). Basing here is a scenario choice. | Airborne at t0; placed as an airborne unit, not also listed in the base CustomAirGroup. Loadout Empty or LandAttack, never StrikePrecision or CAS. Role=MPA,ASW file: bomber tasking untested (CHECK). |
| asset:rus:olenya_tu160_1 | wp_tu-160 | exact | resident_at_base | 1 | R03:72 'several', R03:86, R01:41 | Staging or dispersal, not permanent basing (CHECK). Loadouts StrikeLongRangeKH101 / StrikeLongRange only. Generic 'TU-160' squadron. No receiver. |
| asset:rus:olenya_an12_1 | wp_il-76md (Default squadron) | proxy | support | 1 | R03:72, R03:86 (An-12) | No An-12 exists in the collection. Label 'Il-76MD standing in for An-12'; it is a larger jet airlifter. No supply system, so it is activity only. |
| asset:rus:olenya_tu142_1 | wp_tu-142m | exact (Tu-142MK/MZ missing) | patrol | 1 | R03:117, R03:134 (Tu-142 over the Barents; no base named). Detachment at Olenya is a scenario choice. | Authored detachment, labelled as such. Airborne at t0 on patrol; placed as an airborne unit, not also listed in the base CustomAirGroup. Can be refuelled by the Il-78. |
| asset:rus:olenya_il78_1 | wp_il-78 (Squadron1 '203rd GARP') | exact | support | 1 (optional) | Not in R01-R03; scenario choice | Probe-and-drogue tanker. Can refuel the Tu-22M2 proxy and the Tu-142M only. In the base CustomAirGroup only if authored. A separate airframe from asset:rus:belaya_il78_opt. |
| asset:rus:olenya_sam_opt | wp_sam_site_sa-21 | exact | fixed_defence | 0 by default (optional 1) | No report describes Olenya's defences. R03:162 is generic guidance. | Do not fabricate present-day defences (plan:24). If authored, label it as scenario point defence. |

**Allocations with nothing assigned:** underway, escort, transit and reserve. The proposed training sortie uses two of the four ready aircraft, which are at base at t0.

**Support services.**
- **Ship ammunition supply:** not applicable at this inland airbase. Regional naval rearm is ship-borne only (wp_vt_boris_chilikin, above).
- **Aircraft turnaround and ordnance:** wp_airbase_1 declares FlightDeck_AmmoCapacity 3,000,000 with category limits AirTorpedo 96, Ovod 192 and Harpoon 192. Whether bomber stores draw on these limits is untested. Unit-file ReadyUpTime / CoolDownTime: Tu-22M2 50-60 / 240 min; Tu-95MS 30 / 240 min; Tu-160 30 / 60 min.
- **Air-to-air refuelling:** wp_il-78 (FuelCapacity 100000, 5 nm) can refuel wp_tu-22m2 and wp_tu-142m. It cannot refuel wp_tu95ms, wp_tu-160 or wp_il-76md.
- **Not established:** fuel (tgt_fueltanks_medium is a target object only), repair, and restocking of the base's flight-deck pool.
- **If the optional SAM is placed:** tgt_ammo_depot_small (pool 200000, 1.5 nm, LandUnit targets) can reload it. wp_car_ural can truck its unpriced rounds (verify correction).

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| hn_evenes_air_station | Adversary patrol and QRA intercept context | authored | R03:117 (origin base of the Tu-95/Tu-142 not named); R03:70 |
| sea:barents_sea | Maritime-strike and patrol operating area | authored | R03:66, R03:72, R03:117 |
| sea:giuk_gap / sea:north_atlantic | Geographic proximity | source | R03:70 |
| rus_engels2_airbase | Bomber relocation inflow | authored | R03:72 (influx due to vulnerabilities deeper inside European Russia); R03:162 (redeployment to Olenya out of drone range; no origin named); Engels not named as origin |
| offmap:southbound_standoff_axis | Long-range strike sortie axis | source (context only) | R03:72. Out of maritime scope; not modelled. |
| backlog:russian_northern_fleet_bases | Regional naval context | authored | R03:66, R03:115, R03:166 |

**Routine activity (PROPOSED, not implemented).**
- The Tu-142M flies a Barents ASW patrol loop and recovers to Olenya.
- The Tu-95MS flies a long-range Barents / Norwegian Sea patrol that draws Evenes QRA, with an Empty or LandAttack loadout. Hold/release behaviour must be tested; the aircraft is not automatically hostile.
- A pair of the ready Tu-22M3 proxies flies a maritime-strike training sortie, with an optional Il-78 rendezvous.
- The Il-76MD (An-12 proxy) makes arrivals and departures to an off-map interior origin.
- Optional event: an Engels aircraft disperses to Olenya. Its allocation moves with it, so it is never counted twice.
- **Civilian (neutral):** Barents fishing (see regional context), and civ_a320 Squadron36 (Aeroflot, Nation=RU) on Murmansk routes.
- **Not modelled:** southward strikes (R03:72) and drone strikes on the base (R03:74). Any such event would be an optional authored disruption.

**Validation.** Research: sources are R03 only, which R01 repeats; counts and units need checking. Mapping: as in the table. Placement: pending. Runtime activation and saved-state behaviour: untested.

**Gaps.**
- No Tu-22M3, An-12 or Tu-142MK/MZ in the collection.
- No unit carries the 40th CAR identity.
- No AAR receiver on the Tu-95MS or Tu-160.
- wp_tu95ms is a Tu-142M-derived file declaring Role=MPA,ASW; bomber AI tasking is untested.
- No source for local air defence.
- Fuel, repair and restocking are not established.

### rus_engels2_airbase - Engels-2 Airbase

**Identity.**
- Country: Russia, Saratov Oblast, "14 kilometers east of Saratov" (R03:78).
- Operator: Russian Aerospace Forces (R03:78), per the fidelity fix. The Long-Range Aviation affiliation is editorial.
- Kind: air_base. Policy: populate_small.

**Role (SOURCE CLAIM).**
- "Russia's premier strategic bomber base and the heart of its European aviation deterrence" (R01:41 and R03:78, word for word).
- Table function: "Strategic Bomber Hub" (R03:87).
- Units: the 22nd Guards Heavy Bomber Aviation Division, made up of the 121st GHBAR (Tu-160M) and the 184th HBAR (Tu-95MS) (R03:78).
- Facilities: a 3,500-metre runway, and "extensive munitions storage designed to support sustained strategic bombardment" (R03:78; the register omitted the second half of that claim).
- "Primary launch point for standoff missile strikes into Ukraine"; drones "completely destroying Tu-95MS bombers"; hardened shelters built and fleets dispersed to secondary airfields (R03:78).
- R03:160 makes a joint statement about Engels-2 and Belaya: the strikes "demonstrate that static infrastructure is highly vulnerable to relatively cheap, asymmetric technologies".

**CHECKS.**
- Verify the unit and aircraft assignments.
- The Tu-95MS losses are undated, unsourced and contested. No loss count is asserted here.
- R01:41 and R03:80 describe relocation to Ukrainka and Belaya without naming Engels as the origin. Treat that only as context.
- Do not turn R03:160 into a deterministic vulnerability rule (seed:23).
- The base is inland on the Volga, 726 NM from the nearest proven placement, and terrain there is untested. It can be held as an off-map raid origin.
- **Collection.** wp_airbase_modern resolves 51 of its 61 AirGroup ids; the 10 that fail include wp_tu-22m3_90 and wp_tu-95ms_x101. A custom AirGroup is therefore required.
- **Collection.** wp_tu160air is a proxy, not an exact match (correction).
- **Collection.** The game runway is the Olenya-template mesh, not Engels' 3,500 m runway.
- **Collection.** wp_tu-160 has no Tu-160M distinction.
- **Collection.** wp_tu95ms: LandAttack/Default only; StrikePrecision (KH-55, nuclear-effect model) and CAS (KH-55SM) are excluded. Its file declares Role=MPA,ASW (Tu-142M-derived), so AI tasking as a bomber is untested (see the Olenya CHECK).

**Position.**
- Approx 51.48N 46.21E (approx, verify).
- In-game evidence: wp_airbase_modern Variant1 is named 'Engels airforce base'. There are no repo coordinates for it.
- From the candidate centre: x about 1,573, z about 569 (about 1,210 NM). About 1,070 NM from Olenya.

**Forces (all quantities are SCENARIO CHOICES).**

| Asset id | Unit id | Outcome | Allocation | Qty | Source basis | Notes |
|---|---|---|---|---|---|---|
| asset:rus:engels_base | wp_airbase_modern (Variant1) | exact (name only) | resident_at_base | 1 | R01:41, R03:78, R03:87 | CustomAirGroup: wp_tu-160 and wp_tu95ms only. Capacity 234. Declares no FlightDeck_AmmoCapacity. |
| asset:rus:engels_tu160m | wp_tu-160 | proxy | resident_at_base | 2 | R03:78 (121st GHBAR, Tu-160M), R03:87 | Label 'Tu-160 standing in for Tu-160M'. Loadouts StrikeLongRangeKH101 (KH-101) / StrikeLongRange (KH-555) only; never StrikeNuclear (KH-55, nuclear-effect model) or Default/Strike (KH-55SM). |
| asset:rus:engels_tu95ms_1 | wp_tu95ms (Default squadron) | exact | resident_at_base | 1 | R03:78 (184th HBAR), R03:87 | The '315 regiment' squadron label does not match the 184th; use Default. Loadout LandAttack (KH-101) only; Default (KH-555) is also conventional. Never StrikePrecision (KH-55, the nuclear-effect model also used by the excluded Tu-160 StrikeNuclear) or CAS (KH-55SM). Role=MPA,ASW file: bomber tasking untested (CHECK). |
| asset:rus:engels_tu95ms_2 | wp_tu95ms | exact | servicing_maintenance | 1 | Scenario choice reflecting the R03:78 strike damage | No loss figure is implied. Same loadout limits (LandAttack/Default only) and Role=MPA,ASW CHECK. |

**Allocations with nothing assigned:** patrol, escort, transit, reserve and fixed defence. Hardened shelters (R03:78) have no collection unit. No tanker is placed, because the Il-78 cannot refuel these types.

**Support services.**
- **Ship supply:** not applicable.
- **Aircraft turnaround:** wp_airbase_modern declares no FlightDeck_AmmoCapacity, so the engine default stock applies (undocumented, untested).
- **Munitions storage (R03:78):** kept abstract; no physical representation.
- **AAR:** none usable.
- **Not established:** fuel, repair and restocking.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| hn_kola_olenya_airbase | Dispersal / relocation | authored | R03:78 (dispersal, unnamed); R03:72 (influx due to vulnerabilities deeper inside European Russia); R03:162 (redeployment to Olenya out of drone range; no origin named); Engels not named as origin |
| rus_ukrainka_airbase | Relocation context, not Engels-specific | authored | R01:41, R03:80 |
| rus_belaya_airbase | Relocation context, not Engels-specific; joint strike statement | authored | R01:41, R03:80, R03:160 |
| backlog:engels_secondary_airfields | Dispersal destinations | source | R03:78 (unnamed) |
| offmap:raid_origin | Standoff raid origin | authored | R03:78; register check note |

**Routine activity (PROPOSED, not implemented).**
- Off-map standoff departures, as scenario context.
- One aircraft disperses to Olenya as an event, and its allocation moves with it.
- The servicing aircraft returns to ready after CoolDownTime.
- **Civilian (neutral):** civ_a320 Squadron24 (Ural Airlines), Squadron36 (Aeroflot) and Squadron47 (S7 / 'Siberia Airlines'), all Nation=RU, plus civ_il-76td Squadron1 'Volga Wings Freight' (Nation=Soviet).

**Validation.** Research: R03 only. Mapping: as in the table. Placement: pending and inland. Runtime activation and saved-state behaviour: untested.

**Gaps.**
- Tu-160M is not distinguished in the collection.
- No hardened aircraft shelter unit.
- No receiver for in-game AAR.
- wp_tu95ms is a Tu-142M-derived file declaring Role=MPA,ASW; bomber AI tasking is untested.
- No regiment identities on the long-range aviation units.
- The base's stock is the engine default.
- The dispersal airfields are unnamed.

### rus_ukrainka_airbase - Ukrainka Airbase

**Identity.**
- Country: Russia, Amur region, Far East (R03:80, R03:88).
- Operator: Russia. The operating service is not stated; Long-Range Aviation is inferred from the Tu-95MS type (fidelity fix).
- Kind: air_base. Policy: populate_small.

**Role (SOURCE CLAIM).**
- "A major hub for Tu-95MS operations facing the Pacific" (R03:80).
- Table: "Pacific Bomber Hub", assets Tu-95MS (R03:88).
- A relocation destination for assets moved away from the drone threat (R01:41, R03:80).
- A Tu-95MS "suffered a catastrophic multi-engine failure and crashed upon takeoff from Ukrainka, resulting in six fatalities" (R03:82; repeated within R03 at R03:162).
- R03:82 guidance: model airframe fatigue and engine failure probabilities.

**CHECKS.**
- The crash is undated and unsourced; verify its date and casualty figure. The R03:162 repetition is not corroboration.
- R03:80's "even these remote installations" were struck is not tied to Ukrainka; R03:160 names only Belaya.
- No aircraft count is given.
- The base is inland, about 465 NM from the coastal Kamenny Ruchey point and 590 NM from the nearest proven placement. Whether the active area reaches it is open.
- No collection evidence of a failure-probability model was found. Do not author a deterministic crash rule.
- **Collection.** No Ukrainka unit exists. Use the Default variant of wp_airbase_modern, not the Engels-named Variant1 (correction).
- **Collection.** wp_tu95ms: LandAttack/Default only; StrikePrecision (KH-55, nuclear-effect model) and CAS (KH-55SM) are excluded. Its file declares Role=MPA,ASW (Tu-142M-derived), so AI tasking as a bomber on the Pacific patrol is untested (see the Olenya CHECK).

**Position.**
- Approx 51.17N 128.45E (approx, verify).
- In-game evidence: no anchor nearby. Vanilla airports.ini has UHKG Kamenny Ruchey at 49.2373,140.1915.
- From the candidate centre: x about 6,507, z about 550 (about 4,090 NM). Within the extent that has loaded and been saved, and not near the date line.

**Forces (all quantities are SCENARIO CHOICES).**

| Asset id | Unit id | Outcome | Allocation | Qty | Source basis | Notes |
|---|---|---|---|---|---|---|
| asset:rus:ukrainka_base | wp_airbase_modern (Default; alternatives wp_tu160air, wp_airbase_4) | proxy | resident_at_base | 1 | R03:80, R03:88 | Visible label 'Ukrainka (stand-in)'. CustomAirGroup: wp_tu95ms. A future SEST named clone could follow the integration/raaf-bases pattern; no such id exists yet. wp_airbase_4 (capacity 48) has untested take-off length constraints. |
| asset:rus:ukrainka_tu95ms_pair | wp_tu95ms (Default squadron) | exact | resident_at_base | 2 | R03:80, R03:88 | Fly the proposed Pacific patrol. No receiver. Loadout LandAttack (KH-101) only; Default (KH-555) is also conventional. Never StrikePrecision (KH-55, the nuclear-effect model also used by the excluded Tu-160 StrikeNuclear) or CAS (KH-55SM). Role=MPA,ASW file: bomber tasking untested (CHECK). |
| asset:rus:ukrainka_tu95ms_svc | wp_tu95ms | exact | servicing_maintenance | 1 | Scenario choice reflecting the R03:82 attrition guidance | Represents strain through servicing, not random loss. Same loadout limits (LandAttack/Default only) and Role=MPA,ASW CHECK. |

**Allocations with nothing assigned:** patrol at t0, escort, transit, reserve and fixed defence (no source).

**Support services.**
- **Ship supply:** not applicable.
- **Aircraft turnaround:** wp_airbase_modern declares no FlightDeck_AmmoCapacity (engine default, untested). Tu-95MS CoolDownTime is 240 min.
- **AAR:** none usable.
- **Not established:** fuel, repair and restocking.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| sea:sea_of_okhotsk | Pacific long-range patrol area | authored | R03:80 ('facing the Pacific'), R03:66 |
| rus_belaya_airbase | Co-listed relocation destination | source | R01:41, R03:80 |
| rus_engels2_airbase | Relocation origin (unstated) | authored | R01:41 and R03:80 name no origin |
| backlog:russian_pacific_fleet_bases | Regional naval context | authored | R03:66 |

**Routine activity (PROPOSED, not implemented).**
- The Tu-95MS pair flies a long-range Pacific patrol toward the Sea of Okhotsk and returns. The route must fit unrefuelled range.
- Servicing rotation, with one airframe always in servicing.
- **Civilian (neutral):** civ_a320 Squadron47 'Siberia Airlines' (Nation=RU).

**Validation.** Research: R03 only, with weak detail. Mapping: base proxy, aircraft exact. Placement: pending and inland. Runtime activation and saved-state behaviour: untested.

**Gaps.**
- No named base unit.
- No receiver on the Tu-95MS for in-game AAR.
- wp_tu95ms is a Tu-142M-derived file declaring Role=MPA,ASW; bomber AI tasking is untested.
- No Pacific port or fleet-base units for the surrounding context.
- The inland terrain is unproven.

### rus_belaya_airbase - Belaya Airbase

**Identity.**
- Country: Russia, Irkutsk Oblast, Siberia, "roughly 4,500 kilometers from the Ukrainian border" (R03:80).
- Operator: Russia. The operating service is not stated (table function 'Strategic Aviation', R03:89); Long-Range Aviation is inferred.
- Kind: air_base. Policy: populate_small.

**Role (SOURCE CLAIM).**
- "Has historically hosted up to 42 Tu-22M3 bombers" (R03:80).
- Table assets: Tu-22M3, Tu-95MS (R03:89).
- A relocation destination (R01:41, R03:80).
- Target of successful Ukrainian drone strikes, in the joint statement with Engels-2 (R03:160).

**CHECKS.**
- Tu-95MS at Belaya appears only in the table (R03:89); the prose names only the Tu-22M3. It is not populated.
- 42 is a historical maximum, not a current count.
- Belaya was also reported hit in June 2025. Check its status at the scenario date.
- No deterministic vulnerability rule (seed:23).
- **Collection.** The squadron labels 'Tu-22M2 1225th / 1229th TBAP, based in Belaya' come from in-game language comments, not from R01-R03.
- The base is inland, 1,271 NM from the nearest proven placement and about 1,550 NM from the central Sea of Okhotsk. Its maritime reach is limited, so an off-map raid origin is likely.

**Position.**
- Approx 52.92N 103.58E (approx, verify).
- In-game evidence: none beyond the language comment on wp_tu-22m2 Squadron13/14.
- From the candidate centre: x about 5,015, z about 655 (about 3,260 NM).

**Forces (all quantities are SCENARIO CHOICES).**

| Asset id | Unit id | Outcome | Allocation | Qty | Source basis | Notes |
|---|---|---|---|---|---|---|
| asset:rus:belaya_base | wp_airbase_modern (Default; alternative wp_airbase_4) | proxy | resident_at_base | 1 | R03:80, R03:89 | Visible label 'Belaya (stand-in)'. CustomAirGroup: wp_tu-22m2, plus wp_il-78 only if asset:rus:belaya_il78_opt is authored. |
| asset:rus:belaya_tu22m3 | wp_tu-22m2 (Squadron13 '1225th TBAP') | proxy | resident_at_base | 2 | R03:80, R03:89; scaled from 'historically up to 42' | Label 'Tu-22M2 standing in for Tu-22M3'. Regiment label: CHECK. |
| asset:rus:belaya_tu22m3_svc | wp_tu-22m2 | proxy | servicing_maintenance | 1 | Scenario choice | None. |
| asset:rus:belaya_il78_opt | wp_il-78 (Squadron1 '203rd GARP') | exact | support | 0 by default (optional 1) | Not in R01-R03; scenario choice | Probe-and-drogue tanker for the Tu-22M2 proxies. A separate airframe from asset:rus:olenya_il78_1; never the same tanker at two bases. |

**Allocations with nothing assigned:** patrol, escort, transit, reserve and fixed defence. No Tu-95MS is placed, because the claim is table-only. The Il-78 (asset:rus:belaya_il78_opt) is optional (it is Tu-22M2-compatible) and not placed by default.

**Support services.**
- **Ship supply:** not applicable.
- **Aircraft turnaround:** engine-default stock on wp_airbase_modern. wp_airbase_4 would instead give FlightDeck_AmmoCapacity 1,000,000 with AirTorpedo 48, Ovod 96 and Harpoon 96. Both are untested.
- **AAR:** usable only if the optional Il-78 (asset:rus:belaya_il78_opt) is authored.
- **Not established:** fuel, repair and restocking.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| rus_ukrainka_airbase | Co-listed relocation destination | source | R01:41, R03:80 |
| rus_engels2_airbase | Joint strike-vulnerability statement (status context, not logistics) | source | R03:160 |
| sea:sea_of_okhotsk | Long-range maritime-strike reach | authored | R03:80, R03:89 |
| offmap:raid_origin | Raid origin | authored | Register check notes |

**Routine activity (PROPOSED, not implemented).**
- Tu-22M3-proxy training sorties.
- An optional long-range maritime-strike exercise toward the Sea of Japan / Sea of Okhotsk.
- **Civilian (neutral):** civ_a320 Squadron47 overflights.

**Validation.** Research: R03 only. Mapping: proxies. Placement: pending and remote. Runtime activation and saved-state behaviour: untested.

**Gaps.**
- No Tu-22M3 or Belaya base unit.
- No current count.
- Tu-95MS is held pending a check.
- Remote inland terrain is unproven.
