<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Japanese and Norwegian maritime patrol network

**Nodes (in order):** hn_evenes_air_station, jpn_kanoya_air_base, jpn_atsugi_naf, jpn_okinawa_naha. All four are `populate`, and all four are air stations. The sources describe no ships, piers or naval berths at any of them, so no ship is allocated in this region.

**Sources used:** R01:61; R03:111-134, R03:162, R03:166, R03:168. Fidelity fixes applied: fidelity[0] adds R03:121 (network focus) and R03:127/R03:132 (P-1 fit) at Atsugi. R03:125 (HPS-106, MAD) is added by this package, not by fidelity[0]. fidelity[1] adds R03:115 (role descriptor and upgrade purpose), R03:117 ("kill web", "international airspace") and R03:162 (NASAMS) at Evenes, plus R03:121 at Naha. fidelity[2] adds the Kanoya-Lingshui counter-screen mirror relationship (R03:168).

**Inventory corrections applied:**
- usn_p_8a: USN use is limited to Squadron1-14.
- UK P-8 = usn_p8 Squadron4 (missed asset).
- RAF RC-135 = boeing-rc135 Squadron6/7 (missed asset).
- Modded-tanker refuelling is downgraded to unverified.
- Kanoya and Atsugi placement distances are stated per class.
- SEST supply clones (jmsdf_aoe_mashuu) count as proxy: the data is correct but the mesh is a stand-in.
- Installations: the airbase_us clone template's default [AirGroup] has a malformed line ('S-70B-2_Seahawk=Squadron1=5') and a usmc_vh-3d Squadron1 that the winning squadrons file does not define. Any clone or placement replaces that group via CustomAirGroup.

**Asset-id prefix:** `asset:mpn:` (maritime patrol network).

**How to read each package**
- **SOURCE** = what R01-R03 say (report:line).
- **CHECK** = a doubt or a verification still to do. Sources are never silently corrected.
- **SCENARIO** = our proposal: quantity, allocation and activity.

**Region-level picture**
- **Norway:**
  - The RNoAF P-8A is an exact match (usn_p8 Squadron5).
  - The F-35A is missing_fit: the only F-35A unit has RAAF squadrons only.
  - NASAMS III has only a labelled SL-AMRAAM proxy. There is no counter-UAS unit.
  - There is no Norway-flag airbase: proxy for now, named SEST clone later.
- **Japan:**
  - There is no Kawasaki P-1 in the collection. The only correct-operator stand-in is a Japan-flagged usn_p-3c. As a proxy it needs a visible 'P-1 stand-in' label.
  - No in-game label route for an aircraft is proven yet. Every P-1 stand-in is therefore **pending proxy** and is not placed until a label route exists. The preferred route is a SEST patch adding labelled Japan squadrons to usn_p-3c; the alternative is a mission name override proven in the editor (separate airborne entries only; it cannot label aircraft inside a CustomAirGroup).
  - The JMSDF P-3C itself is exact.
  - No named JMSDF base exists. All three use airfield_small_1 Variant5 'Airbase - small (Japan)' as a labelled proxy.
  - The platform-to-station assignment was checked, not copied: Kanoya and Atsugi = P-1 per R03:127/R03:168 (stand-in); Naha = P-3C (R03:127 omits Naha, and the register check notes it is still reported as P-3C).
  - In game all three look the same (P-3C mesh). They differ only in label and squadron.
- **SCENARIO totals:**
  - Evenes: 5 named P-8A (the sourced count: 4 in the Evenes CustomAirGroup, 1 airborne), 3 visiting aircraft authored as separate aircraft entries (1 USN P-8A counted against the Jacksonville allocation, 1 RAF P-8A, 1 RC-135), 2 F-35A pending a fit, 1 NASAMS proxy fire unit (1 radar, 2 launchers).
  - Japan: 7 P-1 stand-ins (Kanoya 3, Atsugi 4), all pending the label route; 4 P-3C at Naha; 1 conditional P-3C at Kanoya, held out (0) until the transition check and the label route are both in place. R03:127's 34-36 is a fleet-wide count, not per base.
- **Built-in air groups:**
  - Every installation used here ships its own air group: nato_small_airbase 54 Cold War US aircraft, airfield_small_1 Variant5 44, usa_airbase 57 (Default) or 96 (Variant1), and the airbase_us template's USAF-heavy group.
  - Each placement sets CustomAirGroup=True holding only that base's at-base identities, and nothing else.
  - Each patrol airframe is a separate airborne aircraft entry with an explicit LoadoutVariant. It is never also counted in the group.
  - An AirGroup line holds only squadron and count. A ready at-base airframe gets its loadout from `FlightDeck_ReadyUpTaskN=<type>,<squadron>,<loadout>,<count>,0` on the base entry, with the task total in `FlightDeck_ReadyUpTasks=<n>` (vanilla precedent: Showdown off Guam Blue 1985, `FlightDeck_ReadyUpTasks=3` and `FlightDeck_ReadyUpTask2=usn_p-3c,Squadron14,Recon,1,0`). Servicing and reserve airframes get no ready-up task. Runtime behaviour is still to test.
