"""Reviewed additions to the existing SEST mission set.

Reports are advice from named characters, never invented detections. Support
boats are authored for one operation, not sold into the unsupported submarine
roster. Forward UAV sections use finite fuel and an explicit recovery strip.
No enrichment replaces an existing main objective or civilian protection rule.
"""
import collections
from copy import deepcopy
import math
import re


# Red Line's reports speak as roles, never names: its bible names no person
# on the Chinese side, and until 20 Oct 2026 these gave the carrier's captain
# and the group's political officer surnames, put a ceasefire on 12 November
# (it is the 27th) and had a nuclear boat snorkel. Sulu Line's three are
# signed MANALO: Southern Watch's Master Leila Santos had the name first.
REPORTS = {
    "SWD9": "ELLIS: Confirm the UAV's own camera or sensor contact before correcting the guns. The two enemy models are different batteries; count their outgoing fire separately from your own impacts.",
    "SWD10": "RANGE CONTROL: Clear run. Target sensors are disabled. Record the offered launch solution before switching any test shooter to Free. Restart before comparing a different weapon against the same geometry.",
    "SWD11": "RANGE CONTROL: Contested run. Target sensors operate normally; this restores their available radar and jamming systems. Compare with Clear using the same shooter, target, altitude, aspect and elapsed time.",
    "SW01": "PRASETYO: An escort contract is not permission to board. Establish which boat is issuing the orders before opening fire. The convoy masters are listening to your challenge.",
    "SW02": "KILA: Keep a helicopter over the slow end of the convoy. A submarine contact is a reason to shift the screen, not scatter four unescorted merchants. Supply's survival matters after this passage.",
    "SW03": "RIG CONTROL / ELLIS: The last shift is on the helideck. Cover the lifters' return route as well as their approach; a rocket attack on an empty platform still kills the people waiting for the second lift.",
    "SW04": "PRASETYO: Harbour Light's papers and the underwater contact are different investigations. Keep somebody with the passenger while the flight checks the datum. A radar return alone does not establish intent.",
    "SW05": "MERCER: One ship can hold the merchant lane while another works the shooters. Do not let a pursuit of a missile boat leave the transport group uncovered.",
    "SW06": "WARD: An emission bearing is a line, not a ship. Extend the picture with the Triton while the surface screen stays with the convoy. Record the observation time before chasing the next transmission.",
    "SW07": "TEXACO 41: The queue is real, the fuel is finite, and the north side of my orbit is not a fighter sweep. Break their firing solution and leave an escort with the tanker.",
    "SW08": "ROURKE / DOOM: The military runway and dispersal are separate aimpoints. Launch the opening ARRWs early, then assess. Another salvo into a civilian shelter will not buy the relief aircraft another minute.",
    "SW09": "KILA: Put a surface screen between the hose and the corvette. VICTOR remains the flight's problem. At the service signal, give both ships their withdrawal orders; Collins will not dive herself for the story.",
    "SW10": "ARAI: Keep the Japanese screen connected to the convoy picture. Sharing a bearing does not mean sharing a positive identification. The submarine and the aircraft must be solved at the same time.",
    "SW11": "MERCER: Your submarine has a separate patrol box. Do not drive the surface screen through it. The carrier engagement, underwater screen and troop transports are three simultaneous jobs.",
    "SW12": "PRASETYO: The ceasefire has a time and a signature. Neither tells you which individual contact will obey it. Keep a defensive screen with the first merchant through and challenge before you shoot.",
    "SWO1": "BEACON DESK / ELLIS: A broken beacon is not a hostile classification. Search from the last reliable report and keep your ship's flight available for the recovery, not a speculative attack.",
    "SWC1": "MERCER: Rescue and investigation share the same water. Keep the survivor search protected while the sonar team works the older contact. A datum becomes less useful every minute it is unobserved.",
    "SWO2": "REWI / KIWI: I can lay a barrier or follow a contact; I cannot do both everywhere at once. Hold your patrol ship clear of the sonobuoy field and tell me which question you need answered first.",
    "SWO3": "HAN: The Korean ships join as a screen, not a replacement convoy. Protect their stores ship and bring both warships to the rendezvous. Seoul has not promised a second detachment.",
    "SWO4": "LANGGUR / PRASETYO: Keep the coasters on the western offshore route. Local launches will take the bladders ashore. The UAV section is looking at the launch site, not clearing the island passages for a merchant.",
    "SWC2": "ENGINE ROOM: A straggler is a second defended point. Put the flight or a detached escort between her and the incoming axis before moving the rest of the force away.",
    "SWO5": "FUSION CELL / ELLIS: The small surface scouts can hold a second bearing while the patrol ship stays back. Keep the suspect merchant under observation; a radio handover is more useful than a wreck.",
    "SWO6": "PRASETYO: An armed merchant and a neutral merchant can share a silhouette. Classify the hulls before allocating missiles, and reserve something for the craft trying to draw your fire away from the cargo.",
    "SWO7": "WARD: Four internal-JSM Lightnings, two radar aimpoints. Check the surviving airfield support before committing the package. The new mobile belt is not proof that yesterday's runway has repaired itself.",
    "SWO8": "AIR CONTROL: A bomber's turn is not necessarily its launch cue. Keep a fighter pair with the protected anchorage while the other pair works the stream. The airliner is still neutral.",
    "SWO9": "ARAI / VIPER: Use the EC-2's picture to split the surface group, then identify each aimpoint. Hyuga's helicopter is also a recovery asset; do not spend it as a fighter scout.",
    "SWO10": "LANGGUR / ELLIS: The RQ-7 team is on friendly Yapen, south of the Biak enclave. Work the southern approach, confirm launchers and optional support sites, and recover before fuel runs short. Moth has no protection against a live SAM belt.",
    "SWD1": "LIAISON / ELLIS: The borrowed escorts bring different sensors and magazines. Assign sectors and recovery duties before chasing the first electronic-warfare aircraft. The oiler remains the reason for the passage.",
    "SWD2": "DECK CONTROL: A clean launch is half the serial. Stagger the recoveries, watch the maintenance queue, and keep a rescue helicopter available. Someone has written SEND THE NEXT ONE inside the launch folder.",
    "SWD3": "RELIEF COORDINATOR: Work the road approaches with reconnaissance before committing the lift. A vehicle near the landing area is a contact to classify, not permission to shell the town.",
    "SWD4": "EXERCISE CONTROL: The opposing side knows the same Australian equipment you do. Vary the formation and emission plan; keep the supported ship covered while the air picture draws attention away.",
    "SWD5": "RANGE SAFETY: Check altitude floors as well as the displayed maximum range. The small UAV can inspect a pad; it is not a ballistic-missile warning system. Separate a missed detection from a missed intercept.",
    "SWD6": "FUTURE FRONT CONTROL: This is the labelled speculative branch. Separate a missile's paper range from a launch solution against a small manoeuvring aircraft. Keep a record of target height, aspect and jamming.",
    "SWD7": "EXERCISE 1988: The range staff have put a paper red spider on the plotting table. The crews have no modern datalink to explain it. Work the bearings and protect the ships with the equipment actually here.",
    "SWD8": "BORDER LIAISON: The new UAV section can inspect the ridge and vehicle park. Keep the reconnaissance track clear of your own strike line and remember that a quiet radar can still come back on.",
    "SR01": "KILA: The southbound ships do not all turn or accelerate together. Give the last merchant a screen and keep the Okean's bearing separate from the frigate's identification.",
    "SR02": "REWI: Collins and the Poseidon should solve the same contact from different sides. Keep the weapons held; our task is a classification and an exit, not a demonstration shot.",
    "SR03": "ELLIS / SEARCH DESK: Split the surface search and helicopter datum work. A trawler near the search area may have seen something; its presence is not proof it caused the loss.",
    "SR04": "STALWART: A replenishment track needs room on both sides. Leave a ship watching the submarine approach while the receiving group closes. Weather will spend the margin faster than the quartermaster expects.",
    "SR05": "WARD: Let the unarmed aircraft establish identities at different angles. A fisheries label is a claim, not a contact class. Bring the Triton home with its recording.",
    "SR06": "KILA: The submarine detachment watches the outer approach while your convoy escort stays close. Its weapons are held until you decide; a second blue hull under water does not classify VICTOR for you.",
    "SR07": "REWI: Buoy patterns age in this weather. Keep a fresh barrier on the convoy's intended track rather than all your sensors over the last datum.",
    "SR08": "GATEWAY CONTROL: One escort with the arriving ship, one sensor looking ahead if available. Do not let the helicopter chase the trawler until the coastal approach is covered.",
    "SR09": "MERCER: The submarine supports the ocean flank. Keep the carrier's aircraft, its escorts and the convoy as separate plots; a turn towards one need not expose the convoy to the other.",
    "SR10": "WARD: This is reconnaissance under a threat envelope. Use the smallest number of emissions needed for a classification and keep a recovery margin for the patrol aircraft.",
    "SR11": "KILA: The final ship south is the slow reference point. An escort chasing the northern contact still has to get back before the convoy meets the next one.",
    "SR12": "MERCER: Record which hulls leave with the carrier and which remain. A withdrawing group can still support a later operation; damage reports need names, not just a count of symbols.",
    "TS01": "COASTWATCH: Home waters have civil traffic on familiar schedules. Familiar does not mean harmless, and an unfamiliar course does not make a merchant a target. Build the picture before closing.",
    "TS02": "CABLE CONTROL: The workboat cannot evade like an escort. Keep the helicopter watching the next patch of water while the surface ship holds the cable corridor.",
    "TS03": "CHATHAM WATCH: The merchant and the submarine report are separate problems. Put the flight where it can discriminate between them; the patrol ship should not abandon its identification task.",
    "TS04": "KILA: Two merchant groups need two defended bearings. The submarine covers the ocean approach, leaving your surface choices free to screen the groups instead of chasing the carrier.",
    "TS05": "FARNCOMB: The towed-array ship is not the contact it is hunting. Stay outside the active search axis and decide whether a classification is worth giving away your own position.",
    "TS06": "TRAFFIC CONTROL: A decoy emitter can make the tanker look like the wrong centre of the battle. Verify the hull, then shift the screen; do not pursue an antenna away from the protected ship.",
    "TS07": "AIR BRIDGE: Keep a fighter pair near the protected corridor if you have one. The carrier's jammer is useful to find, but an interceptor chasing it may leave the transport axis open.",
    "TS08": "COLLINS: We will work the underwater approach while the escort keeps the surface picture. Pass your intended course before dropping active buoys into the same water.",
    "TS09": "MERCER: Three axes compete for your sensors: the carrier group, the submarine screen and the convoy route. The supporting submarine begins outside the merchant lane. Keep it there until the plot is reconciled.",
    "TS10A": "NORTHERN DESK: The trader's survival is the immediate task. The northern choice costs time on the other approach; do not spend the whole window pursuing a ship that is already leaving.",
    "TS10B": "SOUTHERN DESK: The tanker gives you a defended point, the submarine gives you a search. Hold enough of the screen back to do both while the northern route waits.",
    "TS11": "KILA: The lift ships are not a spare missile magazine. Keep them behind the defensive screen and use the submarine's separate box to watch the flank your surface sensors cannot hold.",
    "TS11A": "LIAISON: The defector has made a choice; the pursuing group may not accept it. Keep her identified and covered. A blue-painted symbol does not erase the need for a safe weapons sector.",
    "TS12": "PRASETYO: Southern Cross is a passage, not a victory parade. Challenge the contacts in the convoy lane and keep a recovery ship ready. The old red-spider card is now pinned beside the departure board.",
    "RL01": "FUJIAN / ASW: Classify the trailing boat without turning the carrier towards it. The coalition aircraft are recording our search as carefully as we record theirs.",
    "RL02": "GROUP STAFF: Hai Yang 7 carries the detachment's fuel. A submarine report is not permission to attack the aircraft recording the route; it attacks nothing. Keep the tanker moving.",
    "RL03": "AIR OPERATIONS: A second look from another bearing is worth more than a closer pass by one aircraft. Record the convoy screen without giving the coalition the escalation it expects.",
    "RL04": "GROUP STAFF: The withdrawal order applies to the impatient ship as well as the carrier. Interpose, challenge and protect the charter. Do not let one ship's captain write the next campaign.",
    "RL05": "BOAT CONTROL: Silence is a resource. A burst of speed or an avoidable turn near a buoy can spend the same concealment as a transmission. Keep the exit plan separate from the temptation to investigate.",
    "RL06": "TENDER CONTROL: The screen and the boat have different jobs. Keep the decoy station loud and credible while the tender and the boat close quietly; Kiwi 05 needs only one useful pass.",
    "RLO1": "AIR OPERATIONS: A class is a buoy pattern and patience. Lay the field ahead of her drift, keep the aircraft off the Poseidon's track, and log what the buoys hear for the escort tomorrow night.",
    "RLO2": "AIR OPERATIONS: Classify from the edge of their radar, not the middle of it. The fighters from Langgur are there to be seen seeing us off; keep ours between them and the Y-9, and keep both at Tight.",
    "RLC1": "SEA BOAT: The beacon is the datum. Run straight at it, put the flight overhead to mark him, and stop the ship upwind of the raft. Do not cross the patrol vessel's bow; she has the same right to be there that we do.",
    "SL01": "MANALO: Keep a gun ship between the ferry lane and the fast craft. Your magazines will not refill at the debrief; leave enough for the next passage or bring the supply ship.",
    "SL01A": "MARKET WATCH: Follow the semi-submersible while the patrol craft cover its exits. The helicopter over the boats may be the lookout, not the cargo. Classify before crossing fire through local traffic.",
    "SL02": "MARINE LIAISON / VEGA: The forward UAV can distinguish the launchers from vehicles on the ridge. Give the gunline a current target report, then move it before answering every radio call.",
    "SL03": "AYUNGIN CONTROL: Our resupply boat needs room to pass, not a naval battle. Keep weapons held and watch the militia's courses. The cameras are part of this engagement.",
    "SL03A": "VEGA: Do not let the trawler's torpedo threat bring both patrol boats onto the same line. Keep a cross-bearing and enough separation to cover the speedboats.",
    "SL04": "SUPPLY CONTROL: Choose which magazines need the next transfer before closing the charter. A threat at the edge of the box does not make the ship alongside any less vulnerable.",
    "SL05": "MANALO: The gun-runner and its scouts are one network. Stop the cargo without shooting through the wrong merchant, and keep the flight watching the boat's intended escape route.",
    "SL05A": "VEGA / SHORE TEAM: Compare Tabak's first strike with a fresh observation pass. Mobile launchers do not owe you a second shot at yesterday's coordinate. Mapun has no friendly recovery strip; preserve the strike aircraft's fuel margin.",
    "SL06": "FIRE CONTROL: Silence the coastal battery without losing the convoy while you turn for a firing solution. The forward UAV's camera can check the radar and launchers separately.",
    "SL07": "MANALO: The patrol submarine is a coalition attachment for this battle only. Keep her clear of the convoy and your ASW weapons. The ships still have only the ammunition you brought or transferred at sea.",
}

