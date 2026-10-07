<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Chinese maritime and naval air bases (Hainan, Zhejiang)

### Region summary

- **Nodes, in register order:**
  - On Hainan (Southern Theater, South China Sea): Yulin, Longpo, Lingshui.
  - In Zhejiang (Eastern Theater, East China Sea and Taiwan Strait): Ningbo.
- **SOURCE CLAIM.** R01:31, R03:97-107, R03:168, R03:172 and R02:48 describe:
  - roles;
  - platform families;
  - named formations.

  They give no hulls, numbers, dates or coordinates, and no classes except the Lingshui aircraft types. R01:31 repeats R03:99, R03:101 and R03:105 almost word for word. Repetition is not corroboration.
- **SCENARIO CHOICE (every quantity below is our proposal):**
  - 22 placed hulls: 7 at Yulin, the 4-ship carrier group homed on Longpo, and 11 at Ningbo.
  - 8 land-based aircraft at Lingshui, plus the carrier's own embarked wing.
  - 6 labelled shore stand-ins: 5 piers and 1 airfield.
  - 4 abstract entries: the Yulin marine SOF elements, the Longpo strategic submarine force (bare fact only), Eastern Theater naval aviation, and its shore radar brigades.

  These allocations do not reproduce any real deployment.
- **Collection.**
  - PLAN combatant and submarine families map exactly, mostly to Modern PLAN Systems custom models.
  - The Type 901 and Type 903A suppliers are labelled stand-ins on donor meshes. They are recorded as proxy, following the installations-lens correction.
  - No named Chinese base unit exists. Piers are RE-power PT-boat docks placed with Nation=china and a NameOverride (proxy).
  - Lingshui is a labelled Chinese airbase with a curated CustomAirGroup (proxy). A named Lingshui unit is missing_fit until a SEST named clone is authored on the integration/raaf-bases pattern.
- **Support.**
  - Finite afloat ship-ammunition supply is evidenced: the [SupplySystem1] blocks on the Type 901 and Type 903A.
  - The RE-power piers have effectively unlimited stock. They must be disclosed as an abstraction or replaced by a finite clone.
  - Not established: fuel transfer, repair, supplier restocking.
  - Untested: aircraft turnaround and base ordnance stock.
- **Positions.** All are approximate public locations, labelled 'approx, verify'.
  - Stock missions prove land about 6-9 NM from the two Hainan naval bases (nearest: about 6 NM from Longpo, about 9 NM from Yulin) and an airborne point 5 NM from Lingshui. Nothing has been placed within about 80 NM of Ningbo.
  - My scratch scan of every repo mission found no sea placement within about 108 NM of Hainan or 200 NM of Ningbo.
  - The only committed coast extract covers 100-180E / 25-72S, which excludes both areas. Placement therefore needs a new tools/make_coast_extract.py box or the global-land-mask tools (fix_land_positions.py, sea_routes.py).
  - All four nodes sit well inside the engine extent already proven. From a 42N 20E centre, |x| is about 5,400-6,100 and |z| about 700-1,430 file units. They are far from the date line.
  - Absolute GeoPosition placement also exists (MFI:436-440).
