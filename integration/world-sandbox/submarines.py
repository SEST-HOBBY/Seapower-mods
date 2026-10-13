"""Submarines: every navy's boats as a submarine force of their own, at the
bases they really sail from, with a boat from each larger squadron at sea
(asked for by the author, 11 Oct 2026: "add submarine to world campaign").

Until now a submarine sat in its base's harbour force with the frigates and
tankers, so the map showed none, and the navies with the largest submarine
arms had no submarine base at all: no Pearl Harbor, Groton, Kings Bay or
Bangor, no Faslane, no JMSDF Yokosuka. Dynamic Campaign Mod's own Pacific
1985 campaign keeps submarines the same way this does - as Surface forces of
their own (SUBRON 7, SSN Patrol Kamchatka), since the engine has no other
force type.

Everything here is a SCENARIO ADDITION. Positions are the bases' public
locations, rounded; quantities are illustrative peacetime presence, not
orders of battle. Squadron names are given only where the real one is sure
(the US squadrons and groups, the JMSDF flotillas, the French strategic
force); every other force is "<base> submarines". A boat is named only where
its homeport is sure.

STAND-INS. The collection has no model of some navies' current boats, so the
nearest hull it has carries the real boats' names:
  UK Astute class       -> rn_swiftsure_class_ssn (no Astute in any mod; no
                           SSBN either, so the Vanguards are left out)
  India Kalvari class   -> ch_ss_scorpene (the same Scorpene design)
  Israel Dolphin class  -> ger_ssk_type_212a_batch1 (Dolphin II is a 212
                           derivative)
  Norway Ula class      -> ger_ssk_type_212a_batch1
  Greece Papanikolis    -> type_209 (Type 214, a 209 descendant)
The Type 209 is the real class for South Korea's Chang Bogo boats, Turkey's
Preveze and Gur classes, Egypt's 209/1400s and Indonesia's Nagapasa class.
Left out for want of any model: Canada's Victorias, Taiwan's Hai Lung and
Hai Kun, Sweden's Gotlands, the Netherlands' Walrus class and North Korea's
Sang-O (its Romeos stand for its whole force). South Korea's
KSS boats exist in Euromod - South Korea Navy but sit in a vessels/non/
folder the game does not load.
"""

from home_bases import naval

# New submarine bases, built like home_bases.py entries: no shipyard, no
# depot - their boats draw on their navy's main base for supply.
SUB_BASES = [
    naval("US", "home_usa_pearl", "Joint Base Pearl Harbor-Hickam", 21.355, -157.945, [
        ("usn_ssn_virginia_block3_2026", 3), ("usn_ssn_virginia_block4", 2),
        ("usn_ssn_los_angeles_flt3_2027", 3)], yard=False, depot=False),
    naval("US", "home_usa_groton", "Naval Submarine Base New London (Groton)", 41.39, -72.09, [
        ("usn_ssn_virginia_block4", 3), ("usn_ssn_virginia_block3_2026", 2),
        ("usn_ssn_los_angeles_flt3_2027", 1)], yard=False, depot=False),
    naval("US", "home_usa_kings_bay", "Naval Submarine Base Kings Bay", 30.8, -81.52, [
        ("usn_ssbn_ohio", 4)], yard=False, depot=False),
    naval("US", "home_usa_bangor", "Naval Base Kitsap-Bangor", 47.73, -122.72, [
        ("usn_ssbn_ohio", 6)], yard=False, depot=False),
    naval("UK", "home_uk_faslane", "HMNB Clyde (Faslane)", 56.07, -4.82, [],
          yard=False, depot=False),
    naval("Japan", "home_jpn_yokosuka", "JMSDF Yokosuka District", 35.3, 139.645, [
        ("jmsdf_ssn_unryu", 5)], yard=False, depot=False),
    naval("India", "home_ind_vizag", "Visakhapatnam (Eastern Naval Command)", 17.69, 83.28, [
        ("wp_ss_kilo", 2)], yard=False, depot=False),
    naval("Germany", "home_deu_eckernfoerde", "Eckernfoerde Naval Base", 54.47, 9.85, [
        ("ger_ssk_type_212a_batch1", 4)], yard=False, depot=False),
    naval("Spain", "home_esp_cartagena", "Cartagena Naval Base", 37.59, -0.98, [],
          yard=False, depot=False),
    naval("Greece", "home_grc_salamis", "Salamis Naval Base", 37.94, 23.5, [
        ("type_209", 4)], yard=False, depot=False),
    naval("Turkey", "home_tur_golcuk", "Golcuk Naval Base", 40.72, 29.81, [
        ("type_209", 4)], yard=False, depot=False),
]