# code: (friendly recovery location, target station). The forward sites are
# fictional coalition sections on actual land, checked by the normal placer.
UAV_SITES = {
    "SW03": ((-8.49, 126.40), "shore"),
    "SW08": ((-0.80, 135.60), "field"),
    "SWO4": ((-5.6614, 132.7314), "site"),
    "SWD3": ((-0.78, 127.38), "road"),
    "SWD5": ((-14.521, 132.378), "pads"),
    "SWD6": ((-0.90, 131.30), "complex"),
    "SWD8": ((-8.60, 140.70), "ridge"),
    "SWO7": ((-0.80, 135.60), "s350"),
    "SWO10": ((-1.72, 135.96), "pads"),
    "SL02": ((6.09, 121.30), "ridge"),
    "SL06": ((9.53, 118.62), "battery"),
}

# Blue boats have their own station, no inherited surface formation. The
# names have not appeared as losses earlier in these campaigns.
SUB_SUPPORT = {
    "SW11": ("us-navy-2027", "usn_ssn_virginia_2027", "US submarine support", (-5.50, 130.70)),
    "SR06": ("SEST_RAN_Fleet", "ran_ssg_collins", "HMAS Rankin", (-51.90, 164.60)),
    "SR09": ("SEST_RAN_Fleet", "ran_ssg_collins", "HMAS Rankin", (-48.90, 137.30)),
    "TS04": ("SEST_RAN_Fleet", "ran_ssg_collins", "HMAS Dechaineux", (-38.80, 158.20)),
    "TS09": ("SEST_RAN_Fleet", "ran_ssg_collins", "HMAS Sheean", (-38.50, 140.60)),
    "TS11": ("us-navy-2027", "usn_ssn_virginia_2027", "US submarine support", (-39.85, 150.30)),
    "SL07": ("SEST_RAN_Fleet", "ran_ssg_collins", "HMAS Dechaineux", (8.20, 117.20)),
}


