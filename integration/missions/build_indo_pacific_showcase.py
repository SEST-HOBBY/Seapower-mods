#!/usr/bin/env python3
"""Generate SEST Indo-Pacific Land Assets: a clean save dense with the
collection's modern modded land units, placed on real ground.

A sandbox, not a campaign chapter. Northern Australia, Papua New Guinea,
eastern Indonesia, Timor-Leste, the Philippines and the South China Sea
features, September 2026, populated so you can walk the map and see how the
modern land units look and sit together - every SAM family, coastal battery,
ballistic-missile TEL, armour type, radar, airbase model and installation the
subscribed mods provide, arranged the way they would actually be deployed:

  BLUE (Taskforce1, player)  ADF and its partners: the northern RAAF bases,
       the US Marine rotation and a French battle group at Darwin, Pine Gap,
       the EDCA sites in the Philippines with Patriot, THAAD, Typhon and
       NMESIS, a JGSDF Type 12 detachment at Batanes, the PNG forward bases.
  RED  (Taskforce2)  PLA garrisons on the Spratly and Paracel bases, Chinese
       lodgements at the Belt-and-Road industrial parks of Halmahera and
       Sulawesi, a Russian air-defence regiment and Bastion battery at Biak,
       DF-21/26 batteries in Papua, a lodgement at Dili and Rabaul, and an
       Iranian-armed insurgent enclave in Mindanao.
  NEUTRAL  Indonesian, Malaysian, Bruneian, PNG and Timorese infrastructure:
       TNI bases, refineries, LNG plants, ports, bridges, the Timor Sea rigs.

Every asset is placed by real coordinates and nudged onto land with the land
mask (the reef bases and rigs are exempt - the mask does not know artificial
islands). The defences come from build_land_defence.py, so each site gets its
nation's kit in a realistic layout, and the whole file passes preflight.

Infrastructure and supply units are period-flexible (vanilla fuel farms,
warehouses and refineries stand in where no modern model exists); combat units
are modern wherever the collection has one.

    python3 integration/missions/build_indo_pacific_showcase.py            # write the mission
    python3 integration/missions/build_indo_pacific_showcase.py --density standard   # lighter defences
    python3 integration/missions/build_indo_pacific_showcase.py --report   # coverage of modded units
"""
import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_land_defence import (Mission, Planner, Geo, unit_info, pick_variant,    # noqa: E402
                                doctrine_for, find_sites, apply_groups, LAND)
from refine_civ_traffic import winning_file           # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = Path(__file__).resolve().parent
NAME = "SEST Indo-Pacific Land Assets"
OUT = MISSIONS / f"{NAME}.ini"
CLAT, CLON = -6.0, 130.0          # map datum: x = (lon-CLON)*60, z = (lat-CLAT)*60
Y_SEA = "220.4727"                # vanilla vessel-waypoint sea-level constant
DESCRIPTION = ("Sandbox: the collection's modern land assets laid out across northern Australia, "
               "PNG, Indonesia, Timor and the Philippines - RAAF bases with Patriot/THAAD/NASAMS, "
               "a French battle group and US Marines at Darwin, EDCA sites with Typhon and NMESIS, "
               "PLA reef bases with HQ-9B/YJ-12, a Russian S-400 regiment at Biak, DF-21/26 "
               "batteries in Papua, insurgent technicals in Mindanao, and neutral TNI bases, "
               "refineries and LNG plants. Walk the map and see how they sit.")

# ---------------------------------------------------------------------------
# Sites. groups = [(formation label, [unit id or (unit id, count)])]; the first
# unit of the first group stands at the coordinates, the rest spiral outward.
# posture drives build_land_defence's layers; mask=False for reefs and rigs.
# ---------------------------------------------------------------------------
SITES = []


def site(label, side, lat, lon, nation, groups, posture="none", coastal=False, mask=True,
         nation_key=None, threat=None, spread=0.25, composite=False, doctrine=None):
    SITES.append(dict(label=label, side=side, lat=lat, lon=lon, nation=nation, groups=groups,
                      posture=posture, coastal=coastal, mask=mask, nation_key=nation_key,
                      threat=threat, spread=spread, composite=composite, doctrine=doctrine))


TF1, TF2, NEU = "Taskforce1", "Taskforce2", "Neutral"

# ---------------- BLUE: northern Australia --------------------------------
site("RAAF Base Darwin", TF1, -12.4147, 130.8767, "australia",
     [("RAAF Base Darwin", ["airbase_raaf_darwin", "tgt_fueltanks_large", "tgt_ammo_depot_small",
                            "usa_car_hemtt", "usa_car_hemtt", "Ammo_Bunker"]),
      ("MRF-D Marine Rotation", [("usa_mlrs_m270a2", 2), ("usa_apc_aav7", 2), ("usa_car_hmmwv_tow", 2),
                                 "usa_car_hmmwv_m2", "usa_car_hemtt", "4tentgroup"])],
     posture="heavy", coastal=True, nation_key="australia", spread=0.45)
site("Robertson Barracks French Battle Group", TF1, -12.4290, 130.9530, "france",
     [("French Battle Group", [("fr_mbt_leclerc", 2), ("fr_ifv_vbci", 2), ("fr_afv_jaguar", 2),
                               ("fr_apc_griffon", 2), "fr_apc_serval", ("fr_spc_caesar", 2), "fr_mlrs_m270",
                               ("fr_vbl_recon", 2), "fr_vbl_milan", "fr_vbl_m2", "fr_apc_vab_ultima+milan",
                               "fr_apc_vab_top", "fr_apc_vab_recon", "fr_arv_amx10", "fr_vlfs",
                               "fr_apc_vab_ultima+minimi", "fr_apc_vab_ultima", "fr_apc_vab_top+milan",
                               "fr_apc_vab_milan", "fr_arv_amx10_shielding"]),
      ("SAMP/T Mamba Battery", [("fr_samp-t", 3), ("swe_spaa_ito_90m", 2)])],
     nation_key="france", spread=0.3)
site("Darwin East Arm Fuel Terminal", TF1, -12.4870, 130.8900, "australia",
     [("Darwin East Arm Fuel Terminal", [("tgt_fueltanks_large_brown", 2), "warehouses_2",
                                         "tgt_industry_buildings_1", "Oil_pump"])],
     nation_key="australia", spread=0.2)