# Boats added at bases that already exist: (unit, count, names or None).
SUB_ADD = {
    "wpac_guam_naval_base_apra_harbor": [("usn_ssn_los_angeles_flt3_2027", 2, None)],
    "usp_sandiego_naval_base_san_diego": [("usn_ssn_los_angeles_flt3_2027", 3, None)],
    "usa_norfolk_naval_station_norfolk": [("usn_ssn_virginia_block3_2026", 2, None),
                                          ("usn_ssn_los_angeles_flt3_2027", 2, None)],
    "home_usa_kings_bay": [("usn_ssgn_ohio_2027", 2, ["USS Florida", "USS Georgia"])],
    "home_usa_bangor": [("usn_ssgn_ohio_2027", 2, ["USS Ohio", "USS Michigan"]),
                        ("usn_ssn_seawolf_2027", 2, ["USS Seawolf", "USS Connecticut"]),
                        ("usn_ssn_seawolf_carter", 1, ["USS Jimmy Carter"])],
    "home_uk_faslane": [("rn_swiftsure_class_ssn", 5, ["HMS Astute", "HMS Ambush", "HMS Artful",
                                                      "HMS Audacious", "HMS Anson"])],
    "aus_stirling_hmas_stirling": [("ran_ssg_collins", 2, ["SSG 73 HMAS Collins",
                                                           "SSG 76 HMAS Dechaineux"])],
    "home_fra_brest": [("fr_ssbn_triomphant", 3, None)],
    "home_fra_toulon": [("fr_ssn_suffren", 2, None)],
    "home_jpn_kure": [("jmsdf_ssn_unryu", 4, None)],
    "home_kor_jinhae": [("type_209", 3, ["ROKS Chang Bogo", "ROKS Lee Chun", "ROKS Choi Museon"])],
    "home_ind_mumbai": [("ch_ss_scorpene", 4, ["INS Kalvari", "INS Khanderi", "INS Karanj",
                                               "INS Vela"])],
    "home_isr_haifa": [("ger_ssk_type_212a_batch1", 3, ["INS Dolphin", "INS Tanin", "INS Rahav"])],
    "home_nor_haakonsvern": [("ger_ssk_type_212a_batch1", 2, ["KNM Ula", "KNM Utstein"])],
    "home_esp_cartagena": [("ae_ssk_s80_plus", 2, ["S-81 Isaac Peral", "S-82 Narciso Monturiol"])],
    "home_egy_alexandria": [("type_209", 4, None)],
    # PLA Navy: about 60 boats in 2028 - six Jin-class SSBNs at Longpo, the
    # Shang SSNs at Qingdao (Jianggezhuang) and Yulin, Yuan, Song and Kilo
    # boats with the three theater fleets.
    "chn_hainan_longpo_naval_base": [("plan_ssbn_type_094a", 4, None), ("plan_ssbn_type_094", 2, None)],
    "chn_hainan_yulin_naval_base": [("plan_ssn_type_093b", 2, None), ("plan_ss_type_039a", 2, None)],
    "home_chn_qingdao": [("plan_ssn_type_093a", 2, None), ("plan_ssn_type_093b", 1, None),
                         ("plan_ssn_type_093", 2, None)],
    "chn_zhejiang_ningbo_naval_base": [("plan_ss_type_039a", 3, None), ("plan_ss_kilo", 4, None)],
    "home_chn_zhanjiang": [("plan_ss_type_039b", 3, None), ("plan_ss_kilo", 2, None)],
    # Russian Navy: the strategic boats at Gadzhiyevo and Vilyuchinsk, the
    # Northern Fleet's attack boats with Severomorsk's, the Pacific Fleet's
    # Kilos at Vladivostok.
    "home_rus_gadzhiyevo": [("wp_ssbn_borei", 1, None), ("wp_ssbn_delta4", 2, None)],
    "home_rus_severomorsk": [("wp_ssgn_oscar2", 2, None), ("wp_ssn_sierra2", 1, None),
                             ("wp_ssn_victor3", 1, None)],
    "home_rus_vilyuchinsk": [("wp_ssbn_borei", 2, None), ("wp_ssgn_oscar2", 2, None),
                             ("wp_ssn_akula", 1, None)],
    "home_rus_vladivostok": [("wp_ss_improved_kilo", 3, None)],
    # North Korea: Romeo boats - the collection has no Sang-O.
    "home_prk_sinpo": [("plan_ss_romeo", 4, None)],
    "home_prk_nampo": [("plan_ss_romeo", 4, None)],
    "home_vnm_cam_ranh": [("wp_ss_improved_kilo", 6, ["HQ-182 Ha Noi", "HQ-183 Ho Chi Minh City",
                                                      "HQ-184 Hai Phong", "HQ-185 Khanh Hoa",
                                                      "HQ-186 Da Nang", "HQ-187 Ba Ria-Vung Tau"])],
    "home_idn_surabaya": [("type_209", 3, ["KRI Nagapasa", "KRI Ardadedali", "KRI Alugoro"])],
}

SQUADRON_NAME = {
    "wpac_guam_naval_base_apra_harbor": "Submarine Squadron 15",
    "usp_sandiego_naval_base_san_diego": "Submarine Squadron 11",
    "usa_norfolk_naval_station_norfolk": "Submarine Squadron 6",
    "home_usa_pearl": "Submarine Squadrons 1 and 7",
    "home_usa_groton": "Submarine Squadrons 4 and 12",
    "home_usa_kings_bay": "Submarine Group 10",
    "home_usa_bangor": "Submarine Group 9",
    "home_jpn_kure": "1st Submarine Flotilla",
    "home_jpn_yokosuka": "2nd Submarine Flotilla",
    "home_fra_brest": "Force oceanique strategique",
}

# A squadron of at least this many boats sends one to sea - an SSBN, where it
# has one, on deterrent patrol - unless its base already has a submarine on
# patrol from the register.
PATROL_FROM = 3