def code_of(m):
    return m.get("code", "SW" + m["num"])


def add_uav(m, code, U, S):
    base, target = UAV_SITES[code]
    at = m["stations"][target]["at"]
    # Start halfway between the strip and the target with a short oblique
    # orbit. It sees what its own sensors see, not a scripted target reveal.
    centre = ((base[0] + at[0]) / 2, (base[1] + at[1]) / 2)
    m["stations"]["uav_strip"] = dict(S(*base, "Forward UAV field team"), coastal=True)
    m["stations"]["uav_scout"] = S(*centre, "Moth reconnaissance UAV", 90, 3000)
    m["units"].append(U("blue", "SEST_Allied_Fixes", "sest_uav_forward", "uav_strip",
        name="Forward UAV team", nation=m["blue_nation"], weapons="Hold",
        air_group=[("usn_rq7705", "Squadron1", 2)]))
    m["units"].append(U("blue", "small-medium-uav-series", "usn_rq7705", "uav_scout",
        name="Moth 11", squadron="Squadron1", nation=m["blue_nation"], weapons="Hold",
        alt=3000, enter=10, route=[(centre[0] - .04, centre[1] - .04, 3000),
                         (centre[0] + .04, centre[1] + .04, 3000)], loop=True))
    # Optional credit for fresh reconnaissance; any surviving sensor can do
    # the job if Moth is lost. Main task and failure rules stay unchanged.
    m["objectives"].append(("ForwardRecon", "Obtain a current classification of the land target area", "5,0,None"))
    m.setdefault("resolve", {})["ForwardRecon"] = ("classify", target, 1)
    location = ("The field team is on friendly Yapen, south of hostile Biak, with a portable launcher and recovery lane; no friendly airfield has been established inside the enclave. "
                if code == "SWO10" else "The field team uses a portable launcher and local recovery lane. ")
    m["brief"] += ("\\n\\nFORWARD RECON: MOTH 11, a small RQ-7 reconnaissance UAV, joins over the local approach at minute ten, allowing time for initial air-defence suppression. " + location + "Two reserve UAVs are with the team from the start. They are unarmed and have finite fuel. Use their sensors to classify the military installations and update strike aimpoints. The small airframes are vulnerable; no scripted reveal grants a target solution. Keep a recovery margin and reposition the initial track as needed.")
    m["forces"] += " Forward RQ-7 field team: two reserve UAVs and a portable launcher; Moth 11 joins at minute ten."


