<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Region summary: Chinese national logistics (JLSF) and the Ban Keun lead

**Nodes (7):** the six JLSF nodes (Wuhan HQ, and the JLSCs at Wuxi, Guilin, Xining, Shenyang and Zhengzhou) and the Ban Keun research lead.

**SOURCE CLAIM (R02:36-59, R01:33-37).**
- R02 describes the PLA Joint Logistics Support Force as a national HQ at Wuhan (R02:42) with five theatre-aligned Joint Logistics Support Centers beneath it (R02:44, R02:52-59).
- It names Guilin and Wuxi jointly as the logistics anchors that "would feed fuel and munitions" to Yulin, Longpo and Ningbo (R02:48).
- It says the logistics centres may mobilise civilian rail, motor transport, air freight and maritime shipping (R02:50). R02:79 adds a simulation-guidance recommendation (activate civilian maritime and rail assets via the JLSCs), not a further factual claim.
- R01 repeats the HQ and five-JLSC statements (R01:35). It adds the Ban Keun training-centre claim under the same heading (R01:33, R01:37).
- Repetition across the reports is not corroboration.

**Representation.**
- **All six JLSF nodes stay abstract**, as recorded in the register. They are register-only abstract logistics nodes and no installation is placed, for two reasons:
  - No PLA logistics or HQ unit exists in the collection (China lens installations: Wuhan, Wuxi, Guilin, Shenyang, Xining and Zhengzhou are all 'fit none').
  - Every one of the six is inland, from about 187 NM (Wuxi) to about 1,100 NM (Xining) from the nearest proven mission placement.
- **Ban Keun is do_not_populate** (plan:44).

**SCENARIO CHOICE: how the JLSF reaches the sea game.**
1. **Mobilised merchant hulls.** The only physical assets this region owns are four mobilised civilian merchant hulls, which stand for R02:50 civil-military fusion (SOURCE CLAIM: mobilisation authority) and the R02:79 surge mechanic (simulation guidance). There are two per theatre:
   - Eastern: owned by Wuxi, running to Ningbo.
   - Southern: owned by Guilin, running to Yulin.
   - In each theatre one hull is underway on a coastal relief run and one is a dormant surge reserve with a single release.
2. **No PLAN auxiliaries here.** PLAN replenishment ships (Type 903A, Type 901) belong to the PLAN, not the JLSF. Their named hulls are left to the Yulin, Ningbo and Djibouti packages, and none is allocated here.
3. **Shore stock belongs to the base packages.** The JLSF-fed depot behind each named naval base is that base package's shore supply. It is not modelled here.
4. **Disruption is gradual, never instant.**
   - It comes from finite pools emptying and from relief hulls being sunk.
   - The Wuhan rail-hub disruption (R01:68 = R02:78) becomes at most a delay on releasing the surge reserves.
   - R01:67/R02:77's 'instantly degrade' is not implemented (seed:23).

**Fidelity fixes applied (source-register fidelity checks 0 and 2):**
- **Guilin:** lists Yulin, Longpo and Ningbo jointly under R02:48. The Guilin-to-Yulin/Longpo pairing is labelled an authored theatre-alignment inference.
- **Wuxi:** Ningbo is removed as a sourced 'supplied base'. A Wuxi-to-Ningbo link is authored only, from theatre alignment (R02:44, R02:55; R03:105, R01:31).
- **Zhengzhou and Wuhan:** the conflict note is reworded to 'R02 gives two Central-theatre entries (Wuhan R02:54, Zhengzhou R02:59); the division of roles is unstated.'
- **Network-wide claims:** R02:48 (depot types), R02:50 and R02:79 are recorded once at Wuhan/network level and apply to every JLSC.

### What the engine and SEST replenishment actually support (inventory evidence; nothing tested in game here)

