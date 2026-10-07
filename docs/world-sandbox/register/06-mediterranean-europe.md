<!-- Part of the SEST world-population register. Overview: ../WORLD_POPULATION_REGISTER.md. World-level identity, connections, gaps and placement: 00-world-integration.md. -->

## Mediterranean and European support: region summary

**Sources.** Six nodes come from R03:44: Rota, Naples, Sigonella, Souda Bay, Deveselu and Redzikowo. Akrotiri comes from R01:59. The two DLA centres come from R02:23 and R02:34. Only one report mentions each node, so none of these claims is backed by a second report. R02:34 repeats R02:23 within the same report, which is not corroboration either. The register's sea areas are the 'Mediterranean' (R02:34; R03:19, R03:44) and the 'Eastern Mediterranean' (R01:59). Fidelity check part 1 found no other place-specific lines for Sigonella NAS, Akrotiri or Germersheim.

**Shape of the region (SCENARIO CHOICE).**
- Populated: Rota, Sigonella, Souda Bay and Akrotiri.
- Context only: Naples, Deveselu and Redzikowo.
- Abstract logistics: DLA Sigonella and Germersheim.

**Physical assets proposed (all small, all labelled scenario choices):**
- 4 Arleigh Burke destroyers (DDG-79, 80, 84 and 117), carrying 8 embarked MH-60R between them
- 4 P-8A
- 1 T-AKE stand-in (Variant4, T-AKE 11)
- 1 Algol-class relief sealift ship (Variant6, Regulus). It is held dormant in a world-level US sealift reserve, not under any node.
- 2 Typhoon FGR4, 1 Voyager and 1 A400M
- 1 SAR helicopter stand-in
- 3 installation stand-ins: the Sigonella, Souda and Akrotiri airfields. The functional Rota pier is an option at quantity 0.

No carrier is placed. R03's carrier table (R03:52-62) homeports none in this region. The collection inventories list 'Souda/Naples (transit)' for carriers, LCS and SSGN, but those are inventory lookup hints, not research.

**Scale and placement.**
- Every node lies about 230-1,260 NM from the scope report's candidate centre at 42N 20E. That is well inside what has already loaded, run and been saved (scope §2.2), so map extent is not a constraint here.
- No node has a named installation unit. Every base is a labelled stand-in until a named SEST clone exists (integration/raaf-bases pattern).
- Coordinates below are approximate public locations; verify each one. The builder's snapper and coast extract do not cover the Mediterranean, so water and land validation needs a new extract or the global land mask.

**Cross-region identity rules.**
- Destroyers DDG-79, 80, 84 and 117 are allocated only in this region.
- DDG-51 is held back, unallocated anywhere. Its name text may describe a past Rota tour (see the Rota CHECKS). Recheck it together with the Rota destroyer count.
- Named hulls are reserved now, so that collisions show up at review:

| Pool | Reserved here | Asset | Other claims seen at review (do not reuse) |
|---|---|---|---|
| usn_take_lewis_clark: 4 named variants, T-AKE 1, 2, 6 and 11 (SEST_Integration language_en/vessel_names.ini:188-191) | Variant4 'T-AKE 11 USNS Washington Chambers' | asset:med:take_1 | US Pacific pins Variant1 (T-AKE 1) to asset:usp:vinson_take_1. US Atlantic uses Default for asset:usatl:take_truman. The W/C Pacific and Gulf T-AKEs are unpinned; the world hull-ledger draft proposes V2 and V3 for the Atlantic and W Pacific carrier groups, and Default with unique labels for any surplus. |
| usn_takr_algol: in-date Variants 1, 3, 6 and 7 (V2/V4/V5/V8 end in 2025) | Variant6 'Regulus T-AKR-292' | asset:med:relief_sealift_1 | US Atlantic and W/C Pacific Algols are unpinned. The hull-ledger draft proposes V1 for asset:usatl:takr_norfolk_relief and V3 for asset:wpac:sealift_algol1, leaving V7 Capella free. |

**Two review items, now settled (details under each node):**
1. Precedent decodes follow the game's convention: lat = centre + z/60 and lon = centre + x/60, with no cos(lat) factor (scope §2.1). Under it the Souda precedent decodes to 35.52N 24.15E, about 1 NM from the field, and only an editor confirmation is pending. Both us-air-and-land figures (Souda 23.83E, Sigonella 14.81E) applied cos(lat), contrary to §2.1.
2. The generic pier's shore supply is effectively unlimited. The functional Rota pier is therefore an option at quantity 0 until the unlimited-supply decision is made (gameplay-and-tests.md:20, :30).

---

### med_rota_naval_station - Naval Station Rota

**Identity.** NS Rota.
- Operator: United States Navy. The name implies 'Navy'; R03:44 puts the station in its US European Command paragraph.
- Host: Spain.
- Kind: naval_base. Policy: populate.

**SOURCE CLAIMS**
- R03:44: Naval Station Rota in Spain 'serves as a critical gateway between the Atlantic and the Mediterranean'.
- R03:44: it hosts 'forward-deployed Arleigh Burke-class destroyers integrated into the NATO missile defense shield'.
- The report gives no destroyer count, no hull names, no aviation and no facilities.

