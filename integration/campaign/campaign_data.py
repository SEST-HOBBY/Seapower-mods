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
helicopter can recover aboard its assigned ship, that a replenishment transfer
moves what it is tuned to, that a briefing's tanker can pass gas to its
receiver, or that a trigger fires when the game is running. SW09 is scored on
survival and a service window rather than on a transfer: HMAS Supply and
Stalwart carry a supply system (SEST RAN Fleet, tuned in SEST Replenishment
At Sea's table) that is set up to pass the missiles and torpedoes the
briefing names while the window runs, but no condition type the engine
offers can count them. The campaign's own notes say so.
"""

INFO_DESC = (
    "SOUTHERN WATCH - The Northern Lifeline. October 2028. A confrontation elsewhere in the"
    " Indo-Pacific has drawn most of America's ready combat power north. Above Australia, "
    "forged movement orders, missing cargo records and insurers refusing cover are closing "
    "the sea lanes. The Meridian Maritime Group offers escorts, inspections and access to "
    "its terminals; some of its vessels carry armed teams. When one escort fires on an "
    "Indonesian patrol in the Arafura Sea, HMAS Warramunga is the nearest warship. Over six"
    " weeks, the Australian-led task group must protect people, fuel and supplies as the "
    "confrontation spreads to the Biak enclave and Chinese carrier groups in the Banda "
    "approaches. Allied detachments, recovered intelligence and the condition of surviving "
    "ships shape the next passage. A ceasefire eventually opens a route home, but the "
    "withdrawing forces and those still prepared to attack must be distinguished."
)


# 816 Squadron RAN: the one squadron of the MH-60R under the Australian flag.
# Every source of the airframe ships only US Navy squadrons, so SEST Collection
# Fixes composes the table and appends this one; a Seahawk on an Australian
# side is always a Royal Australian Navy ship's flight.
RAN_SEAHAWK = "Squadron20"


def U(side, mod, type, station, **kw):
    """One placed unit: whose side, which mod it is there to exercise, what it
    is, and where it stands. Hull variant, squadron and loadout are resolved
    from the winning file at build time, not guessed here.

    A Seahawk's squadron follows its flag, not its side: 816 Squadron when the
    side it sails for is Australian (or its own nation= says so), the file's
    default otherwise. "Blue" was a proxy for Australian while every player
    was; a campaign played from the other side put the RAN's Seahawk on red
    and it came out as a US Navy squadron. The builder applies it once the
    mission's nations are known; an explicit squadron= always wins."""
    if type == "usn_mh-60r":
        kw.setdefault("squadron_by_nation", {"Australia": RAN_SEAHAWK})
    return dict(side=side, mod=mod, type=type, station=station, **kw)


# Formation members fly the same route (the SW10 and D1 convention), so a
# leader lost does not leave its wingman circling a spawn point.
_SW05_STRIKE = [(-8.8, 130.7, 24000), (-10.2, 131.7, 24000), (-8.6, 131.9, 24000)]
_SW07_SWEEP = [(-7.2, 133.0, 52000), (-4.6, 132.45, 52000)]
_SW09_RAID = [(-14.5, 147.0, 30000), (-13.5, 148.4, 30000), (-11.0, 148.05, 30000)]
_D6_HUNT = [(-3.3, 130.48, 42000), (-4.4, 130.1, 42000)]
_D7_SWEEP = [(-10.9, 130.1, 30000), (-11.6, 129.9, 30000)]

def F(objective, units=None, minimum=1, kind="destroyed"):
    """A loss that ends the mission, and the objective it fails.

    One flat list with one objective id used to cover every protected unit in
    a mission, so whatever sank, the same objective was reported failed:
    SW09 said Collins was lost when a freighter with no objective of its own
    went down, and SW07 blamed the tanker for a Rhino. Each entry now names
    its own units, and `units=None` means take them from that objective's own
    resolver - which is the only way the trigger that ends the mission and the
    trigger that marks the objective failed cannot drift apart.

    `kind="destroyed"` is a loss. `kind="unseen"` ends the mission when the
    enemy classifies those player units instead, and takes its units from an
    `unseen` resolver when it names none.
    """
    return dict(objective=objective, units=units, minimum=minimum, kind=kind)


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
    "automatic-sar": (
        "library", "rescue behaviour (a DLL the export skips, plus its "
        "language strings); no unit or round a mission can name. The campaign "
        "reads it through the survivor reward, CSARPointModifier: what a "
        "helicopter or ship picks up is paid at every debrief"),
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
         sub="An armed escort stops a crippled freighter north of Darwin",
         dateline="18 OCTOBER 2028  |  MARITIME BORDER COMMAND, DARWIN",
         headline="SHOTS FIRED IN THE ARAFURA",
         body=[
             "Before dawn today, 150 miles north of Darwin, an armed Meridian "
             "escort ordered the crippled Australian-chartered freighter MV "
             "Coral Pioneer to stop for inspection. The Indonesian patrol boat "
             "sent to investigate reported gunfire, then went silent.",
             "It is the first shot in a campaign that has been closing the "
             "northern sea lanes for months without one: forged movement "
             "orders, lost cargo records, insurers refusing legal voyages.",
             "Meridian - freight lines and security contractors under one name "
             "- sells the cure: its escorts, its inspections, its terminals. "
             "Most of its ships are honest. A few carry armed teams, and at "
             "twelve miles they look exactly the same.",
             "With much of America's ready combat power drawn north by a crisis "
             "elsewhere in the Indo-Pacific, HMAS Warramunga is the nearest "
             "coalition warship. Bring the convoy together. Get the crews out. "
             "Identify before you shoot: the fastest way to start a war is to "
             "be wrong about a fishing boat."]),
    # Rendered as an INTSUM: its dateline already said COALITION JOINT
    # INTELLIGENCE, and a press sheet from an intelligence cell is a form the
    # campaign never had a reason to use.
    dict(file="06_interlude", before="The Open Door", form="intsum",
         title="The Enclave\\n12 November 2028",
         sub="A contested airfield, foreign advisers and a relief window",
         org="Coalition Joint Intelligence Centre, Darwin", ref="INTSUM 028-63",
         date="12 November 2028", subject="The enclave",
         body=[
             (
                 "1. Regional security forces have recovered most of the facilities Meridian's "
                 "hard-line faction seized. One airfield and port enclave, on Biak off "
                 "Indonesian Papua, has not come back, and recent imagery identifies a large "
                 "surface-to-air missile deployment, assessed as S-400, rather than the "
                 "man-portable launchers first reported. It threatens the relief approach."
             ),
             (
                 "2. A Chinese naval task group has arrived under a protection-and-evacuation "
                 "pretext and demanded the coalition patrols suspend. A small Russian "
                 "expeditionary detachment supports the enclave under its own arrangement, not "
                 "Beijing's. Satellite imagery, patrol reports and intercepted logistics "
                 "traffic indicate its supply routes; gaps remain between observations."
             ),
             "3. Local Indonesian authorities have asked for a protected "
             "window to move civilians and emergency supplies out. That "
             "window, not a body count, is the aim.",
             (
                 "4. Guidance. The agreed relief window is seventy minutes. A battery kept off "
                 "the air for that long is worth more than a battery destroyed at the cost of the"
                 " aircraft flying the relief. The civilian buildings on the field are not "
                 "targets."
             )],
         note=(
             "Keep the relief route open for the agreed window. Bring the transports through.  "
             "- Cdre Mercer"
         )),
    dict(file="12_closing", title="The First Ship Through\\n28 November 2028",
         sub="An imperfect ceasefire and a working sea route",
         dateline="28 NOVEMBER 2028  |  MARITIME BORDER COMMAND, DARWIN",
         headline="THE LANES ARE OPEN",
         body=[
             "Coral Pioneer reached Darwin with a cracked bearing and a "
             "volunteer engineer from the escort. Two hundred miles behind her, "
             "one Chinese naval group complied with its withdrawal order and "
             "the other spent the afternoon deciding whether to.",
             "The route is open. Jakarta, Port Moresby and Dili, which asked "
             "for help, still hold their own ports. Most of the merchant crews "
             "went home.",
             "What is left of your task group is alongside at Darwin, and the "
             "ledger says which ships are in it. The measure of these six "
             "weeks is not what was sunk on either side. It is the sea route, "
             "and the people who used it.",
             "Master Santos's last entry for the passage, which she has allowed "
             "to be quoted, reads: \"Alongside. One shaft. All hands.\" The "
             "Commodore Mercer's, which he has not, is understood to be shorter.",
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
    # The stock Task Force campaign's value. Survivors picked up are paid at
    # the debrief ("{0} survivors -> {1} additional point(s) awarded", ui.ini
    # [TaskForceDebrief]), which is what makes Automatic SAR part of the
    # campaign rather than a convenience. Which way the modifier scales is
    # not stated anywhere readable - the stock comment says "100 survivors
    # reward 1 pt" beside a value of 10 - so this ships the stock number and
    # the test card reads the debrief line to settle it.
    CSARPointModifier="10",
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
    dict(unit="ran_opv_arafura", picks=["Variant1"], points=100,
         note="donor Meteoro fit is richer than the real Arafura; one hull "
              "(HMAS Arafura) is on sale until the fit is corrected - Eyre "
              "and Pilbara sail as scripted hulls"),
    dict(unit="raaf_f-35a", picks=["Squadron3"], points=45,
         note="No. 75 Squadron, RAAF Base Tindal - checked against the "
              "squadron file's own comment"),
    dict(unit="usn_fa-18f_blk3", picks=["Squadron8"], points=35,
         note="Australian squadron in the SEST Growler pack's output"),
    dict(unit="usn_ea-18g", picks=["Squadron6"], points=55,
         note="conventional EW/SEAD fits; MALICE stays in Future Front"),
    # The armed patrol aircraft costs more than the unarmed one: both fill the
    # Recon row, and at 45 against the Triton's 60 nobody would buy the Triton.
    dict(unit="usn_p8", picks=["Squadron3"], points=55,
         note="the squadron file labels every entry USN; Squadron3 is the "
              "bible's choice, and the label is worth fixing upstream"),
    dict(unit="E7A_Wedgetail", picks=["Squadron1"], points=80,
         note="No. 2 Squadron RAAF, from the SEST Wedgetail pack"),
    dict(unit="raaf_mq-4c_triton", picks=["Squadron1"], points=40,
         note="unarmed in this implementation, so priced under the P-8 and "
              "the F-35A"),
    dict(unit="usn_mh-60r", picks=[RAN_SEAHAWK], points=20,
         note="816 Squadron RAN; one family chosen explicitly - usn_mh-60r_26 "
              "is a different unit and is never substituted for it"),
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
CommanderNameDefaultAustralia=Morgan Reid
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
    intro="Find MV Coral Pioneer's convoy, work out which contact is armed, "
          "and keep the "
          "rendezvous open. Nothing here is a target without identification.",
    sender="Commodore Alex Mercer, Maritime Border Command, Darwin",
    intent=("Get the crews out of danger and the merchants into the handover box. "
            "Identify before you shoot: a dead fishing boat ends this "
            "operation and starts something worse, and a Meridian escort "
            "that gets away is a problem for another day. Coral Pioneer is the "
            "ship this morning is about; bring her in."),
    date=(2028, 10, 18), time=(5, 40), sea=2, clouds="Scattered_1", wind="NW",
    difficulty=1, minutes=50, centre=(-10.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "ARAFURA SEA, 0540 local. MV Coral Pioneer missed her rendezvous forty minutes ago."
            " Her last report mentioned an engine casualty and an escort claiming the authority"
            " to inspect the convoy. The Indonesian patrol sent to investigate has reported "
            "gunfire and nothing since.\\n\\nYou are the escort, with your embarked Seahawk if "
            "you sailed with one, a Poseidon on task for the first part of the morning and a "
            "Triton high to the north. Bring the merchants together and walk them north-east to"
            " the handover box.\\n\\nYour merchants are Coral Pioneer, the bulker Gove Trader, "
            "the chartered coaster Jeparit and the relief freighter Sunda Relief. Ahead of them"
            " are two trawlers, and a scheduled Denpasar flight is overhead. One contact in "
            "that picture is a Meridian escort with weapons and one is a container hull putting"
            " out the radars of a warship it is not - do not let your ESM operator pick the "
            "wrong one. Your weapons are tight.\\n\\nINTELLIGENCE: The shore cell is correlating "
            "satellite radar imagery, AIS reports and the aircraft picture. An AIS identity is "
            "a claim to check against the contact's position, appearance and emissions. Bluefin"
            " and Sentry provide the local search picture; classify contacts and apply the "
            "engagement orders before firing."
        )),
    forces="Your escort group and its MH-60R if embarked, one P-8A on task, "
           "one MQ-4C Triton overhead. Four merchant hulls to collect; two "
           "trawlers and an airliner on the track; one armed Meridian escort "
           "and one decoy.",
    objectives=[
        ("Convoy", "Walk three of the four merchants, Coral Pioneer among "
                   "them, into the north-eastern handover box",
         "30,-30,Fail,Main"),
        ("Neutrals", "Harm no neutral shipping or aircraft", "0,-40,Complete"),
        ("Warramunga", "Bring your flagship out intact", "10,-15,Complete"),
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
    win=(
        "The required merchants, including Coral Pioneer, have reached the handover box. "
        "Forward the contact reports and recordings to command. Master Leila Santos of Coral "
        "Pioneer, on channel 16: 'Understood, escort. We were not going to heave to anyway.'"
    ),
    lose="The convoy is scattered and Coral Pioneer is not answering. Whatever "
         "Meridian's inspection was for, it worked.",
    stations={
        # Encounter scale. The first build of this opening had Warramunga
        # 34 NM from the group she is told to shepherd (50 minutes at flank
        # covers 24), the "identification traffic" 130 NM away and sailing
        # off, and the armed escort stationary and facing away with a 17 NM
        # radar 20 NM from the nearest merchant. Every gate passed. Now the
        # escort is 8 NM astern, the trawlers and the Meridian hull sit ON
        # the track to the handover box 12-16 NM ahead, and the airliner
        # crosses overhead - so the picture has pieces in it.
        "warramunga": S(-10.42, 131.77, "Escort", heading=80),
        "convoy": S(-10.4, 131.9, "Coral Pioneer group", heading=80),
        "neutrals": S(-10.20, 132.00, "Arafura traffic", heading=230),
        "meridian": S(-10.23, 132.11, "Meridian escort", heading=230),
        "air": S(-10.6, 131.6, "Southern Watch air", heading=70, alt=22000),
        # The brief says a Seahawk on the deck. It spawned 21 NM away at
        # 3,000 ft in the same Vic as a P-8 doing three times its speed at six
        # times its height. Beside the ship, low, on the ship's heading.
        "flight": S(-10.44, 131.76, "Ship's flight", heading=80, alt=500),
        "high": S(-9.9, 131.9, "Triton orbit", heading=90, alt=50000),
        # Pointed down the Darwin-Denpasar track (bearing 275 from here).
        "liner": S(-10.3, 132.32, "Denpasar service", heading=275, alt=34000),
        "home": S(-12.409, 130.8665, "RAAF Base Darwin"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "warramunga",
          variant="Variant3", weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500, weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "air", squadron="Squadron3",
          name="Bluefin 21", alt=18000, weapons="Tight"),
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "high",
          name="Sentry 04", weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "convoy",
          name="MV Gove Trader", weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_jeparit", "convoy",
          name="MV Jeparit (chartered)", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_freighter_a", "convoy",
          name="MV Sunda Relief"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "neutrals",
          name="Arafura trawler north"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_c", "neutrals",
          name="Arafura trawler south"),
        # An aircraft with no Waypoints is held in an orbit over its spawn -
        # the first install saw the airliner circle one spot all mission.
        # Stock airliners fly one waypoint far off the map at cruise
        # (Charlies.ini's DC-10: 500 NM out, Telegraph=4), so this one does:
        # 500 NM toward Denpasar, further than 50 minutes at cruise.
        U("neutral", "civil-aircraft-airbus", "civ_a320", "liner",
          name="Denpasar 214", route=[(-9.57, 123.9, 34000)], telegraph=3),
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
    sender="Commodore Alex Mercer; Commander Mara Kila, PNG Defence Force Maritime Element, concurring",
    intent=((
        "Kokoda Star carries the power plant and medical stores for Moresby's hospital. Lae "
        "Provider carries the fuel that keeps it running until she arrives. If the submarine "
        "report is real, it wants one of those two. At least three must reach the approach box,"
        " including both Kokoda Star and Coral Pioneer. All four is what Moresby is expecting."
    )),
    date=(2028, 10, 21), time=(9, 20), sea=3, clouds="Broken_2", wind="SE",
    difficulty=2, minutes=75, centre=(-10.3, 145.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "GULF OF PAPUA, morning. Port Moresby has asked for engineering "
        "plant, medical stores and fuel, and under the Pukpuk Treaty, "
        "Australia's defence treaty with Papua New Guinea, we deliver them. "
        "Four priority merchant ships are in company with your flagship, the "
        "patrol vessel EYRE and the replenishment ship SUPPLY, "
        "and a Wedgetail is up with a tanker behind it.\\n\\n"
        "Ninety minutes ago a Poseidon laid a sonobuoy field on a diesel-electric "
        "contact across the planned track. The masters want to press on at "
        "twelve knots. We want time to classify it. You will not get both.\\n\\n"
        "Three of four must reach the Moresby approach box, and two of the "
        "three are fixed: Kokoda Star, the medical and engineering ship, and "
        "Coral Pioneer. "
        "Background traffic in this sea is ordinary commerce - it is not "
        "joining your convoy and it is not your enemy."),
    forces="Your escort group with HMAS Eyre and HMAS Supply attached, four priority merchants, "
           "E-7A Wedgetail and a KC-46 on the tanker track. One Type 039C in "
           "the area. Port Moresby is open beyond the box.",
    objectives=[
        ("Cargo", "Get three of four priority ships, Kokoda Star and Coral "
                  "Pioneer among them, into the Moresby approach box",
         "35,-35,Fail,Main"),
        ("Medical", "MV Kokoda Star must arrive", "15,-25,Complete"),
        ("Neutrals", "Harm no neutral shipping", "0,-30,Complete"),
    ],
    # Three of four arrive AND the medical ship is one of them. Without the
    # second condition the mission could be won by leaving Kokoda Star safely
    # behind and sending the other three.
    victory=dict(kind="arrive", station="convoy", min_units=3,
                 objective="Cargo",
                 # ...and Coral Pioneer, convoy#4, because the campaign is
                 # about her and she sails again by name.
                 also=[dict(units=["convoy#1"], min_units=1),
                       dict(units=["convoy#4"], min_units=1)]),
    # Kokoda Star is the first hull at the convoy station: lose her and the
    # mission is over whatever the other three do.
    fatal=[F("Medical", ["convoy#1"]), F("Cargo", ["convoy#4"])],
    neutral_objective="Neutrals",
    win=(
        "At least three ships, including Kokoda Star and Coral Pioneer, have reached the Gulf "
        "handover. Moresby's pilots can take over the arrival. Report which additional cargoes "
        "made it through."
    ),
    lose="The convoy is short and Moresby's hospital is still on generator. The next one will "
         "have to be bigger, slower and later.",
    stations={
        # The Gulf of Papua, not the Coral Sea: the pages route this convoy
        # from the Arafura through Torres Strait to "our entrance" (Kila's
        # cable), and a coaster making eight knots since the eighteenth can
        # be here on the twenty-second and could not be 230 NM south-east of
        # Moresby. The box is the Gulf entrance where Moresby's pilots take
        # over, 150 NM short of the wharf.
        "escort": S(-10.2, 144.3, "Escort group", heading=70),
        "convoy": S(-10.4, 144.5, "Priority convoy", heading=70),
        "traffic": S(-10.21, 144.33, "Gulf traffic", heading=250),
        "moresby": S(-9.5, 147.0, "Port Moresby", heading=0),
        "sub": S(-10.3, 144.1, "Submarine datum", heading=90),
        "air": S(-10.0, 145.0, "Air support", heading=70, alt=30000),
        # The ship's helicopter spawned at 30,000 ft 86 NM from the ship it
        # is homed on, in a mission the submarine can decide in twenty
        # minutes. Beside the escorts, low.
        "flight": S(-10.22, 144.32, "Ship's flight", heading=70, alt=500),
    },
    units=[
        # The anchor: at launch this is the player's first ship (the guide -
        # a Generated mission replaces the anchor with the player's force).
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort"),
        # Eyre, not Arafura: the roster sells Variant1, so a scripted OPV
        # wears a hull the player cannot also own.
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "escort",
          variant="Variant2", name="HMAS Eyre"),
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
        # The auxiliary pack's hulls all carry guns and, on this one, Styx.
        # They are cargo here: WeaponStatus=Hold on every one of them, in
        # every mission, so a "priority ship" never opens fire on its own.
        U("blue", "auxilliary-merchant-pack", "ran_ms_super_p", "convoy",
          name="MV Torres Trader", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_andizhan", "convoy",
          name="MV Lae Provider"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("neutral", "_vanilla", "civ_ms_car_carrier_a", "traffic",
          name="Gulf vehicle carrier"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "traffic",
          name="Gulf trawler"),
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
        U("blue", "us-navy-2027", "usn_mh-60r", "flight"),
        U("blue", "p-8-poseidon", "usn_p8", "air", squadron="Squadron3"),
    ],
))