def add_sub(m, code, U, S):
    mod, uid, name, at = SUB_SUPPORT[code]
    m["stations"]["sub_support"] = S(*at, "Independent submarine patrol box", 90)
    # A slow, quiet start gives the player time to deconflict its patrol.
    boat = U("blue", mod, uid, "sub_support", name=name, weapons="Hold",
        depth="belowlayer", telegraph=2, independent=True,
        route=[(at[0], at[1] + .12, "belowlayer")])
    if uid == "ran_ssg_collins":
        boat["variant"] = {"HMAS Rankin": "Variant6", "HMAS Dechaineux": "Variant4", "HMAS Sheean": "Variant5"}[name]
    if code == "SR06":
        m.setdefault("declares", []).append("SR06RankinLost")
        m.setdefault("flags", []).append(dict(name="SR06RankinLost", units=["sub_support"],
            intel="SUBMARINE CONTROL: Rankin is lost. Her attachment will be unavailable at Cold Route."))
    if code == "SR09":
        boat["spawn_if"] = ("SR06RankinLost", "IsFalse")
    m["units"].append(boat)
    m["brief"] += (f"\\n\\nSUBMARINE ATTACHMENT: {name} is allocated to this operation in an independent patrol box, submerged with weapons held. You command the boat. Deconflict its movements from the convoy and your ASW weapons before releasing it to engage. It is an authored theatre attachment for this operation, not a purchased hull carried into every later battle.")
    m["forces"] += f" Independent submarine attachment: {name}, weapons held initially."
    if code == "SR09":
        m["brief"] += " Rankin is available only if she survived Broken Supply Line; a lost boat is not replaced for this battle."