- **Scope:**
  - From a 42N 20E datum: Evenes x=-199, z=1,589; Kanoya, Atsugi and Naha x=6,459-7,167, z=-393 to -948. All are inside the proven extent (|x| 11,361 saved).
  - No date-line crossing.
  - Evenes-Naha is about 4,381 NM. That is beyond the 3,450 NM played-and-saved separation and inside the 4,913 NM file span. It matters only if both theatres share one mission.
  - The stock sea network (sea_points.ini) has no Pacific coverage, so Japanese routes need sea_routes.py or the land mask.
- **Rules carried:**
  - No perfect-detection rule is derived from "kill web" (R03:117), "impenetrable anti-submarine nets" (R03:111) or "dense curtain" (R03:168). Those phrases are rhetoric.
  - R03:166 is different. It is explicit simulation guidance to "model shared situational awareness rather than individual unit vision cones".
    - **SCENARIO choice, which departs from R03:166:** no shared vision or detection is scripted beyond the engine's own datalink and contact sharing. The basis is that the register invents no engine keys (plan:63).
    - **CHECK:** the engine's real datalink and contact sharing between allied MPAs is untested.
  - Russian and Chinese aircraft and submarines named as opposition belong to their own region packages and are never spawned here.
  - Every usn_p8, usn_p_8a, usn_p-3c, boeing-rc135, raaf_f-35a and civ_as-350 entry needs an explicit LoadoutVariant. None of them lists 'Default' in AvailableLoadouts (civ_as-350 lists only Transport). That is the KJ-500 map-panel crash pattern (docs/design-notes.md:495-527).
  - tools/preflight.py checks only [TaskforceNAircraftM] and [TaskforceNHelicopterM] entries, so it would not catch a neutral civ_as-350. Set that loadout by hand.

---

### hn_evenes_air_station - Evenes Air Station

**Identity.** Norway, Royal Norwegian Air Force, 133 Air Wing (R03:115). Host: Norway, Nordland county above the Arctic Circle (R03:115). Node kind: air_base. Policy: populate.

**SOURCE claims**
- R01:61: Norway operates Evenes "to monitor the GIUK Gap", hosting P-8A Poseidons and F-35A interceptors.
- R03:115:
  - "a cornerstone of NATO's maritime domain awareness in the High North";
  - an 8 billion NOK upgrade "to support next-generation aircraft";
  - 333 Squadron with five P-8A named Vingtor, Viking, Ulabrand, Hugin and Munin, delivered 2021-2022;
  - tasked with hunting Russian submarines transiting from Kola bastions through the GIUK Gap.
- R03:117:
  - QRA base for Norwegian F-35A, taking over from F-16s at Bodø;
  - scrambles "often dozens of times a year" against Tu-142 and Tu-95 over the Barents Sea, "in international airspace";
  - US "agreed area": US and UK P-8As, "as well as RC-135 Rivet Joint intelligence aircraft" (operator not stated), stage from Evenes;
  - "unified, multinational ASW kill web";
  - a British P-8A staged for the first Poseidon North Pole flyover (undated);
  - a dedicated air-defence battalion with NASAMS III and counter-UAS.
- R03:162: "the NASAMS III stationed at Evenes", given as a point-defence example. This repeats R03:117 and is not corroboration.
- R03:166: Kola submarines must first evade the Evenes P-8As; target data is handed off to UK and US aircraft.
- R03:166 (simulation_guidance), verbatim: "target data is handed off across allied platforms via data links, requiring the simulation to model shared situational awareness rather than individual unit vision cones." The SCENARIO departs from this guidance; see Rules carried and CHECKS.
- R03:131 (type table, platform-level): P-8A operated by US, UK and Norway; APY-10, Harpoon, Mk 54.

**Role.** Maritime patrol and ASW (333 Sqn), fighter QRA, staging for allied MPA and ISR, local air defence.

**Position.**
- Public location: approx 68.5N 16.7E (Evenes, north shore of Ofotfjorden). **Approx, verify.**
- In-game evidence:
  - stock sea point [Ofotfjorden] 68.441,16.657 (campaigns/sea_points.ini), about 3 NM away;
  - stock [Port Narvik]/[Narvik] 68.438,17.428, about 17 NM away;
  - nearest proven land placement 26 NM (nato_radar in 3491248180 'Lighting Strike'); nearest proven sea placement 36 NM.
- The campaign snapper has no proof here, so placement needs the global-land-mask tools or a new Norway coast extract. Placement is pending validation.

**Installation**
- asset:mpn:evenes_base: `nato_small_airbase` (vanilla, capacity 60) with Nation=norway set per placement and the label 'Evenes Air Station (stand-in)'. **proxy**. usa_airbase is a poorer fit because its name reads 'Naval Air Station'.
  - Its built-in [AirGroup] holds 54 Cold War US aircraft: usaf_f-15a Squadron1 x8, usaf_f-4e Squadron1/Squadron2 x24, usaf_e-3a x2, usn_ra-5c x6, usn_ea-6b x4, usn_p-3c Squadron1 x8 and usn_ch-46 x2.
  - The placement must set CustomAirGroup=True holding only the at-base identities: `usn_p8=Squadron5,4` (Viking, Ulabrand, Hugin, Munin). Nothing else goes in the group.
  - Vingtor (patrol) is placed only as a separate airborne aircraft entry: usn_p8 Squadron5, LoadoutVariant=ASW. It is never also in the group.
  - The three visiting aircraft stay out of the group (see Forces and CHECKS).