**CHECKS**
- Destroyer count and hulls are not in R03. The hull picks below rest on mod-author name text in 3390330875 (language_en/vessel_names.ini):
  - DDG-84: 'current assignment with DesRon-60 out of Rota' (:448).
  - DDG-117: 'Forward Deployed to Rota' (:605).
  - DDG-80 and DDG-79: 'SeaRam Installed when transferred to DesRon-60 in Rota' (:425, :413). This wording does not state a current assignment either.

  That is collection evidence, not research, and not corroboration. Verify the forward-deployed hulls and their number at the scenario date.
- Former Rota hulls are excluded:
  - The 075_late text (DDG-75 and 78) says the SeaRAM was 'retained after their return stateside' (:397).
  - The 064_late text (DDG-64 and 71) says they 'retain the aft SeaRAM mount from their time with DESRON-60' (:354).
- DDG-51 is ambiguous. Its 051_late text reads 'After assignment to DesRon 60 out of Rota, Spain. SeaRam Installed' (:255). That does not say the ship is at Rota now and may describe a former Rota hull, so DDG-51 is held unallocated. DDG-79, whose wording matches DDG-80's, takes the reserve slot.
- Missile defence role: the hull units do carry SM-3: usn_rim-161d on DDG-84, 80 and 79, and usn_rim-161c on DDG-117 through its alias base usn_ddg_burke_f2a_113 (WeaponMagazineVLS_5, line 1823). Both are SEST_LongRangeSAM, 9,000 AP. Whether the engine models ballistic-missile targets or intercepts at all is untested. Author no guaranteed-intercept or 'shield' rule.
- The embarked helicopter squadron (HSM-79 livery) comes from the variant files, not from R03.

**Position.**
- Public location: approx 36.6N, 6.3W (verify).
- In-game evidence:
  - Stock world-data port [Rota] at 36.620763,-6.331558, Nation=Spain, Role=LargeMilitary, with no LandUnit (stock campaigns/ports.ini:158-161).
  - Stock sea links Rota-Banco Majuan and Rota-Cabo de sao Vicente (sea_links.ini:4191,4195), and the sea point Gibraltar Strait (sea_points.ini:184).
  - Mare Nostrum '28 mission 02 places nato_small_airbase (Nation=spain) at rel -51.51,low,33.15 from centre 36.05,-5.4 (02 Puerta de Hierro.ini:316-322). That decodes to 36.60,-6.26, about 4 NM from the world-data point.
- Pier water position: not validated.

**Forces (SCENARIO CHOICE)**

| Asset id | Allocation | Role | Unit id (variant) | Outcome | Qty |
|---|---|---|---|---|---|
| asset:med:rota_ddg84 | underway_deployed | Missile-defence-capable destroyer on an eastern-Med station | usn_ddg_burke_f2a_084_late (V1 DDG-84 Bulkeley) | exact | 1 |
| asset:med:rota_ddg84_helos | underway_deployed (embarked) | MH-60R pair | usn_mh-60r Squadron19 (HSM-79 livery) | exact | 2 |
| asset:med:rota_ddg117 | patrol | Gateway patrol: Gulf of Cadiz, Strait of Gibraltar, Alboran Sea | usn_ddg_burke_f2a_117 (V1 DDG-117 Paul Ignatius) | exact | 1 |
| asset:med:rota_ddg117_helos | patrol (embarked) | MH-60R pair | usn_mh-60r Squadron19 | exact | 2 |
| asset:med:rota_ddg80 | servicing_maintenance | Alongside Rota; unavailable at start | usn_ddg_burke_f2a_080_late (V1 DDG-80 Roosevelt) | exact | 1 |
| asset:med:rota_ddg80_helos | servicing_maintenance (embarked) | MH-60R pair, embarked on DDG-80; Rota has no aviation-capable unit | usn_mh-60r Squadron19 | exact | 2 |
| asset:med:rota_ddg79 | reserve | Ready destroyer alongside; finite relief hull (replaces the withdrawn asset:med:rota_ddg51) | usn_ddg_burke_f2a_079_late (V1 DDG-79 Oscar Austin) | exact | 1 |
| asset:med:rota_ddg79_helos | reserve (embarked) | MH-60R pair; moves with DDG-79 | usn_mh-60r Squadron19 | exact | 2 |
| option:med:rota_pier | abstract (not baseline) | Functional pier and shore rearm point, deferred until the unlimited-supply decision | nv_pt_boats_docks (Nation=usa, NameOverride 'NAVSTA Rota (pier stand-in)') | proxy | 0 |
| option:med:rota_berth_marker | abstract (not baseline) | Visual berth marker only, if a visible Rota berth is wanted now | ran_pt_boats_docks (no supply system; Nation=usa, NameOverride 'NAVSTA Rota (berth marker; no supply)') | proxy | 0 (1 only if wanted) |

Notes on the pier options:
- nv_pt_boats_docks cannot serve as a visual-only marker. Its supply block is in the unit file, so every placement carries it.
- ran_pt_boats_docks (3455404959; default name 'RAN base', Nation=Australia) has no supply system. It needs the Nation and NameOverride shown.
- The functional path is a capped SEST port clone, built on the integration/raaf-bases pattern. It would carry a finite pool and counted categories, as usn_take_lewis_clark does (AmmoCapacity 550,000 and AccountableAmmunitionCategory_1-5 at usn_take_lewis_clark.ini:292, 302-306).