EXTRA_CONTACTS = {
    "SW02": ("sub", "red-storm-arsenal", "ir_ptg_peykaap_3", "Meridian Escort 12", 18, "A later missile-boat approach adds a surface threat while the flight works the submarine datum."),
    "SW05": ("red_air", "small-medium-uav-series", "usn_Mugin5705", "Meridian Mugin spotter", 12, "A small Mugin reconnaissance UAV joins the strike axis after twelve minutes; it is a scout, not another bomber."),
    "SR07": ("red_sub", "russian-navy-21", "rfn_cvt_20380_7-12", "Russian corvette 312", 18, "A light Russian corvette joins the outer approach after eighteen minutes. Keep surface cover while searching the underwater datum."),
    "TS03": ("red_sub", "modern-plan-systems", "plan_z-9c", "Hunter 52", 15, "A Z-9C submarine-search helicopter joins after fifteen minutes, adding an active sensor to the merchant and submarine puzzle."),
    "SL04": ("raiders", "armed-merchantmen", "civ_fv_okean_armed", "Meridian Tender 9", 22, "An armed trawler joins the threat approach after twenty-two minutes, separate from the three fast craft. Keep the charter protected during transfers."),
}


def add_contact(m, code, U):
    station, mod, uid, name, minute, detail = EXTRA_CONTACTS[code]
    # These are existing, validated approach stations. A separate station
    # prevents a delayed unit from inheriting an active formation leader.
    key = "later_contact"
    m["stations"][key] = deepcopy(m["stations"][station])
    opts = dict(name=name, enter=minute)
    if uid in ("usn_Mugin5705", "plan_z-9c"):
        opts.update(alt=2500, weapons="Hold")
        la, lo = m["stations"][station]["at"]
        # A short sweep towards the player's screen, then a local loop; it
        # is a working sensor instead of an aircraft circling its spawn.
        own = m["stations"][m.get("anchor") or next(u["station"] for u in m["units"] if u["side"] == "blue")]["at"]
        mid = ((la + own[0]) / 2, (lo + own[1]) / 2)
        opts.update(route=[(*mid, 2500), (la, lo, 2500)], loop=True)
    else:
        # Follow the existing validated surface approach when it has one.
        lead = next((u for u in m["units"] if u["side"] == "red" and u["station"] == station and u.get("route")), None)
        if lead and all(isinstance(p[2], (int, float)) and p[2] == 0 for p in lead["route"]):
            opts.update(route=deepcopy(lead["route"]), telegraph=3)
    m["units"].append(U("red", mod, uid, key, **opts))
    m["brief"] += "\\n\\nFOLLOW-ON CONTACT: " + detail
    m["forces"] += " " + detail


