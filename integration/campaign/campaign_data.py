#!/usr/bin/env python3
"""SEST SOUTHERN WATCH - The Northern Lifeline.

Twelve core missions and eight optional dispatches, built to the campaign
bible in docs/campaigns/southern-watch/. Australia and its regional partners
keep people, fuel and supplies moving through the northern approaches while a
maritime coercion campaign escalates into a limited regional war, October to
November 2028. Everything here is fiction: the Meridian Maritime Group, the
contested enclave, the named officers and the deployments.

WHAT THIS FILE IS

The campaign's script. build_pack.py is only the machinery that turns it into
files the game can load. Three rules hold everything together:

  1. Every unit names the mod it is there to exercise. That is enforced, not
     decorative: the builder resolves the load order and refuses to write the
     campaign if the game would read nothing of that mod when the unit spawns.
     "_vanilla" is a legal answer and means "this one is stock" - which is how
     a unit that should have come from a mod gets caught when something
     outranks it.

  2. No position is invented. Stations sit on water or ground a mission
     already in this repo (or in the stock game) has put a unit of that kind
     on, and the builder snaps to the nearest such point. The theatres are
     therefore the collection's own - the Arafura, Timor and Banda seas, the
     Coral Sea, Papua and the Darwin approaches.

  3. Experimental equipment stays in its declared branch. JATM, MALICE,
     AIM-424, Rafale F5 LRASM, the YF-23, J-36, J-50, RQ-180 and Type 004 are
     fiction; they appear in FUTURE FRONT and are labelled there. Cold War and
     retired types live in COLD SEA. The 2028 core flies conventional fits.

WHAT IS NOT PROVEN

Static resolution is not a play test. Nothing here establishes that a
helicopter can recover aboard its assigned ship, that replenishment transfers
actually move fuel, that a briefing's tanker can pass gas to its receiver, or
that a trigger fires when the game is running. SW09 is written around
survival and a service window rather than a replenishment mechanic for exactly
that reason, and the campaign's own notes say so.
"""

INFO_DESC = (
    "SOUTHERN WATCH - The Northern Lifeline. Twelve connected missions, "
    "October-November 2028: Australia and its regional partners keep the "
    "northern sea routes open through a maritime coercion campaign that "
    "escalates into a limited regional war. Eight optional dispatches - "
    "allied rotations, an opposing-force passage, a weapons range, an openly "
    "speculative future branch and a Cold War anthology - give the rest of the "
    "collection a purposeful role. Fiction throughout. "
    "See docs/campaign-coverage.md for which mod supplies what.")


def U(side, mod, type, station, **kw):
    """One placed unit: whose side, which mod it is there to exercise, what it
    is, and where it stands. Hull variant, squadron and loadout are resolved
    from the winning file at build time, not guessed here."""
    return dict(side=side, mod=mod, type=type, station=station, **kw)


def S(lat, lon, label, heading=90, alt=None):
    st = dict(at=(lat, lon), label=label, heading=heading)
    if alt is not None:
        st["alt"] = alt
    return st


# Mods with nothing a mission can name. The builder rejects an excuse that has
# become untrue, so this list can only shrink.
EXCUSES = {
    "anchor-chain": (
        "library", "ships one file, `_info.ini` - the dependency marker other "
        "mods list; there is nothing to place"),
    "auto-time-on-target": (
        "library", "salvo-timing behaviour with no data files; it applies to "
        "every mission and no mission may depend on it"),
    "better-tacmap": (
        "library", "player interface - ships `settings.cfg` and nothing else"),
    "euromod-anchorchain-expansion": (
        "library", "well-deck and effects framework: 182 effect files, six "
        "`systems/` files and 66 ammunition overwrites that the EuroMod hulls "
        "in WESTERN PASSAGE and THE RELIEF SHIP resolve through"),
    "SEST_Campaign": (
        "campaign", "this pack: it ships the campaign, its missions, its "
        "requisition roster and their briefings. It is what the coverage below "
        "is measured on, so it cannot place a unit to reach itself"),
    "SEST_TacMap_Colors": (
        "library", "recolours the tactical map (`ui/`); no unit, no round"),
    "y-8-y-9-family": (
        "shadowed", "all twelve airframes are outranked by Modern PLAN "
        "Systems, which ships the same ids higher in the order - it is an "
        "intentional overlapping source, not a missing one"),
    "nimitz-expanded": (
        "shadowed", "ships one file, `vessels/usn_cvn_nimitz_variants.ini`, "
        "which SEST Collection Fixes replaces - that patch is why it exists"),
}

EVENTS = [
    dict(file="00_opening", title="White Water\\n18 October 2028",
         sub="A missed rendezvous in the Arafura Sea",
         dateline="18 OCTOBER 2028  |  MARITIME BORDER COMMAND, DARWIN",
         headline="THE NORTH GOES QUIET",
         body=[
             "It started as paperwork. A merchant missed its reporting window. "
             "A cable-repair ship received movement instructions from an office "
             "that does not exist. Two ports lost their cargo records in the "
             "same week, and insurers began declining voyages that were still "
             "legal and perfectly possible.",
             "The Meridian Maritime Group has an answer for all of it: travel "
             "in escorted groups, accept its inspections, use its terminals. "
             "Most of its ships are ordinary commerce. A few are not, and "
             "nothing you can see at twelve miles tells you which is which.",
             "This morning MV Coral Pioneer reported an engine casualty and an "
             "escort claiming the authority to inspect her. The Indonesian "
             "patrol sent to look has reported gunfire. HMAS Warramunga is the "
             "nearest coalition ship.",
             "Bring the convoy together. Get the crews out of danger. Identify "
             "before you shoot - none of this is a war yet."]),
    dict(file="06_interlude", before="The Open Door",
         title="The Enclave\\n12 November 2028",
         sub="A contested airfield, foreign advisers and a relief window",
         dateline="12 NOVEMBER 2028  |  COALITION JOINT INTELLIGENCE",
         headline="SOMEONE ELSE'S AIR DEFENCE",
         body=[
             "Regional security forces have recovered most of the facilities "
             "Meridian's hard-line faction seized. One airfield and port "
             "enclave has not come back, and the battery covering it is not "
             "the man-portable inventory the first reports described.",
             "A naval force has arrived under a protection-and-evacuation "
             "pretext and demanded the coalition patrols suspend. A small "
             "foreign expeditionary detachment is supporting the enclave under "
             "a separate arrangement. Its fuel and ammunition arrive by routes "
             "we can see, which is the one advantage we have.",
             "Local authorities have asked for a protected window to move "
             "civilians and emergency supplies out. That window, not a body "
             "count, is the objective."]),
    dict(file="12_closing", title="The First Ship Through\\n28 November 2028",
         sub="An imperfect ceasefire and a working sea route",
         dateline="28 NOVEMBER 2028  |  MARITIME BORDER COMMAND, DARWIN",
         headline="THE LANES ARE OPEN",
         body=[
             "Coral Pioneer made her destination with a cracked bearing and a "
             "volunteer engineer from the escort. Two hundred miles behind her, "
             "one group complied with its withdrawal order and another spent "
             "the afternoon deciding whether to.",
             "The route is open. The partner governments that asked for help "
             "still hold their own ports. Most of the crews went home.",
             "What is left of your task group is alongside at Darwin, and the "
             "ledger says which ships are in it. That is the whole measure of "
             "this campaign - not the exchange rate, the sea route and the "
             "people who used it.",
             "Stand down the watch."]),
]

# =============================================================================
# NATIVE TASK FORCE MODE
#
# Bible v1.1 corrects v1.0 on this point, and the correction is right: the
# exported Pacific Strike campaign under mods-source/_vanilla/original/campaigns/
# is a working Task Force Mode reference, so persistence, repair, rearm and the
# requisition budget are native features rather than something a manual ledger
# has to imitate. Every key below was read out of that campaign before it was
# used here; none of them is invented.
#
# What that does NOT establish is that these particular numbers are balanced,
# or that a modded hull can actually be bought, crewed and deployed. Section 16
# of the bible lists the seven-step acceptance run that would settle it, and it
# needs the running game.
# =============================================================================

TASKFORCE = dict(
    Enabled="True",
    TaskForceRequireFlagship="False",
    DefaultTaskForceName="Southern Watch Task Group",
    TaskForceNameOptions="Southern Watch Task Group|TG 627.1|Northern Escort Group",
    CommanderSettingsFile="commander_settings.ini",
    RosterFile="player_task_force_roster.ini",
    TaskForceDifficultyPresets="Supported|Standard|Veteran",
    DefaultTaskForceDifficultyPreset="Standard",
    StartingPoints="1000",
    PointCap="1500",
    ShipIncludesAirwing="False",
    PurchaseLoadouts="True",
    # One point per complete group of 100 survivors. Rescue is an objective and
    # a human consequence; it is not the campaign's income.
    CSARPointModifier="100",
    CrewSkillInitial="Trained",
    CrewSkillThresholds="Trained:1|Seasoned:4|Veterans:9|Ultra:16",
    UnitDecommissionPointReturnModifier="0.25",
    UnitDismissPointReturnModifier="0.5",
    DamageToAllowRepair="Light,Moderate",
    DamageToDisallowRepair="Heavy",
    RepairPointsCost="Light,0.1|Moderate,0.25",
)

# name, starting points, point cap, repair multiplier. Same objectives and the
# same prices in all three - only the budget and the repair bill move, so a
# package costed on one setting stays intelligible on another.
DIFFICULTIES = [
    ("Supported", 1250, 1500, "0.75"),
    ("Standard", 1000, 1500, "1"),
    ("Veteran", 850, 1250, "1.25"),
]

# The requisition roster. Points are fictional balance values; the variant and
# squadron lists are not - the builder rejects any that the winning file does
# not actually offer, which is the whole reason this is data and not prose.
ROSTER = [
    dict(unit="ran_ffh_anzac", picks=["Variant3", "Variant8"], points=240,
         note="Warramunga and Perth; HMAS Anzac herself decommissioned in 2024, "
              "so Variant1 stays out of the core roster"),
    dict(unit="ran_ddg_hobart", picks=["Variant1", "Variant2", "Variant3"], points=480),
    dict(unit="ran_opv_arafura", picks=["Variant1", "Variant2"], points=100,
         note="donor Meteoro fit is richer than the real Arafura; the campaign "
              "restricts it to two hulls until the fit is corrected"),
    dict(unit="ran_aor_supply", picks=["Variant1", "Variant2"], points=140,
         note="Teide stand-in; no SupplySystem_* block in the winning file, so "
              "replenishment is unproven and SW09 does not depend on it"),
    dict(unit="ran_lsd_choules", picks=["Variant1"], points=220),
    dict(unit="ran_lhd_canberra", picks=["Variant1", "Variant2"], points=420,
         note="helicopter-only in this campaign; the donor's allowed-aircraft "
              "list inherits Spanish fixed-wing types"),
    dict(unit="js_ffg_mogami", picks=["Variant1", "Variant2", "Variant3"], points=260,
         note="allied attachment; only purchasable once a persistent allied "
              "attachment is proved, otherwise it stays mission support"),
    dict(unit="ran_ssg_collins", picks=["Variant1", "Variant2"], points=320,
         note="S-80 stand-in; a submarine, so it goes in AllowedSubmarines"),
    dict(unit="raaf_f-35a", picks=["Squadron3"], points=45,
         note="No. 75 Squadron, RAAF Base Tindal - checked against the "
              "squadron file's own comment"),
    dict(unit="usn_fa-18f_blk3", picks=["Squadron8"], points=35,
         note="Australian squadron in the SEST Growler pack's output"),
    dict(unit="usn_ea-18g", picks=["Squadron6"], points=55,
         note="conventional EW/SEAD fits; MALICE stays in Future Front"),
    dict(unit="usn_p8", picks=["Squadron3"], points=45,
         note="the squadron file labels every entry USN; Squadron3 is the "
              "bible's choice, and the label is worth fixing upstream"),
    dict(unit="E7A_Wedgetail", picks=["Squadron1"], points=80,
         note="No. 2 Squadron RAAF, from the SEST Wedgetail pack"),
    dict(unit="raaf_mq-4c_triton", picks=["Squadron1"], points=60,
         note="unarmed in this implementation"),
    dict(unit="usaf_kc-46a_boom", picks=["Squadron1"], points=75,
         note="US support; receiver pairing is unverified"),
    dict(unit="usn_mh-60r", picks=["Squadron1"], points=20,
         note="one family chosen explicitly - usn_mh-60r_26 is a different "
              "unit and is never substituted for it"),
]

# Australian commander, no same-nation discount: the mod unit definitions carry
# US and allied nationality, and a discount keyed to them would be arbitrary.
# No emblem or ribbon art is referenced - every path would be a .png this repo
# cannot produce.
COMMANDER = """[CommanderSettings]
CommanderNations=Australia
CommanderDefaultNation=Australia
CommanderNameDefaultAustralia=Alex Mercer
CommanderStartingRankLevel=5
SameNationUnitDiscount=0

NavyNameAustralia=Royal Australian Navy
"""

MISSIONS = []

# =============================================================================
# CORE - SW01 to SW12. Australian-led, October-November 2028.
# =============================================================================