Notes on the destroyers:
- Winning files: 3390330875 for 084, 117, 080 and 079 (alias bases f2a_081, f2a_113, f2a_080 and f2a_079).
- Variant1 ServiceDates are 2022 (084, 117) and 2024 (080, 079), with no end date.
- Every hull carries SM-3, SM-6/SM-2, Tomahawk, ESSM, ASROC and Mk54. All four are Flight IIA with a two-helicopter hangar (for example AircraftCapacity=2 on alias base usn_ddg_burke_f2a_079.ini:137). Each Variant1 embarks usn_mh-60r Squadron19 x2.

**Support services**
- **Shore ship ammunition:** none in the baseline. The deferred option nv_pt_boats_docks has a TruckSupplySystem (mods-source/3605013271/land_units/nv_pt_boats_docks.ini:48-57) with:
  - pool 9,999,999,999, AmmoLoadSpeed 9,999,999, no ceiling and no counted categories
  - range 3 nm, up to 6 targets, receivers at 10 kn or less
  - TargetTypes=Vessel only

  CHECK: this supply is effectively unlimited. Use it only as a disclosed home-port restock abstraction, or replace it with a capped SEST clone. It has not been tested in this world.

  SCENARIO CHOICE: near-instant unlimited rearming conflicts with 'No free rearm, stock reset' (gameplay-and-tests.md:20) and with the finite-supplier transfer test (:30). Disclosure alone does not make it a baseline row, so the pier stays at quantity 0 until that decision is made, as at Souda.
- **Round compatibility (from the unit files):**
  - DDG-84, 80 and 79: SM-3 (rim-161d, 9,000 AP), SM-6 (rim-174c, 8,000 AP) and SM-2 (rim-66p, 2,500 AP) are SupplyCategory SEST_LongRangeSAM.
  - DDG-117 (alias base usn_ddg_burke_f2a_113): SM-3 rim-161c (9,000 AP) and SM-6 rim-174a (4,200 AP) are SEST_LongRangeSAM. Its SM-2, usn_rim-66m-5 (3629144864), has no SupplyCategory and inherits 1,768 AP from usn_rim-66g, so it is limited only by points. It also carries rgm-109e5 (SEST_LandAttack, 4,350 AP) and ESSM rim-162a (500 AP).
  - Tomahawk (rgm-109e5a, 4,350 AP) is SEST_LandAttack.
  - Mk54 is AirTorpedo.
  - ESSM and ASROC have no category and are limited only by points.
- **Afloat supply:** the T-AKE in the Souda package, plus the finite relief sealift held in the world-level US sealift reserve (asset:med:relief_sealift_1). With the pier deferred, these are the only ship-ammunition suppliers.
- **Helicopter turnaround:** a flight-deck store exists, for example 13,800 AP on alias base usn_ddg_burke_f2a_081.ini:162. Turnaround itself is untested.
- **Fuel, repair and supplier restocking:** not established. The servicing state is a scenario label, not a repair service.

**Connections**

| To | Kind | Basis | Ref |
|---|---|---|---|
| NATO missile defence shield (no node) | role integration | source | R03:44 |
| eur_deveselu / eur_redzikowo | European missile-defence context (same paragraph, not linked) | authored | R03:44 |
| usa_norfolk_naval_station_norfolk | Norfolk generates forces for the Mediterranean; the Rota link itself is not stated | authored | R03:19 |
| med_souda_bay_nsa | Transit to the eastern-Med station and T-AKE rendezvous (~1,470 NM great-circle, indicative) | authored | - |
| US sealift reserve (asset:med:relief_sealift_1; world-level, not a node) | Relief sealift arrival via Gibraltar; DDG-117 escorts | authored | - |

**Routine activity (proposed, not implemented)**
- DDG-117 patrols the gateway box, seeded from the stock sea points Gibraltar Strait and Banco Majuan.
- DDG-84 holds the eastern-Med station and rearms from the T-AKE. On a set cycle it returns to Rota and DDG-79 sails to relieve it: the same hulls rotate, with no respawn. Each ship's MH-60R pair moves with it.
- When the relief sealift is released, DDG-117 changes from patrol to escort. It is the same hull, reallocated.
- Neutral traffic through the Strait:
  - civ_ms_bulk (Greece, Italy, UK and Liberia variants)
  - civ_ms_ritina (Italy, France and Liberia)
  - civ_ms_car_carrier_a
  - civ_ms_mairangi_bay
  - trawlers civ_fv_okean (Spain and France variants)
- Do not use civ_ms_freighter_d or civ_ms_poltava as neutral traffic. Every variant carries RE-power's near-instant, uncapped supply block, because the block sits in the unit file:
  - pools of 12,000,000 and 4,800,000 AP
  - AmmoLoadSpeed 9,999,999, no MaxAmmoPoints and no categories
  - sources: mods-source/3605013271/vessels/civ_ms_freighter_d.ini:127-137 and civ_ms_poltava.ini:128-138

  Neutral-supplier behaviour is untested.

**Validation and gaps**
- No named Rota installation unit exists.
- The collection has no US hospital, tug, salvage or fast-transport hull ('none').
- Host-nation Armada forces are not sourced and are not in the baseline. Exact units exist if wanted later: ae_ffg_alvaro_bazan, es_ss_galerna and spa_sh-60b_block1.
  - es_ss_galerna: only Variant1 Galerna is in date, to 2026. V2 Siroco ends in 2012, and V3 and V4 end in 2020 and 2024 (vanilla vessels/es_ss_galerna_variants.ini). Check it against the scenario date.
  - The only Spanish oiler is ae_ao_teide, a proxy whose ServiceDate ends in 1988.