MISSIONS.append(dict(
    group="core", num="03", key="Rig Seventeen", place="Timor Sea",
    intro="Civilians on an offshore platform, armed contractors on the deck "
          "above them, and a patrol closing from the north.",
    sender="Commodore Alex Mercer; Captain Ratna Prasetyo, Indonesian Navy (TNI-AL), embarked",
    intent=("The platform is not a target. The armed contractors on its upper "
            "deck are Captain Prasetyo's problem afterwards and not yours now. "
            "Two lift aircraft, each with seats for the whole crew, and a "
            "patrol boat closing from the north that has answered nobody. "
            "Get the crew off before it arrives, "
            "or hold it off until they are."),
    date=(2028, 10, 24), time=(16, 10), sea=3, clouds="Overcast", wind="W",
    difficulty=2, minutes=60, centre=(-11.0, 126.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR SEA, late afternoon. Rig Seventeen has not answered its shore "
        "office since the weekend. Thirty contract staff are still aboard, and "
        "the armed Meridian contractors holding the platform have a helicopter "
        "deck, a shore battery on the Timor coast to the north and an "
        "air-defence vehicle they were not "
        "supposed to have.\\n\\n"
        "Indonesia has asked for help and set the boundary: you may "
        "cover an evacuation, you may not level the installation. CHOULES is "
        "in company with CANBERRA, and the US Marine Rotational Force in "
        "Darwin has lent the lift for one afternoon at the end of its "
        "rotation: a Super Stallion and an Osprey off Canberra's deck, each "
        "with a seat for everyone on that platform.\\n\\n"
        "Get the lifters in, get the people off, get everybody out before "
        "the light goes. Not every platform out here is hostile, and most of "
        "this coast is working its ordinary week. The lifter that takes the "
        "crew off is the lifter that has to bring them south - lose her after "
        "the pickup and they are gone with her."),
    forces="HMAS Choules and HMAS Canberra, a USMC CH-53E and MV-22B on "
           "loan from the Darwin rotational force for the lift, and your escort. "
           "Ashore: a launcher site, a VL MICA battery, a Sosna vehicle and "
           "a technical. At sea: one armed patrol boat closing from the north.",
    objectives=[
        ("Evacuate", "Get a lift helicopter back to the amphibious group "
                     "with the platform crew", "35,-35,Fail,Main"),
        ("Platform", "Leave the civilian platform standing", "10,-20,Complete"),
        ("Ships", "Keep both amphibious ships afloat", "10,-20,Complete"),
    ],
    victory=dict(kind="arrive", station="lift", at=(-11.55, 126.62), radius=12,
                 # Not scored until a lifter has been over the platform. The
                 # first build could be won by flying straight south from
                 # spawn and never going near the thing the mission is about.
                 # One chain per lifter: the aircraft that reached the platform
                 # is the aircraft that has to reach the line, and losing it
                 # after the pickup loses the people aboard. The reviewed build
                 # let A visit the rig and B finish the rescue from the box.
                 after=dict(kind="area", units="lift", at_unit="rig", radius=3,
                            min_units=1, per_unit=True,
                            intel=(
                                "AMPHIBIOUS CONTROL: The lifter is over Rig Seventeen. The "
                                "platform crew is on the helideck and boarding. Return the "
                                "helicopter to the amphibious group; keep the approach clear of"
                                " the patrol boat."
                            ),
                            lost="The lifter with the platform crew aboard is "
                                 "down. There is nobody left to bring south."),
                 min_units=1, objective="Evacuate"),
    fatal=[F("Ships", ["amphib"])],
    neutral_objective="Platform",
    win="A lifter is back with the amphibious group and the platform crew aboard. Rig "
        "Seventeen is still standing and somebody else can argue about who "
        "owns it.",
    lose="The evacuation window closed with people still on the platform. There will not be "
         "another one this week.",
    stations={
        "amphib": S(-11.6, 126.6, "Amphibious group", heading=10),
        # The player's force forms here; the amphibious ships are scripted
        # and stay, whatever the player brought.
        "escort": S(-11.7, 126.72, "Escort", heading=10),
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
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort",
          variant="Variant3", weapons="Tight"),
        U("blue", "SEST_RAN_Fleet", "ran_lsd_choules", "amphib",
          name="HMAS Choules"),
        U("blue", "SEST_RAN_Fleet", "ran_lhd_canberra", "amphib",
          name="HMAS Canberra"),
        # The Rescue fit: 37 seats. The default fit is two Mk48 torpedoes and
        # TransportCapacity=0, which is not a lift helicopter, it is an ASW
        # helicopter with a story attached.
        U("blue", "ch-53e-standalone", "usmc_ch53_standalone", "lift",
          name="Lifter 11", alt=1500, weapons="Tight", loadout="CH53SARescue"),
        # The Marine Osprey: the Transport fit is the one with seats (32) -
        # the mod's own README routes rescue and medevac through it.
        U("blue", "mv-22b-osprey", "mv22b_osprey", "lift",
          name="Lifter 12", alt=1500, weapons="Tight", loadout="Transport"),
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
    intent=("Classify the craft, then walk it into the handover box. Do not "
            "sink it: what it is carrying is evidence, and where it is going "
            "is the hard-liners' supply route. The submarine and the whale "
            "will both want your attention. Only the craft matters tonight."),
    date=(2028, 10, 27), time=(2, 30), sea=2, clouds="Clear", wind="E",
    difficulty=2, minutes=45, centre=(-6.0, 130.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        "BANDA APPROACHES, middle watch. Something small and low is running "
        "south out of the Seram passage with almost no freeboard and no "
        "transponder. It may be carrying weapons for the airfield-and-port "
        "enclave Meridian's hard-liners still hold, it may be "
        "carrying people, and the difference decides what you are allowed to "
        "do about it.\\n\\n"
        "Your ship is working this water, with your Seahawk and Poseidon if you "
        "have them to fly. "
        "There is also a real submarine in this water - a Type 039 that has "
        "been quiet for eleven hours - and a biologic contact that three "
        "different ships have now reported as a hostile boat.\\n\\n"
        "Classify the craft - the passenger - then track it into the "
        "handover box to the south. Classify what else is down there. Do not "
        "lose the ship doing it."),
    forces="Your patrol group, and your MH-60R and P-8A if you have them. In "
           "the water: a low-profile craft, a Type 039, a fishing boat and one "
           "very large mammal. Overhead, for a foreign military: a KJ-500 "
           "early-warning aircraft, a Ka-28 and a spotter drone.",
    objectives=[
        ("Track", "Classify the low-profile craft, then walk it into the "
                  "handover box",
         "30,-30,Fail,Main"),
        ("Patrol", "Keep your flagship afloat", "15,-25,Complete"),
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
                            intel=(
                                "ESCORT CONTACT REPORT: WHISKEY classified as a low-profile "
                                "semi-submersible. Correlate the local observations with the "
                                "surface track and keep the craft under surveillance to the "
                                "handover box. Its cargo is still unconfirmed. Do not sink the "
                                "evidence."
                            ))),
    # Sinking the passenger ends it: the whole point is where it was going.
    fatal=[F("Patrol", ["patrol"]), F("Track", ["passenger"])],
    neutral_objective="Neutrals",
    win=(
        "The low-profile craft has reached the handover under surveillance. The boarding "
        "authority can now secure the vessel and its cargo. Forward all additional submarine "
        "and traffic reports separately."
    ),
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
        "patrol": S(-5.9, 130.3, "Patrol", heading=20),
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
          weapons="Tight"),
        U("blue", "us-navy-2027", "usn_mh-60r", "air",
          alt=2500, weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3", alt=15000, weapons="Tight"),
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
    group="core", num="05", key="Weapons Free", place="Timor corridor",
    intro="One ship of your choosing, one salvo, a target beyond the horizon - "
          "and a convoy behind you that the shot is actually for.",
    sender="Commodore Alex Mercer",
    intent=("Your ship has the shot. The Sovremenny fired on a protected "
            "convoy in daylight, and that changes what you may do to her. "
            "The convoy behind you is what the shot is for; the Type 071 "
            "transport is not. If she turns north, let her. Come out with "
            "rounds left - there is no reload before Monday's convoy."),
    date=(2028, 10, 30), time=(14, 10), sea=4, clouds="Overcast", wind="SE",
    difficulty=3, minutes=55, centre=(-9.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR CORRIDOR. A Chinese surface action group is working south-east down "
        "the corridor screening an amphibious transport, and it has begun "
        "turning merchant traffic back by radio and then by gun.\\n\\n"
        "You send one ship, alone, sixty miles on their disengaged bow "
        "with the weather in your favour and a full deck-launcher load. The "
        "four merchants you are covering are ten miles behind you at a tug's "
        "speed, and ESCORT SEVEN, the Meridian boat that tried to stop Coral "
        "Pioneer on the eighteenth, is on their track to hold them for the "
        "surface group.\\n\\n"
        "Establish the military threat, engage it, and be somewhere else when "
        "the counter-strike arrives - their JH-7A strike pair is "
        "within range of this box and their helicopter is already up. The "
        "merchants in the lane are not targets because somebody wrote "
        "SANCTIONED on a manifest."),
    forces="One escort of your choice, with her anti-ship missiles and her flight. Opposing: a Sovremenny, "
           "a Type 071 with its Z-20J, a JH-7A pair, a Z-21 and Meridian Escort "
           "Seven. Four protected merchants behind you, two neutral ones ahead.",
    objectives=[
        ("Escort", "Neutralise the Sovremenny screening the transport", "35,-30,Fail,Main"),
        ("Convoy", "Lose no more than one merchant, and not Coral Pioneer", "20,-30,Complete"),
        ("Magazine", "Bring your ship out with anti-ship rounds left", "10,-10,Complete"),
    ],
    # sag#1 is the Sovremenny. With both hulls counted, sinking the unarmed
    # transport won "neutralise the armed escort".
    victory=dict(kind="destroy", stations=["sag#1"], min_units=1,
                 objective="Escort"),
    # Losing the frigate ends it. It used to fail one objective and play on
    # with four merchants as the surviving Taskforce1.
    fatal=[F("Convoy", ["convoy"], 2), F("Convoy", ["convoy#1"]),
           F("Magazine", ["warramunga"])],
    neutral_objective="Convoy",
    win=(
        "The hostile escort has been neutralised. Report the convoy's position and remaining "
        "threats, then prepare to disengage with the ammunition you have left."
    ),
    lose="Your ship is gone or the convoy is broken. Either way nothing moves "
         "through this corridor tomorrow. Captain Prasetyo's report to Jakarta "
         "will be short, and it will be accurate.",
    stations={
        # "Sixty miles on their disengaged bow" - now sixty, not thirty-four
        # inside the Moskit envelope. The SAG steams for the convoy, which is
        # ten miles behind the frigate instead of 147 NM from anything; the
        # Seahawk starts on the frigate's disengaged quarter, not 16.7 NM
        # from a weapons-free Sovremenny whose SA-N-7 reaches 16.2; and there
        # is traffic in the lane for the identification premise to be about.
        "warramunga": S(-10.2, 131.7, "Escort", heading=310),
        "sag": S(-9.4, 131.1, "Opposing surface group", heading=140),
        "convoy": S(-10.3, 131.85, "Protected convoy", heading=70),
        "lane": S(-9.9, 131.4, "Corridor traffic", heading=70),
        "red_air": S(-8.6, 131.9, "Maritime strike flight", heading=200,
                     alt=24000),
        # Escort Seven holds the convoy at its inspection point, as the
        # 1 November intercept says she will; the surface group is the
        # "northern element" the same intercept names.
        "inspection": S(-10.22, 132.0, "Inspection point", heading=250),
        "air": S(-10.35, 131.85, "Warramunga Flight", heading=320, alt=3000),
        "home": S(-14.5212, 132.3778, "RAAF Base Tindal"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "warramunga",
          variant="Variant3"),
        U("blue", "us-navy-2027", "usn_mh-60r", "air", alt=3000),
        U("red", "chinese-navy-plan", "plan_em_sovremenny", "sag",
          name="Opposing escort", route=[(-10.3, 131.85, 0)], telegraph=3),
        U("red", "type-071-lpd", "plan_lpd_type_071", "sag",
          name="Amphibious transport", route=[(-10.3, 131.85, 0)], telegraph=3),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "inspection",
          name="Meridian Escort 7", route=[(-10.3, 131.85, 0)], telegraph=4),
        # A maritime strike regiment that can strike: the default fit is four
        # short-range air-to-air missiles and three tanks.
        # It used to orbit 97 NM out with a 59-NM YJ-91, so "the counter-strike
        # arrives" never did. It marshals west on the SAG's back-bearing first
        # (so no shot before ~14 minutes: the player gets the surface action),
        # runs down the corridor onto the frigate's box, and goes home.
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike flight lead",
          loadout="AntiShip", route=_SW05_STRIKE, telegraph=3),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike flight two",
          loadout="AntiShip", route=_SW05_STRIKE, telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_freighter_b", "lane",
          name="MV Kupang Trader", route=[(-9.7, 132.2, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_ritina", "lane",
          name="MT Banda Spirit", route=[(-9.75, 132.1, 0)], telegraph=3),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_roro_a", "convoy",
          name="MV Darwin Ranger", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_freighter_b", "convoy",
          name="MV Darwin Provider"),
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
          "one unarmed Triton, and the enclave's J-16s are coming for it.",
    sender="Commodore Alex Mercer; Wing Commander Daniel Ward for the air plan",
    intent=((
        "The convoy needs protection while we establish the northern surface picture. Satellite"
        " and shore reports narrow the search, but they do not provide a continuous local "
        "track. Sentry 06 can classify the group; pushing it north exposes it to the "
        "approaching fighters. Use the available air cover deliberately. Bring back useful "
        "intelligence without losing the convoy to the search."
    )),
    date=(2028, 11, 2), time=(7, 0), sea=3, clouds="Scattered_1", wind="NW",
    difficulty=3, minutes=60, centre=(-11.0, 132.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "ARAFURA SEA, first light. Your flagship is covering a three-ship convoy south-west"
            " toward Darwin and can hold an air picture out to about her own horizon. The "
            "surface group that matters is somewhere north of that line.\\n\\nSENTRY 06 is your "
            "Triton, launched from Tindal, and it is the assigned aircraft for updating the "
            "northern surface search. Earlier satellite detections and merchant reports give a "
            "search area; they do not fix the group's current position. It is unarmed, it is "
            "slow, and a pair of J-16s has come south off the enclave field on a vector that "
            "only makes sense if they know where the orbit is.\\n\\nClassify that surface group "
            "and it stays on your plot for the rest of the morning. To do it the Triton has to "
            "go north, into the part of the sky the J-16s own. Holding "
            "the Triton south reduces its exposure but leaves gaps in the northern search; the "
            "flagship must work with its remaining sensors and earlier reports. If the Korean "
            "detachment reached the join point on the fourth, ROKS SEJONG THE GREAT is in your "
            "screen for this one operation under Captain Han's rules: she fires when fired "
            "upon, or when you are.\\n\\nTwo Tindal F-35As are your entire air cover. You can "
            "spend them protecting the orbit or holding close escort on the convoy. You cannot "
            "do both, and whatever you lose today you do not have tomorrow.\\n\\nIf the group is "
            "classified, expect it to be screening something you have not seen yet, and expect "
            "to find out while the Triton is still north."
        )),
    forces="Your escort group, a three-ship convoy, two RAAF F-35A off Tindal, one MQ-4C Triton, a "
           "Wedgetail on a long orbit. Opposing: two J-16, a Y-20 shuttling "
           "into the enclave, and a surface group not yet located.",
    objectives=[
        ("Convoy", "Get Coral Pioneer and one other merchant to the passage window", "30,-30,Fail,Main"),
        # Fail at the end if never done: holding the Triton south is a
        # playable choice, and it costs fifteen. It used to resolve Complete
        # for +25 whether the group was ever seen or not.
        ("Picture", "Classify the northern surface group", "25,-15,Fail"),
        ("Sentry", "Keep the Triton flying", "25,-25,Complete"),
        ("Hobart", "Your flagship survives", "10,-20,Complete"),
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
                             intel=(
                                 "FUSION CELL / SENTRY 06: The northern group is a Luda "
                                 "destroyer and a Type 054A frigate, with the J-16s that came "
                                 "for the Triton. All of them are identified on the plot and "
                                 "held there for the rest of the operation."
                             ))},
    victory=dict(kind="arrive", station="convoy", at=(-11.9, 130.6), radius=30,
                 min_units=2, objective="Convoy",
                 also=[dict(units=["convoy#3"], min_units=1)]),
    # Losing the Triton is a COST - the objective fails, the intel says what
    # it means for tomorrow, and SW11 starts with a worse picture. It was an
    # instant red victory that cancelled the main objective, which nothing
    # in the text, the bible or the design ever intended.
    fatal=[F("Convoy", ["convoy#3"])],
    neutral_objective="Convoy",
    win="The convoy is through the window. Whatever Sentry 06 brought back or "
        "did not, the convoy is where it is supposed to be, and tomorrow "
        "starts from there.",
    lose=(
        "The escort operation has failed. Command requires the surviving force's positions and "
        "the last confirmed enemy contacts before it can plan another passage."
    ),
    stations={
        "hobart": S(-10.5, 132.0, "Escort", heading=250),
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
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "hobart"),
        U("blue", "SEST_ADF_Persistent_ISR", "raaf_mq-4c_triton", "isr",
          name="Sentry 06", weapons="Hold"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap",
          squadron="Squadron3"),
        U("blue", "raaf-f-35a", "raaf_f-35a", "cap", squadron="Squadron3"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew",
          weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_tindal", "tindal",
          name="RAAF Base Tindal", nation="australia", weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_bulk", "convoy",
          name="MV Weipa Trader", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_freighter_d", "convoy",
          name="MV Gove Provider"),
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
    intro="A tanker with everybody's fuel on board, a flight that cannot get "
          "home without it, and interceptors that can out-reach all of it.",
    sender="Wing Commander Daniel Ward, Air Component, RAAF Tindal",
    intent=("This is a recovery, not a sweep. The tanker is the mission. The "
            "package needs it, the interceptors know where it is, and "
            "Wedgetail can see them coming but cannot stop them. Nothing you "
            "shoot down today is worth the tanker."),
    date=(2028, 11, 5), time=(11, 0), sea=2, clouds="Clear", wind="SE",
    difficulty=3, minutes=50, centre=(-7.0, 133.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        (
            "HIGH OVER THE BANDA ARC. Weather over the enclave pushed the morning package forty"
            " minutes long and everybody is coming home on somebody else's fuel. TEXACO 41 is "
            "the only tanker in the corridor and three different flights are booked on "
            "it.\\n\\nThe Russian expeditionary detachment supporting the enclave has put two "
            "MiG-31s up out of the enclave field, already above fifty thousand feet, on a "
            "vector toward the tanker track. Their AEW aircraft is behind them and their own "
            "tanker is behind that, which tells you this was planned.\\n\\nYou have a USAF Raptor"
            " pair and a Growler with the returning Super Hornets. The MiG-31s have an altitude"
            " and speed advantage on this approach. A stern chase would draw you away from the "
            "tanker and consume the recovery margin. The tanker must cross the recovery line "
            "before the agreed window closes. Break the shot, not the aircraft. Bring the "
            "tanker home."
        )),
    forces="Two F-22 on station, one EA-18G, two returning F/A-18F, a Wedgetail "
           "orbiting to the south, one KC-135, HMAS Arunta "
           "on picket near the track. Opposing: two MiG-31BM, one A-50U, one Il-78.",
    objectives=[
        ("Tanker", "TEXACO 41 must reach the recovery line", "35,-35,Fail,Main"),
        ("Package", "Bring the returning flight home", "20,-25,Complete"),
        ("Raptors", "Do not trade the Raptors for the interceptors",
         "10,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="tanker", at=(-9.4, 132.6), radius=35,
                 min_units=1, objective="Tanker",
                 # "Bring the returning flight home" is a win condition now,
                 # not a tripwire: two of the three have to be at the
                 # recovery line with the tanker.
                 also=[dict(units=["package"], min_units=2)]),
    # The tanker ends it. The package ends it at TWO lost - one Rhino down
    # used to end the mission with a message saying the tanker was gone.
    fatal=[F("Tanker", ["tanker"]), F("Package", ["package"], 2)],
    neutral_objective="Package",
    win=(
        "The tanker and required returning aircraft have reached the recovery line. Account for"
        " the remaining package and pass the current interceptor picture to air control."
    ),
    lose="The tanker is down, or the package is. Either way every sortie in "
         "the north tomorrow gets shorter, and the ones over the enclave do "
         "not happen at all.",
    stations={
        "tanker": S(-7.2, 133.0, "Texaco 41", heading=200, alt=26000),
        "package": S(-6.6, 133.2, "Returning package", heading=200, alt=28000),
        "cap": S(-6.9, 133.4, "Raptor pair", heading=20, alt=40000),
        "red_air": S(-5.6, 132.6, "Interceptor pair", heading=170, alt=52000),
        # On the Foxhounds' back-bearing, as the brief says - "their AEW
        # aircraft is behind them and their own tanker is behind that" - not
        # 150 NM west where nothing on the map could confirm the sentence.
        "red_support": S(-4.6, 132.45, "Support orbit", heading=170, alt=30000),
        "picket": S(-7.6, 133.4, "Surface picket", heading=270),
        # "WEDGETAIL IS ON A LONG ORBIT AND CAN SEE THE SECTION COME SOUTH"
        # - Ward's memo, the page before this mission. South of the tanker
        # track, out of the Foxhounds' reach, recovering on Darwin.
        "aew": S(-8.3, 133.5, "Wedgetail orbit", heading=90, alt=32000),
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
        # Not Perth: she is Variant8, on sale from the first window, and can be
        # lost in Weapons Free or Blind Horizon three days earlier - a blank
        # mission would sail her again, undamaged. Arunta is never sold and
        # sails nowhere else in the campaign.
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "picket", variant="Variant2",
          name="HMAS Arunta"),
        # "On a vector toward the tanker track", then "turned back": a sweep
        # to TEXACO's station (the R-33 reaches 86 NM; the orbit was 99 NM
        # out and never threatened her) and home to their own AEW and tanker.
        # A tanker that leaves at once is never in reach; one that lingers is.
        U("red", "mig-31-foxhound", "wp_mig-31bm", "red_air", name="Foxhound 51",
          route=_SW07_SWEEP, telegraph=3),
        U("red", "mig-31-foxhound", "wp_mig-31bm", "red_air", name="Foxhound 52",
          route=_SW07_SWEEP, telegraph=3),
        U("red", "a-50-il-76", "wp_a-50u", "red_support", name="Mainstay 20",
          weapons="Hold"),
        U("red", "il-78", "wp_il-78", "red_support", name="Midas 30",
          weapons="Hold"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 02",
          weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="08", key="The Open Door", place="Contested enclave",
    intro="Open a seventy-minute relief window over the enclave on Biak, "
          "where Russian advisers are running the air defence.",
    sender="Commodore Alex Mercer",
    intent=((
        "Protect both relief transports and bring at least one into the safe area before the "
        "seventy-minute window closes. Losing either transport ends the operation. Suppress the"
        " battery covering their approach while avoiding the civilian buildings. The relief "
        "movement takes priority over damage to the airfield."
    )),
    detached=True,
    date=(2028, 11, 8), time=(4, 50), sea=2, clouds="Scattered_1", wind="NE",
    difficulty=4, minutes=70, centre=(-2.0, 136.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        (
            "THE ENCLAVE, BIAK, before dawn. Local Indonesian authorities have negotiated a "
            "seventy-minute window to move civilians and emergency supplies out of the port. "
            "The battery covering the approach is an S-400 the first reports called "
            "man-portable. Its crews are from the Russian detachment, not Meridian's hard-line "
            "faction, which seized the airfield.\\n\\nGRIZZLY, the Growler, has the jamming and "
            "the anti-radiation shots, off the US carrier THEODORE ROOSEVELT. The F-35 pair "
            "carries the follow-up strike, out of Langgur on the Kai group - Captain Prasetyo "
            "has lent the strip for this one operation and not an hour longer, and the pair "
            "recovers there, not on the carrier. The two relief KC-130Js are holding to the "
            "west and will not come in while that radar is up. If the coasters got fuel into "
            "Langgur on the tenth, a KC-46 is on the track south of the box and the pair has "
            "additional refuelling support for time on station; if not, the pair has what it "
            "took off with.\\n\\nSuppress the battery, put its launcher out of the argument, and "
            "let the transports through. You are not levelling a regional industrial complex to"
            " do it. Everything on that field that is not shooting at you is somebody's town."
        )),
    forces="One EA-18G off Theodore Roosevelt, two F-35A out of Langgur, "
           "two relief transports. Opposing: an S-400 "
           "battery with its Flap Lid, a ballistic launcher, a modern airbase, "
           "and a small Russian detachment with Hinds, Hips and Frogfoots.",
    objectives=[
        ("Window", "Get the relief aircraft through to the safe box",
         "40,-40,Fail,Main"),
        ("Battery", "Neutralise the surface-to-air battery", "20,-15,Complete"),
        ("Town", "Leave the civilian buildings on the field standing",
         "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="relief", at=(-2.9, 135.2), radius=25,
                 min_units=1, objective="Window"),
    fatal=[F("Window", ["relief"])],
    neutral_objective="Town",
    win=(
        "A relief transport has reached the safe area and both transports remain available. "
        "Report the remaining aircraft and the battery's status so the relief authorities can "
        "plan the next movement."
    ),
    lose="A relief transport is down, and the window with it. The next "
         "negotiation starts from a worse place.",
    stations={
        # The door is BETWEEN the relief and safety now. The transports used
        # to spawn 113 NM south of the battery flying away from it toward a
        # box 230 NM further south - a win by transit that the SEAD had no
        # bearing on. They come from the north-west, outside the site's
        # longest missile, hold a leg for seventeen minutes, then turn in
        # for a box south-west of the field: 55 minutes of flying in a
        # 70-minute window, with the battery between them and it. The
        # package starts 129 NM out - inside the Growler's 140 NM HARM,
        # outside the 130 NM 48N6 - instead of inside the envelope with its
        # radars on.
        "strike": S(-3.15, 136.1, "Strike package", heading=10, alt=30000),
        "relief": S(-0.4, 132.5, "Relief flight", heading=170, alt=14000),
        "box": S(-2.9, 135.2, "Safe box", heading=0),
        "battery": S(-1.0, 136.0, "S-400 battery", heading=180),
        "field": S(-1.1, 136.2, "Enclave airfield", heading=90),
        "detach": S(-1.2, 136.4, "Foreign detachment", heading=180, alt=4000),
        "port": S(-4.5, 137.0, "Civilian port", heading=0),
        "coaster": S(-3.0, 135.3, "Relief coaster", heading=90),
        "sea": S(0.5, 135.5, "Offshore picket", heading=180),
        # The Growler's deck. The RAAF F-35A file says CarrierCapable=False,
        # so the pair cannot use it: the nearest Australian field is
        # Scherger, 707 NM south, outside a 547 NM radius, and the answer is
        # the Indonesian strip on the Kai group that SW10's F-2As also use -
        # 230 NM from the package, inside the radius, on proven ground, and
        # in the fiction Prasetyo's to lend. It is placed whether or not
        # any optional operation was flown: SW08 must launch on its own.
        "cvn": S(-4.3133, 135.8867, "Carrier group"),
        "strip": S(-5.2953, 132.9232, "Langgur forward strip"),
    },
    units=[
        # No home field: the nearest Australian base is Scherger, 707 NM
        # south, which is not a sortie. These aircraft keep unlimited fuel -
        # the game's own tooltip prescribes exactly that when no airbase is
        # available, and a base on the map that nothing can reach is worse
        # than none.
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_ea-18g", "strike",
          squadron="Squadron6"),
        # "The F-35 pair carries the follow-up": JSM, 120 NM, internal. They
        # carried four AIM-120s.
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "strike",
          squadron="Squadron3", loadout="StrikeLongRangeStealth"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "strike",
          squadron="Squadron3", loadout="StrikeLongRangeStealth"),
        U("blue", "us-naval-aviation", "usmc_kc-130j", "relief",
          name="Relief 61", alt=12000, weapons="Hold",
          route=[(-1.6, 132.8, 14000), (-2.9, 135.2, 14000)]),
        U("blue", "us-naval-aviation", "usmc_kc-130j", "relief",
          name="Relief 62", alt=12000, weapons="Hold",
          route=[(-1.6, 132.85, 14000), (-2.9, 135.25, 14000)]),
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
        # On the field, beside the airbase and the launcher - "everything on
        # that field that is not shooting at you is somebody's town". They
        # used to sit 211 NM away where no strike could have touched them.
        U("neutral", "buildings-targets-missions", "Coal_PowerPlant", "field",
          name="Field power station"),
        U("neutral", "buildings-targets-missions", "4tentgroup", "field",
          name="Civilian shelter camp"),
        U("neutral", "_vanilla", "civ_ms_encounter", "coaster",
          name="Relief coaster"),
        U("blue", "modern-us-navy", "usn_cvn_nimitz_2025", "cvn",
          name="USS Theodore Roosevelt"),
        U("blue", "_vanilla", "airfield_small_1", "strip",
          name="Langgur forward strip", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="09", key="Southern Lifeline", place="Rear support area",
    intro="HMAS Collins on the surface alongside the replenishment ship HMAS "
          "Stalwart: the most vulnerable thing either of them will ever do.",
    special=(
        "STALWART and COLLINS must both be inside the five-nautical-mile service area at the "
        "35-minute check, then reach the withdrawal line together. Completion releases the next"
        " ammunition allocation for Common Sea."
    ),
    sender="Commodore Alex Mercer; Commander Mara Kila for the eastern route",
    intent=((
        "Protect Stalwart and Collins at the service rendezvous. Both must be inside the area "
        "for the 35-minute check and then withdraw south together. Collins is exposed while "
        "surfaced, and enemy reconnaissance has been reported nearby. Keep the approaches "
        "covered and bring both vessels out."
    )),
    date=(2028, 11, 11), time=(6, 30), sea=2, clouds="Broken_2", wind="SE",
    difficulty=3, minutes=85, centre=(-12.5, 146.0),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        # The engine has no dwell, alongside, surfaced or depth predicate -
        # eleven condition types across the whole shipped corpus and not one
        # of them measures time spent in an area, a unit's speed or its
        # depth. What it does have is `03 Lifeline` Trigger8: an area test
        # AND a clock, on units that start inside the area. So the window is
        # scored as "both ships still in the box when the window closes",
        # and the briefing states exactly that rule. Surfaced stays a house
        # rule, in the fiction's own voice. The transfer the brief describes
        # is the one the data sets up: SEST RAN Fleet gives STALWART the
        # supply system in integration/common/ras.py (half a mile, 12 kn for
        # her and 16 for the receiver, nothing dearer than the NSM's 8000
        # points), and what it says crosses is what that system passes. It
        # is just not what is scored.
        (
            "REAR SUPPORT AREA, Coral Sea, east of Cape York. COLLINS has been out for "
            "thirty-five days and comes home next week whatever happens today. She is surfaced "
            "alongside STALWART taking fuel, stores and torpedoes, and putting two crew across "
            "for medical, and while she is up there she is a very large grey target making four"
            " knots.\\n\\nThe service window is thirty-five minutes and it runs on the clock, "
            "not on how much crossed the hose. What crosses is real: STALWART passes COLLINS her"
            " torpedoes, and any escort that comes inside half a mile at twelve knots or less "
            "can take missiles back across - she will pass anything up to an NSM, a Tomahawk or"
            " an SM-6 - for as long as her magazines last. STALWART and COLLINS have to be "
            "inside the service box - five miles around the rendezvous - when the window "
            "closes; what you do with them in between is your judgement, and the clock does not"
            " stop for you. Hold it and your ships are rearmed before the Banda convoy on the "
            "twentieth; miss it and they sail that convoy on what they have left. When the "
            "thirty-five minutes are up, both of them go together to the withdrawal line "
            "eighteen miles south, and COLLINS dives the moment she is clear of the "
            "hose.\\n\\nSTALWART has the duty. MV Coral Provider was pencilled in with the dry "
            "stores; she sails only if SUPPLY survived the Gulf of Papua passage in "
            "October.\\n\\nA Russian Tu-214R came down the outside of the box last night and "
            "did not go home, which usually means somebody now knows where to look. There is an"
            " Akula unaccounted for to the south-east, and a Flanker pair within range of here "
            "with a Helix spotting for them off a tender that has been loitering north of the "
            "box since Tuesday. Assume one of those Flankers is carrying something for a ship. "
            "Keep the window open and get everybody out of it."
        )),
    forces="HMAS Stalwart, HMAS Collins surfaced for service, your escort and "
           "her flight; one P-8 from Scherger if tasked. Opposing, all Russian: one Akula, "
           "one Tu-214R, a Flanker pair with a Ka-27RLD spotting for them.",
    objectives=[
        ("Service", (
            "Have STALWART and COLLINS inside the service area at 35 minutes, then bring both "
            "to the southern withdrawal line"
        ), "35,-35,Fail,Main"),
        ("Collins", "HMAS Collins must survive", "25,-35,Complete"),
        ("Supply", "HMAS Stalwart must survive", "20,-30,Complete"),
    ],
    # Stalwart AND Collins, not "any two of the group" - the freighter could
    # otherwise stand in for the submarine the mission is about. The window
    # is the stage: both ships still inside five miles of the rendezvous
    # WHEN the clock reaches thirty-five minutes (03 Lifeline Trigger8's
    # shape). Dive and run at t=0 and the stage never fires, so the
    # withdrawal line never opens. The line itself is authored, not solved:
    # the group sits in open water where nothing snaps, and the solver does
    # not know that the first thirty-five minutes are spent standing still.
    victory=dict(kind="arrive", units=["support#1", "support#2"], min_units=2,
                 station="support", objective="Service",
                 at=(-13.8, 148.35), radius=12,
                 after=dict(kind="area", units=["support#1", "support#2"],
                            at_unit="support#1", radius=5, min_units=2,
                            after_minutes=35, sets="SW09ServiceHeld",
                            intel=(
                                "SERVICE CONTROL: Stalwart and Collins are inside the area at "
                                "the scheduled check. The protected rendezvous is complete and "
                                "the next ammunition allocation is released. Withdraw both "
                                "vessels south together. The last reconnaissance report remains"
                                " a warning, not a confirmed incoming raid."
                            ))),
    # Each named participant ends the mission by being lost, and fails its
    # own objective. MV Coral Provider is deliberately not here: she carries
    # no objective, she only exists when SUPPLY survived Steel Highway, and
    # as a third member of the "support" station she was a silent defeat
    # condition that reported Collins sunk while Collins was alongside.
    fatal=[F("Collins", ["support#2"]), F("Supply", ["support#1"])],
    neutral_objective="Service",
    win=(
        "Stalwart and Collins have completed the service check and reached the southern "
        "withdrawal line. Command can release the next ammunition allocation. Kila, from "
        "Moresby: 'Send the next one.'"
    ),
    lose="The support group is broken. Every boat in the north now has to come "
         "all the way home to do what should take four hours out here.",
    stations={
        "support": S(-13.5, 148.4, "Support group", heading=200),
        # Her own station: a conditional hull inside an unconditional
        # formation is a shape no vanilla file uses (10 Vengeance at Luzon's
        # one SpawnByVariable formation is conditional throughout).
        "stores": S(-13.45, 148.33, "Dry stores", heading=200),
        "escort": S(-13.62, 148.55, "Escort", heading=160),
        # On the threat axis, not thirty miles north of it.
        "air": S(-13.7, 148.65, "Perth Flight", heading=135, alt=3000),
        "mpa": S(-13.2, 148.9, "Maritime patrol", heading=135, alt=8000),
        "cape": S(-12.5, 142.0, "Cape York strip", heading=0),
        # Fifty miles east-south-east and closing at twenty knots: across the
        # withdrawal track about when the window closes, and inside the
        # Seahawk's reach from the first minute. She used to be 204 NM away,
        # pointed elsewhere, with no route - set dressing with torpedoes.
        "red_sub": S(-14.0, 149.1, "Akula datum", heading=290),
        # Now only the Ka-27RLD, on the seat it held beside the scout and
        # the Flankers before they were split off.
        "red_air": S(-11.05, 148.0, "Opposing aviation", heading=180, alt=30000),
        # Split off red_air so neither routed flight follows an orbiting
        # leader; both keep the spawns they had there.
        "red_scout": S(-11.0, 148.0, "Scout", heading=180, alt=34000),
        "red_raid": S(-11.0, 148.05, "Flanker pair", heading=180, alt=30000),
        "home": S(-12.6188, 142.094, "RAAF Base Scherger"),
    },
    units=[
        # The sister ship, not SUPPLY: Steel Highway can sink SUPPLY and
        # the campaign says so in as many words. A hull the campaign has
        # never sunk is the only one that can be the centrepiece here
        # without lying to the player who lost the other one.
        U("blue", "SEST_RAN_Fleet", "ran_aor_supply", "support",
          variant="Variant2", name="HMAS Stalwart"),
        U("blue", "SEST_RAN_Fleet", "ran_ssg_collins", "support",
          name="HMAS Collins (surfaced)"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant8"),
        U("blue", "re-power-resupply", "civ_ms_amra", "stores",
          name="MV Coral Provider"),
        U("blue", "us-navy-2027", "usn_mh-60r", "air",
          alt=2500),
        U("blue", "buildings-targets-missions", "FOB", "cape",
          name="Cape York forward strip", weapons="Hold"),
        U("red", "russian-submarines", "wp_ssn_akula", "red_sub",
          name="Contact VICTOR", depth="belowlayer",
          route=[(-13.75, 148.5, "belowlayer")], telegraph=5),
        # "A scout is coming to look at it and a raid may follow it." The
        # scout looks from 33 NM west of the box, then leaves (the stage
        # intel speaks of where it WAS looking). Its own station, so it no
        # longer leads the Flankers' formation while orbiting.
        U("red", "tu-214r-family", "msdvd_tu-214r", "red_scout",
          name="Coot-A 90", alt=34000, weapons="Hold",
          route=[(-13.5, 147.85, 34000), (-11.0, 148.0, 34000)], telegraph=3),
        # One of the pair carries Kh-31A, so the "Flanker pair within range
        # of here" is a threat to the ships and not only to the helicopter.
        # The raid comes down the outside of the box and its Kh-31A window
        # opens at about 30 minutes - inside the service window, before the
        # ESSM envelope - then it goes home. A straight run would have shot
        # at 12 minutes, before the scout had looked at anything.
        U("red", "flanker-family", "wp_su-30m", "red_raid", name="Flanker 21",
          loadout="AntiShip", route=_SW09_RAID, telegraph=3),
        U("red", "flanker-family", "wp_su-30m", "red_raid", name="Flanker 22",
          route=_SW09_RAID, telegraph=3),
        U("red", "ka-27rld", "wp_ka-27rdl", "red_air", name="Helix RLD 55",
          alt=9000, weapons="Hold"),
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        U("blue", "p-8-poseidon", "usn_p8", "mpa"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_scherger", "home",
          name="RAAF Base Scherger", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="10", key="Common Sea", place="Eastern Banda corridor",
    intro="A Japanese ASW detachment brings the one thing the Australian "
          "force has run out of: escorts that can hunt.",
    sender="Commodore Alex Mercer",
    intent=("Let the Japanese escorts hunt; that is what they are here for. "
            "The convoy is the cargo, the submarine is theirs, the frigate "
            "from the east is the F-2A pair's one sortie, and the fighters "
            "overhead are yours. Bring both Japanese ships home - the "
            "corridor still needs them after today."),
    date=(2028, 11, 15), time=(13, 40), sea=3, clouds="Scattered_1", wind="E",
    difficulty=3, minutes=75, centre=(-6.5, 133.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        "EASTERN BANDA CORRIDOR. If STALWART's service window held on the "
        "sixteenth, your magazines were refilled; if not, you sail on what "
        "Southern Lifeline left you. The convoy has to cross a patrol box "
        "where a submarine and a surface threat overlap, and five weeks in, the "
        "Australian escort force cannot cover both.\\n\\n"
        "MOGAMI and MAYA sail under Tokyo's orders, not ours, with an SH-60K "
        "and an SH-60J that are the best ASW "
        "pair in this sea. A Japanese F-2A pair forward at Langgur, in the Kai "
        "Islands, has one sortie today and it is loaded for ships: use it on "
        "the frigate coming in from the east, not on the fighters.\\n\\n"
        "Two of the three priority merchants have to reach the handover, and "
        "CORAL PIONEER has to be one of them; lose her, or lose two, and the "
        "corridor is closed. The Type 039C is the real danger - she carries "
        "YJ-18 as well as torpedoes, and the four fighters coming down from "
        "the Biak enclave are her eyes as much as they are the reason you "
        "spend the day looking up instead of down. One of them is "
        "carrying something for a ship."),
    forces="JS Mogami and JS Maya with an SH-60K and an SH-60J, one F-2A pair "
           "from Langgur, your escort group and the convoy. Opposing: a Type "
           "039C, a Type 054A frigate from the east, a J-11BG, a J-11BS, a "
           "Su-27UBK and a J-10C off the Biak enclave field.",
    objectives=[
        ("Cargo", "Two of the three priority merchants, Coral Pioneer among "
                  "them, reach the handover point", "35,-35,Fail,Main"),
        ("Allies", "Keep the Japanese escorts in the fight", "20,-25,Complete"),
        # Scored on the text: classified, not sunk. It used to pay out at
        # mission end whether or not a helicopter ever left the deck.
        ("Submarine", "Locate and classify the submarine", "15,-10,Fail"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(-8.5, 134.5), radius=30,
                 min_units=2, objective="Cargo",
                 also=[dict(units=["convoy#2"], min_units=1)]),
    fatal=[F("Cargo", ["convoy"], 2), F("Cargo", ["convoy#2"])],
    neutral_objective="Cargo",
    win="The cargo is at the handover. Whatever it cost the detachment to get "
        "it there, the corridor has two escort forces that can hunt, for the "
        "first time since October.",
    lose="The convoy is short and the allied detachment is going home for "
         "repairs. The corridor is back to one navy again.",
    stations={
        "jmsdf": S(-7.0, 133.0, "Japanese detachment", heading=160),
        "convoy": S(-6.6, 132.8, "Priority convoy", heading=160),
        "escort": S(-6.8, 133.2, "Escort", heading=160),
        # Ahead of the convoy on the handover bearing, first dip over the
        # datum.
        "helo": S(-6.9, 133.0, "ASW pair", heading=150, alt=3000),
        "mpa": S(-6.4, 132.6, "Maritime patrol", heading=160, alt=15000),
        # East of the convoy and a hundred miles from the fighters, pointed
        # at the surface group. They used to spawn 17 NM in front of four
        # Flankers, inside PL-15 range at second zero.
        "f2": S(-6.45, 133.25, "Kai detachment", heading=120, alt=24000),
        # Across the solved handover track, 38 NM from the convoy and inside
        # Yu-6 range of it before the cargo is halfway. She used to sit 144
        # NM away, pointed elsewhere, with no route, six miles from a
        # handover point the solver had long since moved.
        "red_sub": S(-7.05, 133.25, "Submarine datum", heading=320),
        # A hundred miles out, so the fighters arrive over a quarter of an
        # hour instead of at spawn.
        "red_air": S(-4.7, 133.4, "Enclave fighters", heading=180, alt=32000),
        # The surface half of "where the submarine and surface threats
        # overlap": a hundred miles east of the handover and closing, inside
        # YJ-83 range of it about when the convoy arrives. The F-2As' ASM-3
        # reaches her from their station; so does Perth's NSM. One hull, not
        # a group: an escort mission fields six red combat units at most, and
        # the fighters and the boat are the other five. The Tor that used to
        # sit on the Kai group 66 NM from the handover went the same way.
        "red_sag": S(-7.7, 134.6, "Opposing frigate", heading=290),
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
        U("blue", "euromod-jmsdf", "jmsdf_sh-60k", "helo"),
        # Euromod JMSDF renamed its Seahawks from jp_ to jmsdf_ (19 Sep
        # 2026). Mogami (SEST_JMSDF_Mogami) and Maya now list both ids.
        U("blue", "euromod-jmsdf", "jmsdf_sh-60j", "helo"),
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant8"),
        U("blue", "f-2a-viper-zero", "jp_f-2a_late", "f2", name="Viper 61",
          loadout="AntiShip"),
        U("blue", "f-2a-viper-zero", "jp_f-2a_late", "f2", name="Viper 62",
          loadout="AntiShip"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_antares", "convoy",
          name="MV Antares", weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "re-power-resupply", "civ_ms_freighter_a", "convoy",
          name="MV Kai Trader"),
        U("red", "plan-submarines", "plan_ss_type_039c", "red_sub",
          name="Contact SIERRA", depth="belowlayer",
          route=[(-6.75, 132.95, "belowlayer")], telegraph=3),
        U("red", "j-11", "plaaf_j-11bg", "red_air", name="Flanker 31",
          route=[(-6.7, 132.9, 30000)], telegraph=3),
        U("red", "j-11bs", "plaaf_j-11bs", "red_air", name="Flanker 32",
          route=[(-6.7, 132.9, 30000)], telegraph=3),
        U("red", "su-27ubk", "plaaf_su-27ubk", "red_air", name="Flanker 33",
          route=[(-6.7, 132.9, 30000)], telegraph=3),
        # YJ-91 under the J-10C: the one red aircraft that can reach a
        # merchant, so Maya's SM-2 has something to do.
        U("red", "j-10c", "plaaf_j10c", "red_air", name="Dragon 41",
          loadout="AntiShip", route=[(-6.7, 132.9, 30000)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_sag",
          name="Type 054A frigate", route=[(-7.0, 133.2, 0)], telegraph=4),
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        U("blue", "p-8-poseidon", "usn_p8", "mpa"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
        U("blue", "_vanilla", "airfield_small_1", "strip",
          name="Langgur forward strip", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="core", num="11", key="Fujian's Shadow", place="Wider Banda approaches",
    intro="The Chinese carrier Fujian and her group have come to close the "
          "corridor before the ceasefire talks open. You do not have to sink "
          "them. You have to get the transports through alive.",
    sender="Commodore Alex Mercer",
    intent=("Keep the transports moving and Ford afloat, and let their "
            "commander spend fuel he cannot replace coming to you. He knows "
            "it: his own signal to fleet headquarters on the twenty-second "
            "says so."),
    date=(2028, 11, 19), time=(10, 15), sea=4, clouds="Broken_2", wind="NE",
    difficulty=4, minutes=90, centre=(-4.5, 130.0),
    blue_nation="USA", red_nation="China",
    brief=(
        (
            "WIDER BANDA APPROACHES. The ceasefire talks open on Friday and the opposing fleet "
            "has been told to make the corridor unusable before they do. FUJIAN is a hundred "
            "and thirty miles north-north-west with LIAONING astern of her, screened by a Luda,"
            " a Sovremenny and a Type 054A, and the strike she is building is aimed at the "
            "transports, at FORD and at you.\\n\\nFORD arrived on Tuesday on Washington's terms: "
            "one strike group, a fixed window in theatre, and a departure date that does not "
            "move. You have her air wing, two Burkes and the last of the Australian "
            "escorts.\\n\\nThe protected transports and FORD herself have to come out of this "
            "usable. If their carrier turns north having achieved nothing, that is the whole "
            "victory - you are not chasing it across the Celebes Sea to prove a "
            "point.\\n\\nINTELLIGENCE: Satellite imagery and intercepted naval traffic provided "
            "the carrier group's last reported area. Ford's aircraft and the task group's "
            "sensors must establish its current formation and movement. Gaps between "
            "collections allow ships to change course; correlate the overhead report with local"
            " detections before an attack."
        )),
    forces="USS Gerald R. Ford with F-35Cs, a Growler and a Hawkeye, two "
           "Arleigh Burkes, your own escort group, three protected transports. "
           "Opposing: Fujian with J-35 and J-15D, Liaoning, a J-20 and a "
           "KJ-600, three escorts and a submarine.",
    objectives=[
        ("Transports", "Two of the three transports, Coral Pioneer among "
                       "them, pass to the south-east",
         "40,-40,Fail,Main"),
        ("Ford", "USS Gerald R. Ford must survive", "30,-40,Complete"),
        ("Strike", "Shoot down the YJ-83-armed J-15D before it launches",
         "15,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="transports", at=(-7.0, 130.0),
                 radius=35, min_units=2, objective="Transports",
                 also=[dict(units=["transports#2"], min_units=1)]),
    # Two transports lost ends it (the reviewed build waited out the clock);
    # Coral Pioneer lost ends it on her own.
    fatal=[F("Ford", ["carrier"]), F("Transports", ["transports"], 2),
           F("Transports", ["transports#2"])],
    neutral_objective="Transports",
    win=(
        "The required transports have cleared to the south-east and Ford remains afloat. The "
        "ceasefire talks can proceed with the corridor open. Report the condition of the "
        "surviving ships and any enemy units still in contact."
    ),
    lose="The corridor is closed and the talks open with that as the first "
         "fact on the table.",
    stations={
        "carrier": S(-4.5, 130.0, "Ford strike group", heading=140),
        "escort": S(-4.6, 130.2, "Escort screen", heading=140),
        "transports": S(-5.0, 128.2, "Protected transports", heading=120),
        "cvw": S(-4.2, 130.4, "Carrier air wing", heading=320, alt=28000),
        "red_cv": S(-2.5, 129.0, "Opposing carrier group", heading=140),
        "red_air": S(-2.7, 129.2, "Opposing air wing", heading=205, alt=30000),
        "red_strike": S(-2.7, 129.25, "Anti-ship shooter", heading=205, alt=30000),
        "red_aew": S(-2.7, 129.3, "KJ-600", heading=205, alt=30000),
        "red_j20": S(-2.75, 129.2, "J-20A", heading=205, alt=30000),
        "red_sub": S(-4.9, 129.2, "Submarine screen", heading=140),
        # The Kai strip Prasetyo lent for The Open Door, still ours ten days
        # later: the only field inside a purchased F-35A's radius of the
        # carrier's air wing, and where a land-based aircraft in a CAP or
        # Attack slot recovers.
        "strip": S(-5.2953, 132.9232, "Langgur forward strip"),
    },
    units=[
        U("blue", "ford-cvn", "usn_cvn_ford", "carrier",
          name="USS Gerald R. Ford"),
        # The anchor - the player's flagship - is the Australian ship; the
        # two Burkes are scripted and stay whatever the player brought.
        U("blue", "SEST_RAN_Fleet", "ran_ddg_hobart", "escort"),
        # Both Flight III, each on the variant that carries her own hull
        # number: Variant1 is DDG-125, Variant2 DDG-126. Lucas used to sail
        # as usn_ddg_burke_f2a_g4_2022, a Flight IIA group file painted
        # DDG-97. Modern US Navy no longer ships it - the Flight IIA went to
        # per-ship files on 16-17 Sep 2026 and the mirrored 20 Sep export has
        # no group files - and it resolved here only because the export
        # never deleted. The game has no such unit.
        U("blue", "modern-us-navy", "usn_ddg_burke_f3_125", "escort",
          variant="Variant1", name="USS Jack H. Lucas"),
        U("blue", "us-navy-2027", "usn_ddg_arleigh_flt3_2027", "escort",
          variant="Variant2", name="USS Louis H. Wilson Jr."),
        U("blue", "SEST_F-35C_JATM", "usn_f-35c", "cvw",
          loadout="AirToAirAMRAAM"),
        U("blue", "SEST_F-35C_JATM", "usn_f-35c", "cvw",
          loadout="AirToAirAMRAAM"),
        U("blue", "SEST_Growler_NGJ_MALICE", "usn_ea-18g_2020", "cvw"),
        U("blue", "us-naval-aviation", "usn_e-2d", "cvw", name="Hawkeye 601",
          alt=27000, weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_super_p", "transports",
          name="MV Milne Trader", weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "transports",
          name="MV Coral Pioneer"),
        # NOT Lae Provider: the contingency after STEEL HIGHWAY opens with her
        # going down at 2140 with twenty-six aboard, and that beat is offered
        # unconditionally. A sunk ship cannot be carrying cargo nine missions
        # later, whether or not the player flew the search for her.
        U("blue", "re-power-resupply", "civ_ms_andizhan", "transports",
          name="MV Moresby Star"),
        U("blue", "_vanilla", "airfield_small_1", "strip",
          name="Langgur forward strip", weapons="Hold"),
        U("red", "fujian-cv-18", "plan_cv_type_003", "red_cv", name="PLANS Fujian"),
        U("red", "liaoning-type-001", "plan_type_001", "red_cv",
          name="PLANS Liaoning"),
        # No Type 055 or 052D: their files load YJ-17/YJ-20 hypersonics of
        # ~1000 NM that decided whether Ford lived from beyond any reach the
        # player has, and the bible keeps them out. These are the classes
        # Sentry 06 put a name to on 6 November, plus a Sovremenny.
        U("red", "chinese-navy-plan", "plan_ddg_luda_typ_051dt", "red_cv",
          name="Luda destroyer"),
        U("red", "chinese-navy-plan", "plan_em_sovremenny", "red_cv",
          name="Sovremenny destroyer"),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "red_cv",
          name="Type 054A escort"),
        # A carrier group without a submarine screen is a missile exchange.
        # This is the campaign's one fleet action; it should be the mission
        # where the player cannot watch every axis at once.
        U("red", "plan-submarines", "plan_ssn_type_093b", "red_sub",
          name="Contact ROMEO"),
        U("red", "fujian-cv-18", "plan_j-35", "red_air", name="Falcon 11"),
        # The one anti-ship shooter in the air wing: two YJ-83, pointed at
        # the transports. Strike is scored on this aircraft, not on the AEW.
        # Its own station: as the second member of red_air's formation its
        # route sat under an unrouted J-35 leader, a shape no stock file uses.
        # Strike is scored on red_strike, not red_air#2 - after the move that
        # index would have been the KJ-600.
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_strike",
          name="Flying Shark 21", loadout="AntiShip",
          route=[(-5.0, 128.2, 20000)], telegraph=3),
        # Their own stations, on the seats they held before the J-15D left
        # red_air: re-seated, the KJ-600 moved 3 NM and the J-20A 6.7 NM,
        # which tipped its nearest deck from Liaoning to Fujian.
        U("red", "type-003-004-maneuverwarfare", "pla_kj-600", "red_aew",
          name="KJ-600 Eye", alt=26000, weapons="Hold"),
        U("red", "j-20", "plaaf_j-20a", "red_j20", name="Dragon 51"),
    ],
))

MISSIONS.append(dict(
    group="core", num="12", key="The First Ship Through", place="Arafura Sea",
    intro="An imperfect ceasefire, Coral Pioneer with a cracked bearing, and "
          "two Chinese naval groups out there - one complying and one deciding.",
    sender="Commodore Alex Mercer",
    intent=("Coral Pioneer, nine knots, one shaft. Tell the two groups apart "
            "before you fire: the ceasefire is what six weeks were for, and "
            "one mistake today reopens all of it."),
    date=(2028, 11, 26), time=(6, 20), sea=2, clouds="Scattered_1", wind="NW",
    difficulty=3, minutes=65, centre=(-10.0, 131.0),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "ARAFURA SEA. The ceasefire came into effect at 0000 on 27 November, and the first "
            "convoy sails at first light today because insurers move faster than diplomats. "
            "CORAL PIONEER is at the head of it, with a bearing running hot and nine knots she "
            "can hold.\\n\\nThere are two Chinese naval groups in the box. One "
            "has acknowledged its withdrawal order and is heading north at steady speed. The "
            "other has not acknowledged anything since 0400 and, if FUJIAN is still afloat, has"
            " a maritime strike flight within range.\\n\\nTell them apart. Get the convoy home. "
            "Do not be the incident that restarts this - a withdrawing ship you sink today is "
            "the reason the ceasefire fails before this convoy reaches port."
        )),
    forces="Your escort group with HMAS Eyre and her flight attached, a Poseidon, and "
           "four merchant hulls. Two Chinese groups: one withdrawing, one "
           "not. A Wedgetail is up.",
    objectives=[
        ("Convoy", "Bring three of the four merchants, Coral Pioneer among "
                   "them, into Darwin's approaches",
         "40,-40,Fail,Main"),
        ("Ceasefire", "Do not sink a withdrawing ship", "20,-35,Complete"),
        ("Escorts", "Bring the escorts home", "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="convoy", at=(-12.0, 130.5), radius=30,
                 min_units=3, objective="Convoy",
                 # Nine knots, one shaft: the box is solved at her speed.
                 transit=9,
                 also=[dict(units=["convoy#1"], min_units=1)]),
    fatal=[F("Convoy", ["convoy"], 2), F("Convoy", ["convoy#1"])],
    neutral_objective="Ceasefire",
    win=(
        "The required merchants, including Coral Pioneer, have reached the Darwin handover. The"
        " withdrawing formation remains protected. Account for the remaining convoy before "
        "reporting the passage complete. Santos, on channel 16: 'Nine knots was enough. Thank "
        "you, escort.'"
    ),
    lose="The first ship through did not get through, and the ceasefire is "
         "now a thing that was tried once.",
    stations={
        "escort": S(-10.48, 131.77, "Escort group", heading=200),
        "eyre_flight": S(-10.52, 131.8, "Eyre Flight", heading=200, alt=1500),
        "convoy": S(-10.4, 131.8, "First convoy", heading=200),
        "air": S(-10.8, 131.0, "Air support", heading=200, alt=20000),
        # Two fighter cockpits for whatever the finale's window sold, off
        # Darwin's own field.
        "cap": S(-11.2, 130.9, "Fighter cover", heading=20, alt=30000),
        "aew": S(-11.5, 130.8, "Wedgetail orbit", heading=90, alt=32000),
        # 30 NM off the convoy's bow and opening at 340: close enough that
        # the player has to tell it from the spoiler and hold fire on it,
        # which is the mission. It used to be 73 NM away.
        "withdraw": S(-10.02, 131.47, "Withdrawing group", heading=340),
        "spoiler": S(-9.1, 131.9, "Unacknowledged group", heading=180),
        # The boat ahead of the convoy's track, twenty miles down it, so the
        # Seahawk and the P-8 have a reason to exist; it used to sit 78 NM
        # away with no route.
        "spoiler_sub": S(-10.7, 131.65, "Unacknowledged submarine", heading=20),
        "spoiler_air": S(-9.2, 132.0, "Strike flight", heading=180, alt=24000),
        "darwin": S(-12.4, 130.9, "Darwin", heading=0),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant3",
          weapons="Tight"),
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "escort",
          variant="Variant2", name="HMAS Eyre", weapons="Tight"),
        # Eyre's own flight: the S-70B-2 the RAN deck lists, on the RAN deck.
        U("blue", "s-70b-2-seahawk", "S-70B-2_Seahawk", "eyre_flight",
          name="Eyre Flight", alt=1500, weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "air", squadron="Squadron3", alt=18000, weapons="Tight"),
        U("blue", "e-7a-wedgetail", "E7A_Wedgetail", "aew", name="Wedgetail 03",
          weapons="Hold"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "darwin",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
        U("blue", "merchants-expanded", "civ_ms_mairangi_bay", "convoy",
          name="MV Coral Pioneer"),
        U("blue", "auxilliary-merchant-pack", "ran_ms_jeparit", "convoy",
          name="MV Wewak", weapons="Hold"),
        U("blue", "auxilliary-merchant-pack", "anl_ms_bulk", "convoy",
          name="MV Nhulunbuy", weapons="Hold"),
        U("blue", "re-power-resupply", "civ_ms_freighter_b", "convoy",
          name="MV Arnhem Trader"),
        # "Heading north at steady speed": a route, not a heading.
        U("neutral", "chinese-navy-plan", "plan_ddg_luda_typ_051d", "withdraw",
          name="Withdrawing escort", route=[(-9.55, 131.3, 0)], telegraph=3),
        U("neutral", "type-071-lpd", "plan_lpd_type_071", "withdraw",
          name="Withdrawing transport", route=[(-9.55, 131.3, 0)], telegraph=3),
        U("red", "modern-plan-systems", "plan_type_054a_p5", "spoiler",
          name="Unacknowledged escort", route=[(-10.1, 131.6, 0)], telegraph=4),
        U("red", "chinese-navy-plan", "plan_ss_kilo", "spoiler_sub",
          name="Unacknowledged submarine", depth="belowlayer",
          route=[(-10.6, 131.55, "belowlayer")], telegraph=2),
        # Loaded for ships, as the brief says it is.
        # It orbited 73 NM out with a 59-NM YJ-91. Now it opens east first
        # (no shot for ~20 minutes), comes in over the convoy and goes home.
        U("red", "jh-7a", "plaaf_jh7a", "spoiler_air", name="Strike flight 71",
          loadout="AntiShip", telegraph=3,
          route=[(-9.0, 133.5, 24000), (-10.9, 131.5, 24000), (-9.2, 132.0, 24000)]),
        # Air-tasking placeholder: no name, no objective, no line in the
        # briefing. Its only job is to be a cockpit a purchased aircraft can
        # take, the way every slot-tagged section in the shipped campaign is.
        U("blue", "us-navy-2027", "usn_mh-60r", "air"),
        U("blue", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "cap"),
        U("blue", "raaf-f-35a", "raaf_f-35a", "cap", squadron="Squadron3"),
    ],
))

# =============================================================================
# DISPATCHES - optional episodes. They sit outside the twelve-mission spine
# and give the rest of the collection a purposeful role instead of forcing a
# Spanish frigate or a 1988 bomber into an Australian 2028 convoy escort.
# =============================================================================

# =============================================================================
# THE OPTIONAL OPERATIONS AND THE SECOND CONTINGENCY
#
# Each one is a real trade-off with a consequence a later mission reads
# through a campaign variable (the guide's IsTrue form): skip it and the core
# campaign plays unchanged; fly it and something specific is better later.
# None of them grants a unit to the player's roster - allied aircraft and
# ships are theatre contributions that appear where the story puts them.
# =============================================================================

MISSIONS.append(dict(
    group="optional", num="O2", key="Southern Cross",
    place="Arafura Sea, north of Melville", expires_after="Rig Seventeen",
    intro="Optional. New Zealand has lent one Poseidon for one sortie. What "
          "she finds today is on your plot next week.",
    special=(
        "New Zealand has allocated Kiwi 01 for one sortie, with HMAS Pilbara supporting this "
        "detached operation. Your standing task group remains on its other duties. Identify the"
        " coaster and return the aircraft to the Darwin handover; the report can support the "
        "patrol of 30 October."
    ),
    sender="Commodore Alex Mercer; Squadron Leader Tane Rewi, No. 5 Squadron "
           "RNZAF, for the aircraft",
    intent=("Wellington has given us one Poseidon and one sortie, and Rewi "
            "flies it his way. Put a name on the coaster that has been "
            "shadowing the lane with her transponder off, keep the aircraft "
            "out of the Meridian escort boat's reach, and bring her home. "
            "The picture is "
            "the prize; the aircraft is not ours to spend."),
    date=(2028, 10, 24), time=(10, 30), sea=3, clouds="Scattered_1", wind="E",
    difficulty=2, minutes=70, centre=(-10.5, 131.2),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "ARAFURA SEA, mid-morning. A coaster with no transponder has been pacing the lane "
            "for three days, always outside the twelve-mile limit, always where the next convoy"
            " will be. Her name is what we want.\\n\\nKIWI 01 is a New Zealand Poseidon out of "
            "Darwin on a national allocation: one sortie, Squadron Leader Rewi's crew, and she "
            "goes home to Darwin when it is done - she is not yours to keep and not yours to "
            "lose. The patrol vessel PILBARA is on the lane with the ordinary traffic, and a "
            "Meridian escort boat has been working the same water since Sunday with a drone "
            "spotting for it.\\n\\nGet Kiwi 01 close enough to put a name on the coaster, keep "
            "her out of the escort boat's reach, and bring her to the assigned recovery "
            "handover for Darwin. Everything else on the lane is somebody's living."
        )),
    forces="HMAS Pilbara. One RNZAF P-8A on a single national sortie. Lane "
           "traffic: two merchants and a trawler. Opposing: one coaster with "
           "her transponder off, one Meridian escort boat, one spotter drone.",
    objectives=[
        ("Picture", "Identify the coaster, then recover Kiwi 01 to Darwin",
         "30,-25,Fail,Main"),
        ("Kiwi", "Do not lose Kiwi 01", "20,-30,Complete"),
        ("Traffic", "Harm no lane traffic", "0,-25,Complete"),
    ],
    # Stage: the New Zealand aircraft classifies the coaster - which writes
    # O2KiwiPicture, read by The Quiet Passenger as a revealed contact. Win:
    # that same aircraft within ten miles of Darwin's field.
    victory=dict(kind="arrive", station="kiwi", at=(-12.409, 130.8665), radius=10,
                 after=dict(kind="classify", units="coaster", min_units=1,
                            sets="O2KiwiPicture",
                            intel=(
                                "CONTACT CORRELATION / KIWI 01: Coaster identified as MV "
                                "HARBOUR LIGHT. Rewi's crew has logged the collection fit and a"
                                " report of submarine activity in company. Pass the separate "
                                "surface and acoustic records to Darwin and Wellington, then "
                                "bring Kiwi 01 to the Darwin recovery handover."
                            )),
                 min_units=1, objective="Picture"),
    declares=["O2KiwiPicture"],
    fatal=[F("Kiwi", ["kiwi"])],
    neutral_objective="Traffic",
    win=(
        "Kiwi 01 has reached the recovery handover with the coaster classified. Rewi's crew can"
        " now file the report for Wellington and the coalition intelligence cell."
    ),
    lose="The Poseidon is down and the allocation with her. Wellington will "
         "want to know why its one aircraft was inside a gunboat's reach.",
    stations={
        "patrol": S(-10.6, 131.2, "HMAS Pilbara", heading=90),
        "kiwi": S(-10.95, 131.0, "Kiwi 01", heading=20, alt=12000),
        "coaster": S(-10.2, 131.5, "Coaster, transponder off", heading=110),
        "lane": S(-10.45, 131.35, "Lane traffic", heading=90),
        "raider": S(-10.05, 131.65, "Meridian escort boat", heading=200),
        "spotter": S(-10.4, 131.1, "Spotter drone", heading=90, alt=10000),
        "home": S(-12.409, 130.8665, "RAAF Base Darwin"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_opv_arafura", "patrol",
          variant="Variant3", name="HMAS Pilbara", weapons="Tight"),
        # No. 5 Squadron's own aircraft: Squadron23 in the winning squadrons
        # file is New Zealand. No JoinTaskForce - the guide says that is a
        # grant, and this is a loan.
        U("blue", "red-storm-arsenal", "usn_p_8a", "kiwi", squadron="Squadron23",
          name="Kiwi 01", alt=12000, weapons="Tight", loadout="ASW"),
        U("red", "_vanilla", "civ_ms_encounter", "coaster", name="MV Harbour Light",
          weapons="Hold", route=[(-10.35, 131.95, 0)], telegraph=2),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raider",
          name="Meridian Escort 3", route=[(-10.4, 131.4, 0)], telegraph=4),
        U("red", "small-medium-uav-series", "usn_ForpostR705", "spotter",
          name="Spotter drone", alt=10000),
        U("neutral", "_vanilla", "civ_ms_roro_b", "lane", name="MV Wessel Trader",
          route=[(-10.4, 131.9, 0)], telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_freighter_d", "lane",
          name="MV Croker Provider", route=[(-10.5, 131.95, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "lane",
          name="Arafura trawler", route=[(-10.55, 131.6, 0)], telegraph=2),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_darwin", "home",
          name="RAAF Base Darwin", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="optional", num="O3", key="Borrowed Shield",
    place="Timor Sea, western approach", expires_after="Blind Horizon",
    intro="Optional. The Korean destroyer Sejong the Great and the frigate "
          "Daegu are coming in for one fortnight under their own rules. Get "
          "both to the join point and Sejong the Great is in your screen at "
          "Blind Horizon.",
    special="Optional operation. A Korean detachment for one fortnight: bring "
            "both warships to the join point and SEJONG THE GREAT screens "
            "Blind Horizon; lose either, or leave them short, and she does "
            "not. Your detachment sails to meet them.",
    sender="Commodore Alex Mercer; Captain Han Ji-woo, ROKS Sejong the Great, "
           "for the detachment",
    intent=("Seoul has sent the best air-defence ship in this ocean and a "
            "frigate to keep her company, for fourteen days, under rules I "
            "did not write: they screen what we are already screening and "
            "they do not fire first. Meet "
            "them at the join point with whatever you can spare, and do not "
            "let a Kilo or a strike pair end the fortnight on its first "
            "day."),
    date=(2028, 11, 4), time=(9, 20), sea=3, clouds="Broken_2", wind="W",
    difficulty=3, minutes=70, centre=(-11.3, 126.2),
    blue_nation="Australia", red_nation="China",
    brief=(
        "TIMOR SEA, western approach. SEJONG THE GREAT and DAEGU are coming "
        "in from the Lombok side with the stores ship BUSAN PIONEER, on the "
        "Korean government's own arrangement: one fortnight, one destroyer, "
        "one frigate, and Captain Han fires when fired upon or when you "
        "are.\\n\\n"
        "A Kilo has been reported on the approach they are using, and the "
        "enclave has a strike pair on alert that came south twice this week "
        "to look at the same water. Your detachment meets them at the join "
        "point; until then the shield has to bring itself in.\\n\\n"
        "Both warships reach the join point or there is no fortnight. The "
        "stores ship is worth fifteen minutes of anybody's time, but she is "
        "not the reason Seoul sent a destroyer."),
    forces="Your detachment. Joining: ROKS Sejong the Great with her Lynx, "
           "ROKS Daegu, and the stores ship Busan Pioneer. Two neutral "
           "merchants on the approach. Opposing: one Kilo on the approach, "
           "one JH-7A pair on alert.",
    objectives=[
        ("Shield", "Bring SEJONG THE GREAT and DAEGU to the join point",
         "35,-35,Fail,Main"),
        ("Stores", "Do not lose Busan Pioneer", "15,-15,Complete"),
        ("Traffic", "Harm no neutral shipping", "0,-25,Complete"),
    ],
    # Both warships arrive, alive: the win writes O3ShieldJoined and Blind
    # Horizon spawns Sejong the Great in the screen on it. A destroyed
    # escort cannot be awarded later - losing either ends this mission.
    victory=dict(kind="arrive", station="rok", units=["rok#1", "rok#2"],
                 min_units=2, objective="Shield", transit=16,
                 sets="O3ShieldJoined"),
    declares=["O3ShieldJoined"],
    fatal=[F("Shield", ["rok#1"]), F("Shield", ["rok#2"])],
    neutral_objective="Traffic",
    win="The shield is in. Sejong the Great and Daegu are in company with "
        "your detachment, Busan Pioneer or not, and Captain Han has a signal "
        "to send that says the fortnight has started.",
    lose="The Korean detachment is broken before it joined. Seoul's "
         "fortnight ends "
         "before it began, and the corridor is back to one navy's magazines.",
    stations={
        "rok": S(-11.2, 125.8, "Korean detachment", heading=90),
        "lynx": S(-11.15, 125.92, "Sejong Flight", heading=90, alt=2000),
        # The player's detachment forms here, 45 NM east, and sails west to
        # meet them.
        "escort": S(-11.6, 126.6, "Detachment", heading=270),
        "lane": S(-11.35, 126.2, "Approach traffic", heading=90),
        "red_sub": S(-11.5, 126.35, "Kilo datum", heading=300),
        "red_air": S(-9.6, 126.8, "Strike pair", heading=200, alt=30000),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant3",
          weapons="Tight"),
        U("blue", "euromod-south-korea", "ko_ddg-991", "rok", variant="Variant1",
          name="ROKS Sejong the Great"),
        U("blue", "euromod-south-korea", "ko_ffg-818", "rok", variant="Variant1",
          name="ROKS Daegu"),
        U("blue", "SEST_Replenishment", "civ_ms_sealift_pacific", "rok",
          name="MV Busan Pioneer"),
        U("blue", "euromod-south-korea", "rok_mk99_a", "lynx", name="Sejong Flight",
          alt=2000),
        U("neutral", "_vanilla", "civ_ms_ritina", "lane", name="MT Lombok Spirit",
          route=[(-11.3, 127.0, 0)], telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_andizhan", "lane",
          name="MV Sumba Trader", route=[(-11.4, 127.0, 0)], telegraph=3),
        U("red", "chinese-navy-plan", "plan_ss_kilo", "red_sub", name="Contact KILO",
          depth="belowlayer", route=[(-11.25, 125.95, "belowlayer")], telegraph=2),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike 21",
          loadout="AntiShip", route=[(-11.2, 125.8, 20000)], telegraph=3),
        U("red", "jh-7a", "plaaf_jh7a", "red_air", name="Strike 22",
          loadout="AntiShip", route=[(-11.2, 125.8, 20000)], telegraph=3),
    ],
))

MISSIONS.append(dict(
    group="optional", num="O4", key="Weather Alternate",
    place="Kai Islands", expires_after="The Open Door",
    intro="Optional. A strip is only an alternate if there is fuel on it. "
          "Take the bladders the last forty miles to Langgur.",
    special="Optional operation. Put the fuel on Langgur and The Open Door "
            "gets a tanker on station south of the enclave; miss it and the "
            "F-35 pair flies on what it took off with. The strip is Prasetyo's "
            "either way.",
    sender="Commodore Alex Mercer; Captain Ratna Prasetyo, Indonesian Navy "
           "(TNI-AL), for the strip",
    intent=("Langgur is where The Open Door's F-35 pair will recover, and a "
            "strip is only an alternate if there is fuel on it. Get both "
            "coasters in. "
            "Langgur town is at the head of the anchorage: nothing in it is "
            "yours to break."),
    date=(2028, 11, 10), time=(14, 0), sea=2, clouds="Scattered_1", wind="E",
    difficulty=3, minutes=70, centre=(-5.8, 132.7),
    blue_nation="Australia", red_nation="China",
    brief=(
        "KAI ISLANDS, afternoon. Captain Prasetyo has lent us the strip at "
        "Langgur for the enclave relief window and not an hour longer. "
        "LANGGUR PROVIDER and KEI STAR carry the fuel bladders and the "
        "ground party; you take them the last "
        "forty miles into the anchorage.\\n\\n"
        "The enclave knows what Langgur is for. A Meridian escort pair has "
        "been working the Kai passages since Tuesday, and the last transit "
        "reported a drone launcher site on Kai Besar, across the strait "
        "east of "
        "the anchorage. "
        "Langgur town is at the head of it and every building in it is "
        "somebody's.\\n\\n"
        "Get both coasters in. Put the launcher out of the argument if you "
        "can do it without touching the town."),
    forces="Your detachment, two fuel coasters. Langgur town at the head of "
           "the anchorage, the strip beyond it. Opposing: a Meridian escort "
           "pair, a drone launcher site on Kai Besar.",
    objectives=[
        ("Fuel", "Get both coasters into the Langgur anchorage", "35,-35,Fail,Main"),
        ("Site", "Neutralise the Kai Besar launcher site", "15,-10,Complete"),
        ("Town", "Leave Langgur alone", "0,-30,Complete"),
    ],
    victory=dict(kind="arrive", station="fuel", min_units=2, objective="Fuel",
                 transit=12, sets="O4LanggurStocked"),
    declares=["O4LanggurStocked"],
    fatal=[F("Fuel", ["fuel"], 1)],
    neutral_objective="Town",
    win="Both coasters are in the anchorage and the ground party is pumping "
        "before the light goes. The Open Door has a tanker on the track.",
    lose="The bladders are on the bottom forty miles short. The Open Door "
         "flies on internal fuel and Prasetyo's strip is a runway with "
         "nothing on it.",
    stations={
        "escort": S(-6.15, 132.7, "Detachment", heading=30),
        "fuel": S(-6.1, 132.6, "Fuel coasters", heading=30),
        "raiders": S(-5.7, 133.1, "Meridian pair", heading=210),
        "site": S(-5.3643, 133.516, "Kai Besar launcher site", heading=240),
        # The one proven ground at Langgur: the town takes it, and the strip
        # the fuel is for is the same place in the story - it needs no unit
        # here, nothing in this mission flies from it.
        "town": S(-5.2953, 132.9232, "Langgur", heading=0),
        "fishing": S(-5.9, 132.5, "Kai fishing", heading=60),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant3",
          weapons="Tight"),
        U("blue", "re-power-resupply", "civ_ms_freighter_d", "fuel",
          name="MV Langgur Provider"),
        U("blue", "_vanilla", "civ_ms_encounter", "fuel", name="MV Kei Star"),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raiders",
          name="Meridian Escort 5", route=[(-6.05, 132.65, 0)], telegraph=4),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raiders",
          name="Meridian Escort 6", route=[(-6.1, 132.7, 0)], telegraph=4),
        U("red", "shahed-136-zero-two", "shahed_tel_black", "site",
          name="Kai Besar launcher site"),
        U("neutral", "buildings-targets-missions", "4tentgroup", "town",
          name="Langgur town"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "fishing",
          name="Kai fishing boat", route=[(-5.75, 132.62, 0)], telegraph=2),
    ],
))

