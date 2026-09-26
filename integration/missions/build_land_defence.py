#!/usr/bin/env python3
"""Lay out land defences, and the sites they defend, in a mission automatically.

The mission editor gives you one land unit at a time. A defended airbase is
twenty of them - the point-defence guns on the perimeter, the SHORAD vehicles
a mile out, the medium battery on the flank, the area-defence regiment's radar
with its launchers starred around it, the search radar off to one side - every
one placed by hand, checked against the coast, and grouped. This does that the
way Nuclear Option's editor populates a base: name the asset, get the defences.

What it does, per site:

  1. finds the sites - every formation of land units (an airbase, a missile
     battery, a depot, a coastal launcher group) and every stray land unit, on
     both sides - and decides which are worth defending: airbases, ports,
     installations, missile sites, TBM and drone launchers
  2. reads what is already there - every air-defence unit of that side within
     --cover-radius of the site counts, classified by the longest AAW missile
     it fires (gun / SHORAD / medium / area / search radar), so a battery that
     already has a ZSU gets the outer layers and not a second ZSU
  3. picks a doctrine from the side's nation (the asset's own Nation=, its
     unit-id prefix, or the majority of that side's units) and an era: modern
     by default, which is the S-400, HQ-9B, PAC-3, THAAD, NASAMS, Tor, Pantsir
     and HQ-17 the collection's mods provide; --era cold-war for vanilla
     SA-10 / Hawk / Rapier kit
  4. lays the missing layers out around the site, oriented on the threat axis
     (the distance-weighted bearing to the enemy side's units): gun ring,
     SHORAD ring, medium battery on the flank, area battery forward, search
     radar on the flank, BMD behind (heavy posture), coastal launchers toward
     the threat (--coastal)
  5. keeps every launcher inside its fire-control radar's
     ExternalGuidingSystemSearchRadius - a TEL outside it never fires - and,
     with the land-mask package installed, keeps every unit on land; a site
     with no land around it (a seized rig) is skipped, not flooded
  6. writes the units as [TaskforceNLandUnitM] blocks, one formation per
     layer group, bumps the counts, and names the key radars in [Language_en]

Everything resolves through the load order (winning_file, and a round's
#!extend / #!alias chain down to its base): a unit is planned only if the
game will load it, its VariantReference is the variant whose Nation matches
the site, and a battery is used only if its radar really provides the
guidance system its launchers ask for - checked against the files, not
assumed.

Re-runs are safe: a layer a site already has is not added again, so this can
sit in the refresh chain (refresh-mission.ps1 -LandDefence). Nothing already
in the mission is moved or retyped.

Usage (repo root):
    python3 integration/missions/build_land_defence.py                   # plan for the active mission
    python3 integration/missions/build_land_defence.py --write           # apply the plan
    python3 integration/missions/build_land_defence.py --around Townsville --posture heavy --coastal --write
    python3 integration/missions/build_land_defence.py --build fob --at -11.55 130.95 \\
        --side Taskforce2 --nation china --label "Melville FOB" --posture heavy --coastal --write
    python3 integration/missions/build_land_defence.py --list-sites      # the site analysis only
    python3 integration/missions/build_land_defence.py --catalog         # what each doctrine resolves to
"""
import argparse
import functools
import json
import math
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_civ_traffic import active_mission, file_stack, winning_file  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = Path(__file__).resolve().parent

try:
    from global_land_mask import globe as LAND
except ImportError:      # optional, like fix_land_positions.py's water check
    LAND = None

SIDES = ("Taskforce1", "Taskforce2")
UNIT_CLASSES = ("Vessel", "Submarine", "Aircraft", "LandUnit", "Biologic")

# An AAW missile's MaxLaunchRange (nm) decides which layer an existing unit
# already provides. Guns are 'aaa'; a Radar-subtype unit with no weapons and a
# Radar/ESM role is a search radar ('ew'); a SAM battery's own fire-control
# radar is part of a battery, not a layer of its own.
SHORAD_MAX_NM = 12.0
MEDIUM_MAX_NM = 70.0
BMD_MIN_ALT_M = 15000.0     # a round that cannot engage below this is an interceptor, not a SAM

# Only these count as "an air-defence unit is already here". Radar-subtype
# units are fire-control or search radars; anything else with AAW in its role
# and a MobileUnit body is a SPAAG or a SHORAD vehicle.
ASSET_SUBTYPES = {"Airbase", "Port", "Installation", "MissileSite", "OilRig", "Bridge"}
STRATEGIC_MOBILE = re.compile(r"(_tel$|scud|sejjil|shahed|dronesquad|mlrs|df-\d|ss-26|iskander)", re.I)

# ---------------------------------------------------------------------------
# Nations and doctrines
# ---------------------------------------------------------------------------
NATION_ALIASES = {
    "soviet": "russia", "ussr": "russia", "russian": "russia", "rus": "russia",
    "us": "usa", "united_states": "usa", "america": "usa",
    "prc": "china", "pla": "china", "plan": "china",
    "britain": "uk", "united_kingdom": "uk", "great_britain": "uk",
    "brd": "germany", "west_germany": "germany", "roc": "taiwan",
}

# Who fights with whose kit. Cold-war Warsaw Pact members are re-mapped to
# 'export' by doctrine_for(); in the modern era they are NATO.
DOCTRINE_OF = {
    "russia": "russia", "china": "china", "usa": "usa", "australia": "australia",
    "uk": "uk", "germany": "germany", "france": "france", "japan": "japan",
    "israel": "israel",
    "canada": "nato", "spain": "nato", "italy": "nato", "greece": "nato",
    "belgium": "nato", "denmark": "nato", "netherlands": "nato", "norway": "nato",
    "turkey": "nato", "poland": "nato", "sweden": "nato", "finland": "nato",
    "switzerland": "nato", "south_korea": "nato", "kuwait": "nato", "qatar": "nato",
    "taiwan": "nato", "philippines": "nato", "thailand": "nato", "czech": "nato",
    "hungary": "nato", "romania": "nato", "bulgaria": "nato", "iceland": "nato",
    "iran": "export", "north_korea": "export", "vietnam": "export", "iraq": "export",
    "syria": "export", "egypt": "export", "libya": "export", "cuba": "export",
    "india": "export", "pakistan": "export", "south_yemen": "export",
    "terrorists": "export", "algeria": "export", "ddr": "export", "myanmar": "export",
    "sri_lanka": "export", "jordan": "export", "morocco": "export",
}
WARSAW_PACT = {"poland", "czech", "hungary", "romania", "bulgaria", "ddr"}

# Unit-id prefix -> nation, for assets that carry no Nation= and for the
# majority vote across a side. Order matters: specific before generic.
PREFIX_NATION = [
    (("airbase_raaf", "raaf_", "ran_", "adf_", "aus_"), "australia"),
    (("pla_", "plan_", "plaaf_", "plaf_", "china_", "cn_"), "china"),
    (("wp_", "ru_", "rfn_", "vmf_", "sov_"), "russia"),
    (("usa_", "usn_", "usaf_", "usmc_", "us_", "nato_", "thaad", "dts_"), "usa"),
    (("raf_", "rn_", "uk_", "gb_"), "uk"),
    (("fr_",), "france"),
    (("jp_", "jsdf_", "jmsdf_", "js_"), "japan"),
    (("idf_", "il_"), "israel"),
    (("brd_", "ger_", "de_"), "germany"),
    (("ei_", "it_", "mm_"), "italy"),
    (("nv_",), "vietnam"), (("iqa_", "ods_"), "iraq"), (("swe_",), "sweden"),
    (("fin_",), "finland"), (("is_",), "iceland"), (("ir_", "iran_", "shahed"), "iran"),
    (("nk_", "dprk_"), "north_korea"),
]


def norm_nation(s):
    s = (s or "").strip().lower().replace(" ", "_").replace("-", "_")
    return NATION_ALIASES.get(s, s)


def doctrine_for(nation, era):
    if era == "cold-war" and nation in WARSAW_PACT:
        return "export"
    return DOCTRINE_OF.get(nation, "nato")


def prefix_nation(uid):
    low = uid.lower()
    for prefixes, nation in PREFIX_NATION:
        if low.startswith(prefixes):
            return nation
    return None


def bty(label, radar=None, tels=(), search=(), composite=None):
    """One battery: a fire-control radar plus launchers starred around it, an
    optional acquisition radar behind, or a single composite site unit."""
    return {"label": label, "radar": radar, "tels": list(tels), "search": list(search),
            "composite": composite}