---

### med_naples_nsa_naples - Naval Support Activity Naples

**Identity.** NSA Naples.
- Operator: US Navy (implied by the name; R03:44).
- Host: Italy.
- Kind: headquarters_command. Policy: context_only.

**SOURCE CLAIM.** R03:44: NSA Naples and NAS Sigonella 'provide command, control, and maritime patrol coverage across the Mediterranean and North Africa'. This is a joint statement; no units are named.

**CHECKS**
- The split (Naples for command, Sigonella for patrol) is inferred from a joint sentence. Verify it before assigning roles.
- A headquarters is not a tactical depot or target set.

**Position.**
- Public location: approx 40.9N, 14.3E (verify).
- In-game evidence:
  - Stock [Port Naples] at 40.8518,14.2681 (ports.ini:110-112) and city [Naples] (cities.ini:351-354).
  - Sea links Naples-Genoa and Naples-Iles Cani (sea_links.ini:725,729).
  - The nearest unit placed by any mission is about 215 NM away.

**Forces (SCENARIO CHOICE): none placed.**

| Asset id | Allocation | Role | Unit id | Outcome | Qty |
|---|---|---|---|---|---|
| abstract:med:naples_c2 | abstract | Command and control (register role) | - | none | 0 |

Rejected options:
- No command-ship hull exists for US use (us-navy: 'none').
- nv_headquarters is an army HQ with unlimited land-unit supply, so it would misrepresent a naval HQ.
- The warehouses_3 and nv_pt_boats_docks proxies would add a fake supply point.

**Support services.** None. The patrol role is placed at Sigonella.

**Connections.**
- med_sigonella_nas_sigonella: joint command, control and maritime patrol (source, R03:44).
- Rota and Souda: theatre command context (authored).

**Routine activity.** None. Optional Tyrrhenian merchant traffic (Italy variants of civ_ms_ritina and civ_ms_bulk) on the stock Naples sea links.

**Gaps.** No naval HQ unit and no command ship (Blue Ridge and Mount Whitney classes: none).

---

### med_sigonella_nas_sigonella - Naval Air Station Sigonella

**Identity.** NAS Sigonella.
- Operator: US Navy (implied by the name; R03:44).
- Host: Italy.
- Kind: naval_air_station. Policy: populate.

**SOURCE CLAIMS (R03:44)**
- With Naples it provides 'command, control, and maritime patrol coverage across the Mediterranean and North Africa'.
- With Souda Bay it 'forms the backbone of Mediterranean anti-submarine and intelligence operations'.
- No aircraft types or squadrons are named.

**CHECKS**
- Resident aircraft are the priority check (register, seed:23). The P-8A below is a SCENARIO CHOICE.
- R03:44 says only 'Italy'. 'Sicily' comes from the R02:34 DLA row (fidelity fix).
- Inventory hints of MV-22B and KC-130J at 'Sigonella/Rota (verify)' are not research and are not populated.

**Position.**
- Public location: approx 37.4N, 14.9E (verify).
- In-game evidence:
  - Mare Nostrum '28 mission 08 places nato_small_airbase (Nation=italy) at rel -14,low,26 from centre 36.6/15.1 (08 Escudo de Europa.ini:607-614).
    - This region's recompute under scope §2.1 (no cos(lat) factor) gives about 37.03N 14.87E.
    - The us-air-and-land verifier reported 37.03N 14.81E, because it applied cos(lat).
    - Either way the point lies about 22-23 NM south of the field, so do not reuse it as an anchor.
  - The nearest proven land placement is about 16 NM away (tgt_fueltanks_large at Augusta, lines 571-586).
  - Stock sea point [Canale Di Malta] at 36.29,14.62 (sea_points.ini:232).

**Forces (SCENARIO CHOICE)**

| Asset id | Allocation | Role | Unit id (variant) | Outcome | Qty |
|---|---|---|---|---|---|
| asset:med:sig_nas | support | Maritime patrol airfield | usa_airbase (V1 'Naval Air Station'; NameOverride 'NAS Sigonella (generic NAS stand-in)'; CustomAirGroup=True) | proxy | 1 |
| asset:med:sig_p8_1 | patrol | Central Med, Ionian and Sicily Channel ASW patrol | usn_p_8a (USN Squadron1-14 only) | exact | 1 |
| asset:med:sig_p8_2 | resident_at_base | Ready aircraft on alert | usn_p_8a | exact | 1 |
| asset:med:sig_p8_3 | servicing_maintenance | In maintenance; unavailable at start | usn_p_8a | exact | 1 |
| option:med:sig_isr_uav | abstract (not baseline) | ISR UAV | raaf_mq-4c_triton | missing_fit (Australia-only squadrons) | 0 |

**Support services**
- **Aircraft turnaround:** usa_airbase rearms its own air group from flight-deck stores:
  - 2,000,000 AP in total
  - AirTorpedo 72, which covers the P-8A's Mk54
  - Harpoon 144 and Ovod 144

  Stocks can be overridden per placement (precedent: 02 Puerta de Hierro.ini:327-330). Recovery and repeat sorties are untested.
