# World population register

Status: **DESIGN REGISTER, first complete pass.** Every node in R01-R03 has a population package, and every package is joined to the installed collection. Nothing has been placed, built or run in game. No campaign, unit, pack, load order, installer or Workshop item is changed.

Branch `sest-dev/sweet-lovelace-3kxsve`, built on `feature/world-campaign-draft` (`50cad91b`). Date 7 October 2026. Revised 10 October 2026 on `sest-dev/inspiring-wozniak-8vuckh` after main's 9 October mod export: one retired cruiser id (`usn_cg_ticonderoga_vls_2025` -> `usn_cg_bunker_hill_vls_2024`, CG-64 Gettysburg V5). First runtime candidate: `DYNAMIC_CAMPAIGN_ADAPTER.md`.

## What this is

The first deliverable of `WORLD_POPULATION_PLAN.md`: what goes where in the populated world, how it maps to the collection, how the regions connect, and what is still missing. It is a world to operate in, not a story and not a set of scenarios.

- **69 world nodes** from R01-R03, deduplicated. Colocated facilities stay separate:
  - Guam naval base, Andersen and DLA Guam;
  - the five Djibouti facilities;
  - Yulin, Longpo and Lingshui;
  - NSA Bahrain, Muharraq and Jebel Ali;
  - Mount Pleasant and Mare Harbour.

  There is also one world-level record, the US sealift reserve.
- **37 named sea areas and routes**, and a 26-item expansion backlog of places the reports only mention.
- **318 force rows.** Each is a role slot with an allocation (resident at base, underway, patrol, escort, servicing, reserve, transit, support, training/test, fixed defence or abstract), mapped to unit files that win the load order. Each is labelled with one of four outcomes:
  - **exact**: the platform exists for that operator;
  - **proxy**: a stand-in that must carry a visible label;
  - **missing_fit**: the platform exists, but not the operator, livery, loadout or function needed;
  - **none**: no usable asset.
- **Connections** (source-described vs authored), **routine activity** (patrols, arrivals, transits, civilian and neutral traffic), **support services** (ship ammunition, aviation, restocking, fuel and repair, kept separate) and **checks** for every node.

Every package keeps three things apart:
- **SOURCE CLAIM**: what a report says, cited as `R03:23`.
- **CHECK**: a known doubt or a verification still needed.
- **SCENARIO CHOICE**: our proposed allocation, quantity or activity.

Report totals such as Norfolk's "over 75 ships" are never placement instructions, and quantities are small and suited to each node's role. Each physical asset has one identity and one allocation world-wide. For example, each carrier in R03's status table appears exactly once: George Washington underway from Yokosuka, Roosevelt in transit to the Gulf, Lincoln deployed in the Western Pacific, Stennis in overhaul at Newport News, Reagan in drydock at Puget Sound.

## Files

| File | Contents |
|---|---|
| `register/00-world-integration.md` | World-level sections: identity check and hull ledger, connections register, collection gaps, placement overview with scope implications, status, CHECK items and ordered next steps |
| `register/01-...` to `register/11-...` | One file per region: region summary, then one package per node |
| `register/packages.json` | The same 70 packages in structured form |
| `register/review-log.json` | The review trail: each region's skeptic findings, what was applied or declined, the second skeptic, and the final consistency check |
| `work/` | The inputs: source claims and nodes (`source-register.json`), collection inventories, and the scope and performance evidence and probe plan |

## Coverage by region

