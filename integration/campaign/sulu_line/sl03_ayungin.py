"""SL03 - Ayungin. Second Thomas Shoal, West Philippine Sea, 26 October 2028.

The rotation-and-resupply run to BRP Sierra Madre, the grounded landing ship
the Marines hold on Ayungin Shoal. Two China Coast Guard cutters (converted
Type 056 corvettes, as the real ones are) and three militia trawlers are
between the boat and the shoal; an intelligence ship is watching from the north.
None of them will fire. Neither will the task group: the boat gets through
by being escorted, not by shooting, and anything fired here is a provocation
and a round the supply ships have to replace.

Every Chinese hull is a `spare` with a fatal entry. The win is the boat in
the shoal's lagoon.
"""
from campaign_data import U, F, S
from .tables import HELO

MISSION = dict(
    code="SL03", series="Sulu Line", seq="SULU LINE  ·  MISSION 3",
    group="core", num="03", key="Ayungin", place="West Philippine Sea",
    intro=(
        "The resupply boat for the Marines on Ayungin Shoal, with two coast guard cutters "
        "and three militia trawlers in the way. Nobody fires."
    ),
    sender="Naval Forces West; Western Command",
    intent=((
        "The boat reaches the shoal. Escort it, put your hulls between it and the cutters, "
        "and fire on nothing: the coast guard and the militia are not shooting, and the "
        "first shot fired here would be ours. The ship to the north is watching for it."
    )),
    date=(2028, 10, 26), time=(6, 0), sea=2, clouds="Clear", wind="NE",
    difficulty=3, minutes=100, centre=(9.75, 116.1),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "WEST PHILIPPINE SEA, 0600. M/L KALAYAAN, a chartered supply boat with the "
            "Marines' rotation, water and rations, is twenty-four miles east of Ayungin "
            "Shoal. BRP SIERRA MADRE has been aground in the lagoon since 1999 and her "
            "detachment has not been resupplied in five weeks.\\n\\nTwo China Coast Guard "
            "cutters and three militia trawlers are between the boat and the shoal, as "
            "they were the last three times. A Chinese intelligence ship is holding north of "
            "the shoal, towards Mischief Reef, and an early-warning aircraft is overhead.\\n\\nTake the boat "
            "into the lagoon. Your ships start at weapons Hold. Nobody here is going to "
            "shoot, and if the task group does it will have started something the Navy "
            "cannot finish this week. Use your hulls and your helicopter. Fishing boats are "
            "working the reef."
        )),
    forces=(
        "Your task group and its helicopter. Escorted: M/L Kalayaan. Opposing, not "
        "shooting: two China Coast Guard cutters, three militia trawlers, an intelligence "
        "ship and a KJ-500 early-warning aircraft. Neutral: fishing boats."
    ),
    special="No shot fired: every Chinese hull and the aircraft are protected by the ROE.",
    objectives=[
        ("Resupply", "Bring M/L Kalayaan into Ayungin's lagoon", "35,-35,Fail,Main"),
        ("Boat", "Keep the supply boat afloat", "15,-30,Complete"),
        ("Restraint", "Fire on nothing: not the cutters, the trawlers, the intelligence ship or the "
                      "aircraft", "20,-40,Complete"),
        ("Traffic", "Harm no fishing boat", "0,-30,Complete"),
        ("Watchers", "Classify the intelligence ship to the north", "10,0,None"),
    ],
    victory=dict(kind="arrive", station="boat", min_units=1, at=(9.73, 115.87),
                 radius=3, objective="Resupply"),
    fatal=[F("Boat", ["boat"]),
           F("Restraint", ["ccg", "militia", "frigate", "red_air"])],
    neutral_objective="Traffic",
    win=(
        "KALAYAAN is in the lagoon and alongside SIERRA MADRE. The Marines have their water "
        "and their relief. The cutters have gone back to station. Nothing was fired."
    ),
    lose=(
        "The run to Ayungin has failed. The detachment on SIERRA MADRE will go another week "
        "without relief, and Manila is asking what was fired."
    ),
    timeout="{deadline_clock}, and KALAYAAN is still outside the lagoon. The tide will not let her "
            "in again today.",
    stations={
        # Everything east of the shoal is on proven water out of the
        # Spratly scenarios; the shoal itself is the victory box.
        "escort": S(9.69, 116.25, "Escort", heading=270),
        "flight": S(9.70, 116.22, "Ship's flight", heading=270, alt=500),
        "boat": S(9.72, 116.10, "M/L Kalayaan", heading=265),
        "ccg": S(9.76, 116.00, "Coast guard cutters", heading=90),
        "militia": S(9.66, 115.98, "Militia trawlers", heading=60),
        "frigate": S(10.24, 115.94, "Intelligence ship", heading=180),
        "red_air": S(10.10, 115.70, "Patrol aircraft", heading=90, alt=15000),
        "fishing": S(9.78, 116.15, "Fishing boats", heading=200),
        "home": S(9.74, 118.75, "Puerto Princesa"),
    },
    units=[
        U("blue", "euromod-philippines", "pn_ffg-150", "escort", variant="Variant1",
          weapons="Hold"),
        U("blue", "philippines-luzon-line", "phl_h-76", "flight", squadron="Squadron1",
          alt=500, weapons="Hold", loadout="CAS", slot="HeloRecon"),
        U("blue", "_vanilla", "civ_fv_sterntrawler_b", "boat", name="M/L Kalayaan",
          nation="Philippines", weapons="Hold", route=[(9.73, 115.87, 0)], telegraph=3),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Puerto Princesa (Antonio Bautista Air Base)", nation="Philippines",
          weapons="Hold"),
        # The cutters carry machine guns and nothing else. They were Type 056A
        # corvettes at weapons Hold until the first public report (6 Oct 2026):
        # their YJ-83s were on the boat within fifteen seconds of the start, so
        # Hold does not hold an AI ship back. Nothing here may depend on it:
        # every Chinese hull and aircraft in this mission is unarmed or close
        # to it, and the cutters shadow north of the boat's track rather than
        # crossing it.
        U("red", "_vanilla", "plan_ap_qiongsha", "ccg", name="CCG 3305", weapons="Hold",
          route=[(9.765, 116.00, 0), (9.755, 115.93, 0)], telegraph=3),
        U("red", "_vanilla", "plan_ap_qiongsha", "ccg", name="CCG 3306", weapons="Hold",
          route=[(9.775, 116.04, 0), (9.765, 115.96, 0)], telegraph=3),
        U("red", "_vanilla", "civ_fv_sterntrawler_a", "militia", name="Qiong Sansha Yu 00213",
          weapons="Hold", route=[(9.70, 116.06, 0)], telegraph=3),
        U("red", "_vanilla", "civ_fv_sterntrawler_c", "militia", name="Qiong Sansha Yu 00219",
          weapons="Hold", route=[(9.74, 116.04, 0)], telegraph=3),
        U("red", "_vanilla", "civ_fv_sterntrawler_d", "militia", name="Yue Tai Yu 18000",
          weapons="Hold", route=[(9.68, 116.00, 0)], telegraph=3),
        # The watcher to the north is an intelligence ship, not the 054A
        # frigate the first build placed: 33 NM is well inside a YJ-83.
        U("red", "_vanilla", "civ_fv_okean", "frigate", name="Intelligence ship Nan Hai 31",
          nation="China", weapons="Hold", radars="True"),
        # A KJ-500 carries no weapons; the Y-8FQ it replaces carried torpedoes.
        U("red", "modern-plan-systems", "plaaf_kj-500", "red_air", squadron="Squadron1",
          weapons="Hold",
          route=[(9.60, 116.40, 25000), (10.10, 115.70, 25000)], loop=True, telegraph=3),
        U("neutral", "_vanilla", "civ_fv_fishingboat_c", "fishing",
          name="Fishing boat Ngoc Lan (Vietnam)", route=[(9.85, 115.95, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fishing",
          name="Banca Joanna Marie", route=[(9.90, 116.20, 0)], telegraph=2),
    ],
    resolve={"Resupply": "victory", "Traffic": "neutral",
             "Boat": ("protect", "boat"),
             "Restraint": ("spare", "ccg", "militia", "frigate", "red_air"),
             "Watchers": ("classify", "frigate", 1)},
    declares=[],
    window=dict(buy=False, repair=True, flights=[HELO],
                situation=(
                    "No reinforcements and no rearming before Ayungin. Repairs are "
                    "available. This run is won without firing, so what the gun line spent "
                    "at Jolo does not matter today - but it will at the rendezvous."
                )),
    role="logistics",
)