- **Air-to-air refuelling:** not established. The P-8A file declares no ReceiverSystems.
- **Ship ammunition, fuel, repair and restocking:** none at the air station, or not established.

**Connections.**
- med_naples_nsa_naples (source, R03:44).
- med_souda_bay_nsa: ASW and intelligence backbone (source, R03:44).
- med_sigonella_dla_distribution: same name only; colocation is not stated (authored; R02:34 and R03:44).
- med_rota_naval_station: P-8A cover for destroyer transits (authored).

**Routine activity (proposed).**
- The three P-8As rotate through patrol, alert and servicing. They are the same airframes, not replacements.
- Patrol tracks reach toward the North African coast, following the R03:44 wording; the exact tracks are authored.
- Civilian air traffic: civ_a320 and civ_a330 (Italy, France, Spain, Tunisia, Libya, Turkey and Greece variants).
- Merchant traffic in the Sicily Channel on the stock Canale Di Malta links (sea_links.ini:737).

**Gaps.**
- No named base unit.
- US MQ-4C: missing_fit. RQ-4: none.
- Host Italian maritime patrol aircraft exist only as a date-limited proxy (mm_br1150, ServiceDate 1972-2017). Not proposed.

---

### med_sigonella_dla_distribution - DLA Distribution Sigonella

**Identity.**
- Operator: US Defense Logistics Agency.
- Host: Italy.
- Kind: distribution_depot. Policy: abstract_logistics_only.

**SOURCE CLAIMS**
- R02:23: sustainment for the Middle East and Europe 'flows through DLA Distribution Bahrain, DLA Distribution Sigonella in Italy, and DLA Distribution Europe'.
- R02:34 (table): Sicily, Italy; 'Mediterranean/European logistical gateway'. This repeats R02:23 within the same report.
- Agency-wide context:
  - R02:11: DLA supplies 86% of spare parts and nearly 100% of fuel and troop-support consumables. R01:21 repeats this, which is repetition, not corroboration.
  - R02:21: DLA has seven overseas hubs.

**CHECKS**
- DLA centre counts and scope are a priority check (seed:23).
- Colocation with the air station is not stated. Fidelity wording: 'same name; R02:34 says Sicily for DLA Sigonella; R03:44 says only Italy for NAS Sigonella; colocation not stated'.
- R02:23 and R02:34 name no ships, and R02 does not say that DLA dispatches ships. The relief sealift ship formerly listed here is a strategic sealift hull (vanilla display 'T-AKR, Roll-on Roll-off'), not a DLA asset. It now sits in the world-level US sealift reserve, with only an authored link to this node.

**Position.** Only 'Sicily, Italy' (R02:34). The node is abstract and needs no anchor.

**Forces (SCENARIO CHOICE): none placed.** The node stays abstract. The register's populate_reason says DLA Sigonella stock is expressed through NAS Sigonella support functions, if wanted. The relief sealift ship and its details have moved to the world-level US sealift reserve (after the Germersheim section).

**Support services**
- No depot is placed. If physical stock is wanted, it is the finite NAS Sigonella airfield stores. The relief sealift in the US sealift reserve is not DLA stock.
- Supplier restocking: not established. No port or depot restocks a supplier's pool.
- Air cargo: the usaf_c-141b PlaneCargoSupplySystem is the collection's only air-cargo ammunition system, and it is untested. It holds 60,000 AP with TargetTypes=None (vanilla aircraft/usaf_c-141b.ini:176-180), and its squadrons are dated 1965-2006 (usaf_c-141b_squadrons.ini:18).
- Fuel: not established. The R02:11 fuel share is agency-wide context, not a game service.

**Connections.**
- Sourced (R02:23):
  - usg_dla_distribution_network: parent network.
  - me_bahrain_dla_distribution and eur_germersheim_dla_distribution_europe: the sustainment trio.
- Authored:
  - NAS Sigonella: name association.
  - US sealift reserve (asset:med:relief_sealift_1): gateway context only (R02:23, R02:34). The ship is not DLA's.

**Routine activity.** None. The relief sealift's dormancy and release are described under the US sealift reserve.

**Gaps.**
- No DLA installation unit.
- No in-game supplier restocking.

---

### med_souda_bay_nsa - Naval Support Activity Souda Bay

**Identity.** NSA Souda Bay.
- Operator: US Navy (implied by the name; R03:44).
- Host: Greece.
- Kind: pending/mixed. The fidelity fix applies because R03:44 does not say whether the site is a naval pier, an airfield or both.
- Policy: populate_small.

**SOURCE CLAIM.** R03:44: Sigonella, 'alongside Naval Support Activity Souda Bay in Greece, forms the backbone of Mediterranean anti-submarine and intelligence operations'. No units or facilities are named.

**CHECKS**
- Check the facility type before fixing the population type.
- Host Hellenic forces are not in the reports. An exact HAF unit (haf_f-16c-bl52plus) exists, but there is no Greek warship of any kind.

**Position.**
- Public location: airfield approx 35.5N, 24.1E; naval pier area approx 35.5N, 24.2E (verify).
- In-game evidence: stock 'Dangerous Straits 1985' places airfield_small_1 Variant1, with per-unit Nation=greece, at rel -73.63,low,-115.41 from centre 37.44/25.38 (Dangerous Straits 1985.ini:98-99,643-650).
- Decode, settled under the game's convention (scope §2.1, no cos(lat) factor): 35.52N 24.15E, about 1 NM from the field. That agrees with the placement lens (35.52,24.15).
  - The us-air-and-land verifier's 35.52N 23.83E (about 15 NM west) applied cos(lat), contrary to §2.1. Its Sigonella figure did the same.
  - Only an editor confirmation is pending.

