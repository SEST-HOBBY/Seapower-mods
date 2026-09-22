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
    "Needs the Steam Workshop mods listed in REQUIRED-MODS.txt, in this "
    "mod's own folder; LOAD-ORDER.txt beside it is the Mod Manager order it "
    "was built and tested against.")


def U(side, mod, type, station, **kw):
    """One placed unit: whose side, which mod it is there to exercise, what it
    is, and where it stands. Hull variant, squadron and loadout are resolved
    from the winning file at build time, not guessed here."""
    return dict(side=side, mod=mod, type=type, station=station, **kw)


def F(objective, units=None, minimum=1):
    """A loss that ends the mission, and the objective it fails.

    One flat list with one objective id used to cover every protected unit in
    a mission, so whatever sank, the same objective was reported failed:
    SW09 said Collins was lost when a freighter with no objective of its own
    went down, and SW07 blamed the tanker for a Rhino. Each entry now names
    its own units, and `units=None` means take them from that objective's own
    resolver - which is the only way the trigger that ends the mission and the
    trigger that marks the objective failed cannot drift apart.
    """
    return dict(objective=objective, units=units, minimum=minimum)


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
             "before you shoot - none of this is a war yet, and the fastest "
             "way to make it one is to be wrong about a fishing boat."]),
    # Rendered as an INTSUM: its dateline already said COALITION JOINT
    # INTELLIGENCE, and a press sheet from an intelligence cell is a form the
    # campaign never had a reason to use.
    dict(file="06_interlude", before="The Open Door", form="intsum",
         title="The Enclave\\n12 November 2028",
         sub="A contested airfield, foreign advisers and a relief window",
         org="Coalition Joint Intelligence Centre, Darwin", ref="INTSUM 028-63",
         date="12 November 2028", subject="The enclave",
         body=[
             "1. Regional security forces have recovered most of the "
             "facilities Meridian's hard-line faction seized. One airfield and "
             "port enclave has not come back, and the battery covering it is "
             "not the man-portable inventory the first reports described.",
             "2. A naval force has arrived under a protection-and-evacuation "
             "pretext and demanded the coalition patrols suspend. A small "
             "foreign expeditionary detachment is supporting the enclave under "
             "a separate arrangement. Its fuel and ammunition arrive by routes "
             "we can see, which is the one advantage we have.",
             "3. Local authorities have asked for a protected window to move "
             "civilians and emergency supplies out. That window, not a body "
             "count, is the objective.",
             "4. Guidance. A battery off the air for two hours is worth more "
             "than a battery destroyed at the cost of the aircraft that were "
             "going to fly the relief."],
         note="Two hours. Not the battery.  - AM"),
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
             "Master Santos's last entry for the passage, which she has allowed "
             "to be quoted, reads: \"Alongside. One shaft. All hands.\" The "
             "Commodore's, which he has not, is understood to be shorter.",
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
         note="US support. Role=Airliner with a single Tanker fit, so its "
              "air-tasking row filters Airliner rather than a tanker role; "
              "neither that tasking path nor receiver compatibility is tested"),
    dict(unit="usn_mh-60r", picks=["Squadron1"], points=20,
         note="one family chosen explicitly - usn_mh-60r_26 is a different "
              "unit and is never substituted for it"),
]

# Australian commander, no same-nation discount: the mod unit definitions carry
# US and allied nationality, and a discount keyed to them would be arbitrary.
# No emblem or ribbon art is referenced - every path would be a .png this repo
# cannot produce.
# CommanderStartingRankLevel is an index into [OfficerRanks], and this file
# shipped for one build with the index and no ladder for it to point at. The
# RAN ladder below is the base game's own, from Pacific Strike's
# commander_settings.ini - the only shipped campaign that runs Task Force
# Mode, and therefore the only reference for this file. Level 5 is Commander,
# which is the right rank for a task group of this size.
#
# The insignia and the emblem are base-game assets referenced by path, not
# copied: nothing here ships a PNG for them.
#
# No [TaskForceRibbons] or [MissionRewards]. Pacific Strike carries both and
# awards a US rack with two Australian decorations in it; writing a RAN rack
# would mean inventing decorations and their precedence, which is content, not
# a fix. Their absence costs the campaign its ribbons and nothing else.
COMMANDER = """[CommanderSettings]
CommanderNations=Australia
CommanderDefaultNation=Australia
CommanderNameDefaultAustralia=Alex Mercer
CommanderNamePoolAustralia=Names_Australia
CommanderStartingRankLevel=5
SameNationUnitDiscount=0

NavyNameAustralia=Royal Australian Navy
NavyEmblemAustralia=ui/campaign/navy_emblems/ran_emblem.png

[OfficerRanks]
Australia=Midshipman,MIDN,OF-D,0,ui/campaign/officer_ranks/australia/insignia_midn.png|Acting Sub Lieutenant,ASLT,OF-1,1,ui/campaign/officer_ranks/australia/insignia_aslt.png|Sub Lieutenant,SLT,OF-1,2,ui/campaign/officer_ranks/australia/insignia_slt.png|Lieutenant,LEUT,OF-2,3,ui/campaign/officer_ranks/australia/insignia_lt.png|Lieutenant Commander,LCDR,OF-3,4,ui/campaign/officer_ranks/australia/insignia_lcdr.png|Commander,CMDR,OF-4,5,ui/campaign/officer_ranks/australia/insignia_cdr.png|Captain,CAPT,OF-5,6,ui/campaign/officer_ranks/australia/insignia_capt.png|Commodore,CDRE,OF-6,7,ui/campaign/officer_ranks/australia/insignia_cdre.png|Rear Admiral,RADM,OF-7,8,ui/campaign/officer_ranks/australia/insignia_radm.png|Vice Admiral,VADM,OF-8,9,ui/campaign/officer_ranks/australia/insignia_vadm.png|Admiral,ADM,OF-9,10,ui/campaign/officer_ranks/australia/insignia_adm.png
"""

MISSIONS = []

# =============================================================================
# CORE - SW01 to SW12. Australian-led, October-November 2028.
# =============================================================================