def _navy(entry):
    """The navy an allied entry belongs to, from allied_fleet's note
    ("United Kingdom - Type 23 class (LIFEX)")."""
    navy, sep, _cls = entry.get("note", "").partition(" - ")
    if not sep:
        raise SystemExit(f"{entry['unit']}: an allied entry's note must open with "
                         "its navy (\"United Kingdom - Type 23 class\")")
    return navy


def _class(entry):
    """The class an allied entry names, from the same note."""
    return entry["note"].partition(" - ")[2]


def _names(items):
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


# The navies whose names take an article in a sentence ("from the USA").
_THE = {"USA", "United Kingdom", "Netherlands"}


def _commander(spec, key):
    """CommanderNations or NavyName<nation> from the spec's commander file."""
    m = re.search(rf"^{key}\w*=(.+)$", spec.get("COMMANDER", ""), re.M)
    return m.group(1).strip() if m else ""


def is_aircraft(entry):
    """An entry sold by squadron is an aircraft; a hull is sold by variant.
    That is roster_ini's rule, and build_pack re-checks it against the unit's
    own file before an aircraft is judged (admit_reserve_aircraft)."""
    return bool(entry["picks"]) and all(p.startswith("Squadron") for p in entry["picks"])


def reserve_phrase(spec, units):
    """The reserve's `units`, in words: the allied fleet counted by ships and
    aircraft and named by navy, most classes first, and any of the
    commander's own navy's classes by name. A window and the rules page say
    it this way; sixty classes cannot be listed one by one (21 Oct 2026)."""
    priced = {e["unit"]: e for e in spec["ROSTER"]}
    entries = [priced[u] for u in units]
    nation = _commander(spec, "CommanderNations")
    allied = [e for e in entries if _navy(e) != nation]
    own = [e for e in entries if _navy(e) == nation]
    parts = []
    if allied:
        air = sum(1 for e in allied if is_aircraft(e))
        ships = len(allied) - air
        what = [f"{ships} ship class{'es' if ships != 1 else ''}"] if ships else []
        what += [f"{air} aircraft type{'s' if air != 1 else ''}"] if air else []
        count = collections.Counter(_navy(e) for e in allied)
        navies = [("the " if n in _THE else "") + n
                  for n, _c in sorted(count.items(), key=lambda x: (-x[1], x[0]))]
        parts.append(f"the allied fleet - {_names(what)} from {_names(navies)} -"
                     if own else f"the allied fleet, {_names(what)} from {_names(navies)}")
    if own:
        parts.append(f"the {_commander(spec, 'NavyName')}'s "
                     + _names([_class(e) for e in own]))
    return " and ".join(parts)


def reserve_offer(spec):
    """[(mission, units)] - each reserve opening, earliest first: the mission
    whose force-allocation window first sells them, and the reserve units it
    opens, in roster order. Only what the roster sells: a unit left out
    (RESERVE_LEFT_OUT) or an aircraft not yet judged sells nothing."""
    by_code = {code_of(m): m for m in spec["MISSIONS"]}
    opens = spec.get("RESERVE_OPENS", {})
    opening = collections.defaultdict(list)
    for e in spec["ROSTER"]:
        if e["unit"] in opens:
            opening[opens[e["unit"]]].append(e["unit"])
    return [(by_code[code], units)
            for code, units in sorted(opening.items(), key=lambda kv: _when(by_code[kv[0]]))]


def _when(m):
    return (m["date"], m.get("time") or (0, 0))


def _open_windows(spec, units):
    """Put `units` (reserve units on the roster) on sale at every buy window
    from each one's opening. A new list, never extended in place:
    campaign_data's windows share theirs (BUY_03 is BUY_02, BUY_09 is
    BUY_07), and one extended would open the reserve a window early. Adding
    only what is missing makes a second call change nothing."""
    by_code = {code_of(m): m for m in spec["MISSIONS"]}
    opens = spec["RESERVE_OPENS"]
    for m in spec["MISSIONS"]:
        w = m.get("window", {})
        if not w.get("buy"):
            continue
        selling = [u for u in units if _when(m) >= _when(by_code[opens[u]])]
        if w.get("allow") and any(u not in w["allow"] for u in selling):
            w["allow"] = w["allow"] + [u for u in selling if u not in w["allow"]]