**Forces (SCENARIO CHOICE, conditional on the facility check)**

| Asset id | Allocation | Role | Unit id (variant) | Outcome | Qty |
|---|---|---|---|---|---|
| asset:med:souda_airfield | support | Forward maritime patrol airfield | airfield_small_1 (V1 USA; Nation per placement; NameOverride; CustomAirGroup=True) | proxy | 1 |
| asset:med:souda_p8_det | patrol | Eastern-Med ASW patrol detachment | usn_p_8a (USN Squadron1-14) | exact | 1 |
| asset:med:take_1 | support | Replenishment station south of Crete, turning around at Souda | usn_take_lewis_clark (Variant4 'T-AKE 11 USNS Washington Chambers', reserved here; ServiceDate 2006-2060) | proxy (stand-in hull) | 1 |
| option:med:souda_pier | abstract (not baseline) | Pier | nv_pt_boats_docks | proxy | 0 |

The pier option is deferred because it would add an unlimited shore supply point, as the deferred Rota pier would.

The T-AKE variant name omits '(stand-in)', which only the Default name carries. The placement's NameOverride must therefore carry the label, for example 'USNS Washington Chambers (T-AKE 11; stand-in hull)'. Vessel NameOverride keys have stock mission precedent.

**Support services**
- **Afloat ship ammunition:** the T-AKE has:
  - pool 550,000, no ceiling, 110/s
  - range 1.0 nm, 2 targets, own speed 13 kn or less, receivers 16 kn or less
  - categories: Harpoon 48, AirTorpedo 72, ALWT 40, SEST_LandAttack 48, SEST_LongRangeSAM 56

  SM-3 and SM-6 on all four Rota hulls, and SM-2 rim-66p on DDG-84, 80 and 79, draw on the shared SEST_LongRangeSAM count of 56. DDG-117's SM-2 (rim-66m-5) is uncategorised and limited only by points. The budget is finite because restocking is not established.
- **Aircraft turnaround:** airfield_small_1 stores 1,000,000 AP (AirTorpedo 48, Harpoon 96). Untested.
- **Fuel, repair and restocking:** not established.

**Connections.**
- med_sigonella_nas_sigonella: ASW and intelligence backbone (source, R03:44).
- Authored:
  - Rota: destroyer rearm rendezvous.
  - US sealift reserve (asset:med:relief_sealift_1): relief sealift onward route.
  - Akrotiri: about 440 NM.
  - me_bahrain_nsa_bahrain: via Suez, using the stock points Port Said and Suez (sea_points.ini:238,241).

**Routine activity (proposed).**
- The P-8A detachment flies an eastern-Med ASW line.
- DDG-84 closes on the T-AKE's station to rearm.
- Civilian traffic:
  - civ_fv_dhow (Greece, Cyprus and Egypt variants)
  - civ_ms_ivan_franko (Greece variant; Soviet-era hull, label it as a stand-in)
  - civ_ms_bulk and civ_ms_car_carrier_a (Greece variants)
- Avoid civ_ms_poltava and civ_ms_yuniy_partizan as neutral traffic. Every variant carries RE-power's near-instant, uncapped supply block: 4,800,000 and 2,370,000 AP (2.37M-12M AP across the RE-power merchants named in this region). Neutral-supplier behaviour is untested.

**Gaps.** No named Souda unit, no Greek warships, and no finite shore supply.

---

### med_akrotiri_raf - RAF Akrotiri

**Identity.**
- Operator: United Kingdom (Royal Air Force).
- Host: Cyprus, in the report's wording. Akrotiri is in a UK Sovereign Base Area; check how the build labels the host.
- Kind: air_base. Policy: populate_small.

**SOURCE CLAIM.** R01:59: 'a crucial forward operating and mounting base for the United Kingdom in the Eastern Mediterranean, frequently used for search and rescue operations and regional crisis staging'. No aircraft are named.

**CHECKS**
- Check the current detachments. Every type below is a SCENARIO CHOICE.
- Inventory hints of US rotations at Akrotiri (U-2, RC-135, F-15E, F-16) are not research and are not populated.
- Build no sanctuary rule from the word 'crucial'.

**Position.**
- Public location: approx 34.6N, 33.0E (verify).
- No placement precedent and no stock world-data point for Cyprus.
- The nearest units placed by any mission are about 89 NM away at sea and 147 NM on land.

**Forces (SCENARIO CHOICE)**

| Asset id | Allocation | Role | Unit id (variant) | Outcome | Qty |
|---|---|---|---|---|---|
| asset:med:akr_airfield | support | Forward operating airfield | nato_small_airbase (Nation=uk; NameOverride 'RAF Akrotiri (stand-in airfield)'; CustomAirGroup=True) | proxy | 1 |
| asset:med:akr_typhoon_1 | resident_at_base | Air defence on alert | raf_ef2000_fgr4_late (Default) | exact | 1 |
| asset:med:akr_typhoon_2 | servicing_maintenance | In maintenance | raf_ef2000_fgr4_late | exact | 1 |
| asset:med:akr_voyager | support | Tanker and transport for crisis staging | uk_a330_mrtt (Default or Squadron1) | exact | 1 |
| asset:med:akr_a400m | support | Tactical airlift; visual traffic only | uk_a400m_airdroop-para (No. 30 or No. 70 Sqn) | exact | 1 |
| asset:med:akr_sar | resident_at_base | SAR standby, labelled 'SAR stand-in (Merlin HM2)' | rn_merlin_hm2 | proxy | 1 |