MISSIONS.append(dict(
    group="contingency", num="C2", key="Broken Wake",
    place="Banda Sea, southern approaches", expires_after="The First Ship Through",
    intro="Contingency. The frigate HMAS Stuart has one shaft, thirty-one "
          "wounded and a ceasefire two days off. Bring her to the line where "
          "Darwin's tug meets her.",
    special=(
        "Detached recovery task. Stuart is proceeding at the Chief Engineer's requested six "
        "knots after a reported shaft casualty. Escort her to the handover without pressing the"
        " damaged machinery."
    ),
    sender="Commodore Alex Mercer",
    intent=("One shaft, six knots, thirty-one wounded. Bring STUART to the "
            "line before somebody with a "
            "torpedo finds her, and do not drive her faster than the Chief "
            "says she will go."),
    date=(2028, 11, 25), time=(5, 40), sea=3, clouds="Broken_2", wind="NW",
    difficulty=3, minutes=75, centre=(-6.0, 130.2),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "BANDA SEA, before dawn. HMAS STUART, an Anzac-class frigate, took a hit forward on"
            " the twenty-third screening Ford's oiler group north of here, outside your part of"
            " the fleet action. She has one shaft, six knots, and thirty-one wounded who need a"
            " hospital that is a day and a half away at the speed she can make.\\n\\nFord's group"
            " went north-west without her. A Kilo has been working the southern approaches "
            "since the fleet action, and the enclave still has a strike pair that comes south "
            "to look. The ceasefire is two days off and nobody has told either of "
            "them.\\n\\nBring her south-south-east to the line where the tug from Darwin meets "
            "her. The Chief Engineer requests six knots to protect the damaged shaft. Match the"
            " escort plan to that speed and keep the route ahead clear."
        )),
    forces="Your detachment. HMAS Stuart, one shaft. Two neutral merchants on "
           "the same approach. Opposing: one Kilo, one J-15D pair.",
    objectives=[
        ("Stuart", "Bring STUART to the line", "30,-30,Fail,Main"),
        ("Traffic", "Harm no neutral shipping", "0,-25,Complete"),
    ],
    victory=dict(kind="arrive", station="straggler", min_units=1,
                 objective="Stuart", transit=6),
    fatal=[F("Stuart", ["straggler"])],
    neutral_objective="Traffic",
    win="Stuart is at the line with her people aboard and a tug coming up "
        "from Darwin. Thirty-one wounded get their hospital, and the ship "
        "gets a dockyard instead of a reef.",
    lose="Stuart is gone with her wounded aboard, two days short of a "
         "ceasefire. The recovery that should have been routine is a court "
         "of inquiry.",
    stations={
        "straggler": S(-5.9, 130.1, "HMAS Stuart", heading=160),
        "escort": S(-5.95, 130.2, "Detachment", heading=160),
        "lane": S(-5.7, 130.0, "Approach traffic", heading=160),
        "red_sub": S(-6.2, 130.0, "Kilo datum", heading=330),
        "red_air": S(-4.6, 129.9, "Strike pair", heading=160, alt=30000),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort", variant="Variant3",
          weapons="Tight"),
        # Variant4 is Stuart - a hull the roster does not sell and no other
        # mission places, so she exists whatever happened at Fujian's
        # Shadow. Telegraph 1 on her route is the six knots; the rest is the
        # Chief's word.
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "straggler", variant="Variant4",
          name="HMAS Stuart", weapons="Tight",
          route=[(-6.4, 130.3, 0)], telegraph=1),
        U("neutral", "_vanilla", "civ_ms_ritina", "lane", name="MT Banda Spirit",
          route=[(-6.6, 130.2, 0)], telegraph=3),
        U("neutral", "merchants-expanded", "civ_ms_mairangi_bay", "lane",
          name="MV Tanimbar Trader", route=[(-6.65, 130.25, 0)], telegraph=3),
        U("red", "chinese-navy-plan", "plan_ss_kilo", "red_sub", name="Contact TANGO",
          depth="belowlayer", route=[(-5.95, 130.15, "belowlayer")], telegraph=2),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 31", loadout="AntiShip",
          route=[(-5.9, 130.1, 20000)], telegraph=3),
        U("red", "type-003-004-maneuverwarfare", "plan_j-15d", "red_air",
          name="Flying Shark 32", loadout="AntiShip",
          route=[(-5.9, 130.1, 20000)], telegraph=3),
    ],
))