MISSIONS.append(dict(
    group="core", num="01", key="White Water", place="Arafura Sea",
    intro="Find the convoy, work out which contact is armed, and keep the "
          "rendezvous open. Nothing here is a target without identification.",
    date=(2028, 10, 18), time=(5, 40), sea=2, clouds="Scattered_1", wind="NW",
    difficulty=1, minutes=50, centre=(-10.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "ARAFURA SEA, 0540 local. MV Coral Pioneer missed her rendezvous forty "
        "minutes ago. Her last report mentioned an engine casualty and an "
        "escort claiming the authority to inspect the convoy. The Indonesian "
        "patrol sent to investigate has reported gunfire and nothing since.\\n\\n"
        "You are WARRAMUNGA with a Seahawk on the deck, a Poseidon on task for "
        "the first part of the morning and a Triton high to the north. Bring "
        "the merchants together and walk them east to the handover box.\\n\\n"
        "The lane is working traffic: a bulker, a chartered coaster, a relief "
        "freighter, trawlers and the 0600 Denpasar service overhead. One "
        "contact in that picture is a Meridian escort with weapons and one is "
        "a decoy hull that has squawked as a merchant since it sailed. "
        "Identify before you shoot. Your weapons are tight."),
    forces="HMAS Warramunga (Anzac class), one MH-60R, one P-8A on task, one "
           "MQ-4C Triton overhead. Four merchant hulls to collect, three "
           "neutral contacts in the box, one armed escort and one decoy.",
    objectives=[
        ("Convoy", "Walk the merchant group into the eastern handover box",
         "30,-30,Fail,Main"),
        ("Neutrals", "Harm no neutral shipping or aircraft", "0,-40,Complete"),
        ("Warramunga", "Bring Warramunga out intact", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(-10.1, 132.3), radius=25,
                 min_units=3, objective="Convoy"),
    protect=["convoy"], protect_min=2, protect_objective="Convoy",
    neutral_objective="Neutrals",
    win="The merchants are in the box and their crews are alive. The escort "
        "has been identified, and so has everything you did not shoot.",
    lose="The convoy is scattered and Coral Pioneer is not answering. Whatever "
         "this was, it worked.",
    stations={
        "warramunga": S(-10.05, 131.45, "HMAS Warramunga", heading=80),
        "convoy": S(-10.4, 131.9, "Coral Pioneer group", heading=80),
        "neutrals": S(-11.4, 129.6, "Arafura traffic", heading=250),
        "meridian": S(-10.5, 132.0, "Meridian escort", heading=250),
        "air": S(-10.6, 131.2, "Southern Watch air", heading=70, alt=22000),
        "high": S(-9.6, 131.4, "Triton orbit", heading=90, alt=50000),
        "liner": S(-11.2, 130.4, "Denpasar service", heading=260, alt=34000),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "warramunga",
          variant="Variant3", name="HMAS Warramunga", weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "air",
          name="Warramunga Flight", alt=3000, weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "air", squadron="Squadron3",
          name="Bluefin 21", alt=18000, weapons="Tight"),
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "high",
          name="Sentry 04", weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "convoy",
          name="MV Gove Trader"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_jeparit", "convoy",
          name="MV Jeparit (chartered)"),
        U("blue", "re-power-resupply", "civ_ms_freighter_a", "convoy",
          name="MV Sunda Relief"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "neutrals",
          name="Arafura trawler north"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "neutrals",
          name="Arafura trawler south"),
        U("neutral", "civil-aircraft-airbus", "civ_a320", "liner",
          name="Denpasar 214"),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "meridian",
          name="Meridian Escort 7"),
        U("red", "_vanilla", "wp_ms_mercur_decoy", "meridian",
          name="MV Meridian Assurance"),
    ],
))

MISSIONS.append(dict(
    group="core", num="02", key="Steel Highway", place="Coral Sea",
    intro="Four priority ships to Port Moresby. A submarine report on the "
          "planned track. The masters want to keep going.",
    date=(2028, 10, 21), time=(9, 20), sea=3, clouds="Broken_2", wind="SE",
    difficulty=2, minutes=75, centre=(-12.5, 148.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "CORAL SEA. Port Moresby has asked for engineering plant, medical "
        "stores and fuel, and the Pukpuk arrangements mean we deliver them. "
        "Four priority hulls are in company with HOBART, ARAFURA and SUPPLY, "
        "and a Wedgetail is up with a tanker behind it.\\n\\n"
        "Ninety minutes ago a Poseidon dropped a field on a diesel-electric "
        "contact across the planned track. The masters want to press on at "
        "twelve knots. We want time to classify it. You will not get both.\\n\\n"
        "Three of four must reach the Moresby approach box, and the medical "
        "and engineering ship is not one of the three you can trade away. "
        "Background traffic in this sea is ordinary commerce - it is not "
        "joining your convoy and it is not your enemy."),
    forces="HMAS Hobart, HMAS Arafura, HMAS Supply, four priority merchants, "
           "E-7A Wedgetail and a KC-46 on the tanker track. One Type 039C in "
           "the area. Port Moresby is open behind you.",
    objectives=[
        ("Cargo", "Get three of four priority ships into the Moresby box",
         "35,-35,Fail,Main"),
        ("Medical", "MV Kokoda Star must arrive", "15,-25,Complete"),
        ("Neutrals", "Harm no neutral shipping", "0,-30,Complete"),
    ],
    # Three of four arrive AND the medical ship is one of them. Without the
    # second condition the mission could be won by leaving Kokoda Star safely
    # behind and sending the other three.
    victory=dict(kind="arrive", station="convoy", min_units=3,
                 objective="Cargo",
                 also=[dict(units=["convoy#1"], min_units=1)]),
    # Kokoda Star is the first hull at the convoy station: lose her and the
    # mission is over whatever the other three do.
    protect=["convoy#1"], protect_objective="Medical",
    neutral_objective="Neutrals",
    win="Three hulls alongside at Moresby, Kokoda Star among them. The "
        "engineering plant is ashore and the route is a route again.",
    lose="The convoy is short and Moresby is still waiting. The next one will "
         "have to be bigger, slower and later.",
    stations={
        "escort": S(-13.4, 148.4, "Escort group", heading=320),
        "convoy": S(-13.6, 148.6, "Priority convoy", heading=320),
        "traffic": S(-16.4, 150.0, "Coral Sea traffic", heading=200),
        "moresby": S(-9.5, 147.0, "Port Moresby", heading=0),
        "sub": S(-13.5, 148.2, "Submarine datum", heading=90),
        "air": S(-12.0, 148.0, "Air support", heading=320, alt=30000),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort",
          name="HMAS Hobart"),
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "escort",
          name="HMAS Arafura"),
        U("blue", "SEST_RAN_Fleet", "ran_aor_supply", "escort",
          name="HMAS Supply"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "air",
          name="Wedgetail 01", alt=32000, weapons="Hold"),
        U("blue", "kc-46a", "usaf_kc-46a_boom", "air", name="Texaco 51",
          alt=26000, weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_austral", "convoy",
          name="MV Kokoda Star"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_super_p", "convoy",
          name="MV Torres Trader"),
        U("blue", "re-power-resupply", "civ_ms_andizhan", "convoy",
          name="MV Lae Provider"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("neutral", "_vanilla", "civ_ms_car_carrier_a", "traffic",
          name="Coral Sea vehicle carrier"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "traffic",
          name="Coral Sea trawler"),
        U("blue", "modern-us-airbase", "airbase_us", "moresby",
          name="Jackson Field", nation="australia", weapons="Hold"),
        U("blue", "buildings-targets-missions", "Liberty", "moresby",
          name="Moresby wharf", weapons="Hold"),
        U("red", "plan-submarines", "plan_ss_type_039c", "sub",
          name="Contact BRAVO"),
    ],
))

MISSIONS.append(dict(
    group="core", num="03", key="Rig Seventeen", place="Timor Sea",
    intro="Civilians on an offshore platform, armed contractors on the deck "
          "above them, and a patrol closing from the north.",
    date=(2028, 10, 24), time=(16, 10), sea=3, clouds="Overcast", wind="W",
    difficulty=2, minutes=60, centre=(-11.0, 126.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR SEA, late afternoon. Rig Seventeen stopped answering its shore "
        "office on Tuesday. Forty-one contract staff are still aboard, and the "
        "people holding the platform have a helicopter deck, a shore battery "
        "on the nearest headland and an air-defence vehicle they were not "
        "supposed to have.\\n\\n"
        "The coastal state has asked for help and set the boundary: you may "
        "cover an evacuation, you may not level the installation. CHOULES is "
        "in company with CANBERRA and there are two Super Stallions for the "
        "lift.\\n\\n"
        "Get the transports in, get the people off, get everybody out before "
        "the light goes. Not every platform out here is theirs and most of "
        "this coast is working its ordinary week."),
    forces="HMAS Choules and HMAS Canberra with two CH-53E for the lift. "
           "Ashore: a launcher site, a VL MICA battery, a Sosna vehicle and "
           "technicals. One armed platform.",
    objectives=[
        ("Evacuate", "Get the lift helicopters clear to the south",
         "35,-35,Fail,Main"),
        ("Platform", "Leave the civilian platform standing", "10,-20,Complete"),
        ("Ships", "Bring both amphibious ships home", "10,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="lift", at=(-12.0, 126.4), radius=25,
                 min_units=1, objective="Evacuate"),
    protect=["amphib"], protect_min=1, protect_objective="Ships",
    neutral_objective="Platform",
    win="Both airframes are south of the line with the platform crew aboard. "
        "Rig Seventeen is still standing and somebody else can argue about "
        "who owns it.",
    lose="The window closed with people still on the deck. There will not be "
         "another one this week.",
    stations={
        "amphib": S(-11.6, 126.6, "Amphibious group", heading=10),
        "lift": S(-11.3, 126.5, "Lift flight", heading=350, alt=2000),
        "rig": S(-10.6, 126.4, "Rig Seventeen", heading=0),
        "shore": S(-8.6, 125.6, "Contested headland", heading=180),
        "traffic": S(-12.0, 124.6, "Timor traffic", heading=100),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_lsd_choules", "amphib",
          name="HMAS Choules"),
        U("blue", "SEST_RAN_Fleet", "ran_lhd_canberra", "amphib",
          name="HMAS Canberra"),
        U("blue", "ch-53e-standalone", "usmc_ch53_standalone", "lift",
          name="Lifter 11", alt=1500, weapons="Tight"),
        U("blue", "ch-53e-standalone", "usmc_ch53_standalone", "lift",
          name="Lifter 12", alt=1500, weapons="Tight"),
        U("neutral", "armed-oil-rig", "civ_spar_rig_helo", "rig",
          name="Rig Seventeen", snap="sea"),
        U("neutral", "_vanilla", "civ_ms_ritina", "traffic",
          name="Timor tanker"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "traffic",
          name="Timor fishing boat"),
        U("red", "shahed-136-zero-two", "shahed_tel_black", "shore",
          name="Meridian launcher site"),
        U("red", "sam-pack", "fr_vl-mica_tel", "shore",
          name="Contract air defence"),
        U("red", "ground-upgrade-spaa", "ru_spaa_mt-lb_sosna", "shore",
          name="Sosna vehicle"),
        U("red", "pickup-truck-extension", "civ_car_pickup_1983_assault_civ",
          "shore", name="Technical, headland road"),
        U("red", "buildings-targets-missions", "Oil_pump", "shore",
          name="Shore tank farm"),
    ],
))

MISSIONS.append(dict(
    group="core", num="04", key="The Quiet Passenger", place="Banda approaches",
    intro="A low-profile craft, a genuine submarine somewhere in the same "
          "water, and a whale that will waste an hour of your life.",
    date=(2028, 10, 27), time=(2, 30), sea=2, clouds="Clear", wind="E",
    difficulty=2, minutes=45, centre=(-6.0, 130.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "BANDA APPROACHES, middle watch. Something small and low is running "
        "south out of the Seram passage with almost no freeboard and no "
        "transponder. It may be carrying weapons for the enclave, it may be "
        "carrying people, and the difference decides what you are allowed to "
        "do about it.\\n\\n"
        "You have ARAFURA, a Seahawk and a Poseidon working the same box. "
        "There is also a real submarine in this water - a Type 039 that has "
        "been quiet for eleven hours - and a biologic contact that three "
        "different ships have now reported as a hostile boat.\\n\\n"
        "Track the passenger into the handover box to the south. Classify "
        "what else is down there. Do not lose the patrol vessel doing it."),
    forces="HMAS Arafura, one MH-60R, one P-8A. In the water: one low-profile "
           "craft, one Type 039 submarine, one very large mammal. Overhead: a "
           "KJ-500 and a Ka-28 working for somebody else.",
    objectives=[
        ("Track", "Walk the low-profile craft into the southern box",
         "30,-30,Fail,Main"),
        ("Patrol", "Keep HMAS Arafura afloat", "15,-25,Complete"),
        ("Neutrals", "Do not shoot the wildlife or the fishermen",
         "0,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="passenger", at=(-7.1, 130.1),
                 radius=20, min_units=1, objective="Track"),
    protect=["patrol"], protect_objective="Patrol",
    neutral_objective="Neutrals",
    win="The passenger is in the box with a boarding party alongside and the "
        "Type 039 knows exactly how long you held it. The route is on paper "
        "now.",
    lose="It is gone into the passage and the only thing you positively "
         "identified all night had a blowhole.",
    stations={
        "patrol": S(-5.9, 130.3, "HMAS Arafura", heading=200),
        "passenger": S(-5.2, 130.2, "Low-profile craft", heading=195),
        "sub": S(-4.6, 130.1, "Type 039 datum", heading=180),
        "whale": S(-6.9, 130.2, "Biologic contact", heading=150),
        "fishing": S(-5.1, 128.2, "Banda fishing fleet", heading=90),
        "air": S(-6.2, 130.6, "Patrol aircraft", heading=0, alt=16000),
        "red_air": S(-4.4, 129.9, "PLAAF orbit", heading=180, alt=28000),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "patrol",
          name="HMAS Arafura", weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "air", name="Arafura Flight",
          alt=2500, weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "air", squadron="Squadron3",
          name="Bluefin 24", alt=15000, weapons="Tight"),
        U("red", "red-storm-arsenal", "_narco_narcosub_adv", "passenger",
          name="Contact WHISKEY"),
        U("red", "plan-submarines", "plan_ss_type_039", "sub",
          name="Contact SIERRA"),
        U("red", "modern-plan-systems", "plaaf_kj-500", "red_air",
          name="Dragon Eye 03", weapons="Hold"),
        U("red", "modern-plan-systems", "plan_ka-28", "red_air",
          name="Helix 11", alt=4000),
        U("red", "small-medium-uav-series", "usn_ForpostR705", "red_air",
          name="Spotter drone", alt=12000),
        U("neutral", "humpback-whale", "civ_humpback", "whale",
          name="Biologic MIKE"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "fishing",
          name="Banda fishing boat"),
    ],
))