- **World-level identity.**
  - One carrier is allocated here: Fujian, plan_cv_type_003 Variant1. Liaoning and any relabelled 'Shandong (Type 001 stand-in)' are not allocated in this region.
  - **Hull pins (SCENARIO CHOICE).** Every placed hull is pinned to one VariantReference. Hull names come from the language_en/vessel_names.ini that defines each unit in load order, re-resolved on 2026-10-07. No other region may place a pinned hull.
    - Yulin: plan_ss_type_039b Variant1 'Changcheng334' and Variant2 'Changcheng335'; plan_ss_type_039a Variant1 'Changcheng330'; plan_type_056a Variant1 'Huangshi (502)' and Variant2 'Qinhuangdao (505)'; plan_type_054a_p5 Variant1 'Ziyang (522)'; plan_aor_type903a Variant1 '889 CNS Taihu'.
    - Longpo carrier group: plan_cv_type_003 Variant1 'PLANS Fujian CV18'; plan_type_055_2026 Variant1 'Nanchang (101)'; plan_type_052d_p3 Variant1 'Zibo (156)'; plan_aor_type901 Variant1 '965 CNS Hulunhu'.
    - Ningbo: plan_ddg_type956e_early Variant1 'Hangzhou DDG-136'; plan_type_052d_p4 Variant1 'Dazhou (135)'; plan_type_052d_p1 Variant1 'Kunming (172)'; plan_type_054a_p3 Variant1 'Daqin (576)'; plan_type_054_p2 Variant1 'Maanshan (525)'; plan_ptg_type037IIE Variant1 'Yangjiang PTG-770' and Variant2 "Shunde' PTG-771"; plan_ss_type_039 Variant1 'PLAN Changcheng 320'; plan_ss_type_039b Variant3 'Changcheng336'; plan_ss_kilo Variant1 'Yuan Zheng 64 Hao' (364); plan_aor_type903a Variant2 '890 CNS Chaohu'.
    - The pins say nothing about where the real ships are based.
  - **Left free for other regions.**
    - Two of the four named Type 903A hulls are used here. Variant3 (963 Honghu) and Variant4 (964 Luomahu) stay free for the Djibouti escort group, or for a separately allocated Type 904 stand-in. The inventory says that stand-in must not be double-counted as one of the named 903A hulls.
    - One of the two Type 901 hulls is used here. Variant2 (967 Chaganhu) stays free.
    - The Djibouti frigate and destroyer in the gulf-horn package are still provisional picks. They must come from plan_type_054a_p5 Variants 2-10 and plan_type_052d_p3 Variants 2-8 or 10-12.
  - **A pin binds the physical ship, not just the unit id.** The same hulls recur in duplicate unit files, and none of those may place them elsewhere:
    - Fujian: plan_cv_fujian, plan_cv_fujian_rsa;
    - Nanchang (101): plan_type_055_2020, plan_ddg_type_055_rsa, plan_ddg_type_055_late_rsa;
    - Zibo (156) and Kunming (172): plan_ddg_type_052D_rsa;
    - Dazhou (135): plan_ddg_type_052D_rsa Variant28, spelt 'Dazhou DDG-157' in RSA (the pennant differs between mods);
    - Hangzhou (136): plan_ddg_type956e, plan_em_sovremenny;
    - Ziyang (522) and Daqin (576), spelt 'Daqing FFG-576' in RSA: plan_ffg_type_054a_rsa, plan_ffg_type_054a_late_rsa; 576 also appears on the fictional plan_ffg_krivak2;
    - Maanshan (525): plan_type_054_p1.
  - **Ship names that match place names.** These hulls are ships, not these nodes or the JLSF centres. None of them is used here:
    - 'Yulin (569)' and 'Sanya (574)': plan_type_054a_p2 Variant1 and Variant11;
    - 'Yulin FFG-569' and 'Sanya FFG-574': the RSA kitbash plan_ffg_type_054a_rsa and plan_ffg_type_054a_late_rsa, Variant6 and Variant16 (mods-source/3413868677/language_en/vessel_names.ini:1289, 1299, 1334, 1344);
    - 'Yulin FFG-569': the fictional Type 1135E plan_ffg_krivak2 Variant5 (same file :1384);
    - 'Ningbo DDG-139': plan_ddg_type956e_early and plan_ddg_type956e, Variant4;
    - 'Ningbo 956EM': plan_em_sovremenny Variant4 (3417801942);
    - 'Wuxi (104)': Type 055 Variant4;
    - 'Guilin (164)': 052D Phase 3 Variant9;
    - 'Xining (117)': 052D Phase 1 Variant5.

---

### chn_hainan_yulin_naval_base - Yulin Naval Base

**Identity**
- Operator: PLA Navy. Host: China.
- Location: Hainan, 'eastern suburbs of Sanya' (R03:99).
- node_kind: naval_base. Policy: populate.
- Theatre: Southern Theater Command (R03:97). This is added per the fidelity missing-claim note.

**Role: SOURCE CLAIM**
- **R01:31, R03:99:** a 'heavily fortified' base for conventional diesel-electric submarines and smaller surface combatants. R03:99 adds 'elements of the PLAN Marine Corps Special Operations Brigade'.
- **R03:97:** the Southern Theater Command holds the South China Sea, the South Sea Fleet HQ is in Guangdong, and Hainan is the 'operational spear tip'. R01:31 and R03:99 call it the 'epicenter'.
- **R02:48:** the Guilin and Wuxi centres would feed fuel and munitions to Yulin, Longpo and Ningbo. They are named jointly, with no per-base pairing.
- **R03:168:** the submarine fleet operating out of Yulin and Longpo faces an allied sensor curtain.
- **R03:172 (simulation guidance):** harassing logistical shipping with conventional diesel-electric submarines from Yulin could starve forward-deployed forces of fuel and munitions.
  - Fidelity fix: R03:172 names Diego Garcia and Guam and the United States forces they support. It does not say the harassed logistical shipping is US. Reading the targets as shipping that supplies those forces is contextual.
- **Our label:** naval support for conventional submarines and light surface ships.

**Position**
- Approx 18.2N 109.6E (Yulin Bay, east Sanya). Approx, verify.
- Evidence:
  - stock `missions/PLAN/PLAN 02 Battle of the South China Sea.ini:506-517` (line numbers from the copy in mods-source/_vanilla/original) places [NeutralLandUnit1] airfield_small_1 with Nation=china at 18.29,109.43. That is land, about 11 NM WNW, near Sanya airport. Its NameOverride 'Sanya Airbase' (:38-39) is a stock precedent for Nation=china. The user copy (NEW MISSIONS CLEAN/PLAN) has the same block at :475-486;
  - stock `campaigns/pacific-strike-task-force/missions/10 Vengeance at Luzon.ini:1099-1106` places wp_airbase_4 at 18.30,109.72. That is land, about 9 NM NE, and the nearest land placement;
  - the nearest sea placement is about 110 NM S (civ_ms_poltava, original PLAN 02 :409-414);
  - there is no Hainan entry in asia_ports.ini or airports.ini.
- Placement is pending validation.

**Forces (all SCENARIO CHOICE unless marked SOURCE)**

