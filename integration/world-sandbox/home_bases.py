"""Home bases: the nations the world register leaves without a home port or
an air base of their own, built out (asked for by the author, 10 Oct 2026).

The register is research-led and places forces where the SEST research
reports them: the US worldwide, China, Australia, and other nations mostly at
overseas outposts (Djibouti, Mare Harbour). That left Russia, Japan and Norway
with no naval base at all, the UK, France and Italy with outposts only, and no
place for the many other navies and air forces the collection carries.

Every entry here is a SCENARIO ADDITION, not a register row: a nation's main
home naval base (with a shipyard and a supply depot, so the buy list can build
and supply its ships) and its main air base, each with a home force drawn
from what the collection gives that nation. Positions are the bases' public
locations, rounded; runway headings are the main runway's, rounded to 10
degrees; quantities are illustrative peacetime presence, not orders of
battle. A unit may carry a third field, the force's label, where the unit's
own display name is an id or a date range. A nation the collection gives no plausible ships gets an air base
only. build_dynamic_campaign.py turns each entry into a base and a harbour or
air force exactly as it does a register node.

Sides for the added nations follow 2028 alignments a two-sided engine can
hold: NATO members and the United States' treaty allies and close partners
on blue; Iran and North Korea with China and Russia on red. At the author's
direction (10 Oct 2026) Brazil, India and Egypt are blue and Vietnam,
Indonesia and Pakistan red; Chile is blue to fit the SEST story - in
Southern Reach the coercion network moves into the Southern Ocean in the
Antarctic season, and Chile holds an Antarctic claim and the gateway port,
so its frigate on the Antarctic station sails from Punta Arenas. Nations
with nothing current in the collection, or no part in the story, are left
out, because the engine has no neutral side.
"""

BLUE_ADDED = ["Spain", "Germany", "Netherlands", "Greece", "Poland", "Turkey", "Sweden",
              "Belgium", "Denmark", "Canada", "South_Korea", "Philippines", "Thailand",
              "NewZealand", "RoC", "Israel", "UAE", "Qatar", "Kuwait", "Saudi", "Brazil", "India", "Egypt", "Chile"]
RED_ADDED = ["Iran", "North_Korea", "Vietnam", "Indonesia", "Pakistan"]


def naval(nation, bid, name, lat, lon, units, yard=True, depot=True):
    return {"nation": nation, "id": bid, "name": name, "kind": "NavalBase", "lat": lat,
            "lon": lon, "yard": yard, "depot": depot, "units": units}


def air(nation, bid, name, lat, lon, heading, units, port=None, field=None):
    """port: the naval base this airfield belongs to (an island base with a
    harbour and a runway), so the two are one installation to the engine.
    field: the airfield unit, where the generic airfield_small_1 is wrong - the
    reef bases use the PLA airbases SEST Indo-Pacific Land Assets places there
    (integration/missions/build_indo_pacific_showcase.py). A reef is too small
    for the land mask and may be missing from the game's terrain; a land unit
    there floats at one metre (docs/design-notes.md), as in that mission."""
    return {"nation": nation, "id": bid, "name": name, "kind": "AirBase", "lat": lat,
            "lon": lon, "heading": heading, "units": units, "port": port, "field": field}