Rejected airfield alternatives:
- is_airbase_akureyri V2 is UK-flagged but named 'RAF Gibraltar'; it would need a relabel.
- is_airbase_reykjavik has the TacticalNuke category in its default stocks.
- airbase_us displays as 'U.S. Air Force Base'.

**Support services**
- **Aircraft turnaround:** the airfield stores 1,500,000 AP. Untested.
- **Air-to-air refuelling:** the Voyager has TankerSystems=ProbeAndDrogue (uk_a330_mrtt.ini:194).
  - Voyager-to-A400M probe-and-drogue refuelling is declared in the files (uk_a400m_airdroop-para.ini:153, ReceiverSystems=ProbeAndDrogue) but untested.
  - Typhoon refuelling is not established: raf_ef2000_fgr4_late declares no ReceiverSystems.
- **Airlift:** the A400M unit has no supply system. Its Supply loadout is an airdrop store (Station1=Supply, uk_a400m_airdroop-para.ini:201; ammunition/Supply.ini is Type=Paratrooper). The only air-cargo ammunition system is usaf_c-141b's, untested, and its squadrons are dated 1965-2006.
- **Ship support:** none.
- **Fuel, repair and restocking:** not established.

**Connections.**
- Eastern Mediterranean sea area (source, R01:59).
- med_souda_bay_nsa (authored).

**Routine activity (proposed).**
- Typhoon alert and CAP sorties, with the two airframes swapping on a cycle.
- A400M departures and arrivals.
- The SAR stand-in on standby. SAR events are authored; rescue is not modelled.
- Civilian traffic:
  - civ_a330 (Greece, Egypt, Lebanon, Turkey and Libya variants)
  - civ_fv_dhow (Cyprus and Egypt variants)
  - civ_ms_mairangi_bay (Israel variants)

**Gaps.**
- No named base.
- No modern UK SAR helicopter. rn_sea_king_hc4 squadrons end in 2013-2016.
- UK F-35B: missing_fit.
- Exact RAF RC-135 (boeing-rc135 Sq6/7) and RAF P-8 (usn_p8 Sq4) units exist if later research supports them.

---

### eur_deveselu_nsf_aegis_ashore - Naval Support Facility Deveselu

**Identity.**
- Operator: United States Navy, implied by the NSF name but not stated (fidelity fix).
- Host: Romania. The region is 'Europe - Romania'; the fidelity fix drops '(interior)'.
- Kind: fixed_defence. Policy: context_only.

**SOURCE CLAIM.** R03:44: the simulation 'must account for' the Aegis Ashore sites at Deveselu and Redzikowo, which 'provide critical ballistic missile defense coverage for the European continent'. 'Must account for' is the report's recommendation, not a game rule. No status, interceptor or radar detail is given.

**CHECKS**
- Whether the engine models ballistic-missile threats or intercepts is untested.
- Author no coverage or guaranteed-intercept rule.

**Position.**
- Public location: approx 44.1N, 24.4E (verify). It is inland; that is our check note, not a report claim.
- No precedent. The nearest placed unit is about 244 NM away.
- It is about 230 NM from the candidate world centre.

**What the collection can and cannot represent.**
- It cannot represent:
  - the SPY-1 deckhouse
  - land Mk41 or SM-3 launchers
  - the interceptor inventory
  - the coverage itself

  No such land unit exists (us-navy, us-air-and-land and placement lenses all return 'none').
- SM-3 rounds exist only as ship ammunition, for example on the Rota destroyers.
- At most it can show a labelled passive marker.

| Asset id | Allocation | Role | Unit id | Outcome | Qty |
|---|---|---|---|---|---|
| abstract:eur:deveselu_aegis_ashore | fixed_defence | Aegis Ashore site | - | none | 0 |
| option:eur:deveselu_marker | abstract | Passive map marker only, NameOverride 'NSF Deveselu - Aegis Ashore (marker only; SM-3/SPY-1 not modelled)' | us_cobra_dane_ewr or nato_large_ewr_station | proxy | 0 (1 only if wanted) |

Both marker units are vanilla, Role=Target, with a visual sensor only.

Refuted or unusable stand-ins:
- wp_an_tpy_2 is a 3,000 km datalinked air-search radar, not a passive marker.
- Do not use thaad_tel, Patriot or US_Missile (an ICBM base). They are different systems and would invent a deployment.

**Support services.** None. **Connections:** Redzikowo as companion site (source, R03:44); Rota missile-defence context (authored). **Routine activity:** none.

**Gaps.** Aegis Ashore outcome: none. A new SEST land unit would be needed.

---

### eur_redzikowo_nsf_aegis_ashore - Naval Support Facility Redzikowo

**Identity.**
- Operator: US Navy, implied by the name. The Deveselu fidelity fix is applied here by analogy.
- Host: Poland.
- Kind: fixed_defence. Policy: context_only.

**SOURCE CLAIM.** Same as Deveselu (R03:44).