| Asset | Allocation | Role | Unit id | Outcome | Qty | Source basis |
|---|---|---|---|---|---|---|
| asset:chn:yulin_pier | support | Surface-ship resupply pier, NameOverride 'Yulin naval base (stand-in pier)', Nation=china | nv_pt_boats_docks | proxy | 1 | SOURCE: base exists (R03:99). The mesh is a Vietnamese PT-boat dock |
| asset:chn:yulin_sub_pier | support | Submarine resupply pier, labelled stand-in | nv_pt_boats_docks_small | proxy | 1 | SOURCE: SSK base (R01:31, R03:99) |
| asset:chn:yulin_ssk_1 | resident_at_base | SSK alongside | plan_ss_type_039b (Variant1 'Changcheng334') | exact | 1 | SOURCE: SSK family only (R01:31, R03:99). SCENARIO: Type 039B |
| asset:chn:yulin_ssk_2 | patrol | SSK patrol box south of Hainan | plan_ss_type_039b (Variant2 'Changcheng335') | exact | 1 | As above |
| asset:chn:yulin_ssk_3 | servicing_maintenance | SSK in maintenance at the pier | plan_ss_type_039a (Variant1 'Changcheng330') | exact | 1 | As above |
| asset:chn:yulin_corvette_1 | patrol | Coastal patrol on the Sanya-Lingshui approaches | plan_type_056a (Variant1 'Huangshi (502)') | exact | 1 | SOURCE: 'smaller surface combatants' (R01:31, R03:99). SCENARIO: Type 056A |
| asset:chn:yulin_corvette_2 | escort | Escorts the Guilin JLSF relief run (asset:chn-jlsf:guilin-mob-cargo-1, china-support) from t0; not in the Yulin base count | plan_type_056a (Variant2 'Qinhuangdao (505)') | exact | 1 | As above. SCENARIO: escort allocation per world integration C14/C24 |
| asset:chn:yulin_ffg_1 | escort | Escorts yulin_aor_1 | plan_type_054a_p5 (Variant1 'Ziyang (522)') | exact | 1 | As above. SCENARIO: Type 054A Phase 5 |
| asset:chn:yulin_aor_1 | support | Afloat ammunition shuttle for the Yulin patrols | plan_aor_type903a (Variant1 '889 CNS Taihu') | proxy (labelled '(stand-in)') | 1 | SOURCE: none at Yulin. R02:48 is shore logistics |
| asset:chn:yulin_marine_sof | abstract | PLAN Marine Corps SOF elements | none | none | - | SOURCE: R03:99. No unit is labelled marine or SOF. Generic PLA vehicles resolve (pla_lt_type_63, described as an amphibious light tank; pla_td_ztl-11; pla_apc_zbl-08; the army IFV pla_ifv_zbd-04a), but they do not represent SOF elements. Kept abstract |

Hull variants are pinned (see World-level identity). 039B has 14 Changcheng hulls (334-347, Variant1-14) and 039A has 4 (330-333). The 056A has 6 named hulls and the 054A Phase 5 has 10.

**Support services**
- **Shore ship ammunition: yulin_pier.**
  - nv_pt_boats_docks [SupplySystem1] TruckSupplySystem.
  - TargetTypes=Vessel; AmmoCapacity 9,999,999,999; AmmoLoadSpeed 9,999,999; no MaxAmmoPoints; 3 NM; 6 receivers; own speed 5 kn or less, receiver 10 kn or less; no accountable categories.
- **Shore submarine ammunition: yulin_sub_pier.** nv_pt_boats_docks_small has the same block with TargetTypes=Submarine.
- **Limits of both piers.**
  - Their stock is effectively unlimited, which conflicts with the finite-supply rule. Either disclose them as an abstraction of the R02:48 feed, or author a finite clone.
  - They serve whichever side owns them.
  - The Nation override and supply to China-flagged receivers are untested.
- **Afloat ship ammunition: yulin_aor_1.**
  - plan_aor_type903a [SupplySystem1] TruckSupplySystem.
  - Pool 220,000; MaxAmmoPoints 5,000, which refuses YJ-12A (8,000) and passes YJ-18 and HHQ-16 per the file comment.
  - 80 pts/s; 0.6 NM; 2 receivers; own speed 13 kn or less, receiver 16 kn or less; Vessel,Submarine.
  - Categories: AirTorpedo 32, SovietAdvancedASM 8, SEST_LandAttack 16, SEST_LongRangeSAM 24.
  - Unarmed.
- **Metering.** These rounds have no AmmoPoints, so their resupply is unmetered: plan_yu-7c_ship on the 054A Phase 5 and 056A; plan_hq-16c on the 054A Phase 5; plan_yu-6a (Default and Late loadouts) and plan_yu-6 and plan_yu-9 (Early loadout) on the 039B; plan_yu-6 and plan_yu-9 on the 039A.
- **Aircraft turnaround:** none at this node. The 054A embarks one helicopter; its deck stock is untested.
- **Supplier restocking** (903A pool refilled at the pier): not established.
- **Fuel:** not established.
- **Repair:** not established.

**Connections**
- **Source:**
  - Lingshui, operating in tandem (R01:31, R03:101).
  - Longpo, the neighbouring base further east on Yalong Bay (R03:99).
  - Guilin and Wuxi JLSCs, the joint fuel and munitions feed (R02:48).
  - Sea lines of communication to Diego Garcia and Guam: SSK interdiction threat to logistical shipping (R03:172 simulation guidance). Which shipping is targeted is contextual.
  - Kanoya and Atsugi: the opposing ASW sensor curtain (R03:168).
- **Authored:**
  - Guilin as the primary pairing, inferred from theatre alignment (R02:44, R02:56).
  - South China Sea patrol boxes (context R03:97).
  - A Yulin-Ningbo transfer route. Its geometry is unvalidated.
  - An optional escort or transit deployment to hoa_djibouti_pla_support_base. No source links Hainan to Djibouti.

