"""The allied fleet an Open Allocation campaign sells beside its own roster.

Review of 2e845dc9 (28 Sep): carriers priced as hulls, like the amphibians -
ships come without aircraft and no row launches from a bought deck (Ford 650,
Nimitz 600, Charles de Gaulle 550); the Ticonderogas out (every one retires
by the end of FY2027), Eisenhower out of the Nimitz picks (hull life ends
October 2027), the F-35C's disestablished VFA-101 and the Super Hornet's
VFA-115 (now on the F-35C) out; the F124/F125 spelled as their files are
(MLU); Zumwalt 480 (its CPS cannot strike ships), Jeongjo 520, Sejong 480,
Iver Huitfeldt 400 (SM-2 and APAR, the F124's family), Galicia 250 (Choules
is its copy).

Curated on 28 Sep from the enabled collection (scratch inventory of every
unit file whose variants or squadrons are registered to an allied nation):
one entry per class per navy, the most modern and complete file where mods
duplicate one, picks in service in October 2028 and registered to one
nation. Prices are capability tiers on the campaign's own scale - Anzac 240,
Hobart 480, Arafura 100, F-35A 45, P-8 55, Seahawk 20 - and are list prices:
no same-nation discount reaches another navy's units. The builder re-checks
every pick against the winning file (roster_ini), keeps an aircraft only if
some air-tasking row in the campaign launches and recovers it
(usable_allied), and stops on a unit whose picks are not one nation
(roster_nations). Southern Watch build notes, "The allied fleet".
"""


def _e(unit, picks, points, note):
    return dict(unit=unit, picks=picks, points=points, note=note)