def apply_reserve(specs):
    """The allied reserve: what a standard campaign sells beside its own
    navy, each class from a window its story names.

    A spec names it two ways, and may use both: RESERVE, a list of
    dict(unit, opens=<mission code>), for chosen classes of the fleet its
    commander calls on (spec ALLIED_FLEET, allied_fleet.FOR_NATION by
    commander nation); and RESERVE_FLEET=dict(opens=<mission code>) for the
    rest of that fleet, every class. Windows are keyed by mission code, not
    window number, because Southern Reach's two chapters repeat window
    numbers.

    It replaced expand_roster on 20 Oct 2026, which sold Type 23, Mogami and
    Daegu at every window but Southern Watch's first three, as a set
    hard-coded here. The owner's decisions of that day sold escorts only:
    eleven classes in Southern Watch from Weapons Free, three in Southern
    Reach from Tasman Crossing (Q2 and Q3). On 21 Oct, retiring the Open
    Allocation twins, the owner put what the twins sold in the standard
    campaigns from those same windows: the whole allied fleet - carriers,
    amphibious and replenishment ships and allied aircraft with the escorts
    - and in Red Line, whose commander calls on no allies, the PLAN's own
    Type 901 and 903A from the first force allocation. Earlier windows keep
    the story's own lists.

    Each entry, price and note is allied_fleet's. A hull any mission of any
    campaign places is never sold, and an entry left with none is set aside
    with the reason (spec RESERVE_LEFT_OUT) rather than stopping the build:
    the twins sold HMAS Choules and the Supply-class AOR, and every hull of
    both sails in a Southern Watch or Southern Reach mission. Ships go on
    the roster and on sale here. Aircraft are held (spec RESERVE_AIR): only
    the built missions say whether a row launches and recovers one, so
    build_pack's main() judges them after placement (usable_allied) and
    hands what passes to admit_aircraft(). say_reserve() then writes each
    window's sentence from what the roster sells. RESERVE_OPENS maps every
    reserve unit to its opening.

    Every reserve unit leaves ALLIED_FLEET, so an Open Allocation twin, for
    a campaign that opts in to one (none in the pack since 21 Oct 2026),
    sells it once, from the roster. Repeated campaign_specs() calls change
    nothing: a spec dict already resolved is skipped, and the module lists
    a fresh one shares (ROSTER, the windows) already carry the reserve.
    """
    # A placed variant is a named ship - JS Mogami in Common Sea and The
    # Other Picture, Daegu in O3 - and a hull the player could also buy
    # would sail twice. Until 20 Oct only the campaign's own blue units were
    # looked at, and Southern Reach sold both those hulls. Every campaign's,
    # on any side; not dispatches, which no campaign loads.
    placed = {(u["type"], u.get("variant", "Variant1"))
              for spec in specs for m in spec.get("MISSIONS", [])
              if m["group"] != "dispatch" for u in m["units"]}
    for spec in specs:
        if "MISSIONS" not in spec or "RESERVE_OPENS" in spec:
            continue
        named = list(spec.get("RESERVE", []))
        whole = spec.get("RESERVE_FLEET")
        if not named and not whole:
            continue
        by_code = {code_of(m): m for m in spec["MISSIONS"]}
        fleet = {e["unit"]: e for e in spec.get("ALLIED_FLEET", [])}
        on_roster = {e["unit"] for e in spec["ROSTER"]}
        reserve = named + ([dict(unit=e["unit"], opens=whole["opens"])
                            for e in spec.get("ALLIED_FLEET", [])
                            if e["unit"] not in {r["unit"] for r in named}]
                           if whole else [])
        opens, held, left_out = {}, [], []
        for r in reserve:
            if r["opens"] not in by_code:
                raise SystemExit(f"{spec['TITLE']}: the reserve's {r['unit']} opens at "
                                 f"{r['opens']}, which is not one of its missions")
            opens[r["unit"]] = r["opens"]
            # Already on the roster after a repeated campaign_specs() call:
            # the module's own ROSTER list carries it from the first.
            if r["unit"] in on_roster:
                continue
            if r["unit"] not in fleet:
                raise SystemExit(f"{spec['TITLE']}: the reserve's {r['unit']} is not in "
                                 "the allied fleet its commander calls on (allied_fleet.py)")
            e = deepcopy(fleet[r["unit"]])
            aircraft = is_aircraft(e)
            e["picks"] = [p for p in e["picks"] if (e["unit"], p) not in placed]
            if not e["picks"]:
                left_out.append((e, "every hull it prices is placed by a mission"))
            elif aircraft:
                held.append(e)
            else:
                spec["ROSTER"].append(e)
        spec["RESERVE_OPENS"] = opens
        spec["RESERVE_AIR"] = held
        spec["RESERVE_LEFT_OUT"] = left_out
        spec["ALLIED_FLEET"] = [e for e in spec.get("ALLIED_FLEET", [])
                                if e["unit"] not in opens]
        latest = max((_when(by_code[code]) for code in opens.values()), default=None)
        for m in spec["MISSIONS"]:
            w = m.get("window", {})
            # An open builder with no allowlist sells the whole roster, and
            # the reserve with it, whatever the story says.
            if latest and w.get("buy") and not w.get("allow") and _when(m) < latest:
                raise SystemExit(f"{spec['TITLE']}: {code_of(m)}'s window has no allowlist, "
                                 "so it sells the allied reserve before the reserve opens")
        _open_windows(spec, [e["unit"] for e in spec["ROSTER"] if e["unit"] in opens])


