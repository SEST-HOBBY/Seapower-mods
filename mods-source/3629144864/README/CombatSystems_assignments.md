# Combat system assignments and profile descriptions

Updated 2026-10-01 from the installed Euromod INI files: **54 custom profiles and 162 ship overrides**. Two existing base-game profiles are also referenced. Ship filenames remain exact identifiers; combat-system names use the current neutral IDs.

See [Euromod Combat Systems](README_CombatSystems.md) for setup, field meanings, naming conventions and limitations. The tables describe the configured overrides, not a guarantee that every corresponding ship pack is enabled.

## Profile descriptions and values

Descriptions below express the intended gameplay role. Values come directly from `systems/combatsystems.ini`. All custom profiles have `SignalProcessingBonus=0`. `Tier / source` shows `DatalinkTier` and `DatalinkSource`; `Ships` counts installed overrides using the profile. Equal values do not imply identical real-world equipment.

| Profile ID | Intended role | ReactionTime | CICSlots | EvaluationSlots | Tier / source | Ships |
|---|---|---|---:|---:|---|---:|
| `AEGIS_BL5` | AEGIS BL5: follows the existing eu_AEGIS_BL5 sensor in the mod, including grouped historical fits. | VeryFast | 120 | 4 | 5 / True | 17 |
| `AEGIS_BL9` | AEGIS BL9: modernized SPY-1 ships; follows eu_AEGIS_BL9. No new missile guidance or CEC capability is implied. | VeryFast | 160 | 6 | 5 / True | 33 |
| `AEGIS_BL10` | AEGIS BL10: SPY-6 and concept fits. Future fits are gameplay assumptions. | VeryFast | 200 | 8 | 5 / True | 4 |
| `TSCE` | Integrated combat direction; TSCE family, shared across weapon configurations. | VeryFast | 144 | 6 | 5 / True | 2 |
| `SSDS_Carrier` | Carrier-scale integrated self-defence and air-picture coordination. | Fast | 180 | 5 | 5 / True | 1 |
| `NTDS_Amphibious` | Amphibious combat-direction profile with legacy SPS-48/49 and Mk23 TAS. | Fast | 80 | 3 | 5 / True | 1 |
| `COMBATSS21` | Surface-warfare combat management with a compact CIC. | Fast | 48 | 3 | 5 / True | 2 |
| `CMS_Multirole_MLU` | Generic multirole modernization profile for the mod-specific SPY-5/JUWL fit. | Fast | 48 | 3 | 5 / True | 1 |
| `SATIR` | SATIR-era combat direction with LW08/SMART-S/STIR. | Fast | 48 | 3 | 5 / True | 2 |
| `SATIR_Refit` | Intermediate SATIR refit retaining the original sensor architecture. | Fast | 64 | 4 | 5 / True | 2 |
| `9LV_Multirole_MLU` | Modernized multirole 9LV profile with Sea Giraffe 4A/1X and CEROS 200. | VeryFast | 96 | 5 | 5 / True | 2 |
| `CMS_AAW_APAR` | Area-air-defence combat direction with APAR and SMART-L. | VeryFast | 120 | 5 | 5 / True | 2 |
| `CMS_AAW_APAR_MLU` | Modernized APAR area-air-defence profile; upgrade performance is a gameplay assumption. | VeryFast | 144 | 6 | 5 / True | 1 |
| `ANCS` | ANCS profile for expeditionary surface warfare and local defence. | Fast | 80 | 4 | 5 / True | 1 |
| `ANCS_MLU` | Modernized ANCS profile with assumed improvements in combat-direction automation. | VeryFast | 96 | 5 | 5 / True | 1 |
| `CMS_Compact` | Compact combat-direction profile; no area-air-defence capability is added. | Fast | 32 | 3 | 5 / True | 2 |
| `CMS_Compact_Enhanced` | Enhanced compact profile with TRS-4D and improved parallel evaluation. | Fast | 48 | 4 | 5 / True | 2 |
| `SEWACO_AAW` | SEWACO area-air-defence profile with APAR and SMART-L. | VeryFast | 120 | 5 | 5 / True | 1 |
| `SEWACO_AAW_MLU` | Modernized SEWACO area-air-defence profile with APAR Block 2 and SMART-L MM. | VeryFast | 160 | 6 | 5 / True | 1 |
| `SEWACO_Multirole` | Baseline SEWACO multirole combat direction. | Fast | 48 | 3 | 5 / True | 1 |
| `SEWACO_Multirole_MLU` | Intermediate SEWACO multirole modernization. | Fast | 64 | 4 | 5 / True | 1 |
| `SEWACO_Multirole_Enhanced` | Enhanced SEWACO multirole profile with NS100 and revised directors. | VeryFast | 80 | 4 | 5 / True | 1 |
| `CMS_ASW_Integrated` | Integrated ASW combat-management profile for a future mod fit; gameplay assumption. | VeryFast | 120 | 5 | 5 / True | 1 |
| `TACTICOS_OPV` | TACTICOS patrol-vessel tactical picture and local weapon direction. | Fast | 32 | 2 | 5 / True | 1 |
| `MCM_CMS` | Mine-warfare and local-defence combat-direction profile. | Fast | 24 | 2 | 5 / True | 1 |
| `CMS_AAW_PAAMS` | PAAMS-era area-air-defence profile; national implementations share this gameplay tier. | VeryFast | 128 | 5 | 5 / True | 3 |
| `ATHENA` | ATHENA-family combat direction, shared general-purpose and ASW baseline. | VeryFast | 96 | 4 | 5 / True | 2 |
| `ATHENA_Mk2` | ATHENA Mk2-family combat direction, shared across weapon configurations. | VeryFast | 128 | 6 | 5 / True | 2 |
| `OYQ_Integrated` | Integrated OYQ-family profile for OPY-1 and modern ASW equipment; no specific revision implied. | VeryFast | 96 | 5 | 5 / True | 1 |
| `CFLEX` | C-Flex combat-direction profile. | VeryFast | 120 | 5 | 5 / True | 1 |
| `CFLEX_MLU` | Modernized C-Flex profile with assumed improvements in parallel evaluation. | VeryFast | 144 | 6 | 5 / True | 1 |
| `CMS_FastAttack` | Compact combat-direction profile for fast attack craft. | Fast | 32 | 3 | 5 / True | 1 |
| `9LV_Compact` | Compact 9LV-family combat-management profile. | Fast | 32 | 3 | 5 / True | 1 |
| `9LV_Compact_MLU` | Modernized compact 9LV-family combat-direction profile. | VeryFast | 48 | 4 | 5 / True | 1 |
| `CMS_AAW_SeaViper` | Sea Viper area-air-defence combat-direction profile. | VeryFast | 128 | 5 | 5 / True | 2 |
| `CMS_AAW_SeaViper_Upgrade` | Upgraded Sea Viper combat-direction profile; performance is a gameplay assumption. | VeryFast | 144 | 6 | 5 / True | 1 |
| `DNA` | Early DNA-family combat direction with Sea Wolf. | Fast | 48 | 3 | 5 / True | 1 |
| `DNA_MLU` | Intermediate DNA-family modernization with Sea Wolf. | Fast | 64 | 4 | 5 / True | 1 |
| `CMS_SeaCeptor` | Modern combat-direction profile with Type 997 and Sea Ceptor. | VeryFast | 80 | 4 | 5 / True | 1 |
| `CMS_Amphibious` | Amphibious command and air-picture coordination, shared across ASW loadouts. | Fast | 96 | 4 | 5 / True | 4 |
| `CMS_Patrol` | Patrol-vessel combat-direction profile. | Fast | 24 | 2 | 5 / True | 1 |
| `SENIT_Carrier` | Carrier-scale combat direction in the SENIT family. | Fast | 180 | 5 | 5 / True | 1 |
| `SENIT_Amphibious` | Amphibious command and local self-defence in the SENIT family. | Fast | 96 | 4 | 5 / True | 1 |
| `SETIS_ASW` | SETIS-family ASW combat-direction profile. | VeryFast | 96 | 4 | 5 / True | 1 |
| `SETIS_ASW_MLU` | Modernized SETIS-family ASW profile. | VeryFast | 112 | 5 | 5 / True | 1 |
| `SETIS_AAW` | SETIS area-air-defence profile with Herakles+ as represented in the mod. | VeryFast | 144 | 6 | 5 / True | 1 |
| `SETIS_Integrated` | Integrated SETIS-family combat direction with Sea Fire. | VeryFast | 144 | 6 | 5 / True | 1 |
| `CMS_LocalDefence` | Local-defence combat-direction profile for patrol duties. | Fast | 32 | 2 | 5 / True | 1 |
| `CMS_LocalDefence_Refit` | Modernized local-defence profile with increased evaluation capacity. | Fast | 48 | 3 | 5 / True | 2 |
| `Submarine_Analog` | Generic early submarine fire-control profile. Local-only is a gameplay assumption, not a statement about radio equipment. | Slow | 8 | 1 | 1 / False | 2 |
| `Submarine_Digital` | Generic digital submarine fire-control profile; local picture, no continuous fleet track publication. | Medium | 24 | 2 | 1 / False | 3 |
| `Submarine_Integrated` | Generic modern integrated submarine combat management; sonar processing remains sensor-defined. | Fast | 40 | 3 | 1 / False | 17 |
| `SmallCraft_Local` | Small landing/support craft local plot; no automatic fleet-picture distribution. | Slow | 4 | 1 | 1 / False | 18 |
| `USV_LocalControl` | Conservative USV local sensor/weapon-control abstraction; remote-control/network simulation is outside this profile. | Fast | 8 | 2 | 1 / False | 1 |

