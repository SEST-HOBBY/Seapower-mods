"""Submarines: every navy's boats as a submarine force of their own, at the
bases they really sail from, with a boat from each larger squadron at sea
(asked for by the author, 11 Oct 2026: "add submarine to world campaign").

Until then a submarine sat in its base's harbour force with the frigates and
tankers, so the map showed none, and the navies with the largest submarine
arms had no submarine base at all: no Pearl Harbor, Groton, Kings Bay or
Bangor, no Faslane, no JMSDF Yokosuka. Dynamic Campaign Mod's own Pacific
1985 campaign keeps submarines the same way this does - as Surface forces of
their own (SUBRON 7, SSN Patrol Kamchatka), since the engine has no other
force type - and puts the ones at sea there with an "at" on their patrol.

Everything here is a SCENARIO ADDITION. Positions are the bases' public
locations, rounded; quantities are illustrative peacetime presence in
October 2028, not orders of battle. Squadron names are given only where the
real one is sure; every other force is "<base> submarines". Boats are named
only with the game's own hull names (vessel_names.ini) where the hull is the
real boat, so Dynamic Campaign Mod finds it; a stand-in hull carries the real
boat's name and the mod logs that it "sails as its class's default hull
under that name". Reviewed 13 Oct 2026 (facts, code, engine - adversarially
verified): the Ohio SSGNs other than Michigan are retired by October 2028,
ROKS Jang Bogo and Lee Chun are out of service, the Northern Fleet's attack
boats sail from Zaozersk, not Severomorsk, and Spain has two S-80s.

MAPPINGS says, for every (nation, unit) used here, how well the unit stands
for the real class - exact, same class, same family, representative or proxy
- and which flag the hull flies: the engine takes the flag from the hull's
own variant, not from the force, so a stand-in flies its donor's flag. A
SEST variant per navy would fix the flags; until one exists, they are
recorded here. UNUSABLE and MISSING list what the collection cannot field.
"""

from home_bases import naval

# New submarine bases, built like home_bases.py entries: no shipyard, and no
# depot where the navy has a main base that is one - their boats draw on it.
# Salamis and Golcuk are their navies' only bases in the campaign, so they are
# depots (and Golcuk, a naval shipyard, a yard).
SUB_BASES = [
    naval("US", "home_usa_pearl", "Joint Base Pearl Harbor-Hickam", 21.355, -157.945, [
        ("usn_ssn_virginia_block3_2026", 3), ("usn_ssn_virginia_block4", 2),
        ("usn_ssn_los_angeles_flt3_2027", 3)], yard=False, depot=False),
    naval("US", "home_usa_groton", "Naval Submarine Base New London (Groton)", 41.39, -72.09, [
        ("usn_ssn_virginia_block4", 3), ("usn_ssn_virginia_block3_2026", 2),
        ("usn_ssn_los_angeles_flt3_2027", 1)], yard=False, depot=False),
    naval("US", "home_usa_kings_bay", "Naval Submarine Base Kings Bay", 30.8, -81.52, [],
          yard=False, depot=False),
    naval("US", "home_usa_bangor", "Naval Base Kitsap-Bangor", 47.73, -122.72, [],
          yard=False, depot=False),
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
    naval("Greece", "home_grc_salamis", "Salamis Naval Base", 37.97, 23.545, [], yard=False),
    naval("Turkey", "home_tur_golcuk", "Golcuk Naval Base", 40.72, 29.81, []),
    naval("Russia", "home_rus_zaozersk", "Zaozersk (Zapadnaya Litsa)", 69.438, 32.38, [],
          yard=False, depot=False),
]