**Routine activity (PROPOSED, not implemented)**
- yulin_ssk_2 patrols a box south of Hainan, rotating with yulin_ssk_1. Arrivals and departures happen at the pier.
- yulin_corvette_1 runs a loop: Sanya, Yalong Bay, then off Lingshui.
- yulin_aor_1 and yulin_ffg_1 run a shuttle: they leave Yulin, meet the patrol units, and return to the pier.
- yulin_corvette_2 sails from t0 as the escort of asset:chn-jlsf:guilin-mob-cargo-1 on the Guilin relief run (china-support) and is not in the Yulin base count (SCENARIO CHOICE, world integration C14/C24). For the later roro-2 release (asset:chn-jlsf:guilin-mob-roro-2), the escort is another Yulin hull at base at release time, never yulin_corvette_2; it leaves the Yulin base count when it sails. One allocation at a time. No separate relief-escort slot is created; the ids proposed for one are withdrawn (C24).
- **Neutral traffic:**
  - Vietnamese fishing, civ_fv_sampan. Exact, Vietnam flag.
  - Chinese fishing, civ_fv_fishingboat_a Variant5 'Fishing boat China' with a per-unit Nation=china. Proxy: the variant flag is US, and whether the override changes the flag is untested.
  - Merchants on South China Sea lanes: civ_ms_bulk, civ_ms_ritina, civ_ms_car_carrier_a.
  - Civil air on authored airways into Sanya: civ_a330 with China, Hong_Kong and Taiwan liveries.
  - Avoid the RE-power cargo hulls (civ_ms_freighter_b/d, civ_ms_poltava, civ_ms_amra) until neutral-supplier behaviour has been tested. Each carries a live supply block:
    - very large but finite pools: 12,000,000 AP, or 4,800,000 on civ_ms_poltava;
    - no MaxAmmoPoints ceiling;
    - near-instant transfer (9,999,999 AP/s);
    - 1.5 NM range, Vessel targets.
  - CivilianRoute respawns need a bounded MaxUnits.

**Checks**
- Exact resident assignments are unknown (plan:35). The classes, hulls and numbers above are ours.
- 'Heavily fortified' names no systems, so no defences are placed.
- R03:172 names the United States forces at Diego Garcia and Guam but does not say the harassed shipping is US. Reading the targets that way is contextual.
- Theatre context from R03:97 is added.
- The class choice is ours. Song and Kilo would be equally defensible.
- The 903A ceiling of 5,000 limits which escort rounds it can supply.
- The 'dense curtain' wording (R03:168) gives no perfect-detection rule.

**Gaps**
- No named PLAN base or Port unit, so both piers are proxies.
- No submarine tender (Type 926).
- No PLAN marine unit.
- No CCG or maritime-militia hull. No Chinese merchant flag.
- No proven sea point near the base, and no coast extract.
- Fuel, repair and restocking are not established.

**Validation**
- Research: families only.
- Mapping: all ids re-resolved through winning_file on 2026-10-07.
- Placement: pending.
- Runtime activation and save/load: not tested.

---

### chn_hainan_longpo_naval_base - Longpo Naval Base

**Identity**
- Operator: PLA Navy.
- Location: Hainan, 'further east on Yalong Bay'. Formerly Yulin-East. A deep-water facility (R03:99).
- node_kind: naval_base. Policy: populate_small.
- Fidelity fix: the Yulin-East alias is Longpo's. Yulin is the base in eastern Sanya.

**Role: SOURCE CLAIM**
- **R03:99:** the primary harbour of the PLAN's strategic (ballistic-missile) submarine force. **R01:31:** the Longpo pens exist to protect China's ballistic-missile submarine fleet. Both are recorded as bare facts only. The reports describe underground pens; their layout is not modelled.
- **R03:99:** 'increasingly outfitted to support China's expanding fleet of aircraft carriers'. No carrier is named.
- **R03:97 (context):** the South China Sea is described as a bastion for the nuclear submarine fleet.
- **Other links:** R02:48 (feed), R03:168 (ASW curtain), R01:31 and R03:101 (Lingshui in tandem).
- **Not carried forward:** the 'protect from preemptive strikes' wording does not justify an invulnerability or sanctuary rule.
- **Our label:** naval support for an authored carrier group; the strategic force is context only.

**Position**
- Approx 18.2N 109.7E (Yalong Bay, east of Yulin). Approx, verify.
- Evidence:
  - wp_airbase_4 at 18.30,109.72 (`10 Vengeance at Luzon.ini:1099-1106`): land, about 6 NM. It is a Taskforce2 airfield in a Soviet-themed stock mission, so it proves land only and is not a Chinese base.
  - pla_h-6d airborne at 18.34,109.73 in the same mission: about 8 NM.
  - The nearest sea placement is about 108 NM.

**Forces**