site("HMAS Coonawarra", TF1, -12.4560, 130.8290, "australia",
     [("HMAS Coonawarra", ["nv_pt_boats_docks", "all_sosus", "civ_comm_buildings", "warehouses_1"])],
     posture="light", nation_key="australia", spread=0.2)
site("RAAF Base Tindal", TF1, -14.5211, 132.3778, "australia",
     [("RAAF Base Tindal", ["airbase_raaf_tindal", ("tgt_fueltanks_large", 2), "tgt_ammo_depot_small",
                            "Ammo_Bunker", "Bunker_2", "usa_car_hemtt"])],
     posture="heavy", nation_key="australia", spread=0.5)
site("RAAF Base Scherger", TF1, -12.6239, 142.0872, "australia",
     [("RAAF Base Scherger", ["airbase_raaf_scherger", "tgt_fueltanks_medium", "Ammo_Bunker", "4tentgroup",
                             "usa_sam_site_pac-3_small"])],
     posture="standard", nation_key="australia", spread=0.45)
site("RAAF Base Curtin", TF1, -17.5814, 123.8283, "australia",
     [("RAAF Base Curtin", ["airbase_raaf_curtin", "tgt_fueltanks_medium_sandy", "Ammo_Bunker", "FOB",
                           "usa_sam_site_pac-1_small"])],
     posture="standard", coastal=True, nation_key="australia", spread=0.45)
site("RAAF Base Learmonth", TF1, -22.2356, 114.0886, "australia",
     [("RAAF Base Learmonth", ["airbase_raaf_learmonth", "tgt_fueltanks_small_brown", "Ammo_Bunker"])],
     posture="light", coastal=True, nation_key="australia", spread=0.45)
site("RAAF Base Townsville", TF1, -19.2526, 146.7652, "australia",
     [("RAAF Base Townsville", ["airbase_raaf_townsville", "tgt_fueltanks_large", "Ammo_Bunker",
                               "usa_sam_site_pac-2_small"])],
     posture="standard", nation_key="australia", spread=0.45)
site("Lavarack Barracks 3rd Brigade", TF1, -19.3200, 146.7700, "australia",
     [("Lavarack Barracks 3rd Brigade", [("usa_mbt_abrams", 3), ("usa_ifv_bradley", 3), ("usa_spa_m109a2", 2),
                                         ("usa_apc_m113", 2), ("usa_car_hmmwv", 2), "usa_car_m923",
                                         "usa_mlrs_m270a2", "4tentgroup", "Ammo_Bunker"])],
     nation_key="australia", spread=0.25)
site("Gove Forward Radar Station", TF1, -12.2694, 136.8181, "australia",
     [("Gove Forward Radar Station", ["nato_ewr_station", "all_sosus", "dronesquad705_1", "tgt_refinery_small",
                                      "warehouses_1"])],
     posture="light", nation_key="australia", spread=0.25)
site("Weipa Bauxite Terminal", TF1, -12.6789, 141.9253, "australia",
     [("Weipa Bauxite Terminal", ["tgt_industry_buildings_2", "warehouses_3", "tgt_fueltanks_medium"])],
     nation_key="australia", spread=0.2)
site("Port Hedland Iron Ore Terminal", TF1, -20.3118, 118.5758, "australia",
     [("Port Hedland Iron Ore Terminal", ["tgt_industry_buildings_2_brown", "warehouses_3",
                                          ("tgt_fueltanks_medium_sandy", 2), "civ_radiostation"])],
     posture="light", coastal=True, nation_key="australia", spread=0.25)
site("HMAS Cairns", TF1, -16.9200, 145.7800, "australia",
     [("HMAS Cairns", ["nv_pt_boats_docks_small", "warehouses_1", "tgt_fueltanks_small", "airfield_small_1"])],
     posture="light", nation_key="australia", spread=0.3)
site("Joint Defence Facility Pine Gap", TF1, -23.7990, 133.7370, "australia",
     [("Joint Defence Facility Pine Gap", ["nato_large_ewr_station", "civ_comm_buildings", "us_cobra_dane_ewr",
                                           "civ_radiostation", "Bunker_2"])],
     posture="light", nation_key="australia", spread=0.25)

# ---------------- BLUE: Philippines (EDCA) and Japan ----------------------
site("Clark Air Base", TF1, 15.1859, 120.5603, "usa",
     [("Clark Air Base", ["usa_airbase_6thGEN", ("tgt_fueltanks_large", 2), "Ammo_Bunker", "warehouses_2",
                          "usa_car_hemtt"]),
      ("3rd MLR Combat Team", [("usa_apc_aav7", 2), ("usa_car_hmmwv_tow", 2), ("usa_mlrs_m270a2", 2),
                               "usa_car_hmmwv_m2", "FOB"]),
      ("Patriot Battalion Line-up", ["usa_mim_104_radar_65a", ("usa_mim_104f_mse_tel", 2), "usa_mim_104f_cri_tel",
                                     "usa_mim_104e_gem_t_tel", "usa_mim_104e_gem_c_tel", "usa_mim_104d_gem_tel",
                                     "usa_mim_104_radar_65", "usa_mim_104c_tel", "usa_mim_104b_tel",
                                     "usa_mim_104a_tel", "usa_mim_104_radar_53", "usa_car_hemtt"])],
     posture="heavy", nation_key="usa", spread=0.5)
site("Basa Air Base", TF1, 14.9865, 120.4926, "usa",
     [("Basa Air Base", ["airfield_us", "tgt_fueltanks_medium", "Ammo_Bunker"]),
      ("Basa PAC-2 Battery", ["usa_an_mpq-53_radar", ("usa_pac-2_1990_launcher", 2), ("usa_pac-1_launcher", 2)])],
     posture="standard", nation_key="usa", spread=0.4)
site("Subic Bay", TF1, 14.7944, 120.2714, "usa",
     [("Subic Bay", ["nv_pt_boats_docks", "warehouses_2", "tgt_fueltanks_large", "usa_car_hemtt",
                     "tgt_industry_buildings_3"])],
     posture="standard", coastal=True, nation_key="usa", spread=0.3)
site("Camp Aguinaldo Typhon Battery", TF1, 18.1781, 120.5316, "usa",
     [("Typhon Mid-Range Capability Battery", ["usa_mim-23_fcr", ("usa_tomahawk_launcher", 2),
                                                 "usa_tempest_launcher", "usa_car_hemtt", "FOB"])],
     posture="standard", nation_key="usa", spread=0.2)