HOME_BASES = [
    # --- nations already in the register, given a home port or air base -------
    naval("Russia", "home_rus_severomorsk", "Severomorsk (Northern Fleet)", 69.075, 33.39, [
        ("ru_cv_kuznetsov", 1), ("wp_rkr_admiral_nakhimov_refit", 1), ("rfn_ffg_22350_1-4", 2),
        ("wp_bpk_udaloy_98", 2), ("wp_ssgn_yasen", 2), ("wp_ssn_akula", 2), ("rfn_aor_pashin", 1)]),
    naval("Russia", "home_rus_vladivostok", "Vladivostok (Pacific Fleet)", 43.105, 131.9, [
        ("wp_rkr_slava_16", 1), ("wp_bpk_udaloy_98", 3), ("rfn_cvt_20380_7-12", 3),
        ("rfn_cvt_20385", 1), ("wp_ss_improved_kilo", 3), ("wp_bdk_ropucha", 2)]),
    naval("Japan", "home_jpn_kure", "JMSDF Kure District", 34.235, 132.55, [
        ("jmsdf_ddh_ise", 1), ("jmsdf_ddh_hyuga", 1), ("jmsdf_ddg_maya", 2), ("jmsdf_ddg_atago", 2),
        ("jmsdf_dd_asahi", 2), ("js_ffg_mogami", 3), ("jmsdf_aoe_mashuu", 1)]),
    naval("Norway", "home_nor_haakonsvern", "Haakonsvern Naval Base (Bergen)", 60.334, 5.236, [
        ("knm_cor_skjold", 3), ("knm_cb90", 2)]),
    naval("UK", "home_uk_portsmouth", "HMNB Portsmouth", 50.8, -1.11, [
        ("rn_ddg_type45_26", 3), ("rn_ff_type23", 2), ("rn_aor_tide", 1), ("rn_opv_river_batch2", 2)]),
    air("UK", "home_uk_lossiemouth", "RAF Lossiemouth", 57.705, -3.339, 230, [
        ("raf_ef2000_fgr4_late", 12, "Typhoon FGR.4"), ("usn_p8", 4, "Poseidon MRA1")]),
    naval("France", "home_fra_toulon", "Toulon Naval Base", 43.105, 5.925, [
        ("fr_cvn_charles-de-gaulle_late", 1), ("fr_ddg_horizon", 2),
        ("fr_ffg_aquitaine_modernized_aaw", 2), ("fr_ffg_aquitaine_asw", 2), ("fr_lhd_mistral", 1),
        ("fr_ssn_suffren", 2)]),
    naval("France", "home_fra_brest", "Brest Naval Base", 48.38, -4.495, [
        ("fr_ffg_aquitaine_asw", 2), ("fr_ffg_lafayette_modernized", 2), ("fr_ssbn_triomphant", 1)],
        yard=False, depot=False),
    air("France", "home_fra_saint_dizier", "BA 113 Saint-Dizier", 48.636, 4.899, 290, [
        ("fr_rafale_b_l", 12)]),
    air("France", "home_fra_lann_bihoue", "BAN Lann-Bihoue", 47.76, -3.44, 250, [("fr_atl2", 4)]),
    naval("Italy", "home_ita_taranto", "Taranto Naval Base", 40.47, 17.215, [
        ("ita_ddg_orizzonte_18", 1), ("ita_ffg_fremm", 2), ("ita_ffg_fremm_asw", 2),
        ("ita_ffg_ppa", 2), ("ita_ssk_todaro_batch1", 2)]),
    air("Italy", "home_ita_gioia_del_colle", "Gioia del Colle Air Base", 40.767, 16.933, 320, [
        ("eu_ef2000_fgr4_late", 12)]),

    # --- blue nations added ------------------------------------------------------
    naval("Spain", "home_esp_ferrol", "Ferrol Naval Base", 43.48, -8.24, [
        ("ae_lhd_juan_carlos", 1), ("ae_lpd_galicia", 1), ("ae_ffg_alvaro_bazan", 3),
        ("ae_ffg_cristobal_colon", 1), ("ae_ssk_s80", 1), ("ae_opv_meteoro", 2)]),
    air("Spain", "home_esp_torrejon", "Torrejon Air Base", 40.497, -3.446, 230, [
        ("spa_ef2000", 12), ("sp_a330_mrtt", 1)]),
    naval("Germany", "home_deu_wilhelmshaven", "Wilhelmshaven Naval Base", 53.515, 8.135, [
        ("ger_ffg_f124_MLU", 2), ("ger_ffg_f125_MLU", 2), ("ger_ffg_f123_2025_mlu", 2),
        ("ger_fsg_k130_batch2", 2), ("ger_ssk_type_212a_batch1", 2)]),
    air("Germany", "home_deu_wittmund", "Wittmund Air Base", 53.548, 7.667, 260, [
        ("eu_ef2000_fgr4_late", 12)]),
    naval("Netherlands", "home_nld_den_helder", "Den Helder Naval Base", 52.958, 4.783, [
        ("rnn_ddg_zeven_mlu", 2), ("rnn_ddg_zeven", 2), ("rnn_ffg_karel_eol", 2), ("rnn_ffg_hol", 2),
        ("rnn_mcm_city", 1)]),
    air("Netherlands", "home_nld_eindhoven", "Eindhoven Air Base", 51.45, 5.375, 220, [
        ("otan_a330_mrtt", 2, "A330 MRTT (NATO fleet)")]),
    air("Greece", "home_grc_tanagra", "Tanagra Air Base", 38.34, 23.565, 270, [
        ("gre_m2k-5_mk2_late", 12), ("haf_f-16c-bl52plus", 12)]),
    air("Poland", "home_pol_lask", "Lask Air Base", 51.552, 19.179, 240, [
        ("pol_f-16c-bl52plus", 12)]),
    air("Turkey", "home_tur_konya", "Konya Air Base", 37.979, 32.562, 190, [
        ("tuaf_f-16c", 12), ("E7A_Wedgetail", 2, "E-7T Peace Eagle")]),
    naval("Sweden", "home_swe_karlskrona", "Karlskrona Naval Base", 56.16, 15.595, [
        ("swe_fsg_visby_v6", 3)]),
    air("Sweden", "home_swe_ronneby", "F 17 Ronneby", 56.267, 15.265, 190, [
        ("se_jas-39", 12), ("dts_saab_ge", 1)]),
    air("Belgium", "home_bel_melsbroek", "Melsbroek Air Base", 50.9, 4.484, 250, [
        ("bel_a400m_tankers", 2)]),
    naval("Denmark", "home_dnk_frederikshavn", "Frederikshavn Naval Base", 57.44, 10.548, [
        ("hdms_iver_huitfeldt", 3)]),
    air("Denmark", "home_dnk_karup", "Karup Air Base", 56.297, 9.124, 270, [("dk_mh-60r", 4)]),
    air("Canada", "home_can_bagotville", "CFB Bagotville", 48.331, -70.996, 290, [
        ("usn_fa-18a", 12, "CF-188 Hornet")]),
    naval("South_Korea", "home_kor_jinhae", "Jinhae Naval Base", 35.135, 128.66, [
        ("ko_lph-6111", 1), ("ko_ddg-995", 1), ("ko_ddg-991", 3), ("ko_ddh-975_kvls", 2),
        ("ko_ffg-818", 3), ("ko_ffg-828", 2)]),
    air("South_Korea", "home_kor_gimhae", "Gimhae Air Base", 35.18, 128.938, 360, [
        ("E7A_Wedgetail", 2, "E-737 Peace Eye")]),
    air("South_Korea", "home_kor_pohang", "Pohang Naval Air Base", 35.988, 129.42, 360, [
        ("usn_p8", 3)]),
    naval("Philippines", "home_phl_subic", "Subic Bay Naval Base", 14.805, 120.27, [
        ("pn_ffg-150_2", 2), ("pn_ffg-06", 2), ("phl_ff_hamilton", 2), ("phl_lpd_tarlac", 1),
        ("phl_fs_pohang", 1)]),
    air("Philippines", "home_phl_basa", "Basa Air Base", 14.987, 120.493, 220, [
        ("rok_f-50_ph", 12)]),
    naval("Thailand", "home_tha_sattahip", "Sattahip Naval Base", 12.66, 100.9, [
        ("tha_cvl_chakri_naruebet", 1), ("tha_ffg_naresuan", 2), ("tha_ff_053HT", 2),
        ("tha_pt_hua_hin", 2)]),
    air("Thailand", "home_tha_korat", "Wing 1 Korat", 14.934, 102.079, 240, [("tha_f-16c", 12)]),
    air("NewZealand", "home_nzl_ohakea", "RNZAF Base Ohakea", -40.206, 175.388, 270, [
        ("usn_p8", 4)]),
    air("RoC", "home_twn_hsinchu", "Hsinchu Air Base", 24.818, 120.939, 230, [
        ("tw_m2k-5ei", 12, "Mirage 2000-5EI")]),
    naval("Israel", "home_isr_haifa", "Haifa Naval Base", 32.82, 35.01, [("ins_ptg_hetz", 3)]),
    air("Israel", "home_isr_ramat_david", "Ramat David Air Base", 32.665, 35.18, 270, [
        ("iaf_f-16c-barakII", 12)]),
    air("UAE", "home_are_al_dhafra", "Al Dhafra Air Base", 24.248, 54.547, 310, [
        ("uae_m2k-9", 12, "Mirage 2000-9")]),
    air("Qatar", "home_qat_al_udeid", "Al Udeid Air Base", 25.117, 51.315, 340, [
        ("exp_rafale_c_l", 12)]),
    air("Kuwait", "home_kwt_ali_al_salem", "Ali Al Salem Air Base", 29.347, 47.521, 330, [
        ("eu_ef2000_fgr4_late", 12)]),
    air("Saudi", "home_sau_dhahran", "King Abdulaziz Air Base (Dhahran)", 26.265, 50.152, 340, [
        ("eu_ef2000_fgr4_late", 12)]),
    naval("Brazil", "home_bra_rio", "Rio de Janeiro Naval Base", -22.877, -43.133, [
        ("bra_lph_Atlantico", 1), ("bra_ffg_tamandare", 1), ("bra_ffg_niteroi_2005", 2),
        ("bra_type22b12", 1), ("bra_ss_riachuelo", 3), ("bra_ss_tikuna", 1)]),
    air("Brazil", "home_bra_santa_cruz", "Santa Cruz Air Base", -22.932, -43.719, 230, [
        ("bra_f-5em", 12)]),
    air("Brazil", "home_bra_salvador", "Salvador Air Base", -12.911, -38.331, 280, [
        ("bra_p-3am", 3)]),
    naval("India", "home_ind_mumbai", "Mumbai (Western Naval Command)", 18.92, 72.835, [
        ("ins_d-66", 2), ("ins_d-63", 2), ("wp_ss_kilo", 2, "Sindhughosh-class")]),
    air("India", "home_ind_ambala", "Ambala Air Force Station", 30.368, 76.817, 300, [
        ("exp_rafale_c_l", 12, "Rafale EH")]),
    air("India", "home_ind_rajali", "INS Rajali (Arakkonam)", 13.071, 79.691, 240, [
        ("usn_p8", 4, "P-8I Neptune")]),
    naval("Egypt", "home_egy_alexandria", "Alexandria Naval Base", 31.18, 29.875, [
        ("ae_ffg_descubierta", 2, "El Suez-class")]),
    air("Egypt", "home_egy_cairo_west", "Cairo West Air Base", 30.116, 30.915, 340, [
        ("exp_rafale_c_l", 12, "Rafale EM")]),
    # Chile, fitted to the SEST story: the main fleet and yard at Talcahuano,
    # a frigate on the Antarctic station at Punta Arenas, the F-5 group at
    # Chabunco beside it, the E-3D at Santiago.
    naval("Chile", "home_chl_talcahuano", "Talcahuano Naval Base", -36.7, -73.1, [
        ("ch_ff_type23_pida", 2), ("ch_ffg_adelaide_longhull", 2), ("ch_ss_scorpene", 2),
        ("type_209", 2)]),
    naval("Chile", "home_chl_punta_arenas", "Punta Arenas (Third Naval Zone)", -53.16, -70.905, [
        ("ch_ffg_karel", 1, "Antarctic station frigate")], yard=False),
    air("Chile", "home_chl_chabunco", "Chabunco Air Base (Punta Arenas)", -53.003, -70.855, 70, [
        ("ch_f-5e", 8, "F-5E Tigre III")]),
    air("Chile", "home_chl_santiago", "Santiago Air Brigade (Pudahuel)", -33.393, -70.786, 170, [
        ("ch_e3d", 1, "E-3D Sentry")]),

    # --- red nations added ---------------------------------------------------------
    naval("Iran", "home_irn_bandar_abbas", "Bandar Abbas Naval Base", 27.14, 56.21, [
        ("ir_ffg_alvand_95", 2), ("ir_ptg_combattante_II", 2), ("ir_ptg_peykaap_3", 4),
        ("wp_ss_kilo", 3)]),   # Iran's three Tareq-class Kilos; Soviet-colour stand-ins
    air("Iran", "home_irn_isfahan", "Isfahan (8th Tactical Air Base)", 32.751, 51.861, 260, [
        ("iriaf_f-14a", 8)]),
    air("Iran", "home_irn_bushehr", "Bushehr (6th Tactical Air Base)", 28.945, 50.835, 310, [
        ("iriaf_f-4e", 12)]),
    air("North_Korea", "home_prk_sunchon", "Sunchon Air Base", 39.413, 125.89, 360, [
        ("wp_mig-29a", 12, "MiG-29")]),

    # --- red, to align with reality (asked for by the author, 10 Oct 2026) ------
    # The register places China at three home ports, Djibouti and one air base.
    # The real PLA Navy has three theatre fleets, the shipyards that build its
    # carriers, destroyers and nuclear boats, and garrisoned bases on the
    # Paracel and Spratly reefs; since 2025 its ships use Ream in Cambodia.
    naval("China", "home_chn_qingdao", "Qingdao (Northern Theater Navy)", 36.07, 120.35, [
        ("plan_type_001", 1), ("plan_type_055_2020", 2), ("plan_type_052d_p2_1", 2),
        ("plan_type_054a_p4", 2), ("plan_ssn_type_093a", 2), ("plan_aor_type901", 1)], yard=False),
    naval("China", "home_chn_zhanjiang", "Zhanjiang (Southern Theater Navy)", 21.2, 110.42, [
        ("plan_type_052d_p3", 2), ("plan_type_054a_p5", 2), ("plan_type_056a", 3),
        ("plan_lpd_type_071", 2), ("plan_ss_type_039c", 2)], yard=False),
    naval("China", "home_chn_dalian", "Dalian Shipyard", 38.93, 121.66, [
        ("plan_type_055_2026", 1), ("plan_type_052d_p4", 1)], depot=False),
    naval("China", "home_chn_jiangnan", "Jiangnan Shipyard (Changxing Island)", 31.36, 121.74, [
        ("plan_type_052d_p4", 1), ("plan_type_055_2026", 1)], depot=False),
    naval("China", "home_chn_huludao", "Bohai Shipyard (Huludao)", 40.71, 120.98, [
        ("plan_ssn_type_093b", 1)], depot=False),
    naval("China", "home_chn_fiery_cross", "Fiery Cross Reef", 9.549, 112.889, [
        ("plan_type_054a_p3", 1), ("plan_type_056a", 1)], yard=False, depot=False),
    air("China", "home_chn_fiery_cross_air", "Fiery Cross Reef airfield", 9.549, 112.889, 40, [
        ("plaaf_j-11b", 4), ("plan_y-9fq", 2)], port="home_chn_fiery_cross", field="pla_airbase_modern"),
    naval("China", "home_chn_subi", "Subi Reef", 10.923, 114.084, [
        ("plan_type_056a", 1), ("plan_ptg_type037IIE", 2)], yard=False, depot=False),
    naval("China", "home_chn_mischief", "Mischief Reef", 9.9, 115.535, [
        ("plan_type_056a", 1), ("plan_ptg_type037IIE", 2)], yard=False, depot=False),
    air("China", "home_chn_woody_island", "Woody Island (Paracels)", 16.835, 112.34, 100, [
        ("plaaf_j-11b", 6)], field="china_large_airbase"),
    naval("China", "home_chn_ream", "Ream Naval Base (Cambodia, PLA support)", 10.507, 103.613, [
        ("plan_type_056a", 2)], yard=False, depot=False),
    air("China", "home_chn_longtian", "Longtian Air Base (Fujian)", 25.7, 119.45, 30, [
        ("plaaf_j-16", 12), ("plaaf_j-10c", 12)]),
    air("China", "home_chn_wuhu", "Wuhu Air Base", 31.39, 118.408, 30, [("plaaf_j-20a", 12)]),
    air("China", "home_chn_wugong", "Wugong Air Base", 34.27, 108.25, 80, [
        ("plaaf_h-6k_late", 8), ("plaaf_y-20a", 2)]),
    # Russia: the Baltic and Black Sea Fleets, the ballistic-missile boats'
    # own bases, and the fighter fields beside the fleets.
    naval("Russia", "home_rus_baltiysk", "Baltiysk (Baltic Fleet)", 54.645, 19.89, [
        ("wp_em_sovremenny_98", 1), ("rfn_cvt_20380_3-6", 4), ("rfn_cvt_21631", 2),
        ("wp_ss_improved_kilo", 1), ("wp_bdk_ropucha", 2)]),
    naval("Russia", "home_rus_novorossiysk", "Novorossiysk (Black Sea Fleet)", 44.715, 37.79, [
        ("rfn_ffg_11356", 2), ("wp_ss_improved_kilo", 4), ("rfn_cvt_21631", 3)], yard=False),
    naval("Russia", "home_rus_gadzhiyevo", "Gadzhiyevo (Northern Fleet submarines)", 69.25, 33.33, [
        ("wp_ssbn_borei", 2), ("wp_ssbn_delta4", 3)], yard=False, depot=False),
    naval("Russia", "home_rus_vilyuchinsk", "Vilyuchinsk (Pacific Fleet submarines)", 52.92, 158.42, [
        ("wp_ssbn_borei", 2), ("wp_ssgn_oscar2", 2), ("wp_ssgn_yasen", 1)], yard=False, depot=False),
    air("Russia", "home_rus_severomorsk3", "Severomorsk-3 (naval aviation)", 69.017, 33.42, 10, [
        ("wp_su-33", 8), ("wp_mig-29k_941", 6, "MiG-29K")]),
    air("Russia", "home_rus_chkalovsk", "Chkalovsk (Kaliningrad)", 54.766, 20.397, 70, [
        ("wp_su-30sm", 12)]),
    air("Russia", "home_rus_yelizovo", "Yelizovo (Kamchatka)", 53.168, 158.454, 160, [
        ("wp_mig-31bm", 8)]),
    # Iran: the navy's second district at Bushehr and the Gulf of Oman base at
    # Jask beside Bandar Abbas.
    naval("Iran", "home_irn_bushehr_naval", "Bushehr Naval Base", 28.98, 50.82, [
        ("ir_ptg_combattante_II", 2), ("ir_ptg_peykaap_2", 4)], yard=False, depot=False),
    naval("Iran", "home_irn_jask", "Jask Naval Base", 25.64, 57.77, [
        ("ir_ffg_alvand", 1), ("ir_ptg_peykaap_3", 4)], yard=False, depot=False),
    # North Korea's navy is Romeo submarines and Osa-type boats; the collection
    # has them only in Chinese colours, so these hulls are stand-ins.
    naval("North_Korea", "home_prk_nampo", "Nampo (West Sea Fleet)", 38.72, 125.38, [
        ("plan_ss_romeo", 4), ("plan_ptg_type_021", 4)]),
    naval("North_Korea", "home_prk_sinpo", "Sinpo (East Sea Fleet submarines)", 40.03, 128.19, [
        ("plan_ss_romeo", 4)], yard=False, depot=False),
    # Vietnam: the collection carries its Tarantul (Molniya) and Petya hulls,
    # not its Su-30MK2s, Kilos or Gepards, so a naval base only.
    naval("Vietnam", "home_vnm_cam_ranh", "Cam Ranh Naval Base", 11.92, 109.17, [
        ("wp_ptg_tarantul_re", 4), ("wp_skr_petya3", 2)]),
    # Indonesia: the collection's TNI-AL is the 1960s Soviet fleet; the Ahmad
    # Yani frigates and the Rafale are what is current.
    # Indonesia on red is armed by China (asked for by the author): Chinese-built
    # 054A frigates, 056A corvettes and 039B submarines beside the Ahmad Yani,
    # and J-10Cs - Indonesia studied the J-10 in 2025 - beside the Rafale. The
    # hulls fly their Chinese variants' flags: the collection has no
    # Indonesian livery for them.
    naval("Indonesia", "home_idn_surabaya", "Surabaya (Koarmada II)", -7.2, 112.73, [
        ("idn_ff_vanspeijk", 2), ("plan_type_054a_p5", 2), ("plan_type_056a", 2),
        ("plan_ss_type_039b", 2)]),
    air("Indonesia", "home_idn_pekanbaru", "Roesmin Nurjadin Air Base (Pekanbaru)", 0.461, 101.445, 360, [
        ("exp_rafale_c_l", 6, "Rafale"), ("plaaf_j-10c", 12, "J-10CE")]),
    air("Indonesia", "home_idn_natuna", "Raden Sadjad Air Base (Natuna)", 3.92, 108.37, 180, [
        ("plaaf_j-10c", 8, "J-10CE")]),
    naval("Pakistan", "home_pak_karachi", "Karachi Naval Dockyard", 24.84, 66.98, [
        ("pns_type_054a_p", 4), ("pns_ffg_oliver_hazard_perry_longhull", 1), ("pns_ss_s-26p", 2),
        ("pns_ss_hashmat", 2)]),
    air("Pakistan", "home_pak_minhas", "PAF Base Minhas (Kamra)", 33.869, 72.401, 300, [
        ("paf_j-10ce", 12)]),
    air("Pakistan", "home_pak_masroor", "PAF Base Masroor (Karachi)", 24.894, 66.939, 280, [
        ("paf_jf-17_blk_iii", 12), ("paf_zdk-03", 2)]),
]