- A named Norway clone of `airbase_us` (3592460366), following integration/raaf-bases with an AirGroup of usn_p8 Squadron5, is **missing_fit**: the template exists but the clone is not built.
  - The same rule applies: the clone's AirGroup is `usn_p8=Squadron5,4` and nothing else.
  - None of the template's default group is kept. That group is USAF-heavy and has two broken entries: the malformed 'S-70B-2_Seahawk=Squadron1=5' and a usmc_vh-3d Squadron1 that the winning squadrons file does not define (installations verify correction).

**Forces.** Allocation, quantity and squadron picks are SCENARIO unless marked SOURCE.

| Asset | Allocation | Role | Unit (squadron, loadout) | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:mpn:p8a_vingtor | patrol | ASW patrol | usn_p8 Squadron5 'P-8A No.333 Squadron RNoAF' (Nation=Norway, RNoAF livery, callsign Odin), LoadoutVariant=ASW; separate airborne aircraft entry, not in the CustomAirGroup | exact | 1 | SOURCE R03:115 named airframe |
| asset:mpn:p8a_viking | resident_at_base | ready ASW alert | usn_p8 Sq5 in the CustomAirGroup; ready-up `usn_p8,Squadron5,ASW,1,0` | exact | 1 | R03:115 |
| asset:mpn:p8a_ulabrand | resident_at_base | anti-surface ready | usn_p8 Sq5 in the CustomAirGroup; ready-up `usn_p8,Squadron5,AntiShip,1,0` | exact | 1 | R03:115 |
| asset:mpn:p8a_hugin | servicing_maintenance | in maintenance at start | usn_p8 Sq5 in the CustomAirGroup | exact | 1 | R03:115 |
| asset:mpn:p8a_munin | reserve | finite reserve | usn_p8 Sq5 in the CustomAirGroup | exact | 1 | R03:115 |
| asset:mpn:evenes_f35a_qra_1, _2 | resident_at_base (QRA; not placed yet) | intercept and escort | raaf_f-35a: RAAF squadrons only, wrong flag; joins the CustomAirGroup (count 2) once a Norway squadron exists | missing_fit | 2 | R01:61, R03:117; qty SCENARIO |
| asset:mpn:evenes_usn_p8a_det | underway_deployed (staging) | visiting US MPA | usn_p_8a, USN Squadron1-14 only (Nation=US); squadron set by the Jacksonville package; separate aircraft entry, LoadoutVariant=ASW; not in the CustomAirGroup | exact | 1 | R03:117 staging; origin authored |
| asset:mpn:evenes_raf_p8a_det | underway_deployed (staging) | visiting UK MPA | usn_p8 Squadron4 'Poseidon MRA1 No.54 Squadron RAF' (Nation=UK); alt usn_p_8a Sq15-18; separate aircraft entry, LoadoutVariant=ASW; not in the CustomAirGroup | exact | 1 | R03:117 |
| asset:mpn:evenes_rc135_det | underway_deployed (staging) | SIGINT/ISR | boeing-rc135 Squadron2 (USAF ACC/55th Wing, generic livery, Nation=US); separate aircraft entry, LoadoutVariant=SIGINT; not in the CustomAirGroup | exact | 1 | R03:117 staging only (operator not stated; US pick SCENARIO) |
| asset:mpn:evenes_nasams_radar_1 | fixed_defence | SAM radar | usa_SLAMRAAM_radar (AN/MPQ-64), Nation=norway, label 'NASAMS III (SL-AMRAAM stand-in)' | proxy | 1 | R03:117 |
| asset:mpn:evenes_nasams_launcher_1, _2 | fixed_defence | SAM launcher | usa_SLAMRAAM_launcher (usn_aim_120c_ground, usn_aim_9x_ground), Nation=norway, same label | proxy | 2 | R03:117 |
| asset:mpn:evenes_cuas | abstract | counter-UAS | none found | none | 0 | R03:117 |

The five P-8A identities appear only in this package. In game, the airframes share one squadron livery, and naming individual airframes in an AirGroup is not established.

**Support services**
- **Ship ammunition:** not applicable. The sources give Evenes no berth role, and there is no Norwegian replenishment hull (Maud: none).
- **Aircraft turnaround and ordnance:**
  - nato_small_airbase has FlightDeck_AmmoCapacity 1,500,000 and accountable categories AirTorpedo 60, Ovod 120 and Harpoon 120.
  - usn_p8 loads: ASW = 5 usn_haawc_p8 plus SSQ-53F/62E/77C/101 sonobuoys; AntiShip = 4 AGM-84N.
  - Whether those stores rearm from the base stock, and whether repeat sorties work, is **not established** (test).
  - An airbase_us clone defines no FlightDeck_AmmoCapacity, so its turnaround stock is not established either.
- **Air-to-air refuelling:** not established. usn_p8, boeing-rc135 and raaf_f-35a declare no ReceiverSystems. otan_a330_mrtt Squadron5 (Norway, ProbeAndDrogue) exists but is not sourced at Evenes and has no compatible receiver here, so it is not allocated.
- **Supplier restocking, fuel, repair:** not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| Barents Sea | QRA intercept area | source | R03:117 |
| Kola Peninsula submarine bastions / departure area | ASW threat axis | source | R03:115, R03:166 |
| GIUK Gap | stated monitoring role and transit route (CHECK geography) | source | R01:61, R03:115 |
| hn_kola_olenya_airbase | possible source of intercept targets (Tu-95MS, R03:72); R03:117 names no base | authored | R03:117 + R03:72 |
| usa_jacksonville_nas_jacksonville | home allocation of the visiting USN P-8A | authored | R03:117 (staging), R03:23 (ASW hub) |
| allied UK/US MPA (data handoff) | cooperative ASW. R03:166 asks for shared situational awareness; the SCENARIO adds none beyond the engine's own datalink (CHECK). No perfect-detection rule. | source | R03:166 |
| North Pole / Arctic | context only | source | R03:117 |