site("Antonio Bautista Air Base", TF1, 9.7420, 118.7590, "usa",
     [("Antonio Bautista Air Base", ["usa_airbase", "tgt_fueltanks_medium", "Ammo_Bunker", "Bunker_2"])],
     posture="standard", coastal=True, nation_key="usa", spread=0.45)
site("Balabac EDCA Site", TF1, 7.9950, 117.0600, "usa",
     [("Balabac EDCA Site", ["FOB", "Bunker_2", ("usa_harpoon_launcher_RGM84D", 2), "nato_tps-27_radar",
                             "4tentgroup"])],
     posture="light", nation_key="usa", spread=0.2)
site("Pag-asa Island", TF1, 11.0517, 114.2833, "usa",
     [("Pag-asa Island", ["airfield_small_1", "nato_fps-20_radar", "Omega_trench", "usa_aaa_m42",
                          "civ_car_pickup_1983_assault_us", "Bunker_2"])],
     mask=False, nation_key="philippines", spread=0.15)
site("Western Mindanao Command", TF1, 6.9224, 122.0596, "usa",
     [("Western Mindanao Command", ["airfield_small_1", ("usa_apc_m113", 2), "usa_aaa_vulcan",
                                    ("usa_car_hmmwv_m2", 2), "nv_headquarters", "TBunkerTrench"])],
     posture="light", nation_key="philippines", spread=0.3)
site("Mactan-Benito Ebuen Air Base", TF1, 10.3075, 123.9790, "usa",
     [("Mactan-Benito Ebuen Air Base", ["airfield_us_large", "tgt_fueltanks_medium", "Ammo_Bunker"])],
     posture="light", nation_key="usa", spread=0.4)
site("Basco Forward Site", TF1, 20.4513, 121.9797, "usa",
     [("NMESIS Battery", [("usa_harpoon_launcher", 2), "nato_tps-27_radar", "FOB", "usa_car_hmmwv"]),
      ("JGSDF Type 12 Detachment", [("jp_12ssmht", 2), ("jsdf_sam_type81", 2), "jsdf_apc_type73",
                                    "jsdf_apc_type60"])],
     posture="light", nation_key="usa", spread=0.2)

# ---------------- BLUE: Papua New Guinea ---------------------------------
site("Port Moresby Jacksons", TF1, -9.4434, 147.2202, "australia",
     [("Port Moresby Jacksons", ["nato_large_pvo_airbase1", "tgt_fueltanks_large", "Ammo_Bunker",
                                 "warehouses_1"]),
      ("SLAMRAAM Battery", ["usa_SLAMRAAM_radar", ("usa_SLAMRAAM_launcher", 3)])],
     posture="standard", nation_key="australia", spread=0.45)
site("Lombrum Naval Base", TF1, -2.0333, 147.3667, "australia",
     [("Lombrum Naval Base", ["nv_pt_boats_docks", "tgt_fueltanks_medium", "warehouses_1", "nato_radar",
                              ("usa_harpoon_launcher", 2), "usa_harpoon_launcher_RGM84C"]),
      ("Momote Airfield", ["airfield_small_1", "Ammo_Bunker"])],
     posture="standard", nation_key="australia", spread=0.3)
site("Nadzab Forward Airfield", TF1, -6.5698, 146.7260, "usa",
     [("Nadzab Forward Airfield", ["airfield_a-10", "tgt_fueltanks_medium", "Ammo_Bunker", "FOB"])],
     posture="light", nation_key="usa", spread=0.4)
site("Wewak Forward Operating Base", TF1, -3.5838, 143.6692, "australia",
     [("Wewak Forward Operating Base", ["FOB", "4tentgroup", "Bunker_2", "usa_car_hmmwv_m2", "dronesquad705_1"])],
     posture="light", nation_key="australia", spread=0.2)
site("Markham River Bridge", TF1, -6.6300, 146.8500, "australia",
     [("Markham River Bridge", ["civ_tgt_bridge_3_part"])], nation_key="papua_new_guinea")

# ---------------- RED: South China Sea bases -----------------------------
site("Fiery Cross Reef", TF2, 9.5497, 112.8894, "china",
     [("Fiery Cross Reef", ["pla_airbase_modern", "pla_sam_site_hq-9_morden", ("pla_yj-12_tel", 2),
                            ("pla_yj-62_tel", 2), "pla_llq-120_radar", "pla_lcq-776_radar", "pla_ld-2000",
                            "pla_sam_site_hq-19", "tgt_fueltanks_large", "Ammo_Bunker", "warehouses_2"])],
     posture="heavy", mask=False, spread=0.4, threat=200)
site("Subi Reef", TF2, 10.9219, 114.0653, "china",
     [("Subi Reef", ["china_small_airbase", "pla_sam_site_hq-9", "pla_sam_site_hq-16b", "pla_hq-7b_radar",
                     ("pla_hq-7b_tel", 2), "pla_hq-64_search_radar", ("pla_hq-64_tel", 2),
                     ("china_yj12_launcher", 2), "pla_ylc-xx_radar", "pla_ht-233_radar", ("pla_hq-9_tel", 2),
                     "tgt_fueltanks_medium"])],
     posture="standard", mask=False, spread=0.35, threat=60)
site("Mischief Reef", TF2, 9.9000, 115.5333, "china",
     [("Mischief Reef", ["china_large_airbase_6thGEN", "pla_sam_site_hq-22a", "pla_sam_site_hq-6_small",
                         "pla_ld-3000", ("china_yj83_launcher", 2), "pla_sam_site_hq-11_small",
                         "pla_llq-780_radar", "pla_h-200a_radar", ("pla_hq-22a_tel", 2), "pla_slc-14_radar",
                         ("pla_hq-19_tel", 2), "tgt_fueltanks_large", "Ammo_Bunker"])],
     posture="standard", mask=False, spread=0.4, threat=90)
site("Woody Island", TF2, 16.8333, 112.3333, "china",
     [("Woody Island", ["china_large_airbase", "pla_sam_site_hq_15", "pla_sam_site_hq-7b_small",
                        ("pla_hq-11_tel", 2), "pla_sam_site_hq-16a", "pla_hq-16_fcr", ("pla_hq-16a_tel", 2),
                        "china_hq15_radar", ("china_hq15_launcher", 2), "pla_ylc-18_radar",
                        "tgt_fueltanks_medium", "warehouses_1"])],
     posture="standard", mask=False, spread=0.4, threat=150)