# Boats added at bases that already exist: (unit, count, names or None).
# Names are the game's own where the hull is the real boat.
SUB_ADD = {
    "wpac_guam_naval_base_apra_harbor": [("usn_ssn_los_angeles_flt3_2027", 2, None)],
    "usp_sandiego_naval_base_san_diego": [("usn_ssn_los_angeles_flt3_2027", 3, None)],
    "usa_norfolk_naval_station_norfolk": [("usn_ssn_virginia_block3_2026", 2, None),
                                          ("usn_ssn_los_angeles_flt3_2027", 2, None)],
    # The Atlantic SSBNs at Kings Bay, the Pacific ones at Bangor. The Ohio
    # SSGNs leave service FY2026-29: only Michigan is left in October 2028.
    "home_usa_kings_bay": [("usn_ssbn_ohio", 4, ["Tennessee SSBN-734", "West Virginia SSBN-736",
                                                 "Maryland SSBN-738", "Rhode Island SSBN-740"])],
    "home_usa_bangor": [("usn_ssbn_ohio", 6, ["Henry M. Jackson SSBN-730", "Alabama SSBN-731",
                                              "Nevada SSBN-733", "Pennsylvania SSBN-735",
                                              "Kentucky SSBN-737", "Nebraska SSBN-739"]),
                        ("usn_ssgn_ohio_2027", 1, ["Michigan SSGN-727"]),
                        ("usn_ssn_seawolf_2027", 2, ["Seawolf SSN-21", "Connecticut SSN-22"]),
                        ("usn_ssn_seawolf_carter", 1, ["Jimmy Carter SSN-23"])],
    "home_uk_faslane": [("rn_swiftsure_class_ssn", 5, ["HMS Astute", "HMS Ambush", "HMS Artful",
                                                      "HMS Audacious", "HMS Anson"])],
    # The register has five Collins at Stirling; HMAS Farncomb is in her
    # life-of-type extension at Osborne, so one more makes the six less one.
    "aus_stirling_hmas_stirling": [("ran_ssg_collins", 1, ["SSG 76 HMAS Dechaineux"])],
    "home_fra_brest": [("fr_ssbn_triomphant", 3, None)],
    "home_fra_toulon": [("fr_ssn_suffren", 2, None)],
    "home_jpn_kure": [("jmsdf_ssn_unryu", 4, None)],
    # KSS-I (Type 209/1200) boats still in service in 2028, the youngest three.
    "home_kor_jinhae": [("ch_ss_thomson_mlu", 3, ["ROKS Lee Sunsin SS-068",
                                                  "ROKS Na Daeyong SS-069",
                                                  "ROKS Lee Eokgi SS-071"])],
    "home_ind_mumbai": [("ch_ss_scorpene", 4, ["INS Kalvari", "INS Khanderi", "INS Karanj",
                                               "INS Vela"])],
    "home_isr_haifa": [("ger_ssk_type_212a_batch1", 3, ["INS Dolphin", "INS Tanin", "INS Rahav"])],
    "home_nor_haakonsvern": [("ger_ssk_type_212a_batch1", 2, ["KNM Ula", "KNM Utstein"])],
    # The 2028 boats are the baseline S-80s; the S-80 Plus refits come later.
    "home_esp_cartagena": [("ae_ssk_s80", 2, ["S81 Isaac Peral (Early)",
                                              "S82 Narciso Monturiol (Early)"])],
    # The Type 209 stand-ins sail under their real boats' names (22 Oct 2026):
    # unnamed, each would show the stand-in hull's default name, which since
    # Chile's update that day is its own lead boat, "Thomson". Greece's four
    # are the Type 214s (Papanikolis class), the boats sure to be in service
    # in 2028 while the older 209s are being replaced; Turkey's the Gur class
    # (Type 209/1400); Egypt's boats have numbers, not names.
    "home_grc_salamis": [("ch_ss_thomson_mlu", 4, ["HS Papanikolis S-120", "HS Pipinos S-121",
                                                   "HS Matrozos S-122", "HS Katsonis S-123"])],
    "home_tur_golcuk": [("ch_ss_thomson_mlu", 4, ["TCG Gur S-357", "TCG Canakkale S-358",
                                                  "TCG Burakreis S-359",
                                                  "TCG Birinci Inonu S-360"])],
    "home_egy_alexandria": [("ch_ss_thomson_mlu", 4, ["S41 (861)", "S42 (864)", "S43 (867)",
                                                      "S44 (870)"])],
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
    # Northern Fleet's attack boats at Zaozersk (Zapadnaya Litsa) - the Yasens
    # and Akulas home_bases.py had at Severomorsk, its surface-ship base, move
    # here - and the Pacific Fleet's Kilos at Vladivostok.
    "home_rus_gadzhiyevo": [("wp_ssbn_borei", 1, None), ("wp_ssbn_delta4", 2, None)],
    "home_rus_zaozersk": [("wp_ssgn_yasen", 2, ["K-560 Severodvinsk", "K-561 Kazan"]),
                          ("wp_ssgn_oscar2", 2, ["K-119 Voronezh", "K-266 Orel"]),
                          ("wp_ssn_akula", 2, None), ("wp_ssn_sierra2", 1, None)],
    "home_rus_vilyuchinsk": [("wp_ssbn_borei", 2, None), ("wp_ssgn_oscar2", 2, None),
                             ("wp_ssn_akula", 1, None)],
    "home_rus_vladivostok": [("wp_ss_improved_kilo", 3, None)],
    # North Korea: Romeo boats - the collection has no Sang-O.
    "home_prk_sinpo": [("plan_ss_romeo", 4, None)],
    "home_prk_nampo": [("plan_ss_romeo", 4, None)],
    "home_vnm_cam_ranh": [("wp_ss_improved_kilo", 6, ["HQ-182 Ha Noi", "HQ-183 Ho Chi Minh City",
                                                      "HQ-184 Hai Phong", "HQ-185 Khanh Hoa",
                                                      "HQ-186 Da Nang", "HQ-187 Ba Ria-Vung Tau"])],
}