MISSIONS.append(dict(
    group="core", num="01", key="White Water", place="Arafura Sea",
    intro="Find the convoy, work out which contact is armed, and keep the "
          "rendezvous open. Nothing here is a target without identification.",
    sender="Commodore Alex Mercer, Maritime Border Command, Darwin",
    intent=("Get the crews out of danger and the merchants into the box. "
            "Identify before you shoot: a dead fishing boat ends this "
            "operation and starts something worse, and a Meridian escort "
            "that gets away is a problem for Wednesday. Coral Pioneer is the "
            "ship this morning is about; bring her in."),
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
        "a container hull putting out the radars of a warship it is not - do "
        "not let your ESM operator pick the wrong one. "
        "Identify before you shoot. Your weapons are tight."),
    forces="HMAS Warramunga (Anzac class), one MH-60R, one P-8A on task, one "
           "MQ-4C Triton overhead. Four merchant hulls to collect, three "
           "neutral contacts in the box, one armed escort and one decoy.",
    objectives=[
        ("Convoy", "Walk the merchant group into the eastern handover box",
         "30,-30,Fail,Main"),
        ("Neutrals", "Harm no neutral shipping or aircraft", "0,-40,Complete"),
        ("Warramunga", "Bring Warramunga out intact", "10,-15,Complete"),
        # Identification was the point of the mission and nothing scored it.
        # `None` with a zero failure score is the native pairing for an
        # optional task (9 of the 11 uses in the shipped missions): done, it
        # pays; never done, it resolves to nothing. The difference between a
        # clean pass and a pass, not between a pass and a loss.
        ("Identify", "Classify the Meridian escort before the handover",
         "10,0,None"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(-10.1, 132.3), radius=25,
                 # Coral Pioneer is the ship the briefing opens on and the
                 # defeat text mourns; she used to be optional - any three of
                 # four won. She is convoy#1, and she has to be in the box.
                 also=[dict(units=["convoy#1"], min_units=1)],
                 min_units=3, objective="Convoy"),
    fatal=[F("Convoy", ["convoy"], 2)],
    neutral_objective="Neutrals",
    win="The merchants are in the box and their crews are alive. The escort "
        "has been identified, and so has everything you did not shoot. Santos, on Ch16: 'Understood, "
        "Warramunga. We were not going to heave to anyway.'",
    lose="The convoy is scattered and Coral Pioneer is not answering. Whatever "
         "this was, it worked.",
    stations={
        # Encounter scale. The first build of this opening had Warramunga
        # 34 NM from the group she is told to shepherd (50 minutes at flank
        # covers 24), the "identification traffic" 130 NM away and sailing
        # off, and the armed escort stationary and facing away with a 17 NM
        # radar 20 NM from the nearest merchant. Every gate passed. Now the
        # escort is 8 NM astern, the trawlers and the Meridian hull sit ON
        # the track to the handover box 12-16 NM ahead, and the airliner
        # crosses overhead - so the picture has pieces in it.
        "warramunga": S(-10.42, 131.77, "HMAS Warramunga", heading=80),
        "convoy": S(-10.4, 131.9, "Coral Pioneer group", heading=80),
        "neutrals": S(-10.20, 132.00, "Arafura traffic", heading=230),
        "meridian": S(-10.23, 132.11, "Meridian escort", heading=230),
        "air": S(-10.6, 131.6, "Southern Watch air", heading=70, alt=22000),
        # The brief says a Seahawk on the deck. It spawned 21 NM away at
        # 3,000 ft in the same Vic as a P-8 doing three times its speed at six
        # times its height. Beside the ship, low, on the ship's heading.
        "flight": S(-10.44, 131.76, "Ship's flight", heading=80, alt=500),
        "high": S(-9.9, 131.9, "Triton orbit", heading=90, alt=50000),
        "liner": S(-10.3, 132.32, "Denpasar service", heading=260, alt=34000),
        "home": S(-12.409, 130.8665, "RAAF Base Darwin"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "warramunga",
          variant="Variant3", name="HMAS Warramunga", weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight",
          name="Warramunga Flight", alt=500, weapons="Tight"),
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
        # The escort CLOSES: to the convoy's starting position, then on toward
        # the handover box - so it is the thing the player has to identify
        # before it is inside gun range of a merchant, not a hull parked
        # facing the wrong way 20 NM outside its own radar.
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "meridian",
          name="Meridian Escort 7",
          route=[(-10.4, 131.9, 0), (-10.15, 132.25, 0)]),
        U("red", "_vanilla", "wp_ms_mercur_decoy", "meridian",
          name="MV Meridian Assurance"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="02", key="Steel Highway", place="Coral Sea",
    intro="Four priority ships to Port Moresby. A submarine report on the "
          "planned track. The masters want to keep going.",
    sender="Commodore Alex Mercer; Commander Mara Kila, PNGDF Maritime Element, concurring",
    intent=("Kokoda Star is the hospital. Lae Provider is the fuel that "
            "keeps it running until Kokoda Star arrives. If the submarine "
            "report is real, it wants one of those two. Three of four "
            "through the box is a pass; Kokoda Star among them is the pass. "
            "All four is what Moresby is expecting."),
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
           "the area. Port Moresby is open beyond the box.",
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
    fatal=[F("Medical", ["convoy#1"])],
    neutral_objective="Neutrals",
    win="Three hulls through the approach box, Kokoda Star among them. "
        "Moresby's pilots have them from here, and the route is a route again.",
    lose="The convoy is short and Moresby is still waiting. The next one will "
         "have to be bigger, slower and later.",
    stations={
        "escort": S(-13.4, 148.4, "Escort group", heading=320),
        "convoy": S(-13.6, 148.6, "Priority convoy", heading=320),
        "traffic": S(-13.41, 148.43, "Coral Sea traffic", heading=250),
        "moresby": S(-9.5, 147.0, "Port Moresby", heading=0),
        "sub": S(-13.5, 148.2, "Submarine datum", heading=90),
        "air": S(-12.0, 148.0, "Air support", heading=320, alt=30000),
        # The ship's helicopter spawned at 30,000 ft 86 NM from the ship it
        # is homed on, in a mission the submarine can decide in twenty
        # minutes. Beside the escorts, low.
        "flight": S(-13.42, 148.42, "Ship's flight", heading=320, alt=500),
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
        # An unarmed 24-kn freighter. The hull it replaced was an armed
        # auxiliary with eleven weapon systems, Styx among them, sailing as
        # the "medical and engineering ship" with weapons free - which the
        # bible forbids in so many words, and which a player would have seen
        # the moment it opened fire on the submarine.
        U("blue", "re-power-resupply", "civ_ms_freighter_b", "convoy",
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
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        # Tasking cockpits, unnamed on purpose: a helicopter slot beside the
        # ship and a maritime-patrol slot for the P-8 the roster starts
        # selling here. The two F-35A cockpits and their CAP row are gone -
        # this mission declares no air threat and sells no fighter.
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "flight"),
        U("blue", "p-8-poseidon", "usn_p8", "air", squadron="Squadron3"),
    ],
))

MISSIONS.append(dict(
    group="core", num="03", key="Rig Seventeen", place="Timor Sea",
    intro="Civilians on an offshore platform, armed contractors on the deck "
          "above them, and a patrol closing from the north.",
    sender="Commodore Alex Mercer; Captain Ratna Prasetyo, TNI-AL, embarked",
    intent=("The platform is not a target. The people on its upper deck are "
            "Captain Prasetyo's problem afterwards and not yours now. Two "
            "airframes, one lift each, and a patrol closing from the north "
            "that has answered nobody. Get the crew off before it arrives, "
            "or hold it off until they are."),
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
    victory=dict(kind="arrive", station="lift", at=(-11.55, 126.62), radius=12,
                 # Not scored until a lifter has been over the platform. The
                 # first build could be won by flying straight south from
                 # spawn and never going near the thing the mission is about.
                 after=dict(kind="area", units="lift", at_unit="rig", radius=3,
                            min_units=1,
                            intel="Lifter over the platform. The crew is on "
                                  "the helideck and coming aboard - get them "
                                  "south of the line."),
                 min_units=1, objective="Evacuate"),
    fatal=[F("Ships", ["amphib"])],
    neutral_objective="Platform",
    win="The lifters are south of the line with the platform crew aboard. "
        "Rig Seventeen is still standing and somebody else can argue about "
        "who owns it.",
    lose="The window closed with people still on the deck. There will not be "
         "another one this week.",
    stations={
        "amphib": S(-11.6, 126.6, "Amphibious group", heading=10),
        # 24 NM south of the rig, outside the arrival box: rig and back is
        # 84 NM, 42 minutes at 120 kn, inside a 60-minute clock with margin
        # for the hover. From the old spawn the round trip was 127 NM.
        "lift": S(-11.0, 126.45, "Lift flight", heading=350, alt=2000),
        "rig": S(-10.6, 126.4, "Rig Seventeen", heading=0),
        "shore": S(-8.6, 125.6, "Contested headland", heading=180),
        # The traffic used to be 155 NM away and stationary; the patrol the
        # campaign card promises did not exist at all. Both are now within the
        # rig's horizon: a tanker steaming past the platform on the lifters'
        # track, a fishing boat drifting near it, and a Meridian hull 22 NM
        # north with a route onto the rig - the thing the lift is racing.
        "traffic": S(-10.75, 126.15, "Timor traffic", heading=100),
        "patrol": S(-10.23, 126.35, "Patrol from the north", heading=180),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_lsd_choules", "amphib",
          name="HMAS Choules"),
        U("blue", "SEST_RAN_Fleet", "ran_lhd_canberra", "amphib",
          name="HMAS Canberra"),
        # The Rescue fit: 37 seats. The default fit is two Mk48 torpedoes and
        # TransportCapacity=0, which is not a lift helicopter, it is an ASW
        # helicopter with a story attached.
        U("blue", "ch-53e-standalone", "usmc_ch53_standalone", "lift",
          name="Lifter 11", alt=1500, weapons="Tight", loadout="CH53SARescue"),
        U("blue", "ch-53e-standalone", "usmc_ch53_standalone", "lift",
          name="Lifter 12", alt=1500, weapons="Tight", loadout="CH53SARescue"),
        U("neutral", "armed-oil-rig", "civ_spar_rig_helo", "rig",
          name="Rig Seventeen", snap="sea"),
        U("neutral", "_vanilla", "civ_ms_ritina", "traffic",
          name="Timor tanker",
          route=[(-10.65, 126.55, 0), (-10.7, 126.9, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "traffic",
          name="Timor fishing boat", route=[(-10.9, 126.45, 0)], telegraph=2),
        # A Meridian hull, not a navy: in the fiction the fleet has not arrived
        # yet (that is chapter 3), and Captain Prasetyo's cable says only "a
        # patrol is closing from the north. It is not ours."
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "patrol",
          name="Meridian Escort 4", route=[(-10.62, 126.42, 0)], telegraph=4),
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
    sender="Commodore Alex Mercer",
    intent=("Classify it, then walk it into the box. Do not sink it: what it "
            "is carrying is evidence and where it was going is the route. "
            "There is a real submarine in the same water and a whale that "
            "will cost you an hour. Only one of the three matters tonight."),
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
           "KJ-500, a Ka-28 and a spotter drone working for somebody else.",
    objectives=[
        ("Track", "Walk the low-profile craft into the handover box",
         "30,-30,Fail,Main"),
        ("Patrol", "Keep HMAS Arafura afloat", "15,-25,Complete"),
        ("Neutrals", "Do not shoot the wildlife or the fishermen",
         "0,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="passenger", at=(-7.1, 130.1),
                 radius=20, min_units=1, objective="Track",
                 # The contact used to score the mission by driving itself
                 # into the box. Now nothing counts until the player has
                 # classified it - the mission is called The Quiet Passenger
                 # because finding out what it is IS the task.
                 after=dict(kind="classify", units="passenger", min_units=1,
                            intel="WHISKEY classified: one low-profile "
                                  "semi-submersible, running south on the "
                                  "surface with almost no freeboard. Walk "
                                  "her into the box. Do not sink the "
                                  "evidence.")),
    # Sinking the passenger ends it: the whole point is where it was going.
    fatal=[F("Patrol", ["patrol"]), F("Track", ["passenger"])],
    neutral_objective="Neutrals",
    win="The passenger is in the box with a boarding party alongside and the "
        "Type 039 knows exactly how long you held it. The route is on paper "
        "now.",
    lose="The passenger is gone - into the passage, or onto the bottom with "
         "whatever it was carrying. Either way the route it was running is "
         "still a rumour, and the only thing you positively identified all "
         "night had a blowhole.",
    stations={
        # Arafura faces the box she is walking the contact into (it is north
        # of her, where the contact comes from); the Type 039 runs south past
        # the passenger's track instead of sitting 82 NM away as scenery; the
        # fishing boat crosses that track; and every dissimilar aircraft has
        # its own station, because a P-8 formed 0.1 NM on a helicopter is a
        # formation no vanilla mission flies.
        "patrol": S(-5.9, 130.3, "HMAS Arafura", heading=20),
        "passenger": S(-5.2, 130.2, "Low-profile craft", heading=195),
        "sub": S(-5.6, 130.35, "Type 039 datum", heading=180),
        "whale": S(-5.95, 130.10, "Biologic contact", heading=150),
        "fishing": S(-5.7, 130.05, "Banda fishing boat", heading=60),
        "air": S(-6.2, 130.6, "Arafura Flight", heading=0, alt=2500),
        "mpa": S(-6.3, 130.7, "Maritime patrol", heading=0, alt=15000),
        "red_air": S(-4.4, 129.9, "PLAAF orbit", heading=180, alt=28000),
        "red_helo": S(-4.9, 130.15, "Helix track", heading=180, alt=4000),
        "red_uav": S(-5.0, 130.4, "Spotter track", heading=200, alt=12000),
        "home": S(-12.409, 130.8665, "RAAF Base Darwin"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "patrol",
          name="HMAS Arafura", weapons="Tight"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "air", name="Arafura Flight",
          alt=2500, weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3",
          name="Bluefin 24", alt=15000, weapons="Tight"),
        U("red", "red-storm-arsenal", "_narco_narcosub_adv", "passenger",
          name="Contact WHISKEY"),
        U("red", "plan-submarines", "plan_ss_type_039", "sub",
          name="Contact SIERRA", depth="belowlayer",
          route=[(-6.3, 130.3, "belowlayer")], telegraph=2),
        U("red", "modern-plan-systems", "plaaf_kj-500", "red_air",
          name="Dragon Eye 03", weapons="Hold"),
        U("red", "modern-plan-systems", "plan_ka-28", "red_helo",
          name="Helix 11", alt=4000),
        U("red", "small-medium-uav-series", "usn_ForpostR705", "red_uav",
          name="Spotter drone", alt=12000),
        U("neutral", "humpback-whale", "civ_humpback", "whale",
          name="Biologic MIKE"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "fishing",
          name="Banda fishing boat", route=[(-5.5, 130.4, 0)], telegraph=2),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="05", key="Warramunga's Shot", place="Timor corridor",
    intro="One frigate, one salvo, a target beyond the horizon - and a convoy "
          "behind you that the shot is actually for.",
    sender="Commodore Alex Mercer",
    intent=("The frigate has the shot. The escort fired on a convoy under "
            "protection in daylight, and that changes what you may do to it. "
            "The convoy behind you is what the shot is for; the transport is "
            "not. If it turns north, let it. Come out with rounds left - "
            "Thursday needs them."),
    date=(2028, 10, 30), time=(14, 10), sea=4, clouds="Overcast", wind="SE",
    difficulty=3, minutes=55, centre=(-9.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR CORRIDOR. A surface action group is working south-east down "
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
    # sag#1 is the Sovremenny. With both hulls counted, sinking the unarmed
    # transport won "neutralise the armed escort".
    victory=dict(kind="destroy", stations=["sag#1"], min_units=1,
                 objective="Escort"),
    # Losing the frigate ends it. It used to fail one objective and play on
    # with four merchants as the surviving Taskforce1.
    fatal=[F("Convoy", ["convoy"], 2), F("Magazine", ["warramunga"])],
    neutral_objective="Convoy",
    win="The escort is burning and the transport has turned north. The convoy "
        "passed behind you while it happened, which was the entire point.",
    lose="Warramunga is gone or the lane is closed. Either way nothing moves "
         "through this corridor tomorrow. Captain Prasetyo's report to Jakarta "
         "will be short, and it will be accurate.",
    stations={
        # "Sixty miles on their disengaged bow" - now sixty, not thirty-four
        # inside the Moskit envelope. The SAG steams for the convoy, which is
        # ten miles behind the frigate instead of 147 NM from anything; the
        # Seahawk starts on the frigate's disengaged quarter, not 16.7 NM
        # from a weapons-free Sovremenny whose SA-N-7 reaches 16.2; and there
        # is traffic in the lane for the identification premise to be about.
        "warramunga": S(-10.2, 131.7, "HMAS Warramunga", heading=310),
        "sag": S(-9.4, 131.1, "Opposing surface group", heading=140),
        "convoy": S(-10.3, 131.85, "Protected convoy", heading=70),
        "lane": S(-9.9, 131.4, "Corridor traffic", heading=70),
        "red_air": S(-8.6, 131.9, "Maritime strike flight", heading=200,
                     alt=24000),
        "helo": S(-9.3, 131.3, "Shipborne flight", heading=180, alt=3000),
        "air": S(-10.35, 131.85, "Warramunga Flight", heading=320, alt=3000),
        "home": S(-14.5212, 132.3778, "RAAF Base Tindal"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "warramunga",
          variant="Variant3", name="HMAS Warramunga"),
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "air",
          name="Warramunga Flight", alt=3000),
        U("red", "chinese-navy-plan", "plan_em_sovremenny", "sag",
          name="Opposing escort", route=[(-10.3, 131.85, 0)], telegraph=3),
        U("red", "type-071-lpd", "plan_lpd_type_071", "sag",
          name="Amphibious transport", route=[(-10.3, 131.85, 0)], telegraph=3),
        U("red", "type-071-lpd", "planaf_z-20j", "helo", name="Transport flight"),
        U("red", "z-21", "pla_z21", "helo", name="Escort flight", alt=2500),
        # A maritime strike regiment that can strike: the default fit is four
        # short-range air-to-air missiles and three tanks.
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike flight lead",
          loadout="AntiShip"),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike flight two",
          loadout="AntiShip"),
        U("neutral", "re-power-resupply", "civ_ms_freighter_b", "lane",
          name="MV Kupang Trader", route=[(-9.7, 132.2, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_ritina", "lane",
          name="MT Banda Spirit", route=[(-9.75, 132.1, 0)], telegraph=3),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_roro_a", "convoy",
          name="MV Darwin Ranger"),
        U("blue", "re-power-resupply", "civ_ms_freighter_b", "convoy",
          name="MV Sunda Relief"),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy",
          name="MT Timor Spirit"),
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "air"),
        U("blue", "raaf-f-35a", "raaf_f-35a", "air"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_tindal", "home",
          name="RAAF Base Tindal", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="06", key="Blind Horizon", place="Arafura Sea",
    intro="The destroyer can defend what it can see. Everything past that is "
          "one aircraft, and they are coming for it.",
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for the air plan",
    intent=("The Triton is the only thing that can find the surface group. "
            "It is also the only Triton. Push her north and you fight "
            "tomorrow with a picture; hold her south and you fight today on "
            "a destroyer's horizon, and the picture costs you at the "
            "debrief. Both are decisions. Not making one is not."),
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
        "Classify that surface group and it stays on your plot for the rest of "
        "the morning. To do it the Triton has to go north, into the part of "
        "the sky the J-16s own. Hold her south and she lives, and HOBART "
        "fights on her own horizon.\\n\\n"
        "Two Tindal F-35As are your entire air cover. You can spend them "
        "protecting the orbit or holding close escort on the convoy. You "
        "cannot do both, and whatever you lose today you do not have "
        "tomorrow.\\n\\n"
        "If the group is classified, expect the picture to raise a question it "
        "does not answer, and expect it while the Triton is still north."),
    forces="HMAS Hobart, two RAAF F-35A off Tindal, one MQ-4C Triton, a "
           "Wedgetail on a long orbit. Opposing: two J-16, a Y-20 shuttling "
           "into the enclave, and a surface group not yet located.",
    objectives=[
        ("Convoy", "The convoy reaches its passage window", "30,-30,Fail,Main"),
        # Fail at the end if never done: holding the Triton south is a
        # playable choice, and it costs fifteen. It used to resolve Complete
        # for +25 whether the group was ever seen or not.
        ("Picture", "Classify the northern surface group", "25,-15,Fail"),
        ("Sentry", "Keep the Triton flying", "25,-25,Complete"),
        ("Hobart", "Hobart survives", "10,-20,Complete"),
        # Not on the player's list at briefing. Classifying the surface group
        # is what puts it there, which is the second reconnaissance decision:
        # the Triton is already north and the clock is already running.
        # `None` with a zero failure score: the native pairing for a hidden
        # optional task (9 of the 11 uses of None in the shipped missions look
        # exactly like this). Win without ever revealing it and it resolves to
        # nothing, which is the truth - there was no task.
        ("Airlift", "Identify the transport running into the enclave",
         "20,0,None,Hidden"),
    ],
    # The reconnaissance decision, and the reason this mission exists. Push the
    # Triton north far enough to classify the surface group and it is revealed
    # for the rest of the mission - Hobart fights with a picture. Keep the
    # Triton south where the J-16s cannot reach it and the convoy runs on the
    # destroyer's own horizon. Both are playable; neither is free.
    reveals={"Picture": dict(units=["red_sag", "red_air"], level="Identify",
                             seconds=-1,
                             intel="Sentry 06 has the northern group classified: "
                                   "two escorts on a south-westerly course, with "
                                   "the fighters that came for her now on your "
                                   "plot. The picture holds for the rest of the "
                                   "operation.")},
    victory=dict(kind="arrive", station="convoy", at=(-11.9, 130.6), radius=30,
                 min_units=2, objective="Convoy"),
    # Losing the Triton is a COST - the objective fails, the intel says what
    # it means for tomorrow, and SW11 starts with a worse picture. It was an
    # instant red victory that cancelled the main objective, which nothing
    # in the text, the bible or the design ever intended.
    fatal=[],
    neutral_objective="Convoy",
    win="The convoy is through the window and Sentry 06 is on its way back to "
        "Tindal with the surface picture. Tomorrow starts with information.",
    lose="The orbit is gone. Everything north of the horizon is now a rumour, "
         "and the convoy is inside somebody's launch basket.",
    stations={
        "hobart": S(-10.5, 132.0, "HMAS Hobart", heading=250),
        "convoy": S(-10.6, 132.1, "Convoy", heading=250),
        # South of the fighters' reach at the start (PL-15 108 NM; the J-16s
        # are 113 NM from here), so "hold her south" is a real state and
        # "push her north" is a decision the player makes, not one the AI
        # makes for them in the first seven minutes.
        "isr": S(-9.8, 132.4, "Sentry orbit", heading=90, alt=50000),
        "cap": S(-10.2, 132.6, "Tindal CAP", heading=10, alt=30000),
        "aew": S(-11.6, 132.2, "Wedgetail orbit", heading=90, alt=32000),
        "tindal": S(-14.5, 132.5, "RAAF Base Tindal", heading=0),
        "red_air": S(-8.0, 133.0, "Enclave fighters", heading=180, alt=34000),
        # Inbound to the enclave, which is NORTH of the fighters' field - it
        # used to fly south-west, away from it, through the CAP and into
        # Hobart's SAM envelope. Now it comes up from the south-east, well
        # east of anything Hobart can reach, and the Triton has to be north
        # to see it.
        "red_lift": S(-8.6, 134.2, "Enclave shuttle track", heading=330,
                      alt=28000),
        # 104 NM from Hobart and steaming for the convoy: YJ-83 reach plus an
        # hour at 24 kn is 109. It was 204 NM away and stationary, so the
        # "launch basket" the defeat text talks about did not exist.
        "red_sag": S(-9.1, 132.7, "Opposing surface group", heading=235),
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
        # A patrol box south of their field: they hold it, and the orbit that
        # crosses into it is the orbit that gets shot at.
        U("red", "j-16-multirole", "plaaf_j16", "red_air", name="Enclave 11",
          route=[(-8.4, 133.3, 34000), (-8.2, 132.7, 34000)]),
        U("red", "j-16-multirole", "plaaf_j16", "red_air", name="Enclave 12",
          route=[(-8.2, 132.7, 34000), (-8.4, 133.3, 34000)]),
        U("red", "y-20-kj-3000", "plaaf_y-20a", "red_lift", name="Shuttle 40",
          alt=28000, weapons="Hold", route=[(-6.2, 133.9, 28000)]),
        # Named by class - which is what an Identify-level reveal shows - not
        # "north" and "south", which the formation put the wrong way round.
        U("red", "chinese-navy-plan", "plan_ddg_luda_typ_051dt", "red_sag",
          name="Luda destroyer", route=[(-10.3, 132.3, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_sag",
          name="Type 054A frigate", route=[(-10.3, 132.3, 0)], telegraph=3),
    ],
))

MISSIONS.append(dict(
    group="core", num="07", key="Long Way Home", place="Northern air corridor",
    intro="A tanker with everybody's fuel on board, a flight that has none "
          "left, and interceptors that can out-reach all of it.",
    sender="Wing Commander Daniel Ward, Air Component, RAAF Tindal",
    intent=("This is a recovery, not a sweep. The tanker is the mission. The "
            "package needs it, the interceptors know where it is, and "
            "Wedgetail can see them coming but cannot stop them. Nothing you "
            "shoot down today is worth the tanker."),
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
    fatal=[F("Tanker", ["tanker"]), F("Package", ["package"])],
    neutral_objective="Package",
    win="The tanker is south of the line and the package is behind it. Both "
        "Foxhounds turned back with nothing to show a staff officer.",
    lose="The tanker is down. Every sortie in the north tomorrow gets shorter, "
         "and the ones over the enclave do not happen at all.",
    stations={
        "tanker": S(-7.2, 133.0, "Texaco 41", heading=200, alt=26000),
        "package": S(-6.6, 133.2, "Returning package", heading=200, alt=28000),
        "cap": S(-6.9, 133.4, "Raptor pair", heading=20, alt=40000),
        "red_air": S(-5.6, 132.6, "Interceptor pair", heading=170, alt=52000),
        "red_support": S(-4.5, 130.2, "Support orbit", heading=180, alt=30000),
        "picket": S(-7.6, 133.4, "Surface picket", heading=270),
        "home": S(-12.409, 130.8665, "RAAF Base Darwin"),
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
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="08", key="The Open Door", place="Contested enclave",
    intro="Open a relief window over an airfield somebody else's advisers are "
          "defending. The window is the objective, not the airfield.",
    sender="Commodore Alex Mercer",
    intent=("The window is the objective. Two transports through and the "
            "first hundred people out. A battery off the air for two hours "
            "beats a battery destroyed for the price of the strike package. "
            "When the window closes, come home."),
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
    fatal=[F("Window", ["relief"])],
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
        # The deck this strike always implied. The nearest Australian
        # field is Scherger, 707 NM south - outside an F-35A's 547 NM
        # radius and outside a Growler's 506 - so the package had
        # nowhere to come back to and was quietly given infinite fuel
        # instead. A carrier 103 NM off the target is what a strike on
        # this enclave would actually be flown from.
        "cvn": S(-4.3133, 135.8867, "Carrier group"),
    },
    units=[
        # No home field: the nearest Australian base is Scherger, 707 NM
        # south, which is not a sortie. These aircraft keep unlimited fuel -
        # the game's own tooltip prescribes exactly that when no airbase is
        # available, and a base on the map that nothing can reach is worse
        # than none.
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
        U("blue", "modern-us-navy", "usn_cvn_nimitz_2025", "cvn",
          name="USS Theodore Roosevelt"),
    ],
))

MISSIONS.append(dict(
    group="core", num="09", key="Southern Lifeline", place="Rear support area",
    intro="A submarine on the surface alongside a supply ship, which is the "
          "most vulnerable thing either of them will ever do.",
    sender="Commodore Alex Mercer; Commander Mara Kila for the eastern route",
    intent=("Supply and Collins, in the same box, for the service period, "
            "and then out. Every boat in the north depends on this "
            "rendezvous working. A scout is coming to look at it and a raid "
            "may follow it. The window is the win."),
    date=(2028, 11, 11), time=(6, 30), sea=2, clouds="Broken_2", wind="SE",
    difficulty=3, minutes=65, centre=(-12.5, 146.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "REAR SUPPORT AREA, east of the Cape. COLLINS has been out for "
        "thirty-one days and comes home on Thursday whatever happens today. "
        "She is surfaced alongside SUPPLY taking fuel, stores and two crew off "
        "for medical, and while she is up there she is a very large grey "
        "target moving at eight knots.\\n\\n"
        # The engine has no dwell, alongside, surfaced or service predicate -
        # eleven condition types across the whole shipped corpus and not one
        # of them measures time spent in an area, a unit's speed or its depth.
        # So the briefing states the rule the mission actually enforces. The
        # replenishment itself stays fiction, in the fiction's own voice.
        "The service window is thirty-five minutes and it runs on the clock, "
        "not on how much crossed the hose. Break off to chase something and "
        "the clock does not stop for you - what you lose is the part of the "
        "transfer nobody makes, not the deadline. When the thirty-five "
        "minutes are up, SUPPLY and COLLINS come south together or the "
        "window has failed.\\n\\n"
        "A Tu-214R came down the outside of the box last night and did not "
        "come back, which usually means somebody now knows where to look. "
        "There is an Akula unaccounted for and a Flanker pair within range of "
        "here. Keep the window open and get everybody out of it."),
    forces="HMAS Supply, HMAS Collins surfaced for service, HMAS Perth and a "
           "Seahawk. Opposing: one Akula, one Tu-214R, a Flanker pair with a "
           "Ka-27RLD spotting for them.",
    objectives=[
        ("Service", "Bring SUPPLY and COLLINS south together once the "
                    "35-minute window has run", "35,-35,Fail,Main"),
        ("Collins", "HMAS Collins must survive", "25,-35,Complete"),
        ("Supply", "HMAS Supply must survive", "20,-30,Complete"),
    ],
    # Supply AND Collins, not "any two of the group" - the freighter could
    # otherwise stand in for the submarine the mission is about. The time
    # condition is the service window: withdrawing early does not count.
    victory=dict(kind="arrive", units=["support#1", "support#2"], min_units=2,
                 station="support", objective="Service",
                 also=[dict(after_minutes=35)]),
    # Both named service participants end the mission, each failing its own
    # objective. Coral Provider is not one of them: she carries no objective,
    # she only spawns when SUPPLY survived Steel Highway, and making her a
    # silent third defeat condition meant losing a freighter reported Collins
    # sunk while Collins was alongside.
    # Each named participant ends the mission by being lost, and fails its own
    # objective. MV Coral Provider is deliberately not here: she carries no
    # objective, she only exists when SUPPLY survived Steel Highway, and as
    # the third member of the "support" station she was a silent defeat
    # condition that reported Collins sunk while Collins was alongside.
    fatal=[F("Collins", ["support#2"]), F("Supply", ["support#1"])],
    neutral_objective="Service",
    win="The window held, Collins is dived and heading for Stirling, and "
        "Supply still has enough in her tanks to do this again next week. Kila, "
        "from Moresby: 'Send the next one.'",
    lose="The support group is broken. Every boat in the north now has to come "
         "all the way home to do what should take four hours out here.",
    stations={
        "support": S(-13.5, 148.4, "Support group", heading=200),
        "escort": S(-13.6, 148.6, "Escort", heading=200),
        "air": S(-13.0, 148.2, "Perth Flight", heading=90, alt=3000),
        "cape": S(-12.5, 142.0, "Cape York strip", heading=0),
        "red_sub": S(-16.5, 150.0, "Akula datum", heading=320),
        "red_air": S(-11.0, 148.0, "Opposing aviation", heading=180, alt=30000),
        "home": S(-12.6188, 142.094, "RAAF Base Scherger"),
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
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        U("blue", "p-8-poseidon", "usn_p8", "air"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_scherger", "home",
          name="RAAF Base Scherger", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="10", key="Common Sea", place="Eastern Banda corridor",
    intro="A Japanese ASW detachment brings the one thing the Australian "
          "force has run out of: escorts that can hunt.",
    sender="Commodore Alex Mercer",
    intent=("The Japanese detachment brings the thing we ran out of: escorts "
            "that can hunt. Use them for that. The convoy is the cargo, the "
            "submarine is theirs, the surface threat is yours. Bring both "
            "allied hulls home - Thursday needs them too."),
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
    fatal=[F("Cargo", ["convoy"], 2)],
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
        "f2": S(-5.6, 133.0, "Kai detachment CAP", heading=180, alt=26000),
        "red_sub": S(-8.4, 134.4, "Submarine datum", heading=20),
        "red_air": S(-5.4, 133.2, "Enclave fighters", heading=180, alt=32000),
        "kai": S(-7.0, 134.0, "Kai Islands", heading=0),
        "home": S(-12.409, 130.8665, "RAAF Base Darwin"),
        # The detachment's own strip. The station was already labelled a
        # detachment, but nothing it flew from was ever placed, so the
        # F-2As were homed on Darwin 428 NM away - against 900 NM of
        # total range, which is 856 NM of transit with nothing left for
        # the orbit they are there to fly.
        "strip": S(-5.2953, 132.9232, "Forward strip, Kai group"),
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
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        U("blue", "p-8-poseidon", "usn_p8", "helo"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
        U("blue", "_vanilla", "airfield_small_1", "strip",
          name="Langgur forward strip", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="11", key="Fujian's Shadow", place="Wider Banda approaches",
    intro="The carrier group has come to close the corridor for the "
          "negotiating period. You do not have to sink it. You have to keep "
          "the transports alive through it.",
    sender="Commodore Alex Mercer",
    intent=("The carrier group has come to close the corridor for the talks. "
            "You do not have to sink it. Keep the transports moving and Ford "
            "alive until the window, and let the enemy spend fuel he cannot "
            "replace coming to you. He knows this. His own signals say so."),
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
           "J-35 and J-15D, Liaoning, a J-20 and a KJ-600.",
    objectives=[
        ("Transports", "The transport group must pass to the south-east",
         "40,-40,Fail,Main"),
        ("Ford", "USS Gerald R. Ford survives the window", "30,-40,Complete"),
        ("Strike", "Break up the opposing strike", "15,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="transports", at=(-7.0, 130.0),
                 radius=35, min_units=2, objective="Transports"),
    fatal=[F("Ford", ["carrier"])],
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
        "red_sub": S(-4.9, 129.2, "Submarine screen", heading=140),
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
        # NOT Lae Provider: the contingency after STEEL HIGHWAY opens with her
        # going down at 2140 with twenty-six aboard, and that beat is offered
        # unconditionally. A sunk ship cannot be carrying cargo nine missions
        # later, whether or not the player flew the search for her.
        U("blue", "re-power-resupply", "civ_ms_andizhan", "transports",
          name="MV Moresby Star"),
        U("red", "fujian-cv-18", "plan_cv_type_003", "red_cv", name="PLANS Fujian"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv",
          name="PLANS Liaoning"),
        U("red", "modern-plan-systems", "plan_type_055_2026", "red_cv",
          name="Type 055 escort"),
        U("red", "modern-plan-systems", "plan_type_052d_p3", "red_cv",
          name="Type 052D escort"),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A escort"),
        # A carrier group without a submarine screen is a missile exchange.
        # This is the campaign's one fleet action; it should be the mission
        # where the player cannot watch every axis at once.
        U("red", "plan-submarines", "plan_ssn_type_093b", "red_sub",
          name="Contact ROMEO"),
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
    sender="Commodore Alex Mercer",
    intent=("Coral Pioneer, nine knots, one shaft. One group out there is "
            "complying with the ceasefire and one is deciding whether to. "
            "Tell them apart before you fire, because the ceasefire is the "
            "campaign, and a mistake tonight reopens all of it."),
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
    fatal=[F("Convoy", ["convoy"], 2)],
    neutral_objective="Ceasefire",
    win="Coral Pioneer is alongside at Darwin on one shaft and the rest of the "
        "convoy is behind her. The withdrawing group went north and nobody "
        "shot at it. The route is a route again. Santos's log, 0410: "
        "'Alongside. One shaft. All hands.'",
    lose="The first ship through did not get through, and the ceasefire is "
         "now a thing that was tried once.",
    stations={
        "escort": S(-10.48, 131.77, "Escort group", heading=200),
        "convoy": S(-10.4, 131.8, "First convoy", heading=200),
        "air": S(-10.8, 131.0, "Air support", heading=200, alt=20000),
        "aew": S(-11.5, 130.8, "Wedgetail orbit", heading=90, alt=32000),
        # 30 NM off the convoy's bow and opening at 340: close enough that
        # the player has to tell it from the spoiler and hold fire on it,
        # which is the mission. It used to be 73 NM away.
        "withdraw": S(-10.02, 131.47, "Withdrawing group", heading=340),
        "spoiler": S(-9.1, 131.9, "Unacknowledged group", heading=180),
        "spoiler_air": S(-9.2, 132.0, "Strike flight", heading=180, alt=24000),
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
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        U("blue", "mh-60r-2154545636", "usn_mh-60r", "air"),
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
    sender="Captain (N) Elin Vasse, European escort rotation",
    intent=("The oiler is the group. Everything east of here plans around "
            "what is in her tanks. The shadowers are looking for a reason; "
            "do not give them one, and do not let them get close enough to "
            "find one on their own."),
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
    fatal=[F("Oiler", ["group"])],
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
        "red_air": S(-10.7, 125.05, "Shadowers", heading=200, alt=28000),
        "home": S(-17.5813, 123.8283, "RAAF Base Curtin"),
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
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_curtin", "home",
          name="RAAF Base Curtin", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D2", key="Flight Deck Day", place="Coral Sea",
    intro="Allied Dispatch. A recovery cycle, a deck that has to keep working, "
          "and nobody shooting at anybody if the day goes well.",
    sender="Rear Admiral C. Halvorsen, Carrier Strike Group, Coral Sea",
    intent=("Keep the deck cycling and get the visitor aboard. The tanker is "
            "the schedule. Nobody shoots at anybody today if the day goes "
            "well - and the day goes well if the drifting contact stays a "
            "drifting contact."),
    date=(2028, 11, 13), time=(15, 0), sea=3, clouds="Scattered_1", wind="SE",
    difficulty=1, minutes=55, centre=(-15.5, 149.5),
    blue_nation="USA", red_nation="Russia",
    brief=(
        "CORAL SEA. Three carriers are working the same box: one recovering a "
        "long-range package, one running deck drills with a new air department "
        "and one cycling alert aircraft. "
        "A Seawolf is riding shotgun below and an E-3G is holding the wider "
        "picture while the Wedgetail is off task.\\n\\n"
        "The tanker is the schedule. Everything airborne today is planned "
        "around one KC-10, and the Reaper on the southern track is watching a "
        "merchant that has been drifting off its filed route for two days.\\n\\n"
        "There is a distinguished-visitor lift inbound - a VH-3D bringing the "
        "coalition maritime commander across for the afternoon. That airframe "
        "gets deck priority over everything else that is not on fire. Keep the "
        "cycle running and get the visitor aboard."),
    forces="USS Nimitz, Carl Vinson and Theodore Roosevelt with the 2000s-era "
           "Nimitz air-deck group, one Seawolf, "
           "an E-3G, a KC-10A, an MQ-9A on the southern track and a VH-3D on "
           "the visit.",
    objectives=[
        ("Visit", "Get the VH-3D into the carrier box", "25,-20,Fail,Main"),
        ("Cycle", "Keep the carriers operating", "20,-25,Complete"),
        ("Tanker", "Do not lose the tanker", "10,-10,Complete"),
        ("Neutrals", "Harm no neutral shipping or aircraft", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="visit", at=(-15.6, 149.6), radius=15,
                 min_units=1, objective="Visit"),
    fatal=[F("Cycle", ["carriers"])],
    neutral_objective="Neutrals",
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
    sender="Capitaine de vaisseau A. Mercier, Groupe amphibie",
    intent=("Land the relief and open the distribution point. The port never "
            "changed hands; the roads to it did. The people on those roads "
            "are why we are here, and they are not a target from any angle."),
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
    fatal=[F("Group", ["group"])],
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
    sender="Opposing task group commander, to his own force",
    intent=("You are the other side. The auxiliary took a torpedo forward "
            "eleven days ago and has made six knots since. Get her home. The "
            "coalition escort is professional and it does not chase; it will "
            "not start today unless you give it a reason."),
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
    fatal=[F("Auxiliary", ["auxiliary"])],
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
    sender="Trials Director, Northern Territory Ranges",
    intent=("This is a trial, not a battle. Three of four pads down, the "
            "anti-ship serial into the seaward target, and nothing outside "
            "the danger area. The batteries are the serial; losing one ends "
            "it."),
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
        # The loss rule below ends the exercise the moment ONE of the four
        # defence units is destroyed. That was true before this objective
        # existed too - it just went unannounced, and the defeat was reported
        # as a failure to destroy the enemy's pads, which is a different
        # exercise entirely. An unstated loss condition is not difficulty.
        ("Battery", "Keep all four defence batteries in action",
         "0,-30,Complete"),
    ],
    victory=dict(kind="destroy", stations=["pads"], min_units=3,
                 objective="Pads"),
    fatal=[F("Battery", ["battery"])],
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
    sender="Air Component, 2034 - openly speculative",
    intent=("None of this is real and none of it is a forecast. The stream "
            "releases on the complex or it does not. Get the escorts home "
            "either way; even in fiction, range is range."),
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
    fatal=[F("Stream", ["stream"])],
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
        "sea": S(-4.6, 131.95, "Offshore picket", heading=270),
        "cvn": S(-5.4, 132.2, "Ford", heading=330),
        "home": S(-12.5212, 131.0, "RAAF Base Darwin"),
    },
    units=[
        U("blue", "yf-23-black-widow-ii", "usaf_yf-23_black_widow_ii", "escort",
          name="Black Widow 11"),
        U("blue", "yf-23-black-widow-ii", "usaf_yf-23_black_widow_ii", "escort",
          name="Black Widow 12"),
        # Long Reach is a strike mission and the Eagle II flies a strike fit.
        # It also has to: the f-15ex mod is reached through the targeting pod
        # its strike loadouts hang, and the default air-to-air fit hangs
        # nothing of that mod's at all.
        U("blue", "f-15ex", "usaf_f-15ex_SEII", "escort", name="Eagle II 21",
          loadout="StrikePrecision"),
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
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
        # The escorts had 495 NM to Darwin against radii of 360 to 480,
        # and one of them is a Rafale MARINE - a carrier aeroplane with
        # no carrier. The offshore picket station was already here and
        # empty; 70 NM from the escort track, it covers all five.
        U("blue", "ford-cvn", "usn_cvn_ford_jsf", "cvn",
          name="USS Enterprise"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D7", key="Before the Lifeline",
    place="Darwin approaches, 1988",
    intro="Cold Sea. A 1988 exercise in the same water, forty years before the "
          "campaign - the collection's retired aircraft where they belong.",
    sender="Exercise Director, PITCH BLACK 88, maritime phase",
    intent=("July 1988. The strike serial is broken outside its release line "
            "or the umpires score it against you. Nobody is shooting "
            "anything real. Everybody flies home."),
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
    fatal=[F("Recovery", ["high"])],
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
    sender="Lieutenant Colonel R. Okafor, US ground-support package",
    intent=("The column reaches the airhead. The road is the corridor; the "
            "corridor is the relief. Hold the perimeter open after the "
            "enclave window closes, and bring the gunship home with fuel to "
            "spare."),
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
    fatal=[F("Gunship", ["support"])],
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
        # The perimeter threat sits ON the column's route - the only proven
        # ground in this theatre is around the column - instead of 156 NM
        # up-country where a 6 NM SAM covers nothing.
        "ridge": S(-8.55, 140.40, "Covered ridge", heading=120),
        "red_air": S(-8.1, 139.8, "Opposing fighter", heading=150, alt=30000),
        "home": S(-12.6188, 142.094, "RAAF Base Scherger"),
        # A perimeter operation flies from the perimeter. Everything here
        # was homed on Scherger 370 NM back - inside a Warthog's legs
        # and outside a Viper's, and a long way to send an Apache.
        "strip": S(-8.5165, 140.4812, "Forward airstrip"),
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
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_scherger", "home",
          name="RAAF Base Scherger", nation="australia", weapons="Hold"),
        U("blue", "_vanilla", "airfield_small_1", "strip",
          name="Forward airstrip", weapons="Hold"),
    ],
))

# Every series label here is followed by the missions it covers, by the names
# the browser actually lists them under. It used to name five series -
# "Allied Dispatches", "Red Line", "Future Front", "Cold Sea" - that appear on
# no mission a player can see: they live in each mission's `intro`, which is a
# campaign-map field, and the dispatches are browser entries with no campaign
# map. A folder description that names things the folder does not contain
# reads as a list of missing content.
DISPATCH_DESC = (
    "Eight optional episodes outside the twelve-mission Southern Watch spine, "
    "each stating its own fiction in the briefing. "
    "Allied Dispatch - Western Passage, Flight Deck Day, The Relief Ship and "
    "The Long Perimeter - rotates a European, French/Spanish or US detachment "
    "through the same crisis. Return Passage plays the opposing side's "
    "logistics problem. Range Week fires the missile-defence and ballistic "
    "systems where such things are actually fired. Long Reach is an openly "
    "speculative 2034 branch for the collection's experimental aircraft and "
    "weapons. Before the Lifeline is a 1988 exercise in the same water, for "
    "its retired types.")


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
    sender="Commodore Alex Mercer",
    intent=("One coaster, one search, last light. Find her before the "
            "weather does. Nothing out there is worth a helicopter."),
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
    # The objective is the helicopter and the resolver watches the helicopter;
    # this used to watch HMAS Arafura, so losing the ship ended the mission
    # reporting that the search aircraft was lost. Units=None makes the fatal
    # trigger read the objective's own resolver, which is the only way the two
    # cannot drift apart again.
    fatal=[F("Aircraft")],
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
    # MissionSpecialNote is a player-facing panel on the campaign map - stock
    # uses it for "Note: This is a detached submarine operation." The second
    # half of this note used to explain which engine feature the author could
    # not implement, which is a build note wearing a briefing's clothes. Why
    # the unlock is unconditional belongs in the build notes, and is there.
    special="Recovery operation. It pays no requisition points: it saves "
            "people and changes the debrief, and it does not restore the ship "
            "or its cargo. NOTE: this is offered after STEEL HIGHWAY whatever "
            "happened there.",
    sender="Commodore Alex Mercer",
    intent=("This one pays nothing and I would fly it anyway. Work the box "
            "to its northern edge. Bring the helicopter home. The people we "
            "do not find today we will not find."),
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
        ("Assist", "Do not lose an assisting merchant or harm other traffic",
         "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="search", at=(-12.6, 148.2), radius=25,
                 min_units=1, objective="Survivors"),
    # Same defect O1 had: this watched HMAS Hobart while the objective is the
    # recovery helicopter. The resolver is the source of truth.
    fatal=[F("Helicopter")],
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
     ["Warramunga's report of the Arafura rendezvous went to Canberra inside "
      "an hour and came back the next morning as a standing task. There is "
      "now an Australian maritime task group, it has a name, and it has an "
      "escort group forming around whichever hulls came back from the Coral "
      "Sea.",
      "Port Moresby's engineering plant is ashore. Commander Kila's message "
      "on arrival was three words long and is not printable in a family "
      "newspaper. The Pukpuk access arrangements are being read carefully, "
      "by people who had not read them before, in three capitals.",
      "The Indonesian patrol vessel that challenged the escort on the "
      "eighteenth has been credited, publicly, by Jakarta. The escort has not "
      "been named. Meridian's statement refers to \"a misunderstanding at "
      "sea\" and announces expanded safety-escort coverage \"in response to "
      "client demand\".",
      "The task group's next request comes from an offshore platform, and it "
      "is not a Meridian one."],
     "Rig Seventeen"),
    ("31 October 2028", "Chapter 2 closes", "The network behind the incidents",
     "SOMEBODY IS SUPPLYING THEM",
     ["The platform crews are ashore in Darwin and Kupang. The low-profile "
      "craft tracked into the Banda approaches is in a shed with "
      "photographers around it, and what it was carrying matters less than "
      "where it was going: a Meridian terminal that had been declared closed "
      "for a month.",
      "Two of the supply routes now have names on a chart. The people running "
      "them do not. The Meridian duty controller net went off the air on "
      "Tuesday and has not come back, which the intelligence staff regard as "
      "the most informative thing it has ever done.",
      "Meridian's board has issued a statement disowning \"unauthorised "
      "actions by a security subsidiary\". Its hard-line faction has issued "
      "nothing, holds a service platform and several logistics sites, and "
      "has not disarmed when told to. One airfield-and-port enclave has not "
      "been recovered.",
      "The task group's next convoy sails Wednesday. The escort that fired on "
      "the eighteenth has been seen again, and it has not changed its ways."],
     "Warramunga's Shot"),
    ("7 November 2028", "Chapter 3 closes", "Overt attacks begin",
     "THIS IS NO LONGER DENIABLE",
     ["An armed escort fired on a protected convoy in daylight on the second, "
      "and a Royal Australian Navy frigate answered. The recordings from "
      "three platforms are unambiguous and the diplomatic language changed "
      "the same afternoon. Nobody is calling it a misunderstanding.",
      "A naval force has arrived in the northern approaches under what its "
      "government describes as a protection-and-evacuation mission, and has "
      "demanded that coalition patrols suspend. The demand has been declined. "
      "The force has not gone home. Commodore Mercer's assessment to "
      "Canberra, which has leaked in the way these things do, was one line: "
      "\"They can close the lane for a month. They cannot hold it for two.\"",
      "Growler and wider surveillance allocations are released to the task "
      "group from Monday. What this week has established, and what the "
      "ledger will record, is that damage and magazine expenditure are no "
      "longer things the force can simply absorb between operations.",
      "The next problem is not a ship. It is a tanker, and how many aircraft "
      "are depending on it at once."],
     "Long Way Home"),
    ("14 November 2028", "Chapter 4 closes", "The corridor is open",
     "THE WINDOW HELD",
     ["The relief movement is out of the enclave. The first hundred people "
      "were on the ground at Tindal before the battery that covered the field "
      "had finished being surprised. The negotiation that follows starts from "
      "a better place than the one that would have followed a closed window, "
      "and the negotiators know it.",
      "Commander Kila's report from the eastern route reads, in full: \"Road "
      "open. Column through. Send the next one.\" The Port Moresby plant is "
      "running and the hospital is off generator, which is the first sentence "
      "in this campaign a civilian would recognise as a result.",
      "Tanker hours, not hulls, were the limiting factor this week. Wing "
      "Commander Ward has said so in writing, twice, and will be saying it "
      "again.",
      "The task group's replenishment ship has been at sea for three weeks. A "
      "submarine has been at sea for five. They are going to meet, and "
      "something is going to try to stop them."],
     "Southern Lifeline"),
    ("21 November 2028", "Chapter 5 closes", "The route is sustained",
     "THE LIFELINE HOLDS",
     ["The service window in the rear area held. The submarine that needed it "
      "is dived and heading for Stirling, and the replenishment group that "
      "gave it to her still has enough in her tanks to do it again, which was "
      "the point.",
      "A Japanese ASW detachment is on station in the eastern Banda "
      "approaches. For the first time since October the corridor has two "
      "escort forces that can hunt, and the convoy that went through on the "
      "twentieth was the first in a month to arrive with every hull it "
      "sailed with.",
      "The opposing task group has moved south. Its carrier and its escorts "
      "are now inside the box the corridor runs through, and the talks that "
      "were supposed to open Thursday have been moved to Saturday to see what "
      "happens first. The Commodore's note to the force this morning did not "
      "mention the talks. It said: \"Keep the transports moving. Keep the "
      "high-value ship alive. Everything else is the enemy's problem.\"",
      "What the ledger says about the task group after five weeks, the ledger "
      "says. What it does not say is that the corridor closed. It did not."],
     "Fujian's Shadow"),
    ("27 November 2028", "Before the last passage", "An imperfect ceasefire",
     "ONE PASSAGE THAT MUST WORK",
     ["The talks opened with the corridor open, which is the only reason they "
      "opened at all. A ceasefire takes effect at midnight. Not every group "
      "in the box has acknowledged it, and one of the groups that has is not "
      "the one the intelligence staff are watching.",
      "Coral Pioneer is at the head of the first convoy through. Her master "
      "has declined a replacement ship, a replacement crew and, in writing, a "
      "replacement master. She has a bearing running hot and a chief engineer "
      "who says it will hold if nobody asks him how.",
      "The escorts that will take her through are the escorts that are left. "
      "The ledger has the list. What the list does not record is that every "
      "name on it has done this before, in this water, against these people, "
      "and that the people on the other side know it.",
      "Everything this campaign was about is in the next eight hours."],
     "The First Ship Through"),
]

for _i, (_date, _title, _sub, _head, _body, _before) in enumerate(SITREPS, 1):
    EVENTS.insert(_i, dict(file=f"{_i:02d}_sitrep", before=_before,
                           title=f"{_title}\\n{_date}", sub=_sub,
                           dateline=f"{_date.upper()}  |  MARITIME BORDER COMMAND, DARWIN",
                           headline=_head, body=_body))


# The cast, in the forms they write in. A liaison officer sends a cable, a
# master keeps a log, an intelligence cell writes an INTSUM, an intercept is
# transcribed. Pacific Strike tells its story in at least ten such forms; this
# campaign told its own in one. Every person, company, hull and incident here
# is invented. No page names a ship the player could have lost as alive: where
# a loss is possible the page speaks of the class or the role.
DOCUMENTS = [
    dict(file="00b_meridian_intsum", before="Steel Highway", form="intsum",
         title="What we know about Meridian\\n19 October 2028",
         sub="Coalition Joint Intelligence summary",
         org="Coalition Joint Intelligence Centre, Darwin", ref="INTSUM 028-41",
         date="19 October 2028", subject="Meridian Maritime Group",
         body=[
             "1. Meridian Maritime Group is a freight, port-services and "
             "maritime-security network operating across the Arafura, Banda "
             "and northern Coral Sea approaches. It has grown in two years from "
             "a terminal operator into the largest single router of commercial "
             "traffic in the region. Most of what it does is legal.",
             "2. Three components are relevant to the force:",
             "a. MERIDIAN LINES. Bulk carriers, coasters and one chartered "
             "ro-ro on published schedules. Assessed as ordinary commerce. NOT "
             "to be treated as hostile on the basis of flag or ownership.",
             "b. MERIDIAN SAFETY ESCORT SERVICES. Converted offshore supply "
             "vessels and at least two former naval hulls carrying armed "
             "boarding teams and military-grade communications. Assessed at "
             "five to eight vessels. Identification at range is NOT possible "
             "by silhouette: the hulls are the same classes as the commercial "
             "fleet. Behaviour - loitering on a merchant track, challenging on "
             "VHF 16, closing to inspect - is the indicator.",
             "c. THE DUTY CONTROLLER NET. A commercial HF/VHF net that assigns "
             "rendezvous, \"inspection\" points and terminal slots. Traffic "
             "analysis indicates it has also been assigning movements to "
             "vessels that are not Meridian's. How it obtained their schedules "
             "is under investigation.",
             "3. Assessment. The incidents of the past three weeks - missed "
             "reporting windows, contradictory movement instructions, two "
             "ports' cargo records lost - are consistent with a single actor "
             "shaping traffic toward escorted groups and preferred terminals. "
             "Whether that actor is Meridian's board, a faction within it, or "
             "a client using it, is NOT established.",
             "4. Guidance to the force. A Meridian-flagged contact is a "
             "contact. Classify it by what it does. The escort that fired on "
             "the Indonesian patrol yesterday was tracked as a commercial hull "
             "for six hours before it did."],
         note="Para 4 is the whole campaign.  - AM"),
    dict(file="00c_santos_log", before="Steel Highway", form="log",
         title="Master's log, MV Coral Pioneer\\n18 October 2028",
         sub="Deck log extract, the morning of the rendezvous",
         ship="MV Coral Pioneer", master="L. Santos", date="18 October 2028",
         entries=[
             ("0412", "Main engine casualty, No.2 turbocharger. Reduced to "
                      "6 kn. Informed convoy commodore (MV Gove Trader) and "
                      "Darwin."),
             ("0430", "Contact hailed us on Ch16 as \"Meridian Safety Escort "
                      "Seven\". Stated we were \"under safety inspection\" and "
                      "to heave to. Asked for authority. Was told it was "
                      "\"regional\". Declined."),
             ("0447", "Escort Seven closed to 2 cables. Armed party visible on "
                      "the bridge wing. Rendezvous with relief vessel now 40 "
                      "min overdue."),
             ("0455", "Indonesian patrol vessel on the horizon to the north, "
                      "challenging Escort Seven on Ch16."),
             ("0503", "Gunfire, bearing north. Not at us. Crew mustered below."),
             ("0510", "Escort Seven broke off and stood north. Lost visual in "
                      "haze."),
             ("0540", "Warship on radar to the south-west, closing fast. Have "
                      "not raised her. Chief Engineer says we can make 8 kn if "
                      "nobody asks him how.")],
         note="Note for owners: I did not heave to. I will not heave to for "
              "anyone whose authority is \"regional\". If that is now company "
              "policy, the company can find another master.  - L.S."),
    dict(file="00d_kila_cable", before="Steel Highway", form="signal",
         title="Port Moresby request\\n21 October 2028",
         sub="Signal from the PNGDF maritime liaison",
         header=[("FROM:", "CDR M. KILA, PNGDF MARITIME ELEMENT, PORT MORESBY"),
                 ("TO:", "COMAUSMARTG (CDRE MERCER)"),
                 ("DTG:", "210600Z OCT 28"), ("PREC:", "PRIORITY"),
                 ("SUBJ:", "PROTECTED DELIVERY, MORESBY")],
         body=[
             "1. MORESBY HOSPITAL IS ON GENERATOR. THE PLANT THAT REPLACES IT "
             "IS IN KOKODA STAR. THE FUEL FOR THE GENERATOR UNTIL THEN IS IN "
             "LAE PROVIDER. THAT IS THE ORDER OF PRIORITY IF YOU HAVE TO "
             "CHOOSE, AND I AM TOLD YOU MAY HAVE TO.", "",
             "2. A SUBMARINE REPORT WAS PASSED TO US THIS MORNING FROM A "
             "FISHING VESSEL OFF THE TRACK. UNCONFIRMED. THE MASTERS HAVE BEEN "
             "TOLD. THEY WANT TO SAIL ANYWAY. I HAVE NOT ARGUED.", "",
             "3. WE CAN OFFER A PATROL BOAT AT THE ENTRANCE AND NOTHING "
             "FURTHER OUT. WHAT HAPPENS BETWEEN THE ARAFURA AND OUR ENTRANCE "
             "IS YOURS.", "",
             "4. THIS REQUEST IS FOR ESCORT OF NAMED SHIPS ON A NAMED ROUTE. "
             "IT IS NOT AN INVITATION TO ANYTHING ELSE. PLEASE CONVEY THAT "
             "WHERE IT NEEDS CONVEYING.", "",
             "KILA"]),
    dict(file="01b_prasetyo_cable", before="Rig Seventeen", form="signal",
         title="Terms of assistance\\n25 October 2028",
         sub="Signal from the Indonesian naval liaison",
         header=[("FROM:", "CAPT R. PRASETYO, TNI-AL, LIAISON TO COMAUSMARTG"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "250400Z OCT 28"),
                 ("PREC:", "IMMEDIATE"),
                 ("SUBJ:", "RIG SEVENTEEN - TERMS OF ASSISTANCE")],
         body=[
             "1. THE PLATFORM IS IN INDONESIAN WATERS. THE REQUEST FOR "
             "ASSISTANCE IS FOR THE EVACUATION OF CIVILIAN CREW ONLY.", "",
             "2. AGREED: YOUR AIRCRAFT MAY OVERFLY THE PLATFORM AND LAND ON "
             "IT. YOUR SHIPS MAY OPERATE WITHIN THE BOX ON YOUR CHART. YOU MAY "
             "DEFEND YOUR AIRCRAFT AND THE PEOPLE THEY CARRY.", "",
             "3. NOT AGREED: ACTION AGAINST THE PLATFORM ITSELF. THERE ARE "
             "CONTRACTORS ON THE UPPER DECK WITH WEAPONS. THEY ARE, AS FAR AS "
             "WE KNOW, INDONESIAN NATIONALS EMPLOYED BY A MERIDIAN SUBSIDIARY. "
             "THEY ARE OUR PROBLEM, AFTERWARDS.", "",
             "4. A PATROL IS CLOSING FROM THE NORTH. IT IS NOT OURS. WE HAVE "
             "ASKED IT TO STAND OFF. IT HAS NOT ANSWERED.", "",
             "5. I WILL BE ON THE FLAGSHIP'S BRIDGE FOR THE DURATION. IF THE "
             "TERMS ABOVE BECOME IMPOSSIBLE TO KEEP, I WOULD RATHER HEAR IT "
             "FROM YOU THAN READ IT.", "",
             "PRASETYO"]),
    dict(file="02b_meridian_intercept", before="Warramunga's Shot",
         form="signal", strap="INTERCEPT",
         title="Intercept: Meridian net\\n1 November 2028",
         sub="Commercial HF, transcribed",
         header=[("NET:", "COMMERCIAL HF, 8291 KHZ"), ("DTG:", "010340Z NOV 28"),
                 ("NOTE:", "TRANSLATED / TRANSCRIBED. A: \"MERIDIAN CONTROL\". "
                           "B: \"ESCORT SEVEN\". PARTIAL.")],
         body=[
             "A:  Seven, Control. Your inspection point is confirmed for the "
             "morning. The group is four hulls plus one grey.",
             "B:  One grey. Say again the grey.",
             "A:  One warship. Same one as the eighteenth. You are to establish "
             "the inspection and hold the group until the northern element is "
             "in position. Do not engage the grey unless engaged.",
             "B:  Control, Seven. The grey engaged the last time. It will do "
             "it again.",
             "A:  Then you will have been engaged. Control out.",
             "B:  [unreadable] ... eight minutes ... [unreadable]"],
         note="\"The northern element\" is not a Meridian asset. Its identity "
              "is assessed as the surface group reported 30 OCT. Speaker A's "
              "traffic pattern matches the controller last heard 28 OCT before "
              "the net went silent. The net is not silent. It moved."),
    dict(file="03b_ward_memo", before="Long Way Home", form="signal",
         title="Air component note\\n8 November 2028",
         sub="What tomorrow's flying programme actually costs",
         header=[("FROM:", "WGCDR D. WARD, AIR COMPONENT, RAAF TINDAL"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "080500Z NOV 28"),
                 ("SUBJ:", "TOMORROW'S FLYING PROGRAMME - WHAT IT COSTS")],
         body=[
             "1. YOU HAVE ONE TANKER IN THE NORTH. NOT ONE TANKER TYPE. ONE "
             "TANKER. EVERY SORTIE PAST DARWIN'S RADIUS TOMORROW IS PLANNED "
             "AROUND IT BEING WHERE IT SAYS IT WILL BE, WHEN IT SAYS.", "",
             "2. THE PACKAGE RETURNING FROM THE NORTH-WEST WAS DIVERTED FOR "
             "WEATHER AND HAS SPENT ITS MARGIN. IT WILL NEED THE TANKER BEFORE "
             "IT CAN THINK ABOUT ANYTHING ELSE.", "",
             "3. THERE IS AN INTERCEPTOR SECTION OPERATING OUT OF THE ENCLAVE. "
             "IT KNOWS WHERE THE TANKER TRACK IS BECAUSE THE TANKER TRACK IS "
             "THE ONLY PLACE THE TANKER CAN BE.", "",
             "4. I AM NOT ASKING FOR A DECISION. I AM TELLING YOU THE SHAPE OF "
             "ONE: IF THE TANKER IS LOST, EVERY SORTIE IN THE NORTH GETS "
             "SHORTER FOR THE REST OF THE CAMPAIGN, AND SO DOES THE "
             "CAMPAIGN.", "",
             "5. WEDGETAIL IS ON A LONG ORBIT AND CAN SEE THE SECTION COME "
             "SOUTH. WHAT SHE CANNOT DO IS ANYTHING ABOUT IT.", "",
             "WARD"]),
    dict(file="05b_opposing_intercept", before="Fujian's Shadow",
         form="signal", strap="INTERCEPT",
         title="Intercept: opposing task group\\n22 November 2028",
         sub="Naval HF, partial decrypt, released to the force",
         header=[("NET:", "NAVAL HF, ENCRYPTED, PARTIAL DECRYPT"),
                 ("DTG:", "220110Z NOV 28"),
                 ("NOTE:", "TRANSLATED. SPEAKER: OPPOSING TASK GROUP COMMANDER, "
                           "TO HIGHER. ASSESSED AUTHENTIC.")],
         body=[
             "... the escorts are worn and the air wing has flown for nineteen "
             "days. I am not asking to withdraw. I am stating what the group "
             "can do. It can close the corridor for the period of the talks. "
             "It cannot hold it against a determined passage and preserve "
             "itself, and I will not be the officer who lost the carrier to "
             "prove a point that a signature would have proved.", "",
             "The coalition force is smaller than it was. It is also better at "
             "this than it was. Their escorts do not chase. Their aircraft do "
             "not come out to fight us where we are strong. They protect the "
             "transports and they let us come to them, and every time we do "
             "we spend fuel we cannot replace here.", "",
             "Request guidance on whether the closure is to be enforced "
             "against the passage expected on the twenty-third. If so I will "
             "enforce it. If the settlement is to be signed regardless, I "
             "request the order to withdraw before I am given the order to "
             "withdraw damaged ..."],
         note="The commander's estimate of our force is accurate. His estimate "
              "of his own is assessed as candid. The passage on the "
              "twenty-third will be contested. It will be contested by a "
              "professional who would rather not."),
    dict(file="06b_santos_log", before="The First Ship Through", form="log",
         title="Master's log, MV Coral Pioneer\\n27 November 2028",
         sub="Deck log extract, the night before the passage",
         ship="MV Coral Pioneer", master="L. Santos", date="27 November 2028",
         entries=[
             ("1800", "Convoy conference aboard the escort flagship by boat. "
                      "Told the ceasefire is at 0000 and \"not everyone has "
                      "acknowledged\". Asked what that meant for us. Was told: "
                      "\"Sail as planned.\""),
             ("1830", "Chief reports No.2 bearing at 71 degrees and climbing "
                      "slowly. Will hold at 9 kn. Will not hold at 12. Told the "
                      "commodore. Commodore said the convoy speed is 9 kn."),
             ("1900", "Crew briefed. Nobody asked to be relieved. Two asked "
                      "whether the escort that stopped us on 18 Oct is out "
                      "there. I said I did not know. That is true."),
             ("2200", "Lights of Darwin astern. Escorts on both beams and one "
                      "ahead. Sea state 2. Six weeks ago I was told to heave to "
                      "on this bearing by a man with a \"regional\" "
                      "authority.")],
         note="For the owners, and for whoever reads these afterwards: the navy "
              "did not get us through the first time. We were through before "
              "they arrived. What they did was make it so that we could go "
              "again. Forty ships have gone through behind us since. That is "
              "the job, and it was theirs, and they did it.  - L.S."),
]

# Hang each document before its mission, AFTER the sitrep that closes the
# chapter (a chapter's closing report reads first; the cable that opens the
# next operation reads after it). _spine() keeps EVENTS order for pages that
# share a mission, so the order here is the order the player reads them.
for _doc in DOCUMENTS:
    _pos = max((i for i, e in enumerate(EVENTS[:-1])
                if e.get("before") == _doc["before"]), default=None)
    if _pos is None:
        # no sitrep before that mission: insert before the first event that
        # is hung on a LATER mission, keeping calendar order
        _later = [i for i, e in enumerate(EVENTS[1:-1], 1)
                  if e.get("before") and e["before"] != _doc["before"]]
        _pos = len(EVENTS) - 2
    EVENTS.insert(_pos + 1, _doc)


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

# A flight row's last field is a list of ACCEPTABLE LOADOUT NAMES, and the
# names have to be the ones the winning files actually declare. The stock
# 1985 vocabulary does not survive the mod collection: the Super Hornet's
# fits are MurderHornetCAP and friends, and the Growler's are
# MurderHornetSEADHeavy and SEST_NGJLongRange. Rows written against
# AirToAir/SEAD would have quietly excluded the two aircraft the roster
# sells for exactly those jobs. Checked against the winning files, not
# assumed from the stock campaign.
#
# The speculative fits are deliberately absent: the F-35A's Malice424 and
# Intercept260*, and the Growler's SEST_MaliceNGJ, belong to Future Front.
# Air-tasking rows. The role field is matched against the aircraft file's own
# top-level `Role=` line and the fit field against its `AvailableLoadouts`;
# build_pack.check_flights() proves every row against the roster before a
# campaign entry is written, which is how the three bugs below were found.
#
# All three fast jets declare `Fighter,Bomber,SEAD`, so no role token separates
# the Growler from the two fighters: a CAP flight can always draw one. Offering
# it nothing would be the worse answer, so the row carries its escort fit -
# AARGM-ER x2 and AIM-260 x2 - which is how a Growler flies with a CAP anyway.
CAP = ("CAP|Combat Air Patrol|Fighter|2|"
       "AirToAir/AirToAirStealth/MurderHornetCAP/MurderHornetInterceptor/"
       "MurderHornetLightsOut")
# `Recon` and `AEW` are stock fit names carried by the P-3C and E-2C. Nothing
# in this roster defines either: the P-8 offers only ASW and AntiShip, and the
# Wedgetail and Triton declare no AvailableLoadouts line at all. They still
# match the role filter, and whatever the engine gives a fitless airframe is
# its default - not a preset invented here to make a checker pass.
RECON = "Recon|Maritime Patrol|MPA/ASW/ESM/AEW|1|ASW/AntiShip"
# No helicopter declares a `Helicopter` role, which is very likely why the one
# stock helicopter tasking row is commented out in the shipped campaign. `SAR`
# is the only token the MH-60R declares that no other roster aircraft shares,
# so it is the filter; `ASW` would drag the P-8 in. This path is unverified.
# The fit list is a union across every airframe that can fill this flight,
# each of which flies the intersection. SW03's CH-53s used to need their own
# names here; they are granted outright now, so nothing that can take this
# slot flies a CH53SA* fit and advertising one would be an orphan name.
HELO = ("HeloRecon|Ship's Flight|SAR|1|"
        "ASW/ASWLongRange/ASWPatrol/Anti-shipLate")
STRIKE = ("Attack|Maritime Strike|Bomber/SEAD|2|"
          "Strike/StrikeLongRange/StrikePrecision/AntiShip/AntiShipHeavy/"
          "MurderHornetSEAD/MurderHornetAntiShip/MurderHornetSEADHeavy/"
          "SEST_NGJLongRange")
# There is no tanker row. `ui.ini` localises exactly six air-tasking roles -
# AirTaskingRole_SuCAP, _CAP, _Recon, _HeloRecon, _Attack and _AEW, lines
# 3032-3037 - and Tanker is not among them. A seventh label would be a role
# token invented here. The KC-46 and the KC-135 stay authored mission assets,
# which is what they already were; they are not sold as a taskable flight.

# The native build brief's service table, adopted as written. Purchases open
# at six scheduled points and close at SW04, SW06 and SW08 - the chapters
# where the player fights with what chapter's start gave them. SW10's rearm
# is the labelled scheduled fallback the brief permits until the conditional
# stores gate is demonstrated.
# The builder does not open on the whole roster. The force assembles in
# stages, so each purchase window names what is actually available then -
# rendered into TaskForceModeAllowedRosterUnits, which Pacific Strike uses
# eleven times for exactly this. The variants come from ROSTER, never restated.
ESCORTS = ["ran_ffh_anzac", "ran_opv_arafura", "usn_mh-60r"]
AIR_EARLY = ["usn_p8", "raaf_f-35a"]
AIR_LATE = ["usn_fa-18f_blk3", "E7A_Wedgetail", "usn_ea-18g",
            "raaf_mq-4c_triton", "usaf_kc-46a_boom"]
BUY_01 = ESCORTS
BUY_02 = ESCORTS + ["ran_ddg_hobart", "ran_aor_supply", "usn_p8"]
BUY_03 = BUY_02 + ["ran_lsd_choules", "ran_ssg_collins", "raaf_f-35a"]
BUY_05 = BUY_03 + ["ran_lhd_canberra", "usn_fa-18f_blk3", "E7A_Wedgetail"]
BUY_07 = BUY_05 + ["usn_ea-18g", "raaf_mq-4c_triton", "usaf_kc-46a_boom"]
BUY_09 = BUY_07 + ["js_ffg_mogami"]
# SW12 replaces aircraft and repairs hulls; it does not sell new ones. That
# was a comment above the window until the allowlist made it a rule.
BUY_12 = AIR_EARLY + AIR_LATE + ["usn_mh-60r"]

WINDOWS = {
    "01": dict(buy=True, allow=BUY_01, repair=True, rearm=True, flights=[HELO]),
    # One helicopter, and the objective is about that helicopter. No row.
    "O1": dict(),
    "02": dict(buy=True, allow=BUY_02, repair=True, rearm=True,
               flights=[HELO, RECON]),
    "C1": dict(),
    # Both lifters are granted assets an objective names; nothing is free.
    "03": dict(buy=True, allow=BUY_03, repair=True, rearm=True),
    "04": dict(flights=[HELO, RECON]),
    # "alone": the player picks a detachment rather than sailing everything
    # they own into a mission written for one frigate.
    "05": dict(buy=True, allow=BUY_05, repair=True, rearm=True, flights=[HELO, STRIKE],
               detachment=True),
    "06": dict(flights=[CAP, RECON], airbase_prep=True),
    # Long Way Home has no air-tasking row. Every aircraft in it - the tanker,
    # both Raptors, both Rhinos - is named by an objective, and an objective
    # may not depend on a cockpit the player fills. The window still buys,
    # repairs and rearms; it just has nowhere to put a bought aeroplane.
    "07": dict(buy=True, allow=BUY_07, repair=True, rearm=True,
               airbase_prep=True),
    "08": dict(flights=[STRIKE, CAP], airbase_prep=True),
    "09": dict(buy=True, allow=BUY_09, repair=True, rearm=True, flights=[HELO, RECON]),
    # No ordinary hull purchases and no paid repair; the rearm is the
    # scheduled fallback, not a proved conditional gate.
    "10": dict(rearm=True, flights=[HELO, RECON, CAP]),
    "11": dict(buy=True, allow=BUY_09, repair=True,
           rearm=True, flights=[CAP, STRIKE]),
    # Aircraft replacement and repair only: no new hulls, no general rearm.
    "12": dict(buy=True, allow=BUY_12, repair=True,
           flights=[HELO, RECON]),
}

TIMEOUTS = {
    "01": "0630, half an hour after sunrise, and the merchants are still short "
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
           "Warramunga": ("protect", "warramunga"),
           "Identify": ("classify", "meridian#1", 1)},
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
    "05": {"Escort": "victory", "Convoy": ("protect", "convoy", 2),
           # The NSM round the Anzac's deck launchers carry. Empty them and
           # the objective fails; come out with any left and it stands.
           "Magazine": ("ammo", "warramunga", "knm_nsm_1a")},
    "06": {"Convoy": "victory", "Picture": ("classify", "red_sag", 1),
           "Sentry": ("protect", "isr"), "Hobart": ("protect", "hobart"),
           "Airlift": ("classify", "red_lift", 1)},
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
           "Tanker": ("protect", "air#2"), "Neutrals": "neutral"},
    "D3": {"Relief": "victory", "Town": "neutral",
           "Group": ("protect", "group")},
    "D4": {"Auxiliary": "victory", "Cruiser": ("protect", "escort#1"),
           "Restraint": ("survive", "cap")},
    "D5": {"Pads": "victory", "Safety": "neutral",
           "Serial": ("destroy", "target", 1),
           "Battery": ("protect", "battery")},
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
    # (mission, unit type): the air-tasking ROLE this aircraft's section fills.
    #
    # The slot INTEGER is not authored here. `TaskForceModeAirTaskingSlot` is
    # the ordinal of the row among the rows sharing its LABEL, not the row's
    # position in the list: Pacific Strike Mission26's third row is its FIRST
    # CAP row and both its sections carry Slot=1, while Mission29's third row
    # is its SECOND Recon row and carries Slot=2. No label repeats inside a
    # Southern Watch mission, so every ordinal here is 1 - which is exactly
    # why authoring the number by hand put 2s and 3s in eleven of them. The
    # builder derives it now.
    #
    # Nothing in here may be named by a trigger. A slot is a cockpit the
    # player's own aircraft fills, and no native mission binds an objective to
    # one: 20 slot-tagged sections in the shipped campaign, 0 trigger
    # references. Aircraft an objective depends on carry JOINS instead.
    ("01", "usn_mh-60r"): "HeloRecon",
    ("02", "usn_mh-60r"): "HeloRecon", ("02", "usn_p8"): "Recon",
    ("05", "raaf_f-35a"): "Attack",
    ("09", "usn_p8"): "Recon",
    ("10", "usn_p8"): "Recon",
    ("12", "usn_mh-60r"): "HeloRecon",
    ("04", "usn_mh-60r"): "HeloRecon", ("04", "usn_p8"): "Recon",
    ("05", "usn_mh-60r"): "HeloRecon",
    ("06", "raaf_f-35a"): "CAP", ("06", "E7A_Wedgetail"): "Recon",
    ("08", "usn_ea-18g"): "Attack", ("08", "raaf_f-35a"): "CAP",
    ("09", "usn_mh-60r"): "HeloRecon",
    ("10", "jp_sh-60k"): "HeloRecon", ("10", "jp_sh-60j"): "HeloRecon",
    ("10", "jp_f-2a_late"): "CAP",
    ("11", "usn_f-35c"): "CAP", ("11", "usn_ea-18g_2020"): "Attack",
    ("12", "usn_p8"): "Recon",
}

# Aircraft the player is GIVEN for a mission, because an objective names them.
# `JoinTaskForce=True` with a `CampaignTag`: 04 Sunda Strait line 504, 08A
# Pathfinders line 531, four more in the shipped campaign. This is the native
# answer to "the mission depends on this exact aeroplane", and it is why SW06
# can make the Triton's survival the decision it is without the campaign
# having to sell the player a Triton first.
JOINS = {
    ("01", "usn_p8"),
    # Named in the briefing, so it has to exist: the roster does not sell a
    # Triton until SW07, and a slot nobody can fill is a Triton nobody gets.
    ("01", "raaf_mq-4c_triton"),
    # Same for SW02's Wedgetail - the brief names it, the roster cannot yet
    # sell it, and the designer's own placeholder rule is that a tasking
    # cockpit carries no name and no briefing line.
    ("02", "E7A_Wedgetail"),
    ("03", "usmc_ch53_standalone"),
    ("06", "raaf_mq-4c_triton"),
    ("07", "usaf_f-22_s6"),
    ("O1", "usn_mh-60r"),
    ("C1", "usn_mh-60r"),
}



DEPTHS = {
    # Depth is a NAMED TOKEN, not feet. The native export uses low, shallow,
    # periscope, belowlayer and AboveLayer and never a number - an earlier pass
    # here wrote -400 and friends, which the game has no reason to understand.
    # Hunting boats sit below the layer, where a surface ship's sonar has to
    # work for its contact; the semi-submersible runs at periscope depth
    # because that is what it is.
    "plan_ss_type_039c": "belowlayer", "plan_ss_type_039": "belowlayer",
    "plan_ss_kilo": "belowlayer", "wp_ssn_akula": "belowlayer",
    "plan_ssn_type_093b": "belowlayer", "usn_ssn_seawolf": "belowlayer",
    "_narco_narcosub_adv": "periscope",
    "civ_humpback": "shallow",
    "ran_ssg_collins": 0,                # surfaced alongside, deliberately
}

ROUTES = {
    # SW04's contact runs south out of the Seram passage for the handover box.
    # Its objective is that it gets there; an unrouted contact never would.
    ("04", "_narco_narcosub_adv"): [(-5.45, 130.19, "Periscope"),
                                    (-5.70, 130.18, "Periscope"),
                                    (-5.95, 130.17, "Periscope")],
}

for _m in MISSIONS:
    for _u in _m["units"]:
        _slot = SLOTS.get((_m["num"], _u["type"]))
        if _slot:
            _u["slot"] = _slot
        if (_m["num"], _u["type"]) in JOINS:
            _u["join"] = True
        if _u["type"] in DEPTHS:
            _u["depth"] = DEPTHS[_u["type"]]
        _route = ROUTES.get((_m["num"], _u["type"]))
        if _route:
            _u["route"] = _route


# =============================================================================
# THE ESCALATION CURVE
#
# Every mission declares its place in the shape of the campaign, and the
# builder enforces a red-combat budget per role. "Red combat" is counted from
# the game's own [AI] Role= classification, so an AEW aircraft, a transport,
# an airfield or a merchant decoy does not inflate the opposition: SW04 reads
# as five red units and is really three, and SW07 as four and is really two.
#
# Provisional assignment pending the pacing redesign.
# =============================================================================

ROLES = {
    "01": "opening", "O1": "patrol", "02": "logistics", "C1": "patrol",
    "03": "strike", "04": "recon", "05": "escort", "06": "recon",
    "07": "escort", "08": "strike", "09": "logistics", "10": "escort",
    # SW11 is the campaign's one fleet action. It qualifies now: a carrier
    # group with a proper screen and a submarine the player cannot watch while
    # watching the air picture.
    "11": "fleet", "12": "escort",
    "D1": "escort", "D2": "exercise", "D3": "logistics", "D4": "escort",
    "D5": "exercise", "D6": "strike", "D7": "exercise", "D8": "strike",
}

for _m in MISSIONS:
    _m["role"] = ROLES[_m["num"]]


# =============================================================================
# CONSEQUENCES FOR LOSING SUPPORT SHIPS
#
# Three tiers, kept apart on purpose.
#
# ENFORCED BY THE GAME. The campaign runs native Task Force Mode, so a
# purchased support ship that dies is gone from the owned force and has to be
# re-bought at its roster price: Supply 140 points, a tanker 75, the Wedgetail
# 80, the Triton 60, against mainline allocations of 100-200 per mission. That
# is most of a mission's income to replace one auxiliary, and it is automatic.
# TaskForceModeRequireEntireTaskForce=True on the convoy operations means the
# player cannot leave the AOR at home to keep her safe, either.
#
# ENFORCED BY MISSION DESIGN. Where a support asset is the mission's point -
# the tanker in SW07, Supply and Collins in SW09 - losing it fails an objective
# through a trigger, and in SW07 it cancels the main objective outright.
#
# STATED, NOT ENFORCED. What this build cannot do is gate mission nine on
# something that happened in mission two: that needs a saved campaign outcome
# nothing in the shipped data demonstrates. So the loss raises an intel message
# naming what it will cost, and the cost is then real because the roster price
# is real. The message is honest about which it is.
# =============================================================================

SUPPORT_LOSS = {
    "01": [dict(asset="Bluefin 21", units=["air#1"],
                intel="Bluefin 21 is down. The Poseidon was the only thing "
                      "holding the picture past Warramunga's horizon, and "
                      "92 Wing has no spare airframe in the north this week.  - Ward")],
    "02": [dict(asset="HMAS Supply", units=["escort#3"],
                intel="SUPPLY is gone. Every operation after this one plans "
                      "around a tank that does not refill, and 140 points is "
                      "most of a mission's allocation to put another hull in "
                      "her place.  - Mercer"),
           dict(asset="Texaco 51", units=["air#2"],
                # Says what is true. It used to promise that sortie lengths
                # would shorten "from today", and nothing in the campaign
                # recorded the loss to make that happen.
                intel="The tanker is down. The allied detachment that lent "
                      "her will want a reason, and until she is replaced "
                      "every sortie past Darwin's radius is planned around a "
                      "tanker that is not there.  - Ward")],
    "06": [dict(asset="Sentry 06", units=["isr"], objective="Sentry",
                intel="Sentry 06 is lost. The surface picture north of the "
                      "horizon goes with her, and a replacement Triton is 60 "
                      "points and a week of crew work at Edinburgh.  - Ward")],
    "09": [dict(asset="HMAS Supply", units=["support#1"], objective="Supply",
                intel="SUPPLY is gone with the service half-finished. Collins "
                      "goes home on what she has, and the corridor loses the "
                      "one hull that let it operate east of the Cape.  - Mercer")],
    "12": [dict(asset="Wedgetail 03", units=["aew"],
                intel="Wedgetail 03 is down on the last morning of the "
                      "campaign. 2 Squadron has two airframes and this was "
                      "one of them.  - Ward")],
}

for _m in MISSIONS:
    _loss = SUPPORT_LOSS.get(_m["num"])
    if _loss:
        _m["support_loss"] = _loss

# The convoy and replenishment operations sail with everything: the player may
# not leave the auxiliary at home to keep it safe. The strike and side missions
# let the player pick a detachment.
for _m in MISSIONS:
    if _m["num"] in ("03", "07", "08", "O1", "C1") or _m["group"] == "dispatch":
        _m.setdefault("window", {})["detachment"] = True


# =============================================================================
# CAMPAIGN VARIABLES: consequences that are ENFORCED, not narrated
#
# The native source pack settles a question this build had previously answered
# wrongly. Campaign variables are real and demonstrated in the shipped export:
#
#   [CampaignVariables] 07ASlavaDestroyed=False   declares it with a default
#   Action_VariableSet=07ASlavaDestroyed,True     a trigger writes it
#   SpawnByVariableAND=07ASlavaDestroyed,IsFalse  a later unit spawns on it
#   Condition_Condition1_Type=VariableCheck       a later trigger reads it
#
# 07A Hunt for the Cruiser writes two; 08A Pathfinders and 10 Vengeance at
# Luzon read them and omit launchers and a Slava screen accordingly. 08A also
# writes a recon flag that 09 Shadows off Palawan reads to reveal missile sites.
#
# ONE CONSTRAINT, OBSERVED. Only the IsFalse form appears in the export. So a
# flag always names something that HAPPENED, and later missions spawn the
# content that exists when it did NOT. IsTrue is not invented here.
# =============================================================================

VARIABLES = {
    # Losing the replenishment ship in chapter 1 thins the rear area in
    # chapter 5. Not a message about a consequence - the hull is absent.
    "02": dict(declares=["SW02SupplyLost"]),
    # Classifying the northern surface group is worth something three weeks
    # later, which is what makes exposing the Triton a decision rather than a
    # chore.
    "06": dict(declares=["SW06NorthernGroupClassified"]),
    # The fleet action's result carries into the last passage.
    "11": dict(declares=["SW11FujianSunk"]),
}

for _m in MISSIONS:
    _v = VARIABLES.get(_m["num"])
    if _v:
        _m["declares"] = _v["declares"]

# SW02: the support-loss trigger writes the flag.
for _m in MISSIONS:
    if _m["num"] == "02":
        _m["support_loss"][0]["sets"] = "SW02SupplyLost"
    if _m["num"] == "06":
        # ("classify", ref, minimum, variable-to-set)
        _m["resolve"]["Picture"] = ("classify", "red_sag", 1,
                                    "SW06NorthernGroupClassified")
        # Recon that produces tasking rather than just a reveal: the escorts
        # are screening something, and the something is a shuttle track the
        # player was never briefed on. Taking it means holding the Triton
        # north for another leg with the convoy clock already running - the
        # same decision as the first one, asked again at a worse moment.
        _m["discoveries"] = [dict(
            after="Picture", objective="Airlift", seconds=120,
            intel="Those escorts are screening a track, not a patrol line. "
                  "There is a transport running south-west into the enclave "
                  "field and nobody has put a name on it. Sentry 06 is the "
                  "only thing in range that can.")]
    if _m["num"] == "09":
        # The second replenishment hull only exists if SUPPLY came through
        # chapter 1. Lose her at Steel Highway and the rear-area group is one
        # ship thinner for the service window that matters.
        for _u in _m["units"]:
            if _u["type"] == "civ_ms_amra":
                _u["spawn_if"] = ("SW02SupplyLost", "IsFalse")
    if _m["num"] == "11":
        _m["flags"] = [dict(name="SW11FujianSunk", units=["red_cv#1"],
                            intel="FUJIAN is down. LIAONING is still out "
                                  "there and still flying, but the newest "
                                  "deck in their fleet is on the bottom of "
                                  "the Banda Sea, and the corridor knows it "
                                  "before the talks open.")]
        _m["reveal_if"] = [dict(
            variable="SW06NorthernGroupClassified",
            units=["red_cv#3", "red_cv#4", "red_cv#5"], level="Identify",
            intel="Two of the escorts ahead of you are hulls Sentry 06 put a "
                  "name to on 6 November, and the third keeps the company "
                  "they kept. The screen is on your plot from the start. What "
                  "is behind it is not - that you still have to find.")]
    if _m["num"] == "12":
        # Sink the carrier at Fujian's Shadow and the spoiler group has no air
        # cover on the last morning.
        for _u in _m["units"]:
            if _u["station"] == "spoiler_air":
                _u["spawn_if"] = ("SW11FujianSunk", "IsFalse")