# ---------------- RED: lodgements in eastern Indonesia and Timor ---------
site("Biak Air Base", TF2, -1.1900, 136.1080, "russia",
     [("Biak Air Base", ["wp_airbase_modern", ("tgt_fueltanks_large", 2), "Ammo_Bunker", "wp_car_ural_command",
                         ("wp_car_ural", 2), "warehouses_2", "wp_sam_site_sa-21", "wp_sa-21_9m96e_tel"]),
      ("S-400 Regiment 2nd Battalion", ["wp_sa-21_flaplid", ("wp_sa-21_48n6e3_tel", 4), ("wp_sa-21_9m96e2_tel", 2),
                                        "wp_sa-21_40n6_tel", "wp_p-14_radar"]),
      ("Bastion Coastal Battery", ["wp_sa-10_flaplid", ("wp_k300p_tel", 3), ("wp_bal", 2)]),
      ("Iskander Battery", [("wp_ss-26_tel", 3), "wp_car_ural_command", "Ammo_Bunker"]),
      ("Motor Rifle Company", [("wp_mbt_t-72a", 2), ("wp_spaa_mt-lb_zu-23", 2), "wp_spaa_mt-lb_s-60",
                               "wp_spaa_mt-lb_2m-3", "ru_spaa_mt-lb_sosna", "wp_spa_2s3", "wp_mlrs_bm-21"])],
     posture="heavy", spread=0.5, threat=170)
site("Merauke Airlift Base", TF2, -8.5200, 140.4180, "china",
     [("Merauke Airlift Base", ["plaaf_airlift_airbase", "tgt_fueltanks_large", "Ammo_Bunker", "warehouses_1"]),
      ("DF-26 Brigade", [("pla_df-26b_tel", 3), "pla_df-21d_tel", "pla_df-21c_tel", "pla_apc_zbl-08",
                         "Ammo_Bunker"])],
     posture="standard", spread=0.45, threat=200)
site("Timika Logistics Hub", TF2, -4.5283, 136.8872, "china",
     [("Timika Logistics Hub", ["FOB", ("Ammo_Bunker", 2), "tgt_fueltanks_large", "warehouses_3",
                                ("pla_apc_zbl-08", 2), "4tentgroup", "pla_df-15_tel", "pla_cj-100_tel"])],
     posture="standard", spread=0.25, threat=180)
site("Sorong Coastal Battery", TF2, -0.8944, 131.2875, "china",
     [("Sorong Coastal Battery", ["nv_pt_boats_docks_small", ("pla_yj-12_tel", 2), ("pla_df-10a_tel", 2),
                                  ("pla_cj-10_tel", 2), "pla_ylc-18_radar", "tgt_fueltanks_small",
                                  "Bunker_2"])],
     posture="light", spread=0.25, threat=270)
site("Sentani Drone Site", TF2, -2.5769, 140.5163, "russia",
     [("Sentani Drone Site", ["airfield_wp", "dronesquad705_1", ("shahed_tel_black", 2), ("shahed_tel_white", 2),
                              "wp_car_ural_command", "Ammo_Bunker", "wp_scud_9k72", "wp_sejjil_tel",
                              "wp_sam_site_sa_20a"])],
     posture="standard", spread=0.35, threat=160)
site("Weda Bay Industrial Park", TF2, -0.3833, 127.9167, "china",
     [("Weda Bay Industrial Park", ["Coal_PowerPlant", "tgt_industry_buildings_3", "Oil_refinery",
                                    "warehouses_2", "tgt_fueltanks_medium"]),
      ("Weda Bay Garrison", [("pla_apc_zbl-08", 2), "pla_ifv_zbd-04a", ("pla_yj-62_tel", 2), "Omega_trench"])],
     posture="standard", spread=0.3, threat=250)
site("Morowali Industrial Park", TF2, -2.8167, 122.1667, "china",
     [("Morowali Industrial Park", ["Coal_PowerPlant", "tgt_industry_buildings_4", "tgt_refinery_small_2",
                                    "warehouses_3", "tgt_fueltanks_large_brown"]),
      ("PLA Combined Arms Battalion", [("pla_mbt_ztz-99a", 3), ("pla_mbt_ztz-96", 2), ("pla_ifv_zbd-04a", 3),
                                       ("pla_apc_zbl-08", 2), ("pla_spa_plz-83", 2), ("pla_phl-03", 2),
                                       "pla_td_ptz-89", "pla_td_ztl-11", "pla_td_hj-10_zbd-04a",
                                       "4tentgroup", "Ammo_Bunker"])],
     posture="standard", spread=0.3, threat=220)
site("Dili Lodgement", TF2, -8.5464, 125.5262, "china",
     [("Dili Lodgement", [("pla_apc_zbl-08", 3), ("pla_ifv_zbd-04a", 2), "pla_spa_plz-83", "Omega_trench",
                          "TBunkerTrench", ("pla_yj-62_tel", 2), "nv_headquarters", "Bunker_2"])],
     posture="standard", spread=0.3, threat=170)
site("Rabaul Expeditionary Lodgement", TF2, -4.3400, 152.3800, "russia",
     [("Rabaul Expeditionary Lodgement", ["wp_airbase_57", "nv_pt_boats_docks", "wp_sam_site_sa_20b",
                                          "wp_sam_site_sa_21",
                                          ("wp_bal", 2), "wp_asc_redut", "tgt_fueltanks_medium", "Ammo_Bunker",
                                          "wp_car_ural_command", ("wp_lt_pt-76", 2)])],
     posture="standard", spread=0.4, threat=110)
site("Marawi Insurgent Enclave", TF2, 7.9986, 124.2928, "terrorists",
     [("Marawi Insurgent Enclave", ["nv_headquarters", "civ_car_pickup_1983", "civ_car_pickup_1983_aa-8",
                                    "civ_car_pickup_1983_assault_civ", "civ_car_pickup_1983_bmp-1",
                                    "civ_car_pickup_1983_bmp-2", "civ_car_pickup_1983_fim-92",
                                    "civ_car_pickup_1983_m2", "civ_car_pickup_1983_m224",
                                    "civ_car_pickup_1983_medic", "civ_car_pickup_1983_sa-7",
                                    "civ_car_pickup_1983_tow", "civ_car_pickup_1983_type63",
                                    "civ_car_pickup_1983_ub-16", "civ_car_pickup_1983_zu-23",
                                    "wp_aaa_61K", "wp_sa-7_launcher", "4tentgroup", "Ammo_Bunker"])],
     nation_key="terrorists", spread=0.2)