def admit_aircraft(spec, kept, dropped):
    """The held reserve aircraft (RESERVE_AIR) after build_pack has judged
    them on the built missions: `kept` go on the roster and on sale from
    their opening, `dropped` [(entry, why)] join RESERVE_LEFT_OUT."""
    if not spec.get("RESERVE_OPENS"):
        return
    on_roster = {e["unit"] for e in spec["ROSTER"]}
    for e in kept:
        if e["unit"] not in on_roster:
            spec["ROSTER"].append(e)
    left = {e["unit"] for e, _why in spec["RESERVE_LEFT_OUT"]}
    spec["RESERVE_LEFT_OUT"] += [(e, why) for e, why in dropped if e["unit"] not in left]
    _open_windows(spec, [e["unit"] for e in spec["ROSTER"]
                         if e["unit"] in spec["RESERVE_OPENS"]])


def say_reserve(spec):
    """Each window from an opening says what the reserve sells there, once,
    from what the roster sells: build_pack's main() calls it after
    admit_aircraft(), before the spine is written."""
    if not spec.get("RESERVE_OPENS"):
        return
    by_code = {code_of(m): m for m in spec["MISSIONS"]}
    opens = spec["RESERVE_OPENS"]
    nation = _commander(spec, "CommanderNations")
    units = [e for e in spec["ROSTER"] if e["unit"] in opens]
    for m in spec["MISSIONS"]:
        w = m.get("window", {})
        if not w.get("buy") or w.get("_reserve_said"):
            continue
        selling = [e for e in units if _when(m) >= _when(by_code[opens[e["unit"]]])]
        if selling:
            prices = (", at their own navies' prices"
                      if any(_navy(e) != nation for e in selling) else "")
            w["situation"] = (w.get("situation", "") + f" Also on sale here{prices}: "
                              + reserve_phrase(spec, [e["unit"] for e in selling]) + ".")
        w["_reserve_said"] = True


def apply(specs):
    from campaign_data import U, S
    for spec in specs:
        # Registry-only specs can be inspected before their mission package
        # is loaded. Enrich complete mission definitions at this stage.
        if "MISSIONS" not in spec:
            continue
        for m in spec["MISSIONS"]:
            if m.get("_depth_revision"):
                continue
            code = code_of(m)
            # Explicit author opt-in to the native preparation phase. The
            # renderer emits it only when a starting player deck exists.
            m["initial_deck_prep"] = True
            if code not in REPORTS:
                raise SystemExit(f"{code}: no reviewed tactical report for this SEST mission")
            m.setdefault("reports", []).append(dict(minute=min(8, m["minutes"] / 4), intel=REPORTS[code]))
            m["brief"] += "\\n\\nCOMMAND NET: A mission-specific tactical report follows eight minutes after the start. It is advice from the command team, not a new sensor detection."
            if code in UAV_SITES:
                add_uav(m, code, U, S)
            if code in SUB_SUPPORT:
                add_sub(m, code, U, S)
            if code in EXTRA_CONTACTS:
                add_contact(m, code, U)
            # Count is derived from actual placeholder sections by the builder.
            # Add the cockpits as well as opening the four-aircraft allocation;
            # editing the row alone would silently leave the old two places.
            if m.get("role") == "fleet":
                w = m.get("window", {})
                for row in w.get("flights", []):
                    role = row.split("|", 1)[0]
                    if role not in ("CAP", "Attack"):
                        continue
                    slots = [u for u in m["units"] if u["side"] == "blue" and u.get("slot") == role]
                    if slots:
                        for i in range(len(slots), 4):
                            m["units"].append(deepcopy(slots[i % len(slots)]))
            m["_depth_revision"] = True
    # After the enrichment, so a unit added above counts as placed when the
    # reserve is filtered for named hulls.
    apply_reserve(specs)