# Layer -> candidates. Lists of unit ids are tried in order and cycled to the
# count wanted; lists of batteries use the first whose every unit resolves and
# whose radar provides what its launchers ask for. Missing entries mean the
# doctrine has nothing for that layer and it is skipped with a note.
DOCTRINES = {
    "russia": {
        "modern": {
            "area": [bty("S-400 battery", "wp_sa-21_flaplid",
                         [("wp_sa-21_48n6e3_tel", 4), ("wp_sa-21_40n6_tel", 1),
                          ("wp_sa-21_9m96e2_tel", 1)], ["wp_p-14_radar"]),
                     bty("S-400 site", composite="wp_sam_site_sa_21"),
                     bty("S-300PS battery", "wp_sa-10_flaplid", [("wp_sa-10_tel", 4)],
                         ["wp_p-14_radar"])],
            "medium": [bty("Buk battery", "wp_sa-11_radar", [("wp_sa-11_launcher", 3)]),
                       bty("Buk site", composite="wp_sam_site_sa-11_small")],
            "shorad": ["wp_spaa_sa-19a", "wp_9k332", "wp_spaa_sa-19", "wp_9k331", "wp_spaa_zsu-23-4m4",
                       "wp_sa-13_launcher"],
            "aaa": ["wp_spaa_zsu-23-4", "wp_aaa_ural_zu-23", "wp_zsu-57"],
            "ew": ["wp_p-14_radar", "wp_p-35_radar", "wp_p-18_radar"],
            "bmd": [bty("S-400 long-range section", "wp_sa-21_flaplid", [("wp_sa-21_40n6_tel", 2)])],
            "coastal": [bty("Bastion battery", "wp_sa-10_flaplid", [("wp_k300p_tel", 2), ("wp_bal", 1)]),
                        bty("Bal battery", tels=[("wp_bal", 2)]),
                        bty("Rubezh battery", tels=[("wp_asc_rubezh", 2)])],
            "support": ["wp_car_ural_command", "tgt_fueltanks_small", "tgt_ammo_depot_small",
                        "Ammo_Bunker", "wp_car_ural", "warehouses_1"],
        },
        "cold-war": {
            "area": [bty("S-300PS battery", "wp_sa-10_flaplid", [("wp_sa-10_tel", 4)], ["wp_p-14_radar"]),
                     bty("S-300PS site", composite="wp_sam_site_sa-10"),
                     bty("S-200 site", composite="wp_sam_site_sa-5")],
            "medium": [bty("Buk battery", "wp_sa-11_radar", [("wp_sa-11_launcher", 3)]),
                       bty("Kub battery", "wp_sa-6_straightflush", [("wp_sa-6_launcher", 3)])],
            "shorad": ["wp_sa-8_launcher", "wp_sa-13_launcher"],
            "aaa": ["wp_zsu-57", "wp_aaa_ural_zu-23", "wp_aaa_ural_s-60"],
            "ew": ["wp_p-14_radar", "wp_p-35_radar", "wp_p-18_radar"],
            "coastal": [bty("Rubezh battery", tels=[("wp_asc_rubezh", 2)]),
                        bty("Redut battery", tels=[("wp_asc_redut", 2)])],
            "support": ["wp_car_ural_command", "tgt_fueltanks_small", "tgt_ammo_depot_small", "wp_car_ural"],
        },
    },
    "china": {
        "modern": {
            "area": [bty("HQ-9B battery", "pla_ht-233_radar",
                         [("pla_hq-9b_tel", 4), ("pla_hq-9c_tel", 2)], ["pla_llq-305_radar"]),
                     bty("HQ-9B site", composite="pla_sam_site_hq-9_morden"),
                     bty("HQ-9 site", composite="pla_sam_site_hq-9")],
            "medium": [bty("HQ-16B battery", "pla_hq-16_fcr", [("pla_hq-16b_tel", 4)], ["pla_ylc-18_radar"]),
                       bty("HQ-16B site", composite="pla_sam_site_hq-16b"),
                       bty("HQ-22 battery", "pla_h-200a_radar", [("pla_hq-22a_tel", 4)])],
            "shorad": ["pla_hq-17a", "pla_hq-17_tel", "pla_9k331", "pla_hq-7b_tel"],
            "aaa": ["pla_spaa_pgz-09", "pla_ld-2000", "pla_ld-3000", "pla_aaa_type65"],
            "ew": ["pla_llq-305_radar", "pla_ylc-18_radar", "pla_ylc-xx_radar", "wp_cross_slot"],
            "bmd": [bty("HQ-19 section", "pla_slc-14_radar", [("pla_hq-19_tel", 2)])],
            "coastal": [bty("YJ-12 battery", tels=[("pla_yj-12_tel", 2), ("pla_yj-62_tel", 2)]),
                        bty("YJ-62 battery", tels=[("pla_yj-62_tel", 2)]),
                        bty("HY-4 battery", tels=[("pla_hy-4_launcher", 2)])],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker", "FOB",
                        "warehouses_1", "pla_apc_zbl-08"],
        },
        "cold-war": {
            "area": [bty("HQ-2 site", composite="wp_sam_site_sa-2")],
            "medium": [bty("SA-3 site", composite="wp_sam_site_sa-3")],
            "shorad": [],          # no cold-war Chinese SHORAD missile in the collection
            "aaa": ["pla_spaag_type63", "pla_aaa_type65", "pla_aaa_type55"],
            "ew": ["wp_cross_slot", "wp_p-14_radar"],
            "coastal": [bty("HY-2 battery", tels=[("pla_hy-2_launcher", 2), ("pla_hy-4_launcher", 1)]),
                        bty("Silkworm battery", tels=[("wp_silkworm_launcher", 2)])],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "warehouses_1", "pla_apc_type63"],
        },
    },
    "usa": {
        "modern": {
            "area": [bty("Patriot battery", "usa_an_mpq-65_radar",
                         [("usa_pac-3_launcher", 4), ("usa_pac-2_2000_launcher", 2)], ["nato_radar"]),
                     bty("Patriot battery", "usa_mim_104_radar_65a",
                         [("usa_mim_104f_mse_tel", 4), ("usa_mim_104e_gem_t_tel", 2)]),
                     bty("Patriot site", composite="usa_sam_site_pac-3_small")],
            "medium": [bty("NASAMS battery", "usa_slm_tads_hmmwv", [("usa_slm_tel_hmmwv", 3)]),
                       bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"])],
            "shorad": ["usa_spaa_adats"],
            "aaa": ["usa_aaa_vulcan", "usa_spaa_m247", "usa_aaa_m42"],
            "ew": ["nato_radar", "usa_radar_tps-43", "usa_radar_tps-63"],
            "bmd": [bty("THAAD battery", "wp_an_tpy_2", [("thaad_tel", 2)])],
            "coastal": [bty("Harpoon coastal battery", tels=[("usa_harpoon_launcher", 2)]),
                        bty("Harpoon coastal battery", tels=[("usa_harpoon_launcher_RGM84D", 2)])],
            "support": ["usa_car_hemtt", "tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker",
                        "FOB", "usa_car_m923", "warehouses_1"],
        },
        "cold-war": {
            "area": [bty("Nike Hercules site", composite="usa_sam_site_nike_hercules")],
            "medium": [bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"])],
            "shorad": [],          # Chaparral is not in the collection
            "aaa": ["usa_aaa_m42", "usa_aaa_m51", "usa_aaa_vulcan"],
            "ew": ["usa_radar_tps-43", "nato_fps-20_radar", "nato_radar"],
            "coastal": [bty("Harpoon coastal battery", tels=[("usa_harpoon_launcher_RGM84C", 2)])],
            "support": ["usa_car_m923", "tgt_fueltanks_small", "tgt_ammo_depot_small", "usa_car_hmmwv"],
        },
    },
    "uk": {
        "modern": {
            "medium": [bty("Rapier FSC battery", tels=[("raf_rapier_launcher", 4)])],
            "shorad": ["raf_rapier_launcher"],
            "aaa": ["nato_aaa_gdf"],
            "ew": ["nato_radar", "nato_large_ewr_station"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker", "FOB", "warehouses_1"],
        },
        "cold-war": {
            "medium": [bty("Rapier battery", tels=[("raf_rapier_launcher", 4)])],
            "shorad": ["raf_rapier_launcher"],
            "aaa": ["nato_aaa_gdf"],
            "ew": ["nato_radar", "nato_tps-27_radar"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "warehouses_1"],
        },
    },
    "germany": {
        "modern": {
            "area": [bty("Patriot battery", "usa_an_mpq-65_radar",
                         [("usa_pac-3_launcher", 4), ("usa_pac-2_2000_launcher", 2)], ["nato_radar"])],
            "medium": [bty("Roland battery", tels=[("brd_spaa_flarakpz_1", 3)])],
            "shorad": ["brd_spaa_flarakpz_1", "brd_spaa_gepard1a2"],
            "aaa": ["brd_spaa_gepard", "nato_aaa_gdf"],
            "ew": ["nato_radar", "nato_tps-27_radar"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker", "warehouses_1"],
        },
        "cold-war": {
            "medium": [bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"]),
                       bty("Roland battery", tels=[("brd_spaa_flarakpz_1", 3)])],
            "shorad": ["brd_spaa_flarakpz_1"],
            "aaa": ["brd_spaa_gepard", "nato_aaa_gdf", "usa_aaa_m42"],
            "ew": ["nato_radar", "nato_tps-27_radar"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "warehouses_1"],
        },
    },
    "france": {
        "modern": {
            "area": [bty("SAMP/T battery", tels=[("fr_samp-t", 3)])],
            "medium": [bty("Crotale NG battery", tels=[("swe_spaa_ito_90m", 3)])],
            "shorad": ["swe_spaa_ito_90m"],
            "aaa": ["nato_aaa_gdf"],
            "ew": ["nato_ewr_station", "nato_radar"],
            "support": ["fr_apc_griffon", "fr_vlfs", "tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker"],
        },
        "cold-war": {
            "medium": [bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"])],
            "shorad": ["swe_spaa_ito_90m", "nato_sam_skyguard"],
            "aaa": ["nato_aaa_gdf"],
            "ew": ["nato_ewr_station", "nato_radar"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "warehouses_1"],
        },
    },
    "japan": {
        "modern": {
            "area": [bty("Patriot battery", "usa_an_mpq-65_radar",
                         [("usa_pac-3_launcher", 4), ("usa_pac-2_2000_launcher", 2)])],
            "medium": [bty("Type 81 battery", tels=[("jsdf_sam_type81", 3)])],
            "shorad": ["jsdf_sam_type81"],
            "aaa": ["nato_aaa_gdf", "usa_aaa_m42"],
            "ew": ["nato_radar", "usa_radar_tps-43"],
            "coastal": [bty("Type 12 SSM battery", tels=[("jp_12ssmht", 2)])],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker", "jsdf_apc_type73"],
        },
        "cold-war": {
            "medium": [bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"])],
            "shorad": ["jsdf_sam_type81"],
            "aaa": ["nato_aaa_gdf", "usa_aaa_m42"],
            "ew": ["nato_radar", "usa_radar_tps-43"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "jsdf_apc_type73"],
        },
    },
    "israel": {
        "modern": {
            "area": [bty("David's Sling battery", "idf_dsws_radar", [("idf_dsws", 3)]),
                     bty("Patriot battery", "usa_an_mpq-53_radar", [("usa_pac-2_2000_launcher", 4)])],
            "medium": [bty("Patriot battery", "usa_an_mpq-53_radar", [("usa_pac-2_2000_launcher", 4)])],
            "shorad": [],          # nothing in the collection fills this for Israel
            "aaa": ["usa_aaa_vulcan"],
            "ew": ["usa_radar_tps-63"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker", "usa_apc_m113"],
        },
        "cold-war": {
            "medium": [bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"])],
            "shorad": [],
            "aaa": ["usa_aaa_vulcan"],
            "ew": ["usa_radar_tps-63"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "usa_apc_m113"],
        },
    },
    "nato": {
        "modern": {
            "area": [bty("Patriot battery", "usa_an_mpq-65_radar",
                         [("usa_pac-3_launcher", 4), ("usa_pac-2_2000_launcher", 2)], ["nato_radar"])],
            "medium": [bty("NASAMS battery", "usa_slm_tads_hmmwv", [("usa_slm_tel_hmmwv", 3)]),
                       bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"]),
                       bty("Skyguard/Aspide battery", tels=[("ei_skyguard_sam", 3)])],
            "shorad": ["brd_spaa_flarakpz_1", "nato_sam_skyguard"],
            "aaa": ["nato_aaa_gdf", "brd_spaa_gepard"],
            "ew": ["nato_radar", "nato_tps-27_radar", "nato_ewr_station"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker", "FOB", "warehouses_1"],
        },
        "cold-war": {
            "area": [bty("Nike Hercules site", composite="usa_sam_site_nike_hercules")],
            "medium": [bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)], ["usa_mim-23_radar"])],
            "shorad": ["nato_sam_skyguard", "raf_rapier_launcher"],
            "aaa": ["nato_aaa_gdf", "usa_aaa_m42"],
            "ew": ["nato_radar", "nato_tps-27_radar", "nato_fps-20_radar"],
            "support": ["tgt_fueltanks_small", "tgt_ammo_depot_small", "warehouses_1"],
        },
    },
    "export": {
        "modern": {
            "area": [bty("S-200 battery", "wp_sa-5_squarepair", [("wp_sa-5_launcher", 4)], ["wp_p-14_radar"]),
                     bty("S-200 site", composite="wp_sam_site_sa-5")],
            "medium": [bty("Buk battery", "wp_sa-11_radar", [("wp_sa-11_launcher", 3)]),
                       bty("Kub battery", "wp_sa-6_straightflush", [("wp_sa-6_launcher", 3)]),
                       bty("S-125 site", composite="wp_sam_site_sa-3")],
            "shorad": ["wp_9k331", "wp_sa-8_launcher", "wp_sa-13_launcher", "raf_rapier_launcher"],
            "aaa": ["wp_spaa_zsu-23-4", "wp_zsu-57", "wp_aaa_ural_zu-23", "wp_aaa_61K"],
            "ew": ["wp_p-18_radar", "wp_p-14_radar", "wp_p-35_radar", "wp_cross_slot"],
            "coastal": [bty("HY-4 battery", tels=[("pla_hy-4_launcher", 2)]),
                        bty("Silkworm battery", tels=[("wp_silkworm_launcher", 2)]),
                        bty("Rubezh battery", tels=[("wp_asc_rubezh", 2)])],
            "support": ["wp_car_ural_command", "tgt_fueltanks_small", "tgt_ammo_depot_small", "Ammo_Bunker",
                        "wp_car_ural"],
        },
        "cold-war": {
            "area": [bty("S-75 site", composite="wp_sam_site_sa-2"),
                     bty("S-200 site", composite="wp_sam_site_sa-5")],
            "medium": [bty("Kub battery", "wp_sa-6_straightflush", [("wp_sa-6_launcher", 3)]),
                       bty("S-125 site", composite="wp_sam_site_sa-3")],
            "shorad": ["wp_sa-8_launcher", "wp_sa-13_launcher", "wp_sa-7_launcher"],
            "aaa": ["wp_zsu-57", "wp_aaa_ural_zu-23", "wp_aaa_61K", "nv_s-60"],
            "ew": ["wp_p-18_radar", "wp_p-14_radar", "wp_cross_slot"],
            "coastal": [bty("Silkworm battery", tels=[("wp_silkworm_launcher", 2)]),
                        bty("HY-2 battery", tels=[("pla_hy-2_launcher", 2)])],
            "support": ["wp_car_ural_command", "tgt_fueltanks_small", "tgt_ammo_depot_small", "wp_car_ural"],
        },
    },
}
# Australia fights with US kit (NFIII already stands PAC-3 and THAAD up at
# Darwin under Nation=australia); NASAMS first for the medium layer because it
# is what 16 Regiment actually fields, Rapier for the cold war.
DOCTRINES["australia"] = {
    "modern": dict(DOCTRINES["usa"]["modern"],
                   ew=["nato_ewr_station", "nato_radar", "usa_radar_tps-43"]),
    "cold-war": dict(DOCTRINES["uk"]["cold-war"],
                     medium=[bty("Rapier battery", tels=[("raf_rapier_launcher", 4)]),
                             bty("Hawk battery", "usa_mim-23_fcr", [("usa_mim-23_launcher", 4)],
                                 ["usa_mim-23_radar"])]),
}

# Site templates for --build: what stands at the centre before it is defended.
# Nation-neutral where the collection allows (Buildings and Targets ships
# Nation=All); the TBM and drone rows are doctrine-specific.
SITE_TEMPLATES = {
    "fob": ["FOB", "Ammo_Bunker", "tgt_fueltanks_small", "4tentgroup", "@support", "@support"],
    "depot": ["warehouses_1", "tgt_fueltanks_medium", "tgt_ammo_depot_small", "Ammo_Bunker", "@support"],
    "radar_station": ["@ew", "Bunker_2", "@support"],
    "coastal_battery": ["@coastal", "Bunker_2", "@support"],
    "tbm_battery": ["@tbm", "@tbm", "@tbm", "wp_car_ural_command", "Ammo_Bunker", "@support"],
    "drone_site": ["@drone", "@drone", "@drone", "Ammo_Bunker", "@support"],
    "hq": ["nv_headquarters", "Bunker_2", "4tentgroup", "@support", "@support"],
}
TBM_BY_DOCTRINE = {
    "russia": ["wp_ss-26_tel", "wp_scud_9k72"], "china": ["pla_df-21d_tel", "pla_df-26b_tel", "pla_df-15_tel"],
    "export": ["wp_scud_9k72", "wp_sejjil_tel"], "usa": ["usa_mlrs_m270a2", "usa_mlrs_m270"],
    "australia": ["usa_mlrs_m270a2"], "nato": ["usa_mlrs_m270"], "uk": ["usa_mlrs_m270"],
    "germany": ["usa_mlrs_m270"], "france": ["fr_mlrs_m270"], "japan": ["usa_mlrs_m270"],
    "israel": ["usa_mlrs_m270"],
}
DRONE_BY_DOCTRINE = {
    "russia": ["shahed_tel_black", "shahed_tel_white"], "export": ["shahed_tel_black", "shahed_tel_white"],
    "china": ["pla_cj-10_tel", "dronesquad705_1"],
}

# Layers each posture wants, and how many ring units. Batteries are one each.
POSTURES = {
    "light": {"aaa": 2, "shorad": 2, "ew": 1},
    "standard": {"aaa": 3, "shorad": 4, "medium": 1, "area": 1, "ew": 1},
    "heavy": {"aaa": 4, "shorad": 6, "medium": 1, "area": 2, "ew": 2, "bmd": 1},
}

# ---------------------------------------------------------------------------
# Unit facts, read from the files the game loads
# ---------------------------------------------------------------------------
def parse_ini(path):
    """{section: {key: first value}}; '//' comments and '#' lines stripped."""
    secs, cur = {}, None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("//")[0].strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\[([^\]]+)\]", line)
        if m:
            cur = m.group(1).strip()
            secs.setdefault(cur, {})
            continue
        if "=" in line and cur is not None:
            k, v = line.split("=", 1)
            secs[cur].setdefault(k.strip(), v.strip())
    return secs


@functools.lru_cache(maxsize=None)
def mod_titles():
    try:
        cat = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))
    except OSError:
        return {}
    return {str(m.get("workshop_id")): m.get("title", "") for m in cat.get("mods", [])}


def provider_of(path):
    parts = path.parts
    if "mods-source" in parts:
        token = parts[parts.index("mods-source") + 1]
        if token == "_vanilla":
            return "vanilla"
        title = mod_titles().get(token)
        return f"{title} ({token})" if title else token
    if "integration" in parts:
        return parts[parts.index("integration") + 2]
    return str(path)


# Anchor Chain's layering directives: a file that starts with one is a patch
# whose keys win over the base it names.
LAYER_DIRECTIVE = re.compile(r"^\ufeff?#!(?:alias|extend)\s+(\S+)")


def layered_text(relpath):
    """The text of <relpath> as the game assembles it, highest priority first:
    the winning copy, then - while that copy is a #!extend or #!alias patch -
    the base it layers onto, so the first match of a key is the value that
    loads. A patch that names its own path layers onto the next copy DOWN the
    load order (the PLA AEP pack's rounds extend the PLA Land Unit Pack's
    copies this way, and its stubs carry no TargetType or ranges at all).
    None when no enabled mod defines the file."""
    stack = file_stack(relpath)
    f, parts = (stack[0] if stack else None), []
    for _ in range(8):
        if f is None:
            break
        text = f.read_text(encoding="utf-8", errors="replace")
        parts.append(text)
        m = LAYER_DIRECTIVE.match(text)
        if not m:
            break
        below = file_stack(m.group(1).replace("\\", "/"))
        try:
            f = below[below.index(f) + 1]
        except (ValueError, IndexError):
            f = below[0] if below and below[0] != f else None
    return "\n".join(parts) if parts else None


@functools.lru_cache(maxsize=None)
def ammo_aaw(ammo):
    """(MaxLaunchRange nm, MinAttackAltitude m) of an AAW round, or None when
    the round is not AAW or no enabled mod defines it."""
    text = layered_text(f"ammunition/{ammo}.ini")
    if text is None:
        return None
    tt = re.search(r"^TargetType=([A-Za-z]+)", text, re.M)
    if not tt or tt.group(1).upper() != "AAW":
        return None
    rng = re.search(r"^MaxLaunchRange=([\d.]+)", text, re.M)
    alt = re.search(r"^MinAttackAltitude=([\d.]+)", text, re.M)
    return (float(rng.group(1)) if rng else 0.0, float(alt.group(1)) if alt else 0.0)


@functools.lru_cache(maxsize=None)
def _sensor_files():
    """Every systems/sensors.ini the game merges, highest priority first."""
    from refine_civ_traffic import load_order, MODS
    seen, out = set(), []

    def add(path):
        if path and path.exists() and path not in seen:
            seen.add(path)
            out.append(path)
    for token in load_order():
        if token.startswith("SEST_"):
            for pack in (ROOT / "integration").glob(f"*/{token}"):
                add(pack / "systems" / "sensors.ini")
        else:
            add(MODS / token / "systems" / "sensors.ini")
    for d in sorted(p for p in MODS.iterdir() if p.is_dir() and p.name[0].isdigit()):
        add(d / "systems" / "sensors.ini")
    add(MODS / "_vanilla" / "original" / "systems" / "sensors.ini")
    return out


@functools.lru_cache(maxsize=None)
def _sensor_types(path):
    return {name: sec.get("Type", "") for name, sec in parse_ini(path).items()}


@functools.lru_cache(maxsize=None)
def sensor_type(system):
    """Search / Targeting / ... for a sensor SystemName, from the first file in
    load order that defines it (systems files merge key-by-key)."""
    for f in _sensor_files():
        ty = _sensor_types(f).get(system)
        if ty:
            return ty
    return None


@functools.lru_cache(maxsize=None)
def variants_of(uid):
    """[(section, nation)] the game can pick for a land unit, in file order."""
    vf = winning_file(f"land_units/{uid}_variants.ini")
    if vf is None:
        return [("Default", None)]
    secs = parse_ini(vf)
    out, seen = [], set()
    for name in re.findall(r"^\[(Default|Variant\d+)\]",
                           vf.read_text(encoding="utf-8", errors="replace"), re.M):
        if name in seen:
            continue
        seen.add(name)
        out.append((name, norm_nation(secs.get(name, {}).get("Nation"))))
    declared = secs.get("General", {}).get("NumberOfVariants")
    if declared and declared.isdigit():
        keep = [v for v in out if v[0] == "Default"] + \
               [v for v in out if v[0] != "Default"][:int(declared)]
        out = keep
    return out or [("Default", None)]


@functools.lru_cache(maxsize=None)
def unit_info(uid):
    """Everything the planner needs to know about a land unit type, or None
    when no enabled mod defines it."""
    f = winning_file(f"land_units/{uid}.ini")
    if f is None:
        return None
    secs = parse_ini(f)
    general = secs.get("General", {})
    roles = [r.strip() for r in secs.get("AI", {}).get("Role", "").split(",") if r.strip()]
    radars, weapons, guidance, radius = set(), [], set(), None
    for name, sec in secs.items():
        if name.startswith("SensorSystem") and sec.get("Type") == "Radar" and sec.get("SystemName"):
            radars.add(sec["SystemName"])
        if name.startswith("WeaponSystem") and name != "WeaponSystems" and sec.get("Type"):
            ammo = sec.get("Ammunition") or secs.get(sec.get("AssociatedMagazine", ""), {}).get("Ammunition1", "")
            weapons.append((sec["Type"], ammo))
            ext = sec.get("ExternalGuidingSystems")
            if ext:
                guidance.update(x.strip() for x in ext.split(",") if x.strip())
                r = sec.get("ExternalGuidingSystemSearchRadius")
                if r:
                    try:
                        radius = float(r) if radius is None else min(radius, float(r))
                    except ValueError:
                        pass
    aaw = [ammo_aaw(a) for t, a in weapons if t == "Missile" and a]
    aaw = [r for r in aaw if r is not None]
    sam = [r for r, alt in aaw if alt < BMD_MIN_ALT_M]
    return {
        "id": uid, "file": f, "provider": provider_of(f),
        "subtype": general.get("LandUnitSubType", ""), "roles": roles,
        "mobile": general.get("IsMobile", "").lower() == "true",
        "radars": radars, "weapons": weapons, "guidance": guidance,
        "guidance_radius": radius,
        "max_aaw_nm": max(sam) if sam else None,
        "bmd": bool(aaw) and not sam,
        "tacview": secs.get("Tacview", {}).get("Name", ""),
    }


def pick_variant(uid, nation):
    """The VariantReference whose Nation matches, else the first real variant."""
    variants = variants_of(uid)
    for name, vn in variants:
        if name != "Default" and vn and vn == nation:
            return name
    for name, vn in variants:
        if name != "Default":
            return name
    return "Default"


def ad_layer(info):
    """Which defence layer an existing unit already supplies, or None."""
    if info is None or info["id"].lower().startswith("civ_"):
        return None
    roles = set(info["roles"])
    if info["subtype"] == "Radar":
        if info["weapons"]:
            return "fcr"
        if info["radars"] and all(sensor_type(r) == "Targeting" for r in info["radars"]):
            return "fcr"
        return "ew"
    if info["bmd"]:
        return "bmd"
    if info["max_aaw_nm"] is not None:
        if info["max_aaw_nm"] >= MEDIUM_MAX_NM:
            return "area"
        if info["max_aaw_nm"] >= SHORAD_MAX_NM:
            return "medium"
        return "shorad"
    if info["subtype"] in ("AAA", "SAM"):
        return "aaa"
    if info["subtype"] == "MobileUnit" and "AAW" in roles and \
            any(t in ("Gun", "CIWS") for t, _ in info["weapons"]):
        return "aaa"
    return None


def is_asset(info, uid):
    if info is None:
        return False
    if info["subtype"] in ASSET_SUBTYPES:
        return True
    if "Airfield" in info["roles"] or "Target" in info["roles"]:
        return True
    return info["subtype"] == "MobileUnit" and bool(STRATEGIC_MOBILE.search(uid)) \
        and ad_layer(info) is None


# ---------------------------------------------------------------------------
# Resolving a doctrine against the load order
# ---------------------------------------------------------------------------
def resolve_units(candidates, count, layer=None):
    """The first `count` units from a candidate list that resolve, cycled.

    For a ring layer the unit must also classify as that layer from its own
    files - a gun listed under SHORAD would be placed as SHORAD and then read
    back as a gun, and every re-run would add another. The analyser and the
    planner share one taxonomy or the pass is not idempotent."""
    ok = [c for c in candidates if unit_info(c) is not None
          and (layer is None or ad_layer(unit_info(c)) == layer)]
    if not ok:
        return []
    return [ok[i % len(ok)] for i in range(count)]


def misfiled(candidates, layer):
    """Doctrine entries that resolve but classify as another layer."""
    return [(c, ad_layer(unit_info(c))) for c in candidates
            if unit_info(c) is not None and ad_layer(unit_info(c)) != layer]


def battery_problem(spec):
    """Why a battery spec cannot be used as-is, or None when it is sound."""
    if spec["composite"]:
        return None if unit_info(spec["composite"]) else f"{spec['composite']} not provided by any enabled mod"
    provided = set()
    for uid in ([spec["radar"]] if spec["radar"] else []) + spec["search"]:
        info = unit_info(uid)
        if info is None:
            return f"{uid} not provided by any enabled mod"
        provided |= info["radars"]
    for uid, _ in spec["tels"]:
        info = unit_info(uid)
        if info is None:
            return f"{uid} not provided by any enabled mod"
        if info["guidance"] and not (info["guidance"] & provided):
            return (f"{uid} needs {'/'.join(sorted(info['guidance']))} and the battery's radars "
                    f"provide {'/'.join(sorted(provided)) or 'nothing'}")
    return None


def resolve_battery(specs):
    for spec in specs:
        if battery_problem(spec) is None:
            return spec
    return None


def tel_ring_radius(spec):
    """Launcher ring radius: inside the tightest guidance radius, so every TEL
    can find its radar. 0.35 nm when nothing constrains it."""
    radii = [unit_info(u)["guidance_radius"] for u, _ in spec["tels"]
             if unit_info(u) and unit_info(u)["guidance_radius"]]
    return min(0.35, 0.6 * min(radii)) if radii else 0.35


# ---------------------------------------------------------------------------
# Geometry: x = minutes of longitude, z = minutes of latitude from the datum
# ---------------------------------------------------------------------------
class Geo:
    def __init__(self, clat, clon):
        self.clat, self.clon = clat, clon
        self.mask_enabled = True    # off for artificial islands the land mask does not know

    def to_ll(self, x, z):
        lon = self.clon + x / 60.0
        lon = ((lon + 180.0) % 360.0) - 180.0
        return self.clat + z / 60.0, lon

    def offset(self, x, z, bearing, dist):
        """Point dist nm from (x,z) on a true bearing, as a real-world circle:
        east-west minutes shrink by cos(lat) so rings are round on the ground."""
        lat = self.clat + z / 60.0
        b = math.radians(bearing)
        return (x + dist * math.sin(b) / max(0.2, math.cos(math.radians(lat))),
                z + dist * math.cos(b))

    def dist(self, x1, z1, x2, z2):
        lat = self.clat + (z1 + z2) / 120.0
        return math.hypot((x2 - x1) * math.cos(math.radians(lat)), z2 - z1)

    def bearing(self, x1, z1, x2, z2):
        lat = self.clat + (z1 + z2) / 120.0
        dx = (x2 - x1) * math.cos(math.radians(lat))
        return math.degrees(math.atan2(dx, z2 - z1)) % 360.0

    def on_land(self, x, z):
        if LAND is None or not self.mask_enabled:
            return True
        lat, lon = self.to_ll(x, z)
        return bool(LAND.is_land(lat, lon))


# ---------------------------------------------------------------------------
# The mission file
# ---------------------------------------------------------------------------
class Mission:
    """Sectioned view of a mission .ini that can add land units, formations and
    name overrides without disturbing anything else."""

    def __init__(self, path):
        self.path = path
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("cp1252")
        self.newline = "\r\n" if "\r\n" in text else "\n"
        text = text.replace("\r\n", "\n")
        parts = re.split(r"(?m)^(\[[^\]\n]+\])[ \t]*\n", text)
        self.sections = []                 # [(header or None, body)]
        if parts[0]:
            self.sections.append((None, parts[0]))
        for i in range(1, len(parts), 2):
            self.sections.append((parts[i], parts[i + 1]))
        env = self.body("[Environment]")
        try:
            self.geo = Geo(float(re.search(r"^MapCenterLatitude=([-\d.]+)", env, re.M).group(1)),
                           float(re.search(r"^MapCenterLongitude=([-\d.]+)", env, re.M).group(1)))
        except AttributeError:
            sys.exit(f"{path.name}: no MapCenterLatitude/Longitude in [Environment]")
        self.added = []                    # section names written this run

    # --- reading ---------------------------------------------------------
    def body(self, header):
        for h, b in self.sections:
            if h == header:
                return b
        return ""

    def units(self, side=None, cls=None):
        """[(section name, Type, x, z, body)] for the unit blocks asked for."""
        out = []
        pat = re.compile(rf"^\[({side or 'Taskforce[12]|Neutral'})({cls or '|'.join(UNIT_CLASSES)})(\d+)\]$")
        for h, b in self.sections:
            if not h or not pat.match(h):
                continue
            ty = re.search(r"^Type=(.+?)\s*$", b, re.M)
            pos = re.search(r"^RelativePositionInNM=([-\d.]+),[^,\n]*,([-\d.]+)", b, re.M)
            if not ty or not pos:
                continue
            out.append((h[1:-1], ty.group(1), float(pos.group(1)), float(pos.group(2)), b))
        return out

    def formations(self, side):
        """[(label, [members])] in file order."""
        out = []
        for line in self.body("[Mission]").splitlines():
            m = re.match(rf"^{side}_Formation\d+=(.*)$", line.strip())
            if m:
                head, _, tail = m.group(1).partition("|")
                out.append((tail.split("|")[0] if tail else "",
                            [u.strip() for u in head.split(",") if u.strip()]))
        return out

    def name_override(self, section):
        m = re.search(rf"^{section}NameOverride=(.+)$", self.body("[Language_en]"), re.M)
        return m.group(1).strip() if m else None

    # --- writing ---------------------------------------------------------
    def _mission_lines(self):
        i = next(i for i, (h, _) in enumerate(self.sections) if h == "[Mission]")
        return i, self.sections[i][1].split("\n")

    def _set_mission_lines(self, i, lines):
        self.sections[i] = ("[Mission]", "\n".join(lines))

    def bump(self, key, by, after_pattern):
        """key += by in [Mission]; the key is created after the first line
        matching after_pattern when the editor never wrote it."""
        i, lines = self._mission_lines()
        for n, line in enumerate(lines):
            m = re.match(rf"^{key}=(\d+)\s*$", line)
            if m:
                lines[n] = f"{key}={int(m.group(1)) + by}"
                self._set_mission_lines(i, lines)
                return int(m.group(1)) + by
        anchor = max((n for n, line in enumerate(lines) if re.match(after_pattern, line)), default=None)
        if anchor is None:
            sys.exit(f"{self.path.name}: cannot place {key} - no line matches {after_pattern!r}")
        lines.insert(anchor + 1, f"{key}={by}")
        self._set_mission_lines(i, lines)
        return by

    def set_mission_key(self, key, value):
        """key = value in [Mission]; the key must already exist."""
        i, lines = self._mission_lines()
        for n, line in enumerate(lines):
            if re.match(rf"^{key}=", line):
                lines[n] = f"{key}={value}"
                self._set_mission_lines(i, lines)
                return
        sys.exit(f"{self.path.name}: [Mission] has no {key}= line to set")

    def add_land_unit(self, side, uid, variant, x, z, heading, nation=None):
        n = max((int(re.match(r".*?(\d+)$", s).group(1)) for s, *_ in self.units(side, "LandUnit")),
                default=0) + 1
        name = f"{side}LandUnit{n}"
        body = (f"Type={uid}\nVariantReference={variant}\nUnlimitedFuel=False\nWeaponStatus=Free\n"
                f"CrewSkill=Trained\nMorale=3\nRelativePositionInNM={x:.2f},low,{z:.2f}\n")
        if nation:
            body += f"Nation={nation}\n"
        body += f"Heading={int(round(heading)) % 360}\n"
        # after the side's last land unit; else its last unit of any class
        idx = None
        for i, (h, _) in enumerate(self.sections):
            if h and re.match(rf"^\[{side}LandUnit\d+\]$", h):
                idx = i
        if idx is None:
            for i, (h, _) in enumerate(self.sections):
                if h and re.match(rf"^\[{side}(?:{'|'.join(UNIT_CLASSES)})\d+\]$", h):
                    idx = i
        if idx is None:
            sys.exit(f"{self.path.name}: {side} has no units at all - nothing to anchor a land unit to")
        prev_h, prev_b = self.sections[idx]
        if not prev_b.endswith("\n"):
            self.sections[idx] = (prev_h, prev_b + "\n")
        self.sections.insert(idx + 1, (f"[{name}]", body))
        self.bump(f"NumberOf{side}LandUnits", 1, rf"^NumberOf{side}\w+=")
        self.added.append(name)
        return name

    def add_formation(self, side, members, label):
        count = self.bump(f"{side}_NumberOfFormations", 1, r"^NumberOf\w+=")
        line = f"{side}_Formation{count}={','.join(members)}|{label}|Circle|1.5|OverrideSpawnPositions"
        i, lines = self._mission_lines()
        anchor = max((n for n, l in enumerate(lines) if re.match(rf"^{side}_(Formation\d+|NumberOfFormations)=", l)),
                     default=None)
        lines.insert(anchor + 1, line)
        self._set_mission_lines(i, lines)

    def add_name_override(self, section, name, short=None):
        i = next(i for i, (h, _) in enumerate(self.sections) if h == "[Language_en]")
        h, b = self.sections[i]
        extra = f"{section}NameOverride={name}\n"
        if short:
            extra += f"{section}ShortNameOverride={short[:12]}\n"
        if not b.endswith("\n"):
            b += "\n"
        self.sections[i] = (h, b + extra)

    # --- removing --------------------------------------------------------
    # The add path above only ever appends, so the numbering stays dense by
    # construction. Removal is the hard direction: the unit numbers are dense
    # AND referenced - by every <side>_FormationN line, by every NameOverride
    # key in the language blocks - so deleting one unit renumbers every later
    # unit of that side and every reference to it. remove_land_units does the
    # whole job in one place, and stops rather than leave anything dangling.
    UNIT_REF = r"(?<![A-Za-z0-9_])((?:Taskforce[12]|Neutral)(?:Vessel|Submarine|Aircraft|LandUnit|Biologic))(\d+)(?!\d)"

    def formation_specs(self, side):
        """[(line index in [Mission], key, [members], tail)] in file order;
        tail is everything from the first '|' on, kept verbatim."""
        _, lines = self._mission_lines()
        out = []
        for n, line in enumerate(lines):
            m = re.match(rf"^({side}_Formation\d+)=([^|]*)(.*)$", line)
            if m:
                out.append((n, m.group(1), [u.strip() for u in m.group(2).split(",") if u.strip()],
                            m.group(3)))
        return out

    def remove_land_units(self, side, names):
        """Delete land-unit sections of one side and renumber the survivors
        densely in file order. Every <side>_FormationN line loses the deleted
        members (a removal that would empty a formation is refused - a
        formation with no members is a lost site, not a smaller one), every
        [Language_*] NameOverride / ShortNameOverride key for a deleted unit
        goes, every surviving reference anywhere in the file is renamed to its
        new number, and NumberOf<side>LandUnits is set to what remains. Any
        line that still names a deleted unit afterwards stops the run.
        Returns {old section name: new section name} for the survivors."""
        names = set(names)
        if not names:
            return {}
        headers = {h[1:-1] for h, _ in self.sections if h}
        unknown = sorted(n for n in names if n not in headers)
        if unknown:
            sys.exit(f"{self.path.name}: cannot remove units that do not exist: {unknown}")
        bad = sorted(n for n in names if not re.match(rf"^{side}LandUnit\d+$", n))
        if bad:
            sys.exit(f"{self.path.name}: not {side} land units: {bad}")

        # 1. formations: drop the deleted members, refuse to empty one
        i, lines = self._mission_lines()
        for n, key, members, tail in self.formation_specs(side):
            kept = [u for u in members if u not in names]
            if members and not kept:
                label = tail.split("|")[1] if tail.count("|") >= 1 else ""
                sys.exit(f"{self.path.name}: removing {sorted(names & set(members))} would empty "
                         f"{key} ({label!r})")
            lines[n] = f"{key}={','.join(kept)}{tail}"
        self._set_mission_lines(i, lines)

        # 2. sections: drop the deleted blocks, number the survivors in file order
        survivors, mapping, count = [], {}, 0
        for h, b in self.sections:
            if h and h[1:-1] in names:
                continue
            if h and re.match(rf"^\[{side}LandUnit\d+\]$", h):
                count += 1
                mapping[h[1:-1]] = f"{side}LandUnit{count}"
                h = f"[{mapping[h[1:-1]]}]"
            survivors.append((h, b))
        self.sections = survivors

        pat = re.compile(rf"(?<![A-Za-z0-9_])({side}LandUnit)(\d+)(?!\d)")

        def rename(text, where):
            def sub(m):
                old = m.group(1) + m.group(2)
                if old in names:
                    sys.exit(f"{self.path.name}: {where} still names deleted unit {old}")
                if old not in mapping:
                    sys.exit(f"{self.path.name}: {where} names {old}, which is not a unit section")
                return mapping[old]
            return pat.sub(sub, text)

        # 3. language blocks: drop the deleted units' keys, then rename the rest;
        #    4. every other body (the [Mission] formations included) is renamed,
        #    and anything that still names a deleted unit is an error, not a leftover
        for k, (h, b) in enumerate(self.sections):
            if h and h.startswith("[Language_"):
                b = "\n".join(line for line in b.split("\n")
                              if not (pat.match(line) and re.match(r"^\w+=", line)
                                      and pat.match(line).group(1) + pat.match(line).group(2) in names))
            self.sections[k] = (h, rename(b, h or "preamble"))
        self.set_mission_key(f"NumberOf{side}LandUnits", count)
        self.added = [mapping.get(a, a) for a in self.added if a not in names]
        return mapping

    # An air-group line inside a unit block: <aircraft id>=Default,N or
    # SquadronN,N (or several joined by |), and the mods' Random,N form. The
    # value is what identifies it - an id can carry a space ("plaf_j16a
    # block3" is a real file), and no ordinary key has a value of this shape.
    AIRGROUP_LINE = re.compile(r"^[^=\n]+=(?:Default|Random|Squadron\d+),\d+"
                               r"(?:\|(?:Default|Random|Squadron\d+),\d+)*\s*$")

    def air_group(self, section):
        """(declared, [(aircraft id, spec)]): declared is True when the block
        carries CustomAirGroup=True; the list is what it names, empty for a
        base that spawns nothing."""
        body = self.body(f"[{section}]")
        declared = bool(re.search(r"^CustomAirGroup=True", body, re.M))
        lines = [(l.split("=", 1)[0], l.split("=", 1)[1].strip())
                 for l in body.split("\n") if self.AIRGROUP_LINE.match(l)]
        return declared, lines

    def set_custom_air_group(self, section, aircraft=()):
        """Give a unit an explicit air group: CustomAirGroup=True followed by
        the aircraft lines. With none, the base spawns nothing - that is the
        form the mission editor writes for an emptied base and the form the
        shipped missions use (Caron at Grenada's neutral airfield_small_1,
        forty such blocks across the vanilla missions and campaigns). Any
        air-group lines already in the block are replaced."""
        for k, (h, b) in enumerate(self.sections):
            if h == f"[{section}]":
                kept = [l for l in b.split("\n")
                        if not (l.startswith("CustomAirGroup=") or self.AIRGROUP_LINE.match(l))]
                # after the last line with content, so a blank line that
                # separates this block from the next stays where it was
                last = max((i for i, l in enumerate(kept) if l.strip()), default=-1)
                block = ["CustomAirGroup=True"] + [f"{uid}={spec}" for uid, spec in aircraft]
                body = "\n".join(kept[:last + 1] + block + kept[last + 1:])
                self.sections[k] = (h, body if body.endswith("\n") else body + "\n")
                return
        sys.exit(f"{self.path.name}: no section [{section}]")

    def set_name(self, name):
        """Name= in every [Language_*] block: what the in-game list shows."""
        done = 0
        for k, (h, b) in enumerate(self.sections):
            if h and h.startswith("[Language_"):
                b, n = re.subn(r"^Name=.*$", f"Name={name}", b, count=1, flags=re.M)
                done += n
                self.sections[k] = (h, b)
        if not done:
            sys.exit(f"{self.path.name}: no [Language_*] Name= line to set")

    def set_description(self, text):
        for k, (h, b) in enumerate(self.sections):
            if h == "[Language_en]":
                b, n = re.subn(r"^Description=.*$", f"Description={text}", b, count=1, flags=re.M)
                if not n:
                    b = b.rstrip("\n") + f"\nDescription={text}\n"
                self.sections[k] = (h, b)
                return
        sys.exit(f"{self.path.name}: no [Language_en] block")

    def text(self):
        out = []
        for h, b in self.sections:
            out.append(b if h is None else h + "\n" + b)
        return "".join(out).replace("\n", self.newline)

    def verify(self):
        """Loud guard: counts match sections, formations name real units, no
        duplicate headers, every added type resolves."""
        problems = []
        headers = [h for h, _ in self.sections if h]
        dupes = {h for h in headers if headers.count(h) > 1}
        if dupes:
            problems.append(f"duplicate sections: {sorted(dupes)}")
        body = self.body("[Mission]")
        for side in SIDES + ("Neutral",):
            for cls in UNIT_CLASSES:
                plural = "Aircraft" if cls == "Aircraft" else cls + "s"
                m = re.search(rf"^NumberOf{side}{plural}=(\d+)", body, re.M)
                have = len([h for h in headers if re.match(rf"^\[{side}{cls}\d+\]$", h)])
                want = int(m.group(1)) if m else 0
                if have != want:
                    problems.append(f"NumberOf{side}{plural}={want} but {have} sections")
            n_form = re.search(rf"^{side}_NumberOfFormations=(\d+)", body, re.M)
            lines = re.findall(rf"^{side}_Formation\d+=(.*)$", body, re.M)
            if n_form and int(n_form.group(1)) != len(lines):
                problems.append(f"{side}_NumberOfFormations={n_form.group(1)} but {len(lines)} lines")
            for spec in lines:
                for u in spec.split("|")[0].split(","):
                    if u.strip() and f"[{u.strip()}]" not in headers:
                        problems.append(f"formation names missing unit {u.strip()}")
        for name in self.added:
            ty = re.search(r"^Type=(.+)$", self.body(f"[{name}]"), re.M)
            if not ty or winning_file(f"land_units/{ty.group(1).strip()}.ini") is None:
                problems.append(f"{name}: Type does not resolve")
        # A formation with no members is a site that has silently vanished.
        for side in SIDES + ("Neutral",):
            for _, key, members, _ in self.formation_specs(side):
                if not members:
                    problems.append(f"{key} has no members")
        # Numbering is dense and in file order per side and class - what the
        # game expects and what the removal path relies on.
        for side in SIDES + ("Neutral",):
            for cls in UNIT_CLASSES:
                nums = [int(re.match(rf"^\[{side}{cls}(\d+)\]$", h).group(1))
                        for h in headers if re.match(rf"^\[{side}{cls}\d+\]$", h)]
                if nums != list(range(1, len(nums) + 1)):
                    problems.append(f"{side}{cls} numbering is not dense and in order: {nums[:8]}...")
        # Every unit named anywhere - a language key, a formation, anything -
        # must be a section that exists.
        header_set = set(headers)
        for h, b in self.sections:
            for m in re.finditer(self.UNIT_REF, b):
                if f"[{m.group(1)}{m.group(2)}]" not in header_set:
                    problems.append(f"{h or 'preamble'} names {m.group(1)}{m.group(2)}, which does not exist")
        return sorted(set(problems))


# ---------------------------------------------------------------------------
# Site analysis
# ---------------------------------------------------------------------------
def side_nation(mission, side):
    """Majority nation of a side, from the unit-id prefixes of everything it fields."""
    tally = {}
    for _, ty, *_ in mission.units(side):
        n = prefix_nation(ty)
        if n:
            tally[n] = tally.get(n, 0) + 1
    return max(tally, key=tally.get) if tally else None


def threat_bearing(mission, geo, side, x, z):
    """Distance-weighted mean bearing from (x,z) to the enemy side's units."""
    enemy = "Taskforce2" if side == "Taskforce1" else "Taskforce1"
    sx = sz = 0.0
    for _, _, ex, ez, _ in mission.units(enemy):
        d = max(geo.dist(x, z, ex, ez), 5.0)
        b = math.radians(geo.bearing(x, z, ex, ez))
        sx += math.sin(b) / d
        sz += math.cos(b) / d
    if sx == 0 and sz == 0:
        return 0.0
    return math.degrees(math.atan2(sx, sz)) % 360.0


def find_sites(mission, geo, side, cover_radius):
    """Every group of land units on a side, with what it is and what it has."""
    land = mission.units(side, "LandUnit")
    by_name = {s: (ty, x, z, body) for s, ty, x, z, body in land}
    grouped = set()
    sites = []

    def make(label, members):
        assets = [m for m in members if is_asset(unit_info(by_name[m][0]), by_name[m][0])]
        core = assets or members
        cx = sum(by_name[m][1] for m in core) / len(core)
        cz = sum(by_name[m][2] for m in core) / len(core)
        radius = max([geo.dist(cx, cz, by_name[m][1], by_name[m][2]) for m in core] + [0.3])
        # An explicit Nation= on an asset wins; otherwise the site's members
        # vote by unit-id prefix, assets counting double, so a Russian site
        # that fields Iranian-built Shahed launchers stays Russian.
        nation = None
        for m in assets:
            nm = re.search(r"^Nation=(.+)$", by_name[m][3], re.M)
            if nm:
                nation = norm_nation(nm.group(1))
                break
        if nation is None:
            votes = {}
            for m in members:
                n = prefix_nation(by_name[m][0])
                if n:
                    votes[n] = votes.get(n, 0) + (2 if m in assets else 1)
            nation = max(votes, key=votes.get) if votes else None
        return {"side": side, "label": label, "members": members, "assets": assets,
                "x": cx, "z": cz, "radius": min(radius, 3.0), "nation": nation,
                "types": [by_name[m][0] for m in members],
                "nation_key": next((re.search(r"^Nation=(.+)$", by_name[m][3], re.M).group(1).strip()
                                    for m in assets if re.search(r"^Nation=", by_name[m][3], re.M)), None),
                "offshore": bool(assets) and all(unit_info(by_name[m][0])["subtype"] == "OilRig" for m in assets)}

    for label, members in mission.formations(side):
        lu = [m for m in members if m in by_name]
        if not lu:
            continue
        grouped.update(lu)
        sites.append(make(label, lu))
    for s, ty, x, z, body in land:
        if s not in grouped:
            info = unit_info(ty)
            label = mission.name_override(s) or (info["tacview"] if info and info["tacview"] else ty)
            sites.append(make(label, [s]))

    # what each site already has: every AD unit of this side within reach
    for site in sites:
        have = {}
        for s, ty, x, z, _ in land:
            layer = ad_layer(unit_info(ty))
            if layer in (None, "fcr"):
                continue
            if s in site["members"] or \
                    geo.dist(site["x"], site["z"], x, z) <= cover_radius + site["radius"]:
                have[layer] = have.get(layer, 0) + 1
        site["have"] = have
    return sites


def site_matches(site, wanted):
    w = wanted.lower()
    return (w in site["label"].lower() or any(w in m.lower() for m in site["members"])
            or any(w in t.lower() for t in site["types"]))


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------
class Planner:
    def __init__(self, mission, args):
        self.m = mission
        self.geo = mission.geo
        self.args = args
        self.occupied = [(x, z) for _, _, x, z, _ in mission.units(cls="LandUnit")]
        self.notes = []

    # --- placement helpers ------------------------------------------------
    def clear_of_others(self, x, z, min_sep=0.12):
        return all(self.geo.dist(x, z, ox, oz) >= min_sep for ox, oz in self.occupied)

    def spot(self, ax, az, bearing, dist, footprint=0.0, min_sep=0.12):
        """A point on land (when the mask is available) near the wanted
        bearing/distance, with a footprint of land around it and no other unit
        on top of it. Rotates first, then closes in, then gives up honestly."""
        tried = 0
        for shrink in (1.0, 0.8, 0.6, 0.45, 0.3):
            for k in range(0, 13):
                for sign in ((1,) if k == 0 else (1, -1)):
                    b = bearing + sign * k * 15.0
                    x, z = self.geo.offset(ax, az, b, dist * shrink)
                    x, z = round(x, 2), round(z, 2)     # judge the coordinates that get written
                    tried += 1
                    if not self.geo.on_land(x, z):
                        continue
                    if footprint and not all(self.geo.on_land(*self.geo.offset(x, z, d, footprint))
                                             for d in range(0, 360, 60)):
                        continue
                    if not self.clear_of_others(x, z, min_sep):
                        continue
                    return x, z, b, True
        x, z = self.geo.offset(ax, az, bearing, dist)
        return x, z, bearing, False

    def take(self, x, z):
        self.occupied.append((x, z))

    # --- the plan for one site ---------------------------------------------
    def plan_site(self, site, doctrine, era, posture, layers_wanted, coastal, composite, force):
        """[(group label, [unit dicts])] for the site, or [] with notes."""
        rng = random.Random(f"{site['side']}|{site['label']}|{era}|{posture}")
        jitter = rng.uniform(-12.0, 12.0)
        table = DOCTRINES[doctrine][era]
        have = dict(site["have"])
        want = dict(POSTURES[posture])
        if coastal:
            want["coastal"] = 1
        if layers_wanted:
            want = {k: v for k, v in want.items() if k in layers_wanted}
        threat = (self.args.threat_bearing if self.args.threat_bearing is not None
                  else threat_bearing(self.m, self.geo, site["side"], site["x"], site["z"]))
        site["threat"] = threat
        rs = site["radius"]
        groups, skipped = [], []
        nation = site["nation"]
        nation_key = site["nation_key"]

        def unit(uid, x, z, heading, tag):
            return {"type": uid, "variant": pick_variant(uid, nation), "x": x, "z": z,
                    "heading": heading % 360.0, "tag": tag, "nation": nation_key}

        def ring(layer, radius, count, spread=360.0, centre_bearing=None):
            ids = resolve_units(table.get(layer, []), count, layer)
            if not ids:
                skipped.append(f"{layer}: doctrine {doctrine}/{era} has nothing that resolves as {layer}")
                return []
            out = []
            start = (threat if centre_bearing is None else centre_bearing) + jitter
            step = spread / count
            for i, uid in enumerate(ids):
                b = start - spread / 2 + step * (i + 0.5) if spread < 360 else start + step * i
                x, z, b2, ok = self.spot(site["x"], site["z"], b, radius)
                if not ok:
                    skipped.append(f"{layer} {uid}: no land near bearing {b:.0f} at {radius:.1f} nm")
                    continue
                self.take(x, z)
                out.append(unit(uid, x, z, self.geo.bearing(site["x"], site["z"], x, z), layer))
            return out

        def battery(layer, bearing, dist):
            specs = table.get(layer, [])
            if composite:
                specs = [s for s in specs if s["composite"]] + [s for s in specs if not s["composite"]]
            spec = resolve_battery(specs)
            if spec is None:
                why = "; ".join(p for p in (battery_problem(s) for s in specs) if p) or "no entry"
                skipped.append(f"{layer}: no usable battery ({why})")
                return None, []
            ring_r = tel_ring_radius(spec)
            cx, cz, b, ok = self.spot(site["x"], site["z"], bearing + jitter, dist, footprint=ring_r + 0.1,
                                      min_sep=ring_r + 0.2)
            if not ok:
                skipped.append(f"{layer} {spec['label']}: no land footprint near bearing {bearing:.0f} "
                               f"at {dist:.1f} nm")
                return spec, []
            out = []
            if spec["composite"]:
                self.take(cx, cz)
                out.append(unit(spec["composite"], cx, cz, threat, f"{layer}:site"))
                return spec, out
            if spec["radar"]:
                self.take(cx, cz)
                out.append(unit(spec["radar"], cx, cz, threat, f"{layer}:fcr"))
            tels = [uid for uid, n in spec["tels"] for _ in range(n)]
            for i, uid in enumerate(tels):
                tb = threat + 360.0 * i / len(tels) + jitter
                x, z = self.geo.offset(cx, cz, tb, ring_r)
                if not self.geo.on_land(x, z):     # footprint was checked; keep the star anyway
                    x, z, tb, _ = self.spot(cx, cz, tb, ring_r, min_sep=0.08)
                self.take(x, z)
                out.append(unit(uid, x, z, tb, f"{layer}:tel"))
            for i, uid in enumerate(spec["search"]):
                x, z, sb, ok = self.spot(cx, cz, threat + 180 + 40 * i, ring_r + 0.45, min_sep=0.15)
                if ok:
                    self.take(x, z)
                    out.append(unit(uid, x, z, threat, f"{layer}:search"))
            return spec, out

        def need(layer):
            return force or have.get(layer, 0) < (1 if layer in ("medium", "area", "ew", "bmd", "coastal")
                                                  else want[layer])

        # gun ring on the perimeter, SHORAD a mile out, both bracketing the threat
        ad = []
        if "aaa" in want and need("aaa"):
            ad += ring("aaa", rs + 0.7, max(1, want["aaa"] - (0 if force else have.get("aaa", 0))))
        if "shorad" in want and need("shorad"):
            ad += ring("shorad", rs + 1.4, max(1, want["shorad"] - (0 if force else have.get("shorad", 0))),
                       spread=300.0)
        if "medium" in want and need("medium"):
            spec, units = battery("medium", threat + 35, rs + 2.8)
            ad += units
        if "area" in want and need("area"):
            for i in range(want["area"]):
                spec, units = battery("area", threat - 20 + 130 * i, rs + 4.5)
                ad += units
        if "ew" in want and need("ew"):
            for i in range(want["ew"]):
                ids = resolve_units(table.get("ew", []), 1)
                if not ids:
                    skipped.append(f"ew: doctrine {doctrine}/{era} has no search radar")
                    break
                x, z, b, ok = self.spot(site["x"], site["z"], threat + 90 + 180 * i + jitter, rs + 3.0,
                                        min_sep=0.2)
                if ok:
                    self.take(x, z)
                    ad.append(unit(ids[0], x, z, threat, "ew"))
                else:
                    skipped.append("ew: no land for the search radar")
        if "bmd" in want and need("bmd"):
            spec, units = battery("bmd", threat + 180, rs + 2.5)
            ad += units
        if ad:
            groups.append((f"{site['label']} Air Defence", ad))
        if "coastal" in want and need("coastal"):
            spec, units = battery("coastal", threat, rs + 2.0)
            if units:
                groups.append((f"{site['label']} Coastal Battery", units))
        site["skipped"] = list(dict.fromkeys(skipped))
        return groups

    def build_site(self, template, x, z, side, doctrine, era, nation, nation_key, label):
        """The assets of a new site, on a small ring around its centre."""
        table = DOCTRINES[doctrine][era]
        rows = SITE_TEMPLATES[template]
        rng = random.Random(f"build|{label}")
        out, skipped = [], []
        support_iter = iter(resolve_units(table.get("support", []), 6))
        for i, row in enumerate(rows):
            if row == "@support":
                uid = next(support_iter, None)
            elif row == "@ew":
                uid = next(iter(resolve_units(table.get("ew", []), 1)), None)
            elif row == "@coastal":
                spec = resolve_battery(table.get("coastal", []))
                uid = None
                if spec:
                    for tel, n in spec["tels"]:
                        for _ in range(n):
                            bx, bz, b, ok = self.spot(x, z, rng.uniform(0, 360), 0.25, min_sep=0.08)
                            if ok:
                                self.take(bx, bz)
                                out.append({"type": tel, "variant": pick_variant(tel, nation), "x": bx,
                                            "z": bz, "heading": b, "tag": "coastal:tel", "nation": nation_key})
                    if spec["radar"]:
                        uid = spec["radar"]
            elif row == "@tbm":
                uid = next(iter(resolve_units(TBM_BY_DOCTRINE.get(doctrine, []), 1)), None)
            elif row == "@drone":
                uid = next(iter(resolve_units(DRONE_BY_DOCTRINE.get(doctrine, []), 1)), None)
            else:
                uid = row if unit_info(row) else None
            if uid is None:
                skipped.append(f"{row}: nothing resolves for {doctrine}/{era}")
                continue
            if i == 0 and row != "@coastal":
                bx, bz = x, z
            else:
                bx, bz, b, ok = self.spot(x, z, rng.uniform(0, 360), rng.uniform(0.15, 0.35), min_sep=0.08)
                if not ok:
                    skipped.append(f"{uid}: no land next to the site centre")
                    continue
            self.take(bx, bz)
            out.append({"type": uid, "variant": pick_variant(uid, nation), "x": bx, "z": bz,
                        "heading": rng.uniform(0, 360), "tag": "asset", "nation": nation_key})
        return out, skipped


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def describe_unit(geo, u):
    lat, lon = geo.to_ll(u["x"], u["z"])
    info = unit_info(u["type"])
    return (f"      {u['tag']:14s} {u['type']:30s} {u['variant']:9s} "
            f"({u['x']:.2f},{u['z']:.2f})  {lat:.3f},{lon:.3f}  hdg {u['heading']:.0f}"
            f"   <- {info['provider'] if info else '?'}")


# The units worth a name on the tacmap: a battery's radar or composite site,
# and the search radar. Launchers keep their type's own display name.
NAMED_ROLES = {
    "area:fcr": ("SAM Battery", "SAM BTY"), "area:site": ("SAM Battery", "SAM BTY"),
    "medium:fcr": ("Medium SAM Battery", "MED BTY"), "medium:site": ("Medium SAM Battery", "MED BTY"),
    "bmd:fcr": ("BMD Battery", "BMD BTY"), "bmd:site": ("BMD Battery", "BMD BTY"),
    "coastal:fcr": ("Coastal Battery", "CST BTY"), "coastal:site": ("Coastal Battery", "CST BTY"),
    "ew": ("EW Radar", "EW RADAR"),
}


def apply_groups(mission, site_side, groups, nation_key):
    """Write the planned groups into the mission; returns the section names."""
    written = []
    for label, units in groups:
        members = []
        for u in units:
            name = mission.add_land_unit(site_side, u["type"], u["variant"], u["x"], u["z"],
                                         u["heading"], nation_key)
            members.append(name)
            role = NAMED_ROLES.get(u["tag"])
            if role:
                site_label = label.replace(" Air Defence", "").replace(" Coastal Battery", "")
                mission.add_name_override(name, f"{site_label} {role[0]}", role[1])
        if members:
            mission.add_formation(site_side, members, label)
        written.extend(members)
    return written


def print_catalog(doctrines, era):
    for d in doctrines:
        table = DOCTRINES[d][era]
        print(f"=== {d} / {era}")
        for layer in ("aaa", "shorad", "medium", "area", "ew", "bmd", "coastal", "support"):
            entry = table.get(layer)
            if not entry:
                print(f"   {layer:8s} -")
                continue
            if isinstance(entry[0], dict):
                spec = resolve_battery(entry)
                if spec is None:
                    print(f"   {layer:8s} NONE USABLE: " +
                          "; ".join(p for p in (battery_problem(s) for s in entry) if p))
                    continue
                units = ([spec["composite"]] if spec["composite"] else
                         ([spec["radar"]] if spec["radar"] else []) +
                         [f"{u}x{n}" for u, n in spec["tels"]] + spec["search"])
                src = unit_info(spec["composite"] or spec["radar"] or spec["tels"][0][0])["provider"]
                print(f"   {layer:8s} {spec['label']}: {', '.join(units)}   <- {src}")
            else:
                ring_layer = layer if layer in ("aaa", "shorad") else None
                ok = [(u, unit_info(u)["provider"]) for u in resolve_units(entry, len(entry), ring_layer)]
                ok = list(dict.fromkeys(ok))
                miss = [u for u in entry if not unit_info(u)]
                wrong = misfiled(entry, ring_layer) if ring_layer else []
                print(f"   {layer:8s} " + ", ".join(f"{u} <- {p}" for u, p in ok) +
                      (f"   (unavailable: {', '.join(miss)})" if miss else "") +
                      (f"   (misfiled: {', '.join(f'{u} is {l}' for u, l in wrong)})" if wrong else ""))


# ---------------------------------------------------------------------------
def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mission", default=None, help="mission name without .ini (default: the active mission)")
    ap.add_argument("--write", action="store_true", help="apply the plan (default is a dry run)")
    ap.add_argument("--side", choices=SIDES + ("both",), default="both")
    ap.add_argument("--around", action="append", default=[],
                    help="only sites whose label, section or type contains this (repeatable)")
    ap.add_argument("--force", action="store_true", help="add every layer even where one already exists")
    ap.add_argument("--posture", choices=sorted(POSTURES), default="standard")
    ap.add_argument("--era", choices=("modern", "cold-war"), default="modern")
    ap.add_argument("--doctrine", choices=sorted(DOCTRINES), default=None,
                    help="override the doctrine chosen from the site's nation")
    ap.add_argument("--nation", default=None, help="override the nation used to pick variants and doctrine")
    ap.add_argument("--layers", default=None,
                    help="comma list restricting layers: aaa,shorad,medium,area,ew,bmd,coastal")
    ap.add_argument("--coastal", action="store_true", help="add an anti-ship battery toward the threat")
    ap.add_argument("--composite", action="store_true",
                    help="prefer single-unit composite SAM sites over radar-plus-launcher batteries")
    ap.add_argument("--cover-radius", type=float, default=6.0,
                    help="nm beyond a site's edge within which an existing air-defence unit "
                         "counts for it (default 6)")
    ap.add_argument("--threat-bearing", type=float, default=None, help="override the computed threat axis")
    ap.add_argument("--include-offshore", action="store_true",
                    help="also try rigs and other assets at sea (normally skipped)")
    ap.add_argument("--build", choices=sorted(SITE_TEMPLATES), default=None,
                    help="create a new site of this template at --at and defend it")
    ap.add_argument("--at", nargs=2, type=float, metavar=("LAT", "LON"), default=None,
                    help="where --build stands, decimal degrees (south and west negative)")
    ap.add_argument("--label", default=None, help="name for the built site")
    ap.add_argument("--list-sites", action="store_true", help="print the site analysis and stop")
    ap.add_argument("--catalog", action="store_true", help="print what every doctrine resolves to and stop")
    return ap.parse_args()


def main():
    args = parse_args()
    if args.catalog:
        print_catalog([args.doctrine] if args.doctrine else sorted(DOCTRINES), args.era)
        return

    name = args.mission or active_mission()
    path = MISSIONS / f"{name}.ini"
    if not path.exists():
        sys.exit(f"no such mission: {path}")
    mission = Mission(path)
    geo = mission.geo
    print(f"mission: {name}   datum {geo.clat},{geo.clon}   era {args.era}   posture {args.posture}"
          f"   land mask: {'on' if LAND else 'OFF (pip install global-land-mask numpy)'}")

    layers = set(args.layers.split(",")) if args.layers else None
    planner = Planner(mission, args)
    sides = SIDES if args.side == "both" else (args.side,)
    plans = []          # (site, doctrine, groups)

    # --- build a new site first, so it is then defended like any other -------
    if args.build:
        if not args.at or args.side == "both":
            sys.exit("--build needs --at LAT,LON and a single --side")
        lat, lon = args.at
        bx, bz = (lon - geo.clon) * 60.0, (lat - geo.clat) * 60.0
        if not geo.on_land(bx, bz):
            sys.exit(f"--at {lat},{lon} is not on land")
        nation = norm_nation(args.nation) if args.nation else side_nation(mission, args.side) or "usa"
        doctrine = args.doctrine or doctrine_for(nation, args.era)
        label = args.label or f"{args.build.replace('_', ' ').title()} {int(abs(lat))}{'S' if lat < 0 else 'N'}"
        nation_key = args.nation.strip().lower() if args.nation else None
        assets, skipped = planner.build_site(args.build, bx, bz, args.side, doctrine, args.era, nation,
                                             nation_key, label)
        if not assets:
            sys.exit(f"--build {args.build}: nothing resolved ({'; '.join(skipped)})")
        print(f"\n== BUILD {label} ({args.side}, {args.build}, doctrine {doctrine}) at {lat},{lon}")
        for u in assets:
            print(describe_unit(geo, u))
        for s in skipped:
            print(f"      note: {s}")
        if args.write:
            members = apply_groups(mission, args.side, [(f"{label} Site", assets)], nation_key)
        else:
            members = []
        site = {"side": args.side, "label": label, "members": members, "assets": members, "x": bx, "z": bz,
                "radius": 0.4, "nation": nation, "nation_key": nation_key, "types": [u["type"] for u in assets],
                "offshore": False, "have": {}}
        groups = planner.plan_site(site, doctrine, args.era, args.posture, layers, args.coastal,
                                   args.composite, True)
        plans.append((site, doctrine, groups))

    # --- every existing site ----------------------------------------------------
    else:
        for side in sides:
            fallback = side_nation(mission, side)
            for site in find_sites(mission, geo, side, args.cover_radius):
                wanted = not args.around or any(site_matches(site, w) for w in args.around)
                if args.list_sites or not wanted:
                    if args.list_sites:
                        have = ", ".join(f"{k}x{v}" for k, v in sorted(site["have"].items())) or "nothing"
                        kind = "asset" if site["assets"] else "no asset"
                        print(f"  {side} {site['label']!r:40s} {len(site['members']):2d} units  {kind:8s}"
                              f"  nation {site['nation'] or fallback or '?':10s}  has: {have}")
                    continue
                if not site["assets"]:
                    continue
                if site["offshore"] and not args.include_offshore:
                    continue
                nation = norm_nation(args.nation) if args.nation else (site["nation"] or fallback or "usa")
                site["nation"] = nation
                doctrine = args.doctrine or doctrine_for(nation, args.era)
                force = args.force
                groups = planner.plan_site(site, doctrine, args.era, args.posture, layers, args.coastal,
                                           args.composite, force)
                if groups or site.get("skipped"):
                    plans.append((site, doctrine, groups))
        if args.list_sites:
            return

    # --- report ------------------------------------------------------------------
    total = 0
    for site, doctrine, groups in plans:
        have = ", ".join(f"{k}x{v}" for k, v in sorted(site["have"].items())) or "nothing"
        print(f"\n== {site['side']} {site['label']}  ({len(site['members'])} units, nation {site['nation']}, "
              f"doctrine {doctrine}, has {have}, threat {site.get('threat', 0):.0f} deg)")
        for label, units in groups:
            print(f"   + {label}: {len(units)} units")
            for u in units:
                print(describe_unit(geo, u))
            total += len(units)
        for s in site.get("skipped", []):
            print(f"      note: {s}")
        if not groups:
            print("   nothing to add")
    if not plans:
        print("\nno site needs anything - every asset already has its layers (or nothing matched)")
        return
    print(f"\n{total} unit(s) planned")
    if not args.write:
        print("dry run - pass --write to apply")
        return
    if not total:
        print("nothing to write")
        return

    for site, doctrine, groups in plans:
        apply_groups(mission, site["side"], groups, site["nation_key"])
    problems = mission.verify()
    if problems:
        sys.exit("NOT written - the result fails its own checks:\n  " + "\n  ".join(problems))
    path.write_bytes(mission.text().encode("utf-8"))
    print(f"written: {path}  (+{len(mission.added)} land units)")


if __name__ == "__main__":
    main()