**Routine activity** (SCENARIO, proposed, not implemented)
1. One 333 Sqn P-8A flies an ASW line in the Norwegian Sea north of Andøya toward the Barents approaches, anchored on stock sea points North West Andoya (69.78,14.96), Lofoten Basin 5 (70.83,13.70) and Nordvest Banken (71.01,18.92). The ready airframe relieves it. The rotation draws only on the five named identities.
2. The visiting USN and RAF P-8As extend the line (handoff, R03:166).
   - The RC-135 flies a SIGINT track off the Barents.
   - R03:117 supports only RC-135 staging from Evenes. The track, its location and the US operator are SCENARIO, and the geometry needs validation.
3. Once a Norway F-35A squadron exists, an F-35A pair scrambles against Tu-142/Tu-95 tracks. Those aircraft come from Russia-region allocations.
4. Civilian pool asset:mpn:evenes_civ_pool:
   - 4 Norwegian fishing vessels (civ_fv_sidetrawler, civ_fv_fishingboat_b Default/Variant2, civ_fv_sterntrawler_a Default; all Nation=Norway) in the stock 'Loefoten Fishing' area;
   - 1 Norway-flag car carrier (civ_ms_car_carrier_a Variant24 'MV Dyvi Skagerak') to Port Narvik via Ofotfjorden;
   - optionally civ_as-350 Squadron12 'AS.350B Offshore' (Nation=Norway), but only together with an authored rig. It needs LoadoutVariant=Transport: that is its only loadout, and it has no 'Default'.
   - No Norway-flag airliner exists. Avoid civ_ms_roro_a Variant1-5 and civ_ms_c8 Variant18-20 as neutral traffic, because they carry SEST supply blocks.

**CHECKS**
- Geography: Evenes is far from the GIUK Gap, so the GIUK framing in R01:61 and R03:115 needs checking. The scenario patrol is in the Norwegian Sea and Barents approaches.
- The F-35A presence is commonly described as a forward QRA detachment. The quantity of 2 is SCENARIO.
- Verify the NASAMS III battalion and the counter-UAS claim. The proxy fire unit is a small representative layer, not a reproduction of present-day defences (plan:24).
- The basis for UK staging under a US agreement is not stated. The North Pole flight is undated.
- R03:117 does not say whose RC-135 stages here; choosing the US one is SCENARIO. The tail-specific squadrons, boeing-rc135 Sq3-5 (USAF tails) and Sq6-7 (ZZ664/ZZ665), are named airframes that must be allocated once world-wide.
- The visiting USN P-8A counts against the Jacksonville allocation.
- usn_p-3c Squadron30 'P-3B 333 Squadron RNoAF' is historical. Do not use it.
- Mixed-nation AirGroup behaviour at a Norway-flagged base is untested: which nation and side a UK or US squadron spawns as.
  - SEST RAAF Bases (for example airbase_raaf_tindal, Nation=Australia, with usaf_f-15ex_SEII and usaf_b-2_spirit squadrons) and DARWIN US SUPPLY already put US squadrons in Australia-flagged air groups. The raaf-bases first-flight checks are still open, so the behaviour is not established.
  - Until it is tested, author the three visitors as separate aircraft entries, each with its own Nation (US, UK, US) and explicit LoadoutVariant (ASW, ASW, SIGINT). Keep them out of the Evenes CustomAirGroup.
- The engine's real datalink and contact sharing between allied MPAs (333 Sqn and the USN and RAF P-8As) is untested. R03:166 asks for shared situational awareness, and the SCENARIO adds nothing beyond what the engine does (region rule).
- civ_as-350 needs an explicit LoadoutVariant=Transport. preflight does not scan neutral aircraft entries. Vanilla missions do set LoadoutVariant on neutral aircraft entries (for example 'Mind the Gap - Original 1988').

**Gaps**
- A Norway F-35A squadron (SEST pack).
- A named Evenes base clone.
- NASAMS and counter-UAS units.
- A Norwegian helicopter or SAR unit, a Norway airliner, and a Maud replenishment ship.
- A Norway coast extract.
- Backlog nodes: Bodø (R03:117), Russian Tu-142 bases, Russian Northern Fleet bases, and the UK P-8 home station.

**Validation**
- Research: claims faithful.
- Unit mapping: re-resolved 2026-10-07.
  - usn_p8 resolves to SEST_Integration, usn_p_8a to 3413868677 and boeing-rc135 to 3808882954.
  - raaf_f-35a resolves to SEST_Integration and nato_small_airbase to vanilla.
  - usa_SLAMRAAM_* resolves to 3413868677.
  - civ_as-350 resolves to 3806197116, and the airbase_us clone template to 3592460366.
- Placement, runtime activation, turnaround and save/load are untested.

---

### jpn_kanoya_air_base - Kanoya Air Base