MISSIONS.append(dict(
    group="dispatch", num="D1", key="Western Passage",
    place="Timor Sea, western approach",
    intro="Allied Dispatch. A European escort rotation brings the replenishment "
          "group in from the west.",
    sender="Captain (N) Elin Vasse, European escort rotation",
    intent=("The two tankers are the group. Everything east of here plans "
            "around what is in their tanks. The Russian shadowers to the north "
            "are hunting for the tankers; do not let them get close enough to "
            "find them."),
    date=(2028, 11, 6), time=(8, 30), sea=4, clouds="Broken_2", wind="SW",
    difficulty=3, minutes=85, centre=(-12.5, 125.5),
    blue_nation="Europe", red_nation="Russia",
    brief=(
        (
            "WESTERN APPROACH. The coalition's escort corridor runs on fuel that arrives from "
            "outside it, and the replenishment group coming up from the Indian Ocean is the "
            "reason anything in the Banda still has range.\\n\\nThe escort is a European "
            "rotation: a Type 45 with its Merlin, a German F124, a Dutch Karel Doorman, a "
            "Danish Iver Huitfeldt, an Italian FREMM and an older Type 23 that was already in "
            "the region when the crisis began. Two RAF Typhoons out of Curtin hold the air, "
            "with a Swedish AEW aircraft lent for the transit.\\n\\nThe Russian expeditionary "
            "detachment supporting the Biak enclave has put a MiG-35 pair and a Su-24MP up "
            "along the northern edge. They are here to find the tankers, and one of the MiGs "
            "carries an anti-ship missile. Take them down before they do.\\n\\nAIR PICTURE / "
            "ARGUS 70: The Swedish GlobalEye reports a MiG-35 pair and a Su-24MP along the "
            "northern edge of the corridor. The force assesses one MiG as an anti-ship threat. "
            "Use the AEW picture to cue the Typhoons and ship sensors; keep both tankers "
            "covered while confirming the approaching tracks."
        )),
    forces="Two tankers. Type 45, F124, Karel Doorman, Iver Huitfeldt, "
           "FREMM, Type 23, "
           "Merlin, Wildcat, a Sea Lynx and an NH90 across the group. "
           "Two Typhoons and a Saab AEW&C overhead. Opposing: MiG-35 pair and "
           "a Su-24MP.",
    objectives=[
        ("Oiler", "The replenishment group reaches the eastern box",
         "35,-35,Fail,Main"),
        ("Escorts", "Keep the escort rotation intact", "20,-25,Complete"),
        ("Shadow", "Splash the shadowers before they find the tankers", "15,-10,Complete"),
    ],
    victory=dict(kind="arrive", station="group", at=(-11.6, 129.4), radius=35,
                 transit=14,
                 min_units=2, objective="Oiler"),
    fatal=[F("Oiler", ["group"])],
    neutral_objective="Oiler",
    win="Both tankers are in the eastern box. The corridor has fuel for "
        "another fortnight, whatever the rotation paid to bring it.",
    lose="A tanker is gone. Everything east of here now plans around a tank "
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
        # Each flight on a deck whose AircraftSupported names it: Merlin on
        # the Type 45, Wildcat on the Type 23, the Mk88 on Sachsen, the NH90
        # on Van Speijk. The FREMM lists none of them and homed all four.
        U("blue", "euromod-german", "ger_sea_lynx_mk88", "helo",
          name="Sachsen Flight"),
        U("blue", "french-helicopter-package", "nl_nh90", "helo",
          name="Van Speijk Flight"),
        U("blue", "eurofighter-typhoon", "raf_ef2000_fgr4_late", "cap",
          name="Typhoon 11"),
        U("blue", "eurofighter-typhoon", "raf_ef2000_fgr4_late", "cap",
          name="Typhoon 12"),
        # Squadron2, the Swedish GlobalEye: the default Squadron1 is the UAE's,
        # and the game has no UAE nation key, so it flew with no flag.
        U("blue", "saab-aewc-pack", "dts_saab_ge", "aew", name="Argus 70",
          squadron="Squadron2", weapons="Hold"),
        U("blue", "SEST_Replenishment", "civ_ms_sealift_pacific", "group",
          name="MT Western Provider"),
        U("blue", "_vanilla", "civ_ms_ritina", "group",
          name="MT Passage Trader"),
        # Routed onto the group: the shadowers used to sit 90 NM off with
        # no waypoints. One of the pair carries Kh-31A, so finding the oiler
        # has a consequence the Typhoons can prevent.
        U("red", "mig-35", "wp_mig-35", "red_air", name="Fulcrum-F 21",
          route=[(-11.6, 125.0, 28000), (-12.0, 124.6, 28000)], telegraph=3),
        U("red", "mig-35", "wp_mig-35", "red_air", name="Fulcrum-F 22",
          loadout="AntiShip",
          route=[(-11.6, 125.0, 28000), (-12.0, 124.6, 28000)], telegraph=3),
        U("red", "more-su-24m-variants", "wp_su-24mp", "red_air",
          name="Fencer recon", weapons="Hold",
          route=[(-11.5, 125.1, 28000), (-12.0, 124.7, 28000)], telegraph=3),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_curtin", "home",
          name="RAAF Base Curtin", nation="australia", weapons="Hold"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D2", key="Flight Deck Day", place="Coral Sea",
    intro="Allied Dispatch. Three US carriers keep their decks cycling in "
          "the Coral Sea while the coalition maritime commander flies out to "
          "visit.",
    sender="Rear Admiral C. Halvorsen, Carrier Strike Group, Coral Sea",
    intent=("Keep the deck cycling and get the visitor aboard. Nobody shoots "
            "at anybody today if the day goes well - and the day goes well if "
            "the drifting merchant the Reaper is watching stays a drifting "
            "merchant."),
    date=(2028, 11, 13), time=(15, 0), sea=3, clouds="Scattered_1", wind="SE",
    difficulty=1, minutes=55, centre=(-15.5, 149.5),
    blue_nation="USA", red_nation="Russia",
    brief=(
        (
            "CORAL SEA. Three carriers are working the same box: one recovering a long-range "
            "package, one running deck drills with a new air department and one cycling alert "
            "aircraft. A Seawolf is riding shotgun below and an E-3G is holding the wider "
            "picture while the RAAF Wedgetail is tasked elsewhere.\\n\\nThe tanker is the "
            "schedule. Everything airborne today is planned around one KC-10, and the Reaper "
            "north of the box is watching a merchant that has been drifting off its filed route"
            " for two days.\\n\\nThere is a distinguished-visitor lift inbound - a VH-3D bringing"
            " the coalition maritime commander across for the afternoon. That airframe gets "
            "deck priority over everything else that is not on fire.\\n\\nSURVEILLANCE / REAPER "
            "12: MV SOLOMON TRADER is the merchant reported off its filed route north of the "
            "carrier box. The shore cell is comparing its last AIS report with imagery; the "
            "Reaper provides the local observation. Record changes in course or behaviour "
            "before drawing conclusions about intent."
        )),
    forces="USS Nimitz, Carl Vinson and Theodore Roosevelt, one Seawolf, "
           "an E-3G, a KC-10A, an MQ-9A north of the box and a VH-3D on "
           "the visit.",
    objectives=[
        ("Visit", "Get the VH-3D into the carrier box", "25,-20,Fail,Main"),
        ("Cycle", "Keep the carriers operating", "20,-25,Complete"),
        ("Tanker", "Do not lose the tanker", "10,-10,Complete"),
        ("Neutrals", "Harm no neutral shipping", "0,-25,Complete"),
    ],
    # The carrier box is the carriers: five miles around the deck the
    # visitor lands on, not a solved circle 104 NM from it.
    victory=dict(kind="arrive", station="visit", at=(-16.4, 150.0), radius=5,
                 min_units=1, objective="Visit"),
    fatal=[F("Cycle", ["carriers"])],
    neutral_objective="Neutrals",
    win="The visitor is aboard and the deck cycle never broke. A quiet day, "
        "which is the point of the exercise.",
    lose="The cycle broke. Somebody will write a report about the afternoon "
         "the carriers stopped flying.",
    stations={
        "carriers": S(-16.4, 150.0, "Carrier box", heading=140),
        "screen": S(-16.5, 149.8, "Screen", heading=140),
        "visit": S(-15.2, 149.4, "VIP lift", heading=180, alt=2000),
        "air": S(-15.0, 149.4, "Support aircraft", heading=90, alt=28000),
        "sub": S(-16.6, 150.2, "Seawolf station", heading=140),
        "track": S(-13.5, 148.6, "Southern track", heading=200, alt=22000),
        # The Sentry and the Extender are land-based; a carrier with no
        # AircraftSupported list took them only because nothing else could.
        "home": S(-12.6188, 142.094, "RAAF Base Scherger"),
    },
    units=[
        U("blue", "flight-deck-ops", "usn_cvn_nimitz", "carriers",
          name="USS Nimitz"),
        U("blue", "ado-nimitz-2000s", "usn_cvn_nimitz_2000s_adou", "carriers",
          name="USS Carl Vinson"),
        U("blue", "murder-hornet", "usn_cvn_nimitz_2000s", "carriers",
          name="USS Theodore Roosevelt"),
        U("blue", "us-submarines", "usn_ssn_seawolf", "sub", name="USS Seawolf"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_scherger", "home",
          name="RAAF Base Scherger", nation="australia", weapons="Hold"),
        U("blue", "e-3g", "usaf_e-3g", "air", name="Sentry 40", weapons="Hold"),
        U("blue", "kc-10a", "usaf_kc-10a_extender", "air", name="Texaco 60",
          weapons="Hold"),
        U("blue", "mq-9-reaper", "usaf_mq-9a", "track", name="Reaper 12",
          weapons="Tight"),
        U("blue", "vh-3d-marine-one", "usmc_vh-3d", "visit", name="Nighthawk 1",
          weapons="Hold"),
        U("neutral", "_vanilla", "civ_ms_roro_c", "track",
          name="MV Torres Venture", snap="sea"),
        U("neutral", "merchants-expanded", "civ_ms_mairangi_bay", "track",
          name="MV Solomon Trader", snap="sea"),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D3", key="The Relief Ship", place="Halmahera Sea",
    intro="Allied Dispatch. French and Spanish ships land relief on "
          "Halmahera, into a port the fighting went round rather than through.",
    sender="Capitaine de vaisseau A. Mercier, Groupe amphibie",
    intent=("Land the relief and open the distribution point. The people on "
            "the roads to it are why we are here, and they are not a target "
            "from any angle."),
    date=(2028, 11, 17), time=(7, 45), sea=2, clouds="Broken_2", wind="NE",
    difficulty=2, minutes=60, centre=(0.0, 127.2),
    blue_nation="France", red_nation="China",
    brief=(
        "HALMAHERA. The port never changed hands but the roads to it did, and "
        "twelve thousand people have been on emergency rations since the "
        "second week of the crisis. Indonesia's coastal authority has asked France "
        "and Spain to land relief, and the arrangement is narrow: this beach, "
        "this window, these vehicles.\\n\\n"
        "CHARLES DE GAULLE is offshore with a Horizon destroyer and Rafales "
        "overhead. The lift is a Panther, a Cougar and the group's Lynx, with "
        "a Spanish Harrier from JUAN CARLOS I covering the approach road; a "
        "two-vehicle armoured column is on the road to hold the distribution "
        "point rather than to take anything.\\n\\n"
        "An armed detachment holds a roadblock between the column and the "
        "point. Nothing here is a target unless it shoots first. The people you are "
        "feeding will be living with whoever runs this town next month."),
    forces="Charles de Gaulle, a Horizon destroyer, Juan Carlos I; Rafale "
           "M, AV-8B, Panther, Cougar, Lynx, AB-212; a VAB and a Griffon "
           "ashore. Opposing: a roadblock.",
    objectives=[
        ("Relief", "Get both vehicles of the relief column to the distribution "
                   "point",
         "35,-35,Fail,Main"),
        ("Town", "Leave the port and its people alone", "0,-35,Complete"),
        ("Lift", "Put the lift over the distribution point", "10,-10,Complete"),
        ("Group", "Keep the amphibious group intact", "15,-20,Complete"),
    ],
    # The column itself, both vehicles, at the point: land units carry
    # Waypoints in eight native sections (Caron at Grenada, CombatRecon),
    # so the column drives the road. The lift is scored separately.
    victory=dict(kind="arrive", station="column", at=(-0.5, 128.0), radius=5,
                 min_units=2, objective="Relief"),
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
        # The column starts twenty miles up the road; the roadblock sits
        # between it and the point, not beside the tents.
        "column": S(-0.3, 127.7, "Relief column", heading=120),
        "road": S(-0.42, 127.88, "Roadblock", heading=300),
        "beach": S(0.15, 127.35, "Lift-track traffic", heading=90),
        "harrier": S(0.2, 127.4, "Spanish detachment", heading=120, alt=15000),
    },
    units=[
        U("blue", "cdg-modern-french-navy", "fr_cvn_charles-de-gaulle", "group",
          name="FS Charles de Gaulle"),
        U("blue", "cdg-modern-french-navy", "fr_ddg_horizon", "group",
          name="FS Forbin"),
        # The Spanish detachment's own deck: the Harrier and the AB212 are
        # hers, and the Horizon lists only its NH90.
        U("blue", "euromod-spanish-modern", "ae_lhd_juan_carlos", "group",
          name="SPS Juan Carlos I"),
        U("blue", "sea-lynx", "fr_sea_lynx", "lift", name="Group Flight",
          alt=2000),
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
        U("blue", "french-army-vehicles", "fr_apc_vab_top", "column",
          name="Relief column lead", weapons="Tight",
          route=[(-0.5, 128.0, 0)], telegraph=3),
        U("blue", "french-army-vehicles", "fr_apc_griffon", "column",
          name="Relief column two", weapons="Tight",
          route=[(-0.5, 128.0, 0)], telegraph=3),
        U("neutral", "buildings-targets-missions", "4tentgroup", "shore",
          name="Distribution point"),
        U("blue", "_vanilla", "civ_ms_encounter", "group",
          name="MV Halmahera coaster", loadout="Containers"),
        U("red", "pla-land-unit-pack", "pla_apc_zbl-08", "road",
          name="Roadblock detachment", route=[(-0.3, 127.7, 0)], telegraph=2),
        # Something to tell the roadblock from: an unarmed pickup on the same
        # road and a fishing boat off the beach the lift comes in over.
        U("neutral", "pickup-truck-extension", "civ_car_pickup_1983", "road",
          name="Village pickup"),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_b", "beach",
          name="Halmahera fishing boat", route=[(-0.1, 127.7, 0)], telegraph=2),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D4", key="Return Passage", place="Banda Sea",
    intro="Red Line. As the Russian detachment, bring a damaged auxiliary "
          "home through the coalition's corridor.",
    sender="Russian detachment commander, to his own force",
    intent=("Get the auxiliary home. The Australian patrol is professional "
            "and it does not chase; it will not start a fight today unless you "
            "give it a reason."),
    date=(2028, 11, 21), time=(3, 10), sea=4, clouds="Overcast", wind="NW",
    difficulty=4, minutes=75, centre=(-5.0, 130.0),
    blue_nation="Russia", red_nation="Australia",
    brief=(
        (
            "BANDA SEA, middle watch. The auxiliary took a torpedo forward eleven days ago and "
            "has been making six knots ever since. She carries the Russian detachment's "
            "remaining missile stocks and the only workshop between here and home.\\n\\nYou have "
            "the heavy cruiser, a Project 11356 frigate, a Felon and a Flanker off the "
            "enclave's dispersal field on Biak, and a Chinese J-16D lent for the passage. Your "
            "bombers can reach but they cannot loiter, and every sortie you fly tells the other"
            " side where you are going.\\n\\nGet her south-east past the corridor. This is not a "
            "raid. If you start a fleet action to protect a workshop ship you will lose "
            "both.\\n\\nDETACHMENT INTELLIGENCE: Earlier surface-search reporting places an "
            "Australian Hobart-class destroyer and Anzac-class frigate about a hundred and "
            "twenty miles west-south-west of the auxiliary, closing north-east, with a P-8A and"
            " an assessed F-35A patrol. The escorts' and fighters' sensors must update that "
            "report as contact permits. Avoid widening the fight while the auxiliary clears "
            "south-east."
        )),
    forces="Pyotr Velikiy, a Project 11356 frigate and Kuznetsov's covering "
           "group; a Felon, a Su-30SM2, a MiG-29K, a Su-33 and a lent J-16D; a "
           "Tu-160 and two Tu-95MS already airborne. One damaged auxiliary, and "
           "three neutral merchants on the same track. Opposing: an Australian "
           "patrol - a Hobart and an Anzac with an F-35A and a P-8A over them.",
    objectives=[
        ("Auxiliary", "Bring the auxiliary through to the south-east",
         "40,-40,Fail,Main"),
        ("Cruiser", "Do not lose the heavy cruiser", "20,-30,Complete"),
        ("Traffic", "Harm no neutral shipping", "0,-25,Complete"),
        ("Restraint", "Avoid a fleet action you cannot finish: harm nothing "
                      "of the coalition's",
         "10,-15,Complete"),
    ],
    victory=dict(kind="arrive", station="auxiliary", at=(-7.0, 132.5),
                 transit=6,
                 radius=35, min_units=1, objective="Auxiliary"),
    fatal=[F("Auxiliary", ["auxiliary"])],
    neutral_objective="Traffic",
    win=(
        "The auxiliary has crossed the withdrawal line with her cargo. Maintain the recovery "
        "plan for the damaged machinery and report any contacts still following the detachment."
    ),
    lose="The auxiliary is on the bottom with the detachment's magazines in "
         "her. The Biak enclave now fights with what it is holding.",
    stations={
        "auxiliary": S(-4.6, 130.1, "Damaged auxiliary", heading=130),
        "escort": S(-4.5, 130.3, "Escort", heading=130),
        "cap": S(-4.3, 130.5, "Felon pair", heading=140, alt=36000),
        "bomber": S(-2.6, 129.0, "Bomber track", heading=160, alt=34000),
        "red_sag": S(-5.2, 128.2, "Coalition patrol", heading=60),
        "red_air": S(-5.4, 128.4, "Coalition CAP", heading=60, alt=30000),
        # The passage is "among neutral shipping": three merchants on the
        # same track through the box.
        "lane": S(-4.85, 130.45, "Corridor traffic", heading=130),
        # The bombers and the land-based fighters recover on the enclave's
        # dispersal field, 390 NM north-east, not on Kuznetsov.
        "field": S(-1.1, 136.2, "Enclave dispersal field", heading=90),
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
        U("blue", "modern-russian-airbase", "wp_airbase_modern", "field",
          name="Enclave dispersal field", weapons="Hold"),
        U("blue", "kuznetsov-1143-5", "wp_su-33", "cap", name="Flanker-D 14"),
        U("red", "SEST_RAN_Fleet", "ran_ddg_hobart", "red_sag",
          name="HMAS Hobart"),
        U("red", "SEST_RAN_Fleet", "ran_ffh_anzac", "red_sag", variant="Variant8",
          name="HMAS Perth"),
        # Red can reply: JSM under the F-35A, Harpoon under the P-8. The
        # reviewed build's only way to lose was the clock.
        U("red", "SEST_RAAF_F-35A_JATM", "raaf_f-35a", "red_air",
          squadron="Squadron3", name="Vigilant 41",
          loadout="StrikeLongRangeStealth"),
        U("red", "p-8-poseidon", "usn_p8", "red_air", squadron="Squadron3",
          name="Bluefin 29", loadout="AntiShip"),
        U("neutral", "_vanilla", "civ_ms_ritina", "lane", name="MT Seram Spirit",
          route=[(-7.0, 132.5, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_ms_roro_b", "lane", name="MV Ambon Ferry",
          route=[(-7.0, 132.45, 0)], telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_andizhan", "lane",
          name="MV Tual Trader", route=[(-6.95, 132.55, 0)], telegraph=3),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D5", key="Range Week", place="Northern Territory ranges",
    intro="Range Week. A live counter-launcher serial against the range's own "
          "threat pads, plus an anti-ship shot at the seaward target.",
    sender="Trials Director, Northern Territory Ranges",
    intent=("Three of four pads down, the anti-ship serial into the seaward "
            "target, and nothing outside the danger area. The THAAD and "
            "David's Sling launchers and radars are the serial: lose one and "
            "it ends."),
    date=(2028, 11, 9), time=(9, 0), sea=1, clouds="Clear", wind="SE",
    difficulty=2, minutes=60, centre=(-13.5, 131.5),
    blue_nation="Australia", red_nation="Iran",
    brief=(
        "NORTHERN TERRITORY RANGES. This is a trial, not a battle. The "
        "coalition has brought its layered-defence systems to the Darwin range for a "
        "fortnight of live shots, and the threat side of the range is run by "
        "the trials unit with captured and purchased launchers.\\n\\n"
        "Today's serial is the hard one. The range's own southern pads launch "
        "a mixed ballistic and cruise raid; a THAAD battery and a David's "
        "Sling pair defend against it while a Warthog flies the "
        "counter-launcher shot at the pads. The Sejjil pad is a target, not a "
        "shooter: everything on this range is inside its minimum range. A "
        "Japanese Type 12 battery is firing a separate anti-ship serial at "
        "the seaward target."),
    forces="THAAD with AN/TPY-2, a David's Sling battery, a Type 12 SSM "
           "battery, the range field, an A-10A with the counter-launcher shot "
           "and an F-16A chase. "
           "Range threat pads: Scud-B, Sejjil, Iskander and a Shahed line.",
    objectives=[
        # The trigger destroys launchers, so the objective says destroy
        # launchers. It used to promise intercepted rounds and score destroyed
        # pads, which is two different exercises.
        ("Pads", "Destroy three of the four range threat pads",
         "35,-25,Fail,Main"),
        ("Serial", "Put the anti-ship serial into the seaward target",
         "15,-10,Fail"),
        ("Safety", "Hit nothing outside the danger area", "0,-30,Complete"),
        # The loss rule below ends the exercise the moment ONE of the four
        # defence units is destroyed. That was true before this objective
        # existed too - it just went unannounced, and the defeat was reported
        # as a failure to destroy the enemy's pads, which is a different
        # exercise entirely. An unstated loss condition is not difficulty.
        ("Battery", "Keep all four launchers and radars in action",
         "0,-30,Complete"),
    ],
    victory=dict(kind="destroy", stations=["pads"], min_units=3,
                 objective="Pads"),
    fatal=[F("Battery", ["battery"])],
    # The player's force is the batteries; losing the two aircraft is not
    # losing the trial.
    force_loss=False,
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
        "tow": S(-13.0, 131.4, "Counter-launcher serial", heading=180, alt=18000),
        "target": S(-12.0, 130.5, "Seaward target", heading=270),
        "safety": S(-11.5, 129.6, "Range safety area", heading=90, alt=31000),
        "airway": S(-11.7, 129.9, "Darwin-Singapore airway", heading=300, alt=31000),
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
        U("blue", "a-10a", "usa_a-10a", "tow", name="Counter-launcher 01",
          loadout="AntiArmor"),
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
        # Flying the airway, not orbiting over it: 650 NM toward Singapore
        # on the station's own heading, beyond an hour at cruise.
        U("neutral", "civil-aircraft-airbus", "civ_a330", "airway",
          name="Darwin-Singapore service", route=[(-6.28, 120.3, 31000)],
          telegraph=3),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D6", key="Long Reach", place="Banda Sea, 2034",
    intro=(
        "Banda Sea, March 2034. Escort a long-range bomber package against a mobile launcher "
        "complex while reconnaissance aircraft locate the threat."
    ),
    sender="Air Component, 2034",
    intent=((
        "The bomber package must neutralise the assigned launcher complex. Use the "
        "reconnaissance picture to support the strike, protect the escorts and keep a recovery "
        "route open. New equipment does not remove the need to identify targets or conserve "
        "fuel."
    )),
    date=(2034, 3, 14), time=(1, 20), sea=3, clouds="Broken_2", wind="NE",
    difficulty=5, minutes=80, centre=(-4.0, 130.5),
    blue_nation="USA", red_nation="China",
    brief=(
        (
            "BANDA SEA, MARCH 2034. A mobile launcher complex threatens the north-eastern "
            "passage. An RQ-180 is ahead of the bomber package; the escort includes YF-23s and "
            "aircraft carrying long-range missile fits.\\n\\nOpposing J-36 and J-50 fighters "
            "cover the complex, with a Tu-95MA contributing a further missile threat. Earlier "
            "imagery narrows the launcher search area, but mobile equipment must be located and"
            " identified before attack.\\n\\nStrike the launcher complex and preserve a recovery "
            "route for the package. Darwin is beyond the escorts' reach on this task: they "
            "recover to Langgur in the Kai Islands or to USS Enterprise, south-east of the "
            "track."
        )),
    forces="Two YF-23, one F-15EX, an F-16CM with JATM, a Rafale F5, the "
           "RQ-180, a B-52O, a B-1B and a B-52H in the stream. Opposing: J-36, "
           "J-50, a Tu-95MA with Meteorit, a Type 004 picket and a relocatable "
           "launcher complex.",
    objectives=[
        ("Stream", "Put the stream's release on the launcher complex",
         "40,-35,Fail,Main"),
        ("Escort", "Keep the escort fighters alive", "20,-20,Complete"),
        ("Sensor", "Keep the RQ-180 alive", "15,-15,Complete"),
    ],
    # The complex is the target: the stream's Standoff rounds on it, not an
    # arrival circle 57 NM short of it.
    victory=dict(kind="destroy", stations=["complex"], min_units=1,
 objective="Stream"),
    fatal=[F("Stream", ["stream"], 2)],
    neutral_objective="Escort",
    win=(
        "A launcher target in the complex has been destroyed. Account for the bomber package, "
        "escorts and reconnaissance aircraft before committing to another attack."
    ),
    lose=(
        "The strike has failed. Account for the surviving package and report the launcher "
        "threats that remain."
    ),
    stations={
        "stream": S(-4.4, 130.1, "Bomber stream", heading=28, alt=38000),
        "escort": S(-4.2, 130.4, "Escort", heading=28, alt=40000),
        "sensor": S(-3.2, 130.8, "RQ-180 track", heading=28, alt=60000),
        "red_air": S(-2.4, 129.1, "Opposing fighters", heading=150, alt=42000),
        "red_bomber": S(-2.6, 129.3, "Opposing bomber", heading=150, alt=36000),
        "complex": S(-1.0, 131.5, "Launcher complex", heading=180),
        "sea": S(-4.6, 131.95, "Offshore picket", heading=270),
        "cvn": S(-5.4, 132.2, "Ford", heading=330),
        "home": S(-12.5212, 131.0, "RAAF Base Darwin"),
        # Darwin is 500 NM from the escort station - outside an F-16CM's 360
        # NM radius and an F-15EX's 480. The Kai strip is 164 NM.
        "strip": S(-5.2953, 132.9232, "Langgur forward strip"),
        "red_field": S(-1.1, 136.2, "Enclave field", heading=90),
    },
    units=[
        # The counters the brief promises: AIM-424 under the Widows, the
        # very-long-range fit under the Viper. They flew Empty and AirToAir.
        U("blue", "yf-23-black-widow-ii", "usaf_yf-23_black_widow_ii", "escort",
          name="Black Widow 11", loadout="AirToAirIntercept"),
        U("blue", "yf-23-black-widow-ii", "usaf_yf-23_black_widow_ii", "escort",
          name="Black Widow 12", loadout="AirToAirIntercept"),
        # Long Reach is a strike mission and the Eagle II flies a strike fit.
        # It also has to: the f-15ex mod is reached through the targeting pod
        # its strike loadouts hang, and the default air-to-air fit hangs
        # nothing of that mod's at all.
        U("blue", "f-15ex", "usaf_f-15ex_SEII", "escort", name="Eagle II 21",
          loadout="StrikePrecision"),
        U("blue", "SEST_F16CM_JATM", "usaf_f-16cm-bl52d", "escort",
          name="Viper 31", loadout="AirToAirVLongRange"),
        U("blue", "SEST_Rafale_F5", "fr_rafale_m_l", "escort", name="Rafale 41"),
        U("blue", "rq-180-white-bat", "usaf_rq-180", "sensor",
          name="White Bat 01", weapons="Hold"),
        U("blue", "SEST_B52_ARRW", "usaf_b-52o", "stream", name="Stream 01",
          loadout="Standoff"),
        U("blue", "b-1b", "usaf_b-1b_dts", "stream", name="Stream 02"),
        U("blue", "b-52h", "dts_b-52h", "stream", name="Stream 03"),
        # Onto the stream's line and back down it to where it launched: the
        # orbit was 134 NM north-north-west of the stream and 96 NM off its
        # track, and the J-50's PL-15s never reached it.
        U("red", "j-36-tailless", "plaaf_j36", "red_air", name="Tailless 51",
          route=_D6_HUNT, telegraph=3),
        U("red", "j-50", "plan_j-50", "red_air", name="Silent 52",
          route=_D6_HUNT, telegraph=3),
        U("red", "3m25-meteorit", "wp_tu-95ma", "red_bomber", name="Meteorit 90",
          loadout="AntiShip"),
        U("red", "pla-land-unit-pack", "pla_df-26b_tel", "complex",
          name="Relocatable launcher"),
        U("red", "pla-land-unit-pack", "pla_h-200a_radar", "complex",
          name="Complex radar"),
        U("red", "type-003-004-maneuverwarfare", "plan_cvn_004", "sea",
          name="Type 004 picket"),
        U("blue", "_vanilla", "airfield_small_1", "strip",
          name="Langgur forward strip", weapons="Hold"),
        U("red", "modern-chinese-airbase", "pla_airbase_modern", "red_field",
          name="Enclave field", weapons="Hold"),
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
    intro=(
        "Darwin approaches, July 1988. A PITCH BLACK strike serial has gone live: shoot down "
        "the Bear before its release line and protect the high-altitude reconnaissance "
        "aircraft."
    ),
    sender="Exercise Director, PITCH BLACK 88, maritime phase",
    intent=((
        "The exercise went live at 0412. Kill the Bear before its release line, keep the U-2 "
        "safe and leave the Badger tanker out of the engagement; the umpires still score a "
        "shot at it."
    )),
    date=(1988, 7, 12), time=(5, 55), sea=3, clouds="Scattered_1", wind="SE",
    difficulty=3, minutes=60, centre=(-11.0, 130.2),
    blue_nation="USA", red_nation="Russia",
    brief=(
        (
            "DARWIN APPROACHES, JULY 1988. Exercise PITCH BLACK's maritime phase places an "
            "American carrier group south of the Arafura against a mixed aggressor force flying"
            " Soviet and Chinese profiles.\\n\\nA Bear G is running the maritime strike serial "
            "with a Badger tanker behind it. Dragon 41, the U-2, is high over the exercise box;"
            " the Nighthawk detachment faces the aggressor squadron's J-8s and MiG-23. Airborne"
            " and ship radar reports form the working picture.\\n\\nIt was an exercise until "
            "0412, when the Bear released a live round at the range ship and the aggressors "
            "started answering with real missiles. Kill the Bear before its release line and "
            "protect Dragon 41 throughout the engagement. The umpires are still on the net: the"
            " Badger tanker is out of play and a shot at it is scored against you."
        )),
    forces="USS Kitty Hawk, F-14A and F-117 detachments, a B-52G, a U-2, "
           "an Italian Tornado on exchange. Aggressors: two J-8, a MiG-23, a "
           "Bear G, a Tu-16N tanker.",
    objectives=[
        ("Serial", "Kill the Bear before its release line", "35,-25,Fail,Main"),
        ("Recovery", "Keep Dragon 41 safe throughout the interception", "15,-15,Complete"),
        ("Umpire", "Do not engage the Badger tanker; it is excluded from this exercise serial", "0,-20,Complete"),
    ],
    victory=dict(kind="destroy", stations=["aggressor#1"], min_units=1,
                 objective="Serial"),
    # "Before its release line" used to be prose: nothing failed the serial
    # until the clock ran out. The Bear inside five miles of its release
    # point now ends it.
    denied=[dict(units=["aggressor#1"], at=(-10.9, 130.1), radius=5,
                 objective="Serial",
                 message=(
                     "EXERCISE CONTROL: BEAR G 90 has reached its release area with the serial "
                     "intact. The umpires score the launch against the surface group and close "
                     "the serial. Pass the radar record to the debrief staff."
                 ))],
    fatal=[],
    neutral_objective="Umpire",
    win=(
        "The Bear is down short of its release line. Report the reconnaissance aircraft's "
        "status and account for the remaining exercise participants."
    ),
    lose="The serial got through. Somebody's squadron is buying the drinks and "
         "writing the report.",
    stations={
        "cap": S(-11.4, 129.6, "Exercise CAP", heading=20, alt=28000),
        "strike": S(-11.6, 129.9, "Strike detachment", heading=20, alt=24000),
        "high": S(-12.0, 130.5, "High assets", heading=90, alt=60000),
        "aggressor": S(-8.8, 129.2, "Aggressor force", heading=180, alt=30000),
        # The Badger's own station, on the spot it held as the Bear's #2.
        "tanker": S(-8.8, 129.25, "Badger tanker", heading=180, alt=30000),
        # The fighters sweep ahead of the Bear instead of flying its speed.
        "sweep": S(-9.6, 129.6, "Aggressor sweep", heading=180, alt=30000),
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
        # To the release line on the 157 line, 82 NM short of Kitty Hawk,
        # where the serial ends (the `denied` terminal below). The leg out on
        # the reciprocal only flies if that terminal ever fails to fire - it
        # keeps her from circling the release point in that case.
        U("red", "tu-95k-22", "wp_tu-95_bearg", "aggressor", name="Bear G 90",
          route=[(-10.9, 130.1, 30000), (-6.5, 128.2, 30000)], telegraph=3),
        # Its own station: flying in the Bear's Vic took the out-of-play
        # tanker down to within 42 NM of weapons-free Tomcats.
        U("red", "tu-16n", "wp_tu-16n", "tanker", name="Badger tanker",
          weapons="Hold"),
        # Ahead of the Bear, then onto the strike detachment's station -
        # inside AA-7 reach of the CAP, which is where the sweep's job is.
        U("red", "j-8", "plaaf_j-8f", "sweep", name="Aggressor 51",
          route=_D7_SWEEP, telegraph=3),
        U("red", "j-8", "plaaf_j-8f", "sweep", name="Aggressor 52",
          route=_D7_SWEEP, telegraph=3),
        # The Custom Loadout Editor's own files are its ammunition and its
        # authoring UI; its patches/ folder is not a path the game loads. The
        # aggressor Flogger's air-to-air fit hangs its rounds, which is the
        # only way a mission can make the game read it.
        U("red", "custom-loadout-editor", "wp_mig-23a", "sweep",
          name="Aggressor 53", route=_D7_SWEEP, telegraph=3),
    ],
))

MISSIONS.append(dict(
    group="dispatch", num="D8", key="The Long Perimeter", place="Southern Papua",
    intro="Allied Dispatch. A US ground-support package holds a relief road "
          "open in southern Papua after the Biak relief window closed.",
    sender="Lieutenant Colonel R. Okafor, US ground-support package",
    intent=("The column reaches the airhead. The road is the corridor; the "
            "corridor is the relief. Hold the perimeter open, and bring the "
            "gunship home with fuel to spare."),
    date=(2028, 11, 14), time=(17, 30), sea=2, clouds="Broken_2", wind="E",
    difficulty=3, minutes=80, centre=(-7.5, 138.5),
    blue_nation="USA", red_nation="China",
    brief=(
        "SOUTHERN PAPUA, last light. With the Biak airlift over, relief moves "
        "by road, and the column has stopped twice today because the "
        "road is covered from a ridge nobody has cleared.\\n\\n"
        "A US package has been allocated for one evening: Apaches on the road, "
        "a Warthog pair on the ridge, a gunship on the loiter and a Strike "
        "Eagle holding the long shots. A Polish F-16 detachment "
        "transiting to the theatre has been pulled in for escort.\\n\\n"
        "Two Marine Ospreys are bringing the airhead's first lift in behind "
        "the column, and the ridge covers their approach as surely as it "
        "covers the road.\\n\\n"
        "Get the column - the relief truck is the column - to the airstrip. "
        "The gunship is usable only while no fighter radar is watching this "
        "sector: if the J-16 comes up, pull the gunship the moment its radar "
        "does. Losing the gunship ends the operation."),
    forces="An AH-64E and an AH-64D, two A-10Cs, an AC-130J, an F-15E, a "
           "Polish F-16C, a "
           "B-2 on a single allocated pass, and two MV-22B with the airhead's "
           "first lift. Opposing: a J-16, an attack "
           "helicopter, a PLA road "
           "detachment and a mobile SAM on the ridge.",
    objectives=[
        ("Column", "Get the relief truck to the airstrip", "35,-35,Fail,Main"),
        ("Gunship", "Do not lose the gunship", "20,-25,Complete"),
        ("Village", "Leave the settlements alone", "0,-30,Complete"),
        ("Lift", "Land the Osprey lift at the airstrip", "15,-10,Fail"),
    ],
    # The airhead IS the airstrip, and the cargo IS the truck: the box is
    # drawn on the strip and only the HEMTT counts. The reviewed build let
    # the Jaguar escort, or a civilian pickup, win it 19 NM from the strip.
    victory=dict(kind="arrive", units=["column#2"], station="column",
                 at=(-8.38, 140.35), radius=3,
 objective="Column"),
    fatal=[F("Gunship", ["support"])],
    neutral_objective="Village",
    win=(
        "The relief truck has reached the airhead and the gunship remains available. Report the"
        " Osprey lift separately and arrange recovery for the supporting aircraft."
    ),
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
        "ridge": S(-8.45, 140.42, "Covered ridge", heading=120),
        "ridge_air": S(-8.3, 140.72, "Attack helicopter", heading=250, alt=1500),
        "red_air": S(-8.6, 141.4, "Opposing fighter", heading=270, alt=30000),
        "home": S(-12.6188, 142.094, "RAAF Base Scherger"),
        # A perimeter operation flies from the perimeter. Everything here
        # was homed on Scherger 370 NM back - inside a Warthog's legs
        # and outside a Viper's, and a long way to send an Apache.
        "strip": S(-8.38, 140.35, "Forward airstrip"),
        "traffic": S(-8.52, 140.48, "Road traffic", heading=300),
        # 58 NM south-west of the strip, inbound: the last five miles are
        # inside the ridge Tor's envelope, so the lift arrives when the
        # ridge is cleared or it arrives under fire.
        "lift": S(-9.0, 139.6, "Osprey lift", heading=35, alt=3000),
    },
    units=[
        U("blue", "ah-64", "usa_ah-64e", "gun", name="Gunfighter 11"),
        U("blue", "ah-64", "usa_ah-64d", "gun", name="Gunfighter 12"),
        U("blue", "a-10c", "usa_a-10c", "gun", name="Hog 21", alt=8000),
        U("blue", "SEST_A10C_Plus", "usaf_a-10c_plus", "gun", name="Hog 22",
          alt=8000),
        U("blue", "ac-130-pack", "usaf_ac-130j", "support", name="Spectre 31"),
        U("blue", "f-15e-strike-eagle", "usaf_f-15e_SE", "escort",
          name="Strike Eagle 41"),
        U("blue", "f-16c-modern", "pol_f-16c-bl52plus", "escort",
          name="Viper 51", loadout="AirToAir"),
        U("blue", "b-2-spirit", "usaf_b-2_spirit", "pass", name="Spirit 01"),
        U("blue", "french-army-vehicles", "fr_afv_jaguar", "column",
          name="Column escort", route=[(-8.38, 140.35, 0)], telegraph=3),
        U("blue", "re-power-resupply", "usa_car_hemtt", "column",
          name="Relief column", route=[(-8.38, 140.35, 0)], telegraph=3),
        U("red", "pla-land-unit-pack", "pla_9k331", "ridge",
          name="Mobile SAM, ridge"),
        U("red", "pla-land-unit-pack", "pla_apc_zbl-08", "ridge",
          name="Road detachment"),
        U("red", "j-16a", "plaf_j16a", "red_air", name="Enclave 61"),
        # The attack helicopter's own file says CarrierCapable=False; it was
        # homed on a Type 071 that does not list it. It belongs over a road.
        U("red", "z-21", "pla_z21", "ridge_air", name="Ridge flight", alt=1500),
        U("neutral", "buildings-targets-missions", "4tentgroup", "ridge",
          name="Settlement"),
        U("neutral", "pickup-truck-extension", "civ_car_pickup_1983", "traffic",
          name="Civilian traffic"),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_scherger", "home",
          name="RAAF Base Scherger", nation="australia", weapons="Hold"),
        U("blue", "_vanilla", "airfield_small_1", "strip",
          name="Forward airstrip", weapons="Hold"),
        U("blue", "mv-22b-osprey", "mv22b_osprey", "lift", name="Dragon 71",
          weapons="Hold", loadout="Transport"),
        U("blue", "mv-22b-osprey", "mv22b_osprey", "lift", name="Dragon 72",
          weapons="Hold", loadout="Transport"),
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
    "Operations around the northern approaches. Western Passage, Flight Deck Day, The "
    "Relief Ship and The Long Perimeter follow European and American detachments through "
    "the crisis. Return Passage follows a Russian auxiliary's withdrawal. Range Week "
    "records a live counter-launcher and missile-defence trial. Long Reach follows a bomber"
    " escort in March 2034, while Before the Lifeline returns to the morning in 1988 when a"
    " PITCH BLACK exercise serial in the same waters went live."
)


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
    intro="Optional. MV Torres Light stopped reporting on a route nobody "
          "was watching, and the Meridian ship that sailed with her yesterday "
          "is going back for her. Get there first.",
    # The first build flew this with a placed HMAS Arafura and a placed
    # Seahawk and deployed nothing of the player's (blank generation), so the
    # morning after White Water the ship the player had lost was back and the
    # damage they had taken was gone. It is the player's force now, sailing
    # as White Water left it - a detachment of it, their choice which.
    special=(
        "Select a detachment from the ships available after the Arafura passage, with an "
        "embarked helicopter if assigned. Recover Torres Light's bridge recorder before "
        "Meridian reaches her. Its evidence can support the next Gulf of Papua convoy's "
        "submarine assessment. The recovery request closes once that convoy passage is "
        "complete."
    ),
    sender="Commodore Alex Mercer",
    intent=("One coaster, one recorder, and one ship out there that wants "
            "it more than we do. Get your lead ship alongside first. This is "
            "not a war yet: "
            "Meridian's ship has not fired on anyone, and I would rather "
            "explain a lost recorder than a sunk supply ship."),
    date=(2028, 10, 19), time=(16, 10), sea=3, clouds="Broken_2", wind="NW",
    difficulty=2, minutes=90, centre=(-10.3, 131.8),
    blue_nation="Australia", red_nation="China",
    brief=(
        "ARAFURA SEA, late afternoon. MV Torres Light stopped transmitting "
        "nineteen hours ago on a coastal route that carries no traffic worth "
        "interfering with. A Poseidon found her an hour ago: adrift, holed "
        "above the waterline, crew in the boats and her bridge recorder "
        "still aboard.\\n\\n"
        "She was not alone yesterday. A Meridian supply ship, a Delvar-class "
        "hull with a crane and no business on this route, was in company "
        "with her and has turned back towards her from the south-east. Her "
        "master says it is a salvage claim. What is on that recorder says "
        "otherwise.\\n\\n"
        "Your detachment is eighteen miles out; Meridian's ship is fourteen, "
        "and slow. Identify Torres Light and get your lead ship alongside "
        "her first. Meridian's ship has not fired and is not a target - sinking "
        "her settles the race and starts the shooting war "
        "everyone is working to avoid. The "
        "lane between you and her carries ordinary traffic. Your weapons "
        "are tight."),
    forces="Your detachment, and its Seahawk if one is embarked. Torres "
           "Light "
           "adrift; one Meridian support ship closing on her; four merchant "
           "and fishing contacts on the lane.",
    objectives=[
        ("Search", "Identify Torres Light and get your lead ship alongside "
                   "her before Meridian's ship", "30,-25,Fail,Main"),
        # `spare` - restraint, scored on the ship the text names. Done, it
        # pays by its own end-status; sink her, and it fails.
        ("Restraint", "Do not sink the Meridian ship", "10,-20,Complete"),
        ("Traffic", "Harm no lane traffic", "0,-25,Complete"),
    ],
    # Stage: Torres Light classified. Win: the lead ship - Taskforce1Vessel1,
    # which the generated mission replaces with the player's first ship - in
    # a mile and a half of her. The win writes O1BeaconFound, so a recorder
    # Meridian got to first puts nothing on Steel Highway's plot.
    victory=dict(kind="arrive", station="patrol", at=(-10.4, 131.9),
                 radius=1.5, min_units=1, objective="Search",
                 sets="O1BeaconFound",
                 after=dict(kind="classify", units="wreck", min_units=1,
                            intel=(
                                "ESCORT WATCH: TORRES LIGHT identified, adrift with damage "
                                "above the waterline and boats reported alongside. The bridge "
                                "recorder is believed to remain aboard. Get the lead ship "
                                "alongside her, inside a mile and a half, before MERIDIAN "
                                "SALVOR reaches her. Maintain contact with both vessels."
                            ))),
    declares=["O1BeaconFound"],
    # The win names the lead ship alone, so losing her ends it - stock's
    # "Flagship must survive", paired with every anchor-named win in Pacific
    # Strike. Without it a detachment that lost her sailed on toward a win
    # nothing could give.
    fatal=[F("Search", ["patrol"])],
    # The race, lost: Meridian's ship within a mile of the coaster. Stock
    # ends a mission on an ENEMY unit reaching an area the same way - 01
    # Raid on Okinawa's "Assault unit reaches Kume - player defeat" is a
    # UnitsInTheArea on a Taskforce2 unit, AreaDisplaySide=Both.
    denied=[dict(units=["meridian"], at=(-10.4, 131.9), radius=1.0,
                 objective="Search",
                 message=(
                     "ESCORT WATCH: MERIDIAN SALVOR is alongside TORRES LIGHT and her crane is "
                     "working. The recorder is going aboard a ship we cannot stop without sinking"
                     " her. The recovery has failed; the order not to sink the Meridian vessel "
                     "remains in force."
                 ))],
    neutral_objective="Traffic",
    win=(
        "The lead ship has reached Torres Light before Meridian Salvor. The recovery party can "
        "secure the bridge recorder and bring the survivors aboard. Preserve the recordings for"
        " the intelligence cell; maintain the order not to attack Meridian's vessel."
    ),
    lose="Torres Light's recorder is not in our hands, and without it nobody "
         "on this side can say what happened to her.",
    stations={
        # The player's detachment forms here, 18 NM north-west of the wreck
        # on the game's datum: 16.5 NM to the 1.5 NM ring, 55 minutes at a
        # conservative 18 kn, 34 at an Anzac's 29, 45 at an Arafura's 22.
        "patrol": S(-10.22, 131.66, "Detachment", heading=125),
        # Ship's flight: beside the lead ship, low, on her heading.
        "flight": S(-10.24, 131.64, "Ship's flight", heading=125, alt=500),
        # The coaster herself, adrift at her last reported position.
        "wreck": S(-10.4, 131.9, "Torres Light, adrift", heading=0),
        # Lane traffic between the detachment and the datum, routes across
        # the lead ship's track.
        "traffic": S(-10.25, 131.75, "Lane traffic", heading=70),
        # Meridian's ship, 14 NM south-east of the wreck: 13 NM to her 1 NM
        # ring, 71 minutes at her 11 kn maximum. A frigate lead can spend half
        # an hour on the lane and still win; an Arafura lead has 26 minutes to
        # spare, and a lead slowed by White Water's damage less.
        "meridian": S(-10.55, 132.08, "Meridian support ship", heading=310),
    },
    units=[
        # The anchor: replaced by the player's first ship. Unnamed - the
        # builder refuses a name on a generated anchor.
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "patrol", variant="Variant3",
          weapons="Tight"),
        # The Ship's Flight slot a bought Seahawk fills. No trigger names it.
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          weapons="Tight"),
        U("neutral", "_vanilla", "civ_ms_encounter", "wreck",
          name="MV Torres Light"),
        U("neutral", "merchants-expanded", "civ_ms_mairangi_bay", "traffic",
          name="MV Arafura Trader", route=[(-10.15, 132.3, 0)], telegraph=3),
        U("neutral", "auxilliary-merchant-pack", "ran_ms_antares", "traffic",
          name="MV Melville Trader", weapons="Hold",
          route=[(-10.2, 132.25, 0)], telegraph=3),
        U("neutral", "re-power-resupply", "civ_ms_freighter_a", "traffic",
          name="MV Banda Trader", route=[(-10.1, 132.2, 0)], telegraph=3),
        U("neutral", "_vanilla", "civ_fv_sterntrawler_a", "traffic",
          name="Arafura trawler", route=[(-10.35, 131.95, 0)], telegraph=2),
        # Flank, straight for the coaster. Weapons Hold: she is racing, not
        # fighting, and she does not shoot first.
        U("red", "SEST_Replenishment", "ir_aor_delvar", "meridian",
          name="MV Meridian Salvor", weapons="Hold",
          route=[(-10.4, 131.9, 0)], telegraph=5),
    ],
))