site("Jolo Insurgent Camp", TF2, 6.0500, 121.0000, "terrorists",
     [("Jolo Insurgent Camp", ["4tentgroup", "civ_car_pickup_1983_assault_wp", "civ_car_pickup_1983_assault_rn",
                               "civ_car_pickup_1983_zu-23", "civ_car_pickup_1983_sa-7", "wp_zsu-57",
                               "nv_watchtower"])],
     nation_key="terrorists", spread=0.15)

# ---------------- NEUTRAL: Indonesia, Malaysia, Brunei, Timor Sea --------
site("Ranai Air Base (TNI-AU)", NEU, 3.9083, 108.3878, "export",
     [("Ranai Air Base (TNI-AU)", ["airfield_small_1", "nato_aaa_gdf", "wp_sa-13_launcher", "wp_p-18_radar",
                                   "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.35)
site("El Tari Air Base Kupang (TNI-AU)", NEU, -10.1716, 123.6711, "export",
     [("El Tari Air Base Kupang (TNI-AU)", ["airfield_small_1", "wp_spaa_mt-lb_s-60", "wp_aaa_ural_zu-23",
                                            "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.35)
site("Ambon Naval Base (TNI-AL)", NEU, -3.7103, 128.0890, "export",
     [("Ambon Naval Base (TNI-AL)", ["nv_pt_boats_docks_small", "warehouses_1", "nv_130mm_coastal_artillery",
                                     "wp_son-9", "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.25)
site("Hasanuddin Air Base Makassar (TNI-AU)", NEU, -5.0617, 119.5540, "export",
     [("Hasanuddin Air Base Makassar (TNI-AU)", ["airfield_us", "usa_aaa_m42", "raf_rapier_launcher",
                                                 "tgt_fueltanks_medium"])],
     nation_key="indonesia", spread=0.4)
site("Sam Ratulangi Air Base Manado (TNI-AU)", NEU, 1.5490, 124.9260, "export",
     [("Sam Ratulangi Air Base Manado (TNI-AU)", ["airfield_small_1", "wp_p-35_radar", "nv_s-60"])],
     nation_key="indonesia", spread=0.35)
site("Morotai Airfield", NEU, 2.0500, 128.3200, "export",
     [("Morotai Airfield", ["airfield_small_1", "warehouses_1"])], nation_key="indonesia", spread=0.35)
site("Balikpapan Refinery", NEU, -1.2654, 116.8312, "export",
     [("Balikpapan Refinery", ["Oil_refinery", ("Oil_pump", 2), ("tgt_fueltanks_large", 2),
                               "tgt_refinery_small_3", "warehouses_2"])],
     nation_key="indonesia", spread=0.25)
site("Bontang LNG Plant", NEU, 0.1167, 117.4833, "export",
     [("Bontang LNG Plant", ["tgt_refinery_small", ("tgt_fueltanks_medium", 2), "Oil_pump"])],
     nation_key="indonesia", spread=0.2)
site("Tangguh LNG Plant", NEU, -2.4000, 133.1500, "export",
     [("Tangguh LNG Plant", ["tgt_refinery_small_2", "tgt_fueltanks_medium_sandy", "Oil_pump",
                             "tgt_fueltanks_small_brown"])],
     nation_key="indonesia", spread=0.2)
site("Mahakam River Bridge", NEU, -0.5000, 117.1500, "export",
     [("Mahakam River Bridge", ["civ_tgt_bridge_arches_6_part"])], nation_key="indonesia")
site("Merauke Wharf Bridge", NEU, -8.4930, 140.3960, "export",
     [("Merauke Wharf Bridge", ["civ_tgt_bridge_6_part"])], nation_key="indonesia")
site("Sepanggar Naval Base (RMN)", NEU, 6.0667, 116.1000, "nato",
     [("Sepanggar Naval Base (RMN)", ["nv_pt_boats_docks", "nato_radar", "warehouses_1", "tgt_fueltanks_medium"])],
     nation_key="malaysia", spread=0.25)
site("Muara Fuel Depot", NEU, 5.0300, 115.0700, "nato",
     [("Muara Fuel Depot", ["tgt_fueltanks_large_brown", "Oil_pump", "warehouses_1"])],
     nation_key="brunei", spread=0.2)
site("Honiara Port", NEU, -9.4300, 160.0500, "export",
     [("Honiara Port", ["nv_pt_boats_docks", "warehouses_2", "tgt_fueltanks_small"])],
     nation_key="solomon_islands", spread=0.2)
for rig_label, la, lo in (("Bayu-Undan Platform", -11.0833, 126.5667), ("Montara Platform", -12.6667, 124.5333),
                          ("Ichthys Explorer", -13.1833, 123.3333), ("Greater Sunrise Platform", -9.8, 128.2)):
    site(rig_label, NEU, la, lo, "export", [(rig_label, ["civ_spar_rig_helo"])], mask=False,
         nation_key="timor_leste" if "Sunrise" in rig_label or "Bayu" in rig_label else "australia")

# Naval context so the threat axes mean something: (side, type, variant, role, lat, lon, heading)
SHIP_GROUPS = {TF1: "Darwin Surface Group", TF2: "Fiery Cross SAG"}
SHIPS = [
    (TF1, "ran_ddg_hobart", "Variant1", "AAW", -11.30, 129.80, 300),
    (TF1, "ran_ffh_anzac", "Variant2", "ASW", -11.22, 129.90, 300),
    (TF1, "ran_ffh_anzac", "Variant3", "ASW", -11.38, 129.72, 300),
    (TF1, "usn_ddg_burke_f2a_113", "Variant1", "AAW", 10.60, 118.90, 20),
    (TF1, "usn_ddg_burke_f3_125", "Variant1", "AAW", 10.50, 118.75, 20),
    (TF1, "usn_takr_algol", "Variant1", "Transport", -11.15, 130.00, 120),
    (TF2, "plan_type_055_2026", "Variant2", "AAW", 9.20, 113.30, 120),
    (TF2, "plan_type_052d_p4", "Variant1", "AAW", 9.10, 113.45, 120),
    (TF2, "plan_type_054a_p5", "Variant1", "ASW", 9.30, 113.15, 120),
    (TF2, "rfn_ffg_22350_1-4", "Variant1", "AAW", -0.60, 135.90, 250),
    (TF2, "rfn_ffg_22350_5-8", "Variant1", "AAW", -0.52, 136.02, 250),
]
# Neutral merchant lanes (lat/lon chains): spawn at the first point, waypoints through the rest.
MERCHANTS = [
    ("civ_ms_bulk", [(-12.05, 130.75), (-11.30, 132.00), (-10.90, 133.80)], 55, 2),
    ("civ_ms_sealift_pacific", [(-5.80, 128.30), (-8.30, 131.30), (-9.60, 136.00)], 130, 3),
    ("civ_ms_ritina", [(-2.20, 118.90), (-4.60, 118.50), (-7.20, 117.80)], 190, 2),
    ("civ_ms_mairangi_bay", [(11.20, 119.00), (13.50, 119.60), (15.50, 119.30)], 10, 2),
]

# Modded land units the region cannot justify; everything else modern is expected on the map.
COVERAGE_EXEMPT = {
    "idf_dsws", "idf_dsws_radar", "is_airbase_reykjavik", "US_Missile", "usa_tempest_site", "wp_neptune_site",
    "wp_tu160air", "airbase_us", "ei_skyguard_sam", "ei_aaa_sidam", "ei_aaa_sidam_mistral", "it_spaa_sidam_25",
    "brd_spaa_flarakpz_1", "brd_spaa_gepard", "brd_spaa_gepard1a2", "usa_spaa_m247",
}


# ---------------------------------------------------------------------------
def to_xz(lat, lon):
    return (lon - CLON) * 60.0, (lat - CLAT) * 60.0


def expand(units):
    out = []
    for u in units:
        if isinstance(u, tuple):
            out += [u[0]] * u[1]
        else:
            out.append(u)
    return out


def land_block(uid, variant, x, z, hdg, nation_key):
    b = (f"Type={uid}\nVariantReference={variant}\nUnlimitedFuel=False\nWeaponStatus=Free\n"
         f"CrewSkill=Trained\nMorale=3\nRelativePositionInNM={x:.2f},low,{z:.2f}\n")
    if nation_key:
        b += f"Nation={nation_key}\n"
    return b + f"Heading={int(hdg) % 360}\n"


def ship_block(uid, variant, role, x, z, hdg):
    return (f"Type={uid}\nVariantReference={variant}\nUnlimitedFuel=False\nStationRole={role}\n"
            f"RadarsActive=True\nWeaponStatus=Free\nCrewSkill=Trained\nMorale=3\n"
            f"RelativePositionInNM={x:.2f},0,{z:.2f}\nTelegraph=2\nHeading={hdg}\n")


def bearing(p, q):
    """Initial bearing from p to q, both (x, z) in datum nm, 0 = north."""
    return int(round(math.degrees(math.atan2(q[0] - p[0], q[1] - p[1])))) % 360


def merchant_block(uid, pts, hdg, tel, variant="Default"):
    xz = [to_xz(la, lo) for la, lo in pts]
    wpts = "|".join(f"{x:.1f},{Y_SEA},{z:.1f}" for x, z in xz[1:]) + "/SetTelegraph,3"
    x, z = xz[0]
    if hdg is None:
        hdg = bearing(xz[0], xz[1]) if len(xz) > 1 else 0
    return (f"Type={uid}\nVariantReference={variant}\nRadarsActive=True\nCrewSkill=Trained\n"
            f"RelativePositionInNM={x:.1f},0,{z:.1f}\nTelegraph={tel}\nHeading={hdg}\nWaypoints={wpts}\n")


def aircraft_block(uid, squadron, pts, alt_ft, tel=3):
    """An airborne civil or military aircraft flying a lat/lon chain at alt_ft."""
    xz = [to_xz(la, lo) for la, lo in pts]
    x, z = xz[0]
    hdg = bearing(xz[0], xz[1]) if len(xz) > 1 else 0
    wpts = "|".join(f"{px:.1f},{alt_ft},{pz:.1f}" for px, pz in xz[1:])
    return (f"Type={uid}\nSquadronReference={squadron}\nUnlimitedFuel=False\nWeaponStatus=Free\n"
            f"RadarsActive=True\nMorale=3\nRelativePositionInNM={x:.2f},{alt_ft},{z:.2f}\n"
            f"Telegraph={tel}\nHeading={hdg}\nWaypoints={wpts}\n")


def airgroup_lines(group):
    """CustomAirGroup lines for a land unit: [(aircraft id, 'Squadron1,6|Squadron2,6')]."""
    return "CustomAirGroup=True\n" + "".join(f"{uid}={sq}\n" for uid, sq in group)


class Spiral:
    """Places a site's assets: the first at the centre, the rest outward on a
    golden-angle spiral, on land and clear of each other."""

    def __init__(self, geo, occupied):
        self.geo, self.occupied = geo, occupied

    def place(self, cx, cz, i, spread, mask):
        if i == 0:
            self.occupied.append((cx, cz))
            return cx, cz
        base_b = (i * 137.508) % 360.0
        base_r = spread * (0.55 + 0.32 * math.sqrt(i))
        for shrink in (1.0, 1.3, 1.7, 2.2):
            for k in range(0, 12):
                for sign in ((1,) if k == 0 else (1, -1)):
                    b = base_b + sign * k * 15.0
                    x, z = self.geo.offset(cx, cz, b, base_r * shrink)
                    x, z = round(x, 2), round(z, 2)
                    if mask and not self.geo.on_land(x, z):
                        continue
                    if all(self.geo.dist(x, z, ox, oz) >= 0.07 for ox, oz in self.occupied):
                        self.occupied.append((x, z))
                        return x, z
        raise SystemExit(f"no room for asset {i} near ({cx:.2f},{cz:.2f})")


def afloat(lat, lon, halo=0.10):
    """A vessel needs open water under it and a little room around it. Ships
    are placed by hand, so nothing else catches a position that looks like sea
    on a map and is a beach on the mask (the Darwin group spent three builds
    parked on the Tiwi Islands)."""
    if LAND is None:
        return True
    if LAND.is_land(lat, lon):
        return False
    return not any(LAND.is_land(lat + halo * math.cos(math.radians(c)),
                                lon + halo * math.sin(math.radians(c)) / math.cos(math.radians(lat)))
                   for c in range(0, 360, 20))


def check_units(units):
    """Every planned unit id must resolve, loudly."""
    bad = sorted({u for u in units if unit_info(u) is None})
    if bad:
        sys.exit("unit ids no enabled mod defines: " + ", ".join(bad))


def generate(name, out, description, sites, ships, merchants, aircraft=(), airgroups=None,
             ship_groups=None, datum=None, density="full", coverage_exempt=None, date="2026,9,17",
             report_unused=True):
    """Write the mission `out`: sites laid out on land, then the builder's
    defences on top, then the coverage report. Everything the showcase and
    its regional variants differ in comes through the arguments."""
    global CLAT, CLON
    if datum:
        CLAT, CLON = datum
    airgroups = airgroups or {}
    ship_groups = ship_groups or SHIP_GROUPS
    coverage_exempt = COVERAGE_EXEMPT if coverage_exempt is None else coverage_exempt
    downgrade = {"full": {}, "standard": {"heavy": "standard"},
                 "light": {"heavy": "standard", "standard": "light", "light": "light"}}[density]

    every = [u for s in sites for _, units in s["groups"] for u in expand(units)]
    check_units(every)
    for side, uid, *_ in ships:
        if winning_file(f"vessels/{uid}.ini") is None:
            sys.exit(f"vessel not provided by any enabled mod: {uid}")
    for uid, *_ in merchants:
        if winning_file(f"vessels/{uid}.ini") is None:
            sys.exit(f"vessel not provided by any enabled mod: {uid}")
    for uid, *_ in aircraft:
        if winning_file(f"aircraft/{uid}.ini") is None:
            sys.exit(f"aircraft not provided by any enabled mod: {uid}")
    for label, group in airgroups.items():
        if label not in {s["label"] for s in sites}:
            sys.exit(f"air group for an unknown site: {label!r}")
        for uid, _ in group:
            if winning_file(f"aircraft/{uid}.ini") is None:
                sys.exit(f"air group aircraft not provided by any enabled mod: {uid}")

    geo = Geo(CLAT, CLON)
    occupied = []
    spiral = Spiral(geo, occupied)

    # --- lay the assets out ------------------------------------------------
    units = {TF1: [], TF2: [], NEU: []}        # side -> [(label, uid, variant, x, z, hdg, nation_key, extra)]
    formations = {TF1: [], TF2: [], NEU: []}   # side -> [(label, [indices])]
    names = {TF1: [], TF2: [], NEU: []}        # side -> [(index, name)]
    for s in sites:
        cx, cz = to_xz(s["lat"], s["lon"])
        if s["mask"] and LAND is not None and not geo.on_land(cx, cz):
            # real coordinate that the 1 km mask calls water (a wharf, a reef-edge strip):
            # slide to the nearest land within ~3 nm rather than fail
            moved = False
            for r in (0.5, 1.0, 1.5, 2.0, 3.0):
                for d in range(0, 360, 20):
                    x, z = geo.offset(cx, cz, d, r)
                    if geo.on_land(x, z):
                        cx, cz, moved = x, z, True
                        break
                if moved:
                    break
            if not moved:
                sys.exit(f"{s['label']}: no land within 3 nm of {s['lat']},{s['lon']}")
        i = 0
        for gi, (glabel, group) in enumerate(s["groups"]):
            idx = []
            for uid in expand(group):
                x, z = spiral.place(cx, cz, i, s["spread"], s["mask"])
                hdg = 0 if i == 0 else (i * 137.508 + 90) % 360   # anchor faces north
                variant = pick_variant(uid, s["nation"])
                extra = airgroup_lines(airgroups[s["label"]]) if i == 0 and s["label"] in airgroups else ""
                if extra and unit_info(uid)["subtype"] != "Airbase":
                    sys.exit(f"{s['label']}: air group on {uid}, which is not an Airbase")
                units[s["side"]].append((s["label"], uid, variant, x, z, hdg, s["nation_key"], extra))
                idx.append(len(units[s["side"]]) - 1)
                i += 1
            formations[s["side"]].append((glabel, idx))
            if gi == 0:
                names[s["side"]].append((idx[0], s["label"]))
        s["xz"] = (cx, cz)

    afloat_problems = []
    for _side, uid, _v, _r, la, lo, _h, *_g in ships:
        if not afloat(la, lo):
            afloat_problems.append(f"{uid} at {la},{lo}")
    for uid, pts, *_ in merchants:
        # a merchant may legitimately start at a wharf, so it only has to be on
        # water; a warship group needs room to manoeuvre and keeps the halo
        if not afloat(*pts[0], halo=0.0):
            afloat_problems.append(f"{uid} spawns at {pts[0][0]},{pts[0][1]}")
    if afloat_problems:
        sys.exit("vessels placed on land (the 1 km mask, with a clearance halo):\n  "
                 + "\n  ".join(afloat_problems))

    shipsby = {TF1: [], TF2: []}
    ship_forms = {TF1: {}, TF2: {}}            # side -> {group label: [vessel section names]} in order
    for side, uid, variant, role, la, lo, hdg, *group in ships:
        x, z = to_xz(la, lo)
        shipsby[side].append((uid, variant, role, x, z, hdg))
        label = group[0] if group else ship_groups[side]
        ship_forms[side].setdefault(label, []).append(f"{side}Vessel{len(shipsby[side])}")

    # --- assemble the file -------------------------------------------------
    lang = [f"Name={name}", f"Description={description}"]
    for side in (TF1, TF2, NEU):
        for idx, label in names[side]:
            lang.append(f"{side}LandUnit{idx + 1}NameOverride={label}")
    text = ["\n[Language_en]\n" + "\n".join(lang) + "\n"]
    for code in ("cn", "ru", "de", "es", "fr", "ko", "ja", "vn"):
        text.append(f"[Language_{code}]\nName={name}\n")
    text.append(f"[Environment]\nDate={date}\nTime=8,0\nConvertTimeToLocal=True\nSeaState=2\n"
                "Clouds=Scattered_1\nWindDirection=SE\n"
                f"MapCenterLatitude={CLAT}\nMapCenterLongitude={CLON}\nLoadBackgroundData=False\n")
    mission = ["Difficulty=0", "PlayerTaskforce=Taskforce1", "EnemyTaskforce=Taskforce2"]
    mission += [f"NumberOfTaskforce1Vessels={len(shipsby[TF1])}", f"NumberOfTaskforce2Vessels={len(shipsby[TF2])}",
                f"NumberOfNeutralVessels={len(merchants)}",
                f"NumberOfTaskforce1LandUnits={len(units[TF1])}", f"NumberOfTaskforce2LandUnits={len(units[TF2])}",
                f"NumberOfNeutralLandUnits={len(units[NEU])}"]
    if aircraft:
        mission.append(f"NumberOfNeutralAircraft={len(aircraft)}")
    for side in (TF1, TF2):
        forms = list(ship_forms[side].items())
        forms += [(label, [f"{side}LandUnit{i + 1}" for i in idx]) for label, idx in formations[side]]
        mission.append(f"{side}_NumberOfFormations={len(forms)}")
        for n, (label, members) in enumerate(forms, 1):
            at_sea = all("Vessel" in u for u in members)
            shape = "Loose|1.5" if at_sea else "Circle|1.5|OverrideSpawnPositions"
            mission.append(f"{side}_Formation{n}={','.join(members)}|{label}|{shape}")
    nforms = [(label, [f"NeutralLandUnit{i + 1}" for i in idx]) for label, idx in formations[NEU]]
    mission.append(f"Neutral_NumberOfFormations={len(nforms)}")
    for n, (label, members) in enumerate(nforms, 1):
        mission.append(f"Neutral_Formation{n}={','.join(members)}|{label}|Circle|1.5|OverrideSpawnPositions")
    text.append("[Mission]\n" + "\n".join(mission) + "\n")
    for side in (TF1, TF2):
        for i, (uid, variant, role, x, z, hdg) in enumerate(shipsby[side], 1):
            text.append(f"[{side}Vessel{i}]\n" + ship_block(uid, variant, role, x, z, hdg))
        for i, (_, uid, variant, x, z, hdg, nk, extra) in enumerate(units[side], 1):
            text.append(f"[{side}LandUnit{i}]\n" + land_block(uid, variant, x, z, hdg, nk) + extra)
    for i, (uid, pts, hdg, tel, *rest) in enumerate(merchants, 1):
        text.append(f"[NeutralVessel{i}]\n" + merchant_block(uid, pts, hdg, tel, *rest))
    for i, (uid, squadron, pts, alt) in enumerate(aircraft, 1):
        text.append(f"[NeutralAircraft{i}]\n" + aircraft_block(uid, squadron, pts, alt))
    for i, (_, uid, variant, x, z, hdg, nk, extra) in enumerate(units[NEU], 1):
        text.append(f"[NeutralLandUnit{i}]\n" + land_block(uid, variant, x, z, hdg, nk) + extra)
    text.append("[BackgroundData]\nNumberOfBackgroundCityFiles=0\nNumberOfBackgroundAirportFiles=0\n"
                "NumberOfBackgroundPortFiles=0\nNumberOfBackgroundInstallationFiles=0\n"
                "NumberOfBackgroundSceneryFiles=0\n")
    out.write_bytes("".join(text).encode("utf-8"))

    # --- defences, through the builder ------------------------------------
    m = Mission(out)
    ns = argparse.Namespace(threat_bearing=None)
    planner = Planner(m, ns)
    added = 0
    notes = []
    sites_by = {}
    for side in (TF1, TF2, NEU):
        for st in find_sites(m, m.geo, side, 6.0):
            sites_by[(side, st["label"])] = st
    for s in sites:
        posture = downgrade.get(s["posture"], s["posture"])
        if posture == "none":
            continue
        st = sites_by.get((s["side"], s["groups"][0][0]))
        if st is None:
            sys.exit(f"planner cannot find the site formation {s['label']!r}")
        st["nation"] = s["nation"]
        st["nation_key"] = s["nation_key"]
        doctrine = s["doctrine"] or doctrine_for(s["nation"], "modern")
        m.geo.mask_enabled = s["mask"]
        ns.threat_bearing = s["threat"]
        groups = planner.plan_site(st, doctrine, "modern", posture, None, s["coastal"], s["composite"], False)
        m.geo.mask_enabled = True
        for note in st.get("skipped", []):
            notes.append(f"{s['label']}: {note}")
        apply_groups(m, s["side"], groups, s["nation_key"])
        added += sum(len(u) for _, u in groups)
    problems = m.verify()
    if problems:
        sys.exit("generated mission fails its own checks:\n  " + "\n  ".join(problems))
    out.write_bytes(m.text().encode("utf-8"))

    # --- report ------------------------------------------------------------
    body = out.read_text(encoding="utf-8")
    types = re.findall(r"^Type=(.+)$", body, re.M)
    land_types = [t for t in types if unit_info(t)]
    modded = sorted({t for t in land_types if unit_info(t)["provider"] not in ("vanilla",)
                     and not unit_info(t)["provider"].startswith("SEST_")})
    wet = 0
    if LAND is not None:
        for sec, ty, x, z, _ in m.units(cls="LandUnit"):
            if not m.geo.on_land(x, z):
                wet += 1
    total = len(m.units(cls="LandUnit"))
    print(f"written: {out.name}")
    print(f"  sites {len(sites)}   land units {total} (assets {total - added}, defences {added})"
          f"   ships {sum(len(v) for v in shipsby.values())}   merchants {len(merchants)}"
          f"   civil aircraft {len(aircraft)}   air groups {len(airgroups)}")
    print(f"  distinct land unit types {len(set(land_types))}, of which modded {len(modded)}")
    if LAND is not None:
        print(f"  land units the mask calls water: {wet} (reef bases and rigs are expected here)")
    for n in notes:
        print(f"  note: {n}")
    pool = set()
    for d in (ROOT / "mods-source").glob("*/land_units"):
        if d.parent.name[0].isdigit():
            pool |= {f.stem for f in d.glob("*.ini") if not f.name.endswith("_variants.ini")}
    pool = {u for u in pool if unit_info(u) and unit_info(u)["provider"] != "vanilla"}
    unused = sorted(pool - set(land_types) - coverage_exempt)
    print(f"  modded land unit types available {len(pool)}, used {len(pool & set(land_types))}, "
          f"exempt {len(pool & coverage_exempt)}, unused {len(unused)}")
    if unused and report_unused:
        print("  unused: " + ", ".join(unused))


def cli(default_density="full"):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--density", choices=("full", "standard", "light"), default=default_density,
                    help="scale the defence postures down for a lighter mission")
    return ap.parse_args()


def main():
    args = cli()
    generate(NAME, OUT, DESCRIPTION, SITES, SHIPS, MERCHANTS, density=args.density)


if __name__ == "__main__":
    main()