| Asset | Allocation | Role | Unit id | Outcome | Qty | Source basis |
|---|---|---|---|---|---|---|
| asset:chn:longpo_pier | support | Carrier-group resupply pier, 'Longpo naval base (carrier-support pier stand-in)' | nv_pt_boats_docks | proxy | 1 | SOURCE: carrier support being added (R03:99) |
| asset:chn:scs_cv_1 | underway_deployed | South China Sea carrier group, homed on Longpo, not at the pier at start | plan_cv_type_003 (Variant1 'PLANS Fujian CV18') | exact | 1 | SOURCE: no carrier named (R03:99; register backlog). SCENARIO: Fujian |
| asset:chn:scs_cvg_ddg_1 | escort | Carrier air-defence escort | plan_type_055_2026 (Variant1 'Nanchang (101)') | exact | 1 | SOURCE: none. Not Variant4 'Wuxi (104)' (name collision) |
| asset:chn:scs_cvg_ddg_2 | escort | Carrier escort | plan_type_052d_p3 (Variant1 'Zibo (156)') | exact | 1 | SOURCE: none. Not Variant9 'Guilin (164)' (name collision) |
| asset:chn:scs_cvg_aoe_1 | support | Accompanying fast combat support ship | plan_aor_type901 (Variant1 '965 CNS Hulunhu') | proxy (labelled stand-in) | 1 | SOURCE: none |
| asset:chn:longpo_ssbn_force | abstract | Strategic submarine force, bare fact | plan_ssbn_type_094a (not placed) | missing_fit | 0 placed | SOURCE: R01:31, R03:99. The unit carries a strategic-missile magazine and has no context-only fit, so it is not placed (as with Ile Longue) |

**The embarked wing** belongs to scs_cv_1 only and never also appears at Lingshui.
- Unit default: J-35 x16, J-15T x30, J-15DT x4, KJ-600 x4, plus Z-18JA/FA/Y and Z-9D helicopters.
- These are unit-file figures, not source figures.
- SCENARIO: trim the wing with a mission-level CustomAirGroup. This is the documented mechanism:
  - MFI:401-409 describes it as a 'Complete replace of aircraft on board' for airbases, carriers and escorts;
  - stock missions use it on vessels (`Showdown off Guam Blue 1985.ini:118`; `01A Senkaku Run.ini:97`);
  - runtime spawning and capacity on this hull are untested.

**Support services**
- **Afloat ship ammunition: scs_cvg_aoe_1.**
  - plan_aor_type901 [SupplySystem1] TruckSupplySystem.
  - Pool 400,000; MaxAmmoPoints 9,000, which admits YJ-18, YJ-12A and YJ-19 and blocks YJ-20.
  - 110 pts/s; 0.8 NM; 2 receivers; own speed 13 kn or less, receiver 16 kn or less; Vessel,Submarine.
  - Categories: AirTorpedo 40, SovietAdvancedASM 12, SEST_LandAttack 32, SEST_LongRangeSAM 32.
  - Armed: Type 730, and HQ-10 fired from the Mk29.
- **Shore ship ammunition: longpo_pier.** Same block as at Yulin (Vessel, effectively unlimited). Disclose it.
- **Aircraft turnaround and ordnance: scs_cv_1.**
  - FlightDeck_AmmoCapacity 1,200,000 (finite).
  - Its plan_f3200a magazine is a Count=0 placeholder that resolves nowhere.
  - Recovery and repeat sorties are untested.
- **Flight-deck restock:** not established.
- **Fuel:** not established.
- **Repair:** not established.
- **SSBN support:** none modelled.

**Connections**
- **Source:**
  - Yulin as neighbour (R03:99).
  - Lingshui in tandem (R01:31, R03:101).
  - Guilin and Wuxi feed (R02:48).
  - Yalong Bay as its location (R03:99).
  - Kanoya and Atsugi ASW curtain (R03:168).
- **Authored:** the carrier group's operating area in the northern South China Sea (context R03:97, 'operating space for its expanding surface fleet').

**Routine activity (PROPOSED)**
- The carrier group works an exercise box in the northern South China Sea, flying flight operations.
- It meets scs_cvg_aoe_1 for replenishment.
- It returns to Longpo periodically.
- No strategic submarine patrol is modelled.

**Checks**
- Which carrier facilities are at Longpo, as against Yulin or Sanya? No carrier is named.
- Outside R01-R03, public reporting links Shandong (and reportedly Fujian) to Sanya. This is not used as evidence.
- No SSBN numbers or nuclear specifics are given.
- Changcheng 25-28 is the hull name on 094, 094A and 096 alike. Use one Jin unit per world, or NameOverride the hulls.
- Use Liaoning (plan_type_001) as a Shandong stand-in only with a NameOverride, and only with Variant3 or Default in a current-dated world.
- Fidelity fix: add R01:31 to the Lingshui tandem link.

**Gaps**
- No pen or tunnel model, and none is wanted.
- No context-only fit for an SSBN.
- No carrier-specific shore facility.
- No Type 075 or Type 076.
- Flight-deck restock is not established.

**Validation:** as for Yulin. Placement pending; runtime not tested.

---

### chn_hainan_lingshui_airbase - Lingshui Airbase

**Identity**
- Location: Lingshui Li Autonomous County, Hainan (R03:101).
- node_kind: naval_air_station. Policy: populate.
- **Operator: CHECK.** The operating service is not stated.
  - R03:101 calls Lingshui a 'naval air station' that gives land-based air cover to the PLAN fleet.
  - The R03:133 type table lists the Y-8Q operator as China (PLAN). That is a type-level statement, not a base assignment. Fidelity fix: R03:133 is removed as basing evidence.