| Region file | Coverage | Nodes | populate / small | abstract / context / other | Force rows | exact | proxy | missing_fit | none |
|---|---|---|---|---|---|---|---|---|---|
| [01-us-pacific.md](register/01-us-pacific.md) | US Pacific: Southern California, Puget Sound, West Coast distribution | 8 | 3 / 1 | 4 | 38 | 27 | 10 | 0 | 1 |
| [02-us-atlantic.md](register/02-us-atlantic.md) | US Atlantic, specialist support and CONUS depots | 11 | 2 / 0 | 9 | 36 | 18 | 12 | 3 | 3 |
| [03-west-central-pacific.md](register/03-west-central-pacific.md) | Western and Central Pacific: Yokosuka, Guam/Andersen, Pearl Harbor distribution | 6 | 2 / 1 | 3 | 26 | 13 | 7 | 1 | 5 |
| [04-australia-indian-ocean.md](register/04-australia-indian-ocean.md) | Australia, Indian Ocean and the Afloat Prepositioning Fleet | 4 | 2 / 1 | 1 | 27 | 10 | 15 | 1 | 1 |
| [05-gulf-horn-of-africa.md](register/05-gulf-horn-of-africa.md) | Persian Gulf and the Djibouti cluster | 9 | 0 / 8 | 1 | 44 | 24 | 19 | 0 | 1 |
| [06-mediterranean-europe.md](register/06-mediterranean-europe.md) | Mediterranean and European support | 10 | 2 / 2 | 6 | 32 | 17 | 11 | 1 | 3 |
| [07-china-maritime.md](register/07-china-maritime.md) | Chinese naval and naval-air bases: Hainan, Ningbo | 4 | 3 / 1 | 0 | 34 | 20 | 10 | 1 | 3 |
| [08-china-logistics.md](register/08-china-logistics.md) | Chinese national logistics (JLSF) and the Ban Keun lead | 7 | 0 / 0 | 7 | 11 | 0 | 4 | 0 | 7 |
| [09-russia.md](register/09-russia.md) | Russian long-range aviation and northern/Pacific context | 4 | 1 / 3 | 0 | 21 | 13 | 8 | 0 | 0 |
| [10-japan-norway-patrol.md](register/10-japan-norway-patrol.md) | Japanese and Norwegian maritime patrol network | 4 | 4 / 0 | 0 | 30 | 13 | 14 | 2 | 1 |
| [11-south-atlantic-france.md](register/11-south-atlantic-france.md) | South Atlantic outpost and French strategic context | 3 | 0 / 2 | 1 | 19 | 6 | 9 | 3 | 1 |
| **Total** | | **70** | **19 / 19** | **32** | **318** | **161** | **119** | **12** | **26** |

"Other" means abstract logistics only, context only, do not populate (Ban Keun) or reserve only. Rows marked none, missing_fit, quantity 0 or option place nothing by default: at least 53 rows. Force rows are role slots, not units.

## What the register shows

- **The collection covers the combat forces well, and the infrastructure poorly.**
  - Carriers, destroyers, submarines, maritime patrol aircraft and bombers are mostly exact for the US, China, Russia, Japan and Australia.
  - Named bases are almost all labelled proxies. RAAF Tindal (an existing SEST base) is the exception.
  - No finite shore supplier, no repair system and no ship-fuel model exist. Ship-ammunition resupply is finite only through SEST-patched supply hulls, and supplier restocking is not established.
  - The full gap table is in `00-world-integration.md`, section 3.
- **Placement readiness falls into three groups** (`00-world-integration.md` section 4 and next step 4):
  - **Proven anchors.** Guam/Andersen, Diego Garcia, Tindal/Stirling, Hainan, Djibouti, the Gulf, Rota/Souda/Sigonella, Olenya/Evenes and Naha are near positions that already load.
  - **Land mask or coastline extract needed.** The US coasts, Japan's home islands, Ningbo, Akrotiri and Brest.
  - **Probe-gated.** The Falklands, east of the date line, Pearl Harbor, and the inner waters of Kitsap, Apra and Kola.
- **Scope does not block the world.**
  - The map centre is a coordinate datum, not a boundary. Stock missions and a game-written save hold units 3,900-12,000 NM from it, and absolute `GeoPosition` placement exists.
  - The one engine edge on record is the ±180° date line. Today's binding limits are SEST builder choices, and each can be extended.
  - Capacity, long-range save/load and the date line are unmeasured. The probe plan in `work/scope-probes.md` measures them, and the choice between one mission, linked missions or a hybrid waits on it (`work/scope-and-performance.md`).

## Decisions needed

1. **Scenario date.** Many pinned hulls, squadrons and liveries are date-gated in their unit files. Examples: CVN-68's variant runs to 2027; the JMSDF P-3C squadrons inherit 1977-1995 dates; the C-141B covers 1965-2006. A world date is needed before the date-gate pass (`00-world-integration.md` 5.3 item 2).
2. **Unlimited piers.** The only shore resupply units in the collection are effectively unlimited (9,999,999,999 points). Choose between a capped SEST port clone, a disclosed exception or no shore resupply.
3. **C32: PLAN missile pricing.** The China maritime and China logistics packages read the `#!extend` stack differently: is `plan_yj-18` and the rest of the PLAN list metered or free? This decides whether Chinese resupply is rationed (`review-log.json`, consistency conflicts).
4. **C33: Yulin release escort.** The Guilin relief convoy needs an escort from Yulin, but no Yulin surface hull is at base at release time. Use `yulin_corvette_1` on return from patrol, or allow an unescorted release.
5. **Shared hull pools.** A few named-hull pools are still drawn from more than one region: Burke DDG-99/101-107, T-AKE, T-AO, Algol, LCS/CG and Flight I DDG-54. The proposed pins are in `00-world-integration.md` 1.5 and next step 1.