ALLIED = [
    # --- USA ---------------------------------------------------------
    _e('usn_cvn_gerald_r_ford', ['Variant1', 'Variant2'], 650,
       'USA - Gerald R. Ford-class'),
    _e('usn_cvn_nimitz_2027s_adou', ['Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant8', 'Variant10'], 600,
       'USA - Nimitz-class (2027s) ADOU'),
    _e('usn_ddg-1000_cps', ['Variant1', 'Variant3'], 480,
       'USA - Zumwalt-class (CPS)'),
    _e('usn_lhd_wasp', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant7', 'Variant8'], 550,
       'USA - Wasp-class'),
    _e('usn_ddg_arleigh_flt3_2027', ['Variant1', 'Variant2', 'Variant3'], 520,
       'USA - Arleigh Burke Flt.3'),
    _e('usn_ddg_arleigh_flt2A_119_2027', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant7'], 480,
       'USA - Arleigh Burke Flt.2A [119~127]'),
    _e('usn_ddg_arleigh_flt2_072_2027', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5'], 450,
       'USA - Arleigh Burke Flt.2 [072~077]'),
    _e('usn_ddg_arleigh_flt1_054_2027', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant7', 'Variant8', 'Variant9', 'Variant10', 'Variant11', 'Variant12', 'Variant13'], 440,
       'USA - Arleigh Burke Flt.1 [054~070]'),
    _e('usn_taoe_supply', ['Variant1', 'Variant3'], 180,
       'USA - Supply-class T-AOE (stand-in)'),
    _e('usn_take_lewis_clark', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 170,
       'USA - Lewis and Clark-class T-AKE (stand-in)'),
    _e('usn_tao_kaiser', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 140,
       'USA - Henry J. Kaiser-class T-AO (stand-in)'),
    _e('usn_ssn_seawolf_2027', ['Variant1', 'Variant2'], 520,
       'USA - Seawolf SSN (2027)'),
    _e('usn_ssn_virginia_block5', ['Variant1'], 500,
       'USA - Virginia Class (Block V)'),
    _e('usn_ssn_virginia_block4', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant7', 'Variant8', 'Variant9', 'Variant10'], 490,
       'USA - Virginia Class (Block IV)'),
    _e('usn_ssn_virginia_block3_2026', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant7', 'Variant8'], 480,
       'USA - Virginia Class (Block III) 2026'),
    _e('usn_ssn_virginia_block2_2026', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6'], 470,
       'USA - Virginia Class (Block II) 2026'),
    _e('usn_ssn_virginia_block1_2026', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 460,
       'USA - Virginia Class (Block I) 2026'),
    _e('usn_ssn_los_angeles_flt3_2026', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant7', 'Variant8', 'Variant9', 'Variant10', 'Variant11', 'Variant12', 'Variant13', 'Variant14', 'Variant15', 'Variant16', 'Variant17'], 380,
       'USA - Los Angeles-class Flt3 (2026)'),
    _e('usaf_b-2_spirit', ['Squadron1', 'Squadron2', 'Squadron3'], 150,
       'USA - B-2 Spirit'),
    _e('usaf_b-1b_dts', ['Squadron1', 'Squadron2'], 130,
       'USA - B-1B'),
    _e('dts_b-52h', ['Squadron1'], 120,
       'USA - B-52H'),
    _e('usaf_e-3g', ['Squadron1', 'Squadron2'], 90,
       'USA - E-3G'),
    _e('usaf_f-22_s6', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7'], 70,
       'USA - F-22A(S-6)'),
    _e('usaf_kc-46a_warp', ['Squadron1', 'Squadron2'], 70,
       'USA - KC-46 Pegasus (WARPs)'),
    _e('usn_e-2d', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7', 'Squadron8', 'Squadron9'], 70,
       'USA - E-2D'),
    _e('usaf_f-15ex_SEII', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7', 'Squadron8'], 55,
       'USA - F-15EX Eagle II'),
    _e('usn_p8_2027', ['Squadron1'], 55,
       'USA - P-8A Poseidon (2027)'),
    _e('usn_f-35c', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7', 'Squadron8', 'Squadron9', 'Squadron10', 'Squadron12', 'Squadron13'], 50,
       'USA - F-35C'),
    _e('usaf_f-15e_SE', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5'], 45,
       'USA - F-15E'),
    _e('usaf_ac-130j', ['Squadron1'], 40,
       'USA - AC-130J'),
    _e('usn_fa-18e', ['Squadron2'], 35,
       'USA - F/A-18E'),
    _e('usaf_f-16cm-bl52d', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7', 'Squadron8'], 32,
       'USA - F-16CM block 50/52'),
    _e('usaf_mq-9_er', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5'], 30,
       'USA - MQ-9ER'),
    _e('usmc_uh-1y', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7', 'Squadron8', 'Squadron9', 'Squadron10'], 16,
       'USA - UH-1Y Venom'),
    # --- United Kingdom ----------------------------------------------
    _e('rn_ddg_type45_26', ['Variant3', 'Variant5'], 460,
       'United Kingdom - Type 45 class'),
    _e('rn_ff_type23', ['Variant3', 'Variant8', 'Variant9', 'Variant10', 'Variant11', 'Variant12'], 260,
       'United Kingdom - Type 23 class (LIFEX)'),
    _e('rn_aor_tide', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 160,
       'United Kingdom - Tide-class AOR (stand-in)'),
    _e('rn_opv_river_batch2', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5'], 80,
       'United Kingdom - River class (Batch II)'),
    _e('raf_ef2000_fgr4_late', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7', 'Squadron8'], 45,
       'United Kingdom - Eurofighter Typhoon FGR.4 RAF'),
    _e('rn_merlin_hm2', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4'], 25,
       'United Kingdom - Merlin HM.2'),
    _e('rn_wildcat', ['Squadron1', 'Squadron2', 'Squadron3'], 18,
       'United Kingdom - AW159 Wildcat HMA2'),
    # --- France ------------------------------------------------------
    _e('fr_cvn_charles-de-gaulle', ['Variant1'], 550,
       'France - Charles de Gaulle (2018-2027)'),
    _e('fr_lhd_mistral', ['Variant1', 'Variant2', 'Variant3'], 450,
       'France - Mistral class'),
    _e('fr_ddg_horizon', ['Variant1', 'Variant2'], 420,
       'France - Horizon class'),
    _e('fr_ffg_aquitaine_asw', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 360,
       'France - Aquitaine-class (ASW)'),
    _e("fr_fdi_amiral_ronarc'h", ['Variant1', 'Variant2'], 320,
       "France - Amiral Ronarc'h class"),
    _e('fr_ffg_lafayette_modernized', ['Variant2', 'Variant3'], 200,
       'France - La Fayette-class modernized'),
    _e('fr_ssn_suffren', ['Variant1', 'Variant2', 'Variant3'], 440,
       'France - Suffren-class'),
    _e('fr_e2d', ['Squadron1'], 70,
       'France - E-2D'),
    _e('fr_atl2', ['Squadron1', 'Squadron2'], 50,
       'France - Breguet Atlantique 2'),
    _e('fr_rafale_m_l', ['Squadron1', 'Squadron2', 'Squadron3'], 50,
       'France - Rafale M Late'),
    _e('fr_rafale_b_l', ['Squadron1', 'Squadron2', 'Squadron3', 'Squadron4', 'Squadron5', 'Squadron6', 'Squadron7', 'Squadron8', 'Squadron9', 'Squadron10', 'Squadron11', 'Squadron12', 'Squadron13', 'Squadron14', 'Squadron15', 'Squadron16', 'Squadron17', 'Squadron18', 'Squadron19'], 45,
       'France - Rafale B Late'),
    _e('fr_ec_665_had-e', ['Squadron1'], 20,
       'France - EC-665 Tigre'),
    _e('fr_nh90', ['Squadron1'], 20,
       'France - NH-90 FR'),
    _e('fr_as-565_sa', ['Squadron1'], 16,
       'France - AS-565 SA'),
    # --- Germany -----------------------------------------------------
    _e('ger_ffg_f124_MLU', ['Variant1', 'Variant2', 'Variant3'], 400,
       'Germany - F124 Sachsen-class MLU'),
    _e('ger_ffg_f123_2025_mlu', ['Variant2', 'Variant3', 'Variant4'], 300,
       'Germany - F123B Brandenburg-class'),
    _e('ger_ffg_f125_MLU', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 300,
       'Germany - F125 Baden-Wuerttemberg-class MLU'),
    _e('ger_ssk_type_212a_batch1', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 280,
       'Germany - Type 212A-class (Batch 1)'),
    _e('eu_ef2000_fgr4_late', ['Squadron1'], 45,
       'Germany - Eurofighter Typhoon FGR.4 Late'),
    _e('ger_nh90', ['Squadron1'], 20,
       'Germany - NH-90 DE'),
    # --- Italy -------------------------------------------------------
    _e('ita_ddg_orizzonte_18', ['Variant1', 'Variant2'], 420,
       'Italy - Andrea Doria class'),
    _e('ita_ffg_fremm', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5'], 360,
       'Italy - Bergamini class (GP)'),
    _e('ita_ffg_ppa', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5'], 300,
       'Italy - Thaon di Revel class'),
    _e('mm_ddgh_durand_de_la_penne_02', ['Variant2'], 260,
       'Italy - Luigi Durand de la Penne-class'),
    _e('ita_fs_ppx', ['Variant1', 'Variant2'], 100,
       'Italy - Vivaldi Class'),
    _e('ita_ssk_todaro_batch1', ['Variant1', 'Variant2'], 280,
       'Italy - Todaro class (Batch I)'),
    _e('mm_av-8b_plus', ['Squadron1'], 28,
       'Italy - AV-8B+ Harrier II'),
    _e('ita_sh-101a', ['Squadron1', 'Squadron2'], 25,
       'Italy - SH-101A'),
    _e('ita_sh90', ['Squadron1'], 20,
       'Italy - SH-90 IT'),
    # --- Spain -------------------------------------------------------
    _e('ae_lhd_juan_carlos', ['Variant1'], 500,
       'Spain - Juan Carlos I_L61-class L61'),
    _e('ae_ffg_alvaro_bazan', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 420,
       'Spain - Alvaro de Bazan-class (Early)'),
    _e('ae_ffg_bonifaz', ['Variant1'], 360,
       'Spain - Bonifaz-class'),
    _e('ae_lpd_galicia', ['Variant1', 'Variant2'], 250,
       'Spain - Galicia_L50-class L50'),
    _e('ae_ffg_santa_maria_late', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6'], 220,
       'Spain - Santa Maria-class Late'),
    _e('ae_opv_meteoro', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6'], 100,
       'Spain - Meteoro-class Meteoro'),
    _e('ae_ssk_s80', ['Variant1', 'Variant2'], 270,
       'Spain - S80-class'),
    _e('spa_ef2000', ['Squadron2', 'Squadron3', 'Squadron4'], 45,
       'Spain - C.16 Typhoon'),
    _e('spa_av-8b_plus', ['Squadron1'], 28,
       'Spain - AV-8B+'),
    # --- Netherlands -------------------------------------------------
    _e('rnn_ddg_zeven_mlu', ['Variant1', 'Variant2'], 430,
       'Netherlands - Zeven Provincien MLU Class'),
    _e('rnn_ffg_karel_eol', ['Variant1', 'Variant2'], 240,
       'Netherlands - Karel Doorman Class EOL'),
    _e('rnn_ffg_hol', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 100,
       'Netherlands - Holland Class'),
    _e('nl_nh90', ['Squadron1'], 20,
       'Netherlands - NH-90 NL'),
    # --- Norway ------------------------------------------------------
    _e('knm_cor_skjold', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6'], 130,
       'Norway - Skjold Class'),
    # --- Denmark -----------------------------------------------------
    _e('hdms_iver_huitfeldt', ['Variant2', 'Variant3'], 400,
       'Denmark - Iver Huitfeldt-class'),
    # --- Poland ------------------------------------------------------
    _e('wp_ss_kilo', ['Variant12'], 200,
       'Poland - Kilo-class'),
    # --- Japan -------------------------------------------------------
    _e('jmsdf_ddg_maya', ['Variant1', 'Variant2'], 500,
       'Japan - Maya-class'),
    _e('jmsdf_ddg_atago', ['Variant1', 'Variant2'], 480,
       'Japan - Atago-class'),
    _e('jmsdf_dd_asahi', ['Variant1', 'Variant2'], 360,
       'Japan - Asahi-class'),
    _e('js_ffg_mogami', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant7', 'Variant8', 'Variant9', 'Variant10'], 300,
       'Japan - Mogami-class'),
    _e('jmsdf_aoe_mashuu', ['Variant1', 'Variant2'], 160,
       'Japan - Mashuu-class AOE (stand-in)'),
    _e('jp_f-2a_late', ['Squadron1', 'Squadron2', 'Squadron3'], 35,
       'Japan - F-2A (JASDF/Late)'),
    _e('jmsdf_sh-60k', ['Squadron1', 'Squadron2'], 22,
       'Japan - SH-60K'),
    _e('jmsdf_sh-60j', ['Squadron1', 'Squadron2'], 18,
       'Japan - SH-60J'),
    # --- South Korea -------------------------------------------------
    _e('ko_ddg-995', ['Variant1', 'Variant2', 'Variant3'], 520,
       'South Korea - Jeongjo the Great Class'),
    _e('ko_ddg-991', ['Variant1', 'Variant2', 'Variant3'], 480,
       'South Korea - Sejong the Great Class'),
    _e('ko_ddh-975_kvls', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6'], 320,
       'South Korea - Chungmugong Yi Sun-sin Class'),
    _e('ko_ffg-828', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5'], 300,
       'South Korea - Chungnam Class'),
    _e('ko_ffg-818', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6', 'Variant7', 'Variant8'], 280,
       'South Korea - Daegu Class'),
    _e('ko_ffg-811', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6'], 240,
       'South Korea - Incheon Class'),
    _e('ko_ddh-971', ['Variant1', 'Variant2', 'Variant3'], 220,
       'South Korea - Gwanggaeto the Great Class'),
    # --- Australia ---------------------------------------------------
    _e('ran_lhd_canberra', ['Variant1', 'Variant2'], 500,
       'Australia - Canberra-class LHD'),
    _e('ran_lsd_choules', ['Variant1'], 250,
       'Australia - HMAS Choules LSD (stand-in)'),
    _e('ran_aor_supply', ['Variant1', 'Variant2'], 160,
       'Australia - Supply-class AOR (stand-in)'),
    _e('ran_ssg_collins', ['Variant1', 'Variant2', 'Variant3', 'Variant4', 'Variant5', 'Variant6'], 280,
       'Australia - Collins-class SSG (stand-in)'),
    _e('usa_ah-64e', ['Squadron4'], 22,
       'Australia - AH-64E'),
]

# Red Line's PLAN commander calls on no allied fleet, but its Open
# Allocation twin sold no replenishment ship at all until October 2026,
# although the pack builds two modern PLAN ones (SEST Replenishment's Type
# 901 Fuyu and Type 903A Fuchi clones, every variant registered to China)
# and the carrier group sails with a 901 in The Order to Withdraw. Story
# Red Line still sells none: it rearms at its windows, and a bought hull
# needs a row to sail in. Prices on Red Line's own scale - 054A 280, Luda
# 160, 056A 120: the 901 is the carrier group's 48,000-tonne station ship,
# the 903A a 23,000-tonne replenishment oiler.
PLAN_SUPPORT = [
    _e('plan_aor_type901', ['Variant1', 'Variant2'], 200,
       'China - Type 901 Fuyu fast combat support ship'),
    _e('plan_aor_type903a', ['Variant1', 'Variant2', 'Variant3', 'Variant4'], 150,
       'China - Type 903A Fuchi replenishment oiler'),
]

# Keyed by commander nation: the RAN campaigns call on the allied fleet;
# Red Line's PLAN commander gets its own navy's support ships.
FOR_NATION = {"Australia": ALLIED, "China": PLAN_SUPPORT}