## Reused base-game profiles

These profiles are read from the base game rather than defined by this Euromod file. Values below reflect the installed original configuration when this reference was updated.

| Profile ID | Intended assignment | ReactionTime | CICSlots | EvaluationSlots | Tier / source | SignalProcessingBonus | Ships |
|---|---|---|---:|---:|---|---:|---:|
| `AEGIS_Mk7` | Early AEGIS concept fit. | VeryFast | 100 | 4 | 5 / True | 0 | 1 |
| `NTDS_TAS` | Spruance fits using the existing NTDS/TAS gameplay profile. | Fast | 54 | 3 | 5 / True | 1 | 3 |

## Ship assignments

Each ship ID links to its installed override. Its `SystemName` must exactly match the listed profile ID. Current Burke hull/fit IDs replace the earlier year/group IDs; the Spruance VLS mod target is `usn_dd_spruance_eu_vls`.

### Denmark (3)

| Ship INI ID | Combat-system profile |
|---|---|
| [hdms_iver_huitfeldt](../vessels_overwrite/hdms_iver_huitfeldt_CombatSystems_OVWR.ini) | `CFLEX` |
| [hdms_iver_huitfeldt_mlu](../vessels_overwrite/hdms_iver_huitfeldt_mlu_CombatSystems_OVWR.ini) | `CFLEX_MLU` |
| [hdms_tug_alsin](../vessels_overwrite/hdms_tug_alsin_CombatSystems_OVWR.ini) | `SmallCraft_Local` |