**Role: SOURCE CLAIM**
- **R01:31:** hosts J-15 carrier-capable fighters and Y-8Q MPA, and operates in tandem with the naval bases.
- **R03:101:**
  - hosts J-15, KJ-500 AEW and the ASW-optimised Y-8Q;
  - extensive upgrades;
  - within striking distance of disputed outposts;
  - a dual role: air cover for the PLAN fleet, and ISR tracking foreign naval assets such as US carrier strike groups.
- **R03:168:** J-15s and Y-8Qs from Lingshui form a counter-screen to the allied ASW effort.
- **Our label:** naval aviation (fighter, AEW, MPA/ASW).

**Position**
- Approx 18.5N 110.0E. Approx, verify.
- Evidence:
  - stock `missions/PLAN/PLAN 01 Clash in the Paracels.ini:299-304` places pla_q-5 airborne at 3,000 at 18.41,110.00, about 5 NM away. That is an air position, not proof of a runway.
  - The nearest land placement is about 20 NM away (wp_airbase_4).
  - There is no airports.ini entry.

**Forces**

| Asset | Allocation | Role | Unit id | Outcome | Qty | Source basis |
|---|---|---|---|---|---|---|
| asset:chn:lingshui_airbase | support | Airfield, NameOverride 'Lingshui Airbase (stand-in)', mission CustomAirGroup=True listing only the aircraft below and replacing Variant2's own group | china_large_airbase (VariantReference=Variant2 'PLAN Airbase') | proxy | 1 | SOURCE: base (R03:101). A named unit is missing_fit. Alternative: pla_airbase_modern Default variant |
| asset:chn:lingshui_j15_x4 | resident_at_base | Land-based air cover and CAP | plan_j-15 (Default squadron) | exact | 4 | SOURCE: J-15 (R01:31, R03:101, R03:168), no number |
| asset:chn:lingshui_kj500_x2 | resident_at_base | AEW and ISR | plaaf_kj-500 (Squadron2 'KJ-500 (PLANAF)') | exact | 2 | SOURCE: KJ-500 (R03:101) |
| asset:chn:lingshui_y8q_x2 | resident_at_base | ASW/MPA counter-screen | plan_y-8fq | exact | 2 | SOURCE: Y-8Q (R01:31, R03:101, R03:168). The equivalence of Y-8Q and Y-8FQ/KQ-200 needs a check |

**Support services**
- **Aircraft turnaround and ordnance.**
  - china_large_airbase has FlightDeck_AmmoCapacity 3,000,000, a finite pool.
  - pla_airbase_modern declares no FlightDeck_AmmoCapacity, so it would fall back to the undocumented engine default.
  - A per-mission FlightDeck_ override is possible.
  - Recovery, turnaround and repeat sorties are untested.
- **Ship ammunition:** none.
- **Air refuelling:** none sourced and none proposed. plaaf_yy-20a and plaaf_y-20b exist, but nothing places them here.
- **Base ordnance restock:** not established.
- **Aircraft repair:** not established.

**Connections**
- **Source:**
  - Yulin and Longpo in tandem (R01:31, R03:101).
  - South China Sea ISR (R03:101).
  - Disputed outposts within striking distance; none are named (R03:101).
  - Counter-screen against Kanoya and Atsugi (R03:168). This is the mirror relationship the fidelity check asked for.
- **Authored:**
  - Air cover for asset:chn:scs_cv_1. The role is in R03:101; the pairing with this group is ours.
  - An opposing overlap with Andersen and Guam (R03:38 dispatches to the South China Sea; R03:101 tracks US CSGs).

**Routine activity (PROPOSED)**
- A Y-8FQ sweeps the approaches to Hainan for ASW.
- A KJ-500 flies an AEW orbit over the northern South China Sea.
- J-15 pairs fly CAP over the carrier group or the Hainan approaches.
- All three recover at Lingshui.
- Civil air on authored airways nearby: civ_a330 and civ_a380 with China liveries.
- Note: aircraft orbit when their waypoints end, and editor round-trips reset Hold/Tight weapon status to Free.

**Checks**
- Assignments are a priority check. No units, numbers or dates are given.
- Use the Default squadron. The 8th and 10th Aviation Brigade squadrons are not verified for Lingshui.
- No defences are sourced.
- The chosen Variant2 'PLAN Airbase' has its own CustomAirGroup=True (china_large_airbase_variants.ini [Variant2]):
  - its aircraft are plan_j9, plaaf_j8j, plan_j7k, plaaf_j5 Squadron5, plaaf_h6k, plaaf_jh_6/6a, KJ-100A/B, KQ-100 and Ka-28, and none of them is a sourced Lingshui type (J-15, KJ-500, Y-8Q);
  - plaaf_j5 Squadron5 does not resolve, because the squadrons file holds only Default and Squadron1;
  - Squadron2-4 are requested only by Default and Variant1;
  - so the mission CustomAirGroup must replace Variant2's group.
- That mechanism is documented: MFI:401-409 calls it a 'Complete replace of aircraft on board' for airbases. Runtime spawning and capacity are untested.

**Gaps**
- A named Lingshui unit (missing_fit). The fix is a SEST named clone on the raaf-bases pattern; its id will be assigned when it is authored.
- No PLANAF livery on the Y-8FQ.
- No KJ-200.
- No Chinese UAVs.
- Aircraft turnaround is untested.

**Validation:** as above.

---

### chn_zhejiang_ningbo_naval_base - Ningbo Naval Base