| Service | Evidence | Consequence for the JLSF chain |
|---|---|---|
| Ship ammunition at sea | `TruckSupplySystem` `[SupplySystem1]`:<br>- **plan_aor_type903a:** pool 220,000; MaxAmmoPoints 5,000; 80 pts/s; 0.6 nm; 2 receivers; own speed <=13 kn, receiver <=16 kn; Vessel and Submarine; categories AirTorpedo 32, SovietAdvancedASM 8, SEST_LandAttack 16, SEST_LongRangeSAM 24.<br>- **plan_aor_type901:** 400,000; 9,000; 110/s; 0.8 nm; categories AirTorpedo 40, SovietAdvancedASM 12, SEST_LandAttack 32, SEST_LongRangeSAM 32.<br>Both are SEST stand-ins on donor meshes, i.e. proxies (installations-placement-support (IPS) lens verify correction). SEST-tuned merchants also exist: civ_ms_c8, civ_ms_seabee, civ_ms_roro_a/b and civ_ms_mercur (IPS support_and_traffic). | Finite hulls are the only way JLSF effort reaches ships at sea. |
| Ship ammunition at the shore | The only shore suppliers are RE-power's nv_pt_boats_docks (Vessel) and nv_pt_boats_docks_small (Submarine): AmmoCapacity 9,999,999,999, no ceiling, 3 nm, 6 receivers. No vanilla port carries supply (IPS gaps). | A ship alongside the Yulin or Ningbo stand-in pier draws without limit, so a depot 'running dry' (R01:67, R02:77) cannot happen there unless the base package chooses a finite representation. |
| Supplier restocking | Not established. Pools deplete and are not refilled at sea or by any port (IPS gaps; docs/replenishment-in-play.md:113). A merchant can top up another supplier's own defensive magazine, not its supply pool (integration/replenishment/README.md). | Renewal means the next finite hull arriving, never a refill. |
| Ship fuel | Not modelled: no vessel fuel keys, and 'oilers' pass ammunition only (IPS gaps). | POL depots, pipelines and fuel stations (R02:48) are abstract. |
| Repair | Not established outside the Task Force Mode between-mission flags (IPS gaps). | None. |
| Aircraft fuel | Air-to-air refuelling only, both RefuelSystem: plaaf_yy-20a (FuelCapacity 75,000) and plaaf_y-20b (75,000, Tanker loadout only: mods-source/3782020901/aircraft/plaaf_y-20b.ini [WeaponSystem1Tanker] :171-173). The IPS verify missed-asset figure of 160,000 is stale (it is usaf_kc-10's value; the Y-20B read 45,000 before the 6 Oct export, commit 25e18b9b). | These are PLAAF aircraft for the aviation nodes, not JLSF assets. |
| Air cargo ammunition | The only such system is usaf_c-141b's PlaneCargoSupplySystem (US-flagged, untested; IPS verify missed asset). | No Chinese equivalent, so civil air freight (R02:50) cannot be represented. |
| Land-unit rearm | nv_headquarters: unlimited, LandUnit targets, 2 nm. tgt_ammo_depot_small: finite 200,000-point pool, LandUnit targets, 1.5 nm. | An option for the coastal TEL packages to stand for a JLSF ammunition depot. It cannot reach ships or aircraft. |
| Finite reserve release | A unit can start `Disabled=True` and be woken by a trigger with `Action_SetEnabledStatus=True`. Stock uses this, on one vessel among others (scope-and-performance 2.8). | This is the mechanism for a one-shot surge reserve. It is untested in a SEST world and across save/load. |
| Respawning traffic | `[CivilianRouteN]` respawns units, which conflicts with finite allocation unless MaxUnits is bounded (IPS placement_and_engine). | Not used for mobilised hulls. |

**PLAN receiver fit.** File-derived from AmmoPoints and SupplyCategory; untested.

| Round | Carried by | Points | Category | Type 903A (ceiling 5,000) | Type 901 (ceiling 9,000) | civ_ms_c8 (ceiling 8,000) | civ_ms_roro_a (ceiling 2,000) |
|---|---|---|---|---|---|---|---|
| HHQ-9B | 052D / 055 | 5,250 | SEST_LongRangeSAM | refused | admitted | admitted | refused |
| YJ-18C | 052D / 055 | 5,100 | SEST_LandAttack | refused | admitted | admitted | refused |
| YJ-19 | 039B | 8,800 | SEST_LandAttack | refused | admitted | refused | refused |
| Yu-8 ASROC | 052D / 054A | 2,600 | none | admitted | admitted | admitted | refused |
| Yu-11 / Yu-15 | 056A (the Yulin relief escort) / 055 | 2,950 | none | admitted | admitted | admitted | refused |
| Yu-10 | 039B | 4,850 | none | admitted | admitted | admitted | refused |
| YJ-83 / YJ-83A, HQ-10, HQ-16 (054A_p3, the Ningbo relief escort), Yu-12, guns | various | up to 1,700 | none | admitted | admitted | admitted | admitted |
| Unrationed: HHQ-9C, YJ-17, YJ-18A, YJ-20 (052D / 055); HQ-16C (054A); Yu-7C (054A / 056A); YJ-12 ship; YJ-18, Yu-6, Yu-6A, Yu-9 (039B) | various | none declared | none | free | free | free | free |

- **Unrationed rounds.** Some rounds carry neither AmmoPoints nor a category, so any supplier, including a Ro-Ro and the unlimited pier, hands them over without depleting its pool ("no gate can ration the transfer", integration/replenishment/README.md). "free" in the table above means this:
  - plan_yj-18a, plan_yj-20 and plan_yj12_ship (integration/replenishment/README.md);
  - plan_yu-7c_ship, pla_yu-6 and pla_yj-18 (China lens);
  - plan_hhq-9c and plan_yj-17: integration/dist/SEST_Integration/vessels/plan_type_052d_p3.ini Ammunition at :433, :958 and :615, :840; both also on plan_type_055_2026;
  - plan_hq-16c: plan_type_054a_p5.ini :816, :901, :986, the whole SAM load of the 054A_p5 (Yulin's asset:chn:yulin_ffg_1); the Ningbo relief escort plan_type_054a_p3 carries the priced plan_hq-16 (1,700, no category; :821, :905, :990) instead;
  - plan_yj-18, plan_yu-6, plan_yu-6a and plan_yu-9 on plan_ss_type_039b.
  - Winning ammunition files re-resolved with find_unit_file; none of these declares AmmoPoints or SupplyCategory.
  - This is a CHECK on the finite-logistics intent, and a larger one than a footnote: much of the 052D/055 heavy load (HHQ-9C, YJ-17, YJ-18A, YJ-20) and all of the 054A_p5's HQ-16C refill free. Finite hulls ration only the metered rounds: HHQ-9B, YJ-18C and YJ-19, plus the priced uncategorised rounds against each supplier's ceiling.

### Civil-military fusion: hulls that could act as mobilised logistics (proposal)

| Unit id | Hull and supply (winning file) | Variant flags | Outcome as mobilised Chinese shipping | Use here |
|---|---|---|---|---|
| civ_ms_roro_a | 205.8 m Ro-Ro, ServiceDate 1972. Pool 80,000; ceiling 2,000; 30/s; 0.5 nm; 1 receiver; <=8/12 kn; Harpoon 8, AirTorpedo 16. Placed in 13 SEST/stock mission files. | US, Norway, Soviet | proxy: visible label, and a per-unit Nation=china that is untested for vessels | allocated x2 |
| civ_ms_c8 | 272 m barge carrier, ServiceDate 1968. Pool 300,000; ceiling 8,000; 35/s; 0.5 nm; 1 receiver; <=8/12 kn; Harpoon 24, AirTorpedo 32, ALWT 16, SEST_LandAttack 16, SEST_LongRangeSAM 16. Placed in 11 files. | US, Norway, Germany, Netherlands | proxy | allocated x2 |
| civ_ms_seabee | As the C8, plus SovietAdvancedASM 8. No stock or integration/ mission placement; placed in game-written SEST user saves (mods-source/_vanilla/user/missions/user_missions/SEST/NORTHERN FRONT III FINAL NEWEST.ini:381, mods-source/_vanilla/user/missions/NORTHERN FRONT.ini:381) and one Workshop mission (mods-source/3491248180/missions/The Falklands War/Mission 1 - Baptism of Fire.ini:537). | US, Soviet | proxy | alternative to the C8 |
| civ_ms_roro_b / civ_ms_mercur | 139.6 m Ro-Ro / 169.6 m container ship. Pools 80,000 / 50,000; ceiling 2,000; AirTorpedo 16 / 12. | Soviet | proxy | spare alternatives |
| RE-power merchants (civ_ms_freighter_a/b/d, civ_ms_poltava, civ_ms_amra, etc.) | Live supply: pool 2.4-12 million, no ceiling, near-instant transfer, Vessel targets only. | various; no China | rejected: unlimited supply breaks the finite rule. Also avoid them as neutral traffic near PLA forces. | not used |
| plan_ap_qiongsha | China-flagged natively (flag_prc). No supply block. ServiceDate 1980, no end date (Cold War hull). | China | missing_fit: presence only, no logistics function | fallback only if the Nation override fails |
| plan_lst_yukan | China-flagged natively. No supply block. Every variant's ServiceDate ends in 2020 (1979, 1981 or 1982 to 2020). | China | missing_fit, and out of date for a 2026 world | not a fallback |
| civ_fv_fishingboat_a, Variant5 'Fishing boat China' | Fishing boat, no supply. Its variant flag is US. | US | not a logistics asset | the maritime-militia gap belongs to the Chinese maritime packages |
| Civil air freight / rail / heavy motor transport | No Chinese civil cargo aircraft: the China squadrons of civ_a330 are airliners. Rail is not modelled. Trucks rearm land units only. | - | none | abstract; backlog |

**Region-wide checks.**
- **Per-unit vessel nation is unproven.** Stock missions write `Nation=` on vessel sections. For example, 'Red Madagascar 1985.ini:300-309' places civ_fv_fishingboat_a, whose variants are all Nation=US, with Nation=india. However:
  - the China lens states that vessel nation comes from the variant file;
  - the IPS lens lists per-unit flag rendering as unverified;
  - the variants carry their own FlagTexture (e.g. flag_us).

  So whether a C8 or Ro-Ro becomes PLA-side and flies a Chinese flag is untested.
- **Identity.**
  - The four mobilised hulls appear only in this region. The Yulin and Ningbo packages must not count them, even while they are at those anchorages.
  - All four use `VariantReference=Default` (generic 'Barge Carrier' / 'RORO A') and a unique NameOverride carrying the asset (E-1, E-2, S-1, S-2). No MSC/RRF-named or real-merchant variant is consumed here (see Wuxi labelling).
  - Relief escorts are base-package assets, never JLSF ones. An escort that sails at t=0 needs a reciprocal slot in the Ningbo or Yulin package (world integration C14: asset:chn:ningbo_ffg_1 for wuxi-mob-roro-1, asset:chn:yulin_corvette_2 for guilin-mob-cargo-1). An escort for a reserve release leaves its base count when it sails.
  - No PLAN AOR hull is allocated here: Taihu 889, Chaohu 890, Honghu 963, Luomahu 964, Hulunhu 965 and Chaganhu 967 remain available to the naval packages.
- **City-name collisions.** Ship hulls named after JLSF cities are ships, not these nodes:
  - Wuxi: 104 (Type 055) and FF-512;
  - Guilin: 164;
  - Xining: 117 and DDG-108;
  - Zhengzhou: 151;
  - Wuhan: 169 (052B), plus the vanilla plan_ssg_wuhan class;
  - Shenyang: 115 (051C).

  Source: China lens placement_and_engine and verify correction.

---

### chn_jlsf_wuhan_base - Wuhan Joint Logistics Support Base

**Identity.**
- Aliases: Wuhan JLSF Base, JLSF HQ.
- Operator: PLA Joint Logistics Support Force (as reported).
- Host: China, Hubei.
- Source section: R02:36-59, R01:33-35.
- Policy: abstract_logistics_only.

**SOURCE CLAIM.**
- Created in a 2016 restructuring; centralises sustainment of the Army, Navy, Air Force and Rocket Force (R02:38).
- Upgraded to a full PLA 'Arm' in 2024, centralising sustainment under a unified command structure (R02:38; R01:35).
- HQ at the Wuhan base in Hubei (R02:42; R01:35).
- Wuhan was chosen as China's geographic 'weight center' and a national rail, road and river hub (R02:42).
- Five JLSCs beneath it mirror the five Theater Commands: Wuxi, Guilin, Xining, Shenyang and Zhengzhou (R02:44). R01:35 gives the count only.
- Network-wide claims (recorded here per the fidelity checks):
  - the JLSCs manage POL depots, oil pipeline groups, field fuel station detachments, ammunition depots, quartermaster depots and heavy equipment transport units (R02:48; shorter list at R01:35);
  - the logistics centres may mobilise civilian rail, heavy motor transport, air freight and maritime shipping (R02:50);
  - a player as the PLA should be able to activate civilian maritime and rail assets via the JLSCs (R02:79, simulation guidance).
- Table row: 'Central Command / National HQ' (R02:54).
- Bombing major rail hubs out of Wuhan should cascade into reinforcement delays for frontline bases (R01:68 = R02:78, a verbatim repeat; simulation guidance).

**CHECK.**
- 'Arm'/2024 terminology is a priority check (seed:23).
- R02 gives two Central-theatre entries (Wuhan R02:54, Zhengzhou R02:59); the division of roles is unstated.
- The rail hubs and frontline bases are unnamed (expansion backlog).
- The overlapping lines in R01 and R02 are not corroboration.
- Hull 'Wuhan (169)' (plan_type_052b_2004/_2019) and vanilla plan_ssg_wuhan are ships, not this node.

**Role.** Command: national logistics HQ. It is not a tactical depot (plan:17, 'A headquarters is not automatically a tactical ammunition depot'; plan:36, Chinese national support row).

**Position.**
- Hubei Province (R02:42, R02:54). Public approximate position (city centre; the facility's site is not given): 30.6N 114.3E. Approx, verify.
- In-game evidence: none nearby.
  - Nearest proven placement: land about 382 NM (airfield_small_1 at 26.00N 119.31E, stock pacific-strike-task-force/missions/02 Action in the Taiwan Strait.ini:574); air about 350 NM; sea about 396 NM.
  - Nearest stock world-data point: asia_ports.ini [Shanghai] (a city label), about 371 NM.
  - Inland terrain is untested.
- No placement is proposed.

**Forces (SCENARIO CHOICE).**

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:chn-jlsf:wuhan-hq | abstract | National logistics HQ, register-only | - | none | 0 units | R01:35, R02:42, R02:54 |
| asset:chn-jlsf:wuhan-rail-hubs | abstract | Unnamed rail hubs out of Wuhan; only a reinforcement-timing modifier | - | none | 0 units | R01:68, R02:78 |

Representations considered and not placed:
- **nv_headquarters** (RE-power 'Army Headquarters'): rearms only land units within 2 nm and renders as a Vietnamese HQ.
- **warehouses_3** (vanilla): a target object with no supply.
- **tgt_ammo_depot_small:** supplies land units only.
- **plaaf_airlift_airbase** (Y-20A/B, YY-20A): the operator is the PLAAF, not the JLSF. It is a proxy only. The airlift has no ammunition-cargo supply function (no PlaneCargoSupplySystem): the Y-20B carries Transport, Tanker and Paradrop loadouts only (Paradrop stations pla_airdrop_type63 and pla_paratrooper).

**Support.** Ship ammunition, aircraft turnaround, restocking, fuel and repair are all not established. The node has no physical presence.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| chn_jlsf_wuxi_jlsc, chn_jlsf_guilin_jlsc, chn_jlsf_xining_jlsc, chn_jlsf_shenyang_jlsc, chn_jlsf_zhengzhou_jlsc | parent HQ of the JLSCs | source | R02:44 (R01:35 count) |
| chn_zhejiang_ningbo_naval_base, chn_hainan_yulin_naval_base | reinforcement-timing modifier (rail hubs out of Wuhan) | authored | R01:68, R02:78; the hubs and frontline bases are unnamed and the pairing is ours |

**Routine activity.** Proposed, abstract, not implemented. If rail disruption is modelled at all, it only delays the release triggers of asset:chn-jlsf:wuxi-mob-cargo-2 and asset:chn-jlsf:guilin-mob-roro-2. It never disables units or depots. Because no Wuhan target exists, the delay would be driven by an authored timeline or event.

**Validation.**
- Research: abstract node, terminology check open.
- Mapping: none.
- Placement: none proposed.
- Runtime, save: not applicable.
- Missing: a PLA HQ/logistics installation, a rail network, named hubs.

---

### chn_jlsf_wuxi_jlsc - Wuxi Joint Logistics Support Center

**Identity.**
- Aliases: Wuxi JLSC, 'the Wuxi center'.
- Operator: PLA JLSF (as reported).
- Host: China, Jiangsu.
- Policy: abstract_logistics_only. The node is not placed; its sea effect comes through two mobilised hulls (SCENARIO CHOICE).

**SOURCE CLAIM.**
- A JLSC in Wuxi, aligned to the Eastern Theater and subordinate to Wuhan (R02:44).
- Table row: Jiangsu Province; supports Eastern Theater Command (Taiwan Strait) (R02:55).
- With Guilin, 'the critical logistical anchors that would feed fuel and munitions to the naval bases at Yulin, Longpo, and Ningbo' (R02:48). No per-base pairing is given.
- Depots under 'the Wuxi center'; if they run dry, effectiveness 'must instantly degrade' (R01:67 = R02:77, simulation guidance).
- Network claims R02:48, R02:50 and R02:79 apply (recorded at Wuhan).

**CHECK.**
- A Wuxi-to-Ningbo link is an authored inference from theatre alignment (R02:44, R02:55; R03:105, R01:31), not a source claim. This is the fidelity check 2 fix.
- 'Would feed' is conditional framing.
- No instant-disable rule (seed:23).
- JLSF terminology is a priority check (seed:23). The depots are unnamed.
- R01:67/R02:77 is a repetition; only R02 gives the location.
- Hulls 'Wuxi (104)' (plan_type_055_2020/_2026 and their RSA duplicates) and 'Wuxi FF-512' (vanilla plan_ff_jianghu1) are ships.

**Role.** Regional logistics centre, abstract.

**Position.**
- Node: Jiangsu (R02:55). Public approximate city centre 31.5N 120.3E; the facility is not given. Approx, verify.
- In-game evidence for the node:
  - Nearest proven placement: land about 187 NM (airfield_small_1 at 28.54N 121.42E, stock pacific-strike-task-force/missions/01 Raid on Okinawa.ini:402); air about 223 NM; sea about 294 NM.
  - Stock world-data asia_ports.ini [Shanghai] (Location 31.2304,121.4737, Nation=China; a city label loaded as BackgroundCityFile3 by 01 Raid on Okinawa.ini:467), about 62 NM away.
- Relief run (SCENARIO CHOICE): from the Yangtze estuary approaches at about 31.0N 122.2E, south to the Ningbo/Zhoushan approaches at about 29.9N 122.2E. Approx, verify water.
  - The nearest proven sea placement to Ningbo is about 206 NM away (civ_ms_andizhan at 26.61N 120.78E). That is beyond the builder's 60 NM snap, and the committed coast extract covers only 100-180E / 25-72S.
  - Validate the route with the global-land-mask tools (fix_land_positions.py, sea_routes.py).

**Forces (SCENARIO CHOICE).**

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:chn-jlsf:wuxi-jlsc | abstract | Eastern Theater JLSC and its unnamed depots | - | none | 0 units | R02:44, R02:48, R02:55 |
| asset:chn-jlsf:wuxi-mob-roro-1 | transit | Mobilised Ro-Ro on a coastal relief run to Ningbo, then a slow cargo-pass supplier at the anchorage | civ_ms_roro_a | proxy | 1 hull | SOURCE CLAIM R02:50 (mobilisation authority); R02:79 simulation guidance (surge mechanic); hull, number and route are SCENARIO CHOICE |
| asset:chn-jlsf:wuxi-mob-cargo-2 | reserve | Dormant surge cargo ship, released once | civ_ms_c8 | proxy | 1 hull | SOURCE CLAIM R02:50 (mobilisation authority); R02:79 simulation guidance (surge mechanic); hull, number and trigger are SCENARIO CHOICE |

**Labelling and allocation for both hulls.**
- Labels:
  - a unique `NameOverride` per hull carrying its asset: 'Mobilised Ro-Ro E-1 (stand-in)' (wuxi-mob-roro-1) and 'Mobilised cargo ship E-2 (stand-in)' (wuxi-mob-cargo-2);
  - per-unit Nation=china (CHECK);
  - `VariantReference=Default` on both: the generic 'RORO A' / 'Barge Carrier' (Nation=US, flag_us, ServiceDate 1972 / 1968).
- Named variants are not used. civ_ms_c8 Variants 23-26 are the MSC hulls Cape Fear, Cape Flattery, Cape Florida and Cape Farewell (T-AK-5061, 5070-5072). civ_ms_roro_a Variants 6-10 are the Ready Reserve hulls Cape Ducato to Cape Diamond (T-AKR-5051 to 5055). The other variants are named real merchants (language_en/vessel_names.ini). US or Indian Ocean packages may allocate those named hulls, and a named variant keeps its own FlagTexture.
- Default is a generic class label, not a hull identity, so other regions using it is not a double allocation. Identity is the asset id plus the NameOverride.
- Owned here; the Ningbo package does not count them.
- Escort: a Ningbo package asset, never allocated here (see Routine activity).

**Why these hulls (authored rationale).**
- A Ro-Ro reads as heavy-equipment and vehicle lift on a short strait run (R02:48 heavy equipment transport units; R02:50 maritime shipping).
- The C8 reserve's 8,000 ceiling and SEST_LongRangeSAM/SEST_LandAttack stocks of 16 each let it pass HHQ-9B and YJ-18C, which a Type 903A cannot.
- That argument covers only the metered heavy rounds: HHQ-9B and YJ-18C, with YJ-19 (8,800) metered but beyond the C8 ceiling too. HHQ-9C, YJ-17, YJ-18A, YJ-20 and the 054A_p5's HQ-16C (a Yulin hull, not the Ningbo escort, whose plan_hq-16 at 1,700 is priced) are unrationed and refill free from any supplier (region-wide CHECK).

**Support.**
- **Ship ammunition:**
  - civ_ms_roro_a: pool 80,000, ceiling 2,000, 30 pts/s, 0.5 nm, 1 receiver, <=8/12 kn, Vessel and Submarine; Harpoon 8, AirTorpedo 16. It passes guns, HQ-10, HQ-16 (1,700), YJ-83/83A and Yu-12. It refuses Yu-8 (2,600, on its own 054A_p3 escort, plan_type_054a_p3.ini:1074), Yu-11 (2,950, 056A), the 039B's Yu-10 (4,850), HHQ-9B and YJ-18C, so it cannot fully restock its own escort.
  - civ_ms_c8: pool 300,000, ceiling 8,000, 35 pts/s; Harpoon 24, AirTorpedo 32, ALWT 16, SEST_LandAttack 16, SEST_LongRangeSAM 16. It refuses YJ-19.
  - Unrationed rounds flow free from either hull: HHQ-9C, YJ-17, YJ-18A, YJ-20, YJ-12 ship, HQ-16C, Yu-7C, and the 039B's YJ-18, Yu-6, Yu-6A and Yu-9.
- **Aircraft turnaround and ordnance:** not applicable.
- **Supplier restocking:** not established. Neither hull can refill a PLAN AOR's pool.
- **Fuel:** not established for ships.
- **Repair:** not established.
- **At the destination:** Ningbo's stand-in pier (nv_pt_boats_docks, owned by the Ningbo package) is effectively unlimited.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| chn_jlsf_wuhan_base | subordinate to HQ | source | R02:44 |
| chn_hainan_yulin_naval_base, chn_hainan_longpo_naval_base, chn_zhejiang_ningbo_naval_base | joint fuel/munitions anchor, with Guilin; no per-base pairing | source | R02:48 |
| chn_zhejiang_ningbo_naval_base | relief-run destination and escort source | authored | R02:44, R02:55; R03:105, R01:31 |
| sea:Taiwan Strait | supported theatre | source | R02:55, R02:48 |
| sea:East China Sea | relief-run operating area | authored | R03:105 (not stated for Wuxi) |

**Routine activity (proposed, not implemented).**
- **roro-1:** starts underway at the estuary approach and transits about 70 NM to the Ningbo outer anchorage. It holds there as a finite supplier until its pool is spent or it is sunk, then departs or remains empty. One run, no respawn.
- **cargo-2:** starts `Disabled=True` at an authored holding point off the estuary. It is released once, by a trigger, when roro-1 is spent or sunk or on an authored timeline. The Wuhan rule may delay the release.
- **Escort (cross-package, one allocation per hull):**
  - roro-1 is underway from t=0, so its escort is too: asset:chn:ningbo_ffg_1 (plan_type_054a_p3, pinned Variant1 'Daqin (576)'), whose Ningbo allocation changes from resident_at_base to escort from t0 (world integration C14). It is a Ningbo package asset, never allocated here.
  - For the cargo-2 release, the escort is a Ningbo unit at base at release time other than asset:chn:ningbo_ffg_1, removed from the Ningbo base count when it sails. The Ningbo package must record the hand-over (recorded in china-maritime: the escort is allocated from t0, with the release rule).
  - The earlier example types (plan_type_056a, plan_type_054a_p5) are withdrawn: the Ningbo package fields neither.
- **Neutral surroundings:**
  - Vanilla non-supplying merchants with neutral flags: civ_ms_bulk (Japan, Liberia, Greece), civ_ms_car_carrier_a (Japan, Panama, Liberia), civ_ms_mairangi_bay (Japan).
  - civ_a330 China squadrons as an airliner overflight; these need airways.
  - No China-flagged merchant exists.
  - Bound any CivilianRoute MaxUnits.

**Validation.**
- Research: abstract node; pairing inference labelled.
- Mapping: civ_ms_roro_a and civ_ms_c8 re-resolved to SEST_Integration; outcome proxy.
- Placement: pending; route not validated.
- Runtime: the Nation override, the dormant release and the transfers are untested.
- Save: saves hold supplier CurrentAmmo (scope-and-performance 2.9); reload is untested.
- Missing: a China-flagged merchant or Ro-Ro, named depots and port.

---

### chn_jlsf_guilin_jlsc - Guilin Joint Logistics Support Center

**Identity.**
- Alias: Guilin JLSC.
- Operator: PLA JLSF (as reported).
- Host: China, Guangxi.
- Policy: abstract_logistics_only. The node is not placed; its sea effect comes through two mobilised hulls (SCENARIO CHOICE).

**SOURCE CLAIM.**
- A JLSC in Guilin, aligned to the Southern Theater and subordinate to Wuhan (R02:44).
- Table row: Guangxi Region; supports Southern Theater Command (South China Sea) (R02:56).
- With Wuxi, the anchor that 'would feed fuel and munitions' to Yulin, Longpo and Ningbo, with no per-base pairing (R02:48).
- Network claims R02:48, R02:50 and R02:79 apply.
- Only R02 mentions Guilin.

**CHECK.**
- Fidelity check 0 fix: all three bases are listed under R02:48. The Guilin-to-Hainan pairing is an authored inference (R02:44, R02:56; R03:97-99, which place Hainan in the Southern Theater).
- 'Would feed' is conditional framing.
- JLSF terminology check (seed:23).
- Hulls 'Guilin (164)' (plan_type_052d_p1/p3, RSA plan_ddg_type_052D_rsa) and Guilin DDG-164 (plan_ddg_luda_typ_051d, RSA plan_ddg_type051m, vanilla plan_dd_luda1) are ships.

**Role.** Regional logistics centre, abstract.

**Position.**
- Node: Guangxi (R02:56). Public approximate city centre 25.3N 110.3E. Approx, verify.
- In-game evidence for the node:
  - Nearest proven placement: air about 413 NM (pla_q-5 at 18.41N 110.0E, stock PLAN/PLAN 01 Clash in the Paracels.ini:300); land about 421 NM (wp_airbase_4 at 18.30N 109.72E, pacific-strike-task-force/missions/10 Vengeance at Luzon.ini:1100); sea about 490 NM.
  - Nearest world-data point: Hong Kong (asia_ports.ini), about 278 NM.
- Relief run (SCENARIO CHOICE): from the eastern approach to the Qiongzhou Strait at about 20.1N 110.9E, down Hainan's east coast to the Yulin approaches at about 18.2N 109.6E (about 150 NM). Approx, verify water.
  - Yulin has a proven land placement 8 NM away (airfield_small_1 at 18.29N 109.43E, stock PLAN 02 Battle of the South China Sea.ini:507).
  - The nearest proven sea placement is about 112 NM away (civ_ms_poltava, same mission line 410).

**Forces (SCENARIO CHOICE).**

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:chn-jlsf:guilin-jlsc | abstract | Southern Theater JLSC and its unnamed depots | - | none | 0 units | R02:44, R02:48, R02:56 |
| asset:chn-jlsf:guilin-mob-cargo-1 | transit | Mobilised cargo ship on a relief run to the Yulin anchorage, then a finite cargo-pass supplier | civ_ms_c8 | proxy | 1 hull | SOURCE CLAIM R02:50 (mobilisation authority); R02:79 simulation guidance (surge mechanic); hull, number and route are SCENARIO CHOICE |
| asset:chn-jlsf:guilin-mob-roro-2 | reserve | Dormant surge Ro-Ro, released once | civ_ms_roro_a | proxy | 1 hull | SOURCE CLAIM R02:50 (mobilisation authority); R02:79 simulation guidance (surge mechanic); hull, number and trigger are SCENARIO CHOICE |

**Labelling and allocation.**
- Labels: unique NameOverrides 'Mobilised cargo ship S-1 (stand-in)' (guilin-mob-cargo-1) and 'Mobilised Ro-Ro S-2 (stand-in)' (guilin-mob-roro-2); per-unit Nation=china (CHECK); `VariantReference=Default` on both, for the reasons given under Wuxi (no MSC/RRF-named or real-merchant variant).
- Owned here; the Yulin package does not count them.
- No relief routing to Longpo is proposed; the strategic submarine base is recorded as a bare fact only.
- Rationale: the longer haul and the 300,000-point pool make the C8 the first arrival. Its 8,000 ceiling gives finite HHQ-9B and YJ-18C relief that the Type 903A cannot pass. This covers the metered rounds only; HHQ-9C, YJ-17, YJ-18A, YJ-20 and HQ-16C refill free from any supplier, including the Yulin pier.

**Support.**
- **Ship ammunition:** as in the Wuxi package (same two hull types and figures). The Ro-Ro refuses the 056A escort's Yu-11 (2,950) and the 039B's Yu-10 (4,850); the C8 admits both.
- **Aircraft turnaround:** not applicable.
- **Restocking, fuel, repair:** not established.
- **At the destination:** the Yulin pier stand-in (owned by the Yulin package) is effectively unlimited.

**Connections.**

| To | Kind | Basis | Ref |
|---|---|---|---|
| chn_jlsf_wuhan_base | subordinate to HQ | source | R02:44 |
| chn_hainan_yulin_naval_base, chn_hainan_longpo_naval_base, chn_zhejiang_ningbo_naval_base | joint fuel/munitions anchor, with Wuxi; no per-base pairing | source | R02:48 |
| chn_hainan_yulin_naval_base | relief-run destination and escort source | authored | R02:44, R02:56; R03:97-99 |
| sea:South China Sea | supported theatre | source | R02:56, R02:48 |

**Routine activity (proposed, not implemented).**
- **cargo-1:** a one-way transit to the Yulin anchorage. It holds as a supplier until spent or sunk.
- **roro-2:** starts `Disabled=True` off north-east Hainan, at about 20.0N 111.0E (approx, verify). It is released once by a trigger or timeline, with the Wuhan rule possibly delaying it.
- **Escort (cross-package, one allocation per hull):**
  - cargo-1 is underway from t=0: its escort is asset:chn:yulin_corvette_2 (plan_type_056a, pinned Variant2 'Qinhuangdao (505)'), whose Yulin allocation changes from resident_at_base to escort from t0 (C14).
  - For the roro-2 release, the escort is a Yulin unit at base at release time other than asset:chn:yulin_corvette_2, removed from the Yulin base count when it sails. The Yulin package must record the hand-over (recorded in china-maritime: the escort is allocated from t0, with the release rule).
- **Neutral surroundings:** vanilla non-supplying merchants (civ_ms_bulk, civ_ms_ritina, civ_ms_car_carrier_a variants with Japan, Liberia, Greece or Panama flags). Avoid RE-power supplier merchants.

**Validation.** As for Wuxi. Also, terrain and water near Hainan are partly proven by stock PLAN missions.

---

### chn_jlsf_xining_jlsc - Xining Joint Logistics Support Center

**Identity.**
- Alias: Xining JLSC.
- Operator: PLA JLSF (as reported).
- Host: China, Qinghai.
- Policy: abstract_logistics_only (context only).

**SOURCE CLAIM.**
- A JLSC in Xining, Western Theater, subordinate to Wuhan (R02:44).
- Table row: Qinghai Province; supports Western Theater Command (R02:58).
- Network claims R02:48, R02:50 and R02:79 apply.
- Only R02 mentions it.

**CHECK.**
- JLSF terminology check (seed:23).
- No maritime role is stated.
- Hulls 'Xining (117)' (052D, MPS and RSA) and Xining DDG-108 (Luda family) are ships.

**Role.** Regional logistics centre, kept for completeness of the JLSF structure.

**Position.**
- Qinghai (R02:58). Public approximate city centre 36.6N 101.8E. Approx, verify.
- In-game evidence: nearest proven placement about 1,100 NM (land: airfield_small_1 at 26.00N 119.31E, stock 02 Action in the Taiwan Strait.ini:574). It is the most remote JLSF node; the IPS lens puts Belaya further out (1,271 NM against Xining's 1,102).
- Not placed.

**Forces.**

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:chn-jlsf:xining-jlsc | abstract | Western Theater JLSC, register-only | - | none | 0 units | R02:44, R02:58 |

**Support.** All not established.

**Connections.** chn_jlsf_wuhan_base: subordinate (source, R02:44). Western Theater Command: supported theatre (source, R02:58; no world node).

**Routine activity.** None.

**Validation.** Abstract. No mapping or placement. Missing: nothing needed for the maritime sandbox.

---

### chn_jlsf_shenyang_jlsc - Shenyang Joint Logistics Support Center

**Identity.**
- Alias: Shenyang JLSC.
- Operator: PLA JLSF (as reported).
- Host: China, Liaoning.
- Policy: abstract_logistics_only.

**SOURCE CLAIM.**
- A JLSC in Shenyang, Northern Theater, subordinate to Wuhan (R02:44).
- Table row: Liaoning Province; supports Northern Theater Command (Yellow Sea/Korea) (R02:57).
- Network claims R02:48, R02:50 and R02:79 apply.
- Only R02 mentions it.

**CHECK.**
- No Northern Theater naval base is named in R01-R03 (backlog). Any maritime link would be authored.
- JLSF terminology check (seed:23).
- Hull 'Shenyang (115)' (plan_type_051c) is a ship.

**Role.** Regional logistics centre, abstract.

**Position.**
- Liaoning (R02:57). Public approximate city centre 41.8N 123.4E. Approx, verify.
- In-game evidence, all from user missions in the IPS scan scope:
  - air about 127 NM (wp_tu-22m2 at 43.81N 124.31E, mods-source/_vanilla/user/missions/user_missions/GULF ATTACK .7.7.ini:1000);
  - sea about 257 NM (civ_ms_ritina at 39.58N 128.23E, user mission 'newest 0.7 updated mods v2 smaller.ini:211');
  - land about 282 NM (pla_sam_site_hq-9_morden at 41.35N 129.66E, user 'NK US ATTACK .7.ini:731').
- Nearest world-data point: Pyongyang, about 198 NM.
- Not placed.

**Forces.**

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:chn-jlsf:shenyang-jlsc | abstract | Northern Theater JLSC, register-only | - | none | 0 units | R02:44, R02:57 |

SCENARIO CHOICE: no mobilised hulls until a Northern Theater naval node is researched.

**Support.** All not established.

**Connections.** chn_jlsf_wuhan_base: subordinate (source, R02:44). sea:Yellow Sea / Korea: supported theatre (source, R02:57).

**Routine activity.** None.

**Validation.** Abstract. Missing: the PLAN Northern Theater naval bases (expansion backlog).

---

### chn_jlsf_zhengzhou_jlsc - Zhengzhou Joint Logistics Support Center

**Identity.**
- Alias: Zhengzhou JLSC.
- Operator: PLA JLSF (as reported).
- Host: China, Henan.
- Policy: abstract_logistics_only.

**SOURCE CLAIM.**
- A JLSC in Zhengzhou, Central Theater, subordinate to Wuhan (R02:44).
- Table row: Henan Province; supports Central Theater Command (Strategic Reserve) (R02:59).
- Network claims R02:48, R02:50 and R02:79 apply.
- Only R02 mentions it.

**CHECK.**
- Reworded per the fidelity fix: R02 gives two Central-theatre entries (Wuhan R02:54, Zhengzhou R02:59), and the division of roles is unstated.
- 'Strategic Reserve' does not say what is held, so no naval reserve is inferred.
- Hull 'Zhengzhou (151)' (052C, MPS and RSA) is a ship.

**Role.** Regional logistics centre (strategic reserve), abstract.

**Position.**
- Henan (R02:59). Public approximate city centre 34.8N 113.6E. Approx, verify.
- In-game evidence: nearest proven placement about 545 NM (land: airfield_small_1 at 28.54N 121.42E, stock 01 Raid on Okinawa.ini:402).
- Not placed.

**Forces.**

| Asset | Allocation | Role | Unit | Outcome | Qty | Basis |
|---|---|---|---|---|---|---|
| asset:chn-jlsf:zhengzhou-jlsc | abstract | Central Theater JLSC and strategic reserve, register-only | - | none | 0 units | R02:44, R02:59 |

**Support.** All not established.

**Connections.** chn_jlsf_wuhan_base: subordinate (source, R02:44). Central Theater Command, strategic reserve (source, R02:59; no world node).

**Routine activity.** None.

**Validation.** Abstract. No mapping or placement.

---

### seasia_laos_ban_keun_airport - Ban Keun Airport (joint China-Laos aviation training centre claim)

**Identity.**
- Alias: Ban Keun.
- Operator: China and Laos (joint, as claimed).
- Host: Laos.
- Node kind: research_lead.
- Policy: **do_not_populate** (plan:44).

**SOURCE CLAIM.**
- China and Laos 'have opened a joint military aviation training centre at Ban Keun Airport' (R01:37).
- 'While designated as a training facility', it is described as a new logistical and operational foothold for Chinese air assets beyond the south-western border (R01:37).
- It appears under the heading 'The JLSF and Southeast Asian Expansion' (R01:33).
- Only R01 mentions it.

**CHECK.**
- Priority check on the training claim (seed:23).
- The claim is undated, and 'foothold' is interpretive.
- Sharing a heading with the JLSF is not a stated JLSF role or relationship.
- No assets, units or activity are named.
- Do not populate an operational combat base on this claim alone (plan:44).

**Role.** Research lead only.

**Position.**
- Vientiane Province, Laos. The location is not given by R01; public approximate 18.4N 102.6E. Approx, verify the exact airfield.
- In-game evidence: none.
  - Nearest proven placement about 215 NM (air: wp_mig-17 at 17.65N 106.29E, stock NATO/Dong Hoi.ini:294); land and sea about 225 NM (Dong Hoi user copy).
  - Nearest world-data point: Hanoi, about 241 NM.
- Landlocked.

**Forces.** None. The IPS mapping for 'Ban Keun' is outcome none ('research lead only').

**Support.** None.

**Connections.** None, sourced or authored.

**Routine activity.** None.

**Validation.**
- Research: unresolved claim.
- Mapping: none.
- Placement: none.
- Missing:
  - no Laos nation key or flag anywhere in the collection (grep of all variant and squadron files and the flag table);
  - claim status and date unverified.