MISSIONS.append(dict(
    group="core", num="05", key="Warramunga's Shot", place="Timor corridor",
    intro="One frigate, one salvo, a target beyond the horizon - and a convoy "
          "behind you that the shot is actually for.",
    date=(2028, 10, 30), time=(14, 10), sea=4, clouds="Overcast", wind="SE",
    difficulty=3, minutes=55, centre=(-9.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR CORRIDOR. A surface action group is working south-west across "
        "the corridor screening an amphibious transport, and it has begun "
        "turning merchant traffic back by radio and then by gun.\\n\\n"
        "You are WARRAMUNGA again, alone, sixty miles on their disengaged bow "
        "with the weather in your favour and a full deck-launcher load. The "
        "convoy you are covering is four hulls and a tug's worth of speed "
        "behind you.\\n\\n"
        "Establish the military threat, engage it, and be somewhere else when "
        "the counter-strike arrives - their maritime strike regiment is "
        "within range of this box and their helicopter is already up. The "
        "merchants in the lane are not targets because somebody wrote "
        "SANCTIONED on a manifest."),
    forces="HMAS Warramunga with NSM and one Seahawk. Opposing: a Sovremenny, "
           "a Type 071 with its Z-20J, a JH-7A pair and a Z-21. Four protected "
           "merchant hulls in the lane behind you.",
    objectives=[
        ("Escort", "Neutralise the armed escort group", "35,-30,Fail,Main"),
        ("Convoy", "The protected merchants must pass", "20,-30,Complete"),
        ("Magazine", "Bring Warramunga out with rounds left", "10,-10,Complete"),
    ],
    victory=dict(kind="destroy", stations=["sag"], min_units=1,
                 objective="Escort"),
    protect=["convoy"], protect_min=2, protect_objective="Convoy",
    neutral_objective="Convoy",
    win="The escort is burning and the transport has turned north. The convoy "
        "passed behind you while it happened, which was the entire point.",
    lose="Warramunga is gone or the lane is closed. Either way nothing moves "
         "through this corridor tomorrow.",
    stations={
        "warramunga": S(-10.0, 131.5, "HMAS Warramunga", heading=310),
        "sag": S(-7.0, 130.0, "Opposing surface group", heading=220),
        "convoy": S(-11.4, 129.6, "Protected convoy", heading=70),
        "red_air": S(-7.2, 132.4, "Maritime strike flight", heading=200,
                     alt=24000),
        "helo": S(-7.1, 130.2, "Shipborne flight", heading=180, alt=3000),
        "air": S(-9.8, 131.4, "Warramunga Flight", heading=320, alt=3000),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "warramunga",
          variant="Variant3", name="HMAS Warramunga"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "air",
          name="Warramunga Flight", alt=3000),
        U("red", "chinese-navy-plan", "plan_em_sovremenny", "sag",
          name="Opposing escort"),
        U("red", "type-071-lpd", "plan_lpd_type_071", "sag",
          name="Amphibious transport"),
        U("red", "type-071-lpd", "planaf_z-20j", "helo", name="Transport flight"),
        U("red", "z-21", "pla_z21", "helo", name="Escort flight", alt=2500),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike flight lead"),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike flight two"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_roro_a", "convoy",
          name="MV Darwin Ranger"),
        U("blue", "re-power-resupply", "civ_ms_freighter_b", "convoy",
          name="MV Sunda Relief"),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy",
          name="MT Timor Spirit"),
    ],
))

MISSIONS.append(dict(
    group="core", num="06", key="Blind Horizon", place="Arafura Sea",
    intro="The destroyer can defend what it can see. Everything past that is "
          "one aircraft, and they are coming for it.",
    date=(2028, 11, 2), time=(7, 0), sea=3, clouds="Scattered_1", wind="NW",
    difficulty=3, minutes=60, centre=(-11.0, 132.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "ARAFURA SEA, first light. HOBART is covering a convoy across the top "
        "of the Gulf and can hold an air picture out to about her own horizon. "
        "The surface group that matters is somewhere north of that line.\\n\\n"
        "SENTRY 06 is your Triton, launched from Tindal, and it is the only "
        "thing that can find them before they are inside missile range. It is "
        "unarmed, it is slow, and a pair of J-16s has come south off the "
        "enclave field on a vector that only makes sense if they know where "
        "the orbit is.\\n\\n"
        "Two Tindal F-35As are your entire air cover. You can spend them "
        "protecting the orbit or holding close escort on the convoy. You "
        "cannot do both, and whatever you lose today you do not have "
        "tomorrow."),
    forces="HMAS Hobart, two RAAF F-35A off Tindal, one MQ-4C Triton, a "
           "Wedgetail on a long orbit. Opposing: two J-16, a Y-20 shuttling "
           "into the enclave, and a surface group not yet located.",
    objectives=[
        ("Convoy", "The convoy reaches its passage window", "30,-30,Fail,Main"),
        ("Sentry", "Keep the Triton flying", "25,-25,Complete"),
        ("Hobart", "Hobart survives", "10,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(-11.9, 130.6), radius=30,
                 min_units=2, objective="Convoy"),
    protect=["isr"], protect_objective="Sentry",
    neutral_objective="Convoy",
    win="The convoy is through the window and Sentry 06 is on its way back to "
        "Tindal with the surface picture. Tomorrow starts with information.",
    lose="The orbit is gone. Everything north of the horizon is now a rumour, "
         "and the convoy is inside somebody's launch basket.",
    stations={
        "hobart": S(-10.5, 132.0, "HMAS Hobart", heading=250),
        "convoy": S(-10.6, 132.1, "Convoy", heading=250),
        "isr": S(-9.0, 132.8, "Sentry orbit", heading=90, alt=50000),
        "cap": S(-10.2, 132.6, "Tindal CAP", heading=10, alt=30000),
        "aew": S(-11.6, 132.2, "Wedgetail orbit", heading=90, alt=32000),
        "tindal": S(-14.5, 132.5, "RAAF Base Tindal", heading=0),
        "red_air": S(-7.2, 133.2, "Enclave fighters", heading=180, alt=34000),
        "red_sag": S(-7.6, 133.6, "Opposing surface group", heading=180),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "hobart",
          name="HMAS Hobart"),
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "isr",
          name="Sentry 06", weapons="Hold"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap",
          squadron="Squadron3", name="Vigilant 21"),
        U("blue", "raaf-f-35a", "raaf_f-35a", "cap", squadron="Squadron3",
          name="Vigilant 22"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 02",
          weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_tindal", "tindal",
          name="RAAF Base Tindal", nation="australia", weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_bulk", "convoy",
          name="MV Gove Trader"),
        U("blue", "re-power-resupply", "civ_ms_freighter_d", "convoy",
          name="MV Sunda Relief"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("red", "j-16-multirole", "plaaf_j16", "red_air", name="Enclave 11"),
        U("red", "j-16-multirole", "plaaf_j16", "red_air", name="Enclave 12"),
        U("red", "y-20-kj-3000", "plaaf_y-20a", "red_air", name="Shuttle 40",
          alt=28000, weapons="Hold"),
        U("red", "chinese-navy-plan", "plan_ddg_luda_typ_051dt", "red_sag",
          name="Opposing escort north"),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_sag",
          name="Opposing escort south"),
    ],
))