MISSIONS.append(dict(
    group="contingency", num="C1", key="After the Wake", place="Gulf of Papua",
    expires_after="Rig Seventeen",
    intro="Contingency. MV Kerema Trader sailed without the Steel Highway "
          "convoy and went down last night. This is about her crew.",
    # MissionSpecialNote is a player-facing panel on the campaign map - stock
    # uses it for "Note: This is a detached submarine operation." The second
    # half of this note used to explain which engine feature the author could
    # not implement, which is a build note wearing a briefing's clothes. Why
    # the unlock is unconditional belongs in the build notes, and is there.
    # It used to be flown by a placed HMAS Hobart - a hull the player can buy
    # before Steel Highway and lose in it, which this mission then sailed
    # again the next morning. It is the player's own detachment now.
    special=(
        "Recover the crew of Kerema Trader, a separate casualty from the Gulf of Papua convoy. "
        "Select a detachment from the ships and embarked aircraft available after that passage."
        " The search remains outstanding regardless of the convoy's losses."
    ),
    sender="Commodore Alex Mercer",
    intent=((
        "Work the drift area to its northern boundary with your lead ship. Use the embarked "
        "helicopter if available and report survivors as they are found. Do not abandon the "
        "search to pursue an unconfirmed submarine contact."
    )),
    date=(2028, 10, 23), time=(6, 10), sea=4, clouds="Overcast", wind="SE",
    difficulty=2, minutes=75, centre=(-10.5, 144.5),
    blue_nation="Australia", red_nation="China",
    brief=(
        (
            "GULF OF PAPUA, first light. MV Kerema Trader sailed independent - Santos's people "
            "call it going without - and went down at 2140 last night with twenty-six aboard, "
            "forty miles off the convoy track. Eleven are accounted for. The rest are somewhere"
            " inside a drift box that has been growing all night.\\n\\nYour detachment is just "
            "south of the box. The Type 039C that sank her has not left the area - it is inside"
            " torpedo range of the box - and the search you need to run is exactly the pattern "
            "it will expect.\\n\\nTake your lead ship through the box to its northern edge, "
            "whatever you find. A Seahawk, if you have one embarked, covers more water than any"
            " hull. If the boat presents itself, classify it: pass that identification to "
            "command without delaying the search for survivors. Your weapons are tight."
        )),
    forces="Your detachment, and its Seahawk if one is embarked. One Type "
           "039C still in the area. Two merchant hulls diverted to assist.",
    objectives=[
        ("Survivors", "Take your lead ship through the drift box to its "
                      "northern edge",
         "30,-25,Fail,Main"),
        # `None` with a zero failure score - the native pairing for an
        # optional task. The boat is a bonus, as the brief says.
        ("Contact", "Classify the submarine", "10,0,None"),
        ("Assist", "Do not lose an assisting merchant or harm other traffic",
         "0,-25,Complete"),
    ],
    # The lead ship (Taskforce1Vessel1, which the generated mission replaces
    # with the player's first ship) at the box's northern edge. No timer: a
    # Time condition inside the Disabled win trigger reads either the mission
    # clock or the time since it was enabled, and stock does not settle which
    # - one reading made "past the half hour" a no-op, the other put the win
    # after the deadline at 18 kn. The helicopter the first build scored is a
    # Ship's Flight slot now, and no trigger may name a slot.
    victory=dict(kind="arrive", station="hobart", at=(-10.4, 144.6), radius=3,
                 min_units=1, objective="Survivors"),
    # The win names the lead ship alone, so losing her ends it (stock's
    # "Flagship must survive"). The Type 039C is weapons free on her track.
    fatal=[F("Survivors", ["hobart"])],
    neutral_objective="Assist",
    win=(
        "The lead ship has completed the assigned search leg to the northern edge of the drift "
        "area. Pass the actual recovery count and survivor reports to rescue coordination; the "
        "search track alone does not account for every missing person."
    ),
    lose="The box is open at the northern end and the weather is building. "
         "The rest of that crew stays missing.",
    stations={
        # The detachment just south of the box: 15 NM to the northern-edge
        # ring on the game's datum, 51 minutes at a conservative 18 kn in a
        # 75-minute window.
        "hobart": S(-10.7, 144.66, "Detachment", heading=350),
        "flight": S(-10.71, 144.64, "Ship's flight", heading=350, alt=500),
        "assist": S(-10.55, 144.55, "Assisting merchants", heading=20),
        "sub": S(-10.47, 144.7, "Submarine datum", heading=200),
    },
    units=[
        # The anchor: replaced by the player's first ship. Unnamed - the
        # builder refuses a name on a generated anchor.
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "hobart", variant="Variant3",
          weapons="Tight"),
        # The Ship's Flight slot a bought Seahawk fills. No trigger names it.
        U("blue", "us-navy-2027", "usn_mh-60r", "flight", alt=500,
          weapons="Tight"),
        # Not a Steel Highway hull: any of that convoy's four can be lost
        # the day before, and a page or a mission never names a losable hull
        # as alive. Coral Provider is the same ship, and the same hull, that
        # brings the dry stores to the Lifeline three weeks later.
        U("neutral", "auxilliary-merchant-pack", "ran_ms_super_p", "assist",
          name="MV Gulf Trader", weapons="Hold"),
        U("neutral", "re-power-resupply", "civ_ms_amra", "assist",
          name="MV Coral Provider"),
        # Across the box, towards the detachment's line of search.
        U("red", "plan-submarines", "plan_ss_type_039c", "sub",
          name="Contact BRAVO", depth="belowlayer",
          route=[(-10.6, 144.6, "belowlayer")], telegraph=2),
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
# air operations (SW07, SW08) and O2 stay authored, and O2 disables the
# builder the way the stock campaign's detached operations do. None of them
# names a hull the player can buy: SW07's picket is the unsold Arunta, not
# Perth, who can be lost three days earlier. O1 and C1 sail the player's
# ships - stock's 03B shape - because each follows a mission the player can
# lose hulls in by a day, and a detached cast there brought back a ship they
# had lost.
# =============================================================================

SCHEDULE = {
    # num: (date, completion points, service window, generation, anchor station)
    "01": ((2028, 10, 18), 100, False, "Generated", "warramunga"),
    "O1": ((2028, 10, 19), 50, False, "Generated", "patrol"),
    "02": ((2028, 10, 22), 140, False, "Generated", "escort"),
    "C1": ((2028, 10, 23), 0, False, "Generated", "hobart"),
    "O2": ((2028, 10, 24), 50, False, None, "patrol"),
    "03": ((2028, 10, 26), 120, True, "Generated", "escort"),
    "04": ((2028, 10, 30), 100, False, "Generated", "patrol"),
    "05": ((2028, 11, 2), 140, True, "Replaced", "warramunga"),
    "O3": ((2028, 11, 4), 60, False, "Generated", "escort"),
    "06": ((2028, 11, 6), 140, False, "Generated", "hobart"),
    "07": ((2028, 11, 9), 120, True, None, "picket"),
    "O4": ((2028, 11, 10), 50, False, "Generated", "escort"),
    "08": ((2028, 11, 13), 180, False, None, None),
    "09": ((2028, 11, 16), 160, True, "Generated", "escort"),
    "10": ((2028, 11, 20), 180, False, "Generated", "escort"),
    "11": ((2028, 11, 23), 200, True, "Generated", "escort"),
    "C2": ((2028, 11, 25), 30, False, "Generated", "escort"),
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
    ("24 October 2028", "Situation report 1", "The Arafura convoy is through",
     "THE ESCORT TASK IS FORMALISED",
     ["Warramunga's report of the Arafura rendezvous went to Canberra inside "
      "an hour and came back the next morning as a standing task. There is "
      "now an Australian maritime task group, it has a name, and it has an "
      "escort group forming around whichever hulls came back from the Gulf "
      "of Papua.",
      "Port Moresby's engineering plant is ashore. Commander Kila's message "
      "on arrival was three words long and is not printable in a family "
      "newspaper. The Pukpuk Treaty's access arrangements are being read "
      "carefully, "
      "by people who had not read them before, in three capitals.",
      "The Indonesian patrol vessel that challenged Meridian Safety Escort "
      "Seven on the eighteenth has been credited, publicly, by Jakarta. The "
      "escort has not been named in public. Meridian's statement calls the "
      "exchange of fire \"a misunderstanding at "
      "sea\" and announces expanded safety-escort coverage \"in response to "
      "client demand\".",
      "The task group's next request comes from Jakarta, for an offshore "
      "platform in the Timor Sea that armed Meridian contractors are "
      "holding."],
     "Rig Seventeen"),
    ("31 October 2028", "Situation report 2",
     "The supply network behind Meridian's hard-liners",
     "THE HARD-LINERS HAVE HELP",
     ["The Rig Seventeen crews are ashore in Darwin and Kupang. The "
      "low-profile "
      "craft tracked into the Banda approaches is in a shed with "
      "photographers around it, and what it was carrying matters less than "
      "where it was going: a Meridian terminal that had been declared closed "
      "for a month.",
      "Two of the hard-liners' supply routes now have names on a chart. The "
      "people running "
      "them do not. The Meridian duty controller net went off the air on "
      "Saturday and has not come back, which the intelligence staff regard as "
      "the most informative thing it has ever done.",
      "Meridian's board has issued a statement disowning \"unauthorised "
      "actions by a security subsidiary\". Its hard-line faction has issued "
      "nothing, holds a service platform and several logistics sites, and "
      "has not disarmed when told to. One airfield-and-port enclave, on Biak "
      "off Indonesian Papua, has not been recovered.",
      "The task group's next convoy sails Wednesday. Meridian Safety Escort "
      "Seven, which fired on the Indonesian patrol on the eighteenth, has "
      "been seen again, and it has not changed its ways."],
     "Weapons Free"),
    ("7 November 2028", "Situation report 3", "Overt attacks begin",
     "THIS IS NO LONGER DENIABLE",
     ["A Chinese Sovremenny-class destroyer fired on a protected convoy in "
      "daylight on the second, and a Royal Australian Navy warship answered. "
      "The recordings from "
      "three platforms are unambiguous and the diplomatic language changed "
      "the same afternoon. Nobody is calling it a misunderstanding.",
      "A Chinese naval task group has arrived in the northern approaches "
      "under what Beijing describes as a protection-and-evacuation mission, "
      "and has "
      "demanded that coalition patrols suspend. The demand has been declined. "
      "The force has not gone home. Commodore Mercer's assessment to "
      "Canberra, which has leaked in the way these things do, was one line: "
      "\"They can close the lane for a month. They cannot hold it for two.\"",
      "Growler and wider surveillance allocations were released to the task "
      "group this week. What this week has established, and what the "
      "ledger will record, is that damage and magazine expenditure are no "
      "longer things the force can simply absorb between operations.",
      "The next problem is not a ship. It is a tanker, and how many aircraft "
      "are depending on it at once."],
     "Long Way Home"),
    ("14 November 2028", "Situation report 4", "The corridor is open",
     "THE WINDOW HELD",
     ["The relief movement is out of the enclave. The first hundred people "
      "were on the ground at Tindal before the battery that covered the field "
      "had finished being surprised. The negotiation that follows starts from "
      "a better place than the one that would have followed a closed window, "
      "and the negotiators know it.",
      (
          "Port Moresby's engineers are bringing the delivered plant into service. Commander "
          "Kila reports that reliable power and medical stores remain the immediate priorities."
          " The task group's separate relief operations are being assessed on their own "
          "reports; a clear sea route does not mean every road is open."
      ),
      "Tanker hours, not hulls, were the limiting factor this week. Wing "
      "Commander Ward has said so in writing, twice, and will be saying it "
      "again.",
      "The task group's replenishment ship has been at sea for three weeks. "
      "HMAS Collins has been at sea for five. They are going to meet, and "
      "something is going to try to stop them."],
     "Southern Lifeline"),
    ("21 November 2028", "Situation report 5", "The route is sustained",
     "THE LIFELINE HOLDS",
     ["The service window in the rear area held. HMAS Collins, which needed "
      "it, is dived and heading for Stirling, and HMAS Stalwart, which gave "
      "it to her, still has enough in her tanks to do it again, which was "
      "the point.",
      (
          "The Japanese ASW detachment has supported the eastern Banda passage. The priority "
          "cargo reached the handover under a combined escort. Command is still accounting for "
          "the condition of the ships that made it through; completing the passage did not "
          "require every merchant or escort to return undamaged."
      ),
      "The Chinese carrier group, Fujian and Liaoning with their escorts, has "
      "moved south into the waters the corridor runs through, and the "
      "ceasefire talks that "
      "were supposed to open on Thursday have been moved to Friday to see what "
      "happens first. The Commodore's note to the force this morning did not "
      "mention the talks. It said: \"Keep the transports moving. Keep the "
      "high-value ship alive. Everything else is the enemy's problem.\"",
      "What the ledger says about the task group after five weeks, the ledger "
      "says. What it does not say is that the corridor closed. It did not."],
     "Fujian's Shadow"),
    ("27 November 2028", "Before the last passage", "An imperfect ceasefire",
     "ONE PASSAGE THAT MUST WORK",
     [(
         "The talks opened with the corridor open, which is the only reason they opened at all."
         " A ceasefire took effect at midnight. Not every Chinese group in the corridor has "
         "acknowledged it, and the one the intelligence staff are watching has not."
     ),
      "Coral Pioneer is at the head of the first convoy through. Her master "
      "has declined a replacement ship, a replacement crew and, in writing, a "
      "replacement master. She has a bearing running hot and a chief engineer "
      "who says it will hold if nobody asks him how.",
      "The escorts that will take her through are the escorts that are left. "
      "The ledger has the list. What the list does not record is that every "
      "name on it has done this before, in this water, against these people, "
      "and that the people on the other side know it.",
      "Everything the last six weeks were about is in tomorrow's passage."],
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
             "by silhouette: most are the same classes as the commercial "
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
             (
                 "4. Guidance to the force. Meridian Safety Escort Seven, which fired on the "
                 "Indonesian patrol on 18 October, passed for six hours as a commercial hull on"
                 " AIS and merchant reports. Judge a contact by its behaviour and emissions, not"
                 " its flag or owner."
             )],
         note=(
             "Ownership is not hostile intent. Confirm the contact and its actions.  - Cdre "
             "Mercer"
         )),
    dict(file="00c_santos_log", before="Steel Highway", form="log",
         title="Master's log, MV Coral Pioneer\\n18 October 2028",
         sub="Deck log extract, the morning of the rendezvous",
         ship="MV Coral Pioneer", master="L. Santos", date="18 October 2028",
         entries=[
             ("0412", (
                 "Main engine casualty: No. 2 turbocharger. Reduced to 6 kn. Informed convoy "
                 "commodore aboard MV Gove Trader and the Darwin reporting centre."
             )),
             ("0430", "Contact hailed us on Ch16 as \"Meridian Safety Escort "
                      "Seven\". Stated we were \"under safety inspection\" and "
                      "to heave to. Asked for authority. Was told it was "
                      "\"regional\". Declined."),
             ("0447", "Escort Seven closed to 2 cables. Armed party visible on "
                      "the bridge wing. Will miss 0500 rendezvous with relief "
                      "vessel."),
             ("0455", "Indonesian patrol vessel on the horizon to the north, "
                      "challenging Escort Seven on Ch16."),
             ("0503", "Gunfire, bearing north. Not at us. Crew mustered below."),
             ("0510", "Escort Seven broke off and stood north-east. Lost "
                      "visual in haze."),
             ("0540", "Warship on radar to the west, closing fast. Have "
                      "not raised her. Chief Engineer says we can make 8 kn if "
                      "nobody asks him how.")],
         note=(
             "Note for owners: I did not heave to. I will not heave to for anyone whose "
             "authority is \"regional\". If that is now company policy, the company can find "
             "another master. - L.S."
         )),
    dict(file="00d_kila_cable", before="Steel Highway", form="signal",
         title="Port Moresby request\\n21 October 2028",
         sub="Signal from the PNG Defence Force maritime liaison",
         header=[("FROM:", "CDR M. KILA, PNGDF MARITIME ELEMENT, PORT MORESBY"),
                 ("TO:", "COMAUSMARTG (CDRE MERCER)"),
                 ("DTG:", "210600Z OCT 28"), ("PREC:", "PRIORITY"),
                 ("SUBJ:", "PROTECTED DELIVERY, MORESBY")],
         body=[
             "1. PORT MORESBY GENERAL HOSPITAL IS ON GENERATOR. THE POWER "
             "PLANT THAT REPLACES IT IS IN MV KOKODA STAR. THE FUEL TO RUN THE "
             "GENERATOR UNTIL THEN IS IN MV LAE PROVIDER. THAT IS THE ORDER OF "
             "PRIORITY IF YOU HAVE TO CHOOSE, AND I AM TOLD YOU MAY HAVE TO.", "",
             "2. A SUBMARINE REPORT WAS PASSED TO US THIS MORNING FROM A "
             "FISHING VESSEL OFF THE TRACK. UNCONFIRMED. THE MASTERS HAVE BEEN "
             "TOLD. THEY WANT TO SAIL ANYWAY. I HAVE NOT ARGUED.", "",
             "3. WE CAN OFFER A PATROL BOAT AT THE ENTRANCE TO THE GULF OF "
             "PAPUA AND NOTHING FURTHER OUT. EVERYTHING BETWEEN THE ARAFURA "
             "AND THE GULF, TORRES STRAIT INCLUDED, IS YOURS.", "",
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
             "4. A PATROL CRAFT IS CLOSING FROM THE NORTH. IT IS NOT OURS; WE "
             "BELIEVE IT IS A MERIDIAN ESCORT. WE HAVE ASKED IT TO STAND OFF. "
             "IT HAS NOT ANSWERED.", "",
             "5. I WILL BE ON THE FLAGSHIP'S BRIDGE FOR THE DURATION. IF THE "
             "TERMS ABOVE BECOME IMPOSSIBLE TO KEEP, I WOULD RATHER HEAR IT "
             "FROM YOU THAN READ IT.", "",
             "PRASETYO"]),
    dict(file="02b_meridian_intercept", before="Weapons Free",
         form="signal", strap="INTERCEPT",
         title="Intercept: Meridian net\\n1 November 2028",
         sub="Commercial HF, transcribed",
         header=[("NET:", "COMMERCIAL HF, 8291 KHZ"), ("DTG:", "010340Z NOV 28"),
                 ("NOTE:", "TRANSLATED / TRANSCRIBED. A: \"MERIDIAN CONTROL\". "
                           "B: \"ESCORT SEVEN\". PARTIAL.")],
         body=[
             "A:  Seven, Control. Your inspection point is confirmed for "
             "tomorrow. The group is four hulls plus one grey.",
             "B:  One grey. Say again the grey.",
             (
                 "A:  One warship. Same one as the eighteenth. You are to establish the "
                 "inspection and hold the group until the northern element is in position. Do "
                 "not engage the grey unless engaged."
             ),
             "B:  Control, Seven. The grey engaged the last time. It will do it again.",
             "A:  Then you will have been engaged. Control out.",
             "B:  [unreadable] ... eight minutes ... [unreadable]"],
         note=(
             "The 'northern element' is assessed as the Chinese surface group reported on 30 "
             "October: a Sovremenny-class destroyer and a Type 071 transport. Patrol reporting "
             "and satellite imagery support the group identification; its present course "
             "requires local confirmation. Speaker A's traffic pattern matches the Meridian "
             "duty controller, off the previous channel since 28 October. The net moved."
         )),
    dict(file="03b_ward_memo", before="Long Way Home", form="signal",
         title="Air component note\\n8 November 2028",
         sub="What tomorrow's flying programme actually costs",
         header=[("FROM:", "WGCDR D. WARD, AIR COMPONENT, RAAF TINDAL"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "080500Z NOV 28"),
                 ("SUBJ:", "TOMORROW'S FLYING PROGRAMME - WHAT IT COSTS")],
         body=[
             "1. YOU HAVE ONE TANKER IN THE NORTH. NOT ONE TANKER TYPE. ONE "
             "TANKER: TEXACO 41, THE USAF KC-135. EVERY SORTIE PAST DARWIN'S "
             "UNREFUELLED RADIUS TOMORROW IS PLANNED "
             "AROUND IT BEING WHERE IT SAYS IT WILL BE, WHEN IT SAYS.", "",
             "2. TOMORROW'S PACKAGE OVER THE ENCLAVE - TWO SUPER HORNETS AND "
             "A GROWLER - HAS NO WEATHER MARGIN. IF IT IS HELD UP, IT WILL "
             "NEED THE TANKER BEFORE IT CAN THINK ABOUT ANYTHING ELSE.", "",
             (
                 "3. THE RUSSIAN DETACHMENT'S MIG-31 SECTION AT BIAK IS ASSESSED TO KNOW THE "
                 "TANKER'S GENERAL OPERATING AREA FROM REPEATED FLIGHTS AND EMISSIONS. ITS "
                 "EXACT INFORMATION IS UNKNOWN. PROTECT THE TANKER TRACK AND EXPECT AN APPROACH"
                 " FROM THE ENCLAVE."
             ), "",
             (
                 "4. IF THE TANKER IS LOST, EVERY PACKAGE STILL AIRBORNE LOSES ITS FUEL AND THE "
                 "NEXT DAY'S SORTIES MUST BE REPLANNED. PROTECT IT. DO NOT ASSUME ANOTHER "
                 "AIRFRAME IS AVAILABLE TO REPLACE IT."
             ), "",
             (
                 "5. WEDGETAIL WILL PASS THE INTERCEPTOR PICTURE AS RADAR CONTACTS ARE ACQUIRED"
                 " AND CORRELATED. A LINK REPORT CARRIES THE OBSERVATION TIME AND SOURCE; CHECK"
                 " ITS AGE BEFORE ACTING. COVERAGE IS NOT A GUARANTEE OF DETECTION AT TAKEOFF. "
                 "WEDGETAIL PROVIDES WARNING; THE ESCORT AIRCRAFT MUST BREAK THE APPROACH."
             ), "",
             "WARD"]),
    dict(file="05b_opposing_intercept", before="Fujian's Shadow",
         form="signal", strap="INTERCEPT",
         title="Intercept: the Fujian group\\n22 November 2028",
         sub="Naval HF, partial decrypt, released to the force",
         header=[("NET:", "NAVAL HF, ENCRYPTED, PARTIAL DECRYPT"),
                 ("DTG:", "220110Z NOV 28"),
                 ("NOTE:", "TRANSLATED. SPEAKER: FUJIAN CARRIER GROUP COMMANDER, "
                           "TO FLEET HQ. ASSESSED AUTHENTIC.")],
         body=[
             "... the escorts are worn and the air wing has flown for nineteen "
             "days. I am not asking to withdraw. I am stating what the group "
             "can do. It can close the corridor for the period of the "
             "ceasefire talks. It cannot hold it against a determined passage "
             "and preserve "
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
         note=(
             "The commander's estimate is consistent with recent imagery and intercepted naval "
             "traffic placing FUJIAN and LIAONING in the Banda approaches. Those reports "
             "establish a last observed area, not a current launch position. Ford's aircraft "
             "must update it. The passage on 23 November is assessed as likely to be contested "
             "by a commander who would rather withdraw intact."
         )),
    dict(file="06b_santos_log", before="The First Ship Through", form="log",
         title="Master's log, MV Coral Pioneer\\n27 November 2028",
         sub="Deck log extract, the night before the passage",
         ship="MV Coral Pioneer", master="L. Santos", date="27 November 2028",
         entries=[
             ("1800", (
                 "Convoy conference aboard the escort flagship by boat. Told the ceasefire took"
                 " effect at 0000 and \"not everyone has acknowledged\". Asked what that meant "
                 "for us. Was told: \"Sail as planned.\""
             )),
             ("1830", (
                 "Chief Engineer reports No. 2 bearing at 71 degrees C and rising slowly. "
                 "Requests maximum 9 kn; 12 kn not advised. Commodore informed. Convoy speed "
                 "set to 9 kn."
             )),
             ("1900", "Crew briefed. Nobody asked to be relieved. Two asked "
                      "whether Escort Seven, the Meridian ship that ordered us "
                      "to heave to on 18 Oct, is out there. I said I did not "
                      "know. That is true."),
             ("2200", "Convoy formed, waiting for first light. Escorts on both "
                      "beams and one ahead. Sea state 2. Six weeks ago, in this "
                      "same water, a man with a \"regional\" authority told me "
                      "to heave to.")],
         note=(
             (
                 "Before the passage. On 18 October we refused Meridian's inspection. The "
                 "escorts made it possible to keep sailing afterwards. Other crews are using "
                 "the route behind us. That is what tomorrow's convoy must preserve.  - L.S."
             )
         )),
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
            "raaf_mq-4c_triton"]
BUY_01 = ESCORTS
# No amphibious ship, submarine, tanker or allied frigate is for sale: every
# one of them is a scripted theatre asset in the mission that needs it, and
# the reviewed build sold 1,100 points of hulls no mission could deploy and a
# KC-46 no field could receive. The Growler goes on sale before the strike
# it exists for.
BUY_02 = ESCORTS + ["ran_ddg_hobart", "usn_p8"]
# The F-35A goes on sale where it first flies. Window 03 used to sell it,
# and neither Rig Seventeen (no tasking rows) nor The Quiet Passenger (Ship's
# Flight and patrol only) has a row a fighter can take: a jet bought there
# sat at Tindal for two operations until Weapons Free's strike row, and
# window 05 sells it anyway.
BUY_03 = BUY_02
BUY_05 = BUY_03 + ["raaf_f-35a", "usn_fa-18f_blk3", "E7A_Wedgetail", "usn_ea-18g"]
BUY_07 = BUY_05 + ["raaf_mq-4c_triton"]
BUY_09 = BUY_07
# The carrier action tasks fighters and strike aircraft only, so window 11
# sells no Seahawk, Wedgetail or Triton: none of them has a row in Fujian's
# Shadow, and window 12 sells all three for the finale that does. The P-8
# stays - its Bomber role and AntiShip fit take the Attack row.
BUY_11 = [u for u in BUY_09
          if u not in ("usn_mh-60r", "E7A_Wedgetail", "raaf_mq-4c_triton")]
# SW12 replaces aircraft and repairs hulls; it does not sell new ones. That
# was a comment above the window until the allowlist made it a rule.
# The finale sells what its rows can fly - a CAP row for the fighters, the
# helicopter and patrol rows - and, after a fleet action that sails the whole
# force, a replacement hull or two. No Growler: there is no Attack row.
BUY_12 = ["usn_p8", "raaf_f-35a", "usn_fa-18f_blk3", "E7A_Wedgetail",
          "raaf_mq-4c_triton", "usn_mh-60r", "ran_opv_arafura", "ran_ffh_anzac"]

WINDOWS = {
    "01": dict(buy=True, situation=(
        "Assemble the escort force for the eighteenth. The Seahawk is not automatic: allocate "
        "an MH-60R here and assign it to Ship's Flight under Air Tasking, or the deck sails "
        "empty. Further force allocation is available before Steel Highway."
    ), allow=BUY_01, repair=True, rearm=True, flights=[HELO]),
    # A detachment of what White Water left, and a Ship's Flight row for the
    # Seahawk if one was bought. No builder, no repair: it is the next day.
    "O1": dict(flights=[HELO], detachment=True),
    "O2": dict(),
    "O3": dict(detachment=True),
    "O4": dict(detachment=True),
    "C2": dict(detachment=True),
    "02": dict(buy=True, situation="Force allocation before Steel Highway. The next window is before Rig Seventeen.", allow=BUY_02, repair=True, rearm=True,
               flights=[HELO, RECON]),
    # A detachment of what Steel Highway left, with a Ship's Flight row.
    "C1": dict(flights=[HELO], detachment=True),
    # Both lifters are granted assets an objective names; nothing is free.
    "03": dict(buy=True, situation=(
        (
            "Force allocation before Rig Seventeen. The Quiet Passenger uses the aircraft "
            "already allocated; the next window is before Weapons Free, and that operation "
            "sails one ship."
        )
    ), allow=BUY_03, repair=True, rearm=True),
    # A detachment: nobody sails the whole force to walk one contact.
    "04": dict(flights=[HELO, RECON], detachment=True),
    # "alone": the player picks a detachment rather than sailing everything
    # they own into a mission written for one frigate.
    # The guide's one-ship pattern: Replaced generation plus a unit limit.
    "05": dict(buy=True, situation=(
        (
            "Force allocation before Weapons Free - one ship of your choosing sails it. This is"
            " the last window before Southern Lifeline: Blind Horizon uses the aircraft already"
            " allocated, and Long Way Home and The Open Door are flown with allocated aircraft."
        )
    ), allow=BUY_05, repair=True, rearm=True, flights=[HELO, STRIKE],
               max_units=1, unit_type="Vessel",
               detachment=True),
    "06": dict(flights=[CAP, RECON], airbase_prep=True),
    # Long Way Home has no air-tasking row. Every aircraft in it - the tanker,
    # both Raptors, both Rhinos - is named by an objective, and an objective
    # may not depend on a cockpit the player fills. The window still buys,
    # repairs and rearms; it just has nowhere to put a bought aeroplane.
    # No builder here: the mission places its aircraft and generates no
    # force, so a ship bought in this window could not appear in it. BUY_09
    # carries BUY_07's list, so nothing is lost - it is on sale one mission
    # later, where the purchase can sail.
    # A service window before a blank-generation operation: repair and rearm,
    # no airbase prep (nothing of the player's flies it).
    "07": dict(repair=True, rearm=True),
    # A supplied detached package (blank generation, the guide's "launch
    # as-is"): no rows, no slots, no airbase prep - the aircraft are the
    # mission's own and the player flies what is placed.
    "08": dict(),
    "09": dict(buy=True, situation=(
        "Force allocation before Southern Lifeline. There is no further force allocation before"
        " Common Sea, and its rearm depends on the service window; the next window is before "
        "Fujian's Shadow."
    ), allow=BUY_09, repair=True, rearm=True, flights=[HELO, RECON]),
    # No ordinary hull purchases and no paid repair; the rearm is the
    # scheduled fallback, not a proved conditional gate.
    # The F-2As are the detachment's own anti-ship sortie, not a CAP slot
    # for the player to fill.
    # The Japanese ASW pair are the detachment's own; the player's Seahawks
    # arrive with the ships they are assigned to. One patrol slot.
    "10": dict(rearm_if=("SW09ServiceHeld", "IsTrue"), flights=[RECON]),
    "11": dict(buy=True, situation=(
        "Assemble and service the whole force before the carrier action. Only ships, fighters "
        "and strike aircraft are offered: the carrier action has no patrol or ship's-flight "
        "tasking. Repairs and replacement allocations, helicopters and patrol aircraft "
        "included, remain available before The First Ship Through."
    ), allow=BUY_11, repair=True,
           rearm=True, flights=[CAP, STRIKE]),
    # Aircraft replacement and repair only: no new hulls, no general rearm.
    # The finale flies what it sells: a CAP row for the fighters (Darwin is
    # the placed field), the helicopter and patrol rows.
    "12": dict(buy=True, situation=(
        "Final force allocation: replacement aircraft and escorts, with repairs where required."
        " No ammunition resupply is available; plan the passage around the magazines remaining "
        "after the fleet action."
    ), allow=BUY_12, repair=True,
           flights=[HELO, RECON, CAP], airbase_prep=True),
}

TIMEOUTS = {
    "01": "0630, half an hour after sunrise, and the merchants are still short "
          "of the Arafura. Whatever this was, it worked.",
    # Reached only once Meridian is out of the race: she is at the coaster
    # by 71 minutes otherwise.
    "O1": "Dark, and nobody alongside Torres Light. She drifts through the "
          "night with her recorder still aboard, and whoever reaches her "
          "first in the morning will read it.",
    "O2": "Kiwi 01 is at the end of her allocation with the coaster unnamed. "
          "Wellington's hours were spent and nothing came of them.",
    "O3": "The join point is empty at the end of the window. The Korean "
          "detachment turns back for Surabaya, and the fortnight was spent on "
          "the approach.",
    "O4": "The light went with the bladders still forty miles short. The Open "
          "Door flies on internal fuel and Prasetyo's strip is a runway with "
          "nothing on it.",
    "C2": "Stuart is still short of the line at first light with a Kilo "
          "somewhere astern, and the tug from Darwin has nothing to meet.",
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
    "09": "Eighty-five minutes and the group is still in the area. Whatever "
          "crossed the hose, COLLINS goes home the long way on what she has, "
          "and STALWART is still up here when the next Flanker pair comes.",
    "10": "The handover time passed. The cargo is still in the corridor and the "
          "Japanese detachment is out of allocation.",
    "11": "The transports never cleared the approaches. The talks open on "
          "Friday with the corridor closed.",
    "12": "Darwin's approaches are empty at the deadline. The first ship "
          "through did not get through.",
    "D1": "The group is still west of the line. The corridor plans around a "
          "tank that does not refill.",
    "D2": "The visit was waved off. The deck kept cycling, but the commander is still on the beach and somebody will write a "
          "report about the afternoon the carriers stopped flying.",
    "D3": "The beach window closed. The distribution point never opened and the "
          "request for help goes elsewhere.",
    "D4": "Nautical twilight, and the auxiliary is still in the corridor at six knots "
          "with every coalition sensor in the Banda looking for her.",
    "D5": "The serial ran out of range time with pads still standing. The "
          "trials report will say so at length.",
    "D6": (
        "The strike has failed. Account for the surviving package and report the launcher "
        "threats that remain."
    ),
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
    "02": (70, 12),
    "04": (-177, 12),
    "06": (-131, 12),
    "07": (-170, 20),
    "O3": (90, 12),
    "O4": (30, 8),
    "C2": (160, 10),
    "10": (139, 12),
    "11": (138, 12),
    "12": (-142, 12),
    "D1": (85, 12),
    "D4": (135, 12),
}

RESOLVERS = {
    "01": {"Convoy": "victory", "Neutrals": "neutral",
           "Warramunga": ("protect", "warramunga"),
           "Identify": ("classify", "meridian#1", 1)},
    "O1": {"Search": "victory", "Traffic": "neutral",
           "Restraint": ("spare", "meridian")},
    "O2": {"Picture": "victory", "Traffic": "neutral",
           "Kiwi": ("protect", "kiwi")},
    "O3": {"Shield": "victory", "Traffic": "neutral",
           "Stores": ("protect", "rok#3")},
    "O4": {"Fuel": "victory", "Town": "neutral",
           "Site": ("destroy", "site", 1)},
    "C2": {"Stuart": "victory", "Traffic": "neutral"},
    "02": {"Cargo": "victory", "Neutrals": "neutral",
           "Medical": ("protect", "convoy#1")},
    "C1": {"Survivors": "victory", "Assist": "neutral",
           "Contact": ("classify", "sub", 1)},
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
    # protect, not survive: the first loss fails the objective. "Do not
    # trade the Raptors" used to pay in full after losing one.
    "07": {"Tanker": "victory", "Package": ("protect", "package"),
           "Raptors": ("protect", "cap")},
    "08": {"Window": "victory", "Town": "neutral",
           "Battery": ("destroy", "battery", 2)},
    "09": {"Service": "victory", "Collins": ("protect", "support#2"),
           "Supply": ("protect", "support#1")},
    "10": {"Cargo": "victory", "Allies": ("protect", "jmsdf"),
           "Submarine": ("classify", "red_sub", 1)},
    "11": {"Transports": "victory", "Ford": ("protect", "carrier#1"),
           "Strike": ("destroy", "red_strike", 1)},
    "12": {"Convoy": "victory", "Ceasefire": "neutral",
           "Escorts": ("protect", "escort")},
    "D1": {"Oiler": "victory", "Escorts": ("protect", "escort"),
           "Shadow": ("destroy", "red_air", 2)},
    "D2": {"Visit": "victory", "Cycle": ("protect", "carriers"),
           "Tanker": ("protect", "air#2"), "Neutrals": "neutral"},
    "D3": {"Relief": "victory", "Town": "neutral",
           "Group": ("protect", "group"),
           "Lift": ("arrive", "lift", (-0.5, 128.0), 5, 1)},
    "D4": {"Auxiliary": "victory", "Cruiser": ("protect", "escort#1"),
           "Traffic": "neutral",
           # Scored on the text: destroy anything of the coalition's and the
           # objective fails. It used to be "not all five fighters lost".
           "Restraint": ("spare", "red_sag", "red_air")},
    "D5": {"Pads": "victory", "Safety": "neutral",
           "Serial": ("destroy", "target", 1),
           "Battery": ("protect", "battery")},
    "D6": {"Stream": "victory", "Escort": ("protect", "escort"),
           "Sensor": ("protect", "sensor")},
    "D7": {"Serial": "victory", "Recovery": ("protect", "high"),
           "Umpire": ("spare", "tanker")},
    "D8": {"Column": "victory", "Village": "neutral",
           "Gunship": ("protect", "support"),
           "Lift": ("arrive", "lift", (-8.38, 140.35), 3, 1)},
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
#        sells F-35s, Super Hornets, Growlers, P-8s, a Wedgetail and a Triton;
#        without a flight row and a matching mission slot, buying one
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
    ("01", "usn_mh-60r"): "HeloRecon", ("O1", "usn_mh-60r"): "HeloRecon",
    ("C1", "usn_mh-60r"): "HeloRecon",
    ("02", "usn_mh-60r"): "HeloRecon", ("02", "usn_p8"): "Recon",
    ("05", "raaf_f-35a"): "Attack",
    ("09", "usn_p8"): "Recon",
    ("10", "usn_p8"): "Recon",
    ("12", "usn_mh-60r"): "HeloRecon",
    ("04", "usn_mh-60r"): "HeloRecon", ("04", "usn_p8"): "Recon",
    ("05", "usn_mh-60r"): "HeloRecon",
    ("06", "raaf_f-35a"): "CAP", ("06", "E7A_Wedgetail"): "Recon",
    ("09", "usn_mh-60r"): "HeloRecon",
    ("11", "usn_f-35c"): "CAP", ("11", "usn_ea-18g_2020"): "Attack",
    ("12", "usn_p8"): "Recon", ("12", "raaf_f-35a"): "CAP",
}

# Aircraft the player is GIVEN for a mission, because an objective names them.
# `JoinTaskForce=True` with a `CampaignTag`: 04 Sunda Strait line 504, 08A
# Pathfinders line 531, four more in the shipped campaign. This is the native
# answer to "the mission depends on this exact aeroplane", and it is why SW06
# can make the Triton's survival the decision it is without the campaign
# having to sell the player a Triton first.
# JoinTaskForce is a GRANT: the guide says a surviving unit so tagged joins
# the player's roster at zero cost, as an unassigned air unit. Nothing in this
# campaign is meant to be given away - the P-8, the Triton, the Wedgetail,
# the CH-53s and the search helicopters are theatre contributions that fly
# the mission they are placed in - so no unit carries the tag. The reviewed
# build handed out six priced aircraft and two unpriced heavy-lift
# helicopters this way.
JOINS = set()



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
    "O2": "patrol", "O3": "escort", "O4": "logistics", "C2": "escort",
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
# purchased support asset that dies is gone from the owned force and has to be
# re-bought at its roster price: the Wedgetail 80 points, the P-8 55, the
# Triton 40, against mainline allocations of 100-200 per mission. That is a
# large share of a mission's income to replace one, and it is automatic.
# (Supply and the tankers are not on the roster: they are theatre assets.)
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
                intel=(
                    "AIR COMPONENT: Bluefin 21 confirmed lost. The Poseidon's local sensor "
                    "coverage is gone. Correlate available Triton, ship and shore reports; "
                    "expect gaps until another patrol can be assigned. - Ward"
                ))],
    "02": [dict(asset="HMAS Supply", units=["escort#3"],
                intel=(
                    "COMMAND: SUPPLY confirmed lost. Her support allocation is no longer "
                    "available. The next logistics plan must use the surviving ships and any "
                    "replacement command can release. - Mercer"
                )),
           dict(asset="Texaco 51", units=["air#2"],
                # Says what is true. It used to promise that sortie lengths
                # would shorten "from today", and nothing in the campaign
                # recorded the loss to make that happen.
                intel=(
                    "AIR COMPONENT: The tanker is lost. Its support for this operation has "
                    "ended. Reassess aircraft recovery and report remaining fuel; later "
                    "allocations will require a new plan. - Ward"
                ))],
    "06": [dict(asset="Sentry 06", units=["isr"], objective="Sentry",
                intel=(
                    "AIR COMPONENT: Sentry 06 confirmed lost. Its local surveillance "
                    "contribution has ended. Retain earlier reports with their observation "
                    "times and use surviving sensors to check them; command cannot promise an "
                    "immediate replacement. - Ward"
                ))],
    "12": [dict(asset="Wedgetail 03", units=["aew"],
                intel=(
                    "AIR COMPONENT: Wedgetail 03 confirmed lost. The allocated "
                    "air-surveillance detachment has lost one of its aircraft. Use the "
                    "surviving sensors to maintain the final convoy's warning picture. - Ward"
                ))],
}