**Identity.** Japan Maritime Self-Defense Force, Fleet Air Wing 1 (R03:123). Host: Japan. Node kind: naval_air_station. Policy: populate.

**SOURCE claims**
- R03:121 (network): the JMSDF network is focused on ASW and maritime surveillance against Russian Pacific Fleet movements and the Chinese submarine force.
- R03:123: FAW1 operates out of Kanoya; the bases are transitioning from the P-3C to the P-1.
- R03:127: P-1s flying from Atsugi and Kanoya drop dense sonobuoy networks. There are 34-36 P-1 in service fleet-wide.
- P-1 fit, platform-level only:
  - R03:125: HPS-106 AESA radar and MAD;
  - R03:127: Mk.46 and Type 97 torpedoes, Harpoon, ASM-1C, 30+/70+ sonobuoys, 9,000 kg bay;
  - R03:132: type-table row.
- R03:168: P-1s from Kanoya and Atsugi lay sonobuoy barriers across the First Island Chain against Chinese submarines from Yulin and Longpo. Lingshui J-15s and Y-8Qs act as a counter-screen.

**Role.** Maritime patrol and ASW.

**Position.**
- Public location: approx 31.4N 130.85E (Osumi Peninsula, inland). **Approx, verify.**
- In-game evidence:
  - nearest proven air point 31 NM (usaf_e-3a in 'GULF ATTACK .7.7');
  - nearest proven land point about 337 NM;
  - stock asia_ports [Kagoshima] 31.585,130.562, about 19 NM away.
- Placement is pending validation.

**Installation**
- asset:mpn:kanoya_base: `airfield_small_1` Variant5 'Airbase - small (Japan)', labelled 'Kanoya Air Base (stand-in)'. **proxy**.
  - Its built-in CustomAirGroup must be replaced. That group holds 44 aircraft: F-1, T-2, F-4EJ, PS-1, US-1, HSS-2 and usn_p-3c Squadron23 x4. Squadron23 is Atsugi's 3rd FAS.
  - The placement sets CustomAirGroup=True holding only the at-base identities kanoya_p1_2 and kanoya_p1_3: `usn_p-3c=<P-1 stand-in squadron>,2`.
  - Append `|Squadron21,1` (1 genuine P-3C) only if the conditional kanoya_p3c_1 is confirmed. Nothing else goes in the group.
  - kanoya_p1_1 (patrol) is a separate airborne aircraft entry with LoadoutVariant=ASW. It is never also in the group.
  - `<P-1 stand-in squadron>` is the labelled Japan squadron the SEST patch would add. Its number is assigned when the patch is built; none is invented here. A mission name override, even if proven, can label only the separate airborne entry (kanoya_p1_1). An AirGroup line holds only squadron and count, so the at-base stand-ins (kanoya_p1_2, _3) need the SEST squadron patch and are not placed without it.
- A named JMSDF base clone of airbase_us is **missing_fit**.

**Forces** (SCENARIO allocation)

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:mpn:kanoya_p1_1 | patrol | ASW patrol | usn_p-3c, labelled Japan squadron (proposed name 'P-1 stand-in (P-3C) 1st FAS', reusing the livery of Squadron21 "P-3C 1st FAS 'Jupiter'", Nation=Japan); separate airborne aircraft entry, LoadoutVariant=ASW | proxy (pending label route; not placed until it exists) | 1 | SOURCE R03:127, R03:168 (P-1 at Kanoya) |
| asset:mpn:kanoya_p1_2 | resident_at_base | ready ASW | same squadron, in the CustomAirGroup; ready-up `usn_p-3c,<P-1 stand-in squadron>,ASW,1,0` | proxy (pending label) | 1 | same |
| asset:mpn:kanoya_p1_3 | servicing_maintenance | maintenance | same squadron, in the CustomAirGroup | proxy (pending label) | 1 | same |
| asset:mpn:kanoya_p3c_1 | reserve (conditional; held out) | legacy MPA | usn_p-3c Squadron21 "P-3C 1st FAS 'Jupiter'" (Nation=Japan), in the CustomAirGroup if placed | exact | 0 now (1 only if both conditions below are met) | R03:123 (transition, general) |

Pairing Squadron21 (1st FAS) with Kanoya is SCENARIO: R03 names the wing, not the squadron. The P-3C is placed only if two conditions are met:
- the per-base check shows P-3Cs still at Kanoya;
- the P-1 stand-ins have already moved to their labelled squadron.

Until then it would carry the same Squadron21 livery and name as the stand-ins, so the two could not be told apart in game. It stays out.

**Support services**
- **Ship ammunition:** not applicable (inland air station).
  - The JMSDF supplier jmsdf_aoe_mashuu has a TruckSupplySystem: pool 250,000, ceiling 5,000; Harpoon 24, AirTorpedo 40, ALWT 16, SEST_LandAttack 12, SEST_LongRangeSAM 24.
  - It is proxy (correct data on a Sacramento stand-in mesh) and belongs to the Yokosuka or at-sea allocation, not here.
- **Aircraft turnaround:**
  - airfield_small_1 has FlightDeck_AmmoCapacity 1,000,000; AirTorpedo 48, Ovod 96, Harpoon 96.
  - usn_p-3c loads: ASW = DateBased_Torpedo_Export x8, usn_mk54_dc and SSQ-41/53/62; AntiShip = DateBased_Harpoon x4.
  - Rearm and repeat sorties are **not established**.
