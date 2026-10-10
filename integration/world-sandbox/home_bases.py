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
on blue; Iran and North Korea with China and Russia on red. Brazil is blue
and Vietnam red at the author's direction (10 Oct 2026). Nations unlikely to
fight for either (India, Indonesia, Pakistan, Egypt and others) are left
out, because the engine has no neutral side.
"""

BLUE_ADDED = ["Spain", "Germany", "Netherlands", "Greece", "Poland", "Turkey", "Sweden",
              "Belgium", "Denmark", "Canada", "South_Korea", "Philippines", "Thailand",
              "NewZealand", "RoC", "Israel", "UAE", "Qatar", "Kuwait", "Saudi", "Brazil"]
RED_ADDED = ["Iran", "North_Korea", "Vietnam"]


def naval(nation, bid, name, lat, lon, units, yard=True, depot=True):
    return {"nation": nation, "id": bid, "name": name, "kind": "NavalBase", "lat": lat,
            "lon": lon, "yard": yard, "depot": depot, "units": units}


def air(nation, bid, name, lat, lon, heading, units):
    return {"nation": nation, "id": bid, "name": name, "kind": "AirBase", "lat": lat,
            "lon": lon, "heading": heading, "units": units}


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

    # --- red nations added ---------------------------------------------------------
    naval("Iran", "home_irn_bandar_abbas", "Bandar Abbas Naval Base", 27.14, 56.21, [
        ("ir_ffg_alvand_95", 2), ("ir_ptg_combattante_II", 2), ("ir_ptg_peykaap_3", 4)]),
    air("Iran", "home_irn_isfahan", "Isfahan (8th Tactical Air Base)", 32.751, 51.861, 260, [
        ("iriaf_f-14a", 8)]),
    air("Iran", "home_irn_bushehr", "Bushehr (6th Tactical Air Base)", 28.945, 50.835, 310, [
        ("iriaf_f-4e", 12)]),
    air("North_Korea", "home_prk_sunchon", "Sunchon Air Base", 39.413, 125.89, 360, [
        ("wp_mig-29a", 12, "MiG-29")]),
    # Vietnam: the collection carries its Tarantul (Molniya) and Petya hulls,
    # not its Su-30MK2s, Kilos or Gepards, so a naval base only.
    naval("Vietnam", "home_vnm_cam_ranh", "Cam Ranh Naval Base", 11.92, 109.17, [
        ("wp_ptg_tarantul_re", 4), ("wp_skr_petya3", 2)]),
]