## Most important checks before precise use

The full list is in `00-world-integration.md` 5.3. In short:
- The carrier statuses in R03's table are undated "current/recent" claims.
- Lingshui's aircraft assignments.
- Whether the French Djibouti facility is BA 188, the Héron naval base, or both.
- DLA scope and centre counts.
- The JLSF "Arm" 2024 terminology.
- The MQ-4C operating site.
- The Olenya aircraft counts, a 2024-25 imagery snapshot; the scenario uses 6 Tu-22M3, 2 Tu-95MS, 1 Tu-160 and 1 An-12.
- Labels and fits to confirm in the editor.

## How it was built and checked

- **Claims.** Three agents extracted every place-specific claim with its line number (R01 97, R02 81, R03 196). A consolidation pass merged them into nodes, and three skeptics checked every claim against the report text.
- **Collection.** Six agents inventoried the unit files that win the load order by operator and function. A skeptic per inventory re-resolved every id.
- **Packages.** Eleven regional agents wrote the packages, and a skeptic per region checked:
  - source fidelity;
  - that unit ids resolve;
  - double allocation;
  - scale against role;
  - labels;
  - plan policy.
- **Fixes.**
  - First pass: 112 findings, applied or declined with reasons.
  - Second skeptic: 25 unresolved points and 14 regressions, then fixed.
  - Integration critic: recounted the totals and supplied 47 exact text fixes.

  All of it is recorded in `review-log.json`.
- **Unit ids.** 220 were re-resolved on this branch. Two known ids do not resolve, and neither is used.

None of this establishes placement, runtime behaviour or playtest results. Those are Passes C-E of the plan.

## Node index