SQUADRON_NAME = {
    "wpac_guam_naval_base_apra_harbor": "Submarine Squadron 15",
    "usp_sandiego_naval_base_san_diego": "Submarine Squadron 11",
    "usa_norfolk_naval_station_norfolk": "Submarine Squadrons 6 and 8",
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

# Where a squadron patrols, when the ring nearest its base is the wrong water:
# a base on enclosed water, whose nearest offshore ring lies across land, and
# the SSBN bases, whose deterrent patrol belongs off the shelf, not on it.
# Each is checked by the builder like any other ring (in bounds, on water).
PATROL_CENTRE = {
    "home_deu_eckernfoerde": (55.3, 15.0, "the Bornholm Basin: the nearest ring to Eckernfoerde "
                                          "lies across Jutland"),
    "home_jpn_kure": (32.6, 132.3, "the Hyuga-nada, out through the Bungo Channel: Kure is in "
                                   "the Inland Sea"),
    "home_tur_golcuk": (40.75, 28.3, "the Sea of Marmara"),
    "home_usa_kings_bay": (31.0, -78.8, "the Blake Plateau, off the shelf: a deterrent patrol"),
    "home_usa_bangor": (47.3, -126.5, "off the shelf beyond Juan de Fuca: a deterrent patrol"),
}

# (nation, unit): (quality, the real class it stands for, the flag the hull
# flies, note). Quality, best first: exact, same class, same family,
# representative (a modern boat of another class), proxy (stands in only).
MAPPINGS = {
    ("US", "usn_ssn_virginia_block3_2026"): ("exact", "Virginia class, Block III", "US", ""),
    ("US", "usn_ssn_virginia_block4"): ("exact", "Virginia class, Block IV", "US", ""),
    ("US", "usn_ssn_los_angeles_flt3_2027"): ("exact", "Los Angeles class, Flight III", "US", ""),
    ("US", "usn_ssbn_ohio"): ("exact", "Ohio class SSBN", "US", ""),
    ("US", "usn_ssgn_ohio_2027"): ("exact", "Ohio class SSGN", "US", "Michigan, the last in service"),
    ("US", "usn_ssn_seawolf_2027"): ("exact", "Seawolf class", "US", ""),
    ("US", "usn_ssn_seawolf_carter"): ("exact", "Seawolf class (Jimmy Carter)", "US", ""),
    ("UK", "rn_swiftsure_class_ssn"): ("proxy", "Astute class", "UK",
                                       "Swiftsure class, retired 1992-2010: the collection has no "
                                       "Astute, and no SSBN at all"),
    ("Japan", "jmsdf_ssn_unryu"): ("proxy", "Soryu and Taigei classes (conventional)", "Japan",
                                   "Red Storm Arsenal's fictional nuclear Unryu class; the "
                                   "collection has no modern JMSDF submarine. Unnamed: the boats "
                                   "keep the mod's fictional names"),
    ("India", "wp_ss_kilo"): ("same class", "Sindhughosh class (Kilo, Project 877EKM)", "Soviet", ""),
    ("India", "ch_ss_scorpene"): ("same class", "Kalvari class (Scorpene)", "Chile",
                                  "Chile's Scorpenes are the only ones in the collection"),
    ("Germany", "ger_ssk_type_212a_batch1"): ("exact", "Type 212A, batch 1", "Germany", ""),
    ("Israel", "ger_ssk_type_212a_batch1"): ("representative", "Dolphin class", "Germany",
                                             "Dolphin II is a 212 derivative"),
    ("Norway", "ger_ssk_type_212a_batch1"): ("representative", "Ula class (Type 210)", "Germany", ""),
    ("Spain", "ae_ssk_s80"): ("exact", "S-80 class (baseline, before the AIP refit)", "Spain", ""),
    # The Type 209 stand-in is Chile's Thomson class (renamed from type_209
    # on 22 Oct 2026): the same 209/1400 hull and model, now in Chile's
    # refit fit (SUBTICS, Black Shark, SM-39 Block 2). Every boat is named
    # (SUB_ADD), so none shows the hull's default name, Chile's "Thomson".
    ("Greece", "ch_ss_thomson_mlu"): ("same family", "Type 214 (Papanikolis class)", "Chile",
                                      "the 214 is HDW's development of the 209; Greece's "
                                      "remaining Type 209s (Poseidon, Glavkos) are not placed"),
    ("Turkey", "ch_ss_thomson_mlu"): ("same class", "Preveze and Gur classes (Type 209/1400)",
                                      "Chile", ""),
    ("Egypt", "ch_ss_thomson_mlu"): ("same class", "Type 209/1400mod", "Chile", ""),
    ("South_Korea", "ch_ss_thomson_mlu"): ("same class", "Jang Bogo class, KSS-I (Type 209/1200)",
                                           "Chile",
                                           "Euromod's own KSS boats are unusable (UNUSABLE)"),
    ("Australia", "ran_ssg_collins"): ("representative", "Collins class", "Australia",
                                       "SEST_RAN_Fleet's Collins stand-in hull, under the real names"),
    ("France", "fr_ssbn_triomphant"): ("exact", "Triomphant class", "France", ""),
    ("France", "fr_ssn_suffren"): ("exact", "Suffren class (Barracuda)", "France", ""),
    ("China", "plan_ssbn_type_094a"): ("exact", "Type 094A (Jin)", "China", ""),
    ("China", "plan_ssbn_type_094"): ("exact", "Type 094 (Jin)", "China", ""),
    ("China", "plan_ssn_type_093"): ("exact", "Type 093 (Shang I)", "China", ""),
    ("China", "plan_ssn_type_093a"): ("exact", "Type 093A (Shang II)", "China", ""),
    ("China", "plan_ssn_type_093b"): ("exact", "Type 093B (Shang III)", "China", ""),
    ("China", "plan_ss_type_039a"): ("exact", "Type 039A (Yuan)", "China", ""),
    ("China", "plan_ss_type_039b"): ("exact", "Type 039B (Yuan)", "China", ""),
    ("China", "plan_ss_kilo"): ("exact", "Kilo class (Project 636)", "China", ""),
    ("Russia", "wp_ssbn_borei"): ("exact", "Borei class", "Soviet",
                                  "wp_ hulls register Soviet; SEST's Russian-flag fix reaches "
                                  "missions only"),
    ("Russia", "wp_ssbn_delta4"): ("exact", "Delta IV class", "Soviet", ""),
    ("Russia", "wp_ssgn_yasen"): ("exact", "Yasen class", "Soviet", ""),
    ("Russia", "wp_ssgn_oscar2"): ("exact", "Oscar II class", "Soviet", ""),
    ("Russia", "wp_ssn_akula"): ("exact", "Akula class", "Soviet", ""),
    ("Russia", "wp_ssn_sierra2"): ("exact", "Sierra II class", "Soviet", ""),
    ("Russia", "wp_ss_improved_kilo"): ("exact", "Improved Kilo (Project 636.3)", "Soviet", ""),
    ("Vietnam", "wp_ss_improved_kilo"): ("same class", "Hanoi class (Project 636.1)", "Soviet", ""),
    ("North_Korea", "plan_ss_romeo"): ("same class", "Romeo class", "China",
                                       "North Korea's Sang-O and Sinpo boats are MISSING"),
}

# Present upstream but not loadable by the game.
UNUSABLE = [
    ("South_Korea", "KSS-I, KSS-II, KSS-III (ko_SS-I, ko_SS-II, ko_SS-III)",
     "3789208859 Euromod-South Korea Navy",
     "the files sit in vessels/non/, a folder the game does not load"),
]

# Real classes the collection has no model of at all.
MISSING = [
    ("UK", "Vanguard and Dreadnought class SSBNs"),
    ("Japan", "Soryu and Taigei classes (Japan's boats are a fictional proxy)"),
    ("India", "Arihant class SSBN"),
    ("Indonesia", "Nagapasa class (the Chinese-supplied Type 039B boats of the author's scenario "
                  "stand for the force; a Type 209 would fly Chile's flag)"),
    ("Canada", "Victoria class"),
    ("RoC", "Hai Lung and Hai Kun classes"),
    ("Sweden", "Gotland, Sodermanland and A26 classes"),
    ("Netherlands", "Walrus class"),
    ("North_Korea", "Sang-O and Sinpo classes"),
    ("Iran", "Ghadir and Fateh classes (Iran's Kilos are in the register)"),
]