**Identity**
- Operator: PLA Navy (Eastern Theater Command Navy).
- Location: coast of Zhejiang. Established 1955 (R03:105).
- node_kind: naval_base. Policy: populate.

**Role: SOURCE CLAIM**
- **R03:105:**
  - HQ of the ETC Navy, formerly the East Sea Fleet;
  - a 'massive concentration' of surface and subsurface combatants;
  - resident units: the 3rd and 6th Destroyer Zhidui, 8th Frigate Dadui, 21st Fastboat Zhidui, and 22nd and 42nd Submarine Zhidui.
- **R01:31:** says the ETC itself has its HQ at Ningbo, which conflicts with R03 (see Checks).
- **R03:107:**
  - naval aviation under the command umbrella: the 4th and 6th Air Divisions and the 1st Flying Panther Regiment;
  - shore-based radar brigades;
  - no locations are given for either.
- **R03:107 (simulation guidance):** amphibious and blockade force generation, saturation missile attacks and submarine ambushes. This is guidance, not a placement or a rule.
- **Posture:** a Taiwan contingency (R01:31, R03:105); control of the East China Sea (R03:105).
- **R02:48:** the joint Guilin and Wuxi feed.
- **Our label:** naval support plus command. The HQ is abstract.

**Position**
- Approx 29.9N 121.7E on the Ningbo coast. Anchorages may extend to Zhoushan, about 30.0N 122.1E. Approx, verify.
- Evidence:
  - stock `pacific-strike-task-force/missions/01 Raid on Okinawa.ini:401-408` places airfield_small_1 Variant3 (PLAAF) at 28.54,121.42: land, about 80-88 NM S;
  - asia_ports.ini:7-9 holds the world-data port [Shanghai] at 31.2304,121.4737 with Nation=China, about 80 NM N;
  - the nearest sea placement is about 200 NM away.

**Forces (formation-to-family mapping; no hull lists are implied)**

| Asset | Allocation | Role | Unit id | Outcome | Qty | Source basis |
|---|---|---|---|---|---|---|
| asset:chn:ningbo_pier | support | Surface-ship resupply pier, labelled stand-in | nv_pt_boats_docks | proxy | 1 | SOURCE: base (R03:105) |
| asset:chn:ningbo_sub_pier | support | Submarine resupply pier, labelled stand-in | nv_pt_boats_docks_small | proxy | 1 | SOURCE: Submarine Zhidui (R03:105) |
| asset:chn:ningbo_ddg_1 | resident_at_base | Destroyer alongside | plan_ddg_type956e_early (Variant1 'Hangzhou DDG-136') | exact | 1 | SOURCE: Destroyer Zhidui family (R03:105). SCENARIO: Type 956E. Not Variant4 'Ningbo DDG-139' (name collision) |
| asset:chn:ningbo_ddg_2 | patrol | East China Sea destroyer patrol | plan_type_052d_p4 (Variant1 'Dazhou (135)') | exact | 1 | As above. SCENARIO: 052D |
| asset:chn:ningbo_ddg_3 | reserve | Dormant at the pier (Disabled=True), woken once by trigger | plan_type_052d_p1 (Variant1 'Kunming (172)'; not Variant5 'Xining (117)') | exact | 1 | As above |
| asset:chn:ningbo_ffg_1 | escort | Escorts the Wuxi JLSF relief run (asset:chn-jlsf:wuxi-mob-roro-1, china-support) from t0; not in the Ningbo base count | plan_type_054a_p3 (Variant1 'Daqin (576)') | exact | 1 | SOURCE: Frigate Dadui family (R03:105). SCENARIO: escort allocation per world integration C14/C24 |
| asset:chn:ningbo_ffg_2 | escort | Escorts ningbo_aor_1 | plan_type_054_p2 (Variant1 'Maanshan (525)') | exact | 1 | As above. SCENARIO: Type 054 |
| asset:chn:ningbo_fac_x2 | patrol | Coastal fast-boat patrol, labelled 'fast attack craft (Type 037IIE stand-in for Type 022)' | plan_ptg_type037IIE (Variant1 'Yangjiang PTG-770', Variant2 "Shunde' PTG-771") | proxy | 2 | SOURCE: Fastboat Zhidui (R03:105). The modern Type 022 has no unit |
| asset:chn:ningbo_ssk_1 | resident_at_base | SSK alongside | plan_ss_type_039 (Song; Variant1 'PLAN Changcheng 320') | exact | 1 | SOURCE: Submarine Zhidui, type unstated (R03:105). SCENARIO: conventional |
| asset:chn:ningbo_ssk_2 | patrol | East China Sea SSK patrol | plan_ss_type_039b (Variant3 'Changcheng336') | exact | 1 | As above |
| asset:chn:ningbo_ssk_3 | servicing_maintenance | SSK in maintenance | plan_ss_kilo (Variant1 'Yuan Zheng 64 Hao', hull 364) | exact (877EKM only) | 1 | As above |
| asset:chn:ningbo_aor_1 | support | Afloat ammunition shuttle | plan_aor_type903a (Variant2 '890 CNS Chaohu') | proxy | 1 | SOURCE: none |
| asset:chn:etc_naval_aviation | abstract | 4th and 6th Air Divisions, 1st Flying Panther Regiment | none | none (source gap: no type or base) | - | SOURCE: R03:107. Candidates exist if checks confirm them: plaaf_jh7a, plaaf_kj-500 Sq2, plan_y-8fq, plaaf_j-11bh |
| asset:chn:etc_radar_brigades | abstract | Shore-based radar brigades | none | none (source gap) | - | SOURCE: R03:107. Candidate: pla_ylc-18_radar |