**CHECKS**
- Operational status and date. The register notes it was reported as becoming operational around 2024.
- Its location relative to any playable Baltic area.

**Position.**
- Public location: approx 54.5N, 17.1E, near Slupsk, a short distance inland (verify).
- The nearest placed units are 32 NM away in the air and 50 NM on land.
- The stock Baltic sea network exists, for example [Zatoka Gdansk] (baltic_sea_points.ini:106).
- It is about 760 NM from the candidate world centre.

**Forces.** Same as Deveselu:
- abstract:eur:redzikowo_aegis_ashore: outcome none, quantity 0.
- option:eur:redzikowo_marker: us_cobra_dane_ewr or nato_large_ewr_station, labelled proxy, quantity 0.
- Same refuted stand-ins.

**Support, activity.** None. **Connections:** Deveselu (source, R03:44); Rota (authored). **Gaps:** same as Deveselu.

---

### eur_germersheim_dla_distribution_europe - DLA Distribution Europe (Germersheim)

**Identity.**
- Operator: US Defense Logistics Agency.
- Host: Germany.
- Kind: distribution_depot. Policy: abstract_logistics_only.

**SOURCE CLAIM.** R02:23: 'DLA Distribution Europe located in Germersheim, Germany', part of the sustainment trio with Bahrain and Sigonella. It is not in the R02:27-34 table. Agency context: R02:11 and R02:21.

**CHECKS.** The missing table row, and DLA scope (seed:23).

**Position.**
- Public location: approx 49.2N, 8.4E, inland on the Rhine (verify).
- Stock city [Mannheim] (cities.ini:71-73) is about 16 NM away.
- The nearest placed unit is about 377 NM away.

**Forces.** None.

| Asset id | Allocation | Role | Unit id | Outcome | Qty |
|---|---|---|---|---|---|
| abstract:eur:germersheim_depot | abstract | European resupply origin; marker not recommended | warehouses_3, warehouses_1, tgt_fueltanks_large | proxy | 0 |

These would be static targets with no function: re-nationed, and inland.

**Support services.** None in game. No physical expression of DLA throughput is placed. The nearest in-world stand-in is the finite relief sealift in the world-level US sealift reserve, which has only an authored link to DLA Sigonella.

**Connections.**
- Sourced (R02:23): usg_dla_distribution_network (parent), DLA Sigonella and DLA Bahrain.
- Authored: an abstract supply link to the Mediterranean users.

**Routine activity.** None.

**Gaps.** No depot unit and no depot-to-theatre logistics mechanic. If a physical shipment is ever wanted, the US Ready Reserve Force ro-ros (civ_ms_roro_c, and civ_ms_roro_a US variants) are the honest carrier.

---

**World-level US sealift reserve (not a register node; SCENARIO CHOICE)**

This reserve holds the one physical hull that review moved out of DLA Sigonella. It belongs to no register node. R02:23 and R02:34 give only the gateway context and name no ships.

| Asset id | Allocation | Role | Unit id (variant) | Outcome | Qty |
|---|---|---|---|---|---|
| asset:med:relief_sealift_1 | reserve | Finite relief sealift with an ammunition pass, released once through Gibraltar | usn_takr_algol (Variant6 'Regulus T-AKR-292', reserved here; ServiceDate 1981 with no end) | exact | 1 |

The Algol unit wins from SEST_Integration and has its own mesh. Its supply system:
- TruckSupplySystem pool 500,000, no ceiling, 45 pts/s
- range 0.5 nm; own speed 8 kn or less, receivers 12 kn or less
- categories: Harpoon 40, AirTorpedo 48, ALWT 24, SEST_LandAttack 32, SEST_LongRangeSAM 32

Variants 2, 4, 5 and 8 end in 2025, so they are excluded.

Alternative: civ_ms_roro_a, US Variants 6-10, labelled as an RRF stand-in. Its MaxAmmoPoints of 2,000 blocks SM-3, SM-6, SM-2 rim-66p (2,500 AP) and Tomahawk, but not DDG-117's SM-2 rim-66m-5 (1,768 AP).

**CHECKS**
- Check the real-world status of Regulus at the scenario date.
- Stock sea-link segments exist (Rota-Banco Majuan-Gibraltar Strait; Canale Di Malta-Alexandria), but full route continuity is unvalidated.

**Connections (all authored).**
- med_sigonella_dla_distribution: gateway context (R02:23, R02:34).
- med_rota_naval_station: Gibraltar arrival; DDG-117 escorts.
- med_souda_bay_nsa: onward route to the eastern Med.

**Routine activity (proposed).**
- The ship is held dormant outside the region (Disabled=True, woken by Action_SetEnabledStatus=True; the stock mechanism in scope §2.8).
- It is released once, enters via Gibraltar and is escorted by the gateway destroyer.
- If it is sunk, it is gone; there is no replacement wave.

---

**First tests for this region** (from gameplay-and-tests.md):
1. T-AKE to destroyer transfer of SEST_LongRangeSAM rounds, with the T-AKE pool falling.
2. The decision on the Rota pier's unlimited supply. If a functional pier is wanted, test a capped SEST port clone whose finite pool falls on transfer.
3. P-8A recovery and re-sortie at the usa_airbase stand-in.
4. Dormant release of the relief ship.
5. Rotation of the same hulls between patrol, deployment and servicing across a save and reload.
6. The Souda precedent decode in the editor.