for _m in MISSIONS:
    _loss = SUPPORT_LOSS.get(_m["num"])
    if _loss:
        _m["support_loss"] = _loss

# A mission with no builder says so on its card: the reviewed build let four
# operations pass between windows without a word to the player.
for _m in MISSIONS:
    _w = _m.get("window", {})
    if _m["group"] == "core" and "special" not in _m:
        if _m["num"] in ("04", "06", "10"):
            _m["special"] = ((
                "No additional force allocation before this operation: use the ships and "
                "aircraft already allocated."
            ))
        elif _m["num"] in ("07", "08"):
            _m["special"] = ((
                "No additional force allocation, and your standing task group remains on other "
                "duties: this operation is flown with the aircraft allocated to it."
            ))

# The convoy and replenishment operations sail with everything: the player may
# not leave the auxiliary at home to keep it safe. The strike and side missions
# let the player pick a detachment.
for _m in MISSIONS:
    if _m["num"] in ("03",) or _m["group"] == "dispatch":
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
    # Holding the service window is what Common Sea's rearm is paid with -
    # the guide's TaskForceModeRearmByVariableAND, IsTrue.
    "09": dict(declares=["SW09ServiceHeld"]),
    # The optional operations' results, read by the core missions below.
    "O2": dict(declares=["O2KiwiPicture"]),
    "O3": dict(declares=["O3ShieldJoined"]),
    "O4": dict(declares=["O4LanggurStocked"]),
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
        # The Missing Beacon's promise, kept: get alongside Torres Light
        # before Meridian does and her bridge recorder puts the boat on this
        # plot as a classified contact from the first minute.
        _m["reveal_if"] = [dict(
            variable="O1BeaconFound", units=["sub"], level="Classify",
            intel=(
                "ASW CELL: Torres Light's recovered bridge record matches the submarine report "
                "on this route. The contact is classified on the plot and held there for the "
                "operation. Engage it under the current orders."
            ))]
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
            intel=(
                "FUSION CELL / SENTRY 06: The escorts appear to be screening an air route. An "
                "unidentified heavy transport is running north towards the Biak enclave. Extend"
                " the search only if the Triton can do so safely; the convoy remains the "
                "priority."
            ))]
    if _m["num"] == "04":
        # Southern Cross, kept: Kiwi 01's picture puts the boat on this plot.
        _m["reveal_if"] = [dict(
            variable="O2KiwiPicture", units=["sub"], level="Classify",
            intel=(
                "ASW CELL: Kiwi 01's earlier report links MV Harbour Light to a submarine "
                "working this route. That contact, the Type 039, is classified on the plot and "
                "held there for the operation. It is not the passenger."
            ))]
    if _m["num"] == "06":
        # Borrowed Shield, kept: the Korean destroyer stands in the screen.
        _m["stations"]["shield"] = S(-10.55, 132.05, "Korean destroyer",
                                     heading=250)
        _m["units"].append(U("blue", "euromod-south-korea", "ko_ddg-991",
                             "shield", variant="Variant1",
                             name="ROKS Sejong the Great",
                             spawn_if=("O3ShieldJoined", "IsTrue")))
    if _m["num"] == "08":
        # Weather Alternate, kept: a tanker on the track south of the box.
        _m["stations"]["tanker"] = S(-3.9, 134.3, "Tanker track", heading=90,
                                     alt=26000)
        _m["units"].append(U("blue", "kc-46a", "usaf_kc-46a_boom", "tanker",
                             name="Texaco 52", alt=26000, weapons="Hold",
                             spawn_if=("O4LanggurStocked", "IsTrue")))
    if _m["num"] == "09":
        # The second replenishment hull only exists if SUPPLY came through
        # chapter 1. Lose her at Steel Highway and the rear-area group is one
        # ship thinner for the service window that matters.
        for _u in _m["units"]:
            if _u["type"] == "civ_ms_amra":
                _u["spawn_if"] = ("SW02SupplyLost", "IsFalse")
    if _m["num"] == "11":
        _m["flags"] = [dict(name="SW11FujianSunk", units=["red_cv#1"],
                            intel=(
                                "DAMAGE REPORT: FUJIAN confirmed lost. Its contribution to the"
                                " next interception has been removed from the threat "
                                "assessment. Liaoning's status and any remaining aircraft must "
                                "be established separately."
                            ))]
        _m["reveal_if"] = [dict(
            variable="SW06NorthernGroupClassified",
            units=["red_cv#3", "red_cv#4", "red_cv#5"], level="Identify",
            intel=(
                "FUSION CELL: Earlier Sentry 06 reporting has been correlated with the present"
                " escort screen. The identified escorts are on the plot and held there for the "
                "operation. The carriers are not; use current sensors to establish their "
                "positions."
            ))]
    if _m["num"] == "12":
        # Sink the carrier at Fujian's Shadow and the spoiler group has no air
        # cover on the last morning.
        for _u in _m["units"]:
            if _u["station"] == "spoiler_air":
                _u["spawn_if"] = ("SW11FujianSunk", "IsFalse")