**Support services**
- **Shore ship and submarine ammunition:** the piers, with the same blocks and caveats as at Yulin (unlimited, disclose).
- **Afloat ship ammunition: ningbo_aor_1** (plan_aor_type903a). Same block as at Yulin.
  - The 956E's plan_3m_80mbe (Moskit) and plan_hq16 rounds declare no AmmoPoints. Their winning copies are in mods-source/3413868677/ammunition/. In data, then, MaxAmmoPoints 5,000 does not refuse them, and their resupply is unmetered or untested.
- **Metering.** These rounds have no AmmoPoints, so their resupply is unmetered: plan_3m_80mbe and plan_hq16 on the 956E; plan_yu-7c_ship on the 054A Phase 3, the 054 and the 052D Phase 1; plan_yu-6a (Default and Late loadouts) and plan_yu-6 and plan_yu-9 (Early loadout) on the 039B; pla_yj-18 and pla_yu-6 on the Song; plan_yu-5 and plan_yu-6 on the Kilo. pla_hq-11 also has no AmmoPoints, but on the 052D Phase 4 it sits only in the AntiAirHeavy loadout (plan_type_052d_p4.ini:570, :841, SEST_Integration copy), which AvailableLoadouts (:350) leaves out, so no selectable loadout carries it.
- **Aircraft:** none at this node. Aviation is abstract.
- **Supplier restocking:** not established.
- **Fuel:** not established.
- **Repair:** not established.
- **HQ:** abstract. nv_headquarters supplies only LandUnit targets and is not proposed.

**Connections**
- **Source:**
  - Guilin and Wuxi feed (R02:48).
  - The ETC naval aviation umbrella (R03:107).
  - East China Sea (R03:105).
  - Taiwan Strait (R01:31, R03:105, R03:107).
- **Authored:**
  - Wuxi as the primary pairing, inferred from theatre alignment (R02:44, R02:55). This is the fidelity fix.
  - An opposing overlap with Naha (R03:123).
  - An opposing overlap with Yokosuka (R03:59).
  - A Yulin transfer route.

**Routine activity (PROPOSED)**
- ningbo_ddg_2 and ningbo_ssk_2 patrol the East China Sea.
- ningbo_fac_x2 patrol the coastal and Zhoushan approaches.
- ningbo_aor_1 and ningbo_ffg_2 meet for replenishment.
- ningbo_ffg_1 sails from t0 as the escort of asset:chn-jlsf:wuxi-mob-roro-1 on the Wuxi relief run (china-support) and is not in the Ningbo base count (SCENARIO CHOICE, world integration C14/C24). For the later cargo-2 release (asset:chn-jlsf:wuxi-mob-cargo-2), the escort is another Ningbo hull at base at release time, never ningbo_ffg_1; it leaves the Ningbo base count when it sails. One allocation at a time. No separate relief-escort slot is created; the ids proposed for one are withdrawn (C24).
- ningbo_ddg_3 is activated once by trigger with Action_SetEnabledStatus=True. This is finite, not a respawn.
  - Vessel precedent: stock `missions/Tutorials/Officer_Training_1.ini:88` (Taskforce2Vessel2 Disabled=True), woken at :105-106.
  - Aircraft precedent: stock `missions/Campaign Scenarios/Pacific Strike/01A Senkaku Run.ini:583,720`.
- **Neutral traffic:**
  - Merchants to and from the Shanghai world-data port: civ_ms_bulk, civ_ms_car_carrier_a, civ_ms_ritina, and civ_ms_mairangi_bay (labelled as a period container ship).
  - Japanese fishing: civ_fv_fishingboat_c, civ_fv_fishingboat_d, civ_fv_sterntrawler_d.
  - Chinese fishing proxy: civ_fv_fishingboat_a Variant5.
  - Civil air: civ_a330 with China liveries.
  - Avoid the RE-power cargo hulls until neutral-supplier behaviour has been tested. As at Yulin, they carry live supply blocks with very large finite pools (12,000,000 or 4,800,000 AP), no ceiling and near-instant transfer.

**Checks**
- R01:31 says ETC HQ and R03:105 says ETC Navy HQ. The ETC HQ is usually reported at Nanjing, so R03's wording looks closer.
- The designations may predate the 2016 reorganisation, and the units may be spread across several Zhejiang anchorages.
- The aviation divisions were reportedly reorganised into brigades around 2017.
- 'Flying Panther' is the JH-7's popular name. That is our note, not the source.
- Ship names that match this node: 'Ningbo DDG-139' (Variant4 of plan_ddg_type956e_early and plan_ddg_type956e) and 'Ningbo 956EM' (plan_em_sovremenny Variant4). None of them is used.
- Untested: whether a dormant (Disabled=True) destroyer alongside a pier is present or targetable.
- Fidelity check 0 found no further place-specific claims about Ningbo.

**Gaps**
- No Type 022.
- No Kilo 636/636M (missing_fit).
- No named Ningbo base.
- No aviation base (source gap).
- No modern MCM ship. No Type 815 AGI.
- No proven position within 80 NM.

**Validation:** as above.