- **Air refuelling:** not established (usn_p-3c has no ReceiverSystems).
- **Restocking, fuel, repair:** not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| First Island Chain | sonobuoy-barrier area | source | R03:168 |
| chn_hainan_yulin_naval_base | target submarine force | source | R03:168 |
| chn_hainan_longpo_naval_base | target submarine force | source | R03:168 |
| chn_hainan_lingshui_airbase | opposing counter-screen (fidelity[2] mirror) | source | R03:168 |
| jpn_atsugi_naf | JMSDF Fleet Air Force network | source | R03:123, R03:127 |
| jpn_okinawa_naha | JMSDF Fleet Air Force network | source | R03:123 |
| East China Sea | patrol area | authored | R03:105 (ECS as the Eastern Theater Command area, not a Kanoya link) |
| Russian Pacific Fleet (no base named) | surveillance target | source | R03:121 (backlog) |

**Routine activity** (SCENARIO, proposed)
1. One P-1 stand-in flies a patrol line south of Kyushu across the northern Ryukyu approaches and the East China Sea edge (route via sea_routes.py or the land mask). The ready airframe relieves it.
2. A periodic sonobuoy-barrier sortie (R03:127/R03:168 role). It is not a perfect-detection net.
3. Civilian pool asset:mpn:kanoya_civ_pool:
   - 3 Japanese fishing vessels (civ_fv_fishingboat_c, civ_fv_fishingboat_d, civ_fv_sterntrawler_d);
   - 1 Japan-flag bulk carrier (civ_ms_bulk, Japan variants);
   - an optional airliner track (civ_a330 Squadron43/44 'Japan Airlines').

**CHECKS**
- The per-base transition stage and which squadron flies at Kanoya. The fleet count is undated.
- The P-1 stand-in is the same model as Naha's P-3C.
- A visible label for an aircraft is not established. The label route is a precondition for placing any P-1 stand-in at Kanoya or Atsugi.
  - Preferred route: a SEST patch adding labelled Japan squadrons to usn_p-3c (squadron sections reusing the 1fas/3fas liveries, plus names in aircraft_names.ini). This is the same approach as the proposed Norway raaf_f-35a squadron.
  - Alternative: a mission name override proven in the editor (separate airborne entries only; it cannot label aircraft inside a CustomAirGroup). No mission in the repo yet sets a name on an aircraft entry.
  - Until a route exists, the P-1s are recorded as pending proxy and are not placed.
- Explicit LoadoutVariant on every entry.
- Not checked: whether DateBased_Torpedo_Export resolves to a Mk 46-class weapon at the world date. The Type 97 torpedo and ASM-1C are not represented.
- The regional total of 7 P-1 stand-ins is SCENARIO, against the fleet-wide 34-36.
- Squadron service dates: see the Naha CHECKS (usn_p-3c_squadrons.ini [Default] ServiceDate=1977|1995, not overridden by the Japan Squadron21-29). Every P-1 stand-in here, and the conditional P-3C, depends on that editor check.

**Gaps**
- No P-1 unit.
- No named base.
- The HPS-106 and MAD fit is missing.
- No proven land placement within 300 NM.

**Validation**
- Research: claims faithful.
- Unit mapping: usn_p-3c and airfield_small_1 re-resolved to vanilla.
- Placement and runtime are untested.

---

### jpn_atsugi_naf - Naval Air Facility Atsugi

**Identity.** JMSDF Fleet Air Wing 4 (R03:123); 3rd Squadron at Atsugi (R03:127). R03 does not say the 3rd Squadron belongs to FAW4 (CHECK). Host: Japan, Kanagawa. NAF Atsugi is a US Navy-designated facility shared with the JMSDF (register CHECK on host and access labelling). Node kind: naval_air_station. Policy: populate.

**SOURCE claims**
- R01:61: the JMSDF operates from "nodes like Naha and Atsugi", using the P-1 to create an anti-submarine web over the First Island Chain.
- R03:121: network focus (fidelity[0]).
- R03:123: FAW4 operates from Atsugi; P-3C to P-1 transition.
- R03:127: P-1s flying from Atsugi and Kanoya. In December 2018 a South Korean destroyer "allegedly" locked fire-control radar onto a P-1 from Atsugi's 3rd Squadron.
- R03:127, R03:132: P-1 fit (fidelity[0]). R03:125: HPS-106 radar and MAD (added by this package, not by fidelity[0]).
- R03:168: sonobuoy barriers.

R01 and R03 repeat each other here; that is not corroboration.

**Position.**
- Public location: approx 35.45N 139.45E (inland). **Approx, verify.**
- In-game evidence:
  - nearest proven land point 30 NM (thaad_tel, 'GULF ATTACK .7.7');
  - nearest proven air point about 142 NM;
  - stock asia_ports [Yokohama] 35.444,139.638, about 9 NM away;
  - Yokosuka is about 14 NM away.
- Placement is pending validation.

