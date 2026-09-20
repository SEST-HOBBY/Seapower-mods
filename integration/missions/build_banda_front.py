#!/usr/bin/env python3
"""Generate SEST Banda Front: the Indo-Pacific land-asset showcase narrowed
to the arc from Borneo and Java through Sulawesi, the Moluccas, Timor and
Papua to northern Australia and the Bismarck Sea, with the Sulu corner
(Sabah, Zamboanga, Jolo, Marawi, Balabac) kept exactly as the showcase has it.

Compared with SEST Indo-Pacific Land Assets:

  - The Philippines north of Mindanao, the Spratly and Paracel bases, Natuna,
    Australia south of Tindal and the Solomons are gone. The datum is the same,
    so a site keeps the same RelativePositionInNM in both files.
  - Borneo and Java get their own detail: Malaysian, Bruneian and Indonesian
    bases, refineries, LNG complexes, ports and power stations, plus PLA
    lodgements at the Chinese-financed industrial parks (Tanah Kuning,
    Kendawangan, Batang, Tanjung Jati) and militant camps at Lahad Datu and
    Poso.
  - Civil traffic follows the real lanes: the Lombok-Makassar VLCC and iron-ore
    route, the Java Sea container run, the Darwin LNG route through the Banda
    and Molucca Seas, Torres Strait, Vitiaz Strait, the Pelni liners, the
    Bali-Lombok and Surabaya-Banjarmasin ferries, the Zamboanga-Sandakan run,
    and fishing fleets in the Arafura, Timor, Banda and Celebes Seas. Every leg
    of every lane is checked against the land mask.
  - Modern airliners in regional liveries cross the zone on real city pairs,
    with light aircraft and helicopters on the short hops (Tiwi Islands, Banda
    Neira, the PNG highlands, the Timor Sea rigs, the Mahakam delta).
  - Western Mindanao Command fields an air wing: A-10C, F-16CM, MQ-9A and
    MQ-9 ER, with Marine UH-1Y and a Navy HH-60 CSAR detachment.
  - The US destroyers stand in the Celebes Sea, and a PLAN amphibious group
    lies off the Batang lodgement in the Java Sea.

    python3 integration/missions/build_banda_front.py              # write the mission
    python3 integration/missions/build_banda_front.py --density standard
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_indo_pacific_showcase as base                       # noqa: E402
from build_indo_pacific_showcase import TF1, TF2, NEU, to_xz     # noqa: E402
from build_land_defence import Geo, LAND                         # noqa: E402
from sea_routes import Router                                    # noqa: E402

NAME = "SEST Banda Front"
OUT = base.MISSIONS / f"{NAME}.ini"
LANES = base.MISSIONS / "banda_front_lanes.json"      # routed lanes, keyed on their via points
DESCRIPTION = ("Sandbox, narrowed: Borneo and Java through the Moluccas and Papua to northern Australia. "
               "RAAF bases with Patriot/THAAD/NASAMS, US Marines and a French battle group at Darwin, "
               "an A-10/F-16/MQ-9 wing at Zamboanga, PLA lodgements at the Chinese industrial parks of "
               "Kalimantan, Java, Halmahera and Sulawesi, a Russian S-400 regiment at Biak, DF-21/26 "
               "batteries in Papua, and TNI, RMAF and Bruneian bases, refineries, LNG plants and ports. "
               "Civil shipping follows the real lanes; airliners cross on real city pairs.")

# ---------------------------------------------------------------------------
# Sites: the showcase's, kept inside the zone, plus the Borneo/Java detail.
# ---------------------------------------------------------------------------
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = -15.0, 9.0, 105.0, 153.0
DROP = {"Ranai Air Base (TNI-AU)"}          # Natuna: inside the box, outside the picture

SITES = [s for s in base.SITES
         if LAT_MIN <= s["lat"] <= LAT_MAX and LON_MIN <= s["lon"] <= LON_MAX and s["label"] not in DROP]


def site(*args, **kwargs):
    base.site(*args, **kwargs)
    SITES.append(base.SITES.pop())


# ---------------- NEUTRAL: Borneo (Sabah, Sarawak, Brunei, Kalimantan) ----
site("RMAF Labuan", NEU, 5.3007, 115.2500, "nato",
     [("RMAF Labuan", ["airfield_small_1", "nato_radar", "raf_rapier_launcher", "tgt_fueltanks_small"])],
     nation_key="malaysia", spread=0.35)
site("RMAF Kuching", NEU, 1.4847, 110.3470, "nato",
     [("RMAF Kuching", ["airfield_small_1", "nato_fps-20_radar", "nato_aaa_gdf", "tgt_fueltanks_small"])],
     nation_key="malaysia", spread=0.35)
site("Bintulu LNG Complex", NEU, 3.2400, 113.0700, "nato",
     [("Bintulu LNG Complex", ["tgt_refinery_small", ("tgt_fueltanks_large", 2), "Oil_pump", "warehouses_1"])],
     nation_key="malaysia", spread=0.25)
site("Miri Lutong Oil Terminal", NEU, 4.4600, 114.0100, "nato",
     [("Miri Lutong Oil Terminal", ["tgt_refinery_small_3", ("Oil_pump", 3), "tgt_fueltanks_medium"])],
     nation_key="malaysia", spread=0.25)
site("Sandakan Naval Station (RMN)", NEU, 5.8394, 118.1170, "nato",
     [("Sandakan Naval Station (RMN)", ["nv_pt_boats_docks_small", "warehouses_2", "tgt_fueltanks_small",
                                        "nato_radar"])],
     nation_key="malaysia", spread=0.2)
site("Tawau ESSCOM Post", NEU, 4.2500, 117.8900, "nato",
     [("Tawau ESSCOM Post", ["FOB", "nv_watchtower", "Bunker_2", "warehouses_1"])],
     nation_key="malaysia", spread=0.15)
site("Seria Oil Field", NEU, 4.6060, 114.3230, "nato",
     [("Seria Oil Field", [("Oil_pump", 4), "tgt_fueltanks_small_brown", "tgt_industry_buildings_2_brown"])],
     nation_key="brunei", spread=0.2)
site("Pontianak Supadio (TNI-AU)", NEU, -0.1507, 109.4039, "export",
     [("Pontianak Supadio (TNI-AU)", ["airfield_small_1", "wp_p-18_radar", "nv_s-60", "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.35)
site("Tarakan Oil Terminal", NEU, 3.3000, 117.6300, "export",
     [("Tarakan Oil Terminal", [("Oil_pump", 2), "tgt_fueltanks_small", "warehouses_1"])],
     nation_key="indonesia", spread=0.2)
site("Nusantara Capital (IKN)", NEU, -0.9700, 116.7100, "export",
     [("Nusantara Capital (IKN)", ["civ_comm_buildings", "tgt_industry_buildings_1", "civ_radiostation",
                                   "warehouses_1"])],
     nation_key="indonesia", spread=0.25)
site("Banjarmasin Coal Terminal", NEU, -3.3300, 114.5900, "export",
     [("Banjarmasin Coal Terminal", ["warehouses_2", "tgt_industry_buildings_2", "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.2)

# ---------------- NEUTRAL: Java, Bali ---------------------------------------
site("Halim Perdanakusuma Air Base (TNI-AU)", NEU, -6.2666, 106.8910, "export",
     [("Halim Perdanakusuma Air Base (TNI-AU)", ["airfield_us", "tgt_fueltanks_medium", "Ammo_Bunker"]),
      ("Kohanudnas NASAMS Battery", ["usa_SLAMRAAM_radar", ("usa_SLAMRAAM_launcher", 2), "nato_aaa_gdf"])],
     nation_key="indonesia", spread=0.4)
site("Tanjung Priok Port", NEU, -6.1050, 106.8800, "export",
     [("Tanjung Priok Port", ["warehouses_2", "warehouses_3", "tgt_fueltanks_large", "civ_comm_buildings"])],
     nation_key="indonesia", spread=0.25)
site("Cilegon Steel Works", NEU, -5.9800, 106.0200, "export",
     [("Cilegon Steel Works", ["tgt_industry_buildings_4", "tgt_industry_buildings_1", "Coal_PowerPlant",
                               "warehouses_1"])],
     nation_key="indonesia", spread=0.25)
site("Balongan Refinery", NEU, -6.3800, 108.4000, "export",
     [("Balongan Refinery", ["Oil_refinery", ("tgt_fueltanks_large", 2), "Oil_pump"])],
     nation_key="indonesia", spread=0.25)
site("Cilacap Refinery", NEU, -7.7200, 109.0100, "export",
     [("Cilacap Refinery", ["Oil_refinery", "tgt_fueltanks_large", "tgt_refinery_small_3", "Oil_pump"])],
     nation_key="indonesia", spread=0.25)
site("Tanjung Emas Port Semarang", NEU, -6.9450, 110.4250, "export",
     [("Tanjung Emas Port Semarang", ["warehouses_2", "tgt_fueltanks_small", "civ_comm_buildings"])],
     nation_key="indonesia", spread=0.2)
site("Iswahyudi Air Base Madiun (TNI-AU)", NEU, -7.6157, 111.4343, "export",
     [("Iswahyudi Air Base Madiun (TNI-AU)", ["airfield_us", "nato_radar", ("raf_rapier_launcher", 2),
                                              "tgt_fueltanks_medium", "Ammo_Bunker"])],
     nation_key="indonesia", spread=0.4)
site("Juanda Air Base Surabaya (TNI-AL)", NEU, -7.3798, 112.7869, "export",
     [("Juanda Air Base Surabaya (TNI-AL)", ["airfield_small_1", "nato_radar", "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.35)
site("Koarmada II Tanjung Perak", NEU, -7.2000, 112.7300, "export",
     [("Koarmada II Tanjung Perak", ["nv_pt_boats_docks", "warehouses_2", "tgt_fueltanks_medium", "nato_aaa_gdf"])],
     nation_key="indonesia", spread=0.25)
site("Suramadu Bridge", NEU, -7.1800, 112.7800, "export",
     [("Suramadu Bridge", ["civ_tgt_bridge_6_part"])], mask=False, nation_key="indonesia")
site("Paiton Power Station", NEU, -7.7100, 113.5800, "export",
     [("Paiton Power Station", ["Coal_PowerPlant", "tgt_industry_buildings_2_brown"])],
     nation_key="indonesia", spread=0.2)
site("Ngurah Rai Airport Bali", NEU, -8.7482, 115.1672, "export",
     [("Ngurah Rai Airport Bali", ["airfield_small_1", "civ_comm_buildings", "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.3)
site("Ketapang Ferry Port", NEU, -8.1450, 114.3960, "export",
     [("Ketapang Ferry Port", ["warehouses_1", "tgt_fueltanks_small"])],
     nation_key="indonesia", spread=0.15)

# ---------------- RED: PLA lodgements at the Chinese industrial parks --------
site("Tanah Kuning Industrial Park", TF2, 2.8700, 117.7200, "china",
     [("Tanah Kuning Industrial Park", ["Coal_PowerPlant", "tgt_industry_buildings_2", "warehouses_2",
                                        "tgt_fueltanks_medium"]),
      ("Tanah Kuning Garrison", [("pla_apc_zbl-08", 2), "pla_ifv_zbd-04a", "pla_spaa_pgz-09", "pla_hq-17a",
                                 ("china_yj12_launcher", 2), "pla_ylc-18_radar", "Omega_trench", "Ammo_Bunker"])],
     posture="standard", spread=0.3, threat=90)
site("Kendawangan Alumina Refinery", TF2, -2.5300, 110.1500, "china",
     [("Kendawangan Alumina Refinery", ["tgt_industry_buildings_3", "tgt_refinery_small_2", "warehouses_1",
                                        "tgt_fueltanks_medium_sandy"]),
      ("Kendawangan Marine Detachment", [("pla_apc_zbl-08", 2), ("pla_hq-17_tel", 2), ("pla_yj-62_tel", 2),
                                         "pla_ylc-18_radar", "TBunkerTrench", "Bunker_2"])],
     posture="light", spread=0.3, threat=200)
site("Batang Industrial Park", TF2, -6.9200, 109.8500, "china",
     [("Batang Industrial Park", ["Coal_PowerPlant", "tgt_industry_buildings_3", "warehouses_3",
                                  "tgt_fueltanks_large"]),
      ("PLA Amphibious Combined Arms Battalion", [("pla_mbt_ztz-96", 2), ("pla_ifv_zbd-04a", 3),
                                                  ("pla_apc_zbl-08", 2), "pla_spa_plz-83", "pla_phl-03",
                                                  ("pla_spaa_pgz-09", 2), "pla_hq-17a", "pla_td_ztl-11",
                                                  "4tentgroup", "Ammo_Bunker"]),
      ("Batang Coastal Battery", ["pla_sam_site_hq-16b", ("china_yj83_launcher", 2), "pla_ylc-18_radar",
                                  "Omega_trench"])],
     posture="standard", spread=0.35, threat=10)
site("Tanjung Jati Power Station", TF2, -6.4500, 110.7500, "china",
     [("Tanjung Jati Power Station", ["Coal_PowerPlant", "tgt_industry_buildings_2", "warehouses_1"]),
      ("Tanjung Jati Guard Detachment", ["pla_hq-7b_radar", ("pla_hq-7b_tel", 2), "pla_apc_zbl-08", "Bunker_2"])],
     posture="light", spread=0.25, threat=20)

# ---------------- RED: militant camps -----------------------------------
site("Lahad Datu Militant Landing", TF2, 5.0300, 118.3300, "terrorists",
     [("Lahad Datu Militant Landing", ["4tentgroup", "civ_car_pickup_1983_m2", "civ_car_pickup_1983_type63",
                                       "civ_car_pickup_1983_sa-7", "nv_watchtower"])],
     nation_key="terrorists", spread=0.15)
site("Poso Militant Camp", TF2, -1.3950, 120.7500, "terrorists",
     [("Poso Militant Camp", ["4tentgroup", "civ_car_pickup_1983_assault_civ", "civ_car_pickup_1983_ub-16",
                              "civ_car_pickup_1983_sa-7", "nv_watchtower"])],
     nation_key="terrorists", spread=0.15)

# ---------------------------------------------------------------------------
# Air wings: site label -> [(aircraft id, "SquadronN,count|...")]
# ---------------------------------------------------------------------------
AIRGROUPS = {
    "Western Mindanao Command": [
        ("usa_a-10c", "Squadron1,6"),
        ("usaf_f-16cm-bl52d", "Squadron1,6"),
        ("usaf_mq-9a", "Squadron1,2"),
        ("usaf_mq-9_er", "Squadron1,2"),
        ("usmc_uh-1y", "Squadron1,4"),
        ("usn_hh-60", "Squadron1,2"),
    ],
}

# ---------------------------------------------------------------------------
# Naval context: (side, type, variant, role, lat, lon, heading, group label)
# ---------------------------------------------------------------------------
SHIPS = [
    (TF1, "ran_ddg_hobart", "Variant1", "AAW", -11.30, 129.80, 300, "Darwin Surface Group"),
    (TF1, "ran_ffh_anzac", "Variant2", "ASW", -11.22, 129.90, 300, "Darwin Surface Group"),
    (TF1, "ran_ffh_anzac", "Variant3", "ASW", -11.38, 129.72, 300, "Darwin Surface Group"),
    (TF1, "usn_takr_algol", "Variant1", "Transport", -11.15, 130.00, 120, "Darwin Surface Group"),
    (TF1, "usn_ddg_burke_f2a_113", "Variant1", "AAW", 5.60, 122.30, 250, "Celebes Sea SAG"),
    (TF1, "usn_ddg_burke_f3_125", "Variant1", "AAW", 5.50, 122.45, 250, "Celebes Sea SAG"),
    (TF2, "rfn_ffg_22350_1-4", "Variant1", "AAW", -0.60, 135.90, 250, "Biak Frigate Group"),
    (TF2, "rfn_ffg_22350_5-8", "Variant1", "AAW", -0.52, 136.02, 250, "Biak Frigate Group"),
    (TF2, "plan_lpd_type_071", "Variant1", "Transport", -6.55, 109.75, 90, "Java Sea Amphibious Group"),
    (TF2, "plan_type_054a_p5", "Variant1", "ASW", -6.50, 109.60, 90, "Java Sea Amphibious Group"),
    (TF2, "plan_type_056a", "Variant1", "ASW", -6.60, 109.95, 90, "Java Sea Amphibious Group"),
]

# ---------------------------------------------------------------------------
# Civil shipping: (type, [lat/lon via points], heading or None = along the lane,
# telegraph[, variant]). The via points name the corridor; sea_routes threads
# the lane through water between them. Spawns at the first point.
# ---------------------------------------------------------------------------
MERCHANTS = [
    # Lombok - Makassar Strait: the deep-draft route from the Indian Ocean to north-east Asia,
    # on to the Pacific between Mindanao and Sangihe
    ("civ_ms_super_p", [(-7.60, 116.60), (-5.60, 117.50), (-2.00, 118.30), (0.50, 119.00), (2.40, 120.00),
                        (3.60, 122.60), (4.60, 125.20), (5.00, 126.40)], None, 3, "Variant1"),
    ("civ_ms_bulk", [(-12.60, 116.90), (-9.40, 115.75), (-8.35, 115.85), (-6.80, 116.60), (-5.60, 117.60),
                     (-2.50, 118.40)], None, 3, "Variant2"),          # Port Hedland iron ore, northbound
    ("civ_ms_car_carrier_a", [(1.50, 119.40), (-1.00, 118.40), (-4.20, 118.30), (-6.30, 116.00),
                              (-6.50, 114.00), (-6.90, 112.70)], None, 3),   # Japan - Surabaya, southbound
    ("civ_ms_amra", [(-1.35, 117.00), (-2.50, 117.30), (-5.00, 116.50), (-6.50, 113.60), (-6.90, 112.70)],
     None, 3),                                                       # Balikpapan products to Surabaya
    # Java Sea: Singapore - Surabaya - Makassar
    ("civ_ms_encounter", [(-5.90, 109.00), (-6.20, 112.00), (-6.50, 113.40), (-5.60, 116.00), (-5.20, 118.60),
                          (-5.15, 119.32)], None, 3, "Variant3"),
    ("civ_ms_c8", [(-4.80, 118.60), (-5.60, 116.50), (-6.00, 112.60), (-6.00, 110.00), (-5.80, 107.60),
                   (-5.75, 107.00), (-6.00, 106.85)], None, 3),
    ("civ_ms_roro_b", [(-6.85, 112.65), (-5.00, 113.90), (-3.60, 114.45)], None, 2),   # Surabaya - Banjarmasin
    ("civ_ms_roro_c", [(-8.56, 115.60), (-8.68, 115.95)], None, 2),                    # Padang Bai - Lembar
    # Pelni liners and a cruise ship
    ("civ_ms_ivan_franko", [(-5.15, 119.32), (-6.00, 119.90), (-6.00, 121.50), (-5.85, 123.00), (-4.80, 126.50),
                            (-3.76, 128.08)], None, 3),              # Makassar - Ambon, south of Buton
    ("civ_ms_ivan_franko", [(-12.10, 130.40), (-8.60, 127.60), (-8.40, 125.50), (-8.00, 122.50), (-8.10, 120.50),
                            (-8.45, 119.75)], None, 3, "Variant2"),  # Darwin - Komodo via Wetar and Ombai
    # Darwin LNG north through the Banda and Molucca Seas to Japan
    ("civ_ms_sealift_pacific", [(-12.20, 130.50), (-9.00, 128.20), (-5.00, 127.90), (-2.00, 126.50),
                                (0.50, 126.30), (2.50, 126.90)], None, 3),
    # Tangguh LNG out of Bintuni Bay, north past Halmahera
    ("civ_ms_sealift_pacific", [(-2.50, 132.70), (-1.90, 131.20), (0.20, 128.90), (2.40, 129.00)],
     None, 3, "Variant1"),
    # Torres Strait: Weipa bauxite north-east into the Coral Sea
    ("civ_ms_bulk", [(-12.40, 141.55), (-10.85, 141.75), (-10.30, 142.55), (-9.20, 144.50)], None, 3, "Variant1"),
    # Vitiaz Strait: Lae north into the Bismarck Sea
    ("civ_ms_act_1", [(-6.75, 147.05), (-5.80, 147.60), (-4.80, 147.00), (-3.00, 146.00)], None, 3),
    ("civ_ms_freighter_a", [(-9.60, 147.10), (-10.10, 146.40), (-10.40, 145.60), (-11.50, 144.30)], None, 2),
    ("civ_ms_freighter_b", [(-8.70, 140.20), (-8.80, 139.00), (-8.20, 138.20)], None, 2),   # Merauke coastal
    # Sulu corner: Zamboanga - Sandakan
    ("civ_ms_roro_a", [(6.83, 121.90), (6.55, 121.30), (6.35, 120.40), (6.05, 119.00), (5.90, 118.30)], None, 2),
    # Fishing fleets
    ("civ_fv_sterntrawler_a", [(-8.90, 136.60), (-9.10, 137.40), (-8.80, 138.00)], None, 1),   # Arafura
    ("civ_fv_sterntrawler_b", [(-9.20, 135.50), (-9.60, 136.30)], None, 1),
    ("civ_fv_fishingboat_a", [(-12.00, 122.60), (-12.30, 123.30)], None, 1),                 # Timor Sea
    ("civ_fv_fishingboat_b", [(-11.60, 124.40), (-11.90, 125.20)], None, 1),
    ("civ_fv_sampan", [(6.60, 121.50), (6.50, 121.20)], None, 1),                            # Sulu Sea
    ("civ_fv_fishingboat_c", [(-5.60, 119.10), (-5.90, 118.70)], None, 1),                   # South Sulawesi
    ("civ_fv_sidetrawler", [(-2.50, 118.00), (-3.00, 118.20)], None, 1),                     # Makassar Strait
    ("civ_fv_fishingboat_d", [(-4.60, 129.80), (-4.90, 130.30)], None, 1),                   # Banda Sea
    ("civ_fv_sterntrawler_c", [(-8.30, 144.60), (-8.60, 145.20)], None, 1),                  # Gulf of Papua
    ("civ_fv_sterntrawler_d", [(3.00, 120.50), (3.40, 121.50)], None, 1),                    # Celebes Sea
]

# ---------------------------------------------------------------------------
# Civil aircraft airborne at start: (type, squadron = livery, [lat/lon chain], altitude ft)
# a330: 1 Air China, 10 AirAsia, 17 Cathay, 38 Garuda, 44 JAL, 48 Korean, 50 Lion, 60 PAL, 61 Qantas, 64 SIA
# a320: 6 Asiana, 58 Cebu Pacific     a380: 7 Qantas, 9 SIA
# ---------------------------------------------------------------------------
AIRCRAFT = [
    ("civ_a330", "Squadron38", [(-6.40, 108.00), (-5.90, 113.00), (-5.30, 118.90)], 37000),   # Garuda JKT-Makassar
    ("civ_a330", "Squadron50", [(-6.60, 113.20), (-3.50, 115.80), (-1.50, 116.70)], 35000),   # Lion SUB-Balikpapan
    ("civ_a330", "Squadron61", [(-12.00, 130.00), (-9.00, 124.00), (-5.50, 116.00)], 39000),  # Qantas DRW-SIN
    ("civ_a380", "Squadron7", [(-11.50, 118.00), (-8.00, 113.00), (-5.00, 109.00)], 41000),   # Qantas SYD-SIN
    ("civ_a380", "Squadron9", [(-5.50, 110.00), (-9.00, 116.50), (-12.50, 121.00)], 40000),   # SIA SIN-SYD
    ("civ_a330", "Squadron17", [(2.00, 118.50), (-3.00, 117.00), (-8.50, 115.50)], 39000),    # Cathay HKG-PER
    ("civ_a330", "Squadron1", [(3.00, 114.00), (-1.50, 111.50), (-5.50, 108.00)], 37000),     # Air China PEK-JKT
    ("civ_a330", "Squadron44", [(4.50, 118.50), (-1.00, 113.50), (-5.50, 108.50)], 39000),    # JAL NRT-JKT
    ("civ_a330", "Squadron10", [(5.90, 115.80), (4.00, 113.00), (2.50, 110.50)], 36000),      # AirAsia BKI-KUL
    ("civ_a330", "Squadron64", [(-4.00, 120.00), (-8.00, 127.00), (-11.00, 134.00)], 38000),  # SIA SIN-CNS
    ("civ_a330", "Squadron48", [(2.00, 127.00), (-4.00, 129.00), (-9.50, 131.00)], 39000),    # Korean ICN-SYD
    ("civ_a320", "Squadron6", [(2.50, 122.00), (-3.00, 119.50), (-8.50, 115.30)], 39000),     # Asiana ICN-DPS
    ("civ_a330", "Squadron60", [(8.50, 122.00), (7.30, 122.10), (6.95, 122.06)], 14000),      # PAL MNL-ZAM arriving
    ("civ_a320", "Squadron58", [(7.00, 122.20), (8.50, 122.50), (10.00, 122.50)], 31000),     # Cebu Pacific ZAM-MNL
    # light aircraft and helicopters on the short hops (vanilla types carry one Default livery)
    ("civ_c340", "Default", [(-12.35, 130.70), (-11.77, 130.62)], 6000),     # Darwin - Tiwi Islands
    ("civ_c340", "Default", [(-4.50, 136.85), (-5.50, 138.10)], 6000),       # Timika - Agats
    ("civ_c340", "Default", [(-6.55, 146.70), (-6.10, 145.40)], 11000),      # Nadzab - Goroka
    ("civ_c340", "Default", [(-3.70, 128.10), (-4.50, 129.90)], 8000),       # Ambon - Banda Neira
    ("civ_c340", "Default", [(-10.20, 123.70), (-9.10, 124.90)], 7000),      # Kupang - Atambua
    ("civ_v35", "Default", [(-12.50, 131.20), (-12.90, 131.50)], 4500),      # Darwin private
    ("civ_v35", "Default", [(-8.70, 115.30), (-8.75, 116.20)], 5500),        # Bali - Lombok private
    ("civ_h700", "Default", [(-12.30, 130.75), (-11.10, 126.60)], 1500),     # Darwin - Bayu-Undan
    ("civ_h700", "Default", [(-1.25, 116.90), (-0.70, 117.60)], 1000),       # Balikpapan - Mahakam delta
    ("civ_h700", "Default", [(4.40, 114.00), (4.90, 113.60)], 1200),         # Miri - offshore platforms
    ("civ_h700", "Default", [(-0.90, 131.30), (-2.40, 133.10)], 2000),       # Sorong - Tangguh
]


def routed(merchants):
    """The lanes with their via chains threaded through water."""
    router = Router(LANES)
    out = [(uid, router.route(pts), *rest) for uid, pts, *rest in merchants]
    router.save()
    return out


def check_lanes(merchants, geo):
    """Every leg of every civil lane must stay in water on the 1 km mask,
    sampled every half mile; the first land hit is reported as lat/lon."""
    if LAND is None:
        print("  (no land mask installed: lanes unchecked)")
        return
    bad = []
    for uid, pts, *_ in merchants:
        xz = [to_xz(la, lo) for la, lo in pts]
        for (x0, z0), (x1, z1) in zip(xz, xz[1:]):
            n = max(1, int(geo.dist(x0, z0, x1, z1) / 0.5))
            for k in range(n + 1):
                x, z = x0 + (x1 - x0) * k / n, z0 + (z1 - z0) * k / n
                if geo.on_land(x, z):
                    bad.append(f"{uid}: leg ({x0:.0f},{z0:.0f})->({x1:.0f},{z1:.0f}) crosses land at "
                               f"lat {base.CLAT + z / 60:.2f} lon {base.CLON + x / 60:.2f}")
                    break
    if bad:
        sys.exit("civil lanes cross land:\n  " + "\n  ".join(bad))


def main():
    args = base.cli()
    merchants = routed(MERCHANTS)
    check_lanes(merchants, Geo(base.CLAT, base.CLON))
    base.generate(NAME, OUT, DESCRIPTION, SITES, SHIPS, merchants, aircraft=AIRCRAFT, airgroups=AIRGROUPS,
                  density=args.density, report_unused=False)


if __name__ == "__main__":
    main()