| World id | Name | Operator | Kind | Policy | Region file |
|---|---|---|---|---|---|
| `usp_coronado_naval_base_coronado` | Naval Base Coronado | United States Navy | mixed_base | context_only | [01](register/01-us-pacific.md) |
| `usp_coronado_nas_north_island` | Naval Air Station North Island | United States Navy | naval_air_station | populate | [01](register/01-us-pacific.md) |
| `usp_coronado_nab_coronado` | Naval Amphibious Base Coronado | United States Navy | training | populate_small | [01](register/01-us-pacific.md) |
| `usp_sandiego_naval_base_san_diego` | Naval Base San Diego | United States Navy | naval_base | populate | [01](register/01-us-pacific.md) |
| `usp_kitsap_naval_base_kitsap` | Naval Base Kitsap | United States Navy | mixed_base | context_only | [01](register/01-us-pacific.md) |
| `usp_kitsap_bremerton_psns` | Puget Sound Naval Shipyard (Naval Base Kitsap - Bremerton) | United States Navy | shipyard_maintenance | populate | [01](register/01-us-pacific.md) |
| `usp_kitsap_bangor` | Naval Base Kitsap - Bangor | United States Navy | naval_base | context_only | [01](register/01-us-pacific.md) |
| `usp_dla_san_joaquin` | DLA Distribution San Joaquin | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [01](register/01-us-pacific.md) |
| `usa_norfolk_naval_station_norfolk` | Naval Station Norfolk | United States Navy | naval_base | populate | [02](register/02-us-atlantic.md) |
| `usa_jacksonville_nas_jacksonville` | Naval Air Station Jacksonville | United States Navy | naval_air_station | populate | [02](register/02-us-atlantic.md) |
| `usa_patuxent_nas_patuxent_river` | Naval Air Station Patuxent River | United States Navy | research_test | context_only | [02](register/02-us-atlantic.md) |
| `usa_whiting_nas_whiting_field` | Naval Air Station Whiting Field | United States Navy | training | abstract_logistics_only | [02](register/02-us-atlantic.md) |
| `usa_newport_news_shipbuilding` | Newport News Shipbuilding | not stated in the reports | shipyard_maintenance | context_only | [02](register/02-us-atlantic.md) |
| `usg_dla_distribution_network` | Defense Logistics Agency distribution network (agency-wide) | US Defense Logistics Agency | logistics_centre | abstract_logistics_only | [02](register/02-us-atlantic.md) |
| `usa_dla_susquehanna` | DLA Distribution Susquehanna | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [02](register/02-us-atlantic.md) |
| `usa_richmond_defense_supply_center` | Defense Supply Center Richmond | United States | distribution_depot | abstract_logistics_only | [02](register/02-us-atlantic.md) |
| `usa_army_depot_anniston` | Anniston (Army depot) | US Army | distribution_depot | abstract_logistics_only | [02](register/02-us-atlantic.md) |
| `usa_army_depot_red_river` | Red River (Army depot) | US Army | distribution_depot | abstract_logistics_only | [02](register/02-us-atlantic.md) |
| `usa_army_depot_tobyhanna` | Tobyhanna (Army depot) | US Army | distribution_depot | abstract_logistics_only | [02](register/02-us-atlantic.md) |
| `wpac_yokosuka_naval_base` | Yokosuka Naval Base | United States Navy | naval_base | populate | [03](register/03-west-central-pacific.md) |
| `wpac_yokosuka_dla_distribution` | DLA Distribution Yokosuka | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [03](register/03-west-central-pacific.md) |
| `wpac_guam_naval_base_apra_harbor` | Naval Base Guam (Apra Harbor) | United States Navy | naval_base | populate | [03](register/03-west-central-pacific.md) |
| `wpac_guam_andersen_afb` | Andersen Air Force Base | United States Air Force | air_base | populate_small | [03](register/03-west-central-pacific.md) |
| `wpac_guam_dla_distribution` | DLA Distribution Guam | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [03](register/03-west-central-pacific.md) |
| `cpac_pearl_harbor_dla_distribution` | DLA Distribution Pearl Harbor | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [03](register/03-west-central-pacific.md) |
| `io_diego_garcia_nsf` | Naval Support Facility Diego Garcia | United States Navy | mixed_base | populate | [04](register/04-australia-indian-ocean.md) |
| `glob_us_afloat_prepositioning_fleet` | Afloat Prepositioning Fleet (APF) | United States | anchorage_prepositioning | abstract_logistics_only | [04](register/04-australia-indian-ocean.md) |
| `aus_stirling_hmas_stirling` | HMAS Stirling | Royal Australian Navy | naval_base | populate | [04](register/04-australia-indian-ocean.md) |
| `aus_tindal_raaf` | RAAF Base Tindal | Royal Australian Air Force | air_base | populate_small | [04](register/04-australia-indian-ocean.md) |
| `me_bahrain_nsa_bahrain` | Naval Support Activity Bahrain | United States Navy | headquarters_command | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `me_bahrain_muharraq_airfield` | Muharraq Airfield | Not stated. Aviation assets supporting NSA Bahra | air_base | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `me_uae_jebel_ali_port` | Jebel Ali Port Facility | Not stated in R03:42. Host United Arab Emirates. | port_commercial (assumed) | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `me_bahrain_dla_distribution` | DLA Distribution Bahrain | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [05](register/05-gulf-horn-of-africa.md) |
| `hoa_djibouti_camp_lemonnier` | Camp Lemonnier | United States | mixed_base | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `hoa_djibouti_pla_support_base` | PLA Support Base (Djibouti) | China | logistics_centre | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `hoa_djibouti_fr_ba188_heron` | Base Aérienne 188 / Héron naval base (Djibouti) - report naming | France | mixed_base | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `hoa_djibouti_jp_base` | Japanese defense force base, Djibouti (unnamed in R01) | Japan | mixed_base | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `hoa_djibouti_it_base` | Italian defense force base, Djibouti (unnamed in R01) | Italy | mixed_base | populate_small | [05](register/05-gulf-horn-of-africa.md) |
| `med_rota_naval_station` | Naval Station Rota | United States Navy | naval_base | populate | [06](register/06-mediterranean-europe.md) |
| `med_naples_nsa_naples` | Naval Support Activity Naples | United States Navy | headquarters_command | context_only | [06](register/06-mediterranean-europe.md) |
| `med_sigonella_nas_sigonella` | Naval Air Station Sigonella | United States Navy | naval_air_station | populate | [06](register/06-mediterranean-europe.md) |
| `med_sigonella_dla_distribution` | DLA Distribution Sigonella | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [06](register/06-mediterranean-europe.md) |
| `med_souda_bay_nsa` | Naval Support Activity Souda Bay | United States Navy | pending_mixed (fidelity fix: R03:44 does not say naval pier, airfield or both) | populate_small | [06](register/06-mediterranean-europe.md) |
| `med_akrotiri_raf` | RAF Akrotiri | United Kingdom, Royal Air Force | air_base | populate_small | [06](register/06-mediterranean-europe.md) |
| `eur_deveselu_nsf_aegis_ashore` | Naval Support Facility Deveselu | United States Navy | fixed_defence | context_only | [06](register/06-mediterranean-europe.md) |
| `eur_redzikowo_nsf_aegis_ashore` | Naval Support Facility Redzikowo | United States Navy | fixed_defence | context_only | [06](register/06-mediterranean-europe.md) |
| `eur_germersheim_dla_distribution_europe` | DLA Distribution Europe (Germersheim) | US Defense Logistics Agency | distribution_depot | abstract_logistics_only | [06](register/06-mediterranean-europe.md) |
| `reserve:us_sealift` | World-level US sealift reserve (not a register node) | US strategic sealift hull | world_reserve | reserve_only | [06](register/06-mediterranean-europe.md) |
| `chn_hainan_yulin_naval_base` | Yulin Naval Base | PLA Navy | naval_base | populate | [07](register/07-china-maritime.md) |
| `chn_hainan_longpo_naval_base` | Longpo Naval Base | PLA Navy | naval_base | populate_small | [07](register/07-china-maritime.md) |
| `chn_hainan_lingshui_airbase` | Lingshui Airbase | China | naval_air_station | populate | [07](register/07-china-maritime.md) |
| `chn_zhejiang_ningbo_naval_base` | Ningbo Naval Base | PLA Navy | naval_base | populate | [07](register/07-china-maritime.md) |
| `chn_jlsf_wuhan_base` | Wuhan Joint Logistics Support Base | PLA Joint Logistics Support Force | headquarters_command | abstract_logistics_only | [08](register/08-china-logistics.md) |
| `chn_jlsf_wuxi_jlsc` | Wuxi Joint Logistics Support Center | PLA Joint Logistics Support Force | logistics_centre | abstract_logistics_only | [08](register/08-china-logistics.md) |
| `chn_jlsf_guilin_jlsc` | Guilin Joint Logistics Support Center | PLA Joint Logistics Support Force | logistics_centre | abstract_logistics_only | [08](register/08-china-logistics.md) |
| `chn_jlsf_xining_jlsc` | Xining Joint Logistics Support Center | PLA Joint Logistics Support Force | logistics_centre | abstract_logistics_only | [08](register/08-china-logistics.md) |
| `chn_jlsf_shenyang_jlsc` | Shenyang Joint Logistics Support Center | PLA Joint Logistics Support Force | logistics_centre | abstract_logistics_only | [08](register/08-china-logistics.md) |
| `chn_jlsf_zhengzhou_jlsc` | Zhengzhou Joint Logistics Support Center | PLA Joint Logistics Support Force | logistics_centre | abstract_logistics_only | [08](register/08-china-logistics.md) |
| `seasia_laos_ban_keun_airport` | Ban Keun Airport (joint China-Laos aviation training centre claim) | China and Laos | research_lead | do_not_populate | [08](register/08-china-logistics.md) |
| `hn_kola_olenya_airbase` | Olenya Airbase | Russian Long-Range Aviation | air_base | populate | [09](register/09-russia.md) |
| `rus_engels2_airbase` | Engels-2 Airbase | Russian Aerospace Forces | air_base | populate_small | [09](register/09-russia.md) |
| `rus_ukrainka_airbase` | Ukrainka Airbase | Russia | air_base | populate_small | [09](register/09-russia.md) |
| `rus_belaya_airbase` | Belaya Airbase | Russia | air_base | populate_small | [09](register/09-russia.md) |
| `hn_evenes_air_station` | Evenes Air Station | Norway - Royal Norwegian Air Force, 133 Air Wing | air_base | populate | [10](register/10-japan-norway-patrol.md) |
| `jpn_kanoya_air_base` | Kanoya Air Base | Japan Maritime Self-Defense Force - Fleet Air Wi | naval_air_station | populate | [10](register/10-japan-norway-patrol.md) |
| `jpn_atsugi_naf` | Naval Air Facility Atsugi | Japan Maritime Self-Defense Force - Fleet Air Wi | naval_air_station | populate | [10](register/10-japan-norway-patrol.md) |
| `jpn_okinawa_naha` | Naha (JMSDF air station, Okinawa) | Japan Maritime Self-Defense Force - Fleet Air Wi | naval_air_station | populate | [10](register/10-japan-norway-patrol.md) |
| `satl_falklands_raf_mount_pleasant` | RAF Mount Pleasant | United Kingdom | air_base | populate_small | [11](register/11-south-atlantic-france.md) |
| `satl_falklands_mare_harbour` | Mare Harbour | United Kingdom | naval_base | populate_small | [11](register/11-south-atlantic-france.md) |
| `eur_brest_ile_longue` | Île Longue | France | naval_base | context_only | [11](register/11-south-atlantic-france.md) |