### France (30)

| Ship INI ID | Combat-system profile |
|---|---|
| [fr_cvn_charles-de-gaulle](../vessels_overwrite/fr_cvn_charles-de-gaulle_CombatSystems_OVWR.ini) | `SENIT_Carrier` |
| [fr_ddg_horizon](../vessels_overwrite/fr_ddg_horizon_CombatSystems_OVWR.ini) | `CMS_AAW_PAAMS` |
| [fr_edar_afv-ifv](../vessels_overwrite/fr_edar_afv-ifv_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edar_apc](../vessels_overwrite/fr_edar_apc_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edar_artillery](../vessels_overwrite/fr_edar_artillery_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edar_empty](../vessels_overwrite/fr_edar_empty_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edar_tank](../vessels_overwrite/fr_edar_tank_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edar_vl](../vessels_overwrite/fr_edar_vl_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edas_afv-ifv](../vessels_overwrite/fr_edas_afv-ifv_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edas_apc](../vessels_overwrite/fr_edas_apc_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edas_artillery](../vessels_overwrite/fr_edas_artillery_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edas_empty](../vessels_overwrite/fr_edas_empty_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edas_tank](../vessels_overwrite/fr_edas_tank_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_edas_vl](../vessels_overwrite/fr_edas_vl_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_fdi_amiral_ronarc'h](../vessels_overwrite/fr_fdi_amiral_ronarc'h_CombatSystems_OVWR.ini) | `SETIS_Integrated` |
| [fr_ffg_aquitaine_asw](../vessels_overwrite/fr_ffg_aquitaine_asw_CombatSystems_OVWR.ini) | `SETIS_ASW` |
| [fr_ffg_aquitaine_modernized_aaw](../vessels_overwrite/fr_ffg_aquitaine_modernized_aaw_CombatSystems_OVWR.ini) | `SETIS_AAW` |
| [fr_ffg_aquitaine_modernized_asw](../vessels_overwrite/fr_ffg_aquitaine_modernized_asw_CombatSystems_OVWR.ini) | `SETIS_ASW_MLU` |
| [fr_ffg_lafayette_modernized](../vessels_overwrite/fr_ffg_lafayette_modernized_CombatSystems_OVWR.ini) | `CMS_LocalDefence_Refit` |
| [fr_ffg_lafayette_version_opv](../vessels_overwrite/fr_ffg_lafayette_version_opv_CombatSystems_OVWR.ini) | `CMS_LocalDefence` |
| [fr_ffg_lafayette_version_opv_modernized](../vessels_overwrite/fr_ffg_lafayette_version_opv_modernized_CombatSystems_OVWR.ini) | `CMS_LocalDefence_Refit` |
| [fr_lhd_mistral](../vessels_overwrite/fr_lhd_mistral_CombatSystems_OVWR.ini) | `SENIT_Amphibious` |
| [fr_raft_fm](../vessels_overwrite/fr_raft_fm_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_raft_sof_black](../vessels_overwrite/fr_raft_sof_black_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_raft_sof_bme](../vessels_overwrite/fr_raft_sof_bme_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_ss_psm3g](../vessels_overwrite/fr_ss_psm3g_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [fr_ssbn_triomphant](../vessels_overwrite/fr_ssbn_triomphant_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [fr_ssn_rubis](../vessels_overwrite/fr_ssn_rubis_CombatSystems_OVWR.ini) | `Submarine_Digital` |
| [fr_ssn_suffren](../vessels_overwrite/fr_ssn_suffren_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [fr_ssn_suffren_dds](../vessels_overwrite/fr_ssn_suffren_dds_CombatSystems_OVWR.ini) | `Submarine_Integrated` |

### Germany (19)

| Ship INI ID | Combat-system profile |
|---|---|
| [ger_ffg_f123_1994](../vessels_overwrite/ger_ffg_f123_1994_CombatSystems_OVWR.ini) | `SATIR` |
| [ger_ffg_f123_2007](../vessels_overwrite/ger_ffg_f123_2007_CombatSystems_OVWR.ini) | `SATIR` |
| [ger_ffg_f123_2012_MVP](../vessels_overwrite/ger_ffg_f123_2012_MVP_CombatSystems_OVWR.ini) | `SATIR_Refit` |
| [ger_ffg_f123_2015_essm](../vessels_overwrite/ger_ffg_f123_2015_essm_CombatSystems_OVWR.ini) | `SATIR_Refit` |
| [ger_ffg_f123_2025_mlu](../vessels_overwrite/ger_ffg_f123_2025_mlu_CombatSystems_OVWR.ini) | `9LV_Multirole_MLU` |
| [ger_ffg_f123_2030_mlu_high](../vessels_overwrite/ger_ffg_f123_2030_mlu_high_CombatSystems_OVWR.ini) | `9LV_Multirole_MLU` |
| [ger_ffg_f124](../vessels_overwrite/ger_ffg_f124_CombatSystems_OVWR.ini) | `CMS_AAW_APAR` |
| [ger_ffg_f124_ASMD](../vessels_overwrite/ger_ffg_f124_ASMD_CombatSystems_OVWR.ini) | `CMS_AAW_APAR` |
| [ger_ffg_f124_MLU](../vessels_overwrite/ger_ffg_f124_MLU_CombatSystems_OVWR.ini) | `CMS_AAW_APAR_MLU` |
| [ger_ffg_f125](../vessels_overwrite/ger_ffg_f125_CombatSystems_OVWR.ini) | `ANCS` |
| [ger_ffg_f125_MLU](../vessels_overwrite/ger_ffg_f125_MLU_CombatSystems_OVWR.ini) | `ANCS_MLU` |
| [ger_ffg_f127](../vessels_overwrite/ger_ffg_f127_CombatSystems_OVWR.ini) | `AEGIS_BL10` |
| [ger_ffg_f127_batch2](../vessels_overwrite/ger_ffg_f127_batch2_CombatSystems_OVWR.ini) | `AEGIS_BL10` |
| [ger_fsg_k130_batch1_early](../vessels_overwrite/ger_fsg_k130_batch1_early_CombatSystems_OVWR.ini) | `CMS_Compact` |
| [ger_fsg_k130_batch1_late](../vessels_overwrite/ger_fsg_k130_batch1_late_CombatSystems_OVWR.ini) | `CMS_Compact` |
| [ger_fsg_k130_batch2](../vessels_overwrite/ger_fsg_k130_batch2_CombatSystems_OVWR.ini) | `CMS_Compact_Enhanced` |
| [ger_fsg_k130_batch2_late](../vessels_overwrite/ger_fsg_k130_batch2_late_CombatSystems_OVWR.ini) | `CMS_Compact_Enhanced` |
| [ger_ssk_type_212a_batch1](../vessels_overwrite/ger_ssk_type_212a_batch1_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [ger_ssk_type_212a_batch1_upgraded](../vessels_overwrite/ger_ssk_type_212a_batch1_upgraded_CombatSystems_OVWR.ini) | `Submarine_Integrated` |

### Italy (7)

| Ship INI ID | Combat-system profile |
|---|---|
| [ita_ddg_orizzonte](../vessels_overwrite/ita_ddg_orizzonte_CombatSystems_OVWR.ini) | `CMS_AAW_PAAMS` |
| [ita_ddg_orizzonte_18](../vessels_overwrite/ita_ddg_orizzonte_18_CombatSystems_OVWR.ini) | `CMS_AAW_PAAMS` |
| [ita_ffg_fremm](../vessels_overwrite/ita_ffg_fremm_CombatSystems_OVWR.ini) | `ATHENA` |
| [ita_ffg_fremm_asw](../vessels_overwrite/ita_ffg_fremm_asw_CombatSystems_OVWR.ini) | `ATHENA` |
| [ita_ffg_ppa](../vessels_overwrite/ita_ffg_ppa_CombatSystems_OVWR.ini) | `ATHENA_Mk2` |
| [ita_ffg_ppa_evo](../vessels_overwrite/ita_ffg_ppa_evo_CombatSystems_OVWR.ini) | `ATHENA_Mk2` |
| [ita_ssk_todaro_batch1](../vessels_overwrite/ita_ssk_todaro_batch1_CombatSystems_OVWR.ini) | `Submarine_Integrated` |

### Japan (3)

| Ship INI ID | Combat-system profile |
|---|---|
| [jmsdf_dd_asahi](../vessels_overwrite/jmsdf_dd_asahi_CombatSystems_OVWR.ini) | `OYQ_Integrated` |
| [jmsdf_ddg_atago](../vessels_overwrite/jmsdf_ddg_atago_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [jmsdf_ddg_maya](../vessels_overwrite/jmsdf_ddg_maya_CombatSystems_OVWR.ini) | `AEGIS_BL9` |

### Netherlands (10)

| Ship INI ID | Combat-system profile |
|---|---|
| [rnn_ddg_zeven](../vessels_overwrite/rnn_ddg_zeven_CombatSystems_OVWR.ini) | `SEWACO_AAW` |
| [rnn_ddg_zeven_mlu](../vessels_overwrite/rnn_ddg_zeven_mlu_CombatSystems_OVWR.ini) | `SEWACO_AAW_MLU` |
| [rnn_ffg_Van_Galen](../vessels_overwrite/rnn_ffg_Van_Galen_CombatSystems_OVWR.ini) | `CMS_ASW_Integrated` |
| [rnn_ffg_hol](../vessels_overwrite/rnn_ffg_hol_CombatSystems_OVWR.ini) | `TACTICOS_OPV` |
| [rnn_ffg_karel](../vessels_overwrite/rnn_ffg_karel_CombatSystems_OVWR.ini) | `SEWACO_Multirole` |
| [rnn_ffg_karel_eol](../vessels_overwrite/rnn_ffg_karel_eol_CombatSystems_OVWR.ini) | `SEWACO_Multirole_Enhanced` |
| [rnn_ffg_karel_mlu](../vessels_overwrite/rnn_ffg_karel_mlu_CombatSystems_OVWR.ini) | `SEWACO_Multirole_MLU` |
| [rnn_mcm_city](../vessels_overwrite/rnn_mcm_city_CombatSystems_OVWR.ini) | `MCM_CMS` |
| [rnn_ss_dolfijn](../vessels_overwrite/rnn_ss_dolfijn_CombatSystems_OVWR.ini) | `Submarine_Analog` |
| [rnn_usv_12m](../vessels_overwrite/rnn_usv_12m_CombatSystems_OVWR.ini) | `USV_LocalControl` |

### Norway (2)

| Ship INI ID | Combat-system profile |
|---|---|
| [knm_cb90](../vessels_overwrite/knm_cb90_CombatSystems_OVWR.ini) | `SmallCraft_Local` |
| [knm_cor_skjold](../vessels_overwrite/knm_cor_skjold_CombatSystems_OVWR.ini) | `CMS_FastAttack` |

### Sweden (2)

| Ship INI ID | Combat-system profile |
|---|---|
| [swe_fsg_visby_v5](../vessels_overwrite/swe_fsg_visby_v5_CombatSystems_OVWR.ini) | `9LV_Compact` |
| [swe_fsg_visby_v6](../vessels_overwrite/swe_fsg_visby_v6_CombatSystems_OVWR.ini) | `9LV_Compact_MLU` |

### United Kingdom (11)

| Ship INI ID | Combat-system profile |
|---|---|
| [rn_ddg_type45](../vessels_overwrite/rn_ddg_type45_CombatSystems_OVWR.ini) | `CMS_AAW_SeaViper` |
| [rn_ddg_type45_22](../vessels_overwrite/rn_ddg_type45_22_CombatSystems_OVWR.ini) | `CMS_AAW_SeaViper` |
| [rn_ddg_type45_26](../vessels_overwrite/rn_ddg_type45_26_CombatSystems_OVWR.ini) | `CMS_AAW_SeaViper_Upgrade` |
| [rn_ff_type23](../vessels_overwrite/rn_ff_type23_CombatSystems_OVWR.ini) | `CMS_SeaCeptor` |
| [rn_ff_type23_early](../vessels_overwrite/rn_ff_type23_early_CombatSystems_OVWR.ini) | `DNA` |
| [rn_ff_type23_mlu](../vessels_overwrite/rn_ff_type23_mlu_CombatSystems_OVWR.ini) | `DNA_MLU` |
| [rn_lph_ocean](../vessels_overwrite/rn_lph_ocean_CombatSystems_OVWR.ini) | `CMS_Amphibious` |
| [rn_lph_ocean_asw](../vessels_overwrite/rn_lph_ocean_asw_CombatSystems_OVWR.ini) | `CMS_Amphibious` |
| [rn_lph_ocean_asw_00](../vessels_overwrite/rn_lph_ocean_asw_00_CombatSystems_OVWR.ini) | `CMS_Amphibious` |
| [rn_lph_ocean_asw_13](../vessels_overwrite/rn_lph_ocean_asw_13_CombatSystems_OVWR.ini) | `CMS_Amphibious` |
| [rn_opv_river_batch2](../vessels_overwrite/rn_opv_river_batch2_CombatSystems_OVWR.ini) | `CMS_Patrol` |

### United States (75)

| Ship INI ID | Combat-system profile |
|---|---|
| [usn_cg_ticonderoga_vls_1990](../vessels_overwrite/usn_cg_ticonderoga_vls_1990_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_cg_ticonderoga_vls_1996](../vessels_overwrite/usn_cg_ticonderoga_vls_1996_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_cg_ticonderoga_vls_2004](../vessels_overwrite/usn_cg_ticonderoga_vls_2004_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_cg_ticonderoga_vls_2011](../vessels_overwrite/usn_cg_ticonderoga_vls_2011_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_cg_ticonderoga_vls_2013](../vessels_overwrite/usn_cg_ticonderoga_vls_2013_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_cg_ticonderoga_vls_2018](../vessels_overwrite/usn_cg_ticonderoga_vls_2018_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_cg_ticonderoga_vls_2025](../vessels_overwrite/usn_cg_ticonderoga_vls_2025_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_cvn_nimitz_2025](../vessels_overwrite/usn_cvn_nimitz_2025_CombatSystems_OVWR.ini) | `SSDS_Carrier` |
| [usn_dd_spruance_eu_vls](../vessels_overwrite/usn_dd_spruance_eu_vls_CombatSystems_OVWR.ini) | `NTDS_TAS` |
| [usn_dd_spruance_mk71](../vessels_overwrite/usn_dd_spruance_mk71_CombatSystems_OVWR.ini) | `NTDS_TAS` |
| [usn_dd_spruance_ram](../vessels_overwrite/usn_dd_spruance_ram_CombatSystems_OVWR.ini) | `NTDS_TAS` |
| [usn_ddg-1000](../vessels_overwrite/usn_ddg-1000_CombatSystems_OVWR.ini) | `TSCE` |
| [usn_ddg-1000_cps](../vessels_overwrite/usn_ddg-1000_cps_CombatSystems_OVWR.ini) | `TSCE` |
| [usn_ddg_arleigh_concept](../vessels_overwrite/usn_ddg_arleigh_concept_CombatSystems_OVWR.ini) | `AEGIS_Mk7` |
| [usn_ddg_burke_f1_051](../vessels_overwrite/usn_ddg_burke_f1_051_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f1_051_early](../vessels_overwrite/usn_ddg_burke_f1_051_early_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f1_051_late](../vessels_overwrite/usn_ddg_burke_f1_051_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f1_052](../vessels_overwrite/usn_ddg_burke_f1_052_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f1_052_early](../vessels_overwrite/usn_ddg_burke_f1_052_early_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f1_052_late](../vessels_overwrite/usn_ddg_burke_f1_052_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f1_054](../vessels_overwrite/usn_ddg_burke_f1_054_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f1_054_early](../vessels_overwrite/usn_ddg_burke_f1_054_early_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f1_054_late](../vessels_overwrite/usn_ddg_burke_f1_054_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f1_062_late](../vessels_overwrite/usn_ddg_burke_f1_062_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f1_064_late](../vessels_overwrite/usn_ddg_burke_f1_064_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2_072](../vessels_overwrite/usn_ddg_burke_f2_072_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2_072_early](../vessels_overwrite/usn_ddg_burke_f2_072_early_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2_072_late](../vessels_overwrite/usn_ddg_burke_f2_072_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2_075_late](../vessels_overwrite/usn_ddg_burke_f2_075_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_079](../vessels_overwrite/usn_ddg_burke_f2a_079_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2a_079_late](../vessels_overwrite/usn_ddg_burke_f2a_079_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_080](../vessels_overwrite/usn_ddg_burke_f2a_080_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2a_080_late](../vessels_overwrite/usn_ddg_burke_f2a_080_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_081](../vessels_overwrite/usn_ddg_burke_f2a_081_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2a_081_late](../vessels_overwrite/usn_ddg_burke_f2a_081_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_084_late](../vessels_overwrite/usn_ddg_burke_f2a_084_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_085](../vessels_overwrite/usn_ddg_burke_f2a_085_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2a_085_late](../vessels_overwrite/usn_ddg_burke_f2a_085_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_088_laser](../vessels_overwrite/usn_ddg_burke_f2a_088_laser_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_089](../vessels_overwrite/usn_ddg_burke_f2a_089_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2a_089_late](../vessels_overwrite/usn_ddg_burke_f2a_089_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_091](../vessels_overwrite/usn_ddg_burke_f2a_091_CombatSystems_OVWR.ini) | `AEGIS_BL5` |
| [usn_ddg_burke_f2a_091_late](../vessels_overwrite/usn_ddg_burke_f2a_091_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_091_sewip](../vessels_overwrite/usn_ddg_burke_f2a_091_sewip_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_097](../vessels_overwrite/usn_ddg_burke_f2a_097_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_097_late](../vessels_overwrite/usn_ddg_burke_f2a_097_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_097_sewip](../vessels_overwrite/usn_ddg_burke_f2a_097_sewip_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_099](../vessels_overwrite/usn_ddg_burke_f2a_099_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_099_late](../vessels_overwrite/usn_ddg_burke_f2a_099_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_100_late](../vessels_overwrite/usn_ddg_burke_f2a_100_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_108](../vessels_overwrite/usn_ddg_burke_f2a_108_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_108_late](../vessels_overwrite/usn_ddg_burke_f2a_108_late_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_113](../vessels_overwrite/usn_ddg_burke_f2a_113_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_117](../vessels_overwrite/usn_ddg_burke_f2a_117_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f2a_119](../vessels_overwrite/usn_ddg_burke_f2a_119_CombatSystems_OVWR.ini) | `AEGIS_BL9` |
| [usn_ddg_burke_f3_125](../vessels_overwrite/usn_ddg_burke_f3_125_CombatSystems_OVWR.ini) | `AEGIS_BL10` |
| [usn_ddg_burke_f3_concept](../vessels_overwrite/usn_ddg_burke_f3_concept_CombatSystems_OVWR.ini) | `AEGIS_BL10` |
| [usn_ffg_oliver_hazard_perry_mlu](../vessels_overwrite/usn_ffg_oliver_hazard_perry_mlu_CombatSystems_OVWR.ini) | `CMS_Multirole_MLU` |
| [usn_lcs_freedom_suw_early](../vessels_overwrite/usn_lcs_freedom_suw_early_CombatSystems_OVWR.ini) | `COMBATSS21` |
| [usn_lcs_freedom_suw_late](../vessels_overwrite/usn_lcs_freedom_suw_late_CombatSystems_OVWR.ini) | `COMBATSS21` |
| [usn_lhd_wasp](../vessels_overwrite/usn_lhd_wasp_CombatSystems_OVWR.ini) | `NTDS_Amphibious` |
| [usn_ssbn_george_washington](../vessels_overwrite/usn_ssbn_george_washington_CombatSystems_OVWR.ini) | `Submarine_Analog` |
| [usn_ssgn_virginia_blk5_vpm](../vessels_overwrite/usn_ssgn_virginia_blk5_vpm_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_los_angeles_flt2_90](../vessels_overwrite/usn_ssn_los_angeles_flt2_90_CombatSystems_OVWR.ini) | `Submarine_Digital` |
| [usn_ssn_los_angeles_flt3_90](../vessels_overwrite/usn_ssn_los_angeles_flt3_90_CombatSystems_OVWR.ini) | `Submarine_Digital` |
| [usn_ssn_virginia_block1](../vessels_overwrite/usn_ssn_virginia_block1_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block1_2015](../vessels_overwrite/usn_ssn_virginia_block1_2015_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block1_2026](../vessels_overwrite/usn_ssn_virginia_block1_2026_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block2](../vessels_overwrite/usn_ssn_virginia_block2_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block2_2015](../vessels_overwrite/usn_ssn_virginia_block2_2015_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block2_2026](../vessels_overwrite/usn_ssn_virginia_block2_2026_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block3](../vessels_overwrite/usn_ssn_virginia_block3_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block3_2026](../vessels_overwrite/usn_ssn_virginia_block3_2026_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block4](../vessels_overwrite/usn_ssn_virginia_block4_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
| [usn_ssn_virginia_block5](../vessels_overwrite/usn_ssn_virginia_block5_CombatSystems_OVWR.ini) | `Submarine_Integrated` |