**Installation**
- asset:mpn:atsugi_base: `airfield_small_1` Variant5 (Japan), labelled 'NAF Atsugi (JMSDF) (stand-in)'. **proxy**.
  - The built-in 44-aircraft group is replaced. CustomAirGroup=True holds only the at-base identities atsugi_p1_2, _3 and _4: `usn_p-3c=<3rd FAS stand-in squadron>,3`. Nothing else goes in the group.
  - atsugi_p1_1 (patrol) is a separate airborne aircraft entry with LoadoutVariant=ASW. It is never also in the group.
  - `<3rd FAS stand-in squadron>` is the labelled squadron from the SEST patch (see Kanoya CHECKS). This is the only route for the at-base stand-ins. A proven mission name override could label only the airborne atsugi_p1_1 (Squadron23).
- Alternative: usa_airbase (3413868677), 'Naval Air Station', capacity 72, FlightDeck_AmmoCapacity 2,000,000, with Nation=Japan set per placement.
  - Its unit [AirGroup] (66 aircraft) and variant groups spawn large US forces. Default (57) includes usaf_f_15c_2040c x28, usaf_b-52o x14 and usn_p_8a Squadron1 x4. Variant1 (96) includes usn_f-14e x24, usn_a-6g x14, usn_p-3d Squadron1 x8 and usn_p_8a Squadron4 x4.
  - It is usable only with the same CustomAirGroup=True holding the 3 allocated at-base airframes and nothing else.
- A named JMSDF base clone is **missing_fit**.

**Forces** (SCENARIO allocation)

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:mpn:atsugi_p1_1 | patrol | ASW patrol | usn_p-3c, labelled Japan squadron (proposed name 'P-1 stand-in (P-3C) 3rd FAS', reusing the livery of Squadron23 "P-3C 3rd FAS 'Neptune'", Nation=Japan); separate airborne aircraft entry, LoadoutVariant=ASW | proxy (pending label route; not placed until it exists) | 1 | SOURCE R03:127 (3rd Squadron P-1) |
| asset:mpn:atsugi_p1_2 | resident_at_base | ready ASW | same squadron, in the CustomAirGroup; ready-up `usn_p-3c,<3rd FAS stand-in squadron>,ASW,1,0` | proxy (pending label) | 1 | same |
| asset:mpn:atsugi_p1_3 | resident_at_base | anti-surface ready | same squadron, in the CustomAirGroup; ready-up `usn_p-3c,<3rd FAS stand-in squadron>,AntiShip,1,0` | proxy (pending label) | 1 | same |
| asset:mpn:atsugi_p1_4 | servicing_maintenance | maintenance | same squadron, in the CustomAirGroup | proxy (pending label) | 1 | same |

US Navy tenant units are not described in R01-R03, so none are allocated.

**Support services.** Same as Kanoya:
- Ship ammunition: not applicable.
- Turnaround: airfield_small_1 stock of 1,000,000 (AirTorpedo 48, Harpoon 96), or 2,000,000 with usa_airbase. Not established.
- Refuelling, restocking, fuel, repair: not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| First Island Chain | ASW web and sonobuoy barriers | source | R01:61, R03:168 |
| jpn_kanoya_air_base | network | source | R03:123, R03:127 |
| jpn_okinawa_naha | network | source | R01:61, R03:123 |
| chn_hainan_lingshui_airbase | opposing counter-screen | source | R03:168 |
| wpac_yokosuka_naval_base | nearby fleet base; possible ASW pairing with JMSDF escorts and the Mashuu AOE in that package | authored | none |
| hoa_djibouti_jp_base | if the Djibouti package authors a JMSDF MPA detachment, take it from this allocation; never duplicate it | authored | R01:51 names no aircraft |
| South Korea | incident context only; no hostility rule | source | R03:127 |

**Routine activity** (SCENARIO, proposed)
1. A patrol off the Pacific coast of Honshu (Sagami Bay and Izu Islands approaches), authored geometry.
2. A ready alert airframe on the ground.
3. Civilian pool asset:mpn:atsugi_civ_pool. Merge it with the Yokosuka region's Tokyo Bay pool so no traffic is placed twice:
   - 2 Japan-flag merchants: civ_ms_car_carrier_a Japan Variant13-21 or Variant40-42, and civ_ms_bulk Japan. Variant22-23 are Panama and Variant24 is Norway's 'MV Dyvi Skagerak', which stays unique to asset:mpn:evenes_civ_pool;
   - 2 fishing vessels (civ_fv_fishingboat_c, civ_fv_fishingboat_d);
   - civ_a330 Squadron43/44 (JAL).

**CHECKS**
- The per-station P-1 assignment.
- Host and access labelling at a US-designated facility.
- The incident is "alleged".
- The stand-in label, which is a precondition for placing the P-1 stand-ins (see Kanoya CHECKS), and explicit loadouts.
- Whether the 3rd Squadron belongs to FAW4. R03:127 says only "Atsugi's 3rd Squadron".
- Squadron service dates: see the Naha CHECKS. The P-1 stand-ins here depend on the same usn_p-3c ServiceDate check.
- airfield_small_1 Variant5's default group already uses Squadron23 x4. Each base replaces it with explicit at-base contents (Kanoya 2, Atsugi 3, Naha 3). Kanoya and Naha therefore do not inherit Atsugi's squadron, and no patrol airframe also appears at base. The usa_airbase alternative needs the same override.

**Gaps**
- No P-1 unit.
- No named base.
- SH-60K and SH-60J (3695809489) exist, but no source places helicopters at Atsugi, so they are not allocated.
- US tenants are not modelled.

**Validation.** Mapping re-resolved. Placement and runtime are untested.

---

### jpn_okinawa_naha - Naha (JMSDF air station, Okinawa)