MISSIONS.append(dict(
    group="core", num="07", key="Long Way Home", place="Northern air corridor",
    intro="A tanker with everybody's fuel on board, a flight that has none "
          "left, and interceptors that can out-reach all of it.",
    date=(2028, 11, 5), time=(11, 0), sea=2, clouds="Clear", wind="SE",
    difficulty=3, minutes=50, centre=(-7.0, 133.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "HIGH OVER THE BANDA ARC. Weather over the enclave pushed the morning "
        "package forty minutes long and everybody is coming home on somebody "
        "else's fuel. TEXACO 41 is the only tanker in the corridor and three "
        "different flights are booked on it.\\n\\n"
        "The expeditionary detachment supporting the enclave has put two "
        "MiG-31s up out of the northern field, climbing hard, on a vector "
        "toward the tanker track. Their AEW aircraft is behind them and their "
        "own tanker is behind that, which tells you this was planned.\\n\\n"
        "You have a Raptor pair and a Growler with the returning Super "
        "Hornets. The Foxhound is the one aircraft here you cannot chase: it "
        "shoots from above fifty thousand feet at speeds you will not catch, "
        "and a stern chase is fuel you do not have. Break the shot, not the "
        "aircraft. Bring the tanker home."),
    forces="Two F-22 on station, one EA-18G, two returning F/A-18F, one "
           "KC-135. Opposing: two MiG-31BM, one A-50U, one Il-78.",
    objectives=[
        ("Tanker", "TEXACO 41 must reach the recovery line", "35,-35,Fail,Main"),
        ("Package", "Bring the returning flight home", "20,-25,Complete"),
        ("Raptors", "Do not trade the Raptors for the interceptors",
         "10,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="tanker", at=(-9.4, 132.6), radius=35,
                 min_units=1, objective="Tanker"),
    protect=["tanker", "package"], protect_objective="Tanker",
    neutral_objective="Package",
    win="The tanker is south of the line and the package is behind it. Both "
        "Foxhounds turned back with nothing to show a staff officer.",
    lose="The tanker is down. Every sortie in the north tomorrow gets shorter, "
         "and the ones over the enclave do not happen at all.",
    stations={
        "tanker": S(-7.2, 133.0, "Texaco 41", heading=200, alt=26000),
        "package": S(-6.6, 133.2, "Returning package", heading=200, alt=28000),
        "cap": S(-6.9, 133.4, "Raptor pair", heading=20, alt=40000),
        "red_air": S(-4.6, 131.4, "Interceptor pair", heading=170, alt=52000),
        "red_support": S(-4.5, 130.2, "Support orbit", heading=180, alt=30000),
        "picket": S(-7.6, 133.4, "Surface picket", heading=270),
    },
    units=[
        U("blue", "kc-135", "usaf_stratotanker", "tanker", name="Texaco 41",
          weapons="Hold"),
        U("blue", "f-22", "usaf_f-22_s6", "cap", name="Raptor 11"),
        U("blue", "f-22", "usaf_f-22_s6", "cap", name="Raptor 12"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_ea-18g", "package",
          squadron="Squadron6", name="Grizzly 31"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f_blk3", "package",
          squadron="Squadron8", name="Rhino 21"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_fa-18f_blk3", "package",
          squadron="Squadron8", name="Rhino 22"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "picket", variant="Variant8",
          name="HMAS Perth"),
        U("red", "mig-31-foxhound", "wp_mig-31bm", "red_air", name="Foxhound 51"),
        U("red", "mig-31-foxhound", "wp_mig-31bm", "red_air", name="Foxhound 52"),
        U("red", "a-50-il-76", "wp_a-50u", "red_support", name="Mainstay 20",
          weapons="Hold"),
        U("red", "il-78", "wp_il-78", "red_support", name="Midas 30",
          weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="08", key="The Open Door", place="Contested enclave",
    intro="Open a relief window over an airfield somebody else's advisers are "
          "defending. The window is the objective, not the airfield.",
    date=(2028, 11, 8), time=(4, 50), sea=2, clouds="Scattered_1", wind="NE",
    difficulty=4, minutes=70, centre=(-2.0, 136.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "THE ENCLAVE, before dawn. Local authorities have negotiated a "
        "ninety-minute window to move civilians and emergency supplies out of "
        "the port. The battery covering the approach is an S-400 the first "
        "reports called man-portable, and it is not being run by the people "
        "who seized the airfield.\\n\\n"
        "GRIZZLY has the jamming and the anti-radiation shots. The F-35 pair "
        "carries the follow-up. The relief aircraft are behind you and they "
        "will not come in while that radar is up.\\n\\n"
        "Suppress the battery, put the launcher out of the argument, and let "
        "the transports through. You are not levelling a regional industrial "
        "complex to do it. Everything on that field that is not shooting at "
        "you is somebody's town."),
    forces="One EA-18G, two F-35A, two relief transports. Opposing: an S-400 "
           "battery with its Flap Lid, a ballistic launcher, a modern airbase, "
           "and a small foreign detachment with Hinds, Hips and Frogfoots.",
    objectives=[
        ("Window", "Get the relief aircraft through to the south",
         "40,-40,Fail,Main"),
        ("Battery", "Neutralise the surface-to-air battery", "20,-15,Complete"),
        ("Town", "Leave the civilian port standing", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="relief", at=(-4.6, 136.8), radius=30,
                 min_units=1, objective="Window"),
    protect=["relief"], protect_objective="Window",
    neutral_objective="Town",
    win="Both transports are south with the first hundred people out. The "
        "battery is off the air and the window held.",
    lose="The window closed with the transports still holding. The next "
         "negotiation starts from a worse place.",
    stations={
        "strike": S(-2.6, 135.9, "Strike package", heading=10, alt=30000),
        "relief": S(-3.0, 136.2, "Relief flight", heading=170, alt=14000),
        "battery": S(-1.0, 136.0, "S-400 battery", heading=180),
        "field": S(-1.1, 136.2, "Enclave airfield", heading=90),
        "detach": S(-1.2, 136.4, "Foreign detachment", heading=180, alt=4000),
        "port": S(-4.5, 137.0, "Civilian port", heading=0),
        "sea": S(0.5, 135.5, "Offshore picket", heading=180),
    },
    units=[
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_ea-18g", "strike",
          squadron="Squadron6", name="Grizzly 33"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "strike",
          squadron="Squadron3", name="Vigilant 31"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "strike",
          squadron="Squadron3", name="Vigilant 32"),
        U("blue", "us-naval-aviation", "usmc_kc-130j", "relief",
          name="Relief 61", alt=12000, weapons="Hold"),
        U("blue", "us-naval-aviation", "usmc_kc-130j", "relief",
          name="Relief 62", alt=12000, weapons="Hold"),
        U("red", "sa-21-s400", "wp_sam_site_sa-21", "battery",
          name="Enclave battery"),
        U("red", "sa-21-s400", "wp_sa-21_flaplid", "battery",
          name="Battery radar"),
        U("red", "sa-21-s400", "wp_sa-21_40n6_tel", "battery",
          name="Battery launcher"),
        U("red", "pla-land-unit-pack", "pla_df-21c_tel", "field",
          name="Transporter-erector"),
        U("red", "pla-land-unit-pack", "pla_apc_zbl-08", "field",
          name="Field security"),
        U("red", "modern-chinese-airbase", "pla_airbase_modern", "field",
          name="Enclave airfield"),
        U("red", "modern-russian-airbase", "wp_airbase_modern", "field",
          name="Detachment dispersal"),
        U("red", "mi-24", "wp_mi-24p", "detach", name="Hind 21", alt=3000),
        U("red", "mi-8-t-tv", "wp_mi-8tv", "detach", name="Hip 41", alt=2500),
        U("red", "mi-8ew", "wp_mi-8ew", "detach", name="Hip EW 43", alt=5000),
        U("red", "su-25", "wp_su-25sm3", "detach", name="Frogfoot 61", alt=14000),
        U("neutral", "buildings-targets-missions", "Coal_PowerPlant", "port",
          name="Port power station"),
        U("neutral", "buildings-targets-missions", "4tentgroup", "port",
          name="Civilian shelter camp"),
        U("neutral", "_vanilla", "civ_ms_encounter", "sea",
          name="Relief coaster"),
    ],
))

MISSIONS.append(dict(
    group="core", num="09", key="Southern Lifeline", place="Rear support area",
    intro="A submarine on the surface alongside a supply ship, which is the "
          "most vulnerable thing either of them will ever do.",
    date=(2028, 11, 11), time=(6, 30), sea=2, clouds="Broken_2", wind="SE",
    difficulty=3, minutes=65, centre=(-12.5, 146.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "REAR SUPPORT AREA, east of the Cape. COLLINS has been out for "
        "thirty-one days and comes home on Thursday whatever happens today. "
        "She is surfaced alongside SUPPLY taking fuel, stores and two crew off "
        "for medical, and while she is up there she is a very large grey "
        "target moving at eight knots.\\n\\n"
        "The service window is the mission. Nothing transfers while she is "
        "dived, and nothing transfers while the group is manoeuvring hard, so "
        "every minute you spend avoiding something is a minute added to the "
        "end.\\n\\n"
        "A Tu-214R came down the outside of the box last night and did not "
        "come back, which usually means somebody now knows where to look. "
        "There is an Akula unaccounted for and a Flanker pair within range of "
        "here. Keep the window open and get everybody out of it."),
    forces="HMAS Supply, HMAS Collins surfaced for service, HMAS Perth and a "
           "Seahawk. Opposing: one Akula, one Tu-214R, a Flanker pair with a "
           "Ka-27RLD spotting for them.",
    objectives=[
        ("Service", "Hold the service window and withdraw south",
         "35,-35,Fail,Main"),
        ("Collins", "HMAS Collins must survive", "25,-35,Complete"),
        ("Supply", "HMAS Supply must survive", "20,-30,Complete"),
    ],
    # Supply AND Collins, not "any two of the group" - the freighter could
    # otherwise stand in for the submarine the mission is about. The time
    # condition is the service window: withdrawing early does not count.
    victory=dict(kind="arrive", units=["support#1", "support#2"], min_units=2,
                 station="support", objective="Service",
                 also=[dict(after_minutes=35)]),
    protect=["support"], protect_objective="Collins",
    neutral_objective="Service",
    win="The window held, Collins is dived and heading for Stirling, and "
        "Supply still has enough in her tanks to do this again next week.",
    lose="The support group is broken. Every boat in the north now has to come "
         "all the way home to do what should take four hours out here.",
    stations={
        "support": S(-13.5, 148.4, "Support group", heading=200),
        "escort": S(-13.6, 148.6, "Escort", heading=200),
        "air": S(-13.0, 148.2, "Perth Flight", heading=90, alt=3000),
        "cape": S(-12.5, 142.0, "Cape York strip", heading=0),
        "red_sub": S(-16.5, 150.0, "Akula datum", heading=320),
        "red_air": S(-11.0, 148.0, "Opposing aviation", heading=180, alt=30000),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_aor_supply", "support",
          name="HMAS Supply"),
        U("blue", "SEST_RAN_Fleet", "ran_ssg_collins", "support",
          name="HMAS Collins (surfaced)"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant8",
          name="HMAS Perth"),
        U("blue", "re-power-resupply", "civ_ms_amra", "support",
          name="MV Coral Provider"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "air", name="Perth Flight",
          alt=2500),
        U("blue", "buildings-targets-missions", "FOB", "cape",
          name="Cape York forward strip", weapons="Hold"),
        U("red", "russian-submarines", "wp_ssn_akula", "red_sub",
          name="Contact VICTOR"),
        U("red", "tu-214r-family", "msdvd_tu-214r", "red_air",
          name="Coot-A 90", alt=34000, weapons="Hold"),
        U("red", "flanker-family", "wp_su-30m", "red_air", name="Flanker 21"),
        U("red", "flanker-family", "wp_su-30m", "red_air", name="Flanker 22"),
        U("red", "ka-27rld", "wp_ka-27rdl", "red_air", name="Helix RLD 55",
          alt=9000, weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="10", key="Common Sea", place="Eastern Banda corridor",
    intro="A Japanese ASW detachment brings the one thing the Australian "
          "force has run out of: escorts that can hunt.",
    date=(2028, 11, 15), time=(13, 40), sea=3, clouds="Scattered_1", wind="E",
    difficulty=3, minutes=75, centre=(-6.5, 133.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "EASTERN BANDA CORRIDOR. The convoy has to cross a patrol box where "
        "the submarine and surface threats overlap, and after three weeks the "
        "Australian escort force cannot cover both.\\n\\n"
        "MOGAMI and MAYA are here under the Japanese government's own "
        "arrangements, with two SH-60Ks that are the best ASW asset in this "
        "sea. A Japanese F-2A detachment forward at Biak has one sortie "
        "allocation today and will use it on the surface group, not on your "
        "convoy's CAP.\\n\\n"
        "Get the priority cargo to the handover. The Type 039 is the threat "
        "that ends the mission; the fighters overhead are the threat that "
        "makes you spend the day looking up instead of down."),
    forces="JS Mogami and JS Maya with two SH-60K, one F-2A pair from Biak, "
           "HMAS Perth and the convoy. Opposing: a Type 039C, a J-11BG pair, "
           "a J-11BS, a Su-27UBK and a J-10C off the enclave field.",
    objectives=[
        ("Cargo", "The priority convoy reaches the handover point",
         "35,-35,Fail,Main"),
        ("Allies", "Keep the Japanese escorts in the fight", "20,-25,Complete"),
        ("Submarine", "Locate and break off the submarine", "15,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(-8.5, 134.5), radius=30,
                 min_units=2, objective="Cargo"),
    protect=["convoy"], protect_min=2, protect_objective="Cargo",
    neutral_objective="Cargo",
    win="The cargo is at the handover and both Japanese ships are still on "
        "station. The corridor has a second usable escort force for the first "
        "time since October.",
    lose="The convoy is short and the allied detachment is going home for "
         "repairs. The corridor is back to one navy again.",
    stations={
        "jmsdf": S(-7.0, 133.0, "Japanese detachment", heading=160),
        "convoy": S(-6.6, 132.8, "Priority convoy", heading=160),
        "escort": S(-6.8, 133.2, "HMAS Perth", heading=160),
        "helo": S(-7.2, 133.2, "SH-60K pair", heading=180, alt=3000),
        "f2": S(-5.6, 133.0, "Biak detachment", heading=180, alt=26000),
        "red_sub": S(-8.4, 134.4, "Submarine datum", heading=20),
        "red_air": S(-5.4, 133.2, "Enclave fighters", heading=180, alt=32000),
        "kai": S(-7.0, 134.0, "Kai Islands", heading=0),
    },
    units=[
        U("blue", "SEST_JMSDF_Mogami", "js_ffg_mogami", "jmsdf",
          name="JS Mogami"),
        U("blue", "euromod-jmsdf", "jmsdf_ddg_maya", "jmsdf", name="JS Maya"),
        U("blue", "euromod-jmsdf", "jp_sh-60k", "helo", name="Mogami Flight"),
        U("blue", "euromod-jmsdf", "jp_sh-60j", "helo", name="Maya Flight"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant8",
          name="HMAS Perth"),
        U("blue", "f-2a-viper-zero", "jp_f-2a_late", "f2", name="Viper 61"),
        U("blue", "f-2a-viper-zero", "jp_f-2a_late", "f2", name="Viper 62"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_antares", "convoy",
          name="MV Antares"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "re-power-resupply", "civ_ms_freighter_a", "convoy",
          name="MV Sunda Relief"),
        U("red", "plan-submarines", "plan_ss_type_039c", "red_sub",
          name="Contact SIERRA"),
        U("red", "j-11", "plaaf_j-11bg", "red_air", name="Flanker 31"),
        U("red", "j-11bs", "plaaf_j-11bs", "red_air", name="Flanker 32"),
        U("red", "su-27ubk", "plaaf_su-27ubk", "red_air", name="Flanker 33"),
        U("red", "j-10c", "plaaf_j10c", "red_air", name="Dragon 41"),
        U("red", "pla-land-unit-pack", "pla_9k331", "kai",
          name="Island air defence"),
    ],
))

MISSIONS.append(dict(
    group="core", num="11", key="Fujian's Shadow", place="Wider Banda approaches",
    intro="The carrier group has come to close the corridor for the "
          "negotiating period. You do not have to sink it. You have to keep "
          "the transports alive through it.",
    date=(2028, 11, 19), time=(10, 15), sea=4, clouds="Broken_2", wind="NE",
    difficulty=4, minutes=90, centre=(-4.5, 130.0),
    blue_nation="USA", red_nation="China",
    brief=(
        "WIDER BANDA APPROACHES. The ceasefire talks open on Friday and the "
        "opposing fleet has been told to make the corridor unusable before "
        "they do. FUJIAN is three hundred miles north-west with LIAONING "
        "astern of her, and the strike they are building is aimed at the "
        "transports, not at you.\\n\\n"
        "FORD arrived on Tuesday under a bounded arrangement: one strike "
        "group, a defined window, and a departure date that does not move. "
        "You have her air wing, two Burkes and the last of the Australian "
        "escorts.\\n\\n"
        "The protected transports and FORD herself have to come out of this "
        "usable. If their carrier turns north having achieved nothing, that "
        "is the whole victory - you are not chasing it across the Celebes Sea "
        "to prove a point."),
    forces="USS Gerald R. Ford with F-35C and Growlers, two Arleigh Burkes, "
           "HMAS Hobart, three protected transports. Opposing: Fujian with "
           "J-35 and J-15D, Liaoning, a J-20 pair and a KJ-600.",
    objectives=[
        ("Transports", "The transport group must pass to the south-east",
         "40,-40,Fail,Main"),
        ("Ford", "USS Gerald R. Ford survives the window", "30,-40,Complete"),
        ("Strike", "Break up the opposing strike", "15,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="transports", at=(-7.0, 130.0),
                 radius=35, min_units=2, objective="Transports"),
    protect=["carrier"], protect_objective="Ford",
    neutral_objective="Transports",
    win="The transports are through and Ford is intact with her window "
        "unexpired. Their carrier group is heading north-west and the talks "
        "open on Friday with the corridor open.",
    lose="The corridor is closed and the talks open with that as the first "
         "fact on the table.",
    stations={
        "carrier": S(-4.5, 130.0, "Ford strike group", heading=140),
        "escort": S(-4.6, 130.2, "Escort screen", heading=140),
        "transports": S(-5.0, 128.2, "Protected transports", heading=120),
        "cvw": S(-4.2, 130.4, "Carrier air wing", heading=320, alt=28000),
        "red_cv": S(-2.5, 129.0, "Opposing carrier group", heading=140),
        "red_air": S(-2.7, 129.2, "Opposing air wing", heading=150, alt=30000),
    },
    units=[
        U("blue", "ford-cvn", "usn_cvn_ford", "carrier",
          name="USS Gerald R. Ford"),
        U("blue", "modern-us-navy", "usn_ddg_burke_f2a_g4_2022", "escort",
          name="USS Jack H. Lucas"),
        U("blue", "us-navy-2027", "usn_ddg_arleigh_flt3_2027", "escort",
          name="USS Louis H. Wilson Jr."),
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort",
          name="HMAS Hobart"),
        U("blue", "SEST_F-35C_JATM", "usn_f-35c", "cvw", name="Warhawk 101",
          loadout="AirToAirAMRAAM"),
        U("blue", "SEST_F-35C_JATM", "usn_f-35c", "cvw", name="Warhawk 102",
          loadout="AirToAirAMRAAM"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_ea-18g_2020", "cvw",
          name="Grizzly 35"),
        U("blue", "us-naval-aviation", "usn_e-2d", "cvw", name="Hawkeye 601",
          alt=27000, weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_super_p", "transports",
          name="MV Torres Trader"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "transports",
          name="MV Coral Pioneer"),
        U("blue", "re-power-resupply", "civ_ms_andizhan", "transports",
          name="MV Lae Provider"),
        U("red", "fujian-cv-18", "plan_cv_type_003", "red_cv", name="PLANS Fujian"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv",
          name="PLANS Liaoning"),
        U("red", "modern-plan-systems", "plan_type_055_2026", "red_cv",
          name="Type 055 escort"),
        U("red", "modern-plan-systems", "plan_type_052d_p3", "red_cv",
          name="Type 052D escort"),
        U("red", "fujian-cv-18", "plan_j-35", "red_air", name="Falcon 11"),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 21"),
        U("red", "type-003-004-maneuverwarfare", "pla_kj-600", "red_air",
          name="KJ-600 Eye", alt=26000, weapons="Hold"),
        U("red", "j-20", "plaaf_j-20a", "red_air", name="Dragon 51"),
    ],
))

MISSIONS.append(dict(
    group="core", num="12", key="The First Ship Through", place="Arafura Sea",
    intro="An imperfect ceasefire, a cargo ship with a cracked bearing, and "
          "two groups out there - one complying and one deciding.",
    date=(2028, 11, 26), time=(6, 20), sea=2, clouds="Scattered_1", wind="NW",
    difficulty=3, minutes=65, centre=(-10.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "ARAFURA SEA. The ceasefire came into effect at midnight and traffic "
        "started moving at first light because insurers move faster than "
        "diplomats. CORAL PIONEER is at the head of the first convoy through, "
        "with a bearing running hot and eleven knots on a good hour.\\n\\n"
        "There are two groups in the box. One has acknowledged its withdrawal "
        "order and is heading north at steady speed. The other has not "
        "acknowledged anything since 0400 and has a maritime strike flight "
        "within range.\\n\\n"
        "Tell them apart. Get the convoy home. Do not be the incident that "
        "restarts this - a withdrawing ship you sink today is the reason "
        "there is no ceasefire on Monday."),
    forces="HMAS Warramunga, HMAS Perth, HMAS Arafura and a Poseidon, with "
           "four merchant hulls. Two opposing groups: one withdrawing, one "
           "not. A Wedgetail is up.",
    objectives=[
        ("Convoy", "Bring the convoy into Darwin's approaches",
         "40,-40,Fail,Main"),
        ("Ceasefire", "Do not fire on the withdrawing group", "20,-35,Complete"),
        ("Escorts", "Bring the escorts home", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(-12.0, 130.5), radius=30,
                 min_units=3, objective="Convoy"),
    protect=["convoy"], protect_min=2, protect_objective="Convoy",
    neutral_objective="Ceasefire",
    win="Coral Pioneer is alongside at Darwin on one shaft and the rest of the "
        "convoy is behind her. The withdrawing group went north and nobody "
        "shot at it. The route is a route again.",
    lose="The first ship through did not get through, and the ceasefire is "
         "now a thing that was tried once.",
    stations={
        "escort": S(-10.1, 131.4, "Escort group", heading=200),
        "convoy": S(-10.4, 131.8, "First convoy", heading=200),
        "air": S(-10.8, 131.0, "Air support", heading=200, alt=20000),
        "aew": S(-11.5, 130.8, "Wedgetail orbit", heading=90, alt=32000),
        "withdraw": S(-7.0, 130.0, "Withdrawing group", heading=340),
        "spoiler": S(-7.2, 132.4, "Unacknowledged group", heading=180),
        "spoiler_air": S(-7.4, 132.6, "Strike flight", heading=180, alt=24000),
        "darwin": S(-12.4, 130.9, "Darwin", heading=0),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant3",
          name="HMAS Warramunga", weapons="Tight"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant8",
          name="HMAS Perth", weapons="Tight"),
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "escort",
          name="HMAS Arafura", weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "air", squadron="Squadron3",
          name="Bluefin 27", alt=18000, weapons="Tight"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 03",
          weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "darwin",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_jeparit", "convoy",
          name="MV Jeparit"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "convoy",
          name="MV Gove Trader"),
        U("blue", "re-power-resupply", "civ_ms_freighter_b", "convoy",
          name="MV Sunda Relief"),
        U("neutral", "chinese-navy-plan", "plan_ddg_luda_typ_051d", "withdraw",
          name="Withdrawing escort"),
        U("neutral", "type-071-lpd", "plan_lpd_type_071", "withdraw",
          name="Withdrawing transport"),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "spoiler",
          name="Unacknowledged escort"),
        U("red", "chinese-navy-plan", "plan_ss_kilo", "spoiler",
          name="Unacknowledged submarine"),
        U("red", "jh-7a", "plaaf_jh7a", "spoiler_air", name="Strike flight 71"),
    ],
))

# =============================================================================
# DISPATCHES - optional episodes. They sit outside the twelve-mission spine
# and give the rest of the collection a purposeful role instead of forcing a
# Spanish frigate or a 1988 bomber into an Australian 2028 convoy escort.
# =============================================================================

MISSIONS.append(dict(
    group="dispatch", num="D1", key="Western Passage",
    place="Timor Sea, western approach",
    intro="Allied Dispatch. A European escort rotation brings the replenishment "
          "group in from the west.",
    date=(2028, 11, 6), time=(8, 30), sea=4, clouds="Broken_2", wind="SW",
    difficulty=3, minutes=70, centre=(-12.5, 125.5),
    blue_nation="Europe", red_nation="Russia",
    brief=(
        "WESTERN APPROACH. The corridor runs on fuel that arrives from outside "
        "it, and the replenishment group coming up from the Indian Ocean is "
        "the reason anything in the Banda still has range.\\n\\n"
        "The escort is a European rotation: a Type 45 with its Merlin, a "
        "German F124, a Dutch De Zeven Provincien, a Danish Iver Huitfeldt, an "
        "Italian FREMM and an older Type 23 that was already east when this "
        "started. Typhoons out of Butterworth hold the air, with a Swedish "
        "AEW aircraft lent for the transit.\\n\\n"
        "The expeditionary detachment has put a MiG-35 pair and a Su-24 up "
        "along the northern edge. They are here to find the oiler, not to "
        "fight your escorts. Do not let them do either."),
    forces="Type 45, F124, De Zeven Provincien, Iver Huitfeldt, FREMM, Type 23, "
           "Merlin, NH90, Wildcat, Sea Lynx and an S-70B-2 across the group. "
           "Two Typhoons and a Saab AEW&C overhead. Opposing: MiG-35 pair and "
           "a Su-24MP.",
    objectives=[
        ("Oiler", "The replenishment group reaches the eastern box",
         "35,-35,Fail,Main"),
        ("Escorts", "Keep the escort rotation intact", "20,-25,Complete"),
        ("Shadow", "Deny the shadowers a targeting solution", "15,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="group", at=(-11.6, 129.4), radius=35,
                 min_units=2, objective="Oiler"),
    protect=["group"], protect_objective="Oiler",
    neutral_objective="Oiler",
    win="The group is in the eastern box and every escort in the rotation is "
        "still answering. The corridor has fuel for another fortnight.",
    lose="The oiler is gone. Everything east of here now plans around a tank "
         "that does not refill.",
    stations={
        "group": S(-12.0, 124.6, "Replenishment group", heading=80),
        "escort": S(-12.2, 124.9, "Escort rotation", heading=80),
        "helo": S(-12.1, 125.1, "Escort flights", heading=80, alt=3000),
        "cap": S(-12.6, 125.4, "Typhoon pair", heading=20, alt=33000),
        "aew": S(-13.0, 125.2, "AEW orbit", heading=90, alt=30000),
        "red_air": S(-10.5, 125.0, "Shadowers", heading=200, alt=28000),
    },
    units=[
        U("blue", "euromod-british", "rn_ddg_type45", "escort",
          name="HMS Duncan"),
        U("blue", "euromod-german", "ger_ffg_f124", "escort",
          name="FGS Sachsen"),
        U("blue", "euromod-dutch", "rnn_ffg_karel_mlu", "escort",
          name="HNLMS Van Speijk"),
        U("blue", "euromod-nordic", "hdms_iver_huitfeldt", "escort",
          name="HDMS Iver Huitfeldt"),
        U("blue", "euromod-italian-modern", "ita_ffg_fremm_asw", "escort",
          name="ITS Carabiniere"),
        U("blue", "rn-type23-old", "rn_type23_refit", "escort",
          name="HMS Richmond"),
        U("blue", "euromod-british", "rn_merlin_hm2", "helo", name="Duncan Flight"),
        U("blue", "rn-lynx-has3-old", "rn_wildcat", "helo",
          name="Richmond Flight"),
        U("blue", "sea-lynx", "fr_sea_lynx", "helo", name="Rotation Flight"),
        U("blue", "s-70b-2-seahawk", "S-70B-2_Seahawk", "helo",
          name="Group Flight"),
        U("blue", "eurofighter-typhoon", "raf_ef2000_fgr4_late", "cap",
          name="Typhoon 11"),
        U("blue", "eurofighter-typhoon", "raf_ef2000_fgr4_late", "cap",
          name="Typhoon 12"),
        U("blue", "saab-aewc-pack", "dts_saab_ge", "aew", name="Argus 70",
          weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_sealift_pacific", "group",
          name="MT Western Provider"),
        U("blue", "_vanilla", "civ_ms_ritina", "group",
          name="MT Passage Trader"),
        U("red", "mig-35", "wp_mig-35", "red_air", name="Fulcrum-F 21"),
        U("red", "mig-35", "wp_mig-35", "red_air", name="Fulcrum-F 22"),
        U("red", "more-su-24m-variants", "wp_su-24mp", "red_air",
          name="Fencer recon", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D2", key="Flight Deck Day", place="Coral Sea",
    intro="Allied Dispatch. A recovery cycle, a deck that has to keep working, "
          "and nobody shooting at anybody if the day goes well.",
    date=(2028, 11, 13), time=(15, 0), sea=3, clouds="Scattered_1", wind="SE",
    difficulty=1, minutes=55, centre=(-15.5, 149.5),
    blue_nation="USA", red_nation="Russia",
    brief=(
        "CORAL SEA. Two carriers are working the same box: one recovering a "
        "long-range package, one running deck drills with a new air department. "
        "A Seawolf is riding shotgun below and an E-3G is holding the wider "
        "picture while the Wedgetail is off task.\\n\\n"
        "The tanker is the schedule. Everything airborne today is planned "
        "around one KC-10, and the Reaper on the southern track is watching a "
        "merchant that has been drifting off its filed route for two days.\\n\\n"
        "There is a distinguished-visitor lift inbound - a VH-3D bringing the "
        "coalition maritime commander across for the afternoon. That airframe "
        "gets deck priority over everything else that is not on fire. Keep the "
        "cycle running and get the visitor aboard."),
    forces="USS Nimitz and the 2000s-era Nimitz air-deck group, one Seawolf, "
           "an E-3G, a KC-10A, an MQ-9A on the southern track and a VH-3D on "
           "the visit.",
    objectives=[
        ("Visit", "Get the VH-3D into the carrier box", "25,-20,Fail,Main"),
        ("Cycle", "Keep both carriers operating", "20,-25,Complete"),
        ("Tanker", "Do not lose the tanker", "10,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="visit", at=(-15.6, 149.6), radius=15,
                 min_units=1, objective="Visit"),
    protect=["carriers"], protect_objective="Cycle",
    neutral_objective="Cycle",
    win="The visitor is aboard, the package is down and the deck cycle never "
        "broke. A quiet day, which is the point of the exercise.",
    lose="The cycle broke. Somebody will write a report about the afternoon "
         "the carriers stopped flying.",
    stations={
        "carriers": S(-16.4, 150.0, "Carrier box", heading=140),
        "screen": S(-16.5, 149.8, "Screen", heading=140),
        "visit": S(-13.6, 148.5, "VIP lift", heading=180, alt=2000),
        "air": S(-15.0, 149.4, "Support aircraft", heading=90, alt=28000),
        "sub": S(-16.6, 150.2, "Seawolf station", heading=140),
        "track": S(-13.5, 148.6, "Southern track", heading=200, alt=22000),
    },
    units=[
        U("blue", "flight-deck-ops", "usn_cvn_nimitz", "carriers",
          name="USS Nimitz"),
        U("blue", "ado-nimitz-2000s", "usn_cvn_nimitz_2000s_adou", "carriers",
          name="USS Carl Vinson"),
        U("blue", "murder-hornet", "usn_cvn_nimitz_2000s", "carriers",
          name="USS Theodore Roosevelt"),
        U("blue", "us-submarines", "usn_ssn_seawolf", "sub", name="USS Seawolf"),
        U("blue", "e-3g", "usaf_e-3g", "air", name="Sentry 40", weapons="Hold"),
        U("blue", "kc-10a", "usaf_kc-10a_extender", "air", name="Texaco 60",
          weapons="Hold"),
        U("blue", "mq-9-reaper", "usaf_mq-9a", "track", name="Reaper 12",
          weapons="Tight"),
        U("blue", "vh-3d-marine-one", "usmc_vh-3d", "visit", name="Nighthawk 1",
          weapons="Hold"),
        U("neutral", "_vanilla", "civ_ms_roro_c", "track",
          name="MV drifting contact", snap="sea"),
        U("neutral", "merchants-expanded", "civ_ms_mairangi_bay", "track",
          name="MV Coral Pioneer", snap="sea"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D3", key="The Relief Ship", place="Halmahera Sea",
    intro="Allied Dispatch. A French group lands relief into a port the "
          "fighting went round rather than through.",
    date=(2028, 11, 17), time=(7, 45), sea=2, clouds="Broken_2", wind="NE",
    difficulty=2, minutes=60, centre=(0.0, 127.2),
    blue_nation="France", red_nation="China",
    brief=(
        "HALMAHERA. The port never changed hands but the roads to it did, and "
        "twelve thousand people have been on emergency rations since the "
        "second week of the crisis. The coastal authority has asked France "
        "and Spain to land relief, and the arrangement is narrow: this beach, "
        "this window, these vehicles.\\n\\n"
        "CHARLES DE GAULLE is offshore with a Horizon destroyer and Rafales "
        "overhead. The lift is Panthers and Spanish Harriers covering the "
        "approach road, with an armoured column going ashore to hold the "
        "distribution point rather than to take anything.\\n\\n"
        "Nothing here is a target unless it shoots first. The people you are "
        "feeding will be living with whoever runs this town next month."),
    forces="Charles de Gaulle, a Horizon destroyer, Rafale M, Panther and "
           "Cougar helicopters, a VAB column ashore, Spanish AV-8B and AB-212.",
    objectives=[
        ("Relief", "Get the relief column to the distribution point",
         "35,-35,Fail,Main"),
        ("Town", "Leave the port and its people alone", "0,-35,Complete"),
        ("Group", "Bring the amphibious group out", "15,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="lift", at=(-0.5, 128.0), radius=25,
                 min_units=1, objective="Relief"),
    protect=["group"], protect_objective="Group",
    neutral_objective="Town",
    win="The distribution point is open and the column is ashore without a "
        "shot fired in the town. The coastal authority says so publicly, which "
        "matters more than the tonnage.",
    lose="The relief did not land. The next request for help goes to somebody "
         "else.",
    stations={
        "group": S(1.0, 126.5, "French group", heading=100),
        "lift": S(0.4, 127.0, "Relief lift", heading=110, alt=2000),
        "cap": S(0.6, 126.8, "Rafale pair", heading=90, alt=28000),
        "shore": S(-0.5, 128.0, "Distribution point", heading=0),
        "harrier": S(0.2, 127.4, "Spanish detachment", heading=120, alt=15000),
    },
    units=[
        U("blue", "cdg-modern-french-navy", "fr_cvn_charles-de-gaulle", "group",
          name="FS Charles de Gaulle"),
        U("blue", "cdg-modern-french-navy", "fr_ddg_horizon", "group",
          name="FS Forbin"),
        U("blue", "rafale", "fr_rafale_m", "cap", name="Rafale 11"),
        U("blue", "rafale", "fr_rafale_m", "cap", name="Rafale 12"),
        U("blue", "french-helicopter-package", "fr_as-565_sa", "lift",
          name="Panther 21"),
        U("blue", "french-helicopter-package", "fr_as_332M", "lift",
          name="Cougar 22"),
        U("blue", "euromod-spanish-modern", "spa_av-8b_plus", "harrier",
          name="Harrier 31"),
        U("blue", "euromod-spanish-cold-war", "spa_ab212", "harrier",
          name="Spanish Flight", alt=2500),
        U("blue", "french-army-vehicles", "fr_apc_vab_top", "shore",
          name="Relief column lead"),
        U("blue", "french-army-vehicles", "fr_apc_griffon", "shore",
          name="Relief column two"),
        U("neutral", "buildings-targets-missions", "4tentgroup", "shore",
          name="Distribution point"),
        U("blue", "_vanilla", "civ_ms_encounter", "group",
          name="MV Halmahera coaster"),
        U("red", "pla-land-unit-pack", "pla_apc_zbl-08", "shore",
          name="Roadblock detachment"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D4", key="Return Passage", place="Banda Sea",
    intro="Red Line. You are the other side, bringing a damaged auxiliary "
          "home through somebody else's corridor.",
    date=(2028, 11, 21), time=(3, 10), sea=4, clouds="Overcast", wind="NW",
    difficulty=4, minutes=75, centre=(-5.0, 130.0),
    blue_nation="Russia", red_nation="Australia",
    brief=(
        "BANDA SEA, first watch. The auxiliary took a torpedo forward eleven "
        "days ago and has been making six knots ever since. She carries the "
        "detachment's remaining missile stocks and the only workshop between "
        "here and home.\\n\\n"
        "You have the heavy cruiser, a Project 11356 frigate, a Felon pair off "
        "the dispersal field and a Chinese J-16D lent for the passage. Your "
        "bombers can reach but they cannot loiter, and every sortie you fly "
        "tells the other side where you are going.\\n\\n"
        "Get her south-east past the corridor. This is not a raid. If you "
        "start a fleet action to protect a workshop ship you will lose both."),
    forces="Pyotr Velikiy, a Project 11356 frigate, Su-57 pair, Su-30SM2, "
           "MiG-29K, a Tu-160 and a Tu-95MS on call. One damaged auxiliary.",
    objectives=[
        ("Auxiliary", "Bring the auxiliary through to the south-east",
         "40,-40,Fail,Main"),
        ("Cruiser", "Do not lose the heavy cruiser", "20,-30,Complete"),
        ("Restraint", "Avoid a fleet action you cannot finish",
         "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="auxiliary", at=(-7.0, 132.5),
                 radius=35, min_units=1, objective="Auxiliary"),
    protect=["auxiliary"], protect_objective="Auxiliary",
    neutral_objective="Restraint",
    win="She is past the corridor and making for home at six knots with the "
        "stocks intact. Nobody on either side had to explain a fleet action "
        "to a government this week.",
    lose="The auxiliary is on the bottom with the detachment's magazines in "
         "her. Whatever is left ashore now fights with what it is holding.",
    stations={
        "auxiliary": S(-4.6, 130.1, "Damaged auxiliary", heading=130),
        "escort": S(-4.5, 130.3, "Escort", heading=130),
        "cap": S(-4.3, 130.5, "Felon pair", heading=140, alt=36000),
        "bomber": S(-2.6, 129.0, "Bomber track", heading=160, alt=34000),
        "red_sag": S(-5.2, 128.2, "Coalition patrol", heading=60),
        "red_air": S(-5.4, 128.4, "Coalition CAP", heading=60, alt=30000),
    },
    units=[
        U("blue", "_vanilla", "civ_ms_kommunist", "auxiliary",
          name="Damaged auxiliary"),
        U("blue", "kirov-pyotr-velikiy", "wp_rkr_kirov_improved", "escort",
          name="Pyotr Velikiy"),
        U("blue", "russian-navy-21", "rfn_ffg_11356", "escort",
          name="Admiral Grigorovich"),
        U("blue", "su-57", "wp_su-57", "cap", name="Felon 11"),
        U("blue", "su-30sm2", "wp_su-30sm2", "cap", name="Flanker-H 12"),
        U("blue", "mig-29-family", "wp_mig-29k", "cap", name="Fulcrum-D 13"),
        U("blue", "j-16a", "plaf_j16d", "cap", name="Lent escort"),
        U("blue", "tu-160", "wp_tu-160", "bomber", name="Blackjack 01",
          weapons="Tight"),
        U("blue", "tu-95ms-x-101", "wp_tu-95ms_x101", "bomber", name="Bear 02",
          weapons="Tight"),
        U("blue", "tu-95-as-15", "wp_tu-95ms", "bomber", name="Bear 03",
          weapons="Tight"),
        U("blue", "kuznetsov-1143-5", "ru_cv_kuznetsov", "escort",
          name="Carrier, covering group"),
        U("blue", "kuznetsov-1143-5", "wp_su-33", "cap", name="Flanker-D 14"),
        U("red", "SEST_RAN_Fleet", "ran_ddg_hobart", "red_sag",
          name="HMAS Hobart"),
        U("red", "SEST_RAN_Fleet", "ran_ffh_anzac", "red_sag", variant="Variant8",
          name="HMAS Perth"),
        U("red", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "red_air",
          squadron="Squadron3", name="Vigilant 41"),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          name="Bluefin 29"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D5", key="Range Week", place="Northern Territory ranges",
    intro="Range Week. A live counter-launcher serial against the range's own "
          "threat pads, plus an anti-ship shot at the seaward target.",
    date=(2028, 11, 9), time=(9, 0), sea=1, clouds="Clear", wind="SE",
    difficulty=2, minutes=60, centre=(-13.5, 131.5),
    blue_nation="Australia", red_nation="Iran",
    brief=(
        "NORTHERN TERRITORY RANGES. This is a trial, not a battle. The "
        "coalition has brought its layered-defence systems to Delamere for a "
        "fortnight of live shots, and the threat side of the range is run by "
        "the trials unit with captured and purchased launchers.\\n\\n"
        "Today's serial is the hard one: a THAAD battery and a David's Sling "
        "pair engaging a mixed ballistic and cruise raid launched from the "
        "range's own northern pads. A Japanese Type 12 battery is firing a "
        "separate anti-ship serial at the seaward target, and an ARRW round is "
        "being flown out of the range field.\\n\\n"
        "Everything red here belongs to the range. Nothing ashore is "
        "somebody's country. Score the intercepts and do not put a round "
        "outside the danger area."),
    forces="THAAD with AN/TPY-2, a David's Sling battery, a Type 12 SSM "
           "battery, an ARRW-capable range field and an A-10A target tow. "
           "Range threat pads: Scud-B, Sejjil, Iskander and a Shahed line.",
    objectives=[
        # The trigger destroys launchers, so the objective says destroy
        # launchers. It used to promise intercepted rounds and score destroyed
        # pads, which is two different exercises.
        ("Pads", "Destroy three of the four range threat pads",
         "35,-25,Fail,Main"),
        ("Serial", "Put the anti-ship serial into the seaward target",
         "15,-10,Complete"),
        ("Safety", "Hit nothing outside the danger area", "0,-30,Complete"),
    ],
    victory=dict(kind="destroy", stations=["pads"], min_units=3,
                 objective="Pads"),
    protect=["battery"], protect_objective="Pads",
    neutral_objective="Safety",
    win="Three of four pads down, the anti-ship serial into the target and the "
        "trials staff already arguing about the fourth. Good week.",
    lose="The serial is a write-off and the trials report will say so at "
         "length.",
    stations={
        "battery": S(-12.5, 131.0, "Defence batteries", heading=0),
        "pads": S(-14.5, 132.5, "Range threat pads", heading=180),
        "coastal": S(-12.4, 131.2, "Type 12 battery", heading=300),
        "field": S(-12.6, 131.1, "Range field", heading=90),
        "tow": S(-13.0, 131.4, "Target tow", heading=180, alt=18000),
        "target": S(-12.0, 130.5, "Seaward target", heading=270),
        "safety": S(-11.5, 129.6, "Range safety area", heading=90, alt=31000),
    },
    units=[
        U("blue", "thaad", "thaad_tel", "battery", name="THAAD launcher"),
        U("blue", "thaad", "wp_an_tpy_2", "battery", name="AN/TPY-2"),
        U("blue", "davids-sling", "idf_dsws", "battery",
          name="David's Sling launcher"),
        U("blue", "davids-sling", "idf_dsws_radar", "battery",
          name="David's Sling radar"),
        U("blue", "type-12-ssm", "jp_12ssmht", "coastal",
          name="Type 12 battery"),
        U("blue", "arrw", "nato_large_pvo_airbase1", "field",
          name="Range field", weapons="Hold"),
        U("blue", "apex-predators-mig-29-f-16", "airfield_us", "field",
          name="Range support strip", weapons="Hold"),
        U("blue", "a-10a", "usa_a-10a", "tow", name="Target tow 01",
          weapons="Hold"),
        U("blue", "apex-predators-mig-29-f-16", "usaf_f-16a", "tow",
          name="Chase 02", weapons="Hold"),
        U("red", "scud-b", "wp_scud_9k72", "pads", name="Range pad SCUD"),
        U("red", "sejjil-iran-bm", "wp_sejjil_tel", "pads",
          name="Range pad SEJJIL"),
        U("red", "iskander-tbm", "wp_ss-26_tel", "pads",
          name="Range pad ISKANDER"),
        U("red", "shahed-136-zero-two", "shahed_tel_white", "pads",
          name="Range pad DRONE"),
        # The range's own target hulk. Excluded from the neutral-loss rule:
        # shooting it is the serial, not a civilian casualty.
        U("neutral", "_vanilla", "civ_ms_roro_b", "target",
          name="Range seaward target (AUTHORISED)", snap="sea",
          no_neutral_penalty=True),
        # Range safety craft outside the danger area. Without a contact the
        # safety objective can fail on, "hit nothing outside the danger area"
        # is a line of text and nothing else.
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "safety",
          name="Range safety boat"),
        U("neutral", "civil-aircraft-airbus", "civ_a330", "safety",
          name="Darwin-Singapore service", snap="sea"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D6", key="Long Reach", place="Banda Sea, 2034",
    intro="Future Front. Openly speculative: production YF-23s, a tailless "
          "J-36, the J-50, the RQ-180 and every custom missile fit in the "
          "collection, six years after the campaign ends.",
    date=(2034, 3, 14), time=(1, 20), sea=3, clouds="Broken_2", wind="NE",
    difficulty=5, minutes=80, centre=(-4.0, 130.5),
    blue_nation="USA", red_nation="China",
    brief=(
        "BANDA SEA, 2034. None of this is real and none of it is a forecast. "
        "The YF-23 went into production in this timeline, the AIM-260 and the "
        "AIM-424 exist in quantity, the Rafale F5 carries LRASM and the J-36 "
        "and J-50 are operational squadrons rather than airframes on a taxiway.\\n\\n"
        "A bomber stream is going north-west against a relocatable launcher "
        "complex with the RQ-180 ahead of it, and the opposing force has put "
        "up everything it does not officially have.\\n\\n"
        "Treat the weapons performance here as authored fiction. It is the "
        "branch where the collection's experimental content gets to be the "
        "point instead of an embarrassing exception in a 2028 briefing."),
    forces="Two YF-23, one F-15EX, an F-16CM with JATM, a Rafale F5, the "
           "RQ-180, a B-52O, a B-1B and a B-52H in the stream. Opposing: J-36, "
           "J-50, a Tu-95MA with Meteorit and a relocatable launcher complex.",
    objectives=[
        ("Stream", "Get the bomber stream through to release",
         "40,-35,Fail,Main"),
        ("Escort", "Keep the escort fighters alive", "20,-20,Complete"),
        ("Sensor", "Keep the RQ-180 on task", "15,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="stream", at=(-1.2, 131.6), radius=40,
                 min_units=2, objective="Stream"),
    protect=["stream"], protect_objective="Stream",
    neutral_objective="Escort",
    win="The stream released on the complex and the escorts came home. In this "
        "timeline the aircraft that were cancelled in ours got to matter.",
    lose="The stream broke up short of release. Even in fiction, range is "
         "range.",
    stations={
        "stream": S(-4.4, 130.1, "Bomber stream", heading=330, alt=38000),
        "escort": S(-4.2, 130.4, "Escort", heading=330, alt=40000),
        "sensor": S(-3.2, 130.8, "RQ-180 track", heading=320, alt=60000),
        "red_air": S(-2.4, 129.1, "Opposing fighters", heading=150, alt=42000),
        "red_bomber": S(-2.6, 129.3, "Opposing bomber", heading=150, alt=36000),
        "complex": S(-1.0, 131.5, "Launcher complex", heading=180),
        "sea": S(-4.6, 131.5, "Offshore picket", heading=270),
    },
    units=[
        U("blue", "yf-23-black-widow-ii", "usaf_yf-23_black_widow_ii", "escort",
          name="Black Widow 11"),
        U("blue", "yf-23-black-widow-ii", "usaf_yf-23_black_widow_ii", "escort",
          name="Black Widow 12"),
        U("blue", "f-15ex", "usaf_f-15ex_SEII", "escort", name="Eagle II 21"),
        U("blue", "SEST_F16CM_JATM", "usaf_f-16cm-bl52d", "escort",
          name="Viper 31"),
        U("blue", "SEST_Rafale_F5", "fr_rafale_m_l", "escort", name="Rafale 41"),
        U("blue", "rq-180-white-bat", "usaf_rq-180", "sensor",
          name="White Bat 01", weapons="Hold"),
        U("blue", "SEST_B52_ARRW", "usaf_b-52o", "stream", name="Stream 01"),
        U("blue", "b-1b", "usaf_b-1b_dts", "stream", name="Stream 02"),
        U("blue", "b-52h", "dts_b-52h", "stream", name="Stream 03"),
        U("red", "j-36-tailless", "plaaf_j36", "red_air", name="Tailless 51"),
        U("red", "j-50", "plan_j-50", "red_air", name="Silent 52"),
        U("red", "3m25-meteorit", "wp_tu-95ma", "red_bomber", name="Meteorit 90"),
        U("red", "pla-land-unit-pack", "pla_df-26b_tel", "complex",
          name="Relocatable launcher"),
        U("red", "pla-land-unit-pack", "pla_h-200a_radar", "complex",
          name="Complex radar"),
        U("red", "type-003-004-maneuverwarfare", "plan_cvn_004", "sea",
          name="Type 004 picket"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D7", key="Before the Lifeline",
    place="Darwin approaches, 1988",
    intro="Cold Sea. A 1988 exercise in the same water, forty years before the "
          "campaign - the collection's retired aircraft where they belong.",
    date=(1988, 7, 12), time=(5, 55), sea=3, clouds="Scattered_1", wind="SE",
    difficulty=3, minutes=60, centre=(-11.0, 130.2),
    blue_nation="USA", red_nation="Russia",
    brief=(
        "DARWIN APPROACHES, July 1988. Exercise PITCH BLACK's maritime phase, "
        "with an American carrier group south of the Arafura and a mixed "
        "aggressor force flying the other side's profiles.\\n\\n"
        "A Bear G is running the maritime strike serial with a Badger tanker "
        "behind it, a Dragon Lady is high over the exercise box, and the "
        "Nighthawk detachment is flying its first Southern Hemisphere sortie "
        "with the F-8s of the aggressor squadron as its problem.\\n\\n"
        "This is an exercise. It is also the only place in this collection "
        "where a Tomcat, an F-117, a Tornado and a Bear G share a sky without "
        "somebody having to invent a reason."),
    forces="F-14A and F-117 detachments, a B-52G, a U-2, an Italian Tornado "
           "detachment on exchange. Aggressors: J-8, Tu-16N, Tu-95 Bear G.",
    objectives=[
        ("Serial", "Defeat the maritime strike serial", "35,-25,Fail,Main"),
        ("Recovery", "Recover the exercise aircraft", "15,-15,Complete"),
        ("Umpire", "Stay inside the exercise rules", "0,-20,Complete"),
    ],
    victory=dict(kind="destroy", stations=["aggressor"], min_units=2,
                 objective="Serial"),
    protect=["high"], protect_objective="Recovery",
    neutral_objective="Umpire",
    win="The strike serial was broken outside its release line and everybody "
        "recovered. The debrief will still take four hours.",
    lose="The serial got through. Somebody's squadron is buying the drinks and "
         "writing the report.",
    stations={
        "cap": S(-11.4, 129.6, "Exercise CAP", heading=20, alt=28000),
        "strike": S(-11.6, 129.9, "Strike detachment", heading=20, alt=24000),
        "high": S(-12.0, 130.5, "High assets", heading=90, alt=60000),
        "aggressor": S(-8.8, 129.2, "Aggressor force", heading=180, alt=30000),
        "sea": S(-12.1, 130.7, "Exercise surface group", heading=270),
        "range": S(-12.5, 131.0, "Exercise field", heading=0),
    },
    units=[
        U("blue", "_vanilla", "usn_f-14a", "cap", name="Tomcat 101"),
        U("blue", "_vanilla", "usn_f-14a", "cap", name="Tomcat 102"),
        U("blue", "f-117", "usaf_f-117", "strike", name="Nighthawk 11"),
        U("blue", "italian-navy-cold-war", "am_tornado_ids", "strike",
          name="Tornado 21"),
        U("blue", "b-52g-agm-86", "usaf_b-52g", "strike", name="Buff 31",
          weapons="Tight"),
        U("blue", "u-2", "usaf_u-2_1960", "high", name="Dragon 41",
          weapons="Hold"),
        U("blue", "flight-deck-ops", "usn_cv_kitty_hawk", "sea",
          name="USS Kitty Hawk"),
        U("blue", "a-10a", "airfield_a-10", "range", name="Exercise field",
          weapons="Hold"),
        U("red", "tu-95k-22", "wp_tu-95_bearg", "aggressor", name="Bear G 90"),
        U("red", "tu-16n", "wp_tu-16n", "aggressor", name="Badger tanker",
          weapons="Hold"),
        U("red", "j-8", "plaaf_j-8f", "aggressor", name="Aggressor 51"),
        U("red", "j-8", "plaaf_j-8f", "aggressor", name="Aggressor 52"),
        # The Custom Loadout Editor's own files are its ammunition and its
        # authoring UI; its patches/ folder is not a path the game loads. The
        # aggressor Flogger's air-to-air fit hangs its rounds, which is the
        # only way a mission can make the game read it.
        U("red", "custom-loadout-editor", "wp_mig-23a", "aggressor",
          name="Aggressor 53"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D8", key="The Long Perimeter", place="Southern Papua",
    intro="Allied Dispatch. A US ground-support package holds the relief "
          "perimeter open after the enclave window closes.",
    date=(2028, 11, 12), time=(17, 30), sea=2, clouds="Broken_2", wind="E",
    difficulty=3, minutes=65, centre=(-7.5, 138.5),
    blue_nation="USA", red_nation="China",
    brief=(
        "SOUTHERN PAPUA, last light. The relief corridor out of the enclave "
        "runs overland now, and the column has stopped twice today because the "
        "road is covered from a ridge nobody has cleared.\\n\\n"
        "A US package has been allocated for one evening: Apaches on the road, "
        "a Warthog pair on the ridge, a gunship on the loiter and a Strike "
        "Eagle section holding the long shots. A Polish F-16 detachment "
        "transiting to the theatre has been pulled in for escort.\\n\\n"
        "Get the column to the airhead. The gunship is only usable because "
        "nothing in this sector has a working radar - if the J-16D "
        "re-establishes the picture, it leaves."),
    forces="Two AH-64E, an A-10C, an AC-130J, two F-15E, a Polish F-16C, a "
           "B-2 on a single allocated pass. Opposing: a J-16D, PLA road "
           "detachments and a mobile SAM.",
    objectives=[
        ("Column", "Get the relief column to the airhead", "35,-35,Fail,Main"),
        ("Gunship", "Do not lose the gunship", "20,-25,Complete"),
        ("Village", "Leave the settlements alone", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="column", at=(-4.6, 137.1), radius=30,
                 min_units=1, objective="Column"),
    protect=["support"], protect_objective="Gunship",
    neutral_objective="Village",
    win="The column is at the airhead and the gunship went home with fuel to "
        "spare. The corridor stays overland for another week.",
    lose="The road is closed and the relief corridor with it. Everything now "
         "has to fly, and there are not enough aircraft.",
    stations={
        "column": S(-8.5, 140.5, "Relief column", heading=300),
        "gun": S(-8.0, 139.6, "Attack flight", heading=300, alt=2000),
        "support": S(-7.8, 139.2, "Gunship loiter", heading=270, alt=16000),
        "escort": S(-7.4, 138.8, "Escort section", heading=300, alt=28000),
        "pass": S(-6.8, 138.2, "Single allocated pass", heading=320, alt=40000),
        "ridge": S(-4.5, 137.0, "Covered ridge", heading=120),
        "red_air": S(-4.3, 137.2, "Opposing fighter", heading=150, alt=30000),
    },
    units=[
        U("blue", "ah-64", "usa_ah-64e", "gun", name="Gunfighter 11"),
        U("blue", "ah-64", "usa_ah-64d", "gun", name="Gunfighter 12"),
        U("blue", "a-10c", "usa_a-10c", "gun", name="Hog 21", alt=8000),
        U("blue", "ac-130-pack", "usaf_ac-130j", "support", name="Spectre 31"),
        U("blue", "f-15e-strike-eagle", "usaf_f-15e_SE", "escort",
          name="Strike Eagle 41"),
        U("blue", "f-16c-modern", "pol_f-16c-bl52plus", "escort",
          name="Viper 51"),
        U("blue", "b-2-spirit", "usaf_b-2_spirit", "pass", name="Spirit 01"),
        U("blue", "french-army-vehicles", "fr_afv_jaguar", "column",
          name="Column escort"),
        U("blue", "re-power-resupply", "usa_car_hemtt", "column",
          name="Relief column"),
        U("red", "pla-land-unit-pack", "pla_9k331", "ridge",
          name="Mobile SAM, ridge"),
        U("red", "pla-land-unit-pack", "pla_apc_zbl-08", "ridge",
          name="Road detachment"),
        U("red", "j-16a", "plaf_j16a", "red_air", name="Enclave 61"),
        U("neutral", "buildings-targets-missions", "4tentgroup", "ridge",
          name="Settlement"),
        U("neutral", "pickup-truck-extension", "civ_car_pickup_1983", "column",
          name="Civilian traffic"),
    ],
))

DISPATCH_DESC = (
    "Optional episodes outside the twelve-mission Southern Watch spine. "
    "Allied Dispatches rotate a European, French/Spanish or US detachment "
    "through the same crisis; Red Line plays the opposing side's logistics "
    "problem; Range Week fires the missile-defence and ballistic systems "
    "where such things are actually fired; Future Front is an openly "
    "speculative 2034 branch for the collection's experimental aircraft and "
    "weapons; Cold Sea is a 1988 exercise for its retired types. Each one "
    "states its own fiction in the briefing.")


# =============================================================================
# OPTIONAL AND CONTINGENCY - the two the bible's first release scope names.
#
# O01 and C01 are here because the vertical slice is meant to prove the
# optional window and the setback gate, not because the other sixteen designs
# are unwanted. The rest of O02-O12 and C02-C06 stay unbuilt until the harness
# they depend on has been exercised in the running game; their point rewards
# and branch conditions are unverifiable from here.
# =============================================================================

MISSIONS.append(dict(
    group="optional", num="O1", key="The Missing Beacon",
    place="Arafura Sea", expires_after="Steel Highway",
    intro="Optional. A coaster stopped reporting on a route nobody was "
          "watching. Find her before the weather does.",
    special="Optional operation. It expires once the next main operation is "
            "complete. A confirmed report improves the contact briefing for "
            "STEEL HIGHWAY; a rescue is worth doing whether or not it does.",
    date=(2028, 10, 19), time=(16, 40), sea=3, clouds="Broken_2", wind="NW",
    difficulty=1, minutes=40, centre=(-10.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "ARAFURA SEA, late afternoon. MV Torres Light stopped transmitting "
        "nineteen hours ago on a coastal route that carries no traffic worth "
        "interfering with. Her beacon is silent and the weather is closing "
        "from the north-west.\n\n"
        "ARAFURA and a Seahawk have until last light. The lane has ordinary "
        "traffic in it and one of those hulls was in company with her "
        "yesterday, which is worth a conversation rather than a missile.\n\n"
        "Find her, establish what happened, and bring the search aircraft "
        "home. If this is what the last week suggests it is, the evidence is "
        "worth as much as the crew."),
    forces="HMAS Arafura and one MH-60R. Three merchant contacts on the lane, "
           "one of them the missing coaster's last company.",
    objectives=[
        ("Search", "Reach the missing coaster's last reported position",
         "30,-25,Fail,Main"),
        ("Aircraft", "Bring the search helicopter home", "10,-15,Complete"),
        ("Traffic", "Harm no lane traffic", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="datum", at=(-10.6, 132.0), radius=20,
                 min_units=1, objective="Search"),
    protect=["patrol"], protect_objective="Aircraft",
    neutral_objective="Traffic",
    win="Torres Light is found, her crew is off and the recordings from her "
        "bridge are in a bag on Arafura's quarterdeck. Somebody is going to "
        "have to explain them.",
    lose="Last light came and went. The search resumes tomorrow with worse "
         "weather and colder water.",
    stations={
        "patrol": S(-10.0, 131.5, "HMAS Arafura", heading=100),
        "datum": S(-10.4, 131.9, "Search datum", heading=100, alt=2000),
        "traffic": S(-11.4, 129.6, "Lane traffic", heading=70),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "patrol",
          name="HMAS Arafura", weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "datum",
          name="Arafura Flight", alt=2000, weapons="Tight"),
        U("neutral", "merchants-expanded", "civ_ms_mairangi_bay", "traffic",
          name="MV Coral Pioneer"),
        U("neutral", "auxilliary-merchant-pack", "ran_ms_antares", "traffic",
          name="MV Antares"),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "traffic",
          name="MV Sunda Relief"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "traffic",
          name="Arafura trawler"),
    ],
))

MISSIONS.append(dict(
    group="contingency", num="C1", key="After the Wake", place="Coral Sea",
    expires_after="Rig Seventeen",
    intro="Contingency, offered unconditionally. If STEEL HIGHWAY cost you a "
          "hull, this is about her crew; if it did not, it is a search that "
          "finds an empty sea.",
    special="Recovery operation. It pays no requisition points: it saves "
            "people and changes the debrief, and it does not restore the ship "
            "or its cargo. NOTE: this is offered after STEEL HIGHWAY whatever "
            "happened there. Gating it on the actual lost-cargo outcome needs "
            "a saved campaign condition this build has not demonstrated, so "
            "the unlock is unconditional and says so rather than pretending "
            "otherwise.",
    date=(2028, 10, 23), time=(6, 10), sea=4, clouds="Overcast", wind="SE",
    difficulty=2, minutes=45, centre=(-13.5, 148.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "CORAL SEA, first light. MV Lae Provider went down at 2140 last night "
        "with twenty-six aboard. Eleven are accounted for. The rest are "
        "somewhere inside a drift box that has been growing all night.\n\n"
        "HOBART is detached from the escort task with a Seahawk. The submarine "
        "that did it has not left the area and the search pattern you need to "
        "fly is exactly the pattern it will expect.\n\n"
        "Search the box. Do not lose the helicopter doing it. If the boat "
        "presents itself, that is a bonus and not the reason you are here."),
    forces="HMAS Hobart and one MH-60R on the search. One Type 039C still in "
           "the area. Two merchant hulls diverted to assist.",
    objectives=[
        ("Survivors", "Work the drift box to its northern edge",
         "30,-25,Fail,Main"),
        ("Helicopter", "Bring the search helicopter home", "15,-20,Complete"),
        ("Assist", "Do not lose an assisting merchant", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="search", at=(-12.6, 148.2), radius=25,
                 min_units=1, objective="Survivors"),
    protect=["hobart"], protect_objective="Helicopter",
    neutral_objective="Assist",
    win="Fourteen more out of the water, and the ones who did not make it are "
        "named rather than missing. That is the whole of what this operation "
        "could achieve, and it achieved it.",
    lose="The box is open at the northern end and the weather is building. "
         "The rest of that crew stays missing.",
    stations={
        "hobart": S(-13.5, 148.6, "HMAS Hobart", heading=340),
        "search": S(-13.2, 148.4, "Drift box", heading=340, alt=1500),
        "assist": S(-16.5, 150.0, "Assisting merchants", heading=320),
        "sub": S(-13.4, 148.2, "Submarine datum", heading=180),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "hobart",
          name="HMAS Hobart", weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "search",
          name="Hobart Flight", alt=1500, weapons="Tight"),
        U("neutral", "auxilliary-merchant-pack", "ran_ms_super_p", "assist",
          name="MV Torres Trader"),
        U("neutral", "re-power-resupply", "civ_ms_andizhan", "assist",
          name="MV Coral Provider"),
        U("red", "plan-submarines", "plan_ss_type_039c", "sub",
          name="Contact BRAVO"),
    ],
))

# =============================================================================
# THE SIX-WEEK CALENDAR AND THE REQUISITION ALLOCATIONS
#
# Dates and completion points come from the bible's chapter table and its
# mainline allocation table; they are applied here rather than repeated inside
# twenty mission dicts, so the schedule can be read as a schedule.
#
# service=True marks a mission the player reaches through a service window:
# repair and a free scheduled rearm are offered before it. Six of twelve is a
# first pass, not a measured pacing decision.
#
# generation="Generated" hands placement of the purchased force to the campaign.
# Every mission that deploys the task force now carries it: leaving it blank
# means the owned force never deploys, so a mission with an anchor and no
# Generated was asking the player to buy ships it would then ignore. The two
# air-only operations (SW07, SW08) and the two side missions stay authored,
# and the side missions disable the builder the way the stock campaign's
# detached operations do.
# =============================================================================

SCHEDULE = {
    # num: (date, completion points, service window, generation, anchor station)
    "01": ((2028, 10, 18), 100, False, "Generated", "warramunga"),
    "O1": ((2028, 10, 19), 50, False, None, "patrol"),
    "02": ((2028, 10, 22), 140, False, "Generated", "escort"),
    "C1": ((2028, 10, 23), 0, False, None, "hobart"),
    "03": ((2028, 10, 26), 120, True, "Generated", "amphib"),
    "04": ((2028, 10, 30), 100, False, "Generated", "patrol"),
    "05": ((2028, 11, 2), 140, True, "Generated", "warramunga"),
    "06": ((2028, 11, 6), 140, False, "Generated", "hobart"),
    "07": ((2028, 11, 9), 120, True, None, "picket"),
    "08": ((2028, 11, 13), 180, False, None, None),
    "09": ((2028, 11, 16), 160, True, "Generated", "escort"),
    "10": ((2028, 11, 20), 180, False, "Generated", "escort"),
    "11": ((2028, 11, 23), 200, True, "Generated", "escort"),
    "12": ((2028, 11, 28), 0, True, "Generated", "escort"),
}

for _m in MISSIONS:
    _s = SCHEDULE.get(_m["num"])
    if _s:
        _m["date"], _m["points"], _m["service"], _m["generation"], _m["anchor"] = _s

# Prologue, six situation reports and an epilogue: the eight story screens the
# bible's timeline calls for, one report closing each of the first five
# chapters and one before the last passage.
SITREPS = [
    ("24 October 2028", "Chapter 1 closes", "The Arafura convoy is through",
     "THE ESCORT TASK IS FORMALISED",
     ["Warramunga's report of the rendezvous went to Canberra inside an hour "
      "and came back as a standing task. The escort group forms around her.",
      "Port Moresby's engineering plant is ashore. The Pukpuk arrangements are "
      "being read carefully by people who had not read them before."],
     "Rig Seventeen"),
    ("31 October 2028", "Chapter 2 closes", "The network behind the incidents",
     "SOMEBODY IS SUPPLYING THEM",
     ["The platform crews are ashore and the low-profile craft is in a shed "
      "with photographers around it. What it was carrying matters less than "
      "where it was going.",
      "Two of the routes now have names. The people running them have not been "
      "named, and the Meridian duty controller has stopped answering."],
     "Warramunga's Shot"),
    ("7 November 2028", "Chapter 3 closes", "Overt attacks begin",
     "THIS IS NO LONGER DENIABLE",
     ["An armed escort fired on a protected convoy in daylight. The recordings "
      "are unambiguous and the diplomatic language has changed accordingly.",
      "Growler and wider surveillance allocations are released. Damage and "
      "magazine expenditure are no longer things the force can simply absorb."],
     "Long Way Home"),
    ("14 November 2028", "Chapter 4 closes", "The corridor is open",
     "THE WINDOW HELD",
     ["The relief movement is out and the enclave's battery is off the air. "
      "The negotiation that follows starts from a better place than the one "
      "that would have followed a closed window.",
      "Tanker hours, not hulls, were the limiting factor this week. They will "
      "be again."],
     "Southern Lifeline"),
    ("21 November 2028", "Chapter 5 closes", "The route is sustained",
     "THE LIFELINE HOLDS",
     ["Collins is dived and heading for Stirling. Supply still has enough in "
      "her tanks to do it again.",
      "The Japanese detachment is on station and the corridor has a second "
      "usable escort force for the first time since October."],
     "Fujian's Shadow"),
    ("27 November 2028", "Before the last passage", "An imperfect ceasefire",
     "ONE PASSAGE THAT MUST WORK",
     ["The talks opened with the corridor open, which is the only reason they "
      "opened at all. The ceasefire takes effect at midnight and not every "
      "group in the box has acknowledged it.",
      "Coral Pioneer is at the head of the first convoy through, with a "
      "bearing running hot. Everything this campaign was about is in that one "
      "sentence."],
     "The First Ship Through"),
]

for _i, (_date, _title, _sub, _head, _body, _before) in enumerate(SITREPS, 1):
    EVENTS.insert(_i, dict(file=f"{_i:02d}_sitrep", before=_before,
                           title=f"{_title}\\n{_date}", sub=_sub,
                           dateline=f"{_date.upper()}  |  MARITIME BORDER COMMAND, DARWIN",
                           headline=_head, body=_body))


# =============================================================================
# OBJECTIVES, WINDOWS AND GEOMETRY
#
# Three tables the review of f3e2a783 forced into existence. Each fixes a class
# of defect that no gate in the build could see:
#
# RESOLVERS  every objective now names the predicate that completes or fails
#            it. Twenty objective ids used to resolve to nothing at all: the
#            player was told to keep the Triton flying, and losing it changed
#            no score, no message and no outcome. "victory" means the main
#            trigger completes it; "neutral" means the neutral-loss trigger
#            fails it; everything else gets a trigger of its own.
#
# WINDOWS    purchases, repair and rearm are three separate permissions, and
#            the campaign opens them at the points the design says rather than
#            everywhere at once. Air tasking rows are what connect a purchased
#            aircraft to a mission slot; without them the roster sells
#            fighters that no mission can deploy.
#
# ARRIVALS   an arrival box that a 13-knot merchant cannot reach in 75 minutes
#            is not an objective, and one the search helicopter starts inside
#            is not either. Both shipped. The builder now refuses both.
# =============================================================================

CAP = ("CAP|Combat Air Patrol|Fighter|2|AirToAir/AirToAirLongRange/"
       "AirToAirIntercept")
RECON = ("Recon|Maritime Patrol|MPA/ASW/ESM/AEW|1|ASW/Recon/AntiShip/AEW")
HELO = ("HeloRecon|Ship's Flight|Helicopter|1|ASW/ASWKiller/ASWHunter/"
        "ASWLongRange")
STRIKE = ("Attack|Maritime Strike|Bomber/SEAD|2|AntiShipLongRange/AntiShip/"
          "StrikeLongRange/Strike/StrikePrecision/SEAD/SEADLongRange")

WINDOWS = {
    # buy: the task force builder opens. repair/rearm: a service window.
    # flights: air-tasking rows the purchased aircraft can be assigned to.
    "01": dict(buy=True, flights=[HELO, RECON]),
    "O1": dict(flights=[HELO]),
    "02": dict(buy=True, repair=True, rearm=True, flights=[HELO, RECON, CAP]),
    "C1": dict(flights=[HELO]),
    "03": dict(flights=[HELO]),
    "04": dict(rearm=True, flights=[HELO, RECON]),
    "05": dict(buy=True, repair=True, rearm=True, flights=[HELO, STRIKE]),
    "06": dict(flights=[CAP, RECON], airbase_prep=True),
    "07": dict(repair=True, flights=[CAP], airbase_prep=True),
    "08": dict(buy=True, flights=[STRIKE, CAP], airbase_prep=True),
    "09": dict(repair=True, rearm=True, flights=[HELO, RECON]),
    "10": dict(rearm=True, flights=[HELO, RECON, CAP]),
    "11": dict(buy=True, repair=True, rearm=True, flights=[CAP, STRIKE]),
    # SW12 is the epilogue passage: repair and aircraft replacement, no new
    # hulls and no general rearm.
    "12": dict(repair=True, flights=[HELO, RECON]),
}

TIMEOUTS = {
    "01": "Last light, and the merchants are still scattered across forty miles "
          "of the Arafura. Whatever this was, it worked.",
    "O1": "Dark. The search resumes tomorrow in worse weather and colder water.",
    "02": "The window at Moresby closed. The plant and the medical stores are "
          "still at sea and the wharf party has gone home.",
    "C1": "The drift box is open at the northern end and the weather is "
          "building. The rest of that crew stays missing.",
    "03": "The evacuation window expired with people still on the deck. There "
          "will not be another one this week.",
    "04": "The passenger is into the passage and gone. Whatever the route was, "
          "it still is.",
    "05": "The escort is still between the convoy and the corridor, and the "
          "convoy has turned back.",
    "06": "The passage window closed. The convoy is holding in open water "
          "inside somebody's launch basket.",
    "07": "The tanker never made the recovery line. Every sortie in the north "
          "tomorrow gets shorter.",
    "08": "The relief window expired. The next negotiation starts from a worse "
          "place than this one did.",
    "09": "The service window ran out with the boat still on the surface. She "
          "goes home the long way, on what she has.",
    "10": "The handover time passed. The cargo is still in the corridor and the "
          "Japanese detachment is out of allocation.",
    "11": "The transports never cleared the approaches. The talks open on "
          "Friday with the corridor closed.",
    "12": "Darwin's approaches are empty at the deadline. The first ship "
          "through did not get through.",
    "D1": "The group is still west of the line. The corridor plans around a "
          "tank that does not refill.",
    "D2": "The cycle broke and the visit was waved off. Somebody will write a "
          "report about the afternoon the carriers stopped flying.",
    "D3": "The beach window closed. The distribution point never opened and the "
          "request for help goes elsewhere.",
    "D4": "Daylight, and the auxiliary is still in the corridor at six knots "
          "with every coalition sensor in the Banda looking for her.",
    "D5": "The serial ran out of range time with pads still standing. The "
          "trials report will say so at length.",
    "D6": "The stream broke up short of release. Even in fiction, range is "
          "range.",
    "D7": "The exercise serial expired. The umpires have scored it against you.",
    "D8": "Dark, and the column is still short of the airhead with the ridge "
          "uncleared. The corridor goes back to flying.",
}

# Arrival boxes are authored as a BEARING (the direction the operation runs)
# and a radius. The builder solves the distance against where the units
# actually ended up after position snapping, so a box can be neither already
# occupied at spawn nor out of reach in the mission's own running time. Both
# shipped once as hand-written coordinates.
ARRIVALS = {
    "01": (52, 12),
    "02": (-18, 12),
    "03": (180, 20),
    "04": (-177, 12),
    "06": (-131, 12),
    "07": (-170, 20),
    "08": (161, 20),
    "09": (154, 12),
    "10": (139, 12),
    "11": (138, 12),
    "12": (-142, 12),
    "C1": (-11, 20),
    "D1": (85, 12),
    "D2": (154, 20),
    "D3": (133, 20),
    "D4": (135, 12),
    "D6": (28, 20),
    "D8": (-41, 12),
    "O1": (148, 20),
}

RESOLVERS = {
    "01": {"Convoy": "victory", "Neutrals": "neutral",
           "Warramunga": ("protect", "warramunga")},
    "O1": {"Search": "victory", "Traffic": "neutral",
           "Aircraft": ("protect", "datum")},
    "02": {"Cargo": "victory", "Neutrals": "neutral",
           "Medical": ("protect", "convoy#1")},
    "C1": {"Survivors": "victory", "Assist": "neutral",
           "Helicopter": ("protect", "search")},
    "03": {"Evacuate": "victory", "Platform": "neutral",
           "Ships": ("protect", "amphib")},
    "04": {"Track": "victory", "Neutrals": "neutral",
           "Patrol": ("protect", "patrol")},
    "05": {"Escort": "victory", "Convoy": ("protect", "convoy"),
           "Magazine": ("protect", "warramunga")},
    "06": {"Convoy": "victory", "Sentry": ("protect", "isr"),
           "Hobart": ("protect", "hobart")},
    "07": {"Tanker": "victory", "Package": ("survive", "package"),
           "Raptors": ("survive", "cap")},
    "08": {"Window": "victory", "Town": "neutral",
           "Battery": ("destroy", "battery", 2)},
    "09": {"Service": "victory", "Collins": ("protect", "support#2"),
           "Supply": ("protect", "support#1")},
    "10": {"Cargo": "victory", "Allies": ("protect", "jmsdf"),
           "Submarine": ("destroy", "red_sub", 1)},
    "11": {"Transports": "victory", "Ford": ("protect", "carrier#1"),
           "Strike": ("destroy", "red_air", 2)},
    "12": {"Convoy": "victory", "Ceasefire": "neutral",
           "Escorts": ("protect", "escort")},
    "D1": {"Oiler": "victory", "Escorts": ("survive", "escort"),
           "Shadow": ("destroy", "red_air", 2)},
    "D2": {"Visit": "victory", "Cycle": ("protect", "carriers"),
           "Tanker": ("protect", "air#2")},
    "D3": {"Relief": "victory", "Town": "neutral",
           "Group": ("protect", "group")},
    "D4": {"Auxiliary": "victory", "Cruiser": ("protect", "escort#1"),
           "Restraint": ("survive", "cap")},
    "D5": {"Pads": "victory", "Safety": "neutral",
           "Serial": ("destroy", "target", 1)},
    "D6": {"Stream": "victory", "Escort": ("survive", "escort"),
           "Sensor": ("protect", "sensor")},
    "D7": {"Serial": "victory", "Recovery": ("protect", "high"),
           "Umpire": ("protect", "sea")},
    "D8": {"Column": "victory", "Village": "neutral",
           "Gunship": ("protect", "support")},
}

for _m in MISSIONS:
    _n = _m["num"]
    _m["resolve"] = RESOLVERS[_n]
    _m["timeout"] = TIMEOUTS[_n]
    _m["window"] = WINDOWS.get(_n, {})
    if _n in ARRIVALS:
        _m["victory"]["bearing"], _m["victory"]["radius"] = ARRIVALS[_n]
        _m["victory"].pop("at", None)


# =============================================================================
# AIR TASKING, DEPTH AND ROUTES
#
# SLOTS  connects a purchased aircraft to a place in a mission. The roster
#        sells F-35s, Super Hornets, Growlers, P-8s, a Wedgetail, a Triton and
#        a tanker; without a flight row and a matching mission slot, buying one
#        changed nothing, because every airborne unit was a fixed authored one.
#        The row is declared in WINDOWS, the slot is tagged here, and the role
#        must be one the row's filter accepts.
#
# DEPTHS  every submarine was emitted at 0 - on the surface. That is correct
#         for Collins alongside her tender in SW09 and wrong for a Type 039
#         that is supposed to be the reason the mission is hard.
#
# ROUTES  SW04's whole objective is a contact reaching a handover box, and
#         nothing in the file ever told it to go there. Waypoints are
#         (lat, lon, depth-or-altitude).
# =============================================================================

SLOTS = {
    # (mission, unit type): (flight row, role)
    ("01", "usn_mh-60r"): (1, "HeloRecon"), ("01", "usn_p8"): (2, "Recon"),
    ("O1", "usn_mh-60r"): (1, "HeloRecon"),
    ("02", "E7A_Wedgetail"): (2, "Recon"),
    ("C1", "usn_mh-60r"): (1, "HeloRecon"),
    ("03", "usmc_ch53_standalone"): (1, "HeloRecon"),
    ("04", "usn_mh-60r"): (1, "HeloRecon"), ("04", "usn_p8"): (2, "Recon"),
    ("05", "usn_mh-60r"): (1, "HeloRecon"),
    ("06", "raaf_f-35a"): (1, "CAP"), ("06", "raaf_mq-4c_triton"): (2, "Recon"),
    ("07", "usaf_f-22_s6"): (1, "CAP"),
    ("08", "usn_ea-18g"): (1, "Attack"), ("08", "raaf_f-35a"): (2, "CAP"),
    ("09", "usn_mh-60r"): (1, "HeloRecon"),
    ("10", "jp_sh-60k"): (1, "HeloRecon"), ("10", "jp_sh-60j"): (1, "HeloRecon"),
    ("10", "jp_f-2a_late"): (3, "CAP"),
    ("11", "usn_f-35c"): (1, "CAP"), ("11", "usn_ea-18g_2020"): (2, "Attack"),
    ("12", "usn_p8"): (2, "Recon"),
}

DEPTHS = {
    # Hunting boats sit below the layer; the ones on a surface task do not.
    "plan_ss_type_039c": -400, "plan_ss_type_039": -350,
    "plan_ss_kilo": -300, "wp_ssn_akula": -500,
    "_narco_narcosub_adv": -60,          # semi-submersible, barely under
    "civ_humpback": -120,                # a whale where a whale would be
    "ran_ssg_collins": 0,                # surfaced alongside, deliberately
    "usn_ssn_seawolf": -450,
}

ROUTES = {
    # SW04's contact runs south out of the Seram passage for the handover box.
    # Its objective is that it gets there; an unrouted contact never would.
    ("04", "_narco_narcosub_adv"): [(-5.45, 130.19, -60), (-5.70, 130.18, -60),
                                    (-5.95, 130.17, -60)],
}

for _m in MISSIONS:
    for _u in _m["units"]:
        _slot = SLOTS.get((_m["num"], _u["type"]))
        if _slot:
            _u["slot"] = _slot
        if _u["type"] in DEPTHS:
            _u["depth"] = DEPTHS[_u["type"]]
        _route = ROUTES.get((_m["num"], _u["type"]))
        if _route:
            _u["route"] = _route