**Identity.** JMSDF Fleet Air Wing 5 at Naha, Okinawa (R03:123). Host: Japan. Node kind: naval_air_station. Policy: populate.

**SOURCE claims**
- R01:61: P-1 used from "nodes like Naha and Atsugi".
- R03:121: network context (fidelity[1], optional).
- R03:123: FAW5 at Naha, "extreme proximity to the First Island Chain and the Taiwan Strait"; transition from the P-3C.
- R03:127 (simulation guidance): "rapid response times enabled by bases like Naha".

**Platform CHECK.** R03:127 names only Atsugi and Kanoya as P-1 bases. Only R01:61 ties the P-1 to Naha, and only jointly with Atsugi. The register check notes Naha is generally reported as still flying the P-3C. **SCENARIO:** use the exact P-3C, and relabel as P-1 stand-ins if verification shows Naha has converted. The label-route precondition (Kanoya CHECKS) would then apply.

**Position.**
- Public location: approx 26.2N 127.65E (Naha airfield). **Approx, verify.**
- In-game evidence:
  - proven placements: land 12 NM, sea 16 NM, air 9 NM;
  - stock asia_ports [Naha] 26.213,127.679, about 2 NM away;
  - stock airports [ROTM] MCAS Futenma, about 7 NM; [RODN] Kadena AFB, about 11 NM (Nation=US, not part of this package).
- Placement is pending validation.

**Installation**
- asset:mpn:naha_base: `airfield_small_1` Variant5 (Japan), labelled 'Naha Air Base (JMSDF) (stand-in)'. **proxy**.
  - The built-in 44-aircraft group is replaced. CustomAirGroup=True holds only the at-base identities naha_p3c_2, _3 and _4: `usn_p-3c=Squadron25,3`. Nothing else goes in the group.
  - naha_p3c_1 (patrol) is a separate airborne aircraft entry, usn_p-3c Squadron25, LoadoutVariant=ASW. It is never also in the group.
- A named base clone is **missing_fit**.
- CHECK: the airfield is shared with the JASDF and civil aviation. The reports do not say so.

**Forces** (SCENARIO allocation)

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:mpn:naha_p3c_1 | patrol | ASW patrol | usn_p-3c Squadron25 "P-3C 5th FAS 'Pegasus'" (Nation=Japan); separate airborne aircraft entry, LoadoutVariant=ASW | exact | 1 | R03:123 (FAW5, transition); the P-3C choice is SCENARIO |
| asset:mpn:naha_p3c_2 | resident_at_base | ready alert (rapid response, R03:127) | same, in the CustomAirGroup; ready-up `usn_p-3c,Squadron25,ASW,1,0` | exact | 1 | same |
| asset:mpn:naha_p3c_3 | resident_at_base | anti-surface ready | same, in the CustomAirGroup; ready-up `usn_p-3c,Squadron25,AntiShip,1,0` | exact | 1 | same |
| asset:mpn:naha_p3c_4 | servicing_maintenance | maintenance | same, in the CustomAirGroup | exact | 1 | same |

Some installed units exist but are not described at Naha in R01-R03, so they are not allocated: jasdf_f-15j_peaceeagle, usa_pac-3_launcher Variant6 (Japan) and jp_12ssmht.

**Support services.** Same as Kanoya:
- Ship ammunition: not applicable. The sources give Naha no berth role.
- Turnaround: airfield_small_1 stock, not established.
- Refuelling, restocking, fuel, repair: not established.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| Taiwan Strait | proximity and patrol focus | source | R03:123 |
| First Island Chain | ASW web | source | R01:61, R03:123 |
| jpn_kanoya_air_base | network | source | R03:123 |
| jpn_atsugi_naf | network | source | R01:61, R03:123 |
| chn_zhejiang_ningbo_naval_base / East China Sea | opposing axis, about 380 NM | authored | R03:105 (ETC area; no Naha link) |
| chn_hainan_lingshui_airbase | opposing ISR and counter-screen | authored | R03:168 names Kanoya and Atsugi, not Naha |

**Routine activity** (SCENARIO, proposed)
1. A P-3C patrol across the Miyako Strait area and the East China Sea toward the northern approaches to the Taiwan Strait (authored geometry, validate).
2. A ready airframe for quick launch. This is not a guaranteed response time.
3. Civilian pool asset:mpn:naha_civ_pool. A flag alone does not make a unit hostile.
   - 3 Japanese fishing vessels (civ_fv_fishingboat_c/d, civ_fv_sterntrawler_d);
   - 1 Japan-flag VLCC (civ_ms_ritina, Japan variants) on the Malacca-Japan lane;
   - civ_a330 Squadron43/44 (JAL).

**CHECKS**
- P-3C or P-1 at this station.
- The "rapid response" wording is guidance, not a rule.
- Shared JASDF and civil field.
- usn_p-3c_squadrons.ini [Default] sets ServiceDate=1977|1995 and the Japan Squadron21-29 set none of their own. Check in the editor whether a 2026+ mission filters them out. If it does, Naha's P-3C exact outcome and every P-1 stand-in need a SEST squadron patch with a ServiceDate.

**Gaps**
- A P-1 if Naha has converted.
- No named base.
- No JMSDF surface or submarine forces are sourced at Okinawa.

**Validation.** Mapping re-resolved. Placement and runtime are untested.
